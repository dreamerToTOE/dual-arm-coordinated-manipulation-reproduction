#!/usr/bin/env python3
"""Read saved assets and run only the explicitly authorized pure text transform in memory."""
import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import shlex

ROOT=Path(__file__).resolve().parents[3]
def p(n):
    q=Path(n);return q if q.is_absolute() else ROOT/q
def raw(n):return p(n).read_bytes()
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def js(n):return json.loads(raw(n))
PLAN='configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'
PRE='reports/P4_D080_ENV_V_RRT_PCS_THIN_ENGINEERING_PRE_DRAFT_20261018.md'
plan=js(PLAN);tr=plan['source_byte_transform'];driver=raw(plan['copy_driver_only']['source']).decode()
checks=[]
def ck(n,v,e=None):checks.append(dict(name=n,passed=bool(v),evidence=e))
ck('own_sources_exact_saved_identities',all(sha(n)==w for n,w in plan['own_sources_sha256'].items()))
transform=raw(tr['transform_source']);parsed=ast.parse(transform)
imports=[n.module if isinstance(n,ast.ImportFrom) else z.name for n in parsed.body if isinstance(n,(ast.Import,ast.ImportFrom)) for z in (n.names if isinstance(n,ast.Import) else [n])]
ck('pure_transform_imports_only_hashlib_re_future_and_no_model_or_IO',set(imports)=={'__future__','hashlib','re'} and all(x not in transform.decode() for x in ['open(','read_bytes(','write_bytes(','subprocess','importlib','Popen']))
ck('qualified_input_exact_original_full_file',sha(tr['input'])==tr['input_sha256']=='bdbe5b29125a32c4890f4af5ca77f28bd8830f463d195327f223eab3b6b20509')
mod=runpy.run_path(str(p(tr['transform_source'])),run_name='pure_text_reviewer_only')
original=raw(tr['input']);output,receipt=mod['instrument_svc'](original)
# Independently remove the two exact inserted expression regions, restoring
# the whole qualified input without invoking the transform's reverse code.
text=output.decode()
prefix='\n const State p4_input_ik=ik;\n'
observe=' p4e2e::observe_identify(q1,q2,p4_input_ik,p4_return);\n'
recon_prefix='\n const bool p4_return=[&]() -> bool {'
recon_suffix='}();\n p4e2e::observe_reconstruction(s1,s2,active_chain,ik_sol,Confs,p4_return);\n return p4_return;\n'
ck('only_four_exact_text_insertions_and_single_postreturn_hooks',all(text.count(z)==1 for z in [prefix,observe,recon_prefix,recon_suffix]))
restored=text.replace(prefix,'',1).replace(observe,'',1).replace(recon_prefix,'',1).replace(recon_suffix,'',1)
ck('independent_whole_file_inverse_restores_every_original_byte',restored.encode()==original)
ck('no_second_vector_scientific_lambda',text.count('State p4_return=[&]() -> State {')==original.decode().count('State p4_return=[&]() -> State {') and 'State p4_return=[&]() -> State {' in original.decode())
ck('transform_receipt_matches_observed_output_only_no_additional_science',receipt['input_sha256']==sha(tr['input']) and receipt['output_sha256']==hashlib.sha256(output).hexdigest() and receipt['whole_input_file_byte_reversible'] is True and receipt['additional_model_calls']==receipt['additional_rng_calls']==0 and all(receipt[k] is False for k in ['RRT_search_or_save2file_changed','random_helper_correction','five_argument_helper_correction']))
rrt=plan['RRT_source_byte_identity']
ck('whole_RRT_cpp_and_header_unmodified',sha(rrt['cpp'])==rrt['cpp_sha256']=='4ea1a052a5e9f2668fd62918c39f5a3820fc0300158f9cef0d51def3cb226b0f' and sha(rrt['header'])==rrt['header_sha256']=='93ae661e0af0b7e38bd2f3742e60bf24d1084d1b1f73d87fc0246bcc9a0d6fab' and rrt['changed'] is False)
rrtext=raw(rrt['cpp']).decode()
ck('original_save2file_success_temp_removal_not_replaced',('remove(' in rrtext or 'std::remove(' in rrtext) and 'temp.txt' in rrtext and 'path.txt' in rrtext and 'save2file' in rrtext and rrt['cpp']!=tr['input'])
observer=plan['qualified_V_observer'];cmds=plan['commands'];oldcommands=[z['original_saved_compile_command'] for z in plan['reused_objects']]
ck('uniform_TRACE1_macro_all_five_TU_old_and_new',observer['mode']==1 and all(c.count('-DP4V_TRACE_MODE=1')==1 and '-DP4V_TRACE_MODE=0' not in c for c in oldcommands+cmds[:2]))
ck('same_exact_V_observer_preinclude_path_all_TUs_no_duplicate_driver_include',sha(observer['path'])==observer['sha256']=='ba401a7b0a97b0a34ede6fb129d59f42be2dd7ff67f51454d6c334a3c9b6cc02' and all(any(c[i]=='-include' and c[i+1]==observer['path'] for i in range(len(c)-1)) for c in oldcommands+cmds[:2]) and 'static_assert(P4V_TRACE_MODE == 1' in driver and '#include "comau_v_pcs_observation' not in driver)
legacy=str(ROOT/'baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_observation.hpp')
ck('same_exact_II_observation_ABI_reused_and_V_result_explicit',sha(legacy)=='b597b56199279bd02a7030375e0dd055d650c9a0bb4bee80aef6d4242755381c' and all(any(c[i]=='-include' and c[i+1]==legacy for i in range(len(c)-1)) for c in cmds[:2]) and 'II p4e2e observation ABI retained verbatim; environment is V' in driver and '"environment","V"' in driver)
ck('three_saved_objects_MD_and_sources_match_current_bytes',len(plan['reused_objects'])==3 and all(sha(z['object'])==z['object_sha256'] and sha(z['dependency'])==z['dependency_sha256'] and sha(z['source'])==z['source_sha256'] for z in plan['reused_objects']))
pool=js(plan['reuse_dependency_bound_sets'][0]['protocol'])['bound_files_sha256'];deps=set()
for row in plan['reused_objects']:
    _,tail=raw(row['dependency']).replace(b'\\\n',b' ').decode().split(':',1)
    deps.update(str(Path(n).resolve(strict=True)) for n in shlex.split(tail))
ck('reused_MD_dependency_paths_all_have_saved_pool_binding_without_full_rehash',all(n in pool for n in deps),{'unique_saved_dependency_paths':len(deps),'repeat_full_pool_hash_calls':0})
ck('only_two_new_TU_one_link_and_exact_three_old_objects',len(cmds)==3 and plan['new_compile_calls']==2 and plan['new_link_calls']==1 and all('-c' in c for c in cmds[:2]) and '-c' not in cmds[2] and all(cmds[2].count(z['object'])==1 for z in plan['reused_objects']))
ck('driver_future_freeze_guard_configure_before_all_scientific_construction',all(z in driver for z in ['request.at("frozen")!=true','request.at("scientific_execution_authorized")!=true','request.at("independent_review_passed")!=true','request.at("formal_execution_authorized")!=false']) and driver.index('p4vpcs::configure(')<driver.index('auto planner=std::make_shared<og::RRT>'))
ck('driver_V_original_sampler_range_goalbias_callback_no_simplification',all(z in driver for z in ['{-3.1416,-1.0472,-3.1416/2,-3.1416,-2.0944,-3.1416}','{3.1416,2.1871,1.3090,3.1416,2.0944,3.1416}','std::make_shared<og::RRT>(si,.2,1)','planner->setGoalBias(.05)','si->setStateValidityChecker([](const ob::State*){return true;})','si->setStateValidityCheckingResolution(.02)','{"solution_path_simplification",false}']) and driver.count('planner->solve(')==1)
ck('all_false_partial_and_complete_records_preserved_with_observability_limits',all(z in driver for z in ['reconstruction_attempts.jsonl','identify_observations.jsonl','"reconstruction_true_started"]="UNOBSERVED_NO_START_HOOK"','"identify_true_started"]="UNOBSERVED_NO_START_HOOK"','"full_solve_plain_trace_consistency_qualified"]=false','"source_observed_records"]=p4vpcs::records']))
science=plan['future_science_request_DRAFT']
ck('all_budget_prior_seed_solve_caps_unbound_and_flags_false',plan['budget'] is plan['prior'] is None and all(plan[k] is False for k in ['frozen','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized']) and all(science[k] is None for k in ['seed','solve_seconds','caps']) and all(science[k] is False for k in ['frozen','scientific_execution_authorized','independent_review_passed','formal_execution_authorized']))
ck('no_stage_no_model_binary_or_VI_construction',not p(plan['stage_root']).exists() and plan['new_binary_execution_calls']==plan['new_model_calls']==plan['new_VI_constructions']==0)
out=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
report={'schema':'P4_D080_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_V1','personnel_independent':True,'status':'PASS_SOURCE_SEAMS_ONLY_NOT_EXECUTABLE' if all(x['passed'] for x in checks) else 'FAIL_SOURCE_SEAMS_ONLY','checks_total':len(checks),'checks_passed':sum(x['passed'] for x in checks),'checks_failed':sum(not x['passed'] for x in checks),'checks':checks,'inputs_sha256':{n:sha(n) for n in [PLAN,PRE,tr['transform_source'],tr['input'],plan['copy_driver_only']['source'],legacy,observer['path'],rrt['cpp'],rrt['header']]},'pure_text_transform_calls':1,'pure_transform_output_materialized_to_stage':False,'pure_transform_output_sha256':hashlib.sha256(output).hexdigest(),'pure_transform_receipt':receipt,'new_compile_calls':0,'new_binary_calls':0,'new_model_calls':0,'new_scientific_calls':0,'auditor_sha256':sha(__file__),'engineering_execution_authorized':False,'scientific_execution_authorized':False,'full_solve_plain_trace_consistency_qualified':False,'full_path_qualified':False,'limitations':['Only source/observation seam review, no engineering executor, budget or current-prior freeze exists.','Old three objects and actual saved MD identity checked; saved dependency pool map referenced without whole-pool rehash; runtime must bind every actual protected dependency.','Post-return hook does not expose true_started when source fails before return; old V source lifetime evidence must remain.','Original save2file success deletion and failure partial temp retention remain; original helper defects unchanged.','Original collisions, UNKNOWN and prior scientific failures retained; no new path or formal statistic.']}
with out.open('x') as f:f.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks_total':len(checks),'failed':[x for x in checks if not x['passed']],'sha256':sha(out)},ensure_ascii=False,indent=2))
