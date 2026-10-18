#!/usr/bin/env python3
"""Personnel-independent thin saved-byte/AST review. Never imports candidate code."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import shlex

ROOT=Path(__file__).resolve().parents[3]
def p(n):
    q=Path(n);return q if q.is_absolute() else ROOT/q
def raw(n):return p(n).read_bytes()
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def js(n):return json.loads(raw(n))
def tree(n):return ast.parse(raw(n))
def fn(t,n):return next(x for x in t.body if isinstance(x,ast.FunctionDef) and x.name==n)
def dump(n):return ast.dump(n,include_attributes=False)

RUNNER='scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py'
SUP='scripts/p4_d080/supervise_iii_rrt_pcs_e2e_build_v1_draft.py'
BASE='scripts/p4_d080/build_v_pcs_local_v1_draft.py'
BSUP='scripts/p4_d080/supervise_v_pcs_build_v1_draft.py'
SPEC='configs/p4_d080/iii_rrt_pcs_e2e_build_v1.DRAFT.json'
PLAN='configs/p4_d080/iii_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'
DEPS='configs/p4_d080/iii_rrt_pcs_saved_dependency_union_v1.DRAFT.json'
PRIOR='configs/p4_d080/iii_rrt_pcs_V34_prior_evidence_v1.DRAFT.json'
PRE='reports/P4_D080_ENV_III_RRT_PCS_EXECUTOR_PRE_DRAFT_20261018.md'
SELF='reports/P4_D080_ENV_III_RRT_PCS_EXECUTOR_DRAFT_SELF_STATIC_20261018.json'
s=js(SPEC);plan=js(PLAN);d=js(DEPS);prior=js(PRIOR)
t=tree(RUNNER);b=tree(BASE);txt=raw(RUNNER).decode();checks=[]
def ck(n,v,e=None):checks.append(dict(name=n,passed=bool(v),evidence=e))
ck('exact_new_runner_supervisor_and_dependency_manifest',sha(RUNNER)=='a3035ab09ade161811026eb08fc0523ab07f7adde3da86cd431cabcfddc3eabe' and sha(SUP)=='661dbc63efadbfa1031b4ce248d9f7aebde6b5484e5582826ed3383627db132a' and sha(DEPS)=='28c48db9dfb8bbca8b50856a9a0d09b130422981d28f7f8a8523f56e8f3cfc8b')
ck('exact_reused_V_engineering_bodies',sha(BASE)=='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578' and sha(BSUP)=='7b50c7cd39a00958605f04a6fe997915dcd1f93aada4ed3f36276e2260f8e2ad')
old=raw(plan['base_driver']).decode();new=raw(plan['new_driver']).decode()
replacements=[('// Project-owned one-shot entry to the external author\'s RRT_PCS.','// Project-owned environment III thin entry; derived from qualified II driver, source unchanged.'),('P4_ABB_RRT_PCS_END_TO_END_V1','P4_ABB_III_RRT_PCS_END_TO_END_DRAFT_V1'),('request.at("environment")!="II"','request.at("environment")!="III"'),('request.at("range_rad")!=2.6','request.at("range_rad")!=.8'),('FROZEN_II_SEED7_RANGE26_GOAL005_SOLVE10_REQUIRED','FROZEN_III_SEED7_RANGE08_GOAL005_SOLVE10_REQUIRED'),('{"environment","II"}','{"environment","III"}'),('{"range_rad",2.6}','{"range_rad",.8}'),('std::make_shared<og::RRT>(si,2.6,1)','std::make_shared<og::RRT>(si,.8,2)')]
counts=[]
for a,z in replacements:counts.append([old.count(a),new.count(z)]);new=new.replace(z,a)
ck('III_driver_exactly_eight_environment_identity_replacements',new==old and counts==[[1,1]]*8,counts)
ck('observer_unchanged_and_III_plan_exact',sha(plan['unchanged_observer'])=='b597b56199279bd02a7030375e0dd055d650c9a0bb4bee80aef6d4242755381c' and sha(PLAN)=='cb5f028e38339a36306d791dda2b41f9de04cc922e5fc70a8876046a1485258e')
old=raw(BSUP).decode();new=raw(SUP).decode()
replacements=[('20261018_R2_D080_V_PCS_BUILD01','20261018_R2_D080_III_RRT_PCS_BUILD01'),('ENGINEERING_BUILD_ONLY_V_PCS_ORIGINAL_SCIENTIFIC_CONTROL','ENGINEERING_BUILD_ONLY_III_RRT_PCS_UNCHANGED_QUALIFIED_COMPONENTS'),('scripts/p4_d080/build_v_pcs_local_v1_draft.py','scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py'),("spec['environment']=='V'","spec['environment']=='III'"),('P4_D080_V_PCS_BUILD_FROZEN_V1','P4_D080_III_RRT_PCS_BUILD_FROZEN_V1'),('EXPLICIT_FROZEN_V_PCS_BUILD_REQUIRED','EXPLICIT_FROZEN_III_RRT_PCS_BUILD_REQUIRED'),('P4_D080_V_PCS_BUILD_EXTERNAL_COST_CHARGE_V1','P4_D080_III_RRT_PCS_BUILD_EXTERNAL_COST_CHARGE_V1')]
counts=[]
for a,z in replacements:counts.append([old.count(a),new.count(z)]);new=new.replace(z,a)
ck('supervisor_seven_identity_replacements_only_Decimal_OEXCL_cleanup_unchanged',new==old and counts==[[1,1]]*7,counts)
ck('actual_parent_GNUtime_held_inode_validation_AST_reused',dump(fn(t,'validate_supervision'))==dump(fn(b,'validate_supervision')))
ck('prior_invoke_lifecycle_and_actual_dependency_gate_direct_reuse',all(z in txt for z in ['cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke','lifecycle=B.lifecycle;compiler_group_members=B.compiler_group_members','evidence=B.dependency_evidence(dep,obj,source,staged,bound,state)']))
bt=next(x for x in fn(b,'main').body if isinstance(x,ast.Try));nt=next(x for x in fn(t,'main').body if isinstance(x,ast.Try))
ck('fifteen_of_seventeen_finalizer_statements_exact_AST',len(bt.finalbody)==len(nt.finalbody)==17 and all(dump(bt.finalbody[i])==dump(nt.finalbody[i]) for i in range(17) if i not in (6,14)))
receipt=copy.deepcopy(nt.finalbody[14])
for node in ast.walk(receipt):
    if isinstance(node,ast.Constant) and node.value=='P4_D080_III_RRT_PCS_BUILD_COST_RECEIPT_V1':node.value='P4_D080_V_PCS_BUILD_COST_RECEIPT_V1'
log=ast.unparse(nt.finalbody[6])
ck('two_finalizer_changes_only_receipt_schema_and_log_first_receipt_SHA',dump(receipt)==dump(bt.finalbody[14]) and len(nt.finalbody[6].body)==2 and "(STAGE / 'logs').glob('*.log')" in log and 'immediate_object_collection_receipts_sha256' in log)
ck('single_target_exact32copy_five_TU_one_link',s['copy_exact_assets']==plan['copy_exact_assets'] and len(s['copy_exact_assets'])==32 and s['commands']==[u['command'] for u in plan['compile_units']]+[plan['link_command']] and len(plan['compile_units'])==5 and s['new_compile_calls']==5 and s['new_link_calls']==1)
loop=next(x for x in nt.body if isinstance(x,ast.For) and isinstance(x.target,ast.Tuple));looptext=ast.unparse(loop)
ck('success_object_SHA_first_receipt_precedes_dependency_gate',looptext.index('invoke(')<looptext.index("'object_sha256': sha(obj)")<looptext.index('write_once(')<looptext.index('B.dependency_evidence('))
ck('working40_80_final45_90_zero_binary_or_model_queries',s['budget']=={'wall_s':45,'cpu_s':90} and s['working_budget']=={'wall_s':40,'cpu_s':80} and all(s[k]==0 for k in ['query_calls','solve_calls','binary_execution_calls']) and "time.monotonic()-started<40 and cpu()-before_cpu+live<80" in txt)
bound=s['bound_files_sha256'];observed=set()
for name,w in d['source_MD_files_sha256'].items():
    logical=raw(name).replace(b'\\\n',b' ').decode();_,tail=logical.split(':',1)
    observed.update(str(Path(n).resolve(strict=True)) for n in shlex.split(tail))
ck('six_actual_saved_MD_rules_form_exact684_union_no_preprocessor',len(d['source_MD_files_sha256'])==6 and observed==set(d['actual_saved_dependencies_sha256']) and len(observed)==684 and d['new_compiler_or_dependency_preprocessing_calls']==d['new_model_or_scientific_calls']==0)
ck('managed320_system364_and_bound_maps_consistent_without_repeat_full_hash',len(d['managed_dependencies_sha256'])==320 and len(d['system_dependencies_sha256'])==364 and not set(d['managed_dependencies_sha256'])&set(d['system_dependencies_sha256']) and {**d['managed_dependencies_sha256'],**d['system_dependencies_sha256']}==d['actual_saved_dependencies_sha256'] and all(bound.get(str(p(n).resolve()))==w for field in ['source_MD_files_sha256','actual_saved_dependencies_sha256','PQP_five_headers_sha256'] for n,w in d[field].items()))
ck('five_PQP_headers_explicitly_prebound_and_new_MD_protected_gate_retained',set(Path(n).name for n in d['PQP_five_headers_sha256'])=={'PQP.h','PQP_Internal.h','PQP_Compile.h','BV.h','Tri.h'} and "'UNFROZEN_ACTUAL_PROTECTED_DEPENDENCY_'" in raw(BASE).decode())
guard=ast.unparse(fn(t,'active_d080'))
ck('legacy_plus_actual_D080_process_guard_skips_only_proven_launch_chain',"not lifecycle.active_p4()and not active_d080(supervisor)" in txt and "allowed = {os.getpid(), supervisor['actual_time_pid'], supervisor['supervisor_pid']}" in guard and "parts[1:3]" in guard and "Path('/proc', str(pid), 'cwd') / script" in guard and "('build_', 'qualify_', 'supervise_')" in guard)
ck('live_start_ticks_observed_or_explicit_UNKNOWN_no_fabrication','start_ticks_observation' in txt and 'UNKNOWN_PROCESS_EXITED_BEFORE_READ' in txt)
ck('latest_V34_manifest_exact_and_52execution_21charged_roles179',sha(PRIOR)=='8758da9105c69c4c75472ba8e6b23b0653856dbef1a69432e991ae9fb68ebe65' and prior['execution_count']==52 and prior['charged_executions']==21 and prior['historical_unmeasured_executions']==31 and prior['evidence_count']==179 and len(prior['evidence_sha256'])==179)
pf=prior['prior_fragment_for_root_only'];ledger=js(pf['ledger'])
ck('V34_ledger_bytes_and_exact_saved_prior_numbers',sha(pf['ledger'])==pf['ledger_sha256']=='2675474c8a646428d29101107653ead0a64ef96a1a80af4680d47f453dff7637' and pf['wall_s']==1113.4602605769917 and pf['cpu_s']==927.6919419999999)
merged=dict(bound);conflicts=[]
for n,w in prior['evidence_sha256'].items():
    if n in merged and merged[n]!=w:conflicts.append(n)
    merged[n]=w
ck('747_saved_bindings_plus179_current_prior_evidence_are926_without_conflict',len(bound)==747 and len(merged)==926 and not conflicts,conflicts)
ck('draft_remains_nonexecutable_prior_unbound_no_science_authorized',all(s[k] is False for k in ['frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']) and all(s['prior'][k] is None for k in ['ledger','ledger_sha256','wall_s','cpu_s']))
ck('fresh_run_stage_and_all_sidecars_absent',not p(s['stage_root']).exists() and not (ROOT/'results/p4_full'/s['run_name']).exists() and not any(Path(str(ROOT/'results/p4_full'/s['run_name'])+z).exists() for z in ['.supervision.time.txt','.supervision.jsonl','.supervision.stderr.log','.supervision.charge.json']))
scope=js('configs/p4_d080/execution_scope_v1.json')
ck('D080_scope_I_V_only_no_VI_or_formal',scope['allowed_environments']==['I','II','III','IV','V'] and scope['VI_future_science_authorized'] is False and scope['formal_execution_authorized'] is False)
result={'schema':'P4_D080_III_RRT_PCS_EXECUTOR_INCREMENTAL_INDEPENDENT_PRE_V1','personnel_independent':True,'status':'PASS_THIN_ENGINEERING_PRE_ONLY' if all(x['passed'] for x in checks) else 'FAIL_THIN_ENGINEERING_PRE','checks_total':len(checks),'checks_passed':sum(x['passed'] for x in checks),'checks_failed':sum(not x['passed'] for x in checks),'checks':checks,'inputs_sha256':{n:sha(n) for n in [RUNNER,SUP,BASE,BSUP,SPEC,PLAN,DEPS,PRIOR,PRE,SELF,plan['base_driver'],plan['new_driver'],plan['unchanged_observer']]},'auditor_sha256':sha(__file__),'new_compile_calls':0,'new_model_calls':0,'full_747_or926_hash_sweep_repeated':False,'prior_independent_path_or_model_certificates_retested':False,'allowed_root_only_freeze_transform':{'preserve_DRAFT':True,'new_frozen_config_required':True,'prior':pf,'bound_files_sha256':'Preserve all747; add exact179 V34 evidence paths (926 union), prior manifest and this independent certificate/auditor identities. No conflicting overwrite. Runtime validates every bound input and latest prior again.','flags_to_true':['frozen','independent_review_passed','engineering_execution_authorized'],'flags_stay_false':['scientific_execution_authorized','formal_execution_authorized'],'status_metadata_only':'FROZEN_ENGINEERING_ONLY_NOT_QUERIED','all_other_conditions':'Exact32 copies, original5TU1link, own sources, dependencies, geometry, observer, caps and zero binary calls unchanged; commit OWN and protocol before root unique supervisor.'},'limitations':['Saved-byte/AST thin review; not engineering execution or scientific qualification.','179 prior files referenced by exact saved manifest; no duplicate full historical rehash. Runtime reused validate_prior must verify current complete prior evidence.','Author self33 retained as self review; not relabelled personnel independent.','Engineering success means BUILT_NOT_QUERIED only; future source/path qualification separately frozen.','Historical31 unmeasured tails remain UNKNOWN.']}
out=ROOT/'reports/P4_D080_ENV_III_RRT_PCS_EXECUTOR_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
with out.open('x') as f:f.write(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'total':len(checks),'failed':[x for x in checks if not x['passed']],'sha256':sha(out)},ensure_ascii=False,indent=2))
