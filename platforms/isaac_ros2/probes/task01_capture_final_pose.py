"""Read Isaac's final Cube_05 6D Ground Truth without commanding anything.

Run from a ROS 2 Humble terminal while the Task01 fixture bridge is still up.
This is an observation helper, not an acceptance gate or a force estimator.
"""

import argparse
import json
import math
import time

import rclpy
from geometry_msgs.msg import PoseArray
from rclpy.node import Node


class PoseCapture(Node):
    def __init__(self, topic):
        super().__init__("task01_cube05_final_pose_capture")
        self.samples = []
        self.create_subscription(PoseArray, topic, self._on_poses, 10)

    def _on_poses(self, message):
        if len(message.poses) < 5:
            return
        self.samples.append(message.poses[4])


def _orientation_degrees(pose):
    q = pose.orientation
    norm = math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w)
    if norm < 1e-9:
        raise ValueError("Cube_05 Ground Truth quaternion has near-zero norm")
    x, y, z, w = (q.x / norm, q.y / norm, q.z / norm, q.w / norm)
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return [math.degrees(value) for value in (roll, pitch, yaw)], norm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--timeout-sec", type=float, default=10.0)
    parser.add_argument("--topic", default="/task27/cube_poses")
    args = parser.parse_args()
    if args.samples < 1 or args.timeout_sec <= 0:
        parser.error("samples and timeout-sec must be positive")

    rclpy.init()
    capture = PoseCapture(args.topic)
    try:
        deadline = time.monotonic() + args.timeout_sec
        while len(capture.samples) < args.samples and time.monotonic() < deadline:
            rclpy.spin_once(capture, timeout_sec=min(0.2, max(0.0, deadline - time.monotonic())))
        if len(capture.samples) < args.samples:
            raise RuntimeError(
                f"Only {len(capture.samples)}/{args.samples} Cube_05 samples received"
            )
        pose = capture.samples[-1]
        rpy_deg, quaternion_norm = _orientation_degrees(pose)
        positions = [
            [sample.position.x, sample.position.y, sample.position.z]
            for sample in capture.samples
        ]
        mean_position = [sum(row[axis] for row in positions) / len(positions)
                         for axis in range(3)]
        position_spread_mm = max(
            math.dist(row, mean_position) * 1000.0 for row in positions
        )
        print(json.dumps({
            "topic": args.topic,
            "cube_index_0_based": 4,
            "samples": len(capture.samples),
            "last_position_m": positions[-1],
            "last_quaternion_xyzw": [pose.orientation.x, pose.orientation.y,
                                      pose.orientation.z, pose.orientation.w],
            "last_rpy_deg": rpy_deg,
            "quaternion_norm": quaternion_norm,
            "max_position_deviation_from_sample_mean_mm": position_spread_mm,
        }, ensure_ascii=False, sort_keys=True))
    finally:
        capture.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
