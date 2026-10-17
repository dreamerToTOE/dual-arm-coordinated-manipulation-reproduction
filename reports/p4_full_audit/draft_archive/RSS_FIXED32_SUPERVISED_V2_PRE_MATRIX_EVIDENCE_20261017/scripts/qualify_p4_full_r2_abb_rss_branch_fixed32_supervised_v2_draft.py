#!/usr/bin/env python3
"""DRAFT V2: same saved fixed4x8 math, versioned one-shot supervision only.

No import-time project work. The static template is unfrozen and has no prior.
Future describe/freeze requires the actual reviewed V25 ledger and preservation.
No new candidates, changed gates, collision, RBS, solve, RNG or VI work.
"""
from pathlib import Path
import argparse
import base64
from collections import Counter
import hashlib
import json
import math
import os
import resource
import selectors
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
RUN='20261017_R2_ABB_RSS_BRANCH_MATH01'
CLAIM='P4_R2_ABB_RSS_FIXED32_MATH01_SUPERVISED_V2_10W20CPU_20261017'
SCHEMA='P4_R2_ABB_RSS_FIXED32_BRANCH_MATH_SUPERVISED_V2'
LABEL='RECONSTRUCTED_FIXED_SAVED_INPUT_BRANCH_MAPPING_MATH_ONLY'
IDS=('II_obs0681','II_obs0689','III_obs1065','III_obs1073')
TEMPLATE='configs/p4_full/r2_abb_rss_branch_fixed32_math_supervised_v2.draft.json'
LEGACY='configs/p4_full/r2_abb_rss_branch_fixed32_math_v1.draft.json'
LEGACY_SHA='1bea1b060542c1ef6f478581817e1dda963622600bd9ad3119c99616601da656'
PRIOR_LEDGER='results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V25.json'
PRIOR_SHA='ce612e7c9706666a338aae6deda581274f1aadb229e2be999cd6ee836499e64a'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_rss_branch_fixed32_v2_draft.py'
PRE='reports/P4_FULL_R2_ABB_RSS_BRANCH_FIXED32_SUPERVISED_V2_PRE_DRAFT_20261017.md'
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),SUPERVISOR,PRE,TEMPLATE]
THREADS={k:'1'for k in('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
SOURCE_ENV={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8',**THREADS}

def path(p):
    p=Path(p);return p if p.is_absolute()else ROOT/p
def sha(p):return hashlib.sha256(path(p).read_bytes()).hexdigest()
def load(p):return json.loads(path(p).read_text())
def require(ok,why):
    if not ok:raise RuntimeError(why)
def durable_new(p,value):
    with path(p).open('xb')as f:
        f.write(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2).encode()+b'\n');f.flush();os.fsync(f.fileno())
    fd=os.open(path(p).parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def durable_line(p,value):
    with path(p).open('xb')as f:
        f.write(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()+b'\n');f.flush();os.fsync(f.fileno())
    fd=os.open(path(p).parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def cpu():
    a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime
def stat_row(pid):
    try:return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
    except (OSError,ValueError,IndexError):return None
def process_group_members(pgid):
    rows=[]
    for name in Path('/proc').glob('[0-9]*/stat'):
        try:
            row=name.read_text().rsplit(')',1)[1].split()
            if int(row[2])==pgid:rows.append(dict(pid=int(name.parent.name),ppid=int(row[1]),pgrp=int(row[2]),start_ticks=int(row[19])))
        except (OSError,ValueError,IndexError):pass
    return sorted(rows,key=lambda r:r['pid'])
def live_cpu(processes):
    value=0.
    for p in processes:
        if p.returncode is not None:continue
        row=stat_row(p.pid)
        if row is not None:value+=sum(int(row[i])for i in(11,12,13,14))/os.sysconf('SC_CLK_TCK')
    return value
def kill_group(proc):
    leader=stat_row(proc.pid)
    if leader is not None:
        expected=getattr(proc,'p4_start_ticks',None)
        require((expected is not None and int(leader[19])==expected)or(expected is None and int(leader[1])==os.getpid()),'SOURCE_PID_REUSE_REFUSE_KILL')
    if process_group_members(proc.pid):
        try:os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    if proc.poll()is None:proc.kill()

class Budget:
    def __init__(self,begun,cpu0,spec):
        self.begun=begun;self.cpu0=cpu0;self.processes=[];self.closed=False;self.closing=False
        self.wall=spec['supervision_engineering']['active_wall_stop_s'];self.cpu=spec['supervision_engineering']['active_cpu_stop_s']
        self.previous=signal.getsignal(signal.SIGALRM)
        require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    def start(self):signal.signal(signal.SIGALRM,self.alarm);signal.setitimer(signal.ITIMER_REAL,.02,.02)
    def alarm(self,*_):
        if not self.closing:self.check()
    def check(self):
        require(time.monotonic()-self.begun<self.wall and cpu()-self.cpu0+live_cpu(self.processes)<self.cpu,'FIXED32_ACTIVE_RESOURCE_STOP_CLEANUP_RESERVE')
    def close(self):
        if self.closed:return
        self.closing=True;mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            signal.setitimer(signal.ITIMER_REAL,0)
            while signal.SIGALRM in signal.sigpending():signal.sigwait({signal.SIGALRM})
            signal.signal(signal.SIGALRM,self.previous);self.closed=True
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,mask)

class Journal:
    def __init__(self,p):self.p=p;self.stream=p.open('xb',buffering=0)
    def add(self,kind,**fields):
        raw=json.dumps(dict(event=kind,**fields),allow_nan=False,separators=(',',':')).encode()+b'\n'
        require(self.stream.write(raw)==len(raw),'JOURNAL_SHORT_WRITE');self.stream.flush();os.fsync(self.stream.fileno())
    def finish(self):self.stream.flush();os.fsync(self.stream.fileno());self.stream.close()

def current_prior():
    ledgers=list((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers,'WAIT_LATEST_REAL_V25_OR_LATER_LEDGER')
    ledger=max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1]));version=int(ledger.stem.rsplit('V',1)[1]);value=load(ledger)
    require(str(ledger.relative_to(ROOT))==PRIOR_LEDGER and sha(ledger)==PRIOR_SHA,'LATEST_REAL_V25_FIXED_FREEZE_REQUIRED_NEWER_PRIOR_NEEDS_REVIEW')
    preservation=ROOT/'results/p4_full'/f'20261016_RECOVERY_IMMUTABLE_VERIFICATION_V{version}.json';saved=load(preservation)
    require(saved.get('passed')is True and saved['ledger']['path']==str(ledger.relative_to(ROOT)) and saved['ledger']['sha256']==sha(ledger),'REAL_LATEST_PRESERVATION_REQUIRED')
    actual={str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if p.parent.name!=RUN}
    require({r['execution']:r['execution_sha256']for r in value['executions']}==actual,'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS')
    wall=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in value['executions']);used=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in value['executions'])
    require(all(math.isfinite(v)and v>=0 for v in(wall,used)) and wall==value['conservative_r2_sum_wall_s'] and used==value['conservative_r2_sum_cpu_s'],'EXACT_LATEST_CHARGED_FSUM')
    require(value['r2_caps']=={'wall_s':3600.,'cpu_s':7200.} and value['r2_remaining']['wall_s']==3600.-wall and value['r2_remaining']['cpu_s']==7200.-used and 3600.-wall>=10. and 7200.-used>=20.,'ORIGINAL_R2_CAPS_AND_FULL_ITEM_REMAINING')
    require(value['vi_B_candidate_cap']==974 and value['vi_B_consumed']['candidate_constructions']==974 and value['vi_B_remaining']['candidate_constructions']==0 and value['formal_table_I_calls']==0 and value['formal_table_I_required_calls']==22500,'VI_EXHAUSTED_FORMAL_SCOPE_UNCHANGED')
    for r in value['executions']:
        if 'charged_wall_s'not in r:continue
        post=load(r['external_post'])
        require(sha(r['external_post'])==r['external_post_sha256'] and post['personnel_independent']is True and post['external_supervision_qualified']is True and post['checks_total']==post['checks_passed'] and post['checks_failed']==0 and post['execution_sha256']==r['execution_sha256'] and post['upper_wall_s']==r['charged_wall_s'] and post['upper_cpu_s']==r['charged_cpu_s'] and sha(r['external_time'])==r['external_time_sha256']==post['external_time_sha256'],'REAL_PRIOR_EXTERNAL_REPLACEMENT_CERTIFICATE')
    for charge in(ROOT/'results/p4_full').glob('*_R2_*.supervision.charge.json'):
        run=charge.name.removesuffix('.supervision.charge.json')
        if run!=RUN:require((charge.parent/run/'execution.json').is_file(),'ORPHAN_SUPERVISED_COST_REQUIRES_ACCOUNTING '+run)
    return dict(ledger=str(ledger.relative_to(ROOT)),ledger_sha256=sha(ledger),preservation=str(preservation.relative_to(ROOT)),preservation_sha256=sha(preservation),execution_sha256=actual,wall_s=wall,cpu_s=used,historical_unmeasured_tail='RETAINED_UNKNOWN; REMAINING_IS_UPPER_BOUND')

def draft_protocol():
    spec=load(TEMPLATE);require(spec['frozen']is False and spec['accounting_snapshot']is None and spec['actual_charge_prior']is None,'STATIC_TEMPLATE_MUST_REMAIN_UNFROZEN')
    require(sha(LEGACY)==LEGACY_SHA,'ORIGINAL_V1_PROTOCOL_CHANGED');legacy=load(LEGACY)
    for key in('run_id','classification','runtime_layer','literal_native_scope','active_arm','passive_arm','passive_branches_in_order','fixed_cases','ik_binary','ik_binary_sha256','budget','gates','target_policy','branch_policy','collision_scope','positive_coverage_gate','stop_policy','new_VI_candidate_constructions','formal_table_I_calls','zero_calls','RSS_gamma_preserved'):
        require(spec[key]==legacy[key],'ORIGINAL_SCIENTIFIC_POLICY_CHANGED '+key)
    require(all(spec['bound_files_sha256'].get(k)==v for k,v in legacy['bound_files_sha256'].items()),'ORIGINAL_V1_BOUND_BYTES_REQUIRED')
    prior=current_prior();spec['accounting_snapshot']={'path':prior['ledger'],'sha256':prior['ledger_sha256']};spec['actual_charge_prior']=prior
    spec['previous_r2_wall_s']=prior['wall_s'];spec['previous_r2_cpu_s']=prior['cpu_s']
    spec['own_source_sha256']={n:sha(n)for n in OWN}
    spec['bound_files_sha256'].update(spec['own_source_sha256']);spec['bound_files_sha256'][prior['ledger']]=prior['ledger_sha256'];spec['bound_files_sha256'][prior['preservation']]=prior['preservation_sha256']
    for n,want in spec['bound_files_sha256'].items():require(sha(n)==want,'BOUND_INPUT_CHANGED '+n)
    ext=spec['external_supervision'];ext['time_binary_sha256']=sha('/usr/bin/time');ext['python_binary_sha256']=sha('/usr/bin/python3')
    for n in('/usr/bin/time','/usr/bin/python3'):spec['bound_files_sha256'][n]=sha(n)
    return spec

def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    require(set(spec)==set(expected) and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_REVIEWED_FIXED32_RECIPE')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews']) and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_REVIEW_FLAGS')
    require(tuple(c['case_id']for c in spec['fixed_cases'])==IDS and spec['passive_branches_in_order']==list(range(8)) and spec['runtime_layer']=='GEOMETRY_CONSISTENT_CORRECTED','ORIGINAL_FIXED32_INPUT_ORDER')
    for case in spec['fixed_cases']:
        obs=load(case['observations_path'])[case['observation_index0']]
        require(sha(case['observations_path'])==case['observations_sha256'] and obs['candidate_q_rad']==case['q12_rad'] and obs['branch']==case['original_arm1_construction_branch']==1,'ORIGINAL_Q12_OR_ARM1_IDENTITY_CHANGED')
        require(hashlib.sha256(json.dumps(obs,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()==case['original_record_canonical_sha256'],'ORIGINAL_RECORD_IDENTITY_CHANGED')
    if not execute:return None
    require(spec['frozen'] and all(spec['reviews'].values()),'ROOT_AND_INDEPENDENT_REVIEW_FROZEN_PROTOCOL_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in[*OWN,str(protocol.relative_to(ROOT))]:require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),'UNCOMMITTED_SOURCE_OR_PROTOCOL '+name)
    return commit

def supervisor_proof(spec,protocol):
    ext=spec['external_supervision'];raw=path(ext['metadata_path']).read_bytes().splitlines(keepends=True)[0];planned=json.loads(raw)
    parent=os.getppid();row=stat_row(parent);grand=stat_row(planned['supervisor_pid'])
    require(row is not None and grand is not None and int(row[1])==planned['supervisor_pid'] and int(grand[19])==planned['supervisor_start_ticks'],'LIVE_EXACT_PARENT_TIME_SUPERVISOR_CHAIN')
    require(planned['event']=='planned_launch' and planned['run_id']==RUN and planned['protocol_sha256']==sha(protocol) and planned['runner_sha256']==sha(__file__) and planned['supervisor_source_sha256']==sha(SUPERVISOR),'LIVE_SOURCE_AND_PROTOCOL_BINDING')
    require(sha(Path('/proc',str(parent),'exe'))==ext['time_binary_sha256'],'ACTUAL_PARENT_GNU_TIME_REQUIRED')
    argv=['/usr/bin/time','--quiet','-f',ext['format'],'-o',f"/proc/self/fd/{planned['time_fd']}",'/usr/bin/python3',str(Path(__file__).resolve()),'--protocol',str(protocol)]
    actual=Path('/proc',str(parent),'cmdline').read_bytes()
    require(actual.rstrip(b'\0').split(b'\0')==[v.encode()for v in argv] and planned['argv']==argv,'ACTUAL_GNU_TIME_ARGV_REQUIRED')
    sibling=path(ext['sibling_path']).stat();held=[]
    for p in Path('/proc',str(parent),'fd').iterdir():
        try:
            s=p.stat()
            if(s.st_ino,s.st_dev)==(sibling.st_ino,sibling.st_dev):held.append(dict(fd=int(p.name),fdinfo_raw=Path('/proc',str(parent),'fdinfo',p.name).read_text()))
        except FileNotFoundError:pass
    require(held and sibling.st_ino==planned['time_inode'] and sibling.st_dev==planned['time_device'],'LIVE_EXCLUSIVE_TIME_FD_INODE_REQUIRED')
    return dict(actual_time_pid=parent,actual_time_start_ticks=int(row[19]),supervisor_pid=planned['supervisor_pid'],supervisor_start_ticks=int(grand[19]),actual_time_cmdline_base64=base64.b64encode(actual).decode(),actual_argv=argv,planned_launch_line_sha256=hashlib.sha256(raw).hexdigest(),time_inode=sibling.st_ino,time_device=sibling.st_dev,actual_time_output_fds=held,external_POST_required=True)

class NativeOnce:
    def __init__(self,spec,folder,label,env,text,budget,journal,counts):
        self.spec=spec;self.folder=folder;self.label=label;self.env=env;self.text=text;self.budget=budget;self.journal=journal;self.counts=counts
        self.proc=None;self.raw={'stdout':bytearray(),'stderr':bytearray()};self.EOF={'stdout':False,'stderr':False};self.selector=selectors.DefaultSelector();self.closed=False;self.saved=False
        self.request_raw=(text+'\n').encode();self.request_sent=0;self.stdin_closed=False;self.start_ticks=None;self.pre_request=None;self.after_reap=None
        self.native=folder/(label+'.native.jsonl');self.command=[str(path(spec['ik_binary'])),str(self.native),'--env',env]
    def start(self):
        self.budget.check();inp=self.folder/(self.label+'.input.txt')
        with inp.open('xb')as f:f.write(self.request_raw);f.flush();os.fsync(f.fileno())
        self.counts['source_process_start_attempted']+=1;self.journal.add('source_process_start_attempted',label=self.label,command=self.command,input_sha256=sha(inp))
        mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            proc=subprocess.Popen(self.command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=ROOT,env=SOURCE_ENV,start_new_session=True)
            self.proc=proc;self.budget.processes.append(proc);self.counts['source_process_started']+=1
            row=stat_row(proc.pid);require(row is not None,'ACTUAL_SOURCE_STAT_REQUIRED');self.start_ticks=int(row[19]);proc.p4_start_ticks=self.start_ticks
            for key,stream in(('stdout',proc.stdout),('stderr',proc.stderr)):
                os.set_blocking(stream.fileno(),False);self.selector.register(stream,selectors.EVENT_READ,key)
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,mask)
        self.journal.add('source_process_started',pid=proc.pid,start_ticks=self.start_ticks,label=self.label,command=self.command)
        while True:
            self.budget.check();require(proc.poll()is None,'SOURCE_EXITED_BEFORE_UNIQUE_REQUEST')
            try:
                exe=Path('/proc',str(proc.pid),'exe').resolve();row=stat_row(proc.pid)
                if exe==path(self.spec['ik_binary']).resolve():break
            except FileNotFoundError:pass
            self.pump(.001)
        actual_cmd=Path('/proc',str(proc.pid),'cmdline').read_bytes();actual_env=Path('/proc',str(proc.pid),'environ').read_bytes()
        require(row is not None and int(row[1])==os.getpid() and int(row[2])==proc.pid and int(row[19])==self.start_ticks and sha(exe)==self.spec['ik_binary_sha256'],'ACTUAL_SOURCE_PID_GROUP_EXE_REQUIRED')
        require(actual_cmd.rstrip(b'\0').split(b'\0')==[v.encode()for v in self.command] and dict(x.decode().split('=',1)for x in actual_env.split(b'\0')if x)==SOURCE_ENV,'ACTUAL_SOURCE_ARGV_AND_ENV_REQUIRED')
        self.pre_request=dict(pid=proc.pid,start_ticks=self.start_ticks,parent_pid=os.getpid(),process_group=proc.pid,group=process_group_members(proc.pid),exe=str(exe),exe_sha256=sha(exe),cmdline_base64=base64.b64encode(actual_cmd).decode(),environment_base64=base64.b64encode(actual_env).decode())
        self.journal.add('actual_source_before_unique_request',label=self.label,proof=self.pre_request)
        os.set_blocking(proc.stdin.fileno(),False);self.counts['source_request_write_attempted']+=1
        self.request_sent=os.write(proc.stdin.fileno(),self.request_raw)
        require(self.request_sent==len(self.request_raw),'EXACT_FULL_SINGLE_REQUEST_WRITE_REQUIRED')
        self.counts['source_request_dispatched']+=1;proc.stdin.close();self.stdin_closed=True
    def pump(self,timeout):
        for key,_ in self.selector.select(timeout):
            try:data=os.read(key.fileobj.fileno(),65536)
            except BlockingIOError:continue
            if data:self.raw[key.data].extend(data)
            else:self.EOF[key.data]=True;self.selector.unregister(key.fileobj)
    def finish(self,normal):
        if self.closed:return
        if self.proc is None:self.selector.close();self.closed=True;return
        if not normal:kill_group(self.proc)
        deadline=time.monotonic()+.5
        while self.selector.get_map():
            if normal:self.budget.check()
            elif time.monotonic()>=deadline:break
            self.pump(.002)
        self.proc.wait(timeout=.5);self.after_reap=process_group_members(self.proc.pid)
        for stream in(self.proc.stdin,self.proc.stdout,self.proc.stderr):
            if stream is not None and not stream.closed:stream.close()
        self.selector.close();self.closed=True
        if normal:require(self.proc.returncode==0 and all(self.EOF.values()) and self.after_reap==[],'SUCCESS_EXIT_DUAL_EOF_EMPTY_SOURCE_GROUP_REQUIRED')
    def save(self):
        if self.saved:return
        for key,raw in self.raw.items():
            p=self.folder/(self.label+'.'+key+'.txt')
            with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
        self.journal.add('final_source_raw_streams',label=self.label,streams={k:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest(),base64=base64.b64encode(v).decode())for k,v in self.raw.items()},EOF=self.EOF)
        self.saved=True
    def registry(self):
        return dict(label=self.label,pid=None if self.proc is None else self.proc.pid,start_ticks=self.start_ticks,reaped=self.proc is not None and self.proc.returncode is not None,returncode=None if self.proc is None else self.proc.returncode,actual_before_unique_request=self.pre_request,actual_after_reap_group=self.after_reap,pipe_EOF=self.EOF,stdin_closed_after_unique_request=self.stdin_closed,request_bytes=len(self.request_raw),request_sent=self.request_sent,raw_saved=self.saved)

def active_p4():
    active=[]
    for name in Path('/proc').glob('[0-9]*/cmdline'):
        if int(name.parent.name)==os.getpid():continue
        try:parts=name.read_bytes().split(b'\0');exe=parts[0].decode(errors='replace')if parts else '';scripts=[p.decode(errors='replace')for p in parts[1:3]]if 'python'in exe else []
        except OSError:continue
        if '.p4_d079_dependency_audit/'in exe or any('/qualify_p4_full_r2_'in p or '/build_p4_full_r2_'in p for p in scripts):active.append(dict(pid=int(name.parent.name),command=b' '.join(parts).decode(errors='replace')))
    return active

def execute(protocol):
    begun=time.monotonic();cpu0=cpu();spec=load(protocol);commit=validate(spec,protocol,True);launch=supervisor_proof(spec,protocol)
    folder=ROOT/'results/p4_full'/RUN;claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXCLUSIVE_FIXED32_CLAIM_NO_RETRY');require(not active_p4(),'OTHER_ACTIVE_P4_EXECUTION')
    budget_guard=None;journal=None;sessions=[];counts=Counter();outcomes=[];error=None;diagnostics=[]
    record=dict(schema=SCHEMA,run_id=RUN,classification=LABEL,status='STOP_PREFIX_RETAINED',source_commit=commit,protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),budget=spec['budget'],supervision_engineering=spec['supervision_engineering'],supervisor_launch_proof=launch,external_supervision_qualified=False,independent_saved_POST_required=True,accounting_snapshot=spec['accounting_snapshot'],actual_charge_prior=spec['actual_charge_prior'],prior_execution_sha256=spec['actual_charge_prior']['execution_sha256'],bound_files_sha256=spec['bound_files_sha256'],collision_checked=False,full_RSS_qualified=False,independent_path_qualified=False,formal_table_I_calls=0,new_VI_candidate_constructions=0,zero_calls=spec['zero_calls'],solve_calls=0)
    def event(kind,**fields):journal.add(kind,**fields)
    def budget():budget_guard.check()
    def new(p,value):durable_new(p,value)
    def request(env,text,label,is_ik):
        budget();counts['IK_started'if is_ik else'source_F_started']+=1
        require(counts['IK_started']<=32 and counts['source_F_started']<=4,'FIXED32_CALL_CAP')
        session=NativeOnce(spec,folder,label,env,text,budget_guard,journal,counts);sessions.append(session)
        session.start();session.finish(normal=True);session.save()
        saved=session.native.read_bytes();raw=bytes(session.raw['stdout'])
        require(saved==raw and raw.endswith(b'\n') and len(raw.splitlines())==1,'EXACT_ONE_RAW_RESPONSE_STDOUT_NATIVE_MATCH')
        rows=[json.loads(line)for line in raw.splitlines()]
        require(rows[0]['schema']=='P4_SPATIAL_BATCH_V1' and rows[0]['environment']==env and rows[0]['error']is None and rows[0]['raw_input']==text and rows[0]['input_line']==1,'EXACT_ONE_RAW_RESPONSE_REQUIRED')
        counts['IK_completed'if is_ik else'source_F_completed']+=1
        if is_ik and rows[0]['success']:counts['IK_success_returned_with_internal_FK_completed']+=1
        event('dispatch_returned',label=label,raw_sha256=sha(session.native),response=rows[0]);budget();return rows[0]
    try:
        durable_new(claim,dict(schema='P4_R2_ABB_RSS_FIXED32_MATH01_SUPERVISED_V2_CLAIM',run_id=RUN,protocol=record['protocol'],protocol_sha256=record['protocol_sha256'],source_commit=commit,budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=Journal(folder/'evidence.jsonl');event('setup',record=record)
        budget_guard=Budget(begun,cpu0,spec);budget_guard.start();budget()
        # The original mathematical block is appended unchanged except for
        # explicit started/completed counters around its existing rank SVD.
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
            os.environ[key]='1'
        sys.path.insert(0,str(ROOT))
        import numpy as np
        from baselines.p4_full.geometry_consistent.physical_nr import arm_fk_jac, model_geometry, source_limits
        from scripts.recover_p4_full_r2_endpoints import branch_identity
        def independent(q6, env, arm):
            budget(); counts['independent_arm_FK_J_started']+=1; require(counts['independent_arm_FK_J_started']<=40,'FK_J_CAP')
            event('independent_arm_FK_J_started',q6=q6,environment=env,arm=arm)
            value=arm_fk_jac(q6,env,arm);counts['independent_arm_FK_J_completed']+=1
            event('independent_arm_FK_J_completed',call=counts['independent_arm_FK_J_completed']);budget();return value
        def rank(j):
            budget(); counts['rank_SVD_started']+=1;require(counts['rank_SVD_started']<=36,'RANK_SVD_CAP')
            scaled=j.copy();scaled[:3]/=1000
            sigma=np.linalg.svd(scaled,compute_uv=False)
            value=dict(rank=int(np.count_nonzero(sigma>sigma[0]*spec['gates']['rank_relative'])),
                        singular_values=sigma.tolist(),position_row_scaling='mm_to_m')
            counts['rank_SVD_completed']+=1;budget();return value
        def errors(a,b):
            d=a-b;return dict(position_maxabs_mm=float(np.max(np.abs(d[:3,3]))),rotation_maxabs=float(np.max(np.abs(d[:3,:3]))))
        def close(v):return v['position_maxabs_mm']<=1e-5 and v['rotation_maxabs']<=1e-5
        def fk_agrees(v):return v['position_maxabs_mm']<=1e-7 and v['rotation_maxabs']<=1e-10
        for case in spec['fixed_cases']:
            budget();env=case['environment'];q=case['q12_rad'];q1=q[:6];q2=q[6:]
            one,j1=independent(q1,env,1);two,j2=independent(q2,env,2)
            f=request(env,'F 1 '+' '.join(format(v,'.17g') for v in q1),case['case_id']+'_F1',False)
            require(f['op']=='F' and f['arm']==1 and f['q']==q1 and f['success'] and f['finite'], 'SOURCE_F1_INVALID')
            native1=np.asarray(f['T']);g=model_geometry(env)
            target=native1@g['grasps'][0]@np.diag([-1.,-1.,1.,1.])
            target_physical=one@g['grasps'][0]@np.diag([-1.,-1.,1.,1.])
            original=dict(case_id=case['case_id'],q12_rad=q,original_arm1_construction_branch=1,
                passive_branch_identity=branch_identity(q2,env,spec['gates']['branch_zero_relative_epsilon']),
                passive_rank=rank(j2),closure=errors(two,target_physical),source_F1_vs_independent=errors(native1,one),
                source_target=target.tolist(),physical_target=target_physical.tolist(),collision_saved_only=case['saved_collision'])
            new(folder/(case['case_id']+'.original_math.json'),original)
            for b in range(8):
                label=case['case_id']+'_arm2_b'+str(b)
                response=request(env,'K 2 '+str(b)+' '+' '.join(format(float(v),'.17g') for v in target.ravel()),label,True)
                require(response['op']=='K' and response['arm']==2 and response['branch']==b
                        and response['target']==target.tolist(),'FIXED_ARM2_BRANCH_OR_TARGET_CHANGED')
                row=dict(case_id=case['case_id'],passive_arm=2,requested_source_branch=b,
                    original_q12_rad=q,native_response=response,collision_checked=False,
                    collision_qualification='UNKNOWN_REQUIRES_SEPARATE_FROZEN_REPLAY',original_active_arm1_unchanged=True)
                if response['success']:
                    solved=response['solution'];require(response['finite'] and len(solved)==6 and all(math.isfinite(v)for v in solved),'NONFINITE_SOURCE_SUCCESS')
                    full=q1+solved;outpose,j=independent(solved,env,2);ident=branch_identity(solved,env,spec['gates']['branch_zero_relative_epsilon'])
                    delta=[x-y for x,y in zip(solved,q2)];closure=errors(outpose,target_physical);roundtrip=errors(outpose,target)
                    bounds=source_limits(env);qarr=np.asarray(full)
                    legality=bool(np.all((bounds[:,0]<=qarr)&(qarr<=bounds[:,1])))
                    membership=b in ident['branch_set'];r=rank(j)
                    fk_consistent=fk_agrees(errors(native1,one)) and fk_agrees(errors(np.asarray(response['T']),outpose))
                    row.update(output_q12_rad=full,passive_delta_rad=delta,raw_passive_L2_rad=math.sqrt(math.fsum(x*x for x in delta)),
                        same_original_passive_under_source_raw0p1=math.sqrt(math.fsum(x*x for x in delta))<.1,
                        branch_identity=ident,requested_branch_in_independent_set=membership,passive_rank=r,
                        closure=closure,physical_roundtrip=roundtrip,source_FK_vs_independent=errors(np.asarray(response['T']),outpose),
                        limits_legal=legality,qualified_math_only=close(closure)and close(roundtrip)and membership and legality and fk_consistent,
                        singular_math_only=close(closure)and close(roundtrip)and membership and legality and fk_consistent and r['rank']<6,
                        full_RSS_or_collision_qualified=False)
                else:row.update(qualified_math_only=False,singular_math_only=False,rejection='SOURCE_IK_FALSE_RETAINED')
                new(folder/(label+'.json'),row);outcomes.append(row)
                event('fixed_branch_finished',case_id=case['case_id'],branch=b,qualified_math_only=row['qualified_math_only'])
        require(counts['IK_started']==counts['IK_completed']==32 and len(outcomes)==32,'FIXED32_COMPLETION_REQUIRED')
        record['status']='FIXED32_MATH_RECORDED_COLLISION_UNKNOWN'
    except BaseException as exc:
        if budget_guard is not None:budget_guard.close()
        error=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc))
        if journal is not None:
            try:event('stopped',termination_reason=repr(exc))
            except BaseException as failure:diagnostics.append(dict(stage='stop_event',error=repr(failure)))
    finally:
        # Closing before any cleanup prevents asynchronous reentry. This does
        # not extend10/20: the outer live watchdog still owns the entire tail.
        if budget_guard is not None:budget_guard.close()
        for session in sessions:
            if session.proc is None:continue
            try:kill_group(session.proc)
            except BaseException as exc:diagnostics.append(dict(stage='kill',label=session.label,error=repr(exc)))
        for session in sessions:
            try:session.finish(normal=False)
            except BaseException as exc:diagnostics.append(dict(stage='central_drain_reap',label=session.label,error=repr(exc)))
            if session.proc is not None:
                try:kill_group(session.proc);session.proc.wait(timeout=.25);session.after_reap=process_group_members(session.proc.pid)
                except BaseException as exc:diagnostics.append(dict(stage='central_final_reap',label=session.label,error=repr(exc)))
            try:session.save()
            except BaseException as exc:diagnostics.append(dict(stage='raw_persistence',label=session.label,error=repr(exc)))
        record['source_process_registry']=[s.registry()for s in sessions]
        record['final_raw_streams']={s.label:{key:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode(),EOF=s.EOF[key])for key,raw in s.raw.items()}for s in sessions}
        raw_gate=bool(len(sessions)==counts['source_process_started'] and all(s.proc is not None and s.proc.returncode==0 and s.closed and s.saved and s.after_reap==[] and all(s.EOF.values()) and s.stdin_closed and s.request_sent==len(s.request_raw) for s in sessions))
        record['complete_source_raw_evidence_gate']=raw_gate
        if record['status']=='FIXED32_MATH_RECORDED_COLLISION_UNKNOWN' and not(raw_gate and len(sessions)==36 and counts['source_F_started']==counts['source_F_completed']==4 and counts['source_request_dispatched']==36):record['status']='STOP_PROCESS_RAW_LIFECYCLE_UNQUALIFIED'
        after={}
        for name,want in spec['bound_files_sha256'].items():
            try:
                after[name]=sha(name)
                if after[name]!=want:diagnostics.append(dict(stage='bound_hash',path=name,error='CHANGED'))
            except BaseException as exc:diagnostics.append(dict(stage='bound_hash',path=name,error=repr(exc)))
        record['bound_files_after_sha256']=after
        for field,p in(('protocol',protocol),('claim',claim)):
            try:
                record[field+'_after_sha256']=sha(p)
                require(record[field+'_after_sha256']==record.get(field+'_sha256'),'FROZEN_FILE_CHANGED '+field)
            except BaseException as exc:diagnostics.append(dict(stage='mandatory_hash',field=field,error=repr(exc)))
        try:
            prior=current_prior();record['actual_charge_prior_after']=prior;record['prior_execution_after_sha256']=prior['execution_sha256']
            require(prior==spec['actual_charge_prior'],'LATEST_PRIOR_CHANGED')
        except BaseException as exc:diagnostics.append(dict(stage='prior_hashes',error=repr(exc)))
        record.update(counts=dict(counts),branch_results_retained=len(outcomes),uncompleted_branch_ids=[c['case_id']+'_arm2_b'+str(b)for c in spec['fixed_cases']for b in range(8)if not any(r['case_id']==c['case_id']and r['requested_source_branch']==b for r in outcomes)],IK_internal_FK_started='UNOBSERVED_NO_INTERNAL_TRACE',IK_internal_FK_completed_from_returned_success=counts['IK_success_returned_with_internal_FK_completed'],interrupted_IK_internal_FK='UNKNOWN_NOT_INFERRED_FROM_CAP'if counts['IK_started']!=counts['IK_completed']else 'NO_INTERRUPTED_TOP_LEVEL_IK',math_gate_scope='MATH_ONLY; NEW_OUTPUT_COLLISION_UNKNOWN; NOT_RSS_RBS_OR_PLANNING_QUALIFICATION')
        if journal is not None:
            try:
                event('final_counts',counts=dict(counts),diagnostics=diagnostics);journal.finish()
                record['evidence_journal']=str(journal.p.relative_to(ROOT));record['evidence_journal_sha256']=sha(journal.p)
            except BaseException as exc:diagnostics.append(dict(stage='final_journal',error=repr(exc)))
        record['diagnostics']=diagnostics
        processes=[s.proc for s in sessions if s.proc is not None]
        record.update(wall_s=time.monotonic()-begun,cpu_s=cpu()-cpu0+live_cpu(processes))
        if record['wall_s']>=10. or record['cpu_s']>=20.:record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        persistence_error=None
        if folder.is_dir():
            try:durable_new(folder/'execution.json',record)
            except BaseException as exc:persistence_error=repr(exc)
            # An independent terminal receipt is attempted even when execution
            # hashing/persistence failed; outer charge preserves killed tails.
            receipt=dict(schema='P4_R2_ABB_RSS_FIXED32_SUPERVISED_V2_COST_RECEIPT',run_id=RUN,status=record['status'],execution_sha256=None,execution_persistence_error=persistence_error,wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=cpu()-cpu0+live_cpu(processes),last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            try:
                if(folder/'execution.json').is_file():receipt['execution_sha256']=sha(folder/'execution.json')
            except BaseException as exc:receipt['execution_hash_error']=repr(exc)
            if receipt['wall_s_through_execution_persistence']>=10. or receipt['cpu_s_through_execution_persistence']>=20.:receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            if persistence_error is not None:receipt['status']='STOP_EXECUTION_PERSISTENCE_ERROR'
            try:durable_line(folder/'cost_receipt.jsonl',receipt)
            except BaseException as exc:
                # The already-running independent supervisor retains the
                # actual GNUtime exit/cost even if this final receipt fails.
                receipt['status']='STOP_TERMINAL_RECEIPT_PERSISTENCE_ERROR'
                print(json.dumps(dict(status=receipt['status'],error=repr(exc))),file=sys.stderr)
            record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),external_supervision_qualified=False,full_RSS_qualified=False,formal_table_I_calls=0)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status')=='FIXED32_MATH_RECORDED_COLLISION_UNKNOWN','FIXED32_COMPLETION_NOT_QUALIFIED')

def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_DRAFT_VALIDATED_NO_SCIENCE');return
    execute(protocol)

if __name__=='__main__':main()
