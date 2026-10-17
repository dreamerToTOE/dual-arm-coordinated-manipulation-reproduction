#!/usr/bin/env python3
"""Small saved-source/AST solve delta review. No implementation import/description."""
import ast
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN='scripts/qualify_p4_full_r2_abb_sbl_pcs_solve_shadow_v2_draft.py'
SUP='scripts/supervise_p4_full_r2_abb_sbl_pcs_solve_shadow_v2_draft.py'
PRE='reports/P4_FULL_R2_ABB_SBL_PCS_SINGLE_SOLVE_SHADOW_V2_PRE_DRAFT_20261017.md'
LOCAL='scripts/qualify_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'
LOCALSUP='scripts/supervise_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'
LOCALPOST='reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST_20261017.json'
LOCALSTATIC='reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL_FIXED_SAVED_INDEPENDENT_STATIC_REVIEW_20261017.json'
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_SINGLE_SOLVE_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_20261017'
retained={};checks=[]
def read(n):
 p=Path(n);p=p if p.is_absolute()else ROOT/p;b=p.read_bytes();retained[n]=hashlib.sha256(b).hexdigest();return b
def text(n):return read(n).decode()
def load(n):return json.loads(read(n))
def ck(n,v):checks.append(dict(name=n,passed=bool(v)))
def fn(t,n):return next(x for x in ast.walk(t)if isinstance(x,ast.FunctionDef)and x.name==n)
def segment(t,n,s):return ast.get_source_segment(s,fn(t,n))
def dump(x):return ast.dump(x,include_attributes=False)
r=text(RUN);s=text(SUP);pre=text(PRE);local=text(LOCAL);ls=text(LOCALSUP);rt=ast.parse(r);lt=ast.parse(local)
for n,w in [(RUN,'a01bad83074d99e2746132505764c93b5ff7242eff946cd23956127a0d27b2f3'),(SUP,'bb15ea1e4531be9da1906623107f05114dd2c16ec05211a96e2e0557cf563c34'),(PRE,'9ee3cbf1e7cc8e6b2ea567ed6d6a65187ed97043af0ec96e7992eeb00403c5ca')]:ck('stable_final_SHA:'+n,retained[n]==w)
lp=load(LOCALPOST);oldstatic=load(LOCALSTATIC)
ck('reuse_real_local129_personnel_independent_external_pass',lp['personnel_independent']is lp['independent_local_qualified']is lp['external_supervision_qualified']is True and lp['status']=='PASS_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST'and lp['checks_total']==lp['checks_passed']==129 and lp['checks_failed']==0)
ck('reuse_local_static111_pass',oldstatic['personnel_independent']is True and oldstatic['checks_total']==oldstatic['checks_passed']==111 and oldstatic['checks_failed']==0)
ck('exact_local_sources_unchanged_as_certified',all(lp['retained_sha256'][str(ROOT/n)]==retained[n]==oldstatic['retained_sha256'][n]for n in(LOCAL,LOCALSUP)))
e=load(lp['execution']);v27=load('results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V27.json')
ck('actual_V27_contains_local_external_charge',any(x['execution']==lp['execution']and x['execution_sha256']==lp['execution_sha256']and x['external_post']==LOCALPOST and x['charged_wall_s']==lp['upper_wall_s']and x['charged_cpu_s']==lp['upper_cpu_s']for x in v27['executions']))
ck('local_true_false_same_physical109_discrete_link_reused',lp['positive_discrete_old_certificate_link']['all_new_projected_q12_match_old_independent_nodes']is True and lp['positive_discrete_old_certificate_link']['leaf_count']==108 and lp['positive_discrete_old_certificate_link']['continuous_collision_certificate']is False)
ck('only_stdlib_and_local_lifecycle_import',any(isinstance(x,ast.Import)and x.names[0].name=='qualify_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft'and x.names[0].asname=='S'for x in rt.body)and not any(isinstance(x,ast.Import)and any(y.name.startswith(('numpy','scipy'))for y in x.names)for x in rt.body))
ck('L_is_same_qualified_base_module','L=S.L' in r and "L.RUN=RUN;L.BUILD=BUILD;L.STAGE=STAGE;L.BINARY=BINARY" in r and "L.BUILD_RUN='20261017_R2_ABB_SBL_PCS_BUILD02'" in r)
ck('same_supervisor_parent_inode_proof_AST',dump(fn(rt,'supervisor_proof'))==dump(fn(lt,'supervisor_proof')))
for name in('Budget','Session'):
 c=next(x for x in rt.body if isinstance(x,ast.ClassDef)and x.name==name)
 ck(name+'_inherits_qualified_local_no_new_lifecycle',ast.unparse(c.bases[0])=='S.'+name and len(c.body)==1 and isinstance(c.body[0],ast.FunctionDef)and c.body[0].name=='__init__')
ck('Budget_only20_40_identity_override',"self.wall_cap=min(20.,3600.-spec['previous_r2_wall_s'])" in r and "self.cpu_cap=min(40.,7200.-spec['previous_r2_cpu_s'])" in r)
ck('Session_command_override_precedes_actual_start',"self.command=[target['binary'],'II',str(work),'solve',mode]" in r)
draft=segment(rt,'draft_protocol',r);validate=segment(rt,'validate',r);check=segment(rt,'check_response',r);execute=segment(rt,'execute',r)
ck('real_build_and_latest_prior_required_before_description',draft.index('built=L.build_assets(build_post);prior=L.current_prior();post=load(local_post)')<draft.index('return dict('))
ck('independent_local_and_external_actual_pass_required',all(x in draft for x in ("post['personnel_independent']is True","post['checks_total']==post['checks_passed']>0","post['status'].startswith('PASS')","post['independent_local_qualified']is True","post['external_supervision_qualified']is True")))
ck('actual_local_execution_SHA_and_latest_ledger_required',"post['execution_sha256']==sha(local_execution)" in draft and "str(local_execution.relative_to(ROOT))in prior['execution_sha256']" in draft and "e['binary_execution_calls']==4" in draft and "e['local_calls']==e['setup_calls']==4" in draft)
ck('A01_original_frozen_SHA_collision_qualified_unchanged',all(x in draft for x in ('for name,want in L.ENDPOINTS.items()',"sha(name)==want","value['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'","value['source_policy_collision_qualified']is True")))
ck('exact_single_II_seed7_point8_native10_request',"request=dict(operation='solve',environment='II',seed=7,range_rad=.8,solve_seconds=10.," in draft and 'separately_frozen_runtime_qualification=True,start_q12=points[0],goal_q12=points[1])' in draft)
ck('exact_one_trace_schedule_no_fixture',"schedule=[dict(schedule_index=0,fixture_name='single_solve',mode='trace',request=request)]" in draft and "local_calls=0,public_project_calls=0,solve_calls=1,connect_fixture_calls=0,original_solve_seconds=10." in draft)
ck('exact20_40_total3600_7200_child20',"budget=dict(wall_s=20.,cpu_s=40.,child_cpu_limit_s=20,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)" in draft)
ck('source_request_one_atomic_write_compatible',"len(json.dumps(request,separators=(',',':')).encode())+1<4096" in draft)
ck('build_local_POST_all_retained_meshes_own_current_prior_tools_bound',all(x in draft for x in ('local_bound={review_path:sha(local_post)',"for name,want in retained.items():require(sha(name)==want",'len(meshes)==20',"own={n:sha(n)for n in OWN}","prior['ledger']:prior['ledger_sha256']","str(L.OMPL):L.OMPL_SHA","'/etc/ld.so.cache'")))
ck('zero_extra_model_path_VI_formal_and_no_retry',"zero_calls=dict(compile=0,local_fixture=0,connect_fixture=0,independent_model_queries=0,old_component_requery=0,public13_project=0,VI_constructions=0,formal_table_I=0,independent_path_qualification=0),no_retry_reset_resume=True" in draft)
ck('validation_exact_recipe_boolean_and_committed_code_protocol_POST',all(x in validate for x in ("set(spec)==set(expected)","if k not in('frozen','reviews')","spec['frozen']and all(spec['reviews'].values())","['git','show',commit+':'+name]","spec['local_independent_POST']")))
ck('real_exact_nonexact_both_preserved_not_success_condition',"response['status']in('SOURCE_EXACT_PENDING_INDEPENDENT_PATH_QUALIFICATION','SOURCE_NONEXACT_RETAINED')" in check and "return 'SOURCE_SINGLE_SOLVE_OBSERVED_PENDING_INDEPENDENT_POST'" in check)
ck('one_original_setup_solve_zero_public_projection',all(x in check for x in ("response['request']==row['request']","response['setup_dispatches']==1","response['public_project_observations']==0","response['solve_calls']==1","response['source_dispatch_started']==response['source_dispatch_completed']==1")))
ck('native_exact_stays_unqualified_path_CCD',"response['independent_path_qualified']is False and response['continuous_collision_certificate']is False" in check)
ck('balanced_trace_real_live0_and_durable_outputs',all(x in check for x in ("response['source_started']==response['source_completed']","response['remaining_live_motions']==0","response['shadow_sidecar_saved_and_readback_equal']is True","response['native_output_capture_complete']is True","response['transport_evidence_saved_and_readback_equal']is True")))
ck('exclusive_single_run_no_retry_and_exact_one_dispatch',all(x in execute for x in ('not folder.exists()and not claim.exists()and not L.active_p4()',"for row in spec['schedule']:",'session.start()','session.query(',"len(responses)==1 and counts['setup_dispatched']==1",'setup_calls=1,local_calls=0,solve_calls=1'))and execute.count('session.start()')==execute.count('session.query(')==1)
ck('all_partial_exception_prefix_retained_and_STOP',"except BaseException as exc:" in execute and "record['termination_reason']=repr(exc)" in execute and "error=exc" in execute and 'if error is not None:raise error' in execute)
# The actual cleanup/final evidence lifecycle is AST-identical to qualified local,
# after the sole session count, budget values and own receipt schema substitution.
oldtry=next(x for x in fn(lt,'execute').body if isinstance(x,ast.Try));newtry=next(x for x in fn(rt,'execute').body if isinstance(x,ast.Try))
class FinalDelta(ast.NodeTransformer):
 def visit_Constant(self,node):
  if type(node.value)is float and node.value in(15.,30.):return ast.copy_location(ast.Constant({15.:20.,30.:40.}[node.value]),node)
  if node.value=='P4_R2_ABB_SBL_PCS_LOCAL01_COST_RECEIPT_V1':return ast.copy_location(ast.Constant('P4_R2_ABB_SBL_PCS_SOLVE01_COST_RECEIPT_V1'),node)
  return node
oldfinal=copy.deepcopy(oldtry.finalbody)
for x in oldfinal:
 if isinstance(x,ast.Assign)and any(isinstance(y,ast.Name)and y.id=='raw_gate'for y in x.targets):
  x.value.values[0].comparators[0]=ast.Constant(1)
oldfinal=[FinalDelta().visit(x)for x in oldfinal]
ck('cleanup_finally_AST_exact_except_one_session_20_40_schema',[dump(x)for x in oldfinal]==[dump(x)for x in newtry.finalbody])
ck('raw_stdout_stderr_exact_and_complete',"L.raw_trace(bytes(session.raw['stderr']))" in execute and "raw.endswith(b'\\n')and len(raw.splitlines())==1 and json.loads(raw)==response" in execute)
mapped=ls
for old,new in [('20261017_R2_ABB_SBL_PCS_LOCAL01','20261017_R2_ABB_SBL_PCS_SOLVE01'),('R2_RECONSTRUCTED_SAVED_TREE_FIXTURE_ORIGINAL_SBL_LAZY_CONTROL_SHADOW_V2','R2_RECONSTRUCTED_A01_ORIGINAL_SBL_PCS_SINGLE_NATIVE_SOLVE_SHADOW_V2'),('scripts/qualify_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py','scripts/qualify_p4_full_r2_abb_sbl_pcs_solve_shadow_v2_draft.py'),('EXPLICIT_FROZEN_SBL_PCS_FIXED_LOCAL_REQUIRED','EXPLICIT_FROZEN_SBL_PCS_SINGLE_SOLVE_REQUIRED'),('GNUtime child local runner+four sequential reaped fixed local sources.','GNUtime child solve runner+single reaped native solve source.'),('finite15/30','finite20/40'),('P4_R2_ABB_SBL_PCS_LOCAL_EXTERNAL_COST_CHARGE_V1','P4_R2_ABB_SBL_PCS_SOLVE_EXTERNAL_COST_CHARGE_V1'),('wall<=min(15.,','wall<=min(20.,'),('cpu<=min(30.,','cpu<=min(40.,')]:mapped=mapped.replace(old,new)
ck('supervisor_exact_port_only_identity_schema_cost_caps',mapped==s)
ck('native_unknown_connect_and_original_write_UNKNOWN_PRE','JSON null/text -1' in pre and '不回写生产字段' in pre and 'open/write/flush flags继续UNKNOWN' in pre)
ck('no_extra_fixture_retry_path_oracle_and_no_success_requirement_PRE','本项不要求成功' in pre and '零路径独立物理检查' in pre and '缺项不得添加fixture或重试' in pre)
ck('VI_archival_formal18000_unapproved_no_P2_Isaac_PRE','VI974/974仅只读存档' in pre and 'D08018000正式义务' in pre and '单独申请正式计算预算' in pre and '不进入P2/Isaac' in pre)
points=[]
for n,w in [('results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_0.json','b39d945cd5d49e4649aba22e57aae9f302694e4d8e0880389542f1ad828b112f'),('results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_1.json','991c2efe8e68add65c17375d89c89bbb637711d7125b15a34c84a19a2dc15430')]:
 endpoint=load(n);points.append(endpoint['selected_q_rad']);ck('saved_A01_endpoint_current_SHA:'+n,retained[n]==w)
request=dict(operation='solve',environment='II',seed=7,range_rad=.8,solve_seconds=10.,separately_frozen_runtime_qualification=True,start_q12=points[0],goal_q12=points[1]);size=len(json.dumps(request,allow_nan=False,separators=(',',':')).encode())+1
ck('derived_fixed_request_bytes_under4096',size<4096)
read(str(Path(__file__).relative_to(ROOT)));fail=[x for x in checks if not x['passed']]
report=dict(schema='P4_R2_ABB_SBL_PCS_SINGLE_SOLVE_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_V1',status='PASS_SINGLE_SOLVE_SHADOW_V2_INCREMENTAL_INDEPENDENT_STATIC_REVIEW'if not fail else'FAIL_SINGLE_SOLVE_SHADOW_V2_INCREMENTAL_INDEPENDENT_STATIC_REVIEW',personnel_independent=True,independent_static_review_passed=not fail,checks_total=len(checks),checks_passed=len(checks)-len(fail),checks_failed=len(fail),failures=fail,checks=checks,reviewed_source_sha256={n:retained[n]for n in(RUN,SUP,PRE)},retained_sha256=retained,saved_derived_request_bytes=size,implementation_imports=0,describe_calls=0,scientific_execution_performed=False,compiler_calls=0,binary_calls=0,new_model_queries=0,new_VI_constructions=0,formal_calls=0,limits=['Static source/AST delta only. Actual protocol description and root commit/freeze still required before the single solve.','LOCAL01 independent mechanism/external qualification is reused by exact bytes and charged V27. Lifecycle cleanup is identical except one session20/40/schema.','One original II/A01/seed7/Range.8/ten-second trace solve may succeed, return nonexact, timeout or fail. Every original result is retained without replacement or retry.','Natural checkSolution/connect and writer observations require saved-only independent POST. Exact result remains pending independent full physical path qualification, CCD and formal performance.','VI974/974 archival only. D08018000 formal budget unapproved; no P2/Isaac/FR3 execution.'])
with OUT.with_suffix('.json').open('x')as stream:json.dump(report,stream,ensure_ascii=False,allow_nan=False,indent=2);stream.write('\n')
with OUT.with_suffix('.md').open('x')as stream:stream.write('# SBL PCS 单次原生solve增量独立静审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(len(checks))+'，失败'+str(len(fail))+'。\n\n复用local129/129实际独审与V27外费。新方案仅II/A01/seed7/原Range=.8/10秒trace原solve一次，20wall/40CPU，子CPU20；继承相同Session/Budget和真实清理、双EOF、加载库与证据持久化。finally AST除单session/20和40/receipt schema外完全一致，supervisor仅身份、描述、schema与预算变化。\n\n本审未import实现、未describe/编译/二进制/模型。需要root生成最新prior协议并冻结提交。EXACT/NONEXACT/异常/超时全部保留；不能自动追加fixture/重试/路径oracle。EXACT仍待完整独立物理路径资格，connect角色UNKNOWN与原writer flags UNKNOWN保留。VI仅存档、D08018000正式预算未批准，无P2/Isaac。\n')
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(fail),failures=fail,json_sha256=hashlib.sha256(OUT.with_suffix('.json').read_bytes()).hexdigest(),md_sha256=hashlib.sha256(OUT.with_suffix('.md').read_bytes()).hexdigest()),ensure_ascii=False))
