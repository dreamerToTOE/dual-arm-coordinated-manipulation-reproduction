# CODEX_START_HERE.md

## Mission
Build a traceable reproduction and benchmarking stack for five high-level dual-arm manipulation baselines, then use the evidence to design our own method.

## Current research task
Dual FR3 tightly coordinated transport of a shared cube followed by cooperative pushing/insertion into a carriage-like constrained space.

## Platforms
- **Final system benchmark:** Ubuntu 22.04 + ROS 2 Humble + Isaac Sim + dual FR3.
- **Fast force/contact lab:** MuJoCo, only where useful for P2/P3.
- **Planning/math:** MoveIt2/OMPL/FCL and standalone kinematics/QP modules where possible.

## Five baselines
- P4: closed-chain constrained planning.
- P2: object pose + internal wrench control.
- P3: hybrid force/position insertion and recovery.
- P5: centralized QP coordination and collision constraints.
- P1: two-stage sampling MPC with null-space constraint handling.

## First principle
Do **not** start from P1 because it is newest. Build the dependency chain:
`Foundation → P4 → P2 → P3 → P5 → P1 → unified benchmark → freeze → ours`.

## Before every task
Read `AGENTS.md`, `docs/STATUS.md`, current task file, relevant paper card, and benchmark spec.

## Current expected first task
**TASK00 — Environment Audit.**
No reproduction algorithm should be implemented until TASK00 and TASK01 are complete.

## Scientific rule
“Runs successfully” is not equivalent to “paper reproduced”.
Always report original method, adaptation, deviation, and missing components.
