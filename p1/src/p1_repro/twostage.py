"""Two-stage sampling MPC: clustering, mode selection and refinement.

Implements the paper's stage 1 / stage 2 structure (Eqs. 20-24, 52):

1. draw ``M`` high-variance sequences around the previous optimum;
2. roll out, evaluate ``C_exp``;
3. cluster the descriptors ``D = [C_exp, dq]`` with k-means;
4. pick the mode containing the majority of the ``m`` lowest-cost samples;
5. aggregate **within that mode** with exponential weights;
6. redraw ``M`` low-variance sequences around the aggregate and average all
   of them with ``C_std``.

The k-means here is a small deterministic Lloyd implementation (k-means++
initialisation with a seeded RNG); no sklearn, no GPU.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .sampler import (
    adaptive_weights,
    colored,
    effective_sample_size,
    log_normal,
    softmax_weights,
    weighted_noise,
)


def kmeans(X: np.ndarray, k: int, rng: np.random.Generator, iters: int = 100, tol: float = 1e-8):
    """Deterministic Lloyd k-means with k-means++ seeding."""
    X = np.asarray(X, dtype=float)
    n = X.shape[0]
    centers = [X[rng.integers(n)]]
    for _ in range(1, k):
        d2 = np.min(((X[:, None, :] - np.array(centers)[None, :, :]) ** 2).sum(-1), axis=1)
        probs = d2 / max(d2.sum(), 1e-12)
        centers.append(X[rng.choice(n, p=probs)])
    C = np.array(centers)
    labels = np.zeros(n, dtype=int)
    for _ in range(iters):
        d2 = ((X[:, None, :] - C[None, :, :]) ** 2).sum(-1)
        new_labels = np.argmin(d2, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for j in range(k):
            if np.any(labels == j):
                C[j] = X[labels == j].mean(axis=0)
    return labels, C


def descriptors(diag: dict, raw: np.ndarray | None = None) -> np.ndarray:
    """Clustering descriptors, min-max scaled per column (code style).

    ``raw`` defaults to ``[C_exp, delta_p]``; tasks may pass their own compact
    kinematic summary (the 2-D corridor task uses the mean lateral offset).
    """
    if raw is None:
        raw = np.concatenate([diag["cost"].reshape(-1, 1), diag["delta"]], axis=1)
    lo = raw.min(axis=0, keepdims=True)
    hi = raw.max(axis=0, keepdims=True)
    return (raw - lo) / np.maximum(hi - lo, 1e-12)


def select_mode(labels: np.ndarray, costs: np.ndarray, m: int = 10) -> int:
    """Mode containing the majority of the ``m`` lowest-cost samples."""
    m = min(m, len(costs))
    elite = np.argsort(costs.reshape(-1))[:m]
    counts = np.bincount(labels[elite], minlength=labels.max() + 1)
    return int(np.argmax(counts))


@dataclass
class TwoStageConfig:
    samples: int = 500
    std1: float = 0.5
    std2_ratio: float = 0.2
    gamma: float = 2.0
    clusters: int = 2
    elite: int = 10
    lam: float = 0.5
    iterations: int = 1
    max_abs: float = 0.3
    lam_frac: float | None = None  # fixed lambda = lam_frac * cost range


def two_stage(task, rng, cfg: TwoStageConfig, u_mean: np.ndarray | None = None) -> dict:
    """One two-stage optimisation (or ``iterations`` of it)."""
    u = task.nominal_u() if u_mean is None else u_mean.copy()
    out = None
    for _ in range(cfg.iterations):
        eps1 = colored(rng, cfg.samples, task.horizon, 2, std=cfg.std1, gamma=cfg.gamma, max_abs=cfg.max_abs)
        d1 = task.rollout(u[None] + eps1)
        raw = task.descriptor(d1) if hasattr(task, "descriptor") else None
        D = descriptors(d1, raw)
        labels, _ = kmeans(D, cfg.clusters, rng)
        mode = select_mode(labels, d1["cost"], cfg.elite)
        idx = np.flatnonzero(labels == mode)
        if cfg.lam_frac is None:
            w1, lam1 = adaptive_weights(d1["cost"][idx], cfg.lam, (15.0, 20.0))
        else:
            # Global temperature: the same lambda for the cluster and the full
            # set, as in the paper.  Normalising per cluster makes the
            # temperature mode-dependent (a smaller cost range -> sharper
            # weights) and biases the comparison against clustering.
            c_all = d1["cost"]
            lam1 = cfg.lam_frac * float(c_all.max() - c_all.min())
            w1 = softmax_weights(d1["cost"][idx], max(lam1, 1e-9))
        u1 = np.clip(u + weighted_noise(eps1[idx], w1), -task.u_max, task.u_max)

        eps2 = log_normal(
            rng, cfg.samples, task.horizon, 2,
            std=cfg.std1 * cfg.std2_ratio, log_std=0.1, max_abs=cfg.max_abs,
        )
        d2 = task.rollout(u1[None] + eps2)
        if cfg.lam_frac is None:
            w2, lam2 = adaptive_weights(d2["cost"], cfg.lam, (22.0, 30.0))
        else:
            c2 = d2["cost"]
            lam2 = cfg.lam_frac * float(c2.max() - c2.min())
            w2 = softmax_weights(c2, max(lam2, 1e-9))
        u2 = np.clip(u1 + weighted_noise(eps2, w2), -task.u_max, task.u_max)
        out = {
            "u": u2,
            "u_stage1": u1,
            "mode": mode,
            "labels": labels,
            "cluster_size": int(idx.size),
            "ess_stage2": effective_sample_size(w2),
            "lam1": lam1,
            "lam2": lam2,
            "diag_stage1": d1,
            "diag_stage2": d2,
        }
        u = u2
    return out


def single_stage(task, rng, samples: int, std: float, iterations: int = 1, gamma: float = 2.0,
                 lam: float = 0.5, max_abs: float = 0.3, u_mean: np.ndarray | None = None,
                 lam_frac: float | None = None) -> dict:
    """Generic single-stage MPPI with the same cost and budget."""
    u = task.nominal_u() if u_mean is None else u_mean.copy()
    last = None
    for _ in range(iterations):
        eps = colored(rng, samples, task.horizon, 2, std=std, gamma=gamma, max_abs=max_abs)
        d = task.rollout(u[None] + eps)
        if lam_frac is None:
            w, lam = adaptive_weights(d["cost"], lam, (22.0, 30.0))
        else:
            c = d["cost"]
            lam = lam_frac * float(c.max() - c.min())
            w = softmax_weights(c, max(lam, 1e-9))
        u = np.clip(u + weighted_noise(eps, w), -task.u_max, task.u_max)
        last = {"u": u, "diag": d, "ess": effective_sample_size(w)}
    return last
