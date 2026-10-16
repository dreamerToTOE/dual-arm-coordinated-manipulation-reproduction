#!/usr/bin/env python3
"""One-shot fixed64 real three-argument helper qualification, DRAFT.

Top-level imports are stdlib and saved-source builder only. Describe/validate
never import numerical models or start a process. Execute requires two bound
successful builds, committed source, exact frozen reviews, fresh claim/output.
All64 final candidates, including author false outputs, get independent gates.
"""
from __future__ import annotations
import argparse
from collections import Counter
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
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import build_p4_full_r2_abb_random_helper_draft as builder
RUN=builder.SCIENCE_RUN
CLAIM='P4_R2_ABB_RANDOM_HELPER_H_FIXED64_60W_120CPU_20261015'
BUILD=builder.BUILD/'manifest.json'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),*builder.OWN,
    'scripts/recover_p4_full_r2_endpoints.py','baselines/p4_full/abb_independent_oracle.py',
    'baselines/p4_full/analyze_comau_native_qualification.py',
    'baselines/p4_full/geometry_consistent/collision_adapter.py',
    'baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/geometry_consistent/rss_geometry.py']))
GATES={'position_max_abs_mm':1e-5,'rotation_matrix_max_abs':1e-5,
       'branch_zero_relative_epsilon':64*sys.float_info.epsilon,
       'unchanged_active_bits':True,'plain_trace_exact_non_observation':True,
       'original_fixed_success_prefix_exact':True,'source_limits_literal_pi':3.1416,
       'raw_trace_response_binary64_exact':True,'cleanup_pipe_eof_and_empty_stdout_tail':True,
       'continuous_collision_certificate':False}
THREADS={k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
                       'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
class StopQualification(RuntimeError):pass
def require(ok,reason):
    if not ok:raise StopQualification(reason)
def path(name):
    p=Path(name);return p if p.is_absolute() else ROOT/p
def load(name):return json.loads(path(name).read_text())
def sha(name):return hashlib.sha256(path(name).read_bytes()).hexdigest()
def durable_new(name,value):
    with Path(name).open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def q12(q):
    require(isinstance(q,list) and len(q)==12 and all(type(v) in (float,int) and math.isfinite(v) for v in q),
            'FINITE_Q12_REQUIRED');return q
def bits(q):return struct.pack('>'+str(len(q))+'d',*q)
def exact(a,b):
    """JSON shape and binary64 exactness, including signed zero."""
    if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
    if type(a) in (int,float) and type(b) in (int,float):return bits([a])==bits([b])
    if type(a) is not type(b):return False
    if isinstance(a,dict):return set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b
def bind(files,name,wanted=None):
    name=str(name);actual=sha(name);require(wanted is None or actual==wanted,'BOUND_ASSET_CHANGED '+name)
    files[name]=actual
    return load(name) if name.endswith('.json') else None
def build_assets():
    if not BUILD.is_file():return {'status':'MUST_BUILD_BEFORE_FREEZE','files':{},'targets':{}}
    manifest=load(BUILD);files={};bind(files,str(BUILD))
    require(manifest.get('schema')=='P4_R2_ABB_RANDOM_HELPER_H_ENGINEERING_EXECUTION_DRAFT_V1' and
        manifest.get('run_id')==builder.RUN and manifest.get('status')=='BUILT_NOT_QUERIED',
        'EXACT_SUCCESSFUL_H_BUILD_REQUIRED')
    require(manifest.get('query_calls')==manifest.get('solve_calls')==manifest.get('new_VI_candidate_constructions')==0,
            'H_BUILD_SCOPE_CHANGED')
    require(len(manifest.get('entries',[]))==2 and
        [e['factor'] for e in manifest['entries']]==list(builder.FACTORS),'EXACT_TWO_H_TARGETS_REQUIRED')
    for name,wanted in manifest['own_source_sha256'].items():
        bind(files,name,wanted)
        blob=subprocess.check_output(['git','show',manifest['source_commit']+':'+name],cwd=ROOT)
        require(hashlib.sha256(blob).hexdigest()==wanted,'H_BUILD_COMMIT_BLOB_MISMATCH '+name)
    for name,wanted in manifest['template_assets_sha256'].items():bind(files,name,wanted)
    require(manifest['template_assets_sha256']==manifest['template_assets_after_sha256'],'H_BUILD_TEMPLATE_DRIFT')
    for field in ('protocol','claim'):bind(files,manifest[field],manifest[field+'_sha256'])
    protocol=load(manifest['protocol']);claim=load(manifest['claim'])
    require(protocol.get('frozen') is True and bool(protocol.get('reviews')) and
        all(v is True for v in protocol['reviews'].values()),'H_BUILD_NOT_FROZEN_REVIEWED')
    require(protocol['run_id']==builder.RUN and claim['protocol_sha256']==sha(manifest['protocol']) and
        claim['source_commit']==manifest['source_commit'],'H_BUILD_CLAIM_CHAIN')
    engineering=bind(files,manifest['engineering_execution'])
    require(engineering['manifest_sha256']==sha(BUILD) and
        path(engineering['external_manifest']).resolve()==BUILD.resolve() and
        engineering['source_commit']==manifest['source_commit'],'H_BUILD_EXECUTION_CHAIN')
    targets={}
    for entry in manifest['entries']:
        factor=entry['factor'];stage=builder.BUILD/factor;binary=stage/'p4_abb_random_helper_h'
        require(entry['status']=='BUILT_NOT_QUERIED' and entry.get('exit_code')==0 and
            path(entry['stage']).resolve()==stage.resolve() and path(entry['binary']).resolve()==binary.resolve(),
            'H_TARGET_NOT_SUCCESSFUL')
        for field in ('compiled_source_sha256','mesh_sha256'):
            for name,wanted in entry[field].items():bind(files,str(stage/name),wanted)
        bind(files,str(binary),entry['binary_sha256'])
        require(manifest['source_transform_previews'][factor]==protocol['source_transform_previews'][factor],
                'H_TRANSFORM_PREVIEW_CHAIN')
        targets[factor]={'stage':str(stage),'binary':str(binary),'binary_sha256':entry['binary_sha256']}
    return {'status':'BUILT_NOT_QUERIED','source_commit':manifest['source_commit'],'files':files,'targets':targets}
def science_prior():
    # The engineering reader excludes its own build RUN. This science run must
    # charge that completed build and exclude only its own science execution.
    files=sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json')
        if p.parent.name!=RUN)
    rows=[load(p) for p in files]
    return ({str(p.relative_to(ROOT)):sha(p) for p in files},
            math.fsum(row['wall_s'] for row in rows),math.fsum(row['cpu_s'] for row in rows))
def draft_protocol():
    base=builder.science_draft();prior,wall,cpu=science_prior();assets=build_assets();files={}
    for name in OWN:bind(files,name)
    for name,wanted in prior.items():bind(files,name,wanted)
    for name,wanted in base['endpoint_sources_sha256'].items():bind(files,name,wanted)
    for name,wanted in assets['files'].items():bind(files,name,wanted)
    collision=bind(files,COLLISION);entries=[e for e in collision['entries'] if e['model']=='abb']
    require(sorted(e['variant'] for e in entries)==['aligned','native'],'COLLISION_EXACT_TWO_VARIANTS_REQUIRED')
    for entry in entries:
        require(entry['exit_code']==0,'COLLISION_BUILD_FAILED');bind(files,entry['binary'],entry['binary_sha256'])
        for name,wanted in entry['source_files_sha256'].items():bind(files,str(Path(entry['source_root'])/name),wanted)
        for name,wanted in entry['mesh_sha256'].items():bind(files,str(Path(entry['cwd'])/'simulator'/name),wanted)
    contexts=base['fixed_contexts'];schedule=[]
    for factor in builder.FACTORS:
        for mode in ('plain','trace'):
            for c in contexts:schedule.append({'dispatch_index':len(schedule),'factor':factor,'mode':mode,**c})
    require(len(contexts)==16 and len(schedule)==64 and len({c['case_id'] for c in contexts})==16,'FIXED64_SCHEMA')
    return {'schema':'P4_R2_ABB_RANDOM_HELPER_H_FIXED64_QUALIFICATION_DRAFT_V1','frozen':False,
        'execution_readiness':'WAIT_TWO_BUILD_INDEPENDENT_REVIEW_AND_ROOT_FREEZE',
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False,'prior_ledger_confirmed':False},
        'run_id':RUN,'claim_id':CLAIM,'classification':base['classification'],'fixed_contexts':contexts,
        'fixed_schedule':schedule,'build_assets':assets,'bound_files_sha256':files,
        'prior_execution_sha256':prior,'previous_r2_wall_s':wall,'previous_r2_cpu_s':cpu,
        'budget':base['budget'],'gates':GATES,'thread_environment':THREADS,
        'max_helper_dispatches':64,'max_final_metrics':64,'max_math_arm_FK':128,'max_geometry_branch_checks':128,
        'max_collision_adapter_calls':64,'max_collision_native_worker_queries':128,'max_adapter_internal_arm_FK_J':256,
        'source_structural_maxima_not_observed_counts':base['source_structural_maxima_not_observed_counts'],
        'output_order':'All64 helper dispatches first; then32 plain/trace pairs and16 control-flow prefix comparisons from saved source traces; then all64 final physical/branch/limits/aligned-collision gates. Stop and retain complete UNKNOWN tail on exception/cap/source-soundness mismatch.',
        'source_event_contract':['helper_three','shuffle_completed','branch_entered','calc_R1','calc_R2',
                                 'native_fk','native_ik','identify','identify_completed_in_helper','source_limits','collision'],
        'rng_policy':base['rng_policy'],'observation_policy':base['observation_policy'],
        'final_gate_policy':'No final repair, no extra source FK/IK/identify. Pair plain with exact trace from same factor/context. Independently check every false and true output. Final observed source labels only when its saved marker q equals final output bits. Missing source labels remain NOT_OBSERVED; independent two-arm geometry sets always recorded. Source true with closure/active/direct-branch/dual-label inconsistency is soundness STOP; ordinary limits/collision rejection retained. No all64 collisionfree requirement.',
        'collision_manifest':COLLISION,'formal_table_I_calls':0,'formal_table_I_required_calls':22500,
        'zero_calls':{'NR':0,'SVD':0,'RBS':0,'planner_solve':0,'extra_source_final_IK_or_FK':0,'VI_constructions':0},
        'source_plain_internal_started_completed':'UNOBSERVED_NOT_INFERRED_FROM_TRACE_OR_STRUCTURE',
        'rand_started_completed':'UNOBSERVED_NOT_INFERRED_FROM_STRUCTURAL_448',
        'no_retry_reset_or_resume':True,'limitations':base['limitations']}
def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    require(set(spec)==set(expected) and all(spec[k]==v for k,v in expected.items()
        if k not in ('frozen','reviews','execution_readiness')),'EXACT_CURRENT_H_SCIENCE_RECIPE_REQUIRED')
    require(type(spec['frozen']) is bool and set(spec['reviews'])==set(expected['reviews']) and
        all(type(v) is bool for v in spec['reviews'].values()),'BOOLEAN_REVIEW_FIELDS_REQUIRED')
    if execute:
        require(spec['frozen'] is True and all(v is True for v in spec['reviews'].values()) and
            spec['execution_readiness']=='FROZEN_REVIEWED_READY','ROOT_REVIEW_AND_FREEZE_REQUIRED')
        require(spec['build_assets']['status']=='BUILT_NOT_QUERIED','TWO_SUCCESSFUL_H_BUILDS_REQUIRED')
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        for name in OWN+[str(protocol.relative_to(ROOT))]:
            subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            require(not subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True),
                    'UNCOMMITTED_SOURCE_OR_PROTOCOL '+name)
        for name in OWN:
            blob=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
            require(hashlib.sha256(blob).hexdigest()==spec['bound_files_sha256'][name],'COMMIT_BLOB_MISMATCH '+name)
        return commit
def cpu_total():
    """Own+reaped children+all live descendants, never only dispatcher CPU."""
    own=resource.getrusage(resource.RUSAGE_SELF);done=resource.getrusage(resource.RUSAGE_CHILDREN)
    total=own.ru_utime+own.ru_stime+done.ru_utime+done.ru_stime;rows={}
    for p in Path('/proc').glob('[0-9]*/stat'):
        try:
            f=p.read_text().rsplit(')',1)[1].split();rows[int(p.parent.name)]=(int(f[1]),int(f[11])+int(f[12]))
        except (OSError,ValueError,IndexError):pass
    family={os.getpid()}
    while True:
        added={pid for pid,(parent,_) in rows.items() if parent in family}-family
        if not added:break
        family.update(added)
    return total+sum(rows[p][1] for p in family if p!=os.getpid() and p in rows)/os.sysconf('SC_CLK_TCK')
class Budget:
    def __init__(self,spec,started,cpu_start):
        self.started=started;self.cpu_start=cpu_start
        self.wall_cap=min(spec['budget']['wall_s'],3600.-spec['previous_r2_wall_s'])
        self.cpu_cap=min(spec['budget']['cpu_s'],7200.-spec['previous_r2_cpu_s'])
        require(min(self.wall_cap,self.cpu_cap)>0,'H_TOTAL_BUDGET_EXHAUSTED')
        self.previous=signal.getsignal(signal.SIGALRM)
        self.old_timer=signal.getitimer(signal.ITIMER_REAL)
        require(self.old_timer==(0.,0.),'EXISTING_PROCESS_TIMER_REFUSE_REPLACE')
        signal.signal(signal.SIGALRM,self.alarm);signal.setitimer(signal.ITIMER_REAL,.02,.02)
    def alarm(self,*_):self.check()
    def check(self):
        if time.monotonic()-self.started>=self.wall_cap:raise TimeoutError('H_AGGREGATE_HARD_WALL_CAP')
        if cpu_total()-self.cpu_start>=self.cpu_cap:raise TimeoutError('H_AGGREGATE_SELF_REAPED_AND_LIVE_CPU_CAP')
    def remaining(self):
        self.check();return min(self.wall_cap-(time.monotonic()-self.started),self.cpu_cap-(cpu_total()-self.cpu_start))
    def close(self):
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,self.previous)
class HelperSession:
    def __init__(self,factor,mode,env,assets,folder,budget,event):
        self.factor=factor;self.mode=mode;self.env=env;self.pending=b'';self.budget=budget;self.event=event
        self.base=folder/f'{factor}_{mode}_{env}';self.selector=selectors.DefaultSelector();self.closed=False;self.eof_drained=False;self.proc=None
        self.stdout=self.stderr=None;self.command=[assets['binary'],env,assets['stage'],mode]
        try:
            self.stdout=self.base.with_suffix('.stdout').open('xb');self.stderr=self.base.with_suffix('.stderr').open('xb')
            def limits():resource.setrlimit(resource.RLIMIT_CPU,(120,120))
            self.proc=subprocess.Popen(self.command,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,bufsize=0,start_new_session=True,preexec_fn=limits,env={**os.environ,**THREADS})
            for channel in ('stdout','stderr'):
                stream=getattr(self.proc,channel);os.set_blocking(stream.fileno(),False)
                self.selector.register(stream,selectors.EVENT_READ,channel)
            event('helper_session_started',factor=factor,mode=mode,environment=env,pid=self.proc.pid,command=self.command)
        except BaseException:
            # Constructor failure must not leave an unreachable live helper.
            if self.proc is not None and self.proc.poll() is None:
                try:os.killpg(self.proc.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                self.proc.wait(timeout=2.)
            for stream in (self.stdout,self.stderr):
                if stream is not None:stream.close()
            self.selector.close();raise
    def pump(self,wait=.02):
        self.budget.check()
        for key,_ in self.selector.select(min(wait,max(0.,self.budget.remaining()))):
            chunk=os.read(key.fileobj.fileno(),65536)
            if not chunk:self.selector.unregister(key.fileobj);continue
            output=self.stdout if key.data=='stdout' else self.stderr;output.write(chunk);output.flush()
            if key.data=='stdout':self.pending+=chunk
        self.budget.check()
    def query(self,request,counts):
        self.budget.check();counts['helper_dispatch_attempted']+=1
        message=(json.dumps(request,separators=(',',':'),allow_nan=False)+'\n').encode()
        require(self.proc.poll() is None,'HELPER_EXITED_BEFORE_DISPATCH')
        written=self.proc.stdin.write(message);self.proc.stdin.flush()
        require(written==len(message),'INCOMPLETE_HELPER_REQUEST_WRITE_PREFIX_RETAINED');counts['helper_dispatched']+=1
        while b'\n' not in self.pending:
            self.pump()
            require(self.proc.poll() is None or self.selector.get_map(),'HELPER_EXITED_WITHOUT_RESPONSE')
        line,self.pending=self.pending.split(b'\n',1)
        self.event('helper_response_line_observed',factor=self.factor,mode=self.mode,environment=self.env,
                   response_bytes=len(line))
        return line
    def close(self):
        if self.closed:return
        if self.proc.poll() is None:
            try:self.proc.stdin.close()
            except OSError:pass
            # Kill without waiting on source code; no lingering duplicate call.
            try:os.killpg(self.proc.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        self.proc.wait(timeout=2.)
        # After reaping the only writer, drain both finite pipe tails to EOF.
        # A bounded number of reads does not establish complete raw evidence.
        # If the active budget interrupts this drain, leave its streams open:
        # the outer cleanup disables the timer and can finish the same drain.
        drain_deadline=time.monotonic()+2.
        while self.selector.get_map():
            remaining=drain_deadline-time.monotonic()
            require(remaining>0,'HELPER_PIPE_EOF_DRAIN_TIMEOUT_PREFIX_RETAINED')
            for key,_ in self.selector.select(min(.02,remaining)):
                chunk=os.read(key.fileobj.fileno(),65536)
                if not chunk:self.selector.unregister(key.fileobj);continue
                output=self.stdout if key.data=='stdout' else self.stderr;output.write(chunk)
                if key.data=='stdout':self.pending+=chunk
        self.eof_drained=True
        self.stdout.flush();self.stderr.flush();self.stdout.close();self.stderr.close();self.selector.close();self.closed=True
def observe_trace(value):
    require(isinstance(value,list),'TRACE_LIST_REQUIRED');open_calls={};started=Counter();completed=Counter();stack=[]
    serial=0;helper=None;shuffle=[];branches=[];identified=[]
    for e in value:
        require(type(e.get('id')) is int and e['id']>0,'TRACE_POSITIVE_SERIAL_REQUIRED')
        if e['event'] in ('entered','observed'):
            require(e['id']==serial+1,'TRACE_SERIAL_ORDER');serial=e['id']
        if e['event']=='entered':
            require(e['id'] not in open_calls,'TRACE_DUPLICATE_ENTER');open_calls[e['id']]=e['kind'];started[e['kind']]+=1;stack.append(e['id'])
            if e['kind']=='helper_three':require(helper is None,'ONE_HELPER_ENTRY_REQUIRED');helper=e
        elif e['event']=='completed':
            require(stack and stack.pop()==e['id'],'TRACE_CALL_NESTING_MISMATCH')
            require(open_calls.pop(e['id'],None)==e['kind'],'TRACE_COMPLETION_WITHOUT_ENTRY');completed[e['kind']]+=1
        elif e['event']=='observed':
            if e['kind']=='shuffle_completed':shuffle.append(e)
            elif e['kind']=='branch_entered':branches.append(e)
            elif e['kind']=='identify_completed_in_helper':identified.append(e)
            else:raise StopQualification('UNRECOGNIZED_HELPER_MARK')
        else:raise StopQualification('UNRECOGNIZED_TRACE_EVENT')
    require(not open_calls and helper is not None and started['helper_three']==completed['helper_three']==1,
            'TRACE_ALL_ENTRIES_RETURNED_REQUIRED')
    require(len(shuffle)==1 and sorted(shuffle[0]['args']['order'])==list(range(8)),'ONE_SOURCE_SHUFFLE_REQUIRED')
    require(started.get('collision',0)==completed.get('collision',0)==0,'HELPER_COLLISION_CONTRACT_CHANGED')
    order=shuffle[0]['args']['order']
    for i,b in enumerate(branches):
        require(b['args']['loop_index']==i and b['args']['branch']==order[i],'SOURCE_BRANCH_LOOP_ORDER')
    for mark in identified:
        a=mark['args'];require(type(a['loop_index']) is int and a['loop_index'] in range(len(branches)) and
            a['branch']==order[a['loop_index']] and isinstance(a['ik'],list) and len(a['ik'])==2 and
            all(type(x) in (float,int) and x in range(-1,8) for x in a['ik']),'SOURCE_IDENTIFY_MARK_SCHEMA')
    require(1<=len(branches)<=8 and len(identified)<=len(branches),'HELPER_LOOP_CARDINALITY')
    return {'started':dict(started),'completed':dict(completed),'branches':branches,'identified':identified,
            'shuffle':shuffle[0],'helper':helper,'event_count':len(value)}
def normalize_response(response):
    return {k:v for k,v in response.items() if k not in ('mode','source_counts_observed','source_started','source_completed','trace')}
def prefix_compare(original,fixed):
    ot,ft=original['trace'],fixed['trace'];oo=observe_trace(ot);ff=observe_trace(ft)
    require(original['returned'] is False,'ORIGINAL_NORMAL_CONTROL_RETURN_MUST_BE_FALSE')
    require(len(oo['branches'])==8,'ORIGINAL_MUST_COMPLETE_ALL8_BRANCHES')
    success=[(i,e) for i,e in enumerate(ot) if e['event']=='observed' and e['kind']=='identify_completed_in_helper'
             and all(x!=-1 for x in e['args']['ik'])]
    if success:
        stop,first=success[0];require(fixed['returned'] is True,'BREAK_MUST_RETURN_FIRST_IDENTIFIED_SUCCESS')
        require(exact(ot[:stop+1],ft[:-1]),'H_FIRST_SUCCESS_COMMON_PREFIX_MISMATCH')
        require(ft[-1]['event']=='completed' and ft[-1]['kind']=='helper_three' and
            ft[-1]['result']['returned'] is True,'BREAK_MUST_EXIT_DIRECTLY_AFTER_FIRST_SUCCESS')
        require(exact(join_q(first['args']),fixed['q12']),'BREAK_FINAL_Q_MUST_BE_FIRST_IDENTIFIED_CANDIDATE')
        require(len(oo['branches'])==8,'ORIGINAL_MUST_COMPLETE_ALL8_BRANCHES')
        return {'passed':True,'first_identified_loop_index':first['args']['loop_index'],
                'first_identified_branch':first['args']['branch'],'common_prefix_events':stop+1,
                'original_branch_attempts':len(oo['branches']),'break_branch_attempts':len(ff['branches'])}
    require(fixed['returned'] is False and exact(original['q12'],fixed['q12']) and exact(ot,ft),
            'NO_SUCCESS_MUST_BOTH_FALSE_WITH_IDENTICAL_TRACE_AND_FINAL_Q')
    return {'passed':True,'first_identified_loop_index':None,'first_identified_branch':None,
            'common_prefix_events':len(ot),'original_branch_attempts':len(oo['branches']),
            'break_branch_attempts':len(ff['branches'])}
def join_q(args):return args['q1']+args['q2']
def final_source_identity(trace_response,final_q):
    marks=[e for e in trace_response['trace'] if e['event']=='observed' and e['kind']=='identify_completed_in_helper'
           and exact(join_q(e['args']),final_q)]
    if not marks:return {'status':'NOT_OBSERVED','source_identify_ik':None,'direct_branch':None}
    args=marks[-1]['args']
    return {'status':'OBSERVED_MATCHING_FINAL_CANDIDATE','source_identify_ik':args['ik'],
            'direct_branch':args['branch'],'loop_index':args['loop_index']}
def retained_trace_prefix(filename):
    events=[];tails=[]
    if not filename.is_file():return {'events':events,'tails':tails}
    for line1,line in enumerate(filename.read_bytes().splitlines(keepends=True),1):
        marker=b'P4_HELPER_TRACE '
        if marker not in line:continue
        payload=line.split(marker,1)[1]
        try:events.append(json.loads(payload))
        except (ValueError,UnicodeDecodeError):
            tails.append({'line1':line1,'sha256':hashlib.sha256(payload).hexdigest(),
                          'status':'INCOMPLETE_OR_UNPARSEABLE_SOURCE_PREFIX'})
    return {'events':events,'tails':tails}
def active_p4_processes():
    """Read-only duplicate/concurrent-budget admission, no command execution."""
    answer=[];my_pid=os.getpid()
    for folder in Path('/proc').glob('[0-9]*'):
        try:
            pid=int(folder.name)
            if pid==my_pid:continue
            args=folder.joinpath('cmdline').read_bytes().split(b'\0');names=[Path(a.decode(errors='replace')).name for a in args if a]
            matching=[n for n in names if (n.endswith('.py') and n.startswith(('qualify_p4_full_r2_',
                'recover_p4_full_r2_','build_p4_full_r2_'))) or n=='p4_abb_random_helper_h']
            if matching:answer.append({'pid':pid,'programs':matching})
        except (OSError,ValueError):pass
    return answer
def execute(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists() and not claim.exists(),'OUTPUT_OR_CLAIM_EXISTS_NO_RETRY')
    active=active_p4_processes();require(not active,'OTHER_ACTIVE_P4_WORK_MUST_FINISH_BEFORE_SHARED_BUDGET_RUN '+json.dumps(active))
    begun=time.monotonic();cpu_start=cpu_total();counts=Counter();diagnostics=[];sessions={};responses={};physical=[];actual_helper_completed_ids=[]
    comparisons=[];prefixes=[];events=None;budget=None;adapter=None;physical_module=None;original_fk=None
    current=None;error=None;source_index=None;current_stage='SETUP';runtime=folder/'runtime';original_collision_query=None
    record={'schema':'P4_R2_ABB_RANDOM_HELPER_H_FIXED64_EXECUTION_DRAFT_V1','run_id':RUN,
        'classification':spec['classification'],'source_commit':commit,'status':'STOP_SETUP_PREFIX_RETAINED',
        'protocol':str(protocol.relative_to(ROOT)),'protocol_sha256':sha(protocol),
        'claim':str(claim.relative_to(ROOT)),'budget':spec['budget'],'bound_files_sha256':spec['bound_files_sha256'],
        'prior_execution_sha256':spec['prior_execution_sha256'],'previous_r2_wall_s':spec['previous_r2_wall_s'],
        'previous_r2_cpu_s':spec['previous_r2_cpu_s'],'started_at_utc':builder.utc(),
        'zero_calls':spec['zero_calls'],'formal_table_I_calls':0,'formal_table_I_required_calls':22500,
        'new_VI_candidate_constructions':0,'rand_started_completed':spec['rand_started_completed'],
        'plain_source_internal_counts':spec['source_plain_internal_started_completed'],
        'continuous_collision_certificate':False,'not_planning_or_distribution_capability_pass':True}
    def event(kind,**fields):
        if events is not None:
            events.write(json.dumps({'event':kind,'at_utc':builder.utc(),**fields},allow_nan=False)+'\n');events.flush()
    def retain_error(stage,exc):diagnostics.append({'stage':stage,'error':repr(exc)})
    try:
        new_claim={'schema':'P4_R2_ABB_RANDOM_HELPER_H_FIXED64_CLAIM_DRAFT_V1','claim_id':CLAIM,
            'source_commit':commit,'protocol':record['protocol'],'protocol_sha256':record['protocol_sha256'],
            'budget':spec['budget'],'created_at_utc':builder.utc(),'no_retry_reset_or_resume':True}
        durable_new(claim,new_claim);record['claim_sha256']=sha(claim);folder.mkdir();runtime.mkdir()
        durable_new(folder/'setup_started.json',record);events=(folder/'events.jsonl').open('x',buffering=1)
        budget=Budget(spec,begun,cpu_start);current_stage='SOURCE_HELPERS'
        for fixture in spec['fixed_schedule']:
            budget.check();i=fixture['dispatch_index'];source_index=i;current={'fixture':fixture,'stage':'REQUEST_RETAINED'}
            request={k:fixture[k] for k in ('case_id','operation','environment','q12','active_chain','seed')}
            durable_new(folder/f'helper_{i:03d}_request.json',request)
            factor,mode,env=fixture['factor'],fixture['mode'],fixture['environment'];session_key=(factor,mode,env)
            if session_key not in sessions:
                sessions[session_key]=HelperSession(factor,mode,env,spec['build_assets']['targets'][factor],runtime,budget,event)
            require(counts['helper_dispatch_attempted']<64,'FIXED64_HELPER_CAP')
            current['stage']='HELPER_DISPATCH_STARTED';event('helper_dispatch_started',fixture=fixture)
            raw=sessions[session_key].query(request,counts)
            with (folder/f'helper_{i:03d}_raw_response_line.bin').open('xb') as f:f.write(raw+b'\n');f.flush();os.fsync(f.fileno())
            counts['helper_response_lines_retained']+=1;current['stage']='RAW_RESPONSE_RETAINED'
            response=json.loads(raw);durable_new(folder/f'helper_{i:03d}_raw_response.json',response)
            counts['helper_json_responses_retained']+=1
            require(response.get('schema')=='P4_ABB_RANDOM_HELPER_TRANSPORT_DRAFT_V1' and
                response.get('status')=='SOURCE_HELPER_COMPLETED' and response.get('environment')==env and
                response.get('mode')==mode and exact(response.get('request'),request),'HELPER_RESPONSE_CONTRACT')
            require(type(response.get('returned')) is bool and response.get('helper_dispatch_started')==1 and
                response.get('helper_dispatch_completed')==1 and response.get('srand_calls_completed')==1,
                'ONE_COMPLETED_SOURCE_HELPER_REQUIRED')
            counts['helper_completed']+=1;counts['srand_completed_from_returned_response']+=1
            counts['source_returned_true_completed_response' if response['returned'] else 'source_returned_false_completed_response']+=1
            actual_helper_completed_ids.append(i)
            q12(response.get('q12'));require(response.get('candidate_is_finite') is True,'NONFINITE_FINAL_SOURCE_CANDIDATE')
            active=fixture['active_chain'];a=slice(6*active,6*(active+1))
            require(bits(response['q12'][a])==bits(request['q12'][a]),'SOURCE_HELPER_CHANGED_ACTIVE_COORDINATES')
            if mode=='trace':
                observation=observe_trace(response['trace'])
                require(observation['started']==response.get('source_started') and
                    observation['completed']==response.get('source_completed'),'TRACE_COUNT_RESPONSE_MISMATCH')
                require(exact(join_q(observation['helper']['args']),request['q12']) and
                    observation['helper']['args']['active_chain']==active,'TRACE_HELPER_INPUT_MISMATCH')
                require(response['trace'][-1]['event']=='completed' and response['trace'][-1]['kind']=='helper_three' and
                    response['trace'][-1]['result']['returned'] is response['returned'] and
                    exact(join_q(response['trace'][-1]['result']),response['q12']),'TRACE_HELPER_FINAL_RETURN_MISMATCH')
                for k,v in observation['started'].items():counts['trace_'+k+'_started']+=v
                for k,v in observation['completed'].items():counts['trace_'+k+'_completed']+=v
                counts['trace_shuffle_completed']+=1
            else:
                require(response.get('trace') is None and response.get('source_started') is None and
                    response.get('source_completed') is None,'PLAIN_INTERNAL_WORK_MUST_REMAIN_UNOBSERVED')
            if factor=='source_control':require(response['returned'] is False,'ORIGINAL_CONTROL_MUST_NORMALLY_RETURN_FALSE')
            responses[(factor,mode,fixture['case_id'])]=response
            event('helper_completed',dispatch_index=i,factor=factor,mode=mode,case_id=fixture['case_id'],returned=response['returned'])
            current=None;source_index=None
        require(counts['helper_completed']==64 and len(responses)==64,'ALL64_HELPERS_REQUIRED')
        # End source workers before independent gates: no hidden source operation
        # may race a physical check or contribute uncharged lingering CPU.
        for session in sessions.values():session.close()
        budget.check();current_stage='SAVED_SOURCE_COMPARISONS'
        for factor in builder.FACTORS:
            for context in spec['fixed_contexts']:
                case=context['case_id'];plain=responses[(factor,'plain',case)];trace=responses[(factor,'trace',case)]
                require(exact(normalize_response(plain),normalize_response(trace)),'PLAIN_TRACE_EXACT_PARITY_FAILED')
                item={'factor':factor,'case_id':case,'passed':True,'non_observation_binary64_exact':True}
                comparisons.append(item);durable_new(folder/f'plain_trace_comparison_{len(comparisons)-1:03d}.json',item)
                budget.check()
        for context in spec['fixed_contexts']:
            case=context['case_id'];item={'case_id':case,**prefix_compare(responses[('source_control','trace',case)],
                                                                       responses[('success_break','trace',case)])}
            prefixes.append(item);durable_new(folder/f'control_prefix_comparison_{len(prefixes)-1:03d}.json',item);budget.check()
        current_stage='INDEPENDENT_FINAL_GATES'
        for name,value in THREADS.items():os.environ[name]=value
        import recover_p4_full_r2_endpoints as oracle
        from baselines.p4_full.geometry_consistent import physical_nr as physical_import
        from baselines.p4_full.geometry_consistent import collision_adapter as collision_import
        physical_module=physical_import;adapter=collision_import;original_fk=physical_module.arm_fk_jac
        require(not adapter._sessions,'FRESH_COLLISION_SESSIONS_REQUIRED_NO_INHERITED_RUN')
        original_collision_query=adapter.NativeSession.query
        def counted_collision_query(session,q,timeout_s):
            budget.check();require(counts['collision_native_worker_dispatch_attempted']<128,'COLLISION_WORKER_QUERY_CAP')
            j=counts['collision_native_worker_dispatch_attempted'];counts['collision_native_worker_dispatch_attempted']+=1
            event('collision_native_worker_query_started',query_index=j,environment=session.env,
                  command=session.command,q12=list(q))
            result=original_collision_query(session,q,timeout_s)
            counts['collision_native_worker_query_completed']+=1
            durable_new(folder/f'collision_worker_{j:03d}_raw_response.json',result)
            counts['collision_native_worker_raw_response_retained']+=1
            event('collision_native_worker_query_completed',query_index=j);budget.check();return result
        adapter.NativeSession.query=counted_collision_query
        def counted_fk(q,env,arm):
            budget.check();require(counts['adapter_internal_arm_FK_J_started']<256,'ADAPTER_ARM_FK_J_CAP')
            counts['adapter_internal_arm_FK_J_started']+=1;event('adapter_arm_FK_J_started',arm=arm,environment=env)
            result=original_fk(q,env,arm);counts['adapter_internal_arm_FK_J_completed']+=1
            event('adapter_arm_FK_J_completed',arm=arm,environment=env);budget.check();return result
        physical_module.arm_fk_jac=counted_fk
        for fixture in spec['fixed_schedule']:
            budget.check();i=fixture['dispatch_index'];case=fixture['case_id'];factor=fixture['factor'];mode=fixture['mode'];env=fixture['environment']
            response=responses[(factor,mode,case)];q=response['q12'];trace=responses[(factor,'trace',case)]
            current={'dispatch_index':i,'case_id':case,'factor':factor,'mode':mode,'environment':env,
                'source_returned':response['returned'],'q12':q,'stage':'METRIC_STARTED','poses':[],'branches':[]}
            require(counts['independent_final_metric_started']<64,'FINAL_METRIC_CAP')
            counts['independent_final_metric_started']+=1;event('final_metric_started',dispatch_index=i)
            for arm in (1,2):
                budget.check();require(counts['math_arm_FK_started']<128,'MATH_ARM_FK_CAP')
                counts['math_arm_FK_started']+=1;event('math_arm_FK_started',dispatch_index=i,arm=arm)
                pose=oracle.arm_fk(q[6*(arm-1):6*arm],env,arm);current['poses'].append(pose.tolist())
                counts['math_arm_FK_completed']+=1
                durable_new(folder/f'final_{i:03d}_arm{arm}.json',current);event('math_arm_FK_completed',dispatch_index=i,arm=arm)
            import numpy as np
            poses=[np.asarray(p) for p in current['poses']]
            metric=oracle.matrix_error(poses[1],poses[0]@oracle.grasps_for(env)[0]@oracle.FLIP)
            limits=oracle.limit_score(q,env);source_identity=final_source_identity(trace,q)
            for arm in (1,2):
                budget.check();require(counts['geometry_branch_started']<128,'GEOMETRY_BRANCH_CAP')
                counts['geometry_branch_started']+=1
                current['branches'].append(oracle.branch_identity(q[6*(arm-1):6*arm],env,GATES['branch_zero_relative_epsilon']))
                counts['geometry_branch_completed']+=1
            passive=1-fixture['active_chain'];labels=source_identity['source_identify_ik'];direct=source_identity['direct_branch']
            direct_branch_ok=None if direct is None else direct in current['branches'][passive]['branch_set']
            dual_label_ok=None if labels is None else all(type(label) in (float,int) and label in range(8) and
                label in current['branches'][1-index]['branch_set'] for index,label in enumerate(labels))
            active=slice(6*fixture['active_chain'],6*(fixture['active_chain']+1))
            active_ok=bits(q[active])==bits(fixture['q12'][active]);closed=(metric['position_max_abs']<=1e-5 and metric['rotation_matrix_max_abs']<=1e-5)
            current.update(stage='MATH_COMPLETED',closure=metric,limits=limits,source_identity=source_identity,
                direct_branch_membership=direct_branch_ok,dual_source_label_membership=dual_label_ok,
                active_input_unchanged=active_ok,closed=closed,physical_closed_and_limits=bool(closed and limits['legal']),
                source_true_math_sound=bool(not response['returned'] or (closed and active_ok and direct_branch_ok is True and dual_label_ok is True)))
            counts['independent_final_metric_completed']+=1;durable_new(folder/f'final_{i:03d}_math.json',current)
            event('final_metric_completed',dispatch_index=i,closed=closed,limits_legal=limits['legal'])
            # All finite completed outputs, including false/closed/limit rejects,
            # are sent to collision; no screening chooses favourable candidates.
            budget.check();require(counts['collision_adapter_started']<64,'COLLISION_ADAPTER_CAP')
            counts['collision_adapter_started']+=1;current['stage']='COLLISION_STARTED';event('collision_started',dispatch_index=i)
            collision=adapter.check_collision(env,q,timeout_s=min(10.,budget.remaining()),manifest_path=COLLISION)
            counts['collision_adapter_completed']+=1;durable_new(folder/f'final_{i:03d}_collision_raw_response.json',collision)
            current.update(stage='COLLISION_RESPONSE_RETAINED',collision=collision)
            event('collision_response_retained',dispatch_index=i,status=collision.get('status'))
            require(collision.get('status')=='CHECKED' and collision.get('selected_variant')=='aligned' and
                collision.get('manifest_sha256')==spec['bound_files_sha256'][COLLISION] and
                type(collision.get('collision')) is bool and set(collision.get('variants',{}))=={'native','aligned'},
                'COLLISION_RUNTIME_UNQUALIFIED')
            for variant,row in collision['variants'].items():
                codes=row.get('query_codes',[]);counts[variant+'_PQP_queries_returned']+=len(codes)
                require(codes and all(type(code) is int and code==0 for code in codes),'PQP_QUERY_ERROR '+variant)
            current.update(stage='COMPLETED',source_policy_discrete_collision_free=not collision['collision'],
                physical_final_qualified=bool(closed and limits['legal'] and active_ok and not collision['collision']),
                source_branch_relation_qualified=bool(direct_branch_ok is True and dual_label_ok is True),
                final_candidate_all_gates_qualified=bool(closed and limits['legal'] and active_ok and
                    direct_branch_ok is True and dual_label_ok is True and not collision['collision']),
                source_success_fully_qualified=bool(response['returned'] and closed and limits['legal'] and active_ok and
                    direct_branch_ok is True and dual_label_ok is True and not collision['collision']))
            durable_new(folder/f'final_{i:03d}.json',current);physical.append(current)
            event('final_gate_completed',dispatch_index=i,physical_qualified=current['physical_final_qualified'],
                  source_returned=response['returned'])
            require(current['source_true_math_sound'],'H_SOURCE_TRUE_INDEPENDENT_MATH_OR_BRANCH_SOUNDNESS_FAILED')
            current=None;budget.check()
        require(len(physical)==64 and len(comparisons)==32 and len(prefixes)==16,'COMPLETE_FIXED64_ALL_FINAL_GATES_REQUIRED')
        record['status']='PASS_FIXED64_HELPER_CONTROL_FLOW_WITH_INDEPENDENT_FINAL_GATES'
    except BaseException as exc:
        error=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc),termination_stage=current_stage)
        if current is not None and folder.is_dir():
            try:durable_new(folder/'stopped_partial_candidate.json',current)
            except BaseException as saved_error:retain_error('stopped_partial_candidate',saved_error)
        try:event('stopped',stage=current_stage,reason=repr(exc))
        except BaseException as saved_error:retain_error('stopped_event',saved_error)
    finally:
        if budget is not None:
            try:budget.close()
            except BaseException as exc:retain_error('budget_close',exc)
        for key,session in sessions.items():
            try:session.close()
            except BaseException as exc:retain_error('helper_session_close '+str(key),exc)
        if physical_module is not None and original_fk is not None:physical_module.arm_fk_jac=original_fk
        if adapter is not None:
            if original_collision_query is not None:adapter.NativeSession.query=original_collision_query
            saved_sessions=list(adapter._sessions.values())
            try:adapter.close_sessions()
            except BaseException as exc:retain_error('collision_sessions_close',exc)
            for session in saved_sessions:
                try:
                    if session.proc.poll() is None:session.proc.kill()
                    session.proc.wait(timeout=2.)
                except BaseException as exc:retain_error('collision_worker_reap',exc)
        observed_prefixes={};raw_trace_bindings={}
        for key,session in sessions.items():
            try:
                label='/'.join(key);prefix=retained_trace_prefix(session.base.with_suffix('.stderr'))
                observed_prefixes[label]=prefix
                expected=[];dispatches=[]
                for fixture in spec['fixed_schedule']:
                    response=responses.get((fixture['factor'],fixture['mode'],fixture['case_id']))
                    if (fixture['factor'],fixture['mode'],fixture['environment'])==key and response is not None:
                        dispatches.append(fixture['dispatch_index'])
                        if fixture['mode']=='trace':expected.extend(response['trace'])
                binding={'completed_response_dispatch_indexes':dispatches,
                    'expected_completed_response_trace_events':len(expected),
                    'actual_raw_trace_events':len(prefix['events']),
                    'raw_trace_equals_completed_responses_binary64':exact(prefix['events'],expected),
                    'unparseable_trace_tail_count':len(prefix['tails']),
                    'unexpected_stdout_tail_bytes':len(session.pending),
                    'pipe_eof_drained':session.eof_drained,'cleanup_closed':session.closed}
                binding['complete_raw_evidence_gate']=bool(session.eof_drained and session.closed and
                    not prefix['tails'] and not session.pending and binding['raw_trace_equals_completed_responses_binary64'])
                raw_trace_bindings[label]=binding
            except BaseException as exc:retain_error('trace_prefix_read '+str(key),exc)
        raw_complete=(len(raw_trace_bindings)==len(sessions) and
            all(row['complete_raw_evidence_gate'] for row in raw_trace_bindings.values()))
        # Inflight stopped calls may legitimately have a longer raw trace than
        # the completed responses; retain that prefix as UNKNOWN. Only a full
        # qualification PASS requires exact raw/response linkage and EOF.
        if record['status']=='PASS_FIXED64_HELPER_CONTROL_FLOW_WITH_INDEPENDENT_FINAL_GATES' and not raw_complete:
            record['status']='STOP_RAW_TRACE_OR_PIPE_TAIL_NOT_COMPLETE'
        stream_started=Counter();stream_completed=Counter();stream_marks=Counter()
        for prefix in observed_prefixes.values():
            for e in prefix['events']:
                if e.get('event')=='entered':stream_started[e.get('kind')]+=1
                elif e.get('event')=='completed':stream_completed[e.get('kind')]+=1
                elif e.get('event')=='observed':stream_marks[e.get('kind')]+=1
        after={}
        for name in spec['bound_files_sha256']:
            try:after[name]=sha(name)
            except BaseException as exc:after[name]=None;retain_error('after_bound_sha '+name,exc)
        record['bound_files_after_sha256']=after
        if after!=spec['bound_files_sha256']:record['status']='STOP_BOUND_ASSET_CHANGED'
        try:
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
            if record['protocol_after_sha256']!=record['protocol_sha256'] or record['claim_after_sha256']!=record.get('claim_sha256'):
                record['status']='STOP_PROTOCOL_OR_CLAIM_CHANGED'
        except BaseException as exc:retain_error('protocol_claim_after_sha',exc)
        completed_ids={r['dispatch_index'] for r in physical}
        helper_ids=set(actual_helper_completed_ids)
        validated_ids=[f['dispatch_index'] for f in spec['fixed_schedule'] if (f['factor'],f['mode'],f['case_id']) in responses]
        record.update(counts=dict(counts),completed_helper_ids=sorted(helper_ids),source_response_validation_passed_ids=validated_ids,
            completed_final_ids=sorted(completed_ids),
            uncompleted_helper_fixtures=[f for f in spec['fixed_schedule'] if f['dispatch_index'] not in helper_ids],
            uncompleted_final_fixtures=[f for f in spec['fixed_schedule'] if f['dispatch_index'] not in completed_ids],
            unresolved_tail_status='UNKNOWN_NOT_EXECUTED_OR_NOT_COMPLETED_NO_PREFIX_PASS',
            inflight_unreturned_helper=(source_index if counts['helper_dispatched']>counts['helper_response_lines_retained'] else None),
            dispatch_attempt_incomplete_or_unknown=counts['helper_dispatch_attempted']>counts['helper_dispatched'],
            plain_trace_comparison_cases=len(comparisons),control_prefix_comparison_cases=len(prefixes),
            independent_final_cases=len(physical),physical_final_qualified=sum(r['physical_final_qualified'] for r in physical),
            final_candidate_all_gates_qualified=sum(r['final_candidate_all_gates_qualified'] for r in physical),
            source_success_fully_qualified=sum(r['source_success_fully_qualified'] for r in physical),
            source_true_count=counts['source_returned_true_completed_response'],
            source_false_count=counts['source_returned_false_completed_response'],
            source_trace_stream_observed={'started':dict(stream_started),'completed':dict(stream_completed),
                'marks':dict(stream_marks),'scope':'Events actually retained in stderr, including any unfinished helper prefix; plain internals remain UNOBSERVED.'},
            source_raw_trace_bindings=raw_trace_bindings,complete_source_raw_evidence_gate=raw_complete,
            all64_physical_pass_not_required_for_interface_control_flow_qualification=True,
            session_cleanup={ '/'.join(k):{'returncode':s.proc.returncode,'cleanup_closed':s.closed,
                'pipe_eof_drained':s.eof_drained,
                'pending_stdout_bytes':len(s.pending),'stdout_tail_sha256':hashlib.sha256(s.pending).hexdigest(),
                'policy':'Source calls completed or stopped; remaining transport processes killed and reaped without retry.'}
                for k,s in sessions.items()},
            diagnostics=diagnostics,ended_at_utc=builder.utc())
        if folder.is_dir():
            try:
                durable_new(folder/'source_trace_prefixes_saved.json',observed_prefixes)
                durable_new(folder/'comparison_summary.json',{'plain_trace':comparisons,'control_prefix':prefixes})
                durable_new(folder/'independent_final_summary.json',physical)
                durable_new(folder/'unknown_tail.json',{'helper':record['uncompleted_helper_fixtures'],
                    'final':record['uncompleted_final_fixtures'],'status':record['unresolved_tail_status']})
            except BaseException as exc:retain_error('saved_summaries',exc)
        if events is not None:
            try:events.flush();events.close()
            except BaseException as exc:retain_error('events_close',exc)
        record.update(wall_s=time.monotonic()-begun,cpu_s=cpu_total()-cpu_start)
        wall_cap=min(60.,3600.-spec['previous_r2_wall_s']);cpu_cap=min(120.,7200.-spec['previous_r2_cpu_s'])
        if record['wall_s']>=wall_cap or record['cpu_s']>=cpu_cap:record['status']='STOP_WALL_OR_CPU_BUDGET_PREFIX_RETAINED'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():durable_new(folder/'execution.json',record)
    print(json.dumps({'status':record['status'],'wall_s':record.get('wall_s'),'cpu_s':record.get('cpu_s'),
        'completed_helpers':len(responses),'completed_final_gates':len(physical),'formal_table_I_calls':0},ensure_ascii=False))
    if error is not None:raise error
    require(record['status']=='PASS_FIXED64_HELPER_CONTROL_FLOW_WITH_INDEPENDENT_FINAL_GATES','H_FINAL_STATUS_NOT_PASS')
def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--validate-draft',type=Path);g.add_argument('--protocol',type=Path)
    a=p.parse_args()
    if a.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(a.validate_draft or a.protocol).resolve();spec=load(protocol)
    if a.validate_draft:validate(spec,protocol);print('STATIC_H_SCIENCE_DRAFT_VALIDATED_ZERO_QUERY_ZERO_COMPILE');return
    execute(spec,protocol)
if __name__=='__main__':main()
