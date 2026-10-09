# CODEX_START_HERE.md

## Mission
Build a traceable reproduction and benchmarking stack for five high-level dual-arm manipulation baselines, then use measured evidence to design our own method.

## Current research task
Dual FR3 tightly coordinated transport of one shared Cube followed by cooperative constrained insertion/pushing into a carriage-like space.

## Platforms
- **Final system benchmark:** Ubuntu 22.04 + ROS2 Humble + Isaac Sim + dual FR3.
- **Fast force/contact lab:** MuJoCo, mainly P2/P3.
- **Planning/math:** MoveIt2/OMPL/FCL and standalone kinematics/QP modules where appropriate.

## Five baselines
- P4: closed-chain constrained planning.
- P2: object pose + internal wrench control.
- P3: hybrid force/position insertion and recovery.
- P5: centralized QP coordination and collision constraints.
- P1: two-stage sampling MPC with null-space constraint handling.

## Dependency order
`Foundation → P4 → P2 → P3 → P5 → P1 → unified benchmark → baseline freeze → ours`.

## Current execution gate

Latest user decision (2026-10-09): **TASK01 foundation PASS CANDIDATE ACCEPTED**, not a frozen scientific Benchmark. The original batch1 two-Cube/HOME evidence and first negative run remain unchanged. Do not redevelop original grasp/regrasp/push or repeat foundation qualification.

Active work: **TASK02 minimal migration and unified interfaces**, branch `task02-minimal-foundation-interface`. Use accepted predecessor assets in place through thin adapters first, not a copy/rewrite. TASK02-A state/provenance passes; **TASK02-B/C = PASS CANDIDATE**, parent TASK02 IN_PROGRESS. C reuses Task14 initial-drift geometry/max/RMS, adds explicit tracking/insertion math and data-only wrench/distance with strict clocks/qualification; two independent mock adapters agree. Final72A/B/C tests PASS, no Isaac/ROS/MoveIt invocation, backend/control binding or scientific threshold freeze. Read [latest C POST-TASK REPORT](reports/TASK02_METRICS_MEASUREMENTS01.md), [metric semantics](common/metrics/README.md), [B scope](reports/TASK02_EXCHANGE_LOGGING01.md), STATUS and reuse map. Real post-step binding/attestation, execution RNG control and scoring decisions need separate bounded scope. Stop after C delivery: do not launch runtime, TASK02-D or TASK03 under this authorization. BENCHMARK remains DRAFT / NOT FROZEN.

### Historical qualification (completed; not an active work list)

TASK01 predecessor qualification ran on branch `task01-legacy-scene-foundation`.

TASK01 has been explicitly restarted. Do not continue the previous custom TASK01 harness line.

The original qualification scope was:
1. read the pinned predecessor dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a;
2. launch its mature Task26 scene using the original GUI → scene → Play → bridge lifecycle;
3. reduce Task26 to exactly one independent Cube (task26_r0_deep) using an existing mode or the smallest selector-only patch;
4. run the predecessor planning-only check and then one complete physical Cube flow;
5. decide whether that old scene is suitable as the Isaac foundation.

The current benchmark_v1.yaml is DRAFT and is not an input to this qualification beyond historical comparison.

Read docs/tasks/TASK01_BENCHMARK_FREEZE.md for the restarted scope.

## Scientific rule
“Runs successfully” is not equivalent to “paper reproduced”.

Equally important:
“An auxiliary probe is imperfect” is not equivalent to “the current scientific task is blocked”.

Use minimum sufficient evidence, attempt budgets, blocker ownership, and escalation rules. Never continue an engineering loop merely because another diagnostic refinement is technically possible.

## Reuse rule for TASK02+
Before implementing TASK02 or later, read `docs/POST_TASK01_REUSE_MAP.md` and complete the mandatory PRIOR-ASSET CHECK from `AGENTS.md`. Reuse validated engineering infrastructure from the predecessor project where appropriate; keep paper-specific algorithms new and traceable.
