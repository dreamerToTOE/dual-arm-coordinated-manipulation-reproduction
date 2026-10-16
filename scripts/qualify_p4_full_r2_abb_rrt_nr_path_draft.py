#!/usr/bin/env python3
"""Complete saved original RRT_NR path qualification candidate; never plan.

Describe/validate only read saved bytes and arrays. A future execution requires
the actual exact E2E01 result, complete source provenance, reviewed committed
protocol, and a fresh one-shot claim. No NR/IK/projection/RBS/RNG is invoked.
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
import struct
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_p4_full_r2_abb_rrt_nr_e2e_draft as builder
import qualify_p4_full_r2_abb_nr_local_draft as local

RUN='20261015_R2_ABB_RRT_NR_PATH01'
CLAIM='P4_R2_ABB_RRT_NR_PATH_120W_240CPU_20261015'
PRE='reports/P4_FULL_R2_ABB_RRT_NR_PATH_PRE_DRAFT_20261015.md'
SOURCE_RUN='20261015_R2_ABB_RRT_NR_E2E01'
SOURCE_FOLDER='results/p4_full/'+SOURCE_RUN
SOURCE_EXECUTION=SOURCE_FOLDER+'/execution.json'
SOURCE_RESULT=SOURCE_FOLDER+'/runtime/result.json'
SOURCE_PROTOCOL='configs/p4_full/r2_abb_rrt_nr_e2e_qualification_v1.json'
SOURCE_CLAIM='results/p4_full/P4_R2_ABB_RRT_NR_E2E_SEED7_30W_60CPU_20261015.claim.json'
SOURCE_LOG=SOURCE_FOLDER+'/runtime/reconstruction_attempts.jsonl'
COLLISION=local.COLLISION
ENDPOINTS=[f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_{i}.json'for i in(0,1)]
THREADS=local.THREADS
MAX_NODES=2048
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
    'strict_leaf_full12_L2_rad':.05,'source_literal_pi_for_mechanical_limits':3.1416,
    'source_PQP_tolerance_mm':8.,'fixed_active_or_branch_gate':False,
    'continuous_collision_certificate':False}
OWN=sorted(set([str(Path(__file__).resolve().relative_to(ROOT)),PRE,
    'scripts/qualify_p4_full_r2_abb_rrt_nr_e2e_draft.py',*local.OWN,*builder.OWN]))
sha,load,utc,new_json,cpu=builder.sha,builder.load,builder.utc,builder.new_json,builder.cpu

def require(ok,reason):
    if not ok:raise ValueError(reason)
def path(value):
    p=Path(value);return p if p.is_absolute()else ROOT/p
def bind(files,name,wanted=None):
    name=str(name);actual=sha(path(name))
    require(wanted is None or actual==wanted,'BOUND_HASH_CHANGED '+name)
    files[name]=actual
    return load(path(name))if name.endswith('.json')else None
def q12(q):
    require(isinstance(q,list)and len(q)==12 and all(type(x)in(int,float)and math.isfinite(x)for x in q),'FINITE_BINARY64_Q12_REQUIRED')
    return q
def qkey(q):return struct.pack('>12d',*q12(q))
def distance(a,b):return math.sqrt(math.fsum((x-y)**2 for x,y in zip(q12(a),q12(b))))
def read_jsonl(name):return[json.loads(s)for s in path(name).read_text().splitlines()if s.strip()]

def source_provenance(files):
    """Validate actual execution -> frozen protocol/claim/build -> full JSONL."""
    e=bind(files,SOURCE_EXECUTION)
    require(e['schema']=='P4_R2_ABB_RRT_NR_E2E_EXECUTION_V1'and e['run_id']==SOURCE_RUN,
        'FIXED_NR_E2E01_EXECUTION_REQUIRED')
    require(e['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT'and e['returncode']==0,
        'EXACT_COMPLETED_SOURCE_EXECUTION_REQUIRED')
    require(path(e['protocol']).resolve()==path(SOURCE_PROTOCOL).resolve(),'FIXED_SOURCE_PROTOCOL_REQUIRED')
    p=bind(files,SOURCE_PROTOCOL,e['protocol_sha256'])
    require(p['schema']=='P4_R2_ABB_RRT_NR_E2E_QUALIFICATION_V1'and p['frozen']is True and
        bool(p['reviews'])and all(v is True for v in p['reviews'].values())and
        p['execution_readiness']=='FROZEN_REVIEWED_READY','SOURCE_NOT_REVIEWED_FROZEN')
    require(e['protocol_after_sha256']==e['protocol_sha256'],'SOURCE_PROTOCOL_CHANGED_DURING_RUN')
    require(path(e['claim']).resolve()==path(SOURCE_CLAIM).resolve(),'FIXED_SOURCE_CLAIM_REQUIRED')
    c=bind(files,SOURCE_CLAIM,e['claim_sha256'])
    require(c['protocol_sha256']==files[SOURCE_PROTOCOL]and c['source_commit']==e['source_commit']and
        c['no_retry_reset_or_resume']is True and e['claim_after_sha256']==e['claim_sha256'],'SOURCE_CLAIM_LINK')
    require(e['own_source_after_sha256']==e['own_source_sha256']==p['own_source_sha256'],
        'SOURCE_OWN_BYTES_CHANGED')
    for name,wanted in p['own_source_sha256'].items():
        bind(files,name,wanted)
        blob=subprocess.check_output(['git','show',e['source_commit']+':'+name],cwd=ROOT)
        require(hashlib.sha256(blob).hexdigest()==wanted,'SOURCE_COMMIT_BLOB '+name)
    require(path(e['build_manifest']).resolve()==(builder.BUILD/'manifest.json').resolve(),'FIXED_SOURCE_BUILD_REQUIRED')
    m=bind(files,e['build_manifest'],e['build_manifest_sha256'])
    require(m['status']=='BUILT_NOT_QUERIED'and m['exit_code']==0 and
        m['query_calls']==m['solve_calls']==0,'SOURCE_BUILD_NOT_UNQUERIED_SUCCESS')
    require(p['build_assets']['status']=='BUILT_NOT_QUERIED'and
        path(e['binary']).resolve()==builder.BINARY.resolve()==path(p['build_assets']['binary']).resolve(),
        'SOURCE_BINARY_PATH')
    require(e['binary_sha256']==m['binary_sha256']==p['build_assets']['binary_sha256'],'SOURCE_BINARY_HASH_LINK')
    bind(files,e['binary'],e['binary_sha256'])
    require(e['build_assets_before_sha256']==e['build_assets_after_sha256']==p['build_assets']['files'],
        'SOURCE_BUILD_ASSET_BEFORE_AFTER')
    for name,wanted in p['build_assets']['files'].items():bind(files,name,wanted)
    for field,hashfield in[('protocol','protocol_sha256'),('claim','claim_sha256')]:bind(files,m[field],m[hashfield])
    engineering=bind(files,m['engineering_execution'])
    require(engineering['source_commit']==m['source_commit']and engineering['status']=='BUILT_NOT_QUERIED'and
        engineering['manifest_sha256']==files[e['build_manifest']],'SOURCE_ENGINEERING_MANIFEST_LINK')
    for field in('compiled_source_sha256','mesh_sha256'):
        for name,wanted in m[field].items():bind(files,str(builder.STAGE/name),wanted)
    for name,wanted in m['template_assets_sha256'].items():bind(files,name,wanted)
    for change in m['changes']:
        if 'preserved_original'in change:bind(files,str(builder.STAGE/change['preserved_original']),change['preserved_original_sha256'])
    points=[bind(files,name,p['endpoint_sources_sha256'][name])for name in ENDPOINTS]
    require(all(v['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'and v['source_policy_collision_qualified']is True
        for v in points),'ORIGINAL_A01_RECONSTRUCTED_ENDPOINTS_REQUIRED')
    require(e['endpoint_sources_after_sha256']==p['endpoint_sources_sha256'],'SOURCE_A01_CHANGED_DURING_RUN')
    request={'environment':'II','seed':7,'range_rad':2.6,'goal_bias':.05,'solve_seconds':10.,
        'start_q12':points[0]['selected_q_rad'],'goal_q12':points[1]['selected_q_rad'],
        'bounds_low_rad':[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2,
        'bounds_high_rad':[2.88,1.919,1.22,2.79,2.09,3.1416]*2}
    require(p['request']==request==e['driver_request'],'FIXED_SOURCE_REQUEST')
    for field in('start_q12','goal_q12'):
        require(qkey(p['request'][field])==qkey(request[field])==qkey(e['driver_request'][field]),
            'FIXED_SOURCE_REQUEST_BINARY64 '+field)
    require(path(e['result']).resolve()==path(SOURCE_RESULT).resolve(),'FIXED_RESULT_PATH')
    d=bind(files,SOURCE_RESULT,e['result_sha256'])
    require(d['schema']=='P4_ABB_RRT_NR_END_TO_END_DRAFT_V1'and
        d['status']=='SOURCE_SOLVE_RETURNED_PENDING_INDEPENDENT_PATH_AUDIT'and d['request']==request,
        'SOURCE_DRIVER_RESULT_CONTRACT')
    require(all(type(x)is int and x==1 for x in(e['solve_dispatched'],e['solve_calls_from_result'],d['solve_calls'])),
        'SOURCE_EXACTLY_ONE_COMPLETED_SOLVE')
    require(d['exact']is True and d['approximate']is False and d['has_solution']is True,
        'EXACT_NONAPPROXIMATE_SOLUTION_REQUIRED')
    require(d['formal_table_I_calls']==e['formal_table_I_calls']==p['formal_table_I_calls']==0 and
        e['new_VI_candidate_constructions']==p['new_VI_candidate_constructions']==0,'SOURCE_SCOPE_CHANGED')
    for name in('environment','seed','start_q12','goal_q12','range_rad','goal_bias','bounds_low_rad','bounds_high_rad'):
        require(d[name]==request[name],'SOURCE_DRIVER_METADATA '+name)
    for field in('start_q12','goal_q12'):
        require(qkey(d[field])==qkey(d['request'][field])==qkey(request[field]),'SOURCE_DRIVER_ENDPOINT_BINARY64 '+field)
    bind(files,SOURCE_LOG);attempts=read_jsonl(SOURCE_LOG)
    require(attempts==d['reconstruction_attempts']and
        d['reconstruction_calls_completed_observed']==len(attempts)and
        e['observation_prefix']['reconstruction_calls_completed_observed']==len(attempts)and
        e['observation_prefix']['reconstruction_incomplete_tails']==[],
        'FULL_ORIGINAL_STATE_RECONSTRUCTION_JSONL_REQUIRED')
    for raw,copied in zip(attempts,d['reconstruction_attempts']):
        for field in('qa12','qb12'):
            require(qkey(raw[field])==qkey(copied[field]),'JSONL_RESULT_ENDPOINT_BINARY64 '+field)
        require([qkey(q)for q in raw['path_q12']]==[qkey(q)for q in copied['path_q12']],
            'JSONL_RESULT_COMPLETE_CONFS_BINARY64')
    for name,wanted in e['runtime_mesh_sha256'].items():bind(files,name,wanted)
    for name,wanted in e['retained_run_files_sha256'].items():bind(files,name,wanted)
    return d,{'execution':SOURCE_EXECUTION,'protocol':SOURCE_PROTOCOL,'claim':SOURCE_CLAIM,
        'build_manifest':e['build_manifest'],'binary':e['binary'],'result':SOURCE_RESULT,
        'reconstruction_log':SOURCE_LOG,'request':request,'source_commit':e['source_commit']}

def materialize(d):
    """Retain all milestones and all completed paths; never choose a new path."""
    milestones=d['milestones_q12'];attempts=d['reconstruction_attempts'];nodes=[];lookup={};edges=[]
    require(len(milestones)>=2 and qkey(milestones[0])==qkey(d['start_q12'])and
        qkey(milestones[-1])==qkey(d['goal_q12']),'EXACT_BINARY64_START_GOAL_REQUIRED')
    def add(q,ref):
        k=qkey(q)
        if k not in lookup:
            lookup[k]=len(nodes);nodes.append({'node_id':len(nodes),'environment':'II','q12':q,
                'refs':[],'collision_required':True})
        nodes[lookup[k]]['refs'].append(ref);return lookup[k]
    milestone_ids=[add(q,{'kind':'milestone','milestone_index':i})for i,q in enumerate(milestones)]
    for ai,attempt in enumerate(attempts):
        require(attempt['schema']=='P4_ABB_RRT_NR_RECONSTRUCTION_DRAFT_V1'and
            type(attempt['attempt_index'])is int and attempt['attempt_index']==ai and
            attempt['observation']=='ORIGINAL_STATE_LEVEL_CALL_COMPLETED_POST_RETURN'and
            type(attempt['returned'])is bool,'ORIGINAL_STATE_RECONSTRUCTION_CONTRACT')
        for side in('qa12','qb12'):add(attempt[side],{'kind':'attempt_endpoint','attempt_index':ai,'side':side,'returned':attempt['returned']})
        ids=[add(q,{'kind':'original_dense_path','attempt_index':ai,'path_index':i,'returned':attempt['returned']})
            for i,q in enumerate(attempt['path_q12'])]
        leaves=[distance(a,b)for a,b in zip(attempt['path_q12'],attempt['path_q12'][1:])]
        ordered=ai<len(milestones)-1 and qkey(attempt['qa12'])==qkey(milestones[ai])and qkey(attempt['qb12'])==qkey(milestones[ai+1])
        endpoint_exact=(len(ids)>=2 and qkey(attempt['path_q12'][0])==qkey(attempt['qa12'])and
            qkey(attempt['path_q12'][-1])==qkey(attempt['qb12']))
        edges.append({'edge_index':ai,'selected_attempt_index':ai,'source_returned':attempt['returned'],
            'qa12':attempt['qa12'],'qb12':attempt['qb12'],'milestone_edge_order_exact':ordered,
            'dense_first_last_binary64_exact':endpoint_exact,'node_ids':ids,'leaf_distances_rad':leaves,
            'all_original_leaf_distances_strict':all(v<.05 for v in leaves),
            'structural_qualified':bool(attempt['returned']and ordered and endpoint_exact and all(v<.05 for v in leaves))})
    tree=d['planner_data'];vertices=tree['vertices'];links=tree['edges'];graph={}
    require(tree['num_vertices']==len(vertices)and tree['num_edges']==len(links)and
        [v['index']for v in vertices]==list(range(len(vertices))),'COMPLETE_SOURCE_TREE_COUNTS')
    for a,b in links:
        require(type(a)is int and type(b)is int and 0<=a<len(vertices)and 0<=b<len(vertices),'SOURCE_TREE_EDGE_INDEX')
        graph.setdefault(a,set()).add(b)
    possible={v['index']:[v['index']]for v in vertices if qkey(v['q12'])==qkey(milestones[0])and v['start']is True}
    for q in milestones[1:]:
        possible={child:prefix+[child]for parent,prefix in possible.items()for child in sorted(graph.get(parent,()))
            if qkey(vertices[child]['q12'])==qkey(q)}
        require(bool(possible),'MILESTONE_SEQUENCE_NOT_IN_ORIGINAL_DIRECTED_TREE')
    goal_paths=[v for i,v in sorted(possible.items())if vertices[i]['goal']is True]
    require(bool(goal_paths),'MILESTONE_LAST_NOT_TREE_GOAL')
    return {'nodes':nodes,'edges':edges,'milestone_node_ids':milestone_ids,
        'source_milestone_count':len(milestones),'source_attempt_count':len(attempts),
        'source_tree_vertex_path':goal_paths[0],
        'all_edges_structural_qualified':len(attempts)==len(milestones)-1 and all(e['structural_qualified']for e in edges),
        'deduplication':'Environment II plus packed big-endian binary64 full12 including signed zero; preserve all milestone/attempt/path refs.',
        'queue_policy':'All milestones and every original completed Confs including falseprefix retained; no resampling or path selection.'}

def draft():
    files={}
    for name in OWN:bind(files,name)
    ready=path(SOURCE_EXECUTION).is_file()and path(SOURCE_RESULT).is_file()
    source=provenance=queue=None
    if ready:
        source,provenance=source_provenance(files);queue=materialize(source)
    manifest=bind(files,COLLISION);entries=[e for e in manifest['entries']if e['model']=='abb']
    require(sorted(e['variant']for e in entries)==['aligned','native'],'V3_NATIVE_ALIGNED_REQUIRED')
    for e in entries:
        require(e['exit_code']==0,'COLLISION_BUILD_FAILED');bind(files,e['binary'],e['binary_sha256'])
        for name,wanted in e['source_files_sha256'].items():bind(files,str(Path(e['source_root'])/name),wanted)
        for name,wanted in e['mesh_sha256'].items():bind(files,str(Path(e['cwd'])/'simulator'/name),wanted)
    prior=sorted(p for p in(ROOT/'results/p4_full').glob('20261015_R2_*/execution.json')if p.parent.name!=RUN)
    previous=[]
    for name in prior:
        r=bind(files,str(name.relative_to(ROOT)))
        require(all(type(r[k])in(int,float)and math.isfinite(r[k])and r[k]>=0 for k in('wall_s','cpu_s')),'VALID_PRIOR_OWN_COST')
        previous.append(r)
    n=len(queue['nodes'])if ready else None
    return {'schema':'P4_R2_ABB_RRT_NR_PATH_QUALIFICATION_DRAFT_V1','frozen':False,
        'reviews':{'root_source_and_complete_queue_review_passed':False,'independent_runner_review_passed':False,
            'prior_execution_ledger_confirmed':False},'run_id':RUN,'claim_id':CLAIM,
        'source_ready':ready,'execution_readiness':'CANDIDATE_REQUIRES_REVIEW_FREEZE'if ready else 'WAIT_ACTUAL_NR_E2E01_RESULT',
        'classification':'RECONSTRUCTED_A01_ENDPOINTS / Q1_PHYSICAL_FULL_NR_CPP / ORIGINAL_RRT_NR / DISCRETE_SAVED_PATH_ONLY',
        'source_result':SOURCE_RESULT,'source_provenance':provenance,'environment':'II','fixed_queue':queue,
        'collision_manifest':COLLISION,'gates':GATES,'thread_environment':THREADS,
        'budget':{'wall_s':120.,'cpu_s':240.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'previous_r2_wall_s':math.fsum(r['wall_s']for r in previous),'previous_r2_cpu_s':math.fsum(r['cpu_s']for r in previous),
        'prior_executions':[str(p.relative_to(ROOT))for p in prior],'bound_files_sha256':files,
        'max_unique_nodes':MAX_NODES,'full_queue_node_count':n,
        'max_math_arm_FK_J':2*MAX_NODES,'max_collision_calls':MAX_NODES,'max_adapter_arm_FK_J':4*MAX_NODES,
        'zero_calls':{'solve':0,'NR':0,'IK':0,'projection':0,'RBS':0,'RNG':0,'VI_constructions':0,'formal_table_I':0},
        'resource_policy':'Parent hard wall and live aggregate process-group CPU, single serial worker; 2048 cap means UNKNOWN with complete retained tail, never truncate or PASS.',
        'worker_reuse':'Existing qualified local node_worker unchanged; only module RUN/CLAIM/OWN dispatch metadata is bound to this protocol. All queue nodes collision_required=true.',
        'source_path_policy':'Every milestone edge must have exactly its original returnedtrue state-level reconstruction, exact binary64 qa/qb and first/last, full12 leaves strictly<.05. Any source false or absent call blocks science and path PASS.',
        'scope':'All saved original path nodes, exact A01 start-goal and tree sequence, independent closure/original mechanical limits/v3 aligned original discrete collision; native result kept separately. No fixed passive/analytic branch gate for NR.',
        'limits':['No continuous collision, full solid rod surface, or omitted-pair safety certificate.',
            'No original KDL trajectory or paper speed equivalence claim; Q1 physical full-NR is reconstructed.',
            'Full P4 211 obligations, Table I22500,500000 projections and approximately50000 pointpairs unchanged.'],
        'no_retry_reset_or_resume':True}

def validate(spec,protocol,execute=False):
    expected=draft()
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews','execution_readiness')),
        'EXACT_CURRENT_FULL_SOURCE_QUEUE_AND_RECIPE_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and
        all(type(v)is bool for v in spec['reviews'].values()),'EXACT_BOOLEAN_REVIEW_FIELDS')
    if not execute:return None
    require(spec['source_ready']and spec['frozen']and all(spec['reviews'].values())and
        spec['execution_readiness']=='FROZEN_REVIEWED_READY','ACTUAL_SOURCE_REVIEW_FREEZE_REQUIRED')
    require(spec['fixed_queue']['all_edges_structural_qualified'],'SOURCE_FALSE_OR_INCOMPLETE_OR_NONSTRICT_PATH_BLOCKS_QUERY')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in OWN+[str(protocol.relative_to(ROOT))]:
        require(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes(),
            'UNCOMMITTED_SOURCE_OR_PROTOCOL '+name)
    return commit

def node_worker(protocol):
    # Metadata-only adapter of the already-qualified local node worker, not a
    # new numerical worker. Full source bytes/hash remain bound in OWN/spec.
    spec=load(protocol)
    require(spec['run_id']==RUN and spec['claim_id']==CLAIM and spec['full_queue_node_count']<=MAX_NODES,
        'WORKER_FIXED_FULL_QUEUE_UNDER_CAP_REQUIRED')
    require(all(n['collision_required']is True for n in spec['fixed_queue']['nodes']),'ALL_PATH_NODES_REQUIRE_COLLISION')
    local.RUN=RUN;local.CLAIM=CLAIM;local.OWN=OWN
    local.node_worker(protocol)

def execute(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN;claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXISTING_CLAIM_OR_RUN_NO_RETRY')
    started=time.monotonic();cpu_start=cpu();budget=evidence=None;error=None;diagnostics=[];counts=Counter()
    queue=spec['fixed_queue']['nodes'];record={'schema':'P4_R2_ABB_RRT_NR_PATH_EXECUTION_V1','run_id':RUN,
        'source_commit':commit,'protocol':str(protocol.relative_to(ROOT)),'protocol_sha256':sha(protocol),
        'claim':str(claim.relative_to(ROOT)),'budget':spec['budget'],'source_provenance':spec['source_provenance'],
        'classification':spec['classification'],'bound_files_sha256':spec['bound_files_sha256'],
        'prior_executions':spec['prior_executions'],'previous_r2_wall_s':spec['previous_r2_wall_s'],
        'previous_r2_cpu_s':spec['previous_r2_cpu_s'],'zero_calls':spec['zero_calls'],
        'status':'UNKNOWN_SETUP_PREFIX_RETAINED','continuous_collision_certificate':False,'started_at_utc':utc()}
    try:
        folder.mkdir();new_json(claim,{'schema':'P4_R2_ABB_RRT_NR_PATH_CLAIM_V1','claim_id':CLAIM,
            'parent_pid':os.getpid(),'source_commit':commit,'protocol_sha256':record['protocol_sha256'],
            'budget':spec['budget'],'created_at_utc':utc(),'no_retry_reset_or_resume':True})
        record['claim_sha256']=sha(claim);new_json(folder/'setup_started.json',record)
        new_json(folder/'full_fixed_queue.json',spec['fixed_queue']);new_json(folder/'node_queue.json',queue)
        record['node_queue_sha256']=sha(folder/'node_queue.json')
        if len(queue)>MAX_NODES:
            record['status']='UNKNOWN_FULL_QUEUE_EXCEEDS_2048_CAP';raise RuntimeError(record['status'])
        os.environ.update(THREADS);sys.path.insert(0,str(ROOT))
        import qualify_p4_full_r2_vi_rss_reconstructed as common
        budget=common.RunBudget(spec,spec['previous_r2_wall_s'],spec['previous_r2_cpu_s'])
        budget.started=started;budget.cpu_start=cpu_start
        signal.setitimer(signal.ITIMER_REAL,max(.000001,budget.wall_cap-(time.monotonic()-started)))
        class LiveEvidence(common.Evidence):
            def process(self,command,input_text,label):
                self.budget.remaining();self.process_number+=1;stem=f'{self.process_number:05d}_{label}'
                inp,out,err=[self.folder/(stem+s)for s in('.input.txt','.stdout.txt','.stderr.txt')]
                with inp.open('x')as f:f.write(input_text)
                proc=None;begun=time.monotonic();self.event('process_started',label=label,command=command,input=str(inp.relative_to(ROOT)))
                try:
                    with inp.open()as fi,out.open('x')as fo,err.open('x')as fe:
                        proc=subprocess.Popen(command,stdin=fi,stdout=fo,stderr=fe,cwd=ROOT,start_new_session=True,env=os.environ.copy())
                        while proc.poll()is None:
                            self.budget.remaining()
                            require(self.budget.cpu()-self.budget.cpu_start+builder.live_group_cpu(proc.pid)<self.budget.cpu_cap,
                                'PARENT_PLUS_LIVE_GROUP_CPU_CAP')
                            try:proc.wait(timeout=.02)
                            except subprocess.TimeoutExpired:pass
                except BaseException:
                    if proc is not None and proc.poll()is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                    self.event('process_interrupted',label=label,wall_s=time.monotonic()-begun);raise
                self.event('process_finished',label=label,exit_code=proc.returncode,wall_s=time.monotonic()-begun,
                    stdout_sha256=sha(out),stderr_sha256=sha(err))
                self.budget.remaining();require(proc.returncode==0,'NODE_WORKER_FAILED '+str(proc.returncode))
                return out.read_text()
        evidence=LiveEvidence(folder,budget)
        raw=evidence.process([sys.executable,str(Path(__file__).resolve()),'--node-worker',str(protocol)],
            json.dumps({'node_queue_sha256':record['node_queue_sha256'],'wall_remaining_s':budget.remaining(),
                'worker_monotonic_start':time.monotonic()})+'\n','independent_full_node_queue')
        answers=[json.loads(line.split(' ',1)[1])for line in raw.splitlines()if line.startswith('P4_NR_NODE_RESPONSE ')]
        require([a['node_id']for a in answers]==list(range(len(queue))),'ALL_UNIQUE_NODES_MUST_COMPLETE')
        for source,answer in zip(queue,answers):
            n=answer['result'];require(all(n[k]==v for k,v in source.items()),'SOURCE_NODE_IDENTITY_OR_REFS_CHANGED')
            require(qkey(n['q12'])==qkey(source['q12']),'SOURCE_NODE_BINARY64_CHANGED')
            require(n['stage']=='COMPLETED'and n['node_qualified']is True,'INDEPENDENT_PATH_NODE_FAILED '+str(source['node_id']))
        if answers:counts.update(answers[-1]['observed_counts'])
        require(counts['math_arm_FK_started']==counts['math_arm_FK_completed']==2*len(queue)and
            counts['collision_calls_started']==counts['collision_calls_completed']==len(queue)and
            counts['adapter_arm_FK_J_started']==counts['adapter_arm_FK_J_completed']==4*len(queue),'EXACT_ACTUAL_SCIENTIFIC_COUNTS')
        record['status']='PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH';budget.remaining()
    except BaseException as exc:
        error=exc;record['termination_reason']=repr(exc)
        if record['status']!='UNKNOWN_FULL_QUEUE_EXCEEDS_2048_CAP':record['status']='UNKNOWN_OR_FAILED_PATH_PREFIX_RETAINED'
        if evidence is not None:
            try:evidence.event('run_stopped',reason=repr(exc))
            except BaseException as err:diagnostics.append({'stage':'stop_event','error':repr(err)})
    finally:
        if budget is not None:
            try:budget.close()
            except BaseException as exc:diagnostics.append({'stage':'budget_close','error':repr(exc)})
        completed=[load(name)['node_id']for name in sorted(folder.glob('node_[0-9][0-9][0-9][0-9][0-9].json'))]
        node_responses=[];worker_events=[]
        for name in sorted(folder.glob('*.stdout.txt')):
            for line in name.read_text().splitlines():
                if line.startswith('P4_NR_NODE_RESPONSE '):
                    try:node_responses.append(json.loads(line.split(' ',1)[1]))
                    except ValueError as exc:diagnostics.append({'stage':'raw_stdout_tail','file':str(name),'error':repr(exc)})
        for name in sorted(folder.glob('*.stderr.txt')):
            for line in name.read_text().splitlines():
                if line.startswith('P4_NR_NODE_EVENT '):
                    try:worker_events.append(json.loads(line.split(' ',1)[1]))
                    except ValueError as exc:diagnostics.append({'stage':'raw_stderr_tail','file':str(name),'error':repr(exc)})
        for ev in worker_events:
            if ev['event']in('math_arm_FK_started','math_arm_FK_completed','adapter_arm_FK_J_started',
                'adapter_arm_FK_J_completed','collision_started','collision_completed'):counts['actual_'+ev['event']]+=1
            if ev['event']=='collision_completed':
                counts['actual_adapter_PQP_queries']+=ev['PQP_queries']
                for variant,n in ev['variant_query_counts'].items():counts['actual_adapter_'+variant+'_PQP_queries']+=n
        counts['actual_node_responses_retained']=len(node_responses)
        try:new_json(folder/'raw_prefix_inventory.json',{'node_responses':node_responses,'worker_events':worker_events,'actual_observed_only':True})
        except BaseException as exc:diagnostics.append({'stage':'raw_inventory','error':repr(exc)})
        after={}
        for name in spec['bound_files_sha256']:
            try:after[name]=sha(path(name))
            except BaseException as exc:after[name]=None;diagnostics.append({'stage':'hash '+name,'error':repr(exc)})
        if after!=spec['bound_files_sha256']:record['status']='STOP_BOUND_ASSET_CHANGED'
        try:
            record.update(protocol_after_sha256=sha(protocol),claim_after_sha256=sha(claim))
            if record['protocol_after_sha256']!=record['protocol_sha256']or record['claim_after_sha256']!=record.get('claim_sha256'):
                record['status']='STOP_PROTOCOL_OR_CLAIM_CHANGED'
        except BaseException as exc:diagnostics.append({'stage':'protocol_claim_after','error':repr(exc)})
        wall=time.monotonic()-started;used_cpu=cpu()-cpu_start
        if wall>=min(120.,3600.-spec['previous_r2_wall_s'])or used_cpu>=min(240.,7200.-spec['previous_r2_cpu_s']):
            record['status']='UNKNOWN_WALL_OR_CPU_CAP_PREFIX_RETAINED'
        if diagnostics:record['status']='STOP_EVIDENCE_OR_CLEANUP_ERROR'
        record.update(wall_s=wall,cpu_s=used_cpu,counts=dict(counts),completed_node_ids=completed,
            uncompleted_node_ids=[n['node_id']for n in queue if n['node_id']not in completed],
            full_node_queue_count=len(queue),full_node_queue_checked=bool(queue)and len(completed)==len(queue),
            bound_files_after_sha256=after,diagnostics=diagnostics,ended_at_utc=utc(),
            partial_accounting='Saved response/events count only completed/started observations; entire frozen queue and unchecked tail retained. No prefix PASS.')
        try:new_json(folder/'execution.json',record)
        finally:
            if evidence is not None:evidence.events.close()
    print(json.dumps({k:record[k]for k in('status','wall_s','cpu_s','full_node_queue_count','full_node_queue_checked','counts')}))
    if error:raise error
    require(record['status']=='PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH',record['status'])

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--validate-draft',type=Path)
    g.add_argument('--protocol',type=Path);g.add_argument('--node-worker',type=Path,help=argparse.SUPPRESS);a=p.parse_args()
    if a.node_worker:node_worker(a.node_worker.resolve());return
    if a.describe_protocol:print(json.dumps(draft(),ensure_ascii=False,indent=2,allow_nan=False));return
    protocol=(a.validate_draft or a.protocol).resolve();spec=load(protocol)
    if a.validate_draft:validate(spec,protocol);print('STATIC_DRAFT_VALIDATED_ZERO_SCIENCE');return
    execute(spec,protocol)

if __name__=='__main__':main()
