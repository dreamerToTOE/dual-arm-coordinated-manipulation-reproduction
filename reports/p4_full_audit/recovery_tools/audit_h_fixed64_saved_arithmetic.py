#!/usr/bin/env python3
"""H fixed64 saved arithmetic POST, not personnel-independent verification.

Reviewer contributed runner logging/prior metadata fixes. No scientific module
is imported, no process or binary is executed, and no model is evaluated.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'results/p4_full/20261015_R2_ABB_RANDOM_HELPER_H01'
OUT=ROOT/'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_FIXED64_SAVED_ARITHMETIC_POST_20261016'
CHECKS=[]


def path(p):
    p=Path(p);return p if p.is_absolute() else ROOT/p


def load(p):return json.loads(path(p).read_text())
def sha(p):return hashlib.sha256(path(p).read_bytes()).hexdigest()


def canonical(v):
    if isinstance(v,float):return ['binary64',struct.pack('>d',v).hex()]
    if isinstance(v,list):return [canonical(x)for x in v]
    if isinstance(v,dict):return {k:canonical(x)for k,x in v.items()}
    return v


def fp(v):return hashlib.sha256(json.dumps(canonical(v),sort_keys=True,separators=(',',':')).encode()).hexdigest()


def check(n,b,**evidence):CHECKS.append(dict(check=n,passed=bool(b),**evidence))
def same(n,a,b):check(n,fp(a)==fp(b),actual_sha256=fp(a),expected_sha256=fp(b))
def bits(q):return struct.pack('>'+str(len(q))+'d',*q).hex()


def close(a,b,tol):return abs(a-b)<=tol


def prefix_events(p):
    events=[];tails=[]
    for n,line in enumerate(path(p).read_bytes().splitlines(keepends=True),1):
        marker=b'P4_HELPER_TRACE '
        if marker not in line:continue
        payload=line.split(marker,1)[1]
        try:events.append(json.loads(payload))
        except (ValueError,UnicodeDecodeError):tails.append(dict(line1=n,sha256=hashlib.sha256(payload).hexdigest(),status='INCOMPLETE_OR_UNPARSEABLE_SOURCE_PREFIX'))
    return dict(events=events,tails=tails)


def observe(events,label):
    started=Counter();completed=Counter();marks=Counter();stack=[];serial=0;shuffle=[];branches=[];identifies=[]
    for ev in events:
        if ev['event']in ('entered','observed'):
            same(label+'.serial.'+str(ev['id']),ev['id'],serial+1);serial=ev['id']
        if ev['event']=='entered':started[ev['kind']]+=1;stack.append((ev['id'],ev['kind']))
        elif ev['event']=='completed':
            check(label+'.completion_LIFO.'+str(ev['id']),bool(stack)and stack.pop()==(ev['id'],ev['kind']));completed[ev['kind']]+=1
        elif ev['event']=='observed':
            marks[ev['kind']]+=1
            if ev['kind']=='shuffle_completed':shuffle.append(ev)
            elif ev['kind']=='branch_entered':branches.append(ev)
            elif ev['kind']=='identify_completed_in_helper':identifies.append(ev)
        else:check(label+'.valid_event',False)
    same(label+'.all_calls_returned',stack,[])
    same(label+'.started_completed',dict(started),dict(completed))
    same(label+'.one_helper',started['helper_three'],1)
    same(label+'.no_source_collision_query',started['collision'],0)
    same(label+'.one_shuffle',len(shuffle),1)
    same(label+'.shuffle_permutation',sorted(shuffle[0]['args']['order']),list(range(8)))
    for n,b in enumerate(branches):same(label+'.loop_order.'+str(n),(b['args']['loop_index'],b['args']['branch']),(n,shuffle[0]['args']['order'][n]))
    return dict(started=started,completed=completed,marks=marks,branches=branches,identifies=identifies)


def branch_set(q):
    # Pure arithmetic of saved joint angles, no FK/IK calls or scientific imports.
    alpha=math.atan2(302.,70.);radius=270.*math.sin(q[1])+70.*math.sin(q[1]+q[2])+302.*math.cos(q[1]+q[2])
    factors=(radius,-math.sin(q[2]+alpha),math.sin(q[4]));scales=(270.+math.hypot(70.,302.),1.,1.)
    signs=[None if abs(v)<=64*math.ulp(1.)*s else (1 if v>0 else -1)for v,s in zip(factors,scales)]
    elbow=(1,-1,1,-1,1,-1,1,-1);wrist=(1,-1,-1,1,-1,1,1,-1)
    return [b for b in range(8)if (signs[0]is None or (1 if b<4 else -1)==signs[0])and(signs[1]is None or elbow[b]==signs[1])and(signs[2]is None or wrist[b]==signs[2])]


def audit():
    e=load(RUN/'execution.json');p=load(e['protocol']);claim=load(e['claim'])
    same('frozen',p['frozen'],True);check('all_reviews',all(v is True for v in p['reviews'].values()))
    same('protocol_hash',sha(e['protocol']),e['protocol_sha256'])
    same('protocol_unchanged',e['protocol_sha256'],e['protocol_after_sha256'])
    same('claim_hash',sha(e['claim']),e['claim_sha256']);same('claim_unchanged',e['claim_sha256'],e['claim_after_sha256'])
    same('claim_source_commit',claim['source_commit'],e['source_commit'])
    same('bound_before_protocol',e['bound_files_sha256'],p['bound_files_sha256'])
    same('bound_before_after',e['bound_files_sha256'],e['bound_files_after_sha256'])
    for n,want in e['bound_files_sha256'].items():same('bound_hash.'+n,sha(n),want)
    same('prior26',len(e['prior_execution_sha256']),26)
    same('prior_matches_protocol',e['prior_execution_sha256'],p['prior_execution_sha256'])
    rows=[]
    for n,want in e['prior_execution_sha256'].items():same('prior_hash.'+n,sha(n),want);rows.append(load(n))
    same('prior_own_wall_once',e['previous_r2_wall_s'],math.fsum(r['wall_s']for r in rows))
    same('prior_own_CPU_once',e['previous_r2_cpu_s'],math.fsum(r['cpu_s']for r in rows))
    same('frozen_wall_limit',e['budget']['wall_s'],60.)
    same('frozen_CPU_limit',e['budget']['cpu_s'],120.)
    check('reported_costs_finite_positive',all(math.isfinite(e[k]) and e[k]>0 for k in ('wall_s','cpu_s')))
    budget_exceeded={k:e[k]>=e['budget'][k] for k in ('wall_s','cpu_s')}
    if e['status'].startswith('PASS_'):
        check('PASS_requires_within_both_caps',not any(budget_exceeded.values()))
    elif any(budget_exceeded.values()):
        check('budget_exceeded_requires_STOP',e['status'].startswith('STOP_'))
        if budget_exceeded['wall_s']:
            same('wall_cap_reason_retained',e['termination_reason'],"TimeoutError('H_AGGREGATE_HARD_WALL_CAP')")
    same('fixed_schedule64',len(p['fixed_schedule']),64);same('fixed_contexts16',len(p['fixed_contexts']),16)
    schedule=p['fixed_schedule'];responses={};completed=[];trace_started=Counter();trace_completed=Counter();marks=Counter()
    for fixture in schedule:
        i=fixture['dispatch_index'];request={k:fixture[k]for k in ('case_id','operation','environment','q12','active_chain','seed')}
        request_file=RUN/f'helper_{i:03d}_request.json'
        if request_file.exists():same(f'helper{i}.request',load(request_file),request)
        file=RUN/f'helper_{i:03d}_raw_response.json'
        if not file.exists():continue
        response=load(file);raw=(RUN/f'helper_{i:03d}_raw_response_line.bin').read_bytes()
        same(f'helper{i}.raw_binary_line',json.loads(raw),response)
        same(f'helper{i}.request_response',response['request'],request)
        same(f'helper{i}.source_status',response['status'],'SOURCE_HELPER_COMPLETED')
        same(f'helper{i}.srand_once',response['srand_calls_completed'],1)
        same(f'helper{i}.dispatch_started',response['helper_dispatch_started'],1)
        same(f'helper{i}.dispatch_completed',response['helper_dispatch_completed'],1)
        same(f'helper{i}.rand_unobserved',response['rand_started_completed'],'UNOBSERVED_SOURCE_STDLIB_NOT_INFERRED')
        same(f'helper{i}.no_post_helper_model',response['post_helper_model_calls'],0)
        a=slice(fixture['active_chain']*6,(fixture['active_chain']+1)*6)
        same(f'helper{i}.active_bits',bits(response['q12'][a]),bits(fixture['q12'][a]))
        if fixture['factor']=='source_control':same(f'helper{i}.original_source_bool',response['returned'],False)
        if fixture['mode']=='trace':
            obs=observe(response['trace'],f'helper{i}')
            same(f'helper{i}.actual_started',dict(obs['started']),response['source_started']);same(f'helper{i}.actual_completed',dict(obs['completed']),response['source_completed'])
            trace_started.update(obs['started']);trace_completed.update(obs['completed']);marks.update(obs['marks'])
            same(f'helper{i}.top_final_q',response['trace'][-1]['result']['q1']+response['trace'][-1]['result']['q2'],response['q12'])
            same(f'helper{i}.top_final_bool',response['trace'][-1]['result']['returned'],response['returned'])
        else:
            same(f'helper{i}.plain_UNOBSERVED',[response['source_started'],response['source_completed'],response['trace']],[None,None,None])
        responses[(fixture['factor'],fixture['mode'],fixture['case_id'])]=response;completed.append(i)
    same('completed_helpers_record',e['completed_helper_ids'],completed)
    comparisons=[];prefixes=[]
    for factor in ('source_control','success_break'):
        for context in p['fixed_contexts']:
            case=context['case_id'];plain=responses.get((factor,'plain',case));trace=responses.get((factor,'trace',case))
            if plain is None or trace is None:continue
            normalize=lambda r:{k:v for k,v in r.items()if k not in ('mode','source_counts_observed','source_started','source_completed','trace')}
            same('pair.'+factor+'.'+case,normalize(plain),normalize(trace));comparisons.append((factor,case))
    for context in p['fixed_contexts']:
        case=context['case_id'];original=responses.get(('source_control','trace',case));fixed=responses.get(('success_break','trace',case))
        if original is None or fixed is None:continue
        ot=original['trace'];ft=fixed['trace'];success=[(n,v)for n,v in enumerate(ot)if v['event']=='observed'and v['kind']=='identify_completed_in_helper'and all(label!=-1 for label in v['args']['ik'])]
        if success:
            stop,first=success[0];same('prefix.'+case+'.first_success',ot[:stop+1],ft[:-1]);same('prefix.'+case+'.break_bool',fixed['returned'],True)
            same('prefix.'+case+'.first_candidate',first['args']['q1']+first['args']['q2'],fixed['q12'])
        else:same('prefix.'+case+'.no_success_trace',ot,ft);same('prefix.'+case+'.no_success_final',original['q12'],fixed['q12'])
        prefixes.append(case)
    same('pair_completed_count',e['plain_trace_comparison_cases'],len(comparisons));same('prefix_completed_count',e['control_prefix_comparison_cases'],len(prefixes))
    bounds=[(lo*3.1416/180,hi*3.1416/180)for lo,hi in [(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]]*2
    math_ids=[]
    for fixture in schedule:
        i=fixture['dispatch_index'];file=RUN/f'final_{i:03d}_math.json'
        if not file.exists():continue
        r=load(file);math_ids.append(i);q=r['q12'];t1,t2=r['poses'];length=300. if r['environment']=='II'else 500.
        same(f'math{i}.stage',r['stage'],'MATH_COMPLETED')
        same(f'math{i}.source_q',q,responses[(fixture['factor'],fixture['mode'],fixture['case_id'])]['q12'])
        same(f'math{i}.source_bool',r['source_returned'],responses[(fixture['factor'],fixture['mode'],fixture['case_id'])]['returned'])
        pe=max(abs(t2[j][3]-(t1[j][3]+length*t1[j][0]))for j in range(3))
        re=max(abs(t2[j][k]-t1[j][k]*(-1 if k<2 else 1))for j in range(3)for k in range(3))
        check(f'math{i}.closure_position_replay',close(pe,r['closure']['position_max_abs'],2e-12))
        check(f'math{i}.closure_rotation_replay',close(re,r['closure']['rotation_matrix_max_abs'],1e-15))
        same(f'math{i}.closed',r['closed'],pe<=1e-5 and re<=1e-5)
        same(f'math{i}.limits',r['limits']['legal'],all(lo<=v<=hi for v,(lo,hi)in zip(q,bounds)))
        for arm in (1,2):
            saved_arm=load(RUN/f'final_{i:03d}_arm{arm}.json')
            same(f'math{i}.arm{arm}.q',saved_arm['q12'],q)
            same(f'math{i}.arm{arm}.poses',saved_arm['poses'],r['poses'][:arm])
            same(f'math{i}.arm{arm}.branch_set',r['branches'][arm-1]['branch_set'],branch_set(q[6*(arm-1):6*arm]))
        active=slice(6*fixture['active_chain'],6*(fixture['active_chain']+1))
        same(f'math{i}.active_preserved',r['active_input_unchanged'],bits(q[active])==bits(fixture['q12'][active]))
    final=[];max_pos=0.;max_rot=0.;query_counts=Counter();physical_counts=Counter()
    for fixture in schedule:
        i=fixture['dispatch_index'];file=RUN/f'final_{i:03d}.json'
        if not file.exists():continue
        r=load(file);final.append(r);q=r['q12'];env=r['environment'];length=300. if env=='II'else 500.;t1,t2=r['poses']
        same(f'final{i}.source_q',q,responses[(fixture['factor'],fixture['mode'],fixture['case_id'])]['q12'])
        pe=max(abs(t2[j][3]-(t1[j][3]+length*t1[j][0]))for j in range(3))
        re=max(abs(t2[j][k]-t1[j][k]*(-1 if k<2 else 1))for j in range(3)for k in range(3))
        check(f'final{i}.position_saved_arithmetic',close(pe,r['closure']['position_max_abs'],2e-12),actual=pe,saved=r['closure']['position_max_abs'])
        check(f'final{i}.rotation_saved_arithmetic',close(re,r['closure']['rotation_matrix_max_abs'],1e-15),actual=re,saved=r['closure']['rotation_matrix_max_abs'])
        max_pos=max(max_pos,pe);max_rot=max(max_rot,re);closed=pe<=1e-5 and re<=1e-5
        same(f'final{i}.closed_replay',r['closed'],closed)
        legal=all(lo<=v<=hi for v,(lo,hi)in zip(q,bounds));same(f'final{i}.source_bounds',r['limits']['legal'],legal)
        sets=[branch_set(q[:6]),branch_set(q[6:])]
        for arm in (0,1):same(f'final{i}.geometry_branch_set.{arm}',r['branches'][arm]['branch_set'],sets[arm])
        direct=r['source_identity']['direct_branch'];labels=r['source_identity']['source_identify_ik'];passive=1-fixture['active_chain']
        direct_ok=None if direct is None else direct in sets[passive]
        dual_ok=None if labels is None else all(label in range(8)and label in sets[1-n]for n,label in enumerate(labels))
        same(f'final{i}.direct_label_replay',r['direct_branch_membership'],direct_ok);same(f'final{i}.dual_label_replay',r['dual_source_label_membership'],dual_ok)
        source_trace=responses[(fixture['factor'],'trace',fixture['case_id'])]['trace'];matching=[v['args']for v in source_trace if v['event']=='observed'and v['kind']=='identify_completed_in_helper'and bits(v['args']['q1']+v['args']['q2'])==bits(q)]
        same(f'final{i}.source_labels_from_saved_observation',r['source_identity']['source_identify_ik'],matching[-1]['ik']if matching else None)
        collision=load(RUN/f'final_{i:03d}_collision_raw_response.json');same(f'final{i}.collision_raw',collision,r['collision']);same(f'final{i}.aligned_selected',collision['selected_variant'],'aligned');same(f'final{i}.collision_CHECKED',collision['status'],'CHECKED')
        same(f'final{i}.no_CCD',collision['continuous_collision_certificate'],False)
        for variant,row in collision['variants'].items():
            raw=[json.loads(line.split(' ',1)[1])for line in row['source_stdout'].splitlines()if line.startswith('P4_COLLISION_RESULT ')]
            same(f'final{i}.{variant}.single_raw',len(raw),1);same(f'final{i}.{variant}.raw_values',raw[0],{k:row[k]for k in raw[0]})
            same(f'final{i}.{variant}.query_errors',[code for code in row['query_codes']if code!=0],[]);query_counts[variant]+=len(row['query_codes'])
            if variant=='aligned':same(f'final{i}.aligned_pose_gate',row['pose_consistency']['passed'],True)
        active=bits(q[6*fixture['active_chain']:6*(fixture['active_chain']+1)])==bits(fixture['q12'][6*fixture['active_chain']:6*(fixture['active_chain']+1)])
        collision_free=not collision['collision'];physical_ok=bool(closed and legal and active and collision_free);all_ok=bool(physical_ok and direct_ok is True and dual_ok is True)
        same(f'final{i}.physical_gate_separate',r['physical_final_qualified'],physical_ok)
        same(f'final{i}.all_gate_separate',r['final_candidate_all_gates_qualified'],all_ok)
        same(f'final{i}.source_success_gate_separate',r['source_success_fully_qualified'],bool(r['source_returned']and all_ok))
        for name,value in [('source_true',r['source_returned']),('physical_qualified',physical_ok),('all_qualified',all_ok),('source_success_qualified',r['source_returned']and all_ok),('limits_rejected',not legal),('collision_rejected',not collision_free),('closure_rejected',not closed)]:physical_counts[name]+=bool(value)
    same('completed_final_ids',e['completed_final_ids'],[r['dispatch_index']for r in final])
    same('saved_final_summary',load(RUN/'independent_final_summary.json'),final)
    # Event-to-file accounting preserves the distinct completion layers. Native
    # worker completion is not equivalent to an aligned adapter/final gate.
    event_rows=[json.loads(line)for line in (RUN/'events.jsonl').read_text().splitlines()]
    event_counts=Counter(row['event']for row in event_rows)
    event_links={'helper_dispatch_started':'helper_dispatch_attempted','helper_response_line_observed':'helper_response_lines_retained',
        'helper_completed':'helper_completed','final_metric_started':'independent_final_metric_started',
        'final_metric_completed':'independent_final_metric_completed','math_arm_FK_started':'math_arm_FK_started',
        'math_arm_FK_completed':'math_arm_FK_completed','collision_started':'collision_adapter_started',
        'collision_native_worker_query_started':'collision_native_worker_dispatch_attempted',
        'collision_native_worker_query_completed':'collision_native_worker_query_completed',
        'adapter_arm_FK_J_started':'adapter_internal_arm_FK_J_started',
        'adapter_arm_FK_J_completed':'adapter_internal_arm_FK_J_completed'}
    for event_name,count_name in event_links.items():same('event_count.'+event_name,event_counts[event_name],e['counts'][count_name])
    same('math_completed_event_ids',math_ids,[row['dispatch_index']for row in event_rows if row['event']=='final_metric_completed'])
    same('math_completed_count',len(math_ids),e['counts']['independent_final_metric_completed'])
    same('final_completed_event_ids',[r['dispatch_index']for r in final],[row['dispatch_index']for row in event_rows if row['event']=='final_gate_completed'])
    starts={row['query_index']:row for row in event_rows if row['event']=='collision_native_worker_query_started'}
    worker_files=sorted(RUN.glob('collision_worker_*_raw_response.json'));worker_queries=Counter()
    same('worker_raw_count',len(worker_files),e['counts']['collision_native_worker_raw_response_retained'])
    same('worker_completed_indexes',sorted(starts),[row['query_index']for row in event_rows if row['event']=='collision_native_worker_query_completed'])
    for file in worker_files:
        j=int(file.name.split('_')[2]);r=load(file);ev=starts[j];i=j//2;variant='native' if j%2==0 else 'aligned'
        fixture=schedule[i];response=responses[(fixture['factor'],fixture['mode'],fixture['case_id'])]
        same(f'worker{j}.q_matches_saved_candidate',ev['q12'],response['q12'])
        same(f'worker{j}.command',r['source_command'],ev['command'])
        check(f'worker{j}.variant',('/abb_'+variant+'/') in r['source_command'][0])
        raw=[json.loads(line.split(' ',1)[1])for line in r['source_stdout'].splitlines()if line.startswith('P4_COLLISION_RESULT ')]
        same(f'worker{j}.single_raw_result',len(raw),1)
        same(f'worker{j}.raw_values',raw[0],{k:r[k]for k in raw[0]})
        same(f'worker{j}.PQP_query_errors',[code for code in r['query_codes']if code!=0],[])
        worker_queries[variant]+=len(r['query_codes'])
        adapter_file=RUN/f'final_{i:03d}_collision_raw_response.json'
        if adapter_file.exists():
            returned_variant=load(adapter_file)['variants'].get(variant)
            if returned_variant is not None:same(f'worker{j}.adapter_returned_subset',r,{k:returned_variant[k]for k in r})
    adapter_files=sorted(RUN.glob('final_*_collision_raw_response.json'))
    same('adapter_raw_count',len(adapter_files),e['counts']['collision_adapter_completed'])
    partial_ids=[i for i in math_ids if i not in e['completed_final_ids']]
    partial=[]
    for i in partial_ids:
        r=load(RUN/f'final_{i:03d}_collision_raw_response.json')
        check(f'partial{i}.not_complete_final',not (RUN/f'final_{i:03d}.json').exists())
        same(f'partial{i}.adapter_status',r['status'],'COLLISION_ADAPTER_ERROR')
        same(f'partial{i}.collision_UNRESOLVED',r['collision'],None)
        same(f'partial{i}.termination_reason',r['error'],e['termination_reason'])
        partial.append(dict(dispatch_index=i,math_status='COMPLETED',adapter_status=r['status'],
            adapter_returned_variants=list(r['variants']),raw_native_worker_retained=(RUN/f'collision_worker_{2*i:03d}_raw_response.json').exists(),
            raw_aligned_worker_retained=(RUN/f'collision_worker_{2*i+1:03d}_raw_response.json').exists(),
            full_final_status='UNKNOWN_NOT_COMPLETED',adapter_raw_sha256=sha(RUN/f'final_{i:03d}_collision_raw_response.json')))
    if partial_ids:
        stopped=load(RUN/'stopped_partial_candidate.json')
        same('stopped_partial_id',stopped['dispatch_index'],partial_ids[-1])
        saved_math=load(RUN/f"final_{stopped['dispatch_index']:03d}_math.json")
        same('stopped_partial_saved_math_values',{k:v for k,v in stopped.items()if k!='stage'},
            {k:v for k,v in saved_math.items()if k!='stage'})
        same('stopped_partial_original_stage',stopped['stage'],'COLLISION_STARTED')
    json_inventory=[]
    for file in sorted(RUN.rglob('*.json')):
        blob=file.read_bytes();parsed=True
        try:json.loads(blob)
        except (ValueError,UnicodeDecodeError):parsed=False
        check('saved_JSON_parse.'+str(file.relative_to(RUN)),parsed)
        json_inventory.append(dict(path=str(file.relative_to(RUN)),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),parseable=parsed))
    def stamp(row):return datetime.fromisoformat(row['at_utc'])
    times=[stamp(row)for row in event_rows]
    check('UTC_event_order_nonnegative',all(b>=a for a,b in zip(times,times[1:])))
    def endpoints(kind):return [row for row in event_rows if row['event']==kind]
    def duration(a,b):return (stamp(b)-stamp(a)).total_seconds()
    # These are UTC event-bracket intervals; each includes whichever budget
    # checks, persistence and validation occur between the two recorded events.
    helper_starts=endpoints('helper_dispatch_started');helper_seen=endpoints('helper_response_line_observed');helper_done=endpoints('helper_completed')
    worker_starts=endpoints('collision_native_worker_query_started');worker_done=endpoints('collision_native_worker_query_completed')
    adapter_starts=endpoints('adapter_arm_FK_J_started');adapter_done=endpoints('adapter_arm_FK_J_completed')
    final_starts=endpoints('final_metric_started');final_done=endpoints('final_gate_completed');stops=endpoints('stopped')
    timing=dict(scope='SAVED_UTC_EVENT_BRACKETS_NOT_EXCLUSIVE_KERNEL_OR_FSYNC_TIMINGS',
        first_helper_to_last_helper_s=duration(helper_starts[0],helper_done[-1]),
        helper_dispatch_to_response_observed_sum_s=math.fsum(duration(a,b)for a,b in zip(helper_starts,helper_seen)),
        helper_observed_to_completion_sum_s=math.fsum(duration(a,b)for a,b in zip(helper_seen,helper_done)),
        last_helper_to_first_final_metric_s=duration(helper_done[-1],final_starts[0]),
        first_final_metric_to_STOP_s=duration(final_starts[0],stops[-1]),
        first_final_metric_to_last_full_final_s=duration(final_starts[0],final_done[-1]),
        native_worker_query_event_brackets_sum_s=math.fsum(duration(a,b)for a,b in zip(worker_starts,worker_done)),
        native_worker_reported_transport_wall_sum_s=math.fsum(load(f)['wall_s']for f in worker_files),
        native_worker_reported_kernel_CPU_sum_s=math.fsum(load(f)['cpu_s']for f in worker_files),
        adapter_FK_J_event_brackets_sum_s=math.fsum(duration(a,b)for a,b in zip(adapter_starts,adapter_done)),
        fsync_per_call_duration_observed=False,budget_check_per_call_duration_observed=False,
        causal_limit='Saved data identify aggregate wall exhaustion and the interrupted aligned pose check; they do not isolate fsync, /proc CPU accounting, serialization, polling, or numerical computation as the sole cause.',
        static_runner_sha256=sha('scripts/qualify_p4_full_r2_abb_random_helper_h_draft.py'),
        static_durable_new='JSON serialization, flush and os.fsync occur before durable_new returns; raw helper line also flushes and fsyncs.',
        static_budget_check='Budget.check reads monotonic wall and cpu_total; SIGALRM checks every 0.02 seconds; no per-call accounting durations retained.')
    stream_started=Counter();stream_completed=Counter();stream_marks=Counter();saved_prefix=load(RUN/'source_trace_prefixes_saved.json')
    for label,expected in saved_prefix.items():
        factor,mode,env=label.split('/');raw=prefix_events(RUN/'runtime'/f'{factor}_{mode}_{env}.stderr');same('raw_stream.'+label,raw,expected)
        response_trace=[]
        for fixture in schedule:
            if(fixture['factor'],fixture['mode'],fixture['environment'])==(factor,mode,env):
                response=responses.get((factor,mode,fixture['case_id']))
                if response is not None and mode=='trace':response_trace.extend(response['trace'])
        gate=e['source_raw_trace_bindings'][label]
        same('raw_stream_response_binding.'+label,fp(raw['events'])==fp(response_trace),gate['raw_trace_equals_completed_responses_binary64'])
        same('raw_stream_parse_tails.'+label,len(raw['tails']),gate['unparseable_trace_tail_count'])
        if e['status'].startswith('PASS_'):
            same('raw_stream_complete_gate.'+label,gate['complete_raw_evidence_gate'],True)
            same('raw_pipe_EOF.'+label,gate['pipe_eof_drained'],True);same('raw_stdout_empty.'+label,gate['unexpected_stdout_tail_bytes'],0)
        for ev in raw['events']:
            if ev['event']=='entered':stream_started[ev['kind']]+=1
            elif ev['event']=='completed':stream_completed[ev['kind']]+=1
            else:stream_marks[ev['kind']]+=1
    same('actual_raw_stream_started',dict(stream_started),e['source_trace_stream_observed']['started']);same('actual_raw_stream_completed',dict(stream_completed),e['source_trace_stream_observed']['completed']);same('actual_raw_stream_marks',dict(stream_marks),e['source_trace_stream_observed']['marks'])
    same('complete_raw_binding_count',len(e['source_raw_trace_bindings']),len(saved_prefix))
    same('aggregate_raw_evidence_gate',e['complete_source_raw_evidence_gate'],all(row['complete_raw_evidence_gate']for row in e['source_raw_trace_bindings'].values()))
    counts=e['counts']
    same('actual_helper_completed',counts['helper_completed'],len(completed))
    same('actual_source_true',e['source_true_count'],sum(r['returned']for r in responses.values()))
    same('actual_source_false',e['source_false_count'],sum(not r['returned']for r in responses.values()))
    for kind,value in trace_started.items():same('actual_trace_started.'+kind,counts['trace_'+kind+'_started'],value)
    for kind,value in trace_completed.items():same('actual_trace_completed.'+kind,counts['trace_'+kind+'_completed'],value)
    for variant,n in query_counts.items():same('actual_final_PQP.'+variant,counts[variant+'_PQP_queries_returned'],n)
    for saved_key,replay_key in [('physical_final_qualified','physical_qualified'),('final_candidate_all_gates_qualified','all_qualified'),('source_success_fully_qualified','source_success_qualified')]:same('full_final_count.'+saved_key,e[saved_key],physical_counts[replay_key])
    unknown=load(RUN/'unknown_tail.json');same('unknown_helper_full_tail',unknown['helper'],[f for f in schedule if f['dispatch_index']not in completed]);same('unknown_final_full_tail',unknown['final'],[f for f in schedule if f['dispatch_index']not in [r['dispatch_index']for r in final]])
    if e['status'].startswith('PASS_'):
        same('PASS_requires_64helpers',len(completed),64);same('PASS_requires_32pairs',len(comparisons),32);same('PASS_requires_16prefixes',len(prefixes),16);same('PASS_requires_64finals',len(final),64);same('PASS_requires_no_diag',e['diagnostics'],[])
    return dict(execution_status=e['status'],execution_sha256=sha(RUN/'execution.json'),source_commit=e['source_commit'],wall_s=e['wall_s'],cpu_s=e['cpu_s'],budget_exceeded=budget_exceeded,qualification_pass=False if not e['status'].startswith('PASS_') else True,
        termination_reason=e.get('termination_reason'),termination_stage=e.get('termination_stage'),
        classification='SAVED_EVIDENCE_ARITHMETIC_CONSISTENCY_ONLY_ORIGINAL_SCIENTIFIC_STOP_UNCHANGED',
        completed_helpers=len(completed),pairs=len(comparisons),prefixes=len(prefixes),finals=len(final),
        math_completed=len(math_ids),native_worker_raw_retained=len(worker_files),adapter_raw_retained=len(adapter_files),
        adapter_internal_arm_FK_J_started=counts['adapter_internal_arm_FK_J_started'],adapter_internal_arm_FK_J_completed=counts['adapter_internal_arm_FK_J_completed'],
        partial_candidates=partial,all_saved_JSON_files=len(json_inventory),all_saved_JSON_bytes=sum(row['bytes']for row in json_inventory),all_saved_JSON_parseable=all(row['parseable']for row in json_inventory),
        max_saved_pose_closure_position_mm=max_pos,max_saved_pose_rotation_matrix=max_rot,physical_gate_counts=dict(physical_counts),source_true=e['source_true_count'],source_false=e['source_false_count'],
        fully_completed_final_adapter_PQP=dict(query_counts),all_raw_native_worker_PQP=dict(worker_queries),
        event_counts=dict(event_counts),timing_saved_brackets=timing,trace_started=dict(trace_started),trace_completed=dict(trace_completed),UNKNOWN_helpers=len(unknown['helper']),UNKNOWN_finals=len(unknown['final']),saved_JSON_inventory=json_inventory)


if __name__=='__main__':
    if OUT.with_suffix('.json').exists()or OUT.with_suffix('.md').exists():raise FileExistsError('Preserve old POST')
    summary=audit();failed=[c for c in CHECKS if not c['passed']]
    report=dict(schema='P4_H_FIXED64_SAVED_ARITHMETIC_POST_V1',created_at_utc=datetime.now(timezone.utc).isoformat(),
        status='PASS_SAVED_ARITHMETIC'if not failed else'FAIL_SAVED_ARITHMETIC',
        personnel_independent=False,reviewer_role='Contributed runner logging/prior fixes; arithmetic audit only, separate reviewer required.',
        checks_total=len(CHECKS),checks_passed=len(CHECKS)-len(failed),checks_failed=len(failed),new_scientific_calls=0,new_compile_calls=0,new_helper_dispatches=0,
        script_sha256=sha(__file__),summary=summary,failed_checks=failed,checks=CHECKS)
    with OUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:
        f.write(f'''# H fixed64 保存证据算术POST（非人员独立）

**{report['status']}**：{report['checks_passed']}/{report['checks_total']}检查通过，{report['checks_failed']}失败。审查人参与过runner日志与prior元数据修正，本报告不得称为人员独立复核；另需独立第二层。

实际科学状态`{summary['execution_status']}`，{summary['completed_helpers']}个helper、{summary['pairs']}个plain/trace配对、{summary['prefixes']}个原/修正前缀、{summary['finals']}个完整终态。源true/false={summary['source_true']}/{summary['source_false']}；物理门分列统计见JSON，任何原false或物理拒绝均未筛掉。UNKNOWN helper/final={summary['UNKNOWN_helpers']}/{summary['UNKNOWN_finals']}。本次保存审计新增科学、编译、helper均为0。

保存算术审计通过不能把科学STOP改为PASS。原运行墙钟超限：{summary['budget_exceeded']['wall_s']}；CPU超限：{summary['budget_exceeded']['cpu_s']}；终止原因`{summary['termination_reason']}`，阶段`{summary['termination_stage']}`。数学终态{summary['math_completed']}、原生worker raw {summary['native_worker_raw_retained']}、adapter raw {summary['adapter_raw_retained']}，adapter内部FK/J为{summary['adapter_internal_arm_FK_J_started']}/{summary['adapter_internal_arm_FK_J_completed']}。第35候选只有数学检查和两个原始worker返回；adapter只返回native variant，aligned位姿核验未完成，完整final仍为UNKNOWN。

事件记录显示helper阶段{summary['timing_saved_brackets']['first_helper_to_last_helper_s']:.9f}秒、最后helper至首个终态数学检查{summary['timing_saved_brackets']['last_helper_to_first_final_metric_s']:.9f}秒、首个终态检查至STOP {summary['timing_saved_brackets']['first_final_metric_to_STOP_s']:.9f}秒。各区间包括对应的预算检查、持久化、解析与计算。源码确有flush/fsync及周期预算检查，但未保存逐次fsync或预算检查耗时；不能把fsync或任何单一组件认定为唯一耗时根因。全部{summary['all_saved_JSON_files']}个已存在JSON可解析性为{summary['all_saved_JSON_parseable']}；未改写运行文件。

仅使用stdlib读取raw字节/trace、保存角数组和TCP矩阵做闭链/限位/几何branch算术，核对原源布尔与物理/限位/碰撞门分列、完整raw尾部/实际计数、冻结26笔prior及所有资产hash。不加载FK/IK/NR/碰撞模块，不执行binary。科学own-cost墙钟{summary['wall_s']:.17g}秒、CPU{summary['cpu_s']:.17g}秒。该结果不是正式规划、分布优势、CCD或论文完整复现结论。
''')
    print(json.dumps({k:report[k]for k in ('status','checks_total','checks_passed','checks_failed')},ensure_ascii=False))
