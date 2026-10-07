#!/usr/bin/env python3
"""[ENGINEERING] Read-only audit of TASK01 full-chain geometry artifacts.

This verifier reads stored evidence and hashes only. It does not run IK/FCL,
Isaac, controllers, robot commands, or suction commands. PASS_ARTIFACT_ONLY is
not model parity, reset readiness, dynamics, or a continuous collision proof.
The original config_at_run.yaml is authoritative, not today's working YAML.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys


DISTANCE_KEYS = (
    "minimum_fcl_distance",
    "minimum_self_and_inter_arm_fcl_distance",
    "minimum_inter_arm_fcl_distance",
    "minimum_robot_world_fcl_distance",
    "minimum_robot_environment_excluding_cube_fcl_distance",
    "minimum_wrist_tool_environment_fcl_distance",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self):
        self.assertions = 0

    def check(self, condition, name):
        self.assertions += 1
        if not condition:
            raise ValueError(name)

    def finite(self, value, name):
        if isinstance(value, dict):
            for key, item in value.items():
                self.finite(item, name + "/" + key)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                self.finite(item, name + "/" + str(index))
        elif isinstance(value, float):
            self.check(math.isfinite(value), "nonfinite number: " + name)


def verify(repo, evidence, audit):
    load = lambda name: json.loads((evidence / name).read_text())
    rows = load("state_records.json")
    full = load("full_chain_results.json")
    summary = load("summary.json")
    meta = load("metadata.json")
    start = load("start_joint_state_candidate.json")
    with (evidence / "per_state_minimum_fcl_distance.csv").open() as file:
        csv_rows = list(csv.DictReader(file))
    a = [row for row in rows if row["segment"] == "A_tight_transport"]
    b = [row for row in rows if row["segment"] == "B_constrained_insertion"]
    audit.check((len(rows), len(a), len(b)) == (293, 136, 157), "record counts")
    audit.check([row["state_index"] for row in rows] == list(range(293)), "state indices")
    audit.check(len({tuple(row["cube_center_world_m"]) for row in rows}) == 292, "unique states")
    audit.check(a[-1]["cube_center_world_m"] == b[0]["cube_center_world_m"], "PRE_PUSH seam pose")
    audit.check(a[0]["cube_center_world_m"] == [0.55, 0.0, 0.38], "approved START")
    audit.check(a[-1]["cube_center_world_m"] == [0.79, 0.0, 0.26], "approved PRE_PUSH")
    audit.check(b[-1]["cube_center_world_m"] == [1.1, 0.0, 0.26], "approved TARGET")
    for arm in ("left", "right"):
        audit.check(a[-1][arm + "_q_rad"] == b[0][arm + "_q_rad"], "exact 14q seam " + arm)
    audit.check(b[0]["ik_disposition"] == "REUSED_EXACT_A_PRE_PUSH_Q_NO_RE_IK", "no seam re-IK")
    audit.check(b[0]["seam_source_state_index"] == a[-1]["state_index"], "seam source index")
    maximum_steps = {}
    for name, segment in (("A", a), ("B", b)):
        audit.check([row["segment_index"] for row in segment] == list(range(len(segment))), "segment indices " + name)
        steps = [math.dist(x["cube_center_world_m"], y["cube_center_world_m"])
                 for x, y in zip(segment, segment[1:])]
        maximum_steps[name] = max(steps)
        audit.check(max(steps) <= 0.002 + 1e-14, "translation sampling " + name)
        s = full["segments"][name]
        audit.check(s == summary["segments"][name] == meta["metrics"]["segments"][name], "three segment summaries " + name)
        audit.check(s["states_checked"] == len(segment) == s["states_passed"] == s["planned_states"], "complete segment count " + name)
        audit.check(s["complete_segment_checked"] and s["status"] == "PASS_SAMPLED_SEGMENT", "complete segment status " + name)
        audit.check(s["minimum_joint_margin_rad"] == min(row["min_joint_margin_rad"] for row in segment), "margin aggregation " + name)
        for field, scalar in (("max_grasp_translation_m", "translation_m"), ("max_grasp_rotation_rad", "rotation_rad")):
            observed = max(row[arm + "_relative_grasp_error"][scalar]
                           for row in segment for arm in ("left", "right"))
            audit.check(s[field] == observed, "residual aggregation " + name + "/" + field)
        audit.check(s["cube_environment_checks"] == len(segment) * 4 and s["cube_environment_penetrations"] == 0, "Cube geometry aggregation " + name)
        for key in ("minimum_fcl_distance", "minimum_wrist_tool_environment_fcl_distance"):
            row = min(segment, key=lambda item: item[key]["signed_distance_m"])
            expected = dict(row[key], state_index=row["state_index"], segment_index=row["segment_index"],
                            cube_center_world_m=row["cube_center_world_m"])
            audit.check(s[key] == expected, "minimum distance aggregation " + name + "/" + key)
    for row in rows:
        idx = str(row["state_index"])
        audit.check(row["cube_orientation_xyzw"] == [0.0, 0.0, 0.0, 1.0], "fixed orientation " + idx)
        audit.check(all(row[key] == expected for key, expected in (
            ("status", "PASS_DISCRETE_GEOMETRY"), ("fcl", "PASS"),
            ("joint_limit", "PASS"), ("shared_grasp_acceptance", "PASS"))), "state status " + idx)
        audit.check(all(row[key] == [] for key in (
            "collision_pairs", "self_and_inter_arm_collision_pairs", "robot_world_collision_pairs")), "collision lists " + idx)
        cube = row["cube_environment_geometry"]
        audit.check(cube["status"] == "PASS" and len(cube["checks"]) == 4
                    and not any(check["volumetric_penetration"] for check in cube["checks"]), "Cube environment geometry " + idx)
        for arm in ("left", "right"):
            audit.check(len(row[arm + "_q_rad"]) == 7, "joint count " + idx + "/" + arm)
            error = row[arm + "_relative_grasp_error"]
            audit.check(error["translation_m"] <= 1e-5 and error["rotation_rad"] <= 1e-4, "original residual guards " + idx + "/" + arm)
        for key in DISTANCE_KEYS:
            d = row[key]
            audit.check(isinstance(d["signed_distance_m"], (int, float))
                        and math.isfinite(d["signed_distance_m"]) and d["signed_distance_m"] > 0, "finite positive distance " + idx + "/" + key)
            audit.check(all(isinstance(d[body], str) and d[body] for body in ("body1", "body2")), "exact pair " + idx + "/" + key)
            for nearest in ("nearest_point_1_world_m", "nearest_point_2_world_m"):
                audit.check(len(d[nearest]) == 3 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in d[nearest]), "finite nearest point " + idx + "/" + key)
    for name, value in (("rows", rows), ("full", full), ("summary", summary), ("metadata", meta)):
        audit.finite(value, name)
    audit.check(len(csv_rows) == len(rows) * len(DISTANCE_KEYS), "CSV row count")
    seen = set()
    for item in csv_rows:
        idx, key = int(item["state_index"]), item["category"]
        audit.check((idx, key) not in seen and key in DISTANCE_KEYS, "CSV duplicate/category")
        seen.add((idx, key))
        row, d = rows[idx], rows[idx][key]
        audit.check(item["segment"] == row["segment"] and int(item["segment_index"]) == row["segment_index"], "CSV segment")
        audit.check([float(item[k]) for k in ("cube_x_m", "cube_y_m", "cube_z_m")] == row["cube_center_world_m"], "CSV pose")
        audit.check(float(item["signed_distance_m"]) == d["signed_distance_m"]
                    and item["body1"] == d["body1"] and item["body2"] == d["body2"], "CSV distance/pair")
    for key, minimum in summary["minimum_states"].items():
        row = min(rows, key=lambda item: item[key]["signed_distance_m"])
        audit.check(minimum == {"state_index": row["state_index"], "segment": row["segment"],
                    "segment_index": row["segment_index"], "cube_center_world_m": row["cube_center_world_m"],
                    "pair": row[key]}, "full-chain minimum " + key)
    audit.check(summary == meta["metrics"], "metadata metrics")
    audit.check(summary["start"] == {arm: a[0][arm + "_q_rad"] for arm in ("left", "right")}, "START joint capture")
    audit.check(summary["pre"] == {arm: a[-1][arm + "_q_rad"] for arm in ("left", "right")}, "PRE_PUSH joint capture")
    audit.check(start["benchmark_a_start_joint_state_rad"] == summary["start"], "START candidate file")
    audit.check(start["status"] == "START_JOINT_STATE_CANDIDATE_NOT_FROZEN" and not start["is_task27_feed_pose"], "candidate scope")
    for arm in ("left_arm", "right_arm"):
        n = full["effective_ik_numeric"][arm]
        audit.check(n["epsilon"] == 1e-7 and n["orientation_vs_position"] == 0.01
                    and n["acceptance_translation_m"] == 1e-5 and n["acceptance_rotation_rad"] == 1e-4
                    and not n["position_only_ik"], "approved IK numeric settings")
    audit.check(full["status"] == summary["status"] == meta["status"] == "PASS_DISCRETE_FULL_CHAIN_ONLY", "full-chain scope status")
    audit.check(meta["exit_code"] == 0 and full["acm_unchanged_verified"] and not full["acm_modified"], "exit and ACM")
    audit.check(not full["physics_started"] and full["robot_commands"] == full["suction_commands"] == 0
                and not full["benchmark_frozen"] and not full["kinematic_timed_trajectory"]
                and not full["continuous_collision_certificate"], "no physical/continuous/frozen claims")

    # Do not hash/read the working candidate YAML: q capture may already change it.
    snapshot_hash = sha256(evidence / meta["config_snapshot"])
    audit.check(snapshot_hash == meta["config_sha256_at_run"], "snapshot SHA")
    approved_config = subprocess.check_output(
        ["git", "show", meta["config_approval_commit"] + ":" + meta["config_path"]], cwd=repo)
    audit.check(hashlib.sha256(approved_config).hexdigest() == snapshot_hash, "approval-commit snapshot SHA")
    command = shlex.split(meta["command"])
    audit.check(len(command) == 6, "original command arguments")
    resolve = lambda value: Path(value) if Path(value).is_absolute() else repo / value
    for key, arg_index in (("expanded_urdf", 2), ("expanded_srdf", 3), ("kinematics", 4)):
        audit.check(sha256(resolve(command[arg_index])) == meta["input_hashes"][key], key + " SHA")
    for key, name in (("full_probe_source", "full_chain_probe.cpp"), ("shared_helpers", "geometry_common.hpp")):
        path = "platforms/isaac_ros2/probes/single_cube_geometry/" + name
        committed = subprocess.check_output(["git", "show", meta["git_commit"] + ":" + path], cwd=repo)
        audit.check(hashlib.sha256(committed).hexdigest() == meta["input_hashes"][key], key + " commit SHA")
        audit.check(sha256(repo / path) == meta["input_hashes"][key], key + " local SHA")
    audit.check(sha256(resolve(command[0])) == meta["binary_sha256"], "local binary SHA")
    return {"records": len(rows), "unique_states": 292, "A_states": len(a), "B_states": len(b),
            "csv_rows": len(csv_rows), "failed_states": 0, "maximum_cube_translation_step_m": maximum_steps,
            "config_snapshot_sha256": snapshot_hash, "source_commit": meta["git_commit"],
            "binary_sha256": meta["binary_sha256"], "minimum_states": summary["minimum_states"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_dir", type=Path)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    repo = args.repo.resolve()
    evidence = (args.evidence_dir if args.evidence_dir.is_absolute() else repo / args.evidence_dir).resolve()
    audit = Audit()
    result = {"scientific_classification": "ENGINEERING", "scope": "stored_geometry_artifact_only",
              "isaac_model_parity_verified": False, "dynamics_verified": False,
              "reset_readiness_verified": False, "continuous_collision_certificate": False,
              "probe_or_isaac_started": False, "robot_commands": 0, "suction_commands": 0,
              "evidence_directory": str(evidence.relative_to(repo)),
              "verifier_sha256": sha256(Path(__file__).resolve())}
    try:
        result["metrics"] = verify(repo, evidence, audit)
        result["status"] = "PASS_ARTIFACT_ONLY"
        code = 0
    except (ValueError, KeyError, IndexError, TypeError, OSError, subprocess.CalledProcessError) as error:
        result["status"] = "FAIL_ARTIFACT_ONLY"
        result["error"] = str(error)
        code = 1
    result["assertions_checked"] = audit.assertions
    print(json.dumps(result, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
