#!/usr/bin/env python3
"""L12 fixed three-edge local seam draft; no model runs at import.

Only stdlib and the independently reviewed D64 transport/builder are reused.
No describe/protocol/prior snapshot is created until real D64 PASS is saved.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import qualify_p4_full_r2_abb_cbirrt_d_distance_draft as transport
builder=transport.builder
ROOT=builder.ROOT
RUN='20261015_R2_ABB_CBIRRT_D_LOCAL01'
CLAIM='P4_R2_ABB_CBIRRT_D_FIXED12_LOCAL_30W_60CPU_20261016'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_LOCAL_PRE_DRAFT_20261016.md'
STAGED_PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_STAGED_QUALIFICATION_PRE_DRAFT_20261016.md'
ATTEMPTS='results/p4_full/20261015_R2_ABB_RRT_PCS_E2E01/runtime/reconstruction_attempts.jsonl'
ATTEMPTS_SHA='2aea2a4b79c280d09543a3d2f7f675422c3479c6440d4802e33ca5c66f7c2b26'
PATH_RUN='results/p4_full/20261015_R2_ABB_RRT_PATH01'
FACTOR='distance_destination_fix'
TRANSPORT='scripts/qualify_p4_full_r2_abb_cbirrt_d_distance_draft.py'
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),PRE,STAGED_PRE,TRANSPORT,*transport.OWN]))
require=transport.require
sha=transport.sha
load=transport.load
path=transport.path
exact=transport.exact
bits=transport.bits
durable_new=transport.durable_new
StopQualification=transport.StopQualification
PASS='PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED'

def fixed_edges():
    """Transcribe the original three saved high-precision state-level edges."""
    require(sha(ATTEMPTS)==ATTEMPTS_SHA,'ORIGINAL_THREE_EDGE_BYTES_CHANGED')
    rows=[json.loads(raw)for raw in path(ATTEMPTS).read_bytes().splitlines()]
    expected=[(0,3,80),(1,3,65),(0,0,34)]
    require(len(rows)==3,'EXACT_THREE_ORIGINAL_EDGES_REQUIRED')
    edges=[]
    for i,(row,(role,branch,count))in enumerate(zip(rows,expected)):
        require(row['schema']=='P4_ABB_RRT_PCS_RECONSTRUCTION_V1'and row['attempt_index']==i
            and row['observation']=='ORIGINAL_STATE_LEVEL_CALL_COMPLETED_POST_RETURN'and row['returned']is True,'OLD_EDGE_NOT_EXACT_SUCCESSFUL_SOURCE_RETURN')
        require((row['active_chain'],row['branch'],len(row['path_q12']))==(role,branch,count),'OLD_FIXED_ROLE_BRANCH_NODE_COUNT_CHANGED')
        require(all(len(q)==12 and all(type(v)in(int,float)and math.isfinite(v)for v in q)for q in row['path_q12']),'FINITE_ORIGINAL_Q12_PATH_REQUIRED')
        require(exact(row['qa12'],row['path_q12'][0])and exact(row['qb12'],row['path_q12'][-1]),'OLD_EDGE_ENDPOINTS_CHANGED')
        require(math.sqrt(math.fsum((a-b)**2 for a,b in zip(row['qa12'],row['qb12'])))>.05,'ORIGINAL_NONTRIVIAL_EDGE_REQUIRED')
        edges.append(dict(edge_index=i,environment='II',active_chain=role,branch=branch,qa12=row['qa12'],qb12=row['qb12'],
            reference_path_q12=row['path_q12'],reference_node_count=count,reference_midpoint_count=count-2,
            source_attempt=ATTEMPTS,source_attempt_sha256=ATTEMPTS_SHA))
    return edges

def saved_certificate(edges):
    """Bind existing177-node physical proofs; never evaluate a new physical gate."""
    ep=PATH_RUN+'/execution.json';e=load(ep);pp=e['protocol'];p=load(pp);queue=p['fixed_queue']
    require(e['status']=='PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH'and e['full_queue_checked']is True
        and e['node_count']==e['completed_nodes']==e['qualified_nodes']==177 and e['uncompleted_node_ids']==[],'OLD177_FULL_PHYSICAL_CERTIFICATE_REQUIRED')
    require(sha(pp)==e['protocol_sha256']==e['protocol_after_sha256']and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'],'OLD177_PROTOCOL_OR_CLAIM_CHANGED')
    require(e['bound_files_sha256']==e['bound_files_after_sha256']and all(sha(name)==want for name,want in e['bound_files_sha256'].items()),'OLD177_BOUND_INPUT_CHANGED')
    require(len(queue['nodes'])==177 and len(queue['edges'])==3,'OLD177_FIXED_QUEUE_CHANGED')
    files={name:sha(name)for name in[ep,pp,e['claim'],ATTEMPTS]};files.update(e['bound_files_sha256'])
    seen=set()
    for edge,old in zip(edges,queue['edges']):
        ids=old['node_ids'];mapped=[queue['nodes'][i]for i in ids]
        require(old['edge_index']==edge['edge_index']and old['active_chain']==edge['active_chain']and old['branch']==edge['branch']
            and old['selected_attempt_index']==edge['edge_index']and exact(mapped,edge['reference_path_q12']),'OLD177_EDGE_Q_OR_BRANCH_MAP_CHANGED')
        require(len(old['leaf_distances_rad'])==len(ids)-1 and all(v<.05 for v in old['leaf_distances_rad']),'OLD177_LEAF_CERTIFICATE_REQUIRED')
        seen.update(ids)
    require(seen==set(range(177)),'ALL177_UNIQUE_NODES_MUST_BE_COVERED')
    for i,q in enumerate(queue['nodes']):
        prefix=PATH_RUN+f'/node_{i:05d}';n=load(prefix+'.json');c=load(prefix+'_collision_response.json')
        require(n['node_id']==i and n['stage']=='COMPLETED'and n['qualified']is True and n['math_qualified']is True
            and n['limits']['legal']is True and exact(n['q12'],q),'OLD177_NODE_PROOF_NOT_QUALIFIED')
        require(n['closure']['position_max_abs']<=1e-5 and n['closure']['rotation_matrix_max_abs']<=1e-5
            and all(a['branch_pass']is True for a in n['edge_assignments']),'OLD177_CLOSURE_BRANCH_PROOF_CHANGED')
        require(n['collision']==c and c['environment']=='II'and c['status']=='CHECKED'and c['collision']is False
            and c['selected_variant']=='aligned'and c['continuous_collision_certificate']is False,'OLD177_COLLISION_PROOF_CHANGED')
        for suffix in('.json','_arm1.json','_arm2.json','_math.json','_collision_response.json'):files[prefix+suffix]=sha(prefix+suffix)
    return dict(execution=ep,execution_sha256=sha(ep),qualified_unique_nodes=177,edge_node_counts=[80,65,34],
        reuse_rule='Only if every new reconstruction M is binary64-identical to its entire old path, including both endpoints. No new physical query, epsilon, truncation or changed role/branch.',
        continuous_collision_certificate=False,files_sha256=files)

def schedule(edges):
    rows=[]
    for mode in('plain','trace'):
        for edge in edges:
            for call in('rbs','reconstruct'):
                request=dict(case_id=f"edge{edge['edge_index']}_{call}",operation='local',environment='II',
                    qa12=edge['qa12'],qb12=edge['qb12'],active_chain=edge['active_chain'],branch=edge['branch'],local_call=call)
                rows.append(dict(dispatch_index=len(rows),factor=FACTOR,mode=mode,environment='II',edge_index=edge['edge_index'],local_call=call,request=request))
    require(len(rows)==12,'FIXED_L12_SCHEDULE_REQUIRED');return rows

def prior():
    files=sorted(p for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if p.parent.name!=RUN)
    rows=[load(p)for p in files]
    require(all(all(type(r[k])in(int,float)and math.isfinite(r[k])and r[k]>=0 for k in('wall_s','cpu_s'))for r in rows),'FINITE_PRIOR_OWN_COSTS_REQUIRED')
    return {str(p.relative_to(ROOT)):sha(p)for p in files},math.fsum(r['wall_s']for r in rows),math.fsum(r['cpu_s']for r in rows)

def prerequisites():
    assets=transport.build_assets();ep='results/p4_full/'+transport.RUN+'/execution.json'
    require(path(ep).is_file(),'WAIT_REAL_D64_RESULT_NO_PLACEHOLDER_PROTOCOL')
    e=load(ep);require(e['status']=='PASS_FIXED16_ACTIVE_DISTANCE_INTERFACE'and len(e['completed_dispatch_ids'])==64
        and e['complete_source_raw_evidence_gate']is True and e['source_process_registry_complete_gate']is True
        and e['full_run_raw_body_count_gate']is True and not e['UNKNOWN_uncompleted_fixtures'],'D64_INTERFACE_GATE_REQUIRED_BEFORE_L12')
    require(e['bound_files_sha256']==e['bound_files_after_sha256']and all(sha(name)==want for name,want in e['bound_files_sha256'].items()),'D64_BOUND_ASSETS_CHANGED')
    require(sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'],'D64_RECIPE_CHANGED')
    files=dict(assets['files_sha256'])
    for name in[e['protocol'],e['claim'],*(str(p.relative_to(ROOT))for p in path(ep).parent.rglob('*')if p.is_file())]:files[name]=sha(name)
    return dict(build=assets,distance_execution=ep,distance_execution_sha256=sha(ep),files_sha256=files)

def draft_protocol():
    ready=prerequisites();edges=fixed_edges();certificate=saved_certificate(edges);previous,wall,cpu=prior()
    bound={**ready['files_sha256'],**certificate['files_sha256'],**{name:sha(name)for name in OWN}}
    return dict(schema='P4_R2_ABB_CBIRRT_D_FIXED12_LOCAL_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,latest_actual_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification='R2_NUMERICS / D_FIXED_STAGE_ONLY / AUTHOR_STATE_RBS_AND_RECONSTRUCTION_SEAM / REUSE_SAVED177_DISCRETE_PHYSICAL_PROOFS',
        prerequisites=ready,fixed_edges=edges,fixed_schedule=schedule(edges),saved177_certificate=certificate,
        own_source_sha256={name:sha(name)for name in OWN},bound_files_sha256=bound,
        prior_execution_sha256=previous,previous_r2_wall_s=wall,previous_r2_cpu_s=cpu,
        budget=dict(wall_s=30.,cpu_s=60.,child_cpu_limit_s=30,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        maxima=dict(source_processes=2,top_level_local_dispatches=12,trace_state_rbs=3,trace_state_reconstruct=3,plain_trace_top_level_comparisons=6),
        gates=dict(all12_return_true=True,all3_nontrivial=True,full_reconstruction_binary64_equal_old=True,exact_roles_branches=True,
            source_RBS_tol_rad=.05,source_RBS_max_depth=150,source_withObs=True,plain_trace_external_binary64_equal=True,
            trace_rbs_reconstruct_projection_sequence_binary64_equal=True,trace_projection_outputs_equal_old_interior_multiset=True,
            trace_nested_entry_return_and_raw_EOF=True,no_new_independent_physical_queries=True),
        source_body_counts='Only trace entry/return observed; original RBS performs its own fixed IK/FK/collision. Plain inner starts/completions UNOBSERVED. Constructor mesh_load once on trace, not six repeats.',
        RNG_boundary='Local driver constructs only SVC; no CBi, direct CBi RNG member, setSeed or srand. No random sampling route. Unhooked unrelated library internals remain UNOBSERVED.',
        zero_calls=dict(compile=0,independent_arm_FK_J=0,independent_collision_adapter=0,NR=0,activeDistance=0,CBi_constructor=0,solve=0,VI_constructions=0,formal_table_I=0),
        failure_policy='Keep every raw response before gates; stop on any false/different M, no retry, new edge, threshold, truncation, smoothing, or new physical checks.',
        no_retry_reset_resume=True,full_planner_path_or_RSS_qualified=False)

def validate(spec,protocol,execute=False):
    expected=draft_protocol();require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_L12_RECIPE_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_L12_REVIEW_BOOLEANS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'L12_REVIEW_AND_ROOT_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in[*OWN,str(protocol.relative_to(ROOT))]:
        subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        require(not subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True),'UNCOMMITTED '+name)
    for name,want in spec['own_source_sha256'].items():require(hashlib.sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()==want,'COMMIT_BLOB_MISMATCH '+name)
    return commit

class Budget(transport.Budget):
    def __init__(self,spec,started,cpu_start):
        super().__init__(spec,started,cpu_start)
        # Parent stores this object before inherited start() installs SIGALRM.
        self.wall_cap=min(30.,3600.-spec['previous_r2_wall_s']);self.cpu_cap=min(60.,7200.-spec['previous_r2_cpu_s'])
        require(min(self.wall_cap,self.cpu_cap)>0,'L12_TOTAL_BUDGET_EXHAUSTED')

class Session(transport.Session):
    OPERATION='local'
    def query(self,request,counts):
        self.budget.check();counts['local_dispatch_attempted']+=1
        raw=json.dumps(request,separators=(',',':'),allow_nan=False).encode()+b'\n'
        require(len(raw)<4096,'ATOMIC_SMALL_LOCAL_REQUEST_REQUIRED');require(self.proc.poll()is None,'SOURCE_EXITED_BEFORE_LOCAL_REQUEST')
        sent=os.write(self.proc.stdin.fileno(),raw);require(sent==len(raw),'INCOMPLETE_LOCAL_WRITE_NO_RETRY');counts['local_dispatched']+=1
        while b'\n'not in self.pending:
            self.pump()
            if not self.selector.get_map():raise StopQualification('EOF_WITHOUT_LOCAL_RESPONSE')
        line,self.pending=self.pending.split(b'\n',1);counts['local_response_line_observed']+=1;return line

def trace_audit(response,fixture,edge):
    """Check actual source nested observations; no FK/IK/collision added."""
    trace=response['trace'];stack=[];pairs=[];started=Counter();completed=Counter();serial=0
    allowed={'state_rbs','vector_rbs','state_reconstruct','vector_reconstruct','fixed_branch_project','native_fk','native_ik','collision'}
    for row in trace:
        kind=row['kind'];require(kind in allowed,'UNEXPECTED_LOCAL_SOURCE_BODY '+kind)
        if row['event']=='entered':
            serial+=1;require(row['id']==serial,'LOCAL_TRACE_ENTRY_SERIAL_CHANGED');stack.append(row);started[kind]+=1
        else:
            require(row['event']=='completed'and stack,'LOCAL_TRACE_UNPAIRED_RETURN');entered=stack.pop()
            require((row['id'],kind)==(entered['id'],entered['kind']),'LOCAL_TRACE_STACK_MISMATCH');pairs.append((entered,row));completed[kind]+=1
    require(not stack and started==completed and dict(started)==response['source_started']==response['source_completed'],'LOCAL_ACTUAL_BODY_COUNTS_UNBALANCED')
    top='state_rbs'if fixture['local_call']=='rbs'else'state_reconstruct';vector='vector_rbs'if fixture['local_call']=='rbs'else'vector_reconstruct'
    require(trace[0]['kind']==trace[-1]['kind']==top and trace[0]['id']==trace[-1]['id']==1 and trace[-1]['result']['returned']is True,'EXACT_TRUE_STATE_LEVEL_BODY_REQUIRED')
    args=trace[0]['args'];req=fixture['request'];require(exact(args['qa12'],req['qa12'])and exact(args['qb12'],req['qb12'])
        and args['active_chain']==req['active_chain']and args['branch']==req['branch'],'LOCAL_TRACE_TOP_INPUT_CHANGED')
    interior=edge['reference_path_q12'][1:-1];midpoints=edge['reference_midpoint_count']
    expected={top:1,vector:2*midpoints+1,'fixed_branch_project':midpoints,'native_fk':midpoints,'native_ik':midpoints,'collision':midpoints}
    require(dict(started)==expected,'FIXED_NONTRIVIAL_SOURCE_RECURSION_COUNTS_CHANGED')
    projection=[]
    for entered,returned in sorted(pairs,key=lambda pair:pair[0]['id']):
        kind=entered['kind'];result=returned['result']
        if kind in('state_rbs','vector_rbs','state_reconstruct','vector_reconstruct','native_ik'):require(result['returned']is True,'LOCAL_SOURCE_BODY_FALSE_RETAINED')
        if kind=='collision':require(result['returned']==0,'LOCAL_SOURCE_COLLISION_NOT_CLEAR')
        if kind!='fixed_branch_project':continue
        a=entered['args'];r=result;require(a['active_chain']==edge['active_chain']and a['branch']==edge['branch']and r['returned']is True,'FIXED_BRANCH_PROJECT_NOT_ORIGINAL_TRUE')
        active=slice(6*edge['active_chain'],6*(edge['active_chain']+1));require(exact(a['q12'][active],r['q12'][active]),'LOCAL_PROJECTION_CHANGED_ACTIVE_COORDINATES')
        projection.append(dict(input=a,returned=r))
    require(Counter(bits(x['returned']['q12'])for x in projection)==Counter(bits(q)for q in interior),'PROJECTED_MIDPOINTS_NOT_EXACT_OLD_PATH_INTERIOR')
    if fixture['local_call']=='reconstruct':require(exact(trace[-1]['result']['path_q12'],edge['reference_path_q12']),'SOURCE_STATE_RECONSTRUCT_TRACE_M_NOT_EXACT_OLD')
    return dict(started=started,completed=completed,projection_sequence=projection)


def execute(spec,protocol):
    """Frozen L12 execution only; not invoked during draft preparation."""
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN;claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXCLUSIVE_L12_OUTPUT_AND_CLAIM_NO_RETRY')
    require(not builder.active_p4(),'OTHER_ACTIVE_P4_EXECUTION');require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_BEFORE_L12_CLAIM')
    begun=time.monotonic();cpu_start=transport.own_reaped_cpu();budget=None;events=None;sessions={};responses={};audits={};counts=Counter();diagnostics=[];current=None;error=None;runtime=folder/'runtime'
    record=dict(schema='P4_R2_ABB_CBIRRT_D_FIXED12_LOCAL_EXECUTION_DRAFT_V1',run_id=RUN,source_commit=commit,status='STOP_PREFIX_RETAINED',classification=spec['classification'],
        protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),budget=spec['budget'],
        bound_files_sha256=spec['bound_files_sha256'],prior_execution_sha256=spec['prior_execution_sha256'],previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],
        started_at_utc=builder.utc(),zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0,full_planner_path_or_RSS_qualified=False)
    def event(kind,**fields):
        counts[kind+'_events']+=1
        if events is not None:events.write(json.dumps(dict(event=kind,at_utc=builder.utc(),**fields),allow_nan=False)+'\n');events.flush()
    try:
        durable_new(claim,dict(schema='P4_R2_ABB_CBIRRT_D_FIXED12_LOCAL_CLAIM_DRAFT_V1',claim_id=CLAIM,source_commit=commit,created_at_utc=builder.utc(),
            protocol=record['protocol'],protocol_sha256=record['protocol_sha256'],budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();runtime.mkdir();durable_new(folder/'setup_started.json',record)
        events=(folder/'events.jsonl').open('x',buffering=1);budget=Budget(spec,begun,cpu_start);budget.start()
        target=spec['prerequisites']['build']['targets'][FACTOR]
        for fixture in spec['fixed_schedule']:
            budget.check();i=fixture['dispatch_index'];mode=fixture['mode'];edge=spec['fixed_edges'][fixture['edge_index']]
            current=dict(fixture=fixture,stage='REQUEST_RETAINED');durable_new(folder/f'local_{i:02d}_request.json',fixture['request'])
            if mode not in sessions:
                sessions[mode]=Session(FACTOR,mode,'II',target,runtime,budget,event);sessions[mode].start()
            session=sessions[mode];current['stage']='SOURCE_DISPATCH_STARTED';event('local_dispatch_started',fixture=fixture)
            raw=session.query(fixture['request'],counts)
            with(folder/f'local_{i:02d}_raw_response_line.bin').open('xb')as f:f.write(raw+b'\n');f.flush();os.fsync(f.fileno())
            counts['raw_local_response_lines_retained']+=1;current['stage']='RAW_RESPONSE_RETAINED';response=json.loads(raw)
            durable_new(folder/f'local_{i:02d}_raw_response.json',response);counts['raw_local_response_JSON_retained']+=1
            require(response['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1'and response['status']=='SOURCE_INTERFACE_COMPLETED_NOT_QUALIFIED','LOCAL_SOURCE_INTERFACE_UNQUALIFIED')
            require(response['environment']=='II'and response['operation']=='local'and response['mode']==mode and exact(response['request'],fixture['request']),'LOCAL_RESPONSE_REQUEST_CHANGED')
            require(response['source_dispatch_started']==response['source_dispatch_completed']==1 and response['returned']is True
                and response['solve_calls']==response['formal_table_I_calls']==0 and response['independent_path_qualified']is False,'LOCAL_FALSE_OR_SCOPE_CHANGED')
            for arm in('qa12','qb12'):require(bits(response[arm+'_after'])==bits(fixture['request'][arm])==response[arm+'_binary64_after'],'LOCAL_MUTATED_INPUT_STATE')
            c=response['construction'];require(type(response['source_counts_observed'])is bool and response['source_counts_observed']==(mode=='trace')
                and type(c['source_counts_observed'])is bool and c['source_counts_observed']==(mode=='trace'),'LOCAL_OBSERVATION_FLAGS_CHANGED')
            require(c['svc_only_constructor_dispatch_completed']==1 and c['cbirrt_constructor_dispatch_completed']==c['ompl_setSeed_calls_completed']==c['srand_calls_completed']==c['source_direct_rng_member_initializations_structural']==0,'LOCAL_MUST_CONSTRUCT_ONLY_SVC_NO_SEED_OR_CBI')
            if session.construction is None:session.construction=c
            else:require(exact(session.construction,c),'LOCAL_CONSTRUCTION_CHANGED_WITHIN_PROCESS')
            if mode=='trace':
                require(c['source_started']==c['source_completed']=={'mesh_load':1}and len(c['trace'])==2,'LOCAL_ONLY_MESH_CONSTRUCTION_EXPECTED')
                a,b=c['trace'];require(a['event']=='entered'and b['event']=='completed'and a['kind']==b['kind']=='mesh_load'and a['id']==b['id']==1 and a['args']=={}and b['result']=={},'LOCAL_CONSTRUCTION_TRACE_UNPAIRED')
                audits[(fixture['edge_index'],fixture['local_call'])]=trace_audit(response,fixture,edge)
            else:
                for value in(response,c):require(value['trace']is None and value['source_started']is None and value['source_completed']is None,'PLAIN_LOCAL_INTERNALS_UNOBSERVED')
            if fixture['local_call']=='reconstruct':require(exact(response['path_q12'],edge['reference_path_q12']),'LOCAL_COMPLETE_M_BINARY64_DIFFERS_OLD_NO_EPSILON_OR_REPLACEMENT')
            metric=dict(dispatch_index=i,edge_index=fixture['edge_index'],mode=mode,local_call=fixture['local_call'],returned=True,source_state_inputs_unchanged=True,
                complete_M_binary64_equals_old=True if fixture['local_call']=='reconstruct'else None,source_inner_calls_observed=mode=='trace',new_independent_physical_queries=0)
            durable_new(folder/f'local_{i:02d}_qualification.json',metric);responses[(mode,fixture['edge_index'],fixture['local_call'])]=response;session.responses.append(response);counts['local_completed']+=1;current=None
            event('local_completed',dispatch_index=i)
            if len(session.responses)==6:session.finish(time.monotonic()+budget.remaining(),normal=True)
        require(len(sessions)==2 and counts['local_completed']==12,'FULL_L12_REQUIRED_NO_PREFIX_PASS')
        comparisons=[]
        for edge in spec['fixed_edges']:
            i=edge['edge_index']
            for call in('rbs','reconstruct'):
                require(exact(transport.normalize_response(responses[('plain',i,call)]),transport.normalize_response(responses[('trace',i,call)])),'PLAIN_TRACE_LOCAL_EXTERNAL_BINARY64_MISMATCH')
                comparisons.append(dict(edge_index=i,local_call=call,passed=True))
            require(exact(audits[(i,'rbs')]['projection_sequence'],audits[(i,'reconstruct')]['projection_sequence']),'TRACE_RBS_RECONSTRUCT_PROJECTION_SEQUENCE_CHANGED')
        durable_new(folder/'plain_trace_comparisons.json',comparisons);record['plain_trace_comparisons']=len(comparisons)
        record['reused_saved177_certificate']=spec['saved177_certificate'];record['new_independent_physical_queries']=0;record['status']=PASS
    except BaseException as exc:
        if budget is not None:budget.close()
        error=exc;record['termination_reason']=repr(exc)
        if current is not None and folder.is_dir():
            try:durable_new(folder/'stopped_partial_request.json',current)
            except BaseException as saved:diagnostics.append(dict(stage='save_partial',error=repr(saved)))
        try:event('stopped',reason=repr(exc))
        except BaseException as saved:diagnostics.append(dict(stage='save_stopped_event',error=repr(saved)))
    finally:
        if budget is not None:budget.close()
        processes=transport.all_source_processes(budget,sessions)
        for proc in processes:
            try:transport.kill_source_process(proc)
            except BaseException as exc:diagnostics.append(dict(stage='central_kill',pid=proc.pid,error=repr(exc)))
        deadline=time.monotonic()+2.
        for session in sessions.values():
            try:session.finish(deadline,normal=False)
            except BaseException as exc:diagnostics.append(dict(stage='session_cleanup',mode=session.mode,error=repr(exc)))
        for proc in processes:
            try:transport.kill_source_process(proc);proc.wait(timeout=1.)
            except BaseException as exc:diagnostics.append(dict(stage='central_reap',pid=proc.pid,error=repr(exc)))
        registry=[dict(pid=p.pid,returncode=p.returncode,reaped=p.returncode is not None)for p in processes]
        bindings={};raw_started=Counter();raw_completed=Counter()
        for mode,session in sessions.items():
            try:
                actual,tails=transport.trace_file(session.base.with_suffix('.stderr'));expected=[]
                if mode=='trace'and session.construction is not None:
                    expected.extend(session.construction['trace'])
                    for response in session.responses:expected.extend(response['trace'])
                good=bool(session.startup_complete and session.eof_drained and session.closed and not session.pending and not tails and exact(actual,expected)and session.proc is not None and session.proc.returncode==0)
                bindings[mode]=dict(completed_responses=len(session.responses),startup_complete=session.startup_complete,pipe_EOF_drained=session.eof_drained,
                    cleanup_closed=session.closed,unexpected_stdout_tail_bytes=len(session.pending),process_returncode=None if session.proc is None else session.proc.returncode,
                    source_close_process_group=session.cleanup_group,actual_trace_events=len(actual),expected_trace_events=len(expected),raw_trace_binary64_matches=exact(actual,expected),
                    unparseable_trace_tails=tails,complete_raw_evidence_gate=good,
                    raw_streams={channel:dict(path=str(session.base.with_suffix('.'+channel).relative_to(ROOT)),sha256=sha(session.base.with_suffix('.'+channel)),bytes=session.base.with_suffix('.'+channel).stat().st_size)for channel in('stdout','stderr')})
                for row in actual:
                    if row['event']=='entered':raw_started[row['kind']]+=1
                    elif row['event']=='completed':raw_completed[row['kind']]+=1
            except BaseException as exc:diagnostics.append(dict(stage='raw_binding',mode=mode,error=repr(exc)))
        registered={s.base.with_suffix('.stderr')for s in sessions.values()};unregistered=[]
        for filename in sorted(runtime.glob('*.stderr'))if runtime.is_dir()else[]:
            if filename in registered:continue
            try:
                actual,tails=transport.trace_file(filename);unregistered.append(dict(path=str(filename.relative_to(ROOT)),sha256=sha(filename),bytes=filename.stat().st_size,
                    status='UNKNOWN_UNREGISTERED_LOCAL_PREFIX',actual_trace_events=len(actual),unparseable_trace_tails=tails))
                for row in actual:
                    if row['event']=='entered':raw_started[row['kind']]+=1
                    elif row['event']=='completed':raw_completed[row['kind']]+=1
            except BaseException as exc:diagnostics.append(dict(stage='unregistered_prefix',error=repr(exc)))
        raw_complete=len(bindings)==2 and not unregistered and all(b['complete_raw_evidence_gate']for b in bindings.values())
        registry_complete=len(processes)==counts['source_process_started_events']==2 and all(row['reaped']for row in registry)
        expected_raw=Counter({'mesh_load':1})
        for audit in audits.values():expected_raw.update(audit['started'])
        counts_complete=raw_started==raw_completed==expected_raw and len(audits)==6
        if record['status']==PASS and not(raw_complete and registry_complete and counts_complete):record['status']='STOP_LOCAL_RAW_REGISTRY_OR_BODY_COUNTS_UNQUALIFIED'
        after={}
        for name in spec['bound_files_sha256']:
            try:after[name]=sha(name)
            except BaseException as exc:after[name]=None;diagnostics.append(dict(stage='after_bound_hash',path=name,error=repr(exc)))
        record['bound_files_after_sha256']=after
        if after!=spec['bound_files_sha256']:record['status']='STOP_BOUND_ASSET_CHANGED'
        try:
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
            require(record['protocol_after_sha256']==record['protocol_sha256']and record['claim_after_sha256']==record.get('claim_sha256'),'LOCAL_RECIPE_CHANGED')
            previous,_,_=prior();record['prior_execution_after_sha256']=previous;require(previous==spec['prior_execution_sha256'],'PRIOR_EXECUTION_SET_CHANGED_DURING_L12')
        except BaseException as exc:record['status']='STOP_RECIPE_OR_PRIOR_CHANGED';diagnostics.append(dict(stage='after_recipe',error=repr(exc)))
        done=[f['dispatch_index']for f in spec['fixed_schedule']if(f['mode'],f['edge_index'],f['local_call'])in responses]
        unknown=[f for f in spec['fixed_schedule']if f['dispatch_index']not in done]
        record.update(counts=dict(counts),completed_dispatch_ids=done,UNKNOWN_uncompleted_fixtures=unknown,source_process_registry=registry,source_process_registry_complete_gate=registry_complete,
            source_raw_trace_bindings=bindings,complete_source_raw_evidence_gate=raw_complete,full_run_raw_body_count_gate=counts_complete,
            actual_raw_trace_started=dict(raw_started),actual_raw_trace_completed=dict(raw_completed),unregistered_runtime_raw_prefixes=unregistered,
            completed_SVC_constructor_dispatches=sum(s.construction is not None for s in sessions.values()),CBi_constructor_dispatches=0,direct_CBi_rng_member_initializations_structural=0,
            source_body_plain_true_started_completed='UNOBSERVED_NO_PLAIN_BODY_TRACE',diagnostics=diagnostics,ended_at_utc=builder.utc())
        if folder.is_dir():
            try:durable_new(folder/'unknown_tail.json',dict(status='UNKNOWN_NOT_COMPLETED_NO_PREFIX_PASS',fixtures=unknown))
            except BaseException as exc:diagnostics.append(dict(stage='save_unknown',error=repr(exc)))
        if events is not None:events.flush();events.close()
        used_cpu=transport.own_reaped_cpu()-cpu_start;live_cpu=transport.direct_live_cpu(processes)
        record.update(wall_s=time.monotonic()-begun,cpu_s=used_cpu+live_cpu,final_self_and_reaped_children_cpu_s=used_cpu,final_unreaped_registered_live_cpu_s=live_cpu)
        if record['wall_s']>=min(30.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(60.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_LOCAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():durable_new(folder/'execution.json',record)
    print(json.dumps(dict(status=record['status'],completed_local=len(responses),wall_s=record.get('wall_s'),cpu_s=record.get('cpu_s'),new_independent_physical_queries=0)))
    if error is not None:raise error
    require(record['status']==PASS,'L12_FINAL_STATUS_NOT_PASS')

def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_L12_DRAFT_VALIDATED_ZERO_QUERY_ZERO_COMPILE');return
    execute(spec,protocol)
if __name__=='__main__':main()
