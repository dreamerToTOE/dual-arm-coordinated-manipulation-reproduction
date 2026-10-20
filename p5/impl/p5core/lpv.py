"""LPV / GMR scheduling: Eq.(3), and the numerical sufficiency check for Eq.(5).

    A_i(theta_i) = sum_k theta_ik A_ik ,  theta_ik >= 0,  sum_k theta_ik = 1
    P^R > 0, Q^R > 0, P^R A_ik + A_ik^T P^R < -Q^R

The paper states that P and Q are used only in the proofs and never computed
online.  What we can do numerically is check *sufficiency*: exhibit a single P
that satisfies the inequality for every k.  Failure to find one is **not** a
proof that the LMI is infeasible.

The search objective  J(L) = max_k lambda_max(P A_k + A_k^T P)  with P = L L^T is
homogeneous of degree two in L, so an unconstrained minimiser can drive P -> 0 and
fake success.  `common_P` therefore normalises trace(P) = 1 by default; the
unnormalised run is kept as a defect that T02 must detect.
"""

import numpy as np
import scipy.linalg as sla
from scipy.optimize import minimize


# ---------------------------------------------------------------- Eq.(3)
def mix_A(A_list, theta):
    """A(theta) = sum_k theta_k A_k."""
    theta = np.asarray(theta, float).ravel()
    return sum(float(th) * np.asarray(A, float) for th, A in zip(theta, A_list))


def theta_from_gmm(x, means, covs, priors=None):
    """Normalised component responsibilities, mirroring LPV::Calculate_Theta().

    priors * likelihood, then normalise; the degenerate branch (sum < 1e-100)
    falls back to a uniform distribution, which is what the official code does.
    """
    x = np.asarray(x, float).ravel()
    K = len(means)
    if priors is None:
        priors = np.ones(K) / K
    priors = np.asarray(priors, float).ravel()
    lik = np.empty(K)
    for k in range(K):
        mu = np.asarray(means[k], float).ravel()
        S = np.asarray(covs[k], float)
        d = x - mu
        _, logdet = np.linalg.slogdet(S)
        lik[k] = np.exp(-0.5 * (d @ np.linalg.solve(S, d)) - 0.5 * logdet)
    w = priors * lik
    s = w.sum()
    if s < 1e-100:
        return np.ones(K) / K
    return w / s


def check_simplex(theta, tol=1e-12):
    theta = np.asarray(theta, float).ravel()
    return bool(theta.min() >= 0.0 and abs(theta.sum() - 1.0) < tol)


def in_convex_hull(A, A_list, tol=1e-9):
    """True if A lies within the componentwise box spanned by A_list."""
    stack = np.array([np.asarray(a, float) for a in A_list])
    lo = stack.min(axis=0) - tol
    hi = stack.max(axis=0) + tol
    A = np.asarray(A, float)
    return bool(np.all(A >= lo) and np.all(A <= hi))


# ------------------------------------------------------- Lyapunov helpers
def lyapunov_P(A, Q=None):
    """Solve A^T P + P A = -Q for P (Q = I by default)."""
    A = np.asarray(A, float)
    if Q is None:
        Q = np.eye(A.shape[0])
    return sla.solve_lyapunov(A.T, -np.asarray(Q, float))


def lmi_margin(P, A):
    """lambda_max(P A + A^T P); negative means the strict LMI holds."""
    M = P @ A + A.T @ P
    M = 0.5 * (M + M.T)
    return float(np.linalg.eigvalsh(M)[-1])


# ------------------------------------------- common-P sufficiency search
def _J_from_L(Lflat, A_list, d, normalize):
    L = np.asarray(Lflat, float).reshape(d, d)
    P = L @ L.T
    if normalize:
        tr = np.trace(P)
        if tr <= 1e-300:
            return 1e6
        P = P / tr
    return max(lmi_margin(P, A) for A in A_list)


def common_P(A_list, normalize=True, n_restarts=6, seed=0, maxiter=4000):
    """Search for one P > 0 with P A_k + A_k^T P < 0 for all k.

    Returns dict with `P`, `J`, `lam_min`, `status`, `normalized`.
    status in {CERTIFIED, MARGINAL, NOT_CERTIFIED}.
    """
    A_list = [np.asarray(A, float) for A in A_list]
    d = A_list[0].shape[0]
    rng = np.random.default_rng(seed)
    best = None
    starts = [np.eye(d).ravel()]
    for _ in range(n_restarts):
        starts.append((np.eye(d) + 0.3 * rng.standard_normal((d, d))).ravel())
    for x0 in starts:
        res = minimize(_J_from_L, x0, args=(A_list, d, normalize),
                       method="Nelder-Mead",
                       options={"maxiter": maxiter, "xatol": 1e-10, "fatol": 1e-12})
        if best is None or res.fun < best.fun:
            best = res
    L = best.x.reshape(d, d)
    P = L @ L.T
    if normalize:
        P = P / np.trace(P)
    J = max(lmi_margin(P, A) for A in A_list)
    lam_min = float(np.linalg.eigvalsh(0.5 * (P + P.T))[0])
    if J < -1e-6 and lam_min > 1e-9:
        status = "CERTIFIED"
    elif abs(J) <= 1e-6:
        status = "MARGINAL"
    else:
        status = "NOT_CERTIFIED"
    return {"P": P, "J": J, "lam_min": lam_min, "status": status,
            "normalized": bool(normalize), "trace_P": float(np.trace(P)),
            "per_k": [lmi_margin(P, A) for A in A_list]}


# ------------------------------------------------ closed-loop integration
def integrate_linear(A, x0, T, dt):
    """Exact-free RK4 integration of xdot = A x (A constant over the horizon)."""
    A = np.asarray(A, float)
    n = int(round(T / dt))
    t = np.linspace(0.0, n * dt, n + 1)
    X = np.empty((n + 1, A.shape[0]))
    X[0] = np.asarray(x0, float)
    for i in range(n):
        x = X[i]
        k1 = A @ x
        k2 = A @ (x + dt / 2 * k1)
        k3 = A @ (x + dt / 2 * k2)
        k4 = A @ (x + dt * k3)
        X[i + 1] = x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, X


def stable_rotation(omega, decay, scale=1.0):
    """A 2x2 matrix with eigenvalues -decay +- i omega (real part negative)."""
    A = np.array([[-decay, -omega], [omega, -decay]], dtype=float)
    return scale * A
