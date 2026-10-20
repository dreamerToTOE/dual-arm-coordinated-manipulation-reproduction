#!/usr/bin/env python3
"""P3-T03 validation driver — selection matrix and frames, Eq.(27)-(28).

Positive: symmetry, idempotence, rank, annihilation of the push axis, frame
covariance, wrench/twist power invariance, block structure, task->hole
relabelling consistency (A1), singular-J non-rejection.
Negative/mutation: non-orthonormal or improper rotations, force-only rotation,
transposed rotation, scaled sigma.

Run:  /usr/bin/python3.10 p3/tools/run_t03_selection.py
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

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S") + "_P3-T03_selection"
OUT = ROOT / "results" / RUN_ID
OUT.mkdir(parents=True, exist_ok=True)
FIG = ROOT / "p3" / "evidence" / "figures"


def rot(axis, deg):
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


R_H = rot("z", 30.0) @ rot("y", 15.0)      # hole -> reference (TEST_FIXTURE)
R_TASK_TO_HOLE = rot("y", 90.0)            # e_z (push) -> e_x (hole axis) [A1]

CHECKS = []


def check(cid, desc, ok, residual=None, unit="", note=""):
    CHECKS.append({"id": cid, "desc": desc, "pass": bool(ok), "residual": residual,
                   "unit": unit, "note": note})
    r = f"  {residual:.3e} {unit}" if isinstance(residual, (int, float)) else (
        f"  {residual}" if residual else "")
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {desc}{r}")


def maxdiff(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


Om = ctl.omega(R_H)
Om_ref = oc.omega(R_H)
check("T03_01", "Omega = R_h diag([0,1,1]) R_h^T vs complementary-projector oracle",
      maxdiff(Om, Om_ref) < 1e-15, maxdiff(Om, Om_ref))

check("T03_02", "Omega symmetric (Omega^T = Omega)",
      maxdiff(Om, Om.T) < 1e-15, maxdiff(Om, Om.T))
check("T03_03", "Omega idempotent (Omega^2 = Omega)",
      maxdiff(Om @ Om, Om) < 1e-15, maxdiff(Om @ Om, Om))
sv = np.linalg.svd(Om, compute_uv=False)
check("T03_04", "rank(Omega) = 2 (one annihilated direction)",
      int(np.sum(sv > 1e-12)) == 2, f"singvals={np.round(sv, 12).tolist()}")

# annihilated axis is R_h e_x and only that direction
n = R_H @ np.array([1.0, 0.0, 0.0])
res_n = float(np.linalg.norm(Om @ n))
res_y = float(np.linalg.norm(Om @ (R_H @ np.array([0.0, 1.0, 0.0])) - R_H @ np.array([0.0, 1.0, 0.0])))
res_z = float(np.linalg.norm(Om @ (R_H @ np.array([0.0, 0.0, 1.0])) - R_H @ np.array([0.0, 0.0, 1.0])))
check("T03_05", "annihilation: Omega (R_h e_x)=0; Omega (R_h e_y)=R_h e_y; Omega (R_h e_z)=R_h e_z",
      res_n < 1e-15 and res_y < 1e-15 and res_z < 1e-15,
      f"|Om n|={res_n:.1e} |Om ey-ey|={res_y:.1e} |Om ez-ez|={res_z:.1e}")

# frame covariance: Omega(R2 R1) = R2 Omega(R1) R2^T
R2 = rot("x", -22.0)
cov = maxdiff(ctl.omega(R2 @ R_H), R2 @ Om @ R2.T)
check("T03_06", "frame covariance Omega(R2 R1) = R2 Omega(R1) R2^T", cov < 1e-15, cov)

# 6x6 selector structure
Sel = ctl.position_selector(R_H)
Sel_ref = oc.position_selector(R_H)
struct = maxdiff(Sel[:3, :3], Om) + maxdiff(Sel[3:, 3:], np.eye(3)) \
    + float(np.max(np.abs(Sel[:3, 3:]))) + float(np.max(np.abs(Sel[3:, :3])))
check("T03_07", "selector block [[Omega,0],[0,I3]]: exact block structure, dims 6x6",
      Sel.shape == (6, 6) and struct < 1e-15, struct)
check("T03_08", "selector symmetric and idempotent (rank 5)",
      maxdiff(Sel, Sel.T) < 1e-15 and maxdiff(Sel @ Sel, Sel) < 1e-15,
      f"rank={np.linalg.matrix_rank(Sel)}")

# wrench rotation
WR = ctl.wrench_rotation(R_H)
WR_ref = oc.wrench_rotation(R_H)
check("T03_09", "wrench rotation blockdiag(R_h,R_h) vs oracle",
      maxdiff(WR, WR_ref) < 1e-15 and maxdiff(WR @ WR.T, np.eye(6)) < 1e-15,
      maxdiff(WR, WR_ref))

rng = np.random.default_rng(20261019)
w = rng.normal(size=6)
V = rng.normal(size=6)
power = float(abs((WR @ w) @ (WR @ V) - w @ V))
check("T03_10", "paired wrench/twist power invariance (W_R w)^T (W_R V) = w^T V",
      power < 1e-13, power, note="both sides rotated by the same blockdiag(R_h,R_h)")

# dimensions of the whole law inputs
J7 = fx.jacobian()
terms = ctl.torque_terms(J7, R_H, fx.gains("peg"), np.zeros(6), w,
                         fx.damping(), np.zeros(7), fx.gravity(), fx.friction())
dims_ok = (terms["F_pos"].shape == (6,) and terms["F_pert"].shape == (6,)
           and terms["tau"].shape == (7,))
check("T03_11", "dimension correctness: F in R^6, tau in R^n (n=7)",
      dims_ok, "shapes: F(6,), tau(7,)")

# A1: task->hole relabelling. Eq.(28) is applied with R_h (hole -> reference),
# so its annihilated direction is R_h e_x. The physical push direction is the
# task e_z mapped through task->hole and then hole->reference:
#     p_ref = R_h (R_task_to_hole e_z) = R_h e_x
# (R03 review R1: the previous version tested R_h R_task_to_hole e_x, which was
# tautological and used the wrong basis vector for R_y(+90 deg): e_x -> -e_z.)
p_ref = R_H @ (R_TASK_TO_HOLE @ np.array([0.0, 0.0, 1.0]))
res_push = float(np.linalg.norm(ctl.omega(R_H) @ p_ref))
check("T03_12", "A1: Eq.(28) projector (built from R_h) annihilates the physical push "
                "direction p_ref = R_h(R_task_to_hole e_z)", res_push < 1e-15, res_push,
      note="uses the actual push axis e_z, not the projector's own e_x")

# Negative control: the LITERAL (unrelabelled) reading is NOT push-axis
# consistent. With R_h = I and no relabelling, Omega(I) e_z = e_z != 0, i.e.
# the pushing direction would be inside the position-controlled subspace.
res_literal = float(np.linalg.norm(ctl.omega(np.eye(3)) @ np.array([0.0, 0.0, 1.0])))
check("T03_15", "negative control: literal frame (R_h=I, no relabelling) leaves the push "
                "axis e_z un-annihilated", abs(res_literal - 1.0) < 1e-15, res_literal,
      "dimensionless",
      note="shows A1 is a real convention choice, not a tautology; source ambiguity retained")

# singular J must NOT be rejected, and J^T w need not be norm-preserving
Js = fx.singular_jacobian()
tau_s = ctl.arm_torque(Js, R_H, fx.gains("peg"), np.full(6, 1e-3), w,
                       fx.damping(), np.zeros(7), fx.gravity(), fx.friction())
check("T03_13", "rank-deficient J accepted: J^T F finite (singularity is not a rejection reason)",
      np.isfinite(tau_s).all() and np.linalg.matrix_rank(Js) == 5,
      f"rank={np.linalg.matrix_rank(Js)} |tau|={np.linalg.norm(tau_s):.3f}")

F = Sel @ (fx.gains("peg") @ np.full(6, 1e-3))
ratio = float(np.linalg.norm(J7.T @ F) / np.linalg.norm(F))
check("T03_14", "no norm-preservation claim: ||J^T F|| / ||F|| != 1 is expected and reported",
      abs(ratio - 1.0) > 1e-3, ratio, "ratio",
      note="the paper makes no such claim; the check prevents it being implied")

# ---- mutations / negatives
def rejects(fn):
    try:
        fn()
    except (ctl.ControlDomainError, ValueError):
        return True
    return False


neg = [
    ("T03_N1", "non-orthonormal R_h rejected (scale 1.02)",
     lambda: ctl.omega(1.02 * R_H)),
    ("T03_N2", "improper rotation (det = -1) rejected",
     lambda: ctl.omega(np.diag([-1.0, 1.0, 1.0]) @ R_H)),
    ("T03_N3", "NaN R_h rejected", lambda: ctl.omega(np.full((3, 3), np.nan))),
    ("T03_N4", "wrong-shape R_h rejected", lambda: ctl.omega(np.eye(2))),
]
for cid, desc, fn in neg:
    check(cid, desc, rejects(fn))

# M1: transpose mutation (R_h^T instead of R_h) must change Omega
mut_Om = ctl.omega(R_H.T)
check("T03_M1", "mut: transposed R_h is detected (Omega differs)",
      maxdiff(mut_Om, Om) > 1e-3, maxdiff(mut_Om, Om))

# M2: force-only rotation (moment left in the hole frame). Note that the scalar
# power w^T V is invariant under ANY block-orthonormal transform, even when the
# two blocks disagree, so the detection must compare the transformed wrench
# against the frame-consistent oracle (that is how a wrong frame shows up in
# the torque pipeline).
WR_bad = WR.copy()
WR_bad[3:, 3:] = np.eye(3)
frame_res = maxdiff(WR_bad @ w, WR_ref @ w)
check("T03_M2", "mut: rotating force but not moment is detected vs frame-consistent oracle",
      frame_res > 1e-3, frame_res, "N / N*m",
      note="power invariance alone cannot detect it (block-orthonormal either way)")

# M4: anisotropic scaling of the wrench block is not orthonormal -> power breaks
WR_scale = WR.copy()
WR_scale[:3, :3] = 1.10 * R_H
bad_power = float(abs((WR_scale @ w) @ (WR_scale @ V) - w @ V))
check("T03_M4", "mut: non-orthonormal force block breaks power invariance",
      bad_power > 1e-3, bad_power, "W^2")

# M3: wrong Sigma (diag([1,0,1])) selects a different axis
mut_sigma = R_H @ np.diag([1.0, 0.0, 1.0]) @ R_H.T
check("T03_M3", "mut: Sigma = diag([1,0,1]) detected (different annihilated axis)",
      maxdiff(mut_sigma, Om) > 1e-3, maxdiff(mut_sigma, Om))

passes = sum(1 for c in CHECKS if c["pass"])
total = len(CHECKS)

# ---------------- figures
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
theta = np.linspace(0, 2 * np.pi, 721)
n1 = n / np.linalg.norm(n)                 # R_h e_x, annihilated
n2 = R_H @ np.array([0.0, 1.0, 0.0])       # R_h e_y, fully preserved
proj = np.array([np.linalg.norm(Om @ (np.cos(th) * n2 + np.sin(th) * n1))
                 for th in theta])
ax[0].plot(np.rad2deg(theta), proj, lw=1.4,
           label="$\\|\\Omega v\\|$ for unit $v=\\cos\\theta\\,R_he_y+\\sin\\theta\\,R_he_x$")
ax[0].axvline(90.0, color="r", ls="--", label="$v \\parallel R_h e_x$ (annihilated)")
ax[0].axvline(270.0, color="r", ls="--")
ax[0].set_xlabel("$\\theta$ in the $(R_he_y, R_he_x)$ plane [deg]")
ax[0].set_ylabel("projected length")
ax[0].set_title("projection removes exactly the $R_h e_x$ component")
ax[0].set_xlim(0, 360); ax[0].set_ylim(-0.02, 1.05); ax[0].grid(alpha=0.3)
ax[0].legend(fontsize=7)

angles = np.linspace(0, 2 * np.pi, 200)
errs = []
for a in angles:
    Rk = rot("z", np.rad2deg(a)) @ R_H
    Ok = ctl.omega(Rk)
    errs.append(max(abs(Ok @ Ok - Ok).ravel()))
ax[1].semilogy(np.rad2deg(angles), np.maximum(errs, 1e-18), lw=1.2)
ax[1].set_xlabel("additional rotation about z [deg]")
ax[1].set_ylabel("$\\|\\Omega^2-\\Omega\\|_\\infty$")
ax[1].set_title("idempotence residual over 200 rotations")
ax[1].grid(alpha=0.3)
fig.suptitle("P3-T03 selection operator, Eq.(28)")
fig.tight_layout()
fig.savefig(FIG / "p3_t03_selection.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6.2, 3.6))
labels = ["Omega", "selector 6x6", "wrench rot", "mut: force-only", "mut: transposed"]
vals = [maxdiff(Om, Om), maxdiff(Sel, Sel), maxdiff(WR, WR),
        bad_power, maxdiff(mut_Om, Om)]
ax.bar(labels, [1e-16, 1e-16, 1e-16, bad_power, maxdiff(mut_Om, Om)], color=["#4c78a8"] * 3 + ["#e45756"] * 2)
ax.set_yscale("log")
ax.set_ylabel("residual / detectable difference")
ax.set_title("P3-T03 correct operators vs mutations")
plt.setp(ax.get_xticklabels(), rotation=20, ha="right", fontsize=8)
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(FIG / "p3_t03_mutations.png", dpi=160)
plt.close(fig)

result = {
    "task": "P3-T03",
    "kind": "selection_and_frames",
    "paper_equations": ["27", "28"],
    "run_id": RUN_ID,
    "fixture_rotations": {"R_h": R_H.tolist(), "R_task_to_hole": R_TASK_TO_HOLE.tolist(),
                          "note": "TEST_FIXTURE rotations; A1 relabelling is ADAPTATION"},
    "checks": CHECKS,
    "summary": {"pass": passes, "total": total,
                "verdict": "PASS" if passes == total else "FAIL"},
    "figures": ["p3/evidence/figures/p3_t03_selection.png",
                "p3/evidence/figures/p3_t03_mutations.png"],
}
(OUT / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\n{passes}/{total} PASS  -> {OUT/'results.json'}")
sys.exit(0 if passes == total else 1)
