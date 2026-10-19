#!/usr/bin/env python3
"""Verify complete original saved M with an independent array traversal; no model imports."""
import ast
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[3]
def p(n):
    q=Path(n);return q if q.is_absolute() else ROOT/q
def raw(n):return p(n).read_bytes()
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def js(n):return json.loads(raw(n))
def key(q):return struct.pack('>12d',*q)
QUEUE='configs/p4_d080/iii_rrt_pcs_source01_complete_saved_queue_v1.DRAFT.json'
HELPER='scripts/p4_d080/materialize_iii_rrt_pcs_source01_saved_v1_draft.py'
BASE='scripts/qualify_p4_full_r2_abb_rrt_path.py'
EP='results/p4_full/20261018_R2_D080_III_RRT_PCS_SOURCE01/execution.json'
POST='reports/P4_D080_ENV_III_RRT_PCS_SOURCE01_SAVED_INDEPENDENT_POST_20261018.json'
SOURCE='results/p4_full/20261018_R2_D080_III_RRT_PCS_SOURCE01/runtime/result.json'
q=js(QUEUE);d=js(SOURCE);e=js(EP);post=js(POST);fq=q['fixed_queue'];checks=[]
def ck(n,v,ev=None):checks.append(dict(name=n,passed=bool(v),evidence=ev))
bt=ast.parse(raw(BASE));ht=ast.parse(raw(HELPER))
ck('three_pure_functions_exact_original_source_segments_no_model_import',all(ast.get_source_segment(raw(BASE).decode(),next(z for z in bt.body if isinstance(z,ast.FunctionDef) and z.name==n))==ast.get_source_segment(raw(HELPER).decode(),next(z for z in ht.body if isinstance(z,ast.FunctionDef) and z.name==n)) for n in ['q12','key','materialize']) and sha(HELPER)=='534d1a6571a2e1c8ca13afee7e90316a3f66734bb21666de499e11c9949106bb' and sha(BASE)=='bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865')
ck('exact_actual_source_POST25_and_execution_links',q['source_execution_sha256']==sha(EP)=='f9229c0c2b768f76f540e4667545b09d2b1c425957817cb0a284f696760f39b0' and q['source_independent_POST_sha256']==sha(POST)=='be8a4f2d3ec4b095f34c409d980e6c7d511a5f417594b3d29893e6607e941418' and post['checks_total']==post['checks_passed']==25 and post['personnel_independent'] is post['external_supervision_qualified'] is True and e['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT' and e['solve_calls_from_result']==1)
allqs=[];lookup={};refs=[];selected=[];consumed=[];distances=[];cursor=0;edge_ok=True;assignments={}
for index,(a,b) in enumerate(zip(d['milestones_q12'],d['milestones_q12'][1:])):
    used=[];chosen=None
    while cursor<len(d['reconstruction_attempts']):
        row=d['reconstruction_attempts'][cursor];used.append(cursor);cursor+=1
        if key(row['qa12'])!=key(a) or key(row['qb12'])!=key(b):edge_ok=False
        if row['returned'] is True:chosen=row;break
    if chosen is None:raise ValueError('ORIGINAL_DENSE_EDGE_MISSING_SUCCESS')
    indices=[]
    for node in chosen['path_q12']:
        packed=key(node)
        if packed not in lookup:lookup[packed]=len(allqs);allqs.append(node)
        ident=lookup[packed];indices.append(ident);assignments.setdefault(ident,set()).add((chosen['active_chain'],chosen['branch']))
    leaves=[math.hypot(*(u-v for u,v in zip(left,right))) for left,right in zip(chosen['path_q12'],chosen['path_q12'][1:])]
    edge=fq['edges'][index]
    edge_ok=edge_ok and edge['edge_index']==index and key(edge['qa12'])==key(a) and key(edge['qb12'])==key(b) and edge['node_ids']==indices and edge['active_chain']==chosen['active_chain'] and edge['branch']==chosen['branch'] and edge['selected_attempt_index']==chosen['attempt_index'] and edge['consumed_attempt_indices']==used and len(edge['leaf_distances_rad'])==len(leaves) and all(abs(x-y)<=8*math.ulp(max(abs(x),abs(y))) for x,y in zip(leaves,edge['leaf_distances_rad'])) and len(indices)>=2 and key(chosen['path_q12'][0])==key(a) and key(chosen['path_q12'][-1])==key(b)
    selected.append(chosen['attempt_index']);consumed.extend(used);refs.extend(indices);distances.extend(leaves)
ck('independent_first_true_full_original_M_all14edges16attempts_preserved',edge_ok and cursor==len(d['reconstruction_attempts'])==16 and len(fq['edges'])==14 and consumed==list(range(16)) and len(selected)==14 and q['all_false_attempts_retained_in_source'] is True,{'selected_attempt_indices':selected,'false_attempts':[z['attempt_index'] for z in d['reconstruction_attempts'] if not z['returned']]})
ck('exact649binary64_unique_nodes_all_refs_no_missing_tail_or_invented_nodes',len(allqs)==q['full_queue_node_count']==len(fq['nodes'])==649 and [key(z) for z in allqs]==[key(z) for z in fq['nodes']] and set(refs)==set(range(649)) and len({key(z) for z in fq['nodes']})==649 and fq['source_milestone_count']==15 and fq['source_attempt_count']==16)
ck('all_original_full12_leaves_strict_point05_independent_hypot',bool(distances) and max(distances)<.05 and q['entire_queue_under_resource_limit'] is True and q['max_nodes_per_execution']==2048,{'leaves':len(distances),'max_full12_L2_rad':max(distances),'role_branch_assignments':sum(len(z) for z in assignments.values())})
tree=d['planner_data'];vs={z['index']:z for z in tree['vertices']};links={tuple(z) for z in tree['edges']};chain=fq['source_tree_vertex_path']
ck('complete15milestone_source_PlannerData_chain_identity',len(chain)==15 and all(key(vs[i]['q12'])==key(z) for i,z in zip(chain,d['milestones_q12'])) and vs[chain[0]]['start'] is True and vs[chain[-1]]['goal'] is True and all((a,b) in links for a,b in zip(chain,chain[1:])))
ck('bound_saved_source_bytes_and_draft_only_no_scientific_qualification',all(sha(n)==v for n,v in q['bound_files_sha256'].items()) and q['frozen'] is q['executable'] is q['independent_path_qualified'] is q['continuous_collision_certificate'] is False and q['new_binary_model_scientific_calls']==q['new_VI_candidate_constructions']==q['formal_table_I_calls']==0 and q['materialization_error'] is None)
failed=[z for z in checks if not z['passed']]
report={'schema':'P4_D080_III_RRT_PCS_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_V1','personnel_independent':True,'status':'PASS_COMPLETE_SAVED649_QUEUE_ONLY' if not failed else 'FAIL_SAVED_QUEUE','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'queue':QUEUE,'queue_sha256':sha(QUEUE),'source_execution_sha256':sha(EP),'source_POST_sha256':sha(POST),'materializer_sha256':sha(HELPER),'auditor_sha256':sha(__file__),'new_model_binary_scientific_calls':0,'saved_materializer_execution_count':1,'full_queue_nodes':649,'full_path_edges':14,'full_leaves':len(distances),'all_node_role_branch_assignments':sum(len(z) for z in assignments.values()),'independent_path_qualified':False,'continuous_collision_certificate':False,'limits':['Complete saved original M and fallback bookkeeping only; no FK/branch/limit/PQP or continuous collision evidence yet.','Original14true/2false preserved; no new interpolation, point, seed or solve.','Full649 queue under2048 resource cap does not itself authorize physical execution.']}
out=ROOT/'reports/P4_D080_ENV_III_RRT_PCS_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_20261018.json'
with out.open('x') as stream:stream.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'failed':failed,'sha256':sha(out),'queue_sha256':sha(QUEUE),'nodes':649,'leaves':len(distances)},ensure_ascii=False,indent=2))
