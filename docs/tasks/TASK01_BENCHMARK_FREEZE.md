# TASK01 — Predecessor Single-Cube Scene Foundation Qualification

Status: **FOUNDATION PASS CANDIDATE ACCEPTED BY USER — PREDECESSOR_TASK26_BATCH1_TWO_CUBES_WITH_AUTHORIZED_SOFTWARE_FIXES; SCIENTIFIC BENCHMARK NOT FROZEN**

**2026-10-09 acceptance:** User confirms the foundation feasibility qualification passed,
accepts PASS CANDIDATE, and requires no redevelopment of original grasp/push. Qualification
is closed; next direction is minimal migration and unified interfaces. This does not freeze
benchmark_v1 or elevate old asynchronous feedback/one successful run to research-grade evidence.
TASK02-A uses the accepted source in place, with only read-only interface/provenance code;
see [integration scope and offline tests](../../reports/TASK02_FOUNDATION_INTERFACE01.md).
Earlier pending-review statements below are historical, superseded by this acceptance.

**2026-10-09 latest physical review:** User authorized up to3 fresh existingGUIacceptance attempts after approved5ed0c96 two softwarefixes. Attempt1 preflight0/physical1 (deepfullPASS, shallowactualjointsettletimeout); attempt2 preflight0/physical0, bothoriginalfullCubechains andactualcommonHOME complete. PerCube1.181/.376mm, HOME.059/.062deg. Stop2/3, no3rd, no further source/model/physics/ACM/gate edit. Latestcountoverride is originalbatch1twoCubescandidate, notexactonePrim. Firstnegative/oldFCL/clocklimits retained; no statisticalrepeatability/heldreset/nativecollision/wrenchproof. Await usercandidate/foundationreusepath review; noautomaticFROZEN/port/TASK02. [PASS CANDIDATE REVIEW](../../reports/TASK01_PREDECESSOR_PATCHED_RUNTIME_REVIEW.md). The dated checkpoints and original specification below are historical and governed by these explicit source/count/runtime overrides.

**2026-10-09 authorized software-only follow-up:** After old-asset audit, user approved explicit FK Vector3d return plus reuse of Task27's existing full side-chain rear-candidate gate for Task26. Isolated predecessor commit5ed0c96 changes only these software details, preserving geometry/physics/ACM/constants; this is a recorded exception to the source-preservation clauses below, not a new architecture or silently unmodified pin. Pure software checks/compile do not qualify the foundation. No new scene/reset/MoveIt/planning-only/physical invocation or renewed physical budget; prior negative run retained. Any future candidate must disclose `WITH_AUTHORIZED_SOFTWARE_FIXES`, not claim byte-identical631b1f. [Scope and checks](../../reports/TASK01_PREDECESSOR_SIDE_PREFLIGHT_FIX.md).

**2026-10-09 current outcome:** Original pinned Task26 two-Cube batch1 qualification completed once: planning-only PASS/exit0, physical FAIL/exit1. First Cube reached deep support, then the unchanged FK straight-line gate rejected all side-compaction chains; no actual side-compaction, second Cube or retreat/HOME. No runtime source changes/fix/retry; both SG OPEN, GUI paused. Budgets preflight1/1 and physical1/1 consumed. This does not qualify the foundation or freeze the benchmark; await separately scoped user decision. [Full qualification result](../../reports/TASK01_PREDECESSOR_FOUNDATION_RUNTIME01.md). The audit checkpoint and original restart specification below are historical scope records.

**2026-10-09 latest user override:** “两件cube也可以，请你继续”. Use the pinned predecessor's original batch1 (`task26_r0_deep` then `task26_r0_shallow`, `max_batches=1`) unchanged. No selector/count/loop patch. The exact-one-Cube requirement below is superseded by this count-only approval; all original-runtime preservation, lifecycle, bounded-attempt and first-failure-stop rules remain. Four original Cube rigid-body Prims remain, two active and two dormant; no second batch. Candidate label if qualified: `PREDECESSOR_TASK26_BATCH1_TWO_CUBES`, not `SINGLE_CUBE`. [PREDECESSOR FOUNDATION AUDIT](../../reports/TASK01_PREDECESSOR_FOUNDATION_AUDIT.md) must precede runtime. No new foundation experiment has run at this audit checkpoint.

Restart decision: **2026-10-09, explicit user instruction.**

## 1. Why TASK01 restarted

Previous TASK01 work built a new parallel Isaac/ROS/MoveIt harness and then spent substantial effort validating that new harness. The user has explicitly rejected that direction.

The new rule is:

> Do not rebuild the mature single-Cube engineering stack. Start from the predecessor project itself, reduce it to one Cube, run it, and decide whether that existing scene can become the foundation scene for all later reproduction work.

All earlier TASK01 experiments remain historical evidence, but they are **not active prerequisites** for this restarted task.

## 2. Question TASK01 answers

TASK01 now answers exactly one question:

> Can the already validated predecessor Task26 side-suction truck-box scene, with only one Cube present/active, run its original mature single-Cube workflow reliably enough to serve as the base Isaac scene for this reproduction project?

This task does **not** freeze the final scientific benchmark yet.

## 3. Source of truth

Codex must independently read the predecessor repository before implementation:

- repository: dreamerToTOE/dual-arm-embodied-palletizing
- branch: side-suction-palletizing
- pinned reference: 631b1f65656d025c1bb2173e874192f3fe4d355a

Mandatory predecessor files to read in full:

- docs/tasks/TASK26_TRUCK_BOX_PUSH_IN.md
- isaac/scripts/task26_truck_box_scene.py
- isaac/scripts/task26_truck_box_bridge.py
- ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp
- relevant Task24/Task27 files only when Task26 explicitly depends on or inherits behavior from them.

Do not rely only on reuse summaries in the new repository. Inspect the actual old source.

## 4. Foundation candidate

For this restarted TASK01, the candidate foundation is the predecessor Task26 runtime itself:

    normal Isaac Sim GUI
    → old task26_truck_box_scene.py
    → manual Play
    → old task26_truck_box_bridge.py
    → old dual-FR3 MoveIt launch
    → old task26_truck_box_push_in

The current reproduction TASK01-specific scene/bridge/handoff harness is inactive for this qualification and must not be used to prove PASS.

Inactive historical routes include:

- platforms/isaac_ros2/handoff/task01_*;
- standalone SimulationApp TASK01 harnesses;
- TASK01-specific planning-world validators;
- TASK01-specific INSERT_READY recorder/driver;
- any new rear-push controller written only for the reproduction repository.

## 5. One-Cube requirement

The qualification run must contain **one Task26 Cube only** in the active Task26 scene.

Chosen logical task:

    task26_r0_deep

Reason:

- it is the first Task26 deep-placement task;
- it does not require a previously placed neighbor Cube;
- it exercises the complete mature path:
  feed → bilateral side grasp → tight transport → release → rail transition → rear regrasp → segmented +X push → wall seating → retreat.

### 5.1 First preference — existing mode

Before editing predecessor source, inspect whether the pinned source already has a supported exact single-object/single-task mode that gives one Task26 Cube.

If yes, use it unchanged.

### 5.2 Allowed fallback — minimal one-Cube selector only

If the old source has no exact one-Cube mode, one minimal qualification-only patch is allowed in an isolated old-repo worktree/branch, not by rewriting the scene in this repository.

Allowed changes are only those required to make the old Task26 code operate on the first task as a one-element set, for example:

- active Cube count;
- batch/task count;
- loop bounds;
- metadata arrays that must match that count;
- a compile-time/runtime single_cube_foundation selector.

The patch must preserve the original implementation of:

- FR3 asset loading;
- official joint-limit override;
- L-shaped side-suction tool;
- table and truck-box geometry;
- physics/material settings;
- Surface Gripper construction;
- ROS bridge;
- rail controller/interlock;
- MoveIt description/ACM;
- grasp planning;
- synchronized FCL checks;
- bilateral transport;
- release;
- helper/pusher transition;
- rear -X regrasp;
- segmented +X push;
- progress/jam supervision;
- wall-seat checks;
- retreat/HOME.

No new controller, no new scene builder, no new bridge, no new validator.

## 6. Required execution order

### Phase A — source audit

Produce a short report that identifies:

- exact files and commit used;
- whether exact one-Cube mode already exists;
- if not, the minimum lines/variables required to obtain one Cube;
- confirmation that no geometry/control/physics behavior will change.

Do not spend a full iteration designing architecture.

### Phase B — start the old scene exactly as designed

Use the predecessor lifecycle:

    1. Start Isaac Sim normally with visible GUI.
    2. Timeline STOP.
    3. Run predecessor Task26 scene script.
    4. Confirm exactly one Task26 Cube exists.
    5. Manual Play.
    6. Run predecessor Task26 bridge script.
    7. Start predecessor MoveIt launch.

Do not:

- use standalone SimulationApp;
- create a new Stage harness;
- insert custom app.update startup loops;
- use the reproduction TASK01 scene/bridge.

### Phase C — original zero-command preflight

If the old Task26 workflow provides its original planning_only path, run it first for the same one-Cube task.

This preflight may use the old IK/FCL/candidate logic only.

### Phase D — one physical one-Cube run

Run exactly one Cube through the predecessor workflow.

Expected functional chain:

    single Cube arrives at old supply slot
    → bilateral side-contact approach
    → both Surface Grippers close
    → common lift/transport
    → PRE_PUSH
    → bilateral release
    → helper/pusher safe transition
    → old rail transition
    → old planning-world shift behavior
    → rear -X regrasp
    → segmented +X insertion
    → original deep-wall / side-wall acceptance
    → release/retreat/HOME

Do not stop at INSERT_READY merely because the previous new TASK01 design used that boundary. The point here is to test the mature predecessor scene as a whole.

## 7. Minimum evidence to qualify the scene

TASK01 may become **PASS CANDIDATE** only if all of these are demonstrated in the predecessor scene:

- [ ] normal GUI scene loads without the new standalone startup failure;
- [ ] exactly one Task26 Cube is present/active;
- [ ] both FR3, L-tools, table, rails and truck-box are predecessor assets/geometry;
- [ ] predecessor bridge starts and its original topics/state feedback are available;
- [ ] predecessor MoveIt model connects;
- [ ] predecessor planning-only preflight passes, if supported;
- [ ] physical bilateral grasp and shared transport complete;
- [ ] bilateral release completes;
- [ ] original rail transition and world-shift behavior complete;
- [ ] original rear -X regrasp completes;
- [ ] original segmented +X push completes;
- [ ] original Task26 support/wall-seat acceptance for that Cube passes;
- [ ] safe retreat/HOME completes;
- [ ] no geometry/control/physics patch was needed beyond the one-Cube selector.

Use the old Task26 success semantics for this qualification. Do not invent new benchmark tolerances yet.

## 8. PASS meaning

If the above succeeds:

    TASK01 = PASS CANDIDATE
    FOUNDATION_SCENE = PREDECESSOR_TASK26_SINGLE_CUBE

Then stop.

Do not immediately port it into the reproduction repository.

The next user decision will be whether to:

1. use the predecessor scene in place through thin adapters; or
2. copy the validated old scene/bridge/runtime into platforms/isaac_ros2/ with minimal namespace/config cleanup.

## 9. Failure meaning

If the old one-Cube scene fails, stop at the first substantive failure and classify it as one of:

- environment/version drift;
- missing dependency/path;
- one-Cube selector bug;
- predecessor scene itself no longer reproducible;
- operator/startup error.

Do not immediately build a new replacement subsystem.

A failure in a new wrapper is not evidence that old Task26 is invalid.

## 10. Explicitly out of scope

Do not work on:

- benchmark_v1 numerical freeze;
- START/PRE_PUSH/INSERT_READY states from the previous TASK01 design;
- new collision-parity probes;
- native D6 anchor introspection;
- MoveIt cleanup segfault;
- force/wrench calibration;
- P2/P3/P4/P5/P1 algorithms;
- five-Cube execution;
- new logging infrastructure beyond enough run evidence to judge foundation suitability;
- rewriting Task26 into a cleaner architecture before it passes unchanged/minimally reduced.

## 11. Attempt policy

Allowed sequence:

1. source audit;
2. one minimal one-Cube reduction if required;
3. one planning-only preflight;
4. one physical one-Cube run.

If a blocker appears, report it before creating a second implementation path.

## 12. Required Codex reports

PRE-TASK must include:

    === PREDECESSOR FOUNDATION AUDIT ===
    Pinned predecessor commit:
    Task26 files read:
    Existing exact single-Cube mode: yes/no
    Chosen one-Cube task:
    Minimum selector change required:
    Old runtime components kept behavior-equivalent:
    New runtime components introduced: NONE expected
    Launch sequence:
    Planning-only command:
    Physical command:
    Stop condition:

POST-TASK must include:

    TASK01:
    FOUNDATION_SCENE:
    Predecessor commit:
    One-Cube selector:
    Scene load:
    Bridge:
    MoveIt:
    Planning-only:
    Physical full-chain:
    Final Cube pose / old Task26 acceptance:
    Retreat/HOME:
    Unexpected failures:
    Changes to predecessor behavior:
    Recommended foundation decision:

## 13. Historical TASK01

The pre-restart TASK01 specification is preserved at:

docs/tasks/archive/TASK01_PRE_RESTART_20261009.md

Its reports and code remain history, but they are not prerequisites for the restarted foundation qualification.
