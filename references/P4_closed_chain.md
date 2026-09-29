# P4 — Closed-Chain Motion Planning

Paper: *Motion Planning of Fully Actuated Closed Kinematic Chains With Revolute Joints: A Comparative Analysis* (IEEE RA-L, 2018).

## Problem
Sampling-based planning when valid configurations lie on a closed-chain constraint manifold.

## Reproduction target
- define dual-FR3 shared-object closure residual C(q);
- compute/approximate constraint Jacobian;
- Newton-Raphson/pseudoinverse projection to the constraint manifold;
- constrained local connection with projection at intermediate states;
- integrate with RRT/RRTConnect and collision checks.

## Key measurements
- projection success rate;
- projection iterations/time;
- final closure residual;
- planning success rate/time;
- path length/smoothness;
- collision safety.

## Scope
Reproduce the general projection-based planner path first. Other planning variants from the comparative paper may be added only if needed for a fairer baseline.
