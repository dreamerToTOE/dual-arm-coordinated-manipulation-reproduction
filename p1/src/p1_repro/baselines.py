"""Baseline controller variants for the paper's Table II structure.

These reproduce the *family* of the paper's baselines on the numerical tasks,
not their exact per-scene numbers:

* ``mppi``      - Gaussian MPPI (Eq. 20 printed);
* ``log_mppi``  - log-normal sampling [46];
* ``fre_mppi``  - frequency-domain (coloured) sampling [47];
* ``biased_mppi``- a fixed classical prior anchors the mean [48];
* ``high_mppi`` - no obstacle/tilt penalties (no structured constraint handling);
* ``cem``       - cross-entropy method (elite mean/var), 5 iterations [76].

All share the task cost, budget and temperature schedule so the comparison is
apples-to-apples.
"""

from __future__ import annotations

import numpy as np

from .sampler import colored, gaussian, log_normal, softmax_weights, weighted_noise


def _weights(costs, lam_frac):
    lam = lam_frac * float(costs.max() - costs.min())
    return softmax_weights(costs, max(lam, 1e-9))


def mppi(task, rng, samples, std, iterations, lam_frac, u0, sampler):
    u = u0.copy()
    for _ in range(iterations):
        eps = sampler(rng, samples, task.horizon, 2, std)
        d = task.rollout(u[None] + eps)
        w = _weights(d["cost"], lam_frac)
        u = np.clip(u + weighted_noise(eps, w), -task.u_max, task.u_max)
    return u


def biased_mppi(task, rng, samples, std, iterations, lam_frac, u0, sampler):
    """MPPI anchored to a fixed classical prior (the seed plan)."""
    u = u0.copy()
    for _ in range(iterations):
        eps = sampler(rng, samples, task.horizon, 2, std)
        d = task.rollout(u0[None] + eps)
        w = _weights(d["cost"], lam_frac)
        u = np.clip(u0 + weighted_noise(eps, w), -task.u_max, task.u_max)
    return u


def cem(task, rng, samples, std, iterations, lam_frac, u0, elite_frac=0.2):
    u = u0.copy()
    s = std
    for _ in range(iterations):
        eps = gaussian(rng, (samples, task.horizon, 2), s)
        d = task.rollout(u[None] + eps)
        k = max(2, int(samples * elite_frac))
        elite = np.argsort(d["cost"].reshape(-1))[:k]
        u = np.clip(u + eps[elite].mean(axis=0), -task.u_max, task.u_max)
        s = max(0.05, float(eps[elite].std(axis=0).mean()))
    return u


def _gauss(rng, n, h, d, std):
    return gaussian(rng, (n, h, d), std)


def _log(rng, n, h, d, std):
    return log_normal(rng, n, h, d, std, log_std=0.1)


def _colored(rng, n, h, d, std):
    return colored(rng, n, h, d, std, gamma=2.0)


def run_variant(task, rng, variant: str, samples=1000, std=0.15, iterations=10,
                lam_frac=0.1, u0=None) -> np.ndarray:
    u0 = task.seed_plan(1.0) if u0 is None else u0
    if variant == "cem":
        return cem(task, rng, samples, std, iterations, lam_frac, u0)
    if variant == "biased_mppi":
        return biased_mppi(task, rng, samples, std, iterations, lam_frac, u0, _colored)
    if variant == "high_mppi":
        from .cost import CostConfig

        high = CostConfig(name="high", p_ec=0.0, p_tilt=0.0)
        return mppi(_retask(task, high), rng, samples, std, iterations, lam_frac, u0, _colored)
    samplers = {"mppi": _gauss, "log_mppi": _log, "fre_mppi": _colored}
    if variant not in samplers:
        raise ValueError(variant)
    return mppi(task, rng, samples, std, iterations, lam_frac, u0, samplers[variant])


def _retask(task, cfg):
    """Return a shallow copy of the task with a different cost config."""
    import copy

    t = copy.copy(task)
    t.cfg = cfg
    return t
