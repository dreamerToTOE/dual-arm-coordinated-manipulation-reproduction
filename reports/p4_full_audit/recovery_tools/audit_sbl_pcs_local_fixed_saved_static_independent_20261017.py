#!/usr/bin/env python3
"""Independent saved-byte/AST review only; never import implementation modules."""
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL_FIXED_SAVED_INDEPENDENT_STATIC_REVIEW_20261017'
FIX='configs/p4_full/r2_abb_sbl_pcs_local_fixed_saved_v1.draft.json'
PRE='reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL_FIXED_SAVED_PRE_DRAFT_20261017.md'
RUN='scripts/qualify_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'
SUP='scripts/supervise_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'
BASE='scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py'
BASESUP='scripts/supervise_p4_full_r2_abb_sbl_pcs_setup_draft.py'
SETUPPOST='reports/P4_FULL_R2_ABB_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST_20261017.json'
BUILDPOST='reports/P4_FULL_R2_ABB_SBL_PCS_BUILD02_SAVED_INDEPENDENT_POST_20261017.json'
MERGED='reports/P4_FULL_R2_ABB_SBL_PCS_SHADOW_V2_MERGED_INDEPENDENT_STATIC_REVIEW_20261017.json'
QUEUE='results/p4_full/20261015_R2_ABB_CBIRRT_D_PATH01/complete_original_saved_queue.json'
PATHPOST='reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_20261016.json'
SELECT='reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL_FIXED_SAVED_SELECTION_STATIC_20261017.json'
IDENTIFY='/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning/validity_checkers/StateValidityCheckerPCS.cpp'
SBL='/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning/planners/SBL_PCS.cpp'
retained={};checks=[]
def path(n):
 p=Path(n);return p if p.is_absolute() else ROOT/p
def read(n):
 p=path(n);raw=p.read_bytes();retained[n]=hashlib.sha256(raw).hexdigest();return raw
def text(n):return read(n).decode()
def load(n):return json.loads(read(n))
def ck(n,ok):checks.append(dict(name=n,passed=bool(ok)))
def exact(a,b):return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,allow_nan=False,separators=(',',':'))
def fn(tree,name):return next(x for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name)
def src(tree,name,raw):return ast.get_source_segment(raw,fn(tree,name))
def bitvector(a,b):return len(a)==len(b) and all(struct.pack('>d',float(x))==struct.pack('>d',float(y))for x,y in zip(a,b))

f=load(FIX);pre=text(PRE);r=text(RUN);s=text(SUP);b=text(BASE);bs=text(BASESUP)
rt=ast.parse(r);st=ast.parse(s);bt=ast.parse(b)
for n,expected in [(FIX,'4f3dc390920e0ca8e6a7441ced345d2f99305219b689753a96cc57509800e5ff'),(PRE,'01929fd4b153021dc2f12cb1ed3135b641f724df8d11cf40428d76a9d50e984c'),(RUN,'a3fa3463fe4a7d683806ae82c9f418fc39bf9fa12c8c78d3e563c8fe991f1dd4'),(SUP,'3b420f24e731a4510ceb3153f0367bf2561a73b7b282971bb505843b74a848ea')]:
 ck('exact_final_draft_SHA:'+n,retained[n]==expected)
setup=load(SETUPPOST);built=load(BUILDPOST);merged=load(MERGED)
ck('reuse_actual_setup_9534_independent_pass',setup['personnel_independent'] is True and setup['checks_total']==setup['checks_passed']==9534 and setup['checks_failed']==0 and setup['external_supervision_qualified'] is True)
ck('reuse_setup_lifecycle_exact_current_bytes',all(setup['retained_sha256'][str(path(n))]==retained[n] for n in (BASE,BASESUP)))
ck('reuse_actual_BUILD02_13186_independent_pass',built['personnel_independent'] is True and built['checks_total']==built['checks_passed']==13186 and built['checks_failed']==0 and built['engineering_build_qualified'] is True and built['external_supervision_qualified'] is True)
ck('reuse_merged_engineering_62_independent_pass',merged['personnel_independent'] is True and merged['checks_total']==merged['checks_passed']==62 and merged['checks_failed']==0)
for n,want in merged['retained_sha256'].items():
 if n in ('baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_shadow_v2_draft.cpp','baselines/p4_full/geometry_consistent/abb_sbl_pcs_observation_draft.hpp','baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_shadow_v2_draft.py'):
  read(n);ck('reuse_engineering_current_SHA:'+n,retained[n]==want)
q=load(QUEUE);post=load(PATHPOST);selection=load(SELECT)
ck('old_queue_exact_SHA',retained[QUEUE]=='38ce4780897186fadff49f15cec239008df237b519deb9d16ddbac73eedb852f')
ck('old_independent_path_certificate_reuse',post['checks_total']==post['checks_passed']==58152 and post['checks_failed']==0 and post['personnel_independent'] is True and post['independent_path_qualified'] is True and post['continuous_collision_certificate'] is False and post['retained_sha256'][QUEUE]==retained[QUEUE])
ck('fixture_draft_not_frozen_and_RECONSTRUCTED',f['frozen'] is False and f['draft_not_runtime_protocol'] is True and f['classification']=='RECONSTRUCTED_TREE_FIXTURE_ORIGINAL_SBL_METHOD_BODIES')
ck('exact_budget_and_four_process_scope',f['budget']==dict(wall_s=15.,cpu_s=30.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.) and f['fixture_count']==2 and f['maximum_source_processes']==f['maximum_original_lazy_calls']==4)
ck('fixture_zero_other_science',all(f[k]==0 for k in ('source_model_queries','new_sampling','maximum_solve_calls','maximum_connect_fixture_calls','project_public13_calls','new_VI_candidate_constructions')))
ck('exact_four_order',[(x['fixture_name'],x['mode'],x['schedule_index'])for x in f['schedule']]==[('positive','trace',0),('positive','plain',1),('negative','trace',2),('negative','plain',3)])
ck('positive_old_full_edge_zero_109',q['edges'][0]['node_ids']==list(range(109)) and q['edges'][0]['active_chain']==0 and q['edges'][0]['branch']==3)
ident=text(IDENTIFY);sbl=text(SBL)
ck('source_IK0_is_passive_arm2',ident.index('if (ik[0] == -1)')<ident.index('ik[0] = get_valid_IK_solutions_indices_2(i)'))
ck('source_IK1_is_passive_arm1',ident.index('if (ik[1] == -1)')<ident.index('ik[1] = get_valid_IK_solutions_indices_1(i)'))
lazy=sbl[sbl.index('bool ompl::geometric::SBL::isPathValid('):sbl.index('ompl::geometric::SBL::Motion* ompl::geometric::SBL::selectMotion')]
ck('native_lazy_branch_equal_guards_before_RBS_remove',all(x in lazy for x in ('parent->ik_q1_active == mpath[i]->ik_q1_active','parent->ik_q2_active == mpath[i]->ik_q2_active','removeMotion(tree, mpath[i]);','mpath[i]->valid = true;')))
ck('native_recursive_remove_nulls_children_then_removes', 'motion->children[i]->parent = nullptr;\n\t\tremoveMotion(tree, motion->children[i]);' in sbl)
for name,ids,roles in [('positive',[0,108],[0,0]),('negative',[0,359,360],[0,1,1])]:
 fixture=f['fixtures'][name]
 ck(name+'_exact_saved_node_ids_roles',[(x['saved_node_id'],x['assigned_active_role'])for x in fixture['start_chain']]==list(zip(ids,roles)))
 ck(name+'_lazy_reconstructed_and_unfrozen',fixture['kind']=='lazy_chain' and fixture['classification']=='RECONSTRUCTED_TREE_FIXTURE_ORIGINAL_SBL_METHOD_BODIES' and fixture['separately_frozen_local_fixture'] is False)
 for ref in fixture['saved_input_references']:
  read(ref['path']);ck(name+'_source_reference:'+ref['path'],retained[ref['path']]==ref['sha256'])
 for node in fixture['start_chain']:
  index=node['saved_node_id'];prefix='results/p4_full/20261015_R2_ABB_CBIRRT_D_PATH01/node_'+str(index).zfill(5)
  old=load(prefix+'.json');oldmath=load(prefix+'_math.json')
  ck(name+'_node_'+str(index)+'_q12_binary64_saved',bitvector(node['q12'],q['nodes'][index]) and bitvector(node['q12'],old['q12']) and bitvector(node['q12'],oldmath['q12']))
  ck(name+'_node_'+str(index)+'_old_qualification',old['qualified'] is True and old['math_qualified'] is True and old['stage']=='COMPLETED' and old['limits']['legal'] is True and old['collision']['collision'] is False and old['collision']['selected_variant']=='aligned')
  ck(name+'_node_'+str(index)+'_true_branch_order',old['branches']==oldmath['branches'] and all(x['unique'] is True and len(x['branch_set'])==1 for x in old['branches']) and node['ik']==[old['branches'][1]['branch_set'][0],old['branches'][0]['branch_set'][0]])
  ck(name+'_node_'+str(index)+'_old_edge_role',index in q['edges'][node['saved_edge_index']]['node_ids'] and any(x['edge']==node['saved_edge_index'] and x['role']==node['assigned_active_role'] and x['branch_pass'] is True for x in old['edge_assignments']))
  for ref in node['source_provenance']:
   read(ref['path']);ck(name+'_node_'+str(index)+'_reference:'+ref['path'],retained[ref['path']]==ref['sha256'])
ck('positive_true_shared_branches',[x['ik']for x in f['fixtures']['positive']['start_chain']]==[[3,0],[3,0]])
ck('negative_true_both_branch_mismatch',[x['ik']for x in f['fixtures']['negative']['start_chain']]==[[3,0],[0,3],[0,3]])
distance=math.dist(*[x['q12']for x in f['fixtures']['positive']['start_chain']])
ck('positive_full12_distance_nontrivial',distance>0.05 and math.isclose(distance,2.8088399720774073,rel_tol=0,abs_tol=1e-15))
request_sizes=[]
for i,row in enumerate(f['schedule']):
 req=row['request'];fixture=f['fixtures'][row['fixture_name']]
 ck('request_'+str(i)+'_II_seed7_range_point8_A01',req['operation']=='local' and req['environment']=='II' and req['seed']==7 and req['range_rad']==.8 and bitvector(req['start_q12'],q['nodes'][0]) and bitvector(req['goal_q12'],q['nodes'][-1]))
 compact={k:copy.deepcopy(fixture[k])for k in ('kind','fixture_id','separately_frozen_local_fixture','saved_input_references')}
 compact['start_chain']=[{k:node[k]for k in ('q12','ik','assigned_active_role','saved_node_id','saved_edge_index')}for node in fixture['start_chain']]
 ck('request_'+str(i)+'_exact_compact_fixture',exact(req['fixture'],compact) and req['separately_frozen_runtime_qualification'] is False)
 frozen=copy.deepcopy(req);frozen['separately_frozen_runtime_qualification']=True;frozen['fixture']['separately_frozen_local_fixture']=True
 size=len(json.dumps(frozen,separators=(',',':'),allow_nan=False).encode())+1;request_sizes.append(size);ck('request_'+str(i)+'_single_write_under4096',size<4096)
ck('selection_report_current_only_reused_not_personnel_certificate',selection['personnel_independent'] is False and selection['checks_total']==selection['checks_passed']==35 and selection['checks_failed']==0 and all(selection['source_sha256'][n]==retained[n]for n in (FIX,PRE,QUEUE,PATHPOST)))
ck('new_runner_only_stdlib_and_qualified_lifecycle_imports',set(x.names[0].name for x in rt.body if isinstance(x,ast.Import))=={'argparse','base64','copy','hashlib','json','math','os','signal','subprocess','time','qualify_p4_full_r2_abb_sbl_pcs_setup_draft'})
assigns=[ast.unparse(x.targets[0])for x in rt.body if isinstance(x,ast.Assign)and isinstance(x.targets[0],ast.Attribute)and isinstance(x.targets[0].value,ast.Name)and x.targets[0].value.id=='L']
ck('only_four_explicit_L_identity_mutations',assigns==['L.RUN','L.BUILD','L.STAGE','L.BINARY','L.BUILD_RUN'])
ck('BUILD02_identity_is_explicit',"L.BUILD_RUN='20261017_R2_ABB_SBL_PCS_BUILD02'" in r and "abb_sbl_pcs_shadow_v2" in r)
session=next(x for x in rt.body if isinstance(x,ast.ClassDef)and x.name=='Session');sessioninit=src(session,'__init__',r)
ck('Session_constructor_has_no_dispatch_before_command_override',sessioninit.index('super().__init__')<sessioninit.index("self.command=[target['binary'],'II',str(work),'local',mode]") and 'subprocess.' not in src(next(x for x in bt.body if isinstance(x,ast.ClassDef)and x.name=='Session'),'__init__',b))
ck('aggregate_budget_15_30_reuses_live_cpu_timer',"self.wall_cap=min(15.,3600.-spec['previous_r2_wall_s'])" in r and "self.cpu_cap=min(30.,7200.-spec['previous_r2_cpu_s'])" in r and 'class Budget(L.Budget)' in r)
draft=src(rt,'draft_protocol',r);validate=src(rt,'validate',r);execute=src(rt,'execute',r);check=src(rt,'check_response',r);semantic=src(rt,'semantic',r)
ck('build_POST_and_current_prior_before_protocol',draft.index('built=L.build_assets(build_post);prior=L.current_prior()')<draft.index('return dict('))
buildassets=src(bt,'build_assets',b)
ck('reused_build_assets_identity_compatible_with_BUILD02',"execution=ROOT/'results/p4_full'/BUILD_RUN/'execution.json'" in buildassets and "e['run_id']==BUILD_RUN" in buildassets and "e['binary']==str(BINARY)" in buildassets and "post['status'].startswith('PASS')" in buildassets and 'BUILD01' not in buildassets)
current=src(bt,'current_prior',b)
ck('current_prior_latest_integerV_excludes_this_RUN',"max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1]))" in current and 'if p.parent.name!=RUN' in current and 'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS' in current and 'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING' in current)
ck('independent_fixture_review_exact_current_config_PRE_SHA',all(x in draft for x in ("review['personnel_independent']is True","review['checks_total']==review['checks_passed']>0","for name in (FIXTURE,PRE)",'FIXTURE_REVIEW_CURRENT_ASSET_SHA_REQUIRED')))
ck('only_declared_frozen_booleans_changed',"schedule=copy.deepcopy(fixture['schedule'])" in draft and "request['separately_frozen_runtime_qualification']=True;request['fixture']['separately_frozen_local_fixture']=True" in draft)
ck('protocol_binds_original_refs_meshes_own_review_prior_and_tools',all(x in draft for x in ('source_refs','len(meshes)==20',"own={n:sha(n)for n in OWN}","review_path:sha(fixture_post)","prior['ledger']:prior['ledger_sha256']","str(L.OMPL):L.OMPL_SHA","'/usr/bin/time'","'/etc/ld.so.cache'")))
ck('exact_current_recipe_frozen_boolean_and_committed_source_guards',all(x in validate for x in ("set(spec)==set(expected)","if k not in('frozen','reviews')","spec['frozen']and all(spec['reviews'].values())","['git','show',commit+':'+name]")))
ck('exclusive_no_retry_current_RUN_guard',all(x in execute for x in ('not folder.exists()and not claim.exists()and not L.active_p4()','durable_new(claim','for row in spec[\'schedule\']:',"len(responses)==4 and counts['setup_dispatched']==4")))
ck('one_start_and_query_no_retry_loop',execute.count('session.start()')==1 and execute.count('session.query(')==1 and execute.index('session.query(')<execute.index('session.finish(normal=True)')<execute.index("if row['mode']=='trace'"))
ck('check_balanced_dispatch_local_and_zero_other_calls',all(x in check for x in ("response['request']==row['request']","response['setup_dispatches']==1","response['public_project_observations']==response['solve_calls']==0","response['source_dispatch_started']==response['source_dispatch_completed']==1")))
ck('check_fixed_true_false_tree_counts_and_lifetime',all(x in check for x in ("local['source_isPathValid_returned']is expected['source_isPathValid_returned']","local[phase]['native_tree_sizes']==expected[f'native_tree_sizes_{phase}']","response['remaining_live_motions']==0")))
ck('check_all5_native_files_absent_sidecar_durable',all(x in check for x in ("response['writer_metadata_attempts']==[]","response['shadow_sidecar_saved_and_readback_equal']is True","response['transport_evidence_saved_and_readback_equal']is True","len(response['native_file_evidence'])==5","all(not f['exists']and f['absence_retained']is True")))
ck('trace_positive_nontrivial_negative_noRBS_two_removes',all(x in check for x in ("a==b and a.get('isPathValid')==1","rbs>=2 and a.get('removeMotion',0)==0","rbs==0 and a.get('removeMotion')==2","response['trace']is None and response['source_started']is None")))
ck('semantic_compares_full_nodes_metadata_and_attempts',all(x in semantic for x in ("for phase in ('before','after')","sorted(t['nodes'],key=lambda x:x['motion_id'])","response['setup_metadata']","response['writer_metadata_attempts']")) and "L.exact(value,semantics[row['fixture_name']])" in execute)
ck('raw_stdout_stderr_exact_and_complete',all(x in execute for x in ("L.raw_trace(bytes(session.raw['stderr']))","response['trace']or []","raw.endswith(b'\\n')and len(raw.splitlines())==1 and json.loads(raw)==response")))
ck('real_STOP_cleanup_reap_raw_gate_and_all_current_hashes',all(x in execute for x in ("except BaseException as exc:","record['termination_reason']=repr(exc)",'budget.close()','L.kill_source_group(s.proc)','s.finish(normal=False)','p.wait(timeout=1.)','s.after_reap_group==[]','all(s.pipe_EOF_observed.values())',"record['bound_files_after_sha256']",'PRIOR_CHANGED','PRELOAD_CHANGED','MAPPED_ELF_CHANGED')))
ck('retains_raw_streams_partial_failures_diagnostics_and_external_tail',all(x in execute for x in ("for channel,raw in s.raw.items()",'os.fsync(f.fileno())',"record['diagnostics']=diagnostics",'STOP_FINAL_WALL_OR_CPU_BUDGET','STOP_CLEANUP_OR_EVIDENCE_ERROR','UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED')))
ck('main_description_has_no_execution_and_exact_paths_from_protocol',all(x in src(rt,'main',r)for x in ("if args.describe_protocol:","print(json.dumps(draft_protocol(args.build_post,args.fixture_post),ensure_ascii=False,indent=2));return","if args.validate_draft:validate(spec,protocol);print('STATIC_LOCAL_DRAFT_VALIDATED_NO_EXECUTION');return")))
mapped=bs
for old,new in [('20261017_R2_ABB_SBL_PCS_SETUP01','20261017_R2_ABB_SBL_PCS_LOCAL01'),('R2_RECONSTRUCTED_A01_ORIGINAL_SBL_PCS_SETUP_PUBLIC_LINEAR_ACTION_OBSERVATION_ONLY','R2_RECONSTRUCTED_SAVED_TREE_FIXTURE_ORIGINAL_SBL_LAZY_CONTROL_SHADOW_V2'),('scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py','scripts/qualify_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'),('EXPLICIT_FROZEN_SBL_PCS_SETUP_REQUIRED','EXPLICIT_FROZEN_SBL_PCS_FIXED_LOCAL_REQUIRED'),('GNUtime child setup runner+single reaped setup source.','GNUtime child local runner+four sequential reaped fixed local sources.'),('finite10/20','finite15/30'),('P4_R2_ABB_SBL_PCS_SETUP_EXTERNAL_COST_CHARGE_V1','P4_R2_ABB_SBL_PCS_LOCAL_EXTERNAL_COST_CHARGE_V1'),('wall<=min(10.,','wall<=min(15.,'),('cpu<=min(20.,','cpu<=min(30.,')]:mapped=mapped.replace(old,new)
ck('supervisor_identical_except_declared_identity_text_caps',mapped==s)
ck('supervisor_real_inode_exclusive_time_and_exact_sources',all(x in s for x in ('os.O_WRONLY|os.O_CREAT|os.O_EXCL','pass_fds=(fd,)','time_inode_unchanged=identity_unchanged',"spec['own_source_sha256']",'completed_process_exit0')))
ck('PRE_explicit_limits_and_independent_POST_before_solve','无 connect fixture' in pre and '不重做13点 projection' in pre and '尚未由本PRE授权' in pre and 'VI974/974只读存档' in pre and '不代表连续碰撞' in pre)
v26=load('results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V26.json')
ck('current_saved_prior_V26_contains_actual_BUILD02',any(x['execution']=='results/p4_full/20261017_R2_ABB_SBL_PCS_BUILD02/execution.json'and x['execution_sha256']==built['execution_sha256']for x in v26['executions']))
read(str(Path(__file__).relative_to(ROOT)))
failed=[x for x in checks if not x['passed']]
report=dict(schema='P4_R2_ABB_SBL_PCS_LOCAL_FIXED_SAVED_INDEPENDENT_STATIC_REVIEW_V1',status='PASS_FIXED_LOCAL_SAVED_FIXTURE_AND_INCREMENTAL_RUNTIME_STATIC_REVIEW'if not failed else 'FAIL_FIXED_LOCAL_SAVED_FIXTURE_AND_INCREMENTAL_RUNTIME_STATIC_REVIEW',personnel_independent=True,checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),failures=failed,checks=checks,retained_sha256=retained,request_bytes_after_two_frozen_booleans=request_sizes,positive_saved_full12_distance=distance,reused_certificates=dict(setup=SETUPPOST,engineering_BUILD02=BUILDPOST,merged_engineering_static=MERGED,old_complete_discrete_path=PATHPOST),review_scope='Only fixed saved input and new four-local runner/supervisor delta. Qualified SETUP01 lifecycle bodies are unchanged and reused by exact SHA.',scientific_execution_performed=False,implementation_imports=0,describe_calls=0,compiler_calls=0,binary_calls=0,new_model_queries=0,new_VI_constructions=0,formal_calls=0,qualification_granted='STATIC_ONLY_ROOT_FREEZE_AND_REAL_EXECUTION_POST_STILL_REQUIRED',independent_saved_POST_requirements=['Check actual before/after per-lifetime full node q12, branch, shadow roles, valid and parent/child ancestry. Positive child must become valid; negative child and grandchild must be truly retired with parent-null-before-delete evidence.','Check actual balanced source events, nontrivial positive RBS and no negative RBS, removeMotion=2; compare full plain/trace node and setup semantics.','Independently validate all raw streams, durable native absence/sidecars, process exit0/EOF/empty reaped groups and GNUtime inode/cost upper bounds.','Local reconstructed fixture qualification is not a physical end-to-end SBL path, native checkSolution/connect/writer qualification, continuous collision certificate or planning/performance result.'])
with OUT.with_suffix('.json').open('x')as stream:json.dump(report,stream,ensure_ascii=False,allow_nan=False,indent=2);stream.write('\n')
md='\n'.join(['# SBL PCS 固定保存输入与局部运行增量独立静审','',report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'，失败'+str(report['checks_failed'])+'。','', '固定正例 node0→108、负例 node0→359→360，保留原 q12 与真实 SBL 分支；负例 ancestry 明示 RECONSTRUCTED。四请求为 positive trace/plain、negative trace/plain，各一次原 setup，合计 15wall/30CPU，R2总额3600/7200。冻结后紧凑请求字节数：'+str(request_sizes)+'。','', '复用 SETUP01 9534项、BUILD02 13186项、工程静审62项、旧CBi完整离散路径58152项的现有证书；本审只核新增固定输入与runner/supervisor增量。共用生命周期两文件当前SHA与SETUP01证书一致。supervisor仅身份/描述/schema/15和30上限发生指定变化。','', 'L.build_assets按BUILD_RUN/STAGE/BINARY识别BUILD02，Session构造不派发，命令在start前改为local；current_prior读取最新整数V账本并排除本RUN，已保存V26包含BUILD02。root执行describe/freeze前仍须确认账本没有新成本。','', '未import实现、未describe、未编译、未运行源二进制或模型。这里只允许静态通过，仍待root冻结提交与实际执行及人员独立POST。实际POST必须检查正例child valid、负例真正递归退役与null-before-delete、完整节点语义、四次trace/plain、EOF/reap/group、全量原始证据和外部成本。local成功不代替checkSolution/connect/writer、连续碰撞、端到端路径或正式统计。','', '失败项：'+json.dumps(failed,ensure_ascii=False),''])
with OUT.with_suffix('.md').open('x')as stream:stream.write(md)
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),json_sha256=hashlib.sha256(OUT.with_suffix('.json').read_bytes()).hexdigest(),md_sha256=hashlib.sha256(OUT.with_suffix('.md').read_bytes()).hexdigest(),failures=failed),ensure_ascii=False))
