"""P5-T06 - learned SCA boundary in 2D: Eq.(24) decision function, Eq.(25) gradient.

Fidelity: ORIGINAL.  The model, its parameters and the evaluation points all come
from the material published with `nbfigueroa/SCA-Boundary-Learning`; the only
"translation" is `.mat` field -> (coef, SVs, bias, sigma).  The repository carries
no licence, so the `.mat` files are read in place and only their sha256 is
recorded -- nothing is copied into this repository.

What this task can and cannot prove (review G0, item 6):

  * "analytic gradient == its own finite difference" is self-consistency only: a
    wrong sigma makes both agree.  It is kept as P6.1 but the *independent*
    evidence is P6.2/N6.1, where the sign of Gamma_raw is compared against the
    official labels, which were produced by a geometric threshold and do not
    know anything about our implementation.
  * `-g` in the shipped models is lambda = 1/(2 sigma^2), not sigma.  sigma = 0.1
    for `2d_example.mat`.  N6.1 evaluates the same model with sigma = 50 to show
    what that misreading costs.
  * The shipped CPSP model has bias = 0, so its zero set is Gamma_raw = 0 and
    dropping the bias is a no-op.  A bias-drop test on that model is therefore
    vacuous; P6.6 states that as a *positive* fact and N6.3 uses the libsvm model
    (bias = -rho = -0.9627) as the fixture that can actually detect the defect.
  * No FPR/TPR of the paper is claimed here.  The 863 labelled points are not the
    paper's test set and the model is not retrained (the training set was never
    published).
"""

import hashlib
import os

import numpy as np
import scipy.io as sio

from p5core import svm_sca as S
from p5core.plotting import plt, save
from p5core.results import require

#: read-only checkout of nbfigueroa/SCA-Boundary-Learning (no licence: not vendored)
REF = os.environ.get("P5_OFFICIAL_REF",
                     "/home/ubuntu2004/lmy/p5-official-ref/SCA-Boundary-Learning")
CPSP = os.path.join(REF, "models", "cpsp_models", "2d_example.mat")
DATA = os.path.join(REF, "data", "2d-example2.mat")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _zero_set(model, lo=0.0, hi=1.0, n=241):
    """Zero level of Gamma_raw on a grid, as crossing points on grid edges."""
    xs = np.linspace(lo, hi, n)
    gx, gy = np.meshgrid(xs, xs)
    G = model.gamma(np.c_[gx.ravel(), gy.ravel()]).reshape(n, n)
    h = xs[1] - xs[0]
    pts = []
    for i in range(n):
        row = G[i]
        for j in np.where(np.sign(row[:-1]) * np.sign(row[1:]) < 0)[0]:
            frac = abs(row[j]) / (abs(row[j]) + abs(row[j + 1]))
            pts.append([xs[j] + h * frac, xs[i]])
    for j in range(n):
        col = G[:, j]
        for i in np.where(np.sign(col[:-1]) * np.sign(col[1:]) < 0)[0]:
            frac = abs(col[i]) / (abs(col[i]) + abs(col[i + 1]))
            pts.append([xs[j], xs[i] + h * frac])
    return np.array(pts) if pts else np.zeros((0, 2))


def _hausdorff(A, B):
    if len(A) == 0 or len(B) == 0:
        return float("inf")
    D = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
    return float(max(np.sqrt(D.min(1)).max(), np.sqrt(D.min(0)).max()))


def run(rec):
    require(os.path.exists(CPSP), "official CPSP model not found: %s\n"
            "set P5_OFFICIAL_REF to a read-only checkout of SCA-Boundary-Learning" % CPSP)
    require(os.path.exists(DATA), "official 2D dataset not found: %s" % DATA)

    rec.metric("sha256_2d_example", _sha256(CPSP))
    rec.metric("sha256_2d_example2", _sha256(DATA))

    model = S.load_cpsp(CPSP)
    lib = S.load_libsvm(DATA)
    raw = sio.loadmat(DATA, squeeze_me=True, struct_as_record=False)
    X = np.asarray(raw["X"], float)
    y = np.asarray(raw["labels"], float).ravel()

    rec.metric("sigma_cpsp", model.sigma)
    rec.metric("nbvs_cpsp", model.n_bvs)
    rec.metric("bias_cpsp", model.bias)
    rec.metric("sigma_libsvm", lib.sigma)
    rec.metric("bias_libsvm", lib.bias)
    rec.metric("n_points", int(y.size))
    rec.metric("n_pos", int(np.sum(y > 0)))
    rec.metric("n_neg", int(np.sum(y < 0)))

    # ------------------------------------------------------------- P6.1
    g_bv = model.gamma(model.SVs)
    G_an = model.grad(model.SVs)
    h = 1e-6
    G_fd = np.empty_like(G_an)
    for d in range(model.dim):
        e = np.zeros(model.dim)
        e[d] = h
        G_fd[:, d] = (model.gamma(model.SVs + e) - model.gamma(model.SVs - e)) / (2 * h)
    rel = float(np.linalg.norm(G_an - G_fd) / max(1e-300, np.linalg.norm(G_an)))
    rec.le("P6.1", rel, 1e-6,
           "analytic (25) vs central difference at all %d BVs: rel err %.2e "
           "(self-consistency only; a wrong sigma passes this too)"
           % (model.n_bvs, rel), rel_err=rel)

    # ------------------------------------------------------------- P6.2
    g_all = model.gamma(X)
    agree = float(np.mean(np.sign(g_all) == y))
    rec.metric("label_agreement_sigma0.1", agree)
    rec.check("P6.2", agree >= 0.95,
              "sign(Gamma_raw) vs official labels on %d points: %.4f "
              "(independent reference: labels come from geometry, not from us)"
              % (y.size, agree), agreement=agree)

    # ------------------------------------------------------------- P6.3
    rng = np.random.default_rng(0)
    F = rng.uniform(0.02, 0.98, size=(400, 2))
    grad = model.grad(F)
    norm = np.linalg.norm(grad, axis=1)
    ok_rows = norm > 1e-9
    step = 1e-4 * grad[ok_rows] / norm[ok_rows, None]
    up = model.gamma(F[ok_rows] + step) > model.gamma(F[ok_rows])
    frac_up = float(np.mean(up))
    rec.metric("grad_ascent_fraction", frac_up)
    rec.check("P6.3", frac_up == 1.0,
              "moving along +grad_gamma raises Gamma at %d/%d interior points: the "
              "gradient points to the free side" % (int(np.sum(up)), int(ok_rows.sum())),
              fraction=frac_up)

    # ------------------------------------------------------------- P6.4
    Kdiag = model._kernel(model.SVs)
    diag_err = float(np.max(np.abs(np.diag(Kdiag) - 1.0)))
    f_lib = lib.gamma(X)
    agree_lib = float(np.mean(np.sign(f_lib) == y))
    mutual = float(np.mean(np.sign(f_lib) == np.sign(g_all)))
    rec.check("P6.4", diag_err < 1e-12 and agree_lib >= 0.95 and mutual >= 0.95,
              "K(f_n,f_n)=1 to %.1e; libsvm decision vs the same labels %.4f; "
              "the two models agree on the sign at %.4f of the points"
              % (diag_err, agree_lib, mutual),
              diag_err=diag_err, libsvm_agreement=agree_lib, mutual_agreement=mutual)

    # ------------------------------------------------------------- P6.5
    zs_cpsp = _zero_set(model)
    zs_lib = _zero_set(lib)
    hd_cross = _hausdorff(zs_cpsp, zs_lib)
    corr = float(np.corrcoef(g_all, f_lib)[0, 1])
    rec.metric("hausdorff_zero_set", hd_cross)
    rec.metric("corr_cpsp_vs_libsvm", corr)
    rec.metric("n_zero_points_cpsp", int(len(zs_cpsp)))
    rec.check("P6.5", np.isfinite(hd_cross) and len(zs_cpsp) > 100 and 0.0 <= hd_cross < 0.75,
              "zero-set Hausdorff between the two distinct models: %.4f on the unit "
              "square, corr(Gamma_raw) = %.4f (recorded, not asserted to vanish -- "
              "these are two different SVM solutions of the same task)"
              % (hd_cross, corr), hausdorff=hd_cross, corr=corr)

    # ------------------------------------------------------------- P6.6
    nob = S.RBFModel(model.coef, model.SVs, 0.0, model.sigma, "cpsp_nobias")
    d_bias = float(np.max(np.abs(nob.gamma(X) - g_all)))
    rec.check("P6.6", d_bias == 0.0,
              "the shipped CPSP model has bias = 0, so dropping the bias changes "
              "Gamma by exactly %.1f -- a bias test on this model proves nothing"
              % d_bias, delta=d_bias)

    # ------------------------------------------------------------- N6.1
    trap = S.RBFModel(model.coef, model.SVs, model.bias, 50.0, "sigma_trap")
    g_trap = trap.gamma(X)
    agree_trap = float(np.mean(np.sign(g_trap) == y))
    rec.metric("label_agreement_sigma50", agree_trap)
    rec.defect("N6.1", agree_trap < 0.9,
               "reading -g = 50 as sigma (instead of lambda) drops the label "
               "agreement from %.4f to %.4f -- the unit trap is detected by an "
               "independent reference, not by self-consistency"
               % (agree, agree_trap), agreement=agree_trap, drop=agree - agree_trap)

    # ------------------------------------------------------------- N6.2
    trunc = S.RBFModel(model.coef[:10], model.SVs[:10], model.bias, model.sigma, "trunc")
    hd_trunc = _hausdorff(zs_cpsp, _zero_set(trunc))
    rec.defect("N6.2", hd_trunc > 0.5,
               "keeping only 10 of the 40 BVs deforms the zero set by %.4f "
               "(Hausdorff, unit square): every BV carries boundary information"
               % hd_trunc, hausdorff=hd_trunc)

    # ------------------------------------------------------------- N6.3
    lib_nob = S.RBFModel(lib.coef, lib.SVs, 0.0, lib.sigma, "lib_nobias")
    d_lib = float(np.max(np.abs(lib_nob.gamma(X) - f_lib)))
    hd_lib = _hausdorff(zs_lib, _zero_set(lib_nob))
    rec.defect("N6.3", abs(d_lib - abs(lib.bias)) < 1e-9 and hd_lib > 0.1,
               "non-zero-bias fixture (libsvm, bias = %.4f): dropping it shifts Gamma "
               "by exactly |bias| (%.4f) and moves the zero set by %.4f"
               % (lib.bias, d_lib, hd_lib), delta=d_lib, hausdorff=hd_lib)

    # ------------------------------------------------------------- N6.4
    grad_flip = -grad
    norm_f = np.linalg.norm(grad_flip, axis=1)
    ok_f = norm_f > 1e-9
    step_f = 1e-4 * grad_flip[ok_f] / norm_f[ok_f, None]
    up_flip = model.gamma(F[ok_f] + step_f) > model.gamma(F[ok_f])
    frac_flip = float(np.mean(up_flip))
    n_flip = int(np.sum(up_flip))
    n_ok = int(ok_f.sum())
    rec.defect("N6.4", frac_flip == 0.0,
               "writing (f_n - f) instead of (f - f_n) in (25) flips the gradient: "
               "the ascent test now succeeds at %d/%d points, i.e. P6.3 fails"
               % (n_flip, n_ok), fraction=frac_flip)

    # ----------------------------------------------------------- figures
    n = 241
    xs = np.linspace(0.0, 1.0, n)
    gx, gy = np.meshgrid(xs, xs)
    G = model.gamma(np.c_[gx.ravel(), gy.ravel()]).reshape(n, n)
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    cs = ax.contourf(gx, gy, G, levels=21, cmap="RdBu_r")
    ax.contour(gx, gy, G, levels=[0.0], colors="k", linewidths=1.6)
    ax.contour(gx, gy, lib.gamma(np.c_[gx.ravel(), gy.ravel()]).reshape(n, n),
               levels=[0.0], colors="lime", linestyles="--", linewidths=1.2)
    ax.plot(X[y > 0, 0], X[y > 0, 1], "b.", ms=3, label="label +1")
    ax.plot(X[y < 0, 0], X[y < 0, 1], "r.", ms=3, label="label -1")
    ax.set_title(r"$\Gamma_{raw}$ (CPSP, $\sigma=0.1$): solid = zero set, "
                 "dashed = libsvm zero set")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fig.colorbar(cs, ax=ax, shrink=0.85)
    ax.legend(loc="upper right", fontsize=8)
    save(fig, rec, "t06_gamma_contour.png")

    sx, sy = 0.06, 0.06
    qx, qy = np.meshgrid(np.arange(sx, 1.0, 0.04), np.arange(sy, 1.0, 0.04))
    P = np.c_[qx.ravel(), qy.ravel()]
    gq = model.grad(P)
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    ax.contourf(gx, gy, G, levels=21, cmap="RdBu_r", alpha=0.75)
    ax.contour(gx, gy, G, levels=[0.0], colors="k", linewidths=1.4)
    ax.quiver(P[:, 0], P[:, 1], gq[:, 0], gq[:, 1],
              np.linalg.norm(gq, axis=1), cmap="viridis", scale=6e2)
    ax.set_title(r"$\nabla_f \Gamma$ points to the free ($\Gamma>0$) side")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, rec, "t06_grad_field.png")

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    err_ok = np.max(np.abs(G_an - G_fd), axis=1)
    err_trap = np.max(np.abs(trap.grad(model.SVs) - G_an), axis=1)
    ax.semilogy(np.arange(len(err_ok)) + 1, np.maximum(err_ok, 1e-18), "o-", ms=4,
                label=r"analytic vs FD, $\sigma=0.1$")
    ax.semilogy(np.arange(len(err_trap)) + 1, err_trap, "x-", ms=4,
                label=r"$\sigma=50$ gradient vs $\sigma=0.1$ gradient")
    ax.set_xlabel("support vector index")
    ax.set_ylabel("max |component error|")
    ax.set_title("the FD check is self-consistency only")
    ax.legend(fontsize=8)
    save(fig, rec, "t06_grad_error.png")

    return rec
