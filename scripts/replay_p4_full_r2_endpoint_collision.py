#!/usr/bin/env python3
"""One-shot observation-only collision continuation of four saved A candidates.

No IK, NR, sampler, planner, branch search or endpoint reconstruction. Historical
UNKNOWN results stay immutable. V3 changes TCP observations only; original PQP
mesh/pair/tolerance policy is bound through the preserved controls and parity.
"""
from __future__ import annotations
import argparse
from collections import Counter
import datetime as dt
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'scripts'))
from recover_p4_full_r2_endpoints import (Budget, closure_metrics, digest,
    cpu_seconds, limit_score, save_new)
from baselines.p4_full.geometry_consistent.collision_adapter import check_collision, close_sessions

SCHEMA = 'P4_R2_ENDPOINT_COLLISION_OBSERVATION_CONTINUATION_V1'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(args.protocol.read_text())
    if spec['schema'] != SCHEMA or spec['frozen'] is not True:
        raise ValueError('FROZEN_PROTOCOL_REQUIRED')
    if spec['new_ik_nr_sampling_planning_calls'] != 0 or spec['max_collision_adapter_calls'] != 4:
        raise ValueError('SCOPE_MISMATCH')
    for filename, expected in spec['bound_files_sha256'].items():
        path = Path(filename) if filename.startswith('/') else ROOT/filename
        if digest(path) != expected:
            raise ValueError('BOUND_FILE_CHANGED '+filename)
    old_execution = json.loads((ROOT/spec['original_execution']).read_text())
    if spec['wall_cap_s']+old_execution['wall_s'] > 120 or spec['cpu_cap_s']+old_execution['cpu_s'] > 240:
        raise ValueError('ORIGINAL_A_BUDGET_EXCEEDED')
    v2, v3 = [json.loads(Path(spec[k]).read_text()) for k in ('v2_manifest', 'v3_manifest')]
    for model in ('IV','V'):
        for variant in ('native','aligned'):
            old = next(e for e in v2['entries'] if e['model']==model and e['variant']==variant)
            new = next(e for e in v3['entries'] if e['model']==model and e['variant']==variant)
            if old['source_files_sha256'] != new['source_files_sha256'] or old['mesh_sha256'] != new['mesh_sha256']:
                raise ValueError('SOURCE_OR_MESH_PARITY_FAILED')
            if not new['source_equal_to_v2_after_removing_pose_observations'] or not new['all_active_source_pair_arguments_preserved']:
                raise ValueError('OBSERVATION_ONLY_PARITY_FAILED')
    controls = json.loads((ROOT/spec['collision_controls_result']).read_text())
    if controls.get('passed') is not True:
        raise ValueError('SOURCE_CONTROLS_NOT_PASSED')
    folder = ROOT/'results/p4_full'/spec['run_id']
    folder.mkdir(exist_ok=False)
    budget = Budget(spec['wall_cap_s'], spec['cpu_cap_s'])
    started_cpu = cpu_seconds()
    execution = {'schema': SCHEMA, 'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'git_status_at_start': subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),
        'protocol_sha256': digest(args.protocol), 'source_sha256': digest(__file__),
        'bound_files_sha256': spec['bound_files_sha256'], 'run_id': spec['run_id'],
        'classification': 'RECONSTRUCTED', 'collision_adapter_calls_started': 0,
        'collision_adapter_calls_completed': 0, 'new_ik_nr_sampling_planning_calls': 0,
        'full_physical_geometry_or_CCD_qualified': False}
    records = []
    try:
        with (folder/'events.jsonl').open('x',buffering=1) as stream:
            for item in spec['saved_candidates']:
                budget.check()
                old = json.loads((ROOT/item['path']).read_text())
                if old['status'] != 'UNKNOWN_COLLISION_QUALIFICATION' or old['selected_q_rad'] is not None:
                    raise ValueError('HISTORICAL_UNKNOWN_EXPECTED')
                pre = sorted((c for c in old['candidates_all'] if c['pre_collision_eligible']),
                    key=lambda c:(c['passive_l2_delta_rad'],tuple(c['branch']),tuple(c['true_2pi_lifts'])))
                chosen = pre[0]
                if chosen['candidate_index'] != item['index'] or old['nearest_pre_collision_candidate_index'] != item['index']:
                    raise ValueError('FROZEN_NEAREST_CANDIDATE_CHANGED')
                # A unique original structural branch must produce one root;
                # all remaining representatives must be real 2pi rotations.
                if len({c['source_root_index'] for c in pre}) != 1:
                    raise ValueError('MULTIPLE_SAME_BRANCH_ROOTS_REQUIRE_NEW_PROTOCOL')
                for c in pre:
                    if not c['same_original_branch'] or not c['branch_verified']:
                        raise ValueError('BRANCH_CHANGED')
                    for a,b in zip(c['q_rad'],chosen['q_rad']):
                        delta=(a-b)/math.tau
                        if abs(delta-round(delta)) > 1e-12:
                            raise ValueError('NOT_PERIODICALLY_EQUIVALENT')
                q = chosen['q_rad']; env = old['environment']
                if any(q[i]!=old['original_endpoint']['q_rad'][i] for i in old['active_indices_frozen']):
                    raise ValueError('ACTIVE_ANGLES_CHANGED')
                metrics = closure_metrics(q,env)
                if metrics['position_max_abs']>1e-5 or metrics['rotation_matrix_max_abs']>1e-5 or not limit_score(q,env)['legal']:
                    raise ValueError('SAVED_MATH_RECHECK_FAILED')
                execution['collision_adapter_calls_started'] += 1
                stream.write(json.dumps({'event':'collision_started','saved_candidate':item,'q_rad':q})+'\n')
                result = check_collision(env,q,timeout_s=min(15.,budget.remaining()),manifest_path=spec['v3_manifest'])
                execution['collision_adapter_calls_completed'] += 1
                budget.check()
                passed = result.get('status')=='CHECKED' and result.get('collision') is False
                record = {'environment':env,'endpoint':old['endpoint'],'classification':'RECONSTRUCTED',
                    'historical_status_unchanged':old['status'], 'original_endpoint_closure_qualified':False,
                    'source_candidate':item, 'branch':chosen['branch'], 'true_2pi_lifts':chosen['true_2pi_lifts'],
                    'active_coordinates_exactly_unchanged':True, 'independent_closure_metrics':metrics,
                    'limits':limit_score(q,env), 'passive_l2_delta_rad':chosen['passive_l2_delta_rad'],
                    'passive_linf_delta_rad':chosen['passive_linf_delta_rad'],
                    'periodically_equivalent_prequalified_candidates':len(pre), 'collision':result,
                    'status':'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED' if passed else 'UNKNOWN_OR_FAILED_COLLISION',
                    'selected_q_rad':q if passed else None, 'full_physical_geometry_or_CCD_qualified':False}
                save_new(folder/(env+'_'+old['endpoint']+'.json'),record)
                records.append(record)
                stream.write(json.dumps({'event':'collision_finished','result':record},allow_nan=False)+'\n')
        execution['status']='EVIDENCE_RECORDED'
    except BaseException as error:
        execution['status']='STOPPED';execution['error']=repr(error)
    finally:
        close_sessions()
        import time
        execution.update(wall_s=time.monotonic()-budget.started,cpu_s=cpu_seconds()-started_cpu,
            endpoint_status_counts=dict(Counter(r['status'] for r in records)),
            endpoint_summary=[{k:r[k] for k in ('environment','endpoint','status','source_candidate')} for r in records],
            bound_files_unchanged=all(digest(Path(p) if p.startswith('/') else ROOT/p)==h for p,h in spec['bound_files_sha256'].items()))
        execution['a_total_wall_s']=old_execution['wall_s']+execution['wall_s']
        execution['a_total_cpu_s']=old_execution['cpu_s']+execution['cpu_s']
        save_new(folder/'execution.json',execution)
    print(json.dumps(execution,ensure_ascii=False))


if __name__=='__main__':
    main()
