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

## 2026-09-30 — TASK01 benchmark candidate study started
- Compared the repository benchmark requirements with the existing Task27 Cube/side-suction/carriage geometry and control constants.
- Asked whether the frozen benchmark should use that validated scene as its geometric starting point or a separately designed scene.
- No benchmark values have been frozen; paper algorithms remain untouched.
- Added reports/TASK01_SOURCE_PARAMETER_MATRIX.md: source-grounded Task27 geometry/material/robot values, dimensional checks and explicit decisions still needed before any benchmark_v1 freeze.
- Isaac/MoveIt runtime had exited before TASK01 validation; no fresh physical benchmark was run.

## 2026-09-30 — TASK01 Task27-derived draft assembled
- Recorded user confirmation of Task27 as the geometric starting point in D003.
- Added `configs/benchmark/benchmark_v1.yaml` with source hashes, frames, dual-FR3/rail/L-tool geometry, cube/carriage coordinates, nominal side TCP transforms and explicit nulls for unapproved values.
- Added an analytic checker for internal dimension, handoff, wall-flush and nominal grasp consistency. It passed and enumerated 30 unresolved fields.
- No fresh Isaac simulation was run: no Isaac process was active during this iteration. TASK01 remains IN_PROGRESS; do not interpret the static pass as physics or paper-method validation.

## 2026-09-30 — TASK01 contact-protocol clarification
- Recorded the user's distinct Cube 01–04 dual-arm corrective push/press protocol and Cube 05 precision-staged single-arm insertion protocol in D004 and the draft YAML.
- Extended the static checker to verify four fixture targets and the required single-arm Cube 05 contact topology; it passed with 36 explicit unresolved fields.
- Calculated the nominal center-Cube geometric sensitivity: 1° yaw consumes about 1.038 mm of the 1.5-mm per-side clearance, leaving about 0.462 mm for lateral offset before any physical margin.
- No robot, Isaac or paper baseline was run. The draft remains IN_PROGRESS, not FROZEN.

## 2026-09-30 — TASK01 center-Cube left/right physical probe
- Added a separate Isaac probe wrapper that loads Task27, directly pre-places Cubes 01–04 into their intended cells and waits for real physics settle before permitting only batch 5 feed.
- Added a Task27 test parameter to choose left or right as the fifth Cube's -X-face pusher; its default remains the original right arm. Added a 100 nm float32 comparison epsilon to the inner fixture side-gap boundary (measured 38 nm rounding overshoot), without changing target cells or the millimeter-scale threshold.
- Built `fr3_dual_palletize`, then passed left and right MoveIt/FCL planning-only checks.
- Ran two clean headless Isaac 4.5 scenes, one per physical arm test. Both completed the fifth Cube and returned HOME. Right/left center errors were 0.603/0.669 mm; see `reports/TASK01_CENTER_ARM_SYMMETRY.md` for gap and torque details.
- This is [EXPERIMENTAL] evidence for single-Cube physical feasibility, not a full five-Cube benchmark run or paper-method result. TASK01 remains IN_PROGRESS.
