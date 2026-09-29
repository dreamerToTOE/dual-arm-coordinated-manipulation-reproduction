# P5 — Unified Coordinated Multi-Arm Motion Planning

Paper: *A Unified Framework for Coordinated Multi-Arm Motion Planning* (IJRR, 2018).

## Core method
- synchronous/asynchronous multi-arm task-space coordination;
- centralized inverse kinematics formulated as convex QP;
- joint-space self-collision avoidance;
- paper includes a learned/data-driven SCA boundary representation.

## Reproduction stages
### Core
- centralized dual-arm QP IK;
- joint position/velocity constraints;
- relative/synchronization tasks;
- collision-distance constraints using available FCL geometry.

### Paper-like extension
- reproduce learned SCA boundary only after the core QP baseline is stable and only if needed for scientific comparison.

## Fidelity warning
A QP using FCL distance constraints is a useful core adaptation but not identical to the paper's learned SCA model. Label the difference explicitly.
