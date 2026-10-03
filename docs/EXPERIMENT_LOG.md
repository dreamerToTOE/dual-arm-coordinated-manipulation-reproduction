# EXPERIMENT_LOG

## 2026-10-03 — Cube04 precision variant startup
- C++ policy regression and Python syntax PASS. Package build PASS; non-portable directive-inside-logging-macro warning removed before final test build.
- `20261003_TASK01_cube04_precision_01`: FAIL_NEW_PROBE_STARTUP_API, no controller execution; initially passed extra argument to legacy callback subscription; raw startup preserved. Final probe uses existing verified post-step API and exception artifact writer.
- `20261003_TASK01_cube04_precision_02`: RUNNING_CHECKPOINT; first three pre-placed/physically settled, Cube04/05 physical execution pending. Not full-five proof; scene/material/final gates unchanged.

## 2026-10-03 — TASK01 fixed-contact TCP roll diagnostic
- Same `20261003_TASK01_fixture_protocol_clearance` run family, additional `roll_sweep_summary.json`: fixed face center/normal, TCP roll 0..345 deg in 15 deg steps, 24/24 poses have lateral rod/Cube03 OBB intersection, zero clear box-only poses. No robot commands; no arbitrary-contact/IK completeness claim. New regression passes; 18 Python offline tests total.

## 2026-10-03 — TASK01 controlled hold, protocol geometry and actual material
- `20261003_TASK01_fr3_static_payload_v2`: PASS_CONTROLLED_HOLD_AND_CUBE01 / PARTIAL_METROLOGY. Default-zero optional 7-s task-thread hold, legacy 76408c8; controller exit 0, placement/HOME complete. 34,510 snapshots, 238 full-rate load samples. Mean net-support error 0.000370 N but instantaneous RMS 0.494278 N / moment mean 0.014902 Nm and velocity discrepancy persist. Raw six-step diagnostic was aliased; full-rate reanalysis does not convert this into a sensor PASS.
- `20261003_TASK01_fixture_protocol_clearance`: REQUIRED_SIDE_POSE_INTERFERES. Read exact existing xacro and prior full-flow Cube03 PhysX pose; Cube04 centered right helper support boxes intersect neighbor, minimum lateral SAT axis overlap 33.524 mm. Analytic only, no commands/model changes. Metadata + summary tracked.
- `20261003_TASK01_mass_material_audit`, `_v2`, `_v3`: Initial two PARTIAL audits retained; final PASS_MASS_AND_SHAPE_READOUT / MODEL_REVIEW_PENDING. Cube actual mass 0.800000012 kg, static/dynamic friction 0.5/0.5, restitution 0.0. Declared 0.90/0.75 material deleted by cleanup; no effective combine-rule freeze. Initial wrong tool path corrected in reader only; no scene changed.
- `python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py' -v`: 17/17 PASS. YAML checker still analytic PASS / 36 unresolved, not TASK01 PASS. Report `TASK01_RUNTIME_REVIEW_20261003.md` contains commands, results and boundaries.
- MoveIt SIGINT teardown again exit -11; retained full-five raw launch log. Test processes fully stopped; no ordinary controller failure inferred from teardown.

## 2026-10-03 — TASK01 completed normal feed and retained failed metrology
- results/20261003_TASK01_full_five_corrected_01/: PASS_LEGACY_FIVE_CUBE_DEMO_ONLY, controller exit 0, physical batches 1–5 complete, both arms HOME, wall 1284.391 s. Detailed physical geometry and 70,434-snapshot integrity analysis uploaded; raw heavy remains ignored. BUG-009 contact protocol not passed.
- results/20261003_TASK01_fr3_static_payload/: FAIL_EXPERIMENTAL_PAUSE_THEN_SAFE_ABORT, 7-s SIGSTOP of controller group also pauses state monitor; resume triggers stale-state failure and releases both cups. Raw script/negative logs preserved; no normal-flow regression claimed.
- Fresh results/20261003_TASK01_fr3_static_payload_v2/ is controlled opt-in task-thread hold instead of process suspension; phase recorded with physical snapshots. Build PASS 47.9 s; physical force statistics pending at this checkpoint.

## 2026-10-03 — TASK01 corrected runtime checkpoint
- Run: results/20261003_TASK01_preclose_unit/metadata.json — PASS_UNIT_AND_BUILD_ONLY. Residual regression and corrected colcon build PASS; initial target include-path failure retained.
- Run: results/20261003_TASK01_full_five_corrected_01/metadata.json — RUNNING_CHECKPOINT. Fresh headless normal feed, max_batches=5, right center pusher, time_scale=3, no pre-placed fixture. Cube01 complete; Cube02 pre-close correction passes original gate. Final completion/force/pose audit pending.
- Link8 authored incoming fixed-joint anchor/axes audit succeeds; empty-branch static force/torque consistency is preliminary only, not dynamic contact/internal-force calibration.

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

## 2026-10-03 TASK01 collision force/torque calibration
Task: TASK01
Baseline: none; [EXPERIMENTAL] independent known-load fixture, [ENGINEERING] measurement sampler
Platform: Isaac Sim 4.5 PhysX CPU/numpy
Commit: 32ccb2b902ab23cd5f60c191d579ff7e2ccc7fe6 plus per-run uncommitted probe variants saved in this iteration; benchmark SHA unchanged
Seed: no random sampling
Command/config: results/20261003_TASK01_contact_force_{60hz,60hz_v2,60hz_v3,60hz_torque,120hz_yaw30}/metadata.json; probe paths/arguments/variant recorded separately
Results: First startup FAIL (nonexistent PhysicsContext getter); second startup FAIL (unsupported SingleRigidPrim keyword). Corrected 60 Hz v3 PASS has no nonzero torque stage and is not torque evidence. Final 60 Hz torque and 120 Hz/yaw30 runs each PASS all 13 checks. Saved check results are authoritative; early exceptions can still exit 0 with fast shutdown.
Key metrics: support 7.84800024/7.84799969 N; friction Fx -1.99999991/-2.00000003 N; resisting Tz -0.03996668/-0.03998334 Nm; wall yaw0/yaw30 (Fx,Fy)=(-4,0)/(-3.464101,-2) N. Each main window 60/120 samples. Dual suction CLOSED supports payload at 0.500 m while collision signal is zero, proving this interface excludes suction D6 forces.
Artifacts: per-run metadata/selected summary, ignored raw contact_samples.jsonl and Kit logs; reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md.
Boundary: Fixed calibration gates (0.05 N, 0.001 Nm) belong only to independent fixture. No benchmark material/physics/threshold change or paper/internal-force control.

## 2026-10-03 TASK01 incoming mount reaction / reference identification
Task: TASK01
Baseline: none; [EXPERIMENTAL] static articulated mount and suction payload
Platform: Isaac Sim 4.5 PhysX, Surface Gripper
Commit: 32ccb2b plus explicitly different uncommitted probe variants; seed not applicable
Command/config: per-run metadata in mount_reaction_identity, mount_reaction_roll90, mount_reference_identity, mount_joint_reference, mount_joint_reference_unscaled and mount_joint_reference_final under results/20261003_TASK01_*/
Results: Identity/roll90 trials establish known-load availability/direction, not reference-point identity because frames/points coincide. Early scaled-body COM trials have saved software PASS, but their unscaled COM/anchor interpretation is INVALIDATED; metadata reviewed status PARTIAL_REFERENCE_MODEL_INVALIDATED, raw kept. Final two unscaled trials PASS unique joint_axes_about_joint_anchor among nine hypotheses, verify physics COM=5 mm, principal roll45, joint anchor3 mm/joint roll30, payload hold and CLOSED/timestamps. Final field-name regression repeats exact numeric result.
Key metrics: known payload 0.8 kg, world Fz=7.848 N and Ty=-1.255680 Nm; final raw delta (Fx,Fy,Fz) about (0,6.796570575,-3.923998765) N, (Tx,Ty,Tz) about (0,0.616067643,1.067061339) Nm. Correct joint-axis/anchor error 3.435906e-6 N/4.429936e-7 Nm; wrong link origin 0.023544 Nm, wrong COM 0.015696 Nm, wrong link axes 4.0624 N.
Artifacts: metadata/selected summary, raw mount_samples.jsonl and Kit logs; force report.
Boundary: Not real FR3 compensation or universal rotating-joint convention validation. Hidden tool branch mass was not removed; false early origin inference explicitly corrected rather than silently erased.

## 2026-10-03 TASK01 full normal-feed five-Cube readout/preflight/execution
Task: TASK01
Baseline: none; [EXPERIMENTAL] unchanged legacy Task27 normal five-Cube flow, no pre-placed fixture
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit: 32ccb2b plus measurement runner variants; legacy unchanged at 631b1f65656d025c1bb2173e874192f3fe4d355a
Seed: legacy OMPL uncontrolled; no fixed-seed/repeatability claim
Command/config: results/20261003_TASK01_full_fixture_readout/, full_fixture_readout_v2/, full_five_physical/, full_five_preflight/, full_five_physical_v2/ and full_fixture_frame_audit/ metadata.json; full report contains all scene/bridge/MoveIt/controller commands
Results: Initial readout FAIL nonexistent STATE_READY; corrected v2 PASS_READOUT_STARTUP. Full-run startup FAIL bridge-overwritten namespace/BOX_INTERIOR_X; corrected run ready. Five planning-only batches PASS. Actual run FAIL: completed1/5, Cube02 stopped at PRE_CLOSE before suction, no later physical object commanded. Last added authored-frame startup audit FAIL on remote asset-root lookup (no robot commands), so that audit unverified.
Key metrics: 37,236 physics/contact/raw joint snapshots, zero callback errors; feed state [2,2,0,0,0] is ARRIVED, not placement. Cube02 gap delta 0.968 -> 0.315 -> 0.339 mm vs original 0.300 mm gate, minimum correction0.650 mm; independent physical final delta0.338941 mm. Cube01 center error1.792 mm, physical yaw -1.095465 deg; nearest oriented deep/+Y gaps0.06355/0.19531 mm, not whole-face flush. Peak Cube01-deepwall collision resultant139.098 N, not suction/internal wrench or a frozen force gate. MoveIt teardown -11 recurs.
Artifacts: selected metadata/summaries, full report; local ignored raw controller/MoveIt/Kit logs, topology and approximately1 GB physics_contact_samples.jsonl.
Boundary: Measurement completion and planning PASS are not physical full-flow PASS. Control event wall time is not yet aligned to recorded simulation time. New quaternion/force sampler is read-only; original controller still consumes old pose channel. TASK01 IN_PROGRESS, 36 fields unresolved, TASK02 TODO.

## 2026-10-03 TASK01 final offline/static validation
Task: TASK01
Baseline: none; [ENGINEERING] sampler algebra/guard tests and artifact checks
Platform: Python3/numpy offline
Commit: 32ccb2b plus final measurement changes
Seed: not applicable
Commands: python3 platforms/isaac_ros2/probes/test_physics_contact_sampler.py; python3 -m py_compile (five new Python files); python3 scripts/validate_benchmark_candidate.py; git diff --check; sha256sum configs/benchmark/benchmark_v1.yaml
Results: 8/8 unit tests PASS; Python compile and static checks PASS, analytic draft reports36 unresolved nulls. Draft hash a49d60a4dc6a8a00c3bf55a512113af50760968827a8cefe64dae1c7de55fde8 unchanged.
Artifacts: results/20261003_TASK01_contact_sampler_unit/{metadata,summary}.json; reports/TASK01_FREEZE_REVIEW_CHECKLIST.md lists all36 fields and explicitly pending approvals.
Boundary: These tests do not establish a frozen benchmark or five-Cube physical success.

## 2026-10-03 TASK01 full recorded-stream integrity
Task: TASK01; baseline none, [ENGINEERING] read-only artifact audit
Platform: Python3 JSONL, offline; seed not applicable; commit32ccb2b plus recorded measurement variants
Command/config: Self-contained Python stdin scan in results/20261003_TASK01_full_record_integrity/metadata.json, reading full_five_physical_v2/raw/physics_contact_samples.jsonl
Result: PASS_RECORD_INTEGRITY across37,236 rows. Missing steps, nonmonotonic steps/stamps, contact/pose stamp-step mismatches and nonfinite contact/articulation arrays all0. Maximum force-matrix vs normal reconstruction error1.525879e-5 N; dt0.0166666675359 s; Cube quaternion norm-squared error4.44e-16.
Artifacts: metadata.json/summary.json and original ignored JSONL. Does not turn the incomplete physical task into PASS or establish ROS-event clock alignment/FR3 wrench compensation.

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
