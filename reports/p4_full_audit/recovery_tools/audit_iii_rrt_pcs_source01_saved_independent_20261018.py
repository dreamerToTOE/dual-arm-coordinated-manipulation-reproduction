#!/usr/bin/env python3
"""Saved-only source transport/cost POST; never calls planning or a physical model."""
import base64
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RUN='20261018_R2_D080_III_RRT_PCS_SOURCE01'
EP='results/p4_full/'+RUN+'/execution.json'
PROTOCOL='configs/p4_d080/iii_rrt_pcs_source01_v1.json'
PRE='reports/P4_D080_ENV_III_RRT_PCS_SOURCE01_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
RUNNER='scripts/p4_d080/qualify_iii_rrt_pcs_source01_v1_draft.py'
SUP='scripts/p4_d080/supervise_iii_rrt_pcs_source01_v1_draft.py'
COMMIT='ca984923057864805cf7b44cb1481626492e0140'
checks=[];retained={}
def p(n):
    q=Path(n);return q if q.is_absolute() else ROOT/q
def raw(n):
    data=p(n).read_bytes();retained[str(p(n))]=hashlib.sha256(data).hexdigest();return data
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def js(n):return json.loads(raw(n))
def key(q):return struct.pack('>12d',*q)
def ck(n,v,e=None):checks.append(dict(name=n,passed=bool(v),evidence=e))
def members(g):
    out=[]
    for q in Path('/proc').glob('[0-9]*/stat'):
        try:
            r=q.read_text().rsplit(')',1)[1].split()
            if int(r[2])==g:out.append(int(q.parent.name))
        except (OSError,ValueError,IndexError):pass
    return sorted(out)
e=js(EP);s=js(PROTOCOL);pre=js(PRE);f=p(EP).parent;w=f/'runtime';ext=s['external_supervision'];r=js(ext['charge_path']);i=js(f/'cost_receipt.json');c=js(e['claim']);d=js(w/'result.json')
ck('actual_committed_source_and_frozen_protocol',e['source_commit']==c['source_commit']==COMMIT and sha(PROTOCOL)==e['protocol_sha256']=='d8fe8af3ff5ceb328de0eabb7d7fc97d7a59b35f940f922d1be33921aa0dac83')
ck('exact_incremental_PRE15_reused_no_old_qualification_rerun',sha(PRE)=='6ce3ccdf5349cbc5e4557b31c390edbd4ab3167821384362f77dafe5d2ba777a' and pre['personnel_independent'] is True and pre['checks_total']==pre['checks_passed']==15 and pre['checks_failed']==0)
for n in [RUNNER,SUP,PROTOCOL,PRE]:ck('committed_exact_bytes '+n,subprocess.check_output(['git','show',COMMIT+':'+n],cwd=ROOT)==raw(n))
for n in [RUNNER,SUP]:ck('same_reviewed_runtime_seam '+n,sha(n)==pre['inputs_sha256'][n])
ck('one_source_exact_candidate_not_physical_path',e['status']==i['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT' and e['source_exact'] is d['exact'] is d['has_solution'] is True and e['source_approximate'] is d['approximate'] is False and e['diagnostics']==[] and e['independent_path_qualified'] is e['continuous_collision_certificate'] is False)
ck('frozen_one_original10s_call_caps_and_flags',s['frozen'] is s['scientific_execution_authorized'] is s['independent_review_passed'] is True and s['formal_execution_authorized'] is False and all(s['reviews'].values()) and s['source_process_limit']==s['source_solve_limit']==1 and s['budget']==e['budget']=={'wall_s':30,'cpu_s':60} and s['working_budget']==e['working_budget']=={'wall_s':25,'cpu_s':50} and s['request']['environment']=='III' and s['request']['seed']==7 and s['request']['range_rad']==.8 and s['request']['goal_bias']==.05 and s['request']['solve_seconds']==10.)
ck('immutable_exclusive_claim_and_runtime_frozen_map916_beforeafter',sha(e['claim'])==e['claim_sha256'] and c['run_id']==RUN and c['protocol_sha256']==sha(PROTOCOL) and c['no_retry_reset_resume'] is True and e['bound_files_sha256']==e['bound_files_after_sha256']==s['bound_files_sha256'] and len(s['bound_files_sha256'])==916)
ck('all33_new_saved_run_files_current_original_hashes',len(e['retained_run_files_sha256'])==33 and all(sha(n)==v for n,v in e['retained_run_files_sha256'].items()))
ck('twenty_original_mesh_copies_match_frozen_identity',len(e['copied_runtime_after_sha256'])==20 and {str(w/'simulator'/Path(n).name):v for n,v in s['runtime_meshes_sha256'].items()}==e['copied_runtime_after_sha256'])
request=raw(f/'process0_request.bin');expected=json.dumps(s['request'],allow_nan=False,separators=(',',':')).encode()+b'\n'
ck('single590byte_compact_request_matches_observed_request_and_result',request==expected and len(request)==590 and js(w/'request_observed.json')==d['request']==s['request'] and sha(w/'result.json')==e['source_result_sha256'] and js(f/'parsed_source_result.json')==d and json.loads(raw(f/'process0_stdout.bin').splitlines()[-1])==d)
reg,=e['source_process_registry'];counts=e['counts']
ck('one_actual_worker_dispatched_reaped_exit0_empty_group_bothEOF',e['binary_execution_calls']==e['source_reported_solve_calls']==e['solve_calls_from_result']==d['solve_calls']==1 and all(counts[k]==1 for k in ['source_process_start_attempted','source_process_started','source_request_dispatch_attempted','source_request_dispatched']) and reg['returncode']==0 and reg['actual_group_after_cleanup']==[] and not members(reg['pid']) and reg['start_ticks']>0 and reg['pipe_EOF_observed']=={'stdout':True,'stderr':True} and reg['request_bytes']==reg['request_sent']==len(request) and reg['stdin_closed_after_request'] is True)
journal=[json.loads(z) for z in raw(f/'evidence.jsonl').splitlines()];stdout=b''.join(base64.b64decode(z['base64']) for z in journal if z['event']=='raw_pipe_chunk' and z['channel']=='stdout');stderr=b''.join(base64.b64decode(z['base64']) for z in journal if z['event']=='raw_pipe_chunk' and z['channel']=='stderr')
ck('whole_raw_pipe_chunks_reconstruct_stdout_stderr_without_line_skipping',stdout==raw(f/'process0_stdout.bin') and stderr==raw(f/'process0_stderr.bin') and sum(z['event']=='single_request_exact_bytes' for z in journal)==1 and all(z['exact_raw_stdout_equal'] is True and z['bytes']==len(stdout) and z['sha256']==hashlib.sha256(stdout).hexdigest() for z in journal if z['event']=='entire_mixed_stdout_observed'))
rec=[json.loads(z) for z in raw(w/'reconstruction_attempts.jsonl').splitlines()];ids=[json.loads(z) for z in raw(w/'identify_observations.jsonl').splitlines()]
ck('all16_reconstructions14true2false_and615identify_original_records',rec==d['reconstruction_attempts'] and len(rec)==e['source_reconstruction_calls_completed_observed']==d['reconstruction_calls_completed_observed']==16 and sum(z['returned'] is True for z in rec)==14 and sum(z['returned'] is False for z in rec)==2 and [z['attempt_index'] for z in rec]==list(range(16)) and len(ids)==e['source_identify_calls_completed_observed']==d['identify_calls_completed_observed']==d['identify_observation_count']==615 and [z['call_index'] for z in ids]==list(range(615)))
ck('true_false_full_partial_M_and_postreturn_provenance_retained',all(z['schema']=='P4_ABB_RRT_PCS_RECONSTRUCTION_V1' and z['observation']=='ORIGINAL_STATE_LEVEL_CALL_COMPLETED_POST_RETURN' and type(z['returned']) is bool and all(len(q)==12 and all(math.isfinite(v) for v in q) for q in z['path_q12']) for z in rec) and all(z['schema']=='P4_ABB_RRT_PCS_IDENTIFY_V1' and z['observation']=='ORIGINAL_VECTOR_IDENTIFY_CALL_COMPLETED_POST_RETURN' for z in ids),{'false_attempts':[{'index':z['attempt_index'],'partial_nodes':len(z['path_q12'])} for z in rec if not z['returned']]})
ms=d['milestones_q12'];tree=d['planner_data']
ck('fifteen_original_milestones_exact_A01_binary64_and_complete_tree_counts',len(ms)==15 and key(ms[0])==key(s['request']['start_q12']) and key(ms[-1])==key(s['request']['goal_q12']) and tree['num_vertices']==len(tree['vertices']) and tree['num_edges']==len(tree['edges']) and all(len(q)==12 and all(math.isfinite(v) for v in q) for q in ms) and d['solution_path_simplification'] is False)
ck('internal_starts_unobserved_no_fabricated_source_FK_or_PQP_counts',e['source_actual_internal_call_starts']=='UNOBSERVED' and e['source_FK_IK_PQP_started']=='UNOBSERVED_NO_START_HOOK' and e['source_reconstruction_true_started']==e['source_identify_true_started']=='UNOBSERVED_NO_START_HOOK')
ck('exact_latest_V35_actual_prior_beforeafter_runtime_reused_without_historical_rehash',e['actual_charge_prior']==e['prior_after']==s['actual_charge_prior'] and e['actual_charge_prior']['path']==s['prior']['ledger'] and e['actual_charge_prior']['sha256']==s['prior']['ledger_sha256']==sha(s['prior']['ledger']) and all(s['bound_files_sha256'].get(n)==v for n,v in e['actual_charge_prior']['evidence_sha256'].items()))
fields=raw(ext['sibling_path']).decode().split();elapsed,user,system=map(Decimal,fields[:3]);exitcode=int(fields[3]);rw=elapsed+Decimal('.01');rc=user+system+Decimal('.02')
walls=[rw,Decimal(str(r['fallback_observed_outer_wait_wall_s']))+Decimal('.01'),Decimal(str(i['wall_s_through_execution_persistence']))+Decimal('.01')];cpus=[rc,Decimal(str(r['fallback_reaped_children_CPU_s']))+Decimal('.02'),Decimal(str(i['cpu_s_through_execution_persistence']))+Decimal('.02')];uw=float(max(walls));uc=float(max(cpus));components={'wall_decimal_s':[str(v) for v in walls],'cpu_decimal_s':[str(v) for v in cpus],'order':['raw_GNUtime_plus_padding','outer_monotonic_or_reaped_plus_padding','internal_receipt_plus_padding']}
ck('exact_Decimal_three_observation_envelope_within30_60_and_total',all(v.is_finite() and v>=0 for v in walls+cpus) and r['wall_s']==uw and r['cpu_s']==uc and r['monotonic_envelope_components']==components and r['raw_GNUtime_upper_wall_s']==float(rw) and r['raw_GNUtime_upper_cpu_s']==float(rc) and uw<30 and uc<60 and uw+s['prior']['wall_s']<3600 and uc+s['prior']['cpu_s']<7200)
ck('cost_execution_receipt_time_links_and_exit0_supervision',r['source_execution']==EP and r['execution_sha256']==i['execution_sha256']==sha(EP) and r['receipt_sha256']==sha(r['receipt']) and r['time_sha256']==sha(ext['sibling_path']) and r['time_fields']==fields and r['charge_basis']=='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE' and r['timing_valid'] is r['monotonic_envelope_valid'] is r['time_inode_unchanged'] is r['wall_CPU_caps_pass'] is r['completed_process_exit0'] is True and r['failure'] is r['monotonic_envelope_error'] is None and r['time_returncode']==r['measured_child_exit']==exitcode==0 and r['external_supervision_qualified'] is i['external_supervision_qualified'] is False)
lines=raw(ext['metadata_path']).splitlines(keepends=True);events=[json.loads(z) for z in lines];launch,start,reap=events;proof=e['supervisor_launch_proof'];inode=p(ext['sibling_path']).stat()
ck('real_GNUtime_argv_source_protocol_parent_held_inode_and_reap',len(events)==3 and [z['event'] for z in events]==['planned_launch','time_process_started','time_process_reaped'] and launch['argv']==start['argv']==proof['actual_argv'] and launch['protocol_sha256']==sha(PROTOCOL) and launch['supervisor_source_sha256']==sha(SUP) and launch['runner_sha256']==sha(RUNNER) and start['pid']==reap['pid']==r['time_process_pid']==proof['time_pid'] and reap['returncode']==0 and reap['failure'] is None and launch['supervisor_pid']==proof['supervisor_pid'] and launch['time_inode']==inode.st_ino and launch['time_device']==inode.st_dev and launch['time_fd'] in proof['held_time_fds'] and proof['time_start_ticks']>0 and proof['launch_line_sha256']==hashlib.sha256(lines[0]).hexdigest() and r['metadata_sha256']==sha(ext['metadata_path']) and r['stderr_sha256']==sha(ext['stderr_path']))
ck('no_independent_model_VI_or_formal_science_misclaim',e['formal_table_I_calls']==e['new_VI_candidate_constructions']==e['new_independent_model_calls']==0 and e['independent_path_qualified'] is False and s['formal_table_I_D080_required']==18000)
for n,v in list(retained.items()):
    if hashlib.sha256(Path(n).read_bytes()).hexdigest()!=v:ck('saved_bytes_changed_during_review '+n,False)
failed=[z for z in checks if not z['passed']];ok=not failed
report={'schema':'P4_D080_III_RRT_PCS_SOURCE01_SAVED_INDEPENDENT_POST_V1','personnel_independent':True,'status':'PASS_SOURCE_EXACT_CANDIDATE_TRANSPORT_COST_ONLY' if ok else 'FAIL_SOURCE_SAVED_POST','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'failures':failed,'external_supervision_qualified':ok,'external_timing_qualified':ok,'external_cost_qualified':ok,'source_transport_qualified':ok,'source_exact_candidate':ok and d['exact'],'independent_path_qualified':False,'continuous_collision_certificate':False,'source_commit':COMMIT,'execution':EP,'execution_sha256':sha(EP),'protocol':PROTOCOL,'protocol_sha256':sha(PROTOCOL),'external_charge_sha256':sha(ext['charge_path']),'receipt':ext['charge_path'],'receipt_sha256':sha(ext['charge_path']),'internal_receipt_sha256':sha(r['receipt']),'external_time_sha256':sha(ext['sibling_path']),'upper_wall_s':uw,'upper_cpu_s':uc,'charge_basis':r['charge_basis'],'solve_calls_from_result':e['solve_calls_from_result'],'source_solve_wall_s':d['solve_wall_s'],'source_milestones':len(ms),'source_reconstruction_calls':len(rec),'source_reconstruction_true':sum(z['returned'] is True for z in rec),'source_reconstruction_false':sum(z['returned'] is False for z in rec),'source_identify_completed':len(ids),'retained_sha256':retained,'auditor_sha256':sha(__file__),'new_review_compile_binary_model_scientific_calls':0,'reused_incremental_PRE_checks':15,'historical_full_bound_rehash_repeated':False,'limits':['Source exact candidate only; complete original M queue and independent physical/branch/limit/collision/leaf gates still required.','Both false fallback attempts and all partial original arrays remain saved; no changed seed or repeated solve.','Actual one10s source call returned in observed time; FK/IK/PQP internal starts remain UNOBSERVED.','Original II paths and all historical UNKNOWN/VI974 remain; formal0/18000.']}
out=ROOT/'reports/P4_D080_ENV_III_RRT_PCS_SOURCE01_SAVED_INDEPENDENT_POST_20261018.json'
with out.open('x') as stream:stream.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks_total':len(checks),'failed':failed,'upper_wall_s':uw,'upper_cpu_s':uc,'sha256':sha(out)},ensure_ascii=False,indent=2))
