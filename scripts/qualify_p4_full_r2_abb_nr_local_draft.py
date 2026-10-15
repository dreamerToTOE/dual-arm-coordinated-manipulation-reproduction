#!/usr/bin/env python3
"""Fixed ABB NR GD/SVC/RBS local qualification DRAFT; no planner entry.

Describe/validate are saved-only. Execution needs root-reviewed committed
protocol, successful separate engineering build, and a fresh one-shot claim.
Uses the existing RunBudget/Evidence process API and physical collision API.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import struct
import subprocess
import sys
import time

import build_p4_full_r2_abb_nr_interface_draft as builder
from build_p4_full_r2_abb_rrt_pcs_e2e import sha,load,utc,new_json,cpu

ROOT=Path(__file__).resolve().parents[1]
RUN='20261015_R2_ABB_NR_LOCAL01'
CLAIM='P4_R2_ABB_NR_LOCAL_20TOP_60W_120CPU_20261015'
PRE='reports/P4_FULL_R2_ABB_NR_LOCAL_INTERFACE_PRE_DRAFT_20261015.md'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
SOURCE_RESULT='results/p4_full/20261015_R2_ABB_RRT_PCS_E2E01/runtime/result.json'
SOURCE_EXECUTION='results/p4_full/20261015_R2_ABB_RRT_PCS_E2E01/execution.json'
Q1_EXECUTION='results/p4_full/20261015_R2_NR_ABB_Q1_01/execution.json'
Q1_POST='reports/P4_FULL_R2_NR_ABB_Q1_INDEPENDENT_SAVED_POST_REVIEW_20261015.json'
PCS_PATH_EXECUTION='results/p4_full/20261015_R2_ABB_RRT_PATH01/execution.json'
ENDPOINTS=[f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/{env}_{i}.json'
    for env in ('II','III') for i in (0,1)]
THREADS={k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
    'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),PRE,*builder.OWN,
    'scripts/qualify_p4_full_r2_vi_rss_reconstructed.py','scripts/qualify_p4_full_r2_abb_pcs.py',
    'scripts/recover_p4_full_r2_endpoints.py','baselines/p4_full/geometry_consistent/collision_adapter.py',
    'baselines/p4_full/geometry_consistent/physical_nr.py','baselines/p4_full/abb_independent_oracle.py',
    'baselines/p4_full/analyze_comau_native_qualification.py','baselines/p4_full/geometry_consistent/rss_geometry.py']
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,'strict_leaf_full12_L2_rad':.05,
    'original_source_RBS_max_depth':150,'source_PQP_tolerance_mm':8.,'fixed_active_or_branch_gate':False}

def require(value,reason):
    if not value:raise RuntimeError(reason)
def path(name):
    p=Path(name);return p if p.is_absolute() else ROOT/p
def bind(files,name,wanted=None):
    got=sha(path(name));require(wanted is None or got==wanted,'BOUND_HASH '+str(name));files[str(name)]=got
    return load(path(name)) if str(name).endswith('.json') else None
def q12(q):
    require(isinstance(q,list) and len(q)==12 and all(type(v)in(int,float) and math.isfinite(v) for v in q),'FINITE_Q12')
    return q
def key(env,q):return env.encode()+struct.pack('>12d',*q12(q))
def distance(a,b):return math.sqrt(math.fsum((x-y)**2 for x,y in zip(q12(a),q12(b))))

def fixed_cases(files):
    inventory=bind(files,builder.FIXTURE);endpoints=[]
    for name,wanted in inventory['source_files_sha256'].items():bind(files,name,wanted)
    for name in ENDPOINTS:
        p=bind(files,name);require(p['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED' and
            p['source_policy_collision_qualified']is True,'A01_QUALIFIED_ENDPOINT_REQUIRED')
        env=p['environment'];index=Path(name).stem.split('_')[-1]
        endpoints.append({'environment':env,'request':{'id':env+'_'+index,'op':'project_q12',
            'q12':q12(p['selected_q_rad'])},'source':name})
    execution=bind(files,SOURCE_EXECUTION);source=bind(files,SOURCE_RESULT,execution['result_sha256'])
    protocol=bind(files,execution['protocol'],execution['protocol_sha256']);bind(files,execution['claim'],execution['claim_sha256'])
    require(execution['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT' and execution['returncode']==0 and
        type(execution['solve_dispatched'])is int and execution['solve_dispatched']==1 and
        source['exact']is True and source['approximate']is False and source['solve_calls']==1,
        'SAVED_ORIGINAL_EXACT_SINGLE_SOLVE_REQUIRED')
    require(protocol['frozen']is True and all(protocol['reviews'].values()),'SAVED_SOURCE_FROZEN')
    path_execution=bind(files,PCS_PATH_EXECUTION)
    require(path_execution['status']=='PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH','SAVED_PCS_PATH_AUDIT_REQUIRED')
    for name,wanted in path_execution['bound_files_sha256'].items():bind(files,name,wanted)
    ms=source['milestones_q12'];require(len(ms)==4,'EXACT_SAVED_FOUR_MILESTONES_REQUIRED')
    edges=[]
    for index,(a,b) in enumerate(zip(ms,ms[1:])):
        edges.append({'edge_index':index,'environment':'II','qa12':q12(a),'qb12':q12(b),
            'source':SOURCE_RESULT,'source_milestone_indices':[index,index+1],
            'original_full12_distance_rad':distance(a,b)})
    require(inventory['milestones_q12']==ms and
        [{k:c[k]for k in('id','environment','op','q12')}for c in inventory['project_cases']]==
        [{**c['request'],'environment':c['environment']}for c in endpoints] and
        [(c['edge_index'],c['environment'],c['qa12'],c['qb12'])for c in inventory['edge_cases']]==
        [(c['edge_index'],c['environment'],c['qa12'],c['qb12'])for c in edges],
        'INVENTORY_EXACT_ALL4_ENDPOINT_ALL3_EDGE_PROVENANCE')
    return {'endpoint_projects':endpoints,'edges':edges,'milestones_q12':ms,
        'selection':'All4 A01 endpoints plus all3 consecutive edges of the first saved original PCS path; no new seed/edge/fixture.'}

def build_assets(files):
    manifest=builder.BUILD/'manifest.json';execution=ROOT/'results/p4_full'/builder.RUN/'execution.json'
    if not manifest.is_file() or not execution.is_file():return {'ready':False,'binary':str(builder.BINARY),
        'binary_sha256':'MUST_BUILD_BEFORE_FREEZE','manifest':str(manifest),'manifest_sha256':'MUST_BUILD_BEFORE_FREEZE'}
    m=bind(files,str(manifest));e=bind(files,str(execution.relative_to(ROOT)))
    require(m['status']==e['status']=='BUILT_NOT_QUERIED' and m['exit_code']==0,'SUCCESSFUL_UNQUERIED_INTERFACE_BUILD_REQUIRED')
    require(e['manifest_sha256']==files[str(manifest)] and e['source_commit']==m['source_commit'],'INTERFACE_BUILD_EXECUTION_LINK')
    require(m['binary']==e['binary']==str(builder.BINARY),'INTERFACE_BINARY_PATH')
    bind(files,str(builder.BINARY),m['binary_sha256']);require(e['binary_sha256']==m['binary_sha256'],'INTERFACE_BINARY_CHAIN')
    for field in ('own_source_sha256','template_assets_sha256'):
        for name,wanted in m[field].items():bind(files,name,wanted)
    require(m['template_assets_after_sha256']==m['template_assets_sha256'],'INTERFACE_TEMPLATE_BEFORE_AFTER')
    recipe=bind(files,m['protocol'],m['protocol_sha256']);claim=bind(files,m['claim'],m['claim_sha256'])
    require(recipe['frozen']is True and all(recipe['reviews'].values()) and
        claim['source_commit']==m['source_commit'],'INTERFACE_FROZEN_BUILD_CLAIM')
    for field in ('compiled_source_sha256','mesh_sha256'):
        for name,wanted in m[field].items():bind(files,str(builder.STAGE/name),wanted)
    for change in m['changes']:
        if 'preserved_original'in change:bind(files,str(builder.STAGE/change['preserved_original']),change['preserved_original_sha256'])
    return {'ready':True,'binary':str(builder.BINARY),'binary_sha256':m['binary_sha256'],
        'manifest':str(manifest),'manifest_sha256':files[str(manifest)],'source_commit':m['source_commit'],
        'mesh_sources':{str(builder.STAGE/name):wanted for name,wanted in m['mesh_sha256'].items()},
        'engineering_execution':str(execution.relative_to(ROOT))}

def draft():
    files={};fixed=fixed_cases(files);q1=bind(files,Q1_EXECUTION);review=bind(files,Q1_POST)
    require(q1['status']=='PASS_FIXED64_NUMERICAL_TRANSFER' and review['status']=='PASS_INDEPENDENT_SAVED_POST_REVIEW'
        and review['checks_total']==review['checks_passed'],'Q1_NUMERICAL_TRANSFER_AND_INDEPENDENT_POST')
    for name,wanted in q1['bound_files_sha256'].items():bind(files,name,wanted)
    bind(files,q1['protocol'],q1['protocol_sha256']);bind(files,q1['claim'],q1['claim_sha256'])
    for name in sorted(set(OWN)):bind(files,name)
    assets=build_assets(files);manifest=bind(files,COLLISION)
    entries=[e for e in manifest['entries'] if e['model']=='abb']
    require(sorted(e['variant']for e in entries)==['aligned','native'],'V3_ABB_NATIVE_ALIGNED_REQUIRED')
    for entry in entries:
        require(entry['exit_code']==0,'COLLISION_BUILD_REQUIRED');bind(files,entry['binary'],entry['binary_sha256'])
        for name,wanted in entry['source_files_sha256'].items():bind(files,str(Path(entry['source_root'])/name),wanted)
        for name,wanted in entry['mesh_sha256'].items():bind(files,str(Path(entry['cwd'])/'simulator'/name),wanted)
    schedule=[]
    for env,mode in [('II','trace'),('II','plain'),('III','trace'),('III','plain')]:
        requests=[c['request'] for c in fixed['endpoint_projects'] if c['environment']==env]
        if env=='II':
            for edge in fixed['edges']:
                for op in ('rbs','reconstruct'):
                    requests.append({'id':f'II_edge_{edge["edge_index"]}_{op}','op':op,
                        'qa12':edge['qa12'],'qb12':edge['qb12']})
        schedule.append({'environment':env,'mode':mode,'requests':requests})
    require(sum(len(s['requests'])for s in schedule)==20,'FIXED20_TOP_LEVEL_REQUIRED')
    prior=sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json')if p.parent.name!=RUN)
    rows=[]
    for p in prior:
        r=bind(files,str(p.relative_to(ROOT)));require(all(type(r[k])in(int,float) and math.isfinite(r[k]) and r[k]>=0
            for k in ('wall_s','cpu_s')),'VALID_PRIOR_OWN_COST');rows.append(r)
    return {'schema':'P4_R2_ABB_NR_FIXED_LOCAL_DRAFT_V1','frozen':False,
        'reviews':{'root_runner_review_passed':False,'independent_math_seam_review_passed':False,
            'Q1_POST_and_prior_ledger_confirmed':False},'run_id':RUN,'claim_id':CLAIM,
        'classification':'RECONSTRUCTED_ENDPOINTS / PHYSICAL_FULL_NR_CPP / ORIGINAL_NR_SVC_RBS_CONTROL_FLOW',
        'build':assets,'fixed_inputs':fixed,'schedule':schedule,'bound_files_sha256':files,
        'collision_manifest':COLLISION,'gates':GATES,'thread_environment':THREADS,
        'budget':{'wall_s':60.,'cpu_s':120.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'previous_r2_wall_s':math.fsum(r['wall_s']for r in rows),'previous_r2_cpu_s':math.fsum(r['cpu_s']for r in rows),
        'prior_executions':[str(p.relative_to(ROOT))for p in prior],
        'max_top_level_requests':20,'recursive_GD_calls':'Actual trace entered/completed; plain UNOBSERVED; no inferred cap-use.',
        'observational_caps_per_trace_request':{'nr_gd':1024,'nr_project':1,'nr_valid_midpoint':1024,
            'nr_rbs':2049,'nr_reconstruct':2049,'collision':1024,'pqp':131072},
        'observation_cap_policy':'Trace caps stop runtime UNKNOWN, never algorithm false; plain internals unobserved and external budget only. No retry after cap.',
        'node_policy':'All finite GD candidates math; every accepted GD, top project candidate, and every original path vertex aligned collision. Exact environment+packed-binary64 dedup, all refs preserved.',
        'rejection_policy':'Normal source false retained. PARTIAL if any fixed edge rejects. Next environmentII planner gate requires its two fixed endpoint project true+qualified, >=1 real nontrivial successful full source path, soundness, and no RBStrue/reconstructfalse. EnvironmentIII normal endpoint rejection does not veto qualifiedII.',
        'tail_policy':'Full node queue frozen before qualification. Wall/CPU stops preserve prefix and every unchecked node; no successful truncated path.',
        'zero_calls':{'solve':0,'RNG':0,'IK':0,'VI_constructions':0,'formal_table_I':0},
        'no_retry_reset_or_resume':True,'scope':'Finite local NR source policy only; not native KDL/global planning/performance/CCD/full physical geometry.'}

def validate(spec,protocol,execute=False):
    expected=draft();require(set(spec)==set(expected),'EXACT_PROTOCOL_FIELDS')
    require(all(spec[k]==v for k,v in expected.items() if k not in('frozen','reviews')),'EXACT_CURRENT_RECIPE')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews']) and
        all(type(v)is bool for v in spec['reviews'].values()),'EXACT_REVIEW_FIELDS')
    if not execute:return None
    require(spec['frozen'] and all(spec['reviews'].values()) and spec['build']['ready'],'BUILD_REVIEW_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in sorted(set(OWN+[str(protocol.relative_to(ROOT))])):
        require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),'UNCOMMITTED_ASSET '+name)
    return commit

def node_worker(protocol):
    """Thin persistent adapter of the existing PCS math/collision worker API."""
    spec=load(protocol);claim=load(ROOT/'results/p4_full'/(CLAIM+'.claim.json'));request=json.loads(sys.stdin.read())
    require(spec['frozen']is True and claim['parent_pid']==os.getppid() and claim['protocol_sha256']==sha(protocol),
        'LIVE_ONE_SHOT_PARENT_REQUIRED')
    folder=ROOT/'results/p4_full'/RUN;queue_path=folder/'node_queue.json'
    require(request['node_queue_sha256']==sha(queue_path),'FROZEN_FULL_NODE_QUEUE_HASH')
    queue=load(queue_path);new_json(folder/'node_worker_started.json',{'parent_pid':os.getppid(),
        'pid':os.getpid(),'node_queue_sha256':sha(queue_path),'protocol_sha256':sha(protocol),'started_at_utc':utc()})
    for name in sorted(set(OWN)):
        require(sha(path(name))==spec['bound_files_sha256'][name],'NODE_WORKER_SOURCE_CHANGED '+name)
    os.environ.update(THREADS);sys.path.insert(0,str(ROOT))
    import recover_p4_full_r2_endpoints as oracle
    from baselines.p4_full.geometry_consistent import physical_nr,collision_adapter as adapter
    counts=Counter();current=None;original=physical_nr.arm_fk_jac
    def event(kind,**values):print('P4_NR_NODE_EVENT '+json.dumps({'event':kind,'at_utc':utc(),**values},allow_nan=False),file=sys.stderr,flush=True)
    def counted(q,env,arm):
        counts['adapter_arm_FK_J_started']+=1;event('adapter_arm_FK_J_started',node_id=current['node_id'],environment=env,arm=arm)
        value=original(q,env,arm);counts['adapter_arm_FK_J_completed']+=1
        event('adapter_arm_FK_J_completed',node_id=current['node_id'],environment=env,arm=arm);return value
    physical_nr.arm_fk_jac=counted
    try:
        for source in queue:
            current={**source,'poses':[],'stage':'STARTED'};env=source['environment'];q=source['q12']
            for arm in (1,2):
                counts['math_arm_FK_started']+=1;event('math_arm_FK_started',node_id=source['node_id'],environment=env,arm=arm)
                pose=oracle.arm_fk(q[6*(arm-1):6*arm],env,arm);current['poses'].append(pose.tolist())
                counts['math_arm_FK_completed']+=1
                new_json(folder/f'node_{source["node_id"]:05d}_arm{arm}.json',current)
                event('math_arm_FK_completed',node_id=source['node_id'],environment=env,arm=arm)
            import numpy as np
            poses=[np.asarray(p)for p in current['poses']]
            residual=oracle.matrix_error(poses[1],poses[0]@oracle.grasps_for(env)[0]@oracle.FLIP)
            limits=oracle.limit_score(q,env);closed=residual['position_max_abs']<=1e-5 and residual['rotation_matrix_max_abs']<=1e-5
            current.update(stage='MATH_COMPLETED',closure=residual,limits=limits,
                math_qualified=bool(closed and limits['legal']))
            new_json(folder/f'node_{source["node_id"]:05d}_math.json',current)
            if source['collision_required']:
                counts['collision_calls_started']+=1;event('collision_started',node_id=source['node_id'])
                collision=adapter.check_collision(env,q,timeout_s=min(10.,max(.001,request['wall_remaining_s']-(time.monotonic()-request['worker_monotonic_start']))),
                    manifest_path=spec['collision_manifest'])
                counts['collision_calls_completed']+=1;current.update(stage='COLLISION_RAW_RETAINED',collision=collision)
                new_json(folder/f'node_{source["node_id"]:05d}_collision_raw.json',collision)
                query_counts={variant:len(row.get('query_codes',[]))for variant,row in collision.get('variants',{}).items()}
                counts['PQP_queries']+=sum(query_counts.values())
                event('collision_completed',node_id=source['node_id'],status=collision.get('status'),
                    variant_query_counts=query_counts,PQP_queries=sum(query_counts.values()))
                require(collision.get('status')=='CHECKED' and collision.get('selected_variant')=='aligned' and
                    type(collision.get('collision'))is bool and collision.get('manifest_sha256')==spec['bound_files_sha256'][COLLISION] and
                    list(collision.get('variants',{}))==['native','aligned'],'COLLISION_RUNTIME_OR_PROVENANCE')
                for variant,row in collision['variants'].items():
                    codes=row.get('query_codes',[])
                    require(codes and all(type(code)is int and code==0 for code in codes),'PQP_QUERY_ERROR '+variant)
                require(collision['variants']['aligned']['pose_consistency']['passed']is True,'ALIGNED_TCP_MISMATCH')
                current['node_qualified']=bool(current['math_qualified'] and not collision['collision'])
            else:current['node_qualified']=None
            current['stage']='COMPLETED';new_json(folder/f'node_{source["node_id"]:05d}.json',current)
            print('P4_NR_NODE_RESPONSE '+json.dumps({'node_id':source['node_id'],'result':current,
                'observed_counts':dict(counts)},allow_nan=False),flush=True);current=None
    except BaseException as exc:
        if current is not None:new_json(folder/'node_worker_stopped_partial.json',current)
        event('stopped',reason=repr(exc),current=current,observed_counts=dict(counts));raise
    finally:
        physical_nr.arm_fk_jac=original;sessions=list(adapter._sessions.values());adapter.close_sessions()
        for session in sessions:
            if session.proc.poll()is None:session.proc.kill();session.proc.wait()

def parse_source_stdout(raw,expected,env,mode):
    responses=[json.loads(line.split(' ',1)[1])for line in raw.splitlines()if line.startswith('P4_NR_RESPONSE ')]
    require(len(responses)==len(expected),'COMPLETE_BATCH_RESPONSES_REQUIRED')
    for request,response in zip(expected,responses):
        require(response.get('schema')=='P4_ABB_NR_THIN_V1' and response.get('request')==request and
            response.get('id')==request['id'] and response.get('op')==request['op'] and
            response.get('environment')==env and response.get('mode')==mode and
            response.get('status')=='SOURCE_CALL_COMPLETED' and type(response.get('returned'))is bool and
            response.get('observer_errors')==[] and response.get('solve_calls')==0 and response.get('rng_calls')==0,
            'SOURCE_RESPONSE_CONTRACT')
    return responses

def trace_check(stderr,responses):
    events=[json.loads(line.split(' ',1)[1])for line in Path(stderr).read_text().splitlines()if line.startswith('P4_PCS_TRACE ')]
    cursor=0;by_request=[]
    for response in responses:
        starts={};ends={};counts=Counter();subset=[]
        # p4pcs::reset resets IDs per top-level request; first enter has id1.
        while cursor<len(events):
            row=events[cursor]
            if subset and row['event']=='entered' and row['id']==1:break
            subset.append(row);cursor+=1
        for row in subset:
            if row['event']=='entered':
                require(row['id']not in starts,'TRACE_DUPLICATE_ENTER');starts[row['id']]=row;counts[row['kind']]+=1
            elif row['event']=='completed':
                require(row['id']not in ends and row['id']in starts and starts[row['id']]['kind']==row['kind'],'TRACE_UNMATCHED_LEAVE')
                ends[row['id']]=row
                if row['kind']=='pqp':require(row['result']['code']==0,'SOURCE_PQP_ERROR')
        require(set(starts)==set(ends) and dict(counts)==response['observed_counts'],'TRACE_ENTER_COMPLETED_COUNT_MISMATCH')
        gd=[row['result']for row in subset if row['event']=='completed' and row['kind']=='nr_gd']
        require(gd==response['gd_completed_candidates'],'TRACE_GD_CANDIDATES_MISMATCH')
        for row in subset:
            if row['event']=='completed' and row['kind']=='nr_gd':
                require(starts[row['id']]['args']['input_q12']==row['result']['input_q12'],'GD_TRACE_INPUT_MUTATION')
        by_request.append({'events':subset,'observed_counts':dict(counts)})
    require(cursor==len(events),'UNMATCHED_TRACE_EVENTS');return by_request

def queue_nodes(pairs):
    queue=[];lookup={}
    def add(env,q,ref,collision):
        k=key(env,q)
        if k not in lookup:lookup[k]=len(queue);queue.append({'node_id':len(queue),'environment':env,
            'q12':q,'refs':[],'collision_required':False})
        node=queue[lookup[k]];node['refs'].append(ref);node['collision_required']|=collision;return node['node_id']
    for pair in pairs:
        response=pair['trace'];env=pair['environment'];request=pair['request'];node_refs=[]
        for index,gd in enumerate(response['gd_completed_candidates']):
            require(type(gd['returned'])is bool and (gd['returned']==(gd['status']=='CONVERGED')),'GD_STATUS_RETURN_SEMANTICS')
            if gd['candidate_q12']is not None:
                node_refs.append({'kind':'gd','candidate_index':index,'returned':gd['returned'],
                    'node_id':add(env,gd['candidate_q12'],{'case_id':request['id'],'kind':'gd',
                        'candidate_index':index,'returned':gd['returned']},gd['returned'])})
            else:require(not gd['returned'],'NONFINITE_ACCEPTED_GD')
        if request['op']=='project_q12':
            node_refs.append({'kind':'top_project','node_id':add(env,response['q12'],
                {'case_id':request['id'],'kind':'top_project','returned':response['returned']},True)})
        else:
            for label in ('qa12','qb12'):
                node_refs.append({'kind':label,'node_id':add(env,request[label],{'case_id':request['id'],'kind':label},True)})
            if request['op']=='reconstruct':
                for index,q in enumerate(response['path_q12']):
                    node_refs.append({'kind':'path','path_index':index,'node_id':add(env,q,
                        {'case_id':request['id'],'kind':'path','path_index':index,'returned':response['returned']},True)})
        pair['node_refs']=node_refs
    return queue

def logical(response):
    fields=['schema','environment','request','id','op','status','returned','q12','path_q12','solve_calls','rng_calls']
    out={k:response[k]for k in fields if k in response}
    out['request']=dict(out['request'])
    for name in ('q12','qa12','qb12'):
        if name in out['request']:out['request'][name]=struct.pack('>12d',*q12(out['request'][name])).hex()
    if 'q12'in out:out['q12']=struct.pack('>12d',*q12(out['q12'])).hex()
    if 'path_q12'in out:out['path_q12']=[struct.pack('>12d',*q12(q)).hex()for q in out['path_q12']]
    out['source_log_counters']={k:v for k,v in response['source_log_counters'].items()if 'time'not in k}
    return out

def evaluate(pairs,nodes,spec):
    outcomes=[];by_id={p['request']['id']:p for p in pairs};sound=True
    for pair in pairs:
        response=pair['trace'];refs=pair['node_refs'];rbsop=pair['request']['op']
        accepted_gd=[r for r in refs if r['kind']=='gd' and r['returned']]
        gd_math_sound=all(nodes[r['node_id']]['math_qualified']for r in accepted_gd)
        if not gd_math_sound:sound=False
        if rbsop=='project_q12':
            output=nodes[next(r['node_id']for r in refs if r['kind']=='top_project')]
            passed=not response['returned'] or output['node_qualified']is True
        else:
            accepted=[r for r in refs if r['kind']in('qa12','qb12','path') or r['kind']=='gd' and r['returned']]
            passed=not response['returned'] or all(nodes[r['node_id']]['node_qualified']is True for r in accepted)
            if rbsop=='reconstruct' and response['returned']:
                qs=response['path_q12'];request=pair['request']
                endpoints=(len(qs)>=2 and key(pair['environment'],qs[0])==key(pair['environment'],request['qa12']) and
                    key(pair['environment'],qs[-1])==key(pair['environment'],request['qb12']))
                leaves=[distance(a,b)for a,b in zip(qs,qs[1:])]
                passed=passed and endpoints and all(d<.05 for d in leaves)
                pair.update(path_endpoint_exact=endpoints,all_leaf_distances_rad=leaves,
                    all_source_path_nodes_qualified=all(nodes[r['node_id']]['node_qualified']is True for r in refs if r['kind']=='path'))
        pair.update(gd_accepted_math_sound=gd_math_sound,returned_sound=bool(passed));sound&=passed
    for edge in spec['fixed_inputs']['edges']:
        index=edge['edge_index'];rbs=by_id[f'II_edge_{index}_rbs'];recon=by_id[f'II_edge_{index}_reconstruct']
        nontrivial=edge['original_full12_distance_rad']>=.05 and bool(rbs['trace']['gd_completed_candidates']) and bool(recon['trace']['gd_completed_candidates'])
        successful=bool(rbs['trace']['returned'] and recon['trace']['returned'] and nontrivial and
            rbs['returned_sound'] and recon['returned_sound'] and rbs['gd_accepted_math_sound'] and recon['gd_accepted_math_sound'])
        outcomes.append({'edge_index':index,'source_rbs_returned':rbs['trace']['returned'],
            'source_reconstruct_returned':recon['trace']['returned'],'nontrivial_real_recursion':nontrivial,
            'qualified_nontrivial_RBS_and_full_original_path':successful,
            'status':'PASS_NONTRIVIAL_ORIGINAL_NR_EDGE' if successful else 'REJECT_OR_PARTIAL',
            'full12_endpoint_distance_rad':edge['original_full12_distance_rad']})
        if rbs['trace']['returned'] and not recon['trace']['returned']:
            # Retain distinct original returns, but do not open planner gate.
            outcomes[-1]['rbs_true_reconstruct_false']=True
    return outcomes,bool(sound)

def execute(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN;claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists() and not claim.exists(),'EXISTING_CLAIM_OR_OUTPUT_NO_RETRY')
    started=time.monotonic();cpu_start=cpu();budget=evidence=None;error=None;diagnostics=[];pairs=[];queue=[];outcomes=[];counts=Counter()
    record={'schema':'P4_R2_ABB_NR_FIXED_LOCAL_EXECUTION_V1','run_id':RUN,'source_commit':commit,
        'protocol':str(protocol.relative_to(ROOT)),'protocol_sha256':sha(protocol),'claim':str(claim.relative_to(ROOT)),
        'classification':spec['classification'],'bound_files_sha256':spec['bound_files_sha256'],
        'prior_executions':spec['prior_executions'],'previous_r2_wall_s':spec['previous_r2_wall_s'],
        'previous_r2_cpu_s':spec['previous_r2_cpu_s'],'budget':spec['budget'],'status':'STOP_SETUP_PREFIX_RETAINED',
        'zero_calls':spec['zero_calls'],'started_at_utc':utc(),'plain_internal_GD_FK_PQP':'UNOBSERVED'}
    try:
        folder.mkdir();new_json(claim,{'schema':'P4_R2_ABB_NR_FIXED_LOCAL_CLAIM_V1','claim_id':CLAIM,
            'parent_pid':os.getpid(),'source_commit':commit,'protocol_sha256':record['protocol_sha256'],
            'budget':spec['budget'],'created_at_utc':utc(),'no_retry_reset_or_resume':True})
        record['claim_sha256']=sha(claim);new_json(folder/'setup_started.json',record)
        os.environ.update(THREADS);sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
        import qualify_p4_full_r2_vi_rss_reconstructed as common
        budget=common.RunBudget(spec,spec['previous_r2_wall_s'],spec['previous_r2_cpu_s'])
        budget.started=started;budget.cpu_start=cpu_start
        signal.setitimer(signal.ITIMER_REAL,max(.000001,budget.wall_cap-(time.monotonic()-started)))
        class LiveEvidence(common.Evidence):
            """Same saved-prefix process API, with the prior Q1 live-group CPU guard.

            This thin adaptation is needed because the common API only sees
            reaped child CPU; persistent NR/PQP workers must also count live CPU.
            """
            def process(self,command,input_text,label,environment=None):
                self.budget.remaining();self.process_number+=1;stem=f'{self.process_number:05d}_{label}'
                inp,stdout,stderr=[self.folder/(stem+s)for s in('.input.txt','.stdout.txt','.stderr.txt')]
                with inp.open('x')as stream:stream.write(input_text)
                begun=time.monotonic();proc=None
                self.event('process_started',label=label,command=command,input=str(inp.relative_to(ROOT)))
                try:
                    with inp.open()as fin,stdout.open('x')as fout,stderr.open('x')as ferr:
                        proc=subprocess.Popen(command,stdin=fin,stdout=fout,stderr=ferr,cwd=ROOT,
                            start_new_session=True,env={**os.environ,**(environment or {})})
                        while proc.poll()is None:
                            self.budget.remaining()
                            require(self.budget.cpu()-self.budget.cpu_start+builder.live_group_cpu(proc.pid)<self.budget.cpu_cap,
                                'PARENT_PLUS_LIVE_PROCESS_GROUP_CPU_CAP')
                            try:proc.wait(timeout=.02)
                            except subprocess.TimeoutExpired:pass
                except BaseException:
                    if proc is not None and proc.poll()is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                    self.event('process_interrupted',label=label,wall_s=time.monotonic()-begun);raise
                self.event('process_finished',label=label,exit_code=proc.returncode,wall_s=time.monotonic()-begun,
                    stdout_sha256=sha(stdout),stderr_sha256=sha(stderr))
                self.budget.remaining();require(proc.returncode==0,'PROCESS_FAILED '+label+' '+str(proc.returncode))
                return stdout.read_text()
        evidence=LiveEvidence(folder,budget);responses={};traces={}
        for batch_index,batch in enumerate(spec['schedule']):
            budget.remaining();env=batch['environment'];mode=batch['mode'];runtime=folder/f'runtime_{env}_{mode}'
            runtime.mkdir();(runtime/'simulator').mkdir()
            for source,wanted in spec['build']['mesh_sources'].items():
                require(sha(source)==wanted,'BOUND_MESH_CHANGED');shutil.copy2(source,runtime/'simulator'/Path(source).name)
            label=f'source_{batch_index:02d}_{env}_{mode}';process_number=evidence.process_number+1
            counts['top_requests_submitted_to_batch']+=len(batch['requests'])
            evidence.event('source_batch_started',batch_index=batch_index,environment=env,mode=mode,requests=batch['requests'])
            raw=evidence.process([spec['build']['binary'],env,mode,str(runtime)],
                ''.join(json.dumps(r,allow_nan=False)+'\n'for r in batch['requests']),label)
            answers=parse_source_stdout(raw,batch['requests'],env,mode);counts['top_responses_completed']+=len(answers)
            for answer in answers:
                new_json(folder/f'source_{env}_{mode}_{answer["id"]}.json',answer)
                responses[(env,mode,answer['id'])]=answer
            if mode=='trace':
                observations=trace_check(folder/f'{process_number:05d}_{label}.stderr.txt',answers)
                for answer,observed in zip(answers,observations):
                    traces[(env,answer['id'])]=observed;counts.update({'trace_'+k+'_completed':v for k,v in observed['observed_counts'].items()})
            else:
                require(all(a['observed_counts']=={} and a['gd_completed_candidates']==[]for a in answers),'PLAIN_COUNTS_OR_TRACE_NOT_EMPTY')
        for batch in [b for b in spec['schedule']if b['mode']=='trace']:
            for request in batch['requests']:
                env=batch['environment'];trace=responses[(env,'trace',request['id'])];plain=responses[(env,'plain',request['id'])]
                require(logical(trace)==logical(plain),'PLAIN_TRACE_LOGICAL_OR_COUNTER_MISMATCH '+request['id'])
                pairs.append({'environment':env,'request':request,'trace':trace,'plain':plain,
                    'plain_trace_logical_equal':True,'trace_observation':traces[(env,request['id'])]})
        require(len(pairs)==10,'ALL10_LOGICAL_PAIRS_REQUIRED');queue=queue_nodes(pairs)
        new_json(folder/'source_pairs.json',pairs);new_json(folder/'node_queue.json',queue)
        record['node_queue_sha256']=sha(folder/'node_queue.json');counts['full_node_queue']=len(queue)
        raw=evidence.process([sys.executable,str(Path(__file__).resolve()),'--node-worker',str(protocol)],
            json.dumps({'node_queue_sha256':record['node_queue_sha256'],'wall_remaining_s':budget.remaining(),
                'worker_monotonic_start':time.monotonic()})+'\n','independent_full_node_queue')
        answers=[json.loads(line.split(' ',1)[1])for line in raw.splitlines()if line.startswith('P4_NR_NODE_RESPONSE ')]
        require([a['node_id']for a in answers]==list(range(len(queue))),'FULL_NODE_QUEUE_RETURN_REQUIRED')
        nodes={a['node_id']:a['result']for a in answers};outcomes,sound=evaluate(pairs,nodes,spec)
        new_json(folder/'qualified_source_pairs.json',pairs);new_json(folder/'local_outcomes.json',outcomes)
        counts['completed_nodes']=len(nodes)
        if answers:counts.update(answers[-1]['observed_counts'])
        positive=sum(o['qualified_nontrivial_RBS_and_full_original_path']for o in outcomes)
        project_pass=all(p['returned_sound'] and p['trace']['returned']for p in pairs if p['request']['op']=='project_q12')
        endpoint_gates={env:all(p['returned_sound'] and p['trace']['returned']for p in pairs
            if p['request']['op']=='project_q12' and p['environment']==env)for env in('II','III')}
        record.update(soundness_passed=sound,qualified_nontrivial_edges=positive,
            endpoint_project_gate_by_environment=endpoint_gates,next_planner_environment='II',
            next_planner_gate_supported=bool(sound and endpoint_gates['II'] and positive>=1 and
                all(not o.get('rbs_true_reconstruct_false',False)for o in outcomes)),
            status='STOP_SOURCE_TRUE_UNSOUND' if not sound else
                'FIXED_LOCAL_ABB_NR_QUALIFIED' if positive==3 and project_pass else 'FIXED_LOCAL_ABB_NR_PARTIAL')
        budget.remaining()
    except BaseException as exc:
        error=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc))
        if evidence is not None:
            try:evidence.event('run_stopped',reason=repr(exc))
            except BaseException as e:diagnostics.append({'stage':'stop_event','error':repr(e)})
    finally:
        if budget is not None:
            try:budget.close()
            except BaseException as exc:diagnostics.append({'stage':'budget_close','error':repr(exc)})
        # Count only saved completed nodes/observed events even on a killed worker.
        completed=[]
        for p in sorted(folder.glob('node_[0-9][0-9][0-9][0-9][0-9].json')):completed.append(load(p)['node_id'])
        # Derive actual observed starts/completions from raw prefix, including a
        # batch or worker killed before Evidence.process could return normally.
        source_raw=[];node_raw=[];worker_events=[];trace_started=Counter();trace_completed=Counter()
        for p in sorted(folder.glob('*.stdout.txt')):
            for line in p.read_text().splitlines():
                try:
                    if line.startswith('P4_NR_RESPONSE '):source_raw.append(json.loads(line.split(' ',1)[1]))
                    if line.startswith('P4_NR_NODE_RESPONSE '):node_raw.append(json.loads(line.split(' ',1)[1]))
                except (ValueError,TypeError)as exc:diagnostics.append({'stage':'raw_stdout_parse '+str(p),'error':repr(exc)})
        for p in sorted(folder.glob('*.stderr.txt')):
            for line in p.read_text().splitlines():
                try:
                    if line.startswith('P4_NR_NODE_EVENT '):worker_events.append(json.loads(line.split(' ',1)[1]))
                    if line.startswith('P4_PCS_TRACE '):
                        e=json.loads(line.split(' ',1)[1])
                        if e['event']=='entered':trace_started[e['kind']]+=1
                        if e['event']=='completed':trace_completed[e['kind']]+=1
                except (ValueError,TypeError)as exc:diagnostics.append({'stage':'raw_stderr_parse '+str(p),'error':repr(exc)})
        for e in worker_events:
            if e['event']in('math_arm_FK_started','math_arm_FK_completed','adapter_arm_FK_J_started',
                'adapter_arm_FK_J_completed','collision_started','collision_completed'):counts['actual_'+e['event']]+=1
            if e['event']=='collision_completed':
                counts['actual_adapter_PQP_queries']+=e['PQP_queries']
                for variant,n in e['variant_query_counts'].items():counts['actual_adapter_'+variant+'_PQP_queries']+=n
        counts['actual_source_responses_retained']=len(source_raw)
        counts['actual_source_calls_completed']=sum(r.get('status')=='SOURCE_CALL_COMPLETED'for r in source_raw)
        counts['actual_node_responses_retained']=len(node_raw)
        for kind,value in trace_started.items():counts['actual_trace_'+kind+'_started']=value
        for kind,value in trace_completed.items():counts['actual_trace_'+kind+'_completed']=value
        if evidence is not None:
            try:new_json(folder/'raw_prefix_inventory.json',{'source_responses':source_raw,'node_responses':node_raw,
                'worker_events':worker_events,'trace_entered_counts':dict(trace_started),
                'trace_completed_counts':dict(trace_completed),'actual_observed_only':True})
            except BaseException as exc:diagnostics.append({'stage':'raw_prefix_inventory','error':repr(exc)})
        after={}
        for name in spec['bound_files_sha256']:
            try:after[name]=sha(path(name))
            except BaseException as exc:after[name]=None;diagnostics.append({'stage':'hash '+name,'error':repr(exc)})
        if after!=spec['bound_files_sha256']:record['status']='STOP_BOUND_ASSET_CHANGED'
        try:
            record.update(protocol_after_sha256=sha(protocol),claim_after_sha256=sha(claim))
            if record['protocol_after_sha256']!=record['protocol_sha256'] or record['claim_after_sha256']!=record.get('claim_sha256'):
                record['status']='STOP_PROTOCOL_OR_CLAIM_CHANGED'
        except BaseException as exc:diagnostics.append({'stage':'protocol_claim_after','error':repr(exc)})
        wall=time.monotonic()-started;used_cpu=cpu()-cpu_start
        if wall>=min(60.,3600.-spec['previous_r2_wall_s'])or used_cpu>=min(120.,7200.-spec['previous_r2_cpu_s']):
            record['status']='STOP_WALL_OR_CPU_BUDGET_PREFIX_RETAINED'
        if diagnostics:record['status']='STOP_EVIDENCE_OR_CLEANUP_ERROR'
        record.update(wall_s=wall,cpu_s=used_cpu,counts=dict(counts),outcomes=outcomes,
            completed_node_ids=completed,uncompleted_node_ids=[n['node_id']for n in queue if n['node_id']not in completed],
            full_node_queue_count=len(queue),full_node_queue_checked=bool(queue)and len(completed)==len(queue),
            bound_files_after_sha256=after,diagnostics=diagnostics,ended_at_utc=utc(),
            completed_source_response_ids=[{'environment':r.get('environment'),'mode':r.get('mode'),
                'id':r.get('id'),'status':r.get('status')}for r in source_raw],
            uncompleted_top_requests=[{'environment':b['environment'],'mode':b['mode'],'request':r}
                for b in spec['schedule']for r in b['requests']if not any(
                    s.get('environment')==b['environment']and s.get('mode')==b['mode']and s.get('id')==r['id']
                    and s.get('status')=='SOURCE_CALL_COMPLETED'for s in source_raw)],
            partial_accounting='Raw process stdout/stderr preserves all completed responses/entered traces on interruption; submitted requests are not claimed started. Plain internals UNOBSERVED.')
        try:folder.mkdir(exist_ok=True);new_json(folder/'execution.json',record)
        finally:
            if evidence is not None:evidence.events.close()
    print(json.dumps({k:record.get(k)for k in('status','qualified_nontrivial_edges','wall_s','cpu_s','counts')}))
    if error:raise error
    require(not record['status'].startswith('STOP_'),record['status'])

def main():
    parser=argparse.ArgumentParser(description=__doc__);g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--validate-draft',type=Path)
    g.add_argument('--protocol',type=Path);g.add_argument('--node-worker',type=Path,help=argparse.SUPPRESS)
    args=parser.parse_args()
    if args.node_worker:node_worker(args.node_worker.resolve());return
    if args.describe_protocol:print(json.dumps(draft(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_DRAFT_VALIDATED_ZERO_SCIENTIFIC_CALLS');return
    execute(spec,protocol)

if __name__=='__main__':main()
