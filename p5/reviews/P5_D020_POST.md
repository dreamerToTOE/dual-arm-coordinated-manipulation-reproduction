# P5 — D020 post-delivery review (independent round 2)

**Scope**: post-delivery review of the accepted G4 delivery (`e6135d3d`), four issues R1–R4.
No new task, no T09, no extra environment, no scope extension.
**Branch**: `reproduce-p5-numerical-20261020`
**Status**: fixes implemented and gated; full suite **118 checks (66 positive / 52 negative), 0 failed,
375.0 s, G1–G4 all `PASS`**. This is **not** an unconditional acceptance — see §5.

---

## 1. What was actually wrong

| # | Review claim | Verdict | Why it mattered |
|---|---|---|---|
| R1 | P10.8 compares two derived values, neither is the QP's input; Γ history is post-integration | **confirmed** | the check would have stayed green through exactly the drift it was written to prevent |
| R2 | three different "boundaries" were conflated (`Γ_raw = 0` SVM, `Γ_raw = 0` log domain, `Γ_raw = 1` invariance) | **confirmed** | D019's wording invited the wrong reading; the invariance claim is continuous-time only |
| R3 | T10 runs `solve_active_set()`, not the Eq.(20) LVI dynamics | **confirmed** | any "LVI controller" phrasing is unsupported |
| R4 | stale `log(Γ_raw − 1)` in the POST, P10.7 printing the wrong counter, N10.3/P10.7 integrity | **confirmed** (all four) | a report that disagrees with the code is a reproducibility defect on its own |

## 2. Counterexamples that forced each fix

**R1.** `P10.8` recomputed `log(Γ/κ)` from `ref["gam"]` (the **post-step** Γ) and compared it with
`S.log_barrier` on the same array. It never read `qp.sca_rows`. Counterexample: replace the rhs
assembled in the rollout by `log(Γ_raw − 1)` — the old check still passes, because both of its inputs
are recomputed from Γ and neither comes from the QP. The new check fails that mutation at **0.483**.

**R2.** Write `Γ̇ ≥ −log(Γ_raw)` and ask "what is protected?" Three answers, three objects:
`Γ_raw = 0` (the learned classifier's decision surface, `bias = 0`), `Γ_raw = 0` (where the log
diverges), `Γ_raw = 1` (where `V(Γ) = Γ log Γ − Γ + 1` attains 0, making `[1, ∞)` forward invariant).
The pre-audit `−log(Γ_raw − 1)` had its invariance threshold at `Γ_raw = 2`. Conflating them would
have turned "0/800 steps below 1" into a bogus discrete-time safety claim.

**R3.** Re-solve the loop's own instances with Eq.(20): the *fixed point* is identical
(active-set answer has LVI residual `2.8e-16`), but the *flow* needs > 60 000 RK4 steps to reach
`1e-6` on most instances, and `0/16` reach `1e-10`. A smaller step at the same step budget is worse
(`≥ 1.2e-3`), so this is stiffness, not tuning. Cost: `63.7 s` for 16 instances vs ≈ `2 ms` per
active-set solve.

**R4.** `P10.7`'s verdict interpolated `ref["counts"]["QP_INFEASIBLE"]` where the N10.4 counterfactual
belongs — printing `0` (reference) instead of `594` (λ = 0). Its gate was also `row_carries or
no_fallback` with no reference-run crossing requirement in the `row_carries` branch.

## 3. Fixes

- **`t10_e2e.py`** — `rollout(..., rhs_mode=..., capture=...)`:
  - records, per step, `gam_pre`, `gam_cal_pre`, `g_row`, `qdot`, and the rhs **read back from the QP
    object** (`qp.sca_rows[0][1]`) plus `qp.lam`;
  - `rhs_mode="mutation_log_minus1"` exists **only** as the R1 mutation (documented as such in the
    docstring, not an option anyone should ship);
  - `capture` keeps `(M, b, lo, hi, u, x, active)` per step so P10.9 can re-solve the real instances.
- **P10.8 (rewritten)** — five independent comparisons per row-bearing step, reconstructed from
  `q_pre = q0 if k == 0 else q[k−1]`: Γ_raw, Γ_cal, embedded gradient, rhs vs `S.log_barrier`, and the
  assembled inequality `−g·q̇ ≤ λ·rhs` evaluated at the applied velocity. Measured over 800/800
  steps: `0.0 / 0.0 / 0.0 / 0.0 / 0.0` and `2.2e-16`, `λ = 1`.
- **N10.6 (new)** — the mutation control: 200 steps with the rhs actually assembled as
  `log(Γ_raw − 1)`; the audit must catch it (`d_recon = d_helper = 0.483`, `d_gram = 0.0`). It does.
- **P10.9 (new)** — LVI/Eq.(20) vs active set on 16 real instances, with a two-attempt protocol
  (`dt = 5e-3 / 2e4`, retry `dt = 1e-3 / 6e4`), reporting convergence status, fixed-point residuals,
  primal difference and wall time; the non-convergence is printed as a limitation, not hidden.
- **P10.7 (tightened)** — `ref_ok` now required on every branch: reference crossings `== 0`,
  `min Γ > 0`, and `sum(INF_NOROW_*) == QP_INFEASIBLE` whenever the latter is non-zero (attribution).
  The strong branch still needs `QP_INFEASIBLE == 0` and `ROW_DROPPED == 0`, so frozen motion or a
  silent row drop cannot be sold as an SCA-only result. Verdict now prints `594`, not `0`.
- **R2 reporting** — new metrics `n_steps_below_invariance_threshold` (0/800),
  `n_steps_below_svm_boundary` (0/800), `min_gamma_margin_to_1` (`+0.0043`); the three-level
  distinction is written into D019's R2 addendum and `P5_T10_POST.md` §9b.
- **Docs** — `P5_T10_POST.md` §1 equation corrected (`log(Gamma_raw/κ)`, `κ = 1`), tables extended to
  15 checks, new §9; `docs/DECISIONS.md` D020 (+ addendum, + limitations); `P5_GATE_LOG.md`,
  `P5_IMPLEMENTATION_PLAN.md` §6.1, `docs/STATUS.md`, `docs/WORKLOG.md` updated to the new counts.

## 4. Evidence after the fixes (all regenerated, nothing hand-edited)

| quantity | value |
|---|---|
| T10 `min_t Γ_raw` (SCA on / off) | **1.0043** / −2.3147 (0 / 534 crossings) |
| T10 row activation / infeasible steps | 96.9 % / **0 of 800** |
| T10 steps below `Γ_raw = 1` / below `0` | **0 / 0**, margin `+0.0043` |
| P10.8 audit residuals (Γ, Γ_cal, grad, rhs, helper, row) | `0.0, 0.0, 0.0, 0.0, 0.0, 2.2e-16` |
| N10.6 mutation detected | `0.483` (Γ reconstruction `0.0`) |
| P10.9 active-set LVI residual (16 instances) | `2.8e-16` |
| P10.9 Eq.(20) flow: best / worst / converged to 1e-10 | `7.0e-10` / `0.76` / **0 of 16** |
| P10.9 cost for 16 instances | `63.7 s` |
| T08 (unchanged by D020) | `min_t Γ_raw = 1.3347`, 0 crossings, N8.1 crossing −0.021 |
| suite | **118 checks (66/52), 0 failed, 375.0 s, G1–G4 PASS** |

## 5. What is claimed, and what is not

**Supported by this delivery**
- The (17d) rhs **actually handed to the solver** equals the D007-calibrated form at every step,
  and the assembled inequality carries the right sign and scaling (`2.2e-16`).
- The drift that D019 fixed is now detectable by a coded check (N10.6), not by inspection.
- On both fixtures the calibrated hard row is feasible on every step, so the crossing-free outcome
  needs neither freeze nor row drop; the fallbacks are exercised only by the negative controls.
- Each step's LVI fixed point is solved exactly and coincides with the active-set solution to `2.8e-16`.

**Not claimed**
1. That an LVI-dynamics controller executed the rollout — it did not; Eq.(20) integration is too slow
   here (P10.9), and the limitation is recorded rather than substituted.
2. Any **finite-step** safety guarantee. `[1, ∞)` forward invariance is a continuous-time statement;
   the fixtures use forward Euler at `dt = 10 ms`, and the delivered evidence is the empirical
   per-step `Γ_raw < 0` crossing count (`0`), plus the reported distance to `Γ_raw = 1`.
3. Geometric collision avoidance, timing, tracking accuracy or smoothness — the (17d) criterion is a
   2-D learned barrier on these velocity-level fixtures.
4. `FULL_PAPER_REPRODUCED` — still excluded (hardware, unreleased training set, CVXGEN); T09 remains
   `NOT_AUTHORIZED_THIS_CYCLE` and is outside every gate total.

## 6. Reproduce

```bash
cd p5/impl
PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T10     # ~172 s, 15 checks
PYTHONPATH=. /usr/bin/python3.10 run_all.py                # ~375 s, 118 checks, G1-G4
/usr/bin/python3.10 p5/tools/p5_tables.py --check          # table/figure consistency
```
