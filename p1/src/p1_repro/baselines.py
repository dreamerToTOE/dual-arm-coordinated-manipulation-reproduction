"""Baseline controller variants for the paper's Table II structure.

These reproduce the *family* of the paper's baselines on the numerical tasks,
not their exact per-scene numbers:

* ``mppi``      - Gaussian MPPI (Eq. 20 printed);
* ``log_mppi``  - log-normal sampling [46];
* ``fre_mppi``  - frequency-domain (coloured) sampling [47];
* ``biased_mppi``- a fixed classical prior anchors the mean [48];
* ``high_mppi`` - no obstacle/tilt penalties (no structured constraint handling);
* ``cem``       - cross-entropy method (elite mean/var) [76].

All variants share the task cost (unless stated), the control limit, the
initial plan and the temperature definition.  ``sampling_profile`` records the
*effective* perturbation statistics so that equal nominal ``std`` is not
mistaken for equal exploration (audit D008 section 5).
"""

from __future__ import annotations

import copy

import numpy as np

from .sampler import colored, gaussian, log_normal, softmax_weights, weighted_noise

SAMPLERS = {
    "gauss": lambda rng, n, h, d, std, max_abs: gaussian(rng, (n, h, d), std, max_abs=max_abs),
    "log": lambda rng, n, h, d, std, max_abs: log_normal(rng, n, h, d, std, log_std=0.1, max_abs=max_abs),
    "colored": lambda rng, n, h, d, std, max_abs: colored(rng, n, h, d, std, gamma=2.0, max_abs=max_abs),
}


def _weights(costs, lam_frac):
    lam = lam_frac * float(costs.max() - costs.min())
    return softmax_weights(costs, max(lam, 1e-9))


def sampling_profile(kind: str, samples: int, horizon: int, std: float,
                     max_abs: float | None, seed: int = 0) -> dict:
    """Effective statistics of one perturbation batch."""
    rng = np.random.default_rng(seed)
    raw = SAMPLERS[kind](rng, samples, horizon, 2, std, None)
    clipped = raw if max_abs is None else np.clip(raw, -max_abs, max_abs)
    lag1 = float(np.mean([np.corrcoef(clipped[i, :-1, 0], clipped[i, 1:, 0])[0, 1] for i in range(min(200, samples))]))
    return {
        "sampler": kind,
        "nominal_std": float(std),
        "effective_std": float(clipped.std()),
        "clipping_fraction": float(np.mean(np.abs(raw) > max_abs)) if max_abs else 0.0,
        "lag1_correlation": lag1,
        "max_abs": max_abs,
    }


def mppi(task, rng, samples, std, iterations, lam_frac, u0, kind: str, max_abs=None):
    u = u0.copy()
    for _ in range(iterations):
        eps = SAMPLERS[kind](rng, samples, task.horizon, 2, std, max_abs)
        d = task.rollout(u[None] + eps)
        w = _weights(d["cost"], lam_frac)
        u = np.clip(u + weighted_noise(eps, w), -task.u_max, task.u_max)
    return u


def biased_mppi(task, rng, samples, std, iterations, lam_frac, u0, max_abs=None):
    """MPPI anchored to a fixed classical prior (the seed plan)."""
    for _ in range(iterations):
        eps = SAMPLERS["colored"](rng, samples, task.horizon, 2, std, max_abs)
        d = task.rollout(u0[None] + eps)
        w = _weights(d["cost"], lam_frac)
        u = np.clip(u0 + weighted_noise(eps, w), -task.u_max, task.u_max)
    return u


def cem(task, rng, samples, std, iterations, lam_frac, u0, elite_frac=0.2, max_abs=None):
    u = u0.copy()
    s = std
    for _ in range(iterations):
        eps = SAMPLERS["gauss"](rng, samples, task.horizon, 2, s, max_abs)
        d = task.rollout(u[None] + eps)
        k = max(2, int(samples * elite_frac))
        elite = np.argsort(d["cost"].reshape(-1))[:k]
        u = np.clip(u + eps[elite].mean(axis=0), -task.u_max, task.u_max)
        s = max(0.05, float(eps[elite].std(axis=0).mean()))
    return u


def run_variant(task, rng, variant: str, samples=1000, std=0.15, iterations=10,
                lam_frac=0.1, u0=None, max_abs=None) -> np.ndarray:
    u0 = task.seed_plan(1.0) if u0 is None else u0
    if variant == "cem":
        return cem(task, rng, samples, std, iterations, lam_frac, u0, max_abs=max_abs)
    if variant == "biased_mppi":
        return biased_mppi(task, rng, samples, std, iterations, lam_frac, u0, max_abs=max_abs)
    if variant == "high_mppi":
        from .cost import CostConfig

        high = CostConfig(name="high", p_ec=0.0, p_tilt=0.0)
        return mppi(_retask(task, high), rng, samples, std, iterations, lam_frac, u0,
                    "colored", max_abs)
    kinds = {"mppi": "gauss", "log_mppi": "log", "fre_mppi": "colored"}
    if variant not in kinds:
        raise ValueError(variant)
    return mppi(task, rng, samples, std, iterations, lam_frac, u0, kinds[variant], max_abs)


def _retask(task, cfg):
    """Return a shallow copy of the task with a different cost config."""
    t = copy.copy(task)
    t.cfg = cfg
    return t
