#!/usr/bin/env python3
"""Run a pre-registered D081 planner stability pilot.

This is a small paired extension of the first D081 planar proxy pilot.  It
uses the same two frozen environments and the same five methods for every
seed.  The seed list is stored in the config before execution; no scene or
seed is selected after observing a result.  The output is still pilot data,
never the original paper's spatial Table I statistics.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import platform
import subprocess
import time
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs/p4_d081/numeric_stability_pilot_v1.json"
BASE_SCRIPT = ROOT / "scripts/p4_d081_numeric_pilot.py"


def load_base_module():
    spec = importlib.util.spec_from_file_location("p4_d081_numeric_pilot", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load D081 base pilot module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wilson(success, total, z=1.959963984540054):
    if total <= 0:
        return None, None
    p = float(success) / float(total)
    denom = 1.0 + z * z / total
    centre = (p + z * z / (2.0 * total)) / denom
    half = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def write_rows(path: Path, rows):
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


def make_plot(rows, output):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["environment"], row["method"])].append(row)
    envs = ["E0_sparse", "E1_clutter"]
    methods = ["RSS", "PCS", "PCS_FIXED_0", "PCS_FIXED_16", "NR"]
    x = np.arange(len(methods))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharex=True)
    for ax, env in zip(axes, envs):
        means, lows, highs, walls = [], [], [], []
        for method in methods:
            group = grouped[(env, method)]
            successes = sum(bool(row["success"]) for row in group)
            low, high = wilson(successes, len(group))
            means.append(successes / len(group))
            lows.append(means[-1] - low)
            highs.append(high - means[-1])
            walls.append(float(np.mean([float(row["wall_sec"]) for row in group])))
        ax.errorbar(x, means, yerr=np.vstack([lows, highs]), fmt="o", capsize=4,
                    color="tab:blue", label="success rate, Wilson 95% CI")
        ax.set_title(env)
        ax.set_ylim(-0.05, 1.08)
        ax.set_ylabel("success rate")
        ax.grid(axis="y", alpha=0.3)
        ax2 = ax.twinx()
        ax2.plot(x, walls, "s--", color="tab:orange", label="mean wall time")
        ax2.set_ylabel("mean wall time / s")
        ax.set_xticks(x, ["RSS", "PCS", "fixed-0", "fixed-16", "NR"], rotation=35, ha="right")
    fig.suptitle("D081 paired planar stability pilot (n=5 seeds per method/environment)")
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/20261019_D081_stability_pilot")
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
    base = load_base_module()
    base_config = json.loads((ROOT / config["base_protocol"]).read_text(encoding="utf-8"))
    merged = dict(base_config)
    for key, value in config.items():
        if key.startswith("planner_"):
            merged[key] = value
    merged["planner_seeds"] = list(config["paired_seeds"])
    merged["planner_methods"] = list(config["planner_methods"])
    merged["planner_environments"] = list(config["planner_environments"])
    start = time.perf_counter()
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    git_status = subprocess.check_output(["git", "status", "--short", "--branch"], cwd=ROOT, text=True)
    save_json(output / "config_snapshot.json", config)
    save_json(output / "run_metadata.json", {
        "schema": "P4_D081_NUMERICAL_STABILITY_PILOT_RUN_V1",
        "run_id": output.name,
        "started_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "git_head": git_head,
        "git_status_at_start": git_status,
        "python": __import__("sys").version,
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "platform": platform.platform(),
        "scientific_scope": "paired planar proxy planner only",
        "formal_table_I_calls": 0,
        "author_source_calls": 0,
        "hardware_or_isaac_calls": 0,
        "base_protocol": config["base_protocol"],
        "source_files": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (CONFIG_PATH, BASE_SCRIPT,
                         ROOT / "baselines/p4_comparison/model.py",
                         ROOT / "baselines/p4_comparison/strategies.py",
                         ROOT / "baselines/p4_comparison/planner.py")
        }
    })
    model = base.PlanarModel()
    rows, algorithm = base.run_planner_pilot(model, merged, raw_dir)
    base.csv_write(output / "planner_trials.csv", rows)
    aggregate = base.aggregate_planner(rows)
    summary_rows = []
    for row in aggregate:
        low, high = wilson(row["success"], row["sample_n"])
        summary_rows.append({**row, "success_rate_ci95_low": low,
                             "success_rate_ci95_high": high,
                             "pilot_label": "PLANAR_PROXY_NOT_ORIGINAL_TABLE_I"})
    pair_rows = []
    for env in config["planner_environments"]:
        for seed in config["paired_seeds"]:
            group = {(row["environment"], row["method"], int(row["seed"])): row for row in rows}
            key = lambda method: group[(env, method, int(seed))]
            pcs, fixed0, fixed16, nr, rss = (key(name) for name in
                                              ("PCS", "PCS_FIXED_0", "PCS_FIXED_16", "NR", "RSS"))
            pair_rows.append({
                "environment": env, "seed": int(seed),
                "pcs_success": bool(pcs["success"]),
                "fixed0_success": bool(fixed0["success"]),
                "fixed16_success": bool(fixed16["success"]),
                "nr_success": bool(nr["success"]),
                "rss_success": bool(rss["success"]),
                "pcs_minus_fixed16_wall_sec": float(pcs["wall_sec"]) - float(fixed16["wall_sec"]),
                "pcs_minus_nr_wall_sec": float(pcs["wall_sec"]) - float(nr["wall_sec"]),
                "pcs_minus_fixed16_path_length_rad": (None if pcs["path_length_rad"] is None or fixed16["path_length_rad"] is None
                                                        else float(pcs["path_length_rad"]) - float(fixed16["path_length_rad"])),
                "pcs_minus_nr_path_length_rad": (None if pcs["path_length_rad"] is None or nr["path_length_rad"] is None
                                                  else float(pcs["path_length_rad"]) - float(nr["path_length_rad"])),
            })
    write_rows(output / "paired_seed_comparison.csv", pair_rows)
    save_json(output / "planner_summary.json", {
        "schema": "P4_D081_NUMERICAL_STABILITY_PILOT_SUMMARY_V1",
        "status": "PILOT_COMPLETED_REAL_NUMERICAL_DATA",
        "elapsed_wall_sec": time.perf_counter() - start,
        "sample_design": {
            "environments": config["planner_environments"],
            "methods": config["planner_methods"],
            "seeds": config["paired_seeds"],
            "calls": len(rows),
            "paired": True,
            "pre_registered": config["pre_registration"]
        },
        "rows": summary_rows,
        "paired_seed_comparison": pair_rows,
        "algorithm_config": algorithm,
        "formal_table_I_calls": 0,
        "original_table_I_denominator": config["scope"]["original_table_I_denominator"],
        "limitations": [
            "This is a five-seed planar proxy pilot, not spatial environments II-V or the original 500 trials per cell.",
            "The same frozen E0/E1 scenes and all methods were run for every pre-registered seed.",
            "Discrete RBS/GEOS qualification does not certify continuous swept collision."
        ],
        "source_labels": {"paper_method_control_flow": "ORIGINAL",
                          "planar_geometry_and_collision": "RECONSTRUCTED",
                          "fixed_partition_ablation": "RECONSTRUCTED_ABLATION"}
    })
    make_plot(rows, plots / "stability_success_and_cost.png")
    manifest = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "artifact_sha256.json":
            manifest[str(path.relative_to(output))] = sha256(path)
    save_json(output / "artifact_sha256.json", manifest)
    print(json.dumps({"output": str(output), "elapsed_wall_sec": time.perf_counter() - start,
                      "planner_rows": len(rows), "formal_table_I_calls": 0}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
