"""Fixed saved-path diagnostics, not a planner, retimer, FCL query or executor.

ENGINEERING: numeric review of immutable TASK06-IS-A evidence. No ROS/Isaac imports.
Run with PYTHONPATH=. python3 scripts/review_task06_is_b0_path.py.
"""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

import numpy as np

from common.interfaces.exchange import (
    BenchmarkResult, MeasurementQualification, ResultStatus, RunMetadata,
)
from common.logging.run import RunLogger, source_ref

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def analyze(q, lower, upper, names, direction_filter=1e-9, top_count=10):
    """Literal finite bounded-joint differences; no wrap/clamp/repair/time domain."""
    q = np.asarray(q, dtype=float)
    lower, upper = np.asarray(lower, dtype=float), np.asarray(upper, dtype=float)
    require(q.ndim == 2 and len(q) >= 1 and q.shape[1] == len(names), "invalid q shape")
    require(len(set(names)) == len(names), "duplicate joint names")
    require(lower.shape == upper.shape == (len(names),), "invalid bound shape")
    require(np.isfinite(q).all() and np.isfinite(lower).all() and np.isfinite(upper).all(),
            "nonfinite input")
    require(np.all(lower < upper) and np.all(q >= lower) and np.all(q <= upper),
            "native joint bound violation")
    require(np.isfinite(direction_filter) and direction_filter >= 0, "invalid direction filter")
    margin = np.minimum(q - lower, upper - q)
    delta = np.diff(q, axis=0)
    cumulative = np.vstack([np.zeros(len(names)), np.cumsum(np.abs(delta), axis=0)])
    l2 = np.linalg.norm(delta, axis=1)
    linf = np.max(np.abs(delta), axis=1) if len(delta) else np.empty(0)
    arc = np.r_[0., np.cumsum(l2)]
    index, joint = np.unravel_index(np.argmin(margin), margin.shape)
    rows = []
    reversals = []
    for j, name in enumerate(names):
        idx = int(np.argmin(margin[:, j]))
        side = "LOWER" if q[idx, j] - lower[j] <= upper[j] - q[idx, j] else "UPPER"
        displacement = float(q[-1, j] - q[0, j])
        travel = float(cumulative[-1, j])
        raw, filtered = [], []
        for threshold, output in ((0., raw), (direction_filter, filtered)):
            kept = np.flatnonzero(np.abs(delta[:, j]) > threshold)
            for previous, current in zip(kept[:-1], kept[1:]):
                if np.sign(delta[previous, j]) != np.sign(delta[current, j]):
                    output.append({"previous_edge_index": int(previous),
                                   "next_edge_index": int(current),
                                   "turn_point_index": int(previous + 1),
                                   "plateau_end_point_index": int(current),
                                   "q_at_turn_rad": float(q[previous + 1, j]),
                                   "delta_before_rad": float(delta[previous, j]),
                                   "delta_after_rad": float(delta[current, j])})
        reversals.append({"joint_name": name, "raw": raw, "filtered": filtered})
        rows.append({"joint_name": name, "lower_rad": float(lower[j]), "upper_rad": float(upper[j]),
                     "min_margin_rad": float(margin[idx, j]),
                     "min_margin_deg": float(np.degrees(margin[idx, j])),
                     "point_index": idx, "point_number": idx + 1,
                     "angle_rad": float(q[idx, j]), "angle_deg": float(np.degrees(q[idx, j])),
                     "nearest_bound": side,
                     "nearest_bound_rad": float(lower[j] if side == "LOWER" else upper[j]),
                     "minimum_angle_rad": float(q[:, j].min()),
                     "maximum_angle_rad": float(q[:, j].max()),
                     "start_rad": float(q[0, j]), "goal_rad": float(q[-1, j]),
                     "net_displacement_rad": displacement, "cumulative_travel_rad": travel,
                     "cumulative_travel_deg": float(np.degrees(travel)),
                     "excess_travel_rad": travel - abs(displacement),
                     "travel_to_net_ratio": travel / abs(displacement) if displacement else None,
                     "max_adjacent_abs_rad": float(np.max(np.abs(delta[:, j]))) if len(delta) else 0.,
                     "raw_direction_reversals": len(raw), "filtered_direction_reversals": len(filtered),
                     "points_margin_le_legacy_0035_rad": int(np.sum(margin[:, j] <= .035)),
                     "points_margin_le_legacy_006_rad": int(np.sum(margin[:, j] <= .06))})
    critical = dict(rows[joint])
    critical.update(point_index=int(index), point_number=int(index + 1),
                    path_arc_fraction=float(arc[index] / arc[-1]) if arc[-1] else 0.,
                    q14_rad=q[index].tolist())
    top = sorted(range(len(delta)), key=lambda i: (-l2[i], i))[:top_count]
    summary = {"point_count": len(q), "joint_count": len(names), "critical": critical,
               "joints": rows, "path_joint_l2_length_rad": float(l2.sum()),
               "max_adjacent_l2_rad": float(l2.max()) if len(l2) else 0.,
               "max_adjacent_linf_rad": float(linf.max()) if len(linf) else 0.,
               "direction_filter_rad": direction_filter,
               "top_adjacent_edges": [{"edge_index": i, "from_point_index": i,
                                       "to_point_index": i + 1, "l2_rad": float(l2[i]),
                                       "linf_rad": float(linf[i])} for i in top]}
    return summary, {"q": q, "margin": margin, "delta": delta,
                     "cumulative": cumulative, "l2": l2, "linf": linf, "arc": arc}, reversals


def verify_evidence(run, path, raw, records, gates):
    require(raw["dense_path_rad"] == path["q_rad"], "planner dense path mismatch")
    require(records["qualified"] is True and records["continuous_collision_certificate"] is False,
            "independent qualification mismatch")
    require(len(records["states"]) == len(path["q_rad"]) == len(raw["dense_path_evidence"]),
            "evidence count mismatch")
    require(records["path_edges"] == raw["path_edges"], "tree edge list mismatch")

    def clear(collision):
        require(collision["backend"] == "EXISTING_MOVEIT_PLANNING_SCENE_FCL" and
                collision["acm_identity"] == "ORIGINAL_SRDF_UNCHANGED_NO_ADDED_ENTRIES" and
                collision["complete"] is True and not collision["self_collision"] and
                not collision["world_collision"] and not collision["contacts"], "FCL qualification mismatch")

    for i, (q, row, ref) in enumerate(zip(path["q_rad"], records["states"], raw["dense_path_evidence"])):
        require(row["index"] == i and row["q_rad"] == q == ref["q_rad"] and row["qualified"],
                f"point {i} evidence mismatch")
        require(row["closure"]["position_norm_m"] <= gates["position_tolerance_m"] and
                row["closure"]["rotation_norm_rad"] <= gates["rotation_tolerance_rad"] and
                row["native_joint_margin_rad"] >= 0 and
                row["adjacent_l2_rad"] <= gates["adjacent_joint_l2_limit_rad"] and
                row["adjacent_max_abs_rad"] <= gates["adjacent_joint_max_abs_limit_rad"],
                f"point {i} original gate mismatch")
        clear(row["collision"])
        connection = raw["attempts"][ref["attempt"]]["connection"] if ref["attempt"] is not None else (
            raw["start_root"] if ref["tree"] == "START" else raw["goal_root"])
        checked = connection["checked_points"][ref["checked_point"]]
        require(checked["qualified"] and checked["q_rad"] == q, "dense point source mismatch")
        clear(checked["collision"])
    for edge in raw["path_edges"]:
        tree = raw["start_tree"] if edge["tree"] == "START" else raw["goal_tree"]
        child, parent = tree[edge["child"]], tree[edge["parent"]]
        attempt = raw["attempts"][edge["attempt"]]
        connection = attempt["connection"]
        require(child["parent"] == edge["parent"] and child["incoming_attempt"] == edge["attempt"] and
                attempt["added_node"] == edge["child"] and attempt["tree"] == edge["tree"] and
                connection["requested_start_rad"] == parent["q_rad"] and
                connection["requested_goal_rad"] == child["q_rad"] and
                connection["status"] == "CONNECTED", "tree/attempt/endpoint mismatch")
        for checked in connection["checked_points"]:
            require(checked["qualified"], "unqualified edge checked point")
            clear(checked["collision"])
        for leaf in connection["leaf_edges"]:
            require(leaf["accepted"] and leaf["joint_l2_rad"] <= gates["adjacent_joint_l2_limit_rad"] and
                    leaf["joint_max_abs_rad"] <= gates["adjacent_joint_max_abs_limit_rad"], "leaf mismatch")
    metadata = json.loads((run / "metadata.json").read_text())
    source_meta = metadata["run_metadata"]["data"]
    commit = source_meta["git_commit"]
    for artifact in metadata["artifacts"]:
        require(sha((run / artifact["path"]).read_bytes()) == artifact["sha256"], "artifact hash mismatch")
    repo_source_count = external_count = 0
    for source in source_meta["sources"]:
        source_path = Path(source["path"])
        if source_path.is_relative_to(ROOT):
            data = subprocess.check_output(["git", "show", f"{commit}:{source_path.relative_to(ROOT)}"], cwd=ROOT)
            repo_source_count += 1
        else:
            data = source_path.read_bytes()
            external_count += 1
        require(sha(data) == source["sha256"], f"source hash mismatch: {source_path}")
    model = ET.parse(ROOT / "tests/fixtures/task03/robot.urdf").getroot()
    limits = {joint.attrib["name"]: joint.find("limit").attrib for joint in model.findall("joint")
              if joint.find("limit") is not None}
    for j, name in enumerate(path["joint_names"]):
        require(float(limits[name]["lower"]) == raw["native_lower_rad"][j] and
                float(limits[name]["upper"]) == raw["native_upper_rad"][j], "URDF bound mismatch")
    return {"artifact_hashes_verified": len(metadata["artifacts"]), "tested_source_commit": commit,
            "repo_source_hashes_verified_at_tested_commit": repo_source_count,
            "external_stl_hashes_verified": external_count,
            "path_and_dense_evidence_points_verified": len(path["q_rad"]),
            "qualified_tree_edges_verified": len(raw["path_edges"]), "native_urdf_bounds_verified": len(limits),
            "new_fcl_queries": 0, "new_planning_calls": 0,
            "minimum_collision_distance_status": raw["minimum_distance_status"],
            "continuous_collision_certificate": False, "physical_grasp_certificate": False,
            "original_planning_compute_sec": raw["compute_wall_time_sec"],
            "timed_trajectory": False, "velocity_acceleration_from_untimed_path": None,
            "qualification": path["qualification"]}


def plots(out, names, arrays, summary):
    import matplotlib
    matplotlib.use("Agg")  # Pure file rendering, not an Isaac headless application.
    import matplotlib.pyplot as plt
    x = np.arange(len(arrays["q"]))
    for mode in ("positions", "margins", "travel"):
        fig, axes = plt.subplots(7, 2, figsize=(14, 17), sharex=True)
        for j, name in enumerate(names):
            ax = axes[j % 7, j // 7]
            row = summary["joints"][j]
            if mode == "positions":
                ax.plot(x, arrays["q"][:, j], lw=1)
                ax.axhline(row["lower_rad"], color="r", ls="--", lw=.8)
                ax.axhline(row["upper_rad"], color="r", ls="--", lw=.8)
                ax.plot(x, row["start_rad"] + (row["goal_rad"] - row["start_rad"]) * x / max(1, x[-1]),
                        color="gray", ls=":", lw=.8)
                ax.set_ylabel("q [rad]")
            elif mode == "margins":
                ax.plot(x, arrays["margin"][:, j], lw=1)
                ax.axhline(.035, color="orange", ls="--", lw=.8)
                ax.axhline(.06, color="r", ls=":", lw=.8)
                ax.scatter([row["point_index"]], [row["min_margin_rad"]], c="black", s=9)
                ax.set_yscale("symlog", linthresh=1e-3)
                ax.set_ylabel("margin [rad]")
            else:
                ax.plot(x, arrays["cumulative"][:, j], lw=1)
                ax.axhline(abs(row["net_displacement_rad"]), color="gray", ls="--", lw=.8)
                ax.set_ylabel("sum |dq| [rad]")
            ax.set_title(name, fontsize=10)
            ax.grid(alpha=.25)
        axes[-1, 0].set_xlabel("Saved path point index (NOT TIME)")
        axes[-1, 1].set_xlabel("Saved path point index (NOT TIME)")
        subtitle = {"positions": "Red: native bounds; gray: endpoint straight-line reference, NOT alternative path",
                    "margins": "Orange .035 / red .060: LEGACY endpoint tolerances, NOT certified motion bounds",
                    "travel": "Gray: |endpoint displacement|; curves identify joint detours"}[mode]
        fig.suptitle(f"TASK06-IS-B0: {mode}\n{subtitle}", fontsize=11)
        fig.tight_layout(rect=(0, 0, 1, .965))
        for extension in ("png", "svg"):
            fig.savefig(out / f"joint_{mode}.{extension}", dpi=130)
        plt.close(fig)


def write_csv(path, rows):
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="20261012_TASK06_IS_B0_path_review01")
    args = parser.parse_args()
    protocol_path = ROOT / "configs/engineering/task06_is_b0_review_v1.json"
    protocol = json.loads(protocol_path.read_text())
    run = ROOT / protocol["input_run"]
    paths = [protocol_path, Path(__file__), ROOT / "reports/TASK06_IS_B0_PRE_TASK_PROTOCOL.md"]
    paths += [run / name for name in ("qualified_joint_path.json", "independent_path_validation.json",
                                     "planner_seed7.json.gz", "metadata.json", "native_manifest.json")]
    paths += [ROOT / protocol["local_protocol"], ROOT / "tests/fixtures/task03/robot.urdf",
              ROOT / "tests/test_task06_is_b0_review.py"]
    legacy = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation")
    paths += [legacy / p for p in (
        "ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp",
        "isaac/scripts/task26_truck_box_scene.py", "isaac/scripts/task26_truck_box_bridge.py",
        "ros_ws/src/fr3_dual_palletize/src/shared_object_planner.cpp",
        "ros_ws/src/fr3_dual_side_suction_description/launch/moveit_dual_side_suction.launch.py")]
    paths += [ROOT / "results/20261009_TASK01_predecessor_patched_runtime02" / p
              for p in ("physical.log", "moveit.log", "initial_snapshot.json")]
    paths += [Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/franka_description/robots/fr3/joint_limits.yaml"),
              Path("/opt/ros/humble/include/moveit/trajectory_processing/time_optimal_trajectory_generation.h")]
    before = {str(p): sha(p.read_bytes()) for p in paths}
    metadata = RunMetadata(args.run_id, "TASK06-IS-B0", "P4_FIXED_PATH_EXECUTION_REVIEW",
                           "OFFLINE_SAVED_EVIDENCE_ONLY", subprocess.check_output(
                               ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                           0, None, tuple([sys.executable, *sys.argv]), ("review_v1",),
                           (str(protocol_path),), tuple(source_ref(f"source_{i}", p) for i, p in enumerate(paths)))
    with RunLogger(ROOT / "results", metadata) as logger:
        out = logger.path
        start = time.perf_counter()
        path = json.loads((run / "qualified_joint_path.json").read_text())
        require(before[str(run / "qualified_joint_path.json")] == protocol["path_sha256"], "path hash mismatch")
        require(len(path["q_rad"]) == protocol["expected_points"] and len(path["joint_names"]) == 14,
                "path shape mismatch")
        require(path["joint_names"] == [f"{side}_fr3_joint{i}" for side in ("left", "right") for i in range(1, 8)],
                "joint name order mismatch")
        compressed = (run / "planner_seed7.json.gz").read_bytes()
        decompressed = gzip.decompress(compressed)
        raw = json.loads(decompressed)
        records = json.loads((run / "independent_path_validation.json").read_text())
        gates = json.loads((ROOT / protocol["local_protocol"]).read_text())
        evidence = verify_evidence(run, path, raw, records, gates)
        summary, arrays, reversals = analyze(path["q_rad"], raw["native_lower_rad"], raw["native_upper_rad"],
                                            path["joint_names"], protocol["direction_filter_rad"],
                                            protocol["top_adjacent_edges"])
        for i, row in enumerate(records["states"]):
            require(abs(float(arrays["margin"][i].min()) - row["native_joint_margin_rad"]) <= 1e-15,
                    "independent minimum margin mismatch")
            if i:
                require(abs(float(arrays["l2"][i - 1]) - row["adjacent_l2_rad"]) <= 1e-14 and
                        abs(float(arrays["linf"][i - 1]) - row["adjacent_max_abs_rad"]) <= 1e-14,
                        "independent adjacent distance mismatch")
        summary["provenance"] = evidence
        summary["path_sha256"] = protocol["path_sha256"]
        summary["planner_uncompressed_sha256"] = sha(decompressed)
        summary["max_recorded_position_closure_m"] = max(r["closure"]["position_norm_m"] for r in records["states"])
        summary["max_recorded_rotation_closure_rad"] = max(r["closure"]["rotation_norm_rad"] for r in records["states"])
        summary["velocity_acceleration_qualification"] = "UNAVAILABLE_UNTIMED_PATH_NO_NATIVE_ACCELERATION_CERTIFICATE"
        summary["execution_preconditions"] = "NOT_SATISFIED"
        summary["legacy_tolerance_comparison"] = {
            "ordinary_endpoint_tolerance_rad": .035, "stable_residual_endpoint_tolerance_rad": .06,
            "ordinary_to_margin_ratio": .035 / summary["critical"]["min_margin_rad"],
            "stable_residual_to_margin_ratio": .06 / summary["critical"]["min_margin_rad"],
            "source": "Task26@631b1f6 + approved5ed0c96 controller lines169,176; endpoint-only NOT motion envelope"}
        summary["review_completed"] = True
        summary["new_planning_calls"] = summary["new_fcl_queries"] = summary["execution_commands"] = 0
        summary["simulation_time"] = summary["physics_step"] = None
        write_csv(out / "joint_review.csv", summary["joints"])
        write_csv(out / "path_points.csv", [{"point_index": i, "arc_length_rad": float(arrays["arc"][i]),
                  "minimum_margin_rad": float(arrays["margin"][i].min()),
                  "adjacent_l2_rad": float(arrays["l2"][i-1]) if i else 0.,
                  **{f"{name}_margin_rad": float(arrays["margin"][i, j]) for j, name in enumerate(path["joint_names"])}}
                  for i in range(len(path["q_rad"]))])
        plots(out, path["joint_names"], arrays, summary)
        logger._atomic_json("direction_reversals.json", reversals)
        logger._atomic_json("protocol_at_run.json", protocol)
        require(all(sha(p.read_bytes()) == before[str(p)] for p in paths), "protected input changed")
        summary["protected_input_hashes_unchanged"] = before
        summary["analysis_wall_sec_NOT_EXECUTION_TIME"] = time.perf_counter() - start
        logger._atomic_json("summary.json", summary)
        logger.finish(BenchmarkResult(args.run_id, metadata.baseline_id, ResultStatus.INCOMPLETE,
            "Execution eligibility of immutable saved P4 path; NOT planner or physics acceptance",
            MeasurementQualification.UNQUALIFIED, ("summary.json", "joint_review.csv", "path_points.csv"),
            metadata.config_ids, tuple(s.source_id for s in metadata.sources),
            failure_stage="PRE_EXECUTION_ELIGIBILITY",
            reason="Native joint margin smaller than legacy endpoint error allowance; no certified motion error envelope, timed acceleration qualification or actual held START alignment",
            limitations=("NO_PHYSICS_OR_NEW_FCL", "DISCRETE_ONLY", "BENCHMARK_DRAFT", "NO_TIMED_TRAJECTORY")))
        print(json.dumps({"review_completed": True, "execution_preconditions": "NOT_SATISFIED",
                          "critical": summary["critical"], "points": len(path["q_rad"]),
                          "output": str(out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
