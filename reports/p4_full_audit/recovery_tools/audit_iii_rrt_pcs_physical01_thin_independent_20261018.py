#!/usr/bin/env python3
"""Thin stdlib-only static PCS physical protocol review; no model imports."""
import ast
import copy
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[3];inputs={};checks=[]
def raw(n):
 v=(R/n).read_bytes();inputs[n]=hashlib.sha256(v).hexdigest();return v
def src(n):return raw(n).decode()
def js(n):return json.loads(raw(n))
def ck(n,v):checks.append(dict(name=n,passed=bool(v)))
def find(t,k,n):return next(z for z in ast.walk(t)if isinstance(z,k)and getattr(z,'name',None)==n)
def eq(a,b):return ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
RUNNER='scripts/p4_d080/qualify_iii_rrt_pcs_physical01_v1_draft.py';SUP='scripts/p4_d080/supervise_iii_rrt_pcs_physical01_v1_draft.py';DRAFT='configs/p4_d080/iii_rrt_pcs_physical01_v1.DRAFT.json';PRE='reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_PRE_DRAFT_20261018.md'
s=src(RUNNER);t=ast.parse(s);sup=src(SUP);draft=js(DRAFT);src(PRE)
expected={RUNNER:'1073996b17a8d8888776a046132a91efcf24628d4ebd3693d0ae5bde27fc6551',SUP:'fb6147786b0e294ec1c953316f6f68161e7c4b89f69fd2f357500573b174c5a4',DRAFT:'1ee590c3f07ee1748874e6819f1ff3fad3d3b8cedc675d57736b19c2a0e55f70',PRE:'75a72c93d34cf734a7f44c64ec7da606b8824f4b6c4d4456df535e510bc1b2be'}
ck('four_stable_incremental_sources_exact',all(inputs[n]==v for n,v in expected.items()))
tail=ast.parse(src('scripts/qualify_p4_full_r2_abb_sbl_pcs_path_tail02_draft.py'));nr=ast.parse(src('scripts/qualify_p4_full_r2_abb_cbirrt_nr_path_draft.py'))
ck('adapter_counting_wrapper_exact_AST_of_qualified_tail',eq(find(t,ast.FunctionDef,'counted'),find(tail,ast.FunctionDef,'counted')))
oldloop=next(z for z in ast.walk(tail)if isinstance(z,ast.For)and ast.unparse(z.target)=='(i, q)')
newloop=copy.deepcopy(next(z for z in ast.walk(t)if isinstance(z,ast.For)and ast.unparse(z.target)=='(i, q)'))
class Reverse(ast.NodeTransformer):
 def visit_Constant(self,n):return ast.copy_location(ast.Constant('II'),n)if n.value=='III'else n
 def visit_Name(self,n):return ast.copy_location(ast.Name(id='durable_new',ctx=n.ctx),n)if n.id=='new_json'else n
 def visit_Expr(self,n):
  if isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='require'and any(isinstance(z,ast.Constant)and z.value=='FIXED_III_PQP_QUERY_CAP'for z in ast.walk(n)):return None
  return self.generic_visit(n)
newloop=Reverse().visit(newloop)
ck('complete_node_scientific_loop_exact_AST_after_only_II_to_III_immediate_writer_and_resource_cap',eq(oldloop,newloop))
ck('finalIO_timer_and_byte_verified_tar_fsync_original_AST',eq(find(t,ast.ClassDef,'FinalIOGuard'),find(nr,ast.ClassDef,'FinalIOGuard')) and eq(find(t,ast.FunctionDef,'durable_saved_snapshot'),find(nr,ast.FunctionDef,'durable_saved_snapshot')))
queue='configs/p4_d080/iii_rrt_pcs_source01_complete_saved_queue_v1.DRAFT.json';q=js(queue)
qp='reports/P4_D080_ENV_III_RRT_PCS_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_20261018.json';p=js(qp)
ck('same_saved_complete649_queue_reuses_independent7_no_source_reexecution',inputs[queue]=='037b754847718d5bc2a929c7600d354c61b785d249eeacd31548c52f84fdf1d9' and inputs[qp]=='8318b25ac39cfe6a6f69df71e95a118381ef42ff9b9e88013683719c423f9f73' and p['checks_total']==p['checks_passed']==7 and p['checks_failed']==0 and draft['fixed_queue']==q['fixed_queue'] and len(q['fixed_queue']['nodes'])==649 and len(q['fixed_queue']['edges'])==14 and draft['execution_node_ids']==list(range(649)))
ck('fixed_original_geometry_and_strict_gates_no_budget_increase',draft['geometry']=={'base_distance_mm':1200.,'arm_bases_mm_rad':[[-600.,0.,0.],[600.,0.,3.1416]],'grasp_rod_mm':500.,'source_internal_environment':2,'collision_adapter_model':'abb','worker_environment_argument':'III','source_PQP_tolerance_mm':8.} and draft['gates']=={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*2.220446049250313e-16} and draft['budget']=={'wall_s':120.,'cpu_s':240.,'work_wall_s':100.,'work_cpu_s':200.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.})
ck('exact_all649_fixed_caps_and_no_new_projection_RBS_solve_rng',draft['max_math_arm_FK']==draft['max_branch_identity']==1298 and draft['max_collision_calls']==649 and draft['max_adapter_internal_arm_FK_J']==2596 and draft['max_PQP_queries']==133694 and draft['pair_counts']=={'native':103,'aligned':103} and draft['max_nodes_per_execution']==2048 and draft['zero_calls']=={'IK':0,'NR':0,'projection':0,'RBS':0,'solve':0,'RNG':0,'VI_constructions':0,'formal_table_I':0})
chain='reports/P4_D080_PREFLIGHT_RECOVERY_CHAIN_THIN_INDEPENDENT_PRE_ADDENDUM_20261018.json';c=js(chain)
ck('reviewed_helper_only_prior_connection_and_own_source_frozen',inputs[chain]=='17e47992e46e1b9ae0eee6242c71edda90e3e0ce559332e867ce1ceed728cba3' and c['checks_total']==c['checks_passed']==11 and c['checks_failed']==0 and ast.unparse(find(t,ast.FunctionDef,'current_prior'))=="def current_prior(spec):\n    return P.validate_prior(spec, RUN, ROOT / 'results/p4_full' / RUN)" and draft['preflight_recovery_helper']['sha256']=='b315972ce22569684c4fe21dc487fc0456b7db63b8224906020d6fc41911f65e')
ck('actual_supervision_exclusive_single_run_and_terminal_worker_checks',all(z in sup for z in ['os.O_EXCL','spec[\'budget\']=={\'wall_s\':120.',"proc.wait()","EXPLICIT_FROZEN_III_PHYSICAL_REQUIRED","OLD_RUN_OR_CLAIM_NO_RETRY"]) and all(z in s for z in ['registered_popen','central_collision_worker_kill_reap','pipe_EOF_drained','COLLISION_WORKER_GROUP_REMAINS_AFTER_REAP','complete_collision_worker_cleanup_gate','STOP_DURABLE_SNAPSHOT_UNQUALIFIED','STOP_FINAL_WALL_OR_CPU_BUDGET']))
adapter=src('baselines/p4_full/geometry_consistent/collision_adapter.py')
ck('existing_CHECKED_collision_response_requires_preferred_pose_consistency',"'status': 'CHECKED'"in adapter and "'pose_consistency'"in adapter and "pose_consistency['passed']"in adapter)
ck('draft_unexecuted_and_root_must_fill_latest_ledger_before_freeze',draft['frozen']is draft['scientific_execution_authorized']is draft['formal_execution_authorized']is draft['independent_path_qualified']is False and all(v is False for v in draft['reviews'].values()) and all(z in s for z in ['LATEST_CHARGED_PRIOR_REQUIRED','ALL_PRIOR_CHARGED_CERTIFICATE_BYTES_PREBOUND','UNCOMMITTED_III_PHYSICAL_SOURCE_OR_PROTOCOL','COMPLETE_ORIGINAL_QUEUE_AND_EXACT_CAPS_REQUIRED']))
failed=[z for z in checks if not z['passed']];out=R/'reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_THIN_INDEPENDENT_PRE_20261018.json'
report=dict(schema='P4_D080_III_RRT_PCS_PHYSICAL01_THIN_INDEPENDENT_PRE_V1',personnel_independent=True,status='PASS_COMPLETE649_DRAFT_STATIC_REVIEW'if not failed else'FAIL_COMPLETE649_DRAFT_STATIC_REVIEW',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,inputs_sha256=inputs,independent_path_qualified=False,continuous_collision_certificate=False,new_compile_binary_model_scientific_calls=0,historical_full_bound_rehash_repeated=False,root_freeze_required=True,limits=['Root must bind the latest charged ledger and all independent PREs, freeze and commit actual bytes before the one authorized complete649 qualification.','No new source solve/RBS/projection/sampling; original14 edges and all source true/false attempts preserved.','Independent saved POST must still verify actual closure, branches, limits, collision poses, full12 leaves, worker lifecycle and complete durable evidence.','Only discrete aligned source-policy qualification; no continuous collision, solid rod, omitted pair, native equivalence, rate or full-paper claim.'])
with out.open('x')as f:f.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps(dict(checks=len(checks),failed=failed,sha256=hashlib.sha256(out.read_bytes()).hexdigest())))
