# TASK05 local connection contract

`connect(start, goal, C/Jc, native_bounds, collision, explicit_options)` is
data/math only. It cannot command a robot, call ROS services or modify a simulator.
It uses **unchanged** TASK03 evaluate() and TASK04 project() through read-only callbacks.

## Method / attribution

[ORIGINAL] P4 II-C (printed p.3), Recursive Bi-Section: project the current segment
midpoint, check validity, then recursively connect each half. P4 IV experiments
use RBS. [ADAPTATION] 14 bounded FR3 revolute joints, existing SE(3) residual and
FCL instead of paper PQP. [ENGINEERING] explicit locality/budget/failure evidence.
[Primary paper](https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf).

```text
validate exact start and goal (no projection/repair/snap)
prefix = [start]
rbs(a,b):
    if distance(a,b) <= resolution:
        require projected adjacent L2 and max-abs limits
        append b to ordered verified prefix
    else:
        check finite depth/projection budget
        m = unchanged project((a+b)/2)
        require CONVERGED and bounded correction
        require finite/native bounds/separate C norms/native collision evidence
        rbs(a,m), then rbs(m,b)
```

The exact goal is appended only after the connecting left subtree completes.
Any failure rejects the **whole** connection. `verified_prefix` is for diagnostics,
not an executable partial-success recommendation. `checked_points` can contain
valid future midpoints/endpoints which are **not** reachable prefix points.
`leaf_edges.accepted` means the adjacency gate and append succeeded.
Projection failure retains its original status, initial/final q, singular values,
accepted/rejected update trace. Projection's finite last q is not a success flag.

No per-joint wrap, clamp, branch selection, alternate IK or hidden retry. Separate
position/rotation tests avoid mixing m/rad in convergence. Original pseudoinverse
does retain fixed SI row units; no scale-invariance claim.

## Collision / measurement boundary

CollisionEvaluator is data-only. Incomplete/exception/contradictory free+contacts
fails closed. Real tests instantiate the same MoveIt RobotModel from immutable
URDF/SRDF, load original meshes and private PlanningScene, pin native FCL, and run
unfiltered self (including inter-arm) and robot-world checks.

The carried Cube is a native AttachedBody under left TCP with original fixed G;
right TCP closure is still checked by existing C/Jc. Empty touch-links and original
SRDF ACM: **no added suction/Cube exemption**. Original allowed installation pairs
are explicitly declared in the backend manifest; reported raw tool/Cube penetration
is not auto-exempted. This models geometry, not Surface Gripper attachment/dynamics.
Native carried-body/world checking covers Cube-environment without a new AABB
collision engine. Contact category/depth/body names are FCL model predictions,
not Isaac contact wrench or calibrated physical measurements.

## Limits / protocol

See precommitted `configs/engineering/task05_local_connection_test_v1.json` / D050.
Engineering precision and continuity limits are not frozen Benchmark thresholds.
Finite checked states/adjacent steps do **not** certify continuous swept collision
safety, all intermediate points lying exactly on the manifold, or same branch.
There is no time parameterization, actuator model or robot execution. Compute
wall time is software cost; simulation step/time are null. TASK02-D remains DEFERRED.
Archived original bilateral fixture is offline mathematical evidence only, not
the current handoff benchmark or a validated physics model parity claim.
