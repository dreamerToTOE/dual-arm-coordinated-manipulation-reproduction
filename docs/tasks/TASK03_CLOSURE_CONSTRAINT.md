# TASK03 — P4 Closure Constraint

Status: **PASS CANDIDATE (OFFLINE MATHEMATICS ONLY)** (2026-10-09 user reviewD047)

Acceptance scopes are separate:

- Mathematical implementation: PASS CANDIDATE; real-FR3 Jacobian FD validation passed.
- Historical configuration precision: **FAIL**; original293records max0.435028μm
  versus unchanged0.05μm. Original data/grasps/model/source/tests/results not changed.
- Complete P4 reproduction: not established; TASK03 contains no projection,
  constrained local connection or RRTConnect conclusion.

This approved scope classification does not relax a numeric tolerance. The original
partial delivery/report/test status fields are retained as historical evidence.

Software base36c95ab, task branch `task03-p4-closure-constraint`.
TASK02-D remains PARTIAL / DEFERRED; parent TASK02 IN_PROGRESS;
Benchmark DRAFT / NOT FROZEN. Native measurement qualification is not an offline
math dependency. Original Task26 engineering foundation remains accepted.

## Goal
Define the shared-object closed-chain constraint for dual FR3.

## Method
For q=[qL,qR], both end-effector/grasp chains must predict the same object pose. Define residual C(q) and constraint Jacobian Jc.

## Codex actions
- Implement FK-based object pose from each arm.
- Define translational + rotational closure residual.
- Implement/verify Jc.
- Add finite-difference Jacobian checks.
- Test valid shared-object states and perturbed states.

## Approved scope / minimum sufficient evidence

Pure offline math and tests only. Reuse the existing FR3 RobotModel/RobotState
FK and unchanged side-tool definitions, with explicit world/base/flange/TCP/
Object transforms. Verify rigorous six-dimensional closure and 6×14 Jacobian
against independently evaluated FK finite differences, bounds, original archived
FK oracle, fixed grasps and perturbations. Keep synthetic and real-model evidence
separate; real-model math is not physical holding/collision proof.

No Isaac/ROS service/MoveIt node/controller, Observer, IK regeneration, Newton
projection/TASK04, original Task26/rail/SG/physics/FCL/ACM modification or
benchmark edits. Linking existing MoveIt kinematics libraries is not starting
its planning service.

## Predeclared engineering tests — not frozen scientific thresholds

- Original fixed-grasp closure: position≤5e-8m, attitude≤2e-5rad.
- Existing FK vs stored oracle: position/angle≤1e-11m/rad.
- Analytic vs central FD (h=1e-5,3e-6,1e-6rad) and independent five-point FD
  (h=3e-6rad): max entry error≤2e-7, with row-specific units m/rad or rad/rad.
- Rotated coordinate-gauge arithmetic≤1e-11; quadratic remainder halving ratio
  3.8–4.2. No test automatically sets formal Benchmark SUCCESS.

## Current result / stop

Software math, FK/bounds and derivative tests pass. The original fixed-grasp
fixture is approximate historical IK: 219/293 records exceed positional precision;
maximum4.35027826256e-7m atstate196; rotational maximum1.22663962184e-5rad passes.
The original delivery reported **TASK03 = PARTIAL**, before the scope review above.
That diagnostic remains unchanged. No threshold, grasp or IK adjustment.
One-time algebraic fixed-grasp zero-residual fixtures on the real FR3 model are
software tests only and cannot replace this failed original-grasp acceptance.

Historical precision acceptance remains unmet; mathematical evidence is accepted
underD047. User separately authorizes bounded offline TASK04; no automatic TASK05/06
or scientific Benchmark freezing. This does not authorize rewriting TASK03 tests.

[Source/formulas](../../baselines/p4_closed_chain/README.md),
[POST-TASK REPORT](../../reports/TASK03_CLOSURE_CONSTRAINT01.md).
