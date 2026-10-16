#!/usr/bin/env python3
"""Independent saved/source-only review of one fixed S draft; no runner import."""
from pathlib import Path
import ast
import hashlib
import json
import math
import struct

ROOT=Path(__file__).resolve().parents[3]
RUNNER='scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_draft.py'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_draft.py'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE_PRE_DRAFT_20261016.md'
DESIGN='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE_RUNNER_DESIGN_PRE_DRAFT_20261016.md'
EXPECTED={RUNNER:'7f0327f56bb86246d22f897743b0b2abad6fd54e9527eb0a55e79fdbe4589a46',
 SUPERVISOR:'b4c25d0dcb91a7c79efbc5ee0e341e60bd0c2ec068dd3cc1224b4cfe7f135834',
 PRE:'ccf9ec7cd130f1d4aef3e3a2604aa052b90638e6771d3011e37ee58174b586fc',
 DESIGN:'ad23f19ed6cc74e5f1c178935a4e556e83896eb2969abdac411fc678f645ca09'}

def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def load(n):return json.loads((ROOT/n).read_text())
def bits(q):return struct.pack('>'+str(len(q))+'d',*q).hex()

def main():
 checks=[];retained={};failures=[]
 def ck(name,ok,evidence):
  row=dict(id=name,passed=bool(ok),evidence=evidence);checks.append(row)
  if not ok:failures.append(row)
 def bind(n,want=None):
  retained[n]=sha(n)
  if want is not None:ck('exact_source_'+n,retained[n]==want,want)
 for n,want in EXPECTED.items():bind(n,want)
 r=(ROOT/RUNNER).read_text();s=(ROOT/SUPERVISOR).read_text();p=(ROOT/PRE).read_text()
 rt=ast.parse(r);st=ast.parse(s)
 ck('both_python_AST_parse',isinstance(rt,ast.Module)and isinstance(st,ast.Module),'ast.parse only; no compile/import')
 functions={n.name:ast.get_source_segment(r,n)for n in rt.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
 def has(name,part,tokens):ck(name,all(t in part for t in tokens),tokens)
 has('missing_actual_L_rejects_before_protocol',functions['prerequisites'],[
  "old.path(L_DIR+'/execution.json').is_file()",'old.path(L_POST).is_file()',
  'WAIT_ACTUAL_D_SPLIT_AND_LOCAL02_INDEPENDENT_POST_NO_PLACEHOLDER_PROTOCOL'])
 has('known_D_L_orphan_charge_guard',functions['prerequisites'],[
  'for run in(tail.RUN,Path(L_DIR).name)',"'.supervision.charge.json').is_file()or(prefix/'execution.json').is_file()",
  'KNOWN_D_OR_L_ORPHAN_SUPERVISION_CHARGE_REQUIRES_AUTHORITATIVE_ACCOUNTING'])
 has('D_exact_independent_split_contract',functions['prerequisites'],[
  'sha(D_POST)==D_POST_SHA',"d['schema']=='P4_TAIL02_SAVED_INDEPENDENT_AGGREGATE_POST_V1'",
  "d['checks_total']==d['checks_passed']==1374","d['aggregate_actual_responses']==64",
  "d['aggregate_source_processes']==9","d['aggregate_plain_trace_pairs']==32","d['original_single_run_PASS']is False",
  "de['completed_new_dispatch_ids']==[62,63]","de['UNKNOWN_new_dispatch_ids']==[]"])
 has('L_exact_schema_actual_PASS_and_independence',functions['prerequisites'],[
  "lp['schema']=='P4_LOCAL02_SAVED_INDEPENDENT_POST_V1'",
  "lp['status']=='PASS_LOCAL02_SAVED_DISCRETE_SEAM_INDEPENDENT_POST'",
  "lp['personnel_independent']is True","lp['external_supervision_qualified']is True",
  "lp['checks_total']==lp['checks_passed']and lp['checks_total']>0 and lp['checks_failed']==0",
  "lp['execution_sha256']==sha(L_DIR+'/execution.json')",
  "le['status']=='PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED'"])
 required=('actual12_all_true','six_plain_trace_pairs_binary64_equal',
  'complete_three_M_binary64_equal_saved80_65_34','two_SVC_zero_CBi_zero_direct_rng',
  'raw_EOF_and_all_processes_reaped_exit0','old177_complete_discrete_certificate_reused',
  'external_cost_and_identity_qualified','original_D64_STOP_and_H_STOP_preserved')
 assignment=next(n for n in ast.walk(rt)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='required'for t in n.targets))
 ck('exact_eight_L_required_gate_names',ast.literal_eval(assignment.value)==required,required)
 has('L_all_eight_gates_strict_AND_no_status_OR',functions['prerequisites'],[
  "set(lp.get('required_gates',{}))==set(required)","all(lp['required_gates'][k]is True for k in required)"])
 has('D_L_full_original_files_rebound',functions['prerequisites'],[
  "e['bound_files_sha256']==e['bound_files_after_sha256']","sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']",
  "sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256']","files.update(audit['retained_sha256'])",
  "for n,h in files.items():require(sha(n)==h"])
 has('latest_authoritative_ledger_actual_execution_set',functions['current_prior'],[
  "max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1]))",
  "{r['execution']:r['execution_sha256']for r in saved['executions']}==actual"])
 has('charged_cost_replaces_internal_once',functions['current_prior'],[
  "math.fsum(r.get('charged_wall_s',r['wall_s'])for r in saved['executions'])",
  "math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in saved['executions'])",
  "wall==saved['conservative_r2_sum_wall_s']","cpu==saved['conservative_r2_sum_cpu_s']"])
 has('prior_external_certificates_bound',functions['current_prior'],[
  "sha(r['external_post'])==r['external_post_sha256']","post['personnel_independent']is True",
  "post['external_supervision_qualified']is True","post['execution_sha256']==r['execution_sha256']",
  "post['upper_wall_s']==r['charged_wall_s']","post['upper_cpu_s']==r['charged_cpu_s']",
  "sha(r['external_time'])==r['external_time_sha256']==post['external_time_sha256']",
  'RETAINED_UNKNOWN; CHARGED_REMAINING_IS_UPPER_BOUND'])
 has('frozen_binary_and_twenty_meshes_only',functions['draft_protocol'],[
  'assets=old.build_assets()',"assets['targets']['distance_destination_fix']['stage']",
  "require(len(meshes)==20","runtime_meshes_sha256=meshes","'/usr/bin/time':sha('/usr/bin/time')"])
 has('fixed_S_scope_and_caps',functions['draft_protocol'],[
  'wall_s=30.,cpu_s=60.,child_cpu_limit_s=60,r2_total_wall_s=3600.,r2_total_cpu_s=7200.',
  'new_processes=1,source_requests=1,solve_calls=1,source_seed=7,source_solve_seconds=10.',
  'old_distance_requery=0,local_seam_requery=0,VI_constructions=0,formal_table_I=0'])
 has('committed_source_and_exact_current_protocol_required',functions['validate'],[
  'expected=draft_protocol()',"set(spec)==set(expected)","spec['frozen']and all(spec['reviews'].values())",
  "['git','ls-files','--error-unmatch',n]","['git','status','--porcelain','--',n]",'COMMIT_BLOB_MISMATCH'])
 has('source_argv_II_solve_trace_and_CPU60',functions['Session'],[
  "self.command=[target['binary'],'II',str(work),'solve','trace']",'resource.setrlimit(resource.RLIMIT_CPU,(60,60))'])
 has('signal_mask_covers_Popen_and_registry',functions['Session'],[
  'signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})',
  'self.budget.processes.append(self.proc)',"signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)"])
 has('one_small_request_no_retry_raw_before_parse',functions['Session'],[
  'require(len(raw)<4096',"require(sent==len(raw),'INCOMPLETE_REQUEST_NO_RETRY')",
  "self.journal.add('raw_response_line'","response=json.loads(line)"])
 ck('raw_journal_precedes_response_parse',functions['Session'].index("self.journal.add('raw_response_line'")<functions['Session'].index('response=json.loads(line)'),
  'Exact raw bytes journaled before JSON parsing')
 has('start_and_close_group_saved',functions['Session'],[
  "self.journal.add('source_start_group',members=group)","self.journal.add('source_close_group',members=self.close_group)"])
 has('supervisor_actual_parent_identity_and_FD_proof',functions['supervisor_proof'],[
  "sha(Path('/proc',str(parent),'exe'))==ext['time_binary_sha256']",
  "Path('/proc',str(parent),'cmdline').read_bytes()",'planned[\'argv\']==expected',
  "sibling.st_ino==planned['time_inode']and sibling.st_dev==planned['time_device']"])
 has('response_one_completed_solve_only',functions['check_response'],[
  "response['source_dispatch_started']==response['source_dispatch_completed']==response['solve_calls']==1",
  "response['formal_table_I_calls']==0 and response['independent_path_qualified']is False",
  "SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT","SOURCE_NONEXACT_RETAINED_PREFIX"])
 has('construction_RNG_boundary_truthful',functions['check_response'],[
  "c['cbirrt_constructor_dispatch_completed']==c['ompl_setSeed_calls_completed']==c['srand_calls_completed']==1",
  "c['svc_only_constructor_dispatch_completed']==0 and c['source_direct_rng_member_initializations_structural']==1",
  'UNOBSERVED_LIBRARY_NOT_HOOKED','UNOBSERVED_NOT_REPORTED_ZERO'])
 has('trace_strict_nested_actual_counts',functions['check_response'],[
  "stack.append(key);started[event['kind']]+=1","stack.pop()==key",
  "dict(started)==observed['source_started']and dict(completed)==observed['source_completed']",
  "c['source_started']==c['source_completed']=={'mesh_load':1}"])
 has('existing_observed_save_mark_allowed_without_fake_completion',functions['check_response'],[
  "elif event['event']=='observed':","event['kind']=='save_source_mpaths'and 'source_mpaths'in event['args']",
  'ONLY_EXISTING_SOURCE_MPATHS_OBSERVATION_ALLOWED'])
 has('tree_and_milestones_preserved_not_qualified',functions['check_response'],[
  "isinstance(response['trees']['nodes'],list)and isinstance(response['milestones_q12'],list)",
  'These objects are independently audited after S; no path PASS is asserted here.'])
 has('single_exclusive_run_claim_no_live_overlap',functions['execute'],[
  "require(not folder.exists()and not claim.exists(),'EXCLUSIVE_SINGLE_SOLVE_NO_RETRY')",
  "require(not old.builder.active_p4(),'OTHER_ACTIVE_P4_EXECUTION')",
  "require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')"])
 has('exclusive_mesh_copy_and_fresh_native_outputs',functions['execute'],[
  "(work/'simulator').mkdir(parents=True)","target.open('xb')",'RUNTIME_MESH_CHANGED',
  "not(work/'paths').exists()and not(folder/'paths').exists()"])
 has('one_session_query_and_raw_full_trace_bound',functions['execute'],[
  "session=Session(spec['build_assets']['targets']['distance_destination_fix'],work,budget,journal,counts);session.start()",
  "response=session.query(spec['request']);journal.add('parsed_response_before_gates',response=response)",
  'RAW_BODY_TRACE_MUST_MATCH_FULL_SOURCE_RESPONSE','EXACT_ONE_COMPLETE_SOURCE_STDOUT_REQUIRED',
  "counts['solve_dispatched']==counts['raw_response_lines_observed']==1"])
 ck('exactly_one_source_Session_and_query_site',functions['execute'].count('session=Session(')==1 and functions['execute'].count('session.query(')==1,
  'No second science site or retry loop in execute')
 has('timer_disabled_before_cleanup_and_all_actual_children_reaped',functions['execute'],[
  'if budget is not None:budget.close()',"else[session.proc])}.values())",
  'old.kill_source_process(proc);proc.wait(timeout=1.)',"'STOP_PROCESS_EOF_OR_EXIT_UNQUALIFIED'"])
 has('mandatory_original_hashes_and_current_prior_recheck',functions['execute'],[
  'BOUND_ASSET_CHANGED','RECIPE_CHANGED',"latest=current_prior()",'PRIOR_OR_AUTHORITATIVE_LEDGER_CHANGED'])
 has('complete_raw_streams_preserved_and_fsynced',functions['execute'],[
  "journal.add('final_complete_raw_streams'","(folder/f'source_{channel}.bin').open('xb')",
  'stream.flush();os.fsync(stream.fileno())',"journal.finish()"])
 has('all_original_native_path_and_partial_files_retained_fsynced',functions['execute'],[
  "for base in(folder/'paths',folder/'work/paths')","base.rglob('*')",
  "record['original_native_output_sha256']","with p.open('rb')as stream:os.fsync(stream.fileno())"])
 has('internal_record_never_self_certifies_external_or_path',functions['execute'],[
  'external_supervision_qualified=False,independent_saved_POST_required=True',
  'independent_path_qualified=False',"last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'"])
 has('final_cost_gate_and_exclusive_execution_receipt',functions['execute'],[
  "record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'","old.durable_new(folder/'execution.json',record)",
  "with(folder/'cost_receipt.jsonl').open('xb')",'wall_s_through_execution_persistence=',
  'cpu_s_through_execution_persistence='])
 has('exclusive_GNUtime_FD_and_actual_wait',s,[
  'os.O_WRONLY|os.O_CREAT|os.O_EXCL',"f'/proc/self/fd/{fd}'",'pass_fds=(fd,)',
  "planned=dict(event='planned_launch'","proc.wait()"])
 has('supervisor_fixed_sources_and_no_old_artifact_retry',s,[
  'FROZEN_SUPERVISOR_AND_RUNNER_REQUIRED','OLD_RUN_OR_CLAIM_NO_RETRY','OLD_SUPERVISION_ARTIFACT_NO_RETRY'])
 has('external_Decimal_upper_bounds_and_exact_cap',s,[
  "wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'))",
  "wall<=min(30.,3600.-spec['previous_r2_wall_s'])", "cpu<=min(60.,7200.-spec['previous_r2_cpu_s'])"])
 has('supervisor_retains_failed_attempt_and_no_self_external_certification',s,[
  'started_attempt=attempted','external_supervision_qualified=False,independent_POST_required=True',
  'Supervisor own journal/fsync cost excluded.',"new_json(chargefile,payload)"])
 has('PRE_no_full_path_or_planning_claim_and_latest_ledger',p,[
  'DRAFT_ONLY / NOT_FROZEN / NO_PROTOCOL / NO_PRIOR_SNAPSHOT / NO_CLAIM / NO_EXECUTION',
  '最新权威实际 ledger','S 不自动启动 P 或正式成本 pilot','只有人员独立实际 POST'])
 # Saved-only arithmetic/source matching. These are not new physical queries.
 savedname='reports/P4_FULL_R2_ABB_CBIRRT_ACTIVEDISTANCE_SAVED_COUNTEREXAMPLE_20261015.json'
 bind(savedname);points={x['source']:x for x in load(savedname)['points']}
 lo=[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2;hi=[2.88,1.919,1.22,2.79,2.09,3.1416]*2
 for i in(0,1):
  name=f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_{i}.json';e=load(name);bind(name)
  ck(f'A01_II_{i}_original_exact_binary64_and_hash',sha(name)==points[name]['source_sha256']and bits(e['selected_q_rad'])==bits(points[name]['q12']),name)
  ck(f'A01_II_{i}_within_native_sampler_box',len(e['selected_q_rad'])==12 and all(math.isfinite(v)and a<=v<=b for v,a,b in zip(e['selected_q_rad'],lo,hi)),name)
  ck(f'A01_II_{i}_saved_reconstructed_qualified',e['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'and e['source_policy_collision_qualified']is True,name)
 driver='baselines/p4_full/geometry_consistent/abb_cbirrt_d_driver_draft.cpp'
 observer='baselines/p4_full/geometry_consistent/abb_cbirrt_d_observation_draft.hpp'
 transform='baselines/p4_full/geometry_consistent/abb_cbirrt_d_instrumentation_draft.py'
 for n in(driver,observer,transform):bind(n)
 c=(ROOT/driver).read_text();h=(ROOT/observer).read_text();tr=(ROOT/transform).read_text()
 has('actual_driver_fixed_single_II_solve_source_and_request',c,[
  '(operation=="solve"&&(env!="II"||mode!="trace"))','if(++requests>(operation=="solve"?1u:8u))',
  'request.at("seed")!=7||request.at("range_rad")!=2.6||request.at("solve_seconds")!=10.',
  'planner->solve(ob::timedPlannerTerminationCondition(10.))'])
 has('actual_driver_retains_both_trees_high_precision_path_and_exact_only_PlannerData',c,[
  'out["trees"]=planner->snapshot()', 'out["milestones_q12"].push_back(p4cb::q12(state))',
  'if(problem->hasExactSolution()) {','out["planner_data"]={{"vertices",vertices},{"edges",edges}};',
  'else out["planner_data"]=nullptr;'])
 has('actual_observer_mark_is_existing_observed_event',h,['inline void mark(', '{{"event","observed"}'])
 has('actual_transform_captures_original_save_paths',tr,['p4cb::mark("save_source_mpaths"', '"source_mpaths",p4_paths', 'for(const auto& side:{mpath1,mpath2})'])
 ck('source_hashes_unchanged_during_review',all(sha(n)==w for n,w in EXPECTED.items()),'Review locked to exact four draft hashes')
 result=dict(schema='P4_CBIRRT_D_SOLVE_INDEPENDENT_STATIC_REVIEW_V1',
  status='PASS_STATIC_DRAFT_ONLY_NO_EXECUTION'if not failures else'STOP_STATIC_FINDINGS',
  reviewer='nr_path_prepare: LOCAL02 implementer; not S runner/supervisor/PRE implementer',personnel_independent=True,
  reviewed_source_sha256=EXPECTED,retained_sha256=retained,checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),failures=failures,full_checks=checks,
  no_runner_import_describe_protocol_prior_claim_compile_or_scientific_execution=True,
  external_supervision_qualified=False,independent_path_qualified=False,actual_S_execution_not_reviewed=True,
  limitations=['Static/source/saved-byte review only; actual L independent POST and latest authoritative charged ledger remain hard runtime requirements.',
   'Existing native source can return EXACT despite false reconstruction. Only SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT is accepted; saved independent tree/bridge/path P audit remains mandatory.',
   'S time includes original observation/save I/O and is not a paper statistical timing sample. Supervisor own journal tail is outside scientific child cost; historical unmeasured tails stay UNKNOWN.',
   'No claim of continuous collision proof, RSS qualification, PCS advantage, full paper reproduction, or formal Table I trials.'])
 out=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE_INDEPENDENT_STATIC_REVIEW_20261016.json'
 with out.open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:result[k]for k in('status','checks_total','checks_passed','checks_failed','personnel_independent')}))

if __name__=='__main__':main()
