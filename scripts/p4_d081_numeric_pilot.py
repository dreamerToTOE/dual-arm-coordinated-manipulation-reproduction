#!/usr/bin/env python3
"""Run the first D081 P4 numerical-reproduction pilot.

The pilot is deliberately small and paired.  It executes real NumPy/GEOS
math, projections, RBS local connections and the existing bounded planner;
it does not start Isaac/ROS, an author source binary, or a robot.  Original
paper sample counts remain metadata and are never replaced by this pilot.

Labels used in the saved records are explicit:
  ORIGINAL      paper definitions/control flow and preserved source inputs
  CORRECTED     independently differentiated or source-audited numerical
                implementation where the old implementation was known to be
                numerically defective
  RECONSTRUCTED independent 20R planar geometry and GEOS collision model
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import shapely

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from baselines.p4_comparison.model import PlanarModel
from baselines.p4_comparison.planner import plan
from baselines.p4_comparison.strategies import DEFAULT_CONFIG, nr_project, rbs_connect
from baselines.p4_full.geometry_consistent.physical_nr import (
    arm_fk_jac,
    closure_vector_jacobian,
    residual_metrics,
)
from baselines.p4_full.geometry_consistent.rss_geometry import (
    apply_mode,
    singularity_factors,
)


CONFIG_PATH = ROOT / "configs/p4_d081/numeric_pilot_v1.json"
P4_PDF = ROOT / "references/private_sources/P4_original.pdf"


class PartitionSweepModel(PlanarModel):
    """Same 20R geometry, exposing every valid contiguous 3R partition.

    A 20R chain with 19 positive-length links and one zero-length terminal
    flange has only 17 contiguous positive 3R passive chains (starts 0..16).
    This is why the paper's m=20 curve is recorded as unavailable rather than
    filled by duplicate or synthetic partitions.
    """

    partitions = tuple(range(17))

    def _partition(self, partition_start):
        if partition_start not in self.partitions:
            raise ValueError("invalid contiguous 3R partition")


class PartitionSubsetModel(PartitionSweepModel):
    def __init__(self, partitions):
        super().__init__()
        values = tuple(int(p) for p in partitions)
        if not values or any(p not in PartitionSweepModel.partitions for p in values):
            raise ValueError("partition subset must be nonempty and valid")
        self.partitions = values


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def save_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2,
                                allow_nan=False, default=json_default) + "\n",
                    encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wrap(q):
    return (np.asarray(q, dtype=float) + np.pi) % (2.0 * np.pi) - np.pi


def vector_norm(q):
    return float(np.linalg.norm(np.asarray(q, dtype=float)))


def valid_state(model, q, env="E0_sparse"):
    result = model.valid(np.asarray(q, dtype=float), env)
    return bool(result.get("valid")), result


def generate_closed_state(model, rng, *, partition=None, branch=None,
                          env="E0_sparse", noise=0.18, attempts=400):
    """Generate a real closed state near a registered endpoint.

    Active coordinates are perturbed and the selected passive chain is closed
    analytically.  A failed IK/collision attempt is retained in the returned
    counter; no fallback to NR is used.
    """
    if partition is None:
        partition = int(rng.choice(model.partitions))
    if branch is None:
        branch = int(rng.choice((-1, 1)))
    failures = defaultdict(int)
    base = model.start.copy()
    for _ in range(int(attempts)):
        raw = base.copy()
        active = np.ones(model.n, dtype=bool)
        active[partition:partition + 3] = False
        raw[active] += rng.normal(0.0, noise, int(active.sum()))
        raw = wrap(raw)
        result = model.ik(raw, partition, branch)
        failures[result.reason] += 1
        if result.success:
            qualified, evidence = valid_state(model, result.q, env)
            if qualified:
                return result.q.copy(), {"partition": partition, "branch": branch,
                                         "attempts": int(sum(failures.values())),
                                         "failures": dict(failures),
                                         "qualification": evidence}
            failures["VALID_" + str(evidence.get("reason"))] += 1
    return None, {"partition": partition, "branch": branch,
                  "attempts": int(sum(failures.values())),
                  "failures": dict(failures)}


def collect_states(model, rng, count, *, env="E0_sparse", noise=0.18,
                   fixed_partition=None, fixed_branch=None):
    states, metadata = [], []
    for _ in range(int(count)):
        q, info = generate_closed_state(model, rng, partition=fixed_partition,
                                        branch=fixed_branch, env=env, noise=noise)
        if q is not None:
            states.append(q)
            metadata.append(info)
    if not states:
        # Registered exact endpoints are real data and make a failed sampling
        # stratum visible without inventing a state.
        states = [model.start.copy(), model.goal.copy()]
        metadata = [{"source": "REGISTERED_START"}, {"source": "REGISTERED_GOAL"}]
    return states, metadata


def apc_project(model, q):
    """Analytic APC projection with a fixed passive chain and both IK labels."""
    started = time.perf_counter()
    q = wrap(q)
    partition = 16
    preferred = -1 if float(q[partition + 1]) <= 0.0 else 1
    branches = (preferred, -preferred)
    attempts = []
    for branch in branches:
        result = model.ik(q, partition, branch)
        attempts.append({"branch": branch, "success": bool(result.success),
                         "reason": result.reason, "cosine": result.cosine,
                         "q": None if result.q is None else result.q.tolist()})
    successful = [a for a in attempts if a["success"]]
    if not successful:
        return {"success": False, "reason": attempts[-1]["reason"],
                "partition": partition, "attempts": attempts,
                "wall_sec": time.perf_counter() - started}
    # Re-evaluate candidates to select the closest valid APC branch, a
    # deterministic source-compatible nearest solution policy.
    candidates = []
    for branch in branches:
        result = model.ik(q, partition, branch)
        if result.success:
            candidates.append((vector_norm(result.q - q), branch, result.q))
    distance, branch, projected = min(candidates, key=lambda item: item[0])
    residual = model.closure(projected)
    return {"success": True, "reason": "APC_IK_CONVERGED", "partition": partition,
            "branch": int(branch), "q": projected.tolist(),
            "projection_distance_rad": float(distance),
            "closure_position_m": float(np.linalg.norm(residual[:2])),
            "closure_angle_rad": float(abs(residual[2])),
            "attempts": attempts, "wall_sec": time.perf_counter() - started}


def nr_project_trial(model, q):
    started = time.perf_counter()
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({"max_compute_wall_sec": 2.0, "nr_max_iterations": 100})
    result = nr_project(model, wrap(q), cfg)
    return {"success": bool(result.success), "reason": result.reason,
            "q": None if result.q is None else result.q.tolist(),
            "projection_distance_rad": None if result.q is None else vector_norm(result.q - wrap(q)),
            "closure_position_m": None if result.q is None else float(np.linalg.norm(model.closure(result.q)[:2])),
            "closure_angle_rad": None if result.q is None else float(abs(model.closure(result.q)[2])),
            "iterations": len(result.trace),
            "wall_sec": time.perf_counter() - started,
            "trace": result.trace}


def run_projection_pilot(model, config, rng):
    rows = []
    for scale in config["projection_scales_rad"]:
        for index in range(int(config["projection_samples_per_scale"])):
            q = wrap(model.start + rng.normal(0.0, float(scale), model.n))
            apc = apc_project(model, q)
            nr = nr_project_trial(model, q)
            before = vector_norm(q - model.start)
            for method, result in (("APC", apc), ("NR", nr)):
                row = {"scale_rad": float(scale), "sample": index, "method": method,
                       "input_distance_to_anchor_rad": before, **{k: v for k, v in result.items() if k != "trace"}}
                if method == "NR":
                    row["iterations"] = result["iterations"]
                    row["trace_last_residual_position_m"] = (None if not result["trace"] else
                                                               result["trace"][-1]["position_m"])
                rows.append(row)
    return rows


def finite_difference_planar(model, q, h=1e-6):
    q = np.asarray(q, dtype=float)
    numeric = np.column_stack([(model.closure(q + np.eye(model.n)[j] * h) -
                                model.closure(q - np.eye(model.n)[j] * h)) / (2.0 * h)
                               for j in range(model.n)])
    return float(np.max(np.abs(model.jacobian(q) - numeric)))


def run_math_qualification(model, rng):
    errors = [finite_difference_planar(model, q)
              for q in (model.start, model.goal, (model.start + model.goal) / 2.0,
                        wrap(model.start + rng.normal(0.0, 0.1, model.n)))]
    branches = []
    for partition in model.partitions:
        for base_name, base in (("start", model.start), ("goal", model.goal)):
            for branch in (-1, 1):
                result = model.ik(base, int(partition), branch)
                branches.append({"partition": int(partition), "base": base_name,
                                 "branch": branch, "success": bool(result.success),
                                 "reason": result.reason,
                                 "closure_position_m": None if result.q is None else float(np.linalg.norm(model.closure(result.q)[:2])),
                                 "closure_angle_rad": None if result.q is None else float(abs(model.closure(result.q)[2]))})
    fixture = PlanarModel().singular_fixture()
    singular = {"success": bool(fixture.success), "reason": fixture.reason,
                 "q": None if fixture.q is None else fixture.q.tolist()}
    if fixture.success:
        jp = model.jacobian(fixture.q)[:, 16:19]
        singular.update({"passive_jacobian_rank": int(np.linalg.matrix_rank(jp, tol=1e-10)),
                         "passive_jacobian_determinant": float(np.linalg.det(jp)),
                         "passive_singular_values": np.linalg.svd(jp, compute_uv=False).tolist(),
                         "branch": int(model.branch(fixture.q, 16))})
    collision_negative = model.collision(np.r_[np.zeros(19), 0.0], "E0_sparse")
    return {"jacobian_fd_max_abs": max(errors), "jacobian_fd_errors": errors,
            "analytic_ik_branch_cases": branches,
            "analytic_ik_success_count": sum(item["success"] for item in branches),
            "analytic_ik_total": len(branches), "singular_fixture": singular,
            "collision_negative": collision_negative,
            "labels": {"FK": "RECONSTRUCTED", "IK": "RECONSTRUCTED",
                        "Jacobian": "RECONSTRUCTED", "NR": "ORIGINAL_FORMULA"}}


def run_fig3(model, config, rng):
    rows = []
    state_records = []
    rbs_cfg = dict(DEFAULT_CONFIG)
    rbs_cfg.update({"rbs_resolution_rad": 0.05, "rbs_max_depth": 16,
                    "rbs_max_projections": 512, "max_compute_wall_sec": 2.0})
    requested = [int(x) for x in config["fig3_passive_chain_counts"]]
    for m in requested:
        if m > len(PartitionSweepModel.partitions):
            state_records.append({"m": m, "status": "UNAVAILABLE_IN_RECONSTRUCTED_MODEL",
                                  "available_partitions": len(PartitionSweepModel.partitions)})
            continue
        subset = PartitionSubsetModel(tuple(range(m)))
        states = []
        for partition in subset.partitions:
            generated, metadata = collect_states(subset, rng,
                                                  config["fig3_states_per_partition"],
                                                  fixed_partition=partition,
                                                  fixed_branch=-1, noise=0.12)
            states.extend(generated)
            state_records.append({"m": m, "partition": int(partition),
                                  "generated": len(generated),
                                  "metadata": metadata[:3]})
        if len(states) < 2:
            states = [subset.start.copy(), subset.goal.copy()]
        for pair_index in range(int(config["fig3_pairs_per_count"])):
            a, b = states[int(rng.integers(0, len(states), endpoint=False))], states[int(rng.integers(0, len(states), endpoint=False))]
            result = rbs_connect(subset, "E0_sparse", "PCS", a, b, rbs_cfg)
            rows.append({"m": m, "pair": pair_index,
                         "distance_rad": vector_norm(b - a),
                         "success": bool(result["success"]),
                         "reason": result["reason"],
                         "projection_calls": int(result["projection_calls"]),
                         "wall_sec": float(result["compute_wall_time_sec"])})
    return rows, state_records


def run_visibility(model, config, rng):
    states, metadata = collect_states(model, rng, config["visibility_samples"], noise=0.22)
    pairs = []
    rbs_cfg = dict(DEFAULT_CONFIG)
    rbs_cfg.update({"rbs_resolution_rad": 0.05, "rbs_max_depth": 16,
                    "rbs_max_projections": 512, "max_compute_wall_sec": 2.0})
    methods = ("RSS", "PCS", "NR")
    for pair_index in range(int(config["visibility_pairs"])):
        a = states[int(rng.integers(0, len(states), endpoint=False))]
        b = states[int(rng.integers(0, len(states), endpoint=False))]
        distance = vector_norm(b - a)
        for method in methods:
            result = rbs_connect(model, "E0_sparse", method, a, b, rbs_cfg)
            pairs.append({"pair": pair_index, "method": method,
                          "distance_rad": distance, "success": bool(result["success"]),
                          "reason": result["reason"],
                          "projection_calls": int(result["projection_calls"]),
                          "wall_sec": float(result["compute_wall_time_sec"])})
    return pairs, metadata


def run_fig5(model, config, rng):
    rows = []
    for scale in config["projection_scales_rad"]:
        for index in range(max(32, int(config["projection_samples_per_scale"] // 2))):
            q = wrap(model.start + rng.normal(0.0, float(scale), model.n))
            anchor_distance = vector_norm(q - model.start)
            apc = apc_project(model, q)
            nr = nr_project_trial(model, q)
            for method, result in (("APC", apc), ("NR", nr)):
                row = {"scale_rad": float(scale), "sample": index, "method": method,
                       "distance_before_rad": anchor_distance,
                       "success": bool(result["success"]),
                       "reason": result["reason"],
                       "wall_sec": float(result["wall_sec"])}
                if result["success"]:
                    projected = np.asarray(result["q"], dtype=float)
                    after = vector_norm(projected - model.start)
                    row.update({"distance_after_rad": after,
                                "absolute_distance_change_rad": abs(after - anchor_distance),
                                "projection_distance_rad": result.get("projection_distance_rad")})
                else:
                    row.update({"distance_after_rad": None,
                                "absolute_distance_change_rad": None,
                                "projection_distance_rad": None})
                rows.append(row)
    return rows


def planner_config(config):
    result = dict(DEFAULT_CONFIG)
    result.update({"max_compute_wall_sec": float(config["planner_max_compute_wall_sec"]),
                   "max_nodes": int(config["planner_max_nodes"]),
                   "connect_attempts": int(config["planner_connect_attempts"]),
                   "rbs_max_projections": int(config["planner_rbs_max_projections"]),
                   "rbs_max_depth": int(config["planner_rbs_max_depth"]),
                   "rbs_resolution_rad": float(config["planner_rbs_resolution_rad"]),
                   "nr_max_iterations": int(config["planner_nr_max_iterations"]),
                   "position_tolerance_m": float(config["planner_position_tolerance_m"]),
                   "rotation_tolerance_rad": float(config["planner_rotation_tolerance_rad"]),
                   "svd_absolute_cutoff": float(config["planner_svd_absolute_cutoff"]),
                   "svd_relative_cutoff": float(config["planner_svd_relative_cutoff"]),
                   "singular_probability": float(config["planner_singularity_probability"])})
    return result


def run_planner_pilot(model, config, raw_dir):
    rows = []
    algorithm = planner_config(config)
    for env in config["planner_environments"]:
        for seed in config["planner_seeds"]:
            for method in config["planner_methods"]:
                started = time.perf_counter()
                result = plan(model, env, method, int(seed), int(config["planner_outer_iterations"]), algorithm)
                result["d081_pilot_scope"] = "planar_proxy_only_not_original_spatial_table_I"
                path = raw_dir / f"planner_{env}_{method}_seed{seed}.json.gz"
                with gzip.open(path, "wt", encoding="utf-8") as stream:
                    json.dump(result, stream, ensure_ascii=False, allow_nan=False,
                              default=json_default)
                row = {"environment": env, "method": method, "seed": int(seed),
                       "status": result["status"],
                       "terminal_reason": result["terminal_reason"],
                       "wall_sec": float(result["compute_wall_time_sec"]),
                       "serialization_inclusive_wall_sec": float(time.perf_counter() - started),
                       "node_count": int(result["node_count"]),
                       "samples": int(result["counters"].get("samples", 0)),
                       "projection_calls": int(result["counters"].get("projection_calls", 0)),
                       "local_connection_calls": int(result["counters"].get("local_connection_calls", 0)),
                       "accepted_edges": int(result["counters"].get("accepted_edges", 0)),
                       "partition_choices": int(result["counters"].get("partition_choices", 0)),
                       "pcs_fixed_partition": (None if not method.startswith("PCS_FIXED_")
                                               else int(method.rsplit("_", 1)[1])),
                       "success": result["status"] == "SUCCESS",
                       "path_point_count": None if result["path_metrics"] is None else int(result["path_metrics"]["point_count"]),
                       "path_length_rad": None if result["path_metrics"] is None else float(result["path_metrics"]["joint_path_length_rad"]),
                       "minimum_clearance_m": None if result["path_metrics"] is None else float(result["path_metrics"]["minimum_clearance_m"]),
                       "artifact": str(path.relative_to(raw_dir.parent))}
                rows.append(row)
    return rows, algorithm


def run_spatial_math(config):
    results = {"labels": {"ABB_FK_Jacobian": "RECONSTRUCTED",
                           "closure_equations": "ORIGINAL_EQ1_ADAPTED_SE3",
                           "RSS_singular_factors": "CORRECTED_GEOMETRY_CONSISTENT"}}
    for env, rel in config["spatial_saved_inputs"].items():
        payload = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        if env == "II":
            q = np.asarray(payload["q12"], dtype=float)
        else:
            q = np.asarray(payload["start_q12"], dtype=float)
        residual, jac = closure_vector_jacobian(q, env)
        h = 1e-6
        numeric = np.column_stack([(closure_vector_jacobian(q + np.eye(12)[j] * h, env)[0] -
                                    closure_vector_jacobian(q - np.eye(12)[j] * h, env)[0]) / (2.0 * h)
                                   for j in range(12)])
        results[env] = {"source_input": rel, "q12": q.tolist(),
                        "closure_residual": residual.tolist(),
                        "closure_max_abs": float(np.max(np.abs(residual))),
                        "jacobian_shape": list(jac.shape),
                        "jacobian_rank": int(np.linalg.matrix_rank(jac)),
                        "jacobian_fd_max_abs": float(np.max(np.abs(jac - numeric))),
                        "metrics": residual_metrics(q, env),
                        "new_solver_calls": 0,
                        "classification": "RECONSTRUCTED_SAVED_ENDPOINT_MATH_ONLY"}
    q = np.asarray(results["II"]["q12"][:6], dtype=float)
    singular = []
    for mode in (0, 1, 2):
        candidate = apply_mode(q, "ABB", mode)
        _, jac = arm_fk_jac(candidate, "II", 1)
        factors = singularity_factors(candidate, "ABB")
        singular.append({"mode": int(mode), "q": candidate.tolist(),
                         "factors": factors,
                         "jacobian_rank": int(np.linalg.matrix_rank(jac, tol=1e-8)),
                         "jacobian_singular_values": np.linalg.svd(jac, compute_uv=False).tolist(),
                         "wrist_or_elbow_rank_deficient": bool(np.linalg.matrix_rank(jac, tol=1e-8) < 6)})
    results["rss_singular_modes"] = singular
    results["cross_branch_evidence"] = {
        "planar": "Planar IK computes both analytic labels on every registered partition; see math_summary.",
        "spatial": "Saved ABB singular factors and rank are verified; a complete spatial closed-form branch bridge remains a gap."
    }
    return results


def csv_write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    keys = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def safe_mean(values):
    values = [float(x) for x in values if x is not None and math.isfinite(float(x))]
    return None if not values else float(np.mean(values))


def plot_projection(rows, path):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for method, color in (("APC", "tab:orange"), ("NR", "tab:blue")):
        subset = [r for r in rows if r["method"] == method]
        scales = sorted(set(r["scale_rad"] for r in subset))
        rate = [np.mean([r["success"] for r in subset if r["scale_rad"] == s]) for s in scales]
        cost = [safe_mean([r["wall_sec"] for r in subset if r["scale_rad"] == s]) for s in scales]
        axes[0].plot(scales, rate, marker="o", label=method, color=color)
        axes[1].plot(scales, cost, marker="o", label=method, color=color)
    axes[0].set(xlabel="扰动尺度 / rad", ylabel="投影成功率", ylim=(-0.02, 1.02))
    axes[1].set(xlabel="扰动尺度 / rad", ylabel="平均计算时间 / s")
    for ax in axes:
        ax.grid(alpha=0.3); ax.legend()
    fig.suptitle("D081 APC 与 NR 配对投影 pilot（真实运行数据）")
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def plot_fig3(rows, path):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for m in sorted(set(r["m"] for r in rows)):
        subset = [r for r in rows if r["m"] == m]
        bins = np.arange(0.0, max([r["distance_rad"] for r in subset] + [0.3]) + 0.3, 0.3)
        x, y = [], []
        for low in bins[:-1]:
            high = low + 0.3
            group = [r for r in subset if low <= r["distance_rad"] < high]
            if group:
                x.append(low + 0.15); y.append(np.mean([r["success"] for r in group]))
        if x: ax.plot(x, y, marker="o", label=f"m={m}")
    ax.set(xlabel="构型距离 / rad", ylabel="局部连接成功率", ylim=(-0.02, 1.02))
    ax.grid(alpha=0.3); ax.legend(ncol=2)
    ax.set_title("D081 Fig.3 机制 pilot：真实 RBS/PCS 分划数量")
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def plot_visibility(rows, path):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for method in ("RSS", "PCS", "NR"):
        subset = [r for r in rows if r["method"] == method]
        bins = np.arange(0.0, max([r["distance_rad"] for r in subset] + [0.3]) + 0.3, 0.3)
        x, y = [], []
        for low in bins[:-1]:
            high = low + 0.3
            group = [r for r in subset if low <= r["distance_rad"] < high]
            if group:
                x.append(low + 0.15); y.append(np.mean([r["success"] for r in group]))
        if x: ax.plot(x, y, marker="o", label=method)
    ax.set(xlabel="构型距离 / rad", ylabel="局部可见性估计", ylim=(-0.02, 1.02))
    ax.grid(alpha=0.3); ax.legend(); ax.set_title("D081 Fig.4 局部可见性 pilot")
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def plot_fig5(rows, path):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for method in ("APC", "NR"):
        subset = [r for r in rows if r["method"] == method]
        scales = sorted(set(r["scale_rad"] for r in subset))
        x, y = [], []
        for scale in scales:
            values = [r["absolute_distance_change_rad"] for r in subset
                      if r["scale_rad"] == scale and r["absolute_distance_change_rad"] is not None]
            if values:
                x.append(scale); y.append(float(np.mean(values)))
        if x: ax.plot(x, y, marker="o", label=method)
    ax.set(xlabel="投影前扰动尺度 / rad", ylabel="平均绝对距离变化 / rad")
    ax.grid(alpha=0.3); ax.legend(); ax.set_title("D081 Fig.5 投影距离变化 pilot")
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def plot_planner(rows, path):
    groups = defaultdict(list)
    for row in rows:
        groups[(row["environment"], row["method"])].append(row)
    labels, values = [], []
    for env in sorted(set(r["environment"] for r in rows)):
        for method in ("RSS", "PCS", "PCS_FIXED_0", "PCS_FIXED_16", "NR"):
            group = groups[(env, method)]
            if group:
                labels.append(f"{env}\n{method}")
                values.append(float(np.mean([r["success"] for r in group])))
    fig, ax = plt.subplots(figsize=(10, 4.3))
    ax.bar(np.arange(len(labels)), values, color=["tab:gray" if "RSS" in x else "tab:blue" if "NR" in x else "tab:green" for x in labels])
    ax.set_xticks(np.arange(len(labels)), labels, rotation=45, ha="right")
    ax.set_ylim(0, 1.05); ax.set_ylabel("成功率（pilot 分母）"); ax.grid(axis="y", alpha=0.3)
    ax.set_title("Table I/II 阶段性 planar proxy：真实规划 pilot")
    fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def aggregate_planner(rows):
    out = []
    keys = sorted(set((r["environment"], r["method"]) for r in rows))
    for env, method in keys:
        group = [r for r in rows if (r["environment"], r["method"]) == (env, method)]
        successes = [r for r in group if r["success"]]
        out.append({"environment": env, "method": method, "sample_n": len(group),
                    "success": len(successes), "success_rate": len(successes) / len(group),
                    "mean_wall_sec": safe_mean(r["wall_sec"] for r in group),
                    "mean_success_wall_sec": safe_mean(r["wall_sec"] for r in successes),
                    "mean_nodes": safe_mean(r["node_count"] for r in group),
                    "mean_samples": safe_mean(r["samples"] for r in group),
                    "mean_projection_calls": safe_mean(r["projection_calls"] for r in group),
                    "mean_local_connection_calls": safe_mean(r["local_connection_calls"] for r in group),
                    "mean_path_length_rad": safe_mean(r["path_length_rad"] for r in successes),
                    "mean_minimum_clearance_m": safe_mean(r["minimum_clearance_m"] for r in successes)})
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/20261019_D081_numeric_pilot")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing output directory: {output}")
    output.mkdir(parents=True)
    raw_dir = output / "raw_planner"
    raw_dir.mkdir()
    plots = output / "plots"
    plots.mkdir()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    git_status = subprocess.check_output(["git", "status", "--short", "--branch"], cwd=ROOT, text=True)
    save_json(output / "config_snapshot.json", config)
    save_json(output / "run_metadata.json", {
        "schema": "P4_D081_NUMERICAL_PILOT_RUN_V1", "run_id": output.name,
        "started_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "git_head": git_head, "git_status_at_start": git_status,
        "python": sys.version, "numpy": np.__version__, "shapely": shapely.__version__,
        "geos": shapely.geos_version_string, "matplotlib": matplotlib.__version__,
        "platform": platform.platform(), "processor": platform.processor(),
        "hardware_or_isaac_calls": 0, "author_source_calls": 0,
        "formal_table_I_calls": 0,
        "source_files": {str(p.relative_to(ROOT)): sha256(p) for p in
                          (CONFIG_PATH, P4_PDF, ROOT / "baselines/p4_comparison/model.py",
                           ROOT / "baselines/p4_comparison/strategies.py",
                           ROOT / "baselines/p4_comparison/planner.py",
                           ROOT / "baselines/p4_full/geometry_consistent/physical_nr.py",
                           ROOT / "baselines/p4_full/geometry_consistent/rss_geometry.py",
                           Path(__file__))}
    })

    total_started = time.perf_counter()
    rng = np.random.Generator(np.random.PCG64(int(config["paired_seed"])))
    model = PlanarModel()
    math_summary = run_math_qualification(model, rng)
    save_json(output / "math_summary.json", math_summary)
    spatial_summary = run_spatial_math(config)
    save_json(output / "spatial_saved_math_summary.json", spatial_summary)

    projection_rows = run_projection_pilot(model, config, rng)
    csv_write(output / "projection_trials.csv", projection_rows)
    plot_projection(projection_rows, plots / "projection_success_and_cost.png")

    fig3_rows, fig3_states = run_fig3(model, config, rng)
    csv_write(output / "fig3_pairs.csv", fig3_rows)
    save_json(output / "fig3_state_generation.json", fig3_states)
    plot_fig3([r for r in fig3_rows if isinstance(r.get("m"), int)], plots / "fig3_passive_chain_visibility.png")

    fig4_rows, visibility_states = run_visibility(model, config, rng)
    csv_write(output / "fig4_visibility_pairs.csv", fig4_rows)
    save_json(output / "fig4_state_generation.json", visibility_states)
    plot_visibility(fig4_rows, plots / "fig4_visibility.png")

    fig5_rows = run_fig5(model, config, rng)
    csv_write(output / "fig5_distance_change.csv", fig5_rows)
    plot_fig5(fig5_rows, plots / "fig5_projection_distance_change.png")

    planner_rows, planner_algorithm = run_planner_pilot(model, config, raw_dir)
    csv_write(output / "planner_trials.csv", planner_rows)
    planner_aggregate = aggregate_planner(planner_rows)
    save_json(output / "table_i_ii_planar_proxy_summary.json", {
        "schema": "P4_D081_TABLE_I_II_PLANAR_PROXY_PILOT_V1",
        "rows": planner_aggregate,
        "algorithm_config": planner_algorithm,
        "sample_scope": "two paired seeds per environment/method; not original 500 trials",
        "original_table_I": "spatial environments II-V (and historical VI) remain unfulfilled",
        "D081_formal_table_I_calls": 0
    })
    plot_planner(planner_rows, plots / "planner_success_planar_proxy.png")

    projection_group = []
    for method in ("APC", "NR"):
        group = [r for r in projection_rows if r["method"] == method]
        projection_group.append({"method": method, "n": len(group),
                                 "success": sum(bool(r["success"]) for r in group),
                                 "success_rate": float(np.mean([r["success"] for r in group])),
                                 "mean_wall_sec": safe_mean(r["wall_sec"] for r in group),
                                 "mean_iterations": safe_mean(r.get("iterations") for r in group),
                                 "mean_distance_rad": safe_mean(r.get("projection_distance_rad") for r in group)})
    fig3_group = []
    for m in sorted(set(r["m"] for r in fig3_rows)):
        group = [r for r in fig3_rows if r["m"] == m]
        fig3_group.append({"m": m, "n": len(group), "success": sum(bool(r["success"]) for r in group),
                           "success_rate": float(np.mean([r["success"] for r in group])) if group else None})
    fig4_group = []
    for method in ("RSS", "PCS", "NR"):
        group = [r for r in fig4_rows if r["method"] == method]
        fig4_group.append({"method": method, "n": len(group), "success": sum(bool(r["success"]) for r in group),
                           "success_rate": float(np.mean([r["success"] for r in group])) if group else None,
                           "mean_wall_sec": safe_mean(r["wall_sec"] for r in group)})
    save_json(output / "summary.json", {
        "schema": "P4_D081_NUMERICAL_PILOT_SUMMARY_V1",
        "status": "PILOT_COMPLETED_REAL_NUMERICAL_DATA",
        "elapsed_wall_sec": time.perf_counter() - total_started,
        "math": {"jacobian_fd_max_abs": math_summary["jacobian_fd_max_abs"],
                 "analytic_ik_success": math_summary["analytic_ik_success_count"],
                 "analytic_ik_total": math_summary["analytic_ik_total"],
                 "singular_rank": math_summary["singular_fixture"].get("passive_jacobian_rank"),
                 "collision_negative": bool(math_summary["collision_negative"]["collision"])},
        "spatial": {env: {k: v for k, v in value.items() if k in ("closure_max_abs", "jacobian_rank", "jacobian_fd_max_abs", "classification")}
                    for env, value in spatial_summary.items() if env in ("II", "III")},
        "projection_groups": projection_group,
        "fig3_groups": fig3_group,
        "fig4_groups": fig4_group,
        "planner_groups": planner_aggregate,
        "fig3_m20_status": "UNAVAILABLE_IN_RECONSTRUCTED_20R_CONTIGUOUS_3R_PARTITIONS",
        "formal_table_I_calls": 0,
        "original_table_I_denominator": 22500,
        "d080_target_cancelled_by_d081": 18000,
        "source_labels": {"paper_definitions": "ORIGINAL", "planar_model": "RECONSTRUCTED",
                          "spatial_saved_math": "RECONSTRUCTED", "old_failures": "PRESERVED"},
        "limitations": [
            "This is a paired pilot, not the paper's 500,000 projection or 50,000-pair sample.",
            "Fig.3 uses only the 17 contiguous positive-length 3R partitions available in the reconstructed 20R chain; m=20 is not synthesized.",
            "Table I/II rows are planar proxy pilot data; original spatial II-V and archived VI obligations remain open.",
            "RBS and GEOS checks are discrete; no continuous swept collision certificate is claimed.",
            "Spatial saved endpoint math is read-only and does not rerun the preserved source solve."
        ]
    })
    save_json(output / "artifact_sha256.json", {
        str(path.relative_to(output)): sha256(path)
        for path in sorted(output.rglob("*")) if path.is_file() and path.name != "artifact_sha256.json"
    })
    print(json.dumps({"output": str(output), "elapsed_wall_sec": time.perf_counter() - total_started,
                      "projection_rows": len(projection_rows), "fig3_rows": len(fig3_rows),
                      "fig4_rows": len(fig4_rows), "fig5_rows": len(fig5_rows),
                      "planner_rows": len(planner_rows), "formal_table_I_calls": 0},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
