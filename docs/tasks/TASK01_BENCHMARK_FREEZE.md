# TASK01 — Freeze Benchmark V1

Status: IN_PROGRESS (candidate study; benchmark_v1 not yet reviewed or frozen)

## Current progress (2026-10-02)
- User confirmed the existing Task27 dual-FR3, L-side-suction and truck-box scene as the **geometric starting point**, not as a wholesale approval of its numerical parameters or thresholds.
- Draft candidate: `configs/benchmark/benchmark_v1.yaml`; analytic checker: `scripts/validate_benchmark_candidate.py`.
- Initial static geometry passed with 30 unresolved fields. After recording the user-confirmed B-fixture/B-center contact split, the latest static check still passes and has 36 unresolved fields (new alignment/force gates were made explicit).
- Fresh [EXPERIMENTAL] Isaac 4.5 probe: four Cubes directly pre-placed, then only Cube 05 executed with the right or left pusher in separate clean scenes. Right and left each passed 3/3 physical runs; final center error was at most 0.603/0.669 mm respectively. Detailed Ground Truth and boundaries are in `reports/TASK01_CENTER_ARM_SYMMETRY.md`. This small, non-seeded sample does not validate full four-Cube fixture construction, long-term reliability, calibrated contact forces, or the frozen benchmark.
- New instrumentation records final Bridge pose and compares motion-time PhysX and USD pose sources read-only. The sources differed transiently by up to about 2.8 mm in observed push samples, then converged after settle; this must be resolved as a measurement/timing issue before dynamic contact metrics are frozen (BUG-005). MoveIt shutdown also repeatedly segfaulted after successful controller completion (BUG-004).
- The benchmark remains **DRAFT / IN_PROGRESS**. No paper baseline may use it as a frozen common test yet.

## Goal
Freeze one common dual-FR3 Cube/carriage benchmark before tuning any paper method.

## Measurement follow-up (2026-10-03)
- Diagnosed the motion-time position mismatch as USD application-frame lag relative to PhysX physics steps. Separately confirmed that extracting a quaternion from the scaled Cube world matrix corrupts the old Bridge rotation. Historical Bridge yaw values are retained but must not be treated as accurate 6D measurements.
- Added an opt-in read-only physics pose/velocity channel with a single simulation timestamp and physics-step number per snapshot. External ROS known-motion calibration passed at 30 Hz and 20 Hz frame updates with 60 Hz physics: maximum position error about 0.000313 mm and angular error about 0.000865 deg. This is sensor-plumbing evidence, not contact/benchmark performance.
- Details, failures, source references and complete commands: `reports/TASK01_PHYSICS_POSE_MEASUREMENT.md`. Old Task27 control/scene sources and all 36 unresolved benchmark fields remain unchanged. TASK02 stays TODO pending review/freeze.
- A further real right-arm Cube 05 task passed (0.520 mm final center error, both arms HOME), while the separate recorder obtained 14,295 contiguous five-Cube snapshots with no record errors. This validates measurement integration with the existing physical task, not a new controller or full five-Cube benchmark.

## Force feasibility follow-up (2026-10-03)

- Independent known-load collision calibration passed at 60/120 Hz, including static friction, nonzero torque, rotated-wall force direction and same-step pose/contact stamping. Collision telemetry demonstrably omits suction D6 constraint loads.
- Independent mount-joint load probes passed at 0/90 deg roll, but their coincident frames do not identify the force reference. The final unscaled COM/principal/joint-anchor/joint-axis test identifies incoming joint axes / about joint anchor. Earlier scaled-body origin identification is invalidated and retained in records. This is not a calibrated FR3 TCP contact estimator or paper controller.
- Actual FR3 topology exposes link8 raw reactions, but its downstream hidden hand/finger/hand_tcp bodies retain mass. Gravity/inertia compensation and TCP moment shifting remain necessary; no body mass was removed.
- Added a separate full five-Cube headless measurement runner: normal feed, no pre-placed four-Cube fixture, unchanged legacy controller. Five-batch planning preflight passed, but physical run placed only Cube 01 then stopped at Cube 02 pre-close: symmetry residual 0.968 -> 0.315 -> 0.339 mm versus 0.300 mm gate, with mandatory 0.65 mm minimum correction. No threshold was relaxed. Reports: `TASK01_FORCE_MEASUREMENT_FEASIBILITY.md`, `TASK01_FULL_FIXTURE_CONTACT_PROBE.md`.
- Benchmark YAML is unchanged; its 36 null fields still require resolution/review, not automatic filling from a successful calibration.
- Review queue: `reports/TASK01_FREEZE_REVIEW_CHECKLIST.md` lists all 36 null fields and already-numeric but unapproved model choices. The last added real-FR3 authored-joint-frame startup audit failed on asset-root availability; that check and TCP compensation remain unvalidated.

## Codex actions
- Define FR3 base poses.
- Define cube size, mass and friction/contact parameters.
- Define left/right grasp transforms.
- Define carriage geometry and entrance frame.
- Define PRE_PUSH and insertion target/depth.
- Define physics dt, control dt and seed policy.
- Define all success/failure tolerances for Benchmark A/B.
- Define C0–C5 insertion perturbations.
- Validate geometry in Isaac; validate P2/P3 reduced version in MuJoCo if needed.

## Outputs
- `configs/benchmark/benchmark_v1.yaml`
- benchmark scene notes.
- benchmark hash/version.

## PASS/FROZEN
All values reviewed by user. Then mark FROZEN. Any later change requires DECISIONS entry and benchmark version bump.
