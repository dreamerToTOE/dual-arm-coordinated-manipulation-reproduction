#!/usr/bin/env python3
"""Engineering-only continuation of the frozen D083 batch after JSON failure.

Never rerun C1/PCS/seed7, never reconstruct its lost scientific output, never
repeat the three saved witness/route diagnostics. Run only after static review.
The original 180wall/240CPU envelope charges the failed run before this one.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import gzip
import importlib.util
import json
from pathlib import Path
import signal
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
CONFIG = ROOT/'configs/p4_d083/difficult_v1.json'
FAILED = ROOT/'results/20261022_D083_difficult01'
OUTPUT = ROOT/'results/20261022_D083_difficult02'
FIRST = ('C1',7,'PCS')


def load_helpers():
    source = ROOT/'scripts/p4_d083/bounded_difficulty.py'
    spec = importlib.util.spec_from_file_location('d083_frozen_helpers',source)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def json_default(value):
    if isinstance(value,np.generic):
        return value.item()
    if isinstance(value,np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def figure(out,rows,diagnostics):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes = plt.subplots(1,2,figsize=(11,4.3))
    methods = ['PCS','COMPATIBLE_FIXED','NR','RSS']
    for i,method in enumerate(methods):
        group = [r for r in rows if r['registered_method']==method and r['executed']]
        evaluable = [r for r in group if r['artifact_complete']]
        unknown = len(group)-len(evaluable)
        success = sum(r['independently_qualified'] is True for r in evaluable)
        rate = success/len(evaluable) if evaluable else 0
        axes[0].bar(i,rate,color=['#177caa','#6e9d34','#bf7a20','#8e6dad'][i])
        label = f'{success}/{len(evaluable)}'+(f' + {unknown} unknown' if unknown else '')
        axes[0].text(i,rate+.03,label,ha='center',fontsize=9)
    axes[0].set_xticks(range(4),['PCS','fixed compatible','NR','RSS'],rotation=20)
    axes[0].set_ylim(0,1.18)
    axes[0].set_ylabel('Qualified success / evaluable complete artifacts')
    axes[0].set_title('Three archival conditions; paired seeds 7/23/41')
    for c in diagnostics:
        for d in c['direct_candidates']:
            label = 'NR' if d['partition'] is None else f"p{d['partition']}"
            axes[1].scatter(c['id']+' '+label,d['independent']['minimum_clearance_m'],
                            marker='x' if d['projection_failure'] else 'o',s=55)
    axes[1].axhline(0,color='black',lw=.8)
    axes[1].set_ylabel('Saved independent candidate minimum clearance / m')
    axes[1].set_title('Candidate diagnostics; projection failure shown as x')
    axes[1].tick_params(axis='x',rotation=45)
    fig.suptitle('D083 bounded diagnostic; no general hard-benchmark inference')
    fig.tight_layout()
    fig.savefig(out/'difficult_diagnostic.png',dpi=180)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if not args.execute:
        raise SystemExit('Execution requires --execute after independent static review')
    if OUTPUT.exists():
        raise SystemExit('Refusing to overwrite '+str(OUTPUT))
    h=load_helpers()
    cfg=json.loads(CONFIG.read_text())
    failure=json.loads((FAILED/'engineering_failure.json').read_text())
    if failure['scientific_calls_completed']!=1 or failure['identity']!='C1_PCS_seed7':
        raise RuntimeError('first execution identity is not the frozen failed call')
    first_manifest=json.loads((FAILED/'artifact_sha256.json').read_text())
    if not all(h.sha(FAILED/p)==v for p,v in first_manifest.items()):
        raise RuntimeError('failed-run evidence changed')
    if h.sha(ROOT/'scripts/p4_d083/bounded_difficulty.py')!=failure['frozen_source_sha256']:
        raise RuntimeError('frozen v1 source changed')
    if any(h.sha(ROOT/p)!=v for p,v in cfg['source_sha256'].items()):
        raise RuntimeError('frozen scientific source changed')
    if h.sha(CONFIG)!=h.sha(FAILED/'config_snapshot.json'):
        raise RuntimeError('frozen condition/protocol changed')
    OUTPUT.mkdir(parents=True)
    started,cpu_started=time.perf_counter(),time.process_time()
    remaining_wall=cfg['budget']['stage_wall_sec']-failure['external_wall_sec']
    remaining_cpu=cfg['budget']['stage_process_cpu_sec']-failure['external_cpu_user_plus_sys_sec']

    def guard(*unused):
        if time.perf_counter()-started>=remaining_wall or time.process_time()-cpu_started>=remaining_cpu:
            raise h.BudgetStop('shared stage resource envelope exhausted after charging failed run')

    def alarm(*unused):
        raise h.BudgetStop('shared stage wall envelope exhausted after charging failed run')

    signal.signal(signal.SIGALRM,alarm)
    signal.setitimer(signal.ITIMER_REAL,remaining_wall)
    oracle=h.oracle_module()
    from baselines.p4_comparison.model import PlanarModel
    from baselines.p4_comparison.planner import plan
    diagnostics=json.loads((FAILED/'condition_diagnostics.json').read_text())
    h.save(OUTPUT/'condition_diagnostics.json',diagnostics)
    h.save(OUTPUT/'config_snapshot.json',cfg)
    source_hashes={**cfg['source_sha256'],str(CONFIG.relative_to(ROOT)):h.sha(CONFIG),
                   'scripts/p4_d083/bounded_difficulty.py':failure['frozen_source_sha256'],
                   'scripts/p4_d083/bounded_difficulty_resume.py':h.sha(Path(__file__))}
    h.save(OUTPUT/'run_metadata.json',{
        'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_sha256':source_hashes,'original_failed_run_manifest':first_manifest,
        'remaining_wall_sec':remaining_wall,'remaining_process_cpu_sec':remaining_cpu,
        'prior_failed_external_wall_sec':failure['external_wall_sec'],
        'prior_failed_external_cpu_sec':failure['external_cpu_user_plus_sys_sec'],
        'engineering_change':'NumPy JSON scalar encoder; continue exactly remaining35 calls; no production/scientific changes',
        'reused_saved_diagnostics':'All three independent route/witness diagnostics reused without any scientific recomputation',
        'new_spatial_planner_calls':0,'original_Table_I_calls':0})
    first_artifact=FAILED/'raw_planner/C1_PCS_seed7.json.gz'
    first_wall=float(failure['observed_literal_prefix_fields']['compute_wall_time_sec'])
    rows=[{'condition':'C1','registered_method':'PCS','method':'PCS','seed':7,
           'fixed_partition':diagnostics[0]['fixed_partition'],'executed':True,
           'artifact_complete':False,'status':'UNKNOWN_ARTIFACT_SERIALIZATION_FAILED',
           'independently_qualified':None,'wall_sec':first_wall,
           'artifact':str(first_artifact.relative_to(ROOT)),'artifact_sha256':h.sha(first_artifact),
           'observed_literal_prefix_status':failure['observed_literal_prefix_fields']['status'],
           'terminal_reason':'Real call completed; truncated JSON prefix cannot supply complete scientific evidence; never rerun.'}]
    switch_rows=[]
    stopped=None
    try:
        for condition in diagnostics:
            a,b=np.asarray(condition['endpoints'])
            for seed in cfg['paired_seeds']:
                for registered_method in cfg['method_order']:
                    if (condition['id'],seed,registered_method)==FIRST:
                        continue
                    guard()
                    fixed=condition['fixed_partition']
                    method=f'PCS_FIXED_{fixed}' if registered_method=='COMPATIBLE_FIXED' and fixed is not None else registered_method
                    identity=f"{condition['id']}_{method}_seed{seed}"
                    row={'condition':condition['id'],'registered_method':registered_method,'method':method,
                         'seed':seed,'fixed_partition':fixed,'executed':False,'artifact_complete':False,
                         'status':'NOT_COMPARABLE','independently_qualified':None}
                    rows.append(row)
                    if condition['valid_condition'] and (registered_method!='COMPATIBLE_FIXED' or fixed is not None):
                        model=PlanarModel()
                        model.start,model.goal=a.copy(),b.copy()
                        raw=plan(model,cfg['environment'],method,seed,cfg['budget']['max_iterations_per_call'],cfg['algorithm_config'])
                        raw['d083_scope']=cfg['label']
                        file=OUTPUT/'raw_planner'/f'{identity}.json.gz'
                        file.parent.mkdir(exist_ok=True)
                        with gzip.open(file,'wt') as stream:
                            json.dump(raw,stream,allow_nan=False,default=json_default)
                        tree,parts,switches=h.tree_and_solution_switches(raw)
                        switch_rows.extend({'condition':condition['id'],'method':method,'seed':seed,**x} for x in tree)
                        row.update(executed=True,artifact_complete=True,status=raw['status'],
                            independently_qualified=False,terminal_reason=raw['terminal_reason'],
                            wall_sec=raw['compute_wall_time_sec'],node_count=raw['node_count'],
                            accepted_edges=raw['counters'].get('accepted_edges',0),
                            projection_calls=raw['counters'].get('projection_calls',0),
                            tree_parent_child_switches=sum(x['switch'] for x in tree),
                            solution_switches=switches,solution_partitions=json.dumps(parts),
                            artifact=str(file.relative_to(ROOT)),artifact_sha256=h.sha(file))
                        h.csv_rows(OUTPUT/'planner_trials.csv',rows)
                        if raw['status']=='SUCCESS':
                            try:
                                qualification=h.qualify_success(oracle,raw,a,b,OUTPUT,identity,
                                    cfg['budget']['successful_path_refinement_levels'],guard)
                            except (AssertionError,ValueError) as error:
                                qualification={'qualified':False,'error':str(error),'scope':'INDEPENDENT_CHECK_FAILED'}
                            h.save(OUTPUT/'qualifications'/f'{identity}.json',qualification)
                            row['independently_qualified']=qualification['qualified']
                            row['path_points']=len(raw['path'])
                            row['path_length_rad']=raw['path_metrics']['joint_path_length_rad']
                    h.csv_rows(OUTPUT/'planner_trials.csv',rows)
                    h.csv_rows(OUTPUT/'tree_parent_child_partitions.csv',switch_rows)
                    print(json.dumps(row,default=json_default),flush=True)
    except h.BudgetStop as error:
        stopped=str(error)
        h.save(OUTPUT/'budget_stop.json',{'reason':stopped,'completed_rows':len(rows)})
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
    groups=defaultdict(list)
    for row in rows:
        groups[row['registered_method']].append(row)
    aggregates=[{'registered_method':m,'executed':sum(r['executed'] for r in rs),
                 'evaluable_complete_artifacts':sum(r['artifact_complete'] for r in rs),
                 'artifact_unknown':sum(r['executed'] and not r['artifact_complete'] for r in rs),
                 'source_success':sum(r['status']=='SUCCESS' for r in rs),
                 'independent_success':sum(r['independently_qualified'] is True for r in rs),
                 'mean_wall_sec':float(np.mean([r['wall_sec'] for r in rs if r['executed']])),
                 'tree_switches':sum(r.get('tree_parent_child_switches',0) for r in rs),
                 'solution_switches':sum(r.get('solution_switches',0) for r in rs)} for m,rs in groups.items()]
    h.csv_rows(OUTPUT/'method_summary.csv',aggregates)
    paired=[]
    for condition in cfg['conditions']:
        for seed in cfg['paired_seeds']:
            group={r['registered_method']:r for r in rows if r['condition']==condition['id'] and r['seed']==seed}
            entry={'condition':condition['id'],'seed':seed}
            for method in cfg['method_order']:
                r=group.get(method)
                entry[method+'_status']='NOT_EXECUTED_BUDGET' if r is None else r['status']
                entry[method+'_independent_success']=None if r is None else r['independently_qualified']
            for alternative in ['COMPATIBLE_FIXED','NR','RSS']:
                pcs,other=group.get('PCS'),group.get(alternative)
                entry['PCS_minus_'+alternative+'_wall_sec']=(pcs['wall_sec']-other['wall_sec']
                    if pcs and other and pcs['artifact_complete'] and other['artifact_complete'] else None)
            paired.append(entry)
    h.csv_rows(OUTPUT/'paired_seed_comparison.csv',paired)
    unchanged={p:h.sha(ROOT/p)==v for p,v in source_hashes.items()}
    summary={'schema':'P4_D083_BOUNDED_DIFFICULT_DIAGNOSTIC_V2_ENGINEERING_RESUME',
        'status':'COMPLETED_FROZEN_BATCH_WITH_ONE_ARTIFACT_UNKNOWN' if len(rows)==36 and not stopped else 'STOPPED_PRESERVED',
        'label':cfg['label'],'budget_stop':stopped,'registered_calls':36,
        'executed_calls':sum(r['executed'] for r in rows),'new_resume_calls':sum(r['executed'] for r in rows)-1,
        'evaluable_complete_artifacts':sum(r['artifact_complete'] for r in rows),'artifact_unknown':1,
        'first_call_never_rerun':True,'planner_compute_wall_sec':sum(r.get('wall_sec',0) for r in rows),
        'stage_wall_sec':time.perf_counter()-started,'stage_process_cpu_sec':time.process_time()-cpu_started,
        'prior_external_wall_sec':failure['external_wall_sec'],'prior_external_cpu_sec':failure['external_cpu_user_plus_sys_sec'],
        'method_summary':aggregates,'all_sources_unchanged':all(unchanged.values()),'source_unchanged':unchanged,
        'conditions':[{k:c[k] for k in ['id','valid_condition','fixed_partition','candidate_obstruction_demonstrated','hard_scenario_status']} for c in diagnostics],
        'interpretation':'Archival PCS endpoint diagnostic; no unbiased general hard-problem performance estimate. First call is artifact-unknown, not algorithm failure.',
        'scope':'Saved three witnesses/routes reused. Remaining35 original frozen calls only; independent finite discrete qualification, no continuous CCD, no spatial solve or original TableI.'}
    h.save(OUTPUT/'summary.json',summary)
    figure(OUTPUT,rows,diagnostics)
    summary['total_stage_including_plot_wall_sec']=time.perf_counter()-started
    summary['total_stage_including_plot_process_cpu_sec']=time.process_time()-cpu_started
    summary['combined_shared_wall_sec']=summary['total_stage_including_plot_wall_sec']+failure['external_wall_sec']
    summary['combined_shared_cpu_sec']=summary['total_stage_including_plot_process_cpu_sec']+failure['external_cpu_user_plus_sys_sec']
    h.save(OUTPUT/'summary.json',summary)
    h.save(OUTPUT/'artifact_sha256.json',{str(p.relative_to(OUTPUT)):h.sha(p) for p in sorted(OUTPUT.rglob('*')) if p.is_file() and p.name!='artifact_sha256.json'})
    return 0 if not stopped else 2


if __name__=='__main__':
    raise SystemExit(main())
