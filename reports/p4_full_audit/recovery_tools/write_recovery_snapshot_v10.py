"""Record actual IV zero-query stop and H saved certificate reuse, no new science."""
from pathlib import Path
import csv, hashlib, json, math
R=Path(__file__).resolve().parents[3]
O=Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/outputs')
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(R))
def new(p,x):
    with p.open('x')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
oldp=R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V9.json';old=load(oldp)
ep=R/'results/p4_full/20261015_R2_IV_RSS_WRIST_FIXED100_01/execution.json';e=load(ep)
assert e['status']=='STOP_PREFIX_RETAINED' and e['termination_reason']=="StopQualification('RUNTIME_GEOMETRY_OR_SOURCE_LIMITS_CHANGED')"
assert e['counts']=={'external_K_JSON_completed':0,'native_accepted_FK_observed':0}
assert len(e['uncompleted_branch_diagnostic_ids'])==800 and not e['target_results'] and not e['branch_observations']
link=R/'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_ALL64_SAVED_CERTIFICATE_LINKAGE_20261016.json';a=load(link)
assert a['checks_failed']==0 and a['checks_passed']==a['checks_total']==398
known={x['execution']:x for x in old['executions']};entries=[]
for p in sorted((R/'results/p4_full').glob('20261015_R2_*/execution.json')):
    n=rel(p);x=load(p)
    if n in known:
        assert sha(p)==known[n]['execution_sha256'];entries.append(known[n]);continue
    entries.append({'run_id':x['run_id'],'execution':n,'execution_sha256':sha(p),'source_commit':x['source_commit'],
        'status':x['status'],'classification':x.get('classification'),'engineering_only':False,
        'wall_s':x['wall_s'],'cpu_s':x['cpu_s'],'counts':x['counts'],'authorization_budget_id':None,'formal_planning_calls':0})
assert len(entries)==28 and all(next(x for x in entries if x['execution']==n)==v for n,v in known.items())
sci=[x for x in entries if not x['engineering_only']];eng=[x for x in entries if x['engineering_only']]
wall=math.fsum(x['wall_s']for x in entries);cpu=math.fsum(x['cpu_s']for x in entries)
lp=R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V10.json'
ledger={**old,'schema':'P4_R2_RECOVERY_ACTUAL_LEDGER_V10','previous_snapshot':rel(oldp),'previous_snapshot_sha256':sha(oldp),
    'executions':entries,'count':28,'science_count':22,'engineering_count':6,
    'science_wall_s':math.fsum(x['wall_s']for x in sci),'science_cpu_s':math.fsum(x['cpu_s']for x in sci),
    'engineering_wall_s':math.fsum(x['wall_s']for x in eng),'engineering_cpu_s':math.fsum(x['cpu_s']for x in eng),
    'conservative_r2_sum_wall_s':wall,'conservative_r2_sum_cpu_s':cpu,'r2_remaining':{'wall_s':3600-wall,'cpu_s':7200-cpu},
    'scope':'IV original fixed100 zero-query preflight stop retained, plus H all64 saved certificate linkage. No new H science.',
    'new_qualification_planner_solves_in_this_snapshot':0,
    'iv_wrist_shared_qualification_budget':{'total_wall_s':30.,'total_cpu_s':60.,
        'executions_consumed':[rel(ep)],'used_wall_s':e['wall_s'],'used_cpu_s':e['cpu_s'],
        'remaining_wall_s':30-e['wall_s'],'remaining_cpu_s':60-e['cpu_s'],
        'targets_constructed':0,'IK_dispatched':0,'max_total_targets':100,'max_total_K_requests':800,
        'rule':'Zero-query implementation preflight stop is charged once. Any versioned repair uses only this shared remainder, never a reset 30/60 budget.'},
    'h_saved_all64_linkage':{'report':rel(link),'sha256':sha(link),'checks':398,'new_scientific_calls':0,
        'classification':'SAVED_REUSED_EVIDENCE_ONLY','covered_saved_outputs':64,'unique_environment_q12_binary64_keys':19,
        'original_H_actual_final_gates':34,'original_H_unknown_final_gates':30,'original_H_status_unchanged':True},
    'saved_only_analysis':True,'new_scientific_calls':0}
assert ledger['vi_B_remaining']['candidate_constructions']==0 and ledger['formal_table_I_calls']==0
base=R/'reports/P4_FULL_R2_HELPER_H_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
with base.open(newline='')as f:r=csv.DictReader(f);fields=r.fieldnames;before=list(r)
assert len(fields)==114 and len(before)==211
extra=['iv_wrist_preflight_status','iv_wrist_preflight_scope','iv_wrist_preflight_evidence','iv_wrist_preflight_remaining',
    'h_all64_saved_linkage_status','h_all64_saved_linkage_scope','recovery_v10_ledger','formal_trials_v10']
rows=[]
for oldrow in before:
    row=dict(oldrow);iv=row['item_id']in {'P4-T07','P4-T07-RSS_IV','P4-T13'}
    h=row['item_id']in {'P4-T02','P4-T02-II','P4-T02-III','P4-T25'}
    row.update({'iv_wrist_preflight_status':'ZERO_QUERY_RUNTIME_METADATA_GUARD_STOP'if iv else'NO_NEW_IV_EVIDENCE',
        'iv_wrist_preflight_scope':'原固定100/800在首模型前因q1字面界和degree换算1ULP元数据精确比较退出；0target/FK/IK，800全部未执行；原STOP保留。'if iv else'本阶段此义务无新IV科学结果。',
        'iv_wrist_preflight_evidence':rel(ep)if iv else'NOT_APPLICABLE',
        'iv_wrist_preflight_remaining':'独立核我方元数据guard；不改实际物理界/数学门/固定输入，修复若执行仅原30/60共享余额。RSS碰撞/RBS/分布/规划仍待。'if iv else row['helper_h_remaining_gate'],
        'h_all64_saved_linkage_status':'PASS_SAVED_CERTIFICATE_LINKAGE_64_ONLY'if h else'NO_NEW_H_EVIDENCE',
        'h_all64_saved_linkage_scope':'64输出19精确键；H34完整门覆盖12键，旧已审PCS_LOCAL01覆盖7键。每context主动6角与direct/dual label单独引用和核验，398/398通过、0新科学。原H STOP/30UNKNOWN保持；非64现场外门或规划资格。'if h else'本阶段此义务无新增H证据。',
        'recovery_v10_ledger':rel(lp),'formal_trials_v10':'0/22500; full original scales retained'})
    rows.append(row)
cp=R/'reports/P4_FULL_R2_IV_PREFLIGHT_H_SAVED_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv';mp=cp.with_suffix('.md')
assert not any(p.exists()for p in [lp,cp,mp]);new(lp,ledger)
with cp.open('x',newline='')as f:w=csv.DictWriter(f,fieldnames=fields+extra);w.writeheader();w.writerows(rows)
with cp.open(newline='')as f:assert[{k:r[k]for k in fields}for r in csv.DictReader(f)]==before
with mp.open('x')as f:
    f.write('# P4全文范围：IV零查询入口停止及H既有证据链接\n\n211行前114列原字符串继承，新增8列。H64输出物理证据已精确链接，但原H运行仍STOP/34完整/30UNKNOWN。IV首模型前0query停止，800全部未执行。\n\n'+
        f'28execution=22科学运行账（含零查询入口失败）+6工程，自身成本wall{wall:.17g}/CPU{cpu:.17g}秒；VI974余0，正式0/22500。原100/800资格预算30/60只余{30-e["wall_s"]:.17g}/{60-e["cpu_s"]:.17g}秒，版本修复不重置。\n\n'+
        '全部500000投影/约50000点对、三方法三搜索器六环境、Fig3–5/TableI–II及消融保持；非全文完成，不P2/Isaac。\n\n|ID|原完整义务|原规模|IV状态|H保存链接|后续|\n|---|---|---|---|---|---|\n')
    for row in rows:f.write('|'+ '|'.join(str(row[k]).replace('|','\\|').replace('\n','<br>')for k in['item_id','original_requirement','original_repeats','iv_wrist_preflight_scope','h_all64_saved_linkage_scope','iv_wrist_preflight_remaining'])+'|\n')
for p in[lp,cp,mp]:
    with(O/p.name).open('xb')as f:f.write(p.read_bytes())
print(json.dumps({'ledger':rel(lp),'wall_s':wall,'cpu_s':cpu,'rows':211,'columns':122}))
