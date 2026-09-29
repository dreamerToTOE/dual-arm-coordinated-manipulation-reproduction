# TASK29 — Failure Case Analysis

Status: TODO

## Goal
Turn baseline failures into evidence for later method design.

## Codex actions
Classify failures:
- no feasible closed-chain path;
- projection divergence;
- collision/infeasible QP;
- internal-force growth;
- jam/misalignment;
- MPC local mode/jitter/deadline miss;
- simulator/contact instability.

For each class save representative run, metrics and causal evidence.

## PASS
Failure taxonomy is backed by logs/plots, not only subjective observations.
