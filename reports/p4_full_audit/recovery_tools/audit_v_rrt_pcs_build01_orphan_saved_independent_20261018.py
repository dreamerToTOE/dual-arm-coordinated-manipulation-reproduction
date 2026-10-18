#!/usr/bin/env python3
"""Saved-only failed preflight cost audit. Never manufactures execution or receipt."""
import ast
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RUN='20261018_R2_D080_V_RRT_PCS_BUILD01';PREFIX='results/p4_full/'+RUN
R='scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py';S='scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v1_draft.py';P='configs/p4_d080/v_rrt_pcs_e2e_build_v1.json'
checks=[]
def p(n):
    q=Path(n);return q if q.is_absolute() else ROOT/q
def raw(n):return p(n).read_bytes()
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def js(n):return json.loads(raw(n))
def ck(n,v,e=None):checks.append(dict(name=n,passed=bool(v),evidence=e))
r=js(PREFIX+'.supervision.charge.json');spec=js(P);lines=raw(PREFIX+'.supervision.jsonl').splitlines(keepends=True);events=[json.loads(z) for z in lines];launch,start,reap=events;err=raw(PREFIX+'.supervision.stderr.log').decode();fields=raw(PREFIX+'.supervision.time.txt').decode().split()
ck('exact_failed_preflight_sources_match_independent15_PRE',sha(R)=='9dbca564ff6d8975ffbca71b3d1e163b9d7a488f1f7f907888075fd05e566958' and sha(S)=='c2ff4dc64b983524c09781d75bad99e99200c4cbd9c9ddb0ca8923a7d21063ae' and sha(P)=='6767581f00a9f5697125baee76618e1bd1b70e05af813f6ed8244c4ada9af84e')
ck('raw_stderr_identifies_commit_gate_before_mkdir_and_any_invoke',"main\n    require(subprocess.check_output(['git','show',commit+':'+relative]" in err and 'c6a6a4b17752dc349af54128210661c649589d99:scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py' in err and 'CalledProcessError' in err and 'exit status 128' in err)
txt=raw(R).decode();ck('source_control_order_proves_admission_precedes_run_claim_transform_compile',txt.index("subprocess.check_output(['git','show',commit+':'+relative]")<txt.index('RUN.mkdir(parents=True,exist_ok=False)')<txt.index("write_once(RUN/'claim.json'")<txt.index('transform.instrument_svc(')<txt.index('invoke(command,DEST'))
missing=subprocess.run(['git','cat-file','-e','c6a6a4b17752dc349af54128210661c649589d99:'+R],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
ck('actual_failed_commit_lacks_runner_object',missing.returncode!=0)
ck('no_original_execution_receipt_claim_stage_or_compiler_artifacts',not p(PREFIX).exists() and not p(spec['stage_root']).exists() and r['execution_sha256'] is r['receipt_sha256'] is None and not p(r['source_execution']).exists() and not p(r['receipt']).exists())
ck('three_actual_outer_launch_started_reaped_exit1_records',len(events)==3 and [z['event'] for z in events]==['planned_launch','time_process_started','time_process_reaped'] and launch['argv']==start['argv'] and launch['protocol_sha256']==sha(P) and launch['runner_sha256']==sha(R) and launch['supervisor_source_sha256']==sha(S) and launch['run_id']==RUN and start['pid']==reap['pid']==r['time_process_pid'] and reap['returncode']==r['time_returncode']==r['measured_child_exit']==1 and reap['failure'] is r['failure'] is None)
inode=p(PREFIX+'.supervision.time.txt').stat();ck('exclusive_original_inode_and_all_four_raw_log_hashes',launch['time_inode']==inode.st_ino and launch['time_device']==inode.st_dev and r['time_inode_unchanged'] is True and r['time_sha256']==sha(PREFIX+'.supervision.time.txt') and r['metadata_sha256']==sha(PREFIX+'.supervision.jsonl') and r['stderr_sha256']==sha(PREFIX+'.supervision.stderr.log') and r['time_fields']==fields)
elapsed,user,system=map(Decimal,fields[:3]);rw=elapsed+Decimal('.01');rc=user+system+Decimal('.02');ow=Decimal(str(r['fallback_observed_outer_wait_wall_s']))+Decimal('.01');oc=Decimal(str(r['fallback_reaped_children_CPU_s']))+Decimal('.02');uw=float(max(rw,ow));uc=float(max(rc,oc))
ck('independent_two_observation_conservative_max_exact_finite_within_caps',len(fields)==4 and int(fields[3])==1 and all(v.is_finite() and v>=0 for v in [rw,rc,ow,oc]) and r['raw_GNUtime_upper_wall_s']==float(rw) and r['raw_GNUtime_upper_cpu_s']==float(rc) and r['wall_s']==uw==0.098610285998584 and r['cpu_s']==uc==0.092844 and uw<30 and uc<60)
ck('original_incomplete_three_observation_and_failure_flags_permanently_retained',r['timing_valid'] is True and r['monotonic_envelope_valid'] is r['external_supervision_qualified'] is r['wall_CPU_caps_pass'] is r['completed_process_exit0'] is False and r['monotonic_envelope_components'] is None and 'FileNotFoundError' in r['monotonic_envelope_error'] and r['execution_cap_breach']=={'wall':False,'cpu':False})
failed=[z for z in checks if not z['passed']];ok=not failed
report={'schema':'P4_D080_V_RRT_PCS_BUILD01_ORPHAN_SAVED_INDEPENDENT_POST_V1','personnel_independent':True,'status':'PASS_FAILED_PREFLIGHT_ORPHAN_COST_OBSERVATION_ONLY' if ok else 'FAIL_ORPHAN_COST_AUDIT','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'external_cost_qualified':ok,'orphan_preflight_cost_observation_qualified':ok,'external_supervision_qualified':False,'engineering_build_qualified':False,'independent_path_qualified':False,'run_id':RUN,'source_protocol':P,'protocol_sha256':sha(P),'failed_source_commit':'c6a6a4b17752dc349af54128210661c649589d99','failure_reason':'Uncommitted runner missing from actual Git HEAD; preflight commit gate rejected before claim/run/stage/transform/compiler.','original_execution_exists':False,'execution_sha256':None,'internal_receipt_sha256':None,'external_time':PREFIX+'.supervision.time.txt','external_time_sha256':sha(PREFIX+'.supervision.time.txt'),'external_charge':PREFIX+'.supervision.charge.json','external_charge_sha256':sha(PREFIX+'.supervision.charge.json'),'external_metadata_sha256':sha(PREFIX+'.supervision.jsonl'),'external_stderr_sha256':sha(PREFIX+'.supervision.stderr.log'),'upper_wall_s':uw,'upper_cpu_s':uc,'charge_basis':'INDEPENDENT_TWO_OBSERVATION_PREFLIGHT_ORPHAN_ONCE','original_charge_basis_retained':r['charge_basis'],'two_observation_components':{'wall_decimal_s':[str(rw),str(ow)],'cpu_decimal_s':[str(rc),str(oc)],'order':['raw_GNUtime_plus_padding','actual_outer_monotonic_or_reaped_plus_padding']},'original_three_observation_completeness':False,'new_compile_calls':0,'new_model_calls':0,'new_binary_execution_calls':0,'new_scientific_calls':0,'new_review_compile_model_binary_calls':0,'auditor_sha256':sha(__file__),'limits':['Independent conservative cost for one actually reaped failed preflight only; not complete successful three-observation execution.','No original execution or internal receipt exists; none is fabricated or backfilled.','Original four supervision files and error flags remain immutable.','This cost must be charged exactly once as a separately labelled orphan attempt before later execution; old prior validator needs an explicit versioned orphan-aware route.','No scientific algorithm, geometry, collision threshold, seed, node or budget changed.']}
out=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_BUILD01_ORPHAN_SAVED_INDEPENDENT_POST_20261018.json'
with out.open('x') as f:f.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'failed':failed,'upper_wall_s':uw,'upper_cpu_s':uc,'sha256':sha(out)},ensure_ascii=False,indent=2))
