#!/usr/bin/env python3
"""Finite IV NR local-property qualification; no replacement of old failures.

Draft operations only read saved evidence. Scientific execution requires a
frozen, hash-bound protocol, qualified reconstructed centers and a fresh fixed
claim. The imported unconstrained NR is unchanged. No IK, random search,
bound-aware solver, h adjustment, planner or old-case rerun is implemented.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

# Set before importing NumPy. This is execution accounting, not an algorithm change.
THREAD_KEYS = ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
               'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')
THREAD_ENV_BEFORE = {k: os.environ.get(k) for k in THREAD_KEYS}
for _key in THREAD_KEYS:
    os.environ[_key] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'scripts'))
import numpy as np
from recover_p4_full_r2_endpoints import (
    arm_fk, bounds_for, branch_identity, closure_metrics, digest, grasps_for,
    limit_score, matrix_error, save_new,
)
from baselines.p4_full.geometry_consistent.physical_nr import project_nr, source_limits
from baselines.p4_full.geometry_consistent.collision_adapter import check_collision, close_sessions

SCHEMA = 'P4_R2_IV_NR_LOCAL_PROPERTY_QUALIFICATION_V1'
RUN_ID = '20261015_R2_IV_NR_LOCAL01'
CLAIM_ID = 'P4_R2_IV_NR_LOCAL_24_60W_120CPU_20261015'
A_RUN = 'results/p4_full/20261015_R2_ENDPOINT_COLLISION_REPLAY01'
OLD = 'results/p4_full/20261015_R2_SPATIAL01/IV'
BINARY = 'build/p4_full/20261015_R2_SPATIAL01/comau_iv_batch'
V3 = '/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
EXPECTED_OLD = [('original_input', '2'), ('original_input', '4'), ('original_input', '8'),
                ('known_closed_neighborhood', 'start_3'),
                ('known_closed_neighborhood', 'start_6'),
                ('known_closed_neighborhood', 'start_8')]
GATES = {'position_maxabs_mm': 1e-5, 'rotation_matrix_maxabs': 1e-5,
         'native_fk_position_maxabs_mm': 1e-7, 'native_fk_rotation_matrix_maxabs': 1e-10,
         'nr_max_iterations': 10000, 'nr_svd_relative': 1e-12,
         'branch_epsilon_diagnostic_only': 64*float(np.finfo(float).eps)}
SOURCE_FILES = [str(Path(__file__).relative_to(ROOT)),
    'scripts/recover_p4_full_r2_endpoints.py',
    'baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/geometry_consistent/collision_adapter.py',
    'baselines/p4_full/analyze_comau_native_qualification.py',
    'baselines/p4_full/abb_independent_oracle.py', BINARY]


def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT/p


def cpu_seconds():
    a, b = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime


def ledger_paths():
    return sorted((ROOT/'results/p4_full').glob('20261015_R2_*/execution.json'))


def saved_centers():
    """Read saved arrays and calculate bound margins only; no FK/NR call."""
    result = []
    bounds = bounds_for('IV')
    for endpoint, index, branch in [('start', 22, 1), ('goal', 44, 3)]:
        path = f'{A_RUN}/IV_{endpoint}.json'
        row = json.loads(resolve(path).read_text())
        if (row['status'] != 'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'
                or row['source_candidate']['index'] != index or row['branch'] != [branch]
                or row['collision'].get('status') != 'CHECKED'
                or row['collision'].get('collision') is not False
                or not row['limits']['legal']):
            raise ValueError('A_CENTER_SOURCE_POLICY_QUALIFICATION_REQUIRED')
        q = row['selected_q_rad']
        original = json.loads(resolve(row['source_candidate']['path']).read_text())
        original_candidate = next(c for c in original['candidates_all'] if c['candidate_index'] == index)
        if (original_candidate['q_rad'] != q or original_candidate['branch'] != [branch]
                or not original_candidate['pre_collision_eligible']
                or not original_candidate['same_original_branch']
                or not original_candidate['active_coordinates_exactly_unchanged']):
            raise ValueError('A_ORIGINAL_SAME_BRANCH_CANDIDATE_CHANGED')
        if len(q) != 12 or not all(math.isfinite(x) for x in q):
            raise ValueError('INVALID_CENTER_ARRAY')
        margins = [min(x-lo, hi-x) for x, (lo, hi) in zip(q, bounds)]
        if min(margins) <= 0:
            raise ValueError('POSITIVE_CENTER_LIMIT_MARGIN_REQUIRED')
        result.append({'endpoint': endpoint, 'source': path,
            'source_candidate_index': index, 'center_passive_branch': branch,
            'q_rad': q, 'bound_margins_rad': margins,
            'minimum_all12_bound_margin_rad': min(margins),
            'h_rad': min(1e-4, min(margins)/8.)})
    return result


def old_negative_records():
    rows = json.loads(resolve(OLD+'/observations.json').read_text())
    selected = [r for r in rows if r['kind'] == 'nr_reference'
                and (r['fixture_kind'], r['fixture']) in EXPECTED_OLD]
    if ([(r['fixture_kind'], r['fixture']) for r in selected] != EXPECTED_OLD
            or any(r['result']['status'] != 'CLOSED_BUT_JOINT_LIMIT_REJECTED' for r in selected)):
        raise ValueError('SAVED_SIX_REJECTIONS_CHANGED')
    checks = json.loads(resolve(OLD+'/checks.json').read_text())
    failed = [c['check'] for c in checks if not c['passed']]
    if sorted(failed) != sorted(['NR_positive_start_3', 'NR_positive_start_6', 'NR_positive_start_8']):
        raise ValueError('SAVED_THREE_FAIL_GATES_CHANGED')
    return {'source': OLD+'/observations.json', 'rerun_nr_calls': 0,
            'original_rejections_retained': 6, 'original_failed_positive_gates_retained': failed,
            'records_unchanged': selected}


def fixed_inputs(centers):
    """Freeze the actual24 arrays, without evaluating any model or solver."""
    rows = []
    for center in centers:
        for coordinate in range(6):
            for sign in (1, -1):
                q = list(center['q_rad'])
                q[coordinate] += sign*center['h_rad']
                if not limit_score(q, 'IV')['legal']:
                    raise ValueError('FIXED_INPUT_NOT_SOURCE_BOUND_LEGAL')
                rows.append({'case_id': center['endpoint']+'_q'+str(coordinate+1)
                             +('_plus' if sign > 0 else '_minus'),
                    'center_endpoint': center['endpoint'], 'coordinate0': coordinate,
                    'sign': sign, 'h_rad_frozen': center['h_rad'], 'input_q_rad': q})
    return rows


def draft_protocol():
    ledgers = ledger_paths()
    paths = SOURCE_FILES+[V3, f'{A_RUN}/execution.json', OLD+'/observations.json',
        OLD+'/checks.json', 'reports/P4_FULL_R2_IV_NR_ROOT_CAUSE_RECOVERY_20261015.md',
        'reports/P4_FULL_R2_IV_NR_SAVED_ROOT_CAUSE_20261015.json',
        'results/p4_full/20261015_R2_COLLISION_CONTROLS01/result.json',
        'configs/p4_full/r2_endpoint_collision_replay_v1.json',
        'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/IV_start.json',
        'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/IV_goal.json',
        'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/execution.json']
    centers = saved_centers()
    paths += [c['source'] for c in centers]
    paths += [str(p.relative_to(ROOT)) for p in ledgers]
    values = [json.loads(p.read_text()) for p in ledgers]
    old_negative_records()
    return {'schema': SCHEMA, 'frozen': False, 'run_id': RUN_ID, 'claim_id': CLAIM_ID,
        'classification': 'RECONSTRUCTED / INDEPENDENT-NR-REFERENCE / FINITE-LOCAL-PROPERTY',
        'environment': 'IV', 'centers': centers, 'fixed_inputs': fixed_inputs(centers),
        'h_rule': 'Per center min(1e-4 rad, minimum all12 original source-bound margin/8); numeric h frozen before execution. No h change after results.',
        'inputs': 'For start then goal, arm1 coordinates0..5 ascending, sign+1 then-1. One coordinate shifts by frozen h; all other11 exact center values. Exactly24 NR inputs; centers are reused witnesses, not extra NR calls.',
        'solver': 'Unchanged physical_nr.project_nr: full12-coordinate undamped unconstrained Moore-Penrose update, source mm/rad, original periodic_chart and post-limit rejection. No fixed-active restriction inside NR, damping, line search, nullspace/bound strategy, IK fallback or root selection.',
        'gates': GATES, 'budget': {'max_nr_calls': 24, 'max_collision_adapter_calls': 24,
            'max_native_fk_rows': 52, 'wall_s': 60., 'cpu_s': 120.,
            'r2_total_wall_s': 3600., 'r2_total_cpu_s': 7200.},
        'collision_manifest': V3,
        'collision_scope': 'Qualified original discrete mesh/pair/8mm source policy only; no omitted-pair, complete physical geometry or continuous-collision certificate.',
        'old_rejections_policy': 'Read-only snapshot of the six saved rejections and three positive FAIL gates. Zero reruns, replacements or changes to old counts.',
        'branch_policy': 'Centers are original-same-branch reconstructed fixtures. Record output branch identity and changes as diagnostics; original full-coordinate NR has no fixed branch gate.',
        'ordinary_failure_policy': 'Attempt the frozen24 inputs within budget even after ordinary convergence/limit/collision rejection. Keep every candidate/trace. Any such failure makes this finite group FAIL and blocks downstream; never replace a case or change h.',
        'stop_conditions': ['source/hash/ledger/center mismatch before execution',
            'nonfinite candidate or unexpected NR/chart/runtime status',
            'native FK interface failure or native/independent FK contradiction',
            'NR CONVERGED but independent closure or original limits fail',
            'collision query error/unknown or source geometry mismatch',
            'wall/CPU/count cap; retain prefix, mark unexecuted cases, never restart claim'],
        'conclusion_scope': 'Only these24 fixed axis inputs near two reconstructed centers. Bound margin proves input legality only, not NR output success. Does not replace original +/-0.01 group, prove a whole neighborhood, fair projection speed, RBS or planning success.',
        'new_ik_sampling_planning_calls': 0,
        'prior_executions': [str(p.relative_to(ROOT)) for p in ledgers],
        'previous_r2_wall_s': math.fsum(float(v['wall_s']) for v in values),
        'previous_r2_cpu_s': math.fsum(float(v['cpu_s']) for v in values),
        'bound_files_sha256': {p: digest(resolve(p)) for p in dict.fromkeys(paths)}}


def validate(spec, *, frozen):
    if spec.get('schema') != SCHEMA or (frozen and spec.get('frozen') is not True):
        raise ValueError('FROZEN_PROTOCOL_REQUIRED')
    expected = draft_protocol()
    expected['frozen'] = spec.get('frozen')
    if spec != expected:
        raise ValueError('DRAFT_CONTRACT_OR_BOUND_EVIDENCE_CHANGED')
    if any(digest(resolve(p)) != h for p, h in spec['bound_files_sha256'].items()):
        raise ValueError('BOUND_FILE_CHANGED')
    if spec['previous_r2_wall_s']+60 > 3600 or spec['previous_r2_cpu_s']+120 > 7200:
        raise ValueError('R2_TOTAL_BUDGET_INSUFFICIENT')
    if not np.array_equal(source_limits('IV'), np.asarray(bounds_for('IV'))):
        raise ValueError('INDEPENDENT_SOURCE_BOUND_TRANSCRIPTION_DISAGREES')
    controls = json.loads(resolve('results/p4_full/20261015_R2_COLLISION_CONTROLS01/result.json').read_text())
    a = json.loads(resolve(A_RUN+'/execution.json').read_text())
    if (controls.get('passed') is not True or controls.get('status') != 'SOURCE_POLICY_QUALIFIED'
            or a.get('bound_files_unchanged') is not True
            or a.get('endpoint_status_counts') != {'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED': 4}):
        raise ValueError('SOURCE_COLLISION_PRECONDITIONS_NOT_PASSED')
    manifest = json.loads(resolve(V3).read_text())
    for variant in ('native', 'aligned'):
        entry = next(e for e in manifest['entries'] if e['model'] == 'IV' and e['variant'] == variant)
        if (entry.get('exit_code') != 0
                or entry.get('source_equal_to_v2_after_removing_pose_observations') is not True
                or entry.get('all_active_source_pair_arguments_preserved') is not True
                or digest(entry['binary']) != entry['binary_sha256']):
            raise ValueError('IV_COLLISION_V3_PROVENANCE_OR_BINARY_CHANGED')


class Budget:
    def __init__(self, spec):
        self.spec, self.start, self.cpu_start = spec, time.monotonic(), cpu_seconds()

    def remaining(self):
        wall = self.spec['budget']['wall_s']-(time.monotonic()-self.start)
        cpu = self.spec['budget']['cpu_s']-(cpu_seconds()-self.cpu_start)
        if min(wall, cpu) <= 0:
            raise TimeoutError('IV_NR_LOCAL_WALL_OR_CPU_CAP')
        return min(wall, cpu)


def native_crosscheck(q, tag, folder, budget, execution):
    inp, out = folder/(tag+'_native_input.txt'), folder/(tag+'_native_output.jsonl')
    text = '\n'.join('F '+str(arm)+' '+' '.join(format(v, '.17g') for v in q[(arm-1)*6:arm*6])
                     for arm in (1, 2))+'\n'
    with inp.open('x') as stream:
        stream.write(text)
    command = [str(ROOT/BINARY), str(out)]
    execution['native_fk_rows_started'] += 2
    if execution['native_fk_rows_started'] > 52:
        raise ValueError('NATIVE_FK_COUNT_CAP')
    with inp.open() as fin, (folder/(tag+'_native_process.log')).open('x') as log:
        process = subprocess.run(command, stdin=fin, stdout=log, stderr=subprocess.STDOUT,
                                 cwd=ROOT, timeout=budget.remaining())
    if process.returncode:
        raise RuntimeError('NATIVE_FK_PROCESS_FAILURE')
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    if len(rows) != 2:
        raise RuntimeError('NATIVE_FK_CARDINALITY')
    comparisons, poses = [], []
    for arm, row in enumerate(rows, 1):
        if (row.get('model') != 4 or row.get('environment') != 'IV' or row.get('op') != 'F'
                or row.get('arm') != arm or row.get('q') != list(q[(arm-1)*6:arm*6])
                or not row.get('success') or not row.get('finite') or row.get('error')):
            raise RuntimeError('NATIVE_FK_INTERFACE')
        pose = np.asarray(row['T'], dtype=float)
        if pose.shape != (4, 4) or not np.isfinite(pose).all():
            raise RuntimeError('NONFINITE_NATIVE_FK')
        err = matrix_error(pose, arm_fk(q[(arm-1)*6:arm*6], 'IV', arm))
        comparisons.append({'arm': arm, **err}); poses.append(pose)
        if (err['position_max_abs'] > GATES['native_fk_position_maxabs_mm']
                or err['rotation_matrix_max_abs'] > GATES['native_fk_rotation_matrix_maxabs']):
            raise RuntimeError('NATIVE_INDEPENDENT_FK_CONTRADICTION')
    execution['native_fk_rows_completed'] += 2
    error = matrix_error(poses[1], poses[0]@grasps_for('IV')[0]@np.diag([-1., -1., 1., 1.]))
    return {'command': command, 'native_vs_independent_fk': comparisons,
            'native_loop_error': error,
            'closed': error['position_max_abs'] <= 1e-5 and error['rotation_matrix_max_abs'] <= 1e-5}


def execute(spec, protocol):
    validate(spec, frozen=True)
    # Bind the recorded HEAD to the executable sources and the frozen protocol.
    # Unrelated worktree changes may remain, but these inputs must be committed.
    for path in [*SOURCE_FILES[:-1], str(protocol.resolve().relative_to(ROOT))]:
        committed = subprocess.check_output(['git', 'show', 'HEAD:'+path], cwd=ROOT)
        if committed != resolve(path).read_bytes():
            raise ValueError('EXECUTABLE_SOURCE_OR_PROTOCOL_NOT_COMMITTED '+path)
    claim = ROOT/'results/p4_full'/(CLAIM_ID+'.claim.json')
    folder = ROOT/'results/p4_full'/RUN_ID
    if folder.exists():
        raise ValueError('EXISTING_RUN_DO_NOT_RERUN')
    save_new(claim, {'schema': SCHEMA, 'claim_id': CLAIM_ID, 'run_id': RUN_ID,
                    'protocol_sha256': digest(protocol), 'one_shot': True,
                    'note': 'A crash consumes this claim; preserve prefix, no automatic relaunch.'})
    folder.mkdir(exist_ok=False)
    budget = Budget(spec)
    execution = {'schema': SCHEMA, 'run_id': RUN_ID, 'claim_id': CLAIM_ID,
        'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'command': [sys.executable, str(Path(__file__).resolve()), '--protocol', str(protocol.resolve())],
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'git_status_at_start': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True),
        'protocol_sha256': digest(protocol), 'source_sha256': digest(__file__),
        'bound_files_sha256': spec['bound_files_sha256'],
        'thread_environment_before': THREAD_ENV_BEFORE, 'thread_environment_run': {k: os.environ[k] for k in THREAD_KEYS},
        'nr_calls_started': 0, 'nr_calls_completed': 0, 'collision_calls_started': 0,
        'collision_calls_completed': 0, 'native_fk_rows_started': 0, 'native_fk_rows_completed': 0,
        'planned_nr_inputs': 24, 'new_ik_sampling_planning_calls': 0,
        'old_six_nr_rejections_reexecuted': 0, 'old_three_FAIL_gates_changed': False,
        'full_physical_geometry_or_CCD_qualified': False, 'random_seed': None,
        'seed_policy': 'No RNG; deterministic frozen24 axis inputs.'}
    records, center_checks, nr_returns = [], [], []
    try:
        save_new(folder/'old_six_rejections_readonly.json', old_negative_records())
        with (folder/'events.jsonl').open('x', buffering=1) as events:
            def event(kind, **payload):
                events.write(json.dumps({'event': kind, **payload}, ensure_ascii=False, allow_nan=False)+'\n')
            for center in spec['centers']:
                budget.remaining()
                q = center['q_rad']
                metrics = closure_metrics(q, 'IV')
                native = native_crosscheck(q, 'center_'+center['endpoint'], folder, budget, execution)
                qualified = (limit_score(q, 'IV')['legal'] and native['closed']
                             and metrics['position_max_abs'] <= 1e-5
                             and metrics['rotation_matrix_max_abs'] <= 1e-5)
                check = {'center': center, 'math_recheck': metrics, 'native': native,
                         'saved_collision_reused_no_new_call': True, 'passed': qualified}
                center_checks.append(check); event('center_witness_rechecked', **check)
                if not qualified:
                    raise ValueError('CENTER_MATH_PRECONDITION_FAILED')
            for center in spec['centers']:
                for coordinate in range(6):
                    for sign in (1, -1):
                        budget.remaining()
                        q = list(center['q_rad']); q[coordinate] += sign*center['h_rad']
                        tag = center['endpoint']+'_q'+str(coordinate+1)+('_plus' if sign > 0 else '_minus')
                        if not limit_score(q, 'IV')['legal']:
                            raise ValueError('FROZEN_INPUT_NOT_SOURCE_BOUND_LEGAL')
                        record = {'case_id': tag, 'center_endpoint': center['endpoint'],
                            'input_q_rad': q, 'coordinate0': coordinate, 'sign': sign,
                            'h_rad_frozen': center['h_rad'], 'classification': spec['classification']}
                        event('nr_started', **record)
                        execution['nr_calls_started'] += 1
                        if execution['nr_calls_started'] > 24:
                            raise ValueError('NR_COUNT_CAP')
                        result = project_nr(q, 'IV', wall_limit_s=budget.remaining(),
                            max_iterations=10000, position_gate=1e-5, rotation_gate=1e-5,
                            svd_relative=1e-12)
                        execution['nr_calls_completed'] += 1
                        nr_returns.append({'case_id': tag, 'status': result['status']})
                        record['nr'] = result
                        # Write the full original NR result before additional qualification.
                        save_new(folder/(tag+'_nr.json'), record)
                        event('nr_returned', **record)
                        budget.remaining()
                        candidate = result['candidate_q_rad']
                        if candidate is None or not all(math.isfinite(x) for x in candidate):
                            raise RuntimeError('NONFINITE_NR_CANDIDATE')
                        record['native'] = native_crosscheck(candidate, tag, folder, budget, execution)
                        record['independent_closure'] = closure_metrics(candidate, 'IV')
                        record['limits'] = limit_score(candidate, 'IV')
                        record['output_minus_input_rad'] = [b-a for a, b in zip(q, candidate)]
                        record['output_minus_center_rad'] = [b-a for a, b in zip(center['q_rad'], candidate)]
                        identity = branch_identity(candidate[6:], 'IV', GATES['branch_epsilon_diagnostic_only'])
                        record['passive_branch_diagnostic'] = identity
                        record['same_unique_passive_branch_as_center_diagnostic'] = (
                            identity['unique'] and identity['branch_set'] == [center['center_passive_branch']])
                        save_new(folder/(tag+'_pre_collision.json'), record)
                        event('candidate_pre_collision', **record)
                        closed = (record['native']['closed']
                            and record['independent_closure']['position_max_abs'] <= 1e-5
                            and record['independent_closure']['rotation_matrix_max_abs'] <= 1e-5)
                        if result['status'] == 'CONVERGED' and not (closed and record['limits']['legal']):
                            event('nr_unsound_candidate', **record)
                            raise RuntimeError('NR_CONVERGED_BUT_UNSOUND')
                        record['collision'] = None
                        if result['status'] == 'CONVERGED' and closed and record['limits']['legal']:
                            execution['collision_calls_started'] += 1
                            if execution['collision_calls_started'] > 24:
                                raise ValueError('COLLISION_COUNT_CAP')
                            event('collision_started', case_id=tag, candidate_q_rad=candidate)
                            record['collision'] = check_collision('IV', candidate,
                                timeout_s=min(15., budget.remaining()), manifest_path=spec['collision_manifest'])
                            execution['collision_calls_completed'] += 1
                            event('collision_returned', case_id=tag, collision=record['collision'])
                            budget.remaining()
                            if record['collision'].get('status') != 'CHECKED' or not isinstance(record['collision'].get('collision'), bool):
                                save_new(folder/(tag+'_qualification.json'), record)
                                raise RuntimeError('COLLISION_QUALIFICATION_UNKNOWN')
                        record['passed'] = bool(result['status'] == 'CONVERGED' and closed
                            and record['limits']['legal'] and record['collision'] is not None
                            and record['collision']['status'] == 'CHECKED' and record['collision']['collision'] is False)
                        records.append(record)
                        save_new(folder/(tag+'_qualification.json'), record)
                        event('case_finished', **record)
                        if result['status'] not in ('CONVERGED', 'CLOSED_BUT_JOINT_LIMIT_REJECTED', 'ITERATION_LIMIT', 'WALL_LIMIT'):
                            raise RuntimeError('UNEXPECTED_NR_STATUS_'+result['status'])
            execution['status'] = 'FINITE_LOCAL_PROPERTY_PASS' if all(r['passed'] for r in records) else 'FINITE_LOCAL_PROPERTY_FAIL'
    except BaseException as error:
        execution['status'] = 'STOPPED_PREFIX_RETAINED'; execution['error'] = repr(error)
    finally:
        close_sessions()
        execution.update(wall_s=time.monotonic()-budget.start, cpu_s=cpu_seconds()-budget.cpu_start,
            center_witnesses=center_checks, completed_cases=len(records),
            passed_cases=sum(r['passed'] for r in records),
            failed_cases=sum(not r['passed'] for r in records),
            not_executed_cases=24-execution['nr_calls_started'],
            unqualified_or_unfinished_cases=24-len(records),
            nr_status_counts=dict(Counter(r['status'] for r in nr_returns)),
            nr_return_summary=nr_returns,
            previous_r2_wall_s=spec['previous_r2_wall_s'], previous_r2_cpu_s=spec['previous_r2_cpu_s'],
            bound_files_unchanged=all(digest(resolve(p)) == h for p, h in spec['bound_files_sha256'].items()),
            conclusion_scope=spec['conclusion_scope'])
        execution['cumulative_r2_wall_s'] = spec['previous_r2_wall_s']+execution['wall_s']
        execution['cumulative_r2_cpu_s'] = spec['previous_r2_cpu_s']+execution['cpu_s']
        execution['passed'] = (execution['status'] == 'FINITE_LOCAL_PROPERTY_PASS'
            and len(records) == 24 and execution['bound_files_unchanged']
            and execution['wall_s'] <= 60 and execution['cpu_s'] <= 120)
        if not execution['passed'] and execution['status'] == 'FINITE_LOCAL_PROPERTY_PASS':
            execution['status'] = 'FAIL_ACCOUNTING_OR_SOURCE_INTEGRITY'
        save_new(folder/'execution.json', execution)
    print(json.dumps(execution, ensure_ascii=False, allow_nan=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe-protocol', action='store_true', help='Read saved evidence; no FK/NR/collision.')
    parser.add_argument('--validate-draft', action='store_true', help='Check hashes/saved arrays only; no scientific call.')
    parser.add_argument('--protocol', type=Path)
    args = parser.parse_args()
    if args.describe_protocol:
        print(json.dumps(draft_protocol(), ensure_ascii=False, indent=2, allow_nan=False)); return
    if args.protocol is None:
        parser.error('--protocol is required')
    spec = json.loads(args.protocol.read_text())
    if args.validate_draft:
        validate(spec, frozen=False)
        print(json.dumps({'status': 'DRAFT_VALIDATED_READONLY', 'frozen': spec['frozen'],
                          'new_fk_ik_nr_collision_sampling_planning_calls': 0})); return
    execute(spec, args.protocol)


if __name__ == '__main__':
    main()
