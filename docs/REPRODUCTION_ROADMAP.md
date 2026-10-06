# Reproduction Roadmap — revised 2026-10-06

## Core principle
The scientific benchmark is **one shared Cube + dual FR3 + one carriage**.
The legacy five-Cube Task27 flow remains an application/stress-test asset and does not block paper reproduction.

## Phase 0 — Foundation
- **TASK00 Environment Audit — PASS**
- **TASK01 Core Single-Cube Benchmark Freeze — IN_PROGRESS**
  - geometry / frames / nominal material / time contract / start-goal states;
  - single-Cube geometric feasibility;
  - Isaac deterministic READY/reset;
  - **no force-controller calibration**.
- **TASK02 Common Interface / Logger / Metrics**
  - common state/command/result contracts;
  - same-post-step simulation timestamp;
  - collision-distance interface;
  - deterministic run metadata.

## Phase 1 — P4 Closed-chain Planning
- TASK03 Closure Constraint
- TASK04 Newton-Raphson Projection
- TASK05 Constrained Local Connection
- TASK06 Constrained RRTConnect

**Important:** P4 does not require calibrated contact wrench. Do not block this phase on P2/P3 sensing.

## Phase 2 — P2 Pose / Internal Force
### MuJoCo
- TASK07-MJ Grasp Matrix + Internal Wrench
- TASK08-MJ Object Pose Controller
- TASK09-MJ Pose + Internal Force

### Isaac
- **TASK10-IS Isaac Force/Wrench Interface Calibration + P2 Migration**
  1. establish explicit force/wrench source;
  2. frame/application-point transform;
  3. gravity/inertia compensation as required;
  4. calibration/sanity tests;
  5. migrate the already-working P2 controller to Isaac.

Force calibration is deliberately here, not in TASK01.

## Phase 3 — P3 Constrained Insertion
- TASK11-MJ Position-only Push
- TASK12-MJ Hybrid Force/Position
- TASK13-MJ Jam Detection
- TASK14-MJ Search / Align Recovery
- TASK15-IS Isaac Migration + Benchmark B

Only here freeze desired push force, force safety limits, jam thresholds and C1–C5 contact perturbation values.

## Phase 4 — P5 QP Coordination
- TASK16 QP IK Core
- TASK17 Joint Constraints
- TASK18 Collision Constraints
- TASK19 Isaac Real-time Execution

## Phase 5 — P1 Sampling MPC
- TASK20 Upstream Reproduction
- TASK21 Dual-FR3 Adapter
- TASK22 Equality Constraint / Null Space
- TASK23 Stage-1 Exploration
- TASK24 Stage-2 Refinement
- TASK25 GPU Benchmark
- TASK26 Isaac Integration

## Phase 6 — Scientific Evaluation
- TASK27 Unified Benchmark
- TASK28 Ablation
- TASK29 Failure Case Analysis
- TASK30 Baseline Freeze

## Phase 7 — Our Method
- TASK31 Ours v0 Design

No new method implementation before TASK30.
