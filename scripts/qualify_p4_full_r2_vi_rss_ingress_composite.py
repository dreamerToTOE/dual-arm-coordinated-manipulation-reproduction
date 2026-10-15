#!/usr/bin/env python3
"""Unapproved64-node fixed arithmetic-midpoint/fiber composite draft.

Describe/validate modes read saved files and do arithmetic only. Execution
requires explicit additional14-candidate AND composite-design approval, a
committed frozen protocol and a new retained one-shot claim. No planner runs.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_p4_full_r2_vi_rss_bridge as bridge
base, ROOT, np = bridge.base, bridge.ROOT, bridge.np
SCHEMA = 'P4_R2_VI_RSS_INGRESS_COMPOSITE_QUALIFICATION_V1'
ID = base.BUDGET_ID+'.INGRESS_COMPOSITE_974_V1'
Q2 = ROOT/'results/p4_full/20261015_R2_VI_RSS_BRIDGE01'
FIBER = ROOT/'results/p4_full/20261015_R2_VI_RSS_FIBER_COMPONENT01'
ANALYSIS = ROOT/'reports/P4_FULL_R2_VI_RSS_INGRESS_COST_AND_FIXED_SCHEDULE_20261015'
H = .0025


def saved_arrays_and_schedule():
    """Freeze40 existing q18 arrays and64 known active6 midpoint arrays only."""
    q2 = json.loads((Q2/'execution.json').read_text())
    fiber = json.loads((FIBER/'execution.json').read_text())
    cost = json.loads(ANALYSIS.with_suffix('.json').read_text())
    q2_finished = [json.loads(line) for line in (Q2/'events.jsonl').read_text().splitlines()
        if json.loads(line).get('event') == 'construction_finished']
    if len(q2_finished) != 36 or not all(r['qualified'] and r['source_policy_collision_qualified']
            and r['all_three_source_bounds_legal'] for r in q2_finished):
        raise base.StopQualification('OLD36_Q2_NODE_QUALIFICATION_NOT_PRESERVED')
    if not fiber['component_coverage_gate_passed'] or fiber['coverage_gate_status'] != 'PASS_COMPONENT_DISCRETE_ONLY':
        raise base.StopQualification('SAVED_FIBER_COMPONENT_NOT_QUALIFIED')
    centers = {f['construction']: f for f in bridge.fixtures_from_saved()}
    registry, active, schedule, final_edges, fiber_edges = {}, {}, [], [], []
    def add(ref, q, kind, source, **details):
        if ref in registry and registry[ref]['q18_rad'] != q:
            raise base.StopQualification('SAVED_ARRAY_REFERENCE_CONFLICT')
        registry[ref] = {'q18_rad': q, 'kind': kind, 'source': source, **details}
        active[ref] = np.array(q[:6])
    for parent, fixture in centers.items():
        add(f'f{parent}_original_center', fixture['q_rad'], 'SAVED_ORIGINAL_SINGULAR_CENTER',
            'B construction_finished', parent_construction=parent,
            parent_event_line_sha256=fixture['parent_event_line_sha256'])
    for row in fiber['candidate_results']:
        if not row['qualified']:
            raise base.StopQualification('SAVED_FIBER_NODE_NOT_QUALIFIED')
        item = row['fixed_spec']; parent = item['parent_construction']
        prefix = f'f{parent}_'+('negative' if item['half'].startswith('negative') else 'positive')
        suffix = '_fiber_endpoint' if item['kind'] == 'ENDPOINT' else '_fiber_midpoint'
        add(prefix+suffix, row['q18_rad'], 'SAVED_QUALIFIED_SINGULAR_FIBER',
            str((FIBER/'execution.json').relative_to(ROOT)),
            saved_candidate=row['candidate'], fixed_spec=item)
    def leaves(node):
        return leaves(node['left'])+leaves(node['right']) if 'left' in node else [node]
    for f in q2['fixture_results']:
        parent = f['parent_construction']
        for half in f['half_results']:
            negative = half['half'].startswith('negative')
            prefix = f'f{parent}_'+('negative' if negative else 'positive')
            for index, leaf in enumerate(leaves(half['tree'])):
                k = 7-index if negative else index
                qa, qb = leaf['endpoint_a_q_rad'], leaf['endpoint_b_q_rad']
                lower, upper = (qb, qa) if negative else (qa, qb)
                if k:
                    add(prefix+f'_saved_k{k}', lower, 'SAVED_QUALIFIED_REGULAR_Q2_NODE',
                        str((Q2/'execution.json').relative_to(ROOT)), original_leaf_node_id=leaf['node_id'])
                add(prefix+f'_saved_k{k+1}', upper, 'SAVED_QUALIFIED_REGULAR_Q2_NODE',
                    str((Q2/'execution.json').relative_to(ROOT)), original_leaf_node_id=leaf['node_id'])
            fiber_refs = [f'f{parent}_original_center']
            if parent == 219:
                fiber_refs.append(prefix+'_fiber_midpoint')
            fiber_refs.append(prefix+'_fiber_endpoint')
            for a, b in zip(fiber_refs, fiber_refs[1:]):
                distance = float(np.linalg.norm(np.array(registry[a]['q18_rad'])-registry[b]['q18_rad']))
                if not distance < H:
                    raise base.StopQualification('SAVED_FIBER_EDGE_NOT_STRICT')
                fiber_edges.append({'parent_construction': parent, 'half': half['half'],
                    'a_ref': a, 'b_ref': b, 'saved_full18_distance_rad': distance,
                    'reused_without_scientific_recalculation': True})
    for item in cost['fixed_arithmetic_midpoint_schedule']:
        a, b, ref = item['left_endpoint_ref'], item['right_endpoint_ref'], item['new_node_id']
        if a not in active or b not in active or ref in active:
            raise base.StopQualification('FIXED_SCHEDULE_DEPENDENCY_INVALID')
        active[ref] = (active[a]+active[b])/2.
        schedule.append({**item, 'frozen_active6_midpoint_q_rad': active[ref].tolist()})
    for leaf in cost['saved_leaves']:
        parent, k = leaf['parent_construction'], leaf['leaf_center_outward_index']
        prefix = f'f{parent}_'+('negative' if leaf['half'].startswith('negative') else 'positive')
        refs = [leaf['lower_endpoint_ref']]
        if parent == 219:
            refs.extend(prefix+f'_k{k:02d}_'+s for s in ('ML', 'M', 'MR'))
        else:
            refs.append(prefix+f'_k{k:02d}_M')
        refs.append(leaf['upper_endpoint_ref'])
        for a, b in zip(refs, refs[1:]):
            final_edges.append({'parent_construction': parent, 'half': leaf['half'],
                'saved_leaf_node_id': leaf['saved_leaf_node_id'], 'a_ref': a, 'b_ref': b,
                'is_new_regular_to_fiber_ingress_leaf': k == 0 and a.endswith('_fiber_endpoint')})
    if (len(registry), len(schedule), len(final_edges), len(fiber_edges)) != (40, 64, 96, 6):
        raise base.StopQualification('FIXED_ARRAY_SCHEDULE_CARDINALITY')
    return registry, schedule, final_edges, fiber_edges


def draft_protocol():
    fiber = json.loads((FIBER/'execution.json').read_text())
    parent = json.loads((ROOT/'configs/p4_full/r2_vi_rss_bridge_qualification_v1.json').read_text())
    arrays, schedule, edges, fiber_edges = saved_arrays_and_schedule()
    inputs = [bridge.PARENT_EXECUTION, bridge.PARENT_EVENTS,
        Q2/'execution.json', Q2/'events.jsonl', FIBER/'execution.json', FIBER/'events.jsonl',
        ANALYSIS.with_suffix('.json'), ANALYSIS.with_suffix('.md'),
        ROOT/'scripts/analyze_p4_full_r2_vi_rss_ingress_schedule.py',
        ROOT/'results/p4_full'/(base.BUDGET_ID+'.FIBER_COMPONENT_V1.claim.json')]
    copied = ('ik_binary', 'ik_binary_sha256', 'collision_checker_command', 'collision_manifest',
        'collision_manifest_sha256', 'collision_controls_result', 'collision_controls_result_sha256',
        'collision_success_statuses', 'collision_qualification_scope')
    return {'schema': SCHEMA, 'frozen': False, 'run_id': '20261015_R2_VI_RSS_INGRESS_COMPOSITE01',
        'authorization_budget_id': base.BUDGET_ID, 'continuation_id': ID,
        'classification': 'RECONSTRUCTED / FIBER-COMPOSITE-DISCRETE-QUALIFICATION',
        'approval': {'additional14_candidates_approved': False, 'new_composite_design_approved': False,
            'approval_record': None, 'approval_record_sha256': None},
        'execution_scope': 'Requires explicit approval of14 added candidates AND the independent composite design. Draft creation/validation never authorizes execution.',
        'runner_source_sha256': base.sha(__file__), 'dependency_source_sha256': fiber['source_hashes'],
        'input_sha256': {str(p.relative_to(ROOT)): base.sha(p) for p in inputs},
        'prior_executions': {str(p.relative_to(ROOT)): base.sha(p) for p in sorted(
            (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json'))},
        'parent_actual_remaining': fiber['authorization_budget_remaining'],
        'candidate_ledger': {'original_cap': 960, 'already_consumed': 910,
            'original_remaining': 50, 'additional_requested': 14,
            'proposed_cap_after_explicit_approval': 974, 'this_stage_max': 64,
            'charge_rule': 'Charge first50 actual new candidates to original remaining; at most next14 to explicit extension. Never reset prior910.'},
        'budget': {'max_candidate_constructions': 64, 'wall_s': 30., 'cpu_s': 60.,
            'r2_total_wall_s': 3600., 'r2_total_cpu_s': 7200.},
        'cumulative_B_limits': {'wall_s': 180., 'cpu_s': 360., 'no_time_extension': True},
        'rss_gamma': .2, 'delta_rad': .01, 'leaf_full18_distance_rad': H,
        'gates': base.GATES, 'active_arm': 1, 'random_draws': 0, 'formal_planning_calls': 0,
        'saved_nodes': arrays, 'fixed_new_midpoints': schedule,
        'fixed_final_regular_edges': edges, 'saved_fiber_edges': fiber_edges,
        'midpoint_rule': bridge.STRICT['midpoint'], 'lift_rule': bridge.STRICT['lift_rule'],
        'source_RBS_differences': ['Original author VI singular RBS source is incomplete; no native execution equivalence claimed.',
            'Explicit same-pose singular fiber anchors and retained original-center fiber paths are new independent composite design.',
            'Use strict raw full18 h=.0025; no source .05 early return or7*.05 singular shortcut.',
            'Only2 fixed fixtures/4 designated wrist halves, not all RSS modes or a planner.'],
        'expected_new_regular_ranks': {'arm2': 6, 'arm3': 6, 'passive': 12, 'full': 12},
        'call_accounting': {'per_node_IK_branch_requests': 16, 'per_node_native_F_operation': 1,
            'exact_inprocess_arm_FK_J_counting': 'Temporary count-only forwarding wrappers for base and physical_nr arm_fk_jac bindings; identical original function/arguments/results. Starts/completions logged individually, no source edit or numerical change.',
            'per_fully_checked_node_arm_FK_J': 'target1+accepted-root-roundtrip A+body3+physical3+adapter3=10+A; A in0..16 recorded, not assumed4.',
            'adapter': 'Before collision dispatch request3 pose-consistency FK/J. An observed native result confirms1 query; an observed3-arm pose-consistency error list confirms3 FK/J starts/completions even if later gated. Failed dispatch leaves any unconfirmed requested prefix unresolved, never assumed completed.',
            'IK_requests_cap': 1024, 'native_F_operations_cap': 64,
            'inprocess_arm_FK_J_cap': 1472, 'adapter_internal_arm_FK_J_cap': 192,
            'total_arm_FK_J_cap': 1664, 'native_collision_queries_cap': 64},
        'old_tree_reuse_gate': 'All40 saved q18 nodes are retained exactly under unchanged original model/source/gates/branches/PQP hashes;4 extra +/-delta/2 explicit-curve nodes are not used. Original Q2 UNKNOWN stays unchanged.',
        'new_ingress_gate': 'All64 new regular nodes qualified by dual closure/source limits/unique fixed branches/6,6,12,12 body and independent physical ranks/actual source-PQP. All96 actual final regular edges AND6 saved fiber edges must have raw full18 norm strictly<h. The4 regular-to-fiber ingress leaves are reported separately; original centers remain in composite paths.',
        'failure_policy': 'One fixed schedule only. Retain every failure; stop whole run before descendants of a failed node, process/protocol/rank/branch soundness inconsistency, budget limit or missing dependency. No node replacement, adaptive subdivision, fixture/branch/delta/h change, retry or rerun. Non-PASS edge leaves composite UNKNOWN.',
        'claims_not_established': ['Old Q2 status improvement', 'Author-native RBS equivalence',
            'All singular modes', 'Global RSS/PCS/NR planning', 'Continuous lift/path or CCD certificate',
            'Full collision geometry or original TableI/II statistics'],
        **{key: parent[key] for key in copied},
        'one_shot_policy': 'Separate atomic retained INGRESS_COMPOSITE_974_V1 claim; original/B/Q2/CENTER/FIBER claims never modified. Any interrupted prefix consumes the approved budget and prevents repeat.'}


def validate(spec, path, execute=False):
    expected = draft_protocol()
    for key, value in expected.items():
        if key not in ('frozen', 'approval') and spec.get(key) != value:
            raise base.StopQualification('COMPOSITE_PROTOCOL_MISMATCH_'+key)
    if set(spec) != set(expected) or type(spec.get('frozen')) is not bool:
        raise base.StopQualification('COMPOSITE_PROTOCOL_FIELD_OR_FROZEN_TYPE')
    approval = spec.get('approval', {})
    if set(approval) != set(expected['approval']):
        raise base.StopQualification('COMPOSITE_APPROVAL_FIELD_SET')
    for key in ('additional14_candidates_approved', 'new_composite_design_approved'):
        if type(approval[key]) is not bool:
            raise base.StopQualification('COMPOSITE_APPROVAL_BOOL_TYPE')
    if execute:
        if not spec['frozen'] or not all(approval[k] is True for k in (
                'additional14_candidates_approved', 'new_composite_design_approved')):
            raise base.StopQualification('ADDITIONAL14_AND_COMPOSITE_NOT_EXPLICITLY_APPROVED')
        if not isinstance(approval['approval_record'], str) or not approval['approval_record_sha256']:
            raise base.StopQualification('APPROVAL_EVIDENCE_REQUIRED')
        approval_path = (ROOT/approval['approval_record']).resolve()
        if not approval_path.is_relative_to(ROOT) or base.sha(approval_path) != approval['approval_record_sha256']:
            raise base.StopQualification('APPROVAL_EVIDENCE_HASH_OR_PATH')
        authorization = json.loads(approval_path.read_text())
        if (authorization.get('continuation_id') != ID or authorization.get('explicit_user_approval') is not True
                or authorization.get('additional_candidate_cap') != 14
                or authorization.get('new_composite_design_approved') is not True
                or not authorization.get('user_approval_evidence')):
            raise base.StopQualification('APPROVAL_RECORD_SCOPE_INVALID')
    else:
        approval_path = None
    for relative, digest in spec['dependency_source_sha256'].items():
        if base.sha(ROOT/relative) != digest:
            raise base.StopQualification('PARENT_DEPENDENCY_CHANGED_'+relative)
    for key in ('ik_binary', 'collision_manifest', 'collision_controls_result'):
        if base.sha(ROOT/spec[key]) != spec[key+'_sha256']:
            raise base.StopQualification('BINARY_OR_COLLISION_DEPENDENCY_CHANGED_'+key)
    controls = json.loads((ROOT/spec['collision_controls_result']).read_text())
    if controls.get('passed') is not True or controls.get('status') != 'SOURCE_POLICY_QUALIFIED':
        raise base.StopQualification('COLLISION_CONTROLS_NOT_QUALIFIED')
    remaining = spec['parent_actual_remaining']
    if remaining['candidate_constructions'] != 50 or min(remaining['wall_s'], remaining['cpu_s']) <= 0:
        raise base.StopQualification('PARENT_REMAINING_NOT_EXPECTED')
    sources = [Path(__file__).resolve(), path, *[ROOT/p for p in spec['dependency_source_sha256']]]
    if approval_path:
        sources.append(approval_path)
    if execute:
        for source in [*sources, *[ROOT/p for p in spec['input_sha256']]]:
            relative = str(source.relative_to(ROOT))
            subprocess.run(['git', 'ls-files', '--error-unmatch', relative], cwd=ROOT, check=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if subprocess.check_output(['git', 'status', '--porcelain', '--', relative], cwd=ROOT, text=True):
                raise base.StopQualification('SOURCE_PROTOCOL_INPUT_NOT_COMMITTED_'+relative)
    return {str(p.relative_to(ROOT)): base.sha(p) for p in sources}


@contextmanager
def count_inprocess_fk(evidence, counts):
    """Count-only wrappers; restore both module bindings even on interruption."""
    base_globals = base.__dict__
    physical_globals = base.closure_vector_jacobian.__globals__
    original, physical_original = base_globals['arm_fk_jac'], physical_globals['arm_fk_jac']
    if original is not physical_original:
        raise base.StopQualification('FK_COUNTER_BINDINGS_NOT_SAME_ORIGINAL')
    def forward(q, env, arm):
        evidence.budget.remaining()
        caller = sys._getframe(1).f_code.co_name
        phase = {'midpoint': 'active_target', 'all_roots': 'accepted_root_roundtrip',
            'poses_and_body': 'body_pose', '<genexpr>': 'physical_constraint'}.get(caller)
        if phase is None or env != 'VI' or arm not in (1, 2, 3):
            raise base.StopQualification('UNEXPECTED_COUNTED_FK_CONTEXT_'+caller)
        if counts['mathematical_arm_FK_J_started'] >= 1472:
            raise base.StopQualification('INPROCESS_FK_J_HARD_CAP')
        counts['mathematical_arm_FK_J_started'] += 1
        counts[phase+'_arm_FK_J_started'] += 1
        evidence.event('arm_FK_J_started', phase=phase, arm=arm, q6_rad=np.asarray(q).tolist())
        value = original(q, env, arm)
        counts['mathematical_arm_FK_J_completed'] += 1
        counts[phase+'_arm_FK_J_completed'] += 1
        evidence.event('arm_FK_J_completed', phase=phase, arm=arm,
            pose=value[0].tolist(), world_geometric_J=value[1].tolist())
        return value
    base_globals['arm_fk_jac'] = forward
    physical_globals['arm_fk_jac'] = forward
    try:
        yield
    finally:
        base_globals['arm_fk_jac'] = original
        physical_globals['arm_fk_jac'] = physical_original


class IngressRun(bridge.BridgeRun):
    def begin(self, kind, fixture, **details):
        number = super().begin(kind, fixture, **details)
        self.evidence.event('composite_candidate_budget_charge', candidate=number,
            source='ORIGINAL_REMAINING50' if number <= 50 else 'EXPLICIT_EXTENSION14')
        return number


class CountedEvidence:
    """Observe existing collision_result events without changing their result."""
    def __init__(self, evidence, counts):
        self.underlying, self.counts = evidence, counts
        self.folder, self.budget = evidence.folder, evidence.budget
    def event(self, kind, **values):
        if kind == 'collision_result':
            r = values['result']
            variant = r.get('variants', {}).get('native', {})
            pc = variant.get('pose_consistency', {})
            if len(pc.get('errors', [])) == 3:
                self.counts['adapter_internal_arm_FK_J_started'] += 3
                self.counts['adapter_internal_arm_FK_J_completed'] += 3
            if variant.get('native_result') in (0, 1):
                self.counts['native_collision_queries_confirmed'] += 1
        self.underlying.event(kind, **values)
    def process(self, command, input_text, label, environment=None):
        if label.startswith('collision_'):
            if self.counts['native_collision_queries_dispatched'] >= 64:
                raise base.StopQualification('NATIVE_COLLISION_QUERY_HARD_CAP')
            self.counts['adapter_internal_arm_FK_J_requested'] += 3
            self.counts['native_collision_queries_dispatched'] += 1
        return self.underlying.process(command, input_text, label, environment)


def run_fixed(spec, evidence, counts, results):
    fixtures = {f['construction']: f for f in bridge.fixtures_from_saved()}
    available = {ref: np.array(row['q18_rad']) for ref, row in spec['saved_nodes'].items()}
    qualified = {ref: True for ref in available}
    observer = CountedEvidence(evidence, counts)
    runner = IngressRun(spec, observer, counts, base.model_geometry('VI')['grasps'])
    evidence.event('saved40_nodes_reused_without_model_calls', saved_nodes=spec['saved_nodes'])
    with count_inprocess_fk(evidence, counts):
        for item in spec['fixed_new_midpoints']:
            evidence.budget.remaining()
            a, b, ref = item['left_endpoint_ref'], item['right_endpoint_ref'], item['new_node_id']
            if a not in available or b not in available or ref in available or not qualified[a] or not qualified[b]:
                raise base.StopQualification('MISSING_OR_FAILED_FIXED_MIDPOINT_DEPENDENCY')
            actual_active = (available[a][:6]+available[b][:6])/2.
            if not np.array_equal(actual_active, item['frozen_active6_midpoint_q_rad']):
                raise base.StopQualification('FIXED_ACTIVE_MIDPOINT_ARRAY_CHANGED')
            evidence.event('fixed_composite_midpoint_started', fixed_spec=item)
            result = runner.midpoint(fixtures[item['parent_construction']], available[a], available[b],
                item['designated_regular_branch'], ref)
            result.update(fixed_spec=item)
            results.append(result)
            if not result['qualified']:
                raise base.StopQualification('FIXED_MIDPOINT_NOT_QUALIFIED_NO_RETRY_'+ref)
            available[ref] = np.array(result['q_rad']); qualified[ref] = True
            if not np.array_equal(available[ref][:6], item['frozen_active6_midpoint_q_rad']):
                raise base.StopQualification('PROJECTED_ACTIVE_ARRAY_CHANGED')
            if counts['candidate_constructions'] > 64:
                raise base.StopQualification('FIXED64_CAP')
    edges = []
    for item in spec['fixed_final_regular_edges']:
        a, b = item['a_ref'], item['b_ref']
        distance = float(np.linalg.norm(available[a]-available[b]))
        row = {**item, 'actual_raw_full18_distance_rad': distance, 'strict_distance_passed': distance < H,
            'both_nodes_qualified': qualified[a] and qualified[b], 'continuous_collision_certificate': False}
        edges.append(row); evidence.event('composite_regular_edge_finished', **row)
    return edges


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
            'approval': spec['approval'], 'new_scientific_calls': 0, 'source_hashes': hashes,
            'counts': {'saved_nodes': 40, 'fixed_new_midpoints': 64, 'new_regular_edges': 96,
                'saved_fiber_edges': 6}}, indent=2)); return 0
    prior = [json.loads((ROOT/p).read_text()) for p in spec['prior_executions']]
    prior_wall, prior_cpu = sum(r['wall_s'] for r in prior), sum(r['cpu_s'] for r in prior)
    remaining = spec['parent_actual_remaining']
    runtime = {**spec, 'budget': {**spec['budget'],
        'wall_s': min(spec['budget']['wall_s'], remaining['wall_s']),
        'cpu_s': min(spec['budget']['cpu_s'], remaining['cpu_s'])}}
    out = ROOT/'results/p4_full'/spec['run_id']
    if out.exists():
        raise base.StopQualification('OUTPUT_EXISTS_NO_OVERWRITE')
    base.new_json(ROOT/'results/p4_full'/(ID+'.claim.json'), {'continuation_id': ID,
        'created_at_utc': base.utc(), 'run_id': spec['run_id'], 'protocol_sha256': base.sha(path),
        'approval': spec['approval'], 'caps': runtime['budget'],
        'policy': 'Atomic retained claim; no retry/reset/repeat; charge interrupted prefix.'})
    out.mkdir(parents=True, exist_ok=False)
    budget = base.RunBudget(runtime, prior_wall, prior_cpu); evidence = base.Evidence(out, budget)
    counts = Counter({key: 0 for key in ('candidate_constructions',
        'mathematical_arm_FK_J_started', 'mathematical_arm_FK_J_completed',
        'adapter_internal_arm_FK_J_requested', 'adapter_internal_arm_FK_J_started',
        'adapter_internal_arm_FK_J_completed', 'native_collision_queries_dispatched',
        'native_collision_queries_confirmed')})
    results, edges = [], []
    record = {'schema': SCHEMA, 'run_id': spec['run_id'], 'continuation_id': ID,
        'authorization_budget_id': base.BUDGET_ID, 'classification': spec['classification'],
        'started_at_utc': base.utc(), 'protocol_sha256': base.sha(path), 'approval': spec['approval'],
        'source_hashes': hashes, 'input_sha256': spec['input_sha256'],
        'prior_execution_hashes': spec['prior_executions'],
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'original_Q2_unknown_unchanged': True, 'author_native_RBS_executed': False,
        'random_draws': 0, 'formal_planning_calls': 0, 'rss_gamma': .2,
        'full_RSS_or_planning_pass': False, 'continuous_collision_certificate': False,
        'collision_qualification_scope': spec['collision_qualification_scope']}
    code = 0
    try:
        evidence.event('run_started', protocol=spec, source_hashes=hashes)
        edges = run_fixed(spec, evidence, counts, results)
        record['status'] = 'FIXED_COMPOSITE_QUALIFICATION_RECORDED'
    except BaseException as exc:
        record.update(status='STOP_RETAINED_PREFIX', error=repr(exc)); code = 2
        evidence.event('run_stopped', error=repr(exc))
    finally:
        budget.close(); wall = time.monotonic()-budget.started; used_cpu = budget.cpu()-budget.cpu_start
        counts['adapter_internal_arm_FK_J_unresolved_requested'] = (
            counts['adapter_internal_arm_FK_J_requested']-counts['adapter_internal_arm_FK_J_completed'])
        counts['native_collision_queries_unresolved_dispatched'] = (
            counts['native_collision_queries_dispatched']-counts['native_collision_queries_confirmed'])
        counts['total_arm_FK_J_started_confirmed'] = (
            counts['mathematical_arm_FK_J_started']+counts['adapter_internal_arm_FK_J_started'])
        counts['total_arm_FK_J_completed_confirmed'] = (
            counts['mathematical_arm_FK_J_completed']+counts['adapter_internal_arm_FK_J_completed'])
        n = counts['candidate_constructions']; old_charge, extra_charge = min(n, 50), max(0, n-50)
        passed = (len(results) == 64 and all(r['qualified'] for r in results) and len(edges) == 96
            and all(e['strict_distance_passed'] and e['both_nodes_qualified'] for e in edges)
            and len(spec['saved_fiber_edges']) == 6)
        ingress = [e for e in edges if e['is_new_regular_to_fiber_ingress_leaf']]
        record.update(ended_at_utc=base.utc(), wall_s=wall, cpu_s=used_cpu, counts=dict(counts),
            candidate_results=results, regular_edge_results=edges, saved_fiber_edges=spec['saved_fiber_edges'],
            new_regular_to_fiber_ingress_leaf_results=ingress,
            all4_new_ingress_leaves_passed=len(ingress) == 4 and all(e['strict_distance_passed'] for e in ingress),
            composite_discrete_coverage_gate_passed=passed,
            coverage_gate_status='PASS_RECONSTRUCTED_COMPOSITE_DISCRETE_ONLY' if passed else 'UNKNOWN_OR_FAILED',
            original960_candidate_charge=old_charge, approved_extra14_candidate_charge=extra_charge,
            cumulative_execution_wall_s=prior_wall+wall, cumulative_execution_cpu_s=prior_cpu+used_cpu,
            authorization_budget_remaining={'candidate_constructions': max(0, 64-n),
                'original960_remaining': 50-old_charge, 'approved_extra14_remaining': 14-extra_charge,
                'wall_s': max(0., remaining['wall_s']-wall), 'cpu_s': max(0., remaining['cpu_s']-used_cpu),
                'r2_total_wall_s': max(0., 3600-prior_wall-wall),
                'r2_total_cpu_s': max(0., 7200-prior_cpu-used_cpu),
                'policy': 'Actual retained prefix charged once. No original-time-cap extension or automatic repeat.'})
        base.new_json(out/'execution.json', record); evidence.events.close()
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    main()
