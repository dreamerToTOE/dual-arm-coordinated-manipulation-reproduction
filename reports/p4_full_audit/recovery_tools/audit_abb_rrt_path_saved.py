#!/usr/bin/env python3
"""Independent stdlib-only saved-evidence review: no scientific module import."""
from pathlib import Path
import argparse,hashlib,json,math,struct,sys
P=argparse.ArgumentParser();P.add_argument('--root',type=Path,required=True);P.add_argument('--protocol',type=Path,required=True);P.add_argument('--output',type=Path,required=True);A=P.parse_args()
ROOT=A.root.resolve();RUN=ROOT/'results/p4_full/20261015_R2_ABB_RRT_PATH01'
def path(p):
 p=Path(p);return p if p.is_absolute() else ROOT/p
def sha(p):return hashlib.sha256(path(p).read_bytes()).hexdigest()
def read(p):return json.loads(path(p).read_text())
def bits(q):return struct.pack('>12d',*q)
checks=[]
def check(name,condition,**detail):checks.append({'check':name,'passed':bool(condition),**detail})
protocol=A.protocol.resolve();spec=read(protocol);execution=read(RUN/'execution.json');claim=read(execution['claim'])
check('frozen_protocol',spec['frozen'] is True and spec['run_id']=='20261015_R2_ABB_RRT_PATH01')
check('execution_and_claim_protocol_hash',execution['protocol_sha256']==sha(protocol)==claim['protocol_sha256'])
check('execution_claim_hash',execution['claim_sha256']==sha(execution['claim'])==execution['claim_after_sha256'])
check('protocol_after_hash',execution['protocol_after_sha256']==sha(protocol))
check('source_provenance_exact_match',execution['source_provenance']==spec['source_provenance'])
check('full_bound_before_after',execution['bound_files_sha256']==spec['bound_files_sha256']==execution['bound_files_after_sha256'])
changed={p:{'expected':h,'actual':sha(p)} for p,h in spec['bound_files_sha256'].items() if sha(p)!=h}
check('bound_files_still_unchanged',not changed,changes=changed)
q=spec['fixed_queue'];nodes=q['nodes'];edges=q['edges'];n=len(nodes)
check('full_queue_count',n==spec['full_queue_node_count']==execution['node_count']==execution['completed_nodes'])
check('no_unchecked_tail',execution['uncompleted_node_ids']==[] and execution['full_queue_checked'] is True)
check('resource_stop_not_used_as_truncation',n<=spec['max_nodes_per_execution']==2048)
check('all_nodes_qualified',execution['qualified_nodes']==n)
check('final_status',execution['status']=='PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH')
check('no_qualification_cleanup_error',execution.get('diagnostics')==[])
check('zero_solve_and_VI_and_formal',execution['solve_calls']==execution['formal_planning_calls']==execution['new_VI_candidate_constructions']==0)
source=read(spec['source_result']);se=read(spec['source_provenance']['execution']);sp=read(spec['source_provenance']['protocol'])
check('source_single_exact_nonapprox',source['exact'] is True and source['approximate'] is False and source['solve_calls']==1 and se['solve_dispatched']==1 and se['returncode']==0)
check('source_request_consistent',source['request']==sp['request']==se['driver_request']==spec['source_provenance']['request'])
check('source_result_bound_to_execution',sha(spec['source_result'])==se['result_sha256'])
check('source_request_fixed',source['request']['seed']==7 and source['request']['range_rad']==2.6 and source['request']['goal_bias']==.05 and source['request']['solve_seconds']==10.)
check('source_exact_endpoint_bits',bits(source['milestones_q12'][0])==bits(source['start_q12']) and bits(source['milestones_q12'][-1])==bits(source['goal_q12']))
check('node_dedup_binary64',len({bits(v) for v in nodes})==n)
check('all_dense_nodes_referenced',set(i for e in edges for i in e['node_ids'])==set(range(n)))
expected_assignments={i:[] for i in range(n)};max_leaf=0.
for k,e in enumerate(edges):
 chosen=source['reconstruction_attempts'][e['selected_attempt_index']]
 dense=[nodes[i] for i in e['node_ids']]
 check(f'edge_{k}_source_success_and_dense_exact',chosen['returned'] is True and [bits(v) for v in dense]==[bits(v) for v in chosen['path_q12']] and chosen['active_chain']==e['active_chain'] and chosen['branch']==e['branch'])
 check(f'edge_{k}_milestone_exact',bits(e['qa12'])==bits(source['milestones_q12'][k]) and bits(e['qb12'])==bits(source['milestones_q12'][k+1]) and bits(dense[0])==bits(e['qa12']) and bits(dense[-1])==bits(e['qb12']))
 leaves=[math.sqrt(math.fsum((a-b)**2 for a,b in zip(u,v))) for u,v in zip(dense,dense[1:])]
 check(f'edge_{k}_all_strict_full12_leaves',leaves==e['leaf_distances_rad'] and all(v<.05 for v in leaves))
 max_leaf=max(max_leaf,max(leaves))
 for i in set(e['node_ids']):expected_assignments[i].append((k,e['active_chain'],e['branch']))
raws=[];pqp=0;native_collisions=0;aligned_collisions=0;max_saved_pos=0.;max_saved_rot=0.;branch_combinations=set();minimum_limit_margin=math.inf
ELBOW=(1,-1,1,-1,1,-1,1,-1);WRIST=(1,-1,-1,1,-1,1,1,-1)
for i,inputq in enumerate(nodes):
 r=read(RUN/f'node_{i:05d}.json');raws.append(r)
 check(f'node_{i}_input_exact_and_pass',r['node_id']==i and bits(r['q12'])==bits(inputq) and r['qualified'] is True and r['math_qualified'] is True and r['stage']=='COMPLETED')
 check(f'node_{i}_partial_arm_records',read(RUN/f'node_{i:05d}_arm1.json')['poses']==r['poses'][:1] and read(RUN/f'node_{i:05d}_arm2.json')['poses']==r['poses'])
 mathrow=read(RUN/f'node_{i:05d}_math.json')
 check(f'node_{i}_pre_collision_math_preserved',all(mathrow[z]==r[z] for z in ['q12','poses','branches','closure','limits','edge_assignments','math_qualified']))
 p1,p2=r['poses'];savedpos=max(abs(p2[row][3]-(p1[row][3]+300.*p1[row][0])) for row in range(3))
 savedrot=max(abs(p2[row][col]-p1[row][col]*(-1 if col<2 else 1)) for row in range(3) for col in range(3))
 check(f'node_{i}_saved_pose_closure_consistency',abs(savedpos-r['closure']['position_max_abs'])<=1e-10 and abs(savedrot-r['closure']['rotation_matrix_max_abs'])<=1e-12 and savedpos<=1e-5 and savedrot<=1e-5)
 max_saved_pos=max(max_saved_pos,savedpos);max_saved_rot=max(max_saved_rot,savedrot)
 low=[-165,-110,-110,-160,-120,-400]*2;high=[165,110,70,160,120,400]*2
 bounds=[(a*3.1416/180,b*3.1416/180) for a,b in zip(low,high)]
 check(f'node_{i}_original_mechanical_bounds',r['limits']['legal'] is True and r['limits']['violations']==[] and all(a<=v<=b for v,(a,b) in zip(inputq,bounds)))
 minimum_limit_margin=min(minimum_limit_margin,min(min(v-a,b-v) for v,(a,b) in zip(inputq,bounds)))
 for arm,b in enumerate(r['branches']):
  possible=[z for z in range(8) if (b['shoulder_sign'] is None or (1 if z<4 else -1)==b['shoulder_sign']) and (b['elbow_sign'] is None or ELBOW[z]==b['elbow_sign']) and (b['wrist_sign'] is None or WRIST[z]==b['wrist_sign'])]
  check(f'node_{i}_arm{arm+1}_saved_branch_sign_logic',possible==b['branch_set'])
  branch_combinations.add(tuple(b['branch_set']))
 assignments=r['edge_assignments']
 check(f'node_{i}_complete_edge_assignment_membership',[(a['edge'],a['role'],a['requested_branch']) for a in assignments]==expected_assignments[i] and all(a['branch_pass'] is True and a['requested_branch'] in r['branches'][1-a['role']]['branch_set'] for a in assignments))
 c=r['collision'];check(f'node_{i}_raw_collision_saved_before_interpretation',read(RUN/f'node_{i:05d}_collision_response.json')==c)
 check(f'node_{i}_aligned_collision_gate',c['status']=='CHECKED' and c['selected_variant']=='aligned' and c['collision'] is False and c['manifest_sha256']==spec['bound_files_sha256'][str(path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'))] and set(c['variants'])=={'native','aligned'})
 for variant,row in c['variants'].items():
  codes=row['query_codes'];pqp+=len(codes)
  check(f'node_{i}_{variant}_all_query_codes',bool(codes) and all(type(v) is int and v==0 for v in codes))
  if variant=='native':native_collisions+=bool(row['native_collision'])
  else:
   aligned_collisions+=bool(row['native_collision'])
   check(f'node_{i}_aligned_pose_capture_consistency',row['pose_consistency']['passed'] is True and all(e['translation_maxabs_mm']<=1e-5 and e['rotation_maxabs']<=1e-5 for e in row['pose_consistency']['errors']))
counts=execution['counts'];expectedcounts={'math_arm_FK_started':2*n,'math_arm_FK_completed':2*n,'branch_identity_started':2*n,'branch_identity_completed':2*n,'collision_calls_started':n,'collision_calls_completed':n,'adapter_internal_arm_FK_J_started':4*n,'adapter_internal_arm_FK_J_completed':4*n,'PQP_queries':pqp}
check('all_call_counts_saved_only',all(counts.get(k)==v for k,v in expectedcounts.items()),expected=expectedcounts,actual=counts)
events=[json.loads(l) for l in (RUN/'events.jsonl').read_text().splitlines() if l.strip()];ec={name:sum(e['event']==name for e in events) for name in ('math_node_started','math_node_completed','math_arm_FK_started','math_arm_FK_completed','adapter_internal_FK_J_started','adapter_internal_FK_J_completed','collision_started','collision_response_retained','node_completed','stopped')}
check('events_correspond_to_all_counts',all(ec[k]==v for k,v in {'math_node_started':n,'math_node_completed':n,'math_arm_FK_started':2*n,'math_arm_FK_completed':2*n,'adapter_internal_FK_J_started':4*n,'adapter_internal_FK_J_completed':4*n,'collision_started':n,'collision_response_retained':n,'node_completed':n,'stopped':0}.items()),event_counts=ec)
check('resource_caps_true_actual',0<=execution['wall_s']<min(120.,3600.-spec['previous_r2_wall_s']) and 0<=execution['cpu_s']<min(240.,7200.-spec['previous_r2_cpu_s']))
prior=[read(p) for p in spec['prior_executions']]
check('prior_ledger_fsum',spec['previous_r2_wall_s']==math.fsum(p['wall_s'] for p in prior) and spec['previous_r2_cpu_s']==math.fsum(p['cpu_s'] for p in prior))
check('no_stopped_partial_node_files',not list(RUN.glob('node_*_stopped_partial.json')))
check('exact_final_node_file_count',len([p for p in RUN.glob('node_*.json') if len(p.stem)==10])==n)
out={'schema':'P4_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW','new_scientific_calls':0,'compile_calls':0,'saved_only':True,'root':str(ROOT),'protocol':str(protocol),'protocol_sha256':sha(protocol),'execution':str((RUN/'execution.json').relative_to(ROOT)),'execution_sha256':sha(RUN/'execution.json'),'claim_sha256':sha(execution['claim']),'review_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'passed':all(c['passed'] for c in checks),'check_count':len(checks),'failed_checks':[c for c in checks if not c['passed']],'summary':{'nodes':n,'edges':len(edges),'milestones':len(source['milestones_q12']),'source_exact_nonapprox':True,'max_leaf_rad':max_leaf,'max_saved_pose_closure_position_mm':max_saved_pos,'max_saved_pose_closure_rotation':max_saved_rot,'minimum_mechanical_limit_margin_rad':minimum_limit_margin,'branch_sets_encountered':[list(v) for v in sorted(branch_combinations)],'native_collision_nodes':native_collisions,'aligned_collision_nodes':aligned_collisions,'PQP_queries':pqp,'counts':counts,'wall_s':execution['wall_s'],'cpu_s':execution['cpu_s'],'bound_asset_count':len(spec['bound_files_sha256'])},'limitations':['Saved physical poses and branch-factor records checked; no new FK/J/IK/NR or collision evaluation.','Discrete source-policy qualification only; no CCD/full solid rod/omitted-pair certificate.','No global statistical or PCS-advantage claim.'],'checks':checks}
with A.output.open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({k:out[k] for k in ['passed','check_count','failed_checks','summary']},ensure_ascii=False));sys.exit(0 if out['passed'] else 2)
