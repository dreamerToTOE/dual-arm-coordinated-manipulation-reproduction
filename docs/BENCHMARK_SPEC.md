# Benchmark Specification

Status: **DRAFT until TASK01, then FROZEN as benchmark_v1.**

TASK01 candidate configuration: `configs/benchmark/benchmark_v1.yaml` (DRAFT). Its source-derived geometry is a starting point only; the null fields, contact topology, sensor contract, physics timing, perturbations and thresholds must be resolved and user-reviewed before any FROZEN claim.

## Benchmark A — TIGHT_TRANSPORT
### Start
Both FR3 end-effectors have already established the shared-object grasp/contact configuration.

### Goal
Move the cube to the common PRE_PUSH pose while satisfying coordination and safety constraints.

### Primary metrics
- success_rate
- compute_time_ms
- execution_time_s
- object_pose_rmse
- relative_pose_rmse
- minimum_collision_distance
- trajectory_smoothness
- internal_wrench_rms / max, when the controller exposes forces

### Fail conditions
To be fixed in TASK01:
- collision
- closed-chain/relative-pose violation
- joint-limit violation
- timeout
- object loss / grasp instability
- target tolerance violation

## Benchmark B — CONSTRAINED_INSERTION
### Start
Cube at PRE_PUSH.

### Stages
`PRE_CONTACT → CONTACT → PUSH → optional SEARCH/ALIGN → INSERT → DONE`.

### Standard cases
- C0 perfect alignment
- C1 small lateral error
- C2 larger lateral error
- C3 yaw error
- C4 lateral + yaw
- C5 friction/contact perturbation

Exact perturbations are frozen in TASK01.

### Primary metrics
- insertion_success_rate
- insertion_time_s
- contact_force_rms
- contact_force_max
- left_right_force_difference
- lateral_error
- orientation_error
- jam_rate
- recovery_count

## Fair-comparison rules
1. Same geometry, initial states, target and seed set across comparable methods.
2. Same success/failure thresholds.
3. Warm-up and compile time reported separately from steady-state compute time.
4. Method-specific tuning is allowed, but tuning budget and parameter set must be recorded.
5. A paper component omitted in adaptation must be explicitly marked.
6. Formal comparison tables use Isaac benchmark results unless the table is explicitly labeled MuJoCo/unit-test.
