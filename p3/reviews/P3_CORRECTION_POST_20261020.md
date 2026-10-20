# P3 Correction POST — post-delivery review R1–R4

**Date**: 2026-10-20 | **Branch**: `reproduce-p3-paper-study-20261019`
**Review input**: `11542aee` (`p3/reviews/P3_POST_DELIVERY_REVIEW_20261020.md`, conditional acceptance)
**Status**: `CORRECTIONS_COMPLETE` — **92/92** checks (was 91; T03 gained one negative control)

This was a targeted evidence correction, not a new reproduction phase. No contact model, simulator,
controller, dependency or experiment was added; P2/P4 were not touched.

## R1 — T03_12 used a tautological basis vector (scientific correctness)

**Before**: `Sel_task = position_selector(R_h·R_task→hole)`, then tested
`Sel_task · (R_h·R_task→hole·e_x)`. That shows a projector annihilates its own transformed `e_x`;
the comment `# = R_h e_z` was false because `R_y(+90°) e_x = −e_z`.

**After** (`p3/tools/run_t03_selection.py`, new run `20261020_104153_P3-T03_selection`):

| Check | Content | Result |
|---|---|---|
| T03_12 | `Ω(R_h)` annihilates the **physical push direction** `p_ref = R_h(R_task→hole e_z)` | **8.5e-17** |
| T03_15 (new) | negative control: literal frame (`R_h = I`, no relabelling) leaves `e_z` inside the controlled subspace: `‖Ω(I)e_z‖ = 1` | **1.0** |

**Scientific consequence (recorded, not glossed)**: both readings are valid projectors, but they
exclude *different physical directions*. Only the relabelled reading excludes the push axis. The
paper never states the task→hole rotation, so A1 remains an **open source ambiguity**; the chosen
convention is an explicit **[ADAPTATION]**, not a paper-established fact. The previous claim that
"both variants keep the annihilated axis on the push axis" was wrong and has been removed from the
T00 audit, the T03 POST and the final report.

## R2 — T06 reported max-component as if it were a norm (metric correctness)

**Before**: `max|τ| = 10.15 N·m` was `max_{t,k}|τ_k|`, not `max_t‖τ‖₂`; the report wrote `‖τ‖ ≤ 10.15`.

**After** (new run `20261020_104237_P3-T06_integration`, `magnitude_metrics` in JSON):

| Quantity | Value |
|---|---:|
| `max_{t,k} |τ_k|` | 10.152 N·m |
| `max_t ‖τ‖₂` | 12.590 N·m |
| `max_{t,i} |F_i|` | 10.00 N |
| `max_t ‖F‖₂` | 11.18 N |
| `max_{t,i} |m_i|` | 0.300 N·m |
| `max_t ‖m‖₂` | 0.391 N·m |

Per-stage stats renamed accordingly: `max_abs_tau_component_Nm`, `max_tau_vector_norm_Nm`,
`mean_abs_force_component_N`, `mean_force_vector_norm_N`. The distinction is visible: a pure 10 N push
has `mean |F_i| = 3.33 N` but `mean ‖F‖ = 10.0 N`.

## R3 — T02 mixed newton and newton-metre in one norm (dimensional correctness)

`StageSchedule.discontinuities()` now returns `jump_force_N` and `jump_moment_Nm` as the primary
metrics; the concatenated value is renamed `jump_mixed_l2_unphysical` and documented as a
dimensionless diagnostic (new run `20261020_104220_P3-T02_stages`).

| Boundary (case 1) | ‖Δf‖₂ [N] | ‖Δm‖₂ [N·m] |
|---|---:|---:|
| approach→search | 1.824 | 0.000 |
| search→align | 5.000 | 0.391 |
| align→insert | 0.000 | 0.391 |

The separation is informative: the first boundary is force-only, the last is moment-only — exactly
what the mixed norm obscured. The figure is now two panels with separate units.

## R4 — append-only registers updated (governance)

Appended (never rewriting old entries) in:

- `docs/STATUS.md` — P3 scope/result entry, explicitly *not* touching the roadmap table and not
  claiming TASK11–15 (MuJoCo/Isaac) complete;
- `docs/WORKLOG.md` — study sequence and commit SHAs;
- `docs/EXPERIMENT_LOG.md` — three corrected runs with commands, seeds, metrics, artifacts;
- `docs/DECISIONS.md` — D003 (A1 frame convention), D004 (prescribed stage switching), D005
  (mixed-unit reporting convention).

## Preserved history

Original runs `20261020_093347_P3-T01_patterns`, `093810_P3-T02_stages`, `094115_P3-T03_selection`,
`094329_P3-T04_torque`, `094514_P3-T06_integration` are untouched. Original POSTs are amended in
place with a "superseded run (preserved)" line; the numbers they report remain as-run.

## Amended counts

| Task | Before | After | Why |
|---|---:|---:|---|
| T01 | 21 | 21 | unchanged |
| T02 | 16 | 16 | metrics corrected, no new check |
| T03 | 22 | **23** | T03_15 negative control added |
| T04 | 20 | 20 | unchanged |
| T06 | 12 | 12 | metrics corrected, no new check |
| **Total** | **91** | **92** | |

## Reproducibility

```bash
cd /home/ubuntu2004/lmy/p3-paper-study-20261019
/usr/bin/python3.10 p3/tools/run_t03_selection.py    # 23 checks
/usr/bin/python3.10 p3/tools/run_t02_stages.py       # 16 checks
/usr/bin/python3.10 p3/tools/run_t06_integration.py  # 12 checks
/usr/bin/python3.10 p3/tools/build_p3_csv.py
/usr/bin/python3.10 p3/tools/build_p3_report.py      # md -> docx + pdf
```

## Caveats (unchanged)

All numeric parameters remain `TEST_FIXTURE`; the paper publishes none. The suite demonstrates
formula implementation and command consistency only — no object motion, contact outcome, hardware
success statistics or dual-arm robot dynamics. T05 remains `NOT_EXECUTED_OPTIONAL`.
