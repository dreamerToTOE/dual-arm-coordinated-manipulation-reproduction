#!/usr/bin/env python3
"""Personnel-independent saved-only TAIL02 aggregate and GNUtime audit.

Never imports the runner/supervisor or executes time/binary/model/science.
Only saved bytes, stdlib Decimal/binary64/distance arithmetic and git-show.
"""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import base64
import datetime
import hashlib
import json
import math
import struct
import subprocess

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=ROOT/'results/p4_full/20261015_R2_ABB_CBIRRT_D_TAIL02'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_TAIL02_SAVED_INDEPENDENT_POST_20261016.json'
LABEL='SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO'
MARKER=b'P4_CBIRRT_D_TRACE '

def exact(a,b):
    if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
    if type(a)in(int,float)and type(b)in(int,float):return struct.pack('>d',a)==struct.pack('>d',b)
    if type(a)is not type(b):return False
    if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
    if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
    return a==b

def normalized(r):
    remove=('mode','source_counts_observed','source_started','source_completed','trace')
    r={k:v for k,v in r.items()if k not in remove}
    r['construction']={k:v for k,v in r['construction'].items()if k not in remove}
    return r

def main():
    if not(RUN/'execution.json').exists():raise SystemExit('SAVED_TAIL02_NOT_READY_NO_ACTION')
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('PRESERVE_ORIGINAL_POST_NO_OVERWRITE')
    groups=defaultdict(lambda:dict(total=0,passed=0));failed=[];retained={}
    def path(n):
        n=Path(n);return n if n.is_absolute()else ROOT/n
    def raw(n):
        n=path(n);b=n.read_bytes();retained[str(n)]=hashlib.sha256(b).hexdigest();return b
    def sha(n):return hashlib.sha256(raw(n)).hexdigest()
    def load(n):return json.loads(raw(n))
    def ck(g,k,ok):
        groups[g]['total']+=1;groups[g]['passed']+=bool(ok)
        if not ok:failed.append(dict(group=g,check=k))
    e=load(RUN/'execution.json');p=load(e['protocol']);claim=load(e['claim']);ext=p['external_supervision'];charge=load(ext['charge_path'])
    ck('recipe','split status and explicit frozen reviews',e['status']==p['classification']==LABEL and p['frozen']is True and all(v is True for v in p['reviews'].values()))
    ck('recipe','protocol claim before after',sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']==claim['protocol_sha256'] and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'])
    ck('recipe','full bound before after',e['bound_files_sha256']==e['bound_files_after_sha256']==p['bound_files_sha256'])
    for n,h in p['bound_files_sha256'].items():ck('hashes',n,sha(n)==h)
    for n,h in p['own_source_sha256'].items():
        b=subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)
        ck('commit',n,hashlib.sha256(b).hexdigest()==h)
    ck('commit','frozen protocol exact blob',hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+e['protocol']],cwd=ROOT)).hexdigest()==e['protocol_sha256'])
    priors=[load(n)for n in p['prior_execution_sha256']]
    ck('budget','prior own cost bound once',e['prior_execution_sha256']==e['prior_execution_after_sha256']==p['prior_execution_sha256'] and math.fsum(x['wall_s']for x in priors)==e['previous_r2_wall_s']==p['previous_r2_wall_s'] and math.fsum(x['cpu_s']for x in priors)==e['previous_r2_cpu_s']==p['previous_r2_cpu_s'])
    for n,h in p['prior_execution_sha256'].items():ck('prior',n,sha(n)==h)
    timebytes=raw(ext['sibling_path']);fields=timebytes.decode().strip().split();elapsed,user,system=(Decimal(v)for v in fields[:3]);exitcode=int(fields[3]);upper_wall=float(elapsed+Decimal('.01'));upper_cpu=float(user+system+Decimal('.02'))
    ck('external','single exact fourfield finite line',len(fields)==4 and len(timebytes.splitlines())==1 and all(v.is_finite()and v>=0 for v in(elapsed,user,system)))
    ck('external','Decimal upper pads original5/10 and total balance',upper_wall<=min(5.,3600.-p['previous_r2_wall_s']) and upper_cpu<=min(10.,7200.-p['previous_r2_cpu_s']) and exitcode==0)
    ck('external','charge upper exact hash',charge['time_sha256']==sha(ext['sibling_path']) and charge['time_fields']==fields and exact(charge['wall_s'],upper_wall) and exact(charge['cpu_s'],upper_cpu) and charge['timing_valid']is True and charge['wall_CPU_caps_pass']is True and charge['completed_process_exit0']is True)
    ck('external','charge source and child exit',charge['execution_sha256']==sha(RUN/'execution.json') and charge['receipt_sha256']==sha(RUN/'cost_receipt.jsonl') and charge['time_returncode']==charge['measured_child_exit']==0 and charge['failure']is None)
    metadata=[json.loads(x)for x in raw(ext['metadata_path']).splitlines()];planned,started,reaped=metadata;proof=e['supervisor_launch_proof'];st=path(ext['sibling_path']).stat()
    ck('external','three planned launch/reap records',planned['event']=='planned_launch'and started['event']=='time_process_started'and reaped['event']=='time_process_reaped')
    ck('external','one actual time PID chain',started['pid']==reaped['pid']==proof['actual_time_pid']==charge['time_process_pid'] and proof['supervisor_pid']==planned['supervisor_pid'] and reaped['returncode']==0 and reaped['failure']is None)
    ck('external','planned firstline exact proof hash',hashlib.sha256(raw(ext['metadata_path']).splitlines(keepends=True)[0]).hexdigest()==proof['planned_launch_line_sha256'] and planned['argv']==started['argv']==proof['actual_argv'])
    ck('external','exclusive original inode current and saved',st.st_ino==planned['time_inode']==proof['time_inode'] and st.st_dev==planned['time_device']==proof['time_device'] and proof['actual_time_output_fds'] and charge['time_inode_unchanged']is True)
    ck('external','frozen time Python runner supervisor hash',planned['time_binary_sha256']==ext['time_binary_sha256'] and planned['python_binary_sha256']==ext['python_binary_sha256'] and planned['runner_sha256']==p['own_source_sha256']['scripts/qualify_p4_full_r2_abb_cbirrt_d_tail02_draft.py'] and planned['supervisor_source_sha256']==p['own_source_sha256']['scripts/supervise_p4_full_r2_abb_cbirrt_d_tail02_draft.py'] and planned['protocol_sha256']==e['protocol_sha256'])
    ck('external','metadata stderr current hashes',charge['metadata_sha256']==sha(ext['metadata_path']) and charge['stderr_sha256']==sha(ext['stderr_path']))
    receiptlines=raw(RUN/'cost_receipt.jsonl').splitlines();receipt=json.loads(receiptlines[0])
    ck('receipt','one postexecution receipt source hash',len(receiptlines)==1 and receipt['execution_sha256']==sha(RUN/'execution.json') and receipt['status']==LABEL)
    ck('receipt','external covers final execution and receipt tail',e['wall_s']<=receipt['wall_s_through_execution_persistence']<=upper_wall and e['cpu_s']<=receipt['cpu_s_through_execution_persistence']<=upper_cpu and receipt['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED')
    ck('receipt','internal external approval never forged',receipt['external_supervision_qualified']is False and e['external_supervision_qualified']is False and charge['external_supervision_qualified']is False)
    journalbytes=raw(e['evidence_journal']);rows=[];badtails=[]
    for i,line in enumerate(journalbytes.splitlines(),1):
        if not line:continue
        try:rows.append(json.loads(line))
        except(ValueError,UnicodeDecodeError):badtails.append(dict(line=i,sha256=hashlib.sha256(line).hexdigest()))
    ck('journal','whole journal hashed no malformed records',sha(e['evidence_journal'])==e['evidence_journal_sha256']and not badtails)
    ec=Counter(x['event']for x in rows);snap=next(x for x in rows if x['event']=='final_complete_raw_streams');streams={}
    for channel,info in snap['streams'].items():
        b=base64.b64decode(info['base64'],validate=True);chunks=b''.join(base64.b64decode(x['base64'],validate=True)for x in rows if x['event']=='raw_pipe_chunk'and x['channel']==channel);streams[channel]=b
        ck('raw',channel+' final snapshot exact chunks and hash',b==chunks and len(b)==info['bytes']and hashlib.sha256(b).hexdigest()==info['sha256'])
    lines=streams['stdout'].splitlines(keepends=True);new_responses=[json.loads(x)for x in lines]
    ck('raw','exact2 complete stdout JSONL and EOF',len(lines)==2 and all(x.endswith(b'\n')for x in lines)and snap['EOF']is True)
    lineevents=[x for x in rows if x['event']=='raw_response_line'];parsed=[x for x in rows if x['event']=='parsed_response_before_gates'];qrows=[x for x in rows if x['event']=='qualified_new_distance'];requests=[x['fixture']for x in rows if x['event']=='distance_request']
    ck('raw','raw line journal exact stdout',len(lineevents)==2 and all(base64.b64decode(x['base64'],validate=True)==b and x['bytes']==len(b)for x,b in zip(lineevents,lines)))
    ck('raw','parsed response and gates exact missing62/63',len(parsed)==2 and [x['dispatch_index']for x in qrows]==[62,63]and all(exact(x['response'],r)for x,r in zip(parsed,new_responses))and exact(requests,p['saved_prefix']['fixed_schedule']))
    ck('counts','only one source and two new calls',ec['source_process_started']==e['counts']['source_process_started']==1 and e['counts']['distance_dispatched']==e['counts']['distance_dispatch_attempted']==e['counts']['raw_response_lines_observed']==2 and e['completed_new_dispatch_ids']==[62,63]and not e['UNKNOWN_new_dispatch_ids'])
    ck('process','one new real Popen fully reaped exit0',len(e['source_process_registry'])==1 and e['source_process_registry'][0]['reaped']is True and e['source_process_registry'][0]['returncode']==0)
    sources=p['saved_prefix']['saved_raw_links'];all_responses=[]
    for i,link in enumerate(sources):
        b=raw(link['path']);ck('old prefix',str(i)+' saved original exact',i==link['dispatch_index'] and sha(link['path'])==link['sha256'] and link['original_runner_qualified']is(i<61)and link['saved_only_raw_audit_qualified']is True);all_responses.append(json.loads(b))
    all_responses+=new_responses;fixtures=p['saved_prefix']['original_fixed64_schedule'];contexts=p['saved_prefix']['original_fixed16_contexts'];lookup={};constructors={};diagonals=[]
    ck('aggregate','exact64 frozen response order',len(all_responses)==len(fixtures)==64 and [f['dispatch_index']for f in fixtures]==list(range(64)))
    for i,(r,f)in enumerate(zip(all_responses,fixtures)):
        c=contexts[f['context_index']];qa=f['request']['qa12'];qb=f['request']['qb12'];role=f['request']['active_chain'];part=slice(6*role,6*(role+1))
        ref=math.sqrt(math.fsum((x-y)**2 for x,y in zip(qa[part],qb[part])))if f['factor']=='distance_destination_fix'or role==0 else math.sqrt(math.fsum(x*x for x in qb[6:]))
        ck('aggregate',str(i)+' original exact interface and request',r['status']=='SOURCE_INTERFACE_COMPLETED_NOT_QUALIFIED'and r['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1'and exact(r['request'],f['request'])and r['environment']==f['environment']and r['mode']==f['mode']and r['operation']=='distance'and r['source_dispatch_started']==r['source_dispatch_completed']==1)
        ck('distance',str(i)+' independent L2 or original wrong formula',math.isfinite(r['distance'])and r['distance']>=0 and abs(r['distance']-ref)<=1e-12 and exact(ref,c[f['factor']+'_reference_rad']))
        ck('scope',str(i)+' zero solve formal independent path',r['solve_calls']==r['formal_table_I_calls']==0 and r['independent_path_qualified']is False)
        for k in('qa12','qb12'):ck('states',str(i)+' '+k,exact(r[k+'_after'],f['request'][k])and r[k+'_binary64_after']==struct.pack('>12d',*f['request'][k]).hex())
        if c['diagonal']:
            if f['factor']=='distance_destination_fix':ck('distance',str(i)+' corrected self strict0',r['distance']==0.)
            elif role==1:ck('distance',str(i)+' original nonzero self',r['distance']>0.);diagonals.append(c['case_id'])
        co=r['construction'];trace=f['mode']=='trace';ck('construction',str(i)+' real and structural distinct from UNOBSERVED',co['cbirrt_constructor_dispatch_completed']==co['ompl_setSeed_calls_completed']==co['source_direct_rng_member_initializations_structural']==1 and co['svc_only_constructor_dispatch_completed']==co['srand_calls_completed']==0 and co['source_direct_rng_member_true_started_completed']=='UNOBSERVED_LIBRARY_NOT_HOOKED'and co['library_internal_seed_draws']=='UNOBSERVED_NOT_REPORTED_ZERO')
        ck('trace',str(i)+' explicit observed flags',r['source_counts_observed']is trace and co['source_counts_observed']is trace)
        if trace:
            a,b=r['trace'];u,v=co['trace']
            ck('trace',str(i)+' exact one real original body entry and return',a['event']=='entered'and b['event']=='completed'and a['kind']==b['kind']=='activeDistance'and a['id']==b['id']==1 and r['source_started']==r['source_completed']=={'activeDistance':1}and exact(a['args']['qa12'],qa)and exact(a['args']['qb12'],qb)and a['args']['active_chain']==role and exact(b['result']['distance'],r['distance']))
            ck('trace',str(i)+' mesh constructor once',u['event']=='entered'and v['event']=='completed'and u['kind']==v['kind']=='mesh_load'and u['id']==v['id']==1 and u['args']==v['result']=={}and co['source_started']==co['source_completed']=={'mesh_load':1})
        else:ck('trace',str(i)+' plain remains UNOBSERVED',all(x[k]is None for x in(r,co)for k in('trace','source_started','source_completed')))
        session=('TAIL02',)if i>=62 else(f['factor'],f['mode'],f['environment'])
        if session in constructors:ck('construction',str(i)+' repeated constructor identical',exact(constructors[session],co))
        else:constructors[session]=co
        lookup[(f['factor'],f['mode'],f['case_id'])]=r
    pairs=0
    for factor in('source_control','distance_destination_fix'):
        for c in contexts:ck('pairs',factor+' '+c['case_id'],exact(normalized(lookup[(factor,'plain',c['case_id'])]),normalized(lookup[(factor,'trace',c['case_id'])])));pairs+=1
    for mode in('plain','trace'):
        for c in contexts:
            reverse=next(t for t in contexts if t['a']==c['b']and t['b']==c['a']and t['active_chain']==c['active_chain']);case=c['case_id']
            ck('symmetry',mode+' '+case,exact(lookup[('distance_destination_fix',mode,case)]['distance'],lookup[('distance_destination_fix',mode,reverse['case_id'])]['distance']))
            if c['active_chain']==0:ck('role0',mode+' '+case,exact(lookup[('source_control',mode,case)]['distance'],lookup[('distance_destination_fix',mode,case)]['distance']))
    actual=[json.loads(line.split(MARKER,1)[1])for line in streams['stderr'].splitlines()if MARKER in line];expected=new_responses[0]['construction']['trace']+[x for r in new_responses for x in r['trace']];started_counts=Counter(x['kind']for x in actual if x['event']=='entered');completed_counts=Counter(x['kind']for x in actual if x['event']=='completed')
    ck('trace','new raw ctor once plus2 body exact',exact(actual,expected)and started_counts==completed_counts==Counter(mesh_load=1,activeDistance=2)and e['new_raw_trace_started']==e['new_raw_trace_completed']==dict(started_counts))
    ck('aggregate','9processes32pairs4unique source self failures',len(constructors)==9 and pairs==32 and len(set(diagonals))==4 and e['aggregate_saved_only_qualification']['aggregate_processes']==9 and e['aggregate_saved_only_qualification']['aggregate_dispatched']==64 and e['aggregate_raw_trace_started']==e['aggregate_raw_trace_completed']=={'mesh_load':5,'activeDistance':32})
    olde=load('results/p4_full/20261015_R2_ABB_CBIRRT_D_DISTANCE01/execution.json')
    ck('original','old STOP 61complete UNKNOWN permanently unchanged',olde['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET'and olde['completed_dispatch_ids']==list(range(61))and[f['dispatch_index']for f in olde['UNKNOWN_uncompleted_fixtures']]==[61,62,63]and e['aggregate_saved_only_qualification']['original_single_run_PASS']is False and e['aggregate_saved_only_qualification']['index61_original_qualification']is False)
    ck('scope','zero new model formal VI old requery',all(v==0 for v in e['zero_calls'].values())and e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and not e['diagnostics'])
    ck('preservation','all read bytes unchanged',all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in retained.items()))
    passed=not failed
    report=dict(schema='P4_TAIL02_SAVED_INDEPENDENT_AGGREGATE_POST_V1',status='PASS_SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO_INDEPENDENT_POST'if passed else'FAIL_TAIL02_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of TAIL02 implementation',personnel_independent=True,checks_total=sum(x['total']for x in groups.values()),checks_passed=sum(x['passed']for x in groups.values()),checks_failed=len(failed),groups=dict(groups),failures=failed,external_supervision_qualified=passed,execution_sha256=sha(RUN/'execution.json'),external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),upper_wall_s=upper_wall,upper_cpu_s=upper_cpu,external_time_fields=fields,execution_sample_wall_s=e['wall_s'],execution_sample_cpu_s=e['cpu_s'],receipt_through_execution_wall_s=receipt['wall_s_through_execution_persistence'],receipt_through_execution_cpu_s=receipt['cpu_s_through_execution_persistence'],charge_rule='Keep execution samples; replace this execution effective cost exactly once with independent GNUtime upper_wall_s/upper_cpu_s. Never add both sample and upper.',aggregate_actual_responses=64,aggregate_source_processes=9,aggregate_plain_trace_pairs=32,old_D64_status_preserved=True,old_D64_UNKNOWN=[61,62,63],old_index61_runner_qualified=False,original_single_run_PASS=False,retained_sha256=retained,audit_script_sha256=sha(__file__),new_compile_binary_model_science_query_claim_protocol_prior_commit_calls=0,limitations=['Split saved qualification only; original D64 STOP and UNKNOWN remain.','No function, model, GNUtime, binary or runner was rerun; all64 checks use actual saved responses.','GNUtime upper covers child runner plus reaped source and final receipt/exit; supervisor own log persistence overhead is excluded as disclosed.','Distance interface only; no RBS/PCS planning/path/RSS/performance/full-paper qualification.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write(f"# D_TAIL02 全64与外层费用独立保存审查\n\n{report['status']}：{report['checks_passed']}/{report['checks_total']}，失败{len(failed)}。external_supervision_qualified={passed}。外层GNUtime上界wall={upper_wall:.12f}s、CPU={upper_cpu:.12f}s；原execution样本保留，账目仅以上界替换一次。\n\n旧62raw+新2形成64个真实距离响应、32plain/trace对、9个源进程，原D64 STOP/61complete/UNKNOWN[61,62,63]永久保留。核对journal/base64原字节、raw EOF/trace、原L2与错误对照、state、source/claim/hash、实际time父PID/argv/inode、receipt和外层exit。新增科学/编译/binary/claim/protocol/prior/commit均0，仅距离接口分次资格。\n")
    print(json.dumps({k:report[k]for k in('status','checks_total','checks_passed','checks_failed','external_supervision_qualified','upper_wall_s','upper_cpu_s')},ensure_ascii=False))

if __name__=='__main__':main()
