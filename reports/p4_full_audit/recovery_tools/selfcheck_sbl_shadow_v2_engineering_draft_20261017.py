#!/usr/bin/python3
# Static AST/text check only: no project import, transform, compiler, or runtime.
import ast
import hashlib
import json
from pathlib import Path
import re
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
STEM='P4_FULL_R2_ABB_SBL_PCS_SHADOW_V2_ENGINEERING_STATIC_SELF_CHECK_20261017'
J=(ROOT/'reports'/(STEM+'.json')).open('x',encoding='utf-8');M=(ROOT/'reports'/(STEM+'.md')).open('x',encoding='utf-8')
B=ROOT/'scripts/build_p4_full_r2_abb_sbl_pcs_shadow_v2_draft.py';S=ROOT/'scripts/supervise_p4_full_r2_abb_sbl_pcs_build_shadow_v2_draft.py';D=ROOT/'baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_shadow_v2_draft.cpp';P=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_SHADOW_V2_ENGINEERING_PRE_DRAFT_20261017.md'
b,s,d,p=[x.read_text() for x in (B,S,D,P)]
checks=[]
def ck(n,v,detail=None):checks.append(dict(name=n,passed=bool(v),detail=detail))
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
ck('builder_ast_parsed',isinstance(ast.parse(b),ast.Module));ck('supervisor_ast_parsed',isinstance(ast.parse(s),ast.Module))
# C++ simple lexical bracket check, never compilation.
masked=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:' '*len(m.group()),d,flags=re.S)
stack=[];pairs={')':'(',']':'[','}':'{'};ok=True
for c in masked:
 if c in '([{':stack.append(c)
 elif c in ')]}':
  if not stack or stack.pop()!=pairs[c]:ok=False;break
ck('cpp_lexical_delimiters_balanced',ok and not stack)
for text,label in ((b,'builder'),(s,'supervisor')):
 ck(label+'_BUILD02_identity',"RUN='20261017_R2_ABB_SBL_PCS_BUILD02'" in text)
 ck(label+'_new_label',"LABEL='ENGINEERING_BUILD_ONLY_SBL_PCS_SHADOW_V2_ORIGINAL_SCIENTIFIC_CONTROL'" in text)
ck('new_build_root',"abb_sbl_pcs_shadow_v2')" in b and "abb_sbl_pcs_v1')" not in b)
ck('new_driver_header_transform_selected',all(x in b for x in ('abb_sbl_pcs_observation_shadow_v2_draft.hpp','abb_sbl_pcs_driver_shadow_v2_draft.cpp','abb_sbl_pcs_instrumentation_shadow_v2_draft import')))
ck('PRE_is_current_new_file',P.name in b)
ck('D080_all_four_artifacts_bound',all(x in b for x in ('D080_P4_RELEVANCE_SCOPE_ACCELERATION_20261017.md','P4_D080_FAST_TRACK_IMPLEMENTATION_20261017.md','P4_D080_ORIGINAL_VS_APPROVED_VS_ACTUAL_COVERAGE_20261017.csv','P4_D080_SCOPE_MAPPING_VALIDATION_20261017.json')))
ck('original_and_D080_denominators_separate','original_paper_table_I_target=22500,d080_approved_table_I_target=18000' in b)
ck('build_does_not_authorize_runtime','runtime_execution_authorized_by_engineering=False' in b and 'binary_execution_calls=0' in b)
ck('new_shadow_independent_review_gate','writer_shadow_v2_independently_reviewed=False' in b)
ck('new_modes_local_solve_only',"runtime_modes=['local','solve'],runtime_observation_modes=['plain','trace']" in b)
ck('budget_45_90_still_total_3600_7200','budget=dict(wall_s=45.,cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)' in b)
ck('current_charged_prior_checks_retained',all(x in b for x in ('LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS','EXACT_PRIOR_CHARGE_SUMS_REQUIRED','PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED','ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING')))
ck('five_TU_stdout_dependency_gate_retained',all(x in b for x in ('exactly5 complete rules','-MD','-MF','UNFROZEN_PROTECTED','SYSTEM_SBL_HEADER_MUST_NOT_REPLACE_AUTHOR_CLASS')))
ck('supervisor_exclusive_FD_parent_proof_retained',all(x in b+s for x in ('ACTUAL_GNU_TIME_PARENT_REQUIRED','EXCLUSIVE_SUPERVISION_INODE_REQUIRED','O_EXCL','time_inode_unchanged')))
ck('compiler_lifecycle_empty_after_retained','ACTUAL_COMPILER_GROUP_NOT_EMPTY_AFTER_KILL_WAIT' in b and 'compiler_reaped' in b)
ck('no_binary_launch_in_builder',"subprocess.Popen(command" in b and 'subprocess.Popen([str(BINARY)' not in b)
ck('driver_only_II_local_solve',all(x in d for x in ('environment!="II"','operation!="local"&&operation!="solve"','mode!="plain"&&mode!="trace"')))
ck('driver_requires_one_JSON_and_EOF','ONE_REQUEST_THEN_STDIN_EOF_REQUIRED' in d)
ck('driver_A01_strict_exact_endpoints','finite12(request.at("start_q12"))==START&&finite12(request.at("goal_q12"))==GOAL' in d)
ck('driver_seed7_range08_frozen_guard','request.at("seed")==7&&request.at("range_rad")==.8&&request.at("separately_frozen_runtime_qualification")==true' in d)
ck('driver_only_one_10s_solve_call',d.count('planner->solve(')==1 and 'timedPlannerTerminationCondition(10.)' in d and 'request.at("solve_seconds")==10.' in d)
ck('driver_no_extra_project_observer','.project(' not in d and '->project(' not in d and 'for(unsigned sample=0;sample<13' not in d)
ck('driver_seed_once_each',d.count('ompl::RNG::setSeed(7)')==1 and d.count('std::srand(7)')==1)
ck('driver_no_sampling_observer','uniformInt(' not in d and 'uniform01(' not in d and 'rand(' not in d.replace('srand(',''))
ck('original_resolution_and_range', 'setStateValidityCheckingResolution(.02)' in d and 'og::SBL(si,.8,1)' in d)
ck('local_fixture_explicit_reconstruction','RECONSTRUCTED_TREE_FIXTURE_ORIGINAL_SBL_METHOD_BODIES' in d)
ck('local_requires_frozen_fixture_and_provenance',all(x in d for x in ('FROZEN_LOCAL_FIXTURE_REQUIRED','SAVED_INPUT_PROVENANCE_REQUIRED','saved_input_references')))
ck('local_only_one_native_isPathValid_and_checkSolution',d.count('isPathValid(tStart_,last)')==1 and d.count('checkSolution(true,tStart_,tGoal_,last,solution)')==1)
ck('local_bound_chains_max_three','chain.size()<=3' in d and 'other.size()<=3' in d)
ck('fixture_adapter_root_zero_guard','(parent||role==0)' in d)
ck('driver_never_directly_invokes_SVC_components',all(x not in d for x in ('checkMotionRBS(','IKproject(','identify_state_ik(','collision_state(','reconstructRBS(')))
ck('native_five_paths_explicit',all(x in d for x in ('parent/path_milestones.txt','parent/ik_path.txt','work/path.txt','work/temp.txt','work/perf_log.txt')))
ck('native_existing_files_final_bytes_retained','bytes_hex' in d and 'readback_bytes_saved' in d and 'absence_retained' in d)
ck('native_present_capture_failure_marks_STOP','native_output_capture_complete' in d and 'if(!all_native_retained)out["status"]="STOP_EVIDENCE_PERSISTENCE_ERROR"' in d)
ck('sidecar_durable_exclusive_readback',all(x in d for x in ('O_WRONLY|O_CREAT|O_EXCL','::fsync(fd)','syncdir(path.parent_path())','readbytes(path)==bytes','ik_path_shadow_v2.json')))
ck('no_original_path_overwrite_by_adapter','durable_new(saved,bytes)' in d and 'durable_new(path,bytes)' not in d)
ck('shadow_final_text_not_stream_flags','UNOBSERVED_FINAL_READBACK_CERTIFICATE_ONLY' in d and 'original_stream_open_write_flush_flags' in d)
ck('shadow_attempts_do_not_imply_write_success','empty_attempts_do_not_prove_write_success' in d)
ck('shadow_actual_three_columns_live_ID_check',all(x in d for x in ('EXACT_THREE_INTEGER_IK_PATH_COLUMNS_REQUIRED','FINAL_IK_PATH_COLUMNS_MUST_MATCH_SHADOW_AND_LIVE_BRANCHES','ATTEMPT_LIFETIME_SHADOW_IDENTITY_REQUIRED')))
ck('sidecar_copied_after_destruction_without_reset',d.index('planner.reset();')<d.index('out["writer_metadata_attempts"]=') and d.count('p4sbl::reset()')==1)
ck('EXACT_stays_pending_path_qualification','SOURCE_EXACT_PENDING_INDEPENDENT_PATH_QUALIFICATION' in d and 'independent_path_qualified",false' in d)
ck('no_runtime_fixture_yet_frozen','具体 fixture **尚未冻结' in p)
ck('PRE_no_describe_or_science',all(x in p for x in ('未 describe 协议','未冻结','D080 18000','V25')))
oldpins={'baselines/p4_full/geometry_consistent/abb_sbl_pcs_observation_draft.hpp':'7507648eb8ede25eea1cadcc32270a0bdf27633b1520de717718f6a907b986ac','baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_draft.py':'cf5f5192840883634dfd3f18ea117dd505b66a8f1648391ae15113508ae2a237','baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_draft.cpp':'899fbabf80d2bf8b01e59efea81aa21077a3b113662c579661e044d6f66df7b9','baselines/p4_full/geometry_consistent/abb_sbl_pcs_observation_shadow_v2_draft.hpp':'3c0d3031d53532bb077e7eabb3911aa9f911f771bb34216406cf0a71fb9108c3','baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_shadow_v2_draft.py':'926592eb43ef8ad90a6434a30aa613c2c6c41416e9f9120c734b76adc3a39209'}
for name,want in oldpins.items():ck('prior_unchanged_'+name,sha(ROOT/name)==want)
source_sha={str(x.relative_to(ROOT)):sha(x) for x in (B,S,D,P,Path(__file__))}
failed=sum(not x['passed'] for x in checks);v={'schema':'P4_SBL_SHADOW_V2_ENGINEERING_STATIC_SELF_CHECK_V1','personnel_independent':False,'status':'PASS_STATIC_DRAFT_ONLY_NOT_EXECUTED' if not failed else 'FAIL_STATIC_DRAFT_RETAINED','checks_total':len(checks),'checks_passed':len(checks)-failed,'checks_failed':failed,'checks':checks,'source_sha256':source_sha,'project_imports':0,'text_transform_calls':0,'describe_calls':0,'compile_calls':0,'binary_calls':0,'model_calls':0,'setup_calls':0,'local_calls':0,'solve_calls':0,'formal_calls':0,'local_fixture_frozen':False,'budget_actual_scientific_execution_s':0,'limitations':['Text/AST self-review only, no C++ compilation, no runtime or numerical validation.','Local fixture and runtime protocols/budgets not frozen; exact native path and CCD remain pending.','Real dependency/source/current V25/D080 hashes must be regenerated only after independent review; no protocol describe performed here.']}
json.dump(v,J,ensure_ascii=False,indent=2);J.write('\n');J.close();M.write(f"# SBL shadow v2 合并工程草案静态自检\n\n状态 `{v['status']}`：{v['checks_passed']}/{v['checks_total']}，失败 {failed}。只读 Python AST 与 C++/协议文本；未 import 项目、调用 transform/describe/编译/二进制/模型/setup/local/solve。人员独立性为 false；本自检不代替 root 与独立审查。\n\n新 driver 保存最终原文件证据和版本化 sidecar，原stream内部flags仍UNKNOWN。fixture未冻结，运行预算未冻结。下一步独立静审通过后才生成当前SHA工程协议、commit冻结与单BUILD02。\n");M.close();print(json.dumps({'status':v['status'],'checks_total':len(checks),'checks_failed':failed,'failed':[x for x in checks if not x['passed']],'source_sha256':source_sha},ensure_ascii=False))
