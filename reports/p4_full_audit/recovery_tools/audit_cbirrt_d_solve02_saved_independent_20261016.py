#!/usr/bin/env python3
"""Personnel-independent S02 saved-only transport/tree/reconstruction/cost audit.

No runner/model/library import or science. Only saved bytes, Python arithmetic,
and git-show subprocess. Exact candidate is not an independently qualified path.
"""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import base64,datetime,hashlib,json,math,struct,subprocess
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=ROOT/'results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE02'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_SAVED_INDEPENDENT_POST_20261016.json'
MARKER=b'P4_CBIRRT_D_TRACE '
def exact(a,b):
    if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
    if type(a)in(int,float)and type(b)in(int,float):return struct.pack('>d',a)==struct.pack('>d',b)
    if type(a)is not type(b):return False
    if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
    if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
    return a==b
def bits(q):return struct.pack('>'+str(len(q))+'d',*q).hex()
def main():
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('PRESERVE_PREVIOUS_POST_NO_OVERWRITE')
    retained={};checks=[];groups=defaultdict(lambda:dict(total=0,passed=0))
    def path(n):return Path(n)if Path(n).is_absolute()else ROOT/n
    def raw(n):
        p=path(n);b=p.read_bytes();retained[str(p)]=hashlib.sha256(b).hexdigest();return b
    def sha(n):return hashlib.sha256(raw(n)).hexdigest()
    def load(n):return json.loads(raw(n))
    def ck(g,n,ok):
        ok=bool(ok);checks.append(dict(group=g,check=n,passed=ok));groups[g]['total']+=1;groups[g]['passed']+=ok
    e=load(RUN/'execution.json');p=load(e['protocol']);claim=load(e['claim']);ext=p['external_supervision'];charge=load(ext['charge_path'])
    ck('recipe','frozen committed exact source pending-path scope',e['source_commit']=='4065ac6d00c2ae73a5147e193fa249b7d69cf148'and p['frozen']is True and all(v is True for v in p['reviews'].values())and e['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT'and e['independent_path_qualified']is False)
    ck('recipe','exact protocol claim unchanged',sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']=='4220791572538287371c30800adfae6ce98f651383f3aca62b3758a85db4d8a0'and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256']and claim['protocol_sha256']==e['protocol_sha256']and p['bound_files_sha256']==e['bound_files_sha256']==e['bound_files_after_sha256'])
    for n,h in p['bound_files_sha256'].items():ck('hash',n,sha(n)==h)
    for n,h in p['own_source_sha256'].items():ck('commit',n,hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest()==h)
    ck('commit','protocol exact committed blob',hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+e['protocol']],cwd=ROOT)).hexdigest()==e['protocol_sha256'])
    prior=p['actual_charge_prior'];ledger=load(prior['ledger']);pw=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in ledger['executions']);pc=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in ledger['executions'])
    ck('prior','all true execution hashes once before after charged ledger',sha(prior['ledger'])==prior['ledger_sha256']and {r['execution']:r['execution_sha256']for r in ledger['executions']}==p['prior_execution_sha256']==e['prior_execution_sha256']==e['prior_execution_after_sha256']==prior['execution_sha256']and pw==prior['wall_s']==p['previous_r2_wall_s']and pc==prior['cpu_s']==p['previous_r2_cpu_s']and e['actual_charge_prior']==prior)
    for n,h in p['prior_execution_sha256'].items():ck('prior',n,sha(n)==h)
    previous=p['previous_S01_stop'];old=load(previous['original_execution']);oldpost=load('reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json')
    ck('shared','original failed S01 exact immutable unknown',sha(previous['original_execution'])==previous['original_execution_sha256']=='99c5cc5e980bf52489b154d5a678df903a1897a1e9e966c341ea6b5229533fdd'and old['status']=='STOP_PREFIX_RETAINED'and oldpost['successful_transport_qualified']is False and previous['original_source_solve_entered']is True and previous['original_source_solve_completed']=='UNOBSERVED')
    for n,h in previous['files_sha256'].items():ck('shared',n,sha(n)==h)
    ck('shared','same source budget reduced after actual S01 cost',previous['consumed_upper_wall_s']==oldpost['upper_wall_s']==1.44 and previous['consumed_upper_cpu_s']==oldpost['upper_cpu_s']==1.14 and previous['remaining_wall_s']==p['budget']['wall_s']==28.56 and previous['remaining_cpu_s']==p['budget']['cpu_s']==58.86 and previous['shared_original_wall_s']==30. and previous['shared_original_cpu_s']==60.)
    rows=[json.loads(x)for x in raw(e['evidence_journal']).splitlines()if x.strip()];events=Counter(x['event']for x in rows);snap=next(x for x in rows if x['event']=='final_complete_raw_streams');streams={}
    ck('journal','entire original journal hash exact',sha(e['evidence_journal'])==e['evidence_journal_sha256'])
    ck('journal','one source request response and exact preamble count',events['setup']==events['source_process_started']==events['source_start_group']==events['source_close_group']==events['solve_request']==events['recognized_exact_setup_preamble']==events['raw_response_line']==events['parsed_response_before_gates']==events['final_complete_raw_streams']==events['final_counts']==1 and events['raw_stdout_line']==2)
    for channel,info in snap['streams'].items():
        b=base64.b64decode(info['base64'],validate=True);streams[channel]=b;chunks=b''.join(base64.b64decode(x['base64'],validate=True)for x in rows if x['event']=='raw_pipe_chunk'and x['channel']==channel)
        ck('raw',channel+' chunks final snapshot exact original file',b==chunks==raw(RUN/f'source_{channel}.bin')and len(b)==info['bytes']and hashlib.sha256(b).hexdigest()==info['sha256'])
    lines=streams['stdout'].splitlines(keepends=True);stdout_rows=[x for x in rows if x['event']=='raw_stdout_line'];raw_response=next(x for x in rows if x['event']=='raw_response_line');response=next(x['response']for x in rows if x['event']=='parsed_response_before_gates')
    ck('raw','exact one55B setup plus one complete JSON no tail',len(lines)==2 and lines[0]==base64.b64decode(p['stdout_contract']['exact_setup_preamble_base64'],validate=True)==b'Debug:   CBiRRT: Planner range detected to be 3.415829\n'and len(lines[0])==55 and lines[1].endswith(b'\n')and exact(json.loads(lines[1]),response)and base64.b64decode(raw_response['base64'],validate=True)==lines[1]and all(base64.b64decode(x['base64'],validate=True)==line and x['bytes']==len(line)for x,line in zip(stdout_rows,lines)))
    ck('response','exact source request and completed original solve only',response['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1'and response['environment']=='II'and response['operation']=='solve'and response['mode']=='trace'and exact(response['request'],p['request'])and p['request']['seed']==7 and p['request']['range_rad']==2.6 and p['request']['solve_seconds']==10. and response['source_dispatch_started']==response['source_dispatch_completed']==response['solve_calls']==1 and response['formal_table_I_calls']==0 and response['independent_path_qualified']is False)
    ck('response','exact nonapprox candidate explicitly pending independent physical path',response['status']==e['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT'and response['exact']is e['source_exact']is True and response['has_solution']is e['source_has_solution']is True and response['approximate']is e['source_approximate']is False and response['planner_status']==e['source_planner_status']=='Exact solution')
    c=response['construction'];ck('construction','one CBi one seed source RNG boundary retained',c['cbirrt_constructor_dispatch_completed']==c['ompl_setSeed_calls_completed']==c['srand_calls_completed']==c['source_direct_rng_member_initializations_structural']==1 and c['svc_only_constructor_dispatch_completed']==0 and c['source_direct_rng_member_true_started_completed']=='UNOBSERVED_LIBRARY_NOT_HOOKED'and c['library_internal_seed_draws']=='UNOBSERVED_NOT_REPORTED_ZERO')
    rawtrace=[];bad=[]
    for line in streams['stderr'].splitlines(keepends=True):
        if MARKER not in line:continue
        try:
            x=json.loads(line.split(MARKER,1)[1]);rawtrace.append(x)
            if not line.endswith(b'\n'):bad.append(hashlib.sha256(line).hexdigest())
        except(ValueError,UnicodeDecodeError):bad.append(hashlib.sha256(line).hexdigest())
    ck('trace','whole actual stderr exactly constructor plus complete response trace',not bad and exact(rawtrace,c['trace']+response['trace']))
    false_by_kind=Counter();attempts=[];observations=[];save_return=None;fullpairs=[];total_start=Counter();total_end=Counter()
    for tag,observed in(('construction',c),('solve',response)):
        stack=[];starts=Counter();ends=Counter();serial=0;allpaired=True;allserial=True
        for x in observed['trace']:
            if x['event']=='entered':serial+=1;allserial=allserial and x['id']==serial;stack.append(x);starts[x['kind']]+=1
            elif x['event']=='observed':
                serial+=1;allserial=allserial and x['id']==serial;observations.append(x);allpaired=allpaired and x['kind']=='save_source_mpaths'and set(x['args'])=={'source_mpaths'}
            elif x['event']=='completed':
                a=stack.pop()if stack else {};allpaired=allpaired and a.get('id')==x['id']and a.get('kind')==x['kind'];ends[x['kind']]+=1;fullpairs.append((a,x))
                if x.get('result',{}).get('returned')is False:false_by_kind[x['kind']]+=1
                if x['kind']=='state_reconstruct':attempts.append(dict(trace_id=x['id'],input=a['args'],returned=x['result']['returned'],path_q12=x['result']['path_q12']))
                if x['kind']=='save2file':save_return=x
            else:allpaired=False
        ck('trace',tag+' full nesting serial entry return no missing/extra',not stack and allpaired and allserial and starts==ends and dict(starts)==observed['source_started']==observed['source_completed']and observed['source_counts_observed']is True);total_start.update(starts);total_end.update(ends)
    ck('trace','actual native whole solve counters match saved execution',dict(total_start-Counter(mesh_load=1))==e['actual_source_started']==e['actual_source_completed']and total_start==total_end and c['source_started']=={'mesh_load':1})
    nodes=response['trees']['nodes'];byid={x['motion_id']:x for x in nodes};states={x['state_id']for x in nodes};roots={x['tree']:x for x in nodes if x['parent_motion_id']==0}
    ck('tree','distinct actual6Motion6state two roots never q merged',len(nodes)==len(byid)==len(states)==6 and set(roots)=={'start','goal'}and roots['start']['motion_id']==1 and roots['goal']['motion_id']==3 and exact(roots['start']['q12'],p['request']['start_q12'])and exact(roots['goal']['q12'],p['request']['goal_q12'])and response['trees']['node_identity_policy']=='Actual Motion/state identities; equal q never merged.')
    for n in nodes:
        cur=n;seen=set();ok=True
        while cur['parent_motion_id']:
            if cur['motion_id']in seen or cur['parent_motion_id']not in byid:ok=False;break
            seen.add(cur['motion_id']);cur=byid[cur['parent_motion_id']];ok=ok and cur['tree']==n['tree']
        ck('tree',str(n['motion_id'])+' real parent to matching root',ok and cur['motion_id']==n['root_motion_id']==roots[n['tree']]['motion_id']and cur['state_id']==n['root_state_id']and exact(cur['q12'],n['root_q12']))
    duplicate_q=[(a['motion_id'],b['motion_id'])for i,a in enumerate(nodes)for b in nodes[i+1:]if exact(a['q12'],b['q12'])]
    ck('tree','equal q states7and5 remain distinct actual identities',(7,5)in duplicate_q and byid[7]['state_id']!=byid[5]['state_id']and byid[7]['tree']=='start'and byid[5]['tree']=='goal')
    for tree in('start','goal'):
        bridge=response['trees']['connection_'+tree];n=byid[bridge['motion_id']];ck('tree','actual bridge '+tree,n['tree']==tree and n['state_id']==bridge['state_id']and exact(n['q12'],bridge['q12']))
    ck('tree','actual bridge identities6to5',response['trees']['connection_start']['motion_id']==6 and response['trees']['connection_goal']['motion_id']==5)
    ck('mpaths','one observed original mpaths and matching return',len(observations)==1 and save_return is not None and exact(observations[0]['args']['source_mpaths'],save_return['result']['source_mpaths'])and save_return['result']['return_does_not_certify_complete_reconstruction']is True)
    mpaths=observations[0]['args']['source_mpaths'];ck('mpaths','actual original two chains IDs not inferred from q',[[x['motion_id']for x in a]for a in mpaths]==[[6,4,1],[5,3]])
    for seq in mpaths:
        for i,n in enumerate(seq):
            original=byid[n['motion_id']];ck('mpaths',str(n['motion_id'])+' exact source node parent IK role',n['parent_id']==original['parent_motion_id']and exact(n['q12'],original['q12'])and all(n[k]==original[k]for k in('a_chain','ik_q1_active','ik_q2_active'))and (i==len(seq)-1 or n['parent_id']==seq[i+1]['motion_id']))
    order=list(reversed(mpaths[0]))+mpaths[1];milestones=[n['q12']for n in order];ck('mpaths','all5 milestones order start-root actual bridge goal-root',len(milestones)==5 and exact(milestones,response['milestones_q12'])and [n['motion_id']for n in order]==[1,4,6,5,3])
    attempts.sort(key=lambda x:x['trace_id']);ck('reconstruction','all5 true true FALSE true true retained',len(attempts)==5 and [x['trace_id']for x in attempts]==[27762,28406,29266,29271,29459]and [x['returned']for x in attempts]==[True,True,False,True,True]and [len(x['path_q12'])for x in attempts]==[109,145,2,33,129]and false_by_kind['state_reconstruct']==false_by_kind['vector_reconstruct']==1)
    schedule=[(0,0,3),(1,0,3),(2,0,3),(2,1,3),(3,1,3)];selected=[]
    for a,(edge,role,branch)in zip(attempts,schedule):
        ar=a['input'];qs=a['path_q12'];ck('reconstruction',str(a['trace_id'])+' exact original segment input and fullM endpoints',ar['active_chain']==role and ar['branch']==branch and exact(ar['qa12'],milestones[edge])and exact(ar['qb12'],milestones[edge+1])and exact(qs[0],ar['qa12'])and exact(qs[-1],ar['qb12'])and all(len(q)==12 and all(math.isfinite(v)for v in q)for q in qs))
        if a['returned']:selected.append(a)
    ck('reconstruction','false original branch then native passive fallback same endpoints',attempts[2]['returned']is False and len(attempts[2]['path_q12'])==2 and attempts[3]['returned']is True and exact(attempts[2]['input']['qa12'],attempts[3]['input']['qa12'])and exact(attempts[2]['input']['qb12'],attempts[3]['input']['qb12'])and attempts[2]['input']['active_chain']==0 and attempts[3]['input']['active_chain']==1)
    dense=selected[0]['path_q12'][:]
    for a in selected[1:]:ck('reconstruction',str(a['trace_id'])+' exact seam concatenation',exact(dense[-1],a['path_q12'][0]));dense.extend(a['path_q12'][1:])
    ck('reconstruction','source complete413 highprecision candidate endpoints only',len(dense)==413 and exact(dense[0],p['request']['start_q12'])and exact(dense[-1],p['request']['goal_q12']))
    for n,h in e['original_native_output_sha256'].items():ck('native output',n,sha(n)==h and n in e['original_native_output_fsync_completed'])
    ck('native output','all five original files frozen persisted not repaired',len(e['original_native_output_sha256'])==len(e['original_native_output_fsync_completed'])==5 and raw(RUN/'work/paths/path.txt').splitlines()[0]==b'413'and raw(RUN/'paths/path_milestones.txt').splitlines()[0]==b'5')
    source_start=next(x for x in rows if x['event']=='source_process_started');sg=next(x for x in rows if x['event']=='source_start_group')['members'];cg=next(x for x in rows if x['event']=='source_close_group')['members'];registry=e['source_process_registry']
    ck('process','one PID exact start close snapshots EOF reaped exit0',len(sg)==len(cg)==len(registry)==1 and source_start['pid']==sg[0]['pid']==sg[0]['pgrp']==cg[0]['pid']==cg[0]['pgrp']==registry[0]['pid']and sg[0]['ppid']==cg[0]['ppid']and registry[0]['reaped']is True and registry[0]['returncode']==0 and snap['EOF']is True and e['complete_source_raw_evidence_gate']is True)
    ck('process','one exact sideband response no extra dispatch count',e['counts']==dict(source_process_start_attempted=1,source_process_started=1,solve_dispatch_attempted=1,solve_dispatched=1,stdout_complete_lines_observed=2,setup_preamble_lines_observed=1,raw_response_lines_observed=1))
    ck('runtime','20 native original meshes copied exact',len(e['runtime_mesh_sha256'])==20 and all(sha(n)==h for n,h in e['runtime_mesh_sha256'].items()))
    tb=raw(ext['sibling_path']);fields=tb.decode().split();elapsed,user,system=map(Decimal,fields[:3]);uw=float(elapsed+Decimal('.01'));uc=float(user+system+Decimal('.02'));meta=raw(ext['metadata_path']);planned,started,reaped=[json.loads(x)for x in meta.splitlines()];proof=e['supervisor_launch_proof'];st=path(ext['sibling_path']).stat();receiptlines=raw(RUN/'cost_receipt.jsonl').splitlines();receipt=json.loads(receiptlines[0])
    ck('external','complete finite one line time exit0 local and R2 caps',len(fields)==4 and len(tb.splitlines())==1 and all(x.is_finite()and x>=0 for x in(elapsed,user,system))and fields[3]=='0'and uw<=min(28.56,3600.-pw)and uc<=min(58.86,7200.-pc))
    shared_w=float(Decimal(str(uw))+Decimal(str(oldpost['upper_wall_s'])));shared_c=float(Decimal(str(uc))+Decimal(str(oldpost['upper_cpu_s'])))
    ck('shared','both actual qualified charges within original30wall60CPU',shared_w<=30. and shared_c<=60.)
    ck('external','actual time PID parent/reap chain',planned['event']=='planned_launch'and started['event']=='time_process_started'and reaped['event']=='time_process_reaped'and started['pid']==reaped['pid']==proof['actual_time_pid']==charge['time_process_pid']and reaped['returncode']==0 and reaped['failure']is None and proof['supervisor_pid']==planned['supervisor_pid'])
    argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/'scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py'),'--protocol',str(path(e['protocol']))]
    ck('external','exact argv exclusive inode heldFD identity',argv==planned['argv']==started['argv']==proof['actual_argv']and st.st_ino==planned['time_inode']==proof['time_inode']and st.st_dev==planned['time_device']==proof['time_device']and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and hashlib.sha256(meta.splitlines(keepends=True)[0]).hexdigest()==proof['planned_launch_line_sha256'])
    ck('external','original exact sources binary protocol hashes',planned['protocol_sha256']==e['protocol_sha256']and planned['runner_sha256']==p['own_source_sha256']['scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py']and planned['supervisor_source_sha256']==p['own_source_sha256']['scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py']and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
    ck('external','all measured charge provenance caps exit0',charge['execution_sha256']==sha(RUN/'execution.json')and charge['receipt_sha256']==sha(RUN/'cost_receipt.jsonl')and charge['time_sha256']==sha(ext['sibling_path'])and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr_sha256']==sha(ext['stderr_path'])and charge['time_fields']==fields and exact([charge['wall_s'],charge['cpu_s']],[uw,uc])and charge['timing_valid']is charge['time_inode_unchanged']is charge['wall_CPU_caps_pass']is charge['completed_process_exit0']is True and charge['time_returncode']==charge['measured_child_exit']==0 and charge['failure']is None)
    ck('external','final receipt persistence and exit covered external',len(receiptlines)==1 and receipt['execution_sha256']==sha(RUN/'execution.json')and receipt['status']==e['status']and e['wall_s']<=receipt['wall_s_through_execution_persistence']<=uw and e['cpu_s']<=receipt['cpu_s_through_execution_persistence']<=uc and receipt['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and receipt['external_supervision_qualified']is e['external_supervision_qualified']is charge['external_supervision_qualified']is False)
    ck('scope','all physical/formal/VI calls zero no automatic path PASS',all(v==0 for v in e['zero_calls'].values())and e['independent_path_qualified']is False and e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and not e['diagnostics'])
    ck('preservation','all saved read bytes unchanged',all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in retained.items()))
    failed=[x for x in checks if not x['passed']];ok=not failed
    report=dict(schema='P4_SOLVE02_SAVED_INDEPENDENT_POST_V1',status='PASS_SOLVE02_TRANSPORT_EVIDENCE_INDEPENDENT_POST'if ok else'FAIL_SOLVE02_TRANSPORT_EVIDENCE_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of S02 implementation',personnel_independent=True,checks_total=len(checks),checks_passed=sum(x['passed']for x in checks),checks_failed=len(failed),groups=dict(groups),failures=failed,external_supervision_qualified=ok,external_timing_qualified=ok,successful_transport_qualified=ok,completed_process_exit0=True,execution_sha256=sha(RUN/'execution.json'),external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),upper_wall_s=uw,upper_cpu_s=uc,external_time_fields=fields,execution_sample_wall_s=e['wall_s'],execution_sample_cpu_s=e['cpu_s'],shared_S01_S02_upper_wall_s=shared_w,shared_S01_S02_upper_cpu_s=shared_c,charge_rule='Only S02 new cost external upper replaces its internal sample once. S01 previous failed cost remains already charged; never add it again to R2.',source_status=response['status'],source_exact=response['exact'],source_has_solution=response['has_solution'],source_approximate=response['approximate'],source_tree_motion_count=6,source_tree_state_count=6,source_tree_roots=dict(start=1,goal=3),source_bridge_motion_ids=[6,5],equal_q_distinct_motion_ids=[[7,5]],source_mpaths_motion_ids=[[6,4,1],[5,3]],source_milestone_motion_ids=[1,4,6,5,3],state_reconstruction_attempts=[dict(trace_id=a['trace_id'],active_chain=a['input']['active_chain'],branch=a['input']['branch'],returned=a['returned'],node_count=len(a['path_q12']),full_M_sha256=hashlib.sha256(json.dumps(a['path_q12'],separators=(',',':'),allow_nan=False).encode()).hexdigest())for a in attempts],false_state_reconstruct_ids=[a['trace_id']for a in attempts if not a['returned']],actual_false_returns_by_kind=dict(false_by_kind),selected_complete_reconstruction_nodes=[len(a['path_q12'])for a in selected],selected_complete_dense_node_count=413,source_reconstruction_coverage_observed=True,independent_path_qualified=False,actual_raw_trace_started=dict(total_start),actual_raw_trace_completed=dict(total_end),retained_sha256=retained,audit_script_sha256=sha(__file__),new_import_runner_model_native_query_compile_protocol_prior_claim_commit_calls=0,limitations=['Transport/tree/raw/complete source reconstruction evidence only. SOURCE_EXACT remains pending independent full physical path audit.','Original S01 STOP/one entered solve/-9/no final JSON, D64/H STOP and all historical UNKNOWN remain bound and unchanged.','All5 reconstruction attempts preserved, including false active0/b3 bridge M2 and original fallback active1/b3 true M33. Failed attempt is not erased or declared qualified.','Motion7 and Motion5 have equal q but distinct actual Motion/state identities in different trees; they were never merged. Actual saved bridge is6to5.','Original native path/IK files are retained at native text precision. Independent candidate derives only from full saved binary64 M arrays; no rounding repair.','No new FK/IK/NR/collision/RBS/model execution, CCD/global planning statistics/RSS/full-paper qualification. Actual source internal calls and false returns are retained.','GNUtime covers complete runner import/preflight/source/reap/journal/execution/receipt persistence/exit; supervisor own persistence overhead explicitly excluded.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write(f"# S02 人员独立保存transport与费用POST\n\n{report['status']}：{report['checks_passed']}/{len(checks)}，失败{len(failed)}。exact55字节前导+唯一JSON，原raw/journal/trace全同一，6Motion/6state双树、原桥6→5与相同q的7/5不同身份均核。源exact/nonapprox仅候选，不是独立物理路径PASS。\n\n五次原state回溯 true,true,false,true,true 全保留；桥active0/b3失败M2，原程序fallback active1/b3成功M33。四份成功M109/145/33/129完整高精度拼接413节点，首末和5milestone顺序严格同一，原生5个文件按原字节保留。原S01/D/H STOP/UNKNOWN不变。\n\n外层上界wall={uw}s/CPU={uc}s；S01+S02共享累计{shared_w}/{shared_c}≤原30/60。仅本S02以上界替换内部样本一次，S01不重复计费。0科学/runner import/编译/protocol/prior/claim/commit，无独立物理/CCD/统计成功声明。\n")
    print(json.dumps({k:report[k]for k in('status','checks_total','checks_passed','checks_failed','external_supervision_qualified','upper_wall_s','upper_cpu_s','shared_S01_S02_upper_wall_s','shared_S01_S02_upper_cpu_s','independent_path_qualified')},ensure_ascii=False))
if __name__=='__main__':main()
