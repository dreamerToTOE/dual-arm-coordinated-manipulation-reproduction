# EXPERIMENT_LOG

Append-only experiment index.

At repository initialization, no experiments had been run.

## 2026-09-30 20260930_TASK00_mujoco_smoke
Task: TASK00
Baseline: none; environment smoke test only
Platform: existing isolated MuJoCo .venv
Commit at probe: 9f71e0a78a9d852d060b4e7e4c3225558d1d9bb1
Seed: not applicable
Command: see results/20260930_TASK00_mujoco_smoke/metadata.yaml
Config: inline one-joint sphere model
Result: PASS
Key metrics: MuJoCo 3.13.0; one mj_step advanced simulation time to 0.002 s
Artifacts: results/20260930_TASK00_mujoco_smoke/
Notes: This is not a dual-arm force-control or paper-reproduction experiment.

## 2026-09-30 20260930_TASK01_static_geometry
Task: TASK01
Baseline: none; candidate geometry check only
Platform: system Python 3 + PyYAML; analytic validation (not Isaac)
Commit at probe: ca2b1f75a85c32bcad87b193328cbe7424680183
Seed: not applicable
Command: `python3 scripts/validate_benchmark_candidate.py`
Config: `configs/benchmark/benchmark_v1.yaml` (DRAFT)
Result: PASS for internal analytic geometry; TASK01 itself remains IN_PROGRESS
Key metrics: 0 failed dimension checks; 30 unresolved/null configuration fields
Artifacts: `results/20260930_TASK01_static_geometry/`
Notes: No physical contact, collision, sensing or timing validation was performed.

## 2026-09-30 20260930_TASK01_contact_protocol
Task: TASK01
Baseline: none; candidate protocol and geometry check only
Platform: system Python 3 + PyYAML; analytic validation (not Isaac)
Commit at probe: 93e7e54 (parent of uncommitted draft)
Seed: not applicable
Command: `python3 scripts/validate_benchmark_candidate.py`
Config: `configs/benchmark/benchmark_v1.yaml` (DRAFT)
Result: PASS for internal analytic geometry/protocol; TASK01 itself remains IN_PROGRESS
Key metrics: 0 failed checks; 36 unresolved/null configuration fields; 1° yaw consumes 1.038 mm nominal center clearance
Artifacts: `results/20260930_TASK01_contact_protocol/`
Notes: No physical contact, collision, sensing or timing validation was performed.

## 2026-09-30 20260930_TASK01_center_right_physical
Task: TASK01
Baseline: none; experimental Task27 fifth-Cube probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit at probe: 76d24dc (new repo), d93f285 (legacy repo), with working-tree test patch later committed unchanged as 631b1f6
Seed: not fixed in legacy OMPL
Command/config: `results/20260930_TASK01_center_right_physical/metadata.yaml`
Result: PASS, one physical run; four fixtures pre-placed
Key metrics: Cube 05 final center 0.603 mm; +X wall gap 0.586 mm; +Y/-Y side gaps 1.361/1.639 mm; peak joint torque 35.96 Nm
Artifacts: metadata, `reports/TASK01_CENTER_ARM_SYMMETRY.md`, external raw ROS log listed therein

## 2026-09-30 20260930_TASK01_center_left_physical
Task: TASK01
Baseline: none; experimental Task27 fifth-Cube probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit at probe: 76d24dc (new repo), d93f285 (legacy repo), with working-tree test patch later committed unchanged as 631b1f6
Seed: not fixed in legacy OMPL
Command/config: `results/20260930_TASK01_center_left_physical/metadata.yaml`
Result: PASS, one independent physical run; four fixtures pre-placed
Key metrics: Cube 05 final center 0.669 mm; +X wall gap 0.633 mm; +Y/-Y side gaps 1.719/1.281 mm; peak joint torque 35.87 Nm; one pre-close reacquire
Artifacts: metadata, `reports/TASK01_CENTER_ARM_SYMMETRY.md`, external raw ROS log listed therein
Notes: Both arms HOME. Left and right results differ; no statistical equivalence is claimed.

## 2026-10-02 20261002_TASK01_center_repeatability
Task: TASK01
Baseline: none; [EXPERIMENTAL] legacy Task27 Cube 05 arm-symmetry probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Seed: uncontrolled legacy OMPL (no fixed-seed claim)
Command/config: Four per-run `results/20261002_TASK01_center_{right,left}_{02,03}/metadata.yaml` files; benchmark draft `configs/benchmark/benchmark_v1.yaml`
Result: Four new physical runs PASS with both arms HOME; including 2026-09-30, right 3/3 and left 3/3 PASS. TASK01 remains IN_PROGRESS.
Key metrics: right center error [0.603, 0.429, 0.374] mm, mean 0.469 mm; left [0.669, 0.408, 0.561] mm, mean 0.546 mm; maximum side-gap imbalance 0.582/0.802 mm (right/left).
Artifacts: `reports/TASK01_CENTER_ARM_SYMMETRY.md`, four per-run metadata files, external raw ROS logs named there; scripts `task01_capture_final_pose.py` and `summarize_task01_center_trials.py`.
Limitations: Four fixture cubes were pre-placed; no contact wrench; motion-time PhysX/USD pose disagreement remains open (BUG-005). `move_group` repeatedly segfaulted during Ctrl-C teardown after completed task runs (BUG-004).
Notes: Both arms HOME. Not a reproducibility or statistical symmetry result.

## 2026-10-03 TASK01 known-motion sensor diagnosis/calibration
Task: TASK01
Baseline: none; [EXPERIMENTAL] measurement calibration, not contact control
Platform: Isaac Sim 4.5; external ROS2 Humble observer
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus uncommitted measurement changes committed with this report
Seed: no random sampling
Command/config: Per-run metadata in results/20261003_TASK01_pose_timing/, physics_ros_30hz/, physics_ros_debug/, physics_ros_clean_30hz/, physics_ros_zero_damping_30hz/ and physics_ros_zero_damping_20hz/
Result: Initial no-ROS pose diagnosis passed. Mixed-library startups failed; clean-ROS angular calibration initially failed because the known-motion model omitted angular damping. Explicit zero damping on the free calibration body then produced two PASS_SENSOR_CALIBRATION results; gates unchanged.
Key metrics: 120 motion samples/run; p_max=0.000312946/0.000312902 mm, angle_max=0.000864737/0.000864742 deg (30/20 Hz frames, 60 Hz physics); callback errors=0; legacy USD callback lag=6.667/10.000 mm; scaled-quaternion error up to 27.464 deg.
Artifacts: Per-run metadata and ignored raw JSONL/JSON; reports/TASK01_PHYSICS_POSE_MEASUREMENT.md
Boundary: Deterministic no-contact free body; not manipulation accuracy or a benchmark gate. Explicit zero damping is not a change to Task27 physics.

## 2026-10-03 TASK01 fixture physics-channel integration
Task: TASK01
Baseline: none; [EXPERIMENTAL] pre-placed four-Cube fixture + legacy right-arm fifth-Cube task
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus uncommitted measurement adapter; legacy unchanged at 631b1f65656d025c1bb2173e874192f3fe4d355a
Seed: uncontrolled legacy OMPL
Command/config: results/20261003_TASK01_fixture_sampler_startup/metadata.yaml (failed startup) and results/20261003_TASK01_fixture_physics_channel/metadata.yaml (physical run)
Result: Unsupported tuple constructor argument caused first startup FAIL without robot commands. Corrected list initialization; fresh-scene right-arm full Cube 05 task PASS and independent physics recorder PASS.
Key metrics: center error 0.520 mm; deep gap 0.505 mm; side gaps 1.374/1.626 mm; peak joint torque 35.41 Nm; both arms HOME; logged task duration 215.142 s. Recorder: 14,295 samples, no missing physics steps, no errors, timestamps increasing. Final physical yaw 0.026334 deg versus legacy Bridge 0 deg.
Artifacts: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md; selected result summary + metadata; ROS log /home/ubuntu2004/.ros/log/task27_five_cube_center_insert_32050_1791006079693.log; ignored 32-MB physics snapshot JSONL.
Boundary: New topic is read-only, controller still consumes legacy Bridge; no claim of a synchronized wrench/TCP contract or complete five-Cube fixture construction. MoveIt SIGINT -2 today does not resolve prior BUG-004.

## 2026-10-03 TASK01 final measurement regression / empty-input guard
Task: TASK01
Baseline: none; [ENGINEERING] final measurement checks, [EXPERIMENTAL] known-motion fixture
Platform: Isaac Sim 4.5 + external ROS2 Humble; guard test without an Isaac publisher
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus final working-tree measurement changes
Seed: no random sampling / not applicable
Command/config: results/20261003_TASK01_final_calibration_30hz/metadata.yaml and results/20261003_TASK01_recorder_empty_guard/metadata.yaml
Result: Final 30 Hz external calibration PASS including exact position/quaternion equality of PoseArray and JSON snapshot. Empty stream yielded saved FAIL summary and exit 1 (negative test PASS, not sensor success).
Key metrics: 120 motion / 150 total pose samples; p_max=0.000312945784 mm, angle_max=0.000864737421 deg; zero callback errors. Empty guard: zero samples, 2-s startup timeout.
Artifacts: Per-run metadata, ignored raw summaries, reports/TASK01_PHYSICS_POSE_MEASUREMENT.md
Boundary: No paper controller, no altered benchmark gate; failure is kept distinguishable from physical task success.

Recommended entry:
```text
## <date> <run_id>
Task:
Baseline:
Platform:
Commit:
Seed:
Command:
Config:
Result: PASS/FAIL
Key metrics:
Artifacts:
Notes:
```
