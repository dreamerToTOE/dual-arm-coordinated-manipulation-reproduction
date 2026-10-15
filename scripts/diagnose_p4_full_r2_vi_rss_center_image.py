#!/usr/bin/env python3
"""Two fixed arm1 center FK/J diagnostics within the original VI RSS budget.

Not a saved-only reduction: execution explicitly charges two analytic FK/J
calls, wall and CPU. No new configuration, IK, NR, sampling, collision or planner
is evaluated. A committed frozen protocol is mandatory. The output tests a
first-order local lift condition, not global continuity or paper correctness.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_p4_full_r2_vi_rss_reconstructed as base

ROOT, np = base.ROOT, base.np
SCHEMA = 'P4_R2_VI_RSS_CENTER_IMAGE_DIAGNOSTIC_V1'
B = ROOT/'results/p4_full/20261015_R2_VI_RSS_RECONSTRUCTED01'
Q = ROOT/'results/p4_full/20261015_R2_VI_RSS_BRIDGE01'
ID = base.BUDGET_ID+'.CENTER_IMAGE_V1'
REPORT = ROOT/'reports/P4_FULL_R2_VI_RSS_BRIDGE_ROOT_CAUSE_20261015.json'


def saved_fixtures():
    fixtures = {}
    for line in (B/'events.jsonl').read_bytes().splitlines():
        row = json.loads(line); number = row.get('construction')
        if number not in (219, 643): continue
        if row['event'] == 'designated_singular_fk_and_rank':
            fixtures.setdefault(number, {})['designated_saved'] = row
        if row['event'] == 'construction_finished':
            fixtures.setdefault(number, {}).update(center=row,
                parent_event_line_sha256=hashlib.sha256(line).hexdigest())
    q2 = json.loads((Q/'execution.json').read_text())
    for row in q2['fixture_results']:
        fixtures[row['parent_construction']]['halves'] = row['half_results']
    return [(number, fixtures[number]) for number in (219, 643)]


def draft_protocol():
    q2 = json.loads((Q/'execution.json').read_text())
    deps = q2['source_hashes']
    ledger = sorted((ROOT/'results/p4_full').glob('20261015_R2_*/execution.json'))
    paths = [B/'execution.json', B/'events.jsonl', Q/'execution.json', Q/'events.jsonl',
             ROOT/'results/p4_full'/(base.BUDGET_ID+'.claim.json'),
             ROOT/'results/p4_full'/(base.BUDGET_ID+'.Q2_BRIDGE_V1.claim.json'), REPORT]
    return {'schema': SCHEMA, 'frozen': False, 'run_id': '20261015_R2_VI_RSS_CENTER_IMAGE01',
        'authorization_budget_id': base.BUDGET_ID, 'diagnostic_id': ID,
        'authorization_scope': 'Within the user existing B qualification authorization960/180wall/360CPU; root agent freezes exactly2 fixed mathematical diagnostics. No new authorization or additional candidate budget.',
        'classification': 'RECONSTRUCTED / FIXED-CENTER-FIRST-ORDER-DIAGNOSTIC',
        'runner_source_sha256': base.sha(__file__), 'dependency_source_sha256': deps,
        'input_sha256': {str(p.relative_to(ROOT)): base.sha(p) for p in paths},
        'prior_executions': {str(p.relative_to(ROOT)): base.sha(p) for p in ledger},
        'parent_B_and_Q2_consumed': {'candidate_constructions': 904,
                                   'wall_s': 53.12068026400084, 'cpu_s': 11.951543},
        'parent_remaining_before_diagnostic': q2['authorization_budget_remaining'],
        'fixed_fixture_order': [219, 643], 'active_arm': 1,
        'fixed_inputs': [{'parent_construction': n, 'q18_rad': f['center']['q_rad'],
                          'designated_arm': f['center']['designated_passive_arm'],
                          'parent_event_line_sha256': f['parent_event_line_sha256']}
                         for n, f in saved_fixtures()],
        'budget': {'wall_s': 5., 'cpu_s': 10., 'r2_total_wall_s': 3600., 'r2_total_cpu_s': 7200.},
        'max_active_FK_J_calls': 2, 'candidate_constructions': 0,
        'IK_NR_sampling_collision_planning_calls': 0,
        'method': 'One existing independent analytic arm_fk_jac(center[:6],VI,1) per fixed center. Validate its pose against the original saved native arm1 IK round-trip T. Use literal original grasps and lever offset to compute both target Jacobian blocks. Multiply each fixed center-to-nonzero-endpoint active chord; project onto the exact saved designated-center rank5 image. No finite differences or FK of other arms.',
        'target_velocity': 'world target linear J=J1_linear-skew(R1*grasp_translation)*J1_angular; world target angular J=J1_angular; lambda0=center/lambda1=fixed nonzero side endpoint.',
        'wrist_fiber_diagnostic': 'At q5=0, q4+theta/q6-theta preserves pose analytically for original X-Y-X wrist. Basis=[J1,J2,J3,J4,J5,cross_axis4(J5)] from saved designated center J. Solve target tangent for c/d on last two columns; choose theta=atan2(sign*d,sign*c), sign=-1 for negative q5 branch1 and +1 for positive branch3. No fiber configuration is constructed or checked.',
        'numerical_diagnostic_gates': {'rank_relative': 1e-6, 'position_mm_to_m': .001,
            'image_residual_report_zero_absolute': 1e-10,
            'native_fk_position_maxabs_mm': 1e-7, 'native_fk_rotation_matrix_maxabs': 1e-10},
        'limitations': ['Exact-center means evaluated at that fixed state, not arbitrary precision or new native-J measurement.',
            'Nonzero image residual tests a finite differentiable local lift condition; it is not a global continuity impossibility proof.',
            'Fiber endpoint/connector remains hypothetical and unconstructed; no original Q2 UNKNOWN is upgraded.',
            'No original-author runnable VI RSS equivalence, continuous collision certificate or planning success.'],
        'one_shot_policy': 'Separate atomic retained diagnostic claim; do not alter original/B/Q2 claims or inputs. No repeat after failure. Sum each execution actual wall_s/cpu_s once, never cumulative totals.'}


def validate(spec, path, execute=False):
    expected = draft_protocol()
    for key, value in expected.items():
        if key == 'frozen': continue
        if spec.get(key) != value: raise base.StopQualification('DIAGNOSTIC_PROTOCOL_OR_INPUT_MISMATCH_'+key)
    if set(spec) != set(expected): raise base.StopQualification('DIAGNOSTIC_PROTOCOL_FIELDS_MISMATCH')
    if execute and spec.get('frozen') is not True: raise base.StopQualification('PROTOCOL_NOT_FROZEN')
    if type(spec.get('frozen')) is not bool: raise base.StopQualification('FROZEN_NOT_BOOLEAN')
    for relative, digest in spec['dependency_source_sha256'].items():
        if base.sha(ROOT/relative) != digest: raise base.StopQualification('PARENT_DEPENDENCY_CHANGED_'+relative)
    sources = [Path(__file__).resolve(), path, *[ROOT/p for p in spec['dependency_source_sha256']]]
    if execute:
        for source in sources:
            relative = str(source.relative_to(ROOT))
            subprocess.run(['git', 'ls-files', '--error-unmatch', relative], cwd=ROOT, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if subprocess.check_output(['git', 'status', '--porcelain', '--', relative], cwd=ROOT, text=True):
                raise base.StopQualification('SOURCE_OR_PROTOCOL_UNCOMMITTED_'+relative)
    return {str(p.relative_to(ROOT)): base.sha(p) for p in sources}


def skew(a):
    x, y, z = a
    return np.array([[0., -z, y], [z, 0., -x], [-y, x, 0.]])


def scaled(a):
    b = np.array(a, dtype=float); b[:3] *= .001
    return b


def evaluate_fixed_center(number, fixture, evidence, counts):
    center = fixture['center']; q = np.array(center['q_rad']); s = center['designated_passive_arm']
    evidence.budget.remaining()
    if counts['active_FK_J_calls'] >= 2: raise base.StopQualification('MAX_TWO_ACTIVE_FK_J_CALLS')
    counts['active_FK_J_calls'] += 1
    evidence.event('active_center_FK_J_started', parent_construction=number, arm=1, q6_rad=q[:6].tolist())
    pose, active_j = base.arm_fk_jac(q[:6], 'VI', 1)  # Exactly one model call per fixture.
    evidence.budget.remaining()
    native_pose = center['all_roots']['1'][1]['native']['T']
    native_error = base.errors(pose, native_pose)
    evidence.event('active_center_FK_J_completed', parent_construction=number,
                    q6_rad=q[:6].tolist(), pose=pose.tolist(), world_geometric_J=active_j.tolist(),
                    saved_native_pose=native_pose, native_errors=native_error)
    if native_error['position_maxabs_mm'] > 1e-7 or native_error['rotation_matrix_maxabs'] > 1e-10:
        raise base.StopQualification('FIXED_CENTER_ACTIVE_FK_DISAGREES_WITH_SAVED_NATIVE')
    grasp = base.model_geometry('VI')['grasps'][s-2]
    target_j = active_j.copy()
    offset = pose[:3, :3]@grasp[:3, 3]
    target_j[:3] -= skew(offset)@active_j[3:]
    saved = fixture['designated_saved']; js = np.array(saved['world_geometric_jacobian'])
    target_pose = pose@grasp@np.diag([-1., -1., 1., 1.])
    loop_error = base.errors(saved['world_pose'], target_pose)
    if not base.closed(loop_error): raise base.StopQualification('FIXED_CENTER_SAVED_CLOSURE_MISMATCH')
    scaled_js = scaled(js); u, sigma, vh = np.linalg.svd(scaled_js)
    rank = int(np.count_nonzero(sigma > 1e-6*sigma[0]))
    if rank != 5: raise base.StopQualification('SAVED_DESIGNATED_CENTER_RANK_NOT_5')
    axis = js[3:, 3]
    quadrature = np.r_[np.cross(axis, js[:3, 4]), np.cross(axis, js[3:, 4])]
    basis = scaled(np.column_stack((js[:, :3], js[:, 3], js[:, 4], quadrature)))
    bs = np.linalg.svd(basis, compute_uv=False)
    if int(np.count_nonzero(bs > 1e-6*bs[0])) != 6:
        raise base.StopQualification('WIRST_FIBER_SIX_BASIS_NOT_FULL_RANK')
    rows = []
    for half in fixture['halves']:
        evidence.budget.remaining()
        negative = half['half'].startswith('negative'); tree = half['tree']
        endpoint = np.array(tree['endpoint_a_q_rad'] if negative else tree['endpoint_b_q_rad'])
        original = np.array(tree['endpoint_b_q_rad'] if negative else tree['endpoint_a_q_rad'])
        if not np.array_equal(original, q): raise base.StopQualification('Q2_SAVED_ORIGINAL_CENTER_CHANGED')
        chord = endpoint[:6]-q[:6]; tangent = scaled(target_j@chord)
        projection = u[:, :5]@(u[:, :5].T@tangent)
        residual = tangent-projection; coefficients = np.linalg.solve(basis, tangent)
        sign = -1 if negative else 1
        theta = math.atan2(sign*coefficients[5], sign*coefficients[4])
        rate = sign*math.hypot(coefficients[4], coefficients[5])
        row = {'half': half['half'], 'lambda_definition': '0=saved center;1=fixed nonzero side endpoint',
            'fixed_active_chord_q6_rad': chord.tolist(), 'target_world_twist_scaled': tangent.tolist(),
            'image_projection_residual_vector_scaled': residual.tolist(),
            'image_projection_residual_norm_scaled': float(np.linalg.norm(residual)),
            'image_projection_residual_signed_left_null': float(u[:, -1]@tangent),
            'target_twist_norm_scaled': float(np.linalg.norm(tangent)),
            'numerical_outside_rank5_image': float(np.linalg.norm(residual)) > 1e-10,
            'wrist_six_basis_coefficients': coefficients.tolist(),
            'wrist_six_basis_reconstruction_maxabs': float(np.max(np.abs(basis@coefficients-tangent))),
            'hypothetical_regular_branch_fiber_limit_q4_offset_rad': theta,
            'hypothetical_regular_branch_fiber_limit_q6_offset_rad': -theta,
            'hypothetical_regular_branch_fiber_limit_full18_gap_rad': math.sqrt(2)*abs(theta),
            'nonzero_q5_first_derivative_rad_per_lambda': rate,
            'designated_branch': 1 if negative else 3,
            'scope': 'First-order algebra at the fixed center; no fiber configuration or connector constructed, no global non-continuity claim.'}
        evidence.event('center_image_half_diagnostic', parent_construction=number, **row); rows.append(row)
    return {'parent_construction': number, 'designated_passive_arm': s,
            'active_pose': pose.tolist(), 'active_world_geometric_J': active_j.tolist(),
            'target_J': target_j.tolist(), 'grasp_offset_world_mm': offset.tolist(),
            'native_fk_errors': native_error, 'saved_loop_metrics': loop_error,
            'saved_designated_J_rank': rank, 'saved_designated_J_singular_values': sigma.tolist(),
            'saved_right_null_vector': vh[-1].tolist(), 'wrist_basis_singular_values': bs.tolist(),
            'wrist_basis_condition': float(np.linalg.cond(basis)), 'halves': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe-protocol', action='store_true')
    parser.add_argument('--validate-draft', type=Path)
    parser.add_argument('--protocol', type=Path)
    args = parser.parse_args()
    if sum(bool(v) for v in (args.describe_protocol, args.validate_draft, args.protocol)) != 1:
        parser.error('Choose exactly one mode')
    if args.describe_protocol:
        print(json.dumps(draft_protocol(), ensure_ascii=False, indent=2)); return 0
    path = (args.validate_draft or args.protocol).resolve(); spec = json.loads(path.read_text())
    hashes = validate(spec, path, execute=bool(args.protocol))
    if args.validate_draft:
        print(json.dumps({'status': 'STATIC_DRAFT_VALIDATED', 'frozen': spec['frozen'],
                          'new_scientific_calls': 0, 'source_hashes': hashes}, indent=2)); return 0
    prior = [json.loads((ROOT/p).read_text()) for p in spec['prior_executions']]
    prior_wall = sum(r['wall_s'] for r in prior); prior_cpu = sum(r['cpu_s'] for r in prior)
    remaining = spec['parent_remaining_before_diagnostic']
    runtime_spec = {**spec, 'budget': {**spec['budget'],
        'wall_s': min(spec['budget']['wall_s'], remaining['wall_s']),
        'cpu_s': min(spec['budget']['cpu_s'], remaining['cpu_s'])}}
    out = ROOT/'results/p4_full'/spec['run_id']
    if out.exists(): raise base.StopQualification('OUTPUT_EXISTS_NO_OVERWRITE')
    base.new_json(ROOT/'results/p4_full'/(ID+'.claim.json'), {
        'budget_id': base.BUDGET_ID, 'diagnostic_id': ID, 'run_id': spec['run_id'],
        'created_at_utc': base.utc(), 'protocol_sha256': base.sha(path),
        'active_FK_J_call_cap': 2, 'candidate_constructions': 0,
        'caps': runtime_spec['budget'], 'policy': 'Retain after interruption; no reset/repeat.'})
    out.mkdir(parents=True, exist_ok=False)
    budget = base.RunBudget(runtime_spec, prior_wall, prior_cpu)
    evidence = base.Evidence(out, budget); counts = Counter(); results = []
    record = {'schema': SCHEMA, 'run_id': spec['run_id'], 'diagnostic_id': ID,
        'authorization_budget_id': base.BUDGET_ID, 'classification': spec['classification'],
        'started_at_utc': base.utc(), 'protocol_sha256': base.sha(path), 'source_hashes': hashes,
        'input_sha256': spec['input_sha256'], 'prior_execution_hashes': spec['prior_executions'],
        'previous_wall_s': prior_wall, 'previous_cpu_s': prior_cpu,
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'candidate_constructions': 0, 'IK_NR_sampling_collision_planning_calls': 0,
        'original_Q2_unknown_unchanged': True, 'full_RSS_or_planning_pass': False,
        'limitations': spec['limitations']}
    exit_code = 0
    try:
        evidence.event('run_started', protocol=spec, source_hashes=hashes)
        for number, fixture in saved_fixtures():
            result = evaluate_fixed_center(number, fixture, evidence, counts)
            results.append(result); evidence.event('fixed_center_diagnostic_finished', **result)
        record['status'] = 'FIXED_CENTER_FIRST_ORDER_DIAGNOSTIC_RECORDED'
    except BaseException as exc:
        record.update(status='STOP_RETAINED_PREFIX', error=repr(exc)); exit_code = 2
        evidence.event('run_stopped', error=repr(exc))
    finally:
        budget.close(); wall = time.monotonic()-budget.started; used_cpu = budget.cpu()-budget.cpu_start
        record.update(counts=dict(counts), wall_s=wall, cpu_s=used_cpu, ended_at_utc=base.utc(),
            fixed_center_results=results, cumulative_execution_wall_s=prior_wall+wall,
            cumulative_execution_cpu_s=prior_cpu+used_cpu,
            authorization_budget_remaining={'candidate_constructions': remaining['candidate_constructions'],
                'wall_s': max(0., remaining['wall_s']-wall), 'cpu_s': max(0., remaining['cpu_s']-used_cpu),
                'r2_total_wall_s': max(0., 3600-prior_wall-wall),
                'r2_total_cpu_s': max(0., 7200-prior_cpu-used_cpu),
                'policy': 'Fixed mathematical diagnosis consumes VI original wall/CPU but no candidate. No reset or automatic repeat.'})
        base.new_json(out/'execution.json', record); evidence.events.close()
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__': raise SystemExit(main())
