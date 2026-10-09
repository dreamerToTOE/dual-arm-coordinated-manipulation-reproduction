# TASK05 pre-task / prior-asset / pre-experiment protocol

2026-10-09; software baseline `5d41869156990f095ec7eeb8b5477066a3713066`.
User accepts TASK04 PASS CANDIDATE (OFFLINE PROJECTION MATHEMATICS ONLY).
TASK03 original precision FAIL stays FAIL. TASK02-D DEFERRED; Benchmark DRAFT.

## Pre-task report

- Objective: connect valid closed-chain 14q states using existing C/Jc and NR-SVD.
- Minimum evidence: identical and nearby states connect; projection, bounds,
  closure, continuity and real native FCL failures reject the entire edge with
  ordered verified prefix and rejected-candidate evidence.
- Scope: offline mathematics, library-only PlanningScene/FCL, finite tests/logs.
- Non-goals: Isaac/ROS services/controllers/Task26, TASK06 RRTConnect, new IK/FK,
  alternative projection/collision backend, Benchmark or physical tuning.
- Budget: one bounded software slice, default diagnose/fix/fallback budget per
  root blocker. Missing genuine scene/FCL support => PARTIAL, no substitute engine.
- Preferred method: P4 II-C Recursive Bi-Section; no algorithm fallback.
- Stop: fidelity/model/ACM/threshold changes or budget exhaustion need user review.
- Expected changes: new connector, thin FCL adapter, tests/runner/protocol/report
  and append-only governance records. Previously accepted sources unchanged.
- Validation: TASK02/03/04 regressions, fixed real model/scene tests, protected hashes.
- Risks: finite sampling is not continuous safety or same-branch proof; archived
  fixture is superseded bilateral mathematics, not current scientific execution.
- User confirmation needed: no, current explicit TASK05 authorization covers this.

## Prior-asset check

Pinned predecessor `631b1f65656d025c1bb2173e874192f3fe4d355a`:
shared_object_planner.hpp/.cpp and spatiotemporal_conflict_detector.hpp/.cpp audited.
DIRECT_PORT: reproduction TASK03 C/Jc/MoveIt FK and TASK04 project() unchanged.
THIN_ADAPTER: old private PlanningScene, static boxes, RobotState and native FCL
queries (shared planner validateStage); full self/world query separation already
used by reproduction full_chain_probe.cpp.
TEST_ORACLE: immutable TASK03 URDF/SRDF/archive and TASK04 stored projected q/G*;
historical empty-retreat box-at-TCP negative geometry is reference-only fixture
construction, not invocation of its service-based probe.
REFERENCE_ONLY: old trajectory/event organisation. Rejected: outer plan() writes
remote scenes; conflict classifier filters self/environment; old top-grasp geometry
and tool/Cube ACM permissions are not valid for this side-tool model.
New paper algorithm: RBS from P4 II-C (used by IV), not globally fixed-alpha sampling.
No new collision engine, FK, C/Jc or NR. No mature runtime reimplementation.

## Protocol declared before any TASK05 experiment

Machine-readable: `configs/engineering/task05_local_connection_test_v1.json`.
Original TASK04 separate tolerances `1e-8 m / 1e-8 rad`, max40 full SVD updates,
cutoff max(`1e-12`, `1e-10 sigma_max`), stagnation `1e-14 rad`, no clamp/damping.
RBS projected midpoint; leaf 14q L2 distance <=0.01rad. Adjacent projected path
L2 <=0.01rad and max absolute joint change <=0.01rad. Projection correction L2
<=0.02rad, maxdepth12, midpoint budget1023, path budget1025. No wrap or endpoint
repair/snap. These conservative finite guards are ENGINEERING, not paper/Benchmark
success thresholds or proof of manifold-branch identity.

Original SRDF ACM/padding/scales untouched, no new touch links. Cube represented
as a native AttachedBody using fixed left TCP->Object solely inside a private
RobotState; original right grasp supplies C/Jc. This reuses the old native attach
API but imports no top-tool transform or contact exemption. All raw unexpected
penetrations reject; inherited SRDF legal mounting contacts remain allowed.
Exact Cube/tool contact pairs are identified in evidence, **not newly exempted**.
The historical fixed grasp includes ~1mm nominal cup gap; no suction validation.
Attached-body native FCL also checks carried Cube versus table/walls; no AABB engine.

Exactly ten positive connections: original stored projected q0 identical; q0<->q1
and q0<->q4; once-fixed G* q0 identical; G* q0 to four stored projected single-joint
neighbors (joint0/joint7, +/-0.03rad). No online IK, grasp fitting or random search.
One real collision-negative connection: add an explicitly NEGATIVE-TEST-ONLY
0.120m box at actual left TCP of already-closed original q0; all original scene
objects remain unchanged. This is genuine FCL interpenetration, not a mock callback
or Benchmark geometry change. Native bounds and invalid-closure negative endpoints
are also checked. Synthetic unit tests cover projection/continuity/budget/midpath
failures but do not substitute for native FCL evidence.

No candidate selection/tuning after results. Scene load/resource/count failure
ends native acceptance as PARTIAL. Every native checked point records C, exact q,
margin, self/world results, contacts and ACM identity. Compute wall time is only
software cost, never physical duration; simulation time/step remain null.

Paper: https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf
Attribution: ORIGINAL RBS; ADAPTATION FR3/FCL; ENGINEERING finite guards/logging.
No full P4 planning or continuous-collision claim. Stop after GitHub report.
