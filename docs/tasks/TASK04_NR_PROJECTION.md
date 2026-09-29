# TASK04 — P4 Newton-Raphson Projection

Status: TODO

## Goal
Project arbitrary nearby dual-arm configurations onto the closed-chain manifold.

## Core update
q_{k+1} = q_k - Jc(q_k)^† C(q_k), with damping/step control only if documented.

## Codex actions
- Implement projection with convergence/iteration limits.
- Respect joint limits.
- Record reasons for failure.
- Benchmark random perturbations at multiple magnitudes.

## Metrics
projection success, iterations, compute time, final residual.

## PASS
Meets frozen residual tolerance and produces repeatable statistics.
