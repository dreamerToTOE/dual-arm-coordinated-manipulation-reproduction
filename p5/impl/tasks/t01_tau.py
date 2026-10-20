"""P5-T01 - synchronisation allocation tau, Eq.(8), and its equilibria.

Fidelity: ORIGINAL for Eq.(8); DEVIATION_REFERENCE for the upstream variant.

Review corrections applied here (G0, item 1):
  * tau0 in {0, 1} are the **two unique equilibria** of the logistic field.  With
    finite k and finite G the solution is identically tau0; nothing is
    "non-unique".  The tests therefore check equilibrium invariance and the fact
    that leaving the endpoint requires a perturbation.
"""

import numpy as np

from p5core import tau as TA
from p5core.plotting import plt, save


def run(rec):
    T, k, tau0 = 10.0, 0.5, 1e-3
    eps_g = 1e-6

    # ---------------------------------------------------------- P1.1-P1.3
    cases = {"G>0": 0.8, "G<0": -0.8, "G=0": 0.0}
    curves = {}
    for label, G in cases.items():
        dt = 1e-3
        t, tau_num = TA.rk4(tau0, lambda _t, G=G: G, k, T, dt)
        tau_ex = TA.closed_form(tau0, G, k, t)
        err = float(np.max(np.abs(tau_num - tau_ex)))
        curves[label] = (t, tau_num, tau_ex)
        rec.metric("rel_err_%s" % label.replace(">", "gt").replace("<", "lt"), err)
    e_pos = float(np.max(np.abs(curves["G>0"][1] - curves["G>0"][2])))
    mono_pos = bool(np.all(np.diff(curves["G>0"][1]) >= -1e-15))
    rec.check("P1.1", e_pos < 1e-6 and curves["G>0"][1][-1] > 0.99 and mono_pos,
              "G>0: monotone rise to 1, closed-form error %.3e" % e_pos,
              err=e_pos, monotone=mono_pos)
    e_neg = float(np.max(np.abs(curves["G<0"][1] - curves["G<0"][2])))
    rec.check("P1.2", e_neg < 1e-6 and curves["G<0"][1][-1] < 1e-2,
              "G<0: monotone decay to 0, closed-form error %.3e" % e_neg, err=e_neg)
    e_zero = float(np.max(np.abs(curves["G=0"][1] - tau0)))
    rec.check("P1.3", e_zero < 1e-12, "G=0: tau stays at tau0", drift=e_zero)

    # ------------------------------------------------------------- P1.4
    errs = []
    dts = [1e-2, 5e-3, 2.5e-3]
    for dt in dts:
        t, tau_num = TA.rk4(tau0, lambda _t: 0.8, k, T, dt)
        errs.append(float(np.max(np.abs(tau_num - TA.closed_form(tau0, 0.8, k, t)))))
    orders = [float(np.log2(errs[i] / errs[i + 1])) for i in range(len(errs) - 1)]
    rec.metric("rk4_orders", orders)
    rec.check("P1.4", all(3.7 <= o <= 4.3 for o in orders),
              "RK4 observed order %s on dt in %s" % (orders, dts), orders=orders)

    # ------------------------------------------------------------- P1.6
    drift = []
    for end in (0.0, 1.0):
        t, tau_num = TA.rk4(end, lambda _t: 0.8, k, T, 1e-3)
        drift.append(float(np.max(np.abs(tau_num - end))))
    rec.check("P1.6", max(drift) < 1e-12,
              "tau0 in {0,1} are equilibria: max drift %.3e" % max(drift), drift=drift)

    # ------------------------------------------------------------- N1.1
    t, tau_num = TA.rk4(1.0, lambda _t: 0.8, k, T, 1e-3)
    stuck = float(np.max(np.abs(tau_num - 1.0)))
    t, tau_num = TA.rk4(1.0 - 1e-3, lambda _t: 0.8, k, T, 1e-3)
    moves = float(np.max(np.abs(tau_num - 1.0)))
    rec.defect("N1.1", stuck < 1e-12 and moves > 1e-4,
               "endpoint is invariant (%.2e) yet a 1e-3 perturbation escapes (%.2e)"
               % (stuck, moves), stuck=stuck, moves=moves)

    # ------------------------------------------------------------- N1.2
    with np.errstate(over="ignore", invalid="ignore"):
        t, tau_num = TA.rk4(1e-3, lambda _t: 1.0, 1e-4, T, 1e-2)
    violates = bool(np.any(tau_num < -1e-9) or np.any(tau_num > 1 + 1e-9)
                    or not np.all(np.isfinite(tau_num)))
    rec.defect("N1.2", violates,
               "k->0 with a fixed step breaks the (0,1) invariant, as it must",
               tau_min=float(np.min(tau_num)), tau_max=float(np.max(tau_num)))

    # ------------------------------------------------------------- N1.3
    t, tau_num = TA.rk4(tau0, lambda _t: 1e4, k, T, 1e-2)
    dev = float(np.max(np.abs(tau_num - TA.closed_form(tau0, 1e4, k, t))))
    rec.defect("N1.3", dev > 1e-3,
               "|G| ~ 1e4 with dt=1e-2 is resolved badly (dev %.3e)" % dev, dev=dev)

    # ------------------------------------------------------------- N1.4
    def rk4_reversed(tau0_, G, k_, T_, dt):
        n = int(round(T_ / dt))
        tau_ = np.empty(n + 1)
        tau_[0] = tau0_
        for i in range(n):
            # defect: k moved to the numerator
            tau_[i + 1] = tau_[i] + dt * tau_[i] * (1 - tau_[i]) * G * k_
        return np.linspace(0, n * dt, n + 1), tau_

    t2, tau_bad = rk4_reversed(tau0, 0.8, k, T, 1e-3)
    dev_bad = float(np.max(np.abs(tau_bad - curves["G>0"][2])))
    rec.defect("N1.4", dev_bad > 1e-2,
               "k in the numerator changes the transient (dev %.3e)" % dev_bad, dev=dev_bad)

    # ------------------------------------------------------------- N1.5
    t3, tau_wrong = TA.rk4(tau0, lambda _t: -0.8, k, T, 1e-3)
    dev_wrong = float(np.max(np.abs(tau_wrong - curves["G>0"][2])))
    rec.defect("N1.5", dev_wrong > 1e-3,
               "flipping the sign of G is detected (dev %.3e)" % dev_wrong, dev=dev_wrong)

    # ------------------------------------------------------------- P1.5
    # same approach geometry for Eq.(8) and the official variant
    dt = 1e-3
    t = np.arange(0, T + dt / 2, dt)
    xi0 = np.array([1.0, 1.0])
    v_o = np.array([-0.3, -0.2])
    xi_star = np.zeros(2)
    tau_p = np.empty_like(t)
    tau_p[0] = tau0
    tau_off = np.empty_like(t)
    tau_off[0] = tau0
    for i in range(len(t) - 1):
        xi = xi0 + v_o * t[i]
        G = TA.G_of(xi, v_o, xi_star, eps_g)
        tau_p[i + 1] = tau_p[i] + dt * TA.tau_dot(tau_p[i], G, k)
        dtau, nxt = TA.official_tau_dot(tau_off[i], xi, v_o, xi * 0.5)
        tau_off[i + 1] = nxt
    rms = float(np.sqrt(np.mean((tau_off - tau_p) ** 2)))
    rec.metric("rms_dev_official", rms)
    rec.metric("tau_paper_final", float(tau_p[-1]))
    rec.metric("tau_official_final", float(tau_off[-1]))
    rec.check("P1.5", np.isfinite(rms) and rms > 0,
              "paper Eq.(8) vs upstream variant: RMS deviation %.4f" % rms, rms=rms)
    # the upstream variant has no minus sign: on the same approach geometry it
    # drives tau *down* while Eq.(8) drives it up.  Recorded, not resolved.
    G0_sign = TA.G_of(xi0, v_o, xi_star, eps_g)
    dtau0_off, _ = TA.official_tau_dot(tau0, xi0, v_o, xi0 * 0.5)
    conflict = bool(G0_sign > 0 and dtau0_off < 0)
    rec.metric("official_sign_conflict_on_approach", conflict)
    rec.metric("tau0", tau0)

    # ----------------------------------------------------------- figures
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    for label, (t, num, ex) in curves.items():
        ax.plot(t, num, lw=2, label="RK4  %s" % label)
        ax.plot(t, ex, "k--", lw=0.9, alpha=0.7)
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$\tau_{ci}$")
    ax.set_title("Eq.(8): three G cases (dashed = closed form)")
    ax.legend()
    save(fig, rec, "t01_tau_three_cases.png")

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    Gs = np.linspace(-5, 5, 41)
    ax.plot(Gs, TA.closed_form(tau0, Gs, k, 1.0), "o-", ms=3)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("G")
    ax.set_ylabel(r"$\tau(1\,\mathrm{s})$")
    ax.set_title("tau after 1 s versus G (tau0=1e-3, k=0.5)")
    save(fig, rec, "t01_tau_vs_G.png")

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(t, tau_p, lw=2, label="paper Eq.(8)")
    ax.plot(t, tau_off, lw=2, label="upstream variant")
    ax.set_xlabel("t [s]")
    ax.set_ylabel(r"$\tau_{ci}$")
    ax.set_title("Eq.(8) vs Multiarm_ds::calculate_coordination_allocation (RMS %.3f)" % rms)
    ax.legend()
    save(fig, rec, "t01_deviation.png")

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.loglog(dts, errs, "o-")
    for dt, e in zip(dts, errs):
        ax.annotate("%.1e" % e, (dt, e), textcoords="offset points", xytext=(4, 4), fontsize=7)
    ax.set_xlabel("dt [s]")
    ax.set_ylabel("max |RK4 - closed form|")
    ax.set_title("RK4 convergence, orders %s" % ["%.2f" % o for o in orders])
    save(fig, rec, "t01_convergence.png")

    rec.metric("convergence_orders", orders)
    return rec
