#!/usr/bin/env python3
"""Original 66 mathematical cases plus 2 restored-preload negatives (correction 1).

Prescribed kinematics only: no object ODE, feedback controller or sensor loop.
Independent matrix exp/log oracles test the implemented finite-SE3 geometry.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

import numpy as np
import scipy
from scipy.linalg import expm, logm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from baselines.p2_pose_force import contact_geometry as g


ATOL = 1e-10
FD_ATOL = 1e-7
EPS = 1e-6
SHAPES = [np.zeros(6), np.array([.0003, -.0002, .0001, .06, -.04, .03]),
          np.array([.003, -.0025, .0015, .09, -.07, .06])]
VO = np.array([.01, -.005, .005, .12, -.10, .08])
UE = np.array([-.01, .005, -.005, -.09, .11, -.10])
MODES = ("tight", "pivot", "sliding")


def hat(x):
    a, b, c = x[3:]
    out = np.zeros((4, 4))
    out[:3, :3] = [[0, -c, b], [c, 0, -a], [-b, a, 0]]
    out[:3, 3] = x[:3]
    return out


def vee(A):
    return np.r_[A[:3, 3], A[2, 1], A[0, 2], A[1, 0]]


def exp6(x):
    return expm(hat(x))


def log6(T):
    A = logm(T)
    if np.max(np.abs(A.imag)) > ATOL:
        raise ValueError("complex Log outside oracle tolerance")
    return vee(A.real)


def ad_oracle(T):
    return np.column_stack([vee(T @ hat(x) @ np.linalg.inv(T)) for x in np.eye(6)])


def maximum(x):
    return float(np.max(np.abs(x))) if np.size(x) else 0.


def encode(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixture(tau):
    O = exp6(np.array([0, 0, 0, .3, -.2, .1]))
    O[:3, 3] = [.2, -.1, .4]
    G = exp6(np.array([0, 0, 0, .4, .2, -.3]))
    G[:3, 3] = [-.09, -.045, .01]
    E = O @ G @ exp6(-tau)
    return O, E, G


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), ROOT/'baselines/p2_pose_force/contact_geometry.py',
               ROOT/'reports/P2_CONTACT_GEOMETRY_PRE_TASK.md',
               ROOT/'reports/P2_CONTACT_GEOMETRY_CORRECTION01.md',
               ROOT/'reports/P2_CONTACT_GEOMETRY_DERIVATION.md',
               ROOT/'configs/p2_geometry_requirements.txt',
               ROOT/'configs/p2_closed_loop_protocol_v1_draft.json']
    metadata = {'kind': 'MATHEMATICAL_CONTACT_GEOMETRY_QUALIFICATION',
                'model_id': g.MODEL_ID, 'expected_cases': 68, 'closed_loop_runs': 0,
                'qualification_correction_round': 1,
                'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
                'command': sys.argv, 'interpreter': sys.executable,
                'environment': {'python': platform.python_version(),
                  'numpy': np.__version__, 'scipy': scipy.__version__},
                'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sources},
                'tolerances': {'algebra': ATOL, 'FD': FD_ATOL, 'FD_step_s': EPS,
                               'integration_free_drift': 1e-7, 'convergence_floor': 1e-12},
                'status': 'RUNNING'}
    (out/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    cases = []
    handle = (out/'cases.jsonl').open('x')

    def record(category, name, data, checks):
        row = {'case_index': len(cases), 'category': category, 'name': name,
               'data': data, 'checks': {k: bool(v) for k, v in checks.items()},
               'pass': all(bool(v) for v in checks.values())}
        handle.write(json.dumps(row, default=encode, allow_nan=False)+'\n')
        handle.flush()
        cases.append(row)

    try:
        for mode, si, motion in itertools.product(MODES, range(3), range(4)):
            O, E, G = fixture(SHAPES[si])
            H = g.selection(mode)
            if motion == 0:
                vo, u = VO, np.zeros(6)
            elif motion == 1:
                vo, u = np.zeros(6), UE
            elif motion == 2:
                vo, u = VO, UE
            else:
                s = np.array([.01, .02, -.01, .12, -.08, .1])
                vo, u = ad_oracle(np.linalg.inv(O)) @ s, ad_oracle(np.linalg.inv(E)) @ s
            r = g.grasp_rate(O, E, G, vo, u, H)
            tau_pm = []
            for t in [EPS, -EPS]:
                Ot, Et, Gt = O@exp6(t*vo), E@exp6(t*u), G@exp6(t*r.grasp_body)
                tau_pm.append(log6(np.linalg.inv(Et) @ Ot @ Gt))
            fd = (tau_pm[0]-tau_pm[1])/(2*EPS)
            free_rate = r.free_basis_EE.T @ r.tau_rate
            lift = ad_oracle(r.D) @ r.grasp_body
            h_trans = H.T @ H @ np.array([1.3, -.9, .5, .03, -.02, .01])
            power = float(h_trans @ lift)
            checks = {'module_Log_vs_independent_oracle': maximum(r.tau-log6(r.D)) <= ATOL,
                      'full_tau_dot_FD': maximum(fd-r.tau_rate) <= FD_ATOL,
                      'free_Log_rate': maximum(free_rate) <= ATOL,
                      'physical_free_lift': maximum(H@lift) <= ATOL,
                      'transmitted_wrench_free_power_W': abs(power) <= ATOL}
            if mode == 'tight':
                checks['tight_grasp_attached'] = maximum(r.grasp_body) == 0
            if motion == 3:
                checks['common_world_twist_constant_D'] = maximum(r.tau_rate) <= ATOL
                checks['common_world_twist_zero_G_rate'] = maximum(r.grasp_body) <= ATOL
            record('finite_differential', f'{mode}.shape{si}.motion{motion}',
                   {'O': O, 'E': E, 'G': G, 'V_o': vo, 'U_EE': u,
                    'tau': r.tau, 'VG': r.grasp_body, 'tau_rate': r.tau_rate,
                    'FD_tau_rate': fd, 'FD_error': fd-r.tau_rate,
                    'free_rate': free_rate, 'physical_lift': lift,
                    'free_power_W': power, 'A': r.constraint_matrix, 'A_sigma': r.singular_values}, checks)

        for variant, mode in itertools.product(('world_left', 'object_axes_rotation'), MODES):
            O, E, G = fixture(SHAPES[2])
            H = g.selection(mode)
            r = g.grasp_rate(O, E, G, VO, UE, H)
            if variant == 'world_left':
                Q = exp6(np.array([-.4, .2, .1, .2, .1, -.3]))
                rt = g.grasp_rate(Q@O, Q@E, G, VO, UE, H)
            else:
                Q = exp6(np.array([0, 0, 0, .3, .2, -.1]))
                rt = g.grasp_rate(O@Q, E, np.linalg.inv(Q)@G,
                                  ad_oracle(np.linalg.inv(Q))@VO, UE, H)
            record('coordinate_change', f'{variant}.{mode}',
                   {'Q': Q, 'D_error': rt.D-r.D, 'VG_error': rt.grasp_body-r.grasp_body,
                    'tau_rate_error': rt.tau_rate-r.tau_rate},
                   {'D_same': maximum(rt.D-r.D) <= ATOL,
                    'VG_same': maximum(rt.grasp_body-r.grasp_body) <= ATOL,
                    'tau_rate_same': maximum(rt.tau_rate-r.tau_rate) <= ATOL})

        for mode in ('pivot', 'sliding'):
            O, E, G = fixture(SHAPES[2])
            H = g.selection(mode)
            r = g.grasp_rate(O, E, G, VO, UE, H)
            if mode == 'pivot':
                N2 = -r.free_basis_EE
            else:
                c, s = np.cos(.7), np.sin(.7)
                N2 = r.free_basis_EE @ np.array([[c, -s], [s, c]])
            r2 = g.grasp_rate(O, E, G, VO, UE, H, null_basis=N2)
            record('basis_change', mode, {'N': r.free_basis_EE, 'N2': N2,
                    'VG_error': r2.grasp_body-r.grasp_body},
                   {'VG_basis_independent': maximum(r2.grasp_body-r.grasp_body) <= ATOL})

        draft = json.loads((ROOT/'configs/p2_closed_loop_protocol_v1_draft.json').read_text())
        dual = []
        for grasp in draft['model']['A_grasps']:
            T = np.eye(4)
            T[:3, :3] = np.array(grasp['R_columns_in_object']).T
            T[:3, 3] = grasp['translation_in_object_m']
            dual.append(ad_oracle(np.linalg.inv(T)).T)
        for mode1, mode2 in itertools.product(MODES, repeat=2):
            H1, H2 = g.selection(mode1), g.selection(mode2)
            W = np.hstack([dual[0]@H1.T, dual[1]@H2.T])
            P = np.eye(W.shape[1])-np.linalg.pinv(W, rcond=1e-12)@W
            h = np.linspace(-.3, .4, W.shape[1])
            V = np.array([.02, -.01, .01, .1, -.08, .05])
            expected_rank = 4 if mode1 == mode2 == 'sliding' else 6
            residual = W @ P @ h
            record('dual_H', f'{mode1}.{mode2}',
                   {'W_shape': W.shape, 'rank': np.linalg.matrix_rank(W),
                    'object_force_residual_N': residual[:3], 'object_moment_residual_Nm': residual[3:],
                    'power_check_scope': 'transpose pairing algebra; not independent physical wrench metrology',
                    'power_error_W': float((W@h)@V-h@(W.T@V))},
                   {'shape': W.shape == (6, H1.shape[0]+H2.shape[0]),
                    'rank': np.linalg.matrix_rank(W) == expected_rank,
                    'internal_null': maximum(residual) <= ATOL,
                    'orthogonal_projection': maximum(P@P-P) <= ATOL,
                    'virtual_work': abs((W@h)@V-h@(W.T@V)) <= ATOL})

        durations, dt_values = .02, [1/3000, 1/6000, 1/12000]
        for mode in MODES:
            H = g.selection(mode)
            initial_tau = H.T @ H @ SHAPES[2]
            solutions = []
            for dt in dt_values:
                O, E, G = fixture(initial_tau)
                start = g.grasp_rate(O, E, G, VO, UE, H)
                free0 = start.free_basis_EE.T @ start.tau
                drift = 0.
                steps = int(round(durations/dt))
                for _ in range(steps):
                    r0 = g.grasp_rate(O, E, G, VO, UE, H)
                    Om, Em = O@g.se3_exp(.5*dt*VO), E@g.se3_exp(.5*dt*UE)
                    Gm = G@g.se3_exp(.5*dt*r0.grasp_body)
                    rm = g.grasp_rate(Om, Em, Gm, VO, UE, H)
                    O, E, G = O@g.se3_exp(dt*VO), E@g.se3_exp(dt*UE), G@g.se3_exp(dt*rm.grasp_body)
                    tau_now = g.se3_log(g.inverse(E)@O@G)
                    drift = max(drift, maximum(start.free_basis_EE.T@tau_now-free0))
                solutions.append({'dt': dt, 'steps': steps, 'tau': tau_now,
                                  'G': G, 'drift': drift, 'free_initial': free0})
            for k, row in enumerate(solutions):
                if k < 2:
                    fine = solutions[k+1]
                    dg = log6(np.linalg.inv(row['G'])@fine['G'])
                    dtau = row['tau']-fine['tau']
                    h_error = -np.array(draft['original_parameters']['K_nominal'])*dtau
                    ratio = fine['drift']/row['drift'] if row['drift'] > 1e-12 else None
                    checks = {'free_Log_initial_preserved': row['drift'] <= FD_ATOL,
                              'refined_G_position': np.linalg.norm(dg[:3]) <= 5e-5,
                              'refined_G_rotation': np.linalg.norm(dg[3:]) <= 5e-4,
                              'synthetic_elastic_force_difference': maximum(h_error[:3]) <= .05,
                              'synthetic_elastic_moment_difference': maximum(h_error[3:]) <= .002,
                              'order_or_numerical_floor': ratio is None or ratio <= .5}
                    row.update({'half_step_difference_G_Log': dg, 'half_step_difference_tau': dtau,
                                'synthetic_Eq9_h_difference': h_error, 'free_drift_half_step_ratio': ratio,
                                'synthetic_Eq9_h_difference_definition': 'coarse_hK_minus_fine_hK = -K*(coarse_tau-fine_tau)',
                                'order_status': ('NO_FREE_DIRECTIONS' if mode == 'tight' else
                                                 'NUMERICAL_FLOOR' if ratio is None else 'REFINEMENT_CHECKED')})
                else:
                    checks = {'free_Log_initial_preserved': row['drift'] <= FD_ATOL}
                    row['order_status'] = 'NO_FREE_DIRECTIONS' if mode == 'tight' else 'FINEST_REFERENCE'
                record('finite_integration', f'{mode}.dt{k}', row, checks)

        K = np.array(draft['original_parameters']['K_nominal'])
        for old, new in [('pivot', 'sliding'), ('sliding', 'pivot')]:
            for accept in (True, False):
                tau = np.array([0, 0, .0002, .04, -.03, 0.])
                if not accept:
                    # New free directions, not only newly restored ones, require
                    # unloading. This intentionally tests the missing-release trap.
                    tau[0 if old == 'pivot' else 5] = .0003 if old == 'pivot' else .03
                D = exp6(tau)
                before = D.copy()
                guard = g.mode_switch_guard(D, old, new, -K*tau)
                record('mode_switch', f'{old}_to_{new}.{"accept" if accept else "reject"}',
                       guard, {'expected_guard': guard['eligible'] == accept,
                               'input_not_reset': np.array_equal(before, D),
                               'tau_not_zeroed': maximum(log6(D)-tau) <= ATOL})
        for old, new in [('pivot', 'sliding'), ('sliding', 'pivot')]:
            tau = np.array([0, 0, .0002, .04, -.03, 0.])
            tau[5 if old == 'pivot' else 0] = .03 if old == 'pivot' else .0003
            D = exp6(tau)
            before = D.copy()
            guard = g.mode_switch_guard(D, old, new, -K*tau)
            record('mode_switch', f'{old}_to_{new}.reject_restored',
                   {**guard, 'fixture_class': 'restored-only deliberate invalid preload',
                    'force_source': 'static synthetic Eq9 hK; hB=0, not measured loop force'},
                   {'restored_preload_rejected': not guard['eligible'],
                    'restored_dimension_detected': bool(set(guard['restored_indices']) & set(guard['strain_failures'])),
                    'input_not_reset': np.array_equal(before, D),
                    'tau_not_zeroed': maximum(log6(D)-tau) <= ATOL})
        metadata['status'] = 'PASS' if len(cases) == 68 and all(c['pass'] for c in cases) else 'FAIL'
    except Exception:
        metadata['status'] = 'ABORTED'
        (out/'termination.json').write_text(json.dumps({'traceback': traceback.format_exc()}, indent=2)+'\n')
    finally:
        handle.close()
        metadata['actual_cases'] = len(cases)
        metadata['failed_cases'] = [c['name'] for c in cases if not c['pass']]
        metadata['artifacts'] = {'cases.jsonl': sha(out/'cases.jsonl')}
        (out/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
        summary = {'status': metadata['status'], 'cases': len(cases), 'failures': metadata['failed_cases'],
                   'geometry_qualified': metadata['status'] == 'PASS', 'closed_loop_runs': 0,
                   'max_FD_error': max((maximum(c['data']['FD_error']) for c in cases
                                      if c['category']=='finite_differential'), default=None),
                   'max_free_rate': max((maximum(c['data']['free_rate']) for c in cases
                                       if c['category']=='finite_differential'), default=None),
                   'max_integration_free_drift': max((c['data']['drift'] for c in cases
                                       if c['category']=='finite_integration'), default=None)}
        (out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
        print(json.dumps(summary))
    return 0 if metadata['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
