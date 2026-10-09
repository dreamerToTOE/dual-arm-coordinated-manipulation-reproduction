# TASK04 — Offline Newton-Raphson projection

This slice reuses TASK03 `evaluate()` and its unchanged real dual-FR3 FK/Jacobian
adapter. It does not create a new robot model, IK solver, collision backend or executor.

## Frames and constraint

Let `q = [qL, qR]` contain 14 joint angles in radians. `T^A_B` maps coordinates
from B to A. With world-to-TCP FK `F_i(q_i)` and fixed TCP-to-object grasp `G_i`,

\[
T_{O,i} = {}^W T_{TCP,i}(q_i)\,{}^{TCP,i}T_O = F_i(q_i)G_i.
\]

Reuse the existing six-vector constraint and its analytic derivative:

\[
C(q) = \begin{bmatrix}p_{O,L}-p_{O,R}\\
\operatorname{Log}(R_{O,R}^{T}R_{O,L})^\vee\end{bmatrix},\qquad
J_c(q)=\partial C/\partial q.
\]

Position is in world axes/metres; rotation is an SO(3) log in the right-predicted
object axes/radians. The original TASK03 quaternion-equivalence, lever-arm and
SO(3)-chart handling is unchanged. A pi-chart evaluation failure remains explicit.

## Update and convergence

\[
J_c=U\Sigma V^T,\quad
\Delta q=-V_{[:,0:6]}\Sigma^\dagger U^TC(q),\quad q'=q+\Delta q.
\]

`Eigen::JacobiSVD` uses full U/V. Singular values at or below
`max(absolute_cutoff, relative_cutoff * sigma_max)` are discarded. The declared
qualification policy rejects a needed correction if numerical row rank is below 6.
An already-closed input needs no correction and may succeed at lower rank.

Check position and rotation **separately**. Neither a mixed-unit norm nor a zero
update is by itself convergence. The units are fixed SI m/rad, with no row scaling;
the pseudoinverse step is not asserted to be invariant under a change of units.
Each update is the minimum-norm solution to the current linearized problem, not
a guarantee of the globally nearest point on the nonlinear manifold.

There is no damping, line search, step scaling, joint clamp, IK fallback or retry.
Reject nonfinite, native-out-of-bounds or unevaluable proposals before acceptance.
Never return a rejected proposal as the accepted final configuration. For invalid
initial input, the returned q is still that input; callers must inspect status.

Convergence is checked before the update-budget guard, including after the final
permitted update. The immutable engineering test protocol is
`configs/engineering/task04_projection_test_v1.json`, declared in D048 and committed
as `15951f7` before any projection experiment:

| Item | Engineering test value |
|---|---|
| Position convergence | 1e-8 m |
| Rotation convergence | 1e-8 rad |
| Maximum accepted updates | 40 |
| SVD cutoff | max(1e-12, 1e-10 sigma_max) |
| Unresolved numerical stagnation | step norm <= 1e-14 rad |
| Joint bounds | exact original native bounds; no relaxation/clamp |
| Repeat output q difference | max-absolute <= 1e-12 rad |

These are not formal Benchmark thresholds. No threshold is tuned after execution.

## Failure and evidence contract

Statuses: `CONVERGED`, `INVALID_OPTIONS`, `INVALID_INPUT`, `INITIAL_JOINT_LIMIT`,
`ITERATION_LIMIT`, `RANK_DEFICIENT`, `UPDATE_JOINT_LIMIT`, `NONFINITE_EVALUATION`,
`EVALUATION_ERROR`, `BOUNDS_ERROR`, `NONFINITE_UPDATE`, `STAGNATION`.

Record initial/final C and q, norm/max-absolute q change, accepted updates,
evaluations, reason, steady-clock compute cost, and every proposed/accepted update.
The trace includes singular spectrum, cutoff, numerical rank, joint margin,
proposal, acceptance and residual. Compute wall time is not simulation/execution
time. Simulation timestamp and physics step remain null.

## Bounded tests and fixture distinction

1. Synthetic linear/nonlinear unit tests exercise update and explicit failure
   contracts, including independent convergence, cutoff, limits and final-step budget.
2. At one archived real FR3 q0, construct `G*_i = F_i(q0)^-1 T_O0` **once**.
   This is an algebraically consistent math fixture, not a physical/suction calibration.
   Hold it fixed through zero + 84 signed single-joint + 12 coupled perturbations.
   Magnitudes are 0.001/0.01/0.03 rad; four coupled directions use the declared
   deterministic normalized sine formula. Repeat 97 cases twice: 194 calls.
3. Independently use the original archived grasp transforms and all original
   293 q records, once each. Store new projection outputs only in TASK04 artifacts.
   Preserve the original unprojected TASK03 0.05-micrometre FAIL; never substitute
   projected configurations, refit original grasps or overwrite old evidence.

Exactly 487 real-model projection calls, no random sampling or new IK. TASK02
A/B/C and original TASK03 math/derivative tests are also rerun unchanged.

## Paper fidelity and limitations

- **[ORIGINAL]** Newton pseudoinverse manifold projection follows P4 II-B.2;
  P4 IV-A describes an SVD implementation.
- **[ADAPTATION]** Dual-FR3 coordinates and SE(3) chart are the already-reviewed TASK03 mapping.
- **[ENGINEERING]** Eigen implementation, bounded logs, separate numerical tests,
  strict limits and full-row-rank qualification. Rejecting rank-deficient corrections
  is conservative, not a claim that P4 requires this or such points cannot be projected.
- No claim of physical holding, collision freedom, constraint-aware path connection,
  RRTConnect or full-paper reproduction. TASK05/TASK06 have not been implemented.

Primary source: [P4 original paper](https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf).

## Offline reproduction

From the reproduction repository root, load dependency paths (no services):

```bash
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/install/setup.bash
PYTHONPATH="${PWD}:${PYTHONPATH}" /usr/bin/python3 scripts/run_task04_offline.py \
  --run-id YYYYMMDD_TASK04_projection_new
```

Use a new run ID; existing evidence is never overwritten. The optional build path
stays under ignored `build/`. The runner stores build/test logs, source hashes,
protected-file/accepted-Task26 hashes, complete projection metrics and typed result.
Offline test SUCCESS is explicitly scoped and unqualified for physical measurement.
