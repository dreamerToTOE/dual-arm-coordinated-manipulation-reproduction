"""Saved-data D080 scope overlay. No model imports or experimental dispatch."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import itertools
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'reports/P4_FULL_R2_SBL_PCS_SETUP01_ORIGINAL_VS_REPRODUCED_COVERAGE_20261017.csv'
SOURCE_SHA = '2b34a55a39f3678d1d5a7ec1ca1d1c0bf13c828fad9ec6f2f4cfe7461604a491'
STEM = ROOT/'reports/P4_D080_ORIGINAL_VS_APPROVED_VS_ACTUAL_COVERAGE_20261017'
ENVIRONMENTS = ('I', 'II', 'III', 'IV', 'V', 'VI')
EXTRA = ['d080_scope', 'd080_reason', 'd080_environments', 'd080_actual_evidence',
         'd080_status', 'd080_original_table_I_trials', 'd080_approved_table_I_trials',
         'd080_formal_trials_completed', 'd080_statistical_scale', 'd080_next_action']
PATH_REPORTS = {
    ('RRT', 'PCS'): 'reports/P4_FULL_R2_ABB_RRT_PCS_PATH_POST_TASK_20261015.md',
    ('RRT', 'NR'): 'reports/P4_FULL_R2_ABB_RRT_NR_PATH_POST_TASK_20261016.md',
    ('Bi-RRT', 'PCS'): 'reports/P4_FULL_R2_ABB_CBIRRT_D_PATH_POST_TASK_20261016.md',
    ('Bi-RRT', 'NR'): 'reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH01_POST_TASK_20261017.md',
}
SETUP = 'reports/P4_FULL_R2_ABB_SBL_PCS_SETUP01_POST_TASK_20261017.md'
LEDGER = 'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V25.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dump_new(p, value):
    with p.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def row_env(row):
    """Use explicit platform/IDs; generic legacy platform is not a VI selector."""
    ident = row['item_id']
    if ident == 'P4-T20-NN_COST':
        return 'I|II|III|IV|V|VI_OR_GENERAL_METHOD'
    if row['original_model_platform'] in ENVIRONMENTS:
        return row['original_model_platform']
    match = re.search(r'(?:-|_)(VI|IV|III|II|V|I)(?:_|$)', ident)
    if match:
        return match.group(1)
    if ident in {'P4-T10', 'P4-T19'} or ident.startswith('P4-T19-'):
        return 'I'
    if ident in {'P4-T04', 'P4-T20', 'P4-T22'} or ident.startswith(('P4-T04-', 'P4-T20-', 'P4-T22-')):
        return 'II'
    if ident == 'P4-T21' or ident.startswith('P4-T21-'):
        return 'I|II_PAPER_FIG4_CAPTION_BODY_AMBIGUITY'
    if ident in {'P4-T11', 'P4-T12', 'P4-T13', 'P4-T14', 'P4-T15'}:
        return {'P4-T11': 'II', 'P4-T12': 'III', 'P4-T13': 'IV', 'P4-T14': 'V', 'P4-T15': 'VI'}[ident]
    if ident.startswith('P4-T01-FIG1'):
        return 'FOUR_BAR_METHOD_ILLUSTRATION'
    if ident == 'P4-T29':
        return 'FUTURE_APPLICATION_ANALYSIS_ONLY'
    return 'I|II|III|IV|V|VI_OR_GENERAL_METHOD'


def overlay(row):
    ident = row['item_id']; env = row_env(row)
    excluded = env == 'VI'
    partial = env == 'I|II|III|IV|V|VI_OR_GENERAL_METHOD'
    scope = ('ARCHIVED_OUT_OF_APPROVED_SCOPE' if excluded else
             'PARTIAL_SCOPE_I_V_VI_ARCHIVED' if partial else
             'IN_SCOPE_METHOD_BENCHMARK' if env in ('I', 'FOUR_BAR_METHOD_ILLUSTRATION') else
             'IN_SCOPE_APPLICATION_ANALYSIS_ONLY' if env == 'FUTURE_APPLICATION_ANALYSIS_ONLY' else
             'IN_SCOPE_FULL_APPLICATION_PRIORITY' if env == 'V' else 'IN_SCOPE_FULL')
    reason = ('D080排除后续VI执行；保留原文义务、已有证据和预算，不能计作完成。' if excluded else
              '保留I–V适用部分及数学/源码审查；VI经验泛化本轮不验证，不能将跨环境条目判FULL。' if partial else
              'D080保留此原文义务及原统计规模；Fig4图注/正文歧义继续保留。' if env.startswith('I|II_PAPER') else
              'D080明确保留；V应用优先但不改变作者模型或验收门。' if env == 'V' else
              'D080明确保留；沿用原方法、条件与已有有效证据。')
    evidence = '原186历史列按行保留；索引：reports/P4_D080_RECOVERY_AND_STAGE_PLAN_20261017.md；无新增科学运行。'
    status = 'PARTIAL_EXISTING_EVIDENCE_PENDING_RETAINED_OBLIGATION'
    action = '按阶段计划资格→cost pilot→正式预算批准→对应全量实验。'
    if ident == 'P4-T29':
        action = '完成P4后仅逐方法分析FR3适用性、接口、风险与未来路线；不启动FR3/Isaac/P2实验。'
    if re.fullmatch(r'P4-T(?:01|06)-EQ[1-9]', ident):
        reason = '公式、假设和适用条件的全文核对完整保留；PARTIAL只限制VI经验泛化，不删数学定义或理论审查。'
        action = '完整核对公式/推导/适用假设，复用已审反例；I–V经验验证，VI历史证据只读归档。'
    original = approved = completed = 'NOT_A_TABLE_I_CELL'
    if excluded:
        status = 'ARCHIVED_HISTORY_NOT_D080_COMPLETION'
        action = '只读保全；不再追加VI模型、修复、构造、规划或统计。'
        evidence += ' VI旧证据见reports/P4_FULL_R2_VI_RSS_INGRESS_POST_TASK_20261015.md；974/974，余额0。'
    if ident.startswith('P4-T18-'):
        cell_env, planner, method = ident[len('P4-T18-'):].split('_')
        assert env == cell_env
        original, approved, completed = '500', '0' if excluded else '500', '0'
        if not excluded:
            status = 'NOT_RUN_FORMAL_REQUIRES_COST_PILOT_AND_BUDGET_APPROVAL'
            if env == 'II' and (planner, method) in PATH_REPORTS:
                evidence = PATH_REPORTS[planner, method] + '; 已有单seed离散路径只读复用，正式统计0/500；CCD未证。'
            elif env == 'II' and planner == 'SBL' and method == 'PCS':
                evidence = SETUP + '; setup已验收，局部/solve/完整路径待资格；正式0/500。'
            else:
                evidence += ' 本组合尚无本环境已合格端到端路径；组件不能代正式500次。'
    elif ident == 'P4-T18':
        original, approved, completed = '22500', '18000', '0'
        status = 'PARTIAL_SCOPE_FORMAL_NOT_RUN'
    elif not excluded and env == 'II':
        evidence += ' II四路径及SBL setup见本次恢复报告，证书不自动覆盖此整项义务。'
    scale = row['original_repeats'] + '; ' + row['original_duration_budget']
    return dict(zip(EXTRA, [scope, reason, env, evidence, status, original, approved,
                             completed, scale, action]))


def main():
    assert sha(SOURCE) == SOURCE_SHA
    with SOURCE.open(newline='') as f:
        reader = csv.DictReader(f); fields = reader.fieldnames; old = list(reader)
    assert len(fields) == 186 and len(old) == 211 and len({r['item_id'] for r in old}) == 211
    rows = [{**r, **overlay(r)} for r in old]
    excluded_ids = {'P4-T15', 'P4-T08-VI_ABLATION', 'P4-T07-RSS_VI', 'P4-T24-STEP_VI'}
    excluded_ids |= {'P4-'+key+'-VI' for key in ('T02','T03','T16','T23','T30')}
    excluded_ids |= {'P4-T05-VI_'+method for method in ('RSS','PCS','NR')}
    excluded_ids |= {'P4-T18-VI_'+planner+'_'+method for planner in ('RRT','Bi-RRT','SBL') for method in ('RSS','PCS','NR')}
    assert len(excluded_ids) == 21
    assert {r['item_id'] for r in rows if r['d080_scope']=='ARCHIVED_OUT_OF_APPROVED_SCOPE'} == excluded_ids
    planned_cells = [r for r in rows if r['item_id'].startswith('P4-T18-')]
    assert len(planned_cells)==45 and sum(r['d080_approved_table_I_trials']=='500' for r in planned_cells)==36
    outcsv = STEM.with_suffix('.csv'); outmd = STEM.with_suffix('.md')
    with outcsv.open('x', newline='') as f:
        writer = csv.DictWriter(f, fields + EXTRA); writer.writeheader(); writer.writerows(rows)
    with outcsv.open(newline='') as f:
        reader = csv.DictReader(f); saved = list(reader)
        assert reader.fieldnames == fields + EXTRA
    assert [{k: r[k] for k in fields} for r in saved] == old
    cells = [r for r in rows if r['item_id'].startswith('P4-T18-')]
    expected = set(itertools.product(('II','III','IV','V','VI'), ('RRT','Bi-RRT','SBL'), ('RSS','PCS','NR')))
    assert {tuple(r['item_id'][7:].split('_')) for r in cells} == expected
    assert sum(int(r['d080_original_table_I_trials']) for r in cells) == 22500
    assert sum(int(r['d080_approved_table_I_trials']) for r in cells) == 18000
    kept = [r for r in cells if r['d080_approved_table_I_trials'] == '500']
    assert len(kept) == 36 and len(cells) - len(kept) == 9
    assert all(r['original_duration_budget'] == '1000s/call' and r['original_repeats'] == '500' for r in cells)
    with outmd.open('x') as f:
        f.write('# P4 原论文／D080批准范围／实际证据对照\n\n211行保留原186列，新增10列；旧文件不改。本表不是完成率评分。\n\n')
        f.write('原Table I：45×500=22500；D080：II–V 36×500=18000；VI 9×500=4500仅存档。正式已执行0/18000；单seed路径不计正式统计。\n\n')
        f.write('|ID|原文义务|D080范围|实际状态|证据／后续|\n|---|---|---|---|---|\n')
        for row in rows:
            values = [row[k] for k in ('item_id','original_requirement','d080_scope','d080_status','d080_actual_evidence')]
            f.write('|'+'|'.join(v.replace('|','/').replace('\n','<br>') for v in values)+'|\n')
    jobs = ROOT/'configs/p4_d080/formal_18000_jobs_DRAFT_NOT_AUTHORIZED_v1.csv'
    with jobs.open('x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['job_id','coverage_item_id','environment','planner','method','repeat_index_1based','seed','timeout_s','protocol_status','source_version','result'])
        for row in kept:
            env, planner, method = row['item_id'][7:].split('_')
            for repeat in range(1, 501):
                writer.writerow([f'D080_{env}_{planner}_{method}_{repeat:03d}',row['item_id'],env,planner,method,repeat,'PENDING_PAIRED_SEED_FREEZE',1000,'DRAFT_NOT_AUTHORIZED','PENDING_PER_CELL_QUALIFICATION','NOT_RUN'])
    with jobs.open(newline='') as f:
        saved_jobs = list(csv.DictReader(f))
    assert len(saved_jobs) == len({r['job_id'] for r in saved_jobs}) == 18000
    assert all(n == 500 for n in Counter(r['coverage_item_id'] for r in saved_jobs).values())
    ledger_path = ROOT/LEDGER; ledger = json.loads(ledger_path.read_text())
    assert ledger['count'] == 43 and ledger['formal_table_I_calls'] == 0
    budget = dict(schema='P4_D080_BUDGET_SCOPE_OVERLAY_V1',historical_ledger=LEDGER,historical_ledger_sha256=sha(ledger_path),
                  historical_costs_unchanged=True,executions=43,science_count=32,engineering_count=11,
                  charged_wall_s=ledger['conservative_r2_sum_wall_s'],charged_cpu_s=ledger['conservative_r2_sum_cpu_s'],
                  r2_caps=ledger['r2_caps'],r2_remaining_upper_bound=ledger['r2_remaining'],
                  historical_unmeasured_tails='UNKNOWN_RETAINED',original_table_I_trials=22500,
                  d080_approved_scope_trials=18000,archived_VI_original_trials=4500,formal_completed=0,
                  formal_execution_budget_approved=False,new_scientific_executions=0,
                  VI_candidate_cap=974,VI_candidates_consumed=974,VI_remaining=0,VI_future_execution='PROHIBITED_BY_D080')
    dump_new(ROOT/'results/p4_d080/20261017_SCOPE_RECOVERY/budget_scope_overlay.json',budget)
    result = dict(schema='P4_D080_SCOPE_MAPPING_V1',source=str(SOURCE.relative_to(ROOT)),source_sha256=SOURCE_SHA,
                  output=str(outcsv.relative_to(ROOT)),output_sha256=sha(outcsv),rows=211,historical_columns=186,
                  new_columns=EXTRA,total_columns=196,historical_column_value_differences=0,
                  scope_counts=dict(Counter(r['d080_scope'] for r in rows)),original_cells=45,approved_cells=36,
                  archived_VI_cells=9,original_trials=22500,approved_trials=18000,archived_trials=4500,
                  job_manifest=str(jobs.relative_to(ROOT)),job_manifest_sha256=sha(jobs),unique_jobs=18000,
                  job_status='DRAFT_NOT_AUTHORIZED',formal_trials_completed=0,new_scientific_calls=0)
    dump_new(ROOT/'reports/P4_D080_SCOPE_MAPPING_VALIDATION_20261017.json',result)
    assert sha(SOURCE) == SOURCE_SHA
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
