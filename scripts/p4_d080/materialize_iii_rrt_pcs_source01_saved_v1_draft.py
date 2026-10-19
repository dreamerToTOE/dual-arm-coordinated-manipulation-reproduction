#!/usr/bin/env python3
"""Only materialize the complete immutable III SOURCE01 saved candidate.

Stdlib only. Original II q12/key/materialize bodies are copied byte for byte;
no model imports, planning, projection, interpolation or collision execution.
Every original dense reference is retained; 2048 only limits future execution.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
ROOT=Path(__file__).resolve().parents[2]
RUN='20261018_R2_D080_III_RRT_PCS_SOURCE01'
SOURCE=ROOT/'results/p4_full'/RUN
ORIGINAL_MATERIALIZER='scripts/qualify_p4_full_r2_abb_rrt_path.py'
ORIGINAL_MATERIALIZER_SHA='bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865'
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
 'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon}
MAX_NODES=2048

def require(condition,reason):
    if not condition:raise ValueError(reason)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def exact(a,b):return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,allow_nan=False,separators=(',',':'))

def q12(q):
    require(isinstance(q,list) and len(q)==12 and
        all(type(v) in (int,float) and math.isfinite(v) for v in q),'FINITE_NUMERIC_Q12_REQUIRED')
    return q

def key(q):return struct.pack('>12d',*q12(q))

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


def saved_inputs(execution_sha,post,post_sha):
    execution=SOURCE/'execution.json'
    require(sha(execution)==execution_sha and sha(post)==post_sha,'EXACT_SAVED_SOURCE_AND_INDEPENDENT_POST_REQUIRED')
    e=load(execution);p=load(post)
    require(e['schema']=='P4_D080_III_RRT_PCS_SOURCE01_EXECUTION_V1' and e['run_id']==RUN
        and e['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT'
        and e['solve_calls_from_result']==1 and e['binary_execution_calls']==1
        and e['counts']['source_request_dispatched']==1 and e['independent_path_qualified']is False
        and not e['diagnostics'],'COMPLETE_EXACT_SINGLE_SOURCE_NOT_PATH_QUALIFICATION_REQUIRED')
    require(p['personnel_independent']is True and p['execution_sha256']==execution_sha
        and p['checks_total']==p['checks_passed'] and p['checks_failed']==0
        and p['external_supervision_qualified']is True,'INDEPENDENT_SAVED_SOURCE_TRANSPORT_POST_REQUIRED')
    files={str(execution):execution_sha,str(post):post_sha}
    for name,wanted in e['retained_run_files_sha256'].items():
        filename=ROOT/name
        require(sha(filename)==wanted,'SAVED_SOURCE_FILE_CHANGED '+name)
        files[str(filename)]=wanted
    protocol=ROOT/e['protocol'];claim=ROOT/e['claim']
    for filename,wanted in ((protocol,e['protocol_sha256']),(claim,e['claim_sha256'])):
        require(sha(filename)==wanted,'SAVED_FROZEN_PROTOCOL_OR_CLAIM_CHANGED')
        files[str(filename)]=wanted
    s=load(protocol)
    require(s['environment']=='III' and s['frozen']is True and s['scientific_execution_authorized']is True
        and s['formal_execution_authorized']is False and all(v is True for v in s['reviews'].values()),
        'FROZEN_III_SOURCE_PROTOCOL_REQUIRED')
    result=SOURCE/'runtime/result.json';d=load(result)
    require(sha(result)==e['source_result_sha256'] and exact(d,load(SOURCE/'parsed_source_result.json'))
        and d['schema']=='P4_ABB_III_RRT_PCS_END_TO_END_DRAFT_V1'
        and d['status']=='SOURCE_SOLVE_RETURNED_PENDING_INDEPENDENT_PATH_AUDIT'
        and d['environment']=='III' and d['exact']is True and d['approximate']is False
        and d['has_solution']is True and d['solve_calls']==1 and d['formal_table_I_calls']==0
        and exact(d['request'],s['request']),'ORIGINAL_III_EXACT_RESULT_REQUIRED')
    require(d['seed']==7 and d['range_rad']==.8 and d['goal_bias']==.05 and s['request']['solve_seconds']==10.,
        'ORIGINAL_III_SEED7_RANGE08_ONE10S_REQUIRED')
    for name in ('start_q12','goal_q12','bounds_low_rad','bounds_high_rad'):
        require(exact(d[name],s['request'][name]),'SOURCE_METADATA_MISMATCH '+name)
    rec=[json.loads(line)for line in(SOURCE/'runtime/reconstruction_attempts.jsonl').read_bytes().splitlines()]
    ids=[json.loads(line)for line in(SOURCE/'runtime/identify_observations.jsonl').read_bytes().splitlines()]
    require(exact(rec,d['reconstruction_attempts']) and len(ids)==d['identify_observation_count']
        and all(type(row['attempt_index'])is int and row['attempt_index']==i for i,row in enumerate(rec)),
        'COMPLETE_SAVED_POSTRETURN_LOGS_REQUIRED')
    require(sha(ROOT/ORIGINAL_MATERIALIZER)==ORIGINAL_MATERIALIZER_SHA,'ORIGINAL_PURE_MATERIALIZER_CHANGED')
    files[str(ROOT/ORIGINAL_MATERIALIZER)]=ORIGINAL_MATERIALIZER_SHA
    files[str(Path(__file__).resolve())]=sha(__file__)
    return d,files


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execution-sha',required=True)
    parser.add_argument('--independent-post',required=True,type=Path)
    parser.add_argument('--post-sha',required=True)
    parser.add_argument('--output',required=True,type=Path)
    a=parser.parse_args();post=a.independent_post.resolve()
    d,files=saved_inputs(a.execution_sha,post,a.post_sha)
    # A source EXACT may still lack a successful original reconstruction.
    # Preserve that mechanism as STOP and never call a new solve or fill gaps.
    queue=None;error=None
    try:queue=materialize(d)
    except (ValueError,KeyError,TypeError,OverflowError)as exc:error=repr(exc)
    complete=queue is not None
    data=dict(schema='P4_D080_III_RRT_PCS_SOURCE01_COMPLETE_SAVED_QUEUE_DRAFT_V1',
        status=('DRAFT_COMPLETE_SAVED_QUEUE_PENDING_INDEPENDENT_PHYSICAL_FREEZE'if complete else
                'STOP_ORIGINAL_SAVED_RECONSTRUCTION_NOT_COMPLETE'),
        frozen=False,executable=False,environment='III',method='PCS',planner='RRT',
        classification='RECONSTRUCTED_A01_CORRECTED_ABB_APC_ORIGINAL_RRT_PCS_DISCRETE_SOURCE_POLICY',
        source_execution=str((SOURCE/'execution.json').relative_to(ROOT)),source_execution_sha256=a.execution_sha,
        source_independent_POST=str(post.relative_to(ROOT)),source_independent_POST_sha256=a.post_sha,
        bound_files_sha256=files,original_pure_materializer=ORIGINAL_MATERIALIZER,
        original_pure_materializer_sha256=ORIGINAL_MATERIALIZER_SHA,fixed_queue=queue,materialization_error=error,
        full_queue_node_count=None if queue is None else len(queue['nodes']),max_nodes_per_execution=MAX_NODES,
        entire_queue_under_resource_limit=False if queue is None else len(queue['nodes'])<=MAX_NODES,
        all_false_attempts_retained_in_source=True,source_exact_is_not_independent_path_pass=True,
        new_binary_model_scientific_calls=0,independent_path_qualified=False,continuous_collision_certificate=False,
        new_VI_candidate_constructions=0,formal_table_I_calls=0,
        limits='Complete saved queue only; no new nodes, retries, interpolation, smoothing, model calls or scientific acceptance.')
    with a.output.open('x')as stream:
        json.dump(data,stream,ensure_ascii=False,allow_nan=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps(dict(status=data['status'],full_queue_node_count=data['full_queue_node_count'],
        entire_queue_under_resource_limit=data['entire_queue_under_resource_limit'],new_binary_model_scientific_calls=0)))


if __name__=='__main__':main()
