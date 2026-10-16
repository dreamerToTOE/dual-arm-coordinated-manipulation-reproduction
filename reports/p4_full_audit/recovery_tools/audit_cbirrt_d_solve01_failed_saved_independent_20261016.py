#!/usr/bin/env python3
"""Independent S01 failure/raw-prefix/cost audit. No native execution/import.

Subprocesses only read git blobs and disassemble the saved bound OMPL library.
Preserves every original byte. Failure is never promoted to transport/path PASS.
"""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import base64,datetime,hashlib,json,subprocess
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=ROOT/'results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE01'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json'
MARKER=b'P4_CBIRRT_D_TRACE '
def main():
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('PRESERVE_PREVIOUS_POST_NO_OVERWRITE')
    retained={};checks=[]
    def path(n):return Path(n)if Path(n).is_absolute()else ROOT/n
    def raw(n):
        p=path(n);b=p.read_bytes();retained[str(p)]=hashlib.sha256(b).hexdigest();return b
    def sha(n):return hashlib.sha256(raw(n)).hexdigest()
    def load(n):return json.loads(raw(n))
    def ck(n,ok):checks.append(dict(check=n,passed=bool(ok)))
    e=load(RUN/'execution.json');p=load(e['protocol']);claim=load(e['claim']);ext=p['external_supervision'];charge=load(ext['charge_path'])
    ck('original failure exact retained',e['status']=='STOP_PREFIX_RETAINED'and e['termination_reason']=="JSONDecodeError('Expecting value: line 1 column 1 (char 0)')"and e['complete_source_raw_evidence_gate']is False and e['independent_path_qualified']is False)
    ck('original committed frozen protocol exact',e['source_commit']=='6ac452b4f6edf0c4b396307c385c64a71073a8d0'and sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']=='1635899e7b025d5eaac57acf9e88345b8aa7f9304b4a521e2082129eee138c94'and p['frozen']is True and all(v is True for v in p['reviews'].values()))
    ck('claim protocol and all inputs unchanged',sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256']and claim['protocol_sha256']==e['protocol_sha256']and p['bound_files_sha256']==e['bound_files_sha256']==e['bound_files_after_sha256'])
    for n,h in p['bound_files_sha256'].items():ck('bound '+n,sha(n)==h)
    for n,h in p['own_source_sha256'].items():ck('committed '+n,hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest()==h)
    ck('frozen protocol blob',hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+e['protocol']],cwd=ROOT)).hexdigest()==e['protocol_sha256'])
    for n,h in p['prior_execution_sha256'].items():ck('prior '+n,sha(n)==h)
    ck('prior after exact unchanged',e['prior_execution_sha256']==p['prior_execution_sha256']==e['prior_execution_after_sha256']and e['actual_charge_prior']==p['actual_charge_prior'])
    journal=raw(e['evidence_journal']);rows=[json.loads(x)for x in journal.splitlines()if x.strip()];events=Counter(x['event']for x in rows)
    ck('whole journal intact hash',sha(e['evidence_journal'])==e['evidence_journal_sha256'])
    ck('only one request one raw nonJSON no parsed response',events==Counter(raw_pipe_chunk=5,setup=1,source_process_start_attempted=1,source_process_started=1,source_start_group=1,solve_request=1,raw_response_line=1,final_complete_raw_streams=1,final_counts=1)and next(x['request']for x in rows if x['event']=='solve_request')==p['request'])
    snap=next(x for x in rows if x['event']=='final_complete_raw_streams');streams={}
    for channel,info in snap['streams'].items():
        b=base64.b64decode(info['base64'],validate=True);streams[channel]=b;chunks=b''.join(base64.b64decode(x['base64'],validate=True)for x in rows if x['event']=='raw_pipe_chunk'and x['channel']==channel)
        ck(channel+' complete chunks snapshot binary identical',b==chunks==raw(RUN/f'source_{channel}.bin')and len(b)==info['bytes']and hashlib.sha256(b).hexdigest()==info['sha256'])
    stdout=streams['stdout'];line=next(x for x in rows if x['event']=='raw_response_line');rawline=base64.b64decode(line['base64'],validate=True)
    ck('exact first stdout debug line caused JSON failure',stdout==rawline==b'Debug:   CBiRRT: Planner range detected to be 3.415829\n'and line['bytes']==55)
    json_error=False
    try:json.loads(rawline)
    except json.JSONDecodeError:json_error=True
    ck('independent saved line parse confirms not JSON',json_error)
    trace=[];bad=[]
    for b in streams['stderr'].splitlines(keepends=True):
        if MARKER not in b:continue
        try:trace.append(json.loads(b.split(MARKER,1)[1]));ck('complete saved trace line',b.endswith(b'\n'))
        except(ValueError,UnicodeDecodeError):bad.append(hashlib.sha256(b).hexdigest())
    starts=Counter(x['kind']for x in trace if x['event']=='entered');ends=Counter(x['kind']for x in trace if x['event']=='completed');stack=[];pairs=[]
    for x in trace:
        if x['event']=='entered':stack.append(x)
        elif x['event']=='completed':
            a=stack.pop()if stack else {};ck('saved nested prefix return matches',a.get('id')==x['id']and a.get('kind')==x['kind']);pairs.append((a,x))
        else:ck('unexpected observed prefix event',False)
    ck('actual partial count boundary not manufactured closure',not bad and starts==Counter(native_ik=16,native_fk=2,mesh_load=1,identify=1,collision=1)and ends==Counter(native_ik=16,native_fk=2,mesh_load=1,identify=1)and len(stack)==1 and stack[0]['kind']=='collision'and stack[0]['id']==20)
    false_ik=[b['id']for a,b in pairs if b['kind']=='native_ik'and b['result'].get('returned')is False]
    ck('all false IK return bytes retained',false_ik==[3,5,7,8,9,10])
    ck('no observed tree mpaths reconstruct output',not any(x['kind']in('save_source_mpaths','state_reconstruct','vector_reconstruct','save_path')for x in trace)and e['original_native_output_sha256']=={}and e['original_native_output_fsync_completed']==[]and not any(q.is_file()for base in(RUN/'paths',RUN/'work/paths')if base.is_dir()for q in base.rglob('*')))
    registry=e['source_process_registry'];started=next(x for x in rows if x['event']=='source_process_started');sg=next(x for x in rows if x['event']=='source_start_group')
    ck('one dispatched one real process killed reaped not normal exit',e['counts']==dict(source_process_start_attempted=1,source_process_started=1,solve_dispatch_attempted=1,solve_dispatched=1,raw_response_lines_observed=1)and len(registry)==1 and registry[0]['pid']==started['pid']==sg['members'][0]['pid']==sg['members'][0]['pgrp']and len(sg['members'])==1 and registry[0]['reaped']is True and registry[0]['returncode']==-9 and snap['EOF']is True)
    ck('all20 runtime meshes original bound',len(e['runtime_mesh_sha256'])==20 and all(sha(n)==h for n,h in e['runtime_mesh_sha256'].items()))
    fields=raw(ext['sibling_path']).decode().split();elapsed,user,system=map(Decimal,fields[:3]);uw=float(elapsed+Decimal('.01'));uc=float(user+system+Decimal('.02'));meta=raw(ext['metadata_path']);planned,time_started,reaped=[json.loads(x)for x in meta.splitlines()];proof=e['supervisor_launch_proof'];st=path(ext['sibling_path']).stat();receiptlines=raw(RUN/'cost_receipt.jsonl').splitlines();receipt=json.loads(receiptlines[0])
    ck('failed exit1 complete finite GNUtime cost within frozen caps',len(fields)==4 and all(v.is_finite()and v>=0 for v in(elapsed,user,system))and fields[3]=='1'and uw<=min(30.,3600.-p['previous_r2_wall_s'])and uc<=min(60.,7200.-p['previous_r2_cpu_s']))
    ck('actual time PID reap failed status consistent',planned['event']=='planned_launch'and time_started['event']=='time_process_started'and reaped['event']=='time_process_reaped'and time_started['pid']==reaped['pid']==proof['actual_time_pid']==charge['time_process_pid']and reaped['returncode']==charge['time_returncode']==charge['measured_child_exit']==1 and reaped['failure']is charge['failure']is None and planned['supervisor_pid']==proof['supervisor_pid'])
    argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/'scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_draft.py'),'--protocol',str(path(e['protocol']))]
    ck('actual planned argv PID inode heldFD identity',argv==planned['argv']==time_started['argv']==proof['actual_argv']and st.st_ino==planned['time_inode']==proof['time_inode']and st.st_dev==planned['time_device']==proof['time_device']and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and hashlib.sha256(meta.splitlines(keepends=True)[0]).hexdigest()==proof['planned_launch_line_sha256'])
    ck('supervisor source binaries recipe original hashes',planned['protocol_sha256']==e['protocol_sha256']and planned['runner_sha256']==p['own_source_sha256']['scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_draft.py']and planned['supervisor_source_sha256']==p['own_source_sha256']['scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_draft.py']and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
    ck('failed charge original artifacts and upper exact',charge['execution_sha256']==sha(RUN/'execution.json')and charge['receipt_sha256']==sha(RUN/'cost_receipt.jsonl')and charge['time_sha256']==sha(ext['sibling_path'])and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr_sha256']==sha(ext['stderr_path'])and charge['time_fields']==fields and charge['wall_s']==uw and charge['cpu_s']==uc and charge['timing_valid']is charge['time_inode_unchanged']is charge['wall_CPU_caps_pass']is True and charge['completed_process_exit0']is False)
    ck('failure receipt full persistence measured and original unqualified',len(receiptlines)==1 and receipt['execution_sha256']==sha(RUN/'execution.json')and receipt['status']==e['status']=='STOP_PREFIX_RETAINED'and e['wall_s']<=receipt['wall_s_through_execution_persistence']<=uw and e['cpu_s']<=receipt['cpu_s_through_execution_persistence']<=uc and receipt['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and receipt['external_supervision_qualified']is e['external_supervision_qualified']is charge['external_supervision_qualified']is False)
    ck('all cost exclusions explicit',planned['supervision_cost_boundary']=='GNUtime child runner+all reaped source children. Supervisor own metadata/time-log fsync costs excluded.')
    driver=raw('baselines/p4_full/geometry_consistent/abb_cbirrt_d_driver_draft.cpp').decode();stage=Path(p['build_assets']['targets']['distance_destination_fix']['stage']);planner=raw(stage/'planners/CBiRRT_PCS.cpp').decode();lib=Path('/opt/ros/humble/lib/x86_64-linux-gnu/libompl.so');sha(lib);console=raw('/opt/ros/humble/include/ompl-1.7/ompl/util/Console.h').decode()
    logasm=subprocess.check_output(['objdump','-d','-C','--start-address=0x450bb0','--stop-address=0x450e30',str(lib)],text=True);rangeasm=subprocess.check_output(['objdump','-d','-C','--start-address=0x4368a0','--stop-address=0x4369d0',str(lib)],text=True)
    ck('OMPL actual logger uses stdcout iostream not printf for DEBUG', 'std::cout@GLIBCXX_3.4'in logasm and '__ostream_insert'in logasm and 'std::endl'in logasm and 'printf'not in logasm)
    ck('setup log lies outside driver quiet solve scope',driver.index('planner->setProblemDefinition(problem);planner->setup();')<driver.index('{Redirect quiet;\n                        const auto status=planner->solve')and 'Redirect():prior(std::cout.rdbuf(std::cerr.rdbuf())){}'in driver and 'sc.configurePlannerRange(maxDistance_);'in planner and 'ompl::msg::log'in rangeasm and 'OutputHandlerSTD'in console)
    ck('failure is engineering no formal physical VI upgrade',all(v==0 for v in e['zero_calls'].values())and e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and e['independent_path_qualified']is False and not e['diagnostics'])
    ck('all saved bytes unchanged',all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in retained.items()))
    failed=[x for x in checks if not x['passed']];ok=not failed
    report=dict(schema='P4_SOLVE01_SAVED_INDEPENDENT_POST_V1',status='FAIL_SOLVE01_TRANSPORT_EVIDENCE_INDEPENDENT_POST',audit_status='PASS_FAILED_PREFIX_PRESERVATION_AND_COST_AUDIT'if ok else'FAIL_FAILED_PREFIX_AUDIT',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),personnel_independent=True,reviewer='nr_entry_review; independent of S runner implementation',checks_total=len(checks),checks_passed=sum(x['passed']for x in checks),checks_failed=len(failed),failures=failed,external_supervision_qualified=ok,external_timing_qualified=ok,external_cost_qualified=ok,successful_transport_qualified=False,completed_process_exit0=False,source_response_complete=False,source_exact='UNKNOWN_NO_COMPLETE_SOURCE_RESPONSE',source_has_solution='UNKNOWN_SOURCE_INTERRUPTED',source_approximate='UNKNOWN_SOURCE_INTERRUPTED',source_tree_evidence='UNKNOWN_NO_SOURCE_RESPONSE_OR_TREE_EXPORT',source_mpaths_evidence='UNKNOWN_NO_SOURCE_RESPONSE_OR_MPATHS_OBSERVATION',observed_false_reconstruction_completions=0,total_false_reconstruction_completions='UNKNOWN_SOURCE_INTERRUPTED',observed_false_IK_ids=false_ik,unclosed_source_trace=[dict(id=x['id'],kind=x['kind'])for x in stack],actual_raw_trace_started=dict(starts),actual_raw_trace_completed=dict(ends),execution_sha256=sha(RUN/'execution.json'),external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),upper_wall_s=uw,upper_cpu_s=uc,external_time_fields=fields,execution_sample_wall_s=e['wall_s'],execution_sample_cpu_s=e['cpu_s'],charge_rule='Failed exit1 cost is qualified; replace execution internal samples once with independent external upper bounds, never add both. No transport or scientific qualification.',external_supervision_qualification_scope='IDENTITY_AND_FAILED_PROCESS_COST_ONLY_NOT_SUCCESSFUL_TRANSPORT',retained_sha256=retained,audit_script_sha256=sha(__file__),logging_root_cause=dict(classification='OUR_TRANSPORT_RECEIVER_AND_DRIVER_REDIRECT_SCOPE_ERROR',raw_stdout_line=stdout.decode(),actual_ompl_library_sha256=sha(lib),logger='OutputHandlerSTD::log DEBUG path loads std::cout and uses ostream insert/endl; not printf.',setup='CBiRRT::setup calls SelfConfig::configurePlannerRange; setup occurs before the driver Redirect quiet solve scope.',logger_objdump=logasm,range_objdump=rangeasm,recoverable_route='Versioned Python receiver may preserve only exact reviewed debug prefix as sideband and wait for the single actual JSON response. Preserve all raw; no source/science change or immediate retry authorized.'),new_import_runner_model_native_query_compile_protocol_prior_claim_commit_calls=0,limitations=['Original S01 remains STOP_PREFIX_RETAINED, JSONDecodeError, one dispatched request, no complete JSON response and source -9/reaped.','Observed stderr prefix has collision entered20 without completion. All downstream solve outcome, trees, milestones and mpaths remain UNKNOWN. Zero observed reconstruction returns is not proof that source has zero failed reconstructions.','No physical/path/PCS/NR/RSS or formal-statistical success. No rerun or new protocol was performed.','external_supervision_qualified covers failed-run identity/timing/cost only; successful_transport_qualified=false and completed_process_exit0=false.','GNUtime includes runner import/preflight/source/cleanup/journal/execution/receipt persistence/exit; supervisor own persistence overhead remains excluded.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write(f"# S01 失败前缀、保全及费用独立POST\n\n科学/transport结论仍为 FAIL_SOLVE01_TRANSPORT_EVIDENCE_INDEPENDENT_POST；保存审查{report['checks_passed']}/{len(checks)}通过，失败{len(failed)}。原STOP/JSONDecodeError、唯一dispatch、源-9/reaped保留。stdout仅55字节原debug行，无完整JSON；stderr原41条prefix完整保存，collision20 entered未返，树/M/回溯/求解结果全部UNKNOWN，不将无观测写成零。\n\n外层原exit1身份和完整费用链可核验，上界{uw}s墙钟/{uc}s CPU，external_supervision_qualified只限失败费用身份，successful_transport_qualified=false。内部样本保留，以上界替换一次。\n\n静态独立定位：实际绑定libompl的DEBUG logger使用std::cout/ostream_insert/endl，不是printf；driver planner->setup先于Redirect quiet solve作用域，setup调用configurePlannerRange产生原行。可研究版本化接收器精确保留日志sideband后等待唯一JSON；未修改源、未重跑。0科学/模型import/编译/protocol/prior/claim/commit，无路径物理PASS。\n")
    print(json.dumps({k:report[k]for k in('status','audit_status','checks_total','checks_passed','checks_failed','external_supervision_qualified','external_timing_qualified','successful_transport_qualified','upper_wall_s','upper_cpu_s')},ensure_ascii=False))
if __name__=='__main__':main()
