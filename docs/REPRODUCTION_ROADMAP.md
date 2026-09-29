# Reproduction Roadmap

## Phase 0 — Foundation
- TASK00 Environment Audit
- TASK01 Benchmark Freeze
- TASK02 Common Interface / Logger / Metrics

## Phase 1 — P4 Closed-chain Planning
- TASK03 closure residual/Jacobian definition
- TASK04 Newton-Raphson projection
- TASK05 constrained local connection
- TASK06 constrained RRTConnect + Benchmark A planning baseline

Acceptance emphasis: constraint residual, projection success/time, planning success/time, collision safety.

## Phase 2 — P2 Pose/Force
### MuJoCo
- TASK07-MJ grasp matrix and internal wrench decomposition
- TASK08-MJ object pose controller
- TASK09-MJ pose + internal force controller
### Isaac
- TASK10-IS migrate same controller through adapter

First adaptation uses simulator object pose/contact information instead of reproducing the full visual-tactile IESEKF. This must remain marked [DEVIATION/ADAPTATION] until an estimator is added.

## Phase 3 — P3 Insertion
### MuJoCo
- TASK11-MJ position-only pushing baseline
- TASK12-MJ hybrid force/position control
- TASK13-MJ jam detector
- TASK14-MJ search/align recovery
### Isaac
- TASK15-IS migration and Benchmark B

Do not reproduce dexterous-hand-specific mechanisms unless they are needed for the arm-level insertion comparison.

## Phase 4 — P5 QP Coordination
- TASK16 centralized QP IK
- TASK17 joint constraints
- TASK18 collision constraints
- TASK19 real-time Isaac execution

Core version may use FCL distance constraints. Learned SCA boundary is a second-level fidelity target and must not be silently conflated with the core reproduction.

## Phase 5 — P1 Two-stage Sampling MPC
- TASK20 reproduce pinned upstream example
- TASK21 dual-FR3 adapter
- TASK22 equality constraint/null-space propagation
- TASK23 first-stage exploration + mode discovery
- TASK24 second-stage local refinement
- TASK25 GPU performance benchmark
- TASK26 Isaac integration

## Phase 6 — Scientific evaluation
- TASK27 unified benchmark
- TASK28 ablations
- TASK29 failure-case analysis
- TASK30 baseline freeze

## Phase 7 — Our method
- TASK31 evidence-based method v0 design

No new method implementation before TASK30.
