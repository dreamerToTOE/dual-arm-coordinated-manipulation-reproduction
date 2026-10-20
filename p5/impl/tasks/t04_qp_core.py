"""P5-T04 - centralised QP IK, Eq.(17a-c) with bounds Eq.(18).

Fidelity: ORIGINAL for the mathematics; ADAPTATION for the backend (exact
box-active-set enumeration / SLSQP / LVI fixed point replace the unreleased
CVXGEN code, which cannot change the optimal point of a strictly convex QP, only
the numerical path).

Review corrections applied here (G0, item 3):
  * A pseudo-inverse of an inconsistent equality system is a least-squares
    approximation, never a feasible point of the hard-constrained QP.  The six
    outcome states are separated and every infeasible state returns **no** qdot.
  * A soft-task (safety-prioritised) variant may be explored but is reported
    separately as ADAPTATION and is never used to make an acceptance test pass.

Two things this task had to establish the hard way, both of which are now tests:

  1. ``classify`` needs a *sixth* state.  The equality row and the box can each
     be individually consistent while their intersection is empty -- the rank
     test and the ``lb > ub`` test are both blind to that.  Without the state the
     caller is handed a pinv point that violates Eq.(17c), which is exactly what
     the review forbade (N4.7).
  2. Eq.(18) is *infeasible by construction* as soon as a joint sits outside its
     position limit, because ``theta_dot^- = mu (q^- - q) > 0`` while
     ``theta_dot^+ = min(mu (q^+ - q), qdot^+)`` may be negative.  The official
     code never checks this.  N4.2b pins the behaviour (BOUND_INFEASIBLE, no
     silent clamp).

The plan's N4.5 said "mu -> 0 removes the brake".  That is backwards: with
mu -> 0 both bounds collapse onto zero, so the joint freezes -- a *stronger*
brake.  What removes the look-ahead brake is mu -> infinity (pure velocity
clamp).  N4.5 tests that direction instead; the correction is recorded in
p5/P5_IMPLEMENTATION_PLAN.md and docs/DECISIONS.md.
"""

import time

import numpy as np

import p5core.lvi as LV
from p5core import qp_ik as QP
from p5core.kinematics import PlanarArm
from p5core.plotting import plt, save

Q0 = np.array([0.9, -1.6, 0.8])
GOAL = np.array([0.62, 0.24])


def _arm3():
    return PlanarArm([0.35, 0.30, 0.25], base=(0.0, 0.0))


def _arm4():
    return PlanarArm([0.32, 0.28, 0.22, 0.18], base=(0.0, 0.0))


def _track(arm, W, q0, goal, steps=600, dt=1e-2, gain=2.0, q_lim=2.0, qd_lim=1.5,
           mu=20.0, dt_hold=0.0):
    """Integrate the QP IK.  Returns traj, errors, sigma_min history, fail step.

    ``dt_hold`` > 0 freezes the trajectory once the joint bound would be crossed,
    used by the negative control that measures a *missing* brake.
    """
    n = arm.n
    q = np.array(q0, float)
    traj, errs, smin = [q.copy()], [], []
    fail = None
    for k in range(steps):
        p = arm.eef(q)
        J = arm.jacobian(q)
        xidot = gain * (goal - p)
        lb, ub = QP.velocity_bounds(q, np.full(n, -q_lim), np.full(n, q_lim),
                                    np.full(n, -qd_lim), np.full(n, qd_lim), mu=mu)
        qp = QP.QP(W, J, xidot, lb, ub)
        qdot, _ = qp.solve_active_set()
        if qdot is None:
            fail = k
            break
        q = q + dt * qdot
        traj.append(q.copy())
        errs.append(float(np.linalg.norm(arm.eef(q) - goal)))
        smin.append(float(np.linalg.svd(J, compute_uv=False)[-1]))
    return np.array(traj), np.array(errs), np.array(smin), fail


def _brake_shared_task(q0, q_lim, mu, steps=300, task=0.3, qd=1.5, dt=1e-2):
    """Two joints, one shared task  qdot_1 + qdot_2 = task.

    This is the only fixture in which the brake of Eq.(18) can bind *and* stay
    feasible: a pure 1-DOF task pins the coordinate, so a binding brake there
    makes the equality+bounds system infeasible instead.  With a redundant pair
    the saturated joint is held at mu(q+ - q) while the other one takes up the
    slack, which is exactly the behaviour Eq.(18) is for.
    """
    J = np.array([[1.0, 1.0]])
    W = np.eye(2)
    q = np.array(q0, float)
    qs, xs = [q.copy()], []
    for _ in range(steps):
        lb, ub = QP.velocity_bounds(q, np.full(2, -q_lim), np.full(2, q_lim),
                                    np.full(2, -qd), np.full(2, qd), mu=mu)
        qp = QP.QP(W, J, np.array([task]), lb, ub)
        x, _ = qp.solve_active_set()
        if x is None:
            return np.array(qs), None, None
        xs.append(x.copy())
        q = q + dt * x
        qs.append(q.copy())
    qs = np.array(qs)
    return qs, np.array(xs), mu * (q_lim - qs[:-1, 1])


def run(rec):
    arm = _arm3()
    n = arm.n
    W1 = np.eye(n)

    # ------------------------------------------------------------- P4.1
    J = arm.jacobian(Q0)
    Jfd = arm.jacobian_fd(Q0)
    rec.le("P4.1a", float(np.max(np.abs(J - Jfd))), 1e-8,
           "analytic Jacobian vs central differences")

    xidot = np.array([0.4, -0.25])
    qp = QP.QP(W1, J, xidot, np.full(n, -np.inf), np.full(n, np.inf))
    q_an = qp.solve_analytic()
    q_ls = np.linalg.lstsq(J, xidot, rcond=None)[0]
    rec.le("P4.1b", float(np.max(np.abs(q_an - q_ls))), 1e-12,
           "W=I analytic solution equals the least-squares minimum-norm solution")
    rec.le("P4.1c", float(np.linalg.norm(J @ q_an - xidot)), 1e-9,
           "equality residual of the analytic solution")

    # ------------------------------------------------------------- P4.2
    W = np.diag([2.0, 0.7, 1.3])
    qp2 = QP.QP(W, J, xidot, np.full(n, -np.inf), np.full(n, np.inf))
    q_w = qp2.solve_analytic()
    f_star = 0.5 * float(q_w @ W @ q_w)
    # feasible perturbation along null(J): J(q_w + t z) = xidot must still hold
    _, _, Vt = np.linalg.svd(J)
    z = Vt[-1]
    ts = np.linspace(-0.2, 0.2, 401)
    vals = [0.5 * (q_w + t * z) @ W @ (q_w + t * z) for t in ts]
    rec.check("P4.2", min(vals) >= f_star - 1e-12,
              "weighted objective is minimal along the null-space line "
              "(min %.6f vs %.6f)" % (min(vals), f_star), f_star=f_star, f_min=min(vals))

    # ------------------------------------------------------------- P4.3
    traj, errs, smin, fail = _track(arm, W1, Q0, GOAL)
    rec.metric("track_err_final", float(errs[-1]) if len(errs) else float("nan"))
    rec.check("P4.3", fail is None and len(errs) > 100 and errs[-1] < 1e-6
              and float(np.all(np.diff(errs) <= 1e-12)) and float(smin.min()) > 0.1,
              "3-link tracking: %.3e -> %.3e, monotone, min sigma %.3f, %d steps"
              % (errs[0], errs[-1], smin.min(), len(errs)),
              final=float(errs[-1]), min_sigma=float(smin.min()))

    # ------------------------------------------------------------- P4.4
    # (a) the brake binds: the redundant joint is held at mu (q+ - q) exactly
    #     while the other joint absorbs the rest of the task
    q_lim, mu = 1.0, 20.0
    qs, xs, brake = _brake_shared_task([0.0, 0.995], q_lim, mu)
    brake_err = float(np.max(np.abs(xs[:, 1] - brake)))
    rec.le("P4.4a", brake_err, 1e-12,
           "binding brake: qdot_2 equals mu(q+ - q_2) to %.1e while "
           "qdot_1 + qdot_2 = 0.3 to %.1e"
           % (brake_err, float(np.max(np.abs(xs.sum(1) - 0.3)))),
           brake_err=brake_err, qdot1=xs[0, 0], qdot2=xs[0, 1])

    # (b) the joint approaches the limit without ever crossing it
    creep = float(qs[:, 1].max() - q_lim)
    rec.metric("brake_overshoot", creep)
    rec.check("P4.4b", creep <= 1e-12 and abs(float(qs[-1, 1]) - q_lim) < 1e-6,
              "limit respected over %d steps: max q_2 = %.12f (limit %.2f), "
              "final gap %.1e" % (len(qs) - 1, qs[:, 1].max(), q_lim, q_lim - qs[-1, 1]),
              maxq=float(qs[:, 1].max()), final_gap=float(q_lim - qs[-1, 1]))

    # (c) the discrete approach rate matches the Euler prediction -ln(1 - mu dt)/dt
    gap = q_lim - qs[:-1, 1]
    tt = np.arange(len(gap)) * 1e-2
    keep = gap > 1e-12
    slope = float(np.polyfit(tt[keep], np.log(gap[keep]), 1)[0])
    pred = -np.log(1.0 - mu * 1e-2) / 1e-2
    rec.le("P4.4c", abs(-slope - pred) / pred, 0.02,
           "approach rate fitted %.3f rad/s vs Euler prediction %.3f rad/s"
           % (-slope, pred), fitted=-slope, predicted=pred)

    # (d) three-link arm driven until the saturated joint can no longer be
    #     compensated: the limit still holds and the QP reports INFEASIBLE,
    #     it does not clamp silently and does not violate the limit
    traj_arm, errs_arm, _, fail_arm = _track(arm, W1, np.array([0.9, -1.0, 0.8]),
                                             np.array([0.6, 0.5]), steps=200, gain=1.0,
                                             q_lim=q_lim)
    max_arm = float(np.max(np.abs(traj_arm)))
    rec.metric("limit_arm_maxabs", max_arm)
    rec.metric("limit_arm_fail_step", -1 if fail_arm is None else fail_arm)
    rec.check("P4.4d", max_arm <= q_lim + 1e-12 and (fail_arm is not None or errs_arm[-1] < 1e-6),
              "arm at the limit: max|q| = %.9f (limit %.2f), QP ended as %s at step %s"
              % (max_arm, q_lim, "INFEASIBLE" if fail_arm is not None else "converged",
                 fail_arm), fail_step=fail_arm, max_abs=max_arm)

    # ------------------------------------------------------------- P4.5
    # fixture with an *active* box: xi generated from a velocity sitting on the
    # bound, weights chosen so the optimum stays there
    b_act = 0.25
    x_true = np.array([0.25, -0.12, 0.06])
    xi_act = J @ x_true
    W_act = np.diag([0.4, 2.0, 1.5])
    qp3 = QP.QP(W_act, J, xi_act, np.full(n, -b_act), np.full(n, b_act))
    st3, info3 = qp3.classify()
    x_as, _ = qp3.solve_active_set()
    _, x_sl = qp3.solve_slsqp()
    M, b = qp3.M_b()
    lo, hi = qp3.omega()
    lvi = LV.fixed_point(M, b, lo, hi, tol=1e-11)
    x_lvi = lvi["u"][:n]
    gap_sl = float(np.max(np.abs(x_as - x_sl)))
    gap_lvi = float(np.max(np.abs(x_as - x_lvi)))
    active = [i for i in range(n) if abs(abs(x_as[i]) - b_act) < 1e-9]
    rec.metric("solver_gap_active_set_vs_slsqp", gap_sl)
    rec.metric("solver_gap_active_set_vs_lvi", gap_lvi)
    rec.metric("lvi_iters", lvi["steps"])
    rec.check("P4.5", st3 == QP.OPTIMAL and len(active) == 1 and gap_sl < 1e-9
              and gap_lvi < 1e-6 and lvi["converged"],
              "three solvers on an active-box fixture: |AS-SLSQP| %.2e, "
              "|AS-LVI| %.2e (%d iters), active coords %s"
              % (gap_sl, gap_lvi, lvi["steps"], active),
              gap_slsqp=gap_sl, gap_lvi=gap_lvi, active=active, status=st3)

    # ------------------------------------------------------------- P4.6
    J_rd = np.vstack([J[0], J[0], J[1]])     # 3 rows, rank 2
    xid_cons = np.array([xidot[0], xidot[0], xidot[1]])
    qp_rd = QP.QP(W1, J_rd, xid_cons, np.full(n, -np.inf), np.full(n, np.inf))
    st_rd, info_rd = qp_rd.classify()
    q_rd = qp_rd.solve_analytic()
    rec.check("P4.6", st_rd == QP.RANK_DEFICIENT_CONSISTENT
              and float(np.linalg.norm(J_rd @ q_rd - xid_cons)) < 1e-9,
              "rank-deficient but consistent -> %s, residual %.2e"
              % (st_rd, np.linalg.norm(J_rd @ q_rd - xid_cons)), status=st_rd, info=info_rd)

    # ------------------------------------------------------------- P4.7
    timing = {}
    for label, a, q0t in (("3dof", _arm3(), Q0), ("4dof", _arm4(), None)):
        nn = a.n
        qq = q0t if q0t is not None else np.array([0.6, -0.9, 0.7, 0.4])
        Jt = a.jacobian(qq)
        qt = QP.QP(np.eye(nn), Jt, np.array([0.05, -0.02]),
                   np.full(nn, -0.4), np.full(nn, 0.4))
        reps = 200 if nn == 3 else 100
        ts_ = []
        for _ in range(reps):
            t0 = time.perf_counter()
            qt.solve_active_set()
            ts_.append(time.perf_counter() - t0)
        ts_ = np.array(ts_)
        timing[label] = {"p50_ms": float(1e3 * np.percentile(ts_, 50)),
                         "p99_ms": float(1e3 * np.percentile(ts_, 99)),
                         "max_ms": float(1e3 * ts_.max()), "reps": reps,
                         "active_sets": 3 ** nn}
        rec.metric("timing_" + label, timing[label])

    t0 = time.perf_counter()
    for _ in range(10):
        qp3.solve_slsqp()
    sl_ms = 1e3 * (time.perf_counter() - t0) / 10.0
    rec.metric("slsqp_ms_per_solve_3dof", sl_ms)
    rec.check("P4.7", timing["3dof"]["p50_ms"] < 20.0 and timing["4dof"]["p50_ms"] < 60.0,
              "exact active-set solve: 3 DOF p50 %.2f ms / p99 %.2f ms (27 sets), "
              "4 DOF p50 %.2f ms (81 sets); SLSQP reference %.1f ms. Python only -- "
              "no claim is made about the paper's CVXGEN microsecond budget."
              % (timing["3dof"]["p50_ms"], timing["3dof"]["p99_ms"],
                 timing["4dof"]["p50_ms"], sl_ms), **timing)

    # ------------------------------------------------------------- N4.1
    xid_bad = np.array([xidot[0], xidot[0] + 0.5, xidot[1]])
    qp_bad = QP.QP(W1, J_rd, xid_bad, np.full(n, -np.inf), np.full(n, np.inf))
    st_bad, info_bad = qp_bad.classify()
    q_pinv = np.linalg.pinv(J_rd) @ xid_bad
    res_pinv = float(np.linalg.norm(J_rd @ q_pinv - xid_bad))
    x_bad, _ = qp_bad.solve_active_set()
    rec.defect("N4.1", st_bad == QP.EQUALITY_INFEASIBLE and res_pinv > 1e-6
               and x_bad is None,
               "inconsistent equality -> %s; the pinv point has residual %.3f and no "
               "qdot is returned" % (st_bad, res_pinv),
               status=st_bad, pinv_residual=res_pinv, returned_none=x_bad is None)

    # ------------------------------------------------------------- N4.2
    qp_bi = QP.QP(W1, J, xidot, np.full(n, 0.5), np.full(n, -0.5))
    st_bi, _ = qp_bi.classify()
    rec.defect("N4.2", st_bi == QP.BOUND_INFEASIBLE,
               "contradictory bounds -> %s" % st_bi, status=st_bi)

    # N4.2b -- the real Eq.(18) pathology: a joint deeper outside its position
    # limit than qdot_max / mu makes the two bounds contradictory, because the
    # required retreat rate exceeds the velocity limit.
    q_out = np.array([1.05, -0.2, 0.3])       # q_1 > q_1^+ = 1.0
    lb_o, ub_o = QP.velocity_bounds(q_out, np.full(n, -1.0), np.full(n, 1.0),
                                    np.full(n, -0.5), np.full(n, 0.5), mu=20.0)
    qp_o = QP.QP(W1, J, np.array([0.1, 0.1]), lb_o, ub_o)
    st_o, _ = qp_o.classify()
    rec.defect("N4.2b", st_o == QP.BOUND_INFEASIBLE and bool(lb_o[0] > ub_o[0]),
               "q outside the position limit by more than qdot_max/mu makes Eq.(18) "
               "itself infeasible (theta^- %+.3f > theta^+ %+.3f) -> %s"
               % (lb_o[0], ub_o[0], st_o),
               status=st_o, lb0=float(lb_o[0]), ub0=float(ub_o[0]))

    # ------------------------------------------------------------- N4.3
    qp_ill = QP.QP(np.zeros((n, n)), J, xidot, np.full(n, -np.inf), np.full(n, np.inf))
    st_ill, _ = qp_ill.classify()
    rec.defect("N4.3", st_ill == QP.ILL_CONDITIONED,
               "singular W -> %s" % st_ill, status=st_ill)

    # ------------------------------------------------------------- N4.4
    st_dim = None
    try:
        QP.QP(W1, J, np.array([0.1, 0.2, 0.3]), np.full(n, -np.inf),
              np.full(n, np.inf)).solve_analytic()
    except Exception as exc:
        st_dim = type(exc).__name__
    rec.defect("N4.4", st_dim is not None, "dimension mismatch raises %s" % st_dim,
               exc=st_dim)

    # ------------------------------------------------------------- N4.5
    # mu -> infinity drops the look-ahead brake: the discrete step crosses the
    # limit.  (mu -> 0 is the opposite defect -- it freezes the joint outright --
    # so it is measured in the same block and cannot be confused with a pass.)
    qs_huge, _, _ = _brake_shared_task([0.0, 0.995], q_lim, 1e6, steps=40)
    cross = float(qs_huge[:, 1].max() - q_lim)
    qs_zero, xs_zero, _ = _brake_shared_task([0.0, 0.995], q_lim, 0.0, steps=20)
    frozen = float(np.max(np.abs(qs_zero[-1] - np.array([0.0, 0.995]))))
    rec.defect("N4.5", cross > 1e-6 and frozen < 1e-12,
               "mu -> inf removes the brake (crossing by %.2e, the paper setting gives "
               "%.1e) while mu -> 0 freezes the joint (drift %.1e): mu is demonstrably "
               "load bearing" % (cross, creep, frozen), crossing=cross, drift_mu0=frozen)

    # ------------------------------------------------------------- N4.6
    from scipy.optimize import minimize
    w_soft = 1e3
    fun = lambda x: 0.5 * x @ W @ x + 0.5 * w_soft * float(np.sum((J @ x - xidot) ** 2))
    jac = lambda x: W @ x + w_soft * (J.T @ (J @ x - xidot))
    res = minimize(fun, np.zeros(n), jac=jac, method="BFGS")
    soft_res = float(np.linalg.norm(J @ res.x - xidot))
    rec.defect("N4.6", soft_res > 1e-9,
               "soft-task substitute leaves an equality residual of %.2e, so the "
               "ADAPTATION is detectable and is never used for acceptance" % soft_res,
               residual=soft_res)

    # ------------------------------------------------------------- N4.7
    # near-singular configuration + box: the intersection is empty even though
    # J has full row rank and lb < ub.  The pinv point violates Eq.(17c).
    q_sing = np.array([0.7, -0.02, 0.02])     # links nearly collinear
    J_s = arm.jacobian(q_sing)
    xi_s = np.array([0.30, 0.02])
    qp_s = QP.QP(W1, J_s, xi_s, np.full(n, -0.35), np.full(n, 0.35))
    st_s, _ = qp_s.classify()
    x_s, _ = qp_s.solve_active_set()
    x_pinvs = np.linalg.pinv(J_s) @ xi_s
    viol = float(np.max(np.maximum(np.abs(x_pinvs) - 0.35, 0.0)))
    rec.defect("N4.7", st_s == QP.INFEASIBLE and x_s is None and viol > 1e-3,
               "singular slice: status %s, no qdot returned, while the pinv point "
               "violates the box by %.3f (sigma_min %.4f)"
               % (st_s, viol, np.linalg.svd(J_s, compute_uv=False)[-1]),
               status=st_s, pinv_box_violation=viol)

    # ----------------------------------------------------------- figures
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.semilogy(errs)
    ax.set_xlabel("step [10 ms]")
    ax.set_ylabel(r"$\|p_{ee} - p_{goal}\|$ [m]")
    ax.set_title("end-effector tracking error (QP IK, Eq.17a-c)")
    save(fig, rec, "t04_tracking.png")

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.plot(np.arange(len(xs)), xs[:, 1], "-", lw=1.2, label=r"$\dot q_2$ returned")
    ax.plot(np.arange(len(xs)), brake, "--", lw=1.0, label=r"$\mu(q_2^+ - q_2)$")
    ax.axhline(1.5, color="k", ls=":", lw=0.8, label=r"$\dot q^+$")
    ax.set_xlabel("step")
    ax.set_ylabel("joint velocity [rad/s]")
    ax.set_title("Eq.(18): the position brake, not the velocity clamp, binds")
    ax.legend()
    save(fig, rec, "t04_saturation.png")

    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    ax.plot(x_sl, x_as, "o", ms=6, label="SLSQP vs active set")
    ax.plot(x_lvi, x_as, "x", ms=7, label="LVI vs active set")
    lim = 1.15 * max(np.max(np.abs(x_as)), np.max(np.abs(x_sl)), np.max(np.abs(x_lvi)))
    ax.plot([-lim, lim], [-lim, lim], "k--", lw=0.8)
    ax.set_xlabel("independent solver  qdot")
    ax.set_ylabel("active-set  qdot")
    ax.set_title("solver agreement, |AS-SLSQP| %.1e" % gap_sl)
    ax.legend(fontsize=8)
    save(fig, rec, "t04_solver_agreement.png")

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    labels = ["3 DOF\n(27 sets)", "4 DOF\n(81 sets)"]
    vals = [timing["3dof"]["p50_ms"], timing["4dof"]["p50_ms"]]
    ax.bar(labels, vals, color="#4b7bec", width=0.5)
    for i, v in enumerate(vals):
        ax.text(i, v, "%.2f ms" % v, ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("median solve time [ms]")
    ax.set_title("exact active-set solve time (Python, 1 core)")
    save(fig, rec, "t04_timing_hist.png")

    return rec
