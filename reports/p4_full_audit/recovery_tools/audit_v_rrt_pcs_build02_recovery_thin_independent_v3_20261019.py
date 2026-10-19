#!/usr/bin/env python3
"""Independent static certificate for the versioned V BUILD02 recovery seam.

This audit creates no stage, compiler output, model, query, or planning result.
It checks that the v3 recovery identity is a new run/stage, preserves the
reviewed v2/v1 assets, binds the V40 prior ledger and its two declared
cost-only exceptions, and keeps all scientific/formal execution flags closed.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(rel): return json.loads((R/rel).read_bytes())
checks=[]; inputs={}
def raw(rel):
 p=R/rel; inputs[rel]=sha(p); return p.read_bytes()
def ck(name,passed,details=None): checks.append({'name':name,'passed':bool(passed),'details':details or {}})

B1='scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py'; B2='scripts/p4_d080/build_v_rrt_pcs_e2e_v2_draft.py'; B3='scripts/p4_d080/build_v_rrt_pcs_e2e_v3_draft.py'
S1='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v1_draft.py'; S2='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v2_draft.py'; S3='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v3_draft.py'
D2='configs/p4_d080/v_rrt_pcs_e2e_build_v2.DRAFT.json'; D3='configs/p4_d080/v_rrt_pcs_e2e_build_v3.DRAFT.json'; F3='configs/p4_d080/v_rrt_pcs_e2e_build_v3.json'
H='scripts/p4_d080/validate_prior_preflight_recovery_v2.py'; PLAN='configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'; DEP='configs/p4_d080/v_rrt_pcs_saved_dependency_union_v1.DRAFT.json'
PRE='reports/P4_D080_ENV_V_RRT_PCS_BUILD02_EXECUTOR_PRE_DRAFT_20261018.md'; OLD='reports/P4_D080_ENV_V_RRT_PCS_BUILD_EXECUTOR_INCREMENTAL_INDEPENDENT_PRE_20261018.json'; SEAM='reports/P4_D080_ENV_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_20261018.json'; CHAIN='reports/P4_D080_PREFLIGHT_RECOVERY_CHAIN_THIN_INDEPENDENT_PRE_ADDENDUM_20261018.json'
VA='reports/P4_D080_PRIOR_VALIDATOR_V2_V40_INDEPENDENT_AUDIT_20261019.json'; LEDGER='results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V40.json'
b1=raw(B1); b2=raw(B2); b3=raw(B3); s1=raw(S1); s2=raw(S2); s3=raw(S3); d2=load(D2); d3=load(D3); f3=load(F3)
for rel in [PRE,H,PLAN,DEP,OLD,SEAM,CHAIN,VA,LEDGER]: raw(rel)
ck('prior_independent_seams_retained',load(OLD)['personnel_independent'] is True and load(OLD)['checks_total']==load(OLD)['checks_passed']==15 and load(SEAM)['checks_total']==load(SEAM)['checks_passed']==20 and load(CHAIN)['checks_total']==load(CHAIN)['checks_passed']==11)
ck('v1_v2_assets_preserved',sha(R/B1)=='9dbca564ff6d8975ffbca71b3d1e163b9d7a488f1f7f907888075fd05e566958' and sha(R/S1)=='c2ff4dc64b983524c09781d75bad99e99200c4cbd9c9ddb0ca8923a7d21063ae' and sha(R/B2)=='ef99d36c8d2447d62598deab0f6cd03fe5b294b674ba5b16ea2c83e24277c2a8' and sha(R/S2)=='8bb22cbfa98e21da20ca5cc8a93134e5a5d668fea8b7f1c879064ee16e0b3cb9')
ck('v3_builder_uses_versioned_helper_and_rebase', 'import validate_prior_preflight_recovery_v2 as P' in b3.decode() and 'rebase_stage_paths' in b3.decode() and '/v_rrt_pcs_e2e_v2' in b3.decode() and '20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY' in b3.decode() and 'v_rrt_pcs_e2e_build_v3.DRAFT.json' in b3.decode())
ck('v3_supervisor_identity', 'build_v_rrt_pcs_e2e_v3_draft.py' in s3.decode() and '20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY' in s3.decode() and 'v2_draft.py' not in s3.decode())
ck('exact_two_tu_one_link_and_caps', d3['commands'] and all('/v_rrt_pcs_e2e_v1' not in x for c in d3['commands'] for x in c) and d3['new_compile_calls']==2 and d3['new_link_calls']==1 and d3['budget']=={'wall_s':30,'cpu_s':60} and d3['working_budget']=={'wall_s':25,'cpu_s':50})
ck('draft_flags_closed', d3['run_name']=='20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY' and d3['stage_root']=='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_rrt_pcs_e2e_v2' and all(d3[k] is False for k in ['frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']))
ck('draft_no_science_calls', all(d3[k]==0 for k in ['binary_execution_calls','query_calls','solve_calls','new_VI_candidate_constructions','formal_table_I_calls']))
ck('frozen_identity_and_scope_closed', f3['frozen'] is True and f3['independent_review_passed'] is True and f3['engineering_execution_authorized'] is True and f3['scientific_execution_authorized'] is False and f3['formal_execution_authorized'] is False and f3['environment']=='V' and f3['run_name']=='20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY')
ck('frozen_prior_v40', f3['prior']=={'ledger':'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V40.json','ledger_sha256':'41403b13d1f1152a4d1e079677ba527b74753c293751b400cf69abe217d3bf04','wall_s':1155.5503393179733,'cpu_s':980.01229,'status':'FROZEN_LATEST_V40','historical_unmeasured_tail':'RETAINED_UNKNOWN'})
ck('v40_prior_audit_pass', load(VA)['status']=='PASS' and sha(R/VA)==f3['prior_validator_helper']['prior_validator_v2_audit_sha256'])
ck('v40_bound_map_contains_new_audit', f3['bound_files_sha256'].get(str((R/VA).resolve()))==sha(R/VA))
ck('new_supervision_sidecars', all(f3['external_supervision'][k].startswith('results/p4_full/20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY.') for k in ['sibling_path','metadata_path','stderr_path','charge_path']))
# Validate every prior evidence digest using the reviewed helper; this is read-only.
try:
 sys.path.insert(0,str(R/'scripts/p4_d080')); import validate_prior_preflight_recovery_v2 as V
 led=load(LEDGER); spec={'prior':{'ledger':LEDGER,'ledger_sha256':sha(R/LEDGER),'wall_s':led['conservative_r2_sum_wall_s'],'cpu_s':led['conservative_r2_sum_cpu_s']},'budget':{'wall_s':30,'cpu_s':60}}
 prior=V.validate_prior(spec,'INDEPENDENT_V3_CERT_DUMMY',R/'results/p4_full/INDEPENDENT_V3_CERT_DUMMY')
 missing={k:v for k,v in prior['evidence_sha256'].items() if f3['bound_files_sha256'].get(k)!=v}
 ck('v40_dynamic_prior_evidence_prebound', not missing, {'evidence_count':len(prior['evidence_sha256']),'missing':missing})
except Exception as exc: ck('v40_dynamic_prior_evidence_prebound',False,{'error':repr(exc)})
cert_rel='reports/P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_THIN_INCREMENTAL_INDEPENDENT_PRE_V3_20261019.json'
bound_without_self={k:v for k,v in f3['bound_files_sha256'].items() if Path(k).resolve()!=(R/cert_rel).resolve()}
ck('all_frozen_bound_files_exist_and_match', all(Path(k).is_file() and sha(Path(k))==v for k,v in bound_without_self.items()), {'bound_count':len(f3['bound_files_sha256']),'self_binding_deferred':True})
# The runner's certificate gate requires these exact inputs.  Include their digest map.
required_inputs=[B3,S3,PLAN,DEP,H]
ck('certificate_required_inputs_exist', all((R/p).is_file() for p in required_inputs))
failed=[c for c in checks if not c['passed']]
report={'schema':'P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_THIN_INCREMENTAL_INDEPENDENT_PRE_V3','personnel_independent':True,'status':'PASS_BUILD02_RECOVERY_IDENTITY_V40_SEAM' if not failed else 'FAIL_BUILD02_RECOVERY_IDENTITY_V40_SEAM','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'failures':failed,'inputs_sha256':inputs,'v40_prior_validator_audit':VA,'v40_prior_validator_audit_sha256':sha(R/VA),'limits':['Engineering build only; no model/query/solve/path qualification.','The V40 prebind failure remains a digest-bound cost-only exception with external_supervision_qualified=false and zero compile/model/query/solve calls.','The fresh v3 stage/run identity may not overwrite the retained v2 failure run or any old stage.','No formal 18,000 statistics, VI work, or scientific planning is authorized by this certificate.']}
# Add exact required input digests explicitly (also included above via raw).
report['required_runner_gate_inputs_sha256']={p:inputs[p] for p in required_inputs}
out=R/'reports/P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_THIN_INCREMENTAL_INDEPENDENT_PRE_V3_20261019.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks_total':len(checks),'checks_failed':len(failed),'sha256':sha(out),'failures':failed},ensure_ascii=False))
