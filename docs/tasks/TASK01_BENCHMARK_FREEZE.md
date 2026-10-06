# TASK01 — Core Single-Cube Benchmark Freeze

Status: IN_PROGRESS — re-scoped 2026-10-06

### Current execution gate: BLOCKED / stop for review (2026-10-06)

Single-Cube endpoint probe passes PRE_PUSH/10/30/50/70/100% joint IK/bounds/full FCL. START remains undefined. An extra ≤2mm same-seed insertion check rejects its second state at0.641026% (1.987179mm forward), so no continuous geometric chain has passed. No collision pair is established for that rejected IK state. User stop-on-failure obeyed; no new Isaac READY/reset, tool/carriage/TCP/ACM edits, force controller or paper algorithm. See [geometry report](../../reports/TASK01_SINGLE_CUBE_GEOMETRY.md). Do not mark PASS/FROZEN or proceed until review.

## Why this task was re-scoped
The previous TASK01 inherited the legacy five-Cube Task27 application flow and gradually expanded into multi-Cube sequencing, retreat planning, fixture construction, contact-force metrology, GUI/headless behavior and force/wrench calibration. Those are valuable historical engineering results, but they are not all prerequisites for starting the scientific baselines.

The common SCI benchmark is therefore simplified to the actual research question:

```text
one shared Cube
+ dual FR3
+ fixed side-suction tools
+ one carriage
→ tight cooperative transport
→ PRE_PUSH
→ cooperative constrained insertion/pushing
```

The five-Cube Task27 flow is retained as a legacy application/stress test and must not block this task.

## Goal
Freeze the **minimum scientifically sufficient** common environment for all later baselines.

TASK01 freezes geometry, frames, nominal physical parameters, deterministic start/goal definitions and time policy. It does **not** implement or calibrate the later force-control algorithms.

## In scope
1. Dual-FR3 robot/base/rail geometry.
2. One Cube geometry and mass.
3. Fixed L-side-suction tool geometry.
4. Carriage geometry and explicit `carriage_entrance` frame.
5. Benchmark A start state and PRE_PUSH target.
6. Benchmark B PRE_PUSH start and insertion target.
7. Nominal effective contact material.
8. Physics step / controller period.
9. Single common simulation-time contract.
10. One-Cube geometry feasibility evidence.
11. Isaac reset/READY reproducibility.

## Explicitly out of scope
Do **not** spend TASK01 time on:
- five-Cube placement sequence reliability;
- Cube-to-Cube fixture building;
- batch-to-batch empty retreat;
- five-Cube neighbor gaps;
- final force-control gains;
- desired push force;
- internal-wrench thresholds;
- jam-force thresholds;
- contact-wrench estimator calibration;
- gravity/inertia compensation for TCP wrench;
- P2/P3/P5/P1 paper algorithms.

These are deferred to their owning tasks.

## Required experiment 1 — Single-Cube Geometry Feasibility Probe
No physics control and no suction actuation are required for this check.

Using the intended left/right shared-object contact transforms, sample the nominal shared Cube along:

```text
shared-grasp START
→ PRE_PUSH
→ 10% insertion
→ 30%
→ 50%
→ 70%
→ 100% insertion
```

At every sample verify:
- dual-arm IK exists;
- joint limits;
- full self/inter-arm/environment FCL;
- tool-carriage collision;
- shared-object relative grasp transform;
- joint-limit margin.

If this chain is geometrically infeasible, stop and report the blocking collision/configuration. Do not add force control to cure a geometric impossibility.

## Required experiment 2 — Core Isaac READY
Create or reuse a minimal scene containing:
- dual FR3;
- current fixed L tools;
- one Cube;
- carriage;
- table/support if required.

Reset to the frozen Benchmark-A start and Benchmark-B PRE_PUSH states and verify:
- same geometry each reset;
- deterministic state restore;
- no unintended initial collision;
- explicit frame transforms;
- one post-physics-step simulation timestamp policy.

No five-Cube execution is required.

## Material policy
TASK00/TASK01 measurement found the actually effective Cube friction to be approximately static=0.5, dynamic=0.5 in the inherited scene, while old source constants claimed 0.90/0.75 but were not bound as expected.

For benchmark_v1, use **0.5 / 0.5 as the nominal candidate** unless the user explicitly changes this decision. Later P3 robustness tests may vary friction as a perturbation. Do not rewrite historical 0.90/0.75 runs as 0.5 results.

## Force/wrench policy
TASK01 only specifies the future interface semantics:
- SI units;
- timestamped at the physics post-step;
- frame and application point explicit;
- joint effort must not be mislabeled as TCP/contact wrench.

Actual Isaac contact/TCP wrench calibration is deferred to **TASK10-IS before P2 Isaac benchmark execution** and must not block P4.

## Outputs
- simplified `configs/benchmark/benchmark_v1.yaml`;
- `reports/TASK01_CORE_BENCHMARK.md`;
- single-Cube geometry-feasibility artifacts;
- Isaac READY/reset evidence;
- updated STATUS / WORKLOG / DECISIONS / BUGS as applicable.

## PASS criteria
- [ ] Benchmark uses one Cube only.
- [ ] Base/tool/Cube/carriage geometry is explicit.
- [ ] `carriage_entrance`, shared-object, TCP and world frame conventions are explicit.
- [ ] Benchmark A start and PRE_PUSH target are reproducible.
- [ ] Benchmark B PRE_PUSH and insertion target are reproducible.
- [ ] Single-Cube geometry feasibility probe passes or a user-reviewed geometry change is made.
- [ ] Nominal material is explicit.
- [ ] Physics dt and simulation-time policy are explicit.
- [ ] Isaac reset/READY can be reproduced.
- [ ] No force-controller or paper algorithm was implemented.
- [ ] User reviews the candidate.

## FROZEN criteria
After PASS and explicit user approval, mark benchmark_v1 FROZEN. Any later geometry/time/material change requires a DECISIONS entry and benchmark version bump.
