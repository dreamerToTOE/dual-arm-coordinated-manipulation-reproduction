"""Read-only arithmetic review of saved R2 spatial evidence; no model/solver calls.

This script deliberately imports no reproduction module, NumPy, random generator,
subprocess, planner or kinematic solver.  Its only output is a new JSON report.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime as dt
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENVS = ('II', 'III', 'IV', 'V', 'VI')
R1 = {
    'II': '20261014T1528_R1_ABB01/II_native.json',
    'III': '20261014T1528_R1_ABB01/III_native.json',
    'IV': '20261014T1545_R1_COMAU02/IV_native.jsonl',
    'V': '20261014T1545_R1_COMAU02/V_native.jsonl',
    'VI': '20261014T1550_R1_VI03/VI_native.jsonl',
}
PI_SOURCE = 3.1416
POSITION_GATE_MM = 1e-5
ROTATION_MATRIX_GATE = 1e-5


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def matrix_errors(actual, target):
    return {
        'position_abs_max_mm': max(abs(actual[i][3]-target[i][3]) for i in range(3)),
        'rotation_matrix_abs_max': max(abs(actual[i][j]-target[i][j])
                                       for i in range(3) for j in range(3)),
    }


def physical_ok(errors):
    return (errors['position_abs_max_mm'] <= POSITION_GATE_MM
            and errors['rotation_matrix_abs_max'] <= ROTATION_MATRIX_GATE)


def limits(env):
    # Independent literal transcription of the pinned source's physical bounds.
    deg = ([[-165, 165], [-110, 110], [-110, 70], [-160, 160],
            [-120, 120], [-400, 400]] if env in ('II', 'III') else
           [[-180, 180], [-60, 125], [-90, 75], [-2700, 2700],
            [-120, 120], [-400, 400]])
    return [[a*PI_SOURCE/180, b*PI_SOURCE/180] for a, b in deg] * (3 if env == 'VI' else 2)


def violations(q, env):
    assert len(q) == len(limits(env)) and all(math.isfinite(v) for v in q)
    return [{'arm': k//6+1, 'joint': k % 6+1, 'value_rad': v,
             'lower_rad': lo, 'upper_rad': hi,
             'outside_by_rad': lo-v if v < lo else v-hi}
            for k, (v, (lo, hi)) in enumerate(zip(q, limits(env)))
            if not lo <= v <= hi]


def source_records(path):
    if path.suffix == '.json':
        records = read(path)['rows']
        return {
            'fk': {(r['index'], r['robot']): (r['q'], r['T'])
                   for r in records if r['kind'] == 'fk'},
            'ik': {(r['index'], r['robot'], r['branch']): (r['q'], r['target'])
                   for r in records if r['kind'] == 'ik'},
            'nr': {str(r['index']): r['input'] for r in records if r['kind'] == 'nr'},
            'ep': {str(r['index']): r['q'] for r in records if r['kind'] == 'raw_endpoint'},
        }
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return {
        'fk': {(r['sample'], i+1): (r['q_rad'][6*i:6*i+6], t)
               for r in records if r['type'] == 'fk_sample'
               for i, t in enumerate(r['author_fk'])},
        'ik': {(r['sample'], r['arm'], r['branch']): (r['source_q_rad'], r['target'])
               for r in records if r['type'] == 'ik_roundtrip'},
        'nr': {str(r['sample']): r['input_q_rad']
               for r in records if r['type'] == 'nr_near_endpoint'},
        'ep': {r['name']: r['q_rad'] for r in records if r['type'] == 'raw_endpoint'},
    }


def review(root, run_dir):
    execution = read(run_dir/'execution.json')
    paths = [p for p in run_dir.rglob('*') if p.is_file()]
    paths += [root/'results/p4_full'/R1[e] for e in ENVS]
    paths += [root/'configs/p4_full/r2_geometry_consistent_qualification_v1.json']
    before = {str(p.relative_to(root)): sha(p) for p in sorted(paths)}
    result = {
        'schema': 'P4_D079_R2_SPATIAL_SAVED_EVIDENCE_INDEPENDENT_REVIEW_V1',
        'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'scope': 'Saved-data arithmetic only; no FK/IK/NR, RNG, collision or planner execution',
        'run': str(run_dir.relative_to(root)),
        'source_commit': execution['source_commit'],
        'protocol_sha256': execution['protocol_sha256'],
        'execution_wall_s': execution['wall_s'], 'execution_cpu_s': execution['cpu_s'],
        'formal_planning_calls': execution['formal_planning_calls'],
        'limits_pi_literal': PI_SOURCE,
        'gates': {'position_max_abs_mm': POSITION_GATE_MM,
                  'rotation_matrix_max_abs': ROTATION_MATRIX_GATE},
        'environments': {},
    }
    total = Counter()
    for env in ENVS:
        folder = run_dir/env
        checks, rows, summary = read(folder/'checks.json'), read(folder/'observations.json'), read(folder/'summary.json')
        rawpath = root/'results/p4_full'/R1[env]
        raw = source_records(rawpath)
        assert sha(rawpath) == summary['original_input_sha256']
        count = Counter('passed' if r['passed'] else 'failed' for r in checks)
        assert len(checks) == summary['checks']
        assert count['passed'] == summary['passed'] and count['failed'] == summary['failed']
        total.update({'checks': len(checks), **count})
        kinds = Counter(r['kind'] for r in rows)
        out = {'checks': len(checks), **count,
               'failed_checks': [r for r in checks if not r['passed']],
               'record_counts': dict(kinds), 'r1_input_sha256_matches': True}

        fk = [r for r in rows if r['kind'] == 'fk_replay']
        errors = []
        for r in fk:
            assert raw['fk'][(r['index'], r['arm'])] == (r['q'], r['original_T'])
            e = matrix_errors(r['continuous_native_T'], r['independent_T'])
            assert e['position_abs_max_mm'] == r['errors']['position_abs_max']
            assert e['rotation_matrix_abs_max'] == r['errors']['rotation_matrix_abs_max']
            errors.append(e)
        out['fk'] = {'source_input_count': 100, 'arm_transform_count': len(fk),
                     'max_native_independent_position_error_mm': max(e['position_abs_max_mm'] for e in errors),
                     'max_native_independent_rotation_matrix_error': max(e['rotation_matrix_abs_max'] for e in errors)}

        out['ik'] = {}
        for target_kind in ('original_saved_target', 'physical_continuous_target'):
            rr = [r for r in rows if r['kind'] == 'ik_replay' and r['target_kind'] == target_kind]
            accepted, qualified, groups = 0, 0, defaultdict(int)
            max_errors = {'position_abs_max_mm': 0., 'rotation_matrix_abs_max': 0.}
            for r in rr:
                q_source, t_source = raw['ik'][(r['index'], r['arm'], r['branch'])]
                assert q_source == r['source_q']
                if target_kind == 'original_saved_target': assert t_source == r['target']
                key = (r['index'], r['arm'])
                groups[key] += 0
                if r['native']['success']:
                    accepted += 1
                    b = limits(env)[6*(r['arm']-1):6*r['arm']]
                    assert all(lo <= v <= hi for v, (lo, hi) in zip(r['native']['solution'], b))
                    e = matrix_errors(r['native']['T'], r['target'])
                    good = physical_ok(e)
                    # Expanded native FK also verifies saved elementary-oracle qualification.
                    assert good == r['physical_roundtrip_qualified']
                    qualified += good
                    groups[key] += good
                    for k in max_errors: max_errors[k] = max(max_errors[k], e[k])
            out['ik'][target_kind] = {
                'branch_attempts': len(rr), 'accepted': accepted,
                'native_fk_qualified': qualified, 'rejected': len(rr)-accepted,
                'target_count': len(groups), 'targets_with_qualified_branch': sum(v > 0 for v in groups.values()),
                'qualified_branches_per_target': [
                    {'source_index': i, 'arm': arm, 'qualified_branches': n}
                    for (i, arm), n in sorted(groups.items())],
                'max_accepted_roundtrip_errors': max_errors,
                'gated_in_runner': target_kind == 'physical_continuous_target',
            }

        wrist = [r for r in rows if r['kind'] == 'fixed_wrist_ik']
        out['fixed_wrist'] = {'branch_attempts': len(wrist),
                              'accepted': sum(r['native']['success'] for r in wrist),
                              'target_count': len({(r['arm'], r['fixture']) for r in wrist})}

        rank = [r for r in rows if r['kind'] == 'rank_fixture']
        rank_groups = defaultdict(list)
        for r in rank:
            computed = [sum(s > sv[0]*1e-6 for s in sv) for sv in r['singular_values']]
            assert computed == r['ranks'] and computed[0] == computed[1]
            rank_groups[r['name']].append({'arm': r['arm'], 'ranks': computed})
        out['rank'] = {'rows': len(rank), 'reduced_from_saved_singular_values': True,
                       'by_fixture': dict(rank_groups)}

        out['raw_endpoints'] = []
        for r in rows:
            if r['kind'] != 'raw_endpoint_unchanged': continue
            assert r['q'] == raw['ep'][r['endpoint']]
            assert r['formal_endpoint_repaired'] is False
            m = r['metrics']
            out['raw_endpoints'].append({'endpoint': r['endpoint'], 'source_q_exactly_preserved': True,
                                        **m, 'position_gate_ratio': m['translation_max_abs']/POSITION_GATE_MM,
                                        'physical_closure_qualified': m['translation_max_abs'] <= POSITION_GATE_MM
                                        and m['rotation_matrix_max_abs'] <= ROTATION_MATRIX_GATE})
        out['additional_fixtures'] = []
        for r in rows:
            if r['kind'] != 'additional_component_fixture_only': continue
            assert r['original_q'] == raw['ep'][r['endpoint']]
            assert r['formal_endpoint_replaced'] is False
            delta = [v-w for v, w in zip(r['q'], r['original_q'])]
            assert delta == r['delta_q']
            out['additional_fixtures'].append({'endpoint': r['endpoint'], 'formal_endpoint_replaced': False,
                                               'max_abs_joint_change_rad': max(abs(v) for v in delta),
                                               'source_limits_legal': not violations(r['q'], env)})

        by_set = defaultdict(Counter)
        rejected = []
        rr = [r for r in rows if r['kind'] == 'nr_reference']
        native = {(r['fixture_kind'], r['fixture']): r for r in rows if r['kind'] == 'nr_native_fk_crosscheck'}
        for r in rr:
            s = r['result']; key = (r['fixture_kind'], r['fixture'])
            if r['fixture_kind'] == 'original_input':
                assert s['input_q_rad'] == raw['nr'][r['fixture']]
            v = violations(s['candidate_q_rad'], env)
            x = native[key]
            physical = all(e['position_abs_max'] <= POSITION_GATE_MM
                           and e['rotation_matrix_abs_max'] <= ROTATION_MATRIX_GATE
                           for e in x['independent_native_errors'])
            assert x['source_limits_legal'] == (not v)
            assert x['status'] == s['status']
            if s['status'] == 'CONVERGED': assert physical and not v
            if s['status'] == 'CLOSED_BUT_JOINT_LIMIT_REJECTED': assert physical and v
            by_set[r['fixture_kind']][s['status']] += 1
            if s['status'] != 'CONVERGED':
                rejected.append({'fixture_kind': key[0], 'fixture': key[1], 'status': s['status'],
                                 'native_fk_physical_closure_qualified': physical,
                                 'native_fk_errors': x['independent_native_errors'],
                                 'reference_metrics': s['metrics'], 'limit_violations': v})
        out['nr'] = {'calls': len(rr), 'status_counts': dict(Counter(r['result']['status'] for r in rr)),
                     'by_fixture_set': {k: dict(v) for k, v in by_set.items()},
                     'nonconverged': rejected,
                     'all_converged_physically_closed_and_source_legal': True,
                     'soundness_is_implication_not_completion': True}
        assert out['nr']['status_counts'] == summary['nr_status_counts']

        jacobians = []
        for r in rows:
            if r['kind'] != 'physical_jacobian': continue
            a, b = r['analytic'], r['finite_difference']
            assert len(a) == (12 if env == 'VI' else 6)
            assert all(len(v) == (18 if env == 'VI' else 12) for v in a)
            pe = max(abs(a[i][j]-b[i][j]) for i in range(len(a)) if i % 6 < 3 for j in range(len(a[0])))
            re = max(abs(a[i][j]-b[i][j]) for i in range(len(a)) if i % 6 >= 3 for j in range(len(a[0])))
            jacobians.append({'endpoint': r['endpoint'], 'shape': [len(a), len(a[0])],
                              'translation_max_abs_mm_per_rad': pe, 'angular_max_abs': re})
        out['physical_jacobian'] = jacobians
        assert summary['formal_planning_calls'] == 0 and summary['collision_checked'] is False
        result['environments'][env] = out
    result['totals'] = dict(total)
    result['totals'].update({
        'source_fk_inputs': 500, 'fk_arm_transforms': sum(v['fk']['arm_transform_count'] for v in result['environments'].values()),
        'nr_calls': sum(v['nr']['calls'] for v in result['environments'].values()),
        'nr_converged': sum(v['nr']['status_counts'].get('CONVERGED', 0) for v in result['environments'].values()),
        'nr_closed_but_limit_rejected': sum(v['nr']['status_counts'].get('CLOSED_BUT_JOINT_LIMIT_REJECTED', 0) for v in result['environments'].values()),
        'raw_endpoints': 10,
        'raw_endpoints_physically_closed': sum(r['physical_closure_qualified'] for v in result['environments'].values() for r in v['raw_endpoints']),
        'rank_fixtures': sum(v['rank']['rows'] for v in result['environments'].values()),
    })
    result['input_sha256'] = before
    result['all_input_bytes_unchanged_by_review'] = all(sha(root/p) == h for p, h in before.items())
    assert result['all_input_bytes_unchanged_by_review']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', default='results/p4_full/20261015_R2_SPATIAL01')
    parser.add_argument('--out', default='reports/P4_FULL_R2_SPATIAL_INDEPENDENT_REVIEW.json')
    args = parser.parse_args()
    value = review(ROOT, ROOT/args.run)
    with (ROOT/args.out).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps({'output': args.out, 'totals': value['totals'],
                      'input_bytes_unchanged': value['all_input_bytes_unchanged_by_review']}, ensure_ascii=False))
