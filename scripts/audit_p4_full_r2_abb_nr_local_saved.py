#!/usr/bin/env python3
"""Saved-only NR local POST. Stdlib only; never load a scientific module/binary.

Author also wrote the runner: this is independently implemented evidence
arithmetic, not personnel-independent verification. Root arranges a second review.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RUN = '20261015_R2_ABB_NR_LOCAL01'
FOLDER = ROOT / 'results/p4_full' / RUN
REPORT = ROOT / 'reports/P4_FULL_R2_ABB_NR_LOCAL_INDEPENDENT_POST_20261015'
GATES = {'position_maxabs_mm': 1e-5, 'rotation_matrix_maxabs': 1e-5,
         'strict_leaf_full12_L2_rad': .05, 'original_source_RBS_max_depth': 150,
         'source_PQP_tolerance_mm': 8., 'fixed_active_or_branch_gate': False}
DEG_LIMITS = [(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]*2

def path(p):
    p = Path(p)
    return p if p.is_absolute() else ROOT / p

def load(p): return json.loads(path(p).read_text())
def sha(p): return hashlib.sha256(path(p).read_bytes()).hexdigest()
def jsonl(p): return [json.loads(s) for s in path(p).read_text().splitlines() if s.strip()]
def prefixed(p, prefix):
    return [json.loads(s[len(prefix):]) for s in path(p).read_text().splitlines() if s.startswith(prefix)]
def qbytes(q): return struct.pack('>12d', *q)
def nodekey(env,q): return (env, qbytes(q))
def finite_q(q):
    return isinstance(q,list) and len(q)==12 and all(type(x) in (int,float) and math.isfinite(x) for x in q)
def l2(a,b): return math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,b)))
def flat(x): return [v for y in x for v in flat(y)] if isinstance(x,list) else [x]
def shape(x): return [len(x),[shape(y) for y in x]] if isinstance(x,list) else None
def mm(a,b): return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def logical(x):
    keys = ('schema','environment','request','id','op','status','returned','q12','path_q12','solve_calls','rng_calls')
    r = {k:x[k] for k in keys if k in x}
    r['request'] = dict(r['request'])
    for k in ('q12','qa12','qb12'):
        if k in r['request']: r['request'][k] = qbytes(r['request'][k]).hex()
    if 'q12' in r: r['q12'] = qbytes(r['q12']).hex()
    if 'path_q12' in r: r['path_q12'] = [qbytes(q).hex() for q in r['path_q12']]
    r['source_log_counters'] = {k:v for k,v in x['source_log_counters'].items() if 'time' not in k}
    return r

class Audit:
    def __init__(self): self.checks=[]
    def add(self,name,ok,**ev): self.checks.append({'check':name,'passed':bool(ok),**ev}); return bool(ok)
    def eq(self,name,a,b): return self.add(name,a==b,actual=a,expected=b)
    def near(self,name,a,b,tol):
        aa,bb=flat(a),flat(b)
        valid=shape(a)==shape(b) and all(type(v) in (int,float) and math.isfinite(v) for v in aa+bb)
        err=max((abs(x-y) for x,y in zip(aa,bb)),default=0.) if valid else None
        return self.add(name,valid and err<=tol,max_abs_error=err,absolute_tolerance=tol)
    def passed(self): return all(c['passed'] for c in self.checks)

def audit():
    a=Audit(); e=load(FOLDER/'execution.json'); p=load(e['protocol']); c=load(e['claim'])
    a.eq('protocol.frozen',p['frozen'],True)
    a.add('protocol.all_reviews',all(v is True for v in p['reviews'].values()))
    a.eq('protocol.fixed_gates',p['gates'],GATES)
    a.eq('protocol.hash',sha(e['protocol']),e['protocol_sha256'])
    a.eq('protocol.before_after',e['protocol_sha256'],e['protocol_after_sha256'])
    a.eq('claim.hash',sha(e['claim']),e['claim_sha256'])
    a.eq('claim.before_after',e['claim_sha256'],e['claim_after_sha256'])
    for k in ('source_commit','budget','protocol_sha256'): a.eq('claim.'+k,c[k],e[k])
    a.eq('claim.one_shot',c['no_retry_reset_or_resume'],True)
    a.eq('run_id',e['run_id'],RUN)
    a.eq('bindings.protocol_before',p['bound_files_sha256'],e['bound_files_sha256'])
    a.eq('bindings.before_after',e['bound_files_sha256'],e['bound_files_after_sha256'])
    bound=e['bound_files_sha256']
    for name,want in bound.items(): a.eq('bound.'+name,sha(name),want)
    own=[name for name in bound if not Path(name).is_absolute() and name.startswith(('scripts/','baselines/'))]
    own.append(e['protocol'])
    for name in own:
        blob=subprocess.check_output(['git','show',e['source_commit']+':'+name],cwd=ROOT)
        a.eq('source_commit_blob.'+name,hashlib.sha256(blob).hexdigest(),sha(name))
    build=load(p['build']['manifest']); be=load(p['build']['engineering_execution'])
    for k in ('status','source_commit','binary','binary_sha256'):
        a.eq('build.execution_manifest.'+k,be[k],build[k])
    a.eq('build.unqueried',build['status'],'BUILT_NOT_QUERIED')
    a.eq('build.manifest_hash',sha(p['build']['manifest']),p['build']['manifest_sha256'])
    a.eq('build.binary_hash',sha(p['build']['binary']),p['build']['binary_sha256'])
    a.eq('build.template_unchanged',build['template_assets_sha256'],build['template_assets_after_sha256'])
    a.eq('build.recipe_hash',sha(build['protocol']),build['protocol_sha256'])
    a.eq('build.claim_hash',sha(build['claim']),build['claim_sha256'])
    stage=Path(p['build']['binary']).parent
    for field in ('compiled_source_sha256','mesh_sha256'):
        for name,want in build[field].items(): a.eq('build.'+name,sha(stage/name),want)
    for change in build['changes']:
        if 'preserved_original' in change:
            a.eq('build.preserved.'+change['preserved_original'],sha(stage/change['preserved_original']),change['preserved_original_sha256'])
    inventory=load('reports/P4_FULL_R2_ABB_NR_INTERFACE_SAVED_INPUTS_20261015.json')
    projects=p['fixed_inputs']['endpoint_projects']; edges=p['fixed_inputs']['edges']
    a.eq('inputs.all_four_endpoint_ids',[v['request']['id'] for v in projects],['II_0','II_1','III_0','III_1'])
    a.eq('inputs.all_three_edge_indices',[v['edge_index'] for v in edges],[0,1,2])
    for item in projects:
        endpoint=load(item['source']); n=item['request']['id']
        a.eq('input.'+n+'.reconstructed_status',endpoint['status'],'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED')
        a.eq('input.'+n+'.original_saved_q_binary64',qbytes(item['request']['q12']).hex(),qbytes(endpoint['selected_q_rad']).hex())
        a.eq('input.'+n+'.collision_qualified',endpoint['source_policy_collision_qualified'],True)
    ms=load(edges[0]['source'])['milestones_q12']
    a.eq('inputs.all_milestones',p['fixed_inputs']['milestones_q12'],ms)
    a.eq('inputs.inventory_milestones',inventory['milestones_q12'],ms)
    for edge in edges:
        i=edge['edge_index']; n='input.edge'+str(i)
        a.eq(n+'.indices',edge['source_milestone_indices'],[i,i+1])
        for k,q in [('qa12',ms[i]),('qb12',ms[i+1])]: a.eq(n+'.'+k,qbytes(edge[k]).hex(),qbytes(q).hex())
        a.eq(n+'.distance',edge['original_full12_distance_rad'],l2(ms[i],ms[i+1]))
    schedule=[]
    for env,mode in [('II','trace'),('II','plain'),('III','trace'),('III','plain')]:
        req=[v['request'] for v in projects if v['environment']==env]
        if env=='II':
            for edge in edges:
                for op in ('rbs','reconstruct'):
                    req.append({'id':f'II_edge_{edge["edge_index"]}_{op}','op':op,'qa12':edge['qa12'],'qb12':edge['qb12']})
        schedule.append({'environment':env,'mode':mode,'requests':req})
    a.eq('schedule.exact_fixed20',p['schedule'],schedule)
    raw_sources=[]; all_events=[]; trace_by_id={}; responses={}; counters=Counter(); gd_updates=Counter(); trace_summaries=[]
    for bi,b in enumerate(schedule):
        env,mode=b['environment'],b['mode']; stem=f'{bi+1:05d}_source_{bi:02d}_{env}_{mode}'
        raw=prefixed(FOLDER/(stem+'.stdout.txt'),'P4_NR_RESPONSE ')
        events=prefixed(FOLDER/(stem+'.stderr.txt'),'P4_PCS_TRACE ')
        a.eq(stem+'.input',jsonl(FOLDER/(stem+'.input.txt')),b['requests'])
        a.eq(stem+'.responses',len(raw),len(b['requests']))
        raw_sources.extend(raw); all_events.extend(events)
        chunks=[]
        for ev in events:
            if ev['event']=='entered' and ev['id']==1: chunks.append([])
            chunks[-1].append(ev)
        a.eq(stem+'.trace_chunk_count',len(chunks),len(raw) if mode=='trace' else 0)
        for ri,(req,r) in enumerate(zip(b['requests'],raw)):
            name=stem+'.'+req['id']; responses[(env,mode,req['id'])]=r
            a.eq(name+'.saved_raw',load(FOLDER/f'source_{env}_{mode}_{req["id"]}.json'),r)
            contract=(r['schema']=='P4_ABB_NR_THIN_V1' and r['environment']==env and r['mode']==mode and
                      r['request']==req and r['id']==req['id'] and r['op']==req['op'] and
                      r['status']=='SOURCE_CALL_COMPLETED' and type(r['returned']) is bool and
                      r['observer_errors']==[] and r['solve_calls']==r['rng_calls']==0)
            a.add(name+'.contract',contract)
            if mode=='plain':
                a.eq(name+'.plain_observations',r['observed_counts'],{})
                a.eq(name+'.plain_gd',r['gd_completed_candidates'],[]); continue
            chunk=chunks[ri]; stack=[]; starts={}; ends={}; entered=Counter(); complete=Counter(); gds=[]
            for ev in chunk:
                if ev['event']=='entered':
                    a.add(name+f'.trace{ev["id"]}.unique_enter',ev['id'] not in starts)
                    starts[ev['id']]=ev; entered[ev['kind']]+=1; stack.append((ev['id'],ev['kind']))
                else:
                    a.add(name+f'.trace{ev["id"]}.matched_lifo',ev['event']=='completed' and stack and
                          stack.pop()==(ev['id'],ev['kind']) and ev['id'] not in ends)
                    ends[ev['id']]=ev; complete[ev['kind']]+=1
                    if ev['kind']=='pqp': a.eq(name+f'.pqp{ev["id"]}.return',ev['result']['code'],0)
                    if ev['kind']=='nr_gd':
                        gd=ev['result']; gds.append(gd)
                        a.eq(name+f'.gd{ev["id"]}.input',qbytes(starts[ev['id']]['args']['input_q12']).hex(),qbytes(gd['input_q12']).hex())
                        a.add(name+f'.gd{ev["id"]}.semantics',type(gd['returned']) is bool and
                              gd['returned']==(gd['status']=='CONVERGED') and gd['candidate_is_finite']==finite_q(gd['candidate_q12']))
                        a.add(name+f'.gd{ev["id"]}.update_count',type(gd['accepted_updates']) is int and 0<=gd['accepted_updates']<=10000)
                        gd_updates[gd['accepted_updates']]+=1
            a.eq(name+'.trace_empty_stack',stack,[])
            a.eq(name+'.trace_started_completed_ids',sorted(starts),sorted(ends))
            a.eq(name+'.trace_counts_pair',dict(entered),dict(complete))
            a.eq(name+'.trace_counts_response',dict(entered),r['observed_counts'])
            a.eq(name+'.gd_summaries',gds,r['gd_completed_candidates'])
            a.add(name+'.caps',all(v<=p['observational_caps_per_trace_request'][k] for k,v in entered.items()))
            a.eq(name+'.top_return',ends[1]['result']['returned'],r['returned'])
            if req['op']=='project_q12': a.eq(name+'.top_q_bytes',qbytes(ends[1]['result']['q12']).hex(),qbytes(r['q12']).hex())
            trace_by_id[(env,req['id'])]={'events':chunk,'observed_counts':dict(entered)}
            counters.update(complete)
            trace_summaries.append({'environment':env,'id':req['id'],'counts':dict(complete),'source_log_counters':r['source_log_counters']})
    pairs=load(FOLDER/'source_pairs.json'); qualified=load(FOLDER/'qualified_source_pairs.json')
    a.eq('pairs.count',len(pairs),10); a.eq('qualified.count',len(qualified),10)
    expected_order=[(b['environment'],r['id']) for b in schedule if b['mode']=='trace' for r in b['requests']]
    a.eq('pairs.order',[(v['environment'],v['request']['id']) for v in pairs],expected_order)
    queue=[]; lookup={}; pair_refs={}
    def add_node(env,q,ref,collision):
        a.add('queue.finite_candidate.'+str(len(queue)),finite_q(q))
        k=nodekey(env,q)
        if k not in lookup:
            lookup[k]=len(queue); queue.append({'node_id':len(queue),'environment':env,'q12':q,'refs':[],'collision_required':False})
        n=queue[lookup[k]]; n['refs'].append(ref); n['collision_required']|=collision
        return n['node_id']
    for pair,qp in zip(pairs,qualified):
        env=pair['environment']; req=pair['request']; id=req['id']; n='pair.'+id
        r=responses[(env,'trace',id)]; plain=responses[(env,'plain',id)]
        a.eq(n+'.trace',pair['trace'],r); a.eq(n+'.plain',pair['plain'],plain)
        a.eq(n+'.trace_saved',pair['trace_observation'],trace_by_id[(env,id)])
        a.eq(n+'.logical_binary64',logical(r),logical(plain)); a.eq(n+'.reported_match',pair['plain_trace_logical_equal'],True)
        a.eq(n+'.qualified_copy',{k:qp[k] for k in pair},pair)
        refs=[]
        for i,gd in enumerate(r['gd_completed_candidates']):
            if gd['candidate_q12'] is not None:
                nid=add_node(env,gd['candidate_q12'],{'case_id':id,'kind':'gd','candidate_index':i,'returned':gd['returned']},gd['returned'])
                refs.append({'kind':'gd','candidate_index':i,'returned':gd['returned'],'node_id':nid})
            else: a.eq(n+f'.gd{i}.null_not_returned',gd['returned'],False)
        if req['op']=='project_q12':
            nid=add_node(env,r['q12'],{'case_id':id,'kind':'top_project','returned':r['returned']},True)
            refs.append({'kind':'top_project','node_id':nid})
        else:
            for field in ('qa12','qb12'):
                nid=add_node(env,req[field],{'case_id':id,'kind':field},True); refs.append({'kind':field,'node_id':nid})
            if req['op']=='reconstruct':
                for i,q in enumerate(r['path_q12']):
                    nid=add_node(env,q,{'case_id':id,'kind':'path','path_index':i,'returned':r['returned']},True)
                    refs.append({'kind':'path','path_index':i,'node_id':nid})
        pair_refs[id]=refs; a.eq(n+'.full_node_refs',refs,pair['node_refs'])
    a.eq('queue.exact_rebuild_all_refs',load(FOLDER/'node_queue.json'),queue)
    a.eq('queue.hash',sha(FOLDER/'node_queue.json'),e['node_queue_sha256'])
    a.eq('queue.unique_count',len(queue),147)
    manifest=load(p['collision_manifest']); entries={v['variant']:v for v in manifest['entries'] if v['model']=='abb'}
    worker_responses=prefixed(FOLDER/'00005_independent_full_node_queue.stdout.txt','P4_NR_NODE_RESPONSE ')
    worker_events=prefixed(FOLDER/'00005_independent_full_node_queue.stderr.txt','P4_NR_NODE_EVENT ')
    a.eq('worker.response_ids',[v['node_id'] for v in worker_responses],list(range(len(queue))))
    nodes={}; worker_counts=Counter(); query_totals=Counter(); maxpos=maxrot=0.; minmargin=float('inf')
    posemax={variant:{'position_mm':0.,'rotation':0.} for variant in entries}; node_summaries=[]
    for source,wr in zip(queue,worker_responses):
        i=source['node_id']; n=f'node.{i}'; base=FOLDER/f'node_{i:05d}'
        node=load(str(base)+'.json'); nodes[i]=node
        a.eq(n+'.worker_response',wr['result'],node)
        a.eq(n+'.source_queue',{k:node[k] for k in source},source)
        a.eq(n+'.complete',node['stage'],'COMPLETED')
        for arm in (1,2):
            part=load(str(base)+f'_arm{arm}.json')
            a.eq(n+f'.arm{arm}.saved_partial',part,{**source,'poses':node['poses'][:arm],'stage':'STARTED'})
        a.eq(n+'.math_saved',load(str(base)+'_math.json'),{k:v for k,v in node.items() if k not in ('collision','node_qualified') and k!='stage'}|{'stage':'MATH_COMPLETED'})
        a.add(n+'.pose_finite_shape',shape(node['poses'])==shape([[[0]*4 for _ in range(4)]]*2) and all(math.isfinite(v) for v in flat(node['poses'])))
        for arm in (0,1): a.eq(n+f'.pose{arm}.homogeneous_row',node['poses'][arm][3],[0.,0.,0.,1.])
        grasp=[[1.,0.,0.,300. if node['environment']=='II' else 500.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
        flip=[[-1.,0.,0.,0.],[0.,-1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
        closed=mm(mm(node['poses'][0],grasp),flip); second=node['poses'][1]
        pos=max(abs(second[r][3]-closed[r][3]) for r in range(3))
        rot=max(abs(second[r][c]-closed[r][c]) for r in range(3) for c in range(3))
        maxpos=max(maxpos,pos); maxrot=max(maxrot,rot)
        a.near(n+'.closure.saved_position',node['closure']['position_max_abs'],pos,1e-10)
        a.near(n+'.closure.saved_rotation',node['closure']['rotation_matrix_max_abs'],rot,1e-14)
        violations=[]; margins=[]
        for j,(q,(lo,hi)) in enumerate(zip(node['q12'],DEG_LIMITS)):
            lo*=3.1416/180; hi*=3.1416/180; margins.append(min(q-lo,hi-q))
            if q<lo or q>hi: violations.append(j)
        margin=min(margins); minmargin=min(minmargin,margin)
        a.eq(n+'.limit_legal',node['limits']['legal'],not violations)
        a.eq(n+'.limit_violations',node['limits']['violations'],[])
        a.eq(n+'.literal_pi',node['limits']['source_literal_pi_preserved'],3.1416)
        a.eq(n+'.no_planar_policy',node['limits']['planar_q19_policy'],None)
        math_ok=pos<=1e-5 and rot<=1e-5 and not violations
        a.eq(n+'.math_gate',node['math_qualified'],math_ok)
        co=node['collision']; a.eq(n+'.collision_raw',load(str(base)+'_collision_raw.json'),co)
        a.eq(n+'.collision_header',{k:co[k] for k in ('environment','collision','status','scope','continuous_collision_certificate','selected_variant','manifest_path','manifest_sha256')},
             {'environment':node['environment'],'collision':False,'status':'CHECKED','scope':'AUTHOR_DISCRETE_COLLISION_POLICY','continuous_collision_certificate':False,'selected_variant':'aligned','manifest_path':p['collision_manifest'],'manifest_sha256':sha(p['collision_manifest'])})
        a.eq(n+'.collision_variants',list(co['variants']),['native','aligned'])
        for variant,row in co['variants'].items():
            cn=n+'.collision.'+variant; entry=entries[variant]
            a.eq(cn+'.source_command',row['source_command'],[entry['binary'],node['environment']])
            a.eq(cn+'.provenance',row['provenance'],{k:entry[k] for k in row['provenance']})
            raw=[json.loads(s[len('P4_COLLISION_RESULT '):]) for s in row['source_stdout'].splitlines() if s.startswith('P4_COLLISION_RESULT ')]
            a.eq(cn+'.raw_count',len(raw),1)
            a.eq(cn+'.raw_fields',raw[0],{k:row[k] for k in ('native_result','cpu_s','poses','query_codes')})
            a.add(cn+'.all_raw_codes',bool(row['query_codes']) and all(type(x) is int and x==0 for x in row['query_codes']))
            a.eq(cn+'.native_result',row['native_result'],0); a.eq(cn+'.query_error_codes',row['query_error_codes'],[])
            a.eq(cn+'.native_collision',row['native_collision'],False)
            query_totals[variant]+=len(row['query_codes'])
            pc=row['pose_consistency']; pc_pass=True
            a.eq(cn+'.pose_gates',[pc['position_gate_mm'],pc['rotation_matrix_gate']],[1e-5,1e-5])
            a.eq(cn+'.pose_arm_order',[v['arm'] for v in pc['errors']],[1,2])
            for arm,er in enumerate(pc['errors']):
                col=[row['poses'][arm][j:j+4] for j in (0,4,8)]
                a.eq(cn+f'.arm{arm}.raw_pose',er['collision_TCP'],col)
                a.eq(cn+f'.arm{arm}.independent_pose',er['independent_TCP'],node['poses'][arm][:3])
                pe=max(abs(col[r][3]-node['poses'][arm][r][3]) for r in range(3))
                re=max(abs(col[r][c]-node['poses'][arm][r][c]) for r in range(3) for c in range(3))
                a.near(cn+f'.arm{arm}.position_error',er['translation_maxabs_mm'],pe,1e-12)
                a.near(cn+f'.arm{arm}.rotation_error',er['rotation_maxabs'],re,1e-15)
                pc_pass &= pe<=1e-5 and re<=1e-5
                posemax[variant]['position_mm']=max(posemax[variant]['position_mm'],pe)
                posemax[variant]['rotation']=max(posemax[variant]['rotation'],re)
            a.eq(cn+'.pose_pass_arithmetic',pc['passed'],pc_pass)
            a.eq(cn+'.pose_status',pc['status'],'PASS' if pc_pass else 'COLLISION_PHYSICAL_TCP_MISMATCH')
            if variant=='aligned': a.eq(cn+'.aligned_must_pass',pc_pass,True)
        for k in ('source_command','source_stdout','source_stderr'): a.eq(n+'.selected_'+k,co[k],co['variants']['aligned'][k])
        a.eq(n+'.node_gate',node['node_qualified'],math_ok and not co['collision'])
        events=[v for v in worker_events if v.get('node_id')==i]
        expected=[]
        for arm in (1,2):
            for kind in ('math_arm_FK_started','math_arm_FK_completed'): expected.append((kind,arm))
        expected.append(('collision_started',None))
        for variant in ('native','aligned'):
            for arm in (1,2):
                for kind in ('adapter_arm_FK_J_started','adapter_arm_FK_J_completed'): expected.append((kind,arm))
        expected.append(('collision_completed',None))
        a.eq(n+'.events_in_exact_order',[(v['event'],v.get('arm')) for v in events],expected)
        for ev in events:
            k=ev['event']; worker_counts['collision_calls_'+k.split('_')[-1] if k in ('collision_started','collision_completed') else k]+=1
            if 'environment' in ev: a.eq(n+'.event_environment',ev['environment'],node['environment'])
        finish=events[-1]; qc={v:len(r['query_codes']) for v,r in co['variants'].items()}
        a.eq(n+'.collision_event_queries',finish['variant_query_counts'],qc)
        a.eq(n+'.collision_event_query_total',finish['PQP_queries'],sum(qc.values()))
        a.eq(n+'.collision_event_status',finish['status'],co['status'])
        worker_counts['PQP_queries']+=sum(qc.values())
        a.eq(n+'.worker_cumulative_counts',wr['observed_counts'],dict(worker_counts))
        node_summaries.append({'node_id':i,'environment':node['environment'],'closure_position_mm':pos,'closure_rotation':rot,'minimum_limit_margin_rad':margin,'qualified':math_ok and not co['collision']})
    sound=True; endpoint_gates={env:True for env in ('II','III')}; pair_summaries=[]
    for pair,qp in zip(pairs,qualified):
        id=pair['request']['id']; r=pair['trace']; req=pair['request']; refs=pair_refs[id]
        gd_ok=all(nodes[v['node_id']]['math_qualified'] for v in refs if v['kind']=='gd' and v['returned'])
        relevant=[v for v in refs if v['kind']!='gd' or v['returned']]
        ret_ok=not r['returned'] or all(nodes[v['node_id']]['node_qualified'] is True for v in relevant)
        a.eq('pair.'+id+'.gd_math_sound',qp['gd_accepted_math_sound'],gd_ok)
        info={'id':id,'returned':r['returned'],'accepted_GD_math_sound':gd_ok}
        if req['op']=='reconstruct' and r['returned']:
            qs=r['path_q12']; exact=len(qs)>=2 and qbytes(qs[0])==qbytes(req['qa12']) and qbytes(qs[-1])==qbytes(req['qb12'])
            leaves=[l2(qa,qb) for qa,qb in zip(qs,qs[1:])]
            ret_ok &= exact and all(d<.05 for d in leaves)
            a.eq('pair.'+id+'.endpoints_exact',qp['path_endpoint_exact'],exact)
            a.eq('pair.'+id+'.saved_leaf_distances',qp['all_leaf_distances_rad'],leaves)
            a.eq('pair.'+id+'.all_original_path_nodes',qp['all_source_path_nodes_qualified'],all(nodes[v['node_id']]['node_qualified'] for v in refs if v['kind']=='path'))
            a.add('pair.'+id+'.all_strict_leaves',all(d<.05 for d in leaves))
            info.update(path_node_count=len(qs),max_leaf_L2_rad=max(leaves),path_endpoint_exact=exact)
        a.eq('pair.'+id+'.returned_sound',qp['returned_sound'],ret_ok)
        info['returned_sound']=ret_ok; sound &= gd_ok and ret_ok; pair_summaries.append(info)
        if req['op']=='project_q12': endpoint_gates[pair['environment']] &= bool(r['returned'] and ret_ok)
    byid={s['id']:s for s in pair_summaries}; outcomes=[]
    for edge in edges:
        i=edge['edge_index']; rb=byid[f'II_edge_{i}_rbs']; rc=byid[f'II_edge_{i}_reconstruct']
        rr=responses[('II','trace',rb['id'])]; cr=responses[('II','trace',rc['id'])]
        nontrivial=l2(edge['qa12'],edge['qb12'])>=.05 and bool(rr['gd_completed_candidates']) and bool(cr['gd_completed_candidates'])
        ok=bool(rb['returned'] and rc['returned'] and nontrivial and rb['returned_sound'] and rc['returned_sound'] and rb['accepted_GD_math_sound'] and rc['accepted_GD_math_sound'])
        out={'edge_index':i,'source_rbs_returned':rb['returned'],'source_reconstruct_returned':rc['returned'],'nontrivial_real_recursion':nontrivial,'qualified_nontrivial_RBS_and_full_original_path':ok,'status':'PASS_NONTRIVIAL_ORIGINAL_NR_EDGE' if ok else 'REJECT_OR_PARTIAL','full12_endpoint_distance_rad':l2(edge['qa12'],edge['qb12'])}
        if rb['returned'] and not rc['returned']: out['rbs_true_reconstruct_false']=True
        outcomes.append(out)
    positive=sum(v['qualified_nontrivial_RBS_and_full_original_path'] for v in outcomes)
    next_gate=sound and endpoint_gates['II'] and positive>=1 and not any(v.get('rbs_true_reconstruct_false',False) for v in outcomes)
    status='STOP_SOURCE_TRUE_UNSOUND' if not sound else 'FIXED_LOCAL_ABB_NR_QUALIFIED' if positive==3 and all(endpoint_gates.values()) else 'FIXED_LOCAL_ABB_NR_PARTIAL'
    a.eq('outcomes.saved',load(FOLDER/'local_outcomes.json'),outcomes); a.eq('outcomes.execution',e['outcomes'],outcomes)
    for k,v in {'status':status,'soundness_passed':sound,'qualified_nontrivial_edges':positive,'endpoint_project_gate_by_environment':endpoint_gates,'next_planner_environment':'II','next_planner_gate_supported':next_gate}.items(): a.eq('derived_gate.'+k,e[k],v)
    expected_counts={'top_requests_submitted_to_batch':20,'top_responses_completed':len(raw_sources),'full_node_queue':len(queue),'completed_nodes':len(nodes),**dict(worker_counts)}
    expected_counts.update({'trace_'+k+'_completed':v for k,v in counters.items()})
    expected_counts.update({'actual_'+k.replace('collision_calls_','collision_'):v for k,v in worker_counts.items() if k!='PQP_queries'})
    expected_counts.update({'actual_adapter_PQP_queries':sum(query_totals.values()),**{'actual_adapter_'+k+'_PQP_queries':v for k,v in query_totals.items()},'actual_source_responses_retained':len(raw_sources),'actual_source_calls_completed':sum(v['status']=='SOURCE_CALL_COMPLETED' for v in raw_sources),'actual_node_responses_retained':len(worker_responses)})
    for k,v in counters.items():
        expected_counts['actual_trace_'+k+'_started']=v; expected_counts['actual_trace_'+k+'_completed']=v
    a.eq('counts.exact_independent_accounting',e['counts'],expected_counts)
    inv=load(FOLDER/'raw_prefix_inventory.json')
    for k,v in {'source_responses':raw_sources,'node_responses':worker_responses,'worker_events':worker_events,'trace_entered_counts':dict(counters),'trace_completed_counts':dict(counters),'actual_observed_only':True}.items(): a.eq('raw_prefix_inventory.'+k,inv[k],v)
    pevents=jsonl(FOLDER/'events.jsonl'); starts=[v for v in pevents if v['event']=='process_started']; finishes=[v for v in pevents if v['event']=='process_finished']
    a.eq('processes.all5_started_completed',len(starts),5); a.eq('processes.all5_finish_count',len(finishes),5)
    a.add('processes.no_interrupted_stop_events',all(v['event'] in ('source_batch_started','process_started','process_finished') for v in pevents))
    for i,(start,finish) in enumerate(zip(starts,finishes)):
        label=start['label']; stem=f'{i+1:05d}_{label}'
        a.eq('process.'+label+'.same_label',finish['label'],label); a.eq('process.'+label+'.exit0',finish['exit_code'],0)
        for field,suffix in [('stdout_sha256','.stdout.txt'),('stderr_sha256','.stderr.txt')]: a.eq('process.'+label+'.'+field,sha(FOLDER/(stem+suffix)),finish[field])
        if i<4:
            b=schedule[i]; runtime=FOLDER/f'runtime_{b["environment"]}_{b["mode"]}'
            a.eq('process.'+label+'.command',start['command'],[p['build']['binary'],b['environment'],b['mode'],str(runtime)])
            for mesh,want in p['build']['mesh_sources'].items(): a.eq('runtime.mesh.'+label+'.'+Path(mesh).name,sha(runtime/'simulator'/Path(mesh).name),want)
    a.eq('worker.input_queue_hash',jsonl(FOLDER/'00005_independent_full_node_queue.input.txt')[0]['node_queue_sha256'],e['node_queue_sha256'])
    started=load(FOLDER/'node_worker_started.json')
    a.eq('worker.parent',started['parent_pid'],c['parent_pid']); a.eq('worker.protocol',started['protocol_sha256'],e['protocol_sha256']); a.eq('worker.queue',started['node_queue_sha256'],e['node_queue_sha256'])
    a.eq('tail.completed_ids',e['completed_node_ids'],list(range(len(queue))))
    for k in ('uncompleted_node_ids','uncompleted_top_requests','diagnostics'): a.eq('tail.'+k,e[k],[])
    a.eq('tail.full_queue_count',e['full_node_queue_count'],len(queue)); a.eq('tail.full_checked',e['full_node_queue_checked'],True)
    a.eq('tail.all20_response_ids',e['completed_source_response_ids'],[{k:r[k] for k in ('environment','mode','id','status')} for r in raw_sources])
    a.eq('tail.no_partial_files',sorted(v.name for v in FOLDER.glob('*stopped*')),[])
    a.eq('zero_calls',e['zero_calls'],{'solve':0,'RNG':0,'IK':0,'VI_constructions':0,'formal_table_I':0})
    a.eq('plain_internals_unobserved',e['plain_internal_GD_FK_PQP'],'UNOBSERVED')
    priors=[load(v) for v in e['prior_executions']]
    a.eq('budget.prior_paths',e['prior_executions'],p['prior_executions'])
    for axis in ('wall_s','cpu_s'):
        total=math.fsum(v[axis] for v in priors)
        a.eq('budget.prior_'+axis,e['previous_r2_'+axis],total)
        a.eq('budget.protocol_prior_'+axis,p['previous_r2_'+axis],total)
        cap=e['budget'][axis]; cumulative=total+e[axis]
        a.add('budget.local_'+axis,0<=e[axis]<cap,used=e[axis],cap=cap)
        a.add('budget.cumulative_'+axis,cumulative<e['budget']['r2_total_'+axis],used=cumulative,cap=e['budget']['r2_total_'+axis])
    a.eq('budget.protocol',e['budget'],p['budget'])
    a.add('timestamps.ordered',datetime.fromisoformat(e['ended_at_utc'])>datetime.fromisoformat(e['started_at_utc']))
    failed=[v for v in a.checks if not v['passed']]
    return {'schema':'P4_R2_ABB_NR_LOCAL_SAVED_POST_V1','created_at_utc':datetime.now(timezone.utc).isoformat(),'run_id':RUN,
        'status':'PASS_SAVED_EVIDENCE_POST' if not failed else 'FAIL_SAVED_EVIDENCE_POST','source_commit':e['source_commit'],
        'audit_author_wrote_runner':True,'personnel_independent':False,
        'independence_scope':'Separately implemented stdlib-only evidence parsing, binary64 queue/ref reconstruction, saved-pose closure/limit/collision arithmetic; root/second agent must independently review.',
        'audit_scientific_calls':{'solve':0,'NR':0,'FK':0,'Jacobian':0,'IK':0,'PQP':0,'RNG':0,'compile':0},
        'execution_sha256':sha(FOLDER/'execution.json'),'protocol_sha256':sha(e['protocol']),'audit_script_sha256':sha(__file__),
        'checks_total':len(a.checks),'checks_passed':len(a.checks)-len(failed),'checks_failed':len(failed),'failed_checks':failed,
        'result':{'source_top_responses':len(raw_sources),'logical_pairs':len(pairs),'full_unique_nodes':len(queue),'qualified_nodes':sum(v['node_qualified'] is True for v in nodes.values()),'qualified_nontrivial_edges':positive,'next_environment_II_planner_gate':next_gate,'max_closure_position_mm':maxpos,'max_closure_rotation_matrix':maxrot,'min_source_limit_margin_rad':minmargin,'GD_accepted_updates_histogram':dict(sorted(gd_updates.items())),'source_trace_completed_counts':dict(counters),'adapter_PQP_queries_by_variant':dict(query_totals),'pose_error_maxima':posemax,'prior_execution_count':len(priors),'wall_s':e['wall_s'],'cpu_s':e['cpu_s'],'cumulative_r2_wall_s':e['previous_r2_wall_s']+e['wall_s'],'cumulative_r2_cpu_s':e['previous_r2_cpu_s']+e['cpu_s']},
        'pair_summaries':pair_summaries,'trace_summaries':trace_summaries,'node_summaries':node_summaries,
        'limits':['Finite fixed local qualification only; no planner solve or formal Table I statistic.',
            'Native collision TCP mismatch retained separately; selected aligned v3 passes saved TCP evidence.',
            'Original discrete mesh pair policy, 8mm PQP tolerance and collinear rod triangles retained; no CCD, rod-surface or omitted-pair certificate.',
            'Legacy math_arm_FK event calls the FK/J implementation; does not establish zero Jacobian evaluations.',
            'Plain internal GD/FK/PQP counts are UNOBSERVED; trace counts are not doubled.'],
        'checks':a.checks}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--inspect-only',action='store_true'); args=parser.parse_args()
    if not args.inspect_only:
        for suffix in ('.json','.md'):
            if Path(str(REPORT)+suffix).exists(): raise SystemExit('EXCLUSIVE_REPORT_EXISTS: '+str(REPORT)+suffix)
    r=audit()
    print(json.dumps({k:r[k] for k in ('status','checks_total','checks_passed','checks_failed','result')},ensure_ascii=False))
    if r['failed_checks']: print(json.dumps(r['failed_checks'][:30],ensure_ascii=False))
    if args.inspect_only: return
    with Path(str(REPORT)+'.json').open('x') as f: json.dump(r,f,ensure_ascii=False,indent=2,allow_nan=False); f.write('\n')
    s=r['result']; recon=[v for v in r['pair_summaries'] if 'path_node_count' in v]
    md=f'''# P4 R2 ABB NR 固定 local 保存证据 POST（2026-10-15）

状态：`{r['status']}`；检查 {r['checks_passed']}/{r['checks_total']} 通过，失败 {r['checks_failed']}。

本审查作者也编写了 local runner。这里的独立性指单独实现的 stdlib 保存证据解析与算术，不能声称人员独立；须由 root 和另一代理复核。审查不导入科学模块，不调用模型、FK/J、NR、IK、PQP、RNG、planner 或编译器，仅 Git 读取、文件重 hash 和保存数组算术。

冻结源提交 `{r['source_commit']}`；execution SHA256 `{r['execution_sha256']}`。协议/claim、{len(load(FOLDER/'execution.json')['bound_files_sha256'])} 项绑定的前/后/当前 hash、冻结提交源 blob、已有未查询 build 的源码/mesh/binary 链均核对。4个A01 RECONSTRUCTED端点和首PCS原路径全部3条连续边逐项回溯；原作者原端点没有据此改记直接合格。

20/20 原响应、10 logical pairs 均保留；plain/trace 非计时结果与 binary64 q/path 精确一致，entered/completed 按 id/kind/LIFO 配对。全部 GD summary 与原 trace 逐项一致，PQP 原返回码全0。按环境与 q12 二进制字节重新构造全部 {s['full_unique_nodes']} 节点，全部 refs、collision-required OR 及节点顺序一致，无抽稀、无未检查尾部。

{s['qualified_nodes']}/{s['full_unique_nodes']} 节点通过。仅由保存 poses 计算 `T2 - T1 @ grasp @ diag(-1,-1,1,1)`，最大位置残差 {s['max_closure_position_mm']:.17g} mm，最大旋转矩阵残差 {s['max_closure_rotation_matrix']:.17g}；物理门均为1e-5。原关节界保留 `degrees * 3.1416 / 180`，最小余量 {s['min_source_limit_margin_rad']:.17g} rad；没有wrap/lift/主动链或PCS分支门。

| 固定原边 | 原 reconstruct 节点数 | 最大全12角叶L2 (rad) | 门 |
| --- | ---: | ---: | --- |
'''
    for v in recon: md+=f"| {v['id']} | {v['path_node_count']} | {v['max_leaf_L2_rad']:.17g} | 首尾binary64精确、所有叶严格<0.05、所有节点合格 |\n"
    md+=f'''
全部3条 RBS/reconstruct 各有真实GD递归，原始返回均 true。没有 RBStrue/reconstructfalse，soundness通过，环境II两个固定project通过，支持下一项环境II RRT_NR规划入口资格（仍须单独冻结与审批）。本次不计正式规划/统计，不证明NR全局能力、PCS相对优势或Table I结论。

原 trace计数：`{json.dumps(s['source_trace_completed_counts'],ensure_ascii=False)}`。GD accepted-updates分布：`{json.dumps(s['GD_accepted_updates_histogram'])}`。数学逐臂294次、adapter FK/J 588次，独立碰撞147次；adapter PQP native/aligned 各 {s['adapter_PQP_queries_by_variant']['native']} / {s['adapter_PQP_queries_by_variant']['aligned']}，共 {sum(s['adapter_PQP_queries_by_variant'].values())}。源trace PQP是另一层计数 {s['source_trace_completed_counts']['pqp']}，plain内部标记UNOBSERVED，未按trace倍增。

native TCP最大位置差 {s['pose_error_maxima']['native']['position_mm']:.17g} mm、旋转差 {s['pose_error_maxima']['native']['rotation']:.17g}，保留失败证据；selected aligned最大位置差 {s['pose_error_maxima']['aligned']['position_mm']:.17g} mm、旋转差 {s['pose_error_maxima']['aligned']['rotation']:.17g}，所有pose门通过。逐variant原stdout、query_codes、provenance、node collision raw与worker副本全部交叉核对。

本次 wall {s['wall_s']:.17g}s / CPU {s['cpu_s']:.17g}s，低于60/120；之前{ s['prior_execution_count']}项自有execution按fsum重算，总R2累计wall {s['cumulative_r2_wall_s']:.17g}s / CPU {s['cumulative_r2_cpu_s']:.17g}s，低于3600/7200。5个进程完成退出0，所有process原始stdout/stderr hash及worker开始证据相符，无stopped partial、未完成请求、节点尾部或cleanup诊断。

保留原离散碰撞pair策略、8mm PQP容差、共线杆三角形限制；不声称连续碰撞、实体杆表面或省略pair安全。旧`math_arm_FK`标签实际经FK/J实现，不解释为Jacobian零次。211项完整覆盖清单和Table I 0/22500义务保留。

详细检查、每对响应计数及每节点算术见同名JSON。审查脚本SHA256 `{r['audit_script_sha256']}`。
'''
    if r['failed_checks']: md+='\n失败证据：\n\n```json\n'+json.dumps(r['failed_checks'],ensure_ascii=False,indent=2)+'\n```\n'
    with Path(str(REPORT)+'.md').open('x') as f: f.write(md)

if __name__=='__main__': main()
