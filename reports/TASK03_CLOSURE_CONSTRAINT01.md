# TASK03 — P4 closure mathematics, offline evidence

## Subsequent user reviewD047 (original report/results retained)

User accepts **PASS CANDIDATE (OFFLINE MATHEMATICS ONLY)** for the mathematical
implementation and verified real-FR3 Jacobian. Historical293-configuration precision
remains **FAIL**: max0.435028μm versus original0.05μm, no numerical/source/data/G/model
change. Full P4 reproduction is incomplete; TASK03 establishes no projection,
constrained connector or RRTConnect. This is a reviewed acceptance-scope classification,
not a tolerance relaxation. The following report and all original JSON/test outcomes
retain the pre-review PARTIAL result. TASK04 is separately authorized; its projected
configurations must not overwrite these original fixtures or results.

2026-10-09 · software base `36c95ab` · branch `task03-p4-closure-constraint`

**TASK03 = PARTIAL / USER REVIEW**

**TASK02-D = PARTIAL / DEFERRED; TASK02 = IN_PROGRESS**

**BENCHMARK = DRAFT / NOT FROZEN**

Residual/Jacobian implementation and real-model derivative tests pass. Original
fixed-grasp historical closure does **not** meet the declared positional precision.
The failed acceptance is preserved, not repaired by threshold/IK/grasp changes.
No Isaac, ROS node/service, MoveIt planning server or original Task26 controller
started. No Newton/projection/planning algorithm or physical holding proof.

## PRE-TASK REPORT (declared before implementation)

```text
Task: TASK02-D audit closure + TASK03 P4 rigid-chain residual/Jacobian
Scientific objective: explicit dual-FR3 object-pose closure and trustworthy derivative
Minimum sufficient evidence: primary P4 math attribution; same existing FR3 FK;
  fixed-grasp/perturbed model states; finite differences; frame/SO3/limits tests
Current scope: pure Eigen math, thin offline MoveIt-core model adapter, tests/files
Explicit non-goals: physics/ROS planning services/control/Observer/IK/projection;
  benchmark/Task26/SG/rails/tool/carriage/ACM/gates edits; TASK04
Attempt budget: one bounded offline implementation; runtime allowance0
Preferred method: original RobotModel/RobotState, immutable historical FK/q fixtures,
  analytic derivative + central and independent five-point differences
Fallback: clearly qualified synthetic/algebraic mathematical fixtures; never replace
  a failed original-grasp acceptance claim
Stop/escalation: required benchmark/geometry/acceptance change or missing true-model
  evidence; report PARTIAL rather than silently alter criteria
Files expected to change: common/geometry, P4 closure, offline adapter/tests, evidence,
  task/paper/report and persistent records
Validation: FK oracle 1e-11m/rad; closure5e-8m/2e-5rad; J entry2e-7 with
  h={1e-5,3e-6,1e-6}; limits; quaternion signs/frames; TASK02 regression
Known risks: historical IK is approximate; old top-TCP drift is not SE3 closure;
  MoveIt Jacobian reference frame; log pi branch; no physical/native time evidence
Need user confirmation: no for this explicit offline slice; yes for acceptance revision
```

The main agent reread repository governance/task/reuse/benchmark documents, inspected
the entire original shared-object planner and tool/model definitions, and consulted
the primary paper. Independent paper/math review found no blocking sign, lever-arm,
reference-frame or SO(3) implementation defect. This is not full P4 reproduction.

## PRIOR-ASSET CHECK

```text
Current task: TASK03
New paper-derived work: rigid-chain mathematical residual and derivative; P4 generic C=0
Old areas searched: shared_object_planner.hpp/.cpp; FR3 common model and dual side tools;
  previous geometry q/FK/config records; Task14 and Task16 evidence patterns
Pinned source: dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a
DIRECT_PORT: none of the runtime planner or controller
THIN_ADAPTER: existing MoveIt RobotModel/RobotState FK/geometric Jacobian/URDF bounds
TEST_ORACLE: archived293 q/TCP FK records; unchanged model/config; Task16 file metadata
REFERENCE_ONLY: old top-suction midpoint/progress/relative drift/synchronized resampling
Rejected: hard-coded top-tool .105m, old gate thresholds and entire planning/executor
  shell; they cannot replace full SE3 closure or fit this offline scope
Reused: original FR3/tool model and existing FK, accepted TASK02 RunLogger/contracts
New: explicit local closure/Jc, pure rigid arithmetic and derivative verification tests
Risk: algebraic grasp fixture or superseded bilateral TARGET mistaken for physical/
  current benchmark evidence; strictly label as mathematical tests only
Need user decision: yes before changing original-grasp offline acceptance policy
```

Pinned source SHA256:

```text
shared_object_planner.hpp 75331295e39c26296a1f07be56e418b76a5a66a88ec07fa9d63bfaf1b42679ec
shared_object_planner.cpp f591324b838fc806034f03f1bdc31c69cba68d2682506bc495ff6986fde410bc
dual_fr3_side_suction.urdf.xacro 3f72a4d6d14967bfa98db5ee3e6c31c1e03927abbd12f0d7c0f26bfbdc3bfea6
dual_side_suction.xacro a0630156df03502e6624f593041db3e5f281f52958512672049b60b31ed49f1d
```

## Formulas, frames and provenance

The [implementation README](../baselines/p4_closed_chain/README.md) supplies full
formulas and directions. With `G_i=T^TCP_i_Object`,
`T_i=FK_world_TCP_i(q_i)G_i`, `ep=pL-pR`, `phi=Log(RR^T RL)^vee`.
Position is world-m; rotation is right-predicted-object-rad. `Jc` has left-minus-right
object-origin linear blocks and `Jl^-1(phi)RR^T` angular blocks. Fixed grasp lever arms
are included. No Euler subtraction or quaternion-sign dependence; pi derivative rejects.

P4 full manuscript II-A Eq.(1)/(2) is [ORIGINAL] rigid-chain framework; this explicit
FR3 chart/Jc is [ADAPTATION], not a printed P4 formula. See [paper/source audit](../references/P4_closed_chain.md).
MoveIt 2.5.9 Jacobian implementation is the primary adapter reference:
[robot_state.cpp](https://github.com/moveit/moveit2/blob/2.5.9/moveit_core/robot_state/src/robot_state.cpp#L1202).
Both geometric blocks are rotated from first-joint-parent axes to world; coordinate
gauge test covers nonidentity base rotation. No independently invented FR3 DH chain.

Historical model frames: world→left/right base xyz(.650,∓.600,0), identity orientation;
joint1..7 from original description; link7→link8 fixed xyz(0,0,.107), identity;
tool mount identity; link8→TCP left(0,-.155,.080), yaw−pi/2, right(0,+.155,.080),
yaw+pi/2. Archived `T_Object_TCP` xyz(0,∓.061,0), xyzwleft(sqrt(.5),sqrt(.5),0,0),
right(sqrt(.5),-sqrt(.5),0,0). Adapter takes the inverse once. These are **historical
fixture values**, not new production defaults or approved benchmark calibrations.

Exact expanded URDF/SRDF copies (hash-matched, with dependency license/provenance)
are in [tests/fixtures/task03](../tests/fixtures/task03/README.md). Archived q/FK input
`results/20261007_TASK01_full_single_cube_geometry01/state_records.json` SHA256
`607c30480ae264fd20ae4a09a750d5af6acb992d6d67c65a86103f86baa88d8e` is unchanged.
293 records contain292 uniqueq because PRE_PUSH is represented in both segment boundaries.
This superseded bilateral-to-TARGET archive is a math oracle, **not** current
Benchmark B, accepted foundation physics or a held-object measurement stream.

## Actual offline results

Final evidence: [summary](../results/20261009_TASK03_closure02/summary.json),
[full numerical metrics/example C and Jc](../results/20261009_TASK03_closure02/model_metrics.json),
[typed result](../results/20261009_TASK03_closure02/result.json),
[metadata/source and artifact hashes](../results/20261009_TASK03_closure02/metadata.json).

[Scope audit](TASK03_SCOPE_CHECK.json): accepted predecessor4/4 assets match the
existing manifest, including original controller source/binary. Benchmark SHA256
`fbef560ae81963fdf5839cd83d95274edebd9769024d1ae74527f00092c8f2a2` unchanged;
TASK02 interfaces/metrics/logger, foundation and archived geometry results unchanged
against36c95ab. Copied model files byte-identical; all final source/artifact hashes
read back correctly. Environment: g++11.4.0,Python3.10.12,MoveIt core2.5.9.
This is file/software scope evidence, not runtime/native measurement attestation.

| Check | Actual result | Qualification |
| --- | --- | --- |
| TASK02-A/B/C regression | 72/72 PASS | Offline contracts, not native sensing |
| Pure synthetic closure tests | 93 checks PASS | Toy mapping, not FR3 |
| Real FK vs archived TCP | max0m / 6.107e-16rad | Same existing model |
| Original293-record joint margin | min0.461828rad | Original URDF bounds |
| Original grasps + critical perturbations | 405 derivative configurations PASS | Original G unchanged |
| Once-fixed algebraic FR3 grasps | 29 derivative configurations PASS | Test-only G*, not calibration |
| Rotated-frame real-model gauge | 1 derivative configuration PASS | In-memory coordinate test |
| Overall central FD max element | 3.281e-10 versus2e-7 | 435 configs, three h values |
| Independent five-point max | 1.545e-10 versus2e-7 | Same435 derivative configs |
| Linearization halving ratios | ≈4.000 | Quadratic residual remainder |
| **Original-grasp position closure** | **max0.435028μm; 219/293 >0.05μm** | **Acceptance NOT MET** |
| Original-grasp rotation closure | max1.22664e-5rad <2e-5rad | Acceptance met |

All28 ±.01rad single-joint perturbations of the fixed algebraic FR3 fixture produce
nonzero closure (minimum position1.586mm, rotation.01rad). Its q0 residual is
1.145e-16m /1.117e-24rad. `G*` is computed once, then remains fixed; it is explicitly
not a replacement for original `G`. Original state196 worst residual is retained.
No new IK/NR solve or original result edit occurred.

The **0.05μm** positional test was our predeclared offline engineering precision,
not a user-approved scientific benchmark success threshold. The observed residual
is consistent with approximate historical IK/encoding. It is **not evidence of a
physical collision or failed suction**. We did not loosen it after seeing results.
Current missing acceptance is a precision/fixture review decision, not a reason to
modify mature scene/bridge, apply projection, fit grasps or rerun Isaac.

## Commands and environmental diagnostics

Full reproduction commands are in the [README](../baselines/p4_closed_chain/README.md).
Final runner invokes only TASK02 unittest, synthetic math, CTest and real-model
offline executable, each bounded≤60s. SeedUNSET/noRNG, simstamp/stepnull. Source hashes
identify the working implementation independently of the pre-commit base hash.
RunLogger records `INCOMPLETE` with failure stage original fixed-grasp precision;
software exit0 and `PASS_OFFLINE_MATH_ONLY` cannot be mistaken for TASK03 PASS.

Initial configure without sourcing Humble failed on `ament_package`, and a prior
binary could not resolve `libmoveit_kinematics_base`. Sourcing installed dependencies
resolved this build/environment issue, not an algorithm or physical defect. First
successful math run [closure01](../results/20261009_TASK03_closure01/model_metrics.json)
reported unresolved `package://franka_description` meshes: kinematics still valid,
not collision evidence. Final environment sources the existing predecessor install;
its missing `fr3_dual_palletize/local_setup.bash` warning does not load a controller
or change FK. Final real-model log preserves actual resource resolution messages.
No install files or environment packages edited.

## POST-TASK REPORT

```text
Task: TASK02-D closure and TASK03 P4 closure math
Status: TASK03 PARTIAL; offline math/derivatives PASS; TASK02-D PARTIAL/DEFERRED
Scientific objective: explicit rigid shared-object closure and trustworthy Jc on FR3
Minimum sufficient evidence achieved: yes for software mathematics/derivative;
  no for original fixed-grasp configuration acceptance at predeclared5e-8m
Completed: primary-source audit, prior-asset reuse audit, formulas/frames, pure math,
  existing FK adapter, 435 real-model derivative checks, 72 old +93 math regression,
  immutable input snapshots, structured source/artifact/result evidence
Files changed: baselines/p4_closed_chain; common/geometry; platforms/offline_moveit;
  tests/math + exact fixture; offline test runner; reports/references/task/six records
Commands run: sourced installed build environment; cmake configure/build; offline
  unittest/math/ctest/model tests; hashes/diff audit; git commit/push
Tests/metrics: see actual results table and full JSON; original position precision FAIL
TASK-BLOCKING: original-grasp acceptance/precision review for complete TASK03 claim
DEFERRED: real Isaac clock/step/reset binding, Observer, force/TASK10-IS
KNOWN LIMITATION: approximate archived IK, local SO3 chart, library-version coupling;
  algebraic fixture not independently physical; superseded execution topology
LEGACY: old Task26/Task27 execution; unchanged and not rerun
Attempt budget used: one bounded offline implementation; no runtime; no original-G
  repair/projection/re-IK or threshold iteration. Stop, no automatic new acceptance route
Escalation required: user review for precision/fixture decision, not further engineering
Paper fidelity: ORIGINAL generic rigid C=0; ADAPTATION dualFR3 pose chart/Jc;
  ENGINEERING robust SO3/existing FK/tests/logger; DEVIATION none introduced;
  EXPERIMENTAL algebraic/gauge software fixtures clearly separated
Records: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK updated
Open risks: original closure precision unaccepted; no physical or collision proof
Recommended next: review original-grasp engineering precision/fixture policy; do not
  start TASK04, physical experiments or benchmark freezing automatically
Git: task03-p4-closure-constraint; scoped commit; old unrelated raw logs excluded
```
