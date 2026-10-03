# BUGS

## 2026-10-03 — BUG-008 bounded-correction checkpoint
Status: FIX_IMPLEMENTED / FULL_FLOW_VALIDATION_PENDING
Evidence: d80b6b6 in legacy task01-runtime-fixes replaces 0.650 mm minimum correction with measured residual and precise seeded FK solving. Unit/build PASS. Fresh Cube01 0.447 -> 0.001 mm; Cube02 0.287 mm passes original 0.300 mm gate. Do not claim full five-Cube fix until physical completion.

## BUG-009 — Legacy first-four push contact protocol differs from D004
Date: 2026-10-03
Task: TASK01
Status: OPEN
Symptom: Legacy deep push holds helper at a parked pose, rather than side-face suction constraint. Inner cubes later get rear-arm-only lateral trim, not the approved side-primary/rear-hold role swap.
Evidence: task26_truck_box_push_in.cpp executePushWithSupervision call and isInnerReferenceTask block under TASK27_FIVE_CUBE.
Impact: Legacy full five-Cube demo PASS cannot establish requested cooperative fixture behavior or be relabeled as paper dual-arm insertion evidence.
Resolution needed: Verify contact accessibility and implement/test the distinct fixture protocol without geometry/gate relaxation; stop for user direction if physical constraints require benchmark change.

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

## 2026-10-03 — BUG-001 follow-up: collision channel calibrated, suction gap remains
Status: PARTIAL WORKAROUND; FR3 TCP contact-wrench contract still OPEN
Evidence: Independent known-load normal/friction/torque calibration passes at 60/120 Hz. A dual-suction-held 0.8 kg object produces 0 N collision telemetry: D6 reaction is excluded. Independent articulated-mount reaction captures the known suction load and identifies the raw link-axis/link-origin convention, but is not a FR3 compensation calibration.
Next: Validate the actual link8 branch gravity/inertia compensation, action/reaction sign and moment shift to TCP before publishing a contact estimator. Do not treat old JointState.effort, new collision wrench, or uncorrected incoming joint wrench as interchangeable.
Related report: reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md

## BUG-007 — Hidden tool-body mass / contact-force compensation ambiguity
Date: 2026-10-03
Task: TASK01
Status: OPEN (model audit finding; no model change authorized)
Symptom: Disabling old hand/finger visual and collision does not remove their rigid-body masses. Actual articulation topology has 13 links, with about 1.946277 kg in the link8+hand+fingers+hand_tcp branch; static support is about 19.093 N before grasping any Cube.
Evidence: Full-scene readout topology.json; independent mount calibration proves that incoming reactions include downstream gravitational load. Actual link8 raw reactions also show roughly this support after world-frame rotation.
Risk: Calling raw incoming force a suction contact wrench gives biased force/internal-stress metrics. Invisible bodies also influence the physical dynamics and must be included in the benchmark model description.
Resolution needed: Audit/record model masses and inertias; calibrate compensation. Any removal/replacement of masses changes the benchmark physics and requires explicit user review; not done here.
Related report: reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md

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

## 2026-10-03 — BUG-001/007 reference-convention correction
Status: OPEN / independently calibrated channel only
Correction: Earlier follow-up's link-axis/link-origin identification is INVALIDATED due to scaled authored COM/anchors. Final unscaled nine-hypothesis test identifies incoming joint axes/about joint anchor (3.436e-6 N / 4.430e-7 Nm errors), with physics COM checked. Raw prior PASS retained; metadata explicitly invalidated for reference inference. Do not transform FR3 raw incoming by link pose alone or ignore the moment reference.
BUG-007 qualification: 1.946277 kg and 19.092980 N are topology/analytic facts. The temporary about-19.10 N link-pose rotation is only an uncalibrated magnitude observation, not FR3 joint mapping proof. Added authored-frame audit failed on asset-root lookup; mapping/compensation stay unverified.
Evidence: results/20261003_TASK01_mount_joint_reference_final/ and reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md.

## BUG-008 — Pre-close minimum correction overshoots symmetry gate
Date: 2026-10-03
Task: TASK01
Status: OPEN
Symptom: Normal-feed run places Cube 01 then fails Cube 02 before suction. Gap difference 0.968 -> 0.315 -> 0.339 mm never meets original 0.300 mm gate; controller exits 1, no later cube commanded.
Evidence-supported cause: Legacy effective_step clamps nonzero correction to at least 0.650 mm. Near the gate it overshoots the acceptable interval. Last x/z mismatches are within original 2.5 mm gate and not the failure. Final independent physics TCP/body pose confirms 0.338941 mm difference.
Evidence: results/20261003_TASK01_full_five_physical_v2/raw/controller.log; reports/TASK01_FULL_FIXTURE_CONTACT_PROBE.md.
Resolution needed: Fix quantization/deadband with endpoint FK/tracking feedback, retain the 0.300 mm geometry gate and three-attempt stop. Rerun five normal-feed cubes; no ACM/physics change. Not fixed in this metrology scope.

## 2026-10-03 — BUG-004/006 full-flow reproduction
BUG-004: move_group again exits -11 at rclcpp::CallbackGroup destruction after stopping the incomplete run. Execution and shutdown failures are separate; no clean-lifecycle claim.
BUG-006: Cube 01 final physical yaw -1.095465 deg versus legacy scaled-USD near-zero yaw. Oriented nearest-wall gap differs from center/axis-aligned gap; no physical orientation PASS from old telemetry.
Evidence: results/20261003_TASK01_full_five_physical_v2/raw/{controller,moveit}.log and physics_contact_samples.jsonl; report above.
