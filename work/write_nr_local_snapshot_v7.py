"""Saved-only V7 local NR ledger and full 211-row coverage snapshot; zero science."""
from pathlib import Path
import json,csv,math,hashlib,shutil
R=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full');O=Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/outputs')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def new(p,x):
 with p.open('x')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def rel(p):return str(p.relative_to(R))
oldp=R/'results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V6.json';old=load(oldp);mapping={x['execution']:x for x in old['executions']}
base=R/'reports/P4_FULL_R2_NR_Q1_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv'
oldhash={str(p):sha(p)for p in [oldp,base,base.with_suffix('.md')]}
ep=R/'results/p4_full/20261015_R2_ABB_NR_LOCAL01/execution.json';e=load(ep)
assert e['status']=='FIXED_LOCAL_ABB_NR_QUALIFIED' and e['qualified_nontrivial_edges']==3 and e['next_planner_gate_supported'] and e['full_node_queue_checked']
assert len(e['prior_executions'])==21 and e['full_node_queue_count']==147 and not e['diagnostics'] and not e['uncompleted_node_ids'] and not e['uncompleted_top_requests']
post=R/'reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_INDEPENDENT_POST_20261015.json';p=load(post)
assert p['status']=='PASS_SAVED_EVIDENCE_AUDIT' and p['checks_total']==p['checks_passed']==218766 and p['checks_failed']==0
add=R/'reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_20261015.json';a=load(add)
assert a['status']=='PASS_RAW_LINK_ADDENDUM' and a['checks_total']==a['checks_passed']==666 and a['checks_failed']==0
assert e['bound_files_sha256']==e['bound_files_after_sha256']
for n,h in e['bound_files_sha256'].items():
 q=Path(n);q=q if q.is_absolute()else R/q
 assert sha(q)==h,n
entries=[]
for q in sorted((R/'results/p4_full').glob('20261015_R2_*/execution.json')):
 n=rel(q);x=load(q)
 if n in mapping:
  assert sha(q)==mapping[n]['execution_sha256'];entries.append(mapping[n]);continue
 entries.append({'run_id':x['run_id'],'execution':n,'execution_sha256':sha(q),'source_commit':x['source_commit'],'status':x['status'],'classification':x.get('classification'),'engineering_only':x.get('classification')=='ENGINEERING_BUILD_ONLY','wall_s':x['wall_s'],'cpu_s':x['cpu_s'],'counts':x.get('counts',{}),'authorization_budget_id':x.get('authorization_budget_id'),'formal_planning_calls':x.get('formal_planning_calls',x.get('formal_table_I_calls',x.get('zero_calls',{}).get('formal_table_I',0)))})
assert len(entries)==22 and all(next(x for x in entries if x['execution']==k)==v for k,v in mapping.items())
sci=[x for x in entries if not x['engineering_only']];eng=[x for x in entries if x['engineering_only']];assert len(sci)==18 and len(eng)==4
wall=math.fsum(x['wall_s']for x in entries);cpu=math.fsum(x['cpu_s']for x in entries)
assert math.fsum(x['wall_s']for x in entries if x['run_id']!=e['run_id'])==e['previous_r2_wall_s']
assert math.fsum(x['cpu_s']for x in entries if x['run_id']!=e['run_id'])==e['previous_r2_cpu_s']
lp=R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V7.json'
ledger={**old,'schema':'P4_R2_RECOVERY_ACTUAL_LEDGER_V7','previous_snapshot':rel(oldp),'previous_snapshot_sha256':sha(oldp),'executions':entries,'count':22,'science_count':len(sci),'engineering_count':len(eng),'science_wall_s':math.fsum(x['wall_s']for x in sci),'science_cpu_s':math.fsum(x['cpu_s']for x in sci),'engineering_wall_s':math.fsum(x['wall_s']for x in eng),'engineering_cpu_s':math.fsum(x['cpu_s']for x in eng),'conservative_r2_sum_wall_s':wall,'conservative_r2_sum_cpu_s':cpu,'r2_remaining':{'wall_s':3600-wall,'cpu_s':7200-cpu},'double_counting_rule':'Each execution own cost once; four engineering builds included conservatively, no cumulative fields. All inherited V6 entries unchanged.','scope':'Added original NR GD/SVC/RBS fixed local interface only and its single engineering build; no new planner solve or performance statistics.','new_qualification_planner_solves_in_this_snapshot':0,'previous_snapshot_qualification_planner_solves':old['new_qualification_planner_solves_in_this_snapshot'],'nr_local_actual':{'execution':rel(ep),'execution_sha256':sha(ep),'source_commit':e['source_commit'],'status':e['status'],'top_completed':20,'logical_pairs':10,'unique_nodes':147,'nontrivial_edges':3,'math_arm_FK_J':294,'adapter_internal_arm_FK_J':588,'adapter_collision':147,'source_trace_GD':286,'source_trace_PQP':33150,'adapter_PQP':34052,'plain_internal':'UNOBSERVED','personnel_independent_saved_post':rel(post),'post_sha256':sha(post),'raw_link_addendum':rel(add),'raw_link_sha256':sha(add),'saved_post_lossless_archive':'reports/P4_FULL_R2_ABB_NR_LOCAL_SAVED_POST_ARCHIVE_20261016.json','next_planner_gate_supported_II':True,'global_planning_qualified':False},'saved_only_analysis':True,'new_scientific_calls':0}
assert ledger['formal_table_I_calls']==0 and ledger['formal_table_I_required_calls']==22500 and ledger['vi_B_consumed']['candidate_constructions']==974 and ledger['vi_B_remaining']['candidate_constructions']==0
with base.open(newline='')as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
assert len(fields)==90 and len(rows)==211
extra=['nr_local_status','nr_local_actual_scope','nr_local_evidence','nr_local_remaining_gate','nr_local_formal_trials','nr_local_classification','nr_local_ledger_snapshot','nr_local_saved_review']
direct={'P4-T03','P4-T03-II','P4-T03-III','P4-T05','P4-T05-II_NR'}
scope='II/III四A01端点及II首PCS保存全部三边原NR RBS/回溯，plain/trace20顶层全部完成；3/3非平凡边、147/147完整唯一节点通过。原回溯65/65/17节点，最大叶距.04769340858982442<.05；max闭链位置9.887878832159913e-6mm/旋转2.5558390071012127e-8。普通NR无PCS分支/固定主动链门。'
gate='仅固定有限原GD/SVC/RBS资格；RECONSTRUCTED physical NR不冒称原KDL轨迹。环境II原RRT真实路径尚待，III RBS及其余环境、全部三planner/分布/投影/局部可见性/复杂窄通道/消融/正式统计保持。'
evidence=';'.join([rel(ep),'reports/P4_FULL_R2_ABB_NR_LOCAL_POST_TASK_20261015.md',rel(post),rel(add),rel(lp)])
for row in rows:
 aff=row['item_id']in direct
 row.update({'nr_local_status':'PARTIAL_WITH_FIXED_LOCAL_NR_PASS'if aff else row['nr_q1_status'],'nr_local_actual_scope':scope if aff else '本阶段此义务无新增科学执行；前90列全部历史原字符串保留。 '+row['nr_q1_actual_scope'],'nr_local_evidence':evidence if aff else row['nr_q1_evidence'],'nr_local_remaining_gate':gate+' 原完整义务：'+row['original_requirement']if aff else row['nr_q1_remaining_gate'],'nr_local_formal_trials':'0/22500; local solve=0; prior PCS qualification solve=1 nonformal','nr_local_classification':e['classification']if aff else 'NO_NEW_RESULT_FOR_THIS_OBLIGATION','nr_local_ledger_snapshot':rel(lp),'nr_local_saved_review':'218766+666 personnel-independent saved checks PASS; 0new science'if aff else 'NOT_APPLICABLE_NO_NEW_RESULT'})
cp=R/'reports/P4_FULL_R2_NR_LOCAL_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv';mp=cp.with_suffix('.md')
assert not any(q.exists()for q in[lp,cp,mp]);new(lp,ledger)
with cp.open('x',newline='')as f:w=csv.DictWriter(f,fieldnames=fields+extra);w.writeheader();w.writerows(rows)
with cp.open(newline='')as f:after=list(csv.DictReader(f))
with base.open(newline='')as f:before=list(csv.DictReader(f))
assert [{k:r[k]for k in fields}for r in after]==before
with mp.open('x')as f:
 f.write('# P4原论文与实际复现范围：NR局部接口资格后\n\n全文仍部分完成。211行与前90列逐值原样继承，追加8列；原文所有规模保持。\n\n'+scope+'\n\n'+gate+'\n\n22execution=18科学+4工程；逐自身实耗一次：wall '+repr(wall)+' / CPU '+repr(cpu)+'秒。R2余额'+repr(3600-wall)+' / '+repr(7200-cpu)+'秒。VI974/974余0，正式TableI0/22500，500000投影、约50000点对、全部Fig3–5/TableI–II/消融均保留。\n\n审计为0新科学，218766+666人员独立保存检查全通过；大JSON无损gzip与SHA manifest保全，原文件本地保持。尚未开始正式大规模实验，不P2/Isaac。\n\n|ID|原完整要求|原规模|当前范围|待完成|证据|\n|---|---|---|---|---|---|\n')
 for row in rows:
  cols=[row[k]for k in['item_id','original_requirement','original_repeats','nr_local_actual_scope','nr_local_remaining_gate','nr_local_evidence']]
  f.write('|'+ '|'.join(str(v).replace('|','\\|').replace('\n','<br>')for v in cols)+'|\n')
assert all(sha(q)==h for q,h in oldhash.items())
for q in[lp,cp,mp]:
 with (O/q.name).open('xb')as f:f.write(q.read_bytes())
print(json.dumps({'ledger':rel(lp),'wall_s':wall,'cpu_s':cpu,'preserved_rows':211,'preserved_columns':90,'new_columns':8,'coverage':rel(cp)},ensure_ascii=False))
