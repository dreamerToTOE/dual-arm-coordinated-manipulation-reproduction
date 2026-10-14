#!/usr/bin/env python3
"""Independent serial-transform oracle for the external Comau author kernels.

This consumes saved qualification measurements only. It neither imports author
code, retries IK/NR, runs planners, nor repairs endpoints. Geometry comes from the
pinned original model definitions; transforms are our elementary matrix products.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any

import numpy as np


SOURCE = {
    4: "80089340f0f1f6822e5b2821a63c998b6ae0413f",
    5: "ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca",
    6: "25488a86947cd07377cc62c43850df719a70d9ee",
}
AUTHOR_PI = 3.1416
FLIP = np.diag([-1.0, -1.0, 1.0, 1.0])


def translation(x: float, y: float, z: float) -> np.ndarray:
    value = np.eye(4)
    value[:3, 3] = [x, y, z]
    return value


def rotation(axis: str, angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    result = np.eye(4)
    if axis == "X":
        result[:3, :3] = [[1, 0, 0], [0, c, -s], [0, s, c]]
    elif axis == "Y":
        result[:3, :3] = [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    elif axis == "Z":
        result[:3, :3] = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    else:
        raise ValueError("invalid elementary axis")
    return result


def geometry(model: int) -> dict[str, Any]:
    """Declared source inputs, independently encoded, never fitted to outputs."""
    properties = [344.0, 524.5, 199.0, 1250.0, 186.5, 210.0, 1250.0, 116.5,
                  422.7 if model == 5 else 22.0]
    if model == 4:
        bases = [[-3000, 0, 0, 0], [3000, 0, 0, -AUTHOR_PI]]
        grasps = [translation(1800, 0, 0)]
    elif model == 5:
        distance = 2358.3 - 20.055
        bases = [[-distance / 2, 0, 1000, 0],
                 [distance / 2, 4200, 100, -AUTHOR_PI / 2]]
        # Source Q is an exact signed-permutation rotation, not cos(3.1416/2).
        bridge = np.array([[0., 0., -1., 250.], [0., 1., 0., 0.],
                           [1., 0., 0., 750.], [0., 0., 0., 1.]])
        grasps = [bridge]
    elif model == 6:
        radius, grasp_radius = 2600, 400
        bases = [[-radius, 0, 0, 0]]
        for yaw in [-2 * AUTHOR_PI / 3, 2 * AUTHOR_PI / 3]:
            # C++ round uses half-away-from-zero. These values are not half-ties.
            x = radius * math.sin(yaw - AUTHOR_PI / 2)
            y = -radius * math.cos(yaw - AUTHOR_PI / 2)
            bases.append([math.copysign(math.floor(abs(x) + 0.5), x),
                          math.copysign(math.floor(abs(y) + 0.5), y), 0, yaw])
        grasps = []
        for yaw in [AUTHOR_PI / 3, -AUTHOR_PI / 3]:
            bridge = rotation("Z", yaw)
            bridge[:3, 3] = [grasp_radius * math.cos(yaw) + grasp_radius,
                              grasp_radius * math.sin(yaw), 0]
            grasps.append(bridge)
    else:
        raise ValueError("model must be IV (4), V (5), or VI (6)")
    return {"properties_mm": properties, "bases_mm_rad": bases,
            "grasps": grasps, "axes": ["Z", "Y", "Y", "X", "Y", "X"]}


def serial_fk(q: Any, model: int, arm: int,
              return_stages: bool = False) -> Any:
    """World FK by six rotations followed by their actual link translations."""
    q = array(q, (6,))
    inputs = geometry(model)
    b, l1x, l1z, l2, l3x, l3z, l4, l5, tool = inputs["properties_mm"]
    base = inputs["bases_mm_rad"][arm - 1]
    result = translation(*base[:3]) @ rotation("Z", base[3]) @ translation(0, 0, b)
    offsets = [[l1x, 0, l1z], [0, 0, l2], [l3x, 0, l3z],
               [l4, 0, 0], [l5, 0, 0], [tool, 0, 0]]
    stages = [result.copy()]
    for axis, angle, offset in zip(inputs["axes"], q, offsets):
        result = result @ rotation(axis, float(angle)) @ translation(*offset)
        stages.append(result.copy())
    return (result, stages) if return_stages else result


def array(value: Any, shape: tuple[int, ...] | None = None) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if shape is not None and result.shape != shape:
        raise ValueError(f"shape {result.shape} differs from {shape}")
    if not np.isfinite(result).all():
        raise ValueError("NON_FINITE_RECORDED_VALUE")
    return result


def pose_error(actual: Any, expected: Any) -> dict[str, float]:
    actual, expected = array(actual, (4, 4)), array(expected, (4, 4))
    delta_p = actual[:3, 3] - expected[:3, 3]
    return {"translation_abs_max_mm": float(np.max(np.abs(delta_p))),
            "translation_l2_mm": float(np.linalg.norm(delta_p)),
            "rotation_matrix_abs_max": float(np.max(np.abs(actual[:3, :3] - expected[:3, :3]))),
            "actual_rotation_orthogonality_abs_max": float(np.max(np.abs(actual[:3, :3].T @ actual[:3, :3] - np.eye(3)))),
            "actual_rotation_determinant": float(np.linalg.det(actual[:3, :3]))}


def within(error: dict[str, float], position_gate: float,
           rotation_gate: float) -> bool:
    return (error["translation_abs_max_mm"] <= position_gate
            and error["rotation_matrix_abs_max"] <= rotation_gate)


def all_serial_fk(q: Any, model: int) -> list[np.ndarray]:
    arms = 3 if model == 6 else 2
    q = array(q, (arms * 6,))
    return [serial_fk(q[6*i:6*i+6], model, i+1) for i in range(arms)]


def so3_log(matrix_value: np.ndarray) -> np.ndarray:
    """Principal SO(3) logarithm for the independent, unquantized rotations."""
    cosine = float(np.clip((np.trace(matrix_value) - 1) / 2, -1, 1))
    theta = math.acos(cosine)
    axial = np.array([matrix_value[2, 1] - matrix_value[1, 2],
                      matrix_value[0, 2] - matrix_value[2, 0],
                      matrix_value[1, 0] - matrix_value[0, 1]]) / 2
    if theta < 1e-7:
        return axial * (1 + theta * theta / 6)
    if math.pi - theta < 1e-5:
        # Diagnostic finite differences never intentionally cross the pi chart.
        raise ValueError("SO3_PRINCIPAL_CHART_NEAR_PI")
    return theta / math.sin(theta) * axial


def closure_errors(q: Any, model: int) -> list[dict[str, float]]:
    poses = all_serial_fk(q, model)
    return [pose_error(poses[i + 1], poses[0] @ grasp @ FLIP)
            for i, grasp in enumerate(geometry(model)["grasps"])]


def closure_vector(q: Any, model: int) -> np.ndarray:
    poses = all_serial_fk(q, model)
    values = []
    for i, grasp in enumerate(geometry(model)["grasps"]):
        target, actual = poses[0] @ grasp @ FLIP, poses[i + 1]
        values.extend(actual[:3, 3] - target[:3, 3])
        values.extend(so3_log(actual[:3, :3] @ target[:3, :3].T))
    return array(values)


def closure_jacobian(q: Any, model: int, epsilon: float) -> np.ndarray:
    q = array(q)
    result = np.empty((6 * (2 if model == 6 else 1), len(q)))
    for j in range(len(q)):
        perturb = np.zeros(len(q)); perturb[j] = epsilon
        result[:, j] = (closure_vector(q + perturb, model)
                        - closure_vector(q - perturb, model)) / (2 * epsilon)
    return result


def passive_jacobian(q: Any, model: int, arm: int,
                     epsilon: float) -> np.ndarray:
    q = array(q, (6,))
    reference = serial_fk(q, model, arm)
    jacobian = np.empty((6, 6))
    for j in range(6):
        perturb = np.zeros(6); perturb[j] = epsilon
        plus, minus = serial_fk(q + perturb, model, arm), serial_fk(q - perturb, model, arm)
        jacobian[:3, j] = (plus[:3, 3] - minus[:3, 3]) / (2 * epsilon)
        relative_derivative = ((plus[:3, :3] - minus[:3, :3]) / (2 * epsilon)) @ reference[:3, :3].T
        jacobian[3:, j] = [relative_derivative[2, 1] - relative_derivative[1, 2],
                           relative_derivative[0, 2] - relative_derivative[2, 0],
                           relative_derivative[1, 0] - relative_derivative[0, 1]]
        jacobian[3:, j] *= 0.5
    return jacobian


def native_passive_jacobian(row: dict[str, Any]) -> np.ndarray:
    """Finite differences from actual author FK measurements saved by the harness."""
    reference = array(row["author_fk"], (4, 4))
    plus = array(row["author_fk_plus"], (6, 4, 4))
    minus = array(row["author_fk_minus"], (6, 4, 4))
    epsilon = float(row["epsilon_rad"])
    jacobian = np.empty((6, 6))
    for j in range(6):
        derivative = (plus[j] - minus[j]) / (2 * epsilon)
        jacobian[:3, j] = derivative[:3, 3]
        omega = derivative[:3, :3] @ reference[:3, :3].T
        jacobian[3:, j] = [omega[2, 1] - omega[1, 2],
                           omega[0, 2] - omega[2, 0],
                           omega[1, 0] - omega[0, 1]]
        jacobian[3:, j] *= 0.5
    return jacobian


def closure_from_poses(poses: Any, model: int) -> np.ndarray:
    poses = array(poses, (3 if model == 6 else 2, 4, 4))
    values = []
    for i, grasp in enumerate(geometry(model)["grasps"]):
        target, actual = poses[0] @ grasp @ FLIP, poses[i+1]
        values.extend(actual[:3, 3] - target[:3, 3])
        values.extend(so3_log(actual[:3, :3] @ target[:3, :3].T))
    return array(values)


def native_closure_jacobian(row: dict[str, Any], model: int) -> np.ndarray:
    count = len(row["q_rad"])
    plus = array(row["author_fk_plus"], (count, 3 if model == 6 else 2, 4, 4))
    minus = array(row["author_fk_minus"], plus.shape)
    epsilon = float(row["epsilon_rad"])
    return np.column_stack([(closure_from_poses(plus[j], model)
                             - closure_from_poses(minus[j], model)) / (2 * epsilon)
                            for j in range(count)])


def svd_record(jacobian: np.ndarray, relative_threshold: float) -> dict[str, Any]:
    scaled = jacobian.copy()
    for begin in range(0, len(scaled), 6):
        scaled[begin:begin+3] /= 1000.0
    singular = np.linalg.svd(scaled, compute_uv=False)
    original = np.linalg.svd(jacobian, compute_uv=False)
    threshold = singular[0] * relative_threshold if len(singular) else 0.0
    return {"rank": int(np.sum(singular > threshold)),
            "relative_rank_threshold": relative_threshold,
            "absolute_rank_threshold_scaled": float(threshold),
            "singular_values_scaled_m_rad": singular.tolist(),
            "singular_values_original_mm_rad": original.tolist(),
            "jacobian_original_mm_rad": jacobian.tolist(),
            "jacobian_scaled_m_rad": scaled.tolist()}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(args: argparse.Namespace) -> int:
    started = time.monotonic()
    protocol = json.loads(args.protocol.read_text())
    if protocol["schema"] != "P4_D079_R1_QUALIFICATION_V1" or not protocol["frozen"]:
        raise ValueError("wrong or unfrozen qualification protocol")
    rows = []
    parse_failures = []
    for index, line in enumerate(args.raw.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as error:
            parse_failures.append({"type": "parse_failure", "line": index,
                                   "reason": str(error), "raw_line": line})
    metadata = next(row for row in rows if row["type"] == "metadata")
    model, arms = int(metadata["model"]), int(metadata["arms"])
    fk_gate = (protocol["independent_fk_abs_translation_gate_mm"],
               protocol["independent_fk_abs_rotation_matrix_gate"])
    projection_gate = (protocol["ik_projection_abs_translation_gate_mm"],
                       protocol["ik_projection_abs_rotation_matrix_gate"])
    epsilon, relative = (protocol["finite_difference_eps_rad"],
                         protocol["svd_rank_relative_threshold"])
    counts = Counter(row["type"] for row in rows)
    checks: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    matrices: dict[str, np.ndarray] = {}

    def check(name: str, passed: bool, evidence: Any) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "evidence": evidence})

    check("source_identity", metadata["source_commit"] == SOURCE[model],
          {"recorded": metadata["source_commit"], "expected": SOURCE[model]})
    check("counts_complete", counts["fk_sample"] == protocol["fk_sample_count_per_model"]
          and counts["ik_roundtrip"] == protocol["ik_roundtrip_sample_count_per_spatial_model"] * len(protocol["ik_branch_indices"])
          and counts["nr_near_endpoint"] == protocol["projection_near_endpoint_count_per_model"]
          and counts["raw_endpoint"] == 2 and counts["far_unreachable_ik"] == 8
          and counts["passive_fixture"] == 3 * arms and counts["completion"] == 1
          and counts["closure_fd_fixture"] == 2 and counts["failure"] == 0
          and not parse_failures, {"counts": dict(counts), "parse_failures": parse_failures})
    inputs = geometry(model)
    check("declared_author_model_inputs", np.max(np.abs(array(metadata["author_properties_mm"]) - inputs["properties_mm"])) <= 1e-12
          and np.max(np.abs(array(metadata["base_xyz_yaw_mm_rad"]) - inputs["bases_mm_rad"])) <= 1e-12
          and all(np.max(np.abs(array(got) - expected)) <= 1e-12
                  for got, expected in zip(metadata["grasp_transforms"], inputs["grasps"])),
          {"author_properties_mm": metadata["author_properties_mm"],
           "declared_properties_mm": inputs["properties_mm"],
           "kdl_properties_mm": metadata["kdl_properties_mm"]})
    check("frozen_random_stream", metadata["seed"] == protocol["seed"]
          and metadata["effective_seed"] == protocol["seed"] + 1000 * model,
          {"base_seed": metadata["seed"], "effective_seed": metadata["effective_seed"],
           "mapping": metadata["seed_mapping"]})

    ik_per_sample = Counter()
    def analyze_row(row: dict[str, Any]) -> None:
        kind = row["type"]
        if kind in ("fk_sample", "raw_endpoint", "negative_state"):
            arm_errors = []
            q = array(row["q_rad"], (6 * arms,))
            for arm in range(1, arms + 1):
                independent, stages = serial_fk(q[6*(arm-1):6*arm], model, arm, True)
                error = pose_error(row["author_fk"][arm-1], independent)
                arm_errors.append(error)
                if kind == "fk_sample":
                    check(f"fk_{row['sample']}_arm_{arm}", within(error, *fk_gate), error)
                    # Keep all seven independent matrices; they are derived from the
                    # saved q and declared links, not author closed-form functions.
                    matrices[f"fk_{row['sample']}_arm_{arm}_serial_stages"] = np.asarray(stages)
            detail = {"type": kind, "sample": row.get("sample"), "name": row.get("name"),
                      "q_rad": row["q_rad"], "fk_errors": arm_errors}
            if kind != "fk_sample":
                detail["closure_errors_independent"] = closure_errors(q, model)
                detail["status"] = "DIAGNOSTIC_UNCHANGED_LITERAL_ENDPOINT" if kind == "raw_endpoint" else "NEGATIVE_DIAGNOSTIC"
                if kind == "negative_state":
                    check("negative_closure_perturbation_rejected", any(
                        not within(item, *projection_gate)
                        for item in detail["closure_errors_independent"]),
                        detail["closure_errors_independent"])
            details.append(detail)
        elif kind == "ik_roundtrip":
            detail = dict(row)
            if row["accepted"]:
                independent = serial_fk(row["q_result_rad"], model, row["arm"])
                error = pose_error(independent, row["target"])
                check(f"ik_{row['sample']}_branch_{row['branch']}_returned_fk", within(error, *projection_gate), error)
                detail["independent_target_error"] = error
                detail["source_result_vs_independent_fk"] = pose_error(row["author_result_fk"], independent)
                ik_per_sample[row["sample"]] += 1
            else:
                detail["status"] = "RECORDED_BRANCH_REJECTION_NOT_RETRIED"
            details.append(detail)
        elif kind == "nr_near_endpoint":
            detail = dict(row)
            check(f"nr_{row['sample']}_returned_success", row["accepted"],
                  {"anchor": row["anchor"], "wall_s": row["wall_s"]})
            if row["accepted"]:
                errors = closure_errors(row["q_result_rad"], model)
                for loop, error in enumerate(errors, 1):
                    check(f"nr_{row['sample']}_closure_{loop}", within(error, *projection_gate), error)
                detail["independent_closure_errors"] = errors
            details.append(detail)
        elif kind == "far_unreachable_ik":
            check(f"negative_far_target_branch_{row['branch']}", not row["accepted"], row)
        elif kind == "passive_fixture":
            jacobian = native_passive_jacobian(row)
            independent_jacobian = passive_jacobian(row["q_rad"], model, row["arm"], epsilon)
            evidence = svd_record(jacobian, relative)
            name = row["name"]
            details.append({"type": kind, "name": name, "arm": row["arm"],
                            "q_rad": row["q_rad"], "native_svd": evidence,
                            "independent_svd": svd_record(independent_jacobian, relative),
                            "jacobian_native_minus_independent_abs_max_mm_rad": float(np.max(np.abs(jacobian-independent_jacobian))),
                            "fk_error": pose_error(row["author_fk"], serial_fk(row["q_rad"], model, row["arm"]))})
            matrices[f"passive_{name}_arm_{row['arm']}_native_jacobian"] = jacobian
            matrices[f"passive_{name}_arm_{row['arm']}_independent_jacobian"] = independent_jacobian
            if name == "regular_passive_jacobian_positive_control":
                check(f"regular_passive_rank_arm_{row['arm']}", evidence["rank"] == 6, evidence)
            elif name == "wrist_singular_q5_zero":
                check(f"wrist_singular_rank_arm_{row['arm']}", evidence["rank"] < 6, evidence)
            # The author's elbow formula is diagnosed, not silently rewritten or
            # made a successful singular sample by forcing an extra wrist zero.
        elif kind == "failure":
            details.append(row)
        elif kind == "closure_fd_fixture":
            if row["epsilon_rad"] != epsilon:
                raise ValueError("native finite difference epsilon differs from frozen protocol")
            independent_jacobian = closure_jacobian(row["q_rad"], model, epsilon)
            jacobian = native_closure_jacobian(row, model)
            details.append({"type": kind, "name": row["name"],
                            "status": "NATIVE_AND_INDEPENDENT_DIAGNOSTIC_AT_RAW_ENDPOINT",
                            "native_svd": svd_record(jacobian, relative),
                            "independent_svd": svd_record(independent_jacobian, relative),
                            "jacobian_native_minus_independent_abs_max_mm_rad": float(np.max(np.abs(jacobian-independent_jacobian)))})
            matrices[f"raw_{row['name']}_native_closure_jacobian"] = jacobian
            matrices[f"raw_{row['name']}_independent_closure_jacobian"] = independent_jacobian
            for loop in range(arms - 1):
                details.append({"type": "native_closure_block_jacobian", "name": row["name"],
                                "closure": loop + 1,
                                "native_svd": svd_record(jacobian[6*loop:6*loop+6], relative),
                                "independent_svd": svd_record(independent_jacobian[6*loop:6*loop+6], relative)})
            if model == 6:
                details.append({"type": "native_two_passive_chains_jacobian", "name": row["name"],
                                "active_arm": 1, "native_svd": svd_record(jacobian[:, 6:], relative),
                                "independent_svd": svd_record(independent_jacobian[:, 6:], relative)})

    for index, row in enumerate(rows):
        if time.monotonic() - started >= protocol["diagnostic_single_limit_s"]:
            check("analysis_wall_budget", False, "DIAGNOSTIC_WALL_LIMIT")
            break
        try:
            analyze_row(row)
        except (ValueError, KeyError, IndexError, np.linalg.LinAlgError) as error:
            check(f"row_{index}_finite_and_valid", False,
                  {"type": row.get("type"), "reason": str(error)})
            details.append({"type": "analysis_row_failure", "index": index,
                            "original_record": row, "reason": str(error)})
    for sample in range(protocol["ik_roundtrip_sample_count_per_spatial_model"]):
        check(f"ik_target_{sample}_has_valid_branch", ik_per_sample[sample] > 0,
              {"accepted_branch_count": ik_per_sample[sample]})

    summary = {"schema": "P4_COMAU_QUALIFICATION_ANALYSIS_V1",
               "classification": "INDEPENDENT_QUALIFICATION_NOT_FORMAL_PAPER_TRIALS",
               "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL_GATE",
               "model": model, "source_commit": SOURCE[model], "raw_sha256": digest(args.raw),
               "protocol_sha256": digest(args.protocol), "analysis_source_sha256": digest(Path(__file__)),
               "checks_passed": sum(item["status"] == "PASS" for item in checks),
               "checks_failed": sum(item["status"] == "FAIL" for item in checks),
               "record_counts": dict(counts), "checks": checks, "details": details,
               "raw_endpoint_policy": protocol["raw_endpoint_policy"],
               "limits": {"FK": fk_gate, "IK_NR": projection_gate, "FD_eps_rad": epsilon,
                          "SVD_relative": relative},
               "analysis_wall_s": time.monotonic() - started,
               "not_executed": ["collision qualification", "formal planning", "FR3 adaptation"]}
    matrix_path = args.output.with_name(args.output.stem + "_matrices.npz")
    np.savez_compressed(matrix_path, **matrices)
    summary["matrices_file"] = matrix_path.name
    summary["matrices_sha256"] = digest(matrix_path)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: summary[key] for key in ["status", "model", "checks_passed", "checks_failed", "analysis_wall_s"]}))
    return 0 if summary["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "--raw", dest="raw", required=True, type=Path)
    parser.add_argument("--protocol", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    matrix_path = args.output.with_name(args.output.stem + "_matrices.npz")
    if args.output.exists() or matrix_path.exists():
        parser.error("refusing to overwrite existing evidence")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        return analyze(args)
    except Exception as error:
        # An interrupted/invalid raw prefix is still delivered as explicit failure.
        failure = {"schema": "P4_COMAU_QUALIFICATION_ANALYSIS_V1", "status": "FAIL_ANALYSIS",
                   "reason": str(error), "raw_sha256": digest(args.raw) if args.raw.exists() else None,
                   "protocol_sha256": digest(args.protocol) if args.protocol.exists() else None,
                   "analysis_source_sha256": digest(Path(__file__)), "source_file": str(args.raw),
                   "not_executed": ["collision qualification", "formal planning", "FR3 adaptation"]}
        args.output.write_text(json.dumps(failure, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"status": failure["status"], "reason": failure["reason"]}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
