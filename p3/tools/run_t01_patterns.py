#!/usr/bin/env python3
"""P3-T01 validation driver — perturbation patterns, Eq.(16)-(22).

Positive: analytic spot checks against p3/oracles/oracle_patterns.py (scalar
closed forms), time-domain invariants, axis/unit placement.
Negative: non-finite / wrong-shape rejection, and mutation tests where the
*checker* must fail on a deliberately mutated pattern (swapped phase/frequency/
amplitude, phase on the wrong axis).

Run:  /usr/bin/python3.10 p3/tools/run_t01_patterns.py
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

from baselines.p3_peg_in_hole import fixtures as fx          # noqa: E402
from baselines.p3_peg_in_hole import patterns as pat        # noqa: E402
from oracles import oracle_patterns as op                   # noqa: E402

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S") + "_P3-T01_patterns"
OUT = ROOT / "results" / RUN_ID
OUT.mkdir(parents=True, exist_ok=True)
FIG = ROOT / "p3" / "evidence" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

F = fx.TEST_FIXTURE
CHECKS = []


def check(cid, desc, ok, residual=None, unit="", note=""):
    CHECKS.append({"id": cid, "desc": desc, "pass": bool(ok),
                   "residual": residual, "unit": unit, "note": note})
    r = f"  {residual:.3e} {unit}" if isinstance(residual, (int, float)) else (
        f"  {residual}" if residual else "")
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {desc}{r}")


def maxdiff(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


# ---------------------------------------------------------------- production
P = fx.pattern_set()
T_SPOT = (0.0, 0.13, 0.37, 1.0, 2.5, 7.25)

# oracle parameters mirror the fixture (explicitly, not by importing objects)
ORACLE_PARAMS = {
    "push": {"f_push": F["f_push_N"]},
    "rub": {"f_rub": F["f_rub_Nm"], "v_rub": F["v_rub_rad_s"]},
    "wiggle": {"f_wiggle": F["f_wiggle_Nm"], "v_wiggle": F["v_wiggle_rad_s"]},
    "spiral": {"alpha": F["alpha_N"], "beta": F["beta_N"], "v_spiral": F["v_spiral_rad_s"]},
}

# ---------------------------------------------------------------- T01_01..04
for cid, name in (("T01_01", "push"), ("T01_02", "rub"),
                  ("T01_03", "wiggle"), ("T01_04", "spiral")):
    worst = 0.0
    for t in T_SPOT:
        worst = max(worst, maxdiff(P[name].wrench(t), op.ORACLES[name](t, ORACLE_PARAMS[name])))
    check(cid, f"{name}: wrench(t) vs independent scalar closed form at "
               f"{len(T_SPOT)} sample times", worst < 1e-14, worst, "N / N*m")

# ---------------------------------------------------------------- T01_05
rng = np.random.default_rng(20261019)
a = rng.normal(size=6); b = rng.normal(size=6); c = rng.normal(size=6); d = rng.normal(size=6)
gp = pat.GeneralPattern(a, b, c, d)
worst = max(maxdiff(gp.wrench(t), op.general(t, a, b, c, d)) for t in T_SPOT)
check("T01_05", "Eq.(18) general form vs independent per-component loop",
      worst < 1e-14, worst, "mixed N / N*m")

# ---------------------------------------------------------------- T01_06..10
grid = np.linspace(0.0, 12.0, 6001)
push_series = np.array([P["push"].wrench(t) for t in grid])
check("T01_06", "push is constant in time (a=b=c=0, Eq.19)",
      float(np.max(np.abs(push_series - push_series[0]))) < 1e-15,
      float(np.max(np.abs(push_series - push_series[0]))), "N")

# rub: zero mean over integer periods (T = 2*pi/v)
v_rub = F["v_rub_rad_s"]; period = 2 * np.pi / v_rub
n_per = 20
t_r = np.linspace(0.0, n_per * period, 20001, endpoint=False)
w_r = np.array([P["rub"].wrench(t)[5] for t in t_r])
check("T01_07", "rub: moment mean over 20 integer periods is zero",
      abs(float(np.trapz(w_r, t_r)) / (n_per * period)) < 1e-6,
      abs(float(np.trapz(w_r, t_r)) / (n_per * period)), "N*m")

wig = np.array([P["wiggle"].wrench(t) for t in grid])
quad = np.max(np.abs(wig[:, 3] ** 2 + wig[:, 4] ** 2 - F["f_wiggle_Nm"] ** 2))
check("T01_08", "wiggle: w4^2 + w5^2 = f_wiggle^2 (exact quadrature, c5=pi/2)",
      quad < 1e-15, float(quad), "N^2*m^2")

spr = np.array([P["spiral"].wrench(t) for t in grid])
fsp = np.array([F["alpha_N"] * np.sin(F["v_spiral_rad_s"] * t) + F["beta_N"] for t in grid])
rad = np.max(np.abs(np.hypot(spr[:, 0], spr[:, 1]) - np.abs(fsp)))
check("T01_09", "spiral: instantaneous radius sqrt(w1^2+w2^2) = |f_spiral(t)|",
      rad < 1e-13, float(rad), "N")

amp = np.array([P["spiral"].amplitude(t) for t in grid])
mod = np.max(np.abs(amp[:, 0] - fsp)) + np.max(np.abs(amp[:, 1] - fsp))
check("T01_10", "spiral: amplitude modulation a1 = a2 = alpha sin(vt) + beta",
      mod < 1e-15, float(mod), "N")

# ---------------------------------------------------------------- T01_11..12
const = pat.GeneralPattern(np.ones(6), np.zeros(6), np.zeros(6), np.arange(6.0))
same = max(maxdiff(const.wrench(t), np.arange(6.0)) for t in T_SPOT)
check("T01_11", "b = 0 is a legal constant mode (not an error)",
      same < 1e-15, same, "mixed")

neg_beta = pat.Spiral(1.0, -2.0, 2.0 * np.pi * 0.5)
nb = max(abs(np.linalg.norm(neg_beta.wrench(t)[:2]) -
             abs(1.0 * np.sin(2.0 * np.pi * 0.5 * t) - 2.0)) for t in T_SPOT)
check("T01_12", "beta < 0 accepted (no paper-specified positivity domain)",
      nb < 1e-13 and np.isfinite(neg_beta.wrench(0.3)).all(), float(nb), "N",
      note="radius sign flips; pattern stays finite")

# ---------------------------------------------------------------- negatives
def rejects(fn):
    try:
        fn()
    except (pat.PatternDomainError, ValueError):
        return True
    return False

neg_cases = [
    ("T01_N1", "NaN amplitude rejected",
     lambda: pat.Push(float("nan"))),
    ("T01_N2", "inf frequency rejected",
     lambda: pat.Rub(1.0, float("inf"))),
    ("T01_N3", "wrong shape (5,) rejected",
     lambda: pat.GeneralPattern(np.zeros(5), np.zeros(6), np.zeros(6), np.zeros(6))),
    ("T01_N4", "non-finite time rejected",
     lambda: pat.Push(1.0).wrench(float("nan"))),
    ("T01_N5", "unknown pattern kind rejected",
     lambda: pat.pattern_from_spec({"kind": "poke"})),
]
for cid, desc, fn in neg_cases:
    check(cid, desc, rejects(fn))

# ---------------------------------------------------------------- mutations
# Each mutant is a deliberately wrong pattern; the SAME analytic comparison
# must fail, proving the checks are sensitive to the paper's phase/frequency/
# amplitude placement rather than passing trivially.
def matches(prod_w, ref_w, tol=1e-14):
    return np.max(np.abs(np.asarray(prod_w) - np.asarray(ref_w))) < tol

mutants = {
    "T01_M1": ("mut: phase and frequency swapped (b<->c) is detected",
               np.array([0, 0, 0, 0.25, 0.25, 0]), np.array([0, 0, 0, 0, np.pi / 2, 0]),
               np.array([0, 0, 0, 2 * np.pi, 2 * np.pi, 0]), np.zeros(6), "wiggle"),
    "T01_M2": ("mut: amplitude scaled by 0.5 is detected",
               np.array([0, 0, 0, 0.125, 0.125, 0]), np.array([0, 0, 0, 2 * np.pi, 2 * np.pi, 0]),
               np.array([0, 0, 0, 0, np.pi / 2, 0]), np.zeros(6), "wiggle"),
    "T01_M3": ("mut: pi/2 phase placed on mx instead of my is detected",
               np.array([0, 0, 0, 0.25, 0.25, 0]), np.array([0, 0, 0, 2 * np.pi, 2 * np.pi, 0]),
               np.array([0, 0, 0, np.pi / 2, 0, 0]), np.zeros(6), "wiggle"),
}
for cid, (desc, ma, mb, mc, md, name) in mutants.items():
    mutant = pat.GeneralPattern(ma, mb, mc, md)
    ref = op.ORACLES[name](0.37, ORACLE_PARAMS[name])
    check(cid, desc, not matches(mutant.wrench(0.37), ref, 1e-6),
          float(np.max(np.abs(mutant.wrench(0.37) - ref))), "N*m")

# ---------------------------------------------------------------- axes
def nonzero_axes(w, tol=1e-15):
    vec = np.asarray(w, dtype=float).ravel()
    return tuple(i for i in range(vec.size) if abs(vec[i]) > tol)

axes_ok = (
    nonzero_axes(P["push"].wrench(1.0)) == (2,)
    and nonzero_axes(P["rub"].wrench(0.31)) == (5,)
    and set(nonzero_axes(P["wiggle"].wrench(0.31))) <= {3, 4}
    and set(nonzero_axes(P["spiral"].wrench(0.31))) <= {0, 1}
)
check("T01_13", "axis placement matches Eq.(16)/(19)-(22): fz | mz | mx,my | fx,fy",
      axes_ok, f"push{nonzero_axes(P['push'].wrench(1.0))} rub"
               f"{nonzero_axes(P['rub'].wrench(0.31))} "
               f"wig{nonzero_axes(P['wiggle'].wrench(0.31))} "
               f"spr{nonzero_axes(P['spiral'].wrench(0.31))}")

passes = sum(1 for c in CHECKS if c["pass"])
total = len(CHECKS)

# ---------------------------------------------------------------- figures
t = np.linspace(0.0, 4.0, 801)
fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), sharex=True)
for ax, name in zip(axes.ravel(), ("push", "rub", "wiggle", "spiral")):
    W = np.array([P[name].wrench(ti) for ti in t])
    for k in range(3):
        ax.plot(t, W[:, k], lw=1.2, label=f"f{['x','y','z'][k]} [N]")
    for k in range(3):
        ax.plot(t, W[:, 3 + k], lw=1.0, ls="--", label=f"m{['x','y','z'][k]} [N$\\cdot$m]")
    ax.set_title(f"{name} pattern (TEST_FIXTURE)")
    ax.grid(alpha=0.3)
    ax.set_xlabel("t [s]")
axes[0, 0].legend(fontsize=6, ncol=2)
fig.suptitle("P3-T01 perturbation wrenches w(t), Eq.(16)-(22)")
fig.tight_layout()
fig.savefig(FIG / "p3_t01_patterns_time.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
spr_plot = np.array([P["spiral"].wrench(ti) for ti in t])
fsp_plot = np.array([F["alpha_N"] * np.sin(F["v_spiral_rad_s"] * ti) + F["beta_N"] for ti in t])
ax[0].plot(spr_plot[:, 0], spr_plot[:, 1], lw=1.0)
ax[0].set_xlabel("fx [N]"); ax[0].set_ylabel("fy [N]")
ax[0].set_title("spiral in the x-y force plane")
ax[0].grid(alpha=0.3); ax[0].axis("equal")
ax[1].plot(t, fsp_plot, label=r"$f_{spiral}(t)=\alpha\sin(vt)+\beta$ [N]")
ax[1].plot(t, np.hypot(spr_plot[:, 0], spr_plot[:, 1]), ls="--",
           label="radius $\\sqrt{f_x^2+f_y^2}$ [N]")
ax[1].set_xlabel("t [s]"); ax[1].set_title("spiral amplitude modulation")
ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
fig.suptitle("P3-T01 spiral structure (TEST_FIXTURE parameters)")
fig.tight_layout()
fig.savefig(FIG / "p3_t01_spiral.png", dpi=160)
plt.close(fig)

result = {
    "task": "P3-T01",
    "kind": "perturbation_patterns",
    "paper_equations": ["16", "17", "18", "19", "20", "21", "22"],
    "run_id": RUN_ID,
    "seed": 20261019,
    "fixtures_note": "all numeric values are TEST_FIXTURE; the paper gives none",
    "checks": CHECKS,
    "summary": {"pass": passes, "total": total,
                "verdict": "PASS" if passes == total else "FAIL"},
    "figures": ["p3/evidence/figures/p3_t01_patterns_time.png",
                "p3/evidence/figures/p3_t01_spiral.png"],
}
(OUT / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\n{passes}/{total} PASS  -> {OUT/'results.json'}")
sys.exit(0 if passes == total else 1)
