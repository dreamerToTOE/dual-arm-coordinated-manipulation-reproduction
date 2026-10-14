"""Independent ABB geometry oracle for saved native qualification JSON.

This module generates no random configurations and invokes no author solver,
sampler, collision checker, planner or robot.  It composes the six documented
joint axes and offsets independently of the author's expanded FK expressions.
Single-arm Jacobian fixtures and abstract Eq. (7) enumeration do not establish
dual-arm closure, collision freedom, RSS target generation or global planning.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from math import atan2, cos, sin
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


GEOMETRY_MM = {
    "b": 166.0, "l1": 124.0, "l2": 270.0, "l3a": 70.0,
    "l3b": 149.6, "l4": 152.4, "l5": 65.5, "lee": 66.5,
}
AXES = ("z", "y", "y", "x", "y", "x")


def _vector(value: Any, count: int) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (count,) or not np.isfinite(result).all():
        raise ValueError(f"expected finite vector of length {count}")
    return result


def _matrix(value: Any) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (4, 4) or not np.isfinite(result).all():
        raise ValueError("expected finite 4 by 4 transformation")
    return result


def translation(vector: Sequence[float]) -> np.ndarray:
    result = np.eye(4)
    result[:3, 3] = _vector(vector, 3)
    return result


def rotation(axis: str, angle: float) -> np.ndarray:
    c, s = cos(float(angle)), sin(float(angle))
    result = np.eye(4)
    if axis == "x":
        result[:3, :3] = [[1, 0, 0], [0, c, -s], [0, s, c]]
    elif axis == "y":
        result[:3, :3] = [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    elif axis == "z":
        result[:3, :3] = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    else:
        raise ValueError("unknown revolute axis")
    return result


def abb_fk_and_jacobian(q: Sequence[float], base: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """World FK in mm and world geometric [linear, angular] Jacobian.

    ``base`` is [x_mm, y_mm, yaw_rad], as in the author APC constructor.
    No modern URDF, zero-position correction or exact-pi replacement is used.
    """
    q = _vector(q, 6)
    base = _vector(base, 3)
    g = GEOMETRY_MM
    offsets = ((0, 0, g["l1"]), (0, 0, g["l2"]),
               (g["l3b"], 0, g["l3a"]), (g["l4"], 0, 0),
               (g["l5"], 0, 0), (g["lee"], 0, 0))
    transform = translation((base[0], base[1], g["b"])) @ rotation("z", base[2])
    origins, directions = [], []
    axis_vectors = {"x": np.array([1., 0., 0.]),
                    "y": np.array([0., 1., 0.]), "z": np.array([0., 0., 1.])}
    for angle, axis, offset in zip(q, AXES, offsets):
        origins.append(transform[:3, 3].copy())
        directions.append(transform[:3, :3] @ axis_vectors[axis])
        transform = transform @ rotation(axis, angle) @ translation(offset)
    endpoint = transform[:3, 3]
    jacobian = np.vstack((np.column_stack([np.cross(axis, endpoint-origin)
                                         for axis, origin in zip(directions, origins)]),
                          np.column_stack(directions)))
    return transform, jacobian


def abb_fk(q: Sequence[float], base: Sequence[float]) -> np.ndarray:
    return abb_fk_and_jacobian(q, base)[0]


def independent_author_kdl_chain_fk(q: Sequence[float], rod_length_mm: float) -> np.ndarray:
    """Compose the documented forward/reversed 12-joint KDL chain in mm.

    The reversed second-arm coordinates, final sign and integer source offsets
    are preserved.  Agreement with this chain is reported separately from the
    physical two-arm relation using the author's approximate-pi base frame.
    """
    q = _vector(q, 12)
    g = GEOMETRY_MM
    # In kdl_class.cpp the literal integer expressions give 66 and 66.
    # APC gives 65.5 and 66.5.  Preserve both, rather than hide the source
    # difference; their sum is equal for this endpoint-only check.
    kdl_l5, kdl_lee = 66.0, 66.0
    transform = translation((0, 0, g["b"]))
    forward_offsets = ((0, 0, g["l1"]), (0, 0, g["l2"]),
                       (g["l3b"], 0, g["l3a"]), (g["l4"], 0, 0),
                       (kdl_l5, 0, 0), (2*kdl_lee+float(rod_length_mm), 0, 0))
    for angle, axis, offset in zip(q[:6], AXES, forward_offsets):
        transform = transform @ rotation(axis, angle) @ translation(offset)
    reversed_q = q[6:][::-1].copy()
    reversed_q[-1] = -reversed_q[-1]
    reversed_offsets = ((kdl_l5, 0, 0), (g["l4"], 0, 0),
                        (g["l3b"], 0, -g["l3a"]), (0, 0, -g["l2"]),
                        (0, 0, -g["l1"]), (0, 0, -g["b"]))
    for angle, axis, offset in zip(reversed_q, ("x", "y", "x", "y", "y", "z"), reversed_offsets):
        transform = transform @ rotation(axis, angle) @ translation(offset)
    return transform


def _vee_skew(matrix: np.ndarray) -> np.ndarray:
    skew_part = 0.5*(matrix-matrix.T)
    return np.array([skew_part[2, 1], skew_part[0, 2], skew_part[1, 0]])


def finite_difference_from_transforms(center: Any, plus: Any, minus: Any,
                                     epsilon: float) -> np.ndarray:
    """Spatial geometric derivative; position in mm, angular in rad/rad."""
    center = _matrix(center)
    plus = np.asarray(plus, dtype=float)
    minus = np.asarray(minus, dtype=float)
    if plus.shape != (6, 4, 4) or minus.shape != (6, 4, 4):
        raise ValueError("expected six plus and six minus transformations")
    if not np.isfinite(plus).all() or not np.isfinite(minus).all():
        raise ValueError("nonfinite finite-difference transformations")
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("invalid finite-difference epsilon")
    columns = []
    for p, m in zip(plus, minus):
        derivative = (p-m)/(2.0*epsilon)
        angular = _vee_skew(derivative[:3, :3] @ center[:3, :3].T)
        columns.append(np.r_[derivative[:3, 3], angular])
    return np.column_stack(columns)


def rank_evidence(jacobian: Any, relative_threshold: float) -> dict[str, Any]:
    jacobian = np.asarray(jacobian, dtype=float)
    if jacobian.shape != (6, 6) or not np.isfinite(jacobian).all():
        raise ValueError("expected finite 6 by 6 Jacobian")
    in_metres = jacobian.copy()
    in_metres[:3] /= 1000.0
    sigma = np.linalg.svd(in_metres, compute_uv=False)
    cutoff = float(relative_threshold * sigma[0])
    return {"rank": int(np.count_nonzero(sigma > cutoff)), "cutoff": cutoff,
            "relative_threshold": float(relative_threshold),
            "singular_values_translation_m": sigma.tolist(),
            "singular_values_translation_mm": np.linalg.svd(jacobian, compute_uv=False).tolist(),
            "determinant_unscaled_mm3": float(np.linalg.det(jacobian)),
            "jacobian_translation_mm_angular_rad": jacobian.tolist(),
            "rank_scaling": "translation rows /1000; angular rows unchanged; diagnostic mixed-row SVD, not a physical norm"}


def transform_errors(actual: Any, expected: Any) -> dict[str, float]:
    actual, expected = _matrix(actual), _matrix(expected)
    delta = actual[:3, 3]-expected[:3, 3]
    r = actual[:3, :3] @ expected[:3, :3].T
    angle = atan2(float(np.linalg.norm(_vee_skew(r))), float((np.trace(r)-1.0)/2.0))
    return {"translation_max_abs_mm": float(np.max(np.abs(delta))),
            "translation_l2_mm": float(np.linalg.norm(delta)),
            "rotation_matrix_max_abs": float(np.max(np.abs(actual[:3, :3]-expected[:3, :3]))),
            "rotation_geodesic_rad": float(angle),
            "bottom_row_max_abs": float(np.max(np.abs(actual[3]-np.array([0., 0., 0., 1.])))),
            "rotation_orthogonality_max_abs": float(np.max(np.abs(actual[:3, :3].T @ actual[:3, :3]-np.eye(3)))),
            "rotation_determinant": float(np.linalg.det(actual[:3, :3]))}


def _passes(errors: Mapping[str, float], translation_gate_mm: float,
            rotation_gate: float) -> bool:
    return bool(errors["translation_max_abs_mm"] <= translation_gate_mm
                and errors["rotation_matrix_max_abs"] <= rotation_gate)


def equation7_enumeration() -> dict[str, Any]:
    """Abstract equal-weight labels, not robot samples or a formula repair."""
    tuples = list(itertools.product(range(2), range(4), range(4)))
    reference = (0, 0, 0)
    rows = []
    for wrist, elbow_a, elbow_b in tuples:
        a = wrist == reference[0] and elbow_a == reference[1]
        b = wrist == reference[0] and elbow_b == reference[2]
        rows.append({"shared_wrist": wrist, "elbow_A": elbow_a, "elbow_B": elbow_b,
                     "same_chain_A_branch": a, "same_chain_B_branch": b})
    count_a = sum(row["same_chain_A_branch"] for row in rows)
    count_b = sum(row["same_chain_B_branch"] for row in rows)
    count_intersection = sum(row["same_chain_A_branch"] and row["same_chain_B_branch"] for row in rows)
    count_union = count_a+count_b-count_intersection
    count_b_not_a = count_b-count_intersection
    total = len(rows)
    # Evaluate the printed equations unchanged with xi_i=xi_j=8 and
    # xi_ij=4 canceled branches due to the shared binary wrist.
    original_eq7_value = (1.0-1.0/8.0)/(8.0-4.0)
    original_eq8_pair_not_shared = 1.0-original_eq7_value
    return {"schema": "P4_EQ7_ABSTRACT_32_TUPLES_V1", "rows": rows,
            "reference": list(reference), "total": total,
            "counts": {"A": count_a, "B": count_b, "A_and_B": count_intersection,
                       "A_or_B": count_union, "B_and_not_A": count_b_not_a, "not_A": total-count_a},
            "probabilities": {"A": count_a/total, "B": count_b/total,
                              "A_and_B": count_intersection/total, "A_or_B": count_union/total,
                              "B_given_not_A": count_b_not_a/(total-count_a)},
            "original_equations_unchanged": {"xi_i": 8, "xi_j": 8, "xi_ij": 4,
                                            "equation7_value": original_eq7_value,
                                            "equation8_dependent_pair_not_shared": original_eq8_pair_not_shared,
                                            "equation9_pair_upper_fraction": 1.0-original_eq8_pair_not_shared},
            "observation": "Printed Eq7 value equals the toy union 7/32, while the toy conditional P(B|not A)=3/28. The semantic distinction is reported; Eq7/8 and author methods are not changed.",
            "scope": "abstract equally weighted branch labels; no geometry, joint limits, collision, actual manifold distribution or measured robot visibility"}


def analyze_native_records(payload: Mapping[str, Any], protocol: Mapping[str, Any]) -> dict[str, Any]:
    """Analyze the root native-driver payload; keep native failures as data."""
    if protocol.get("frozen") is not True:
        raise ValueError("qualification protocol must be frozen before analysis")
    d, length = float(payload["D_mm"]), float(payload["L_mm"])
    bases = {1: _vector(payload["base1"], 3), 2: _vector(payload["base2"], 3)}
    epsilon = float(protocol["finite_difference_eps_rad"])
    rank_relative = float(protocol["svd_rank_relative_threshold"])
    fk_translation_gate = float(protocol["independent_fk_abs_translation_gate_mm"])
    fk_rotation_gate = float(protocol["independent_fk_abs_rotation_matrix_gate"])
    projection_translation_gate = float(protocol["ik_projection_abs_translation_gate_mm"])
    projection_rotation_gate = float(protocol["ik_projection_abs_rotation_matrix_gate"])
    approx_pi = float(payload.get("approxPI", bases[2][2]))
    bounds = np.array([[-165., 165.], [-110., 110.], [-110., 70.],
                       [-160., 160.], [-120., 120.], [-400., 400.]]) * approx_pi/180.0
    rows = list(payload["rows"])
    evidence, checks, diagnostics = [], [], []
    counts = Counter(str(row.get("kind")) for row in rows)
    ik_targets: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    jacobian_fixtures = {}

    def check(label: str, passed: bool, row_index: int | None = None, **extra: Any) -> None:
        checks.append({"check": label, "passed": bool(passed), "row_index": row_index, **extra})

    def source_fk_check(row: Mapping[str, Any], index: int, field: str, q: np.ndarray, robot: int) -> dict[str, float]:
        expected = abb_fk(q, bases[robot])
        errors = transform_errors(row[field], expected)
        check(f"independent_fk:{field}", _passes(errors, fk_translation_gate, fk_rotation_gate), index, robot=robot, **errors)
        return errors

    def closed_geometry(q: np.ndarray) -> dict[str, Any]:
        first = abb_fk(q[:6], bases[1])
        second = abb_fk(q[6:], bases[2])
        rod = translation((length, 0, 0))
        facing = np.diag([-1., -1., 1., 1.])
        physical_errors = transform_errors(first @ rod @ facing, second)
        chain = independent_author_kdl_chain_fk(q, length)
        chain_errors = transform_errors(chain, translation((d, 0, 0)))
        return {"T1_independent": first.tolist(), "T2_independent": second.tolist(),
                "T_chain_independent": chain.tolist(),
                "physical_rigid_grasp_closure": physical_errors,
                "author_kdl_chain_target": chain_errors,
                "both_arm_angle_limits_passed": bool(np.all(q.reshape(2, 6) >= bounds[:, 0])
                                                     and np.all(q.reshape(2, 6) <= bounds[:, 1])),
                "no_collision_test": True}

    for index, row in enumerate(rows):
        kind = row.get("kind")
        item: dict[str, Any] = {"row_index": index, "kind": kind}
        try:
            if kind == "fk":
                q, robot = _vector(row["q"], 6), int(row["robot"])
                item.update(robot=robot, q=q.tolist(), errors=source_fk_check(row, index, "T", q, robot))
            elif kind == "ik":
                robot, sample = int(row["robot"]), int(row["index"])
                item.update(robot=robot, index=sample, branch=int(row["branch"]), native_success=bool(row["success"]))
                ik_targets[(sample, robot)].append(row)
                if not row["success"]:
                    item["classification"] = "NATIVE_BRANCH_REJECTION_RETAINED"
                else:
                    solution = _vector(row["solution"], 6)
                    expected = abb_fk(solution, bases[robot])
                    target_errors = transform_errors(expected, row["target"])
                    native_fk_errors = source_fk_check(row, index, "T_out", solution, robot)
                    angle_limits = bool(np.all(solution >= bounds[:, 0]) and np.all(solution <= bounds[:, 1]))
                    check("ik_success_roundtrip", _passes(target_errors, projection_translation_gate, projection_rotation_gate), index, **target_errors)
                    check("ik_success_native_joint_limits", angle_limits, index)
                    item.update(solution=solution.tolist(), target_errors=target_errors,
                                output_fk_errors=native_fk_errors, native_joint_limits_passed=angle_limits)
            elif kind == "unreachable_ik":
                item.update(robot=int(row["robot"]), branch=int(row["branch"]), native_success=bool(row["success"]))
                check("far_unreachable_ik_rejected", not row["success"], index)
            elif kind in ("raw_endpoint", "closure_negative", "nr"):
                native_success = bool(row.get("success", True))
                item["native_success"] = native_success
                if kind == "nr":
                    item["wall_s"] = float(row["wall_s"])
                    item["input"] = _vector(row["input"], 12).tolist()
                    if not native_success:
                        item["classification"] = "NATIVE_NR_FAILURE_RETAINED"
                        check("native_nr_declared_fixed_case", False, index)
                        evidence.append(item)
                        continue
                    q = _vector(row["solution"], 12)
                else:
                    q = _vector(row["q"], 12)
                item.update(q=q.tolist(), geometry=closed_geometry(q))
                source_fk_check(row, index, "T1", q[:6], 1)
                source_fk_check(row, index, "T2", q[6:], 2)
                chain_errors = transform_errors(row["T_chain"], item["geometry"]["T_chain_independent"])
                check("independent_kdl_chain_fk", _passes(chain_errors, fk_translation_gate, fk_rotation_gate), index, **chain_errors)
                item["native_chain_agreement"] = chain_errors
                physical = item["geometry"]["physical_rigid_grasp_closure"]
                physical_pass = _passes(physical, projection_translation_gate, projection_rotation_gate)
                if kind == "raw_endpoint":
                    item["classification"] = "RAW_SOURCE_ENDPOINT_DIAGNOSTIC_NOT_REPAIRED"
                    item["component_threshold_comparison_only"] = physical_pass
                    diagnostics.append({"kind": "raw_endpoint", "row_index": index,
                                        "physical_component_threshold_comparison": physical_pass,
                                        "closure": physical,
                                        "scope": "not an accepted endpoint; source rounding/threshold provenance remains to be reviewed, and collision is untested"})
                elif kind == "closure_negative":
                    check("closure_perturbation_independently_rejected", not physical_pass, index, **physical)
                    item["scope"] = "independent closure negative only; native validity checker and collision not exercised"
                else:
                    check("native_nr_physical_rigid_grasp_closure", physical_pass, index, **physical)
                    check("native_nr_both_arm_joint_limits", item["geometry"]["both_arm_angle_limits_passed"], index)
                    chain_target = item["geometry"]["author_kdl_chain_target"]
                    check("native_nr_chain_target", _passes(chain_target, projection_translation_gate, projection_rotation_gate), index, **chain_target)
            elif kind == "jacobian_fixture":
                q, robot = _vector(row["q"], 6), int(row["robot"])
                transform, analytic = abb_fk_and_jacobian(q, bases[robot])
                source_fk_check(row, index, "T", q, robot)
                native_fd = finite_difference_from_transforms(row["T"], row["Tplus"], row["Tminus"], epsilon)
                independent_plus, independent_minus = [], []
                for j in range(6):
                    direction = np.eye(6)[j]*epsilon
                    independent_plus.append(abb_fk(q+direction, bases[robot]))
                    independent_minus.append(abb_fk(q-direction, bases[robot]))
                independent_fd = finite_difference_from_transforms(transform, independent_plus, independent_minus, epsilon)
                difference = native_fd-analytic
                item.update(name=row["name"], robot=robot, q=q.tolist(),
                            independent_analytic=rank_evidence(analytic, rank_relative),
                            native_finite_difference=rank_evidence(native_fd, rank_relative),
                            independent_finite_difference=rank_evidence(independent_fd, rank_relative),
                            native_fd_vs_analytic_position_max_abs_mm=float(np.max(np.abs(difference[:3]))),
                            native_fd_vs_analytic_position_max_abs_m=float(np.max(np.abs(difference[:3]/1000.0))),
                            native_fd_vs_analytic_angular_max_abs=float(np.max(np.abs(difference[3:]))),
                            independent_fd_vs_analytic_position_max_abs_mm=float(np.max(np.abs(independent_fd[:3]-analytic[:3]))),
                            independent_fd_vs_analytic_angular_max_abs=float(np.max(np.abs(independent_fd[3:]-analytic[3:]))),
                            derivative_error_status="DIAGNOSTIC: protocol contains no standalone derivative-error acceptance threshold",
                            scope="single-arm fixed fixture; no dual-arm closed sample, collision or RSS generation executed")
                ranks = [item[name]["rank"] for name in ("independent_analytic", "native_finite_difference", "independent_finite_difference")]
                name = str(row["name"])
                expected_rank = 5 if name == "wrist_zero" else 6
                check("fixture_rank_crosscheck:"+name, all(rank == expected_rank for rank in ranks), index,
                      ranks=ranks, expected_rank=expected_rank)
                if name == "author_elbow_only":
                    item["author_mode2_constant_alone_verified_singular"] = all(rank < 6 for rank in ranks)
                    item["source_rule_status"] = ("SINGLE_ARM_COUNTEREXAMPLE_TO_CONSTANT_SINGULAR_TAG" if all(rank == 6 for rank in ranks)
                                                   else "REQUIRES_SEPARATE_REVIEW")
                jacobian_fixtures[name] = item
            else:
                item["classification"] = "UNSUPPORTED_NATIVE_RECORD_KIND"
                check("supported_record_kind", False, index, record_kind=kind)
        except (ValueError, KeyError, TypeError, np.linalg.LinAlgError) as error:
            item["classification"] = "INVALID_SAVED_NATIVE_EVIDENCE"
            item["error"] = type(error).__name__+": "+str(error)
            check("finite_shape_and_record_contract", False, index, error=item["error"])
        evidence.append(item)

    check("fk_declared_row_count", counts["fk"] == int(protocol["fk_sample_count_per_model"]),
          actual=counts["fk"], expected=protocol["fk_sample_count_per_model"])
    check("ik_declared_target_count", len(ik_targets) == int(protocol["ik_roundtrip_sample_count_per_spatial_model"]),
          actual=len(ik_targets), expected=protocol["ik_roundtrip_sample_count_per_spatial_model"])
    branch_indices = set(int(value) for value in protocol["ik_branch_indices"])
    for target, target_rows in ik_targets.items():
        observed = [int(row["branch"]) for row in target_rows]
        check("ik_all_branch_indices_preserved", len(observed) == len(branch_indices) and set(observed) == branch_indices,
              target=list(target), observed=observed)
        check("ik_target_has_a_native_solution", any(row["success"] for row in target_rows), target=list(target))
    check("nr_declared_row_count", counts["nr"] == int(protocol["projection_near_endpoint_count_per_model"]),
          actual=counts["nr"], expected=protocol["projection_near_endpoint_count_per_model"])
    check("declared_jacobian_fixture_names", set(jacobian_fixtures) == {"author_elbow_only", "wrist_zero", "regular"},
          actual=sorted(jacobian_fixtures))
    failed = [entry for entry in checks if not entry["passed"]]
    return {"schema": "P4_ABB_INDEPENDENT_MATHEMATICAL_ORACLE_V1",
            "status": "FAIL_COMPONENT_QUALIFICATION" if failed else "PASS_MATHEMATICAL_COMPONENTS_ONLY",
            "environment": payload.get("environment"), "seed": payload.get("seed"),
            "D_mm": d, "L_mm": length, "base1": bases[1].tolist(), "base2": bases[2].tolist(),
            "author_approximate_pi_preserved": approx_pi,
            "geometry_mm": GEOMETRY_MM,
            "input_row_counts": dict(counts),
            "fk_rows_by_robot": dict(Counter(int(row["robot"]) for row in rows if row.get("kind") == "fk")),
            "checks": checks, "checks_total": len(checks), "checks_passed": len(checks)-len(failed),
            "checks_failed": len(failed), "failures": failed,
            "evidence": evidence, "raw_endpoint_diagnostics": diagnostics,
            "equation7_abstract_enumeration": equation7_enumeration(),
            "critical_scope_limits": ["No collision qualification or RSS random target generation was run.",
                                      "Single-arm fixtures do not establish dual-arm closure or global RSS planning.",
                                      "Raw source endpoints were not projected, reset, snapped or accepted.",
                                      "Author KDL chain agreement and physical rigid-grasp closure are distinct checks.",
                                      "Eq7 branch-label enumeration preserves the printed equations and does not represent robot visibility."]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = analyze_native_records(payload, protocol)
    result["input_sha256"] = hashlib.sha256(args.input.read_bytes()).hexdigest()
    result["protocol_sha256"] = hashlib.sha256(args.protocol.read_bytes()).hexdigest()
    result["oracle_source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps({"status": result["status"], "checks_total": result["checks_total"],
                      "checks_passed": result["checks_passed"], "checks_failed": result["checks_failed"],
                      "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
