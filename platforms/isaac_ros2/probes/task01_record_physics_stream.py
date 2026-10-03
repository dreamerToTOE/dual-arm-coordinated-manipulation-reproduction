"""Record the five-Cube physics stream during the legacy insertion experiment.

Read-only measurement checks; the controller's separate log determines physical
task success. This recorder does not invent benchmark acceptance thresholds.
"""

import argparse
import bisect
import json
import math
from pathlib import Path
import time

import rclpy
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rosgraph_msgs.msg import Clock
from std_msgs.msg import String


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-sec", type=float, default=250.0)
    parser.add_argument("--startup-timeout-sec", type=float, default=60.0)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.duration_sec <= 0 or args.startup_timeout_sec <= 0:
        parser.error("duration-sec and startup-timeout-sec must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rclpy.init()
    node = rclpy.create_node("task01_physics_stream_recorder")
    stamps, clocks, steps, norms, cube05_positions, errors = [], [], [], [], [], []
    first_received = None
    final = None
    expected_paths = [f"/World/Task27/Supply/Cube_{index:02d}" for index in range(1, 6)]
    with (args.output_dir / "physics_snapshots.jsonl").open("w", encoding="utf-8") as raw:
        def on_snapshot(message):
            nonlocal first_received, final
            try:
                sample = json.loads(message.data)
                paths = [body["prim_path"] for body in sample["bodies"]]
            except (ValueError, KeyError, TypeError) as error:
                errors.append(f"Invalid physics JSON: {error}")
                return
            if paths != expected_paths or sample.get("frame_id") != "world":
                errors.append("Invalid five-Cube/frame contract")
                return
            if first_received is None:
                first_received = time.monotonic()
            raw.write(message.data + "\n")
            stamps.append(sample["stamp_ns"])
            steps.append(sample["physics_step"])
            for body in sample["bodies"]:
                norms.append(abs(math.sqrt(sum(v * v for v in body["quaternion_xyzw"])) - 1))
                if not all(math.isfinite(v) for key in ("position_m", "quaternion_xyzw",
                           "linear_velocity_m_s", "angular_velocity_rad_s") for v in body[key]):
                    errors.append("Nonfinite physics measurement")
            cube05_positions.append(sample["bodies"][4]["position_m"])
            final = sample

        node.create_subscription(String, "/task01/physics/cube_poses/snapshot", on_snapshot, 200)
        node.create_subscription(Clock, "/clock", lambda msg: clocks.append(
            msg.clock.sec * 1_000_000_000 + msg.clock.nanosec),
            QoSProfile(depth=200, reliability=ReliabilityPolicy.BEST_EFFORT))
        print("[TASK01 physics recorder] READY: no command publishers", flush=True)
        started = time.monotonic()
        try:
            while rclpy.ok():
                rclpy.spin_once(node, timeout_sec=0.05)
                now = time.monotonic()
                if first_received is None and now - started >= args.startup_timeout_sec:
                    errors.append("Physics snapshot startup timeout")
                    break
                if first_received is not None and now - first_received >= args.duration_sec:
                    break
            clock_ordered = sorted(set(clocks))
            nearest = []
            for stamp in stamps:
                index = bisect.bisect_left(clock_ordered, stamp)
                candidates = clock_ordered[max(0, index - 1):index + 1]
                if candidates:
                    nearest.append(min(abs(stamp - value) for value in candidates) / 1e9)
            summary = {
                "samples": len(stamps), "clock_samples": len(clocks), "errors": errors,
                "stamps_increasing": all(b > a for a, b in zip(stamps, stamps[1:])),
                "steps_increasing": all(b > a for a, b in zip(steps, steps[1:])),
                "missing_physics_steps": sum(max(0, b - a - 1) for a, b in zip(steps, steps[1:])),
                "max_step_gap": max((b - a for a, b in zip(steps, steps[1:])), default=None),
                "max_quaternion_norm_error": max(norms, default=None),
                "max_nearest_clock_stamp_difference_s": max(nearest, default=None),
                "cube05_x_range_m": [min(p[0] for p in cube05_positions),
                                      max(p[0] for p in cube05_positions)] if cube05_positions else None,
                "final_snapshot": final,
            }
            summary["status"] = "PASS" if (not errors and len(stamps) >= 120 and
                summary["stamps_increasing"] and summary["steps_increasing"] and
                clocks and max(norms) <= 1e-12) else "FAIL"
            (args.output_dir / "recorder_summary.json").write_text(
                json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            print("[TASK01 physics recorder] " + json.dumps(summary, sort_keys=True), flush=True)
            if summary["status"] != "PASS":
                raise RuntimeError("Physics recording checks failed")
        finally:
            node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()


if __name__ == "__main__":
    main()
