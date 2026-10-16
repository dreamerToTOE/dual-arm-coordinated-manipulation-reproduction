#!/usr/bin/env python3
"""D_TAIL02 saved-prefix plus original missing62/63 draft; import has no run.

Only stdlib and immutable D64 saved-asset/transport helpers are imported.
This module does not build a protocol/prior, claim, process or result at import.
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
import selectors
import signal
import subprocess
import time
import qualify_p4_full_r2_abb_cbirrt_d_distance_draft as old

ROOT=old.ROOT
RUN='20261015_R2_ABB_CBIRRT_D_TAIL02'
CLAIM='P4_R2_ABB_CBIRRT_D_TAIL02_ONLY62_63_5W_10CPU_20261016'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_TAIL02_PRE_DRAFT_20261016.md'
OLD_DIR='results/p4_full/'+old.RUN
OLD_EXEC=OLD_DIR+'/execution.json'
OLD_EXEC_SHA='6e18068ea1ffad849c01faa377e5268fe892448029640feb4421c3c05941e140'
OLD_PROTOCOL='configs/p4_full/r2_abb_cbirrt_d_distance_fixed64_v1.json'
OLD_PROTOCOL_SHA='3c1c1d6c25b21579bd67832e4c70df6bcc7538ab21514c91b69e61fa26d38f14'
AUDIT='reports/P4_FULL_R2_ABB_CBIRRT_D_DISTANCE01_STOP_RAW_PREFIX_INDEPENDENT_POST_V2_20261016.json'
AUDIT_SHA='15fd13b857b663a46656600b1318d65c49aebcdf6785e1a3e660c47f5264917d'
LABEL='SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_cbirrt_d_tail02_draft.py'
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),PRE,SUPERVISOR,*old.OWN]))
require=old.require
sha=old.sha
load=old.load
exact=old.exact
bits=old.bits


def fixed_assets():
    """Read old evidence only; never query62old returns or change old status."""
    require(sha(OLD_EXEC)==OLD_EXEC_SHA and sha(OLD_PROTOCOL)==OLD_PROTOCOL_SHA and sha(AUDIT)==AUDIT_SHA,'EXACT_OLD_STOP_PROTOCOL_AND_INDEPENDENT_AUDIT_REQUIRED')
    e=load(OLD_EXEC);p=load(OLD_PROTOCOL);a=load(AUDIT)
    require(sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'],'ORIGINAL_CLAIM_HASH_CHAIN_CHANGED')
    require(e['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET'and e['completed_dispatch_ids']==list(range(61))
        and [r['dispatch_index']for r in e['UNKNOWN_uncompleted_fixtures']]==[61,62,63],'ORIGINAL_STOP_AND_UNKNOWN_MUST_REMAIN')
    require(e['counts']['distance_dispatched']==e['counts']['distance_response_line_observed']==62
        and e['complete_source_raw_evidence_gate']is False and e['source_process_registry'][-1]['returncode']==-9,'ORIGINAL_PARTIAL_AND_FAILED_RAW_GATE_REQUIRED')
    require(e['actual_raw_trace_started']==e['actual_raw_trace_completed']=={'mesh_load':4,'activeDistance':30}
        and len(e['source_process_registry'])==8 and all(r['reaped']for r in e['source_process_registry']),'OLD_ACTUAL_TRACE_AND_PROCESS_TOTALS_CHANGED')
    require(a['personnel_independent']is True and a['checks_total']==a['checks_passed']==510
        and a['checks_failed']==0 and a['actual_complete_raw_returns']==62 and a['not_dispatched']==[62,63]
        and a['original_runner_index61_qualified']is False,'EXACT_SAVED_PREFIX_AUDIT_REQUIRED')
    files={name:sha(name)for name in (OLD_EXEC,OLD_PROTOCOL,AUDIT,e['claim'])}
    require(e['bound_files_sha256']==e['bound_files_after_sha256'],'ORIGINAL_BOUND_ASSETS_WERE_CHANGED')
    for name,want in {**e['bound_files_sha256'],**a['retained_sha256']}.items():
        require(sha(name)==want,'SAVED_PREFIX_ASSET_CHANGED '+name);files[name]=want
    links=[]
    for i in range(62):
        name=OLD_DIR+f'/distance_{i:03d}_raw_response_line.bin';raw=old.path(name).read_bytes()
        require(raw.endswith(b'\n')and len(raw.splitlines())==1,'EXACT_OLD_COMPLETE_RAW_LINE_REQUIRED')
        require(sha(name)==a['raw_responses'][i]['raw_line_sha256'],'OLD_RAW_AUDIT_HASH_MISMATCH')
        require(json.loads(raw)['request']==p['fixed_schedule'][i]['request'],'OLD_RAW_REQUEST_CHANGED')
        files[name]=sha(name);links.append(dict(dispatch_index=i,path=name,sha256=sha(name),
            original_runner_qualified=i<61,saved_only_raw_audit_qualified=True))
    require(not any((ROOT/OLD_DIR/f'distance_{i:03d}_request.json').exists()for i in (62,63)),'TAIL_CASE_WAS_ALREADY_DISPATCHED')
    require(len(p['fixed_schedule'])==64 and len(p['fixed_contexts'])==16,'ORIGINAL_FIXED64_REQUIRED')
    tail=p['fixed_schedule'][62:]
    require([r['dispatch_index']for r in tail]==[62,63]and all((r['factor'],r['mode'],r['environment'])==('distance_destination_fix','trace','III')for r in tail),'ONLY_ORIGINAL_MISSING_TWO_REQUIRED')
    return dict(files_sha256=files,saved_raw_links=links,fixed_schedule=tail,
        original_fixed64_schedule=p['fixed_schedule'],original_fixed16_contexts=p['fixed_contexts'])


def prior():
    paths=sorted(p for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if p.parent.name!=RUN)
    rows=[load(p)for p in paths]
    require(all(all(type(r[k])in(int,float)and math.isfinite(r[k])and r[k]>=0 for k in('wall_s','cpu_s'))for r in rows),'FINITE_PRIOR_OWN_COSTS_REQUIRED')
    return {str(p.relative_to(ROOT)):sha(p)for p in paths},math.fsum(r['wall_s']for r in rows),math.fsum(r['cpu_s']for r in rows)


def draft_protocol():
    assets=old.build_assets();prefix=fixed_assets();previous,wall,cpu=prior()
    bound={**assets['files_sha256'],**prefix['files_sha256'],**{name:sha(name)for name in OWN}}
    bound.update({name:sha(name)for name in('/usr/bin/time','/usr/bin/python3')})
    return dict(schema='P4_R2_ABB_CBIRRT_D_TAIL02_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,latest_actual_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,build_assets=assets,saved_prefix=prefix,
        own_source_sha256={name:sha(name)for name in OWN},bound_files_sha256=bound,
        prior_execution_sha256=previous,previous_r2_wall_s=wall,previous_r2_cpu_s=cpu,
        budget=dict(wall_s=5.,cpu_s=10.,child_cpu_limit_s=10,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        maxima=dict(new_processes=1,new_distance_dispatches=2,aggregate_processes=9,aggregate_dispatched=64,
            aggregate_trace_mesh_load=5,aggregate_trace_activeDistance=32,plain_trace_pairs=32),
        gates=load(OLD_PROTOCOL)['gates'],
        external_supervision=dict(required=True,exclusive_sibling_time_log=True,
            sibling_path='results/p4_full/'+RUN+'.supervision.time.txt',format='%e %U %S %x',
            metadata_path='results/p4_full/'+RUN+'.supervision.jsonl',
            stderr_path='results/p4_full/'+RUN+'.supervision.stderr.log',
            charge_path='results/p4_full/'+RUN+'.supervision.charge.json',
            time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'),
            elapsed_decimal_upper_padding_s=.01,CPU_user_plus_system_upper_padding_s=.02,
            final_independent_POST_required=True,supervisor_log_write_is_not_scientific_process_cost=True),
        preservation=dict(original_D64_status='STOP_FINAL_WALL_OR_CPU_BUDGET',original_completed=61,
            original_UNKNOWN=[61,62,63],original_tail_exit=-9,original_full_raw_gate=False,
            original_single_run_PASS_permanently_unavailable=True,index61_is_saved_raw_only=True),
        RNG_boundary='Newprocess setSeed7 once;1newCBi constructor/structuralRNG member. Aggregate9, library actualRNG constructor/seed drawsUNOBSERVED. This does not restore the old eighthprocess history.',
        save_policy='OneappendJSONL journal for events/requests/base64 raw chunks/responses/gates;flush perrecord;oneend fsync. Separateexclusiveclaim,execution,receipt eachonce. Finalreceipt tail cost nonzeroUNMEASURED, externaltime+independentPOST mandatory.',
        zero_calls=dict(compile=0,old_distance_requery=0,FK=0,IK=0,NR=0,collision_queries=0,RBS=0,solve=0,VI_constructions=0,formal_table_I=0),
        not_qualification_for=['original_D64_single_run_PASS','planning','RSS','RBS','path','paper_full_reproduction'],
        no_retry_reset_resume=True)


def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_TAIL02_CURRENT_RECIPE_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_TAIL02_REVIEWS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'TAIL02_REVIEW_AND_ROOT_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in [*OWN,str(protocol.relative_to(ROOT))]:
        subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        require(not subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True),'UNCOMMITTED '+name)
    for name,want in spec['own_source_sha256'].items():
        require(hashlib.sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()==want,'COMMIT_BLOB_MISMATCH '+name)
    return commit


class Budget(old.Budget):
    def __init__(self,spec,begun,cpu_start):
        super().__init__(spec,begun,cpu_start)
        self.wall_cap=min(5.,3600.-spec['previous_r2_wall_s']);self.cpu_cap=min(10.,7200.-spec['previous_r2_cpu_s'])
        require(min(self.wall_cap,self.cpu_cap)>0,'TAIL02_TOTAL_BUDGET_EXHAUSTED')


class Journal:
    def __init__(self,name):self.stream=name.open('xb',buffering=0)
    def add(self,event,**fields):
        raw=json.dumps(dict(event=event,at_utc=old.builder.utc(),**fields),allow_nan=False,separators=(',',':')).encode()+b'\n'
        require(self.stream.write(raw)==len(raw),'JOURNAL_INCOMPLETE_WRITE_NO_RETRY');self.stream.flush()
    def finish(self):
        self.stream.flush();os.fsync(self.stream.fileno());self.stream.close()


class Session:
    """D64 safe registration/EOF transport, single raw journal instead of16fsyncs."""
    def __init__(self,target,budget,journal,counts):
        self.target=target;self.budget=budget;self.journal=journal;self.counts=counts;self.proc=None
        self.selector=selectors.DefaultSelector();self.raw={'stdout':bytearray(),'stderr':bytearray()}
        self.pending=b'';self.responses=[];self.eof=False;self.closed=False;self.startup_complete=False;self.close_group=None
        self.command=[target['binary'],'III',target['stage'],'distance','trace']
    def start(self):
        previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            def limits():
                signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask);resource.setrlimit(resource.RLIMIT_CPU,(10,10))
            self.counts['source_process_start_attempted']+=1;self.journal.add('source_process_start_attempted',command=self.command)
            self.proc=subprocess.Popen(self.command,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                bufsize=0,start_new_session=True,preexec_fn=limits,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8',**old.builder.THREADS})
            self.budget.processes.append(self.proc);self.counts['source_process_started']+=1
            self.journal.add('source_process_started',pid=self.proc.pid,command=self.command)
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
        self.budget.check();self.register_pipes()
        group=old.process_group_members(self.proc.pid)
        require([r['pid']for r in group]==[self.proc.pid],'UNEXPECTED_SOURCE_START_GROUP')
        self.journal.add('source_start_group',members=group);self.startup_complete=True
    def register_pipes(self):
        if self.proc is None:return
        for channel in ('stdout','stderr'):
            stream=getattr(self.proc,channel)
            if stream is not None and not stream.closed and stream not in [k.fileobj for k in self.selector.get_map().values()]:
                os.set_blocking(stream.fileno(),False);self.selector.register(stream,selectors.EVENT_READ,channel)
    def pump(self,timeout=.02,enforce=True):
        if enforce:self.budget.check();timeout=min(timeout,max(0.,self.budget.remaining()))
        for key,_ in self.selector.select(max(0.,timeout)):
            raw=os.read(key.fileobj.fileno(),65536)
            if not raw:self.selector.unregister(key.fileobj);continue
            self.raw[key.data].extend(raw)
            if key.data=='stdout':self.pending+=raw
            self.journal.add('raw_pipe_chunk',channel=key.data,bytes=len(raw),base64=base64.b64encode(raw).decode())
        if enforce:self.budget.check()
    def query(self,fixture):
        self.budget.check();self.journal.add('distance_request',fixture=fixture)
        raw=json.dumps(fixture['request'],allow_nan=False,separators=(',',':')).encode()+b'\n'
        require(len(raw)<4096 and self.proc.poll()is None,'SOURCE_NOT_READY_FOR_EXACT_REQUEST')
        self.counts['distance_dispatch_attempted']+=1
        sent=os.write(self.proc.stdin.fileno(),raw);require(sent==len(raw),'INCOMPLETE_REQUEST_NO_RETRY')
        self.counts['distance_dispatched']+=1
        while b'\n'not in self.pending:
            self.pump()
            require(bool(self.selector.get_map())or b'\n'in self.pending,'EOF_WITHOUT_RESPONSE')
        line,self.pending=self.pending.split(b'\n',1);self.counts['raw_response_lines_observed']+=1
        self.journal.add('raw_response_line',dispatch_index=fixture['dispatch_index'],bytes=len(line)+1,base64=base64.b64encode(line+b'\n').decode())
        response=json.loads(line);self.responses.append(response);return response
    def finish(self,normal):
        if self.closed:return
        if self.proc is not None:
            self.register_pipes()
            if normal:
                self.close_group=old.process_group_members(self.proc.pid)
                require([r['pid']for r in self.close_group]==[self.proc.pid],'UNEXPECTED_SOURCE_CLOSE_GROUP')
                if self.proc.stdin and not self.proc.stdin.closed:self.proc.stdin.close()
                deadline=time.monotonic()+self.budget.remaining()
            else:old.kill_source_process(self.proc);deadline=time.monotonic()+2.
            while self.selector.get_map()and time.monotonic()<deadline:self.pump(.01,enforce=normal)
            try:self.proc.wait(timeout=max(.001,deadline-time.monotonic()))
            except subprocess.TimeoutExpired:old.kill_source_process(self.proc);self.proc.wait(timeout=1.)
            while self.selector.get_map()and time.monotonic()<deadline:self.pump(0.,enforce=False)
            self.eof=not self.selector.get_map()
            for stream in(self.proc.stdin,self.proc.stdout,self.proc.stderr):
                if stream is not None and not stream.closed:stream.close()
        self.selector.close();self.closed=True
        if normal:require(self.eof and not self.pending and self.proc.returncode==0,'NEW_SOURCE_EXIT_EOF_OR_STDOUT_TAIL_FAILED')


def check_response(response,fixture,context):
    require(response['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1'and response['status']=='SOURCE_INTERFACE_COMPLETED_NOT_QUALIFIED','EXACT_D_RESPONSE_REQUIRED')
    require(response['environment']==fixture['environment']and response['mode']==fixture['mode']and response['operation']=='distance'
        and exact(response['request'],fixture['request']),'FIXED_REQUEST_CHANGED')
    require(response['source_dispatch_started']==response['source_dispatch_completed']==1 and response['solve_calls']==0
        and response['formal_table_I_calls']==0 and response['independent_path_qualified']is False,'DISTANCE_SCOPE_CHANGED')
    require(type(response['distance'])in(int,float)and math.isfinite(response['distance'])and response['distance']>=0,'FINITE_DISTANCE_REQUIRED')
    for arm in('qa12','qb12'):
        require(bits(response[arm+'_after'])==bits(fixture['request'][arm])==response[arm+'_binary64_after'],'OMPL_STATE_MUTATION')
    trace=fixture['mode']=='trace';construction=response['construction']
    require(type(response['source_counts_observed'])is bool and response['source_counts_observed']==trace
        and type(construction['source_counts_observed'])is bool and construction['source_counts_observed']==trace,'OBSERVATION_FLAGS_CHANGED')
    require(construction['cbirrt_constructor_dispatch_completed']==construction['ompl_setSeed_calls_completed']==1
        and construction['svc_only_constructor_dispatch_completed']==construction['srand_calls_completed']==0
        and construction['source_direct_rng_member_initializations_structural']==1
        and construction['source_direct_rng_member_true_started_completed']=='UNOBSERVED_LIBRARY_NOT_HOOKED'
        and construction['library_internal_seed_draws']=='UNOBSERVED_NOT_REPORTED_ZERO','CONSTRUCTOR_RNG_BOUNDARY_CHANGED')
    if trace:
        old.assert_trace(response,fixture)
        require(construction['source_started']==construction['source_completed']=={'mesh_load':1}and len(construction['trace'])==2,'CONSTRUCTOR_TRACE_COUNT_CHANGED')
        a,b=construction['trace']
        require(a['event']=='entered'and b['event']=='completed'and a['kind']==b['kind']=='mesh_load'
            and a['id']==b['id']==1 and a['args']=={}and b['result']=={},'CONSTRUCTOR_TRACE_CHANGED')
    else:
        for item in(response,construction):require(item['trace']is None and item['source_started']is None and item['source_completed']is None,'PLAIN_BODY_MUST_REMAIN_UNOBSERVED')
    reference=context[fixture['factor']+'_reference_rad']
    require(abs(response['distance']-reference)<=1e-12,'FIXED_L2_REFERENCE_FAILED')
    if fixture['factor']=='distance_destination_fix'and context['diagonal']:require(response['distance']==0.,'FIXED_DIAGONAL_NOT_STRICT_ZERO')
    if fixture['factor']=='source_control'and context['diagonal']and context['active_chain']==1:require(response['distance']>0.,'OLD_NONZERO_SELF_NOT_REPRODUCED')


def check_all64(spec,new_responses):
    prefix=spec['saved_prefix'];fixtures=prefix['original_fixed64_schedule'];contexts=prefix['original_fixed16_contexts']
    responses=[json.loads(old.path(row['path']).read_bytes())for row in prefix['saved_raw_links']]+new_responses
    require(len(responses)==64,'FULL64_RAW_RESPONSES_REQUIRED')
    lookup={};constructors={}
    for response,fixture in zip(responses,fixtures):
        check_response(response,fixture,contexts[fixture['context_index']]);key=(fixture['factor'],fixture['mode'],fixture['case_id'])
        require(key not in lookup,'DUPLICATE_FIXED_CASE');lookup[key]=response
        # The new two responses belong to a ninth process, not the old eighth.
        session=('TAIL02',)if fixture['dispatch_index']>=62 else(fixture['factor'],fixture['mode'],fixture['environment'])
        if session in constructors:require(exact(constructors[session],response['construction']),'CONSTRUCTOR_METADATA_CHANGED_WITHIN_PROCESS')
        else:constructors[session]=response['construction']
    pairs=[]
    for factor in old.FACTORS:
        for c in contexts:
            a,b=(lookup[(factor,mode,c['case_id'])]for mode in('plain','trace'))
            require(exact(old.normalize_response(a),old.normalize_response(b)),'SPLIT_PLAIN_TRACE_BINARY64_MISMATCH')
            pairs.append(dict(factor=factor,case_id=c['case_id'],passed=True))
    for mode in('plain','trace'):
        for c in contexts:
            case=c['case_id'];rev=next(r for r in contexts if r['a']==c['b']and r['b']==c['a']and r['active_chain']==c['active_chain'])
            if c['active_chain']==0:require(exact(lookup[(old.FACTORS[0],mode,case)]['distance'],lookup[(old.FACTORS[1],mode,case)]['distance']),'ROLE0_CROSS_FACTOR_CHANGED')
            require(exact(lookup[(old.FACTORS[1],mode,case)]['distance'],lookup[(old.FACTORS[1],mode,rev['case_id'])]['distance']),'FIXED_EXCHANGE_SYMMETRY_FAILED')
    require(len(constructors)==9 and len(pairs)==32,'EXACT9_CONSTRUCTORS32_PAIRS_REQUIRED')
    return dict(actual64_raw_responses_saved_qualified=True,plain_trace_comparisons=pairs,
        original_control_four_unique_nonzero_self_cases=4,aggregate_processes=9,aggregate_dispatched=64,
        structural_direct_rng_initializations=9,library_actual_rng_and_seed_draws='UNOBSERVED',
        original_single_run_PASS=False,original_UNKNOWN=[61,62,63],index61_original_qualification=False)


def raw_trace(raw):
    rows=[]
    for line in raw.splitlines(keepends=True):
        if old.MARKER in line:rows.append(json.loads(line.split(old.MARKER,1)[1]))
    return rows


def supervisor_proof(spec,protocol):
    """Bind this actual parent GNUtime to the atomically exclusive open inode."""
    ext=spec['external_supervision'];metadata=old.path(ext['metadata_path'])
    planned_raw=metadata.read_bytes().splitlines(keepends=True)[0];planned=json.loads(planned_raw)
    parent=os.getppid();parent_row=old.stat_row(parent)
    require(parent_row is not None and int(parent_row[1])==planned['supervisor_pid'],'EXACT_SUPERVISOR_PARENT_CHAIN_REQUIRED')
    require(planned['event']=='planned_launch'and planned['run_id']==RUN and planned['protocol_sha256']==sha(protocol)
        and planned['runner_sha256']==sha(__file__)and planned['supervisor_source_sha256']==sha(SUPERVISOR),'EXACT_SUPERVISOR_SOURCE_PROTOCOL_REQUIRED')
    require(sha(Path('/proc',str(parent),'exe'))==ext['time_binary_sha256'],'ACTUAL_PARENT_GNU_TIME_REQUIRED')
    actual_argv=Path('/proc',str(parent),'cmdline').read_bytes().rstrip(b'\0').split(b'\0')
    expected=['/usr/bin/time','--quiet','-f',ext['format'],'-o',f"/proc/self/fd/{planned['time_fd']}",'/usr/bin/python3',str(Path(__file__).resolve()),'--protocol',str(protocol)]
    require(actual_argv==[v.encode()for v in expected]and planned['argv']==expected,'ACTUAL_TIME_ARGV_MISMATCH')
    sibling=old.path(ext['sibling_path']).stat();held=[]
    for name in Path('/proc',str(parent),'fd').iterdir():
        try:
            stat=name.stat()
            if(stat.st_ino,stat.st_dev)==(sibling.st_ino,sibling.st_dev):held.append(int(name.name))
        except FileNotFoundError:pass
    require(held and sibling.st_ino==planned['time_inode']and sibling.st_dev==planned['time_device'],'EXCLUSIVE_SUPERVISION_INODE_MISMATCH')
    return dict(actual_time_pid=parent,actual_time_start_ticks=int(parent_row[19]),supervisor_pid=planned['supervisor_pid'],
        actual_argv=expected,planned_launch_line_sha256=hashlib.sha256(planned_raw).hexdigest(),
        time_inode=sibling.st_ino,time_device=sibling.st_dev,actual_time_output_fds=sorted(held),metadata_path=ext['metadata_path'],
        cost_charge_path=ext['charge_path'],external_POST_required=True)


def execute(spec,protocol):
    begun=time.monotonic();cpu_start=old.own_reaped_cpu();commit=validate(spec,protocol,True)
    launch_proof=supervisor_proof(spec,protocol)
    folder=ROOT/'results/p4_full'/RUN;claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXCLUSIVE_TAIL02_NO_RETRY')
    require(not old.builder.active_p4(),'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    budget=None;journal=None;session=None;counts=Counter();diagnostics=[];completed=[];error=None
    record=dict(schema='P4_R2_ABB_CBIRRT_D_TAIL02_EXECUTION_V1',run_id=RUN,classification=LABEL,
        source_commit=commit,status='STOP_PREFIX_RETAINED',protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),
        claim=str(claim.relative_to(ROOT)),budget=spec['budget'],prior_execution_sha256=spec['prior_execution_sha256'],
        previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],
        bound_files_sha256=spec['bound_files_sha256'],original_preservation=spec['preservation'],
        supervisor_launch_proof=launch_proof,cost_supervision_charge=spec['external_supervision']['charge_path'],
        external_supervision_qualified=False,independent_saved_POST_required=True,
        zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0)
    try:
        old.durable_new(claim,dict(schema='P4_R2_ABB_CBIRRT_D_TAIL02_CLAIM_V1',run_id=RUN,protocol=record['protocol'],
            protocol_sha256=record['protocol_sha256'],source_commit=commit,budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=Journal(folder/'evidence.jsonl')
        journal.add('setup',record=record,saved_raw_links=spec['saved_prefix']['saved_raw_links'])
        budget=Budget(spec,begun,cpu_start);budget.start();budget.check()
        session=Session(spec['build_assets']['targets']['distance_destination_fix'],budget,journal,counts);session.start()
        for fixture in spec['saved_prefix']['fixed_schedule']:
            response=session.query(fixture)
            journal.add('parsed_response_before_gates',dispatch_index=fixture['dispatch_index'],response=response)
            check_response(response,fixture,spec['saved_prefix']['original_fixed16_contexts'][fixture['context_index']])
            completed.append(fixture['dispatch_index']);journal.add('qualified_new_distance',dispatch_index=fixture['dispatch_index'])
        session.finish(normal=True);budget.check()
        require(counts['distance_dispatched']==counts['raw_response_lines_observed']==2 and completed==[62,63],'EXACT2_NEW_DISPATCHES_AND_RETURNS_REQUIRED')
        record['aggregate_saved_only_qualification']=check_all64(spec,session.responses);budget.check()
        expected=session.responses[0]['construction']['trace']+[row for response in session.responses for row in response['trace']]
        actual=raw_trace(bytes(session.raw['stderr']))
        require(exact(actual,expected),'NEW_RAW_CONSTRUCTOR_ONCE_PLUS2_DISTANCE_TRACE_MISMATCH')
        lines=bytes(session.raw['stdout']).splitlines(keepends=True)
        require(len(lines)==2 and all(line.endswith(b'\n')and exact(json.loads(line),response)for line,response in zip(lines,session.responses)),'EXACT2_NEW_STDOUT_LINES_REQUIRED')
        entered=Counter(r['kind']for r in actual if r['event']=='entered');returned=Counter(r['kind']for r in actual if r['event']=='completed')
        require(dict(entered)==dict(returned)=={'mesh_load':1,'activeDistance':2},'NEW_RAW_BODY_TOTALS_REQUIRED')
        record['new_raw_trace_started']=dict(entered);record['new_raw_trace_completed']=dict(returned)
        record['aggregate_raw_trace_started']={'mesh_load':5,'activeDistance':32};record['aggregate_raw_trace_completed']={'mesh_load':5,'activeDistance':32}
        record['status']=LABEL
    except BaseException as exc:
        if budget is not None:budget.close()
        error=exc;record['termination_reason']=repr(exc)
    finally:
        if budget is not None:budget.close()
        processes=list({p.pid:p for p in ([]if budget is None else budget.processes)+([]if session is None or session.proc is None else[session.proc])}.values())
        for proc in processes:
            try:old.kill_source_process(proc)
            except BaseException as exc:diagnostics.append(dict(stage='kill',error=repr(exc)))
        if session is not None:
            try:session.finish(normal=False)
            except BaseException as exc:diagnostics.append(dict(stage='session_cleanup',error=repr(exc)))
        for proc in processes:
            try:old.kill_source_process(proc);proc.wait(timeout=1.)
            except BaseException as exc:diagnostics.append(dict(stage='central_reap',pid=proc.pid,error=repr(exc)))
        record['source_process_registry']=[dict(pid=p.pid,reaped=p.returncode is not None,returncode=p.returncode)for p in processes]
        record['counts']=dict(counts);record['completed_new_dispatch_ids']=completed
        record['UNKNOWN_new_dispatch_ids']=[i for i in(62,63)if i not in completed]
        raw_gate=session is not None and session.proc is not None and session.proc.returncode==0 and session.eof and session.closed and session.startup_complete and not session.pending
        if record['status']==LABEL and not(len(processes)==counts['source_process_started']==1 and raw_gate):record['status']='STOP_PROCESS_EOF_OR_EXIT_UNQUALIFIED'
        try:
            after={name:sha(name)for name in spec['bound_files_sha256']};record['bound_files_after_sha256']=after
            require(after==spec['bound_files_sha256'],'BOUND_ASSET_CHANGED')
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
            require(record['protocol_after_sha256']==record['protocol_sha256']and record['claim_after_sha256']==record.get('claim_sha256'),'RECIPE_CHANGED')
            previous,_,_=prior();record['prior_execution_after_sha256']=previous
            require(previous==spec['prior_execution_sha256'],'PRIOR_SET_CHANGED')
        except BaseException as exc:diagnostics.append(dict(stage='mandatory_hashes',error=repr(exc)))
        if journal is not None:
            try:
                # A failed append can leave an incomplete old line: retain it,
                # add a fresh boundary, and retain complete final raw snapshots.
                journal.stream.write(b'\n')
                if session is not None:
                    journal.add('final_complete_raw_streams',streams={channel:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode())for channel,raw in session.raw.items()},EOF=session.eof)
                journal.add('final_counts',counts=dict(counts),completed_new_dispatch_ids=completed,diagnostics=diagnostics)
                journal.finish();record['evidence_journal']=str((folder/'evidence.jsonl').relative_to(ROOT));record['evidence_journal_sha256']=sha(folder/'evidence.jsonl')
            except BaseException as exc:diagnostics.append(dict(stage='journal_final_preservation',error=repr(exc)))
        record['diagnostics']=diagnostics
        record.update(wall_s=time.monotonic()-begun,cpu_s=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes))
        if record['wall_s']>=min(5.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(10.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            old.durable_new(folder/'execution.json',record)
            # This sample includes execution.json serialization+fsync; the
            # receipt's own serialization+fsync is explicitly not zero-cost.
            receipt=dict(schema='P4_R2_ABB_CBIRRT_D_TAIL02_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),
                status=record['status'],wall_s_through_execution_persistence=time.monotonic()-begun,
                cpu_s_through_execution_persistence=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(5.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(10.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            with(folder/'cost_receipt.jsonl').open('xb')as stream:
                stream.write(json.dumps(receipt,allow_nan=False,separators=(',',':')).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
            record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),completed_new=completed,
        external_supervision_qualified=False,receipt_tail_cost='UNMEASURED_NONZERO',new_compile=0,new_solve=0)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status')==LABEL,'TAIL02_DID_NOT_COMPLETE_INTERNAL_GATES')


def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_TAIL02_DRAFT_VALIDATED_NO_EXECUTION');return
    execute(spec,protocol)


if __name__=='__main__':main()
