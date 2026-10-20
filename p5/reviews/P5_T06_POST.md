# P5-T06 POST — The learned SCA boundary in 2D: Eq.(24) and Eq.(25)

**Status**: `PASS` — 10 checks (6 positive / 4 negative), 0 failed, 0.8 s.
**Run**: `p5/evidence/impl_checks/T06.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T06`)
**Code**: `p5/impl/p5core/svm_sca.py` **[ORIGINAL]** · **Task**: `p5/impl/tasks/t06_sca_2d.py`
**Figures**: `t06_gamma_contour.png`, `t06_grad_field.png`, `t06_grad_error.png`

## 1. Data provenance (read-only, not vendored)

| File | sha256 | Content actually used |
|---|---|---|
| `models/cpsp_models/2d_example.mat` | `4e9efd5f85a34523…` | `gamma=50 ⇒ σ=0.1`, `Nbvs=40`, `bias=0`, `alphay(40)`, `BVs(40×2)` |
| `data/2d-example2.mat` | `12f7a81071469030…` | `X(863×2)`, `labels` (−1:480 / +1:383), full libsvm model (`totalSV=40`, `rho=0.96269`, `σ=0.1`, `C=100`) |

`SCA-Boundary-Learning` carries **no licence**, so the `.mat` files are read in place from a
read-only checkout (`P5_OFFICIAL_REF`, default `/home/ubuntu2004/lmy/p5-official-ref/SCA-Boundary-Learning`)
and only their sha256 is recorded. The task refuses to run if the checkout is missing rather than
silently skipping.

## 2. Why the FD test alone would have been worthless

"Analytic gradient equals its own finite difference" is self-consistency. A wrong `σ` makes both
agree, so P6.1 is kept but is explicitly labelled as such — and the figure `t06_grad_error.png`
plots the `σ = 50` gradient error against the `σ = 0.1` one to show that the FD check cannot tell
them apart. The independent evidence is P6.2/N6.1: the **labels** come from a geometric threshold
and know nothing about this implementation.

## 3. Positive evidence

| Check | Content | Result |
|---|---|---|
| P6.1 | (25) vs central difference at all 40 BVs | rel err 6.2e-11 (self-consistency only) |
| P6.2 | `sign(Γ_raw)` vs official labels (863 points) | **0.9930** |
| P6.3 | `+∇Γ` raises `Γ` | 400 / 400 interior points |
| P6.4 | `K(f_n,f_n) = 1`; libsvm decision vs the same labels | 0.0; **0.9977**; mutual sign agreement 0.9954 |
| P6.5 | zero-set Hausdorff between the two distinct models | 0.3770 (recorded); `corr = 0.9646` |
| P6.6 | shipped model has `bias = 0` ⇒ dropping bias is a no-op | Δ = **exactly 0** |

P6.6 is a *positive* test on purpose: it states that a bias-drop experiment on the shipped CPSP model
would be vacuous, which is why N6.3 uses a different fixture.

## 4. Negative / mutation evidence

| Check | Content | Result |
|---|---|---|
| N6.1 | `σ = 50` (reading `-g` as `σ`) | agreement 0.9930 → **0.5562** |
| N6.2 | keep only 10 of 40 BVs | zero-set Hausdorff **0.7024** |
| N6.3 | non-zero-bias fixture (libsvm, `bias = −0.9627`), drop the bias | ΔΓ = 0.9627 = `|bias|`, Hausdorff 0.3097 |
| N6.4 | write `(f_n − f)` in (25) | ascent test succeeds at **0/400** points → P6.3 would fail |

## 5. Fidelity and limits

- **[ORIGINAL]**: model, parameters and evaluation points are the published ones; the only translation
  is `.mat` field → `(coef, SVs, bias, σ)`.
- The 863 labelled points are **not** the paper's test set, the model is **not** retrained (the
  training set was never published), and **no FPR/TPR of the paper is claimed** (`docs/DECISIONS.md` D008).
- Boundary semantics: the shipped CPSP model has `bias = 0`, so its boundary is `Γ_raw = 0`. The
  paper's `Γ = 1` requires the calibrated quantity of T07; this task therefore always writes
  `Γ_raw = 0` and never `Γ = 1`.
- Limit: this is a 2-D toy model. Its conclusions do not transfer to the 36-D case; that is T07.
