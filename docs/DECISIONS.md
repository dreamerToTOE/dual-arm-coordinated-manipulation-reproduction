# DECISIONS

Append-only architectural and scientific decisions.

## D001 — Two-platform strategy
- Date: 2026-09-29
- Decision: Isaac Sim + ROS2 is the final common benchmark; MuJoCo is an auxiliary force/contact laboratory mainly for P2/P3.
- Reason: preserve fair final comparison while accelerating force/contact debugging.
- Impact: baseline algorithms remain platform-independent and use adapters.

## D002 — Baseline-first rule
- Date: 2026-09-29
- Decision: `ours/` remains algorithmically empty until TASK30.
- Reason: derive our method from reproducible evidence and failure cases rather than premature design.

## D003 — P3 task→hole frame relabelling is an explicit, unproven convention
- Date: 2026-10-20
- Context: Eq.(19)/Fig.5 push along task **z**; §IV-D excludes **x** with `Σ=diag([0 1 1])`. The paper
  never states the task-frame→hole-frame rotation.
- Decision: implement `R_h` literally (hole→reference) and apply an explicit
  `R_task_to_hole` (`e_z→e_x`) to the perturbation wrench; label it **[ADAPTATION: frame naming]**.
- Evidence: with the relabelling, `Ω(R_h)·R_h(R_task→hole e_z) = 0` (8.5e-17, T03_12). Under the
  literal reading the push axis is *not* excluded (`‖Ω(I)e_z‖ = 1`, T03_15). Both variants are valid
  projectors, so this changes physical meaning, not algebra.
- Status: **open source ambiguity** — do not present the chosen convention as paper-established.

## D004 — P3 stage switching is a prescribed script, not state estimation
- Date: 2026-10-20
- Context: the paper switches stages manually (p.8572) and gives no criterion.
- Decision: `stages.StageSchedule` takes externally supplied boundaries; no contact-driven state
  machine is implemented. Label **[ADAPTATION]**.
- Impact: stage *sequences* are validated; insertion success and automatic recognition are explicitly
  not claimed.

## D005 — Reporting convention for mixed-unit quantities
- Date: 2026-10-20 (post-delivery review R2/R3)
- Decision: never quote a norm over a vector that mixes newtons and newton-metres. Force and moment
  jumps are reported separately (`jump_force_N`, `jump_moment_Nm`); the concatenated norm survives
  only as `jump_mixed_l2_unphysical`. Maxima are labelled either `max_{t,k}|x_k|` (component) or
  `max_t‖x‖₂` (vector norm), never conflated.

## D006 — P5 Eq.(21b) sign: `+log(Γ−1)`
- Date: 2026-10-20 (G0, review Q3)
- Context: the paper prints `b = [0; −ξ̇^R; −log(Γ−1)]`, which contradicts its own (17d).
- Derivation: with `h(q̇) = −∇Γᵀq̇ − log(Γ−1) ≤ 0` and `ν ≥ 0`, the complementary row of the LCP is
  `∇Γᵀq̇ + b₃ = 0`; on the active set `∇Γᵀq̇ = −log(Γ−1)`, hence `b₃ = +log(Γ−1)`. The paper's own
  prose agrees ("the value of `log(Γ−1)` is positive which relaxes the inequality").
- Decision: primary implementation uses `+log(Γ−1)` with `λ = 1`. The printed `−log(Γ−1)` is kept as a
  separately labelled negative control. Any `λ ≠ 1` is described as a *modified* constraint.
- Impact: `T05`/`T08`/`T10`; see `P5_IMPLEMENTATION_PLAN.md` §11 row 4.

## D007 — P5 SCA calibration uses `κ ≡ 1` (identity), not a data statistic
- Date: 2026-10-20 (G0, review Q4)
- Context: the shipped CPSP models have `bias = 0`, so their decision boundary is `Γ_raw = 0`, whereas
  (17d) needs `log(Γ−1)`, i.e. `Γ > 1`.
- Key fact: the map `Γ_cal = 1 + Γ_raw/κ` satisfies `Γ_raw = 0 ⟺ Γ_cal = 1` for **every** `κ > 0`, and
  preserves ordering for every `κ > 0`. The boundary condition therefore places **no constraint** on `κ`.
- Decision: freeze `κ ≡ 1`. It is the unique choice that adds no scale and needs no data statistic, so it
  cannot be tuned toward a preferred outcome. Implementations must still support arbitrary `κ > 0` (a
  `κ = 2` scaling test verifies the `1/κ` factor of the gradient).
- Rejected: `κ = median|Γ_raw|` over near-boundary samples. It was justified by "median calibrated value
  equals 1", which is circular and was never required.
- Label: **[ADAPTATION]** — the paper never defines this map.

## D008 — P5 T07 metrics are in-sample independent evaluations, not the paper's FPR/TPR
- Date: 2026-10-20 (G0, review T07)
- Context: the 36-D model ships `X_train(24892×36)`, `y_train`, `y_est`; the paper's own held-out set and
  its data split are not published.
- Decision: label every metric `IN_SAMPLE_INDEPENDENT_EVALUATION`, report bootstrap 95% intervals, and do
  **not** compare against the paper's `FPR ≈ 1.45% / TPR ≈ 97.4%`, nor claim a "within 1 pp" acceptance.
- Positive use: `y_est` is a genuine external reference for the decision function — our implementation
  reproduces its sign on 100 % of the 24 892 points, which validates the kernel path end to end.

## D009 — P5 control-side energy bookkeeping, not `Σ½‖q̇‖²`
- Date: 2026-10-20 (G0, review T10)
- Decision: `Σ½‖q̇‖²` is not treated as physical energy or as a passivity measure. T10 reports
  `P_in = ξ̇^{Rᵀ} f` with `f = Wq̇` (**stated assumption**), a tracking-error storage `S = ½‖ξ̃‖²`, the
  Theorem-3 dissipation `ψ = uᵀ(I+Mᵀ)u`, and the residual of the numerical ledger `∫P_in − ΔS − ∫ψ`.
- Impact: the residual is an implementation-consistency indicator, never a physical claim.

## D010 — P5 uses the exact box-active-set solver downstream; LVI stays the dynamics object
- Date: 2026-10-20 (G1, T04)
- Context: solving `P_Ω(u − (Mu + b)) − u = 0` by the scaled projection iteration needs 7 414 steps on
  the T04 fixture and ~1.8e5 when `W` is stiff (`W = 20 I`), i.e. 60–1800 ms in pure Python. The KKT
  matrix of (21a) has a zero (2,2) block, so the map has directions with contraction factor ~1.
- Decision: the **exact** `3^d` box-active-set enumeration (`QP.solve_active_set`) is the solver used by
  T04/T08/T10 (p50 0.99 ms at 3 DOF, 3.00 ms at 4 DOF). The LVI formulation is kept for what the paper
  actually claims — the projected *dynamics* (20) and the passivity inequality of Theorem 3 (T05).
- Rationale: for a strictly convex QP the minimiser is unique, so using an exact solver changes the
  numerical path only. Pretending the slow fixed point is a real-time solver would be the dishonest option.
- Label: **[ADAPTATION]** (solver), **[ORIGINAL]** (dynamics and passivity identity).
- Consequence: the paper's μs real-time budget is explicitly *not* reproduced; Python times are reported
  as absolute numbers with an order-of-magnitude guard, never as a comparison.

## D011 — Eq.(18): `μ → 0` freezes the joint; the look-ahead brake is removed by `μ → ∞`
- Date: 2026-10-20 (G1, T04)
- Context: the plan's N4.5 asked for `μ = 0` as the "brake removed" control. With
  `θ̇⁻ = max(μ(q⁻−q), q̇⁻)` and `θ̇⁺ = min(μ(q⁺−q), q̇⁺)`, `μ = 0` gives `θ̇⁻ = 0` and `θ̇⁺ = 0`,
  so the joint is **frozen** — a stronger brake, and a degenerate control.
- Decision: N4.5 tests both directions. `μ → ∞` (pure velocity clamp) must produce a limit crossing;
  `μ → 0` must freeze. Reporting only one of them would leave "frozen" indistinguishable from "unprotected".
- Second finding, same equation: Eq.(18) is **infeasible by construction** when a joint sits outside its
  position limit by more than `q̇_max/μ`, because then `θ̇⁻ > θ̇⁺`. The official `Construct_boundaries_vel()`
  never checks it; the implementation classifies it as `BOUND_INFEASIBLE` (N4.2b) and never clamps silently.
- Label: **[ORIGINAL]** (equation), **[ENGINEERING]** (classification).

## D012 — PlanarArm uses relative joint angles
- Date: 2026-10-20 (G1, T04)
- Context: `points()` placed link `i` at angle `q_i` (absolute) while `jacobian()` used
  `dp/dq_i = z × (p − p_i)` for all downstream links, which is the *relative*-joint convention. P4.1a
  caught the mismatch at 3e-1.
- Decision: accumulate the angles (`angle_i = Σ_{j≤i} q_j`), i.e. the standard serial-chain convention.
  Link-point Jacobians were then re-verified against finite differences at 1e-10 for both arms of
  `DualPlanarArm`.
- Impact: the geometry changes for every downstream task (T08/T10). Any figure produced before this fix
  would have described a different arm, which is why the fix was made at G1 and not later.
- Label: **[ENGINEERING]**.

## D013 — The two published sigmas are numerically interchangeable; the pairing is a provenance rule
- Date: 2026-10-20 (G2, T07)
- Context: the sparse CPSP model carries `-g 3.3` (⇒ `σ = 1/√(2g) = 0.38925`) while the full libsvm
  model stores `σ = 0.38815`. N7.3 originally asserted that swapping them destroys the decision
  function. Measured: swapping them still reproduces `y_est` at **0.9992** (they differ by 0.28 %).
- Decision: the swap becomes a *reported metric* (`agree_sigma_swapped`), not a defect claim. N7.3
  injects the defect that is actually harmful — reading `-g` as the RBF width (`σ = 3.3`) — which
  drops the agreement to 0.5670. The code still refuses to cross-wire the two models, but the reason
  recorded is **provenance** (each model keeps the hyper-parameters it was shipped with), not accuracy.
- Alternative rejected: relaxing N7.3's threshold to `< 0.9993` would have produced a ledger that
  claims a sensitivity the model does not have.
- Label: **[ORIGINAL]** (parameters), **[ENGINEERING]** (test redesign).

## D014 — `(11) → (36)` is conditional on the shared-velocity premise, not an algebraic identity
- Date: 2026-10-20 (G2, T03)
- Context: the review (Q2) asked whether the paper's two-segment cancellation is an identity. T03
  separates the two segments: `U_i = τ_i ẋ_i^V` kills `τ̇` unconditionally (residual 1.2e-15, and
  `∂U_i/∂τ̇ ≡ 0` to 1.9e-16), but the collapse of the *aggregate* `(11)` onto `(36)` happens only under
  the paper's App. D premise `ẋ_i^V = ẋ^V` for all `i` (5.6e-17 under the premise; a ±50 % change in
  `τ` moves `x^V` by 5.0e-2 when per-arm offsets are present).
- Decision: T08 and T10 may implement `(36)` directly, but they must state that this presumes the
  synchronisation layer of Eq.(8) is working. The T10 end-to-end check therefore exercises the
  asynchronous→synchronous switch (where `τ` is *not* shared) rather than only the synchronous regime,
  so that a broken `τ` coupling cannot hide behind `(36)`.
- Label: **[ORIGINAL]** (equations), **[ENGINEERING]** (test design).

## D015 — In T08 the SCA feature must not be the task coordinate
- Date: 2026-10-20 (G3, T08)
- Context: the plan specified the SCA feature as the relative position of the two tips, and the
  natural task for that fixture is "move the relative position to a goal". With that pairing
  `Γ̇ = ∇_fΓ·ḟ` is **implied by the task equality row**, so (17d) can neither bind nor be satisfied by
  the redundant joints: the QP would either accept the task velocity or report infeasibility. The
  learned boundary would act as a switch, and P8.2 ("activation rate > 0") would be measuring nothing.
- Decision: the task drives **one** arm's tip (`d_n = 2`) while (17d) constrains the **pair**
  (`d_c = 1`) over both arms, leaving two joints of slack. Measured activation 50.1 %.
- Consequence: this is a fixture property, not a claim about the paper — the paper's task is the
  object pose and its constraints are over all body-point pairs, so its rows are never implied.
- Label: **[ENGINEERING]** (test design).

## D016 — Two structural limits of (17d) found in closed loop
- Date: 2026-10-20 (G3, T08)
- Context: two plan expectations were falsified by measurement.
- Decision 1 (`PAPER_FALLBACK`): with `Γ_raw < 1` the paper replaces `log(Γ−1)` by a large negative
  number. As a **hard** row with rhs = −1000 this demands `Γ̇ ≥ 1000`; the best achievable rate in the
  fixture is 28.2 s⁻¹, so the exact solver reports `INFEASIBLE` and the robot freezes. The fallback is
  therefore a *soft-formulation* device; it is implemented and labelled as such, and P8.6 reports the
  infeasibility instead of pretending the push happens.
- Decision 2 (`λ = 0`): `λ` scales `log(Γ−1)`, which is positive for `Γ > 2`. So `λ = 1` *grants* a
  decrease budget far from the boundary while `λ = 0` turns the row into the strict cone `Γ̇ ≥ 0`.
  λ = 0 is thus stricter, not looser, away from the wall; the plan's prediction is recorded as
  falsified rather than engineered into a crossing.
- Label: **[ORIGINAL]** (equations) / **[ENGINEERING]** (findings about their use).

## D017 — Theorem 3 is an identity *at each QP solution*, not a closed-loop ledger
- Date: 2026-10-20 (G4, T10)
- Context: the review correction #14 asked T10 to replace "`Σ ½‖q̇‖²` as energy" by a numerical
  energy ledger: control input power + tracking-error storage + the Theorem-3 dissipation `ψ` +
  residual. T10 records the Theorem-3 quantities of every step (`V = ½‖u‖²`,
  `ψ = uᵀ(I+Mᵀ)u`, `YᵀU = uᵀ(I+Mᵀ)P(u − Mu − b)`) and the measurement refuses the ledger:
  `∫YᵀU dt − ΔV − ∫ψ dt = −328.4` against `∫|YᵀU| dt = 328.7` (2152 %).
- Diagnosis (measured, not argued): at every step the active-set solution *is* the LVI fixed point, so
  `P(u − Mu − b) = u` and therefore `YᵀU = ψ` to `9.1e-13` (relative `3.7e-17`), i.e. `V̇ ≡ 0`
  instantaneously. What changes `V` is the **jump of `u` between two fixed points of different LVIs**,
  not a flow. The residual of the ledger is then exactly `−ΔV`: `residual + ΔV = 2.8e-14`.
- Decision: P10.5 gates the per-step identity (it is the (21a) assembly check); P10.6 gates the
  statement that the ledger's non-closure is *entirely* `−ΔV`, i.e. that no term is unmodelled. The
  telescoping ledger itself is reported as a metric and never used as a pass criterion, and the
  `P_in = ẋ^R·f`, `S = ½‖separation‖²` variant is reported without gating (its residual −328.4 is
  dominated by `S` not being a storage function at all).
- Consequence: a re-solved QP loop is a sequence of fixed points, not a trajectory of (20). Any future
  "`V̇ ≤ 0` in closed loop" claim is out of scope for this implementation; it would require integrating
  (20), which neither this code nor the official one does (the official code calls a QP solver per
  cycle and has `Gamma_/DGamma_` never updated).
- Label: **[ORIGINAL]** (equations) / **[ENGINEERING]** (accounting choice).

## D018 — The hard (17d) row is infeasible on 46 % of the end-to-end steps
- Date: 2026-10-20 (G4, T10)
- Context: the T10 run reports `370/800` `QP_INFEASIBLE` steps with the row on and `0` with it off.
  The attribution is unambiguous: the same QP without the row is `OPTIMAL` on all 370, and the
  reference velocity on those steps is `≤ 0.0279`, so the velocity box is not the cause. The cause is
  the D016 mechanism at a different operating point: `log(Γ_raw − 1)` shrinks as `Γ → 1`, so the row
  demands `Γ̇ ≥ −log(Γ−1)` while the hard equality `J q̇ = ẋ^R` has only a 2-dimensional null space in
  which to satisfy it. A hard row with no slack is therefore routinely unsatisfiable; the paper's
  formulation is only coherent in its soft form.
- Decision: the fallback is an explicit, labelled parameter with two documented modes instead of an
  implicit one — `row_policy="freeze"` (hold `q̇ = 0`, the only box-safe value when the solver returns
  nothing) and `row_policy="drop_row"` (re-solve without (17d)). **Neither is presented as the paper's
  controller.** Both are run and P10.7 reports them side by side: freeze gives `min Γ = 2.0700`, 0
  crossings; drop-row gives `min Γ = 1.2400`, 0 crossings (368 drops); row off gives `−2.3147`, 534
  crossings.
- Why this is not a dodge: the counterfactual was fixed *before* the number was known and it can come
  out either way. It came out as "the row carries the guarantee on the steps where it is feasible",
  which is a claim about the row; had it produced crossings, the e2e claim would have been downgraded
  to "the freeze, not the row, avoids the boundary" and reported that way.
- Consequence: the freeze makes `q̇ = 0` on 46 % of the steps, so **no timing, tracking-accuracy or
  smoothness claim is drawn from this run**; only the `Γ` criterion is. Activation 53.1 % is reported
  against the same 800 steps, not only the solvable ones.
- Label: **[ORIGINAL]** (equations) / **[ENGINEERING]** (fallback policy, fixture).

## D019 — Post-delivery audit: the closed-loop rhs contradicted D007 (barrier one unit above the boundary)
- Date: 2026-10-20 (post-G4 adversarial audit, after `8a64c38c` / `13f4bf8a`)
- Context: re-auditing G4 with fresh eyes found that both closed-loop tasks computed the (17d)
  right-hand side as `log(Γ_raw − 1)` with domain `Γ_raw > 1`, while D007 (review Q4) fixes
  `Γ_cal = 1 + Γ_raw/κ` with `κ ≡ 1`, i.e. rhs `= log(Γ_raw)` with domain `Γ_raw > 0`. The shipped
  models have `bias = 0`, so their decision boundary is `Γ_raw = 0`; `log(Γ_raw − 1)` silently placed
  the barrier at `Γ_raw = 1`, **one unit above the boundary the paper protects**, and made every row
  stricter than the approved form. T07 tests `S.log_barrier` (the calibrated form), so the drift was
  between the calibrated helper and the closed loops that bypassed it. Neither the G3 review nor the
  first G4 acceptance caught it; the T08 POST even carried the contradiction internally ((16) quoted
  with a `Γ = 1` boundary next to a `Γ_raw < 0` crossing criterion).
- Why this is a fix and not a retune: D007 is the G0-approved calibration rule; the code simply did
  not implement it. The corrected row is *weaker* away from the boundary (at `Γ_raw = 2.07` it demands
  `Γ̇ ≥ −0.73` instead of `Γ̇ ≥ −0.068`), so this cannot be read as loosening a test to make it pass —
  the acceptance criterion (crossings) is unchanged and the negative controls got sharper.
- Fix: `T08/Fixture.rhs()` and the `T10` inline row now use `log(Γ_raw / KAPPA)` with
  `PAPER_FALLBACK` for `Γ_raw ≤ 0`. New check **P10.8** asserts the in-loop rhs is bit-identical to
  `S.log_barrier` on the whole recorded `Γ` history (max diff `0.0`); it exists because this drift
  already happened once.
- Regenerated closed-loop numbers (old → new):
  - T08: `min_t Γ_raw` SCA on **2.1813 → 1.3347** (0 crossings, unchanged); activation
    **50.1 % → 47.0 %**; `nu_max 1.1e-3 → 1.0e-3`; dt ladder `2.18127/2.18267/2.18316` (Δ ≤ 1.4e-3)
    → **1.33474/1.33677/1.33743** (Δ ≤ 2.0e-3); **N8.1 is now a stronger control**: flipping the
    gradient sign produces an actual crossing (`min Γ_raw = −0.0209`, was `+0.9859`) plus 647
    infeasible steps (was 701); N8.3 infeasible 1473 → 1479. SCA-off control unchanged
    (−2.3942 / 656).
  - T10: `min_t Γ_raw` **2.0700 → 1.0043** (0 crossings, unchanged); **QP_INFEASIBLE 370/800 → 0/800**
    — the calibrated hard row is feasible on every step; activation **53.1 % → 96.9 %**; KKT
    `1.6e-14 → 3.2e-16`; Theorem-3 identity `9.1e-13 → 3.3e-16` (relative `6.5e-16`), ledger
    `residual + ΔV = 4.9e-17`; `λ = 0` control unchanged in direction (4.2235 / 0 crossings) with 594
    infeasible steps; dt-doubled `1.0042` / `t_switch 2.820 s`.
- Consequences for earlier decisions:
  - **D018 is superseded in its quantitative part**: the "hard row infeasible on 46 % of steps" was
    an artifact of the uncalibrated offset. Under D007 the e2e claim *upgrades*: with **no freeze and
    no row drop**, the row alone prevents all crossings on both fixtures. The `row_policy` machinery
    stays in the code as a measured fallback; on these fixtures it is exercised only by the negative
    controls (T10/N10.4: 594 steps; T08/N8.1: 647 steps). The prohibition on timing/tracking claims
    from these runs is kept as a standing rule (velocity-level fixtures, not tracking experiments).
  - **D016, Decision 1, phrasing correction**: "with `Γ_raw < 1` the paper replaces `log(Γ−1)`" must
    read "with `Γ_cal < 1` (⟺ `Γ_raw ≤ 0`)". The measured content of D016 (fallback as a hard row
    demands `Γ̇ ≥ 1000` against a best effort of 28.2 s⁻¹) is unchanged.
  - **D017 is unaffected structurally** (the identity is rhs-independent) and its numbers improve.
- **R2 addendum (added by D020, 2026-10-21) — three different "boundaries", do not conflate them.**
  D019's phrase "the barrier sat one unit above the boundary the paper protects" and its
  "`Γ_raw = 1`" wording are easy to misread, so the three levels are now stated explicitly:
  1. **SVM classification boundary: `Γ_raw = 0`.** The learned decision function is
     `Γ_raw(q) = d(q)`; the shipped models have `bias = 0`, so "positive class" ⟺ `Γ_raw > 0`. This is
     a *classification* property of the learned model, not a dynamical one.
  2. **Logarithmic domain boundary: `Γ_raw = 0`.** Under D007, `log(Γ_cal − 1) = log(Γ_raw/κ)` is real
     only for `Γ_raw > 0`; the rhs has a singularity there.
  3. **Continuous-time forward-invariant threshold: `Γ_raw = 1`.** For the corrected inequality
     `Γ̇_raw ≥ −log(Γ_raw)` the set `[1, ∞)` is forward invariant: `V(Γ) = Γ log Γ − Γ + 1 ≥ 0` with
     `V(1) = 0` gives `V̇ = log(Γ)·Γ̇ ≥ −(log Γ)² ≤ 0`, and directly at `Γ = 1` the bound is `Γ̇ ≥ 0`,
     so no trajectory can cross `1` downwards. The **pre-audit** form `−log(Γ_raw − 1)` had its
     analogous threshold at `Γ_raw = 2` — that is the sense in which D019 says the old barrier was
     "one unit above": it was one unit above **the invariance threshold of the barrier it replaced**,
     while its *domain* boundary also sat at `Γ_raw = 1`, i.e. above the **SVM/log** boundary at `0`.
     Both offsets are real but they are offsets of different objects; D019's numbers are correct and
     its wording is now disambiguated here.
  - Why the distinction matters operationally: the **acceptance criterion is empirical and unchanged
    — per-step `Γ_raw < 0` crossings** — because (3) is a continuous-time statement and the fixtures
    integrate with forward Euler at `dt = 10 ms`. No finite-step guarantee is claimed from the
    Lyapunov/comparison argument; the coded gates (`P10.x`, `P8.x`) count crossings and boundary
    distance on the actual trajectories, and D020 adds `n_steps_below_invariance_threshold` so the
    `Γ_raw = 1` level is *reported* rather than silently assumed.
- Label: **[ORIGINAL]** (equations) / **[ENGINEERING]** (drift fix, drift guard).

## D020 — Independent post-delivery review round 2 (R1–R4)
- Date: 2026-10-20 (after `e6135d3d`)
- Trigger: an independent source-code review raised four issues. All four were verified against the
  code, fixed or documented, and the closed-loop evidence was regenerated. No new task, no T09, no
  scope extension.

**R1 — P10.8 audited derived values, not the solver's input.** Accepted. The old P10.8 recomputed the
rhs from the recorded (post-step) Γ history and compared it with `S.log_barrier` — two derived values,
neither of them the number the QP actually received, and the Γ values were post-integration while the
QP uses pre-integration state. Fix: the rollout now records, per step, the pre-solve `Γ_raw`, the
joint-space gradient, the applied joint velocity, and the rhs **read back from the `QP` object itself**
(`qp.sca_rows[0][1]`, `qp.lam`). The new P10.8 (a) re-derives `Γ_raw` and the gradient from the
pre-solve joints `q_pre = q0 if k==0 else q[k-1]`, (b) reconstructs (17d) from that and compares with
the applied rhs, (c) compares with `S.log_barrier`, and (d) checks the assembled inequality
`-g·q̇ ≤ λ·rhs` against the applied `q̇` (sign and scaling of the real numerical constraint).
Measured over all 800 row-bearing steps: Γ reconstruction **exactly 0**, gradient **exactly 0**,
rhs reconstruction **exactly 0**, log-barrier **exactly 0**, row violation **2.2e-16**, `λ = 1`.
New negative control **N10.6** re-runs a 200-step rollout with the actual rhs replaced by
`log(Γ_raw − 1)`: the audit reads the solver's input, so the mutation is detected at **0.483**
(Γ reconstruction stays exact), i.e. the D019-class drift can no longer pass silently.

**R2 — three different "boundaries" were being conflated.** Accepted and now distinguished everywhere:
- **SVM classification boundary: `Γ_raw = 0`** (shipped models have `bias = 0`).
- **Logarithmic domain boundary: `Γ_raw = 0`** (under D007, `log(Γ_cal−1) = log(Γ_raw/κ)`).
- **Continuous-time forward-invariant threshold of the corrected inequality: `Γ_raw = 1`.**
  Proof: with `Γ̇ ≥ −log(Γ_raw)` and `V(Γ) = Γ log Γ − Γ + 1` (V ≥ 0, V(1) = 0),
  `V̇ = log(Γ)·Γ̇ ≥ −(log Γ)² ≤ 0`, so by the comparison lemma every trajectory with `Γ_raw(0) ≥ 1`
  stays `≥ 1`; on `(0,1)` the bound gives `Γ̇ ≥ −log Γ_raw > 0` (repelled from 0, attracted to 1).
  The pre-audit `−log(Γ_raw−1)` had the analogous threshold at `Γ_raw = 2`. These three levels are
  **not** the same property, and the acceptance criterion remains the empirical, per-step
  **`Γ_raw < 0`** crossing count — the continuous-time invariance argument makes **no** finite-step
  guarantee. Empirics on the recorded trajectories: T10 spends **0/800 steps below `Γ_raw = 1`**
  (margin to 1: `+0.0043`, metrics `n_steps_below_invariance_threshold`,
  `n_steps_below_svm_boundary`); T08's `min_t Γ_raw = 1.3347 > 1`, i.e. also never below the
  threshold. Finite-step safety is therefore an *observation on these trajectories*, never a
  continuous-time corollary.

**R3 — T10 solves the QP with the exact active set, not by integrating Eq.(20).** Accepted; the POST
and this record now say so explicitly. New check **P10.9** re-solves 16 of the *actual* QP instances
captured during the reference rollout (4 nearest min-Γ, 6 with an active row, 6 uniform;
`Γ_raw ∈ [1.004, 4.237]`) with the Eq.(20) RK4 flow (`LV.solve`), protocol: T05 settings
(dt = 5e-3, 20000 steps) plus one retry (dt = 1e-3, 60000 steps). Findings, reported not substituted:
- The active-set answer is the LVI fixed point **`P(u − (Mu+b)) = u` to 2.8e-16 on every instance**.
- The (20) flow converges but **slowly**: best fixed-point residual **7.0e-10** (in agreement with the
  active set to **4.2e-09**), worst **0.76**; **0/16** instances reached the 1e-10 tolerance within
  the budget. Smaller steps with the same step *budget* cover less ODE-time and do worse (2e-4 probe:
  ≥ 1.2e-3), so this is slow flow dynamics near the stiff log barrier, not a step-size artifact.
- **Limitation recorded (discipline rule 5):** the LVI-dynamics route is not used as the closed-loop
  solver and no claim is made that an "LVI controller" ran the 800-step rollout; the closed loop
  solves the LVI's fixed-point problem exactly each step (as the official solver, one QP call per
  cycle, also does), and D017/P10.6 quantify what the quasi-static re-solve does and does not mean.

**R4 — documentation and test integrity.** Fixed: the stale `log(Gamma_raw - 1)` wiring line in
`P5_T10_POST.md` §1; the P10.7 verdict that printed the *reference* run's infeasibility count where
the N10.4 (λ = 0) count belongs (the reference has 0, N10.4 has 594). Reconfirmed by inspection:
N10.3 feeds `run_all.evaluate_gates` an **in-memory fake result set** and performs no disk I/O;
P10.7's gate is falsifiable — it fails on any crossing in the reference or counterfactual run, on any
unattributed infeasibility, and its "no fallback" branch requires `QP_INFEASIBLE == 0` on the
reference run, so a frozen-motion dependence cannot hide.

**D020 addendum — what the P10.7/R4 wording actually gates now.** The R4 claim above was originally
backed by inspection only, so the gate itself was tightened (not just the prose):
- `ref_ok` is now required for **every** branch: reference-run `BOUNDARY_CROSSING == 0`,
  `min_gamma > 0`, and **attribution** — `sum(counts["INF_NOROW_*"]) == counts["QP_INFEASIBLE"]`
  whenever the latter is non-zero. An unattributed infeasibility (the row-removed re-solve failing
  in a *different* class) now fails P10.7 instead of being reported as a curiosity.
- The strong "row only, no fallback" branch still requires `QP_INFEASIBLE == 0` **and**
  `ROW_DROPPED == 0`, so a crossing-free outcome produced by frozen motion (or by silently dropping
  the row) cannot be read as an SCA-only result.
- The verdict string now prints the N10.4 (λ = 0) infeasibility count — 594 — where the pre-D020 code
  printed the *reference* run's 0, and the metric `infeasible_sca_on_attributed` is recorded so the
  attribution claim is auditable from the ledger alone.
- P10.8 additionally records and gates the **calibrated** Gamma actually used to build the rhs
  (`Γ_cal = 1 + Γ_raw/κ`, max diff `0.0`), completing the R1 list (pre-solve Γ, calibrated Γ,
  joint-space gradient, rhs, λ, assembled inequality).

**Remaining limitations after D020 (unconditional acceptance is NOT claimed):**
1. The 800-step rollout is solved by the **exact active set**, not by integrating Eq.(20); P10.9
   documents that the (20) flow is too slow near the log barrier to reach 1e-10 within 20 000–60 000
   RK4 steps on most sampled instances. "LVI-controller executed" remains an unsupported statement.
2. All safety numbers are finite-step **observations** on two velocity-level fixtures with forward
   Euler at `dt = 10 ms`; the continuous-time invariance threshold `Γ_raw = 1` is an analytic fact
   about the ODE, not a discrete-time guarantee.
3. The `Γ` criterion is a 2-D learned barrier on these fixtures only; nothing here is a geometric
   collision-avoidance guarantee, and no timing/tracking claim is derived from these runs.
4. T09 remains **not authorized** and is excluded from the ledger; `FULL_PAPER_REPRODUCED` is still
   not claimed (hardware, unreleased training set, CVXGEN).
