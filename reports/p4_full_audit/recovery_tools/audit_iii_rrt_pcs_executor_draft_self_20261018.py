#!/usr/bin/env python3
"""Saved-byte/AST self review only; never imports any candidate or runs tools."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import shlex

ROOT=Path(__file__).resolve().parents[3]
def p(n):
    q=Path(n);return q if q.is_absolute()else ROOT/q
def raw(n):return p(n).read_bytes()
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def js(n):return json.loads(raw(n))
def tree(n):return ast.parse(raw(n),filename=str(p(n)))
def fn(t,n):return next(v for v in t.body if isinstance(v,ast.FunctionDef)and v.name==n)
def dump(t):return ast.dump(t,include_attributes=False)

RUNNER='scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py'
SUP='scripts/p4_d080/supervise_iii_rrt_pcs_e2e_build_v1_draft.py'
BASE='scripts/p4_d080/build_v_pcs_local_v1_draft.py'
BASE_SUP='scripts/p4_d080/supervise_v_pcs_build_v1_draft.py'
SPEC='configs/p4_d080/iii_rrt_pcs_e2e_build_v1.DRAFT.json'
PLAN='configs/p4_d080/iii_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'
DEPS='configs/p4_d080/iii_rrt_pcs_saved_dependency_union_v1.DRAFT.json'
PRE='reports/P4_D080_ENV_III_RRT_PCS_EXECUTOR_PRE_DRAFT_20261018.md'
spec=js(SPEC);plan=js(PLAN);deps=js(DEPS)
t=tree(RUNNER);b=tree(BASE);st=tree(SUP)
text=raw(RUNNER).decode();checks=[]
def check(name,ok,evidence=None):
    checks.append({'name':name,'passed':bool(ok),'evidence':evidence})

check('stdlib_AST_parse_runner_and_supervisor_only',isinstance(t,ast.Module)and isinstance(st,ast.Module))
check('base_V_builder_frozen_bytes_unchanged',sha(BASE)=='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578')
check('base_V_supervisor_frozen_bytes_unchanged',sha(BASE_SUP)=='7b50c7cd39a00958605f04a6fe997915dcd1f93aada4ed3f36276e2260f8e2ad')
check('original_III_plan_unchanged',sha(PLAN)=='cb5f028e38339a36306d791dda2b41f9de04cc922e5fc70a8876046a1485258e')
check('original_III_driver_unchanged',sha(plan['new_driver'])=='1ca2cf62944649a2a59d1e52280ec016cd878386a3fdd66b3b700ab0ada170e5')
check('original_II_observer_unchanged',sha(plan['unchanged_observer'])=='b597b56199279bd02a7030375e0dd055d650c9a0bb4bee80aef6d4242755381c')
old=raw(BASE_SUP).decode();new=raw(SUP).decode()
replacements=[('20261018_R2_D080_V_PCS_BUILD01','20261018_R2_D080_III_RRT_PCS_BUILD01'),
 ('ENGINEERING_BUILD_ONLY_V_PCS_ORIGINAL_SCIENTIFIC_CONTROL','ENGINEERING_BUILD_ONLY_III_RRT_PCS_UNCHANGED_QUALIFIED_COMPONENTS'),
 ('scripts/p4_d080/build_v_pcs_local_v1_draft.py','scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py'),
 ("spec['environment']=='V'","spec['environment']=='III'"),
 ('P4_D080_V_PCS_BUILD_FROZEN_V1','P4_D080_III_RRT_PCS_BUILD_FROZEN_V1'),
 ('EXPLICIT_FROZEN_V_PCS_BUILD_REQUIRED','EXPLICIT_FROZEN_III_RRT_PCS_BUILD_REQUIRED'),
 ('P4_D080_V_PCS_BUILD_EXTERNAL_COST_CHARGE_V1','P4_D080_III_RRT_PCS_BUILD_EXTERNAL_COST_CHARGE_V1')]
counts=[]
for a,z in replacements:
    counts.append([old.count(a),new.count(z)]);new=new.replace(z,a)
check('supervisor_exact_inverse_seven_identity_replacements',new==old and counts==[[1,1]]*7,counts)
check('validate_supervision_exact_base_AST',dump(fn(t,'validate_supervision'))==dump(fn(b,'validate_supervision')))
check('prior_CPU_invoke_group_helpers_direct_aliases',all(s in text for s in [
 'cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke',
 'lifecycle=B.lifecycle;compiler_group_members=B.compiler_group_members',
 'evidence=B.dependency_evidence(dep,obj,source,staged,bound,state)']))
bt=next(v for v in fn(b,'main').body if isinstance(v,ast.Try))
nt=next(v for v in fn(t,'main').body if isinstance(v,ast.Try))
unchanged=[i for i in range(17)if i not in(6,14)]
check('finalization_fifteen_of_seventeen_statements_exact_base_AST',len(bt.finalbody)==len(nt.finalbody)==17 and all(dump(bt.finalbody[i])==dump(nt.finalbody[i])for i in unchanged),unchanged)
normalized=copy.deepcopy(nt.finalbody[14])
for node in ast.walk(normalized):
    if isinstance(node,ast.Constant)and node.value=='P4_D080_III_RRT_PCS_BUILD_COST_RECEIPT_V1':node.value='P4_D080_V_PCS_BUILD_COST_RECEIPT_V1'
check('receipt_AST_only_schema_identity_change',dump(normalized)==dump(bt.finalbody[14]))
log=ast.unparse(nt.finalbody[6])
check('remaining_finalization_change_only_stage_logs_and_first_receipt_hashes',
 "(STAGE / 'logs').glob('*.log')"in log and 'immediate_object_collection_receipts_sha256'in log
 and 'compile_log_hashes'in log and len(nt.finalbody[6].body)==2)
check('original_plan_32_copies_and_five_TU_one_link_commands_exact',spec['copy_exact_assets']==plan['copy_exact_assets']and len(spec['copy_exact_assets'])==32
 and spec['commands']==[u['command']for u in plan['compile_units']]+[plan['link_command']]
 and len(plan['compile_units'])==5 and spec['new_compile_calls']==5 and spec['new_link_calls']==1)
check('all_copy_source_bytes_and_unique_fresh_destinations',all(sha(r['source'])==r['sha256']for r in spec['copy_exact_assets'])
 and len({r['destination']for r in spec['copy_exact_assets']})==32 and all(not p(r['destination']).exists()for r in spec['copy_exact_assets']))
check('original_III_environment_geometry_range_frozen_plan',plan['author_internal_environment']==2 and plan['source_geometry_mm']=={'robot_distance':1200.,'rod_length':500.}
 and 'std::make_shared<og::RRT>(si,.8,2)'in raw(plan['new_driver']).decode())
check('draft_unexecutable_all_five_flags_false',all(spec[k]is False for k in ['frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']))
check('latest_prior_unbound_no_stale_V_binding',all(spec['prior'][k]is None for k in ['ledger','ledger_sha256','wall_s','cpu_s']))
check('original_fixed_engineering_caps_and_zero_science_calls',spec['budget']=={'wall_s':45,'cpu_s':90}and spec['working_budget']=={'wall_s':40,'cpu_s':80}
 and all(spec[k]==0 for k in ['query_calls','solve_calls','binary_execution_calls']))
bound=spec['bound_files_sha256']
check('all_747_pre_prior_binding_bytes_current',len(bound)==747 and all(sha(n)==w for n,w in bound.items()),{'count':len(bound)})
check('current_OWN_runner_supervisor_PRE_plan_union_bound',all(bound.get(str(p(n)))==sha(n)for n in [RUNNER,SUP,PRE,PLAN,DEPS,BASE]))
check('saved_MD_union_original_bytes',sha(DEPS)==spec['dependency_union_sha256']=='28c48db9dfb8bbca8b50856a9a0d09b130422981d28f7f8a8523f56e8f3cfc8b')
observed=set()
for n,w in deps['source_MD_files_sha256'].items():
    assert sha(n)==w
    logical=raw(n).replace(b'\\\n',b' ').decode();head,tail=logical.split(':',1)
    observed.update(str(Path(n).resolve(strict=True))for n in shlex.split(tail))
check('six_saved_actual_MD_rules_reconstruct_exact_684_union',len(deps['source_MD_files_sha256'])==6 and observed==set(deps['actual_saved_dependencies_sha256'])and len(observed)==684)
managed=deps['managed_dependencies_sha256'];system=deps['system_dependencies_sha256']
check('managed320_system364_disjoint_and_complete',len(managed)==320 and len(system)==364 and not set(managed)&set(system)
 and {**managed,**system}==deps['actual_saved_dependencies_sha256'])
check('all_MD_union_and_five_PQP_headers_current_prebound',all(bound.get(str(p(n)))==w==sha(n)
 for field in ['source_MD_files_sha256','actual_saved_dependencies_sha256','PQP_five_headers_sha256']for n,w in deps[field].items()))
check('exact_five_PQP_header_names',set(Path(n).name for n in deps['PQP_five_headers_sha256'])=={'PQP.h','PQP_Internal.h','PQP_Compile.h','BV.h','Tri.h'})
check('new_actual_MD_protected_dependency_gate_retained','B.dependency_evidence(dep,obj,source,staged,bound,state)'in text
 and "'UNFROZEN_ACTUAL_PROTECTED_DEPENDENCY_'"in raw(BASE).decode())
compileloop=next(v for v in nt.body if isinstance(v,ast.For)and isinstance(v.target,ast.Tuple))
body=ast.unparse(compileloop)
check('first_object_SHA_receipt_after_compile_before_dependency_gate',body.index('invoke(')<body.index("'object_sha256': sha(obj)")<body.index('write_once(')<body.index('B.dependency_evidence('))
check('live_start_ticks_true_observation_or_explicit_UNKNOWN','start_ticks_observation'in text and 'UNKNOWN_PROCESS_EXITED_BEFORE_READ'in text)
check('legacy_activity_guard_plus_small_D080_actual_script_guard','not lifecycle.active_p4()and not active_d080(supervisor)'in text
 and "allowed={os.getpid(),supervisor['actual_time_pid'],supervisor['supervisor_pid']}"in text
 and "('build_','qualify_','supervise_')"in text and "Path('/proc',str(pid),'cwd')/script"in text)
stage=p(spec['stage_root']);run=ROOT/'results/p4_full'/spec['run_name']
sidecars=[Path(str(run)+s)for s in ['.supervision.time.txt','.supervision.jsonl','.supervision.stderr.log','.supervision.charge.json']]
check('fresh_stage_run_and_all_external_sidecars_absent',not stage.exists()and not run.exists()and not any(q.exists()for q in sidecars))
scope=js('configs/p4_d080/execution_scope_v1.json')
check('D080_scope_I_V_VI_archive_and_no_formal',scope['allowed_environments']==['I','II','III','IV','V']and scope['VI_future_science_authorized']is False and scope['formal_execution_authorized']is False)
check('no_new_dependency_preprocessing_or_model_by_preparation',deps['new_compiler_or_dependency_preprocessing_calls']==deps['new_model_or_scientific_calls']==0)
archive=ROOT/'work/preserved_iii_executor_before_d080_activity_guard_20261018'
manifest=json.loads((archive/'manifest.json').read_text())
check('pre_guard_three_draft_versions_preserved_exact',len(manifest)==3 and all(hashlib.sha256((archive/n).read_bytes()).hexdigest()==r['sha256']for n,r in manifest.items()))

result={'schema':'P4_D080_III_RRT_PCS_EXECUTOR_DRAFT_SELF_STATIC_V1','personnel_independent':False,
 'status':'PASS_SELF_STATIC_ONLY_NOT_EXECUTION_OR_QUALIFICATION'if all(r['passed']for r in checks)else 'FAIL_SELF_STATIC',
 'review_scope':'Saved bytes and AST only; no candidate import, compiler, preprocessor, binary, model, describe or scientific query.',
 'checks_total':len(checks),'checks_passed':sum(r['passed']for r in checks),'checks_failed':sum(not r['passed']for r in checks),
 'inputs_sha256':{n:sha(n)for n in [RUNNER,SUP,SPEC,PLAN,DEPS,PRE,BASE,BASE_SUP,plan['new_driver'],plan['unchanged_observer']]},
 'self_auditor_sha256':sha(__file__),'checks':checks,'latest_prior_bound':False,'new_compile_calls':0,'new_model_calls':0,
 'independent_review_and_root_V34_latest_prior_binding_required':True}
output=ROOT/'reports/P4_D080_ENV_III_RRT_PCS_EXECUTOR_DRAFT_SELF_STATIC_20261018.json'
with output.open('x')as stream:stream.write(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'total':result['checks_total'],'passed':result['checks_passed'],
 'failed':[r for r in checks if not r['passed']],'output_sha256':sha(output)},ensure_ascii=False,indent=2))
