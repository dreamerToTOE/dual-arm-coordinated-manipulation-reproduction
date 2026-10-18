#!/usr/bin/env python3
"""Saved-only SOLVE01 transport/lifetime/output POST; no implementation import."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import argparse,base64,datetime,hashlib,json,math,struct,subprocess
ROOT=Path(__file__).resolve().parents[3]
RUN='20261017_R2_ABB_SBL_PCS_SOLVE01'
STATIC='reports/P4_FULL_R2_ABB_SBL_PCS_SINGLE_SOLVE_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_20261017.json'
STATIC_SHA='1b09e0476a6ef26d10beb7026809a14747fba81de849c3ae17544dd708ba8dcc'
LOCALPOST='reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST_20261017.json'
SETUPPOST='reports/P4_FULL_R2_ABB_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST_20261017.json'
RUNNER='scripts/qualify_p4_full_r2_abb_sbl_pcs_solve_shadow_v2_draft.py'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_sbl_pcs_solve_shadow_v2_draft.py'
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST_20261017.json'
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
def hex64(q):return ''.join(struct.pack('>d',float(x)).hex()for x in q)
def one(events,kind):
 rows=[x for x in events if x['event']==kind]
 if len(rows)!=1:raise ValueError('EXACT_ONE_SAVED_EVENT '+kind+' '+str(len(rows)))
 return rows[0]
def members(pgid):
 rows=[]
 for p in Path('/proc').glob('[0-9]*/stat'):
  try:
   row=p.read_text().rsplit(')',1)[1].split()
   if int(row[2])==pgid:rows.append(int(p.parent.name))
  except(OSError,ValueError,IndexError):pass
 return sorted(rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--protocol',required=True);ap.add_argument('--protocol-sha256',required=True);args=ap.parse_args();protocol=str(path(args.protocol).resolve().relative_to(ROOT))
 if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_POST_PRESERVED')
 folder=ROOT/'results/p4_full'/RUN;en=str((folder/'execution.json').relative_to(ROOT));e=load(en);p=load(protocol);claim=e['claim'];c=load(claim);internal=str((folder/'cost_receipt.jsonl').relative_to(ROOT));i=load(internal);ext=p['external_supervision'];receipt=ext['charge_path'];charge=load(receipt);st=load(STATIC)
 ck('freeze','exact actual committed protocol SHA',sha(protocol)==args.protocol_sha256==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'])
 ck('freeze','all frozen explicit reviews one native10 solve20/40',p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())and p['budget']==e['budget']==dict(wall_s=20.,cpu_s=40.,child_cpu_limit_s=20,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)and p['maxima']==dict(new_source_processes=1,source_requests=1,setup_calls=1,local_calls=0,public_project_calls=0,solve_calls=1,connect_fixture_calls=0,original_solve_seconds=10.))
 ck('static','exact41 independent incremental static certificate',sha(STATIC)==STATIC_SHA and st['personnel_independent']is st['independent_static_review_passed']is True and st['checks_total']==st['checks_passed']==41 and st['checks_failed']==0)
 ck('execution','actual completed transport pending physical path',e['schema']=='P4_R2_ABB_SBL_PCS_SOLVE01_EXECUTION_V1'and e['run_id']==RUN and e['classification']==p['classification']and e['status']==i['status']=='SOURCE_SINGLE_SOLVE_OBSERVED_PENDING_INDEPENDENT_POST'and e['diagnostics']==[]and e['independent_path_qualified']is e['continuous_collision_certificate']is False)
 ck('claim','exact exclusive no-retry claim',c['run_id']==RUN and c['source_commit']==e['source_commit']and c['protocol']==protocol and c['budget']==p['budget']and c['no_retry_reset_resume']is True and sha(claim)==e['claim_sha256']==e['claim_after_sha256'])
 ck('binding','all recorded frozen maps and prior identical',all(e[k]==p[k]for k in('budget','bound_files_sha256','prior_execution_sha256','previous_r2_wall_s','previous_r2_cpu_s','actual_charge_prior','zero_calls'))and e['bound_files_after_sha256']==p['bound_files_sha256'])
 ck('binding','every actual bound current asset exact '+str(len(p['bound_files_sha256'])),all(sha(n)==w for n,w in p['bound_files_sha256'].items()))
 for n,w in p['own_source_sha256'].items():ck('source','actual committed exact source '+n,sha(n)==w and hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest()==w)
 ck('source','actual committed exact protocol/static',all(hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest()==sha(n)for n in(protocol,STATIC)))
 ck('source','actual solve source same independent static review',all(sha(n)==w==p['own_source_sha256'][n]for n,w in st['reviewed_source_sha256'].items()))
 lp=load(LOCALPOST);prior=load(p['actual_charge_prior']['ledger']);ck('local','actual local independent129 and charged prerequisite',p['local_independent_POST']==LOCALPOST and lp['personnel_independent']is lp['independent_local_qualified']is lp['external_supervision_qualified']is True and lp['checks_total']==lp['checks_passed']==129 and lp['checks_failed']==0 and any(x['execution']==lp['execution']and x['execution_sha256']==lp['execution_sha256']and x['charged_wall_s']==lp['upper_wall_s']and x['charged_cpu_s']==lp['upper_cpu_s']for x in prior['executions']))
 build=p['build_assets'];bp=load(build['personnel_independent_POST']);be=load(build['execution']);ck('build','same actual compiler-only independently qualified BUILD02',sha(build['execution'])==build['execution_sha256']==bp['execution_sha256']and sha(build['manifest'])==build['manifest_sha256']and sha(build['personnel_independent_POST'])==build['personnel_independent_POST_sha256']and be['status']=='BUILT_NOT_QUERIED'and be['run_id']=='20261017_R2_ABB_SBL_PCS_BUILD02'and bp['personnel_independent']is bp['engineering_build_qualified']is bp['external_supervision_qualified']is True and bp['checks_failed']==0)
 ck('scope','one actual setup solve zero local13 formal VI',e['binary_execution_calls']==e['setup_calls']==e['solve_calls']==1 and e['local_calls']==e['public_project_calls']==e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and all(x==0 for x in e['zero_calls'].values())and len(p['schedule'])==1 and p['schedule'][0]['mode']=='trace')
 journalpath=folder/'evidence.jsonl';jb=raw(journalpath);jl=jb.splitlines(keepends=True);ck('journal','complete nonempty JSONLF exact digest',all(x.endswith(b'\n')and x.strip()for x in jl)and sha(journalpath)==e['evidence_journal_sha256']);events=[parse(x)for x in jl];kinds=Counter(x['event']for x in events);prefix=one(events,'single_solve_setup')['record'];mutable={'status','setup_calls','solve_calls','binary_execution_calls'}
 ck('journal','initial STOP prefix immutable evidence preserved',prefix['status']=='STOP_PREFIX_RETAINED'and prefix['setup_calls']is prefix['solve_calls']is None and prefix['binary_execution_calls']==0 and all(e[k]==v for k,v in prefix.items()if k not in mutable))
 ck('journal','exact final counts diagnostics',one(events,'final_counts')['counts']==e['counts']and one(events,'final_counts')['diagnostics']==[])
 streams={}
 for channel in('stdout','stderr'):
  data=raw(folder/f'request_00_{channel}.bin');streams[channel]=data;chunks=[base64.b64decode(x['base64'],validate=True)for x in events if x['event']=='raw_pipe_chunk'and x['channel']==channel];final=[x for x in events if x['event']=='final_raw_stream'and x['channel']==channel]
  ck('raw','exact complete chunk/final stream '+channel,len(final)==1 and final[0]['schedule_index']==0 and b''.join(chunks)==data and all(len(base64.b64decode(x['base64'],validate=True))==x['bytes']for x in events if x['event']=='raw_pipe_chunk'and x['channel']==channel)and final[0]['bytes']==len(data)and final[0]['sha256']==hashlib.sha256(data).hexdigest()and base64.b64decode(final[0]['base64'],validate=True)==data)
 ck('raw','one exact JSONLF response',streams['stdout'].endswith(b'\n')and len(streams['stdout'].splitlines())==1 and len(e['responses'])==1)
 response=parse(streams['stdout']);ck('raw','exact response saved before gates',response==e['responses'][0]==one(events,'parsed_response_before_gates')['response']and base64.b64decode(one(events,'raw_response_line')['base64'],validate=True)==streams['stdout'])
 request=p['schedule'][0]['request'];req=one(events,'setup_request_exact_bytes');rb=base64.b64decode(req['base64'],validate=True);write=one(events,'single_request_write_and_stdin_close');work=folder/'request_00_single_solve_trace/work'
 ck('request','exact original II A01 seed7 point8 native10 trace',request['operation']=='solve'and request['environment']=='II'and request['seed']==7 and request['range_rad']==.8 and request['solve_seconds']==10. and request['separately_frozen_runtime_qualification']is True and response['request']==req['request']==request)
 ck('request','unique exact atomic write followed EOF',rb==json.dumps(request,allow_nan=False,separators=(',',':')).encode()+b'\n'and len(rb)<4096 and req['bytes']==len(rb)and req['sha256']==hashlib.sha256(rb).hexdigest()and write['actual_sent']==len(rb)and write['exact_full_request_written']is write['stdin_closed']is True and write['sent_sha256']==hashlib.sha256(rb).hexdigest()and base64.b64decode(write['sent_bytes_base64'],validate=True)==rb)
 ck('response','native result exact/nonexact remains pending independent path',response['schema']=='P4_ABB_SBL_PCS_SHADOW_V2_RUNTIME_DRAFT'and response['status']in('SOURCE_EXACT_PENDING_INDEPENDENT_PATH_QUALIFICATION','SOURCE_NONEXACT_RETAINED')and response['operation']=='solve'and response['mode']=='trace'and response['setup_dispatches']==response['solve_calls']==response['source_dispatch_started']==response['source_dispatch_completed']==1 and response['public_project_observations']==response['formal_table_I_calls']==response['new_VI_candidate_constructions']==response['remaining_live_motions']==0 and response['independent_path_qualified']is response['continuous_collision_certificate']is False)
 ck('response','exact boolean solution metadata internal consistency',type(response['exact'])is bool and type(response['solution_count'])is int and response['solution_count']>=0 and response['status']==('SOURCE_EXACT_PENDING_INDEPENDENT_PATH_QUALIFICATION'if response['exact']else'SOURCE_NONEXACT_RETAINED')and (not response['exact']or response['solution_count']>=1))
 ck('path','milestones finite and exact endpoint identity only',all(len(q)==12 and all(type(x)in(int,float)and math.isfinite(x)for x in q)for q in response['milestones_q12'])and (not response['exact']or len(response['milestones_q12'])>=2 and hex64(response['milestones_q12'][0])==hex64(request['start_q12'])and hex64(response['milestones_q12'][-1])==hex64(request['goal_q12'])))
 trace=response['trace'];rawtrace=[parse(line.split(b'P4_SBL_PCS_TRACE ',1)[1])for line in streams['stderr'].splitlines()if b'P4_SBL_PCS_TRACE 'in line];entered={};completed={};live={};registered={};prepared={};retired={};marks=[];live_before_destructor=None;call_return_hist={}
 for event in trace:
  if event['event']=='entered':
   if event['id']in entered:raise ValueError('DUPLICATE_SOURCE_ENTRY')
   entered[event['id']]=event['kind']
   if event['kind']=='freeGridMotions'and live_before_destructor is None:live_before_destructor=set(live)
  elif event['event']=='completed':
   if event['id']in completed:raise ValueError('DUPLICATE_SOURCE_COMPLETION')
   completed[event['id']]=event['kind'];result=event.get('result',{})
   if 'returned'in result:call_return_hist.setdefault(event['kind'],Counter())[json.dumps(result['returned'])]+=1
  elif event['event']=='observed':
   marks.append(event);kind=event['kind'];a=event['args']
   if kind=='motion_lifetime_registered':
    ident=a['motion_id']
    if ident in registered or ident in live:raise ValueError('DUPLICATE_MOTION_LIFETIME')
    ck('lifetime','registered unique finite q/role ancestry '+str(ident),len(a['q12'])==12 and all(math.isfinite(x)for x in a['q12'])and a['address_generation']>0 and a['state_id']>0 and a['tree']in('start','goal')and (a['parent_motion_id']==0 or a['parent_motion_id']in live)and (a['root_motion_id']==ident or a['root_motion_id']in live)and ((a['a_chain']in(0,1)and a['a_chain_provenance']in('ROOT_ASSIGNED','GROW_ASSIGNED'))or(a['a_chain']is None and a['a_chain_provenance']=='UNINITIALIZED_NOT_READ')))
    registered[ident]=a;live[ident]=a
   elif kind=='motion_before_native_retirement':
    ident=a['motion_id']
    if ident not in live or ident in prepared:raise ValueError('INVALID_RETIREMENT_TOKEN')
    prepared[ident]=a
   elif kind=='motion_lifetime_retired':
    ident=a['motion_id']
    if ident not in live or ident in retired or prepared.get(ident)!=a:raise ValueError('RETIRE_WITHOUT_EXACT_PREDELETE_TOKEN')
    retired[ident]=a;del live[ident]
  else:raise ValueError('UNKNOWN_SOURCE_EVENT')
 calls=dict(Counter(entered.values()));trees=response['trees_before_destruction'];nodes=trees['nodes'];byid={x['motion_id']:x for x in nodes}
 ck('trace','complete exact raw balanced original calls',trace==rawtrace and response['source_counts_observed']is True and entered==completed and calls==response['source_started']==response['source_completed']and calls.get('mesh_load')==1 and calls.get('freeGridMotions')==2)
 ck('lifetime','all registered retired once final live0',not live and set(registered)==set(prepared)==set(retired)and len(set(x['state_id']for x in registered.values()))==len(registered))
 ck('lifetime','final native trees exact live set before original destructor',live_before_destructor==set(byid)and len(byid)==len(nodes)==sum(trees['native_tree_sizes'])and trees['identity_policy']=='LIVE_MOTION_LIFETIME_GENERATION_NO_Q_MERGE')
 ck('lifetime','all final tree identities bound to real source lifetimes',all(n['motion_id']in registered and all(n[k]==registered[n['motion_id']][k]for k in('q12','state_id','address_generation','a_chain','a_chain_provenance','ik_q1_active','ik_q2_active','root_motion_id','tree'))for n in nodes))
 attempts=response['writer_metadata_attempts'];attemptmarks=[x['args']for x in marks if x['kind']=='ik_path_metadata_attempt'];ck('writer','all metadata attempts actual trace exact',attempts==attemptmarks and all(x['attempt_row_1based']==j+1 for j,x in enumerate(attempts)))
 native=response['native_file_evidence'];ck('files','capture complete expected5 files no hidden persistence errors',len(native)>=5 and response['native_output_capture_complete']is response['shadow_sidecar_saved_and_readback_equal']is response['transport_evidence_saved_and_readback_equal']is True and all('error'not in row for row in native))
 for row in native:
  if row['exists']:
   content=raw(row['saved_path']);ck('files','actual final byte readback '+row['name'],row['readback_bytes_saved']is row['original_final_bytes_readable']is True and row['bytes']==len(content)and row['bytes_hex']==content.hex()and raw(row['original_path'])==content and row['original_stream_open_write_flush_flags']=='UNOBSERVED')
  else:ck('files','actual absence retained '+row['name'],row['absence_retained']is True and not path(row['original_path']).exists())
 sidecar=load(response['shadow_sidecar_path']);prefixio=load(work/'writer_evidence/transport_prefix_and_io_evidence.json');ck('sidecar','actual durable transport exact prefix',all(response[k]==v for k,v in prefixio.items())and 'transport_evidence_saved_and_readback_equal'not in prefixio)
 ck('sidecar','versioned original writer UNKNOWN exact attempts evidence',sidecar['schema']=='P4_R2_ABB_SBL_PCS_IK_PATH_SHADOW_PERSISTED_V2'and sidecar['classification']=='RECONSTRUCTED_OUTPUT_METADATA_ONLY'and sidecar['attempts']==attempts and sidecar['attempt_count']==len(attempts)and sidecar['native_file_evidence']==native and sidecar['original_fstream_open_write_flush_flags']=='UNOBSERVED')
 unknown_attempts=[x for x in attempts if x['a_chain']is None];writer_qualified=False
 if attempts:
  actual_rows=raw(work.parent/'paths/ik_path.txt').decode().splitlines();parsedrows=[tuple(int(x)for x in line.split())for line in actual_rows];rowchecks=[];prior_side=1;prior_source=-1
  for index,(attempt,columns)in enumerate(zip(attempts,parsedrows)):
   n=byid.get(attempt['motion_id']);side=attempt['source_side'];source=attempt['source_index_0based'];rowchecks.append(n is not None and len(columns)==3 and columns==(attempt['text_first_column'],n['ik_q1_active'],n['ik_q2_active'])and attempt['a_chain']==n['a_chain']and attempt['state_id']==n['state_id']and attempt['address_generation']==n['address_generation']and attempt['text_write_success_observed']is None and ((attempt['a_chain']is None and attempt['text_first_column']==-1 and attempt['motion_origin']=='CHECKSOLUTION_CONNECT'and attempt['a_chain_provenance']=='UNINITIALIZED_NOT_READ')or(attempt['a_chain']in(0,1)and attempt['text_first_column']==attempt['a_chain']and attempt['motion_origin']in('ROOT_ASSIGNED','GROW_ASSIGNED'))))
   rowchecks.append(side in(1,2)and side>=prior_side and (not index or side!=prior_side or source==prior_source+(-1 if side==1 else 1))and (side!=2 or prior_side==2 or source==0 and(not index or prior_source==0)));prior_side=side;prior_source=source
  writer_qualified=len(actual_rows)==len(attempts)and all(rowchecks)and sidecar['final_text_readback_matches_attempts']is True
  ck('writer','independent final3integer rows exact lifetime branches side order unknown sentinel',writer_qualified and response['shadow_final_text_readback_matches_attempts']is True and all(row['actual_three_columns']==list(parsedrows[j])and row['matches']is True and row['line_1based']==j+1 for j,row in enumerate(sidecar['final_rows'])))
 else:ck('writer','noattempt is observed gap not write success',sidecar['no_writer_attempts_observed']is sidecar['empty_attempts_do_not_prove_write_success']is True and sidecar['final_text_readback_matches_attempts']is False)
 reg=e['source_process_registry'];ck('lifecycle','one registered process complete source evidence',len(reg)==1 and e['complete_source_raw_evidence_gate']is True);proc=reg[0];start=one(events,'source_process_started');sg=one(events,'source_start_group');close=one(events,'source_close_group');after=one(events,'source_after_reap_group')
 ck('lifecycle','actual original single solve command registered reaped exit0',start['command']==[build['target']['binary'],'II',str(work),'solve','trace']and start['pid']==proc['pid']and start['start_ticks']==sg['actual_start_ticks']==close['start_ticks']==after['start_ticks']==proc['start_ticks']>0 and [x['pid']for x in sg['members']]==[proc['pid']]and proc['returncode']==after['returncode']==0 and proc['actual_after_reap_group']==after['members']==[]and not members(proc['pid']))
 ck('lifecycle','both actual EOF unique stdin close request bytes',proc['actual_pipe_EOF_observed']==after['actual_pipe_EOF_observed']=={'stdout':True,'stderr':True}and {x['channel']for x in events if x['event']=='actual_pipe_EOF_observed'}=={'stdout','stderr'}and proc['stdin_closed_after_unique_request']is True and proc['request_bytes']==proc['actual_request_sent']==len(rb)and proc['request_sha256']==hashlib.sha256(rb).hexdigest())
 preclose=[x['pid']for x in proc['close_group']];ck('lifecycle','actual close branch original evidence coherent',proc['close_group']==close['members']and proc['close_poll_result']==close['actual_poll_result']and proc['close_poll_observations']==close['actual_poll_observations']and proc['close_postpoll_group']==close['actual_postpoll_group']and ((preclose==[proc['pid']]and proc['close_poll_result']is None)or(preclose in([],[proc['pid']])and proc['close_poll_result']==0 and proc['close_postpoll_group']==[])))
 oldpost=load(SETUPPOST);olde=load(oldpost['execution']);oldscope=olde['actual_loaded_project_symbol_scope'];scope=proc['loaded_scope'];scopeevent=one(events,'actual_loaded_project_symbol_scope')['observation'];initial=one(events,'actual_loaded_scope_raw_before_gates');candidates=one(events,'actual_loaded_symbol_candidates_before_gates');maps=base64.b64decode(scope['maps_bytes_base64'],validate=True);mapped=set()
 for line in maps.decode().splitlines():
  fields=line.split(maxsplit=5)
  if len(fields)==6 and fields[5].startswith('/'):
   if fields[5].endswith(' (deleted)'):raise ValueError('DELETED_LOADED_MAPPING')
   mapped.add(str(Path(fields[5]).resolve()))
 ck('loaded','actual exact pre-request maps environment providers unchanged',scope==scopeevent and scope['actual_environment']==p['source_environment']==initial['actual_environment']and scope['actual_exe']==build['target']['binary']and scope['actual_exe_sha256']==sha(scope['actual_exe'])and hashlib.sha256(maps).hexdigest()==scope['maps_sha256']==initial['maps_sha256']and base64.b64decode(initial['maps_bytes_base64'],validate=True)==maps and mapped==set(scope['mapped_files_sha256'])and scope['mapped_files_sha256']==candidates['mapped_files_sha256']and all(sha(n)==w for n,w in scope['mapped_files_sha256'].items())and scope['project_symbol_providers']==oldscope['project_symbol_providers']==candidates['project_symbol_providers']and all(oldscope['mapped_files_sha256'].get(n)==w for n,w in scope['mapped_files_sha256'].items()if n!=scope['actual_exe']))
 m=response['setup_metadata'];om=olde['actual_setup_metadata'];ck('setup','same qualified native setup metadata no repeated13',all(m[k]==om[k]for k in('projection_dimension','projection_dynamic_type','native_grid_dimensions','cell_sizes','user_configured','original_solve_Range','setup_getRange'))and m['additional_public_project_observations']==m['observer_rng_draws']==0 and m['setup_internal_rng_draws']=='UNOBSERVED')
 expected_mesh={str((work/'simulator'/Path(n).name).relative_to(ROOT)):w for n,w in p['runtime_meshes_sha256'].items()};ck('mesh','exact20 actual source mesh copies unchanged',len(expected_mesh)==20 and e['runtime_mesh_sha256']==e['runtime_mesh_after_sha256']==expected_mesh and all(sha(n)==w for n,w in expected_mesh.items()))
 ck('counts','one start write response exact6 counts',len(e['counts'])==6 and all(e['counts'][n]==1 for n in('source_process_start_attempted','source_process_started','setup_dispatch_attempted','setup_dispatched','stdout_complete_lines_observed','raw_response_lines_observed')))
 ck('retention','all actual saved run files exact',all(sha(n)==w for n,w in e['retained_run_files_sha256'].items()))
 fields=raw(ext['sibling_path']).decode().strip().split()
 if len(fields)!=4:raise ValueError('EXACT_FOUR_GNU_TIME_FIELDS')
 elapsed,user,system=(Decimal(x)for x in fields[:3]);exitcode=int(fields[3]);wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'))
 ck('external','complete child GNUtime upper20/40 total3600/7200',all(x.is_finite()and x>=0 for x in(elapsed,user,system))and wall<=20 and cpu<=40 and wall+e['previous_r2_wall_s']<=3600 and cpu+e['previous_r2_cpu_s']<=7200)
 ck('external','actual exact charge timing4 fields process0',charge['time_fields']==fields and charge['wall_s']==wall and charge['cpu_s']==cpu and charge['timing_valid']is charge['time_inode_unchanged']is charge['wall_CPU_caps_pass']is charge['completed_process_exit0']is charge['started_attempt']is True and charge['time_returncode']==charge['measured_child_exit']==exitcode==0 and charge['failure']is None)
 ck('external','execution receipt full persistence hash chain',charge['source_execution']==en and charge['execution_sha256']==sha(en)==i['execution_sha256']and charge['receipt']==internal and charge['receipt_sha256']==sha(internal)and charge['time_file']==ext['sibling_path']and charge['time_sha256']==sha(ext['sibling_path'])and e['external_supervision_qualified']is i['external_supervision_qualified']is charge['external_supervision_qualified']is False and i['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and wall>=max(e['wall_s'],i['wall_s_through_execution_persistence'])and cpu>=max(e['cpu_s'],i['cpu_s_through_execution_persistence']))
 ml=raw(ext['metadata_path']).splitlines(keepends=True);me=[parse(x)for x in ml];ck('external','actual planned started reaped metadata3',len(me)==3 and [x['event']for x in me]==['planned_launch','time_process_started','time_process_reaped']);planned,started,reaped=me;proof=e['supervisor_launch_proof'];stat=path(ext['sibling_path']).stat();argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/RUNNER),'--protocol',str(path(protocol))]
 ck('external','actual source protocol argv parent pid and inode FD chain',planned['run_id']==RUN and planned['protocol']==protocol and planned['protocol_sha256']==args.protocol_sha256 and planned['argv']==started['argv']==proof['actual_argv']==argv and started['pid']==reaped['pid']==charge['time_process_pid']==proof['actual_time_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid']and planned['time_inode']==proof['time_inode']==stat.st_ino and planned['time_device']==proof['time_device']==stat.st_dev and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and proof['planned_launch_line_sha256']==hashlib.sha256(ml[0]).hexdigest())
 ck('external','actual source tool and durable logs exact SHA',planned['supervisor_source_sha256']==sha(SUPERVISOR)and planned['runner_sha256']==sha(RUNNER)and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3')and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr_sha256']==sha(ext['stderr_path']))
 actual={str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent.name!=RUN};ck('prior','all prior actual execution SHAs and charged sum unchanged',actual==e['prior_execution_after_sha256']==e['prior_execution_sha256']=={x['execution']:x['execution_sha256']for x in prior['executions']}and sha(p['actual_charge_prior']['ledger'])==p['actual_charge_prior']['ledger_sha256']and math.fsum(x.get('charged_wall_s',x['wall_s'])for x in prior['executions'])==e['previous_r2_wall_s']==p['actual_charge_prior']['wall_s']and math.fsum(x.get('charged_cpu_s',x['cpu_s'])for x in prior['executions'])==e['previous_r2_cpu_s']==p['actual_charge_prior']['cpu_s'])
 ck('scope','VI archival974 exhausted formal0 historical22500',prior['vi_B_candidate_cap']==974 and prior['vi_B_remaining']['candidate_constructions']==0 and prior['formal_table_I_calls']==0 and prior['formal_table_I_required_calls']==22500)
 ck('unchanged','every read saved asset still exact',all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==w for n,w in retained.items()))
 fail=[x for x in checks if not x['passed']];summary=dict(native_exact=response['exact'],planner_status=response['planner_status'],solution_count=response['solution_count'],milestone_count=len(response['milestones_q12']),source_started=calls,return_histograms={k:dict(v)for k,v in call_return_hist.items()},registered_motion_lifetimes=len(registered),uninitialized_connect_lifetimes=sum(x['a_chain']is None for x in registered.values()),writer_attempts=len(attempts),writer_unknown_connect_attempts=len(unknown_attempts),writer_final_bytes_qualified=writer_qualified,native_file_count=len(native))
 report=dict(schema='P4_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST_V1',status='PASS_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST'if not fail else'FAIL_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review independent saved-only transport/lifetime/output review',personnel_independent=True,solve_transport_qualified=not fail,external_supervision_qualified=not fail,external_timing_qualified=not fail,external_cost_qualified=not fail,independent_path_qualified=False,continuous_collision_certificate=False,native_writer_final_bytes_qualified=not fail and writer_qualified,checks_total=len(checks),checks_passed=len(checks)-len(fail),checks_failed=len(fail),failures=fail,checks=checks,source_commit=e['source_commit'],execution=en,execution_sha256=sha(en),protocol=protocol,protocol_sha256=sha(protocol),claim=claim,claim_sha256=sha(claim),receipt=receipt,receipt_sha256=sha(receipt),internal_receipt=internal,internal_receipt_sha256=sha(internal),external_time=ext['sibling_path'],external_time_sha256=sha(ext['sibling_path']),external_time_fields=fields,upper_wall_s=wall,upper_cpu_s=cpu,cumulative_charged_wall_s=e['previous_r2_wall_s']+wall,cumulative_charged_cpu_s=e['previous_r2_cpu_s']+cpu,retained_sha256=retained,observations=summary,new_import_model_compile_binary_solve_VI_formal_calls=0,limits=['Only saved transport/lifetime/output evidence. Source exact result, RBS and reconstruction return values are not independent full physical path qualification.','Full milestone/intermediate chain closure/Jacobian/branch/limits/collision and independent path reconstruction remain pending a separately frozen qualification. Continuous collision and formal statistics remain unproved.','Unknown checkSolution connect role remains JSON null/text-1 RECONSTRUCTED_OUTPUT_METADATA_ONLY. Native final byte certificate never proves original fstream internal flags.','All source successes/failures, early/false reconstruction and raw evidence retained; no new solve, model, sampling or retry.','GNUtime measures complete runner child, excluding supervisor own persistence; historical unmeasured tails remain UNKNOWN. D080 formal18000 budget unapproved; VI974/974 archival only, no P2/Isaac/FR3 execution.'])
 with OUT.open('x')as stream:json.dump(report,stream,ensure_ascii=False,allow_nan=False,indent=2);stream.write('\n')
 with OUT.with_suffix('.md').open('x')as stream:stream.write('# SBL PCS SOLVE01 保存证据独立后审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(len(checks))+'，失败'+str(len(fail))+'。\n\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n\n外费上界'+str(wall)+'wall/'+str(cpu)+'CPU，累计'+str(report['cumulative_charged_wall_s'])+'/'+str(report['cumulative_charged_cpu_s'])+'。真实单solve、raw、双EOF/回收/空group、全部生命周期与unknown connect、原生最终文件/sidecar/元数据分支及外费核验。EXACT仍待另冻完整独立物理路径资格；无新模型或科学运行，不证明CCD或正式性能。\n')
 print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(fail),failures=fail,upper_wall_s=wall,upper_cpu_s=cpu,observations=summary),ensure_ascii=False))
 if fail:raise SystemExit(2)
if __name__=='__main__':main()
