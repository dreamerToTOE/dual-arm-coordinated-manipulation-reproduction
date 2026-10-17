#!/usr/bin/env python3
"""Four fixed saved-input SBL local requests; reuse the qualified setup lifecycle."""
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
import qualify_p4_full_r2_abb_sbl_pcs_setup_draft as L

ROOT=Path(__file__).resolve().parents[1]
RUN='20261017_R2_ABB_SBL_PCS_LOCAL01'
CLAIM='P4_R2_ABB_SBL_PCS_LOCAL01_FIXED_POS_NEG_TRACE_PLAIN_15W_30CPU_20261017'
LABEL='R2_RECONSTRUCTED_SAVED_TREE_FIXTURE_ORIGINAL_SBL_LAZY_CONTROL_SHADOW_V2'
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_sbl_pcs_shadow_v2')
STAGE=BUILD/'geometry_consistent_observed';BINARY=STAGE/'p4_abb_sbl_pcs'
PRE='reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL_FIXED_SAVED_PRE_DRAFT_20261017.md'
FIXTURE='configs/p4_full/r2_abb_sbl_pcs_local_fixed_saved_v1.draft.json'
FIXTURE_SHA='4f3dc390920e0ca8e6a7441ced345d2f99305219b689753a96cc57509800e5ff'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'
REUSE='scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py'
OWN=[str(Path(__file__).relative_to(ROOT)),SUPERVISOR,REUSE,PRE,FIXTURE]
# Only the shared lifecycle's explicit identity parameters change. Its process,
# budget timer/cleanup, loaded-library and build provenance bodies are reused.
L.RUN=RUN;L.BUILD=BUILD;L.STAGE=STAGE;L.BINARY=BINARY
L.BUILD_RUN='20261017_R2_ABB_SBL_PCS_BUILD02'
require=L.require;path=L.path;sha=L.sha;load=L.load;durable_new=L.durable_new

class Budget(L.Budget):
    def __init__(self,spec,started,cpu_start):
        super().__init__(spec,started,cpu_start)
        self.wall_cap=min(15.,3600.-spec['previous_r2_wall_s'])
        self.cpu_cap=min(30.,7200.-spec['previous_r2_cpu_s'])

class Session(L.Session):
    def __init__(self,target,work,budget,journal,counts,mode):
        super().__init__(target,work,budget,journal,counts)
        self.command=[target['binary'],'II',str(work),'local',mode]

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

def draft_protocol(build_post,fixture_post):
    built=L.build_assets(build_post);prior=L.current_prior()
    require(sha(FIXTURE)==FIXTURE_SHA,'EXACT_SAVED_LOCAL_INPUT_REQUIRED')
    fixture=load(FIXTURE);review=load(fixture_post)
    require(review['personnel_independent']is True and review['checks_failed']==0
        and review['checks_total']==review['checks_passed']>0 and review['status'].startswith('PASS'),'PASS_INDEPENDENT_SAVED_FIXTURE_REVIEW_REQUIRED')
    retained=review.get('retained_sha256',review.get('source_sha256',{}))
    for name in (FIXTURE,PRE):require(retained.get(name,retained.get(str(path(name))))==sha(name),'FIXTURE_REVIEW_CURRENT_ASSET_SHA_REQUIRED '+name)
    schedule=copy.deepcopy(fixture['schedule'])
    require(len(schedule)==4 and [(s['fixture_name'],s['mode'])for s in schedule]==[('positive','trace'),('positive','plain'),('negative','trace'),('negative','plain')],'EXACT_FOUR_LOCAL_SCHEDULE_REQUIRED')
    source_refs={}
    for row in schedule:
        request=row['request'];request['separately_frozen_runtime_qualification']=True;request['fixture']['separately_frozen_local_fixture']=True
        require(len(json.dumps(request,separators=(',',':')).encode())+1<4096,'EXACT_ATOMIC_REQUEST_SIZE_REQUIRED')
        for ref in request['fixture']['saved_input_references']:
            require(sha(ref['path'])==ref['sha256'],'SAVED_SOURCE_CHANGED');source_refs[ref['path']]=ref['sha256']
    meshes={str(p):sha(p)for p in sorted((STAGE/'simulator').glob('*.tris'))};require(len(meshes)==20,'EXACT20_NATIVE_MESHES_REQUIRED')
    own={n:sha(n)for n in OWN};review_path=str(path(fixture_post).relative_to(ROOT))
    bound={**built['files_sha256'],**source_refs,**meshes,**own,review_path:sha(fixture_post),prior['ledger']:prior['ledger_sha256'],
        str(L.OMPL):L.OMPL_SHA,'/usr/bin/time':sha('/usr/bin/time'),'/usr/bin/python3':sha('/usr/bin/python3'),'/etc/ld.so.cache':sha('/etc/ld.so.cache')}
    return dict(schema='P4_R2_ABB_SBL_PCS_FIXED_LOCAL_SHADOW_V2_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,latest_actual_charged_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,build_assets=built,fixture_independent_POST=review_path,
        actual_charge_prior=prior,previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],prior_execution_sha256=prior['execution_sha256'],
        schedule=schedule,runtime_meshes_sha256=meshes,own_source_sha256=own,bound_files_sha256=bound,
        budget=dict(wall_s=15.,cpu_s=30.,child_cpu_limit_s=20,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        maxima=dict(new_source_processes=4,source_requests=4,setup_calls=4,local_calls=4,public_project_calls=0,solve_calls=0,connect_fixture_calls=0),
        source_environment=L.SOURCE_ENV,system_preload_state=L.preload_state(),
        output_contract='Four sequential fixed requests, one atomic write+EOF each; exact complete raw streams, reaped empty groups, native final bytes and durable sidecar saved. Any failure stops the schedule without replacement/retry.',
        external_supervision=dict(required=True,sibling_path=f'results/p4_full/{RUN}.supervision.time.txt',format='%e %U %S %x',
            metadata_path=f'results/p4_full/{RUN}.supervision.jsonl',stderr_path=f'results/p4_full/{RUN}.supervision.stderr.log',charge_path=f'results/p4_full/{RUN}.supervision.charge.json',
            time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'),elapsed_decimal_upper_padding_s=.01,CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True),
        zero_calls=dict(compile=0,solve=0,connect_fixture=0,independent_model_queries=0,old_component_requery=0,public13_project=0,VI_constructions=0,formal_table_I=0,independent_path_qualification=0),no_retry_reset_resume=True)

def validate(spec,protocol,execute=False):
    expected=draft_protocol(spec['build_assets']['personnel_independent_POST'],spec['fixture_independent_POST'])
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_FIXED_LOCAL_RECIPE_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_LOCAL_REVIEW_FIELDS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'LOCAL_INDEPENDENT_REVIEW_ROOT_COMMIT_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in [*OWN,str(protocol.relative_to(ROOT)),spec['fixture_independent_POST']]:
        require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),'UNCOMMITTED_LOCAL_SOURCE_PROTOCOL_OR_REVIEW '+name)
    return commit

def semantic(response):
    local=response['local']; trees={}
    for phase in ('before','after'):
        t=local[phase];trees[phase]=dict(native_tree_sizes=t['native_tree_sizes'],nodes=sorted(t['nodes'],key=lambda x:x['motion_id']))
    return dict(returned=local['source_isPathValid_returned'],trees=trees,setup_metadata=response['setup_metadata'],writer_metadata_attempts=response['writer_metadata_attempts'])

def check_response(response,row):
    fixture=load(FIXTURE)['fixtures'][row['fixture_name']];expected=fixture['expected_observations'];mode=row['mode']
    require(response['status']=='SOURCE_LOCAL_OBSERVED_PENDING_INDEPENDENT_QUALIFICATION'and response['operation']=='local'and response['mode']==mode,'NATIVE_LOCAL_RESPONSE_REQUIRED')
    require(response['request']==row['request']and response['setup_dispatches']==1 and response['public_project_observations']==response['solve_calls']==0
        and response['source_dispatch_started']==response['source_dispatch_completed']==1,'ONE_EXACT_LOCAL_REQUEST_DISPATCH_REQUIRED')
    local=response['local'];require(local['fixture_id']==fixture['fixture_id']and local['source_isPathValid_returned']is expected['source_isPathValid_returned'],'FIXED_LOCAL_RETURN_REQUIRED')
    for phase in ('before','after'):require(local[phase]['native_tree_sizes']==expected[f'native_tree_sizes_{phase}'],'FIXED_LOCAL_TREE_SIZES_REQUIRED')
    require(response['remaining_live_motions']==0 and response['writer_metadata_attempts']==[]and response['shadow_sidecar_saved_and_readback_equal']is True
        and response['native_output_capture_complete']is True and response['transport_evidence_saved_and_readback_equal']is True,'LOCAL_LIFETIME_AND_DURABLE_EVIDENCE_REQUIRED')
    require(len(response['native_file_evidence'])==5 and all(not f['exists']and f['absence_retained']is True for f in response['native_file_evidence']),'LOCAL_NATIVE_SAVE_MUST_NOT_DISPATCH')
    if mode=='trace':
        a=response['source_started'];b=response['source_completed'];require(a==b and a.get('isPathValid')==1 and a.get('save2file',0)==0,'LOCAL_TRACE_BALANCED_DISPATCH_REQUIRED')
        rbs=a.get('state_rbs',0)+a.get('vector_rbs',0)
        if row['fixture_name']=='positive':require(rbs>=2 and a.get('removeMotion',0)==0,'NONTRIVIAL_POSITIVE_RBS_REQUIRED')
        else:require(rbs==0 and a.get('removeMotion')==2,'NATURAL_BRANCH_REJECTION_TWO_RECURSIVE_REMOVALS_REQUIRED')
    else:require(response['trace']is None and response['source_started']is None and response['source_completed']is None,'PLAIN_MODE_UNOBSERVED_SOURCE_COUNTS_REQUIRED')
    return semantic(response)

def execute(spec,protocol):
    begun=time.monotonic();cpu0=L.own_reaped_cpu();commit=validate(spec,protocol,True);proof=supervisor_proof(spec,protocol)
    folder=ROOT/'results/p4_full'/RUN;claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists()and not L.active_p4(),'EXCLUSIVE_FIXED_LOCAL_NO_RETRY_OR_OTHER_EXECUTION')
    budget=None;journal=None;sessions=[];counts=Counter();diagnostics=[];error=None;responses=[];semantics={};copied={}
    record=dict(schema='P4_R2_ABB_SBL_PCS_LOCAL01_EXECUTION_V1',run_id=RUN,classification=LABEL,status='STOP_PREFIX_RETAINED',source_commit=commit,
        protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),budget=spec['budget'],bound_files_sha256=spec['bound_files_sha256'],
        prior_execution_sha256=spec['prior_execution_sha256'],actual_charge_prior=spec['actual_charge_prior'],previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],
        supervisor_launch_proof=proof,external_supervision_qualified=False,independent_saved_POST_required=True,independent_local_qualified=False,independent_path_qualified=False,
        continuous_collision_certificate=False,zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0,setup_calls=None,local_calls=None,public_project_calls=0,solve_calls=0,binary_execution_calls=0)
    try:
        durable_new(claim,dict(schema='P4_R2_ABB_SBL_PCS_LOCAL01_CLAIM_V1',run_id=RUN,protocol=record['protocol'],protocol_sha256=record['protocol_sha256'],source_commit=commit,budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=L.Journal(folder/'evidence.jsonl');journal.add('local_setup',record=record)
        budget=Budget(spec,begun,cpu0);budget.start()
        for row in spec['schedule']:
            budget.check();one=folder/f"request_{row['schedule_index']:02}_{row['fixture_name']}_{row['mode']}";work=one/'work';(work/'simulator').mkdir(parents=True)
            for name,want in spec['runtime_meshes_sha256'].items():
                budget.check();target=work/'simulator'/Path(name).name
                with target.open('xb')as f:f.write(path(name).read_bytes())
                require(sha(target)==want,'RUNTIME_MESH_CHANGED');copied[str(target.relative_to(ROOT))]=want
            session=Session(spec['build_assets']['target'],work,budget,journal,counts,row['mode']);sessions.append(session);session.start()
            response=session.query(row['request']);responses.append(response);journal.add('parsed_response_before_gates',schedule_index=row['schedule_index'],response=response)
            value=check_response(response,row);session.finish(normal=True);budget.check()
            require(L.exact(L.raw_trace(bytes(session.raw['stderr'])),response['trace']or []),'RAW_STDERR_TRACE_MUST_MATCH_RESPONSE')
            raw=bytes(session.raw['stdout']);require(raw.endswith(b'\n')and len(raw.splitlines())==1 and json.loads(raw)==response,'ONE_COMPLETE_RESPONSE_REQUIRED')
            if row['mode']=='trace':semantics[row['fixture_name']]=value
            else:require(L.exact(value,semantics[row['fixture_name']]),'PLAIN_TRACE_SEMANTICS_MUST_MATCH')
        require(len(responses)==4 and counts['setup_dispatched']==4,'EXACT_FOUR_REQUESTS_COMPLETED_REQUIRED')
        record.update(status='SOURCE_FIXED_LOCAL_OBSERVED_PENDING_INDEPENDENT_POST',setup_calls=4,local_calls=4,plain_trace_semantics_equal=True)
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
        raw_gate=len(sessions)==4 and all(s.proc is not None and s.proc.returncode==0 and s.eof and s.closed and s.startup_complete and not s.pending and s.after_reap_group==[]and all(s.pipe_EOF_observed.values())for s in sessions)
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
        if record['wall_s']>=min(15.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(30.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_R2_ABB_SBL_PCS_LOCAL01_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=L.own_reaped_cpu()-cpu0+L.direct_live_cpu(processes),last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(15.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(30.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            durable_new(folder/'cost_receipt.jsonl',receipt);record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),independent_local_qualified=False,independent_POST_required=True)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status','').startswith('SOURCE_'),'FIXED_LOCAL_TRANSPORT_DID_NOT_COMPLETE')

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--validate-draft',type=Path);g.add_argument('--protocol',type=Path)
    p.add_argument('--build-post',type=Path);p.add_argument('--fixture-post',type=Path);args=p.parse_args()
    if args.describe_protocol:
        require(args.build_post is not None and args.fixture_post is not None,'ACTUAL_BUILD_AND_FIXTURE_POST_REQUIRED')
        print(json.dumps(draft_protocol(args.build_post,args.fixture_post),ensure_ascii=False,indent=2));return
    require(args.build_post is None and args.fixture_post is None,'REVIEW_PATHS_MUST_COME_FROM_EXACT_PROTOCOL')
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_LOCAL_DRAFT_VALIDATED_NO_EXECUTION');return
    execute(spec,protocol)
if __name__=='__main__':main()
