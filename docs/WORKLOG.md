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

## 2026-10-02 — TASK01 center-Cube exploratory repeatability
- Restarted the Isaac fixture scene and MoveIt independently for four more physical Cube 05 runs (right/left/right/left). With the two earlier runs, each pusher arm now has three completed runs, all with `Task27 batch 5 PASS` and both arms HOME.
- Right arm final center errors: 0.603, 0.429, 0.374 mm; left arm: 0.669, 0.408, 0.561 mm. This is only fixed-scene exploratory repeatability, not proof of statistical equivalence or a frozen benchmark. OMPL seed is not controlled.
- Added read-only final six-DoF Bridge pose sampling, a read-only PhysX/USD pose-source comparison in the headless runner, and a ROS-log parser that only calls a run PASS when the final Task27 PASS line exists.
- In the local Isaac 4.5 `python.sh` clean terminal, ROS Bridge needed explicit bundled Humble `LD_LIBRARY_PATH` and `RMW_IMPLEMENTATION`; the first failed Bridge startup sent no robot commands. Corrected reproduction command in the report.
- Observed motion-time PhysX/USD pose-source disagreement up to about 2.8 mm but zero positional difference after settle (printed precision). Reproduced post-task MoveIt Ctrl-C teardown segfault on each completed run. Recorded BUG-004/BUG-005; neither changed the task geometry or controller.

## 2026-10-03 — TASK01 physical pose/time channel diagnosis and calibration
- Isolated USD position frame-update lag from a separate scaled-transform quaternion extraction defect. At 0.2 m/s, callback position lag grew from 6.667 to 10.000 mm when application frames changed from 30 to 20 Hz; after app update positions match. Raw scaled USD rotation extraction had up to 27.464 deg error, versus 0.000154 deg after removing scale. Marked old Bridge yaw invalid for physical 6D claims without erasing the historical data.
- Added a separate opt-in read-only live-PhysX pose/velocity snapshot with simulation timestamp and step number, external ROS calibration/stream recorders, and a launcher that removes inherited system ROS Python/library paths. No Task27 scene/control source, benchmark value or paper algorithm changed.
- Kept failed attempts visible: mixed ROS type-support startup, a free-body angular expectation that omitted default damping, and an unsupported tuple argument to the five-body view. Corrected those causes without relaxing gates. Zero damping is authored only on the calibration fixture.
- External ROS known-motion calibration passed at 60 Hz physics with both 30/20 Hz app frames (120 motion samples each; maximum position error about 0.000313 mm, angle error about 0.000865 deg).
- One additional right-arm full Cube 05 physical probe passed, center error 0.520 mm, both arms HOME. Separate 250-s recorder received 14,295 contiguous snapshots without record errors. PhysX final yaw was 0.026334 deg while the old Bridge returned 0 deg. Report and complete commands: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md.
- Stopped the processes started by this iteration. MoveIt shutdown yielded SIGINT -2 rather than prior -11; BUG-004 remains open. TASK01 remains IN_PROGRESS with 36 unresolved fields; TASK02 and paper implementations remain untouched.
- Final code regression re-ran 30 Hz calibration with explicit position AND quaternion snapshot equality: all checks PASS. Empty-input recorder test saved FAIL and exited 1 as expected. Python compilation, shell syntax, draft analytic check (36 unresolved fields, unchanged SHA256) and diff checks passed; legacy tracked source remains unchanged.

## 2026-10-03 — TASK01 contact/mount force feasibility checkpoint
- Added a same-step collision sampler combining normal and friction impulses, contact locations and moments about an explicit body origin. Path ordering and shared contact/friction buffers are checked; 8 offline tests PASS.
- Known-load calibration at 60/120 Hz PASS: 0.8 kg support 7.848 N, horizontal friction -2 N, resisting moment about -0.04 Nm, rotated-wall 4 N direction. Dual suction holds the body while collision signal stays zero, confirming this channel does not measure D6 constraint loads.
- Independent mount reaction probes at 0/90 deg roll and nonzero COM/principal axes PASS; identified link-axis components/about-link-origin convention in this API. Actual FR3 gravity/inertia compensation has not been validated.
- Actual FR3 topology retains about 1.946277 kg in the link8/hidden hand/finger/hand_tcp branch. Do not silently delete mass or treat its roughly 19.093 N empty support as contact force.
- Retained startup failures: incorrect 4.5 PhysicsContext getter, SingleRigidPrim constructor keyword, nonexistent feed-state constant, and overwritten scene namespace. No failed startup sent robot commands. Fast-shutdown exit 0 is not a PASS criterion.
- Added full normal-feed five-Cube measurement runner without pre-placement. All five planning-only batches passed; physical execution is underway at this checkpoint. Benchmark YAML remains unchanged with 36 unresolved fields, TASK02 stays TODO.

## 2026-10-03 — TASK01 reference correction and final full-flow result
- Supersedes the checkpoint's reference-point conclusion: early COM fixtures had rigid-body scale, which also scaled authored COM/anchors. Preserve their software PASS but invalidate origin inference. Final unscaled fixture verifies actual COM=5 mm and tests nine axes/point hypotheses; only incoming joint axes/about joint anchor matches (3.436e-6 N / 4.430e-7 Nm error). Final code regression repeats this result.
- Collision calibration remains PASS (13 checks each at 60/120 Hz); 8 offline tests, final Python compilation, analytic draft and diff checks PASS. Benchmark hash unchanged with 36 nulls.
- Normal five-batch preflight PASS, but actual run placed only Cube 01 then safely failed Cube 02 before suction: asymmetry 0.968 -> 0.315 -> 0.339 mm against 0.300 mm gate, with mandatory 0.650 mm minimum correction (BUG-008). PhysX final asymmetry 0.338941 mm independently confirms. No later physical task was advanced.
- 37,236 same-step snapshots, zero measurement errors; not full task PASS. Cube 01 PhysX yaw -1.095465 deg contradicts legacy scaled-USD near-zero yaw (BUG-006). Deep-wall collision peak 139.098 N is not suction/internal force or an approved gate.
- Own full-run processes stopped. MoveIt teardown -11 recurred (BUG-004). Final added authored FR3 joint-frame audit failed on remote asset-root lookup before control commands; new audit remains unverified.
- Reports distinguish force calibration, failed full flow and 36-field freeze review. Metadata retains negative starts and invalidated fixtures; heavy raw remains local/ignored. No legacy tracked model/control or protected-directory change.
- TASK01 IN_PROGRESS, TASK02 TODO. Next scoped correction fix must retain gates, followed by normal five-Cube re-run and remaining model/frame/numeric review; no paper force controller yet.
