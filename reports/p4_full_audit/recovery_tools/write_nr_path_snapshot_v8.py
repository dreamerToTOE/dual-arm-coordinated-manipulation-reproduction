"""Immutable complete coverage V8; saved evidence only."""
from pathlib import Path
import json,csv,hashlib,math
R=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full');O=Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/outputs')
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(R))
def new(p,x):
 with p.open('x')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
oldp=R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V7.json';old=load(oldp);om={x['execution']:x for x in old['executions']}
base=R/'reports/P4_FULL_R2_NR_LOCAL_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
oldhash={str(p):sha(p)for p in[oldp,base,base.with_suffix('.md')]}
qp=R/'results/p4_full/20261015_R2_ABB_RRT_NR_PATH01';ep=qp/'execution.json';e=load(ep);protocol=load(R/e['protocol']);source=load(R/'results/p4_full/20261015_R2_ABB_RRT_NR_E2E01/runtime/result.json');qe=protocol['fixed_queue']
assert e['status']=='PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH'and e['full_node_queue_checked']and e['full_node_queue_count']==393 and not e['uncompleted_node_ids']and not e['diagnostics']
assert len(protocol['prior_executions'])==24 and qe['all_edges_structural_qualified']and len(qe['edges'])==6
assert source['exact']is True and source['approximate']is False and source['solve_calls']==1 and len(source['milestones_q12'])==7
assert e['bound_files_sha256']==e['bound_files_after_sha256']
for n,h in e['bound_files_sha256'].items():
 p=Path(n);p=p if p.is_absolute()else R/p
 assert sha(p)==h,n
post=R/'reports/P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json';p=load(post)
assert p['checks_failed']==0 and p['checks_total']==p['checks_passed']and p['status'].startswith('PASS')
entries=[]
for q in sorted((R/'results/p4_full').glob('20261015_R2_*/execution.json')):
 n=rel(q);x=load(q)
 if n in om:
  assert sha(q)==om[n]['execution_sha256'];entries.append(om[n]);continue
 entries.append({'run_id':x['run_id'],'execution':n,'execution_sha256':sha(q),'source_commit':x['source_commit'],'status':x['status'],'classification':x.get('classification'),'engineering_only':x.get('classification')=='ENGINEERING_BUILD_ONLY','wall_s':x['wall_s'],'cpu_s':x['cpu_s'],'counts':x.get('counts',{}),'authorization_budget_id':x.get('authorization_budget_id'),'formal_planning_calls':x.get('formal_planning_calls',x.get('formal_table_I_calls',x.get('zero_calls',{}).get('formal_table_I',0)))})
assert len(entries)==25 and all(next(x for x in entries if x['execution']==k)==v for k,v in om.items())
sci=[x for x in entries if not x['engineering_only']];eng=[x for x in entries if x['engineering_only']];assert len(sci)==20 and len(eng)==5
wall=math.fsum(x['wall_s']for x in entries);cpu=math.fsum(x['cpu_s']for x in entries)
ns=[load(q)for q in qp.glob('node_[0-9][0-9][0-9][0-9][0-9].json')];assert len(ns)==393
pos=max(n['closure']['position_max_abs']for n in ns);rot=max(n['closure']['rotation_matrix_max_abs']for n in ns);leaf=max(x for v in qe['edges']for x in v['leaf_distances_rad'])
lp=R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V8.json';ledger={**old,'schema':'P4_R2_RECOVERY_ACTUAL_LEDGER_V8','previous_snapshot':rel(oldp),'previous_snapshot_sha256':sha(oldp),'executions':entries,'count':25,'science_count':20,'engineering_count':5,'science_wall_s':math.fsum(x['wall_s']for x in sci),'science_cpu_s':math.fsum(x['cpu_s']for x in sci),'engineering_wall_s':math.fsum(x['wall_s']for x in eng),'engineering_cpu_s':math.fsum(x['cpu_s']for x in eng),'conservative_r2_sum_wall_s':wall,'conservative_r2_sum_cpu_s':cpu,'r2_remaining':{'wall_s':3600-wall,'cpu_s':7200-cpu},'double_counting_rule':'Each execution own cost once, all five engineering builds conservatively included. Inherited V7 entries unchanged.','new_qualification_planner_solves_in_this_snapshot':1,'total_qualification_planner_solves':2,'scope':'Added one II original RRT_NR seed7 qualification solve, its single engineering build and all393-node full path independent qualification. Not a paper performance sample.','nr_rrt_path_actual':{'execution':rel(ep),'execution_sha256':sha(ep),'status':e['status'],'source_commit':e['source_commit'],'unique_nodes':393,'milestones':7,'original_reconstruction_calls':6,'tree_vertices':source['planner_data']['num_vertices'],'tree_edges':source['planner_data']['num_edges'],'math_arm_FK_J':786,'adapter_internal_arm_FK_J':1572,'adapter_collision':393,'adapter_PQP':91176,'max_position_mm':pos,'max_rotation_matrix':rot,'max_leaf_full12_L2_rad':leaf,'personnel_independent_saved_post':rel(post),'post_sha256':sha(post),'CCD_qualified':False,'formal_statistics_sample':False},'saved_only_analysis':True,'new_scientific_calls':0}
assert ledger['formal_table_I_calls']==0 and ledger['formal_table_I_required_calls']==22500 and ledger['vi_B_remaining']['candidate_constructions']==0
with base.open(newline='')as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
assert len(rows)==211 and len(fields)==98
extra=['nr_rrt_path_status','nr_rrt_path_actual_scope','nr_rrt_path_evidence','nr_rrt_path_remaining_gate','nr_rrt_path_formal_trials','nr_rrt_path_classification','nr_rrt_path_ledger_snapshot','nr_rrt_path_saved_review']
direct={'P4-T03','P4-T03-II','P4-T05','P4-T05-II_NR','P4-T17','P4-T18','P4-T18-II_RRT_NR'}
scope=f'环境II原RRT_NR+已合格重建physical全链NR+A01 RECONSTRUCTED端点，原采样盒/Range2.6/goalBias.05/resolution.1/seed7单次solve10s；exact非approx、7milestone/55树节点54边、6次原完整回溯全true。393/393唯一节点独立闭链/原界/aligned离散碰撞通过，max位置{pos:.17g}mm、旋转矩阵{rot:.17g}、叶距{leaf:.17g}<.05；786数学FKJ/1572adapterFKJ/393collision/91176PQP。'
gate='只一条版本化原RRT_NR离散源策略合格空间路径；非作者原始端点/KDL轨迹/速度、无CCD或完整实体几何保证；其余环境/三planner/分布/投影/可见性/复杂障碍消融及全部正式500重复保持。'
ev=';'.join([rel(ep),'reports/P4_FULL_R2_ABB_RRT_NR_PATH_POST_TASK_20261016.md',rel(post),rel(lp)])
for row in rows:
 aff=row['item_id']in direct
 row.update({'nr_rrt_path_status':'PARTIAL_WITH_II_RRT_NR_DISCRETE_PATH_PASS'if aff else row['nr_local_status'],'nr_rrt_path_actual_scope':scope if aff else '本阶段该义务无新科学执行；前98列历史原字符串全保留。 '+row['nr_local_actual_scope'],'nr_rrt_path_evidence':ev if aff else row['nr_local_evidence'],'nr_rrt_path_remaining_gate':gate+' 原完整义务：'+row['original_requirement']if aff else row['nr_local_remaining_gate'],'nr_rrt_path_formal_trials':'0/22500; II_RRT_NR0/500; PCS+NR qualification solves2 nonformal','nr_rrt_path_classification':e['classification']if aff else 'NO_NEW_RESULT_FOR_THIS_OBLIGATION','nr_rrt_path_ledger_snapshot':rel(lp),'nr_rrt_path_saved_review':rel(post)if aff else 'NOT_APPLICABLE_NO_NEW_RESULT'})
cp=R/'reports/P4_FULL_R2_NR_RRT_PATH_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv';mp=cp.with_suffix('.md');assert not any(x.exists()for x in[lp,cp,mp]);new(lp,ledger)
with cp.open('x',newline='')as f:w=csv.DictWriter(f,fieldnames=fields+extra);w.writeheader();w.writerows(rows)
with cp.open(newline='')as f:after=list(csv.DictReader(f))
with base.open(newline='')as f:before=list(csv.DictReader(f))
assert[{k:r[k]for k in fields}for r in after]==before
with mp.open('x')as f:
 f.write('# P4原论文与实际复现范围：环境II原RRT_NR完整离散路径后\n\n全文仍部分完成。211行及前98列逐值继承，新增8列；全部原分母不缩。\n\n'+scope+'\n\n'+gate+f'\n\n25execution=20科学+5工程，逐自身成本一次wall{wall:.17g}/CPU{cpu:.17g}秒，R2余额{3600-wall:.17g}/{7200-cpu:.17g}秒。VI974/974余0，正式TableI0/22500，资格路径PCS+NR两次均非正式样本。\n\n完整500000投影、约50000合法点对、三planner/六环境、Fig3–5/TableI–II及全部消融保持；最终Word/PDF与双FR3适用分析待全文完成，不P2/Isaac。\n\n|ID|原完整要求|原规模|当前范围|待完成|证据|\n|---|---|---|---|---|---|\n')
 for row in rows:f.write('|'+ '|'.join(str(row[k]).replace('|','\\|').replace('\n','<br>')for k in['item_id','original_requirement','original_repeats','nr_rrt_path_actual_scope','nr_rrt_path_remaining_gate','nr_rrt_path_evidence'])+'|\n')
assert all(sha(Path(q))==h for q,h in oldhash.items())
for q in[lp,cp,mp]:
 with(O/q.name).open('xb')as f:f.write(q.read_bytes())
print(json.dumps({'ledger':rel(lp),'wall_s':wall,'cpu_s':cpu,'rows':211,'old_columns':98,'new_columns':8,'coverage':rel(cp)},ensure_ascii=False))
