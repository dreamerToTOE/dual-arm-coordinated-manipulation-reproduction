# P5 Gate Log

Append-only record of gate outcomes for the numerical phase on branch
`reproduce-p5-numerical-20261020` (base `42f8b857`). Every number here is produced by
`p5/impl/run_all.py`; nothing is estimated.

Reproduce any row with:

```
cd p5/impl && PYTHONPATH=. /usr/bin/python3.10 run_all.py --gate G1
```

---

## G0 — documents and matrix (2026-10-20)

- Outcome: **PASS**, recorded at commit `23a77816`.
- Ten mandatory review corrections applied to the plan, the reproduction matrix, the study report,
  the equation audit; `p5/tools/p5_tables.py --check` green (`table_sha256` `1b0e2c64…`).

## G1 — foundation layer (2026-10-20)

| Task | Status | Checks | pos / neg | Wall | Report |
|---|---|---|---|---|---|
| T01 τ allocation, Eq.(8) | PASS | 11 | 6 / 5 | 1.4 s | `p5/reviews/P5_T01_POST.md` |
| T02 LPV + common Lyapunov `P` | PASS | 12 | 7 / 5 | 7.3 s | `p5/reviews/P5_T02_POST.md` |
| T04 centralised QP IK | PASS | 20 | 12 / 8 | 1.9 s | `p5/reviews/P5_T04_POST.md` |
| T06 2-D SCA boundary | PASS | 10 | 6 / 4 | 0.8 s | `p5/reviews/P5_T06_POST.md` |
| **G1 total** | **PASS** | **53** | **31 / 22** | **11.4 s** | `p5/evidence/P5_impl_checks.json` |

Gate condition (plan §3.2): all four L1 validation sets green — met, 0 failed checks.

### Corrections made *during* G1 (all recorded in the plan in place)

| # | Where | What was wrong | Disposition |
|---|---|---|---|
| 1 | plan §4 T04 state table | five states assume "equality consistent ∧ `θ̇⁻ ≤ θ̇⁺` ⇒ feasible" | added sixth state `INFEASIBLE`; N4.7 pins it |
| 2 | plan §4 N4.5 | said `μ → 0` removes the brake; actually it freezes the joint | N4.5 now tests `μ → ∞` for removal and `μ → 0` for freezing |
| 3 | plan §4 P4.7 | demanded a 1 ms single solve | recorded p50/p99 instead; order-of-magnitude guard only, no real-time claim |
| 4 | `p5core/kinematics.py` | mixed absolute link angles with a relative-joint Jacobian | FK now accumulates angles; link-point Jacobian re-verified at 1e-10 |

### Deviations that carry a scientific label

| Item | Label | Note |
|---|---|---|
| QP backend (active-set / SLSQP / LVI instead of CVXGEN) | `ADAPTATION` | strictly convex QP ⇒ unique minimiser; changes the path, not the answer |
| LVI used as dynamics/passivity object, not as the solver | `ADAPTATION` | projected iteration converges in 7 414 steps on the T04 fixture, ~1e5 when `W` is stiff — see D010 |
| 2-D and 3-link geometries | `ADAPTATION` | no claim about the paper's KUKA IIWA arms |
| `PlanarArm` / `DualPlanarArm` | `ENGINEERING` | structure only, carries no scientific claim |

---

## G2 — solve layer (2026-10-20)

| Task | Status | Checks | pos / neg | Wall | Report |
|---|---|---|---|---|---|
| T03 virtual-object DS, Eq.(9)–(11)–(36) | PASS | 11 | 6 / 5 | 5.5 s | `p5/reviews/P5_T03_POST.md` |
| T05 LVI + Theorem 3 passivity | PASS | 14 | 7 / 7 | 0.6 s | `p5/reviews/P5_T05_POST.md` |
| T07 36-D model, calibration, Eq.(26) | PASS | 12 | 6 / 6 | 99.9 s | `p5/reviews/P5_T07_POST.md` |
| **G2 total** | **PASS** | **37** | **19 / 18** | **106.0 s** | `p5/evidence/P5_impl_checks.json` |
| **G1 + G2 cumulative** | **PASS** | **90** | **50 / 40** | **117.4 s** | same ledger |

Gate condition (plan §3.2): two-segment cancellation resolved, LVI agrees with an independent QP
(3.9e-9) and the KKT/passivity residuals meet tolerance (8.3e-17), 36-D calibration invariants and
the chain rule pass. All met, 0 failed.

### Corrections made *during* G2

| # | Where | What was wrong | Disposition |
|---|---|---|---|
| 5 | plan §4 N7.3 | asserted that swapping the two published `σ` destroys the decision function | measured 0.9992 → the swap is now a *metric*; N7.3 injects the harmful defect (`-g` read as width, 0.5670). See D013 |
| 6 | plan §4 N3.1 wording | "(11) is `τ`-free" | false in general; only the `τ̇` *segment* cancels unconditionally, the aggregate collapse needs `ẋ_i^V = ẋ^V`. See D014 |
| 7 | `p5core/qp_ik.py` | `solve_active_set` ignored SCA rows (equality-only enumeration) | rows are now enumerated as inequality constraints; this is what made the T05 fixture solvable |
| 8 | plan §4 P5.3 | monotone-residual requirement | replaced by a convergence-decades requirement (≥5) since the projection map is not a gradient flow |

### G2 deviations with a label

| Item | Label | Note |
|---|---|---|
| exact box-active-set solver as the production QP; LVI kept for dynamics/passivity only | `ADAPTATION` | D010; strictly convex QP ⇒ same minimiser |
| Eq.(26) verified on an explicit `f = Aq + b` | `ADAPTATION` | no DH geometry published; the chain rule is verified, the kinematics are not |
| 36-D metrics evaluated on `X_train` | `ADAPTATION` | `IN_SAMPLE_INDEPENDENT_EVALUATION`, D008; no FPR/TPR comparison with the paper |
| `κ ≡ 1` frozen pre-inspection | `ENGINEERING` | D007; the calibrated `Γ` scale is not data-derived and T08 must not depend on it |
| toy 2-D/3-D object and 3-DOF fixtures | `ENGINEERING` | the 12-DOF dual-arm case is T08/T10 |

---

## G3 — integration layer (2026-10-20)

| Task | Status | Checks | pos / neg | Wall | Report |
|---|---|---|---|---|---|
| T08 learnt SCA boundary inside the QP | PASS | 13 | 7 / 6 | 85.9 s | `p5/reviews/P5_T08_POST.md` |
| **G3 total** | **PASS** | **13** | **7 / 6** | **85.9 s** | `p5/evidence/P5_impl_checks.json` |
| **G1 + G2 + G3 cumulative** | **PASS** | **103** | **57 / 46** | **201.4 s** | same ledger |

Gate condition (plan §3.2): zero boundary crossings with SCA on **and** crossings present in the
matched SCA-off control. Measured: `min_t Γ_raw = +2.1813` with 0 crossings on, `−2.3942` with 656
crossings off, same task and same initial state. Met.

### What G3 added beyond the plan

| # | Item | Why the plan was not enough | Disposition |
|---|---|---|---|
| 9 | task coordinate ≠ SCA feature | if the SCA feature were the task coordinate, `Γ̇` would be *implied* by the equality row and (17d) could never bind; the boundary would behave like a switch | task drives one tip, SCA constrains the tip pair, second arm supplies the slack (D015) |
| 10 | `λ = 0` expectation | plan predicted λ = 0 to be the looser setting with crossings; measured it is a strict no-decrease cone that blocks the approach at step 1 | N8.2 rewritten to report the falsification (D016) |
| 11 | printed `−log(Γ−1)` expectation | plan predicted "attracted to the boundary"; measured the request is *inverted* far away and *vacuous* near the wall | N8.3 reports both halves, with the rhs table at Γ_raw ∈ {1.01, 1.2, 2.0, 6.38} |
| 12 | `PAPER_FALLBACK` | plan assumed it "pushes outward"; as a hard row with rhs = −1000 it is unsatisfiable (demands Γ̇ ≥ 1000 against a best effort of 28.2) | P8.6 reports it as a soft-formulation device (D016) |

### G3 deviations with a label

| Item | Label | Note |
|---|---|---|
| learned boundary = official 2-D CPSP model, native coordinates | `ADAPTATION` | no rescaling or rotation; the model is used where it was trained |
| 4-DOF planar dual arm, `d_n = 2`, `d_c = 1` | `ADAPTATION` | the paper's 12-DOF dual arm is not reproduced |
| `dt` ladder `{5e-3, 2.5e-3, 1.25e-3}` | `ENGINEERING` | plan said `{2e-3, 1e-3, 5e-4}`; same 2× refinement, coarse end chosen for runtime |
| `λ = 1`, `μ = 20`, `q̇_max = 1.5 rad/s` | `ENGINEERING` | no numerical value is published for any of them |

---

## G4 — end-to-end (2026-10-20)

| Task | Status | Checks | pos / neg | Wall | Report |
|---|---|---|---|---|---|
| T10 end-to-end chain (tau → LPV DS → virtual object → QP → LVI) | PASS | 12 | 7 / 5 | 142.2 s | `p5/reviews/P5_T10_POST.md` |
| **G4 total** | **PASS** | **12** | **7 / 5** | **142.2 s** | `p5/evidence/P5_impl_checks.json` |
| **G1 + G2 + G3 + G4 cumulative** | **PASS** | **115** | **64 / 51** | **344.2 s** | same ledger |

Gate condition (plan §3.2): the asynchronous→synchronous switch is observable **and** the matched SCA
on/off control holds. Measured: `τ` integrates from `ε = (0.02, 0.03)` to `(0.982, 0.988)`
monotonically with `t_switch = 2.800 s` inside the pre-declared `[1, 5] s` window; `min_t Γ_raw =
+2.0700` with 0 crossings on against `−2.3147` with 534 crossings off. Met.

### What G4 added beyond the plan

| # | Item | Why the plan was not enough | Disposition |
|---|---|---|---|
| 13 | Theorem-3 ledger | review #14 asked for a numerical energy ledger; the ledger does **not** close (−328.4 against 328.7) because every step's `u` is a fixed point of a *different* LVI, so `YᵀU = ψ` instantaneously and the non-closure is exactly `−ΔV` | P10.5 gates the per-step identity (`9.1e-13`), P10.6 gates `residual + ΔV = 2.8e-14`; the ledger is a reported metric, never a pass criterion (D017) |
| 14 | hard (17d) infeasible on 46 % of steps | plan assumed infeasibility was an edge case; measured `370/800`, all attributed to the row (row removed → `OPTIMAL` 370/370, reference velocity `≤ 0.0279`) | two labelled fallbacks were run: freeze (`min Γ 2.0700`) and row-dropped on those steps (`min Γ 1.2400`, 0 crossings) → the row, not the freeze, carries the guarantee (D018) |
| 15 | the pair selection rule | the plan named the SCA feature but not how *which* pair is chosen; picking on the constrained outcome would leak the result | rule fixed on the uncontrolled trajectory only (Γ(0) > 1.5, `min Γ < −0.5`, null share ≥ 0.10) → `L3–R2`, `Γ_raw(0) = 4.2255`, share 0.21; full candidate table in the evidence |
| 16 | `τ` must be integrated, not scheduled | Eq.(8) has equilibria at 0 and 1, so a "switch" is only meaningful if it emerges | N10.2 pins `τ ≡ 1` / `τ ≡ 0` and gets `t_switch = None` in both |

### G4 deviations with a label

| Item | Label | Note |
|---|---|---|
| two 3R planar arms, `d_Q = 6`, `d_n = 4`, `d_c = 1` | `ADAPTATION` | the paper's 12-DOF dual arm is not reproduced |
| learned boundary = official 2-D CPSP model, native coordinates | `ADAPTATION` | used where it was trained; no rescaling |
| `A_ARM = −0.35 I`, `A_V = −1.5 I`, `k = 0.8`, `V_MAX_TIP = 0.15 m/s` | `ENGINEERING` | no published value for any of them |
| `row_policy ∈ {freeze, drop_row}` | `ENGINEERING` | both are reported; neither is the paper's controller (D018) |
| `t_switch` window `[1, 5] s` | `ENGINEERING` | declared before the run, chosen from the `τ` time constant `k/G`, not from the outcome |

---

## T09 — not executed

T09 (FCL/distance constraints) is `NOT_AUTHORIZED_THIS_CYCLE` and is not part of any G1–G4 total. Its
numbers may never be merged with T08/T10 into a single "SCA reproduction" claim.
