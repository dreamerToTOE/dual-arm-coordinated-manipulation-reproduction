#!/usr/bin/env python3
"""Bounded VI RSS candidate-A qualification; independent reconstruction.

No experiment runs without a committed, frozen JSON protocol.  --describe-protocol
prints a draft only.  Existing author/R1/R2 files are never changed.  The one-shot
budget claim prevents a crash or a different run_id from silently resetting the
same authorization.  This program does not implement a planner or an RBS bridge.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import random
import resource
import signal
import subprocess
import sys
import time

# One scientific process at a time; a BLAS thread pool must not turn a bounded
# qualification into an undeclared parallel benchmark.
THREAD_ENV_BEFORE = {k: os.environ.get(k) for k in (
    'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
    'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')}
for _key in THREAD_ENV_BEFORE:
    os.environ[_key] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np

from baselines.p4_full.geometry_consistent.physical_nr import (
    arm_fk_jac, closure_vector_jacobian, model_geometry, source_limits,
)
from baselines.p4_full.geometry_consistent.rss_geometry import (
    apply_mode, singularity_factors, vi_constraint_jacobian_at_closure,
    vi_rank_report, vi_residual_transforms, vi_target_poses,
)

SCHEMA = 'P4_R2_VI_RSS_RECONSTRUCTED_QUALIFICATION_V1'
BUDGET_ID = 'P4_R2_VI_RSS_USER_960_180W_360CPU_20261015'
SEEDS = [7, 23, 41, 101, 20261013]
PRIOR_RUNS = ['20261015_R2_SPATIAL01', '20261015_R2_PLANAR01',
              '20261015_R2_RSS_CONSTRUCTION01', '20261015_R2_COLLISION_CONTROLS01',
              '20261015_R2_ENDPOINT_RECONSTRUCTED01']
SAVED = ROOT/'results/p4_full/20261015_R2_SPATIAL01/VI/observations.json'
BINARY = ROOT/'build/p4_full/20261015_R2_SPATIAL01/comau_vi_batch'
COLLISION_MANIFEST = Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v2/manifest.json')
COLLISION_CONTROLS = ROOT/'results/p4_full/20261015_R2_COLLISION_CONTROLS01/result.json'
GATES = {'position_maxabs_mm': 1e-5, 'rotation_matrix_maxabs': 1e-5,
         'fk_position_maxabs_mm': 1e-7, 'fk_rotation_matrix_maxabs': 1e-10,
         'rank_relative': 1e-6, 'rank_position_mm_to_m': .001,
         'jacobian_fd_epsilon': 1e-6, 'jacobian_position_maxabs': 5e-6,
         'jacobian_angular_maxabs': 5e-7, 'require_full_constraint_rank': 12,
         'branch_zero_relative_epsilon': 64*np.finfo(float).eps}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def new_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def draft_protocol():
    return {'schema': SCHEMA, 'frozen': False, 'run_id': '20261015_R2_VI_RSS_RECONSTRUCTED01',
            'authorization_budget_id': BUDGET_ID,
            'classification': 'RECONSTRUCTED / INDEPENDENT-RECONSTRUCTION',
            'active_arm': 1, 'designated_passive_arms': [2, 3],
            'designated_passive_probabilities': [.5, .5], 'singular_mode': 1,
            'rss_gamma': .2, 'gamma_scope': 'Preserved planner parameter; this is a conditional singular-request qualification, no planner Bernoulli events.',
            'seeds': SEEDS, 'requests_per_seed': 6, 'attempts_per_request': 32,
            'budget': {'max_candidate_constructions': 960, 'wall_s': 180., 'cpu_s': 360.,
                       'r2_total_wall_s': 3600., 'r2_total_cpu_s': 7200.},
            'prior_runs': PRIOR_RUNS, 'gates': GATES,
            'random_stream': 'Python random.Random(seed), separate seed streams. Per request: one random()<0.5 selects s, held for all retries. Each construction draws all6 uniform source-limit angles then sets q5=0. After all8 roots/arm, one random() chooses uniformly from ascending source-bound-legal roots, for arm1 then other arm. No root replacement after collision.',
            'ik_branches_per_construct': 'All8 for arm1 and all8 for other passive arm, even if either list is empty; no designated-arm IK/re-solving.',
            'root_policy': 'Original0..7 numbered, source-accepted finite source-bound-legal roots. Every accepted root must independently round-trip; a soundness failure stops the run. Duplicated roots retain their source branch multiplicity.',
            'ik_binary': str(BINARY.relative_to(ROOT)),
            'ik_binary_sha256': sha(BINARY) if BINARY.is_file() else 'MUST_SET_BEFORE_FREEZE',
            'saved_q0_observations': str(SAVED.relative_to(ROOT)),
            'saved_q0_observations_sha256': sha(SAVED),
            'collision_checker_command': [sys.executable, '-m', 'baselines.p4_full.geometry_consistent.collision_adapter'],
            'collision_manifest': str(COLLISION_MANIFEST),
            'collision_manifest_sha256': sha(COLLISION_MANIFEST) if COLLISION_MANIFEST.is_file() else 'MUST_SET_BEFORE_FREEZE',
            'collision_controls_result': str(COLLISION_CONTROLS.relative_to(ROOT)),
            'collision_controls_result_sha256': sha(COLLISION_CONTROLS) if COLLISION_CONTROLS.is_file() else 'MUST_SET_AFTER_CONTROLS_BEFORE_FREEZE',
            'collision_qualification_scope': 'Qualified original discrete source pair/mesh/tolerance policy only; complete physical geometry, omitted pairs and CCD remain unverified.',
            'collision_checker_contract': 'stdin one JSON line {environment:VI,q:[18 angles]}; stdout exactly one JSON object with status and collision bool/null. Only actual qualified original-PQP call with collision=false can qualify.',
            'collision_success_statuses': ['CHECKED'],
            'positive_coverage_gate': 'At least one fully closure/bounds/rank/collision-qualified candidate with each designated passive arm2/3. Request failures remain failures; this gate is not RSS/RBS/planning PASS.',
            'q2_branch_bridge': 'NOT_IMPLEMENTED_NOT_EXECUTED; no global RSS success claim',
            'no_reset_policy': 'Atomic fixed authorization claim; this runner refuses any second launch, including after crash. Claim is not a claim that all960 were used. Preserve prefix and actual remaining; an evidenced correction may continue within those remaining limits only under a new frozen continuation protocol/source, without resetting the original authorization.'}


class StopQualification(RuntimeError):
    pass


class RunBudget:
    def __init__(self, spec, prior_wall, prior_cpu):
        self.started = time.monotonic()
        self.cpu_start = self.cpu()
        self.wall_cap = min(spec['budget']['wall_s'],
                            spec['budget']['r2_total_wall_s']-prior_wall)
        self.cpu_cap = min(spec['budget']['cpu_s'],
                           spec['budget']['r2_total_cpu_s']-prior_cpu)
        self.previous_handler = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, self._alarm)
        if min(self.wall_cap, self.cpu_cap) <= 0:
            raise StopQualification('R2_PREVIOUS_BUDGET_EXHAUSTED')
        signal.setitimer(signal.ITIMER_REAL, self.wall_cap)

    @staticmethod
    def cpu():
        a = resource.getrusage(resource.RUSAGE_SELF)
        b = resource.getrusage(resource.RUSAGE_CHILDREN)
        return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime

    def _alarm(self, *_):
        raise StopQualification('VI_RSS_WALL_BUDGET')

    def remaining(self):
        wall = self.wall_cap-(time.monotonic()-self.started)
        cpu = self.cpu_cap-(self.cpu()-self.cpu_start)
        if min(wall, cpu) <= 0:
            raise StopQualification('VI_RSS_WALL_OR_CPU_BUDGET')
        return min(wall, cpu)

    def close(self):
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, self.previous_handler)


class Evidence:
    def __init__(self, folder, budget):
        self.folder, self.budget = folder, budget
        self.events = (folder/'events.jsonl').open('x', buffering=1)
        self.process_number = 0

    def event(self, kind, **values):
        self.events.write(json.dumps({'event': kind, 'at_utc': utc(), **values},
                                    ensure_ascii=False, allow_nan=False)+'\n')
        self.events.flush()

    def process(self, command, input_text, label, environment=None):
        self.budget.remaining()
        self.process_number += 1
        stem = f'{self.process_number:05d}_{label}'
        inp, stdout, stderr = [self.folder/(stem+suffix) for suffix in
                               ('.input.txt', '.stdout.txt', '.stderr.txt')]
        inp.write_text(input_text)
        started = time.monotonic()
        self.event('process_started', label=label, command=command, input=str(inp.relative_to(ROOT)))
        proc = None
        try:
            with inp.open() as fin, stdout.open('x') as fout, stderr.open('x') as ferr:
                proc = subprocess.Popen(command, stdin=fin, stdout=fout, stderr=ferr,
                                        cwd=ROOT, start_new_session=True,
                                        env={**os.environ, **(environment or {})})
                while proc.poll() is None:
                    # Serial one-thread child, wall deadline and aggregate
                    # reaped CPU are checked; no unaccounted concurrent worker.
                    timeout = min(.02, self.budget.remaining())
                    try:
                        proc.wait(timeout=timeout)
                    except subprocess.TimeoutExpired:
                        pass
        except BaseException:
            if proc is not None and proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            self.event('process_interrupted', label=label, wall_s=time.monotonic()-started)
            raise
        self.event('process_finished', label=label, exit_code=proc.returncode,
                   wall_s=time.monotonic()-started, stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))
        self.budget.remaining()
        if proc.returncode:
            raise StopQualification('PROCESS_FAILED_'+label+'_'+str(proc.returncode))
        return stdout.read_text()


def errors(actual, target):
    delta = np.asarray(actual)-np.asarray(target)
    return {'position_maxabs_mm': float(np.max(np.abs(delta[:3, 3]))),
            'rotation_matrix_maxabs': float(np.max(np.abs(delta[:3, :3])))}


def closed(metric):
    return (metric['position_maxabs_mm'] <= GATES['position_maxabs_mm'] and
            metric['rotation_matrix_maxabs'] <= GATES['rotation_matrix_maxabs'])


def poses_and_body(q):
    poses, bodies = [], []
    for arm in (1, 2, 3):
        pose, world_geometric = arm_fk_jac(q[6*(arm-1):6*arm], 'VI', arm)
        # arm_fk_jac linear rows are velocity of the EE origin, not spatial
        # twist v at the world origin.  Rotate both blocks, with no spurious
        # translation skew term, to obtain [v_body, omega_body].
        rotate = np.zeros((6, 6))
        rotate[:3, :3] = pose[:3, :3].T
        rotate[3:, 3:] = pose[:3, :3].T
        poses.append(pose)
        bodies.append(rotate@world_geometric)
    return poses, bodies


def rank_data(jacobian, linear_rows):
    scaled = np.asarray(jacobian).copy()
    scaled[list(linear_rows)] *= GATES['rank_position_mm_to_m']
    values = np.linalg.svd(scaled, compute_uv=False)
    cutoff = GATES['rank_relative']*float(values[0])
    return {'rank': int(np.count_nonzero(values > cutoff)),
            'singular_values': values.tolist(), 'cutoff': cutoff}


def q0_math(spec, evidence, grasps):
    records = json.loads((ROOT/spec['saved_q0_observations']).read_text())
    fixtures = [r for r in records if r['kind'] == 'additional_component_fixture_only']
    if [r['endpoint'] for r in fixtures] != ['start', 'goal']:
        raise StopQualification('Q0_SAVED_FIXTURE_CARDINALITY')
    for row in fixtures:
        evidence.budget.remaining()
        q = np.asarray(row['q'])
        poses, bodies = poses_and_body(q)
        metrics = [errors(poses[i+1], poses[0]@grasps[i]@np.diag([-1., -1., 1., 1.])) for i in (0, 1)]
        g, physical_j = closure_vector_jacobian(q, 'VI')
        fd = np.empty_like(physical_j)
        eps = GATES['jacobian_fd_epsilon']
        for k in range(18):
            evidence.budget.remaining()
            step = np.zeros(18); step[k] = eps
            fd[:, k] = (closure_vector_jacobian(q+step, 'VI')[0]-
                        closure_vector_jacobian(q-step, 'VI')[0])/(2*eps)
        body_j = vi_constraint_jacobian_at_closure(*bodies, *grasps)
        coordinate_map = np.zeros((12, 12))
        for block, pose in enumerate(poses[1:]):
            for offset in (0, 3):
                begin = 6*block+offset
                coordinate_map[begin:begin+3, begin:begin+3] = -pose[:3, :3].T
        p_rows, r_rows = [0, 1, 2, 6, 7, 8], [3, 4, 5, 9, 10, 11]
        fd_error = np.abs(fd-physical_j)
        coordinate_error = np.abs(body_j-coordinate_map@physical_j)
        transform_checks = []
        for s in (2, 3):
            targets = vi_target_poses(poses[s-1], s, *grasps)
            transform_checks.extend(errors(poses[a-1], targets[a]) for a in (1, 2, 3))
        passed = (all(closed(m) for m in metrics+transform_checks) and
                  float(fd_error[p_rows].max()) <= GATES['jacobian_position_maxabs'] and
                  float(fd_error[r_rows].max()) <= GATES['jacobian_angular_maxabs'] and
                  float(coordinate_error[p_rows].max()) <= GATES['jacobian_position_maxabs'] and
                  float(coordinate_error[r_rows].max()) <= GATES['jacobian_angular_maxabs'])
        evidence.event('q0_math', endpoint=row['endpoint'], passed=passed, q=q.tolist(),
                       closure_metrics=metrics, target_recipe_metrics=transform_checks,
                       physical_residual=g.tolist(), physical_jacobian=physical_j.tolist(),
                       finite_difference_jacobian=fd.tolist(), body_jacobian=body_j.tolist(),
                       world_to_body_residual_map=coordinate_map.tolist(),
                       fd_position_maxabs=float(fd_error[p_rows].max()),
                       fd_angular_maxabs=float(fd_error[r_rows].max()),
                       body_coordinate_position_maxabs=float(coordinate_error[p_rows].max()),
                       body_coordinate_angular_maxabs=float(coordinate_error[r_rows].max()))
        if not passed:
            raise StopQualification('Q0_MATHEMATICAL_QUALIFICATION_FAILED')


def all_roots(targets, arms, designated_arm, designated_q, binary, folder, evidence, number):
    raw_output = folder/f'ik_{number:04d}.jsonl'
    lines = [' '.join(['K', str(arm), str(branch)]+[format(v, '.17g') for v in targets[arm].ravel()])
             for arm in arms for branch in range(8)]
    lines.append(' '.join(['F', str(designated_arm)]+[format(v, '.17g') for v in designated_q]))
    evidence.process([str(binary), str(raw_output)], '\n'.join(lines)+'\n', f'ik_{number:04d}')
    rows = [json.loads(line) for line in raw_output.read_text().splitlines()]
    if len(rows) != 17:
        raise StopQualification('IK_16_ROOT_PLUS_SAMPLED_FK_CARDINALITY')
    sampled = rows[-1]
    if (sampled['environment'] != 'VI' or sampled['model'] != 6 or
            sampled['op'] != 'F' or sampled['arm'] != designated_arm or
            not sampled['success'] or not sampled['finite'] or sampled.get('error')):
        raise StopQualification('SAMPLED_ARM_NATIVE_FK_INTERFACE_FAILED')
    sampled_error = errors(sampled['T'], targets[designated_arm])
    sampled_passed = (sampled_error['position_maxabs_mm'] <= GATES['fk_position_maxabs_mm'] and
                      sampled_error['rotation_matrix_maxabs'] <= GATES['fk_rotation_matrix_maxabs'])
    evidence.event('sampled_arm_native_fk_crosscheck', construction=number,
                   designated_arm=designated_arm, native=sampled,
                   independent_errors=sampled_error, passed=sampled_passed)
    if not sampled_passed:
        raise StopQualification('SAMPLED_ARM_NATIVE_FK_DISAGREES_WITH_INDEPENDENT_ORACLE')
    result, bounds = {}, source_limits('VI')
    for arm in arms:
        annotated = []
        for branch in range(8):
            row = rows[len(annotated)+(0 if arm == arms[0] else 8)]
            if (row['environment'] != 'VI' or row['model'] != 6 or row['op'] != 'K' or
                    row['arm'] != arm or row['branch'] != branch or row.get('error')):
                raise StopQualification('IK_ROOT_IDENTITY_OR_INTERFACE_ERROR')
            item = {'branch': branch, 'native': row, 'source_bounds_legal': False,
                    'independent_roundtrip': None, 'geometric_branch_identity': None,
                    'requested_branch_in_geometric_set': None}
            if row['success']:
                q = np.asarray(row['solution'], dtype=float)
                if q.shape != (6,) or not np.isfinite(q).all() or not row['finite']:
                    raise StopQualification('IK_NONFINITE_ACCEPTED')
                item['source_bounds_legal'] = bool(np.all((bounds[6*(arm-1):6*arm, 0] <= q) &
                                                         (q <= bounds[6*(arm-1):6*arm, 1])))
                item['independent_roundtrip'] = errors(arm_fk_jac(q, 'VI', arm)[0], targets[arm])
                item['geometric_branch_identity'] = geometric_branch_identity(q)
                item['requested_branch_in_geometric_set'] = branch in item['geometric_branch_identity']['branch_set']
                if not item['requested_branch_in_geometric_set']:
                    evidence.event('ik_branch_identity_mismatch', arm=arm, **item)
                    raise StopQualification('IK_REQUESTED_BRANCH_NOT_IN_INDEPENDENT_GEOMETRIC_SET')
                if not closed(item['independent_roundtrip']):
                    evidence.event('ik_unsound_root', arm=arm, **item)
                    raise StopQualification('IK_ACCEPTED_ROOT_UNSOUND')
            annotated.append(item)
        result[arm] = annotated
    return result


def select_root(roots, rng):
    legal = [r for r in roots if r['native']['success'] and r['source_bounds_legal']]
    if not legal:
        return None, {'legal_branches': [], 'choice_u': None, 'selected_branch': None}
    u = rng.random()
    selected = legal[min(int(u*len(legal)), len(legal)-1)]
    return selected, {'legal_branches': [r['branch'] for r in legal], 'choice_u': u,
                      'selected_branch': selected['branch']}


def geometric_branch_identity(q):
    """Independent periodic invariants for all source branch labels.

    Zero factors retain their entire meeting branch set.  In particular an
    accepted FK round-trip does not certify that the requested branch label
    identifies that returned state.  This is not an RBS adjacency certificate.
    """
    factors = singularity_factors(q, 'COMAU')
    radial = factors['shoulder_radial_factor_mm']
    elbow_factor = -math.sin(float(q[2])+float(factors['alpha_rad']))
    wrist_factor = math.sin(float(q[4]))
    epsilon = GATES['branch_zero_relative_epsilon']
    radial_scale = 524.5+1250.+math.hypot(210., 1436.5)
    def sign(value, scale=1.):
        return None if abs(value) <= epsilon*scale else (1 if value > 0 else -1)
    shoulder, elbow, wrist = sign(radial, radial_scale), sign(elbow_factor), sign(wrist_factor)
    q3_sign = (1, -1, 1, -1, 1, -1, 1, -1)
    wrist_sign = (1, -1, -1, 1, -1, 1, 1, -1)
    labels = [i for i in range(8)
              if (shoulder is None or (1 if i < 4 else -1) == shoulder)
              and (elbow is None or q3_sign[i] == elbow)
              and (wrist is None or wrist_sign[i] == wrist)]
    return {'unique': all(x is not None for x in (shoulder, elbow, wrist)),
            'branch_set': labels, 'geometric_factors': factors,
            'signed_shoulder_radius_mm': radial, 'shoulder_scale_mm': radial_scale,
            'elbow_factor': elbow_factor, 'wrist_factor': wrist_factor,
            'shoulder_sign': shoulder, 'elbow_sign': elbow, 'wrist_sign': wrist,
            'branch_zero_relative_epsilon': epsilon,
            'label_basis': 'Independent source numbering invariants: signed shoulder radius; -sin(q3+alpha); sin(q5). Meeting sets retained, not certified RBS paths.',
            'source_elbow_sign_by_label': list(q3_sign),
            'source_wrist_sign_by_label': list(wrist_sign)}


def sampled_branch_identity(q):
    return {**geometric_branch_identity(q), 'sampled_q_preserved': True,
            'wrist_family_actual_q4_q6_rad': [float(q[3]), float(q[5])],
            'wrist_family_sum_rad': float(q[3]+q[5])}


def collision_check(spec, q, evidence, number):
    text = evidence.process(spec['collision_checker_command'],
                            json.dumps({'environment': 'VI', 'q': q.tolist()})+'\n',
                            f'collision_{number:04d}',
                            environment={'P4_COLLISION_MANIFEST': str(ROOT/spec['collision_manifest'])})
    try:
        result = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise StopQualification('COLLISION_INVALID_JSON') from exc
    evidence.event('collision_result', construction=number, result=result)
    if (result.get('environment') != 'VI' or
            result.get('manifest_sha256') != spec['collision_manifest_sha256'] or
            result.get('status') not in spec['collision_success_statuses'] or
            type(result.get('collision')) is not bool):
        raise StopQualification('COLLISION_NOT_QUALIFIED_OR_NOT_CHECKED')
    return result


def run_candidates(spec, evidence, binary, grasps, counts):
    bounds = source_limits('VI')
    full_linear = (0, 1, 2, 6, 7, 8)
    number = 0
    for seed in SEEDS:
        rng = random.Random(seed)
        for request in range(6):
            evidence.budget.remaining()
            choose_s = rng.random(); s = 2 if choose_s < .5 else 3
            other = 5-s
            counts['requests_started'] += 1
            evidence.event('request_started', seed=seed, request=request, designated_passive_arm=s,
                           designated_arm_u=choose_s, mode=1, gamma=.2)
            success = False
            for attempt in range(32):
                evidence.budget.remaining()
                if number >= 960:
                    raise StopQualification('MAX_960_CANDIDATE_CONSTRUCTIONS')
                number += 1; counts['candidate_constructions'] += 1
                raw = np.array([rng.uniform(lo, hi) for lo, hi in bounds[6*(s-1):6*s]])
                qs = apply_mode(raw, 'COMAU', 1)
                evidence.event('construction_started', construction=number, seed=seed,
                               request=request, attempt=attempt, designated_passive_arm=s,
                               raw_uniform_q_rad=raw.tolist(), forced_q_rad=qs.tolist(),
                               rng_state_after_joint_draws=repr(rng.getstate()))
                ts, js_world = arm_fk_jac(qs, 'VI', s)
                sampled_rank = rank_data(js_world, (0, 1, 2))
                evidence.event('designated_singular_fk_and_rank', construction=number,
                               designated_arm=s, world_pose=ts.tolist(),
                               source_bounds_legal=bool(np.all((bounds[6*(s-1):6*s, 0] <= qs) &
                                                               (qs <= bounds[6*(s-1):6*s, 1]))),
                               world_geometric_jacobian=js_world.tolist(),
                               rank=sampled_rank, branch_set=sampled_branch_identity(qs))
                if sampled_rank['rank'] >= 6:
                    raise StopQualification('SAMPLED_WRIST_MODE_IS_NOT_TRUE_SINGULAR')
                targets = vi_target_poses(ts, s, *grasps)
                counts['ik_branch_evaluations_requested'] += 16
                counts['sampled_arm_native_fk_requests'] += 1
                roots = all_roots(targets, (1, other), s, qs, binary, evidence.folder, evidence, number)
                counts['ik_branch_evaluations_completed'] += 16
                chosen1, choice1 = select_root(roots[1], rng)
                chosen_other, choice_other = select_root(roots[other], rng)
                record = {'construction': number, 'seed': seed, 'request': request,
                          'attempt': attempt, 'designated_passive_arm': s,
                          'target_poses': {str(a): t.tolist() for a, t in targets.items()},
                          'all_roots': {str(a): r for a, r in roots.items()},
                          'root_choices': {'1': choice1, str(other): choice_other},
                          'rng_state_after_root_choices': repr(rng.getstate()),
                          'fully_qualified_candidate': False, 'collision_checked': False,
                          'source_policy_collision_qualified': False,
                          'full_geometry_collision_qualified': False,
                          'continuous_collision_certificate': False,
                          'RBS_or_branch_bridge_checked': False}
                reasons = []
                if chosen1 is None: reasons.append('ACTIVE_ARM1_NO_SOURCE_BOUND_LEGAL_ROOT')
                if chosen_other is None: reasons.append('OTHER_PASSIVE_NO_SOURCE_BOUND_LEGAL_ROOT')
                if reasons:
                    record['rejection_reasons'] = reasons
                    evidence.event('construction_finished', **record)
                    counts.update(reasons)
                    continue
                q = np.empty(18)
                q[6*(s-1):6*s] = qs
                q[:6] = chosen1['native']['solution']
                q[6*(other-1):6*other] = chosen_other['native']['solution']
                poses, bodies = poses_and_body(q)
                metrics = [errors(poses[i+1], poses[0]@grasps[i]@np.diag([-1., -1., 1., 1.])) for i in (0, 1)]
                transforms = vi_residual_transforms(*poses, *grasps)
                rank = vi_rank_report(*bodies, *grasps, relative_threshold=GATES['rank_relative'])
                _, physical_j = closure_vector_jacobian(q, 'VI')
                physical_ranks = {'full': rank_data(physical_j, full_linear),
                                  'passive': rank_data(physical_j[:, 6:], full_linear)}
                legal = bool(np.all((bounds[:, 0] <= q) & (q <= bounds[:, 1])))
                record.update(q_rad=q.tolist(), physical_loop_metrics=metrics,
                              loop_error_transforms=[t.tolist() for t in transforms],
                              all_three_source_bounds_legal=legal, body_rank_report=rank,
                              independent_world_residual_rank_report=physical_ranks,
                              branch_identity={'active_arm': 1,
                                  'selected_arm1_branch': choice1['selected_branch'],
                                  'selected_other_passive_arm': other,
                                  'selected_other_passive_branch': choice_other['selected_branch'],
                                  'designated_singular_arm': s,
                                  'sampled_singular_branch_set': sampled_branch_identity(qs)})
                if not all(closed(m) for m in metrics): reasons.append('DUAL_CLOSURE_REJECTED')
                if not legal: reasons.append('THREE_ARM_SOURCE_JOINT_LIMIT_REJECTED')
                designated_rank = rank['passive_arm_'+str(s)]['rank']
                if designated_rank >= 6 or rank['passive_12_by_12']['rank'] >= 12:
                    reasons.append('PASSIVE_NOT_TRUE_RANK_DEFICIENT')
                if rank['full_12_by_18']['rank'] != 12: reasons.append('FULL_CONSTRAINT_RANK_NOT_12')
                if (physical_ranks['full']['rank'] != rank['full_12_by_18']['rank'] or
                        physical_ranks['passive']['rank'] != rank['passive_12_by_12']['rank']):
                    reasons.append('INDEPENDENT_RANK_COUNTS_DISAGREE')
                # Save before calling any external checker, so interruption
                # cannot erase a mathematically closed candidate or root choice.
                evidence.event('candidate_pre_collision', **record, rejection_reasons=reasons)
                if not reasons:
                    counts['collision_queries_started'] += 1
                    result = collision_check(spec, q, evidence, number)
                    counts['collision_queries_completed'] += 1
                    record['collision_checked'] = True; record['collision'] = result
                    record['source_policy_collision_qualified'] = not result['collision']
                    if result['collision']: reasons.append('ORIGINAL_PQP_COLLISION')
                record['rejection_reasons'] = reasons
                record['fully_qualified_candidate'] = not reasons and record['collision_checked']
                evidence.event('construction_finished', **record)
                counts.update(reasons)
                if record['fully_qualified_candidate']:
                    counts['fully_qualified_candidates'] += 1
                    counts['fully_qualified_designated_arm'+str(s)] += 1
                    success = True
                    break
            counts['requests_completed'] += 1
            counts['requests_success' if success else 'requests_failed_32_constructions'] += 1
            evidence.event('request_finished', seed=seed, request=request,
                           designated_passive_arm=s, succeeded=success,
                           constructions=attempt+1, rng_final_state=repr(rng.getstate()))


def validate_protocol(spec, path):
    expected = draft_protocol()
    exact = ('schema', 'authorization_budget_id', 'classification', 'active_arm',
             'designated_passive_arms', 'designated_passive_probabilities',
             'singular_mode', 'rss_gamma', 'seeds', 'requests_per_seed',
             'attempts_per_request', 'budget', 'prior_runs', 'gates')
    for key in exact:
        if spec.get(key) != expected[key]:
            raise StopQualification('PROTOCOL_CONSTANT_MISMATCH_'+key)
    if spec.get('frozen') is not True:
        raise StopQualification('PROTOCOL_NOT_FROZEN')
    run_id = spec.get('run_id', '')
    if not run_id or Path(run_id).name != run_id or run_id in ('.', '..'):
        raise StopQualification('INVALID_RUN_ID')
    binary = ROOT/spec['ik_binary']
    saved = ROOT/spec['saved_q0_observations']
    if sha(binary) != spec['ik_binary_sha256'] or sha(saved) != spec['saved_q0_observations_sha256']:
        raise StopQualification('FROZEN_INPUT_HASH_MISMATCH')
    if sha(ROOT/spec['collision_manifest']) != spec['collision_manifest_sha256']:
        raise StopQualification('FROZEN_COLLISION_MANIFEST_HASH_MISMATCH')
    controls_path = ROOT/spec['collision_controls_result']
    if sha(controls_path) != spec['collision_controls_result_sha256']:
        raise StopQualification('FROZEN_COLLISION_CONTROLS_HASH_MISMATCH')
    controls = json.loads(controls_path.read_text())
    if controls.get('status') != 'SOURCE_POLICY_QUALIFIED' or controls.get('passed') is not True:
        raise StopQualification('COLLISION_SOURCE_POLICY_CONTROLS_NOT_QUALIFIED')
    if not isinstance(spec.get('collision_checker_command'), list) or not spec['collision_checker_command']:
        raise StopQualification('COLLISION_COMMAND_REQUIRED')
    if not spec.get('collision_success_statuses'):
        raise StopQualification('COLLISION_SUCCESS_STATUS_REQUIRED')
    sources = [Path(__file__).resolve(), path,
               ROOT/'baselines/p4_full/geometry_consistent/physical_nr.py',
               ROOT/'baselines/p4_full/geometry_consistent/rss_geometry.py',
               ROOT/'baselines/p4_full/geometry_consistent/collision_adapter.py',
               ROOT/'baselines/p4_full/analyze_comau_native_qualification.py',
               ROOT/'baselines/p4_full/abb_independent_oracle.py']
    checker_script = [ROOT/token for token in spec['collision_checker_command'] if token.endswith('.py')]
    sources.extend(checker_script)
    for source in sources:
        relative = source.resolve().relative_to(ROOT)
        subprocess.run(['git', 'ls-files', '--error-unmatch', str(relative)],
                       check=True, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.check_output(['git', 'status', '--porcelain', '--', str(relative)], cwd=ROOT, text=True):
            raise StopQualification('SOURCE_OR_PROTOCOL_NOT_COMMITTED_'+str(relative))
    return binary, {str(p.relative_to(ROOT)): sha(p) for p in sources}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe-protocol', action='store_true', help='Print draft JSON; no FK/IK/RNG/collision experiment.')
    parser.add_argument('--protocol', type=Path, help='Committed frozen protocol JSON; creates unique evidence directory.')
    args = parser.parse_args()
    if args.describe_protocol:
        print(json.dumps(draft_protocol(), ensure_ascii=False, indent=2)); return 0
    if not args.protocol:
        parser.error('--protocol is required for execution')
    path = args.protocol.resolve(); spec = json.loads(path.read_text())
    binary, sources = validate_protocol(spec, path)
    previous = [json.loads((ROOT/'results/p4_full'/run/'execution.json').read_text()) for run in PRIOR_RUNS]
    prior_wall = sum(r['wall_s'] for r in previous)
    prior_cpu = sum(r['cpu_s'] for r in previous)
    # A fixed, atomic claim outside run_id prevents rename-and-restart.  It is
    # retained even on exception.  No script option removes or overrides it.
    claim = ROOT/'results/p4_full'/(BUDGET_ID+'.claim.json')
    out = ROOT/'results/p4_full'/spec['run_id']
    if out.exists(): raise StopQualification('OUTPUT_EXISTS_NO_OVERWRITE')
    new_json(claim, {'budget_id': BUDGET_ID, 'run_id': spec['run_id'], 'created_at_utc': utc(),
                     'protocol_sha256': sha(path), 'wall_cap_s': 180, 'cpu_cap_s': 360,
                     'max_constructions': 960, 'policy': 'Retain after interruption; no automatic budget reset.'})
    out.mkdir(parents=True, exist_ok=False)
    record = {'schema': SCHEMA, 'run_id': spec['run_id'], 'authorization_budget_id': BUDGET_ID,
              'started_at_utc': utc(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'git_status_at_start': subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True),
              'source_hashes': sources, 'protocol_sha256': sha(path), 'ik_binary_sha256': sha(binary),
              'previous_wall_s': prior_wall, 'previous_cpu_s': prior_cpu,
              'prior_execution_hashes': {r: sha(ROOT/'results/p4_full'/r/'execution.json') for r in PRIOR_RUNS},
              'collision_controls_result_sha256': spec['collision_controls_result_sha256'],
              'collision_qualification_scope': spec['collision_qualification_scope'],
              'formal_planning_calls': 0, 'RBS_or_branch_bridge_checked': False,
              'classification': spec['classification'], 'thread_environment_before': THREAD_ENV_BEFORE,
              'rss_gamma': .2, 'gamma_used_for_planner_events': False}
    budget = RunBudget(spec, prior_wall, prior_cpu)
    evidence = Evidence(out, budget); counts = Counter()
    exit_code = 0
    try:
        evidence.event('run_started', protocol=spec, source_hashes=sources)
        grasps = model_geometry('VI')['grasps']
        q0_math(spec, evidence, grasps)
        run_candidates(spec, evidence, binary, grasps, counts)
        record['status'] = 'CANDIDATE_CONSTRUCTION_RECORDED'
    except BaseException as exc:
        record['status'] = 'STOP_RETAINED_PREFIX'
        record['error'] = repr(exc); exit_code = 2
        evidence.event('run_stopped', error=repr(exc))
    finally:
        budget.close()
        record.update(counts=dict(counts), wall_s=time.monotonic()-budget.started,
                      cpu_s=budget.cpu()-budget.cpu_start, ended_at_utc=utc())
        record['cumulative_execution_wall_s'] = prior_wall+record['wall_s']
        record['cumulative_execution_cpu_s'] = prior_cpu+record['cpu_s']
        retained = Counter()
        for native_path in out.glob('ik_*.jsonl'):
            for line in native_path.read_text().splitlines():
                try:
                    retained[json.loads(line)['op']] += 1
                except (ValueError, KeyError):
                    retained['INCOMPLETE_JSON_ROW'] += 1
        record['retained_native_output_rows'] = dict(retained)
        record['authorization_budget_remaining'] = {
            'candidate_constructions': max(0, 960-counts['candidate_constructions']),
            'wall_s': max(0., 180.-record['wall_s']),
            'cpu_s': max(0., 360.-record['cpu_s']),
            'r2_total_wall_s': max(0., 3600.-record['cumulative_execution_wall_s']),
            'r2_total_cpu_s': max(0., 7200.-record['cumulative_execution_cpu_s']),
            'policy': 'Not executable by rerunning this script. Preserve this prefix and freeze any evidenced continuation against these remaining caps; do not reset or duplicate sampled candidates.'}
        record['candidate_coverage_by_designated_arm'] = {
            str(a): {'fully_qualified': counts['fully_qualified_designated_arm'+str(a)],
                     'has_at_least_one': counts['fully_qualified_designated_arm'+str(a)] > 0}
            for a in (2, 3)}
        record['candidate_coverage_gate_passed'] = all(
            item['has_at_least_one'] for item in record['candidate_coverage_by_designated_arm'].values())
        record['coverage_gate_status'] = 'PASS' if record['candidate_coverage_gate_passed'] else 'FAIL'
        record['full_RSS_or_planning_pass'] = False
        record['scope_limitation'] = 'Candidates only. Adjacent branch identities are geometric, no RBS bridge, visibility, planner or original-author VI sampler equivalence validated.'
        new_json(out/'execution.json', record)
        evidence.events.close()
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
