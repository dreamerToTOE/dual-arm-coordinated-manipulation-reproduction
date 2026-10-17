#!/usr/bin/env python3
"""Personnel-independent saved SETUP01 POST; stdlib only, no science execution."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import argparse,base64,datetime,hashlib,json,math,os,struct,subprocess
ROOT=Path(__file__).resolve().parents[3]
RUN='20261017_R2_ABB_SBL_PCS_SETUP01'
STATIC='reports/P4_FULL_R2_ABB_SBL_PCS_SETUP01_INDEPENDENT_STATIC_REVIEW_ADDENDUM_20261017.json'
STATIC_SHA='6561fbbbed04c004a3472180b93d5c6c4aa8c7ce67c35ec8f30576353e4b8e8a'
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST_20261017.json'
checks=[];retained={}
def path(n):
 p=Path(n);return p if p.is_absolute()else ROOT/p
def raw(n):
 p=path(n);b=p.read_bytes();retained[str(p)]=hashlib.sha256(b).hexdigest();return b
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def reject(value):raise ValueError('NONFINITE_JSON_TOKEN '+value)
def parse(b):return json.loads(b,parse_constant=reject)
def load(n):return parse(raw(n))
def exact(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False)
def ck(g,n,v):checks.append(dict(group=g,check=n,passed=bool(v)))
def members(pgid):
 out=[]
 for p in Path('/proc').glob('[0-9]*/stat'):
  try:
   a=p.read_text().rsplit(')',1)[1].split()
   if int(a[2])==pgid:out.append(int(p.parent.name))
  except (OSError,ValueError,IndexError):pass
 return sorted(out)
def hex64(q):return ''.join(struct.pack('>d',float(x)).hex()for x in q)
def finite(q,n):return isinstance(q,list)and len(q)==n and all(type(x)in(int,float)and math.isfinite(x)for x in q)
def elf_exports(filename,names):
 b=raw(filename);h=struct.unpack_from('<16sHHIQQQIHHHHHH',b)
 if b[:6]!=b'\x7fELF\x02\x01'or h[2]!=62 or h[11]!=64 or not(0<h[12]<65535):raise ValueError('SAVED_ELF64_REQUIRED')
 table=[struct.unpack_from('<IIQQQQIIQQ',b,h[6]+i*64)for i in range(h[12])];out={n:[]for n in names}
 for section in table:
  if section[1]!=11:continue
  if section[9]!=24 or section[5]%24:raise ValueError('SAVED_DYNSYM_LAYOUT_REQUIRED')
  strings=table[section[6]];words=b[strings[4]:strings[4]+strings[5]]
  for off in range(section[4],section[4]+section[5],24):
   index,info,other,ndx,value,size=struct.unpack_from('<IBBHQQ',b,off);end=words.find(b'\0',index)
   if end<0:raise ValueError('SAVED_DYNSYM_TERMINATOR_REQUIRED')
   name=words[index:end].decode('ascii')
   if name in out and ndx and info>>4 in(1,2)and(other&3)in(0,3):out[name].append(dict(value=value,size=size,binding=info>>4,type=info&15,visibility=other&3))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--protocol',required=True);ap.add_argument('--protocol-sha256',required=True);args=ap.parse_args();protocol=str(path(args.protocol).resolve().relative_to(ROOT))
 if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_POST_PRESERVED')
 en='results/p4_full/'+RUN+'/execution.json';e=load(en);p=load(protocol);claim=e['claim'];c=load(claim);internal='results/p4_full/'+RUN+'/cost_receipt.jsonl';ib=raw(internal);i=parse(ib);receipt=p['external_supervision']['charge_path'];r=load(receipt);st=load(STATIC)
 ck('freeze','exact committed frozen protocol SHA',sha(protocol)==args.protocol_sha256==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'])
 ck('freeze','all explicit reviews10/20 and unique setup',p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())and p['budget']==e['budget']==dict(wall_s=10.,cpu_s=20.,child_cpu_limit_s=20,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)and p['maxima']==dict(new_source_processes=1,source_requests=1,setup_calls=1,public_project_calls=13,solve_calls=0,seed=7))
 ck('freeze','exact successful independent static review',sha(STATIC)==STATIC_SHA and st['status']=='PASS_SBL_PCS_SETUP01_INDEPENDENT_STATIC_REVIEW'and st['personnel_independent']is True and st['independent_static_review_passed']is True and st['checks_total']==st['checks_passed']>0 and st['checks_failed']==0)
 ck('execution','actual setup status not scientific qualification',e['schema']=='P4_R2_ABB_SBL_PCS_SETUP01_EXECUTION_V3'and e['run_id']==RUN and e['classification']==p['classification']and e['status']==i['status']=='SOURCE_SETUP_PUBLIC13_OBSERVED_PENDING_INDEPENDENT_POST'and e['diagnostics']==[])
 ck('claim','exclusive no-retry exact claim',c['run_id']==RUN and c['source_commit']==e['source_commit']and c['protocol']==protocol and c['budget']==p['budget']and c['no_retry_reset_resume']is True and sha(claim)==e['claim_sha256']==e['claim_after_sha256'])
 ck('binding','full protocol/evidence maps same',all(e[k]==p[k]for k in('budget','bound_files_sha256','prior_execution_sha256','previous_r2_wall_s','previous_r2_cpu_s','actual_charge_prior','zero_calls','output_contract'))and e['bound_files_after_sha256']==p['bound_files_sha256'])
 for n,w in p['bound_files_sha256'].items():ck('bound','actual frozen bytes '+n,sha(n)==w)
 for n,w in p['own_source_sha256'].items():
  ck('source','actual committed source '+n,sha(n)==w and hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest()==w)
 ck('commit','actual committed protocol',hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+protocol],cwd=ROOT)).hexdigest()==args.protocol_sha256)
 for n,w in st['reviewed_source_sha256'].items():ck('static','actual reviewed source '+n,sha(n)==w==p['own_source_sha256'][n])
 build=p['build_assets'];bm=load(build['manifest']);bp=load(build['personnel_independent_POST']);be=load(build['execution'])
 ck('build','actual successful compiler-only ancestor exact bytes',sha(build['manifest'])==build['manifest_sha256']and sha(build['personnel_independent_POST'])==build['personnel_independent_POST_sha256']and sha(build['execution'])==build['execution_sha256']and bm['status']==be['status']=='BUILT_NOT_QUERIED'and bp['engineering_build_qualified']is bp['personnel_independent']is bp['external_supervision_qualified']is True and bp['checks_total']==bp['checks_passed']>0 and bp['checks_failed']==0 and bp['execution_sha256']==sha(build['execution']))
 ck('mesh','exact20 copied mesh maps unchanged',len(e['runtime_mesh_sha256'])==20 and e['runtime_mesh_sha256']==e['runtime_mesh_after_sha256'])
 expected_mesh={str((ROOT/'results/p4_full'/RUN/'work/simulator'/Path(n).name).relative_to(ROOT)):w for n,w in p['runtime_meshes_sha256'].items()}
 ck('mesh','exact original frozen source mesh bytes mapped',e['runtime_mesh_sha256']==expected_mesh)
 for n,w in e['runtime_mesh_sha256'].items():ck('mesh','actual retained runtime mesh '+n,sha(n)==w)
 folder=ROOT/'results/p4_full'/RUN;native=[x for b in(folder/'paths',folder/'work/paths')for x in b.rglob('*')if x.is_file()]
 ck('scope','native planning output absent actual directories retained',not native and e['original_native_output_sha256']=={}and e['original_native_output_fsync_completed']==[]and(folder/'paths').is_dir()and(folder/'work/paths').is_dir())
 journal=raw(e['evidence_journal']);ck('journal','actual complete journal digest',sha(e['evidence_journal'])==e['evidence_journal_sha256'])
 physical=journal.splitlines(keepends=True);blanks=[j for j,x in enumerate(physical)if x==b'\n'];events=[]
 for j,line in enumerate(physical):
  if line==b'\n':continue
  if not line.endswith(b'\n')or not line.strip():raise ValueError('UNEXPECTED_JOURNAL_NONEMPTY_OR_INCOMPLETE_BYTES')
  value=parse(line)
  if not isinstance(value,dict)or not isinstance(value.get('event'),str):raise ValueError('EXPLICIT_JOURNAL_EVENT_REQUIRED')
  events.append(value)
 ck('journal','one explicit retained blank line before three final events',len(blanks)==1 and blanks[0]==len(physical)-4)
 kinds=Counter(x['event']for x in events)
 def only(kind):
  found=[x for x in events if x['event']==kind]
  if len(found)!=1:raise ValueError('EXACT_ONE_SAVED_EVENT '+kind)
  return found[0]
 ck('journal','actual parsed journal setup record exact prefix',only('setup')['record']=={k:v for k,v in e.items()if k in only('setup')['record']})
 final=only('final_complete_raw_streams');finalcounts=only('final_counts')
 ck('journal','final actual counters and diagnostics',finalcounts['counts']==e['counts']and finalcounts['diagnostics']==[])
 streams={}
 for channel in('stdout','stderr'):
  data=raw(folder/('source_'+channel+'.bin'));streams[channel]=data;chunks=[base64.b64decode(x['base64'],validate=True)for x in events if x['event']=='raw_pipe_chunk'and x['channel']==channel]
  ck('raw','all actual chunks exact retained '+channel,b''.join(chunks)==data and all(len(base64.b64decode(x['base64'],validate=True))==x['bytes']for x in events if x['event']=='raw_pipe_chunk'and x['channel']==channel))
  saved=final['streams'][channel];ck('raw','actual final raw record '+channel,saved['bytes']==len(data)and saved['sha256']==hashlib.sha256(data).hexdigest()and base64.b64decode(saved['base64'],validate=True)==data)
 response_lines=streams['stdout'].splitlines(keepends=True);ck('raw','one unique complete JSONLF response',len(response_lines)==1 and response_lines[0].endswith(b'\n'))
 response=parse(response_lines[0]);ck('raw','returned response preserved before qualification',response==only('parsed_response_before_gates')['response']and base64.b64decode(only('raw_response_line')['base64'],validate=True)==response_lines[0])
 request=only('setup_request_exact_bytes');requestbytes=base64.b64decode(request['base64'],validate=True);write=only('single_request_write_and_stdin_close')
 ck('request','exact unique compactJSONLF bytes original request',requestbytes==json.dumps(p['request'],allow_nan=False,separators=(',',':')).encode()+b'\n'and request['request']==response['request']==p['request']and request['bytes']==len(requestbytes)and request['sha256']==hashlib.sha256(requestbytes).hexdigest())
 ck('request','only single full write then stdin close',kinds['single_request_write_and_stdin_close']==kinds['setup_request_exact_bytes']==1 and write['actual_sent']==len(requestbytes)and write['exact_full_request_written']is write['stdin_closed']is True and write['sent_sha256']==hashlib.sha256(requestbytes).hexdigest()and base64.b64decode(write['sent_bytes_base64'],validate=True)==requestbytes)
 ck('scope','actual once setup13 zero solve/formal/VI',e['setup_calls']==1 and e['public_project_calls']==13 and e['binary_execution_calls']==1 and e['solve_calls']==e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and e['independent_path_qualified']is False and all(v==0 for v in e['zero_calls'].values()))
 ck('response','source setup only original false fields retained',response['schema']=='P4_ABB_SBL_PCS_SETUP_TRANSPORT_DRAFT_V1'and response['status']=='SOURCE_SETUP_OBSERVED_NOT_RUNTIME_QUALIFIED'and response['operation']=='setup'and response['original_default_setup_order_preserved']is True and response['solve_calls']==response['formal_table_I_calls']==response['new_VI_candidate_constructions']==response['remaining_live_motions']==0 and response['independent_path_qualified']is False)
 expected={'mesh_load':1,'freeGridMotions':2};trace=response['trace'];rawtrace=[parse(x.split(b'P4_SBL_PCS_TRACE ',1)[1])for x in streams['stderr'].splitlines(keepends=True)if b'P4_SBL_PCS_TRACE 'in x]
 ck('trace','original six entry exit source traces exact raw',trace==rawtrace and len(trace)==6 and response['source_started']==response['source_completed']==e['actual_source_started']==e['actual_source_completed']==expected)
 enters={};leaves={}
 for x in trace:
  if x['kind']not in expected:raise ValueError('UNEXPECTED_SAVED_BODY_CALL')
  if x['event']=='entered':
   if x['id']in enters:raise ValueError('DUPLICATE_SAVED_TRACE_ID')
   enters[x['id']]=x['kind']
  elif x['event']=='completed':
   if x['id']in leaves or enters.get(x['id'])!=x['kind']:raise ValueError('SAVED_TRACE_UNMATCHED_COMPLETION')
   leaves[x['id']]=x['kind']
  else:raise ValueError('UNEXPECTED_SAVED_TRACE_EVENT')
 ck('trace','one mesh_load and two empty grid destruction complete',enters==leaves and Counter(enters.values())==Counter(expected))
 m=response['actual_setup_metadata'];dim=m['projection_dimension'];ck('metadata','actual exact type projection dimension and both empty grids',m==e['actual_setup_metadata']and m['projection_dynamic_type']in('N4ompl4base35RealVectorLinearProjectionEvaluatorE','N4ompl4base41RealVectorRandomLinearProjectionEvaluatorE')and type(dim)is int and 0<dim<=12 and m['native_grid_dimensions']==[dim,dim]and m['both_grid_dimensions_match_projection']is True and m['native_tree_sizes']==[0,0])
 ck('metadata','actual finite positive cells and bool configuration',finite(m['cell_sizes'],dim)and all(x>0 for x in m['cell_sizes'])and type(m['user_configured'])is bool and type(m['has_bounds'])is bool)
 ck('metadata','actual bound presence exact finite ordered',finite(m['bounds']['low'],dim)and finite(m['bounds']['high'],dim)and all(a<b for a,b in zip(m['bounds']['low'],m['bounds']['high']))if m['has_bounds']else m['bounds']is None)
 ck('metadata','actual original solveRange and auto setup range sampler null',m['original_solve_Range']==.8 and type(m['setup_getRange'])in(int,float)and math.isfinite(m['setup_getRange'])and m['setup_getRange']>0 and m['sampler']is None and m['sampler_allocated_by_observer']is False and m['original_solve_entry_available']is False)
 ck('metadata','scope public action only library internal RNG unobserved',m['public_project_observation_count']==13 and m['matrix_identity_label']=='OBSERVED_LINEAR_ACTION_MATRIX_NOT_PROTECTED_STORAGE_BYTES'and m['projection_observer_RNG_draws']==0 and m['actual_setup_library_RNG_draws']=='UNOBSERVED')
 points=m['fixed_zero_then_basis_observations'];columns=m['observed_linear_action_matrix_columns'];ck('public13','exact13 fixed points12 action columns',len(points)==13 and len(columns)==12)
 for j,point in enumerate(points):
  q=[1. if j>0 and j-1==k else 0. for k in range(12)];v=point['output'];ck('public13','all independent binary64 inputs outputs '+str(j),point['input_q12']==q and point['input_binary64']==hex64(q)and finite(v,dim)and point['output_binary64']==hex64(v))
  ck('public13','zero origin or exact action column '+str(j),all(x==0 for x in v)if j==0 else exact(v,columns[j-1]))
 scope=e['actual_loaded_project_symbol_scope'];scopeevent=only('actual_loaded_project_symbol_scope')['observation'];initial=only('actual_loaded_scope_raw_before_gates');candidates=only('actual_loaded_symbol_candidates_before_gates');maps=base64.b64decode(scope['maps_bytes_base64'],validate=True)
 ck('scope binding','same complete saved pre-request scope',scope==scopeevent and scope['scope']=='STATIC_AND_PRE_REQUEST_LOADED_SYMBOL_SCOPE_NOT_RUNTIME_GOT_ADDRESS_READ'and scope['protected_matrix_storage_read']is False and scope['LD_BIND_NOW']=='1'and hashlib.sha256(maps).hexdigest()==scope['maps_sha256']==initial['maps_sha256']and base64.b64decode(initial['maps_bytes_base64'],validate=True)==maps)
 env=scope['actual_environment'];envbytes=b''.join((k+'='+v).encode()+b'\0'for k,v in env.items());ck('scope binding','exact sanitized actual environment roundtrip bytes',env==initial['actual_environment']==p['source_environment']and hashlib.sha256(envbytes).hexdigest()==scope['environment_sha256']==initial['environment_sha256']and env['LD_BIND_NOW']=='1'and not any(x in env for x in('LD_PRELOAD','LD_AUDIT','LD_LIBRARY_PATH')))
 mapped=set()
 for line in maps.decode().splitlines():
  fields=line.split(maxsplit=5)
  if len(fields)==6 and fields[5].startswith('/'):
   if fields[5].endswith(' (deleted)'):raise ValueError('DELETED_SAVED_MAPPING')
   mapped.add(str(Path(fields[5]).resolve()))
 ck('scope binding','all mapped paths exactly retained hashes',mapped==set(scope['mapped_files_sha256'])and scope['mapped_files_sha256']==candidates['mapped_files_sha256']==e['mapped_files_after_sha256'])
 names=tuple(scope['project_symbol_providers']);providers={n:[]for n in names}
 for n,w in scope['mapped_files_sha256'].items():
  b=raw(n);ck('scope binding','actual mapped file unchanged '+n,hashlib.sha256(b).hexdigest()==w)
  if b[:4]!=b'\x7fELF':continue
  found=elf_exports(n,names)
  for name,rows in found.items():
   if rows:providers[name].append(dict(file=n,definitions=rows))
 ck('scope binding','independent saved ELF project provider inventory exact',providers==scope['project_symbol_providers']==candidates['project_symbol_providers']and len(names)==2)
 ompl='/opt/ros/humble/lib/x86_64-linux-gnu/libompl.so.1.7.0'
 ck('scope binding','only hashed OMPL exports both project functions',all(len(rows)==1 and rows[0]['file']==ompl and len(rows[0]['definitions'])==1 and rows[0]['definitions'][0]['type']==2 for rows in providers.values())and sha(ompl)=='25e9cbdc7c1c3b1e7c56221e954e72c4f5cb96e6c45253631773655cac71499e')
 ck('scope binding','actual source executable binary bytes',scope['actual_exe']==initial['actual_exe']==p['build_assets']['target']['binary']and scope['actual_exe_sha256']==sha(scope['actual_exe']))
 reg=e['source_process_registry'];life=e['source_lifecycle'];ck('lifecycle','one actual registered reaped source process',len(reg)==1 and reg[0]['reaped']is True and reg[0]['returncode']==0 and reg[0]['actual_after_reap_group']==[]and not members(reg[0]['pid'])and reg[0]['actual_start_ticks']==life['actual_start_ticks']>0)
 ck('lifecycle','both actual EOF stdin close empty final group',life['actual_pipe_EOF_observed']=={'stdout':True,'stderr':True}and life['actual_after_reap_group']==[]and life['stdin_closed_after_unique_request']is True and life['request_bytes']==life['actual_request_sent']==len(requestbytes)and life['request_sha256']==hashlib.sha256(requestbytes).hexdigest()and e['complete_source_raw_evidence_gate']is final['EOF']is True)
 ck('lifecycle','actual EOF events both channels',set(x['channel']for x in events if x['event']=='actual_pipe_EOF_observed')=={'stdout','stderr'})
 start=only('source_process_started');sg=only('source_start_group');close=only('source_close_group');after=only('source_after_reap_group');ck('lifecycle','all actual source identity and reap observations bound',start['pid']==reg[0]['pid']and start['start_ticks']==sg['actual_start_ticks']==close['start_ticks']==after['start_ticks']==reg[0]['actual_start_ticks']and [x['pid']for x in sg['members']]==[reg[0]['pid']]and after['members']==[]and after['returncode']==0 and after['actual_pipe_EOF_observed']==life['actual_pipe_EOF_observed'])
 preclose=[x['pid']for x in life['actual_preclose_group']];ck('lifecycle','actual original close branch coherent',close['members']==life['actual_preclose_group']and close['actual_poll_result']==life['actual_preclose_poll_result']and close['actual_poll_observations']==life['actual_preclose_poll_observations']and close['actual_postpoll_group']==life['actual_postpoll_group']and ((preclose==[reg[0]['pid']]and life['actual_preclose_poll_result']is None)or(preclose in([],[reg[0]['pid']])and life['actual_preclose_poll_result']==0 and life['actual_postpoll_group']==[])))
 counts=e['counts'];ck('counts','one source start write response actual counters',all(counts[k]==1 for k in('source_process_start_attempted','source_process_started','setup_dispatch_attempted','setup_dispatched','stdout_complete_lines_observed','raw_response_lines_observed'))and len(counts)==6)
 ext=p['external_supervision'];timefile=ext['sibling_path'];fields=raw(timefile).decode().strip().split()
 if len(fields)!=4:raise ValueError('EXACT_FOUR_EXTERNAL_TIME_FIELDS_REQUIRED')
 elapsed,user,system=(Decimal(x)for x in fields[:3]);exitcode=int(fields[3]);wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'))
 ck('external','full child actual timing finite caps10/20',all(x.is_finite()and x>=0 for x in(elapsed,user,system))and wall<=10 and cpu<=20 and wall+e['previous_r2_wall_s']<=3600 and cpu+e['previous_r2_cpu_s']<=7200)
 ck('external','actual charge upper match direct GNUtime',r['time_fields']==fields and r['wall_s']==wall and r['cpu_s']==cpu and r['timing_valid']is r['time_inode_unchanged']is r['wall_CPU_caps_pass']is r['completed_process_exit0']is True and r['time_returncode']==r['measured_child_exit']==exitcode==0 and r['started_attempt']is True and r['failure']is None)
 ck('external','execution receipt time hash chain exact',r['source_execution']==en and r['execution_sha256']==sha(en)==i['execution_sha256']and r['receipt']==internal and r['receipt_sha256']==sha(internal)and r['time_file']==timefile and r['time_sha256']==sha(timefile))
 ck('external','original external false untouched final cost covers persistence',e['external_supervision_qualified']is i['external_supervision_qualified']is r['external_supervision_qualified']is False and i['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and wall>=max(e['wall_s'],i['wall_s_through_execution_persistence'])and cpu>=max(e['cpu_s'],i['cpu_s_through_execution_persistence']))
 meta=raw(ext['metadata_path']);ml=meta.splitlines(keepends=True);me=[parse(x)for x in ml]
 ck('external','exact planned started reaped metadata',len(me)==3 and [x['event']for x in me]==['planned_launch','time_process_started','time_process_reaped'])
 planned,started,reaped=me;proof=e['supervisor_launch_proof'];stat=path(timefile).stat();argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/'scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py'),'--protocol',str(path(protocol))]
 ck('external','actual metadata source protocol pid argv chain',planned['run_id']==RUN and planned['protocol']==protocol and planned['protocol_sha256']==args.protocol_sha256 and planned['argv']==started['argv']==proof['actual_argv']==argv and started['pid']==reaped['pid']==r['time_process_pid']==proof['actual_time_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid'])
 ck('external','actual held FD inode starttick proof',planned['time_inode']==proof['time_inode']==stat.st_ino and planned['time_device']==proof['time_device']==stat.st_dev and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and proof['planned_launch_line_sha256']==hashlib.sha256(ml[0]).hexdigest())
 ck('external','actual supervisor runner and tool hashes',planned['supervisor_source_sha256']==sha('scripts/supervise_p4_full_r2_abb_sbl_pcs_setup_draft.py')and planned['runner_sha256']==sha('scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py')and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
 ck('external','actual external logs receipt links',r['metadata']==ext['metadata_path']and r['metadata_sha256']==sha(ext['metadata_path'])and r['stderr']==ext['stderr_path']and r['stderr_sha256']==sha(ext['stderr_path']))
 prior=load(p['actual_charge_prior']['ledger']);actual={str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent.name!=RUN}
 ck('prior','actual old execution identities unchanged',actual==e['prior_execution_after_sha256']==e['prior_execution_sha256']=={x['execution']:x['execution_sha256']for x in prior['executions']}and sha(p['actual_charge_prior']['ledger'])==p['actual_charge_prior']['ledger_sha256'])
 ck('prior','actual prior effective charged sums unchanged',math.fsum(x.get('charged_wall_s',x['wall_s'])for x in prior['executions'])==e['previous_r2_wall_s']==p['actual_charge_prior']['wall_s']and math.fsum(x.get('charged_cpu_s',x['cpu_s'])for x in prior['executions'])==e['previous_r2_cpu_s']==p['actual_charge_prior']['cpu_s'])
 ck('scope','VI exhausted formal22500 all obligations retained',prior['vi_B_candidate_cap']==974 and prior['vi_B_remaining']['candidate_constructions']==0 and prior['formal_table_I_calls']==0 and prior['formal_table_I_required_calls']==22500)
 for n,w in list(retained.items()):ck('unchanged','all read saved bytes retained '+n,hashlib.sha256(Path(n).read_bytes()).hexdigest()==w)
 fail=[x for x in checks if not x['passed']]
 report=dict(schema='P4_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST_V1',status='PASS_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST'if not fail else'FAIL_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of SBL setup runner supervisor PRE',personnel_independent=True,setup_qualified=not fail,external_supervision_qualified=not fail,external_timing_qualified=not fail,external_cost_qualified=not fail,independent_path_qualified=False,checks=checks,checks_total=len(checks),checks_passed=len(checks)-len(fail),checks_failed=len(fail),failures=fail,source_commit=e['source_commit'],execution=en,execution_sha256=sha(en),protocol=protocol,protocol_sha256=sha(protocol),claim=claim,claim_sha256=sha(claim),receipt=receipt,receipt_sha256=sha(receipt),internal_receipt=internal,internal_receipt_sha256=sha(internal),external_time=timefile,external_time_sha256=sha(timefile),external_time_fields=fields,upper_wall_s=wall,upper_cpu_s=cpu,cumulative_charged_wall_s=e['previous_r2_wall_s']+wall,cumulative_charged_cpu_s=e['previous_r2_cpu_s']+cpu,retained_sha256=retained,setup_calls=1,public_project_calls=13,solve_calls=0,source_processes=1,projection_dimension=dim,actual_setup_metadata=m,journal_blank_physical_line_count=len(blanks),journal_blank_physical_line_indices=blanks,original_external_false_retained=True,new_runner_import_compile_binary_setup_model_query_solve_protocol_claim_prior_VI_formal_calls=0,limits=['Saved-only independent evidence check; no new setup, public project, model, compile or solve. Prior source setup happened once and is charged once.','Projection certificate covers13 public zero/basis action outputs and metadata, not protected matrix storage or robot/path qualification. Library setup RNG remains UNOBSERVED.','Loaded ELF export scope and sanitized environment are pre-request evidence, not direct GOT address reads or complete generic DSO implementation proof.','Full-child GNUtime includes preflight and final durable evidence; preflight had no installed hard timer. Supervisor own persistence excluded. Historical unmeasured tails UNKNOWN.','Historical connect a_chain original save risk persists. VI974/974 remaining0,formal0/22500,all211 obligations; no P2/Isaac.'])
 with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,allow_nan=False,indent=2);f.write('\n')
 with OUT.with_suffix('.md').open('x')as f:f.write('# SBL_PCS SETUP01 保存证据独立后审\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(len(checks))+'，失败'+str(len(fail))+'。\n\n实际1source/1write/双EOF与回收、原mesh_load1/freeGrid2共6trace、公有13点及binary64、动态类型/两grid/自动range/sampler null、请求前loaded scope独立ELF、20mesh前后、完整raw/journal及恰一空白行、费用链全部核验。没有新增setup/model/solve。\n\n外费上界'+str(wall)+'wall/'+str(cpu)+'CPU，累计'+str(report['cumulative_charged_wall_s'])+'/'+str(report['cumulative_charged_cpu_s'])+'。仅公有作用与setup接口资格，原external false和connect风险保留；VI余0、formal0/22500、211义务不变。\n')
 print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(fail),failures=fail,upper_wall_s=wall,upper_cpu_s=cpu),ensure_ascii=False))
 if fail:raise SystemExit(2)
if __name__=='__main__':main()
