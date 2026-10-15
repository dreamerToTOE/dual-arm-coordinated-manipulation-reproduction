#!/usr/bin/env python3
"""One-shot NR Q1 DRAFT. Describe/validate are saved-only; run needs build/freeze.

No numerical module is imported until inside the claimed scientific budget.
No solver is implemented here: one C++ kernel and immutable Python reference.
"""
from __future__ import annotations
import argparse
from collections import Counter
import importlib.util
import json
import math
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time

import build_p4_full_r2_nr_abb_q1_draft as build
from build_p4_full_r2_abb_rrt_pcs_e2e import sha, load, utc, new_json, cpu, live_group_cpu
from p4_full_r2_nr_python_trace_draft import observe_project_nr

ROOT=Path(__file__).resolve().parents[1]
RUN='20261015_R2_NR_ABB_Q1_01'
CLAIM='P4_R2_NR_ABB_Q1_64X3_60W_120CPU_20261015'
AUDIT='reports/P4_FULL_R2_NR_SOURCE_AUDIT_SAVED_INPUTS_20261015.json'
AUDIT_SHA='8200269d0369262f6af76657b5921ee051884f9ead0bd7b08e92a7cafd61d62b'
REFERENCE='baselines/p4_full/geometry_consistent/physical_nr.py'
REFERENCE_SHA='e2dc41936190c7fe335a442c1fee2952681ea5c1be5b94393590188f0fb87d43'
PRE='reports/P4_FULL_R2_NR_ABB_Q1_RUNNER_PRE_DRAFT_20261015.md'
OWN=[str(Path(__file__).relative_to(ROOT)),PRE,*build.OWN]
THREADS={k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
    'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
GATES={'q_rad_abs':1e-10,'observed_delta_rad_abs':1e-10,
    'g_position_mm_abs':1e-8,'g_rotation_abs':1e-11,
    'J_position_mm_per_rad_abs':1e-8,'J_rotation_abs':1e-11,
    'metric_position_mm_abs':1e-8,'metric_rotation_abs':1e-11,
    'singular_abs':1e-8,'singular_relative':1e-10,
    'cutoff_abs':1e-18,'cutoff_relative':1e-10,
    'physical_position_mm':1e-5,'physical_rotation_matrix':1e-5}

def require(condition, reason):
    if not condition:raise RuntimeError(reason)

def path(name):
    p=Path(name)
    return p if p.is_absolute() else ROOT/p

def bind(files,name,expected=None):
    actual=sha(path(name));require(expected is None or actual==expected,'BOUND_HASH_MISMATCH '+str(name))
    files[str(name)]=actual
    return load(path(name)) if str(name).endswith('.json') else None

def fixed_inputs(files):
    audit=bind(files,AUDIT,AUDIT_SHA);copied=audit['Q1_saved_NR_cases_in_original_environment_and_observation_order']
    actual=[]
    for env in ('II','III'):
        name=f'results/p4_full/20261015_R2_SPATIAL01/{env}/observations.json'
        observations=bind(files,name,audit['project_files_sha256'][name]);count=0
        for index,row in enumerate(observations):
            if row.get('kind')!='nr_reference':continue
            r=row['result'];count+=1
            actual.append({'case_id':env+'_'+row['fixture_kind']+'_'+row['fixture'],
                'environment':env,'source_path':name,'source_observation_index':index,
                'fixture_kind':row['fixture_kind'],'fixture':row['fixture'],'q12':r['input_q_rad'],
                'historical_status':r['status'],'historical_candidate_q_rad':r['candidate_q_rad'],
                'historical_metrics':r['metrics'],'historical_metric_only_trace':r['trace'],
                'historical_trace_lacks_q_g_J_sigma_delta':True})
        require(count==32,'EXACT_32_ORIGINAL_NR_INPUTS_PER_ENVIRONMENT')
    require(actual==copied and len(actual)==64,'EXACT_ALL64_AUDIT_AND_ORIGINAL_SOURCE_REQUIRED')
    require(len({c['case_id'] for c in actual})==64,'UNIQUE_CASE_IDS_REQUIRED')
    require(all(len(c['q12'])==12 and all(type(x)in(int,float) and math.isfinite(x) for x in c['q12'])
        for c in actual),'FINITE_HISTORICAL_Q12_REQUIRED')
    for name in (REFERENCE,'baselines/p4_full/abb_independent_oracle.py',
            'baselines/p4_full/analyze_comau_native_qualification.py'):
        bind(files,name,audit['project_files_sha256'][name])
    require(files[REFERENCE]==REFERENCE_SHA,'IMMUTABLE_PYTHON_REFERENCE_REQUIRED')
    return actual

def python_assets(files):
    # Discovery reads installed file metadata/bytes; it does not import NumPy.
    spec=importlib.util.find_spec('numpy');require(spec is not None and spec.origin,'NUMPY_INSTALLATION_REQUIRED')
    package=Path(spec.origin).resolve().parent
    candidates=[Path(sys.executable).resolve()]
    candidates += sorted(p for p in package.rglob('*') if p.is_file() and p.suffix in ('.py','.so'))
    for sibling in (package.parent/'numpy.libs',package.parent/'numpy/.libs'):
        if sibling.exists():candidates+=sorted(p for p in sibling.rglob('*') if p.is_file())
    for filename in sorted(set(candidates)):bind(files,str(filename))
    return {'executable':str(Path(sys.executable).resolve()),'version':sys.version,
        'numpy_package':str(package),'numpy_imported_by_describe':False}

def build_chain(files):
    manifest=build.BUILD/'manifest.json';execution=ROOT/'results/p4_full'/build.RUN/'execution.json'
    if not manifest.is_file() or not execution.is_file() or not build.BINARY.is_file():
        return {'ready':False,'binary':str(build.BINARY),'binary_sha256':'MUST_BUILD_BEFORE_FREEZE',
            'manifest':str(manifest),'manifest_sha256':'MUST_BUILD_BEFORE_FREEZE',
            'execution':str(execution.relative_to(ROOT)),'execution_sha256':'MUST_BUILD_BEFORE_FREEZE'}
    m=bind(files,str(manifest));e=bind(files,str(execution.relative_to(ROOT)))
    require(m['status']=='BUILT_NOT_QUERIED' and e['status']=='BUILT_NOT_QUERIED','SUCCESSFUL_UNQUERIED_BUILD_REQUIRED')
    require(e['build_manifest_sha256']==files[str(manifest)],'BUILD_EXECUTION_MANIFEST_CHAIN')
    require(m['binary']==str(build.BINARY) and e['binary']==str(build.BINARY),'BUILD_BINARY_PATH')
    bind(files,str(build.BINARY),m['binary_sha256']);require(e['binary_sha256']==m['binary_sha256'],'BUILD_BINARY_CHAIN')
    for field in ('own_source_sha256','library_headers_sha256'):
        require(m[field]==m[field.replace('_sha256','_after_sha256')] and e[field]==m[field],
            'BUILD_BEFORE_AFTER_ASSET_CHAIN '+field)
        for name,wanted in m[field].items():bind(files,name,wanted)
    protocol=bind(files,m['protocol'],m['protocol_sha256']);claim=bind(files,m['claim'],m['claim_sha256'])
    require(protocol['frozen'] is True and all(protocol['reviews'].values()),'BUILD_PROTOCOL_FROZEN')
    require(claim['source_commit']==m['source_commit']==e['source_commit'],'BUILD_COMMIT_CHAIN')
    return {'ready':True,'binary':str(build.BINARY),'binary_sha256':files[str(build.BINARY)],
        'manifest':str(manifest),'manifest_sha256':files[str(manifest)],
        'execution':str(execution.relative_to(ROOT)),
        'execution_sha256':files[str(execution.relative_to(ROOT))],'source_commit':m['source_commit']}

def draft():
    files={};cases=fixed_inputs(files)
    for name in sorted(set(OWN+['scripts/qualify_p4_full_r2_vi_rss_reconstructed.py'])):bind(files,name)
    chain=build_chain(files);runtime=python_assets(files)
    prior=sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json') if p.parent.name!=RUN)
    rows=[]
    for p in prior:
        row=bind(files,str(p.relative_to(ROOT)))
        require(all(type(row[k])in(int,float) and math.isfinite(row[k]) and row[k]>=0
            for k in ('wall_s','cpu_s')),'VALID_PRIOR_OWN_COST_REQUIRED')
        rows.append(row)
    return {'schema':'P4_R2_NR_ABB_Q1_QUALIFICATION_DRAFT_V1','frozen':False,
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False,'prior_ledger_confirmed':False},
        'run_id':RUN,'claim_id':CLAIM,'classification':'RECONSTRUCTED_PHYSICAL_FULL_NR_CPP / FIXED64_TRANSFER_ONLY',
        'build':chain,'fixed_cases':cases,'bound_files_sha256':files,'python_runtime':runtime,
        'schedule':[{'variant':v,'case_ids':[c['case_id'] for c in cases]}
            for v in ('cpp_plain','cpp_trace','python_original_observed')],
        'parameters':{'max_iterations':10000,'per_call_wall_limit_s':120.,'position_gate':1e-5,
            'rotation_gate':1e-5,'svd_relative':1e-12,'source_pi_literal':3.1416,
            'periodic_chart':'Original atan2(sin,cos) only after convergence; no replacement wrap/lift.'},
        'comparison_gates':GATES,'thread_environment':THREADS,
        'budget':{'wall_s':60.,'cpu_s':120.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'previous_r2_wall_s':math.fsum(r['wall_s'] for r in rows),
        'previous_r2_cpu_s':math.fsum(r['cpu_s'] for r in rows),
        'prior_executions':[str(p.relative_to(ROOT)) for p in prior],
        'max_top_level_nr_dispatches':192,'max_independent_final_metric_calls':64,
        'max_independent_final_arm_FK_J':128,
        'zero_calls':{'IK':0,'collision':0,'RBS':0,'solve':0,'RNG':0,'VI_constructions':0,'formal_table_I':0},
        'no_retry_reset_or_resume':True,
        'history_policy':'Per-case original replay status/iteration exact and q/metrics by fixed gates. Mismatch UNKNOWN blocks transfer PASS. No hardcoded184/120 total or forced success.',
        'cpp_inflight_trace_policy':'Unreturned internal steps are UNOBSERVED; retain raw stdout/stderr and dispatch, mark UNKNOWN; never infer old steps.',
        'python_worker_policy':'One serial worker for original64 then independent_final64; parent wall/live CPU/process-group hard cap; callback errors cannot suppress parent budget.',
        'scope':'Only saved near64 transfer/physical soundness, not original KDL or all RNG/global planning/other environments/speed/collision.'}

def validate(spec,protocol,execute=False):
    expected=draft()
    require(set(spec)==set(expected),'EXACT_PROTOCOL_FIELDS_REQUIRED')
    require(all(spec[k]==v for k,v in expected.items() if k not in ('frozen','reviews')),'EXACT_CURRENT_PROTOCOL_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews']) and
        all(type(v)is bool for v in spec['reviews'].values()),'EXACT_REVIEW_FIELDS_REQUIRED')
    if not execute:return None
    require(spec['frozen'] and all(spec['reviews'].values()) and spec['build']['ready'],'BUILD_REVIEW_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in sorted(set(OWN+[str(protocol.relative_to(ROOT)),REFERENCE])):
        require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),
            'UNCOMMITTED_SOURCE_OR_PROTOCOL '+name)
    return commit

def without_cost_and_trace(result):
    return {k:v for k,v in result.items() if k not in ('wall_s','trace')}

def compare(cpp,py,case_id):
    checks=[]
    def check(name,ok,**details):checks.append({'check':name,'passed':bool(ok),**details})
    def exact(name,a,b):check(name,a==b,actual=a,reference=b)
    def close(name,a,b,absolute,relative=0.):
        def flatten(value):
            if isinstance(value,list):
                return [x for child in value for x in flatten(child)]
            return [value]
        aa,bb=flatten(a),flatten(b)
        shape=lambda x: (len(x),[shape(v) for v in x]) if isinstance(x,list) else None
        valid=(shape(a)==shape(b) and len(aa)==len(bb) and
            all(type(x)in(int,float) and math.isfinite(x) for x in aa+bb))
        errors=[abs(x-y) for x,y in zip(aa,bb)] if valid else []
        margins=[absolute+relative*max(abs(x),abs(y))-e for x,y,e in zip(aa,bb,errors)] if valid else []
        check(name,valid and all(m>=0 for m in margins),absolute=absolute,relative=relative,
            max_abs_error=max(errors,default=0.) if valid else None,
            minimum_margin=min(margins,default=absolute) if valid else None,shape_valid=valid)
    def metrics(name,a,b):
        exact(name+'.keys',sorted(a or {}),sorted(b or {}))
        if not isinstance(a,dict) or not isinstance(b,dict):return
        exact(name+'.unit',a.get('position_unit'),b.get('position_unit'))
        for key in ('translation_max_abs','rotation_matrix_max_abs','rotation_angle_max_rad'):
            if key in a and key in b:close(name+'.'+key,a[key],b[key],
                GATES['metric_position_mm_abs'] if key=='translation_max_abs' else GATES['metric_rotation_abs'])
    result=py['result'];trace=py['detailed_trace'];ct=cpp['trace']
    exact('status',cpp['status'],result['status']);exact('input',cpp['input_q_rad'],result['input_q_rad'])
    exact('collision_checked',cpp['collision_checked'],False)
    exact('observer_errors',py['observer_errors'],[])
    exact('accepted_updates',cpp['accepted_updates'],py['accepted_updates_observed'])
    exact('trace_length',len(ct),len(trace))
    if cpp['candidate_q_rad'] is None or result['candidate_q_rad'] is None:
        exact('candidate_none',cpp['candidate_q_rad'],result['candidate_q_rad'])
    else:close('candidate',cpp['candidate_q_rad'],result['candidate_q_rad'],GATES['q_rad_abs'])
    metrics('final_metrics',cpp['metrics'],result['metrics'])
    for index,(a,b) in enumerate(zip(ct,trace)):
        prefix=f'iteration{index}'
        exact(prefix+'.iteration',a['iteration'],b['iteration']);exact(prefix+'.rank',a['numerical_rank'],b['numerical_rank'])
        for key in ('q_before','q_next','observed_delta_q'):
            close(prefix+'.'+key,a[key],b[key],GATES['observed_delta_rad_abs'] if key=='observed_delta_q' else GATES['q_rad_abs'])
        exact(prefix+'.update_pattern',bool(a['q_next']),bool(b['q_next']))
        close(prefix+'.g_position',a['g'][:3],b['g'][:3],GATES['g_position_mm_abs'])
        close(prefix+'.g_rotation',a['g'][3:],b['g'][3:],GATES['g_rotation_abs'])
        close(prefix+'.J_position',a['j'][:3],b['j'][:3],GATES['J_position_mm_per_rad_abs'])
        close(prefix+'.J_rotation',a['j'][3:],b['j'][3:],GATES['J_rotation_abs'])
        close(prefix+'.singular_values',a['singular_values'],b['singular_values'],GATES['singular_abs'],GATES['singular_relative'])
        close(prefix+'.cutoff',a['cutoff'],b['cutoff'],GATES['cutoff_abs'],GATES['cutoff_relative'])
        metrics(prefix+'.metrics',a['metrics'],b['metrics'])
    return {'case_id':case_id,'all_passed':all(c['passed'] for c in checks),'checks':checks}

def compare_history(result,case):
    """Saved old values versus new original replay; no new numerical evaluations."""
    checks=[]
    def exact(name,a,b):checks.append({'check':name,'passed':a==b,'actual':a,'historical':b})
    def close(name,a,b,tolerance):
        if a is None or b is None:
            exact(name,a,b);return
        aa=a if isinstance(a,list) else [a];bb=b if isinstance(b,list) else [b]
        valid=len(aa)==len(bb) and all(type(x)in(int,float) and math.isfinite(x) for x in aa+bb)
        errors=[abs(x-y) for x,y in zip(aa,bb)] if valid else []
        checks.append({'check':name,'passed':valid and all(e<=tolerance for e in errors),
            'max_abs_error':max(errors,default=0.) if valid else None,'absolute':tolerance})
    def metric(prefix,a,b):
        if not isinstance(a,dict) or not isinstance(b,dict):exact(prefix,a,b);return
        exact(prefix+'.keys',sorted(a),sorted(b));exact(prefix+'.unit',a.get('position_unit'),b.get('position_unit'))
        for key in ('translation_max_abs','rotation_matrix_max_abs','rotation_angle_max_rad'):
            close(prefix+'.'+key,a.get(key),b.get(key),GATES['metric_position_mm_abs']
                if key=='translation_max_abs' else GATES['metric_rotation_abs'])
    exact('status',result['status'],case['historical_status'])
    exact('iteration_sequence',[r['iteration'] for r in result['trace']],
        [r['iteration'] for r in case['historical_metric_only_trace']])
    close('candidate',result['candidate_q_rad'],case['historical_candidate_q_rad'],GATES['q_rad_abs'])
    metric('final_metrics',result['metrics'],case['historical_metrics'])
    for index,(a,b) in enumerate(zip(result['trace'],case['historical_metric_only_trace'])):
        metric(f'iteration{index}.metrics',{k:v for k,v in a.items() if k!='iteration'},
            {k:v for k,v in b.items() if k!='iteration'})
    return {'case_id':case['case_id'],'all_passed':all(c['passed'] for c in checks),'checks':checks,
        'status':'HISTORY_REPLAY_MATCH' if all(c['passed'] for c in checks) else 'HISTORY_REPLAY_MISMATCH_UNKNOWN'}

def python_worker(protocol):
    """Private, claimed subprocess: same original solver, external parent watchdog.

    Parent owns the deadline, raw stdout/stderr and in-flight accounting. A
    swallowed observer exception cannot defeat the parent's process-group kill.
    """
    spec=load(protocol);claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    folder=ROOT/'results/p4_full'/RUN;admission=load(claim)
    require(spec.get('frozen')is True and all(spec['reviews'].values()) and spec['build']['ready'],
        'WORKER_FROZEN_PROTOCOL_REQUIRED')
    require(admission['protocol_sha256']==sha(protocol) and admission['claim_id']==CLAIM,
        'WORKER_PARENT_CLAIM_REQUIRED')
    require((folder/'setup_started.json').is_file(),'WORKER_PARENT_SETUP_REQUIRED')
    # An existing token refuses a second worker, even after an interrupted call.
    new_json(folder/'python_worker_started.json',{'protocol_sha256':sha(protocol),
        'source_commit':admission['source_commit'],'started_at_utc':utc(),'pid':os.getpid()})
    for name,wanted in spec['bound_files_sha256'].items():require(sha(path(name))==wanted,'WORKER_BOUND_ASSET '+name)
    os.environ.update(THREADS);sys.path.insert(0,str(ROOT))
    from baselines.p4_full.geometry_consistent import physical_nr as reference
    import numpy as np
    counts=Counter();active=None;stage=None
    def emit(kind,**values):
        sys.stderr.write(json.dumps({'schema':'P4_NR_ABB_PYTHON_Q1_EVENT_V1','event':kind,
            'at_utc':utc(),**values},ensure_ascii=False,allow_nan=False)+'\n');sys.stderr.flush()
    emit('runtime',version=sys.version,numpy_version=np.__version__,numpy_file=np.__file__,
        thread_environment={k:os.environ.get(k) for k in THREADS})
    original_arm=reference.arm_fk_jac
    def counted_arm(q,env,arm):
        counts[stage+'_arm_FK_J_started']+=1;emit('arm_FK_J_started',stage=stage,case_id=active,
            environment=env,arm=arm)
        value=original_arm(q,env,arm);counts[stage+'_arm_FK_J_completed']+=1
        emit('arm_FK_J_completed',stage=stage,case_id=active,environment=env,arm=arm);return value
    reference.arm_fk_jac=counted_arm;request_index=0;nr_count=0;final_count=0
    try:
        for line in sys.stdin:
            request=json.loads(line);index=request_index;request_index+=1
            require(set(request)=={'operation','case_id','environment','q12'},'WORKER_EXACT_REQUEST_KEYS')
            active=request['case_id'];operation=request['operation']
            require(request['environment']in('II','III'),'WORKER_ENVIRONMENT')
            q=request['q12'];finite=(isinstance(q,list) and len(q)==12 and
                all(type(x)in(int,float) and math.isfinite(x) for x in q))
            if operation=='nr':
                require(finite,'WORKER_FINITE_NR_Q12')
                require(nr_count<64 and final_count==0,'WORKER_NR_SCHEDULE')
                case=spec['fixed_cases'][nr_count]
                require({k:request[k] for k in ('case_id','environment','q12')}==
                    {k:case[k] for k in ('case_id','environment','q12')},'WORKER_ORIGINAL_INPUT_ORDER')
                nr_count+=1;stage='python_original'
                result=observe_project_nr(reference,q,request['environment'],
                    event_sink=lambda observation:emit('observer',case_id=active,observation=observation))
            elif operation=='independent_final':
                require(nr_count==64 and final_count<64,'WORKER_FINAL_SCHEDULE')
                case=spec['fixed_cases'][final_count];require(active==case['case_id'] and
                    request['environment']==case['environment'],'WORKER_FINAL_CASE_ORDER')
                final_count+=1;stage='independent_final'
                result={'candidate_is_finite':finite,'physical_qualified':False}
                if finite:
                    emit('independent_final_metric_started',case_id=active)
                    metric=reference.residual_metrics(q,request['environment'])
                    emit('independent_final_metric_completed',case_id=active,metrics=metric)
                    bounds=reference.source_limits(request['environment']).tolist()
                    margins=[min(v-lo,hi-v) for v,(lo,hi) in zip(q,bounds)]
                    result.update(metrics=metric,source_bounds_rad=bounds,limit_margins_rad=margins,
                        minimum_limit_margin_rad=min(margins),
                        closed=metric['translation_max_abs']<=1e-5 and metric['rotation_matrix_max_abs']<=1e-5,
                        limits_legal=all(m>=0 for m in margins))
                    result['physical_qualified']=result['closed'] and result['limits_legal']
            else:raise RuntimeError('WORKER_OPERATION')
            print(json.dumps({'schema':'P4_NR_ABB_PYTHON_Q1_WORKER_DRAFT_V1','request_index':index,
                'request':request,'completed_operation':True,'result':result,'observed_counts':dict(counts)},
                ensure_ascii=False,allow_nan=False),flush=True)
            # Preserve returned observation failures, then stop before another call.
            if operation=='nr' and result['observer_errors']:return 2
        return 0
    except BaseException as exc:
        emit('worker_stopped',reason=repr(exc),case_id=active,stage=stage,observed_counts=dict(counts))
        return 2
    finally:reference.arm_fk_jac=original_arm

def execute(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists() and not claim.exists(),'EXISTING_OUTPUT_OR_CLAIM_NO_RETRY')
    started=time.monotonic();cpu_started=cpu();counts=Counter();diagnostics=[];current=None
    events=budget=worker=None;results={};error=None;sessions=[]
    record={'schema':'P4_R2_NR_ABB_Q1_EXECUTION_V1','run_id':RUN,'source_commit':commit,
        'status':'STOP_SETUP_PREFIX_RETAINED','protocol':str(protocol.relative_to(ROOT)),
        'protocol_sha256':sha(protocol),'claim':str(claim.relative_to(ROOT)),'budget':spec['budget'],
        'previous_r2_wall_s':spec['previous_r2_wall_s'],'previous_r2_cpu_s':spec['previous_r2_cpu_s'],
        'bound_files_sha256':spec['bound_files_sha256'],'prior_executions':spec['prior_executions'],
        'classification':spec['classification'],'zero_calls':spec['zero_calls'],'started_at_utc':utc(),
        'cpp_internal_started_completed_counts':'UNOBSERVED_NOT_INFERRED_FROM_HISTORICAL_TRAJECTORY'}
    def event(kind,**values):
        if events is not None:
            events.write(json.dumps({'event':kind,'at_utc':utc(),**values},ensure_ascii=False,allow_nan=False)+'\n');events.flush()
    def retain_error(label,exc):diagnostics.append({'stage':label,'error':repr(exc)})
    class Session:
        """Thin serial JSONL transport using the existing budget/live CPU tools."""
        def __init__(self,label,command):
            self.label=label;self.proc=None;self.selector=None;self.buffer=b'';self.index=0;self.handles=[];self.closed=False
            sessions.append(self);base=folder/label
            self.requests=base.with_suffix('.requests.jsonl').open('xb');self.handles.append(self.requests)
            self.raw=base.with_suffix('.stdout.bin').open('xb');self.handles.append(self.raw)
            self.stderr=base.with_suffix('.stderr.txt').open('xb');self.handles.append(self.stderr)
            self.proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,
                cwd=ROOT,env={**os.environ,**THREADS},start_new_session=True,bufsize=0)
            self.selector=selectors.DefaultSelector();self.selector.register(self.proc.stdout,selectors.EVENT_READ)
            event('process_started',label=label,command=command,pid=self.proc.pid)
        def remaining(self):
            budget.remaining()
            require(cpu()-cpu_started+live_group_cpu(self.proc.pid)<budget.cpu_cap,'LIVE_CHILD_CPU_CAP')
        def read(self):
            chunk=os.read(self.proc.stdout.fileno(),65536)
            if chunk:self.raw.write(chunk);self.raw.flush();self.buffer+=chunk
            return chunk
        def query(self,request,dispatch_counter=None):
            self.remaining();require(not self.buffer.strip(),'UNSOLICITED_JSONL_OUTPUT')
            line=(json.dumps(request,allow_nan=False)+'\n').encode();self.requests.write(line);self.requests.flush()
            self.proc.stdin.write(line);self.proc.stdin.flush()
            if dispatch_counter is not None:counts[dispatch_counter]+=1
            event('request_bytes_sent',label=self.label,request_index=self.index,request=request)
            while b'\n' not in self.buffer:
                self.remaining()
                if self.selector.select(.02):require(bool(self.read()),'EOF_BEFORE_RESPONSE '+self.label)
                elif self.proc.poll() is not None:raise RuntimeError('EXIT_BEFORE_RESPONSE '+self.label)
            encoded,self.buffer=self.buffer.split(b'\n',1);response=json.loads(encoded)
            # Raw bytes are already durable; retain parsed response before interpreting.
            new_json(folder/f'{self.label}_{self.index:03d}_raw_response.json',response)
            self.index+=1;return response
        def finish(self):
            self.proc.stdin.close()
            while self.proc.poll() is None:
                self.remaining()
                if self.selector.select(.02):self.read()
            while self.selector.select(0):
                if not self.read():break
            require(self.proc.returncode==0 and not self.buffer.strip(),'EXIT_OR_UNEXPECTED_OUTPUT '+self.label)
            self.abort()
        def abort(self):
            if self.closed:return
            if self.proc is not None:
                if self.proc.poll() is None:os.killpg(self.proc.pid,signal.SIGKILL)
                self.proc.wait()
                # Drain the complete available stdout prefix after reaping.
                if self.selector is not None:
                    while self.selector.select(0):
                        if not self.read():break
                if self.proc.stdin is not None and not self.proc.stdin.closed:self.proc.stdin.close()
                if self.proc.stdout is not None:self.proc.stdout.close()
                event('process_reaped',label=self.label,returncode=self.proc.returncode,
                    responses_retained=self.index,inflight=current)
            if self.selector is not None:self.selector.close()
            for handle in self.handles:handle.close()
            self.closed=True
    def cpp_mode(mode):
        nonlocal current
        session=Session('cpp_'+mode,[spec['build']['binary'],mode]);completed=[]
        try:
            for index,case in enumerate(spec['fixed_cases']):
                request={k:case[k] for k in ('case_id','environment','q12')}
                current={'variant':'cpp_'+mode,'case_index':index,'case_id':case['case_id'],'request':request,
                    'status':'DISPATCHED_RETURN_UNKNOWN','internal_trace':'UNOBSERVED_UNTIL_RETURN'}
                counts['cpp_'+mode+'_dispatch_attempted']+=1;event('nr_dispatch_attempted',**current)
                response=session.query(request,'cpp_'+mode+'_dispatched');counts['cpp_'+mode+'_responses_retained']+=1
                require(response.get('schema')=='P4_NR_ABB_CPP_Q1_DRAFT_V1' and response.get('request_index')==index and
                    response.get('request')==request and response.get('mode')==mode and
                    response.get('completed_top_level_nr')is True and 'transport_error' not in response,'CPP_RESPONSE_CONTRACT')
                counts['cpp_'+mode+'_completed']+=1;completed.append(response['result'])
                event('nr_completed',variant='cpp_'+mode,case_index=index,case_id=case['case_id'],status=response['result']['status']);current=None
            session.finish()
        finally:session.abort()
        return completed
    try:
        folder.mkdir();new_json(claim,{'schema':'P4_R2_NR_ABB_Q1_CLAIM_V1','claim_id':CLAIM,
            'source_commit':commit,'protocol':record['protocol'],'protocol_sha256':record['protocol_sha256'],
            'created_at_utc':utc(),'budget':spec['budget'],'no_retry_reset_or_resume':True})
        record['claim_sha256']=sha(claim);new_json(folder/'setup_started.json',record)
        events=(folder/'events.jsonl').open('x',buffering=1)
        before={k:os.environ.get(k) for k in THREADS};os.environ.update(THREADS);record['thread_environment_before']=before
        sys.path.insert(0,str(ROOT))
        import qualify_p4_full_r2_vi_rss_reconstructed as common
        budget=common.RunBudget(spec,spec['previous_r2_wall_s'],spec['previous_r2_cpu_s'])
        # Charge imports/setup from the outer clock, not only RunBudget's later clock.
        budget.started=started;budget.cpu_start=cpu_started
        signal.setitimer(signal.ITIMER_REAL,max(.000001,budget.wall_cap-(time.monotonic()-started)))
        results['cpp_plain']=cpp_mode('plain');budget.remaining()
        results['cpp_trace']=cpp_mode('trace');budget.remaining()
        worker=Session('python_worker',[sys.executable,'-u',str(Path(__file__).resolve()),
            '--internal-python-worker',str(protocol)])
        results['python_original_observed']=[]
        for index,case in enumerate(spec['fixed_cases']):
            budget.remaining();current={'variant':'python_original_observed',
                'case_index':index,'case_id':case['case_id'],'status':'DISPATCHED_RETURN_UNKNOWN'}
            counts['python_original_dispatch_attempted']+=1;event('nr_dispatch_attempted',**current)
            request={'operation':'nr',**{k:case[k] for k in ('case_id','environment','q12')}}
            response=worker.query(request,'python_original_dispatched')
            counts['python_original_responses_retained']+=1
            require(response.get('schema')=='P4_NR_ABB_PYTHON_Q1_WORKER_DRAFT_V1' and
                response.get('request')==request and response.get('request_index')==index and
                response.get('completed_operation')is True,'PYTHON_WORKER_RESPONSE_CONTRACT')
            counts['python_original_completed']+=1
            result=response['result'];results['python_original_observed'].append(result)
            event('nr_completed',variant='python_original_observed',case_index=index,
                case_id=case['case_id'],status=result['result']['status']);current=None
            require(result['observer_errors']==[],'PYTHON_OBSERVER_ERROR_NO_FURTHER_CALLS')
        comparisons=[];physical=[];history=[]
        for index,case in enumerate(spec['fixed_cases']):
            budget.remaining();a=results['cpp_plain'][index];b=results['cpp_trace'][index]
            py=results['python_original_observed'][index]
            equality=without_cost_and_trace(a)==without_cost_and_trace(b)
            item=compare(b,py,case['case_id']);item['plain_trace_exact_non_cost_equality']=equality
            item['all_passed']=item['all_passed'] and equality;comparisons.append(item)
            new_json(folder/f'comparison_{index:03d}.json',item)
            # Per-case source/determinism gate; never hardcode old total counts.
            old={'status':case['historical_status'],'candidate_q_rad':case['historical_candidate_q_rad'],
                'metrics':case['historical_metrics'],'trace':case['historical_metric_only_trace']}
            history.append({**compare_history(py['result'],case),'historical':old,
                'new_original_reference':py['result'],'history_does_not_force_success':True})
            q=b['candidate_q_rad'];candidate_finite=isinstance(q,list) and len(q)==12 and all(type(x)in(int,float) and math.isfinite(x) for x in q)
            row={'case_id':case['case_id'],'candidate_is_finite':candidate_finite,'cpp_status':b['status'],
                'collision_checked':False,'branch_or_fixed_active_gate':False}
            current={'variant':'independent_final','case_index':index,'case_id':case['case_id'],
                'q12':q,'status':'FINAL_REQUEST_DISPATCHED_RETURN_UNKNOWN'}
            request={'operation':'independent_final','case_id':case['case_id'],
                'environment':case['environment'],'q12':q}
            counts['independent_final_requests_dispatch_attempted']+=1
            event('independent_final_dispatched',**current)
            response=worker.query(request,'independent_final_requests_dispatched')
            require(response.get('schema')=='P4_NR_ABB_PYTHON_Q1_WORKER_DRAFT_V1' and
                response.get('request')==request and response.get('request_index')==64+index and
                response.get('completed_operation')is True,'FINAL_WORKER_RESPONSE_CONTRACT')
            counts['independent_final_requests_completed']+=1
            row.update(response['result']);event('independent_final_completed',case_id=case['case_id'],result=row);current=None
            row['soundness_passed']=(b['status']!='CONVERGED' or row.get('physical_qualified')is True)
            new_json(folder/f'independent_final_{index:03d}.json',row);physical.append(row)
        worker.finish()
        new_json(folder/'history_diagnostics.json',history)
        new_json(folder/'comparison_summary.json',{'all64_completed':len(comparisons)==64,
            'comparisons':comparisons,'independent_final':physical})
        record.update(comparison_cases=64,comparison_passed=sum(x['all_passed'] for x in comparisons),
            history_cases=64,history_passed=sum(x['all_passed'] for x in history),
            independent_final_cases=len(physical),independent_final_qualified=sum(x.get('physical_qualified',False) for x in physical),
            cpp_converged_cases=sum(r['status']=='CONVERGED' for r in results['cpp_trace']),
            python_converged_cases=sum(r['result']['status']=='CONVERGED' for r in results['python_original_observed']),
            soundness_passed=all(x['soundness_passed'] for x in physical),
            status='PASS_FIXED64_NUMERICAL_TRANSFER' if all(x['all_passed'] for x in comparisons) and
                all(x['all_passed'] for x in history) and all(x['soundness_passed'] for x in physical)
                else 'NUMERICAL_TRANSFER_OR_HISTORY_OR_SOUNDNESS_REJECTED_UNKNOWN_CAUSE',
            not_projection_capability_pass=True)
        budget.remaining()
    except BaseException as exc:
        error=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc))
        try:event('stopped',reason=repr(exc),current=current)
        except BaseException as exc2:retain_error('stopped_event',exc2)
        if current is not None and folder.exists():
            try:new_json(folder/'stopped_partial_call.json',current)
            except BaseException as exc2:retain_error('partial_call',exc2)
    finally:
        if budget is not None:
            try:budget.close()
            except BaseException as exc:retain_error('budget_close',exc)
        for session in sessions:
            try:session.abort()
            except BaseException as exc:retain_error('process_cleanup '+session.label,exc)
        worker_events=folder/'python_worker.stderr.txt'
        if worker_events.exists():
            try:
                observed=[];unknown=[]
                for line_number,line in enumerate(worker_events.read_text().splitlines()):
                    try:row=json.loads(line)
                    except (ValueError,TypeError):unknown.append({'line_number':line_number,'raw':line});continue
                    if row.get('schema')!='P4_NR_ABB_PYTHON_Q1_EVENT_V1':
                        unknown.append({'line_number':line_number,'raw':line});continue
                    observed.append(row)
                    if row['event']in('arm_FK_J_started','arm_FK_J_completed'):
                        counts[row['stage']+'_'+row['event']]+=1
                    if row['event']in('independent_final_metric_started','independent_final_metric_completed'):
                        counts[row['event']]+=1
                    if row['event']=='runtime':record['actual_python_runtime']=row
                new_json(folder/'python_worker_observed_events.json',{'events':observed,'non_event_stderr':unknown,
                    'counts_are_observed_not_predicted':True})
            except BaseException as exc:retain_error('worker_event_retention',exc)
        after={}
        for name in spec['bound_files_sha256']:
            try:after[name]=sha(path(name))
            except BaseException as exc:after[name]=None;retain_error('bound_after '+name,exc)
        if after!=spec['bound_files_sha256']:record['status']='STOP_BOUND_ASSET_CHANGED'
        try:
            record.update(protocol_after_sha256=sha(protocol),claim_after_sha256=sha(claim))
            if record['protocol_after_sha256']!=record['protocol_sha256'] or record['claim_after_sha256']!=record.get('claim_sha256'):
                record['status']='STOP_PROTOCOL_OR_CLAIM_CHANGED'
        except BaseException as exc:retain_error('protocol_claim_after',exc)
        wall=time.monotonic()-started;used_cpu=cpu()-cpu_started
        if wall>=min(60.,3600.-spec['previous_r2_wall_s']) or used_cpu>=min(120.,7200.-spec['previous_r2_cpu_s']):
            record['status']='STOP_WALL_OR_CPU_BUDGET_PREFIX_RETAINED'
        if diagnostics:record['status']='STOP_EVIDENCE_OR_CLEANUP_ERROR'
        record.update(wall_s=wall,cpu_s=used_cpu,counts=dict(counts),diagnostics=diagnostics,
            bound_files_after_sha256=after,ended_at_utc=utc(),inflight_unreturned_call=current,
            uncompleted_case_ids={v:[c['case_id'] for c in spec['fixed_cases'][counts[k]:]]
                for v,k in (('cpp_plain','cpp_plain_completed'),('cpp_trace','cpp_trace_completed'),
                    ('python_original_observed','python_original_completed'))})
        try:
            folder.mkdir(exist_ok=True);new_json(folder/'execution.json',record)
        finally:
            if events is not None:events.close()
    print(json.dumps({k:record.get(k) for k in ('status','counts','comparison_passed','wall_s','cpu_s')}))
    if error:raise error
    require(record['status']=='PASS_FIXED64_NUMERICAL_TRANSFER',record['status'])

def main():
    ap=argparse.ArgumentParser();group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path)
    group.add_argument('--protocol',type=Path);group.add_argument('--internal-python-worker',type=Path)
    args=ap.parse_args()
    if args.internal_python_worker:raise SystemExit(python_worker(args.internal_python_worker.resolve()))
    if args.describe_protocol:print(json.dumps(draft(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_DRAFT_VALIDATED_ZERO_SCIENTIFIC_CALLS');return
    execute(spec,protocol)

if __name__=='__main__':main()
