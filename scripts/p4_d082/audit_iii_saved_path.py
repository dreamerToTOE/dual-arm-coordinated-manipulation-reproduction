#!/usr/bin/env python3
"""Recheck the preserved III path without starting the author executable.

This is a D082 evidence audit.  It reads the already saved 649-node queue and
the preserved per-node math/collision records, then writes a new qualification
record.  It does not call FK/IK, a collision process, a planner, or a source
binary.  Its PASS label is limited to the reconstructed/aligned discrete
source-policy path; it never upgrades native TCP equivalence or continuous CCD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01"
QUEUE = RUN / "complete_original_saved_queue.json"
OLD_POST = ROOT / "reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json"
SOURCE_RESULT = ROOT / "results/p4_full/20261018_R2_D080_III_RRT_PCS_SOURCE01/parsed_source_result.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def fail(checks, name, detail):
    checks.append({"name": name, "passed": False, "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reports/P4_D082_ENV_III_SAVED_PATH_INDEPENDENT_QUALIFICATION_20261019.json")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    checks = []
    queue = load(QUEUE)
    old_post = load(OLD_POST)
    source = load(SOURCE_RESULT)
    nodes = queue.get("nodes", [])
    expected_start = source["start_q12"]
    expected_goal = source["goal_q12"]
    checks.append({"name": "saved_post_is_independent_and_complete",
                   "passed": old_post.get("personnel_independent") is True and
                             str(old_post.get("status", "")).startswith("PASS_649_DISCRETE_SOURCE_POLICY") and
                             old_post.get("checks_total") == old_post.get("checks_passed") == 16})
    checks.append({"name": "queue_has_exact_649_nodes",
                   "passed": len(nodes) == 649, "observed": len(nodes)})
    checks.append({"name": "source_exact_endpoint_identity",
                   "passed": nodes and nodes[0] == expected_start and nodes[-1] == expected_goal})

    math_pass = 0
    collision_pass = 0
    branch_pass = 0
    native_pose_mismatch = 0
    aligned_pose_pass = 0
    finite = True
    max_pos = 0.0
    max_rot = 0.0
    min_clearance = None
    max_leaf = 0.0
    max_linf = 0.0
    failure_samples = []
    node_digest = hashlib.sha256()
    for index, q in enumerate(nodes):
        node = RUN / f"node_{index:05d}.json"
        math_path = RUN / f"node_{index:05d}_math.json"
        collision_path = RUN / f"node_{index:05d}_collision_response.json"
        for path in (node, math_path, collision_path):
            if not path.is_file():
                failure_samples.append({"node": index, "reason": "MISSING_FILE", "path": str(path)})
                finite = False
                continue
            node_digest.update(str(path.relative_to(ROOT)).encode())
            node_digest.update(sha256(path).encode())
        if not node.is_file() or not math_path.is_file() or not collision_path.is_file():
            continue
        math_row = load(math_path)
        collision = load(collision_path)
        q_ok = isinstance(q, list) and len(q) == 12 and all(isinstance(x, (int, float)) for x in q)
        finite = finite and q_ok
        closure = math_row.get("closure", {})
        pos = float(closure.get("position_max_abs", float("inf")))
        rot = float(closure.get("rotation_matrix_max_abs", float("inf")))
        max_pos = max(max_pos, pos)
        max_rot = max(max_rot, rot)
        limits_ok = math_row.get("limits", {}).get("legal") is True
        math_ok = math_row.get("math_qualified") is True and limits_ok and pos <= 1e-5 and rot <= 1e-5
        math_pass += int(math_ok)
        assignments = math_row.get("edge_assignments", [])
        branch_ok = bool(assignments) and all(a.get("branch_pass") is True for a in assignments)
        branch_pass += int(branch_ok)
        aligned = collision.get("variants", {}).get("aligned", {})
        native = collision.get("variants", {}).get("native", {})
        aligned_pose = aligned.get("pose_consistency", {}).get("passed") is True
        aligned_ok = (collision.get("status") == "CHECKED" and collision.get("collision") is False and
                      aligned.get("native_collision") is False and aligned_pose)
        collision_pass += int(aligned_ok)
        aligned_pose_pass += int(aligned_pose)
        native_pose_mismatch += int(native.get("pose_consistency", {}).get("passed") is not True)
        if not (math_ok and branch_ok and aligned_ok):
            failure_samples.append({"node": index, "math": math_ok, "branch": branch_ok,
                                    "aligned_collision": aligned_ok})
        for value in (q,):
            if not all(abs(float(x)) < float("inf") for x in value):
                finite = False

        # The saved queue is the source-policy path order.  Retain the full
        # adjacent-distance statistic, without treating it as a CCD proof.
        if index:
            import math as _math
            delta = [float(a) - float(b) for a, b in zip(nodes[index], nodes[index - 1])]
            max_leaf = max(max_leaf, _math.sqrt(sum(x * x for x in delta)))
            max_linf = max(max_linf, max(abs(x) for x in delta))

    checks.append({"name": "all_saved_math_records_pass", "passed": math_pass == len(nodes),
                   "passed_nodes": math_pass, "total_nodes": len(nodes),
                   "max_position_abs_mm": max_pos, "max_rotation_abs": max_rot})
    checks.append({"name": "all_saved_branch_records_pass", "passed": branch_pass == len(nodes),
                   "passed_nodes": branch_pass, "total_nodes": len(nodes)})
    checks.append({"name": "all_saved_aligned_collision_records_pass",
                   "passed": collision_pass == len(nodes), "passed_nodes": collision_pass,
                   "total_nodes": len(nodes), "aligned_pose_pass": aligned_pose_pass,
                   "native_pose_mismatch_nodes": native_pose_mismatch})
    checks.append({"name": "saved_nodes_are_finite", "passed": finite})
    checks.append({"name": "saved_leaf_distance_is_bounded",
                   "passed": max_leaf < 0.05, "max_adjacent_l2_rad": max_leaf,
                   "max_adjacent_linf_rad": max_linf, "threshold_rad": 0.05})

    status = "PASS_D082_RECONSTRUCTED_ALIGNED_DISCRETE_PATH" if all(c["passed"] for c in checks) else "FAIL_D082_SAVED_PATH_RECHECK"
    result = {
        "schema": "P4_D082_III_SAVED_PATH_INDEPENDENT_QUALIFICATION_V1",
        "status": status,
        "independent_path_qualified": status.startswith("PASS_"),
        "classification": "RECONSTRUCTED_ALIGNED_SOURCE_POLICY_DISCRETE_ONLY",
        "source_environment": "III",
        "method": "PCS",
        "planner": "RRT",
        "node_count": len(nodes),
        "edge_count": max(0, len(nodes) - 1),
        "max_adjacent_l2_rad": max_leaf,
        "max_adjacent_linf_rad": max_linf,
        "max_position_abs_mm": max_pos,
        "max_rotation_abs": max_rot,
        "native_pose_mismatch_nodes": native_pose_mismatch,
        "minimum_clearance_m": min_clearance,
        "continuous_collision_certificate": False,
        "native_tcp_equivalence": False,
        "new_source_or_model_calls": 0,
        "new_planner_calls": 0,
        "checks_total": len(checks),
        "checks_passed": sum(int(c["passed"]) for c in checks),
        "checks": checks,
        "failure_samples": failure_samples[:20],
        "inputs": {
            "queue": str(QUEUE.relative_to(ROOT)), "queue_sha256": sha256(QUEUE),
            "old_independent_post": str(OLD_POST.relative_to(ROOT)), "old_post_sha256": sha256(OLD_POST),
            "source_result": str(SOURCE_RESULT.relative_to(ROOT)), "source_result_sha256": sha256(SOURCE_RESULT),
            "node_records_aggregate_sha256": node_digest.hexdigest(),
        },
        "scope_statement": "Only the preserved reconstructed/aligned discrete nodes and saved per-node records are requalified; native TCP mismatch and continuous collision remain unproved.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k: result[k] for k in ("status", "node_count", "checks_total", "checks_passed", "max_position_abs_mm", "max_adjacent_l2_rad", "native_pose_mismatch_nodes")}, ensure_ascii=False))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
