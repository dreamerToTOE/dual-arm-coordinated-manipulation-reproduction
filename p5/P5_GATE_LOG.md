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

## G3 — integration layer (pending)

T08 SCA inside the QP: zero boundary crossings with SCA on, crossings present in the matched
SCA-off control.

## G4 — end-to-end (pending, mandatory)

T10: asynchronous→synchronous switch observable + matched SCA on/off control. T09 is
`NOT_AUTHORIZED_THIS_CYCLE` and is not executed.
