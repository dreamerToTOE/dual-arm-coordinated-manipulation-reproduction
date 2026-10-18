#!/usr/bin/env python3
"""V fixed24 saved-only diagnostic POST. No project/model imports or execution."""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
import argparse
import hashlib
import json
import math
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RUN_ID='20261018_R2_D080_V_PCS_PHYSICAL01';RUN=Path('results/p4_full')/RUN_ID
STATIC='reports/P4_D080_ENV_V_PCS_PHYSICAL01_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
STATIC_SHA='00a2ccd54bfe2ea8d5f9be63f56ddc743ed2ae41cc545bad89bc9d7d63463f21'
RUNNER='scripts/p4_d080/qualify_v_pcs_physical01_v1_draft.py';SUP='scripts/p4_d080/supervise_v_pcs_physical01_v1_draft.py'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json'
BASIS='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
ELBOW=[1,-1,1,-1,1,-1,1,-1];WRIST=[1,-1,-1,1,-1,1,1,-1]
checks=[];retained={}
def path(n):
 p=Path(n);return p if p.is_absolute()else ROOT/p
def raw(n):
 p=path(n);b=p.read_bytes();h=hashlib.sha256(b).hexdigest();assert retained.setdefault(str(p),h)==h;return b
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def load(n):return json.loads(raw(n))
def ck(g,n,v):checks.append(dict(group=g,check=n,passed=bool(v)))
def exact(a,b):
 if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
 if type(a)in(int,float)and type(b)in(int,float):return struct.pack('>d',a)==struct.pack('>d',b)
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
 if isinstance(a,(list,tuple)):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 return a==b
def key(q):return struct.pack('>12d',*q).hex()
def near(a,b,eps=1e-12):return math.isfinite(a)and math.isfinite(b)and abs(a-b)<=eps
def matrix(p,n=4):return isinstance(p,list)and len(p)==n and all(len(r)==4 and all(type(v)in(int,float)and math.isfinite(v)for v in r)for r in p)
def lines(n):
 b=raw(n);assert b.endswith(b'\n');return[json.loads(x)for x in b.splitlines()]

def audit(args):
 e=load(RUN/'execution.json');p=load(e['protocol']);claim=load(e['claim']);static=load(STATIC)
 ck('reuse','exact21 independent V adapter static without oldpath or fullunionreview',sha(STATIC)==STATIC_SHA and static['personnel_independent']is True and static['checks_total']==static['checks_passed']==21 and static['checks_failed']==0)
 ck('identity','unique actual committed run protocol and claim no retry',e['schema']=='P4_D080_V_PCS_PHYSICAL01_EXECUTION_V1'and e['run_id']==p['run_id']==claim['run_id']==RUN_ID and e['source_commit']==claim['source_commit']==args.expected_source_commit and sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']==claim['protocol_sha256']==args.protocol_sha256 and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256']and claim['no_retry_reset_resume']is True and p['frozen']is p['scientific_execution_authorized']is True and all(p['reviews'].values())and p['formal_execution_authorized']is False)
 for n,h in p['own_source_sha256'].items():ck('commit','current reviewed committed OWN '+n,sha(n)==h and hashlib.sha256(subprocess.check_output(['git','show',args.expected_source_commit+':'+n],cwd=ROOT)).hexdigest()==h)
 ck('commit','actual committed protocol bytes',subprocess.check_output(['git','show',args.expected_source_commit+':'+e['protocol']],cwd=ROOT)==raw(e['protocol']))
 ck('assets','exact frozen before after complete maps no5052unionrehash',e['bound_files_sha256']==e['bound_files_after_sha256']==p['bound_files_sha256']and all(sha(n)==h for n,h in e['retained_run_files_sha256'].items()))
 q=p['fixed_queue'];nodes=q['nodes'];n=len(nodes)
 ck('queue','full exact24 originally saved data and no truncation complete',n==24 and q==load(p['queue'])==load(RUN/'complete_original_saved_queue.json')and sha(p['queue'])==p['queue_sha256']and p['execution_node_ids']==e['execution_node_ids']==e['completed_original_node_ids']==list(range(24))and e['node_count']==e['original_full_queue_node_count']==e['completed_nodes']==24 and e['uncompleted_node_ids']==[]and e['full_queue_checked']is True)
 ck('diagnostic','complete success means diagnosis only independentlocal/pathfalse',e['status']=='COMPLETED_FIXED24_DIAGNOSTIC_PENDING_INDEPENDENT_POST'and e['diagnostics']==[]and e['diagnosis_complete_does_not_imply_local_or_path_success']is True and e['independent_local_qualified']is e['independent_path_qualified']is e['continuous_collision_certificate']is False)
 ev=lines(RUN/'events.jsonl');by=defaultdict(list)
 for r in ev:by[r['event']].append(r)
 ck('events','one setup final counts no stopped exactjournalhash',sha(RUN/'events.jsonl')==e['events_sha256']and len(by['setup'])==len(by['final_counts'])==1 and not by['stopped']and by['final_counts'][0]['counts']==e['counts']and by['final_counts'][0]['diagnostics']==[])
 manifest=load(COLLISION);entries={r['variant']:r for r in manifest['entries']if r['model']=='V'}
 ck('collision','same v3 twoV frozen successful builds',set(entries)=={'native','aligned'}and sha(COLLISION)==p['bound_files_sha256'][COLLISION]and all(r['exit_code']==0 for r in entries.values()))
 bounds=[(a*3.1416/180,b*3.1416/180)for a,b in[(-180,180),(-60,125),(-90,75),(-2700,2700),(-120,120),(-400,400)]]*2
 results=[];rejected=[];maxpos=maxrot=0.;native_reject=0;native_tcp_fail=[];branches=set();pqp=0
 for i,node in enumerate(nodes):
  r=load(RUN/f'node_{i:05d}.json');a1=load(RUN/f'node_{i:05d}_arm1.json');a2=load(RUN/f'node_{i:05d}_arm2.json');mr=load(RUN/f'node_{i:05d}_math.json');cr=load(RUN/f'node_{i:05d}_collision_response.json');v=node['q12'];poses=r['poses']
  ck('node',str(i)+' exact original input two savedFK snapshots rawmath andcollision',r['node_id']==i and key(r['q12'])==key(v)and r['stage']=='COMPLETED'and len(poses)==2 and all(matrix(t)and t[3]==[0.,0.,0.,1.]for t in poses)and exact(a1['poses'],poses[:1])and exact(a2['poses'],poses)and all(exact(mr[k],r[k])for k in('q12','poses','branches','closure','limits','role_branch_assignments','math_qualified'))and exact(cr,r['collision']))
  x,y=poses;targetp=[x[j][3]+250*x[j][0]+750*x[j][2]for j in range(3)];targetr=[[-x[j][2],-x[j][1],-x[j][0]]for j in range(3)]
  dp=max(abs(y[j][3]-targetp[j])for j in range(3));dr=max(abs(y[j][k]-targetr[j][k])for j in range(3)for k in range(3));maxpos=max(maxpos,dp);maxrot=max(maxrot,dr)
  closureok=dp<=1e-5 and dr<=1e-5
  ck('math',str(i)+' saved matrix original exactQ FLIP closure',near(dp,r['closure']['position_max_abs'],1e-10)and near(dr,r['closure']['rotation_matrix_max_abs'])and closureok)
  violations=[dict(index=j,q_rad=z,lower_rad=lo,upper_rad=hi)for j,(z,(lo,hi))in enumerate(zip(v,bounds))if not lo<=z<=hi];legal=not violations
  ck('math',str(i)+' original unwrapped limits literal3.1416 exact',r['limits']==dict(legal=legal,violations=violations,source_literal_pi_preserved=3.1416,planar_q19_policy=None))
  for arm,b in enumerate(r['branches']):
   a=v[arm*6:arm*6+6];radius=524.5+1250*math.sin(a[1])+210*math.sin(a[1]+a[2])+1436.5*math.cos(a[1]+a[2]);elbow=-math.sin(a[2]+math.atan2(1436.5,210));wrist=math.sin(a[4]);epsilon=p['gates']['branch_zero_relative_epsilon'];sign=lambda z,scale:None if abs(z)<=epsilon*scale else 1 if z>0 else-1
   rs,es,ws=sign(radius,524.5+1250+math.hypot(210,1436.5)),sign(elbow,1),sign(wrist,1);expected=[z for z in range(8)if(rs is None or(1 if z<4 else-1)==rs)and(es is None or ELBOW[z]==es)and(ws is None or WRIST[z]==ws)];branches.add(tuple(expected))
   ck('branch',str(i)+' arm'+str(arm+1)+' independent joint invariants and coalesced branchset',near(radius,b['signed_shoulder_radius_mm'],1e-10)and near(elbow,b['elbow_factor'])and near(wrist,b['wrist_factor'])and b['shoulder_sign']==rs and b['elbow_sign']==es and b['wrist_sign']==ws and b['branch_set']==expected and b['unique']is all(z is not None for z in(rs,es,ws)))
  assign=[dict(a,branch_pass=a['requested_branch']in r['branches'][1-a['active_chain']]['branch_set'])for a in node['role_branch_assignments']];branchok=bool(assign)and all(a['branch_pass']for a in assign);mathok=closureok and legal and branchok
  ck('branch',str(i)+' all source role/passive/branch assignments math flag exact',exact(assign,r['role_branch_assignments'])and r['math_qualified']is mathok)
  col=r['collision'];colok=col['status']=='CHECKED'and col['environment']=='V'and col['scope']=='AUTHOR_DISCRETE_COLLISION_POLICY'and col['selected_variant']=='aligned'and type(col['collision'])is bool and col['continuous_collision_certificate']is False and set(col['variants'])=={'native','aligned'}and col['manifest_sha256']==p['bound_files_sha256'][COLLISION]
  for variant,z in col['variants'].items():
   entry=entries[variant];ll=z['source_stdout'].splitlines(keepends=True);terminal=[line for line in ll if line.startswith('P4_COLLISION_RESULT ')];parsed=json.loads(terminal[0].split(' ',1)[1])if len(terminal)==1 else{}
   ck('collision_raw',str(i)+' '+variant+' original unique final JSON provenance87API0 and collisionpredicate',len(terminal)==1 and ll[-1]==terminal[0]and terminal[0].endswith('\n')and all(exact(z[k],a)for k,a in parsed.items())and {'native_result','poses','query_codes','cpu_s'}<=set(parsed)and z['source_command']==[entry['binary'],'V']and z['provenance']=={k:entry[k]for k in('source_root','source_commit','source_files_sha256','mesh_sha256','binary_sha256','physical_alignment_changes')}and len(z['query_codes'])==87 and all(type(a)is int and a==0 for a in z['query_codes'])and z['query_error_codes']==[]and type(z['native_result'])is int and z['native_result']in(0,1)and z['native_collision']is bool(z['native_result']))
   pqp+=len(z['query_codes']);pc=z['pose_consistency'];errors=pc['errors']
   for arm,er in enumerate(errors):
    tcp=[z['poses'][arm][j:j+4]for j in(0,4,8)];ind=er['independent_TCP'];dpt=max(abs(tcp[j][3]-ind[j][3])for j in range(3));drt=max(abs(tcp[j][k]-ind[j][k])for j in range(3)for k in range(3))
    ck('TCP',str(i)+' '+variant+' arm'+str(arm+1)+' saved workerTCP independentFK/J andmathFK same physical transform',er['arm']==arm+1 and exact(er['collision_TCP'],tcp)and matrix(ind,3)and near(dpt,er['translation_maxabs_mm'])and near(drt,er['rotation_maxabs'])and max(abs(ind[j][k]-poses[arm][j][k])for j in range(3)for k in range(4))<=1e-5)
   passed=all(er['translation_maxabs_mm']<=1e-5 and er['rotation_maxabs']<=1e-5 for er in errors)
   ck('TCP',str(i)+' '+variant+' original1e-5 TCP pass flag exact',len(errors)==2 and pc['position_gate_mm']==pc['rotation_matrix_gate']==1e-5 and pc['passed']is passed)
   if variant=='aligned':colok=colok and passed and col['collision']is z['native_collision']
   else:
    native_reject+=z['native_collision']
    if not passed:native_tcp_fail.append(i)
  qualified=mathok and colok and not col['collision'];ck('node',str(i)+' reject retained as normal completed diagnostic qualifiedflag exact',r['collision_response_qualified']is colok and r['qualified']is qualified)
  if not qualified:rejected.append(dict(node_id=i,math_reject=not mathok,closure_reject=not closureok,limits_reject=not legal,branch_reject=not branchok,collision_reject=col['collision']))
  results.append(r)
  starts=[z for z in by['math_node_started']if z['node_id']==i];fk=[z for z in by['math_arm_FK_completed']if z['node_id']==i];co=[z for z in by['collision_response_retained']if z['node_id']==i]
  ck('events',str(i)+' saved q FK rawcollision and completion realjournal',len(starts)==len(co)==1 and exact(starts[0]['q12'],v)and[z['arm']for z in fk]==[1,2]and exact([z['pose']for z in fk],poses)and exact(co[0]['response'],col)and len([z for z in by['node_completed']if z['node_id']==i])==1)
 expectedcounts=dict(collision_worker_start_attempted=2,collision_worker_started=2,math_arm_FK_started=48,math_arm_FK_completed=48,branch_identity_started=48,branch_identity_completed=48,collision_calls_started=24,collision_calls_completed=24,adapter_internal_arm_FK_J_started=96,adapter_internal_arm_FK_J_completed=96,PQP_queries=4176)
 ck('complete','all24 mathtrue fifteenqualified ninecollisions preserved exactcounts',e['counts']==expectedcounts and pqp==4176 and sum(r['qualified']for r in results)==e['qualified_nodes']==15 and e['rejected_node_ids']==[r['node_id']for r in rejected]and all(r['math_qualified']for r in results)and e['all_saved_nodes_qualified']is False and not list(path(RUN).glob('node_*_stopped_partial.json'))and len(list(path(RUN).glob('node_*.json')))==120)
 wanted=[(arm+1,v['q12'][arm*6:arm*6+6])for v in nodes for _ in('native','aligned')for arm in range(2)];actual=[(v['arm'],v['q6'])for v in by['adapter_internal_FK_J_started']]
 ck('events','all96 counted adapter FK/J order original q6 bits',exact(actual,wanted)and len(by['adapter_internal_FK_J_completed'])==96)
 registry=e['collision_worker_registry'];workers=e['collision_worker_evidence'];ck('worker','two real registered reaped exit0 same PID cleanup',len(registry)==len(workers)==2 and len({r['pid']for r in registry})==2 and {r['pid']for r in registry}=={r['pid']for r in workers}and all(r['reaped']is True and r['returncode']==0 for r in registry)and e['complete_collision_worker_cleanup_gate']is True)
 for w in workers:
  pid=w['pid'];variant=next(k for k,v in entries.items()if w['command']==[v['binary'],'V']);a,b=w['start_process_group'],w['close_process_group']
  ck('worker',variant+' directsingleton bothgroups exactEOF empty pendingtail',len(a)==len(b)==1 and a[0]['pid']==a[0]['pgrp']==b[0]['pid']==b[0]['pgrp']==pid and a[0]['ppid']==b[0]['ppid']>0 and w['original_selector_closed']is w['pipe_EOF_drained']is True and w['stdout_pending_base64']==w['stdout_EOF_tail_base64']=='')
  for event,field,value in[('collision_worker_started','pid',pid),('collision_worker_start_group','members',a),('collision_worker_close_group','members',b),('collision_worker_after_original_close_group','members',[]),('collision_worker_final_raw_tail','pending_base64','')]:
   rr=[r for r in by[event]if r['pid']==pid];ck('worker',variant+' '+event+' originaljournal',len(rr)==1 and exact(rr[0][field],value))
 prior=p['actual_charge_prior'];ledger=load(p['prior']['ledger']);pm={r['execution']:r['execution_sha256']for r in ledger['executions']};pw,pc=p['previous_r2_wall_s'],p['previous_r2_cpu_s']
 ck('prior','unchanged exactV33 certificate51savedidentities no oldscience reaudit',sha(p['prior']['ledger'])==p['prior']['ledger_sha256']==prior['sha256']and pm==p['prior_execution_sha256']==e['prior_execution_sha256']==e['prior_execution_after_sha256']and e['actual_charge_prior']==prior and pw==p['prior']['wall_s']==prior['wall_s']and pc==p['prior']['cpu_s']==prior['cpu_s']and str(RUN/'execution.json')not in pm)
 # Reuse exact current tail02 whole-child Decimal envelope check with V caps;
 # raw GNUtime, outer monotonic/reaped and receipt remain distinct observations.
 ext=p['external_supervision'];tb=raw(ext['sibling_path']);fields=tb.decode().split();elapsed,user,system=(Decimal(x)for x in fields[:3]);meta=raw(ext['metadata_path']);planned,started,reaped=[json.loads(x)for x in meta.splitlines()];proof=e['supervisor_launch_proof'];charge=load(ext['charge_path']);rr=lines(RUN/'cost_receipt.jsonl');receipt=rr[0]
 walls=[elapsed+Decimal('.01'),Decimal(str(charge['fallback_observed_outer_wait_wall_s']))+Decimal('.01'),Decimal(str(receipt['wall_s_through_execution_persistence']))+Decimal('.01')];cpus=[user+system+Decimal('.02'),Decimal(str(charge['fallback_reaped_children_CPU_s']))+Decimal('.02'),Decimal(str(receipt['cpu_s_through_execution_persistence']))+Decimal('.02')];uw,uc=float(max(walls)),float(max(cpus));st=path(ext['sibling_path']).stat()
 ck('external','finite complete originalraw one line exit0',len(tb.splitlines())==1 and tb.endswith(b'\n')and len(fields)==4 and fields[3]=='0'and all(x.is_finite()and x>=0 for x in(elapsed,user,system,*walls,*cpus)))
 argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(path(RUNNER)),'--protocol',str(path(e['protocol']))]
 ck('external','actualGNUtime parent argv PID reap heldexclusive inode proof',planned['event']=='planned_launch'and started['event']=='time_process_started'and reaped['event']=='time_process_reaped'and started['pid']==reaped['pid']==proof['actual_time_pid']==charge['time_process_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid']and argv==planned['argv']==started['argv']==proof['actual_argv']and st.st_ino==planned['time_inode']==proof['time_inode']and st.st_dev==planned['time_device']==proof['time_device']and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and hashlib.sha256(meta.splitlines(keepends=True)[0]).hexdigest()==proof['planned_launch_line_sha256'])
 ck('external','frozen source protocol timepython hashes original planned',planned['run_id']==RUN_ID and planned['protocol_sha256']==e['protocol_sha256']and planned['runner_sha256']==p['own_source_sha256'][RUNNER]and planned['supervisor_source_sha256']==p['own_source_sha256'][SUP]and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
 ck('external','exact actualexecution receipt charge metadata stderr timeSHAchain',charge['schema']=='P4_D080_V_PCS_PHYSICAL01_EXTERNAL_COST_CHARGE_V1'and charge['run_id']==RUN_ID and charge['source_execution']==str(RUN/'execution.json')and charge['execution_sha256']==receipt['execution_sha256']==sha(RUN/'execution.json')and charge['receipt']==str(RUN/'cost_receipt.jsonl')and charge['receipt_sha256']==sha(RUN/'cost_receipt.jsonl')and charge['time_file']==ext['sibling_path']and charge['time_sha256']==sha(ext['sibling_path'])and charge['metadata']==ext['metadata_path']and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr']==ext['stderr_path']and charge['stderr_sha256']==sha(ext['stderr_path'])and charge['time_fields']==fields)
 ck('external','exactDecimal conservative three-observation envelope unchanged',charge['charge_basis']==ext['charge_basis']==BASIS and charge['raw_GNUtime_upper_wall_s']==float(walls[0])and charge['raw_GNUtime_upper_cpu_s']==float(cpus[0])and charge['monotonic_envelope_components']==dict(wall_decimal_s=[str(x)for x in walls],cpu_decimal_s=[str(x)for x in cpus],order=['raw_GNUtime_plus_padding','outer_monotonic_or_reaped_plus_padding','internal_receipt_plus_padding'])and charge['monotonic_envelope_valid']is True and charge['monotonic_envelope_error']is None and exact([charge['wall_s'],charge['cpu_s']],[uw,uc]))
 ck('external','actualexit0 complete capped cost not automatic physicalqualification',charge['timing_valid']is charge['time_inode_unchanged']is charge['wall_CPU_caps_pass']is charge['completed_process_exit0']is charge['started_attempt']is True and charge['time_returncode']==charge['measured_child_exit']==0 and charge['failure']is None and charge['execution_cap_breach']==dict(wall=False,cpu=False)and len(rr)==1 and receipt['status']==e['status']and 0<=e['wall_s']<=receipt['wall_s_through_execution_persistence']<=uw<=min(60.,3600.-pw)and 0<=e['cpu_s']<=receipt['cpu_s_through_execution_persistence']<=uc<=min(120.,7200.-pc)and receipt['external_supervision_qualified']is e['external_supervision_qualified']is charge['external_supervision_qualified']is False)
 ck('scope','no new IK projection NR RBS solve RNG VI formal local path orCCDclaim',e['zero_calls']==dict.fromkeys(('IK','NR','projection','RBS','solve','RNG','VI_constructions','formal_table_I'),0)and e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and e['independent_local_qualified']is e['independent_path_qualified']is e['continuous_collision_certificate']is False)
 for name,h in retained.items():assert hashlib.sha256(path(name).read_bytes()).hexdigest()==h
 return dict(execution=str(RUN/'execution.json'),execution_sha256=sha(RUN/'execution.json'),protocol=e['protocol'],protocol_sha256=e['protocol_sha256'],source_commit=e['source_commit'],source_transport_independent_STATIC=STATIC,source_transport_independent_STATIC_sha256=STATIC_SHA,completed_saved_nodes=24,math_qualified_nodes=sum(r['math_qualified']for r in results),discrete_source_policy_qualified_nodes=15,rejected_nodes=rejected,rejected_node_ids=[r['node_id']for r in rejected],native_collision_nodes=native_reject,aligned_collision_nodes=sum(r['collision']['collision']for r in results),native_TCP_mismatch_node_ids=native_tcp_fail,maximum_saved_closure_position_mm=maxpos,maximum_saved_closure_rotation=maxrot,branch_sets_encountered=[list(b)for b in sorted(branches)],actual_counts=e['counts'],external_time=ext['sibling_path'],external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),internal_receipt_sha256=sha(RUN/'cost_receipt.jsonl'),charge_basis=BASIS,upper_wall_s=uw,upper_cpu_s=uc,cumulative_charged_wall_s=math.fsum((pw,uw)),cumulative_charged_cpu_s=math.fsum((pc,uc)),source17_crosscheck_status='PENDING_SAVED_ONLY_SEPARATE_DIAGNOSTIC')

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--expected-source-commit',required=True);ap.add_argument('--protocol-sha256',required=True);args=ap.parse_args()
 if OUT.exists()or OUT.with_suffix('.md').exists():raise FileExistsError('EXCLUSIVE_PHYSICAL_SAVED_POST')
 details={}
 try:details=audit(args)
 except BaseException as exc:ck('completion','saved audit complete withoutstructuralexception '+repr(exc),False)
 failed=[x for x in checks if not x['passed']];external=[x for x in checks if x['group']=='external'];extok=bool(external)and all(x['passed']for x in external)
 report=dict(schema='P4_D080_V_PCS_PHYSICAL01_SAVED_PERSONNEL_INDEPENDENT_POST_V1',status='PASS_COMPLETE24_DISCRETE_DIAGNOSTIC_SOURCE_CONNECTIONS_STILL_FALSE'if not failed else'FAIL_PHYSICAL_SAVED_POST_RETAINED',personnel_independent=True,reviewer='/root/sbl_independent_resume independent of physical adapter implementation',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,external_supervision_qualified=extok,external_timing_qualified=extok,completed_process_exit0=extok,independent_fixed_node_diagnostic_qualified=not failed,independent_local_qualified=False,independent_path_qualified=False,continuous_collision_certificate=False,**details,retained_sha256=retained,new_model_import_compile_binary_FK_J_IK_NR_PQP_RBS_RNG_solve_VI_formal_calls=0,full5052_bound_union_rehash_calls=0,limits=['Whole24 diagnostics only; publicRBS0true/3false/1dependency and reconstruct0true/3false/1dependency retained.','15 discrete aligned nodes qualified;9collisions rejected; successful projection alone never implied collision clearance.','Native TCP mismatch retained; source87pair8mm policy does not establish solid CAD/suctioncontact/omittedpair/continuouscollision or complete planner path.','Scientific source17 TCP/box/pair saved-only crosscheck is reported separately and cannot alter these actual measurements.','Three-observation whole-child conservative charge excludes final supervisor own journal/fsync tail; originalR2 total unchanged.'])
 with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
 with OUT.with_suffix('.md').open('x')as f:f.write('# V PHYSICAL01 完整24保存节点独立后审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'。\n\n24数学/分支/限位通过；15点离散aligned clear、9点碰撞拒绝。原三根RBS与回溯false、一对依赖未执行不改判，independent_local/path始终false。保存重算仅矩阵残差、关节分支不变量和费用；新FK/J/IK/PQP/模型/规划调用0。source17 TCP/box/pair一致性单独保存诊断。\n')
 print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),failures=failed,sha256=sha(OUT))))
 if failed:raise SystemExit(2)
if __name__=='__main__':main()
