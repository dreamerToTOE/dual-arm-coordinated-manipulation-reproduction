"""[ENGINEERING] Exact OBB check of existing tool at the requested side pose.

Read existing xacro boxes, do not invent a shortened geometry or change ACM.
An intersecting tool box at the required pose blocks that pose independently
of FR3 IK. This is geometry evidence, not a full-path or PhysX run.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import numpy as np

from analyze_full_fixture import rotation_xyzw


def signed_xyz(text, side_sign):
    text = re.sub(r"\$\{side_sign\s*\*\s*([0-9.]+)\}",
                  lambda match: str(side_sign*float(match.group(1))), text)
    values = np.asarray([float(part) for part in text.split()])
    if values.shape != (3,) or not np.isfinite(values).all():
        raise ValueError("unexpected geometry expression")
    return values


def obb_intersection(a_center, a_rotation, a_half, b_center, b_rotation, b_half):
    axes = [a_rotation[:, i] for i in range(3)] + [b_rotation[:, i] for i in range(3)]
    axes += [np.cross(a_rotation[:, i], b_rotation[:, j]) for i in range(3) for j in range(3)]
    minimum = float("inf")
    displacement = np.asarray(b_center)-a_center
    for axis in axes:
        norm = np.linalg.norm(axis)
        if norm < 1e-9:
            continue
        axis = axis/norm
        radius_a = np.dot(np.abs(a_rotation.T@axis), a_half)
        radius_b = np.dot(np.abs(b_rotation.T@axis), b_half)
        overlap = radius_a+radius_b-abs(np.dot(displacement, axis))
        if overlap < 0:
            return False, float(overlap)
        minimum = min(minimum, overlap)
    return True, float(minimum)


def audit(xacro_path, physical_analysis, roll_sweep_step_deg=None):
    tree = ET.parse(xacro_path)
    side_sign = 1  # Cube04 -Y placement: right helper on its +Y face.
    joints = [element for element in tree.iter("joint")
              if element.attrib["name"].endswith("side_suction_tcp_joint")]
    if len(joints) != 1:
        raise ValueError("unexpected fixed TCP topology")
    tcp_offset = signed_xyz(joints[0].find("origin").attrib["xyz"], side_sign)
    tcp_origin_rpy = signed_xyz(joints[0].find("origin").attrib["rpy"], side_sign)
    if not np.allclose(tcp_origin_rpy[:2], 0):
        raise ValueError("TCP local roll/pitch changed")
    yaw = tcp_origin_rpy[2]
    local_tcp_rotation = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                                   [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
    target_tcp = np.array([1.100, -.1215+.060+.001, .260])
    root = 2**-.5
    tcp_rotation = rotation_xyzw([root, -root, 0, 0])  # existing sidePose(right)
    link_rotation = tcp_rotation@local_tcp_rotation.T
    link_origin = target_tcp-link_rotation@tcp_offset
    primitives, collisions = [], []
    for collision in tree.iter("collision"):
        box = collision.find("geometry/box")
        if box is None:
            continue
        origin = signed_xyz(collision.find("origin").attrib["xyz"], side_sign)
        rpy = signed_xyz(collision.find("origin").attrib["rpy"], side_sign)
        if not np.allclose(rpy, 0):
            raise ValueError("tool collision local rotation changed")
        size = np.asarray([float(value) for value in box.attrib["size"].split()])
        center = link_origin+link_rotation@origin
        primitive = {"name": collision.attrib["name"], "world_center_m": center.tolist(),
                     "size_m": size.tolist(), "world_rotation": link_rotation.tolist()}
        primitives.append(primitive)
        for neighbor in physical_analysis["final_geometry"][:3]:
            hit, overlap = obb_intersection(center, link_rotation, size/2,
                np.asarray(neighbor["position_m"]), rotation_xyzw(neighbor["quaternion_xyzw"]),
                np.array([.06, .06, .06]))
            if hit:
                collisions.append({"tool_primitive": collision.attrib["name"],
                    "neighbor": neighbor["prim_path"], "minimum_SAT_axis_overlap_mm": overlap*1000})
    roll_sweep = []
    if roll_sweep_step_deg is not None:
        # 只读候选扫描：保持面中心和杯面法向，只绕 TCP 局部 +X 自转。
        # 不改工具，不求解 IK，不把无 box 相交当作可执行轨迹。
        for angle in np.arange(0, 360, roll_sweep_step_deg):
            roll = np.radians(angle)
            local_roll = np.array([[1, 0, 0], [0, np.cos(roll), -np.sin(roll)],
                                   [0, np.sin(roll), np.cos(roll)]])
            rotation = tcp_rotation@local_roll@local_tcp_rotation.T
            origin_world = target_tcp-rotation@tcp_offset
            intersecting_boxes = []
            for collision in tree.iter("collision"):
                box = collision.find("geometry/box")
                if box is None:
                    continue
                center = origin_world+rotation@signed_xyz(collision.find("origin").attrib["xyz"], side_sign)
                half = np.array([float(value) for value in box.attrib["size"].split()])/2
                for neighbor in physical_analysis["final_geometry"][:3]:
                    hit, overlap = obb_intersection(center, rotation, half,
                        np.asarray(neighbor["position_m"]), rotation_xyzw(neighbor["quaternion_xyzw"]),
                        np.array([.06, .06, .06]))
                    if hit:
                        intersecting_boxes.append({"tool_primitive": collision.attrib["name"],
                            "neighbor": neighbor["prim_path"], "minimum_SAT_axis_overlap_mm": overlap*1000})
            roll_sweep.append({"tcp_roll_deg": float(angle), "collisions": intersecting_boxes})
    return {"status": "REQUIRED_SIDE_POSE_INTERFERES" if collisions else "NO_BOX_INTERFERENCE_FOUND",
        "source_xacro": str(xacro_path), "source_sha256": hashlib.sha256(xacro_path.read_bytes()).hexdigest(),
        "requested_stage": "Cube04 +Y-face-centered right side helper after Cube01/02/03 seated",
        "tcp_world_m": target_tcp.tolist(), "tcp_quaternion_xyzw": [root, -root, 0, 0],
        "link8_world_m": link_origin.tolist(), "tool_box_primitives": primitives,
        "collisions": collisions,
        "roll_sweep_fixed_face_center_and_normal": roll_sweep,
        "roll_sweep_clear_box_pose_count": sum(not entry["collisions"] for entry in roll_sweep),
        "boundaries": ["Required face-center/normal; optional discrete TCP roll sweep is not an exhaustive continuous contact/IK search",
                       "Exact OBB box intersections, not reported PhysX penetration depth",
                       "Cup cylinders, arm reachability and arm/wall collisions not needed to establish these box intersections",
                       "No physics, geometry, ACM or benchmark gate modified",
                       "This diagnostic is not a fixture-protocol PASS; changing tool/contact/order requires explicit review"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xacro", type=Path, required=True)
    parser.add_argument("--physical-analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--roll-sweep-step-deg", type=float, default=None)
    args = parser.parse_args()
    if args.roll_sweep_step_deg is not None and not 0 < args.roll_sweep_step_deg <= 360:
        parser.error("roll sweep step must be finite and in (0, 360]")
    result = audit(args.xacro, json.loads(args.physical_analysis.read_text()), args.roll_sweep_step_deg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
