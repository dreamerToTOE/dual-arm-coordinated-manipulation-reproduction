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
