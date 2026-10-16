#!/usr/bin/env python3
"""Static/metadata-only H runner review; no processes/models/queries/builds.

Mock pipes contain invented text bytes, not robot configurations. This reviewer
did not author the scientific runner but implemented its small raw-tail repair.
"""
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'scripts/qualify_p4_full_r2_abb_random_helper_h_draft.py'
PRE = ROOT / 'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_PRE_DRAFT_20261015.md'
OUTPUT = ROOT / 'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_SCIENCE_RAW_TAIL_ROOT_REVIEW_20261016'
checks = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check(name, passed, **evidence):
    checks.append(dict(check=name, passed=bool(passed), **evidence))


def contains(text, *needles):
    return all(n in text for n in needles)


def review():
    sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
    spec = importlib.util.spec_from_file_location('h_static_metadata_review_target', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = SOURCE.read_text()
    tree = ast.parse(text)
    top_imports = [ast.unparse(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    check('stdlib_and_pure_builder_top_imports', not any('numpy' in s or 'oracle' in s or 'physical_nr' in s or 'collision_adapter' in s for s in top_imports), imports=top_imports)
    check('explicit_raw_log_gates', module.GATES['raw_trace_response_binary64_exact'] is True and module.GATES['cleanup_pipe_eof_and_empty_stdout_tail'] is True)
    check('exact_signed_zero_distinguishes', module.exact([0.0], [-0.0]) is False)
    check('exact_binary64_distinguishes_adjacent', module.exact([1.0], [1.0000000000000002]) is False)
    check('exact_bool_not_integer', module.exact(True, 1) is False)
    check('exact_identical_nested_shape', module.exact({'q':[1.25,-0.0],'returned':False},{'q':[1.25,-0.0],'returned':False}))
    old = json.loads((ROOT / 'configs/p4_full/r2_abb_random_helper_h_qualification_v1.draft.json').read_text())
    contexts = old['fixed_contexts']
    check('fixed_all16_contexts', len(contexts)==16 and len({v['case_id'] for v in contexts})==16)
    check('exact_4centers_2roles_2seeds', {(v['environment'],v['endpoint_source'],v['active_chain'],v['seed']) for v in contexts} == {(env,f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/{env}_{i}.json',role,seed) for env in ('II','III') for i in (0,1) for role in (0,1) for seed in (7,17)})
    for c in contexts:
        endpoint = json.loads((ROOT / c['endpoint_source']).read_text())
        check('fixed_center_bits.'+c['case_id'], module.exact(c['q12'],endpoint['selected_q_rad']))
    check('64_fixed_dispatches_no_new_fixture', contains(text, "require(len(contexts)==16 and len(schedule)==64", "for factor in builder.FACTORS:", "for mode in ('plain','trace'):"))
    check('32_plain_trace_binary64_pairs', contains(text, "exact(normalize_response(plain),normalize_response(trace))", "len(comparisons)==32"))
    check('16_first_success_prefixes', contains(text, "exact(ot[:stop+1],ft[:-1])", "BREAK_MUST_EXIT_DIRECTLY_AFTER_FIRST_SUCCESS", "len(prefixes)==16"))
    check('source_original_false_and_all8', contains(text, "ORIGINAL_NORMAL_CONTROL_RETURN_MUST_BE_FALSE", "ORIGINAL_MUST_COMPLETE_ALL8_BRANCHES"))
    check('no_success_identical_final_and_trace', contains(text, "fixed['returned'] is False and exact(original['q12'],fixed['q12']) and exact(ot,ft)"))
    check('active_bits_exact_all_outputs', contains(text, "bits(response['q12'][a])==bits(request['q12'][a])"))
    check('all64_false_and_true_final_queue', contains(text, "for fixture in spec['fixed_schedule']:", "response=responses[(factor,mode,case)];q=response['q12']", "ALL64_HELPERS_REQUIRED", "len(physical)==64"))
    check('missing_source_identity_not_guessed', contains(text, "'status':'NOT_OBSERVED'", "exact(join_q(e['args']),final_q)"))
    check('dual_source_label_arm_mapping', "label in current['branches'][1-index]['branch_set']" in text)
    check('direct_label_passive_mapping', contains(text, "passive=1-fixture['active_chain']", "direct in current['branches'][passive]['branch_set']"))
    check('separate_source_and_physical_gates', contains(text, "source_policy_discrete_collision_free=", "physical_final_qualified=", "source_branch_relation_qualified=", "final_candidate_all_gates_qualified=", "source_success_fully_qualified="))
    check('true_closure_or_branch_soundness_stop', contains(text, "source_true_math_sound=", "H_SOURCE_TRUE_INDEPENDENT_MATH_OR_BRANCH_SOUNDNESS_FAILED"))
    check('ordinary_collision_or_limit_reject_not_source_bool', "all64_physical_pass_not_required_for_interface_control_flow_qualification=True" in text)
    check('all_outputs_collision_no_screen', contains(text, "collision=adapter.check_collision(env,q", "max_collision_adapter_calls':64", "max_collision_native_worker_queries':128"))
    check('bound_aligned_pose_policy', contains(text, "collision.get('selected_variant')=='aligned'", "collision.get('status')=='CHECKED'", "PQP_QUERY_ERROR"))
    adapter = (ROOT / 'baselines/p4_full/geometry_consistent/collision_adapter.py').read_text()
    check('adapter_CHECKED_requires_aligned_physical_TCP', contains(adapter, "elif not preferred['pose_consistency']['passed']:", "answer['status']='COLLISION_PHYSICAL_TCP_MISMATCH'", "answer['collision']=preferred['native_collision'];answer['status']='CHECKED'"))
    check('budget_current_r2_caps', contains(text, "3600.-spec['previous_r2_wall_s']", "7200.-spec['previous_r2_cpu_s']", "signal.setitimer(signal.ITIMER_REAL,.02,.02)"))
    check('budget_own_reaped_and_live_descendants', contains(text, "resource.RUSAGE_SELF", "resource.RUSAGE_CHILDREN", "parent in family", "cpu_total()-self.cpu_start>=self.cpu_cap"))
    check('final_cost_includes_cleanup_and_hashes', text.index("record.update(wall_s=time.monotonic()-begun,cpu_s=cpu_total()-cpu_start)") > text.index("record['bound_files_after_sha256']=after") and text.index("record.update(wall_s=time.monotonic()-begun,cpu_s=cpu_total()-cpu_start)") > text.index("adapter.close_sessions()"))
    check('final_budget_cancels_pass', "record['status']='STOP_WALL_OR_CPU_BUDGET_PREFIX_RETAINED'" in text)
    check('complete_unknown_tail_not_trimmed', contains(text, "uncompleted_helper_fixtures=[f for f in spec['fixed_schedule']", "uncompleted_final_fixtures=[f for f in spec['fixed_schedule']", "UNKNOWN_NOT_EXECUTED_OR_NOT_COMPLETED_NO_PREFIX_PASS"))
    check('raw_false_true_unmodified_saved_first', text.index("helper_{i:03d}_raw_response_line.bin") < text.index("response=json.loads(raw)"))
    check('raw_collision_before_added_provenance', contains(text, "result=original_collision_query(session,q,timeout_s)", "collision_worker_{j:03d}_raw_response.json"))
    check('plain_internal_and_rand_unobserved', contains(text, "UNOBSERVED_NOT_INFERRED_FROM_TRACE_OR_STRUCTURE", "UNOBSERVED_NOT_INFERRED_FROM_STRUCTURAL_448"))
    check('no_scientific_retry_or_seed_change', contains(text, "OUTPUT_OR_CLAIM_EXISTS_NO_RETRY", "no_retry_reset_or_resume':True"))
    check('EOF_not_fixed_read_rounds', "while self.selector.get_map():" in text and "for _ in range(4):" not in text)
    check('raw_binary64_completed_response_binding', "exact(prefix['events'],expected)" in text)
    check('extra_tail_and_incomplete_trace_cancel_PASS', contains(text, "not prefix['tails'] and not session.pending", "STOP_RAW_TRACE_OR_PIPE_TAIL_NOT_COMPLETE"))
    # Metadata-only mock: six text chunks exceed the old four-select loop.
    # There is no real pipe, child process, binary or robot input here.
    class Capture(io.BytesIO):
        def close(self):
            self.saved=self.getvalue();super().close()
    class File:
        def __init__(self,fd):self.fd=fd
        def fileno(self):return self.fd
    class Selector:
        def __init__(self):
            self.keys={1:SimpleNamespace(fileobj=File(1),data='stderr'),2:SimpleNamespace(fileobj=File(2),data='stdout')}
            self.select_count=0
        def get_map(self):return self.keys
        def select(self,*_):self.select_count+=1;return [(self.keys[min(self.keys)],None)]
        def unregister(self,stream):self.keys.pop(stream.fileno())
        def close(self):pass
    session=module.HelperSession.__new__(module.HelperSession)
    session.closed=False;session.eof_drained=False;session.pending=b''
    session.stdout=Capture();session.stderr=Capture();session.selector=Selector()
    session.proc=SimpleNamespace(poll=lambda:0,wait=lambda **_:0)
    chunks=[('invented-tail-'+str(n)+'\n').encode() for n in range(6)]
    buffers={1:[*chunks,b''],2:[b'']};original_read=module.os.read
    try:
        module.os.read=lambda fd,_:buffers[fd].pop(0)
        session.close()
    finally:module.os.read=original_read
    check('mock_6chunk_tail_fully_preserved', session.stderr.saved==b''.join(chunks), select_calls=session.selector.select_count)
    check('mock_both_pipe_EOF_and_closed', session.eof_drained and session.closed and not session.selector.get_map())
    check('mock_no_invented_stdout_tail', session.stdout.saved==b'' and session.pending==b'')
    return checks


if __name__=='__main__':
    if OUTPUT.with_suffix('.json').exists() or OUTPUT.with_suffix('.md').exists():
        raise FileExistsError('Preserve prior static review')
    review()
    failed=[c for c in checks if not c['passed']]
    report=dict(schema='P4_H_SCIENCE_INDEPENDENT_STATIC_METADATA_REVIEW_V1',
        status='PASS_STATIC_METADATA_PENDING_BUILD_AND_FRESH_PROTOCOL' if not failed else 'FAIL_STATIC_METADATA',
        checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),
        scientific_runner_original_author=False,logging_repair_implemented_by_reviewer=True,
        new_scientific_calls=0,new_compile_calls=0,new_helper_dispatches=0,
        source_sha256=sha(SOURCE),PRE_sha256=sha(PRE),review_script_sha256=sha(__file__),
        required_next='Root reviews logging-only change; actual two-target build succeeds; generate new scientific protocol from this runner with actual newest prior ledger, then separately freeze/commit. Existing v1 draft is superseded preparation, not executable.',
        failed_checks=failed,checks=checks)
    with OUTPUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    with OUTPUT.with_suffix('.md').open('x')as f:
        f.write(f'''# ABB helper H 科学 runner 独立静态审查

**{report['status']}**：{report['checks_passed']}/{report['checks_total']} 通过，{report['checks_failed']} 失败。0 新科学调用、0 编译、0 helper 派发。

审查人未编写原科学 runner；按 root 授权实施了本次日志完整性小修。保留全部16 context×2控制流×2 mode=64请求、原始源布尔值和原数值门。核对32 plain/trace binary64配对、16首次双身份成功前缀、所有false/true终态数学/源branch/限位/aligned碰撞分列、原helper无碰撞查询契约、真实父子CPU与最终含清理实账、完整UNKNOWN尾部。

日志小修使transport在reap后读取两pipe至EOF，并要求每session原始stderr与全部已完成响应trace逐事件binary64相等；不可解析trace尾部、额外stdout或未EOF均不能取得完整PASS。中断prefix仍保存且保持UNKNOWN。只用6块虚构文本的mock验证超过旧4轮的尾部仍完整读取，没有真实pipe/process/query或机器人输入。

本报告仅静态审查与纯metadata反例，不认定H已编译或通过科学资格。root须复核本日志修正；两个真实工程目标成功后，必须从当前science runner另存新协议、绑定实际最新prior并独立冻结。旧builder生成的v1草案不能直接执行。本次没有更新H prior或运行任何科学程序。

修前runner/PRE已逐字节归档到聊天work/h_science_raw_tail_recovery_20261016。源码、PRE和本审查脚本的SHA见同名JSON。
''')
    print(json.dumps({k:report[k]for k in ('status','checks_total','checks_passed','checks_failed','source_sha256','PRE_sha256')},ensure_ascii=False))
