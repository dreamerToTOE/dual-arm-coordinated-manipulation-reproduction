# P5-T02 POST — LPV scheduler and the numerical sufficiency of Theorem 1

**Status**: `PASS` — 12 checks (7 positive / 5 negative), 0 failed, 7.3 s.
**Run**: `p5/evidence/impl_checks/T02.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T02`)
**Code**: `p5/impl/p5core/lpv.py` **[ORIGINAL]** (Eq.3–5, 12–13) · **Task**: `p5/impl/tasks/t02_lpv.py`
**Figures**: `t02_convergence.png`, `t02_lyap_eig.png`, `t02_theta_simplex.png`

## 1. What is being tested

A common quadratic Lyapunov matrix `P` for the LPV mixture `A(θ) = Σ θ_k A_k` is *sufficient* for
Theorem 1, and the paper never claims it is necessary. Two things had to be handled explicitly
(G0 item 2):

1. The search `min λ s.t. P A_k + A_kᵀP ⪯ λI` is scale-degenerate: scaling `P → cP` scales the
   margin, and a solver can drive `P → 0` to make any margin look good. The search therefore
   normalises `trace(P) = 1`, which removes exactly that direction.
2. A failed search means **`SUFFICIENT_CONDITION_NOT_CERTIFIED`**, never "the LMI is infeasible".

## 2. Positive evidence

| Check | Content | Result |
|---|---|---|
| P2.1 | common `P` exists for a constructed family | J\* = −0.341, CERTIFIED, direction cos vs truth 0.9955 |
| P2.2 | normalisation and definiteness | `trace(P) = 1.000000000000`, `λ_min = 0.351` |
| P2.3 | `θ` on the simplex | 4 probe points, `θ_k ≥ 0`, `Σθ = 1` |
| P2.3b | `A(θ)` inside the componentwise hull of `{A_k}` | holds |
| P2.4 | stable mix decays | `‖x(T)‖ = 1.7e-09` at `T = 56.4 s` |
| P2.5 | `τ = 1` tracks the virtual object exactly | `‖x^R − x^V‖ = 4.1e-15` |
| P2.6 | degenerate prior falls back to uniform | holds |

## 3. Negative / mutation evidence

| Check | Content | Result |
|---|---|---|
| N2.1 | inject `A_k` with a positive real eigenvalue | `NOT_CERTIFIED`, `‖x‖ → 11.0` |
| N2.2 | search **without** `trace(P) = 1` | scaling-degenerate: `‖P‖_F = inf`, `J = −6.3e+307` |
| N2.3 | un-normalised `θ` (sum 1.5) | rejected |
| N2.4 | one zero eigenvalue | `J = 0`, reported `MARGINAL`, not `CERTIFIED` |
| N2.5 | inconsistent `A_k` dimensions | rejected |

N2.2 is the direct evidence for the review's correction: without the trace normalisation the
"certificate" is meaningless, and the test shows the failure mode rather than hiding it.

## 4. Fidelity and limits

- **[ORIGINAL]** for the LPV construction, the GMR scheduling density and the Lyapunov condition.
- The search is a **penalty/heuristic** over `P`, not an SDP solver. It certifies when it finds a
  `P` with a strictly negative margin, and it reports the margin it found. It never claims the LMI
  is infeasible.
- Limit: the `A_k` families are constructed here (ADAPTATION of *structure*, not of *data*). No
  claim is made about the paper's 7-DOF KUKA models.
