"""Independent references for Eq.(23)-(26) stage composition and Eq.(27)-(28).

Does not import `baselines.p3_peg_in_hole`.
"""
from __future__ import annotations

import numpy as np

from . import oracle_patterns as op

# Eq.(23)-(26), transcribed independently as explicit lists.
ORACLE_COMPOSITION = {
    "approach": ("push",),
    "search": ("push", "spiral"),
    "align": ("push", "wiggle", "rub"),
    "insert": ("push",),
}


def stage_wrench(stage, t, params):
    total = np.zeros(6)
    for name in ORACLE_COMPOSITION[stage]:
        total += op.ORACLES[name](t, params[name])
    return total


def omega(R_h):
    """Eq.(28) via the complementary projector: Omega = I - n n^T, n = R_h e_x.

    Algebraically equal to R_h diag(0,1,1) R_h^T for orthonormal R_h, but derived
    by a different route (orthogonal complement of the pushing axis).
    """
    R_h = np.asarray(R_h, float)
    n = R_h @ np.array([1.0, 0.0, 0.0])
    return np.eye(3) - np.outer(n, n)


def position_selector(R_h):
    Om = omega(R_h)
    sel = np.zeros((6, 6))
    for i in range(3):
        for j in range(3):
            sel[i, j] = Om[i, j]
    for i in range(3, 6):
        sel[i, i] = 1.0
    return sel


def wrench_rotation(R_h):
    R_h = np.asarray(R_h, float)
    rot = np.zeros((6, 6))
    for i in range(3):
        for j in range(3):
            rot[i, j] = R_h[i, j]
            rot[i + 3, j + 3] = R_h[i, j]
    return rot


def torque(J, R_h, Kp, dx, w, D, qdot, tau_g, tau_f):
    """Eq.(27) written with explicit index loops."""
    J = np.asarray(J, float)
    F = position_selector(R_h) @ (np.asarray(Kp, float) @ np.asarray(dx, float))
    F = F + wrench_rotation(R_h) @ np.asarray(w, float)
    n = J.shape[1]
    tau = np.zeros(n)
    for k in range(n):
        acc = 0.0
        for i in range(6):
            acc += J[i, k] * F[i]
        for j in range(n):
            acc -= D[k, j] * qdot[j]
        acc += tau_g[k] + tau_f[k]
        tau[k] = acc
    return tau
