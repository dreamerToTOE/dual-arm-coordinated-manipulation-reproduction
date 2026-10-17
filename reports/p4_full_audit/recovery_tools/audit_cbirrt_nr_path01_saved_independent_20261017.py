#!/usr/bin/env python3
"""Personnel independent CBiRRT_NR P saved-only audit; no implementation imports."""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import argparse,base64,datetime,hashlib,json,math,struct,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[3]
RUN='20261016_R2_ABB_CBIRRT_NR_PATH01';F=ROOT/'results/p4_full'/RUN
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_20261017.json'
S='results/p4_full/20261016_R2_ABB_CBIRRT_NR_SOLVE01'
SP='reports/P4_FULL_R2_ABB_CBIRRT_NR_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json'
RR='scripts/qualify_p4_full_r2_abb_cbirrt_nr_path_draft.py';SS='scripts/supervise_p4_full_r2_abb_cbirrt_nr_path_draft.py'
checks=[];retained={}
def path(n):return Path(n)if Path(n).is_absolute()else ROOT/n
def raw(n):
 p=path(n);b=p.read_bytes();retained[str(p)]=hashlib.sha256(b).hexdigest();return b
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def load(n):return json.loads(raw(n))
def jl(n):return[json.loads(z)for z in raw(n).splitlines()if z.strip()]
def ck(g,n,ok):checks.append(dict(group=g,check=n,passed=bool(ok)))
def key(q):return struct.pack('>12d',*q)
def exact(a,b):
 if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
 if type(a)in(int,float)and type(b)in(int,float):return struct.pack('>d',a)==struct.pack('>d',b)
 if type(a)is not type(b):return False
 if isinstance(a,list):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
 if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
 return a==b
def near(a,b,t=1e-12):return math.isfinite(a)and math.isfinite(b)and abs(a-b)<=t
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--protocol-sha256',required=True);ap.add_argument('--expected-source-commit',required=True);args=ap.parse_args()
 if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_REPORT_PRESERVED')
 ex=str((F/'execution.json').relative_to(ROOT));e=load(ex);p=load(e['protocol']);c=load(e['claim']);q=p['fixed_queue']
 ck('freeze','exact reviewedrootcommit frozenprotocolclaim',e['source_commit']==args.expected_source_commit and p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())and sha(e['protocol'])==args.protocol_sha256==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256']and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256']and c['source_commit']==e['source_commit']and c['no_retry_reset_resume']is True)
 ck('freeze','exact actualP schema fullpathscope',e['schema']=='P4_R2_ABB_CBIRRT_NR_PATH_EXECUTION_V1'and e['run_id']==p['run_id']==RUN and e['independent_path_qualified']is e['continuous_collision_certificate']is False and p['budget']==dict(wall_s=120.,cpu_s=240.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.))
 ck('freeze','allactualboundmaps beforeafter',p['bound_files_sha256']==e['bound_files_sha256']==e['bound_files_after_sha256'])
 for n,h in p['bound_files_sha256'].items():ck('bound',n,sha(n)==h)
 for n,h in p['own_source_sha256'].items():ck('commit',n,sha(n)==h==hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest())
 ck('commit','exactprotocol committedblob',hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+e['protocol']],cwd=ROOT)).hexdigest()==args.protocol_sha256)
 se=load(S+'/execution.json');sp=load(SP);d=load(S+'/source_stdout.bin')
 ck('source','unchanged realS16711 independentcandidate no pathPASS',sha(S+'/execution.json')=='bc30019b1e5282817adee945fbb4b86a7bb9f30e6f419a6def0e559815a7b1b6'and sha(SP)=='549d585f1fb2be390b28a0d64dfb90815e58092a9efd7e3c4d478abebe381ef1'and sp['checks_total']==sp['checks_passed']==16711 and sp['checks_failed']==0 and sp['successful_transport_qualified']is sp['personnel_independent']is sp['external_supervision_qualified']is True and sp['independent_path_qualified']is False and exact(d['request'],p['source_provenance']['request'])and e['source_provenance']==p['source_provenance'])
 by={n['motion_id']:n for n in d['trees']['nodes']};mpaths=next(z['args']['source_mpaths']for z in d['trace']if z['event']=='observed');order=list(reversed(mpaths[0]))+mpaths[1];ms=d['milestones_q12'];starts={z['id']:z for z in d['trace']if z['event']=='entered'};attempts=[]
 ck('tree','actual16unique trees roots2/3 bridge16to14 sameq17 notmerged',len(by)==len({n['state_id']for n in by.values()})==16 and {n['motion_id']for n in by.values()if not n['parent_motion_id']}=={2,3}and [n['motion_id']for n in order]==[2,15,16,14,11,10,9,8,7,6,4,3]and [d['trees']['connection_'+s]['motion_id']for s in ['start','goal']]==[16,14]and key(by[17]['q12'])==key(by[14]['q12'])and by[17]['state_id']!=by[14]['state_id'])
 for n in by.values():
  cur=n;seen=set();ok=True
  while cur['parent_motion_id']:
   if cur['motion_id']in seen or cur['parent_motion_id']not in by:ok=False;break
   seen.add(cur['motion_id']);cur=by[cur['parent_motion_id']];ok=ok and cur['tree']==n['tree']
  ck('tree','rootparent '+str(n['motion_id']),ok and cur['motion_id']==n['root_motion_id']and cur['state_id']==n['root_state_id']and key(cur['q12'])==key(n['root_q12']))
 for i,n in enumerate(order):ck('tree','originalmpathstateparentq '+str(i),n['parent_id']==by[n['motion_id']]['parent_motion_id']and n['state_id']==by[n['motion_id']]['state_id']and key(n['q12'])==key(by[n['motion_id']]['q12'])==key(ms[i]))
 for z in d['trace']:
  if z['event']=='completed'and z['kind']=='state_reconstruct':
   a=starts[z['id']];attempts.append(dict(attempt_index=len(attempts),trace_entry_id=a['id'],trace_return_id=z['id'],qa12=a['args']['qa12'],qb12=a['args']['qb12'],returned=z['result']['returned'],path_q12=z['result']['path_q12']))
 ck('queue','exactall11originalfullM arrays',exact(attempts,q['all_original_attempts'])and [len(a['path_q12'])for a in attempts]==[65,65,17,65,129,129,65,33,33,33,65])
 nodes=q['nodes'];edges=q['edges'];lookup={};rebuilt=[];refs=[];leaves=[]
 def add(v,ref):
  k=key(v)
  if k not in lookup:lookup[k]=len(rebuilt);rebuilt.append(dict(node_id=len(rebuilt),environment='II',q12=v,refs=[],collision_required=True))
  rebuilt[lookup[k]]['refs'].append(ref);return lookup[k]
 for i,(edge,a)in enumerate(zip(edges,attempts)):
  qs=a['path_q12'];ids=[add(v,dict(kind='original_dense_M',edge_index=i,attempt_index=i,path_index=j,trace_entry_id=a['trace_entry_id']))for j,v in enumerate(qs)];ls=[math.sqrt(math.fsum((x-y)**2 for x,y in zip(v,w)))for v,w in zip(qs,qs[1:])];refs.extend(ids);leaves.extend(ls)
  ck('queue','fulloriginaledge '+str(i),a['returned']is True and key(a['qa12'])==key(qs[0])==key(ms[i])and key(a['qb12'])==key(qs[-1])==key(ms[i+1])and edge['node_ids']==ids and exact([nodes[k]['q12']for k in ids],qs)and exact(ls,edge['leaf_distances_rad'])and all(v<.05 for v in ls)and edge['qa_motion_id']==order[i]['motion_id']and edge['qb_motion_id']==order[i+1]['motion_id']and edge['qa_state_id']==order[i]['state_id']and edge['qb_state_id']==order[i+1]['state_id']and edge['edge_kind']==('start_parent_to_child'if i<2 else'actual_cross_tree_bridge'if i==2 else'goal_child_to_parent'))
 mids=[add(n['q12'],dict(kind='original_milestone',milestone_index=i,motion_id=n['motion_id'],state_id=n['state_id']))for i,n in enumerate(order)]
 ck('queue','entire699refs689nodes688strictleaves no truncation exactrefs',len(nodes)==689 and len(refs)==699 and len(leaves)==688 and len(edges)==11 and exact(nodes,rebuilt)and set(refs)==set(range(689))and q['milestone_node_ids']==mids and q['full_queue_node_count']==p['full_queue_node_count']==689 and q['full_dense_leaf_count']==688 and q['full_dense_node_reference_count']==699 and q['under_2048_full_queue_cap']is True and p['max_nodes_per_execution']==2048)
 ck('queue','savedqueue frozenexact firstlastbinary64',exact(load(F/'complete_original_saved_queue.json'),q)and key(nodes[0]['q12'])==key(d['request']['start_q12'])and key(nodes[-1]['q12'])==key(d['request']['goal_q12']))
 ck('complete','all689qualified no tail diagnostics actualPATHPASS',e['node_count']==e['completed_nodes']==e['qualified_nodes']==689 and e['uncompleted_node_ids']==[]and e['full_queue_checked']is True and e['status']=='PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH'and e['diagnostics']==[])
 events=jl(F/'events.jsonl');evby=defaultdict(list)
 for ev in events:evby[ev['event']].append(ev)
 ck('events','originaljournal hash setupfinal no stopped',sha(F/'events.jsonl')==e['events_sha256']and len(evby['setup'])==len(evby['final_counts'])==1 and not evby['stopped']and evby['final_counts'][0]['counts']==e['counts']and evby['final_counts'][0]['diagnostics']==[])
 coll=p['collision_manifest'];manifest=load(coll);entries={v['variant']:v for v in manifest['entries']if v['model']=='abb'};ck('collision','realnativealigned builds exactfrozenmanifest',set(entries)=={'native','aligned'}and all(v['exit_code']==0 for v in entries.values())and sha(coll)==p['bound_files_sha256'][coll])
 bounds=[(lo*3.1416/180.,hi*3.1416/180.)for lo,hi in [(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]]*2
 maxpos=maxrot=0.;minmargin=math.inf;pqp=Counter();colcounts=Counter();posepass=Counter();posemax={v:dict(position_mm=0.,rotation=0.)for v in ['native','aligned']}
 for i,src in enumerate(nodes):
  n=load(F/f'node_{i:05d}.json');a1=load(F/f'node_{i:05d}_arm1.json');a2=load(F/f'node_{i:05d}_arm2.json');mr=load(F/f'node_{i:05d}_math.json');cr=load(F/f'node_{i:05d}_collision_raw.json')
  ck('node',str(i)+' completeinputbitsrefs noPCSgate',all(exact(n[k],v)for k,v in src.items())and n['stage']=='COMPLETED'and n['node_qualified']is n['math_qualified']is True and key(n['q12'])==key(src['q12'])and all(k not in n for k in ['branches','active_chain','edge_assignments']))
  ck('node',str(i)+' originalpartials raw fullFKposes retained',exact(a1,{**src,'poses':n['poses'][:1],'stage':'STARTED'})and exact(a2,{**src,'poses':n['poses'],'stage':'STARTED'})and exact(mr,{k:v for k,v in n.items()if k not in ['stage','collision','node_qualified']}|{'stage':'MATH_COMPLETED'})and exact(cr,n['collision'])and len(n['poses'])==2 and all(len(m)==4 and all(len(r)==4 for r in m)and all(math.isfinite(v)for r in m for v in r)and m[3]==[0.,0.,0.,1.]for m in n['poses']))
  t1,t2=n['poses'];cp=max(abs(t2[r][3]-(t1[r][3]+300.*t1[r][0]))for r in range(3));ct=max(abs(t2[r][j]-t1[r][j]*(-1. if j<2 else 1.))for r in range(3)for j in range(3));maxpos=max(maxpos,cp);maxrot=max(maxrot,ct);margins=[min(v-lo,hi-v)for v,(lo,hi)in zip(n['q12'],bounds)];minmargin=min(minmargin,*margins)
  ck('math',str(i)+' independent300graspFLIPclosure originallimitsPI',near(cp,n['closure']['position_max_abs'],1e-10)and near(ct,n['closure']['rotation_matrix_max_abs'],1e-14)and cp<=1e-5 and ct<=1e-5 and min(margins)>=0 and n['limits']==dict(legal=True,violations=[],source_literal_pi_preserved=3.1416,planar_q19_policy=None))
  co=n['collision'];ck('collision',str(i)+' originalselectedalignedclearpolicy',co['environment']=='II'and co['status']=='CHECKED'and co['collision']is False and co['scope']=='AUTHOR_DISCRETE_COLLISION_POLICY'and co['continuous_collision_certificate']is False and co['selected_variant']=='aligned'and list(co['variants'])==['native','aligned']and co['manifest_sha256']==sha(coll))
  for variant,row in co['variants'].items():
   ent=entries[variant];ls=row['source_stdout'].splitlines(keepends=True);term=[v for v in ls if v.startswith('P4_COLLISION_RESULT ')];nr=json.loads(term[0].split(' ',1)[1])if len(term)==1 else{}
   ck('raw',str(i)+' '+variant+' originalunique rawJSON retained',len(term)==1 and ls[-1]==term[0]and term[0].endswith('\n')and set(nr)=={'native_result','cpu_s','poses','query_codes'}and all(exact(row[k],v)for k,v in nr.items())and row['source_stderr']=='merged into source_stdout')
   ck('raw',str(i)+' '+variant+' realPQPcodes0 provenanceboolresult',row['source_command']==[ent['binary'],'II']and row['provenance']=={k:ent[k]for k in ['source_root','source_commit','source_files_sha256','mesh_sha256','binary_sha256','physical_alignment_changes']}and bool(row['query_codes'])and all(type(v)is int and v==0 for v in row['query_codes'])and row['query_error_codes']==[]and type(row['native_result'])is int and row['native_result']in [0,1]and row['native_collision']is bool(row['native_result']))
   pqp[variant]+=len(row['query_codes']);colcounts[variant]+=int(row['native_collision']);pc=row['pose_consistency'];ers=pc['errors'];oks=[]
   for arm,er in enumerate(ers):
    tcp=[row['poses'][arm][j:j+4]for j in [0,4,8]];ind=n['poses'][arm][:3];dp=max(abs(tcp[r][3]-ind[r][3])for r in range(3));dr=max(abs(tcp[r][j]-ind[r][j])for r in range(3)for j in range(3));oks.append(dp<=1e-5 and dr<=1e-5);posemax[variant]['position_mm']=max(posemax[variant]['position_mm'],dp);posemax[variant]['rotation']=max(posemax[variant]['rotation'],dr)
    ck('pose',str(i)+' '+variant+' arm'+str(arm+1)+' independentTCP/rawresidual',er['arm']==arm+1 and exact(er['collision_TCP'],tcp)and exact(er['independent_TCP'],ind)and near(dp,er['translation_maxabs_mm'],1e-12)and near(dr,er['rotation_maxabs'],1e-15))
   ck('pose',str(i)+' '+variant+' actualpasscriterion separately',len(ers)==2 and pc['position_gate_mm']==pc['rotation_matrix_gate']==1e-5 and pc['passed']is all(oks)and pc['status']==('PASS'if all(oks)else'COLLISION_PHYSICAL_TCP_MISMATCH'));posepass[variant]+=int(pc['passed'])
   if variant=='aligned':ck('pose',str(i)+' alignedTCPconsistentclear required',pc['passed']is True and row['native_collision']is False)
  ck('collision',str(i)+' selectedsourceexactaligned',all(exact(co[k],co['variants']['aligned'][k])for k in ['source_command','source_stdout','source_stderr'])and co['collision']is co['variants']['aligned']['native_collision'])
  evs=[v for v in events if v.get('node_id')==i];want=[]
  for arm in [1,2]:want.extend([('math_arm_FK_started',arm),('math_arm_FK_completed',arm)])
  want.append(('collision_started',None))
  for variant in ['native','aligned']:
   for arm in [1,2]:want.extend([('adapter_arm_FK_J_started',arm),('adapter_arm_FK_J_completed',arm)])
  want.append(('collision_completed',None));ck('events',str(i)+' alloriginalscienceevents exactorder',[(v['event'],v.get('arm'))for v in evs]==want and evs[-1]['variant_query_counts']=={v:len(r['query_codes'])for v,r in co['variants'].items()}and evs[-1]['PQP_queries']==sum(len(r['query_codes'])for r in co['variants'].values()))
 counts=dict(collision_worker_start_attempted=2,collision_worker_started=2,math_arm_FK_started=1378,math_arm_FK_completed=1378,collision_calls_started=689,collision_calls_completed=689,adapter_arm_FK_J_started=2756,adapter_arm_FK_J_completed=2756,PQP_queries=sum(pqp.values()))
 ck('counts','actual1378math689collision2756adapter allstartedcompleted',e['counts']==counts and len(evby['math_arm_FK_started'])==len(evby['math_arm_FK_completed'])==1378 and len(evby['collision_started'])==len(evby['collision_completed'])==689 and len(evby['adapter_arm_FK_J_started'])==len(evby['adapter_arm_FK_J_completed'])==2756)
 workers=e['collision_worker_evidence'];reg=e['collision_worker_registry'];ck('workers','twoactualregisteredreapedexit0 truecleanupgate',len(workers)==len(reg)==2 and {v['pid']for v in workers}=={v['pid']for v in reg}and len({v['pid']for v in reg})==2 and all(v['reaped']is True and v['returncode']==0 for v in reg)and e['complete_collision_worker_cleanup_gate']is True)
 for w in workers:
  pid=w['pid'];sg,cg=w['start_process_group'],w['close_process_group'];ck('workers',str(pid)+' directsingleton actualEOF emptytail',len(sg)==len(cg)==1 and sg[0]['pid']==sg[0]['pgrp']==cg[0]['pid']==cg[0]['pgrp']==pid and sg[0]['ppid']==cg[0]['ppid']>0 and w['original_selector_closed']is w['pipe_EOF_drained']is True and base64.b64decode(w['stdout_pending_base64'],validate=True)==base64.b64decode(w['stdout_EOF_tail_base64'],validate=True)==b'')
  for ev,field,value in [('collision_worker_started','pid',pid),('collision_worker_start_group','members',sg),('collision_worker_close_group','members',cg),('collision_worker_after_original_close_group','members',[]),('collision_worker_final_raw_tail','pending_base64','')]:
   rows=[v for v in evby[ev]if v['pid']==pid];ck('workers',str(pid)+' '+ev,len(rows)==1 and exact(rows[0][field],value))
 ck('complete','all3445originalnodefiles nopartialstop',len(list(F.glob('node_*.json')))==3445 and not list(F.glob('*stopped*')))
 snap=e['durable_saved_snapshot'];archive=path(snap['path']);ck('archive','actualfsyncfiledirectory exactdurablesnapshot',sha(archive)==snap['sha256']and snap['archive_file_fsync_completed']is snap['containing_directory_fsync_completed']is snap['loose_files_byte_exact']is True and snap['members_verified']==len(snap['members']))
 members={}
 with tarfile.open(archive,'r:')as tar:
  for member in tar:
   b=tar.extractfile(member).read()if member.isfile()else b'';info=dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));ck('archive',member.name,member.isfile()and member.name not in members and info==snap['members'].get(member.name)and member.size==len(b)and raw(F/member.name)==b);members[member.name]=info
 ck('archive','wholememberset everyloosefile beforeexecutionreceipt',members==snap['members']and {str(v.relative_to(F))for v in F.rglob('*')if v.is_file()and v not in [archive,F/'execution.json',F/'cost_receipt.jsonl']}==set(members))
 for n,h in e['retained_run_files_sha256'].items():ck('archive','retained '+n,sha(n)==h)
 ck('archive','retainedfileinventory exactarchiveplusmembers',{str(path(n).relative_to(F))for n in e['retained_run_files_sha256']}==set(members)|{archive.name})
 prior=p['actual_charge_prior'];ledger=load(prior['ledger']);pm={v['execution']:v['execution_sha256']for v in ledger['executions']};pw=math.fsum(v.get('charged_wall_s',v['wall_s'])for v in ledger['executions']);pcpu=math.fsum(v.get('charged_cpu_s',v['cpu_s'])for v in ledger['executions'])
 ck('prior','actual40allrunprior effectivecharges exact nohiddenrun',len(pm)==40 and sha(prior['ledger'])==prior['ledger_sha256']and pm==prior['execution_sha256']==p['prior_execution_sha256']==e['prior_execution_sha256']==e['prior_execution_after_sha256']and {str(v.relative_to(ROOT)):sha(v)for v in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if v.parent.name!=RUN}==pm and pw==prior['wall_s']==e['previous_r2_wall_s']and pcpu==prior['cpu_s']==e['previous_r2_cpu_s'])
 for v in ledger['executions']:
  ck('prior',v['execution'],sha(v['execution'])==v['execution_sha256'])
  if 'charged_wall_s'in v:
   cert=load(v['external_post']);ck('prior','oneupperreplacement '+v['execution'],sha(v['external_post'])==v['external_post_sha256']and cert['personnel_independent']is cert['external_supervision_qualified']is True and cert['checks_failed']==0 and cert['execution_sha256']==v['execution_sha256']and cert['upper_wall_s']==v['charged_wall_s']and cert['upper_cpu_s']==v['charged_cpu_s']and sha(v['external_time'])==v['external_time_sha256']==cert['external_time_sha256'])
 ext=p['external_supervision'];tb=raw(ext['sibling_path']);fields=tb.decode().split();elapsed,user,system=(Decimal(v)for v in fields[:3]);uw,uc=float(elapsed+Decimal('.01')),float(user+system+Decimal('.02'));meta=raw(ext['metadata_path']);planned,started,reaped=[json.loads(z)for z in meta.splitlines()];proof=e['supervisor_launch_proof'];charge=load(ext['charge_path']);rl=jl(F/'cost_receipt.jsonl');receipt=rl[0];inode=path(ext['sibling_path']).stat();argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/RR),'--protocol',str(path(e['protocol']))]
 ck('external','actualfourfinite timeexit0 original120240andR2caps',len(fields)==4 and len(tb.splitlines())==1 and fields[3]=='0'and all(v.is_finite()and v>=0 for v in [elapsed,user,system])and uw<=min(120.,3600.-pw)and uc<=min(240.,7200.-pcpu))
 ck('external','actualGNUtimeparentPIDargvheldFDinode reaped0',planned['event']=='planned_launch'and started['event']=='time_process_started'and reaped['event']=='time_process_reaped'and started['pid']==reaped['pid']==proof['actual_time_pid']==charge['time_process_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid']and argv==planned['argv']==started['argv']==proof['actual_argv']and inode.st_ino==planned['time_inode']==proof['time_inode']and inode.st_dev==planned['time_device']==proof['time_device']and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and hashlib.sha256(meta.splitlines(keepends=True)[0]).hexdigest()==proof['planned_launch_line_sha256'])
 ck('external','actualfrozenplannedsourcebinarySHA',planned['protocol_sha256']==args.protocol_sha256 and planned['runner_sha256']==p['own_source_sha256'][RR]and planned['supervisor_source_sha256']==p['own_source_sha256'][SS]and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
 ck('external','actualchargeexactsource executionreceiptfullhash andtrueexitcap',charge['source_execution']==ex and charge['execution_sha256']==sha(ex)and charge['receipt_sha256']==sha(F/'cost_receipt.jsonl')and charge['time_sha256']==sha(ext['sibling_path'])and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr_sha256']==sha(ext['stderr_path'])and charge['time_fields']==fields and exact([charge['wall_s'],charge['cpu_s']],[uw,uc])and charge['timing_valid']is charge['time_inode_unchanged']is charge['wall_CPU_caps_pass']is charge['completed_process_exit0']is True and charge['time_returncode']==charge['measured_child_exit']==0 and charge['failure']is None)
 ck('external','wholechild receiptpersistencefinalexit coveredbytrueupper',len(rl)==1 and receipt['execution_sha256']==sha(ex)and receipt['status']==e['status']and 0<=e['wall_s']<=receipt['wall_s_through_execution_persistence']<=uw and 0<=e['cpu_s']<=receipt['cpu_s_through_execution_persistence']<=uc and receipt['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and receipt['external_supervision_qualified']is e['external_supervision_qualified']is charge['external_supervision_qualified']is False)
 ck('scope','originalNRthresholds full12 noactivebranch CCDfalse',p['gates']==dict(position_maxabs_mm=1e-5,rotation_matrix_maxabs=1e-5,strict_leaf_full12_L2_rad=.05,source_literal_pi_for_mechanical_limits=3.1416,source_PQP_tolerance_mm=8.,fixed_active_or_branch_gate=False,continuous_collision_certificate=False))
 ck('scope','allzero IKNRsolveRBSprojectionRNGVIformal obligationsunchanged',e['zero_calls']==dict.fromkeys(['IK','NR','projection','RBS','solve','RNG','VI_constructions','formal_table_I'],0)and e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and q['independent_path_qualified']is q['continuous_collision_certificate']is False and ledger['vi_B_remaining']['candidate_constructions']==0 and ledger['formal_table_I_calls']==0 and ledger['formal_table_I_required_calls']==22500)
 for n,h in list(retained.items()):ck('unchanged',n,hashlib.sha256(Path(n).read_bytes()).hexdigest()==h)
 fail=[v for v in checks if not v['passed']];ok=not fail
 r=dict(schema='P4_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_V1',status='PASS_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST'if ok else'FAIL_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review independent of P helper runner supervisor',personnel_independent=True,checks=checks,checks_total=len(checks),checks_passed=len(checks)-len(fail),checks_failed=len(fail),failures=fail,independent_path_qualified=ok,external_supervision_qualified=ok,external_timing_qualified=ok,external_cost_qualified=ok,execution=ex,execution_sha256=sha(ex),protocol=e['protocol'],protocol_sha256=sha(e['protocol']),claim=e['claim'],claim_sha256=sha(e['claim']),receipt=ext['charge_path'],receipt_sha256=sha(ext['charge_path']),internal_receipt=str((F/'cost_receipt.jsonl').relative_to(ROOT)),internal_receipt_sha256=sha(F/'cost_receipt.jsonl'),source_execution=S+'/execution.json',source_execution_sha256=sha(S+'/execution.json'),source_POST=SP,source_POST_sha256=sha(SP),nodes=689,edges=11,leaves=688,dense_references=699,maximum_full12_leaf_rad=max(leaves),maximum_saved_closure_position_mm=maxpos,maximum_saved_closure_rotation=maxrot,minimum_source_mechanical_margin_rad=minmargin,native_collision_nodes=colcounts['native'],aligned_collision_nodes=colcounts['aligned'],variant_pose_pass_nodes=dict(posepass),variant_pose_max_errors=posemax,variant_PQP_queries=dict(pqp),PQP_queries=sum(pqp.values()),actual_counts=e['counts'],external_time=ext['sibling_path'],external_time_sha256=sha(ext['sibling_path']),external_time_fields=fields,upper_wall_s=uw,upper_cpu_s=uc,previous_charged_wall_s=pw,previous_charged_cpu_s=pcpu,cumulative_charged_wall_s=math.fsum([pw,uw]),cumulative_charged_cpu_s=math.fsum([pcpu,uc]),retained_sha256=retained,audit_script_sha256=sha(__file__),new_runner_model_import_describe_compile_binary_query_solve_protocol_prior_claim_calls=0,limitations=['Complete saved original path discrete source-policy qualification only; original execution independent_path_qualified=false preserved.','Native/aligned statuses separately reported. No fixed passive/analyticbranch gate for NR. No continuous collision, solidrod/omittedpair safety, nativeKDL equivalence, globalstatistics, RSS/PCSadvantage or completepaper claim.211obligationsVI974remaining0formal0/22500 persist.','GNUtime whole-child includes import/preflight/saved arrays/model/collision/cleanup/archive/verify/finalhash/receipt/exit. Supervisorownlog/fsync excluded. Only current upper replaces own once; historical unmeasured tails remain UNKNOWN.'])
 with OUT.open('x')as f:json.dump(r,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
 with OUT.with_suffix('.md').open('x')as f:f.write('# CBiRRT_NR 完整路径独立后审\n\n'+r['status']+'：'+str(r['checks_passed'])+'/'+str(len(checks))+'，失败'+str(len(fail))+'。完整689节点、688叶、699原M引用和11条原边均独立核验。\n\n数学闭链/原限位、native与aligned各自原raw/PQP/TCP/计数、全部worker实际EOF/reap/空组、全部durable tar member与散文件逐字匹配、完整尾节点及外层费用均核。aligned碰撞'+str(colcounts['aligned'])+'，native碰撞'+str(colcounts['native'])+'；最大闭链误差'+str(maxpos)+'mm / '+str(maxrot)+'。\n\n外层上界'+str(uw)+'wall / '+str(uc)+'CPU，只替换本次内部一次。原execution false与旧STOP/UNKNOWN保留；211项、VI974余0、formal0/22500不变。无连续碰撞或算法统计优势结论。\n')
 print(json.dumps({k:r[k]for k in ['status','checks_total','checks_failed','failures','independent_path_qualified','upper_wall_s','upper_cpu_s','maximum_saved_closure_position_mm','maximum_saved_closure_rotation','native_collision_nodes','aligned_collision_nodes']},ensure_ascii=False))
 if fail:raise SystemExit(2)
if __name__=='__main__':main()
