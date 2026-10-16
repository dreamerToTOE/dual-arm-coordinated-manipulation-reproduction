#!/usr/bin/env python3
"""Compact, separately implemented stdlib-only saved NR-path POST.

No imports of scientific modules/runners, no query, compiler, solve or RNG.
The author also wrote the path runner: not personnel-independent verification.
Large scientific arrays stay in their original files, bound by SHA256; this
report keeps aggregate checks, every failure, and bounded necessary summaries.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone,timedelta
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
RUN='20261015_R2_ABB_RRT_NR_PATH01'
FOLDER=ROOT/'results/p4_full'/RUN
SOURCE='results/p4_full/20261015_R2_ABB_RRT_NR_E2E01'
REPORT=ROOT/'reports/P4_FULL_R2_ABB_NR_PATH_INDEPENDENT_POST_20261016'
PRESERVED_REPORTS=[ROOT/'reports/P4_FULL_R2_ABB_NR_LOCAL_INDEPENDENT_POST_20261015.json',
    ROOT/'reports/P4_FULL_R2_ABB_NR_LOCAL_INDEPENDENT_POST_20261015.md']
DEG_LIMITS=[(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]*2
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
    'strict_leaf_full12_L2_rad':.05,'source_literal_pi_for_mechanical_limits':3.1416,
    'source_PQP_tolerance_mm':8.,'fixed_active_or_branch_gate':False,
    'continuous_collision_certificate':False}

def path(value):
    p=Path(value);return p if p.is_absolute()else ROOT/p
def load(name):return json.loads(path(name).read_text())
def sha(name):return hashlib.sha256(path(name).read_bytes()).hexdigest()
def jsonl(name):return[json.loads(s)for s in path(name).read_text().splitlines()if s.strip()]
def prefix(name,start):return[json.loads(s[len(start):])for s in path(name).read_text().splitlines()if s.startswith(start)]
def qkey(q):return struct.pack('>12d',*q)
def finite_q(q):return isinstance(q,list)and len(q)==12 and all(type(v)in(int,float)and math.isfinite(v)for v in q)
def distance(a,b):return math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,b)))
def mm(a,b):return[[math.fsum(a[i][k]*b[k][j]for k in range(4))for j in range(4)]for i in range(4)]
def flatten(value):
    if isinstance(value,list):return[v for row in value for v in flatten(row)]
    return[value]
def shape(value):return[len(value),[shape(v)for v in value]]if isinstance(value,list)else None
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def compact(value):
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
    if len(raw)<=1024:return value
    return{'omitted_duplicate_value':True,'canonical_json_sha256':hashlib.sha256(raw.encode()).hexdigest(),
        'canonical_json_characters':len(raw),'type':type(value).__name__,
        'items':len(value)if isinstance(value,(list,dict,str))else None,
        'original_evidence':'Full original value remains in source files referenced by input_artifacts_sha256.'}

class Audit:
    def __init__(self):self.total=0;self.passed=0;self.failed=[];self.categories=Counter();self.failed_categories=Counter()
    def add(self,name,ok,**evidence):
        self.total+=1;category=name.split('.',1)[0];self.categories[category]+=1
        if ok:self.passed+=1
        else:self.failed_categories[category]+=1;self.failed.append({'check':name,'passed':False,**{k:compact(v)for k,v in evidence.items()}})
        return bool(ok)
    def eq(self,name,a,b):return self.add(name,a==b,actual=a,expected=b)
    def exactq(self,name,a,b):return self.eq(name,qkey(a).hex(),qkey(b).hex())
    def near(self,name,a,b,tolerance):
        aa,bb=flatten(a),flatten(b)
        valid=shape(a)==shape(b)and all(type(v)in(int,float)and math.isfinite(v)for v in aa+bb)
        err=max((abs(x-y)for x,y in zip(aa,bb)),default=0.)if valid else None
        return self.add(name,valid and err<=tolerance,max_abs_error=err,tolerance=tolerance)

def rebuild(d,a):
    nodes=[];lookup={};edges=[];milestones=d['milestones_q12'];attempts=d['reconstruction_attempts']
    a.add('structure.at_least_two_milestones',len(milestones)>=2)
    a.exactq('structure.first_start',milestones[0],d['start_q12']);a.exactq('structure.last_goal',milestones[-1],d['goal_q12'])
    def add(q,ref):
        a.add('structure.all_saved_q_finite',finite_q(q))
        k=qkey(q)
        if k not in lookup:
            lookup[k]=len(nodes);nodes.append({'node_id':len(nodes),'environment':'II','q12':q,'refs':[],'collision_required':True})
        nodes[lookup[k]]['refs'].append(ref);return lookup[k]
    mids=[add(q,{'kind':'milestone','milestone_index':i})for i,q in enumerate(milestones)]
    a.eq('structure.exact_original_attempt_count',len(attempts),len(milestones)-1)
    for ai,attempt in enumerate(attempts):
        n='structure.attempt'+str(ai)
        a.eq(n+'.schema',attempt['schema'],'P4_ABB_RRT_NR_RECONSTRUCTION_DRAFT_V1')
        a.add(n+'.index_and_bool_types',type(attempt['attempt_index'])is int and attempt['attempt_index']==ai and type(attempt['returned'])is bool)
        a.eq(n+'.post_return_observation',attempt['observation'],'ORIGINAL_STATE_LEVEL_CALL_COMPLETED_POST_RETURN')
        for side in('qa12','qb12'):add(attempt[side],{'kind':'attempt_endpoint','attempt_index':ai,'side':side,'returned':attempt['returned']})
        qs=attempt['path_q12'];ids=[add(q,{'kind':'original_dense_path','attempt_index':ai,'path_index':i,'returned':attempt['returned']})for i,q in enumerate(qs)]
        leaves=[distance(qa,qb)for qa,qb in zip(qs,qs[1:])]
        ordered=ai<len(milestones)-1 and qkey(attempt['qa12'])==qkey(milestones[ai])and qkey(attempt['qb12'])==qkey(milestones[ai+1])
        exact=len(ids)>=2 and qkey(qs[0])==qkey(attempt['qa12'])and qkey(qs[-1])==qkey(attempt['qb12'])
        strict=all(v<.05 for v in leaves)
        edges.append({'edge_index':ai,'selected_attempt_index':ai,'source_returned':attempt['returned'],
            'qa12':attempt['qa12'],'qb12':attempt['qb12'],'milestone_edge_order_exact':ordered,
            'dense_first_last_binary64_exact':exact,'node_ids':ids,'leaf_distances_rad':leaves,
            'all_original_leaf_distances_strict':strict,'structural_qualified':bool(attempt['returned']and ordered and exact and strict)})
        a.add(n+'.source_true_original_complete_strict',edges[-1]['structural_qualified'])
    tree=d['planner_data'];vertices=tree['vertices'];links=tree['edges'];graph={}
    a.eq('tree.vertex_count',tree['num_vertices'],len(vertices));a.eq('tree.edge_count',tree['num_edges'],len(links))
    a.eq('tree.vertex_ids',[v['index']for v in vertices],list(range(len(vertices))))
    for i,(parent,child)in enumerate(links):
        good=type(parent)is int and type(child)is int and 0<=parent<len(vertices)and 0<=child<len(vertices)
        a.add('tree.edge'+str(i)+'.valid_index',good)
        if good:graph.setdefault(parent,set()).add(child)
    possible={v['index']:[v['index']]for v in vertices if qkey(v['q12'])==qkey(milestones[0])and v['start']is True}
    for i,q in enumerate(milestones[1:]):
        possible={child:prior+[child]for parent,prior in possible.items()for child in sorted(graph.get(parent,()))if qkey(vertices[child]['q12'])==qkey(q)}
        a.add('tree.milestone'+str(i+1)+'.directed_source_sequence',bool(possible))
    goal_paths=[value for i,value in sorted(possible.items())if vertices[i]['goal']is True]
    a.add('tree.path_reaches_marked_goal',bool(goal_paths))
    return{'nodes':nodes,'edges':edges,'milestone_node_ids':mids,'source_milestone_count':len(milestones),
        'source_attempt_count':len(attempts),'source_tree_vertex_path':goal_paths[0]if goal_paths else [],
        'all_edges_structural_qualified':len(attempts)==len(milestones)-1 and all(e['structural_qualified']for e in edges),
        'deduplication':'Environment II plus packed big-endian binary64 full12 including signed zero; preserve all milestone/attempt/path refs.',
        'queue_policy':'All milestones and every original completed Confs including falseprefix retained; no resampling or path selection.'}

def audit():
    a=Audit();artifacts={}
    def bound(name,wanted=None):
        name=str(name);actual=sha(name);artifacts[name]=actual
        if wanted is not None:a.eq('provenance.hash.'+name,actual,wanted)
        return load(name)if name.endswith('.json')else None
    e=bound(FOLDER/'execution.json');p=bound(e['protocol'],e['protocol_sha256']);c=bound(e['claim'],e['claim_sha256'])
    a.eq('protocol.frozen',p['frozen'],True);a.add('protocol.all_reviews',bool(p['reviews'])and all(v is True for v in p['reviews'].values()))
    a.eq('protocol.readiness',p['execution_readiness'],'FROZEN_REVIEWED_READY');a.eq('protocol.source_ready',p['source_ready'],True)
    a.eq('protocol.gates',p['gates'],GATES);a.eq('protocol.max_unique_nodes',p['max_unique_nodes'],2048)
    a.eq('protocol.execution_schema',e['schema'],'P4_R2_ABB_RRT_NR_PATH_EXECUTION_V1');a.eq('protocol.run_id',e['run_id'],RUN)
    a.eq('protocol.claim_id',c['claim_id'],p['claim_id']);a.eq('protocol.one_shot',c['no_retry_reset_or_resume'],True)
    for key in('source_commit','protocol_sha256','budget'):a.eq('protocol.claim_'+key,c[key],e[key])
    a.eq('protocol.before_after',e['protocol_after_sha256'],e['protocol_sha256']);a.eq('protocol.claim_before_after',e['claim_after_sha256'],e['claim_sha256'])
    a.eq('protocol.bindings',p['bound_files_sha256'],e['bound_files_sha256']);a.eq('protocol.binding_before_after',e['bound_files_after_sha256'],e['bound_files_sha256'])
    a.eq('protocol.source_provenance',e['source_provenance'],p['source_provenance'])
    for name,wanted in p['bound_files_sha256'].items():bound(name,wanted)
    for name in list(p['bound_files_sha256'])+[e['protocol']]:
        if not Path(name).is_absolute()and(name.startswith(('scripts/','baselines/'))or name==e['protocol']):
            blob=subprocess.check_output(['git','show',e['source_commit']+':'+name],cwd=ROOT)
            a.eq('provenance.committed_blob.'+name,hashlib.sha256(blob).hexdigest(),sha(name))
    source=bound(SOURCE+'/execution.json');sp=bound(source['protocol'],source['protocol_sha256']);sc=bound(source['claim'],source['claim_sha256'])
    d=bound(source['result'],source['result_sha256']);raw=bound(SOURCE+'/runtime/reconstruction_attempts.jsonl')
    attempts=jsonl(SOURCE+'/runtime/reconstruction_attempts.jsonl')
    a.eq('source.exact_execution',source['status'],'SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT');a.eq('source.exit0',source['returncode'],0)
    a.eq('source.schema',d['schema'],'P4_ABB_RRT_NR_END_TO_END_DRAFT_V1');a.eq('source.result_status',d['status'],'SOURCE_SOLVE_RETURNED_PENDING_INDEPENDENT_PATH_AUDIT')
    a.add('source.exact_nonapprox',d['exact']is True and d['approximate']is False and d['has_solution']is True)
    a.eq('source.single_solve',[source['solve_dispatched'],source['solve_calls_from_result'],d['solve_calls']],[1,1,1])
    a.eq('source.formal_zero',[source['formal_table_I_calls'],sp['formal_table_I_calls'],d['formal_table_I_calls']],[0,0,0])
    a.eq('source.VI_zero',[source['new_VI_candidate_constructions'],sp['new_VI_candidate_constructions']],[0,0])
    a.eq('source.protocol_frozen',sp['frozen'],True);a.add('source.protocol_reviews',bool(sp['reviews'])and all(v is True for v in sp['reviews'].values()))
    a.eq('source.claim_commit',sc['source_commit'],source['source_commit']);a.eq('source.claim_protocol',sc['protocol_sha256'],source['protocol_sha256'])
    a.eq('source.before_after_protocol',source['protocol_after_sha256'],source['protocol_sha256']);a.eq('source.before_after_claim',source['claim_after_sha256'],source['claim_sha256'])
    points=[bound(f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_{i}.json')for i in(0,1)]
    expected={'environment':'II','seed':7,'range_rad':2.6,'goal_bias':.05,'solve_seconds':10.,
        'start_q12':points[0]['selected_q_rad'],'goal_q12':points[1]['selected_q_rad'],
        'bounds_low_rad':[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2,
        'bounds_high_rad':[2.88,1.919,1.22,2.79,2.09,3.1416]*2}
    for i,point in enumerate(points):
        a.eq('source.A01_status'+str(i),point['status'],'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED');a.eq('source.A01_collision'+str(i),point['source_policy_collision_qualified'],True)
    for field,value in expected.items():
        for prefixname,owner in[('protocol',sp['request']),('execution',source['driver_request']),('driver_request',d['request'])]:
            a.eq('source.'+prefixname+'.'+field,owner[field],value)
            if field in('start_q12','goal_q12'):a.exactq('source.'+prefixname+'.'+field+'.binary64',owner[field],value)
        if field!='solve_seconds':a.eq('source.result_metadata.'+field,d[field],value)
    for field in('start_q12','goal_q12'):a.exactq('source.result_endpoint.'+field,d[field],expected[field])
    a.eq('source.full_JSONL_copy',attempts,d['reconstruction_attempts'])
    for i,(x,y)in enumerate(zip(attempts,d['reconstruction_attempts'])):
        for field in('qa12','qb12'):a.exactq('source.JSONL'+str(i)+'.'+field,x[field],y[field])
        a.eq('source.JSONL'+str(i)+'.all_Confs_bits',[qkey(q).hex()for q in x['path_q12']],[qkey(q).hex()for q in y['path_q12']])
    a.eq('source.observed_call_counts',[source['observation_prefix']['reconstruction_calls_completed_observed'],d['reconstruction_calls_completed_observed']],[len(attempts)]*2)
    a.eq('source.no_incomplete_observation_tail',source['observation_prefix']['reconstruction_incomplete_tails'],[])
    a.eq('source.own_before_after',source['own_source_sha256'],source['own_source_after_sha256']);a.eq('source.own_protocol',source['own_source_sha256'],sp['own_source_sha256'])
    a.eq('source.build_before_after',source['build_assets_before_sha256'],source['build_assets_after_sha256']);a.eq('source.build_protocol_assets',source['build_assets_before_sha256'],sp['build_assets']['files'])
    a.eq('source.A01_before_after',source['endpoint_sources_after_sha256'],sp['endpoint_sources_sha256'])
    for name,wanted in source['retained_run_files_sha256'].items():bound(name,wanted)
    build=bound(source['build_manifest'],source['build_manifest_sha256']);be=bound(build['engineering_execution'])
    a.eq('build.manifest_execution_commit',build['source_commit'],be['source_commit']);a.eq('build.manifest_hash',be['manifest_sha256'],sha(source['build_manifest']))
    a.eq('build.unqueried',[build['status'],be['status']],['BUILT_NOT_QUERIED']*2);a.eq('build.scope',[build['query_calls'],build['solve_calls']],[0,0])
    for name in('binary_sha256','binary'):a.eq('build.'+name,build[name],source[name])
    stage=Path(build['binary']).parent;bound(build['binary'],build['binary_sha256'])
    for field in('compiled_source_sha256','mesh_sha256'):
        for name,wanted in build[field].items():bound(stage/name,wanted)
    for name,wanted in build['template_assets_sha256'].items():bound(name,wanted)
    a.eq('build.template_before_after',build['template_assets_sha256'],build['template_assets_after_sha256'])
    for change in build['changes']:
        if 'preserved_original'in change:bound(stage/change['preserved_original'],change['preserved_original_sha256'])
    for field,hashfield in[('protocol','protocol_sha256'),('claim','claim_sha256')]:bound(build[field],build[hashfield])
    full=rebuild(d,a);queue=full['nodes']
    a.eq('queue.protocol_complete_rebuild',p['fixed_queue'],full);a.eq('queue.saved_complete_rebuild',bound(FOLDER/'full_fixed_queue.json'),full)
    a.eq('queue.saved_nodes',bound(FOLDER/'node_queue.json'),queue);a.eq('queue.hash',sha(FOLDER/'node_queue.json'),e['node_queue_sha256'])
    a.eq('queue.actual_size',len(queue),p['full_queue_node_count']);a.add('queue.under_resource_cap',0<len(queue)<=2048)
    a.eq('queue.all_source_structural',full['all_edges_structural_qualified'],True)
    manifest=bound(p['collision_manifest']);entries={r['variant']:r for r in manifest['entries']if r['model']=='abb'}
    worker_stdout=FOLDER/'00001_independent_full_node_queue.stdout.txt';worker_stderr=FOLDER/'00001_independent_full_node_queue.stderr.txt'
    bound(worker_stdout);bound(worker_stderr);responses=prefix(worker_stdout,'P4_NR_NODE_RESPONSE ');events=prefix(worker_stderr,'P4_NR_NODE_EVENT ')
    a.eq('worker.all_response_ids',[r['node_id']for r in responses],list(range(len(queue))))
    inputs=jsonl(FOLDER/'00001_independent_full_node_queue.input.txt');a.eq('worker.input_queue_hash',inputs[0]['node_queue_sha256'],e['node_queue_sha256'])
    start=bound(FOLDER/'node_worker_started.json');a.eq('worker.parent',start['parent_pid'],c['parent_pid']);a.eq('worker.start_protocol',start['protocol_sha256'],e['protocol_sha256']);a.eq('worker.start_queue',start['node_queue_sha256'],e['node_queue_sha256'])
    observed=Counter();maxpos=maxrot=maxleaf=0.;marginmin=float('inf');query_totals=Counter();posemax={v:{'position_mm':0.,'rotation':0.}for v in('native','aligned')};nodes_ok=0;native_collisions=0;node_summaries=[]
    for expected_node,response in zip(queue,responses):
        i=expected_node['node_id'];name='node.'+str(i);stem=FOLDER/f'node_{i:05d}';n=bound(str(stem)+'.json')
        a.eq(name+'.response_copy',response['result'],n);a.eq(name+'.source_identity',{k:n[k]for k in expected_node},expected_node);a.exactq(name+'.source_q_bits',n['q12'],expected_node['q12']);a.eq(name+'.complete',n['stage'],'COMPLETED')
        for arm in(1,2):a.eq(name+f'.arm{arm}_partial',bound(str(stem)+f'_arm{arm}.json'),{**expected_node,'poses':n['poses'][:arm],'stage':'STARTED'})
        a.eq(name+'.math_partial',bound(str(stem)+'_math.json'),{k:v for k,v in n.items()if k not in('stage','collision','node_qualified')}|{'stage':'MATH_COMPLETED'})
        a.add(name+'.pose_finite_shape',shape(n['poses'])==shape([[[0]*4 for _ in range(4)]]*2)and all(math.isfinite(v)for v in flatten(n['poses'])))
        for arm in(0,1):a.eq(name+f'.arm{arm}_homogeneous',n['poses'][arm][3],[0.,0.,0.,1.])
        grasp=[[1.,0.,0.,300.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]];flip=[[-1.,0.,0.,0.],[0.,-1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
        closed=mm(mm(n['poses'][0],grasp),flip);second=n['poses'][1]
        position=max(abs(second[r][3]-closed[r][3])for r in range(3));rotation=max(abs(second[r][col]-closed[r][col])for r in range(3)for col in range(3))
        maxpos=max(maxpos,position);maxrot=max(maxrot,rotation)
        a.near(name+'.closure_position',n['closure']['position_max_abs'],position,1e-10);a.near(name+'.closure_rotation',n['closure']['rotation_matrix_max_abs'],rotation,1e-14)
        violations=[];margins=[]
        for j,(q,(lo,hi))in enumerate(zip(n['q12'],DEG_LIMITS)):
            lo*=3.1416/180;hi*=3.1416/180;margins.append(min(q-lo,hi-q))
            if not lo<=q<=hi:violations.append({'index':j,'q_rad':q,'lower_rad':lo,'upper_rad':hi})
        marginmin=min(marginmin,min(margins));a.eq(name+'.source_limit_literal',n['limits']['source_literal_pi_preserved'],3.1416);a.eq(name+'.source_limit_violations',n['limits']['violations'],violations);a.eq(name+'.source_limit_legal',n['limits']['legal'],not violations);a.eq(name+'.no_planar_gate',n['limits']['planar_q19_policy'],None)
        math_ok=position<=1e-5 and rotation<=1e-5 and not violations;a.eq(name+'.math_qualified',n['math_qualified'],math_ok)
        collision=n['collision'];a.eq(name+'.collision_raw',bound(str(stem)+'_collision_raw.json'),collision)
        a.eq(name+'.collision_header',{k:collision[k]for k in('environment','status','scope','continuous_collision_certificate','selected_variant','manifest_path','manifest_sha256')},
            {'environment':'II','status':'CHECKED','scope':'AUTHOR_DISCRETE_COLLISION_POLICY','continuous_collision_certificate':False,'selected_variant':'aligned','manifest_path':p['collision_manifest'],'manifest_sha256':sha(p['collision_manifest'])})
        a.eq(name+'.collision_variant_order',list(collision['variants']),['native','aligned'])
        for variant,row in collision['variants'].items():
            cn=name+'.'+variant;entry=entries[variant]
            a.eq(cn+'.command',row['source_command'],[entry['binary'],'II']);a.eq(cn+'.provenance',row['provenance'],{k:entry[k]for k in row['provenance']})
            raws=[json.loads(s[len('P4_COLLISION_RESULT '):])for s in row['source_stdout'].splitlines()if s.startswith('P4_COLLISION_RESULT ')]
            a.eq(cn+'.one_raw_response',len(raws),1);a.eq(cn+'.raw_copy',raws[0],{k:row[k]for k in('native_result','cpu_s','poses','query_codes')})
            a.add(cn+'.native_result_bool_domain',type(row['native_result'])is int and row['native_result']in(0,1));a.eq(cn+'.native_collision',row['native_collision'],bool(row['native_result']))
            if variant=='native':native_collisions+=int(row['native_collision'])
            codes=row['query_codes'];a.add(cn+'.nonempty_all_integer_zero_PQP',bool(codes)and all(type(v)is int and v==0 for v in codes));a.eq(cn+'.query_errors',row['query_error_codes'],[]);query_totals[variant]+=len(codes)
            pc=row['pose_consistency'];a.eq(cn+'.pose_gate',[pc['position_gate_mm'],pc['rotation_matrix_gate']],[1e-5,1e-5]);a.eq(cn+'.pose_arm_order',[r['arm']for r in pc['errors']],[1,2]);ok=True
            for arm,detail in enumerate(pc['errors']):
                tcp=[row['poses'][arm][j:j+4]for j in(0,4,8)];independent=n['poses'][arm][:3]
                a.eq(cn+f'.arm{arm}_captured',detail['collision_TCP'],tcp);a.eq(cn+f'.arm{arm}_independent',detail['independent_TCP'],independent)
                pe=max(abs(tcp[r][3]-independent[r][3])for r in range(3));re=max(abs(tcp[r][col]-independent[r][col])for r in range(3)for col in range(3))
                a.near(cn+f'.arm{arm}_position_error',detail['translation_maxabs_mm'],pe,1e-12);a.near(cn+f'.arm{arm}_rotation_error',detail['rotation_maxabs'],re,1e-15)
                posemax[variant]['position_mm']=max(posemax[variant]['position_mm'],pe);posemax[variant]['rotation']=max(posemax[variant]['rotation'],re);ok&=pe<=1e-5 and re<=1e-5
            a.eq(cn+'.pose_pass',pc['passed'],ok);a.eq(cn+'.pose_status',pc['status'],'PASS'if ok else'COLLISION_PHYSICAL_TCP_MISMATCH')
            if variant=='aligned':a.eq(cn+'.aligned_pass_required',ok,True)
        preferred=collision['variants']['aligned'];a.eq(name+'.selected_collision',collision['collision'],preferred['native_collision'])
        for field in('source_command','source_stdout','source_stderr'):a.eq(name+'.selected_'+field,collision[field],preferred[field])
        node_ok=math_ok and collision['collision']is False;a.eq(name+'.node_qualified_arithmetic',n['node_qualified'],node_ok);a.eq(name+'.node_must_qualify',node_ok,True);nodes_ok+=int(node_ok)
        local_events=[ev for ev in events if ev.get('node_id')==i];expected_events=[]
        for arm in(1,2):
            for kind in('math_arm_FK_started','math_arm_FK_completed'):expected_events.append((kind,arm))
        expected_events.append(('collision_started',None))
        for variant in('native','aligned'):
            for arm in(1,2):
                for kind in('adapter_arm_FK_J_started','adapter_arm_FK_J_completed'):expected_events.append((kind,arm))
        expected_events.append(('collision_completed',None))
        a.eq(name+'.actual_event_order',[(ev['event'],ev.get('arm'))for ev in local_events],expected_events)
        for ev in local_events:
            kind=ev['event'];observed['collision_calls_'+kind.split('_')[-1]if kind in('collision_started','collision_completed')else kind]+=1
            if'environment'in ev:a.eq(name+'.event_env',ev['environment'],'II')
        final=local_events[-1];qc={variant:len(row['query_codes'])for variant,row in collision['variants'].items()}
        a.eq(name+'.collision_event_query_counts',final['variant_query_counts'],qc);a.eq(name+'.collision_event_query_total',final['PQP_queries'],sum(qc.values()));a.eq(name+'.collision_event_status',final['status'],collision['status']);observed['PQP_queries']+=sum(qc.values())
        a.eq(name+'.worker_running_counts',response['observed_counts'],dict(observed))
        node_summaries.append({'node_id':i,'position_maxabs_mm':position,'rotation_matrix_maxabs':rotation,'minimum_limit_margin_rad':min(margins),'qualified':node_ok})
    expected_counts=dict(observed)
    for ev in events:
        if ev['event']in('math_arm_FK_started','math_arm_FK_completed','adapter_arm_FK_J_started','adapter_arm_FK_J_completed','collision_started','collision_completed'):
            key='actual_'+ev['event'];expected_counts[key]=expected_counts.get(key,0)+1
        if ev['event']=='collision_completed':
            expected_counts['actual_adapter_PQP_queries']=expected_counts.get('actual_adapter_PQP_queries',0)+ev['PQP_queries']
            for variant,n in ev['variant_query_counts'].items():
                key='actual_adapter_'+variant+'_PQP_queries';expected_counts[key]=expected_counts.get(key,0)+n
    expected_counts['actual_node_responses_retained']=len(responses);a.eq('counts.exact_actual_events',e['counts'],expected_counts)
    a.eq('counts.math2pernode',[observed['math_arm_FK_started'],observed['math_arm_FK_completed']],[2*len(queue)]*2)
    a.eq('counts.collision1pernode',[observed['collision_calls_started'],observed['collision_calls_completed']],[len(queue)]*2)
    a.eq('counts.adapter4pernode',[observed['adapter_arm_FK_J_started'],observed['adapter_arm_FK_J_completed']],[4*len(queue)]*2)
    inv=bound(FOLDER/'raw_prefix_inventory.json');a.eq('counts.raw_inventory',inv,{'node_responses':responses,'worker_events':events,'actual_observed_only':True})
    process_events=jsonl(FOLDER/'events.jsonl');a.eq('process.event_types',[r['event']for r in process_events],['process_started','process_finished'])
    begin,end=process_events;a.eq('process.same_label',begin['label'],end['label']);a.eq('process.exit0',end['exit_code'],0)
    a.eq('process.stdout_hash',end['stdout_sha256'],sha(worker_stdout));a.eq('process.stderr_hash',end['stderr_sha256'],sha(worker_stderr))
    a.eq('process.command',begin['command'],[begin['command'][0],str(ROOT/'scripts/qualify_p4_full_r2_abb_rrt_nr_path_draft.py'),'--node-worker',str(path(e['protocol']))])
    a.eq('tail.completed_all_ids',e['completed_node_ids'],list(range(len(queue))));a.eq('tail.uncompleted_ids',e['uncompleted_node_ids'],[])
    a.eq('tail.full_count',e['full_node_queue_count'],len(queue));a.eq('tail.all_checked',e['full_node_queue_checked'],True);a.eq('tail.diagnostics',e['diagnostics'],[])
    a.eq('tail.no_partial_stop_files',sorted(v.name for v in FOLDER.glob('*stopped*')),[])
    a.eq('tail.zero_extra_calls',e['zero_calls'],{'solve':0,'NR':0,'IK':0,'projection':0,'RBS':0,'RNG':0,'VI_constructions':0,'formal_table_I':0})
    a.eq('tail.discrete_only',e['continuous_collision_certificate'],False)
    a.eq('budget.protocol',e['budget'],p['budget']);a.eq('budget.fixed_caps',[p['budget']['wall_s'],p['budget']['cpu_s']],[120.,240.])
    a.eq('budget.prior_paths',e['prior_executions'],p['prior_executions']);priors=[load(name)for name in e['prior_executions']]
    for axis in('wall_s','cpu_s'):
        prior=math.fsum(r[axis]for r in priors);a.eq('budget.prior_'+axis,e['previous_r2_'+axis],prior);a.eq('budget.protocol_prior_'+axis,p['previous_r2_'+axis],prior)
        a.add('budget.own_'+axis,0<=e[axis]<p['budget'][axis],used=e[axis],cap=p['budget'][axis]);a.add('budget.cumulative_'+axis,prior+e[axis]<p['budget']['r2_total_'+axis],used=prior+e[axis],cap=p['budget']['r2_total_'+axis])
    a.add('budget.timestamp_order',datetime.fromisoformat(e['ended_at_utc'])>datetime.fromisoformat(e['started_at_utc']))
    independently_qualified=full['all_edges_structural_qualified']and len(responses)==len(queue)==nodes_ok and not a.failed
    a.eq('conclusion.source_path_status',e['status'],'PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH')
    for edge in full['edges']:maxleaf=max(maxleaf,max(edge['leaf_distances_rad'],default=0.))
    result={'milestones':len(d['milestones_q12']),'original_reconstruction_calls':len(attempts),
        'full_unique_nodes':len(queue),'qualified_nodes':nodes_ok,'edges':len(full['edges']),
        'dense_leaf_occurrences':sum(len(edge['leaf_distances_rad'])for edge in full['edges']),
        'max_leaf_full12_L2_rad':maxleaf,'max_closure_position_mm':maxpos,'max_closure_rotation_matrix':maxrot,
        'minimum_mechanical_limit_margin_rad':marginmin,'native_collision_count':native_collisions,
        'pose_error_maxima':posemax,'adapter_PQP_queries_by_variant':dict(query_totals),
        'actual_counts':expected_counts,'wall_s':e['wall_s'],'cpu_s':e['cpu_s'],
        'prior_execution_count':len(priors),'cumulative_r2_wall_s':e['previous_r2_wall_s']+e['wall_s'],
        'cumulative_r2_cpu_s':e['previous_r2_cpu_s']+e['cpu_s']}
    return{'schema':'P4_R2_ABB_RRT_NR_PATH_COMPACT_SAVED_POST_V1','created_at_utc':datetime.now(timezone.utc).isoformat(),
        'run_id':RUN,'status':'PASS_SAVED_EVIDENCE_POST'if not a.failed else'FAIL_SAVED_EVIDENCE_POST',
        'independently_derived_path_qualified':independently_qualified and not a.failed,
        'scientific_scope':'Original discrete source-policy NR start-to-goal path only; reconstructed A01 endpoints and physical NR numerical seam.',
        'audit_author_also_wrote_path_runner':True,'personnel_independent':False,
        'independence_scope':'Separately implemented stdlib parsing/binary64 queue/tree/ref reconstruction and arithmetic on saved poses/limits/collision captures; root and second agent independently review.',
        'audit_scientific_calls':{'solve':0,'NR':0,'FK':0,'Jacobian':0,'IK':0,'PQP':0,'RNG':0,'compile':0},
        'audit_script_sha256':sha(__file__),'source_commit':e['source_commit'],'input_artifacts_sha256':artifacts,
        'checks_total':a.total,'checks_passed':a.passed,'checks_failed':len(a.failed),
        'check_counts_by_category':dict(a.categories),'failed_counts_by_category':dict(a.failed_categories),
        'failed_checks':a.failed,'result':result,
        'edge_summaries':[{'edge_index':edge['edge_index'],'source_returned':edge['source_returned'],
            'path_node_occurrences':len(edge['node_ids']),'leaf_occurrences':len(edge['leaf_distances_rad']),
            'max_leaf_full12_L2_rad':max(edge['leaf_distances_rad'],default=0.),'binary64_endpoints_exact':edge['dense_first_last_binary64_exact'],
            'structural_qualified':edge['structural_qualified']}for edge in full['edges']],
        'node_summaries':node_summaries,
        'retained_historical_local_POST_sha256':{str(name.relative_to(ROOT)):sha(name)for name in PRESERVED_REPORTS if name.is_file()},
        'limitations':['No planner/performance/statistical/full P4 qualification beyond this saved discrete path.',
            'No native KDL equivalence, continuous collision, full solid rod surface, or omitted-pair certificate.',
            'Native TCP mismatch and native collision result retained separately; only aligned v3 qualified for physical TCP.',
            'The legacy math_arm_FK event performs FK/J; does not assert zero Jacobian evaluations.',
            'Passing checks are aggregated; all failures kept. Large arrays remain in hash-bound original scientific evidence.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--inspect-only',action='store_true');args=parser.parse_args()
    if not args.inspect_only:
        for suffix in('.json','.md'):
            if Path(str(REPORT)+suffix).exists():raise SystemExit('EXCLUSIVE_REPORT_EXISTS '+str(REPORT)+suffix)
    r=audit();print(json.dumps({k:r[k]for k in('status','checks_total','checks_passed','checks_failed','independently_derived_path_qualified','result')},ensure_ascii=False))
    if r['failed_checks']:print(json.dumps(r['failed_checks'][:20],ensure_ascii=False))
    if args.inspect_only:return
    with Path(str(REPORT)+'.json').open('x')as f:json.dump(r,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    s=r['result'];md=f'''# P4 R2 ABB 原 RRT_NR 完整保存路径独立算术 POST

审查日期 {datetime.now(timezone(timedelta(hours=8))).date().isoformat()}（Asia/Shanghai）；状态 `{r['status']}`，{r['checks_passed']}/{r['checks_total']} 检查通过，失败 {r['checks_failed']}。独立保存算术得出路径合格 `{r['independently_derived_path_qualified']}`。本审查作者也编写 path runner，人员独立=false；需 root 与另一代理独立复核。仅 stdlib 解析、Git blob读取、文件hash与保存数组矩阵算术，0 新模型、FK/J、NR、IK、PQP、RBS、RNG、solve或编译。

原 source E2E01 的 exact 非approx 结果历史保持 PENDING；本项单独后审。{s['milestones']} 个原里程点、{s['original_reconstruction_calls']} 次原 state-level reconstruct 原返回 true，完整 qa/qb 与首末 Confs binary64 一致，原有向 tree 包含完整起终点序列。按全12角字节独立重建队列、每个ref与碰撞义务，{s['qualified_nodes']}/{s['full_unique_nodes']} 唯一节点通过，无抽稀、无未知尾部。

闭链最大位置 {s['max_closure_position_mm']:.17g} mm，旋转矩阵 {s['max_closure_rotation_matrix']:.17g}，原门均1e-5；原 degrees×3.1416/180 机械界最小余量 {s['minimum_mechanical_limit_margin_rad']:.17g} rad。{s['dense_leaf_occurrences']} 个原全12角叶最远 {s['max_leaf_full12_L2_rad']:.17g} rad，严格<.05；不加PCS固定主动链或解析分支门，不wrap/lift/重投影。

| 原边 | 原路径节点数 | 叶数 | 最大full12叶L2(rad) | 原返回/精确首末 |
|---|---:|---:|---:|---|
'''
    for row in r['edge_summaries']:md+=f"| {row['edge_index']} | {row['path_node_occurrences']} | {row['leaf_occurrences']} | {row['max_leaf_full12_L2_rad']:.17g} | {row['source_returned']}/{row['binary64_endpoints_exact']} |\n"
    md+=f'''
逐节点完整 native/aligned 原PQP响应、实际querycodes、TCP/独立pose、worker事件和累计计数均交叉核对。adapter PQP native/aligned `{json.dumps(s['adapter_PQP_queries_by_variant'])}`，实际数学臂FK/J {s['actual_counts'].get('math_arm_FK_completed',0)}、碰撞 {s['actual_counts'].get('collision_calls_completed',0)}、adapter内部臂FK/J {s['actual_counts'].get('adapter_arm_FK_J_completed',0)}；未以上限冒充实测。native TCP最大差 {s['pose_error_maxima']['native']['position_mm']:.17g} mm / {s['pose_error_maxima']['native']['rotation']:.17g}，其原失败单列；aligned {s['pose_error_maxima']['aligned']['position_mm']:.17g} mm / {s['pose_error_maxima']['aligned']['rotation']:.17g}。

本次自有wall {s['wall_s']:.17g}s /CPU {s['cpu_s']:.17g}s；之前{s['prior_execution_count']}份自有execution按fsum重算，R2累计 {s['cumulative_r2_wall_s']:.17g} wall / {s['cumulative_r2_cpu_s']:.17g} CPU。协议、claim、源码提交blob、build manifest/binary/源和mesh、完整日志/队列hash、前后保全和全部实际计数见同名紧凑JSON。每个失败完整保留；重复大数组只引用原始证据hash。

仅原离散碰撞策略的空间NR起终点路径资格；A01端点与数值接缝属于RECONSTRUCTED，不是作者原输入/KDL直接通过。保留8mm容差、原pair与共线杆三角形，不证明CCD、实体杆表面、省略pair安全、方法速度/成功率、PCS优势或全文复现。211义务、Table I0/22500及其他原文规模均保持，不P2/Isaac。

审查脚本 SHA256 `{r['audit_script_sha256']}`。
'''
    if r['failed_checks']:md+='\n失败详见同名JSON failed_checks；本报告不据失败项升级路径资格。\n'
    with Path(str(REPORT)+'.md').open('x')as f:f.write(md)

if __name__=='__main__':main()
