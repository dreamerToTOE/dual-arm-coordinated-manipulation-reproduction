#!/usr/bin/env python3
"""Personnel-independent saved evidence audit. Python standard library only.

No subprocess, scientific import, model evaluation, solver, sampler, collision
query or compilation. Matrix operations below act only on already saved poses.
Reports are exclusive-created; original observations are read-only.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'results/p4_full/20261015_R2_ABB_NR_LOCAL01'
OUT = ROOT / 'reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_INDEPENDENT_POST_20261015'
CHECKS = []


def load(p):
    p = Path(p)
    return json.loads((p if p.is_absolute() else ROOT / p).read_text())


def digest(p):
    p = Path(p)
    return hashlib.sha256((p if p.is_absolute() else ROOT / p).read_bytes()).hexdigest()


def check(name, condition, **evidence):
    CHECKS.append(dict(check=name, passed=bool(condition), **evidence))


def same(name, actual, expected):
    check(name, actual == expected, actual=actual, expected=expected)


def near(name, a, b, tolerance):
    error = abs(a - b)
    check(name, math.isfinite(error) and error <= tolerance,
          absolute_error=error, tolerance=tolerance)


def qb(q):
    return struct.pack('>12d', *q).hex()


def qsame(name, a, b):
    same(name, qb(a), qb(b))


def distance(a, b):
    # Source sequential accumulation, with no periodic equivalence reduction.
    total = 0.0
    for x, y in zip(a, b):
        total += (x - y) ** 2
    return math.sqrt(total)


def prefixed(p, prefix):
    return [json.loads(s[len(prefix):]) for s in p.read_text().splitlines()
            if s.startswith(prefix)]


def logical(response):
    d = {k: response[k] for k in ('schema', 'environment', 'id', 'op', 'status',
         'returned', 'request', 'q12', 'path_q12', 'rng_calls', 'solve_calls') if k in response}
    d['request'] = dict(d['request'])
    for k in ('q12', 'qa12', 'qb12'):
        if k in d['request']:
            d['request'][k] = qb(d['request'][k])
    if 'q12' in d:
        d['q12'] = qb(d['q12'])
    if 'path_q12' in d:
        d['path_q12'] = [qb(q) for q in d['path_q12']]
    d['counters'] = {k: v for k, v in response['source_log_counters'].items() if 'time' not in k}
    return d


def tree_events(events, label):
    stack, roots, started, completed = [], [], Counter(), Counter()
    next_id = 1
    for event in events:
        name = label + '.event.' + str(event['id'])
        kind = event['kind']
        if event['event'] == 'entered':
            same(name + '.sequential_id', event['id'], next_id)
            next_id += 1
            node = {'entry': event, 'children': []}
            (stack[-1]['children'] if stack else roots).append(node)
            stack.append(node)
            started[kind] += 1
        else:
            check(name + '.completion_lifo', bool(stack) and event['event'] == 'completed'
                  and (event['id'], kind) == (stack[-1]['entry']['id'], stack[-1]['entry']['kind']))
            node = stack.pop()
            node['exit'] = event
            completed[kind] += 1
    same(label + '.unfinished_stack', len(stack), 0)
    same(label + '.single_top', len(roots), 1)
    same(label + '.started_completed', dict(started), dict(completed))
    return roots[0], completed


def replay(node, name, path=None, expected_args=None):
    entry, children, result = node['entry'], node['children'], node['exit']['result']
    kind, args = entry['kind'], entry['args']
    name += '.' + str(entry['id']) + '.' + kind
    if expected_args is not None:
        for key, value in expected_args.items():
            if key in ('qa12', 'qb12', 'q12', 'input_q12'):
                qsame(name + '.args.' + key, args[key], value)
            else:
                same(name + '.args.' + key, args[key], value)
    if kind == 'pqp':
        same(name + '.no_children', len(children), 0)
        same(name + '.return_code', result['code'], 0)
        same(name + '.tolerance', args['tolerance'], 8.0)
        return result['code']
    if kind == 'collision':
        check(name + '.only_pqp_children', all(c['entry']['kind'] == 'pqp' for c in children))
        for child in children:
            replay(child, name)
        same(name + '.original_collision_return', result['returned'], 0)
        return result['returned']
    if kind == 'nr_gd':
        same(name + '.no_children', len(children), 0)
        qsame(name + '.preserved_input', args['input_q12'], result['input_q12'])
        same(name + '.converged_return_semantics', result['returned'], result['status'] == 'CONVERGED')
        finite = isinstance(result['candidate_q12'], list) and len(result['candidate_q12']) == 12 and all(math.isfinite(x) for x in result['candidate_q12'])
        same(name + '.candidate_finite', result['candidate_is_finite'], finite)
        check(name + '.update_count', type(result['accepted_updates']) is int and result['accepted_updates'] >= 0)
        return result
    if kind in ('nr_project', 'nr_valid_midpoint'):
        check(name + '.gd_first', bool(children) and children[0]['entry']['kind'] == 'nr_gd')
        gd = replay(children[0], name, expected_args={'input_q12': args['q12']})
        expected_q = gd['candidate_q12'] if gd['returned'] else args['q12']
        qsame(name + '.result_q', result['q12'], expected_q)
        expected_return = bool(gd['returned'])
        if gd['returned']:
            same(name + '.collision_count', len(children), 2)
            collision = children[1]
            qsame(name + '.collision_candidate', collision['entry']['args']['q1'] + collision['entry']['args']['q2'], expected_q)
            expected_return = replay(collision, name) == 0
        else:
            same(name + '.no_collision_after_failed_gd', len(children), 1)
        same(name + '.source_return_replay', result['returned'], expected_return)
        return result
    if kind in ('nr_rbs', 'nr_reconstruct'):
        qa, qb_ = args['qa12'], args['qb12']
        d = distance(qa, qb_)
        depth = args['recursion_depth'] if kind == 'nr_rbs' else args['iteration'] + 1
        if d < .05:
            same(name + '.leaf_children', len(children), 0)
            expected_return = True
        elif depth > 150:
            same(name + '.depth_stop_children', len(children), 0)
            expected_return = False
        else:
            check(name + '.valid_midpoint_first', bool(children) and children[0]['entry']['kind'] == 'nr_valid_midpoint')
            midpoint = [(x + y) / 2 for x, y in zip(qa, qb_)]
            valid = replay(children[0], name, expected_args={'q12': midpoint})
            expected_return = bool(valid['returned'])
            if not expected_return:
                same(name + '.failed_midpoint_short_circuit', len(children), 1)
            else:
                mid = valid['q12']
                leftargs = {'qa12': qa, 'qb12': mid}
                rightargs = {'qa12': mid, 'qb12': qb_}
                if kind == 'nr_rbs':
                    leftargs.update(recursion_depth=depth + 1, non_decrease_count=args['non_decrease_count'])
                    rightargs.update(recursion_depth=depth + 1, non_decrease_count=args['non_decrease_count'])
                else:
                    last = args['last_index'] + (args['firstORsecond'] != 1)
                    path.insert(last, mid)
                    before = len(path)
                    leftargs.update(iteration=depth, last_index=last, firstORsecond=1)
                check(name + '.left_kind', len(children) >= 2 and children[1]['entry']['kind'] == kind)
                left = replay(children[1], name, path=path, expected_args=leftargs)
                if not left:
                    expected_return = False
                    same(name + '.failed_left_short_circuit', len(children), 2)
                else:
                    same(name + '.two_recursions', len(children), 3)
                    if kind == 'nr_reconstruct':
                        rightargs.update(iteration=depth, last_index=last + len(path) - before, firstORsecond=2)
                    check(name + '.right_kind', children[2]['entry']['kind'] == kind)
                    expected_return = replay(children[2], name, path=path, expected_args=rightargs)
        same(name + '.source_return_replay', result['returned'], expected_return)
        return expected_return
    raise ValueError('unrecognized trace kind ' + kind)


def audit():
    execution = load(RUN / 'execution.json')
    protocol = load(execution['protocol'])
    same('frozen', protocol['frozen'], True)
    check('all_reviews', all(v is True for v in protocol['reviews'].values()))
    same('protocol_hash', digest(execution['protocol']), execution['protocol_sha256'])
    same('protocol_hash_unchanged', execution['protocol_sha256'], execution['protocol_after_sha256'])
    same('claim_hash', digest(execution['claim']), execution['claim_sha256'])
    same('claim_hash_unchanged', execution['claim_sha256'], execution['claim_after_sha256'])
    same('bound_before_after', execution['bound_files_sha256'], execution['bound_files_after_sha256'])
    same('bound_count', len(execution['bound_files_sha256']), 1203)
    for name, wanted in execution['bound_files_sha256'].items():
        same('bound_hash.' + name, digest(name), wanted)
    same('node_queue_hash', digest(RUN / 'node_queue.json'), execution['node_queue_sha256'])
    same('status', execution['status'], 'FIXED_LOCAL_ABB_NR_QUALIFIED')
    same('source_commit', execution['source_commit'], '7ee551afea8dc8ae49d4427e69f36f32bd771da5')
    same('zero_new_scientific_calls_claim', execution['zero_calls'], {'solve': 0, 'RNG': 0, 'IK': 0, 'VI_constructions': 0, 'formal_table_I': 0})
    check('execution_budget', 0 < execution['wall_s'] < 60 and 0 < execution['cpu_s'] < 120)
    responses, trace_trees, raw_trace, raw_source = {}, {}, [], []
    aggregate = Counter()
    for i, batch in enumerate(protocol['schedule']):
        env, mode = batch['environment'], batch['mode']
        stem = f'{i+1:05d}_source_{i:02d}_{env}_{mode}'
        saved_input = [json.loads(s) for s in (RUN / (stem + '.input.txt')).read_text().splitlines()]
        same(stem + '.fixed_input', saved_input, batch['requests'])
        observed = prefixed(RUN / (stem + '.stdout.txt'), 'P4_NR_RESPONSE ')
        events = prefixed(RUN / (stem + '.stderr.txt'), 'P4_PCS_TRACE ')
        same(stem + '.complete_responses', len(observed), len(batch['requests']))
        chunks = []
        for event in events:
            if event['event'] == 'entered' and event['id'] == 1:
                chunks.append([])
            chunks[-1].append(event)
        same(stem + '.trace_chunks', len(chunks), len(observed) if mode == 'trace' else 0)
        raw_trace.extend(events)
        raw_source.extend(observed)
        for j, (request, response) in enumerate(zip(batch['requests'], observed)):
            label = env + '.' + mode + '.' + request['id']
            responses[(env, mode, request['id'])] = response
            same(label + '.raw_saved', response, load(RUN / f'source_{env}_{mode}_{request["id"]}.json'))
            same(label + '.fixed_request', response['request'], request)
            same(label + '.success_status', response['status'], 'SOURCE_CALL_COMPLETED')
            same(label + '.no_observer_errors', response['observer_errors'], [])
            same(label + '.zero_rng', response['rng_calls'], 0)
            same(label + '.zero_solve', response['solve_calls'], 0)
            same(label + '.bool', type(response['returned']).__name__, 'bool')
            if mode == 'plain':
                same(label + '.unobserved_internals', response['observed_counts'], {})
                same(label + '.unobserved_gd', response['gd_completed_candidates'], [])
                continue
            tree, counts = tree_events(chunks[j], label)
            trace_trees[(env, request['id'])] = tree
            aggregate.update(counts)
            same(label + '.observed_counts', dict(counts), response['observed_counts'])
            path = [request['qa12'], request['qb12']] if request['op'] == 'reconstruct' else None
            expected = ({'q12': request['q12'], 'includeObs': True} if request['op'] == 'project_q12'
                        else {'qa12': request['qa12'], 'qb12': request['qb12'], **(
                            {'recursion_depth': 0, 'non_decrease_count': 0} if request['op'] == 'rbs'
                            else {'iteration': 0, 'last_index': 1, 'firstORsecond': 1})})
            result = replay(tree, label, path=path, expected_args=expected)
            same(label + '.top_return_replay', result['returned'] if isinstance(result, dict) else result, response['returned'])
            if path is not None:
                same(label + '.reconstructed_path_binary64', [qb(q) for q in path], [qb(q) for q in response['path_q12']])
    same('raw_source_count', len(raw_source), 20)
    queue, key_to_node = [], {}
    def queue_add(env, q, ref, required):
        key = (env, qb(q))
        if key not in key_to_node:
            key_to_node[key] = len(queue)
            queue.append(dict(node_id=len(queue), environment=env, q12=q, refs=[], collision_required=False))
        node = queue[key_to_node[key]]
        node['refs'].append(ref)
        node['collision_required'] |= required
    pairs = load(RUN / 'source_pairs.json')
    for pair in pairs:
        env, request = pair['environment'], pair['request']
        ident = request['id']
        trace = responses[(env, 'trace', ident)]
        plain = responses[(env, 'plain', ident)]
        same(ident + '.plain_trace_binary64', logical(trace), logical(plain))
        same(ident + '.pair_raw_trace', pair['trace'], trace)
        same(ident + '.pair_raw_plain', pair['plain'], plain)
        gd_events = [v['result'] for v in pair['trace_observation']['events'] if v['event'] == 'completed' and v['kind'] == 'nr_gd']
        same(ident + '.all_gd_candidates', gd_events, trace['gd_completed_candidates'])
        for n, gd in enumerate(trace['gd_completed_candidates']):
            if gd['candidate_q12'] is not None:
                queue_add(env, gd['candidate_q12'], dict(case_id=ident, kind='gd', candidate_index=n, returned=gd['returned']), gd['returned'])
        if request['op'] == 'project_q12':
            queue_add(env, trace['q12'], dict(case_id=ident, kind='top_project', returned=trace['returned']), True)
        else:
            for k in ('qa12', 'qb12'):
                queue_add(env, request[k], dict(case_id=ident, kind=k), True)
            if request['op'] == 'reconstruct':
                for n, q in enumerate(trace['path_q12']):
                    queue_add(env, q, dict(case_id=ident, kind='path', path_index=n, returned=trace['returned']), True)
    same('full_queue_rebuilt_from_raw', queue, load(RUN / 'node_queue.json'))
    same('full_queue_size', len(queue), 147)
    node_responses = prefixed(RUN / '00005_independent_full_node_queue.stdout.txt', 'P4_NR_NODE_RESPONSE ')
    same('full_node_responses_count', len(node_responses), len(queue))
    maxima = Counter()
    native_mismatches = 0
    pqp_counts = Counter()
    bounds = [(a * 3.1416 / 180, b * 3.1416 / 180) for a, b in [(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)] * 2]
    for n, source in enumerate(queue):
        label = 'node.' + str(n)
        node = load(RUN / f'node_{n:05d}.json')
        same(label + '.worker_raw', node_responses[n]['result'], node)
        same(label + '.queue_binding', {k: node[k] for k in source}, source)
        same(label + '.stage', node['stage'], 'COMPLETED')
        for arm in (1, 2):
            part = load(RUN / f'node_{n:05d}_arm{arm}.json')
            same(label + f'.arm{arm}.saved_prefix', part['poses'], node['poses'][:arm])
        math_saved = load(RUN / f'node_{n:05d}_math.json')
        same(label + '.saved_math', {k: node[k] for k in math_saved if k != 'stage'}, {k: v for k, v in math_saved.items() if k != 'stage'})
        t1, t2 = node['poses']
        length = 300. if source['environment'] == 'II' else 500.
        pos_error = max(abs(t2[i][3] - (t1[i][3] + length * t1[i][0])) for i in range(3))
        rot_error = max(abs(t2[i][j] - t1[i][j] * (-1 if j < 2 else 1)) for i in range(3) for j in range(3))
        near(label + '.closure_saved_position', pos_error, node['closure']['position_max_abs'], 2e-12)
        near(label + '.closure_saved_rotation', rot_error, node['closure']['rotation_matrix_max_abs'], 1e-15)
        check(label + '.independent_saved_pose_closure_gate', pos_error <= 1e-5 and rot_error <= 1e-5)
        maxima['closure_position_mm'] = max(maxima['closure_position_mm'], pos_error)
        maxima['closure_rotation_matrix'] = max(maxima['closure_rotation_matrix'], rot_error)
        check(label + '.source_literal_joint_bounds', all(lo <= q <= hi for q, (lo, hi) in zip(node['q12'], bounds)))
        same(label + '.limits_report', node['limits'], dict(legal=True, violations=[], source_literal_pi_preserved=3.1416, planar_q19_policy=None))
        same(label + '.math_qualified', node['math_qualified'], True)
        collision = load(RUN / f'node_{n:05d}_collision_raw.json')
        same(label + '.collision_raw', node['collision'], collision)
        same(label + '.collision_selected', collision['selected_variant'], 'aligned')
        same(label + '.collision_status', collision['status'], 'CHECKED')
        same(label + '.collision_discrete_scope', collision['scope'], 'AUTHOR_DISCRETE_COLLISION_POLICY')
        same(label + '.no_continuous_claim', collision['continuous_collision_certificate'], False)
        same(label + '.collision_manifest_hash', digest(collision['manifest_path']), collision['manifest_sha256'])
        for variant, row in collision['variants'].items():
            raw = [json.loads(s[len('P4_COLLISION_RESULT '):]) for s in row['source_stdout'].splitlines() if s.startswith('P4_COLLISION_RESULT ')]
            same(label + '.' + variant + '.single_raw_result', len(raw), 1)
            same(label + '.' + variant + '.raw_values', raw[0], {k: row[k] for k in raw[0]})
            same(label + '.' + variant + '.pqp_call_count', len(row['query_codes']), 116 if source['environment'] == 'II' else 103)
            for j, code in enumerate(row['query_codes']):
                same(label + '.' + variant + '.pqp_code.' + str(j), code, 0)
            same(label + '.' + variant + '.collision_return', row['native_result'], 0)
            pqp_counts[variant] += len(row['query_codes'])
            errs = []
            for arm in (0, 1):
                pose = row['poses'][arm]
                pe = max(abs(pose[4*i+3] - node['poses'][arm][i][3]) for i in range(3))
                re = max(abs(pose[4*i+j] - node['poses'][arm][i][j]) for i in range(3) for j in range(3))
                near(label + f'.{variant}.arm{arm+1}.saved_pose_pos_error', pe, row['pose_consistency']['errors'][arm]['translation_maxabs_mm'], 1e-12)
                near(label + f'.{variant}.arm{arm+1}.saved_pose_rot_error', re, row['pose_consistency']['errors'][arm]['rotation_maxabs'], 1e-15)
                errs.append(pe <= 1e-5 and re <= 1e-5)
            same(label + '.' + variant + '.pose_gate_replay', all(errs), row['pose_consistency']['passed'])
            if variant == 'aligned':
                check(label + '.aligned_physical_pose_gate', all(errs))
            elif not all(errs):
                native_mismatches += 1
        same(label + '.collision_qualified', collision['collision'], False)
        same(label + '.node_qualified', node['node_qualified'], True)
    worker_events = prefixed(RUN / '00005_independent_full_node_queue.stderr.txt', 'P4_NR_NODE_EVENT ')
    wc = Counter(e['event'] for e in worker_events)
    expected_worker = {'math_arm_FK_started':294,'math_arm_FK_completed':294,'adapter_arm_FK_J_started':588,'adapter_arm_FK_J_completed':588,'collision_started':147,'collision_completed':147}
    same('worker_actual_event_counts', dict(wc), expected_worker)
    same('actual_native_pqp', pqp_counts['native'], 17026)
    same('actual_aligned_pqp', pqp_counts['aligned'], 17026)
    for kind, count in aggregate.items():
        same('execution_trace_actual_started.' + kind, execution['counts']['actual_trace_' + kind + '_started'], count)
        same('execution_trace_actual_completed.' + kind, execution['counts']['actual_trace_' + kind + '_completed'], count)
    for name, observed in [('actual_math_arm_FK_started',wc['math_arm_FK_started']),('actual_math_arm_FK_completed',wc['math_arm_FK_completed']),('actual_collision_started',wc['collision_started']),('actual_collision_completed',wc['collision_completed']),('actual_adapter_arm_FK_J_started',wc['adapter_arm_FK_J_started']),('actual_adapter_arm_FK_J_completed',wc['adapter_arm_FK_J_completed']),('actual_adapter_PQP_queries',sum(pqp_counts.values())),('actual_adapter_native_PQP_queries',pqp_counts['native']),('actual_adapter_aligned_PQP_queries',pqp_counts['aligned'])]:
        same('execution_counts.'+name, execution['counts'][name], observed)
    same('execution_complete_top_tail', execution['uncompleted_top_requests'], [])
    same('execution_complete_node_tail', execution['uncompleted_node_ids'], [])
    same('execution_complete_node_ids', execution['completed_node_ids'], list(range(147)))
    same('execution_complete_queue_flag', execution['full_node_queue_checked'], True)
    same('plain_internals_unobserved', execution['plain_internal_GD_FK_PQP'], 'UNOBSERVED')
    path_summaries=[]
    for edge in range(3):
        r = responses[('II', 'trace', f'II_edge_{edge}_reconstruct')]
        path = r['path_q12']
        leaves = [distance(x, y) for x, y in zip(path, path[1:])]
        check(f'edge.{edge}.nontrivial', distance(path[0], path[-1]) > .05 and len(path) > 2)
        for j, leaf in enumerate(leaves):
            check(f'edge.{edge}.leaf.{j}', leaf < .05, full12_L2_rad=leaf)
        for q in path:
            check(f'edge.{edge}.all_path_nodes_qualified.'+qb(q), (r['environment'],qb(q)) in key_to_node)
        path_summaries.append(dict(edge_index=edge,nodes=len(path),leaves=len(leaves),max_leaf_full12_L2_rad=max(leaves),source_rbs_returned=responses[('II','trace',f'II_edge_{edge}_rbs')]['returned'],source_reconstruct_returned=r['returned']))
    same('three_qualified_edges', execution['qualified_nontrivial_edges'], 3)
    same('next_planner_gate_supported', execution['next_planner_gate_supported'], True)
    same('next_planner_environment', execution['next_planner_environment'], 'II')
    same('independent_raw_prefix_source', load(RUN / 'raw_prefix_inventory.json')['source_responses'], raw_source)
    same('independent_raw_prefix_nodes', load(RUN / 'raw_prefix_inventory.json')['node_responses'], node_responses)
    same('independent_raw_prefix_worker', load(RUN / 'raw_prefix_inventory.json')['worker_events'], worker_events)
    return dict(trace_counts=dict(aggregate),worker_counts=dict(wc),adapter_pqp=dict(pqp_counts),native_pose_mismatch_count=native_mismatches,maxima=dict(maxima),paths=path_summaries,scientific_run_wall_s=execution['wall_s'],scientific_run_cpu_s=execution['cpu_s'])


if __name__ == '__main__':
    if OUT.with_suffix('.json').exists() or OUT.with_suffix('.md').exists():
        raise FileExistsError('Exclusive report path already exists; preserve prior report')
    summary = audit()
    failed = [c for c in CHECKS if not c['passed']]
    report = dict(schema='P4_NR_LOCAL_PERSONNEL_INDEPENDENT_STDLIB_SAVED_POST_V1',
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        run_id=RUN.name,reviewer='nr_local_independent_post (not runner author)',
        status='PASS_SAVED_EVIDENCE_AUDIT' if not failed else 'FAIL_SAVED_EVIDENCE_AUDIT',
        checks_total=len(CHECKS),checks_passed=len(CHECKS)-len(failed),checks_failed=len(failed),
        zero_new_scientific_calls=True,zero_compile_calls=True,
        script_sha256=digest(Path(__file__)),summary=summary,
        evidence_boundary=['Only stored binary64 joint arrays, TCP matrices, raw events and file bytes were examined.',
            'No FK/IK/NR/Jacobian/collision/model evaluation or binary execution; arithmetic closure uses stored poses.',
            'Native collision TCP inconsistency is retained; aligned variant is the qualified physical pose gate.',
            'Local original RBS/reconstruction with RECONSTRUCTED physical full NR replacement is qualified on fixed inputs only.',
            'Does not establish random ambient projection coverage, native KDL equivalence, global NR planner success, CCD or formal paper statistics.'],
        failed_checks=failed,checks=CHECKS)
    with OUT.with_suffix('.json').open('x') as f:
        json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    md = f'''# ABB NR 局部资格：独立保存证据复核

结果：**{report['status']}**。共 {len(CHECKS)} 项检查，{len(CHECKS)-len(failed)} 通过、{len(failed)} 失败。审计人员未编写本次 runner；只使用 Python 标准库读取保存证据，新增科学调用与编译均为 0。

20 项原调用响应完整；plain/trace 的源布尔值、完整 12 角 binary64、完整回溯路径和非计时计数逐项一致。独立重建事件树并重放原递归叶门、深度门、短路返回、投影后中点和回溯插入索引，没有再次运行 NR。所有 147 个唯一节点及其全部来源引用、数学保存阶段、native/aligned 原始碰撞响应和完整尾部均已复核；1203 项绑定文件哈希保持。

保存 TCP 矩阵算术重算的最大闭链位置残差为 {summary['maxima']['closure_position_mm']:.17g} mm，旋转矩阵最大绝对残差为 {summary['maxima']['closure_rotation_matrix']:.17g}。所有节点满足原 3.1416 限位。native TCP 的既有几何不一致有 {summary['native_pose_mismatch_count']} 个节点，原记录保留；aligned 物理 TCP 和离散碰撞门全部合格。adapter 两版本各保留 {summary['adapter_pqp']['native']} 次 PQP 查询代码。

| 边 | 完整路径节点 | 叶数 | 最大 full12 L2 叶距离 (rad) |
|---|---:|---:|---:|
'''
    for row in summary['paths']:
        md += f"| {row['edge_index']} | {row['nodes']} | {row['leaves']} | {row['max_leaf_full12_L2_rad']:.17g} |\n"
    md += '''
三条原 RBS 和原回溯是固定输入的真实非平凡局部资格。数值内核为已版本化的 RECONSTRUCTED physical full NR，不能据此认定原 KDL 数值轨迹一致、全局 NR 规划已成功、连续无碰撞或全文统计实验已完成。

完整检查和实际事件计数保存在同名 JSON。运行本审计不会消耗 VI 候选预算，也不改变正式 Table I 的 0/22500 状态。
'''
    if failed:
        md += '\n失败条目：\n' + '\n'.join('- ' + c['check'] for c in failed) + '\n'
    with OUT.with_suffix('.md').open('x') as f:
        f.write(md)
    print(json.dumps({k: report[k] for k in ('status','checks_total','checks_passed','checks_failed')},ensure_ascii=False))
