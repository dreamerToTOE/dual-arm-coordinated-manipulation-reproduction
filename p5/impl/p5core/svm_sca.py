"""Learned SCA boundary: Eq.(24) decision function, Eq.(25) gradient, calibration.

    Gamma(f) = sum_n c_n exp(-||f - f_n||^2 / (2 sigma^2)) + b          (24)
    grad_f Gamma = -(1/sigma^2) sum_n c_n exp(...) (f - f_n)            (25)

`-g` in libsvm is lambda = 1/(2 sigma^2), **not** sigma.  For the shipped models:

    2d_example.mat      gamma = 50  -> sigma = 0.1
    *SparseModel.mat    gamma = 3.3 -> sigma = 0.38924
    36D-24k full model  stored sigma = 0.38815 (lambda = 3.3197)

The shipped CPSP models carry bias = 0, so their decision boundary is
Gamma_raw = 0.  The paper's Gamma = 1 boundary needs the calibrated quantity
Gamma_cal = 1 + Gamma_raw / KAPPA (ADAPTATION, see docs/DECISIONS.md D007).
Because Gamma_raw = 0 <=> Gamma_cal = 1 for *every* KAPPA > 0, the boundary
condition constrains nothing; KAPPA is frozen at 1 before any metric is inspected.

Log domain: log(Gamma_cal - 1) = log(Gamma_raw / KAPPA).  For Gamma_raw <= 0 this
is undefined.  The paper's own remedy (p.1215) is to replace it with "a large
negative number that pushes the robots outward towards the boundary"; that is
implemented as PAPER_FALLBACK and is reported separately from the literal form.
"""

import numpy as np
import scipy.io as sio
import scipy.sparse as sp

KAPPA = 1.0
GAMMA_RAW_FLOOR = 1e-9       # below this the literal log is treated as out of domain
PAPER_FALLBACK = -1.0e3      # the paper's "large negative number"


# --------------------------------------------------------------- models
class RBFModel:
    """Decision function of a two-class RBF-SVM given (coef, SVs, bias, sigma)."""

    def __init__(self, coef, SVs, bias, sigma, name=""):
        self.coef = np.asarray(coef, float).ravel()
        self.SVs = np.asarray(SVs, float)
        self.bias = float(bias)
        self.sigma = float(sigma)
        self.name = name
        if self.SVs.shape[0] != self.coef.size:
            raise ValueError("coef/SVs mismatch: %d vs %d" % (self.coef.size, self.SVs.shape[0]))

    @property
    def lam(self):
        return 1.0 / (2.0 * self.sigma ** 2)

    @property
    def dim(self):
        return self.SVs.shape[1]

    # ------------------------------------------------------------- (24)
    def _kernel(self, F, chunk=2000):
        F = np.atleast_2d(np.asarray(F, float))
        out = np.empty((F.shape[0], self.SVs.shape[0]))
        for s in range(0, F.shape[0], chunk):
            Fi = F[s:s + chunk]
            d2 = ((Fi[:, None, :] - self.SVs[None, :, :]) ** 2).sum(-1)
            out[s:s + chunk] = np.exp(-self.lam * d2)
        return out

    def gamma(self, F):
        F = np.atleast_2d(np.asarray(F, float))
        return self._kernel(F) @ self.coef + self.bias

    # ------------------------------------------------------------- (25)
    def grad(self, F, chunk=2000):
        """grad_f Gamma, shape (N, dim).  -2*lam*[(K c) f - K (c * SVs)]."""
        F = np.atleast_2d(np.asarray(F, float))
        G = np.empty((F.shape[0], self.dim))
        cSV = self.coef[:, None] * self.SVs
        for s in range(0, F.shape[0], chunk):
            Fi = F[s:s + chunk]
            K = self._kernel(Fi)
            Kc = K @ self.coef
            G[s:s + chunk] = -2.0 * self.lam * (Kc[:, None] * Fi - K @ cSV)
        return G


def load_cpsp(path, name=None):
    """Load one of the CPSP `.mat` models published with SCA-Boundary-Learning."""
    d = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
    key = [k for k in d if not k.startswith("__")][0]
    m = d[key]
    gamma_param = float(np.asarray(m.gamma).ravel()[0])
    sigma = 1.0 / np.sqrt(2.0 * gamma_param)
    model = RBFModel(np.asarray(m.alphay, float).ravel(), np.asarray(m.BVs, float),
                     float(np.asarray(m.bias).ravel()[0]), sigma, name=name or path)
    model.n_bvs = int(np.asarray(m.Nbvs).ravel()[0])
    model.gamma_param = gamma_param
    return model


def load_libsvm(path, name=None):
    """Load a libsvm-style struct: decision = sum(coef*K) - rho."""
    d = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
    mod = d["model"]
    SV = mod.SVs
    if sp.issparse(SV):
        SV = SV.toarray()
    SV = np.asarray(SV, float)
    coef = np.asarray(mod.sv_coef, float).ravel()
    rho = float(np.asarray(mod.rho).ravel()[0])
    sigma = float(np.asarray(d["options"].sigma).ravel()[0]) if "options" in d else None
    if sigma is None:
        raise ValueError("no sigma in %s" % path)
    return RBFModel(coef, SV, -rho, sigma, name=name or path)


# ---------------------------------------------------------- calibration
def calibrate(gamma_raw, kappa=KAPPA):
    """Gamma_cal = 1 + Gamma_raw / kappa  (ADAPTATION)."""
    if kappa <= 0:
        raise ValueError("kappa must be positive")
    return 1.0 + np.asarray(gamma_raw, float) / float(kappa)


def calibrate_grad(grad_raw, kappa=KAPPA):
    """The calibrated gradient carries a 1/kappa factor."""
    if kappa <= 0:
        raise ValueError("kappa must be positive")
    return np.asarray(grad_raw, float) / float(kappa)


def log_barrier(gamma_raw, kappa=KAPPA, mode="paper"):
    """log(Gamma_cal - 1) with explicit handling of the out-of-domain branch.

    mode="paper"   : Gamma_raw <= 0 -> PAPER_FALLBACK (large negative number)
    mode="literal" : Gamma_raw <= 0 -> nan   (used by the negative control N7.1)

    Returns (value, n_domain_violations).
    """
    g = np.asarray(gamma_raw, float)
    bad = g <= GAMMA_RAW_FLOOR
    n_bad = int(np.count_nonzero(bad))
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.log(g / float(kappa))
    if mode == "literal":
        val = np.where(bad, np.nan, val)
    elif mode == "paper":
        val = np.where(bad, PAPER_FALLBACK, val)
    else:
        raise ValueError("mode must be 'paper' or 'literal'")
    return val, n_bad


# ------------------------------------------------------------- metrics
def classification_metrics(pred_sign, y_true):
    """ACC / TPR(+) / FPR(-).  Positive class is +1 (the boundary band)."""
    pred_sign = np.asarray(pred_sign, float).ravel()
    y = np.asarray(y_true, float).ravel()
    pos = y > 0
    neg = ~pos
    tp = int(np.sum((pred_sign > 0) & pos))
    fn = int(np.sum((pred_sign <= 0) & pos))
    fp = int(np.sum((pred_sign > 0) & neg))
    tn = int(np.sum((pred_sign <= 0) & neg))
    acc = (tp + tn) / max(1, y.size)
    tpr = tp / max(1, tp + fn)
    fpr = fp / max(1, fp + tn)
    return {"acc": acc, "tpr": tpr, "fpr": fpr, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "n": int(y.size)}


def bootstrap_ci(pred_sign, y_true, n_boot=400, seed=0):
    """Percentile bootstrap over samples for ACC/TPR/FPR."""
    pred_sign = np.asarray(pred_sign, float).ravel()
    y = np.asarray(y_true, float).ravel()
    rng = np.random.default_rng(seed)
    n = y.size
    accs, tprs, fprs = [], [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        m = classification_metrics(pred_sign[idx], y[idx])
        accs.append(m["acc"]); tprs.append(m["tpr"]); fprs.append(m["fpr"])
    q = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    return {"acc": q(accs), "tpr": q(tprs), "fpr": q(fprs)}
