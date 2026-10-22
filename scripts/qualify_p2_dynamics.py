#!/usr/bin/env python3
"""Preregistered independent Eq16 mechanics gates; no controller or observer."""
import argparse
import gzip
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from scipy.spatial.transform import Rotation
from baselines.p2_pose_force.mechanics import (State, Physics, initial_state,
    physics_from_protocol, mechanics, acceleration, midpoint_step,
    validate_state, equilibrium_residual, transform)
from baselines.p2_pose_force.contact_geometry import se3_log, se3_exp, inverse, selection


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output-dir', required=True)
    args = ap.parse_args(); out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=False)
    config_path = ROOT/'configs/p2_closed_loop_protocol_v1.json'
    cfg = json.loads(config_path.read_text()); dt = cfg['clocks']['plant_tick_s']
    sources = ['baselines/p2_pose_force/mechanics.py', 'baselines/p2_pose_force/contact_geometry.py',
               'scripts/qualify_p2_dynamics.py', 'reports/P2_STAGE2_DYNAMICS_QUALIFICATION_SPEC.md']
    if sha(ROOT/cfg['contact_geometry']['source']) != cfg['contact_geometry']['source_sha256']:
        raise ValueError('FROZEN_GEOMETRY_HASH_CHANGED')
    write(out/'metadata.json', {'kind':'INDEPENDENT_DYNAMICS_QUALIFICATION_NO_CONTROL',
        'date':'2026-10-14', 'command':sys.argv, 'python':platform.python_version(),
        'numpy':np.__version__, 'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'source_sha256':{p:sha(ROOT/p) for p in sources}, 'protocol_sha256':sha(config_path),
        'corrections_used_before_run':1,'remaining_corrections':2,
        'wall_limit_s':120, 'synthetic_gate_scope':'not control trial; not paper performance evidence'})
    (out/'config_snapshot.json').write_bytes(config_path.read_bytes())
    cases = []; success = True; started = time.perf_counter()
    def record(name, passed, evidence):
        nonlocal success
        entry = {'name':name,'pass':bool(passed),'evidence':evidence}
        cases.append(entry); success = success and bool(passed)
        with (out/'cases.jsonl').open('a') as f: f.write(json.dumps(entry,allow_nan=False)+'\n')
        print(name, 'PASS' if passed else 'FAIL', flush=True)
    try:
        state = initial_state(cfg); phys = physics_from_protocol(cfg)
        # Independent classical vector wrench mapping, including lever arm.
        state.O = state.O @ se3_exp(np.array([.0003,-.0002,.0001,.04,-.03,.02]))
        for m1 in ('tight','pivot','sliding'):
            for m2 in ('tight','pivot','sliding'):
                modes = (m1,m2); U = (np.array([.001,-.002,.001,.01,-.015,.003]),np.zeros(6))
                c = mechanics(state,U,modes,phys); independent = np.zeros(6)
                for r,E in enumerate((state.E1,inverse(state.C)@state.E2)):
                    A = inverse(state.O)@E; H = selection(modes[r]); h = H.T@H@c.h[r]
                    f = A[:3,:3]@h[:3]
                    independent[:3] += f
                    independent[3:] += A[:3,:3]@h[3:] + np.cross(A[:3,3],f)
                error = c.external-independent
                proj = c.W @ (c.H @ c.internal.ravel())
                record('wrench_physical_'+m1+'_'+m2, np.max(np.abs(error))<=1e-10 and np.max(np.abs(proj))<=1e-9,
                       {'force_mapping_error_N':error[:3].tolist(),'moment_mapping_error_Nm':error[3:].tolist(),
                        'internal_force_projection_N':proj[:3].tolist(),'internal_moment_projection_Nm':proj[3:].tolist(),
                        'W_singular_values':c.singular_values.tolist()})
        # Independent zero-contact free-fall exact solution for a single tick.
        state = initial_state(cfg); gravity_phys = Physics(phys.mass,phys.inertia_diag,
            (np.zeros(6),np.zeros(6)), np.zeros(6),np.zeros(6),phys.gravity)
        new = midpoint_step(state,(np.zeros(6),np.zeros(6)),('tight','tight'),gravity_phys,dt)
        error_p = new.O[:3,3]-(state.O[:3,3]+.5*phys.gravity*dt*dt)
        error_v = new.V[:3]-phys.gravity*dt
        record('free_fall_without_contact',max(np.max(np.abs(error_p)),np.max(np.abs(error_v)))<=1e-10,
               {'position_error_m':error_p.tolist(),'velocity_error_m_s':error_v.tolist()})
        state.V = np.array([.01,-.02,.03,.2,-.3,.4]); free = Physics(phys.mass,phys.inertia_diag,
             (np.zeros(6),np.zeros(6)),np.zeros(6),np.zeros(6),np.zeros(3))
        a = acceleration(state,np.zeros(6),free)
        # Direct Newton/Euler equations independently from the block matrix.
        independent = np.r_[-np.cross(state.V[3:],state.V[:3]),
            -np.cross(state.V[3:],phys.inertia_diag*state.V[3:])/phys.inertia_diag]
        record('body_newton_euler_and_kinetic_energy',np.max(np.abs(a-independent))<=1e-10 and abs(np.dot(free.M_diag*state.V,a))<=1e-10,
               {'linear_acceleration_error_m_s2':(a-independent)[:3].tolist(),
                'angular_acceleration_error_rad_s2':(a-independent)[3:].tolist(),
                'kinetic_energy_derivative_W':float(np.dot(free.M_diag*state.V,a))})
        if not success: raise RuntimeError('ALGEBRA_GATE_FAILED')
        runs = [('transport',dt),('transport_half_step',dt/2),('high_moment',dt),('sliding',dt)]
        traces = {}
        for label,h in runs:
            variant = 'transport' if label.startswith('transport') else label
            state = initial_state(cfg,variant); phys = physics_from_protocol(cfg,'C' if variant=='sliding' else 'A')
            inputs = (np.zeros(6),np.zeros(6)); modes = ('pivot','pivot')
            duration = cfg['model']['initial_settling']['duration_s']; steps = round(duration/h)
            run_start = time.perf_counter(); rows = []
            with gzip.open(out/(label+'.jsonl.gz'),'wt') as f:
                for tick in range(steps+1):
                    if time.perf_counter()-run_start > cfg['suite']['wall_time_per_case_s']:
                        raise RuntimeError('DYNAMICS_WALL_LIMIT')
                    if tick % round(.004/h) == 0 or tick == steps:
                        c = mechanics(state,inputs,modes,phys); validate_state(state,c)
                        residual = equilibrium_residual(state,c,phys)
                        entry = {'time_s':tick*h, 'tick':tick,'state':state.as_dict(),
                            'tau':c.tau.tolist(),'hK_N_Nm':c.hK.tolist(),'hB_N_Nm':c.hB.tolist(),
                            'external_N_Nm':c.external.tolist(),'internal_N_Nm':c.internal.tolist(),
                            'force_balance_N':residual[:3].tolist(),'moment_balance_Nm':residual[3:].tolist()}
                        f.write(json.dumps(entry,allow_nan=False)+'\n'); rows.append(entry)
                    if tick < steps: state = midpoint_step(state,inputs,modes,phys,h)
            terminal = cfg['model']['initial_settling']
            passed = (np.max(np.abs(residual[:3]))<=terminal['required_terminal_force_balance_N']
                and np.max(np.abs(residual[3:]))<=terminal['required_terminal_moment_balance_Nm']
                and np.max(np.abs(state.V[:3]))<=terminal['required_linear_speed_m_s']
                and np.max(np.abs(state.V[3:]))<=terminal['required_angular_speed_rad_s'])
            record('locked_EE_five_seconds_'+label,passed,{'duration_s':duration,'dt_s':h,
                'wall_s':time.perf_counter()-run_start,'terminal_force_balance_N':residual[:3].tolist(),
                'terminal_moment_balance_Nm':residual[3:].tolist(), 'terminal_linear_speed_m_s':state.V[:3].tolist(),
                'terminal_angular_speed_rad_s':state.V[3:].tolist(),'state_from_integration':True})
            traces[label] = rows
            if not passed: raise RuntimeError('INIT_INVALID')
            if label == 'transport_half_step':
                maxdiff = np.zeros(4)
                for first,second in zip(traces['transport'],rows):
                    O1 = np.array(first['state']['O']); O2 = np.array(second['state']['O'])
                    hi = np.array(first['internal_N_Nm'])-np.array(second['internal_N_Nm'])
                    diff = [np.linalg.norm(O1[:3,3]-O2[:3,3]),np.linalg.norm(se3_log(inverse(O1)@O2)[3:]),
                            np.max(np.abs(hi[:,:3])),np.max(np.abs(hi[:,3:]))]
                    maxdiff = np.maximum(maxdiff,diff)
                lim = cfg['numerical_qualification']['half_step_max_difference']; limits = np.array([lim['position_m'],lim['orientation_rad'],lim['force_component_N'],lim['moment_component_Nm']])
                record('locked_EE_step_refinement',np.all(maxdiff<=limits),
                       dict(zip(['max_position_difference_m','max_orientation_difference_rad','max_internal_force_component_difference_N','max_internal_moment_component_difference_Nm'],maxdiff.tolist())))
                if not success: raise RuntimeError('STEP_REFINEMENT_FAILED')
    except Exception as exc:
        success = False
        write(out/'termination.json',{'reason':str(exc),'traceback':traceback.format_exc(),
              'last_integrated_state':None if 'state' not in locals() else state.as_dict(),
              'last_tick':locals().get('tick'),'dt_s':locals().get('h'),'active_qualification':locals().get('label'),
              'controller_estimator_runs':0,'no_restart_or_reset':True})
        print('STOP',str(exc),flush=True)
    summary = {'status':'PASS' if success else 'FAIL_STOP','passed':sum(c['pass'] for c in cases),
        'executed_checks':len(cases),'wall_s':time.perf_counter()-started,'closed_loop_runs':0,
        'estimator_qualified':False,'controller_qualified':False,'cases':cases}
    write(out/'summary.json',summary)
    write(out/'artifact_sha256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps({k:v for k,v in summary.items() if k!='cases'}),flush=True)
    return 0 if success else 2

if __name__=='__main__': sys.exit(main())
