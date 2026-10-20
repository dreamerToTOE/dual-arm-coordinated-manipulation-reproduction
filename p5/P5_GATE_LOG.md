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

## G2 — solve layer (pending)

T03 virtual-object dynamics (two-segment cancellation), T05 LVI + passivity inequality,
T07 36-D model + chain rule + calibration invariants.

## G3 — integration layer (pending)

T08 SCA inside the QP: zero boundary crossings with SCA on, crossings present in the matched
SCA-off control.

## G4 — end-to-end (pending, mandatory)

T10: asynchronous→synchronous switch observable + matched SCA on/off control. T09 is
`NOT_AUTHORIZED_THIS_CYCLE` and is not executed.
