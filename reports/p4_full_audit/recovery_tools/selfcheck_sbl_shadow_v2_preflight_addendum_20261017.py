#!/usr/bin/python3
"""Read-only AST/text addendum. Never imports project or executes C++/model."""
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
D=ROOT/'baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_shadow_v2_draft.cpp'
P=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_SHADOW_V2_ENGINEERING_PRE_DRAFT_20261017.md'
B=ROOT/'scripts/build_p4_full_r2_abb_sbl_pcs_shadow_v2_draft.py'
S=ROOT/'scripts/supervise_p4_full_r2_abb_sbl_pcs_build_shadow_v2_draft.py'
STEM='P4_FULL_R2_ABB_SBL_PCS_SHADOW_V2_LOCAL_PREFLIGHT_STATIC_ADDENDUM_20261017'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=D.read_text(); p=P.read_text();checks=[]
def ck(name,value):checks.append(dict(name=name,passed=bool(value)))
ck('driver_expected_SHA',sha(D)=='5e6a78ac051d9f2a32b4abad3bb41c466e82bfc8f56b3a08c624b387de9a7cda')
ck('PRE_final_engineering_SHA',sha(P)=='c229fa7dc56fcafdc7c69434742b7a14b052e7ea15348fe89cd7cbe7ca994c08')
ck('builder_unchanged_and_AST_only',sha(B)=='fac6cde1ca4cd03cdc8f14d131af9f3ff1c6d9323f4c52717f7f771f7c6ae94f' and isinstance(ast.parse(B.read_text()),ast.Module))
ck('supervisor_unchanged_and_AST_only',sha(S)=='32ba34ea2e800204b0f3372ed62102b0b30ae80bb51b940d43a757de03d36078' and isinstance(ast.parse(S.read_text()),ast.Module))
pre=d[d.index('void local_preflight('):d.index('std::string hexbytes(')]
ck('preflight_strings_no_escaped_source_quotes',r'\"' not in pre)
for value in ('FROZEN_LOCAL_FIXTURE_REQUIRED_BEFORE_MODEL','EXACT_LOCAL_FIXTURE_KIND_REQUIRED_BEFORE_MODEL','SAVED_LOCAL_INPUT_PROVENANCE_REQUIRED_BEFORE_MODEL','BOUNDED_LOCAL_CHAIN_REQUIRED_BEFORE_MODEL','INTEGER_LOCAL_BRANCH_ID_REQUIRED_BEFORE_MODEL','LOCAL_BRANCH_RANGE_REQUIRED_BEFORE_MODEL','INTEGER_LOCAL_ROLE_REQUIRED_BEFORE_MODEL','LOCAL_ROOT_ZERO_OR_GROW_ROLE_REQUIRED_BEFORE_MODEL','NONROOT_LOCAL_LAZY_CHAIN_REQUIRED_BEFORE_MODEL'):
 ck(value,value in pre)
ck('finite12_checked_in_pure_JSON_preflight','finite12(node.at("q12"))' in pre)
ck('no_model_RNG_IO_inside_preflight',all(value not in pre for value in ('planner','setup(', 'RNG','srand','fs::','::open','checkMotion','FKsolve','IKproject')))
main=d[d.index('int main('):]
call=main.index('local_preflight(request.at("fixture"))')
ck('preflight_after_parse_and_exact_endpoints',main.index('json::parse(line)')<main.index('EXACT_SAVED_A01_RECONSTRUCTED_ENDPOINTS_REQUIRED')<call)
ck('preflight_before_directory_seed_and_model',all(call<main.index(value) for value in ('work=fs::absolute','ompl::RNG::setSeed','std::srand','std::make_shared<ob::RealVectorStateSpace>','planner->setup()')))
ck('internal_guard_retained',d.count('FROZEN_LOCAL_FIXTURE_REQUIRED')==2 and 'BOUNDED_START_CHAIN_ONE_TO_THREE_REQUIRED' in d and '(parent||role==0)' in d)
masked=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:' '*len(m.group()),d,flags=re.S)
stack=[];pairs={')':'(',']':'[','}':'{'};ok=True
for c in masked:
 if c in '([{':stack.append(c)
 elif c in ')]}':
  if not stack or stack.pop()!=pairs[c]:ok=False;break
ck('CXX_lexical_delimiters_balanced_no_compiler',ok and not stack)
old=ROOT/'reports/p4_full_audit/draft_archive/sbl_shadow_v2_driver_before_local_preflight_20261017.cpp.txt'
ck('old_driver_exactly_retained',sha(old)=='4cc75e933dedd503f4c3e1668567958a2dd5c9f50912abdd23989eca7787b620')
oldtext=old.read_text();expected=oldtext.replace('std::string hexbytes(',pre+'std::string hexbytes(',1).replace('if(operation=="solve")p4sbl::require(request.at("solve_seconds")==10.,"ONE_NATIVE_TEN_SECOND_SOLVE_REQUIRED");','if(operation=="solve")p4sbl::require(request.at("solve_seconds")==10.,"ONE_NATIVE_TEN_SECOND_SOLVE_REQUIRED");if(operation=="local")local_preflight(request.at("fixture"));',1)
ck('only_pure_JSON_function_and_pre_model_call_added',expected==d)
failed=sum(not c['passed']for c in checks)
result=dict(schema='P4_SBL_SHADOW_V2_LOCAL_PREFLIGHT_STATIC_ADDENDUM_V1',personnel_independent=False,status='PASS_STATIC_TEXT_ONLY' if not failed else 'FAIL_RETAINED_STATIC',checks_total=len(checks),checks_passed=len(checks)-failed,checks_failed=failed,checks=checks,source_sha256={str(x.relative_to(ROOT)):sha(x) for x in (D,P,B,S,old,Path(__file__))},project_imports=0,text_transform_calls=0,compile_calls=0,binary_calls=0,model_calls=0,setup_calls=0,local_calls=0,solve_calls=0,limitations=['Pure text/AST self-check; no C++ compiler, JSON runtime rejection test or numerical validation.','Prior failed checker and prior independent certificate are retained; this addendum binds only the new preflight SHA.'])
with (ROOT/'reports'/(STEM+'.json')).open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
with (ROOT/'reports'/(STEM+'.md')).open('x')as f:f.write(f"# SBL shadow v2 local 前置拒绝静态补记\n\n状态 `{result['status']}`，{result['checks_passed']}/{len(checks)}。仅读取文本、Python AST 与保存字节，未 import 项目或运行编译/模型/setup/local/solve。人员独立性 false，不替代独审。\n\n新 local_preflight 在 request 解析及固定端点核验后、工作目录/seed/模型前执行；原内部 guard 保留。旧稿与旧静态失败证据逐字保留。工程 PRE 和其余五个工程资产保持最终冻结候选 SHA。\n")
print(json.dumps(dict(status=result['status'],checks_total=len(checks),checks_failed=failed,failures=[c for c in checks if not c['passed']],report_sha256=sha(ROOT/'reports'/(STEM+'.json')))))
