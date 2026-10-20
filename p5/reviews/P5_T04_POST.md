# P5-T04 POST — Centralised QP IK, Eq.(17a–c) with Eq.(18)

**Status**: `PASS` — 20 checks (12 positive / 8 negative), 0 failed, 1.9 s.
**Run**: `p5/evidence/impl_checks/T04.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T04`)
**Code**: `p5/impl/p5core/qp_ik.py` **[ORIGINAL]** maths / **[ADAPTATION]** backend · **Task**: `p5/impl/tasks/t04_qp_core.py`
**Figures**: `t04_tracking.png`, `t04_saturation.png`, `t04_solver_agreement.png`, `t04_timing_hist.png`

## 1. Three implementation findings that changed the plan

This is the foundation task for T05/T08/T10, so three defects surfaced here rather than later:

1. **`classify` needed a sixth state.** The five-state table in the plan assumed "equality consistent
   ∧ `θ̇⁻ ≤ θ̇⁺` ⇒ feasible". That is false: the affine set and the box can each be individually fine
   while their intersection is empty — routinely so at near-singular configurations. Without the new
   state `INFEASIBLE`, `classify` answers `OPTIMAL` and the caller receives a `pinv` point that
   violates Eq.(17c). That is precisely what the review forbade, so the state was added and N4.7 pins
   it (pinv violates the box by 61.5 rad/s at `σ_min = 1.4e-03`).
2. **Eq.(18) is infeasible by construction when a joint sits outside its position limit** by more
   than `q̇_max/μ`: then `θ̇⁻ > θ̇⁺`. The official `Construct_boundaries_vel()` never checks this.
   N4.2b records the behaviour (status, no silent clamp).
3. **The plan's N4.5 had the direction reversed.** With `μ → 0` both bounds collapse onto zero and the
   joint *freezes* — a stronger brake, not a removed one. Removing the look-ahead brake means `μ → ∞`.
   N4.5 now tests both directions so "frozen" cannot be mistaken for "unprotected".
   (Correction applied in `p5/P5_IMPLEMENTATION_PLAN.md` §4 and `docs/DECISIONS.md` D011.)

A fourth, smaller one: `PlanarArm.points()` mixed absolute link angles with a geometric Jacobian that
assumes relative joints. P4.1a caught it immediately (the Jacobian disagreed with its own finite
difference by 3e-1). The FK now accumulates the joint angles, which is the standard convention, and
`link_point_jacobian` was re-verified against finite differences at 1e-10.

## 2. Positive evidence

| Check | Content | Result |
|---|---|---|
| P4.1a | analytic Jacobian vs central difference | 3.8e-11 |
| P4.1b | `W=I`: analytic solution = `lstsq` minimum norm | 5.6e-17 |
| P4.1c | equality residual | 1e-16 |
| P4.2 | weighted objective minimal along the null-space line | min = f\* to 1e-12 |
| P4.3 | 3-link tracking, monotone, min `σ_min = 0.20` | 1.51e-01 → **8.39e-07** in 600 steps |
| P4.4a | binding brake: `q̇₂ = μ(q₂⁺ − q₂)` exactly, task preserved | 0.0 / 0.0 |
| P4.4b | 300 steps at the limit, no crossing | max `q₂` = 1.000000000000, final gap 2.2e-16 |
| P4.4c | discrete approach rate vs Euler prediction | 22.314 vs 22.314 rad/s (0.00 %) |
| P4.4d | arm driven into saturation | max`|q|` = 1.000000000, ends `INFEASIBLE` at step 29 |
| P4.5 | three solvers, active box | `|AS−SLSQP| = 1.7e-16`, `|AS−LVI| = 9.3e-11` |
| P4.6 | rank-deficient but consistent | `RANK_DEFICIENT_CONSISTENT`, residual 3.9e-16 |
| P4.7 | solve time | 3 DOF p50 **0.99 ms** / p99 1.27 ms; 4 DOF p50 **3.00 ms**; SLSQP 6.6 ms |

## 3. Negative / mutation evidence

| Check | Content | Result |
|---|---|---|
| N4.1 | inconsistent equality → no `qdot` | `EQUALITY_INFEASIBLE`; pinv residual 0.354 |
| N4.2 | contradictory bounds | `BOUND_INFEASIBLE` |
| N4.2b | joint outside its limit beyond `q̇_max/μ` | `BOUND_INFEASIBLE` (`θ̇⁻ = −0.5 > θ̇⁺ = −1.0`) |
| N4.3 | singular `W` | `ILL_CONDITIONED` |
| N4.4 | dimension mismatch | `ValueError` |
| N4.5 | `μ → ∞` removes the brake / `μ → 0` freezes | crossing 1.0e-03 / drift 0.0 |
| N4.6 | soft-task relaxation | equality residual 1.1e-02 → detectable, labelled `ADAPTATION`, never used for acceptance |
| N4.7 | near-singular slice, empty intersection | `INFEASIBLE`, no `qdot`; pinv violates the box by 61.5 |

## 4. Fidelity and limits

- **[ORIGINAL]** Eq.(17a–d), Eq.(18) and the KKT conditions.
- **[ADAPTATION]** the backend. CVXGEN's generated C is not in any official repository, so the
  implementation uses (a) an exact box-active-set enumeration — `3^d` KKT solves, the reference
  solver in P4.5/P4.7 — (b) `scipy.optimize.SLSQP`, (c) the LVI fixed point of T05. For a strictly
  convex QP the minimiser is unique, so the backend changes the numerical path, not the answer.
- Limit: **no real-time claim.** The paper's μs budget belongs to generated C code that is not
  reproduced here; Python absolute times are recorded, not compared. P4.7's threshold is an
  order-of-magnitude guard (20 ms / 60 ms), not a performance claim.
- Limit: the LVI *solver* is slow (7 414 projected iterations on the P4.5 fixture; ~1e5 when `W` is
  stiff, see `docs/DECISIONS.md` D010). It is therefore used as the dynamics/passivity object in T05
  and as a cross-check here, while the exact enumeration is the solver used downstream.
