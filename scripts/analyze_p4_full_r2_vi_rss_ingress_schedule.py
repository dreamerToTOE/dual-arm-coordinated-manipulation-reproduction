#!/usr/bin/env python3
"""Pure saved-data cost/schedule analysis, with zero new model calls.

Only JSON, hashes, scalar/vector arithmetic and report serialization are used.
Schedules contain node references and active interpolation parameters, not new
qualified robot configurations. This script is not an experiment runner.
"""
from __future__ import annotations
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import resource
import time

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT/'results/p4_full/20261015_R2_VI_RSS_BRIDGE01/execution.json'
EVENTS = BRIDGE.with_name('events.jsonl')
CENTER = ROOT/'results/p4_full/20261015_R2_VI_RSS_CENTER_IMAGE01/execution.json'
FIBER = ROOT/'results/p4_full/20261015_R2_VI_RSS_FIBER_COMPONENT01/execution.json'
OUT = ROOT/'reports/P4_FULL_R2_VI_RSS_INGRESS_COST_AND_FIXED_SCHEDULE_20261015.json'
H = .0025


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cpu():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime+r.ru_stime


def leaves(node):
    if 'left' not in node:
        return [node]
    return leaves(node['left'])+leaves(node['right'])


def fraction(value):
    return {'exact': str(value), 'numerator': value.numerator,
            'denominator': value.denominator, 'float': float(value)}


def main():
    started, c0 = time.monotonic(), cpu()
    bridge = json.loads(BRIDGE.read_text())
    diagnostic = json.loads(CENTER.read_text())
    fiber_run = json.loads(FIBER.read_text())
    assert fiber_run['component_coverage_gate_passed'] is True
    assert fiber_run['coverage_gate_status'] == 'PASS_COMPONENT_DISCRETE_ONLY'
    assert fiber_run['authorization_budget_remaining']['candidate_constructions'] == 50
    fiber_endpoints = {(r['fixed_spec']['parent_construction'], r['fixed_spec']['half']): r
        for r in fiber_run['candidate_results'] if r['fixed_spec']['kind'] == 'ENDPOINT'}
    assert len(fiber_endpoints) == 4 and all(r['qualified'] for r in fiber_run['candidate_results'])
    events = [json.loads(line) for line in EVENTS.read_text().splitlines()]
    centers = {e['parent_construction']: e['q_rad'] for e in events
               if e['event'] == 'saved_center_reused_without_scientific_recalculation'}
    ds = {(f['parent_construction'], h['half']): h
          for f in diagnostic['fixed_center_results'] for h in f['halves']}
    qualified = [e for e in events if e['event'] == 'construction_finished']
    assert len(qualified) == 36 and all(e['qualified'] for e in qualified)
    old_nodes, all_nodes = set(), {tuple(e['q_rad']) for e in qualified}
    rows, halves, binary, fibers = [], [], [], []
    for f in bridge['fixture_results']:
        parent, arm = f['parent_construction'], f['designated_passive_arm']
        original = centers[parent]
        old_nodes.add(tuple(original)); all_nodes.add(tuple(original))
        for half in f['half_results']:
            label = half['half']; negative = label.startswith('negative')
            prefix = f'f{parent}_'+('negative' if negative else 'positive')
            theta = ds[(parent, label)]['hypothetical_regular_branch_fiber_limit_q4_offset_rad']
            fiber_id = prefix+'_fiber_endpoint'
            fiber_count = 2 if parent == 219 else 1
            fibers.append({'parent_construction': parent, 'half': label, 'theta_rad': theta,
                'fixed_fiber_candidate_fractions': [.5, 1.] if parent == 219 else [1.],
                'new_fiber_candidates': fiber_count,
                'center_to_fiber_coordinate_distance_rad': math.sqrt(2)*abs(theta),
                'fiber_component_already_qualified': True,
                'saved_fiber_endpoint_candidate': fiber_endpoints[(parent, label)]['candidate'],
                'regular_ingress_not_established': True})
            half_rows = []
            saved_leaves = leaves(half['tree'])
            assert len(saved_leaves) == 8
            for index, node in enumerate(saved_leaves):
                k = 7-index if negative else index
                a, b = node['endpoint_a_q_rad'], node['endpoint_b_q_rad']
                old_nodes.update((tuple(a), tuple(b)))
                all_nodes.update((tuple(a), tuple(b)))
                d = math.dist(a, b)
                if abs(d-node['distance_full18_rad']) > 1e-16:
                    raise ValueError('Saved leaf distance disagreement')
                touches = a == original or b == original
                reanchored = d
                if touches:
                    regular = b if a == original else a
                    q4, q6 = 6*(arm-1)+3, 6*(arm-1)+5
                    # Hypothetical distance only; do not build a new q candidate.
                    cross = (regular[q4]-original[q4])-(regular[q6]-original[q6])
                    reanchored = math.sqrt(d*d-2*theta*cross+2*theta*theta)
                    actual_saved_distance = math.dist(regular, fiber_endpoints[(parent, label)]['q18_rad'])
                    assert abs(reanchored-actual_saved_distance) < 1e-14
                    reanchored = actual_saved_distance
                depth = 2 if parent == 219 else 1
                ideal_children = 2**depth
                assert reanchored/ideal_children < H
                lower = fiber_id if k == 0 else prefix+f'_saved_k{k}'
                upper = prefix+f'_saved_k{k+1}'
                lo, hi = Fraction(k, 8), Fraction(k+1, 8)
                mid = (lo+hi)/2
                mid_id = prefix+f'_k{k:02d}_M'
                common = {'parent_construction': parent, 'half': label,
                    'saved_leaf_node_id': node['node_id'], 'leaf_center_outward_index': k,
                    'designated_regular_branch': half['designated_branch'], 'other_passive_branch': 3}
                binary.append({**common, 'new_node_id': mid_id,
                    'left_endpoint_ref': lower, 'right_endpoint_ref': upper,
                    'active_center_to_outer_lambda': fraction(mid),
                    'raw_full18_reference_rule': 'Arithmetic midpoint of referenced qualified endpoints; retain its active first6 exactly.'})
                if depth == 2:
                    for suffix, left, right, lam in (
                        ('ML', lower, mid_id, (lo+mid)/2),
                        ('MR', mid_id, upper, (mid+hi)/2)):
                        binary.append({**common, 'new_node_id': prefix+f'_k{k:02d}_'+suffix,
                            'left_endpoint_ref': left, 'right_endpoint_ref': right,
                            'active_center_to_outer_lambda': fraction(lam),
                            'raw_full18_reference_rule': 'Arithmetic midpoint of referenced qualified endpoints; retain its active first6 exactly.'})
                row = {**common, 'touches_original_center': touches,
                    'original_distance_rad': d, 'stored_distance_rad': node['distance_full18_rad'],
                    'saved_matching_fiber_reanchored_distance_rad': reanchored,
                    'additional_binary_depth': depth, 'fixed_binary_new_midpoints': ideal_children-1,
                    'binary_equal_partition_surrogate_max_leaf_rad': reanchored/ideal_children,
                    'distance_only_minimum_new_nodes': math.floor(reanchored/H),
                    'surrogates_are_not_bounds_on_unevaluated_projected_nodes': True,
                    'lower_endpoint_ref': lower, 'upper_endpoint_ref': upper,
                    'center_outward_lambda_interval': [fraction(lo), fraction(hi)]}
                rows.append(row); half_rows.append(row)
            halves.append({'parent_construction': parent, 'half': label,
                'designated_arm': arm, 'exact_theta_rad': theta,
                'saved_regular_nodes_reused': 8, 'saved_original_center_reused': True,
                'fixed_binary_new_midpoints': sum(r['fixed_binary_new_midpoints'] for r in half_rows),
                'noncenter_fixed_binary_new_midpoints': sum(r['fixed_binary_new_midpoints'] for r in half_rows if not r['touches_original_center']),
                'center_ingress_fixed_binary_new_midpoints': sum(r['fixed_binary_new_midpoints'] for r in half_rows if r['touches_original_center']),
                'maximum_binary_equal_partition_surrogate_rad': max(r['binary_equal_partition_surrogate_max_leaf_rad'] for r in half_rows),
                'candidate_fiber_endpoint_already_qualified': True})
    # Stable center-out order; M precedes its ML/MR dependency within each leaf.
    order = lambda x: (x['parent_construction'], x['half'].startswith('center_'), x['leaf_center_outward_index'])
    rows.sort(key=order); binary.sort(key=order)
    assert len(binary) == 64
    assert len(old_nodes) == 34 and len(all_nodes) == 38
    expected_rate_wall = bridge['wall_s']/36
    expected_rate_cpu = bridge['cpu_s']/36
    result = {'schema': 'P4_R2_VI_RSS_SAVED_INGRESS_COST_AND_FIXED_SCHEDULE_V1',
        'classification': 'SAVED-DATA-ONLY / UNFROZEN DESIGN / NOT AN EXECUTABLE PROTOCOL',
        'source_sha256': sha(__file__),
        'input_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (BRIDGE, EVENTS, CENTER, FIBER)},
        'new_candidate_FK_IK_collision_sampling_planning_calls': 0,
        'original_Q2_unknown_unchanged': True, 'rss_gamma': .2, 'delta_rad': .01,
        'leaf_full18_raw_unwrapped_distance_gate_rad': H,
        'actual_fiber_component': {'source_commit': fiber_run['source_commit'],
            'status': fiber_run['coverage_gate_status'], 'qualified_candidates': 6,
            'wall_s': fiber_run['wall_s'], 'cpu_s': fiber_run['cpu_s'],
            'counts': fiber_run['counts'],
            'actual_remaining_budget': fiber_run['authorization_budget_remaining'],
            'scope': 'The6 singular-fiber discrete nodes are qualified and reusable; regular ingress remains UNKNOWN.'},
        'reuse': {'saved_chord_tree_unique_nodes': 34, 'saved_regular_chord_nodes': 32,
            'saved_original_centers': 2, 'saved_extra_curve_nodes_not_on_straight_active_chord': 4,
            'all_saved_unique_nodes_before_fiber': 38, 'additional_qualified_fiber_nodes': 6,
            'chord_tree_plus_fiber_unique_nodes': 40,
            'rule': 'Reuse saved full18 coordinates and qualification only under unchanged model, gates, branches and source-policy hashes. No old science rerun. The4 curve-only points cannot silently become straight-chord RBS nodes.'},
        'fibers': fibers, 'halves': halves, 'saved_leaves': rows,
        'fixed_arithmetic_midpoint_schedule': binary,
        'candidate_costs': {'noncenter_binary': 56, 'center_fiber_ingress_binary': 8,
            'total_regular_binary_after_fiber': 64, 'separate_fiber': 6,
            'combined_binary_plus_already_run_fiber': 70, 'actual_remaining_after_fiber': 50,
            'binary_schedule_shortfall': 14,
            'distance_only_new_node_lower_bound': sum(r['distance_only_minimum_new_nodes'] for r in rows),
            'lower_bound_scope': 'The distance-only48-node lower bound is not an arithmetic-midpoint schedule, not a PASS guarantee, and not an authorized substitute chosen to fit50. No trisection alternative is proposed for execution.'},
        'binary_additional_budget_request_design_only': {'additional_candidate_constructions': 14,
            'proposed_overall_candidate_cap': 974, 'regular_stage_cap': 64,
            'proposed_regular_stage_wall_cap_s': 30., 'proposed_regular_stage_cpu_cap_s': 60.,
            'extension_of_original_wall_or_cpu_cap_requested': False,
            'estimated_wall_s_from_Q2_rate': 64*expected_rate_wall,
            'estimated_cpu_s_from_Q2_rate': 64*expected_rate_cpu,
            'estimate_is_not_a_runtime_or_scientific_guarantee': True,
            'execution_requires': 'Explicit approval of14 added candidates and scientific review/freeze. Bind actual fiber execution remaining in protocol. No automatic960-cap bypass; no formal planner.'},
        'regular_node_call_accounting_design': {'IK_branch_requests_per_new_regular_node': 16,
            'native_F_operation_per_node': 1, 'mathematical_target_pose_arm_FK_J_per_node': 1,
            'accepted_root_roundtrip_arm_FK_J_per_node': 'A, actual native accepted-root count in0..16; Q2 observed A=4 per candidate.',
            'body_pose_arm_FK_J_per_node': 3, 'physical_constraint_arm_FK_J_per_node': 3,
            'collision_adapter_pose_arm_FK_J_per_qualified_collision_dispatch': 3,
            'arm_FK_J_per_fully_checked_node': '10+A;14 at the previously observed A=4, worst case26 if all16 roots accepted.',
            'binary64_IK_requests': 1024, 'binary64_native_F_operations': 64,
            'binary64_arm_FK_J_at_observed_A4': 896, 'binary64_arm_FK_J_upper_A16': 1664,
            'native_collision_queries_cap': 64,
            'interruption': 'Requested versus confirmed completed model/query calls must be distinct; failed prefixes remain charged and unresolved calls marked.'},
        'scientific_limits': ['No guarantee that projected child distances equal the equal-partition surrogate; every new actual edge must pass strict h.',
            'No regular-to-fiber endpoint or continuous lift has been qualified by saved distances or exact first-order theta.',
            'No statement of global impossibility within50; only the declared complete arithmetic-midpoint schedule requires64 slots.',
            'Any failed point/edge is retained UNKNOWN or failed; do not retry, change delta/h/branches/fixtures or spend beyond the approved cap.',
            'Source-policy discrete collision only; omitted pairs/full geometry/continuous CCD remain unqualified.',
            'This is an independent3-arm RECONSTRUCTED connector with explicit fiber anchors, not the incomplete author-native VI singular RBS or a full RSS planner.']}
    result['analysis_ledger'] = {'wall_s': time.monotonic()-started, 'cpu_s': cpu()-c0,
        'scope': 'Saved-file reads, hashes, scalar/vector arithmetic and report-data assembly only; excludes interpreter startup and final serialization.',
        'new_scientific_calls': 0}
    if OUT.exists():
        raise FileExistsError('No overwrite: '+str(OUT))
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'output': str(OUT), 'source_sha256': result['source_sha256'],
        'candidate_costs': result['candidate_costs'], 'halves': halves,
        'analysis_ledger': result['analysis_ledger']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
