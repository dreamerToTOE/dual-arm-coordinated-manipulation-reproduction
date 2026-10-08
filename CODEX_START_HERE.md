# CODEX_START_HERE.md

## Mission
Build a traceable reproduction and benchmarking stack for five high-level dual-arm manipulation baselines, then use measured evidence to design our own method.

## Current research task
Dual FR3 tightly coordinated transport of one shared Cube followed by cooperative constrained insertion/pushing into a carriage-like space.

## Platforms
- **Final system benchmark:** Ubuntu 22.04 + ROS2 Humble + Isaac Sim + dual FR3.
- **Fast force/contact lab:** MuJoCo, mainly P2/P3.
- **Planning/math:** MoveIt2/OMPL/FCL and standalone kinematics/QP modules where appropriate.

## Five baselines
- P4: closed-chain constrained planning.
- P2: object pose + internal wrench control.
- P3: hybrid force/position insertion and recovery.
- P5: centralized QP coordination and collision constraints.
- P1: two-stage sampling MPC with null-space constraint handling.

## Dependency order
`Foundation → P4 → P2 → P3 → P5 → P1 → unified benchmark → baseline freeze → ours`.

## Current execution gate
Current active work is **TASK01 — Core Single-Cube Benchmark Freeze** on the task branch.

TASK01's scientific purpose is to establish a minimal, stable, reproducible one-Cube environment. It is **not** a mandate to perfect every Isaac/PhysX diagnostic mechanism.

Before every task/iteration, read:
1. `AGENTS.md`
2. `docs/EXECUTION_GOVERNANCE.md`
3. `docs/STATUS.md`
4. current task spec
5. benchmark spec / relevant paper card

## Scientific rule
“Runs successfully” is not equivalent to “paper reproduced”.

Equally important:
“An auxiliary probe is imperfect” is not equivalent to “the current scientific task is blocked”.

Use minimum sufficient evidence, attempt budgets, blocker ownership, and escalation rules. Never continue an engineering loop merely because another diagnostic refinement is technically possible.
