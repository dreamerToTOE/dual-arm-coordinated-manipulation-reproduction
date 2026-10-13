#!/usr/bin/env python3
"""Portable, read-only audit of saved P4 data and independent planar geometry.

Uses only Python's standard library. Does not import the planner, its model,
Shapely, or any simulator. An optional new output file is created exclusively.
Historical absolute source paths are relocated without editing their records.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
import zipfile


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/20261013_P4_three_methods_round3"
OBSTACLES = {
    "E0_sparse": [(0.45, 0.72, 0.045)],
    "E1_clutter": [(0.45, 0.72, 0.045), (0.50, 0.18, 0.065),
                   (0.72, 0.60, 0.05)],
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def point_distance(point, a, b):
    delta = (b[0] - a[0], b[1] - a[1])
    denominator = delta[0] ** 2 + delta[1] ** 2
    t = 0.0 if denominator == 0 else min(1.0, max(0.0,
        ((point[0] - a[0]) * delta[0] + (point[1] - a[1]) * delta[1]) / denominator))
    return math.hypot(point[0] - a[0] - t * delta[0], point[1] - a[1] - t * delta[1])


def segment_distance(a, b, c, d):
    # Intersection including collinear overlap, followed by endpoint distances.
    bounding_overlap = all(max(min(a[k], b[k]), min(c[k], d[k])) <=
                           min(max(a[k], b[k]), max(c[k], d[k])) for k in (0, 1))
    if (bounding_overlap and orientation(a, b, c) * orientation(a, b, d) <= 0 and
            orientation(c, d, a) * orientation(c, d, b) <= 0):
        return 0.0
    return min(point_distance(a, c, d), point_distance(b, c, d),
               point_distance(c, a, b), point_distance(d, a, b))


def independent_state(q, environment):
    require(len(q) == 20 and all(math.isfinite(x) and -math.pi <= x <= math.pi for x in q),
            "saved joint vector invalid")
    length = math.sin(math.pi / 38)
    vertices = [(0.0, 0.0)]
    angle = 0.0
    for value in q[:19]:
        angle += value
        x, y = vertices[-1]
        vertices.append((x + length * math.cos(angle), y + length * math.sin(angle)))
    position = math.hypot(vertices[-1][0] - 1.0, vertices[-1][1])
    rotation = abs(math.atan2(math.sin(sum(q)), math.cos(sum(q))))
    require(position <= 1e-8 and rotation <= 1e-8, "saved closure invalid")
    segments = list(zip(vertices[:-1], vertices[1:])) + [((1.0, 0.0), (0.0, 0.0))]
    clearance = min(segment_distance(*segments[i], *segments[j]) - 0.004
                    for i in range(20) for j in range(i + 1, 20)
                    if j != i + 1 and (i, j) != (0, 19))
    for x, y, radius in OBSTACLES[environment]:
        clearance = min(clearance, *(point_distance((x, y), *segment) - radius - 0.002
                                    for segment in segments))
    require(clearance > 0.0, "independent saved-path collision")
    return position, rotation, clearance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional NEW JSON file; existing files refused")
    args = parser.parse_args()
    snapshot = read(ROOT / "reports/P4_THREE_METHOD_HANDOFF_SNAPSHOT.json")
    for name, item in snapshot["files"].items():
        require(digest(ROOT / name) == item["sha256"], "handoff file changed: " + name)
    protected = read(RUN / "protected_sha256.json")
    for name, expected in protected.items():
        require(digest(ROOT / name) == expected, "historical protected file changed: " + name)
    metadata = read(RUN / "metadata.json")["run_metadata"]["data"]
    recorded_root = Path(metadata["config_paths"][0]).parents[2]
    source_map = read(RUN / "source_sha256.json")
    for name, expected in source_map.items():
        path = Path(name)
        relative = path.relative_to(recorded_root) if path.is_absolute() else path
        require(digest(ROOT / relative) == expected, "scientific source changed: " + name)
    config, trials, summary = (read(RUN / name) for name in
                               ("config_snapshot.json", "trials.json", "summary.json"))
    expected = set(itertools.product(config["environments"], config["outer_iteration_budgets"],
                                     config["methods"], config["seeds"]))
    observed = [(r["environment"], r["budget"], r["method"], r["seed"]) for r in trials]
    require(len(trials) == 60 and len(set(observed)) == 60 and set(observed) == expected,
            "registered trial coverage differs")
    points = 0
    maxima = {"position_m": 0.0, "rotation_rad": 0.0, "clearance_record_difference_m": 0.0}
    partitions, status_counts, aggregate = Counter(), {}, {}
    for row in trials:
        artifact = RUN / row["artifact"]
        require(digest(artifact) == row["sha256"], "trial raw hash differs")
        raw = read(artifact)
        require(not row["repeat"] and raw["config"] == config["algorithm"], "trial config differs")
        for a, b in [("environment", "environment"), ("method", "method"), ("seed", "seed"),
                     ("budget", "max_iterations"), ("status", "status"), ("nodes", "node_count"),
                     ("wall_sec", "compute_wall_time_sec"), ("counters", "counters"),
                     ("failure_counts", "failure_counts")]:
            require(row[a] == raw[b], "trial row/raw differs: " + a)
        method = raw["method"]
        require(raw["counters"].get("nr_calls", 0) == 0 if method != "NR" else
                raw["counters"].get("ik_calls", 0) == 0, "strategy substitution detected")
        if raw["status"] != "SUCCESS":
            require(raw["path"] == [] and row["path_metrics"] is None, "failure contains claimed path")
            continue
        path = raw["path"]
        require(path[0] == raw["start"] and path[-1] == raw["goal"], "saved endpoints differ")
        saved = raw["path_metrics"]["state_qualifications"]
        require(len(saved) == len(path), "path qualification count differs")
        for q, state in zip(path, saved):
            position, rotation, clearance = independent_state(q, raw["environment"])
            difference = abs(clearance - state["collision"]["minimum_clearance"])
            require(difference <= 1e-10, "independent geometry differs from GEOS record")
            maxima["position_m"] = max(maxima["position_m"], position)
            maxima["rotation_rad"] = max(maxima["rotation_rad"], rotation)
            maxima["clearance_record_difference_m"] = max(maxima["clearance_record_difference_m"], difference)
            points += 1
        distances = [math.sqrt(sum((b - a) ** 2 for a, b in zip(first, second)))
                     for first, second in zip(path[:-1], path[1:])]
        require(max(distances, default=0) <= 0.05 + 1e-12, "saved RBS leaf distance invalid")
        require(abs(sum(distances) - row["path_metrics"]["joint_path_length_rad"]) <= 1e-9,
                "saved path length differs")
        for edge in raw["path_edges"]:
            attempt = raw["attempts"][edge["attempt_index"]]
            require(attempt["accepted"] and attempt["connection"]["success"], "invalid edge source")
            partition = edge["partition"]
            require(partition == attempt["connection"]["partition"], "edge partition differs")
            require(partition in (0, 16) if method == "PCS" else partition is None,
                    "solution edge method invalid")
            partitions[f"{method}:{partition}"] += 1
    for method in config["methods"]:
        rows = [r for r in trials if r["method"] == method]
        status_counts[method] = dict(Counter(r["status"] for r in rows))
        aggregate[method] = {"trials": len(rows), "successes": sum(r["status"] == "SUCCESS" for r in rows),
                             "mean_all_call_seconds": statistics.mean(r["wall_sec"] for r in rows),
                             "mean_tree_nodes": statistics.mean(r["nodes"] for r in rows)}
    require(status_counts == {"RSS": {"TIME_LIMIT": 20}, "PCS": {"SUCCESS": 20},
                              "NR": {"SUCCESS": 20}}, "recorded final outcomes differ")
    assets = read(ROOT / "reports/p4_three_assets/report_data.json")
    require(assets["summary"] == summary and assets["trials"] == trials, "figure inputs differ")
    for name, expected_hash in assets["source_sha256"].items():
        require(digest(ROOT / name) == expected_hash, "figure source hash differs")
    with zipfile.ZipFile(ROOT / "reports/P4_三方法复现汇总.docx") as document:
        xml = document.read("word/document.xml").decode()
    result = {"saved_evidence_verified": True, "independent_geometry_verified": True,
              "snapshot_files_unchanged": len(snapshot["files"]),
              "historical_files_unchanged": len(protected), "scientific_sources_unchanged": len(source_map),
              "statistical_trials": len(trials), "repeat_artifacts": len(summary["deterministic_repeats"]),
              "successful_path_points_independently_rechecked": points,
              "independent_geometry_maxima": maxima, "solution_edge_partitions": dict(partitions),
              "aggregates": aggregate, "status_counts": status_counts,
              "editable_equations": xml.count("<m:oMath>"), "embedded_figures": xml.count("<w:drawing>"),
              "new_planning_calls": 0, "new_random_samples": 0, "physical_runs": 0,
              "scientific_status": "部分完成：RSS全局路径失败；重建模型非原输入；RSS完整重复未通过"}
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
