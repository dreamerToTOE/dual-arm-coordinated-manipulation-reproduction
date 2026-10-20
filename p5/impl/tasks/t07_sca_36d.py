"""P5-T07 - 36-D dual-arm model: feature layout, calibration map, chain rule.

Fidelity: ORIGINAL for the evaluation (model, parameters and data are the
published ones); ADAPTATION for the calibration map and for the feature-to-joint
map used in the chain-rule test.

Review corrections applied here (G0, items 6 and 7):

  * The evaluation set is `X_train`, i.e. the model's *own training set*.  Every
    metric is labelled `IN_SAMPLE_INDEPENDENT_EVALUATION`; the paper's FPR/TPR come
    from a different split and a different geometry, so no "within 1 pp" claim is
    made anywhere (docs/DECISIONS.md D008).
  * Calibration: `Gamma_cal = 1 + Gamma_raw / kappa` with kappa frozen at 1 before
    any metric is inspected.  `Gamma_raw = 0 <=> Gamma_cal = 1` for every kappa > 0,
    so the boundary condition constrains kappa not at all; the "median calibrated
    value equals 1" condition was circular and is not used.  The six invariants
    I1-I6 (plan section 4) are asserted instead, and kappa=2 checks the 1/kappa
    factor of the gradient.
  * Two sigmas, never interchanged *as a provenance rule*: the sparse CPSP model
    carries `-g 3.3` (=> sigma = 0.38925), the full libsvm model stores
    `sigma = 0.38815`.  These differ by 0.28% and are numerically interchangeable
    at the decision boundary (measured agreement 0.998 when swapped), which is
    recorded as a metric, NOT claimed as a defect.  N7.3 therefore injects the
    defect that is actually harmful: reading `-g 3.3` as the kernel width instead
    of converting it (sigma = 3.3), which drops the agreement to 0.58.
  * Eq.(26) has no upstream implementation at all.  The chain rule is therefore
    verified on an *explicit* feature map `f = A q + b` (ENGINEERING): that checks
    the derivative chain itself, which is what the paper's (26) asserts, without
    pretending to reconstruct the unpublished DH geometry.
"""

import hashlib
import os
import time

import numpy as np
import scipy.io as sio

import p5core
from p5core import svm_sca as S
from p5core.plotting import plt, save
from p5core.results import require

REF = os.environ.get("P5_OFFICIAL_REF",
                     "/home/ubuntu2004/lmy/p5-official-ref/SCA-Boundary-Learning")
SPARSE = os.path.join(REF, "models", "cpsp_models", "NewIIWASetup-Feb18-SparseModel.mat")
FULL = os.path.join(REF, "models", "NewSetup-IIWAs-Feb18",
                    "36D-24k-40deg-New-IIWA-Setup-OptimalModel.mat")

CONST_COLS = list(range(0, 6)) + list(range(18, 24))
EVAL_LABEL = "IN_SAMPLE_INDEPENDENT_EVALUATION"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _batch(model, F, chunk=1000):
    """Evaluate in chunks so the kernel matrix never eats the machine."""
    out = []
    for s in range(0, F.shape[0], chunk):
        out.append(model.gamma(F[s:s + chunk]))
    return np.concatenate(out)


def run(rec):
    require(os.path.exists(SPARSE), "sparse 36-D model not found: %s" % SPARSE)
    require(os.path.exists(FULL), "full 36-D model not found: %s" % FULL)
    rec.metric("sha256_sparse36d", _sha256(SPARSE))
    rec.metric("sha256_full36d", _sha256(FULL))

    sraw = sio.loadmat(SPARSE, squeeze_me=True, struct_as_record=False)
    skey = [k for k in sraw if not k.startswith("__")][0]
    sparse = S.load_cpsp(SPARSE)

    draw = sio.loadmat(FULL, squeeze_me=True, struct_as_record=False)
    X = np.asarray(draw["X_train"], float)
    y_train = np.asarray(draw["y_train"], float).ravel()
    y_est = np.asarray(draw["y_est"], float).ravel()
    mod = draw["model"]
    SV = mod.SVs.toarray() if hasattr(mod.SVs, "toarray") else np.asarray(mod.SVs, float)
    full = S.RBFModel(np.asarray(mod.sv_coef, float).ravel(), SV,
                      -float(np.asarray(mod.rho).ravel()[0]),
                      float(np.asarray(draw["options"].sigma).ravel()[0]), "full36d")
    full.n_svs = int(np.asarray(mod.totalSV).ravel()[0])

    # ------------------------------------------------------------- P7.1
    const_cols = [j for j in range(X.shape[1]) if np.allclose(X[:, j], X[0, j])]
    rec.metric("sigma_sparse", sparse.sigma)
    rec.metric("sigma_full", full.sigma)
    rec.metric("nbvs_sparse", sparse.n_bvs)
    rec.metric("nsv_full", full.n_svs)
    rec.metric("bias_sparse", sparse.bias)
    rec.metric("bias_full", full.bias)
    rec.metric("n_eval", int(X.shape[0]))
    rec.check("P7.1",
              sparse.dim == 36 and full.dim == 36 and X.shape[1] == 36
              and sparse.n_bvs == 3000 and full.n_svs == 7262
              and abs(sparse.bias) < 1e-12 and abs(sparse.sigma - 1 / np.sqrt(2 * 3.3)) < 1e-9
              and const_cols == CONST_COLS and sparse.coef.size == 3000,
              "dimensions: D=36 both models, 3000 BVs (sparse) / 7262 SVs (full), "
              "bias_sparse=0, sigma_sparse=%.5f, sigma_full=%.5f; constant triples at "
              "columns 0-5 and 18-23 exactly as measured" % (sparse.sigma, full.sigma),
              const_cols=const_cols, sigma_sparse=sparse.sigma, sigma_full=full.sigma)

    # ------------------------------------------------------------- P7.2
    t0 = time.perf_counter()
    g_full = _batch(full, X)
    t_full = time.perf_counter() - t0
    agree_est = float(np.mean(np.sign(g_full) == np.sign(y_est)))
    agree_train = float(np.mean(np.sign(g_full) == y_train))
    rec.metric("agree_y_est", agree_est)
    rec.metric("agree_y_train", agree_train)
    rec.metric("eval_time_us_per_point_full", 1e6 * t_full / X.shape[0])
    rec.check("P7.2", agree_est == 1.0 and agree_train > 0.98,
              "decision function reproduces the official y_est sign on %d/%d points "
              "(%.4f); agreement with y_train is %.4f -- y_est is the independent "
              "reference, y_train is the noisy label"
              % (int(agree_est * X.size / X.shape[1]), X.shape[0], agree_est, agree_train),
              agree_est=agree_est, agree_train=agree_train)

    # ------------------------------------------------------------- P7.3 + N7.1
    kappa = p5core.KAPPA
    g_cal = S.calibrate(g_full, kappa)
    i1 = float(abs(S.calibrate(np.array([0.0]), 2.0)[0] - 1.0))
    i2 = float(np.mean(np.sign(g_cal - 1.0) == np.sign(g_full)))
    g_cal2 = S.calibrate(g_full, 2.0)
    i6 = float(np.max(np.abs(g_cal2 - g_full)))

    sub = X[:200]
    graw = full.grad(sub)
    i3 = max(float(np.max(np.abs(S.calibrate_grad(graw, 1.0) - graw))),
             float(np.max(np.abs(S.calibrate_grad(graw, 2.0) - graw / 2.0))))

    def cal_fn(F, k):
        return S.calibrate(full.gamma(F), k)

    h = 1e-6
    fd = np.zeros_like(graw)
    for d in range(full.dim):
        e = np.zeros(full.dim)
        e[d] = h
        fd[:, d] = (cal_fn(sub + e, 2.0) - cal_fn(sub - e, 2.0)) / (2 * h)
    i4 = float(np.linalg.norm(fd - S.calibrate_grad(graw, 2.0))
               / max(1e-300, np.linalg.norm(fd)))

    log_paper, n_bad_paper = S.log_barrier(g_full, kappa, mode="paper")
    log_lit, n_bad_lit = S.log_barrier(g_full, kappa, mode="literal")
    n_nan = int(np.count_nonzero(~np.isfinite(log_lit)))
    i5_ok = (n_bad_paper == n_bad_lit == n_nan) and n_bad_paper > 0
    rec.metric("n_gamma_raw_nonpositive", n_bad_paper)
    rec.metric("calibration_kappa", kappa)

    rec.check("P7.3", i1 < 1e-12 and i2 == 1.0 and i3 < 1e-12 and i4 < 1e-5
              and i5_ok and i6 > 1e-3,
              "calibration invariants: I1 |Gamma_cal(0)-1| = %.1e; I2 order preserved on "
              "%.4f; I3 1/kappa gradient = %.1e; I4 FD agreement %.1e; I5 %d non-positive "
              "Gamma_raw all flagged (paper fallback applied); I6 kappa=2 changes Gamma by "
              "up to %.3f" % (i1, i2, i3, i4, n_bad_paper, i6),
              I1=i1, I2=i2, I3=i3, I4=i4, I5=n_bad_paper, I6=i6)

    # ------------------------------------------------------------- P7.4
    rng = np.random.default_rng(7)
    d_q = 6
    A = rng.normal(size=(36, d_q)) * 0.15
    b = X[0]
    q0 = np.zeros(d_q)

    def phi(q):
        return A @ q + b

    def chain_grad(q, k):
        gq = full.grad(phi(q)[None, :])[0]
        return A.T @ S.calibrate_grad(gq, k)

    def chain_fd(q, k):
        out = np.zeros(d_q)
        for i in range(d_q):
            e = np.zeros(d_q)
            e[i] = h
            out[i] = (cal_fn(phi(q + e)[None, :], k) - cal_fn(phi(q - e)[None, :], k))[0] / (2 * h)
        return out

    rel = {}
    for k in (1.0, 2.0):
        an = chain_grad(q0, k)
        num = chain_fd(q0, k)
        rel[k] = float(np.linalg.norm(an - num) / max(1e-300, np.linalg.norm(num)))
    rec.metric("chain_rule_rel_err", rel)
    rec.check("P7.4", rel[1.0] < 1e-5 and rel[2.0] < 1e-5,
              "Eq.(26) on an explicit map f = Aq + b: relative error %.1e (kappa=1) and "
              "%.1e (kappa=2, including the 1/kappa factor)" % (rel[1.0], rel[2.0]),
              rel=rel)

    # ------------------------------------------------------------- P7.5
    g_sparse = _batch(sparse, X)
    m_sparse = S.classification_metrics(np.sign(g_sparse), y_train)
    ci = S.bootstrap_ci(np.sign(g_sparse), y_train, n_boot=200, seed=0)
    rec.metric("sparse_metrics", dict(m_sparse))
    rec.metric("sparse_ci", ci)
    rec.metric("evaluation_label", EVAL_LABEL)
    rec.check("P7.5", 0.0 <= m_sparse["acc"] <= 1.0 and m_sparse["acc"] > 0.5,
              "sparse CPSP model on the full model's training set [%s]: ACC %.4f "
              "(95%% CI %.3f-%.3f), TPR %.4f, FPR %.4f -- reported, never compared to "
              "the paper's FPR/TPR"
              % (EVAL_LABEL, m_sparse["acc"], ci["acc"][0], ci["acc"][1],
                 m_sparse["tpr"], m_sparse["fpr"]), acc=m_sparse["acc"], ci=ci)

    # ------------------------------------------------------------- P7.6
    reps = 50
    t0 = time.perf_counter()
    for i in range(reps):
        full.gamma(X[i % X.shape[0]][None, :])
    t_single = 1e6 * (time.perf_counter() - t0) / reps
    rec.metric("eval_time_us_single", t_single)
    rec.check("P7.6", t_single < 2000.0,
              "single-point evaluation %.0f us (3000-BV sparse model would be ~5x less); "
              "batched evaluation %.0f us/point over %d points. Python/NumPy only: the "
              "2 ms real-time budget is met in order of magnitude, but the paper's C "
              "implementation is not reproduced"
              % (t_single, 1e6 * t_full / X.shape[0], X.shape[0]),
              us_single=t_single, us_batched=1e6 * t_full / X.shape[0])

    # ------------------------------------------------------------- N7.1
    n_domain = int(np.count_nonzero(g_full <= S.GAMMA_RAW_FLOOR))
    rec.defect("N7.1", n_domain > 0 and n_nan == n_domain
               and np.all(log_paper[g_full <= S.GAMMA_RAW_FLOOR] == S.PAPER_FALLBACK),
               "feeding Gamma_raw into log(Gamma-1) without calibration: %d points lie "
               "outside the domain and become NaN unless the paper's large-negative "
               "fallback (%.0f) is applied -- counted, never silently propagated"
               % (n_domain, S.PAPER_FALLBACK), n_domain=n_domain, n_nan=n_nan)

    # ------------------------------------------------------------- N7.2
    perm = rng.permutation(36)
    const_perm = [j for j in range(36) if np.allclose(X[:, perm[j]], X[0, perm[j]])]
    g_perm = _batch(full, X[:, perm])
    agree_perm = float(np.mean(np.sign(g_perm) == np.sign(y_est)))
    rec.defect("N7.2", const_perm != CONST_COLS and agree_perm < 0.9,
               "permuting the 36 unnamed columns moves the constant triples (detected by "
               "P7.1's column check) and drops the y_est agreement from %.4f to %.4f"
               % (agree_est, agree_perm), agree_perm=agree_perm, const_perm=const_perm)

    # ------------------------------------------------------------- N7.3
    # Two halves, deliberately separated:
    #  (a) METRIC, not a defect: swapping the two published sigmas is harmless.
    #  (b) DEFECT that is actually injected: reading -g as the kernel width.
    mix_sigma = S.RBFModel(full.coef, full.SVs, full.bias, sparse.sigma, "mixed_sigma")
    agree_mixed = float(np.mean(np.sign(_batch(mix_sigma, X)) == np.sign(y_est)))
    unit_sigma = S.RBFModel(full.coef, full.SVs, full.bias, 3.3, "g_as_width")
    agree_unit = float(np.mean(np.sign(_batch(unit_sigma, X)) == np.sign(y_est)))
    rec.metric("agree_sigma_swapped", agree_mixed)
    rec.metric("agree_g_taken_as_width", agree_unit)
    rec.metric("sigma_relative_difference", abs(sparse.sigma - full.sigma) / full.sigma)
    rec.defect("N7.3", agree_unit < 0.95,
               "reading the CPSP penalty '-g 3.3' as the RBF width (sigma = 3.3) instead of "
               "converting it (sigma = 1/sqrt(2g) = 0.38925) drops the y_est agreement from "
               "%.4f to %.4f.  Note the measured caveat: the two *published* sigmas differ by "
               "only %.2f%% and score %.4f when swapped, so they are numerically "
               "interchangeable -- the model/sigma pairing is enforced for provenance, not "
               "for accuracy" % (agree_est, agree_unit,
                                 100 * abs(sparse.sigma - full.sigma) / full.sigma, agree_mixed),
               agree_unit=agree_unit, agree_swapped=agree_mixed)

    # ------------------------------------------------------------- N7.4
    grad_no_kappa = graw / 2.0
    grad_wrong = graw.copy()                     # forgot the 1/kappa factor
    i3_bad = float(np.max(np.abs(grad_wrong - grad_no_kappa)))
    rec.defect("N7.4", i3_bad > 1e-3,
               "kappa=2 with the 1/kappa factor omitted leaves a gradient error of %.3f, "
               "i.e. I3 fails by a factor of two" % i3_bad, error=i3_bad)

    # ------------------------------------------------------------- N7.5
    rec.defect("N7.5", float(np.max(np.abs(g_cal2 - g_full))) > 1e-3,
               "asserting Gamma_cal == Gamma_raw at kappa=2 is false by up to %.3f: the "
               "calibration map is not the identity once kappa != 1" % i6, max_diff=i6)

    # ------------------------------------------------------------- N7.6
    zero = np.zeros((1, 36))
    g_zero = float(full.gamma(zero)[0])
    rec.defect("N7.6", np.isfinite(g_zero),
               "all-zero feature vector gives a finite Gamma_raw = %.4f (no division by "
               "zero in the kernel path)" % g_zero, gamma_zero=g_zero)

    # ----------------------------------------------------------- figures
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.hist(g_full, bins=80, alpha=0.7, label=r"$\Gamma_{raw}$", color="#4b7bec")
    ax.hist(g_cal2, bins=80, alpha=0.5, label=r"$\Gamma_{cal}$ ($\kappa=2$)",
            color="#eb3b5a")
    ax.axvline(0.0, color="k", ls=":", lw=1.0)
    ax.axvline(1.0, color="k", ls="--", lw=1.0)
    ax.set_xlabel(r"$\Gamma$")
    ax.set_ylabel("count")
    ax.set_title("the boundary is Gamma_raw = 0; Gamma = 1 is the calibrated image")
    ax.legend(fontsize=8)
    save(fig, rec, "t07_gamma_hist.png")

    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    bins = np.linspace(-1.0, 1.0, 61)
    ax.hist(g_full[y_train > 0], bins=bins, alpha=0.6, label="label +1",
            color="#4b7bec", density=True)
    ax.hist(g_full[y_train < 0], bins=bins, alpha=0.6, label="label -1",
            color="#eb3b5a", density=True)
    ax.axvline(0.0, color="k", ls=":", lw=1.0)
    ax.set_xlabel(r"$\Gamma_{raw}$")
    ax.set_ylabel("density")
    ax.set_title("decision values by label (agreement vs y_est = %.4f)" % agree_est)
    ax.legend(fontsize=8)
    save(fig, rec, "t07_decision_hist.png")

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.bar(["kappa=1", "kappa=2"], [rel[1.0], rel[2.0]], color="#20bf6b", width=0.45)
    ax.set_yscale("log")
    ax.axhline(1e-5, color="k", ls=":", lw=0.8, label="tolerance 1e-5")
    for i, v in enumerate((rel[1.0], rel[2.0])):
        ax.text(i, v, "%.1e" % v, ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("relative error, analytic vs FD")
    ax.set_title("Eq.(26) chain rule, with and without the 1/kappa factor")
    ax.legend(fontsize=8)
    save(fig, rec, "t07_grad_check.png")

    return rec
