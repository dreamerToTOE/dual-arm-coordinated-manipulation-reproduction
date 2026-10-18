#!/usr/bin/env python3
"""Pure saved SBL arrays only; no file/model/process I/O and no reconstruction."""
from collections import Counter
import materialize_p4_full_r2_abb_cbirrt_d_path_draft as common

MAX_NODES=common.MAX_NODES
LEAF_GATE=common.LEAF_GATE
require=common.require
q12=common.q12
key=common.key
distance=common.distance
same_path=common.same_path
same_mpaths=common.same_mpaths


def trace_pairs(trace):
    stack=[];pairs=[];marks=[];serial=0;started=Counter();completed=Counter();live={};registered={}
    allowed={'save_source_mpaths','motion_lifetime_registered','motion_before_native_retirement','motion_lifetime_retired','ik_path_metadata_attempt'}
    for row in trace:
        event=row['event'];kind=row['kind'];ident=row['id']
        require(type(ident)is int and ident>0,'ACTUAL_TRACE_ID_REQUIRED')
        if event in('entered','observed'):
            serial+=1;require(ident==serial,'ACTUAL_TRACE_SERIAL_REQUIRED')
        if event=='entered':stack.append(row);started[kind]+=1
        elif event=='observed':
            require(kind in allowed,'UNRECOGNIZED_ORIGINAL_OBSERVATION')
            marks.append(dict(event=row,parent_id=None if not stack else stack[-1]['id']))
            args=row['args']
            if kind=='motion_lifetime_registered':
                mid=args['motion_id'];require(mid not in registered and type(mid)is int and mid>0,'UNIQUE_LIFETIME_REGISTRATION_REQUIRED')
                require(type(args['state_id'])is int and args['state_id']>0 and type(args['address_generation'])is int and args['address_generation']>0,
                    'ACTUAL_STATE_AND_ADDRESS_GENERATION_REQUIRED')
                registered[mid]=args;live[mid]=args
            elif kind=='motion_before_native_retirement':
                require(args['motion_id']in live,'RETIREMENT_MUST_BE_LIVE')
            elif kind=='motion_lifetime_retired':
                mid=args['motion_id'];require(mid in live,'RETIREMENT_MUST_BE_UNIQUE');del live[mid]
        else:
            require(event=='completed'and stack,'INCOMPLETE_SOURCE_BODY_TRACE')
            entered=stack.pop();require((ident,kind)==(entered['id'],entered['kind']),'SOURCE_TRACE_STACK_MISMATCH')
            completed[kind]+=1;pairs.append(dict(entered=entered,completed=row,parent_id=None if not stack else stack[-1]['id']))
    require(not stack and started==completed and not live,'COMPLETE_SOURCE_BODY_AND_LIFETIME_RETIREMENT_REQUIRED')
    return sorted(pairs,key=lambda p:p['entered']['id']),marks,dict(started),dict(completed),registered


def tree_identity_audit(d,mpaths,request,pairs,marks,registered):
    tree=d['trees_before_destruction'];rows=tree['nodes'];motions={};states={}
    require(tree['identity_policy']=='LIVE_MOTION_LIFETIME_GENERATION_NO_Q_MERGE','ACTUAL_LIVE_LIFETIME_POLICY_REQUIRED')
    for row in rows:
        mid=row['motion_id'];sid=row['state_id']
        require(type(mid)is int and mid>0 and type(sid)is int and sid>0 and mid not in motions and sid not in states,
            'UNIQUE_ACTUAL_LIVE_MOTION_AND_STATE_REQUIRED')
        require(row['tree']in('start','goal')and type(row['parent_motion_id'])is int and row['parent_motion_id']>=0,
            'ORIGINAL_TREE_PARENT_ID_REQUIRED')
        require(all(type(row[k])is int for k in('root_motion_id','ik_q1_active','ik_q2_active','address_generation')),
            'ORIGINAL_INITIALIZED_TREE_METADATA_REQUIRED')
        require((row['a_chain']in(0,1)and type(row['a_chain'])is int and row['a_chain_provenance']in('ROOT_ASSIGNED','GROW_ASSIGNED'))
            or(row['a_chain']is None and row['a_chain_provenance']=='UNINITIALIZED_NOT_READ'),
            'UNKNOWN_CONNECT_ROLE_MUST_REMAIN_NULL')
        q12(row['q12']);require(mid in registered,'LIVE_TREE_MOTION_NOT_REGISTERED')
        original=registered[mid]
        for name in('state_id','parent_motion_id','root_motion_id','ik_q1_active','ik_q2_active','address_generation','a_chain','a_chain_provenance','tree'):
            require(row[name]==original[name]and type(row[name])is type(original[name]),'REGISTERED_MOTION_IDENTITY_CHANGED '+name)
        require(key(row['q12'])==key(original['q12']),'REGISTERED_MOTION_Q_CHANGED')
        motions[mid]=row;states[sid]=row
    require(tree['native_tree_sizes']==[sum(r['tree']==s for r in rows)for s in('start','goal')],'ACTUAL_NATIVE_TREE_SIZE_MISMATCH')
    roots={s:[r for r in rows if r['tree']==s and r['parent_motion_id']==0]for s in('start','goal')}
    require(all(len(v)==1 for v in roots.values()),'ONE_START_AND_GOAL_ROOT_REQUIRED')
    for side,field in(('start','start_q12'),('goal','goal_q12')):
        require(key(roots[side][0]['q12'])==key(request[field]),'ROOT_NOT_ORIGINAL_A01_'+side)
    for row in rows:
        seen=set();current=row
        while current['parent_motion_id']:
            require(current['motion_id']not in seen,'SOURCE_PARENT_CYCLE');seen.add(current['motion_id'])
            require(current['parent_motion_id']in motions,'SOURCE_PARENT_ABSENT');current=motions[current['parent_motion_id']]
            require(current['tree']==row['tree'],'SOURCE_PARENT_CROSSES_TREES')
        require(current['motion_id']==roots[row['tree']][0]['motion_id']==row['root_motion_id'],'SOURCE_ROOT_IDENTITY_CHANGED')
    require(len(mpaths)==2 and all(isinstance(p,list)and p for p in mpaths),'TWO_COMPLETE_ORIGINAL_MPATHS_REQUIRED')
    for side,mpath in zip(('start','goal'),mpaths):
        for index,copied in enumerate(mpath):
            require(copied['motion_id']in motions,'SAVED_MOTION_ABSENT_FROM_LIVE_TREE');row=motions[copied['motion_id']]
            require(row['tree']==side and row['valid']is True and copied['valid']is True,'SOURCE_SAVED_MOTION_NOT_VALID_IN_ITS_TREE')
            require(set(copied)==set(row)-{'tree'}and key(copied['q12'])==key(row['q12'])and all(copied[k]==row[k]and type(copied[k])is type(row[k])for k in copied if k!='q12'),
                'SAVED_MOTION_ID_GENERATION_Q_BRANCH_OR_PARENT_CHANGED')
            require(row['parent_motion_id']==(mpath[index+1]['motion_id']if index+1<len(mpath)else 0),'SAVED_PATH_NOT_COMPLETE_PARENT_CHAIN')
        require(mpath[-1]['motion_id']==roots[side][0]['motion_id'],'SOURCE_SAVE_PATH_ROOT_ABSENT')
    ordered=list(reversed(mpaths[0]))+mpaths[1]
    require(same_path([r['q12']for r in ordered],d['milestones_q12']),'MILESTONES_NOT_ACTUAL_SAVED_IDENTITY_ORDER')
    saves=[p for p in pairs if p['entered']['kind']=='save2file'];save=saves[0]
    successful=[p for p in pairs if p['entered']['kind']=='checkSolution'and p['completed']['result']['returned']is True]
    require(len(successful)==1 and save['parent_id']==successful[0]['entered']['id'],'SAVE_NOT_INSIDE_UNIQUE_SUCCESSFUL_NATIVE_CHECKSOLUTION')
    check=successful[0];args=check['entered']['args'];side='start'if args['start']else'goal';other='goal'if args['start']else'start'
    current=mpaths[0][0]if side=='start'else mpaths[1][0];target=mpaths[1][0]if other=='goal'else mpaths[0][0]
    require(args['motion']['motion_id']==current['motion_id']and key(args['motion']['q12'])==key(current['q12']),
        'NATIVE_CHECKSOLUTION_MOTION_NOT_ACTUAL_BRIDGE_ENDPOINT')
    connects=[r for r in rows if r['tree']==side and r['parent_motion_id']==current['motion_id']and key(r['q12'])==key(target['q12'])
        and r['a_chain']is None and r['a_chain_provenance']=='UNINITIALIZED_NOT_READ'and r['valid']is True]
    require(len(connects)==1,'UNIQUE_NATIVE_VALID_CONNECT_COPY_REQUIRED');connect=connects[0]
    require(any(any(p['entered']['id']==m['parent_id']and p['entered']['kind']=='addMotion'and p['parent_id']==check['entered']['id']for p in pairs)and m['event']['kind']=='motion_lifetime_registered'
        and m['event']['args']['motion_id']==connect['motion_id']for m in marks),'CONNECT_NOT_CREATED_IN_ACTUAL_SUCCESSFUL_CHECKSOLUTION')
    return dict(source_motion_path=[r['motion_id']for r in ordered],source_state_path=[r['state_id']for r in ordered],
        source_address_generations=[r['address_generation']for r in ordered],source_bridge_milestone_edge_index=len(mpaths[0])-1,
        source_bridge_motion_ids=[mpaths[0][0]['motion_id'],mpaths[1][0]['motion_id']],native_connect_motion_id=connect['motion_id'],
        native_connect_role=None,native_connect_role_provenance='UNINITIALIZED_NOT_READ',complete_tree_motion_count=len(rows),
        planner_data='NOT_EMITTED_BY_THIS_SBL_DRIVER; actual live trees plus source checkSolution/save identity used',
        same_q_motion_policy='Motion/state/lifetime identities remain separate; only physical query bytes may be reused.')


def materialize(d,request):
    require(d['schema']=='P4_ABB_SBL_PCS_SHADOW_V2_RUNTIME_DRAFT'and d['request']['environment']=='II'
        and d['operation']=='solve'and d['mode']=='trace'and d['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_QUALIFICATION'
        and d['exact']is True and d['solution_count']==1,'ACTUAL_EXACT_SINGLE_SBL_RESPONSE_REQUIRED')
    require(d['request']==request,'EXACT_FIXED_SOURCE_REQUEST_REQUIRED')
    ms=d['milestones_q12'];require(len(ms)>=2 and key(ms[0])==key(request['start_q12'])and key(ms[-1])==key(request['goal_q12']),
        'EXACT_ORIGINAL_A01_FIRST_LAST_REQUIRED')
    pairs,marks,started,completed,registered=trace_pairs(d['trace'])
    require(started==d['source_started']and completed==d['source_completed'],'COMPLETE_SOURCE_BODY_COUNTS_REQUIRED')
    saves=[p for p in pairs if p['entered']['kind']=='save2file'];mpath_marks=[m for m in marks if m['event']['kind']=='save_source_mpaths']
    require(len(saves)==len(mpath_marks)==1 and mpath_marks[0]['parent_id']==saves[0]['entered']['id'],'ONE_ORIGINAL_SAVE_AND_MPATH_MARK_REQUIRED')
    save=saves[0];mpaths=mpath_marks[0]['event']['args']['source_mpaths'];ret=save['completed']['result']
    require(same_mpaths(ret['source_mpaths'],mpaths)and ret['return_does_not_certify_complete_reconstruction']is True,'SAVE_MARK_RETURN_IDENTITY_REQUIRED')
    identity=tree_identity_audit(d,mpaths,request,pairs,marks,registered);ordered=list(reversed(mpaths[0]))+mpaths[1]
    attempts=[]
    for p in pairs:
        if p['entered']['kind']!='state_reconstruct':continue
        require(p['parent_id']==save['entered']['id'],'STATE_RECONSTRUCTION_OUTSIDE_SAVE')
        a=p['entered'];z=p['completed'];args=a['args'];ret=z['result']
        require(type(ret['returned'])is bool,'ORIGINAL_RECONSTRUCT_RETURN_BOOL_REQUIRED')
        for q in ret['path_q12']:q12(q)
        attempts.append(dict(attempt_index=len(attempts),trace_entry_id=a['id'],trace_return_id=z['id'],qa12=q12(args['qa12']),qb12=q12(args['qb12']),
            active_chain=args['active_chain'],branch=args['branch'],returned=ret['returned'],path_q12=ret['path_q12']))
    nodes=[];lookup={};edges=[];cursor=0;dense=[]
    for ei,(a,b)in enumerate(zip(ordered,ordered[1:])):
        chosen=None;consumed=[]
        for role,field in((0,'ik_q1_active'),(1,'ik_q2_active')):
            if chosen is not None:break
            if a[field]!=b[field]:continue
            require(cursor<len(attempts),'SOURCE_EXACT_MISSING_RECONSTRUCTION');attempt=attempts[cursor];consumed.append(cursor);cursor+=1
            require(key(attempt['qa12'])==key(a['q12'])and key(attempt['qb12'])==key(b['q12'])and attempt['active_chain']==role and attempt['branch']==a[field],
                'ORIGINAL_ROLE0_THEN_ROLE1_CALL_ORDER_CHANGED')
            if attempt['returned']:chosen=attempt
        require(chosen is not None,'SOURCE_EXACT_EDGE_LACKS_TRUE_DENSE_M')
        qs=chosen['path_q12'];require(len(qs)>=2 and chosen['active_chain']in(0,1)and chosen['branch']in range(8)
            and key(qs[0])==key(a['q12'])and key(qs[-1])==key(b['q12']),'COMPLETE_SUCCESSFUL_M_ENDPOINTS_REQUIRED')
        dense.extend(qs if not dense else qs[1:]);refs=[]
        for q in qs:
            packed=key(q)
            if packed not in lookup:lookup[packed]=len(nodes);nodes.append(q)
            refs.append(lookup[packed])
        leaves=[distance(x,y)for x,y in zip(qs,qs[1:])]
        require(all(v<LEAF_GATE for v in leaves),'FULL12_ORIGINAL_LEAF_DISTANCE_NOT_STRICT_POINT05')
        edges.append(dict(edge_index=ei,qa12=a['q12'],qb12=b['q12'],qa_motion_id=a['motion_id'],qb_motion_id=b['motion_id'],
            active_chain=chosen['active_chain'],branch=chosen['branch'],selected_attempt_index=chosen['attempt_index'],consumed_attempt_indices=consumed,
            node_ids=refs,leaf_distances_rad=leaves,edge_kind='actual_cross_tree_bridge'if ei==identity['source_bridge_milestone_edge_index']else
            'start_parent_to_child'if ei<identity['source_bridge_milestone_edge_index']else'goal_child_to_parent'))
    require(cursor==len(attempts),'UNMATCHED_EXTRA_SOURCE_RECONSTRUCTION')
    files={r['name']:r for r in d['native_file_evidence']};native=files['work/path.txt'];raw=bytes.fromhex(native['bytes_hex'])
    require(native['exists']and native['readback_bytes_saved']and native['original_final_bytes_readable']and len(raw)==native['bytes'],'ORIGINAL_FULL_PATH_FILE_BYTES_REQUIRED')
    lines=raw.decode('ascii').splitlines();require(lines[-1]==''and all(line.strip()for line in lines[:-1]),'ORIGINAL_ONE_TRAILING_EMPTY_LINE_REQUIRED');lines=lines[:-1];require(int(lines[0])==len(lines)-1==len(dense),'ORIGINAL_PATH_FILE_HEADER_AND_ROW_COUNT_REQUIRED')
    textq=[[float(v)for v in line.split()]for line in lines[1:]]
    require(all(len(q)==12 for q in textq),'ORIGINAL_PATH_FILE_FULL_Q12_ROWS_REQUIRED')
    # Author default ostream precision is six significant digits. This audits
    # display text only; all qualification inputs remain the exact trace values.
    require(all(x==float(format(y,'.6g'))for a,b in zip(textq,dense)for x,y in zip(a,b)),'ORIGINAL_TEXT_NOT_SOURCE_DENSE_M_SIX_SIGNIFICANT_DIGITS')
    require(set(i for e in edges for i in e['node_ids'])==set(range(len(nodes))),'FULL_UNIQUE_QUEUE_NOT_COVERED')
    return dict(nodes=nodes,edges=edges,source_identity_audit=identity,source_milestone_count=len(ms),source_attempt_count=len(attempts),
        all_original_attempts=attempts,original_dense_path_node_count=len(dense),original_dense_path_leaf_count=len(dense)-1,
        original_dense_node_ids=[lookup[key(q)]for q in dense],source_native_text_path_name=native['name'],
        source_native_text_precision_policy='Author six significant digits audited against original trace; qualification uses trace binary64.',
        full_queue_node_count=len(nodes),under_2048_full_queue_cap=len(nodes)<=MAX_NODES,
        deduplication='Physical query reuse only by complete packed big-endian binary64 q12 including signed zero; original identities/ordered path refs retained.',
        node_limit_policy='Keep complete exact queue; over2048 blocks execution without prefix/truncation/substitution.',
        independent_physical_queries_performed=0,independent_path_qualified=False,continuous_collision_certificate=False)
