# WORKLOG

Append-only project work log.

## 2026-09-29 — Repository initialization
- Created V2 architecture for five-paper reproduction.
- Defined dual-platform strategy: MuJoCo for contact/force unit validation; Isaac/ROS2 for final benchmark.
- Defined mandatory traceability rules for Codex.
- Next task: TASK00 Environment Audit.

## 2026-09-30 — TASK00 environment audit started
- Cloned the repository and opened `task00-environment-audit` from `main`.
- Began read-only host, ROS 2, MoveIt, Isaac Sim, model and runtime-interface checks.
- No paper algorithm or benchmark geometry has been changed.

## 2026-09-30 — TASK00 environment audit completed
- Recorded host/GPU/ROS/MoveIt/OMPL/FCL/Isaac/MuJoCo versions and exact probe commands in reports/TASK00_ENVIRONMENT.md.
- Corrected the initial system-Python-only MuJoCo finding: MuJoCo 3.13.0 works in the existing isolated .venv; its minimal step was logged under results/.
- Expanded the legacy dual-FR3 URDF/SRDF, sampled live ROS interfaces while available, and marked unavailable or untested scientific interfaces explicitly.
- TASK00 PASS is an audit result, not a claim of benchmark readiness. TASK01 is READY but cannot be FROZEN before user review.

## 2026-10-20 — P3 paper-first study and arm-level numerical reproduction (D082)
- Locked the P3 paper (DOI `10.1109/LRA.2022.3187497`), audited Eq.16–28 from **page images**
  (`pdftotext` misplaces the equations) and registered the ambiguity set A1–A7.
- Implemented `baselines/p3_peg_in_hole/{patterns,stages,control,fixtures}.py` with independent
  oracles under `p3/oracles/` (scalar closed forms, complementary projector, index loops).
- T01 patterns `54306928`; T02 stage composition `6aa406e5`; T03 selection/frames `bf3fdec7`;
  T04 torque law `f01e36f2`; T06 deterministic integration `dedd8e90`; report `e1f7d874`.
- Post-delivery review `11542aee` required four corrections (R1 push-axis test, R2 max-component vs
  norm notation, R3 force/moment jump separation, R4 append-only registers). Corrections applied;
  see `p3/reviews/P3_CORRECTION_POST_20261020.md` for the amended count (92/92) and new run IDs.
- No contact model, simulator, hardware, or controller was added; T05 stays optional and unexecuted.
