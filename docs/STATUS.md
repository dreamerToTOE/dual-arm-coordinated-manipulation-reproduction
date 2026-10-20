# STATUS

Last update: 2026-09-30

## Project state
Repository initialized. No baseline implementation has started.

| Task | Status | Notes |
|---|---|---|
| TASK00 Environment Audit | PASS | Report: reports/TASK00_ENVIRONMENT.md; external integration gaps identified |
| TASK01 Benchmark Freeze | READY | Needs user review before FROZEN; spec remains DRAFT |
| TASK02 Common Interfaces / Logger / Metrics | TODO | Depends on TASK01 |
| TASK03–06 P4 | TODO | |
| TASK07–10 P2 | TODO | |
| TASK11–15 P3 | TODO | |
| TASK16–19 P5 | TODO | |
| TASK20–26 P1 | TODO | |
| TASK27–30 Evaluation/Freeze | TODO | |
| TASK31 Ours v0 | TODO | Must wait for TASK30 |

## Current gate
**Do not implement paper algorithms yet. Draft and review TASK01 benchmark_v1 first.**

## 2026-10-20 — P3 arm-level numerical reproduction (D082 scope)

Appended by the P3 numerical study. The roadmap table above is **not** rewritten, and the
MuJoCo/Isaac P3 tasks (TASK11–15) remain TODO — this entry describes a separate, explicitly
approved algorithm-level numerical study on its own branch.

- Branch: `reproduce-p3-paper-study-20261019` (review base `5e43cf05`, correction base `11542aee`).
- Paper: Lee et al., *Peg-in-Hole Assembly With Dual-Arm Robot and Dexterous Robot Hands*,
  IEEE RA-L 7(4):8566–8573, 2022, DOI `10.1109/LRA.2022.3187497`.
- Scope: arm-level Eq.(16)–(28) only — perturbation patterns, stage composition, selection/frames,
  feedforward torque law, deterministic stage integration.
- Out of scope (`OUT_OF_SCOPE_D082`): Eq.(1)–(15) dexterous hand, 50-DOF hardware, 87% / 13.86 s
  statistics, Fig.8/9/11 trajectories, automatic phase recognition, MuJoCo/Isaac deployment.
- Result: **`ALGORITHM_NUMERICAL_VERIFIED` (D082 scope)**, 92/92 checks after the post-delivery
  corrections (T01 21, T02 16, T03 23, T04 20, T06 12). **Not** `FULL_PAPER_REPRODUCED`.
- Evidence: `p3/reviews/P3_T0*_{PRE,POST}.md`, `p3/reviews/P3_CORRECTION_POST_20261020.md`,
  `results/20261020_*_P3-T0*`, `p3/reports/final/`.
- T05 quasi-static contact surrogate: `NOT_EXECUTED_OPTIONAL` (not an acceptance dependency).

## 2026-10-20 — P5 paper-first study (pre-implementation gate)

Appended by the P5 paper study. The roadmap table above is **not** rewritten, and the P5 tasks
(TASK16–19) remain TODO — this entry describes a separate, explicitly scoped study on its own branch.

- Branch: `reproduce-p5-paper-study-20261020` (base `c39ef42c` = P3 acceptance commit).
- Paper: Mirrazavi Salehian, Figueroa, Billard, *A Unified Framework for Coordinated Multi-Arm
  Motion Planning*, IJRR 37(6):583–603, 2018, DOI `10.1177/0278364918765952`.
- Scope: full-text study + equation audit + official-code audit + proposed reproduction matrix.
  **Status `PAPER_STUDIED / AWAITING_REPRODUCTION_MATRIX_REVIEW`.**
- Deliverables: `p5/P5_PAPER_STUDY.md`, `p5/P5_EQUATION_AUDIT.md`, `p5/P5_OFFICIAL_CODE_AUDIT.md`,
  `p5/P5_IMPLEMENTATION_PLAN.md`, `p5/P5_ORIGINAL_EXPERIMENT_MATRIX.csv`,
  `p5/P5_PROPOSED_REPRODUCTION_MATRIX.csv`, `p5/P5_EQUATION_REGISTRY.csv`,
  `p5/evidence/P5_official_code_manifest.json`, 5 redrawn schematic figures, 2 generator scripts.
- Proposed scope: A (sync/async DS + τ allocation) + B (centralised QP IK + LVI) + C (learned SCA
  boundary + ∇Γ chain rule) as `MINIMUM_ESSENTIAL` (T01–T08); FCL distance constraints (T09) and the
  end-to-end replay (T10) as `OPTIONAL_EXTENSION` and explicitly `ADAPTATION`.
- Official code: 0 of 9 repositories run out of the box. `QP_IK_solver` has no CVXGEN backend and
  its SCA path is dead code; Eq.(26) has no implementation upstream. Nothing was vendored.
- **No numerical implementation was started.** The next gate is review of
  `p5/P5_PROPOSED_REPRODUCTION_MATRIX.csv` and `p5/P5_IMPLEMENTATION_PLAN.md` §9 (Q1–Q6).

## 2026-10-20 — P5 numerical reproduction: G1 green

- Branch: `reproduce-p5-numerical-20261020` (base `42f8b857` = approved study commit). P2/P3/P4 untouched.
- **G1 (foundation layer) PASS**: T01 11, T02 12, T04 20, T06 10 checks — **53 total (31 positive /
  22 negative), 0 failed, 11.4 s**. Ledger: `p5/evidence/P5_impl_checks.json`.
- Code: clean-room package `p5/impl/p5core` (results, kinematics, tau, lpv, qp_ik, lvi, svm_sca,
  plotting) + per-task modules + single-command runner `p5/impl/run_all.py`.
- Three plan defects were found and fixed while implementing T04 (see `p5/P5_GATE_LOG.md` and
  `docs/DECISIONS.md` D010–D012): the QP classifier needed a sixth state `INFEASIBLE` (empty
  equality∩box intersection), N4.5's `μ` direction was reversed, and `PlanarArm` mixed absolute and
  relative joint conventions.
- Next: G2 (T03 two-segment cancellation, T05 LVI passivity, T07 36-D model + calibration).
- Scope unchanged: T09 `NOT_AUTHORIZED_THIS_CYCLE`, T10 mandatory at G4.

## 2026-10-20 — P5 numerical reproduction: G2 green

- **G2 (solve layer) PASS**: T03 11, T05 14, T07 12 checks — **37 total (19 positive / 18 negative),
  0 failed, 106.0 s**. Cumulative G1+G2: **90 checks (50 pos / 40 neg), 0 failed, 117.4 s**.
- T03: the `τ̇` cancellation is split into the part that is an identity (`U_i = τ_i ẋ_i^V`, 1.2e-15,
  `∂U_i/∂τ̇ ≡ 0`) and the part that is a *premise* (`ẋ_i^V = ẋ^V` ⇒ (11) collapses onto (36), 5.6e-17;
  per-arm offsets make `τ` visible again at 5.0e-2). Recorded as D014.
- T05: LVI fixed point vs an exact active-set referee 3.9e-09 in 1133 iterations, passivity identity
  `V̇ + ψ = YᵀU` at 8.3e-17, and `V̇ > 0` on 2999/3000 steps — Theorem 3 is an energy balance, **not**
  a Lyapunov decrease.
- T07: the 36-D decision function reproduces the official `y_est` sign on **24892/24892** points
  (agreement with `y_train` 0.9874); calibration invariants I1–I6 hold; Eq.(26) chain rule 9.2e-08 at
  κ = 1 and κ = 2. The sparse CPSP model scores ACC 0.9313 on the same points
  (`IN_SAMPLE_INDEPENDENT_EVALUATION`, D008 — no comparison with the paper's FPR/TPR).
- N7.3 had to be redesigned: the two published σ differ by 0.28 % and swapping them costs only 0.0008
  agreement, so the swap is reported as a metric and the negative control injects the harmful defect
  instead (`-g` read as width → 0.5670). Recorded as D013.
- Next: G3 (T08 — SCA inside the closed-loop QP), then G4 (T10, mandatory).
- Scope unchanged: T09 `NOT_AUTHORIZED_THIS_CYCLE`.

## 2026-10-20 — P5 numerical reproduction: G3 green

- **G3 (integration layer) PASS**: T08 13 checks (7 positive / 6 negative), 0 failed, 85.9 s.
  Cumulative G1+G2+G3: **103 checks (57 pos / 46 neg), 0 failed, 201.4 s**.
- T08 wires (17d) with the Q3 sign, (26) and (21a/b) around the official 2-D CPSP model used as the
  learned boundary oracle in its native coordinates. `min_t Γ_raw = +2.1813` with SCA on and **0**
  crossings, against `−2.3942` and **656** crossings in the matched SCA-off control.
- The SCA row is active on 50.1 % of the steps with a positive dual multiplier, the Eq.(26) chain rule
  matches central differences at 1.2e-09, and `min_t Γ_raw` converges over
  `dt ∈ {5e-3, 2.5e-3, 1.25e-3}` to 1.4e-03.
- Three findings contradict the plan and are reported as measured (D015, D016): the SCA feature must
  not be the task coordinate or (17d) can never bind; `λ = 0` is *stricter* away from the wall, not
  looser; and `PAPER_FALLBACK` as a hard row is unsatisfiable (demands Γ̇ ≥ 1000 against 28.2), i.e. it
  is a soft-formulation device.
- Next: G4 (T10, mandatory — asynchronous→synchronous switch plus SCA on/off).
- Scope unchanged: T09 `NOT_AUTHORIZED_THIS_CYCLE`.

## 2026-10-20 — P5 numerical reproduction: G4 green, D082 ceiling reached

- **G4 (end-to-end) PASS**: T10 12 checks (7 positive / 5 negative), 0 failed, 142.2 s.
  Cumulative G1+G2+G3+G4: **115 checks (64 pos / 51 neg), 0 failed, 344.2 s**, all four gates `PASS`.
- The chain `τ → LPV DS → virtual object → QP → LVI` runs end to end on a 6-DOF planar dual arm with
  both tips as the task: `τ` integrates from `ε = (0.02, 0.03)` to `(0.982, 0.988)` and the
  asynchronous→synchronous switch lands at `t_switch = 2.800 s` (window `[1, 5] s` declared before the
  run). `min_t Γ_raw = +2.0700` with 0 boundary crossings against `−2.3147` and 534 crossings in the
  matched SCA-off control.
- The e2e claim is deliberately narrowed: the hard (17d) row makes the QP **infeasible on 370/800
  steps (46 %)**, all attributed to the row (same QP without it: `OPTIMAL` 370/370; reference velocity
  there `≤ 0.0279`). A second run drops the row on exactly those steps instead of freezing and still
  gets `min Γ = 1.2400` with 0 crossings, so the row — not the freeze — carries the guarantee. No
  timing or tracking-accuracy claim is drawn from this run (D018).
- Theorem 3 is reported as measured: the identity `V̇ + ψ = YᵀU` holds at every QP solution
  (`9.1e-13`, relative `3.7e-17`), while the plan's telescoping ledger does **not** close
  (`−328.4` against a scale of `328.7`) because every step re-solves a different LVI; the entire
  non-closure is `−ΔV` to `2.8e-14`. The ledger is reported, never a pass criterion (D017).
- `λ = 0` again behaves opposite to the plan's prediction (`min Γ` 4.2235, 0 crossings, 594 infeasible
  steps): it is a strict no-decrease cone, not a looser row. `dt` doubled moves `min Γ` 2.0700 → 2.0600
  and `t_switch` 2.800 → 2.820 s, so the step size is really in the loop.
- Ceiling: `ALGORITHM_NUMERICAL_VERIFIED (D082)`. `FULL_PAPER_REPRODUCED` stays abandoned (hardware +
  unpublished training set + CVXGEN). T09 remains `NOT_AUTHORIZED_THIS_CYCLE` and is excluded from
  every total above.
- Reports: `p5/reviews/P5_T10_POST.md`, `p5/P5_GATE_LOG.md`, `p5/evidence/P5_impl_checks.{json,md}`,
  figures `t10_e2e_triptych.png` / `t10_phase.png` / `t10_sca_ablation.png`.
