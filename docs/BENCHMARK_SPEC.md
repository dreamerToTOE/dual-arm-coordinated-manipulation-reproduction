# Benchmark Specification — staged single-Cube scientific core

Status: **DRAFT — formal Benchmark freeze requires a separate explicit user decision.**

2026-10-09: user accepts TASK01 foundation feasibility PASS CANDIDATE, but expressly
does not freeze the scientific Benchmark. Minimal migration/common interfaces may proceed;
this acceptance does not approve numerical parameters or scientific success thresholds below.

## Scope boundary
The common scientific benchmark contains:
- dual FR3;
- current fixed L-shaped side-suction tools;
- one rigid Cube;
- one carriage;
- support/table geometry required by the task;
- a fixed engineering handoff between shared transport and rear insertion.

The full historical five-Cube Task27 sequence is not the common baseline. Its validated **center-Cube primitives** are reusable engineering evidence; see `docs/PRIOR_PROJECT_REUSE.md`.

## Benchmark A — TIGHT_TRANSPORT

### Start
Both FR3 side Surface Grippers already hold the same Cube at the frozen START state.

### Goal
Move the Cube to PRE_PUSH_SHARED while maintaining shared-object geometry and collision safety.

### Scientific focus
Closed-chain/shared-object dual-arm planning and control.

### Primary metrics
- success rate;
- planning/control compute time;
- execution time;
- object pose RMSE;
- relative-grasp/TCP error;
- minimum collision distance;
- trajectory smoothness;
- internal wrench only for methods with a validated force interface.

TASK01 does not require calibrated wrench.

## Fixed engineering handoff — not a scored P3 algorithm

```text
PRE_PUSH_SHARED
→ release both side suctions
→ left helper parks outside insertion work zone
→ right arm regrips Cube -X face
→ right rear Surface Gripper CLOSED
→ INSERT_READY
```

This handoff is common to all Benchmark-B controller comparisons. It is logged for reproducibility but excluded from P3 controller metrics.

The implementation should preferentially reuse the already validated Task26/27 mechanisms and full-chain candidate screening.

## Benchmark B — CONSTRAINED_INSERTION

### Start
INSERT_READY:
- Cube at PRE_PUSH pose;
- right-arm rear (-X face) Surface Gripper active;
- left helper parked safely.

### Goal
Push along carriage +X to the frozen target `[1.100, 0.000, 0.260]`.

### Nominal case
C0 has no intentional lateral/yaw perturbation.

### Robustness cases
C1–C5 values are finalized in the P3 phase:
- small lateral;
- larger lateral;
- yaw;
- lateral + yaw;
- friction/contact perturbation.

Any new guide/fixture geometry required to make those perturbations scientifically meaningful must receive an explicit benchmark decision/version treatment; it may not be added silently.

### Primary metrics
Measured from INSERT_READY onward:
- insertion success rate/time;
- contact force RMS/max after TASK10-IS calibration;
- lateral/orientation error;
- jam rate;
- recovery count.

The former metric “left-right insertion force difference” is not a default Benchmark-B metric because nominal B is now a single rear-pusher topology. Dual-arm/internal-wrench metrics belong to Benchmark A or a separately declared cooperative-contact experiment.

## Relationship to prior project
The predecessor project already demonstrated:
- bilateral side-suction transport;
- dual Surface Gripper attachment to one object;
- release/regrasp transition;
- single-arm segmented +X insertion to x≈1.100;
- deep-wall gap checks and safe retreat.

Those are engineering feasibility assets, not paper-reproduction results. Formal cross-method measurements are rerun under this repository's frozen benchmark/logging contract.

## Time/measurement contract
Formal data use one post-physics-step simulation timestamp. Wall time may be logged for profiling but must not be mixed with synchronized scientific state.

Pose, TCP and later wrench records carry explicit frame IDs; wrench also carries application point.

## Fair-comparison rules
1. Same frozen A START/PRE_PUSH and B INSERT_READY/TARGET across comparable methods.
2. Same success thresholds once frozen.
3. Same fixed handoff for all P3 variants; handoff is not part of controller scoring.
4. No method changes carriage/tool geometry to obtain a PASS.
5. Paper-specific control gains are method parameters, not benchmark geometry.
6. Omitted paper components are labeled Original/Adaptation/Deviation.
7. Final cross-method Isaac results are the formal benchmark; MuJoCo is controller/unit evidence.
