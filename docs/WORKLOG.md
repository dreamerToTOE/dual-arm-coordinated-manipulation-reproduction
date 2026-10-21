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

## 2026-10-21 — P1 G0 paper study and reproduction planning
- Created `reproduce-p1-numerical-20261021` from `main@a596c973`; no accepted P2/P3/P4/P5 branch content was modified.
- Read the full 19-page T-RO paper (PDF SHA256 `8b4589ce…de3c`), rebuilt every equation's assumptions/inputs/outputs/dimensions, and resolved the absolute-pose equation by three independent arguments (group midpoint, base-frame invariance, official kernel).
- Audited both official repositories at two fixed snapshots each (`dual_arm_gpu_mpc@fe5b49f7` / `@1820a9e8`; `cuda_dq_kernel@231f130e` / `@c762b7d6`), recording tarball and key-file SHA256, dependency stacks, structure, examples, model assets, and missing components.
- Built the paper-equation-to-source map (35 items: 17 ORIGINAL, 7 CODE_MODIFIED, 4 MISSING, 1 AMBIGUOUS, 6 EXTERNAL_DEPENDENCY) and the 16-row original-experiment matrix with per-task reported values.
- Wrote the 16-module proposed reproduction matrix (A–G) with independent oracles, positive/negative controls, quantitative acceptance criteria, dependencies, compute cost, and expected fidelity.
- Wrote the implementation plan as DRAFT only. No dependency was installed, no CUDA extension compiled, no GPU context initialized, and no paper algorithm was executed.
- Open scientific decisions Q1–Q10 are recorded in `p1/P1_IMPLEMENTATION_PLAN.md` §5; G1 must not start before they are resolved.
