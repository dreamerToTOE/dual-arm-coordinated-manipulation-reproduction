"""[THIN_ADAPTER] 只读旧文件/快照；不导入或执行 Isaac scene、bridge、控制器。"""
import ast
import hashlib
import json
import math
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

from platforms.isaac_ros2.foundation.legacy_task26 import load_manifest, verify_legacy_assets

SCENE = "isaac/scripts/task26_truck_box_scene.py"
BRIDGE = "isaac/scripts/task26_truck_box_bridge.py"
CONTROLLER = "ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp"
DESCRIPTION = "ros_ws/src/fr3_dual_side_suction_description/"
JOINT_NAMES = [f"{side}_fr3_joint{i}" for side in ("left", "right") for i in range(1, 8)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_constants(text, names):
    """仅解释白名单常量表达式；不能执行任意旧脚本或 imports/calls。"""
    assignments = {n.targets[0].id: n.value for n in ast.parse(text).body
                   if isinstance(n, ast.Assign) and len(n.targets) == 1
                   and isinstance(n.targets[0], ast.Name)}
    known = {"TASK27_MODE": False}

    def value(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in known:
                known[node.id] = value(assignments[node.id])
            return known[node.id]
        if isinstance(node, (ast.Tuple, ast.List)):
            return [value(n) for n in node.elts]
        if isinstance(node, ast.Dict):
            return {value(k): value(v) for k, v in zip(node.keys, node.values)}
        if isinstance(node, ast.IfExp):
            return value(node.body if value(node.test) else node.orelse)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            return (-1 if isinstance(node.op, ast.USub) else 1) * value(node.operand)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and (
                node.value.id, node.attr) == ("math", "pi"):
            return math.pi
        if isinstance(node, ast.BinOp):
            a, b = value(node.left), value(node.right)
            for kind, operation in ((ast.Add, lambda: a+b), (ast.Sub, lambda: a-b),
                                    (ast.Mult, lambda: a*b), (ast.Div, lambda: a/b)):
                if isinstance(node.op, kind):
                    return operation()
        raise ValueError(f"Unapproved static expression: {ast.dump(node)}")
    return {name: value(ast.Name(id=name)) for name in names}


def xml_signature(text):
    """忽略注释、排版和属性顺序；保留全部模型数值/结构/URI。"""
    def signature(node):
        return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
                tuple(signature(child) for child in node))
    return signature(ET.fromstring(text))


def endpoint_gate(endpoints):
    # 禁止从原异步 HOME 快照或名义 pose 自动推导持件 14q。
    missing = [name for name in ("start", "goal") if endpoints.get(name) is None]
    if missing:
        return {"ready": False, "status": "INPUT_UNAVAILABLE", "missing": missing,
                "reason": "Actual shared-held START/PRE_PUSH 14q evidence is unconfirmed"}
    raise ValueError("Current audited protocol has no approved endpoint evidence; new input needs review")


def audit(root, legacy, protocol):
    root, legacy = Path(root), Path(legacy)
    manifest = load_manifest()
    verified = verify_legacy_assets(legacy, manifest)
    if (manifest["base_commit"], manifest["approved_runtime_commit"]) != (
            protocol["legacy_base_commit"], protocol["legacy_approved_commit"]):
        raise ValueError("Approved predecessor identity mismatch")
    paths = [SCENE, BRIDGE, CONTROLLER,
             DESCRIPTION+"urdf/dual_fr3_side_suction.urdf.xacro",
             DESCRIPTION+"urdf/dual_side_suction.xacro",
             DESCRIPTION+"srdf/dual_fr3_side_suction.srdf.xacro",
             DESCRIPTION+"launch/moveit_dual_side_suction.launch.py"]
    sources = {}
    for path in paths:
        pinned = subprocess.check_output(["git", "show", f'{protocol["legacy_approved_commit"]}:{path}'], cwd=legacy)
        if (legacy/path).read_bytes() != pinned:
            raise ValueError(f"Local file differs from approved commit: {path}")
        base = subprocess.check_output(["git", "show", f'{protocol["legacy_base_commit"]}:{path}'], cwd=legacy)
        if path != CONTROLLER and base != pinned:
            raise ValueError(f"Unapproved mature-asset change: {path}")
        sources[path] = {"sha256": sha(legacy/path), "base_sha256": hashlib.sha256(base).hexdigest(),
                         "same_as_631b1f": base == pinned}
    constants = source_constants((legacy/SCENE).read_text(), [
        "LEFT_BASE", "RIGHT_BASE", "TABLE_CENTER", "TABLE_SIZE", "TABLE_TOP_Z", "CUBE_SIZE",
        "CUBE_MASS", "SLOT_A", "SLOT_B", "BOX_INTERIOR_X", "BOX_INTERIOR_Y",
        "BOX_WALL_THICKNESS", "BOX_WALL_HEIGHT", "PRE_PUSH_X", "ROW_Y",
        "VERTICAL_DROP_Z", "LATERAL_STANDOFF_Y", "TCP_Y", "FR3_OFFICIAL_JOINT_LIMITS_RAD",
        "RAIL_TRAVEL", "BATCH_SIZE", "BATCH_COUNT"])
    archive = yaml.safe_load((root/protocol["geometry_archive"]).read_text())
    comparisons = [
        ("left_base", constants["LEFT_BASE"], archive["robots"]["left"]["base_at_rest_world_m"]),
        ("right_base", constants["RIGHT_BASE"], archive["robots"]["right"]["base_at_rest_world_m"]),
        ("table_center", constants["TABLE_CENTER"], archive["table"]["center_world_m"]),
        ("table_size", constants["TABLE_SIZE"], archive["table"]["size_m"]),
        ("cube_size", [constants["CUBE_SIZE"]]*3, archive["cube"]["size_m"]),
        ("cube_mass", constants["CUBE_MASS"], archive["cube"]["mass_kg"]),
        ("carriage_x", constants["BOX_INTERIOR_X"], archive["carriage"]["interior_x_world_m"]),
        ("carriage_y", constants["BOX_INTERIOR_Y"], archive["carriage"]["interior_y_world_m"]),
        ("wall_thickness", constants["BOX_WALL_THICKNESS"], archive["carriage"]["wall_thickness_m"]),
        ("wall_height", constants["BOX_WALL_HEIGHT"], archive["carriage"]["wall_height_m"]),
        ("wall_top", constants["TABLE_TOP_Z"]+constants["BOX_WALL_HEIGHT"], archive["carriage"]["wall_top_world_z_m"])]
    for name, actual, expected in comparisons:
        def flat(v):
            return [float(x) for x in v] if isinstance(v, (tuple, list)) else [float(v)]
        if len(flat(actual)) != len(flat(expected)) or any(abs(a-b) > 1e-12 for a, b in zip(flat(actual), flat(expected))):
            raise ValueError(f"Static scene/archive mismatch: {name}: {actual} != {expected}")
    model_checks = {}
    for kind, source in (("urdf", "urdf/dual_fr3_side_suction.urdf.xacro"),
                         ("srdf", "srdf/dual_fr3_side_suction.srdf.xacro")):
        expanded = subprocess.run(["xacro", str(legacy/DESCRIPTION/source)], capture_output=True,
                                  text=True, timeout=30, check=True)
        if xml_signature(expanded.stdout) != xml_signature((root/protocol[kind]).read_text()):
            raise ValueError(f"Expanded pinned model != existing TASK03 {kind} fixture")
        model_checks[kind] = {"xml_structure_and_all_numeric_fields_equal": True,
                              "fixture_sha256": sha(root/protocol[kind]),
                              "expanded_stdout_sha256": hashlib.sha256(expanded.stdout.encode()).hexdigest(),
                              "stderr": expanded.stderr}
    cpp = (legacy/CONTROLLER).read_text()
    # 仅提取明确的已知标量，不求 IK、不猜测未保存的关节值。
    scalar = {}
    for name in ("kSideContactCommandGap", "kSideContactCommandZOffset", "kLiftHeight",
                 "kPrePushOffsetX", "kReleaseGapZ"):
        match = re.search(rf"constexpr double {name}\s*=\s*([0-9.]+)\s*;", cpp)
        if not match:
            raise ValueError(f"Cannot attest unchanged controller scalar: {name}")
        scalar[name] = float(match.group(1))
    gap = scalar["kSideContactCommandGap"]
    side_pose = cpp[cpp.index("geometry_msgs::msg::Pose sidePose("):cpp.index("// 推入姿态：")]
    if not all(token in side_pose for token in (
            "constexpr double half_root = 0.7071067811865476;",
            "pose.orientation.x = half_root;", "pose.orientation.y = half_root;",
            "pose.orientation.y = -half_root;", "pose.orientation.z = 0.0;",
            "pose.orientation.w = 0.0;")):
        raise ValueError("Pinned sidePose orientation is not the audited fixed grasp convention")
    grasps = {side: {"translation_m": [0., sign*(constants["CUBE_SIZE"]/2.+gap), 0.],
                     "quaternion_xyzw": [math.sqrt(.5), -sign*math.sqrt(.5), 0., 0.]}
              for side, sign in (("left", -1), ("right", 1))}
    historical = archive["shared_grasp"]
    for side in ("left", "right"):
        original = historical[f"object_to_{side}_tcp_candidate"]
        for field in ("translation_m", "quaternion_xyzw"):
            if any(abs(a-b) > 1e-12 for a, b in zip(grasps[side][field], original[field])):
                raise ValueError(f"Fixed nominal grasp differs from pinned Task26: {side}/{field}")
    snapshots = {}
    for name in ("foundation_initial_snapshot", "foundation_final_snapshot"):
        envelope = json.loads((root/protocol[name]).read_text())
        data = json.loads(envelope["output"])
        snapshots[name] = {"path": protocol[name], "sha256": sha(root/protocol[name]),
                           "label": data["label"], "SG": data["SG"], "rails": data["rails"],
                           "usable_as_shared_held_endpoint": False,
                           "reason": "Both SG OPEN; HOME, not shared-held transport state"}
        if data["SG"] != {"left": False, "right": False}:
            raise ValueError("Historical snapshot interpretation changed; review required")
    return {"source_scenario": protocol["source_scenario"], "sources": sources,
            "legacy_asset_hashes": verified, "constants": constants, "controller_scalars": scalar,
            "geometry_comparisons": [{"field": n, "scene": a, "archive": e, "equal": True}
                                     for n, a, e in comparisons],
            "model_checks": model_checks, "nominal_object_to_tcp": grasps,
            "grasp_rotation_source": {"path": CONTROLLER, "function": "sidePose"},
            "joint_names": JOINT_NAMES, "snapshots": snapshots,
            "endpoint_gate": endpoint_gate(protocol["endpoints"]),
            "source_qualification": "PINNED_STATIC_DEFINITION_NOT_ACTUAL_ATTACHMENT_CALIBRATION",
            "planning_calls": 0, "ik_calls": 0, "execution_commands": 0}
