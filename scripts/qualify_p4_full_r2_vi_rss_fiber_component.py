#!/usr/bin/env python3
"""Six fixed singular-fiber component candidates; no regular-branch connector.

This is an independent RECONSTRUCTED component qualification within the
remaining original VI RSS authorization. It never upgrades Q2 or runs a planner.
Draft modes only read saved inputs. Execution requires committed frozen inputs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_p4_full_r2_vi_rss_reconstructed as base
import diagnose_p4_full_r2_vi_rss_center_image as center_diag

ROOT, np = base.ROOT, base.np
SCHEMA = 'P4_R2_VI_RSS_FIBER_COMPONENT_QUALIFICATION_V1'
ID = base.BUDGET_ID+'.FIBER_COMPONENT_V1'
CENTER = ROOT/'results/p4_full/20261015_R2_VI_RSS_CENTER_IMAGE01'
REVIEW = ROOT/'reports/P4_FULL_R2_VI_RSS_CENTER_IMAGE_REVIEW_20261015.md'
H = .0025


def fixed_schedule():
    """Read exact measured theta; do not build new q in draft modes."""
    rows = json.loads((CENTER/'execution.json').read_text())['fixed_center_results']
    schedule = []
    for fixture in rows:
        number = fixture['parent_construction']
        for half in fixture['halves']:
            fractions = [.5, 1.] if number == 219 else [1.]
            schedule.extend({'parent_construction': number,
                'designated_arm': fixture['designated_passive_arm'], 'half': half['half'],
                'theta_rad': half['hypothetical_regular_branch_fiber_limit_q4_offset_rad'],
                'theta_fraction': fraction, 'kind': 'MIDPOINT' if fraction == .5 else 'ENDPOINT'}
                for fraction in fractions)
    if len(schedule) != 6 or [row['parent_construction'] for row in schedule] != [219]*4+[643]*2:
        raise base.StopQualification('FIXED_FIBER_SCHEDULE_MISMATCH')
    return schedule


def draft_protocol():
    diagnostic = json.loads((CENTER/'execution.json').read_text())
    bspec = json.loads((ROOT/'configs/p4_full/r2_vi_rss_reconstructed_qualification_v1.json').read_text())
    inputs = [CENTER/'execution.json', CENTER/'events.jsonl', REVIEW,
        ROOT/'results/p4_full'/(base.BUDGET_ID+'.CENTER_IMAGE_V1.claim.json'),
        ROOT/'results/p4_full/20261015_R2_VI_RSS_RECONSTRUCTED01/events.jsonl',
        ROOT/'results/p4_full/20261015_R2_VI_RSS_RECONSTRUCTED01/execution.json',
        ROOT/'results/p4_full/20261015_R2_VI_RSS_BRIDGE01/execution.json']
    copied = ('collision_checker_command', 'collision_manifest', 'collision_manifest_sha256',
        'collision_controls_result', 'collision_controls_result_sha256',
        'collision_success_statuses', 'collision_qualification_scope')
    return {'schema': SCHEMA, 'frozen': False, 'run_id': '20261015_R2_VI_RSS_FIBER_COMPONENT01',
        'authorization_budget_id': base.BUDGET_ID, 'component_id': ID,
        'classification': 'RECONSTRUCTED / SINGULAR-FIBER-DISCRETE-COMPONENT-ONLY',
        'authorization_scope': 'Versioned component qualification inside the existing user-approved independent VI RSS construction budget; no new allowance or formal planning authorization.',
        'runner_source_sha256': base.sha(__file__),
        'dependency_source_sha256': diagnostic['source_hashes'],
        'input_sha256': {str(p.relative_to(ROOT)): base.sha(p) for p in inputs},
        'prior_executions': {str(p.relative_to(ROOT)): base.sha(p) for p in sorted(
            (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json'))},
        'parent_remaining_before_component': diagnostic['authorization_budget_remaining'],
        'schedule': fixed_schedule(), 'rss_gamma': .2, 'planner_gamma_events': 0,
        'budget': {'max_candidate_constructions': 6, 'wall_s': 10., 'cpu_s': 20.,
                   'r2_total_wall_s': 3600., 'r2_total_cpu_s': 7200.},
        'gates': base.GATES, 'leaf_full18_distance_rad': H,
        'expected_ranks': {'designated_passive_arm': 5, 'other_passive_arm': 6,
                           'passive': 11, 'full': 12},
        'fixed_coordinates': 'Only designated q4+=fraction*theta and q6-=fraction*theta. All other16 angles remain bitwise equal to original saved center, including q5=0. Do not change centers, branches, theta, h, geometry or source limits.',
        'expected_branches': 'Designated meeting set[1,3]; active1 remains branch1 and other passive remains branch3. No unique label is falsely assigned to singular wrist.',
        'FK_J_accounting': 'Per candidate poses_and_body requests3 mathematical arm FK/J and physical closure_vector_jacobian requests3, total36 mathematical calls if all6 finish. Each VI collision adapter query has1 native variant and independently calls arm_fk_jac for3 pose-consistency checks, adding18 adapter-internal arm FK/J: total54 for6 qualified candidates. No extra native FK crosscheck; compare all3 new mathematical poses to saved original native/B poses.',
        'planned_arm_FK_J_calls': {'mathematical': 36, 'adapter_internal': 18, 'total': 54},
        'interrupted_FK_J_and_query_accounting': 'Mathematical requested/completed remain separate. Before collision dispatch, adapter_internal_arm_FK_J_requested increases by3. Only a returned qualified CHECKED result confirms all3 adapter internal starts/completions and1 native_collision_queries. On a failed/interrupted dispatch, confirmed started/completed/native counts are lower bounds; requested minus confirmed completed and dispatched minus confirmed native queries are explicitly retained as unresolved, never reported as completed.',
        'IK_NR_sampling_planning_calls': 0, 'source_policy_collision_queries_cap': 6,
        'image_diagnostic': 'Using the already evaluated physical J only, record the rank5 image residual of each corresponding old fixed active chord. This is a diagnostic, not regular-to-fiber ingress qualification or an extra model call.',
        'positive_gate': 'All6 fixed points pass pose invariance/dual closure/expected independent ranks/branch sets/source bounds/actual qualified source-PQP checks. Original saved center plus theta/2 (219 only) plus endpoint have every raw full18 Euclidean leaf distance strictly<h. No wrapping or shortcut.',
        'failure_policy': 'Preserve every fixed node and failure; do not replace points or retry. Protocol/interface/process/independent-rank inconsistency stops the run with retained prefix. Other node failures remain explicit non-PASS; no threshold relaxation.',
        'scope_limits': ['Singular-fiber discrete component only; no regular-branch-to-fiber ingress tested.',
            'Original Q2 UNKNOWN remains unchanged; this is not author-native RBS.',
            'No global RSS result, all-mode equivalence, planning statistic, full-geometry or CCD certificate.'],
        **{key: bspec[key] for key in copied},
        'one_shot_policy': 'New fixed atomic retained component claim. Original/B/Q2/center claims never modified. No repeat/reset; subtract actual6 or interrupted prefix and actual wall/CPU from parent remaining.'}


def validate(spec, path, execute=False):
    expected = draft_protocol()
    for key, value in expected.items():
        if key != 'frozen' and spec.get(key) != value:
            raise base.StopQualification('FIBER_PROTOCOL_OR_INPUT_MISMATCH_'+key)
    if set(spec) != set(expected): raise base.StopQualification('FIBER_PROTOCOL_FIELD_SET_MISMATCH')
    if type(spec.get('frozen')) is not bool or execute and spec['frozen'] is not True:
        raise base.StopQualification('PROTOCOL_NOT_FROZEN')
    for relative, digest in spec['dependency_source_sha256'].items():
        if base.sha(ROOT/relative) != digest: raise base.StopQualification('PARENT_DEPENDENCY_CHANGED_'+relative)
    for key in ('collision_manifest', 'collision_controls_result'):
        if base.sha(ROOT/spec[key]) != spec[key+'_sha256']:
            raise base.StopQualification('COLLISION_DEPENDENCY_CHANGED_'+key)
    controls = json.loads((ROOT/spec['collision_controls_result']).read_text())
    if controls.get('passed') is not True or controls.get('status') != 'SOURCE_POLICY_QUALIFIED':
        raise base.StopQualification('COLLISION_CONTROLS_NOT_QUALIFIED')
    diagnostic = json.loads((CENTER/'execution.json').read_text())
    if diagnostic.get('counts', {}).get('active_FK_J_calls') != 2 or diagnostic.get('status') != 'FIXED_CENTER_FIRST_ORDER_DIAGNOSTIC_RECORDED':
        raise base.StopQualification('FIXED_CENTER_DIAGNOSTIC_INCOMPLETE')
    sources = [Path(__file__).resolve(), path, *[ROOT/p for p in spec['dependency_source_sha256']]]
    if execute:
        for source in sources:
            relative = str(source.relative_to(ROOT))
            subprocess.run(['git', 'ls-files', '--error-unmatch', relative], cwd=ROOT, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if subprocess.check_output(['git', 'status', '--porcelain', '--', relative], cwd=ROOT, text=True):
                raise base.StopQualification('SOURCE_OR_PROTOCOL_UNCOMMITTED_'+relative)
    return {str(p.relative_to(ROOT)): base.sha(p) for p in sources}


def run_fixed(spec, evidence, counts, results):
    fixtures = dict(center_diag.saved_fixtures()); bounds = base.source_limits('VI')
    grasps = base.model_geometry('VI')['grasps']; full_rows = (0, 1, 2, 6, 7, 8)
    for item in spec['schedule']:
        evidence.budget.remaining(); number = counts['candidate_constructions']+1
        if number > 6: raise base.StopQualification('MAX_SIX_FIBER_CANDIDATES')
        counts['candidate_constructions'] = number
        fixture = fixtures[item['parent_construction']]; saved = fixture['center']
        center = np.array(saved['q_rad']); q = center.copy(); s = item['designated_arm']; other = 5-s
        q4, q6 = 6*(s-1)+3, 6*(s-1)+5
        q[q4] += item['theta_fraction']*item['theta_rad']; q[q6] -= item['theta_fraction']*item['theta_rad']
        unchanged = [i for i in range(18) if i not in (q4, q6)]
        evidence.event('fiber_candidate_started', candidate=number, fixed_spec=item,
                        original_center_q18_rad=center.tolist(), q18_rad=q.tolist())
        if not np.array_equal(q[unchanged], center[unchanged]) or q[6*(s-1)+4] != 0.:
            raise base.StopQualification('UNCHANGED_SIXTEEN_ANGLES_OR_WRIST_ZERO_CHANGED')
        counts['independent_arm_FK_J_requested'] += 3
        poses, bodies = base.poses_and_body(q)
        counts['independent_arm_FK_J_completed'] += 3
        evidence.budget.remaining(); counts['independent_arm_FK_J_requested'] += 3
        residual, physical_j = base.closure_vector_jacobian(q, 'VI')
        counts['independent_arm_FK_J_completed'] += 3
        body_rank = base.vi_rank_report(*bodies, *grasps, relative_threshold=base.GATES['rank_relative'])
        physical_rank = {'full': base.rank_data(physical_j, full_rows),
                         'passive': base.rank_data(physical_j[:, 6:], full_rows)}
        flip = np.diag([-1., -1., 1., 1.])
        closure = [base.errors(poses[i+1], poses[0]@grasps[i]@flip) for i in (0, 1)]
        old_poses = {s: fixture['designated_saved']['world_pose'],
            1: saved['all_roots']['1'][1]['native']['T'],
            other: saved['all_roots'][str(other)][3]['native']['T']}
        invariant = {str(a): base.errors(poses[a-1], old_poses[a]) for a in (1, 2, 3)}
        branches = {str(a): base.geometric_branch_identity(q[6*(a-1):6*a]) for a in (1, 2, 3)}
        legal = bool(np.all((bounds[:, 0] <= q) & (q <= bounds[:, 1])))
        reasons = []
        if not all(base.closed(m) for m in closure): reasons.append('DUAL_CLOSURE_REJECTED')
        if not all(m['position_maxabs_mm'] <= base.GATES['fk_position_maxabs_mm'] and
                   m['rotation_matrix_maxabs'] <= base.GATES['fk_rotation_matrix_maxabs'] for m in invariant.values()):
            reasons.append('ORIGINAL_THREE_POSES_NOT_PRESERVED')
        if not legal: reasons.append('ORIGINAL_SOURCE_BOUNDS_REJECTED')
        for arm, expected in ((s, [1, 3]), (1, [1]), (other, [3])):
            if branches[str(arm)]['branch_set'] != expected: reasons.append('BRANCH_SET_REJECTED_ARM'+str(arm))
        if body_rank['passive_arm_'+str(s)]['rank'] != 5: reasons.append('DESIGNATED_RANK_NOT_5')
        if body_rank['passive_arm_'+str(other)]['rank'] != 6: reasons.append('OTHER_PASSIVE_RANK_NOT_6')
        if body_rank['passive_12_by_12']['rank'] != 11: reasons.append('PASSIVE_RANK_NOT_11')
        if body_rank['full_12_by_18']['rank'] != 12: reasons.append('FULL_RANK_NOT_12')
        if (physical_rank['full']['rank'] != body_rank['full_12_by_18']['rank'] or
                physical_rank['passive']['rank'] != body_rank['passive_12_by_12']['rank']):
            evidence.event('independent_rank_disagreement', candidate=number,
                            q18_rad=q.tolist(), body_rank=body_rank, physical_rank=physical_rank,
                            physical_jacobian=physical_j.tolist(),
                            body_jacobians=[b.tolist() for b in bodies],
                            poses=[p.tolist() for p in poses], dual_closure_metrics=closure)
            raise base.StopQualification('INDEPENDENT_RANK_COUNTS_DISAGREE')
        half = next(h for h in fixture['halves'] if h['half'] == item['half'])
        negative = item['half'].startswith('negative'); tree = half['tree']
        endpoint = np.array(tree['endpoint_a_q_rad'] if negative else tree['endpoint_b_q_rad'])
        rows = slice(6*(s-2), 6*(s-1)); js = physical_j[rows, 6*(s-1):6*s].copy(); js[:3] *= .001
        tangent = -physical_j[rows, :6]@(endpoint[:6]-center[:6]); tangent[:3] *= .001
        u, sigma, _ = np.linalg.svd(js); image_rank = int(np.count_nonzero(sigma > sigma[0]*1e-6))
        image_residual = tangent-u[:, :image_rank]@(u[:, :image_rank].T@tangent)
        record = {'candidate': number, 'fixed_spec': item, 'q18_rad': q.tolist(),
            'original_sixteen_angles_preserved_exactly': True, 'designated_q5_preserved_zero': True,
            'designated_q4_plus_q6_change_rad': float(q[q4]+q[q6]-center[q4]-center[q6]),
            'pose_invariance_errors': invariant, 'dual_closure_metrics': closure,
            'physical_residual': residual.tolist(), 'physical_jacobian': physical_j.tolist(),
            'body_jacobians': [b.tolist() for b in bodies], 'poses': [p.tolist() for p in poses],
            'body_rank_report': body_rank, 'physical_rank_report': physical_rank,
            'branch_identity': branches, 'all_source_bounds_legal': legal,
            'source_bounds_margin_rad': float(np.min(np.minimum(q-bounds[:, 0], bounds[:, 1]-q))),
            'image_diagnostic_not_ingress_qualification': {'rank': image_rank,
                'residual_norm_scaled': float(np.linalg.norm(image_residual)),
                'residual_vector_scaled': image_residual.tolist()},
            'collision_checked': False, 'source_policy_collision_qualified': False,
            'continuous_collision_certificate': False, 'regular_to_fiber_ingress_checked': False}
        evidence.event('fiber_pre_collision', rejection_reasons=reasons, **record)
        if not reasons:
            counts['collision_queries_started'] += 1
            counts['adapter_internal_arm_FK_J_requested'] += 3
            collision = base.collision_check(spec, q, evidence, number)
            counts['collision_queries_completed'] += 1
            counts['adapter_internal_arm_FK_J_started'] += 3
            counts['adapter_internal_arm_FK_J_completed'] += 3
            counts['native_collision_queries'] += 1
            record.update(collision_checked=True, collision=collision,
                          source_policy_collision_qualified=not collision['collision'])
            if collision['collision']: reasons.append('ORIGINAL_PQP_COLLISION')
        record.update(qualified=not reasons and record['collision_checked'], rejection_reasons=reasons)
        counts['qualified_candidates'] += int(record['qualified']); counts.update(reasons)
        results.append(record); evidence.event('fiber_candidate_finished', **record)
    segments = []
    for number, fixture in fixtures.items():
        center = np.array(fixture['center']['q_rad'])
        for half in fixture['halves']:
            points = [r for r in results if r['fixed_spec']['parent_construction'] == number and r['fixed_spec']['half'] == half['half']]
            points.sort(key=lambda r: r['fixed_spec']['theta_fraction'])
            qs = [center, *[np.array(r['q18_rad']) for r in points]]
            distances = [float(np.linalg.norm(qb-qa)) for qa, qb in zip(qs, qs[1:])]
            segment = {'parent_construction': number, 'half': half['half'],
                'fractions': [0., *[r['fixed_spec']['theta_fraction'] for r in points]],
                'leaf_full18_distances_rad': distances, 'all_leaf_distances_strictly_below_h': all(d < H for d in distances),
                'all_new_points_qualified': all(r['qualified'] for r in points),
                'original_center_reused_unchanged': True, 'continuous_collision_certificate': False}
            segments.append(segment); evidence.event('fiber_segment_finished', **segment)
    return segments


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
    previous = [json.loads((ROOT/p).read_text()) for p in spec['prior_executions']]
    prior_wall = sum(r['wall_s'] for r in previous); prior_cpu = sum(r['cpu_s'] for r in previous)
    remaining = spec['parent_remaining_before_component']
    if remaining['candidate_constructions'] < 6: raise base.StopQualification('INSUFFICIENT_REMAINING_CANDIDATES')
    runtime_spec = {**spec, 'budget': {**spec['budget'],
        'wall_s': min(spec['budget']['wall_s'], remaining['wall_s']),
        'cpu_s': min(spec['budget']['cpu_s'], remaining['cpu_s'])}}
    out = ROOT/'results/p4_full'/spec['run_id']
    if out.exists(): raise base.StopQualification('OUTPUT_EXISTS_NO_OVERWRITE')
    base.new_json(ROOT/'results/p4_full'/(ID+'.claim.json'), {
        'budget_id': base.BUDGET_ID, 'component_id': ID, 'run_id': spec['run_id'],
        'created_at_utc': base.utc(), 'protocol_sha256': base.sha(path),
        'caps': runtime_spec['budget'], 'policy': 'Retain after interruption; no reset/repeat.'})
    out.mkdir(parents=True, exist_ok=False)
    budget = base.RunBudget(runtime_spec, prior_wall, prior_cpu); evidence = base.Evidence(out, budget)
    counts = Counter({key: 0 for key in (
        'candidate_constructions', 'independent_arm_FK_J_requested', 'independent_arm_FK_J_completed',
        'adapter_internal_arm_FK_J_requested', 'adapter_internal_arm_FK_J_started',
        'adapter_internal_arm_FK_J_completed', 'native_collision_queries',
        'collision_queries_started', 'collision_queries_completed', 'qualified_candidates')})
    results, segments = [], []
    record = {'schema': SCHEMA, 'run_id': spec['run_id'], 'component_id': ID,
        'authorization_budget_id': base.BUDGET_ID, 'classification': spec['classification'],
        'started_at_utc': base.utc(), 'protocol_sha256': base.sha(path), 'source_hashes': hashes,
        'input_sha256': spec['input_sha256'], 'prior_execution_hashes': spec['prior_executions'],
        'previous_wall_s': prior_wall, 'previous_cpu_s': prior_cpu,
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'original_Q2_unknown_unchanged': True, 'regular_to_fiber_ingress_checked': False,
        'IK_NR_sampling_planning_calls': 0, 'full_RSS_or_planning_pass': False,
        'scope_limits': spec['scope_limits'], 'collision_qualification_scope': spec['collision_qualification_scope']}
    exit_code = 0
    try:
        evidence.event('run_started', protocol=spec, source_hashes=hashes)
        segments = run_fixed(spec, evidence, counts, results)
        record['status'] = 'SINGULAR_FIBER_COMPONENT_RECORDED'
    except BaseException as exc:
        record.update(status='STOP_RETAINED_PREFIX', error=repr(exc)); exit_code = 2
        evidence.event('run_stopped', error=repr(exc))
    finally:
        budget.close(); wall = time.monotonic()-budget.started; used_cpu = budget.cpu()-budget.cpu_start
        counts['adapter_internal_arm_FK_J_unresolved_requested'] = (
            counts['adapter_internal_arm_FK_J_requested']-counts['adapter_internal_arm_FK_J_completed'])
        counts['native_collision_queries_unresolved_dispatched'] = (
            counts['collision_queries_started']-counts['native_collision_queries'])
        counts['total_arm_FK_J_requested'] = (
            counts['independent_arm_FK_J_requested']+counts['adapter_internal_arm_FK_J_requested'])
        counts['total_arm_FK_J_completed'] = (
            counts['independent_arm_FK_J_completed']+counts['adapter_internal_arm_FK_J_completed'])
        passed = (len(results) == 6 and all(r['qualified'] for r in results) and len(segments) == 4 and
                  all(s['all_leaf_distances_strictly_below_h'] for s in segments))
        record.update(counts=dict(counts), wall_s=wall, cpu_s=used_cpu, ended_at_utc=base.utc(),
            candidate_results=results, segment_results=segments,
            component_coverage_gate_passed=passed, coverage_gate_status='PASS_COMPONENT_DISCRETE_ONLY' if passed else 'UNKNOWN_OR_FAILED',
            cumulative_execution_wall_s=prior_wall+wall, cumulative_execution_cpu_s=prior_cpu+used_cpu,
            authorization_budget_remaining={'candidate_constructions': max(0, remaining['candidate_constructions']-counts['candidate_constructions']),
                'wall_s': max(0., remaining['wall_s']-wall), 'cpu_s': max(0., remaining['cpu_s']-used_cpu),
                'r2_total_wall_s': max(0., 3600-prior_wall-wall), 'r2_total_cpu_s': max(0., 7200-prior_cpu-used_cpu),
                'policy': 'Actual fixed candidates and wall/CPU charged to original authorization; preserve prefix, no reset/repeat.'})
        base.new_json(out/'execution.json', record); evidence.events.close()
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__': raise SystemExit(main())
