#!/usr/bin/env python3
"""DRAFT complete III saved PCS path: old scientific loop, existing lifecycle.

No import-time robot/model calls. A complete actual SOURCE01 queue and its
independent saved POST must exist before a separate frozen physical execution.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import hashlib
import io
import json
import math
import os
from pathlib import Path
import resource
import select
import signal
import subprocess
import sys
import tarfile
import time
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(Path(__file__).resolve().parent)]
import qualify_p4_full_r2_abb_cbirrt_d_distance_draft as old
import qualify_p4_full_r2_abb_sbl_pcs_setup_draft as L
import build_v_pcs_local_v1_draft as B
import validate_prior_preflight_recovery_v1 as P
import materialize_iii_rrt_pcs_source01_saved_v1_draft as saved
RUN='20261018_R2_D080_III_RRT_PCS_PHYSICAL01'
CLAIM='P4_D080_III_RRT_PCS_PHYSICAL01_FULL2048_120W240CPU_20261018'
LABEL='RECONSTRUCTED_A01_CORRECTED_ABB_APC_III_ORIGINAL_RRT_PCS_COMPLETE_DISCRETE_SOURCE_POLICY'
PRE='reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_PRE_DRAFT_20261018.md'
SUPERVISOR='scripts/p4_d080/supervise_iii_rrt_pcs_physical01_v1_draft.py'
SOURCE_EXEC='results/p4_full/20261018_R2_D080_III_RRT_PCS_SOURCE01/execution.json'
SOURCE_EXEC_SHA='f9229c0c2b768f76f540e4667545b09d2b1c425957817cb0a284f696760f39b0'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
COLLISION_SHA='c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388'
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
    'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon}
BUDGET={'wall_s':120.,'cpu_s':240.,'work_wall_s':100.,'work_cpu_s':200.,
    'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.}
B.RUN_NAME=RUN
B.RUN=ROOT/'results/p4_full'/RUN
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),SUPERVISOR,PRE,
    'scripts/p4_d080/materialize_iii_rrt_pcs_source01_saved_v1_draft.py',
    'scripts/p4_d080/qualify_iii_rrt_pcs_source01_v1_draft.py',
    'scripts/p4_d080/build_v_pcs_local_v1_draft.py',
    'scripts/p4_d080/validate_prior_preflight_recovery_v1.py',
    'scripts/qualify_p4_full_r2_abb_cbirrt_d_distance_draft.py',
    'scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py',
    'scripts/qualify_p4_full_r2_abb_rrt_path.py',
    'scripts/qualify_p4_full_r2_abb_cbirrt_nr_path_draft.py',
    'scripts/recover_p4_full_r2_endpoints.py',
    'baselines/p4_full/geometry_consistent/collision_adapter.py',
    'baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/abb_independent_oracle.py',
    'baselines/p4_full/analyze_comau_native_qualification.py']
require=old.require
sha=old.sha
load=old.load
path=old.path
exact=old.exact
durable_new=old.durable_new

def new_json(p,value):
    # Same immediate-close writer as qualified NR393; final archive is fsynced.
    with Path(p).open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def current_prior(spec):return P.validate_prior(spec,RUN,ROOT/'results/p4_full'/RUN)

def validate(spec,protocol,execute=False):
    require(spec['schema']=='P4_D080_III_RRT_PCS_PHYSICAL01_FROZEN_V1' and spec['run_id']==RUN
        and spec['claim_id']==CLAIM and spec['classification']==LABEL and spec['environment']=='III'
        and spec['budget']==BUDGET and spec['gates']==GATES,'EXACT_III_PHYSICAL_PROTOCOL_REQUIRED')
    require(sha(SOURCE_EXEC)==SOURCE_EXEC_SHA and sha(COLLISION)==COLLISION_SHA,
        'EXACT_ACTUAL_SOURCE01_AND_ORIGINAL_COLLISION_V3_REQUIRED')
    queue=load(spec['queue_path'])
    require(spec['queue_path']=='configs/p4_d080/iii_rrt_pcs_source01_complete_saved_queue_v1.DRAFT.json'
        and sha(spec['queue_path'])==spec['queue_sha256']=='037b754847718d5bc2a929c7600d354c61b785d249eeacd31548c52f84fdf1d9'
        and queue['environment']=='III'
        and queue['status']=='DRAFT_COMPLETE_SAVED_QUEUE_PENDING_INDEPENDENT_PHYSICAL_FREEZE'
        and queue['new_binary_model_scientific_calls']==0 and queue['independent_path_qualified']is False
        and exact(spec['fixed_queue'],queue['fixed_queue']),'COMPLETE_SAVED_SOURCE_QUEUE_REQUIRED')
    d,files=saved.saved_inputs(SOURCE_EXEC_SHA,path(queue['source_independent_POST']),queue['source_independent_POST_sha256'])
    require(exact(saved.materialize(d),spec['fixed_queue']) and queue['source_execution_sha256']==SOURCE_EXEC_SHA,
        'FULL_ORIGINAL_MATERIALIZATION_NO_NEW_NODES_REQUIRED')
    n=len(spec['fixed_queue']['nodes'])
    require(n==649 and n<=2048 and spec['execution_node_ids']==list(range(n)) and spec['full_queue_node_count']==n
        and spec['max_nodes_per_execution']==2048 and spec['max_math_arm_FK']==2*n
        and spec['max_branch_identity']==2*n and spec['max_collision_calls']==n
        and spec['max_adapter_internal_arm_FK_J']==4*n,'COMPLETE_ORIGINAL_QUEUE_AND_EXACT_CAPS_REQUIRED')
    manifest=load(COLLISION);entries=[e for e in manifest['entries']if e['model']=='abb']
    require(sorted(e['variant']for e in entries)==['aligned','native']
        and all(e['exit_code']==0 for e in entries),'EXISTING_ABB_NATIVE_ALIGNED_WORKERS_REQUIRED')
    # Original III env2 executes 0..76, then 77..102 unless its original
    # TCP-height >800mm source-policy rejection returns early. The manifest's
    # query_count=0 is build-time metadata and is not this per-query bound.
    pairs={'native':103,'aligned':103}
    require(spec['pair_counts']==pairs and spec['max_PQP_queries']==n*sum(pairs.values()),
        'ORIGINAL_PAIR_LIST_EXACT_QUERY_CAP_REQUIRED')
    assets={COLLISION:COLLISION_SHA}
    for e in entries:
        assets[e['binary']]=e['binary_sha256']
        assets[str(Path(e['cwd'])/'validity_checkers/collisionDetection.cpp')]=e['instrumented_source_sha256']
        assets.update({str(Path(e['source_root'])/name):digest for name,digest in e['source_files_sha256'].items()})
        assets.update({str(Path(e['cwd'])/'simulator'/name):digest for name,digest in e['mesh_sha256'].items()})
    for name,digest in {**files,**assets}.items():
        require(spec['bound_files_sha256'].get(name)==digest and sha(name)==digest,'SOURCE_OR_COLLISION_ASSET_BINDING '+name)
    require(spec['geometry']=={'base_distance_mm':1200.,'arm_bases_mm_rad':[[-600.,0.,0.],[600.,0.,3.1416]],
        'grasp_rod_mm':500.,'source_internal_environment':2,'collision_adapter_model':'abb',
        'worker_environment_argument':'III','source_PQP_tolerance_mm':8.},'EXPLICIT_ORIGINAL_III_GEOMETRY_REQUIRED')
    require(spec['zero_calls']=={'IK':0,'NR':0,'projection':0,'RBS':0,'solve':0,'RNG':0,'VI_constructions':0,'formal_table_I':0}
        and spec['formal_execution_authorized']is False and spec['independent_path_qualified']is False,
        'NO_NEW_SOLVE_PROJECTION_OR_PREMATURE_PATH_CLAIM')
    for name,digest in spec['bound_files_sha256'].items():require(sha(name)==digest,'FROZEN_BOUND_INPUT_CHANGED '+name)
    require(set(OWN)<=set(spec['own_source_sha256']) and all(spec['own_source_sha256'][n]==spec['bound_files_sha256'][n]==sha(n)
        for n in spec['own_source_sha256']),'ALL_OWN_AND_REUSED_SOURCES_PREBOUND')
    require(current_prior(spec)==spec['actual_charge_prior'] and spec['previous_r2_wall_s']==spec['prior']['wall_s']
        and spec['previous_r2_cpu_s']==spec['prior']['cpu_s'],'LATEST_CHARGED_PRIOR_REQUIRED')
    require(all(spec['bound_files_sha256'].get(n)==digest for n,digest in spec['actual_charge_prior']['evidence_sha256'].items()),
        'ALL_PRIOR_CHARGED_CERTIFICATE_BYTES_PREBOUND')
    scope=load(B.SCOPE)
    require(sha(B.SCOPE)==B.SCOPE_SHA and sha(B.OVERLAY)==B.OVERLAY_SHA
        and scope['allowed_environments']==['I','II','III','IV','V'] and scope['VI_future_science_authorized']is False
        and scope['formal_table_I_D080']==18000 and scope['formal_execution_authorized']is False,'D080_SCOPE_REQUIRED')
    require(L.preload_state()==spec['system_preload_state'],'SYSTEM_PRELOAD_CHANGED')
    require(set(spec['reviews'])=={'independent_static_review_passed','root_complete_queue_freeze_approved','latest_actual_prior_confirmed'}
        and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_REVIEW_FLAGS_REQUIRED')
    if not execute:return None
    require(spec['frozen']is True and spec['scientific_execution_authorized']is True
        and all(spec['reviews'].values()),'FROZEN_REVIEWED_SINGLE_PHYSICAL_RUN_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in[*spec['own_source_sha256'],str(protocol.relative_to(ROOT))]:
        require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),
            'UNCOMMITTED_III_PHYSICAL_SOURCE_OR_PROTOCOL '+name)
    return commit

class Budget(old.Budget):
    def __init__(self,spec,begun,cpu_start):
        super().__init__(spec,begun,cpu_start)
        self.wall_cap=min(100.,3600.-spec['previous_r2_wall_s']-20.)
        self.cpu_cap=min(200.,7200.-spec['previous_r2_cpu_s']-40.)
        require(min(self.wall_cap,self.cpu_cap)>0,'III_PHYSICAL_TOTAL_BUDGET_EXHAUSTED')


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

def active_d080(supervisor):
    # Thin copy of III BUILD01 active_d080; launch-proof key adapted only.
    allowed = {os.getpid(), supervisor['actual_time_pid'], supervisor['supervisor_pid']}
    active = []
    directory = str(ROOT / 'scripts/p4_d080') + '/'
    for entry in Path('/proc').glob('[0-9]*/cmdline'):
        pid = int(entry.parent.name)
        if pid in allowed:
            continue
        try:
            parts = entry.read_bytes().split(b'\0')
        except OSError:
            continue
        exe = parts[0].decode(errors='replace') if parts else ''
        scripts = [p.decode(errors='replace') for p in parts[1:3]] if 'python' in exe else []
        resolved = []
        for script in scripts:
            if script.startswith('-'):
                continue
            try:
                resolved.append(str((Path('/proc', str(pid), 'cwd') / script).resolve(strict=True)))
            except OSError:
                continue
        if any(s.startswith(directory) and Path(s).name.startswith(('build_', 'qualify_', 'supervise_')) for s in resolved):
            active.append({'pid': pid, 'command': b' '.join(parts).decode(errors='replace')})
    return active

class FinalIOGuard:
    """Absolute original budget remains active through expensive final I/O."""
    def __init__(self,budget):self.budget=budget;self.previous=None;self.armed=False
    def __enter__(self):
        require(self.budget is not None,'NO_RUN_BUDGET_FOR_FINAL_IO')
        self.budget.check();require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_FINAL_IO_TIMER')
        self.previous=signal.getsignal(signal.SIGALRM);signal.signal(signal.SIGALRM,self.alarm)
        signal.setitimer(signal.ITIMER_REAL,.02,.02);self.armed=True;return self
    def alarm(self,*_):
        try:self.budget.check()
        except BaseException:
            # One interruption only. Failure preservation does not retry the
            # heavy copy or verification after the absolute budget expires.
            signal.setitimer(signal.ITIMER_REAL,0);raise
    def __exit__(self,*_):
        if not self.armed:return
        previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            signal.setitimer(signal.ITIMER_REAL,0)
            while signal.SIGALRM in signal.sigpending():signal.sigwait({signal.SIGALRM})
            signal.signal(signal.SIGALRM,self.previous);self.armed=False
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)

def durable_saved_snapshot(folder,budget):
    """Keep loose files and one byte-verified durable recovery envelope."""
    archive=folder/'complete_saved_prefix.tar'
    require(not archive.exists(),'EXCLUSIVE_SAVED_PREFIX_ARCHIVE_NO_RETRY')
    loose=sorted(p for p in folder.rglob('*')if p.is_file())
    require(all(not p.is_symlink()for p in loose),'REGULAR_NEW_RUN_FILES_ONLY')
    members={}
    with archive.open('xb')as output:
        with tarfile.open(fileobj=output,mode='w',format=tarfile.PAX_FORMAT)as packed:
            for filename in loose:
                budget.check();raw=filename.read_bytes();name=str(filename.relative_to(folder))
                digest=hashlib.sha256(raw).hexdigest();members[name]=dict(sha256=digest,bytes=len(raw))
                info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o600;info.mtime=0
                packed.addfile(info,io.BytesIO(raw));budget.check()
        output.flush();budget.check();os.fsync(output.fileno());budget.check()
    directory=os.open(folder,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(directory);budget.check()
    finally:os.close(directory)
    seen={}
    with tarfile.open(archive,'r:')as packed:
        for member in packed:
            budget.check();require(member.isfile()and member.name in members and member.name not in seen,'EXACT_UNIQUE_SNAPSHOT_MEMBERS_REQUIRED')
            raw=packed.extractfile(member).read();seen[member.name]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
            require(seen[member.name]==members[member.name]and member.size==members[member.name]['bytes'],'SNAPSHOT_MEMBER_BYTES_OR_SHA_CHANGED')
            filename=folder/member.name;require(filename.read_bytes()==raw,'LOOSE_AND_DURABLE_SNAPSHOT_MEMBER_BYTES_DIFFER')
            budget.check()
    require(seen==members and set(loose)=={p for p in folder.rglob('*')if p.is_file()and p!=archive},'COMPLETE_SNAPSHOT_SET_NO_MISSING_OR_EXTRA_FILE')
    budget.check();digest=sha(archive);budget.check()
    return dict(path=str(archive.relative_to(ROOT)),sha256=digest,members=members,members_verified=len(seen),
        archive_file_fsync_completed=True,containing_directory_fsync_completed=True,loose_files_byte_exact=True,
        scope='All closed loose node/partial/queue files and finished journal at finalization boundary. Execution/receipt follow as separately durable files.',
        partial_or_unverified_archive_policy='STOP_PREFIX_RETAINED; no resume, overwrite or success claim')

def execute(spec,protocol):
    # Admission and actual GNUtime identity proof happen before a fresh claim.
    begun=time.monotonic();cpu_start=old.own_reaped_cpu();commit=validate(spec,protocol,True)
    launch=supervisor_proof(spec,protocol);folder=ROOT/'results/p4_full'/RUN
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXCLUSIVE_P_NO_RETRY_RESET_OR_RESUME')
    require(not old.builder.active_p4()and not active_d080(launch),'OTHER_ACTIVE_P4_OR_D080_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    budget=None;journal=None;physical_nr=None;adapter=None;original=None;adapter_process_api=None
    diagnostics=[];results=[];counts=Counter();current=None;error=None;worker_evidence=[]
    record=dict(schema='P4_D080_III_RRT_PCS_PHYSICAL01_EXECUTION_V1',run_id=RUN,classification=LABEL,
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
        durable_new(claim,dict(schema='P4_D080_III_RRT_PCS_PHYSICAL01_CLAIM_V1',run_id=RUN,
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
                    resource.setrlimit(resource.RLIMIT_CPU,(240,240))
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
        common=old
        for i,q in ((i,spec['fixed_queue']['nodes'][i])for i in spec['execution_node_ids']):
            budget.remaining()
            if i>=spec['max_nodes_per_execution']:raise common.StopQualification('FIXED_2048_NODE_RESOURCE_STOP_FULL_TAIL_UNCHECKED')
            current={'node_id':i,'q12':q,'poses':[],'branches':[],'stage':'STARTED'};event('math_node_started',node_id=i,q12=q)
            for a in range(2):
                budget.remaining();require(counts['math_arm_FK_started']<spec['max_math_arm_FK'],'MATH_FK_CAP')
                counts['math_arm_FK_started']+=1;event('math_arm_FK_started',node_id=i,arm=a+1)
                pose=oracle.arm_fk(q[6*a:6*a+6],'III',a+1);counts['math_arm_FK_completed']+=1
                current['poses'].append(pose.tolist());new_json(folder/f'node_{i:05d}_arm{a+1}.json',current)
                event('math_arm_FK_completed',node_id=i,arm=a+1,pose=pose.tolist())
            import numpy as np
            poses=[np.asarray(p) for p in current['poses']]
            metric=oracle.matrix_error(poses[1],poses[0]@oracle.grasps_for('III')[0]@oracle.FLIP);limits=oracle.limit_score(q,'III')
            for a in range(2):
                counts['branch_identity_started']+=1
                current['branches'].append(oracle.branch_identity(q[6*a:6*a+6],'III',GATES['branch_zero_relative_epsilon']))
                counts['branch_identity_completed']+=1
            assignments=[{'edge':k,'role':e['active_chain'],'requested_branch':e['branch'],
                'branch_pass':e['branch'] in current['branches'][1-e['active_chain']]['branch_set']}
                for k,e in enumerate(spec['fixed_queue']['edges']) if i in e['node_ids']]
            mathok=(metric['position_max_abs']<=GATES['position_maxabs_mm'] and
                metric['rotation_matrix_max_abs']<=GATES['rotation_matrix_maxabs'] and limits['legal'] and
                bool(assignments) and all(a['branch_pass'] for a in assignments))
            current.update(stage='MATH_COMPLETED',closure=metric,limits=limits,edge_assignments=assignments,math_qualified=bool(mathok))
            new_json(folder/f'node_{i:05d}_math.json',current);event('math_node_completed',node_id=i,math_qualified=bool(mathok))
            budget.remaining();require(counts['collision_calls_started']<spec['max_collision_calls'],'COLLISION_CALL_CAP')
            counts['collision_calls_started']+=1;current['stage']='COLLISION_STARTED';event('collision_started',node_id=i)
            collision=adapter.check_collision('III',q,timeout_s=min(10.,budget.remaining()),manifest_path=COLLISION)
            counts['collision_calls_completed']+=1;current.update(stage='COLLISION_RESPONSE_RETAINED',collision=collision)
            new_json(folder/f'node_{i:05d}_collision_response.json',collision);event('collision_response_retained',node_id=i,response=collision)
            require(collision.get('status')=='CHECKED' and collision.get('selected_variant')=='aligned' and
                collision.get('manifest_sha256')==spec['bound_files_sha256'][COLLISION] and
                type(collision.get('collision')) is bool and set(collision.get('variants',{}))=={'native','aligned'},
                'COLLISION_UNQUALIFIED_RUNTIME')
            for variant,response in collision['variants'].items():
                codes=response.get('query_codes',[]);counts['PQP_queries']+=len(codes)
                require(len(codes)<=spec['pair_counts'][variant]and counts['PQP_queries']<=spec['max_PQP_queries'],'FIXED_III_PQP_QUERY_CAP')
                require(bool(codes) and all(type(v) is int and v==0 for v in codes),'COLLISION_QUERY_ERROR '+variant)
            current.update(stage='COMPLETED',qualified=bool(mathok and not collision['collision']))
            new_json(folder/f'node_{i:05d}.json',current);results.append(current)
            event('node_completed',node_id=i,qualified=current['qualified']);current=None;budget.remaining()
        require([r['node_id']for r in results]==spec['execution_node_ids'],'COMPLETE_FIXED_FULL_QUEUE_REQUIRED')
        record['status']='PASS_DISCRETE_SOURCE_POLICY_III_START_TO_GOAL_PATH'if all(r['qualified']for r in results)else'PATH_REJECTED_BY_INDEPENDENT_QUALIFICATION'
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
        if record['status'].startswith('PASS_')and not worker_gate:record['status']='STOP_WORKER_EOF_EXIT_OR_REGISTRY_UNQUALIFIED'
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
            if folder.is_dir()and budget is not None:
                with FinalIOGuard(budget):
                    record['durable_saved_snapshot']=durable_saved_snapshot(folder,budget)
                    record['retained_run_files_sha256']={str(p.relative_to(ROOT)):sha(p)for p in sorted(folder.rglob('*'))if p.is_file()}
        except BaseException as exc:diagnostic('final_evidence_preservation',exc)
        record.update(counts=dict(counts),wall_s=time.monotonic()-begun,cpu_s=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
            node_count=len(spec['execution_node_ids']),original_full_queue_node_count=len(spec['fixed_queue']['nodes']),completed_nodes=len(results),qualified_nodes=sum(r['qualified']for r in results),
            completed_original_node_ids=[r['node_id']for r in results],uncompleted_node_ids=[i for i in spec['execution_node_ids']if i not in {r['node_id']for r in results}],
            full_queue_checked=[r['node_id']for r in results]==spec['execution_node_ids'],binary_execution_calls=counts['collision_worker_started'],diagnostics=diagnostics)
        if record['wall_s']>=min(120.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(240.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if record['status'].startswith('PASS_')and record.get('durable_saved_snapshot',{}).get('loose_files_byte_exact')is not True:record['status']='STOP_DURABLE_SNAPSHOT_UNQUALIFIED'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_D080_III_RRT_PCS_PHYSICAL01_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(120.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(240.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            with(folder/'cost_receipt.jsonl').open('xb')as stream:stream.write(json.dumps(receipt,allow_nan=False,separators=(',',':')).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
            record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),node_count=record['node_count'],completed_nodes=record['completed_nodes'],qualified_nodes=record['qualified_nodes'],
        external_supervision_qualified=False,independent_saved_POST_required=True,continuous_collision_certificate=False)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status')=='PASS_DISCRETE_SOURCE_POLICY_III_START_TO_GOAL_PATH','III_COMPLETE_PHYSICAL_PATH_DID_NOT_QUALIFY')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args();protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:
        validate(spec,protocol);print('STATIC_III_PHYSICAL_DRAFT_VALIDATED_NO_MODEL_EXECUTION');return
    execute(spec,protocol)

if __name__=='__main__':main()
