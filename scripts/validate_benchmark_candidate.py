#!/usr/bin/env python3
"""Static geometry checks for the TASK01 draft; not an Isaac validation."""

import math
import sys
from pathlib import Path

import yaml


def near(actual, expected, label, atol=1e-9):
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=atol):
        raise ValueError(f"{label}: {actual} != {expected}")


def main(path: Path) -> int:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if config["status"] != "DRAFT":
        raise ValueError("Candidate validator only accepts DRAFT status")

    size = config["cube"]["size_m"]
    if len(size) != 3 or any(d <= 0 for d in size):
        raise ValueError("Cube size must have three positive dimensions")
    half = size[0] / 2.0
    table = config["table"]
    carriage = config["carriage"]
    a = config["benchmarks"]["A_tight_transport"]
    b = config["benchmarks"]["B_constrained_insertion"]
    y_min, y_max = carriage["interior_y_world_m"]
    x_min, x_max = carriage["interior_x_world_m"]

    near(table["center_world_m"][2] + table["size_m"][2] / 2, table["top_world_z_m"], "table top")
    near(table["top_world_z_m"] + half, config["cube"]["nominal_first_layer_center_world_z_m"], "cube support")
    near(table["top_world_z_m"] + carriage["wall_height_m"], carriage["wall_top_world_z_m"], "wall top")
    near(y_max - y_min, 0.606, "carriage width")
    near(a["target_cube_center_world_m"][0], b["start_cube_center_world_m"][0], "A/B handoff x")
    near(a["target_cube_center_world_m"][1], b["start_cube_center_world_m"][1], "A/B handoff y")
    near(a["target_cube_center_world_m"][2], b["start_cube_center_world_m"][2], "A/B handoff z")
    near(b["target_cube_center_world_m"][0] - b["start_cube_center_world_m"][0], b["commanded_cube_translation_world_m"][0], "insert travel")
    near(x_min - (b["start_cube_center_world_m"][0] + half), 0.060, "pre-push entrance gap")
    near(x_max - (b["target_cube_center_world_m"][0] + half), 0.0, "deep-wall flush")
    near(y_max - (carriage["final_cell_centers_world_y_m"][-1] + half), 0.0, "+Y wall flush")
    near((carriage["final_cell_centers_world_y_m"][0] - half) - y_min, 0.0, "-Y wall flush")

    for side, index in (("left", -1), ("right", 1)):
        tcp = config["grasp"][f"object_to_{side}_tcp"]
        near(tcp["translation_m"][1], index * (half + 0.001), f"{side} TCP side gap")
        near(sum(q * q for q in tcp["quaternion_xyzw"]), 1.0, f"{side} TCP quaternion")
    for y in b["neighboring_inner_cube_centers_world_y_m"]:
        near(abs(y) - size[1], 0.0015, "center side gap")

    fixture = b["fixture_preparation_cubes_01_to_04"]
    pre_push = fixture["nominal_pre_push_centers_world_m"]
    final_cells = fixture["final_cell_centers_world_m"]
    if len(fixture["sequence"]) != 4 or len(pre_push) != 4 or len(final_cells) != 4:
        raise ValueError("Fixture preparation must specify four cubes in order")
    for index, (start, goal) in enumerate(zip(pre_push, final_cells), start=1):
        near(start[0], b["start_cube_center_world_m"][0], f"cube {index} PRE_PUSH x")
        near(goal[0], b["target_cube_center_world_m"][0], f"cube {index} final x")
        near(start[2], b["start_cube_center_world_m"][2], f"cube {index} PRE_PUSH z")
        near(goal[2], b["target_cube_center_world_m"][2], f"cube {index} final z")
    near(final_cells[0][1], carriage["final_cell_centers_world_y_m"][-1], "positive outer cell")
    near(final_cells[1][1], carriage["final_cell_centers_world_y_m"][0], "negative outer cell")
    near(final_cells[2][1], carriage["final_cell_centers_world_y_m"][-2], "positive inner cell")
    near(final_cells[3][1], carriage["final_cell_centers_world_y_m"][1], "negative inner cell")
    if b["center_cube_05"]["contact_topology"] != "one_arm_suction_on_minus_x_face_other_arm_no_cube_contact":
        raise ValueError("Cube 05 must use single-arm rear-suction insertion")
    if b["side_support_policy"] != "none_for_cube_05":
        raise ValueError("Cube 05 cannot have a second-arm side constraint")

    pending = []
    def find_null(value, prefix=""):
        if isinstance(value, dict):
            for key, child in value.items():
                find_null(child, f"{prefix}.{key}" if prefix else key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                find_null(child, f"{prefix}[{index}]")
        elif value is None:
            pending.append(prefix)

    find_null(config)
    print("PASS: TASK01 draft geometry is internally consistent (analytic only).")
    print(f"PENDING: {len(pending)} unresolved fields; benchmark remains DRAFT.")
    for field in pending:
        print(f"  - {field}")
    return 0


if __name__ == "__main__":
    candidate = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "configs/benchmark/benchmark_v1.yaml"
    raise SystemExit(main(candidate))
