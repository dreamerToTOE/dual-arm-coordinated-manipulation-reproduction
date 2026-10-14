"""Read-only analysis of frozen P4 evidence; no model, IK, RNG or planner calls.

The complex-number SE(2) calculation is independent of PlanarModel._transform
and PlanarModel.ik.  It replays the exact stored singular-generator inputs.
No output is written under any repository.
"""
from __future__ import annotations
import collections
import gzip
import hashlib
import json
import math
from pathlib import Path
import subprocess
import numpy as np

REPO = Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-three-methods')
DATA = REPO / 'results/20261013_P4_three_methods_round3'
OUT = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    before = subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=REPO, text=True)
    source = {str(p.relative_to(REPO)):digest(p) for p in sorted((REPO/'baselines/p4_comparison').glob('*.py'))}
    source['configs/engineering/p4_three_methods_v1.json'] = digest(REPO/'configs/engineering/p4_three_methods_v1.json')
    records, unique = [], {}
    stages, straight, folded = (collections.Counter() for _ in range(3))
    tree_parts, path_parts, transitions, candidate_parts = (collections.Counter() for _ in range(4))
    path_hashes, hashes, trials = {}, {}, []
    length = math.sin(math.pi/38.0)
    for path in sorted(DATA.glob('*.json.gz')):
        if 'repeat' in path.name:
            continue
        hashes[str(path.relative_to(REPO))] = digest(path)
        data = json.loads(gzip.decompress(path.read_bytes()))
        if data['method'] == 'RSS':
            trial = collections.Counter()
            for index, record in enumerate(data['singular_log']):
                stage = record.get('qualification', {}).get('reason', record['reason'])
                stages[stage] += 1
                (straight if record['raw_q'][17] == 0.0 else folded)[stage] += 1
                trial[stage] += 1
                q = np.asarray(record['raw_q'])
                cumulative = np.cumsum(q[3:])
                suffix = np.sum(np.r_[np.full(16, length), 0.0] * np.exp(1j*cumulative))
                reverse_rotation = np.exp(-1j*cumulative[-1])
                wrist = 1.0 - reverse_rotation*suffix - length*reverse_rotation
                radius = abs(wrist)
                cosine = (radius**2 - 2.0*length**2)/(2.0*length**2)
                derived = {'artifact':str(path.relative_to(REPO)), 'singular_log_index':index,
                           'wrist_radius_m':float(radius), 'cosine':float(cosine),
                           'suffix_radius_m':float(abs(suffix)), 'q17_rad':float(q[17]),
                           'generator_branch':record['generator_branch']}
                records.append(derived)
                key = json.dumps([record['raw_q'], record['generator_branch']], separators=(',', ':'))
                unique[key] = derived
            trials.append({'artifact':str(path.relative_to(REPO)), 'singular_requests':data['counters'].get('singular_sample_requests',0),
                           'stored_construction_attempts':len(data['singular_log']), 'rejection_stages':dict(trial)})
        elif data['method'] == 'PCS':
            path_parts.update(str(edge['partition']) for edge in data['path_edges'])
            for tree in data['trees'].values():
                for node in tree:
                    index = node['incoming_attempt']
                    if index is None:
                        continue
                    edge = data['attempts'][index]
                    tree_parts[str(edge['edge_partition'])] += 1
                    projection_id = edge['candidate_projection_id']
                    candidate_parts[str(data['projection_log'][projection_id]['partition'] if projection_id is not None else None)] += 1
                    parent_index = tree[node['parent']]['incoming_attempt']
                    if parent_index is not None:
                        parent_edge = data['attempts'][parent_index]
                        transitions[f"{parent_edge['edge_partition']}->{edge['edge_partition']}"] += 1
        if data['method'] in ('PCS', 'NR'):
            payload = json.dumps(data['path'], separators=(',', ':'), allow_nan=False).encode()
            path_hashes[path.name] = hashlib.sha256(payload).hexdigest()
    radii = np.asarray([item['wrist_radius_m'] for item in records])
    cosine = np.asarray([item['cosine'] for item in records])
    suffix = np.asarray([item['suffix_radius_m'] for item in records])
    after = subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=REPO, text=True)
    source_after = {name:digest(REPO/name) for name in source}
    result = {
      'scope':'Saved-data analysis only; no new stochastic samples, IK calls, planner calls or acceptance verdict changes.',
      'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
      'source_sha256':source, 'input_artifact_sha256':hashes,
      'audit_source_sha256':digest(Path(__file__)),
      'frozen_worktree_status_before':before,'frozen_worktree_status_after':after,
      'frozen_source_bytes_unchanged':source==source_after,
      'RSS':{'primary_trials':len(trials),'saved_requests':sum(item['singular_requests'] for item in trials),
             'stored_attempts':len(records),'unique_raw_q_and_generator_branch':len(unique),
             'stage_counts':dict(stages),'straight_stage_counts':dict(straight),'folded_stage_counts':dict(folded),
             'link_length_m':length,'wrist_reach_upper_bound_m':2.0*length,
             'wrist_radius_quantiles_m':np.quantile(radii,[0,.25,.5,.75,1]).tolist(),
             'minimum_cosine':float(cosine.min()),'maximum_cosine':float(cosine.max()),
             'suffix_radius_quantiles_m':np.quantile(suffix,[0,.25,.5,.75,1]).tolist(),
             'independent_unreachable_count':int(np.count_nonzero(cosine>1.0+1e-12)),
             'minimum_wrist_record':min(records,key=lambda item:item['wrist_radius_m']),
             'per_trial':trials},
      'PCS':{'accepted_tree_edge_partitions':dict(tree_parts),'qualified_solution_edge_partitions':dict(path_parts),
             'parent_child_edge_partition_pairs':dict(transitions),
             'accepted_node_candidate_projection_partitions':dict(candidate_parts),
             'actual_parent_child_switch_count':sum(value for key,value in transitions.items() if key.split('->')[0]!=key.split('->')[1])},
      'qualified_path_payload_sha256':path_hashes,
      'classification':{
         'RSS_recorded_failure_mechanism':'Confirmed geometric unreachability of first-end 3R closure for every saved generator input.',
         'RSS_primary_root_cause':'OUR-EXPERIMENT-DESIGN / MODEL-COVERAGE: uniform long-suffix generator gives zero feasible targets in the frozen finite budget; this is not evidence of an IK formula bug or paper failure.',
         'RSS_new_sampler_or_model_choice':'UNKNOWN until original author model/code and justified reconstruction are qualified. No repair executed.',
         'PCS_missing_advantage':'OUR-EXPERIMENT-DESIGN: endpoints share p0 and every solution edge uses p0; fixed-p0 ablation and switch-required complex environments are absent.',
         'original_exact_planar_Comau_resources':'RESOURCE-LIMITATION candidate, subject to current source audit; old lack of resources does not prove current unavailability.'}
    }
    with (OUT/'saved_data_audit.json').open('x',encoding='utf-8') as handle:
        json.dump(result,handle,ensure_ascii=False,indent=2,allow_nan=False)
    print(json.dumps({'stored_attempts':len(records),'unique_inputs':len(unique),'minimum_cosine':float(cosine.min()),
                      'stage_counts':dict(stages),'switches':result['PCS']['actual_parent_child_switch_count'],
                      'source_unchanged':result['frozen_source_bytes_unchanged'],'output':str(OUT/'saved_data_audit.json')},ensure_ascii=False))

if __name__ == '__main__':
    main()
