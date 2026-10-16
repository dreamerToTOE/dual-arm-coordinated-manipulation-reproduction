#!/usr/bin/env python3
"""Independent LOCAL02 saved-only audit; no runner/model import or scientific call.

Reads immutable saved bytes and git blobs. Uses stdlib comparisons and arithmetic;
sole subprocess is git-show. Writes new reports exclusively; never edits evidence.
"""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import base64,datetime,hashlib,json,math,struct,subprocess
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=ROOT/'results/p4_full/20261015_R2_ABB_CBIRRT_D_LOCAL02'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_LOCAL02_SAVED_INDEPENDENT_POST_20261016.json'
MARKER=b'P4_CBIRRT_D_TRACE '
PASS='PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED'
GATES=('actual12_all_true','six_plain_trace_pairs_binary64_equal','complete_three_M_binary64_equal_saved80_65_34','two_SVC_zero_CBi_zero_direct_rng','raw_EOF_and_all_processes_reaped_exit0','old177_complete_discrete_certificate_reused','external_cost_and_identity_qualified','original_D64_STOP_and_H_STOP_preserved')
def exact(a,b):
    if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
    if type(a)in(int,float)and type(b)in(int,float):return struct.pack('>d',a)==struct.pack('>d',b)
    if type(a)is not type(b):return False
    if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
    if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
    return a==b
def bits(q):return struct.pack('>'+str(len(q))+'d',*q).hex()
def norm(r):
    omit=('mode','source_counts_observed','source_started','source_completed','trace')
    q={k:v for k,v in r.items()if k not in omit};q['construction']={k:v for k,v in q['construction'].items()if k not in omit};return q

def main():
    if not(RUN/'execution.json').is_file():raise SystemExit('WAIT_SAVED_EXECUTION_NO_ACTION')
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
    ck('recipe','exact committed frozen source',e['source_commit']=='4ffdda4'+e['source_commit'][7:]and p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())and e['status']==PASS)
    ck('recipe','protocol and claim unchanged before/after',sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']=='2d56ecdb7ed755da4526218102eb4d742d7134dedbf9b13a4a2dd51d7b3e8723'and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256']and claim['protocol_sha256']==e['protocol_sha256'])
    ck('recipe','all bound sets unchanged',p['bound_files_sha256']==e['bound_files_sha256']==e['bound_files_after_sha256'])
    for n,h in p['bound_files_sha256'].items():ck('bound',n,sha(n)==h)
    for n,h in p['own_source_sha256'].items():ck('commit',n,hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest()==h)
    ck('commit','frozen protocol blob',hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+e['protocol']],cwd=ROOT)).hexdigest()==e['protocol_sha256'])
    ledger=load(p['prerequisites']['authoritative_ledger']);prior={r['execution']:r['execution_sha256']for r in ledger['executions']}
    ck('prior','all actual executions once except current',len(prior)==len(ledger['executions'])==32 and prior==p['prior_execution_sha256']==e['prior_execution_sha256']==e['prior_execution_after_sha256']and set(prior)=={str(q.relative_to(ROOT))for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent!=RUN})
    for r in ledger['executions']:ck('prior',r['execution'],sha(r['execution'])==r['execution_sha256'])
    wall=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in ledger['executions']);cpu=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in ledger['executions'])
    ck('prior','effective external charge used exactly once',wall==p['previous_r2_wall_s']==e['previous_r2_wall_s']==ledger['conservative_r2_sum_wall_s']and cpu==p['previous_r2_cpu_s']==e['previous_r2_cpu_s']==ledger['conservative_r2_sum_cpu_s'])
    ck('scope','frozen exact budget and all8 POST gates',p['budget']=={'wall_s':30.,'cpu_s':60.,'child_cpu_limit_s':30,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.}and p['independent_POST_contract']['required_gates']=={k:True for k in GATES}and set(p['independent_POST_contract']['required_gates'])==set(GATES))
    rows=[json.loads(x)for x in raw(e['evidence_journal']).splitlines()if x.strip()];events=Counter(x['event']for x in rows)
    ck('journal','complete hash and exact all event counts',sha(e['evidence_journal'])==e['evidence_journal_sha256']and events==Counter(setup=1,local_request=12,local_dispatch_started=12,raw_response_line=12,parsed_response_before_gates=12,qualified_local=12,local_completed=12,source_process_start_attempted=2,source_process_started=2,session_started=2,plain_trace_comparisons=1,final_counts_and_prefix=1))
    requests=[x['fixture']for x in rows if x['event']=='local_request'];parsed=[x for x in rows if x['event']=='parsed_response_before_gates'];rawlines=[x for x in rows if x['event']=='raw_response_line'];qualified=[x['metric']for x in rows if x['event']=='qualified_local']
    ck('calls','original exact12 schedule all completed no unknown',exact(requests,p['fixed_schedule'])and [x['dispatch_index']for x in parsed]==[x['dispatch_index']for x in rawlines]==[x['dispatch_index']for x in qualified]==e['completed_dispatch_ids']==list(range(12))and not e['UNKNOWN_uncompleted_fixtures'])
    edges=p['fixed_edges'];attempts=[json.loads(x)for x in raw(edges[0]['source_attempt']).splitlines()];expected_edges=[(0,3,80),(1,3,65),(0,0,34)]
    ck('M','exact original3 edges',len(edges)==len(attempts)==3 and [(x['active_chain'],x['branch'],x['reference_node_count'])for x in edges]==expected_edges)
    for i,(edge,old)in enumerate(zip(edges,attempts)):
        ck('M',str(i)+' old complete M and endpoints binary64',edge['edge_index']==old['attempt_index']==i and old['returned']is True and exact(edge['reference_path_q12'],old['path_q12'])and exact(edge['qa12'],old['qa12'])and exact(edge['qb12'],old['qb12'])and len(old['path_q12'])==expected_edges[i][2]and sha(edge['source_attempt'])==edge['source_attempt_sha256'])
        ck('M',str(i)+' nontrivial full state distance',math.sqrt(math.fsum((a-b)**2 for a,b in zip(edge['qa12'],edge['qb12'])))>.05)
    responses={};projections={};raw_expected=[];constructors={};trace_total=Counter();trace_return=Counter()
    for i,(f,z,rl,qmetric)in enumerate(zip(p['fixed_schedule'],parsed,rawlines,qualified)):
        r=z['response'];edge=edges[f['edge_index']];mode=f['mode'];call=f['local_call'];responses[(mode,f['edge_index'],call)]=r
        line=base64.b64decode(rl['base64'],validate=True)
        ck('raw',str(i)+' base64 complete original response',len(line)==rl['bytes']and line.endswith(b'\n')and exact(json.loads(line),r))
        ck('calls',str(i)+' exact true original body return',r['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1'and r['status']=='SOURCE_INTERFACE_COMPLETED_NOT_QUALIFIED'and r['environment']=='II'and r['operation']=='local'and r['mode']==mode and exact(r['request'],f['request'])and r['returned']is True and r['source_dispatch_started']==r['source_dispatch_completed']==1 and qmetric['returned']is True)
        ck('scope',str(i)+' no solve formal path or physical query',r['solve_calls']==r['formal_table_I_calls']==0 and r['independent_path_qualified']is False and qmetric['new_independent_physical_queries']==0)
        for k in('qa12','qb12'):ck('states',str(i)+k,exact(r[k+'_after'],f['request'][k])and bits(r[k+'_after'])==bits(f['request'][k])==r[k+'_binary64_after'])
        c=r['construction'];ck('construction',str(i)+' SVC only no rng seeds',c['svc_only_constructor_dispatch_completed']==1 and c['cbirrt_constructor_dispatch_completed']==c['ompl_setSeed_calls_completed']==c['srand_calls_completed']==c['source_direct_rng_member_initializations_structural']==0 and c['source_direct_rng_member_true_started_completed']=='UNOBSERVED_LIBRARY_NOT_HOOKED'and c['library_internal_seed_draws']=='UNOBSERVED_NOT_REPORTED_ZERO')
        ck('construction',str(i)+' explicit observed flags',r['source_counts_observed']is(mode=='trace')and c['source_counts_observed']is(mode=='trace'))
        if mode not in constructors:
            constructors[mode]=c
            if mode=='trace':raw_expected.extend(c['trace'])
        else:ck('construction',str(i)+' once per process',exact(c,constructors[mode]))
        if call=='reconstruct':ck('M',str(i)+' complete M exact all binary64 including endpoints',exact(r['path_q12'],edge['reference_path_q12'])and len(r['path_q12'])==edge['reference_node_count'])
        if mode=='plain':ck('plain',str(i)+' internals remain UNOBSERVED',all(x[k]is None for x in(r,c)for k in('source_started','source_completed','trace')));continue
        u,v=c['trace'];ck('trace',str(i)+' exact mesh constructor',c['source_started']==c['source_completed']=={'mesh_load':1}and u=={'event':'entered','id':1,'kind':'mesh_load','args':{}}and v=={'event':'completed','id':1,'kind':'mesh_load','result':{}})
        trace=r['trace'];raw_expected.extend(trace);stack=[];pairs=[];started=Counter();completed=Counter();serial=0
        allowed={'state_rbs','vector_rbs','state_reconstruct','vector_reconstruct','fixed_branch_project','native_fk','native_ik','collision'}
        for j,x in enumerate(trace):
            ck('trace',str(i)+':'+str(j)+' allowed true event',x['kind']in allowed and x['event']in('entered','completed'))
            if x['event']=='entered':
                serial+=1;ck('trace',str(i)+':'+str(j)+' serial',x['id']==serial);stack.append(x);started[x['kind']]+=1
            else:
                parent=stack.pop()if stack else {};ck('trace',str(i)+':'+str(j)+' nested matched return',parent.get('id')==x['id']and parent.get('kind')==x['kind']);pairs.append((parent,x));completed[x['kind']]+=1
        top='state_rbs'if call=='rbs'else'state_reconstruct';vector='vector_rbs'if call=='rbs'else'vector_reconstruct';n=edge['reference_midpoint_count'];expect={top:1,vector:2*n+1,'fixed_branch_project':n,'native_fk':n,'native_ik':n,'collision':n}
        ck('trace',str(i)+' exact nontrivial recursion counts',not stack and started==completed and dict(started)==r['source_started']==r['source_completed']==expect)
        ck('trace',str(i)+' top source exact request',trace[0]['kind']==trace[-1]['kind']==top and trace[0]['id']==trace[-1]['id']==1 and exact(trace[0]['args'],{k:f['request'][k]for k in('qa12','qb12','active_chain','branch')})and trace[-1]['result']['returned']is True)
        projection=[]
        for a,b in sorted(pairs,key=lambda z:z[0].get('id',-1)):
            k=a.get('kind');ar=a.get('args',{});res=b['result']
            if k in('state_rbs','vector_rbs','state_reconstruct','vector_reconstruct','native_ik'):ck('trace',str(i)+':'+str(a['id'])+' all source returns true',res['returned']is True)
            if k in('state_rbs','vector_rbs','state_reconstruct','vector_reconstruct','fixed_branch_project'):ck('trace',str(i)+':'+str(a['id'])+' original role branch',ar['active_chain']==edge['active_chain']and ar['branch']==edge['branch'])
            if k=='native_ik':ck('trace',str(i)+':'+str(a['id'])+' passive IK role branch',ar['robot_num']==2-edge['active_chain']and ar['branch']==edge['branch'])
            if k=='native_fk':ck('trace',str(i)+':'+str(a['id'])+' active FK role',ar['robot_num']==1+edge['active_chain'])
            if k=='collision':ck('trace',str(i)+':'+str(a['id'])+' actual collision clear',type(res['returned'])is int and res['returned']==0)
            if k=='fixed_branch_project':
                part=slice(edge['active_chain']*6,(edge['active_chain']+1)*6);ck('trace',str(i)+':'+str(a['id'])+' active joints unchanged',res['returned']is True and exact(ar['q12'][part],res['q12'][part]));projection.append(dict(input=ar,returned=res))
        ck('M',str(i)+' projection output multiset exact old M interior',Counter(bits(x['returned']['q12'])for x in projection)==Counter(bits(q)for q in edge['reference_path_q12'][1:-1]))
        if call=='reconstruct':ck('M',str(i)+' true state trace whole M',exact(trace[-1]['result']['path_q12'],edge['reference_path_q12']))
        projections[(edge['edge_index'],call)]=projection;trace_total.update(started);trace_return.update(completed)
    for edge in edges:
        i=edge['edge_index']
        for call in('rbs','reconstruct'):ck('pairs',str(i)+call,exact(norm(responses[('plain',i,call)]),norm(responses[('trace',i,call)])))
        ck('projection',str(i)+' full RBS/reconstruct projection sequences',exact(projections[(i,'rbs')],projections[(i,'reconstruct')]))
    started_events=[x for x in rows if x['event']=='source_process_started'];groups_start=[x for x in rows if x['event']=='session_started'];all_pids=[];all_raw=[]
    for mode in('plain','trace'):
        binding=e['source_raw_trace_bindings'][mode];sr=next(x for x in started_events if x['mode']==mode);sg=next(x for x in groups_start if x['mode']==mode);all_pids.append(sr['pid']);close=binding['source_close_process_group']
        ck('process',mode+' actual start and close group snapshots',len(sg['process_group'])==len(close)==1 and sg['pid']==sr['pid']==sg['process_group'][0]['pid']==sg['process_group'][0]['pgrp']==close[0]['pid']==close[0]['pgrp']and sg['process_group'][0]['ppid']==close[0]['ppid'])
        ck('process',mode+' full EOF exit no extra stdout',binding['completed_responses']==6 and binding['startup_complete']is True and binding['pipe_EOF_drained']is True and binding['cleanup_closed']is True and binding['unexpected_stdout_tail_bytes']==0 and binding['process_returncode']==0 and binding['complete_raw_evidence_gate']is True and binding['unparseable_trace_tails']==[])
        stream={}
        for channel,info in binding['raw_streams'].items():stream[channel]=raw(info['path']);ck('raw',mode+channel+' actual bytes bound',len(stream[channel])==info['bytes']and sha(info['path'])==info['sha256'])
        lines=stream['stdout'].splitlines(keepends=True);wanted=[base64.b64decode(x['base64'],validate=True)for x in rawlines if p['fixed_schedule'][x['dispatch_index']]['mode']==mode];ck('raw',mode+' exact6 raw stdout lines',len(lines)==6 and all(x.endswith(b'\n')for x in lines)and lines==wanted)
        actual=[];bad=[]
        for line in stream['stderr'].splitlines(keepends=True):
            if MARKER not in line:continue
            try:actual.append(json.loads(line.split(MARKER,1)[1]));ck('raw',mode+' complete trace line',line.endswith(b'\n'))
            except(ValueError,UnicodeDecodeError):bad.append(line)
        ck('raw',mode+' actual complete source stderr trace',not bad and exact(actual,raw_expected if mode=='trace'else[])and len(actual)==binding['actual_trace_events']==binding['expected_trace_events']and binding['raw_trace_binary64_matches']is True)
        all_raw.extend(actual)
    ck('process','all2 registered reaped actual unique PIDs',len(set(all_pids))==2 and len(e['source_process_registry'])==2 and {x['pid']for x in e['source_process_registry']}==set(all_pids)and all(x['reaped']is True and x['returncode']==0 for x in e['source_process_registry'])and not e['unregistered_runtime_raw_prefixes'])
    observed_start=Counter(x['kind']for x in all_raw if x['event']=='entered');observed_end=Counter(x['kind']for x in all_raw if x['event']=='completed');trace_total['mesh_load']+=1;trace_return['mesh_load']+=1
    ck('trace','whole actual stderr body counts equal all12 evidence',observed_start==observed_end==trace_total==trace_return and dict(observed_start)==e['actual_raw_trace_started']==e['actual_raw_trace_completed']and observed_start==Counter(mesh_load=1,state_rbs=3,vector_rbs=349,fixed_branch_project=346,native_fk=346,native_ik=346,collision=346,state_reconstruct=3,vector_reconstruct=349))
    cert=p['saved177_certificate'];oldpath=load(cert['execution']);oldpp=load(oldpath['protocol']);queue=oldpp['fixed_queue'];seen=set();leaves=0
    ck('certificate','full original177 proof and reused object',exact(cert,e['reused_saved177_certificate'])and cert['qualified_unique_nodes']==177 and cert['edge_node_counts']==[80,65,34]and cert['continuous_collision_certificate']is False and sha(cert['execution'])==cert['execution_sha256']and oldpath['status']=='PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH'and oldpath['full_queue_checked']is True and oldpath['completed_nodes']==oldpath['qualified_nodes']==177 and not oldpath['uncompleted_node_ids'])
    for n,h in cert['files_sha256'].items():ck('certificate',n,sha(n)==h)
    for i,oldedge in enumerate(queue['edges']):
        qs=[queue['nodes'][j]for j in oldedge['node_ids']];seen.update(oldedge['node_ids']);leaves+=len(qs)-1
        ck('certificate',str(i)+' full node mapping and leaves',exact(qs,edges[i]['reference_path_q12'])and oldedge['active_chain']==edges[i]['active_chain']and oldedge['branch']==edges[i]['branch']and len(oldedge['leaf_distances_rad'])==len(qs)-1 and all(x<.05 for x in oldedge['leaf_distances_rad']))
    ck('certificate','exact177 unique176 leaves',seen==set(range(177))and leaves==176)
    for i,q in enumerate(queue['nodes']):
        base=Path(cert['execution']).parent/f'node_{i:05d}';n=load(str(base)+'.json');collision=load(str(base)+'_collision_response.json')
        ck('certificate',str(i)+' saved completed math limits closure branch collision',n['node_id']==i and exact(n['q12'],q)and n['stage']=='COMPLETED'and n['qualified']is True and n['math_qualified']is True and n['limits']['legal']is True and n['closure']['position_max_abs']<=1e-5 and n['closure']['rotation_matrix_max_abs']<=1e-5 and all(a['branch_pass']is True for a in n['edge_assignments'])and exact(n['collision'],collision)and collision['status']=='CHECKED'and collision['environment']=='II'and collision['collision']is False and collision['selected_variant']=='aligned'and collision['continuous_collision_certificate']is False)
    oldaudit=load('reports/P4_FULL_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW_20261015.json');ck('certificate','old saved personnel independent audit retained',oldaudit['passed']is True and oldaudit['failed_checks']==[]and oldaudit['execution_sha256']==sha(cert['execution'])and oldaudit['summary']['nodes']==177 and oldaudit['summary']['edges']==3 and oldaudit['new_scientific_calls']==0)
    d=load('results/p4_full/20261015_R2_ABB_CBIRRT_D_DISTANCE01/execution.json');h=load('results/p4_full/20261015_R2_ABB_RANDOM_HELPER_H01/execution.json')
    ck('historical','original D STOP61 UNKNOWN and killed tail',d['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET'and d['completed_dispatch_ids']==list(range(61))and [x['dispatch_index']for x in d['UNKNOWN_uncompleted_fixtures']]==[61,62,63]and d['source_process_registry'][-1]['returncode']==-9 and e['original_D64_single_run_PASS']is False)
    ck('historical','original H STOP and unknown preserved by prior exact hash',h['status']=='STOP_CLEANUP_OR_EVIDENCE_ERROR'and sha('results/p4_full/20261015_R2_ABB_RANDOM_HELPER_H01/execution.json')==prior['results/p4_full/20261015_R2_ABB_RANDOM_HELPER_H01/execution.json'])
    tb=raw(ext['sibling_path']);fields=tb.decode().split();elapsed,user,system=map(Decimal,fields[:3]);uw=float(elapsed+Decimal('.01'));uc=float(user+system+Decimal('.02'));metadata=[json.loads(x)for x in raw(ext['metadata_path']).splitlines()];planned,started,reaped=metadata;proof=e['supervisor_launch_proof'];st=path(ext['sibling_path']).stat();receiptlines=raw(RUN/'cost_receipt.jsonl').splitlines();receipt=json.loads(receiptlines[0])
    ck('external','one valid fourfield time exit0 caps',len(fields)==4 and len(tb.splitlines())==1 and all(v.is_finite()and v>=0 for v in(elapsed,user,system))and int(fields[3])==0 and uw<=min(30.,3600.-wall)and uc<=min(60.,7200.-cpu))
    ck('external','actual parent time PID full metadata chain',planned['event']=='planned_launch'and started['event']=='time_process_started'and reaped['event']=='time_process_reaped'and started['pid']==reaped['pid']==proof['actual_time_pid']==charge['time_process_pid']and reaped['returncode']==0 and reaped['failure']is None and proof['supervisor_pid']==planned['supervisor_pid']and proof['actual_time_start_ticks']>0)
    argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/'scripts/qualify_p4_full_r2_abb_cbirrt_d_local_v2_draft.py'),'--protocol',str(path(e['protocol']))]
    ck('external','actual exact argv original inode FD proof',argv==planned['argv']==started['argv']==proof['actual_argv']and planned['time_fd']in proof['actual_time_output_fds']and st.st_ino==planned['time_inode']==proof['time_inode']and st.st_dev==planned['time_device']==proof['time_device']and charge['time_inode_unchanged']is True and hashlib.sha256(raw(ext['metadata_path']).splitlines(keepends=True)[0]).hexdigest()==proof['planned_launch_line_sha256'])
    ck('external','committed runner supervisor time Python protocol bound',planned['protocol_sha256']==sha(e['protocol'])and planned['runner_sha256']==p['own_source_sha256']['scripts/qualify_p4_full_r2_abb_cbirrt_d_local_v2_draft.py']and planned['supervisor_source_sha256']==p['own_source_sha256']['scripts/supervise_p4_full_r2_abb_cbirrt_d_local_v2_draft.py']and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
    ck('external','charge every measured saved artifact bound',charge['execution_sha256']==sha(RUN/'execution.json')and charge['receipt_sha256']==sha(RUN/'cost_receipt.jsonl')and charge['time_sha256']==sha(ext['sibling_path'])and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr_sha256']==sha(ext['stderr_path'])and charge['time_fields']==fields and exact([charge['wall_s'],charge['cpu_s']],[uw,uc])and charge['timing_valid']is True and charge['wall_CPU_caps_pass']is True and charge['completed_process_exit0']is True and charge['time_returncode']==charge['measured_child_exit']==0 and charge['failure']is None)
    ck('external','receipt full execution persistence measured through exit',len(receiptlines)==1 and receipt['execution_sha256']==sha(RUN/'execution.json')and receipt['status']==e['status']==PASS and e['wall_s']<=receipt['wall_s_through_execution_persistence']<=uw and e['cpu_s']<=receipt['cpu_s_through_execution_persistence']<=uc and receipt['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and receipt['external_supervision_qualified']is e['external_supervision_qualified']is charge['external_supervision_qualified']is False)
    ck('external','explicit supervisor own overhead boundary',planned['supervision_cost_boundary']=='GNUtime child runner+all reaped source children. Supervisor own metadata/time-log fsync costs excluded.')
    ck('scope','no physics formal VI and final all gates',all(v==0 for v in e['zero_calls'].values())and e['formal_table_I_calls']==e['new_VI_candidate_constructions']==e['new_independent_physical_queries']==0 and e['full_planner_path_or_RSS_qualified']is False and not e['diagnostics']and e['completed_SVC_constructor_dispatches']==2 and e['CBi_constructor_dispatches']==e['direct_CBi_rng_member_initializations_structural']==0 and e['plain_trace_comparisons']==6 and e['complete_source_raw_evidence_gate']is e['source_process_registry_complete_gate']is e['full_run_raw_body_count_gate']is True)
    ck('preservation','all saved read bytes still identical',all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==v for n,v in retained.items()))
    failed=[x for x in checks if not x['passed']];passed=not failed
    mapping={'actual12_all_true':('calls','states','recipe','bound','commit','prior','scope','journal','raw','preservation'),'six_plain_trace_pairs_binary64_equal':('pairs',),'complete_three_M_binary64_equal_saved80_65_34':('M','projection','trace'),'two_SVC_zero_CBi_zero_direct_rng':('construction','plain'),'raw_EOF_and_all_processes_reaped_exit0':('process','raw'),'old177_complete_discrete_certificate_reused':('certificate',),'external_cost_and_identity_qualified':('external',),'original_D64_STOP_and_H_STOP_preserved':('historical',)}
    gates={k:all(x['passed']for x in checks if x['group']in gs)for k,gs in mapping.items()}
    report=dict(schema='P4_LOCAL02_SAVED_INDEPENDENT_POST_V1',status='PASS_LOCAL02_SAVED_DISCRETE_SEAM_INDEPENDENT_POST'if passed else'FAIL_LOCAL02_SAVED_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of LOCAL02 implementation',personnel_independent=True,checks_total=len(checks),checks_passed=sum(x['passed']for x in checks),checks_failed=len(failed),groups=dict(groups),failures=failed,required_gates=gates,external_supervision_qualified=passed,execution_sha256=sha(RUN/'execution.json'),external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),upper_wall_s=uw,upper_cpu_s=uc,external_time_fields=fields,execution_sample_wall_s=e['wall_s'],execution_sample_cpu_s=e['cpu_s'],charge_rule='Retain execution internal samples; replace exactly once by independent external upper bound. Do not add both.',completed_top_level_calls=12,plain_trace_pairs=6,full_M_node_counts=[80,65,34],reused_discrete_unique_nodes=177,reused_discrete_leaves=176,source_processes=2,source_group_evidence='START_AND_CLOSE_GROUP_SAVED_DIRECT_SNAPSHOTS_BOTH_PROCESSES',actual_raw_trace_started=dict(observed_start),actual_raw_trace_completed=dict(observed_end),original_D64_single_run_PASS=False,retained_sha256=retained,audit_script_sha256=sha(__file__),new_import_runner_model_science_query_compile_protocol_prior_claim_commit_calls=0,limitations=['Original D64 STOP/61 completed/UNKNOWN[61,62,63] and H STOP retained. Split distance certificate only.','Complete M binary64 identity permits reuse of existing177 discrete physical proofs; no new FK/IK/NR/collision queries, continuous collision certificate, global planner path or RSS claim.','Source native FK/IK/collision observed calls are real; plain internal counts and actual library RNG internals remain UNOBSERVED.','GNUtime upper includes Python import/preflight/source/reap/all journal-execution-receipt persistence and exit. Supervisor own persistence overhead is explicitly excluded.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write(f"# LOCAL02 人员独立保存POST\n\n{report['status']}：{report['checks_passed']}/{len(checks)}，失败{len(failed)}；八required_gates全真={all(gates.values())}。真实12次全true、6对plain/trace、三份完整M80/65/34 binary64与原M一致，177唯一节点/176叶旧离散物理证书完整复用；两SVC启动/关闭group均有直接保存快照，raw EOF/trace/退出0及全部哈希完整。\n\n外层GNUtime上界wall={uw:.12f}s、CPU={uc:.12f}s，覆盖runner全尾；内部sample保留，记账以上界替换一次。监督器自身持久化开销明确排除。原D64/H STOP及UNKNOWN保留。只读saved证据及git blob，0runner import/科学/编译/protocol/prior/claim/commit，不构成完整规划/CCD/RSS或论文完成。\n")
    print(json.dumps({k:report[k]for k in('status','checks_total','checks_passed','checks_failed','required_gates','external_supervision_qualified','upper_wall_s','upper_cpu_s')},ensure_ascii=False))
if __name__=='__main__':main()
