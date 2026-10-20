#!/usr/bin/env python3
"""P3-T04 validation driver — full torque law, Eq.(27).

Positive: independent loop oracle; term decomposition; push-axis exclusion of
the position term; virtual work; affine/linear response in w; gravity/friction/
damping independence; singular-J acceptance.
Negative/mutation: sign flip, transposed frame, missing selector, dropped
gravity, dropped damping, and an injected measured-force feedback term are all
detected against the source law.

Run:  /usr/bin/python3.10 p3/tools/run_t04_torque.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "p3"))

from baselines.p3_peg_in_hole import control as ctl     # noqa: E402
from baselines.p3_peg_in_hole import fixtures as fx     # noqa: E402
from oracles import oracle_control as oc                # noqa: E402

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S") + "_P3-T04_torque"
OUT = ROOT / "results" / RUN_ID
OUT.mkdir(parents=True, exist_ok=True)
FIG = ROOT / "p3" / "evidence" / "figures"


def rot(axis, deg):
    a = np.deg2rad(deg); c, s = np.cos(a), np.sin(a)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


R_H = rot("z", 30.0) @ rot("y", 15.0)
CHECKS = []


def check(cid, desc, ok, residual=None, unit="", note=""):
    CHECKS.append({"id": cid, "desc": desc, "pass": bool(ok), "residual": residual,
                   "unit": unit, "note": note})
    r = f"  {residual:.3e} {unit}" if isinstance(residual, (int, float)) else (
        f"  {residual}" if residual else "")
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {desc}{r}")


def maxdiff(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


rng = np.random.default_rng(20261019)
n = 7
J = fx.jacobian(n)
Kp = fx.gains("peg")
D = fx.damping(n)
tau_g = fx.gravity(n)
tau_f = fx.friction(n)
dx = rng.normal(size=6) * 1e-3
w = np.array([2.0, -1.0, 10.0, 0.1, -0.2, 0.3])
qdot = rng.normal(size=n) * 0.05

terms = ctl.torque_terms(J, R_H, Kp, dx, w, D, qdot, tau_g, tau_f)
tau = terms["tau"]
tau_ref = oc.torque(J, R_H, Kp, dx, w, D, qdot, tau_g, tau_f)

check("T04_01", "Eq.(27) vs independent index-loop oracle (random state)",
      maxdiff(tau, tau_ref) < 1e-12, maxdiff(tau, tau_ref), "N*m")

# ---------------------------------------------------------------- decomposition
Sel = ctl.position_selector(R_H)
F_pos_ref = Sel @ (Kp @ dx)
F_pert_ref = ctl.wrench_rotation(R_H) @ w
decomp = (maxdiff(terms["F_pos"], F_pos_ref) + maxdiff(terms["F_pert"], F_pert_ref)
          + maxdiff(terms["tau_pos"], J.T @ F_pos_ref)
          + maxdiff(terms["tau_pert"], J.T @ F_pert_ref)
          + maxdiff(terms["tau_damp"], -D @ qdot)
          + maxdiff(terms["tau"], terms["tau_pos"] + terms["tau_pert"]
                    + terms["tau_damp"] + tau_g + tau_f))
check("T04_02", "term-by-term decomposition: position, perturbation, damping, gravity, friction",
      decomp < 1e-13, decomp, "N*m")

# printed form has two J^T terms; verify the combined form is identical
tau_two_terms = J.T @ (Sel @ (Kp @ dx)) + J.T @ (ctl.wrench_rotation(R_H) @ w) \
    - D @ qdot + tau_g + tau_f
check("T04_03", "two-J^T printed form == combined J^T(F_pos+F_pert) form",
      maxdiff(tau, tau_two_terms) < 1e-13, maxdiff(tau, tau_two_terms), "N*m")

# ---------------------------------------------------------------- push-axis exclusion
n_ax = R_H @ np.array([1.0, 0.0, 0.0])
res_axis = float(abs(n_ax @ terms["F_pos"][:3]))
dx_along = dx + 0.05 * np.r_[n_ax, np.zeros(3)]
tau_shift = ctl.arm_torque(J, R_H, Kp, dx_along, w, D, qdot, tau_g, tau_f)
res_invariance = maxdiff(tau_shift, tau)
check("T04_04", "position term has no component along the push axis R_h e_x",
      res_axis < 1e-12, res_axis, "N")
check("T04_05", "dx shifted along the push axis does not change tau (axis excluded)",
      res_invariance < 1e-12, res_invariance, "N*m")

# ---------------------------------------------------------------- virtual work
Jq = J @ qdot
F_task = terms["F_pos"] + terms["F_pert"]
lhs = float((J.T @ F_task) @ qdot)
rhs = float(F_task @ Jq)
check("T04_06", "virtual work: (J^T F)^T qdot = F^T (J qdot)",
      abs(lhs - rhs) < 1e-12 * max(1.0, abs(lhs)), abs(lhs - rhs), "W",
      note=f"lhs={lhs:.6f} rhs={rhs:.6f}")

# ---------------------------------------------------------------- affine response
w1 = rng.normal(size=6); w2 = rng.normal(size=6)
t0 = ctl.arm_torque(J, R_H, Kp, dx, np.zeros(6), D, qdot, tau_g, tau_f)
t1 = ctl.arm_torque(J, R_H, Kp, dx, w1, D, qdot, tau_g, tau_f)
t2 = ctl.arm_torque(J, R_H, Kp, dx, w2, D, qdot, tau_g, tau_f)
t12 = ctl.arm_torque(J, R_H, Kp, dx, w1 + w2, D, qdot, tau_g, tau_f)
affine = maxdiff((t12 - t0), (t1 - t0) + (t2 - t0))
check("T04_07", "affine response to the feedforward wrench for fixed state",
      affine < 1e-12, affine, "N*m")
scale = maxdiff((ctl.arm_torque(J, R_H, Kp, dx, 3.7 * w1, D, qdot, tau_g, tau_f) - t0),
                3.7 * (t1 - t0))
check("T04_08", "homogeneous scaling in w (tau(cw)-tau(0) = c(tau(w)-tau(0)))",
      scale < 1e-12, scale, "N*m")

# ---------------------------------------------------------------- additive channels
dg = rng.normal(size=n) * 0.1
df = rng.normal(size=n) * 0.1
t_g = ctl.arm_torque(J, R_H, Kp, dx, w, D, qdot, tau_g + dg, tau_f)
t_f = ctl.arm_torque(J, R_H, Kp, dx, w, D, qdot, tau_g, tau_f + df)
check("T04_09", "gravity compensation enters additively and independently",
      maxdiff(t_g - tau, dg) < 1e-13, maxdiff(t_g - tau, dg), "N*m")
check("T04_10", "friction compensation enters additively and independently",
      maxdiff(t_f - tau, df) < 1e-13, maxdiff(t_f - tau, df), "N*m")

# ---------------------------------------------------------------- singular J
Js = fx.singular_jacobian()
tau_s = ctl.arm_torque(Js, R_H, Kp, dx, w, D, qdot, tau_g, tau_f)
Fs = ctl.position_selector(R_H) @ (Kp @ dx) + ctl.wrench_rotation(R_H) @ w
vw_s = abs(float((Js.T @ Fs) @ qdot) - float(Fs @ (Js @ qdot)))
check("T04_11", "rank-deficient J: tau finite and virtual work still exact",
      np.isfinite(tau_s).all() and vw_s < 1e-12, vw_s, "W",
      note=f"rank={np.linalg.matrix_rank(Js)} |tau|={np.linalg.norm(tau_s):.3f} N*m")

# ---------------------------------------------------------------- no feedback
# Structural: the public API has no force-input parameter.
import inspect  # noqa: E402
sig = inspect.signature(ctl.arm_torque)
params = list(sig.parameters)
no_fb_api = not any("force" in p or "f_ext" in p or "wrench_meas" in p for p in params)
check("T04_12", "API carries no measured-force input (paper: no force feedback term)",
      no_fb_api, f"params={params}")

# Behavioural: the source law equals the oracle *without* any feedback term; an
# implementation that added K_f * F_ext would deviate by exactly that term.
Kf = 0.02
F_ext = np.array([3.0, -2.0, 1.0, 0.05, 0.02, -0.01])
tau_with_fb = tau + J.T @ (Kf * F_ext)
fb_delta = maxdiff(tau_with_fb, tau_ref)
check("T04_13", "mut: injected force feedback is detected as a source-law deviation",
      fb_delta > 1e-6, fb_delta, "N*m",
      note="the implemented law contains no such term (T04_12)")

# ---------------------------------------------------------------- mutations
def detected(mut_tau):
    return maxdiff(mut_tau, tau_ref) > 1e-9


mut_sign = J.T @ F_pos_ref - J.T @ F_pert_ref - D @ qdot + tau_g + tau_f
check("T04_M1", "mut: sign flip on the perturbation term detected",
      detected(mut_sign), maxdiff(mut_sign, tau_ref), "N*m")

WR_wrong = ctl.wrench_rotation(R_H.T)
mut_frame = J.T @ F_pos_ref + J.T @ (WR_wrong @ w) - D @ qdot + tau_g + tau_f
check("T04_M2", "mut: transposed wrench frame detected",
      detected(mut_frame), maxdiff(mut_frame, tau_ref), "N*m")

mut_nosel = J.T @ (Kp @ dx) + J.T @ F_pert_ref - D @ qdot + tau_g + tau_f
check("T04_M3", "mut: missing selector (position control on all 6 axes) detected",
      detected(mut_nosel), maxdiff(mut_nosel, tau_ref), "N*m")

mut_nog = J.T @ F_pos_ref + J.T @ F_pert_ref - D @ qdot + tau_f
check("T04_M4", "mut: dropped gravity compensation detected",
      detected(mut_nog), maxdiff(mut_nog, tau_ref), "N*m")

mut_nod = J.T @ F_pos_ref + J.T @ F_pert_ref + tau_g + tau_f
check("T04_M5", "mut: dropped damping term detected",
      detected(mut_nod), maxdiff(mut_nod, tau_ref), "N*m")

mut_swap = J.T @ (np.block([[np.zeros((3, 3)), np.eye(3)],
                            [np.eye(3), np.zeros((3, 3))]]) @ F_pos_ref) \
    + J.T @ F_pert_ref - D @ qdot + tau_g + tau_f
check("T04_M6", "mut: force/moment blocks swapped in the position command detected",
      detected(mut_swap), maxdiff(mut_swap, tau_ref), "N*m")

# ---------------------------------------------------------------- gain anchor
kp_hole = fx.TEST_FIXTURE["k_p_hole_translation_N_m"]
check("T04_14", "hole-arm translation gain inside the paper's stated 500 <= k_p <= 1000",
      500.0 <= kp_hole <= 1000.0, kp_hole, "N/m",
      note="only paper-provided numeric anchor; peg-arm gains are TEST_FIXTURE")

passes = sum(1 for c in CHECKS if c["pass"])
total = len(CHECKS)

# ---------------- figures
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.2))
labels = ["tau_pos", "tau_pert", "tau_damp", "tau_grav", "tau_fric"]
stack = np.vstack([terms["tau_pos"], terms["tau_pert"], terms["tau_damp"],
                   terms["tau_gravity"], terms["tau_friction"]])
bottom = np.zeros(n)
colors = ["#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756"]
for row, lab, col in zip(stack, labels, colors):
    ax[0].bar(np.arange(n), row, bottom=bottom, label=lab + " [N$\\cdot$m]", color=col)
    bottom += row
ax[0].plot(np.arange(n), tau, "k.", ms=7, label="total $\\tau$")
ax[0].set_xlabel("joint index"); ax[0].set_ylabel("torque [N$\\cdot$m]")
ax[0].set_title("Eq.(27) term decomposition (TEST_FIXTURE state)")
ax[0].legend(fontsize=6, ncol=2); ax[0].grid(alpha=0.3, axis="y")

trials = 300
errs, affine_errs = [], []
for k in range(trials):
    Jk = np.hstack([np.eye(6), (rng.normal(size=6) * 0.2).reshape(6, 1)])
    qk = rng.normal(size=7) * 0.1
    wk = rng.normal(size=6)
    Fk = ctl.position_selector(R_H) @ (Kp @ dx) + ctl.wrench_rotation(R_H) @ wk
    errs.append(abs(float((Jk.T @ Fk) @ qk) - float(Fk @ (Jk @ qk))))
    a1 = ctl.arm_torque(Jk, R_H, Kp, dx, wk, D, qk, tau_g, tau_f)
    a2 = ctl.arm_torque(Jk, R_H, Kp, dx, 2 * wk, D, qk, tau_g, tau_f)
    a0 = ctl.arm_torque(Jk, R_H, Kp, dx, np.zeros(6), D, qk, tau_g, tau_f)
    affine_errs.append(maxdiff(a2 - a0, 2 * (a1 - a0)))
ax[1].semilogy(np.maximum(errs, 1e-18), lw=0.9, label="virtual-work residual [W]")
ax[1].semilogy(np.maximum(affine_errs, 1e-18), lw=0.9, label="affine-response residual [N$\\cdot$m]")
ax[1].set_xlabel("random trial"); ax[1].set_ylabel("residual")
ax[1].set_title(f"{trials} random states: identities hold to machine precision")
ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
fig.suptitle("P3-T04 torque law validation, Eq.(27)")
fig.tight_layout()
fig.savefig(FIG / "p3_t04_terms.png", dpi=160)
plt.close(fig)

result = {
    "task": "P3-T04",
    "kind": "torque_law",
    "paper_equations": ["27"],
    "run_id": RUN_ID,
    "state_fixture": {"note": "TEST_FIXTURE state and gains; no paper numeric values exist",
                      "J_shape": list(J.shape), "dx": dx.tolist(), "w": w.tolist()},
    "checks": CHECKS,
    "summary": {"pass": passes, "total": total,
                "verdict": "PASS" if passes == total else "FAIL"},
    "figures": ["p3/evidence/figures/p3_t04_terms.png"],
}
(OUT / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\n{passes}/{total} PASS  -> {OUT/'results.json'}")
sys.exit(0 if passes == total else 1)
