#!/usr/bin/env python3
"""Only BUILD01-to-BUILD02 identity/prior seam; reuse prior independent15/20."""
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[3];inputs={};checks=[]
def raw(n):
 v=(R/n).read_bytes();inputs[n]=hashlib.sha256(v).hexdigest();return v
def src(n):return raw(n).decode()
def js(n):return json.loads(raw(n))
def ck(n,v):checks.append(dict(name=n,passed=bool(v)))
B1='scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py';B2='scripts/p4_d080/build_v_rrt_pcs_e2e_v2_draft.py';S1='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v1_draft.py';S2='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v2_draft.py';D1='configs/p4_d080/v_rrt_pcs_e2e_build_v1.DRAFT.json';D2='configs/p4_d080/v_rrt_pcs_e2e_build_v2.DRAFT.json';H='scripts/p4_d080/validate_prior_preflight_recovery_v1.py';PLAN='configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json';DEP='configs/p4_d080/v_rrt_pcs_saved_dependency_union_v1.DRAFT.json';PRE='reports/P4_D080_ENV_V_RRT_PCS_BUILD02_EXECUTOR_PRE_DRAFT_20261018.md'
b1=src(B1);b2=src(B2);s1=src(S1);s2=src(S2);d1=js(D1);d2=js(D2);src(PRE);src(H);raw(PLAN);raw(DEP)
oldpre='reports/P4_D080_ENV_V_RRT_PCS_BUILD_EXECUTOR_INCREMENTAL_INDEPENDENT_PRE_20261018.json';p=js(oldpre)
sourcepre='reports/P4_D080_ENV_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_20261018.json';q=js(sourcepre)
chain='reports/P4_D080_PREFLIGHT_RECOVERY_CHAIN_THIN_INDEPENDENT_PRE_ADDENDUM_20261018.json';c=js(chain)
ck('reuse_independent15_executor_and20_source_seams_exact_no_old_rerun',inputs[oldpre]=='7180af339dbff9f9360208f444d49e4b25e790d55e47e19789183c69fd7f7112' and p['personnel_independent']is True and p['checks_total']==p['checks_passed']==15 and p['checks_failed']==0 and inputs[sourcepre]=='d5f05c246a2a7cfafc5183e3166bde9bd2ce47ab42d3da9dd43b3df72ac1f858' and q['checks_total']==q['checks_passed']==20 and q['checks_failed']==0)
ck('stable_BUILD02_executor_supervisor_plan_union_and_helper',inputs[B2]=='85cbaffb82010ca066913888907415e13a3fc32a910f55a61c80981167cc9f46' and inputs[S2]=='8bb22cbfa98e21da20ca5cc8a93134e5a5d668fea8b7f1c879064ee16e0b3cb9' and inputs[D2]=='0ebb9caa107e75c5468eff889fd082871c64dc3988d3378b463e08de7f2039e1' and inputs[H]=='b315972ce22569684c4fe21dc487fc0456b7db63b8224906020d6fc41911f65e' and inputs[PLAN]==p['inputs_sha256'][PLAN] and inputs[DEP]==p['inputs_sha256'][DEP])
x=b2.replace('import validate_prior_preflight_recovery_v1 as P\n','',1).replace('V_RRT_PCS_BUILD02','V_RRT_PCS_BUILD01').replace('v_rrt_pcs_e2e_build_v2','v_rrt_pcs_e2e_build_v1').replace('V_RRT_PCS_BUILD02_EXECUTOR','V_RRT_PCS_BUILD_EXECUTOR').replace(',Path(P.__file__).resolve()]',']',1).replace('cpu=B.cpu;invoke=B.invoke','cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke',1).replace('def validate_prior(spec):\n    return P.validate_prior(spec,RUN_NAME,RUN)\n\n\n','',1).replace('(OWN[0],SUPERVISOR,PLAN,DEPENDENCIES,Path(P.__file__).resolve())','(OWN[0],SUPERVISOR,PLAN,DEPENDENCIES)',1)
# PRE's historical name had no BUILD01 numeral.
x=x.replace('V_RRT_PCS_BUILD01_EXECUTOR_PRE_DRAFT','V_RRT_PCS_BUILD_EXECUTOR_PRE_DRAFT')
ck('BUILD02_reverse_identity_and_reviewed_helper_seam_restores_v1_byte_exact',x==b1)
ck('supervisor_changes_only_new_RUN_and_runner_filename',s2.replace('V_RRT_PCS_BUILD02','V_RRT_PCS_BUILD01').replace('build_v_rrt_pcs_e2e_v2_draft.py','build_v_rrt_pcs_e2e_v1_draft.py')==s1)
ck('new_prior_helper_independent11_exact_and_single_exception_no_budget_relaxation',inputs[chain]=='17e47992e46e1b9ae0eee6242c71edda90e3e0ce559332e867ce1ceed728cba3' and c['checks_total']==c['checks_passed']==11 and c['checks_failed']==0 and 'return P.validate_prior(spec,RUN_NAME,RUN)'in b2)
unchanged=['commands','reused_objects','binary','stage_root','budget','working_budget','new_compile_calls','new_link_calls','source_transform_receipt']
ck('same_exact_twoTU_oneLINK_three_reused_objects_transform_and_resource_caps',all(d1[k]==d2[k]for k in unchanged) and d2['new_compile_calls']==2 and d2['new_link_calls']==1 and len(d2['reused_objects'])==3 and d2['budget']=={'wall_s':30,'cpu_s':60} and d2['working_budget']=={'wall_s':25,'cpu_s':50})
ck('engineering_only_unfrozen_DRAFT_and_unique_new_RUN',d2['run_name']=='20261018_R2_D080_V_RRT_PCS_BUILD02' and all(d2[k]is False for k in ['frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']) and 'EXACT_NEW_EXECUTOR_AND_PLAN_INDEPENDENT_REVIEW_REQUIRED'in b2)
ck('old_v1_source_preserved_and_old_original_attempt_not_relabelled',inputs[B1]==p['inputs_sha256'][B1] and inputs[S1]==p['inputs_sha256'][S1] and "RUN_NAME='20261018_R2_D080_V_RRT_PCS_BUILD01'"in b1)
failed=[z for z in checks if not z['passed']]
report=dict(schema='P4_D080_V_RRT_PCS_BUILD02_THIN_INCREMENTAL_INDEPENDENT_PRE_V1',personnel_independent=True,status='PASS_BUILD02_IDENTITY_AND_PRIOR_SEAM'if not failed else'FAIL_BUILD02_IDENTITY_AND_PRIOR_SEAM',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,inputs_sha256=inputs,source_seams20_reused_without_rerun=True,old_executor15_reused_without_rerun=True,full_bound_union_hash_repeated=False,new_transform_compile_binary_model_scientific_calls=0,allowed_root_freeze_transform={'preserve_DRAFT':True,'new_formal_config_required':True,'flags_to_true':['frozen','independent_review_passed','engineering_execution_authorized'],'flags_stay_false':['scientific_execution_authorized','formal_execution_authorized'],'latest_prior':'Bind latest actual charged ledger, complete evidence, this certificate and auditor, reviewed helper-chain certificate; no conflicting overwrite.','independent_review_certificate':'Exact path/SHA of this new report.','conditions_unchanged':'2newTU+1link/3same objects/TRACE1/30wall60CPU/work25wall50CPU/0modelbinaryscience. Commit runner/supervisor/template/PRE/helper and formal config before unique launch.'},limits=['Engineering build only; no model/query/solve/path qualification.','Original BUILD01 rejected preflight and saved-only recovery cost retain their identity and failure.','Only new BUILD02 identity and independently reviewed helper seam; no repeated union or old science review.'])
out=R/'reports/P4_D080_ENV_V_RRT_PCS_BUILD02_THIN_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
with out.open('x')as f:f.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps(dict(checks=len(checks),failed=failed,sha256=hashlib.sha256(out.read_bytes()).hexdigest())))
