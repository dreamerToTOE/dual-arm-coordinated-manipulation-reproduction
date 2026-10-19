import csv,hashlib,json,math
from pathlib import Path
R=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def save_new(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
oldp=R/'results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V4.json';old=load(oldp);olde={r['execution']:r for r in old['executions']};entries=[]
for p in sorted((R/'results/p4_full').glob('20261015_R2_*/execution.json')):
 rel=str(p.relative_to(R));x=load(p)
 if rel in olde:
  assert sha(p)==olde[rel]['execution_sha256'];entries.append(olde[rel]);continue
 eng=x.get('classification')=='ENGINEERING_BUILD_ONLY'
 entries.append({'run_id':x['run_id'],'execution':rel,'execution_sha256':sha(p),'source_commit':x['source_commit'],'status':x['status'],'classification':x.get('classification'),'engineering_only':eng,'wall_s':x['wall_s'],'cpu_s':x['cpu_s'],'counts':x.get('counts',{}),'authorization_budget_id':x.get('authorization_budget_id'),'formal_planning_calls':x.get('formal_planning_calls',x.get('formal_table_I_calls',0))})
assert len(entries)==18;assert all(next(r for r in entries if r['execution']==k)==v for k,v in olde.items())
science=[r for r in entries if not r['engineering_only']];eng=[r for r in entries if r['engineering_only']]
w=math.fsum(r['wall_s'] for r in entries);c=math.fsum(r['cpu_s'] for r in entries)
ledger={**old,'schema':'P4_R2_RECOVERY_ACTUAL_LEDGER_V5','previous_snapshot':str(oldp.relative_to(R)),'previous_snapshot_sha256':sha(oldp),'executions':entries,'count':len(entries),'science_count':len(science),'engineering_count':len(eng),'science_wall_s':math.fsum(r['wall_s'] for r in science),'science_cpu_s':math.fsum(r['cpu_s'] for r in science),'engineering_wall_s':math.fsum(r['wall_s'] for r in eng),'engineering_cpu_s':math.fsum(r['cpu_s'] for r in eng),'conservative_r2_sum_wall_s':w,'conservative_r2_sum_cpu_s':c,'r2_remaining':{'wall_s':3600-w,'cpu_s':7200-c},'double_counting_rule':'Each execution own cost once. Two engineering builds included conservatively in R2. No cumulative fields. All old entries/costs unchanged; V4 unchanged.','new_qualification_planner_solves_in_this_snapshot':1,'source_solve_original_execution_status_retained':'SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT','source_solve_followup_path_status':'PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH','source_solve_followup_path_execution':'results/p4_full/20261015_R2_ABB_RRT_PATH01/execution.json','source_solve_followup_path_execution_sha256':sha(R/'results/p4_full/20261015_R2_ABB_RRT_PATH01/execution.json'),'scope':'Qualification only; II seed7 original RRT_PCS with reconstructed endpoints/R2 numerics/observational I/O. Not Table I statistics, fair performance, complete geometry or CCD.','saved_only_analysis':True,'new_scientific_calls':0}
assert len(science)==16 and len(eng)==2;assert ledger['formal_table_I_calls']==0 and ledger['formal_table_I_required_calls']==22500
lp=R/'results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V5.json';save_new(lp,ledger)
base=R/'reports/P4_FULL_R2_ABB_PCS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv'
with base.open(newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
assert len(rows)==211 and len(fields)==73
extra=['rrt_pcs_e2e_status','rrt_pcs_e2e_actual_scope','rrt_pcs_e2e_evidence','rrt_pcs_e2e_remaining_gate','rrt_pcs_e2e_formal_trials','rrt_pcs_e2e_classification','rrt_pcs_e2e_ledger_snapshot','rrt_pcs_e2e_source_path_qualified']
key={'P4-T01','P4-T02','P4-T05','P4-T08','P4-T11','P4-T16','P4-T17','P4-T18','P4-T20','P4-T24','P4-T25','P4-T26','P4-T27','P4-T28','P4-T02-II','P4-T05-II_PCS','P4-T08-II_ABLATION','P4-T18-II_RRT_PCS','P4-T24-STEP_II','P4-T20-NN_COST'}
pathrun=R/'results/p4_full/20261015_R2_ABB_RRT_PATH01';nodes=[load(pathrun/f'node_{i:05d}.json') for i in range(177)]
assert all(n['qualified'] for n in nodes) if 'qualified' in nodes[0] else all(n['math_qualified'] and n['collision']['status']=='CHECKED' and n['collision']['collision'] is False for n in nodes)
maxp=max(n['closure']['position_max_abs'] for n in nodes);maxr=max(n['closure']['rotation_matrix_max_abs'] for n in nodes)
actual=f'新增II单seed7原RRT_PCS一次资格solve，Range2.6/goalbias.05/原采样界、A01重建端点及R2数值；source Exact，4milestone/6树节点/5边，3次完整源回溯(0,3)→(1,3)→(0,0)，177唯一节点/176叶、2角色切换；独立177/177闭链/原机械界/原被动branch meeting-set/v3 aligned源策略离散碰撞通过。max闭链位置{maxp:.17g}mm、旋转矩阵{maxr:.17g}，max叶12L2=.04949053472601928<.05。'
evidence='results/p4_full/20261015_R2_ABB_RRT_PCS_E2E_BUILD01/execution.json;results/p4_full/20261015_R2_ABB_RRT_PCS_E2E01/execution.json;results/p4_full/20261015_R2_ABB_RRT_PATH01/execution.json;reports/P4_FULL_R2_ABB_RRT_PCS_E2E_POST_REVIEW_20261015.md;results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V5.json'
gate='仅II/RRT/PCS单次资格；其他环境、Bi-RRT/SBL、普通NR/RSS与固定链消融待；45×500正式统计仍0/22500。2角色切换不证明PCS优势或奇异rank见证。完整碰撞几何/连续碰撞、速度公平性、Fig3–5/TableI–II全规模和其他原文义务均未完成；638原PQP重建rod警告保留。'
for r in rows:
 affected=r['item_id'] in key
 r.update({'rrt_pcs_e2e_status':'PARTIAL_WITH_ONE_QUALIFIED_DISCRETE_PATH' if affected else r['pcs_status'],'rrt_pcs_e2e_actual_scope':actual if affected else '本阶段无该项新增科学执行；前73列历史记录逐值保留。 '+r['pcs_actual_scope'],'rrt_pcs_e2e_evidence':evidence if affected else r['pcs_evidence'],'rrt_pcs_e2e_remaining_gate':gate+' 原完整义务：'+r['original_requirement'] if affected else r['pcs_remaining_gate'],'rrt_pcs_e2e_formal_trials':'0/22500; II_RRT_PCS qualification solve=1, formal=0','rrt_pcs_e2e_classification':'RECONSTRUCTED_ENDPOINTS_AND_R2_NUMERICS / AUTHOR_RRT_PCS / OBSERVED_IO / DISCRETE_SOURCE_POLICY_ONLY' if affected else 'UNCHANGED_PREVIOUS_SCOPE','rrt_pcs_e2e_ledger_snapshot':str(lp.relative_to(R))+' SHA256 '+sha(lp),'rrt_pcs_e2e_source_path_qualified':'II_RRT_PCS seed7 177/177 DISCRETE_SOURCE_POLICY_PASS; no full-statistics PASS' if affected else 'NO_NEW_PATH_FOR_THIS_OBLIGATION'})
out=R/'reports/P4_FULL_R2_ABB_RRT_PCS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv'
with out.open('x',newline='') as f:wr=csv.DictWriter(f,fieldnames=fields+extra);wr.writeheader();wr.writerows(rows)
with out.open(newline='') as f:newrows=list(csv.DictReader(f))
with base.open(newline='') as f:oldrows=list(csv.DictReader(f))
assert [{k:r[k] for k in fields} for r in newrows]==oldrows
assert {r['item_id'] for r in newrows}=={r['item_id'] for r in oldrows}
def esc(x):return str(x).replace('|','\\|').replace('\n','<br>')
md=R/'reports/P4_FULL_R2_ABB_RRT_PCS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.md'
intro=f'''# P4最新原论文与实际复现范围对照表：首条合格II原RRT_PCS离散路径

状态仍为全文PARTIAL。211项完整义务全部保留，CSV前73列的211×73个原字符串逐值/顺序保持，追加8列记录此次单次资格。旧CSV/MD与V4账本不变。

{actual}

{gate}

只增加一次qualification solve与一次完整path审查，不是正式Table I样本；正式仍0/22500（45cell×500，原1000s帽保留）。原source执行状态PENDING保持原字节，后续path PASS以独立execution关联。177节点通过原策略离散检查不构成连续路径或完整几何证书。

18个execution=16科学+2工程；保守纳R2的wall={w:.17g}s、CPU={c:.17g}s，余{3600-w:.17g}/{7200-c:.17g}s；VI B974/974、构造余0，未追加VI构造。新V5 SHA256 `{sha(lp)}`；本表生成仅读保存证据，0新科学调用。

NR C++准备、其他尚未资格算法和全规模科学审批均不因这条路径提前完成。P4后中文Word/PDF和双FR3适用分析仍待；必须交用户审查完整表，不自动进入P2/Isaac。

|ID|原文完整要求|原规模|本阶段最新状态|实际证据/范围|尚未完成|证据路径|
|---|---|---|---|---|---|---|
'''
with md.open('x') as f:
 f.write(intro)
 for r in rows:f.write('|'+ '|'.join(esc(r[k]) for k in ['item_id','original_requirement','original_repeats','rrt_pcs_e2e_status','rrt_pcs_e2e_actual_scope','rrt_pcs_e2e_remaining_gate','rrt_pcs_e2e_evidence'])+'|\n')
print(json.dumps({'ledger':str(lp),'ledger_sha256':sha(lp),'wall_s':w,'cpu_s':c,'remaining':ledger['r2_remaining'],'science_count':len(science),'engineering_count':len(eng),'coverage':str(out),'coverage_sha256':sha(out),'coverage_md_sha256':sha(md),'preserved_rows':len(rows),'preserved_columns':len(fields),'new_columns':len(extra),'max_saved_position_mm':maxp,'max_saved_rotation_matrix':maxr},ensure_ascii=False,indent=2))
