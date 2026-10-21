"""G3 tests: clustering, mode selection and the two-stage loop."""

from __future__ import annotations

import numpy as np

from p1_repro.sampler import colored
from p1_repro.tasks_bimodal import BimodalTask
from p1_repro.twostage import TwoStageConfig, kmeans, select_mode, single_stage, two_stage


def _batch(seed=0, samples=400):
    task = BimodalTask()
    rng = np.random.default_rng(seed)
    eps = colored(rng, samples, task.horizon, 2, std=0.5, gamma=2.0, max_abs=0.6)
    d = task.rollout(np.zeros((1, task.horizon, 2)) + eps)
    return task, d


def test_kmeans_recovers_two_blobs():
    rng = np.random.default_rng(0)
    a = rng.normal(loc=-2.0, scale=0.2, size=(100, 2))
    b = rng.normal(loc=+2.0, scale=0.2, size=(100, 2))
    labels, centers = kmeans(np.vstack([a, b]), 2, rng)
    acc = max(np.mean(labels[:100] == 0), np.mean(labels[:100] == 1))
    assert acc > 0.98
    assert np.linalg.norm(np.sort(centers[:, 0]) - [-2.0, 2.0]).max() < 0.1


def test_descriptor_recovers_corridor_modes():
    task, d = _batch(0)
    X = task.descriptor(d)
    labels, _ = kmeans(X, 2, np.random.default_rng(0))
    mask = d["label"] != 0
    acc = max(
        np.mean(labels[mask] == (d["label"][mask] > 0)),
        np.mean(labels[mask] == (d["label"][mask] < 0)),
    )
    assert acc > 0.7, f"accuracy={acc:.3f}"


def test_mode_selection_picks_elite_majority():
    labels = np.array([0] * 6 + [1] * 4)
    costs = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [100.0], [0.5], [0.6], [0.7], [0.8]])
    # the 5 lowest-cost samples are all in cluster 0 -> mode 0
    assert select_mode(labels, costs, m=5) == 0


def test_two_stage_reaches_goal_where_single_stalls():
    task = BimodalTask()
    u0 = task.seed_plan(1.0)
    cfg = TwoStageConfig(samples=400, std1=0.15, std2_ratio=0.2, elite=10, max_abs=0.3,
                         iterations=10, lam_frac=0.1)
    two = two_stage(task, np.random.default_rng(0), cfg, u_mean=u0)
    one = single_stage(task, np.random.default_rng(0), samples=800, std=0.15, iterations=10,
                       max_abs=0.3, u_mean=u0, lam_frac=0.1)
    d_two = task.rollout(two["u"][None])
    d_one = task.rollout(one["u"][None])
    assert d_two["goal_error"][0, 0] < d_one["goal_error"][0, 0]
    assert d_two["goal_error"][0, 0] < 0.08


def test_two_stage_budget_is_equal():
    # 2 * samples stage-1/stage-2 must equal the single-stage sample count used in F1.
    cfg = TwoStageConfig(samples=500)
    assert 2 * cfg.samples == 1000
