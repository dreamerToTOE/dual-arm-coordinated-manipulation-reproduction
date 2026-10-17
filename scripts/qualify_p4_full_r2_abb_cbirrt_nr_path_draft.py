#!/usr/bin/env python3
"""Complete original CBiRRT_NR saved path candidate; no science at import/describe.

Missing real S and personnel-independent POST hard-refuses draft generation.
The physical node loop is the qualified NR393 local worker loop, unchanged.
"""
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
import io
import tarfile
from types import SimpleNamespace
import qualify_p4_full_r2_abb_cbirrt_nr_solve_v3_draft as source_run
import materialize_p4_full_r2_abb_cbirrt_nr_path_draft as saved

old=source_run.old
ROOT=old.ROOT
RUN='20261016_R2_ABB_CBIRRT_NR_PATH01'
CLAIM='P4_R2_ABB_CBIRRT_NR_PATH_FULL2048_120W_240CPU_20261016'
LABEL='R2_RECONSTRUCTED_PHYSICAL_NR_CBIRRT_A01_FULL_DISCRETE_SOURCE_POLICY_PATH'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH_PRE_DRAFT_20261016.md'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_cbirrt_nr_path_draft.py'
SOURCE_DIR='results/p4_full/'+source_run.RUN
SOURCE_EXEC_SHA='bc30019b1e5282817adee945fbb4b86a7bb9f30e6f419a6def0e559815a7b1b6'
SOURCE_POST='reports/P4_FULL_R2_ABB_CBIRRT_NR_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json'
ORIGINAL_NR='scripts/qualify_p4_full_r2_abb_nr_local_draft.py'
ORIGINAL_NR_SHA='6c2e5bad7b0b16c4657e454e04b50195a226ec4779b16e1b7580ba1239772467'
ORIGINAL_NR_PATH='scripts/qualify_p4_full_r2_abb_rrt_nr_path_draft.py'
ORIGINAL_NR_PATH_SHA='2b9ec39b195a8470a00c58cd82788d67543b824c8c2039c6609ef88535801fc8'
ORIGINAL_JSON='scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py'
ORIGINAL_JSON_SHA='a76c67a53690a9e04dcb6fdb087bc65595192d09f69675667ab4ff271d8506e7'
SOURCE_POST_SHA='549d585f1fb2be390b28a0d64dfb90815e58092a9efd7e3c4d478abebe381ef1'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
MAX_NODES=2048
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,'strict_leaf_full12_L2_rad':.05,
    'source_literal_pi_for_mechanical_limits':3.1416,'source_PQP_tolerance_mm':8.,
    'fixed_active_or_branch_gate':False,'continuous_collision_certificate':False}
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),PRE,SUPERVISOR,
    'scripts/materialize_p4_full_r2_abb_cbirrt_nr_path_draft.py',ORIGINAL_NR,ORIGINAL_NR_PATH,ORIGINAL_JSON,
    'scripts/recover_p4_full_r2_endpoints.py','scripts/qualify_p4_full_r2_vi_rss_reconstructed.py',
    'baselines/p4_full/geometry_consistent/collision_adapter.py','baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/abb_independent_oracle.py','baselines/p4_full/analyze_comau_native_qualification.py',
    'baselines/p4_full/geometry_consistent/rss_geometry.py',*source_run.OWN]))
require=old.require
sha=old.sha
load=old.load
path=old.path
exact=old.exact
key=saved.key
durable_new=old.durable_new
# Exact writer used by the qualified NR393 science block: close every file;
# durable completion is the separately verified final uncompressed snapshot.
def new_json(p,value):
    with Path(p).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')

def bind(files,name,want=None):
    name=str(name);actual=sha(name);require(want is None or actual==want,'P_BOUND_HASH_CHANGED '+name);files[name]=actual
    return load(name)if name.endswith('.json')else None

def source_provenance():
    require(path(SOURCE_DIR+'/execution.json').is_file()and path(SOURCE_POST).is_file(),
        'WAIT_ACTUAL_SINGLE_S_AND_PERSONNEL_INDEPENDENT_POST_NO_PLACEHOLDER_QUEUE')
    files={};e=bind(files,SOURCE_DIR+'/execution.json',SOURCE_EXEC_SHA);post=bind(files,SOURCE_POST,SOURCE_POST_SHA)
    require(e['schema']=='P4_R2_ABB_CBIRRT_NR_SOLVE01_EXECUTION_V3'and e['run_id']==source_run.RUN
        and e['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT'and e['source_exact']is True
        and e['source_has_solution']is True and e['source_approximate']is False,
        'ACTUAL_EXACT_NONAPPROXIMATE_SINGLE_S_REQUIRED')
    require(post['schema']=='P4_CBIRRT_NR_SOLVE01_SAVED_INDEPENDENT_POST_V1'
        and post['status']=='PASS_CBIRRT_NR_SOLVE01_TRANSPORT_EVIDENCE_INDEPENDENT_POST'
        and post['personnel_independent']is True and post['external_supervision_qualified']is True
        and post['successful_transport_qualified']is True and post['completed_process_exit0']is True and post['failures']==[]
        and post['checks_total']==post['checks_passed']and post['checks_total']>0 and post['checks_failed']==0
        and post['execution_sha256']==sha(SOURCE_DIR+'/execution.json')
        and post['source_status']==e['status']and post['source_exact']is True and post['source_has_solution']is True
        and post['source_approximate']is False,'S_FULL_ACTUAL_INDEPENDENT_TRANSPORT_AND_EXACT_CONTRACT_REQUIRED')
    require(e['bound_files_sha256']==e['bound_files_after_sha256'],'S_ORIGINAL_BOUND_SET_CHANGED')
    for n,w in e['bound_files_sha256'].items():bind(files,n,w)
    p=bind(files,e['protocol'],e['protocol_sha256']);c=bind(files,e['claim'],e['claim_sha256'])
    require(e['protocol_sha256']==e['protocol_after_sha256']and e['claim_sha256']==e['claim_after_sha256']
        and p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())
        and p['run_id']==source_run.RUN and c['protocol_sha256']==e['protocol_sha256'],'S_FROZEN_PROTOCOL_CLAIM_CHAIN_REQUIRED')
    require(e['complete_source_raw_evidence_gate']is True and len(e['source_process_registry'])==1
        and all(r['reaped']is True and r['returncode']==0 for r in e['source_process_registry'])
        and e['counts']['solve_dispatched']==e['counts']['raw_response_lines_observed']==1,
        'S_ONE_REQUEST_PROCESS_COMPLETE_RAW_EOF_EXIT_REQUIRED')
    require(isinstance(post['retained_sha256'],dict)and post['retained_sha256'],'FULL_S_INDEPENDENT_BINDINGS_REQUIRED')
    for n,w in post['retained_sha256'].items():bind(files,n,w)
    for n,w in e['runtime_mesh_sha256'].items():bind(files,n,w)
    for n,w in e['original_native_output_sha256'].items():bind(files,n,w)
    bind(files,e['evidence_journal'],e['evidence_journal_sha256'])
    rows=[json.loads(line)for line in path(e['evidence_journal']).read_bytes().splitlines()if line.strip()]
    parsed=[r['response']for r in rows if r['event']=='parsed_response_before_gates']
    require(len(parsed)==1,'EXACT_ONE_S_PARSED_RESPONSE_REQUIRED');d=parsed[0]
    stdout=SOURCE_DIR+'/source_stdout.bin';stderr=SOURCE_DIR+'/source_stderr.bin';bind(files,stdout);bind(files,stderr)
    lines=path(stdout).read_bytes().splitlines(keepends=True)
    require(len(lines)==1 and lines[0].endswith(b'\n')and lines[0].startswith(b'{')and exact(json.loads(lines[0]),d),
        'NR_S_EXACT_ONE_ORIGINAL_STDOUT_JSON_RESPONSE_BINARY64_REQUIRED')
    require(exact(source_run.raw_trace(path(stderr).read_bytes()),d['construction']['trace']+d['trace']),
        'S_COMPLETE_ORIGINAL_BODY_TRACE_REQUIRED')
    require(exact(d['request'],p['request'])and d['source_dispatch_started']==d['source_dispatch_completed']==d['solve_calls']==1
        and d['formal_table_I_calls']==0 and d['independent_path_qualified']is False,
        'S_ACTUAL_FIXED_REQUEST_ONE_SOLVE_SCOPE_REQUIRED')
    return d,files,dict(execution=SOURCE_DIR+'/execution.json',execution_sha256=sha(SOURCE_DIR+'/execution.json'),
        independent_POST=SOURCE_POST,independent_POST_sha256=sha(SOURCE_POST),protocol=e['protocol'],claim=e['claim'],
        source_commit=e['source_commit'],request=p['request'],source_status=e['status'],
        scope='Native exact remains pending independently qualified complete discrete source-policy path.')

def current_prior():
    ledgers=list((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers,'WAIT_ACTUAL_CURRENT_AUTHORITATIVE_LEDGER');ledger=max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1]));value=load(ledger)
    actual={str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if p.parent.name!=RUN}
    require({r['execution']:r['execution_sha256']for r in value['executions']}==actual,'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS')
    wall=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in value['executions'])
    cpu=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in value['executions'])
    require(all(math.isfinite(v)and v>=0 for v in(wall,cpu))and wall==value['conservative_r2_sum_wall_s']
        and cpu==value['conservative_r2_sum_cpu_s'],'EXACT_PRIOR_CHARGE_SUMS_REQUIRED')
    for r in value['executions']:
        if 'charged_wall_s'not in r:continue
        post=load(r['external_post'])
        require(sha(r['external_post'])==r['external_post_sha256']and post['personnel_independent']is True
            and post['external_supervision_qualified']is True and post['checks_total']==post['checks_passed']and post['checks_failed']==0
            and post['execution_sha256']==r['execution_sha256']and post['upper_wall_s']==r['charged_wall_s']and post['upper_cpu_s']==r['charged_cpu_s']
            and sha(r['external_time'])==r['external_time_sha256']==post['external_time_sha256'],'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED')
    for charge in(ROOT/'results/p4_full').glob('*_R2_*.supervision.charge.json'):
        run=charge.name.removesuffix('.supervision.charge.json')
        if run!=RUN:require((charge.parent/run/'execution.json').is_file(),'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING '+run)
    return dict(ledger=str(ledger.relative_to(ROOT)),ledger_sha256=sha(ledger),execution_sha256=actual,
        wall_s=wall,cpu_s=cpu,historical_unmeasured_tail='RETAINED_UNKNOWN; CHARGED_REMAINING_IS_UPPER_BOUND')

def draft_protocol():
    d,files,provenance=source_provenance();queue=saved.materialize(d,provenance['request']);prior=current_prior()
    require(sha(ORIGINAL_NR)==ORIGINAL_NR_SHA and sha(ORIGINAL_NR_PATH)==ORIGINAL_NR_PATH_SHA and sha(ORIGINAL_JSON)==ORIGINAL_JSON_SHA,'QUALIFIED_NR393_SCIENTIFIC_LOOP_SOURCE_CHANGED')
    require(queue['full_queue_node_count']==689 and queue['full_dense_leaf_count']==688 and queue['full_dense_node_reference_count']==699
        and queue['source_milestone_count']==12 and queue['source_attempt_count']==11
        and queue['source_identity_audit']['complete_tree_motion_count']==16
        and queue['source_identity_audit']['source_bridge_milestone_edge_index']==2
        and queue['source_identity_audit']['source_motion_path']==[2,15,16,14,11,10,9,8,7,6,4,3],
        'EXACT_ACTUAL_NR_SOURCE_FULL_QUEUE_AND_IDENTITY_REQUIRED')
    manifest=bind(files,COLLISION);entries=[r for r in manifest['entries']if r['model']=='abb']
    require(sorted(r['variant']for r in entries)==['aligned','native'],'EXACT_V3_ABB_NATIVE_ALIGNED_REQUIRED')
    for entry in entries:
        require(entry['exit_code']==0,'V3_COLLISION_BUILD_REQUIRED');bind(files,entry['binary'],entry['binary_sha256'])
        for n,w in entry['source_files_sha256'].items():bind(files,str(Path(entry['source_root'])/n),w)
        for n,w in entry['mesh_sha256'].items():bind(files,str(Path(entry['cwd'])/'simulator'/n),w)
    for n in OWN:bind(files,n)
    bind(files,prior['ledger'],prior['ledger_sha256'])
    for n,w in prior['execution_sha256'].items():bind(files,n,w)
    bind(files,'/usr/bin/time');bind(files,'/usr/bin/python3');n=min(len(queue['nodes']),MAX_NODES)
    return dict(schema='P4_R2_ABB_CBIRRT_NR_PATH_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_complete_queue_freeze_approved=False,latest_actual_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,source_provenance=provenance,fixed_queue=queue,
        bound_files_sha256=files,own_source_sha256={n:sha(n)for n in OWN},actual_charge_prior=prior,
        prior_execution_sha256=prior['execution_sha256'],previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],
        budget=dict(wall_s=120.,cpu_s=240.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),gates=GATES,
        max_nodes_per_execution=MAX_NODES,full_queue_node_count=len(queue['nodes']),
        max_math_arm_FK_J=2*n,max_collision_calls=n,max_adapter_arm_FK_J=4*n,
        zero_calls=dict(IK=0,NR=0,projection=0,RBS=0,solve=0,RNG=0,VI_constructions=0,formal_table_I=0),
        external_supervision=dict(required=True,sibling_path='results/p4_full/'+RUN+'.supervision.time.txt',format='%e %U %S %x',
            metadata_path='results/p4_full/'+RUN+'.supervision.jsonl',stderr_path='results/p4_full/'+RUN+'.supervision.stderr.log',
            charge_path='results/p4_full/'+RUN+'.supervision.charge.json',time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'),
            elapsed_decimal_upper_padding_s=.01,CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True),
        collision_manifest=COLLISION,scope='All original NR dense M, independent closure/original limits/v3 aligned discrete source collision; native separately. No fixed passive or analytic identity gate, continuous collision, original KDL equivalence or statistical claim.',
        persistence_policy='Exact NR393 immediate-close JSON; complete live append journal. Exclusive final uncompressed tar/member-SHA, fsync archive+directory, full loose/member bytes verified within absolute budget guard. Partial archive remains STOP, never resume.',
        resource_policy='Complete unique original queue, at most2048; above cap blocks science without truncation. No second source solve or RBS, no node replacement, retry/reset/resume.',
        no_retry_reset_resume=True)

def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_FULL_CBIRRT_SAVED_QUEUE_AND_PRIOR_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_P_REVIEW_FIELDS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'P_INDEPENDENT_REVIEW_ROOT_COMPLETE_QUEUE_FREEZE_REQUIRED')
    require(spec['fixed_queue']['all_edges_structural_qualified']is True and spec['full_queue_node_count']<=MAX_NODES and spec['fixed_queue']['under_2048_full_queue_cap']is True,'COMPLETE_QUEUE_OVER2048_NO_PHYSICAL_QUERY')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for n in[*OWN,str(protocol.relative_to(ROOT))]:
        require(subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)==path(n).read_bytes(),'UNCOMMITTED_P_SOURCE_OR_PROTOCOL '+n)
    return commit

class Budget(old.Budget):
    def __init__(self,spec,begun,cpu_start):
        super().__init__(spec,begun,cpu_start)
        self.wall_cap=min(120.,3600.-spec['previous_r2_wall_s']);self.cpu_cap=min(240.,7200.-spec['previous_r2_cpu_s'])
        require(min(self.wall_cap,self.cpu_cap)>0,'P_TOTAL_BUDGET_EXHAUSTED')

# Actual parent/argv/exclusive time-inode proof has the same function body as S;
# its globals resolve to this independently versioned P runner/supervisor.
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
    require(not old.builder.active_p4(),'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    budget=None;journal=None;physical_nr=None;adapter=None;original=None;adapter_process_api=None
    diagnostics=[];results=[];counts=Counter();current=None;error=None;worker_evidence=[]
    record=dict(schema='P4_R2_ABB_CBIRRT_NR_PATH_EXECUTION_V1',run_id=RUN,classification=LABEL,
        status='STOP_SETUP_PREFIX_RETAINED',source_commit=commit,protocol=str(protocol.relative_to(ROOT)),
        protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),budget=spec['budget'],
        source_provenance=spec['source_provenance'],bound_files_sha256=spec['bound_files_sha256'],
        prior_execution_sha256=spec['prior_execution_sha256'],actual_charge_prior=spec['actual_charge_prior'],
        previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],
        supervisor_launch_proof=launch,external_supervision_qualified=False,independent_saved_POST_required=True,
        independent_path_qualified=False,continuous_collision_certificate=False,
        zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0)
    def event(kind,**values):
        if journal is not None:journal.add(kind,**values)
    def diagnostic(stage,exc):diagnostics.append(dict(stage=stage,error=repr(exc)))
    try:
        durable_new(claim,dict(schema='P4_R2_ABB_CBIRRT_NR_PATH_CLAIM_V1',run_id=RUN,
            protocol=record['protocol'],protocol_sha256=record['protocol_sha256'],source_commit=commit,
            budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=source_run.tail.Journal(folder/'events.jsonl')
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
        # from the already qualified NR393 local worker, without changing
        # its FK/closure/limits/collision predicates or node order.
        def counted(q,env,arm):
            counts['adapter_arm_FK_J_started']+=1;event('adapter_arm_FK_J_started',node_id=current['node_id'],environment=env,arm=arm)
            value=original(q,env,arm);counts['adapter_arm_FK_J_completed']+=1
            event('adapter_arm_FK_J_completed',node_id=current['node_id'],environment=env,arm=arm);return value
        physical_nr.arm_fk_jac=counted
        queue=spec['fixed_queue']['nodes']
        request=dict(wall_remaining_s=budget.remaining(),worker_monotonic_start=time.monotonic())
        for source in queue:
            current={**source,'poses':[],'stage':'STARTED'};env=source['environment'];q=source['q12']
            for arm in (1,2):
                counts['math_arm_FK_started']+=1;event('math_arm_FK_started',node_id=source['node_id'],environment=env,arm=arm)
                pose=oracle.arm_fk(q[6*(arm-1):6*arm],env,arm);current['poses'].append(pose.tolist())
                counts['math_arm_FK_completed']+=1
                new_json(folder/f'node_{source["node_id"]:05d}_arm{arm}.json',current)
                event('math_arm_FK_completed',node_id=source['node_id'],environment=env,arm=arm)
            import numpy as np
            poses=[np.asarray(p)for p in current['poses']]
            residual=oracle.matrix_error(poses[1],poses[0]@oracle.grasps_for(env)[0]@oracle.FLIP)
            limits=oracle.limit_score(q,env);closed=residual['position_max_abs']<=1e-5 and residual['rotation_matrix_max_abs']<=1e-5
            current.update(stage='MATH_COMPLETED',closure=residual,limits=limits,
                math_qualified=bool(closed and limits['legal']))
            new_json(folder/f'node_{source["node_id"]:05d}_math.json',current)
            if source['collision_required']:
                counts['collision_calls_started']+=1;event('collision_started',node_id=source['node_id'])
                collision=adapter.check_collision(env,q,timeout_s=min(10.,max(.001,request['wall_remaining_s']-(time.monotonic()-request['worker_monotonic_start']))),
                    manifest_path=spec['collision_manifest'])
                counts['collision_calls_completed']+=1;current.update(stage='COLLISION_RAW_RETAINED',collision=collision)
                new_json(folder/f'node_{source["node_id"]:05d}_collision_raw.json',collision)
                query_counts={variant:len(row.get('query_codes',[]))for variant,row in collision.get('variants',{}).items()}
                counts['PQP_queries']+=sum(query_counts.values())
                event('collision_completed',node_id=source['node_id'],status=collision.get('status'),
                    variant_query_counts=query_counts,PQP_queries=sum(query_counts.values()))
                require(collision.get('status')=='CHECKED' and collision.get('selected_variant')=='aligned' and
                    type(collision.get('collision'))is bool and collision.get('manifest_sha256')==spec['bound_files_sha256'][COLLISION] and
                    list(collision.get('variants',{}))==['native','aligned'],'COLLISION_RUNTIME_OR_PROVENANCE')
                for variant,row in collision['variants'].items():
                    codes=row.get('query_codes',[])
                    require(codes and all(type(code)is int and code==0 for code in codes),'PQP_QUERY_ERROR '+variant)
                require(collision['variants']['aligned']['pose_consistency']['passed']is True,'ALIGNED_TCP_MISMATCH')
                current['node_qualified']=bool(current['math_qualified'] and not collision['collision'])
            else:current['node_qualified']=None
            current['stage']='COMPLETED';new_json(folder/f'node_{source["node_id"]:05d}.json',current)
            print('P4_NR_NODE_RESPONSE '+json.dumps({'node_id':source['node_id'],'result':current,
                'observed_counts':dict(counts)},allow_nan=False),flush=True);current=None
        results=[load(folder/f'node_{i:05d}.json')for i in range(len(queue))]
        require(len(results)==len(queue)and [r['node_id']for r in results]==list(range(len(queue))),'COMPLETE_FULL_NR_QUEUE_REQUIRED')
        require(counts['math_arm_FK_started']==counts['math_arm_FK_completed']==2*len(queue)
            and counts['collision_calls_started']==counts['collision_calls_completed']==len(queue)
            and counts['adapter_arm_FK_J_started']==counts['adapter_arm_FK_J_completed']==4*len(queue),
            'EXACT_ACTUAL_NR393_SCIENTIFIC_COUNTS_REQUIRED')
        record['status']='PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH'if all(r['node_qualified']for r in results)else'PATH_REJECTED_BY_INDEPENDENT_QUALIFICATION'
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
        try:results=[load(p)for p in sorted(folder.glob('node_[0-9][0-9][0-9][0-9][0-9].json'))]
        except BaseException as exc:diagnostic('retained_completed_nr_prefix',exc)
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
            with FinalIOGuard(budget):
                try:
                    after={n:sha(n)for n in spec['bound_files_sha256']};record['bound_files_after_sha256']=after
                    require(after==spec['bound_files_sha256'],'P_BOUND_ASSET_CHANGED')
                    record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
                    require(record['protocol_after_sha256']==record['protocol_sha256']and record['claim_after_sha256']==record.get('claim_sha256'),'P_PROTOCOL_OR_CLAIM_CHANGED')
                    latest=current_prior();record['prior_execution_after_sha256']=latest['execution_sha256']
                    require(latest==spec['actual_charge_prior'],'P_PRIOR_CHARGED_LEDGER_CHANGED')
                except BaseException as exc:diagnostic('mandatory_final_hashes',exc)
                try:
                    if journal is not None:
                        event('final_counts',counts=dict(counts),diagnostics=diagnostics);journal.finish()
                        record['events']=str((folder/'events.jsonl').relative_to(ROOT));record['events_sha256']=sha(folder/'events.jsonl')
                    if folder.is_dir():
                        record['durable_saved_snapshot']=durable_saved_snapshot(folder,budget)
                        record['retained_run_files_sha256']={str(p.relative_to(ROOT)):sha(p)for p in sorted(folder.rglob('*'))if p.is_file()}
                        budget.check()
                except BaseException as exc:diagnostic('final_evidence_preservation',exc)
        except BaseException as exc:diagnostic('absolute_budget_final_io_boundary',exc)
        record.update(counts=dict(counts),wall_s=time.monotonic()-begun,cpu_s=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
            node_count=len(spec['fixed_queue']['nodes']),completed_nodes=len(results),qualified_nodes=sum(r['node_qualified']for r in results),
            uncompleted_node_ids=list(range(len(results),len(spec['fixed_queue']['nodes']))),full_queue_checked=len(results)==len(spec['fixed_queue']['nodes']),diagnostics=diagnostics)
        if record['wall_s']>=min(120.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(240.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if record['status'].startswith('PASS_')and record.get('durable_saved_snapshot',{}).get('loose_files_byte_exact')is not True:record['status']='STOP_DURABLE_SNAPSHOT_UNQUALIFIED'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_R2_ABB_CBIRRT_NR_PATH_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(120.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(240.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            with(folder/'cost_receipt.jsonl').open('xb')as stream:stream.write(json.dumps(receipt,allow_nan=False,separators=(',',':')).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
            record['terminal_receipt_status']=receipt['status']
            directory=os.open(folder,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(directory)
            finally:os.close(directory)
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),node_count=record['node_count'],completed_nodes=record['completed_nodes'],qualified_nodes=record['qualified_nodes'],
        external_supervision_qualified=False,independent_saved_POST_required=True,continuous_collision_certificate=False)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status')=='PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH','P_FULL_DISCRETE_PATH_NOT_QUALIFIED')

def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_P_DRAFT_VALIDATED_NO_EXECUTION');return
    execute(spec,protocol)

if __name__=='__main__':main()
