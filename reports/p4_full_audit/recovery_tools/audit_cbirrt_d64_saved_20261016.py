#!/usr/bin/env python3
"""Independent D64 saved-only audit; never import or execute runner or binary.

Only stdlib saved bytes, binary64, distance arithmetic and git-show are used.
No FK/IK/model/RNG/RBS/collision/solve/compile/claim/protocol/prior generation.
"""
from pathlib import Path
from collections import Counter,defaultdict
import datetime
import hashlib
import json
import math
import struct
import subprocess

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=ROOT/'results/p4_full/20261015_R2_ABB_CBIRRT_D_DISTANCE01'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_DISTANCE01_SAVED_INDEPENDENT_POST_20261016.json'
MARKER=b'P4_CBIRRT_D_TRACE '

def exact(a,b):
    if isinstance(a,bool) or isinstance(b,bool):return type(a)is type(b) and a==b
    if type(a)in (int,float) and type(b)in (int,float):return struct.pack('>d',a)==struct.pack('>d',b)
    if type(a)is not type(b):return False
    if isinstance(a,list):return len(a)==len(b) and all(exact(x,y)for x,y in zip(a,b))
    if isinstance(a,dict):return set(a)==set(b) and all(exact(a[k],b[k])for k in a)
    return a==b

def normalized(r):
    remove=('mode','source_counts_observed','source_started','source_completed','trace')
    r={k:v for k,v in r.items()if k not in remove}
    r['construction']={k:v for k,v in r['construction'].items()if k not in remove}
    return r

def main():
    if not (RUN/'execution.json').is_file():raise SystemExit('SAVED_EXECUTION_NOT_READY_NO_ACTION')
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_REPORT_PRESERVED')
    groups=defaultdict(lambda:dict(total=0,passed=0));failed=[];retained={}
    def path(n):
        n=Path(n);return n if n.is_absolute()else ROOT/n
    def read(n):
        n=path(n);b=n.read_bytes();retained[str(n)]=hashlib.sha256(b).hexdigest();return b
    def sha(n):return hashlib.sha256(read(n)).hexdigest()
    def load(n):return json.loads(read(n))
    def ck(g,k,ok):
        groups[g]['total']+=1;groups[g]['passed']+=bool(ok)
        if not ok:failed.append(dict(group=g,check=k))
    e=load(RUN/'execution.json');p=load(e['protocol']);claim=load(e['claim'])
    complete=e['status']=='PASS_FIXED16_ACTIVE_DISTANCE_INTERFACE'
    ck('provenance','exact distance-only scope',e['run_id']==p['run_id']==RUN.name and e['not_planner_or_path_qualification']is True and e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0)
    ck('provenance','frozen root and independent reviews',p['frozen']is True and all(v is True for v in p['reviews'].values()))
    ck('provenance','protocol and claim unchanged',sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']==claim['protocol_sha256'] and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'])
    ck('provenance','bound before and after exact',e['bound_files_sha256']==p['bound_files_sha256']==e['bound_files_after_sha256'])
    for n,h in p['bound_files_sha256'].items():ck('assets',n,sha(n)==h)
    for n,h in p['own_source_sha256'].items():
        blob=subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)
        ck('committed',n,hashlib.sha256(blob).hexdigest()==h)
    blob=subprocess.check_output(['git','show',e['source_commit']+':'+e['protocol']],cwd=ROOT)
    ck('committed','exact protocol',hashlib.sha256(blob).hexdigest()==e['protocol_sha256'])
    prior=[load(n)for n in p['prior_execution_sha256']]
    ck('budget','all prior own costs once',e['prior_execution_sha256']==e['prior_execution_after_sha256']==p['prior_execution_sha256'] and math.fsum(r['wall_s']for r in prior)==p['previous_r2_wall_s']==e['previous_r2_wall_s'] and math.fsum(r['cpu_s']for r in prior)==p['previous_r2_cpu_s']==e['previous_r2_cpu_s'])
    ck('budget','original15/30 caps',p['budget']==dict(wall_s=15.,cpu_s=30.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.))
    ck('budget','final full CPU association',exact(e['cpu_s'],e['final_self_and_reaped_children_cpu_s']+e['final_unreaped_registered_live_cpu_s']))
    if complete:ck('budget','complete PASS under full own cap',e['wall_s']<min(15.,3600.-e['previous_r2_wall_s']) and e['cpu_s']<min(30.,7200.-e['previous_r2_cpu_s']) and e['final_unreaped_registered_live_cpu_s']==0)
    ck('scope','all zero scientific counters',all(v==0 for v in e['zero_calls'].values()) and e['zero_calls']==p['zero_calls'])
    ck('scope','plain and RNG internals remain unobserved',e['source_body_plain_true_started_completed']=='UNOBSERVED_NO_PLAIN_BODY_TRACE' and e['direct_rng_member_true_started_completed']=='UNOBSERVED_LIBRARY_NOT_HOOKED' and e['library_seed_draws']=='UNOBSERVED_NOT_INFERRED')
    schedule=p['fixed_schedule'];contexts=p['fixed_contexts'];bygroup=defaultdict(list)
    ck('schedule','unchanged16/64',len(contexts)==16 and len(schedule)==64 and [r['dispatch_index']for r in schedule]==list(range(64)))
    for s in schedule:bygroup[(s['factor'],s['mode'],s['environment'])].append(s)
    ck('schedule','8fixedgroups each8',len(bygroup)==8 and all(len(v)==8 for v in bygroup.values()))
    references={};diagonals=[]
    for c in contexts:
        role=c['active_chain'];part=slice(6*role,6*(role+1));a=c['qa12'];b=c['qb12']
        correct=math.sqrt(math.fsum((x-y)**2 for x,y in zip(a[part],b[part])))
        original=correct if role==0 else math.sqrt(math.fsum(x*x for x in b[6:]))
        ck('references',c['case_id'],exact(correct,c['distance_destination_fix_reference_rad']) and exact(original,c['source_control_reference_rad']))
        references[(c['case_id'],'source_control')]=original;references[(c['case_id'],'distance_destination_fix')]=correct
        if role==1 and c['diagonal']:diagonals.append(dict(case_id=c['case_id'],saved_original_reference_rad=original))
    ck('references','four original unique nonzero self cases',len(diagonals)==4 and all(x['saved_original_reference_rad']>0 for x in diagonals))
    responses={};metrics={};retained_raw_return_ids=[];original_rejected_retained=[]
    for s in schedule:
        i=s['dispatch_index'];base=RUN/f'distance_{i:03d}';req=base.with_name(base.name+'_request.json');rp=base.with_name(base.name+'_raw_response.json');qp=base.with_name(base.name+'_qualification.json')
        if req.is_file():ck('request',str(i),exact(load(req),s['request']))
        if not rp.is_file():continue
        r=load(rp);raw=read(base.with_name(base.name+'_raw_response_line.bin'))
        retained_raw_return_ids.append(i)
        ck('raw',str(i)+' line and JSON',raw.endswith(b'\n') and exact(json.loads(raw),r))
        if not qp.is_file():original_rejected_retained.append(i);continue
        q=load(qp);metricref=references[(s['case_id'],s['factor'])];c=contexts[s['context_index']]
        ck('response',str(i)+' exact interface request',r['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1' and r['status']=='SOURCE_INTERFACE_COMPLETED_NOT_QUALIFIED' and r['environment']==s['environment'] and r['mode']==s['mode'] and r['operation']=='distance' and exact(r['request'],s['request']))
        ck('response',str(i)+' dispatch and scope',r['source_dispatch_started']==r['source_dispatch_completed']==1 and r['solve_calls']==r['formal_table_I_calls']==0 and r['independent_path_qualified']is False)
        ck('distance',str(i)+' independent saved arithmetic',math.isfinite(r['distance']) and r['distance']>=0 and abs(r['distance']-metricref)<=1e-12 and exact(q['independent_reference_rad'],metricref) and exact(q['actual_distance_rad'],r['distance']) and exact(q['absolute_error_rad'],abs(r['distance']-metricref)))
        if c['diagonal']:ck('distance',str(i)+' diagonal',r['distance']==0 if s['factor']=='distance_destination_fix' or c['active_chain']==0 else r['distance']>0)
        for k in ('qa12','qb12'):ck('states',str(i)+' '+k,exact(r[k+'_after'],s['request'][k]) and struct.pack('>12d',*s['request'][k]).hex()==r[k+'_binary64_after'])
        co=r['construction'];trace=s['mode']=='trace'
        ck('construction',str(i)+' transport actual and structural scopes',co['cbirrt_constructor_dispatch_completed']==co['ompl_setSeed_calls_completed']==1 and co['svc_only_constructor_dispatch_completed']==co['srand_calls_completed']==0 and co['source_direct_rng_member_initializations_structural']==1 and co['source_direct_rng_member_true_started_completed']=='UNOBSERVED_LIBRARY_NOT_HOOKED' and co['library_internal_seed_draws']=='UNOBSERVED_NOT_REPORTED_ZERO')
        ck('trace',str(i)+' explicit flags',r['source_counts_observed']is trace and co['source_counts_observed']is trace)
        if trace:
            a,b=r['trace'];u,v=co['trace']
            ck('trace',str(i)+' original function entry return',a['event']=='entered' and b['event']=='completed' and a['kind']==b['kind']=='activeDistance' and a['id']==b['id']==1 and r['source_started']==r['source_completed']=={'activeDistance':1} and exact(a['args']['qa12'],s['request']['qa12']) and exact(a['args']['qb12'],s['request']['qb12']) and a['args']['active_chain']==s['request']['active_chain'] and exact(b['result']['distance'],r['distance']))
            ck('trace',str(i)+' original construction entry return',u['event']=='entered' and v['event']=='completed' and u['kind']==v['kind']=='mesh_load' and u['id']==v['id']==1 and u['args']==v['result']=={} and co['source_started']==co['source_completed']=={'mesh_load':1})
        else:ck('trace',str(i)+' plain internals null',all(x[k]is None for x in (r,co)for k in ('trace','source_started','source_completed')))
        responses[(s['factor'],s['mode'],s['case_id'])]=r;metrics[i]=q
    expected_completed=[s['dispatch_index']for s in schedule if(s['factor'],s['mode'],s['case_id'])in responses]
    ck('counts','completed IDs and UNKNOWN exact',e['completed_dispatch_ids']==expected_completed and e['UNKNOWN_uncompleted_fixtures']==[s for s in schedule if s['dispatch_index']not in expected_completed])
    if complete:ck('counts','full64 only complete PASS',len(responses)==64 and not original_rejected_retained and e['counts']['distance_completed']==e['counts']['distance_dispatched']==64)
    pairstats=[]
    for factor in ('source_control','distance_destination_fix'):
        for c in contexts:
            a=responses.get((factor,'plain',c['case_id']));b=responses.get((factor,'trace',c['case_id']))
            if a is not None and b is not None:
                ok=exact(normalized(a),normalized(b));ck('pairs',factor+' '+c['case_id'],ok);pairstats.append(ok)
    rawstarts=Counter();rawends=Counter();processes=[]
    for group,fixtures in bygroup.items():
        key='/'.join(group);binding=e['source_raw_trace_bindings'].get(key)
        if binding is None:continue
        actual=[];tails=[];rawstdout=b''
        for channel,info in binding['raw_streams'].items():
            raw=read(info['path']);ck('streams',key+' '+channel,hashlib.sha256(raw).hexdigest()==info['sha256'] and len(raw)==info['bytes'])
            if channel=='stdout':rawstdout=raw
            else:
                for line in raw.splitlines():
                    if MARKER not in line:continue
                    try:actual.append(json.loads(line.split(MARKER,1)[1]))
                    except (ValueError,UnicodeDecodeError):tails.append(hashlib.sha256(line).hexdigest())
        expected=[];seen=[]
        for s in fixtures:
            r=responses.get((s['factor'],s['mode'],s['case_id']))
            if r is None:continue
            if not seen and group[1]=='trace':expected+=r['construction']['trace']
            if seen:ck('construction',key+' repeated metadata',exact(r['construction'],seen[0]['construction']))
            seen.append(r)
            if group[1]=='trace':expected+=r['trace']
        for row in actual:
            if row['event']=='entered':rawstarts[row['kind']]+=1
            if row['event']=='completed':rawends[row['kind']]+=1
        if complete:
            ck('streams',key+' all8stdout JSON only',len(rawstdout.splitlines())==8 and all(exact(json.loads(a),b)for a,b in zip(rawstdout.splitlines(),seen)))
            ck('streams',key+' exact construction once then8traces',exact(actual,expected) and not tails and binding['raw_trace_binary64_matches']is True)
            ck('streams',key+' complete EOF return0',binding['complete_raw_evidence_gate']is True and binding['startup_complete']is True and binding['pipe_EOF_drained']is True and binding['cleanup_closed']is True and binding['unexpected_stdout_tail_bytes']==0 and binding['process_returncode']==0)
        processes.append(dict(group=key,raw_trace_events=len(actual),qualified_responses=len(seen),retained_unparseable_trace_lines=len(tails)))
    ck('counts','raw actual body counts exact',dict(rawstarts)==e['actual_raw_trace_started'] and dict(rawends)==e['actual_raw_trace_completed'])
    events=[json.loads(x)for x in read(RUN/'events.jsonl').splitlines()];ec=Counter(x['event']for x in events)
    ck('counts','actual source process started from durable events',ec['source_process_started']==e['source_process_started_events']==e['counts'].get('source_process_started_events',0))
    if complete:
        ck('counts','8constructor processes all reaped',len(e['source_process_registry'])==e['source_processes_started']==e['source_process_started_events']==e['registered_transport_sessions']==e['completed_CBIRRT_constructor_dispatches']==8 and all(r['reaped']is True and r['returncode']==0 for r in e['source_process_registry']) and e['source_process_registry_complete_gate']is True)
        ck('counts','4mesh32distance actual trace each',rawstarts==rawends==Counter(mesh_load=4,activeDistance=32) and e['full_run_raw_body_count_gate']is True and not e['unregistered_runtime_raw_prefixes'])
        ck('counts','32plain trace pairs',len(pairstats)==32 and e['plain_trace_comparisons']==32)
        ck('counts','no unknown/raw or cleanup tails',e['complete_source_raw_evidence_gate']is True and not e['diagnostics'] and not e['UNKNOWN_uncompleted_fixtures'])
    ck('preservation','all saved bytes still unchanged',all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in retained.items()))
    report=dict(schema='P4_CBIRRT_D64_STDLIB_SAVED_INDEPENDENT_POST_V1',status='PASS_SAVED_EVIDENCE_AUDIT'if not failed else'FAIL_SAVED_EVIDENCE_AUDIT',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of D64 runner implementation',personnel_independent=True,original_scientific_status=e['status'],original_run_full64_interface_gate=complete,checks_total=sum(x['total']for x in groups.values()),checks_passed=sum(x['passed']for x in groups.values()),checks_failed=len(failed),groups=dict(groups),failures=failed,execution_sha256=sha(RUN/'execution.json'),audit_script_sha256=sha(__file__),retained_raw_return_ids=retained_raw_return_ids,qualified_response_ids=expected_completed,retained_unqualified_raw_return_ids=original_rejected_retained,UNKNOWN_count=len(e['UNKNOWN_uncompleted_fixtures']),actual_raw_trace_started=dict(rawstarts),actual_raw_trace_completed=dict(rawends),plain_trace_pairs=len(pairstats),original_four_nonzero_diagonals=diagonals,processes=processes,own_wall_s=e['wall_s'],own_cpu_s=e['cpu_s'],prior_execution_count=len(prior),retained_sha256=retained,new_compile_binary_model_query_claim_protocol_prior_commit_calls=0,limitations=['Saved-only consistency audit; no native C++ function was rerun.','Original status and failed/UNKNOWN suffix remain unchanged.','D64 is distance-interface qualification only, not local RBS, PCS solve, independent path, RSS, continuous safety, performance or full-paper qualification.','All211 obligations, formal0/22500 andVI974/974 remain.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write(f"# D64 保存证据独立后审\n\n{report['status']}：{report['checks_passed']}/{report['checks_total']}，失败{len(failed)}。原科学状态{e['status']}；已合格返回{len(responses)}/64，UNKNOWN {len(e['UNKNOWN_uncompleted_fixtures'])}。本审查者未编写D64 runner，新增编译/binary/科学/claim/protocol/prior/commit均0。\n\n核对冻结source/claim/hash、保存64输入与原距离参考、binary64 state/plain-trace、每进程构造一次和完整raw EOF、真实body计数及全部Popen回收与实账。仅距离接口资格，未执行或认可RBS、CBi规划、路径、RSS和性能实验。\n")
    print(json.dumps({k:report[k]for k in ('status','checks_total','checks_passed','checks_failed','original_scientific_status')},ensure_ascii=False))

if __name__=='__main__':main()
