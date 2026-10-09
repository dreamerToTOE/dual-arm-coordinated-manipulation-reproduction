# Reproduction Roadmap — revised 2026-10-08 (D039)

## Core principle
The scientific workflow is:

```text
Benchmark A:
dual-arm bilateral shared-object transport
START → PRE_PUSH

fixed engineering handoff:
release → right rear regrasp → INSERT_READY

Benchmark B:
single rear-pusher constrained insertion
INSERT_READY → TARGET
```

This matches the validated engineering topology in `dual-arm-embodied-palletizing@side-suction-palletizing` while keeping the scientific benchmark to one Cube.

Read `docs/PRIOR_PROJECT_REUSE.md` before rebuilding existing Isaac primitives.

## Phase 0 — Foundation
- **TASK00 Environment Audit — PASS**
- **TASK01 Predecessor Single-Cube Scene Foundation Qualification — IN_PROGRESS (RESTARTED)**
  - directly read and run predecessor Task26 at pinned commit 631b1f65656d025c1bb2173e874192f3fe4d355a;
  - reduce to one independent Cube only;
  - use original GUI → scene → Play → bridge → MoveIt → executor lifecycle;
  - run original planning-only preflight and one complete physical one-Cube flow;
  - if successful, mark predecessor Task26 single-Cube scene FOUNDATION_SCENE PASS CANDIDATE;
  - benchmark_v1 freeze is deferred until the foundation decision.
- **TASK02 Common Interface / Logger / Metrics**
  - common state/command/result contracts;
  - explicit phase label: A / HANDOFF / B;
  - same-post-step simulation timestamp;
  - collision-distance interface;
  - deterministic run metadata.

## Phase 1 — P4 Closed-chain Planning
- TASK03 Closure Constraint
- TASK04 Newton-Raphson Projection
- TASK05 Constrained Local Connection
- TASK06 Constrained RRTConnect

P4 evaluates Benchmark A. It does not require calibrated contact wrench and must not be blocked by Benchmark-B force sensing.

## Phase 2 — P2 Pose / Internal Force
### MuJoCo
- TASK07-MJ Grasp Matrix + Internal Wrench
- TASK08-MJ Object Pose Controller
- TASK09-MJ Pose + Internal Force

### Isaac
- **TASK10-IS Force/Wrench Calibration + P2 Migration**
  - validate explicit wrench source/frame/application point;
  - compensation as required;
  - migrate P2 to Benchmark A.

P2's dual-arm internal-wrench claims belong primarily to Benchmark A.

## Phase 3 — P3 Constrained Insertion
P3 begins from the frozen **INSERT_READY** state after the common fixed handoff.

- TASK11-MJ Position-only rear-push baseline
- TASK12-MJ Hybrid Force/Position rear-push
- TASK13-MJ Jam Detection
- TASK14-MJ Search / Align Recovery
- TASK15-IS Isaac Migration + Benchmark B

Only here freeze desired push force, force safety limits, jam thresholds and C1–C5 perturbation values.

## Phase 4 — P5 QP Coordination
- TASK16 QP IK Core
- TASK17 Joint Constraints
- TASK18 Collision Constraints
- TASK19 Isaac Real-time Execution

Primary common comparison target is Benchmark A unless a later explicit decision defines a cooperative-contact B variant.

## Phase 5 — P1 Sampling MPC
- TASK20 Upstream Reproduction
- TASK21 Dual-FR3 Adapter
- TASK22 Equality Constraint / Null Space
- TASK23 Stage-1 Exploration
- TASK24 Stage-2 Refinement
- TASK25 GPU Benchmark
- TASK26 Isaac Integration

Primary shared-object target is Benchmark A.

## Phase 6 — Scientific Evaluation
- TASK27 Unified Benchmark
- TASK28 Ablation
- TASK29 Failure Case Analysis
- TASK30 Baseline Freeze

## Phase 7 — Our Method
- TASK31 Ours v0 Design

No new method implementation before TASK30. Prior project code is an engineering reference, not a substitute for formal reproduction measurements.
