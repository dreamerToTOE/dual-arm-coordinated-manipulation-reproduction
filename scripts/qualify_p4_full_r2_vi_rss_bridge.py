#!/usr/bin/env python3
"""One-shot Q2 continuation of saved VI RECONSTRUCTED wrist samples.

Draft generation and draft validation read saved evidence only. Execution needs
a committed frozen protocol. No original claim, source, endpoint or run is
modified. The source-text RBS audit is distinct from the stricter independent
three-arm discrete witness; neither certifies continuous collision freedom.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_p4_full_r2_vi_rss_reconstructed as base

np, ROOT = base.np, base.ROOT
SCHEMA = 'P4_R2_VI_RSS_BRIDGE_QUALIFICATION_V1'
PARENT_RUN = '20261015_R2_VI_RSS_RECONSTRUCTED01'
PARENT = ROOT/'results/p4_full'/PARENT_RUN
PARENT_EVENTS = PARENT/'events.jsonl'
PARENT_EXECUTION = PARENT/'execution.json'
CONTINUATION_ID = base.BUDGET_ID+'.Q2_BRIDGE_V1'
AUTHOR = Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/ckcComau3/validity_checkers')
FIXTURE_IDS = (219, 643)  # First source-policy-qualified sample for s=3, then s=2.
EXPECTED_PARENT = {'candidate_constructions': 868, 'wall_s': 45.133593771999585,
                   'cpu_s': 5.6411750000000005}
STRICT = {'delta_rad': .01, 'curve_t_rad': [-.01, -.005, .005, .01],
          'leaf_full18_distance_rad': .0025, 'max_depth': 3,
          'max_midpoints_per_half': 8, 'depth_root': 0,
          'depth_rule': 'At depth>=3 inspect the leaf only; d>=h is UNKNOWN_DEPTH_CAP. No projection at depth3.',
          'distance': 'Euclidean norm of all18 original joint coordinates, no angular wrapping; pass iff d<h.',
          'midpoint': 'All18 arithmetic midpoint; keep active arm1 first6 bitwise equal to the unprojected midpoint; project arms2/3 only.',
          'lift_reference': 'Explicit curve: saved center per-arm q. RBS: corresponding passive6 of the full18 unprojected midpoint.',
          'lift_rule': 'Enumerate all source-limit-legal true2pi integer copies of the one fixed analytic branch. Minimize squared raw6 distance to reference; exact ties use q lexicographic order. No pi wrist-family changes.',
          'designated_branch_negative': 1, 'designated_branch_positive': 3,
          'other_passive_branch': 3, 'curve_active_arm1_branch': 1,
          'center_policy': 'Reuse saved center unchanged, including actual q4/q6. No IK/canonical replacement of center.',
          'half_order': ['negative_endpoint_to_center', 'center_to_positive_endpoint'],
          'seed_reuse': 'The +/-delta/2 curve points are separate evidence; never reused as RBS midpoints.'}
SOURCE_RBS = {'classification': 'SOURCE_TEXT_AUDIT_ONLY / INDEPENDENT_THREE_ARM_ADAPTATION',
              'tolerance_rad': .05, 'max_depth': 150,
              'singular_shortcut_multiplier': 7,
              'singular_shortcut_rad': .35000000000000003,
              'distance': 'normDistanceDuo: raw full18 Euclidean norm; no wrapping.',
              'order': 'd<.05 before projection; depth>150 rejects; arithmetic midpoint then fixed-branch IK and collision; singular variant returns when projected midpoint distance to saved singular endpoint<7*.05.',
              'execution': 'Derive ordinary and singular textual traversal only from the strict tree already evaluated; no extra scientific calls. Missing projected tree nodes mean UNKNOWN_UNEVALUATED_NODE.',
              'vacuous': 'Any d<.05 leaf without a projected midpoint is VACUOUS_THRESHOLD_PASS, never evidence that RBS projection or continuity passed.',
              'source_compile_defects': ['singular checkMotionRBS declares q1/q2 but uses undeclared q3',
                                        'line661 uses dsg2 instead of qsg2 and inconsistent recursive arity'],
              'native_original_execution': False}


def digest_value(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def fixtures_from_saved():
    """Read exact saved event lines; no kinematics or rank calculation."""
    found, first_by_arm = {}, {}
    for line in PARENT_EVENTS.read_bytes().splitlines():
        row = json.loads(line)
        if row.get('event') != 'construction_finished' or not row.get('fully_qualified_candidate'):
            continue
        s = row['designated_passive_arm']
        first_by_arm.setdefault(s, row['construction'])
        if row['construction'] in FIXTURE_IDS:
            found[row['construction']] = {
                'construction': row['construction'], 'designated_passive_arm': s,
                'seed': row['seed'], 'request': row['request'], 'attempt': row['attempt'],
                'q_rad': row['q_rad'], 'q_sha256': digest_value(row['q_rad']),
                'parent_event_line_sha256': hashlib.sha256(line).hexdigest(),
                'event_line_hash_scope': 'UTF8 event line excluding newline',
                'saved_record': row}
    if first_by_arm != {3: 219, 2: 643} or set(found) != set(FIXTURE_IDS):
        raise base.StopQualification('FIXED_FIRST_BY_ARM_PARENT_FIXTURE_MISMATCH')
    return [found[i] for i in FIXTURE_IDS]


def ledger_paths():
    # Freeze every existing R2 execution, not only the original three batches.
    return sorted((ROOT/'results/p4_full').glob('20261015_R2_*/execution.json'))


def draft_protocol():
    parent = json.loads(PARENT_EXECUTION.read_text())
    fixtures = [{k: v for k, v in item.items() if k != 'saved_record'}
                for item in fixtures_from_saved()]
    bspec = json.loads((ROOT/'configs/p4_full/r2_vi_rss_reconstructed_qualification_v1.json').read_text())
    retained = ('ik_binary', 'ik_binary_sha256', 'collision_checker_command',
                'collision_manifest', 'collision_manifest_sha256', 'collision_controls_result',
                'collision_controls_result_sha256', 'collision_success_statuses',
                'collision_qualification_scope')
    return {'schema': SCHEMA, 'frozen': False,
            'run_id': '20261015_R2_VI_RSS_BRIDGE01',
            'authorization_budget_id': base.BUDGET_ID, 'continuation_id': CONTINUATION_ID,
            'classification': 'RECONSTRUCTED / INDEPENDENT-RECONSTRUCTION / LOCAL-WRIST-BRIDGE-ONLY',
            'parent_run': PARENT_RUN,
            'parent_execution_sha256': base.sha(PARENT_EXECUTION),
            'parent_events_sha256': base.sha(PARENT_EVENTS),
            'parent_claim': str((ROOT/'results/p4_full'/(base.BUDGET_ID+'.claim.json')).relative_to(ROOT)),
            'parent_claim_sha256': base.sha(ROOT/'results/p4_full'/(base.BUDGET_ID+'.claim.json')),
            'parent_consumed': EXPECTED_PARENT,
            'parent_remaining_before_continuation': parent['authorization_budget_remaining'],
            'parent_source_hashes': parent['source_hashes'],
            'prior_executions': {str(p.relative_to(ROOT)): base.sha(p) for p in ledger_paths()},
            'budget': {'max_candidate_constructions': 40, 'wall_s': 60., 'cpu_s': 120.,
                       'r2_total_wall_s': 3600., 'r2_total_cpu_s': 7200.},
            'budget_scope': 'These caps consume the remaining original960/180wall/360CPU authorization; original868/45.133593771999585/5.6411750000000005 are not reset. Eight explicit curve constructions plus at most4*7 midpoint constructions=36;40 is a hard conservative ceiling.',
            'active_arm': 1, 'rss_gamma': .2, 'planner_gamma_events': 0,
            'random_draws': 0, 'formal_planning_calls': 0,
            'fixed_fixtures': fixtures, 'strict_discrete': STRICT,
            'source_rbs_text_semantics': SOURCE_RBS, 'gates': base.GATES,
            'author_source_hashes': {str(p): base.sha(p) for p in
                (AUTHOR/'StateValidityCheckerRSS.cpp', AUTHOR/'StateValidityCheckerRSS.h')},
            **{k: bspec[k] for k in retained},
            'positive_gate': 'Both fixed fixtures need all4 regular explicit curve points and both strict discrete half-connections. Every retained node is closure/bounds/expected-rank/branch/source-policy-collision qualified; all final full18 leaf distances<h. No fixture/branch/delta replacement, canonical center or shortcut PASS.',
            'failure_policy': 'Preserve each failure; continue only the other predeclared fixtures/halves while within the same cap. Unsound accepted IK, inconsistent independent ranks, protocol or process errors stop all new scientific calls. Depth/branch-family/locality uncertainty is UNKNOWN, no adaptive solver or retry.',
            'claims_not_established': ['original native VI RSS runnable equivalence', 'all RSS modes',
                                      'global RSS/PCS/NR planning', 'original TableI/II statistics',
                                      'complete physical collision geometry or CCD',
                                      'continuous mathematical path certificate'],
            'one_shot_policy': 'Create a new atomic fixed Q2 continuation claim; never change/delete original claim. Any prior sibling continuation claim prevents execution. Preserve interrupted prefix and charge it; no restart flag.'}


def validate_protocol(spec, path, *, execute=False):
    expected = draft_protocol()
    for key, value in expected.items():
        if key in ('frozen', 'run_id'):
            continue
        if spec.get(key) != value:
            raise base.StopQualification('PROTOCOL_CONSTANT_OR_HASH_MISMATCH_'+key)
    if set(spec) != set(expected):
        raise base.StopQualification('PROTOCOL_FIELD_SET_MISMATCH')
    if execute and spec.get('frozen') is not True:
        raise base.StopQualification('PROTOCOL_NOT_FROZEN')
    if type(spec.get('frozen')) is not bool:
        raise base.StopQualification('PROTOCOL_FROZEN_NOT_BOOLEAN')
    run_id = spec['run_id']
    if not run_id or Path(run_id).name != run_id or run_id in ('.', '..', PARENT_RUN):
        raise base.StopQualification('INVALID_RUN_ID')
    parent = json.loads(PARENT_EXECUTION.read_text())
    if (parent['counts']['candidate_constructions'] != EXPECTED_PARENT['candidate_constructions'] or
            parent['wall_s'] != EXPECTED_PARENT['wall_s'] or
            parent['cpu_s'] != EXPECTED_PARENT['cpu_s'] or
            parent.get('candidate_coverage_gate_passed') is not True):
        raise base.StopQualification('PARENT_EXECUTION_NOT_EXPECTED_QUALIFIED_PREFIX')
    for source, digest in spec['parent_source_hashes'].items():
        if base.sha(ROOT/source) != digest:
            raise base.StopQualification('PARENT_SOURCE_CHANGED_'+source)
    for key in ('ik_binary', 'collision_manifest', 'collision_controls_result'):
        if base.sha(ROOT/spec[key]) != spec[key+'_sha256']:
            raise base.StopQualification('FROZEN_DEPENDENCY_HASH_MISMATCH_'+key)
    controls = json.loads((ROOT/spec['collision_controls_result']).read_text())
    if controls.get('passed') is not True or controls.get('status') != 'SOURCE_POLICY_QUALIFIED':
        raise base.StopQualification('COLLISION_POLICY_CONTROLS_NOT_QUALIFIED')
    for fixture in fixtures_from_saved():
        row = fixture['saved_record']; s = fixture['designated_passive_arm']; other = 5-s
        identity = row['branch_identity']; rank = row['body_rank_report']
        if (row.get('source_policy_collision_qualified') is not True or
                row.get('all_three_source_bounds_legal') is not True or
                identity['selected_arm1_branch'] != 1 or
                identity['selected_other_passive_branch'] != 3 or
                identity['selected_other_passive_arm'] != other or
                identity['sampled_singular_branch_set']['branch_set'] != [1, 3] or
                rank['passive_arm_'+str(s)]['rank'] != 5 or
                rank['passive_arm_'+str(other)]['rank'] != 6 or
                rank['passive_12_by_12']['rank'] != 11 or
                rank['full_12_by_18']['rank'] != 12 or
                fixture['q_rad'][6*(s-1)+4] != 0.):
            raise base.StopQualification('SAVED_CENTER_EVIDENCE_NOT_QUALIFIED')
    sources = [Path(__file__).resolve(), path,
               *[ROOT/k for k in spec['parent_source_hashes']],
               ROOT/'baselines/p4_full/geometry_consistent/spatial_batch_driver.cpp',
               ROOT/'baselines/p4_full/geometry_consistent/spatial_ik_patch.py']
    hashes = {str(p.relative_to(ROOT)): base.sha(p) for p in sources}
    if execute:
        for source in sources:
            relative = str(source.relative_to(ROOT))
            subprocess.run(['git', 'ls-files', '--error-unmatch', relative], check=True,
                           cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if subprocess.check_output(['git', 'status', '--porcelain', '--', relative], cwd=ROOT, text=True):
                raise base.StopQualification('SOURCE_OR_PROTOCOL_NOT_COMMITTED_'+relative)
    return hashes


def fixed_lift(root, reference, bounds):
    """All legal true2pi copies, then closest raw-coordinate representative."""
    if not root['native']['success']:
        return None, {'branch': root['branch'], 'status': 'FIXED_BRANCH_NATIVE_IK_FAILED',
                      'reference_q_rad': reference.tolist(), 'candidates': []}
    raw = np.asarray(root['native']['solution'], dtype=float)
    integer_sets = [list(range(math.ceil((lo-x)/(2*math.pi)),
                               math.floor((hi-x)/(2*math.pi))+1))
                    for x, (lo, hi) in zip(raw, bounds)]
    candidates = []
    for integers in itertools.product(*integer_sets):
        q = raw+2*math.pi*np.asarray(integers)
        if np.all((bounds[:, 0] <= q) & (q <= bounds[:, 1])):
            candidates.append({'q_rad': q.tolist(), 'true2pi_integers': list(integers),
                               'raw6_squared_distance_rad2': float(np.dot(q-reference, q-reference))})
    candidates.sort(key=lambda r: (r['raw6_squared_distance_rad2'], tuple(r['q_rad'])))
    result = {'branch': root['branch'], 'reference_q_rad': reference.tolist(),
              'canonical_q_rad': raw.tolist(), 'candidates': candidates,
              'status': 'SELECTED' if candidates else 'NO_LEGAL_TRUE2PI_COPY',
              'selected_index': 0 if candidates else None}
    return (np.asarray(candidates[0]['q_rad']) if candidates else None), result


class BridgeRun:
    def __init__(self, spec, evidence, counts, grasps):
        self.spec, self.evidence, self.counts, self.grasps = spec, evidence, counts, grasps
        self.bounds = base.source_limits('VI')
        self.binary = ROOT/spec['ik_binary']

    def begin(self, kind, fixture, **details):
        self.evidence.budget.remaining()
        number = self.counts['candidate_constructions']+1
        if number > self.spec['budget']['max_candidate_constructions']:
            raise base.StopQualification('Q2_MAX_CONSTRUCTIONS')
        self.counts['candidate_constructions'] = number
        self.counts[kind+'_constructions'] += 1
        self.evidence.event('construction_started', construction=number, construction_kind=kind,
                            parent_construction=fixture['construction'], **details)
        return number

    def roots(self, targets, arms, retained_arm, retained_q, number):
        self.counts['ik_branch_evaluations_requested'] += 16
        self.counts['native_fk_requests'] += 1
        roots = base.all_roots(targets, arms, retained_arm, retained_q, self.binary,
                               self.evidence.folder, self.evidence, number)
        self.counts['ik_branch_evaluations_completed'] += 16
        return roots

    def finish(self, q, fixture, branches, number, record):
        s = fixture['designated_passive_arm']; other = 5-s
        reasons = []
        if q is None:
            record.update(status='UNKNOWN_FIXED_BRANCH_NO_LEGAL_COPY', qualified=False)
            self.evidence.event('construction_finished', construction=number, **record)
            self.counts['fixed_branch_no_legal_copy'] += 1
            return record
        self.evidence.budget.remaining()
        poses, bodies = base.poses_and_body(q)
        flip = np.diag([-1., -1., 1., 1.])
        metrics = [base.errors(poses[i+1], poses[0]@self.grasps[i]@flip) for i in (0, 1)]
        transforms = base.vi_residual_transforms(*poses, *self.grasps)
        rank = base.vi_rank_report(*bodies, *self.grasps, relative_threshold=base.GATES['rank_relative'])
        physical_residual, physical_j = base.closure_vector_jacobian(q, 'VI')
        p_rows = (0, 1, 2, 6, 7, 8)
        physical_rank = {'full': base.rank_data(physical_j, p_rows),
                         'passive': base.rank_data(physical_j[:, 6:], p_rows)}
        branch_identity = {str(a): base.geometric_branch_identity(q[6*(a-1):6*a]) for a in (1, 2, 3)}
        legal = bool(np.all((self.bounds[:, 0] <= q) & (q <= self.bounds[:, 1])))
        if not all(base.closed(m) for m in metrics): reasons.append('DUAL_CLOSURE_REJECTED')
        if not legal: reasons.append('SOURCE_JOINT_LIMIT_REJECTED')
        for arm, branch in branches.items():
            identity = branch_identity[str(arm)]
            if not identity['unique'] or identity['branch_set'] != [branch]:
                reasons.append('REGULAR_FIXED_BRANCH_IDENTITY_REJECTED_ARM'+str(arm))
        if rank['passive_arm_'+str(s)]['rank'] != 6: reasons.append('DESIGNATED_REGULAR_RANK_NOT_6')
        if rank['passive_arm_'+str(other)]['rank'] != 6: reasons.append('OTHER_PASSIVE_RANK_NOT_6')
        if rank['passive_12_by_12']['rank'] != 12: reasons.append('PASSIVE_REGULAR_RANK_NOT_12')
        if rank['full_12_by_18']['rank'] != 12: reasons.append('FULL_CONSTRAINT_RANK_NOT_12')
        if (physical_rank['full']['rank'] != rank['full_12_by_18']['rank'] or
                physical_rank['passive']['rank'] != rank['passive_12_by_12']['rank']):
            self.evidence.event('independent_rank_counts_disagree', construction=number,
                                body=rank, physical=physical_rank, q_rad=q.tolist())
            raise base.StopQualification('INDEPENDENT_RANK_COUNTS_DISAGREE')
        record.update(q_rad=q.tolist(), q_sha256=digest_value(q.tolist()),
                      physical_loop_metrics=metrics, loop_error_transforms=[t.tolist() for t in transforms],
                      all_three_source_bounds_legal=legal, body_rank_report=rank,
                      independent_world_residual_rank_report=physical_rank,
                      physical_residual=physical_residual.tolist(), physical_jacobian=physical_j.tolist(),
                      body_jacobians=[j.tolist() for j in bodies], branch_identity=branch_identity,
                      required_branches={str(a): b for a, b in branches.items()},
                      collision_checked=False, source_policy_collision_qualified=False,
                      full_geometry_collision_qualified=False, continuous_collision_certificate=False)
        self.evidence.event('candidate_pre_collision', construction=number,
                            rejection_reasons=reasons, **record)
        if not reasons:
            self.counts['collision_queries_started'] += 1
            result = base.collision_check(self.spec, q, self.evidence, number)
            self.counts['collision_queries_completed'] += 1
            record.update(collision_checked=True, collision=result,
                          source_policy_collision_qualified=not result['collision'])
            if result['collision']: reasons.append('ORIGINAL_PQP_COLLISION')
        status = 'PASS' if not reasons and record['collision_checked'] else 'FAILED_NODE_QUALIFICATION'
        if (record['construction_kind'].startswith('RBS_') and
                (not branch_identity[str(s)]['unique'] or rank['passive_arm_'+str(s)]['rank'] < 6)):
            status = 'UNKNOWN_INTERNAL_SINGULAR_FAMILY'
        record.update(rejection_reasons=reasons, qualified=not reasons and record['collision_checked'],
                      status=status)
        self.evidence.event('construction_finished', construction=number, **record)
        self.counts.update(reasons)
        self.counts['qualified_constructions'] += int(record['qualified'])
        return record

    def curve_point(self, fixture, t):
        s = fixture['designated_passive_arm']; other = 5-s
        center = np.asarray(fixture['q_rad']); qs = center[6*(s-1):6*s].copy(); qs[4] = t
        number = self.begin('explicit_curve', fixture, t_rad=t, retained_designated_q_rad=qs.tolist())
        ts, _ = base.arm_fk_jac(qs, 'VI', s)
        targets = base.vi_target_poses(ts, s, *self.grasps)
        roots = self.roots(targets, (1, other), s, qs, number)
        q = center.copy(); q[6*(s-1):6*s] = qs
        lifts = {}; complete = True
        for arm, branch in ((1, 1), (other, 3)):
            section = slice(6*(arm-1), 6*arm)
            lifted, selection = fixed_lift(roots[arm][branch], center[section], self.bounds[section])
            lifts[str(arm)] = selection
            if lifted is None: complete = False
            else: q[section] = lifted
        record = {'construction_kind': 'EXPLICIT_Q5_PARAMETER_CURVE_NOT_RBS', 'parent_construction': fixture['construction'],
                  't_rad': t, 'all_roots': {str(a): r for a, r in roots.items()},
                  'lift_selections': lifts, 'target_poses': {str(a): v.tolist() for a, v in targets.items()},
                  'retained_designated_q_rad': qs.tolist()}
        branches = {1: 1, other: 3, s: 1 if t < 0 else 3}
        return self.finish(q if complete else None, fixture, branches, number, record)

    def midpoint(self, fixture, qa, qb, branch, node_id):
        s = fixture['designated_passive_arm']; other = 5-s
        raw = (qa+qb)/2.
        number = self.begin('rbs_midpoint', fixture, node_id=node_id,
                            endpoint_a_q_rad=qa.tolist(), endpoint_b_q_rad=qb.tolist(),
                            unprojected_full18_midpoint_q_rad=raw.tolist(), designated_branch=branch)
        t1, _ = base.arm_fk_jac(raw[:6], 'VI', 1)
        flip = np.diag([-1., -1., 1., 1.])
        targets = {1: t1, 2: t1@self.grasps[0]@flip, 3: t1@self.grasps[1]@flip}
        roots = self.roots(targets, (2, 3), 1, raw[:6], number)
        q = raw.copy(); lifts = {}; complete = True
        for arm in (2, 3):
            section = slice(6*(arm-1), 6*arm); desired = branch if arm == s else 3
            lifted, selection = fixed_lift(roots[arm][desired], raw[section], self.bounds[section])
            lifts[str(arm)] = selection
            if lifted is None: complete = False
            else: q[section] = lifted
        if not np.array_equal(q[:6], raw[:6]):
            raise base.StopQualification('ACTIVE_ARM_MIDPOINT_WAS_CHANGED')
        record = {'construction_kind': 'RBS_ACTIVE1_ARITHMETIC_MIDPOINT_PASSIVE23_ANALYTIC_PROJECTION',
                  'parent_construction': fixture['construction'], 'node_id': node_id,
                  'unprojected_full18_midpoint_q_rad': raw.tolist(),
                  'active_arm1_retained_exactly': True,
                  'all_roots': {str(a): r for a, r in roots.items()}, 'lift_selections': lifts,
                  'target_poses': {str(a): v.tolist() for a, v in targets.items()}}
        return self.finish(q if complete else None, fixture, {1: 1, other: 3, s: branch}, number, record)

    def strict_half(self, fixture, qa, qb, branch, label):
        used = 0
        def visit(a, b, depth, address):
            nonlocal used
            self.evidence.budget.remaining()
            distance = float(np.linalg.norm(a-b))
            node = {'node_id': address, 'depth': depth, 'endpoint_a_q_rad': a.tolist(),
                    'endpoint_b_q_rad': b.tolist(), 'distance_full18_rad': distance}
            if distance < STRICT['leaf_full18_distance_rad']:
                node.update(status='PASS_LEAF_STRICT_DISTANCE', passed=True)
            elif depth >= STRICT['max_depth']:
                node.update(status='UNKNOWN_DEPTH_CAP', passed=False)
            elif used >= STRICT['max_midpoints_per_half']:
                node.update(status='UNKNOWN_MIDPOINT_CAP', passed=False)
            else:
                used += 1
                projection = self.midpoint(fixture, a, b, branch, address)
                node['projection'] = projection
                if not projection['qualified']:
                    node.update(status=projection['status'], passed=False)
                else:
                    m = np.asarray(projection['q_rad'])
                    node['left_full18_distance_rad'] = float(np.linalg.norm(a-m))
                    node['right_full18_distance_rad'] = float(np.linalg.norm(m-b))
                    node['max_projected_joint_displacement_from_raw_midpoint_rad'] = float(np.max(np.abs(m-(a+b)/2)))
                    # Evaluate both predeclared branches of recursion even if
                    # one leaf fails, keeping the bounded evidence tree complete.
                    left = visit(a, m, depth+1, address+'L')
                    right = visit(m, b, depth+1, address+'R')
                    node.update(left=left, right=right,
                                status='PASS_STRICT_DISCRETE' if left['passed'] and right['passed'] else 'UNKNOWN_OR_FAILED_CHILD',
                                passed=left['passed'] and right['passed'])
            self.evidence.event('rbs_node_finished', parent_construction=fixture['construction'], half=label, **node)
            return node
        tree = visit(qa, qb, 0, f"f{fixture['construction']}_{label}")
        return {'half': label, 'designated_branch': branch, 'midpoint_constructions': used,
                'tree': tree, 'strict_discrete_passed': tree['passed'],
                'source_text_ordinary_audit': source_text_audit(tree, np.asarray(fixture['q_rad']), False),
                'source_text_singular_audit': source_text_audit(tree, np.asarray(fixture['q_rad']), True)}


def source_text_audit(node, singular, use_shortcut):
    """Pure reduction of already saved tree: never FK, IK or collision."""
    if node['distance_full18_rad'] < SOURCE_RBS['tolerance_rad']:
        return {'status': 'VACUOUS_THRESHOLD_PASS', 'textual_return': True,
                'projection_calls_in_textual_prefix': 0, 'counts_as_strict_bridge_evidence': False}
    if node['depth'] > SOURCE_RBS['max_depth']:
        return {'status': 'TEXTUAL_DEPTH_FAIL', 'textual_return': False}
    projection = node.get('projection')
    if projection is None:
        return {'status': 'UNKNOWN_UNEVALUATED_NODE', 'textual_return': None}
    if not projection['qualified']:
        # Extra independent rank/branch gates are stricter than source
        # isValidRBS. A gated/skipped source collision query is not its false
        # return, and the author's singular family is not reconstructed here.
        known_failure = (projection['status'] == 'UNKNOWN_FIXED_BRANCH_NO_LEGAL_COPY' or
                         projection.get('collision', {}).get('collision') is True)
        return {'status': 'ADAPTED_FIXED_BRANCH_OR_COLLISION_FAILED' if known_failure else
                         'UNKNOWN_QUALIFICATION_GATED_NO_SOURCE_RETURN',
                'textual_return': False if known_failure else None,
                'strict_projection_status': projection['status']}
    dsg = float(np.linalg.norm(np.asarray(projection['q_rad'])-singular))
    if use_shortcut and dsg < SOURCE_RBS['singular_shortcut_rad']:
        return {'status': 'TEXTUAL_SINGULAR_SHORTCUT_PASS', 'textual_return': True,
                'projected_midpoint_to_singular_full18_rad': dsg,
                'projection_calls_in_textual_prefix': 1, 'counts_as_strict_bridge_evidence': False}
    if 'left' not in node or 'right' not in node:
        return {'status': 'UNKNOWN_UNEVALUATED_CHILD', 'textual_return': None}
    left = source_text_audit(node['left'], singular, use_shortcut)
    right = source_text_audit(node['right'], singular, use_shortcut)
    values = [left['textual_return'], right['textual_return']]
    result = False if False in values else (None if None in values else True)
    return {'status': 'TEXTUAL_ADAPTED_TRAVERSAL', 'textual_return': result,
            'left': left, 'right': right, 'native_original_execution': False}


def run_all(spec, evidence, counts):
    runner = BridgeRun(spec, evidence, counts, base.model_geometry('VI')['grasps'])
    results = []
    for fixture in fixtures_from_saved():
        evidence.event('saved_center_reused_without_scientific_recalculation',
                        parent_construction=fixture['construction'],
                        q_rad=fixture['q_rad'], parent_event_line_sha256=fixture['parent_event_line_sha256'],
                        saved_record=fixture['saved_record'])
        points = {t: runner.curve_point(fixture, t) for t in STRICT['curve_t_rad']}
        center = np.asarray(fixture['q_rad']); halves = []
        for label, t, branch in (('negative_endpoint_to_center', -.01, 1),
                                  ('center_to_positive_endpoint', .01, 3)):
            endpoint = points[t]
            if not endpoint['qualified']:
                halves.append({'half': label, 'strict_discrete_passed': False,
                               'status': 'NOT_EXECUTED_UNQUALIFIED_FIXED_BRACKET',
                               'endpoint_status': endpoint['status']})
                continue
            regular = np.asarray(endpoint['q_rad'])
            qa, qb = (regular, center) if t < 0 else (center, regular)
            halves.append(runner.strict_half(fixture, qa, qb, branch, label))
        result = {'parent_construction': fixture['construction'],
                  'designated_passive_arm': fixture['designated_passive_arm'],
                  'curve_point_results': {str(t): row for t, row in points.items()},
                  'half_results': halves,
                  'curve_bracket_qualified': all(row['qualified'] for row in points.values()),
                  'both_strict_halves_qualified': all(row['strict_discrete_passed'] for row in halves)}
        result['local_wrist_bridge_qualified'] = result['curve_bracket_qualified'] and result['both_strict_halves_qualified']
        evidence.event('fixture_finished', **result); results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe-protocol', action='store_true', help='Saved-evidence-only draft JSON; no scientific calls.')
    parser.add_argument('--validate-draft', type=Path, help='Static fields/hashes/saved-evidence validation only; no scientific calls.')
    parser.add_argument('--protocol', type=Path, help='Execute once using committed frozen protocol.')
    args = parser.parse_args()
    if sum(bool(v) for v in (args.describe_protocol, args.validate_draft, args.protocol)) != 1:
        parser.error('choose exactly one of --describe-protocol / --validate-draft / --protocol')
    if args.describe_protocol:
        print(json.dumps(draft_protocol(), ensure_ascii=False, indent=2)); return 0
    path = (args.validate_draft or args.protocol).resolve()
    spec = json.loads(path.read_text())
    hashes = validate_protocol(spec, path, execute=bool(args.protocol))
    if args.validate_draft:
        print(json.dumps({'status': 'STATIC_DRAFT_VALIDATED', 'frozen': spec['frozen'],
                          'scientific_calls': 0, 'source_hashes': hashes}, indent=2)); return 0
    previous = [json.loads((ROOT/p).read_text()) for p in spec['prior_executions']]
    prior_wall = sum(p['wall_s'] for p in previous); prior_cpu = sum(p['cpu_s'] for p in previous)
    parent_remaining = spec['parent_remaining_before_continuation']
    runtime_spec = dict(spec)
    runtime_spec['budget'] = {**spec['budget'],
                            'wall_s': min(spec['budget']['wall_s'], parent_remaining['wall_s']),
                            'cpu_s': min(spec['budget']['cpu_s'], parent_remaining['cpu_s'])}
    if spec['budget']['max_candidate_constructions'] > parent_remaining['candidate_constructions']:
        raise base.StopQualification('CONTINUATION_EXCEEDS_PARENT_REMAINING_CONSTRUCTIONS')
    claim_folder = ROOT/'results/p4_full'
    if list(claim_folder.glob(base.BUDGET_ID+'.*.claim.json')):
        raise base.StopQualification('SIBLING_CONTINUATION_CLAIM_EXISTS_NO_BUDGET_RESET')
    out = claim_folder/spec['run_id']
    if out.exists(): raise base.StopQualification('OUTPUT_EXISTS_NO_OVERWRITE')
    base.new_json(claim_folder/(CONTINUATION_ID+'.claim.json'), {
        'budget_id': base.BUDGET_ID, 'continuation_id': CONTINUATION_ID,
        'run_id': spec['run_id'], 'created_at_utc': base.utc(),
        'protocol_sha256': base.sha(path), 'parent_claim_sha256': spec['parent_claim_sha256'],
        'parent_execution_sha256': spec['parent_execution_sha256'],
        'parent_consumed': EXPECTED_PARENT, 'continuation_caps': runtime_spec['budget'],
        'policy': 'Atomic retained claim; no restart/reset, original claim unchanged.'})
    out.mkdir(parents=True, exist_ok=False)
    budget = base.RunBudget(runtime_spec, prior_wall, prior_cpu)
    evidence = base.Evidence(out, budget); counts = Counter(); results = []
    record = {'schema': SCHEMA, 'run_id': spec['run_id'],
              'authorization_budget_id': base.BUDGET_ID, 'continuation_id': CONTINUATION_ID,
              'started_at_utc': base.utc(), 'protocol_sha256': base.sha(path),
              'source_hashes': hashes, 'parent_execution_sha256': spec['parent_execution_sha256'],
              'prior_execution_hashes': spec['prior_executions'],
              'previous_wall_s': prior_wall, 'previous_cpu_s': prior_cpu,
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'git_status_at_start': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True),
              'classification': spec['classification'], 'rss_gamma': .2,
              'formal_planning_calls': 0, 'random_draws': 0, 'native_author_RBS_executed': False,
              'full_RSS_or_planning_pass': False,
              'collision_qualification_scope': spec['collision_qualification_scope'],
              'claims_not_established': spec['claims_not_established']}
    exit_code = 0
    try:
        evidence.event('run_started', protocol=spec, source_hashes=hashes)
        results = run_all(spec, evidence, counts)
        record['status'] = 'LOCAL_BRIDGE_QUALIFICATION_RECORDED'
    except BaseException as exc:
        record.update(status='STOP_RETAINED_PREFIX', error=repr(exc)); exit_code = 2
        evidence.event('run_stopped', error=repr(exc))
    finally:
        budget.close()
        wall = time.monotonic()-budget.started; cpu = budget.cpu()-budget.cpu_start
        record.update(counts=dict(counts), wall_s=wall, cpu_s=cpu, ended_at_utc=base.utc(),
                      fixture_results=results, cumulative_execution_wall_s=prior_wall+wall,
                      cumulative_execution_cpu_s=prior_cpu+cpu,
                      local_bridge_coverage_gate_passed=len(results) == 2 and all(r['local_wrist_bridge_qualified'] for r in results))
        retained = Counter()
        for output in out.glob('ik_*.jsonl'):
            for line in output.read_text().splitlines():
                try: retained[json.loads(line)['op']] += 1
                except (ValueError, KeyError): retained['INCOMPLETE_JSON_ROW'] += 1
        record['retained_native_output_rows'] = dict(retained)
        record['authorization_budget_remaining'] = {
            'candidate_constructions': max(0, parent_remaining['candidate_constructions']-counts['candidate_constructions']),
            'wall_s': max(0., parent_remaining['wall_s']-wall),
            'cpu_s': max(0., parent_remaining['cpu_s']-cpu),
            'r2_total_wall_s': max(0., 3600.-prior_wall-wall),
            'r2_total_cpu_s': max(0., 7200.-prior_cpu-cpu),
            'policy': 'Retained prefix, no repeat execution; any evidenced continuation needs a distinct frozen reviewed protocol charging this remaining budget.'}
        record['coverage_gate_status'] = 'PASS_LOCAL_DISCRETE_ONLY' if record['local_bridge_coverage_gate_passed'] else 'UNKNOWN_OR_FAILED'
        base.new_json(out/'execution.json', record)
        evidence.events.close()
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
