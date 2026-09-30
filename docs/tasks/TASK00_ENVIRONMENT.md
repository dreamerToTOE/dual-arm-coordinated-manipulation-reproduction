# TASK00 — Environment Audit

Status: PASS (2026-09-30)

## Goal
Record the exact software/hardware/runtime environment before reproducing any paper.

## Codex actions
- Detect OS, kernel, GPU, NVIDIA driver, CUDA.
- Detect Python, compiler, CMake.
- Detect ROS2 distro, MoveIt2, OMPL, FCL.
- Detect Isaac Sim and MuJoCo versions if installed.
- Verify dual-FR3 model availability and joint naming.
- Verify access to joint state, FK/Jacobian, two TCP poses, cube pose, contact wrench and carriage frame where applicable.
- Record missing dependencies; do not install major components without approval.

## Outputs
- `reports/TASK00_ENVIRONMENT.md`
- update STATUS/WORKLOG/BUGS.

## PASS
Environment report is reproducible and identifies all blockers for TASK01/TASK02.

Evidence: reports/TASK00_ENVIRONMENT.md; results/20260930_TASK00_mujoco_smoke.
