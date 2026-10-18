#!/usr/bin/env python3
"""Stdlib saved-byte/AST only. No candidate import, transform or model call."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import shlex

ROOT=Path(__file__).resolve().parents[3]
def p(n):return Path(n)if Path(n).is_absolute()else ROOT/n
def sha(n):return hashlib.sha256(p(n).read_bytes()).hexdigest()
def load(n):return json.loads(p(n).read_text())
def tree(n):return ast.parse(p(n).read_text())
def fn(t,n):return next(x for x in t.body if isinstance(x,ast.FunctionDef)and x.name==n)
def dump(n):return ast.dump(n,include_attributes=False)
RUNNER='scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py'
SUP='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v1_draft.py'
BASE='scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py'
BASE_SUP='scripts/p4_d080/supervise_iii_rrt_pcs_e2e_build_v1_draft.py'
PLAN='configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'
DRAFT='configs/p4_d080/v_rrt_pcs_e2e_build_v1.DRAFT.json'
DEPS='configs/p4_d080/v_rrt_pcs_saved_dependency_union_v1.DRAFT.json'
PRE='reports/P4_D080_ENV_V_RRT_PCS_BUILD_EXECUTOR_PRE_DRAFT_20261018.md'
SEAM='reports/P4_D080_ENV_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
COMPOSITE='reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_COMPOSITE_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json'
spec=load(DRAFT);plan=load(PLAN);deps=load(DEPS);seam=load(SEAM)
rt=p(RUNNER).read_text();st=p(SUP).read_text();t=tree(RUNNER);base=tree(BASE)
checks=[]
def check(n,ok,e=None):checks.append({'name':n,'passed':bool(ok),'evidence':e})
check('runner_and_supervisor_AST_parse_only',isinstance(t,ast.Module)and isinstance(tree(SUP),ast.Module))
check('original20_seam_certificate_unchanged',sha(SEAM)=='d5f05c246a2a7cfafc5183e3166bde9bd2ce47ab42d3da9dd43b3df72ac1f858'
 and seam['personnel_independent']is True and seam['checks_passed']==20 and seam['checks_failed']==0)
check('original_plan_unchanged',sha(PLAN)=='1c320aa3d55a638124b86b1235445c0aac80857dd4313dcb4d8c060f802d55fe')
check('original_driver_transform_II_ABI_all_unchanged',all(sha(n)==w for n,w in plan['own_sources_sha256'].items()))
check('exact_III_V_infrastructure_unchanged',sha(BASE)=='a3035ab09ade161811026eb08fc0523ab07f7adde3da86cd431cabcfddc3eabe'
 and sha(BASE_SUP)=='661dbc63efadbfa1031b4ce248d9f7aebde6b5484e5582826ed3383627db132a'
 and sha('scripts/p4_d080/build_v_pcs_local_v1_draft.py')=='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578')
check('supervision_activity_prior_invoke_dependency_direct_reuse',all(s in rt for s in ['validate_supervision=I.validate_supervision;active_d080=I.active_d080',
 'cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke','lifecycle=B.lifecycle;compiler_group_members=B.compiler_group_members',
 'evidence=B.dependency_evidence(dep,obj,source,staged,bound,state)']))
check('III_source_Path_captured_before_metadata_change','Path(I.__file__).resolve()'in rt and rt.index('Path(I.__file__).resolve()')<rt.index('I.__file__=__file__')and 'sha(OWN[5])==I_SOURCE_SHA'in rt)
replacements=[('20261018_R2_D080_III_RRT_PCS_BUILD01','20261018_R2_D080_V_RRT_PCS_BUILD01'),
 ('ENGINEERING_BUILD_ONLY_III_RRT_PCS_UNCHANGED_QUALIFIED_COMPONENTS','ENGINEERING_BUILD_ONLY_V_RRT_PCS_2TU1LINK_ORIGINAL_RRT_CONTROL'),
 ('scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py','scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py'),
 ("spec['environment']=='III'","spec['environment']=='V'"),('P4_D080_III_RRT_PCS_BUILD_FROZEN_V1','P4_D080_V_RRT_PCS_BUILD_FROZEN_V1'),
 ('EXPLICIT_FROZEN_III_RRT_PCS_BUILD_REQUIRED','EXPLICIT_FROZEN_V_RRT_PCS_BUILD_REQUIRED'),
 ('P4_D080_III_RRT_PCS_BUILD_EXTERNAL_COST_CHARGE_V1','P4_D080_V_RRT_PCS_BUILD_EXTERNAL_COST_CHARGE_V1'),
 ("{'wall_s':45,'cpu_s':90}","{'wall_s':30,'cpu_s':60}"),('min(45.,3600.','min(30.,3600.'),
 ('min(90.,7200.','min(60.,7200.'),('dict(wall=wall>45.,cpu=cpu>90.)','dict(wall=wall>30.,cpu=cpu>60.)')]
original=p(BASE_SUP).read_text();modified=st;counts=[]
for a,z in replacements:
 counts.append([original.count(a),modified.count(z)]);modified=modified.replace(z,a)
check('supervisor_exact_inverse11_identity_and_budget_replacements',modified==original and counts==[[1,1]]*11,counts)
bf=next(v for v in fn(base,'main').body if isinstance(v,ast.Try)).finalbody
nf=copy.deepcopy(next(v for v in fn(t,'main').body if isinstance(v,ast.Try)).finalbody)
for i,node in enumerate(nf):
 for c in ast.walk(node):
  if isinstance(c,ast.Constant):
   if c.value=='P4_D080_V_RRT_PCS_BUILD_COST_RECEIPT_V1':c.value='P4_D080_III_RRT_PCS_BUILD_COST_RECEIPT_V1'
   elif isinstance(c.value,(int,float))and type(c.value)is not bool and c.value in (30,60):c.value={30:45,60:90}[c.value]
check('cleanup_final_hash_prior_log_receipt_AST_identical_except_caps_and_schema',len(bf)==len(nf)==17 and all(dump(a)==dump(z)for a,z in zip(bf,nf)))
check('exact_new2TU1link_commands_and_three_reused_objects',spec['commands']==plan['commands']and len(spec['commands'])==3 and spec['new_compile_calls']==2
 and spec['new_link_calls']==1 and spec['reused_objects']==plan['reused_objects']and len(spec['reused_objects'])==3)
check('whole_RRT_cpp_header_current_bytes_unchanged',all(sha(plan['RRT_source_byte_identity'][f])==plan['RRT_source_byte_identity'][f+'_sha256']for f in ['cpp','header'])and plan['RRT_source_byte_identity']['changed']is False)
check('same_trace1_macro_and_observer_path_all5_TU',all('-DP4V_TRACE_MODE=1'in c for c in spec['commands'][:2])
 and all('-DP4V_TRACE_MODE=1'in r['original_saved_compile_command']for r in spec['reused_objects'])
 and all(plan['qualified_V_observer']['path']in c for c in spec['commands'][:2])
 and all(plan['qualified_V_observer']['path']in r['original_saved_compile_command']for r in spec['reused_objects']))
check('all_reused_object_MD_source_hashes_match',all(sha(row[f])==row[f+'_sha256']for row in spec['reused_objects']for f in ['object','dependency','source']))
check('exact_qualified_composite_and_original_failed_BUILD01_preserved',sha(COMPOSITE)=='3a04f69aedc861166de04e147046a19ea35500b13e73270acb4e742ec7e9f7f8'
 and load(COMPOSITE)['composite_build_qualified']is True and load(COMPOSITE)['original_BUILD01_engineering_build_qualified']is False)
check('original_pure_transform_receipt_reused_without_new_transform_call',spec['source_transform_receipt']==seam['pure_transform_receipt']
 and spec['transformed_SVC_sha256']==seam['pure_transform_output_sha256']=='23dbc4882fc641046fdcf0c624816d4eb3b0116aeb2890a209891e20afa47c65')
check('runtime_transform_before_compile_receipt_strict_gate',rt.index('changed,proof=transform.instrument_svc(')<rt.index("for index,command in enumerate(spec['commands'][:2])")
 and "proof==spec['source_transform_receipt']"in rt and "write_once(svc,changed)"in rt)
check('prior_four_numeric_fields_and_certificate_unbound',all(spec['prior'][k]is None for k in ['ledger','ledger_sha256','wall_s','cpu_s'])and spec['independent_review_certificate']is None)
check('all_five_execution_flags_false',all(spec[k]is False for k in ['frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']))
check('fixed30_60_total25_50_working_budget',spec['budget']=={'wall_s':30,'cpu_s':60}and spec['working_budget']=={'wall_s':25,'cpu_s':50}
 and 'time.monotonic()-started<25 and cpu()-before_cpu+live<50'in rt)
check('zero_binary_query_solve_VI_formal',all(spec[k]==0 for k in ['binary_execution_calls','query_calls','solve_calls','new_VI_candidate_constructions','formal_table_I_calls']))
bound=spec['bound_files_sha256'];check('all723_pre_prior_binding_bytes_current',len(bound)==723 and all(sha(n)==w for n,w in bound.items()),len(bound))
observed=set()
for n,w in deps['source_MD_files_sha256'].items():
 assert sha(n)==w
 logical=p(n).read_bytes().replace(b'\\\n',b' ').decode();observed.update(str(Path(v).resolve(strict=True))for v in shlex.split(logical.split(':',1)[1]))
check('saved6_MD_exact681_union_no_preprocess',len(deps['source_MD_files_sha256'])==6 and observed==set(deps['actual_saved_dependencies_sha256'])and len(observed)==681
 and deps['new_compiler_or_dependency_preprocessing_calls']==0)
check('managed318_system363_and_PQP5',len(deps['managed_dependencies_sha256'])==318 and len(deps['system_dependencies_sha256'])==363
 and set(Path(n).name for n in deps['PQP_five_headers_sha256'])=={'PQP.h','PQP_Internal.h','PQP_Compile.h','BV.h','Tri.h'})
check('all_saved_MD_union_PQP_prebound',all(bound.get(str(Path(n).resolve()))==w==sha(n)
 for field in ['source_MD_files_sha256','actual_saved_dependencies_sha256','PQP_five_headers_sha256']for n,w in deps[field].items()))
check('three_reused_MD663_previously_reviewed_pool',deps['reused_three_MD_unique_dependency_count']==663 and deps['reused_three_MD_dependencies_match_reviewed_V_pool']is True
 and sha(deps['reviewed_V_pool']['path'])==deps['reviewed_V_pool']['sha256'])
loop=next(v for v in next(v for v in fn(t,'main').body if isinstance(v,ast.Try)).body if isinstance(v,ast.For));body=ast.unparse(loop)
check('first_object_receipt_before_new_actual_dependency_gate',body.index('invoke(')<body.index("'object_sha256': sha(obj)")<body.index('write_once(')<body.index('B.dependency_evidence('))
check('latest_prior_complete_evidence_bound_final_revalidated','record[\'prior\']=validate_prior(spec)'in rt
 and "record['prior']['evidence_sha256']"in rt and "record['prior_after'] = validate_prior(spec)"in rt)
check('new_executor_review_precisely_binds_current_sources_and_plan',"spec['independent_review_certificate']"in rt and "checked['personnel_independent']is True"in rt
 and "(OWN[0],SUPERVISOR,PLAN,DEPENDENCIES)"in rt)
check('D080_actual_scope18k_noVI_or_formal',"scope['formal_table_I_D080']==18000"in rt
 and "scope['VI_future_science_authorized']is False"in rt and "scope['formal_execution_authorized']is False"in rt)
stage=p(spec['stage_root']);run=ROOT/'results/p4_full'/spec['run_name']
check('fresh_stage_run_sidecars_absent',not stage.exists()and not run.exists()and not any(Path(str(run)+s).exists()for s in ['.supervision.time.txt','.supervision.jsonl','.supervision.stderr.log','.supervision.charge.json']))
check('old24_results_not_requalified_native_TCP_separate',spec['old_V_24_physical_results_requalified']is False and spec['native_TCP_results_kept_separate_from_aligned']is True)
inputs=[RUNNER,SUP,DRAFT,PLAN,DEPS,PRE,SEAM,COMPOSITE,BASE,BASE_SUP]
result={'schema':'P4_D080_V_RRT_PCS_EXECUTOR_DRAFT_SELF_STATIC_V1','personnel_independent':False,
 'status':'PASS_SELF_STATIC_ONLY_NOT_EXECUTION_OR_PATH_QUALIFICATION'if all(c['passed']for c in checks)else 'FAIL_SELF_STATIC',
 'checks_total':len(checks),'checks_passed':sum(c['passed']for c in checks),'checks_failed':sum(not c['passed']for c in checks),
 'inputs_sha256':{n:sha(n)for n in inputs},'checks':checks,'self_auditor_sha256':sha(__file__),
 'new_compile_model_binary_scientific_calls':0,'pure_text_transform_calls':0,'prior_bound':False,
 'scope':'Stdlib saved bytes/AST only, no candidate import, transform, describe, compiler, model, binary, claim, freeze, budget charge or commit.',
 'next_gate':'Independent incremental executor review then root binds latest actual III cost ledger and freezes separate protocol.'}
out=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_BUILD_EXECUTOR_SELF_STATIC_20261018.json'
with out.open('x')as f:f.write(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'total':len(checks),'passed':result['checks_passed'],'failed':[c for c in checks if not c['passed']],
 'output_sha256':sha(out)},indent=2))
