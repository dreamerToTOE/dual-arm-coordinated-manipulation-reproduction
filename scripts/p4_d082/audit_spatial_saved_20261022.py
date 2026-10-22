#!/usr/bin/env python3
"""Read-only arithmetic/hash audit of preserved spatial paths; zero model calls."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cache = {}

    def digest(path):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        key = str(path.resolve())
        if key not in cache:
            h = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    h.update(block)
            cache[key] = h.hexdigest()
        return cache[key]

    def read(path):
        return json.loads((ROOT / path).read_text())

    paths = [
        ('II', 'RRT', 'PCS', 177, 'reports/P4_FULL_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW_20261015.json', 'results/p4_full/20261015_R2_ABB_RRT_PATH01/execution.json'),
        ('II', 'RRT', 'NR', 393, 'reports/P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json', 'results/p4_full/20261015_R2_ABB_RRT_NR_PATH01/execution.json'),
        ('II', 'CBiRRT', 'PCS', 413, 'reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_20261016.json', 'results/p4_full/20261015_R2_ABB_CBIRRT_D_PATH01/execution.json'),
        ('II', 'CBiRRT', 'NR', 689, 'reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_20261017.json', 'results/p4_full/20261016_R2_ABB_CBIRRT_NR_PATH01/execution.json'),
        ('III', 'RRT', 'PCS', 649, 'reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json', 'results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01/execution.json'),
    ]
    recovered = []
    for env, planner, method, nodes, post_path, execution_path in paths:
        post = read(post_path)
        retained = post.get('retained_sha256', {})
        bad = []
        for path, expected in retained.items():
            try:
                if digest(path) != expected:
                    bad.append({'path': path, 'reason': 'HASH_MISMATCH'})
            except FileNotFoundError:
                bad.append({'path': path, 'reason': 'MISSING'})
        execution_ok = digest(execution_path) == post['execution_sha256']
        status_ok = post.get('passed') is True or str(post.get('status', '')).startswith('PASS_')
        recovered.append({
            'environment': env, 'planner': planner, 'method': method, 'nodes': nodes,
            'historical_certificate': post_path, 'certificate_sha256': digest(post_path),
            'historical_status': post.get('status', 'PASS' if post.get('passed') else 'FAIL'),
            'execution': execution_path, 'execution_sha256': digest(execution_path),
            'execution_matches_certificate': execution_ok,
            'retained_hash_entries': len(retained), 'retained_hash_mismatches': bad,
            'certificate_and_recovery_pass': execution_ok and status_ok and not bad,
            'scope': 'RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY',
        })

    run = 'results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01'
    queue_path = f'{run}/complete_original_saved_queue.json'
    source_path = 'results/p4_full/20261018_R2_D080_III_RRT_PCS_SOURCE01/parsed_source_result.json'
    queue, source = read(queue_path), read(source_path)
    mismatches, max_position, max_rotation = [], 0.0, 0.0
    max_native_position, max_native_rotation = 0.0, 0.0
    aligned_pass = native_pass = 0
    for index, q in enumerate(queue['nodes']):
        n, m, c = [read(f'{run}/node_{index:05d}{suffix}.json') for suffix in ('', '_math', '_collision_response')]
        if n.get('q12') != q or m.get('q12') != q or n.get('collision') != c:
            mismatches.append(index)
        max_position = max(max_position, m['closure']['position_max_abs'])
        max_rotation = max(max_rotation, m['closure']['rotation_matrix_max_abs'])
        aligned_pass += int(c['variants']['aligned']['pose_consistency']['passed'])
        native_pass += int(c['variants']['native']['pose_consistency']['passed'])
        for error in c['variants']['native']['pose_consistency']['errors']:
            max_native_position = max(max_native_position, error['translation_maxabs_mm'])
            max_native_rotation = max(max_native_rotation, error['rotation_maxabs'])
    roles = [edge['active_chain'] for edge in queue['edges']]
    maximum_leaf = max(math.dist(a, b) for a, b in zip(queue['nodes'], queue['nodes'][1:]))
    iii = {
        'queue': queue_path, 'queue_sha256': digest(queue_path),
        'source': source_path, 'source_sha256': digest(source_path),
        'source_exact': source['exact'], 'source_approximate': source['approximate'],
        'source_seed': source['seed'], 'source_solve_wall_s': source['solve_wall_s'],
        'source_validity_callback': source['state_validity_callback'],
        'nodes': len(queue['nodes']), 'leaves': len(queue['nodes']) - 1,
        'source_milestones': queue['source_milestone_count'],
        'source_attempts_including_failures': queue['source_attempt_count'],
        'endpoint_identity': queue['nodes'][0] == source['start_q12'] and queue['nodes'][-1] == source['goal_q12'],
        'q12_node_math_and_collision_binding_mismatches': mismatches,
        'maximum_adjacent_l2_rad': maximum_leaf,
        'maximum_saved_position_residual_mm': max_position,
        'maximum_saved_rotation_matrix_residual': max_rotation,
        'final_path_active_roles': roles,
        'final_path_active_role_switches': sum(a != b for a, b in zip(roles, roles[1:])),
        'aligned_pose_pass_nodes': aligned_pass, 'native_pose_pass_nodes': native_pass,
        'maximum_native_tcp_position_mismatch_mm': max_native_position,
        'maximum_native_tcp_rotation_matrix_mismatch': max_native_rotation,
        'continuous_collision_certificate': False,
        'minimum_clearance_available': False,
    }
    result = {
        'schema': 'P4_D082_SPATIAL_SAVED_RECOVERY_20261022_V1',
        'status': 'PASS_SAVED_SPATIAL_EVIDENCE_RECOVERY' if all(p['certificate_and_recovery_pass'] for p in recovered) and not mismatches and iii['endpoint_identity'] else 'FAIL_SAVED_SPATIAL_EVIDENCE_RECOVERY',
        'new_scientific_model_or_planner_calls': 0,
        'independent_arithmetic_and_hash_audit_only': True,
        'qualified_II_complete_discrete_paths_reused': 4,
        'qualified_III_complete_aligned_discrete_paths_reused': 1,
        'paths': recovered, 'III_saved_binding_and_arithmetic': iii,
        'limitations': ['No new FK/IK/Jacobian/NR/RBS/collision/source execution.', 'Historical certificates remain immutable; this does not upgrade native TCP equivalence or strict continuous collision safety.', 'D082 audit scripts only read prior qualification flags; the additional q12-to-record binding check closes that recovery omission without invalidating the original spatial evidence.'],
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    with output.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'II_paths': 4, 'III_paths': 1, 'III_binding_mismatches': len(mismatches), 'III_role_switches': iii['final_path_active_role_switches'], 'retained_hash_entries_checked': sum(p['retained_hash_entries'] for p in recovered)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
