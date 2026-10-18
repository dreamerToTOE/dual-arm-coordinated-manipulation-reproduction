#!/usr/bin/env python3
"""Thin saved-only recovery-index POST. No runtime, model, compile or Git work."""
from decimal import Decimal
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[3]
RUN='20261018_R2_D080_V_RRT_PCS_BUILD01'
EP='results/p4_full/'+RUN+'/execution.json'
OLD='reports/P4_D080_ENV_V_RRT_PCS_BUILD01_ORPHAN_SAVED_INDEPENDENT_POST_20261018.json'
OUT='reports/P4_D080_ENV_V_RRT_PCS_BUILD01_RECOVERY_COST_INDEPENDENT_POST_20261018.json'
EXPECTED_EP='6e6b3d9f44a51a2ee2d3dd0f35efce10dc6d2d1090c74d5a13552cc93cd900df'
EXPECTED_OLD='4232c2fb5a00bf8ebc00ad2cf15943d2dfd17282ba3354c42234a381967b1a85'
FILES={
 'charge':('results/p4_full/'+RUN+'.supervision.charge.json','a928bd149ec0084f040f460c0ac771eefdbe2f4fb98514c318a52324ddd0f756'),
 'time':('results/p4_full/'+RUN+'.supervision.time.txt','c8ad42b5726c63bd680400335bb4fb088dc349c8f5a5440fe8461384bc4b329f'),
 'metadata':('results/p4_full/'+RUN+'.supervision.jsonl','158a3e3527db8871b2f024fd0d5d8bf906ccee0ed76b8673c1474bb523598e6d'),
 'stderr':('results/p4_full/'+RUN+'.supervision.stderr.log','6f6ccafe40576c7ff809a94ad3bfb18bda686220e39baba072d4bdf521031191')}
retained={};checks=[]
def raw(n):
 p=R/n;v=p.read_bytes();retained[n]=hashlib.sha256(v).hexdigest();return v
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def load(n):return json.loads(raw(n))
def ck(n,v):checks.append(dict(name=n,passed=bool(v)))
old=load(OLD);e=load(EP);c=load(FILES['charge'][0])
ck('reused_original_nine_check_independent_orphan_certificate_unchanged',sha(OLD)==EXPECTED_OLD and old['personnel_independent'] is True and old['checks_total']==old['checks_passed']==9 and old['checks_failed']==0 and old['external_supervision_qualified'] is False and old['external_cost_qualified'] is old['orphan_preflight_cost_observation_qualified'] is True and old['execution_sha256'] is old['internal_receipt_sha256'] is None)
ck('exact_explicit_post_attempt_saved_only_recovery_record_not_original_runtime',sha(EP)==EXPECTED_EP and e['schema']=='SAVED_ONLY_PREFLIGHT_RECOVERY' and e['run_id']==RUN and e['saved_only_recovery'] is True and e['source_execution_created_during_attempt'] is e['original_runtime_execution_exists'] is e['internal_receipt_exists'] is False and e['status']=='STOP_PRECOMMIT_NO_COMPILER_SAVED_ONLY_RECOVERY')
ck('all_four_original_supervision_files_exact_and_unchanged',all(sha(n)==v for n,v in FILES.values()))
ck('explicit_chain_to_original_independent_orphan_POST_and_charge',e['original_independent_cost_POST']==OLD and e['original_independent_cost_POST_sha256']==EXPECTED_OLD and e['original_charge']==FILES['charge'][0] and e['original_charge_sha256']==FILES['charge'][1] and e['source_commit']==old['failed_source_commit'])
ck('zero_compile_model_binary_query_solve_formal_VI_and_no_qualification_claim',all(type(e[k]) is int and e[k]==0 for k in ('solve_calls','compile_calls','binary_execution_calls','query_calls','formal_table_I_calls','new_VI_candidate_constructions')) and e['engineering_only'] is True and e['engineering_build_qualified'] is e['external_supervision_qualified'] is e['independent_path_qualified'] is False)
ck('original_null_execution_receipt_exit1_incomplete_monotonic_flags_remain',c['execution_sha256'] is c['receipt_sha256'] is None and c['monotonic_envelope_valid'] is c['external_supervision_qualified'] is c['completed_process_exit0'] is False and c['time_returncode']==c['measured_child_exit']==1 and not (R/c['receipt']).exists() and e['original_charge_execution_sha256'] is e['original_charge_receipt_sha256'] is None and e['original_charge_monotonic_envelope_valid'] is False)
fields=raw(FILES['time'][0]).decode().split();elapsed,user,system=map(Decimal,fields[:3])
wall=float(max(elapsed+Decimal('.01'),Decimal(str(c['fallback_observed_outer_wait_wall_s']))+Decimal('.01')))
cpu=float(max(user+system+Decimal('.02'),Decimal(str(c['fallback_reaped_children_CPU_s']))+Decimal('.02')))
ck('same_independent_finite_two_observation_cost_once_within_original_caps',fields==c['time_fields']==['0.08','0.05','0.01','1'] and wall==e['wall_s']==c['wall_s']==old['upper_wall_s']==0.098610285998584 and cpu==e['cpu_s']==c['cpu_s']==old['upper_cpu_s']==0.092844 and e['charge_basis']=='EXTERNAL_PREFLIGHT_TWO_OBSERVATION_ENVELOPE_ONCE' and wall<e['budget']['wall_s']==30 and cpu<e['budget']['cpu_s']==60)
ck('all_saved_input_bytes_retained_during_review',all(hashlib.sha256((R/n).read_bytes()).hexdigest()==v for n,v in retained.items()))
failed=[z for z in checks if not z['passed']];ok=not failed
post=dict(schema='P4_D080_V_RRT_PCS_BUILD01_RECOVERY_COST_INDEPENDENT_POST_V1',personnel_independent=True,status='PASS_SAVED_ONLY_RECOVERY_COST_INDEX' if ok else 'FAIL_RECOVERY_COST_INDEX',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,reused_original_orphan_checks=9,original_orphan_POST=OLD,original_orphan_POST_sha256=EXPECTED_OLD,external_cost_qualified=ok,orphan_preflight_cost_observation_qualified=ok,external_supervision_qualified=False,engineering_build_qualified=False,independent_path_qualified=False,saved_only_recovery=True,source_execution_created_during_attempt=False,original_runtime_execution_exists=False,original_execution_sha256=None,execution=EP,execution_sha256=sha(EP),internal_receipt_sha256=None,external_time=FILES['time'][0],external_time_sha256=FILES['time'][1],external_charge=FILES['charge'][0],external_charge_sha256=FILES['charge'][1],external_metadata_sha256=FILES['metadata'][1],external_stderr_sha256=FILES['stderr'][1],upper_wall_s=wall,upper_cpu_s=cpu,charge_basis=e['charge_basis'],original_three_observation_completeness=False,new_scientific_calls=0,new_compile_calls=0,new_binary_execution_calls=0,new_review_compile_model_binary_calls=0,retained_sha256=retained,auditor_sha256=sha(str(Path(__file__).relative_to(R))),limits=['Recovery execution_sha256 binds a transparent post-attempt cost index; no original runtime execution or internal receipt is invented.','Original independent orphan9 certificate and four raw files remain unchanged.','Charge this failed engineering preflight once; 54 original runtime records remain 54, independently of the additional cost index.','This is a two-observation cost certificate, never full external supervision, successful build or scientific qualification.'])
with (R/OUT).open('x') as f:f.write(json.dumps(post,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps(dict(output=OUT,checks=len(checks),failures=failed,sha256=sha(OUT))))
