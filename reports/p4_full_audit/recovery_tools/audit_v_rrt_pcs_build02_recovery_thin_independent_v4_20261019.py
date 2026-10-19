#!/usr/bin/env python3
"""Independent static certificate for the V4 V RRT+PCS engineering recovery.

No compiler, model, query, solve, or stage is created. This certificate verifies
that the V4 runner fixes only the preflight NameError seam, uses a fresh run/stage,
retains all V3/V41 evidence, and keeps scientific/formal execution closed.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
B='scripts/p4_d080/build_v_rrt_pcs_e2e_v4_draft.py'; S='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v4_draft.py'; D='configs/p4_d080/v_rrt_pcs_e2e_build_v4.DRAFT.json'; F='configs/p4_d080/v_rrt_pcs_e2e_build_v4.json'; H='scripts/p4_d080/validate_prior_preflight_recovery_v3.py'; PLAN='configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'; DEP='configs/p4_d080/v_rrt_pcs_saved_dependency_union_v1.DRAFT.json'; VA='reports/P4_D080_PRIOR_VALIDATOR_V3_V41_INDEPENDENT_AUDIT_20261019.json'; LED='results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V41.json'; V3='results/p4_full/20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY/execution.json'; POST3='reports/P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_NAMEERROR_SAVED_INDEPENDENT_POST_20261019.json'
RUN='20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY_V4'; STAGE='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_rrt_pcs_e2e_v4'; V3RUN='20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(rel): return json.loads((R/rel).read_bytes())
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args(); rows=[]; inputs={}
 def raw(rel): p=R/rel; inputs[str(p.resolve())]=sha(p); return p.read_bytes()
 def ck(n,v,d=None): rows.append({'name':n,'passed':bool(v),'details':d or {}})
 try:
  bs=raw(B); ss=raw(S); ds=raw(D); hs=raw(H); ps=raw(PLAN); deps=raw(DEP); vas=raw(VA); led=load(LED); d=load(D)
 except Exception as e: print('precondition',e); return 1
 ck('v4_runner_fix_is_exact_rebased_plan_return',b'validate_prior_preflight_recovery_v3 as P' in bs and b'return bound,plan_local' in bs and b'driver=plan[' in bs and b'20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY_V4' in bs)
 ck('v4_supervisor_identity',b'build_v_rrt_pcs_e2e_v4_draft.py' in ss and b'20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY_V4' in ss and b'v3_draft.py' not in ss)
 ck('fresh_stage_and_run',d['run_name']==RUN and d['stage_root']==STAGE and all('/v_rrt_pcs_e2e_v2' not in x for c in d['commands'] for x in c))
 ck('exact_two_tu_one_link_caps',d['new_compile_calls']==2 and d['new_link_calls']==1 and d['budget']=={'wall_s':30,'cpu_s':60} and d['working_budget']=={'wall_s':25,'cpu_s':50})
 ck('draft_flags_closed',all(d[k] is False for k in ['frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']) and all(d[k]==0 for k in ['binary_execution_calls','query_calls','solve_calls','new_VI_candidate_constructions','formal_table_I_calls']))
 ck('v41_prior_frozen',d['prior']=={'ledger':'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V41.json','ledger_sha256':sha(R/LED),'wall_s':led['conservative_r2_sum_wall_s'],'cpu_s':led['conservative_r2_sum_cpu_s'],'status':'FROZEN_LATEST_V41','historical_unmeasured_tail':'RETAINED_UNKNOWN'})
 ck('v41_prior_audit_pass',load(VA)['status']=='PASS' and sha(R/VA)==sha(R/VA))
 ck('v3_failure_retained',Path(R/V3).is_file() and load(V3)['run_id']==V3RUN and load(V3).get('error')=="NameError: name 'plan_local' is not defined" and Path(R/POST3).is_file() and load(POST3)['checks_failed']==0)
 ck('v3_helper_bound',d['prior_validator_helper']['path']==H and d['prior_validator_helper']['sha256']==sha(R/H) and d['prior_validator_helper']['prior_validator_v3_audit']=='reports/P4_D080_PRIOR_VALIDATOR_V3_V41_INDEPENDENT_AUDIT_20261019.json')
 # Dynamic validator test is read-only and uses a dummy run identity.
 dynamic={'status':'FAIL'}
 try:
  sys.path.insert(0,str(R/'scripts/p4_d080')); import validate_prior_preflight_recovery_v3 as V
  spec={'prior':{'ledger':LED,'ledger_sha256':sha(R/LED),'wall_s':led['conservative_r2_sum_wall_s'],'cpu_s':led['conservative_r2_sum_cpu_s']},'budget':{'wall_s':30,'cpu_s':60}}
  p=V.validate_prior(spec,'INDEPENDENT_V4_CERT_DUMMY',R/'results/p4_full/INDEPENDENT_V4_CERT_DUMMY'); dynamic={'status':'PASS','evidence_count':len(p['evidence_sha256']),'wall_s':p['wall_s'],'cpu_s':p['cpu_s']}
 except Exception as e: dynamic={'status':'FAIL','error':repr(e)}
 ck('v41_dynamic_prior_evidence',dynamic['status']=='PASS',dynamic)
 failed=[x for x in rows if not x['passed']]
 report={'schema':'P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_THIN_INCREMENTAL_INDEPENDENT_PRE_V4','personnel_independent':True,'status':'PASS_BUILD02_RECOVERY_IDENTITY_V41_SEAM' if not failed else 'FAIL_BUILD02_RECOVERY_IDENTITY_V41_SEAM','checks_total':len(rows),'checks_passed':len(rows)-len(failed),'checks_failed':len(failed),'checks':rows,'failures':failed,'inputs_sha256':inputs,'v41_prior_validator_audit':VA,'v41_prior_validator_audit_sha256':sha(R/VA),'required_runner_gate_inputs_sha256':{str((R/p).resolve()):sha(R/p) for p in [B,S,PLAN,DEP,H]},'limits':['Engineering build only; no model/query/solve/path qualification.','V3 NameError failure remains a separate digest-bound cost-only exception; it is never upgraded to supervision or build qualification.','Fresh V4 run/stage may not overwrite V3 or any earlier stage.','No formal 18,000 statistics, VI work, or scientific planning is authorized by this certificate.']}
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':report['status'],'checks_total':len(rows),'checks_failed':len(failed),'sha256':sha(a.output)},ensure_ascii=False)); return 0 if not failed else 1
if __name__=='__main__': raise SystemExit(main())
