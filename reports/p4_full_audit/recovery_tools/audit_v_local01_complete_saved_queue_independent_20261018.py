#!/usr/bin/env python3
"""Personnel-independent saved-only queue review; never import model/materializer."""
from pathlib import Path
from collections import Counter, defaultdict
import ast
import hashlib
import json
import math
import struct

ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'results/p4_full/20261018_R2_D080_V_PCS_LOCAL01'
SRC='scripts/p4_d080/materialize_v_pcs_local01_saved_queue_v1_draft.py'
SRC_SHA='c8d9e38b0354d64276fbfc15f47748ec58aa9be12bf862557325acab3a4e44c7'
QUEUE='configs/p4_d080/v_pcs_local01_complete_saved_queue_v1.DRAFT.json'
QUEUE_SHA='6fa6da08e32e92068bad12346e14cf4d68440c6c205147937ea8c912daec8e35'
PRE='reports/P4_D080_ENV_V_PCS_LOCAL01_SAVED_QUEUE_PRE_DRAFT_20261018.md'
PRE_SHA='03cdcbf00ed143ad8f8e0b61dbd830cfec862205546347987e3c3dc5f2c24c34'
POST='reports/P4_D080_ENV_V_PCS_LOCAL01_SAVED_INDEPENDENT_POST_20261018.json'
POST_SHA='06c1a4c82db1accd7900b26e78c7bc84ebed33948e0b7d1d734aef877e00ac49'
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_LOCAL01_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_20261018.json'
checks=[];retained={}
def raw(p):
 p=Path(p);p=p if p.is_absolute()else ROOT/p;b=p.read_bytes();h=hashlib.sha256(b).hexdigest();assert retained.setdefault(str(p),h)==h;return b
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def load(p):return json.loads(raw(p))
def ck(n,v):checks.append(dict(check=n,passed=bool(v)))
def packed(q):
 assert len(q)==12 and all(type(v)in(int,float)and math.isfinite(v)for v in q)
 return struct.pack('>12d',*q).hex()
def same(a,b):
 if type(a)in(int,float)and type(b)in(int,float):return struct.pack('>d',a)==struct.pack('>d',b)
 if type(a)is not type(b):return False
 if isinstance(a,dict):return set(a)==set(b)and all(same(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b
def dist(a,b):return math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,b)))

def audit():
 q=load(QUEUE);post=load(POST);e=load(RUN/'execution.json');tree=ast.parse(raw(SRC))
 ck('exact reviewed inputs and personnel independent source transport194 reused',sha(SRC)==SRC_SHA and sha(QUEUE)==QUEUE_SHA and sha(PRE)==PRE_SHA and sha(POST)==POST_SHA and post['checks_total']==post['checks_passed']==194 and post['checks_failed']==0 and post['personnel_independent']is post['source_transport_qualified']is True and post['independent_local_qualified']is post['independent_path_qualified']is False)
 imports=[]
 for n in ast.walk(tree):
  if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
  elif isinstance(n,ast.ImportFrom):imports.append(n.module)
 ck('materializer imports stdlib only no dynamic/model/process execution',set(imports)<={'__future__','argparse','collections','hashlib','json','math','pathlib','struct'}and not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in('eval','exec','__import__','compile')for n in ast.walk(tree)))
 ck('draft only no physical/planning/formal authorization',q['schema']=='P4_D080_V_PCS_LOCAL01_SAVED_COMPLETE_QUEUE_DRAFT_V1'and q['status']=='DRAFT_SAVED_ONLY_PENDING_INDEPENDENT_PHYSICAL_FREEZE'and q['frozen']is q['executable']is q['independent_local_qualified']is q['independent_path_qualified']is q['continuous_collision_certificate']is False and all(q[k]==0 for k in('independent_model_calls','binary_calls','solve_calls','new_VI_candidate_constructions','formal_table_I_calls')))
 ck('source identity and exact hashes bound to existing approved transport',sha(RUN/'execution.json')==q['source_execution_sha256']==post['execution_sha256']and q['source_commit']==e['source_commit']and q['source_protocol']==e['protocol']and q['source_protocol_sha256']==e['protocol_sha256']and q['materializer_source_sha256']==SRC_SHA and all(sha(n)==h for n,h in q['saved_inputs_sha256'].items()))
 # Parent and public identities derive from the original stderr temporal tree,
 # independently of the materializer implementation or its stored queue.
 rows=load(RUN/'trace/parsed_rows.json');observed={r['id']:r for row in rows for r in row['observed_records']}
 parents={};children=defaultdict(list);publics={};stack=[];entered={};completed={}
 events=[json.loads(line[len(b'P4_V_PCS_TRACE '):])for line in raw(RUN/'process0_stderr.bin').splitlines()if line.startswith(b'P4_V_PCS_TRACE ')]
 for ev in events:
  ident=ev['id']
  if ev['event']=='entered':
   assert ident not in entered and ident==len(entered)+1
   parent=stack[-1]if stack else None;parents[ident]=parent
   if parent is not None:children[parent].append(ident)
   publics[ident]=ident if ev['kind']=='public_request'else publics.get(parent)
   entered[ident]=ev;stack.append(ident)
  else:
   assert ev['event']=='completed'and stack.pop()==ident and ident not in completed
   completed[ident]=ev
 ck('complete3309 temporal parent tree exact original saved194 lifetimes',not stack and len(entered)==len(completed)==len(observed)==3309 and all(same(observed[i]['args'],entered[i]['args'])and same(observed[i]['result'],completed[i]['result'])and observed[i]['kind']==entered[i]['kind']==completed[i]['kind']for i in observed))
 def role(ident):
  while ident is not None:
   a=observed[ident]['args']
   if 'active_chain'in a:return a['active_chain'],a.get('branch')
   ident=parents[ident]
  return None,None
 def identity(i):
  r=observed[i];a,b=role(i)
  return dict(source_record_id=i,parent_trace_id=parents[i],public_record_id=publics[i],kind=r['kind'],active_chain=a,requested_branch=b,modes=['trace','plain'])
 nodes=q['nodes'];bykey={packed(n['q12']):n for n in nodes};byid={n['node_id']:n for n in nodes}
 ck('24 finite unique exact binary64 nodes IDs and no truncation',len(bykey)==len(byid)==len(nodes)==24 and set(byid)==set(range(24))and all(n['binary64_be_key']==packed(n['q12'])and n['qualification_status']=='NOT_EXECUTED'for n in nodes)and len(nodes)<=256)
 expected_refs=defaultdict(list);expected_assign=defaultdict(list);expected_union=set()
 def expect(v,i,occ,extra=None):
  k=packed(v);expected_union.add(k);a,b=role(i);r=observed[i];pub=observed.get(publics[i]);kw={}if extra is None else extra
  for mode in('trace','plain'):expected_refs[k].append(dict(mode=mode,public_request_id=None if pub is None else pub['args']['id'],source_record_id=i,parent_trace_id=parents[i],kind=r['kind'],occurrence=occ,active_chain=a,requested_branch=b,source_returned=r['result'].get('returned'),**kw))
  if a is not None:
   assignment=dict(active_chain=a,passive_arm=2-a,requested_branch=b)
   if assignment not in expected_assign[k]:expected_assign[k].append(assignment)
  return bykey[k]['node_id']
 paths=[];leaves=[];collisions=[];failures=[];public=[];success=set();arithmetic_diffs=[];arithmetic_ulps=[]
 for i,r in observed.items():
  kind=r['kind'];a=r['args'];z=r['result'];returned=z.get('returned');iden=identity(i)
  if returned is False or(kind=='collision'and returned!=0)or z.get('source_call_started')is False:failures.append(dict(iden,args=a,result=z))
  if kind in('project_fixed','is_valid_rbs')and returned is True:expect(z['q12'],i,'SUCCESSFUL_SOURCE_OUTPUT');success.add(packed(z['q12']))
  if kind=='reconstruct':
   qs=z['path_q12'];ids=[expect(v,i,'ALL_SOURCE_RECONSTRUCT_M',dict(path_index=j))for j,v in enumerate(qs)];ds=[dist(x,y)for x,y in zip(qs,qs[1:])]
   saved=next(v for v in q['all_reconstruct_paths']if v['source_record_id']==i)
   arithmetic_diffs.extend(abs(x-y)for x,y in zip(ds,saved['adjacent_full12_L2_rad']))
   arithmetic_ulps.extend(abs(x-y)/math.ulp(y)for x,y in zip(ds,saved['adjacent_full12_L2_rad']))
   paths.append(dict(iden,returned=returned,ordered_node_ids=ids,all_adjacent_strict_lt05=all(v<.05 for v in ds),path_status='SOURCE_TRUE_PENDING_PHYSICAL'if returned else'SOURCE_FALSE_PARTIAL_M_NOT_ACCEPTED'))
  if kind in('rbs','reconstruct')and returned is True and not any(observed[c]['kind']==kind for c in children[i]):
   ds=dist(a['qa12'],a['qb12']);ids=[expect(a['qa12'],i,'SOURCE_TRUE_RECURSIVE_LEAF_A'),expect(a['qb12'],i,'SOURCE_TRUE_RECURSIVE_LEAF_B')];leaves.append(dict(iden,node_ids=ids,strict_lt05=ds<.05))
   saved=next(v for v in q['recursive_true_leaves']if v['source_record_id']==i);arithmetic_diffs.append(abs(ds-saved['full12_L2_rad']))
   arithmetic_ulps.append(abs(ds-saved['full12_L2_rad'])/math.ulp(saved['full12_L2_rad']))
  if kind=='collision':
   nid=expect(a['q12'],i,'ORIGINAL_COLLISION_INPUT',dict(collision_returned=returned));collisions.append(dict(iden,node_id=nid,source_collision_returned=returned,source_rejected=returned!=0,source_pair_count=len(z['active_pairs']),source_result=z))
  if kind=='public_request':
   item=dict(iden,request=a,result_status=z.get('status','SOURCE_CALL_COMPLETED'),returned=returned,resolved_branch=z.get('resolved_branch'),source_result=z)
   if'q12'in z:item['output_binary64_be_key']=packed(z['q12'])
   if'path_q12'in z:item['path_binary64_be_keys']=[packed(v)for v in z['path_q12']]
   public.append(item)
 ck('complete original union and both-mode occurrence provenance role branch exact',expected_union==set(bykey)==success and all(same(n['source_occurrences'],expected_refs[k])and same(n['role_branch_assignments'],expected_assign[k])for k,n in bykey.items()))
 ck('requested roles branches match actual public fixed resolved identities',all(a['active_chain']in(0,1)and type(a['requested_branch'])is int and 0<=a['requested_branch']<=7 for n in nodes for a in n['role_branch_assignments'])and all(ref['requested_branch']==observed[publics[ref['source_record_id']]]['result']['resolved_branch']for n in nodes for ref in n['source_occurrences']))
 ck('all29 recursive M including false partial ordered nodes retained without acceptance',len(paths)==29 and len({n for p in paths for n in p['ordered_node_ids']})==20 and all(same(p,{k:v for k,v in s.items()if k!='adjacent_full12_L2_rad'})for p,s in zip(paths,q['all_reconstruct_paths']))and all(p['path_status']=='SOURCE_FALSE_PARTIAL_M_NOT_ACCEPTED'for p in paths if p['returned']is False))
 ck('24 true recursive leaf source identities and exact endpoints all strict gate',len(leaves)==24 and all(p['strict_lt05']for p in leaves)and all(same(p,{k:v for k,v in s.items()if k!='full12_L2_rad'})for p,s in zip(leaves,q['recursive_true_leaves'])))
 # Independent fsum may round one ULP differently from sum; this reviewer
 # reports that numerical difference instead of altering source saved values.
 ck('independent full12 fsum arithmetic agrees within4ULP; scientific strict05 predicates unchanged',bool(arithmetic_ulps)and max(arithmetic_ulps)<=4)
 reject=[x for x in collisions if x['source_rejected']]
 ck('all34 collision occurrences87pairs and six rejects three unique retained',len(collisions)==34 and len({x['node_id']for x in collisions})==17 and len(reject)==6 and len({x['node_id']for x in reject})==3 and all(x['source_pair_count']==87 for x in collisions)and same(collisions,q['all_original_collision_occurrences'])and same(reject,q['rejected_collision_occurrences'])and q['rejected_collision_node_ids']==sorted({x['node_id']for x in reject}))
 ck('all62 original failure identities args results preserved',len(failures)==62 and same(failures,q['all_failure_identities']))
 ck('all18 public identities preserve7true7false2identify2dependency',len(public)==18 and same(public,q['all_public_request_identities'])and sum(x['returned']is True for x in public)==7 and sum(x['returned']is False for x in public)==7 and sum(x['result_status']=='NOT_EXECUTED_DEPENDENCY_FAILED'for x in public)==2)
 pending=load(RUN/'independent_nodes_PENDING.json');s=q['stats']
 ck('pending24 and all output summary counts recomputed exactly',success==set(pending['nodes'])and s==dict(unique_nodes=24,original_pending_success_nodes=24,all_reconstruct_records=29,all_reconstruct_unique_nodes=20,true_recursive_leaves=24,all_true_leaf_distances_strict_lt05=True,collision_records_per_mode=34,collision_unique_nodes=17,rejected_collision_records_per_mode=6,rejected_collision_unique_nodes=3,source_failure_identities_per_mode=62,public_requests_per_mode=18,public_outcomes=dict(Counter(x['result_status']if x['returned']is None else'SOURCE_TRUE'if x['returned']else'SOURCE_FALSE'for x in public)),source_lifetimes_per_mode=3309,physical_node_limit=256,complete_union_under_limit=True))
 for n,h in retained.items():assert hashlib.sha256(Path(n).read_bytes()).hexdigest()==h
 return dict(stats=s,maximum_independent_fsum_vs_saved_distance_difference_rad=max(arithmetic_diffs),maximum_independent_fsum_vs_saved_distance_difference_ULP=max(arithmetic_ulps),source_projection_true=7,source_projection_false=1,source_public_RBS_true=0,source_public_RBS_false=3,source_public_RBS_dependency_not_executed=1,source_public_reconstruct_true=0,source_public_reconstruct_false=3,source_public_reconstruct_dependency_not_executed=1)

def main():
 if OUT.exists()or OUT.with_suffix('.md').exists():raise FileExistsError('EXCLUSIVE_SAVED_QUEUE_REVIEW')
 details={}
 try:details=audit()
 except BaseException as exc:ck('saved audit structural completion '+repr(exc),False)
 failures=[x for x in checks if not x['passed']]
 report=dict(schema='P4_D080_V_PCS_LOCAL01_COMPLETE_QUEUE_SAVED_PERSONNEL_INDEPENDENT_PRE_V1',status='PASS_SAVED_QUEUE_ONLY_PENDING_PHYSICAL_PROTOCOL'if not failures else'FAIL_SAVED_QUEUE_STATIC_RETAINED',personnel_independent=True,reviewer='/root/sbl_independent_resume independent of materializer author',checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),checks=checks,failures=failures,materializer=SRC,materializer_sha256=SRC_SHA,queue=QUEUE,queue_sha256=QUEUE_SHA,PRE=PRE,PRE_sha256=PRE_SHA,reused_source_transport194=POST,reused_source_transport194_sha256=POST_SHA,independent_local_qualified=False,independent_path_qualified=False,continuous_collision_certificate=False,new_model_compile_binary_FK_J_IK_NR_PQP_RBS_RNG_solve_VI_formal_calls=0,scientific_budget_charge=0,execution_authorized=False,retained_sha256=retained,**details,limits=['Complete saved queue only; no independent Comau physical node or collision query run.','Three false root connections and reconstructions, one dependency pair and all old failures remain false/not executed.','True recursive subleaves are not successful public connections or global paths.','Separate frozen physical protocol and resource supervision required before physical qualification.'])
 with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
 with OUT.with_suffix('.md').open('x')as f:f.write('# V LOCAL01 完整保存队列独立增量审查\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'。\n\n完整24点union、3309 temporal parents、双模式原引用、29次false部分M、24条true递归子叶、34次碰撞与62项失败保留。只读数组算术；未执行FK/IK/碰撞/模型/编译/规划。独立物理及完整路径资格仍false；本证书不授权科学执行。\n')
 print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures),failures=failures)))
 if failures:raise SystemExit(2)
if __name__=='__main__':main()
