#!/usr/bin/env python3
"""[ENGINEERING] 原候选的名义 Cube/环境 AABB 检查，不启动任何仿真。

MoveIt robot/world 检查不检查 world/world；此文件补充当前零偏航 Cube
与桌面、三墙的几何检查。仅适用于本候选的轴对齐方盒，不是 PhysX
接触、连续扫掠或有偏航/变形物体的通用碰撞证明。不改变接触或 ACM。
"""
import argparse
import json
import math
from pathlib import Path

import yaml


def classify(center_a, size_a, center_b, size_b):
    overlaps = [
        min(a + sa / 2, b + sb / 2) - max(a - sa / 2, b - sb / 2)
        for a, sa, b, sb in zip(center_a, size_a, center_b, size_b)
    ]
    # 仅抑制双精度边界舍入误差，不增加物理容许穿透量。
    roundoff = 1e-12
    if all(value > roundoff for value in overlaps):
        relation = "VOLUME_OVERLAP"
    elif all(value >= -roundoff for value in overlaps):
        relation = "BOUNDARY_TOUCH"
    else:
        relation = "SEPARATED"
    return {
        "relation": relation,
        "axis_overlap_m": overlaps,
        "separation_m": math.sqrt(sum(max(0.0, -v) ** 2 for v in overlaps)),
        "volume_overlap": relation == "VOLUME_OVERLAP",
    }


def self_test():
    unit = [1.0] * 3
    origin = [0.0] * 3
    assert classify(origin, unit, [1.0, 0.0, 0.0], unit)["relation"] == "BOUNDARY_TOUCH"
    assert classify(origin, unit, [1.001, 0.0, 0.0], unit)["relation"] == "SEPARATED"
    assert classify(origin, unit, [0.999, 0.0, 0.0], unit)["relation"] == "VOLUME_OVERLAP"
    assert classify(origin, unit, [0.5, 2.0, 0.0], unit)["relation"] == "SEPARATED"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("dense_results", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    self_test()
    if args.output.exists():
        raise RuntimeError("Refusing to overwrite prior audit")
    with args.config.open() as stream:
        config = yaml.safe_load(stream)
    with args.dense_results.open() as stream:
        dense = json.load(stream)
    benchmark = config["benchmarks"]["B_constrained_insertion"]
    for key in ("start_orientation_xyzw", "target_orientation_xyzw"):
        if benchmark[key] != [0.0, 0.0, 0.0, 1.0]:
            raise ValueError("AABB audit only supports the unchanged identity orientation")
    if not dense or any(row["status"] != "PASS" for row in dense):
        raise ValueError("Audit expects a completed nominal dense sequence")
    carriage = config["carriage"]
    x0, x1 = carriage["interior_x_world_m"]
    y0, y1 = carriage["interior_y_world_m"]
    thickness = carriage["wall_thickness_m"]
    height = carriage["wall_height_m"]
    z = carriage["wall_top_world_z_m"] - height / 2
    obstacles = [
        ("table", config["table"]["center_world_m"], config["table"]["size_m"]),
        ("carriage_deep_wall", [x1 + thickness / 2, (y0 + y1) / 2, z],
         [thickness, y1 - y0 + 2 * thickness, height]),
        ("carriage_minus_y_wall", [(x0 + x1) / 2, y0 - thickness / 2, z],
         [x1 - x0 + 2 * thickness, thickness, height]),
        ("carriage_plus_y_wall", [(x0 + x1) / 2, y1 + thickness / 2, z],
         [x1 - x0 + 2 * thickness, thickness, height]),
    ]
    records = []
    for row in dense:
        for name, center, size in obstacles:
            records.append({
                "index": row["index"], "insertion_fraction": row["insertion_fraction"],
                "body1": "shared_cube", "body2": name,
                **classify(row["cube_center_world_m"], config["cube"]["size_m"], center, size),
            })
    failed = [record for record in records if record["volume_overlap"]]
    output = {
        "scope": "nominal_axis_aligned_cube_vs_environment_only",
        "status": "FAIL_VOLUME_OVERLAP" if failed else "PASS_NOMINAL_AABB_ONLY",
        "dense_states": len(dense), "pair_checks": len(records),
        "volumetric_overlaps": len(failed),
        "table_touch_states": sum(r["body2"] == "table" and r["relation"] == "BOUNDARY_TOUCH" for r in records),
        "deep_wall_touch_states": sum(r["body2"] == "carriage_deep_wall" and r["relation"] == "BOUNDARY_TOUCH" for r in records),
        "self_tests_passed": 4, "floating_point_roundoff_m": 1e-12,
        "physics_started": False, "acm_modified": False,
        "config": str(args.config), "input": str(args.dense_results), "records": records,
    }
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k: v for k, v in output.items() if k != "records"}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
