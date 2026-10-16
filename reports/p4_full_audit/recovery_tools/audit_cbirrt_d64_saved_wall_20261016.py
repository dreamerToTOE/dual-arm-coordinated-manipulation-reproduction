#!/usr/bin/env python3
"""Saved-only D64 wall diagnosis; no runner/model import, process or science."""
from pathlib import Path
from collections import Counter
import ast
import datetime as dt
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'results/p4_full/20261015_R2_ABB_CBIRRT_D_DISTANCE01'
REPORT = ROOT / 'reports/P4_FULL_R2_ABB_CBIRRT_D_DISTANCE01_SAVED_WALL_DIAGNOSIS_20261016'
RUNNER = ROOT / 'scripts/qualify_p4_full_r2_abb_cbirrt_d_distance_draft.py'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def timestamp(value):
    return dt.datetime.fromisoformat(value).timestamp()


def utc(value):
    return dt.datetime.fromtimestamp(value, dt.timezone.utc).isoformat()


def summarize(values):
    return dict(count=len(values), sum_s=math.fsum(values), minimum_s=min(values),
                median_s=statistics.median(values), maximum_s=max(values),
                negative_interval_count=sum(v < 0 for v in values))


def main():
    execution = json.loads((RUN / 'execution.json').read_text())
    protocol_path = ROOT / execution['protocol']
    claim_path = ROOT / execution['claim']
    inputs = sorted([p for p in RUN.rglob('*') if p.is_file()] +
                    [RUNNER, protocol_path, claim_path])
    before = {str(p.relative_to(ROOT)): dict(sha256=sha(p), bytes=p.stat().st_size,
              mtime_ns=p.stat().st_mtime_ns) for p in inputs}
    protocol = json.loads(protocol_path.read_text())
    events = [json.loads(line) for line in (RUN / 'events.jsonl').read_text().splitlines()]
    starts = {r['fixture']['dispatch_index']: timestamp(r['at_utc']) for r in events
              if r['event'] == 'distance_dispatch_started'}
    completed = {r['dispatch_index']: timestamp(r['at_utc']) for r in events
                 if r['event'] == 'distance_completed'}
    stopped = next(r for r in events if r['event'] == 'stopped')
    assert execution['status'] == 'STOP_FINAL_WALL_OR_CPU_BUDGET'
    assert sorted(starts) == list(range(62)) and sorted(completed) == list(range(61))
    assert execution['counts']['distance_dispatched'] == 62
    assert execution['counts']['distance_response_line_observed'] == 62
    assert [r['dispatch_index'] for r in execution['UNKNOWN_uncompleted_fixtures']] == [61, 62, 63]
    assert len(execution['source_process_registry']) == 8
    assert all(r['reaped'] for r in execution['source_process_registry'])
    assert execution['final_unreaped_registered_live_cpu_s'] == 0
    assert execution['diagnostics'] == []

    def artifact(i, suffix):
        return RUN / f'distance_{i:03d}_{suffix}'

    def marker(i, suffix):
        return artifact(i, suffix).stat().st_mtime_ns / 1e9

    marker_intervals = dict(
        request_write_marker_to_dispatch_event=[starts[i] - marker(i, 'request.json')
                                                for i in range(62)],
        dispatch_event_to_raw_line_write_marker=[marker(i, 'raw_response_line.bin') - starts[i]
                                                 for i in range(62)],
        raw_line_to_JSON_write_markers=[marker(i, 'raw_response.json') - marker(i, 'raw_response_line.bin')
                                        for i in range(61)],
        JSON_to_qualification_write_markers=[marker(i, 'qualification.json') - marker(i, 'raw_response.json')
                                             for i in range(61)],
        qualification_write_marker_to_completed_event=[completed[i] - marker(i, 'qualification.json')
                                                       for i in range(61)])
    rows = []
    for i in range(61):
        for name, a, b in [
            ('raw_line_to_JSON_write_markers', marker(i, 'raw_response_line.bin'), marker(i, 'raw_response.json')),
            ('JSON_to_qualification_write_markers', marker(i, 'raw_response.json'), marker(i, 'qualification.json')),
            ('qualification_write_marker_to_completed_event', marker(i, 'qualification.json'), completed[i])]:
            rows.append(dict(dispatch_index=i, interval=name, start_utc=utc(a), end_utc=utc(b),
                             approximate_elapsed_s=b-a))
    early_stall = next(r for r in sorted(rows, key=lambda r: r['start_utc'])
                       if r['approximate_elapsed_s'] >= .1)
    postresponse_sum = math.fsum(marker_intervals[k][i]
                               for k in list(marker_intervals)[2:] for i in range(61))

    raw62 = artifact(61, 'raw_response_line.bin').read_bytes()
    response62 = json.loads(raw62)
    stdout = (RUN / 'runtime/distance_destination_fix_trace_III.stdout').read_bytes().splitlines(keepends=True)
    assert raw62.endswith(b'\n') and raw62 == stdout[-1] and len(stdout) == 6
    assert response62['request'] == protocol['fixed_schedule'][61]['request']
    assert response62['source_dispatch_started'] == response62['source_dispatch_completed'] == 1
    assert response62['source_started'] == response62['source_completed'] == {'activeDistance': 1}
    assert not artifact(61, 'raw_response.json').exists()
    assert not artifact(61, 'qualification.json').exists()
    assert not any(artifact(i, 'request.json').exists() for i in (62, 63))

    source = RUNNER.read_text()
    ast.parse(source)
    final_sample = source.index('final_reaped_cpu=own_reaped_cpu()-cpu_start;final_live_cpu=direct_live_cpu(processes)')
    final_save = source.index("if folder.is_dir():durable_new(folder/'execution.json',record)")
    assert final_sample < final_save
    previous_wall = execution['previous_r2_wall_s']
    previous_cpu = execution['previous_r2_cpu_s']
    after_wall = math.fsum((previous_wall, execution['wall_s']))
    after_cpu = math.fsum((previous_cpu, execution['cpu_s']))
    start_epoch = timestamp(execution['started_at_utc'])
    stop_epoch = timestamp(stopped['at_utc'])
    output = dict(
        schema='P4_D64_SAVED_WALL_DIAGNOSIS_V1',
        created_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        status='SAVED_ONLY_ENGINEERING_WALL_STOP_DIAGNOSIS_NO_RETRY_NO_PASS',
        author='nr_local_independent_post; D64 runner author, not personnel-independent',
        personnel_independent=False,
        source_commit=execution['source_commit'], run_status_unchanged=execution['status'],
        run_execution_sha256=sha(RUN / 'execution.json'),
        observed_counts=dict(frozen_fixtures=64, actual_dispatched=62, response_lines_observed=62,
                             raw_line_files_present=62, raw_line_persistence_counter_completed=61,
                             raw_JSON_and_qualification_completed=61,
                             runner_UNKNOWN_dispatch_indices=[61, 62, 63],
                             never_dispatched_indices=[62, 63],
                             actual_raw_trace_started=execution['actual_raw_trace_started'],
                             actual_raw_trace_completed=execution['actual_raw_trace_completed']),
        partial62=dict(dispatch_index=61, case_id=response62['request']['case_id'],
                       raw_path=str(artifact(61, 'raw_response_line.bin').relative_to(ROOT)),
                       raw_sha256=sha(artifact(61, 'raw_response_line.bin')), bytes=len(raw62),
                       complete_JSON_line=True, matches_final_stdout_line=True,
                       source_interface_completed_not_qualified=True,
                       runner_qualification_not_completed=True,
                       raw_line_fsync_completion='UNKNOWN_SIGNAL_CAN_PRECEDE_POST_FSYNC_COUNTER',
                       arithmetic_pass_not_inferred_from_presence=True),
        earliest_saved_boundaries=dict(
            started_at_utc=execution['started_at_utc'], first_dispatch_utc=utc(starts[0]),
            first_raw_line_write_marker_utc=utc(marker(0, 'raw_response_line.bin')),
            first_qualification_completed_utc=utc(completed[0]),
            earliest_post_response_marker_interval_at_least_100ms=early_stall,
            last_completed_dispatch_index=60, last_completed_utc=utc(completed[60]),
            partial62_dispatch_utc=utc(starts[61]),
            partial62_raw_line_write_marker_utc=utc(marker(61, 'raw_response_line.bin')),
            stopped_event_utc=stopped['at_utc'], ended_at_utc=execution['ended_at_utc']),
        wall_cpu=dict(reported_wall_s=execution['wall_s'], reported_CPU_s=execution['cpu_s'],
                      reported_wall_minus_aggregate_CPU_s=execution['wall_s']-execution['cpu_s'],
                      aggregate_CPU_divided_by_wall=execution['cpu_s']/execution['wall_s'],
                      self_and_all_reaped_children_CPU_s=execution['final_self_and_reaped_children_cpu_s'],
                      unreaped_registered_live_CPU_s=0., all8_reaped=True,
                      cleanup_specific_CPU_s='UNOBSERVED_NO_PHASE_RUSAGE_SAMPLES',
                      source_activeDistance_specific_wall_CPU_s='UNOBSERVED_NO_BODY_TIMESTAMPS',
                      stopped_event_to_final_measured_sample_approx_s=execution['wall_s']-(stop_epoch-start_epoch)),
        marker_interval_summaries={k:summarize(v) for k,v in marker_intervals.items()},
        post_response_marker_intervals_61_total_approx_s=postresponse_sum,
        largest_post_response_marker_intervals=sorted(rows, key=lambda r:r['approximate_elapsed_s'], reverse=True)[:10],
        evidence_interpretation=[
            'The measured STOP is the fixed run wall cap, not a recorded numeric gate failure or exhausted CPU cap.',
            'Approximately 10.54s lies between already-returned raw-response write markers and qualification-completed events; these intervals are parent evidence/validation/scheduling work, not that request activeDistance body.',
            'At least245 per-request fsync calls completed:62 request+61 raw-line+61 parsed-JSON+61 qualification. The62nd raw-line fsync was attempted; its completion isUNKNOWN.',
            'Repeated approximately42ms marker intervals and low aggregateCPU strongly support evidence-persistence/I-O or scheduling overhead as the engineering bottleneck. No syscall timing proves fsync latency, storage-device cause, or exact source runtime.',
            'UTC events and filesystem mtime markers differ by about1ms on some logically ordered boundaries;49 dispatch-to-raw intervals are slightly negative. These markers are approximate diagnostic intervals, never a calibrated profiler.',
            'Saved counters/source narrow the interruption to partial62 raw-line persistence before its retained counter increment. Exactopen/write/flush/fsync cause requires a retained traceback/syscall trace; no new timing experiment was run.',
            'No observer trace mismatch is inferred from the final session14actual vs12expected events: the extra complete pair belongs to the returned partial62 that had not entered the runner response list.',
            'Finalwall/CPU samples precede execution.json serialization/fsync and terminal output. Those final costs are unmeasured; originalexecution remains immutable and reportedcost is not a complete process-lifetime measurement.'
        ],
        budget=dict(fixed_D_wall_cap_s=15., fixed_D_CPU_cap_s=30.,
                    fixed_D_run_expired_no_retry_or_resume=True, new_D_allocation_authorized=False,
                    measured_R2_after_this_run_wall_s=after_wall, measured_R2_after_this_run_CPU_s=after_cpu,
                    measured_R2_remaining_wall_s=3600.-after_wall,
                    measured_R2_remaining_CPU_s=7200.-after_cpu,
                    remaining_large_R2_cap_does_not_reauthorize_D=True,
                    VI_constructed=974, VI_remaining=0),
        next_engineering_items_not_executed=[
            'Version any future evidence-persistence redesign separately; preserve every original byte and every failure. Keep the64fixedcases, numericalgates, sourceversions andUNKNOWNs.',
            'Add no-science phase timing and include final record persistence in process-lifetime accounting before requesting any fresh qualification budget.',
            'Any future D run needs a separately reviewed protocol and explicitnew budget; this STOP cannot be retried/resumed or converted into a fullPASS.',
            'L12 draft preparation may continue without source execution; no planning or formalTableI scope is enabled.'
        ],
        source_observation_counts=dict(new_runner_import=0, new_model_query=0, new_source_binary=0,
                                       new_compile=0, new_claim=0, new_scientific_execution=0,
                                       new_prior_snapshot=0, new_commit=0),
        input_files_sha256_bytes_mtime_ns=before)
    assert before == {str(p.relative_to(ROOT)): dict(sha256=sha(p), bytes=p.stat().st_size,
                     mtime_ns=p.stat().st_mtime_ns) for p in inputs}
    output['all_inputs_unchanged_after_read'] = True
    with REPORT.with_suffix('.json').open('x') as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    markdown = f'''# D64 保存证据墙钟诊断

本报告仅用stdlib读取保存文件、事件、源码和mtime；作者参与过runner实现，因此不标人员独立。未执行模型、binary、编译、科学请求、新claim或重跑。原execution及所有raw保持原样，状态仍为`{execution['status']}`。

实际请求62/64、观察到62行响应，runner完成61项资格。第62项index61的完整JSON行与最后stdout逐字节一致，含原body entry/return；但未进入rawJSON和qualification持久化阶段，不能补算为runner完整成功。原UNKNOWN[61,62,63]保留，其中62/63从未dispatch。

已测墙钟{execution['wall_s']:.12f}秒、总CPU{execution['cpu_s']:.6f}秒，8个Popen均已reaped，无登记liveCPU。清理专用CPU与activeDistance本体时间没有阶段采样，均UNOBSERVED。stop事件后至最终已测sample约{execution['wall_s']-(stop_epoch-start_epoch):.6f}秒，包含回收、哈希和保存尾部，不能当作纯清理耗时。

61个已返回响应在raw-line写入marker、JSON写入marker、qualification写入marker和complete事件之间合计约{postresponse_sum:.6f}秒。三个后处理区间中位数均约42毫秒，首个至少100毫秒的区间为index9，{early_stall['start_utc']}起。最大区间为index57 JSON到qualification约451毫秒。62项request写入到dispatch事件合计约{math.fsum(marker_intervals['request_write_marker_to_dispatch_event']):.6f}秒。每项有4次单独durable保存：至少245次per-request fsync已完成，另第62raw-line fsync完成状态UNKNOWN。

这些证据支持父级证据保存、I/O或调度开销是本次主要工程瓶颈；不能据此归因为原论文理论错误、源距离函数算术失败或CPU预算不足。没有独立syscall计时，不能把上述窗口全部叫作fsync耗时，也不能判定具体存储设备故障。mtime与UTC存在约1毫秒边界差，49条dispatch到raw写marker为微小负值，所以不以这些marker代替校准计时器。

保存资料把中断收敛到第62raw-line持久化至其retained计数之前；精确open/write/flush/fsync位置需保留的traceback或syscall日志。最终会话14actual/12expected trace多出的完整pair属于该partial，不是已经证明observer产生额外调用。

记账边界另有明确限制：最终wall/CPU sample在execution.json序列化/fsync和终端输出之前，其额外成本未测。原数字原样保留并报告这一限制，不改写历史。

按保存own-cost相加，R2现为墙钟{after_wall:.12f}秒、CPU{after_cpu:.6f}秒；大帽余额约{3600.-after_wall:.12f}/{7200.-after_cpu:.6f}秒。这不重新授权D64固定15/30项；D64已到墙钟帽且禁止retry/resume，VI仍974/974。未来任何D证据管道或记账修订必须独立版本化、冻结、申请新预算，保持原64清单和判据。L12可继续草案准备，不能执行。

完整输入hash、mtime、分段描述及限制见同名JSON。全部输入读前读后hash、bytes、mtime一致。
'''
    with REPORT.with_suffix('.md').open('x') as stream:
        stream.write(markdown)
    print(json.dumps(dict(report_json=str(REPORT.with_suffix('.json').relative_to(ROOT)),
                          report_json_sha256=sha(REPORT.with_suffix('.json')),
                          report_md_sha256=sha(REPORT.with_suffix('.md')),
                          post_response_marker_intervals_approx_s=postresponse_sum,
                          all_inputs_unchanged=True, new_scientific_executions=0)))


if __name__ == '__main__':
    main()
