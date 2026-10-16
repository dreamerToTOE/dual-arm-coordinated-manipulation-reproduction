#!/usr/bin/env python3
"""Saved-only LOCAL02 check. Author implemented runner: never independent POST.

Stdlib only. No imported runner/model, process, FK/IK/RBS or scientific call.
No report is written without an actual execution and explicit --output.
"""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import argparse
import base64
import hashlib
import json
import math
import struct

ROOT=Path(__file__).resolve().parents[3]
RUN='20261015_R2_ABB_CBIRRT_D_LOCAL02'
PASS='PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED'
MARKER=b'P4_CBIRRT_D_TRACE '
GATES=('actual12_all_true','six_plain_trace_pairs_binary64_equal','complete_three_M_binary64_equal_saved80_65_34',
 'two_SVC_zero_CBi_zero_direct_rng','raw_EOF_and_all_processes_reaped_exit0','old177_complete_discrete_certificate_reused',
 'external_cost_and_identity_qualified','original_D64_STOP_and_H_STOP_preserved')

def path(n):
 p=Path(n);return p if p.is_absolute()else ROOT/p

def sha(n):return hashlib.sha256(path(n).read_bytes()).hexdigest()
def load(n):return json.loads(path(n).read_text())
def bits(q):return struct.pack('>'+str(len(q))+'d',*q).hex()
def canonical(v):
 if isinstance(v,bool):return v
 if type(v)in(int,float):return ['binary64',struct.pack('>d',v).hex()]
 if isinstance(v,list):return [canonical(x)for x in v]
 if isinstance(v,dict):return {k:canonical(x)for k,x in v.items()}
 return v

def exact(a,b):return canonical(a)==canonical(b)
def normalized(r):
 excluded=('mode','source_counts_observed','source_started','source_completed','trace')
 a={k:v for k,v in r.items()if k not in excluded};a['construction']={k:v for k,v in a['construction'].items()if k not in excluded};return a


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 ep='results/p4_full/'+RUN+'/execution.json'
 if not path(ep).is_file():raise SystemExit('WAIT_ACTUAL_LOCAL02_NO_REPORT_NO_QUERIES')
 checks=[];failed=[];retained={}
 def ck(name,ok):
  row=dict(id=name,passed=bool(ok));checks.append(row)
  if not ok:failed.append(row)
 def bind(name,want=None):
  actual=sha(name);retained[str(name)]=actual
  if want is not None:ck('sha '+str(name),actual==want)
 e=load(ep);p=load(e['protocol']);bind(ep);bind(e['protocol'],e['protocol_sha256']);bind(e['claim'],e['claim_sha256'])
 ck('actual_internal_PASS',e['run_id']==RUN and e['status']==PASS and e['external_supervision_qualified']is False)
 ck('frozen_protocol_and_reviews',p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values()))
 ck('all12_done_no_UNKNOWN',e['completed_dispatch_ids']==list(range(12))and not e['UNKNOWN_uncompleted_fixtures'])
 ck('measured_budget_unchanged',p['budget']['wall_s']==30 and p['budget']['cpu_s']==60 and p['budget']['child_cpu_limit_s']==30)
 ck('before_after_bound_equal',e['bound_files_sha256']==e['bound_files_after_sha256'])
 for n,w in e['bound_files_sha256'].items():bind(n,w)
 for n,w in e['prior_execution_sha256'].items():bind(n,w)
 ck('prior_before_after_equal',e['prior_execution_sha256']==e['prior_execution_after_sha256'])
 bind(e['evidence_journal'],e['evidence_journal_sha256'])
 rows=[json.loads(line)for line in path(e['evidence_journal']).read_bytes().splitlines()if line.strip()]
 rawrows=[r for r in rows if r['event']=='raw_response_line'];parsed=[r for r in rows if r['event']=='parsed_response_before_gates']
 ck('exact12_raw_and_parse_rows',[r['dispatch_index']for r in rawrows]==[r['dispatch_index']for r in parsed]==list(range(12)))
 fixtures=p['fixed_schedule'];edges=p['fixed_edges'];responses={};rawmode={'plain':[],'trace':[]};projections={};sumtrace=Counter(mesh_load=1)
 ck('fixed3_original_roles_branches_nodes',[(r['active_chain'],r['branch'],r['reference_node_count'])for r in edges]==[(0,3,80),(1,3,65),(0,0,34)])
 ck('fixed12_schedule',len(fixtures)==12 and [f['dispatch_index']for f in fixtures]==list(range(12)))
 for i,(rawrow,parsedrow,fixture)in enumerate(zip(rawrows,parsed,fixtures)):
  raw=base64.b64decode(rawrow['base64'],validate=True);r=json.loads(raw);edge=edges[fixture['edge_index']];mode=fixture['mode'];call=fixture['local_call']
  rawmode[mode].append(raw);responses[(mode,edge['edge_index'],call)]=r
  ck(f'{i}:raw_bytes_and_parsed_binding',len(raw)==rawrow['bytes']and raw.endswith(b'\n')and exact(r,parsedrow['response']))
  ck(f'{i}:source_request_true_scope',exact(r['request'],fixture['request'])and r['returned']is True and r['source_dispatch_started']==r['source_dispatch_completed']==1
   and r['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1'and r['status']=='SOURCE_INTERFACE_COMPLETED_NOT_QUALIFIED'and r['operation']=='local'and r['environment']=='II'and r['mode']==mode
   and r['solve_calls']==r['formal_table_I_calls']==0 and r['independent_path_qualified']is False)
  for arm in('qa12','qb12'):ck(f'{i}:{arm}:unchanged',bits(r[arm+'_after'])==bits(fixture['request'][arm])==r[arm+'_binary64_after'])
  c=r['construction'];ck(f'{i}:SVC1_CBi_rng_seed0',c['svc_only_constructor_dispatch_completed']==1 and c['cbirrt_constructor_dispatch_completed']==c['source_direct_rng_member_initializations_structural']==c['ompl_setSeed_calls_completed']==c['srand_calls_completed']==0)
  if call=='reconstruct':ck(f'{i}:entireM_exact',exact(r['path_q12'],edge['reference_path_q12'])and len(r['path_q12'])==edge['reference_node_count'])
  if mode=='plain':
   ck(f'{i}:plain_unobserved',r['source_counts_observed']is False and all(x['trace']is None and x['source_started']is None and x['source_completed']is None for x in(r,c)))
   continue
  stack=[];pairs=[];started=Counter();completed=Counter();serial=0
  for item in r['trace']:
   if item['event']=='entered':
    serial+=1;ck(f'{i}:trace_serial{serial}',item['id']==serial);stack.append(item);started[item['kind']]+=1
   else:
    ck(f'{i}:trace_has_entry{item["id"]}',item['event']=='completed'and bool(stack))
    if not stack:continue
    a=stack.pop();ck(f'{i}:trace_pair{item["id"]}',(a['id'],a['kind'])==(item['id'],item['kind']));pairs.append((a,item));completed[item['kind']]+=1
  m=edge['reference_node_count']-2;top='state_rbs'if call=='rbs'else'state_reconstruct';vector='vector_rbs'if call=='rbs'else'vector_reconstruct'
  expected={top:1,vector:2*m+1,'fixed_branch_project':m,'native_fk':m,'native_ik':m,'collision':m}
  ck(f'{i}:actual_nested_body_counts',not stack and dict(started)==dict(completed)==r['source_started']==r['source_completed']==expected)
  ck(f'{i}:state_top',r['trace'][0]['kind']==r['trace'][-1]['kind']==top and r['trace'][-1]['result']['returned']is True)
  topa=r['trace'][0]['args'];ck(f'{i}:top_original_context',exact(topa['qa12'],fixture['request']['qa12'])and exact(topa['qb12'],fixture['request']['qb12'])and topa['active_chain']==edge['active_chain']and topa['branch']==edge['branch'])
  sequence=[]
  for a,z in sorted(pairs,key=lambda pair:pair[0]['id']):
   if a['kind']in('state_rbs','vector_rbs','state_reconstruct','vector_reconstruct','native_ik','fixed_branch_project'):ck(f'{i}:true_body{a["id"]}',z['result']['returned']is True)
   if a['kind']=='collision':ck(f'{i}:clear_collision{a["id"]}',z['result']['returned']==0)
   if a['kind']=='fixed_branch_project':
    qa=a['args'];qb=z['result'];part=slice(6*edge['active_chain'],6*(edge['active_chain']+1))
    ck(f'{i}:project_context{a["id"]}',qa['active_chain']==edge['active_chain']and qa['branch']==edge['branch']and exact(qa['q12'][part],qb['q12'][part]));sequence.append(dict(input=qa,returned=qb))
  ck(f'{i}:projected_old_interiors',Counter(bits(x['returned']['q12'])for x in sequence)==Counter(bits(q)for q in edge['reference_path_q12'][1:-1]))
  if call=='reconstruct':ck(f'{i}:trace_entireM',exact(r['trace'][-1]['result']['path_q12'],edge['reference_path_q12']))
  projections[(edge['edge_index'],call)]=sequence;sumtrace.update(started)
 for edge in edges:
  n=edge['edge_index']
  for call in('rbs','reconstruct'):ck(f'{n}:{call}:plain_trace',exact(normalized(responses[('plain',n,call)]),normalized(responses[('trace',n,call)])))
  ck(f'{n}:RBS_reconstruct_projection_sequence',exact(projections[(n,'rbs')],projections[(n,'reconstruct')]))
 ck('source_registry_two_reaped_exit0',len(e['source_process_registry'])==2 and all(x['reaped']is True and x['returncode']==0 for x in e['source_process_registry']))
 ck('raw_body_aggregate',e['actual_raw_trace_started']==e['actual_raw_trace_completed']==dict(sumtrace))
 for mode,binding in e['source_raw_trace_bindings'].items():
  ck(mode+':EOF_exit_closed_group',binding['pipe_EOF_drained']is True and binding['cleanup_closed']is True and binding['startup_complete']is True and binding['process_returncode']==0 and binding['unexpected_stdout_tail_bytes']==0 and len(binding['source_close_process_group'])==1)
  for channel,record in binding['raw_streams'].items():bind(record['path'],record['sha256'])
  stdout=path(binding['raw_streams']['stdout']['path']).read_bytes();stderr=path(binding['raw_streams']['stderr']['path']).read_bytes()
  ck(mode+':stdout_original_raw_exact',stdout==b''.join(rawmode[mode]))
  actual=[json.loads(line.split(MARKER,1)[1])for line in stderr.splitlines()if MARKER in line]
  expected=[]
  if mode=='trace':
   expected.extend(responses[(mode,0,'rbs')]['construction']['trace'])
   for f in fixtures:
    if f['mode']==mode:expected.extend(responses[(mode,f['edge_index'],f['local_call'])]['trace'])
  ck(mode+':complete_raw_source_trace',exact(actual,expected))
 certificate=p['saved177_certificate'];ck('old177_certificate_reused_exact',exact(certificate,e['reused_saved177_certificate'])and certificate['qualified_unique_nodes']==177 and certificate['edge_node_counts']==[80,65,34]and certificate['continuous_collision_certificate']is False)
 for name,want in certificate['files_sha256'].items():bind(name,want)
 ck('scope_stays_discrete_no_new_physical',e['new_independent_physical_queries']==0 and e['CBi_constructor_dispatches']==e['direct_CBi_rng_member_initializations_structural']==0 and e['completed_SVC_constructor_dispatches']==2 and e['new_VI_candidate_constructions']==e['formal_table_I_calls']==0)
 ext=p['external_supervision'];charge=load(ext['charge_path']);bind(ext['charge_path'])
 for field,shafield in(('sibling_path','time_sha256'),('metadata_path','metadata_sha256'),('stderr_path','stderr_sha256')):bind(ext[field],charge[shafield])
 fields=path(ext['sibling_path']).read_text().strip().split();elapsed,user,system=(Decimal(v)for v in fields[:3]);upperwall=float(elapsed+Decimal('.01'));uppercpu=float(user+system+Decimal('.02'))
 ck('external_time_finite_exit0_cap',len(fields)==4 and all(v.is_finite()and v>=0 for v in(elapsed,user,system))and int(fields[3])==0 and upperwall<=30 and uppercpu<=60)
 ck('charge_exact_upper_bound_exit0_identity',exact([upperwall,uppercpu],[charge['wall_s'],charge['cpu_s']])and charge['timing_valid']is True and charge['time_inode_unchanged']is True and charge['wall_CPU_caps_pass']is True and charge['completed_process_exit0']is True and charge['execution_sha256']==sha(ep))
 receipt=load(charge['receipt']);bind(charge['receipt'],charge['receipt_sha256']);ck('receipt_binding_and_budget',receipt['execution_sha256']==sha(ep)and receipt['status']==PASS and receipt['wall_s_through_execution_persistence']<=upperwall and receipt['cpu_s_through_execution_persistence']<=uppercpu)
 metadata=[json.loads(line)for line in path(ext['metadata_path']).read_bytes().splitlines()];launch=e['supervisor_launch_proof'];planned,started,reaped=metadata
 ck('actual_time_PID_argv_inode_bound',planned['event']=='planned_launch'and started['event']=='time_process_started'and reaped['event']=='time_process_reaped'and started['pid']==reaped['pid']==launch['actual_time_pid']==charge['time_process_pid']and reaped['returncode']==0 and exact(planned['argv'],launch['actual_argv'])and launch['time_inode']==planned['time_inode']==path(ext['sibling_path']).stat().st_ino)
 ck('planned_original_line_bound',launch['planned_launch_line_sha256']==hashlib.sha256(path(ext['metadata_path']).read_bytes().splitlines(keepends=True)[0]).hexdigest())
 old=load('results/p4_full/20261015_R2_ABB_CBIRRT_D_DISTANCE01/execution.json');ck('old_D64_failure_kept',old['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET'and old['completed_dispatch_ids']==list(range(61))and [r['dispatch_index']for r in old['UNKNOWN_uncompleted_fixtures']]==[61,62,63]and old['source_process_registry'][-1]['returncode']==-9)
 ledger=load(p['prerequisites']['authoritative_ledger']);hrows=[r for r in ledger['executions']if 'RANDOM_HELPER_H01'in r['run_id']];ck('H_original_STOP_kept',len(hrows)==1 and load(hrows[0]['execution'])['status'].startswith('STOP'))
 report=dict(schema='P4_LOCAL02_IMPLEMENTER_SAVED_AUDIT_V1',status='PASS_IMPLEMENTER_SAVED_AUDIT_NOT_INDEPENDENT_CERTIFICATE'if not failed else'STOP_SAVED_EVIDENCE_UNQUALIFIED',
  reviewer='nr_path_prepare, implemented LOCAL02 runner',personnel_independent=False,checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),failures=failed,
  execution_sha256=sha(ep),external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),upper_wall_s=upperwall,upper_cpu_s=uppercpu,
  external_supervision_verified_by_implementer=not failed,external_supervision_qualified=False,independent_POST_still_required=True,required_gate_names=list(GATES),retained_sha256=retained,
  full_checks=checks,new_model_process_scientific_query_compile_claim_protocol_prior_calls=0,CCD_certificate=False,not_full_path_or_paper_qualification=True)
 with args.output.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:report[k]for k in('status','checks_total','checks_passed','checks_failed','personnel_independent','external_supervision_qualified')}))

if __name__=='__main__':main()
