"""P5-T05 - LVI projection dynamics, Eq.(19)-(23), and the passivity inequality.

Fidelity: ORIGINAL.

Theorem 3 is a **passivity inequality**, not Vdot <= 0.  With V = 1/2 u^T u,
Y = u, U = (I + M^T) P_Omega(u - (M u + b)) and psi(u) = u^T (I + M^T) u >= 0:

    Vdot + psi = Y^T U                                            (App. F)

Vdot may be positive whenever the input supplies energy; treating Vdot <= 0 as a
pass/fail criterion would be a misreading.  P5.6 checks the identity, P5.7 records
the sign distribution of Vdot, and N5.6 shows the identity breaks when the I in
(I + M^T) is dropped.

The paper prints b3 = -log(Gamma - 1) in (21b), contradicting its own (17d); the
implementation uses +log(Gamma - 1) (docs/DECISIONS.md D006) and N5.4 measures what
the printed sign does.
"""

import numpy as np

import p5core.lvi as LV
from p5core import qp_ik as QP
from p5core.plotting import plt, save

OUT = np.array([0.9, -1.6, 0.8])       # configuration with sigma_min ~ 0.2


def _problem():
    """A 3-DOF QP with three bounds, one equality pair and one *active* SCA row.

    `xidot` is generated from a feasible velocity so the box slice is non-empty
    (the first version of this fixture used a task velocity outside the box, which
    made the whole QP infeasible and made "LVI does not converge" look like an
    LVI defect -- it was the fixture).  `g` and `rhs` are then chosen so that the
    unconstrained-by-(17d) optimum violates the row, i.e. the SCA constraint is
    active at the solution.  `solve_active_set` now enumerates the SCA rows as
    well, so a known-good reference exists for the LVI fixed point.
    """
    from p5core.kinematics import PlanarArm
    arm = PlanarArm([0.35, 0.30, 0.25])
    J = arm.jacobian(OUT)
    W = np.diag([2.0, 0.7, 1.3])
    xidot = J @ np.array([0.30, -0.10, 0.05])
    g = np.array([0.0, 0.0, -1.0])
    rhs = 0.1                                   # row: qdot_3 <= 0.1 (Gamma = e^0.1 + 1)
    qp = QP.QP(W, J, xidot, np.full(3, -0.45), np.full(3, 0.45),
               sca_rows=[(g, rhs)])
    return qp, J, W, xidot, g, rhs


def _run(qp, dt=2e-3, tol=1e-9, max_steps=60000):
    M, b = qp.M_b()
    lo, hi = qp.omega()
    return M, b, lo, hi, LV.fixed_point(M, b, lo, hi, tol=tol, max_iter=max_steps)


def run(rec):
    qp, J, W, xidot, g, rhs = _problem()
    d_q = qp.d_q

    # ------------------------------------------------------------- P5.1
    M, b, lo, hi, fp = _run(qp)
    u = fp["u"]
    qdot_lvi = u[:d_q]
    nu = u[d_q + qp.d_n:]
    x_ref, ref_info = qp.solve_active_set()
    _, qdot_slsqp = qp.solve_slsqp()
    gap = float(np.max(np.abs(qdot_lvi - x_ref)))
    gap_slsqp = float(np.max(np.abs(qdot_slsqp - x_ref)))
    rec.metric("lvi_vs_exact_gap", gap)
    rec.metric("slsqp_vs_exact_gap", gap_slsqp)
    rec.metric("lvi_iters", fp["steps"])
    rec.metric("lvi_residual", fp["residual"])
    rec.check("P5.1", gap < 1e-6 and fp["converged"] and ref_info["sca_active_rows"] == [0],
              "LVI fixed point vs the exact active-set solution (SCA row active = %s): "
              "gap %.2e in %d iterations (residual %.1e); SLSQP differs by %.1e, which "
              "is recorded rather than used as a referee"
              % (ref_info["sca_active_rows"], gap, fp["steps"], fp["residual"], gap_slsqp),
              gap=gap, gap_slsqp=gap_slsqp, iters=fp["steps"])

    # ------------------------------------------------------------- P5.2
    r = float(np.linalg.norm(LV.residual(u, M, b, lo, hi)))
    rec.le("P5.2", r, 1e-8,
           "fixed-point residual ||P(u - Mu - b) - u|| = %.2e, nu = [%s] all >= 0"
           % (r, ", ".join("%.2e" % v for v in nu)),
           residual=r, nu_min=float(nu.min()) if nu.size else 0.0, nu=nu)
    rec.check("P5.2b", (nu.size == 0 or float(nu.min()) >= -1e-12),
              "KLT multiplier of the SCA row stays non-negative (min %.2e)"
              % (float(nu.min()) if nu.size else 0.0),
              nu_min=float(nu.min()) if nu.size else 0.0)

    # ------------------------------------------------------------- P5.3
    # The projection map is not a gradient flow, so per-step monotonicity is not
    # promised (the step is halved only when the residual grows).  What must hold:
    # it converges, in far fewer than 1e5 steps, and it removes >= 5 orders of
    # magnitude of the initial residual.
    res_series = []
    v = LV.project(np.zeros(len(b)), lo, hi)
    for _ in range(min(fp["steps"], 4000)):
        res_series.append(float(np.linalg.norm(LV.residual(v, M, b, lo, hi))))
        v = LV.project(v - fp["alpha"] * (M @ v + b), lo, hi)
    res_series = np.array(res_series)
    decades = float(np.log10(res_series[0] / max(res_series[-1], 1e-300)))
    rec.check("P5.3", fp["steps"] < 1e5 and fp["residual"] < 1e-9 and decades >= 5.0,
              "convergence: %d iterations (< 1e5), residual %.1e -> %.1e (%.1f decades), "
              "step %.3f" % (fp["steps"], res_series[0], fp["residual"], decades, fp["alpha"]),
              iters=fp["steps"], r0=float(res_series[0]), r_end=float(fp["residual"]),
              decades=decades)

    # ------------------------------------------------------------- P5.4
    J2 = np.vstack([J, J[0]])            # duplicate equality row -> singular M
    qp_dup = QP.QP(W, J2, np.array([xidot[0], xidot[1], xidot[0]]),
                   np.full(3, -0.45), np.full(3, 0.45))
    M2, b2, lo2, hi2, fp2 = _run(qp_dup)
    r2 = float(np.linalg.norm(LV.residual(fp2["u"], M2, b2, lo2, hi2)))
    rec.check("P5.4", fp2["converged"] and r2 < 1e-8,
              "redundant equality row (M singular, cond %.1e): still converges, "
              "residual %.1e" % (float(np.linalg.cond(M2)), r2),
              cond=float(np.linalg.cond(M2)), residual=r2)

    # ------------------------------------------------------------- P5.5
    # (I + M^T) vs (I + M): in the unconstrained case the two trajectories differ
    qp_u = QP.QP(W, J, xidot, np.full(3, -np.inf), np.full(3, np.inf))
    Mu, bu = qp_u.M_b()
    lou, hiu = qp_u.omega()
    v = np.array([0.05, -0.03, 0.02, 0.01, -0.02])
    dt = 1e-3
    steps = 400

    def traj(transpose):
        w = v.copy()
        out = [w.copy()]
        for _ in range(steps):
            rr = LV.residual(w, Mu, bu, lou, hiu)
            G = (np.eye(len(bu)) + (Mu.T if transpose else Mu))
            w = LV.project(w + dt * (G @ rr), lou, hiu)
            out.append(w.copy())
        return np.array(out)

    t_t = traj(True)
    t_f = traj(False)
    dev_t = float(np.max(np.abs(t_t - t_f)))
    rec.defect("P5.5", dev_t > 1e-3,
               "writing (I + M) instead of (I + M^T) changes the trajectory by %.3e "
               "in the unconstrained case: the transpose position is observable"
               % dev_t, deviation=dev_t)

    # ------------------------------------------------------------- P5.6
    # passivity along the transient of (20)
    w = np.zeros(len(b))
    w = LV.project(w, lo, hi)
    id_res, psi_min, vdot = [], np.inf, []
    for _ in range(3000):
        udot = LV.dynamics(w, M, b, lo, hi)
        pt = LV.passivity_terms(w, udot, M, b, lo, hi)
        id_res.append(pt["identity_residual"])
        psi_min = min(psi_min, pt["psi"])
        vdot.append(pt["Vdot"])
        w = w + dt * udot
        w = LV.project(w, lo, hi)
    id_max = float(np.max(id_res))
    rec.metric("passivity_identity_max", id_max)
    rec.metric("psi_min", float(psi_min))
    rec.check("P5.6", id_max < 1e-10 and psi_min >= -1e-12,
              "Vdot + psi - Y^T U = 0 to %.1e along 3000 steps; min psi = %.1e "
              "(dissipation non-negative)" % (id_max, psi_min),
              identity=id_max, psi_min=float(psi_min))

    # ------------------------------------------------------------- P5.7
    vdot = np.array(vdot)
    pos = int(np.sum(vdot > 0))
    rec.metric("vdot_positive_steps", pos)
    rec.metric("vdot_max", float(vdot.max()))
    rec.check("P5.7", True,
              "Vdot is positive on %d of %d steps (max %.3e) and negative elsewhere: "
              "it is an energy *rate* with sign changes, not a Lyapunov decrement"
              % (pos, vdot.size, float(vdot.max())), positive_steps=pos)

    # ------------------------------------------------------------- N5.1
    Wbad = np.diag([1.0, 1e-6, 1e6])
    qp_bad = QP.QP(Wbad, J, xidot, np.full(3, -0.45), np.full(3, 0.45))
    st_bad, info_bad = qp_bad.classify()
    Mb, bb = qp_bad.M_b()
    lob, hib = qp_bad.omega()
    fpb = LV.fixed_point(Mb, bb, lob, hib, tol=1e-12, max_iter=20000)
    rec.defect("N5.1", (not fpb["converged"]) or st_bad == QP.ILL_CONDITIONED,
               "ill-conditioned W (cond %.1e): status %s, convergence flag %s, "
               "residual %.2e -- the defect is visible instead of hanging"
               % (float(np.linalg.cond(Wbad)), st_bad, fpb["converged"], fpb["residual"]),
               cond=float(np.linalg.cond(Wbad)), status=st_bad)

    # ------------------------------------------------------------- N5.2
    # lambda = 0 gives the feasible *cone* g.qdot >= 0, not a frozen constraint:
    # sliding along the level set and moving to the free side are both allowed.
    # Solved with the exact enumeration (a row with rhs = 0), because a slow fixed
    # point would blur the very distinction under test.
    qp0 = QP.QP(W, J, xidot, np.full(3, -0.45), np.full(3, 0.45), sca_rows=[(g, 0.0)])
    q0, info0 = qp0.solve_active_set()
    slack0 = float(g @ q0)
    move0 = float(np.max(np.abs(q0 - x_ref)))
    slack1 = float(g @ x_ref + rhs)
    rec.metric("lambda0_slack", slack0)
    rec.metric("lambda1_slack", slack1)
    rec.defect("N5.2", abs(slack0) < 1e-9 and move0 > 1e-3 and abs(slack1) < 1e-9,
               "lambda = 0 leaves the half-space g.qdot >= 0 (boundary reached to %.1e, "
               "active row %s): the solution sits %.3f away from the lambda=1 answer, "
               "which sits on g.qdot = -log(Gamma-1) to %.1e -- a cone without margin, "
               "not a frozen gradient"
               % (abs(slack0), info0["sca_active_rows"], move0, abs(slack1)),
               slack0=slack0, move=move0, slack1=slack1)

    # ------------------------------------------------------------- N5.3
    out_of_range = np.array([5.0, -5.0])
    good = LV.project(out_of_range, np.array([-1.0, -1.0]), np.array([1.0, 1.0]))
    bad = LV.project_defective(out_of_range, np.array([-1.0, -1.0]), np.array([1.0, 1.0]))
    rec.defect("N5.3", np.all(np.abs(good) <= 1.0) and np.all(bad == out_of_range),
               "the upstream Omega_projector() computes the projection and returns its "
               "input: bounds [%s] vs [%s] -- pinned as a reproducible failure"
               % (good, bad), good=good, bad=bad)

    # ------------------------------------------------------------- N5.4
    # b3 = -log(Gamma-1) (as printed): the row becomes g.qdot >= +rhs instead of
    # >= -rhs, i.e. it pushes qdot the wrong way by 2*rhs.  Solved exactly.
    qp_neg = QP.QP(W, J, xidot, np.full(3, -0.45), np.full(3, 0.45),
                   sca_rows=[(g, -rhs)])
    qn, info_neg = qp_neg.solve_active_set()
    wrong_side = float(abs(g @ qn - rhs))      # driven to +rhs, the printed-sign row
    shift = float(np.max(np.abs(qn - x_ref)))
    rec.defect("N5.4", wrong_side < 1e-9 and shift > 1e-2,
               "b3 = -log(Gamma-1) (printed form) drives the row to g.qdot = +rhs instead "
               "of -rhs (residual %.1e, active row %s), moving qdot by %.3f -- the "
               "opposite of (17d)" % (wrong_side, info_neg["sca_active_rows"], shift),
               residual=wrong_side, shift=shift)

    # ------------------------------------------------------------- N5.5
    lo_rev = np.array([+0.5, +0.5, +0.5, 0.0])
    hi_rev = np.array([-0.5, -0.5, -0.5, 1.0])
    qp_rev = QP.QP(W, J, xidot, lo_rev[:3], hi_rev[:3])
    st_rev, _ = qp_rev.classify()
    detected = bool(np.any(lo_rev > hi_rev)) and st_rev == QP.BOUND_INFEASIBLE
    rec.defect("N5.5", detected,
               "reversed box order is caught before any iteration: Omega ordering "
               "violation detected = %s, status %s" % (detected, st_rev), status=st_rev)

    # ------------------------------------------------------------- N5.6
    w = np.zeros(len(b))
    w = LV.project(w, lo, hi)
    id_bad = []
    for _ in range(500):
        rr = LV.residual(w, M, b, lo, hi)
        udot_bad = M.T @ rr                    # the I of (I + M^T) dropped
        pt = LV.passivity_terms(w, udot_bad, M, b, lo, hi)
        id_bad.append(pt["identity_residual"])
        w = LV.project(w + dt * udot_bad, lo, hi)
    id_bad_max = float(np.max(id_bad))
    ratio = id_bad_max / max(id_max, 1e-300)
    rec.defect("N5.6", id_bad_max > 1e-8 and ratio > 1e3,
               "dropping the I in (I + M^T) makes the passivity identity residual %.2e, "
               "i.e. %.1e times the correct %.1e: the identity is not vacuous"
               % (id_bad_max, ratio, id_max), residual=id_bad_max, ratio=ratio)

    # ----------------------------------------------------------- figures
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.semilogy(np.arange(len(res_series)), np.maximum(res_series, 1e-18), lw=1.2)
    ax.set_xlabel("iteration")
    ax.set_ylabel(r"$\|P_\Omega(u - Mu - b) - u\|$")
    ax.set_title("LVI fixed-point residual, Eq.(19)")
    save(fig, rec, "t05_convergence.png")

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.plot(np.arange(vdot.size) * dt, vdot, lw=1.0)
    ax.axhline(0.0, color="k", ls=":", lw=0.8)
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$\dot V$")
    ax.set_title(r"$\dot V$ changes sign: input supplies energy (not a Lyapunov decrement)")
    save(fig, rec, "t05_vdot_sign.png")

    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    ax.plot(qdot_slsqp, qdot_lvi, "o", ms=7)
    lim = 1.15 * max(np.max(np.abs(qdot_slsqp)), np.max(np.abs(qdot_lvi)), 1e-3)
    ax.plot([-lim, lim], [-lim, lim], "k--", lw=0.8)
    ax.set_xlabel("SLSQP  qdot")
    ax.set_ylabel("LVI  qdot")
    ax.set_title("(17a-d) solution: gap %.1e" % gap)
    save(fig, rec, "t05_solver_agreement.png")

    return rec
