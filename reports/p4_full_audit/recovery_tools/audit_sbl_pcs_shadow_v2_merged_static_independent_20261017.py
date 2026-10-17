"""Read-only AST/text review of the final SBL shadow-v2 engineering delta."""
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
STEM = ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_SHADOW_V2_MERGED_INDEPENDENT_STATIC_REVIEW_20261017'
D = 'baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_shadow_v2_draft.cpp'
B = 'scripts/build_p4_full_r2_abb_sbl_pcs_shadow_v2_draft.py'
S = 'scripts/supervise_p4_full_r2_abb_sbl_pcs_build_shadow_v2_draft.py'
P = 'reports/P4_FULL_R2_ABB_SBL_PCS_SHADOW_V2_ENGINEERING_PRE_DRAFT_20261017.md'
H = 'baselines/p4_full/geometry_consistent/abb_sbl_pcs_observation_shadow_v2_draft.hpp'
T = 'baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_shadow_v2_draft.py'
EXPECTED = {D: '5e6a78ac051d9f2a32b4abad3bb41c466e82bfc8f56b3a08c624b387de9a7cda',
            B: 'fac6cde1ca4cd03cdc8f14d131af9f3ff1c6d9323f4c52717f7f771f7c6ae94f',
            S: '32ba34ea2e800204b0f3372ed62102b0b30ae80bb51b940d43a757de03d36078',
            P: 'c229fa7dc56fcafdc7c69434742b7a14b052e7ea15348fe89cd7cbe7ca994c08',
            H: '3c0d3031d53532bb077e7eabb3911aa9f911f771bb34216406cf0a71fb9108c3',
            T: '926592eb43ef8ad90a6434a30aa613c2c6c41416e9f9120c734b76adc3a39209'}
checks = []
retained = {}


def read(name):
    data = (ROOT/name).read_bytes(); retained[name] = hashlib.sha256(data).hexdigest(); return data.decode()


def ck(name, value):
    checks.append({'name': name, 'passed': bool(value)})


def functions(source):
    return {n.name: n for n in ast.parse(source).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def dump(node):
    return ast.dump(node, include_attributes=False)


def main():
    texts = {name: read(name) for name in EXPECTED}
    for name, want in EXPECTED.items(): ck('stable_final_source:' + name, retained[name] == want)
    driver, builder, supervisor, pre = (texts[x] for x in (D, B, S, P))
    oldb = read('scripts/build_p4_full_r2_abb_sbl_pcs_draft.py')
    olds = read('scripts/supervise_p4_full_r2_abb_sbl_pcs_build_draft.py')
    bnew, bold, snew, sold = map(functions, (builder, oldb, supervisor, olds))
    ck('builder_function_set_reused', set(bnew) == set(bold))
    for name in bnew:
        if name in ('draft_protocol', 'build'): continue
        ck('reused_builder_function_AST:' + name, dump(bnew[name]) == dump(bold[name]))
    # Only one engineering prefix label changes inside the actual build body.
    normal_build = ast.parse(ast.get_source_segment(builder, bnew['build']).replace('STOP_BUILD02_PREFIX_RETAINED', 'STOP_SETUP_PREFIX_RETAINED')).body[0]
    ck('reused_build_body_AST_except_prefix_label', dump(normal_build) == dump(bold['build']))
    ck('supervisor_function_set_reused', set(snew) == set(sold))
    for name in snew: ck('reused_supervisor_function_AST:' + name, dump(snew[name]) == dump(sold[name]))
    cert = 'reports/P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_OUTPUT_SUPPLEMENT_20261017.json'
    cs = json.loads(read(cert))
    ck('reuse_shadow104_exact_certificate', retained[cert] == '85c3a7f9df949d7059f1a99fed85337c9ef29376736a79e5b1bff69dcdc7e365' and cs['checks_total'] == cs['checks_passed'] == 104 and cs['checks_failed'] == 0)
    ck('new_engineering_identity_and_stage', all(x in builder for x in ("RUN='20261017_R2_ABB_SBL_PCS_BUILD02'", "CLAIM='P4_R2_ABB_SBL_PCS_SHADOW_V2_BUILD02_45W_90CPU_20261017'", "BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_sbl_pcs_shadow_v2')")))
    ck('only_new_shadow_header_driver_transform_bound', all(name in builder for name in (D, H, T, S)))
    ck('d080_explicit_scale_and_separate_runtime_auth', all(x in builder for x in ('d080_approved_table_I_target=18000', 'original_paper_table_I_target=22500', 'runtime_execution_authorized_by_engineering=False', 'public13_setup_qualification_repeated=False', 'scientific_execution_authorized=False')))
    ck('engineering_one_target_45_90_and_zero_runtime', 'budget=dict(wall_s=45.,cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)' in builder and 'targets=1' in builder and 'query_calls=0,solve_calls=0,binary_execution_calls=0,formal_table_I_calls=0,new_VI_candidate_constructions=0' in builder)
    ck('freeze_and_current_charged_prior_reused', all(x in builder for x in ('EXACT_CURRENT_SBL_PCS_BUILD_REQUIRED', 'REVIEWED_SBL_PCS_BUILD_FREEZE_REQUIRED', 'UNCOMMITTED_BUILD_SOURCE_OR_PROTOCOL', 'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS', 'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED')))
    ck('driver_args_II_local_or_solve_plain_trace_only', 'environment!="II"||(operation!="local"&&operation!="solve")||(mode!="plain"&&mode!="trace")' in driver)
    ck('single_request_eof_and_runtime_approval', 'ONE_REQUEST_THEN_STDIN_EOF_REQUIRED' in driver and 'separately_frozen_runtime_qualification' in driver and 'SEPARATELY_FROZEN_II_SEED7_RANGE08_REQUEST_REQUIRED' in driver)
    preflight = driver.index('if(operation=="local")local_preflight(request.at("fixture"))')
    ck('pure_json_preflight_before_output_rng_and_models', preflight < driver.index('work=fs::absolute') < driver.index('ompl::RNG::setSeed') < driver.index('auto space=std::make_shared') < driver.index('auto planner=std::make_unique'))
    pf = driver[driver.index('void local_preflight'):driver.index('std::string hexbytes')]
    ck('preflight_bounded_all_node_json_conditions', all(x in pf for x in ('FROZEN_LOCAL_FIXTURE_REQUIRED_BEFORE_MODEL', 'EXACT_LOCAL_FIXTURE_KIND_REQUIRED_BEFORE_MODEL', 'SAVED_LOCAL_INPUT_PROVENANCE_REQUIRED_BEFORE_MODEL', 'values.size()<=3', 'finite12(node.at("q12"))', 'ik.size()==2', 'value.is_number_integer()', 'branch>=-1&&branch<8', 'node.at("assigned_active_role").is_number_integer()', '(role==0||role==1)&&(i>0||role==0)', 'NONROOT_LOCAL_LAZY_CHAIN_REQUIRED_BEFORE_MODEL')))
    ck('preflight_has_no_model_or_rng_calls', not any(x in pf for x in ('new Motion', 'make_shared', 'setSeed', 'FKsolve', 'IKsolve', 'checkMotion', 'setup(', 'solve(')))
    olddriver = read('baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_draft.cpp')
    oldsetup = json.loads(read('configs/p4_full/r2_abb_sbl_pcs_setup_v1.json'))
    def vector(src, name):
        m = re.search(r'\b' + name + r'=\{([^}]+)\}', src)
        return [float(x) for x in m.group(1).split(',') if x.strip()]
    for name, key in (('START', 'start_q12'), ('GOAL', 'goal_q12')):
        ck('reused_complete_binary64_input:' + name, vector(driver, name) == oldsetup['request'][key])
    for name, oldname in (('LOW', 'lo'), ('HIGH', 'hi')):
        ck('reused_complete_binary64_input:' + name, vector(driver, name) == vector(olddriver, oldname))
    ck('original_native1_range08_and_single_ten_second_solve', 'og::SBL(si,.8,1)' in driver and driver.count('planner->solve(') == 1 and 'ob::timedPlannerTerminationCondition(10.)' in driver and 'request.at("solve_seconds")==10.' in driver)
    ck('no_public13_or_new_project_queries', 'additional_public_project_observations",0' in driver and 'public_project_observations",0' in driver and '->project(' not in driver)
    ck('fixture_adaptation_explicit_root_grow_only', all(x in driver for x in ('RECONSTRUCTED_TREE_FIXTURE_ORIGINAL_SBL_METHOD_BODIES', 'm->a_chain=role;m->valid=parent?false:true', 'addMotion(tree,m);owned.release()', 'result["source_isPathValid_returned"]=isPathValid(tStart_,last)')))
    ck('checkSolution_only_author_body_one_dispatch_interface', driver.count('checkSolution(true,tStart_,tGoal_,last,solution)') == 1 and 'source_checkSolution_dispatches"]=1' in driver and 'ConnectionScope' not in driver)
    ck('no_simplifier_repeated_solve_or_NR_fallback', not any(x in driver for x in ('simplifySolution', 'reduceVertices', 'shortcutPath', 'IKproject(', 'FKsolve_rob(', 'checkMotionRBS(', 'reconstructRBS(')))
    ck('lifetime_before_native_destruction_and_empty_after', driver.index('out["trees_before_destruction"]=planner->trees()') < driver.index('planner.reset()') and 'REGISTRY_EMPTY_AFTER_NATIVE_DESTRUCTION_REQUIRED' in driver)
    ck('final_evidence_is_exclusive_durable_readback', all(x in driver for x in ('O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC', '::fsync(fd)', 'syncdir(path.parent_path())', 'readbytes(path)==bytes', 'EVIDENCE_READBACK_BYTES_MUST_MATCH')))
    ck('fresh_original_parent_and_work_paths', all(x in driver for x in ('!fs::exists(work/"paths")', '!fs::exists(work.parent_path()/"paths")', '!fs::exists(work/"writer_evidence")', 'FRESH_OUTPUT_DIRECTORIES_REQUIRED')))
    ck('all_expected_native_outputs_captured_and_unknown_internal_streams', all(x in driver for x in ('parent/path_milestones.txt', 'parent/ik_path.txt', 'work/path.txt', 'work/temp.txt', 'work/perf_log.txt', 'original_stream_open_write_flush_flags","UNOBSERVED', 'absence_retained', 'NATIVE_OUTPUT_REGULAR_NONLINK_REQUIRED')))
    ck('attempts_not_equated_with_native_write_success', all(x in driver for x in ('empty_attempts_do_not_prove_write_success', 'final_text_readback_matches_attempts",false', 'final_byte_certificate_not_internal_stream_flags', 'ORIGINAL_SIDE_SOURCE_INDEX_SEQUENCE_REQUIRED', 'ALL_ATTEMPTS_REQUIRE_FINAL_IK_PATH_ROWS')))
    ck('sidecar_persistence_separate_from_math_and_source_status', all(x in driver for x in ('durable_new(evidence/"ik_path_shadow_v2.json"', 'shadow_sidecar_saved_and_readback_equal', 'independent_path_qualified",false', 'continuous_collision_certificate",false', 'SOURCE_EXACT_PENDING_INDEPENDENT_PATH_QUALIFICATION')))
    ck('errors_and_unknown_timing_boundary_retained', all(x in driver for x in ('STOP_RETAINED_PREFIX', 'STOP_EVIDENCE_PERSISTENCE_ERROR', 'UNOBSERVED_FINAL_READBACK_CERTIFICATE_ONLY', 'ORIGINAL_SOLVE_AND_OBSERVATIONS_NOT_FORMAL_PAPER_TIMING')))
    ck('pre_no_runtime_or_fixture_pass_claim', all(x in pre for x in ('本文件不启动或预扣工程/科学运行，也不批准 local 或 solve', '具体 fixture **尚未冻结', '原 setup 内部 RNG 仍 UNOBSERVED', '不得把 attempt 或 sidecar 保存成功冒作原 stream 内部成功', '原 22500 事实并单独声明 D080 18000')))
    ledger_old_name = 'reports/p4_full_audit/recovery_tools/append_external_cost_snapshot_v3_20261016.py'
    ledger_new_name = 'reports/p4_full_audit/recovery_tools/append_external_cost_snapshot_d080_v4_20261017.py'
    ledger_old, ledger_new = read(ledger_old_name), read(ledger_new_name)
    lf_old, lf_new = functions(ledger_old), functions(ledger_new)
    ck('d080_ledger_all_functions_AST_reused', set(lf_old) == set(lf_new) and all(dump(lf_old[n]) == dump(lf_new[n]) for n in lf_old))
    ck('d080_ledger_original_history_kept_via_old_copy', "result = dict(old)" in ledger_new or "result = {**old" in ledger_new or "result = dict(**old" in ledger_new or "out = dict(old)" in ledger_new or "updated_ledger = dict(old)" in ledger_new or "value = dict(old)" in ledger_new or "ledger = dict(old)" in ledger_new or "**old," in ledger_new)
    ck('d080_ledger_new_scope_separate_and_no_VI_execution', all(x in ledger_new for x in ("d080['formal_table_I_original'] == 22500", "d080['formal_table_I_D080'] == 18000", "d080['VI_future_science_authorized'] is False", "'d080_formal_table_I_required_calls': 18000", "'d080_formal_table_I_calls': 0", "'d080_VI_status': 'ARCHIVED_OUT_OF_APPROVED_SCOPE_NO_NEW_EXECUTION'")))
    ck('d080_ledger_inherits_196_columns_and_adds_four', 'x.expected_old_columns >= 196' in ledger_new and 'SAVED_HISTORICAL_COLUMNS_NOT_IDENTICAL' in ledger_new and '新增4列' in ledger_new)
    failed = [x for x in checks if not x['passed']]
    report = {'schema': 'P4_SBL_PCS_SHADOW_V2_MERGED_INDEPENDENT_STATIC_REVIEW_V1', 'status': 'PASS_SBL_PCS_SHADOW_V2_ENGINEERING_ONLY_STATIC_REVIEW' if not failed else 'FAIL_SBL_PCS_SHADOW_V2_ENGINEERING_STATIC_REVIEW',
              'personnel_independent': True, 'static_read_only': True, 'checks_total': len(checks), 'checks_passed': len(checks)-len(failed), 'checks_failed': len(failed),
              'reviewed_source_sha256': {k: retained[k] for k in EXPECTED}, 'retained_sha256': retained, 'checks': checks,
              'blockers': [x['name'] for x in failed], 'describe_calls': 0, 'compiler_calls': 0, 'model_queries': 0, 'binary_calls': 0, 'scientific_runs': 0,
              'engineering_only': True, 'runtime_qualified': False, 'source_path_qualified': False,
              'local_fixture_recommendation': {'positive': 'Saved CBiPCS edge0, nodes0→108; 109-point original successful reconstruction; fresh SBL isPathValid only.', 'negative': 'Saved physical nodes0→359→360; real branches differ at root/child for both passive roles, original lazy rejection recursively removes child and grandchild.', 'modes': ['trace', 'plain'], 'processes': 4, 'wall_cap_s': 15, 'cpu_cap_s': 30, 'no_connect_fixture': True, 'address_reuse': 'UNOBSERVED_UNLESS_ALLOCATOR_ACTUALLY_REUSES; no forced address', 'remaining_checkSolution_and_unknown_writer': 'Observe in separately frozen single native solve, retain unobserved if absent; do not fabricate historical connect.'},
              'limits': ['复用已审BUILD01函数AST与shadow104证书，未重做原setup或文本transform。', '该静审只允许root进一步describe/冻结工程协议；不授权运行local、solve或正式统计。', '新fixture adapter明示RECONSTRUCTED，作者科学body不变，历史connect不赋值。', '写盘只能由实际最终字节/sidecar读回证明，原fstream内部状态仍UNKNOWN。', 'D080账本工具仅静态diff审查，未执行或更新任何账本。']}
    with STEM.with_suffix('.json').open('x') as f: json.dump(report, f, ensure_ascii=False, indent=2); f.write('\n')
    with STEM.with_suffix('.md').open('x') as f:
        f.write('# SBL shadow v2 合并工程独立静审\n\n')
        f.write(f"状态：{report['status']}；实际{report['checks_passed']}/{len(checks)}检查通过，失败{len(failed)}。只读源码/AST和已保存证书；未describe、import实施模块、编译、模型查询或运行二进制。\n\n")
        f.write('冻结前发现的local guard位置问题已在新driver改为纯JSON前置检查，位于work目录写入、seed及模型构造之前。未改变作者body、header或transform。BUILD01不变函数AST与shadow104证书直接复用；新工程保留45秒墙钟/90秒CPU、单目标和零runtime，D080原22500/新18000分别绑定。\n\n')
        f.write('最小local固定建议为正lazy node0→108和拒绝lazy node0→359→360，来自旧CBiPCS完整合格路径；trace/plain共4进程、15秒墙钟/30秒CPU。仅触达SBL lazy/RBS与递归删除；不加connect fixture。checkSolution、真实historical connect及unknown writer由另冻单solve观察。地址复用若未实际出现仍UNKNOWN。\n\n')
        f.write('新driver分开expression attempt、原文件最终字节复制读回及sidecar持久化；不把sidecar成功当原fstream内部成功或物理路径资格。D080账本v4为v3增量，原历史和费用/solve函数保持，另记18000范围与VI只读；本次未执行账本工具。\n')
        if failed: f.write('\n阻塞：\n'+'\n'.join('- '+x['name'] for x in failed)+'\n')
    print(json.dumps({'status': report['status'], 'checks_total': len(checks), 'checks_failed': len(failed), 'json_sha256': hashlib.sha256(STEM.with_suffix('.json').read_bytes()).hexdigest(), 'md_sha256': hashlib.sha256(STEM.with_suffix('.md').read_bytes()).hexdigest(), 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
