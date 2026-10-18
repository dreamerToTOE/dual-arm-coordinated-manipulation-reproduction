#!/usr/bin/env python3
"""V fixed local transport draft; no describe mode, no import-time model calls.

Thin adaptation of SBL local Budget/Journal/Session pump+finish and external
GNUtime supervision. V's frozen argv file runs once without stdin, so only that
startup/collection transport differs. Raw evidence never implies qualification.
"""
from __future__ import annotations
from collections import Counter
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_p4_full_r2_abb_sbl_pcs_setup_draft as L
import build_v_pcs_local_v1_draft as B
RUN = '20261018_R2_D080_V_PCS_LOCAL01'
CLAIM = 'P4_D080_V_PCS_LOCAL01_FIXED_A02_PM005_30W60CPU_20261018'
LABEL = 'CORRECTED_COMAU_APC_ALIGNED_V3_ORIGINAL_FIXED_PCS_RBS_CONTROL_RECONSTRUCTED_A02'
FIXTURE = ROOT / 'configs/p4_d080/v_pcs_local_fixed_saved_v1.DRAFT.json'
SUPERVISOR = ROOT / 'scripts/p4_d080/supervise_v_pcs_local_v1_draft.py'
STAGE = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1')
BUILD_RUN = '20261018_R2_D080_V_PCS_BUILD01'
MARKER = b'P4_V_PCS_TRACE '
COMPAT_PRE = ROOT / 'reports/P4_D080_ENV_V_PCS_MONOTONIC_COMPAT_INDEPENDENT_PRE_20261018.json'
COMPAT_PRE_SHA = '3f357584a3413b43eb2d2bc20465121a3a494579a824ce4a4eaa0dee27c58a7d'
COST_BASIS = 'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
DRIVER_OUTPUT_SCHEMA = 'P4_D080_V_PCS_LOCAL_DRAFT_V1'
PUBLIC_REQUESTS_PER_BINARY = 18
STDOUT_JSON_ROWS_PER_BINARY = 1 + PUBLIC_REQUESTS_PER_BINARY
# Explicit identity-only adaptation of prior snapshot exclusion. No body edits.
B.RUN_NAME = RUN; B.RUN = ROOT / 'results/p4_full' / RUN
require = L.require; sha = L.sha; load = L.load; exact = L.exact; path = L.path
OWN = [Path(__file__).resolve(), SUPERVISOR, FIXTURE,
       ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL_FIXED_PRE_DRAFT_20261018.md',
       ROOT / 'scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py',
       ROOT / 'scripts/p4_d080/build_v_pcs_local_v1_draft.py', COMPAT_PRE]


class Budget(L.Budget):
    def __init__(self, spec, started, cpu0):
        super().__init__({'previous_r2_wall_s': spec['prior']['wall_s'],
                          'previous_r2_cpu_s': spec['prior']['cpu_s']}, started, cpu0)
        self.wall_cap = min(30., 3600. - spec['prior']['wall_s'])
        self.cpu_cap = min(60., 7200. - spec['prior']['cpu_s'])
    def check(self):
        live = sum(B.lifecycle.live_group_cpu(p.pid) for p in self.processes if p.returncode is None)
        require(time.monotonic() - self.started < self.wall_cap
                and L.own_reaped_cpu() - self.cpu_start + live < self.cpu_cap, 'V_LOCAL_SELF_REAPED_LIVE_GROUP_CAP')


class Session(L.Session):
    def __init__(self, target, work, protocol, budget, journal, counts):
        super().__init__(target, work, budget, journal, counts)
        self.command = [target['binary'], str(work), str(protocol)]
    def start(self):
        # V has no stdin gate. Validate/freeze all input files before this launch;
        # do not pretend this observes loaded symbols before model construction.
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            def limits():
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
                resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
            self.counts['source_process_start_attempted'] += 1
            self.journal.add('source_process_start_attempted', command=self.command)
            self.proc = subprocess.Popen(self.command, cwd=ROOT, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, start_new_session=True,
                preexec_fn=limits, env=L.SOURCE_ENV)
            self.budget.processes.append(self.proc); self.counts['source_process_started'] += 1
            self.proc.stdin.close(); self.stdin_closed_after_request = True
            self.request_sent = 0; self.request_raw = b''
            row = L.stat_row(self.proc.pid)
            require(row is not None and int(row[2]) == self.proc.pid, 'REGISTERED_V_SOURCE_STAT_REQUIRED')
            self.start_ticks = int(row[19]); self.register_pipes(); self.startup_complete = True
            self.journal.add('source_process_started', pid=self.proc.pid, start_ticks=self.start_ticks,
                command=self.command, input_transport='PREBOUND_FIXED_ARGV_FILE_NO_STDIN',
                pre_model_loaded_symbol_observation='UNOBSERVED_NOT_CLAIMED')
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    def collect(self, expected):
        rows = []
        while self.selector.get_map():
            self.pump()
            while b'\n' in self.pending:
                raw, self.pending = self.pending.split(b'\n', 1)
                self.journal.add('complete_response_line', bytes=len(raw) + 1,
                                 sha256=hashlib.sha256(raw + b'\n').hexdigest())
                require(raw.startswith(b'{'), 'UNKNOWN_STDOUT_PREFIX_NO_SKIP')
                rows.append(json.loads(raw)); require(len(rows) <= expected, 'EXTRA_V_OUTPUT_NO_SKIP')
        self.proc.wait(timeout=max(.001, self.budget.remaining()))
        require(not self.pending and len(rows) == expected and self.proc.returncode == 0,
                'EXACT_COMPLETE_V_STDOUT_EXIT0_REQUIRED')
        self.responses = rows; self.finish(normal=True); return rows


def supervisor_proof(spec, protocol):
    # Same audited SBL source/argv/parent/FD proof, with V runner identity.
    ext = spec['external_supervision']; raw = path(ext['metadata_path']).read_bytes().splitlines(keepends=True)[0]
    planned = json.loads(raw); parent = os.getppid(); stat = L.stat_row(parent)
    argv = ['/usr/bin/time', '--quiet', '-f', '%e %U %S %x', '-o', f"/proc/self/fd/{planned['time_fd']}",
            '/usr/bin/python3', str(Path(__file__).resolve()), '--protocol', str(protocol)]
    require(stat is not None and int(stat[1]) == planned['supervisor_pid']
            and sha(Path('/proc', str(parent), 'exe')) == ext['time_binary_sha256']
            and planned['event'] == 'planned_launch' and planned['run_id'] == RUN
            and planned['protocol_sha256'] == sha(protocol) and planned['runner_sha256'] == sha(__file__)
            and planned['supervisor_source_sha256'] == sha(SUPERVISOR) and planned['argv'] == argv
            and Path('/proc', str(parent), 'cmdline').read_bytes().rstrip(b'\0').split(b'\0') == [v.encode() for v in argv],
            'ACTUAL_GNUTIME_PARENT_SOURCE_PROTOCOL_ARGV_REQUIRED')
    inode = path(ext['sibling_path']).stat(); held = []
    for descriptor in Path('/proc', str(parent), 'fd').iterdir():
        try:
            observed = descriptor.stat()
            if (observed.st_dev, observed.st_ino) == (inode.st_dev, inode.st_ino):
                held.append(int(descriptor.name))
        except FileNotFoundError:
            pass
    require(held and (inode.st_dev, inode.st_ino) == (planned['time_device'], planned['time_inode']),
            'ACTUAL_EXCLUSIVE_TIME_INODE_REQUIRED')
    return {'time_pid': parent, 'time_start_ticks': int(stat[19]), 'supervisor_pid': planned['supervisor_pid'],
            'actual_argv': argv, 'held_time_fds': held, 'launch_line_sha256': hashlib.sha256(raw).hexdigest()}


def preflight(spec, protocol):
    require(spec['schema'] == 'P4_D080_V_PCS_LOCAL_RUN_FROZEN_V1' and spec['frozen'] is True
            and spec['environment'] == 'V' and spec['method'] == 'PCS' and spec['run_id'] == RUN
            and spec['classification'] == LABEL and spec['budget'] == {'wall_s': 30, 'cpu_s': 60}
            and spec['scientific_execution_authorized'] is True and spec['formal_execution_authorized'] is False
            and spec['independent_review_passed'] is True, 'V_FIXED_LOCAL_REVIEW_FREEZE_REQUIRED')
    require(spec['fixture_sha256'] == sha(FIXTURE), 'FIXED_SAVED_V_FIXTURE_BYTES_REQUIRED')
    compat = load(COMPAT_PRE)
    require(sha(COMPAT_PRE) == COMPAT_PRE_SHA and compat['personnel_independent'] is True
            and compat['checks_total'] == compat['checks_passed'] == 7 and compat['checks_failed'] == 0
            and compat['status'] == 'PASS_INCREMENTAL_ENGINEERING_COMPATIBILITY_STATIC_ONLY'
            and sha(B.__file__) == compat['source_sha256']['scripts/p4_d080/build_v_pcs_local_v1_draft.py'],
            'EXACT_REVIEWED_PRIOR_MONOTONIC_COMPATIBILITY_ADAPTER_REQUIRED')
    fixture = load(FIXTURE); driver = spec['driver_protocol']
    require(driver['schema'] == 'P4_D080_V_PCS_LOCAL_FROZEN_V1' and driver['environment'] == 'V'
            and driver['method'] == 'PCS' and driver['frozen'] is True and driver['api_local_only'] is True
            and driver['scientific_execution_authorized'] is True and driver['independent_review_passed'] is True
            and driver['requests'] == fixture['requests'] and driver['caps'] == fixture['caps_per_binary_proposal']
            and len(driver['requests']) == PUBLIC_REQUESTS_PER_BINARY and spec['schedule_modes'] == ['trace', 'plain'],
            'ORIGINAL_FIXED_18_REQUESTS_TRACE_PLAIN_REQUIRED')
    for center in fixture['source_centers'].values():
        require(sha(center['path']) == center['sha256']
                and load(center['path'])['selected_q_rad'] == center['q12'], 'SAVED_A02_CENTER_BYTES_CHANGED')
    require(spec['maxima'] == fixture['global_maxima_proposal'], 'GLOBAL_512_PROJECT_256_NODE_MAXIMA_REQUIRED')
    build_path = path(spec['build_assets']['execution']); build = load(build_path)
    post_path = path(spec['build_assets']['personnel_independent_POST']); post = load(post_path)
    require(sha(build_path) == spec['build_assets']['execution_sha256'] == post['execution_sha256']
            and sha(post_path) == spec['build_assets']['post_sha256'] and build['status'] == 'BUILT_NOT_QUERIED'
            and build['run_id'] == BUILD_RUN and post['personnel_independent'] is True
            and post['external_supervision_qualified'] is True and post['engineering_build_qualified'] is True
            and post['charge_basis'] == COST_BASIS and post['monotonic_envelope_qualified'] is True
            and post['checks_failed'] == 0
            and post['checks_total'] == post['checks_passed'] > 0, 'ACTUAL_INDEPENDENT_V_BUILD_AND_COST_PASS_REQUIRED')
    build_charge = load(post['receipt']); build_receipt = load(post['internal_receipt'])
    require(sha(post['receipt']) == post['external_charge_sha256'] == post['receipt_sha256']
            and sha(post['internal_receipt']) == post['internal_receipt_sha256'] == build_charge['receipt_sha256']
            and build_charge['execution_sha256'] == build_receipt['execution_sha256'] == sha(build_path)
            and build_charge['charge_basis'] == COST_BASIS and build_charge['monotonic_envelope_valid'] is True
            and build_charge['wall_s'] == post['upper_wall_s'] and build_charge['cpu_s'] == post['upper_cpu_s'],
            'EXACT_SUCCESSFUL_BUILD_MAX_ENVELOPE_CHARGE_RECEIPT_REQUIRED')
    for target in build['targets']:
        mode = target['mode']; frozen = spec['build_assets']['targets'][mode]
        require(mode in ('trace', 'plain') and frozen['binary'] == target['binary']
                and sha(frozen['binary']) == target['binary_sha256'] == frozen['binary_sha256'], 'EXACT_BUILT_V_TARGET_BYTES_REQUIRED')
    require(set(spec['build_assets']['targets']) == {'trace', 'plain'}, 'TWO_BUILT_TARGETS_REQUIRED')
    collision = load(B.COL_ROOT / 'manifest.json')
    model, = [row for row in collision['entries'] if row['model'] == 'V' and row['variant'] == 'aligned']
    expected_meshes = {str(B.COL_STAGE / 'simulator' / name): digest for name, digest in model['mesh_sha256'].items()}
    require(len(expected_meshes) == 27 and spec['runtime_meshes_sha256'] == expected_meshes
            and model['active_call_statement_count'] == 87 and model['tcp_observation_version'] == 3,
            'EXACT27_V3_MESHES_AND87_SOURCE_PAIRS_REQUIRED')
    require(sha(B.SCOPE) == B.SCOPE_SHA and sha(B.OVERLAY) == B.OVERLAY_SHA
            and load(B.SCOPE)['VI_future_science_authorized'] is False
            and load(B.SCOPE)['formal_execution_authorized'] is False, 'D080_SCOPE_VI_AND_FORMAL_GUARD_REQUIRED')
    require(all(sha(name) == digest for name, digest in spec['bound_files_sha256'].items()), 'FROZEN_RUNTIME_ASSET_DRIFT')
    for filename in OWN:
        require(spec['bound_files_sha256'].get(str(filename)) == sha(filename), 'ALL_OWN_RUNTIME_SOURCES_MUST_BE_PREBOUND')
    prior = B.validate_prior(spec)
    require(all(spec['bound_files_sha256'].get(name) == digest for name, digest in prior['evidence_sha256'].items()),
            'ALL_CURRENT_CHARGED_PRIOR_CERTIFICATE_BYTES_REQUIRED')
    require(L.preload_state() == spec['system_preload_state'], 'SYSTEM_PRELOAD_CHANGED')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for filename in [*OWN, protocol]:
        require(subprocess.check_output(['git', 'show', commit + ':' + str(filename.relative_to(ROOT))], cwd=ROOT)
                == filename.read_bytes(), 'FROZEN_RUNTIME_FILES_MUST_BE_COMMITTED')
    return commit, prior


def collect_semantics(rows, mode, spec):
    require(len(rows) == STDOUT_JSON_ROWS_PER_BINARY and rows[0]['status'] == 'SETUP_COMPLETED'
            and 'request' not in rows[0] and 'result' not in rows[0], 'ONE_SETUP_PLUS18_REQUEST_ROWS_REQUIRED')
    records = []; semantic = []
    for index, row in enumerate(rows):
        require(row['schema'] == DRIVER_OUTPUT_SCHEMA and row['environment'] == 'V'
                and row['continuous_collision_checked'] is False and row['trace_enabled'] is (mode == 'trace')
                and row['solve_calls'] == row['rng_calls'] == 0, 'NO_SOLVE_OR_DRIVER_RNG_REQUIRED')
        records.extend(row['observed_records'])
        if index:
            require(row['request'] == spec['driver_protocol']['requests'][index - 1]
                    and row['status'] in ('SOURCE_CALL_COMPLETED', 'NOT_EXECUTED_DEPENDENCY_FAILED'),
                    'FIXED_REQUEST_OR_DEPENDENCY_FAILURE_REQUIRED')
            semantic.append({'request': row['request'], 'result': row['result'], 'status': row['status']})
    require(rows[-1]['observed_counts_cumulative'].get('public_request') == PUBLIC_REQUESTS_PER_BINARY, 'EXACT18_PUBLIC_REQUESTS_REQUIRED')
    require(len({r['id'] for r in records}) == len(records), 'UNIQUE_OBSERVER_LIFETIMES_REQUIRED')
    return {'rows': semantic, 'records': records, 'counts': rows[-1]['observed_counts_cumulative']}


def independent_nodes(semantic):
    # Queue saved successful source outputs; do not run any independent oracle.
    nodes = {}
    for record in semantic['records']:
        if record.get('event') != 'completed' or record['kind'] not in ('project_fixed', 'is_valid_rbs'):
            continue
        result = record['result']
        if result.get('returned') is not True:
            continue
        q = result['q12']; require(len(q) == 12 and all(math.isfinite(v) for v in q), 'FINITE_SUCCESSFUL_SOURCE_Q12_REQUIRED')
        key = b''.join(struct.pack('>d', float(v)) for v in q).hex()
        nodes.setdefault(key, {'q12': q, 'source_records': []})['source_records'].append(record['id'])
    return nodes


def execute(spec, protocol):
    started = time.monotonic(); cpu0 = L.own_reaped_cpu()
    commit, prior = preflight(spec, protocol); proof = supervisor_proof(spec, protocol)
    folder = ROOT / 'results/p4_full' / RUN; claim = ROOT / 'results/p4_full' / (CLAIM + '.claim.json')
    require(not folder.exists() and not claim.exists() and not L.active_p4(), 'FRESH_LOCAL_ONLY_NO_OTHER_ACTIVE_P4')
    budget = None; journal = None; sessions = []; diagnostics = []; error = None; semantics = {}; copied = {}
    record = {'schema': 'P4_D080_V_PCS_LOCAL_EXECUTION_V1', 'run_id': RUN, 'classification': LABEL,
              'status': 'STOP_PREFIX_RETAINED', 'source_commit': commit, 'protocol_sha256': sha(protocol),
              'actual_charge_prior': prior, 'budget': spec['budget'], 'supervisor_launch_proof': proof,
              'protocol': str(protocol.relative_to(ROOT)), 'claim': str(claim.relative_to(ROOT)),
              'bound_files_sha256': spec['bound_files_sha256'],
              'new_external_charge_basis': COST_BASIS,
              'source_stdout_contract': {'setup_rows_per_binary': 1, 'request_rows_per_binary': 18, 'total_rows_per_binary': 19,
                  'source_processes': 2, 'total_public_requests': 36, 'fixed_argv_file_no_stdin': True},
              'independent_local_qualified': False, 'independent_path_qualified': False,
              'continuous_collision_certificate': False, 'formal_table_I_calls': 0, 'solve_calls': 0,
              'new_VI_candidate_constructions': 0, 'binary_execution_calls': 0, 'counts': {},
              'pre_model_loaded_symbol_observation': 'UNOBSERVED_NOT_CLAIMED'}
    counts = Counter()
    try:
        L.durable_new(claim, {'run_id': RUN, 'source_commit': commit, 'protocol_sha256': sha(protocol),
                             'budget': spec['budget'], 'no_retry_reset_resume': True})
        record['claim_sha256'] = sha(claim); folder.mkdir(); journal = L.Journal(folder / 'evidence.jsonl')
        budget = Budget(spec, started, cpu0); budget.start()
        for mode in spec['schedule_modes']:
            budget.check(); one = folder / mode; work = one / 'work'; (work / 'simulator').mkdir(parents=True)
            for name, digest in spec['runtime_meshes_sha256'].items():
                filename = work / 'simulator' / Path(name).name
                with filename.open('xb') as stream:
                    stream.write(path(name).read_bytes()); stream.flush(); os.fsync(stream.fileno())
                require(sha(filename) == digest, 'RUNTIME_MESH_BYTES_CHANGED'); copied[str(filename)] = digest
            local_protocol = one / 'driver_protocol.json'; L.durable_new(local_protocol, spec['driver_protocol'])
            copied[str(local_protocol)] = sha(local_protocol)
            session = Session(spec['build_assets']['targets'][mode], work, local_protocol, budget, journal, counts)
            sessions.append(session); session.start(); rows = session.collect(STDOUT_JSON_ROWS_PER_BINARY)
            semantic = collect_semantics(rows, mode, spec); semantics[mode] = semantic
            L.durable_new(one / 'parsed_rows.json', rows)
            trace = [json.loads(line[len(MARKER):]) for line in bytes(session.raw['stderr']).splitlines() if line.startswith(MARKER)]
            require(bool(trace) is (mode == 'trace'), 'TRACE_STDERR_MODE_REQUIRED')
            if mode == 'trace':
                require(sum(r.get('event') == 'entered' for r in trace) == len(semantic['records']), 'ALL_TRACE_ENTRY_LIFETIMES_REQUIRED')
        require(exact(semantics['trace'], semantics['plain']), 'PLAIN_TRACE_SEMANTICS_MISMATCH')
        nodes = independent_nodes(semantics['trace']); record['independent_unique_nodes_observed'] = len(nodes)
        L.durable_new(folder / 'independent_nodes_PENDING.json', {'status': 'NOT_EXECUTED_PENDING_INDEPENDENT_QUALIFICATION',
            'max_unique_nodes': 256, 'nodes': nodes, 'new_independent_oracle_calls': 0})
        require(len(nodes) <= 256, 'NO_EXPANSION_OF_INDEPENDENT_NODE_BUDGET')
        project_count = sum(s['counts'].get('project_fixed', 0) for s in semantics.values())
        require(project_count <= 512, 'TOTAL_INTERNAL_AND_PUBLIC_FIXED_PROJECT_CAP512')
        record.update(status='SOURCE_FIXED_LOCAL_OBSERVED_PENDING_INDEPENDENT_POST',
                      source_counts_by_mode={m: s['counts'] for m, s in semantics.items()},
                      internal_and_public_fixed_project_calls=project_count, plain_trace_semantics_equal=True,
                      public_request_calls=36, setup_calls=2)
    except BaseException as exception:
        error = exception; record['termination_reason'] = repr(exception)
    finally:
        if budget is not None:
            budget.close()
        for session in sessions:
            try:
                if session.proc is not None:
                    L.kill_source_group(session.proc)
                session.finish(normal=False)
            except BaseException as exception:
                diagnostics.append({'stage': 'source_cleanup', 'error': repr(exception)})
        record['source_process_registry'] = [{'pid': s.proc.pid, 'returncode': s.proc.returncode,
            'start_ticks': s.start_ticks, 'actual_group_after_cleanup': L.process_group_members(s.proc.pid),
            'pipe_EOF_observed': s.pipe_EOF_observed} for s in sessions if s.proc is not None]
        try:
            require(all(s.proc is not None and not L.process_group_members(s.proc.pid)
                        and s.proc.returncode == 0 and all(s.pipe_EOF_observed.values()) for s in sessions)
                    and len(sessions) == 2, 'TWO_REAPED_COMPLETE_EXIT0_SOURCES_REQUIRED')
        except BaseException as exception:
            diagnostics.append({'stage': 'complete_process_gate', 'error': repr(exception)})
        try:
            record['bound_files_after_sha256'] = {n: sha(n) for n in spec['bound_files_sha256']}
            require(record['bound_files_after_sha256'] == spec['bound_files_sha256'], 'BOUND_FILE_CHANGED')
            record['copied_runtime_after_sha256'] = {n: sha(n) for n in copied}
            require(record['copied_runtime_after_sha256'] == copied, 'COPIED_RUNTIME_CHANGED')
            require(sha(protocol) == record['protocol_sha256'] and sha(claim) == record['claim_sha256'], 'PROTOCOL_OR_CLAIM_CHANGED')
            record['prior_after'] = B.validate_prior(spec)
            require(record['prior_after'] == prior, 'LATEST_CHARGED_PRIOR_CHANGED')
        except BaseException as exception:
            diagnostics.append({'stage': 'final_assets_and_prior', 'error': repr(exception)})
        if folder.is_dir():
            try:
                for index, session in enumerate(sessions):
                    for channel, raw in session.raw.items():
                        filename = folder / f'process{index}_{channel}.bin'
                        with filename.open('xb') as stream:
                            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
                if journal is not None:
                    journal.add('final_counts', counts=dict(counts), diagnostics=diagnostics); journal.finish()
                record['retained_run_files_sha256'] = {str(p.relative_to(ROOT)): sha(p) for p in folder.rglob('*') if p.is_file()}
            except BaseException as exception:
                diagnostics.append({'stage': 'raw_evidence_persistence', 'error': repr(exception)})
        record.update(wall_s=time.monotonic() - started, cpu_s=L.own_reaped_cpu() - cpu0,
                      binary_execution_calls=counts['source_process_started'], counts=dict(counts), diagnostics=diagnostics)
        if diagnostics:
            record['status'] = 'STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if record['wall_s'] >= 30 or record['cpu_s'] >= 60:
            record['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'
        if folder.is_dir():
            L.durable_new(folder / 'execution.json', record)
            receipt = {'schema': 'P4_D080_V_PCS_LOCAL_COST_RECEIPT_V1', 'execution_sha256': sha(folder / 'execution.json'),
                'status': record['status'], 'wall_s_through_execution_persistence': time.monotonic() - started,
                'cpu_s_through_execution_persistence': L.own_reaped_cpu() - cpu0,
                'last_receipt_persistence_tail': 'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',
                'external_supervision_qualified': False}
            if receipt['wall_s_through_execution_persistence'] >= 30 or receipt['cpu_s_through_execution_persistence'] >= 60:
                receipt['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'
            L.durable_new(folder / 'cost_receipt.json', receipt); record['terminal_receipt_status'] = receipt['status']
    print(json.dumps({'status': record.get('terminal_receipt_status', record['status']),
                      'independent_POST_required': True, 'independent_local_qualified': False}))
    if error is not None:
        raise error
    require(record.get('terminal_receipt_status', '').startswith('SOURCE_'), 'FIXED_V_LOCAL_TRANSPORT_DID_NOT_COMPLETE')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, required=True); args = parser.parse_args()
    protocol = args.protocol.resolve(); execute(load(protocol), protocol)


if __name__ == '__main__':
    main()
