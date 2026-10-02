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
