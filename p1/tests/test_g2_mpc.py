"""G2 tests: single-stage MPPI (C1), estimator (C2), auxiliary/L switching (E2)."""

from __future__ import annotations

import numpy as np

from p1_repro.cost import CostConfig
from p1_repro.sampler import (
    adaptive_weights,
    colored,
    effective_sample_size,
    gaussian,
    log_normal,
    softmax_weights,
    weighted_noise,
)
from p1_repro.switch import UnexploredIndicator, auxiliary_control, decay_rate_fit
from p1_repro.tasks_linear import LinearQuadraticTask, run_mppi


def test_c1_mppi_matches_lqr_across_seeds():
    task = LinearQuadraticTask(dt=0.1, horizon=20)
    x0 = np.array([1.0, -0.5, 0.0, 0.0])
    opt = task.lqr_cost(x0)
    ratios = []
    for seed in range(50):
        r = run_mppi(task, x0, np.random.default_rng(seed), samples=800, iterations=60)
        ratios.append(r["cost"] / opt)
    ratios = np.array(ratios)
    assert np.median(ratios) <= 1.10, f"median ratio {np.median(ratios):.3f}"
    assert np.sum(ratios <= 1.10) >= 45, f"{np.sum(ratios <= 1.10)}/50 within 10%"
    assert np.all(np.isfinite(ratios))


def test_c1_cost_decreases():
    task = LinearQuadraticTask(dt=0.1, horizon=20)
    x0 = np.array([1.0, -0.5, 0.0, 0.0])
    r = run_mppi(task, x0, np.random.default_rng(0), samples=800, iterations=40)
    h = np.array(r["history"])
    assert h[-1] < 0.5 * h[0], f"{h[0]:.1f} -> {h[-1]:.1f}"
    assert np.mean(np.diff(h) <= 1e-9) > 0.8


def test_c2_effective_sample_size_and_variance():
    rng = np.random.default_rng(3)
    M, N, n = 200, 5, 2
    costs = rng.normal(size=(M, 1))
    w = softmax_weights(costs, lam=0.5)
    ess = effective_sample_size(w)
    analytic = 1.0 / np.sum(w.reshape(-1) ** 2)
    assert abs(ess - analytic) < 1e-9

    reps = 2000
    means = []
    for _ in range(reps):
        eps = rng.normal(size=(M, N, n))
        means.append(weighted_noise(eps, w))
    means = np.array(means)
    var = means.var(axis=0).mean()
    predicted = 1.0 / ess  # sigma^2 = 1
    assert 0.8 < var / predicted < 1.25, f"var={var:.4f} predicted={predicted:.4f}"


def test_c2_lambda_limits():
    costs = np.array([[0.0], [1.0], [2.0], [10.0]])
    w_small = softmax_weights(costs, lam=1e-4)
    assert np.argmax(w_small) == 0 and w_small.max() > 0.999
    w_large = softmax_weights(costs, lam=1e6)
    assert np.allclose(w_large, 0.25, atol=1e-6)


def test_samplers_shapes_and_scales():
    rng = np.random.default_rng(0)
    g = gaussian(rng, (500, 15, 4), std=3.0, max_abs=0.45)
    assert g.shape == (500, 15, 4) and np.abs(g).max() <= 0.45 + 1e-12
    c = colored(rng, 500, 15, 4, std=3.0, gamma=2.0)
    assert c.shape == (500, 15, 4) and np.all(np.isfinite(c))
    assert abs(float(c.std()) - 3.0) < 0.5, f"colored std={c.std():.2f} (expect ~3.0)"
    # coloured noise must be temporally correlated: lag-1 correlation > 0.5
    lag1 = np.mean([np.corrcoef(c[i, :-1, 0], c[i, 1:, 0])[0, 1] for i in range(200)])
    assert lag1 > 0.5, f"lag1={lag1:.3f}"
    ln = log_normal(rng, 500, 15, 4, std=1.0, log_std=0.1)
    assert ln.shape == (500, 15, 4)


def test_e2_auxiliary_control_decays_exponentially():
    # First-order closed loop: e_{k+1} = (1 - dt * K) e_k.
    K, dt, steps = 2.0, 0.01, 400
    e = np.array([1.0, -0.5, 0.25])
    hist = [e.copy()]
    for _ in range(steps):
        e = auxiliary_control(e, K, dt)
        hist.append(e.copy())
    rate = decay_rate_fit(np.array(hist), dt)
    assert abs(rate - K) / K < 0.02, f"rate={rate:.4f}"


def test_e2_unexplored_indicator_slope_and_saturation():
    ind = UnexploredIndicator(eta=0.4, l_min=-0.05, l_max=0.4, dt=0.15)
    # constant ratio 0.5: slope = 0.1 per second
    vals = [ind.value]
    for _ in range(20):
        ind.update(ratio=0.5)
        vals.append(ind.value)
    slope = (vals[-1] - vals[0]) / (20 * ind.dt)
    assert abs(slope - (0.5 - 0.4)) < 1e-3
    # saturation
    for _ in range(1000):
        ind.update(ratio=10.0)
    assert ind.value == ind.l_max
    for _ in range(1000):
        ind.update(ratio=-10.0)
    assert ind.value == ind.l_min


def test_e2_switching_dwell_time_ratio():
    """With |ratio-eta| fixed, dwell times scale as L_max / |L_min| = 8."""
    def dwell(start, target, ratio):
        # Small dt removes the integer-step quantisation so the continuous
        # ratio L_max / |L_min| can be checked directly.
        ind = UnexploredIndicator(eta=0.4, l_min=-0.05, l_max=0.4, dt=0.001)
        ind.value = start
        n = 0
        while (ind.value > target if start > target else ind.value < target):
            ind.update(ratio=ratio)
            n += 1
            if n > 10**6:
                break
        return n

    down = dwell(0.4, 0.0, 0.3)   # ratio - eta = -0.1
    up = dwell(-0.05, 0.0, 0.5)   # ratio - eta = +0.1
    ratio = down / max(up, 1)
    assert 7.9 < ratio < 8.1, f"ratio={ratio:.2f} (down={down}, up={up})"
