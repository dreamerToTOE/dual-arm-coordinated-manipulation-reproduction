# P5-T07 POST — The 36-D dual-arm model: layout, calibration, Eq.(26) chain rule

**Status**: `PASS` — 12 checks (6 positive / 6 negative), 0 failed, 99.9 s.
**Run**: `p5/evidence/impl_checks/T07.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T07`)
**Code**: `p5/impl/p5core/svm_sca.py` **[ORIGINAL]** · **Task**: `p5/impl/tasks/t07_sca_36d.py`
**Figures**: `t07_gamma_hist.png`, `t07_decision_hist.png`, `t07_grad_check.png`

## 1. Data provenance (read-only, not vendored)

| File | sha256 | Content actually used |
|---|---|---|
| `models/cpsp_models/NewIIWASetup-Feb18-SparseModel.mat` | `9f217f51…4421` | 3000 BVs, `-g 3.3 ⇒ σ = 0.38925`, `bias = 0`, `alphay(3000)` |
| `models/NewSetup-IIWAs-Feb18/36D-24k-40deg-…-OptimalModel.mat` | `107d77ec…18d6` | `X_train(24892×36)`, `y_train` (13979 `+1` / 10913 `−1`), `y_est`, 7262 SVs, `rho`, `σ = 0.38815` |

`SCA-Boundary-Learning` carries **no licence**; the `.mat` files are read in place from the read-only
checkout (`P5_OFFICIAL_REF`) and only their sha256 is recorded. The task refuses to run if the
checkout is missing.

## 2. The strongest available independent reference

The full model's `y_est` is the paper's own decision output, and it is reproduced from
`(coef, SVs, bias, σ)` **exactly**:

> P7.2 — `sign(Γ_raw)` equals `sign(y_est)` on **24892 / 24892** points (1.0000)

Agreement with the stored `y_train` labels is **0.9874**, i.e. the labels themselves are the noisy
quantity (the model fits its own labels at 98.7 %, which is what an `OptimalModel` with `C`-regularised
SVMs does at 24k samples). This is the check that makes the 36-D path trustworthy: the parameters were
transcribed by hand-reading `.mat` fields, and a single transposed matrix or a `rho` sign flip would
have collapsed the 1.0000.

## 3. Positive evidence

| Check | Content | Result |
|---|---|---|
| P7.1 | dims, SV counts, bias, σ derivation, constant columns | `D = 36` both; 3000 BVs / 7262 SVs; `bias_sparse = 0`; `σ_sparse = 1/√(2·3.3)` to 1e-9; **constant columns exactly `{0–5, 18–23}`** |
| P7.2 | `sign(Γ_raw)` vs official `y_est` / vs `y_train` | **1.0000** / 0.9874 |
| P7.3 | calibration invariants I1–I6 at `κ = 1`, `κ = 2` | I1 `0.0e+00`, I2 `1.0000`, I3 `0.0e+00`, I4 FD `6.5e-08`, I5 11085 flagged, I6 `κ=2` shifts `Γ` by 4.044 |
| P7.4 | Eq.(26) chain rule on `f = Aq + b`, `d_q = 6` | rel err **9.2e-08** at `κ = 1` and `9.2e-08` at `κ = 2` (incl. the `1/κ` factor) |
| P7.5 | sparse CPSP model on the full model's training set | ACC **0.9313** (95 % CI 0.927–0.934), TPR 0.9262, FPR 0.0620 |
| P7.6 | evaluation cost | 389 µs single-point, 799 µs/point batched (NumPy) |

### Why the calibration map is `Γ_cal = 1 + Γ_raw/κ`, not a statistic

The review's Q4/G0 item is honoured literally: `κ ≡ 1` was frozen **before** any metric was looked
at, and `Γ_raw = 0 ⟺ Γ_cal = 1` for **every** `κ > 0`. That means the boundary condition constrains
`κ` not at all — so the "median calibrated value equals 1" criterion that the plan originally carried
was circular and is **not used**. Instead the six algebraic invariants are asserted, and `κ = 2` is
used solely to expose the `1/κ` factor in the gradient (I3, N7.4). The consequence is stated plainly:
**the paper's calibrated `Γ` has no data-derived scale in this reproduction**, and T08 is therefore
constructed so that its conclusions do not depend on the numerical value of `κ`.

### Eq.(26) has no upstream implementation

There is no DH geometry published for the 12-DOF dual arm, so the chain rule cannot be verified
against the paper's own feature map. P7.4 verifies the **derivative chain itself** on an explicit
affine map `f = Aq + b` (36 × 6, `A` random full rank): `∂Γ/∂q = Aᵀ ∇_f Γ`, checked against central
differences at 9.2e-08 for both `κ`. This proves the chain rule is implemented correctly; it does
**not** claim the feature map matches the paper's kinematics. That gap is carried into T08 as an
explicit adaptation.

## 4. Negative controls

| Check | Mutation | Result |
|---|---|---|
| N7.1 | feed `Γ_raw` into `log(Γ−1)` without calibration | **11085** points outside the domain → NaN unless the paper's `−1000` fallback is applied; counted, never silently propagated |
| N7.2 | permute the 36 unnamed columns | constant triples move (caught by P7.1's column check); `y_est` agreement 1.0000 → **0.5547** |
| N7.3 | read `-g 3.3` as the RBF **width** (`σ = 3.3`) | agreement 1.0000 → **0.5670** |
| N7.4 | `κ = 2` with the `1/κ` factor omitted | gradient error **13.717** → I3 fails by a factor of two |
| N7.5 | assert `Γ_cal == Γ_raw` at `κ = 2` | false by up to **4.044** — the map is not the identity once `κ ≠ 1` |
| N7.6 | all-zero feature vector | finite `Γ_raw = 3.5749` (the bias), no 0/0 in the kernel path |

### A correction made during G2, and why it matters

N7.3 was **first written** to swap the two published sigmas (`0.38925` vs `0.38815`) and assert that
this "destroys" the decision function. It failed: the swapped model still agrees with `y_est` at
**0.9992**. The two sigmas differ by **0.28 %** and are numerically interchangeable.

That is a finding, not a broken test, and the response was to report it rather than to loosen the
threshold:

- the swap is now a **metric** (`agree_sigma_swapped = 0.9992`, `sigma_relative_difference = 2.8e-3`);
- N7.3 injects the defect that is actually harmful — treating `-g` as the width — which drops the
  agreement to 0.5670;
- the code still refuses to cross-wire the two models, but now for the honest reason: **provenance**,
  not accuracy. `docs/DECISIONS.md` D013 records this.

Had the threshold simply been relaxed to `< 0.9993`, the ledger would have claimed a sensitivity that
the model does not have.

## 5. Fidelity and limits

- **[ORIGINAL]**: both models, all hyper-parameters, the 24892-point evaluation set and the `y_est`
  reference are the published artefacts, unmodified.
- **Evaluation label**: every metric is `IN_SAMPLE_INDEPENDENT_EVALUATION` (D008). `X_train` is the
  model's own training set and the paper's FPR/TPR come from a different split of a different
  dataset, so **no "within 1 pp of the paper" claim is made anywhere**.
- **Missing artefact**: the SVM *training* set was never published, so the model is not retrained and
  Eq.(28) (CPSP sparsification) is not reproduced end-to-end — only the shipped sparse model is
  evaluated (ACC 0.9313 vs the full model's 1.0000 on the same points).
- **Cost**: 389 µs/point in NumPy is within an order of magnitude of the paper's 2 ms budget, but the
  paper's C implementation is not reproduced; no real-time claim is transferred to T10.
- **Decision boundary semantics**: the shipped CPSP model has `bias = 0`, so its boundary is
  `Γ_raw = 0`; `Γ = 1` is the *calibrated* image (T06 §5 says the same thing for the 2-D case).
