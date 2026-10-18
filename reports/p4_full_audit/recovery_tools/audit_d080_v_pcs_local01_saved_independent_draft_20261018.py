#!/usr/bin/env python3
"""DRAFT LOCAL01 saved-only transport/source semantics and cost POST.

Never import runner/model, compile, execute binary or call math/collision oracle.
Successful source outputs remain pending independent Comau physical qualification.
"""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
from datetime import datetime, timezone
import argparse
import base64
import hashlib
import json
import math
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RUN='20261018_R2_D080_V_PCS_LOCAL01'
FOLDER=ROOT/'results/p4_full'/RUN
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_LOCAL01_SAVED_INDEPENDENT_POST_20261018.json'
RUNNER='scripts/p4_d080/qualify_v_pcs_local_v1_draft.py'
SUPERVISOR='scripts/p4_d080/supervise_v_pcs_local_v1_draft.py'
PRE='reports/P4_D080_ENV_V_PCS_LOCAL_FIXED_PRE_DRAFT_20261018.md'
GATE='reports/P4_D080_ENV_V_PCS_LOCAL_COMPOSITE_BUILD_GATE_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
GATE_SHA='307a989b8a093d9ace4bb458a38c96a8684afcb6faf04c912939418363f75c58'
FIXTURE='configs/p4_d080/v_pcs_local_fixed_saved_v1.DRAFT.json'
FIXTURE_SHA='1c7ced65d4652529c9d956142ab4264746aa30b7c0809cf4b2731a655b33401c'
BUILD='reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_COMPOSITE_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json'
BUILD_SHA='3a04f69aedc861166de04e147046a19ea35500b13e73270acb4e742ec7e9f7f8'
BASIS='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
MARKER=b'P4_V_PCS_TRACE '
checks=[];retained={}

def path(n):
    p=Path(n);return p if p.is_absolute()else ROOT/p
def raw(n):
    p=path(n);b=p.read_bytes();h=hashlib.sha256(b).hexdigest()
    previous=retained.setdefault(str(p),h)
    if previous!=h:ck('preservation','re-read original bytes changed '+str(p),False)
    return b
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def load(n):return json.loads(raw(n))
def ck(group,n,v):checks.append(dict(group=group,check=n,passed=bool(v)))
def exact(a,b):
    if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
    if type(a)in(int,float)and type(b)in(int,float):return struct.pack('>d',a)==struct.pack('>d',b)
    if type(a)is not type(b):return False
    if isinstance(a,dict):return set(a)==set(b)and all(exact(a[k],b[k])for k in a)
    if isinstance(a,(list,tuple)):return len(a)==len(b)and all(exact(x,y)for x,y in zip(a,b))
    return a==b
def finiteq(q):return isinstance(q,list)and len(q)==12 and all(type(v)in(int,float)and math.isfinite(v)for v in q)
def qkey(q):return struct.pack('>12d',*q).hex()
def lines(n):
    b=raw(n);ck('raw','complete JSONL newline '+str(n),not b or b.endswith(b'\n'));return[json.loads(x)for x in b.splitlines()]

def audit(args):
    epath=FOLDER/'execution.json';e=load(epath);protocol=path(args.protocol);p=load(protocol);claim=load(e['claim'])
    gate=load(GATE);fixture=load(FIXTURE);build=load(BUILD)
    ck('reuse','exact13 build gate plus unchanged29 without re-review',sha(GATE)==GATE_SHA and gate['personnel_independent_for_this_delta']is True and gate['checks_total']==gate['checks_passed']==13 and gate['checks_failed']==0 and gate['reused_prior29_checks_without_rerun']['checks']==29)
    for n in(RUNNER,SUPERVISOR,PRE,FIXTURE):ck('reuse','exact reviewed current local source '+n,sha(n)==gate['source_sha256'][n])
    ck('reuse','exact fixed saved A02 fixture and actual same-source composite engineering',sha(FIXTURE)==FIXTURE_SHA and sha(BUILD)==BUILD_SHA and build['engineering_build_qualified']is build['composite_build_qualified']is True and build['original_BUILD01_engineering_build_qualified']is False and build['checks_total']==build['checks_passed']==5 and build['checks_failed']==0)
    ck('metadata','actual unique source-local expected commit protocol',e['schema']=='P4_D080_V_PCS_LOCAL_EXECUTION_V1'and e['run_id']==p['run_id']==RUN and e['source_commit']==claim['source_commit']==args.expected_source_commit and sha(protocol)==args.protocol_sha256==e['protocol_sha256']==claim['protocol_sha256'])
    ck('metadata','source observation complete but independent local and path still false',e['status']=='SOURCE_FIXED_LOCAL_OBSERVED_PENDING_INDEPENDENT_POST'and e['independent_local_qualified']is e['independent_path_qualified']is e['continuous_collision_certificate']is False and e['diagnostics']==[]and e['pre_model_loaded_symbol_observation']=='UNOBSERVED_NOT_CLAIMED')
    ck('freeze','scientific local fixed30wall60CPU formalfalse exact driver18 requests',p['schema']=='P4_D080_V_PCS_LOCAL_RUN_FROZEN_V1'and p['frozen']is p['scientific_execution_authorized']is p['independent_review_passed']is True and p['formal_execution_authorized']is False and p['budget']==e['budget']==dict(wall_s=30,cpu_s=60)and p['schedule_modes']==['trace','plain']and p['driver_protocol']['requests']==fixture['requests']and p['driver_protocol']['caps']==fixture['caps_per_binary_proposal']and p['maxima']==fixture['global_maxima_proposal']and p['fixture_sha256']==FIXTURE_SHA)
    ck('freeze','claim no retry immutable',claim['run_id']==RUN and claim['budget']==p['budget']and claim['no_retry_reset_resume']is True and sha(e['claim'])==e['claim_sha256'])
    for n in(RUNNER,SUPERVISOR,PRE,FIXTURE,str(protocol.relative_to(ROOT))):ck('commit','frozen actual committed bytes '+n,subprocess.check_output(['git','show',args.expected_source_commit+':'+n],cwd=ROOT)==raw(n))
    # Runtime already independently constrained the frozen union before and
    # after execution. Reuse those exact saved maps and the prior source/build
    # certificates; do not perform a third 4823-file union/body review here.
    critical=(RUNNER,SUPERVISOR,PRE,FIXTURE,BUILD)
    ck('assets','exact saved full bound maps before/after; incremental current critical bytes only',e['bound_files_sha256']==e['bound_files_after_sha256']==p['bound_files_sha256']and all(p['bound_files_sha256'].get(str(path(n).resolve()))==sha(n)for n in critical))
    ck('assets','retained raw/runtime before and after exact',all(sha(n)==h for n,h in e['retained_run_files_sha256'].items())and all(sha(n)==h for n,h in e['copied_runtime_after_sha256'].items()))
    ck('build','exact separately qualified binaries used',p['build_assets']['post_sha256']==BUILD_SHA and p['build_assets']['execution_sha256']==build['execution_sha256']and all(p['build_assets']['targets'][t['mode']]['binary']==t['binary']and p['build_assets']['targets'][t['mode']]['binary_sha256']==t['binary_sha256']==sha(t['binary'])for t in build['build_targets']))
    journal=lines(FOLDER/'evidence.jsonl');by=defaultdict(list)
    for row in journal:by[row['event']].append(row)
    ck('transport','two real source starts and38 complete lines with final counters',e['binary_execution_calls']==2 and e['public_request_calls']==36 and e['setup_calls']==2 and len(by['source_process_start_attempted'])==len(by['source_process_started'])==2 and len(by['complete_response_line'])==38 and len(by['final_counts'])==1 and by['final_counts'][0]['counts']==e['counts']and by['final_counts'][0]['diagnostics']==[])
    ck('transport','exact stdout contract fixed argv no stdin',e['source_stdout_contract']==dict(setup_rows_per_binary=1,request_rows_per_binary=18,total_rows_per_binary=19,source_processes=2,total_public_requests=36,fixed_argv_file_no_stdin=True))
    semantics={};metrics={};queued={};public_outcomes=[];max_saved_leaf=0.;saved_reconstruct_true=0
    for index,mode in enumerate(('trace','plain')):
        one=FOLDER/mode;work=one/'work';driver=load(one/'driver_protocol.json')
        ck('runtime',mode+' exact copied driver and27 mesh bytes',exact(driver,p['driver_protocol'])and len(p['runtime_meshes_sha256'])==27 and all(sha(work/'simulator'/Path(n).name)==h for n,h in p['runtime_meshes_sha256'].items()))
        stdout=raw(FOLDER/f'process{index}_stdout.bin');stderr=raw(FOLDER/f'process{index}_stderr.bin');rows=[json.loads(x)for x in stdout.splitlines()]
        ck('raw',mode+' exact19 original stdout rows and parsed copy',stdout.endswith(b'\n')and len(rows)==19 and exact(rows,load(one/'parsed_rows.json'))and rows[0]['status']=='SETUP_COMPLETED'and 'request'not in rows[0]and 'result'not in rows[0])
        chunks={'stdout':bytearray(),'stderr':bytearray()};segment_start=next(k for k,x in enumerate(journal)if x is by['source_process_started'][index]);segment_end=next((k for k in range(segment_start+1,len(journal))if journal[k]['event']=='source_process_started'),len(journal))
        for ev in journal[segment_start:segment_end]:
            if ev['event']=='raw_pipe_chunk':chunks[ev['channel']].extend(base64.b64decode(ev['base64'],validate=True))
        ck('raw',mode+' all dualpipe raw journal chunks exact bytes',bytes(chunks['stdout'])==stdout and bytes(chunks['stderr'])==stderr)
        observed_lines=[x for x in journal[segment_start:segment_end]if x['event']=='complete_response_line'];expected_lines=stdout.splitlines(keepends=True)
        ck('raw',mode+' all19 complete response line byte lengths and SHA exact',len(observed_lines)==len(expected_lines)==19 and all(x['bytes']==len(b)and x['sha256']==hashlib.sha256(b).hexdigest()for x,b in zip(observed_lines,expected_lines)))
        records=[];semantic=[];definitions={};previous=Counter()
        for number,row in enumerate(rows):
            records.extend(row['observed_records']);now=Counter(x['kind']for x in records);now['records']=len(records)
            ck('source',mode+' row'+str(number)+' source schema counts/caps no driver RNG/solve',row['schema']=='P4_D080_V_PCS_LOCAL_DRAFT_V1'and row['environment']=='V'and row['trace_enabled']is(mode=='trace')and row['continuous_collision_checked']is False and row['solve_calls']==row['rng_calls']==0 and dict(now)==row['observed_counts_cumulative']and all(v<=p['driver_protocol']['caps'][k]for k,v in now.items())and all(now[k]>=v for k,v in previous.items()))
            previous=now
            if not number:continue
            request=p['driver_protocol']['requests'][number-1];result=row['result'];semantic.append(dict(request=row['request'],result=result,status=row['status']))
            ck('public',mode+' exact original request'+str(number),exact(row['request'],request)and row['status']in('SOURCE_CALL_COMPLETED','NOT_EXECUTED_DEPENDENCY_FAILED'))
            if row['status']=='NOT_EXECUTED_DEPENDENCY_FAILED':
                reason=None
                if isinstance(request.get('branch'),dict):
                    named=request['branch']['from_identify'];indices=definitions[named].get('returned_ik')
                    if indices is None:reason='CENTER_IDENTIFY_NOT_COMPLETED_'+named
                    elif len(indices)!=2 or not isinstance(indices[request['active_chain']],(int,float))or not math.isfinite(indices[request['active_chain']])or not 0<=indices[request['active_chain']]<=7 or indices[request['active_chain']]!=math.floor(indices[request['active_chain']]):reason='CENTER_ROLE_IDENTIFY_FAILED_'+named
                if reason is None and request['op']in('rbs','reconstruct'):
                    for field in('qa_from_project','qb_from_project'):
                        named=request[field]
                        if definitions[named].get('returned')is not True:reason='FROZEN_PROJECT_DEPENDENCY_FAILED_'+named;break
                ck('public',mode+' independently resolved dependency failure no source fallback '+request['id'],reason is not None and result['status']=='NOT_EXECUTED_DEPENDENCY_FAILED'and result['source_call_started']is False and result['reason']==reason and all(x['kind']=='public_request'for x in row['observed_records']))
            elif request['op']=='identify':ck('public',mode+' identify actual saved indices '+request['id'],isinstance(result['returned_ik'],list)and len(result['returned_ik'])==2)
            else:
                branch=request['branch']if isinstance(request['branch'],int)else definitions[request['branch']['from_identify']]['returned_ik'][request['active_chain']]
                ck('public',mode+' fixed original role branch resolved '+request['id'],result['resolved_branch']==branch and type(result['returned'])is bool)
                if request['op']=='project':ck('public',mode+' project saved q12 finite '+request['id'],finiteq(result['q12']))
                else:
                    qa=definitions[request['qa_from_project']];qb=definitions[request['qb_from_project']]
                    ck('public',mode+' exact original projected endpoints '+request['id'],qa['returned']is qb['returned']is True and exact(result['resolved_qa12'],qa['q12'])and exact(result['resolved_qb12'],qb['q12']))
                    if request['op']=='reconstruct':
                        ck('public',mode+' reconstructed saved q array '+request['id'],isinstance(result['path_q12'],list)and len(result['path_q12'])>=2 and all(finiteq(q)for q in result['path_q12']))
                        if result['returned']:
                            leaves=[math.dist(a,b)for a,b in zip(result['path_q12'],result['path_q12'][1:])];max_saved_leaf=max(max_saved_leaf,*leaves);saved_reconstruct_true+=mode=='trace'
            definitions[request['id']]=result
            if mode=='trace':public_outcomes.append(dict(id=request['id'],op=request['op'],status=row['status'],returned=result.get('returned'),returned_ik=result.get('returned_ik'),result=result))
        ck('lifetimes',mode+' full unique monotonic reserved record IDs all completed',len(records)==len({x['id']for x in records})and[x['id']for x in records]==list(range(1,len(records)+1))and all(x['event']=='completed'for x in records)and now['public_request']==18 and now['identify']==2)
        roots=[x for x in records if x['kind']=='public_request'];ck('public',mode+'18 public lifetime args and return exact row semantics',len(roots)==18 and all(exact(x['args'],r['request'])and exact(x['result'],r['result'])for x,r in zip(roots,rows[1:])))
        trace=[json.loads(x[len(MARKER):])for x in stderr.splitlines()if x.startswith(MARKER)]
        ck('trace',mode+' trace markers correct mode',bool(trace)is(mode=='trace'))
        if mode=='trace':
            stack=[];entered={};completed={};nested_ok=True
            for t in trace:
                if t['event']=='entered':stack.append((t['id'],t['kind']));entered[t['id']]=t
                elif t['event']=='completed':
                    nested_ok=bool(stack)and stack.pop()==(t['id'],t['kind'])and nested_ok;completed[t['id']]=t
                else:nested_ok=False
            ck('trace','complete unique nested raw entries/returns no abort or cap; saved records exact',nested_ok and not stack and len(trace)==2*len(records)and len(entered)==len(completed)==len(records)and all(exact(entered[x['id']]['args'],x['args'])and exact(completed[x['id']]['result'],x['result'])and entered[x['id']]['kind']==completed[x['id']]['kind']==x['kind']for x in records))
            for rec in records:
                if rec['kind']in('project_fixed','is_valid_rbs')and rec['result'].get('returned')is True:
                    q=rec['result']['q12'];queued.setdefault(qkey(q),dict(q12=q,source_records=[]))['source_records'].append(rec['id'])
        semantics[mode]=dict(rows=semantic,records=records,counts=dict(now));metrics[mode]=dict(counts=dict(now),records=len(records),stdout_rows=len(rows),stderr_trace_events=len(trace),public_status_counts=dict(Counter(x['status']for x in rows[1:])),public_api_counts=dict(Counter(x['request']['op']for x in rows[1:])),public_returned_true_by_api=dict(Counter(x['request']['op']for x in rows[1:]if x['result'].get('returned')is True)),public_returned_false_by_api=dict(Counter(x['request']['op']for x in rows[1:]if x['result'].get('returned')is False)),public_dependency_not_executed_by_api=dict(Counter(x['request']['op']for x in rows[1:]if x['status']=='NOT_EXECUTED_DEPENDENCY_FAILED')),saved_recursive_rbs_max_depth=max((x['args']['recursion_depth']for x in records if x['kind']=='rbs'),default=None),saved_public_reconstruct_path_node_counts={x['request']['id']:len(x['result'].get('path_q12',[]))for x in rows[1:]if x['request']['op']=='reconstruct'})
    ck('semantics','entire plain/trace source results records counters binary64 exact',exact(semantics['trace'],semantics['plain'])and e['plain_trace_semantics_equal']is True)
    ck('queue','all successful saved source nodes finite q12 without new physical oracle',all(finiteq(x['q12'])for x in queued.values()))
    nodes=load(FOLDER/'independent_nodes_PENDING.json');project_total=sum(x['counts'].get('project_fixed',0)for x in semantics.values())
    ck('queue','all successful source nodes exact dedup pending no oracle',nodes['status']=='NOT_EXECUTED_PENDING_INDEPENDENT_QUALIFICATION'and nodes['new_independent_oracle_calls']==0 and nodes['max_unique_nodes']==256 and len(queued)<=256 and exact(nodes['nodes'],queued)and e['independent_unique_nodes_observed']==len(queued)and project_total==e['internal_and_public_fixed_project_calls']<=512 and e['source_counts_by_mode']=={m:x['counts']for m,x in semantics.items()})
    registry=e['source_process_registry'];ck('lifecycle','two distinct exit0 reaped empty groups and both EOF',len(registry)==2 and len({x['pid']for x in registry})==2 and all(x['returncode']==0 and x['actual_group_after_cleanup']==[]and x['pipe_EOF_observed']==dict(stdout=True,stderr=True)for x in registry))
    for index,mode in enumerate(('trace','plain')):
        start=by['source_process_started'][index];end=by['source_after_reap_group'][index];reg=registry[index]
        ck('lifecycle',mode+'actual fixed argv PID lifetime EOF proof',start['pid']==reg['pid']and start['start_ticks']==reg['start_ticks']==end['start_ticks']and start['command']==[p['build_assets']['targets'][mode]['binary'],str(FOLDER/mode/'work'),str(FOLDER/mode/'driver_protocol.json')]and start['input_transport']=='PREBOUND_FIXED_ARGV_FILE_NO_STDIN'and start['pre_model_loaded_symbol_observation']=='UNOBSERVED_NOT_CLAIMED'and end['returncode']==0 and end['members']==[]and end['actual_pipe_EOF_observed']==dict(stdout=True,stderr=True))
    prior=load(p['prior']['ledger']);ck('prior','unchanged exact prior certificate and sums',sha(p['prior']['ledger'])==p['prior']['ledger_sha256']and e['actual_charge_prior']==e['prior_after']and e['actual_charge_prior']['sha256']==p['prior']['ledger_sha256']and e['actual_charge_prior']['wall_s']==p['prior']['wall_s']==math.fsum(x.get('charged_wall_s',x['wall_s'])for x in prior['executions'])and e['actual_charge_prior']['cpu_s']==p['prior']['cpu_s']==math.fsum(x.get('charged_cpu_s',x['cpu_s'])for x in prior['executions']))
    ext=p['external_supervision'];charge=load(ext['charge_path']);receipt=load(FOLDER/'cost_receipt.json');tb=raw(ext['sibling_path']);fields=tb.decode().split();elapsed,user,system=(Decimal(x)for x in fields[:3])
    walls=[elapsed+Decimal('.01'),Decimal(str(charge['fallback_observed_outer_wait_wall_s']))+Decimal('.01'),Decimal(str(receipt['wall_s_through_execution_persistence']))+Decimal('.01')];cpus=[user+system+Decimal('.02'),Decimal(str(charge['fallback_reaped_children_CPU_s']))+Decimal('.02'),Decimal(str(receipt['cpu_s_through_execution_persistence']))+Decimal('.02')];uw,uc=float(max(walls)),float(max(cpus))
    ck('external','finite one line successful raw time original exit',len(fields)==4 and fields[3]=='0'and tb.endswith(b'\n')and len(tb.splitlines())==1 and all(x.is_finite()and x>=0 for x in(elapsed,user,system,*walls,*cpus)))
    ck('external','original receipt charge time execution hash exact',charge['schema']=='P4_D080_V_PCS_LOCAL_EXTERNAL_COST_CHARGE_V1'and charge['run_id']==RUN and charge['source_execution']==str(epath.relative_to(ROOT))and charge['execution_sha256']==receipt['execution_sha256']==sha(epath)and charge['receipt_sha256']==sha(FOLDER/'cost_receipt.json')and charge['time_sha256']==sha(ext['sibling_path'])and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr_sha256']==sha(ext['stderr_path'])and charge['time_fields']==fields and receipt['status']==e['status'])
    ck('external','exact Decimal conservative three observation components basis limits',charge['charge_basis']==e['new_external_charge_basis']==BASIS and charge['monotonic_envelope_valid']is True and charge['monotonic_envelope_error']is None and charge['raw_GNUtime_upper_wall_s']==float(elapsed+Decimal('.01'))and charge['raw_GNUtime_upper_cpu_s']==float(user+system+Decimal('.02'))and charge['monotonic_envelope_components']==dict(wall_decimal_s=[str(x)for x in walls],cpu_decimal_s=[str(x)for x in cpus],order=['raw_GNUtime_plus_padding','outer_monotonic_or_reaped_plus_padding','internal_receipt_plus_padding'])and exact([charge['wall_s'],charge['cpu_s']],[uw,uc])and 0<=e['wall_s']<=receipt['wall_s_through_execution_persistence']<=uw<=min(30,3600-p['prior']['wall_s'])and 0<=e['cpu_s']<=receipt['cpu_s_through_execution_persistence']<=uc<=min(60,7200-p['prior']['cpu_s']))
    ck('external','complete exit0 successful charge no automatic qualification',charge['timing_valid']is charge['time_inode_unchanged']is charge['wall_CPU_caps_pass']is charge['completed_process_exit0']is charge['started_attempt']is True and charge['time_returncode']==charge['measured_child_exit']==0 and charge['failure']is None and charge['execution_cap_breach']==dict(wall=False,cpu=False)and receipt['external_supervision_qualified']is charge['external_supervision_qualified']is False)
    meta=raw(ext['metadata_path']);planned,started,reaped=[json.loads(x)for x in meta.splitlines()];proof=e['supervisor_launch_proof'];inode=path(ext['sibling_path']).stat();argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/RUNNER),'--protocol',str(protocol)]
    ck('external','actual source supervisor GNUtime argv PID launch/reap inode identity',planned['argv']==started['argv']==proof['actual_argv']==argv and planned['event']=='planned_launch'and started['event']=='time_process_started'and reaped['event']=='time_process_reaped'and started['pid']==reaped['pid']==proof['time_pid']==charge['time_process_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid']and planned['time_inode']==inode.st_ino and planned['time_device']==inode.st_dev and planned['time_fd']in proof['held_time_fds']and proof['time_start_ticks']>0 and proof['launch_line_sha256']==hashlib.sha256(meta.splitlines(keepends=True)[0]).hexdigest())
    ck('external','frozen runner protocol supervisor binaries actual hashes',planned['run_id']==RUN and planned['protocol_sha256']==sha(protocol)and planned['runner_sha256']==sha(RUNNER)and planned['supervisor_source_sha256']==sha(SUPERVISOR)and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
    ck('scope','formal VI planner solve0 and independent physical unqualified',e['formal_table_I_calls']==e['solve_calls']==e['new_VI_candidate_constructions']==0 and p['formal_execution_authorized']is False and all(x['counts'].get('public_request')==18 for x in semantics.values()))
    for n,h in list(retained.items()):
        if hashlib.sha256(path(n).read_bytes()).hexdigest()!=h:ck('preservation','all saved final bytes retained '+n,False)
    return dict(source_commit=e['source_commit'],execution=str(epath.relative_to(ROOT)),execution_sha256=sha(epath),protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),external_time=ext['sibling_path'],external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),internal_receipt_sha256=sha(FOLDER/'cost_receipt.json'),charge_basis=BASIS,upper_wall_s=uw,upper_cpu_s=uc,wall_components_decimal_s=[str(x)for x in walls],cpu_components_decimal_s=[str(x)for x in cpus],cumulative_charged_wall_s=math.fsum((p['prior']['wall_s'],uw)),cumulative_charged_cpu_s=math.fsum((p['prior']['cpu_s'],uc)),reused_build_POST=BUILD,reused_build_POST_sha256=BUILD_SHA,source_metrics_by_mode=metrics,public_outcomes_trace=public_outcomes,unique_successful_source_nodes_pending=len(queued),successful_reconstruct_calls_trace=saved_reconstruct_true,maximum_saved_successful_reconstruct_leaf_rad=max_saved_leaf,physical_qualification_queue=str((FOLDER/'independent_nodes_PENDING.json').relative_to(ROOT)),physical_qualification_queue_sha256=sha(FOLDER/'independent_nodes_PENDING.json'),source_local_transport_qualified=True,source_plain_trace_semantics_qualified=True,independent_local_qualified=False,independent_path_qualified=False,continuous_collision_certificate=False)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--protocol',required=True);ap.add_argument('--protocol-sha256',required=True);ap.add_argument('--expected-source-commit',required=True);args=ap.parse_args()
    if OUT.exists()or OUT.with_suffix('.md').exists():raise FileExistsError('EXCLUSIVE_LOCAL_POST_NO_OVERWRITE')
    details={}
    try:details=audit(args)
    except BaseException as exc:ck('audit_completion','complete saved audit without structural exception '+repr(exc),False)
    failures=[x for x in checks if not x['passed']];ok=not failures
    cost=[x for x in checks if x['group']=='external'];costok=bool(cost)and all(x['passed']for x in cost)
    report=dict(schema='P4_D080_V_PCS_LOCAL01_SAVED_INDEPENDENT_POST_V1',status='PASS_LOCAL_SOURCE_TRANSPORT_SEMANTICS_ONLY_PENDING_PHYSICAL_POST'if ok else'FAIL_LOCAL_SAVED_POST',generated_at_utc=datetime.now(timezone.utc).isoformat(),personnel_independent=True,reviewer='/root/sbl_independent_resume independent of V local implementation',checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),checks=checks,failures=failures,external_supervision_qualified=costok,external_timing_qualified=costok,completed_process_exit0=costok,**details,retained_sha256=retained,new_runner_model_import_transform_compile_binary_FK_J_IK_NR_PQP_RBS_solve_RNG_protocol_prior_claim_VI_formal_calls=0,limits=['Source observation, transport and plain/trace semantics only; no independent Comau physical oracle run.','False source returns and dependency-not-executed rows are retained; transport PASS is not local mathematical/collision/path qualification.','Successful projection/internal nodes are only queued for future independent closure/branch/limits/87-pair collision and strict leaf qualification under separately frozen budget.','Native/aligned mismatch, reconstructed A02 endpoints and original BUILD01 failure/old object hashes UNKNOWN remain distinct.','No continuous collision, planner solve, global path, formal statistics or PCS advantage claim; VI archival, formal18000 unapproved.','Three-observation conservative whole-child cost excludes supervisor own final journal/fsync tail.'])
    # A saved transport/source-semantic PASS never grants Comau physical or
    # planner/path qualification; a partial/failed review grants neither.
    report['source_transport_qualified']=ok
    report['source_local_transport_qualified']=ok
    report['source_plain_trace_semantics_qualified']=ok
    report['independent_local_qualified']=False
    report['independent_path_qualified']=False
    report['continuous_collision_certificate']=False
    report['full_bound_union_rehash_calls']=0
    report['prior_219_scientific_source_and_87_pair_physical_policy_rereviews']=0
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write('# V LOCAL01 保存证据独立后审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'。\n\n只读36public/38stdout、原trace/返回/依赖false、两进程EOF/清理、plain-trace完整语义与三观测费用；新FK/IK/碰撞/规划/编译调用0。物理局部及路径资格仍false，成功source节点只排队独立资格。\n')
    print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures),failures=failures),ensure_ascii=False))
    if failures:raise SystemExit(2)

if __name__=='__main__':main()
