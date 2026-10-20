"""P5-T02 - LPV scheduling Eq.(3) and a numerical sufficiency check for Eq.(5).

Fidelity: ORIGINAL (only the paper's own conditions are checked).

Review corrections applied here (G0, item 2):
  * The objective J(L) = max_k lam_max(P A_k + A_k^T P) with P = L L^T is
    homogeneous of degree two, so P -> 0 makes J -> 0 and fakes success.  The
    search therefore enforces trace(P) = 1, and a defect run *without* the
    normalisation must reproduce the fake success.
  * Failure of the search is reported as SUFFICIENT_CONDITION_NOT_CERTIFIED; it
    is never reported as "the LMI is infeasible".
"""

import numpy as np

from p5core import lpv as LP
from p5core.plotting import plt, save


def _family(P_true, K=4, seed=0):
    """A_ik = P^-1 (-Q_k/2 + S_k) so that P A + A^T P = -Q_k < 0 by construction."""
    rng = np.random.default_rng(seed)
    d = P_true.shape[0]
    Pinv = np.linalg.inv(P_true)
    A, Q = [], []
    for k in range(K):
        M = rng.standard_normal((d, d))
        S = 0.5 * (M - M.T)                      # skew
        Qk = np.diag(rng.uniform(0.8, 1.4, d))
        A.append(Pinv @ (-0.5 * Qk + S))
        Q.append(Qk)
    return A, Q


def run(rec):
    P_true = np.array([[2.0, 0.3], [0.3, 1.0]])
    A_list, Q_list = _family(P_true)
    d = 2

    # ------------------------------------------------------------- P2.1
    out = LP.common_P(A_list, normalize=True)
    P = out["P"]
    rec.metric("J_star", out["J"])
    rec.metric("lam_min_P", out["lam_min"])
    rec.metric("trace_P", out["trace_P"])
    rec.metric("certification_status", out["status"])
    # direction agreement after normalisation
    Pt = P_true / np.trace(P_true)
    cos = float(np.sum(P * Pt) / (np.linalg.norm(P) * np.linalg.norm(Pt)))
    rec.check("P2.1", out["status"] == "CERTIFIED" and out["J"] < -1e-6,
              "common P found: J*=%.3e, status=%s, direction cos=%.4f"
              % (out["J"], out["status"], cos), J=out["J"], cos=cos)

    # ------------------------------------------------------------- P2.2
    lam_min = out["lam_min"]
    rec.check("P2.2", abs(out["trace_P"] - 1.0) < 1e-9 and lam_min > 1e-9,
              "trace(P)=%.12f, lambda_min(P)=%.3e" % (out["trace_P"], lam_min),
              trace=out["trace_P"], lam_min=lam_min)

    # ------------------------------------------------------------- N2.2
    bad = LP.common_P(A_list, normalize=False)
    fro = float(np.linalg.norm(bad["P"]))
    rec.metric("unnormalized_J", bad["J"])
    rec.metric("unnormalized_fro", fro)
    # The objective is homogeneous of degree two, so without a normalisation the
    # minimiser is not well posed: it either runs P -> infinity (J -> -inf) or
    # stalls at P -> 0 with J -> 0-.  Both are degenerate and must be caught.
    degenerate = bool((not np.isfinite(bad["J"])) or fro > 1e3
                      or (bad["J"] > -1e-6 and fro < 1e-3))
    rec.defect("N2.2", degenerate,
               "unnormalised search is scaling-degenerate (|P|_F=%.2e, J=%.2e); "
               "trace(P)=1 is what makes the margin meaningful" % (fro, bad["J"]),
               fro=fro, J=bad["J"])

    # ------------------------------------------------------------- P2.3
    means = [np.array([0.0, 0.0]), np.array([1.0, 0.5]), np.array([-0.7, 0.9])]
    covs = [np.eye(2) * 0.6, np.array([[0.5, 0.1], [0.1, 0.8]]), np.eye(2) * 0.4]
    thetas = []
    ok_simplex = True
    for x in ([0.0, 0.0], [0.9, 0.6], [-0.6, 0.8], [0.2, -0.3]):
        th = LP.theta_from_gmm(x, means, covs)
        thetas.append(th)
        ok_simplex &= LP.check_simplex(th) and abs(th.sum() - 1) < 1e-12
    rec.check("P2.3", ok_simplex, "theta on the simplex for %d probe points" % len(thetas),
              thetas=thetas)

    # mixing preserves the hull
    A_mix = LP.mix_A(A_list, thetas[0])
    rec.check("P2.3b", LP.in_convex_hull(A_mix, A_list),
              "A(theta) lies in the componentwise hull of {A_ik}")

    # ------------------------------------------------------------- P2.4
    theta0 = np.array([0.5, 0.3, 0.2])
    A0 = LP.mix_A(A_list[:3], theta0)
    decay = -float(np.max(np.real(np.linalg.eigvals(A0))))
    T_end = 20.0 / max(decay, 1e-6)
    dt_int = min(1e-2, 0.05 / max(decay, 1e-6))
    t, X = LP.integrate_linear(A0, [1.0, -0.5], T=T_end, dt=dt_int)
    term = float(np.linalg.norm(X[-1]))
    rec.metric("terminal_norm", term)
    rec.metric("mix_decay_rate", decay)
    rec.metric("integration_horizon", T_end)
    rec.check("P2.4", term < 1e-6,
              "||x(T)|| = %.3e at T=%.1f s (decay rate %.2f) for a stable mix"
              % (term, T_end, decay), term=term, decay=decay)

    # ------------------------------------------------------------- P2.5
    # Eq.(4) with tau=1: x^R -> x^V for a stable A
    x_v = np.array([0.7, -0.4])
    x_r = np.array([-1.0, 1.0])
    A_stable = LP.stable_rotation(0.9, 1.2)
    dt = 1e-2
    for _ in range(3000):
        x_r = x_r + dt * A_stable @ (x_r - x_v)      # tau=1, xdot^V=0
    err = float(np.linalg.norm(x_r - x_v))
    rec.check("P2.5", err < 1e-6, "tau=1 tracking: ||x^R - x^V|| = %.3e" % err, err=err)

    # ------------------------------------------------------------- P2.6
    th_deg = LP.theta_from_gmm([0.0, 0.0], means, covs, priors=np.zeros(3))
    rec.check("P2.6", LP.check_simplex(th_deg) and np.allclose(th_deg, 1 / 3.0),
              "degenerate prior falls back to the uniform distribution", theta=th_deg)

    # ------------------------------------------------------------- N2.1
    A_unstable = [A_list[0], np.array([[0.4, 0.0], [0.0, -1.0]])]
    bad2 = LP.common_P(A_unstable, normalize=True)
    t2, X2 = LP.integrate_linear(A_unstable[1], [1.0, 0.1], T=6.0, dt=1e-2)
    diverged = float(np.linalg.norm(X2[-1])) > 10 * float(np.linalg.norm(X2[0]))
    rec.defect("N2.1", bad2["status"] == "NOT_CERTIFIED" and diverged,
               "unstable A_ik -> %s and ||x|| grows to %.2e"
               % (bad2["status"], np.linalg.norm(X2[-1])),
               status=bad2["status"], J=bad2["J"])

    # ------------------------------------------------------------- N2.3
    th_bad = np.array([0.7, 0.6, 0.2])
    rec.defect("N2.3", not LP.check_simplex(th_bad),
               "unnormalised theta (sum=%.2f) is rejected" % th_bad.sum(), sum=float(th_bad.sum()))

    # ------------------------------------------------------------- N2.4
    A_marg = [np.array([[0.0, 0.0], [0.0, -1.0]])]
    marg = LP.common_P(A_marg, normalize=True)
    rec.defect("N2.4", marg["status"] == "MARGINAL",
               "a zero eigenvalue gives J=0 and is reported MARGINAL, not CERTIFIED",
               status=marg["status"], J=marg["J"])

    # ------------------------------------------------------------- N2.5
    caught = False
    try:
        LP.common_P([np.zeros((3, 2))], normalize=True)
    except Exception:
        caught = True
    rec.defect("N2.5", caught, "inconsistent A_ik dimensions are rejected")

    # ----------------------------------------------------------- figures
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.semilogy(t, np.linalg.norm(X, axis=1))
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$\|x(t)\|$")
    ax.set_title("Eq.(3)/(4): decay of a stable LPV mix")
    save(fig, rec, "t02_convergence.png")

    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    per_k = out["per_k"]
    ax.bar(np.arange(len(per_k)), per_k)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("component k")
    ax.set_ylabel(r"$\lambda_{max}(P A_{ik} + A_{ik}^T P)$")
    ax.set_title("common P (trace=1): all components strictly negative")
    save(fig, rec, "t02_lyap_eig.png")

    fig = plt.figure(figsize=(5.0, 4.2))
    ax = fig.add_subplot(111)
    for th in thetas:
        ax.plot(th[0], th[1], "o", ms=5)
    ax.plot([0, 1, 0, 0], [0, 0, 1, 0], "k-", lw=0.8)
    ax.set_xlabel(r"$\theta_1$")
    ax.set_ylabel(r"$\theta_2$")
    ax.set_title(r"$\theta$ samples ($\theta_3 = 1-\theta_1-\theta_2$)")
    ax.set_aspect("equal")
    save(fig, rec, "t02_theta_simplex.png")

    return rec
