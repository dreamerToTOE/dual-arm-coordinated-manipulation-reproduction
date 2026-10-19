#!/usr/bin/env python3
"""V single SOURCE-entry thin adapter. No import-time binary/model calls.

The III audited transport/budget/proof and complete execution finalizer are reused.
V-specific preflight/result gates bind actual BUILD/POST only after they exist.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'scripts'), str(Path(__file__).resolve().parent)]
import qualify_iii_rrt_pcs_source01_v1_draft as I
import validate_prior_preflight_recovery_v3 as P
L = I.L
B = I.B
RUN = '20261019_R2_D080_V_RRT_PCS_SOURCE01_V4'
CLAIM = 'P4_D080_V_RRT_PCS_SOURCE01_V4_A02_SEED7_30W60CPU_20261019'
LABEL = 'CORRECTED_COMAU_APC_ALIGNED_V3_RECONSTRUCTED_A02_ORIGINAL_RRT_CONTROL'
PRE = ROOT / 'reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_V4_PRE_20261019.md'
SUPERVISOR = ROOT / 'scripts/p4_d080/supervise_v_rrt_pcs_source01_v4_draft.py'
BUILD = ROOT / 'results/p4_full/20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY_V4/execution.json'
BUILD_POST = ROOT / 'reports/P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_V4_SAVED_INDEPENDENT_POST_20261019.json'
LOCAL_PROTOCOL = ROOT / 'configs/p4_d080/v_pcs_local01_v1.json'
LOCAL_POST = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL01_SAVED_INDEPENDENT_POST_20261018.md'
LOCAL_ADDENDUM = ROOT / 'reports/P4_D080_ENV_V_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.md'
ENDPOINTS = [ROOT / ('results/p4_full/20261015_R2_ENDPOINT_COLLISION_REPLAY01/V_' + n + '.json') for n in ('start', 'goal')]
ENDPOINT_SHAS = ['f906a6b61999c71efe15c8d86188edbded704d66dcba18f9833d940ccfa6c405',
                 'feae5fd78837327db9c83d66621e2aa4fc9eec72a46c0d0dfc1e98cbc9d88737']
STAGE = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_rrt_pcs_e2e_v4')
BINARY = STAGE / 'v_rrt_pcs_e2e'
BUDGET = {'wall_s': 30, 'cpu_s': 60}
WORK_BUDGET = {'wall_s': 25, 'cpu_s': 50}
COST_BASIS = I.COST_BASIS
CAP_NAMES = ('public_request', 'project_fixed', 'identify', 'is_valid_rbs', 'rbs',
             'reconstruct', 'native_fk', 'native_ik', 'specific_ik', 'limits',
             'collision', 'pqp', 'mesh_load', 'records')
RESOURCE_CAPS = dict.fromkeys(CAP_NAMES, 1000000)
III_SOURCE = Path(I.__file__).resolve()
OWN = [Path(__file__).resolve(), SUPERVISOR, PRE, III_SOURCE, Path(L.__file__).resolve(),
       Path(B.__file__).resolve(), Path(B.lifecycle.__file__).resolve(), Path(P.__file__).resolve()]
# Rebound metadata makes the original proof check the actual V entry/launch.
# The original III module path remains prebound in OWN; no III source is edited.
I.__file__ = str(Path(__file__).resolve())
I.RUN, I.CLAIM, I.LABEL, I.PRE, I.SUPERVISOR, I.OWN = RUN, CLAIM, LABEL, PRE, SUPERVISOR, OWN
B.RUN_NAME = RUN
B.RUN = ROOT / 'results/p4_full' / RUN
Budget, Session = I.Budget, I.Session
supervisor_proof, active_d080 = I.supervisor_proof, I.active_d080
require, sha, load, path = L.require, L.sha, L.load, L.path


def validate_prior(spec):
    return P.validate_prior(spec, RUN, ROOT / 'results/p4_full' / RUN)


def preflight(spec, protocol):
    require(spec['schema'] == 'P4_D080_V_RRT_PCS_SOURCE01_FROZEN_V1' and spec['frozen'] is True
            and spec['scientific_execution_authorized'] is True and spec['independent_review_passed'] is True
            and spec['formal_execution_authorized'] is False and spec['environment'] == 'V'
            and spec['run_id'] == RUN and spec['claim_id'] == CLAIM and spec['classification'] == LABEL
            and spec['budget'] == BUDGET and spec['working_budget'] == WORK_BUDGET
            and all(spec['reviews'].values()), 'V_SINGLE_SOURCE_REVIEW_FREEZE_REQUIRED')
    require(set(spec['reviews']) == {'independent_static_review_passed', 'root_source_freeze_approved',
            'latest_actual_prior_confirmed'} and all(type(v) is bool for v in spec['reviews'].values()),
            'EXACT_BOOLEAN_REVIEW_FLAGS_REQUIRED')
    assets = spec['build_assets']
    require(assets['execution'] == str(BUILD.relative_to(ROOT))
            and assets['personnel_independent_POST'] == str(BUILD_POST.relative_to(ROOT))
            and sha(BUILD) == assets['execution_sha256'] and sha(BUILD_POST) == assets['post_sha256'],
            'ACTUAL_V_BUILD_AND_INDEPENDENT_POST_MUST_BE_BOUND_AFTER_COMPLETION')
    build, post = load(BUILD), load(BUILD_POST)
    require(type(assets['post_checks_total']) is int and assets['post_checks_total'] > 0
            and build['status'] == 'BUILT_NOT_QUERIED' and build['environment'] == 'V'
            and post['personnel_independent'] is True
            and post['checks_total'] == post['checks_passed'] == assets['post_checks_total']
            and post['checks_failed'] == 0 and post['engineering_build_qualified'] is True
            and post['external_supervision_qualified'] is True
            and post['execution_sha256'] == assets['execution_sha256']
            and post['source_planning_qualified'] is False and post['independent_path_qualified'] is False,
            'ACTUAL_V_ENGINEERING_ONLY_CERTIFICATE_REQUIRED_NO_ANTICIPATED_PASS')
    target, = build['targets']
    require(spec['target']['binary'] == target['binary'] == str(BINARY)
            and spec['target']['binary_sha256'] == target['binary_sha256'] == sha(BINARY),
            'EXACT_ALREADY_BUILT_V_BINARY_REQUIRED')
    for mapping in ('bound_files_after_sha256', 'staged_after_sha256', 'dependencies_after_sha256'):
        require(all(spec['bound_files_sha256'].get(str(path(n))) == digest for n, digest in build[mapping].items()),
                'ALL_ACTUAL_V_BUILD_BOUND_STAGED_DEPENDENCY_BYTES_REQUIRED')
    local = load(LOCAL_PROTOCOL)
    require(len(local['runtime_meshes_sha256']) == 27
            and spec['runtime_meshes_sha256'] == local['runtime_meshes_sha256'],
            'EXACT_ORIGINAL_V27_RUNTIME_MESHES_REUSE_REQUIRED')
    q = []
    for endpoint, digest in zip(ENDPOINTS, ENDPOINT_SHAS):
        row = load(endpoint)
        require(sha(endpoint) == digest and row['status'] == 'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'
                and row['environment'] == 'V' and row['classification'] == 'RECONSTRUCTED'
                and row['active_coordinates_exactly_unchanged'] is True
                and row['collision']['selected_variant'] == 'aligned' and row['collision']['collision'] is False,
                'ORIGINAL_SAVED_V_A02_RECONSTRUCTED_ENDPOINT_REQUIRED')
        q.append(row['selected_q_rad'])
    low = [-3.1416, -1.0472, -3.1416 / 2, -3.1416, -2.0944, -3.1416] * 2
    high = [3.1416, 2.1871, 1.3090, 3.1416, 2.0944, 3.1416] * 2
    request = {'schema': 'P4_D080_V_RRT_PCS_ONE_SHOT_FROZEN_V1', 'frozen': True,
               'scientific_execution_authorized': True, 'independent_review_passed': True,
               'formal_execution_authorized': False, 'environment': 'V', 'seed': 7,
               'range_rad': .2, 'goal_bias': .05, 'solve_seconds': 10., 'caps': RESOURCE_CAPS,
               'start_q12': q[0], 'goal_q12': q[1], 'bounds_low_rad': low, 'bounds_high_rad': high}
    require(L.exact(spec['request'], request) and spec['source_process_limit'] == spec['source_solve_limit'] == 1
            and spec['new_independent_model_calls'] == 0 and spec['independent_path_qualified'] is False
            and spec['resource_caps_only'] is True and spec['cap_reached_action'] == 'FAIL_RETAIN_PREFIX_NO_RETRY',
            'FIXED_A02_SEED7_RANGE02_ORIGINAL10S_SOLVE_AND_FAIL_CLOSED_RESOURCE_CAPS_REQUIRED')
    require(sha(B.SCOPE) == B.SCOPE_SHA and sha(B.OVERLAY) == B.OVERLAY_SHA
            and load(B.SCOPE)['VI_future_science_authorized'] is False
            and load(B.SCOPE)['formal_execution_authorized'] is False
            and load(B.SCOPE)['formal_table_I_D080'] == 18000, 'D080_SCOPE_REQUIRED')
    for filename in [*OWN, BUILD, BUILD_POST, LOCAL_PROTOCOL, LOCAL_POST, LOCAL_ADDENDUM, *ENDPOINTS, B.SCOPE, B.OVERLAY]:
        require(spec['bound_files_sha256'].get(str(filename)) == sha(filename), 'ALL_OWN_AND_SAVED_EVIDENCE_PREBOUND')
    require(all(sha(n) == digest for n, digest in spec['bound_files_sha256'].items()), 'FROZEN_ASSET_DRIFT')
    prior = validate_prior(spec)
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
    require(result['schema'] == 'P4_D080_V_RRT_PCS_END_TO_END_DRAFT_V1'
            and result['status'] == 'SOURCE_SOLVE_RETURNED_PENDING_INDEPENDENT_PATH_AUDIT'
            and result['environment'] == 'V' and result['classification'] == LABEL
            and L.exact(result['request'], spec['request']) and result['solve_calls'] == 1
            and result['formal_table_I_calls'] == 0 and result['independent_path_qualified'] is False
            and result['full_physical_geometry_or_CCD_qualified'] is False
            and result['full_solve_plain_trace_consistency_qualified'] is False
            and result['source_observation_trace_mode'] == 1
            and result['state_validity_callback'] == 'ORIGINAL_MAIN_ALWAYS_TRUE_NO_FK'
            and result['solution_path_simplification'] is False, 'V_ONE_SOURCE_SOLVE_RETURN_CONTRACT_REQUIRED')
    # The existing II observation ABI is intentionally retained by the V driver.
    legacy = dict(result)
    legacy.update(schema='P4_ABB_III_RRT_PCS_END_TO_END_DRAFT_V1', environment='III')
    inherited_status = I.result_contract(legacy, spec, work)
    records = result['source_observed_records']
    counts = result['source_observed_counts_started']
    require(isinstance(records, list) and isinstance(counts, dict)
            and [row['id'] for row in records] == list(range(1, len(records) + 1))
            and all(row['kind'] in CAP_NAMES and row['kind'] != 'records' and row['event'] == 'completed' for row in records),
            'COMPLETE_DISTINCT_V_OBSERVER_LIFETIMES_REQUIRED')
    expected_counts = dict(Counter(row['kind'] for row in records), records=len(records))
    require(all(type(v) is int and v >= 0 and v <= RESOURCE_CAPS[n] for n, v in counts.items())
            and counts == expected_counts, 'V_REAL_ENTER_COUNTS_MATCH_FULL_RECORDS_AND_RESOURCE_CAPS')
    # Raw streams persist later in the unchanged audited finalizer.
    traces = [json.loads(line[len(b'P4_V_PCS_TRACE '):]) for line in ACTIVE_SESSION.raw['stderr'].splitlines()
              if line.startswith(b'P4_V_PCS_TRACE ')]
    entered = [row for row in traces if row['event'] == 'entered']
    completed = [row for row in traces if row['event'] == 'completed']
    require(len(traces) == 2 * len(records) and len(entered) == len(completed) == len(records)
            and entered == [dict(event='entered', id=row['id'], kind=row['kind'], args=row['args']) for row in records]
            and {row['id']: row for row in completed} == {row['id']: dict(event='completed', id=row['id'], kind=row['kind'], result=row['result']) for row in records},
            'V_ENTIRE_TRACE_ENTRY_AND_COMPLETION_AGREES_WITH_RESULT_NO_CAP_NO_TRUNCATION')
    return inherited_status


def execute(spec, protocol):
    started = time.monotonic()
    cpu0 = L.own_reaped_cpu()
    commit, prior = preflight(spec, protocol)
    proof = supervisor_proof(spec, protocol)
    folder = ROOT / 'results/p4_full' / RUN
    claim = ROOT / 'results/p4_full' / (CLAIM + '.claim.json')
    require(not folder.exists() and not claim.exists() and not L.active_p4() and not active_d080(proof),
            'FRESH_SINGLE_V_SOURCE_NO_OTHER_P4_OR_D080')
    budget = None
    journal = None
    sessions = []
    diagnostics = []
    copied = {}
    error = None
    counts = Counter()
    record = {'schema': 'P4_D080_V_RRT_PCS_SOURCE01_EXECUTION_V1', 'run_id': RUN, 'classification': LABEL, 'environment': 'V',
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
            require(sha(filename) == digest, 'RUNTIME_V_MESH_BYTES_CHANGED')
            copied[str(filename)] = digest
        session = Session(spec['target'], work, budget, journal, counts)
        sessions.append(session)  # Register object before an interruptible start.
        session.start()
        global ACTIVE_SESSION
        ACTIVE_SESSION = session
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
        record['source_observed_counts_started'] = result['source_observed_counts_started']
        record['source_FK_IK_PQP_started'] = {n: result['source_observed_counts_started'].get(n, 0) for n in ('native_fk', 'native_ik', 'specific_ik', 'pqp')}
        record['source_actual_internal_call_starts'] = 'V_OBSERVER_ENTRY_RECORDS_WITH_LEGACY_POSTRETURN_ABI_SEPARATE'
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
            record['prior_after'] = validate_prior(spec)
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
            receipt = {'schema': 'P4_D080_V_RRT_PCS_SOURCE01_COST_RECEIPT_V1', 'execution_sha256': sha(folder / 'execution.json'),
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
    require(record.get('terminal_receipt_status', '').startswith('SOURCE_'), 'V_SINGLE_SOURCE_DID_NOT_COMPLETE')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, required=True)
    protocol = parser.parse_args().protocol.resolve()
    execute(load(protocol), protocol)


if __name__ == '__main__':
    main()
