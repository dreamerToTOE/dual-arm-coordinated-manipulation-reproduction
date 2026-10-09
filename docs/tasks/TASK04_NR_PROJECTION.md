# TASK04 — P4 Newton-Raphson Projection

Status: PASS CANDIDATE — OFFLINE PROJECTION MATHEMATICS ONLY; awaiting review.

Bounded offline slice authorized at `91422f4`, protocol precommitted as `15951f7`.
Required 194/194 neighboring cases and independent 293/293 original-grasp diagnostic
projections converge under the unchanged declared protocol. Maximum required final
residual 3.6973e-9 m / 9.1305e-9 rad; at most 3 updates, identical repeat q.
72 TASK02 / 93 TASK03 / 108 TASK04 checks and 435 real-model derivative configurations
PASS. Original TASK03 historical precision FAIL is not overwritten. Complete evidence
and explicit limitations: [POST-TASK REPORT](../../reports/TASK04_NR_PROJECTION01.md).
No physical/collision/path/full-P4 claim; stop, no TASK05/TASK06.

TASK03 mathematical implementation PASS CANDIDATE underD047; original historical
precision FAIL unchanged. Benchmark DRAFT / NOT FROZEN. Same task03 branch.

## Goal
Project arbitrary nearby dual-arm configurations onto the closed-chain manifold.

## Core update
q_{k+1} = q_k - Jc(q_k)^† C(q_k), with damping/step control only if documented.

## Codex actions
- Implement projection with convergence/iteration limits.
- Respect joint limits.
- Record reasons for failure.
- Test finite deterministic perturbations at multiple declared magnitudes; no RNG.

## Metrics
projection success, iterations, compute time, final residual.

## Predeclared engineering protocol (before experiments)

SeeD048 and `configs/engineering/task04_projection_test_v1.json`: independent
position1e-8m/rotation1e-8rad, full-step undamped SVD, cutoffmax(1e-12,1e-10σmax),
max40acceptedupdates, originalnativejoint-bound rejection/no clamp, numerical
stagnation≤1e-14rad. Correction at rank<6 rejects with explicit reason; this is a
conservative engineering qualification policy, not the paper's general singular
projection behavior. No extra row weighting, fixedm/rad, not scale-invariance claim.

97neighborhoodcases (one zero,84single-joint,12coupled), two repeats; outputq repeat
maxdifference≤1e-12rad. Fixed algebraicG* constructed once from existing START FK,
then unchanged throughout. Independently project293originalq using originalG once.
New projectedq is a TASK04 artifact, never a replacement for historical TASK03 data.

## Minimum sufficient evidence / PASS CANDIDATE

- Existing C/Jc/FK reused unchanged; paper-method attribution explicit.
- Required97×2 neighboring real-model math cases converge under declared criteria,
  stay within original limits and repeat; failure paths covered with synthetic inputs.
- OriginalG historical diagnostics preserved separately, including any failures.
- Initial/final position+rotation residual, proposed/accepted updates, q delta,
  singular spectrum/cutoff/rank, iterations/failure and compute walltime recorded.
- No physical, collision-free/path/trajectory/full-P4 claim; no threshold adaptation.

If scoped evidence fails, report PARTIAL and stop, rather than relax configuration
or add a new method. One bounded offline implementation; no engineering extension
requiring geometry/benchmark/old control changes. No Isaac/ROS services/Observer/
Task26, TASK05 connector, TASK06 planner, damping fallback or model/Benchmark edits.
