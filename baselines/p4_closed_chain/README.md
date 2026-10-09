# P4 closure residual and Jacobian — offline TASK03

Subsequent bounded TASK04 projection is **PASS CANDIDATE (OFFLINE MATHEMATICS ONLY)**.
See [projection implementation/contract](PROJECTION.md) and
[TASK04 POST-TASK REPORT](../../reports/TASK04_NR_PROJECTION01.md). It reuses the
unchanged C/Jc/FK below; new projected q never replace original precision FAIL.
Constraint-path connection/RRTConnect/full P4 remain unimplemented. Stop for review.

**TASK03 = PASS CANDIDATE (OFFLINE MATHEMATICS ONLY)** after user reviewD047.
Original historical configuration precision remains **FAIL** with unchanged0.05μm
threshold and0.435028μm maximum. No source/test/model/grasp or historical result edit.
This is a reviewed classification, not a tolerance relaxation. The prior delivery
was **PARTIAL**: residual/Jacobian software checks pass; original historical
fixed-grasp closure does not satisfy the predeclared positional precision. No
projection, local connection, constrained planner or physical shared-grasp proof.
The parent Benchmark is DRAFT / NOT FROZEN.

## Attribution and reuse

[ORIGINAL] P4 II-A Eq. (1)/(2) defines rigid-chain closure `C(q)=0`, with joint
limits and collision validity separate. [ADAPTATION] The following dual-FR3
SE(3) chart is our explicit mapping, **not a formula printed in P4**.
[ENGINEERING] Numerical SO(3) validation, finite differences and an offline adapter
to the existing MoveIt RobotModel/RobotState. The predecessor shared-object planner
is a thin-adapter/reference oracle: its top-suction `.105 m` midpoint/drift gates
are not a full rigid pose residual and are not imported here. See
[P4 paper card](../../references/P4_closed_chain.md) and
[evidence/report](../../reports/TASK03_CLOSURE_CONSTRAINT01.md).

## Frames and transform direction

`T^A_B` maps coordinates **from B into A**. All joints are rad, position m.
`q=[qL1..qL7,qR1..qR7]`. World→base→existing FR3 joint1..7→link7→fixed
joint8→link8 (flange)→side-suction TCP uses unchanged model FK. TCP is the
cup frame, not link8, hand, a midpoint or object center.

For a fixed grasp `G_i = T^TCP_i_Object`, compute

\[
T_i = {}^WT_{TCP_i}(q_i)G_i = {}^WT_{O,i},\qquad
C(q)=\begin{bmatrix}p_L-p_R\\\phi\end{bmatrix},\quad
\phi=\operatorname{Log}(R_R^TR_L)^\vee.
\]

Position rows are expressed in world, metres. Rotation rows are expressed in the
right **predicted object** axes, radians. This mixed-frame 6-vector is an explicit
local chart, not a global smooth chart or an automatically weighted success norm.
Quaternion xyzw and its negation represent the same SO(3) input; no Euler subtraction.

Historical config stores the opposite transform `H_i=T^Object_TCP_i`; the test
adapter explicitly uses `G_i=H_i^-1`. Parameters remain caller-supplied: production
math contains no old Cube size, cup clearance or historical success threshold.

## Analytic Jacobian

Let the world geometric **TCP-origin** Jacobian be `[V_i; Omega_i]`, and
`r_i=R_world_TCP_i G_i.translation`. The predicted object-origin Jacobian is
`B_i=V_i-[r_i]_x Omega_i`. The derivative is

\[
J_c=\begin{bmatrix}
B_L & -B_R\\
J_l^{-1}(\phi)R_R^T\Omega_L & -J_l^{-1}(\phi)R_R^T\Omega_R
\end{bmatrix}\in\mathbb R^{6\times14}.
\]

For `K=[phi]_x`,
`Jl^-1=I-K/2+a K²`,
`a=(1-theta/2*cot(theta/2))/theta²`; use the small-angle series
`1/12+theta²/720+theta⁴/30240`. SO(3) log at pi is branch ambiguous:
residual still describes a rotation; analytic Jacobian evaluation explicitly
rejects `theta >= pi-1e-8`. This is numerical chart qualification, not a
Benchmark rotation success tolerance. Invalid/nonfinite/scaled rotation inputs
are rejected, not silently projected onto SO(3).

MoveIt 2.5.9 `RobotState::getJacobian` uses the parent of the group's first joint
as its reference. The adapter rotates **both** geometric blocks into world. It
does not apply the translation adjoint of a spatial screw twist. A rotated-base
coordinate-gauge unit test covers this distinction without changing source models.

## Three evidence classes — do not merge

1. Synthetic toy mapping: pure mathematical unit tests, not FR3 or physical proof.
2. Original FR3 + archived original grasps: FK/original bounds and derivatives at
   293 saved records (292 unique q), plus critical-state perturbations. Historical
   IK was approximate. Maximum closure `4.35027826256e-7 m` exceeds the predeclared
   `5e-8 m` precision in 219 records. This negative acceptance result is retained.
3. Real FR3 **algebraic fixed-grasp test fixture**: at archived START q0 only,
   `G*_i=FK_i(q0)^-1 O0` is constructed once, then held constant for all tests.
   This gives an exact mathematical zero-residual configuration and detects joint
   perturbations. It is **not** a benchmark grasp, sensor calibration, IK solution,
   suction adjustment or replacement for evidence class 2.

Declared engineering precision: original closure `5e-8 m / 2e-5 rad`, FK oracle
`1e-11 m/rad`, Jacobian max element error `2e-7` (position rows m/rad; rotation
rows rad/rad), frame-gauge arithmetic `1e-11`. These were not relaxed after results.
They are offline tests, not formally approved benchmark thresholds.

## Run without simulator/services

Prerequisites: existing ROS Humble MoveIt core libraries, Eigen3, yaml-cpp,
nlohmann-json and Python TASK02 dependencies. Sourcing environment scripts does
not launch ROS. No `rclcpp::init`, node, MoveGroup, IK, FCL query or command sender
exists in this adapter/test. No physics time is invented.

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
# Resolve unchanged package://franka_description mesh URIs if installed there:
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/install/setup.bash
cmake -S platforms/offline_moveit/task03_closure -B build/task03_closure \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build/task03_closure --parallel 2
PYTHONPATH=. /usr/bin/python3 scripts/run_task03_offline.py \
  --run-id YOUR_NEW_TASK03_RUN_ID
```

The unchanged TASK03 logger refuses an existing run directory. Software exit0 means the offline
tests pass; `task03_status`, `result.json` and the report independently preserve
PARTIAL/INCOMPLETE when original closure acceptance fails. Seeds are explicitly
UNSET; tests are deterministic, with no random IK. These are original delivery
semantics and are not rewritten after review. TASK04 has separate acceptance,
config/results and user authorization; see its task card. No full P4 reproduction.
