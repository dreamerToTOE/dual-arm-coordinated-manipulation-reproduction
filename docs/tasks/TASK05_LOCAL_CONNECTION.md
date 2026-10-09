# TASK05 — P4 Constrained Local Connection

Status: IN_PROGRESS — user-authorized bounded offline slice from `5d41869`.

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

## Current authorized protocol (2026-10-09)

Read [PRE-TASK / reuse / protocol](../../reports/TASK05_PRE_TASK_PROTOCOL.md),
[connector contract](../../baselines/p4_closed_chain/LOCAL_CONNECTION.md) and D050.
RBS reuses original TASK03 C/Jc/FK and TASK04 NR-SVD. No endpoint repair, ACM edits,
new projection/FK/collision backend or TASK06. Real FCL scene/resource failure =>
PARTIAL, not synthetic replacement. Ten fixed real-model positive connections,
exact-bound/closure negatives and native FCL penetration-negative fixture are
predeclared. Full point/projection/continuity/collision evidence and ordered failed
prefix retained. Discrete PASS is not continuous collision or physics proof.
TASK02-D DEFERRED; TASK02 IN_PROGRESS; Benchmark DRAFT / NOT FROZEN.
Stop after delivery/review, do not automatically start TASK06.
