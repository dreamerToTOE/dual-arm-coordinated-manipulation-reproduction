#!/usr/bin/env python3
"""P3-T02 validation driver — assembly-stage composition, Eq.(23)-(26).

Positive: per-stage composition equality against an independent oracle; all
four documented assembly-case stage sequences traced on a prescribed schedule.
Negative: unknown stage, non-contiguous / backwards / mis-sized schedules,
unknown case, and a mutated composition are all detected.

Boundary discontinuities are *reported* (the paper switches stages manually);
they are not treated as errors.

Run:  /usr/bin/python3.10 p3/tools/run_t02_stages.py
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

from baselines.p3_peg_in_hole import fixtures as fx      # noqa: E402
from baselines.p3_peg_in_hole import patterns as pat    # noqa: E402
from baselines.p3_peg_in_hole import stages as st       # noqa: E402
from oracles import oracle_control as oc                # noqa: E402

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S") + "_P3-T02_stages"
OUT = ROOT / "results" / RUN_ID
OUT.mkdir(parents=True, exist_ok=True)
FIG = ROOT / "p3" / "evidence" / "figures"

F = fx.TEST_FIXTURE
P = fx.pattern_set()
CHECKS = []

OP = {
    "push": {"f_push": F["f_push_N"]},
    "rub": {"f_rub": F["f_rub_Nm"], "v_rub": F["v_rub_rad_s"]},
    "wiggle": {"f_wiggle": F["f_wiggle_Nm"], "v_wiggle": F["v_wiggle_rad_s"]},
    "spiral": {"alpha": F["alpha_N"], "beta": F["beta_N"], "v_spiral": F["v_spiral_rad_s"]},
}

BOUNDARIES = {
    "case1_approach_search_align_insert": fx.STAGE_BOUNDARIES_CASE1_S,
    "case2_approach_search_insert": fx.STAGE_BOUNDARIES_CASE2_S,
    "case3_approach_align_insert": fx.STAGE_BOUNDARIES_CASE3_S,
    "case4_approach_insert": fx.STAGE_BOUNDARIES_CASE4_S,
}


def check(cid, desc, ok, residual=None, unit="", note=""):
    CHECKS.append({"id": cid, "desc": desc, "pass": bool(ok), "residual": residual,
                   "unit": unit, "note": note})
    r = f"  {residual:.3e} {unit}" if isinstance(residual, (int, float)) else (
        f"  {residual}" if residual else "")
    print(f"{'PASS' if ok else 'FAIL'} {cid}: {desc}{r}")


def maxdiff(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


T_SPOT = (0.0, 0.75, 3.1, 4.4, 9.9, 12.0, 16.0, 17.4)

# ---------------------------------------------------------------- T02_01..04
for cid, stage in (("T02_01", "approach"), ("T02_02", "search"),
                   ("T02_03", "align"), ("T02_04", "insert")):
    worst = 0.0
    for t in T_SPOT:
        worst = max(worst, maxdiff(st.stage_wrench(stage, P, t), oc.stage_wrench(stage, t, OP)))
    check(cid, f"{stage}: composition vs independent oracle "
               f"({'+'.join(st.COMPOSITION[stage])})", worst < 1e-14, worst, "N / N*m")

# ---------------------------------------------------------------- T02_05
# The compositions must be *these* sums, not merely oracle-equal: verify the
# structural separation (e.g. approach carries no oscillation) elementwise.
t0 = 1.234
push_only = P["push"].wrench(t0)
struct_ok = (
    maxdiff(st.stage_wrench("approach", P, t0), push_only) < 1e-15
    and maxdiff(st.stage_wrench("insert", P, t0), push_only) < 1e-15
    and abs(st.stage_wrench("search", P, t0)[0] - P["spiral"].wrench(t0)[0]) < 1e-15
    and abs(st.stage_wrench("align", P, t0)[5] - P["rub"].wrench(t0)[5]) < 1e-15
    and abs(st.stage_wrench("align", P, t0)[3] - P["wiggle"].wrench(t0)[3]) < 1e-15
)
check("T02_05", "structural check: approach/insert = push only; search adds spiral x; "
                "align adds wiggle mx and rub mz", struct_ok)

# ---------------------------------------------------------------- T02_06
# All four documented sequences trace correctly on their prescribed schedules.
schedules = {case: st.schedule_from_case(case, BOUNDARIES[case]) for case in st.CASES}
seq_ok, worst_seq, stage_errors = True, 0.0, 0
for case, sched in schedules.items():
    expected = st.CASES[case]
    seq_ok &= (sched.sequence == expected)
    for seg in sched.segments:
        for t in np.linspace(seg.t_start, seg.t_end - 1e-9, 17):
            got_stage, got_w = sched.wrench_at(P, t)
            if got_stage != seg.stage:
                stage_errors += 1
            worst_seq = max(worst_seq, maxdiff(got_w, oc.stage_wrench(seg.stage, t, OP)))
check("T02_06", "four documented case sequences: stage attribution + wrench equality",
      seq_ok and stage_errors == 0 and worst_seq < 1e-14,
      f"seq_ok={seq_ok} stage_errors={stage_errors} maxdiff={worst_seq:.2e}",
      note="cases 2-4 boundaries are illustrative [ADAPTATION]")

# ---------------------------------------------------------------- T02_07
# Boundary jumps are reported, and the reported jump equals the analytic jump.
jumps = {case: sched.discontinuities(P) for case, sched in schedules.items()}
case1 = jumps["case1_approach_search_align_insert"]
analytic = float(np.linalg.norm(P["spiral"].wrench(3.2)[:3]))
check("T02_07", "boundary discontinuities reported (approach|search force jump = |spiral force| at t=3.2 s)",
      len(case1) == 3 and abs(case1[0]["jump_force_N"] - analytic) < 1e-12,
      f"jumps={[round(r['jump_l2'], 6) for r in case1]} N",
      note="manual switching => jumps legitimate, only reported")

# ---------------------------------------------------------------- negatives
def raises(fn):
    try:
        fn()
    except (st.StageDomainError, ValueError):
        return True
    return False


neg = [
    ("T02_N1", "unknown stage rejected",
     lambda: st.stage_wrench("dwell", P, 1.0)),
    ("T02_N2", "non-contiguous schedule rejected",
     lambda: st.StageSchedule([st.Segment("approach", 0.0, 1.0),
                               st.Segment("insert", 2.0, 3.0)])),
    ("T02_N3", "backwards segment rejected",
     lambda: st.StageSchedule([st.Segment("approach", 1.0, 1.0)])),
    ("T02_N4", "wrong boundary count rejected",
     lambda: st.schedule_from_case("case1_approach_search_align_insert", [0.0, 3.0])),
    ("T02_N5", "unknown case rejected",
     lambda: st.schedule_from_case("case9", [0.0, 1.0])),
    ("T02_N6", "time outside schedule rejected",
     lambda: schedules["case1_approach_search_align_insert"].wrench_at(P, 99.0)),
]
for cid, desc, fn in neg:
    check(cid, desc, raises(fn))

# ---------------------------------------------------------------- mutations
# M1: drop the rub term from aligning -> oracle mismatch must be detected.
T_MUT = 12.05  # chosen so that the rub moment is non-zero
mut_align = (P["push"].wrench(T_MUT) + P["wiggle"].wrench(T_MUT))
detected = maxdiff(mut_align, oc.stage_wrench("align", T_MUT, OP)) > 1e-6
check("T02_M1", "mut: aligning without rub is detected",
      detected, float(maxdiff(mut_align, oc.stage_wrench("align", T_MUT, OP))), "N*m")

# M2: search without push (spiral only) must be detected.
mut_search = P["spiral"].wrench(5.0)
detected2 = maxdiff(mut_search, oc.stage_wrench("search", 5.0, OP)) > 1e-6
check("T02_M2", "mut: searching without push is detected",
      detected2, float(maxdiff(mut_search, oc.stage_wrench("search", 5.0, OP))), "N")

# M3: swapping approach and insert compositions is undetectable by value alone
# (both are w_push) -> documented as an expected structural equivalence, not a
# failure. The check below asserts the equivalence is *known* and reported.
equiv = maxdiff(st.stage_wrench("approach", P, 7.7), st.stage_wrench("insert", P, 7.7)) < 1e-15
check("T02_08", "approach and insert are identical by Eq.(23)/(26) (documented equivalence)",
      equiv, note="not a defect; matters for stage attribution only")

passes = sum(1 for c in CHECKS if c["pass"])
total = len(CHECKS)

# ---------------------------------------------------------------- figure
sched = schedules["case1_approach_search_align_insert"]
t = np.linspace(0.0, sched.t_end - 1e-9, 1401)
W = np.zeros((t.size, 6))
S = []
for i, ti in enumerate(t):
    s, w = sched.wrench_at(P, ti)
    S.append(s)
    W[i] = w

fig, ax = plt.subplots(2, 1, figsize=(11, 6.4), sharex=True)
for k in range(3):
    ax[0].plot(t, W[:, k], lw=1.1, label=f"f{['x','y','z'][k]} [N]")
for k in range(3):
    ax[1].plot(t, W[:, 3 + k], lw=1.0, ls="--", label=f"m{['x','y','z'][k]} [N$\\cdot$m]")
colors = {"approach": "#cfe3f7", "search": "#fbe3c2", "align": "#d8f0d0", "insert": "#f5d3d3"}
for seg in sched.segments:
    for a in ax:
        a.axvspan(seg.t_start, seg.t_end, color=colors[seg.stage], alpha=0.55)
        a.text((seg.t_start + seg.t_end) / 2, a.get_ylim()[1] * 0.9, seg.stage,
               ha="center", fontsize=8)
ax[0].set_ylabel("force [N]"); ax[1].set_ylabel("moment [N$\\cdot$m]")
ax[1].set_xlabel("t [s]")
ax[0].legend(fontsize=7, ncol=3); ax[1].legend(fontsize=7, ncol=3)
ax[0].set_title("P3-T02 case 1 (approach-search-align-insert): composed wrench, Eq.(23)-(26)")
ax[0].grid(alpha=0.3); ax[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "p3_t02_case1_wrench.png", dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 3.6))
names = list(schedules)
width = 0.2
for j, case in enumerate(names):
    js = [r["jump_l2"] for r in jumps[case]]
    ax.bar(np.arange(len(js)) + j * width, js, width=width, label=case)
ax.set_xlabel("boundary index"); ax.set_ylabel("wrench jump $\\|\\Delta w\\|$ [N or N$\\cdot$m]")
ax.set_title("P3-T02 stage-boundary command jumps (reported, not errors)")
ax.legend(fontsize=7); ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(FIG / "p3_t02_boundary_jumps.png", dpi=160)
plt.close(fig)

result = {
    "task": "P3-T02",
    "kind": "stage_composition",
    "paper_equations": ["23", "24", "25", "26"],
    "run_id": RUN_ID,
    "checks": CHECKS,
    "schedules": {case: {"sequence": list(s.sequence),
                         "segments": [[seg.stage, seg.t_start, seg.t_end] for seg in s.segments]}
                  for case, s in schedules.items()},
    "boundary_jumps": {case: jumps[case] for case in jumps},
    "summary": {"pass": passes, "total": total,
                "verdict": "PASS" if passes == total else "FAIL"},
    "figures": ["p3/evidence/figures/p3_t02_case1_wrench.png",
                "p3/evidence/figures/p3_t02_boundary_jumps.png"],
}
(OUT / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(f"\n{passes}/{total} PASS  -> {OUT/'results.json'}")
sys.exit(0 if passes == total else 1)
