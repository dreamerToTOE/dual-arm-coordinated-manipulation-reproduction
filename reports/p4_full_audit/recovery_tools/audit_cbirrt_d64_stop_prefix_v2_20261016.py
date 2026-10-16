#!/usr/bin/env python3
"""Append saved raw-prefix audit; never repair/restart the original D64 run."""
from pathlib import Path
from collections import Counter,defaultdict
import datetime
import hashlib
import json
import math
import struct

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=ROOT/'results/p4_full/20261015_R2_ABB_CBIRRT_D_DISTANCE01'
FIRST=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_DISTANCE01_SAVED_INDEPENDENT_POST_20261016.json'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_DISTANCE01_STOP_RAW_PREFIX_INDEPENDENT_POST_V2_20261016.json'
MARKER=b'P4_CBIRRT_D_TRACE '

def exact(a,b):
    if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
    if type(a)in (int,float)and type(b)in (int,float):return struct.pack('>d',a)==struct.pack('>d',b)
    if type(a)is not type(b):return False
    if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
    if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
    return a==b

def main():
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('ORIGINAL_POST_PRESERVED_NO_OVERWRITE')
    checks=defaultdict(lambda:dict(total=0,passed=0));failed=[];retained={}
    def path(n):
        n=Path(n);return n if n.is_absolute()else ROOT/n
    def raw(n):
        n=path(n);b=n.read_bytes();retained[str(n)]=hashlib.sha256(b).hexdigest();return b
    def load(n):return json.loads(raw(n))
    def ck(g,k,v):
        checks[g]['total']+=1;checks[g]['passed']+=bool(v)
        if not v:failed.append(dict(group=g,check=k))
    e=load(RUN/'execution.json');p=load(e['protocol']);first=load(FIRST)
    ck('original','original full science STOP preserved',e['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET' and e['termination_reason']=="TimeoutError('D64_AGGREGATE_HARD_WALL_CAP')")
    ck('original','prior saved audit pass original STOP',first['status']=='PASS_SAVED_EVIDENCE_AUDIT' and first['checks_total']==first['checks_passed']==1062 and first['original_scientific_status']==e['status'] and first['execution_sha256']==hashlib.sha256(raw(RUN/'execution.json')).hexdigest())
    ck('original','budget full own cost no PASS',e['wall_s']==15.463848030998633 and e['wall_s']>=p['budget']['wall_s']==15. and exact(e['cpu_s'],.9817729999999999) and e['final_unreaped_registered_live_cpu_s']==0 and e['cpu_s']==e['final_self_and_reaped_children_cpu_s'])
    schedule=p['fixed_schedule'];rawresponses={};qualified=[];allrows=[]
    for f in schedule:
        i=f['dispatch_index'];prefix=RUN/f'distance_{i:03d}';rp=prefix.with_name(prefix.name+'_raw_response_line.bin');jp=prefix.with_name(prefix.name+'_raw_response.json');qp=prefix.with_name(prefix.name+'_qualification.json')
        if not rp.exists():continue
        b=raw(rp);r=json.loads(b);rawresponses[i]=r;c=p['fixed_contexts'][f['context_index']]
        ck('raw',str(i)+' complete exact one JSONL',b.endswith(b'\n')and len(b.splitlines())==1 and exact(r['request'],f['request'])and exact(load(prefix.with_name(prefix.name+'_request.json')),f['request']))
        if jp.exists():ck('raw',str(i)+' existing rawJSON identical',exact(load(jp),r))
        if qp.exists():qualified.append(i)
        ck('response',str(i)+' returned true original interface',r['status']=='SOURCE_INTERFACE_COMPLETED_NOT_QUALIFIED' and r['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1' and r['operation']=='distance' and r['environment']==f['environment'] and r['mode']==f['mode'] and r['source_dispatch_started']==r['source_dispatch_completed']==1)
        ck('scope',str(i)+' no source solve/formal/path',r['solve_calls']==r['formal_table_I_calls']==0 and r['independent_path_qualified']is False)
        qa=f['request']['qa12'];qb=f['request']['qb12'];role=f['request']['active_chain'];part=slice(6*role,6*(role+1))
        ref=math.sqrt(math.fsum((x-y)**2 for x,y in zip(qa[part],qb[part])))if f['factor']=='distance_destination_fix'or role==0 else math.sqrt(math.fsum(v*v for v in qb[6:]))
        ck('arithmetic',str(i)+' exact saved reference and tolerance',exact(ref,c[f['factor']+'_reference_rad']) and math.isfinite(r['distance'])and abs(r['distance']-ref)<=1e-12)
        for k in ('qa12','qb12'):ck('states',str(i)+' '+k,exact(r[k+'_after'],f['request'][k])and r[k+'_binary64_after']==struct.pack('>12d',*f['request'][k]).hex())
        allrows.append(dict(dispatch_index=i,case_id=f['case_id'],factor=f['factor'],mode=f['mode'],actual_distance_rad=r['distance'],reference_rad=ref,absolute_error_rad=abs(r['distance']-ref),original_runner_qualified=qp.exists(),raw_response_json_existed=jp.exists(),raw_line_sha256=hashlib.sha256(b).hexdigest()))
    ck('counts','62 complete raw returns versus61 runner complete',list(rawresponses)==list(range(62))and qualified==e['completed_dispatch_ids']==list(range(61))and e['counts']['distance_completed']==61)
    ck('counts','actual dispatch62 raw counter61 fsync interrupted',e['counts']['distance_dispatch_attempted']==e['counts']['distance_dispatched']==e['counts']['distance_response_line_observed']==62 and e['counts']['raw_distance_response_lines_retained']==e['counts']['raw_distance_response_JSON_retained']==61)
    ck('counts','original UNKNOWN[61,62,63] unchanged',[f['dispatch_index']for f in e['UNKNOWN_uncompleted_fixtures']]==[61,62,63])
    ck('counts','not dispatched62and63 no artifacts',all(not list(RUN.glob(f'distance_{i:03d}*'))for i in (62,63)))
    streams=defaultdict(list)
    for f in schedule:streams[(f['factor'],f['mode'],f['environment'])].append(f)
    starts=Counter();ends=Counter();pair_results=[];raw_count=0
    for group,fixtures in streams.items():
        binding=e['source_raw_trace_bindings']['/'.join(group)];stdout=raw(binding['raw_streams']['stdout']['path']);stderr=raw(binding['raw_streams']['stderr']['path']);responses=[rawresponses[f['dispatch_index']]for f in fixtures if f['dispatch_index']in rawresponses]
        lines=stdout.splitlines(keepends=True);events=[];tails=[]
        for line in stderr.splitlines():
            if MARKER not in line:continue
            try:events.append(json.loads(line.split(MARKER,1)[1]))
            except (ValueError,UnicodeDecodeError):tails.append(hashlib.sha256(line).hexdigest())
        raw_count+=len(lines)
        ck('streams','/'.join(group)+' entire stdout covers actual raw returns',len(lines)==len(responses)and all(exact(json.loads(a),b)for a,b in zip(lines,responses))and all(x.endswith(b'\n')for x in lines))
        ck('streams','/'.join(group)+' both complete original hashes',all(hashlib.sha256(b).hexdigest()==binding['raw_streams'][k]['sha256']and len(b)==binding['raw_streams'][k]['bytes']for k,b in (('stdout',stdout),('stderr',stderr))))
        ck('streams','/'.join(group)+' raw EOF all drained',binding['pipe_EOF_drained']is True and binding['cleanup_closed']is True and binding['unexpected_stdout_tail_bytes']==0 and not tails)
        expected=[]
        if group[1]=='trace':
            expected+=responses[0]['construction']['trace']
            for r in responses:expected+=r['trace']
        ck('trace','/'.join(group)+' actual complete constructor and raw responses once',exact(events,expected))
        for event in events:
            if event['event']=='entered':starts[event['kind']]+=1
            if event['event']=='completed':ends[event['kind']]+=1
    ck('counts','actual all62 stdout complete',raw_count==62)
    ck('trace','4mesh30body actual raw starts and returns',starts==ends==Counter(mesh_load=4,activeDistance=30)and dict(starts)==e['actual_raw_trace_started']and dict(ends)==e['actual_raw_trace_completed'])
    ck('trace','live qualification29trace excludes one raw-only30th',e['counts']['trace_activeDistance_started']==e['counts']['trace_activeDistance_completed']==29)
    for traceidx in (i for i in rawresponses if schedule[i]['mode']=='trace'):
        t=rawresponses[traceidx];f=schedule[traceidx];plainidx=next(s['dispatch_index']for s in schedule if s['factor']==f['factor']and s['mode']=='plain'and s['case_id']==f['case_id']);q=rawresponses[plainidx]
        def normal(r):
            excl=('mode','source_counts_observed','source_started','source_completed','trace');r={k:v for k,v in r.items()if k not in excl};r['construction']={k:v for k,v in r['construction'].items()if k not in excl};return r
        ok=exact(normal(q),normal(t));ck('pairs',f['case_id']+' '+f['factor'],ok);pair_results.append(dict(plain_index=plainidx,trace_index=traceidx,passed=ok,original_runner_qualified=traceidx in qualified))
    ck('pairs','30saved pairs but only29live qualified',len(pair_results)==30 and sum(x['original_runner_qualified']for x in pair_results)==29)
    registry=e['source_process_registry'];ck('processes','8actually started and all8reaped',len(registry)==e['source_processes_started']==e['source_process_started_events']==8 and len({r['pid']for r in registry})==8 and all(r['reaped']is True for r in registry))
    ck('processes','7normal plus final killed',Counter(r['returncode']for r in registry)==Counter({0:7,-9:1})and e['source_process_registry_complete_gate']is True)
    stopped=load(RUN/'stopped_partial_request.json');ck('original','partial index61 raw retained stage',stopped['fixture']['dispatch_index']==61 and stopped['stage']=='SOURCE_DISPATCH_STARTED')
    ck('preservation','all original read bytes unchanged',all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in retained.items()))
    report=dict(schema='P4_CBIRRT_D64_STOP_RAW_PREFIX_INDEPENDENT_POST_V2',status='PASS_SAVED_STOP_PREFIX_AUDIT_ORIGINAL_STOP_UNCHANGED'if not failed else'FAIL_SAVED_STOP_PREFIX_AUDIT',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review, independent of D64 runner',personnel_independent=True,original_status=e['status'],checks_total=sum(x['total']for x in checks.values()),checks_passed=sum(x['passed']for x in checks.values()),checks_failed=len(failed),groups=dict(checks),failures=failed,original_denominator=64,original_completed=61,original_UNKNOWN=[61,62,63],actual_dispatched=62,actual_complete_raw_returns=62,not_dispatched=[62,63],saved_only_extra_return_index61=True,original_runner_index61_qualified=False,independent_saved_arithmetic_and_state_pairs_only=True,actual_raw_trace_started=dict(starts),actual_raw_trace_completed=dict(ends),saved_plain_trace_pair_count=30,original_live_trace_qualified_pairs=29,all8Popen_reaped=True,original_wall_s=e['wall_s'],original_cpu_s=e['cpu_s'],raw_responses=allrows,saved_plain_trace_pairs=pair_results,first_audit_sha256=hashlib.sha256(raw(FIRST)).hexdigest(),audit_script_sha256=hashlib.sha256(raw(__file__)).hexdigest(),retained_sha256=retained,new_compile_binary_science_query_claim_protocol_prior_commit_calls=0,limitations=['Index61 complete raw response is independently parsed from preserved .bin/stdout; original runner qualification remains absent and UNKNOWN.','No source model/function/binary was rerun and no failed/timeout run is promoted to PASS_FIXED16.','Final killed process has complete available pipe EOF; that proves preserved raw prefix only.','15swall cap exhausted; no permission for further source calls or formal experiments is inferred.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write(f"# D64 STOP 原始前缀独立后审 V2\n\n{report['status']}：{report['checks_passed']}/{report['checks_total']}，失败{len(failed)}。原STOP_FINAL_WALL_OR_CPU_BUDGET、61/64完整资格和UNKNOWN[61,62,63]保持。\n\n实际dispatch/完整raw均62；index61的2710字节JSONL与最后stdout行完全相同，已有完整返回、保存算术/state/plain-trace匹配，但原runner未完成JSON/qualification落盘，仍UNKNOWN。index62/63未dispatch。全部raw无截断尾；真实trace为4次mesh和30次distance各entry/return，原29个live-qualified trace保持。\n\n8个Popen均回收，7个exit0、末个SIGKILL；原wall15.463848030998633s/CPU.981773s，15/30预算未重置。保存新增算术核对不等于原运行64门通过。新增科学/编译/binary/claim/protocol/prior/commit均0。\n")
    print(json.dumps({k:report[k]for k in ('status','checks_total','checks_passed','checks_failed')},ensure_ascii=False))

if __name__=='__main__':main()
