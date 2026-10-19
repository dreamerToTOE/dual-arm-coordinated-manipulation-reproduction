"""Saved-file only; no numerical/project modules, no scientific calls.
Create new V6 and 211-row snapshot only after final independent POST is supplied.
"""
import argparse,csv,hashlib,json,math
from pathlib import Path
R=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
O=Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/outputs')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def new(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def rel(p):return str(p.relative_to(R))
def check_hashes(items):
 for name,want in items.items():
  p=Path(name);p=p if p.is_absolute() else R/p
  assert sha(p)==want,(str(p),'SHA_MISMATCH')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--post-review',required=True,type=Path)
 a=ap.parse_args();post=a.post_review.resolve();assert post.is_file();postdata=load(post)
 postmd=post.with_suffix('.md');assert postmd.is_file()
 # Explicit independent POST gate supplied after root notification, never a guessed PASS.
 assert postdata.get('status') in ('PASS_INDEPENDENT_SAVED_POST_REVIEW',),('UNRECOGNIZED_INDEPENDENT_POST_STATUS',postdata.get('status'))
 oldp=R/'results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V5.json';old=load(oldp);oldmap={x['execution']:x for x in old['executions']}
 base=R/'reports/P4_FULL_R2_ABB_RRT_PCS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv'
 oldhash={str(p):sha(p) for p in [oldp,base,base.with_suffix('.md')]}
 qp=R/'results/p4_full/20261015_R2_NR_ABB_Q1_01';e=load(qp/'execution.json');protocol=load(R/e['protocol'])
 assert e['status']=='PASS_FIXED64_NUMERICAL_TRANSFER' and e['source_commit']=='c68fa7605a94eb07f7588e850b95980b62bc0c8f'
 assert all(e[k]==64 for k in ['comparison_cases','comparison_passed','history_cases','history_passed','independent_final_cases','independent_final_qualified','cpp_converged_cases','python_converged_cases'])
 assert e['soundness_passed'] is True and e['not_projection_capability_pass'] is True
 assert not e['inflight_unreturned_call'] and all(not v for v in e['uncompleted_case_ids'].values()) and not e['diagnostics']
 assert e['bound_files_sha256']==e['bound_files_after_sha256'];check_hashes(e['bound_files_sha256'])
 assert sha(R/e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256'];assert sha(R/e['claim'])==e['claim_sha256']==e['claim_after_sha256']
 assert protocol['frozen'] and all(protocol['reviews'].values()) and len(protocol['fixed_cases'])==64
 assert all(v==0 for v in e['zero_calls'].values())
 cs=e['counts']
 for variant in ['cpp_plain','cpp_trace']:
  assert all(cs[variant+'_'+s]==64 for s in ['dispatch_attempted','dispatched','responses_retained','completed'])
 assert all(cs['python_original_'+s]==64 for s in ['dispatch_attempted','dispatched','responses_retained','completed'])
 assert cs['python_original_arm_FK_J_started']==cs['python_original_arm_FK_J_completed']==864
 assert cs['independent_final_arm_FK_J_started']==cs['independent_final_arm_FK_J_completed']==128
 assert cs['independent_final_metric_started']==cs['independent_final_metric_completed']==64
 summary=load(qp/'comparison_summary.json');history=load(qp/'history_diagnostics.json')
 assert summary['all64_completed'] and len(summary['comparisons'])==len(summary['independent_final'])==len(history)==64
 assert all(x['all_passed'] for x in history)
 comparisons=[];physical=[];plain=[];trace=[];py=[]
 for i,case in enumerate(protocol['fixed_cases']):
  comp=load(qp/f'comparison_{i:03d}.json');fin=load(qp/f'independent_final_{i:03d}.json')
  assert comp==summary['comparisons'][i] and fin==summary['independent_final'][i]
  assert comp['case_id']==fin['case_id']==case['case_id'] and comp['all_passed'] and comp['plain_trace_exact_non_cost_equality']
  assert fin['physical_qualified'] and fin['soundness_passed'] and fin['closed'] and fin['limits_legal'] and not fin['collision_checked'] and not fin['branch_or_fixed_active_gate']
  assert fin['metrics']['translation_max_abs']<=1e-5 and fin['metrics']['rotation_matrix_max_abs']<=1e-5
  for group,dest in [('cpp_plain',plain),('cpp_trace',trace),('python_worker',py)]:
   row=load(qp/f'{group}_{i:03d}_raw_response.json');assert row['request']['case_id']==case['case_id'];dest.append(row)
  comparisons.append(comp);physical.append(fin)
 assert all({k:v for k,v in p['result'].items() if k not in ('trace','wall_s')}=={k:v for k,v in t['result'].items() if k not in ('trace','wall_s')} for p,t in zip(plain,trace))
 trace_checks=sum(len(x['result']['trace']) for x in trace);updates=sum(x['result']['accepted_updates'] for x in trace)
 maxpos=max(x['metrics']['translation_max_abs'] for x in physical);maxrot=max(x['metrics']['rotation_matrix_max_abs'] for x in physical)
 minlimit=min(x['minimum_limit_margin_rad'] for x in physical)
 error_max={}
 for row in comparisons:
  for chk in row['checks']:
   assert chk['passed']
   if chk.get('max_abs_error') is not None:
    k=chk['check'];k=k.split('.',1)[-1] if k.startswith('iteration') else k
    error_max[k]=max(error_max.get(k,0.),chk['max_abs_error'])
 paths=sorted((R/'results/p4_full').glob('20261015_R2_*/execution.json'));entries=[]
 assert len(paths)==20
 for p in paths:
  name=rel(p);x=load(p)
  if name in oldmap:
   assert sha(p)==oldmap[name]['execution_sha256'];entries.append(oldmap[name]);continue
  entries.append({'run_id':x['run_id'],'execution':name,'execution_sha256':sha(p),'source_commit':x['source_commit'],'status':x['status'],'classification':x.get('classification'),'engineering_only':x.get('classification')=='ENGINEERING_BUILD_ONLY','wall_s':x['wall_s'],'cpu_s':x['cpu_s'],'counts':x.get('counts',{}),'authorization_budget_id':x.get('authorization_budget_id'),'formal_planning_calls':x.get('formal_planning_calls',x.get('formal_table_I_calls',x.get('zero_calls',{}).get('formal_table_I',0)))})
 assert all(next(x for x in entries if x['execution']==k)==v for k,v in oldmap.items())
 s=[x for x in entries if not x['engineering_only']];g=[x for x in entries if x['engineering_only']];assert len(s)==17 and len(g)==3
 wall=math.fsum(x['wall_s'] for x in entries);cpu=math.fsum(x['cpu_s'] for x in entries)
 assert math.fsum(x['wall_s'] for x in entries if x['run_id']!=e['run_id'])==e['previous_r2_wall_s']
 assert math.fsum(x['cpu_s'] for x in entries if x['run_id']!=e['run_id'])==e['previous_r2_cpu_s']
 ledger={**old,'schema':'P4_R2_RECOVERY_ACTUAL_LEDGER_V6','previous_snapshot':rel(oldp),'previous_snapshot_sha256':sha(oldp),'executions':entries,'count':len(entries),'science_count':len(s),'engineering_count':len(g),'science_wall_s':math.fsum(x['wall_s'] for x in s),'science_cpu_s':math.fsum(x['cpu_s'] for x in s),'engineering_wall_s':math.fsum(x['wall_s'] for x in g),'engineering_cpu_s':math.fsum(x['cpu_s'] for x in g),'conservative_r2_sum_wall_s':wall,'conservative_r2_sum_cpu_s':cpu,'r2_remaining':{'wall_s':3600-wall,'cpu_s':7200-cpu},'double_counting_rule':'Each execution own cost once; all three engineering builds conservatively included. No cumulative fields. Old V5 and all18 inherited entries unchanged.','new_qualification_planner_solves_in_this_snapshot':0,'previous_snapshot_qualification_planner_solves':old['new_qualification_planner_solves_in_this_snapshot'],'scope':'Added only II/III fixed64 C++ physical full-NR numerical transfer qualification plus its one-target engineering build; no RBS/planner/global capability/fair speed qualification. Prior II original RRT_PCS discrete path unchanged.','nr_q1_actual':{'execution':rel(qp/'execution.json'),'execution_sha256':sha(qp/'execution.json'),'status':e['status'],'classification':e['classification'],'top_level_NR_completed':192,'independent_final_metrics_completed':64,'python_original_arm_FK_J_started_completed':864,'independent_final_arm_FK_J_started_completed':128,'cpp_internal_started_completed_counts':e['cpp_internal_started_completed_counts'],'independent_saved_post':rel(post),'independent_saved_post_sha256':sha(post),'source_commit':e['source_commit'],'not_projection_capability_pass':True},'saved_only_analysis':True,'new_scientific_calls':0}
 ledger['nr_q1_actual']['independent_saved_post_md']=rel(postmd)
 ledger['nr_q1_actual']['independent_saved_post_md_sha256']=sha(postmd)
 assert ledger['formal_table_I_calls']==0 and ledger['formal_table_I_required_calls']==22500 and ledger['vi_B_consumed']['candidate_constructions']==974 and ledger['vi_B_remaining']['candidate_constructions']==0
 lp=R/'results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V6.json'
 cp=R/'reports/P4_FULL_R2_NR_Q1_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv';mp=cp.with_suffix('.md')
 with base.open(newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 assert len(fields)==81 and len(rows)==211
 extra=['nr_q1_status','nr_q1_actual_scope','nr_q1_evidence','nr_q1_remaining_gate','nr_q1_formal_trials','nr_q1_classification','nr_q1_ledger_snapshot','nr_q1_independent_saved_review','nr_q1_frozen_numerical_gates']
 direct={'P4-T03','P4-T03-II','P4-T03-III'}
 scope=f'新增II/III历史固定64输入的物理全链NR C++移植资格；C++plain/trace及原Python各64，共192顶层NR，64逐步数值对照/64历史重放/64终态闭链原界均通过；每份C++64共{trace_checks}次迭代检查/{updates}更新，plain/trace逻辑数值精确一致。独立终态max位置{maxpos:.17g}mm、旋转矩阵{maxrot:.17g}、最小源界margin{minlimit:.17g}rad。Python原迭代864+终态128 armFK/J实测进入完成；C++内部计数UNOBSERVED。'
 evidence=';'.join([rel(qp/'execution.json'),rel(qp/'comparison_summary.json'),rel(qp/'history_diagnostics.json'),rel(post),rel(postmd),rel(lp)])
 gates=json.dumps(protocol['comparison_gates'],ensure_ascii=False,sort_keys=True,separators=(',',':'))
 gate='仅已保存II/III固定近邻64数值移植，不是原KDL轨迹/任意ambient投影能力/碰撞资格/公平速度/RBS/GD接缝/planner PASS；其余环境普通NR、真实原接口/RBS/三搜索器及Fig3–5/TableI–II完整统计均待。旧失败保留、不得外推NR全局优势。'
 for row in rows:
  affected=row['item_id'] in direct
  row.update({'nr_q1_status':'PARTIAL_WITH_II_III_FIXED64_TRANSFER_PASS' if affected else row['rrt_pcs_e2e_status'],'nr_q1_actual_scope':scope if affected else '本阶段无该义务新增科学执行；前81列历史范围逐值保留。 '+row['rrt_pcs_e2e_actual_scope'],'nr_q1_evidence':evidence if affected else row['rrt_pcs_e2e_evidence'],'nr_q1_remaining_gate':gate+' 原完整义务：'+row['original_requirement'] if affected else row['rrt_pcs_e2e_remaining_gate'],'nr_q1_formal_trials':'0/22500; current Q1 solve=0, collision=0, RBS=0; prior RRT_PCS qualification solve=1 remains nonformal','nr_q1_classification':e['classification'] if affected else 'NO_NEW_RESULT_FOR_THIS_OBLIGATION','nr_q1_ledger_snapshot':rel(lp),'nr_q1_independent_saved_review':'FIXED64_TRANSFER_PASS / '+rel(post) if affected else 'NOT_APPLICABLE_NO_NEW_QUALIFICATION'})
  row['nr_q1_frozen_numerical_gates']=gates if affected else 'NOT_APPLICABLE_NO_NEW_QUALIFICATION'
 # Finish all validation before creating the three immutable deliverables.
 assert all(not p.exists() for p in [lp,cp,mp])
 new(lp,ledger)
 with cp.open('x',newline='') as f:writer=csv.DictWriter(f,fieldnames=fields+extra);writer.writeheader();writer.writerows(rows)
 with cp.open(newline='') as f:written=list(csv.DictReader(f))
 with base.open(newline='') as f:before=list(csv.DictReader(f))
 assert [{k:r[k] for k in fields} for r in written]==before
 def esc(s):return str(s).replace('|','\\|').replace('\n','<br>')
 intro=f'''# P4最新原论文与实际复现范围对照表：II/III固定64 NR数值移植资格

全文仍PARTIAL。211完整义务与所有原分母不变，CSV继承前81列全部211×81个原字符串及顺序，追加9列（含冻结数值门）；V5及前表不改。

{scope}

{gate}

独立保存证据审查：`{rel(post)}`（SHA256 `{sha(post)}`），文本`{rel(postmd)}`（SHA256 `{sha(postmd)}`）。冻结数值门：`{gates}`。原本体/参数/输入与跨语言数值门未放宽；这不是新增原R1/R2几何研究，也不替换旧失败。Q1零IK/碰撞/RBS/RNG/solve/VI构造；正式TableI仍0/22500（45cell×500、原1000s）。此前II seed7原RRT_PCS的177/177源策略离散路径保持，不升级为完整几何/CCD或统计。

20execution=17科学+3工程，own-cost各一次：wall{wall:.17g}s、CPU{cpu:.17g}s；R2余额{3600-wall:.17g}/{7200-cpu:.17g}s。Q1自身wall{e['wall_s']:.17g}s/CPU{e['cpu_s']:.17g}s，工程另计。VI B974/974，构造余额0。V6账SHA256 `{sha(lp)}`。本表纯保存文件分析，0新科学调用。

尚未执行的新GD/RBS/planner与两个source-correction候选均不得冒充PASS。完整Fig3–5/TableI–II、500000投影/50000点对、PCS被动链数量/局部可见性/复杂障碍/窄通道/固定链消融仍待；P4完成后中文Word/PDF与双FR3适用分析保留，提交最新全范围表给用户审查，不自动进入P2或Isaac。

|ID|原文完整要求|原规模|最新状态|实际范围与证据|尚未完成|证据路径|
|---|---|---|---|---|---|---|
'''
 with mp.open('x') as f:
  f.write(intro)
  for row in rows:f.write('|'+ '|'.join(esc(row[k]) for k in ['item_id','original_requirement','original_repeats','nr_q1_status','nr_q1_actual_scope','nr_q1_remaining_gate','nr_q1_evidence'])+'|\n')
 assert all(sha(p)==v for p,v in oldhash.items())
 for p in [lp,cp,mp]:
  target=O/p.name
  with target.open('xb') as f:f.write(p.read_bytes())
  assert sha(target)==sha(p)
 print(json.dumps({'ledger':rel(lp),'ledger_sha256':sha(lp),'wall_s':wall,'cpu_s':cpu,'remaining':ledger['r2_remaining'],'science_count':len(s),'engineering_count':len(g),'coverage':rel(cp),'csv_sha256':sha(cp),'md_sha256':sha(mp),'preserved_rows':211,'preserved_columns':81,'new_columns':len(extra),'trace_checks':trace_checks,'updates':updates,'max_physical_position_mm':maxpos,'max_physical_rotation_matrix':maxrot,'min_limit_margin_rad':minlimit,'comparison_error_maxima':error_max,'output_copy_names':[lp.name,cp.name,mp.name]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
