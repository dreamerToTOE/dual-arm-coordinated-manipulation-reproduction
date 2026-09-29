# TASK16 — P5 Centralized QP IK Core

Status: TODO

## Goal
Build a centralized dual-arm velocity-level QP baseline.

## Codex actions
- Decision variable: stacked dual-arm joint velocity.
- Encode task-space tracking/synchronization objective.
- Add regularization and solver diagnostics.
- Compare analytic/finite-difference Jacobians where needed.
- Start without collision constraints.

## PASS
QP converges deterministically on representative states and tracks the desired dual-arm task with recorded solve time.
