"""P5-T08 - the learned SCA boundary inside the closed-loop QP, Eq.(17d)+(26)+(21).

Fidelity
--------
`ORIGINAL` for the constraint structure: (17d) with the KKT-consistent sign of
Q3, (26) as the chain rule from feature space to joint space, (21a)/(21b) as the
QV assembly.  `ADAPTATION` for the scale: the *official 2-D CPSP model* is used
as the learned boundary oracle, fed with the relative position of the two tips.
No metric distance is claimed -- the 2-D model's Gamma has no calibration
against the planar arm's physical clearance (plan section "fidelity and limits").

Why the task and the SCA feature are *different* quantities
----------------------------------------------------------
This is the structural point that decides whether the test can mean anything.
Let the task be J_t qdot = xidot_t and the SCA feature f = f(q).  If f happened
to be exactly the task coordinate, then

    Gamma_dot = grad_f Gamma . f_dot = grad_f Gamma . (J_t qdot)

would be *implied* by the equality row, so (17d) could never bind: the QP would
either accept the task velocity or declare itself infeasible, and the redundant
degrees of freedom would have no way to satisfy the constraint.  The learned
boundary would look like a switch, not a constraint.

So the fixture is built the way the paper builds it: the task acts on one arm's
tip, while the SCA constrains the *pair* (both arms), which leaves the second
arm's two joints free to satisfy (17d).  With d_Q = 4, d_n = 2, d_c = 1 the
constraint has a 2-dimensional null space to work in, and the measured
activation ratio (about 0.5) shows it uses it.

Two plan expectations are falsified here and reported as measured, not adjusted
(see p5/reviews/P5_T08_POST.md section 4):

  * N8.2 said "lambda = 0 has no margin, so discretisation should produce
    crossings".  With lambda = 0 the row becomes Gamma_dot >= 0, which is
    *stricter* far from the boundary: it forbids any decrease at all and the
    approach stops immediately.
  * N8.3 said "the printed -log(Gamma-1) form attracts the configuration to the
    boundary".  That is true only in the limit Gamma -> 1; far away the printed
    form demands a *retreat* (the opposite sign), and in closed loop it
    saturates the velocity box.  Both halves are measured separately.
"""

import os

import numpy as np
import scipy.io as sio

import p5core
from p5core import qp_ik as QP
from p5core import svm_sca as S
from p5core.kinematics import DualPlanarArm
from p5core.plotting import plt, save
from p5core.results import require

REF = os.environ.get("P5_OFFICIAL_REF",
                     "/home/ubuntu2004/lmy/p5-official-ref/SCA-Boundary-Learning")
MODEL2D = os.path.join(REF, "models", "cpsp_models", "2d_example.mat")

#: Initial configuration: both arms comfortably away from their singularities
#: (sigma_min(J_left) = 0.325, sigma_min(J_right) = 0.256) and the relative tip
#: vector inside the 2-D model's validated domain at Gamma_raw = 6.38.
Q0 = np.array([-1.13625228, 1.51646827, -1.39144101, -1.14410536])
F_TARGET = np.array([0.60, 0.50])          # inside the model's collision band
Q_LIM = np.pi
QD_LIM = 1.5
V_TASK = 0.06                              # m/s, constant-speed tip task
T_END = 8.0
DT = 5e-3

EVENTS = ("LOG_DOMAIN", "QP_INFEASIBLE", "SOLVER_FAILURE", "BOUNDARY_CROSSING")


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


#: zero-padding (Eq.26) and the KKT measure live in p5core so that T10 uses
#: exactly the same code path and the two tasks cannot drift apart.
embed = QP.embed_pair_gradient


class Fixture:
    """Dual planar arm + the official 2-D CPSP model as the boundary oracle."""

    def __init__(self):
        require(os.path.exists(MODEL2D), "2-D CPSP model not found: %s" % MODEL2D)
        self.sha = _sha256(MODEL2D)
        self.model = S.load_cpsp(MODEL2D)
        self.arm = DualPlanarArm(2, (0.6, 0.45), (0.0, 0.0), (1.2, 1.2))
        self.d_q = self.arm.n

    # ---------------------------------------------------------- feature map
    def tips(self, q):
        return self.arm.eefs(q)

    def feature(self, q):
        pl, pr = self.tips(q)
        return pr - pl

    def gamma_raw(self, q):
        return float(self.model.gamma(self.feature(q)[None, :])[0])

    def grad_q(self, q):
        """Eq.(26): grad_q Gamma = (J_right - J_left)^T grad_f Gamma, zero-padded."""
        Jl, Jr = self.arm.jacobians(q)
        gf = self.model.grad(self.feature(q)[None, :])[0]
        pair = (Jr - Jl).T @ gf                       # 4-vector, both arms involved
        return pair, embed(pair, range(self.d_q), self.d_q)

    def rhs(self, gamma_raw, mode, lam=1.0):
        """Eq.(17d) right-hand side, and the event it raises.

        The QP convention here is `(g, rhs)` => `g.qdot >= -rhs`, so passing
        `g = +grad Gamma` with `rhs = log(Gamma_cal - 1)` encodes
        `-grad Gamma . qdot <= log(Gamma_cal - 1)`, i.e. (17d) with the
        KKT-consistent sign (Q3, docs/DECISIONS.md D006).
        """
        if mode == "paper":                 # b3 = +log(Gamma-1)
            if gamma_raw > 1.0:
                return float(np.log(gamma_raw - 1.0)), None
            return float(S.PAPER_FALLBACK), "LOG_DOMAIN"
        if mode == "printed":               # the paper's printed b3 = -log(Gamma-1)
            if gamma_raw > 1.0:
                return -float(np.log(gamma_raw - 1.0)), None
            return -float(S.PAPER_FALLBACK), "LOG_DOMAIN"
        if mode == "cone":                  # lambda = 0
            return 0.0, (None if gamma_raw > 1.0 else "LOG_DOMAIN")
        raise ValueError(mode)


def rollout(fx, sca_on=True, lam=1.0, mode="paper", sign=1.0, dt=DT, t_end=T_END,
            v_task=V_TASK, q0=None, stop_on_freeze=True):
    """Closed-loop integration of one configuration of the mechanism."""
    q = (Q0 if q0 is None else np.asarray(q0, float)).copy()
    pr0 = fx.tips(Q0)[1]
    goal = pr0 - F_TARGET
    n = int(round(t_end / dt))

    hist = {k: [] for k in ("t", "q", "gamma", "nu", "active", "qdot_max",
                            "event", "slack", "kkt", "pl")}
    counts = {k: 0 for k in EVENTS}
    fallback_count = 0
    first = {"freeze_t": None, "cross_t": None}

    def log(k, **kw):
        hist["t"].append(k * dt)
        hist["q"].append(q.copy())
        hist["event"].append(kw.get("event"))

    log(0)
    hist["gamma"].append(fx.gamma_raw(q))
    hist["nu"].append(0.0)
    hist["active"].append(False)
    hist["qdot_max"].append(0.0)
    hist["slack"].append(0.0)
    hist["kkt"].append(0.0)
    hist["pl"].append(fx.tips(q)[0].copy())

    frozen = False
    for k in range(n):
        if frozen:
            # The state does not advance any more; the failure is counted once
            # per step because the plan asks for a count, and the first
            # occurrence is reported separately.
            counts["QP_INFEASIBLE"] += 1
            log(k + 1, event="QP_INFEASIBLE")
            hist["gamma"].append(hist["gamma"][-1])
            hist["nu"].append(0.0)
            hist["active"].append(False)
            hist["qdot_max"].append(0.0)
            hist["slack"].append(0.0)
            hist["kkt"].append(np.nan)
            hist["pl"].append(hist["pl"][-1].copy())
            continue

        Jl, Jr = fx.arm.jacobians(q)
        pl, pr = fx.tips(q)
        d = goal - pl
        nrm = float(np.linalg.norm(d))
        fdot = (v_task * d / nrm) if nrm > 1e-4 else np.zeros(2)

        g, gq = fx.grad_q(q)
        gramp = fx.gamma_raw(q)

        rows = []
        ev = None
        if sca_on:
            r, ev0 = fx.rhs(gramp, mode, lam)
            if ev0 == "LOG_DOMAIN":
                counts["LOG_DOMAIN"] += 1
                fallback_count += 1
                ev = ev0
            rows = [(sign * gq, r)]

        lb, ub = QP.velocity_bounds(q, np.full(fx.d_q, -Q_LIM), np.full(fx.d_q, Q_LIM),
                                    np.full(fx.d_q, -QD_LIM), np.full(fx.d_q, QD_LIM),
                                    mu=20.0)
        qp = QP.QP(np.eye(fx.d_q), Jl, fdot, lb, ub, sca_rows=rows, lam=lam)
        x, info = qp.solve_active_set()

        if x is None:
            counts["QP_INFEASIBLE"] += 1
            if first["freeze_t"] is None:
                first["freeze_t"] = k * dt
                st = qp.classify()[0]
                first["classify"] = st
                if st == "OPTIMAL":       # feasible per classify but unsolvable
                    counts["SOLVER_FAILURE"] += 1
            log(k + 1, event="QP_INFEASIBLE")
            hist["gamma"].append(hist["gamma"][-1])
            hist["nu"].append(0.0)
            hist["active"].append(False)
            hist["qdot_max"].append(0.0)
            hist["slack"].append(0.0)
            hist["kkt"].append(np.nan)
            hist["pl"].append(hist["pl"][-1].copy())
            if stop_on_freeze:
                frozen = True         # keep the state, keep counting
            continue

        if ev == "LOG_DOMAIN":
            log(k + 1, event="LOG_DOMAIN")
        else:
            log(k + 1)

        q = q + dt * x
        g2 = fx.gamma_raw(q)
        act = bool(info.get("sca_active_rows"))
        nu = float(np.max(info.get("sca_multipliers") or [0.0]))
        slack = 0.0
        if rows:
            slack = float(rows[0][1] + rows[0][0] @ x)   # h = -g.qdot - rhs >= 0
        hist["gamma"].append(g2)
        hist["nu"].append(nu)
        hist["active"].append(act)
        hist["qdot_max"].append(float(np.max(np.abs(x))))
        hist["slack"].append(slack)
        hist["kkt"].append(QP.kkt_feasible(qp, x, info, rows))
        hist["pl"].append(fx.tips(q)[0].copy())

        if g2 < 0.0:
            counts["BOUNDARY_CROSSING"] += 1
            if first["cross_t"] is None:
                first["cross_t"] = (k + 1) * dt

    out = {k: np.asarray(v) for k, v in hist.items() if k != "event"}
    out["event"] = hist["event"]
    out["counts"] = counts
    out["fallback_count"] = fallback_count
    out["first"] = first
    out["activation_ratio"] = float(np.mean(hist["active"][1:])) if n else 0.0
    out["min_gamma"] = float(np.min(out["gamma"]))
    out["nu_max"] = float(np.max(out["nu"])) if len(out["nu"]) else 0.0
    out["kkt_max"] = float(np.nanmax(out["kkt"])) if np.any(np.isfinite(out["kkt"])) else np.nan
    return out


def run(rec):
    fx = Fixture()
    rec.metric("sha256_model2d", fx.sha)
    rec.metric("model", {"dim": fx.model.dim, "n_bvs": fx.model.n_bvs,
                         "sigma": fx.model.sigma, "bias": fx.model.bias})
    rec.metric("q0", Q0.tolist())
    rec.metric("f_target", F_TARGET.tolist())
    rec.metric("tip_goal", (fx.tips(Q0)[1] - F_TARGET).tolist())
    rec.metric("d_q", int(fx.d_q))

    # All rollouts are produced before any check is evaluated, so that a check
    # can cite the run that *exercises* an event class (P8.4 needs exactly that
    # for the classes that stay at zero on the reference run).
    ref = rollout(fx, sca_on=True, lam=1.0, mode="paper")
    off = rollout(fx, sca_on=False)
    flip = rollout(fx, sca_on=True, sign=-1.0)
    cone = rollout(fx, sca_on=True, lam=0.0)
    printed = rollout(fx, sca_on=True, mode="printed")
    coarse = rollout(fx, sca_on=True, dt=10 * DT)

    # ------------------------------------------------------------- P8.1
    rec.metric("min_gamma_raw_sca_on", ref["min_gamma"])
    rec.metric("crossing_count_sca_on", ref["counts"]["BOUNDARY_CROSSING"])
    rec.check("P8.1", ref["min_gamma"] >= -1e-6 and ref["counts"]["BOUNDARY_CROSSING"] == 0,
              "SCA on (lambda=1, literal +log form): min_t Gamma_raw = %.4f over %.1f s, "
              "boundary crossings = %d" % (ref["min_gamma"], T_END,
                                           ref["counts"]["BOUNDARY_CROSSING"]),
              min_gamma=ref["min_gamma"])

    # ------------------------------------------------------------- P8.2
    rec.metric("activation_ratio", ref["activation_ratio"])
    rec.metric("nu_max", ref["nu_max"])
    rec.check("P8.2", ref["activation_ratio"] > 0.05 and ref["nu_max"] > 0.0,
              "the constraint is genuinely binding: active on %.0f%% of the steps and the "
              "dual multiplier reaches nu_max = %.3f > 0 (a constraint that never binds "
              "would make the safety claim vacuous)"
              % (100 * ref["activation_ratio"], ref["nu_max"]),
              activation=ref["activation_ratio"], nu_max=ref["nu_max"])

    # ------------------------------------------------------------- P8.3
    rng = np.random.default_rng(11)
    qs = Q0 + rng.uniform(-0.6, 0.6, size=(400, fx.d_q))
    rel, mono_ok, mono_tot = 0.0, 0, 0
    h = 1e-6
    for q in qs:
        _, gq = fx.grad_q(q)
        fd = np.zeros(fx.d_q)
        for i in range(fx.d_q):
            e = np.zeros(fx.d_q)
            e[i] = h
            fd[i] = (fx.gamma_raw(q + e) - fx.gamma_raw(q - e)) / (2 * h)
        rel = max(rel, float(np.linalg.norm(gq - fd) / max(1e-300, np.linalg.norm(fd))))
        u = gq / max(1e-300, np.linalg.norm(gq))
        up = fx.gamma_raw(q + 1e-4 * u) - fx.gamma_raw(q - 1e-4 * u)
        mono_tot += 1
        mono_ok += int(up > 0)
    rec.metric("chain_rule_rel_err_max", rel)
    rec.metric("direction_check", [mono_ok, mono_tot])
    rec.check("P8.3", rel < 1e-6 and mono_ok == mono_tot,
              "Eq.(26) in the closed loop: max relative error against a central difference of "
              "Gamma(f(q)) over 400 configurations = %.2e; +grad_q Gamma raises Gamma on "
              "%d/%d configurations (a sign-agnostic FD test would not catch a flipped row)"
              % (rel, mono_ok, mono_tot), rel=rel, mono=mono_ok)

    # ------------------------------------------------------------- P8.4
    kkt_on = ref["kkt_max"]
    rec.metric("kkt_max_sca_on", kkt_on)
    rec.metric("log_domain_count", ref["counts"]["LOG_DOMAIN"])
    rec.metric("qp_infeasible_count", ref["counts"]["QP_INFEASIBLE"])
    rec.metric("solver_failure_count", ref["counts"]["SOLVER_FAILURE"])
    rec.metric("fallback_count", ref["fallback_count"])
    four_ok = (set(ref["counts"]) == set(EVENTS)
               and ref["counts"]["SOLVER_FAILURE"] == 0 and np.isfinite(kkt_on)
               and kkt_on < 1e-6)
    rec.metric("qp_infeasible_count_n8_1", flip["counts"]["QP_INFEASIBLE"])
    rec.metric("qp_infeasible_count_n8_3", printed["counts"]["QP_INFEASIBLE"])
    rec.check("P8.4", four_ok,
              "four event classes counted separately on the SCA-on run: LOG_DOMAIN %d, "
              "QP_INFEASIBLE %d, SOLVER_FAILURE %d, BOUNDARY_CROSSING %d.  Why each zero is "
              "zero, with the run that exercises the class: LOG_DOMAIN -- the log budget binds "
              "while Gamma_raw is still ~%.2f, so the trajectory is deflected before the domain "
              "ends (exercised by construction in P8.6, which starts inside the domain); "
              "QP_INFEASIBLE -- the barrier is satisfied inside the "
              "velocity box instead of saturating it (exercised by N8.1: %d steps, N8.3: %d "
              "steps, so the counter is wired to a live code path and is not dead); "
              "SOLVER_FAILURE -- every solve returns a KKT-verified point, max primal residual "
              "%.1e (never exercised anywhere: the exact enumerator either finds the optimum or "
              "proves infeasibility); BOUNDARY_CROSSING -- 0 with SCA on against %d with SCA off "
              "(P8.5), i.e. the counter is proven live by the matched control"
              % (ref["counts"]["LOG_DOMAIN"], ref["counts"]["QP_INFEASIBLE"],
                 ref["counts"]["SOLVER_FAILURE"], ref["counts"]["BOUNDARY_CROSSING"],
                 ref["min_gamma"],
                 flip["counts"]["QP_INFEASIBLE"], printed["counts"]["QP_INFEASIBLE"],
                 kkt_on, off["counts"]["BOUNDARY_CROSSING"]),
              counts=dict(ref["counts"]), kkt_max=kkt_on)

    # ------------------------------------------------------------- P8.5
    rec.metric("min_gamma_raw_sca_off", off["min_gamma"])
    rec.metric("crossing_count_sca_off", off["counts"]["BOUNDARY_CROSSING"])
    rec.check("P8.5", off["min_gamma"] < 0.0 and off["counts"]["BOUNDARY_CROSSING"] > 0,
              "matched control with SCA switched off, same task and same initial state: "
              "min_t Gamma_raw = %.4f and %d boundary crossings.  Without this the SCA-on "
              "result would be indistinguishable from 'the task never approaches the boundary'"
              % (off["min_gamma"], off["counts"]["BOUNDARY_CROSSING"]),
              min_gamma=off["min_gamma"], n=off["counts"]["BOUNDARY_CROSSING"])

    # ------------------------------------------------------------- P8.6
    q_bad = _inside_configuration(fx, rng)
    g_bad = fx.gamma_raw(q_bad)
    r_fb, ev_fb = fx.rhs(g_bad, "paper")
    # (a) the demanded rate is +|fallback| and cannot be met by any admissible qdot
    lb, ub = QP.velocity_bounds(q_bad, np.full(fx.d_q, -Q_LIM), np.full(fx.d_q, Q_LIM),
                                np.full(fx.d_q, -QD_LIM), np.full(fx.d_q, QD_LIM), mu=20.0)
    _, Jl_bad = fx.arm.jacobians(q_bad)
    qp_fb = QP.QP(np.eye(fx.d_q), Jl_bad, np.zeros(2), lb, ub,
                  sca_rows=[(fx.grad_q(q_bad)[1], r_fb)], lam=1.0)
    x_fb, _ = qp_fb.solve_active_set()
    # (b) the *direction* of the fallback is right: the closest admissible velocity
    #     (the box vertex along +grad Gamma) raises Gamma.
    _, gq_bad = fx.grad_q(q_bad)
    u = gq_bad / np.linalg.norm(gq_bad)
    vert = np.where(u > 0, ub, lb)
    best_effort_rate = float(gq_bad @ vert)
    q_up = q_bad + 1e-6 * vert
    g_up = fx.gamma_raw(q_up)
    rec.metric("inside_gamma_raw", g_bad)
    rec.metric("fallback_rhs", r_fb)
    rec.metric("fallback_demanded_rate", -r_fb)
    rec.metric("fallback_best_effort_rate", best_effort_rate)
    rec.metric("fallback_gamma_step", g_up - g_bad)
    rec.check("P8.6", ev_fb == "LOG_DOMAIN" and g_bad < 0.0 and g_up > g_bad
              and best_effort_rate < -r_fb and x_fb is None,
              "PAPER_FALLBACK tested on its own, separately from the literal log form: from a "
              "configuration with Gamma_raw = %.3f the fallback fires (rhs = %.0f, i.e. it "
              "demands Gamma_dot >= %.0f).  The direction is right -- the box vertex along "
              "+grad Gamma raises Gamma at %.1f/s (one 1e-6 s step: %+.2e) -- but the best "
              "achievable rate is %.1f, so the hard-constrained QP is INFEASIBLE: the fallback "
              "is a *soft-formulation* device and this fixture shows it cannot be honoured as a "
              "hard row"
              % (g_bad, r_fb, -r_fb, best_effort_rate, g_up - g_bad, best_effort_rate),
              gamma_inside=g_bad, demanded=-r_fb, best_effort=best_effort_rate)

    # ------------------------------------------------------------- N8.1
    rec.metric("min_gamma_sign_flipped", flip["min_gamma"])
    rec.defect("N8.1", flip["min_gamma"] < ref["min_gamma"] - 0.5,
              "flipping the sign of grad_q Gamma (a one-character defect) drops min_t "
              "Gamma_raw from %.3f to %.3f and freezes the run at t = %s s instead of "
              "completing it: the row's sign is observable in the closed loop"
              % (ref["min_gamma"], flip["min_gamma"], _fmt(flip["first"]["freeze_t"])),
              min_gamma_flipped=flip["min_gamma"])

    # ------------------------------------------------------------- N8.2
    rec.metric("min_gamma_lambda0", cone["min_gamma"])
    rec.metric("activation_ratio_lambda0", cone["activation_ratio"])
    rec.defect("N8.2", abs(cone["min_gamma"] - ref["min_gamma"]) > 1.0,
              "lambda = 0 makes the row Gamma_dot >= 0.  Measured: min_t Gamma_raw stays at "
              "%.3f and the constraint is active on %.0f%% of the steps, so the approach is "
              "blocked immediately.  This FALSIFIES the plan's expectation that lambda = 0 "
              "should be the looser setting (see the POST report): far from the boundary "
              "lambda = 0 removes the log budget rather than adding margin"
              % (cone["min_gamma"], 100 * cone["activation_ratio"]),
              min_gamma=cone["min_gamma"], activation=cone["activation_ratio"])

    # ------------------------------------------------------------- N8.3
    grid = [1.01, 1.2, 2.0, 6.38]
    # demanded Gamma_dot of each form, +log(g-1) for the printed b3 = -log(g-1)
    # and -log(g-1) for the KKT-consistent b3 = +log(g-1)
    tbl = {g: (float(np.log(g - 1.0)), float(-np.log(g - 1.0))) for g in grid}
    rec.metric("printed_vs_kkt_rhs", {str(g): v for g, v in tbl.items()})
    rec.metric("min_gamma_printed", printed["min_gamma"])
    rec.defect("N8.3", printed["counts"]["QP_INFEASIBLE"] > 0
              and tbl[6.38][0] > 0 > tbl[1.01][0],
              "the printed b3 = -log(Gamma-1) inverts the requested rate: at Gamma_raw = 6.38 it "
              "demands Gamma_dot >= %+.2f (a retreat) where the KKT form allows %+.2f, and at "
              "Gamma_raw = 1.01 it demands %+.2f where the KKT form demands %+.2f -- i.e. the "
              "protection vanishes exactly where it is needed.  Closed loop: saturated from "
              "t = %s s, min_t Gamma_raw held at %.3f by the velocity box, not by the boundary"
              % (tbl[6.38][0], tbl[6.38][1], tbl[1.01][0], tbl[1.01][1],
                 _fmt(printed["first"]["freeze_t"]), printed["min_gamma"]),
              infeasible=printed["counts"]["QP_INFEASIBLE"], table=rec.metrics["printed_vs_kkt_rhs"])

    # ------------------------------------------------------------- N8.4
    _, gq = fx.grad_q(Q0)
    cols_wrong = np.zeros(fx.d_q)
    cols_wrong[[0, 1]] = gq[[2, 3]]               # arm-2 block written into arm-1 columns
    dim_err = False
    try:
        embed(np.array([1.0, 2.0, 3.0]), (0, 1), fx.d_q)
    except ValueError:
        dim_err = True
    rel_wrong = _closed_loop_row_error(fx, Q0, cols_wrong)
    rec.metric("embedding_error_rel", rel_wrong)
    rec.defect("N8.4", dim_err and rel_wrong > 1e-2,
              "zero-padding defects: a pair gradient of length 3 into 2 columns raises "
              "ValueError (dimension assertion), and writing the arm-2 block into the arm-1 "
              "columns changes the predicted Gamma_dot by %.1e relative -- the FD check P8.3 "
              "would reject it" % rel_wrong, rel_wrong=rel_wrong)

    # ------------------------------------------------------------- N8.5
    n_clip = _count_clip(fx)
    patched_hit = _clip_hit_on_path(fx)
    rec.metric("np_clip_calls_on_path", patched_hit)
    rec.metric("clip_occurrences_in_sca_path", n_clip)
    rec.defect("N8.5", patched_hit == 0,
              "no silent clamping on the SCA path: np.clip was replaced by a tripwire and the "
              "closed loop ran %d steps without calling it (the only clip call in the package "
              "sits in the unused SLSQP backend).  Gamma_raw outside the log domain is handled "
              "by the labelled PAPER_FALLBACK, never by clipping" % 60,
              calls=patched_hit, occurrences=n_clip)

    # ------------------------------------------------------------- N8.6
    rec.metric("min_gamma_dt10x", coarse["min_gamma"])
    rec.metric("crossing_count_dt10x", coarse["counts"]["BOUNDARY_CROSSING"])
    rec.defect("N8.6", abs(coarse["min_gamma"] - ref["min_gamma"]) > 1e-3,
              "step size multiplied by 10: min_t Gamma_raw moves from %.4f to %.4f and the "
              "crossing count goes from %d to %d.  Discretisation error is real -- the hold "
              "point is not step-size invariant, so no 'any step size is perfect' claim is made"
              % (ref["min_gamma"], coarse["min_gamma"],
                 ref["counts"]["BOUNDARY_CROSSING"], coarse["counts"]["BOUNDARY_CROSSING"]),
              min_gamma=coarse["min_gamma"])

    # ------------------------------------------------------- dt convergence
    ladder = [DT, DT / 2, DT / 4]
    mins = []
    for dtl in ladder:
        r = rollout(fx, sca_on=True, dt=dtl)
        mins.append(r["min_gamma"])
    delta = float(np.max(np.abs(np.diff(mins))))
    rec.metric("dt_ladder", ladder)
    rec.metric("dt_ladder_min_gamma", mins)
    rec.metric("step_convergence_delta", delta)
    rec.check("P8.7", delta < 1e-2,
              "step-size convergence over dt = %s: min_t Gamma_raw = %s, successive differences "
              "<= %.1e -- the reported minimum is a property of the mechanism, not of dt"
              % (["%.4g" % d for d in ladder], ["%.5f" % m for m in mins], delta), delta=delta)

    # ----------------------------------------------------------- figures
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.plot(ref["t"], ref["gamma"], color="#4b7bec", lw=1.6, label="SCA on ($\\lambda=1$)")
    ax.plot(off["t"], off["gamma"], color="#eb3b5a", lw=1.4, label="SCA off")
    ax.axhline(0.0, color="k", ls=":", lw=1.0)
    ax.annotate("$\\Gamma_{raw}=0$: learned boundary", xy=(0.02, 0.02),
                xycoords="axes fraction", fontsize=8)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("$\\Gamma_{raw}$")
    ax.set_title("learned boundary inside the QP: min %.2f (on) vs %.2f (off)"
                 % (ref["min_gamma"], off["min_gamma"]))
    ax.legend(fontsize=8)
    save(fig, rec, "t08_min_gamma.png")

    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    for i in range(fx.d_q):
        ax.plot(ref["t"], ref["q"][:, i], lw=1.2, label="q%d" % (i + 1))
    act_t = ref["t"][1:][np.asarray(ref["active"][1:], bool)]
    for tt in act_t:
        ax.axvspan(tt - DT / 2, tt + DT / 2, color="#fed330", alpha=0.25, lw=0)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("joint angle [rad]")
    ax.set_title("joint trajectories (shaded: (17d) active)")
    ax.legend(fontsize=7, ncol=4)
    save(fig, rec, "t08_joint_traj.png")

    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    qs2 = Q0 + np.random.default_rng(3).uniform(-0.6, 0.6, size=(120, fx.d_q))
    A, N = [], []
    for q in qs2:
        _, gqv = fx.grad_q(q)
        fdv = np.zeros(fx.d_q)
        for i in range(fx.d_q):
            e = np.zeros(fx.d_q)
            e[i] = 1e-6
            fdv[i] = (fx.gamma_raw(q + e) - fx.gamma_raw(q - e)) / 2e-6
        A.append(gqv)
        N.append(fdv)
    A, N = np.concatenate(A), np.concatenate(N)
    ax.scatter(N, A, s=6, alpha=0.5, color="#4b7bec")
    lim = [min(N.min(), A.min()), max(N.max(), A.max())]
    ax.plot(lim, lim, "k--", lw=1.0)
    ax.set_xlabel("central difference $\\partial\\Gamma/\\partial q_i$")
    ax.set_ylabel("analytic $(J_2-J_1)^T \\nabla_f\\Gamma$")
    ax.set_title("Eq.(26), max rel. err %.1e" % rel)
    save(fig, rec, "t08_grad_check.png")

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.6), sharex=True,
                                 gridspec_kw={"height_ratios": [1, 1.4]})
    a1.plot(ref["t"], ref["nu"], color="#20bf6b", lw=1.2)
    a1.set_ylabel("$\\nu$")
    a1.set_title("dual multiplier of (17d): zero when inactive, positive when binding")
    mark = {"LOG_DOMAIN": ("#f7b731", "|"), "QP_INFEASIBLE": ("#eb3b5a", "x"),
            "BOUNDARY_CROSSING": ("#000000", "o")}
    for name, (col, mk) in mark.items():
        idx = [i for i, e in enumerate(ref["event"]) if e == name]
        if idx:
            a2.plot(ref["t"][idx], [0] * len(idx), mk, color=col, ms=5, label=name)
    idx = [i for i, e in enumerate(off["event"]) if e == "BOUNDARY_CROSSING"]
    if idx:
        a2.plot(off["t"][idx], np.full(len(idx), -1.0), "o", color="#eb3b5a", ms=3,
                label="crossing (SCA off)")
    a2.set_ylim(-1.6, 0.6)
    a2.set_yticks([])
    a2.set_xlabel("t [s]")
    a2.set_ylabel("events")
    if a2.get_legend_handles_labels()[0]:
        a2.legend(fontsize=7, loc="lower left")
    save(fig, rec, "t08_events.png")

    return rec


# ---------------------------------------------------------------- helpers
def _fmt(v):
    return "n/a" if v is None else "%.3f" % v


def _inside_configuration(fx, rng):
    """A configuration whose tip-pair feature sits inside the collision band."""
    target = np.array([0.60, 0.55])
    best = None
    for _ in range(40000):
        q = rng.uniform(-2.6, 2.6, fx.d_q)
        d = float(np.linalg.norm(fx.feature(q) - target))
        if best is None or d < best[0]:
            best = (d, q.copy())
    return best[1]


def _closed_loop_row_error(fx, q, gq_wrong):
    """Relative error of Gamma_dot predicted with a mis-embedded row."""
    Jl, Jr = fx.arm.jacobians(q)
    d = (fx.tips(Q0)[1] - F_TARGET) - fx.tips(q)[0]
    n = np.linalg.norm(d)
    fdot = V_TASK * d / n if n > 1e-4 else np.zeros(2)
    lb, ub = QP.velocity_bounds(q, np.full(fx.d_q, -Q_LIM), np.full(fx.d_q, Q_LIM),
                                np.full(fx.d_q, -QD_LIM), np.full(fx.d_q, QD_LIM), mu=20.0)
    qp = QP.QP(np.eye(fx.d_q), Jl, fdot, lb, ub)
    x, _ = qp.solve_active_set()
    if x is None:
        return np.inf
    _, gq_ok = fx.grad_q(q)
    a = float(gq_ok @ x)
    b = float(gq_wrong @ x)
    return abs(a - b) / max(1e-300, abs(a))


def _count_clip(fx):
    """How many np.clip calls exist in the modules the closed loop touches."""
    import inspect
    n = 0
    for mod in (QP, S):
        src = inspect.getsource(mod)
        n += src.count("np.clip(")
    return n


def _clip_hit_on_path(fx):
    """Run a few closed-loop steps with np.clip replaced by a tripwire."""
    real = np.clip
    hits = [0]

    def tripwire(*a, **k):
        hits[0] += 1
        return real(*a, **k)

    np.clip = tripwire
    try:
        rollout(fx, sca_on=True, t_end=0.3)
    finally:
        np.clip = real
    return hits[0]
