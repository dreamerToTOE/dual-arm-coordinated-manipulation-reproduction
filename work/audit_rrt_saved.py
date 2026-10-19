import hashlib,json,math,re,subprocess
from pathlib import Path
R=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
run=R/'results/p4_full/20261015_R2_ABB_RRT_PCS_E2E01'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hashes(d):
 for name,want in d.items():
  p=Path(name);p=p if p.is_absolute() else R/p
  assert sha(p)==want,(str(p),want,sha(p))
 return len(d)
e=load(run/'execution.json');p=load(e['protocol']);m=load(e['build_manifest']);x=load(run/'runtime/result.json')
counts={}
for key in ['build_assets_before_sha256','build_assets_after_sha256','own_source_sha256','own_source_after_sha256','endpoint_sources_after_sha256','retained_run_files_sha256','prior_execution_sha256']:
 counts[key]=hashes(e[key])
assert e['build_assets_before_sha256']==e['build_assets_after_sha256']
for record in [e,m]:
 for key in ['protocol','claim','binary']:
  f=Path(record[key]);f=f if f.is_absolute() else R/f
  assert sha(f)==record[key+'_sha256']
 for name,want in record['own_source_sha256'].items():
  blob=subprocess.check_output(['git','show',record['source_commit']+':'+name],cwd=R)
  assert hashlib.sha256(blob).hexdigest()==want
assert sha(e['build_manifest'])==e['build_manifest_sha256']
me=load(R/m['engineering_execution']);assert me.pop('external_manifest')==e['build_manifest'];assert me.pop('manifest_sha256')==e['build_manifest_sha256'];mm=dict(m);mm.pop('engineering_execution');assert me==mm
hashes(m['template_assets_sha256']);assert m['template_assets_sha256']==m['template_assets_after_sha256']
assert p['frozen'] and all(p['reviews'].values()) and p['prior_execution_sha256']==e['prior_execution_sha256']
assert p['own_source_sha256']==e['own_source_sha256']
assert e['driver_request']==x['request']==load(run/'driver_request.json')==load(run/'runtime/request_observed.json')
assert e['driver_request']==p['request']
assert e['source_commit']=='1a5b811b61be61dea80f8183f123379d167fd3f0'
assert sha(e['result'])==e['result_sha256']
priors=[load(R/f) for f in e['prior_execution_sha256']]
assert math.fsum(t['wall_s'] for t in priors)==e['previous_r2_wall_s']
assert math.fsum(t['cpu_s'] for t in priors)==e['previous_r2_cpu_s']
O=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/geometry_consistent_plain')
N=Path(e['binary']).parent
old=(O/'validity_checkers/StateValidityCheckerPCS.cpp').read_text();new=(N/'validity_checkers/StateValidityCheckerPCS.cpp').read_text()
sigs=[('bool StateValidityChecker::reconstructRBS(const ob::State *s1, const ob::State *s2, Matrix &Confs, int active_chain, int ik_sol)','\n const bool p4_return=[&]() -> bool {','}();\n p4e2e::observe_reconstruction(s1,s2,active_chain,ik_sol,Confs,p4_return);\n return p4_return;\n'),('State StateValidityChecker::identify_state_ik(State q1, State q2, State ik)','\n const State p4_input_ik=ik;\n State p4_return=[&]() -> State {','}();\n p4e2e::observe_identify(q1,q2,p4_input_ik,p4_return);\n return p4_return;\n')]
def body(s,sig):
 mask=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda z:' '*len(z.group()),s,flags=re.S)
 a=mask.index('{',s.index(sig));d=1;b=a+1
 while d:
  d+=(mask[b]=='{')-(mask[b]=='}');b+=1
 return s[a+1:b-1]
body_hash={}
for sig,prefix,suffix in sigs:
 b=body(old,sig);wrapped=prefix+b+suffix
 assert new.count(wrapped)==1
 assert body(new,sig)==wrapped
 new=new.replace(wrapped,b)
 body_hash[sig]=hashlib.sha256(b.encode()).hexdigest()
assert new==old
assert (N/'planners/RRT_PCS.cpp').read_bytes()==(O/'planners/RRT_PCS.cpp').read_bytes().replace(b'std::remove("./paths/temp.txt");',b'/* P4 I/O observation: retain ./paths/temp.txt verbatim. */')
for rel in ['proj_classes/apc_class.cpp','validity_checkers/collisionDetection.cpp']:
 assert (O/rel).read_bytes()==(N/rel).read_bytes()
tr=[json.loads(t) for t in (run/'runtime/reconstruction_attempts.jsonl').read_text().splitlines()];ids=[json.loads(t) for t in (run/'runtime/identify_observations.jsonl').read_text().splitlines()]
assert tr==x['reconstruction_attempts'];assert len(tr)==x['reconstruction_calls_completed_observed']==3
assert len(ids)==x['identify_observation_count']==x['identify_calls_completed_observed']==11
assert all(a['attempt_index']==i for i,a in enumerate(tr));assert all(a['call_index']==i for i,a in enumerate(ids))
mil=x['milestones_q12'];dense=[];stats=[]
assert mil[0]==x['start_q12'] and mil[-1]==x['goal_q12']
for i,a in enumerate(tr):
 q=a['path_q12'];assert a['returned'] is True and a['qa12']==mil[i] and a['qb12']==mil[i+1]
 assert q[0]==a['qa12'] and q[-1]==a['qb12']
 assert all(len(v)==12 and all(math.isfinite(z) for z in v) for v in q)
 ds=[math.dist(v,w) for v,w in zip(q,q[1:])];assert max(ds)<.05
 dense.extend(q if i==0 else q[1:]);stats.append({'edge':i,'active_chain':a['active_chain'],'branch':a['branch'],'nodes':len(q),'min_leaf_l2':min(ds),'max_leaf_l2':max(ds),'endpoint_l2':math.dist(q[0],q[-1])})
assert len(dense)==177 and len(set(map(tuple,dense)))==177
pd=x['planner_data'];vs=pd['vertices'];edges=pd['edges'];assert len(vs)==pd['num_vertices']==6 and len(edges)==pd['num_edges']==5
assert [v['index'] for v in vs]==list(range(6));assert edges==[[1,2],[2,3],[2,4],[2,5],[5,0]]
pathids=[next(v['index'] for v in vs if v['q12']==q) for q in mil];assert pathids==[1,2,5,0]
assert all([a,b] in edges for a,b in zip(pathids,pathids[1:]))
assert vs[pathids[0]]['start'] and vs[pathids[-1]]['goal']
children=[b for a,b in edges];assert sorted(children)==[0,2,3,4,5]
seen={1}
for _ in range(len(vs)):
 seen|={b for a,b in edges if a in seen}
assert seen==set(range(6))
raw=[z for z in (run/'runtime/paths/path.txt').read_text().splitlines() if z.strip()];assert int(raw[0])==177 and len(raw)==178
assert [[float(t) for t in s.split()] for s in raw[1:]]==[[float(format(z,'.6g')) for z in q] for q in dense]
perf=[float(z) for z in (run/'runtime/paths/perf_log.txt').read_text().splitlines()]
assert len(perf)==16
warn=(run/'driver.stderr').read_text()
out={'schema':'P4_R2_ABB_RRT_PCS_SAVED_ONLY_POST_REVIEW_V1','status':'SOURCE_TRACE_PROVENANCE_PASS_PENDING_INDEPENDENT_PATH_AUDIT','scientific_calls':0,'compile_calls':0,'source_execution_sha256':sha(run/'execution.json'),'source_result_sha256':sha(run/'runtime/result.json'),'verified_hash_map_counts':counts,'build_manifest_sha256':sha(e['build_manifest']),'build_manifest_equal_retained_execution':True,'original_bodies_dewrapped_to_identical_source':True,'original_body_sha256':body_hash,'raw_path_matches_default_6significant_digits_of_full_double_trace':True,'complete_trace_milestone_tree_match':True,'selected_tree_path':pathids,'milestones':len(mil),'tree_vertices':len(vs),'tree_edges':len(edges),'reconstruction_completed':len(tr),'identify_completed':len(ids),'true_started':'UNOBSERVED_NO_START_HOOK','edge_trace':stats,'dense_nodes':len(dense),'distinct_dense_nodes':len(set(map(tuple,dense))),'dense_leaves':len(dense)-1,'selected_path_role_changes':2,'source_perf_log_16_values':perf,'retained_source_warning_lines':len(warn.splitlines()),'pqp_BeginModel_warning_count':warn.count('BeginModel'),'first_warning_line':warn.splitlines()[0],'prior_execution_count':len(priors),'prior_wall_s':math.fsum(t['wall_s'] for t in priors),'prior_cpu_s':math.fsum(t['cpu_s'] for t in priors),'execution_wall_s':e['wall_s'],'execution_cpu_s':e['cpu_s'],'independent_path_qualified':False,'formal_table_I_calls':0,'new_VI_candidate_constructions':0,'limitations':['No physical FK/J, IK, collision, NR or planner was called in this review.','Source exact and structural path completeness are not physical path qualification.','Raw source counters are implementation-scoped, not observed native FK/IK/PQP started counts.','Source projection counter628 is incremented at IKproject entry, not IKsolve_rob; one call may make one or two analytic IK requests and identify also uses IK outside this counter.','total_runtime sourceCPU stops before save2file/reconstruction whereas logged accumulated counters include reconstruction; driver solve_wall includes save2file.','638 retained PQP BeginModel warnings remain raw evidence; this saved-only audit cannot declare their physical impact.']}
pout=R/'reports/P4_FULL_R2_ABB_RRT_PCS_E2E_POST_REVIEW_20261015.json'
with pout.open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'report':str(pout),'sha256':sha(pout),'status':out['status'],'hash_map_counts':counts,'edge_trace':stats,'pqp_warning_count':out['pqp_BeginModel_warning_count']},ensure_ascii=False,indent=2))
