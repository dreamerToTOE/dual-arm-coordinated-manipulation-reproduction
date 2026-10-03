"""Validate the known-motion physics stream from an external ROS2 process.

Calibration tolerances below test the sensor plumbing, not benchmark success.
No joint, suction, feed, or rail publishers are created.
"""

import argparse
import json
import math
from pathlib import Path
import time

import rclpy
from geometry_msgs.msg import PoseArray
from rosgraph_msgs.msg import Clock
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from std_msgs.msg import String


def stamp_ns(stamp):
    return stamp.sec * 1_000_000_000 + stamp.nanosec


def angle_deg(first, second):
    norm = math.sqrt(sum(v * v for v in first) * sum(v * v for v in second))
    dot = abs(sum(a * b for a, b in zip(first, second))) / norm
    return math.degrees(2 * math.acos(min(1.0, dot)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-sec", type=float, default=150.0)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.timeout_sec <= 0:
        parser.error("timeout-sec must be positive")
    rclpy.init()
    node = rclpy.create_node("task01_physics_stream_validator")
    calibration, poses, snapshots, clocks, parse_errors = {}, [], {}, [], []

    def on_calibration(message):
        calibration.update(json.loads(message.data))

    def on_pose(message):
        if len(message.poses) != 1:
            parse_errors.append("Expected the one-body calibration fixture")
            return
        pose = message.poses[0]
        poses.append({"stamp_ns": stamp_ns(message.header.stamp),
                      "frame_id": message.header.frame_id,
                      "position_m": [pose.position.x, pose.position.y, pose.position.z],
                      "quaternion_xyzw": [pose.orientation.x, pose.orientation.y,
                                          pose.orientation.z, pose.orientation.w]})

    def on_snapshot(message):
        row = json.loads(message.data)
        snapshots[row["stamp_ns"]] = row

    subscriptions = [
        node.create_subscription(String, "/task01/physics/calibration", on_calibration,
                                 QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)),
        node.create_subscription(PoseArray, "/task01/physics/cube_poses", on_pose, 200),
        node.create_subscription(String, "/task01/physics/cube_poses/snapshot", on_snapshot, 200),
        node.create_subscription(Clock, "/clock", lambda msg: clocks.append(stamp_ns(msg.clock)),
                                 QoSProfile(depth=200, reliability=ReliabilityPolicy.BEST_EFFORT)),
    ]
    print("[TASK01 physics observer] READY: listening only, no command publishers", flush=True)
    try:
        deadline, finished = time.monotonic() + args.timeout_sec, None
        while time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.05)
            if calibration and poses:
                end = calibration["baseline_time_s"] + calibration["motion_duration_s"] + 0.2
                if poses[-1]["stamp_ns"] / 1e9 >= end and finished is None:
                    finished = time.monotonic()
                if finished is not None and time.monotonic() - finished >= 0.5:
                    break
        if not calibration or not poses or not clocks:
            raise RuntimeError("Timed out waiting for calibration, poses and /clock")

        position_errors, rotation_errors, norm_errors, matched_errors, step_ids = [], [], [], [], []
        motion_rows = []
        for row in poses:
            sample_time = row["stamp_ns"] / 1e9 - calibration["baseline_time_s"]
            if sample_time <= 0 or sample_time > calibration["motion_duration_s"] + 1e-6:
                continue
            motion_rows.append(row)
            expected = [calibration["initial_position_m"][i] +
                        calibration["linear_velocity_m_s"][i] * sample_time for i in range(3)]
            position_errors.append(math.dist(row["position_m"], expected) * 1000)
            x, y, z, w = calibration["initial_quaternion_xyzw"]
            half = 0.5 * calibration["angular_velocity_z_rad_s"] * sample_time
            sine, cosine = math.sin(half), math.cos(half)
            expected_quaternion = [cosine * x - sine * y, cosine * y + sine * x,
                                   cosine * z + sine * w, cosine * w - sine * z]
            rotation_errors.append(angle_deg(row["quaternion_xyzw"], expected_quaternion))
            norm_errors.append(abs(math.sqrt(sum(v * v for v in row["quaternion_xyzw"])) - 1))
            info = snapshots.get(row["stamp_ns"])
            if info is not None:
                body = info["bodies"][0]
                matched_errors.append(max(math.dist(body["position_m"], row["position_m"]),
                    math.dist(body["quaternion_xyzw"], row["quaternion_xyzw"])))
                step_ids.append(info["physics_step"])

        if not motion_rows:
            raise RuntimeError("No known-motion samples received")
        nearest_clock_errors = [min(abs(row["stamp_ns"] - c) for c in clocks)
                                for row in motion_rows]
        required_count = math.ceil(0.9 * calibration["motion_duration_s"] / calibration["physics_dt_s"])
        checks = {
            "motion_samples_at_least_90_percent": len(motion_rows) >= required_count,
            "pose_stamps_strictly_increasing": all(
                b["stamp_ns"] > a["stamp_ns"] for a, b in zip(poses, poses[1:])),
            "simulation_time_not_wall_time": max(row["stamp_ns"] for row in poses) < 60 * 1e9,
            "world_frame": all(row["frame_id"] == "world" for row in poses),
            "position_matches_known_motion_within_10_um": max(position_errors) <= 0.01,
            "rotation_matches_known_motion_within_0_001_deg": max(rotation_errors) <= 0.001,
            "quaternion_unit_norm": max(norm_errors) <= 1e-12,
            "every_motion_pose_has_same_snapshot": len(matched_errors) == len(motion_rows),
            "pose_and_snapshot_identical": bool(matched_errors) and max(matched_errors) <= 1e-12,
            "physics_steps_strictly_increasing": all(b > a for a, b in zip(step_ids, step_ids[1:])),
            "clock_in_same_time_domain": max(nearest_clock_errors) <=
                round(calibration["rendering_dt_s"] * 1e9) + 2,
            "no_message_parse_errors": not parse_errors,
        }
        summary = {
            "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
            "motion_samples": len(motion_rows), "total_pose_samples": len(poses),
            "clock_samples": len(clocks), "max_position_error_mm": max(position_errors),
            "max_rotation_error_deg": max(rotation_errors),
            "max_nearest_clock_stamp_difference_s": max(nearest_clock_errors) / 1e9,
            "calibration": calibration, "parse_errors": parse_errors,
        }
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "observer_summary.json").write_text(
            json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print("[TASK01 physics observer] " + json.dumps(summary, sort_keys=True), flush=True)
        if summary["status"] != "PASS":
            raise RuntimeError("Physics stream calibration failed; inspect summary")
    finally:
        for subscription in subscriptions:
            node.destroy_subscription(subscription)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
