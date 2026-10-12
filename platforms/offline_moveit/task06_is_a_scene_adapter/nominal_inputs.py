"""来源一致的 V2 静态输入核验；不 import/执行旧 scene 或 controller。"""
import ast
import re
from pathlib import Path
import yaml

from .source_audit import audit, CONTROLLER, DESCRIPTION, SCENE, sha


def validate_world(scene, constants, launch, cpp, epsilon=1e-12):
    """从已验 hash 的源码重建原 BOX；scene 参数不能因候选结果改变。"""
    x0, x1 = constants["BOX_INTERIOR_X"]
    y0, y1 = constants["BOX_INTERIOR_Y"]
    t, h = constants["BOX_WALL_THICKNESS"], constants["BOX_WALL_HEIGHT"]
    z = constants["TABLE_TOP_Z"] + h/2
    expected = {
        "task26_table": (constants["TABLE_CENTER"], constants["TABLE_SIZE"]),
        "task26_box_wall_deep": ([x1+t/2, (y0+y1)/2, z], [t, y1-y0+2*t, h]),
        "task26_box_wall_minus_y": ([(x0+x1)/2, y0-t/2, z], [x1-x0+2*t, t, h]),
        "task26_box_wall_plus_y": ([(x0+x1)/2, y1+t/2, z], [x1-x0+2*t, t, h]),
        "task26_cube_2": (constants["SLOT_B"], [constants["CUBE_SIZE"]]*3),
    }
    # 保留旧 launch 已有的第二张嵌套表；只读取 AST literal，不启动 launch。
    values = {}
    for node in ast.walk(ast.parse(launch)):
        if isinstance(node, ast.Dict):
            pairs = {k.value: v for k, v in zip(node.keys, node.values)
                     if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            if "table_id" in pairs:
                values = {k: ast.literal_eval(v) for k, v in pairs.items()}
    if values.get("table_id") != "task24_table" or values.get("table_frame") != "world":
        raise ValueError("Pinned launch table identity/frame unavailable")
    expected[values["table_id"]] = (values["table_center"], values["table_size"])
    for identity in ("task26_table", "task26_box_wall_deep", "task26_box_wall_minus_y", "task26_box_wall_plus_y"):
        if f'"{identity}"' not in cpp:
            raise ValueError("Original controller world ID not confirmed: " + identity)
    if '"task26_cube_" + std::to_string' not in cpp:
        raise ValueError("Original Cube ID formula not confirmed")
    rows = scene["adapter_world_objects"]
    if len(rows) != len(expected) or {r["id"] for r in rows} != set(expected):
        raise ValueError("World IDs/count differ from declared source scene")
    comparison = []
    for row in rows:
        center, size = expected[row["id"]]
        if row["frame_id"] != "world" or row["quaternion_xyzw"] != [0., 0., 0., 1.]:
            raise ValueError("World frame/orientation differs")
        for actual, reference in ((row["center_world_m"], center), (row["size_m"], size)):
            if len(actual) != 3 or any(abs(a-b) > epsilon for a, b in zip(actual, reference)):
                raise ValueError("World shape differs: " + row["id"])
        comparison.append({"id": row["id"], "source_center_world_m": center,
                           "source_size_m": size, "input": row, "equal": True})
    return comparison


def nominal_audit(root, legacy, protocol):
    root, legacy = Path(root), Path(legacy)
    original = audit(root, legacy, protocol)  # 复用原来源/模型/抓取 hash 门禁。
    scene = yaml.safe_load((root/protocol["geometry_archive"]).read_text())
    cpp = (legacy/CONTROLLER).read_text()
    launch = (legacy/DESCRIPTION/"launch/moveit_dual_side_suction.launch.py").read_text()
    original["source_world_comparisons"] = validate_world(scene, original["constants"], launch, cpp,
                                                           protocol["static_message_equivalence_epsilon"])
    c, s = original["constants"], original["controller_scalars"]
    targets = {"start": [c["SLOT_A"][0], c["SLOT_A"][1], c["SLOT_A"][2]+s["kLiftHeight"]],
               "goal": [c["PRE_PUSH_X"], c["ROW_Y"][0], c["SLOT_A"][2]+s["kReleaseGapZ"]]}
    for name, target in targets.items():
        row = scene["nominal_endpoints"][name]
        if any(abs(a-b) > 1e-12 for a, b in zip(target, row["translation_m"])) or row["quaternion_xyzw"] != [0., 0., 0., 1.]:
            raise ValueError("Nominal held target mismatch: " + name)
    physical = root/protocol["foundation_physical_log"]
    lines = physical.read_text().splitlines()
    held = [dict(line_number=i+1, text=line) for i, line in enumerate(lines)
            if re.search(r"task26_r0_deep COMMON_(LIFT|SIDE_SHORT_PUSH) GT", line)
            and "left:CLOSED" in line and "right:CLOSED" in line]
    if not any("COMMON_LIFT" in r["text"] for r in held) or not any("COMMON_SIDE_SHORT_PUSH" in r["text"] for r in held):
        raise ValueError("Historical bilateral-held phase evidence missing")
    folder = physical.parent
    original["nominal_held_phase_evidence"] = {"source": str(physical.relative_to(root)),
        "sha256": sha(physical), "lines": held, "nominal_target_from_controller": targets,
        "qualification": "NOMINAL_DEFINITION_NOT_ACTUAL_14Q_OR_SCIENTIFIC_SYNCHRONIZED_STATE"}
    original["historical_q_inventory"] = {"files": sorted(p.name for p in folder.iterdir() if p.is_file()),
        "complete_held_endpoint_q_available": False,
        "exclusion": "HOME/OPEN snapshots and truncated single-arm commands are not held endpoints"}
    original["scene_input"] = scene
    return original
