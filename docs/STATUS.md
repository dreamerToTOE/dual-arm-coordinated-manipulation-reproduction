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
