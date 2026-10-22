#!/usr/bin/env python3
"""One preregistered D083 diagnostic batch; unchanged D081 production planner.

Endpoints are frozen archival states, before new route/planner checks. This is
not a representative sample of difficult problems. Geometry/branch/path checks
use the independently implemented D082 NumPy oracle, never production FK/GEOS.
Run only after static review: python3 scripts/p4_d083/bounded_difficulty.py --execute
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'configs/p4_d083/difficult_v1.json'
OUTPUT = ROOT / 'results/20261022_D083_difficult01'
sys.path.insert(0, str(ROOT))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    def default(v):
        if isinstance(v, np.ndarray):
            return v.tolist()
        if isinstance(v, np.generic):
            return v.item()
        raise TypeError(type(v).__name__)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False,
                               allow_nan=False, default=default)+'\n')


def csv_rows(path, rows):
    if not rows:
        path.write_text('\n')
        return
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, keys, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def oracle_module():
    p = ROOT / 'scripts/p4_d082/independent_planar_validation.py'
    spec = importlib.util.spec_from_file_location('d083_independent_planar', p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BudgetStop(RuntimeError):
    pass


def qualifies(result):
    return all(result[k] == 0 for k in
               ('closure_failures', 'joint_limit_failures', 'collision_failures'))


def tree_and_solution_switches(raw):
    tree_rows = []
    for side, tree in raw['trees'].items():
        for node_index, node in enumerate(tree):
            if node['parent'] is None:
                continue
            parent = tree[node['parent']]
            before = parent['incoming_attempt']
            after = node['incoming_attempt']
            p0 = None if before is None else raw['attempts'][before]['edge_partition']
            p1 = raw['attempts'][after]['edge_partition']
            tree_rows.append({'tree': side, 'node': node_index,
                              'parent': node['parent'], 'previous_partition': p0,
                              'incoming_partition': p1,
                              'switch': p0 is not None and p1 is not None and p0 != p1})
    parts = [e['partition'] for e in raw['path_edges'] if e['partition'] is not None]
    return (tree_rows, parts,
            sum(a != b for a, b in zip(parts[:-1], parts[1:])))


def direct_diagnostic(oracle, a, b, partition, branch, cfg, levels, guard):
    """Independent fixed-depth projected candidate; no production RBS calls.

    An analytically/numerically closed colliding midpoint is an obstruction of
    this specific candidate only. IK failure is not evidence of an obstacle.
    All computed states and rejected seeds survive in trace on any failure.
    """
    trace = []
    updates = 0

    def recurse(left, right, depth):
        nonlocal updates
        guard()
        if depth == levels:
            return [left, right]
        seed = (left + right) * .5
        entry = {'depth': depth+1, 'seed_q': seed.tolist()}
        trace.append(entry)
        try:
            if partition is None:
                mid, n = oracle.nr_close(seed, cfg)
                updates += n
            else:
                mid = oracle.analytic_close(seed, partition, branch)
        except ValueError as error:
            entry.update(q=None, projection_status='FAILED', reason=str(error))
            raise
        entry.update(q=mid.tolist(), projection_status='SUCCESS')
        return recurse(left, mid, depth+1) + recurse(mid, right, depth+1)[1:]

    path, failure = None, None
    try:
        path = np.asarray(recurse(a, b, 0))
    except ValueError as error:
        failure = str(error)
    closed = np.asarray([x['q'] for x in trace if x.get('q') is not None])
    candidates = np.vstack([a, b, closed]) if len(closed) else np.asarray([a, b])
    values = oracle.geometry(candidates, 'E1_clutter')
    stats = oracle.aggregate(values)
    independently_closed = ((values['position'] <= oracle.POS_TOL) &
                            (values['angle'] <= oracle.ANGLE_TOL) &
                            (values['joint_margin'] >= 0))
    obstructed_ids = np.flatnonzero(independently_closed & (values['clearance'] <= 0))
    max_step = None if path is None else float(np.linalg.norm(np.diff(path, axis=0), axis=1).max())
    return {'partition': partition, 'branch': branch, 'levels': levels,
            'trace': trace, 'path': None if path is None else path.tolist(),
            'projection_failure': failure, 'independent': stats,
            'independently_closed_collision_indices': obstructed_ids.tolist(),
            'collision_obstruction_demonstrated': bool(len(obstructed_ids)),
            'independently_closed_colliding_states': candidates[obstructed_ids].tolist(),
            'maximum_adjacent_l2_rad': max_step,
            'resolution_qualified': max_step is not None and max_step <= cfg['rbs_resolution_rad'],
            'independent_NR_updates': updates,
            'interpretation': 'Specific deterministic projected candidate; not proof of a narrow passage or a topological disconnection.'}


def qualify_success(oracle, raw, a, b, out, identity, levels, guard):
    oracle.START, oracle.GOAL = a.copy(), b.copy()
    edges, leaves, error = oracle.validate_provenance(raw)
    path = np.asarray(raw['path'])
    saved_values = oracle.geometry(path, raw['environment'])
    dense = [path[0]]
    branch_failures, updates = 0, 0
    for edge_meta, edge in edges:
        edge_dense = [edge[0]]
        for left, right in zip(edge[:-1], edge[1:]):
            guard()
            points, n = oracle.refine(left, right, edge_meta['partition'],
                                       edge_meta['branch'], raw['config'], levels=levels)
            updates += n
            edge_dense.extend(points[1:])
        edge_dense = np.asarray(edge_dense)
        if edge_meta['partition'] is not None:
            labels = oracle.branch(edge_dense, edge_meta['partition'])
            branch_failures += int(np.count_nonzero((labels != 0) &
                                                     (labels != edge_meta['branch'])))
        dense.extend(edge_dense[1:])
    dense = np.asarray(dense)
    dense_values = oracle.geometry(dense, raw['environment'])
    saved_stats, dense_stats = oracle.aggregate(saved_values), oracle.aggregate(dense_values)
    file = out / 'independent_paths' / f'{identity}.npz'
    file.parent.mkdir(exist_ok=True)
    np.savez_compressed(file, q=dense, **dense_values)
    return {'qualified': qualifies(saved_stats) and qualifies(dense_stats) and branch_failures == 0,
            'exact_endpoints_and_tree_RBS_provenance': True,
            'saved': saved_stats, 'dense': dense_stats,
            'branch_failures': branch_failures, 'saved_RBS_leaves': leaves,
            'leaf_distance_metadata_max_error_rad': error,
            'independent_NR_updates': updates, 'refinement_levels': levels,
            'dense_artifact': str(file.relative_to(ROOT)), 'dense_sha256': sha(file),
            'scope': 'DISCRETE_CONFIGURATIONS_NOT_CONTINUOUS_SWEEP'}


def make_figure(out, rows, diagnostics):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    methods = ['PCS', 'COMPATIBLE_FIXED', 'NR', 'RSS']
    for i, method in enumerate(methods):
        group = [r for r in rows if r['registered_method'] == method and r['executed']]
        n, successes = len(group), sum(r['independently_qualified'] for r in group)
        axes[0].bar(i, successes/n if n else 0, color=['#177caa','#6e9d34','#bf7a20','#8e6dad'][i])
        axes[0].text(i, (successes/n if n else 0)+.03, f'{successes}/{n}', ha='center')
    axes[0].set_xticks(range(4), ['PCS', 'fixed compatible', 'NR', 'RSS'], rotation=20)
    axes[0].set_ylim(0, 1.18)
    axes[0].set_ylabel('Independently qualified success fraction')
    axes[0].set_title('Frozen diagnostic conditions, paired seeds 7/23/41')
    for condition in diagnostics:
        for d in condition['direct_candidates']:
            p = 'NR' if d['partition'] is None else f"p{d['partition']}"
            axes[1].scatter(condition['id']+' '+p, d['independent']['minimum_clearance_m'],
                            marker='x' if d['projection_failure'] else 'o', s=55)
    axes[1].axhline(0, color='black', lw=.8)
    axes[1].set_ylabel('Independent candidate minimum clearance / m')
    axes[1].set_title('Candidate diagnostics; projection failures shown as x')
    axes[1].tick_params(axis='x', rotation=45)
    fig.suptitle('D083 bounded archival-endpoint diagnostic; not a general hard benchmark')
    fig.tight_layout()
    fig.savefig(out / 'difficult_diagnostic.png', dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Run the single frozen batch after static review')
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit('Static-review entry only: execution requires explicit --execute after review')
    if OUTPUT.exists():
        raise SystemExit('Refusing to overwrite '+str(OUTPUT))
    cfg = json.loads(CONFIG.read_text())
    for rel, expected in cfg['source_sha256'].items():
        if sha(ROOT/rel) != expected:
            raise RuntimeError('frozen scientific source changed: '+rel)
    certificate = ROOT/cfg['source_certificate']
    if sha(certificate) != cfg['source_certificate_sha256']:
        raise RuntimeError('source certificate changed')
    certificates = {x['dense_artifact']: x for x in json.loads(certificate.read_text())['results']}
    OUTPUT.mkdir(parents=True)
    started, cpu_started = time.perf_counter(), time.process_time()
    budget = cfg['budget']

    def guard(*unused):
        if (time.perf_counter()-started >= budget['stage_wall_sec'] or
                time.process_time()-cpu_started >= budget['stage_process_cpu_sec']):
            raise BudgetStop('frozen stage wall/CPU resource envelope exhausted')

    def alarm(*unused):
        raise BudgetStop('frozen stage wall resource envelope exhausted')

    signal.signal(signal.SIGALRM, alarm)
    signal.setitimer(signal.ITIMER_REAL, budget['stage_wall_sec'])
    oracle = oracle_module()
    # Production imports are used only by the unchanged planner, never the oracle.
    from baselines.p4_comparison.model import PlanarModel
    from baselines.p4_comparison.planner import plan
    save(OUTPUT/'config_snapshot.json', cfg)
    source_hashes = dict(cfg['source_sha256'])
    source_hashes[str(Path(__file__).relative_to(ROOT))] = sha(Path(__file__))
    source_hashes[str(CONFIG.relative_to(ROOT))] = sha(CONFIG)
    save(OUTPUT/'run_metadata.json', {
        'git_head': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'git_status_at_start': subprocess.check_output(['git','status','--short'], cwd=ROOT, text=True),
        'python': sys.version, 'numpy': np.__version__, 'platform': platform.platform(),
        'source_sha256': source_hashes, 'new_spatial_planner_calls': 0,
        'original_Table_I_calls': 0, 'time_scope': 'stage imports, checks, diagnostic routes, planner, independent qualification, serialization and plots'})
    diagnostics, rows, switch_rows = [], [], []
    stopped = None
    try:
        # All three conditions and their witness/precheck data are frozen before
        # any method success is evaluated. Invalid conditions are never replaced.
        for condition in cfg['conditions']:
            guard()
            endpoints, prefixes = [], []
            source_records = []
            for source in condition['endpoint_sources']:
                p = ROOT/source['artifact']
                if sha(p) != source['sha256']:
                    raise RuntimeError('frozen endpoint artifact changed')
                cert = certificates[source['artifact']]
                if not cert['independently_qualified'] or cert['dense_sha256'] != sha(p):
                    raise RuntimeError('source independent certificate not bound')
                data = np.load(p)['q']
                if len(data) != source['source_point_count']:
                    raise RuntimeError('source path point count changed')
                q = np.asarray(source['q'])
                if not np.array_equal(q, data[source['index']]):
                    raise RuntimeError('frozen endpoint differs from source')
                endpoints.append(q)
                prefixes.append(data[:source['index']+1])
                source_records.append({'artifact': source['artifact'], 'sha256': sha(p),
                                       'certificate_qualified': True, 'prefix_points': source['index']+1})
            a, b = endpoints
            exact_common_root = bool(np.array_equal(prefixes[0][0], prefixes[1][0]))
            if not exact_common_root:
                raise RuntimeError('feasible witness common root not exactly identical')
            witness = np.vstack([prefixes[0][::-1], prefixes[1][1:]])
            witness_stats = oracle.aggregate(oracle.geometry(witness, cfg['environment']))
            np.savez_compressed(OUTPUT/f"{condition['id']}_feasible_witness.npz", q=witness)
            endpoint_stats = oracle.aggregate(oracle.geometry(np.asarray(endpoints), cfg['environment']))
            branches = [{'partition': p, 'start_branch': int(oracle.branch(a,p)),
                         'goal_branch': int(oracle.branch(b,p))} for p in (0,16)]
            for x in branches:
                x['compatible'] = (x['start_branch'] == x['goal_branch'] or
                                   x['start_branch'] == 0 or x['goal_branch'] == 0)
            compatible = [x for x in branches if x['compatible']]
            d = {'id': condition['id'], 'endpoints': [a.tolist(),b.tolist()],
                 'endpoint_independent': endpoint_stats, 'branches': branches,
                 'fixed_partition': compatible[0]['partition'] if compatible else None,
                 'witness_independent': witness_stats, 'witness_sources': source_records,
                 'exact_common_root': exact_common_root,
                 'witness_exact_endpoints': bool(np.array_equal(witness[0],a) and np.array_equal(witness[-1],b)),
                 'witness_maximum_step_rad': float(np.linalg.norm(np.diff(witness,axis=0),axis=1).max()),
                 'valid_condition': qualifies(endpoint_stats) and qualifies(witness_stats),
                 'direct_candidates': []}
            diagnostics.append(d)
            if d['valid_condition']:
                for x in compatible + [{'partition':None,'start_branch':None,'goal_branch':None}]:
                    branch = None if x['partition'] is None else x['start_branch'] or x['goal_branch'] or 1
                    route = direct_diagnostic(oracle,a,b,x['partition'],branch,cfg['algorithm_config'],
                                              budget['direct_diagnostic_levels'],guard)
                    d['direct_candidates'].append(route)
            d['candidate_obstruction_demonstrated'] = any(x['collision_obstruction_demonstrated'] for x in d['direct_candidates'])
            d['hard_scenario_status'] = ('CANDIDATE_OBSTRUCTION_ONLY_NARROW_PASSAGE_NOT_PROVEN'
                                         if d['candidate_obstruction_demonstrated'] else 'NOT_ESTABLISHED_HARD')
            save(OUTPUT/'condition_diagnostics.json', diagnostics)
        for condition in diagnostics:
            a,b = np.asarray(condition['endpoints'])
            for seed in cfg['paired_seeds']:
                for registered_method in cfg['method_order']:
                    guard()
                    fixed = condition['fixed_partition']
                    method = f'PCS_FIXED_{fixed}' if registered_method == 'COMPATIBLE_FIXED' and fixed is not None else registered_method
                    identity = f"{condition['id']}_{method}_seed{seed}"
                    row = {'condition':condition['id'],'registered_method':registered_method,
                           'method':method,'seed':seed,'fixed_partition':fixed,
                           'executed':False,'status':'NOT_COMPARABLE',
                           'independently_qualified':False}
                    rows.append(row)
                    if condition['valid_condition'] and (registered_method != 'COMPATIBLE_FIXED' or fixed is not None):
                        model = PlanarModel()
                        model.start,model.goal = a.copy(),b.copy()
                        raw = plan(model,cfg['environment'],method,seed,budget['max_iterations_per_call'],cfg['algorithm_config'])
                        raw['d083_scope'] = cfg['label']
                        file = OUTPUT/'raw_planner'/f'{identity}.json.gz'
                        file.parent.mkdir(exist_ok=True)
                        with gzip.open(file,'wt') as stream:
                            json.dump(raw,stream,allow_nan=False)
                        tree,parts,solution_switches = tree_and_solution_switches(raw)
                        switch_rows.extend({'condition':condition['id'],'method':method,'seed':seed,**x} for x in tree)
                        row.update(executed=True,status=raw['status'],terminal_reason=raw['terminal_reason'],
                                   wall_sec=raw['compute_wall_time_sec'],node_count=raw['node_count'],
                                   accepted_edges=raw['counters'].get('accepted_edges',0),
                                   projection_calls=raw['counters'].get('projection_calls',0),
                                   tree_parent_child_switches=sum(x['switch'] for x in tree),
                                   solution_switches=solution_switches,solution_partitions=json.dumps(parts),
                                   artifact=str(file.relative_to(ROOT)),artifact_sha256=sha(file))
                        # Charge the real call before its independent postcheck,
                        # preserving the denominator if the stage cap intervenes.
                        csv_rows(OUTPUT/'planner_trials.csv',rows)
                        if raw['status'] == 'SUCCESS':
                            try:
                                qualification = qualify_success(oracle,raw,a,b,OUTPUT,identity,
                                                                  budget['successful_path_refinement_levels'],guard)
                            except (AssertionError,ValueError) as error:
                                qualification = {'qualified':False,'error':str(error),'scope':'INDEPENDENT_CHECK_FAILED'}
                            save(OUTPUT/'qualifications'/f'{identity}.json',qualification)
                            row['independently_qualified'] = qualification['qualified']
                            row['path_points'] = len(raw['path'])
                            row['path_length_rad'] = raw['path_metrics']['joint_path_length_rad']
                    csv_rows(OUTPUT/'planner_trials.csv',rows)
                    csv_rows(OUTPUT/'tree_parent_child_partitions.csv',switch_rows)
                    print(json.dumps(row),flush=True)
    except BudgetStop as error:
        stopped = str(error)
        save(OUTPUT/'budget_stop.json',{'reason':stopped,'completed_rows':len(rows)})
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
    groups = defaultdict(list)
    for row in rows:
        groups[row['registered_method']].append(row)
    aggregate = [{'registered_method':m,'executed':sum(x['executed'] for x in rs),
                  'source_success':sum(x['status']=='SUCCESS' for x in rs),
                  'independent_success':sum(x['independently_qualified'] for x in rs),
                  'mean_wall_sec':(float(np.mean([x['wall_sec'] for x in rs if x['executed']]))
                                   if any(x['executed'] for x in rs) else None),
                  'tree_switches':sum(x.get('tree_parent_child_switches',0) for x in rs),
                  'solution_switches':sum(x.get('solution_switches',0) for x in rs)} for m,rs in groups.items()]
    csv_rows(OUTPUT/'method_summary.csv',aggregate)
    unchanged = {p:sha(ROOT/p)==h for p,h in source_hashes.items()}
    summary = {'schema':'P4_D083_BOUNDED_DIFFICULT_DIAGNOSTIC_V1',
         'status':'COMPLETED_FROZEN_BATCH' if len(rows)==36 and not stopped else 'STOPPED_PRESERVED',
         'label':cfg['label'],'budget_stop':stopped,'registered_calls':36,
         'executed_calls':sum(x['executed'] for x in rows),
         'planner_compute_wall_sec':sum(x.get('wall_sec',0) for x in rows),
         'stage_wall_sec':time.perf_counter()-started,'stage_process_cpu_sec':time.process_time()-cpu_started,
         'method_summary':aggregate,'all_sources_unchanged':all(unchanged.values()),
         'source_unchanged':unchanged,'conditions':[{
             k:c[k] for k in ['id','valid_condition','fixed_partition','candidate_obstruction_demonstrated','hard_scenario_status']}
             for c in diagnostics],
         'interpretation':'Archival PCS-endpoint diagnostic, three conditions only; cannot estimate unbiased general hard-problem success rates. A collision blocks only a particular candidate, not every route.',
         'scope':'Independent finite discrete states with two new recursive midpoint levels; no continuous CCD, physical dynamics, new spatial solve, original TableI or other environments.'}
    paired = []
    for condition in cfg['conditions']:
        for seed in cfg['paired_seeds']:
            group = {r['registered_method']:r for r in rows if r['condition']==condition['id'] and r['seed']==seed}
            entry = {'condition':condition['id'],'seed':seed}
            for method in cfg['method_order']:
                r = group.get(method)
                entry[method+'_status'] = 'NOT_EXECUTED_BUDGET' if r is None else r['status']
                entry[method+'_independent_success'] = None if r is None else r['independently_qualified']
            for alternative in ['COMPATIBLE_FIXED','NR','RSS']:
                pcs,other = group.get('PCS'),group.get(alternative)
                entry['PCS_minus_'+alternative+'_wall_sec'] = (
                    pcs['wall_sec']-other['wall_sec'] if pcs and other and pcs['executed'] and other['executed'] else None)
            paired.append(entry)
    csv_rows(OUTPUT/'paired_seed_comparison.csv',paired)
    save(OUTPUT/'summary.json',summary)
    if diagnostics and rows:
        make_figure(OUTPUT,rows,diagnostics)
    summary['total_stage_including_plot_wall_sec'] = time.perf_counter()-started
    summary['total_stage_including_plot_process_cpu_sec'] = time.process_time()-cpu_started
    save(OUTPUT/'summary.json',summary)
    save(OUTPUT/'artifact_sha256.json',{str(p.relative_to(OUTPUT)):sha(p) for p in sorted(OUTPUT.rglob('*')) if p.is_file() and p.name!='artifact_sha256.json'})
    return 0 if not stopped else 2


if __name__ == '__main__':
    raise SystemExit(main())
