#!/usr/bin/env python3
"""Independent fixed P2 equation audit; no controller or dynamics simulation.

Uses scipy matrix exp/log rather than the uncommitted P2 core. The output
records a consistency dispute, not transport results or a controller ranking.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.linalg import expm, logm


def skew(x):
    a, b, c = x
    return np.array([[0, -c, b], [c, 0, -a], [-b, a, 0.]])


def hat(x):
    out = np.zeros((4, 4))
    out[:3, :3] = skew(x[3:])
    out[:3, 3] = x[:3]
    return out


def log6(T):
    a = logm(T)
    if np.max(np.abs(a.imag)) > 1e-12:
        raise ValueError('unexpected complex matrix Log')
    a = a.real
    return np.r_[a[:3, 3], a[2, 1], a[0, 2], a[1, 0]]


def adjoint(T):
    R = T[:3, :3]
    return np.block([[R, skew(T[:3, 3]) @ R], [np.zeros((3, 3)), R]])


def jr(x):
    ad = np.block([[skew(x[3:]), skew(x[:3])],
                   [np.zeros((3, 3)), skew(x[3:])]])
    a = np.zeros((12, 12))
    a[:6, :6] = -ad
    a[:6, 6:] = np.eye(6)
    return expm(a)[:6, 6:]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True)
    args = p.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError('audit output must not be overwritten')

    # Eq15: D=E^-1 O G, all initial transforms identity, EE held still,
    # object +x at 0.01 m/s, x is suppressed by sliding H=[0,I4].
    # The two signs below are counterexample/candidate, not two experiments.
    v = np.array([.01, 0, 0, 0, 0, 0])
    dt = .004
    O_next = expm(hat(v * dt))
    original = log6(O_next @ expm(hat(v * dt)))
    candidate = log6(O_next @ expm(hat(-v * dt)))

    # Eq22 necessary kinematic identity: fixed object and grasp; B=0.
    # h here is elastic hK, not a measured or projected dual-arm internal force.
    tau = np.array([.0003, -.0002, .0001, .06, -.04, .03])
    K = np.diag([5641., 5641., 4400., 1.28, 1.28, 1.28])
    KF = np.diag([.001, .001, .001, .02, .02, .02])
    D = expm(hat(tau))
    h = -K @ tau
    u = -KF @ h
    # E(t)=E(0) Exp(t*u), hence D(t)=Exp(-t*u) D(0).
    original_rate = K @ np.linalg.solve(jr(np.linalg.solve(K, h)),
                                        adjoint(np.linalg.inv(D)) @ u)
    derived_rate = K @ np.linalg.solve(jr(tau),
                                       adjoint(np.linalg.inv(D)) @ u)
    differences = []
    for eps in [1e-4, 1e-5, 1e-6]:
        fd = (-K @ log6(expm(hat(-eps * u)) @ D)
              + K @ log6(expm(hat(eps * u)) @ D)) / (2 * eps)
        differences.append({
            'epsilon_s': eps, 'finite_difference_N_s_Nm_s': fd.tolist(),
            'original_eq22_component_error': (original_rate - fd).tolist(),
            'derived_component_error': (derived_rate - fd).tolist(),
        })
    result = {
        'kind': 'MATHEMATICAL_IDENTITY_AUDIT_ONLY',
        'controller_runs': 0, 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'eq15': {'initial_D': 'I4', 'H': 'sliding: select indices 2,3,4,5',
                 'object_twist': v.tolist(), 'EE_twist': [0] * 6, 'dt_s': dt,
                 'printed_plus_sign_D_log_m_rad': original.tolist(),
                 'candidate_minus_sign_D_log_m_rad': candidate.tolist(),
                 'expected_untransmitted_deformation_m_rad': [0] * 6,
                 'verdict': 'PRINTED_EQ15_CONFLICTS_WITH_ZERO_DEFORMATION_DESCRIPTION'},
        'eq22': {'scope': 'fixed-object/fixed-grasp differentiation of elastic Eq9; not full projected Eq20 dynamics',
                 'tau_m_rad': tau.tolist(), 'K_diagonal': np.diag(K).tolist(),
                 'u_m_s_rad_s': u.tolist(), 'printed_rate': original_rate.tolist(),
                 'derived_rate': derived_rate.tolist(), 'finite_differences': differences,
                 'verdict': 'FINITE_DEFORMATION_RIGHT_JACOBIAN_ARGUMENT_DISPUTE; Eq24 local limit unaffected'},
        'interpretation': 'Do not silently repair equations. Await user decision before closed-loop implementation.'
    }
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': str(out), 'eq15_x_original_m': original[0],
                      'eq15_x_candidate_m': candidate[0],
                      'eq22_error_at_1e_6': differences[-1]['original_eq22_component_error'],
                      'derived_error_at_1e_6': differences[-1]['derived_component_error']}))


if __name__ == '__main__':
    main()
