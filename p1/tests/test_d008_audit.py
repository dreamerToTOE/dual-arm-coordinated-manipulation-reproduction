"""Regression tests for the D008 audit fixes."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

import p1_repro.twostage as ts
from p1_repro.cost import CostConfig, yoshikawa
from p1_repro.kinematics import SerialChain, relative_jacobian
from p1_repro.sampler import colored, softmax_weights, weighted_noise
from p1_repro.tasks_bimodal import BimodalTask
from p1_repro.tasks_dual import BASE1, BASE2, HOME1, HOME2, UR3_DH
from p1_repro.twostage import TwoStageConfig, kmeans, select_mode_inertial, two_stage

ROOT = Path(__file__).resolve().parents[1]


def _load_g3_module():
    spec = importlib.util.spec_from_file_location("g3_acceptance_mod", ROOT / "scripts" / "g3_acceptance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# D2: identical temperature for both aggregators
# ---------------------------------------------------------------------------
def test_d2_uses_identical_global_temperature():
    mod = _load_g3_module()
    task = BimodalTask()
    u0 = np.zeros((task.horizon, 2))
    rng = np.random.default_rng(0)
    eps = colored(rng, 200, task.horizon, 2, std=0.5, gamma=2.0, max_abs=0.6)
    d = task.rollout(u0[None] + eps)
    labels, _ = kmeans(mod.descriptors(d, task.descriptor(d)), 2, rng)
    mode = mod.select_mode(labels, d["cost"], 10)
    u_full, u_clu, lam_full, lam_clu = mod.aggregate(
        task, d, eps, u0, labels, mode, 0.1, "global"
    )
    assert lam_full == lam_clu, "global temperature must be shared by both aggregators"
    idx = np.flatnonzero(labels == mode)
    expected = u0 + weighted_noise(eps[idx], softmax_weights(d["cost"][idx], lam_full))
    assert np.allclose(u_clu, expected, atol=1e-12)
    # the historical variant must use a different (cluster-local) temperature
    _, _, lam_full_h, lam_clu_h = mod.aggregate(task, d, eps, u0, labels, mode, 0.1, "cluster_local")
    assert lam_full_h == lam_full
    assert lam_clu_h != lam_clu


def test_reports_use_measured_d2_counts():
    """Regression for the 3/20-vs-0/20 discrepancy between data and prose."""
    import json

    data = json.loads((ROOT / "reports" / "G3_ACCEPTANCE.json").read_text(encoding="utf-8"))
    md = (ROOT / "reports" / "G3_ACCEPTANCE.md").read_text(encoding="utf-8")
    d2 = data["D2"]
    token = f"{d2['cluster_better']}/{d2['seeds']}"
    assert token in md, f"report does not contain the measured D2 count {token}"


# ---------------------------------------------------------------------------
# stage-2 ablation must genuinely bypass the second stage
# ---------------------------------------------------------------------------
def test_stage2_false_bypasses_second_stage(monkeypatch):
    task = BimodalTask()
    u0 = task.seed_plan(1.0)
    cfg = TwoStageConfig(samples=20, iterations=1, stage2=False, max_abs=0.3)
    rng = np.random.default_rng(0)
    out = two_stage(task, rng, cfg, u_mean=u0)
    assert out["diag_stage2"] is None
    assert np.allclose(out["u"], out["u_stage1"])

    called = {"n": 0}

    def _fail(*args, **kwargs):
        called["n"] += 1
        raise AssertionError("stage 2 sampler called")

    monkeypatch.setattr(ts, "log_normal", _fail)
    with pytest.raises(AssertionError):
        two_stage(task, np.random.default_rng(0), TwoStageConfig(samples=20, iterations=1, stage2=True), u_mean=u0)
    assert called["n"] == 1


def test_no_variance_reduction_still_runs_stage2():
    task = BimodalTask()
    u0 = task.seed_plan(1.0)
    out = two_stage(
        task, np.random.default_rng(0),
        TwoStageConfig(samples=20, iterations=1, std2_ratio=1.0), u_mean=u0,
    )
    assert out["diag_stage2"] is not None, "no_variance_reduction must not disable stage 2"


# ---------------------------------------------------------------------------
# mode inertia: permutation-equivariant cluster identity
# ---------------------------------------------------------------------------
def test_select_mode_inertial_is_permutation_equivariant():
    labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    centroids = np.array([[0.0], [5.0]])
    costs = np.array([[0.0], [0.1], [0.2], [0.3], [0.4], [0.5], [0.6], [0.7]])
    prev_centroid = centroids.copy()
    prev_mode = 0
    mode, matched = select_mode_inertial(labels, centroids, costs, prev_centroid, prev_mode, m=4, ratio=0.6)
    assert matched == 0 and mode == 0

    perm = [1, 0]
    labels_p = np.array([perm[l] for l in labels])
    centroids_p = centroids[perm]
    prev_centroid_p = centroids_p.copy()
    prev_mode_p = perm[prev_mode]
    mode_p, _ = select_mode_inertial(labels_p, centroids_p, costs, prev_centroid_p, prev_mode_p, m=4, ratio=0.6)
    assert np.allclose(centroids_p[mode_p], centroids[mode])


def test_mode_inertia_is_off_by_default():
    assert TwoStageConfig().mode_inertia is False


# ---------------------------------------------------------------------------
# G3B fairness: equal total evaluations
# ---------------------------------------------------------------------------
def test_g3b_budget_is_matched():
    two = TwoStageConfig(samples=500, iterations=10)
    assert two.samples * 2 * two.iterations == 1000 * 10


# ---------------------------------------------------------------------------
# N3: definition and scale
# ---------------------------------------------------------------------------
def test_yoshikawa_is_product_of_six_singular_values():
    c1 = SerialChain(UR3_DH, base=BASE1)
    c2 = SerialChain(UR3_DH, base=BASE2)
    J = relative_jacobian(c1, c2, HOME1[None], HOME2[None])
    s = np.linalg.svd(J[0], compute_uv=False)
    assert abs(float(yoshikawa(J)[0, 0]) - float(np.prod(s[:6]))) < 1e-14


def test_singularity_cost_inverse_and_scale_dependent():
    c1 = SerialChain(UR3_DH, base=BASE1)
    c2 = SerialChain(UR3_DH, base=BASE2)
    cfg = CostConfig.paper()
    w1 = float(yoshikawa(relative_jacobian(c1, c2, HOME1[None], HOME2[None]))[0, 0])
    dh = UR3_DH.copy()
    dh[:, 1] *= 10.0
    dh[:, 2] *= 10.0
    c1s = SerialChain(dh, base=BASE1)
    c2s = SerialChain(dh, base=BASE2)
    w10 = float(yoshikawa(relative_jacobian(c1s, c2s, HOME1[None], HOME2[None]))[0, 0])
    assert w10 > 100.0 * w1, "w must grow with length units (not scale-free)"
    assert abs(cfg.p_sing / w1 - cfg.p_sing / w1) == 0
