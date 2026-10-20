# P5-T03 POST — The virtual-object DS and the two-segment cancellation, Eq.(9)–(11)–(36)

**Status**: `PASS` — 11 checks (6 positive / 5 negative), 0 failed, 5.5 s.
**Run**: `p5/evidence/impl_checks/T03.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T03`)
**Code**: `p5/impl/p5core/multiarm_ds.py` **[ORIGINAL]** · **Task**: `p5/impl/tasks/t03_virtual_object.py`
**Figures**: `t03_identity_residual.png`, `t03_tau_dot_invariance.png`, `t03_traj_overlay.png`

## 1. What the paper actually claims (Q2 of the review)

The paper builds the object-level DS in two segments and then differentiates the substitution:

```
(9)   ẋ^V = R(x^V) + Σ_i τ_i δ_i(x^V, x^d)
(10)  δ_i  = -A(x^V)(x^V - x^d) - τ̇_i (x^V - x^d) / (1 + Σ_j τ_j²)  + ...      (per-arm term)
(11)  τ̇ = Σ_i τ̇_i ...                                                            (the "-τ̇" segment)
(36)  ẋ^V = R(x^V) + Σ_i τ_i δ_i   with the τ̇ segment removed
```

The review asked whether the step (11) → (36) is an identity or a premise. T03 answers with
measurements, not with prose:

| Claim | Evidence | Verdict |
|---|---|---|
| `U_i = τ_i ẋ_i^V` makes `τ̇` cancel **unconditionally** | P3.1: `max|U_i − τ_i ẋ_i^V| = 1.19e-15` over 4000 random states with `τ̇ ≠ 0`; P3.3: scaling `τ̇` by 0.1× and 10× leaves `U_i` unchanged to 1.9e-16, i.e. `∂U_i/∂τ̇ ≡ 0` | **identity** |
| `(11)` collapses onto `(36)` **only** when `ẋ_i^V = ẋ^V` for all `i` | P3.2: under that premise the two agree to `5.6e-17` over a 10 s rollout | **conditional** |
| Without the premise, `τ` does **not** drop out | N3.1: per-arm offsets `δ_i`, scaling `τ` by ±50 % moves `x^V` by `5.04e-2` | **premise is load-bearing** |

P3.4/P3.5 are the two degenerate ends of the same statement: `τ = 0` reduces (11) to the bare object
DS *identically* to (36) (`0.0e+00`), and `τ = 1` (fully synchronous, shared velocity) reproduces (36)
exactly (`0.0e+00`). P3.6 then shows that in the shared-velocity regime `τ` has genuinely vanished:
scaling it by ±50 % moves `x^V` by 5.6e-17.

So the honest form of the paper's App. D argument is:

> under the paper's synchronisation premise, `τ̇` cancels *by construction* — it is not cancelled
> *by the algebra of (11)*.

This matters for reproduction because it means `(36)` may be implemented directly (as T08/T10 do)
**provided** the synchronisation layer of Eq.(8) is doing its job; if T01's `τ` coupling were broken,
`(36)` would silently stop being the same system as `(11)`. That dependency is recorded, not hidden.

## 2. Negative controls

| Check | Mutation | Result |
|---|---|---|
| N3.1 | per-arm offsets `ẋ_i^V = ẋ^V + δ_i` | `τ` becomes visible again: 5.04e-2 shift |
| N3.2 | upstream `U_i = −A(·) − τ̇ e` instead of `τ_i ẋ_i^V` | differs by 0.360 — **not interchangeable**, kept as `DEVIATION_REFERENCE` only |
| N3.3 | drop the `−τ̇(x^V − x^d)` segment from (10) | residual 0.060 → P3.1 fails immediately, so the segment is real |
| N3.4 | weight written as `(1 + Στ_i²)` instead of the derived `(1 + Στ_i)` | `x^V` moves by 2.145 |
| N3.5 | `τ = 0` **and** `γ = 0` | RHS is exactly `A^V x^V` (residual `0.0e+00`): no arm term survives at the origin of the interpolation |

N3.2 is the one that had to be handled carefully. The upstream `U_paper` and the paper's own
`U_i = τ_i ẋ_i^V` are different functions that happen to agree on the synchronous manifold; the code
keeps both, labels the upstream one `DEVIATION_REFERENCE`, and uses the paper form everywhere else.
Reporting them as "equal" would have been a silent substitution of the object of study.

## 3. Fidelity and limits

- **[ORIGINAL]**: (9), (10), (11), (36) are implemented as printed, including the `1 + Στ_j²`
  denominator and the `−τ̇` segment.
- **[ADAPTATION]**: the state space is a 2-D/3-D toy object, not the 6-D object of the paper; `A(·)`
  is a constant stable matrix rather than the LPV family of T02. This task tests the *algebra* of the
  two-segment construction, which is dimension-independent; the closed-loop consequence is T08/T10.
- The literal implicit iteration of (11) converges only for small `τ̇`; the paper never states a
  solvability condition, so the task uses the explicit two-segment form and records the iteration
  failure mode rather than asserting global solvability.
- No claim is made about the paper's multi-arm experiments; nothing here is compared to a published
  trajectory because none is published at the numerical level.
