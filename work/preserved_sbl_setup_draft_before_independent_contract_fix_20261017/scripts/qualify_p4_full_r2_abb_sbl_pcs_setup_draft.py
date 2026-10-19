#!/usr/bin/env python3
"""Future single SBL setup observation draft. No import-time effects.

Only stdlib imports. Rejects protocol description before real successful build
and independent external POST. No compile, solve or independent model query.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import selectors
import signal
import struct
import subprocess
import time
ROOT=Path(__file__).resolve().parents[1]
RUN='20261017_R2_ABB_SBL_PCS_SETUP01'
CLAIM='P4_R2_ABB_SBL_PCS_SETUP01_II_A01_SEED7_PUBLIC13_ONCE_10W_20CPU_20261017'
LABEL='R2_RECONSTRUCTED_A01_ORIGINAL_SBL_PCS_SETUP_PUBLIC_LINEAR_ACTION_OBSERVATION_ONLY'
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_sbl_pcs_v1')
STAGE=BUILD/'geometry_consistent_observed'
BINARY=STAGE/'p4_abb_sbl_pcs'
BUILD_RUN='20261017_R2_ABB_SBL_PCS_BUILD01'
PRE='reports/P4_FULL_R2_ABB_SBL_PCS_SETUP_INTERFACE_PRE_DRAFT_20261017.md'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_sbl_pcs_setup_draft.py'
LIBRARY_EVIDENCE='reports/P4_FULL_R2_ABB_SBL_PCS_ACTUAL_LIB_LINEAR_PROJECT_STATIC_EVIDENCE_20261017.md'
LIBRARY_EVIDENCE_SHA='788dad1f7eda728078699f271b949204e3689d8714c4765a40355f9f87a9d535'
OMPL=Path('/opt/ros/humble/lib/x86_64-linux-gnu/libompl.so.1.7.0')
OMPL_SHA='25e9cbdc7c1c3b1e7c56221e954e72c4f5cb96e6c45253631773655cac71499e'
LINEAR_SYMBOL='_ZNK4ompl4base35RealVectorLinearProjectionEvaluator7projectEPKNS0_5StateEN5Eigen3RefINS5_6MatrixIdLin1ELi1ELi0ELin1ELi1EEELi0ENS5_11InnerStrideILi1EEEEE'
MATRIX_SYMBOL='_ZNK4ompl4base16ProjectionMatrix7projectEPKdN5Eigen3RefINS4_6MatrixIdLin1ELi1ELi0ELin1ELi1EEELi0ENS4_11InnerStrideILi1EEEEE'
SYMBOLS=(LINEAR_SYMBOL,MATRIX_SYMBOL)
ENDPOINTS={
 'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_0.json':'b39d945cd5d49e4649aba22e57aae9f302694e4d8e0880389542f1ad828b112f',
 'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_1.json':'991c2efe8e68add65c17375d89c89bbb637711d7125b15a34c84a19a2dc15430',
}
HEADER_SHA={
 '/opt/ros/humble/include/ompl-1.7/ompl/base/ProjectionEvaluator.h':'e6d38f478826365f110fee87e0bca58ab20686a354d91f98a1c391ada0c7ea4d',
 '/opt/ros/humble/include/ompl-1.7/ompl/base/spaces/RealVectorStateProjections.h':'34fc567e726e8cafef27e1169c60b90d21e0f2091c1461919220120535ed9ead',
}
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),PRE,SUPERVISOR,LIBRARY_EVIDENCE]
THREADS={k:'1'for k in('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
SOURCE_ENV={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LD_BIND_NOW':'1',**THREADS}
MARKER=b'P4_SBL_PCS_TRACE '
def require(ok,reason):
    if not ok:raise RuntimeError(reason)
def path(value):
    p=Path(value);return p if p.is_absolute()else ROOT/p
def sha(value):return hashlib.sha256(path(value).read_bytes()).hexdigest()
def load(value):return json.loads(path(value).read_text())
def exact(a,b):return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,allow_nan=False,separators=(',',':'))
def durable_new(value,record):
    with path(value).open('xb')as stream:
        stream.write(json.dumps(record,ensure_ascii=False,allow_nan=False,indent=2).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
def utc():return dt.datetime.now(dt.timezone.utc).isoformat()

def own_reaped_cpu():
    own=resource.getrusage(resource.RUSAGE_SELF);child=resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime+own.ru_stime+child.ru_utime+child.ru_stime

def stat_row(pid):
    try:return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
    except (OSError,ValueError,IndexError):return None

def direct_live_cpu(processes):
    total=0.
    for proc in processes:
        if proc.returncode is not None:continue # already reaped and included above
        row=stat_row(proc.pid)
        if row is not None:total+=sum(int(row[i])for i in (11,12,13,14))/os.sysconf('SC_CLK_TCK')
    return total

def process_group_members(pgid):
    rows=[]
    for name in Path('/proc').glob('[0-9]*/stat'):
        try:
            row=name.read_text().rsplit(')',1)[1].split()
            if int(row[2])==pgid:rows.append(dict(pid=int(name.parent.name),ppid=int(row[1]),pgrp=int(row[2])))
        except (OSError,ValueError,IndexError):pass
    return sorted(rows,key=lambda r:r['pid'])

class Budget:
    def __init__(self,spec,started,cpu_start):
        self.started=started;self.cpu_start=cpu_start;self.processes=[]
        self.wall_cap=min(10.,3600.-spec['previous_r2_wall_s']);self.cpu_cap=min(20.,7200.-spec['previous_r2_cpu_s'])
        require(min(self.wall_cap,self.cpu_cap)>0,'SBL_SETUP_TOTAL_BUDGET_EXHAUSTED')
        self.previous=signal.getsignal(signal.SIGALRM)
        require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
        self.closed=False;self.closing=False
    def start(self):
        # The owner stores this Budget before enabling asynchronous exceptions.
        signal.signal(signal.SIGALRM,self.alarm);signal.setitimer(signal.ITIMER_REAL,.02,.02)
    def alarm(self,*_):
        if not self.closing:self.check()
    def check(self):
        if time.monotonic()-self.started>=self.wall_cap:raise TimeoutError('SBL_SETUP_AGGREGATE_HARD_WALL_CAP')
        if own_reaped_cpu()-self.cpu_start+direct_live_cpu(self.processes)>=self.cpu_cap:raise TimeoutError('SBL_SETUP_SELF_REAPED_AND_REGISTERED_LIVE_CPU_CAP')
    def remaining(self):
        self.check();return min(self.wall_cap-(time.monotonic()-self.started),self.cpu_cap-(own_reaped_cpu()-self.cpu_start+direct_live_cpu(self.processes)))
    def close(self):
        if self.closed:return
        self.closing=True
        previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            signal.setitimer(signal.ITIMER_REAL,0)
            # Consume our pending alarm before restoring the pre-run handler.
            while signal.SIGALRM in signal.sigpending():signal.sigwait({signal.SIGALRM})
            signal.signal(signal.SIGALRM,self.previous);self.closed=True
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)

class Journal:
    def __init__(self,name):self.stream=name.open('xb',buffering=0)
    def add(self,event,**fields):
        raw=json.dumps(dict(event=event,at_utc=utc(),**fields),allow_nan=False,separators=(',',':')).encode()+b'\n'
        require(self.stream.write(raw)==len(raw),'JOURNAL_INCOMPLETE_WRITE_NO_RETRY');self.stream.flush()
    def finish(self):
        self.stream.flush();os.fsync(self.stream.fileno());self.stream.close()

class Session:
    def __init__(self,target,work,budget,journal,counts):
        self.target=target;self.budget=budget;self.journal=journal;self.counts=counts;self.proc=None
        self.selector=selectors.DefaultSelector();self.raw={'stdout':bytearray(),'stderr':bytearray()}
        self.pending=b'';self.responses=[];self.eof=False;self.closed=False;self.startup_complete=False;self.close_group=None
        self.command=[target['binary'],'II',str(work),'setup']
        self.start_ticks=None;self.pipe_EOF_observed={'stdout':False,'stderr':False};self.after_reap_group=None
        self.request_raw=None;self.request_sent=None;self.stdin_closed_after_request=False;self.close_poll_result=None;self.close_postpoll_group=None;self.close_poll_observations=[];self.loaded_scope=None
    def start(self):
        previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            def limits():
                signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask);resource.setrlimit(resource.RLIMIT_CPU,(20,20))
            self.counts['source_process_start_attempted']+=1;self.journal.add('source_process_start_attempted',command=self.command)
            self.proc=subprocess.Popen(self.command,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                bufsize=0,start_new_session=True,preexec_fn=limits,env=SOURCE_ENV)
            self.budget.processes.append(self.proc);self.counts['source_process_started']+=1
            row=stat_row(self.proc.pid);require(row is not None and int(row[2])==self.proc.pid,'ACTUAL_REGISTERED_SOURCE_STAT_REQUIRED')
            self.start_ticks=int(row[19]);require(self.start_ticks>0,'ACTUAL_SOURCE_START_TICKS_REQUIRED')
            self.journal.add('source_process_started',pid=self.proc.pid,start_ticks=self.start_ticks,command=self.command)
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
        self.budget.check();self.register_pipes();group=process_group_members(self.proc.pid)
        require([r['pid']for r in group]==[self.proc.pid],'UNEXPECTED_SOURCE_START_GROUP')
        row=stat_row(self.proc.pid);require(row is not None and int(row[19])==self.start_ticks,'SOURCE_PID_IDENTITY_CHANGED_AT_START')
        self.journal.add('source_start_group',members=group,actual_start_ticks=int(row[19]));self.startup_complete=True
        self.loaded_scope=loaded_scope(self.proc,self.budget,self.journal)
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
            if not raw:
                self.pipe_EOF_observed[key.data]=True;self.selector.unregister(key.fileobj)
                self.journal.add('actual_pipe_EOF_observed',channel=key.data);continue
            self.raw[key.data].extend(raw)
            if key.data=='stdout':self.pending+=raw
            self.journal.add('raw_pipe_chunk',channel=key.data,bytes=len(raw),base64=base64.b64encode(raw).decode())
        if enforce:self.budget.check()
    def query(self,request):
        self.budget.check();raw=json.dumps(request,allow_nan=False,separators=(',',':')).encode()+b'\n'
        self.request_raw=raw;self.journal.add('setup_request_exact_bytes',request=request,bytes=len(raw),
            base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest())
        require(len(raw)<4096 and self.proc.poll()is None,'SOURCE_NOT_READY_FOR_EXACT_REQUEST')
        self.counts['setup_dispatch_attempted']+=1
        try:
            self.request_sent=os.write(self.proc.stdin.fileno(),raw)
            require(self.request_sent==len(raw),'INCOMPLETE_REQUEST_NO_RETRY')
            self.counts['setup_dispatched']+=1
        finally:
            # The source waits for EOF before setup. Close even after a failed
            # single write; cleanup never sends a retry or second request.
            if self.proc.stdin and not self.proc.stdin.closed:self.proc.stdin.close()
            self.stdin_closed_after_request=True
            self.journal.add('single_request_write_and_stdin_close',actual_sent=self.request_sent,
                sent_bytes_base64=None if self.request_sent is None else base64.b64encode(raw[:self.request_sent]).decode(),
                sent_sha256=None if self.request_sent is None else hashlib.sha256(raw[:self.request_sent]).hexdigest(),
                exact_full_request_written=self.request_sent==len(raw),stdin_closed=self.proc.stdin.closed)
        while b'\n'not in self.pending:
            self.pump();require(bool(self.selector.get_map())or b'\n'in self.pending,'EOF_WITHOUT_RESPONSE')
        line,self.pending=self.pending.split(b'\n',1);rawline=line+b'\n';self.counts['stdout_complete_lines_observed']+=1
        self.journal.add('raw_response_line',bytes=len(rawline),base64=base64.b64encode(rawline).decode())
        require(line.startswith(b'{'),'UNKNOWN_STDOUT_PREFIX_NO_SKIP')
        response=json.loads(line);self.counts['raw_response_lines_observed']+=1;self.responses.append(response);return response
    def finish(self,normal):
        if self.closed:return
        try:
            if self.proc is not None:
                self.register_pipes()
                if normal:
                    self.close_group=process_group_members(self.proc.pid)
                    self.close_poll_result=self.proc.poll();self.close_poll_observations.append(self.close_poll_result)
                    ids=[r['pid']for r in self.close_group]
                    if ids==[self.proc.pid]and self.close_poll_result is None:
                        row=stat_row(self.proc.pid)
                        if row is None or int(row[19])!=self.start_ticks:
                            # A source can finish between poll and /proc read.
                            # One actual re-poll may enter only the reviewed
                            # exit0+empty-group alternative, never infer success.
                            self.close_poll_result=self.proc.poll();self.close_poll_observations.append(self.close_poll_result)
                            self.close_postpoll_group=process_group_members(self.proc.pid)
                            require(self.close_poll_result==0 and self.close_postpoll_group==[],
                                'VANISHED_OR_CHANGED_SOURCE_REQUIRES_ACTUAL_EXIT0_AND_EMPTY_GROUP')
                    else:
                        self.close_postpoll_group=process_group_members(self.proc.pid)
                        require(ids in([], [self.proc.pid])and self.close_poll_result==0 and self.close_postpoll_group==[],
                            'EXITED_SOURCE_REQUIRES_ACTUAL_POLL_EXIT0_AND_ACTUAL_EMPTY_GROUP')
                    require(self.stdin_closed_after_request and self.proc.stdin.closed,'STDIN_MUST_CLOSE_AFTER_UNIQUE_WRITE')
                    self.journal.add('source_close_group',members=self.close_group,actual_poll_result=self.close_poll_result,actual_poll_observations=self.close_poll_observations,actual_postpoll_group=self.close_postpoll_group,start_ticks=self.start_ticks)
                    deadline=time.monotonic()+self.budget.remaining()
                else:kill_source_group(self.proc);deadline=time.monotonic()+2.
                while self.selector.get_map()and time.monotonic()<deadline:self.pump(.01,enforce=normal)
                try:self.proc.wait(timeout=max(.001,deadline-time.monotonic()))
                except subprocess.TimeoutExpired:kill_source_group(self.proc);self.proc.wait(timeout=1.)
                while self.selector.get_map()and time.monotonic()<deadline:self.pump(0.,enforce=False)
                self.eof=all(self.pipe_EOF_observed.values())and not self.selector.get_map()
                self.after_reap_group=process_group_members(self.proc.pid)
                self.journal.add('source_after_reap_group',members=self.after_reap_group,returncode=self.proc.returncode,
                    actual_pipe_EOF_observed=self.pipe_EOF_observed,start_ticks=self.start_ticks)
                require(not self.after_reap_group,'ACTUAL_SOURCE_GROUP_MUST_BE_EMPTY_AFTER_REAP')
                for stream in(self.proc.stdin,self.proc.stdout,self.proc.stderr):
                    if stream is not None and not stream.closed:stream.close()
            self.selector.close();self.closed=True
            if normal:require(self.eof and not self.pending and self.proc.returncode==0,'SOURCE_ACTUAL_DUAL_EOF_TAIL_OR_EXIT_FAILED')
        except BaseException:
            # Leave the selector usable for the central failure drain.
            raise


def kill_source_group(proc):
    group=process_group_members(proc.pid)
    if group:
        try:os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    if proc.poll()is None:proc.kill()

def supervisor_proof(spec,protocol):
    ext=spec['external_supervision'];metadata=path(ext['metadata_path'])
    planned_raw=metadata.read_bytes().splitlines(keepends=True)[0];planned=json.loads(planned_raw)
    parent=os.getppid();row=stat_row(parent)
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

def preload_state():
    p=Path('/etc/ld.so.preload')
    require(not p.exists()or p.is_file()and not p.read_bytes().strip(),'SYSTEM_PRELOAD_MUST_BE_ABSENT_OR_EMPTY')
    return dict(path=str(p),exists=p.exists(),sha256=sha(p)if p.exists()else None)

def symbol_definitions(filename):
    """Read ELF64 little-endian x86-64 dynsym bytes; never load the file."""
    raw=Path(filename).read_bytes();require(len(raw)>=64 and raw[:6]==b'\x7fELF\x02\x01','ACTUAL_ELF64_LE_REQUIRED')
    h=struct.unpack_from('<16sHHIQQQIHHHHHH',raw)
    require(h[2]==62 and h[11]==64 and 0<h[12]<65535,'NORMAL_X86_64_SECTION_TABLE_REQUIRED')
    require(h[6]+h[11]*h[12]<=len(raw),'COMPLETE_ELF_SECTION_TABLE_REQUIRED')
    sections=[struct.unpack_from('<IIQQQQIIQQ',raw,h[6]+i*h[11])for i in range(h[12])]
    found={n:[]for n in SYMBOLS}
    for section in sections:
        if section[1]!=11:continue
        require(section[9]==24 and section[5]%24==0 and section[4]+section[5]<=len(raw)and section[6]<len(sections),'COMPLETE_DYNSYM_REQUIRED')
        names=sections[section[6]];require(names[1]==3 and names[4]+names[5]<=len(raw),'BOUND_DYNSTR_REQUIRED')
        strings=raw[names[4]:names[4]+names[5]]
        for off in range(section[4],section[4]+section[5],24):
            name,info,other,ndx,value,size=struct.unpack_from('<IBBHQQ',raw,off)
            require(name<len(strings),'DYNSYM_NAME_IN_BOUNDS_REQUIRED');end=strings.find(b'\0',name);require(end>=0,'TERMINATED_DYNSYM_NAME_REQUIRED')
            text=strings[name:end].decode('ascii',errors='strict')
            if text in found and ndx!=0 and info>>4 in(1,2)and other&3 in(0,3):
                found[text].append(dict(value=value,size=size,binding=info>>4,type=info&15,visibility=other&3))
    return found

def loaded_scope(proc,budget,journal):
    # Driver waits for the sole request+EOF before constructing any model.
    previous=None;observed=None
    while observed is None:
        budget.check();require(proc.poll()is None,'SOURCE_EXITED_BEFORE_LOADED_SCOPE_OBSERVATION')
        try:
            exe=Path('/proc',str(proc.pid),'exe').resolve()
            raw=Path('/proc',str(proc.pid),'maps').read_bytes();mapped=set()
            for line in raw.decode().splitlines():
                fields=line.split(maxsplit=5)
                if len(fields)==6 and fields[5].startswith('/'):
                    require(not fields[5].endswith(' (deleted)'),'DELETED_LOADED_ELF_REFUSED');mapped.add(Path(fields[5]).resolve())
            signature=(exe,tuple(sorted(str(p)for p in mapped)))
            if exe==BINARY.resolve()and OMPL.resolve()in mapped and signature==previous:observed=(raw,mapped)
            previous=signature
        except FileNotFoundError:pass
        if observed is None:time.sleep(.002)
    raw,mapped=observed;envraw=Path('/proc',str(proc.pid),'environ').read_bytes()
    env=dict(x.decode().split('=',1)for x in envraw.split(b'\0')if x)
    journal.add('actual_loaded_scope_raw_before_gates',actual_exe=str(exe),maps_bytes_base64=base64.b64encode(raw).decode(),
        maps_sha256=hashlib.sha256(raw).hexdigest(),actual_environment=env,environment_sha256=hashlib.sha256(envraw).hexdigest())
    require(env==SOURCE_ENV and sha(exe)==sha(BINARY)and sha(OMPL)==OMPL_SHA,'ACTUAL_SOURCE_EXE_LIBRARY_AND_SANITIZED_ENV_REQUIRED')
    exports={n:[]for n in SYMBOLS};files={}
    for filename in sorted(mapped):
        budget.check();files[str(filename)]=sha(filename)
        if filename.read_bytes()[:4]!=b'\x7fELF':continue
        definitions=symbol_definitions(filename)
        for name,rows in definitions.items():
            if rows:exports[name].append(dict(file=str(filename),definitions=rows))
    journal.add('actual_loaded_symbol_candidates_before_gates',mapped_files_sha256=files,project_symbol_providers=exports)
    for name,rows in exports.items():
        require(len(rows)==1 and rows[0]['file']==str(OMPL.resolve())and len(rows[0]['definitions'])==1,'UNIQUE_ACTUAL_LOADED_OMPL_PROJECT_SYMBOL_PROVIDER_REQUIRED '+name)
    result=dict(scope='STATIC_AND_PRE_REQUEST_LOADED_SYMBOL_SCOPE_NOT_RUNTIME_GOT_ADDRESS_READ',
        actual_exe=str(exe),actual_exe_sha256=sha(exe),actual_environment=env,environment_sha256=hashlib.sha256(envraw).hexdigest(),
        maps_sha256=hashlib.sha256(raw).hexdigest(),maps_bytes_base64=base64.b64encode(raw).decode(),
        mapped_files_sha256=files,project_symbol_providers=exports,LD_BIND_NOW='1',protected_matrix_storage_read=False)
    journal.add('actual_loaded_project_symbol_scope',observation=result);return result

def build_assets(post_name):
    post_path=path(post_name).resolve();require(post_path.is_relative_to(ROOT/'reports'),'SAVED_BUILD_POST_WITHIN_REPORTS_REQUIRED')
    execution=ROOT/'results/p4_full'/BUILD_RUN/'execution.json';manifest=BUILD/'manifest.json'
    require(execution.is_file()and manifest.is_file()and post_path.is_file(),'WAIT_REAL_BUILD_AND_PERSONNEL_INDEPENDENT_POST_NO_PLACEHOLDER_PROTOCOL')
    e=load(execution);m=load(manifest);post=load(post_path)
    require(e['schema']=='P4_R2_ABB_SBL_PCS_ENGINEERING_EXECUTION_V4'and e['run_id']==BUILD_RUN
        and e['status']=='BUILT_NOT_QUERIED'and e['exit_code']==0 and e['compiler_reaped']is True
        and e['compiler_group_members_after_cleanup']==[]and e['diagnostics']==[]
        and e['query_calls']==e['solve_calls']==e['binary_execution_calls']==e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0,'REAL_SUCCESSFUL_SBL_COMPILER_ONLY_BUILD_REQUIRED')
    require(m==dict(e,engineering_execution=str(execution.relative_to(ROOT)))and e['binary']==str(BINARY),'EXACT_ACTUAL_SBL_MANIFEST_REQUIRED')
    require(post['personnel_independent']is True and post['engineering_build_qualified']is True and post['external_supervision_qualified']is True
        and isinstance(post['schema'],str)and post['status'].startswith('PASS')and post['checks_total']==post['checks_passed']>0
        and post['checks_failed']==0 and post['failures']==[],'REAL_INDEPENDENT_BUILD_POST_MUST_PASS')
    files={str(execution.relative_to(ROOT)):sha(execution),str(manifest):sha(manifest),str(post_path.relative_to(ROOT)):sha(post_path)}
    for field,filename in(('execution',execution),('manifest',manifest),('protocol',path(e['protocol'])),('claim',path(e['claim']))):
        require(path(post[field]).resolve()==filename.resolve()and post[field+'_sha256']==sha(filename),'EXACT_BUILD_POST_LINK_REQUIRED '+field)
        files[str(filename)]=sha(filename)
    external=ROOT/'results/p4_full'/(BUILD_RUN+'.supervision.charge.json');internal=execution.parent/'cost_receipt.json'
    for field,filename in(('receipt',external),('internal_receipt',internal)):
        require(path(post[field]).resolve()==filename.resolve()and post[field+'_sha256']==sha(filename),'EXACT_BUILD_RECEIPT_LINK_REQUIRED '+field);files[str(filename)]=sha(filename)
    ex=load(external);inside=load(internal)
    require(ex['execution_sha256']==sha(execution)and ex['receipt_sha256']==sha(internal)and ex['timing_valid']is True
        and ex['time_inode_unchanged']is True and ex['wall_CPU_caps_pass']is True and ex['completed_process_exit0']is True
        and inside['execution_sha256']==sha(execution)and inside['status']=='BUILT_NOT_QUERIED','BUILD_REAL_EXTERNAL_CHARGE_REQUIRED')
    require(e['bound_files_after_sha256']==e['bound_files_sha256']and e['compiled_source_after_sha256']==e['compiled_source_sha256']
        and e['mesh_after_sha256']==e['mesh_sha256']and e['preserved_source_after_sha256']==e['preserved_source_sha256']
        and e['compiler_dependency_files_after_sha256']==e['compiler_dependency_files_sha256']
        and len(e['compiler_dependency_rule_bindings'])==len(e['actual_dependency_translation_units'])==len(e['compiler_dependency_files_sha256'])==5
        and all(row['compiler_created_individual_d_file']is False for row in e['compiler_dependency_rule_bindings'])and e['unfrozen_protected_dependencies']==[],
        'ACTUAL_COMPLETE_FIVE_TU_SOURCE_DEPENDENCY_AND_ASSET_GATE_REQUIRED')
    files.update(e['bound_files_sha256']);files.update(post['retained_sha256'])
    files[e['compiler_dependency_stdout']]=e['compiler_dependency_stdout_sha256'];files[e['binary']]=e['binary_sha256']
    for field,prefix in(('compiled_source_sha256',STAGE),('mesh_sha256',STAGE),('preserved_source_sha256',STAGE/'preserved_originals'),('compiler_dependency_files_sha256',STAGE)):
        for name,want in e[field].items():files[str(prefix/name)]=want
    for name,want in files.items():require(sha(name)==want,'BOUND_BUILD_OR_POST_ASSET_CHANGED '+name)
    return dict(execution=str(execution.relative_to(ROOT)),execution_sha256=sha(execution),manifest=str(manifest),manifest_sha256=sha(manifest),
        personnel_independent_POST=str(post_path.relative_to(ROOT)),personnel_independent_POST_sha256=sha(post_path),
        target=dict(stage=str(STAGE),binary=str(BINARY)),files_sha256=files)

def draft_protocol(post_name):
    built=build_assets(post_name);prior=current_prior();points=[]
    low=[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2;high=[2.88,1.919,1.22,2.79,2.09,3.1416]*2
    for name,want in ENDPOINTS.items():
        require(sha(name)==want,'ORIGINAL_FROZEN_A01_ENDPOINT_CHANGED');e=load(name);q=e['selected_q_rad']
        require(e['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'and e['source_policy_collision_qualified']is True
            and len(q)==12 and all(type(x)in(int,float)and math.isfinite(x)and a<=x<=b for x,a,b in zip(q,low,high)),'FROZEN_A01_ENDPOINT_REQUIRED')
        points.append(q)
    require(sha(LIBRARY_EVIDENCE)==LIBRARY_EVIDENCE_SHA and sha(OMPL)==OMPL_SHA,'EXACT_REVIEWED_LIBRARY_EVIDENCE_REQUIRED')
    for name,want in HEADER_SHA.items():require(sha(name)==want,'REVIEWED_LINEAR_HEADER_CHANGED')
    meshes={str(p):sha(p)for p in sorted((STAGE/'simulator').glob('*.tris'))};require(len(meshes)==20,'EXACT20_NATIVE_MESHES_REQUIRED')
    bound={**built['files_sha256'],**ENDPOINTS,**HEADER_SHA,**meshes,str(OMPL):OMPL_SHA,
        prior['ledger']:prior['ledger_sha256'],**{n:sha(n)for n in OWN},'/usr/bin/time':sha('/usr/bin/time'),
        '/usr/bin/python3':sha('/usr/bin/python3'),'/etc/ld.so.cache':sha('/etc/ld.so.cache')}
    return dict(schema='P4_R2_ABB_SBL_PCS_SINGLE_SETUP_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,latest_actual_charged_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,build_assets=built,actual_charge_prior=prior,
        request=dict(operation='setup',environment='II',seed=7,separately_frozen_setup_qualification=True,start_q12=points[0],goal_q12=points[1]),
        runtime_meshes_sha256=meshes,own_source_sha256={n:sha(n)for n in OWN},bound_files_sha256=bound,
        prior_execution_sha256=prior['execution_sha256'],previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],
        budget=dict(wall_s=10.,cpu_s=20.,child_cpu_limit_s=20,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        maxima=dict(new_source_processes=1,source_requests=1,setup_calls=1,public_project_calls=13,solve_calls=0,seed=7),
        source_environment=SOURCE_ENV,system_preload_state=preload_state(),
        output_contract='Exactly1 response, sole write+stdinEOF, actual stdout/stderr EOF and empty reaped process group; full raw stdout/stderr plus traces and loaded maps retained.',
        external_supervision=dict(required=True,sibling_path='results/p4_full/'+RUN+'.supervision.time.txt',format='%e %U %S %x',
            metadata_path='results/p4_full/'+RUN+'.supervision.jsonl',stderr_path='results/p4_full/'+RUN+'.supervision.stderr.log',charge_path='results/p4_full/'+RUN+'.supervision.charge.json',
            time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'),elapsed_decimal_upper_padding_s=.01,
            CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True),
        observer_scope='Existing actual exact linear/random-linear class, public(0,e0..e11) fixed13; projection/grid metadata and binary64. No protected storage; setup internal RNG UNOBSERVED.',
        source_policy='Original SBL setup sequence and default automatic maxDistance; constructor original native1 Range=.8 only, no advance setRange. No solve, no new FK/IK/RBS/collision queries.',
        zero_calls=dict(compile=0,solve=0,independent_model_queries=0,old_component_requery=0,VI_constructions=0,formal_table_I=0,independent_path_qualification=0),
        no_retry_reset_resume=True)

def validate(spec,protocol,execute=False):
    expected=draft_protocol(spec['build_assets']['personnel_independent_POST'])
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_SETUP_RECIPE_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_SETUP_REVIEW_FIELDS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'SETUP_INDEPENDENT_REVIEW_ROOT_COMMIT_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in[*OWN,str(protocol.relative_to(ROOT))]:
        require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),'UNCOMMITTED_SETUP_SOURCE_OR_PROTOCOL '+name)
    return commit

def binary64(values):return ''.join(struct.pack('>d',float(x)).hex()for x in values)
def finite_vector(values,size):
    return isinstance(values,list)and len(values)==size and all(type(x)in(int,float)and math.isfinite(x)for x in values)
def raw_trace(raw):
    rows=[]
    for line in raw.splitlines(keepends=True):
        if MARKER in line:
            require(line.endswith(b'\n'),'INCOMPLETE_RAW_SBL_TRACE_LINE');rows.append(json.loads(line.split(MARKER,1)[1]))
    return rows
def check_response(response,spec):
    require(response['schema']=='P4_ABB_SBL_PCS_SETUP_TRANSPORT_DRAFT_V1'and response['status']=='SOURCE_SETUP_OBSERVED_NOT_RUNTIME_QUALIFIED'
        and response['operation']=='setup'and exact(response['request'],spec['request'])and response['original_default_setup_order_preserved']is True,
        'EXACT_ORIGINAL_SINGLE_SETUP_RESPONSE_REQUIRED')
    require(response['solve_calls']==response['formal_table_I_calls']==response['new_VI_candidate_constructions']==response['remaining_live_motions']==0
        and response['independent_path_qualified']is False,'SETUP_MUST_NOT_CLAIM_SOLVE_PATH_OR_EXTRA_QUERIES')
    expected={'mesh_load':1,'freeGridMotions':2};require(response['source_started']==response['source_completed']==expected,'ONLY_NATIVE_MESH_LOAD_AND_EMPTY_GRID_DESTRUCTION_EXPECTED')
    trace=response['trace'];require(len(trace)==6,'EXACT6_SETUP_BODY_ENTRY_EXIT_EVENTS_REQUIRED')
    started={};completed={}
    for event in trace:
        require(event['kind']in expected and event['event']in('entered','completed'),'UNEXPECTED_SETUP_SOURCE_TRACE_KIND')
        if event['event']=='entered':require(event['id']not in started,'TRACE_ID_REUSE');started[event['id']]=event['kind']
        else:require(started.get(event['id'])==event['kind']and event['id']not in completed,'TRACE_EXIT_WITHOUT_UNIQUE_MATCH');completed[event['id']]=event['kind']
    require(started==completed and Counter(started.values())==Counter(expected),'COMPLETE_SETUP_TRACE_PAIRS_REQUIRED')
    m=response['actual_setup_metadata'];dim=m['projection_dimension']
    allowed=['RealVectorLinearProjectionEvaluator','RealVectorRandomLinearProjectionEvaluator']
    require(m['projection_dynamic_type']in[f'N4ompl4base{len(n)}{n}E'for n in allowed]and type(dim)is int and 0<dim<=12,'EXACT_REVIEWED_DYNAMIC_PROJECTION_TYPE_REQUIRED')
    require(m['native_grid_dimensions']==[dim,dim]and m['both_grid_dimensions_match_projection']is True and m['native_tree_sizes']==[0,0],
        'ACTUAL_EMPTY_SBL_GRID_DIMENSIONS_MUST_MATCH')
    require(finite_vector(m['cell_sizes'],dim)and all(x>0 for x in m['cell_sizes'])and type(m['user_configured'])is bool,'FINITE_POSITIVE_ACTUAL_GRID_CELLS_REQUIRED')
    require(type(m['has_bounds'])is bool,'EXPLICIT_PROJECTION_BOUNDS_PRESENCE_REQUIRED')
    if m['has_bounds']:
        b=m['bounds'];require(finite_vector(b['low'],dim)and finite_vector(b['high'],dim)and all(a<b for a,b in zip(b['low'],b['high'])),'FINITE_ORDERED_PROJECTION_BOUNDS_REQUIRED')
    else:require(m['bounds']is None,'ABSENT_BOUNDS_MUST_BE_NULL')
    require(type(m['setup_getRange'])in(int,float)and math.isfinite(m['setup_getRange'])and m['setup_getRange']>0 and m['original_solve_Range']==.8
        and m['sampler']is None and m['sampler_allocated_by_observer']is False,'ORIGINAL_AUTO_RANGE_AND_UNALLOCATED_SAMPLER_REQUIRED')
    require(m['public_project_observation_count']==13 and m['matrix_identity_label']=='OBSERVED_LINEAR_ACTION_MATRIX_NOT_PROTECTED_STORAGE_BYTES'
        and m['projection_observer_RNG_draws']==0 and m['actual_setup_library_RNG_draws']=='UNOBSERVED'
        and m['original_solve_entry_available']is False,'PUBLIC_ACTION_SCOPE_AND_UNOBSERVED_INTERNAL_RNG_REQUIRED')
    observations=m['fixed_zero_then_basis_observations'];columns=m['observed_linear_action_matrix_columns'];require(len(observations)==13 and len(columns)==12,'EXACT_FIXED13_PUBLIC_OBSERVATIONS_REQUIRED')
    for i,point in enumerate(observations):
        expected_q=[1. if i>0 and i-1==j else 0. for j in range(12)]
        require(point['input_q12']==expected_q and point['input_binary64']==binary64(expected_q)and finite_vector(point['output'],dim)
            and point['output_binary64']==binary64(point['output']),'EXACT_PUBLIC_INPUT_AND_BINARY64_OBSERVATION_REQUIRED')
        if i==0:require(all(x==0 for x in point['output']),'LINEAR_ORIGIN_MUST_BE_ZERO')
        else:require(exact(point['output'],columns[i-1]),'ACTUAL_PUBLIC_ACTION_COLUMN_MUST_MATCH_OBSERVATION')
    return 'SOURCE_SETUP_PUBLIC13_OBSERVED_PENDING_INDEPENDENT_POST'


def active_p4():
    active=[]
    for entry in Path('/proc').glob('[0-9]*/cmdline'):
        if int(entry.parent.name)==os.getpid():continue
        try:parts=entry.read_bytes().split(b'\0');cmd=b' '.join(parts).decode(errors='replace')
        except OSError:continue
        # Match actual Python script arguments or executable; do not match shell
        # commentary/cmd text merely mentioning the project.
        exe=parts[0].decode(errors='replace')if parts else ''
        scripts=[x.decode(errors='replace')for x in parts[1:3]]if 'python' in exe else []
        if '.p4_d079_dependency_audit/'in exe or any('/qualify_p4_full_r2_'in x or '/build_p4_full_r2_'in x for x in scripts):active.append(dict(pid=int(entry.parent.name),command=cmd))
    return active

def execute(spec,protocol):
    begun=time.monotonic();cpu_start=own_reaped_cpu();commit=validate(spec,protocol,True)
    launch_proof=supervisor_proof(spec,protocol);folder=ROOT/'results/p4_full'/RUN
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXCLUSIVE_SINGLE_SETUP_NO_RETRY')
    require(not active_p4(),'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    budget=None;journal=None;session=None;counts=Counter();diagnostics=[];error=None
    record=dict(schema='P4_R2_ABB_SBL_PCS_SETUP01_EXECUTION_V3',run_id=RUN,classification=LABEL,status='STOP_PREFIX_RETAINED',
        source_commit=commit,protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),
        budget=spec['budget'],bound_files_sha256=spec['bound_files_sha256'],prior_execution_sha256=spec['prior_execution_sha256'],
        previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],actual_charge_prior=spec['actual_charge_prior'],
        stdout_contract=spec['stdout_contract'],
        supervisor_launch_proof=launch_proof,external_supervision_qualified=False,independent_saved_POST_required=True,
        independent_path_qualified=False,zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0,
        setup_calls=None,public_project_calls=None,solve_calls=0,binary_execution_calls=0)
    try:
        durable_new(claim,dict(schema='P4_R2_ABB_SBL_PCS_SETUP01_CLAIM_V3',run_id=RUN,protocol=record['protocol'],
            protocol_sha256=record['protocol_sha256'],source_commit=commit,budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=Journal(folder/'evidence.jsonl')
        journal.add('setup',record=record);budget=Budget(spec,begun,cpu_start);budget.start();budget.check()
        work=folder/'work';(work/'simulator').mkdir(parents=True);copied={}
        for name,want in spec['runtime_meshes_sha256'].items():
            budget.check();target=work/'simulator'/Path(name).name
            with target.open('xb')as stream:stream.write(path(name).read_bytes())
            require(sha(target)==want,'RUNTIME_MESH_CHANGED');copied[str(target.relative_to(ROOT))]=want
        record['runtime_mesh_sha256']=copied;require(len(copied)==20 and not(work/'paths').exists()and not(folder/'paths').exists(),'FRESH_NATIVE_PATH_DIRECTORIES_REQUIRED')
        session=Session(spec['build_assets']['target'],work,budget,journal,counts);session.start()
        response=session.query(spec['request']);journal.add('parsed_response_before_gates',response=response)
        result_status=check_response(response,spec);session.finish(normal=True);budget.check()
        expected=response['trace'];actual=raw_trace(bytes(session.raw['stderr']))
        require(exact(actual,expected),'RAW_BODY_TRACE_MUST_MATCH_FULL_SOURCE_RESPONSE')
        lines=bytes(session.raw['stdout']).splitlines(keepends=True)
        require(len(lines)==1 and lines[0].endswith(b'\n')and exact(json.loads(lines[0]),response),'EXACT_ONE_COMPLETE_SOURCE_STDOUT_NO_PREAMBLE_REQUIRED')
        require(counts['stdout_complete_lines_observed']==1,'EXACT_ONE_RESPONSE_LINE_REQUIRED')
        require(session.request_sent==len(session.request_raw)and exact(json.loads(session.request_raw),response['request'])
            and session.stdin_closed_after_request,'ACTUAL_FULL_SINGLE_REQUEST_MUST_MATCH_RESPONSE_AND_STDIN_CLOSE')
        require(counts['setup_dispatched']==counts['raw_response_lines_observed']==1,'EXACT_ONE_SETUP_DISPATCH_RETURN_REQUIRED')
        record.update(status=result_status,actual_setup_metadata=response['actual_setup_metadata'],
            actual_source_started=response['source_started'],actual_source_completed=response['source_completed'],
            actual_loaded_project_symbol_scope=session.loaded_scope,setup_calls=1,public_project_calls=13,solve_calls=0)
    except BaseException as exc:
        if budget is not None:budget.close()
        error=exc;record['termination_reason']=repr(exc)
    finally:
        if budget is not None:budget.close()
        processes=list({p.pid:p for p in([]if budget is None else budget.processes)+([]if session is None or session.proc is None else[session.proc])}.values())
        for proc in processes:
            try:kill_source_group(proc)
            except BaseException as exc:diagnostics.append(dict(stage='kill',error=repr(exc)))
        if session is not None:
            try:session.finish(normal=False)
            except BaseException as exc:diagnostics.append(dict(stage='session_cleanup',error=repr(exc)))
        for proc in processes:
            try:kill_source_group(proc);proc.wait(timeout=1.)
            except BaseException as exc:diagnostics.append(dict(stage='central_reap',pid=proc.pid,error=repr(exc)))
        after_groups={str(p.pid):process_group_members(p.pid)for p in processes}
        record['source_process_registry']=[dict(pid=p.pid,reaped=p.returncode is not None,returncode=p.returncode,
            actual_start_ticks=None if session is None or session.proc is not p else session.start_ticks,
            actual_after_reap_group=after_groups[str(p.pid)])for p in processes]
        if session is not None:
            record['source_lifecycle']=dict(actual_start_ticks=session.start_ticks,actual_pipe_EOF_observed=session.pipe_EOF_observed,
                actual_preclose_group=session.close_group,actual_preclose_poll_result=session.close_poll_result,actual_preclose_poll_observations=session.close_poll_observations,actual_postpoll_group=session.close_postpoll_group,
                actual_after_reap_group=session.after_reap_group,stdin_closed_after_unique_request=session.stdin_closed_after_request,
                request_bytes=None if session.request_raw is None else len(session.request_raw),actual_request_sent=session.request_sent,
                request_sha256=None if session.request_raw is None else hashlib.sha256(session.request_raw).hexdigest())
        record['counts']=dict(counts)
        record['binary_execution_calls']=counts['source_process_started']
        raw_gate=session is not None and session.proc is not None and session.proc.returncode==0 and session.eof and session.closed and session.startup_complete and not session.pending and session.after_reap_group==[]and all(session.pipe_EOF_observed.values())and all(not g for g in after_groups.values())
        record['complete_source_raw_evidence_gate']=raw_gate
        if record['status'].startswith('SOURCE_')and not(len(processes)==counts['source_process_started']==1 and raw_gate):record['status']='STOP_PROCESS_EOF_OR_EXIT_UNQUALIFIED'
        try:
            after={n:sha(n)for n in spec['bound_files_sha256']};record['bound_files_after_sha256']=after
            require(after==spec['bound_files_sha256'],'BOUND_ASSET_CHANGED')
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
            require(record['protocol_after_sha256']==record['protocol_sha256']and record['claim_after_sha256']==record.get('claim_sha256'),'RECIPE_CHANGED')
            latest=current_prior();record['prior_execution_after_sha256']=latest['execution_sha256']
            require(latest==spec['actual_charge_prior'],'PRIOR_OR_AUTHORITATIVE_LEDGER_CHANGED')
            require(preload_state()==spec['system_preload_state'],'SYSTEM_PRELOAD_STATE_CHANGED')
            if session is not None and session.loaded_scope is not None:
                record['mapped_files_after_sha256']={n:sha(n)for n in session.loaded_scope['mapped_files_sha256']}
                require(record['mapped_files_after_sha256']==session.loaded_scope['mapped_files_sha256'],'ACTUAL_MAPPED_ELF_CHANGED')
        except BaseException as exc:diagnostics.append(dict(stage='mandatory_hashes',error=repr(exc)))
        if journal is not None:
            try:
                journal.stream.write(b'\n')
                if session is not None:
                    journal.add('final_complete_raw_streams',streams={c:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode())for c,raw in session.raw.items()},EOF=session.eof)
                    for channel,raw in session.raw.items():
                        with(folder/f'source_{channel}.bin').open('xb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
                journal.add('final_counts',counts=dict(counts),diagnostics=diagnostics);journal.finish()
                record['evidence_journal']=str((folder/'evidence.jsonl').relative_to(ROOT));record['evidence_journal_sha256']=sha(folder/'evidence.jsonl')
                native_files=[p for base in(folder/'paths',folder/'work/paths')if base.is_dir()for p in sorted(base.rglob('*'))if p.is_file()]
                require(not native_files,'SETUP_MUST_NOT_PRODUCE_NATIVE_PLANNING_FILES')
                record['original_native_output_sha256']={str(p.relative_to(ROOT)):sha(p)for p in native_files}
                record['original_native_output_fsync_completed']=[]
                for p in native_files:
                    with p.open('rb')as stream:os.fsync(stream.fileno())
                    record['original_native_output_fsync_completed'].append(str(p.relative_to(ROOT)))
            except BaseException as exc:diagnostics.append(dict(stage='final_evidence_preservation',error=repr(exc)))
        record['diagnostics']=diagnostics
        record.update(wall_s=time.monotonic()-begun,cpu_s=own_reaped_cpu()-cpu_start+direct_live_cpu(processes))
        if record['wall_s']>=min(10.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(20.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_R2_ABB_SBL_PCS_SETUP01_COST_RECEIPT_V3',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=own_reaped_cpu()-cpu_start+direct_live_cpu(processes),
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(10.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(20.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            with(folder/'cost_receipt.jsonl').open('xb')as stream:
                stream.write(json.dumps(receipt,allow_nan=False,separators=(',',':')).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
            record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),external_supervision_qualified=False,
        independent_path_qualified=False,new_compile=0,formal_table_I_calls=0)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status','').startswith('SOURCE_'),'SINGLE_SETUP_TRANSPORT_DID_NOT_COMPLETE')

def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    parser.add_argument('--build-post',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:
        require(args.build_post is not None,'ACTUAL_BUILD_POST_PATH_REQUIRED_NO_PLACEHOLDER')
        print(json.dumps(draft_protocol(args.build_post),ensure_ascii=False,indent=2));return
    require(args.build_post is None,'BUILD_POST_PATH_MUST_COME_FROM_EXACT_FROZEN_PROTOCOL')
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_SETUP_DRAFT_VALIDATED_NO_EXECUTION');return
    execute(spec,protocol)

if __name__=='__main__':main()
