"""Centralised QP inverse kinematics, Eq.(17a-d) with bounds Eq.(18).

    argmin  1/2 qdot^T W qdot
    s.t.    J(q) qdot = xi^R                     (Eq.17b)
            theta_dot^- <= qdot <= theta_dot^+    (Eq.17c)
            -gradGamma_i^T qdot <= log(Gamma_i - 1)  for each SCA row i  (Eq.17d)

The official backend (CVXGEN-generated C) is not in the repository, so four
solution paths are implemented here:

    active_set  exact enumeration of the box-active sets (reference solver)
    analytic    weighted minimum-norm solution (equality only, full row rank)
    slsqp       scipy.optimize.minimize(method="SLSQP")
    lvi         projected LVI dynamics, see p5core.lvi

The active-set enumeration exists because the *unbounded* analytic solution is
not a valid referee once the box is active: it can violate Eq.(17c) happily.  The
convex objective has a unique minimiser, so an exact enumeration of the 3^n
box-active assignments is a legitimate independent reference -- and it is the
only referee here that owes nothing to scipy or to the LVI formulation.

Feasibility is *classified*, never papered over.  A pseudo-inverse of an
inconsistent equality system is a least-squares approximation; returning it as a
"solution" of the hard-constrained QP is exactly the defect the review asked us
to avoid (T04).
"""

import numpy as np
from scipy.optimize import minimize

OPTIMAL = "OPTIMAL"
RANK_DEFICIENT_CONSISTENT = "RANK_DEFICIENT_CONSISTENT"
EQUALITY_INFEASIBLE = "EQUALITY_INFEASIBLE"
BOUND_INFEASIBLE = "BOUND_INFEASIBLE"
ILL_CONDITIONED = "ILL_CONDITIONED"
#: equality consistent and lb<=ub, yet the box slice of the affine set is empty
INFEASIBLE = "INFEASIBLE"


# --------------------------------------------------------------- Eq.(18)
def velocity_bounds(q, q_min, q_max, qdot_min, qdot_max, mu=20.0, eta=None):
    """Eq.(18).  `eta` reproduces the official shrink factor (CODE_MODIFIED)."""
    q = np.asarray(q, float)
    lo = np.maximum(mu * (np.asarray(q_min, float) - q), np.asarray(qdot_min, float))
    hi = np.minimum(mu * (np.asarray(q_max, float) - q), np.asarray(qdot_max, float))
    if eta is not None:
        lo = np.maximum(mu * (eta * np.asarray(q_min, float) - q), np.asarray(qdot_min, float))
        hi = np.minimum(mu * (eta * np.asarray(q_max, float) - q), np.asarray(qdot_max, float))
    return lo, hi


# ------------------------------------------------------- problem assembly
class QP:
    """A box-constrained QP with equality and (optional) linear inequality rows."""

    def __init__(self, W, J, xidot, lb, ub, sca_rows=None, lam=1.0):
        self.W = np.asarray(W, float)
        self.J = np.asarray(J, float)
        self.xidot = np.asarray(xidot, float).ravel()
        self.lb = np.asarray(lb, float).ravel()
        self.ub = np.asarray(ub, float).ravel()
        self.sca_rows = list(sca_rows or [])      # [(g_vec, rhs_const)]
        self.d_q = self.W.shape[0]
        self.d_n = self.J.shape[0]
        self.d_c = len(self.sca_rows)
        #: Eq.(17d) weight lambda.  It scales every SCA right-hand side, so both
        #: paths (the LVI assembly in `M_b` and the exact active-set enumeration)
        #: must read the same value -- see the note in `_enumerate`.
        self.lam = float(lam)

    # ------------------------------------------------------------ assembly
    def M_b(self, lam=None):
        """Eq.(21a)/(21b) with the KKT-consistent sign b3 = +lam*log(Gamma-1)."""
        lam = self.lam if lam is None else lam
        d_q, d_n, d_c = self.d_q, self.d_n, self.d_c
        M = np.zeros((d_q + d_n + d_c, d_q + d_n + d_c))
        M[:d_q, :d_q] = self.W
        M[:d_q, d_q:d_q + d_n] = -self.J.T
        M[d_q:d_q + d_n, :d_q] = self.J
        b = np.zeros(d_q + d_n + d_c)
        b[d_q:d_q + d_n] = -self.xidot
        for i, (g, rhs) in enumerate(self.sca_rows):
            g = np.asarray(g, float).ravel()
            M[:d_q, d_q + d_n + i] = -g
            M[d_q + d_n + i, :d_q] = g
            b[d_q + d_n + i] = lam * rhs
        return M, b

    def omega(self):
        u_lo = np.concatenate([self.lb, np.full(self.d_n, -np.inf), np.zeros(self.d_c)])
        u_hi = np.concatenate([self.ub, np.full(self.d_n, np.inf), np.full(self.d_c, np.inf)])
        return u_lo, u_hi

    # ---------------------------------------------------------- feasibility
    def classify(self, tol_rank=1e-9, tol_eq=1e-8, check_box=True, max_enum_dof=7):
        """Six mutually exclusive outcomes.

        ``INFEASIBLE`` is the sixth state and it is not decoration: the equality
        row and the box can each be individually consistent while their
        intersection is empty, which happens routinely with Eq.(18) as soon as
        the arm sits on (or beyond) a position limit.  Neither the rank test nor
        the lb>ub test can see that, so the box-active enumeration is the only
        honest detector.  Without it ``classify`` would answer OPTIMAL and the
        caller would be handed a pinv point that violates Eq.(17c) -- exactly
        the failure the review warned about.
        """
        W = 0.5 * (self.W + self.W.T)
        if not np.allclose(self.W, self.W.T, atol=1e-12):
            return ILL_CONDITIONED, {"reason": "W not symmetric"}
        lam_min = float(np.linalg.eigvalsh(W)[0])
        if lam_min <= 0.0:
            return ILL_CONDITIONED, {"reason": "W not positive definite", "lam_min": lam_min}
        if np.any(self.lb > self.ub + 1e-12):
            return BOUND_INFEASIBLE, {"violated": int(np.sum(self.lb > self.ub + 1e-12))}
        J = self.J
        U, s, Vt = np.linalg.svd(J, full_matrices=False)
        r = int(np.sum(s > tol_rank * max(s[0], 1.0)))
        qdot_ls = np.linalg.pinv(J, rcond=tol_rank) @ self.xidot
        resid = float(np.linalg.norm(J @ qdot_ls - self.xidot))
        info = {"rank": r, "d_n": self.d_n, "eq_residual_ls": resid,
                "sigma_min": float(s[-1]), "sigma_max": float(s[0])}
        if resid > tol_eq * max(1.0, float(np.linalg.norm(self.xidot))):
            return EQUALITY_INFEASIBLE, info
        if check_box and self.d_q <= max_enum_dof:
            x, einfo = self._enumerate()
            info.update({"box_intersection_feasible": x is not None,
                         "active_sets_visited": einfo["active_sets_visited"]})
            if x is None:
                return INFEASIBLE, info
        if r < self.d_n:
            return RANK_DEFICIENT_CONSISTENT, info
        return OPTIMAL, info

    # -------------------------------------------------------------- solvers
    def solve_analytic(self):
        """W-weighted minimum-norm solution; only valid for consistent systems.

        This ignores Eq.(17c) entirely on purpose: it is the equality-only
        solution, not a feasible point of the full QP.  Callers that want a
        feasible point use :meth:`solve_active_set` or the numerical solvers.
        """
        Wi = np.linalg.inv(self.W)
        A = self.J @ Wi @ self.J.T
        qdot = Wi @ self.J.T @ np.linalg.pinv(A, rcond=1e-12) @ self.xidot
        return qdot

    def solve_active_set(self, tol=1e-9):
        """Exact solution by enumerating the 3^n box-active assignments.

        Returns ``(x, info)``; ``x`` is ``None`` when the box slice of the affine
        set is empty (status INFEASIBLE upstream) -- never a least-squares
        stand-in.
        """
        return self._enumerate(tol=tol)

    def _enumerate(self, tol=1e-9):
        """Implementation of the exact active-set enumeration.

        For each assignment the active coordinates are pinned to their bound and
        the remaining ones solve the equality-constrained KKT system.  A
        candidate is accepted only if (i) it satisfies J qdot = xidot, (ii) every
        coordinate sits inside its box, and (iii) the KKT multipliers of the
        pinned coordinates have the correct sign (gradient pushes them inward).
        The feasible candidate with the lowest objective wins.  This is the
        referee for P4.5/P4.7 -- it shares no code path with scipy or with the
        LVI projection.
        """
        n = self.d_q
        W = self.W
        lb = np.where(np.isfinite(self.lb), self.lb, -1e12)
        ub = np.where(np.isfinite(self.ub), self.ub, 1e12)
        # Reduce a redundant equality system to full row rank once.  Without
        # this the KKT matrix is singular whenever J has duplicated rows and
        # every active set would be rejected as "singular" rather than evaluated
        # (P4.6 caught exactly that).
        U, s, _ = np.linalg.svd(self.J, full_matrices=False)
        r = int(np.sum(s > 1e-9 * max(s[0], 1.0)))
        # Consistency must be decided *before* the projection: U^T xidot silently
        # throws away the component of xidot that lies outside range(J), which
        # would turn an inconsistent system into a consistent-looking one and
        # hand back a point that violates the original equality (N4.1).
        proj = U[:, :r] @ (U[:, :r].T @ self.xidot)
        incons = float(np.linalg.norm(self.xidot - proj))
        if incons > tol * max(1.0, float(np.linalg.norm(self.xidot))):
            return None, {"objective": None, "active_sets_visited": 0,
                          "equality_inconsistent": True, "residual_outside_range": incons}
        Jr = U[:, :r].T @ self.J
        xir = U[:, :r].T @ self.xidot
        J = Jr
        d_eq = r
        # SCA rows (17d): -g^T qdot <= rhs, i.e. g^T qdot >= -rhs.  They are linear,
        # so the same enumeration applies: an active row joins the equality system
        # with multiplier nu >= 0, an inactive row must satisfy the inequality.
        G_all = np.array([np.asarray(g, float).ravel() for g, _ in self.sca_rows]) \
            if self.sca_rows else np.zeros((0, n))
        # The lambda factor must be applied HERE too, not only in `M_b`: the exact
        # solver never builds M, so a lam-unaware enumeration would solve a
        # different QP than the one the LVI path describes (T08/N8.2 depends on
        # lam = 0 actually relaxing the row).
        r_all = np.array([self.lam * float(rhs) for _, rhs in self.sca_rows]) \
            if self.sca_rows else np.zeros(0)
        d_c = len(self.sca_rows)
        best = None
        best_f = np.inf
        best_mask = None
        best_nu = None
        visited = 0
        for mask in range(2 ** d_c):
            act = [i for i in range(d_c) if (mask >> i) & 1]
            A_eq = np.vstack([J, G_all[act]]) if act else J
            c_eq = np.concatenate([xir, -r_all[act]]) if act else xir
            deq = d_eq + len(act)
            for code in np.ndindex(*([3] * n)):
                # code[i]: 0 = free, 1 = at lower bound, 2 = at upper bound
                x = np.zeros(n)
                pinned = []
                for i, c in enumerate(code):
                    if c == 1:
                        x[i] = lb[i]
                        pinned.append(i)
                    elif c == 2:
                        x[i] = ub[i]
                        pinned.append(i)
                free = [i for i in range(n) if i not in pinned]
                nf = len(free)
                if nf:
                    if nf < deq:
                        visited += 1
                        continue
                    Wff = W[np.ix_(free, free)]
                    Wfp = W[np.ix_(free, pinned)] if pinned else np.zeros((nf, 0))
                    Af = A_eq[:, free]
                    rhs = c_eq - (A_eq[:, pinned] @ x[pinned] if pinned else 0.0)
                    K = np.zeros((nf + deq, nf + deq))
                    K[:nf, :nf] = Wff
                    # stationarity is Wff x_f - Af^T eta = -Wfp x_p, hence the minus sign
                    K[:nf, nf:] = -Af.T
                    K[nf:, :nf] = Af
                    b = np.concatenate([-(Wfp @ x[pinned]) if pinned else np.zeros(nf), rhs])
                    try:
                        sol = np.linalg.solve(K, b)
                    except np.linalg.LinAlgError:
                        visited += 1
                        continue
                    x[free] = sol[:nf]
                    eta = sol[nf:]
                else:
                    eta = np.linalg.lstsq(A_eq.T, W @ x, rcond=None)[0]
                visited += 1
                if not np.all(np.isfinite(x)):
                    continue
                if np.any(x < lb - 1e-9) or np.any(x > ub + 1e-9):
                    continue
                if np.linalg.norm(A_eq @ x - c_eq) > tol * max(1.0, np.linalg.norm(c_eq)):
                    continue
                grad = W @ x - A_eq.T @ eta
                ok = True
                for i, c in enumerate(code):
                    if c == 1 and grad[i] < -1e-7:
                        ok = False
                        break
                    if c == 2 and grad[i] > 1e-7:
                        ok = False
                        break
                    if c == 0 and x[i] > lb[i] + 1e-9 and x[i] < ub[i] - 1e-9 \
                            and abs(grad[i]) > 1e-7:
                        # a free coordinate strictly inside the box must be stationary
                        ok = False
                        break
                if not ok:
                    continue
                if len(act):
                    nu = eta[d_eq:]
                    if np.any(nu < -1e-7):           # dual feasibility of (17d)
                        continue
                    if np.any(G_all @ x < -r_all - 1e-7):
                        continue
                if d_c:
                    inact = [i for i in range(d_c) if i not in act]
                    if inact and np.any(G_all[inact] @ x < -r_all[inact] - 1e-7):
                        continue
                f = 0.5 * float(x @ W @ x)
                if f < best_f - 1e-15:
                    best_f = f
                    best = x.copy()
                    best_mask = mask
                    # dual multipliers of (17d) for the winning active set: T08
                    # reports nu to show the constraint was genuinely binding
                    # (nu > 0) rather than merely satisfied.
                    best_nu = (eta[d_eq:].copy() if len(act) else np.zeros(d_c))
        return best, {"objective": best_f if best is not None else None,
                      "active_sets_visited": visited,
                      "sca_active_rows": (None if best is None else
                                          [i for i in range(d_c) if (best_mask >> i) & 1]),
                      "sca_multipliers": (None if best is None else
                                          [float(v) for v in np.atleast_1d(best_nu)])}

    def solve_slsqp(self, x0=None, maxiter=300):
        d_q = self.d_q
        if x0 is None:
            x0 = np.clip(np.zeros(d_q), self.lb, self.ub)
        bounds = [(self.lb[i], self.ub[i]) for i in range(d_q)]
        cons = [{"type": "eq",
                 "fun": lambda x: self.J @ x - self.xidot,
                 "jac": lambda x: self.J}]
        for g, rhs in self.sca_rows:
            gv = np.asarray(g, float).ravel()
            cons.append({"type": "ineq",
                         "fun": _make_ineq(gv, self.lam * rhs),
                         "jac": _make_ineq_jac(gv)})
        fun = lambda x: 0.5 * float(x @ self.W @ x)
        jac = lambda x: self.W @ x
        res = minimize(fun, x0, jac=jac, bounds=bounds, constraints=cons,
                       method="SLSQP", options={"maxiter": maxiter, "ftol": 1e-14})
        return res, np.asarray(res.x, float)


def _make_ineq(g, rhs):
    # h(x) = -g^T x - rhs <= 0
    return lambda x, g=g, rhs=rhs: -float(g @ x) - rhs


def _make_ineq_jac(g):
    return lambda x, g=g: -g


def kkt_residual(qp, qdot, nu=None, mu=None):
    """Primal equality, bound and stationarity residuals for a candidate point."""
    qdot = np.asarray(qdot, float).ravel()
    mu = np.zeros(qp.d_n) if mu is None else np.asarray(mu, float).ravel()
    nu = np.zeros(qp.d_c) if nu is None else np.asarray(nu, float).ravel()
    r_eq = float(np.linalg.norm(qp.J @ qdot - qp.xidot))
    r_bnd = float(max(0.0, np.max(qp.lb - qdot), np.max(qdot - qp.ub), 0.0))
    grad = qp.W @ qdot - qp.J.T @ mu
    for i, (g, rhs) in enumerate(qp.sca_rows):
        g = np.asarray(g, float).ravel()
        grad = grad - nu[i] * g
    r_stat = float(np.linalg.norm(grad))
    r_comp = 0.0
    for i, (g, rhs) in enumerate(qp.sca_rows):
        g = np.asarray(g, float).ravel()
        slack = rhs + float(g @ qdot)          # h = -g.qdot - rhs <= 0  ->  slack = -h
        r_comp += abs(nu[i] * slack)
    return {"eq": r_eq, "bound": r_bnd, "stationarity": r_stat, "complementarity": r_comp,
            "total": max(r_eq, r_bnd, r_stat, r_comp)}
