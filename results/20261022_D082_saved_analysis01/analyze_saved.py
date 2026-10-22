#!/usr/bin/env python3
"""Derive D082 statistics from frozen saved records; no planning/model calls."""
from pathlib import Path
import collections, csv, datetime, gzip, hashlib, json, math, statistics, time

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
START_WALL=time.perf_counter();START_CPU=time.process_time()
OLD=ROOT/'results/20261019_D081_stability_pilot'
NUM=ROOT/'results/20261019_D081_numeric_pilot'

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(name,d):
    (OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def csvout(name,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def counterstr(c):return json.dumps(dict(c),ensure_ascii=False,sort_keys=True)
def branch(q,p):
    x=math.sin(q[p+1]);return 0 if abs(x)<=1e-10 else (1 if x>0 else -1)
def mean(x):return statistics.mean(x) if x else None
def wilson(k,n):
    z=1.959963984540054;a=z*z/n;v=(k/n+a/2)/(1+a);b=z*math.sqrt(k/n*(1-k/n)/n+z*z/(4*n*n))/(1+a)
    return max(0.,v-b),min(1.,v+b)

index=list(csv.DictReader((OLD/'planner_trials.csv').open()))
assert len(index)==50
trials=[];transitions=[];solution_edges=[];singular=[];failures=[];counterrows=[];rawhash={};payloads={}
for ix in index:
    p=OLD/ix['artifact'];rawhash[str(p.relative_to(ROOT))]=sha(p)
    with gzip.open(p,'rt',encoding='utf-8') as f:d=json.load(f)
    identity={'environment':d['environment'],'method':d['method'],'seed':d['seed']}
    assert d['status']==ix['status']
    payloads[(d['environment'],d['method'],d['seed'])]=d
    accepted=collections.Counter(a.get('edge_partition') for a in d['attempts'] if a.get('accepted'))
    validtrans=collections.Counter()
    nroots=0
    for side,nodes in d['trees'].items():
        for ni,node in enumerate(nodes):
            if node['parent'] is None:nroots+=1;continue
            parent=nodes[node['parent']]
            incoming=d['attempts'][node['incoming_attempt']]
            prior=None if parent['incoming_attempt'] is None else d['attempts'][parent['incoming_attempt']]
            part=incoming.get('edge_partition');previous=None if prior is None else prior.get('edge_partition')
            comparable=prior is not None and part is not None and previous is not None
            if comparable:validtrans[(previous,part)]+=1
            transitions.append({**identity,'tree':side,'node':ni,'parent_node':node['parent'],
                'incoming_attempt':node['incoming_attempt'],'parent_incoming_attempt':parent['incoming_attempt'],
                'partition':part,'parent_partition':previous,'parent_is_root':prior is None,
                'partition_comparable':comparable,'partition_changed':comparable and part!=previous,
                'edge_branch':incoming.get('edge_branch')})
    parts=[e['partition'] for e in d['path_edges']]
    changes=sum(a is not None and b is not None and a!=b for a,b in zip(parts,parts[1:]))
    for ei,e in enumerate(d['path_edges']):solution_edges.append({**identity,'edge_order':ei,**e})
    m=d.get('path_metrics') or {}
    dense_branches={p:[branch(q,p) for q in d['path']] for p in (0,16)}
    dense_branch_changes={p:sum(a!=b for a,b in zip([v for v in seq if v],[v for v in seq if v][1:])) for p,seq in dense_branches.items()}
    tr={**identity,'status':d['status'],'terminal_reason':d['terminal_reason'],
        'compute_wall_sec':d['compute_wall_time_sec'],'serialization_inclusive_wall_sec':float(ix['serialization_inclusive_wall_sec']),
        'cpu_sec':None,'node_count':d['node_count'],'path_point_count':len(d['path']),
        'path_length_rad':m.get('joint_path_length_rad'),'maximum_position_residual_m':m.get('maximum_position_residual_m'),
        'maximum_rotation_residual_rad':m.get('maximum_rotation_residual_rad'),
        'minimum_joint_margin_rad':m.get('minimum_joint_margin_rad'),'minimum_clearance_m':m.get('minimum_clearance_m'),
        'maximum_adjacent_l2_rad':m.get('maximum_adjacent_l2_rad'),
        'accepted_p0_edges':accepted[0],'accepted_p16_edges':accepted[16],
        'parent_child_partition_comparisons':sum(validtrans.values()),
        'parent_child_partition_changes':sum(v for (a,b),v in validtrans.items() if a!=b),
        'parent_child_transition_counts':counterstr({f'{a}->{b}':v for (a,b),v in validtrans.items()}),
        'solution_edge_partition_sequence':json.dumps(parts),'solution_partition_changes':changes,
        'dense_path_p0_nonzero_branch_changes':dense_branch_changes[0],
        'dense_path_p16_nonzero_branch_changes':dense_branch_changes[16],
        'start_branch_p0':branch(d['start'],0),'goal_branch_p0':branch(d['goal'],0),
        'start_branch_p16':branch(d['start'],16),'goal_branch_p16':branch(d['goal'],16),
        'singular_requests':d['counters'].get('singular_sample_requests',0),
        'singular_construction_attempts':len(d['singular_log']),
        'accepted_singular_targets':sum(bool(s.get('success')) for s in d['singular_log']),
        'source':str(p.relative_to(ROOT))}
    trials.append(tr)
    for k,v in d['counters'].items():counterrows.append({**identity,'counter':k,'count':v})
    for k,v in d['failure_counts'].items():failures.append({**identity,'category':'strategy_failure_counts','reason':k,'count':v})
    for k,v in collections.Counter(a.get('reason') for a in d['attempts'] if not a.get('accepted')).items():
        failures.append({**identity,'category':'rejected_tree_growth_attempt','reason':k,'count':v})
    for si,s in enumerate(d['singular_log']):
        q=s.get('raw_q');qual=s.get('qualification')
        singular.append({**identity,'construction_index':si,'within_request_attempt':s['attempt'],
            'generator_partition':s['generator_partition'],'rss_partition':s['rss_partition'],
            'generator_branch':s['generator_branch'],'ik_reason':s['reason'],'accepted':s['success'],
            'raw_middle_angle_rad':q[17] if q else None,
            'raw_middle_abs_sine':abs(math.sin(q[17])) if q else None,
            'closed_configuration_saved':s.get('q') is not None,
            'closed_qualification_reason':qual.get('reason') if qual else None,
            'closed_passive_jacobian_rank':None,
            'rank_status':'NOT_EVALUATED_IK_REJECTED' if s.get('q') is None else 'NOT_SAVED'})

summaryrows=[]
for env in sorted({r['environment'] for r in trials}):
 for method in ['RSS','PCS','PCS_FIXED_0','PCS_FIXED_16','NR']:
    rs=[r for r in trials if r['environment']==env and r['method']==method];ok=[r for r in rs if r['status']=='SUCCESS']
    lo,hi=wilson(len(ok),len(rs));st=collections.Counter(r['status'] for r in rs)
    summaryrows.append({'environment':env,'method':method,'n':len(rs),'success':len(ok),'timeout':st['TIME_LIMIT'],
        'other_failure':len(rs)-len(ok)-st['TIME_LIMIT'],'success_rate':len(ok)/len(rs),
        'wilson_ci95_low':lo,'wilson_ci95_high':hi,'mean_wall_sec_all_calls':mean([r['compute_wall_sec'] for r in rs]),
        'mean_success_wall_sec':mean([r['compute_wall_sec'] for r in ok]),
        'mean_success_path_length_rad':mean([r['path_length_rad'] for r in ok]),
        'mean_nodes_all_calls':mean([r['node_count'] for r in rs]),
        'parent_child_partition_changes':sum(r['parent_child_partition_changes'] for r in rs),
        'successful_solution_partition_changes':sum(r['solution_partition_changes'] for r in ok)})

fa=collections.Counter()
for r in failures:fa[(r['method'],r['category'],r['reason'])]+=r['count']
aggregate_fail=[{'method':m,'category':c,'reason':r,'count':n} for (m,c,r),n in sorted(fa.items())]
ca=collections.Counter()
for r in counterrows:ca[(r['method'],r['counter'])]+=r['count']
aggregate_counter=[{'method':m,'counter':c,'count':n} for (m,c),n in sorted(ca.items())]
fig3=list(csv.DictReader((NUM/'fig3_pairs.csv').open()))
projection=list(csv.DictReader((NUM/'projection_trials.csv').open()))
nr_trace_lengths=[int(r['iterations']) for r in projection if r['method']=='NR']
fig4=list(csv.DictReader((NUM/'fig4_visibility_pairs.csv').open()))
fig3diag=[]
for m in sorted({int(x['m']) for x in fig3}):
 rs=[x for x in fig3 if int(x['m'])==m];dist=[float(x['distance_rad']) for x in rs]
 fig3diag.append({'m':m,'pairs':len(rs),'successes':sum(x['success']=='True' for x in rs),
    'mean_distance_rad':mean(dist),'minimum_distance_rad':min(dist),'maximum_distance_rad':max(dist),
    'zero_distance_pairs':sum(v==0. for v in dist),
    'sampling_population':'new states generated for each m, fixed branch -1 over starts range(m)'})
paired=[]
for method in ['RSS','PCS','PCS_FIXED_0','PCS_FIXED_16','NR']:
 for seed in [7,23,41,59,73]:
    a=payloads[('E0_sparse',method,seed)];b=payloads[('E1_clutter',method,seed)]
    paired.append({'method':method,'seed':seed,'same_terminal_status':a['status']==b['status'],
        'both_success':a['status']==b['status']=='SUCCESS',
        'successful_paths_exactly_equal':a['status']==b['status']=='SUCCESS' and a['path']==b['path']})

sources=['baselines/p4_comparison/model.py','baselines/p4_comparison/strategies.py','baselines/p4_comparison/planner.py',
 'scripts/p4_d081_numeric_pilot.py','scripts/p4_d081_stability_pilot.py','configs/p4_d081/numeric_pilot_v1.json',
 'configs/p4_d081/numeric_stability_pilot_v1.json','results/20261019_D081_stability_pilot/config_snapshot.json',
 'results/20261019_D081_stability_pilot/run_metadata.json','results/20261019_D081_stability_pilot/planner_summary.json',
 'results/20261019_D081_stability_pilot/planner_trials.csv','results/20261019_D081_numeric_pilot/summary.json',
 'results/20261019_D081_numeric_pilot/math_summary.json','results/20261019_D081_numeric_pilot/fig3_pairs.csv',
 'results/20261019_D081_numeric_pilot/projection_trials.csv',
 'results/20261019_D081_numeric_pilot/fig3_state_generation.json','results/20261019_D081_numeric_pilot/fig4_visibility_pairs.csv',
 'results/20261019_D081_numeric_pilot/fig5_distance_change.csv','results/20261013_P4_three_methods_round3/math_evidence.json',
 'reports/P4_THREE_METHOD_CORRECTION_01.md','reports/P4_THREE_METHOD_CORRECTION_02.md','reports/P4_THREE_METHOD_CORRECTION_03.md',
 'reports/P4_THREE_METHOD_POST_TASK.md','work/d081_p4_text/P4_original.txt']
sourcehash={s:sha(ROOT/s) for s in sources}
mathdata=load(NUM/'math_summary.json');oldmath=load(ROOT/'results/20261013_P4_three_methods_round3/math_evidence.json')
bridge=oldmath['rss_registered_bridge']
rank_evidence={'d081_saved_fixture':mathdata['singular_fixture'],
 'd065_saved_hand_constructed_bridge':{'source':'results/20261013_P4_three_methods_round3/math_evidence.json',
    'passive_jacobian':bridge['passive_jacobian'],'determinant':bridge['determinant'],
    'singular_values':bridge['singular_values'],'middle_angle_rad':bridge['middle_angle_rad'],
    'qualification':bridge['qualification'],'left_success':bridge['left_connection']['success'],
    'right_success':bridge['right_connection']['success'],'two_branch_bridge_qualified':bridge['two_branch_bridge_qualified']},
 'random_sampler_rank_evidence':'0 accepted closed singular candidates; raw rejected candidates lack closed Jacobian rank evidence. No new rank/IK/qualification calls performed.'}

csvout('per_trial_metrics.csv',trials);csvout('tree_parent_child_partitions.csv',transitions)
csvout('solution_edge_partitions.csv',solution_edges);csvout('singular_attempts.csv',singular)
csvout('failure_counts_per_trial.csv',failures);csvout('failure_aggregates.csv',aggregate_fail)
csvout('counter_aggregates.csv',aggregate_counter);csvout('method_environment_summary.csv',summaryrows)
csvout('fig3_population_diagnostics.csv',fig3diag);csvout('paired_environment_path_equality.csv',paired)
save('saved_rank_and_bridge_evidence.json',rank_evidence);save('input_sha256.json',{**sourcehash,**rawhash})
metadata=load(OLD/'run_metadata.json')
summary={'schema':'P4_D082_SAVED_ANALYSIS01_V1','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'input_calls':50,'unique_seeds':[7,23,41,59,73],'conditions':10,
    'successes':sum(r['status']=='SUCCESS' for r in trials),'timeouts':sum(r['status']=='TIME_LIMIT' for r in trials),
    'new_scientific_calls':{'planner':0,'RSS':0,'PCS':0,'NR':0,'RBS':0,'FK':0,'IK':0,'collision':0,'rank':0},
    'method_environment_summary':summaryrows,
    'tree_parent_child_partition_changes_full_pcs':sum(r['parent_child_partition_changes'] for r in trials if r['method']=='PCS'),
    'solution_partition_changes_full_pcs':sum(r['solution_partition_changes'] for r in trials if r['method']=='PCS'),
    'rss':{'requests':sum(r['singular_requests'] for r in trials if r['method']=='RSS'),
        'attempts':len(singular),'ik_reasons':dict(collections.Counter(r['ik_reason'] for r in singular)),
        'accepted_closed_targets':sum(r['accepted'] for r in singular),'rank_qualified_random_targets':0,
        'raw_middle_angle_counts':dict(collections.Counter(str(r['raw_middle_angle_rad']) for r in singular)),
        'raw_max_abs_sine_middle_angle':max(r['raw_middle_abs_sine'] for r in singular)},
    'same_paths_across_environments':sum(r['successful_paths_exactly_equal'] for r in paired),
    'both_success_pairs':sum(r['both_success'] for r in paired),
    'nr_projection_trace_mean_length':mean(nr_trace_lengths),
    'nr_projection_actual_newton_updates_mean':mean([n-1 for n in nr_trace_lengths]),
    'nr_iteration_semantics':'saved iterations counts residual trace entries including initial/terminal; all 768 converge, so updates = entries minus one',
    'fig4_zero_distance_rows':sum(float(r['distance_rad'])==0. for r in fig4),
    'fig4_zero_distance_pairs':sum(float(r['distance_rad'])==0. for r in fig4 if r['method']=='NR'),
    'saved_compute_wall_sec_sum':sum(r['compute_wall_sec'] for r in trials),
    'saved_run_wall_sec':load(OLD/'planner_summary.json')['elapsed_wall_sec'],
    'saved_cpu_time':'NOT_RECORDED; do not infer from wall time',
    'baseline_numeric_20_calls':'seeds 7/23 overlap; do not count as additional independent seeds',
    'source_hash_matches_saved':{s:sourcehash[s]==h for s,h in metadata['source_files'].items()},
    'same_root_engineering_corrections':{'D065_used':3,'D065_cap':3,'new_corrections_in_this_analysis':0,
        'D065_round0':'pre-logger filename failure, zero scientific calls',
        'D065_round1':'17 tests, 1 numeric singular-identity failure; zero comparison calls',
        'D065_round2':'17 tests pass; 1 RSS timeout preserved; PCS raw serialization interrupted',
        'D065_round3':'60 statistical calls plus 3 repeat calls, no further correction allowance'},
    'limitations':['Postprocessing saved evidence is not independent numerical revalidation.',
        'Five seed pairs per environment are small; environments share endpoints, so do not claim 10 independent seeds.',
        'Time-limit records are right-censored failures, not measured solve times.',
        'No continuous swept collision claim.',
        'Fixed p16 has opposite start/goal branch labels and no singular sampler; treat as structural negative control.',
        'Figure 3 m groups resample distinct populations; observed trend is not a controlled causal m ablation.'],
    'analysis_wall_sec':time.perf_counter()-START_WALL,'analysis_cpu_sec':time.process_time()-START_CPU}
save('summary.json',summary)
print(json.dumps({k:summary[k] for k in ['input_calls','successes','timeouts','tree_parent_child_partition_changes_full_pcs','solution_partition_changes_full_pcs','rss','analysis_wall_sec','analysis_cpu_sec']},ensure_ascii=False))
