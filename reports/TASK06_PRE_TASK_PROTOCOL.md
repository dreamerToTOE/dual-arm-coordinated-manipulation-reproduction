# TASK06 pre-task / pre-experiment protocol

2026-10-12; baseline `91a1adc`; branch `task06-p4-constrained-rrtconnect`.
This document and its JSON protocol are committed **before any new planning experiment**.

## PRE-TASK REPORT

- Task: bounded offline P4 NR constrained bidirectional RRTConnect.
- Scientific objective: compose accepted C/Jc/FK, Newton–SVD projection and RBS/FCL
  into nontrivial closed-chain search, not unconstrained MoveIt planning and repair.
- Minimum sufficient evidence: real FR3 nontrivial dual-tree path, every inserted
  edge qualified by TASK05, private-obstacle direct-connection rejection and search
  detour, deterministic repeats and explicit negative/budget evidence.
- Scope: one fixed software implementation and finite offline seed suite.
- Non-goals: Isaac, ROS services, robots, Task26, Observer, benchmark freeze,
  PCS/RSS variants, smoothing, execution timing, continuous safety, TASK07.
- Attempt budget: one scientific protocol/suite; at most governance diagnosis/fix/
  fallback for a software blocker, no scenario/seed/budget retuning after results.
- Preferred method: independently implemented source-audited NR search loop using
  unchanged accepted mathematical/FCL implementations.
- Fallback: PARTIAL with retained failed evidence; no alternate collision engine.
- Stop/escalation: native assets unavailable, fixed acceptance unmet, or governance
  blocker budget exhausted. No outcome-driven extra trials.
- Expected files: new `constrained_rrtconnect.{hpp,cpp}`, tests, runner, standalone
  offline CMake/harness/evidence, protocol/audit/report and task/status records.
  Read-only getters in TASK03 model adapter and private-box insertion in existing
  TASK05 collision adapter; mathematical/collision semantics unchanged.
- Validation: synthetic orchestration guards, prior TASK02–05 regressions, three
  real scenes × three seeds × two repeats, frozen protocol/hash protection.
- Risks: NR may reject samples or reach bounds; the fixed private obstacle may not
  yield a path within budget. Then PARTIAL, not retrospective tuning. Wall-time
  cutoffs can prevent deterministic counts; such a repeat fails the declared gate.
- User confirmation needed: no within this explicitly authorized offline slice.

## PRIOR-ASSET CHECK

- New scientific work: P4 constrained bidirectional search and parent-tree assembly.
- Searched: pinned predecessor `shared_object_planner`, `spatiotemporal_conflict_detector`,
  Task16 seed/logging and its ordinary MoveIt planning usage; current TASK02–05.
- Pinned old source: `631b1f65656d025c1bb2173e874192f3fe4d355a`.
- DIRECT_PORT: none; accepted current implementations reused by linking/import.
- THIN_ADAPTER: existing RobotModel native FK/bounds and private PlanningScene/FCL;
  only expose native position bounds and already existing private world-box function.
- TEST_ORACLE: unchanged original model/meshes/ACM, archived projected configurations;
  TASK02 metadata/results, TASK03–05 regressions, old Task16 file-log experience.
- REFERENCE_ONLY: original author code; old shared-stage/robust motion selection.
- Rejected: external MoveGroup ordinary RRTConnect, old tool/Cube ACM exemptions,
  top-grasp offset, control timing, candidate selectors and scheduling policies.
  These are not P4 closed-chain search and/or contaminate fixed grasps/acceptance.
- Reused files: `closure`, `projection`, `local_connection`, existing model/collision
  adapters and JSON serializers, `common/logging/run.py` and result contracts.
- New files: only search orchestration, tests/harness and scoped evidence/report.
- Fidelity risk: clearly separate FR3/FCL adaptation and conservative engineering
  guards from original method. No fresh projection/FK/FCL or author-only source copy.
- User decision needed: no; material algorithm deviation would require stopping.

## Primary method audit

[P4 original manuscript](https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf),
II-B.2/II-C/III-C/IV: NR projects sampled/interpolated candidates; RBS projects
midpoints and recursively validates; standard bidirectional sampling planners;
rigid held object is part of the chain. Paper experiments use KDL/SVD and PQP,
not FR3/MoveIt. No complete planner pseudocode or universal optimal range is given.

[CKCplanning source](https://github.com/avishais/CKCplanning/tree/909bd72fff778aca8682c96f9eb86ae4eb75557b),
`planners/CBiRRT_NR.cpp:132–207,271–370`, `CBiRRT_NR.h:168–170`,
`run/plan_NR.cpp:80–110`, `validity_checkers/StateValidityCheckerNR.cpp:115–176`:
alternate trees; uniformly sample ambient bounds; nearest in Euclidean space;
bounded raw steering then NR projection then RBS before inserting every node.
Both grow modes repeat, with calls 100/500 and inclusive loop giving 101/501
attempts. Final connect to an existing target skips projection and validates its
exact RBS edge. Even a trapped first tree is followed by connection from the other.
Backtrack parent chains and remove duplicate meeting configuration. No smoothing.

| Label | Implementation choice |
|---|---|
| ORIGINAL | above source-audited two-tree grow/project/RBS order and exact final connect |
| ADAPTATION | 14D dual FR3, accepted C/Jc/SVD/RBS, existing native FCL rather than PQP |
| ENGINEERING | stable linear NN; explicit mt19937_64 and binary53 uniform mapping; fixed budgets checked inside growth; exact endpoint qualification; progress/projection/accepted-step bounds; complete failure traces |
| DEVIATION inherited/explicit | TASK04 rejects rank<6 corrections instead of claiming general singular passage; TASK05 uses preapproved locality/continuity guards. This slice does not claim the paper's singularity experiments or performance reproduction. No new planning heuristic or bias. |

Author original numerical RBS resolution `.05`, depth150, KDL tolerance1e-5,
10,000 iterations and angle wrapping are **not** imported into FR3. Existing
TASK04/05 accepted guards are unchanged. Author default OMPL/KDL versions/NN are
not pinned, so exact upstream binary behavior is not claimed. No repository-wide
license found: planner files carry BSD notices, author validity/KDL files do not.
All are REFERENCE_ONLY; no upstream source is imported.

## Fixed engineering experiment

[Machine-readable protocol](../configs/engineering/task06_constrained_rrtconnect_test_v1.json)
is normative. Original grasps, URDF, SRDF, table/walls, meshes and old raw results
remain unchanged. Source endpoints are **already stored** TASK04 projected states,
not new random IK or newly fitted grasps. Simple0→1, nontrivial0→100 and a separate
private obstacle0→100. Nominal archived object centers for0/100 are
(.550,0,.380)/(.7277777777777779,0,.2911111111111111). They are engineering fixture
metadata, not current frozen benchmark or new measured physical states.

Private BOX center is their nominal arithmetic midpoint, size(.020,.180,.120)m;
chosen geometrically without running any endpoint/connector/planning evaluation.
It intersects nominal straight motion and leaves nominal endpoint x gaps≈.018889m.
Actual FCL endpoint clearance and direct RBS collision must be established by tests;
if unsuitable, record failure and **do not move/resize** it.

Uniform full-native 14D bounds, seeds7/41/20261012, two repeats each; no goal bias,
weighted metric, sample prescreen, shortcuts or direct-return path. Raw step.20rad,
candidate correction≤.25rad, accepted step≤.45rad, progress>1e-12rad. Grow caps
101/501; ≤600 nodes/800 outeriterations/20 wall-seconds per call. Each invocation
is bounded; runner has an outer finite cap. Prior TASK05 leaf.01rad and correction
.02rad remain unchanged. Separate position/rotation convergence≤1e-8m/rad.

All simple seeds succeed; at least one nontrivial and obstacle seed must grow both
trees and have≥3 accepted tree edges on returned solution; obstacle direct RBS must
be rejected specifically for collision. All repeats must match status, path and
deterministic search counters. Save every sampled vector, projection, attempted
edge's full TASK05 evidence, trees/parents, ordered dense path and deterministic
fingerprint. Negative tests cover bounds/projection/connection/iterations/nodes/
wall limits and actual native collision. Failed search is not impossibility proof.

No minimum distance API is requested: report UNAVAILABLE. No positive clearance
inferred from zero contacts; discrete checking is not a swept-volume certificate.
Retain TASK02-D DEFERRED, parentTASK02 IN_PROGRESS and BenchmarkDRAFT. Stop after
GitHub delivery as TASK06 PASS CANDIDATE or PARTIAL, wait for review.
