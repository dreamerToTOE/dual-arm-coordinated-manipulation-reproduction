#!/usr/bin/env python3
"""One separately frozen native SBL solve; reuse local/setup lifecycle, no path query."""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time
import qualify_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft as S
L=S.L

ROOT=Path(__file__).resolve().parents[1]
RUN='20261017_R2_ABB_SBL_PCS_SOLVE01'
CLAIM='P4_R2_ABB_SBL_PCS_SOLVE01_II_A01_SEED7_RANGE08_TRACE_ONCE_20W_40CPU_20261017'
LABEL='R2_RECONSTRUCTED_A01_ORIGINAL_SBL_PCS_SINGLE_NATIVE_SOLVE_SHADOW_V2'
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_sbl_pcs_shadow_v2')
STAGE=BUILD/'geometry_consistent_observed';BINARY=STAGE/'p4_abb_sbl_pcs'
PRE='reports/P4_FULL_R2_ABB_SBL_PCS_SINGLE_SOLVE_SHADOW_V2_PRE_DRAFT_20261017.md'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_sbl_pcs_solve_shadow_v2_draft.py'
REUSE='scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py'
LOCAL_REUSE='scripts/qualify_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'
LOCAL_RUN='20261017_R2_ABB_SBL_PCS_LOCAL01'
OWN=[str(Path(__file__).relative_to(ROOT)),SUPERVISOR,REUSE,LOCAL_REUSE,PRE]
# Only the shared lifecycle's explicit identity parameters change. Its process,
# budget timer/cleanup, loaded-library and build provenance bodies are reused.
L.RUN=RUN;L.BUILD=BUILD;L.STAGE=STAGE;L.BINARY=BINARY
L.BUILD_RUN='20261017_R2_ABB_SBL_PCS_BUILD02'
require=L.require;path=L.path;sha=L.sha;load=L.load;durable_new=L.durable_new

class Budget(S.Budget):
    def __init__(self,spec,started,cpu_start):
        super().__init__(spec,started,cpu_start)
        self.wall_cap=min(20.,3600.-spec['previous_r2_wall_s'])
        self.cpu_cap=min(40.,7200.-spec['previous_r2_cpu_s'])

class Session(S.Session):
    def __init__(self,target,work,budget,journal,counts,mode):
        super().__init__(target,work,budget,journal,counts,mode)
        self.command=[target['binary'],'II',str(work),'solve',mode]

def supervisor_proof(spec,protocol):
    ext=spec['external_supervision'];metadata=path(ext['metadata_path'])
    planned_raw=metadata.read_bytes().splitlines(keepends=True)[0];planned=json.loads(planned_raw)
    parent=os.getppid();row=L.stat_row(parent)
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
    return dict(actual_time_pid=parent,actual_time_start_ticks=int(row[19]),supervisor_pid=planned['supervisor_pid'],actual_argv=expected,
        planned_launch_line_sha256=hashlib.sha256(planned_raw).hexdigest(),time_inode=sibling.st_ino,time_device=sibling.st_dev,
        actual_time_output_fds=sorted(held),external_POST_required=True)

def draft_protocol(build_post,local_post):
    built=L.build_assets(build_post);prior=L.current_prior();post=load(local_post)
    local_execution=ROOT/'results/p4_full'/LOCAL_RUN/'execution.json'
    require(post['personnel_independent']is True and post['checks_failed']==0
        and post['checks_total']==post['checks_passed']>0 and post['status'].startswith('PASS')
        and post['independent_local_qualified']is True and post['external_supervision_qualified']is True,
        'PASS_INDEPENDENT_LOCAL_AND_EXTERNAL_POST_REQUIRED')
    require(post['execution_sha256']==sha(local_execution) and str(local_execution.relative_to(ROOT))in prior['execution_sha256'],
        'LOCAL_EXECUTION_MUST_BE_REAL_AND_CHARGED_IN_LATEST_LEDGER')
    e=load(local_execution)
    require(e['status']=='SOURCE_FIXED_LOCAL_OBSERVED_PENDING_INDEPENDENT_POST' and e['binary_execution_calls']==4
        and e['local_calls']==e['setup_calls']==4 and e['solve_calls']==e['public_project_calls']==0,
        'EXACT_FOUR_LOCAL_PREFIX_REQUIRED_BEFORE_SINGLE_SOLVE')
    points=[]
    for name,want in L.ENDPOINTS.items():
        require(sha(name)==want,'EXACT_A01_ENDPOINT_SOURCE_REQUIRED');value=load(name)
        require(value['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'and value['source_policy_collision_qualified']is True,
            'SAVED_RECONSTRUCTED_A01_QUALIFICATION_REQUIRED');points.append(value['selected_q_rad'])
    request=dict(operation='solve',environment='II',seed=7,range_rad=.8,solve_seconds=10.,
        separately_frozen_runtime_qualification=True,start_q12=points[0],goal_q12=points[1])
    require(len(json.dumps(request,separators=(',',':')).encode())+1<4096,'EXACT_ATOMIC_REQUEST_SIZE_REQUIRED')
    meshes={str(p):sha(p)for p in sorted((STAGE/'simulator').glob('*.tris'))};require(len(meshes)==20,'EXACT20_NATIVE_MESHES_REQUIRED')
    own={n:sha(n)for n in OWN};review_path=str(path(local_post).relative_to(ROOT))
    local_bound={review_path:sha(local_post),str(local_execution.relative_to(ROOT)):sha(local_execution)}
    retained=post.get('retained_sha256',post.get('source_sha256',{}))
    for name,want in retained.items():require(sha(name)==want,'LOCAL_POST_BOUND_ASSET_CHANGED');local_bound[name]=want
    bound={**built['files_sha256'],**local_bound,**L.ENDPOINTS,**meshes,**own,prior['ledger']:prior['ledger_sha256'],
        str(L.OMPL):L.OMPL_SHA,'/usr/bin/time':sha('/usr/bin/time'),'/usr/bin/python3':sha('/usr/bin/python3'),'/etc/ld.so.cache':sha('/etc/ld.so.cache')}
    return dict(schema='P4_R2_ABB_SBL_PCS_SINGLE_SOLVE_SHADOW_V2_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,latest_actual_charged_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,build_assets=built,local_independent_POST=review_path,
        actual_charge_prior=prior,previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],prior_execution_sha256=prior['execution_sha256'],
        schedule=[dict(schedule_index=0,fixture_name='single_solve',mode='trace',request=request)],runtime_meshes_sha256=meshes,own_source_sha256=own,bound_files_sha256=bound,
        budget=dict(wall_s=20.,cpu_s=40.,child_cpu_limit_s=20,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        maxima=dict(new_source_processes=1,source_requests=1,setup_calls=1,local_calls=0,public_project_calls=0,solve_calls=1,connect_fixture_calls=0,original_solve_seconds=10.),
        source_environment=L.SOURCE_ENV,system_preload_state=L.preload_state(),
        output_contract='One seed7 native ten-second trace solve only, one atomic write+EOF; preserve native exact/nonexact/exception, original reconstruction attempts, live branch/unknown connect, final native bytes and sidecar. No retry or automatic independent path query.',
        external_supervision=dict(required=True,sibling_path=f'results/p4_full/{RUN}.supervision.time.txt',format='%e %U %S %x',
            metadata_path=f'results/p4_full/{RUN}.supervision.jsonl',stderr_path=f'results/p4_full/{RUN}.supervision.stderr.log',charge_path=f'results/p4_full/{RUN}.supervision.charge.json',
            time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'),elapsed_decimal_upper_padding_s=.01,CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True),
        zero_calls=dict(compile=0,local_fixture=0,connect_fixture=0,independent_model_queries=0,old_component_requery=0,public13_project=0,VI_constructions=0,formal_table_I=0,independent_path_qualification=0),no_retry_reset_resume=True)

def validate(spec,protocol,execute=False):
    expected=draft_protocol(spec['build_assets']['personnel_independent_POST'],spec['local_independent_POST'])
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_SINGLE_SOLVE_RECIPE_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_SOLVE_REVIEW_FIELDS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'SOLVE_INDEPENDENT_REVIEW_ROOT_COMMIT_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in [*OWN,str(protocol.relative_to(ROOT)),spec['local_independent_POST']]:
        require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),'UNCOMMITTED_SOLVE_SOURCE_PROTOCOL_OR_REVIEW '+name)
    return commit

def check_response(response,row):
    require(response['status']in('SOURCE_EXACT_PENDING_INDEPENDENT_PATH_QUALIFICATION','SOURCE_NONEXACT_RETAINED')
        and response['operation']=='solve'and response['mode']=='trace','NATIVE_SINGLE_SOLVE_RESPONSE_REQUIRED')
    require(response['request']==row['request']and response['setup_dispatches']==1 and response['public_project_observations']==0
        and response['solve_calls']==1 and response['source_dispatch_started']==response['source_dispatch_completed']==1,
        'ONE_EXACT_NATIVE_SOLVE_DISPATCH_REQUIRED')
    require(response['remaining_live_motions']==0 and response['shadow_sidecar_saved_and_readback_equal']is True
        and response['native_output_capture_complete']is True and response['transport_evidence_saved_and_readback_equal']is True,
        'SINGLE_SOLVE_LIFETIME_AND_DURABLE_EVIDENCE_REQUIRED')
    require(response['source_started']==response['source_completed'],'SINGLE_SOLVE_TRACE_BALANCED_DISPATCH_REQUIRED')
    require(response['independent_path_qualified']is False and response['continuous_collision_certificate']is False,
        'NATIVE_EXACT_MUST_REMAIN_PENDING_INDEPENDENT_PATH_AND_CCD')
    return 'SOURCE_SINGLE_SOLVE_OBSERVED_PENDING_INDEPENDENT_POST'

def execute(spec,protocol):
    begun=time.monotonic();cpu0=L.own_reaped_cpu();commit=validate(spec,protocol,True);proof=supervisor_proof(spec,protocol)
    folder=ROOT/'results/p4_full'/RUN;claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists()and not L.active_p4(),'EXCLUSIVE_SINGLE_SOLVE_NO_RETRY_OR_OTHER_EXECUTION')
    budget=None;journal=None;sessions=[];counts=Counter();diagnostics=[];error=None;responses=[];copied={}
    record=dict(schema='P4_R2_ABB_SBL_PCS_SOLVE01_EXECUTION_V1',run_id=RUN,classification=LABEL,status='STOP_PREFIX_RETAINED',source_commit=commit,
        protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),budget=spec['budget'],bound_files_sha256=spec['bound_files_sha256'],
        prior_execution_sha256=spec['prior_execution_sha256'],actual_charge_prior=spec['actual_charge_prior'],previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],
        supervisor_launch_proof=proof,external_supervision_qualified=False,independent_saved_POST_required=True,independent_local_qualified=False,independent_path_qualified=False,
        continuous_collision_certificate=False,zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0,setup_calls=None,local_calls=0,public_project_calls=0,solve_calls=None,binary_execution_calls=0)
    try:
        durable_new(claim,dict(schema='P4_R2_ABB_SBL_PCS_SOLVE01_CLAIM_V1',run_id=RUN,protocol=record['protocol'],protocol_sha256=record['protocol_sha256'],source_commit=commit,budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=L.Journal(folder/'evidence.jsonl');journal.add('single_solve_setup',record=record)
        budget=Budget(spec,begun,cpu0);budget.start()
        for row in spec['schedule']:
            budget.check();one=folder/f"request_{row['schedule_index']:02}_{row['fixture_name']}_{row['mode']}";work=one/'work';(work/'simulator').mkdir(parents=True)
            for name,want in spec['runtime_meshes_sha256'].items():
                budget.check();target=work/'simulator'/Path(name).name
                with target.open('xb')as f:f.write(path(name).read_bytes())
                require(sha(target)==want,'RUNTIME_MESH_CHANGED');copied[str(target.relative_to(ROOT))]=want
            session=Session(spec['build_assets']['target'],work,budget,journal,counts,row['mode']);sessions.append(session);session.start()
            response=session.query(row['request']);responses.append(response);journal.add('parsed_response_before_gates',schedule_index=row['schedule_index'],response=response)
            result_status=check_response(response,row);session.finish(normal=True);budget.check()
            require(L.exact(L.raw_trace(bytes(session.raw['stderr'])),response['trace']or []),'RAW_STDERR_TRACE_MUST_MATCH_RESPONSE')
            raw=bytes(session.raw['stdout']);require(raw.endswith(b'\n')and len(raw.splitlines())==1 and json.loads(raw)==response,'ONE_COMPLETE_RESPONSE_REQUIRED')
        require(len(responses)==1 and counts['setup_dispatched']==1,'EXACT_ONE_SOLVE_REQUEST_COMPLETED_REQUIRED')
        record.update(status=result_status,setup_calls=1,local_calls=0,solve_calls=1)
    except BaseException as exc:
        error=exc;record['termination_reason']=repr(exc)
    finally:
        if budget is not None:budget.close()
        processes=list({s.proc.pid:s.proc for s in sessions if s.proc is not None}.values())
        for s in sessions:
            try:
                if s.proc is not None:L.kill_source_group(s.proc)
                s.finish(normal=False)
            except BaseException as exc:diagnostics.append(dict(stage='session_cleanup',error=repr(exc)))
        for p in processes:
            try:L.kill_source_group(p);p.wait(timeout=1.)
            except BaseException as exc:diagnostics.append(dict(stage='central_reap',pid=p.pid,error=repr(exc)))
        record['source_process_registry']=[dict(pid=s.proc.pid,returncode=s.proc.returncode,start_ticks=s.start_ticks,actual_after_reap_group=L.process_group_members(s.proc.pid),
            actual_pipe_EOF_observed=s.pipe_EOF_observed,stdin_closed_after_unique_request=s.stdin_closed_after_request,actual_request_sent=s.request_sent,
            request_bytes=None if s.request_raw is None else len(s.request_raw),request_sha256=None if s.request_raw is None else hashlib.sha256(s.request_raw).hexdigest(),
            loaded_scope=s.loaded_scope,close_group=s.close_group,close_poll_result=s.close_poll_result,close_poll_observations=s.close_poll_observations,
            close_postpoll_group=s.close_postpoll_group)for s in sessions if s.proc is not None]
        raw_gate=len(sessions)==1 and all(s.proc is not None and s.proc.returncode==0 and s.eof and s.closed and s.startup_complete and not s.pending and s.after_reap_group==[]and all(s.pipe_EOF_observed.values())for s in sessions)
        record['complete_source_raw_evidence_gate']=raw_gate;record['counts']=dict(counts);record['binary_execution_calls']=counts['source_process_started'];record['responses']=responses
        if record['status'].startswith('SOURCE_')and not raw_gate:record['status']='STOP_PROCESS_EOF_OR_EXIT_UNQUALIFIED'
        try:
            record['runtime_mesh_sha256']=copied;record['runtime_mesh_after_sha256']={n:sha(n)for n in copied};require(record['runtime_mesh_after_sha256']==copied,'RUNTIME_MESH_CHANGED')
            record['bound_files_after_sha256']={n:sha(n)for n in spec['bound_files_sha256']};require(record['bound_files_after_sha256']==spec['bound_files_sha256'],'BOUND_ASSET_CHANGED')
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim);require(sha(protocol)==record['protocol_sha256']and sha(claim)==record.get('claim_sha256'),'RECIPE_CHANGED')
            record['prior_execution_after_sha256']=L.current_prior()['execution_sha256'];require(L.current_prior()==spec['actual_charge_prior'],'PRIOR_CHANGED')
            require(L.preload_state()==spec['system_preload_state'],'PRELOAD_CHANGED')
            for s in sessions:
                if s.loaded_scope:require(all(sha(n)==want for n,want in s.loaded_scope['mapped_files_sha256'].items()),'MAPPED_ELF_CHANGED')
        except BaseException as exc:diagnostics.append(dict(stage='mandatory_hashes',error=repr(exc)))
        if journal is not None:
            try:
                for i,s in enumerate(sessions):
                    for channel,raw in s.raw.items():
                        p=folder/f'request_{i:02}_{channel}.bin'
                        with p.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
                        journal.add('final_raw_stream',schedule_index=i,channel=channel,bytes=len(raw),sha256=sha(p),path=str(p.relative_to(ROOT)),base64=base64.b64encode(raw).decode())
                journal.add('final_counts',counts=dict(counts),diagnostics=diagnostics);journal.finish();record['evidence_journal_sha256']=sha(folder/'evidence.jsonl')
                saved=[p for p in folder.rglob('*')if p.is_file()]
                for p in saved:
                    with p.open('rb')as f:os.fsync(f.fileno())
                record['retained_run_files_sha256']={str(p.relative_to(ROOT)):sha(p)for p in saved}
            except BaseException as exc:diagnostics.append(dict(stage='evidence_preservation',error=repr(exc)))
        record['diagnostics']=diagnostics;record.update(wall_s=time.monotonic()-begun,cpu_s=L.own_reaped_cpu()-cpu0+L.direct_live_cpu(processes))
        if record['wall_s']>=min(20.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(40.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_R2_ABB_SBL_PCS_SOLVE01_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=L.own_reaped_cpu()-cpu0+L.direct_live_cpu(processes),last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(20.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(40.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            durable_new(folder/'cost_receipt.jsonl',receipt);record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),independent_local_qualified=False,independent_POST_required=True)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status','').startswith('SOURCE_'),'SINGLE_SOLVE_TRANSPORT_DID_NOT_COMPLETE')

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--validate-draft',type=Path);g.add_argument('--protocol',type=Path)
    p.add_argument('--build-post',type=Path);p.add_argument('--local-post',type=Path);args=p.parse_args()
    if args.describe_protocol:
        require(args.build_post is not None and args.local_post is not None,'ACTUAL_BUILD_AND_LOCAL_POST_REQUIRED')
        print(json.dumps(draft_protocol(args.build_post,args.local_post),ensure_ascii=False,indent=2));return
    require(args.build_post is None and args.local_post is None,'REVIEW_PATHS_MUST_COME_FROM_EXACT_PROTOCOL')
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_SOLVE_DRAFT_VALIDATED_NO_EXECUTION');return
    execute(spec,protocol)
if __name__=='__main__':main()
