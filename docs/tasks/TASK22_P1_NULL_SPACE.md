# TASK22 — P1 Equality Constraint / Null Space

Status: TODO

## Goal
Enforce shared-object relative-pose equality during sampled rollout propagation.

## Codex actions
- Construct equality-constraint Jacobian.
- Implement N = I - Jc^† Jc (or paper-exact variant).
- Apply projection at each rollout step.
- Measure residual drift across horizon.

## PASS
Rollouts remain within frozen closure tolerance with documented numerical behavior.
