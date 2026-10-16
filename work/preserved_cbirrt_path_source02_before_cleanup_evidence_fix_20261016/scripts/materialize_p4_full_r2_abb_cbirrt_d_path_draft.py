#!/usr/bin/env python3
"""Pure saved-array CBiRRT path materializer draft; no model/process/file I/O.

The source caller must bind the actual S raw/execution/independent POST before
calling materialize. This helper does not create a protocol, prior or claim.
"""
from collections import Counter
import math
import struct

MAX_NODES=2048
LEAF_GATE=.05

def require(ok,reason):
    if not ok:raise ValueError(reason)

def q12(q):
    require(isinstance(q,list)and len(q)==12 and all(type(v)in(int,float)and math.isfinite(v)for v in q),
        'FINITE_FULL_BINARY64_Q12_REQUIRED')
    return q

def key(q):return struct.pack('>12d',*q12(q))
def distance(a,b):return math.sqrt(math.fsum((x-y)**2 for x,y in zip(q12(a),q12(b))))
def same_path(a,b):return isinstance(a,list)and isinstance(b,list)and [key(q)for q in a]==[key(q)for q in b]
def same_mpaths(a,b):
    if not(isinstance(a,list)and isinstance(b,list)and len(a)==len(b)):return False
    for left,right in zip(a,b):
        if not(isinstance(left,list)and isinstance(right,list)and len(left)==len(right)):return False
        for x,y in zip(left,right):
            if set(x)!=set(y)or key(x['q12'])!=key(y['q12']):return False
            if any(type(x[k])is not type(y[k])or x[k]!=y[k]for k in x if k!='q12'):return False
    return True

def trace_pairs(trace):
    """Pair actual entries/returns and preserve observed markers separately."""
    require(isinstance(trace,list),'ACTUAL_COMPLETE_SOURCE_TRACE_REQUIRED')
    stack=[];pairs=[];marks=[];serial=0;started=Counter();completed=Counter()
    for row in trace:
        event=row['event'];kind=row['kind'];ident=row['id']
        require(type(ident)is int and ident>0,'ACTUAL_TRACE_ID_REQUIRED')
        if event in('entered','observed'):
            serial+=1;require(ident==serial,'ACTUAL_TRACE_SERIAL_REQUIRED')
        if event=='entered':
            stack.append(row);started[kind]+=1
        elif event=='observed':
            require(kind=='save_source_mpaths'and 'source_mpaths'in row['args'],
                'ONLY_ORIGINAL_SOURCE_MPATHS_OBSERVATION_ALLOWED')
            marks.append(dict(event=row,parent_id=None if not stack else stack[-1]['id']))
        else:
            require(event=='completed'and stack,'INCOMPLETE_SOURCE_BODY_TRACE')
            entered=stack.pop();require((ident,kind)==(entered['id'],entered['kind']),'SOURCE_TRACE_STACK_MISMATCH')
            completed[kind]+=1
            pairs.append(dict(entered=entered,completed=row,parent_id=None if not stack else stack[-1]['id']))
    require(not stack and started==completed,'SOURCE_TRACE_UNBALANCED_PREFIX')
    return sorted(pairs,key=lambda p:p['entered']['id']),marks,dict(started),dict(completed)

def tree_identity_audit(d,mpaths,request):
    """Audit both actual Motion trees and their true bridge, without q merging."""
    tree=d['trees'];rows=tree['nodes'];motions={};states={}
    require(isinstance(rows,list)and rows,'ACTUAL_NONEMPTY_TWO_TREES_REQUIRED')
    for row in rows:
        mid=row['motion_id'];sid=row['state_id']
        require(type(mid)is int and mid>0 and type(sid)is int and sid>0 and mid not in motions and sid not in states,
            'UNIQUE_ACTUAL_MOTION_AND_STATE_IDENTITIES_REQUIRED')
        require(row['tree']in('start','goal')and type(row['parent_motion_id'])is int and row['parent_motion_id']>=0,
            'ORIGINAL_TREE_PARENT_ID_REQUIRED')
        require(all(type(row[k])is int for k in('root_motion_id','root_state_id','ik_q1_active','ik_q2_active','a_chain')),
            'ORIGINAL_INITIALIZED_TREE_METADATA_REQUIRED')
        q12(row['q12']);q12(row['root_q12']);motions[mid]=row;states[sid]=row
    roots={side:[r for r in rows if r['tree']==side and r['parent_motion_id']==0]for side in('start','goal')}
    require(all(len(v)==1 for v in roots.values()),'FIXED_ONE_START_AND_ONE_GOAL_ROOT_REQUIRED')
    for side,field in(('start','start_q12'),('goal','goal_q12')):
        require(key(roots[side][0]['q12'])==key(request[field]),'ROOT_NOT_ORIGINAL_A01_'+side)
    for row in rows:
        chain=[];current=row
        while True:
            require(current['motion_id']not in chain,'SOURCE_PARENT_CYCLE')
            chain.append(current['motion_id'])
            require(current['tree']==row['tree'],'SOURCE_PARENT_CROSSES_TREES')
            parent=current['parent_motion_id']
            if parent==0:break
            require(parent in motions,'SOURCE_PARENT_ID_ABSENT');current=motions[parent]
        require(current['motion_id']==roots[row['tree']][0]['motion_id']==row['root_motion_id']
            and current['state_id']==row['root_state_id']and key(current['q12'])==key(row['root_q12']),
            'SOURCE_ROOT_IDENTITY_OR_Q_CHANGED')
    require(isinstance(mpaths,list)and len(mpaths)==2 and all(isinstance(p,list)and p for p in mpaths),
        'TWO_COMPLETE_ORIGINAL_SOURCE_MPATHS_REQUIRED')
    for side,path in zip(('start','goal'),mpaths):
        for index,copied in enumerate(path):
            require(copied['motion_id']in motions,'SOURCE_SAVE_MOTION_NOT_IN_TREE')
            row=motions[copied['motion_id']]
            require(row['tree']==side and copied['parent_id']==row['parent_motion_id']and key(copied['q12'])==key(row['q12'])
                and all(copied[k]==row[k]for k in('ik_q1_active','ik_q2_active','a_chain')),
                'SOURCE_SAVE_MOTION_ID_Q_BRANCH_OR_PARENT_CHANGED')
            expected_parent=path[index+1]['motion_id']if index+1<len(path)else 0
            require(row['parent_motion_id']==expected_parent,'SOURCE_SAVED_PATH_NOT_COMPLETE_PARENT_CHAIN')
        require(path[-1]['motion_id']==roots[side][0]['motion_id'],'SOURCE_SAVE_PATH_ROOT_ABSENT')
        point=tree['connection_'+side];first=motions[path[0]['motion_id']]
        require(point is not None and point['motion_id']==first['motion_id']and point['state_id']==first['state_id']
            and key(point['q12'])==key(first['q12']),'ACTUAL_CONNECTION_POINT_NOT_FIRST_SAVED_MOTION')
    ordered=list(reversed(mpaths[0]))+mpaths[1]
    require(same_path([r['q12']for r in ordered],d['milestones_q12']),
        'MILESTONES_NOT_REVERSE_START_PLUS_FORWARD_GOAL_IDENTITY_ORDER')
    data=d['planner_data'];require(isinstance(data,dict),'EXACT_SOURCE_PLANNER_DATA_REQUIRED')
    vs=data['vertices'];links=data['edges'];vmap={};state_vertex={}
    require([v['index']for v in vs]==list(range(len(vs))),'SOURCE_PLANNER_VERTEX_ORDER')
    for v in vs:
        sid=v['state_id'];require(sid in states and sid not in state_vertex,'PLANNER_VERTEX_STATE_ID_NOT_UNIQUE_TREE_STATE')
        row=states[sid];require(key(v['q12'])==key(row['q12'])and v['tag']==(1 if row['tree']=='start'else 2),
            'PLANNER_VERTEX_STATE_Q_OR_TREE_TAG_CHANGED')
        require(v['start']is(row['tree']=='start'and row['parent_motion_id']==0)
            and v['goal']is(row['tree']=='goal'and row['parent_motion_id']==0),'PLANNER_ROOT_FLAGS_CHANGED')
        vmap[v['index']]=row;state_vertex[sid]=v['index']
    require(set(state_vertex)==set(states),'ALL_TREE_MOTIONS_MUST_HAVE_PLANNER_VERTICES')
    expected=[]
    for row in rows:
        if row['parent_motion_id']==0:continue
        parent=motions[row['parent_motion_id']]
        edge=(parent['state_id'],row['state_id'])if row['tree']=='start'else(row['state_id'],parent['state_id'])
        expected.append(edge)
    bridge=(tree['connection_start']['state_id'],tree['connection_goal']['state_id']);expected.append(bridge)
    actual=[]
    for edge in links:
        require(isinstance(edge,list)and len(edge)==2 and all(type(i)is int and i in vmap for i in edge),
            'SOURCE_PLANNER_EDGE_ID_INVALID')
        actual.append((vmap[edge[0]]['state_id'],vmap[edge[1]]['state_id']))
    require(Counter(actual)==Counter(expected),'PLANNER_DATA_NOT_EXACT_TWO_TREES_PLUS_ACTUAL_BRIDGE')
    ordered_ids=[r['motion_id']for r in ordered]
    bridge_index=len(mpaths[0])-1
    for i,(a,b)in enumerate(zip(ordered_ids,ordered_ids[1:])):
        left,right=motions[a],motions[b]
        if i<bridge_index:require(right['parent_motion_id']==a,'START_PATH_EDGE_NOT_PARENT_TO_CHILD')
        elif i==bridge_index:require((left['state_id'],right['state_id'])==bridge,'MISSING_OR_FABRICATED_REAL_BRIDGE')
        else:require(left['parent_motion_id']==b,'GOAL_PATH_EDGE_NOT_CHILD_TO_PARENT')
    return dict(source_motion_path=ordered_ids,source_tree_vertex_path=[state_vertex[motions[i]['state_id']]for i in ordered_ids],
        source_bridge_milestone_edge_index=bridge_index,source_bridge_state_ids=list(bridge),
        complete_tree_motion_count=len(rows),complete_tree_vertex_count=len(vs),complete_tree_edge_count=len(links),
        same_q_motion_policy='Actual Motion/state identities remain distinct even when complete q12 bytes coincide.')

def materialize(d,request):
    """Freeze all original successful dense M; retain every failed attempt."""
    require(d['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1'and d['environment']=='II'
        and d['operation']=='solve'and d['mode']=='trace'and d['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT'
        and d['exact']is True and d['has_solution']is True and d['approximate']is False,
        'COMPLETE_EXACT_S_RESPONSE_PENDING_P_REQUIRED')
    require(key(d['request']['start_q12'])==key(request['start_q12'])
        and key(d['request']['goal_q12'])==key(request['goal_q12']),'S_ORIGINAL_A01_BINARY64_REQUIRED')
    ms=d['milestones_q12'];require(len(ms)>=2 and key(ms[0])==key(request['start_q12'])and key(ms[-1])==key(request['goal_q12']),
        'EXACT_ORIGINAL_A01_FIRST_LAST_REQUIRED')
    pairs,marks,started,completed=trace_pairs(d['trace'])
    require(started==d['source_started']and completed==d['source_completed'],'COMPLETE_ACTUAL_SOURCE_BODY_COUNTS_REQUIRED')
    saves=[p for p in pairs if p['entered']['kind']=='save2file']
    require(len(saves)==1 and len(marks)==1 and marks[0]['parent_id']==saves[0]['entered']['id'],
        'ONE_ACTUAL_SAVE_BODY_AND_MPATHS_MARK_REQUIRED')
    save=saves[0];mpaths=marks[0]['event']['args']['source_mpaths']
    result=save['completed']['result']
    require(same_mpaths(result['source_mpaths'],mpaths)and result['return_does_not_certify_complete_reconstruction']is True,
        'ORIGINAL_SAVE_MARK_AND_RETURN_PATHS_REQUIRED')
    identity=tree_identity_audit(d,mpaths,request);ordered=list(reversed(mpaths[0]))+mpaths[1]
    attempts=[]
    for pair in pairs:
        if pair['entered']['kind']!='state_reconstruct':continue
        require(pair['parent_id']==save['entered']['id'],'STATE_RECONSTRUCTION_OUTSIDE_ORIGINAL_SAVE_BODY')
        a,z=pair['entered'],pair['completed'];args=a['args'];ret=z['result']
        require(type(ret['returned'])is bool,'ORIGINAL_STATE_RECONSTRUCT_RETURN_TYPE')
        for q in ret['path_q12']:q12(q)
        attempts.append(dict(attempt_index=len(attempts),trace_entry_id=a['id'],trace_return_id=z['id'],
            qa12=q12(args['qa12']),qb12=q12(args['qb12']),active_chain=args['active_chain'],branch=args['branch'],
            returned=ret['returned'],path_q12=ret['path_q12']))
    nodes=[];lookup={};edges=[];cursor=0
    for ei,(a,b)in enumerate(zip(ordered,ordered[1:])):
        chosen=None;consumed=[]
        for role,branch_field in((0,'ik_q1_active'),(1,'ik_q2_active')):
            if chosen is not None:break
            if a[branch_field]!=b[branch_field]:continue
            require(cursor<len(attempts),'SOURCE_EXACT_HAS_MISSING_STATE_RECONSTRUCTION')
            attempt=attempts[cursor];consumed.append(cursor);cursor+=1
            require(key(attempt['qa12'])==key(a['q12'])and key(attempt['qb12'])==key(b['q12'])
                and attempt['active_chain']==role and attempt['branch']==a[branch_field],
                'ORIGINAL_ROLE0_THEN_ROLE1_FALLBACK_CALL_ORDER_CHANGED')
            if attempt['returned']:chosen=attempt
        require(chosen is not None,'SOURCE_EXACT_HAS_FALSE_OR_ABSENT_DENSE_PATH_EDGE')
        qs=chosen['path_q12'];require(type(chosen['active_chain'])is int and chosen['active_chain']in(0,1)
            and type(chosen['branch'])is int and chosen['branch']in range(8),'SUCCESSFUL_ORIGINAL_BRANCH_NOT_0_TO_7')
        require(len(qs)>=2 and key(qs[0])==key(a['q12'])and key(qs[-1])==key(b['q12']),
            'ENTIRE_ORIGINAL_SUCCESSFUL_M_FIRST_LAST_BINARY64_REQUIRED')
        refs=[]
        for q in qs:
            packed=key(q)
            if packed not in lookup:lookup[packed]=len(nodes);nodes.append(q)
            refs.append(lookup[packed])
        leaves=[distance(x,y)for x,y in zip(qs,qs[1:])]
        require(all(math.isfinite(v)and v<LEAF_GATE for v in leaves),'FULL12_ORIGINAL_LEAF_DISTANCE_NOT_STRICT_POINT05')
        edges.append(dict(edge_index=ei,qa12=a['q12'],qb12=b['q12'],qa_motion_id=a['motion_id'],qb_motion_id=b['motion_id'],
            active_chain=chosen['active_chain'],branch=chosen['branch'],selected_attempt_index=chosen['attempt_index'],
            consumed_attempt_indices=consumed,node_ids=refs,leaf_distances_rad=leaves,
            edge_kind='actual_cross_tree_bridge'if ei==identity['source_bridge_milestone_edge_index']else
                'start_parent_to_child'if ei<identity['source_bridge_milestone_edge_index']else'goal_child_to_parent'))
    require(cursor==len(attempts),'UNMATCHED_EXTRA_SOURCE_STATE_RECONSTRUCTIONS')
    require(set(i for edge in edges for i in edge['node_ids'])==set(range(len(nodes))),'FULL_UNIQUE_NODE_QUEUE_NOT_COVERED')
    return dict(nodes=nodes,edges=edges,source_identity_audit=identity,source_milestone_count=len(ms),
        source_attempt_count=len(attempts),all_original_attempts=attempts,
        full_queue_node_count=len(nodes),under_2048_full_queue_cap=len(nodes)<=MAX_NODES,
        deduplication='Physical query reuse only: complete packed big-endian binary64 q12 including signed zero. All actual Motion identities and edge refs remain.',
        node_limit_policy='Retain the entire exact queue. Above2048 blocks execution; no prefix/truncation or node substitution.',
        independent_physical_queries_performed=0,independent_path_qualified=False,continuous_collision_certificate=False)
