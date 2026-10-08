# TASK01 — Core Single-Cube Benchmark Freeze

Status: IN_PROGRESS — re-scoped 2026-10-06

### Current gate: FULL_GEOMETRY_PASS / RENDER_GUARD_STOP; 07 NOT_RUN (2026-10-08)

06 (`0a78485` /`923aca…`) GUI14.25s, START accepted0: render-only gate still observed2 callbacks of0.01666666753590107s. Pre-render27 native comparisons max0m/6.165552397244359e-7rad and mirror stale0 are saved, but render_guard rejected before moving queries/collision. Fifty pure testsOK/0.079s and wrapper0 are not parityPASS. SDK_warm_start/direct update_simulation and second_create_simulation_view can bypass render gate; event count is consistent, not a uniquely captured causal trace.

07 only prepares original force_load/start_simulation initialization without timeline PLAY/update/simulate/fetch or SDK callback patch/disable; preserve zero-step/q/native/geometry/query guards and original physics/model/ACM/benchmark. Source8887ad…freeze pending, GUI07 NOT_RUN; retain03–06, READY NOT_RUN until parity passes, BUG019 unadjudicated, BUG001 non-blocking, TASK02 TODO. D035 ENGINEERING/no P4/DEVIATION or frozen claim.

#### Historical 05 checkpoint

### Current gate: FULL_GEOMETRY_PASS / UNINTENDED_PHYSICS_DISPATCH_STOP; 06 NOT_RUN (2026-10-08)

05 (`8188168` /`66dce1cd…`) visible GUI13.8s, START accepted0: paused app.update dispatched2 actual physics callbacks, Cube USD z0.38→0.3772749900817871m/vz=-0.16350001m/s. Integration observed despite not requested; no valid static parity/collision verdict or READY evidence. Saved27 pre-notice native comparisons (position max0m/rotation max6.165552397244359e-7rad) are not after-notice values; wrapper0 is not PASS. Preserve03/04/05.

06 only prepares official render-style temporary playSimulations=False/app.update/finally original-bool restoration, including force_load; require independent callback0/time/q/native checks. Separate SDK dynamic velocity/jointstate output from geometry hash while retaining mass/scale/mesh/limits/drive/material/scene/frames; no step0 weakening or dt/gravity/benchmark/geometry/ACM changes. Mock regression/source freeze pending, GUI06 NOT_RUN; D035 ENGINEERING/no P4/DEVIATION, READY NOT_RUN, BUG019 unadjudicated, BUG001 non-blocking. `8188168` direct push confirmed.

#### Historical 04 checkpoint

### Current gate: FULL_GEOMETRY_PASS / USD_ATTRIBUTE_PRECISION_STOP; 05 NOT_RUN (2026-10-08)

04 commit `a672224`, source `3bf86b380723b317b2eb4b32f3020a3736a16126887648bbc8a80c0bc3da8753`: visible GUI stopped at START/index0, accepted0, because original SDK Cube orient requires GfQuatf but adapter supplied GfQuatd. Actual Fabric disabled/updateToUsd=true; native success values not saved; wrapper0 is not PASS. No collision verdict, geometric failure, or BUG019 reproduction/resolution. Preserve03/04 negative evidence separately.

05 only prepares existing-attribute precision adaptation and distinguishes SDK-materialized body pose output from immutable geometry scale. Helper still rejects added/reordered/illegal ops; whole-scene physics/materials, ancestors and tool-TCP inventory enter the geometry fingerprint, while original scale/local shape/limits/settings/q/native/step0 checks remain. Final/screenshot step0 guards added. Main actually reran35 pure USD/query tests: exit0/0.093s; source frozen, GUI05 **not run**. Original benchmark/geometry/ACM unchanged; READY NOT_RUN, BUG019 OPEN/NOT_ESTABLISHED, BUG001 deferred TASK10-IS non-blocking, TASK02/P4 TODO. D035 remains ENGINEERING, no paper DEVIATION/PASS CANDIDATE/FROZEN claim.

#### Historical 03 checkpoint

### Current ordered gate: FULL_GEOMETRY_PASS / STATIC_OUTPUT_GUARD_STOP (2026-10-08)

03 visible single-Cube replay stopped at START/state0 with `ENGINEERING_STALE_USD_QUERY_SOURCE_STOP`, accepted parity states=0. The original left_link1 collider USD rotation remained old despite recorded q/Cube/TCP/live-FK checks. Native actor success values were not saved; only non-rejection by control flow is known and must not be reconstructed as measurements. Wrapper exit0 is not PASS. No actual new-chain collision verdict or BUG019 reproduction/resolution was established; pure geometry A136/B157 remains valid.

04 is prepared, **not run**: first use the existing official scene/Fabric output path; if still stale, mirror verified native SE3 only through original body existing translate/orient, without adding/reordering ops or changing local collider transforms/scale, geometry, physics/settings, shared-grasp, SRDF/ACM, or IK acceptance. After paused notices, re-check q/native/original geometry/settings/step0 and retain full cooked-shape and moving-query guards (D035, ENGINEERING only; no P4/DEVIATION). READY/reset NOT_RUN; BUG019 OPEN, BUG001 deferred TASK10-IS non-blocking; TASK02 TODO. No TASK01 PASS CANDIDATE/FROZEN claim. Three reports and [03 evidence](../../results/20261008_TASK01_isaac_model_parity03/metadata.json) distinguish each gate.

#### Historical full-geometry / GUI initialization checkpoint

### Current ordered gate: FULL_GEOMETRY_PASS / ISAAC_PARITY_PENDING (2026-10-07)

Actual full-chain native exit0: A136/B157,293 records292 distinct states, exact PRE14q seam, every-state signed FCL distance/pair recorded. START/PRE14q is captured in candidate YAML, not FROZEN. Visible GUI model parity is initializing; repeated READY/reset has not run. See reports/TASK01_FULL_SINGLE_CUBE_GEOMETRY.md, TASK01_ISAAC_MODEL_PARITY.md and TASK01_READY_RESET.md. BUG001 belongs to TASK10-IS, non-blocking; TASK02 remains TODO.

#### Historical PRE checkpoint (before full-chain execution)

User confirmed the new scientific START=(0.550,0,0.380), identity orientation, already shared-grasped and off-table; not Task27 feed. Probe LMA epsilon1e-7 and independent limits unchanged. First run dense START→PRE_PUSH with every-state full FCL signed distance/pair; failure stops without geometry edits. Only then stitch by exact PRE14q into B, capture START14q candidate, perform visible single-Cube static original-model parity, then repeated READY/reset. No force calibration or frozen claim; BUG001 belongs to TASK10-IS. Previous entries below are historical and remain intact.

### Latest execution gate: PARTIAL_PENDING_START_AND_ISAAC_REVIEW (2026-10-07)

User approved continuing geometry-preserving diagnosis. Same-seed precision A/B identifies both prior IK candidates as SUCCESS/bounds-valid but rotation-residual rejected. Local epsilon1e-7 resolves that step without changing acceptance1e-5m/1e-4rad or geometry/weight. PRE_PUSH→TARGET now passes157 ≤2mm discrete IK/bounds/full robot FCL states; separate nominal Cube/table/three-wall audit has628 checks/zero volumetric overlaps. Not continuous collision or physics proof. START→PRE_PUSH remains undefined; BUG019 mesh mismatch/Isaac READY-reset/user freeze review remain pending. No Isaac started or robot/suction command; TASK02 stays TODO. See [new diagnosis report](../../reports/TASK01_SINGLE_CUBE_IK_DIAGNOSIS.md). Do not mark TASK01 PASS/FROZEN.

### Historical execution gate: BLOCKED / stop for review (2026-10-06)

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
