#!/usr/bin/env python3
"""Audit the fixed saved E2E01 path; never plan, project, smooth, or retry.

--describe reads saved bytes/arrays only. Every dense node is frozen. 2048 is
an execution resource stop, never path truncation or a prefix success claim.
"""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from collections import Counter
import json,math,struct,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import qualify_p4_full_r2_vi_rss_reconstructed as common
RUN='20261015_R2_ABB_RRT_PATH01'
CLAIM='P4_R2_ABB_RRT_PATH_120W_240CPU_20261015'
SOURCE_RUN='20261015_R2_ABB_RRT_PCS_E2E01'
SOURCE_FOLDER='results/p4_full/'+SOURCE_RUN
SOURCE_EXECUTION=SOURCE_FOLDER+'/execution.json'
SOURCE_RESULT=SOURCE_FOLDER+'/runtime/result.json'
SOURCE_PROTOCOL='configs/p4_full/r2_abb_rrt_pcs_e2e_qualification_v1.json'
SOURCE_CLAIM='results/p4_full/P4_R2_ABB_RRT_PCS_E2E_SEED7_30W_60CPU_20261015.claim.json'
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_pcs_e2e_v1')
BINARY=BUILD/'geometry_consistent_observed/p4_abb_rrt_pcs_e2e'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
ENDPOINTS=[f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_{i}.json' for i in (0,1)]
PRE='reports/P4_FULL_R2_ABB_RRT_PATH_PRE_DRAFT_20261015.md'
OWN=[str(Path(__file__).relative_to(ROOT)),PRE,'scripts/recover_p4_full_r2_endpoints.py',
 'scripts/qualify_p4_full_r2_vi_rss_reconstructed.py','scripts/qualify_p4_full_r2_abb_rrt_pcs_e2e.py',
 'baselines/p4_full/geometry_consistent/collision_adapter.py',
 'baselines/p4_full/geometry_consistent/physical_nr.py',
 'baselines/p4_full/abb_independent_oracle.py','baselines/p4_full/analyze_comau_native_qualification.py',
 'baselines/p4_full/geometry_consistent/rss_geometry.py']
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
 'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon}
MAX_NODES=2048

def path(value):
    p=Path(value);return p if p.is_absolute() else ROOT/p

def load(value):return json.loads(path(value).read_text())

def require(condition,reason):
    if not condition:raise ValueError(reason)

def durable_new(filename,value):
    with Path(filename).open('x') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())

def q12(q):
    require(isinstance(q,list) and len(q)==12 and
        all(type(v) in (int,float) and math.isfinite(v) for v in q),'FINITE_NUMERIC_Q12_REQUIRED')
    return q

def key(q):return struct.pack('>12d',*q12(q))

def bind(files,filename,wanted=None):
    name=str(filename);got=common.sha(path(name))
    require(wanted is None or wanted==got,'SOURCE_HASH_CHANGED '+name);files[name]=got
    return load(name) if name.endswith('.json') else None

def source_provenance(source):
    """Actual execution/protocol/claim/build/A01, not self-reported path JSON."""
    require(path(source).resolve()==path(SOURCE_RESULT).resolve(),'FIXED_E2E01_RESULT_REQUIRED')
    files={};execution=bind(files,SOURCE_EXECUTION)
    require(execution['schema']=='P4_R2_ABB_RRT_PCS_E2E_EXECUTION_V1' and execution['run_id']==SOURCE_RUN,'SOURCE_EXECUTION_SCHEMA')
    require(execution['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT','SOURCE_EXECUTION_NOT_EXACT_COMPLETED')
    require(path(execution['protocol']).resolve()==path(SOURCE_PROTOCOL).resolve(),'SOURCE_PROTOCOL_PATH')
    protocol=bind(files,SOURCE_PROTOCOL,execution['protocol_sha256'])
    require(protocol['frozen'] is True and protocol['run_id']==SOURCE_RUN and bool(protocol['reviews']) and
        all(v is True for v in protocol['reviews'].values()),'SOURCE_NOT_FROZEN_REVIEWED')
    require(path(execution['claim']).resolve()==path(SOURCE_CLAIM).resolve(),'SOURCE_CLAIM_PATH')
    claim=bind(files,SOURCE_CLAIM,execution['claim_sha256'])
    require(claim['protocol_sha256']==files[SOURCE_PROTOCOL],'SOURCE_CLAIM_PROTOCOL_HASH')
    require(path(execution['build_manifest']).resolve()==(BUILD/'manifest.json').resolve(),'SOURCE_BUILD_PATH')
    manifest=bind(files,str(BUILD/'manifest.json'),execution['build_manifest_sha256'])
    require(manifest['status']=='BUILT_NOT_QUERIED' and manifest['exit_code']==0,'SOURCE_BUILD_FAILED')
    assets=protocol['build_assets']
    require(assets['status']=='BUILT_NOT_QUERIED' and path(assets['binary']).resolve()==BINARY.resolve() and
        path(execution['binary']).resolve()==BINARY.resolve(),'SOURCE_BINARY_PATH')
    bind(files,str(BINARY),execution['binary_sha256'])
    require(assets['binary_sha256']==files[str(BINARY)]==manifest['binary_sha256'],'SOURCE_BINARY_HASH')
    for filename,wanted in assets['files'].items():bind(files,filename,wanted)
    for filename,wanted in protocol['own_source_sha256'].items():bind(files,filename,wanted)
    for field,hashfield in [('protocol','protocol_sha256'),('claim','claim_sha256')]:
        bind(files,manifest[field],manifest[hashfield])
    engineering=bind(files,manifest['engineering_execution'])
    require(engineering['manifest_sha256']==files[str(BUILD/'manifest.json')] and
        engineering['source_commit']==manifest['source_commit'],'SOURCE_ENGINEERING_EXECUTION_LINK')
    points=[bind(files,p,protocol['endpoint_sources_sha256'][p]) for p in ENDPOINTS]
    require(all(p['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED' and
        p['source_policy_collision_qualified'] is True for p in points),'A01_ENDPOINT_QUALIFICATION')
    expected={'environment':'II','seed':7,'range_rad':2.6,'goal_bias':.05,'solve_seconds':10.,
        'start_q12':points[0]['selected_q_rad'],'goal_q12':points[1]['selected_q_rad'],
        'bounds_low_rad':[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2,
        'bounds_high_rad':[2.88,1.919,1.22,2.79,2.09,3.1416]*2}
    require(protocol['request']==expected and execution['driver_request']==expected,'SOURCE_REQUEST_MISMATCH')
    require(path(execution['result']).resolve()==path(SOURCE_RESULT).resolve(),'SOURCE_RESULT_PATH')
    d=bind(files,SOURCE_RESULT,execution['result_sha256'])
    require(execution['returncode']==0 and type(execution['solve_dispatched']) is int and
        execution['solve_dispatched']==1 and type(execution['solve_calls_from_result']) is int and
        execution['solve_calls_from_result']==1,'SOURCE_NOT_ONE_COMPLETED_SOLVE')
    require(d['schema']=='P4_ABB_RRT_PCS_END_TO_END_V1' and
        d['status']=='SOURCE_SOLVE_RETURNED_PENDING_INDEPENDENT_PATH_AUDIT' and d['request']==expected and
        type(d['solve_calls']) is int and d['solve_calls']==1,'SOURCE_DRIVER_RESULT_MISMATCH')
    require(d['exact'] is True and d['approximate'] is False and d['has_solution'] is True,'EXACT_NONAPPROXIMATE_REQUIRED')
    for name in ('environment','seed','range_rad','goal_bias','start_q12','goal_q12','bounds_low_rad','bounds_high_rad'):
        require(d[name]==expected[name],'SOURCE_METADATA_MISMATCH '+name)
    require(d['formal_table_I_calls']==0,'SOURCE_FORMAL_QUALIFICATION_MIXED')
    rec_log=SOURCE_FOLDER+'/runtime/reconstruction_attempts.jsonl';bind(files,rec_log)
    attempts=[json.loads(line) for line in path(rec_log).read_text().splitlines() if line.strip()]
    require(attempts==d['reconstruction_attempts'],'SOURCE_RECONSTRUCTION_LOG_MISMATCH')
    require(all(type(r['attempt_index']) is int and r['attempt_index']==i for i,r in enumerate(attempts)),
        'SOURCE_RECONSTRUCTION_ORDER')
    id_log=SOURCE_FOLDER+'/runtime/identify_observations.jsonl';bind(files,id_log)
    identify=[json.loads(line) for line in path(id_log).read_text().splitlines() if line.strip()]
    require(d['identify_observation_count']==len(identify),'SOURCE_IDENTIFY_LOG_COUNT')
    return d,files,{'execution':SOURCE_EXECUTION,'protocol':SOURCE_PROTOCOL,'claim':SOURCE_CLAIM,
        'build_manifest':str(BUILD/'manifest.json'),'binary':str(BINARY),'result':SOURCE_RESULT,'request':expected,
        'source_commit':execution['source_commit'],'reconstruction_log':rec_log,'identify_log':id_log}

def materialize(d):
    """Full saved queue; first success in actual ordered calls, never screening."""
    ms=d['milestones_q12'];attempts=d['reconstruction_attempts']
    require(len(ms)>=2 and key(ms[0])==key(d['start_q12']) and key(ms[-1])==key(d['goal_q12']),
        'EXACT_ENDPOINTS_REQUIRED')
    nodes=[];edges=[];lookup={};cursor=0
    for ei,(a,b) in enumerate(zip(ms,ms[1:])):
        consumed=[];chosen=None
        while cursor<len(attempts):
            e=attempts[cursor]
            require(key(e['qa12'])==key(a) and key(e['qb12'])==key(b),'SOURCE_EDGE_ATTEMPT_ORDER')
            consumed.append(cursor);cursor+=1
            require(type(e['returned']) is bool,'SOURCE_RETURN_TYPE')
            if e['returned']:chosen=e;break
        require(chosen is not None,'MISSING_SUCCESSFUL_RECONSTRUCTED_EDGE');e=chosen;qs=e['path_q12']
        require(len(qs)>=2 and key(qs[0])==key(a) and key(qs[-1])==key(b) and
            type(e['active_chain']) is int and e['active_chain'] in (0,1) and
            type(e['branch']) is int and e['branch'] in range(8),'INVALID_EDGE_PATH_OR_IDENTITY')
        refs=[]
        for q in qs:
            k=key(q)
            if k not in lookup:lookup[k]=len(nodes);nodes.append(q)
            refs.append(lookup[k])
        leaves=[math.sqrt(math.fsum((u-v)**2 for u,v in zip(x,y))) for x,y in zip(qs,qs[1:])]
        require(all(math.isfinite(v) and v<GATES['strict_leaf_full12_L2_rad'] for v in leaves),
            'SOURCE_RESOLUTION_LEAF_NOT_STRICT')
        edges.append({'edge_index':ei,'qa12':a,'qb12':b,'active_chain':e['active_chain'],'branch':e['branch'],
            'selected_attempt_index':e['attempt_index'],'consumed_attempt_indices':consumed,
            'node_ids':refs,'leaf_distances_rad':leaves})
    require(cursor==len(attempts),'UNMATCHED_SOURCE_RECONSTRUCTION_ATTEMPTS')
    # A read-only provenance check, not another motion validation or solve.
    tree=d['planner_data'];vs=tree['vertices'];links=tree['edges'];graph={}
    require(tree['num_vertices']==len(vs) and tree['num_edges']==len(links),'SOURCE_TREE_COUNTS')
    require([v['index'] for v in vs]==list(range(len(vs))),'SOURCE_TREE_VERTEX_IDS')
    for a,b in links:
        require(type(a) is int and type(b) is int and 0<=a<len(vs) and 0<=b<len(vs),'SOURCE_TREE_EDGE_INDEX')
        graph.setdefault(a,set()).add(b)
    possible={v['index']:[v['index']] for v in vs if key(v['q12'])==key(ms[0]) and v['start'] is True}
    for q in ms[1:]:
        possible={child:prefix+[child] for parent,prefix in possible.items()
            for child in sorted(graph.get(parent,())) if key(vs[child]['q12'])==key(q)}
        require(bool(possible),'MILESTONE_PATH_NOT_IN_SOURCE_TREE')
    goal_paths=[p for i,p in sorted(possible.items()) if vs[i]['goal'] is True]
    require(bool(goal_paths),'MILESTONE_END_NOT_SOURCE_TREE_GOAL')
    return {'nodes':nodes,'edges':edges,'source_tree_vertex_path':goal_paths[0],
        'source_milestone_count':len(ms),'source_attempt_count':len(attempts),
        'deduplication':'Packed binary64 q12 bytes, including signed zero; every original edge reference retained.',
        'node_limit_policy':'All dense nodes frozen;2048 is execution stop only, never truncate or PASS with tail.'}

def draft(source):
    d,files,provenance=source_provenance(source);queue=materialize(d)
    prior=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json') if p.parent.name!=RUN)
    require(SOURCE_EXECUTION in prior,'SOURCE_EXECUTION_NOT_IN_LEDGER');values=[load(p) for p in prior]
    require(all(all(type(r[k]) in (int,float) and math.isfinite(r[k]) and r[k]>=0 for k in ('wall_s','cpu_s'))
        for r in values),'INVALID_PRIOR_COST')
    for filename in OWN+prior:bind(files,filename)
    m=bind(files,COLLISION);entries=[e for e in m['entries'] if e['model']=='abb']
    require(sorted(e['variant'] for e in entries)==['aligned','native'],'EXACT_COLLISION_VARIANTS_REQUIRED')
    for entry in entries:
        require(entry['exit_code']==0,'COLLISION_BUILD_FAILED');bind(files,entry['binary'],entry['binary_sha256'])
        for r,w in entry['source_files_sha256'].items():bind(files,str(Path(entry['source_root'])/r),w)
        for r,w in entry['mesh_sha256'].items():bind(files,str(Path(entry['cwd'])/'simulator'/r),w)
    n=min(len(queue['nodes']),MAX_NODES)
    return {'schema':'P4_R2_ABB_RRT_PATH_QUALIFICATION_V1','frozen':False,'run_id':RUN,'claim_id':CLAIM,
        'classification':'RECONSTRUCTED_ENDPOINTS_AND_R2_NUMERICS / AUTHOR_RRT_PCS / DISCRETE_SOURCE_POLICY_PATH_ONLY',
        'source_result':SOURCE_RESULT,'environment':'II','source_provenance':provenance,'fixed_queue':queue,
        'budget':{'wall_s':120.,'cpu_s':240.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'previous_r2_wall_s':math.fsum(r['wall_s'] for r in values),'previous_r2_cpu_s':math.fsum(r['cpu_s'] for r in values),
        'prior_executions':prior,'bound_files_sha256':files,'gates':GATES,
        'max_nodes_per_execution':MAX_NODES,'full_queue_node_count':len(queue['nodes']),
        'max_math_arm_FK':2*n,'max_collision_calls':n,'max_adapter_internal_arm_FK_J':4*n,
        'zero_calls':{'IK':0,'NR':0,'projection':0,'RBS':0,'solve':0,'RNG':0,'VI_constructions':0},
        'scope':'Every saved dense vertex; exact A01 endpoints, original mechanical bounds, independent closure, per-edge branch membership, strict source .05 leaves, aligned discrete source collision. Not CCD/full rod/omitted pairs.',
        'failure':'Retain raw partial math/collision and full unresolved tail. No retry, smoothing, projection, changed node/threshold, or PASS with unchecked tail.'}

def execute(spec,protocol):
    # Read-only invalid/frozen/duplicate admission refuses before any new claim.
    expected=draft(spec['source_result'])
    require(spec.get('frozen') is True and {**spec,'frozen':False}==expected,'FROZEN_EXACT_FULL_QUEUE_REQUIRED')
    for name in OWN+[str(protocol.relative_to(ROOT))]:
        subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        require(not subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True),'UNCOMMITTED_SOURCE '+name)
    folder=ROOT/'results/p4_full'/RUN;claim_file=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists() and not claim_file.exists(),'OUTPUT_OR_CLAIM_EXISTS_NO_RETRY')
    started=time.monotonic();cpu_start=common.RunBudget.cpu();counts=Counter();results=[];diagnostics=[]
    record={'schema':'P4_R2_ABB_RRT_PATH_EXECUTION_V1','run_id':RUN,'status':'STOP_SETUP_PREFIX_RETAINED',
        'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'protocol':str(protocol.relative_to(ROOT)),'protocol_sha256':common.sha(protocol),'claim':str(claim_file.relative_to(ROOT)),
        'budget':spec['budget'],'source_provenance':spec['source_provenance'],'bound_files_sha256':spec['bound_files_sha256'],
        'prior_executions':spec['prior_executions'],'previous_r2_wall_s':spec['previous_r2_wall_s'],
        'previous_r2_cpu_s':spec['previous_r2_cpu_s'],'classification':spec['classification'],
        'formal_planning_calls':0,'solve_calls':0,'new_VI_candidate_constructions':0,
        'continuous_collision_certificate':False,'started_at_utc':common.utc()}
    budget=events=physical_nr=original=adapter=None;error=None;current=None
    def event(kind,**v):
        if events is not None:
            events.write(json.dumps({'event':kind,'at_utc':common.utc(),**v},allow_nan=False)+'\n');events.flush()
    def retain_error(stage,exc):diagnostics.append({'stage':stage,'error':repr(exc)})
    try:
        folder.mkdir()
        durable_new(claim_file,{'schema':'P4_R2_ABB_RRT_PATH_CLAIM_V1','claim_id':CLAIM,
            'protocol':record['protocol'],'protocol_sha256':record['protocol_sha256'],'source_commit':record['source_commit'],
            'created_at_utc':common.utc(),'budget':spec['budget'],'no_retry':True})
        record['claim_sha256']=common.sha(claim_file);durable_new(folder/'setup_started.json',record)
        events=(folder/'events.jsonl').open('x',buffering=1)
        budget=common.RunBudget(spec,spec['previous_r2_wall_s'],spec['previous_r2_cpu_s'])
        from baselines.p4_full.geometry_consistent import physical_nr as physical_module
        from baselines.p4_full.geometry_consistent import collision_adapter as collision_module
        import recover_p4_full_r2_endpoints as oracle
        physical_nr,adapter=physical_module,collision_module;original=physical_nr.arm_fk_jac
        def counted(q,env,arm):
            budget.remaining();require(counts['adapter_internal_arm_FK_J_started']<spec['max_adapter_internal_arm_FK_J'],'ADAPTER_FK_CAP')
            counts['adapter_internal_arm_FK_J_started']+=1;event('adapter_internal_FK_J_started',arm=arm,q6=list(q))
            ans=original(q,env,arm);counts['adapter_internal_arm_FK_J_completed']+=1
            event('adapter_internal_FK_J_completed',arm=arm);return ans
        physical_nr.arm_fk_jac=counted
        for i,q in enumerate(spec['fixed_queue']['nodes']):
            budget.remaining()
            if i>=spec['max_nodes_per_execution']:raise common.StopQualification('FIXED_2048_NODE_RESOURCE_STOP_FULL_TAIL_UNCHECKED')
            current={'node_id':i,'q12':q,'poses':[],'branches':[],'stage':'STARTED'};event('math_node_started',node_id=i,q12=q)
            for a in range(2):
                budget.remaining();require(counts['math_arm_FK_started']<spec['max_math_arm_FK'],'MATH_FK_CAP')
                counts['math_arm_FK_started']+=1;event('math_arm_FK_started',node_id=i,arm=a+1)
                pose=oracle.arm_fk(q[6*a:6*a+6],'II',a+1);counts['math_arm_FK_completed']+=1
                current['poses'].append(pose.tolist());durable_new(folder/f'node_{i:05d}_arm{a+1}.json',current)
                event('math_arm_FK_completed',node_id=i,arm=a+1,pose=pose.tolist())
            import numpy as np
            poses=[np.asarray(p) for p in current['poses']]
            metric=oracle.matrix_error(poses[1],poses[0]@oracle.grasps_for('II')[0]@oracle.FLIP);limits=oracle.limit_score(q,'II')
            for a in range(2):
                counts['branch_identity_started']+=1
                current['branches'].append(oracle.branch_identity(q[6*a:6*a+6],'II',GATES['branch_zero_relative_epsilon']))
                counts['branch_identity_completed']+=1
            assignments=[{'edge':k,'role':e['active_chain'],'requested_branch':e['branch'],
                'branch_pass':e['branch'] in current['branches'][1-e['active_chain']]['branch_set']}
                for k,e in enumerate(spec['fixed_queue']['edges']) if i in e['node_ids']]
            mathok=(metric['position_max_abs']<=GATES['position_maxabs_mm'] and
                metric['rotation_matrix_max_abs']<=GATES['rotation_matrix_maxabs'] and limits['legal'] and
                bool(assignments) and all(a['branch_pass'] for a in assignments))
            current.update(stage='MATH_COMPLETED',closure=metric,limits=limits,edge_assignments=assignments,math_qualified=bool(mathok))
            durable_new(folder/f'node_{i:05d}_math.json',current);event('math_node_completed',node_id=i,math_qualified=bool(mathok))
            budget.remaining();require(counts['collision_calls_started']<spec['max_collision_calls'],'COLLISION_CALL_CAP')
            counts['collision_calls_started']+=1;current['stage']='COLLISION_STARTED';event('collision_started',node_id=i)
            collision=adapter.check_collision('II',q,timeout_s=min(10.,budget.remaining()),manifest_path=COLLISION)
            counts['collision_calls_completed']+=1;current.update(stage='COLLISION_RESPONSE_RETAINED',collision=collision)
            durable_new(folder/f'node_{i:05d}_collision_response.json',collision);event('collision_response_retained',node_id=i,response=collision)
            require(collision.get('status')=='CHECKED' and collision.get('selected_variant')=='aligned' and
                collision.get('manifest_sha256')==spec['bound_files_sha256'][COLLISION] and
                type(collision.get('collision')) is bool and set(collision.get('variants',{}))=={'native','aligned'},
                'COLLISION_UNQUALIFIED_RUNTIME')
            for variant,response in collision['variants'].items():
                codes=response.get('query_codes',[]);counts['PQP_queries']+=len(codes)
                require(bool(codes) and all(type(v) is int and v==0 for v in codes),'COLLISION_QUERY_ERROR '+variant)
            current.update(stage='COMPLETED',qualified=bool(mathok and not collision['collision']))
            durable_new(folder/f'node_{i:05d}.json',current);results.append(current)
            event('node_completed',node_id=i,qualified=current['qualified']);current=None;budget.remaining()
        require(len(results)==len(spec['fixed_queue']['nodes']),'COMPLETE_FULL_QUEUE_REQUIRED')
        record['status']='PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH' if all(r['qualified'] for r in results) else 'PATH_REJECTED_BY_INDEPENDENT_QUALIFICATION'
    except BaseException as exc:
        error=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc))
        if current is not None and folder.exists():
            try:durable_new(folder/f'node_{current["node_id"]:05d}_stopped_partial.json',current)
            except BaseException as write_error:retain_error('partial_node_write',write_error)
        try:event('stopped',reason=repr(exc))
        except BaseException as write_error:retain_error('stopped_event_write',write_error)
    finally:
        # Cancel alarm for evidence finalization; actual cleanup cost remains in
        # ledger and cap excess always invalidates PASS.
        if budget is not None:
            try:budget.close()
            except BaseException as exc:retain_error('budget_close',exc)
        if physical_nr is not None and original is not None:physical_nr.arm_fk_jac=original
        if adapter is not None:
            sessions=list(adapter._sessions.values())
            try:adapter.close_sessions()
            except BaseException as exc:retain_error('collision_sessions_close',exc)
            for session in sessions:
                try:
                    if session.proc.poll() is None:session.proc.kill();session.proc.wait(timeout=1.)
                except BaseException as exc:retain_error('collision_worker_reap',exc)
        after={}
        for filename in spec['bound_files_sha256']:
            try:after[filename]=common.sha(path(filename))
            except BaseException as exc:after[filename]=None;retain_error('bound_hash '+filename,exc)
        if after!=spec['bound_files_sha256']:record['status']='STOP_BOUND_ASSET_CHANGED'
        try:
            protocol_after=common.sha(protocol);claim_after=common.sha(claim_file)
            if protocol_after!=record['protocol_sha256'] or claim_after!=record.get('claim_sha256'):record['status']='STOP_PROTOCOL_OR_CLAIM_CHANGED'
            record.update(protocol_after_sha256=protocol_after,claim_after_sha256=claim_after)
        except BaseException as exc:retain_error('protocol_claim_after_hash',exc)
        wall=time.monotonic()-started;used_cpu=common.RunBudget.cpu()-cpu_start
        wall_cap=min(spec['budget']['wall_s'],spec['budget']['r2_total_wall_s']-spec['previous_r2_wall_s'])
        cpu_cap=min(spec['budget']['cpu_s'],spec['budget']['r2_total_cpu_s']-spec['previous_r2_cpu_s'])
        if wall>=wall_cap or used_cpu>=cpu_cap:record['status']='STOP_WALL_OR_CPU_BUDGET_PREFIX_RETAINED'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        record.update(counts=dict(counts),wall_s=wall,cpu_s=used_cpu,node_count=len(spec['fixed_queue']['nodes']),
            completed_nodes=len(results),qualified_nodes=sum(r['qualified'] for r in results),
            uncompleted_node_ids=list(range(len(results),len(spec['fixed_queue']['nodes']))),
            full_queue_checked=len(results)==len(spec['fixed_queue']['nodes']),bound_files_after_sha256=after,
            diagnostics=diagnostics,ended_at_utc=common.utc())
        try:
            folder.mkdir(exist_ok=True);durable_new(folder/'execution.json',record)
        finally:
            if events is not None:events.close()
    print(json.dumps({k:record[k] for k in ('status','completed_nodes','qualified_nodes','wall_s','cpu_s')}))
    if error is not None:raise error
    if record['status'].startswith('STOP_'):raise RuntimeError(record['status'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe',type=Path);group.add_argument('--protocol',type=Path);args=parser.parse_args()
    if args.describe:print(json.dumps(draft(args.describe),ensure_ascii=False,indent=2))
    else:
        protocol=args.protocol.resolve();execute(load(protocol),protocol)
