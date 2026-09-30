# TASK00 — Environment Audit

Date: 2026-09-30 (Asia/Shanghai)
Status: PASS as an audit; the integration gaps below remain open for later tasks.
Audit branch: task00-environment-audit
Reference commit at probe time: 9f71e0a78a9d852d060b4e7e4c3225558d1d9bb1

## Scope and provenance

This is a read-only audit of the host and an existing, separate palletizing workspace. It does not claim that this reproduction repository already contains a robot adapter, force controller or paper baseline. The old workspace was not modified. No major dependency was installed.

The legacy Isaac Sim GUI, ROS bridge and MoveIt processes were active during the first ROS graph snapshot, then exited before follow-up queries. The live samples below are therefore a time-bounded observation, not a fresh-launch or repeatability result for this repository.

## Host and software

| Item | Observed result | Evidence command |
|---|---|---|
| OS/kernel | Ubuntu 22.04.5 LTS; Linux 6.8.0-138-generic x86_64 | lsb_release -a; uname -srmo |
| CPU memory | 46 GiB total; 31 GiB available at audit time | free -h |
| GPU | NVIDIA GeForce RTX 3070, 8192 MiB, compute capability 8.6 | nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader |
| Driver | 580.178.04 | nvidia-smi |
| CUDA | nvidia-smi reports driver-supported CUDA 13.0; no nvcc or /usr/local/cuda toolkit found | nvidia-smi; nvcc --version; ls -l /usr/local/cuda |
| Python/system | 3.10.12 | python3 --version |
| GCC/G++ | 11.4.0 | gcc --version; g++ --version |
| CMake | 3.22.1 | cmake --version |
| colcon-core | 0.21.0 | python3 -m pip show colcon-core |
| ROS 2 | Humble; ros-base 0.10.0; ros2cli 0.18.18 | ls /opt/ros; dpkg-query -W |
| MoveIt 2 | 2.5.9 | dpkg-query -W ros-humble-moveit ros-humble-moveit-core |
| OMPL | ROS package 1.7.0 | dpkg-query -W ros-humble-ompl |
| FCL | libfcl 0.7.0-3 | dpkg-query -W libfcl-dev libfcl0.7 |
| Isaac Sim | 4.5.0-rc.36+release.19112.f59b3005.gl, installed at /home/ubuntu2004/isaacsim-4.5.0 | sed -n '1,20p' /home/ubuntu2004/isaacsim-4.5.0/VERSION |
| MuJoCo | 3.13.0 in legacy project's isolated .venv; minimal mj_step passed | see MuJoCo probe below |

The currently detected GPU is RTX 3070, not the RTX 4070 mentioned in older project notes. The nvidia-smi CUDA value is driver capability, not proof of an installed CUDA compiler/toolkit.

### MuJoCo probe

System Python cannot import mujoco, but the package is installed and usable here:

    /home/ubuntu2004/lmy/dual-arm-force-control-mujoco-isaacsim/dual-arm-force-control-mujoco-isaacsim/.venv/bin/python

Probe: run scripts/task00_mujoco_smoke.py using the virtual-environment interpreter. It constructs one hinge/sphere model from inline XML and calls mujoco.mj_step once. Result: Python 3.10.12, MuJoCo 3.13.0, data.time=0.002 s. The run metadata and output are in results/20260930_TASK00_mujoco_smoke.

## Dual-FR3 model and planning access

The legacy workspace is /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws. After sourcing /opt/ros/humble/setup.bash and that workspace's install/setup.bash, ROS resolves fr3_dual_side_suction_description.

Its dual_fr3_side_suction.urdf.xacro expands successfully to robot dual_fr3_side_suction with 47 links, 46 joints, two side_suction_tcp links and fourteen actuated FR3 arm joints. Its SRDF expands to groups left_arm, right_arm and dual_arm, with chain tips left_fr3_side_suction_tcp and right_fr3_side_suction_tcp. Both use the original legacy workspace and its local franka_description dependency; they have not been copied into this repository.

The live /joint_states sample contained left_fr3_joint1..7 and right_fr3_joint1..7. MoveIt exposed /compute_fk, /compute_ik and /get_planning_scene. Installed MoveIt RobotState headers expose getGlobalLinkTransform and getJacobian; the legacy Task26 controller uses RobotState FK. A numerical Jacobian call in this new repository has NOT yet been run. TASK02 must test FK/Jacobian values against the chosen frozen robot model.

Reproduce the model check without starting a simulator:

    source /opt/ros/humble/setup.bash
    source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash
    ros2 pkg prefix fr3_dual_side_suction_description
    ros2 run xacro xacro /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/urdf/dual_fr3_side_suction.urdf.xacro
    ros2 run xacro xacro /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/srdf/dual_fr3_side_suction.srdf.xacro

## Time-bounded legacy runtime interface snapshot

At the time of the first snapshot, the legacy Task27 bridge and MoveIt were running with ROS_LOCALHOST_ONLY=0. These commands were read-only:

    source /opt/ros/humble/setup.bash
    export ROS_LOCALHOST_ONLY=0
    ros2 node list
    ros2 topic list -t
    ros2 service list -t
    ros2 topic echo /joint_states --once --field name
    ros2 topic echo /task27/cube_poses --once --field header
    ros2 topic echo /task27/left/side_suction_tcp_pose --once --field header
    ros2 topic echo /task27/right/side_suction_tcp_pose --once --field header
    ros2 topic echo /task27/left/measured_joint_forces --once --field name
    ros2 topic echo /task27/left/rail_state --once --field data

Observed interfaces:

| Need | Legacy evidence | Assessment |
|---|---|---|
| Joint state | /joint_states; 14 named arm joints | Live sample observed |
| Left/right TCP pose | /task27/{left,right}/side_suction_tcp_pose, PoseStamped, frame_id=world | Live samples observed |
| Cube pose | /task27/cube_poses, PoseArray, frame_id=world | Publisher/header observed; PoseArray indexing contract needs adapter |
| FK | /compute_fk service and MoveIt RobotState FK use in legacy controller | Service observed; new-repo call not yet tested |
| Jacobian | MoveIt RobotState::getJacobian API present | API available; numerical runtime probe outstanding |
| Contact wrench | No WrenchStamped/contact-wrench topic observed; measured_joint_forces is JointState joint effort, not a contact wrench | NOT available through observed ROS interface |
| Carriage/entrance frame | Legacy USD prim /World/Task27/TruckBox and /task27/{left,right}/rail_state exist | No explicit carriage/entrance TF contract observed |
| Simulation clock | /clock exists | Time-base policy not established |

A sampled /clock value was about 1787 s, while nearby TCP/Cube PoseStamped headers used approximately 1790752970 s. This suggests mixed simulation/wall time domains; it does not by itself prove a runtime bug. Reproduce and define a single benchmark timestamp policy before calculating synchronized pose/force errors.

The live Isaac/ROS processes had exited before later parameter and topic queries, so use_sim_time values were not verified. Do not infer them from the earlier topic list.

## Gaps and next-task gates

1. TASK01 can draft the frozen geometry, physics, seeds and thresholds from one explicit benchmark scene, but the repository requires user review before marking benchmark_v1 FROZEN. The current spec is DRAFT.
2. TASK02 needs a platform-independent model/telemetry contract, numerical FK/Jacobian probe, cube identity/order contract, a contact-wrench measurement path and an explicit carriage/entrance frame. Legacy joint effort is not a substitute for contact wrench.
3. The MuJoCo environment is present but lives in another project; record or package the dependency before a reproducible P2/P3 run.
4. P1 GPU work must check its actual CUDA build requirements; nvcc is absent even though the driver supports CUDA 13.0.
5. A clean standalone launch/bridge test for this new repository has not been performed. The observed legacy process is useful reference evidence only.

TASK00 PASS means this audit is reproducible and its missing interfaces are identified; it does not certify any paper baseline or full-stack benchmark.
