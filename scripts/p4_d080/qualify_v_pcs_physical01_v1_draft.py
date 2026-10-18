#!/usr/bin/env python3
"""DRAFT V fixed24 saved-node diagnostics. No model imports/calls before frozen execution."""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import select
import signal
import subprocess
import sys
import time
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
# Audited engineering helpers only; independent robot modules load inside execute.
import qualify_p4_full_r2_abb_cbirrt_d_distance_draft as old
import qualify_p4_full_r2_abb_sbl_pcs_setup_draft as L
import build_v_pcs_local_v1_draft as B
RUN='20261018_R2_D080_V_PCS_PHYSICAL01'
CLAIM='P4_D080_V_PCS_PHYSICAL01_FIXED24_60W120CPU_20261018'
LABEL='CORRECTED_COMAU_APC_RECONSTRUCTED_A02_FIXED24_INDEPENDENT_DISCRETE_DIAGNOSTIC'
PRE='reports/P4_D080_ENV_V_PCS_PHYSICAL01_PRE_DRAFT_20261018.md'
SUPERVISOR='scripts/p4_d080/supervise_v_pcs_physical01_v1_draft.py'
QUEUE='configs/p4_d080/v_pcs_local01_complete_saved_queue_v1.DRAFT.json'
QUEUE_SHA='6fa6da08e32e92068bad12346e14cf4d68440c6c205147937ea8c912daec8e35'
SOURCE_EXEC='results/p4_full/20261018_R2_D080_V_PCS_LOCAL01/execution.json'
SOURCE_EXEC_SHA='a0549cd8207b0a4c16e5adb71aab0f063859458a803916ba72db287e419d7985'
SOURCE_POST='reports/P4_D080_ENV_V_PCS_LOCAL01_SAVED_INDEPENDENT_POST_20261018.json'
SOURCE_POST_SHA='06c1a4c82db1accd7900b26e78c7bc84ebed33948e0b7d1d734aef877e00ac49'
QUEUE_POST='reports/P4_D080_ENV_V_PCS_LOCAL01_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_ADDENDUM_20261018.json'
QUEUE_POST_SHA='ca155059e6311e9f4cd5eb7485ac590ae795874fa32b03c8ae2b7f61f2e6c59c'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
COLLISION_SHA='c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388'
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
       'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon}
BUDGET={'wall_s':60.,'cpu_s':120.,'work_wall_s':50.,'work_cpu_s':100.,
        'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.}
B.RUN_NAME=RUN
B.RUN=ROOT/'results/p4_full'/RUN
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),SUPERVISOR,PRE,
     'scripts/p4_d080/materialize_v_pcs_local01_saved_queue_v1_draft.py',
     'scripts/qualify_p4_full_r2_abb_cbirrt_d_distance_draft.py',
     'scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py',
     'scripts/p4_d080/build_v_pcs_local_v1_draft.py',
     'scripts/recover_p4_full_r2_endpoints.py',
     'baselines/p4_full/analyze_comau_native_qualification.py',
     'baselines/p4_full/abb_independent_oracle.py',
     'baselines/p4_full/geometry_consistent/physical_nr.py',
     'baselines/p4_full/geometry_consistent/collision_adapter.py']
require=old.require
sha=old.sha
load=old.load
path=old.path
exact=old.exact
durable_new=old.durable_new

def current_prior(spec):
    # Current v6 charged-prior validator is reused directly; no historical sum rewrite.
    return B.validate_prior(spec)

def validate(spec,protocol,execute=False):
    require(spec['schema']=='P4_D080_V_PCS_PHYSICAL_FIXED24_RUN_V1' and spec['run_id']==RUN
        and spec['claim_id']==CLAIM and spec['classification']==LABEL and spec['environment']=='V'
        and spec['budget']==BUDGET and spec['gates']==GATES,'EXACT_V_FIXED24_PROTOCOL_REQUIRED')
    require(spec['queue']==QUEUE and spec['queue_sha256']==sha(QUEUE)==QUEUE_SHA
        and exact(spec['fixed_queue'],load(QUEUE)) and spec['execution_node_ids']==list(range(24))
        and spec['full_queue_node_count']==24 and spec['max_nodes_per_execution']==256
        and spec['fixed_queue']['stats']['unique_nodes']==24
        and spec['fixed_queue']['stats']['complete_union_under_limit'] is True,'COMPLETE_ORIGINAL24_QUEUE_REQUIRED')
    require(spec['max_math_arm_FK']==48 and spec['max_branch_identity']==48 and spec['max_collision_calls']==24
        and spec['max_adapter_internal_arm_FK_J']==96 and spec['max_PQP_queries']==4176,'EXACT_FIXED24_CALL_CAPS_REQUIRED')
    require(spec['zero_calls']=={'IK':0,'NR':0,'projection':0,'RBS':0,'solve':0,'RNG':0,'VI_constructions':0,'formal_table_I':0}
        and spec['formal_execution_authorized'] is False and spec['independent_local_qualified'] is False
        and spec['independent_path_qualified'] is False,'NO_NEW_CONSTRUCTION_PLANNING_OR_PATH_CLAIM')
    for name,wanted in spec['bound_files_sha256'].items():
        require(sha(name)==wanted,'FROZEN_BOUND_INPUT_CHANGED '+name)
    require(set(OWN)<=set(spec['own_source_sha256']) and all(
        spec['own_source_sha256'][n]==spec['bound_files_sha256'][n]==sha(n) for n in spec['own_source_sha256']),
        'ALL_OWN_AND_REUSED_SOURCE_BINDINGS_REQUIRED')
    for name,wanted in ((SOURCE_EXEC,SOURCE_EXEC_SHA),(SOURCE_POST,SOURCE_POST_SHA),(QUEUE_POST,QUEUE_POST_SHA),(COLLISION,COLLISION_SHA)):
        require(spec['bound_files_sha256'][name]==sha(name)==wanted,'EXACT_SAVED_SOURCE_AND_V3_CERTIFICATE_REQUIRED '+name)
    source_post=load(SOURCE_POST);queue_post=load(QUEUE_POST)
    require(source_post['personnel_independent'] is True and source_post['checks_total']==source_post['checks_passed']==194
        and source_post['checks_failed']==0 and source_post['execution_sha256']==SOURCE_EXEC_SHA
        and source_post['external_supervision_qualified'] is True,'SOURCE_TRANSPORT194_REQUIRED')
    require(queue_post['personnel_independent'] is True and queue_post['checks_total']==queue_post['checks_passed']==4
        and queue_post['checks_failed']==0 and queue_post['queue_sha256']==QUEUE_SHA
        and queue_post['reused_prior14_checks_without_rerun']['original_FAIL_retained'] is True,'COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_REQUIRED')
    for node in spec['fixed_queue']['nodes']:
        require(node['node_id'] in range(24) and node['role_branch_assignments'] and
            all(a['active_chain'] in (0,1) and a['passive_arm']==2-a['active_chain'] and
                type(a['requested_branch']) is int and a['requested_branch'] in range(8)
                for a in node['role_branch_assignments']),'ORIGINAL_ROLE_BRANCH_ASSIGNMENTS_REQUIRED')
    require(current_prior(spec)==spec['actual_charge_prior'],'LATEST_CHARGED_PRIOR_REQUIRED')
    require(spec['previous_r2_wall_s']==spec['prior']['wall_s'] and spec['previous_r2_cpu_s']==spec['prior']['cpu_s'],
            'CONSISTENT_PRIOR_COST_FIELDS_REQUIRED')
    scope=load('configs/p4_d080/execution_scope_v1.json')
    require(scope['allowed_environments']==['I','II','III','IV','V'] and scope['VI_future_science_authorized'] is False
        and scope['formal_table_I_D080']==18000 and scope['formal_execution_authorized'] is False,'D080_SCOPE_REQUIRED')
    require(L.preload_state()==spec['system_preload_state'],'SYSTEM_PRELOAD_CHANGED')
    require(set(spec['reviews'])=={'independent_static_review_passed','root_complete_queue_freeze_approved','latest_actual_prior_confirmed'}
        and all(type(v) is bool for v in spec['reviews'].values()),'EXPLICIT_REVIEW_FLAGS_REQUIRED')
    if not execute:return None
    require(spec['frozen'] is True and spec['scientific_execution_authorized'] is True
        and all(spec['reviews'].values()),'FROZEN_REVIEWED_SINGLE_RUN_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for n in [*spec['own_source_sha256'],str(protocol.relative_to(ROOT))]:
        require(subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)==path(n).read_bytes(),'UNCOMMITTED_V_PHYSICAL_SOURCE_OR_PROTOCOL '+n)
    return commit

class Budget(old.Budget):
    def __init__(self,spec,begun,cpu_start):
        super().__init__(spec,begun,cpu_start)
        self.wall_cap=min(50.,3600.-spec['previous_r2_wall_s']-10.)
        self.cpu_cap=min(100.,7200.-spec['previous_r2_cpu_s']-20.)
        require(min(self.wall_cap,self.cpu_cap)>0,'V_PHYSICAL_TOTAL_BUDGET_EXHAUSTED')

def supervisor_proof(spec,protocol):
    ext=spec['external_supervision'];metadata=path(ext['metadata_path'])
    planned_raw=metadata.read_bytes().splitlines(keepends=True)[0];planned=json.loads(planned_raw)
    parent=os.getppid();row=old.stat_row(parent)
    require(row is not None and int(row[1])==planned['supervisor_pid'],'EXACT_SUPERVISOR_PARENT_CHAIN_REQUIRED')
    require(planned['event']=='planned_launch'and planned['run_id']==RUN and planned['protocol_sha256']==sha(protocol)
        and planned['runner_sha256']==sha(__file__)and planned['supervisor_source_sha256']==sha(SUPERVISOR),'EXACT_SUPERVISOR_SOURCE_PROTOCOL_REQUIRED')
    require(sha(Path('/proc',str(parent),'exe'))==ext['time_binary_sha256'],'ACTUAL_PARENT_GNU_TIME_REQUIRED')
    expected=['/usr/bin/time','--quiet','-f',ext['format'],'-o',f"/proc/self/fd/{planned['time_fd']}",'/usr/bin/python3',str(Path(__file__).resolve()),'--protocol',str(protocol)]
    require(Path('/proc',str(parent),'cmdline').read_bytes().rstrip(b'\0').split(b'\0')==[v.encode()for v in expected]
        and planned['argv']==expected,'ACTUAL_TIME_ARGV_MISMATCH')
    sibling=path(ext['sibling_path']).stat();held=[]
    for p in Path('/proc',str(parent),'fd').iterdir():
        try:
            s=p.stat()
            if(s.st_ino,s.st_dev)==(sibling.st_ino,sibling.st_dev):held.append(int(p.name))
        except FileNotFoundError:pass
    require(held and sibling.st_ino==planned['time_inode']and sibling.st_dev==planned['time_device'],'EXCLUSIVE_SUPERVISION_INODE_MISMATCH')
    return dict(actual_time_pid=parent,actual_time_start_ticks=int(row[19]),supervisor_pid=planned['supervisor_pid'],
        actual_argv=expected,planned_launch_line_sha256=hashlib.sha256(planned_raw).hexdigest(),
        time_inode=sibling.st_ino,time_device=sibling.st_dev,actual_time_output_fds=sorted(held),external_POST_required=True)

def execute(spec,protocol):
    # Admission and actual GNUtime identity proof happen before a fresh claim.
    begun=time.monotonic();cpu_start=old.own_reaped_cpu();commit=validate(spec,protocol,True)
    launch=supervisor_proof(spec,protocol);folder=ROOT/'results/p4_full'/RUN
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXCLUSIVE_P_NO_RETRY_RESET_OR_RESUME')
    require(not old.builder.active_p4(),'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    budget=None;journal=None;physical_nr=None;adapter=None;original=None;adapter_process_api=None
    diagnostics=[];results=[];counts=Counter();current=None;error=None;worker_evidence=[]
    record=dict(schema='P4_D080_V_PCS_PHYSICAL01_EXECUTION_V1',run_id=RUN,classification=LABEL,
        status='STOP_SETUP_PREFIX_RETAINED',source_commit=commit,protocol=str(protocol.relative_to(ROOT)),
        protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),budget=spec['budget'],
        source_provenance=spec['source_provenance'],queue_provenance=spec['queue_provenance'],execution_node_ids=spec['execution_node_ids'],bound_files_sha256=spec['bound_files_sha256'],
        prior_execution_sha256=spec['prior_execution_sha256'],actual_charge_prior=spec['actual_charge_prior'],
        previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],
        supervisor_launch_proof=launch,external_supervision_qualified=False,independent_saved_POST_required=True,
        independent_local_qualified=False,independent_path_qualified=False,continuous_collision_certificate=False,
        zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0)
    def event(kind,**values):
        if journal is not None:journal.add(kind,**values)
    def diagnostic(stage,exc):diagnostics.append(dict(stage=stage,error=repr(exc)))
    try:
        durable_new(claim,dict(schema='P4_D080_V_PCS_PHYSICAL01_CLAIM_V1',run_id=RUN,
            protocol=record['protocol'],protocol_sha256=record['protocol_sha256'],source_commit=commit,
            budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=L.Journal(folder/'events.jsonl')
        event('setup',record=record);budget=Budget(spec,begun,cpu_start);budget.start();budget.check()
        durable_new(folder/'complete_original_saved_queue.json',spec['fixed_queue'])
        os.environ.update(old.builder.THREADS);sys.path.insert(0,str(ROOT))
        from baselines.p4_full.geometry_consistent import physical_nr as physical_module
        from baselines.p4_full.geometry_consistent import collision_adapter as collision_module
        import recover_p4_full_r2_endpoints as oracle
        physical_nr,adapter=physical_module,collision_module;original=physical_nr.arm_fk_jac
        # Lifecycle-only adapter around the unchanged collision worker transport.
        # Only fork/exec/PID registration masks our alarm; no scientific body is
        # replaced. A direct-child group lets the parent kill/reap every worker.
        adapter_process_api=adapter.subprocess
        require(not adapter._sessions,'PREEXISTING_COLLISION_SESSION_REFUSE_REUSE')
        def registered_popen(*args,**kwargs):
            budget.check();previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
            try:
                def limits():
                    signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
                    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
                require('start_new_session'not in kwargs and 'preexec_fn'not in kwargs,'UNEXPECTED_COLLISION_LAUNCH_HOOK')
                counts['collision_worker_start_attempted']+=1;event('collision_worker_start_attempted',command=args[0])
                proc=subprocess.Popen(*args,**kwargs,start_new_session=True,preexec_fn=limits)
                budget.processes.append(proc);counts['collision_worker_started']+=1
                event('collision_worker_started',pid=proc.pid,command=args[0])
            finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
            group=old.process_group_members(proc.pid)
            worker_evidence.append(dict(pid=proc.pid,command=args[0],start_process_group=group))
            event('collision_worker_start_group',pid=proc.pid,members=group)
            require([r['pid']for r in group]==[proc.pid],'COLLISION_WORKER_START_GROUP_NOT_SINGLE_CHILD')
            budget.check();return proc
        adapter.subprocess=SimpleNamespace(Popen=registered_popen,PIPE=subprocess.PIPE,STDOUT=subprocess.STDOUT,
            TimeoutExpired=subprocess.TimeoutExpired)
        # This counting wrapper and the complete node loop below are copied
        # from the already qualified original PCS path source, without changing
        # its FK/closure/limits/branch/collision predicates or node order.
        def counted(q,env,arm):
            budget.remaining();require(counts['adapter_internal_arm_FK_J_started']<spec['max_adapter_internal_arm_FK_J'],'ADAPTER_FK_CAP')
            counts['adapter_internal_arm_FK_J_started']+=1;event('adapter_internal_FK_J_started',arm=arm,q6=list(q))
            ans=original(q,env,arm);counts['adapter_internal_arm_FK_J_completed']+=1
            event('adapter_internal_FK_J_completed',arm=arm);return ans
        physical_nr.arm_fk_jac=counted
        # V adaptation only: unchanged independent endpoint kernel, explicit original24 queue.
        for i in spec['execution_node_ids']:
            q=spec['fixed_queue']['nodes'][i]['q12'];budget.remaining()
            require(i<spec['max_nodes_per_execution'],'COMPLETE_QUEUE_OVER256_NO_TRUNCATION')
            current={'node_id':i,'q12':q,'poses':[],'branches':[],'stage':'STARTED'}
            event('math_node_started',node_id=i,q12=q)
            for a in range(2):
                budget.remaining();require(counts['math_arm_FK_started']<spec['max_math_arm_FK'],'MATH_FK_CAP')
                counts['math_arm_FK_started']+=1;event('math_arm_FK_started',node_id=i,arm=a+1)
                pose=oracle.arm_fk(q[6*a:6*a+6],'V',a+1);counts['math_arm_FK_completed']+=1
                current['poses'].append(pose.tolist());durable_new(folder/f'node_{i:05d}_arm{a+1}.json',current)
                event('math_arm_FK_completed',node_id=i,arm=a+1,pose=pose.tolist())
            import numpy as np
            poses=[np.asarray(p) for p in current['poses']]
            metric=oracle.matrix_error(poses[1],poses[0]@oracle.grasps_for('V')[0]@oracle.FLIP)
            limits=oracle.limit_score(q,'V')
            for a in range(2):
                budget.remaining();require(counts['branch_identity_started']<spec['max_branch_identity'],'BRANCH_IDENTITY_CAP')
                counts['branch_identity_started']+=1
                current['branches'].append(oracle.branch_identity(q[6*a:6*a+6],'V',GATES['branch_zero_relative_epsilon']))
                counts['branch_identity_completed']+=1
            assignments=[dict(a,branch_pass=a['requested_branch'] in current['branches'][1-a['active_chain']]['branch_set'])
                         for a in spec['fixed_queue']['nodes'][i]['role_branch_assignments']]
            mathok=(metric['position_max_abs']<=GATES['position_maxabs_mm'] and
                metric['rotation_matrix_max_abs']<=GATES['rotation_matrix_maxabs'] and limits['legal'] and
                bool(assignments) and all(a['branch_pass'] for a in assignments))
            current.update(stage='MATH_COMPLETED',closure=metric,limits=limits,role_branch_assignments=assignments,math_qualified=bool(mathok))
            durable_new(folder/f'node_{i:05d}_math.json',current);event('math_node_completed',node_id=i,math_qualified=bool(mathok))
            budget.remaining();require(counts['collision_calls_started']<spec['max_collision_calls'],'COLLISION_CALL_CAP')
            counts['collision_calls_started']+=1;current['stage']='COLLISION_STARTED';event('collision_started',node_id=i)
            collision=adapter.check_collision('V',q,timeout_s=min(10.,budget.remaining()),manifest_path=COLLISION)
            counts['collision_calls_completed']+=1;current.update(stage='COLLISION_RESPONSE_RETAINED',collision=collision)
            durable_new(folder/f'node_{i:05d}_collision_response.json',collision);event('collision_response_retained',node_id=i,response=collision)
            variants=collision.get('variants',{});codes_qualified=set(variants)=={'native','aligned'}
            for variant,response in variants.items():
                codes=response.get('query_codes',[]);counts['PQP_queries']+=len(codes)
                codes_qualified=codes_qualified and len(codes)==87 and all(type(v) is int and v==0 for v in codes)
            require(counts['PQP_queries']<=spec['max_PQP_queries'],'FIXED_PQP_CAP')
            collisionok=(collision.get('status')=='CHECKED' and collision.get('selected_variant')=='aligned' and
                collision.get('manifest_sha256')==spec['bound_files_sha256'][COLLISION] and
                type(collision.get('collision')) is bool and codes_qualified and
                variants.get('aligned',{}).get('pose_consistency',{}).get('passed') is True)
            current['collision_response_qualified']=bool(collisionok)
            require(collisionok,'V_COLLISION_RUNTIME_OR_TCP_EVIDENCE_UNQUALIFIED_PREFIX_RETAINED')
            current.update(stage='COMPLETED',collision_response_qualified=bool(collisionok),
                qualified=bool(mathok and collisionok and collision['collision'] is False))
            durable_new(folder/f'node_{i:05d}.json',current);results.append(current)
            event('node_completed',node_id=i,qualified=current['qualified']);current=None;budget.remaining()
        require([r['node_id']for r in results]==spec['execution_node_ids'],'COMPLETE_FIXED24_REQUIRED')
        require(counts['math_arm_FK_started']==counts['math_arm_FK_completed']==48
            and counts['branch_identity_started']==counts['branch_identity_completed']==48
            and counts['collision_calls_started']==counts['collision_calls_completed']==24
            and counts['adapter_internal_arm_FK_J_started']==counts['adapter_internal_arm_FK_J_completed']==96
            and counts['PQP_queries']==4176,'COMPLETE_FIXED24_SCIENTIFIC_COUNTS_REQUIRED')
        record.update(status='COMPLETED_FIXED24_DIAGNOSTIC_PENDING_INDEPENDENT_POST',
            all_saved_nodes_qualified=all(r['qualified']for r in results),
            rejected_node_ids=[r['node_id']for r in results if not r['qualified']],
            diagnosis_complete_does_not_imply_local_or_path_success=True)
        budget.check()
    except BaseException as exc:
        if budget is not None:budget.close()
        error=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc))
        if current is not None and folder.is_dir():
            try:durable_new(folder/f'node_{current["node_id"]:05d}_stopped_partial.json',current)
            except BaseException as write_error:diagnostic('stopped_partial_node_preservation',write_error)
        try:event('stopped',reason=repr(exc))
        except BaseException as write_error:diagnostic('stopped_event_preservation',write_error)
    finally:
        if budget is not None:
            try:budget.close()
            except BaseException as exc:diagnostic('disable_timer_before_cleanup',exc)
        if physical_nr is not None and original is not None:physical_nr.arm_fk_jac=original
        processes=[]if budget is None else list({p.pid:p for p in budget.processes}.values())
        # Retain both exact process-group snapshots before graceful close.
        for proc in processes:
            try:
                group=old.process_group_members(proc.pid)
                event('collision_worker_close_group',pid=proc.pid,members=group)
                next(r for r in worker_evidence if r['pid']==proc.pid)['close_process_group']=group
                require([r['pid']for r in group]==[proc.pid],'COLLISION_WORKER_CLOSE_GROUP_NOT_SINGLE_CHILD')
            except BaseException as exc:diagnostic('worker_close_process_group',exc)
        sessions=[]if adapter is None else list(adapter._sessions.values())
        if adapter is not None:
            try:adapter.close_sessions()
            except BaseException as exc:diagnostic('original_collision_sessions_close',exc)
        # Registry includes Popen instances even if adapter initialization failed
        # before its _sessions assignment. No registry entry is silently dropped.
        for proc in processes:
            try:
                remaining_group=old.process_group_members(proc.pid)
                event('collision_worker_after_original_close_group',pid=proc.pid,members=remaining_group)
                if remaining_group:
                    os.killpg(proc.pid,signal.SIGKILL)
                proc.wait(timeout=1.)
                require(not old.process_group_members(proc.pid),'COLLISION_WORKER_GROUP_REMAINS_AFTER_REAP')
            except BaseException as exc:diagnostic('central_collision_worker_kill_reap',exc)
        for session in sessions:
            try:
                pending=session.pending;tail=bytearray();eof=False
                selector_closed=session.selector.get_map()is None
                require(selector_closed,'ORIGINAL_COLLISION_SELECTOR_NOT_CLOSED')
                require(session.proc.stdout is not None and not session.proc.stdout.closed,'COLLISION_STDOUT_UNAVAILABLE_BEFORE_EOF_AUDIT')
                # Observe EOF with a finite drain; never equate a swallowed
                # adapter.close exception with a closed selector or empty pipe.
                fd=session.proc.stdout.fileno();os.set_blocking(fd,False);deadline=time.monotonic()+1.
                while not eof:
                    remaining=deadline-time.monotonic();require(remaining>0,'COLLISION_STDOUT_EOF_DRAIN_TIMEOUT')
                    if not select.select([fd],[],[],remaining)[0]:continue
                    try:chunk=os.read(fd,65536)
                    except BlockingIOError:continue
                    if chunk:tail.extend(chunk)
                    else:eof=True
                row=next(r for r in worker_evidence if r['pid']==session.proc.pid)
                row.update(stdout_pending_base64=base64.b64encode(pending).decode(),stdout_EOF_tail_base64=base64.b64encode(bytes(tail)).decode(),
                    original_selector_closed=selector_closed,pipe_EOF_drained=eof)
                event('collision_worker_final_raw_tail',pid=session.proc.pid,pending_base64=row['stdout_pending_base64'],tail_base64=row['stdout_EOF_tail_base64'])
                require(not pending and not tail,'UNEXPECTED_COLLISION_WORKER_STDOUT_TAIL')
            except BaseException as exc:diagnostic('worker_original_stdout_tail',exc)
        for proc in processes:
            for stream in(proc.stdin,proc.stdout,proc.stderr):
                try:
                    if stream is not None and not stream.closed:stream.close()
                except BaseException as exc:diagnostic('collision_worker_pipe_close',exc)
        if adapter is not None and adapter_process_api is not None:adapter.subprocess=adapter_process_api
        record['collision_worker_registry']=[dict(pid=p.pid,reaped=p.returncode is not None,returncode=p.returncode)for p in processes]
        record['collision_worker_evidence']=worker_evidence
        worker_gate=(len(processes)==counts['collision_worker_started']==2 and len(sessions)==2
            and {r['pid']for r in worker_evidence}=={p.pid for p in processes}=={s.proc.pid for s in sessions}
            and all(p.returncode==0 for p in processes)and all(r.get('pipe_EOF_drained')is True and r.get('stdout_pending_base64')==r.get('stdout_EOF_tail_base64')==''for r in worker_evidence))
        record['complete_collision_worker_cleanup_gate']=worker_gate
        if record['status'].startswith('COMPLETED_')and not worker_gate:record['status']='STOP_WORKER_EOF_EXIT_OR_REGISTRY_UNQUALIFIED'
        try:
            after={n:sha(n)for n in spec['bound_files_sha256']};record['bound_files_after_sha256']=after
            require(after==spec['bound_files_sha256'],'P_BOUND_ASSET_CHANGED')
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
            require(record['protocol_after_sha256']==record['protocol_sha256']and record['claim_after_sha256']==record.get('claim_sha256'),'P_PROTOCOL_OR_CLAIM_CHANGED')
            latest=current_prior(spec);record['prior_execution_after_sha256']={n:sha(n)for n in spec['prior_execution_sha256']}
            require(latest==spec['actual_charge_prior'],'P_PRIOR_CHARGED_LEDGER_CHANGED')
        except BaseException as exc:diagnostic('mandatory_final_hashes',exc)
        try:
            if journal is not None:
                event('final_counts',counts=dict(counts),diagnostics=diagnostics);journal.finish()
                record['events']=str((folder/'events.jsonl').relative_to(ROOT));record['events_sha256']=sha(folder/'events.jsonl')
            if folder.is_dir():record['retained_run_files_sha256']={str(p.relative_to(ROOT)):sha(p)for p in sorted(folder.rglob('*'))if p.is_file()}
        except BaseException as exc:diagnostic('final_evidence_preservation',exc)
        record.update(counts=dict(counts),wall_s=time.monotonic()-begun,cpu_s=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
            node_count=len(spec['execution_node_ids']),original_full_queue_node_count=len(spec['fixed_queue']['nodes']),completed_nodes=len(results),qualified_nodes=sum(r['qualified']for r in results),
            completed_original_node_ids=[r['node_id']for r in results],uncompleted_node_ids=[i for i in spec['execution_node_ids']if i not in {r['node_id']for r in results}],
            full_queue_checked=[r['node_id']for r in results]==spec['execution_node_ids'],binary_execution_calls=counts['collision_worker_started'],diagnostics=diagnostics)
        if record['wall_s']>=min(60.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(120.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_D080_V_PCS_PHYSICAL01_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(60.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(120.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            with(folder/'cost_receipt.jsonl').open('xb')as stream:stream.write(json.dumps(receipt,allow_nan=False,separators=(',',':')).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
            record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),node_count=record['node_count'],completed_nodes=record['completed_nodes'],qualified_nodes=record['qualified_nodes'],
        external_supervision_qualified=False,independent_saved_POST_required=True,continuous_collision_certificate=False)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status')=='COMPLETED_FIXED24_DIAGNOSTIC_PENDING_INDEPENDENT_POST','V_COMPLETE_DIAGNOSTIC_DID_NOT_FINISH')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args();protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:
        validate(spec,protocol);print('STATIC_V_PHYSICAL_DRAFT_VALIDATED_NO_MODEL_EXECUTION');return
    execute(spec,protocol)

if __name__=='__main__':main()
