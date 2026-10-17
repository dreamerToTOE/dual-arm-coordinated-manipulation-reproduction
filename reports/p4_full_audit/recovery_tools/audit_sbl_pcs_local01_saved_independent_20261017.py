#!/usr/bin/env python3
"""Personnel-independent LOCAL01 saved evidence only; never import a runner/model."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import argparse,base64,datetime,hashlib,json,math,struct,subprocess
ROOT=Path(__file__).resolve().parents[3]
RUN='20261017_R2_ABB_SBL_PCS_LOCAL01'
STATIC='reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL_FIXED_SAVED_INDEPENDENT_STATIC_REVIEW_20261017.json'
STATIC_SHA='ed704149dd90533ab05bc15363e19a774fea9ab3f90173683075e8a87e896842'
FIXTURE='configs/p4_full/r2_abb_sbl_pcs_local_fixed_saved_v1.draft.json'
QUEUE='results/p4_full/20261015_R2_ABB_CBIRRT_D_PATH01/complete_original_saved_queue.json'
PATHPOST='reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_20261016.json'
SETUPPOST='reports/P4_FULL_R2_ABB_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST_20261017.json'
RUNNER='scripts/qualify_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py'
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST_20261017.json'
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
def one(events,kind):
 found=[x for x in events if x['event']==kind]
 if len(found)!=1:raise ValueError('EXACT_ONE_SAVED_EVENT '+kind+' '+str(len(found)))
 return found[0]
def semantic(response):
 local=response['local'];return dict(returned=local['source_isPathValid_returned'],trees={phase:dict(native_tree_sizes=local[phase]['native_tree_sizes'],nodes=sorted(local[phase]['nodes'],key=lambda x:x['motion_id']))for phase in ('before','after')},setup_metadata=response['setup_metadata'],writer_metadata_attempts=response['writer_metadata_attempts'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--protocol',required=True);ap.add_argument('--protocol-sha256',required=True);args=ap.parse_args();protocol=str(path(args.protocol).resolve().relative_to(ROOT))
 if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_POST_PRESERVED')
 folder=ROOT/'results/p4_full'/RUN;en=str((folder/'execution.json').relative_to(ROOT));e=load(en);p=load(protocol);claim=e['claim'];c=load(claim);internal=str((folder/'cost_receipt.jsonl').relative_to(ROOT));i=load(internal);ext=p['external_supervision'];receipt=ext['charge_path'];charge=load(receipt);st=load(STATIC);fixture=load(FIXTURE)
 ck('freeze','exact committed protocol SHA',sha(protocol)==args.protocol_sha256==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'])
 ck('freeze','exact four frozen local maxima and15/30 budget',p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())and p['budget']==e['budget']==dict(wall_s=15.,cpu_s=30.,child_cpu_limit_s=20,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)and p['maxima']==dict(new_source_processes=4,source_requests=4,setup_calls=4,local_calls=4,public_project_calls=0,solve_calls=0,connect_fixture_calls=0))
 ck('static','exact111 current independent static certificate',sha(STATIC)==STATIC_SHA and st['personnel_independent']is True and st['checks_total']==st['checks_passed']==111 and st['checks_failed']==0 and st['status'].startswith('PASS')and p['fixture_independent_POST']==STATIC)
 ck('execution','actual local success and pending independent fields',e['schema']=='P4_R2_ABB_SBL_PCS_LOCAL01_EXECUTION_V1'and e['run_id']==RUN and e['classification']==p['classification']and e['status']==i['status']=='SOURCE_FIXED_LOCAL_OBSERVED_PENDING_INDEPENDENT_POST'and e['diagnostics']==[]and e['independent_local_qualified']is e['independent_path_qualified']is e['continuous_collision_certificate']is False)
 ck('claim','exclusive no-retry exact frozen claim',c['run_id']==RUN and c['source_commit']==e['source_commit']and c['protocol']==protocol and c['budget']==p['budget']and c['no_retry_reset_resume']is True and sha(claim)==e['claim_sha256']==e['claim_after_sha256'])
 ck('binding','protocol prior source and after hashes exact',all(e[k]==p[k]for k in('budget','bound_files_sha256','prior_execution_sha256','previous_r2_wall_s','previous_r2_cpu_s','actual_charge_prior','zero_calls'))and e['bound_files_after_sha256']==p['bound_files_sha256'])
 changed=[n for n,w in p['bound_files_sha256'].items()if sha(n)!=w]
 ck('bound','every current bound asset unchanged '+str(len(p['bound_files_sha256'])),not changed)
 for n,w in p['own_source_sha256'].items():ck('source','committed exact runner/source '+n,sha(n)==w and hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest()==w)
 ck('commit','committed exact protocol and independent static certificate',all(hashlib.sha256(subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)).hexdigest()==sha(n)for n in (protocol,STATIC)))
 ck('static','current config PRE runner supervisor match retained independent review',all(st['retained_sha256'][n]==sha(n)for n in (FIXTURE,'reports/P4_FULL_R2_ABB_SBL_PCS_LOCAL_FIXED_SAVED_PRE_DRAFT_20261017.md',RUNNER,SUPERVISOR)))
 build=p['build_assets'];bp=load(build['personnel_independent_POST']);be=load(build['execution']);bm=load(build['manifest'])
 ck('build','BUILD02 compiler-only independent ancestor reused',sha(build['execution'])==build['execution_sha256']==bp['execution_sha256']and sha(build['manifest'])==build['manifest_sha256']and sha(build['personnel_independent_POST'])==build['personnel_independent_POST_sha256']and be['run_id']=='20261017_R2_ABB_SBL_PCS_BUILD02'and bm['status']==be['status']=='BUILT_NOT_QUERIED'and bp['personnel_independent']is bp['engineering_build_qualified']is bp['external_supervision_qualified']is True and bp['checks_total']==bp['checks_passed']==13186 and bp['checks_failed']==0)
 expected_schedule=[]
 for row in fixture['schedule']:
  changed_request=json.loads(json.dumps(row));changed_request['request']['separately_frozen_runtime_qualification']=True;changed_request['request']['fixture']['separately_frozen_local_fixture']=True;expected_schedule.append(changed_request)
 ck('schedule','exact frozen four original saved requests only two booleans changed',exact(p['schedule'],expected_schedule)and [(x['fixture_name'],x['mode'])for x in p['schedule']]==[('positive','trace'),('positive','plain'),('negative','trace'),('negative','plain')])
 ck('scope','actual four local setup and zero solve projection formal VI',e['setup_calls']==e['local_calls']==e['binary_execution_calls']==4 and e['public_project_calls']==e['solve_calls']==e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and all(x==0 for x in e['zero_calls'].values())and e['plain_trace_semantics_equal']is True)
 journalpath=folder/'evidence.jsonl';journal=raw(journalpath);lines=journal.splitlines(keepends=True)
 ck('journal','all complete nonempty JSONLF and exact digest',all(x.endswith(b'\n')and x.strip()for x in lines)and sha(journalpath)==e['evidence_journal_sha256'])
 events=[parse(x)for x in lines];kinds=Counter(x['event']for x in events);prefix=one(events,'local_setup')['record'];mutable={'status','setup_calls','local_calls','binary_execution_calls'}
 ck('journal','initial prefix and immutable fields retained',prefix['status']=='STOP_PREFIX_RETAINED'and prefix['setup_calls']is prefix['local_calls']is None and prefix['binary_execution_calls']==0 and all(e[k]==v for k,v in prefix.items()if k not in mutable))
 ck('journal','actual final counts diagnostics',one(events,'final_counts')['counts']==e['counts']and one(events,'final_counts')['diagnostics']==[])
 starts=[j for j,x in enumerate(events)if x['event']=='source_process_start_attempted'];stop=next(j for j,x in enumerate(events)if x['event']=='final_raw_stream');ends=starts[1:]+[stop]
 ck('journal','four sequential source sessions exact final raw8',len(starts)==len(ends)==4 and kinds['final_raw_stream']==8)
 reg=e['source_process_registry'];responses=e['responses'];ck('lifecycle','exact four actual registered source responses',len(reg)==len(responses)==4 and e['complete_source_raw_evidence_gate']is True)
 oldpost=load(SETUPPOST);olde=load(oldpost['execution']);oldscope=olde['actual_loaded_project_symbol_scope'];case_summary=[];semantic_by_name={};expected_mesh={};discrete_link={}
 for index,(row,begin,end,proc,response)in enumerate(zip(p['schedule'],starts,ends,reg,responses)):
  group=events[begin:end];label=str(index)+' '+row['fixture_name']+' '+row['mode'];work=folder/f"request_{index:02}_{row['fixture_name']}_{row['mode']}"/'work';rf=row['request']['fixture'];name=row['fixture_name'];mode=row['mode'];expected=fixture['fixtures'][name]['expected_observations']
  streams={}
  for channel in('stdout','stderr'):
   data=raw(folder/f'request_{index:02}_{channel}.bin');streams[channel]=data;chunks=[base64.b64decode(x['base64'],validate=True)for x in group if x['event']=='raw_pipe_chunk'and x['channel']==channel]
   saved=[x for x in events if x['event']=='final_raw_stream'and x['schedule_index']==index and x['channel']==channel]
   ck('raw',label+' exact chunk/final bytes '+channel,len(saved)==1 and b''.join(chunks)==data and all(len(base64.b64decode(x['base64'],validate=True))==x['bytes']for x in group if x['event']=='raw_pipe_chunk'and x['channel']==channel)and saved[0]['bytes']==len(data)and saved[0]['sha256']==hashlib.sha256(data).hexdigest()and base64.b64decode(saved[0]['base64'],validate=True)==data)
  ck('raw',label+' one complete exact JSON response',streams['stdout'].endswith(b'\n')and len(streams['stdout'].splitlines())==1 and parse(streams['stdout'])==response==one(group,'parsed_response_before_gates')['response']and base64.b64decode(one(group,'raw_response_line')['base64'],validate=True)==streams['stdout'])
  req=one(group,'setup_request_exact_bytes');rb=base64.b64decode(req['base64'],validate=True);write=one(group,'single_request_write_and_stdin_close');expectedraw=json.dumps(row['request'],allow_nan=False,separators=(',',':')).encode()+b'\n'
  ck('request',label+' one atomic exact write then EOF',rb==expectedraw and len(rb)<4096 and req['request']==row['request']==response['request']and req['bytes']==len(rb)and req['sha256']==hashlib.sha256(rb).hexdigest()and write['actual_sent']==len(rb)and write['exact_full_request_written']is write['stdin_closed']is True and write['sent_sha256']==hashlib.sha256(rb).hexdigest()and base64.b64decode(write['sent_bytes_base64'],validate=True)==rb)
  ck('response',label+' exact source local pending qualification',response['schema']=='P4_ABB_SBL_PCS_SHADOW_V2_RUNTIME_DRAFT'and response['status']=='SOURCE_LOCAL_OBSERVED_PENDING_INDEPENDENT_QUALIFICATION'and response['operation']=='local'and response['mode']==mode and response['setup_dispatches']==response['source_dispatch_started']==response['source_dispatch_completed']==1 and response['public_project_observations']==response['solve_calls']==response['formal_table_I_calls']==response['new_VI_candidate_constructions']==response['remaining_live_motions']==0 and response['independent_path_qualified']is response['continuous_collision_certificate']is False and response['setup_scope']=='NECESSARY_RUNTIME_SETUP_NOT_REPEATED_PUBLIC13_QUALIFICATION')
  local=response['local'];before=sorted(local['before']['nodes'],key=lambda x:x['motion_id']);after=sorted(local['after']['nodes'],key=lambda x:x['motion_id']);ids=[x['motion_id']for x in before];node_by_id={x['motion_id']:x for x in before}
  ck('local',label+' original true/false and exact tree sizes',local['kind']=='lazy_chain'and local['fixture_id']==rf['fixture_id']and local['fixture_adapter']=='RECONSTRUCTED_TREE_FIXTURE_ORIGINAL_SBL_METHOD_BODIES'and local['saved_input_references']==rf['saved_input_references']and local['no_retry_or_fixture_replacement']is True and local['source_isPathValid_returned']is expected['source_isPathValid_returned']and local['before']['native_tree_sizes']==expected['native_tree_sizes_before']and local['after']['native_tree_sizes']==expected['native_tree_sizes_after']and exact(response['trees_before_destruction'],local['after']))
  ck('identity',label+' all distinct exact saved node lifetime state generation',len(before)==len(rf['start_chain'])and len(set(ids))==len(set(x['state_id']for x in before))==len(before)and ids==list(range(1,len(before)+1))and all(x['address_generation']==1 and x['tree']=='start'for x in before))
  for j,(node,saved)in enumerate(zip(before,rf['start_chain'])):
   ck('identity',label+' saved node '+str(saved['saved_node_id'])+' q12 branches role ancestry',hex64(node['q12'])==hex64(saved['q12'])and [node['ik_q1_active'],node['ik_q2_active']]==saved['ik']and node['a_chain']==saved['assigned_active_role']and node['a_chain_provenance']==('ROOT_ASSIGNED'if j==0 else'GROW_ASSIGNED')and node['root_motion_id']==ids[0]and node['parent_motion_id']==(0 if j==0 else ids[j-1])and node['valid']is(j==0))
  if name=='positive':
   ck('local',label+' positive retained exact2 now child valid',len(after)==2 and all({k:v for k,v in node.items()if k!='valid'}=={k:v for k,v in before[j].items()if k!='valid'}and node['valid']is True for j,node in enumerate(after)))
  else:ck('local',label+' negative root retained child+grandchild gone',len(after)==1 and after[0]==before[0])
  m=response['setup_metadata'];om=olde['actual_setup_metadata'];ck('setup',label+' native dimension range cell metadata no public13/RNG',all(m[k]==om[k]for k in('projection_dimension','projection_dynamic_type','native_grid_dimensions','cell_sizes','user_configured','original_solve_Range','setup_getRange'))and m['native_grid_dimensions']==[m['projection_dimension']]*2 and m['original_solve_Range']==.8 and m['setup_getRange']>0 and m['additional_public_project_observations']==m['observer_rng_draws']==0 and m['setup_internal_rng_draws']=='UNOBSERVED'and all(math.isfinite(v)and v>0 for v in m['cell_sizes']))
  ck('writer',label+' no attempts all5 native absent',response['writer_metadata_attempts']==[]and response['native_output_capture_complete']is response['shadow_sidecar_saved_and_readback_equal']is response['transport_evidence_saved_and_readback_equal']is True and len(response['native_file_evidence'])==5 and all(x['exists']is False and x['absence_retained']is True and x['readback_bytes_saved']is False and not path(x['original_path']).exists()for x in response['native_file_evidence']))
  sidecar=load(response['shadow_sidecar_path']);prefixio=load(work/'writer_evidence/transport_prefix_and_io_evidence.json')
  ck('writer',label+' durable saved sidecar/native absence match',sidecar['native_file_evidence']==response['native_file_evidence']and sidecar['attempt_count']==0 and sidecar['attempts']==[]and sidecar['no_writer_attempts_observed']is sidecar['empty_attempts_do_not_prove_write_success']is True and sidecar['final_text_readback_matches_attempts']is sidecar['ik_path_exists']is False)
  ck('writer',label+' durable saved transport exact pre-final prefix',all(response[k]==v for k,v in prefixio.items())and 'transport_evidence_saved_and_readback_equal'not in prefixio)
  observed_trace=[parse(line.split(b'P4_SBL_PCS_TRACE ',1)[1])for line in streams['stderr'].splitlines()if b'P4_SBL_PCS_TRACE 'in line]
  if mode=='trace':
   trace=response['trace'];entered={};completed={};marked=[]
   for event in trace:
    if event['event']=='entered':
     if event['id']in entered:raise ValueError('DUPLICATE_NATIVE_ENTER')
     entered[event['id']]=event['kind']
    elif event['event']=='completed':
     if event['id']in completed:raise ValueError('DUPLICATE_NATIVE_COMPLETE')
     completed[event['id']]=event['kind']
    elif event['event']=='observed':marked.append(event)
    else:raise ValueError('UNKNOWN_NATIVE_TRACE_EVENT')
   calls=dict(Counter(entered.values()));rbs=calls.get('state_rbs',0)+calls.get('vector_rbs',0)
   ck('trace',label+' exact raw balanced original calls',trace==observed_trace and response['source_counts_observed']is True and entered==completed and calls==response['source_started']==response['source_completed']and calls.get('isPathValid')==1 and calls.get('mesh_load')==1 and calls.get('freeGridMotions')==2 and calls.get('save2file',0)==calls.get('solve',0)==calls.get('checkSolution',0)==0)
   ck('trace',label+' actual RBS/removal qualification',rbs>=2 and calls.get('removeMotion',0)==0 if name=='positive'else rbs==0 and calls.get('removeMotion')==2)
   if name=='positive':
    oldq=load(QUEUE);oldphysical=load(PATHPOST);edgeids=oldq['edges'][0]['node_ids'];lookup={hex64(oldq['nodes'][j]):j for j in edgeids};projects=[];unmatched=[];frames={};vstack=[];rootids=[]
    for event in trace:
     if event['kind']=='fixed_branch_project'and event['event']=='completed':
      result=event['result'];matched=lookup.get(hex64(result['q12']));projects.append(dict(trace_id=event['id'],returned=result['returned'],saved_node_id=matched,q12_binary64=hex64(result['q12'])))
      if matched is None:unmatched.append(event['id'])
     if event['kind']=='vector_rbs':
      if event['event']=='entered':
       frame=dict(trace_id=event['id'],args=event['args'],children=[]);frames[event['id']]=frame
       if vstack:frames[vstack[-1]]['children'].append(event['id'])
       else:rootids.append(event['id'])
       vstack.append(event['id'])
      elif event['event']=='completed':
       if not vstack or vstack[-1]!=event['id']:raise ValueError('RBS_RECURSION_TRACE_NOT_NESTED')
       frames[event['id']]['returned']=event['result']['returned'];vstack.pop()
    leaves=[];bad_structure=[]
    for frame in frames.values():
     a=frame['args'];children=frame['children'];left=lookup.get(hex64(a['qa12']));right=lookup.get(hex64(a['qb12']));d=math.dist(a['qa12'],a['qb12'])
     if frame.get('returned')is not True or a['active_chain']!=0 or a['branch']!=3:bad_structure.append(frame['trace_id'])
     if not children:leaves.append(dict(trace_id=frame['trace_id'],saved_node_a=left,saved_node_b=right,distance_full12=d))
     elif len(children)==2:
      first=frames[children[0]]['args'];second=frames[children[1]]['args']
      if not(hex64(a['qa12'])==hex64(first['qa12'])and hex64(first['qb12'])==hex64(second['qa12'])and hex64(second['qb12'])==hex64(a['qb12'])):bad_structure.append(frame['trace_id'])
     else:bad_structure.append(frame['trace_id'])
    leafpairs=[(x['saved_node_a'],x['saved_node_b'])for x in leaves];orderedpairs=sorted(leafpairs)if all(a is not None and b is not None for a,b in leafpairs)else[]
    fully_linked=not unmatched and len(projects)==107 and all(x['returned']is True for x in projects)and len(set(x['saved_node_id']for x in projects))==107 and set(x['saved_node_id']for x in projects)==set(edgeids[1:-1])and len(frames)==215 and len(rootids)==1 and not vstack and not bad_structure and len(leaves)==108 and orderedpairs==list(zip(edgeids,edgeids[1:]))and all(x['distance_full12']<.05 for x in leaves)
    discrete_link=dict(status='PASS_EXACT_BINARY64_REUSE_OLD_EDGE0_DISCRETE_CERTIFICATE'if fully_linked else'UNKNOWN_NOT_ALL_NEW_RECURSION_POINTS_EXACTLY_LINKED',old_queue=QUEUE,old_queue_sha256=sha(QUEUE),old_independent_path_POST=PATHPOST,old_independent_path_POST_sha256=sha(PATHPOST),old_edge_index=0,old_edge_node_count=len(edgeids),fixed_project_count=len(projects),fixed_project_matches=projects,unmatched_project_trace_ids=unmatched,vector_rbs_count=len(frames),leaf_count=len(leaves),leaves=leaves,recursion_structure_bad_trace_ids=bad_structure,all_new_projected_q12_match_old_independent_nodes=fully_linked,continuous_collision_certificate=False,new_model_queries=0)
    ck('discrete reuse','old independent physical certificate and queue exact',oldphysical['personnel_independent']is oldphysical['independent_path_qualified']is True and oldphysical['checks_total']==oldphysical['checks_passed']==58152 and oldphysical['checks_failed']==0 and oldphysical['retained_sha256'][QUEUE]==sha(QUEUE)==st['retained_sha256'][QUEUE])
    if fully_linked:
     qualified=[]
     for j in edgeids:
      n='results/p4_full/20261015_R2_ABB_CBIRRT_D_PATH01/node_'+str(j).zfill(5)+'.json';saved=load(n);bound=oldphysical['retained_sha256'].get(n,oldphysical['retained_sha256'].get(str(path(n))))
      qualified.append(sha(n)==bound and hex64(saved['q12'])==hex64(oldq['nodes'][j])and saved['qualified']is saved['math_qualified']is saved['limits']['legal']is True and saved['collision']['collision']is False and saved['collision']['selected_variant']=='aligned')
     ck('discrete reuse','all109 old independently qualified node files retain exact bytes',len(qualified)==109 and all(qualified))
     ck('discrete reuse','107 exact interior binary64 matches and108 original adjacent leaves',fully_linked)
   registered=[x['args']for x in marked if x['kind']=='motion_lifetime_registered'];retired=[x['args']for x in marked if x['kind']=='motion_lifetime_retired'];retirement=[x['args']for x in marked if x['kind']=='motion_before_native_retirement']
   ck('lifetime',label+' all registered and retired once exact IDs',registered==before and sorted(x['motion_id']for x in retired)==ids and len(set(x['motion_id']for x in retired))==len(ids)and {x['motion_id']:x for x in retirement}=={x['motion_id']:x for x in retired})
   if name=='negative':
    child=next(x for x in retirement if x['motion_id']==ids[1]);grand=next(x for x in retirement if x['motion_id']==ids[2]);root=next(x for x in retirement if x['motion_id']==ids[0])
    ck('lifetime',label+' natural branch guard and real parent-null before delete',all(a!=b for a,b in zip(rf['start_chain'][0]['ik'],rf['start_chain'][1]['ik']))and child['parent_motion_id']==ids[0]and [x['motion_id']for x in child['original_children_before_parent_null']]==[ids[2]]and child['original_children_before_parent_null'][0]['parent_motion_id']==ids[1]and grand['parent_motion_id']==0 and grand['original_children_before_parent_null']==[]and root['original_children_before_parent_null']==[])
   semantic_by_name[name]=semantic(response)
  else:
   ck('trace',label+' plain trace null counts unobserved',response['trace']is response['source_started']is response['source_completed']is None and response['source_counts_observed']is False and observed_trace==[])
   ck('semantic',label+' exact plain/trace all nodes metadata attempts',exact(semantic(response),semantic_by_name[name]))
  scope=proc['loaded_scope'];scopeevent=one(group,'actual_loaded_project_symbol_scope')['observation'];initial=one(group,'actual_loaded_scope_raw_before_gates');candidates=one(group,'actual_loaded_symbol_candidates_before_gates');maps=base64.b64decode(scope['maps_bytes_base64'],validate=True)
  ck('loaded',label+' actual complete pre-request maps env source',scope==scopeevent and scope['actual_environment']==p['source_environment']==initial['actual_environment']and scope['actual_exe']==build['target']['binary']and scope['actual_exe_sha256']==sha(scope['actual_exe'])and scope['maps_sha256']==initial['maps_sha256']==hashlib.sha256(maps).hexdigest()and base64.b64decode(initial['maps_bytes_base64'],validate=True)==maps and scope['protected_matrix_storage_read']is False)
  mapped=set()
  for line in maps.decode().splitlines():
   parts=line.split(maxsplit=5)
   if len(parts)==6 and parts[5].startswith('/'):
    if parts[5].endswith(' (deleted)'):raise ValueError('DELETED_NATIVE_MAP')
    mapped.add(str(Path(parts[5]).resolve()))
  ck('loaded',label+' saved map hashes and reused exact OMPL providers',mapped==set(scope['mapped_files_sha256'])and scope['mapped_files_sha256']==candidates['mapped_files_sha256']and all(sha(n)==w for n,w in scope['mapped_files_sha256'].items())and scope['project_symbol_providers']==oldscope['project_symbol_providers']==candidates['project_symbol_providers']and all(oldscope['mapped_files_sha256'].get(n)==w for n,w in scope['mapped_files_sha256'].items()if n!=scope['actual_exe']))
  start=one(group,'source_process_started');sg=one(group,'source_start_group');close=one(group,'source_close_group');afterevent=one(group,'source_after_reap_group')
  ck('lifecycle',label+' original command unique registered identity reaped exit0',start['command']==[build['target']['binary'],'II',str(work),'local',mode]and start['pid']==proc['pid']and start['start_ticks']==sg['actual_start_ticks']==close['start_ticks']==afterevent['start_ticks']==proc['start_ticks']>0 and [x['pid']for x in sg['members']]==[proc['pid']]and proc['returncode']==afterevent['returncode']==0 and proc['actual_after_reap_group']==afterevent['members']==[]and not members(proc['pid']))
  ck('lifecycle',label+' both actual EOF stdin close no pending',proc['actual_pipe_EOF_observed']==afterevent['actual_pipe_EOF_observed']=={'stdout':True,'stderr':True}and {x['channel']for x in group if x['event']=='actual_pipe_EOF_observed'}=={'stdout','stderr'}and proc['stdin_closed_after_unique_request']is True and proc['request_bytes']==proc['actual_request_sent']==len(rb)and proc['request_sha256']==hashlib.sha256(rb).hexdigest())
  preclose=[x['pid']for x in proc['close_group']];ck('lifecycle',label+' exact actual close branch evidence',proc['close_group']==close['members']and proc['close_poll_result']==close['actual_poll_result']and proc['close_poll_observations']==close['actual_poll_observations']and proc['close_postpoll_group']==close['actual_postpoll_group']and ((preclose==[proc['pid']]and proc['close_poll_result']is None)or(preclose in([],[proc['pid']])and proc['close_poll_result']==0 and proc['close_postpoll_group']==[])))
  for n,w in p['runtime_meshes_sha256'].items():expected_mesh[str((work/'simulator'/Path(n).name).relative_to(ROOT))]=w
  case_summary.append(dict(schedule_index=index,fixture=name,mode=mode,returned=local['source_isPathValid_returned'],before=len(before),after=len(after),source_started=response['source_started'],remaining_live_motions=response['remaining_live_motions']))
 ck('mesh','all80 exact copies retained unchanged',len(e['runtime_mesh_sha256'])==80 and e['runtime_mesh_sha256']==e['runtime_mesh_after_sha256']==expected_mesh and all(sha(n)==w for n,w in expected_mesh.items()))
 ck('counts','exact four source starts writes responses no extra',len(e['counts'])==6 and all(e['counts'][n]==4 for n in('source_process_start_attempted','source_process_started','setup_dispatch_attempted','setup_dispatched','stdout_complete_lines_observed','raw_response_lines_observed')))
 ck('retention','all saved run files still exact',all(sha(n)==w for n,w in e['retained_run_files_sha256'].items()))
 fields=raw(ext['sibling_path']).decode().strip().split()
 if len(fields)!=4:raise ValueError('EXACT_FOUR_GNU_TIME_FIELDS')
 elapsed,user,system=(Decimal(x)for x in fields[:3]);exitcode=int(fields[3]);wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'))
 ck('external','complete child GNUtime upper15/30 total3600/7200',all(x.is_finite()and x>=0 for x in(elapsed,user,system))and wall<=15 and cpu<=30 and wall+e['previous_r2_wall_s']<=3600 and cpu+e['previous_r2_cpu_s']<=7200)
 ck('external','exact external charge from actual time4 fields',charge['time_fields']==fields and charge['wall_s']==wall and charge['cpu_s']==cpu and charge['timing_valid']is charge['time_inode_unchanged']is charge['wall_CPU_caps_pass']is charge['completed_process_exit0']is charge['started_attempt']is True and charge['time_returncode']==charge['measured_child_exit']==exitcode==0 and charge['failure']is None)
 ck('external','exact execution internal receipt time hash chain',charge['source_execution']==en and charge['execution_sha256']==sha(en)==i['execution_sha256']and charge['receipt']==internal and charge['receipt_sha256']==sha(internal)and charge['time_file']==ext['sibling_path']and charge['time_sha256']==sha(ext['sibling_path']))
 ck('external','original false retained full persistence child cost covered',e['external_supervision_qualified']is i['external_supervision_qualified']is charge['external_supervision_qualified']is False and i['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and wall>=max(e['wall_s'],i['wall_s_through_execution_persistence'])and cpu>=max(e['cpu_s'],i['cpu_s_through_execution_persistence']))
 ml=raw(ext['metadata_path']).splitlines(keepends=True);me=[parse(x)for x in ml];ck('external','planned started reaped exact metadata3',len(me)==3 and [x['event']for x in me]==['planned_launch','time_process_started','time_process_reaped'])
 planned,started,reaped=me;proof=e['supervisor_launch_proof'];stat=path(ext['sibling_path']).stat();argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/RUNNER),'--protocol',str(path(protocol))]
 ck('external','actual supervisor argv parent pid source frozen SHA',planned['run_id']==RUN and planned['protocol']==protocol and planned['protocol_sha256']==args.protocol_sha256 and planned['argv']==started['argv']==proof['actual_argv']==argv and started['pid']==reaped['pid']==charge['time_process_pid']==proof['actual_time_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid']and planned['supervisor_source_sha256']==sha(SUPERVISOR)and planned['runner_sha256']==sha(RUNNER))
 ck('external','actual inherited inode FD and launch bytes proof',planned['time_inode']==proof['time_inode']==stat.st_ino and planned['time_device']==proof['time_device']==stat.st_dev and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and proof['planned_launch_line_sha256']==hashlib.sha256(ml[0]).hexdigest())
 ck('external','actual tool and log hashes exact',planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3')and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr_sha256']==sha(ext['stderr_path']))
 prior=load(p['actual_charge_prior']['ledger']);actual={str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent.name!=RUN}
 ck('prior','all actual previous executions exact charged prior',actual==e['prior_execution_after_sha256']==e['prior_execution_sha256']=={x['execution']:x['execution_sha256']for x in prior['executions']}and sha(p['actual_charge_prior']['ledger'])==p['actual_charge_prior']['ledger_sha256'])
 ck('prior','exact effective prior wall CPU sum',math.fsum(x.get('charged_wall_s',x['wall_s'])for x in prior['executions'])==e['previous_r2_wall_s']==p['actual_charge_prior']['wall_s']and math.fsum(x.get('charged_cpu_s',x['cpu_s'])for x in prior['executions'])==e['previous_r2_cpu_s']==p['actual_charge_prior']['cpu_s'])
 ck('scope','VI974 exhausted historical22500 unchanged formal0',prior['vi_B_candidate_cap']==974 and prior['vi_B_remaining']['candidate_constructions']==0 and prior['formal_table_I_calls']==0 and prior['formal_table_I_required_calls']==22500)
 changed_after=[n for n,w in retained.items()if hashlib.sha256(Path(n).read_bytes()).hexdigest()!=w];ck('unchanged','every read saved asset still exact',not changed_after)
 failed=[x for x in checks if not x['passed']]
 report=dict(schema='P4_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST_V1',status='PASS_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST'if not failed else'FAIL_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of implementation runner supervisor PRE',personnel_independent=True,independent_local_qualified=not failed,external_supervision_qualified=not failed,external_timing_qualified=not failed,external_cost_qualified=not failed,independent_path_qualified=False,continuous_collision_certificate=False,checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),failures=failed,checks=checks,source_commit=e['source_commit'],execution=en,execution_sha256=sha(en),protocol=protocol,protocol_sha256=sha(protocol),claim=claim,claim_sha256=sha(claim),receipt=receipt,receipt_sha256=sha(receipt),internal_receipt=internal,internal_receipt_sha256=sha(internal),external_time=ext['sibling_path'],external_time_sha256=sha(ext['sibling_path']),external_time_fields=fields,upper_wall_s=wall,upper_cpu_s=cpu,cumulative_charged_wall_s=e['previous_r2_wall_s']+wall,cumulative_charged_cpu_s=e['previous_r2_cpu_s']+cpu,retained_sha256=retained,cases=case_summary,positive_discrete_old_certificate_link=discrete_link,source_processes=4,setup_calls=4,local_calls=4,public_project_calls=0,solve_calls=0,new_import_model_compile_binary_setup_local_solve_VI_formal_calls=0,limits=['Only saved source local mechanism and transport/lifetime evidence; no new model or independent physical path oracle.','Fixture q12 and true branches reuse the prior independent CBi discrete certificate; artificial SBL ancestry explicitly RECONSTRUCTED. Exact binary64 linkage separately reports whether all107 new projection outputs and108 leaf pairs reuse old109 qualified nodes. It never proves continuous collision.','No checkSolution/connect/native writer dispatched, no global SBL planning, no formal statistics or performance claim.','GNUtime child includes runner preflight and final persistence. Supervisor own metadata/fsync and historical unmeasured tails remain outside measured child boundary/UNKNOWN.','D080 I method plus II–V complete obligations18000 retained, formal budget unapproved; VI974/974 archival only. No P2/Isaac/FR3 execution.'])
 with OUT.open('x')as stream:json.dump(report,stream,ensure_ascii=False,allow_nan=False,indent=2);stream.write('\n')
 with OUT.with_suffix('.md').open('x')as stream:stream.write('# SBL PCS LOCAL01 保存证据人员独立后审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(len(checks))+'，失败'+str(len(failed))+'。\n\n'+json.dumps(case_summary,ensure_ascii=False,indent=2)+'\n\n实际四进程/四setup/四local，public13/solve/connect/writer/VI/formal均0。正例真实RBS非平凡true并保留child valid，负例真实分支不同不调RBS且递归删除child和grandchild；完整生命周期、q12/分支/角色/祖先、plain/trace、raw/EOF/reap/group、原生文件缺失及持久sidecar、加载scope与外费逐项核验。\n\n费用上界'+str(wall)+'wall / '+str(cpu)+'CPU，累计'+str(report['cumulative_charged_wall_s'])+' / '+str(report['cumulative_charged_cpu_s'])+'。局部机制成功不是独立物理端到端路径或连续碰撞资格，checkSolution/connect/writer仍待另冻单solve。无新模型计算或科学运行；原失败、UNKNOWN、VI只读边界和正式预算未批准均保留。\n')
 print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),failures=failed,upper_wall_s=wall,upper_cpu_s=cpu),ensure_ascii=False))
 if failed:raise SystemExit(2)
if __name__=='__main__':main()
