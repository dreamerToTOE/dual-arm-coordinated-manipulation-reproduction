#!/usr/bin/env python3
"""Independent saved-artifact audit for the D081 numerical pilot.

This audit reads CSV/JSON/gzip output only.  It does not import a scientific
model, call FK/IK/NR/RSS/PCS/RBS, start a planner, or modify the run.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def read_gzip(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path,
                        default=Path("results/20261019_D081_numeric_pilot"))
    args = parser.parse_args()
    root = args.run_dir.resolve()
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    config = json.loads((root / "config_snapshot.json").read_text(encoding="utf-8"))
    projection = read_csv(root / "projection_trials.csv")
    fig3 = read_csv(root / "fig3_pairs.csv")
    fig4 = read_csv(root / "fig4_visibility_pairs.csv")
    fig5 = read_csv(root / "fig5_distance_change.csv")
    planner = read_csv(root / "planner_trials.csv")
    checks = []

    def check(name, passed, **extra):
        item = {"name": name, "passed": bool(passed)}
        item.update(extra)
        checks.append(item)
        if not passed:
            raise AssertionError(name + " " + json.dumps(extra, ensure_ascii=False))

    check("pilot_status", summary["status"] == "PILOT_COMPLETED_REAL_NUMERICAL_DATA")
    check("formal_table_I_calls_zero", summary["formal_table_I_calls"] == 0)
    check("projection_row_count", len(projection) == 1536, observed=len(projection))
    check("fig3_row_count", len(fig3) == 900, observed=len(fig3))
    check("fig4_row_count", len(fig4) == 720, observed=len(fig4))
    check("fig5_row_count", len(fig5) == 768, observed=len(fig5))
    check("planner_row_count", len(planner) == 20, observed=len(planner))
    check("paired_projection_methods",
          {row["method"] for row in projection} == {"APC", "NR"})
    check("paired_visibility_methods",
          {row["method"] for row in fig4} == {"RSS", "PCS", "NR"})
    check("fig3_m_counts", {int(row["m"]) for row in fig3} == {1, 2, 3, 7, 16})
    check("fig3_m20_is_explicitly_unavailable",
          summary["fig3_m20_status"].startswith("UNAVAILABLE"))

    raw_dir = root / "raw_planner"
    for row in planner:
        raw = raw_dir / Path(row["artifact"]).name
        check("raw_artifact_exists", raw.is_file(), artifact=str(raw))
        payload = read_gzip(raw)
        check("raw_header_matches", payload["environment"] == row["environment"] and
              payload["method"] == row["method"] and int(payload["seed"]) == int(row["seed"]))
        check("raw_status_matches", payload["status"] == row["status"])
        if payload["status"] == "SUCCESS":
            path = payload["path"]
            metrics = payload["path_metrics"]
            check("success_path_nonempty", len(path) > 0)
            check("success_path_endpoints", path[0] == payload["start"] and path[-1] == payload["goal"])
            check("success_path_state_qualifications",
                  all(item["valid"] and item["closure_position"] <= 1e-8 and
                      item["closure_angle"] <= 1e-8 and
                      not item["collision"]["collision"]
                      for item in metrics["state_qualifications"]))
            check("success_path_leaf_distance",
                  metrics["maximum_adjacent_l2_rad"] <= 0.05 + 1e-12,
                  observed=metrics["maximum_adjacent_l2_rad"])
        else:
            check("failed_path_is_empty", payload["path"] == [])

    manifest = json.loads((root / "artifact_sha256.json").read_text(encoding="utf-8"))
    for rel, expected in manifest.items():
        path = root / rel
        check("artifact_sha256", path.is_file() and sha256(path) == expected, artifact=rel)

    result = {
        "schema": "P4_D081_NUMERICAL_PILOT_SAVED_AUDIT_V1",
        "status": "PASS_SAVED_ARTIFACT_INDEPENDENT_AUDIT",
        "run_dir": str(root),
        "scientific_calls": {"FK": 0, "IK": 0, "NR": 0, "RSS": 0,
                              "PCS": 0, "RBS": 0, "planner": 0, "author_source": 0},
        "checks_total": len(checks), "checks_passed": sum(int(x["passed"]) for x in checks),
        "checks": checks,
        "counts": {"projection": len(projection), "fig3": len(fig3), "fig4": len(fig4),
                   "fig5": len(fig5), "planner": len(planner)},
        "scope": "saved-data integrity and path qualification only; no new numerical result",
        "config_seed": config["paired_seed"]
    }
    out = root / "pilot_audit.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "checks_total", "checks_passed", "scientific_calls", "counts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
