"""Multi-arm LPV dynamics, Eq.(2), and the virtual-object DS, Eq.(9)-(11)/(36).

Eq.(2)
    xdot_i^R = taudot_i (x_i^V - x_i^d)
             + tau_i xdot_i^V
             + A_i(theta_i) ( x_i^R - x_i^d - tau_i (x_i^V - x_i^d) )

Eq.(10)
    U_i = xdot_i^R - A_i(.) ( x_i^R - x_i^d - tau_i (x_i^V - x_i^d) ) - taudot_i (x_i^V - x_i^d)

Substituting (2) into (10) gives U_i = tau_i xdot_i^V **unconditionally**
(assertion A).  Feeding that into (9)

    (1 + sum tau) xdot^V = gamma xdot^O + gammadot x^O + A^V (x^V - gamma x^O)
                           + sum tau_i xdot_i^V

still contains tau.  Only with the paper's own premise xdot_i^V = xdot^V for all i
(Appendix D Part A: "As xdot_i^V = xdot^V, forall i, (11) can be written as (36)")
does it collapse to

    xdot^V = gamma xdot^O + gammadot x^O + A^V (x^V - gamma x^O)          (36)

which is free of tau.  Both statements are implemented separately; the code never
silently applies the premise.

To probe the conditional branch we carry per-arm offsets delta_i defined by
xdot_i^V = xdot^V + delta_i.  Then (9)/(11) solve to

    xdot^V = R + sum_i tau_i delta_i ,   R = gamma xdot^O + gammadot x^O + A^V(x^V - gamma x^O)

so tau enters exactly through the offsets, and delta_i = 0 is the paper's premise.
States are abstract vectors of dimension 2*d (position block, velocity block); A
acts on the full state, as in the paper.
"""

import numpy as np


def robot_ds(x_r, x_v, x_d, A, tau, taudot, xdot_v):
    """Eq.(2)."""
    e = np.asarray(x_v, float) - np.asarray(x_d, float)
    return (taudot * e + tau * np.asarray(xdot_v, float)
            + np.asarray(A, float) @ (np.asarray(x_r, float) - np.asarray(x_d, float) - tau * e))


def U_paper(xdot_r, x_r, x_v, x_d, A, tau, taudot):
    """Eq.(10), written literally, from an independently supplied xdot_r."""
    e = np.asarray(x_v, float) - np.asarray(x_d, float)
    return (np.asarray(xdot_r, float)
            - np.asarray(A, float) @ (np.asarray(x_r, float) - np.asarray(x_d, float) - tau * e)
            - taudot * e)


def U_official(x_r, x_v, x_d, A, tau, taudot):
    """`Multiarm_ds` lines 574/584: ATX = A(.) + taudot (xV - xd);  U = -ATX.

    DEVIATION_REFERENCE.  The official code works in intercept-relative
    coordinates; that coordinate change is not reproduced, only the U_i formula,
    which is what T03 compares.
    """
    e = np.asarray(x_v, float) - np.asarray(x_d, float)
    ATX = np.asarray(A, float) @ (np.asarray(x_r, float) - np.asarray(x_d, float) - tau * e) + taudot * e
    return -ATX


def vo_R(gamma, gammadot, x_o, xdot_o, x_v, A_v):
    """Object-driven part shared by (9)/(11)/(36)."""
    x_o = np.asarray(x_o, float)
    return (gamma * np.asarray(xdot_o, float) + gammadot * x_o
            + np.asarray(A_v, float) @ (np.asarray(x_v, float) - gamma * x_o))


def vo_eq9(R, taus, deltas):
    """Eq.(9)/(11) solved: xdot^V = R + sum tau_i delta_i."""
    taus = np.asarray(taus, float).ravel()
    deltas = np.asarray(deltas, float).reshape(len(taus), -1)
    return np.asarray(R, float) + (taus[:, None] * deltas).sum(axis=0)


def vo_eq36(R):
    """Eq.(36): valid only under xdot_i^V = xdot^V for all i."""
    return np.asarray(R, float)


def gamma_dot(gamma, xi_o, xi_star, eps=1e-6):
    """Eq.(15)."""
    d = np.asarray(xi_o, float) - np.asarray(xi_star, float)
    return float((1.0 - gamma) / (np.linalg.norm(d) + eps))


def gamma_official(xi_o, xi_star):
    """`calculate_coordination_parameter()`: algebraic gamma, DEVIATION_REFERENCE."""
    d = np.linalg.norm(np.asarray(xi_o, float) - np.asarray(xi_star, float))
    return float(np.clip(np.exp(-0.1 * d * d), 0.0, 1.0))


def vo_eq11_fixedpoint(R, taus, deltas, iters=400, tol=1e-14):
    """Eq.(11) evaluated *literally*, by fixed-point iteration on the implicit form.

    (1 + sum tau) v = R + sum tau_i (v + delta_i)

    This is a different code path from `vo_eq9`, so comparing the two is a real
    check of the algebraic reduction rather than a tautology.
    """
    taus = np.asarray(taus, float).ravel()
    deltas = np.asarray(deltas, float).reshape(len(taus), -1)
    R = np.asarray(R, float)
    v = R.copy()
    denom = 1.0 + taus.sum()
    for _ in range(iters):
        v_new = (R + (taus[:, None] * (v + deltas)).sum(axis=0)) / denom
        if np.linalg.norm(v_new - v) < tol:
            return v_new
        v = v_new
    return v
