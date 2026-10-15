#!/usr/bin/env python3
"""One-shot source-policy collision replay of the exact old48 RSS candidates.

Draft modes only read saved evidence. Worker instrumentation counts existing
adapter FK/J calls without modifying their inputs or outputs. No new IK/NR,
candidate construction, RNG, RBS or planner is implemented.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

THREAD_KEYS = ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
               'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')
THREAD_ENV_BEFORE = {k: os.environ.get(k) for k in THREAD_KEYS}
for key in THREAD_KEYS:
    os.environ[key] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/'scripts'))
import qualify_p4_full_r2_vi_rss_reconstructed as common

SCHEMA = 'P4_R2_SAVED_RSS_COLLISION_QUALIFICATION_V1'
RUN_ID = '20261015_R2_SAVED_RSS_COLLISION01'
CLAIM_ID = 'P4_R2_SAVED_RSS_COLLISION_48_30W_60CPU_20261015'
OLD = 'results/p4_full/20261015_R2_RSS_CONSTRUCTION01'
PRE = 'reports/P4_FULL_R2_SAVED_RSS_COLLISION_PRE_TASK_20261015.md'
MANIFEST = '/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
EXPECTED = {'II': 18, 'III': 22, 'V': 8}
RAW = {'II': 'results/p4_full/20261014T1528_R1_ABB01/II_native.json',
       'III': 'results/p4_full/20261014T1528_R1_ABB01/III_native.json',
       'V': 'results/p4_full/20261014T1545_R1_COMAU02/V_native.jsonl'}
SOURCES = [str(Path(__file__).resolve().relative_to(ROOT)),
    'scripts/qualify_p4_full_r2_vi_rss_reconstructed.py',
    'baselines/p4_full/geometry_consistent/collision_adapter.py',
    'baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/abb_independent_oracle.py',
    'baselines/p4_full/analyze_comau_native_qualification.py',
    'baselines/p4_full/geometry_consistent/qualify_rss_construction.py',
    'baselines/p4_full/geometry_consistent/run_qualification.py',
    'baselines/p4_full/geometry_consistent/rss_geometry.py',
    'baselines/p4_full/geometry_consistent/spatial_ik_patch.py',
    'baselines/p4_full/geometry_consistent/spatial_batch_driver.cpp', PRE]


def path(value):
    p = Path(value)
    return p if p.is_absolute() else ROOT/p


def load(value):
    return json.loads(path(value).read_text())


def record_sha(value):
    import hashlib
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def prior_paths():
    return sorted(str(p.relative_to(ROOT)) for p in
        (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json')
        if p.parent.name != RUN_ID)


def saved_candidates():
    """Select only the already-true saved qualification flags; no model call."""
    selected = []
    for env, expected in EXPECTED.items():
        observations_path = OLD+'/'+env+'/observations.json'
        observations = load(observations_path)
        local = []
        for index, original in enumerate(observations):
            if original['qualified_closure_rank_bounds_only'] is not True:
                continue
            q = original['candidate_q_rad']; ik = original['native_active_ik']
            metric = original['physical_metrics']
            if (len(q) != 12 or not all(math.isfinite(v) for v in q)
                    or original['source_joint_limits_legal'] is not True
                    or original['passive_rank'] >= 6 or original['rejection_reasons']
                    or original['collision_checked'] is not False
                    or original['RBS_or_branch_bridge_checked'] is not False
                    or ik['success'] is not True or ik['finite'] is not True
                    or ik['input_line'] != index+1
                    or ik['solution']+original['forced_passive_q_rad'] != q
                    or metric['position_unit'] != 'mm'
                    or metric['translation_max_abs'] > 1e-5
                    or metric['rotation_matrix_max_abs'] > 1e-5):
                raise common.StopQualification('SAVED_MATH_ELIGIBILITY_CHANGED')
            local.append({'case_id': f'{env}_obs{index:04d}', 'environment': env,
                'observations_path': observations_path, 'observation_index0': index,
                'source_index': original['source_index'], 'mode': original['mode'],
                'active_branch': original['branch'], 'original_input_line1': ik['input_line'],
                'q12_rad': q, 'original_record_sha256_canonical_json': record_sha(original),
                'saved_physical_metrics': metric, 'saved_passive_rank': original['passive_rank'],
                'saved_passive_singular_values': original['scaled_passive_singular_values'],
                'saved_original_bounds_legal': True})
        if len(local) != expected:
            raise common.StopQualification('EXPECTED_OLD_CANDIDATE_COUNT_CHANGED_'+env)
        selected.extend(local)
    if len({r['case_id'] for r in selected}) != 48:
        raise common.StopQualification('EXPECTED_48_UNIQUE_CASES')
    return selected


def assets():
    files = SOURCES + [MANIFEST,
        'configs/p4_full/r2_geometry_consistent_qualification_v1.json',
        'configs/p4_full/r2_rss_fixed_construction_addendum_v1.json',
        'results/p4_full/20261015_R2_COLLISION_CONTROLS01/result.json']
    files += [str(p.relative_to(ROOT)) for p in sorted(path(OLD).rglob('*')) if p.is_file()]
    files += list(RAW.values())
    for env in EXPECTED:
        executable = 'abb' if env in ('II', 'III') else 'comau_v'
        files.append('build/p4_full/20261015_R2_SPATIAL01/'+executable+'_batch')
    for entry in load(MANIFEST)['entries']:
        if entry['model'] not in ('abb', 'V'):
            continue
        files.append(entry['binary'])
        for relative in entry['source_files_sha256']:
            files += [str(Path(entry['source_root'])/relative), str(Path(entry['cwd'])/relative)]
        files += [str(Path(entry['cwd'])/'simulator'/name) for name in entry['mesh_sha256']]
        files.append(str(Path(entry['source_root'])/'validity_checkers/StateValidityCheckerRSS.cpp'))
    return list(dict.fromkeys(files))


def draft_protocol():
    prior = prior_paths(); ledgers = [load(p) for p in prior]
    return {'schema': SCHEMA, 'frozen': False, 'run_id': RUN_ID, 'claim_id': CLAIM_ID,
        'classification': 'RECONSTRUCTED / SAVED-DETERMINISTIC-RSS-CANDIDATE / SOURCE-POLICY-COLLISION-REPLAY',
        'authorization_scope': 'Existing D079 R2 qualification total3600wall/7200CPU. No VI B candidate or wall/CPU charge; not formal planning authorization.',
        'candidate_selection': 'II then III then V; exact original observations order; every and only saved qualified_closure_rank_bounds_only=true row. No candidate/root/angle/periodic copy replacement.',
        'fixed_candidates': saved_candidates(), 'expected_environment_counts': EXPECTED,
        'budget': {'max_collision_adapter_calls': 48, 'max_native_variant_queries': 96,
            'max_internal_adapter_arm_FK_J_calls': 192, 'wall_s': 30., 'cpu_s': 60.,
            'r2_total_wall_s': 3600., 'r2_total_cpu_s': 7200.},
        'accounting': 'One adapter native+aligned per candidate, two arms per variant:48 logical calls,96 source queries,192 internal independent arm FK/J if complete. Instrument existing physical_nr.arm_fk_jac boundary for start/completed events only, original function/input/output unchanged. Count source query_codes lengths as actual PQP pair calls. Zero extra mathematical-qualification replay.',
        'collision_manifest': MANIFEST, 'collision_manifest_sha256': common.sha(path(MANIFEST)),
        'gates': {'adapter_status': 'CHECKED', 'selected_variant': 'aligned',
            'required_variants_in_order': ['native', 'aligned'],
            'all_source_query_codes_zero': True, 'selected_TCP_consistency_passed': True,
            'TCP_position_gate_mm': 1e-5, 'TCP_rotation_matrix_gate': 1e-5},
        'source_scope': 'Original meshes/pair list/8mm PQP only. Native and physical-base-aligned results separate. Native TCP mismatch retained; selected aligned must pass. ABB source collinear rod triangles retained. No full-geometry or continuous-collision certificate.',
        'source_EE_and_limits_scope': 'Original bound legality reused from saved math. No original sampler or checkEE executed. V source sampleSingular also requires both TCPz>=10mm; this collision-only replay cannot certify complete source RSS validity. ABB source singular path has no explicit separate bound check. Original control-flow differences recorded in PRE.',
        'ordinary_collision_policy': 'True collision is an ordinary candidate rejection; continue fixed remaining cases. Never replace it. A checked clear only qualifies this saved candidate under selected source policy.',
        'stop_policy': 'Source/protocol/ledger/old case mismatch; invalid adapter/native query/PQP error/selected TCP mismatch; FK instrumentation mismatch; wall/CPU/count cap. Preserve prefix and all unexecuted cases. No retry or automatic second claim.',
        'preserved_failures': 'All old5600 branch observations and old mode0 FAIL gates unchanged. No RBS/fullRSS/planning upgrade.',
        'new_candidate_constructions': 0, 'IK_NR_RNG_RBS_planning_calls': 0,
        'prior_executions': prior,
        'previous_r2_wall_s': math.fsum(float(r['wall_s']) for r in ledgers),
        'previous_r2_cpu_s': math.fsum(float(r['cpu_s']) for r in ledgers),
        'source_files': SOURCES,
        'bound_files_sha256': {p: common.sha(path(p)) for p in assets()+prior}}


def validate(spec, protocol, execute=False):
    expected = draft_protocol()
    if set(spec) != set(expected):
        raise common.StopQualification('PROTOCOL_FIELD_SET_CHANGED')
    for key, value in expected.items():
        if key != 'frozen' and spec[key] != value:
            raise common.StopQualification('PROTOCOL_OR_INPUT_CHANGED_'+key)
    if type(spec['frozen']) is not bool or execute and spec['frozen'] is not True:
        raise common.StopQualification('FROZEN_PROTOCOL_REQUIRED')
    if execute:
        for relative in SOURCES+[str(protocol.relative_to(ROOT))]:
            subprocess.run(['git', 'ls-files', '--error-unmatch', relative], cwd=ROOT,
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if subprocess.check_output(['git', 'status', '--porcelain', '--', relative], cwd=ROOT, text=True):
                raise common.StopQualification('SOURCE_OR_CONFIG_UNCOMMITTED_'+relative)


def worker(protocol):
    """Internal child, permitted only under its live parent one-shot claim."""
    spec = load(protocol); request = json.loads(sys.stdin.read())
    if spec.get('schema') != SCHEMA or spec.get('frozen') is not True:
        raise common.StopQualification('WORKER_FROZEN_PROTOCOL_REQUIRED')
    claim = load('results/p4_full/'+CLAIM_ID+'.claim.json')
    if claim['parent_pid'] != os.getppid() or claim['protocol_sha256'] != common.sha(protocol):
        raise common.StopQualification('WORKER_REQUIRES_LIVE_ONE_SHOT_PARENT')
    for relative in SOURCES:
        if common.sha(path(relative)) != spec['bound_files_sha256'][relative]:
            raise common.StopQualification('WORKER_SOURCE_HASH_CHANGED_'+relative)
    case = next(c for c in spec['fixed_candidates'] if c['case_id'] == request['case_id'])
    if case['q12_rad'] != request['q'] or case['environment'] != request['environment']:
        raise common.StopQualification('WORKER_FIXED_CASE_MISMATCH')
    folder = ROOT/'results/p4_full'/RUN_ID
    common.new_json(folder/(case['case_id']+'.worker.claim.json'),
        {'case_id': case['case_id'], 'parent_pid': os.getppid(), 'started_at_utc': common.utc()})
    from baselines.p4_full.geometry_consistent import physical_nr
    from baselines.p4_full.geometry_consistent.collision_adapter import check_collision, close_sessions
    original = physical_nr.arm_fk_jac
    counters = {'started': 0, 'completed': 0}
    def counted(q, environment, arm):
        if counters['started'] >= 4:
            raise common.StopQualification('WORKER_MAX_FOUR_INTERNAL_ARM_FK_J_CALLS')
        counters['started'] += 1
        print(json.dumps({'event': 'adapter_internal_arm_FK_J_started', 'case_id': case['case_id'],
            'call': counters['started'], 'environment': environment, 'arm': arm,
            'q6_rad': [float(v) for v in q]}), file=sys.stderr, flush=True)
        result = original(q, environment, arm)
        counters['completed'] += 1
        print(json.dumps({'event': 'adapter_internal_arm_FK_J_completed', 'case_id': case['case_id'],
            'call': counters['completed']}), file=sys.stderr, flush=True)
        return result
    physical_nr.arm_fk_jac = counted
    try:
        result = check_collision(case['environment'], case['q12_rad'],
            timeout_s=float(request['timeout_s']), manifest_path=spec['collision_manifest'])
    finally:
        physical_nr.arm_fk_jac = original
        close_sessions()
    print(json.dumps({'case_id': case['case_id'], 'collision_result': result,
        'adapter_internal_arm_FK_J': counters}, ensure_ascii=False, allow_nan=False), flush=True)


def qualify_return(spec, case, answer):
    r = answer['collision_result']; c = answer['adapter_internal_arm_FK_J']
    if (answer['case_id'] != case['case_id'] or r.get('environment') != case['environment']
            or r.get('manifest_sha256') != spec['collision_manifest_sha256']
            or r.get('status') != 'CHECKED' or type(r.get('collision')) is not bool
            or r.get('selected_variant') != 'aligned'
            or list(r.get('variants', {})) != ['native', 'aligned']
            or c != {'started': 4, 'completed': 4}):
        raise common.StopQualification('ADAPTER_OR_FK_ACCOUNTING_NOT_QUALIFIED')
    for variant in ('native', 'aligned'):
        row = r['variants'][variant]; pose = row['pose_consistency']; codes = row.get('query_codes')
        if (row.get('native_result') not in (0, 1) or not isinstance(codes, list) or not codes
                or any(type(v) is not int or v != 0 for v in codes)
                or len(pose.get('errors', [])) != 2):
            raise common.StopQualification('SOURCE_QUERY_OR_POSE_CAPTURE_INVALID_'+variant)
    if r['variants']['aligned']['pose_consistency'].get('passed') is not True:
        raise common.StopQualification('SELECTED_ALIGNED_TCP_MISMATCH')


def execute(spec, protocol):
    folder = ROOT/'results/p4_full'/RUN_ID
    if folder.exists():
        raise common.StopQualification('OUTPUT_EXISTS_NO_OVERWRITE')
    common.new_json(ROOT/'results/p4_full'/(CLAIM_ID+'.claim.json'),
        {'claim_id': CLAIM_ID, 'parent_pid': os.getpid(), 'protocol_sha256': common.sha(protocol),
         'created_at_utc': common.utc(), 'budget': spec['budget'],
         'policy': 'Preserve prefix after interruption. No restart/retry/VI B budget charge.'})
    folder.mkdir(parents=True, exist_ok=False)
    budget = common.RunBudget(spec, spec['previous_r2_wall_s'], spec['previous_r2_cpu_s'])
    evidence = common.Evidence(folder, budget); counters = Counter(); results = []
    record = {'schema': SCHEMA, 'run_id': RUN_ID, 'classification': spec['classification'],
        'started_at_utc': common.utc(), 'source_commit': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'protocol_sha256': common.sha(protocol), 'bound_files_sha256': spec['bound_files_sha256'],
        'previous_wall_s': spec['previous_r2_wall_s'], 'previous_cpu_s': spec['previous_r2_cpu_s'],
        'new_candidate_constructions': 0, 'IK_NR_RNG_RBS_planning_calls': 0,
        'VI_B_budget_charged': False, 'original_failures_unchanged': True,
        'full_RSS_or_planning_pass': False, 'continuous_collision_certificate': False}
    evidence.event('run_started', metadata=record, budget=spec['budget'], thread_env_before=THREAD_ENV_BEFORE)
    error = None
    try:
        for case in spec['fixed_candidates']:
            remaining = budget.remaining()
            if counters['collision_adapter_calls_started'] >= 48:
                raise common.StopQualification('LOGICAL_COLLISION_CALL_CAP')
            counters['collision_adapter_calls_started'] += 1
            counters['adapter_internal_arm_FK_J_requested'] += 4
            counters['native_variant_queries_requested'] += 2
            evidence.event('candidate_collision_started', fixed_case=case,
                internal_arm_FK_J_requested=4, native_variant_queries_requested=2)
            text = evidence.process([sys.executable, str(Path(__file__).resolve()),
                '--collision-worker', str(protocol)], json.dumps({'case_id': case['case_id'],
                'environment': case['environment'], 'q': case['q12_rad'],
                'timeout_s': min(10., remaining)})+'\n', case['case_id'])
            answer = json.loads(text)
            evidence.event('candidate_collision_returned', fixed_case=case, answer=answer)
            common.new_json(folder/(case['case_id']+'.json'), {'fixed_case': case, **answer})
            counters['collision_adapter_calls_completed'] += 1
            fk = answer['adapter_internal_arm_FK_J']
            counters['adapter_internal_arm_FK_J_started'] += fk['started']
            counters['adapter_internal_arm_FK_J_completed'] += fk['completed']
            collision = answer['collision_result']
            counters['native_variant_queries_returned'] += len(collision.get('variants', {}))
            for variant, row in collision.get('variants', {}).items():
                pairs = len(row.get('query_codes', []))
                counters['PQP_pair_queries_'+case['environment']+'_'+variant] += pairs
                counters['PQP_pair_queries_total'] += pairs
            qualify_return(spec, case, answer)
            clear = collision['collision'] is False
            counters['source_policy_clear' if clear else 'source_policy_collision'] += 1
            results.append({'case_id': case['case_id'], 'environment': case['environment'],
                'source_policy_clear': clear, 'collision': collision['collision'],
                'qualified_math_and_selected_source_policy': clear, 'original_source_EE_executed': False})
            evidence.event('candidate_finished', result=results[-1])
            budget.remaining()
        record['status'] = 'SAVED_48_CANDIDATES_SOURCE_POLICY_CHECKED'
    except BaseException as exc:
        error = exc; record.update(status='STOP_PREFIX_RETAINED', termination_reason=repr(exc))
        evidence.event('run_stopped', termination_reason=repr(exc))
    finally:
        budget.close()
        after = {p: common.sha(path(p)) for p in spec['bound_files_sha256']}
        record['bound_files_after_sha256'] = after
        if after != spec['bound_files_sha256']:
            record.update(status='STOP_BOUND_FILE_CHANGED', source_or_old_input_changed=True)
            if error is None: error = common.StopQualification('BOUND_FILE_CHANGED')
        record.update(ended_at_utc=common.utc(), wall_s=time.monotonic()-budget.started,
            cpu_s=budget.cpu()-budget.cpu_start, counts=dict(counters), candidate_results=results,
            uncompleted_case_ids=[c['case_id'] for c in spec['fixed_candidates']
                if c['case_id'] not in {r['case_id'] for r in results}],
            partial_call_accounting='All FK start/completed events and raw process output retained in per-case stderr. Interrupted worker counts not guessed from cap; inspect retained prefix.',
            environment_counts={env: dict(Counter('clear' if r['source_policy_clear'] else 'collision'
                for r in results if r['environment'] == env)) for env in EXPECTED})
        record['cumulative_execution_wall_s'] = spec['previous_r2_wall_s']+record['wall_s']
        record['cumulative_execution_cpu_s'] = spec['previous_r2_cpu_s']+record['cpu_s']
        record['r2_remaining'] = {'wall_s': 3600.-record['cumulative_execution_wall_s'],
            'cpu_s': 7200.-record['cumulative_execution_cpu_s']}
        common.new_json(folder/'execution.json', record)
        evidence.events.close()
    print(json.dumps({'status': record['status'], 'run_id': RUN_ID, 'counts': dict(counters),
        'wall_s': record['wall_s'], 'cpu_s': record['cpu_s']}, ensure_ascii=False))
    if error is not None:
        raise error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe-protocol', action='store_true')
    parser.add_argument('--validate-draft', type=Path)
    parser.add_argument('--protocol', type=Path)
    parser.add_argument('--collision-worker', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if sum(bool(v) for v in vars(args).values()) != 1:
        parser.error('Choose exactly one mode')
    if args.collision_worker:
        worker(args.collision_worker.resolve()); return
    if args.describe_protocol:
        print(json.dumps(draft_protocol(), ensure_ascii=False, indent=2)); return
    protocol = (args.validate_draft or args.protocol).resolve()
    spec = load(protocol); validate(spec, protocol, execute=bool(args.protocol))
    if args.validate_draft:
        print(json.dumps({'status': 'STATIC_DRAFT_VALIDATED', 'frozen': spec['frozen'],
            'candidates': len(spec['fixed_candidates']), 'new_scientific_calls': 0})); return
    execute(spec, protocol)


if __name__ == '__main__':
    main()
