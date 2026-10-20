# P5-T05 POST — The LVI projection dynamics, Eq.(19)–(23), and Theorem 3

**Status**: `PASS` — 14 checks (7 positive / 7 negative), 0 failed, 0.6 s.
**Run**: `p5/evidence/impl_checks/T05.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T05`)
**Code**: `p5/impl/p5core/lvi.py` **[ORIGINAL]** · **Task**: `p5/impl/tasks/t05_lvi.py`
**Figures**: `t05_convergence.png`, `t05_solver_agreement.png`, `t05_vdot_sign.png`

## 1. What this task verifies, and what it does not

The paper's Eq.(19)–(23) is a **linear variational inequality** on the joint-velocity box:

```
(19)  find u ∈ Ω = { u : g u ≥ b, u_min ≤ u ≤ u_max }
(20)  such that  (v − u)ᵀ (M u + b_M) ≥ 0   ∀ v ∈ Ω
(21a) u̇ = Π_Ω(u, M u + b_M)                     (projection dynamics)
(21b) b_M,i = −log(Γ_i − 1)                     (barrier row)
(22)  V = ½ uᵀ u ,  ψ = ...                     (storage function)
(23)  V̇ + ψ = Yᵀ U
```

Three separate things are tested, and they must not be conflated:

1. **The equilibrium** (P5.1, P5.2): does the fixed point of (21a) coincide with the exact
   KKT solution of the LVI? Yes — `3.88e-09` gap in 1133 iterations.
2. **The dynamics** (P5.3, P5.4): does the projection iteration converge, and how fast?
   8.3 decades of residual, robust to a redundant (rank-deficient) equality row.
3. **The passivity identity** (P5.6, P5.7, N5.6): does `V̇ + ψ = YᵀU` hold to machine precision, and
   is it non-vacuous?

Theorem 3 is an **energy-balance** statement, not a stability statement. P5.7 exists to prevent the
common misreading: `V̇` is **positive on 2999 of 3000 steps** (max 2.44e-2). The system is *not* a
gradient flow of `V`; `V̇` changes sign and the input supplies energy. Writing "`V̇ ≤ 0`, hence
convergent" would have been a fabricated Lyapunov proof.

## 2. Positive evidence

| Check | Content | Result |
|---|---|---|
| P5.1 | LVI fixed point vs exact active-set referee | gap **3.88e-09**, 1133 iters (residual 9.9e-10); SLSQP 3.2e-2 off, recorded as a solver caveat |
| P5.2 | fixed-point residual `‖Π(u − Mu − b) − u‖` and KKT multiplier | 9.86e-10, `ν = 4.83e-02 ≥ 0` |
| P5.2b | KLT multiplier of the active SCA row | min 4.83e-02, i.e. the row's sign convention matches (17d) |
| P5.3 | convergence profile | 1133 iters (< 1e5), residual 1.8e-1 → 9.9e-10, step 0.445 |
| P5.4 | redundant equality row (`M` singular, cond 1.7e+17) | still converges, residual 1.0e-09 |
| P5.6 | passivity identity over 3000 steps | residual **8.3e-17**, `min ψ = 0` (dissipation never negative) |
| P5.7 | sign of `V̇` | positive on 2999/3000 steps → it is an energy *rate*, not a Lyapunov decrement |

P5.5 also gave a useful methodological lesson: `M` here is **not symmetric** (it is the QP's
`[G; −G; A]` stack with Lagrange multipliers), so `M` vs `Mᵀ` is a real fork. Writing `M` by accident
gives an `8e-17`-clean identity too — the identity is silent about the transpose. It had to be pinned
by trajectory deviation, which is why P5.5 is a *negative* control with a *measured* deviation rather
than a claim.

## 3. Negative controls

| Check | Mutation | Result |
|---|---|---|
| P5.5 | `(I + M)` instead of `(I + Mᵀ)` (positive-looking check, negative control by nature) | trajectory differs by **4.80e-2** — the transpose position is observable, not cosmetic |
| N5.1 | ill-conditioned `M` (cond 1e+12) | status `OPTIMAL` but convergence flag `False`, residual 1.8e-1 — the defect is **visible** instead of hanging |
| N5.2 | `λ = 0` on the SCA row | the constraint degenerates to a half-space `g·u̇ ≥ 0`; boundary reached exactly, solution sits **0.100** away from the `λ = 1` answer which lies on `g·u̇ = b` |
| N5.3 | upstream `Omega_projector()` returns its input | pinned: bounds `[[1,−1]]` in, `[[5,−5]]` out — a reproducible upstream failure, not a claim |
| N5.4 | `b3 = −log(Γ−1)` (the printed form) | drives the row to `g·u̇ = +rhs` instead of `−rhs`, moving `u̇` by **0.200**: the printed sign contradicts the KKT conditions (Q3) |
| N5.5 | reversed box order (`u_min > u_max`) | caught **before** any iteration: `Ω` ordering violation, status `BOUND_INFEASIBLE` |
| N5.6 | drop the `I` in `(I + Mᵀ)` | passivity residual 2.48e-04 = **3.0e+12×** the correct 8.3e-17 → the identity is not vacuous |

N5.2 and N5.4 are the two places where the paper's printed text and the KKT conditions disagree or
degenerate. Both are recorded as **observations about the paper**, resolved in favour of the KKT
conditions, and logged in `docs/DECISIONS.md` D006 (the `(21b)` sign) and D010 (solver split) rather
than silently "fixed".

## 4. Solver architecture decision (D010)

The first implementation integrated (21a) with RK4 and used it as *the* QP backend. On the T05
fixture that diverged (residual 0.21, gap 9.5e-2) because the projection map is only
non-expansive, not contractive, and the fixture's LVI was in fact **infeasible** — the target
velocity lay outside the velocity box. Two changes followed:

- `solve_active_set` now enumerates SCA rows as linear constraints as well (mask over `2^{d_c}`),
  so an infeasible `Ω` is diagnosed instead of being reported as a solve;
- the LVI is **not** used as the production solver. It is retained exactly where the paper needs it —
  reproducing the *dynamics* and *passivity* of (21a) — while QP answers come from exact
  box-active-set enumeration (3^d KKT solves) plus an SLSQP cross-check. This is why P5.1 compares
  two independent solvers instead of comparing a solver with itself.

Consequence for T08/T10: the real-time claim is about the QP, and the timing in T04 (P4.7) and T07
(P7.6) is measured on that path, not on an LVI iteration that would never meet a 2 ms budget.

## 5. Fidelity and limits

- **[ORIGINAL]**: (19)–(23) and the passivity identity are implemented as printed, including the
  `+log(Γ−1)` sign taken from the KKT conditions.
- **[ADAPTATION]**: the fixture is a 3-DOF box with one SCA row, chosen so that the active set is
  unambiguous; the paper's 12-DOF dual-arm case is T08/T10.
- `λ` (the barrier weight in (18)) is varied but not calibrated against the paper; the paper gives no
  numerical value. `λ = 1` is the reference, `λ = 0` the degenerate control.
- The convergence rate (1133 iterations for a 3-D problem) is honest but slow: the scaled projection
  iteration is a *correctness* device, not an implementation proposal. No claim of real-time LVI is made.
