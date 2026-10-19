#!/usr/bin/env python3
"""Independent read-only audit of the V3 prior validator and V41 ledger.

The V1/V2 helpers and all historical exceptions remain separate.  This audit
adds exactly one digest-bound V3 NameError cost-only exception and dynamically
validates the complete V41 ledger without starting a build or writing any
experiment artifact.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
V1=R/'scripts/p4_d080/validate_prior_preflight_recovery_v1.py'; V2=R/'scripts/p4_d080/validate_prior_preflight_recovery_v2.py'; V3=R/'scripts/p4_d080/validate_prior_preflight_recovery_v3.py'
LEDGER=R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V41.json'
POST_REL='reports/P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_NAMEERROR_SAVED_INDEPENDENT_POST_20261019.json'; EXEC_REL='results/p4_full/20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY/execution.json'; TIME_REL='results/p4_full/20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY.supervision.time.txt'; CHARGE_REL='results/p4_full/20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY.supervision.charge.json'; RECEIPT_REL='results/p4_full/20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY/cost_receipt.json'
RUN='20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY'; V1_SHA='b315972ce22569684c4fe21dc487fc0456b7db63b8224906020d6fc41911f65e'; V2_SHA=hashlib.sha256(V2.read_bytes()).hexdigest()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path); args=ap.parse_args(); rows=[]; inputs={}
 def raw(p): inputs[str(Path(p).relative_to(R))]=sha(p); return Path(p).read_text()
 def ck(n,v,d=None): rows.append({'name':n,'passed':bool(v),'details':d or {}})
 try:
  s1=raw(V1); s2=raw(V2); s3=raw(V3); ledger=load(LEDGER); post=load(R/POST_REL); e=load(R/EXEC_REL); c=load(R/CHARGE_REL); rc=load(R/RECEIPT_REL)
  for p in [LEDGER,R/POST_REL,R/EXEC_REL,R/TIME_REL,R/CHARGE_REL,R/RECEIPT_REL]: raw(p)
 except Exception as exc:
  report={'schema':'P4_D080_PRIOR_VALIDATOR_V3_V41_INDEPENDENT_AUDIT_V1','status':'FAIL','checks':[],'errors':[repr(exc)]};
  if args.output: args.output.write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps(report)); return 1
 ck('v1_hash_preserved',sha(V1)==V1_SHA,{'actual':sha(V1),'expected':V1_SHA})
 ck('v2_hash_and_source_preserved',V2.is_file() and sha(V2)==V2_SHA,{'sha256':V2_SHA})
 ck('v3_parses_and_imports_v1', 'import validate_prior_preflight_recovery_v1 as V1' in s3 and 'def validate_prior(spec,run_name,run_dir):' in s3)
 basis='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
 ck('v3_single_explicit_nameerror_exception',"v3_nameerror_exception=(row['run_id']==V3_NAMEERROR_RUN and row['charge_basis']=='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE')" in s3)
 ck('v3_exception_combined_with_prior_only', 'exception=iii_exception or prebind_exception or v3_nameerror_exception' in s3)
 ck('v3_post_digest_and_zero_call_gates', 'V3_NAMEERROR_POST_SHA' in s3 and 'V3_NAMEERROR_FAILURE_IDENTITY_AND_ZERO_CALLS_REQUIRED' in s3 and "execution.get('compile_log_sha256')=={}" in s3)
 rows_ledger={r['run_id']:r for r in ledger['executions']}; row=rows_ledger.get(RUN)
 ck('v41_ledger_identity', ledger['schema']=='P4_R2_RECOVERY_ACTUAL_LEDGER_V41' and ledger['count']==58 and row is not None and row['execution_sha256']==sha(R/EXEC_REL) and row['external_post_sha256']==sha(R/POST_REL))
 ck('v3_artifact_hash_bundle', sha(R/EXEC_REL)== 'eff935b8c6e9f401da94a5fcdca91a5341e36797afec75becfbc14d52f972bb5' and sha(R/POST_REL)=='4ae2a6370d5dbbfd4fdf7a5f7ea50a74152532b7e06835fec2c6024a78e0bdcf' and sha(R/TIME_REL)=='5963a001ce68b877689bb07b5263f6600e6828cc594f33d87de13229dc919aca' and sha(R/CHARGE_REL)=='8203f0fb4b56c49eed572ac164cdf834e855342b3ac46d946e324569b79c4c8c' and sha(R/RECEIPT_REL)=='60408c159307ca510a89e6cf77f6b881b1212fdfe3ac1580b8b1c7e913f55e5f')
 ck('v3_failure_boundary',e['status']=='STOP_ENGINEERING_FAILURE_RETAINED_PREFIX' and e.get('error')=="NameError: name 'plan_local' is not defined" and e.get('targets')==[] and not e.get('compile_log_sha256') and e.get('scientific_calls')==0 and post['external_supervision_qualified'] is False and post['external_timing_qualified'] is False and post['external_cost_qualified'] is True)
 ck('v3_post_charge_receipt_binding',post['execution_sha256']==sha(R/EXEC_REL) and post['external_charge_sha256']==sha(R/CHARGE_REL) and post['external_time_sha256']==sha(R/TIME_REL) and post['internal_receipt_sha256']==sha(R/RECEIPT_REL) and c['execution_sha256']==sha(R/EXEC_REL) and c['receipt_sha256']==sha(R/RECEIPT_REL) and rc['execution_sha256']==sha(R/EXEC_REL))
 dynamic={'status':'FAIL'}
 try:
  sys.path.insert(0,str(V3.parent)); import validate_prior_preflight_recovery_v3 as V
  spec={'prior':{'ledger':str(LEDGER.relative_to(R)),'ledger_sha256':sha(LEDGER),'wall_s':ledger['conservative_r2_sum_wall_s'],'cpu_s':ledger['conservative_r2_sum_cpu_s']},'budget':{'wall_s':30,'cpu_s':60}}
  out=V.validate_prior(spec,'INDEPENDENT_V3_V41_AUDIT_DUMMY',R/'results/p4_full/INDEPENDENT_V3_V41_AUDIT_DUMMY'); dynamic={'status':'PASS','wall_s':out['wall_s'],'cpu_s':out['cpu_s'],'evidence_count':len(out['evidence_sha256'])}
 except Exception as exc: dynamic={'status':'FAIL','error':repr(exc)}
 ck('dynamic_v41_validation',dynamic['status']=='PASS',dynamic)
 failed=[x for x in rows if not x['passed']]; report={'schema':'P4_D080_PRIOR_VALIDATOR_V3_V41_INDEPENDENT_AUDIT_V1','status':'PASS' if not failed else 'FAIL','checks_total':len(rows),'checks_passed':len(rows)-len(failed),'checks_failed':len(failed),'checks':rows,'failures':failed,'inputs_sha256':inputs,'ledger':str(LEDGER.relative_to(R)),'ledger_sha256':sha(LEDGER),'interpretation':'PASS binds V1/V2 historical validators plus one explicit V3 NameError cost-only exception; it does not qualify external supervision, build, planning, or scientific execution.'}
 if args.output: args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'checks_total':len(rows),'checks_failed':len(failed),'sha256':sha(args.output) if args.output else None},ensure_ascii=False)); return 0 if not failed else 1
if __name__=='__main__': raise SystemExit(main())
