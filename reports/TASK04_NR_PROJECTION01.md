# TASK04 — Offline Newton-Raphson projection POST-TASK REPORT

2026-10-09; repository `dual-arm-coordinated-manipulation-reproduction`;
branch `task03-p4-closure-constraint`; user baseline `91422f4`.

**TASK03 = PASS CANDIDATE (OFFLINE MATHEMATICS ONLY), accepted by user.**
**TASK04 = PASS CANDIDATE (OFFLINE PROJECTION MATHEMATICS ONLY).**
**TASK02 = IN_PROGRESS; BENCHMARK = DRAFT / NOT FROZEN.**
Stop for review. No TASK05/TASK06 or physical run.

## TASK03 review closure — not a precision relaxation

D047 records the approved scope classification. Real-model analytic/finite-difference
Jacobian verification is accepted as offline mathematics. Historical precision remains
**FAIL**: maximum position closure `0.435027826256 micrometres` exceeds unchanged
`0.05 micrometre`, with 219/293 records over the gate. Original rotation precision
passes at `1.2266396218402976e-5 rad <= 2e-5 rad`.
Source/tests/grasps/model/raw q/old results are unchanged. The unchanged TASK03
executable still records `task03_status=PARTIAL` in its new regression artifact;
review acceptance is separate. Projection, connection and RRTConnect were absent at
TASK03 delivery; TASK04 now supplies projection only, not full P4 reproduction.

## PRE-TASK REPORT

- Task/objective: P4 pseudoinverse NR projection reusing accepted C/Jc/FK.
- Minimum evidence: finite declared real-model neighbors converge, remain within
  native limits and repeat; explicit failures covered, original diagnostic separate.
- Scope: offline library/tests/logging/docs; no IK, FCL, simulator, ROS service,
  execution, TASK05/06 or Benchmark changes.
- Budget: one bounded implementation and finite deterministic experiments; no
  empirical tolerance change or alternate algorithm after failure.
- Preferred method: full Newton step / Eigen SVD / explicit guards.
- Fallback: preserve PARTIAL evidence and stop, not add damping/line search/clamp.
- Stop/escalation: bounded evidence fails or requires original-input/model/scope changes.
- Files: new projection module, standalone target/tests/runner/config and documentation.
- Validation: synthetic failure tests, 97x2 neighboring real-model cases, independent
  293 original-grasp diagnoses, unchanged TASK02/TASK03 regression and asset hashes.
- Risks: local convergence only; pi chart, singularity and rejected proposals; no
  physical/collision-free qualification. Need user confirmation: no, explicitly authorized.

## PRIOR-ASSET CHECK

Read governance/start/status/TASK04/P4/Benchmark/reuse map and accepted TASK03 code.
Pinned predecessor `631b1f65656d025c1bb2173e874192f3fe4d355a`: inspect
`shared_object_planner.hpp/.cpp` and related `fr3_dual_palletize`; no reusable NR
manifold/pseudoinverse projection found. Old planning does not reproduce the paper method.

- **DIRECT_PORT/REUSE:** unchanged TASK03 C/Jc, SE(3) and FR3 model adapter.
- **THIN_ADAPTER:** separate standalone target and existing TASK02 file logger/result/hash contracts.
- **TEST_ORACLE:** archived expanded URDF/SRDF, original 293 q/FK records and original grasp config.
- **REFERENCE_ONLY:** old object/TCP mapping and Task16 finite run/trial logging.
- Rejected: executor, Task26 runtime, old application gates, IK/path/physics modules.
- New paper algorithm: `q_next = q - Jc(q)^dagger C(q)`, not new kinematics/execution.
- Fidelity risks: low-rank rejection is qualification policy, not a paper theorem;
  algebraic test-only G* cannot replace original grasps. No user decision required.

## Predeclared engineering precision and method

D048/protocol was committed and pushed as **`15951f7` before projection experiments**.
Protocol SHA256 `23d5ea3a04ede0faaa9cbb6b64b2d5c1da3429fdde9f34663f2a501af4f6a1e2`.
The model test rejects any protocol-field difference; no post-result tuning.

- Position <= `1e-8 m`, rotation <= `1e-8 rad`, independently.
- Eigen JacobiSVD; cutoff `max(1e-12, 1e-10 sigma_max)`; values <= cutoff discarded.
- Needed correction with row rank < 6 returns `RANK_DEFICIENT`; already-closed
  zero-update states may succeed at lower rank. Singular corrections unqualified.
- Maximum 40 accepted full updates, final convergence check before budget failure.
- Exact native joint limits; finite/bounds/evaluation checked before acceptance.
- No damping/line search/step scaling/row weighting/clamp/IK retry.
- Unresolved step norm <= `1e-14 rad` or unrepresentable q change -> `STAGNATION`.
- Fixed SI m/rad; separate convergence is not unit-scale invariance.

[Formulas, frames, API and failure contract](../baselines/p4_closed_chain/PROJECTION.md).
**[ORIGINAL]** pseudoinverse update follows P4 II-B.2; IV-A describes SVD.
**[ADAPTATION]** accepted dual-FR3 closure/FK. **[ENGINEERING]** Eigen/guards/test protocol.
[Primary P4 paper](https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf).
The correction is minimum-norm for the current linearization, not globally closest
on the nonlinear manifold. No constraint-path/RRTConnect/full-paper claim.

## Bounded run history, including negatives

| Run | Scope reached | Outcome |
|---|---|---|
| projection01 | Configure only | Launcher overwrote sourced PYTHONPATH; logger used wrong predecessor root. ABORTED preserved, projection calls 0. |
| projection02 | Configure/generate only | Child-directory imported fastcdr target invisible to parent. FAILURE/PARTIAL preserved, projection calls 0. |
| projection03 | Build and all offline checks | PASS CANDIDATE; 487 real-model projection calls, no extra experiment rerun. |

Only dependency/runner corrections: retain sourced PYTHONPATH, use accepted legacy
root, load existing imported MoveIt dependencies in parent CMake scope. No mathematical
method/model/grasp/threshold/input changes. Known missing predecessor package setup
warning was not repaired. All negative artifacts retained, not described as math failures.

## Actual results

All eight build/test command exits 0. **72/72 TASK02 tests, 93 TASK03 math checks,
435 real-model derivative configurations, 108 TASK04 checks, CTest 2/2 PASS**.
Unchanged derivative maximum central `3.2806662941808895e-10` / five-point
`1.5442695733280942e-10`, versus original `2e-7` gate.

### Required neighborhood — real FR3 model, algebraic fixture, not physical grasp

At archived q0, construct `G*_i = F_i(q0)^-1 O0` once and keep fixed. 97 cases:
zero + 14 joints x 2 signs x 3 magnitudes + 4 coupled directions x 3 magnitudes.
Magnitudes 0.001/0.01/0.03 rad; two repeats, no RNG or IK.

| Measurement | Actual result |
|---|---|
| Converged | 194/194 |
| Maximum final position residual | 3.6972737725634625e-9 m |
| Maximum final rotation residual | 9.130545164669255e-9 rad |
| Accepted updates | 2 zero-update cases, 144 two-update cases, 48 three-update cases |
| Minimum final native joint margin | 0.6348353653921195 rad |
| Repeat max-absolute q difference | 0 rad; status/update/evaluation counts also match |
| Maximum initial position/rotation residual | 0.021012799144335088 m / 0.03982793551053071 rad |
| Maximum q change norm/max element | 0.024391984814115465 / 0.01935097405972408 rad |
| Projection compute cost | total 6.707253 ms; mean 0.034573 ms; max 0.112740 ms |

### Original grasp/original q diagnosis

Original transforms are inverted for TCP-to-object convention, never refitted.
**293/293** converge in one update: maximum final position `2.522693079754995e-11 m`,
rotation `3.1769445399432167e-11 rad`. Maximum q correction norm `9.421368222543194e-6 rad`
/ element `4.3485778208340875e-6 rad`. Compute total 4.717277 ms, mean 0.016100 ms,
max 0.082114 ms. These are new mathematical q, not historical data replacement.
Original 219/293 precision FAIL / worst state196 remain FAIL. New q have no collision
or physical shared-hold qualification.

### Guards, provenance and qualification

- Synthetic coverage: minimum norm/sign/nullspace, independent convergence, final-step
  budget, SVD cutoff/rank/equality, initial/proposal limits, invalid/nonfinite/empty/pi
  inputs, callbacks/candidate exceptions, accepted-then-rejected history, stagnation,
  overflow and invalid options. Rejected proposals never replace final accepted q.
- Full trace stores initial/final q/C, q change, spectrum/cutoff/rank, margins,
  proposed/accepted updates, reason/count and compute time.
- **477 protected tracked files unchanged; old accepted Task26 assets 4/4 unchanged.**
  Scope diff against `91422f4` confirms original TASK03 source/tests/fixtures/TASK02/
  Isaac adapters/Benchmark unmodified; old logs/raw data untouched.
- Benchmark YAML SHA256 unchanged:
  `fbef560ae81963fdf5839cd83d95274edebd9769024d1ae74527f00092c8f2a2`.
- Exactly 194+293=487 real-model calls; IK/FCL/execution **0**; original grasp refits
  **0**; simulator/service/controller starts **0**.
- Result SUCCESS is scoped offline acceptance, measurement UNQUALIFIED. Seed UNSET;
  simulation stamp/physics step null. Steady-clock cost excludes model load/serialization/
  whole test cost; it is not physical execution time or planner performance evidence.
- Metadata records invocation commit `15951f7` and source hashes of then-uncommitted
  implementation; final delivery commit is not retroactively called the run commit.

## Evidence and reproduction

[Summary and immutable hashes](../results/20261009_TASK04_projection03/summary.json),
[complete per-trial metrics](../results/20261009_TASK04_projection03/projection_metrics.json),
[typed result](../results/20261009_TASK04_projection03/result.json).
Negatives: [projection01 termination](../results/20261009_TASK04_projection01/termination.json),
[projection02 summary](../results/20261009_TASK04_projection02/summary.json).

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/install/setup.bash
PYTHONPATH="${PWD}:${PYTHONPATH}" /usr/bin/python3 scripts/run_task04_offline.py \
  --run-id YYYYMMDD_TASK04_projection_new
```

New run ID required; no current evidence rerun needed for review.

## POST-TASK REPORT

- Changed: new pure projection library, standalone reuse target/tests/runner/docs;
  TASK03 review classification persisted separately from historical precision.
- Verified: predeclared 97x2 suite, independent 293 diagnostics, all offline regressions,
  complete traces and immutable hash guards. Local finite cases satisfy declared precision.
- Not established: global convergence, singular manifold coverage, closest nonlinear q,
  collision freedom, physical/suction stability, connector/RRTConnect/full P4.
- Known limitations: original precision gap stays historical FAIL; low-rank correction
  unqualified; TASK02-D native time/reset qualification remains DEFERRED.
- State: **TASK04 PASS CANDIDATE; TASK02 IN_PROGRESS; Benchmark DRAFT / NOT FROZEN**.
- Stop: GitHub submission, wait for user review. Do not automatically start TASK05/TASK06.
