#!/usr/bin/env python3
"""Original SBL saved tail262..386 candidate; no science at import/describe.

Missing real S and personnel-independent POST hard-refuses draft generation.
The physical node loop is the original qualified PCS path loop, unchanged.
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
from types import SimpleNamespace
import qualify_p4_full_r2_abb_cbirrt_d_path_draft as path_reuse
import qualify_p4_full_r2_abb_sbl_pcs_solve_shadow_v2_draft as source
import materialize_p4_full_r2_abb_sbl_pcs_path_draft as saved

old=path_reuse.old
ROOT=old.ROOT
RUN='20261018_R2_ABB_SBL_PCS_PATH_TAIL02'
CLAIM='P4_R2_ABB_SBL_PCS_PATH_TAIL02_262_TO386_90W_180CPU_20261018'
LABEL='R2_CORRECTED_SBL_PCS_RECONSTRUCTED_A01_SAVED_PREFIX_PLUS_ORIGINAL_TAIL'
PRE='reports/P4_FULL_R2_ABB_SBL_PCS_PATH_TAIL02_PRE_DRAFT_20261018.md'
MATERIALIZER_PRE=PRE
SUPERVISOR='scripts/supervise_p4_full_r2_abb_sbl_pcs_path_tail02_draft.py'
SOURCE_DIR='results/p4_full/'+source.RUN
SOURCE_EXEC_SHA='2867a03699b8901c9e065bbcc1993a9ac14a7f624232f29ed603df89c1d09208'
SOURCE_POST='reports/P4_FULL_R2_ABB_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST_20261017.json'
SOURCE_POST_SHA='fea6f01839a041430d10da796a0c7a59bd65dbf4bcf7487dc8c27a7c15358066'
D080='configs/p4_d080/execution_scope_v1.json'
PREFIX_DIR='results/p4_full/20261018_R2_ABB_SBL_PCS_PATH01'
PREFIX_EXEC_SHA='cee39aae1538742e1ab54e19d28ff42a8de2c4165cf2511bb1477d69847bc1e0'
PREFIX_POST='reports/P4_FULL_R2_ABB_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json'
PREFIX_POST_SHA='e2fb37a5d63e5219395baedef7630c386893ea13aa07e9bcc0777aa8316b75b4'
EXECUTION_NODE_IDS=list(range(262,387))
ORIGINAL_PCS='scripts/qualify_p4_full_r2_abb_rrt_path.py'
ORIGINAL_PCS_SHA='bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
MAX_NODES=2048
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
    'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon}
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),PRE,MATERIALIZER_PRE,SUPERVISOR,
    'scripts/materialize_p4_full_r2_abb_sbl_pcs_path_draft.py',
    'scripts/materialize_p4_full_r2_abb_cbirrt_d_path_draft.py',
    'scripts/qualify_p4_full_r2_abb_cbirrt_d_path_draft.py',
    'scripts/qualify_p4_full_r2_abb_sbl_pcs_path_draft.py',D080,ORIGINAL_PCS,
    'scripts/recover_p4_full_r2_endpoints.py','scripts/qualify_p4_full_r2_vi_rss_reconstructed.py',
    'baselines/p4_full/geometry_consistent/collision_adapter.py','baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/abb_independent_oracle.py','baselines/p4_full/analyze_comau_native_qualification.py',
    'baselines/p4_full/geometry_consistent/rss_geometry.py',*path_reuse.OWN,*source.OWN]))
require=old.require
sha=old.sha
load=old.load
path=old.path
exact=old.exact
key=saved.key
durable_new=old.durable_new

def bind(files,name,want=None):
    name=str(name);actual=sha(name)
    if want is not None and actual!=want and path(name)==Path('/etc/ld.so.cache'):
        # The sole allowed historical metadata drift: independently timestamped
        # package cache update AFTER PATH01 completed. Never waive library,
        # source, runtime mesh, input, or threshold byte identity.
        require(sha(PREFIX_POST)==PREFIX_POST_SHA,'EXACT_INDEPENDENT_PREFIX_ADDENDUM_REQUIRED')
        evidence=load(PREFIX_POST)['post_run_loader_cache_drift']
        require(evidence['path']=='/etc/ld.so.cache'and evidence['historical_sha256']==want
            and evidence['current_sha256']==actual and evidence['execution_after_matches_historical']is True
            and bool(evidence['mtime_UTC'])and bool(evidence['dpkg_evidence']),
            'ONLY_INDEPENDENT_POST_RUN_LDSO_CACHE_METADATA_DRIFT_ALLOWED')
    else:require(want is None or actual==want,'P_BOUND_HASH_CHANGED '+name)
    files[name]=actual
    return load(name)if name.endswith('.json')else None

def source_provenance():
    files={};e=bind(files,SOURCE_DIR+'/execution.json',SOURCE_EXEC_SHA);post=bind(files,SOURCE_POST,SOURCE_POST_SHA)
    require(e['schema']=='P4_R2_ABB_SBL_PCS_SOLVE01_EXECUTION_V1'and e['run_id']==source.RUN
        and e['status']=='SOURCE_SINGLE_SOLVE_OBSERVED_PENDING_INDEPENDENT_POST','ACTUAL_SBL_SINGLE_SOLVE_REQUIRED')
    require(post['schema']=='P4_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST_V1'
        and post['status']=='PASS_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST'and post['personnel_independent']is True
        and post['solve_transport_qualified']is True and post['external_supervision_qualified']is True
        and post['checks_total']==post['checks_passed']==111 and post['checks_failed']==0
        and post['execution_sha256']==SOURCE_EXEC_SHA and post['independent_path_qualified']is False,
        'SBL_ACTUAL_INDEPENDENT_TRANSPORT_POST_REQUIRED')
    require(e['bound_files_sha256']==e['bound_files_after_sha256'],'SBL_SOURCE_BOUND_SET_CHANGED')
    for n,w in e['bound_files_sha256'].items():bind(files,n,w)
    p=bind(files,e['protocol'],e['protocol_sha256']);c=bind(files,e['claim'],e['claim_sha256'])
    require(e['protocol_sha256']==e['protocol_after_sha256']and e['claim_sha256']==e['claim_after_sha256']
        and p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())
        and p['run_id']==source.RUN and c['protocol_sha256']==e['protocol_sha256'],'SBL_FROZEN_PROTOCOL_AND_CLAIM_REQUIRED')
    require(e['complete_source_raw_evidence_gate']is True and len(e['source_process_registry'])==1
        and all(r['returncode']==0 and r['actual_after_reap_group']==[]and r['actual_pipe_EOF_observed']=={'stdout':True,'stderr':True}for r in e['source_process_registry'])
        and e['solve_calls']==e['binary_execution_calls']==1 and e['local_calls']==e['public_project_calls']==0,
        'SBL_SINGLE_REQUEST_COMPLETE_EXIT_REQUIRED')
    for n,w in post['retained_sha256'].items():bind(files,n,w)
    for n,w in e['runtime_mesh_sha256'].items():bind(files,n,w)
    for n,w in e['retained_run_files_sha256'].items():bind(files,n,w)
    journal=SOURCE_DIR+'/evidence.jsonl';bind(files,journal,e['evidence_journal_sha256'])
    rows=[json.loads(line)for line in path(journal).read_bytes().splitlines()if line.strip()]
    parsed=[r['response']for r in rows if r['event']=='parsed_response_before_gates']
    require(len(parsed)==len(e['responses'])==1 and exact(parsed[0],e['responses'][0]),'EXACT_ONE_SBL_SAVED_RESPONSE_REQUIRED');d=e['responses'][0]
    stdout=SOURCE_DIR+'/request_00_stdout.bin';stderr=SOURCE_DIR+'/request_00_stderr.bin';bind(files,stdout);bind(files,stderr)
    lines=path(stdout).read_bytes().splitlines(keepends=True)
    require(len(lines)==1 and lines[0].endswith(b'\n')and exact(json.loads(lines[0]),d),'ORIGINAL_SBL_STDOUT_RESPONSE_REQUIRED')
    require(exact(source.L.raw_trace(path(stderr).read_bytes()),d['trace']),'COMPLETE_ORIGINAL_SBL_TRACE_REQUIRED')
    require(exact(d['request'],p['schedule'][0]['request'])and d['source_dispatch_started']==d['source_dispatch_completed']==d['solve_calls']==1
        and d['formal_table_I_calls']==0 and d['new_VI_candidate_constructions']==0 and d['independent_path_qualified']is False
        and d['exact']is True and d['solution_count']==1,'FIXED_SBL_EXACT_SINGLE_SOLVE_SCOPE_REQUIRED')
    for row in d['native_file_evidence']:
        if not row['exists']:continue
        require(row['readback_bytes_saved']is True and row['original_final_bytes_readable']is True,'SBL_NATIVE_FINAL_BYTES_REQUIRED')
        bind(files,row['saved_path']);bind(files,row['original_path'])
        raw=bytes.fromhex(row['bytes_hex']);require(path(row['saved_path']).read_bytes()==path(row['original_path']).read_bytes()==raw
            and len(raw)==row['bytes'],'SBL_ORIGINAL_NATIVE_FILE_BYTES_CHANGED')
    return d,files,dict(execution=SOURCE_DIR+'/execution.json',execution_sha256=SOURCE_EXEC_SHA,
        independent_POST=SOURCE_POST,independent_POST_sha256=SOURCE_POST_SHA,protocol=e['protocol'],claim=e['claim'],
        source_commit=e['source_commit'],request=d['request'],source_status=e['status'],
        scope='Reuse actual independent transport111; source EXACT remains pending complete independent discrete physical path.')

def current_prior():
    ledgers=list((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers,'WAIT_CURRENT_AUTHORITATIVE_CHARGED_LEDGER')
    ledger=max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1]));value=load(ledger)
    actual={str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if p.parent.name!=RUN}
    require({r['execution']:r['execution_sha256']for r in value['executions']}==actual,'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS')
    wall=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in value['executions']);used=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in value['executions'])
    require(all(math.isfinite(v)and v>=0 for v in(wall,used))and wall==value['conservative_r2_sum_wall_s']and used==value['conservative_r2_sum_cpu_s'],'EXACT_PRIOR_CHARGE_SUMS_REQUIRED')
    for row in value['executions']:
        if 'charged_wall_s'not in row:continue
        post=load(path(row['external_post']))
        require(sha(path(row['external_post']))==row['external_post_sha256']and post['personnel_independent']is True
            and post['external_supervision_qualified']is True and post['checks_total']==post['checks_passed']and post['checks_failed']==0
            and post['execution_sha256']==row['execution_sha256']and post['upper_wall_s']==row['charged_wall_s']and post['upper_cpu_s']==row['charged_cpu_s']
            and sha(path(row['external_time']))==row['external_time_sha256']==post['external_time_sha256'],'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED')
    # An attempted supervised preflight is a real cost, even without execution.
    # No next run may silently skip such an orphan while forming the prior.
    for charge in(ROOT/'results/p4_full').glob('*_R2_*.supervision.charge.json'):
        run=charge.name.removesuffix('.supervision.charge.json')
        if run!=RUN:require((charge.parent/run/'execution.json').is_file(),'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING '+run)
    return dict(ledger=str(ledger.relative_to(ROOT)),ledger_sha256=sha(ledger),execution_sha256=actual,wall_s=wall,cpu_s=used,
        historical_unmeasured_tail='RETAINED_UNKNOWN; CHARGED_REMAINING_IS_UPPER_BOUND')

def prefix_provenance(queue,files):
    require(path(PREFIX_POST).is_file(),'WAIT_ACTUAL_INDEPENDENT_SAVED_262_PREFIX_POST')
    post=bind(files,PREFIX_POST,PREFIX_POST_SHA);e=bind(files,PREFIX_DIR+'/execution.json',PREFIX_EXEC_SHA)
    require(post['schema']=='P4_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_ADDENDUM_V1'
        and post['personnel_independent']is True and post['saved_prefix_qualified']is True and post['partial_path_prefix_qualified']is True
        and post['independent_prefix_node_ids']==post['independently_saved_qualified_node_ids']==list(range(262))and post['independently_saved_qualified_nodes']==262
        and post['remaining_unverified_node_ids']==EXECUTION_NODE_IDS and post['independent_path_qualified']is False
        and post['checks_total']==post['checks_passed']and post['checks_total']>0 and post['checks_failed']==0
        and post['execution_sha256']==PREFIX_EXEC_SHA,'INDEPENDENT_FULL_SAVED_262_PREFIX_QUALIFICATION_REQUIRED')
    require(e['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET'and e['completed_nodes']==261 and e['node_count']==387
        and e['counts']['collision_calls_completed']==262 and e['diagnostics']==[],
        'ORIGINAL_PATH01_STOP_MUST_REMAIN_UNCHANGED')
    original=bind(files,e['protocol'],e['protocol_sha256']);bind(files,e['claim'],e['claim_sha256'])
    original_queue=bind(files,PREFIX_DIR+'/complete_original_saved_queue.json',post['source_full_queue_sha256'])
    require(original_queue==queue and original['fixed_queue']==queue and original['full_queue_node_count']==387,
        'TAIL_MUST_USE_ENTIRE_ORIGINAL_UNMODIFIED_QUEUE')
    require(post['retained_sha256'],'INDEPENDENT_PREFIX_ALL_SAVED_ASSETS_REQUIRED')
    for name,want in post['retained_sha256'].items():bind(files,name,want)
    return dict(execution=PREFIX_DIR+'/execution.json',execution_sha256=PREFIX_EXEC_SHA,independent_POST=PREFIX_POST,
        independent_POST_sha256=sha(PREFIX_POST),independently_saved_qualified_node_ids=list(range(262)),
        historical_loader_cache_drift=post['post_run_loader_cache_drift'],new_cache_bound_as_current_input=True,
        remaining_unverified_node_ids=EXECUTION_NODE_IDS,original_stop_retained=True,
        source_full_queue_protocol=e['protocol'],source_full_queue_protocol_sha256=e['protocol_sha256'],
        new_physical_queries_for_prefix=0)

def draft_protocol():
    d,files,provenance=source_provenance();queue=saved.materialize(d,provenance['request']);prefix=prefix_provenance(queue,files);prior=current_prior()
    require(sha(ORIGINAL_PCS)==ORIGINAL_PCS_SHA,'QUALIFIED_PCS_PHYSICAL_LOOP_SOURCE_CHANGED')
    scope=bind(files,D080);require(scope['allowed_environments']==['I','II','III','IV','V']and scope['VI_future_science_authorized']is False
        and scope['formal_table_I_D080']==18000 and scope['formal_execution_authorized']is False,'D080_SCOPE_REQUIRED')
    manifest=bind(files,COLLISION);entries=[r for r in manifest['entries']if r['model']=='abb']
    require(sorted(r['variant']for r in entries)==['aligned','native'],'EXACT_V3_ABB_NATIVE_ALIGNED_REQUIRED')
    for entry in entries:
        require(entry['exit_code']==0,'V3_COLLISION_BUILD_REQUIRED');bind(files,entry['binary'],entry['binary_sha256'])
        for n,w in entry['source_files_sha256'].items():bind(files,str(Path(entry['source_root'])/n),w)
        for n,w in entry['mesh_sha256'].items():bind(files,str(Path(entry['cwd'])/'simulator'/n),w)
    for n in OWN:bind(files,n)
    bind(files,prior['ledger'],prior['ledger_sha256'])
    for n,w in prior['execution_sha256'].items():bind(files,n,w)
    bind(files,'/usr/bin/time');bind(files,'/usr/bin/python3');n=len(EXECUTION_NODE_IDS);require(len(queue['nodes'])==387 and n==125,'FIXED_COMPLETE_SOURCE_AND_125_TAIL_REQUIRED')
    return dict(schema='P4_R2_ABB_SBL_PCS_PATH_TAIL02_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_complete_queue_freeze_approved=False,latest_actual_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,source_provenance=provenance,prefix_provenance=prefix,fixed_queue=queue,
        execution_node_ids=EXECUTION_NODE_IDS,execution_node_count=125,
        D080_scope=dict(path=D080,sha256=sha(D080),formal_table_I_original=22500,formal_table_I_D080=18000,formal_calls=0,VI_new_calls=0),
        bound_files_sha256=files,own_source_sha256={n:sha(n)for n in OWN},actual_charge_prior=prior,
        prior_execution_sha256=prior['execution_sha256'],previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],
        budget=dict(wall_s=90.,cpu_s=180.,work_wall_s=80.,work_cpu_s=160.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),gates=GATES,
        max_nodes_per_execution=MAX_NODES,full_queue_node_count=len(queue['nodes']),
        max_math_arm_FK=2*n,max_collision_calls=n,max_adapter_internal_arm_FK_J=4*n,
        zero_calls=dict(IK=0,NR=0,projection=0,RBS=0,solve=0,RNG=0,VI_constructions=0,formal_table_I=0),
        external_supervision=dict(required=True,sibling_path='results/p4_full/'+RUN+'.supervision.time.txt',format='%e %U %S %x',
            metadata_path='results/p4_full/'+RUN+'.supervision.jsonl',stderr_path='results/p4_full/'+RUN+'.supervision.stderr.log',
            charge_path='results/p4_full/'+RUN+'.supervision.charge.json',time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'),
            elapsed_decimal_upper_padding_s=.01,CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True,
            charge_basis='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE',
            arithmetic='Exact Decimal maximum, converted once to float; original clock observations retained separately',
            conservative_wall_charge='max(GNUtime_elapsed+.01, outer_monotonic_wait+.01, internal_receipt_monotonic+.01)',
            conservative_CPU_charge='max(GNUtime_user_system+.02, outer_reaped_children+.02, internal_receipt_CPU+.02)'),
        scope='Only original node_ids262..386; prefix0..261 reused from independent saved POST. Full original true dense M remains immutable: original math closure/limits/per-edge passive branch and v3 aligned discrete source collision; native kept separately. No CCD/solid-rod/omitted-pair/PCS-advantage claim.',
        resource_policy='Complete387 queue preserved; execute only fixed original125 tail ids262..386. No prefix query, second solve/RBS, node replacement or tail retry/reset/resume.',
        no_retry_reset_resume=True)

def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_FULL_SBL_SAVED_QUEUE_AND_PRIOR_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_P_REVIEW_FIELDS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'P_INDEPENDENT_REVIEW_ROOT_COMPLETE_QUEUE_FREEZE_REQUIRED')
    require(spec['full_queue_node_count']<=MAX_NODES and spec['fixed_queue']['under_2048_full_queue_cap']is True,'COMPLETE_QUEUE_OVER2048_NO_PHYSICAL_QUERY')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for n in[*OWN,str(protocol.relative_to(ROOT))]:
        require(subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)==path(n).read_bytes(),'UNCOMMITTED_P_SOURCE_OR_PROTOCOL '+n)
    return commit

class Budget(old.Budget):
    def __init__(self,spec,begun,cpu_start):
        super().__init__(spec,begun,cpu_start)
        self.wall_cap=min(80.,3600.-spec['previous_r2_wall_s']-10.);self.cpu_cap=min(160.,7200.-spec['previous_r2_cpu_s']-20.)
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
    record=dict(schema='P4_R2_ABB_SBL_PCS_PATH_TAIL02_EXECUTION_V1',run_id=RUN,classification=LABEL,
        status='STOP_SETUP_PREFIX_RETAINED',source_commit=commit,protocol=str(protocol.relative_to(ROOT)),
        protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),budget=spec['budget'],
        source_provenance=spec['source_provenance'],prefix_provenance=spec['prefix_provenance'],execution_node_ids=spec['execution_node_ids'],bound_files_sha256=spec['bound_files_sha256'],
        prior_execution_sha256=spec['prior_execution_sha256'],actual_charge_prior=spec['actual_charge_prior'],
        previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],
        supervisor_launch_proof=launch,external_supervision_qualified=False,independent_saved_POST_required=True,
        independent_path_qualified=False,continuous_collision_certificate=False,
        zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0)
    def event(kind,**values):
        if journal is not None:journal.add(kind,**values)
    def diagnostic(stage,exc):diagnostics.append(dict(stage=stage,error=repr(exc)))
    try:
        durable_new(claim,dict(schema='P4_R2_ABB_SBL_PCS_PATH_TAIL02_CLAIM_V1',run_id=RUN,
            protocol=record['protocol'],protocol_sha256=record['protocol_sha256'],source_commit=commit,
            budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=source.L.Journal(folder/'events.jsonl')
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
                    resource.setrlimit(resource.RLIMIT_CPU,(180,180))
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
                pose=oracle.arm_fk(q[6*a:6*a+6],'II',a+1);counts['math_arm_FK_completed']+=1
                current['poses'].append(pose.tolist());durable_new(folder/f'node_{i:05d}_arm{a+1}.json',current)
                event('math_arm_FK_completed',node_id=i,arm=a+1,pose=pose.tolist())
            import numpy as np
            poses=[np.asarray(p) for p in current['poses']]
            metric=oracle.matrix_error(poses[1],poses[0]@oracle.grasps_for('II')[0]@oracle.FLIP);limits=oracle.limit_score(q,'II')
            for a in range(2):
                counts['branch_identity_started']+=1
                current['branches'].append(oracle.branch_identity(q[6*a:6*a+6],'II',GATES['branch_zero_relative_epsilon']))
                counts['branch_identity_completed']+=1
            assignments=[{'edge':k,'role':e['active_chain'],'requested_branch':e['branch'],
                'branch_pass':e['branch'] in current['branches'][1-e['active_chain']]['branch_set']}
                for k,e in enumerate(spec['fixed_queue']['edges']) if i in e['node_ids']]
            mathok=(metric['position_max_abs']<=GATES['position_maxabs_mm'] and
                metric['rotation_matrix_max_abs']<=GATES['rotation_matrix_maxabs'] and limits['legal'] and
                bool(assignments) and all(a['branch_pass'] for a in assignments))
            current.update(stage='MATH_COMPLETED',closure=metric,limits=limits,edge_assignments=assignments,math_qualified=bool(mathok))
            durable_new(folder/f'node_{i:05d}_math.json',current);event('math_node_completed',node_id=i,math_qualified=bool(mathok))
            budget.remaining();require(counts['collision_calls_started']<spec['max_collision_calls'],'COLLISION_CALL_CAP')
            counts['collision_calls_started']+=1;current['stage']='COLLISION_STARTED';event('collision_started',node_id=i)
            collision=adapter.check_collision('II',q,timeout_s=min(10.,budget.remaining()),manifest_path=COLLISION)
            counts['collision_calls_completed']+=1;current.update(stage='COLLISION_RESPONSE_RETAINED',collision=collision)
            durable_new(folder/f'node_{i:05d}_collision_response.json',collision);event('collision_response_retained',node_id=i,response=collision)
            require(collision.get('status')=='CHECKED' and collision.get('selected_variant')=='aligned' and
                collision.get('manifest_sha256')==spec['bound_files_sha256'][COLLISION] and
                type(collision.get('collision')) is bool and set(collision.get('variants',{}))=={'native','aligned'},
                'COLLISION_UNQUALIFIED_RUNTIME')
            for variant,response in collision['variants'].items():
                codes=response.get('query_codes',[]);counts['PQP_queries']+=len(codes)
                require(bool(codes) and all(type(v) is int and v==0 for v in codes),'COLLISION_QUERY_ERROR '+variant)
            current.update(stage='COMPLETED',qualified=bool(mathok and not collision['collision']))
            durable_new(folder/f'node_{i:05d}.json',current);results.append(current)
            event('node_completed',node_id=i,qualified=current['qualified']);current=None;budget.remaining()
        require([r['node_id']for r in results]==spec['execution_node_ids'],'COMPLETE_FIXED_TAIL_REQUIRED')
        record['status']='PASS_DISCRETE_SOURCE_POLICY_TAIL262_386_PENDING_COMBINED_POST'if all(r['qualified']for r in results)else'PATH_REJECTED_BY_INDEPENDENT_QUALIFICATION'
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
            latest=current_prior();record['prior_execution_after_sha256']=latest['execution_sha256']
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
            full_tail_checked=[r['node_id']for r in results]==spec['execution_node_ids'],full_queue_checked=False,diagnostics=diagnostics)
        if record['wall_s']>=min(90.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(180.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_R2_ABB_SBL_PCS_PATH_TAIL02_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(90.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(180.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            with(folder/'cost_receipt.jsonl').open('xb')as stream:stream.write(json.dumps(receipt,allow_nan=False,separators=(',',':')).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
            record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),node_count=record['node_count'],completed_nodes=record['completed_nodes'],qualified_nodes=record['qualified_nodes'],
        external_supervision_qualified=False,independent_saved_POST_required=True,continuous_collision_certificate=False)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status')=='PASS_DISCRETE_SOURCE_POLICY_TAIL262_386_PENDING_COMBINED_POST','P_FULL_DISCRETE_PATH_NOT_QUALIFIED')

def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_P_DRAFT_VALIDATED_NO_EXECUTION');return
    execute(spec,protocol)

if __name__=='__main__':main()
