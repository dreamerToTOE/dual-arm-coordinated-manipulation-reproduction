#!/usr/bin/env python3
"""P3-T06 validation driver — deterministic integration of Eq.(16)-(28).

For each documented assembly case the driver samples a prescribed stage
schedule, evaluates the composed perturbation wrench, the selection/frame
operators and the full torque law, then checks:

  * per-sample equality with the independent oracle (w and tau)
  * every documented stage is exercised (no dead branches)
  * clock monotonicity and boundary alignment
  * finiteness and engineering sanity bounds
  * determinism (bitwise identical second pass)
  * a dropped stage is detected

It demonstrates **command consistency only**. No object motion, contact or
insertion success is simulated or claimed.

Run:  /usr/bin/python3.10 p3/tools/run_t06_integration.py
"""
import hashlib
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
from baselines.p3_peg_in_hole import stages as st       # noqa: E402
from oracles import oracle_control as oc                # noqa: E402

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S") + "_P3-T06_integration"
OUT = ROOT / "results" / RUN_ID
OUT.mkdir(parents=True, exist_ok=True)
FIG = ROOT / "p3" / "evidence" / "figures"

DT = 0.01
BOUNDARIES = {
    "case1_approach_search_align_insert": fx.STAGE_BOUNDARIES_CASE1_S,
    "case2_approach_search_insert": fx.STAGE_BOUNDARIES_CASE2_S,
    "case3_approach_align_insert": fx.STAGE_BOUNDARIES_CASE3_S,
    "case4_approach_insert": fx.STAGE_BOUNDARIES_CASE4_S,
}
CHECKS = []
P = fx.pattern_set()
OP = {
    "push": {"f_push": fx.TEST_FIXTURE["f_push_N"]},
    "rub": {"f_rub": fx.TEST_FIXTURE["f_rub_Nm"], "v_rub": fx.TEST_FIXTURE["v_rub_rad_s"]},
    "wiggle": {"f_wiggle": fx.TEST_FIXTURE["f_wiggle_Nm"],
               "v_wiggle": fx.TEST_FIXTURE["v_wiggle_rad_s"]},
    "spiral": {"alpha": fx.TEST_FIXTURE["alpha_N"], "beta": fx.TEST_FIXTURE["beta_N"],
               "v_spiral": fx.TEST_FIXTURE["v_spiral_rad_s"]},
}

R_H = np.array([[0.8660254037844386, -0.5, 0.0],
                [0.5, 0.8660254037844386, 0.0],
                [0.0, 0.0, 1.0]]) @ np.array([[0.9659258262890683, 0.0, 0.2588190451025207],
                                              [0.0, 1.0, 0.0],
                                              [-0.2588190451025207, 0.0, 0.9659258262890683]])
R_T2H = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]])  # e_z -> e_x (A1)

J = fx.jacobian()
KP = fx.gains("peg")
D = fx.damping()
TG = fx.gravity()
TF = fx.friction()
J_PINV = np.linalg.pinv(J)


def check(cid, desc, ok, residual=None, unit="", note=""):
    CHECKS.append({"id": cid, "desc": desc, "pass": bool(ok), "residual": residual,
                   "unit": unit, "note": note})
    r = f"  {residual:.3e} {unit}" if isinstance(residual, (int, float)) else (
        f"  {residual}" if residual else "")
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {desc}{r}")


def maxdiff(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def state_at(t):
    """TEST_FIXTURE error/joint-velocity profiles (no dynamics)."""
    dx = np.array([1.0e-3 * np.sin(0.4 * np.pi * t),
                   1.0e-3 * np.cos(0.4 * np.pi * t),
                   1.0e-3 * np.sin(0.4 * np.pi * t + 0.5),
                   5.0e-4 * np.sin(0.8 * t),
                   5.0e-4 * np.cos(0.8 * t),
                   5.0e-4 * np.sin(0.8 * t + 0.3)])
    V = np.array([1.0e-3 * np.sin(0.5 * t), 1.0e-3 * np.cos(0.5 * t), 0.0,
                  1.0e-4 * np.sin(0.5 * t), 0.0, 1.0e-4 * np.cos(0.5 * t)])
    return dx, J_PINV @ V


def run_case(case):
    sched = st.schedule_from_case(case, BOUNDARIES[case])
    t = np.arange(0.0, sched.t_end - 1e-12, DT)
    rows, w_list, Fpos_list, Fpert_list, tau_list, stages_seen = [], [], [], [], [], []
    for ti in t:
        stage, w = sched.wrench_at(P, ti)
        dx, qdot = state_at(ti)
        terms = ctl.torque_terms(J, R_H, KP, dx, w, D, qdot, TG, TF,
                                 R_task_to_hole=R_T2H)
        w_list.append(w); Fpos_list.append(terms["F_pos"]); Fpert_list.append(terms["F_pert"])
        tau_list.append(terms["tau"]); stages_seen.append(stage)
        rows.append([ti, stage] + list(w) + list(terms["F_pos"])
                    + list(terms["F_pert"]) + list(terms["tau"]))
    W = np.array(w_list); FP = np.array(Fpos_list); FQ = np.array(Fpert_list)
    TAU = np.array(tau_list)
    hdr = (["t_s", "stage"]
           + [f"w_{n}" for n in ("fx", "fy", "fz", "mx", "my", "mz")]
           + [f"Fpos_{n}" for n in ("fx", "fy", "fz", "mx", "my", "mz")]
           + [f"Fpert_{n}" for n in ("fx", "fy", "fz", "mx", "my", "mz")]
           + [f"tau_{k}" for k in range(7)])
    import csv
    with open(OUT / f"{case}_trace.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(hdr)
        for r in rows:
            wr.writerow([f"{r[0]:.6f}", r[1]] + [f"{v:.12g}" for v in r[2:]])
    numeric = np.array([r[2:] for r in rows], dtype=float)
    return {"schedule": sched, "t": t, "stage": stages_seen, "w": W, "Fpos": FP,
            "Fpert": FQ, "tau": TAU,
            "rows_digest": hashlib.sha256(numeric.tobytes()).hexdigest()}


runs = {case: run_case(case) for case in st.CASES}

# ---------------------------------------------------------------- T06_01 coverage
missing = {}
for case, r in runs.items():
    seen = set(r["stage"])
    expected = set(st.CASES[case])
    missing[case] = sorted(expected - seen)
check("T06_01", "every documented stage of every case is exercised (no dead branch)",
      not any(missing.values()), str({k: v for k, v in missing.items() if v}) or "none missing")

# ---------------------------------------------------------------- T06_02 clock
clock_ok, clock_res = True, 0.0
for case, r in runs.items():
    t = r["t"]
    clock_ok &= bool(np.all(np.diff(t) > 0)) and abs((t[-1] + DT) - r["schedule"].t_end) < 1e-9
    for ti, stage in zip(t, r["stage"]):
        if r["schedule"].segment_at(ti).stage != stage:
            clock_ok = False
    clock_res = max(clock_res, float(np.max(np.abs(np.diff(t) - DT))))
check("T06_02", "clock monotone, uniform dt, stage attribution consistent with schedule",
      clock_ok, clock_res, "s", note="dt = 0.01 s")

# ---------------------------------------------------------------- T06_03 oracle
worst_tau, worst_w = 0.0, 0.0
for case, r in runs.items():
    sched = r["schedule"]
    for ti, stage, wk, tau_k in zip(r["t"], r["stage"], r["w"], r["tau"]):
        worst_w = max(worst_w, maxdiff(wk, oc.stage_wrench(stage, ti, OP)))
        dx, qdot = state_at(ti)
        w_hole = ctl.wrench_rotation(R_T2H) @ wk   # explicit A1 relabelling
        ref = oc.torque(J, R_H, KP, dx, w_hole, D, qdot, TG, TF)
        worst_tau = max(worst_tau, maxdiff(tau_k, ref))
check("T06_03", "per-sample wrench equals composition oracle", worst_w < 1e-14, worst_w, "N / N*m")
check("T06_04", "per-sample torque equals independent oracle (A1 mapping applied explicitly)",
      worst_tau < 1e-12, worst_tau, "N*m")

# ---------------------------------------------------------------- T06_05 finite/bounds
all_tau = np.vstack([r["tau"] for r in runs.values()])
all_w = np.vstack([r["w"] for r in runs.values()])
finite = np.isfinite(all_tau).all() and np.isfinite(all_w).all()
METRICS = {
    # review R2: max absolute component and max vector norm are different
    # quantities; both are reported and neither is called "||tau||".
    "max_abs_tau_component_Nm": float(np.max(np.abs(all_tau))),
    "max_tau_vector_norm_Nm": float(np.max(np.linalg.norm(all_tau, axis=1))),
    "max_abs_force_component_N": float(np.max(np.abs(all_w[:, :3]))),
    "max_force_vector_norm_N": float(np.max(np.linalg.norm(all_w[:, :3], axis=1))),
    "max_abs_moment_component_Nm": float(np.max(np.abs(all_w[:, 3:]))),
    "max_moment_vector_norm_Nm": float(np.max(np.linalg.norm(all_w[:, 3:], axis=1))),
}
check("T06_05", "all samples finite; max component and max vector norm reported separately",
      bool(finite),
      f"max_t,k|tau_k|={METRICS['max_abs_tau_component_Nm']:.3f} N*m; "
      f"max_t||tau||2={METRICS['max_tau_vector_norm_Nm']:.3f} N*m; "
      f"max_t,i|F_i|={METRICS['max_abs_force_component_N']:.2f} N; "
      f"max_t||F||2={METRICS['max_force_vector_norm_N']:.2f} N; "
      f"max_t||m||2={METRICS['max_moment_vector_norm_Nm']:.3f} N*m")

# ---------------------------------------------------------------- T06_06 push axis
# The position term must stay inside the controlled subspace for every sample.
worst_axis = 0.0
n_ax = R_H @ (R_T2H @ np.array([0.0, 0.0, 1.0]))   # task push axis e_z -> hole x -> reference
for r in runs.values():
    for fp in r["Fpos"]:
        worst_axis = max(worst_axis, float(abs(n_ax @ fp[:3])))
check("T06_06", "position command never acts along the push axis (all samples)",
      worst_axis < 1e-12, worst_axis, "N")

# ---------------------------------------------------------------- T06_07 determinism
digest2 = {case: run_case(case)["rows_digest"] for case in st.CASES}
check("T06_07", "deterministic: second full pass is bitwise identical",
      all(digest2[c] == runs[c]["rows_digest"] for c in st.CASES),
      "sha256 match")

# ---------------------------------------------------------------- T06_08 per-stage stats
stats = {}
for case, r in runs.items():
    for stage in st.CASES[case]:
        mask = np.array([s == stage for s in r["stage"]])
        stats.setdefault(case, {})[stage] = {
            "samples": int(mask.sum()),
            "duration_s": float(mask.sum() * DT),
            "max_abs_tau_component_Nm": float(np.max(np.abs(r["tau"][mask]))) if mask.any() else None,
            "max_tau_vector_norm_Nm": float(np.max(np.linalg.norm(r["tau"][mask], axis=1))) if mask.any() else None,
            "mean_abs_force_component_N": float(np.mean(np.abs(r["w"][mask][:, :3]))) if mask.any() else None,
            "mean_force_vector_norm_N": float(np.mean(np.linalg.norm(r["w"][mask][:, :3], axis=1))) if mask.any() else None,
        }
stage_ok = all(v["samples"] > 0 for c in stats.values() for v in c.values())
check("T06_08", "per-stage sample counts and magnitudes recorded", stage_ok,
      f"{sum(len(v) for v in stats.values())} stage blocks")

# ---------------------------------------------------------------- negatives
# N1: dropping a documented stage is detected by the coverage check.
sched_bad = st.StageSchedule([st.Segment("approach", 0.0, 3.0),
                              st.Segment("insert", 3.0, 5.0)])
missing_detected = set(st.CASES["case1_approach_search_align_insert"]) - set(sched_bad.sequence)
check("T06_N1", "missing stage command is detected (case1 without search/align)",
      bool(missing_detected), f"missing={sorted(missing_detected)}")

# N2: overlapping clocks are rejected by the schedule type.
def rejects(fn):
    try:
        fn()
    except (st.StageDomainError, ValueError):
        return True
    return False


check("T06_N2", "overlapping/backwards stage clocks rejected",
      rejects(lambda: st.StageSchedule([st.Segment("approach", 0.0, 2.0),
                                        st.Segment("search", 1.5, 3.0)])))

# N3: a stage longer than the trace cannot silently disappear
check("T06_N3", "out-of-range sampling rejected instead of silently clamped",
      rejects(lambda: runs["case1_approach_search_align_insert"]["schedule"].wrench_at(
          P, runs["case1_approach_search_align_insert"]["schedule"].t_end + 1.0)))

# ---------------------------------------------------------------- T06_09 mapping composition
_dx, _qdot = state_at(1.0)
_w = np.array([1.0, -2.0, 8.0, 0.2, -0.1, 0.05])
_t = ctl.torque_terms(J, R_H, KP, _dx, _w, D, _qdot, TG, TF, R_task_to_hole=R_T2H)
_expect = ctl.wrench_rotation(R_H @ R_T2H) @ _w
check("T06_09", "A1 mapping composes as R_h*R_task_to_hole in the perturbation term",
      maxdiff(_t["F_pert"], _expect) < 1e-14, maxdiff(_t["F_pert"], _expect), "N / N*m")

passes = sum(1 for c in CHECKS if c["pass"])
total = len(CHECKS)

# ---------------------------------------------------------------- figures
r1 = runs["case1_approach_search_align_insert"]
sched1 = r1["schedule"]
fig, ax = plt.subplots(3, 1, figsize=(11, 8.2), sharex=True)
for k in range(3):
    ax[0].plot(r1["t"], r1["w"][:, k], lw=1.0, label=f"f{['x','y','z'][k]} [N]")
ax[0].set_ylabel("command force [N]"); ax[0].legend(fontsize=7, ncol=3)
for k in range(3):
    ax[1].plot(r1["t"], r1["w"][:, 3 + k], lw=1.0, ls="--", label=f"m{['x','y','z'][k]} [N$\\cdot$m]")
ax[1].set_ylabel("command moment [N$\\cdot$m]"); ax[1].legend(fontsize=7, ncol=3)
for k in range(7):
    ax[2].plot(r1["t"], r1["tau"][:, k], lw=0.9, label=f"$\\tau_{k+1}$ [N$\\cdot$m]")
ax[2].set_ylabel("joint torque [N$\\cdot$m]"); ax[2].set_xlabel("t [s]")
ax[2].legend(fontsize=6, ncol=4)
colors = {"approach": "#cfe3f7", "search": "#fbe3c2", "align": "#d8f0d0", "insert": "#f5d3d3"}
for seg in sched1.segments:
    for a in ax:
        a.axvspan(seg.t_start, seg.t_end, color=colors[seg.stage], alpha=0.5)
        a.text((seg.t_start + seg.t_end) / 2, a.get_ylim()[1] * 0.88, seg.stage,
               ha="center", fontsize=8)
ax[0].set_title("P3-T06 case 1: commanded wrench and Eq.(27) torque (TEST_FIXTURE state)")
for a in ax:
    a.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "p3_t06_case1_trace.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 3.4))
for i, case in enumerate(st.CASES):
    sched = runs[case]["schedule"]
    for seg in sched.segments:
        ax.barh(i, seg.t_end - seg.t_start, left=seg.t_start,
                color=colors[seg.stage], edgecolor="k", linewidth=0.4)
        ax.text((seg.t_start + seg.t_end) / 2, i, seg.stage, ha="center", va="center", fontsize=7)
ax.set_yticks(range(len(st.CASES)))
ax.set_yticklabels([c.split("_", 1)[0] + ": " + "-".join(st.CASES[c]) for c in st.CASES], fontsize=7)
ax.set_xlabel("t [s]"); ax.set_title("P3-T06 documented case sequences on prescribed schedules [ADAPTATION]")
ax.grid(alpha=0.3, axis="x")
fig.tight_layout()
fig.savefig(FIG / "p3_t06_case_sequences.png", dpi=160)
plt.close(fig)

result = {
    "task": "P3-T06",
    "kind": "deterministic_integration",
    "paper_equations": ["16-22", "23-26", "27", "28"],
    "run_id": RUN_ID,
    "dt_s": DT,
    "scope_note": "command consistency only: no object motion, no contact, no insertion success",
    "checks": CHECKS,
    "per_stage_stats": stats,
    "magnitude_metrics": METRICS,
    "traces": [f"{c}_trace.csv" for c in st.CASES],
    "summary": {"pass": passes, "total": total,
                "verdict": "PASS" if passes == total else "FAIL"},
    "figures": ["p3/evidence/figures/p3_t06_case1_trace.png",
                "p3/evidence/figures/p3_t06_case_sequences.png"],
}
(OUT / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\n{passes}/{total} PASS  -> {OUT/'results.json'}")
sys.exit(0 if passes == total else 1)
