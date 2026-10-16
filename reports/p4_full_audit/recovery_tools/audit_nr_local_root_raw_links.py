#!/usr/bin/env python3
"""Stdlib-only exclusive addendum linking every saved raw NR local prefix.

No imports from the runner or its first independent review and no subprocesses.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'results/p4_full/20261015_R2_ABB_NR_LOCAL01'
BASE = ROOT / 'reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_INDEPENDENT_POST_20261015'
OUT = ROOT / 'reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_20261015'
checks = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text())


def exact(x):
    if isinstance(x, float):
        return ['binary64', struct.pack('>d', x).hex()]
    if isinstance(x, list):
        return [exact(v) for v in x]
    if isinstance(x, dict):
        return {k: exact(v) for k, v in x.items()}
    return x


def fp(x):
    return hashlib.sha256(json.dumps(exact(x), sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def check(n, a, b):
    checks.append(dict(check=n, passed=fp(a) == fp(b), actual_sha256=fp(a), expected_sha256=fp(b)))


def prefixed(p, pre):
    return [json.loads(v[len(pre):]) for v in p.read_text().splitlines() if v.startswith(pre)]


if __name__ == '__main__':
    if OUT.with_suffix('.json').exists() or OUT.with_suffix('.md').exists():
        raise FileExistsError('Preserve existing addendum')
    execution = load(RUN / 'execution.json')
    protocol = load(ROOT / execution['protocol'])
    main = load(BASE.with_suffix('.json'))
    check('main.PASS', main['status'], 'PASS_SAVED_EVIDENCE_AUDIT')
    check('main.failure_count', main['checks_failed'], 0)
    pairs = {(v['environment'], v['request']['id']): v for v in load(RUN / 'source_pairs.json')}
    all_started, all_completed = Counter(), Counter()
    for bi, batch in enumerate(protocol['schedule']):
        env, mode = batch['environment'], batch['mode']
        stem = f'{bi+1:05d}_source_{bi:02d}_{env}_{mode}'
        events = prefixed(RUN / (stem + '.stderr.txt'), 'P4_PCS_TRACE ')
        responses = prefixed(RUN / (stem + '.stdout.txt'), 'P4_NR_RESPONSE ')
        chunks = []
        for event in events:
            if event['event'] == 'entered' and event['id'] == 1:
                chunks.append([])
            chunks[-1].append(event)
        check(stem + '.chunk_count', len(chunks), len(responses) if mode == 'trace' else 0)
        if mode == 'trace':
            for chunk, response in zip(chunks, responses):
                label = env + '.' + response['id']
                pair = pairs[(env, response['id'])]
                check(label + '.raw_all_events_binary64', chunk, pair['trace_observation']['events'])
                gd = [e['result'] for e in chunk if e['event'] == 'completed' and e['kind'] == 'nr_gd']
                check(label + '.raw_GD_candidates_response_binary64', gd, response['gd_completed_candidates'])
                entered = Counter(e['kind'] for e in chunk if e['event'] == 'entered')
                completed = Counter(e['kind'] for e in chunk if e['event'] == 'completed')
                all_started.update(entered)
                all_completed.update(completed)
                check(label + '.raw_source_IK_counter', response['source_log_counters']['IK_counter'], entered['nr_gd'])
                check(label + '.raw_source_collision_counter', response['source_log_counters']['collisionCheck_counter'], entered['collision'])
                check(label + '.raw_source_isValid_counter', response['source_log_counters']['isValid_counter'], entered['nr_valid_midpoint'])
    inventory = load(RUN / 'raw_prefix_inventory.json')
    check('raw_prefix_started_counts', inventory['trace_entered_counts'], dict(all_started))
    check('raw_prefix_completed_counts', inventory['trace_completed_counts'], dict(all_completed))
    worker_events = prefixed(RUN / '00005_independent_full_node_queue.stderr.txt', 'P4_NR_NODE_EVENT ')
    node_responses = prefixed(RUN / '00005_independent_full_node_queue.stdout.txt', 'P4_NR_NODE_RESPONSE ')
    by_node = {}
    for event in worker_events:
        by_node.setdefault(event['node_id'], []).append(event)
    check('worker_complete_node_ids', sorted(by_node), list(range(147)))
    adapter_pqp = 0
    for n, response in enumerate(node_responses):
        events = by_node[n]
        sequence = [(v['event'], v.get('arm')) for v in events]
        expected = [('math_arm_FK_started',1),('math_arm_FK_completed',1),('math_arm_FK_started',2),('math_arm_FK_completed',2),('collision_started',None)]
        expected += [('adapter_arm_FK_J_started',1),('adapter_arm_FK_J_completed',1),('adapter_arm_FK_J_started',2),('adapter_arm_FK_J_completed',2)] * 2
        expected += [('collision_completed', None)]
        check(f'worker.node{n}.full_sequence', sequence, expected)
        expected_counts = {k: len(v['query_codes']) for k, v in response['result']['collision']['variants'].items()}
        check(f'worker.node{n}.durable_query_counts', events[-1]['variant_query_counts'], expected_counts)
        check(f'worker.node{n}.durable_query_total', events[-1]['PQP_queries'], sum(expected_counts.values()))
        adapter_pqp += sum(expected_counts.values())
        check(f'worker.node{n}.cumulative_counts', response['observed_counts'], {
            'math_arm_FK_started':2*(n+1), 'math_arm_FK_completed':2*(n+1),
            'collision_calls_started':n+1, 'collision_calls_completed':n+1,
            'adapter_arm_FK_J_started':4*(n+1), 'adapter_arm_FK_J_completed':4*(n+1),
            'PQP_queries':adapter_pqp})
    events = [json.loads(v) for v in (RUN / 'events.jsonl').read_text().splitlines()]
    starts = [v for v in events if v['event'] == 'process_started']
    finishes = [v for v in events if v['event'] == 'process_finished']
    check('processes.complete5', len(starts), 5)
    check('processes.no_missing_tail', [v['label'] for v in starts], [v['label'] for v in finishes])
    for start, finish in zip(starts, finishes):
        name = finish['label']
        stem = Path(start['input']).name.removesuffix('.input.txt')
        check(name + '.exit0', finish['exit_code'], 0)
        check(name + '.stdout_hash', sha(RUN / (stem + '.stdout.txt')), finish['stdout_sha256'])
        check(name + '.stderr_hash', sha(RUN / (stem + '.stderr.txt')), finish['stderr_sha256'])
    check('no_execution_diagnostics', execution['diagnostics'], [])
    check('full_tail_no_partial', sorted(p.name for p in RUN.glob('*partial*')), [])
    failed = [v for v in checks if not v['passed']]
    report = dict(schema='P4_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_V1', generated_at_utc=datetime.now(timezone.utc).isoformat(),
        run_id=RUN.name, status='PASS_RAW_LINK_ADDENDUM' if not failed else 'FAIL_RAW_LINK_ADDENDUM',
        checks_total=len(checks), checks_passed=len(checks)-len(failed), checks_failed=len(failed),
        zero_new_scientific_calls=True, zero_compile_calls=True,
        main_report_sha256=sha(BASE.with_suffix('.json')), script_sha256=sha(__file__),
        all_raw_started_counts=dict(all_started), all_raw_completed_counts=dict(all_completed),
        failed_checks=failed, checks=checks)
    with OUT.with_suffix('.json').open('x') as f:
        json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    with OUT.with_suffix('.md').open('x') as f:
        f.write(f'''# NR 局部资格独立 raw 绑定补充复核

**{report['status']}**：{len(checks)-len(failed)}/{len(checks)} 通过，{len(failed)} 失败。0 新科学调用，0 编译。

逐请求核对 raw trace 的完整事件及 GD 完成候选与保存 pair/response 的 binary64 内容；复核源 IK、collision、isValid 非计时计数，147 节点逐个的完整 worker 事件顺序和累计实际计数，5 个进程 exit0、原始 stdout/stderr 哈希与全部尾部。它补充主独立审计，不覆盖或替换主报告。

主报告 SHA256：`{report['main_report_sha256']}`。本补充仅读取保存资料，不增加任何算法、模型、碰撞或规划结论。
''')
    print(json.dumps({k:report[k] for k in ('status','checks_total','checks_passed','checks_failed')}))
