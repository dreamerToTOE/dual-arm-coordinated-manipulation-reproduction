#!/usr/bin/env python3
"""D083 controlled Fig.3: freeze shared endpoints before any RBS outcome.

prepare is a separate phase and never calls an IK, projection or connector.
execute refuses old outputs and rechecks every frozen source hash. Production
model/strategies and the D082 independent NumPy geometry oracle are reused.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from baselines.p4_comparison.model import PlanarModel
from baselines.p4_comparison.strategies import DEFAULT_CONFIG, Strategy, rbs_connect

DEFAULT_CONFIG_PATH = ROOT / 'configs/p4_d083/fig3_controlled_v1.json'
DEFAULT_OUTPUT = ROOT / 'results/20261022_D083_fig3_controlled01'
ORACLE_PATH = ROOT / 'scripts/p4_d082/independent_planar_validation.py'
spec = importlib.util.spec_from_file_location('d083_fig3_independent_geometry', ORACLE_PATH)
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


class ChartModel(PlanarModel):
    """Existing D081 contiguous nonzero 3R charts; no geometry override."""
    def __init__(self, partitions):
        super().__init__()
        self.partitions = tuple(int(p) for p in partitions)
        if not self.partitions or any(p not in range(17) for p in self.partitions):
            raise ValueError('invalid existing 3R partition')

    def _partition(self, partition_start):
        if partition_start not in self.partitions:
            raise ValueError('partition not in frozen subset')


def native(x):
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    raise TypeError(type(x).__name__)


def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False, default=native)
        f.write('\n')


def save_csv(path, rows, fields=None):
    rows = list(rows)
    fields = fields or list(rows[0])
    with path.open('x', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def relative(path):
    return str(path.resolve().relative_to(ROOT))


def check_hashes(values):
    bad = [p for p, h in values.items() if sha(ROOT/p) != h]
    if bad:
        raise RuntimeError('frozen input hash mismatch: '+repr(bad))


def validate_config(cfg):
    assert cfg['available_partitions'] == list(range(17))
    assert cfg['partition_order'] == list(range(16))
    assert cfg['requested_m'] == [1, 2, 3, 7, 16]
    assert cfg['pair_count'] == 180 and cfg['pool_size'] == 96
    assert cfg['position_tolerance_m'] == cfg['rotation_tolerance_rad'] == 1e-8
    assert cfg['rbs_config'] == {'rbs_resolution_rad': .05, 'rbs_max_depth': 16,
                                 'rbs_max_projections': 512, 'max_compute_wall_sec': 2.0}
    assert all(np.diff(cfg['distance_bin_edges_rad']) > 0)
    return cfg


def prepare(cfg, config_path, output):
    wall, cpu = time.perf_counter(), time.process_time()
    output.mkdir(parents=True, exist_ok=False)
    inputs = [config_path, Path(__file__).resolve(), ORACLE_PATH,
              ROOT/'baselines/p4_comparison/model.py', ROOT/'baselines/p4_comparison/strategies.py',
              ROOT/'scripts/p4_d081_numeric_pilot.py',
              ROOT/'reports/P4_D083_FIG3_CONTROLLED_PRE_TASK_20261022.md',
              ROOT/'references/private_sources/P4_original.pdf',
              ROOT/'results/20261019_D081_numeric_pilot/fig3_pairs.csv']
    records = []
    source_records = []
    for method, seeds in cfg['pool_methods_and_seeds'].items():
        for seed in seeds:
            stem = f'planner_E0_sparse_{method}_seed{seed}'
            cert_path = ROOT/cfg['pool_source']/(stem+'_qualification.json')
            cert = json.loads(cert_path.read_text())
            dense_path = ROOT/cert['dense_artifact']
            source_path = ROOT/cert['artifact']
            inputs.extend([cert_path, dense_path, source_path])
            if (not cert['independently_qualified'] or not cert['exact_start_goal'] or
                    sha(source_path) != cert['input_sha256'] or sha(dense_path) != cert['dense_sha256']):
                raise RuntimeError('saved path/certificate provenance mismatch: '+stem)
            states = np.load(dense_path)['q']
            source_records.append({'method': method, 'seed': seed, 'certificate': relative(cert_path),
                                   'dense_artifact': relative(dense_path), 'dense_points': len(states),
                                   'source_artifact': relative(source_path)})
            for row, q in enumerate(states):
                records.append({'q': q.copy(), 'source': relative(dense_path), 'source_row': row,
                                'method': method, 'seed': seed})
    input_hashes = {relative(p): sha(p) for p in inputs}
    save(output/'input_sha256.json', input_hashes)
    unique, seen = [], set()
    for ref, item in enumerate(records):
        key = np.asarray(item['q'], dtype='<f8').tobytes()
        if key not in seen:
            seen.add(key)
            unique.append({**item, 'concatenated_reference_index': ref})
    chosen = np.sort(np.random.Generator(np.random.PCG64(cfg['pool_seed'])).choice(
        len(unique), cfg['pool_size'], replace=False))
    selected = [{**unique[i], 'state_id': j, 'unique_source_index': int(i)} for j, i in enumerate(chosen)]
    q = np.array([item['q'] for item in selected])
    independent = oracle.geometry(q, cfg['environment'])
    agg = oracle.aggregate(independent)
    model = ChartModel(cfg['available_partitions'])
    production = [model.valid(x, cfg['environment']) for x in q]
    valid = (not agg['closure_failures'] and not agg['joint_limit_failures'] and
             not agg['collision_failures'] and all(v['valid'] for v in production))
    for i, item in enumerate(selected):
        item['independent_qualification'] = {k: float(v[i]) for k, v in independent.items()}
        item['production_qualification'] = production[i]
        item['partition_branches'] = {str(p): int(model.branch(item['q'], p)) for p in cfg['available_partitions']}
    pool = {'schema': 'P4_D083_FROZEN_SHARED_POOL_V1', 'valid': bool(valid),
            'selected_state_count': len(selected), 'concatenated_point_references': len(records),
            'unique_source_state_count': len(unique), 'source_trajectories': source_records,
            'selection': cfg['inference'], 'independent_aggregate': agg, 'states': selected}
    save(output/'frozen_pool.json', pool)
    if not valid:
        save(output/'prepare_failure.json', {'reason': 'INVALID_FROZEN_ENDPOINT_POOL_STOP_NO_REPLACEMENT'})
        raise RuntimeError('endpoint qualification failed; pool retained without replacement')
    possible = list(itertools.combinations(range(len(q)), 2))
    indices = np.random.Generator(np.random.PCG64(cfg['pair_seed'])).choice(
        len(possible), cfg['pair_count'], replace=False)
    pairs = []
    for pair_id, index in enumerate(indices):
        a, b = possible[index]
        distance = float(np.linalg.norm(q[b]-q[a]))
        bin_id = int(np.searchsorted(cfg['distance_bin_edges_rad'], distance, side='right')-1)
        if not distance > 0 or not 0 <= bin_id < len(cfg['distance_bin_edges_rad'])-1:
            raise RuntimeError('self/zero/out-of-bin pair violates frozen design')
        pairs.append({'pair_id': pair_id, 'state_a': a, 'state_b': b,
                      'full_unordered_pair_index': int(index), 'distance_rad': distance,
                      'bin_id': bin_id, 'bin_left_rad': cfg['distance_bin_edges_rad'][bin_id],
                      'bin_right_rad': cfg['distance_bin_edges_rad'][bin_id+1]})
    save(output/'frozen_pairs.json', pairs)
    save_csv(output/'frozen_pairs.csv', pairs)
    freeze_hashes = {relative(output/p): sha(output/p) for p in
                     ('input_sha256.json', 'frozen_pool.json', 'frozen_pairs.json', 'frozen_pairs.csv')}
    check_hashes(input_hashes)
    save(output/'freeze_manifest.json', {'schema': 'P4_D083_POOL_FROZEN_BEFORE_ANY_CONNECTION_V1',
        'frozen_artifact_sha256': freeze_hashes, 'new_connection_calls': 0,
        'new_projection_calls': 0, 'new_planner_calls': 0,
        'prepare_wall_sec': time.perf_counter()-wall, 'prepare_cpu_sec': time.process_time()-cpu,
        'config': cfg, 'numpy': np.__version__, 'python': platform.python_version()})
    print(json.dumps({'phase': 'prepare', 'valid_states': len(q), 'pairs': len(pairs),
                      'unique_source_states': len(unique), 'connections': 0}))


def accepted_oracle(result, partition, branch_label, cfg):
    if not result['success']:
        return None
    q = np.asarray(result['path'], dtype=float)
    values = oracle.geometry(q, cfg['environment'])
    agg = oracle.aggregate(values)
    mismatch = int(np.count_nonzero(~np.isin(oracle.branch(q, partition), [0, branch_label])))
    agg['branch_mismatches'] = mismatch
    agg['independently_qualified'] = not any(agg[k] for k in
        ['closure_failures', 'joint_limit_failures', 'collision_failures', 'branch_mismatches'])
    if not agg['independently_qualified']:
        raise RuntimeError('accepted production local path fails independent oracle')
    return agg


def outcome_status(result):
    if result['success']:
        return 'SUCCESS'
    if 'TIME_LIMIT' in result['reason']:
        return 'TIME_LIMIT'
    if result['reason'] in ('RBS_PROJECTION_LIMIT', 'RBS_DEPTH_LIMIT'):
        return 'EXHAUSTED'
    return 'FAILURE'


def execute(cfg, output):
    wall, cpu = time.perf_counter(), time.process_time()
    freeze = json.loads((output/'freeze_manifest.json').read_text())
    assert freeze['config'] == cfg
    input_hashes = json.loads((output/'input_sha256.json').read_text())
    check_hashes(input_hashes)
    check_hashes(freeze['frozen_artifact_sha256'])
    raw = output/'raw_pairs'
    raw.mkdir(exist_ok=False)
    save(output/'execution_started.json', {'schema': 'P4_D083_EXECUTE_ONCE_V1',
         'freeze_manifest_sha256': sha(output/'freeze_manifest.json'), 'new_planner_calls': 0})
    q = np.array([x['q'] for x in json.loads((output/'frozen_pool.json').read_text())['states']])
    pairs = json.loads((output/'frozen_pairs.json').read_text())
    algorithm = dict(DEFAULT_CONFIG)
    algorithm.update(cfg['rbs_config'])
    candidate_models = {p: ChartModel((p,)) for p in cfg['partition_order']}
    nested_models = {m: ChartModel(cfg['partition_order'][:m]) for m in cfg['requested_m']}
    candidate_rows, pair_rows = [], []
    totals = {'candidate_calls': 0, 'bounded_calls': 0, 'accepted_paths_independently_qualified': 0}
    stop = None

    def global_expired():
        return (time.perf_counter()-wall+freeze['prepare_wall_sec'] >= cfg['total_compute_wall_cap_sec'] or
                time.process_time()-cpu+freeze['prepare_cpu_sec'] >= cfg['total_compute_cpu_cap_sec'])

    def call(model, a, b, bounded):
        started = time.perf_counter()
        expired = (lambda: global_expired() or time.perf_counter()-started >= algorithm['max_compute_wall_sec']) if bounded else global_expired
        strategy = Strategy(model, cfg['environment'], 'PCS', algorithm, expired=expired)
        result = rbs_connect(model, cfg['environment'], 'PCS', a, b, algorithm, strategy=strategy)
        independent = accepted_oracle(result, result.get('partition'), result.get('branch'), cfg)
        if independent is not None:
            totals['accepted_paths_independently_qualified'] += 1
        return {'result': result, 'counters': strategy.counters, 'failure_counts': strategy.failure_counts,
                'projection_log': strategy.projection_log, 'independent_qualification': independent,
                'serialization_excluded_outer_wall_sec': time.perf_counter()-started}

    try:
        for pair in pairs:
            a, b = q[pair['state_a']], q[pair['state_b']]
            candidates, bounded = {}, {}
            for p in cfg['partition_order']:
                if global_expired():
                    stop = 'TOTAL_COMPUTE_CAP'
                    break
                evidence = call(candidate_models[p], a, b, False)
                candidates[p] = evidence
                totals['candidate_calls'] += 1
                result, counters = evidence['result'], evidence['counters']
                candidate_rows.append({**pair, 'partition': p,
                    'start_branch': candidate_models[p].branch(a, p),
                    'goal_branch': candidate_models[p].branch(b, p),
                    'selected_branch': result.get('branch'), 'outcome_status': outcome_status(result), 'success': result['success'],
                    'reason': result['reason'], 'projection_calls': result['projection_calls'],
                    'ik_solver_calls': counters.get('ik_solver_calls', 0),
                    'state_qualification_calls': counters.get('state_qualification_calls', 0),
                    'geometry_queries': counters.get('geometry_queries', 0),
                    'wall_sec': result['compute_wall_time_sec'],
                    'raw_artifact': f'raw_pairs/pair_{pair["pair_id"]:03d}.json.gz'})
            for m in cfg['requested_m']:
                selected = cfg['partition_order'][:m]
                known = [candidates[p]['result'] for p in selected if p in candidates]
                successes = [p for p in selected if p in candidates and candidates[p]['result']['success']]
                unknown = [p for p in selected if p not in candidates or outcome_status(candidates[p]['result']) in ('TIME_LIMIT', 'EXHAUSTED')]
                existential = 'SUCCESS' if successes else ('UNKNOWN' if unknown else 'FAILURE')
                if not global_expired():
                    bounded[m] = call(nested_models[m], a, b, True)
                    totals['bounded_calls'] += 1
                else:
                    stop = 'TOTAL_COMPUTE_CAP'
                evidence = bounded.get(m)
                r = None if evidence is None else evidence['result']
                counters = {} if evidence is None else evidence['counters']
                pair_rows.append({**pair, 'm': m, 'partition_set': json.dumps(selected),
                    'existential_status': existential, 'existential_success': int(bool(successes)),
                    'existential_upper': int(bool(successes or unknown)),
                    'successful_partitions': json.dumps(successes), 'unknown_partitions': json.dumps(unknown),
                    'exhaustive_candidate_count': len(known),
                    'exhaustive_candidate_projection_calls': sum(x['projection_calls'] for x in known),
                    'exhaustive_candidate_wall_sec': sum(x['compute_wall_time_sec'] for x in known),
                    'bounded_status': 'NOT_EXECUTED' if r is None else outcome_status(r),
                    'bounded_success': None if r is None else r['success'],
                    'bounded_reason': 'TOTAL_COMPUTE_CAP' if r is None else r['reason'],
                    'bounded_partition': None if r is None else r.get('partition'),
                    'bounded_branch': None if r is None else r.get('branch'),
                    'bounded_trial_partitions': json.dumps([] if r is None else [x['partition'] for x in r['trials']]),
                    'bounded_projection_calls': None if r is None else r['projection_calls'],
                    'bounded_ik_solver_calls': counters.get('ik_solver_calls', 0),
                    'bounded_geometry_queries': counters.get('geometry_queries', 0),
                    'bounded_wall_sec': None if r is None else r['compute_wall_time_sec'],
                    'raw_artifact': f'raw_pairs/pair_{pair["pair_id"]:03d}.json.gz'})
            payload = {'pair': pair, 'candidates': candidates, 'bounded': bounded}
            with gzip.open(raw/f'pair_{pair["pair_id"]:03d}.json.gz', 'xt', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, allow_nan=False, default=native)
            if pair['pair_id'] % 20 == 0:
                print(json.dumps({'pair': pair['pair_id'], **totals,
                                  'elapsed_wall_sec': time.perf_counter()-wall}), flush=True)
            if stop:
                break
    except Exception as exc:
        stop = 'EXCEPTION:'+repr(exc)
        save(output/'exception.json', {'exception': repr(exc), 'completed_calls': totals})
        if 'pair' in locals():
            with gzip.open(raw/f'exception_pair_{pair["pair_id"]:03d}.json.gz', 'xt', encoding='utf-8') as f:
                json.dump({'pair': pair, 'candidates': candidates, 'bounded': bounded}, f,
                          ensure_ascii=False, allow_nan=False, default=native)
    completed = {(x['pair_id'], x['m']) for x in pair_rows}
    for pair in pairs:
        for m in cfg['requested_m']:
            if (pair['pair_id'], m) in completed:
                continue
            pair_rows.append({**pair, 'm': m, 'partition_set': json.dumps(cfg['partition_order'][:m]),
                'existential_status': 'UNKNOWN', 'existential_success': 0, 'existential_upper': 1,
                'successful_partitions': '[]', 'unknown_partitions': json.dumps(cfg['partition_order'][:m]),
                'exhaustive_candidate_count': 0, 'exhaustive_candidate_projection_calls': 0,
                'exhaustive_candidate_wall_sec': 0., 'bounded_status': 'NOT_EXECUTED',
                'bounded_success': None, 'bounded_reason': stop or 'NOT_EXECUTED',
                'bounded_partition': None, 'bounded_branch': None, 'bounded_trial_partitions': '[]',
                'bounded_projection_calls': None, 'bounded_ik_solver_calls': 0,
                'bounded_geometry_queries': 0, 'bounded_wall_sec': None, 'raw_artifact': ''})
    candidate_done = {(x['pair_id'], x['partition']) for x in candidate_rows}
    for pair in pairs:
        for p in cfg['partition_order']:
            if (pair['pair_id'], p) not in candidate_done:
                candidate_rows.append({**pair, 'partition': p,
                    'start_branch': candidate_models[p].branch(q[pair['state_a']], p),
                    'goal_branch': candidate_models[p].branch(q[pair['state_b']], p),
                    'selected_branch': None, 'outcome_status': 'NOT_EXECUTED', 'success': False,
                    'reason': stop or 'NOT_EXECUTED', 'projection_calls': 0, 'ik_solver_calls': 0,
                    'state_qualification_calls': 0, 'geometry_queries': 0, 'wall_sec': None, 'raw_artifact': ''})
    pair_rows.sort(key=lambda x: (x['pair_id'], x['m']))
    candidate_rows.sort(key=lambda x: (x['pair_id'], x['partition']))
    save_csv(output/'candidate_outcomes.csv', candidate_rows)
    save_csv(output/'pair_by_m_outcomes.csv', pair_rows)
    save(output/'pair_by_m_outcomes.json', pair_rows)
    summary = summarize(cfg, pair_rows, candidate_rows)
    check_hashes(input_hashes)
    check_hashes(freeze['frozen_artifact_sha256'])
    summary.update({'schema': 'P4_D083_CONTROLLED_FIG3_RESULT_V1', 'stop_reason': stop,
                    'status': 'COMPLETE' if stop is None else 'PARTIAL_RETAINED', **totals,
                    'pair_count': len(pairs), 'self_pairs': 0, 'new_planner_calls': 0,
                    'uncertainty': cfg['inference'], 'independent_geometry_scope': 'all96 endpoints and all accepted local discrete path points; no continuous CCD',
                    'execute_wall_sec': time.perf_counter()-wall, 'execute_cpu_sec': time.process_time()-cpu,
                    'prepare_wall_sec': freeze['prepare_wall_sec'], 'prepare_cpu_sec': freeze['prepare_cpu_sec'],
                    'input_hashes_unchanged': True})
    save(output/'summary.json', summary)
    save_csv(output/'summary_by_m.csv', summary['by_m'])
    save_csv(output/'visibility_by_distance.csv', summary['by_distance'])
    plot(output, summary)
    save(output/'execution_total_cost.json', {'wall_sec': time.perf_counter()-wall+freeze['prepare_wall_sec'],
          'cpu_sec': time.process_time()-cpu+freeze['prepare_cpu_sec'],
          'includes_prepare_execute_output_plotting': True, 'total_wall_cap_sec': cfg['total_compute_wall_cap_sec'],
          'total_cpu_cap_sec': cfg['total_compute_cpu_cap_sec']})
    save(output/'artifact_sha256.json', {relative(p): sha(p) for p in sorted(output.rglob('*')) if p.is_file()})
    print(json.dumps({k: v for k, v in summary.items() if k not in ('by_m', 'by_distance')}, default=native))


def summarize(cfg, rows, candidates):
    by_m, by_distance = [], []
    for m in cfg['requested_m']:
        group = [x for x in rows if x['m'] == m]
        finished = [x for x in group if x['bounded_success'] is not None]
        by_m.append({'m': m, 'pairs': len(group), 'existential_success_count': sum(x['existential_success'] for x in group),
            'existential_unknown_count': sum(x['existential_status'] == 'UNKNOWN' for x in group),
            'existential_rate_lower': np.mean([x['existential_success'] for x in group]),
            'existential_rate_upper': np.mean([x['existential_upper'] for x in group]),
            'bounded_executed_count': len(finished), 'bounded_success_count': sum(x['bounded_success'] for x in finished),
            'bounded_time_limit_count': sum(x['bounded_status'] == 'TIME_LIMIT' for x in group),
            'bounded_exhausted_count': sum(x['bounded_status'] == 'EXHAUSTED' for x in group),
            'bounded_rate': sum(x['bounded_success'] for x in finished)/len(finished) if finished else None,
            'mean_exhaustive_chart_wall_sec': np.mean([x['exhaustive_candidate_wall_sec'] for x in group]),
            'mean_bounded_wall_sec': np.mean([x['bounded_wall_sec'] for x in finished]) if finished else None,
            'mean_bounded_midpoint_projections': np.mean([x['bounded_projection_calls'] for x in finished]) if finished else None,
            'mean_bounded_ik_solver_calls': np.mean([x['bounded_ik_solver_calls'] for x in finished]) if finished else None,
            'mean_bounded_geometry_queries': np.mean([x['bounded_geometry_queries'] for x in finished]) if finished else None})
        for bin_id, (left, right) in enumerate(zip(cfg['distance_bin_edges_rad'][:-1], cfg['distance_bin_edges_rad'][1:])):
            g = [x for x in group if x['bin_id'] == bin_id]
            done = [x for x in g if x['bounded_success'] is not None]
            by_distance.append({'m': m, 'bin_id': bin_id, 'bin_left_rad': left, 'bin_right_rad': right,
                'pair_count': len(g), 'existential_success_count': sum(x['existential_success'] for x in g),
                'existential_rate': np.mean([x['existential_success'] for x in g]) if g else None,
                'bounded_executed_count': len(done), 'bounded_success_count': sum(x['bounded_success'] for x in done),
                'bounded_rate': np.mean([x['bounded_success'] for x in done]) if done else None})
    violations = []
    for pair_id in range(cfg['pair_count']):
        g = [x for x in rows if x['pair_id'] == pair_id]
        if any(a['existential_success'] > b['existential_success'] for a, b in zip(g[:-1], g[1:])):
            violations.append(pair_id)
    return {'by_m': by_m, 'by_distance': by_distance, 'existential_monotonicity_violations': violations,
            'candidate_failure_reasons': {reason: sum(x['reason'] == reason for x in candidates)
                for reason in sorted({x['reason'] for x in candidates})},
            'candidate_success_count': sum(x['success'] for x in candidates)}


def plot(output, summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plots = output/'plots'
    plots.mkdir(exist_ok=False)
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    for m in [x['m'] for x in summary['by_m']]:
        last_bin = max(v['bin_id'] for v in summary['by_distance'] if v['pair_count'])
        g = [x for x in summary['by_distance'] if x['m'] == m and x['bin_id'] <= last_bin]
        x = [(v['bin_left_rad']+v['bin_right_rad'])/2 for v in g]
        axes[0].plot(x, [v['existential_rate'] for v in g], marker='o', label=f'm={m}')
        axes[1].plot(x, [v['bounded_rate'] for v in g], marker='o', label=f'm={m}')
    axes[0].set_title('Exhaustive per-chart availability (same cached candidates)')
    axes[1].set_title('Actual bounded PCS strategy (512 midpoints shared)')
    for ax in axes:
        ax.set_ylabel('Local visibility (fixed pair population)')
        ax.set_ylim(-.03, 1.04)
        ax.grid(alpha=.25)
        ax.legend(ncol=5)
    counts = [x for x in summary['by_distance'] if x['m'] == 1 and x['pair_count']]
    for g in counts:
        axes[1].annotate(f'n={g["pair_count"]}', ((g['bin_left_rad']+g['bin_right_rad'])/2, .02),
                         rotation=90, fontsize=8, va='bottom')
    axes[1].set_xlabel('Euclidean joint distance (rad); fixed 0.3-rad bins')
    fig.text(.5, .015, 'Finite saved-trajectory population; correlated endpoints. Descriptive rates, no population confidence claim.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=[0,.04,1,1])
    fig.savefig(plots/'fig3_controlled_visibility_by_distance.png', dpi=200)
    plt.close(fig)
    g = summary['by_m']
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    x = [v['m'] for v in g]
    axes[0].plot(x, [v['existential_rate_lower'] for v in g], 'o-', label='Exhaustive chart union')
    axes[0].plot(x, [v['bounded_rate'] for v in g], 's--', label='Actual bounded PCS')
    axes[0].set_ylabel('Local visibility rate (same 180 pairs)')
    axes[0].set_ylim(-.03, 1.04)
    axes[0].legend(fontsize=8)
    axes[1].plot(x, [1000*v['mean_exhaustive_chart_wall_sec'] for v in g], 'o-', label='Exhaustive sum')
    axes[1].plot(x, [1000*v['mean_bounded_wall_sec'] for v in g], 's--', label='Actual bounded PCS')
    axes[1].set_ylabel('Mean LOCAL check wall time (ms)')
    axes[1].legend(fontsize=8)
    axes[2].plot(x, [v['mean_bounded_midpoint_projections'] for v in g], 'o-', label='Midpoint projections')
    axes[2].plot(x, [v['mean_bounded_ik_solver_calls'] for v in g], 's--', label='Analytic IK solves')
    axes[2].set_ylabel('Mean calls per bounded local check')
    axes[2].legend(fontsize=8)
    for ax in axes:
        ax.set_xlabel('Number of nested passive partitions m')
        ax.set_xticks(x)
        ax.grid(alpha=.25)
    fig.suptitle('Controlled Fig.3 supplement: valid shared endpoints, nonself pairs, unchanged RBS rules')
    fig.tight_layout()
    fig.savefig(plots/'fig3_controlled_visibility_and_local_cost_by_m.png', dpi=200)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['prepare', 'execute', 'static-check'])
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    cfg = validate_config(json.loads(args.config.read_text()))
    if args.phase == 'static-check':
        assert len(list(itertools.combinations(range(cfg['pool_size']), 2))) == 4560
        print('PASS_STATIC_CONFIGURATION_ONLY_ZERO_NUMERICAL_CALLS')
    elif args.phase == 'prepare':
        prepare(cfg, args.config.resolve(), args.output.resolve())
    else:
        execute(cfg, args.output.resolve())


if __name__ == '__main__':
    main()
