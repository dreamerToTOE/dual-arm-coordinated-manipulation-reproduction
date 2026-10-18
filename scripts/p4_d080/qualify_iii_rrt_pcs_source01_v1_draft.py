#!/usr/bin/env python3
"""III single SOURCE-entry draft. No import-time model or binary calls.

Reuse audited SBL transport and V charged-prior/cleanup infrastructure. The
only new transport is one compact request followed by EOF, then arbitrary raw
author stdout and a separately saved result. No physical path qualification.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(Path(__file__).resolve().parent)]
import qualify_p4_full_r2_abb_sbl_pcs_setup_draft as L
import build_v_pcs_local_v1_draft as B
RUN = '20261018_R2_D080_III_RRT_PCS_SOURCE01'
CLAIM = 'P4_D080_III_RRT_PCS_SOURCE01_A01_SEED7_30W60CPU_20261018'
LABEL = 'CORRECTED_ABB_APC_ALIGNED_III_ORIGINAL_RRT_PCS_CONTROL_RECONSTRUCTED_A01'
PRE = ROOT / 'reports/P4_D080_ENV_III_RRT_PCS_SOURCE01_PRE_DRAFT_20261018.md'
SUPERVISOR = ROOT / 'scripts/p4_d080/supervise_iii_rrt_pcs_source01_v1_draft.py'
BUILD = ROOT / 'results/p4_full/20261018_R2_D080_III_RRT_PCS_BUILD01/execution.json'
BUILD_SHA = '16696c0d80ce0ac893814afc2ca5e0720e6ebb478da63cc6e46eb8f7b80c4f31'
BUILD_POST = ROOT / 'reports/P4_D080_ENV_III_RRT_PCS_BUILD01_SAVED_INDEPENDENT_POST_20261018.json'
BUILD_POST_SHA = 'c311dd3601995006c6b476163b51c3719bad193896d17ca349e35ca5ed3d829e'
LOCAL_POST = ROOT / 'reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_TASK_20261015.md'
LOCAL_ADDENDUM = ROOT / 'reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_ADDENDUM_20261015.md'
ENDPOINTS = [ROOT / f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/III_{i}.json' for i in range(2)]
ENDPOINT_SHAS = ['85550cbc3ffbf80c80519b5e592e85401dcf1e96ce747f0df5f3d97c97065c6a',
                 '50db8b75e8c29c9dfc42646e5165c22f31dd8e2853858686572405c3cd91cc12']
STAGE = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_iii_rrt_pcs_e2e_v1/geometry_consistent_observed')
BINARY = STAGE / 'p4_abb_iii_rrt_pcs_e2e'
BINARY_SHA = '81dac2e24b8c929c1849f60bc95b6e034ee7b4f3ec21eed5dc35595fdb60174e'
BUDGET = {'wall_s': 30, 'cpu_s': 60}
WORK_BUDGET = {'wall_s': 25, 'cpu_s': 50}
COST_BASIS = 'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
OWN = [Path(__file__).resolve(), SUPERVISOR, PRE, Path(L.__file__).resolve(), Path(B.__file__).resolve(),
       Path(B.lifecycle.__file__).resolve()]
B.RUN_NAME = RUN
B.RUN = ROOT / 'results/p4_full' / RUN
require = L.require
sha = L.sha
load = L.load
path = L.path


class Budget(L.Budget):
    def __init__(self, spec, started, cpu0):
        super().__init__({'previous_r2_wall_s': spec['prior']['wall_s'],
                          'previous_r2_cpu_s': spec['prior']['cpu_s']}, started, cpu0)
        self.wall_cap = min(25., 3600. - spec['prior']['wall_s'] - 5.)
        self.cpu_cap = min(50., 7200. - spec['prior']['cpu_s'] - 10.)
        require(min(self.wall_cap, self.cpu_cap) > 0, 'III_SOURCE_TOTAL_BUDGET_EXHAUSTED')
    def check(self):
        live = sum(B.lifecycle.live_group_cpu(p.pid) for p in self.processes if p.returncode is None)
        require(time.monotonic() - self.started < self.wall_cap
                and L.own_reaped_cpu() - self.cpu_start + live < self.cpu_cap,
                'III_SOURCE_SELF_REAPED_LIVE_GROUP_WORK_CAP')


class Session(L.Session):
    def __init__(self, target, work, budget, journal, counts):
        super().__init__(target, work, budget, journal, counts)
        self.command = [target['binary'], str(work)]
        self.work = work
    def start(self):
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
            self.budget.processes.append(self.proc)
            self.counts['source_process_started'] += 1
            row = L.stat_row(self.proc.pid)
            require(row is not None and int(row[2]) == self.proc.pid, 'REGISTERED_III_SOURCE_STAT_REQUIRED')
            self.start_ticks = int(row[19])
            require(self.start_ticks > 0, 'ACTUAL_III_SOURCE_START_TICKS_REQUIRED')
            self.register_pipes()
            self.startup_complete = True
            self.journal.add('source_process_started', pid=self.proc.pid, start_ticks=self.start_ticks,
                command=self.command, pre_model_loaded_symbol_observation='UNOBSERVED_NOT_CLAIMED')
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        self.budget.check()
        group = L.process_group_members(self.proc.pid)
        require([row['pid'] for row in group] == [self.proc.pid], 'III_START_GROUP_SINGLE_CHILD_REQUIRED')
        self.journal.add('source_start_group', members=group)
    def run_once(self, request):
        self.budget.check()
        raw = json.dumps(request, allow_nan=False, separators=(',', ':')).encode() + b'\n'
        self.request_raw = raw
        self.journal.add('single_request_exact_bytes', request=request, bytes=len(raw),
                         base64=base64.b64encode(raw).decode(), sha256=hashlib.sha256(raw).hexdigest())
        require(len(raw) < 4096 and self.proc.poll() is None, 'FINITE_SINGLE_COMPACT_III_REQUEST_REQUIRED')
        self.counts['source_request_dispatch_attempted'] += 1
        try:
            self.request_sent = os.write(self.proc.stdin.fileno(), raw)
            require(self.request_sent == len(raw), 'INCOMPLETE_REQUEST_NO_RETRY')
            self.counts['source_request_dispatched'] += 1
        finally:
            if self.proc.stdin and not self.proc.stdin.closed:
                self.proc.stdin.close()
            self.stdin_closed_after_request = True
            self.journal.add('single_request_write_and_stdin_close', actual_sent=self.request_sent,
                sent_bytes_base64=None if self.request_sent is None else base64.b64encode(raw[:self.request_sent]).decode(),
                sent_sha256=None if self.request_sent is None else hashlib.sha256(raw[:self.request_sent]).hexdigest(),
                exact_full_request_written=self.request_sent == len(raw), stdin_closed=self.proc.stdin.closed)
        while self.selector.get_map():
            self.pump()
        self.proc.wait(timeout=max(.001, self.budget.remaining()))
        # The author writes arbitrary stdout. Preserve the entire buffer before
        # explicitly consuming it; inherited finish must never silently drop it.
        self.journal.add('entire_mixed_stdout_observed', bytes=len(self.pending),
                         sha256=hashlib.sha256(self.pending).hexdigest(),
                         exact_raw_stdout_equal=self.pending == bytes(self.raw['stdout']))
        require(self.pending == bytes(self.raw['stdout']), 'WHOLE_MIXED_STDOUT_MUST_REMAIN_RETAINED')
        self.pending = b''
        require(self.proc.returncode == 0, 'III_SOURCE_NONZERO_EXIT_RETAINED_NOT_TRANSPORT_SUCCESS')
        self.finish(normal=True)
        result = load(self.work / 'result.json')
        lines = bytes(self.raw['stdout']).splitlines()
        require(lines and json.loads(lines[-1]) == result, 'RESULT_FILE_AND_FINAL_STDOUT_OBJECT_MUST_AGREE')
        self.responses = [result]
        return result


def supervisor_proof(spec, protocol):
    # Identity adaptation of audited V LOCAL proof: actual parent/argv/FD inode.
    ext = spec['external_supervision']
    raw = path(ext['metadata_path']).read_bytes().splitlines(keepends=True)[0]
    planned = json.loads(raw)
    parent = os.getppid()
    stat = L.stat_row(parent)
    argv = ['/usr/bin/time', '--quiet', '-f', '%e %U %S %x', '-o', f"/proc/self/fd/{planned['time_fd']}",
            '/usr/bin/python3', str(Path(__file__).resolve()), '--protocol', str(protocol)]
    require(stat is not None and int(stat[1]) == planned['supervisor_pid']
            and sha(Path('/proc', str(parent), 'exe')) == ext['time_binary_sha256']
            and planned['event'] == 'planned_launch' and planned['run_id'] == RUN
            and planned['protocol_sha256'] == sha(protocol) and planned['runner_sha256'] == sha(__file__)
            and planned['supervisor_source_sha256'] == sha(SUPERVISOR) and planned['argv'] == argv
            and Path('/proc', str(parent), 'cmdline').read_bytes().rstrip(b'\0').split(b'\0') == [v.encode() for v in argv],
            'ACTUAL_GNUTIME_PARENT_SOURCE_PROTOCOL_ARGV_REQUIRED')
    inode = path(ext['sibling_path']).stat()
    held = []
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


def active_d080(supervisor):
    # Thin copy of III BUILD01 active_d080; launch-proof key adapted only.
    allowed = {os.getpid(), supervisor['time_pid'], supervisor['supervisor_pid']}
    active = []
    directory = str(ROOT / 'scripts/p4_d080') + '/'
    for entry in Path('/proc').glob('[0-9]*/cmdline'):
        pid = int(entry.parent.name)
        if pid in allowed:
            continue
        try:
            parts = entry.read_bytes().split(b'\0')
        except OSError:
            continue
        exe = parts[0].decode(errors='replace') if parts else ''
        scripts = [p.decode(errors='replace') for p in parts[1:3]] if 'python' in exe else []
        resolved = []
        for script in scripts:
            if script.startswith('-'):
                continue
            try:
                resolved.append(str((Path('/proc', str(pid), 'cwd') / script).resolve(strict=True)))
            except OSError:
                continue
        if any(s.startswith(directory) and Path(s).name.startswith(('build_', 'qualify_', 'supervise_')) for s in resolved):
            active.append({'pid': pid, 'command': b' '.join(parts).decode(errors='replace')})
    return active


def preflight(spec, protocol):
    require(spec['schema'] == 'P4_D080_III_RRT_PCS_SOURCE01_FROZEN_V1' and spec['frozen'] is True
            and spec['scientific_execution_authorized'] is True and spec['independent_review_passed'] is True
            and spec['formal_execution_authorized'] is False and spec['environment'] == 'III'
            and spec['run_id'] == RUN and spec['claim_id'] == CLAIM and spec['classification'] == LABEL
            and spec['budget'] == BUDGET and spec['working_budget'] == WORK_BUDGET
            and all(spec['reviews'].values()), 'III_SINGLE_SOURCE_REVIEW_FREEZE_REQUIRED')
    require(set(spec['reviews']) == {'independent_static_review_passed', 'root_source_freeze_approved',
            'latest_actual_prior_confirmed'} and all(type(v) is bool for v in spec['reviews'].values()),
            'EXACT_BOOLEAN_REVIEW_FLAGS_REQUIRED')
    require(sha(BUILD) == BUILD_SHA and sha(BUILD_POST) == BUILD_POST_SHA, 'EXACT_III_BUILD_EVIDENCE_REQUIRED')
    build = load(BUILD)
    post = load(BUILD_POST)
    require(build['status'] == 'BUILT_NOT_QUERIED' and post['personnel_independent'] is True
            and post['checks_total'] == post['checks_passed'] == 49 and post['checks_failed'] == 0
            and post['engineering_build_qualified'] is True and post['external_supervision_qualified'] is True
            and post['execution_sha256'] == BUILD_SHA and post['source_planning_qualified'] is False
            and post['independent_path_qualified'] is False, 'BUILD49_ENGINEERING_ONLY_CERTIFICATE_REQUIRED')
    target, = build['targets']
    require(spec['target'] == {'binary': str(BINARY), 'binary_sha256': BINARY_SHA}
            and target['binary'] == str(BINARY) and target['binary_sha256'] == sha(BINARY) == BINARY_SHA,
            'EXACT_ALREADY_BUILT_III_BINARY_REQUIRED')
    for mapping in ('staged_after_sha256', 'dependencies_after_sha256'):
        require(all(spec['bound_files_sha256'].get(str(path(n))) == digest for n, digest in build[mapping].items()),
                'ALL_SAVED_III_STAGED_AND_DEPENDENCY_BYTES_REQUIRED')
    expected_meshes = {n: digest for n, digest in build['staged_after_sha256'].items()
                       if Path(n).parent == STAGE / 'simulator' and Path(n).suffix == '.tris'}
    require(len(expected_meshes) == 20 and spec['runtime_meshes_sha256'] == expected_meshes,
            'ORIGINAL_III20_RUNTIME_MESHES_REQUIRED')
    q = []
    for endpoint, digest in zip(ENDPOINTS, ENDPOINT_SHAS):
        row = load(endpoint)
        require(sha(endpoint) == digest and row['status'] == 'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED',
                'ORIGINAL_SAVED_III_A01_RECONSTRUCTED_ENDPOINT_REQUIRED')
        q.append(row['selected_q_rad'])
    low = [-2.88, -1.919, -1.919, -2.79, -2.09, -3.1416] * 2
    high = [2.88, 1.919, 1.22, 2.79, 2.09, 3.1416] * 2
    request = {'environment': 'III', 'seed': 7, 'range_rad': .8, 'goal_bias': .05, 'solve_seconds': 10.,
               'start_q12': q[0], 'goal_q12': q[1], 'bounds_low_rad': low, 'bounds_high_rad': high}
    require(L.exact(spec['request'], request) and spec['source_process_limit'] == spec['source_solve_limit'] == 1
            and spec['new_independent_model_calls'] == 0 and spec['independent_path_qualified'] is False,
            'FIXED_A01_SEED7_RANGE08_SINGLE_ORIGINAL10S_SOLVE_NO_ORACLE_REQUIRED')
    require(sha(B.SCOPE) == B.SCOPE_SHA and sha(B.OVERLAY) == B.OVERLAY_SHA
            and load(B.SCOPE)['VI_future_science_authorized'] is False
            and load(B.SCOPE)['formal_execution_authorized'] is False
            and load(B.SCOPE)['formal_table_I_D080'] == 18000, 'D080_SCOPE_REQUIRED')
    for filename in [*OWN, BUILD, BUILD_POST, LOCAL_POST, LOCAL_ADDENDUM, *ENDPOINTS, B.SCOPE, B.OVERLAY]:
        require(spec['bound_files_sha256'].get(str(filename)) == sha(filename), 'ALL_OWN_AND_SAVED_EVIDENCE_PREBOUND')
    require(all(sha(n) == digest for n, digest in spec['bound_files_sha256'].items()), 'FROZEN_ASSET_DRIFT')
    prior = B.validate_prior(spec)
    require(prior == spec['actual_charge_prior'] and all(spec['bound_files_sha256'].get(n) == digest
            for n, digest in prior['evidence_sha256'].items()), 'ALL_CURRENT_CHARGED_PRIOR_CERTIFICATES_REQUIRED')
    require(L.preload_state() == spec['system_preload_state'], 'SYSTEM_PRELOAD_CHANGED')
    require(signal.getitimer(signal.ITIMER_REAL) == (0., 0.), 'EXISTING_TIMER_REFUSE_REPLACE')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for filename in [*OWN, protocol]:
        require(subprocess.check_output(['git', 'show', commit + ':' + str(filename.relative_to(ROOT))], cwd=ROOT)
                == filename.read_bytes(), 'ALL_RUNTIME_SOURCE_AND_PROTOCOL_MUST_BE_COMMITTED')
    return commit, prior


def result_contract(result, spec, work):
    require(result['schema'] == 'P4_ABB_III_RRT_PCS_END_TO_END_DRAFT_V1'
            and result['status'] == 'SOURCE_SOLVE_RETURNED_PENDING_INDEPENDENT_PATH_AUDIT'
            and result['environment'] == 'III' and L.exact(result['request'], spec['request'])
            and result['solve_calls'] == 1 and result['formal_table_I_calls'] == 0
            and result['independent_path_qualified'] is False
            and result['solution_path_simplification'] is False, 'ONE_SOURCE_SOLVE_RETURN_CONTRACT_REQUIRED')
    require(all(type(result[n]) is bool for n in ('exact', 'approximate', 'has_solution'))
            and not (result['exact'] and result['approximate'])
            and result['has_solution'] == (result['exact'] or result['approximate']),
            'EXACT_APPROXIMATE_AND_NO_SOLUTION_MUST_REMAIN_SEPARATE')
    require(all(len(q) == 12 and all(type(v) in (int, float) and math.isfinite(v) for v in q)
                for q in result['milestones_q12']), 'FINITE_COMPLETE_ORIGINAL_MILESTONES_REQUIRED')
    require(load(work / 'request_observed.json') == spec['request'], 'DRIVER_OBSERVED_FULL_REQUEST_REQUIRED')
    reconstruction = [json.loads(line) for line in (work / 'reconstruction_attempts.jsonl').read_bytes().splitlines()]
    identify = [json.loads(line) for line in (work / 'identify_observations.jsonl').read_bytes().splitlines()]
    require(L.exact(reconstruction, result['reconstruction_attempts'])
            and len(reconstruction) == result['reconstruction_calls_completed_observed']
            and len(identify) == result['identify_observation_count'] == result['identify_calls_completed_observed']
            and [row['attempt_index'] for row in reconstruction] == list(range(len(reconstruction)))
            and [row['call_index'] for row in identify] == list(range(len(identify))),
            'COMPLETE_ORIGINAL_POSTRETURN_LOGS_MUST_MATCH_RESULT_NO_TRUNCATION')
    require(all(row['schema'] == 'P4_ABB_RRT_PCS_RECONSTRUCTION_V1'
                and row['observation'] == 'ORIGINAL_STATE_LEVEL_CALL_COMPLETED_POST_RETURN'
                and type(row['returned']) is bool for row in reconstruction)
            and all(row['schema'] == 'P4_ABB_RRT_PCS_IDENTIFY_V1'
                and row['observation'] == 'ORIGINAL_VECTOR_IDENTIFY_CALL_COMPLETED_POST_RETURN' for row in identify),
            'TRUE_FALSE_AND_POSTRETURN_OBSERVATION_PROVENANCE_REQUIRED')
    return 'SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT' if result['exact'] else 'SOURCE_NONEXACT_RETAINED'


def execute(spec, protocol):
    started = time.monotonic()
    cpu0 = L.own_reaped_cpu()
    commit, prior = preflight(spec, protocol)
    proof = supervisor_proof(spec, protocol)
    folder = ROOT / 'results/p4_full' / RUN
    claim = ROOT / 'results/p4_full' / (CLAIM + '.claim.json')
    require(not folder.exists() and not claim.exists() and not L.active_p4() and not active_d080(proof),
            'FRESH_SINGLE_III_SOURCE_NO_OTHER_P4_OR_D080')
    budget = None
    journal = None
    sessions = []
    diagnostics = []
    copied = {}
    error = None
    counts = Counter()
    record = {'schema': 'P4_D080_III_RRT_PCS_SOURCE01_EXECUTION_V1', 'run_id': RUN, 'classification': LABEL,
              'status': 'STOP_PREFIX_RETAINED', 'source_commit': commit, 'protocol_sha256': sha(protocol),
              'protocol': str(protocol.relative_to(ROOT)), 'claim': str(claim.relative_to(ROOT)),
              'actual_charge_prior': prior, 'budget': BUDGET, 'working_budget': WORK_BUDGET,
              'supervisor_launch_proof': proof, 'bound_files_sha256': spec['bound_files_sha256'],
              'new_external_charge_basis': COST_BASIS, 'independent_path_qualified': False,
              'continuous_collision_certificate': False, 'formal_table_I_calls': 0,
              'new_VI_candidate_constructions': 0, 'new_independent_model_calls': 0,
              'source_reported_solve_calls': None, 'solve_calls_from_result': None,
              'source_actual_internal_call_starts': 'UNOBSERVED',
              'source_FK_IK_PQP_started': 'UNOBSERVED_NO_START_HOOK',
              'pre_model_loaded_symbol_observation': 'UNOBSERVED_NOT_CLAIMED',
              'source_implementation': 'RECONSTRUCTED_ENDPOINTS_AND_CORRECTED_KINEMATICS_ORIGINAL_RRT_PCS_CONTROL',
              'independent_saved_POST_required': True, 'external_supervision_qualified': False}
    try:
        L.durable_new(claim, {'run_id': RUN, 'source_commit': commit, 'protocol_sha256': sha(protocol),
                             'budget': BUDGET, 'no_retry_reset_resume': True})
        record['claim_sha256'] = sha(claim)
        folder.mkdir()
        journal = L.Journal(folder / 'evidence.jsonl')
        budget = Budget(spec, started, cpu0)
        budget.start()
        budget.check()
        work = folder / 'runtime'
        (work / 'simulator').mkdir(parents=True)
        for name, digest in spec['runtime_meshes_sha256'].items():
            budget.check()
            filename = work / 'simulator' / Path(name).name
            with filename.open('xb') as stream:
                stream.write(path(name).read_bytes())
                stream.flush()
                os.fsync(stream.fileno())
            require(sha(filename) == digest, 'RUNTIME_III_MESH_BYTES_CHANGED')
            copied[str(filename)] = digest
        session = Session(spec['target'], work, budget, journal, counts)
        sessions.append(session)  # Register object before an interruptible start.
        session.start()
        result = session.run_once(spec['request'])
        record['source_reported_solve_calls'] = result.get('solve_calls')
        record['source_exact'] = result.get('exact')
        record['source_approximate'] = result.get('approximate')
        record['source_solution_difference'] = result.get('solution_difference')
        record['source_result_sha256'] = sha(work / 'result.json')
        L.durable_new(folder / 'parsed_source_result.json', result)
        record['status'] = result_contract(result, spec, work)
        record['solve_calls_from_result'] = result['solve_calls']
        record['source_reconstruction_calls_completed_observed'] = result['reconstruction_calls_completed_observed']
        record['source_reconstruction_true_started'] = result['reconstruction_true_started']
        record['source_identify_calls_completed_observed'] = result['identify_calls_completed_observed']
        record['source_identify_true_started'] = result['identify_true_started']
    except BaseException as exception:
        error = exception
        record['termination_reason'] = repr(exception)
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
            'pipe_EOF_observed': s.pipe_EOF_observed, 'request_bytes': None if s.request_raw is None else len(s.request_raw),
            'request_sent': s.request_sent, 'stdin_closed_after_request': s.stdin_closed_after_request}
            for s in sessions if s.proc is not None]
        try:
            require(all(s.proc is None or (s.proc.returncode is not None and not L.process_group_members(s.proc.pid)
                    and all(s.pipe_EOF_observed.values())) for s in sessions), 'ALL_REAL_WORKERS_REAPED_EMPTY_DUAL_EOF_REQUIRED')
            if record['status'].startswith('SOURCE_'):
                require(len(sessions) == 1 and sessions[0].proc.returncode == 0
                        and counts['source_request_dispatched'] == 1, 'ONE_EXIT0_SOURCE_COMPLETE_WRITE_REQUIRED')
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
                        with (folder / f'process{index}_{channel}.bin').open('xb') as stream:
                            stream.write(raw)
                            stream.flush()
                            os.fsync(stream.fileno())
                    if session.request_raw is not None:
                        with (folder / f'process{index}_request.bin').open('xb') as stream:
                            stream.write(session.request_raw)
                            stream.flush()
                            os.fsync(stream.fileno())
                if journal is not None:
                    journal.add('final_counts', counts=dict(counts), diagnostics=diagnostics)
                    journal.finish()
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
            receipt = {'schema': 'P4_D080_III_RRT_PCS_SOURCE01_COST_RECEIPT_V1', 'execution_sha256': sha(folder / 'execution.json'),
                'status': record['status'], 'wall_s_through_execution_persistence': time.monotonic() - started,
                'cpu_s_through_execution_persistence': L.own_reaped_cpu() - cpu0,
                'last_receipt_persistence_tail': 'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',
                'external_supervision_qualified': False}
            if receipt['wall_s_through_execution_persistence'] >= 30 or receipt['cpu_s_through_execution_persistence'] >= 60:
                receipt['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'
            L.durable_new(folder / 'cost_receipt.json', receipt)
            record['terminal_receipt_status'] = receipt['status']
    print(json.dumps({'status': record.get('terminal_receipt_status', record['status']),
                      'independent_POST_required': True, 'independent_path_qualified': False}))
    if error is not None:
        raise error
    require(record.get('terminal_receipt_status', '').startswith('SOURCE_'), 'III_SINGLE_SOURCE_DID_NOT_COMPLETE')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, required=True)
    protocol = parser.parse_args().protocol.resolve()
    execute(load(protocol), protocol)


if __name__ == '__main__':
    main()
