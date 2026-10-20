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
