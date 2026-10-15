#!/usr/bin/env python3
"""Single-target engineering draft. --describe is saved-only; compile needs freeze.
No numerical modules, author code, planner or binary invocation is imported/run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import time
from build_p4_full_r2_abb_rrt_pcs_e2e import sha,load,utc,new_json,cpu,live_group_cpu

ROOT=Path(__file__).resolve().parents[1]
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/nr_abb_q1_cpp_v1')
BINARY=BUILD/'p4_nr_abb_q1'
RUN='20261015_R2_NR_ABB_Q1_BUILD01'
CLAIM='P4_R2_NR_ABB_Q1_BUILD_45W_90CPU_20261015'
HEADER='baselines/p4_full/geometry_consistent/physical_nr_abb_cpp_draft.hpp'
DRIVER='baselines/p4_full/geometry_consistent/physical_nr_abb_q1_driver_draft.cpp'
PRE='reports/P4_FULL_R2_NR_ABB_CPP_Q1_PRE_DRAFT_20261015.md'
AUDIT='reports/P4_FULL_R2_NR_SOURCE_AUDIT_SAVED_INPUTS_20261015.json'
OBSERVER='scripts/p4_full_r2_nr_python_trace_draft.py'
OWN=[str(Path(__file__).relative_to(ROOT)),HEADER,DRIVER,PRE,AUDIT,OBSERVER,
     'scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py']

def prior():
    paths=sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json') if p.parent.name!=RUN)
    rows=[load(p) for p in paths]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths},math.fsum(x['wall_s'] for x in rows),math.fsum(x['cpu_s'] for x in rows)

def libraries():
    paths=[Path('/usr/bin/g++').resolve(),Path('/usr/include/nlohmann/json.hpp')]
    paths+=sorted(p for p in Path('/usr/include/eigen3/Eigen').rglob('*') if p.is_file())
    paths+=sorted(p for p in Path('/usr/include/nlohmann').rglob('*') if p.is_file())
    return {str(p):sha(p) for p in sorted(set(paths))}

def command():
    return [str(Path('/usr/bin/g++').resolve()),'-std=c++17','-O1','-g0','-Wall','-Wextra','-I/usr/include/eigen3',
        '-I'+str((ROOT/HEADER).parent),str(ROOT/DRIVER),'-o',str(BINARY)]

def describe():
    old,wall,used=prior()
    return {'schema':'P4_R2_NR_ABB_Q1_ENGINEERING_DRAFT_V1','frozen':False,
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False},
        'run_id':RUN,'claim_id':CLAIM,'build_root':str(BUILD),'binary':str(BINARY),
        'classification':'PROJECT_OWNED_RECONSTRUCTED_NR_CPP / ENGINEERING_BUILD_ONLY',
        'own_source_sha256':{p:sha(ROOT/p) for p in OWN},'library_headers_sha256':libraries(),
        'prior_execution_sha256':old,'previous_r2_wall_s':wall,'previous_r2_cpu_s':used,
        'budget':{'wall_s':45.,'cpu_s':90.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'compiler_command':command(),'compilation_targets':1,'runtime_modes':['plain','trace'],
        'engineering_difference':'One binary/runtime bool; -O1 without fast-math. Not two independent plain/trace builds and not a speed baseline.',
        'cost_evidence':{'actual_Eigen_NR_compile_cost':'UNKNOWN_NOT_COMPILED',
            'old_RRT_PCS_build_wall_s':17.12737691100483,'old_RRT_PCS_build_cpu_s':23.727903,
            'old_RRT_PCS_is_not_Eigen_NR_cost_measurement':True,
            'naive_two_target_doubling_of_old_RRT_PCS_cost_wall_s':34.25475382200966,
            'naive_two_target_doubling_of_old_RRT_PCS_cost_cpu_s':47.455806,
            'unknown_Eigen_template_overhead_cannot_be_guaranteed_within_45s':True,
            'cap_response':'Retain compile prefix and ledger; no retry or automatic second compilation.'},
        'query_calls':0,'solve_calls':0,'new_VI_candidate_constructions':0,
        'scientific_execution_authorized':False,'no_retry_reset_or_resume':True}

def validate(spec,protocol,execute=False):
    draft=describe()
    if set(spec)!=set(draft) or any(spec[k]!=v for k,v in draft.items() if k not in ('frozen','reviews','schema')):
        raise ValueError('EXACT_CURRENT_ENGINEERING_RECIPE_REQUIRED')
    if spec['schema'] not in ('P4_R2_NR_ABB_Q1_ENGINEERING_DRAFT_V1','P4_R2_NR_ABB_Q1_ENGINEERING_V1'):
        raise ValueError('EXACT_SCHEMA_REQUIRED')
    if type(spec['frozen']) is not bool or set(spec['reviews'])!=set(draft['reviews']) or any(type(v)is not bool for v in spec['reviews'].values()):
        raise ValueError('EXACT_REVIEW_FIELDS_REQUIRED')
    if execute:
        if not spec['frozen'] or not all(spec['reviews'].values()):raise ValueError('REVIEW_ROOT_FREEZE_REQUIRED')
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        for name in [*OWN,str(protocol.relative_to(ROOT))]:
            blob=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
            if blob!=(ROOT/name).read_bytes():raise ValueError('UNCOMMITTED_ASSET '+name)
        return commit

def build(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN
    if folder.exists() or BUILD.exists():raise FileExistsError('FRESH_BUILD_AND_LEDGER_REQUIRED')
    wall_cap=min(45.,3600.-spec['previous_r2_wall_s']);cpu_cap=min(90.,7200.-spec['previous_r2_cpu_s'])
    if min(wall_cap,cpu_cap)<=0:raise ValueError('R2_BUDGET_EXHAUSTED')
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    new_json(claim,{'schema':'P4_R2_NR_ABB_Q1_ENGINEERING_CLAIM_V1','created_at_utc':utc(),
        'source_commit':commit,'protocol':str(protocol),'protocol_sha256':sha(protocol),
        'budget':spec['budget'],'no_retry_reset_or_resume':True})
    BUILD.mkdir();folder.mkdir();started=time.monotonic();began_cpu=cpu();proc=None;error=None
    old_handler=signal.getsignal(signal.SIGALRM)
    def alarm(*_):raise TimeoutError('BUILD_WALL_CAP')
    rec={'schema':'P4_R2_NR_ABB_Q1_ENGINEERING_EXECUTION_V1','run_id':RUN,'status':'STOP_PREFIX_RETAINED',
        'classification':'ENGINEERING_BUILD_ONLY','source_commit':commit,'protocol':str(protocol),
        'protocol_sha256':sha(protocol),'claim':str(claim.relative_to(ROOT)),'claim_sha256':sha(claim),
        'own_source_sha256':spec['own_source_sha256'],'library_headers_sha256':spec['library_headers_sha256'],
        'prior_execution_sha256':spec['prior_execution_sha256'],'previous_r2_wall_s':spec['previous_r2_wall_s'],
        'previous_r2_cpu_s':spec['previous_r2_cpu_s'],'query_calls':0,'solve_calls':0,
        'formal_table_I_calls':0,'new_VI_candidate_constructions':0,'command':command(),'started_at_utc':utc()}
    try:
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,wall_cap)
        with (BUILD/'compile.stdout').open('x') as out,(BUILD/'compile.stderr').open('x') as err:
            def limit():resource.setrlimit(resource.RLIMIT_CPU,(90,90))
            proc=subprocess.Popen(command(),stdout=out,stderr=err,cwd=ROOT,start_new_session=True,preexec_fn=limit)
            while proc.poll() is None:
                if time.monotonic()-started>=wall_cap or cpu()-began_cpu+live_group_cpu(proc.pid)>=cpu_cap:
                    raise TimeoutError('BUILD_WALL_OR_LIVE_CPU_CAP')
                try:proc.wait(timeout=.02)
                except subprocess.TimeoutExpired:pass
        rec['returncode']=proc.returncode
        if proc.returncode:raise RuntimeError('COMPILE_FAILED')
        rec.update(status='BUILT_NOT_QUERIED',binary=str(BINARY),binary_sha256=sha(BINARY))
    except BaseException as exc:
        error=exc;rec['termination_reason']=repr(exc)
        if proc is not None and proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        if proc is not None:rec['returncode']=proc.returncode
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old_handler)
        rec['own_source_after_sha256']={p:sha(ROOT/p) for p in spec['own_source_sha256']}
        rec['library_headers_after_sha256']={p:sha(p) for p in spec['library_headers_sha256']}
        if rec['own_source_after_sha256']!=spec['own_source_sha256'] or rec['library_headers_after_sha256']!=spec['library_headers_sha256']:
            rec['status']='STOP_ASSET_CHANGED';error=error or RuntimeError('ASSET_CHANGED')
        rec['retained_compile_files_sha256']={str(p):sha(p) for p in BUILD.iterdir() if p.is_file()}
        rec['ended_at_utc']=utc();rec['wall_s']=time.monotonic()-started;rec['cpu_s']=cpu()-began_cpu
        if rec['wall_s']>wall_cap or rec['cpu_s']>cpu_cap:
            rec['status']='STOP_BUILD_POSTPROCESS_BUDGET_EXCEEDED'
            error=error or TimeoutError('BUILD_POSTPROCESS_BUDGET_EXCEEDED')
        if rec['status']=='BUILT_NOT_QUERIED':
            new_json(BUILD/'manifest.json',rec);rec['build_manifest']=str(BUILD/'manifest.json');rec['build_manifest_sha256']=sha(BUILD/'manifest.json')
        new_json(folder/'execution.json',rec)
    print(json.dumps({'run_id':RUN,'status':rec['status'],'wall_s':rec['wall_s'],'cpu_s':rec['cpu_s']}))
    if error:raise error

def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--validate-draft',type=Path);g.add_argument('--protocol',type=Path)
    args=ap.parse_args()
    if args.describe_protocol:print(json.dumps(describe(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_DRAFT_VALIDATED_ZERO_QUERY_ZERO_COMPILE');return
    build(spec,protocol)
if __name__=='__main__':main()
