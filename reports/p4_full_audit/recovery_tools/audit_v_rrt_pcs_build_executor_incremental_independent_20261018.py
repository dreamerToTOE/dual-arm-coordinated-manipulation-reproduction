#!/usr/bin/env python3
"""Thin V2TU engineering PRE. AST/saved maps only; no candidate import or transform."""
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
def fn(t,n):return next(z for z in t.body if isinstance(z,ast.FunctionDef) and z.name==n)
def dump(n):return ast.dump(n,include_attributes=False)
R='scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py'
S='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v1_draft.py'
I='scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py'
IS='scripts/p4_d080/supervise_iii_rrt_pcs_e2e_build_v1_draft.py'
P='configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'
D='configs/p4_d080/v_rrt_pcs_saved_dependency_union_v1.DRAFT.json'
C='configs/p4_d080/v_rrt_pcs_e2e_build_v1.DRAFT.json'
PRE='reports/P4_D080_ENV_V_RRT_PCS_BUILD_EXECUTOR_PRE_DRAFT_20261018.md'
SEAM='reports/P4_D080_ENV_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
spec=js(C);plan=js(P);deps=js(D);seam=js(SEAM);txt=raw(R).decode();t=tree(R);base=tree(I);checks=[]
def ck(n,v,e=None):checks.append(dict(name=n,passed=bool(v),evidence=e))
ck('stable_new_executor_and_saved_union_exact',sha(R)=='9dbca564ff6d8975ffbca71b3d1e163b9d7a488f1f7f907888075fd05e566958' and sha(S)=='c2ff4dc64b983524c09781d75bad99e99200c4cbd9c9ddb0ca8923a7d21063ae' and sha(C)=='f2b3120cfa9ee950ddc1d596f51980804752975763577ecd80487f99061a0a7a' and sha(D)=='ec9359321fb0cf072302bf6a361d9237ad4c5d9d25e4e0d5a75ea0b064214ea5')
ck('prior20_source_seams_certificate_reused_not_transformed_or_reaudited',sha(SEAM)=='d5f05c246a2a7cfafc5183e3166bde9bd2ce47ab42d3da9dd43b3df72ac1f858' and seam['personnel_independent'] is True and seam['checks_total']==seam['checks_passed']==20 and seam['checks_failed']==0 and spec['source_transform_receipt']==seam['pure_transform_receipt'] and spec['transformed_SVC_sha256']==seam['pure_transform_output_sha256'] and sha(P)=='1c320aa3d55a638124b86b1235445c0aac80857dd4313dcb4d8c060f802d55fe')
ck('exact_III_and_V_infrastructure_reused_direct_aliases',sha(I)=='a3035ab09ade161811026eb08fc0523ab07f7adde3da86cd431cabcfddc3eabe' and sha(IS)=='661dbc63efadbfa1031b4ce248d9f7aebde6b5484e5582826ed3383627db132a' and all(z in txt for z in ['validate_supervision=I.validate_supervision;active_d080=I.active_d080','cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke','lifecycle=B.lifecycle;compiler_group_members=B.compiler_group_members','evidence=B.dependency_evidence(dep,obj,source,staged,bound,state)']))
ck('original_module_source_path_saved_before_runtime_identity_metadata_switch',txt.index('Path(I.__file__).resolve()')<txt.index('I.__file__=__file__') and 'sha(OWN[5])==I_SOURCE_SHA' in txt and 'I.RUN_NAME=RUN_NAME;I.SUPERVISOR=SUPERVISOR' in txt)
old=raw(IS).decode();new=raw(S).decode();sub=[('20261018_R2_D080_III_RRT_PCS_BUILD01','20261018_R2_D080_V_RRT_PCS_BUILD01'),('ENGINEERING_BUILD_ONLY_III_RRT_PCS_UNCHANGED_QUALIFIED_COMPONENTS','ENGINEERING_BUILD_ONLY_V_RRT_PCS_2TU1LINK_ORIGINAL_RRT_CONTROL'),('scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py','scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py'),("spec['environment']=='III'","spec['environment']=='V'"),('P4_D080_III_RRT_PCS_BUILD_FROZEN_V1','P4_D080_V_RRT_PCS_BUILD_FROZEN_V1'),('EXPLICIT_FROZEN_III_RRT_PCS_BUILD_REQUIRED','EXPLICIT_FROZEN_V_RRT_PCS_BUILD_REQUIRED'),('P4_D080_III_RRT_PCS_BUILD_EXTERNAL_COST_CHARGE_V1','P4_D080_V_RRT_PCS_BUILD_EXTERNAL_COST_CHARGE_V1'),("{'wall_s':45,'cpu_s':90}","{'wall_s':30,'cpu_s':60}"),('min(45.,3600.','min(30.,3600.'),('min(90.,7200.','min(60.,7200.'),('dict(wall=wall>45.,cpu=cpu>90.)','dict(wall=wall>30.,cpu=cpu>60.)')];counts=[]
for a,z in sub:counts.append([old.count(a),new.count(z)]);new=new.replace(z,a)
ck('supervisor_exact11_inverse_identity_budget_substitutions',new==old and counts==[[1,1]]*11,counts)
old_final=next(z for z in fn(base,'main').body if isinstance(z,ast.Try)).finalbody;new_final=copy.deepcopy(next(z for z in fn(t,'main').body if isinstance(z,ast.Try)).finalbody)
for z in ast.walk(ast.Module(body=new_final,type_ignores=[])):
    if isinstance(z,ast.Constant):
        if z.value=='P4_D080_V_RRT_PCS_BUILD_COST_RECEIPT_V1':z.value='P4_D080_III_RRT_PCS_BUILD_COST_RECEIPT_V1'
        elif type(z.value) in (int,float) and z.value in (30,60):z.value={30:45,60:90}[z.value]
ck('all17_cleanup_finalhash_prior_log_and_receipt_statements_exact_except_caps_schema',len(old_final)==len(new_final)==17 and all(dump(a)==dump(b) for a,b in zip(old_final,new_final)))
ck('original_twoTU_oneLink_plan_and_three_old_object_identities_exact',spec['commands']==plan['commands'] and len(spec['commands'])==3 and spec['new_compile_calls']==2 and spec['new_link_calls']==1 and spec['reused_objects']==plan['reused_objects'] and len(spec['reused_objects'])==3 and all(sha(z[f])==z[f+'_sha256'] for z in spec['reused_objects'] for f in ['object','dependency','source']))
ck('only_previously_reviewed_pure_transform_input_output_receipt_accepted',txt.index('changed,proof=transform.instrument_svc(')<txt.index("for index,command in enumerate(spec['commands'][:2])") and "proof==spec['source_transform_receipt']" in txt and "hashlib.sha256(changed).hexdigest()==spec['transformed_SVC_sha256']" in txt and 'write_once(svc,changed)' in txt)
loop=next(z for z in next(z for z in fn(t,'main').body if isinstance(z,ast.Try)).body if isinstance(z,ast.For));body=ast.unparse(loop)
ck('immediate_new_object_MD_SHA_receipt_before_dependency_gate',body.index('invoke(')<body.index("'object_sha256': sha(obj)")<body.index('write_once(')<body.index('B.dependency_evidence('))
union=set()
for n,v in deps['source_MD_files_sha256'].items():
    if sha(n)!=v:raise ValueError('SAVED_MD_CHANGED')
    union.update(str(Path(z).resolve(strict=True)) for z in shlex.split(raw(n).replace(b'\\\n',b' ').decode().split(':',1)[1]))
bound=spec['bound_files_sha256']
ck('six_saved_MD_exact681union_318managed363system_prebound_without_fullhash',len(deps['source_MD_files_sha256'])==6 and union==set(deps['actual_saved_dependencies_sha256']) and len(union)==681 and len(deps['managed_dependencies_sha256'])==318 and len(deps['system_dependencies_sha256'])==363 and {**deps['managed_dependencies_sha256'],**deps['system_dependencies_sha256']}==deps['actual_saved_dependencies_sha256'] and all(bound.get(str(p(n).resolve()))==v for field in ['source_MD_files_sha256','actual_saved_dependencies_sha256','PQP_five_headers_sha256'] for n,v in deps[field].items()) and len(bound)==723)
ck('reused_three_MD663_saved_pool_and_five_PQP_headers_explicit',deps['reused_three_MD_unique_dependency_count']==663 and deps['reused_three_MD_dependencies_match_reviewed_V_pool'] is True and set(Path(n).name for n in deps['PQP_five_headers_sha256'])=={'PQP.h','PQP_Internal.h','PQP_Compile.h','BV.h','Tri.h'} and deps['new_compiler_or_dependency_preprocessing_calls']==deps['new_model_or_scientific_calls']==0)
ck('runtime_new_MD_protected_gate_and_prior_beforeafter_retained',"record['prior']=validate_prior(spec)" in txt and "record['prior_after'] = validate_prior(spec)" in txt and "record['prior']['evidence_sha256']" in txt and 'B.dependency_evidence(dep,obj,source,staged,bound,state)' in txt)
ck('strict_new_executor_independent_certificate_precisely_binds_four_sources',"spec['independent_review_certificate']" in txt and "checked['personnel_independent']is True" in txt and '(OWN[0],SUPERVISOR,PLAN,DEPENDENCIES)' in txt)
ck('fixed30_60_work25_50_unbound_prior_nonexecutable_flags',spec['budget']=={'wall_s':30,'cpu_s':60} and spec['working_budget']=={'wall_s':25,'cpu_s':50} and 'time.monotonic()-started<25 and cpu()-before_cpu+live<50' in txt and all(spec[k] is False for k in ['frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']) and spec['independent_review_certificate'] is None and all(spec['prior'][k] is None for k in ['ledger','ledger_sha256','wall_s','cpu_s']))
ck('fresh_stage_run_no_VI_formal_or_model_execution',not p(spec['stage_root']).exists() and not (ROOT/'results/p4_full'/spec['run_name']).exists() and all(spec[k]==0 for k in ['binary_execution_calls','query_calls','solve_calls','new_VI_candidate_constructions','formal_table_I_calls']) and spec['old_V_24_physical_results_requalified'] is False and spec['native_TCP_results_kept_separate_from_aligned'] is True)
failed=[z for z in checks if not z['passed']]
report={'schema':'P4_D080_V_RRT_PCS_BUILD_EXECUTOR_INCREMENTAL_INDEPENDENT_PRE_V1','personnel_independent':True,'status':'PASS_THIN_ENGINEERING_EXECUTOR_ONLY' if not failed else 'FAIL_ENGINEERING_EXECUTOR_PRE','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'inputs_sha256':{n:sha(n) for n in [R,S,P,D,C,PRE,I,IS,SEAM]},'auditor_sha256':sha(__file__),'source_seams20_reused_without_rerun':True,'full_bound723_hash_repeated':False,'new_transform_compile_binary_model_scientific_calls':0,'allowed_root_freeze_transform':{'preserve_DRAFT':True,'new_formal_config_required':True,'flags_to_true':['frozen','independent_review_passed','engineering_execution_authorized'],'flags_stay_false':['scientific_execution_authorized','formal_execution_authorized'],'latest_prior':'Bind latest charged ledger after III SOURCE01 actual POST; preserve723 bindings, add complete current ledger/evidence and this certificate/auditor SHA; no conflicting overwrite. Runtime reused validate_prior enforces complete actual set again.','independent_review_certificate':'Exact path/SHA of this report.','status_and_prior_status_metadata_only':'Frozen engineering only.','conditions_unchanged':'2newTU+1link,3same old objects,known exact pure-transform output/receipt,same TRACE1 originalRRT/geometry/thresholds,30wall60CPU/work25wall50CPU,zero scientific calls; commit OWN/template/formal config before root unique supervisor.'},'limitations':['Engineering only; output can only be BUILT_NOT_QUERIED, never planning/path qualification.','Original V BUILD01 STOP and old24 physical source outcomes remain; no repeated old model or path tests.','No fresh dependency discovery: future real MD must still pass frozen protected-header gate.','No extra R2 total budget; VI974 archival/formal0/18000 remain.']}
out=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_BUILD_EXECUTOR_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
with out.open('x') as stream:stream.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks_total':len(checks),'failed':failed,'sha256':sha(out)},ensure_ascii=False,indent=2))
