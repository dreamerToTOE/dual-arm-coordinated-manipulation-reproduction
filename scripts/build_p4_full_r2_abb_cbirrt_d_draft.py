#!/usr/bin/env python3
"""D engineering draft: two new stages, compile only after exact freeze.

Describe/validate read saved bytes with stdlib; neither executes a model/binary.
No current-prior protocol is emitted until the preceding IV run has settled.
The frozen RRT saved-asset reader is reused read-only; H is unchanged.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baselines.p4_full.geometry_consistent.abb_cbirrt_d_instrumentation_draft import (
    APC,SVC,COL,CBI,FACTORS,instrument_sources,
)
TEMPLATE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/geometry_consistent_plain')
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_d_v1')
PQP=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3')
COMPILER=Path('/usr/bin/x86_64-linux-gnu-g++-11')
RUN='20261015_R2_ABB_CBIRRT_D_BUILD01'
CLAIM='P4_R2_ABB_CBIRRT_D_BUILD_2_60W_120CPU_20261016'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_STAGED_QUALIFICATION_PRE_DRAFT_20261016.md'
ADDENDUM='reports/P4_FULL_R2_ABB_CBIRRT_D_ENGINEERING_IMPLEMENTATION_DRAFT_20261016.md'
HEADER='baselines/p4_full/geometry_consistent/abb_cbirrt_d_observation_draft.hpp'
DRIVER='baselines/p4_full/geometry_consistent/abb_cbirrt_d_driver_draft.cpp'
TRANSFORM='baselines/p4_full/geometry_consistent/abb_cbirrt_d_instrumentation_draft.py'
READER='scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py'
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),HEADER,DRIVER,TRANSFORM,PRE,ADDENDUM,READER,
     'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py']
THREADS={k:'1'for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def new_json(p,value):
    with Path(p).open('x')as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cpu():
    own=resource.getrusage(resource.RUSAGE_SELF);child=resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime+own.ru_stime+child.ru_utime+child.ru_stime
def prior():
    files=sorted(p for p in (ROOT/'results/p4_full').glob('*_R2_*/execution.json')if p.parent.name!=RUN)
    rows=[load(p)for p in files]
    if any(not all(type(r[k])in (int,float) and math.isfinite(r[k]) and r[k]>=0 for k in ('wall_s','cpu_s'))for r in rows):
        raise ValueError('FINITE_ACTUAL_OWN_COSTS_REQUIRED')
    return {str(p.relative_to(ROOT)):sha(p)for p in files},math.fsum(r['wall_s']for r in rows),math.fsum(r['cpu_s']for r in rows)
def template_assets():
    spec=importlib.util.spec_from_file_location('p4_d_saved_template_reader',ROOT/READER)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    assets=reader.template_assets()
    required=[COMPILER,Path('/usr/lib/gcc/x86_64-linux-gnu/11/cc1plus'),Path('/usr/bin/as'),Path('/usr/bin/x86_64-linux-gnu-ld.bfd'),
        TEMPLATE/'planners/CBiRRT_PCS.cpp',TEMPLATE/'planners/CBiRRT_PCS.h',
        Path('/opt/ros/humble/include/ompl-1.7/ompl/util/RandomNumbers.h'),
        Path('/opt/ros/humble/include/ompl-1.7/ompl/base/PlannerData.h')]
    for name in ('filesystem','system','serialization','program_options'):
        choices=[Path('/opt/ros/humble/lib/x86_64-linux-gnu')/('libboost_'+name+'.so'),Path('/usr/lib/x86_64-linux-gnu')/('libboost_'+name+'.so')]
        selected=next((p for p in choices if p.is_file()),None)
        if selected is None:raise FileNotFoundError('LINKED_BOOST_REQUIRED '+name)
        required.append(selected)
    for p in required:assets[str(p)]=sha(p)
    return assets
def preview():
    source={p:(TEMPLATE/p).read_bytes()for p in (APC,SVC,COL,CBI)}
    return {factor:instrument_sources(source,factor)[1]for factor in FACTORS}
def draft_protocol():
    previous,wall,used=prior()
    return dict(schema='P4_R2_ABB_CBIRRT_D_ENGINEERING_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,prior_ledger_after_IV_confirmed=False),
        run_id=RUN,claim_id=CLAIM,author_commit='909bd72fff778aca8682c96f9eb86ae4eb75557b',
        classification='ENGINEERING_BUILD_ONLY_D_SINGLE_TOKEN_NO_H',template_stage=str(TEMPLATE),build_root=str(BUILD),
        template_assets_sha256=template_assets(),own_source_sha256={p:sha(ROOT/p)for p in OWN},source_transform_previews=preview(),
        targets=[dict(factor=f,stage=str(BUILD/f),binary=str(BUILD/f/'p4_abb_cbirrt_d'))for f in FACTORS],
        linked_author_cpp=[APC,SVC,COL,CBI],runtime_modes=['distance','local','solve'],runtime_observation_modes=['plain','trace'],
        prior_execution_sha256=previous,previous_r2_wall_s=wall,previous_r2_cpu_s=used,
        budget=dict(wall_s=60.,cpu_s=120.,single_wall_s=45.,single_cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        query_calls=0,solve_calls=0,binary_execution_calls=0,formal_table_I_calls=0,new_VI_candidate_constructions=0,
        scientific_execution_authorized=False,
        factor_policy='Fresh R2 copies; source_control versus role1 first retrieve destination qb->qa only. No H helper patch; NN, original complete bodies, RNG/search, geometry, branches, limits, RBS and collision unchanged.',
        observation_policy='Read-only complete-body lambda hooks; original temp deletion retained as I/O-only deviation; both original relative paths remain inside future exclusive run. No model/RNG calls in observer.',
        construction_policy='Future distance constructs a real CBiRRT and original mesh models; direct RNG member seed initialization is structurally one per CBi constructor, actual unhooked library calls/draws UNOBSERVED. Future local constructs only real SVC with SI.',
        one_shot='Exclusive claim/stages/ledger and complete source/log preservation; no retry/reset/resume. Build does not authorize any runtime mode.')
def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    if set(spec)!=set(expected)or any(spec[k]!=v for k,v in expected.items()if k not in ('frozen','reviews')):raise ValueError('EXACT_CURRENT_D_RECIPE_REQUIRED')
    if type(spec['frozen'])is not bool or set(spec['reviews'])!=set(expected['reviews'])or any(type(v)is not bool for v in spec['reviews'].values()):raise ValueError('EXPLICIT_REVIEW_BOOLEANS_REQUIRED')
    if not execute:return None
    if not spec['frozen']or not all(spec['reviews'].values()):raise ValueError('D_INDEPENDENT_REVIEW_ROOT_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in [*OWN,str(protocol.relative_to(ROOT))]:
        subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        if subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True):raise ValueError('UNCOMMITTED '+name)
    for name,wanted in spec['own_source_sha256'].items():
        if hashlib.sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()!=wanted:raise ValueError('COMMIT_BLOB_MISMATCH '+name)
    return commit
def live_group_cpu(pgid):
    total=0.
    for stat in Path('/proc').glob('[0-9]*/stat'):
        try:
            row=stat.read_text().rsplit(')',1)[1].split()
            if int(row[2])==pgid:total+=sum(int(row[i])for i in (11,12,13,14))/os.sysconf('SC_CLK_TCK')
        except (OSError,ValueError,IndexError):pass
    return total
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
def build(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN
    if BUILD.exists()or folder.exists():raise FileExistsError('FRESH_D_STAGES_AND_LEDGER_REQUIRED')
    active=active_p4()
    if active:raise RuntimeError('OTHER_P4_EXECUTION_MUST_SETTLE '+json.dumps(active))
    old_handler=signal.getsignal(signal.SIGALRM);old_timer=signal.getitimer(signal.ITIMER_REAL)
    if old_timer!=(0.,0.):raise RuntimeError('EXISTING_TIMER_REFUSE_REPLACE')
    wall_cap=min(60.,3600.-spec['previous_r2_wall_s']);cpu_cap=min(120.,7200.-spec['previous_r2_cpu_s'])
    if min(wall_cap,cpu_cap)<=0:raise ValueError('R2_BUDGET_EXHAUSTED')
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    new_json(claim,dict(schema='P4_R2_ABB_CBIRRT_D_ENGINEERING_CLAIM_DRAFT_V1',claim_id=CLAIM,created_at_utc=utc(),
        source_commit=commit,protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),budget=spec['budget'],no_retry_reset_or_resume=True))
    BUILD.mkdir();folder.mkdir();begun=time.monotonic();base_cpu=cpu();proc=None;error=None
    record=dict(schema='P4_R2_ABB_CBIRRT_D_ENGINEERING_EXECUTION_DRAFT_V1',run_id=RUN,
        classification=spec['classification'],author_commit=spec['author_commit'],source_commit=commit,budget=spec['budget'],protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),
        claim=str(claim.relative_to(ROOT)),claim_sha256=sha(claim),own_source_sha256=spec['own_source_sha256'],
        template_assets_sha256=spec['template_assets_sha256'],source_transform_previews=spec['source_transform_previews'],
        prior_execution_sha256=spec['prior_execution_sha256'],previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],
        query_calls=0,solve_calls=0,binary_execution_calls=0,formal_table_I_calls=0,new_VI_candidate_constructions=0,
        started_at_utc=utc(),status='STOP_PREFIX_RETAINED',entries=[])
    def alarm(*_):raise TimeoutError('D_AGGREGATE_WALL_CAP')
    try:
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,wall_cap)
        for target in spec['targets']:
            start=time.monotonic();target_cpu=cpu();stage=Path(target['stage']);factor=target['factor'];proc=None
            entry=dict(factor=factor,stage=str(stage),started_at_utc=utc(),status='STOP_PREFIX_RETAINED');record['entries'].append(entry)
            try:
                shutil.copytree(TEMPLATE,stage,ignore=shutil.ignore_patterns('.git','paths','p4_abb_pcs_thin','compile.stdout','compile.stderr'))
                original={p:(stage/p).read_bytes()for p in (APC,SVC,COL,CBI)}
                transformed,changes=instrument_sources(original,factor)
                if changes!=spec['source_transform_previews'][factor]:raise ValueError('D_STAGED_PREVIEW_MISMATCH')
                preserved=stage/'preserved_originals';preserved.mkdir()
                for relative,blob in original.items():
                    p=preserved/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
                for relative,blob in transformed.items():(stage/relative).write_bytes(blob)
                new_json(stage/'source_transform_manifest.json',changes)
                sources=[stage/p for p in spec['linked_author_cpp']]
                headers=sorted(p for p in stage.rglob('*')if p.is_file()and p.suffix in ('.h','.hpp'))
                entry['compiled_source_sha256']={str(p.relative_to(stage)):sha(p)for p in [*sources,*headers]}
                entry['preserved_source_sha256']={p:sha(preserved/p)for p in original}
                entry['mesh_sha256']={str(p.relative_to(stage)):sha(p)for p in sorted((stage/'simulator').glob('*.tris'))}
                cmd=[str(COMPILER),'-std=c++17','-O2','-Wall','-Wextra','-pthread','-I/opt/ros/humble/include/ompl-1.7',
                    '-I/usr/include/eigen3','-I'+str(PQP/'include'),'-I'+str(stage/'proj_classes'),'-I'+str(stage/'validity_checkers'),
                    '-I'+str(stage/'planners'),'-I'+str((ROOT/HEADER).parent),'-include',str(ROOT/HEADER),str(ROOT/DRIVER),
                    *[str(p)for p in sources],str(PQP/'lib/libPQP.a'),'-L/opt/ros/humble/lib/x86_64-linux-gnu',
                    '-Wl,-rpath,/opt/ros/humble/lib/x86_64-linux-gnu','-lompl','-lboost_filesystem','-lboost_system',
                    '-lboost_serialization','-lboost_program_options','-o',target['binary']]
                entry['command']=cmd
                def check(live=0.):
                    if time.monotonic()-begun>=wall_cap or cpu()-base_cpu+live>=cpu_cap or time.monotonic()-start>=45. or cpu()-target_cpu+live>=90.:
                        raise TimeoutError('D_TARGET_OR_AGGREGATE_WALL_CPU_CAP')
                check()
                with (stage/'compile.stdout').open('x')as out,(stage/'compile.stderr').open('x')as err:
                    def limits():resource.setrlimit(resource.RLIMIT_CPU,(90,90))
                    proc=subprocess.Popen(cmd,cwd=ROOT,stdout=out,stderr=err,preexec_fn=limits,start_new_session=True,
                        env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8',**THREADS})
                    while proc.poll()is None:
                        check(live_group_cpu(proc.pid))
                        try:proc.wait(timeout=.02)
                        except subprocess.TimeoutExpired:pass
                entry['exit_code']=proc.returncode
                if proc.returncode:raise RuntimeError('D_BUILD_FAILED')
                check()
                # All complete compile logs/source bytes remain in the new
                # stage; deterministic copies bind those logs in the repo run.
                logs=folder/factor;logs.mkdir()
                for name in ('compile.stdout','compile.stderr','source_transform_manifest.json'):shutil.copyfile(stage/name,logs/name)
                entry.update(binary=target['binary'],binary_sha256=sha(target['binary']),
                    compile_log_sha256={name:sha(logs/name)for name in ('compile.stdout','compile.stderr')},
                    source_transform_manifest_sha256=sha(stage/'source_transform_manifest.json'))
                check();entry['status']='BUILT_NOT_QUERIED'
            except BaseException as exc:
                if proc is not None and proc.poll()is None:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait()
                if proc is not None:entry['exit_code']=proc.returncode
                entry['termination_reason']=repr(exc);raise
            finally:
                # Partial compiler output is evidence too. Keep the original
                # stage log bytes and a separate repo copy on every outcome.
                try:
                    logs=folder/factor;logs.mkdir(exist_ok=True)
                    hashes={}
                    for name in ('compile.stdout','compile.stderr','source_transform_manifest.json'):
                        source=stage/name;destination=logs/name
                        if source.is_file():
                            if not destination.exists():shutil.copyfile(source,destination)
                            if sha(destination)!=sha(source):raise ValueError('LOG_COPY_MISMATCH '+name)
                            hashes[name]=sha(destination)
                    entry['all_retained_log_sha256']=hashes
                except BaseException as exc:
                    entry['log_preservation_error']=repr(exc)
                    if entry['status']=='BUILT_NOT_QUERIED':entry['status']='STOP_LOG_PRESERVATION_ERROR'
                for before_key,after_key in [('compiled_source_sha256','compiled_source_after_sha256'),('mesh_sha256','mesh_after_sha256'),('preserved_source_sha256','preserved_source_after_sha256')]:
                    after={};errors=[]
                    for name in entry.get(before_key,{}):
                        try:after[name]=sha((stage/'preserved_originals' if before_key=='preserved_source_sha256' else stage)/name)
                        except BaseException as exc:after[name]=None;errors.append(dict(path=name,error=repr(exc)))
                    entry[after_key]=after
                    if errors:entry.setdefault('target_hash_errors',[]).extend(errors)
                    if after!=entry.get(before_key,{})and entry['status']=='BUILT_NOT_QUERIED':entry['status']='STOP_TARGET_ASSET_CHANGED'
                entry.update(ended_at_utc=utc(),wall_s=time.monotonic()-start,cpu_s=cpu()-target_cpu)
                if entry['wall_s']>=45. or entry['cpu_s']>=90.:
                    if entry['status']=='BUILT_NOT_QUERIED':entry['status']='STOP_TARGET_FINAL_BUDGET_EXCEEDED'
            if entry['status']!='BUILT_NOT_QUERIED':raise RuntimeError('D_TARGET_FINAL_GATE_FAILED '+entry['status'])
        record['status']='BUILT_NOT_QUERIED'
    except BaseException as exc:error=exc;record['termination_reason']=repr(exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old_handler)
        after={};failures=[]
        for name in spec['template_assets_sha256']:
            try:after[name]=sha(name)
            except BaseException as exc:after[name]=None;failures.append(dict(path=name,error=repr(exc)))
        record['template_assets_after_sha256']=after;record['old_asset_verification_errors']=failures
        if after!=spec['template_assets_sha256']:
            record['status']='STOP_OLD_ASSET_CHANGED';error=error or RuntimeError('OLD_ASSET_CHANGED')
        own_after={};prior_after={}
        try:
            own_after={name:sha(ROOT/name)for name in spec['own_source_sha256']}
            prior_after={name:sha(ROOT/name)for name in spec['prior_execution_sha256']}
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
            if (own_after!=spec['own_source_sha256'] or prior_after!=spec['prior_execution_sha256']
                or record['protocol_after_sha256']!=record['protocol_sha256'] or record['claim_after_sha256']!=record['claim_sha256']):
                record['status']='STOP_FROZEN_RECIPE_CHANGED';error=error or RuntimeError('FROZEN_RECIPE_CHANGED')
        except BaseException as exc:
            record['frozen_recipe_after_error']=repr(exc);record['status']='STOP_FROZEN_RECIPE_AFTER_ERROR';error=error or exc
        record['own_source_after_sha256']=own_after;record['prior_execution_after_sha256']=prior_after
        if any(e['status']!='BUILT_NOT_QUERIED'for e in record['entries'])and record['status']=='BUILT_NOT_QUERIED':
            record['status']='STOP_TARGET_FINAL_EVIDENCE_OR_BUDGET_ERROR';error=error or RuntimeError('D_TARGET_FINAL_GATE_FAILED')
        record.update(ended_at_utc=utc(),wall_s=time.monotonic()-begun,cpu_s=cpu()-base_cpu)
        if record['wall_s']>=wall_cap or record['cpu_s']>=cpu_cap:
            record['final_budget_exceeded']=dict(wall_cap_s=wall_cap,cpu_cap_s=cpu_cap,wall_s=record['wall_s'],cpu_s=record['cpu_s'])
            if record['status']=='BUILT_NOT_QUERIED':record['status']='STOP_FINAL_BUDGET_EXCEEDED'
            error=error or TimeoutError('D_FINAL_EVIDENCE_WALL_CPU_CAP')
        new_json(BUILD/'manifest.json',{**record,'engineering_execution':str((folder/'execution.json').relative_to(ROOT))})
        new_json(folder/'execution.json',{**record,'external_manifest':str(BUILD/'manifest.json'),'manifest_sha256':sha(BUILD/'manifest.json')})
    print(json.dumps(dict(status=record['status'],wall_s=record['wall_s'],cpu_s=record['cpu_s'],query_calls=0,solve_calls=0,binary_execution_calls=0)))
    if error is not None:raise error
def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_D_DRAFT_VALIDATED_ZERO_QUERY_ZERO_COMPILE');return
    build(spec,protocol)
if __name__=='__main__':main()
