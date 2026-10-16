"""Preserve V8 and record the actual H wall-cap stop, saved evidence only."""
from pathlib import Path
import csv
import hashlib
import json
import math

R = Path(__file__).resolve().parents[3]
O = Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/outputs')
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return str(p.relative_to(R))
def new(p, v):
    with p.open('x') as f:
        json.dump(v, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')

oldp = R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V8.json'
old = read(oldp); known = {x['execution']: x for x in old['executions']}
base = R/'reports/P4_FULL_R2_NR_RRT_PATH_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
old_hashes = {p: sha(p) for p in [oldp, base, base.with_suffix('.md')]}
ep = R/'results/p4_full/20261015_R2_ABB_RANDOM_HELPER_H01/execution.json'; e = read(ep)
assert e['status'] == 'STOP_CLEANUP_OR_EVIDENCE_ERROR'
assert e['termination_reason'] == "TimeoutError('H_AGGREGATE_HARD_WALL_CAP')"
assert e['plain_trace_comparison_cases'] == 32 and e['control_prefix_comparison_cases'] == 16
assert e['counts']['helper_completed'] == 64 and e['independent_final_cases'] == 34
assert e['source_true_count'] == e['source_false_count'] == 32
assert e['bound_files_sha256'] == e['bound_files_after_sha256'] and e['complete_source_raw_evidence_gate']
assert len(e['uncompleted_final_fixtures']) == 30 and not e['uncompleted_helper_fixtures']
post = R/'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_ROOT_INDEPENDENT_POST_20261016.json'
p = read(post)
assert p['checks_failed'] == 0 and p['checks_passed'] == p['checks_total']
entries = []
for q in sorted((R/'results/p4_full').glob('20261015_R2_*/execution.json')):
    name = rel(q); x = read(q)
    if name in known:
        assert sha(q) == known[name]['execution_sha256']; entries.append(known[name]); continue
    entries.append({'run_id': x['run_id'], 'execution': name, 'execution_sha256': sha(q),
        'source_commit': x['source_commit'], 'status': x['status'], 'classification': x.get('classification'),
        'engineering_only': x.get('classification') == 'ENGINEERING_BUILD_ONLY',
        'wall_s': x['wall_s'], 'cpu_s': x['cpu_s'], 'counts': x.get('counts', {}),
        'authorization_budget_id': x.get('authorization_budget_id'),
        'formal_planning_calls': x.get('formal_table_I_calls', 0)})
assert len(entries) == 27
assert all(next(x for x in entries if x['execution'] == n) == v for n, v in known.items())
science = [x for x in entries if not x['engineering_only']]
engineering = [x for x in entries if x['engineering_only']]
assert len(science) == 21 and len(engineering) == 6
wall = math.fsum(x['wall_s'] for x in entries); cpu = math.fsum(x['cpu_s'] for x in entries)
lp = R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V9.json'
ledger = {**old, 'schema': 'P4_R2_RECOVERY_ACTUAL_LEDGER_V9', 'previous_snapshot': rel(oldp),
    'previous_snapshot_sha256': sha(oldp), 'executions': entries, 'count': 27,
    'science_count': 21, 'engineering_count': 6,
    'science_wall_s': math.fsum(x['wall_s'] for x in science),
    'science_cpu_s': math.fsum(x['cpu_s'] for x in science),
    'engineering_wall_s': math.fsum(x['wall_s'] for x in engineering),
    'engineering_cpu_s': math.fsum(x['cpu_s'] for x in engineering),
    'conservative_r2_sum_wall_s': wall, 'conservative_r2_sum_cpu_s': cpu,
    'r2_remaining': {'wall_s': 3600-wall, 'cpu_s': 7200-cpu},
    'double_counting_rule': 'Each execution own cost once; old V8 entries byte-equivalent. H build and stopped science each charged once, including cleanup overrun.',
    'new_qualification_planner_solves_in_this_snapshot': 0, 'total_qualification_planner_solves': 2,
    'scope': 'Added H two-target build and actual fixed64 helper/control-flow result with original 60wall cap stop; incomplete physical gate remains incomplete.',
    'h_actual': {'execution': rel(ep), 'execution_sha256': sha(ep), 'status': e['status'],
        'helper_completed': 64, 'plain_trace_pairs': 32, 'control_prefix_pairs': 16,
        'source_control_false': 32, 'success_break_true': 32, 'complete_final_gates': 34,
        'uncompleted_final_gate_ids': [f['dispatch_index'] for f in e['uncompleted_final_fixtures']],
        'source_raw_evidence_complete': True, 'counts': e['counts'],
        'independent_saved_post': rel(post), 'saved_post_sha256': sha(post),
        'interface_control_flow_subgate_complete': True, 'full_fixed64_physical_qualification': False,
        'formal_statistics_sample': False}, 'saved_only_analysis': True, 'new_scientific_calls': 0}
assert ledger['formal_table_I_calls'] == 0 and ledger['formal_table_I_required_calls'] == 22500
assert ledger['vi_B_candidate_cap'] == 974 and ledger['vi_B_remaining']['candidate_constructions'] == 0
with base.open(newline='') as f:
    reader = csv.DictReader(f); fields = reader.fieldnames; before = list(reader)
assert len(before) == 211 and len(fields) == 106
extra = ['helper_h_status', 'helper_h_actual_scope', 'helper_h_evidence', 'helper_h_remaining_gate',
    'helper_h_formal_trials', 'helper_h_classification', 'helper_h_ledger_snapshot', 'helper_h_saved_review']
scope = ('H原三参helper固定16上下文×两控制流×plain/trace=64真实调用完成；32逐bit模式对及16首次成功prefix全通过，原控制32false/成功break32true。'
    '独立终态34完整合格，35数学/70真实worker已完成，第35adapter在60wall帽附近返回错误，原STOP及30未完成尾保持；raw全部EOF完整。'
    '本接口不在原三planner实际grow路径；不外推规划或分布。')
gate = '固定64全部物理门尚未完成；原60wall单次预算已停止，不自动续跑/扩大。需保存证据根因与明确冻结的后续方案；其他环境/方法/搜索器及全部正式统计仍待。'
evidence = ';'.join([rel(ep), 'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_POST_TASK_20261016.md', rel(post), rel(lp)])
rows = []
for oldrow in before:
    row = dict(oldrow); affected = row['item_id'] in {'P4-T02', 'P4-T02-II', 'P4-T02-III', 'P4-T25'}
    row.update({'helper_h_status': 'PARTIAL_CONTROL_FLOW_PASS_FINAL_GATE_WALL_CAP_STOP' if affected else row['nr_rrt_path_status'],
        'helper_h_actual_scope': scope if affected else '本阶段此义务无新增科学证据；'+row['nr_rrt_path_actual_scope'],
        'helper_h_evidence': evidence if affected else row['nr_rrt_path_evidence'],
        'helper_h_remaining_gate': gate+' 原完整义务：'+row['original_requirement'] if affected else row['nr_rrt_path_remaining_gate'],
        'helper_h_formal_trials': '0/22500; H fixed local interface nonformal; PCS+NR qualification solves2 nonformal',
        'helper_h_classification': e['classification'] if affected else 'NO_NEW_RESULT_FOR_THIS_OBLIGATION',
        'helper_h_ledger_snapshot': rel(lp), 'helper_h_saved_review': rel(post) if affected else 'NOT_APPLICABLE_NO_NEW_RESULT'})
    rows.append(row)
cp = R/'reports/P4_FULL_R2_HELPER_H_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'; mp = cp.with_suffix('.md')
assert not any(p.exists() for p in [lp, cp, mp]); new(lp, ledger)
with cp.open('x', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields+extra); writer.writeheader(); writer.writerows(rows)
with cp.open(newline='') as f: after = list(csv.DictReader(f))
assert [{k: r[k] for k in fields} for r in after] == before
with mp.open('x') as f:
    f.write('# P4 原论文与实际范围：H 固定资格真实超时后\n\n全文仍部分完成。211行及前106列逐值继承，新增8列。\n\n'+scope+'\n\n'+gate+
        f'\n\nV9共27execution=21科学+6工程，自身成本各计一次wall{wall:.17g}/CPU{cpu:.17g}秒，R2余{3600-wall:.17g}/{7200-cpu:.17g}秒。VI974/974余0；正式0/22500；500000投影、约50000合法点对、Fig3–5/TableI–II和全部消融保持。\n\n|ID|原完整要求|原规模|当前范围|待完成|证据|\n|---|---|---|---|---|---|\n')
    for row in rows:
        f.write('|'+ '|'.join(str(row[k]).replace('|', '\\|').replace('\n', '<br>') for k in
            ['item_id', 'original_requirement', 'original_repeats', 'helper_h_actual_scope', 'helper_h_remaining_gate', 'helper_h_evidence'])+'|\n')
assert all(sha(p) == h for p, h in old_hashes.items())
for p in [lp, cp, mp]:
    with (O/p.name).open('xb') as f: f.write(p.read_bytes())
print(json.dumps({'ledger': rel(lp), 'wall_s': wall, 'cpu_s': cpu, 'rows': 211, 'old_columns': 106, 'new_columns': 8}))
