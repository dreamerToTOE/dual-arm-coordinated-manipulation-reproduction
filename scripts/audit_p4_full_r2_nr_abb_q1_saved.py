#!/usr/bin/env python3
"""Independent saved-only NR Q1 POST auditor DRAFT; stdlib only.

Never imports the runner, NumPy, model, FK/J, IK, NR, collision or planner.
No command executes until explicitly called after Q1 completion. All output is
exclusive: an old audit or any scientific result is never overwritten.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
RUN='20261015_R2_NR_ABB_Q1_01'
GATES={'q_rad_abs':1e-10,'observed_delta_rad_abs':1e-10,
    'g_position_mm_abs':1e-8,'g_rotation_abs':1e-11,
    'J_position_mm_per_rad_abs':1e-8,'J_rotation_abs':1e-11,
    'metric_position_mm_abs':1e-8,'metric_rotation_abs':1e-11,
    'singular_abs':1e-8,'singular_relative':1e-10,
    'cutoff_abs':1e-18,'cutoff_relative':1e-10,
    'physical_position_mm':1e-5,'physical_rotation_matrix':1e-5}

def load(p):return json.loads(Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def target(name):
    p=Path(name);return p if p.is_absolute() else ROOT/p
def lines(p):return [json.loads(line) for line in Path(p).read_text().splitlines() if line.strip()]
def write_new(p,value):
    with Path(p).open('x') as stream:json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
def shape(value):
    return [len(value),[shape(v) for v in value]] if isinstance(value,list) else None
def flatten(value):
    return [x for child in value for x in flatten(child)] if isinstance(value,list) else [value]

class Audit:
    def __init__(self):self.checks=[]
    def add(self,name,passed,**evidence):
        self.checks.append({'check':name,'passed':bool(passed),**evidence});return bool(passed)
    def equal(self,name,a,b):return self.add(name,a==b,actual=a,expected=b)
    def close(self,name,a,b,absolute,relative=0.):
        aa,bb=flatten(a),flatten(b)
        finite=shape(a)==shape(b) and len(aa)==len(bb) and all(type(x)in(int,float) and math.isfinite(x) for x in aa+bb)
        errors=[abs(x-y) for x,y in zip(aa,bb)] if finite else []
        margins=[absolute+relative*max(abs(x),abs(y))-e for x,y,e in zip(aa,bb,errors)] if finite else []
        return self.add(name,finite and all(m>=0 for m in margins),shape_valid=finite,
            max_abs_error=max(errors,default=0.) if finite else None,
            minimum_margin=min(margins,default=absolute) if finite else None,absolute=absolute,relative=relative)
    def metrics(self,name,a,b):
        if not isinstance(a,dict) or not isinstance(b,dict):self.equal(name,a,b);return
        self.equal(name+'.keys',sorted(a),sorted(b));self.equal(name+'.unit',a['position_unit'],b['position_unit'])
        for key in ('translation_max_abs','rotation_matrix_max_abs','rotation_angle_max_rad'):
            self.close(name+'.'+key,a[key],b[key],GATES['metric_position_mm_abs']
                if key=='translation_max_abs' else GATES['metric_rotation_abs'])
    def passed(self):return all(c['passed'] for c in self.checks)

def original_cases(spec,audit):
    inventory=load(ROOT/'reports/P4_FULL_R2_NR_SOURCE_AUDIT_SAVED_INPUTS_20261015.json')
    audit.equal('fixed_cases.audit_copy',spec['fixed_cases'],inventory['Q1_saved_NR_cases_in_original_environment_and_observation_order'])
    rebuilt=[]
    for env in ('II','III'):
        path=f'results/p4_full/20261015_R2_SPATIAL01/{env}/observations.json'
        rows=load(ROOT/path);indices=[i for i,r in enumerate(rows) if r.get('kind')=='nr_reference']
        audit.equal('fixed_cases.'+env+'.original_count',len(indices),32)
        for index in indices:
            row=rows[index];r=row['result'];rebuilt.append({'case_id':env+'_'+row['fixture_kind']+'_'+row['fixture'],
                'environment':env,'source_path':path,'source_observation_index':index,
                'fixture_kind':row['fixture_kind'],'fixture':row['fixture'],'q12':r['input_q_rad'],
                'historical_status':r['status'],'historical_candidate_q_rad':r['candidate_q_rad'],
                'historical_metrics':r['metrics'],'historical_metric_only_trace':r['trace'],
                'historical_trace_lacks_q_g_J_sigma_delta':True})
    audit.equal('fixed_cases.original_all_nr_order',spec['fixed_cases'],rebuilt)
    return spec['fixed_cases']

def trace_self(audit,name,trace,q_input,accepted_updates):
    audit.equal(name+'.iterations',[s['iteration'] for s in trace],list(range(len(trace))))
    audit.equal(name+'.first_q',trace[0]['q_before'] if trace else None,q_input)
    updates=0
    for index,step in enumerate(trace):
        p=f'{name}.step{index}'
        audit.equal(p+'.q_dimension',len(step['q_before']),12);audit.equal(p+'.g_dimension',len(step['g']),6)
        audit.equal(p+'.J_shape',shape(step['j']),shape([[0]*12 for _ in range(6)]))
        audit.add(p+'.finite_g_J',all(type(v)in(int,float) and math.isfinite(v)
            for v in flatten(step['q_before'])+flatten(step['g'])+flatten(step['j'])))
        audit.close(p+'.saved_translation_metric',max(abs(v) for v in step['g'][:3]),
            step['metrics']['translation_max_abs'],1e-12)
        if step['q_next']:
            updates+=1;s=step['singular_values']
            audit.equal(p+'.spectrum_length',len(s),6)
            audit.add(p+'.spectrum_sorted_finite',all(math.isfinite(v) and v>=0 for v in s) and
                all(a>=b for a,b in zip(s,s[1:])))
            audit.equal(p+'.cutoff_from_original_relative',step['cutoff'],s[0]*1e-12)
            audit.equal(p+'.rank_from_saved_spectrum',step['numerical_rank'],sum(v>step['cutoff'] for v in s))
            audit.equal(p+'.observed_delta_from_saved_q',step['observed_delta_q'],
                [a-b for a,b in zip(step['q_next'],step['q_before'])])
            if index+1<len(trace):audit.equal(p+'.next_iteration_q',step['q_next'],trace[index+1]['q_before'])
            if 'proposed_delta_q' in step:
                audit.close(p+'.proposal_lands_at_saved_q',
                    [a+b for a,b in zip(step['q_before'],step['proposed_delta_q'])],step['q_next'],1e-14)
        else:
            for key,wanted in (('singular_values',[]),('cutoff',0.),('numerical_rank',0),('observed_delta_q',[])):
                audit.equal(p+'.terminal_'+key,step[key],wanted)
            if 'proposed_delta_q'in step:audit.equal(p+'.terminal_proposal',step['proposed_delta_q'],[])
    audit.equal(name+'.accepted_updates',accepted_updates,updates)

def transfer_case(audit,case,plain,cpp,observed):
    name='transfer.'+case['case_id'];py=observed['result'];pt=observed['detailed_trace'];ct=cpp['trace']
    audit.equal(name+'.plain_trace_non_cost',{k:v for k,v in plain.items() if k not in ('wall_s','trace')},
        {k:v for k,v in cpp.items() if k not in ('wall_s','trace')})
    audit.equal(name+'.plain_trace_empty',plain['trace'],[])
    audit.equal(name+'.python_observer_errors',observed['observer_errors'],[])
    audit.equal(name+'.python_original_body_modified',observed['original_body_modified'],False)
    audit.equal(name+'.python_additional_math_calls',observed['additional_FK_J_SVD_calls'],0)
    audit.equal(name+'.input_cpp',cpp['input_q_rad'],case['q12']);audit.equal(name+'.input_python',py['input_q_rad'],case['q12'])
    audit.equal(name+'.status',cpp['status'],py['status']);audit.equal(name+'.trace_length',len(ct),len(pt))
    audit.equal(name+'.updates',cpp['accepted_updates'],observed['accepted_updates_observed'])
    if cpp['candidate_q_rad']is None or py['candidate_q_rad']is None:
        audit.equal(name+'.candidate_null',cpp['candidate_q_rad'],py['candidate_q_rad'])
    else:audit.close(name+'.candidate',cpp['candidate_q_rad'],py['candidate_q_rad'],GATES['q_rad_abs'])
    audit.metrics(name+'.metrics',cpp['metrics'],py['metrics'])
    audit.equal(name+'.python_basic_trace',py['trace'],[{'iteration':s['iteration'],**s['metrics']} for s in pt])
    trace_self(audit,name+'.cpp',ct,case['q12'],cpp['accepted_updates'])
    trace_self(audit,name+'.python',pt,case['q12'],observed['accepted_updates_observed'])
    for index,(a,b) in enumerate(zip(ct,pt)):
        p=f'{name}.step{index}';audit.equal(p+'.iteration',a['iteration'],b['iteration'])
        audit.equal(p+'.rank',a['numerical_rank'],b['numerical_rank']);audit.equal(p+'.update',bool(a['q_next']),bool(b['q_next']))
        for key in ('q_before','q_next','observed_delta_q'):audit.close(p+'.'+key,a[key],b[key],GATES['q_rad_abs'])
        for key,split,position,rotation in (('g',3,GATES['g_position_mm_abs'],GATES['g_rotation_abs']),
                ('j',3,GATES['J_position_mm_per_rad_abs'],GATES['J_rotation_abs'])):
            audit.close(p+'.'+key+'_position',a[key][:split],b[key][:split],position)
            audit.close(p+'.'+key+'_rotation',a[key][split:],b[key][split:],rotation)
        audit.close(p+'.singular_values',a['singular_values'],b['singular_values'],GATES['singular_abs'],GATES['singular_relative'])
        audit.close(p+'.cutoff',a['cutoff'],b['cutoff'],GATES['cutoff_abs'],GATES['cutoff_relative'])
        audit.metrics(p+'.metrics',a['metrics'],b['metrics'])

def history_case(audit,case,py):
    name='history.'+case['case_id'];audit.equal(name+'.status',py['status'],case['historical_status'])
    audit.equal(name+'.iterations',[r['iteration'] for r in py['trace']],
        [r['iteration'] for r in case['historical_metric_only_trace']])
    if py['candidate_q_rad']is None or case['historical_candidate_q_rad']is None:
        audit.equal(name+'.candidate_null',py['candidate_q_rad'],case['historical_candidate_q_rad'])
    else:audit.close(name+'.candidate',py['candidate_q_rad'],case['historical_candidate_q_rad'],GATES['q_rad_abs'])
    audit.metrics(name+'.final_metrics',py['metrics'],case['historical_metrics'])
    for index,(a,b) in enumerate(zip(py['trace'],case['historical_metric_only_trace'])):
        audit.metrics(f'{name}.step{index}.metrics',{k:v for k,v in a.items() if k!='iteration'},
            {k:v for k,v in b.items() if k!='iteration'})

def audit_run(protocol,folder):
    audit=Audit();spec=load(protocol);execution=load(folder/'execution.json');claim=load(target(execution['claim']))
    audit.equal('protocol.frozen',spec['frozen'],True)
    audit.add('protocol.reviews_all_true',all(v is True for v in spec['reviews'].values()))
    audit.equal('protocol.gates_unchanged',spec['comparison_gates'],GATES)
    audit.equal('protocol.source_hash',execution['protocol_sha256'],digest(protocol))
    audit.equal('protocol.before_after',execution['protocol_sha256'],execution['protocol_after_sha256'])
    audit.equal('claim.current',execution['claim_sha256'],digest(target(execution['claim'])))
    audit.equal('claim.before_after',execution['claim_sha256'],execution['claim_after_sha256'])
    audit.equal('claim.protocol',claim['protocol_sha256'],execution['protocol_sha256'])
    audit.equal('claim.commit',claim['source_commit'],execution['source_commit'])
    audit.equal('run.no_retry',claim['no_retry_reset_or_resume'],True)
    audit.equal('run.id',execution['run_id'],RUN)
    audit.equal('bound.spec_execution',spec['bound_files_sha256'],execution['bound_files_sha256'])
    audit.equal('bound.before_after',execution['bound_files_sha256'],execution['bound_files_after_sha256'])
    for name,wanted in spec['bound_files_sha256'].items():audit.equal('asset.'+name,digest(target(name)),wanted)
    for name in ('scripts/qualify_p4_full_r2_nr_abb_q1_draft.py',
            'scripts/p4_full_r2_nr_python_trace_draft.py',
            'baselines/p4_full/geometry_consistent/physical_nr.py',str(protocol.relative_to(ROOT))):
        blob=subprocess.check_output(['git','show',execution['source_commit']+':'+name],cwd=ROOT)
        audit.equal('committed_blob.'+name,hashlib.sha256(blob).hexdigest(),digest(target(name)))
    cases=original_cases(spec,audit);responses={};process_requests={}
    for label,mode,count in (('cpp_plain','plain',64),('cpp_trace','trace',64),('python_worker',None,128)):
        requests=lines(folder/(label+'.requests.jsonl'));stdout=lines(folder/(label+'.stdout.bin'))
        audit.equal(label+'.request_count',len(requests),count);audit.equal(label+'.stdout_response_count',len(stdout),count)
        saved=[]
        for index,response in enumerate(stdout):
            stored=load(folder/f'{label}_{index:03d}_raw_response.json');audit.equal(f'{label}.{index}.raw_saved',stored,response)
            audit.equal(f'{label}.{index}.index',response['request_index'],index)
            audit.equal(f'{label}.{index}.request',response['request'],requests[index])
            if mode is not None:
                audit.equal(f'{label}.{index}.schema',response['schema'],'P4_NR_ABB_CPP_Q1_DRAFT_V1')
                audit.equal(f'{label}.{index}.mode',response['mode'],mode)
                audit.equal(f'{label}.{index}.returned',response['completed_top_level_nr'],True)
                audit.equal(f'{label}.{index}.original_request',requests[index],{k:cases[index][k] for k in ('case_id','environment','q12')})
            else:
                audit.equal(f'{label}.{index}.schema',response['schema'],'P4_NR_ABB_PYTHON_Q1_WORKER_DRAFT_V1')
                audit.equal(f'{label}.{index}.returned',response['completed_operation'],True)
                case=cases[index%64];expected={'operation':'nr' if index<64 else 'independent_final',
                    'case_id':case['case_id'],'environment':case['environment'],
                    'q12':case['q12'] if index<64 else responses['cpp_trace'][index-64]['candidate_q_rad']}
                audit.equal(f'{label}.{index}.fixed_request',requests[index],expected)
            saved.append(response['result'])
        responses[label]=saved;process_requests[label]=requests
    events=lines(folder/'events.jsonl');worker_events=lines(folder/'python_worker.stderr.txt')
    copied_events=load(folder/'python_worker_observed_events.json')
    audit.equal('worker_events.raw_saved',copied_events['events'],worker_events)
    audit.equal('worker_events.no_unknown_stderr',copied_events['non_event_stderr'],[])
    audit.equal('worker_events.no_stopped',[e for e in worker_events if e['event']=='worker_stopped'],[])
    audit.equal('parent_events.no_stopped',[e for e in events if e['event']=='stopped'],[])
    starts=[e for e in events if e['event']=='process_started'];ends=[e for e in events if e['event']=='process_reaped']
    audit.equal('processes.start_order',[e['label'] for e in starts],['cpp_plain','cpp_trace','python_worker'])
    audit.equal('processes.end_order',[e['label'] for e in ends],['cpp_plain','cpp_trace','python_worker'])
    audit.add('processes.all_clean',len(ends)==3 and all(e['returncode']==0 and e['inflight']is None for e in ends))
    sent=[e for e in events if e['event']=='request_bytes_sent']
    expected_sent=[(label,i,r) for label in ('cpp_plain','cpp_trace','python_worker')
        for i,r in enumerate(process_requests[label])]
    audit.equal('actual_sent.256_operations',[(e['label'],e['request_index'],e['request']) for e in sent],expected_sent)
    nr_completed=[e for e in events if e['event']=='nr_completed'];dispatch_attempts=[e for e in events if e['event']=='nr_dispatch_attempted']
    expected_nr=[(v,i,c['case_id']) for v in ('cpp_plain','cpp_trace','python_original_observed') for i,c in enumerate(cases)]
    for name,rows in (('nr_completed',nr_completed),('nr_dispatch_attempted',dispatch_attempts)):
        audit.equal(name+'.exact_192_order',[(e['variant'],e['case_index'],e['case_id']) for e in rows],expected_nr)
    for name in ('independent_final_dispatched','independent_final_completed'):
        rows=[e for e in events if e['event']==name]
        audit.equal(name+'.case_order',[e['case_id'] for e in rows],[c['case_id'] for c in cases])
    summary=load(folder/'comparison_summary.json');histories=load(folder/'history_diagnostics.json')
    audit.equal('summary.all64_completed',summary['all64_completed'],True)
    audit.equal('summary.comparison_count',len(summary['comparisons']),64);audit.equal('summary.history_count',len(histories),64)
    physical=[];transfer_passed=history_passed=0
    for index,case in enumerate(cases):
        start=len(audit.checks);cpp=responses['cpp_trace'][index];observed=responses['python_worker'][index]
        transfer_case(audit,case,responses['cpp_plain'][index],cpp,observed)
        case_transfer=all(c['passed'] for c in audit.checks[start:]);transfer_passed+=case_transfer
        start=len(audit.checks);history_case(audit,case,observed['result'])
        case_history=all(c['passed'] for c in audit.checks[start:]);history_passed+=case_history
        comparison=load(folder/f'comparison_{index:03d}.json')
        audit.equal(f'comparison{index}.summary_copy',comparison,summary['comparisons'][index])
        audit.equal(f'comparison{index}.independent_verdict',comparison['all_passed'],case_transfer)
        audit.add(f'comparison{index}.all_saved_checks',all(c['passed']is True for c in comparison['checks']))
        audit.equal(f'history{index}.new_reference_copy',histories[index]['new_original_reference'],observed['result'])
        audit.equal(f'history{index}.independent_verdict',histories[index]['all_passed'],case_history)
        audit.add(f'history{index}.all_saved_checks',all(c['passed']is True for c in histories[index]['checks']))
        row=load(folder/f'independent_final_{index:03d}.json');raw=responses['python_worker'][64+index]
        audit.equal(f'final{index}.raw_fields',{k:row[k] for k in raw},raw)
        audit.equal(f'final{index}.summary_copy',row,summary['independent_final'][index])
        finite=isinstance(cpp['candidate_q_rad'],list) and len(cpp['candidate_q_rad'])==12 and all(math.isfinite(v) for v in cpp['candidate_q_rad'])
        audit.equal(f'final{index}.finite',row['candidate_is_finite'],finite)
        if finite:
            bounds=[[a*3.1416/180,b*3.1416/180] for a,b in [(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]]*2
            audit.equal(f'final{index}.original_bounds',row['source_bounds_rad'],bounds)
            margins=[min(q-a,b-q) for q,(a,b) in zip(cpp['candidate_q_rad'],bounds)]
            audit.equal(f'final{index}.margins',row['limit_margins_rad'],margins)
            audit.equal(f'final{index}.min_margin',row['minimum_limit_margin_rad'],min(margins))
            legal=all(v>=0 for v in margins);closed=row['metrics']['translation_max_abs']<=1e-5 and row['metrics']['rotation_matrix_max_abs']<=1e-5
            audit.equal(f'final{index}.legal',row['limits_legal'],legal);audit.equal(f'final{index}.closed',row['closed'],closed)
            audit.equal(f'final{index}.physical_qualified',row['physical_qualified'],closed and legal)
            audit.metrics(f'final{index}.cpp_saved_metric_agreement',row['metrics'],cpp['metrics'])
        sound=cpp['status']!='CONVERGED' or row['physical_qualified']is True
        audit.equal(f'final{index}.soundness_verdict',row['soundness_passed'],sound);audit.add(f'final{index}.sound',sound)
        physical.append(row)
        # Match every Python snapshot/update event to the final returned row.
        stream=[e['observation'] for e in worker_events if e['event']=='observer' and e['case_id']==case['case_id']]
        expected=[]
        for step in observed['detailed_trace']:
            snap={**step,'singular_values':[],'cutoff':0.,'numerical_rank':0,'observed_delta_q':[],'q_next':[]}
            expected.append({'event':'STEP_SNAPSHOT','step':snap})
            if step['q_next']:expected.append({'event':'STEP_UPDATE','step':step})
        audit.equal(f'worker{index}.full_observer_stream',stream,expected)
        for stage in ('python_original','independent_final'):
            arms=[e for e in worker_events if e['event']in('arm_FK_J_started','arm_FK_J_completed') and e['stage']==stage and e['case_id']==case['case_id']]
            if stage=='python_original':
                trace=observed['detailed_trace'];terminal=trace[-1]['metrics']
                chart=terminal['translation_max_abs']<=1e-5 and terminal['rotation_matrix_max_abs']<=1e-5
                arm_sequence=[1,2]*(2*len(trace)+int(chart))
            else:arm_sequence=[1,2] if finite else []
            expected_arm=[(kind,arm) for arm in arm_sequence for kind in ('arm_FK_J_started','arm_FK_J_completed')]
            audit.equal(f'worker{index}.{stage}.observed_arm_sequence',[(e['event'],e['arm']) for e in arms],expected_arm)
    derived=Counter()
    for e in worker_events:
        if e['event']in('arm_FK_J_started','arm_FK_J_completed'):derived[e['stage']+'_'+e['event']]+=1
        if e['event']in('independent_final_metric_started','independent_final_metric_completed'):derived[e['event']]+=1
    for name,count in derived.items():audit.equal('actual_event_count.'+name,execution['counts'].get(name),count)
    for prefix in ('cpp_plain','cpp_trace','python_original'):
        for suffix in ('dispatch_attempted','dispatched','responses_retained','completed'):
            audit.equal('actual_top_level_count.'+prefix+'_'+suffix,execution['counts'].get(prefix+'_'+suffix),64)
    for suffix in ('dispatch_attempted','dispatched','completed'):
        audit.equal('actual_final_request_count.'+suffix,execution['counts'].get('independent_final_requests_'+suffix),64)
    audit.equal('actual_final_metrics.started',derived['independent_final_metric_started'],sum(r['candidate_is_finite'] for r in physical))
    audit.equal('actual_final_metrics.completed',derived['independent_final_metric_completed'],derived['independent_final_metric_started'])
    audit.equal('actual_final_arms.started',derived['independent_final_arm_FK_J_started'],2*derived['independent_final_metric_started'])
    audit.equal('execution.transfer_count',execution['comparison_passed'],transfer_passed)
    audit.equal('execution.history_count',execution['history_passed'],history_passed)
    audit.equal('execution.physical_count',execution['independent_final_qualified'],sum(r['physical_qualified'] for r in physical))
    audit.equal('execution.no_inflight',execution['inflight_unreturned_call'],None)
    audit.equal('execution.no_diagnostics',execution['diagnostics'],[])
    audit.add('execution.no_uncompleted',all(v==[] for v in execution['uncompleted_case_ids'].values()))
    audit.equal('execution.zero_science_outside_scope',execution['zero_calls'],spec['zero_calls'])
    prior=[load(target(name)) for name in spec['prior_executions']]
    prior_wall=math.fsum(r['wall_s'] for r in prior);prior_cpu=math.fsum(r['cpu_s'] for r in prior)
    audit.equal('ledger.prior_wall',spec['previous_r2_wall_s'],prior_wall);audit.equal('ledger.prior_cpu',spec['previous_r2_cpu_s'],prior_cpu)
    audit.add('budget.actual_wall',0<=execution['wall_s']<min(60.,3600.-prior_wall))
    audit.add('budget.actual_cpu',0<=execution['cpu_s']<min(120.,7200.-prior_cpu))
    audit.equal('execution.status_corresponds_independent_evidence',execution['status'],
        'PASS_FIXED64_NUMERICAL_TRANSFER' if transfer_passed==64 and history_passed==64 and all(r['soundness_passed'] for r in physical)
        else 'NUMERICAL_TRANSFER_OR_HISTORY_OR_SOUNDNESS_REJECTED_UNKNOWN_CAUSE')
    return {'schema':'P4_R2_NR_ABB_Q1_INDEPENDENT_SAVED_POST_REVIEW_V1',
        'classification':'SAVED_ONLY_NO_NEW_FK_J_SVD_NR_OR_OTHER_SCIENCE',
        'status':'PASS_INDEPENDENT_SAVED_POST_REVIEW' if audit.passed() else 'SAVED_POST_REVIEW_REJECTED',
        'protocol':str(protocol),'protocol_sha256':digest(protocol),'execution':str(folder/'execution.json'),
        'execution_sha256':digest(folder/'execution.json'),'audit_script_sha256':digest(__file__),
        'checks_total':len(audit.checks),'checks_passed':sum(c['passed'] for c in audit.checks),
        'fixed_cases':len(cases),'top_level_nr_dispatched':192,'top_level_nr_completed':len(nr_completed),
        'transfer_passed':transfer_passed,'history_passed':history_passed,
        'independent_final_metric_started':derived['independent_final_metric_started'],
        'independent_final_metric_completed':derived['independent_final_metric_completed'],
        'physical_qualified':sum(r['physical_qualified'] for r in physical),'actual_worker_counts':dict(derived),
        'bound_asset_count':len(spec['bound_files_sha256']),'wall_s':execution['wall_s'],'cpu_s':execution['cpu_s'],
        'scope':'Fixed near64 transfer only; stored physical metrics independently audited arithmetically, no new FK. No collision/RBS/planner/RNG/general projection capability or speed claim.',
        'checks':audit.checks}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--protocol',type=Path,required=True)
    parser.add_argument('--run-directory',type=Path,default=ROOT/'results/p4_full'/RUN)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('AUDIT_OUTPUT_EXISTS_NO_OVERWRITE')
    result=audit_run(args.protocol.resolve(),args.run_directory.resolve());write_new(args.output,result)
    print(json.dumps({k:result[k] for k in ('status','checks_total','checks_passed','transfer_passed','history_passed')}))
    if result['status']!='PASS_INDEPENDENT_SAVED_POST_REVIEW':raise SystemExit(2)

if __name__=='__main__':main()
