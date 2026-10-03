# BUGS

Append-only unresolved/resolved bug register.

At repository initialization, no bugs were recorded.

## BUG-001 — Contact-wrench telemetry gap
Date: 2026-09-30
Task: TASK00
Status: OPEN
Symptom: The observed legacy Task27 ROS graph has joint effort but no contact-wrench message for either suction/contact interface.
Reproduction: With the legacy bridge active, run ros2 topic list -t and inspect /task27/{left,right}/measured_joint_forces.
Suspected cause: Current legacy bridge publishes articulation joint forces, not a contact sensor wrench.
Evidence: reports/TASK00_ENVIRONMENT.md and legacy task26_truck_box_bridge.py.
Workaround: None. Do not treat joint effort as end-effector contact wrench.
Resolution: Define a sensor/estimator and calibrated frame contract in TASK01/TASK02 before P2/P3 force benchmarks.
Related commit/run: TASK00 environment audit.

## BUG-002 — Benchmark time-base ambiguity
Date: 2026-09-30
Task: TASK00
Status: OPEN
Symptom: One live snapshot had /clock at approximately 1787 s while TCP/Cube pose headers were near 1790752970 s.
Reproduction: During a fresh legacy launch, sample /clock and both stamped pose topics together, and query use_sim_time on all consumers.
Suspected cause: Mixed simulation-time and wall-time stamping; not yet proven.
Evidence: reports/TASK00_ENVIRONMENT.md.
Workaround: None accepted for scientific metrics.
Resolution: Freeze and validate one timestamp policy before synchronized benchmark logging.
Related commit/run: TASK00 environment audit.

## BUG-003 — Carriage reference-frame contract absent
Date: 2026-09-30
Task: TASK00
Status: OPEN
Symptom: Legacy USD TruckBox prim and rail-state messages exist, but no explicit carriage/entrance TF was observed.
Reproduction: Inspect the legacy Task27 scene/bridge and its ROS graph.
Suspected cause: The existing controller uses known scene geometry rather than a public frame contract.
Evidence: reports/TASK00_ENVIRONMENT.md.
Workaround: None for a transferable common benchmark.
Resolution: Define carriage and entrance frames in TASK01 and expose them through the TASK02 adapter.
Related commit/run: TASK00 environment audit.

## BUG-004 — MoveIt shutdown segmentation fault after completed Task01 probes
Date: 2026-09-30
Task: TASK01
Status: OPEN
Symptom: After both Cube 05 physical runs had exited normally and the MoveIt launch was interrupted with Ctrl-C, `move_group` exited with code -11 during `rclcpp::CallbackGroup` destruction.
Reproduction: Launch `moveit_dual_side_suction.launch.py use_rviz:=false`, run the Task01 probe, then send Ctrl-C to launch. Reproduced after every one of the four additional completed runs on 2026-10-02; `move_group` exit code -11 and stack ends in `rclcpp::CallbackGroup::~CallbackGroup()`.
Suspected cause: Shutdown lifetime/race in the installed MoveIt/ROS stack; unconfirmed.
Evidence: Launch output from 2026-09-30 and 2026-10-02; all six Task27 node logs contain `batch 5 PASS` before shutdown. The controller process exited 0 in each new trial.
Workaround: None required for completed trajectory execution, but do not classify launch teardown as clean.
Resolution: Isolate the MoveIt/ROS shutdown lifetime issue under a standalone shutdown check before declaring the runtime harness reliable; do not change the manipulation planner to mask this teardown defect.
Related commit/run: TASK01 center right/left physical probes.

## BUG-005 — Motion-time PhysX and USD Cube pose sources are not synchronized
Date: 2026-10-02
Task: TASK01
Status: OPEN
Symptom: During Cube 05 pushing, a read-only same-loop comparison of the Isaac `RigidPrim.get_world_pose()` result and the USD transform used by the legacy Bridge's `/task27/cube_poses` sometimes differed by 0.4–2.8 mm in position. After Cube settle, the positional difference printed as 0.000 mm. Orientation-source difference in observed samples was around 0.02–0.15 deg.
Reproduction: Run `platforms/isaac_ros2/probes/task01_center_headless.py` with the bundled Humble ROS environment, execute the Cube 05 probe, and inspect `[TASK01 pose-source-check]` lines during motion and after settle.
Suspected cause: A physics/USD update or read timing mismatch is possible but not established. This instrumentation alone cannot distinguish timing from transform or caching issues.
Evidence: Headless stdout from left/right repeat runs on 2026-10-02; e.g. left 3 had a 2.840 mm transient sample during push, then 0.000 mm after settle. Final Bridge pose samples and Task27 ROS logs are recorded in `reports/TASK01_CENTER_ARM_SYMMETRY.md`.
Workaround: Use only settled final Bridge pose for current exploratory static placement metrics; do not treat instantaneous Bridge pose as a synchronized contact/velocity measurement.
Resolution: Define one timestamped physics pose pipeline, compare against USD and ROS with a common simulation time, then freeze the TASK01/TASK02 measurement contract.
Related commit/run: TASK01 center repeatability probes.

## 2026-10-03 — BUG-002 follow-up: new channel workaround only
Status: WORKAROUND for TASK01 probe; legacy interface remains OPEN
Evidence: Legacy `_publish()` stamps poses with `node.get_clock().now()` in wall-time while the scene publishes simulation `/clock`. New `PhysicsObjectSampler` reads Isaac core simulation time in a completed physics step. External ROS calibration verifies that new poses, snapshots and `/clock` share the simulation time domain.
Boundary: `/task01/physics/cube_poses` is separate from `/task27/cube_poses`. TCP, effort and legacy consumers have not been migrated; this is not a global resolution or a frozen synchronization contract.
Related report: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md

## 2026-10-03 — BUG-004 follow-up: not reproduced on today's interrupt paths
Status: OPEN
Observation: One idle MoveIt startup interrupted before robot execution and one launch interrupted after a successful 215-s Cube 05 task both exited move_group with SIGINT code -2, not -11. The joint-state bridge also showed KeyboardInterrupt. This differs from the prior repeatable callback-group teardown stack, but no shutdown fix was implemented and these interrupt paths are not proof of resolution.
Related run: results/20261003_TASK01_fixture_physics_channel/

## 2026-10-03 — BUG-005 follow-up: frame-update lag reproduced
Status: WORKAROUND for new PhysX channel; legacy USD motion measurement remains OPEN
Confirmed cause: At 0.2 m/s and 60 Hz physics, legacy/post-step callbacks see stale USD position up to 6.667 mm with 30 Hz application frames or 10.000 mm with 20 Hz frames. After application update, positional difference is zero. The independent known-motion ROS probe directly sampling PhysX passed at both frame rates.
Workaround: New read-only live-physics snapshot, one simulation stamp/step per sample, rejecting USD fallback. Do not compute dynamic contact/velocity metrics from legacy USD callback data.
Related report/runs: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md; results/20261003_TASK01_physics_ros_zero_damping_{30hz,20hz}/

## BUG-006 — Scaled USD matrix corrupts legacy Cube orientation
Date: 2026-10-03
Task: TASK01
Status: WORKAROUND for new physics measurement; legacy Bridge remains OPEN
Symptom: Legacy `_pose()` extracts a quaternion directly from the Cube world transform containing scale=(0.12,0.12,0.12), then normalizes it. This underestimates the actual angle; normalization does not remove scale from the rotation matrix.
Reproduction: Run task01_pose_timing_probe.py; inspect raw_usd_rotation_error_deg versus scale_removed_usd_rotation_error_deg after app.update().
Confirmed cause: ExtractRotationQuat requires a rotation matrix; applying it before removing scaling violates the OpenUSD API contract. In the corrected zero-damping calibration, raw extraction error reaches 27.464 deg while scale-removed extraction differs from PhysX by at most 0.000154 deg after app update.
Workaround: Use live PhysX quaternion in the new measurement channel. Do not reinterpret old Bridge yaw as physical 6D Ground Truth. Correct only the historical report's validity statement; retain original numbers.
Resolution needed: Migrate the final common adapter's pose consumers with an explicit tested frame/time contract. This iteration does not modify legacy control code.
Related report: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md

Template:
```text
## BUG-XXX
Date:
Task:
Status: OPEN/WORKAROUND/RESOLVED
Symptom:
Reproduction:
Suspected cause:
Evidence:
Workaround:
Resolution:
Related commit/run:
```
