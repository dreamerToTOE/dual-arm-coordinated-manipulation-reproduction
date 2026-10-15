"""Bounded, source-frozen R2 component execution. No planner or collision claim."""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

import numpy as np

from baselines.p4_full.geometry_consistent.spatial_ik_patch import stage_spatial_ik
from baselines.p4_full.geometry_consistent.physical_nr import (
    arm_fk_jac, closure_vector_jacobian, model_geometry, project_nr,
    residual_metrics, source_limits,
)
from baselines.p4_full.geometry_consistent.rss_geometry import apply_mode

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = ROOT/'configs/p4_full/r2_geometry_consistent_qualification_v1.json'
SOURCE_ROOT = Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit')
RAW = {
    'II': '20261014T1528_R1_ABB01/II_native.json',
    'III': '20261014T1528_R1_ABB01/III_native.json',
    'IV': '20261014T1545_R1_COMAU02/IV_native.jsonl',
    'V': '20261014T1545_R1_COMAU02/V_native.jsonl',
    'VI': '20261014T1550_R1_VI03/VI_native.jsonl',
}
SPECS = {'II': ('abb', 'CKCplanning', 0), 'III': ('abb', 'CKCplanning', 0),
         'IV': ('comau_iv', 'ckcComau2', 4),
         'V': ('comau_v', 'ckcComau_industrialScene', 5),
         'VI': ('comau_vi', 'ckcComau3', 6)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump_new(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def source_records(env):
    p = ROOT/'results/p4_full'/RAW[env]
    if p.suffix == '.json':
        x = json.loads(p.read_text())
        g = model_geometry(env)
        assert x['D_mm'] == g['bases'][1][0]*2
        assert x['L_mm'] == g['grasps'][0][0, 3]
        rr = x['rows']
        fk = [(r['index'], r['robot'], r['q'], r['T']) for r in rr if r['kind'] == 'fk']
        ik = [(r['index'], r['robot'], r['branch'], r['q'], r['target'])
              for r in rr if r['kind'] == 'ik']
        nr = [(r['index'], r['input']) for r in rr if r['kind'] == 'nr']
        ep = [(str(r['index']), r['q']) for r in rr if r['kind'] == 'raw_endpoint']
    else:
        rr = [json.loads(s) for s in p.read_text().splitlines()]
        fk = []
        for r in rr:
            if r['type'] == 'fk_sample':
                for i in range(model_geometry(env)['arms']):
                    fk.append((r['sample'], i+1, r['q_rad'][6*i:6*i+6], r['author_fk'][i]))
        ik = [(r['sample'], r['arm'], r['branch'], r['source_q_rad'], r['target'])
              for r in rr if r['type'] == 'ik_roundtrip']
        nr = [(r['sample'], r['input_q_rad']) for r in rr if r['type'] == 'nr_near_endpoint']
        ep = [(r['name'], r['q_rad']) for r in rr if r['type'] == 'raw_endpoint']
    assert len(ik) == 80 and len(nr) == 10 and len(ep) == 2
    return p, fk, ik, nr, ep


class Budget:
    def __init__(self, protocol):
        self.started = time.monotonic()
        self.cpu_start = self.cpu()
        self.p = protocol['budget']

    @staticmethod
    def cpu():
        a, b = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
        return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime

    def remaining(self):
        w = self.p['total_execution_wall_s']-(time.monotonic()-self.started)
        c = self.p['total_cpu_s']-(self.cpu()-self.cpu_start)
        if min(w, c) <= 0: raise TimeoutError('R2_GLOBAL_BUDGET')
        return min(120., w, c)


class Batch:
    def __init__(self, exe, env, folder, budget):
        self.exe, self.env, self.folder, self.budget = exe, env, folder, budget
        self.count = 0

    def __call__(self, requests):
        self.count += 1
        tag = f'{self.count:03d}'
        inp = self.folder/f'input_{tag}.txt'
        out = self.folder/f'output_{tag}.jsonl'
        log = self.folder/f'process_{tag}.log'
        text = '\n'.join(' '.join([op, str(arm)]+([str(branch)] if op == 'K' else [])+
                    [format(v, '.17g') for v in np.asarray(values).ravel()])
                    for op, arm, branch, values in requests)+'\n'
        inp.write_text(text)
        cmd = [str(self.exe), str(out)]
        if self.env in ('II', 'III'): cmd.extend(['--env', self.env])
        with inp.open('r') as fin, log.open('x') as flog:
            p = subprocess.run(cmd, stdin=fin, stdout=flog, stderr=subprocess.STDOUT,
                               timeout=self.budget.remaining(), cwd=ROOT)
        if p.returncode: raise RuntimeError(f'BATCH_FAILED_{self.env}_{tag}_{p.returncode}')
        rr = [json.loads(s) for s in out.read_text().splitlines()]
        if len(rr) != len(requests): raise RuntimeError('BATCH_CARDINALITY')
        return rr


def error_transform(a, b):
    delta = np.asarray(a)-np.asarray(b)
    return {'position_abs_max': float(np.max(np.abs(delta[:3, 3]))),
            'rotation_matrix_abs_max': float(np.max(np.abs(delta[:3, :3])))}


def check_error(errors, p=1e-5, r=1e-5):
    return errors['position_abs_max'] <= p and errors['rotation_matrix_abs_max'] <= r


def run_spatial(env, out, binary, budget, protocol):
    folder = out/env; folder.mkdir()
    batch = Batch(binary, env, folder, budget)
    rawpath, fk, ik, nr, endpoints = source_records(env)
    checks, observations = [], []
    def check(name, passed, detail):
        checks.append({'check': name, 'passed': bool(passed), 'detail': detail})
    def observe(kind, **kw):
        observations.append({'kind': kind, **kw})
    rr = batch([('F', arm, None, q) for _, arm, q, _ in fk])
    for (idx, arm, q, old), row in zip(fk, rr):
        target = arm_fk_jac(q, env, arm)[0]
        errors = error_transform(row['T'], target)
        check(f'FK_{idx}_arm{arm}', check_error(errors, 1e-7, 1e-10), errors)
        observe('fk_replay', index=idx, arm=arm, q=q, original_T=old,
                continuous_native_T=row['T'], independent_T=target.tolist(), errors=errors)
    # Exactly the same original q/branch. Original clipped targets get a
    # separate diagnostic, never silently replaced by continuous physical FK.
    requests, tags = [], []
    for idx, arm, branch, q, target in ik:
        for target_kind, t in [('original_saved_target', target),
                               ('physical_continuous_target', arm_fk_jac(q, env, arm)[0])]:
            requests.append(('K', arm, branch, t)); tags.append((idx, arm, branch, q, target_kind, t))
    rr = batch(requests)
    exists = Counter()
    for tag, row in zip(tags, rr):
        idx, arm, branch, q, target_kind, t = tag
        good = False
        errors = None
        if row['success']:
            errors = error_transform(arm_fk_jac(row['solution'], env, arm)[0], t)
            good = check_error(errors)
        if target_kind == 'physical_continuous_target':
            check(f'IK_sound_{idx}_{branch}', not row['success'] or good,
                  {'accepted': row['success'], 'errors': errors})
            exists[(idx, arm)] += int(good)
        observe('ik_replay', index=idx, arm=arm, branch=branch, target_kind=target_kind,
                source_q=q, target=np.asarray(t).tolist(), native=row, errors=errors,
                physical_roundtrip_qualified=good)
    for tag, count in exists.items():
        check(f'IK_target_has_solution_{tag}', count > 0, {'qualified_branches': count})
    # Fixed wrist strata, including the old source angle-truncation bands.
    wrist = protocol['fixtures']['additional_spatial_wrist_per_arm']
    requests, tags = [], []
    for arm in range(1, model_geometry(env)['arms']+1):
        for idx, q in enumerate(wrist):
            t = arm_fk_jac(q, env, arm)[0]
            for branch in range(8):
                requests.append(('K', arm, branch, t)); tags.append((arm, idx, branch, q, t))
    rr = batch(requests)
    exists = Counter()
    for (arm, idx, branch, q, t), row in zip(tags, rr):
        errors = error_transform(arm_fk_jac(row['solution'], env, arm)[0], t) if row['success'] else None
        good = row['success'] and check_error(errors)
        check(f'wrist_sound_{arm}_{idx}_{branch}', not row['success'] or good,
              {'accepted': row['success'], 'errors': errors})
        exists[(arm, idx)] += int(good)
        observe('fixed_wrist_ik', arm=arm, fixture=idx, branch=branch, q=q,
                target=t.tolist(), native=row, errors=errors)
    for tag, count in exists.items():
        check(f'wrist_target_has_solution_{tag}', count > 0, {'qualified_branches': count})
    # Fixed actual Jacobian derivative checks, not arbitrary large sample runs.
    for name, q in endpoints:
        q = np.array(q); _, j = closure_vector_jacobian(q, env)
        columns = []
        for k in range(len(q)):
            dq = np.zeros(len(q)); dq[k] = 1e-6
            columns.append((closure_vector_jacobian(q+dq, env)[0]-
                            closure_vector_jacobian(q-dq, env)[0])/2e-6)
        fd = np.column_stack(columns)
        pe = max(np.max(np.abs((j-fd)[i:i+3])) for i in range(0, len(j), 6))
        re = max(np.max(np.abs((j-fd)[i+3:i+6])) for i in range(0, len(j), 6))
        check('jacobian_'+name, pe <= 5e-6 and re <= 5e-7,
              {'translation_max_abs': float(pe), 'angular_max_abs': float(re)})
        observe('physical_jacobian', endpoint=name, input_q=q.tolist(),
                analytic=j.tolist(), finite_difference=fd.tolist())
        observe('raw_endpoint_unchanged', endpoint=name, q=q.tolist(),
                metrics=residual_metrics(q, env), formal_endpoint_repaired=False)
    # True singularity rank is checked with independent analytic derivatives
    # AND derivatives of precision-preserving expanded author FK.
    family = 'ABB' if env in ('II', 'III') else 'COMAU'
    regular = np.array([.37, .21, -.7, .48, .71, -.31])
    old = regular.copy(); old[2] = -3.1416/2
    fixtures = [('regular', regular, 6), ('original_elbow', old, 6),
                ('true_elbow', apply_mode(regular, family, 2), 5),
                ('wrist', apply_mode(regular, family, 1), 5),
                ('true_elbow_wrist', apply_mode(regular, family, 0), 'deficient')]
    requests, tags = [], []
    for arm in range(1, model_geometry(env)['arms']+1):
        for name, q, expected_rank in fixtures:
            start = len(requests)
            requests.append(('F', arm, None, q))
            for sign in (1, -1):
                for k in range(6):
                    shifted=q.copy(); shifted[k]+=sign*1e-6
                    requests.append(('F', arm, None, shifted))
            tags.append((arm, name, q, expected_rank, start))
    rr = batch(requests)
    for arm, name, q, expected, start in tags:
        center = np.array(rr[start]['T'])
        native_j = np.zeros((6, 6))
        for k in range(6):
            deriv = (np.array(rr[start+1+k]['T'])-np.array(rr[start+7+k]['T']))/2e-6
            omega = deriv[:3, :3]@center[:3, :3].T
            native_j[:3, k] = deriv[:3, 3]
            native_j[3:, k] = [omega[2,1]-omega[1,2], omega[0,2]-omega[2,0],
                               omega[1,0]-omega[0,1]]
            native_j[3:, k] /= 2
        analytic = arm_fk_jac(q, env, arm)[1]
        ranks, sigmas = [], []
        for j in (analytic, native_j):
            scaled = j.copy(); scaled[:3] /= 1000
            s = np.linalg.svd(scaled, compute_uv=False)
            ranks.append(int(np.sum(s > s[0]*1e-6))); sigmas.append(s.tolist())
        # The intersection of two determinant-zero sets need not lose two
        # independent ranks. Certify singularity, never infer corank from
        # the number of fixed singular-mode coordinates.
        valid = (all(r < 6 for r in ranks) if expected == 'deficient'
                 else all(r == expected for r in ranks))
        check(f'rank_{arm}_{name}', valid, {'ranks': ranks, 'expected': expected, 'sigmas': sigmas})
        observe('rank_fixture', arm=arm, name=name, q=q.tolist(), analytic=analytic.tolist(),
                native_fd=native_j.tolist(), ranks=ranks, singular_values=sigmas)
    # Primary original near-endpoint inputs remain an explicit independent set.
    # Source limit rejection is preserved separately from solver convergence.
    nr_results = []
    for idx, q in nr:
        result = project_nr(q, env, wall_limit_s=budget.remaining())
        nr_results.append(('original_input', str(idx), result))
    # Construct two additional known-closed component fixtures from unchanged
    # source active arm values. These are NEVER formal start/goal replacements.
    for name, q in endpoints:
        q = np.array(q); requests = []
        t1 = arm_fk_jac(q[:6], env, 1)[0]
        for arm, grasp in enumerate(model_geometry(env)['grasps'], 2):
            target = t1@grasp@np.diag([-1., -1., 1., 1.])
            requests.extend(('K', arm, b, target) for b in range(8))
        rr = batch(requests); candidates = []
        for arm in range(2, model_geometry(env)['arms']+1):
            choices = [r for r in rr[8*(arm-2):8*(arm-1)] if r['success']]
            if not choices: break
            candidates.append(choices[0]['solution'])
        built = len(candidates) == model_geometry(env)['arms']-1
        check('known_closed_fixture_constructed_'+name, built, {'endpoint': name})
        if not built: continue
        q_closed = np.r_[q[:6], np.array(candidates).ravel()]
        observe('additional_component_fixture_only', endpoint=name,
                original_q=q.tolist(), q=q_closed.tolist(), delta_q=(q_closed-q).tolist(),
                raw_branch_attempts=rr, formal_endpoint_replaced=False)
        for k in range(11):
            shifted = q_closed.copy()
            if k: shifted[(k-1)//2] += .01 if k%2 else -.01
            result = project_nr(shifted, env, wall_limit_s=budget.remaining())
            nr_results.append(('known_closed_neighborhood', name+'_'+str(k), result))
    # Cross-check reference NR candidates using native expanded FK, not the
    # same elementary transforms that computed the NR updates.
    requests, tags = [], []
    for kind, idx, result in nr_results:
        observe('nr_reference', fixture_kind=kind, fixture=idx, result=result)
        if result['candidate_q_rad'] is None:
            check('NR_finite_'+kind+'_'+idx, False, result['status']); continue
        start = len(requests)
        for arm in range(1, model_geometry(env)['arms']+1):
            requests.append(('F', arm, None, result['candidate_q_rad'][6*(arm-1):6*arm]))
        tags.append((kind, idx, result, start))
    rr = batch(requests)
    for kind, idx, result, start in tags:
        poses = [np.array(rr[start+i]['T']) for i in range(model_geometry(env)['arms'])]
        errors = [error_transform(poses[i+1], poses[0]@grasp@np.diag([-1.,-1.,1.,1.]))
                  for i, grasp in enumerate(model_geometry(env)['grasps'])]
        valid = all(check_error(e) for e in errors)
        check('NR_sound_'+kind+'_'+idx, result['status'] != 'CONVERGED' or valid,
              {'status': result['status'], 'native_fk_errors': errors})
        if kind == 'known_closed_neighborhood':
            check('NR_positive_'+idx, result['status'] == 'CONVERGED' and valid, result['status'])
        observe('nr_native_fk_crosscheck', fixture_kind=kind, fixture=idx,
                status=result['status'], independent_native_errors=errors,
                source_limits_legal=bool(np.all((source_limits(env)[:,0] <= result['candidate_q_rad']) &
                                                    (result['candidate_q_rad'] <= source_limits(env)[:,1]))))
    dump_new(folder/'observations.json', observations)
    dump_new(folder/'checks.json', checks)
    summary = {'environment': env, 'checks': len(checks), 'passed': sum(c['passed'] for c in checks),
               'failed': sum(not c['passed'] for c in checks),
               'nr_status_counts': dict(Counter(r['status'] for _, _, r in nr_results)),
               'original_input_sha256': sha(rawpath), 'formal_planning_calls': 0,
               'collision_checked': False}
    dump_new(folder/'summary.json', summary)
    return summary


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run-id', required=True)
    ap.add_argument('--targets', nargs='+', choices=['I','II','III','IV','V','VI'], required=True)
    args=ap.parse_args()
    protocol=json.loads(PROTOCOL.read_text()); budget=Budget(protocol)
    out=ROOT/'results/p4_full'/args.run_id; out.mkdir(exist_ok=False, parents=True)
    build=ROOT/'build/p4_full'/args.run_id; build.mkdir(exist_ok=False, parents=True)
    record={'run_id':args.run_id,'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'git_status_at_start':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),
            'protocol_sha256':sha(PROTOCOL),'stages':[],'formal_planning_calls':0,
            'source_files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(Path(__file__).parent.glob('*')) if p.is_file()}}
    staged={}
    try:
        for env in args.targets:
            budget.remaining()
            if env == 'I':
                from baselines.p4_full.geometry_consistent.qualify_planar import run_planar_suite
                record['stages'].append(run_planar_suite(ROOT,out,protocol)); continue
            model, dirname, macro=SPECS[env]
            if model not in staged:
                stage=stage_spatial_ik(model,SOURCE_ROOT/dirname,build/dirname)
                src=Path(stage['stage_root']); binary=build/(model+'_batch')
                cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-I'+str(src/'proj_classes'),
                     '-DP4_MODEL='+str(macro),str(Path(__file__).parent/'spatial_batch_driver.cpp'),
                     str(src/'proj_classes/apc_class.cpp'),'-o',str(binary)]
                start=time.monotonic()
                with (out/(model+'_build.log')).open('x') as log:
                    proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT,timeout=budget.remaining())
                stage.update(build_command=cmd,build_wall_s=time.monotonic()-start,exit_code=proc.returncode)
                dump_new(out/(model+'_staging.json'),stage)
                if proc.returncode: raise RuntimeError('BUILD_FAILED_'+model)
                staged[model]=binary
            summary=run_spatial(env,out,staged[model],budget,protocol)
            record['stages'].append(summary)
            print(json.dumps(summary),flush=True)
        record['status']='COMPONENT_EVIDENCE_RECORDED'
    except Exception as e:
        record['status']='STOP'; record['error']=repr(e); raise
    finally:
        record['wall_s']=time.monotonic()-budget.started
        record['cpu_s']=budget.cpu()-budget.cpu_start
        record['ended_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        dump_new(out/'execution.json',record)


if __name__ == '__main__': main()
