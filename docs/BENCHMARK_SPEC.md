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
Task27's first four cubes form a standard four-cube fixture. Cube 05 starts at its accurately aligned PRE_PUSH pose between the two inner cubes. Do not aggregate the first-four dual-arm and fifth-cube single-arm success rates into one "dual-arm insertion" result.

### B-fixture — Cubes 01–04
For each cube, the nominal PRE_PUSH position is a safe staging pose, **not** a requirement to achieve final lateral precision before pushing. A primary arm suctions the `-X` face and pushes toward the deep wall while a second arm suctions a side face to constrain lateral/yaw drift. After deep-wall contact, the side arm becomes the lateral pressing arm; the original pusher maintains deep-wall contact. For outer cubes the lateral contact target is a Y wall; for inner cubes it is the previously seated outer cube. Force and pose limits remain to be frozen.

### B-center — Cube 05
Precisely align Cube 05 at PRE_PUSH before insertion, then one arm alone suctions its `-X` face and pushes in `+X`. The other arm must clear the insertion corridor and make no Cube contact. Which arm pushes and the pre-push pose tolerances remain open. This is a **single-arm center-insertion subcase** within a dual-arm cell, not evidence that a two-arm insertion controller was reproduced.

The nominal center clearance is 1.5 mm per side. For an axis-aligned 120-mm Cube with lateral offset `dy` and yaw `theta`, a necessary geometric clearance condition is approximately `|dy| + 0.060*(|cos(theta)| + |sin(theta)| - 1) < 0.0015` m, before collision/physics margin. At 1° yaw, rotation alone consumes about 1.038 mm of that budget. This is analytic only; it is not a frozen success threshold.

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
The C0 start must meet the eventual alignment gate; C1–C5 are controlled perturbations of that gate, not uncontrolled staging errors.

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
7. Report dual-arm fixture manipulation and single-arm center insertion separately. A method that requires two-arm insertion must receive a separately specified comparable two-arm case; Cube 05 alone cannot support a claim of dual-arm insertion performance.
