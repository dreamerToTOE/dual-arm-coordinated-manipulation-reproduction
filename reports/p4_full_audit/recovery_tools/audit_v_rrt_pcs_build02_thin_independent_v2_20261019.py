#!/usr/bin/env python3
"""Independent BUILD02 seam review after versioned prior-helper correction."""
import hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
checks=[]; inputs={}
def raw(rel):
 p=R/rel; inputs[rel]=sha(p); return p.read_bytes()
def ck(name,passed): checks.append({'name':name,'passed':bool(passed)})
B1='scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py'; B2='scripts/p4_d080/build_v_rrt_pcs_e2e_v2_draft.py'
S1='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v1_draft.py'; S2='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v2_draft.py'
D1='configs/p4_d080/v_rrt_pcs_e2e_build_v1.DRAFT.json'; D2='configs/p4_d080/v_rrt_pcs_e2e_build_v2.DRAFT.json'
H='scripts/p4_d080/validate_prior_preflight_recovery_v2.py'; PLAN='configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'; DEP='configs/p4_d080/v_rrt_pcs_saved_dependency_union_v1.DRAFT.json'
PRE='reports/P4_D080_ENV_V_RRT_PCS_BUILD02_EXECUTOR_PRE_DRAFT_20261018.md'; OLD='reports/P4_D080_ENV_V_RRT_PCS_BUILD_EXECUTOR_INCREMENTAL_INDEPENDENT_PRE_20261018.json'; SEAM='reports/P4_D080_ENV_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_20261018.json'; CHAIN='reports/P4_D080_PREFLIGHT_RECOVERY_CHAIN_THIN_INDEPENDENT_PRE_ADDENDUM_20261018.json'
b1=raw(B1); b2=raw(B2); s1=raw(S1); s2=raw(S2); d1=load(R/D1); d2=load(R/D2); raw(PRE); raw(H); raw(PLAN); raw(DEP); old=load(R/OLD); seam=load(R/SEAM); chain=load(R/CHAIN)
ck('reuse_prior_independent_seams',old['personnel_independent'] is True and old['checks_total']==old['checks_passed']==15 and seam['checks_total']==seam['checks_passed']==20 and chain['checks_total']==chain['checks_passed']==11)
ck('v2_builder_supervisor_and_helper_current','import validate_prior_preflight_recovery_v2 as P' in b2.decode() and sha(R/S2)==inputs[S2] and sha(R/H)==inputs[H])
ck('v1_assets_preserved',sha(R/B1)=='9dbca564ff6d8975ffbca71b3d1e163b9d7a488f1f7f907888075fd05e566958' and sha(R/S1)=='c2ff4dc64b983524c09781d75bad99e99200c4cbd9c9ddb0ca8923a7d21063ae')
normalized=b2.decode().replace('import validate_prior_preflight_recovery_v2 as P\n','').replace('V_RRT_PCS_BUILD02','V_RRT_PCS_BUILD01').replace('v_rrt_pcs_e2e_build_v2','v_rrt_pcs_e2e_build_v1').replace('V_RRT_PCS_BUILD02_EXECUTOR','V_RRT_PCS_BUILD_EXECUTOR').replace(',Path(P.__file__).resolve()]',']').replace('cpu=B.cpu;invoke=B.invoke','cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke').replace('def validate_prior(spec):\n    return P.validate_prior(spec,RUN_NAME,RUN)\n\n\n','').replace('(OWN[0],SUPERVISOR,PLAN,DEPENDENCIES,Path(P.__file__).resolve())','(OWN[0],SUPERVISOR,PLAN,DEPENDENCIES)').replace('V_RRT_PCS_BUILD01_EXECUTOR_PRE_DRAFT','V_RRT_PCS_BUILD_EXECUTOR_PRE_DRAFT')
ck('build02_reverse_identity_restores_v1',normalized==b1.decode())
ck('supervisor_identity_only',s2.decode().replace('V_RRT_PCS_BUILD02','V_RRT_PCS_BUILD01').replace('build_v_rrt_pcs_e2e_v2_draft.py','build_v_rrt_pcs_e2e_v1_draft.py')==s1.decode())
audit=R/'reports/P4_D080_PRIOR_VALIDATOR_V2_INDEPENDENT_AUDIT_20261019.json'; ck('reviewed_helper_v2_independent_audit_bound',audit.is_file() and load(audit)['status']=='PASS')
ck('exact_two_tu_one_link_and_caps',d1['commands']==d2['commands'] and d1['reused_objects']==d2['reused_objects'] and d2['budget']=={'wall_s':30,'cpu_s':60} and d2['working_budget']=={'wall_s':25,'cpu_s':50} and d2['new_compile_calls']==2 and d2['new_link_calls']==1)
ck('draft_execution_flags_remain_closed',d2['run_name']=='20261018_R2_D080_V_RRT_PCS_BUILD02' and all(d2[k] is False for k in ['frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']))
ck('no_new_science_or_vi_calls',all(d2[k]==0 for k in ['binary_execution_calls','query_calls','solve_calls','new_VI_candidate_constructions','formal_table_I_calls']))
failed=[c for c in checks if not c['passed']]
report={'schema':'P4_D080_V_RRT_PCS_BUILD02_THIN_INCREMENTAL_INDEPENDENT_PRE_V2','personnel_independent':True,'status':'PASS_BUILD02_IDENTITY_PRIOR_V2_SEAM' if not failed else 'FAIL_BUILD02_IDENTITY_PRIOR_V2_SEAM','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'failures':failed,'inputs_sha256':inputs,'v2_prior_validator_audit':'reports/P4_D080_PRIOR_VALIDATOR_V2_INDEPENDENT_AUDIT_20261019.json','v2_prior_validator_audit_sha256':sha(audit),'limits':['Engineering build only; no model/query/solve/path qualification.','V1 helper and all prior failed/orphan evidence remain preserved.','V2 helper admits only the digest-bound III cost-only POST and does not qualify external supervision.']}
out=R/'reports/P4_D080_ENV_V_RRT_PCS_BUILD02_THIN_INCREMENTAL_INDEPENDENT_PRE_V2_20261019.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failed':failed,'sha256':sha(out)}))
