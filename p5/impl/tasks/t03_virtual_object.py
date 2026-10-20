"""P5-T03 - virtual-object DS, Eq.(9)-(11), and the two-segment cancellation (Q2).

Fidelity: ORIGINAL.  Both segments are derived on the paper's own equations; the
second one uses the premise the paper itself states in Appendix D Part A.

Segment A (unconditional)
    Substituting (2) into (10) gives U_i = tau_i xdot_i^V, i.e. taudot_i cancels
    identically.  No assumption is involved: P3.1 samples random states with
    taudot != 0 and requires the residual to be zero to machine precision.

Segment B (conditional)
    Feeding U_i back into (9) leaves

        (1 + sum tau) xdot^V = R + sum tau_i xdot_i^V ,  R = the object terms

    which still contains tau.  Only under the paper's premise xdot_i^V = xdot^V
    for every i does it collapse to (36), which is then tau-free.  This task
    verifies the collapse *under the premise* (P3.2, P3.6) and verifies that the
    premise is load bearing (N3.1: with per-arm offsets, scaling tau by +-50 %
    changes xdot^V).

What is deliberately *not* claimed: "(11) does not depend on tau".  In the
non-shared case tau enters through both the weight (1 + sum tau) and the sum
sum tau_i xdot_i^V.  The docstring of p5core.multiarm_ds states the same thing.
"""

import numpy as np

from p5core import multiarm_ds as MD
from p5core.plotting import plt, save
from p5core.results import require

N_ARM = 2
D = 2
DT = 1e-2
T_END = 10.0


def _system(seed=0):
    rng = np.random.default_rng(seed)
    A_v = np.array([[-1.0, 0.3], [-0.2, -0.8]])
    return {
        "A_v": A_v,
        "x_o": np.array([0.5, 0.2]),
        "xdot_o": np.array([0.05, -0.02]),
        "gamma": 0.7,
        "gammadot": -0.05,
        "taus": rng.uniform(0.2, 0.9, N_ARM),
        "deltas": np.zeros((N_ARM, D)),
    }


def _rhs(v, sysd, deltas, denom_mode="paper"):
    R = MD.vo_R(sysd["gamma"], sysd["gammadot"], sysd["x_o"], sysd["xdot_o"], v, sysd["A_v"])
    taus = sysd["taus"]
    if denom_mode == "paper":
        # the literal implicit (11), solved by fixed-point iteration: an
        # independent code path from the closed form of (9)
        return MD.vo_eq11_fixedpoint(R, taus, deltas)
    if denom_mode == "tau_squared":
        # defective variant: (1 + sum tau^2) instead of (1 + sum tau)
        return (R + (taus[:, None] * (v + deltas)).sum(axis=0)) / (1.0 + float((taus ** 2).sum()))
    if denom_mode == "eq36":
        return MD.vo_eq36(R)
    raise ValueError(denom_mode)


def _integrate(sysd, deltas=None, denom_mode="paper", t_end=T_END, dt=DT, v0=None):
    deltas = sysd["deltas"] if deltas is None else deltas
    v = np.zeros(D) if v0 is None else np.array(v0, float)
    n = int(round(t_end / dt))
    out = [v.copy()]
    for _ in range(n):
        k1 = _rhs(v, sysd, deltas, denom_mode)
        k2 = _rhs(v + dt / 2 * k1, sysd, deltas, denom_mode)
        k3 = _rhs(v + dt / 2 * k2, sysd, deltas, denom_mode)
        k4 = _rhs(v + dt * k3, sysd, deltas, denom_mode)
        v = v + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(v.copy())
    return np.array(out)


def run(rec):
    sysd = _system(0)
    tau = sysd["taus"]
    require(len(tau) == N_ARM, "expected %d arms" % N_ARM)

    # ------------------------------------------------------------- P3.1
    rng = np.random.default_rng(1)
    worst = 0.0
    for _ in range(4000):
        d = D
        x_r = rng.normal(size=d)
        x_v = rng.normal(size=d)
        x_d = rng.normal(size=d)
        xdot_v = rng.normal(size=d)
        A = rng.normal(size=(d, d)) * 0.4
        t_i = float(rng.uniform(0.0, 1.0))
        tdot = float(rng.normal())
        xdot_r = MD.robot_ds(x_r, x_v, x_d, A, t_i, tdot, xdot_v)
        U = MD.U_paper(xdot_r, x_r, x_v, x_d, A, t_i, tdot)
        worst = max(worst, float(np.max(np.abs(U - t_i * xdot_v))))
    rec.metric("identity_residual_max", worst)
    rec.le("P3.1", worst, 1e-10,
           "assertion A on 4000 random states with taudot != 0: "
           "max|U_i - tau_i xdot_i^V| = %.2e" % worst, residual=worst)

    # ------------------------------------------------------------- P3.2
    traj_11 = _integrate(sysd, denom_mode="paper")
    traj_36 = _integrate(sysd, denom_mode="eq36")
    gap = float(np.max(np.abs(traj_11 - traj_36)))
    rec.metric("traj_gap_max", gap)
    rec.le("P3.2", gap, 1e-10,
           "under xdot_i^V = xdot^V the literal (11) and (36) coincide over %.0f s: "
           "max|dx^V| = %.2e" % (T_END, gap), gap=gap)

    # ------------------------------------------------------------- P3.3
    base = _rhs(np.array([0.1, -0.2]), sysd, sysd["deltas"])
    devs = []
    for scale in (0.1, 10.0):
        # taudot only enters (10)/(2); at the virtual-object level the identity of
        # P3.1 already removed it, so the check is that the *substituted* form is
        # invariant: recompute U with a scaled taudot and compare the velocity.
        d = D
        x_r = np.array([0.3, -0.1])
        x_v = np.array([0.1, -0.2])
        x_d = np.zeros(d)
        xdot_v = np.array([0.4, 0.7])
        A = np.array([[-0.5, 0.1], [0.05, -0.6]])
        r = []
        for tdot in (0.1 * 3.7, 10.0 * 3.7):
            xdot_r = MD.robot_ds(x_r, x_v, x_d, A, 0.6, tdot, xdot_v)
            U = MD.U_paper(xdot_r, x_r, x_v, x_d, A, 0.6, tdot)
            r.append(U)
        devs.append(float(np.max(np.abs(r[0] - r[1]))))
    dev_max = max(devs)
    rec.metric("tau_dot_jacobian_max", dev_max)
    rec.le("P3.3", dev_max, 1e-12,
           "scaling taudot by 0.1x and 10x leaves U_i unchanged (%.1e), i.e. the "
           "Jacobian with respect to taudot is zero" % dev_max, dev=dev_max)

    # ------------------------------------------------------------- P3.4
    s0 = dict(sysd)
    s0["taus"] = np.zeros(N_ARM)
    g0 = float(np.max(np.abs(_integrate(s0, denom_mode="paper")
                             - _integrate(s0, denom_mode="eq36"))))
    rec.le("P3.4", g0, 1e-12,
           "tau = 0 (fully asynchronous): (11) degenerates to the object DS, "
           "identical to (36) to %.1e" % g0, gap=g0)

    # ------------------------------------------------------------- P3.5
    s1 = dict(sysd)
    s1["taus"] = np.ones(N_ARM)
    g1 = float(np.max(np.abs(_integrate(s1, denom_mode="paper")
                             - _integrate(s1, denom_mode="eq36"))))
    rec.le("P3.5", g1, 1e-12,
           "tau = 1 (fully synchronous, shared velocity): (11) equals (36) to %.1e"
           % g1, gap=g1)

    # ------------------------------------------------------------- P3.6
    dev_tau = []
    for f in (0.5, 1.5):
        sx = dict(sysd)
        sx["taus"] = sysd["taus"] * f
        dev_tau.append(float(np.max(np.abs(_integrate(sx, denom_mode="paper") - traj_11))))
    dev_tau_max = max(dev_tau)
    rec.le("P3.6", dev_tau_max, 1e-12,
           "with the shared-velocity premise, scaling tau by +-50%% leaves x^V "
           "unchanged (%.1e): tau really has dropped out" % dev_tau_max, dev=dev_tau_max)

    # ------------------------------------------------------------- N3.1
    offs = np.array([[0.25, -0.10], [-0.15, 0.20]])
    traj_off = _integrate(sysd, deltas=offs, denom_mode="paper")
    dev_off = []
    for f in (0.5, 1.5):
        sx = dict(sysd)
        sx["taus"] = sysd["taus"] * f
        dev_off.append(float(np.max(np.abs(_integrate(sx, deltas=offs, denom_mode="paper")
                                          - traj_off))))
    dev_off_min = min(dev_off)
    rec.metric("nonshared_tau_sensitivity", dev_off_min)
    rec.defect("N3.1", dev_off_min > 1e-3,
               "with per-arm offsets xdot_i^V = xdot^V + delta_i, scaling tau by +-50%% "
               "moves x^V by %.3e: the collapse is conditional, not an identity"
               % dev_off_min, shift=dev_off_min)

    # ------------------------------------------------------------- N3.2
    # replace sum tau_i xdot_i^V by the official U_sum (which is -A(.) - taudot e)
    d = D
    x_r, x_v, x_d, xdot_v = np.array([0.3, -0.1]), np.array([0.1, -0.2]), np.zeros(d), np.array([0.4, 0.7])
    A1 = np.array([[-0.5, 0.1], [0.05, -0.6]])
    t_i, tdot = 0.6, 0.3
    xdot_r = MD.robot_ds(x_r, x_v, x_d, A1, t_i, tdot, xdot_v)
    U_ref = MD.U_paper(xdot_r, x_r, x_v, x_d, A1, t_i, tdot)
    U_off = MD.U_official(x_r, x_v, x_d, A1, t_i, tdot)
    dev_official = float(np.max(np.abs(U_ref - U_off)))
    rec.metric("dev_official_gap", dev_official)
    rec.defect("N3.2", dev_official > 1e-2,
               "the upstream U_i = -A(.) - taudot e differs from tau_i xdot_i^V by "
               "%.3f: the two are not interchangeable (DEVIATION_REFERENCE only)"
               % dev_official, gap=dev_official)

    # ------------------------------------------------------------- N3.3
    def U_missing_taudot(xdot_r, x_r, x_v, x_d, A, t, tdot):
        e = x_v - x_d
        return xdot_r - A @ (x_r - x_d - t * e)      # the -taudot e term dropped

    res_bad = float(np.max(np.abs(U_missing_taudot(xdot_r, x_r, x_v, x_d, A1, t_i, tdot)
                                 - t_i * xdot_v)))
    rec.defect("N3.3", res_bad > 1e-2,
               "dropping -taudot(x^V - x^d) from (10) leaves a residual of %.3f, so "
               "P3.1 fails immediately" % res_bad, residual=res_bad)

    # ------------------------------------------------------------- N3.4
    traj_bad = _integrate(sysd, denom_mode="tau_squared")
    dev_den = float(np.max(np.abs(traj_bad - traj_11)))
    rec.defect("N3.4", dev_den > 1e-3,
               "writing the denominator as (1 + sum tau^2) moves x^V by %.3e"
               % dev_den, deviation=dev_den)

    # ------------------------------------------------------------- N3.5
    sz = dict(sysd)
    sz["taus"] = np.zeros(N_ARM)
    sz["gamma"] = 0.0
    sz["gammadot"] = 0.0
    v_test = np.array([0.3, -0.4])
    Rz = MD.vo_R(0.0, 0.0, sz["x_o"], sz["xdot_o"], v_test, sz["A_v"])
    rhs_z = _rhs(v_test, sz, sz["deltas"])
    expected = sz["A_v"] @ v_test
    dev_zero = float(np.max(np.abs(rhs_z - expected)))
    rec.defect("N3.5", dev_zero < 1e-12,
               "tau = 0 and gamma = 0: the right-hand side is exactly A^V x^V "
               "(residual %.1e), no arm term survives" % dev_zero, residual=dev_zero,
               R_norm=float(np.linalg.norm(Rz)))

    # ----------------------------------------------------------- figures
    t = np.arange(len(traj_11)) * DT
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.semilogy(t, np.maximum(np.abs(traj_11 - traj_36).max(axis=1), 1e-18),
                lw=1.2, label=r"$|(11)-(36)|$ (shared premise)")
    ax.axhline(1e-10, color="k", ls=":", lw=0.8, label="tolerance 1e-10")
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$\max_i |\Delta x^V_i|$")
    ax.set_title("identity (11) -> (36) holds only under the shared-velocity premise")
    ax.legend(fontsize=8)
    save(fig, rec, "t03_identity_residual.png")

    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for k, c in ((0, "C0"), (1, "C1")):
        ax.plot(t, traj_11[:, k], "-", color=c, lw=1.4, label="(11) component %d" % (k + 1))
        ax.plot(t, traj_36[:, k], "--", color=c, lw=1.0, label="(36) component %d" % (k + 1))
    ax.plot(t, traj_off[:, 0], ":", color="C3", lw=1.2,
            label="(11), per-arm offsets (non-shared)")
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$x^V$")
    ax.set_title("virtual-object trajectory: closed form vs literal (11)")
    ax.legend(fontsize=7, ncol=2)
    save(fig, rec, "t03_traj_overlay.png")

    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    labels = ["shared\n(paper premise)", "non-shared\n(offsets)"]
    vals = [max(dev_tau), dev_off_min]
    ax.bar(labels, vals, color=["#4b7bec", "#eb3b5a"], width=0.45)
    ax.set_yscale("log")
    for i, v in enumerate(vals):
        ax.text(i, v, "%.1e" % v, ha="center", va="bottom", fontsize=9)
    ax.set_ylabel(r"max change when $\tau$ scales $\pm50\%$")
    ax.set_title(r"$\tau$ is inert only under the shared-velocity assumption")
    save(fig, rec, "t03_tau_dot_invariance.png")

    return rec
