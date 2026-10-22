#!/usr/bin/env python3
"""Build D082 figures from the saved D081 numerical records.

All plotted values come from the saved CSV/JSON/gzip records.  The planar
vertices are reconstructed only to draw the already-qualified path; this
script does not run a planner or requalify a state.
"""
from __future__ import annotations

import csv
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NUMERIC = ROOT / "results/20261019_D081_numeric_pilot"
STABILITY = ROOT / "results/20261019_D081_stability_pilot"
OUT = ROOT / "reports/p4_d082_simulation_assets"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def read_gzip(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def vertices(q):
    """Display-only planar FK reconstruction matching the saved 20R model."""
    angles = np.cumsum(np.asarray(q, dtype=float))
    length = math.sin(math.pi / 38.0)
    steps = length * np.column_stack((np.cos(angles[:19]), np.sin(angles[:19])))
    return np.vstack((np.zeros(2), np.cumsum(steps, axis=0)))


def plot_path(payload: dict, path: Path):
    q_path = payload["path"]
    indices = [0, len(q_path) // 2, len(q_path) - 1]
    fig, ax = plt.subplots(figsize=(7.6, 6.0))
    obstacles = ((0.45, 0.72, 0.045), (0.50, 0.18, 0.065), (0.72, 0.60, 0.05))
    for x, y, radius in obstacles:
        ax.add_patch(plt.Circle((x, y), radius, color="tab:red", alpha=0.18, ec="tab:red", lw=1.2))
    colors = ("tab:blue", "tab:orange", "tab:green")
    labels = ("start", "midpoint", "goal")
    for index, color, label in zip(indices, colors, labels):
        points = vertices(q_path[index])
        ax.plot(points[:, 0], points[:, 1], "-o", color=color, lw=1.4, ms=2.5, alpha=0.9, label=f"{label} (node {index})")
        ax.plot(points[-1, 0], points[-1, 1], "o", color=color, ms=5)
    ax.plot((0.0, 1.0), (0.0, 0.0), "k--", lw=1.0, alpha=0.6, label="ground closure")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title("D082 E1 clutter: PCS full path, seed 7 (saved run)")
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_path_metrics(payload: dict, path: Path):
    states = payload["path_metrics"]["state_qualifications"]
    x = np.arange(len(states))
    closure = np.array([max(float(s["closure_position"]), 1e-18) for s in states])
    clearance = np.array([float(s["collision"]["minimum_clearance"]) for s in states])
    margin = np.array([float(s["joint_margin"]) for s in states])
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 7.0), sharex=True)
    axes[0].semilogy(x, closure, color="tab:blue")
    axes[0].set_ylabel("closure position / m")
    axes[0].set_title("Independent state records on the saved E1 PCS path")
    axes[1].plot(x, clearance, color="tab:green")
    axes[1].axhline(0.0, color="k", lw=0.8)
    axes[1].set_ylabel("minimum clearance / m")
    axes[2].plot(x, margin, color="tab:purple")
    axes[2].set_ylabel("joint margin / rad")
    axes[2].set_xlabel("path state index")
    for ax in axes:
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_comparison(rows, path: Path):
    methods = ["RSS", "PCS", "PCS_FIXED_0", "PCS_FIXED_16", "NR"]
    names = ["RSS", "PCS", "fixed-0", "fixed-16", "NR"]
    envs = ["E0_sparse", "E1_clutter"]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.8))
    for ax, env in zip(axes, envs):
        success = []
        wall = []
        for method in methods:
            group = [row for row in rows if row["environment"] == env and row["method"] == method]
            success.append(sum(row["status"] == "SUCCESS" for row in group) / len(group))
            wall.append(np.mean([float(row["wall_sec"]) for row in group]))
        x = np.arange(len(methods))
        bars = ax.bar(x, success, color=("tab:red", "tab:blue", "tab:orange", "tab:gray", "tab:green"), alpha=0.78)
        ax.set_ylim(0, 1.08)
        ax.set_ylabel("success rate")
        ax.set_xticks(x, names, rotation=30, ha="right")
        ax.set_title(env)
        ax.grid(axis="y", alpha=0.25)
        ax2 = ax.twinx()
        ax2.plot(x, wall, "k.--", ms=5, label="mean wall time")
        ax2.set_ylabel("mean wall time / s")
        for bar, value in zip(bars, success):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.025, f"{value:.1%}", ha="center", va="bottom", fontsize=8)
    fig.suptitle("D082 paired virtual-simulation comparison (five seeds)")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_projection(rows, path: Path):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["method"], float(row["scale_rad"]))].append(row)
    methods = ["APC", "NR"]
    scales = sorted({float(row["scale_rad"]) for row in rows})
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.3))
    for method, color in zip(methods, ("tab:orange", "tab:blue")):
        rate = [sum(row["success"] == "True" for row in grouped[(method, scale)]) / len(grouped[(method, scale)]) for scale in scales]
        after = [np.mean([float(row["projection_distance_rad"]) for row in grouped[(method, scale)] if row["projection_distance_rad"]]) if any(row["projection_distance_rad"] for row in grouped[(method, scale)]) else np.nan for scale in scales]
        axes[0].plot(scales, rate, "o-", color=color, label=method)
        axes[1].plot(scales, after, "o-", color=color, label=method)
    axes[0].set_ylabel("projection success rate")
    axes[1].set_ylabel("mean correction distance / rad")
    for ax in axes:
        ax.set_xlabel("initial perturbation scale / rad")
        ax.grid(alpha=0.25)
        ax.legend()
    fig.suptitle("D082 NR/APC projection pilot (saved numerical records)")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit(f"refusing to overwrite existing asset directory: {OUT}")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_csv(STABILITY / "planner_trials.csv")
    projection = read_csv(NUMERIC / "projection_trials.csv")
    raw = read_gzip(STABILITY / "raw_planner/planner_E1_clutter_PCS_seed7.json.gz")
    plot_path(raw, OUT / "trajectory_E1_PCS_seed7.png")
    plot_path_metrics(raw, OUT / "trajectory_metrics_E1_PCS_seed7.png")
    plot_comparison(rows, OUT / "algorithm_comparison_paired.png")
    plot_projection(projection, OUT / "projection_success_and_correction.png")
    manifest = {
        "schema": "P4_D082_VIRTUAL_SIMULATION_ASSET_MANIFEST_V1",
        "classification": "PLOTS_FROM_SAVED_D081_REAL_NUMERICAL_RECORDS",
        "showcase": "results/20261019_D081_stability_pilot/raw_planner/planner_E1_clutter_PCS_seed7.json.gz",
        "figures": [str(path.relative_to(ROOT)) for path in sorted(OUT.glob("*.png"))],
        "source_runs": [str(NUMERIC.relative_to(ROOT)), str(STABILITY.relative_to(ROOT))],
        "display_only_fk_reconstruction": "sin(pi/38) for each of the 19 positive-length links; no state is requalified",
        "continuous_collision_certificate": False,
        "author_spatial_equivalence": False,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
