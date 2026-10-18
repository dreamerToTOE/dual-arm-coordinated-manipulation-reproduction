#!/usr/bin/env python3
"""Saved evidence and AST-only TAIL02 incremental review; no runner import."""
from pathlib import Path
import ast
from datetime import datetime, timezone
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_PATH_TAIL02_INDEPENDENT_STATIC_REVIEW_20261018'
R='scripts/qualify_p4_full_r2_abb_sbl_pcs_path_tail02_draft.py'
S='scripts/supervise_p4_full_r2_abb_sbl_pcs_path_tail02_draft.py'
P='reports/P4_FULL_R2_ABB_SBL_PCS_PATH_TAIL02_PRE_DRAFT_20261018.md'
OLD='scripts/qualify_p4_full_r2_abb_sbl_pcs_path_draft.py'
ORIGINAL='scripts/qualify_p4_full_r2_abb_rrt_path.py'
PREFIX='reports/P4_FULL_R2_ABB_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json'
PRIOR_STATIC='reports/P4_FULL_R2_ABB_SBL_PCS_PATH_INDEPENDENT_STATIC_REVIEW_20261018.json'
V='scripts/p4_d080/supervise_v_pcs_build_v1_draft.py'
checks=[];reviewed={}

def read(n,want=None):
    p=Path(n);p=p if p.is_absolute()else ROOT/p
    b=p.read_bytes();h=hashlib.sha256(b).hexdigest();reviewed[n]=h
    if want is not None:ck('fixed reviewed SHA '+n,h==want)
    return b
def js(n,want=None):return json.loads(read(n,want))
def ck(n,p):checks.append(dict(check=n,passed=bool(p)))
def fn(t,n):return next(v for v in t.body if isinstance(v,(ast.FunctionDef,ast.ClassDef))and v.name==n)
def dump(n):return ast.dump(n,include_attributes=False)
def part(s,t,n):return ast.get_source_segment(s,fn(t,n))
def loop(t):return next(n for n in ast.walk(fn(t,'execute'))if isinstance(n,ast.For)and isinstance(n.target,ast.Tuple)and [getattr(x,'id',None)for x in n.target.elts]==['i','q'])

r=read(R,'efd7895bbef81ca2f11045636baa0bab56966a93052da0e7d8d03770870e7596').decode()
s=read(S,'e667fc1491a5d419b882bc22ee5b5d11591ad6c6b23305e1aef96827898b28a2').decode()
p=read(P,'6b11b4eb78bb778713f7454365f1b677fec357cdb020fbe6215208e190f10350').decode()
old=read(OLD,'8f0d063b620366c6df69d6de9e3154b072fb466bd388897e0b5be02de3d44a86').decode()
original=read(ORIGINAL,'bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865').decode()
v=read(V).decode()
rt,st,ot,pt,vt=[ast.parse(x)for x in(r,s,old,original,v)]
ck('all reviewed Python files parse with no runner/model import',True)
prior=js(PRIOR_STATIC,'1896714d85a154d760d3266581641e271109ee7d7be9cd6dd4b120dd781a5979')
ck('reuse prior full queue static62 without rerunning saved-array negatives',prior['checks_total']==prior['checks_passed']==62 and prior['checks_failed']==0 and prior['personnel_independent']is True and prior['new_model_or_scientific_calls']==0)
for n in('source_provenance','current_prior','validate','supervisor_proof'):
    ck('unchanged prior reviewed function AST '+n,dump(fn(rt,n))==dump(fn(ot,n)))
rl,ol,pl=loop(rt),loop(ot),loop(pt)
ck('physical node loop body exact AST with both qualified source versions',[dump(x)for x in rl.body]==[dump(x)for x in ol.body]==[dump(x)for x in pl.body])
ck('physical node loop body exact source lines',r.splitlines()[rl.body[0].lineno-1:rl.end_lineno]==old.splitlines()[ol.body[0].lineno-1:ol.end_lineno]==original.splitlines()[pl.body[0].lineno-1:pl.end_lineno])
count=lambda t:next(n for n in ast.walk(fn(t,'execute'))if isinstance(n,ast.FunctionDef)and n.name=='counted')
ck('original FK/J wrapper exact AST',dump(count(rt))==dump(count(ot))==dump(count(pt)))
ck('only loop iterator changed to fixed original node IDs',ast.unparse(rl.iter)=="((i, spec['fixed_queue']['nodes'][i]) for i in spec['execution_node_ids'])" and "EXECUTION_NODE_IDS=list(range(262,387))"in r)
tail=list(range(262,387));prefix=list(range(262))
ck('fixed saved prefix and executed tail disjoint and exhaustive387',not set(prefix)&set(tail)and prefix+tail==list(range(387))and len(tail)==125)
ck('complete queue persists without truncation and original node IDs retained',"durable_new(folder/'complete_original_saved_queue.json',spec['fixed_queue'])"in r and "original_queue==queue and original['fixed_queue']==queue"in r and "completed_original_node_ids=[r['node_id']for r in results]"in r)
ck('tail only completion predicate cannot promote a partial tail',"require([r['node_id']for r in results]==spec['execution_node_ids'],'COMPLETE_FIXED_TAIL_REQUIRED')"in r and "full_tail_checked=[r['node_id']for r in results]==spec['execution_node_ids'],full_queue_checked=False"in r)
ck('unchanged scientific gates and qualified original source hash',"'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5"in r and "'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon"in r and reviewed[ORIGINAL]in r)
post=js(PREFIX,'e2fb37a5d63e5219395baedef7630c386893ea13aa07e9bcc0777aa8316b75b4')
ck('reuse exact independent262 prefix PASS and never promote original STOP',post['personnel_independent']is True and post['checks_total']==post['checks_passed']==35 and post['checks_failed']==0 and post['saved_prefix_qualified']is True and post['partial_path_prefix_qualified']is True and post['independent_prefix_node_ids']==post['independently_saved_qualified_node_ids']==prefix and post['remaining_unverified_node_ids']==tail and post['independent_path_qualified']is False and post['scientific_run_within_local_budget']is False and post['execution_cap_breach_retained']is True)
ck('runner pins prefix cert and requires complete pass and exact original execution',reviewed[PREFIX]in r and "post=bind(files,PREFIX_POST,PREFIX_POST_SHA)"in r and "post['checks_total']==post['checks_passed']"in r and "post['checks_failed']==0"in r and "post['execution_sha256']==PREFIX_EXEC_SHA"in r)
pe=js('results/p4_full/20261018_R2_ABB_SBL_PCS_PATH01/execution.json',post['execution_sha256'])
ck('original execution remains STOP261 final with262 real collision completions',pe['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET'and pe['completed_nodes']==pe['qualified_nodes']==261 and pe['counts']['collision_calls_completed']==262 and pe['diagnostics']==[])
ck('original failure semantics explicitly enforced by new runner',"e['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET'and e['completed_nodes']==261"in r and "e['counts']['collision_calls_completed']==262"in r and "'ORIGINAL_PATH01_STOP_MUST_REMAIN_UNCHANGED'"in r and "new_physical_queries_for_prefix=0"in r)
q=js(post['source_full_queue'],post['source_full_queue_sha256'])
ck('same immutable original complete saved queue387',len(q['nodes'])==387 and len(q['edges'])==5 and q['original_dense_path_node_count']==387 and max(d for e in q['edges']for d in e['leaf_distances_rad'])<.05)
ck('all prefix retained evidence bound without recomputing physical or arrays',"for name,want in post['retained_sha256'].items():bind(files,name,want)"in r and "source_full_queue_sha256"in r and "prefix_provenance(queue,files)"in r)
cache=post['post_run_loader_cache_drift'];actual_cache=hashlib.sha256(Path('/etc/ld.so.cache').read_bytes()).hexdigest()
ck('sole cache exception exact historical/current pair independently certified',cache['path']=='/etc/ld.so.cache'and cache['historical_sha256']=='306f8fef1055e6d8c8de8a0dbcd0c8a38cbf29f1748cf83dcfb6bd2efead67de'and cache['current_sha256']==actual_cache and cache['execution_after_matches_historical']is True and bool(cache['dpkg_evidence'])and bool(cache['mtime_UTC']))
ck('bind exception limited exact cache path and fixed independent cert',"if want is not None and actual!=want and path(name)==Path('/etc/ld.so.cache'):"in r and "require(sha(PREFIX_POST)==PREFIX_POST_SHA"in r and "evidence['historical_sha256']==want"in r and "evidence['current_sha256']==actual"in r and "else:require(want is None or actual==want,'P_BOUND_HASH_CHANGED '+name)"in r and "files[name]=actual"in r)
ck('work80/160 reserves10/20 inside total90/180 and cumulative3600/7200',"budget=dict(wall_s=90.,cpu_s=180.,work_wall_s=80.,work_cpu_s=160.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)"in r and "self.wall_cap=min(80.,3600.-spec['previous_r2_wall_s']-10.);self.cpu_cap=min(160.,7200.-spec['previous_r2_cpu_s']-20.)"in r and "resource.setrlimit(resource.RLIMIT_CPU,(180,180))"in r)
ck('per-tail250 mathFK125 collision500 adapterFK caps and all scientific generation0',"n=len(EXECUTION_NODE_IDS)"in r and "max_math_arm_FK=2*n,max_collision_calls=n,max_adapter_internal_arm_FK_J=4*n"in r and "zero_calls=dict(IK=0,NR=0,projection=0,RBS=0,solve=0,RNG=0,VI_constructions=0,formal_table_I=0)"in r)
ck('fresh exclusive run claim artifact refusal and committed frozen review admission',all(x in r for x in("'EXCLUSIVE_P_NO_RETRY_RESET_OR_RESUME'","'OTHER_ACTIVE_P4_EXECUTION'","subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)==path(n).read_bytes()","require(spec['frozen']and all(spec['reviews'].values())"))and "'OLD_SUPERVISION_ARTIFACT_NO_RETRY'"in s and "os.O_WRONLY|os.O_CREAT|os.O_EXCL"in s)
ck('independent raw native/aligned collision policy and full worker cleanup reused',"collision_adapter_v3/manifest.json"in r and "sorted(r['variant']for r in entries)==['aligned','native']"in r and "entry['mesh_sha256'].items()"in r and "worker_gate=(len(processes)==counts['collision_worker_started']==2"in r and "'STOP_WORKER_EOF_EXIT_OR_REGISTRY_UNQUALIFIED'"in r)
envelope=lambda src:src[src.index('        timing_valid=False;'):src.index('        payload=dict(')]
ck('complete three-observation Decimal envelope byte identical reviewed V supervisor',envelope(s)==envelope(v))
ck('Decimal math retains exact terms maximum then single final conversion',all(x in s for x in("elapsed,user,system=(Decimal(v)for v in fields[:3])","values=[Decimal(str(v))for v in(fallback_wall,fallback_cpu,","walls=[elapsed+Decimal('.01'),values[0]+Decimal('.01'),values[2]+Decimal('.01')]","cpus=[user+system+Decimal('.02'),values[1]+Decimal('.02'),values[3]+Decimal('.02')]","wall=float(max(walls));cpu=float(max(cpus));envelope_valid=True")))
ck('incomplete observations never qualify envelope or local cap',"timing_valid and execution.is_file() and saved['execution_sha256']==sha(execution)"in s and "bool(timing_valid and envelope_valid and identity_unchanged and wall<=min(90.,3600.-spec['previous_r2_wall_s'])"in s and "'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'"in s)
ck('raw time outer and receipt separately preserved with exact SHA and components',all(x in s for x in("raw_GNUtime_upper_wall_s=raw_wall,raw_GNUtime_upper_cpu_s=raw_cpu","fallback_observed_outer_wait_wall_s=fallback_wall,fallback_reaped_children_CPU_s=fallback_cpu","receipt_sha256=sha(receipt)if receipt.is_file()else None","monotonic_envelope_components=components","time_inode_unchanged=identity_unchanged")))
ck('STOP and incomplete cleanup evidence dominate any physical pass',"record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'"in r and "if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'"in r and "record['terminal_receipt_status']=receipt['status']"in r and "if error is not None:raise error"in r)
scope=js('configs/p4_d080/execution_scope_v1.json')
ck('D080 I-V only with VI archival and formal0/18000 unapproved',scope['allowed_environments']==['I','II','III','IV','V']and scope['VI_future_science_authorized']is False and scope['formal_table_I_D080']==18000 and scope['formal_execution_authorized']is False and "formal_table_I_original=22500,formal_table_I_D080=18000,formal_calls=0,VI_new_calls=0"in r)
ledgers=list((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'));lp=max(ledgers,key=lambda x:int(x.stem.rsplit('V',1)[1]));ledger=js(str(lp.relative_to(ROOT)))
actual={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest()for x in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if x.parent.name!='20261018_R2_ABB_SBL_PCS_PATH_TAIL02'}
wall=math.fsum(x.get('charged_wall_s',x['wall_s'])for x in ledger['executions']);cpu=math.fsum(x.get('charged_cpu_s',x['cpu_s'])for x in ledger['executions'])
ck('latest ledger covers every current execution and exact conservative sums',{x['execution']:x['execution_sha256']for x in ledger['executions']}==actual and wall==ledger['conservative_r2_sum_wall_s']and cpu==ledger['conservative_r2_sum_cpu_s'])
ck('new fixed90/180 qualification fits unexpanded R2 total',wall+90<=3600 and cpu+180<=7200)
ck('each new protocol describes latest actual ledger and refuses orphan attempts',"'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS'"in r and "'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED'"in r and "'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING '"in r)
ck('fresh target execution and claim absent',not(ROOT/'results/p4_full/20261018_R2_ABB_SBL_PCS_PATH_TAIL02').exists()and not(ROOT/'results/p4_full/P4_R2_ABB_SBL_PCS_PATH_TAIL02_262_TO386_90W_180CPU_20261018.claim.json').exists())
ck('PRE explicitly preserves STOP and0 new prefix source calls',all(x in p for x in('261','262','125','90','180','80/160','Decimal','不重新solve/RBS/reconstruct/投影','原历史SHA与首版FAIL永久保留','不称其为完整系统费用','不VI/P2/Isaac')))
for n,h in list(reviewed.items()):
    f=Path(n);f=f if f.is_absolute()else ROOT/f
    ck('reviewed evidence/source unchanged '+n,hashlib.sha256(f.read_bytes()).hexdigest()==h)
failed=[x for x in checks if not x['passed']]
report=dict(schema='P4_SBL_PCS_PATH_TAIL02_INCREMENTAL_INDEPENDENT_STATIC_REVIEW_V1',status='PASS_SBL_PCS_TAIL02_INCREMENTAL_STATIC_REVIEW'if not failed else'FAIL_STATIC_REVIEW',generated_at_utc=datetime.now(timezone.utc).isoformat(),personnel_independent=True,reviewer='sbl_independent_resume',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,reviewed_sha256=reviewed,reused_prior_full_queue_static_POST=PRIOR_STATIC,reused_prefix_POST=PREFIX,physical_loop_body_AST_and_source_unchanged=True,fixed_full_queue_nodes=387,reused_independently_saved_prefix_nodes=262,new_fixed_original_tail_node_ids=tail,new_fixed_original_tail_nodes=125,current_prior=dict(ledger=str(lp.relative_to(ROOT)),execution_count=len(actual),wall_s=wall,cpu_s=cpu),new_runner_model_import_scientific_compile_describe_calls=0,independent_path_qualified=False,execution_authorization='Root unique describe, freeze latest prior and commit, then one original fixed125 tail execution under90wall/180CPU. No generation or retry.',reviewed_execute_adaptation_whitelist=['run/schema/classification/PRE identity','prefix certificate and exact saved queue provenance','fixed original tail262..386 iteration/completion identity','work80/160 plus10/20 reserve inside90/180 caps and unchanged cumulative3600/7200','conservative external Decimal three-observation envelope and separately retained raw observations'],limits=['Static increment only; unchanged physical prefix262 reused by exact independent certificate, not rerun.','PATH01 original STOP261 final and cap breach/cache first FAIL remain immutable.','Full387 discrete path remains unqualified until unique tail execution and independent saved-only combined POST.','No continuous collision or solid-rod/omitted-pair safety/performance/formal statistics claim; VI archival only.'])
for suffix in('.json','.md'):
    if OUT.with_suffix(suffix).exists():raise FileExistsError(OUT.with_suffix(suffix))
with OUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
with OUT.with_suffix('.md').open('x')as f:
    f.write('# SBL PCS TAIL02 增量独立静审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'，失败'+str(report['checks_failed'])+'。\n\n原完整387节点及已保存独审262点不重算；仅原262–386共125点。物理loop主体源码及AST、FK/J wrapper与已验源完全相同。原闭链/分支/限位/原离散collision门不变；仅固定tail索引、prefix接缝、预算和费用监督薄适配。\n\n工作80wall/160CPU，收尾预留10/20，总帽90/180，仍受累计3600/7200约束。外费用用GNUtime、outer、receipt三观测精确Decimal加padding取最大值。原PATH01 STOP、实际帽超限、261 final/262保存物理点、首版cache FAIL均保留；新cache必须匹配独立时序证书，其它资产不得漂移。\n\n本审查只读源/AST/保存证书；模型导入、describe、编译及科学运行均0。root仍需冻结最新账本并commit后唯一执行tail，完成保存后组合独审才可认定完整离散路径。未证明CCD、正式统计或PCS优势；VI只读，正式18000未获启动授权。\n')
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),output=str(OUT.with_suffix('.json').relative_to(ROOT)))))
if failed:raise SystemExit(1)
