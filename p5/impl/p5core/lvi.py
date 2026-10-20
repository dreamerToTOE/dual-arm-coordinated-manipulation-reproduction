"""LVI form of the QP and the projected dynamical system, Eq.(19)-(23).

    P_Omega(u - (M u + b)) - u = 0                    (19) fixed point
    udot = (I + M^T) ( P_Omega(u - (M u + b)) - u )   (20) dynamics
    Omega = [theta_dot^-; -inf; 0] .. [theta_dot^+; +inf; +inf]   (23)

Note the bracket: (I + M^T) * ( P(.) - u ), not (I + M^T) P(.) - u.

Theorem 3 (paper, App. F) is *not* "Vdot <= 0".  With V = 1/2 u^T u, output Y = u
and input U = (I + M^T) P_Omega(u - (M u + b)) the claim is

    Vdot + psi = Y^T U ,      psi(u) = u^T (I + M^T) u >= 0

i.e. a passivity inequality with supply rate Y^T U and dissipation psi.  For the
block structure of (21a) the cross terms cancel and psi = ||u||^2 + qdot^T W qdot,
which is non-negative for any positive definite W.  Vdot itself may be positive
whenever the input supplies energy; that is not a failure.
"""

import numpy as np


def project(u, lo, hi):
    """Eq.(22): elementwise saturation.  This is the correct projector."""
    return np.minimum(np.maximum(u, lo), hi)


def project_defective(u, lo, hi):
    """The upstream `Omega_projector()` bug: compute the projection, return the input."""
    _ = np.minimum(np.maximum(u, lo), hi)
    return u


def residual(u, M, b, lo, hi):
    return project(u - (M @ u + b), lo, hi) - u


def fixed_point(M, b, lo, hi, u0=None, alpha=None, max_iter=200000, tol=1e-10):
    """Solve (19) by the scaled projection iteration  u <- P(u - alpha (M u + b)).

    (19) and this iteration share their fixed points for every alpha > 0, so the
    scaling changes the *path*, never the answer.  It is used instead of
    integrating (20) whenever a task needs the equilibrium itself: (20) is a
    continuous dynamical system whose numerical integration converges only
    linearly and needs ~1e5 RK4 steps on the stiffness of a KKT matrix, which is
    fine for T05 (where the transient *is* the object of study) but pointless
    when we only want the solution.  The step is scaled by ||M||_2 and halved if
    the residual grows, so a badly scaled W cannot make it diverge silently.
    """
    n = M.shape[0]
    u = np.zeros(n) if u0 is None else np.array(u0, float)
    u = project(u, lo, hi)
    if alpha is None:
        alpha = 1.0 / max(1.0, float(np.linalg.norm(M, 2)))
    r = float(np.linalg.norm(residual(u, M, b, lo, hi)))
    grow = 0
    for it in range(max_iter):
        if r < tol:
            return {"u": u, "converged": True, "steps": it, "residual": r, "alpha": alpha}
        u_new = project(u - alpha * (M @ u + b), lo, hi)
        r_new = float(np.linalg.norm(residual(u_new, M, b, lo, hi)))
        if r_new > r:
            grow += 1
            if grow >= 5:
                alpha *= 0.5
                grow = 0
                continue
        else:
            grow = 0
        u, r = u_new, r_new
    return {"u": u, "converged": False, "steps": max_iter, "residual": r,
            "alpha": alpha, "reason": "max_iter"}


def dynamics(u, M, b, lo, hi):
    return (np.eye(M.shape[0]) + M.T) @ residual(u, M, b, lo, hi)


def solve(M, b, lo, hi, u0=None, dt=5e-3, max_steps=200000, tol=1e-10,
          stop_on_stall=True):
    """Integrate (20) with RK4 until the fixed-point residual is below `tol`."""
    n = M.shape[0]
    u = np.zeros(n) if u0 is None else np.array(u0, float)
    # a feasible start keeps the projection from fighting the initial condition
    u = project(u, lo, hi)
    hist = []
    r = np.linalg.norm(residual(u, M, b, lo, hi))
    for step in range(max_steps):
        hist.append((step * dt, float(r), float(np.linalg.norm(u))))
        if r < tol:
            return {"u": u, "converged": True, "steps": step, "residual": r,
                    "history": hist}
        k1 = dynamics(u, M, b, lo, hi)
        k2 = dynamics(u + dt / 2 * k1, M, b, lo, hi)
        k3 = dynamics(u + dt / 2 * k2, M, b, lo, hi)
        k4 = dynamics(u + dt * k3, M, b, lo, hi)
        u = project(u + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4), lo, hi)
        r_new = np.linalg.norm(residual(u, M, b, lo, hi))
        if stop_on_stall and r_new > 1e3 * (r + 1e-300) and step > 50:
            return {"u": u, "converged": False, "steps": step, "residual": r_new,
                    "history": hist, "reason": "diverging"}
        r = r_new
    return {"u": u, "converged": False, "steps": max_steps, "residual": r,
            "history": hist, "reason": "max_steps"}


def passivity_terms(u, udot, M, b, lo, hi):
    """Return (V, Vdot, psi, YTU) for the Theorem-3 identity.

    Y = u, U = (I + M^T) P(.), hence Y^T U = u^T (I+M^T) P(.) and
    psi = u^T (I+M^T) u.
    """
    u = np.asarray(u, float)
    udot = np.asarray(udot, float)
    P = project(u - (M @ u + b), lo, hi)
    YTU = float(u @ ((np.eye(M.shape[0]) + M.T) @ P))
    psi = float(u @ ((np.eye(M.shape[0]) + M.T) @ u))
    V = 0.5 * float(u @ u)
    Vdot = float(u @ udot)
    return {"V": V, "Vdot": Vdot, "psi": psi, "YTU": YTU,
            "identity_residual": float(abs(Vdot + psi - YTU))}
