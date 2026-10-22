#!/usr/bin/env python3
"""Audit the saved D081 numerical runs as D082 virtual-simulation evidence.

The audit is deliberately read-only with respect to scientific execution.  It
opens saved CSV/JSON/gzip records, rechecks path provenance and hashes, and
reports the D082 scope.  It never calls FK, IK, NR, RSS, PCS, RBS, a planner,
or an author executable.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NUMERIC = ROOT / "results/20261019_D081_numeric_pilot"
STABILITY = ROOT / "results/20261019_D081_stability_pilot"
III_AUDIT = ROOT / "reports/P4_D082_ENV_III_SAVED_PATH_INDEPENDENT_QUALIFICATION_20261019_v2.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def read_gzip(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports/P4_D082_VIRTUAL_SIMULATION_SAVED_AUDIT_20261020.json",
    )
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing audit: {output}")

    checks = []

    def check(name: str, passed: bool, **extra):
        row = {"name": name, "passed": bool(passed)}
        row.update(extra)
        checks.append(row)

    numeric_summary = load_json(NUMERIC / "summary.json")
    numeric_config = load_json(NUMERIC / "config_snapshot.json")
    numeric_rows = read_csv(NUMERIC / "planner_trials.csv")
    stability_summary = load_json(STABILITY / "planner_summary.json")
    stability_rows = read_csv(STABILITY / "planner_trials.csv")
    stability_manifest = load_json(STABILITY / "artifact_sha256.json")

    check("numeric_pilot_completed", numeric_summary.get("status") == "PILOT_COMPLETED_REAL_NUMERICAL_DATA")
    check("numeric_formal_table_calls_zero", numeric_summary.get("formal_table_I_calls") == 0)
    check("numeric_planner_row_count", len(numeric_rows) == 20, observed=len(numeric_rows))
    check("numeric_methods_and_environments", {
        row["method"] for row in numeric_rows
    } == {"RSS", "PCS", "PCS_FIXED_0", "PCS_FIXED_16", "NR"} and {
        row["environment"] for row in numeric_rows
    } == {"E0_sparse", "E1_clutter"})
    check("stability_pilot_completed", stability_summary.get("status") == "PILOT_COMPLETED_REAL_NUMERICAL_DATA")
    check("stability_formal_table_calls_zero", stability_summary.get("formal_table_I_calls") == 0)
    check("stability_planner_row_count", len(stability_rows) == 50, observed=len(stability_rows))
    check("stability_pre_registered", stability_summary.get("sample_design", {}).get("pre_registered", {}).get("status") == "PILOT_ONLY_NOT_FORMAL_TABLE_I")

    success_count = 0
    failure_count = 0
    qualified_states = 0
    path_lengths = []
    showcase = None

    def audit_raw(row, raw_dir: Path, label: str):
        nonlocal success_count, failure_count, qualified_states, showcase
        artifact = row.get("artifact", "")
        raw = raw_dir / Path(artifact).name
        check(f"{label}_raw_exists", raw.is_file(), artifact=str(raw))
        if not raw.is_file():
            return
        payload = read_gzip(raw)
        header_ok = payload.get("environment") == row.get("environment") and payload.get("method") == row.get("method") and int(payload.get("seed")) == int(row.get("seed"))
        check(f"{label}_header_matches", header_ok, artifact=str(raw))
        status = payload.get("status")
        check(f"{label}_status_matches", status == row.get("status"), observed=(status, row.get("status")))
        if status == "SUCCESS":
            success_count += 1
            path = payload.get("path", [])
            metrics = payload.get("path_metrics") or {}
            check(f"{label}_path_nonempty", bool(path), observed=len(path))
            check(f"{label}_path_endpoints", bool(path) and path[0] == payload.get("start") and path[-1] == payload.get("goal"))
            states = metrics.get("state_qualifications", [])
            state_ok = len(states) == len(path) and all(
                state.get("valid") is True
                and float(state.get("closure_position", float("inf"))) <= 1e-8
                and float(state.get("closure_angle", float("inf"))) <= 1e-8
                and not state.get("collision", {}).get("collision", True)
                for state in states
            )
            qualified_states += sum(1 for state in states if state.get("valid") is True)
            check(f"{label}_all_states_qualified", state_ok, state_count=len(states), path_count=len(path))
            maximum_leaf = float(metrics.get("maximum_adjacent_l2_rad", float("inf")))
            check(f"{label}_leaf_bound", maximum_leaf <= 0.05 + 1e-12, observed=maximum_leaf)
            path_lengths.append(float(metrics.get("joint_path_length_rad", float("nan"))))
            if showcase is None and payload.get("environment") == "E1_clutter" and payload.get("method") == "PCS" and int(payload.get("seed")) == 7:
                showcase = {"raw": str(raw.relative_to(ROOT)), "payload": payload}
        else:
            failure_count += 1
            check(f"{label}_failed_path_empty", payload.get("path") == [], observed=status)

    for index, row in enumerate(numeric_rows):
        audit_raw(row, NUMERIC / "raw_planner", f"numeric_{index:02d}")
    for index, row in enumerate(stability_rows):
        audit_raw(row, STABILITY / "raw_planner", f"stability_{index:02d}")

    manifest_ok = True
    for relative, expected in stability_manifest.items():
        path = STABILITY / relative
        if not path.is_file() or sha256(path) != expected:
            manifest_ok = False
            break
    check("stability_artifact_manifest", manifest_ok, entries=len(stability_manifest))

    iii = load_json(III_AUDIT)
    check("iii_saved_path_independent_qualification", iii.get("status") == "PASS_D082_RECONSTRUCTED_ALIGNED_DISCRETE_PATH" and iii.get("checks_passed") == iii.get("checks_total") == 8)
    check("showcase_path_available", showcase is not None)

    success_by_method = {}
    for method in ("RSS", "PCS", "PCS_FIXED_0", "PCS_FIXED_16", "NR"):
        rows = [row for row in stability_rows if row["method"] == method]
        successes = sum(row["status"] == "SUCCESS" for row in rows)
        success_by_method[method] = {"success": successes, "total": len(rows), "rate": successes / len(rows) if rows else None}

    result = {
        "schema": "P4_D082_VIRTUAL_SIMULATION_SAVED_AUDIT_V1",
        "status": "PASS_D082_RECONSTRUCTED_VIRTUAL_SIMULATION_DISCRETE_ONLY" if all(row["passed"] for row in checks) else "FAIL_D082_VIRTUAL_SIMULATION_SAVED_AUDIT",
        "classification": "RECONSTRUCTED_PLANAR_20R_TASK_WITH_REAL_GEOS_DISCRETE_RBS",
        "scientific_calls_during_audit": {"FK": 0, "IK": 0, "NR": 0, "RSS": 0, "PCS": 0, "RBS": 0, "planner": 0, "author_source": 0},
        "new_display_reconstruction": "planar vertices are reconstructed only for plotting from saved q; no qualification result is recomputed",
        "checks_total": len(checks),
        "checks_passed": sum(int(row["passed"]) for row in checks),
        "checks": checks,
        "planner_calls_reused": {"numeric_pilot": len(numeric_rows), "stability_pilot": len(stability_rows), "total": len(numeric_rows) + len(stability_rows)},
        "path_states_requalified": qualified_states,
        "success_paths_requalified": success_count,
        "failed_or_timeout_calls_requalified": failure_count,
        "success_by_method_stability": success_by_method,
        "mean_success_path_length_rad": (sum(path_lengths) / len(path_lengths) if path_lengths else None),
        "showcase": None if showcase is None else {"raw": showcase["raw"], "environment": showcase["payload"]["environment"], "method": showcase["payload"]["method"], "seed": showcase["payload"]["seed"], "path_points": len(showcase["payload"].get("path", [])), "path_metrics": showcase["payload"].get("path_metrics")},
        "inputs": {
            "numeric_summary": str((NUMERIC / "summary.json").relative_to(ROOT)),
            "numeric_summary_sha256": sha256(NUMERIC / "summary.json"),
            "numeric_config": str((NUMERIC / "config_snapshot.json").relative_to(ROOT)),
            "numeric_config_sha256": sha256(NUMERIC / "config_snapshot.json"),
            "stability_summary": str((STABILITY / "planner_summary.json").relative_to(ROOT)),
            "stability_summary_sha256": sha256(STABILITY / "planner_summary.json"),
            "iii_saved_audit": str(III_AUDIT.relative_to(ROOT)),
            "iii_saved_audit_sha256": sha256(III_AUDIT),
        },
        "scope_statement": "真实运行来自D081已保存的NumPy/GEOS平面重建；本审计确认端到端离散闭链路径与算法对照证据，但不升级为原论文空间II-V/VI完整统计、连续CCD或作者原生实现。",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "checks_total", "checks_passed", "success_paths_requalified", "failed_or_timeout_calls_requalified", "path_states_requalified")}, ensure_ascii=False))
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
