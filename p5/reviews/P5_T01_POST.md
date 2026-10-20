# P5-T01 POST — Synchronisation allocation τ, Eq.(8)

**Status**: `PASS` — 11 checks (6 positive / 5 negative), 0 failed, 1.4 s.
**Run**: `p5/evidence/impl_checks/T01.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T01`)
**Code**: `p5/impl/p5core/tau.py` **[ORIGINAL]** for Eq.(8) · `official_tau_dot` **[DEVIATION_REFERENCE]**
**Task**: `p5/impl/tasks/t01_tau.py` · **Figures**: `t01_tau_three_cases.png`, `t01_tau_vs_G.png`,
`t01_deviation.png`, `t01_convergence.png`

## 1. What is being tested

Eq.(8) gives the coordination allocation `τ` as a logistic field driven by the distance to the
virtual object. With `G` constant the ODE has a closed form, which is what makes this task a
*reference* test rather than a self-check.

The G0 correction that matters here: `τ₀ ∈ {0,1}` are the **two unique equilibria**, not a
non-unique family. With finite `k` and finite `G` the solution is identically `τ₀`; nothing drifts.
So the tests check equilibrium invariance and the fact that leaving an endpoint *requires* a
perturbation, instead of asserting a non-uniqueness that does not exist.

## 2. Positive evidence

| Check | Content | Result |
|---|---|---|
| P1.1 | `G>0`: monotone rise to 1 | closed-form error 6.6e-14 |
| P1.2 | `G<0`: monotone decay to 0 | closed-form error 2.0e-17 |
| P1.3 | `G=0`: `τ` stays at `τ₀` | drift 0 |
| P1.4 | RK4 convergence order | 3.991 / 3.995 on `dt ∈ {1e-2, 5e-3, 2.5e-3}` |
| P1.6 | `τ₀ ∈ {0,1}` are equilibria | max drift 0.0 |
| P1.5 | paper (8) vs the upstream `Multiarm_ds` variant | RMS deviation 8.3e-03, sign conflict on the x-component |

## 3. Negative / mutation evidence

| Check | Content | Result |
|---|---|---|
| N1.1 | endpoint invariance survives a zero perturbation but a 1e-3 perturbation escapes | detected (1e-3) |
| N1.2 | `k→0` with fixed step breaks the (0,1) invariant | detected |
| N1.3 | `|G| ~ 1e4` with `dt = 1e-2` is badly resolved | detected (divergence) |
| N1.4 | putting `k` in the numerator reverses the transient | detected (dev 0.974) |
| N1.5 | flipping the sign of `G` | detected (dev 1.000) |

## 4. Fidelity and limits

- **[ORIGINAL]** Eq.(8) as printed; the closed form is derived from it, not fitted to it.
- **[DEVIATION_REFERENCE]** the upstream `calculate_coordination_allocation` uses only the
  x-component of the distance to the virtual object, a scale of 10 and a clamp to `[0.001, 0.99]`.
  It is reproduced **only** so that P1.5 can quantify the difference; it is never used downstream.
- Limit: `τ` here is driven by a synthetic `G(t)`; the closed loop that generates `G` belongs to
  T03/T10, so no claim is made about the switching *time* of the paper's experiments.
