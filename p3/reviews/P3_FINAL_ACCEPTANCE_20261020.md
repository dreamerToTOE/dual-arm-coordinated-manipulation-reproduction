# P3 Final Acceptance — 2026-10-20

**Decision: ACCEPT and ARCHIVE the P3 D082 numerical reproduction.**

**Verified submitted revision:** `e0de3b9fe8a2c46605dfeb307592de71910017dc` on branch `reproduce-p3-paper-study-20261019`.

## Scope accepted

- Arm-level paper equations (16)–(28): perturbation patterns, four-stage compositions, force/position selector and coordinate transforms, feedforward joint-torque law.
- Deterministic command-pipeline demonstrations for four paper-described stage sequences.
- Independent mathematical oracles, negative tests, source-PDF page-image audits, and preserved numerical JSON evidence.
- Acceptance label: **`ALGORITHM_NUMERICAL_VERIFIED (D082 scope)`** — **not `FULL_PAPER_REPRODUCED`**.

## Evidence reviewed

- Original T01 21/21 and T04 20/20 (unchanged).
- Corrected T02 16/16: `results/20261020_104220_P3-T02_stages/results.json`.
- Corrected T03 23/23, including corrected physical push direction and literal-frame negative control: `results/20261020_104153_P3-T03_selection/results.json`.
- Corrected T06 12/12: `results/20261020_104237_P3-T06_integration/results.json`.
- Total archived recorded evidence: **92/92 PASS**. Reviewed stored code, records and results; reviewer did not run every test on the original machine.
- Final artifact: `p3/reports/final/P3_FINAL_REPORT.md`, alongside DOCX, PDF, equation comparison CSV, scope matrix CSV, figures.

## Scientific restrictions and unresolved items

- A1 is **open source ambiguity**, not resolved by the original paper: Eq.(19)/Fig.5 use task-z pushing while Eq.(28) selects hole-x; an explicit `R_task_to_hole` (`e_z` to `e_x`) is an **[ADAPTATION]**. The literal unrelabeled reading need not suppress the physical push axis.
- No object dynamics, calibrated robot, contacts, insertion completion, hardware success statistics, original Fig.9/11 object trajectories, dexterous-hand subsystem or MuJoCo/Isaac migration was reproduced.
- All numeric control examples remain TEST_FIXTURE, not experimentally matched original parameters.
- P3-T05 quasi-static contact surrogate remains `NOT_EXECUTED_OPTIONAL`.
- TASK11–15 MuJoCo/Isaac roadmap items are **not** marked complete merely because this separate D082 numerical study is accepted.

## Next approved stage

P3 numerical reproduction is closed. Begin **P5 paper study and proposed numerical reproduction matrix**, not implementation, subject to review before coding. Keep P4's full virtual-simulation objective separate and preserve P2/P3 history.

**P5 paper card:** `references/P5_qp_coordination.md`. Exact paper: Salehian, Figueroa & Billard (2018), *A unified framework for coordinated multi-arm motion planning*, IJRR 37(10):1205–1232, DOI 10.1177/0278364918765952. Study must include asynchronous/synchronous task-space dynamical systems, synchronization allocation, centralized QP inverse kinematics, and learned sparse-kernel SCA boundary. An FCL distance-based QP is an **ADAPTATION**, not faithful proof of learned SCA.
