# POST-TASK01 Reuse Map — do not rebuild validated engineering infrastructure

Status: **ACTIVE RULE FOR TASK02+**

Review date: 2026-10-09

Source engineering repository:
- repository: `dreamerToTOE/dual-arm-embodied-palletizing`
- branch: `side-suction-palletizing`
- pinned commit reviewed here: `631b1f65656d025c1bb2173e874192f3fe4d355a`

Target scientific repository:
- `dreamerToTOE/dual-arm-coordinated-manipulation-reproduction`

This document intentionally excludes work already absorbed into TASK01. Its purpose is to prevent TASK02 and later paper-reproduction tasks from rebuilding generic engineering infrastructure that already exists and has useful evidence.

## Core policy

The old repository is an **engineering asset library**, not a source of paper-reproduction claims.

Use this split:

```text
old repository
  → engineering infrastructure
  → data contracts
  → MoveIt/FCL wrappers
  → synchronized execution
  → metrics/logging patterns
  → sandbox/isolation patterns
  → regression oracles

new repository
  → paper-exact mathematics
  → paper controllers/planners
  → benchmark-neutral common APIs
  → formal cross-method measurements
```

A reused engineering component does **not** make the corresponding paper baseline reproduced.

## Mandatory classification before reuse

Every candidate asset must be classified as exactly one of:

- **DIRECT_PORT** — generic implementation can be migrated with only namespace/build cleanup.
- **THIN_ADAPTER** — useful implementation exists but contains old topics, geometry, tool assumptions or ROS-specific coupling that must be parameterized.
- **TEST_ORACLE** — keep old implementation/result as a regression reference; do not place it in the new baseline path.
- **REFERENCE_ONLY** — useful design history, but importing it would contaminate the scientific baseline or add irrelevant application complexity.

For TASK02+, Codex must complete a PRIOR-ASSET CHECK before writing a replacement implementation.

---

# 1. TASK02 — common interfaces, geometry, logger and metrics

## 1.1 Trajectory/event contract
Source:
- `ros_ws/src/fr3_dual_palletize/include/fr3_dual_palletize/task_event.hpp`
- `ros_ws/src/fr3_dual_palletize/include/fr3_dual_palletize/task_trajectory_candidate.hpp`

Classification: **THIN_ADAPTER**

Already implemented:
- unified relative trajectory time;
- stage markers;
- event stream;
- `SUCTION_ON / ATTACH / SUCTION_OFF / DETACH`;
- start/goal q;
- object/grasp metadata;
- task duration.

Reuse target:
- common trajectory/event schema;
- benchmark phase markers;
- event-aware logging.

Do not blindly preserve old palletizing names or top-suction assumptions.

## 1.2 Object/task data model
Source:
- `palletizing_job.hpp`
- `palletizing_job_loader.cpp`
- `runtime_box_state.cpp`

Classification: **THIN_ADAPTER**

Already implemented:
- `BoxSpec`;
- `GraspCandidate`;
- `PlacementSpec`;
- dimension/mass validation;
- quaternion normalization;
- pose composition;
- conversion to MoveIt CollisionObject;
- safe YAML validation.

Preferred reuse:
extract generic math/data validation into `common/geometry` / `common/interfaces`.

Avoid forcing the new common layer to depend on ROS messages if a platform-independent representation is cleaner.

## 1.3 Experiment output and deterministic seeds
Source:
- `task16_planning_benchmark.cpp`

Classification: **THIN_ADAPTER**

Already implemented:
- explicit OMPL random seed;
- repeated trials;
- candidate-level metrics;
- CSV output;
- JSON summary;
- selected-candidate annotation;
- planning-time/path-length/joint-margin fields.

Reuse this pattern when implementing TASK02 run metadata and TASK27 unified benchmark. Do not create a second incompatible experiment format unless scientifically required.

## 1.4 Continuous geometry metrics
Source:
- `task14_shared_box_geometry_monitor.cpp`
- `docs/tasks/TASK14_CONTINUOUS_GEOMETRY.md`

Classification: **THIN_ADAPTER / TEST_ORACLE**

Already implemented:
- relative TCP error;
- object-to-dual-TCP midpoint error;
- object orientation error;
- max and RMS;
- synchronized-sample acceptance;
- explicit rejection of timestamp-skewed samples.

These are strong starting metrics for Benchmark A and later P2 comparisons. Thresholds are historical evidence only and must not silently become new benchmark thresholds.

---

# 2. TASK03–06 / P4 — closed-chain planning

## 2.1 Shared-object planning shell
Source:
- `shared_object_planner.hpp/.cpp`

Classification: **THIN_ADAPTER + TEST_ORACLE**

Reusable infrastructure:
- dual-arm MoveIt setup;
- common-stage representation;
- trajectory interpolation;
- synchronized dual-arm resampling;
- normalized TCP path progress;
- private PlanningScene/FCL verification;
- joint-limit and geometry gates;
- object/TCP tracking diagnostics.

Important existing idea:
the old planner does **not** simply align two trajectories by waypoint index. It computes each TCP's path progress and resamples both onto a common time base. Preserve this engineering idea rather than rebuilding a weaker synchronization layer.

Do **not** claim this is P4. P4 still requires new paper-specific:
- closure residual `C(q)`;
- constraint Jacobian `Jc(q)`;
- Newton-Raphson/manifold projection;
- constrained local connection;
- constrained RRTConnect semantics.

Old hard-coded tool/grasp transforms must be replaced by benchmark-supplied object-to-grasp transforms.

## 2.2 Spatiotemporal FCL sampling
Source:
- `spatiotemporal_conflict_detector.hpp/.cpp`

Classification: **THIN_ADAPTER**

Reusable:
- one 14-DoF RobotState;
- interpolation on a common task clock;
- per-sample private PlanningScene;
- world/attached object state transitions;
- contact pair classification;
- first-conflict time;
- conflict windows;
- integer-index sampling to avoid accumulated floating error.

Must be generalized:
- remove historical fixed top-suction relative transform;
- accept explicit benchmark grasp transforms;
- expose data through the new common collision interface.

## 2.3 Robust MoveIt candidate generation
Source:
- `robust_planner.hpp/.cpp`
- `docs/tasks/TASK16_PLANNING_ROBUSTNESS.md`

Classification: **DIRECT_PORT / THIN_ADAPTER**

Already implemented:
- repeated RRTConnect candidates;
- path-length score;
- normalized joint-limit margin;
- redundancy modes:
  - FREE_7DOF
  - HARD_LOCK_JOINT
  - SOFT_PREFERENCE
- selected-candidate diagnostics.

Reuse as a platform/MoveIt utility. It must not replace P4's paper algorithm.

---

# 3. TASK07–10 / P2 — pose and internal-wrench control

## 3.1 Shared-object execution shell
Source:
- `shared_object_executor.hpp/.cpp`
- `coordinated_task_executor.hpp/.cpp`

Classification: **THIN_ADAPTER**

Already implemented:
- synchronized dual-arm command publication;
- one shared execution clock;
- interpolation of prevalidated trajectories;
- global HOLD at discrete grasp/release events;
- suction state confirmation;
- TCP pose feedback;
- failure-safe suction release;
- physical timing separate from candidate time.

This should become the Isaac execution adapter rather than writing another dual-arm executor for P2/P5.

P2 paper-specific work remains new:
- grasp matrix;
- external/internal wrench decomposition;
- object pose controller;
- internal-force controller;
- force/wrench calibration and compensation.

## 3.2 P2 geometry validation oracle
Source:
- Task14 continuous geometry monitor.

Classification: **TEST_ORACLE / THIN_ADAPTER**

Use the old metrics as a before/after control-quality comparison, while new force-related metrics come from TASK10-IS.

---

# 4. TASK11–15 / P3 — constrained rear insertion

## 4.1 Position-only rear-push baseline
Source:
- `task26_truck_box_push_in.cpp`
- Task26/Task27 reports.

Classification: **THIN_ADAPTER + TEST_ORACLE**

Beyond the TASK01 handoff already reused, Task26 contains a ready engineering baseline for TASK11:
- right rear (-X face) grasp;
- segmented +X insertion;
- complete-chain precheck;
- Cube progress/lag supervision;
- deep-wall gap check;
- safe exit.

TASK11 should adapt this into the frozen INSERT_READY→TARGET contract instead of creating a second position-only push implementation.

P3 paper-specific TASK12–14 work remains new:
- hybrid force/position control;
- jam detector;
- bounded search/align recovery.

For fair ablation, TASK11 and TASK12 should share the same state/input/output/attachment/execution shell; only the control law should change.

---

# 5. TASK16–19 / P5 — centralized QP

## 5.1 Reusable platform shell
Sources:
- MoveIt RobotModel parameter-copy patterns;
- PlanningScene snapshots;
- `spatiotemporal_conflict_detector`;
- shared-clock executor;
- robust planner diagnostics.

Classification: **THIN_ADAPTER**

Reuse:
- RobotModel/state acquisition;
- scene management;
- FCL object naming;
- synchronized Isaac command path;
- collision regression scenarios.

Do not claim the old repository already implements P5.

New P5 work required:
- centralized stacked dual-arm QP;
- task Jacobians/object tracking objective;
- joint velocity/position dampers;
- QP solve status/infeasibility;
- collision-distance inequality.

## 5.2 Collision constraint warning
The old FCL detector is primarily a collision/contact-time detector. TASK18 requires a richer interface such as:
- signed/minimum distance;
- nearest points;
- normal;
- link/body IDs;
- distance gradient or distance Jacobian.

Therefore the old detector is a scene/sampling scaffold, not a substitute for TASK18.

---

# 6. TASK20–26 / P1 — sampling MPC

## 6.1 Isolated MoveIt sandbox
Sources:
- `launch/task22_predictive_sandbox.launch.py`
- `task22_predictive_sandbox_probe.cpp`
- `task22_predictive_sandbox_candidate_demo.cpp`

Classification: **DIRECT_PORT / THIN_ADAPTER**

Already validated design:
- isolated namespaced move_group;
- `allow_trajectory_execution=false`;
- global `/joint_states`, `/tf`, `/tf_static` input;
- private PlanningScene/action/services;
- explicit proof that sandbox CollisionObjects do not appear in execution `/move_group`;
- execution-scene snapshot copied into sandbox;
- planning without joint/suction output.

This should be the default starting point for P1 planning/rollout integration that needs MoveIt access without contaminating the execution scene.

Do not invent a second temporary move_group isolation mechanism.

## 6.2 Predictive result validity
Sources:
- `predictive_plan_cache.hpp/.cpp`

Classification: **THIN_ADAPTER**

Reusable concepts:
- source scene version;
- expected object pose;
- expected next-object source pose;
- expected left/right terminal q;
- explicit invalidation reason;
- cache hit does not equal execution authorization;
- final collision/FCL recheck required.

This is useful for safe caching of expensive predictive planning/MPC outputs, but it is not part of the P1 paper algorithm unless the paper requires it. Keep it in engineering/platform infrastructure.

---

# 7. TASK27–30 — unified experiments and freeze

Classification: **THIN_ADAPTER / TEST_ORACLE**

Reuse from old project:
- Task16 seed/trial/CSV/JSON structure;
- Task14 max/RMS geometry metrics and synchronized sampling discipline;
- Task08 conflict windows;
- Task09/coordination timing measurements where semantically applicable;
- explicit failure reason recording;
- candidate-selection diagnostics.

The new repository must still provide its own unified schema required by `docs/ARCHITECTURE.md`; reuse implementation ideas instead of preserving historical file formats blindly.

---

# 8. Assets deliberately NOT promoted into the reproduction baselines

Classification: **REFERENCE_ONLY**, unless a later explicit decision changes this.

Do not automatically migrate:
- `PlacementPlanner`;
- `CoordinationRouter`;
- `TemporalCoordinator`;
- `LocalWaitCoordinator`;
- five-Cube scheduling;
- batched feed;
- continuous palletizing scheduler;
- Ground-Truth dispatch selector;
- predictive scheduling policy;
- multi-size pallet placement logic.

Reason:
these are valuable application/system components, but importing them into P1–P5 could make scientific attribution unclear. They may become useful after baseline freeze in `ours/` or in a separate application/stress-test layer.

---

# 9. Components that must still be implemented from the papers

The reuse policy must never be used to avoid the scientific work.

Still new/paper-derived:
- **P4:** closed-chain residual/Jacobian, NR projection, constrained local connection, constrained RRTConnect.
- **P2:** grasp matrix, wrench decomposition, object pose/internal-force controller.
- **P3:** hybrid force-position controller, jam detection, paper-inspired recovery/search.
- **P5:** centralized QP objective/constraints and online collision inequalities.
- **P1:** upstream sampling MPC, equality/null-space handling, two-stage exploration/refinement.

These belong under `baselines/` and must carry the repository's paper-fidelity labels.

---

# 10. Required PRIOR-ASSET CHECK for every TASK02+ implementation

Before writing code, Codex must report:

```text
=== PRIOR-ASSET CHECK ===
Current task:
Scientific algorithm that must remain new/paper-derived:

Old repository areas searched:
Pinned source commit:

DIRECT_PORT:
- ...

THIN_ADAPTER:
- ...

TEST_ORACLE:
- ...

REFERENCE_ONLY:
- ...

Rejected old assets and reason:
- ...

Files that will be reused/adapted:
Files that will still be newly implemented:
Risk of contaminating paper fidelity:
Need user decision: yes/no
```

Rules:
1. Search before implementing, not after.
2. Prefer a thin adapter over a parallel reimplementation.
3. Preserve provenance in comments/docs when porting non-trivial code.
4. Do not import historical numeric thresholds as benchmark truth.
5. Do not import a whole legacy subsystem merely because one utility is useful.
6. If an old asset materially changes the paper method, classify it [DEVIATION] and ask the user.
7. If no reusable asset exists, state that explicitly and proceed.
8. TASK01-specific reuse remains governed by `docs/PRIOR_PROJECT_REUSE.md`; this document governs TASK02+.

## One-line rule

> **Reuse old engineering wheels; reproduce new scientific algorithms.**
