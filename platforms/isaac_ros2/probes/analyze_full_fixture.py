"""[ENGINEERING] Streaming audit, not a benchmark/controller success oracle.

Raw reactions are joint-frame/anchor loads. The static check compensates the
unchanged hidden branch gravity only; moving samples remain uncalibrated.
"""

import argparse
from collections import defaultdict
import json
from pathlib import Path

import numpy as np


def rotation_xyzw(quaternion):
    q = np.asarray(quaternion, dtype=float)
    if q.shape != (4,) or not np.isfinite(q).all() or np.linalg.norm(q) < 1e-12:
        raise ValueError("invalid quaternion")
    x, y, z, w = q / np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])


def static_excess_wrench(row, topology, side):
    """Return parent support minus known branch gravity, about physical TCP.

    The actual link8 incoming fixed-joint axes/anchor are verified first. This
    sign is parent-on-child support; after gravity removal it is the load the
    mount supplies to the payload, NOT a calibrated per-cup internal force.
    """
    paths = topology[side]["link_paths"][0]
    anchor_index = paths.index(f"/World/{side}_fr3/fr3_link8")
    frame = topology["incoming_joint_frames_authored"][paths[anchor_index]]
    if frame["joint_type"] != "PhysicsFixedJoint":
        raise ValueError("incoming axes require independent rotating-joint validation")
    if not np.allclose(frame["child_local_anchor_m_authored"], 0, atol=1e-9):
        raise ValueError("unexpected link8 joint anchor")
    if not np.allclose(frame["child_local_joint_quaternion_xyzw"], [0, 0, 0, 1], atol=1e-9):
        raise ValueError("unexpected link8 joint axes")
    expected_names = {"fr3_link8", "fr3_hand", "fr3_leftfinger", "fr3_rightfinger", "fr3_hand_tcp"}
    if {path.rsplit("/", 1)[-1] for path in paths[anchor_index:]} != expected_names:
        raise ValueError("branch topology changed; audit descendants before compensation")
    data = row["articulations"][side]
    poses = np.asarray(data["link_poses_world_xyzw"], dtype=float)[0]
    raw = np.asarray(data["incoming_joint_wrench_raw"], dtype=float)[0, anchor_index]
    anchor = poses[anchor_index, :3]
    rotation = rotation_xyzw(poses[anchor_index, 3:])
    force = rotation @ raw[:3]
    torque = rotation @ raw[3:]
    masses = np.asarray(topology[side]["masses_kg"])[0]
    coms = np.asarray(topology[side]["com_poses"])[0]
    for index in range(anchor_index, len(paths)):
        center = poses[index, :3] + rotation_xyzw(poses[index, 3:]) @ coms[index, :3]
        support = np.array([0., 0., 9.81 * masses[index]])
        force -= support
        torque -= np.cross(center - anchor, support)
    tcp = np.asarray(row["tcp_poses_world_from_physics_link8"][side]["position_m"])
    return np.r_[force, torque + np.cross(anchor - tcp, force)]


def statistics(values):
    if not values:
        return {"count": 0}
    array = np.asarray(values)
    return {"count": len(values), "max": float(array.max()),
            "rms": float(np.sqrt(np.mean(array**2))), "median": float(np.median(array))}


def payload_support(row, topology, body):
    """Sum gravity-compensated support about the physical payload center."""
    center = np.asarray(body["position_m"])
    loads = {side: static_excess_wrench(row, topology, side) for side in ("left", "right")}
    force = sum(load[:3] for load in loads.values())
    torque = sum(load[3:] + np.cross(
        np.asarray(row["tcp_poses_world_from_physics_link8"][side]["position_m"])-center,
        load[:3]) for side, load in loads.items())
    return np.r_[force, torque]


def support_statistics(wrenches, expected_force):
    """Keep mean bias separate from instantaneous error; neither is a PASS gate.

    Analyze all recorded physics steps: decimation without anti-aliasing can
    turn an alternating reaction into a false DC offset.
    """
    if not wrenches:
        return {"count": 0}
    array = np.asarray(wrenches)
    mean = array.mean(axis=0)
    return {"count": len(wrenches), "mean_wrench_world_about_cube_center": mean.tolist(),
            "mean_force_error_n": float(np.linalg.norm(mean[:3]-expected_force)),
            "mean_moment_error_nm": float(np.linalg.norm(mean[3:])),
            "instantaneous_force_error_n": statistics(np.linalg.norm(
                array[:, :3]-expected_force, axis=1).tolist()),
            "instantaneous_moment_error_nm": statistics(np.linalg.norm(array[:, 3:], axis=1).tolist()),
            "status": "DIAGNOSTIC_ONLY_NOT_CALIBRATED"}


def suction_face(tcp, body):
    """Identify the face geometrically; these are audit bins, not control gates.

    CLOSED alone does not identify the contacted body. Require near-face-center
    position and inward local +X cup normal before associating it with a Cube.
    """
    rotation = rotation_xyzw(body["quaternion_xyzw"])
    local = rotation.T @ (np.asarray(tcp["position_m"])-body["position_m"])
    normal = rotation.T @ rotation_xyzw(tcp["quaternion_xyzw"])[:, 0]
    for axis, label in ((0, "X"), (1, "Y"), (2, "Z")):
        others = [index for index in range(3) if index != axis]
        if max(abs(local[index]) for index in others) > .015:
            continue
        for sign in (-1, 1):
            if abs(local[axis]-sign*.06) <= .010 and -sign*normal[axis] > .99:
                return ("+" if sign > 0 else "-") + label
    return None


def audit(raw_dir, max_samples=None):
    topology = json.loads((raw_dir / "topology.json").read_text())
    errors, peaks, force_checks = defaultdict(int), defaultdict(float), defaultdict(list)
    protocols = {f"Cube_{index:02d}": defaultdict(int) for index in range(1, 6)}
    count, previous, last_row, previous_static, stable_since = 0, None, None, None, None
    dt_range, matrix_error = [float("inf"), 0.], 0.
    first_closed_step, last_closed_step, ever_closed, hold_started = None, None, False, None
    tagged_hold_checks = defaultdict(list)
    hold_wrenches, previous_hold = [], None
    with (raw_dir / "physics_contact_samples.jsonl").open() as stream:
        for line in stream:
            if max_samples and count >= max_samples:
                break
            row = json.loads(line)
            count += 1
            sample = row["physics"]
            key = sample["physics_step"], sample["stamp_ns"]
            if previous:
                errors["missing_steps"] += max(0, key[0] - previous[0] - 1)
                errors["nonmonotonic"] += int(key[0] <= previous[0] or key[1] <= previous[1])
            previous, last_row = key, row
            ever_closed = ever_closed or any(row["suction_closed"].values())
            errors["wrong_body_count"] += int(len(sample["bodies"]) != 5)
            for body in sample["bodies"]:
                body_values = (body["position_m"] + body["quaternion_xyzw"] +
                               body["linear_velocity_m_s"] + body["angular_velocity_rad_s"])
                errors["nonfinite_body"] += int(not np.isfinite(body_values).all())
                errors["quaternion_not_normalized"] += int(
                    abs(np.dot(body["quaternion_xyzw"], body["quaternion_xyzw"])-1) > 1e-6)
            for side in ("left", "right"):
                errors["nonfinite_articulation"] += int(not all(
                    np.isfinite(row["articulations"][side][field]).all()
                    for field in ("link_poses_world_xyzw", "incoming_joint_wrench_raw")))
            for contact in row["contacts"]:
                errors["stamp_step_mismatch"] += int(
                    (contact["physics_step"], contact["stamp_ns"]) != key)
                dt = contact["physics_dt_s"]
                errors["invalid_dt"] += int(not np.isfinite(dt) or dt <= 0)
                dt_range = [min(dt_range[0], dt), max(dt_range[1], dt)]
                for pair in contact["pairs"]:
                    name = pair["sensor_path"] + " <-> " + pair["other_path"]
                    values = pair["collision_force_world_n"] + pair["collision_torque_about_sensor_origin_world_nm"]
                    errors["nonfinite_contact"] += int(not np.isfinite(values).all())
                    errors["nonfinite_components"] += int(not np.isfinite(
                        pair["force_matrix_world_n"] + pair["normal_force_world_n"] +
                        pair["friction_force_world_n"] + [pair["matrix_vs_normal_error_n"]]).all())
                    peaks[name] = max(peaks[name], float(np.linalg.norm(values[:3])))
                    matrix_error = max(matrix_error, pair["matrix_vs_normal_error_n"])
            closed = row["suction_closed"]
            # Explicit static-load diagnostics must retain every physics step.
            # Ordinary geometric/empty-load screening below remains decimated.
            if row.get("calibration_phase") == "STATIC_LIFT_HOLD":
                if hold_started is None:
                    hold_started = key[1]
                airborne = [body for body in sample["bodies"] if body["position_m"][2] > .3]
                if len(airborne) != 1 or not all(closed.values()):
                    errors["invalid_tagged_hold_state"] += 1
                else:
                    body = airborne[0]
                    if key[1]-hold_started > 1_000_000_000:
                        hold_wrenches.append(payload_support(row, topology, body))
                        tagged_hold_checks["cube_linear_speed_tensor_m_s"].append(
                            float(np.linalg.norm(body["linear_velocity_m_s"])))
                        tagged_hold_checks["cube_angular_speed_tensor_rad_s"].append(
                            float(np.linalg.norm(body["angular_velocity_rad_s"])))
                        if previous_hold:
                            dt_hold = (key[1]-previous_hold[0])*1e-9
                            position_velocity = (np.asarray(body["position_m"])-previous_hold[1])/dt_hold
                            tagged_hold_checks["cube_position_fd_speed_m_s"].append(
                                float(np.linalg.norm(position_velocity)))
                            tagged_hold_checks["tensor_vs_position_fd_velocity_error_m_s"].append(
                                float(np.linalg.norm(np.asarray(body["linear_velocity_m_s"])-position_velocity)))
                    previous_hold = key[1], np.asarray(body["position_m"])
            else:
                hold_started = None
                previous_hold = None
            if count % 6 != 0:
                continue
            poses = np.concatenate([np.asarray(row["articulations"][side]["link_poses_world_xyzw"])[0]
                                    for side in ("left", "right")])
            for index, body in enumerate(sample["bodies"], 1):
                faces = {side: suction_face(row["tcp_poses_world_from_physics_link8"][side], body)
                         if closed[side] else None for side in ("left", "right")}
                face_set = {face for face in faces.values() if face}
                if face_set == {"-Y", "+Y"}:
                    protocols[f"Cube_{index:02d}"]["dual_opposed_side_closed_samples"] += 1
                if len(face_set) == 2 and "-X" in face_set and face_set.intersection({"-Y", "+Y"}):
                    protocols[f"Cube_{index:02d}"]["rear_plus_side_closed_samples"] += 1
                if face_set == {"-X"}:
                    protocols[f"Cube_{index:02d}"]["rear_only_closed_samples"] += 1
            dt = (key[1] - previous_static[0]) * 1e-9 if previous_static else 0
            # Metrology sample selection only, not new benchmark/controller gates.
            stationary = False
            if dt > 0:
                old_poses = previous_static[1]
                speed = np.linalg.norm(poses[:, :3] - old_poses[:, :3], axis=1).max() / dt
                dots = np.abs(np.sum(poses[:, 3:] * old_poses[:, 3:], axis=1))
                norms = np.linalg.norm(poses[:, 3:], axis=1) * np.linalg.norm(old_poses[:, 3:], axis=1)
                angular_speed = (2*np.arccos(np.clip(dots/norms, 0, 1))).max() / dt
                stationary = speed < 0.002 and angular_speed < 0.01
            previous_static = key[1], poses.copy()
            if not stationary:
                stable_since = None
                continue
            if stable_since is None:
                stable_since = key[1]
            if key[1] - stable_since < 1_000_000_000:
                continue
            loads = {side: static_excess_wrench(row, topology, side) for side in ("left", "right")}
            # Only initial empty-arm samples: after a release an OPEN tool may
            # still be pressing a Cube, so OPEN is not evidence of zero load.
            if not ever_closed:
                for side in loads:
                    tcp_position = np.asarray(row["tcp_poses_world_from_physics_link8"][side]["position_m"])
                    # Near a Cube, an OPEN cup can already carry collision load.
                    if any(np.linalg.norm(tcp_position-np.asarray(body["position_m"])) < .2
                           for body in sample["bodies"] if body["position_m"][2] > .2):
                        continue
                    force_checks[f"empty_{side}_force_error_n"].append(float(np.linalg.norm(loads[side][:3])))
                    force_checks[f"empty_{side}_torque_error_nm"].append(float(np.linalg.norm(loads[side][3:])))
            if all(closed.values()):
                airborne = [(i, body) for i, body in enumerate(sample["bodies"])
                            if body["position_m"][2] > 0.30 and
                            np.linalg.norm(body["linear_velocity_m_s"]) < 0.001 and
                            np.linalg.norm(body["angular_velocity_rad_s"]) < 0.01]
                # Both tool TCPs must be adjacent to the same airborne body.
                for index, body in airborne:
                    center = np.asarray(body["position_m"])
                    if max(np.linalg.norm(np.asarray(row["tcp_poses_world_from_physics_link8"][side]["position_m"])-center)
                           for side in loads) > 0.09:
                        continue
                    if any(np.linalg.norm(pair["collision_force_world_n"]) > 0.01
                           for pair in row["contacts"][index]["pairs"]):
                        continue
                    force = sum(load[:3] for load in loads.values())
                    torque = sum(load[3:] + np.cross(
                        np.asarray(row["tcp_poses_world_from_physics_link8"][side]["position_m"])-center,
                        load[:3]) for side, load in loads.items())
                    force_checks["airborne_payload_support_error_n"].append(float(np.linalg.norm(force-[0, 0, 0.8*9.81])))
                    force_checks["airborne_payload_moment_error_nm"].append(float(np.linalg.norm(torque)))
                    first_closed_step = key[0] if first_closed_step is None else first_closed_step
                    last_closed_step = key[0]
    if not count:
        raise ValueError("empty recording")
    final_geometry = []
    targets_y = [.243, -.243, .1215, -.1215, 0.]
    for index, body in enumerate(last_row["physics"]["bodies"]):
        center = np.asarray(body["position_m"])
        rotation = rotation_xyzw(body["quaternion_xyzw"])
        extent = np.abs(rotation) @ np.array([.06, .06, .06])
        final_geometry.append({"prim_path": body["prim_path"], "position_m": center.tolist(),
            "quaternion_xyzw": body["quaternion_xyzw"],
            "yaw_deg": float(np.degrees(np.arctan2(rotation[1, 0], rotation[0, 0]))),
            "nominal_cell_center_error_mm": float(np.linalg.norm(center-[1.1, targets_y[index], .26])*1000),
            "oriented_nearest_deep_wall_gap_mm": float((1.16-center[0]-extent[0])*1000),
            "oriented_nearest_plus_wall_gap_mm": float((.303-center[1]-extent[1])*1000),
            "oriented_nearest_minus_wall_gap_mm": float((center[1]-extent[1]+.303)*1000)})
    return {"status": "PASS_RECORD_INTEGRITY" if not any(errors.values()) else "FAIL_RECORD_INTEGRITY",
        "snapshots": count, "partial_prefix_only": max_samples is not None,
        "errors": dict(errors), "physics_dt_range_s": dt_range,
        "normal_matrix_max_error_n": matrix_error,
        "sampled_contact_topology_audit": {name: dict(counts) for name, counts in protocols.items()},
        "contact_topology_audit_note": "Every sixth recorded step; CLOSED + physical TCP/cup normal near face center is geometric association, not per-cup force proof",
        "static_gravity_consistency": {name: statistics(values) for name, values in force_checks.items()},
        "explicit_hold_metrology": {
            "sampling": "Every recorded physics step; first observed simulation second excluded",
            "net_payload_support": support_statistics(hold_wrenches, np.array([0, 0, .8*9.81])),
            "kinematics": {name: statistics(values) for name, values in tagged_hold_checks.items()},
            "expected_payload_mass_kg": .8,
            "mass_provenance": "legacy scene constant; independently confirmed by separate physics mass audit",
            "note": "Hold phase does not by itself prove static force balance or calibrated per-cup wrench"},
        "static_airborne_checked_step_range": [first_closed_step, last_closed_step],
        "final_geometry": final_geometry, "peak_pair_collision_force_n": dict(peaks),
        "limitations": ["No dynamic inertia compensation; no per-cup internal-force calibration",
                        "Stationarity criteria are metrology filters, not frozen benchmark gates",
                        "Nearest plane gaps do not prove entire face flush",
                        "Controller/protocol completion must be checked separately"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Audit only a complete prefix; never infer final placement from this")
    args = parser.parse_args()
    if args.max_samples is not None and args.max_samples <= 0:
        parser.error("max-samples must be positive")
    result = audit(args.raw_dir, args.max_samples)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items()
                      if key != "peak_pair_collision_force_n"}, indent=2))
    if result["status"] != "PASS_RECORD_INTEGRITY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
