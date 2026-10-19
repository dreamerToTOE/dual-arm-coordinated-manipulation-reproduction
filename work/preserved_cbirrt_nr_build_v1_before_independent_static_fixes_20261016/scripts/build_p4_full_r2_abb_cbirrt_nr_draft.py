#!/usr/bin/env python3
"""Single CBiRRT_NR target: build only after a committed reviewed freeze.

Describe reads saved bytes only; no model/binary execution. Uses the immutable
qualified GD seam, original full12 CBiNR control and a complete external cost
boundary. This draft never grants a solve or new scientific sample.
"""
from __future__ import annotations
import argparse
import hashlib
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
import build_p4_full_r2_abb_rrt_nr_e2e_draft as reused
import build_p4_full_r2_abb_cbirrt_d_draft as lifecycle
ROOT=reused.ROOT
sys.path.insert(0,str(ROOT))
from baselines.p4_full.geometry_consistent.abb_cbirrt_nr_instrumentation_draft import (
    KDL,SVC,COL,CBI,HDR,instrument_sources,
)
TEMPLATE=reused.TEMPLATE
AUTHOR=reused.AUTHOR
PQP=reused.PQP
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_nr_v1')
STAGE=BUILD/'physical_nr_observed'
BINARY=STAGE/'p4_abb_cbirrt_nr'
RUN='20261016_R2_ABB_CBIRRT_NR_BUILD01'
CLAIM='P4_R2_ABB_CBIRRT_NR_BUILD_1_45W_90CPU_20261016'
LABEL='ENGINEERING_BUILD_ONLY_ORIGINAL_CBIRRT_NR_WITH_EXISTING_PHYSICAL_GD_SEAM'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_NR_ENGINEERING_PRE_DRAFT_20261016.md'
DIAGNOSIS='reports/P4_FULL_R2_ABB_SBL_PCS_CBIRRT_NR_ENTRY_STATIC_DIAGNOSIS_20261016.json'
HEADER='baselines/p4_full/geometry_consistent/abb_cbirrt_nr_observation_draft.hpp'
DRIVER='baselines/p4_full/geometry_consistent/abb_cbirrt_nr_driver_draft.cpp'
TRANSFORM='baselines/p4_full/geometry_consistent/abb_cbirrt_nr_instrumentation_draft.py'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_draft.py'
KERNEL=reused.KERNEL
COMPILER=Path('/usr/bin/x86_64-linux-gnu-g++-11')
INPUT_FILES=(KDL,SVC,COL,CBI,HDR)
LINKED=(KDL,SVC,COL,CBI)
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),PRE,DIAGNOSIS,HEADER,DRIVER,TRANSFORM,SUPERVISOR,
    'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py',
    'scripts/build_p4_full_r2_abb_cbirrt_d_draft.py',*reused.OWN]))
sha=reused.sha
load=reused.load
THREADS=lifecycle.THREADS
def require(ok,reason):
    if not ok:raise RuntimeError(reason)
def path(value):
    p=Path(value);return p if p.is_absolute()else ROOT/p
def durable_new(filename,value):
    with Path(filename).open('xb')as stream:
        stream.write(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
def cpu():
    own=resource.getrusage(resource.RUSAGE_SELF);child=resource.getrusage(resource.RUSAGE_CHILDREN)
    return own.ru_utime+own.ru_stime+child.ru_utime+child.ru_stime
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
def assets():
    files=reused.assets()
    def bind(filename,wanted=None):
        filename=path(filename);actual=sha(filename);require(wanted is None or actual==wanted,'BOUND_PREVIOUS_ASSET_CHANGED '+str(filename));files[str(filename)]=actual
    manifest=reused.BUILD/'manifest.json';entry=load(manifest)
    require(entry['status']=='BUILT_NOT_QUERIED'and entry['exit_code']==0,'REAL_SUCCESSFUL_RRT_NR_BUILD_REQUIRED');bind(manifest)
    for field in('compiled_source_sha256','mesh_sha256'):
        for name,want in entry[field].items():bind(reused.STAGE/name,want)
    for field,hashfield in(('protocol','protocol_sha256'),('claim','claim_sha256'),('binary','binary_sha256')):bind(entry[field],entry[hashfield])
    for name in(CBI,HDR):
        require((TEMPLATE/name).read_bytes()==(AUTHOR/name).read_bytes(),'CBIRRT_NR_TEMPLATE_MUST_BE_ORIGINAL '+name)
        bind(TEMPLATE/name);bind(AUTHOR/name)
    for name in('run/plan_NR.cpp','run/plan_NR.h'):bind(AUTHOR/name)
    for filename in(COMPILER,Path('/usr/lib/gcc/x86_64-linux-gnu/11/cc1plus'),Path('/usr/bin/as'),Path('/usr/bin/x86_64-linux-gnu-ld.bfd'),
        Path('/usr/bin/time'),Path('/usr/bin/python3')):bind(filename)
    return files
def preview():return instrument_sources({name:(TEMPLATE/name).read_bytes()for name in INPUT_FILES})[1]
def draft_protocol():
    prior=current_prior();files=assets()
    for name in OWN:files[name]=sha(ROOT/name)
    files[prior['ledger']]=prior['ledger_sha256']
    for name,want in prior['execution_sha256'].items():files[name]=want
    return dict(schema='P4_R2_ABB_CBIRRT_NR_ENGINEERING_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,latest_actual_charged_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,author_commit='909bd72fff778aca8682c96f9eb86ae4eb75557b',
        template_stage=str(TEMPLATE),build_root=str(BUILD),stage_root=str(STAGE),binary=str(BINARY),
        source_transform_preview=preview(),bound_files_sha256=files,own_source_sha256={name:sha(ROOT/name)for name in OWN},
        actual_charge_prior=prior,prior_execution_sha256=prior['execution_sha256'],previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],
        budget=dict(wall_s=45.,cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        targets=1,linked_author_cpp=list(LINKED),runtime_modes=['solve'],runtime_observation_modes=['plain','trace'],
        query_calls=0,solve_calls=0,binary_execution_calls=0,formal_table_I_calls=0,new_VI_candidate_constructions=0,scientific_execution_authorized=False,
        source_policy='Original CBiNR full12 NN/control/RBS/reconstruction; only existing qualified GD seam, complete-body read-only observers, retain original temp I/O. No PCS H/D, role or branch design.',
        external_supervision=dict(required=True,sibling_path='results/p4_full/'+RUN+'.supervision.time.txt',format='%e %U %S %x',
            metadata_path='results/p4_full/'+RUN+'.supervision.jsonl',stderr_path='results/p4_full/'+RUN+'.supervision.stderr.log',charge_path='results/p4_full/'+RUN+'.supervision.charge.json',
            time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'),elapsed_decimal_upper_padding_s=.01,
            CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True),
        one_shot='Exclusive fresh stage/claim/logs; compiler-only after independent review/commit/freeze. No retry/reset/resume or runtime query.')
def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_CBIRRT_NR_BUILD_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_BUILD_REVIEW_FIELDS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'REVIEWED_CBIRRT_NR_BUILD_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in[*OWN,str(protocol.relative_to(ROOT))]:require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),'UNCOMMITTED_BUILD_SOURCE_OR_PROTOCOL '+name)
    return commit
def supervisor_proof(spec,protocol):
    ext=spec['external_supervision'];raw=path(ext['metadata_path']).read_bytes().splitlines(keepends=True)[0];planned=json.loads(raw)
    parent=os.getppid();row=Path('/proc',str(parent),'stat').read_text().rsplit(')',1)[1].split()
    require(int(row[1])==planned['supervisor_pid']and sha(Path('/proc',str(parent),'exe'))==ext['time_binary_sha256'],'ACTUAL_GNU_TIME_PARENT_REQUIRED')
    argv=['/usr/bin/time','--quiet','-f',ext['format'],'-o',f"/proc/self/fd/{planned['time_fd']}",'/usr/bin/python3',str(Path(__file__).resolve()),'--protocol',str(protocol)]
    require(planned['event']=='planned_launch'and planned['run_id']==RUN and planned['protocol_sha256']==sha(protocol)
        and planned['runner_sha256']==sha(__file__)and planned['supervisor_source_sha256']==sha(ROOT/SUPERVISOR)
        and planned['argv']==argv and Path('/proc',str(parent),'cmdline').read_bytes().rstrip(b'\0').split(b'\0')==[s.encode()for s in argv],'EXACT_TIME_SOURCE_PROTOCOL_ARGV_REQUIRED')
    stat=path(ext['sibling_path']).stat();held=[]
    for fd in Path('/proc',str(parent),'fd').iterdir():
        try:
            value=fd.stat()
            if(value.st_ino,value.st_dev)==(stat.st_ino,stat.st_dev):held.append(int(fd.name))
        except FileNotFoundError:pass
    require(held and(stat.st_ino,stat.st_dev)==(planned['time_inode'],planned['time_device']),'EXCLUSIVE_SUPERVISION_INODE_REQUIRED')
    return dict(actual_time_pid=parent,actual_time_start_ticks=int(row[19]),supervisor_pid=planned['supervisor_pid'],actual_argv=argv,
        planned_launch_line_sha256=hashlib.sha256(raw).hexdigest(),time_inode=stat.st_ino,time_device=stat.st_dev,actual_time_output_fds=sorted(held),external_POST_required=True)
def build(spec,protocol):
    begun=time.monotonic();used=cpu();commit=validate(spec,protocol,True);proof=supervisor_proof(spec,protocol)
    folder=ROOT/'results/p4_full'/RUN;claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not BUILD.exists()and not folder.exists()and not claim.exists(),'EXCLUSIVE_FRESH_CBIRRT_NR_STAGE_RUN_CLAIM_REQUIRED')
    require(not lifecycle.active_p4(),'OTHER_ACTIVE_P4_EXECUTION');require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    wall_cap=min(45.,3600.-spec['previous_r2_wall_s']);cpu_cap=min(90.,7200.-spec['previous_r2_cpu_s']);require(min(wall_cap,cpu_cap)>0,'R2_BUILD_BUDGET_EXHAUSTED')
    old_handler=signal.getsignal(signal.SIGALRM);proc=None;failure=None;diagnostics=[]
    record=dict(schema='P4_R2_ABB_CBIRRT_NR_ENGINEERING_EXECUTION_V1',run_id=RUN,classification=LABEL,status='STOP_SETUP_PREFIX_RETAINED',
        source_commit=commit,author_commit=spec['author_commit'],protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),
        claim=str(claim.relative_to(ROOT)),budget=spec['budget'],actual_charge_prior=spec['actual_charge_prior'],prior_execution_sha256=spec['prior_execution_sha256'],
        previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],bound_files_sha256=spec['bound_files_sha256'],own_source_sha256=spec['own_source_sha256'],
        supervisor_launch_proof=proof,external_supervision_qualified=False,independent_saved_POST_required=True,
        query_calls=0,solve_calls=0,binary_execution_calls=0,formal_table_I_calls=0,new_VI_candidate_constructions=0)
    def check():
        live=0. if proc is None or proc.returncode is not None else lifecycle.live_group_cpu(proc.pid)
        if time.monotonic()-begun>=wall_cap or cpu()-used+live>=cpu_cap:raise TimeoutError('CBIRRT_NR_BUILD_WALL_OR_SELF_REAPED_LIVE_GROUP_CPU_CAP')
    def alarm(*_):check()
    try:
        durable_new(claim,dict(schema='P4_R2_ABB_CBIRRT_NR_ENGINEERING_CLAIM_V1',run_id=RUN,source_commit=commit,
            protocol=record['protocol'],protocol_sha256=record['protocol_sha256'],budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();BUILD.mkdir()
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,.02,.02);check()
        shutil.copytree(TEMPLATE,STAGE,ignore=shutil.ignore_patterns('.git','paths','p4_abb_*','compile.stdout','compile.stderr'))
        original={name:(STAGE/name).read_bytes()for name in INPUT_FILES};transformed,changes=instrument_sources(original)
        require(changes==spec['source_transform_preview'],'EXACT_STAGED_SOURCE_PREVIEW_REQUIRED')
        for name,blob in original.items():
            saved=STAGE/'preserved_originals'/name;saved.parent.mkdir(parents=True,exist_ok=True)
            with saved.open('xb')as stream:stream.write(blob);stream.flush();os.fsync(stream.fileno())
        for name,blob in transformed.items():(STAGE/name).write_bytes(blob)
        durable_new(STAGE/'source_transform_manifest.json',changes);record['source_transform_manifest']=changes
        sources=[STAGE/name for name in LINKED];headers=sorted(p for p in STAGE.rglob('*')if p.is_file()and p.suffix in('.h','.hpp'))
        record['compiled_source_sha256']={str(p.relative_to(STAGE)):sha(p)for p in[*sources,*headers]}
        record['preserved_source_sha256']={name:sha(STAGE/'preserved_originals'/name)for name in INPUT_FILES}
        record['mesh_sha256']={str(p.relative_to(STAGE)):sha(p)for p in sorted((STAGE/'simulator').glob('*.tris'))}
        command=[str(COMPILER),'-std=c++17','-O1','-g0','-Wall','-Wextra','-pthread','-I/opt/ros/humble/include/ompl-1.7','-I/usr/include/eigen3',
            '-I'+str(PQP/'include'),'-I'+str(STAGE/'proj_classes'),'-I'+str(STAGE/'validity_checkers'),'-I'+str(STAGE/'planners'),
            '-I'+str((ROOT/HEADER).parent),'-include',str(ROOT/HEADER),str(ROOT/DRIVER),str(ROOT/KERNEL),*[str(p)for p in sources],
            str(PQP/'lib/libPQP.a'),'-L/opt/ros/humble/lib/x86_64-linux-gnu','-Wl,-rpath,/opt/ros/humble/lib/x86_64-linux-gnu',
            '-lompl','-lorocos-kdl','-lboost_filesystem','-lboost_system','-lboost_serialization','-lboost_program_options','-o',str(BINARY)]
        record['command']=command;check()
        with(folder/'compile.stdout').open('xb')as out,(folder/'compile.stderr').open('xb')as err:
            previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
            try:
                def limits():
                    signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask);resource.setrlimit(resource.RLIMIT_CPU,(90,90))
                proc=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,start_new_session=True,preexec_fn=limits,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8',**THREADS})
                record['compiler_pid']=proc.pid
            finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
            while proc.poll()is None:
                check()
                try:proc.wait(timeout=.02)
                except subprocess.TimeoutExpired:pass
            out.flush();os.fsync(out.fileno());err.flush();os.fsync(err.fileno())
        record['exit_code']=proc.returncode;require(proc.returncode==0,'CBIRRT_NR_BUILD_FAILED');check()
        record.update(binary=str(BINARY),binary_sha256=sha(BINARY),status='BUILT_NOT_QUERIED')
    except BaseException as exc:failure=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc))
    finally:
        previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            signal.setitimer(signal.ITIMER_REAL,0)
            while signal.SIGALRM in signal.sigpending():signal.sigwait({signal.SIGALRM})
            signal.signal(signal.SIGALRM,old_handler)
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
        if proc is not None:
            try:
                group=lifecycle.live_group_cpu(proc.pid);record['compiler_group_live_CPU_before_cleanup_s']=group
                members=[]
                for stat in Path('/proc').glob('[0-9]*/stat'):
                    try:
                        row=stat.read_text().rsplit(')',1)[1].split()
                        if int(row[2])==proc.pid:members.append(int(stat.parent.name))
                    except(OSError,ValueError,IndexError):pass
                record['compiler_group_members_before_cleanup']=sorted(members)
                if members:os.killpg(proc.pid,signal.SIGKILL)
                proc.wait(timeout=2.);record['exit_code']=proc.returncode;record['compiler_reaped']=True
            except BaseException as exc:diagnostics.append(dict(stage='compiler_cleanup',error=repr(exc)))
        for before,after,prefix in(('compiled_source_sha256','compiled_source_after_sha256',STAGE),('mesh_sha256','mesh_after_sha256',STAGE),('preserved_source_sha256','preserved_source_after_sha256',STAGE/'preserved_originals')):
            try:
                record[after]={name:sha(prefix/name)for name in record.get(before,{})};require(record[after]==record.get(before,{}),'STAGED_ASSET_CHANGED '+before)
            except BaseException as exc:diagnostics.append(dict(stage='staged_final_hashes',error=repr(exc)))
        try:
            record['bound_files_after_sha256']={name:sha(path(name))for name in spec['bound_files_sha256']}
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
            require(record['bound_files_after_sha256']==spec['bound_files_sha256']and record['protocol_after_sha256']==record['protocol_sha256']and record['claim_after_sha256']==record.get('claim_sha256'),'BUILD_BOUND_PROTOCOL_OR_CLAIM_CHANGED')
            require(current_prior()==spec['actual_charge_prior'],'BUILD_LATEST_CHARGED_PRIOR_CHANGED')
        except BaseException as exc:diagnostics.append(dict(stage='final_provenance_or_prior',error=repr(exc)))
        try:record['compile_log_sha256']={str(p.relative_to(ROOT)):sha(p)for p in sorted(folder.glob('compile.*'))if p.is_file()}
        except BaseException as exc:diagnostics.append(dict(stage='compile_log_hashes',error=repr(exc)))
        record.update(wall_s=time.monotonic()-begun,cpu_s=cpu()-used,diagnostics=diagnostics)
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if record['wall_s']>=wall_cap or record['cpu_s']>=cpu_cap:record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if folder.is_dir():
            if record['status']=='BUILT_NOT_QUERIED':durable_new(BUILD/'manifest.json',{**record,'engineering_execution':str((folder/'execution.json').relative_to(ROOT))})
            durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_R2_ABB_CBIRRT_NR_ENGINEERING_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=cpu()-used,
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=wall_cap or receipt['cpu_s_through_execution_persistence']>=cpu_cap:receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            durable_new(folder/'cost_receipt.json',receipt);record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),query_calls=0,solve_calls=0,external_supervision_qualified=False,independent_saved_POST_required=True)))
    if failure is not None:raise failure
    require(record.get('terminal_receipt_status')=='BUILT_NOT_QUERIED','CBIRRT_NR_BUILD_FINAL_GATE_FAILED')
def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_BUILD_DRAFT_VALIDATED_NO_EXECUTION');return
    build(spec,protocol)
if __name__=='__main__':main()
