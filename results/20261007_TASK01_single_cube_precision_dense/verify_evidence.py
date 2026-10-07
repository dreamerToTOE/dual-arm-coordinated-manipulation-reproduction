"""[ENGINEERING] 本轮固定证据的一致性及不覆盖/不放宽门禁审计；无物理运行。"""
import hashlib
import json
import math
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
base = root / "results"


def load(name, file):
    return json.loads((base / f"20261007_TASK01_single_cube_{name}" / file).read_text())


report = {}
a = load("precision_default", "replay_step_results.json")
b = load("precision_tight", "replay_step_results.json")
for key in ("original_seed_left_q_rad", "original_seed_right_q_rad", "cube_center_world_m"):
    assert a[key] == b[key], key
for arm in ("left", "right"):
    da, db = a[arm + "_ik_diagnostics"][0], b[arm + "_ik_diagnostics"][0]
    assert da["target_world_pose"] == db["target_world_pose"]
    assert da["solver_return"] and db["solver_return"]
    assert da["bounds_satisfied"] and db["bounds_satisfied"]
    assert da["moveit_error_code"] == db["moveit_error_code"] == 1
    assert da["disposition"] == "ROTATION_RESIDUAL_REJECTED" and db["disposition"] == "ACCEPTED"
    assert da["acceptance_translation_limit_m"] == db["acceptance_translation_limit_m"] == 1e-5
    assert da["acceptance_rotation_limit_rad"] == db["acceptance_rotation_limit_rad"] == 1e-4
    assert da["residual"]["rotation_rad"] > 1e-4 >= db["residual"]["rotation_rad"]
    assert a["effective_ik_numeric"][arm + "_arm"]["orientation_vs_position"] == b["effective_ik_numeric"][arm + "_arm"]["orientation_vs_position"] == .01
assert a["fcl"] == "NOT_RUN_NO_ACCEPTED_DUAL_IK" and b["fcl"] == "PASS" and not b["collision_pairs"]
report["same_seed_same_pose_same_acceptance_ab"] = "PASS"
d = load("precision_dense", "dense_insertion_results.json")
s = load("precision_dense", "sample_results.json")
assert len(d) == 157 and all(row["status"] == "PASS" for row in d)
assert s["status"] == "PARTIAL_UNDEFINED_START" and not s["continuous_path_verified"]
assert sum(row["status"] == "PASS_SAMPLED_ENDPOINT" for row in s["samples"]) == 6
assert s["samples"][0]["status"] == "NOT_RUN_UNDEFINED_START"
for index, row in enumerate(d):
    assert index == row["index"] and row["joint_limit"] and not row["collision_pairs"]
    assert len(row["left_q_rad"]) == len(row["right_q_rad"]) == 7
    for arm in ("left", "right"):
        error = row[arm + "_relative_grasp_error"]
        assert error["translation_m"] <= 1e-5 and error["rotation_rad"] <= 1e-4
    if index:
        assert 0 < math.dist(row["cube_center_world_m"], d[index - 1]["cube_center_world_m"]) <= .002 + 1e-12
report["157_state_spacing_bounds_residual_and_fcl"] = "PASS"
audit = load("precision_dense", "cube_environment_audit.json")
assert audit["status"] == "PASS_NOMINAL_AABB_ONLY" and audit["pair_checks"] == 628
assert audit["volumetric_overlaps"] == 0 and audit["table_touch_states"] == 157 and audit["deep_wall_touch_states"] == 1
report["628_nominal_cube_environment_checks"] = "PASS"
for name in ("ik_diagnostic01", "ik_diagnostic02", "precision_default", "precision_tight", "precision_dense"):
    directory = base / f"20261007_TASK01_single_cube_{name}"
    metadata = load(name, "metadata.json")
    for key in ("task", "baseline", "platform", "git_commit", "seed", "config_path", "command", "status", "metrics", "artifacts"):
        assert key in metadata, (name, key)
    for artifact in metadata["artifacts"]:
        assert (directory / artifact).exists(), (name, artifact)
    assert metadata["config_sha256"] == hashlib.sha256((root / metadata["config_path"]).read_bytes()).hexdigest()
    if name == "ik_diagnostic01":
        assert metadata["status"] == "INVALID_DIAGNOSTIC_OLD_BINARY" and metadata["binary_sha256"] is None
        assert not metadata["metrics"]["instrumentation_present"]
    else:
        source = subprocess.check_output(["git", "show", metadata["git_commit"] + ":platforms/isaac_ros2/probes/single_cube_geometry/probe.cpp"], cwd=root)
        assert metadata["source_sha256"] == hashlib.sha256(source).hexdigest(), name
for name in ("precision_default", "precision_tight", "precision_dense"):
    assert load(name, "metadata.json")["binary_sha256"] == hashlib.sha256((root / "build/single_cube_geometry/task01_single_cube_geometry").read_bytes()).hexdigest()
report["five_run_metadata_source_binary_artifacts_provenance"] = "PASS"
common = ["build/single_cube_geometry/task01_single_cube_geometry", "configs/benchmark/benchmark_v1.yaml", "results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.urdf", "results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf", "/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/config/kinematics.yaml", "results/20261007_TASK01_single_cube_arg_guard"]
for value in ("0", "-1", "nan", "1e-4"):
    result = subprocess.run(common + ["--ik-epsilon", value], cwd=root, capture_output=True, text=True)
    assert result.returncode == 2, (value, result.returncode)
assert not (root / common[-1]).exists()
result = subprocess.run(common[:-1] + ["results/20261007_TASK01_single_cube_precision_tight", "--replay-step", "results/20261006_TASK01_single_cube_geometry_probe02/dense_insertion_results.json", "--ik-epsilon", "1e-7"], cwd=root, capture_output=True, text=True)
assert result.returncode == 2 and "Refusing to overwrite prior run" in result.stderr
report["invalid_epsilon_and_prior_result_overwrite_refused"] = "PASS"
print(json.dumps(report, indent=2))
