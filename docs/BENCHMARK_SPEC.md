# Benchmark Specification — single-Cube scientific core

Status: **DRAFT until TASK01 user review; then FROZEN as benchmark_v1.**

## Scope boundary
The common SCI benchmark contains exactly:
- dual FR3;
- current fixed side-suction tools;
- one rigid Cube;
- one carriage;
- support/table geometry required by the task.

The historical five-Cube Task27 sequence is a **legacy application/stress test**, not the common baseline.

## Benchmark A — TIGHT_TRANSPORT
### Start
Both FR3 end-effectors already establish the frozen shared-object grasp on the one Cube.

### Goal
Move the Cube to the frozen PRE_PUSH pose while maintaining shared-object geometry and safety constraints.

### Primary metrics
- success rate;
- planning/control compute time;
- execution time;
- object pose RMSE;
- relative-grasp/TCP error;
- minimum collision distance;
- trajectory smoothness;
- internal wrench only for methods/tasks that expose a validated force interface.

### TASK01 requirement
Only geometric/start-goal reproducibility is required. Calibrated wrench is **not** a TASK01 gate.

## Benchmark B — CONSTRAINED_INSERTION
### Start
Same one Cube at PRE_PUSH.

### Goal
Insert/push the shared Cube along carriage +X to the frozen target.

### Nominal case
C0 has no intentional lateral/yaw perturbation.

### Robustness cases
C1–C5 values are finalized during P3 after the nominal geometry is frozen:
- small lateral;
- larger lateral;
- yaw;
- lateral + yaw;
- friction/contact perturbation.

### Primary metrics
- insertion success rate/time;
- contact force RMS/max after TASK10-IS calibration;
- left-right force difference/internal wrench when valid;
- lateral/orientation error;
- jam rate;
- recovery count.

## Time/measurement contract
Formal benchmark data use **one post-physics-step simulation timestamp**. Wall time may be logged for profiling but must not be mixed with synchronized scientific state.

Pose, TCP and later wrench records must carry explicit frame IDs; wrench also carries application point.

## Fair-comparison rules
1. Same one-Cube geometry, starts and goals across comparable methods.
2. Same success thresholds once frozen.
3. No method may change carriage/tool geometry to obtain a PASS.
4. Paper-specific force/control gains are method parameters, not benchmark geometry.
5. Omitted paper components are labeled Original/Adaptation/Deviation.
6. Final cross-method Isaac results remain the formal benchmark; MuJoCo is controller/unit evidence.
