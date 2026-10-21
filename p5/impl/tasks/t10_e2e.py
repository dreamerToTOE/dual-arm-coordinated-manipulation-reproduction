"""P5-T10 - end-to-end numerical chain: tau -> LPV DS -> virtual object -> QP -> LVI.

Fidelity: `ADAPTATION` throughout.  This task reproduces the *mechanism chain* of
the paper, not its performance figures (those are 7-DOF KUKA arms on hardware).

The chain, with the task that produced each link
------------------------------------------------

    Eq.(8)   tau_dot = tau(1-tau) G / k                      T01
    Eq.(2)   xdot_i^R = taudot_i e + tau_i xdot^V + A_i(...)  T02 (LPV scheduler)
    Eq.(15)  gammadot = (1-gamma)/(|x^O - x*| + eps)          T03
    Eq.(36)  xdot^V = R(gamma, gammadot, x^O, xdot^O, x^V)    T03 (the tau-free form)
    Eq.(17)  min ||qdot||^2  s.t. J qdot = xdot^R             T04
    (17d)+grad  -grad Gamma . qdot <= log(Gamma-1)            T08 (chain rule from T07)
    Eq.(19)-(23) the LVI assembly; its multipliers are read back T05

Two structural points that come straight out of D014/D015 and shape this file:

1. **`tau` has to be integrated, not switched.**  Eq.(8) is a logistic field with
   equilibria at 0 and 1: `tau(0) = eps` starts asynchronous and the object's
   motion toward the intercept point (`G > 0`) carries it to 1.  The switch is
   therefore *observable* (`t_switch := first t with max_i tau_i >= 0.5`) and
   pinning `tau == 1` or `tau == 0` cannot produce it.  N10.2 pins both.
2. **The SCA pair must not be a pair whose relative position the task pins.**
   Both tips are task coordinates here (that is the point of the chain), so a
   tip-tip SCA row would be *implied* by the equality rows -- measured null-space
   share 0.00 at the initial configuration.  The pair is therefore chosen by a
   rule fixed *before* any constrained run: among the 15 body-point pairs, take
   the one with the largest initial `Gamma_raw` whose gradient keeps a usable
   share of the task null space.  The rule picks "left tip vs right elbow"
   (`Gamma_raw = 4.24`, share 0.21); this is reported, not tuned.

Energy bookkeeping (plan section on T10, docs/DECISIONS.md D009)
---------------------------------------------------------------
There is **no** physical energy statement here.  Under the stated assumption
that the QP is a velocity-level controller with `f = W qdot`, the run reports
`int P_in dt - Delta S - int psi dt` as an *implementation self-consistency*
residual.  `S` is a tracking-error norm, never called energy; `psi` is the
Theorem-3 dissipation of the LVI of each step.  A large residual means an
unmodelled term in the implementation, nothing else.
"""

import os
import time

import numpy as np

import p5core
from p5core import lvi as LV
from p5core import multiarm_ds as MD
from p5core import qp_ik as QP
from p5core import svm_sca as S
from p5core import tau as TAU
from p5core.kinematics import DualPlanarArm
from p5core.plotting import plt, save
from p5core.results import require

REF = os.environ.get("P5_OFFICIAL_REF",
                     "/home/ubuntu2004/lmy/p5-official-ref/SCA-Boundary-Learning")
MODEL2D = os.path.join(REF, "models", "cpsp_models", "2d_example.mat")

# ---------------------------------------------------------------- fixture
BASE_L = np.array([0.0, 0.0])
BASE_R = np.array([1.6, 0.0])
LINKS = (0.60, 0.45, 0.35)
D_ARM = 3
Q0 = np.array([-0.8992135004382478, 1.4394429338308097, 1.6632712609730937,
               1.5362577616709157, 1.2387815404449594, 0.45154770892407914])
X_STAR = np.array([0.95, 0.25])           # object goal = intercept point x*
X_O0 = np.array([1.25, 0.75])             # object start
F_TIP_TARGET = np.array([0.28, 0.41])     # goal separation of the two tips

K_TAU = 0.8
EPS_TAU = (0.02, 0.03)                    # per-arm, so the two tau curves differ
LAMBDA_OBJ = 1.0
A_ARM = -0.35 * np.eye(2)                 # Eq.(2)'s A, position-only (ADAPTATION)
A_V = -1.5 * np.eye(2)
Q_LIM = np.pi
QD_LIM = 1.5
DT = 1e-2
T_END = 8.0
V_MAX_TIP = 0.15                          # m/s, bounds the Eq.(2) reference


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


class Chain:
    """Body-point bookkeeping for the two 3-link arms."""

    def __init__(self):
        require(os.path.exists(MODEL2D), "2-D CPSP model not found: %s" % MODEL2D)
        self.sha = _sha256(MODEL2D)
        self.model = S.load_cpsp(MODEL2D)
        self.arm = DualPlanarArm(D_ARM, LINKS, BASE_L, BASE_R)
        self.d_q = self.arm.n
        self.d_n = 2 * 2 * D_ARM // D_ARM      # 4 task rows (two tips)
        self.d_n = 4

    def tips(self, q):
        return self.arm.eefs(q)

    def point(self, q, arm, link):
        return self.arm.link_point(q, arm, link)

    def point_jac(self, q, arm, link):
        return self.arm.link_point_jacobian(q, arm, link)

    def task_jac(self, q):
        return self.arm.stacked_jacobian(q)

    def pair_grad(self, q, i, j):
        """Eq.(26) for the body-point pair (i, j), zero-padded into d_Q."""
        ai, ki = i // D_ARM, i % D_ARM
        aj, kj = j // D_ARM, j % D_ARM
        f = self.point(q, aj, kj) - self.point(q, ai, ki)
        gf = self.model.grad(f[None, :])[0]
        Jp = self.point_jac(q, aj, kj) - self.point_jac(q, ai, ki)
        pair = Jp.T @ gf                                  # (d_Q,), arm order as q
        cols = list(range(ai * D_ARM, (ai + 1) * D_ARM)) + \
               list(range(aj * D_ARM, (aj + 1) * D_ARM))
        return f, pair, cols

    def pair_gamma(self, q, i, j):
        return float(self.model.gamma(self.pair_grad(q, i, j)[0][None, :])[0])

    def candidate_pairs(self, qs, stride=8):
        """Every mixed body-point pair evaluated ALONG the reference trajectory.

        A pair is only usable as an SCA row if (i) its `Gamma_raw` is positive
        where the motion starts, (ii) it goes negative somewhere along the
        uncontrolled motion (otherwise the constraint is never exercised), and
        (iii) its gradient keeps a usable share of the task null space over the
        *whole* path -- a pair whose gradient lies inside the task space at some
        configuration makes (17d) implied there, and the QP can then only freeze.
        Selecting on (iii) is a fixture-validity criterion, not an outcome
        criterion: it uses only the uncontrolled trajectory and the kinematics.
        """
        qs = np.asarray(qs, float)[::stride]
        out = []
        for i in range(D_ARM):
            for j in range(D_ARM, 2 * D_ARM):
                gam = np.array([self.pair_gamma(q, i, j) for q in qs])
                shares = []
                for q in qs:
                    N = np.linalg.svd(self.task_jac(q))[2][4:].T
                    _, gq, _ = self.pair_grad(q, i, j)
                    gq = QP.embed_pair_gradient(gq, range(self.d_q), self.d_q)
                    shares.append(float(np.linalg.norm(N.T @ gq)
                                        / max(1e-12, np.linalg.norm(gq))))
                out.append({"i": i, "j": j, "gamma0": float(gam[0]),
                            "gamma_min": float(gam.min()),
                            "share_min": float(np.min(shares)),
                            "share_mean": float(np.mean(shares))})
        return out

    def choose_pair(self, qs, gamma0_floor=1.5, cross_margin=-0.5, share_floor=0.10):
        cands = self.candidate_pairs(qs)
        ok = [c for c in cands if c["gamma0"] > gamma0_floor
              and c["gamma_min"] < cross_margin and c["share_min"] >= share_floor]
        require(len(ok) > 0,
                "no mixed body-point pair is both actuable (null share >= %.2f) and "
                "violated (Gamma_min < %.1f) on this task" % (share_floor, cross_margin))
        return max(ok, key=lambda c: c["share_min"]), cands


LABELS = ["L1", "L2", "L3", "R1", "R2", "R3"]


def _reference_velocity(chain, q, xv, xstar, xdotv, taus, taudots, g):
    """Eq.(2) for both arms with per-arm grasp offsets `g`."""
    pl, pr = chain.tips(q)
    e = xv - xstar                                     # common to both arms
    out = []
    for p, gi, tau_i, taudot_i in zip((pl, pr), g, taus, taudots):
        xd = xstar + gi
        v = taudot_i * e + tau_i * xdotv + A_ARM @ (p - xd - tau_i * e)
        n = float(np.linalg.norm(v))
        if n > V_MAX_TIP:
            v = v * (V_MAX_TIP / n)
        out.append(v)
    return np.concatenate(out)


def rollout(chain, pair, sca_on=True, lam=1.0, mu_tau=None, dt=DT, t_end=T_END,
            row_policy="freeze", rhs_mode="calibrated", capture=None):
    """One end-to-end run.  `mu_tau` = 1 or 0 pins tau, used by N10.2.

    `rhs_mode` selects the (17d) right-hand side actually assembled into the QP:

    * ``"calibrated"``          -- log(Gamma_raw/KAPPA), domain Gamma_raw > 0 (D007).
    * ``"mutation_log_minus1"`` -- the pre-audit log(Gamma_raw - 1), domain
      Gamma_raw > 1.  NOT an implementation option: it exists only as the R1
      mutation that the applied-rhs audit (P10.8) must detect.

    `capture`, when given a dict, collects one snapshot per step of the *actual*
    LVI data seen by the solver (M, b, box, recomposed u, multipliers) so that
    R3 can re-solve the very same instances with Eq.(20).

    `row_policy` decides what happens on a step where (17d) makes the QP
    infeasible (which is not rare -- see D018):

    * ``"freeze"``  -- hold the joint velocity at 0 for that step (ENGINEERING:
      the solver returned nothing, and zero is the only value that is guaranteed
      to stay inside the box).
    * ``"drop_row"`` -- re-solve the same QP without (17d) and take that motion.
      This is the *counterfactual* that separates "the row steers the arms away
      from the boundary" from "the row froze the arms", so it is measured in
      both modes and neither is presented as the paper's controller.
    """
    i, j = pair["i"], pair["j"]
    q = Q0.copy()
    xo = X_O0.copy()
    xv = X_O0.copy()
    gamma = 0.02
    taus = np.array(EPS_TAU, float)
    pl0 = chain.tips(Q0)[0]
    g = [pl0 - X_STAR, pl0 + F_TIP_TARGET - X_STAR]

    n = int(round(t_end / dt))
    hist = {k: [] for k in ("t", "tau", "gamma", "gam", "G", "sep", "q", "xv", "xo",
                            "pin", "psi", "V", "ytu", "active", "cross", "idres",
                            "gam_pre", "gam_cal_pre", "rhs_applied", "g_row",
                            "qdot")}
    counts = {"LOG_DOMAIN": 0, "QP_INFEASIBLE": 0, "SOLVER_FAILURE": 0,
              "BOUNDARY_CROSSING": 0, "ROW_DROPPED": 0}
    solve_s = []
    t_switch = None
    t_close = None
    #: a "switch" only exists if tau starts BELOW 0.5; pinning tau removes it by
    #: construction (N10.2), it must not be reported as an instantaneous switch.
    tau_start = float(np.max(taus)) if mu_tau is None else float(mu_tau)
    prev_sep = None
    kkt_max = 0.0

    for k in range(n):
        J = chain.task_jac(q)
        dvec = xo - X_STAR
        gscalar = TAU.G_of(xo, -LAMBDA_OBJ * dvec, X_STAR)
        gammadot = MD.gamma_dot(gamma, xo, X_STAR)
        R = MD.vo_R(gamma, gammadot, xo, -LAMBDA_OBJ * dvec, xv, A_V)
        xdotv = MD.vo_eq36(R)

        if mu_tau == 1:
            taus, taudots = np.ones(2), np.zeros(2)
        elif mu_tau == 0:
            taus, taudots = np.zeros(2), np.zeros(2)
        else:
            taudots = np.array([TAU.tau_dot(taus[a], gscalar, K_TAU) for a in range(2)])

        xr = _reference_velocity(chain, q, xv, X_STAR, xdotv, taus, taudots, g)
        _, gq, _ = chain.pair_grad(q, i, j)
        gq = QP.embed_pair_gradient(gq, range(chain.d_q), chain.d_q)
        gram = float(chain.model.gamma(chain.pair_grad(q, i, j)[0][None, :])[0])

        rows = []
        if sca_on:
            # (17d) rhs in the calibrated coordinates of Q4/D007:
            # log(Gamma_cal - 1) = log(Gamma_raw / KAPPA), KAPPA = 1, domain
            # Gamma_raw > 0 -- the learned boundary.  This MUST stay identical
            # to S.log_barrier; P10.8 audits the value ACTUALLY assembled into
            # the QP against an independent reconstruction (D020/R1).  The
            # pre-audit code used log(Gamma_raw - 1) here, which moved the
            # barrier to Gamma_raw = 1; D019.
            if rhs_mode == "calibrated":
                if gram > S.GAMMA_RAW_FLOOR:
                    rhs_val = float(np.log(gram / S.KAPPA))
                else:
                    rhs_val = float(S.PAPER_FALLBACK)
                    counts["LOG_DOMAIN"] += 1
            elif rhs_mode == "mutation_log_minus1":
                rhs_val = float(np.log(gram - 1.0)) if gram > 1.0 \
                    else float(S.PAPER_FALLBACK)
                if gram <= 1.0:
                    counts["LOG_DOMAIN"] += 1
            else:
                raise ValueError("unknown rhs_mode: %r" % (rhs_mode,))
            rows = [(gq, rhs_val)]

        lb, ub = QP.velocity_bounds(q, np.full(chain.d_q, -Q_LIM), np.full(chain.d_q, Q_LIM),
                                    np.full(chain.d_q, -QD_LIM), np.full(chain.d_q, QD_LIM),
                                    mu=20.0)
        qp = QP.QP(np.eye(chain.d_q), J, xr, lb, ub, sca_rows=rows, lam=lam)
        # D020/R1: record what the solver ACTUALLY receives -- read back from the
        # QP object itself, not from the local variable that built it.
        rhs_applied = float(qp.sca_rows[0][1]) if qp.sca_rows else float("nan")
        hist["gam_pre"].append(gram)
        hist["gam_cal_pre"].append(1.0 + gram / S.KAPPA)
        hist["rhs_applied"].append(rhs_applied)
        hist["g_row"].append(gq.copy())
        t0 = time.perf_counter()
        x, info = qp.solve_active_set()
        solve_s.append(time.perf_counter() - t0)
        if x is None:
            counts["QP_INFEASIBLE"] += 1
            # Attribution of the infeasibility, so that "the SCA row made the QP
            # infeasible" and "the reference velocity left the box" can never be
            # confused (docs/DECISIONS.md D018).  Same QP, rows removed.
            cls, _ci = qp.classify()
            counts["INF_" + str(cls)] = counts.get("INF_" + str(cls), 0) + 1
            qp0 = QP.QP(np.eye(chain.d_q), J, xr, lb, ub, sca_rows=[], lam=lam)
            cls0, _ci0 = qp0.classify()
            counts["INF_NOROW_" + str(cls0)] = counts.get("INF_NOROW_" + str(cls0), 0) + 1
            if float(np.linalg.norm(xr)) > 0:
                counts["INF_REFNORM_MAX"] = max(counts.get("INF_REFNORM_MAX", 0.0),
                                                float(np.linalg.norm(xr)))
            x = np.zeros(chain.d_q)
            info = {}
            if row_policy == "drop_row":
                xr0, info0 = qp0.solve_active_set()
                if xr0 is not None:
                    counts["ROW_DROPPED"] += 1
                    x = np.asarray(xr0, float)
                    info = info0
                    qp = qp0
                    # the row was not part of the QP that produced this x, so no
                    # multiplier may be invented for it downstream
                    rows = []
        else:
            kkt_max = max(kkt_max, QP.kkt_feasible(qp, x, info, rows))

        sep = float(np.linalg.norm(chain.tips(q)[1] - chain.tips(q)[0]))
        nxv = xv + dt * xdotv
        nxo = xo + dt * (-LAMBDA_OBJ * dvec)
        ngamma = float(np.clip(gamma + dt * gammadot, 0.0, 1.0))
        ntaus = np.clip(taus + dt * taudots, 0.0, 1.0)

        # --- Theorem-3 dissipation of this step: psi = u^T (I + M^T) u
        M, b = qp.M_b()
        nu = np.atleast_1d(np.asarray(info.get("sca_multipliers") or [0.0], float))
        G_all = np.array([gg for gg, _ in rows]).reshape(len(rows), chain.d_q) \
            if rows else np.zeros((0, chain.d_q))
        stat = np.eye(chain.d_q) @ x - (G_all.T @ nu if rows else 0.0)
        mu_eq = np.linalg.lstsq(J.T, stat, rcond=None)[0]
        uvec = np.concatenate([x, mu_eq, nu if rows else np.zeros(0)])
        I_M = np.eye(M.shape[0]) + M.T
        psi = float(uvec @ (I_M @ uvec))
        # Theorem-3 quantities of THIS step: V = 1/2 u^T u and the supply rate
        # Y^T U = u^T (I + M^T) P(u - Mu - b).  Recording them lets P10.5 check the
        # identity Vdot + psi = Y^T U along the whole chain instead of asserting it.
        lo, hi = qp.omega()
        Pproj = LV.project(uvec - (M @ uvec + b), lo, hi)
        Vval = 0.5 * float(uvec @ uvec)
        ytu = float(uvec @ (I_M @ Pproj))
        if capture is not None:
            #: D020/R3: the exact LVI instance (M, b, box) this step's QP defines,
            #: plus the active-set answer, for the same-instance LVI comparison.
            capture["items"].append({"k": k, "gram": gram, "M": M.copy(),
                                     "b": b.copy(), "lo": lo.copy(), "hi": hi.copy(),
                                     "u": uvec.copy(), "x": np.asarray(x, float).copy(),
                                     "active": bool(info.get("sca_active_rows"))})

        q = q + dt * x
        hist["qdot"].append(np.asarray(x, float).copy())
        xv, xo, gamma, taus = nxv, nxo, ngamma, ntaus
        nsep = float(np.linalg.norm(chain.tips(q)[1] - chain.tips(q)[0]))

        if t_switch is None and tau_start < 0.5 and float(np.max(taus)) >= 0.5:
            t_switch = (k + 1) * dt
        if t_close is None and prev_sep is not None and nsep < prev_sep - 1e-9:
            t_close = (k + 1) * dt
        prev_sep = nsep

        g2 = chain.pair_gamma(q, i, j)
        crossed = g2 < 0.0
        if crossed:
            counts["BOUNDARY_CROSSING"] += 1

        hist["t"].append((k + 1) * dt)
        hist["tau"].append(taus.copy())
        hist["gamma"].append(gamma)
        hist["gam"].append(g2)
        hist["G"].append(gscalar)
        hist["sep"].append(nsep)
        hist["q"].append(q.copy())
        hist["xv"].append(xv.copy())
        hist["xo"].append(xo.copy())
        # P_in = xdot^R . f with f the task-space force, i.e. the equality
        # multiplier recovered from W qdot = J^T mu + G^T nu (plan T10 table).
        hist["pin"].append(float(xr @ mu_eq))
        hist["psi"].append(psi)
        hist["V"].append(Vval)
        hist["ytu"].append(ytu)
        #: psi - Y^T U is the Theorem-3 identity residual *at the QP solution*: the
        #: active-set solution is the LVI fixed point, so this must vanish for the
        #: assembled M/b, independently of whether the trajectory is an ODE flow.
        hist["idres"].append(psi - ytu)
        hist["active"].append(bool(info.get("sca_active_rows")))
        hist["cross"].append(crossed)

    out = {k: np.asarray(v, float) for k, v in hist.items()}
    out["counts"] = counts
    out["t_switch"] = t_switch
    out["t_close"] = t_close
    out["solve_s"] = np.asarray(solve_s)
    out["kkt_max"] = kkt_max
    out["min_gamma"] = float(np.min(out["gam"]))
    out["activation"] = float(np.mean(hist["active"])) if hist["active"] else 0.0
    out["dt"] = dt
    out["q0"] = Q0.copy()
    out["n_steps"] = int(n)
    out["lam"] = float(lam)
    return out


# ===================================================================== run
def run(rec):
    chain = Chain()
    # Fixture design: the SCA row is chosen along the *uncontrolled* trajectory
    # (SCA off makes the pair irrelevant to the run, so this cannot leak the
    # constrained outcome into the choice).
    probe = rollout(chain, {"i": 0, "j": D_ARM}, sca_on=False)
    pair, cands = chain.choose_pair(probe["q"])
    i, j = pair["i"], pair["j"]
    rec.metric("sha256_model2d", chain.sha)
    rec.metric("sca_pair", "%s-%s" % (LABELS[i], LABELS[j]))
    rec.metric("sca_pair_indices", [i, j])
    rec.metric("sca_pair_gamma0", pair["gamma0"])
    rec.metric("sca_pair_gamma_min", pair["gamma_min"])
    rec.metric("sca_pair_null_share_min", pair["share_min"])
    rec.metric("sca_pair_null_share_mean", pair["share_mean"])
    rec.metric("candidate_table",
               [{"pair": "%s-%s" % (LABELS[c["i"]], LABELS[c["j"]]),
                 "gamma0": round(c["gamma0"], 4), "gamma_min": round(c["gamma_min"], 4),
                 "share_min": round(c["share_min"], 4)}
                for c in cands])
    rec.metric("d_q", int(chain.d_q))
    rec.metric("d_n", int(chain.d_n))
    rec.metric("d_c", 1)
    rec.metric("t_end", T_END)
    rec.metric("dt", DT)

    caps = {"items": []}
    ref = rollout(chain, pair, capture=caps)
    off = rollout(chain, pair, sca_on=False)
    #: counterfactual for the infeasible steps: drop (17d) instead of freezing.
    #: Without this the "0 crossings" number cannot be attributed to the row
    #: rather than to the freeze (D018).
    drop = rollout(chain, pair, row_policy="drop_row")
    t0_run = time.perf_counter()
    dt2 = rollout(chain, pair, dt=2 * DT)
    rec.metric("wall_dt_doubled_s", time.perf_counter() - t0_run)
    lam0 = rollout(chain, pair, lam=0.0)
    tau1 = rollout(chain, pair, mu_tau=1)
    tau0 = rollout(chain, pair, mu_tau=0)

    # ------------------------------------------------------------- P10.1
    tau_curve = ref["tau"][:, 0]
    mono = float(np.min(np.diff(tau_curve))) if tau_curve.size > 1 else 0.0
    # Pre-declared criterion (plan P10.1): tau rises monotonically from eps to > 0.9
    # and t_switch = first t with max_i tau_i >= 0.5 lands in [1, 5] s.
    # The plan's second, exploratory quantity -- "when does the pair start closing
    # on the boundary" -- is reported as t_approach = first t with dGamma/dt < 0.
    # It is NOT required to be simultaneous with t_switch: on a banded learned
    # boundary the pair can start approaching long before the arms synchronise,
    # and pretending otherwise would be an invented criterion.  What the switch
    # changes is reported as the two-phase rate ratio instead.
    dgam = np.diff(ref["gam"])
    t_approach = float(ref["t"][1:][dgam < 0][0]) if np.any(dgam < 0) else None
    rec.metric("t_switch", ref["t_switch"])
    rec.metric("t_approach", t_approach)
    rec.metric("tau_final", ref["tau"][-1].tolist())
    rec.metric("tau_monotonicity_min_diff", mono)
    if ref["t_switch"] is not None:
        pre = np.abs(dgam[ref["t"][1:] < ref["t_switch"]])
        post = np.abs(dgam[ref["t"][1:] >= ref["t_switch"]])
        rec.metric("approach_rate_pre", float(np.median(pre)) if pre.size else float("nan"))
        rec.metric("approach_rate_post", float(np.median(post)) if post.size else float("nan"))
        rec.metric("approach_rate_ratio",
                   float(np.median(post) / max(1e-300, np.median(pre)))
                   if pre.size and post.size else float("nan"))
    win_lo, win_hi = 1.0, 5.0
    p101 = (ref["t_switch"] is not None and win_lo <= ref["t_switch"] <= win_hi
            and float(np.min(ref["tau"][-1])) > 0.9 and mono >= -1e-12
            and t_approach is not None)
    rec.check("P10.1", p101,
              "asynchronous -> synchronous switch is observable and was not hand-placed: "
              "tau starts at eps = %s, rises monotonically (min increment %.1e) to %s, and "
              "t_switch (max_i tau_i >= 0.5) = %s s lands inside the pre-declared window "
              "[%.0f, %.0f] s.  The pair starts approaching the learned boundary at "
              "t_approach = %s s, i.e. well before the switch; the two are reported side by "
              "side, not forced to coincide"
              % (list(EPS_TAU), mono, np.round(ref["tau"][-1], 3),
                 _fmt(ref["t_switch"]), win_lo, win_hi, _fmt(t_approach)),
              t_switch=ref["t_switch"], t_approach=t_approach)

    # ------------------------------------------------------------- P10.2
    rec.metric("min_gamma_raw_sca_on", ref["min_gamma"])
    rec.metric("crossing_count_sca_on", ref["counts"]["BOUNDARY_CROSSING"])
    rec.metric("activation_ratio", ref["activation"])
    rec.metric("infeasible_sca_on", ref["counts"]["QP_INFEASIBLE"])
    rec.metric("infeasible_attribution", {k: v for k, v in ref["counts"].items()
                                          if k.startswith("INF_")})
    rec.check("P10.2", ref["counts"]["BOUNDARY_CROSSING"] == 0 and ref["activation"] > 0.05,
              "end-to-end with the learned boundary in the QP: min_t Gamma_raw = %.4f, "
              "boundary crossings = %d, the (17d) row is active on %.0f%% of the steps.  %s"
              % (ref["min_gamma"], ref["counts"]["BOUNDARY_CROSSING"],
                 100 * ref["activation"],
                 ("The calibrated (D007) row is feasible on ALL %d steps -- no freeze, no "
                  "row drop -- so the crossing-free outcome is attributable to the row "
                  "alone.  (The pre-audit uncalibrated rhs log(Gamma_raw-1) made 370/800 "
                  "steps infeasible; D019.)" % ref["n_steps"])
                 if ref["counts"]["QP_INFEASIBLE"] == 0 else
                 "Reported with its cost: the hard row makes the QP INFEASIBLE on %d of %d "
                 "steps (%.0f%%), every one of them attributed to the row -- the same QP "
                 "without (17d) is OPTIMAL on all %d.  Those steps are frozen at qdot = 0 "
                 "(`row_policy='freeze'`), so this number alone cannot be attributed to the "
                 "row steering the arms; P10.7 measures the counterfactual"
                 % (ref["counts"]["QP_INFEASIBLE"], ref["n_steps"],
                    100 * ref["counts"]["QP_INFEASIBLE"] / ref["n_steps"],
                    ref["counts"].get("INF_NOROW_OPTIMAL", 0))),
              min_gamma=ref["min_gamma"])

    # ------------------------------------------------------------- P10.8 / N10.6
    # D020/R1: audit the rhs ACTUALLY supplied to the solver, not a re-derivation.
    # Four comparisons per step with a row: (a) Gamma_raw re-computed from the
    # pre-solve joints, (b) the joint-space gradient re-computed the same way,
    # (c) (17d) reconstructed from (a) and compared with the value carried by the
    # QP object, (d) the same against S.log_barrier, and (e) the assembled
    # inequality -g.qdot <= lam*rhs checked against the applied joint velocity
    # (sign and scaling of the real numerical constraint).
    def _rhs_audit(run_out):
        gam_pre = run_out["gam_pre"]
        rhs_app = run_out["rhs_applied"]
        g_rec = run_out["g_row"]
        qd = run_out["qdot"]
        q_hist = run_out["q"]
        d_gram = d_grad = d_recon = d_helper = d_row = d_gal = 0.0
        for k in range(len(gam_pre)):
            r = rhs_app[k]
            if not np.isfinite(r):
                continue
            q_pre = Q0 if k == 0 else q_hist[k - 1]
            f, gq_re, _ = chain.pair_grad(q_pre, i, j)
            gq_emb = QP.embed_pair_gradient(gq_re, range(chain.d_q), chain.d_q)
            gram_re = float(chain.model.gamma(f[None, :])[0])
            d_gram = max(d_gram, abs(gram_re - gam_pre[k]))
            d_gal = max(d_gal, abs((1.0 + gram_re / S.KAPPA) - run_out["gam_cal_pre"][k]))
            d_grad = max(d_grad, float(np.max(np.abs(gq_emb - g_rec[k]))))
            rhs_re = float(np.log(gram_re / S.KAPPA)) \
                if gram_re > S.GAMMA_RAW_FLOOR else float(S.PAPER_FALLBACK)
            d_recon = max(d_recon, abs(rhs_re - r))
            lb_val, _ = S.log_barrier(np.array([gam_pre[k]]), S.KAPPA, mode="paper")
            d_helper = max(d_helper, abs(float(lb_val[0]) - r))
            #: the assembled inequality is  -g.qdot <= lam*rhs  (sign and scaling
            #: exactly as the exact enumerator enforces it)
            viol = max(0.0, -run_out["lam"] * r - float(g_rec[k] @ qd[k]))
            d_row = max(d_row, viol)
        return {"d_gram": d_gram, "d_grad": d_grad, "d_recon": d_recon,
                "d_helper": d_helper, "d_row": d_row, "d_gam_cal": d_gal}

    audit = _rhs_audit(ref)
    for kk, vv in audit.items():
        rec.metric("rhs_audit_" + kk, vv)
    audit_ok = (audit["d_gram"] == 0.0 and audit["d_grad"] == 0.0
                and audit["d_gam_cal"] == 0.0
                and audit["d_recon"] <= 1e-12 and audit["d_helper"] == 0.0
                and audit["d_row"] <= 1e-9 and ref["lam"] == 1.0)
    rec.check("P10.8", audit_ok,
              "the (17d) rhs is audited where it matters -- inside the QP the solver saw.  "
              "Over all %d row-bearing steps: Gamma_raw recomputed from the pre-solve joints "
              "matches the recorded pre-solve value EXACTLY (max diff %.1e); the embedded "
              "joint-space gradient matches EXACTLY (%.1e); (17d) reconstructed from the "
              "re-computed Gamma (and the calibrated Gamma_cal = 1 + Gamma_raw/kappa, max diff "
              "%.1e) matches the rhs carried by the QP object to %.1e and matches "
              "S.log_barrier EXACTLY (%.1e); and the assembled inequality -g.qdot <= lam*rhs "
              "holds with the applied joint velocity to %.1e (lam = %.0f).  The barrier sits at "
              "the learned boundary Gamma_raw = 0 per Q4/D007.  The pre-audit loop used "
              "log(Gamma_raw - 1) with domain Gamma_raw > 1, i.e. a barrier one unit above "
              "the boundary (D019); N10.6 proves this audit detects that mutation."
              % (int(np.count_nonzero(np.isfinite(ref["rhs_applied"]))),
                 audit["d_gram"], audit["d_grad"], audit["d_gam_cal"],
                 audit["d_recon"], audit["d_helper"],
                 audit["d_row"], ref["lam"]),
              **audit)

    # --- N10.6 (D020/R1): the mutation that caused the D019 drift must be caught.
    mut = rollout(chain, pair, rhs_mode="mutation_log_minus1", t_end=2.0)
    mut_audit = _rhs_audit(mut)
    rec.metric("mutation_rhs_audit", mut_audit)
    mutation_detected = (mut_audit["d_recon"] > 0.1 and mut_audit["d_helper"] > 0.1
                         and mut_audit["d_gram"] == 0.0)
    rec.defect("N10.6", mutation_detected,
               "replacing the applied rhs with the pre-audit log(Gamma_raw - 1) is DETECTED by "
               "the P10.8 audit: over %d mutated steps the reconstructed (17d) diverges from "
               "the applied rhs by max %.3f and S.log_barrier by max %.3f, while the Gamma "
               "reconstruction stays exact (%.1e) -- i.e. the audit reads the solver's actual "
               "input, so this exact drift can never pass silently again (D019/D020)."
               % (int(np.count_nonzero(np.isfinite(mut["rhs_applied"]))),
                  mut_audit["d_recon"], mut_audit["d_helper"], mut_audit["d_gram"]),
               **mut_audit)

    # ------------------------------------------------- R2: three Gamma levels
    n_below_1 = int(np.count_nonzero(ref["gam"] < 1.0))
    n_below_0 = int(np.count_nonzero(ref["gam"] < 0.0))
    rec.metric("n_steps_below_invariance_threshold", n_below_1)
    rec.metric("n_steps_below_svm_boundary", n_below_0)
    rec.metric("min_gamma_margin_to_1", float(ref["min_gamma"] - 1.0))

    # ------------------------------------------------------------- P10.9
    # D020/R3: the closed loop solves each QP with the exact active set; the LVI
    # (Eq. 19/20) is the paper's *formulation* of the same QP.  Re-solve the very
    # instances the loop encountered with the Eq.(20) dynamics and compare.
    items = caps["items"]
    grams = np.array([it["gram"] for it in items])
    order = np.argsort(grams)
    picked = {}
    for rank, idx in enumerate(order[:4]):          # closest to the boundary
        picked[idx] = "minGamma#%d" % rank
    act = [k for k, it in enumerate(items) if it["active"]]
    for idx in act[:: max(1, len(act) // 6)][:6]:   # active SCA rows
        picked.setdefault(idx, "activeRow")
    for idx in range(0, len(items), max(1, len(items) // 6))[:6]:
        picked.setdefault(idx, "uniform")
    lvi = []
    t_lvi = 0.0
    fp_as_max = 0.0
    for idx in sorted(picked):
        it = items[idx]
        u_as = it["u"]
        fp_as = float(np.linalg.norm(LV.residual(u_as, it["M"], it["b"],
                                                 it["lo"], it["hi"])))
        fp_as_max = max(fp_as_max, fp_as)
        #: protocol: the T05 settings first (dt = 5e-3, 20000 RK4 steps); on a
        #: non-converging instance ONE retry at dt = 1e-3 / 60000 steps.  The best
        #: attempt is reported; nothing is silently substituted.
        best = None
        steps_used = 0
        reason = None
        for dt_i, ms_i in ((5e-3, 20000), (1e-3, 60000)):
            t0 = time.perf_counter()
            res = LV.solve(it["M"], it["b"], it["lo"], it["hi"],
                           dt=dt_i, max_steps=ms_i, tol=1e-10)
            t_lvi += time.perf_counter() - t0
            steps_used += int(res["steps"])
            reason = res.get("reason")
            if best is None or res["residual"] < best["fp_residual"]:
                best = {"fp_residual": float(res["residual"]),
                        "primal_diff": float(np.linalg.norm(res["u"] - u_as)),
                        "dt": dt_i, "converged": bool(res["converged"])}
            if res["converged"]:
                break
        lvi.append({"k": int(it["k"]), "tag": picked[idx], "gram": float(it["gram"]),
                    "fp_residual": best["fp_residual"],
                    "primal_diff": best["primal_diff"], "dt_best": best["dt"],
                    "converged": best["converged"], "steps": steps_used,
                    "reason": reason, "as_fp_residual": fp_as})
    rec.metric("lvi_instances", len(lvi))
    rec.metric("lvi_converged_tol1e10", sum(1 for r in lvi if r["converged"]))
    rec.metric("lvi_below_1e-6", sum(1 for r in lvi if r["fp_residual"] <= 1e-6))
    rec.metric("lvi_best_fp_residual", min(r["fp_residual"] for r in lvi))
    rec.metric("lvi_worst_fp_residual", max(r["fp_residual"] for r in lvi))
    agree = [r for r in lvi if r["fp_residual"] <= 1e-6]
    lvi_max_diff = max((r["primal_diff"] for r in agree), default=float("nan"))
    rec.metric("lvi_max_primal_diff_below_1e-6", lvi_max_diff)
    rec.metric("as_fixed_point_residual_max", fp_as_max)
    rec.metric("lvi_time_s", t_lvi)
    rec.metric("lvi_detail", lvi)
    agreement_ok = (len(agree) > 0 and lvi_max_diff <= 1e-6)
    as_is_fixed_point = fp_as_max <= 1e-8
    flow_works = min(r["fp_residual"] for r in lvi) <= 1e-6
    rec.check("P10.9", agreement_ok and as_is_fixed_point and flow_works,
              "LVI (Eq.19/20) vs the exact active set on %d of the QP instances the loop "
              "actually encountered (4 nearest min-Gamma, %d with an active row, rest uniform; "
              "gram %.3f..%.3f; protocol: dt=5e-3/20000 steps, one retry dt=1e-3/60000).  "
              "The active-set answer is the LVI fixed point to %.1e on EVERY instance; the "
              "(20) flow converges (best fixed-point residual %.1e) and every instance that "
              "reached 1e-6 agrees with the active set to %.1e.  LIMITATION, reported not "
              "substituted: the (20) RK4 integration did NOT reach the 1e-10 tolerance on "
              "%d/%d instances within the budget (worst residual %.2f) -- the (I+M^T) "
              "dynamics are stiff near the log barrier, so the closed loop keeps the exact "
              "fixed-point solve and NO claim is made that an LVI-dynamics controller ran "
              "the 800-step rollout; P10.6 already quantifies the quasi-static distinction."
              % (len(lvi), sum(1 for r in lvi if r["tag"] == "activeRow"),
                 min(r["gram"] for r in lvi), max(r["gram"] for r in lvi),
                 fp_as_max, min(r["fp_residual"] for r in lvi), lvi_max_diff,
                 sum(1 for r in lvi if not r["converged"]), len(lvi),
                 max(r["fp_residual"] for r in lvi)),
              n_conv=sum(1 for r in lvi if r["converged"]),
              max_diff=lvi_max_diff, fp_as_max=fp_as_max,
              best_fp=min(r["fp_residual"] for r in lvi))

    # ------------------------------------------------------------- P10.3 / N10.1
    rec.metric("min_gamma_raw_sca_off", off["min_gamma"])
    rec.metric("crossing_count_sca_off", off["counts"]["BOUNDARY_CROSSING"])
    matched = (off["min_gamma"] < 0.0 and off["counts"]["BOUNDARY_CROSSING"] > 0)
    rec.check("P10.3", matched,
              "matched SCA-off control (same initial state, same object motion, same dt, same "
              "solver): min_t Gamma_raw = %.4f and %d boundary crossings, versus %.4f and %d "
              "with SCA on"
              % (off["min_gamma"], off["counts"]["BOUNDARY_CROSSING"],
                 ref["min_gamma"], ref["counts"]["BOUNDARY_CROSSING"]),
              min_gamma=off["min_gamma"])
    rec.defect("N10.1", matched,
               "removing the SCA row is detected as a defect: the crossing counter goes from "
               "%d to %d and min_t Gamma_raw from %.4f to %.4f"
               % (ref["counts"]["BOUNDARY_CROSSING"], off["counts"]["BOUNDARY_CROSSING"],
                  ref["min_gamma"], off["min_gamma"]),
               n=off["counts"]["BOUNDARY_CROSSING"])

    # ------------------------------------------------------------- P10.7
    # The counterfactual that keeps the e2e claim honest: on the steps where the
    # hard (17d) row is infeasible, drop the row and take the resulting motion
    # instead of freezing.  If the crossing-free outcome survives, the row is what
    # steers; if it does not, the "success" of the freeze policy was the freeze.
    dropped = drop["counts"]["ROW_DROPPED"]
    rec.metric("infeasible_drop_row", dropped)
    rec.metric("min_gamma_drop_row", drop["min_gamma"])
    rec.metric("crossing_count_drop_row", drop["counts"]["BOUNDARY_CROSSING"])
    # The gated claim is the STRONG one: without any freeze, the row keeps
    # Gamma_raw > 0.  Two ways to establish it: the counterfactual (rows existed
    # but were dropped on the infeasible steps) or direct feasibility (no step
    # was ever infeasible, so freeze/drop never fired).  A `True` placeholder
    # would make P10.7 decorative; a failure here turns the suite red and forces
    # the e2e claim down to "the freeze, not the row, avoids the boundary".
    # D020/R4: every infeasible step must be *attributed* to the (17d) row --
    # re-solving with the row removed reproduces the same failure class.  An
    # unattributed infeasibility means the e2e claim is measuring something else.
    attributed = sum(v for kk, v in ref["counts"].items() if kk.startswith("INF_NOROW_"))
    rec.metric("infeasible_sca_on_attributed", attributed)
    attribution_ok = (ref["counts"]["QP_INFEASIBLE"] == 0
                      or attributed == ref["counts"]["QP_INFEASIBLE"])
    # The reference run itself must be crossing-free for ANY branch of the gate;
    # otherwise "the row prevents crossings" is false before the counterfactual
    # is even consulted.
    ref_ok = (ref["counts"]["BOUNDARY_CROSSING"] == 0 and ref["min_gamma"] > 0.0
              and attribution_ok)
    vacuous = (dropped == 0)
    no_fallback = (vacuous and ref["counts"]["QP_INFEASIBLE"] == 0
                   and ref["counts"]["BOUNDARY_CROSSING"] == 0
                   and ref["min_gamma"] > 0.0)
    row_carries = (not vacuous and drop["counts"]["BOUNDARY_CROSSING"] == 0
                   and drop["min_gamma"] > 0.0)
    if no_fallback:
        verdict = ("The calibrated row was feasible on ALL %d steps: no freeze and no row "
                   "drop ever fired, so the crossing-free outcome is attributable to the row "
                   "alone.  The fallback machinery is exercised by the negative controls "
                   "instead (N10.4: %d infeasible at lambda = 0; T08/N8.1: 647 with the "
                   "gradient sign flipped).  (Pre-audit, the uncalibrated rhs "
                   "log(Gamma_raw - 1) made 370/800 steps infeasible; D019.)"
                   % (ref["n_steps"], lam0["counts"]["QP_INFEASIBLE"]))
    elif row_carries:
        verdict = ("The row still carries the guarantee without the freeze; the freeze "
                   "only adds conservatism.")
    elif vacuous:
        verdict = ("FAILED: no step was infeasible, so the counterfactual measures nothing, "
                   "and the reference run itself does not establish the row-only claim.")
    else:
        verdict = ("FAILED: the crossing-free outcome does NOT survive losing the row on "
                   "those steps, so the freeze is part of the mechanism and the e2e claim "
                   "is downgraded accordingly (D018) -- it must not be reported as an "
                   "SCA-only result.")
    rec.check("P10.7", ref_ok and (row_carries or no_fallback),
              "counterfactual on the %d infeasible steps (row dropped instead of frozen): "
              "min_t Gamma_raw = %.4f and %d boundary crossings, against %.4f / %d for the "
              "freeze policy and %.4f / %d with the row switched off entirely; "
              "attribution: %d/%d infeasible steps reproduce with the row removed.  %s"
              % (dropped, drop["min_gamma"], drop["counts"]["BOUNDARY_CROSSING"],
                 ref["min_gamma"], ref["counts"]["BOUNDARY_CROSSING"],
                 off["min_gamma"], off["counts"]["BOUNDARY_CROSSING"],
                 attributed, ref["counts"]["QP_INFEASIBLE"], verdict),
              dropped=dropped, min_gamma=drop["min_gamma"],
              crossings=drop["counts"]["BOUNDARY_CROSSING"],
              attributed=attributed, attribution_ok=attribution_ok,
              ref_crossings=ref["counts"]["BOUNDARY_CROSSING"])

    # ------------------------------------------------------------- P10.4
    # (a) the tau curve must match an *independent* RK4 integration of Eq.(8)
    #     driven by the recorded G(t); the loop itself uses forward Euler, so this
    #     checks the equation, not the integrator's identity with itself.
    G_hist = ref["G"]
    def _G(t):
        k = min(max(int(round(t / DT)), 0), len(G_hist) - 1)
        return float(G_hist[k])
    t_rk, tau_rk = TAU.rk4(EPS_TAU[0], _G, K_TAU, ref["t"][-1], DT)
    tau_err = float(np.max(np.abs(tau_rk[:len(ref["t"])] - ref["tau"][:, 0])))
    # (b) the recorded Gamma history must be reproducible from the recorded q
    gam_check = np.array([chain.pair_gamma(qq, i, j) for qq in ref["q"]])
    gam_err = float(np.max(np.abs(gam_check - ref["gam"])))
    rec.metric("tau_vs_independent_rk4", tau_err)
    rec.metric("gamma_history_recompute_err", gam_err)
    rec.metric("kkt_max_e2e", ref["kkt_max"])
    t08 = _load_task_metrics("T08")
    rec.metric("t08_reference", {"min_gamma": t08.get("min_gamma_raw_sca_on"),
                                 "crossings": t08.get("crossing_count_sca_on"),
                                 "crossings_off": t08.get("crossing_count_sca_off")})
    rec.check("P10.4", tau_err < 5e-2 and gam_err < 1e-9 and ref["kkt_max"] < 1e-8,
              "sub-task consistency: the e2e tau agrees with an independent RK4 integration "
              "of Eq.(8) (driven by the recorded G) to %.1e, the Gamma history is "
              "reproduced from "
              "the recorded joints to %.1e, and the per-step KKT residual stays at %.1e (T08 "
              "reported 8.3e-16 on its own fixture).  A pointwise Gamma(t) comparison against "
              "T08 is NOT meaningful -- different arms, task and horizon -- so only the "
              "criterion (crossings 0 on / > 0 off) is compared, and T08's numbers are reported "
              "for the record: min %.3f / %s / %s"
              % (tau_err, gam_err, ref["kkt_max"], t08.get("min_gamma_raw_sca_on", float("nan")),
                 t08.get("crossing_count_sca_on"), t08.get("crossing_count_sca_off")),
              tau_err=tau_err, gam_err=gam_err)

    # ------------------------------------------------------------- P10.5 / P10.6
    # Two accounts, and they do NOT have the same status (docs/DECISIONS.md D017):
    #
    # (a) the Theorem-3 identity *at the QP solution of each step*.  The active-set
    #     solution is the LVI fixed point, P(u - Mu - b) = u, so Y^T U = psi
    #     identically and Vdot = 0 at that instant.  `max |psi - Y^T U|` is the
    #     real self-consistency test of the (21a) assembly, and it is what P10.5
    #     gates on.
    # (b) the plan's telescoping ledger `int Y^T U dt - Delta V - int psi dt`.
    #     It cannot close here for a structural reason: `u` is re-solved from
    #     scratch every step, so the record is a sequence of fixed points of a
    #     *time-varying* LVI, not a trajectory of the autonomous flow (20).  The
    #     entire non-closure must then be exactly -Delta V, and that is
    #     falsifiable: `res + Delta V` is the accumulated identity residual and
    #     has to vanish (P10.6).
    dtv = ref["dt"]
    ytu = ref["ytu"]
    psi = ref["psi"]
    V = ref["V"]
    idres = ref["idres"]
    res_thm3 = float(np.sum(ytu) * dtv - (V[-1] - V[0]) - float(np.sum(psi) * dtv))
    scale_thm3 = float(np.sum(np.abs(ytu)) * dtv)
    unexplained = res_thm3 + float(V[-1] - V[0])
    idres_max = float(np.max(np.abs(idres))) if len(idres) else float("nan")
    idres_scale = float(np.max(np.abs(psi))) if len(psi) else float("nan")
    # (c) the plan's *other* variant: P_in = xdot^R . f with f the recovered task
    #     force and S = 1/2 ||tip separation||^2.  S is NOT the storage function of
    #     Theorem 3, so this ledger has no reason to close; it is reported to keep
    #     the number from ever being quoted as an energy balance.
    coh = 0.5 * (ref["sep"] ** 2)
    pin = ref["pin"]
    dS = float(coh[-1] - coh[0])
    ledger_plan = float(np.sum(pin) * dtv - dS - float(np.sum(psi) * dtv))
    scale_plan = float(np.sum(np.abs(pin)) * dtv)
    rec.metric("thm3_ledger_residual", res_thm3)
    rec.metric("thm3_ledger_scale", scale_thm3)
    rec.metric("thm3_dV", float(V[-1] - V[0]))
    rec.metric("thm3_unexplained", unexplained)
    rec.metric("thm3_idres_max", idres_max)
    rec.metric("thm3_idres_rel", idres_max / idres_scale if idres_scale > 0 else float("nan"))
    rec.metric("plan_ledger_residual", ledger_plan)
    rec.metric("plan_ledger_scale", scale_plan)
    rec.metric("plan_ledger_relative",
               ledger_plan / scale_plan if scale_plan > 0 else float("nan"))
    rec.metric("psi_integral", float(np.sum(psi) * dtv))
    rec.metric("V_final", float(V[-1]))
    rec.check("P10.5", np.isfinite(idres_max)
              and idres_max <= 1e-8 * max(1e-12, idres_scale),
              "Theorem-3 identity at every QP solution: max |psi - Y^T U| = %.3e against "
              "max psi = %.3e (relative %.1e).  The active-set solution satisfies "
              "P(u - Mu - b) = u, so Y^T U must collapse onto psi and Vdot onto 0 "
              "instantaneously; this is the (21a) assembly check, not a trajectory claim."
              % (idres_max, idres_scale, idres_max / idres_scale if idres_scale > 0 else float("nan")),
              idres_max=idres_max, idres_scale=idres_scale)
    rec.check("P10.6", np.isfinite(unexplained)
              and abs(unexplained) <= 1e-2 * max(1e-12, scale_thm3) + 1e-6,
              "the plan's Theorem-3 ledger does NOT close and the reason is fully accounted "
              "for: int Y^T U dt - Delta V - int psi dt = %.3e with Delta V = %.3e, so "
              "residual + Delta V = %.3e (%.2f%% of int|Y^T U| dt = %.3e).  Delta V is the "
              "quasi-static jump of the multiplier vector when the QP is re-solved, not a "
              "missing term: Theorem 3 governs the flow (20), and this loop replaces that "
              "flow by a sequence of fixed points of a time-varying LVI.  The other variant "
              "(P_in = xdot^R . f, S = 0.5||separation||^2) is reported and NOT gated: "
              "residual = %.3e (%.0f%% of its scale).  Neither number is an energy balance."
              % (res_thm3, float(V[-1] - V[0]), unexplained,
                 100 * abs(unexplained) / scale_thm3 if scale_thm3 > 0 else float("nan"),
                 scale_thm3, ledger_plan,
                 100 * abs(ledger_plan) / scale_plan if scale_plan > 0 else float("nan")),
              residual=res_thm3, dV=float(V[-1] - V[0]), unexplained=unexplained)

    # ------------------------------------------------------------- N10.2
    no_switch = (tau1["t_switch"] is None and tau0["t_switch"] is None)
    rec.metric("t_switch_tau1", tau1["t_switch"])
    rec.metric("t_switch_tau0", tau0["t_switch"])
    rec.defect("N10.2", no_switch,
               "pinning tau == 1 or tau == 0 removes the switch entirely (t_switch is None in "
               "both runs, against %s s with Eq.(8)): the asynchronous->synchronous transition "
               "is produced by the logistic field, not by a schedule" % _fmt(ref["t_switch"]),
               tau1=tau1["t_switch"], tau0=tau0["t_switch"])

    # ------------------------------------------------------------- N10.3
    sub = {t: _load_status(t) for t in ["T%02d" % k for k in (1, 2, 3, 4, 5, 6, 7, 8)]}
    all_pass = all(v == "PASS" for v in sub.values())
    gated = _gate_blocks_when_subtask_fails()
    rec.metric("subtask_status", sub)
    rec.defect("N10.3", all_pass and gated,
               "the end-to-end result is gated by the sub-tasks: on disk T01-T08 are %d/8 PASS, "
               "and run_all.evaluate_gates returns BLOCKED_BY_UPSTREAM for G4 when T08 is "
               "doctored to FAIL, so an e2e number can never paper over a failing sub-task"
               % sum(1 for v in sub.values() if v == "PASS"), subtasks=sub, gated=gated)

    # ------------------------------------------------------------- N10.4
    rec.metric("min_gamma_lambda0", lam0["min_gamma"])
    rec.metric("crossing_count_lambda0", lam0["counts"]["BOUNDARY_CROSSING"])
    rec.metric("infeasible_lambda0", lam0["counts"]["QP_INFEASIBLE"])
    moved = (abs(lam0["min_gamma"] - ref["min_gamma"]) > 1e-3
             or lam0["counts"]["BOUNDARY_CROSSING"] != ref["counts"]["BOUNDARY_CROSSING"]
             or lam0["counts"]["QP_INFEASIBLE"] != ref["counts"]["QP_INFEASIBLE"])
    rec.defect("N10.4", moved,
               "lambda = 0 changes the outcome: min_t Gamma_raw %.4f vs %.4f, crossings %d vs "
               "%d, infeasible steps %d vs %d.  The direction is NOT 'crossings rise' -- on this "
               "fixture the lambda = 0 cone stops the approach earlier, which is the same "
               "finding as T08/N8.2 (docs/DECISIONS.md D016)"
               % (lam0["min_gamma"], ref["min_gamma"],
                  lam0["counts"]["BOUNDARY_CROSSING"], ref["counts"]["BOUNDARY_CROSSING"],
                  lam0["counts"]["QP_INFEASIBLE"], ref["counts"]["QP_INFEASIBLE"]),
               min_gamma=lam0["min_gamma"])

    # ------------------------------------------------------------- N10.5
    rec.metric("min_gamma_dt_doubled", dt2["min_gamma"])
    rec.metric("t_switch_dt_doubled", dt2["t_switch"])
    dt_moved = (abs(dt2["min_gamma"] - ref["min_gamma"]) > 1e-3
                or dt2["t_switch"] != ref["t_switch"])
    rec.defect("N10.5", dt_moved,
               "dt doubled: min_t Gamma_raw %.4f -> %.4f and t_switch %s -> %s s, so the "
               "integration step is really in the loop and the reported numbers are not "
               "step-size independent"
               % (ref["min_gamma"], dt2["min_gamma"], _fmt(ref["t_switch"]),
                  _fmt(dt2["t_switch"])),
               min_gamma=dt2["min_gamma"], t_switch=dt2["t_switch"])

    # ------------------------------------------------------------ metrics
    sv = ref["solve_s"]
    rec.metric("solve_time_p50_ms", 1e3 * float(np.percentile(sv, 50)))
    rec.metric("solve_time_p99_ms", 1e3 * float(np.percentile(sv, 99)))
    rec.metric("qdot_sum_max", float(np.max(np.sum(
        (np.diff(ref["q"], axis=0) / ref["dt"]) ** 2, axis=1))))
    rec.metric("counts_sca_on", dict(ref["counts"]))
    rec.metric("counts_sca_off", dict(off["counts"]))
    rec.metric("n_steps", int(ref["q"].shape[0]))

    # ------------------------------------------------------------ figures
    _fig_triptych(rec, ref, i, j)
    _fig_phase(rec, ref)
    _fig_ablation(rec, ref, off, drop)
    return rec


# ---------------------------------------------------------------- figures
def _fig_triptych(rec, ref, i, j):
    fig, axs = plt.subplots(3, 1, figsize=(6.8, 6.4), sharex=True)
    axs[0].plot(ref["t"], ref["tau"][:, 0], label="$\\tau_1$", lw=1.4)
    axs[0].plot(ref["t"], ref["tau"][:, 1], label="$\\tau_2$", lw=1.0, ls="--")
    axs[0].axhline(0.5, color="k", ls=":", lw=0.9)
    if ref["t_switch"] is not None:
        axs[0].axvline(ref["t_switch"], color="#eb3b5a", lw=1.0)
    axs[0].set_ylabel("$\\tau$ (Eq.8)")
    axs[0].legend(fontsize=7)
    axs[0].set_title("asynchronous -> synchronous: $t_{switch}$ = %s s"
                     % _fmt(ref["t_switch"]))

    axs[1].plot(ref["t"], ref["gam"], color="#4b7bec", lw=1.4)
    axs[1].axhline(0.0, color="k", ls=":", lw=0.9)
    axs[1].set_ylabel("$\\Gamma_{raw}$ (%s-%s)"
                      % (LABELS[i], LABELS[j]))
    axs[1].set_title("learned boundary, SCA on: min %.3f" % ref["min_gamma"])

    axs[2].plot(ref["t"], 1e3 * ref["solve_s"], color="#20bf6b", lw=0.9)
    axs[2].set_ylabel("QP solve [ms]")
    axs[2].set_xlabel("t [s]")
    save(fig, rec, "t10_e2e_triptych.png")


def _fig_phase(rec, ref):
    fig, ax = plt.subplots(figsize=(5.8, 4.2))
    sc = ax.scatter(ref["sep"], ref["tau"][:, 0], c=ref["t"], s=8, cmap="viridis")
    ax.plot(ref["sep"][0], ref["tau"][0, 0], "o", color="#eb3b5a", ms=7, label="start")
    ax.plot(ref["sep"][-1], ref["tau"][-1, 0], "s", color="#000000", ms=6, label="end")
    if ref["t_switch"] is not None:
        k = int(np.argmin(np.abs(ref["tau"][:, 0] - 0.5)))
        ax.plot(ref["sep"][k], ref["tau"][k, 0], "*", color="#eb3b5a", ms=13,
                label="$t_{switch}$")
    fig.colorbar(sc, ax=ax, label="t [s]")
    ax.set_xlabel("tip separation [m]")
    ax.set_ylabel("$\\tau$")
    ax.set_title("phase portrait: where the switch lands")
    ax.legend(fontsize=7)
    save(fig, rec, "t10_phase.png")


def _fig_ablation(rec, ref, off, drop=None):
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    if drop is not None:
        ax.plot(drop["t"], drop["gam"], lw=1.2, color="#20bf6b", ls="--",
                label="SCA on, row dropped where infeasible")
    ax.plot(ref["t"], ref["gam"], lw=1.6, color="#4b7bec", label="SCA on (freeze)")
    ax.plot(off["t"], off["gam"], lw=1.4, color="#eb3b5a", label="SCA off")
    ax.axhline(0.0, color="k", ls=":", lw=1.0)
    ax.axhline(1.0, color="0.4", ls="-.", lw=0.9)
    idx = np.where(off["cross"])[0]
    if idx.size:
        ax.plot(off["t"][idx], off["gam"][idx], ".", color="#eb3b5a", ms=2,
                label="crossing (%d steps)" % idx.size)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("$\\Gamma_{raw}$")
    title = "SCA ablation: min %.3f (on) vs %.3f (off)" % (ref["min_gamma"], off["min_gamma"])
    if drop is not None:
        title += "\nrow dropped on infeasible steps: min %.3f" % drop["min_gamma"]
    ax.set_title(title, fontsize=9)
    ax.legend(fontsize=7)
    save(fig, rec, "t10_sca_ablation.png")


# ---------------------------------------------------------------- helpers
def _fmt(v):
    return "n/a" if v is None else "%.3f" % v


def _load_status(tid):
    import json
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "evidence", "impl_checks", tid + ".json")
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh).get("status", "MISSING")
    except OSError:
        return "MISSING"


def _load_task_metrics(tid):
    import json
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "evidence", "impl_checks", tid + ".json")
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh).get("metrics", {})
    except OSError:
        return {}


def _gate_blocks_when_subtask_fails():
    """Prove the N10.3 gate by feeding `evaluate_gates` a doctored result set."""
    try:
        import run_all
    except Exception:
        return False
    fake = {t: {"status": "PASS"} for t in ["T%02d" % k for k in range(1, 11)]}
    ok_g4 = run_all.evaluate_gates(fake)["G4"]["status"]
    fake["T08"] = {"status": "FAIL"}
    bad_g4 = run_all.evaluate_gates(fake)["G4"]["status"]
    return ok_g4 == "PASS" and bad_g4 == "BLOCKED_BY_UPSTREAM"
