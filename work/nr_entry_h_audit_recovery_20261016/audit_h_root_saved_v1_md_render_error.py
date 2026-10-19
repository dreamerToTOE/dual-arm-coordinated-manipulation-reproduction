#!/usr/bin/env python3
"""Personnel-independent stdlib audit of saved fixed64 ABB helper H.

No scientific module import, binary execution, FK/IK/Jacobian/NR/PQP/RNG,
compilation, candidate construction, retry or resume. Matrix subtraction,
source-limit arithmetic and membership in saved geometric branch sets only.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import datetime
import hashlib
import json
import math
import struct
import subprocess

ROOT = Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
DEFAULT_RUN = 'results/p4_full/20261015_R2_ABB_RANDOM_HELPER_H01'
DEFAULT_OUT = 'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_ROOT_INDEPENDENT_POST_20261016.json'


def fp(name):
    p = Path(name)
    return p if p.is_absolute() else ROOT/p


def sha(name):
    return hashlib.sha256(fp(name).read_bytes()).hexdigest()


def read(name):
    return json.loads(fp(name).read_text())


def exact(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if type(a) in (float, int) and type(b) in (float, int):
        return struct.pack('>d', a) == struct.pack('>d', b)
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return set(a) == set(b) and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def join(e):
    return e['q1'] + e['q2']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run', default=DEFAULT_RUN)
    ap.add_argument('--output', default=DEFAULT_OUT)
    ap.add_argument('--audit-original-stop', action='store_true', help='Audit retained STOP prefix; never promote original qualification.')
    args = ap.parse_args()
    run, out = fp(args.run), fp(args.output)
    if not (run/'execution.json').is_file():
        raise SystemExit('SAVED_EXECUTION_REQUIRED_NO_SCIENCE_STARTED')
    if out.exists() or out.with_suffix('.md').exists():
        raise SystemExit('AUDIT_OUTPUT_EXISTS_PRESERVE_PRIOR_NO_OVERWRITE')
    groups = defaultdict(lambda: {'total': 0, 'passed': 0})
    failed, observations = [], []
    retained = {}

    def ck(group, label, ok):
        groups[group]['total'] += 1
        groups[group]['passed'] += bool(ok)
        if not ok:
            failed.append({'group': group, 'check': label})

    def saved(name):
        name = fp(name)
        retained[str(name.relative_to(ROOT)) if name.is_relative_to(ROOT) else str(name)] = sha(name)
        return read(name)

    def jsonl(name, marker=None):
        name = fp(name)
        retained[str(name.relative_to(ROOT))] = sha(name)
        raw = name.read_bytes()
        if marker is None:
            ck('raw_streams', str(name.relative_to(run))+' final newline', not raw or raw.endswith(b'\n'))
        rows = []
        for i, line in enumerate(raw.splitlines(), 1):
            if marker is not None:
                if marker not in line:
                    continue
                line = line.split(marker, 1)[1]
            try:
                rows.append(json.loads(line))
            except (ValueError, UnicodeDecodeError):
                ck('raw_streams', str(name.relative_to(run))+' parse line '+str(i), False)
        return rows

    e = saved(run/'execution.json')
    p = saved(e['protocol'])
    c = saved(e['claim'])
    stopped = args.audit_original_stop
    ck('metadata', 'exact execution schema/status', e['schema'] == 'P4_R2_ABB_RANDOM_HELPER_H_FIXED64_EXECUTION_DRAFT_V1'
       and e['status'] == ('STOP_CLEANUP_OR_EVIDENCE_ERROR' if stopped else 'PASS_FIXED64_HELPER_CONTROL_FLOW_WITH_INDEPENDENT_FINAL_GATES'))
    ck('metadata', 'root frozen reviewed protocol', p['frozen'] is True and all(v is True for v in p['reviews'].values())
       and p['execution_readiness'] == 'FROZEN_REVIEWED_READY')
    ck('metadata', 'protocol and claim pre/post hashes', sha(e['protocol']) == e['protocol_sha256'] == e['protocol_after_sha256']
       and sha(e['claim']) == e['claim_sha256'] == e['claim_after_sha256'])
    ck('metadata', 'claim matches source and protocol', c['source_commit'] == e['source_commit']
       and c['protocol_sha256'] == e['protocol_sha256'] and c['no_retry_reset_or_resume'] is True)
    ck('metadata', 'RECONSTRUCTED and nonformal', 'RECONSTRUCTED' in e['classification'] and 'NONFORMAL' in e['classification']
       and e['formal_table_I_calls'] == e['new_VI_candidate_constructions'] == 0 and e['formal_table_I_required_calls'] == 22500)
    ck('metadata', 'no planning or distribution claim', e['continuous_collision_certificate'] is False
       and e['not_planning_or_distribution_capability_pass'] is True)
    ck('metadata', 'zero science exclusions', e['zero_calls'] == p['zero_calls']
       and all(type(v) is int and v == 0 for v in e['zero_calls'].values()))
    ck('metadata', 'original metric gates', p['gates']['position_max_abs_mm'] == p['gates']['rotation_matrix_max_abs'] == 1e-5
       and p['gates']['source_limits_literal_pi'] == 3.1416 and p['gates']['continuous_collision_certificate'] is False)
    ck('metadata', 'plain and rand work remains unobserved', 'UNOBSERVED' in e['plain_source_internal_counts']
       and 'UNOBSERVED' in e['rand_started_completed'])
    ck('provenance', 'all bound tables exact', e['bound_files_sha256'] == p['bound_files_sha256'] == e['bound_files_after_sha256'])
    for name, wanted in e['bound_files_sha256'].items():
        ck('provenance', 'bound bytes '+name, sha(name) == wanted)
    ck('provenance', 'prior exact binding', e['prior_execution_sha256'] == p['prior_execution_sha256'])
    priors = []
    for name, wanted in p['prior_execution_sha256'].items():
        ck('ledger', 'prior '+name, sha(name) == wanted)
        priors.append(read(name))
    wall, cpu = math.fsum(x['wall_s'] for x in priors), math.fsum(x['cpu_s'] for x in priors)
    ck('ledger', 'only own prior costs sum', exact(wall, p['previous_r2_wall_s']) and exact(cpu, p['previous_r2_cpu_s'])
       and exact(wall, e['previous_r2_wall_s']) and exact(cpu, e['previous_r2_cpu_s']))
    ck('ledger', 'single and cumulative hats honestly classified', 0 <= e['cpu_s'] < 120.
       and (e['wall_s'] >= 60. if stopped else 0 <= e['wall_s'] < 60.)
       and wall+e['wall_s'] < 3600. and cpu+e['cpu_s'] < 7200.)
    build = p['build_assets']
    ck('build', 'two exact built targets', build['status'] == 'BUILT_NOT_QUERIED'
       and set(build['targets']) == {'source_control','success_break'})
    for name, wanted in build['files'].items():
        ck('build', 'bound build asset '+name, sha(name) == wanted)
    # git show is the sole subprocess: it reads committed source bytes only.
    own = [name for name in p['bound_files_sha256'] if name.startswith(('scripts/','baselines/'))]
    for name in own:
        blob = subprocess.check_output(['git','show',e['source_commit']+':'+name], cwd=ROOT)
        ck('provenance', 'science commit blob '+name, hashlib.sha256(blob).hexdigest() == p['bound_files_sha256'][name])
    contexts = p['fixed_contexts']
    schedule = [{**ctx, 'dispatch_index': i, 'factor': factor, 'mode': mode}
                for i, (factor,mode,ctx) in enumerate((f,m,x) for f in ('source_control','success_break')
                                                     for m in ('plain','trace') for x in contexts)]
    ck('schedule', 'exact frozen 16 contexts and64', len(contexts) == 16 and len({x['case_id'] for x in contexts}) == 16
       and exact(schedule, p['fixed_schedule']))
    ck('schedule', 'unmodified four A01 centers roles/seeds',
       {(x['environment'],x['active_chain'],x['seed']) for x in contexts} ==
       {(env,active,seed) for env in ('II','III') for active in (0,1) for seed in (7,17)})
    for ctx in contexts:
        source = saved(ctx['endpoint_source'])
        ck('schedule', ctx['case_id']+' endpoint identity', exact(ctx['q12'],source['selected_q_rad'])
           and source['status'] == 'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED')
    bykey, byindex = {}, {}
    trace_started, trace_completed, trace_marks = Counter(), Counter(), Counter()
    branch_attempts = defaultdict(list)
    for fixture in schedule:
        i = fixture['dispatch_index']
        label = str(i)+' '+fixture['case_id']
        request = saved(run/f'helper_{i:03d}_request.json')
        r = saved(run/f'helper_{i:03d}_raw_response.json')
        rawname = run/f'helper_{i:03d}_raw_response_line.bin'
        raw = rawname.read_bytes();retained[str(rawname.relative_to(ROOT))] = sha(rawname)
        ck('responses', label+' raw full newline', raw.endswith(b'\n') and raw.count(b'\n') == 1)
        ck('responses', label+' raw exact JSON', exact(json.loads(raw),r))
        wanted = {k: fixture[k] for k in ('case_id','operation','environment','q12','active_chain','seed')}
        ck('responses', label+' request exact', exact(request,wanted) and exact(r['request'],wanted))
        ck('responses', label+' successful transport', r['schema'] == 'P4_ABB_RANDOM_HELPER_TRANSPORT_DRAFT_V1'
           and r['status'] == 'SOURCE_HELPER_COMPLETED' and r['mode'] == fixture['mode'] and r['environment'] == fixture['environment']
           and r['helper_dispatch_started'] == r['helper_dispatch_completed'] == r['srand_calls_completed'] == 1
           and r['post_helper_model_calls'] == 0 and type(r['returned']) is bool)
        ck('responses', label+' finite untouched active bits', len(r['q12']) == 12 and all(math.isfinite(v) for v in r['q12'])
           and r['candidate_is_finite'] is True and exact(r['q12'][6*fixture['active_chain']:6*(fixture['active_chain']+1)],
                                                       fixture['q12'][6*fixture['active_chain']:6*(fixture['active_chain']+1)]))
        bykey[(fixture['factor'],fixture['mode'],fixture['case_id'])] = r
        byindex[i] = r
        if fixture['factor'] == 'source_control':
            ck('control_flow', label+' source false retained', r['returned'] is False)
        if fixture['mode'] == 'plain':
            ck('trace', label+' plain not inferred', r['source_counts_observed'] is False and r['trace'] is None
               and r['source_started'] is None and r['source_completed'] is None)
            continue
        ck('trace', label+' trace enabled', r['source_counts_observed'] is True)
        starts, dones, marks = Counter(), Counter(), Counter()
        serial, stack, opened = 0, [], {}
        shuffles, branches, helpers = [], [], []
        for j, ev in enumerate(r['trace']):
            event, kind, eid = ev['event'], ev['kind'], ev['id']
            ck('trace', label+' event'+str(j)+' positive id', type(eid) is int and eid > 0)
            if event in ('entered','observed'):
                serial += 1
                ck('trace', label+' event'+str(j)+' serial', eid == serial)
            if event == 'entered':
                ck('trace', label+' event'+str(j)+' unique opened', eid not in opened)
                opened[eid]=kind;stack.append(eid);starts[kind]+=1
                if kind == 'helper_three':helpers.append(ev)
            elif event == 'completed':
                ck('trace', label+' event'+str(j)+' nested completion', bool(stack) and stack.pop() == eid and opened.pop(eid,None) == kind)
                dones[kind]+=1
            elif event == 'observed':
                marks[kind]+=1
                if kind == 'shuffle_completed':shuffles.append(ev)
                if kind == 'branch_entered':branches.append(ev)
            else:ck('trace', label+' event'+str(j)+' allowed event', False)
        ck('trace', label+' full calls and counters', not stack and not opened and dict(starts) == r['source_started']
           and dict(dones) == r['source_completed'] and starts == dones and starts['helper_three'] == 1
           and starts.get('collision',0) == 0)
        ck('trace', label+' helper endpoints exact', len(helpers) == 1 and exact(join(helpers[0]['args']),request['q12'])
           and helpers[0]['args']['active_chain'] == fixture['active_chain']
           and r['trace'][-1]['kind'] == 'helper_three' and r['trace'][-1]['event'] == 'completed'
           and r['trace'][-1]['result']['returned'] is r['returned'] and exact(join(r['trace'][-1]['result']),r['q12']))
        ck('trace', label+' original shuffled order', len(shuffles) == 1 and sorted(shuffles[0]['args']['order']) == list(range(8)))
        if len(shuffles) == 1:
            order = shuffles[0]['args']['order']
            ck('trace', label+' visited shuffled prefix', 1 <= len(branches) <= 8
               and [b['args']['loop_index'] for b in branches] == list(range(len(branches)))
               and [b['args']['branch'] for b in branches] == order[:len(branches)])
        trace_started.update(starts);trace_completed.update(dones);trace_marks.update(marks)
        branch_attempts[fixture['factor']].append(len(branches))
    summary = saved(run/'comparison_summary.json')
    comparisons, prefixes = [], []
    ignored = {'mode','source_counts_observed','source_started','source_completed','trace'}
    for factor in ('source_control','success_break'):
        for ctx in contexts:
            case = ctx['case_id']; a,b = (bykey[(factor,m,case)] for m in ('plain','trace'))
            ck('plain_trace', factor+'/'+case+' exact binary64 nonobservation',
               exact({k:v for k,v in a.items() if k not in ignored},{k:v for k,v in b.items() if k not in ignored}))
            comparisons.append({'factor':factor,'case_id':case,'passed':True,'non_observation_binary64_exact':True})
    for ctx in contexts:
        case = ctx['case_id']; a,b = (bykey[(f,'trace',case)] for f in ('source_control','success_break'))
        successes = [(j,t) for j,t in enumerate(a['trace']) if t['event'] == 'observed'
                     and t['kind'] == 'identify_completed_in_helper' and all(v != -1 for v in t['args']['ik'])]
        acount = sum(t['event']=='observed' and t['kind']=='branch_entered' for t in a['trace'])
        bcount = sum(t['event']=='observed' and t['kind']=='branch_entered' for t in b['trace'])
        ck('control_flow', case+' source eight branches', a['returned'] is False and acount == 8)
        if successes:
            stop, first = successes[0]
            ck('control_flow', case+' H exact first-success prefix', b['returned'] is True
               and exact(a['trace'][:stop+1],b['trace'][:-1]) and exact(join(first['args']),b['q12'])
               and b['trace'][-1]['event'] == 'completed' and b['trace'][-1]['kind'] == 'helper_three')
            prefixes.append({'case_id':case,'passed':True,'first_identified_loop_index':first['args']['loop_index'],
                             'first_identified_branch':first['args']['branch'],'common_prefix_events':stop+1,
                             'original_branch_attempts':acount,'break_branch_attempts':bcount})
        else:
            ck('control_flow', case+' no success preserved', b['returned'] is False and exact(a['q12'],b['q12']) and exact(a['trace'],b['trace']))
            prefixes.append({'case_id':case,'passed':True,'first_identified_loop_index':None,'first_identified_branch':None,
                             'common_prefix_events':len(a['trace']),'original_branch_attempts':acount,'break_branch_attempts':bcount})
    ck('summaries', 'plain trace and prefix saved summary exact', exact(comparisons,summary['plain_trace']) and exact(prefixes,summary['control_prefix']))
    # No model evaluation: arithmetic from the two independently saved TCPs.
    finals = saved(run/'independent_final_summary.json')
    metrics, aggregate = [], Counter()
    degrees = [(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]*2
    completed_schedule = [x for x in schedule if x['dispatch_index'] in e['completed_final_ids']]
    for fixture in completed_schedule:
        i, factor, mode, case = (fixture[k] for k in ('dispatch_index','factor','mode','case_id'))
        f = saved(run/f'final_{i:03d}.json'); fm = saved(run/f'final_{i:03d}_math.json')
        col = saved(run/f'final_{i:03d}_collision_raw_response.json')
        response = byindex[i];q = response['q12'];trace = bykey[(factor,'trace',case)]['trace']
        ck('physical', str(i)+' exact source final and summaries', exact(f,finals[i]) and exact(q,f['q12'])
           and f['dispatch_index'] == i and f['source_returned'] is response['returned'] and f['stage'] == 'COMPLETED')
        ck('physical', str(i)+' math fields unchanged', all(exact(fm[k],f[k]) for k in fm if k != 'stage'))
        for arm in (1,2):
            savedpose = saved(run/f'final_{i:03d}_arm{arm}.json')
            ck('physical', str(i)+' arm'+str(arm)+' pose exact', exact(savedpose['poses'],f['poses'][:arm]))
        a,b = f['poses'];length = 300. if fixture['environment']=='II' else 500.
        pos = max(abs(b[j][3]-(a[j][3]+a[j][0]*length)) for j in range(3))
        rot = max(abs(b[j][k]-a[j][k]*(-1. if k < 2 else 1.)) for j in range(3) for k in range(3))
        # BLAS multiplication association may differ in the final few bits.
        ck('physical', str(i)+' saved matrix residual independent arithmetic', math.isclose(pos,f['closure']['position_max_abs'],abs_tol=2e-12,rel_tol=2e-12)
           and math.isclose(rot,f['closure']['rotation_matrix_max_abs'],abs_tol=2e-15,rel_tol=2e-12))
        closed = pos <= 1e-5 and rot <= 1e-5
        bounds = [(lo*3.1416/180.,hi*3.1416/180.) for lo,hi in degrees]
        violations = [{'index':j,'q_rad':x,'lower_rad':lo,'upper_rad':hi} for j,(x,(lo,hi)) in enumerate(zip(q,bounds)) if not lo <= x <= hi]
        legal = not violations
        ck('physical', str(i)+' literal limit qualifications', f['closed'] is closed and f['limits']['legal'] is legal
           and exact(f['limits']['violations'],violations) and f['limits']['source_literal_pi_preserved'] == 3.1416)
        marks = [t['args'] for t in trace if t['event']=='observed' and t['kind']=='identify_completed_in_helper'
                 and exact(join(t['args']),q)]
        if marks:
            last = marks[-1]; labels = last['ik'];direct=last['branch']
            identity = {'status':'OBSERVED_MATCHING_FINAL_CANDIDATE','source_identify_ik':labels,
                        'direct_branch':direct,'loop_index':last['loop_index']}
            direct_ok = direct in f['branches'][1-fixture['active_chain']]['branch_set']
            dual_ok = all(type(label) in (int,float) and label in range(8) and label in f['branches'][1-j]['branch_set'] for j,label in enumerate(labels))
        else:
            identity = {'status':'NOT_OBSERVED','source_identify_ik':None,'direct_branch':None}
            direct_ok=dual_ok=None
        ck('branch_evidence', str(i)+' saved final source labels exact', exact(identity,f['source_identity'])
           and f['direct_branch_membership'] is direct_ok and f['dual_source_label_membership'] is dual_ok)
        for arm, branch in enumerate(f['branches']):
            elbow_sign, wrist_sign = (1,-1,1,-1,1,-1,1,-1),(1,-1,-1,1,-1,1,1,-1)
            expected_set = [j for j in range(8) if
                            (branch['shoulder_sign'] is None or branch['shoulder_sign'] == (1 if j<4 else -1)) and
                            (branch['elbow_sign'] is None or branch['elbow_sign'] == elbow_sign[j]) and
                            (branch['wrist_sign'] is None or branch['wrist_sign'] == wrist_sign[j])]
            ck('branch_evidence', str(i)+' arm'+str(arm+1)+' saved sign-to-set exact', branch['branch_set'] == expected_set
               and branch['unique'] is all(branch[k] is not None for k in ('shoulder_sign','elbow_sign','wrist_sign')))
        ck('collision', str(i)+' retained adapter exact', exact(col,f['collision']) and col['status']=='CHECKED'
           and col['selected_variant']=='aligned' and col['continuous_collision_certificate'] is False
           and col['manifest_sha256']==p['bound_files_sha256'][col['manifest_path']] and set(col['variants'])=={'native','aligned'})
        for variant, row in col['variants'].items():
            codes=row['query_codes'];aggregate[variant+'_PQP_queries']+=len(codes)
            ck('collision', str(i)+' '+variant+' query results', bool(codes) and all(type(v) is int and v == 0 for v in codes)
               and row['native_result'] in (0,1) and row['native_collision'] is bool(row['native_result']))
            worker = saved(run/f'collision_worker_{2*i+(variant=="aligned"):03d}_raw_response.json')
            ck('collision', str(i)+' '+variant+' raw worker fields exact', all(exact(v,row[k]) for k,v in worker.items()))
            rawrows=[json.loads(s.split(' ',1)[1]) for s in row['source_stdout'].splitlines() if s.startswith('P4_COLLISION_RESULT ')]
            ck('collision', str(i)+' '+variant+' raw marker exact', len(rawrows)==1 and all(exact(v,worker[k]) for k,v in rawrows[0].items()))
            pc=row['pose_consistency']; independent_ok=True
            for err in pc['errors']:
                collision_tcp, independent_tcp = err['collision_TCP'],err['independent_TCP']
                xyz=max(abs(collision_tcp[j][3]-independent_tcp[j][3]) for j in range(3))
                rotation=max(abs(collision_tcp[j][k]-independent_tcp[j][k]) for j in range(3) for k in range(3))
                passed=xyz<=1e-5 and rotation<=1e-5;independent_ok &= passed
                ck('collision', str(i)+' '+variant+' TCP saved arithmetic arm'+str(err['arm']),
                   exact(xyz,err['translation_maxabs_mm']) and exact(rotation,err['rotation_maxabs']))
            ck('collision', str(i)+' '+variant+' TCP gate preserved', pc['passed'] is independent_ok)
            aggregate[variant+'_TCP_pass']+=independent_ok
            aggregate[variant+'_collision']+=row['native_collision']
        active_ok=exact(q[6*fixture['active_chain']:6*(fixture['active_chain']+1)],fixture['q12'][6*fixture['active_chain']:6*(fixture['active_chain']+1)])
        clear=not col['collision'];physical=closed and legal and active_ok and clear
        branch_ok=direct_ok is True and dual_ok is True;allgates=physical and branch_ok
        sound=not response['returned'] or (closed and active_ok and branch_ok)
        ck('physical', str(i)+' separated qualifications exact', f['active_input_unchanged'] is active_ok
           and f['physical_closed_and_limits'] is (closed and legal) and f['source_true_math_sound'] is sound
           and f['physical_final_qualified'] is physical and f['source_branch_relation_qualified'] is branch_ok
           and f['final_candidate_all_gates_qualified'] is allgates and f['source_success_fully_qualified'] is (response['returned'] and allgates)
           and f['source_policy_discrete_collision_free'] is clear and col['collision'] is col['variants']['aligned']['native_collision'])
        ck('physical', str(i)+' source true independent soundness', sound)
        for key,value in {'closed':closed,'legal':legal,'clear':clear,'physical':physical,'branch_relation':branch_ok,'allgates':allgates,
                          'source_true':response['returned'],'source_success_qualified':response['returned'] and allgates}.items():
            aggregate[factor+'_'+key]+=value
        metrics.append({'dispatch_index':i,'factor':factor,'mode':mode,'case_id':case,'source_returned':response['returned'],
                        'position_maxabs_mm':pos,'rotation_maxabs':rot,'closed':closed,'limits_legal':legal,'aligned_clear':clear,
                        'direct_branch_membership':direct_ok,'dual_source_label_membership':dual_ok,'physical_qualified':physical,
                        'all_gates_qualified':allgates,'source_true_math_sound':sound})
    events = jsonl(run/'events.jsonl')
    ec=Counter(x['event'] for x in events)
    ck('events', 'expected stopped event classification', ec['stopped']==int(stopped))
    exact_counts={'helper_dispatch_started':64,'helper_response_line_observed':64,'helper_completed':64,
                  'math_arm_FK_started':128,'math_arm_FK_completed':128,'final_metric_started':64,'final_metric_completed':64,
                  'collision_started':64,'collision_response_retained':64,'final_gate_completed':64,
                  'collision_native_worker_query_started':128,'collision_native_worker_query_completed':128,
                  'adapter_arm_FK_J_started':256,'adapter_arm_FK_J_completed':256,'helper_session_started':8}
    if stopped:
        exact_counts.update(math_arm_FK_started=70,math_arm_FK_completed=70,final_metric_started=35,final_metric_completed=35,
                            collision_started=35,collision_response_retained=34,final_gate_completed=34,
                            collision_native_worker_query_started=70,collision_native_worker_query_completed=70,
                            adapter_arm_FK_J_started=139,adapter_arm_FK_J_completed=139)
    for kind,n in exact_counts.items():ck('events', kind+' actual count',ec[kind]==n)
    unknown=saved(run/'unknown_tail.json')
    ck('completion', 'all64 helper complete and exact final prefix/tail', e['completed_helper_ids']==e['source_response_validation_passed_ids']==list(range(64))
       and e['completed_final_ids']==list(range(34 if stopped else 64)) and e['uncompleted_helper_fixtures']==unknown['helper']==[]
       and e['uncompleted_final_fixtures']==unknown['final']==(schedule[34:] if stopped else [])
       and e['inflight_unreturned_helper'] is None and e['dispatch_attempt_incomplete_or_unknown'] is False)
    ck('completion', 'counts preserved', e['plain_trace_comparison_cases']==32 and e['control_prefix_comparison_cases']==16
       and e['independent_final_cases']==(34 if stopped else 64) and e['source_true_count']+e['source_false_count']==64)
    ck('completion', 'source observed aggregate exact', e['source_trace_stream_observed']['started']==dict(trace_started)
       and e['source_trace_stream_observed']['completed']==dict(trace_completed) and e['source_trace_stream_observed']['marks']==dict(trace_marks))
    rawprefix=saved(run/'source_trace_prefixes_saved.json')
    for factor in ('source_control','success_break'):
        for mode in ('plain','trace'):
            for env in ('II','III'):
                label='/'.join((factor,mode,env));stem=run/'runtime'/('_'.join((factor,mode,env)))
                fixtures=[x for x in schedule if (x['factor'],x['mode'],x['environment'])==(factor,mode,env)]
                expected_trace=[ev for x in fixtures for ev in (byindex[x['dispatch_index']]['trace'] or [])]
                stderr=jsonl(stem.with_suffix('.stderr'),b'P4_HELPER_TRACE ')
                stdout=jsonl(stem.with_suffix('.stdout'))
                ck('raw_streams', label+' raw stderr exact full trace', exact(stderr,expected_trace)
                   and exact(rawprefix[label]['events'],stderr) and rawprefix[label]['tails']==[])
                ck('raw_streams', label+' stdout all8 exact responses', exact(stdout,[byindex[x['dispatch_index']] for x in fixtures]))
                row=e['source_raw_trace_bindings'][label];cleanup=e['session_cleanup'][label]
                ck('raw_streams', label+' EOF and no unknown tail', row['complete_raw_evidence_gate'] is True
                   and row['raw_trace_equals_completed_responses_binary64'] is True and row['pipe_eof_drained'] is True
                   and row['cleanup_closed'] is True and row['unparseable_trace_tail_count']==row['unexpected_stdout_tail_bytes']==0
                   and row['expected_completed_response_trace_events']==row['actual_raw_trace_events']==len(stderr)
                   and row['completed_response_dispatch_indexes']==[x['dispatch_index'] for x in fixtures]
                   and cleanup['cleanup_closed'] is cleanup['pipe_eof_drained'] is True and cleanup['pending_stdout_bytes']==0)
    expected_diagnostics=[{'stage':'stopped_partial_candidate','error':"TimeoutError('H_AGGREGATE_HARD_WALL_CAP')"}] if stopped else []
    ck('completion', 'complete source raw gate and diagnostics preserved', e['complete_source_raw_evidence_gate'] is True and e['diagnostics']==expected_diagnostics)
    for key, count in {'physical_final_qualified':sum(x['physical_qualified'] for x in metrics),
                       'final_candidate_all_gates_qualified':sum(x['all_gates_qualified'] for x in metrics),
                       'source_success_fully_qualified':sum(x['source_returned'] and x['all_gates_qualified'] for x in metrics),
                       'source_true_count':sum(x['returned'] for x in byindex.values())}.items():
        ck('summaries', key+' independently counted',e[key]==count)
    stop_evidence = {}
    if stopped:
        fm=saved(run/'final_034_math.json');col=saved(run/'final_034_collision_raw_response.json')
        partial=saved(run/'stopped_partial_candidate.json')
        ck('stop_tail', 'original timed cap and stage', e['termination_reason']=="TimeoutError('H_AGGREGATE_HARD_WALL_CAP')"
           and e['termination_stage']=='INDEPENDENT_FINAL_GATES' and e['unresolved_tail_status']=='UNKNOWN_NOT_EXECUTED_OR_NOT_COMPLETED_NO_PREFIX_PASS')
        ck('stop_tail', '35th math exists but final absent', fm['dispatch_index']==34 and fm['stage']=='MATH_COMPLETED'
           and fm['closed'] is fm['source_true_math_sound'] is True and not (run/'final_034.json').exists())
        ck('stop_tail', 'adapter error exact preserved complete JSON', col['status']=='COLLISION_ADAPTER_ERROR'
           and col['error']==e['termination_reason'] and col['collision'] is None and set(col['variants'])=={'native'})
        ck('stop_tail', 'partial durable JSON survived repeated timer', partial['stage']=='COLLISION_STARTED'
           and all(exact(partial[k],fm[k]) for k in fm if k!='stage'))
        for i in (68,69):
            worker=saved(run/f'collision_worker_{i:03d}_raw_response.json')
            ck('stop_tail', str(i)+' retained worker raw integer zero codes', bool(worker['query_codes'])
               and all(type(v) is int and v==0 for v in worker['query_codes']))
        stop_evidence={'original_status':e['status'],'original_termination_reason':e['termination_reason'],
                       'original_diagnostics':e['diagnostics'],'completed_final_count':len(metrics),
                       '35th_math_complete':True,'35th_adapter_status':col['status'],
                       '35th_adapter_variants_retained':list(col['variants']),'35th_aligned_worker_raw_retained':True,
                       '35th_adapter_pose_fk_j_started_completed':139,'35th_required_adapter_pose_fk_j_total_for35':140,
                       'unknown_final_dispatch_indexes':[x['dispatch_index'] for x in unknown['final']],
                       'original_qualification_promoted':False}
    ck('provenance', 'all read retained bytes unchanged at end', all(sha(name)==wanted for name,wanted in retained.items()))
    report={'schema':'P4_ABB_HELPER_H_PERSONNEL_INDEPENDENT_STDLIB_SAVED_POST_V1',
            'status':('PASS_SAVED_STOP_PREFIX_AUDIT_ORIGINAL_QUALIFICATION_STOP_UNCHANGED' if stopped else 'PASS_SAVED_EVIDENCE_AUDIT') if not failed else 'FAIL_SAVED_EVIDENCE_AUDIT',
            'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'personnel_independent':True,'run':str(run.relative_to(ROOT)),'source_execution_sha256':sha(run/'execution.json'),
            'audit_script':str(Path(__file__).relative_to(ROOT)),'audit_script_sha256':sha(__file__),
            'checks_total':sum(v['total'] for v in groups.values()),'checks_passed':sum(v['passed'] for v in groups.values()),
            'checks_failed':len(failed),'groups':dict(groups),'failures':failed,
            'prior_execution_count':len(priors),'previous_r2_wall_s':wall,'previous_r2_cpu_s':cpu,
            'own_h_wall_s':e['wall_s'],'own_h_cpu_s':e['cpu_s'],'aggregate_saved_evidence':dict(aggregate),
            'original_stop_evidence':stop_evidence,
            'observed_source_trace_started':dict(trace_started),'observed_source_trace_completed':dict(trace_completed),
            'observed_source_trace_marks':dict(trace_marks),'source_branch_attempts':dict(branch_attempts),
            'retained_read_file_count':len(retained),'retained_read_sha256':retained,'final_candidates':metrics,
            'zero_new_calls':dict.fromkeys(('helper','FK','IK','Jacobian','NR','PQP','RNG','compile','VI_constructions','planner','formal_Table_I'),0),
            'limitations':['All evidence predates this audit; no fresh geometric branch invariant or model query was run.',
                           'Saved independent branch signs are checked against their sets and actual final source labels; original raw source traces are retained.',
                           'Final source false outputs are audited too; physical rejection is an observed outcome, not automatically an interface failure.',
                           'Discrete source collision policy only; native TCP mismatch, if present, is preserved.',
                           'This qualifies a fixed local helper interface, not ambient sampling distribution, planner success, PCS advantage, or faithful original algorithm.',
                           'Formal statistics remain 0/22500; VI candidate budget remains 974/974.']}
    with out.open('x') as stream:json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    text=(f"# ABB helper H 人员独立保存证据后审\n\n"
          f"**{report['status']}**：{report['checks_passed']}/{report['checks_total']}，失败{len(failed)}。"
          "仅 stdlib 保存证据审计，0 新科学调用、0 编译、0 helper 派发。\n\n"
          f"64 个原始 helper 请求、32 组 plain/trace、16 组首成功控制流前缀，以及{len(metrics)}个完整终态的保存矩阵、"
          "原始机械界、几何分支集合、native/aligned 碰撞与完整 pipe EOF 逐项核对。"
          "源码布尔返回值、物理资格、分支资格分别保留；普通限位/碰撞拒绝不改为通过。\n\n"
          f"本次 H 实账 {e['wall_s']:.9f} 秒墙钟、{e['cpu_s']:.9f} 秒 CPU；"
          f"此前 {len(priors)} 笔原 execution 合计 {wall:.9f}/{cpu:.9f} 秒。"
          ("原始资格 STOP 及30个 UNKNOWN 终态保持；第35数学结果完整、adapter错误JSON与raw worker保留，但不补称final通过。" if stopped else "")+
          "该结论仅限保存证据审计；不能替代完整局部资格、规划入口、分布资格、连续无碰撞或正式统计。"
          "人员独立后审未重算机器人 FK/IK/Jacobian 或调用 PQP。逐项结果与完整 SHA 绑定见同名 JSON。\n")
    with out.with_suffix('.md').open('x') as stream:stream.write(text)
    print(json.dumps({k:report[k] for k in ('status','checks_total','checks_passed','checks_failed','retained_read_file_count')},ensure_ascii=False))


if __name__ == '__main__':
    main()
