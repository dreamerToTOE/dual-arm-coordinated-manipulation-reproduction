import hashlib,json,math,sys
from pathlib import Path
R=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full');sys.path.insert(0,str(R))
from baselines.p4_full.geometry_consistent.abb_pcs_source_corrections_draft import FACTORS,candidate_bytes
B=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def save(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
assets={str(B/'manifest.json'):sha(B/'manifest.json')};edits=[]
for variant in ['author_native','geometry_consistent']:
 for factor,definition in FACTORS.items():
  p=B/(variant+'_plain')/definition['relative_file'];assets[str(p)]=sha(p)
  changed,row=candidate_bytes(p.read_bytes(),factor);row.update(base_variant=variant,original_file=str(p),proposed_fresh_stage=f'/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_source_corrections_v1/{factor.lower()}/{variant}_candidate')
  edits.append(row)
points=[]
for env in ['II','III']:
 for index in [0,1]:
  p=R/f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/{env}_{index}.json';x=load(p);q=x['selected_q_rad'];assert len(q)==12
  assets[str(p)]=sha(p);points.append({'id':env+'_'+str(index),'environment':env,'q12':q,'source':str(p.relative_to(R)),'source_sha256':sha(p)})
examples=[]
for a in points:
 for b in points:
  if a['environment']!=b['environment']:continue
  for role in [0,1]:
   a6=a['q12'][6*role:6*role+6];b6=b['q12'][6*role:6*role+6]
   source=math.sqrt(math.fsum((v-w)**2 for v,w in zip(a6,b6))) if role==0 else math.sqrt(math.fsum(v*v for v in b6))
   target=math.sqrt(math.fsum((v-w)**2 for v,w in zip(a6,b6)))
   examples.append({'a':a['id'],'b':b['id'],'active_chain':role,'source_qa_after_retrieve':a6 if role==0 else [0.]*6,'source_qb_after_retrieve':b6,'original_formula_value_rad':source,'corrected_formula_value_rad':target,'diagonal':a['id']==b['id'],'zero_self_distance_counterexample':a['id']==b['id'] and role==1 and source>0.,'arithmetic_only_no_original_function_execution':True})
assert len(examples)==16 and sum(x['zero_self_distance_counterexample'] for x in examples)==4
old_manifest=load(B/'manifest.json');buildrows=[e for e in old_manifest['entries'] if e['mode']=='plain']
config={'schema':'P4_R2_ABB_PCS_SOURCE_CORRECTION_CANDIDATES_DRAFT_V1','frozen':False,'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False},'classification':'PURE_SAVED_SOURCE_AND_ARRAY_ANALYSIS / UNBUILT_UNEXECUTED_CANDIDATES','source_author_commit':'909bd72fff778aca8682c96f9eb86ae4eb75557b','candidate_module':'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py','candidate_module_sha256':sha(R/'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py'),'bound_saved_assets_sha256':assets,'independent_factor_edits':edits,'never_patch_old_stage':True,'never_combine_factors_in_qualification':True,'helper_actual_planner_reachability':'RRT_PCS/CBiRRT_PCS/SBL_PCS real grow paths do not call random-three-argument IKproject; helper qualification is not their prerequisite.','source_policy_preserved':['Original 0..7 vector and std::random_shuffle call/order, before one success break.','Original calc_specific_IK_solution_R1/R2 and identify_state_ik checks.','Original loop-end i==8 return and false-output mutation.','No collision/limit gate added to helper; existing policy remains separately audited.','CBiRRT role1 first destination qb becomes qa only; original norm, interpolation, role RNG and other planner code unchanged.'],'draft_future_budget_not_authorization':{'helper_engineering':{'targets':4,'wall_s':120.,'cpu_s':180.,'per_target_wall_s':45.,'per_target_cpu_s':90.},'helper_science':{'wall_s':90.,'cpu_s':180.,'saved_centers':4,'roles':2,'seeds':[7,17],'base_requests':16,'numerical_variants':2,'source_control_variants':2,'runtime_observation_modes':2,'top_helper_call_cap':128,'maximum_direct_analytic_IK_attempts':1024,'maximum_identify_analytic_IK_attempts':16384,'maximum_total_analytic_IK_attempts':17408,'maximum_source_arm_FK':3072,'rand_draws_from_bound_libstdcpp_shuffle_structural_prediction':896,'collision_checks_after_source_return_cap':128,'external_math_arm_FK_cap':256,'collision_adapter_arm_FK_J_cap':512},'distance_engineering':{'targets':2,'wall_s':60.,'cpu_s':120.,'per_target_wall_s':45.,'per_target_cpu_s':90.},'distance_science':{'wall_s':15.,'cpu_s':30.,'fixed_array_cases':16,'source_control_variants':2,'runtime_observation_modes':2,'top_activeDistance_call_cap':64,'FK_IK_NR_RNG_collision_solve_calls':0}},'historical_build_cost_evidence':[{'variant':e['variant'],'mode':e['mode'],'wall_s':e['wall_s'],'cpu_s':e['cpu_s']} for e in buildrows],'historical_one_RRT_target':{'wall_s':17.12737691100483,'cpu_s':23.727903,'two_target_linear_reference_wall_s':34.25475382200966,'two_target_linear_reference_cpu_s':47.455806,'four_target_linear_reference_wall_s':68.50950764401932,'four_target_linear_reference_cpu_s':94.911612,'is_new_target_cost_measurement':False},'scientific_calls':0,'compile_calls':0,'new_stage_writes':0,'formal_table_I_calls':0,'new_VI_candidate_constructions':0}
save(R/'configs/p4_full/r2_abb_pcs_source_corrections_v1.draft.json',config)
proof={'schema':'P4_R2_ABB_CBIRRT_ACTIVEDISTANCE_SAVED_ARRAY_COUNTEREXAMPLE_V1','classification':'STATIC_SOURCE_SEMANTICS_AND_SAVED_ANGLE_ARITHMETIC_ONLY','bound_source_sha256':{str(B/(v+'_plain')/'planners/CBiRRT_PCS.cpp'):sha(B/(v+'_plain')/'planners/CBiRRT_PCS.cpp') for v in ['author_native','geometry_consistent']},'candidate_module_sha256':config['candidate_module_sha256'],'formula_scope':'Original role1 leaves qa zero, overwrites qb with b.arm2; therefore d(a,b)=norm(b.arm2), independent of a. Values below are formula-derived saved-array arithmetic, not execution of original C++ method.','points':points,'cases':examples,'diagonal_counterexamples':4,'original_function_calls':0,'mathematical_model_calls':0,'compile_calls':0,'limitations':['No repaired source was staged, compiled, or executed.','Pure distance counterexample does not establish planner runtime or success-rate impact.','No statement about paper theoretical metric or PCS method follows from this implementation defect.']}
save(R/'reports/P4_FULL_R2_ABB_CBIRRT_ACTIVEDISTANCE_SAVED_COUNTEREXAMPLE_20261015.json',proof)
print(json.dumps({'edits':edits,'counterexamples':[x for x in examples if x['zero_self_distance_counterexample']]},ensure_ascii=False,indent=2))
