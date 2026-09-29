# P1 — Two-Stage Sampling MPC

Paper: *Real-Time Dual-Arm Cooperative Manipulation Under Multiple Constraints: A Two-Stage Sampling MPC Approach* (IEEE T-RO, 2026).

## Problem
Real-time reactive dual-arm coordination under high-dimensional nonconvex constraints.

## Core method
- cooperative dual task-space with relative/absolute pose variables;
- sampling-based MPC;
- first-stage high-variance exploration;
- k-means mode clustering/selection;
- second-stage lower-variance refinement;
- equality constraints enforced through null-space projection;
- inequality constraints handled by sampling rejection/clamping/cost shaping;
- auxiliary controller near steady state;
- GPU acceleration.

## Reproduction target
1. Reproduce upstream example at pinned commit.
2. Port/adapt to dual FR3.
3. Enforce shared-object relative-pose constraint.
4. Reproduce two-stage exploration/refinement.
5. Evaluate collision handling and real-time compute.
6. Integrate with Isaac Benchmark A.

## Fidelity warning
Do not call a generic MPPI controller “P1 reproduction” unless two-stage mode handling and equality-constraint treatment are implemented and documented.
