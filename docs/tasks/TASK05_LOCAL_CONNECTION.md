# TASK05 — P4 Constrained Local Connection

Status: TODO

## Goal
Connect two valid closed-chain states without leaving the constraint manifold.

## Codex actions
For interpolated intermediate states:
1. interpolate joint state;
2. project to manifold;
3. enforce joint limits;
4. collision-check;
5. verify closure residual.

Reject edge on any failed intermediate state.

## PASS
Unit tests include feasible connection, projection failure, joint-limit failure and collision failure.
