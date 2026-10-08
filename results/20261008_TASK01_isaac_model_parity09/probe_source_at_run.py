"""[ENGINEERING] Visible, bounded TASK01 nominal cooked-shape parity replay.

No controller, ROS graph, suction actuation, five-Cube scene, integration, or
physics-parameter change. Static observations are indexed geometry snapshots,
not post-physics-step scientific measurements. Unexpected overlap stops at once.
"""

import argparse
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import time
import traceback
import xml.etree.ElementTree as ET


SOURCE_SHA = "43aa7c2eb6a5667da5e94eaaef347229fe6178ec58d6a10d12dddf14ba2aa9e7"
ASSET_SHA = "3feceb47747b49f908f9719299132deb9759f2d5edb390d14f0f3ed62c63255f"
TOOL_CONSTANTS = (
    "VERTICAL_DROP_Z", "LATERAL_STANDOFF_Y", "VERTICAL_SUPPORT_WIDTH",
    "LATERAL_SUPPORT_WIDTH", "MANIFOLD_Y", "MANIFOLD_X_SIZE",
    "MANIFOLD_Y_SIZE", "MANIFOLD_Z_SIZE", "ARRAY_X_OFFSET", "ARRAY_Z_OFFSET",
    "CUP_RADIUS", "CUP_LENGTH", "CUP_CENTER_Y", "TCP_Y",
)
SOURCE_FUNCTIONS = (
    "_remove", "_disable_visual_and_collision", "_add_fr3",
    "_apply_official_joint_limits", "_box", "_build_tool",
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def original_constructor_namespace(source, stage, asset):
    """Extract existing constructors only; never execute legacy module bottom."""
    from pxr import Gf, PhysxSchema, Usd, UsdGeom, UsdPhysics
    tree = ast.parse(source.read_text(encoding="utf-8"))
    names = set(TOOL_CONSTANTS) | {"FR3_OFFICIAL_JOINT_LIMITS_RAD", "CUBE_MASS"}
    selected = []
    for item in tree.body:
        if isinstance(item, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id in names for target in item.targets):
            selected.append(item)
        elif isinstance(item, ast.FunctionDef) and item.name in SOURCE_FUNCTIONS:
            selected.append(item)
    if {item.name for item in selected if isinstance(item, ast.FunctionDef)} != set(SOURCE_FUNCTIONS):
        raise RuntimeError("Missing original, allowlisted scene constructors")
    namespace = {"stage": stage, "math": math, "Gf": Gf, "PhysxSchema": PhysxSchema,
                 "Usd": Usd, "UsdGeom": UsdGeom, "UsdPhysics": UsdPhysics,
                 "LEFT_ROOT": "/World/left_fr3", "RIGHT_ROOT": "/World/right_fr3",
                 "_MATERIAL": None,
                 # Geometry-only adapter avoids binding the old incorrectly effective 0.90/0.75 material.
                 # Actual physics material is measured below, never assumed from this no-op.
                 "_bind": lambda prim, material: None, "_asset_url": lambda: str(asset)}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(source), "exec"), namespace)
    return namespace


def model_name(path):
    if path == "/World/Task01/Cube":
        return "shared_cube"
    environment = {"/World/Table": "table", "/World/Task01/Carriage/WallDeep": "carriage_deep_wall",
                   "/World/Task01/Carriage/WallMinusY": "carriage_minus_y_wall",
                   "/World/Task01/Carriage/WallPlusY": "carriage_plus_y_wall"}
    if path in environment:
        return environment[path]
    parts = path.split("/")
    if len(parts) >= 5 and parts[2] in ("left_fr3", "right_fr3"):
        side = parts[2].split("_")[0]
        if "side_suction_tool" in parts:
            return f"{side}_fr3_side_suction"
        if parts[3].startswith("fr3_link"):
            return side + "_" + parts[3]
        return side + "_" + parts[3]
    raise RuntimeError("Unmapped original enabled collider: " + path)


def quat_angle(a, b):
    if len(a) != 4 or len(b) != 4 or not all(math.isfinite(float(v)) for v in list(a) + list(b)):
        raise RuntimeError("Non-finite or malformed quaternion readback")
    dot = abs(sum(float(x) * float(y) for x, y in zip(a, b)))
    na = math.sqrt(sum(float(x)**2 for x in a))
    nb = math.sqrt(sum(float(x)**2 for x in b))
    if na < 1e-12 or nb < 1e-12:
        raise RuntimeError("Zero-length quaternion readback")
    return 2 * math.acos(min(1., dot / (na * nb)))


def matrix_pose(matrix):
    q = matrix.ExtractRotationQuat()
    return list(map(float, matrix.ExtractTranslation())) + list(map(float, q.GetImaginary())) + [float(q.GetReal())]


def transform_matrix(pose, Gf):
    if len(pose) != 7 or not all(math.isfinite(float(v)) for v in pose):
        raise RuntimeError("Non-finite or malformed rigid-body pose")
    matrix = Gf.Matrix4d(1.)
    matrix.SetRotate(Gf.Quatd(float(pose[6]), Gf.Vec3d(*map(float, pose[3:6]))))
    matrix.SetTranslateOnly(Gf.Vec3d(*map(float, pose[:3])))
    return matrix


def pure_rigid_matrix(matrix, Gf):
    """Remove owner scale only from frame arithmetic; never edit USD or physics geometry."""
    pose = matrix_pose(matrix.RemoveScaleShear())
    norm = math.sqrt(sum(float(v)**2 for v in pose[3:]))
    if not math.isfinite(norm) or norm < 1e-12:
        raise RuntimeError("Invalid scale-free original rigid-body quaternion")
    pose[3:] = [float(v) / norm for v in pose[3:]]
    return transform_matrix(pose, Gf)


def native_query_hits(call, known_paths, description):
    """Never throw through a C++ callback; reject callback/count errors afterwards."""
    hits, callback_errors = [], []
    def report(hit):
        try:
            path, owner = str(hit.collision), str(hit.rigid_body)
            hits.append({"collision": path, "rigid_body": owner})
            if path not in known_paths:
                callback_errors.append("Unmapped native collider: " + path)
        except Exception as error:
            callback_errors.append(repr(error))
        return True
    count = call(report)
    result = {"query": description, "reported_hit_count": int(count),
              "callback_count": len(hits), "hits": hits, "callback_errors": callback_errors}
    if not math.isfinite(float(count)) or int(count) != count or count < 0 or count != len(hits):
        result["error"] = "Invalid native query count or callback/count mismatch"
    if callback_errors:
        result["error"] = "Native query callback or collider mapping failed"
    return result


def transformed_probe_geometry(prim, cooked_shape, matrix, np, Gf, UsdGeom):
    """Actual cooked-convex interior point and conservative world AABB; no authored hull."""
    if prim.IsA(UsdGeom.Mesh):
        if cooked_shape is None or len(cooked_shape["convexes"]) != 1:
            raise RuntimeError("Only one original cooked convexHull can be queried: " + str(prim.GetPath()))
        vertices = np.asarray(cooked_shape["convexes"][0]["vertices"], dtype=float)
        if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) < 4 or not np.all(np.isfinite(vertices)):
            raise RuntimeError("Malformed actual cooked convex vertices")
        center = vertices.mean(axis=0)
        if np.linalg.matrix_rank(vertices - center) != 3:
            raise RuntimeError("Actual cooked convex has no full-dimensional interior point")
        corners = vertices
    else:
        center = np.zeros(3, dtype=float)
        if prim.IsA(UsdGeom.Cube):
            half = np.full(3, float(UsdGeom.Cube(prim).GetSizeAttr().Get()) / 2.)
        elif prim.IsA(UsdGeom.Cylinder):
            cylinder = UsdGeom.Cylinder(prim)
            half = np.full(3, float(cylinder.GetRadiusAttr().Get()))
            axis = str(cylinder.GetAxisAttr().Get()).upper()
            if axis not in ("X", "Y", "Z"):
                raise RuntimeError("Unrecognized original cylinder axis")
            half["XYZ".index(axis)] = float(cylinder.GetHeightAttr().Get()) / 2.
        else:
            raise RuntimeError("Original primitive has no validated interior-point guard: " + str(prim.GetPath()))
        if not np.all(np.isfinite(half)) or np.min(half) <= 0:
            raise RuntimeError("Invalid original primitive dimensions")
        corners = np.asarray([[sx*half[0], sy*half[1], sz*half[2]]
                              for sx in (-1., 1.) for sy in (-1., 1.) for sz in (-1., 1.)])
    point = np.asarray(matrix.Transform(Gf.Vec3d(*map(float, center))), dtype=float)
    world_vertices = np.asarray([matrix.Transform(Gf.Vec3d(*map(float, v))) for v in corners], dtype=float)
    if not np.all(np.isfinite(point)) or not np.all(np.isfinite(world_vertices)):
        raise RuntimeError("Non-finite actual cooked/primitive world probe geometry")
    return point, world_vertices.min(axis=0), world_vertices.max(axis=0)


def sphere_proven_outside_aabb(point, lower, upper, radius):
    """A conservative whole-shape proof: sphere separated along at least one world axis."""
    return any(float(point[k]) + radius < float(lower[k]) - 1e-6 or
               float(point[k]) - radius > float(upper[k]) + 1e-6 for k in range(3))


def owning_body(prim, UsdPhysics):
    while prim and prim.IsValid():
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            return prim
        prim = prim.GetParent()
    return None


def static_render_update(app, timeline, settings, physics_steps):
    """Official SimulationContext.render dispatch gate; no physics-parameter edit.

    PAUSED标签不能证明queued Play事件不会积分；刷新期间用官方
    /app/player/playSimulations=False，finally精确还原，实际step事件仍须0。
    """
    path = "/app/player/playSimulations"
    original = settings.get(path)
    if not isinstance(original, bool):
        raise RuntimeError("Missing/invalid original render-only dispatcher setting")
    if timeline.is_playing() or physics_steps:
        raise RuntimeError("Static render requires paused timeline and zero physics steps")
    before_time = float(timeline.get_current_time())
    if not math.isfinite(before_time):
        raise RuntimeError("Static render requires a finite timeline time before update")
    settings.set_bool(path, False)
    try:
        app.update()
    finally:
        settings.set_bool(path, original)
    after_time = float(timeline.get_current_time())
    if physics_steps or timeline.is_playing() or not math.isfinite(after_time) or after_time != before_time:
        raise RuntimeError("Official render-only dispatch advanced physics/timeline")


def static_subsystem_refresh(simulation_interface, stage_update_interface, timeline, physics_steps):
    """Process original buffered changes with physics update explicitly disabled.

    官方 IPhysxStageUpdate.on_update(..., enable_update=False) 仍更新其他
    子系统，不进行 physics update。它不承诺刷新查询树，所以每形状实际
    正/负命中门禁仍不可省略；不能用接口调用成功冒充模型一致性。
    """
    before = float(timeline.get_current_time())
    if physics_steps or timeline.is_playing() or not math.isfinite(before):
        raise RuntimeError("Static subsystem refresh requires zero steps and a finite paused clock")
    simulation_interface.flush_changes()
    stage_update_interface.on_update(before, 0.0, False)
    after = float(timeline.get_current_time())
    if physics_steps or timeline.is_playing() or not math.isfinite(after) or after != before:
        raise RuntimeError("Disabled-physics subsystem refresh advanced physics/timeline")


def rebuild_original_static_handles(physx, tensors, sim, settings, timeline, physics_steps,
                                    original_digest, geometry_digest):
    """Reparse unchanged original USD at the verified body-pose state, no step.

    原查询树未随 tensor teleport 更新时，重新解析原场景，而不是改碰撞模型。
    release 只释放原生对象；严禁 reset_simulation（会回滚 USD 初态）。
    新 view 必须先读出原14q并与目标核验，不能用 setter 修补加载误差。
    不增加 JointStateAPI、状态属性、shape、padding、过滤规则或 ACM。
    """
    clock = float(timeline.get_current_time())
    def guard():
        if (physics_steps or timeline.is_playing() or
                not math.isfinite(float(timeline.get_current_time())) or
                float(timeline.get_current_time()) != clock or
                geometry_digest() != original_digest):
            raise RuntimeError("Original static-handle rebuild changed model or advanced physics/time")
    guard()
    path = "/app/player/playSimulations"
    original_dispatch = settings.get(path)
    if not isinstance(original_dispatch, bool):
        raise RuntimeError("Original dispatcher bool missing before static-handle rebuild")
    settings.set_bool(path, False)
    try:
        sim.invalidate()
        physx.release_physics_objects()
        guard()
        physx.force_load_physics_from_usd()
        physx.start_simulation()
        guard()
        result = tensors.create_simulation_view("numpy")
        result.set_subspace_roots("/")
        arts = {side: result.create_articulation_view(f"/World/{side}_fr3") for side in ("left", "right")}
        cube = result.create_rigid_body_view("/World/Task01/Cube")
        for name, view in list(arts.items()) + [("Cube", cube)]:
            if view.count != 1 or not view.check():
                raise RuntimeError("Original reloaded handle unavailable: " + name)
        if int(result.device_ordinal) != -1:
            raise RuntimeError("Original static CPU backend changed during handle rebuild")
        guard()
        return result, arts, cube
    finally:
        settings.set_bool(path, original_dispatch)


def original_geometry_fingerprint(stage, enabled, body_paths, UsdPhysics, UsdGeom, return_records=False):
    """Exclude body pose output fields; preserve scale, shapes and physical settings.

    PhysX may materialize an orient state-output op on a Cube originally T/S.
    Pose op names/order are audited separately and stacks strictly validated;
    they are not geometry dimensions. No adapter adds/reorders any ops.
    """
    paths = set(enabled) | set(body_paths)
    for p in stage.Traverse():
        if (p.IsA(UsdPhysics.Joint) or p.IsA(UsdPhysics.Scene) or p.HasAPI(UsdPhysics.CollisionAPI) or
                p.HasAPI(UsdPhysics.MassAPI) or p.HasAPI(UsdPhysics.MaterialAPI) or
                str(p.GetName()) == "side_suction_tcp"):
            paths.add(str(p.GetPath()))
    for path in list(paths):
        parent = stage.GetPrimAtPath(path).GetParent()
        while parent and not parent.IsPseudoRoot():
            paths.add(str(parent.GetPath()))
            parent = parent.GetParent()
    records = []
    for path in sorted(paths):
        prim = stage.GetPrimAtPath(path)
        pose_names = set()
        if path in body_paths:
            pose_names = {str(op.GetOpName()) for op in UsdGeom.Xformable(prim).GetOrderedXformOps()
                          if op.GetOpType() in (UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.TypeOrient)}
            pose_names.add("xformOpOrder")
        # SDK state output is not a physical PARAMETER. Its actual evolution is
        # guarded by zero-step callbacks and native/q invariance, not mislabelled
        # as a changed mesh/material. Original limits/drives/mass/friction stay hashed.
        state_names = {"physics:velocity", "physics:angularVelocity"} if path in body_paths else set()
        if prim.IsA(UsdPhysics.Joint):
            state_names.update(str(a.GetName()) for a in prim.GetAttributes()
                               if str(a.GetName()).startswith("state:") and
                               str(a.GetName()).endswith((":position", ":velocity")))
        attrs = {str(a.GetName()): {"value": str(a.Get()), "time_samples": a.GetTimeSamples()}
                 for a in prim.GetAttributes() if str(a.GetName()) not in pose_names | state_names}
        records.append({"path": path, "type": str(prim.GetTypeName()),
                        "schemas": list(prim.GetAppliedSchemas()), "attributes": attrs,
                        "relationships": {str(r.GetName()): list(map(str, r.GetTargets()))
                                          for r in prim.GetRelationships()}})
    digest = hashlib.sha256(json.dumps(records, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return (digest, records) if return_records else digest


def body_output_op_audit(stage, body_paths, UsdGeom):
    return {path: {"reset_stack": UsdGeom.Xformable(stage.GetPrimAtPath(path)).GetResetXformStack(),
                   "ordered_ops": [{"name": str(op.GetOpName()), "type": str(op.GetOpType()),
                       "precision": str(op.GetPrecision()), "value": str(op.Get()),
                       "time_samples": op.GetAttr().GetTimeSamples(), "inverse": op.IsInverseOp()}
                       for op in UsdGeom.Xformable(stage.GetPrimAtPath(path)).GetOrderedXformOps()]}
            for path in body_paths}


def mirror_existing_body_pose_ops(stage, body_matrices, Gf, UsdGeom, np):
    """Static replay state output only: existing pose ops, never new/reordered ops.

    原暂停状态的 update_transformations 可能不输出 tensor teleport。
    仅将已核验的 native/tensor SE3 写回原 body 的现存位姿 ops；必须再验
    原生 actor/14q 未变、原几何 hash 未变及查询真正更新，不能凭写 USD 算通过。
    """
    changes = []
    for path in sorted(body_matrices, key=lambda p: (p.count("/"), p)):
        prim = stage.GetPrimAtPath(path)
        xform = UsdGeom.Xformable(prim)
        ops = xform.GetOrderedXformOps()
        if xform.GetResetXformStack() or any(op.IsInverseOp() for op in ops):
            raise RuntimeError("Unsupported original body transform stack: " + path)
        translates = [op for op in ops if op.GetOpType() == UsdGeom.XformOp.TypeTranslate]
        orients = [op for op in ops if op.GetOpType() == UsdGeom.XformOp.TypeOrient]
        allowed_stacks = ((UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.TypeOrient, UsdGeom.XformOp.TypeScale),
                          (UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.TypeScale))
        if (len(translates) != 1 or len(orients) > 1 or
                tuple(op.GetOpType() for op in ops) not in allowed_stacks or
                any(op.GetOpType() not in (UsdGeom.XformOp.TypeTranslate, UsdGeom.XformOp.TypeOrient,
                                          UsdGeom.XformOp.TypeScale) for op in ops) or
                any(op.GetAttr().GetTimeSamples() for op in ops)):
            raise RuntimeError("Refusing to change/reorder original body pose stack: " + path)
        parent = prim.GetParent()
        parent_world = UsdGeom.Xformable(parent).ComputeLocalToWorldTransform(0.)
        if np.max(np.abs(np.asarray(parent_world) - np.asarray(pure_rigid_matrix(parent_world, Gf)))) > 1e-7:
            raise RuntimeError("Scaled original body parent is unsupported: " + path)
        local_rigid = body_matrices[path] * parent_world.GetInverse()
        q = local_rigid.ExtractRotationQuat()
        if not orients and quat_angle(list(map(float, q.GetImaginary())) + [float(q.GetReal())], [0.,0.,0.,1.]) > 1e-6:
            raise RuntimeError("Original body has no orient op; do not add one: " + path)
        # Use the precision of the ORIGINAL/current SDK output attribute, not a
        # new attribute or a hard-coded double; native Cube output can be Quatf.
        translation = local_rigid.ExtractTranslation()
        translates[0].Set(type(translates[0].Get())(*map(float, translation)))
        if orients:
            original_q = orients[0].Get()
            orients[0].Set(type(original_q)(float(q.GetReal()),
                type(original_q.GetImaginary())(*map(float, q.GetImaginary()))))
        changes.append({"body_path": path, "existing_pose_ops_written":
                        [str(op.GetOpName()) for op in translates + orients]})
    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path,
                        default=Path("results/20261007_TASK01_full_single_cube_geometry01"))
    parser.add_argument("--config", type=Path, default=None,
                        help="Optional exact snapshot path; default is input-dir/config_at_run.yaml, never mutable working YAML")
    parser.add_argument("--hold-for-inspection-sec", type=float, default=0.)
    args = parser.parse_args()
    if not os.environ.get("DISPLAY"):
        parser.error("Visible DISPLAY is required; no headless fallback")
    if args.hold_for_inspection_sec < 0 or args.hold_for_inspection_sec > 60:
        parser.error("Bounded inspection hold must be in [0,60] seconds")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[3]
    runtime = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing")
    source = runtime / "isaac/scripts/task26_truck_box_scene.py"
    asset = root / "results/20261006_TASK01_held_fixture_diagnostic02/raw/fr3_official.usd"
    srdf = root / "results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf"
    if sha(source) != SOURCE_SHA or sha(asset) != ASSET_SHA:
        raise RuntimeError("Original scene/asset hash changed; do not substitute geometry")
    import yaml
    config_path = args.config or args.input_dir / "config_at_run.yaml"
    if sha(config_path) != sha(args.input_dir / "config_at_run.yaml"):
        raise RuntimeError("Parity configuration must be the exact FCL-run snapshot")
    config = yaml.safe_load(config_path.read_text())
    states = json.loads((args.input_dir / "state_records.json").read_text())
    summary = json.loads((args.input_dir / "full_chain_results.json").read_text())
    if (config["schema_version"] != 2 or len(states) != 293 or
            summary["segments"]["A"]["status"] != "PASS_SAMPLED_SEGMENT" or
            summary["segments"]["B"]["status"] != "PASS_SAMPLED_SEGMENT" or
            any(row["status"] != "PASS_DISCRETE_GEOMETRY" or row["fcl"] != "PASS" for row in states)):
        raise RuntimeError("Only the complete approved A+B sampled geometry chain may be replayed")
    original_acm = {tuple(sorted((entry.get("link1"), entry.get("link2")))): entry.get("reason")
                    for entry in ET.parse(srdf).getroot().findall("disable_collisions")}
    write_json(args.output_dir / "inputs.json", {
        "scope": "single_cube_core_benchmark", "classification": "ENGINEERING",
        "time_contract": "GEOMETRY_STATIC_REPLAY; state_index only; no simulation measurement timestamp",
        "source": str(source), "source_sha256": sha(source), "asset": str(asset),
        "asset_sha256": sha(asset), "config_path":str(config_path), "config_sha256": sha(config_path), "srdf_sha256": sha(srdf),
        "probe_source_sha256":sha(__file__),"argv":__import__("sys").argv,
        "states_sha256": sha(args.input_dir / "state_records.json"), "expected_records": len(states),
        "robot_controller_started": False, "ROS_publishers": 0, "suction_commands": 0,
        "physics_integration_requested": False, "physics_parameters_changed": False,
        "old_material_bound": False})
    from isaacsim import SimulationApp
    app = SimulationApp({"headless": False, "width": 1280, "height": 960,
                         "multi_gpu": False, "sync_loads": False, "fast_shutdown": True,
                         "extra_args": ["--enable", "isaacsim.code_editor.vscode",
                            "--/exts/isaacsim.code_editor.vscode/host=127.0.0.1",
                            "--/exts/isaacsim.code_editor.vscode/port=8226",
                            "--/exts/isaacsim.code_editor.vscode/carb_logs=false"]})
    stopping = False
    def stop(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        import numpy as np
        import carb.settings
        import omni.kit.app
        import omni.physx
        import omni.physics.tensors as tensors
        import omni.timeline
        import omni.usd
        from pxr import Gf, PhysxSchema, PhysicsSchemaTools, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics
        from isaacsim.core.utils.viewports import set_camera_view
        from omni.kit.viewport.utility import capture_viewport_to_file, get_active_viewport
        timeline = omni.timeline.get_timeline_interface()
        physx = omni.physx.get_physx_interface()
        physics_steps = []
        physics_step_subscription = physx.subscribe_physics_step_events(
            lambda dt: physics_steps.append(float(dt)))
        static_timeline_time = float(timeline.get_current_time())
        output_settings_paths = ("/physics/updateToUsd", "/physics/updateVelocitiesToUsd",
            "/physics/updateParticlesToUsd", "/physics/updateForceSensorsToUsd",
            "/physics/fabricEnabled", "/physics/fabricUpdateTransformations")
        settings = carb.settings.get_settings()
        original_output_settings = {path: settings.get(path) for path in output_settings_paths}
        fabric_enabled = omni.kit.app.get_app().get_extension_manager().is_extension_enabled("omni.physx.fabric")
        fabric_interface = None
        if fabric_enabled:
            from omni.physxfabric import get_physx_fabric_interface
            fabric_interface = get_physx_fabric_interface()
        write_json(args.output_dir / "output_sync_contract.json", {
            "original_settings": original_output_settings, "existing_fabric_extension_enabled": fabric_enabled,
            "no_output_settings_or_physics_parameters_changed": True,
            "temporary_render_dispatch_gate": "/app/player/playSimulations=False during refresh/load; exact original bool restored; official SimulationContext.render pattern",
            "official_api_order": "update_transformations; update_transformations_scene; existing Fabric force_update/save_to_usd",
            "guarded_fallback": "mirror already verified native SE3 to existing body translate/orient ops only",
            "fallback_requires": "all q/native actor/Cube unchanged; immutable shape/scale/physics hash unchanged; moving queries verified",
            "physics_step_count_must_remain": 0})
        render_only = lambda: static_render_update(app, timeline, settings, physics_steps)
        timeline.stop()
        static_timeline_time = float(timeline.get_current_time())
        omni.usd.get_context().new_stage()
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(stage, 1.)
        world = UsdGeom.Xform.Define(stage, "/World")
        stage.SetDefaultPrim(world.GetPrim())
        scene = UsdPhysics.Scene.Define(stage, "/physicsScene")
        scene.GetGravityDirectionAttr().Set(Gf.Vec3f(0., 0., -1.))
        scene.GetGravityMagnitudeAttr().Set(9.81)
        scene_api = PhysxSchema.PhysxSceneAPI.Apply(scene.GetPrim())
        scene_api.CreateEnableCCDAttr().Set(True)
        scene_api.CreateEnableStabilizationAttr().Set(True)
        scene_api.CreateSolverTypeAttr().Set("TGS")
        scene_api.CreateTimeStepsPerSecondAttr().Set(60)
        namespace = original_constructor_namespace(source, stage, asset)
        for side in ("left", "right"):
            namespace["_add_fr3"](f"/World/{side}_fr3", config["robots"][side]["base_at_rest_world_m"])
        for _ in range(20):
            render_only()
        namespace["_apply_official_joint_limits"]()
        namespace["_build_tool"]("/World/left_fr3", -1.)
        namespace["_build_tool"]("/World/right_fr3", 1.)
        box = namespace["_box"]
        box("/World/Table", config["table"]["center_world_m"], config["table"]["size_m"], (.0,.65,.85))
        x0, x1 = config["carriage"]["interior_x_world_m"]
        y0, y1 = config["carriage"]["interior_y_world_m"]
        t, h = config["carriage"]["wall_thickness_m"], config["carriage"]["wall_height_m"]
        z = config["table"]["top_world_z_m"] + .5*h
        UsdGeom.Xform.Define(stage, "/World/Task01")
        UsdGeom.Xform.Define(stage, "/World/Task01/Carriage")
        box("/World/Task01/Carriage/WallDeep", (x1+t*.5,(y0+y1)*.5,z), (t,y1-y0+2*t,h), (.32,.40,.55))
        box("/World/Task01/Carriage/WallMinusY", ((x0+x1)*.5,y0-t*.5,z), (x1-x0+2*t,t,h), (.32,.40,.55))
        box("/World/Task01/Carriage/WallPlusY", ((x0+x1)*.5,y1+t*.5,z), (x1-x0+2*t,t,h), (.32,.40,.55))
        box("/World/Task01/Cube", states[0]["cube_center_world_m"], config["cube"]["size_m"],
            (.92,.62,.18), dynamic=True, gravity=True)
        entrance = UsdGeom.Xform.Define(stage, "/World/Task01/carriage_entrance")
        entrance.AddTranslateOp().Set(Gf.Vec3d(*config["frames"]["carriage_entrance"]["origin_world_m"]))
        light = UsdLux.DomeLight.Define(stage, "/World/PreviewLight")
        light.CreateIntensityAttr(1000.)
        set_camera_view(eye=[2.5,-2.2,1.8], target=[.8,0.,.35])
        for _ in range(20):
            render_only()
        capture = capture_viewport_to_file(get_active_viewport(), str(args.output_dir / "gui_initial.png"))
        for _ in range(12):
            render_only()
        print("TASK01 VISIBLE_SINGLE_CUBE_GUI_READY: before physics load; no controller", flush=True)
        # Snapshot immutable original shape placement relative to its actual rigid body.
        # Later source-query geometry must match the LIVE tensor body pose, not a stale USD pose.
        shape_audit, local_to_owner, owners = {}, {}, {}
        enabled = []
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.CollisionAPI) and UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Get():
                if not prim.IsA(UsdGeom.Gprim):
                    raise RuntimeError("Enabled collider is not an inspectable Gprim: "+str(prim.GetPath()))
                path = str(prim.GetPath())
                enabled.append(path)
                matrix = UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(0.)
                body = owning_body(prim,UsdPhysics)
                owner = str(body.GetPath()) if body else None
                owners[path] = owner
                # Cube collider 与 rigid body 是同一 prim，其 USD scale 是原实际尺寸。
                # Tensor/native body 是纯 SE(3)；若用完整 owner USD inverse 会错误消掉尺寸。
                owner_rigid_world = pure_rigid_matrix(UsdGeom.Xformable(body).ComputeLocalToWorldTransform(0.), Gf) if body else None
                relative = matrix * owner_rigid_world.GetInverse() if body else matrix
                local_to_owner[path] = relative
                info = {"type":str(prim.GetTypeName()),"rigid_body_owner":owner,
                        "original_local_to_owner_matrix":np.asarray(relative).tolist(),
                        "original_authored_local_matrix":np.asarray(UsdGeom.Xformable(prim).GetLocalTransformation()).tolist(),
                        "original_owner_rigid_world_matrix":np.asarray(owner_rigid_world).tolist() if body else None,
                        "owner_frame_contract":"pure SE3; original collider scales retained in local_to_owner",
                        "collision_enabled":True}
                if prim.IsA(UsdGeom.Cube): info["cube_size_attribute"]=float(UsdGeom.Cube(prim).GetSizeAttr().Get())
                if prim.IsA(UsdGeom.Cylinder):
                    cylinder=UsdGeom.Cylinder(prim)
                    info.update({"cylinder_axis":str(cylinder.GetAxisAttr().Get()),
                                 "cylinder_radius":float(cylinder.GetRadiusAttr().Get()),
                                 "cylinder_height":float(cylinder.GetHeightAttr().Get())})
                if prim.IsA(UsdGeom.Mesh):
                    info["mesh_approximation"]=str(UsdPhysics.MeshCollisionAPI(prim).GetApproximationAttr().Get())
                    info["mesh_point_count"]=len(UsdGeom.Mesh(prim).GetPointsAttr().Get())
                collision_api=PhysxSchema.PhysxCollisionAPI(prim)
                info["authored_contact_offset_m"]=collision_api.GetContactOffsetAttr().Get()
                info["authored_rest_offset_m"]=collision_api.GetRestOffsetAttr().Get()
                info["effective_contact_offset"]= "NOT_EXPOSED_BY_THIS_STATIC_API"
                shape_audit[path]=info
        tcp_local={}
        for side in ("left","right"):
            link_path=f"/World/{side}_fr3/fr3_link8"
            tcp_path=link_path+"/side_suction_tool/side_suction_tcp"
            tcp_prim=stage.GetPrimAtPath(tcp_path)
            if not tcp_prim.IsValid(): raise RuntimeError("Original TCP missing: "+tcp_path)
            tcp_local[side]=UsdGeom.Xformable(tcp_prim).ComputeLocalToWorldTransform(0.) * pure_rigid_matrix(UsdGeom.Xformable(stage.GetPrimAtPath(link_path)).ComputeLocalToWorldTransform(0.), Gf).GetInverse()
        write_json(args.output_dir/"original_shape_audit.json",shape_audit)
        # 不发 timeline PLAY：Isaac4.5 SimulationManager 的 PLAY warm-start
        # 回调直接 update_simulation 两次，绕过 renderer dispatcher。
        # 原生 start_simulation 仅保存初态/初始化 manual-step 上下文；此处
        # 不调用 update_simulation/simulate/fetch，实际零step事件仍是硬门禁。
        original_dispatch = settings.get("/app/player/playSimulations")
        if not isinstance(original_dispatch, bool):
            raise RuntimeError("Original render-only dispatcher setting missing before physics load")
        settings.set_bool("/app/player/playSimulations",False)
        try:
            physx.force_load_physics_from_usd()
            physx.start_simulation()
        finally:
            settings.set_bool("/app/player/playSimulations",original_dispatch)
        if physics_steps:
            raise RuntimeError("Static handle initialization triggered physics steps")
        sim = tensors.create_simulation_view("numpy")
        sim.set_subspace_roots("/")
        arts = {side: sim.create_articulation_view(f"/World/{side}_fr3") for side in ("left","right")}
        cube = sim.create_rigid_body_view("/World/Task01/Cube")
        for side, art in arts.items():
            if art.count != 1 or not art.check():
                raise RuntimeError("Original articulation handle not available without an integration step: "+side)
        if cube.count != 1 or not cube.check():
            raise RuntimeError("Original dynamic Cube handle not initialized")
        physx = omni.physx.get_physx_interface()
        readback_suppressed = bool(physx.is_readback_suppressed())
        cooking = omni.physx.get_physx_cooking_interface()
        query = omni.physx.get_physx_scene_query_interface()
        model_by_shape = {path: model_name(path) for path in enabled}
        cooked = {}
        for path in enabled:
            prim = stage.GetPrimAtPath(path)
            if prim.IsA(UsdGeom.Mesh):
                approximation = str(UsdPhysics.MeshCollisionAPI(prim).GetApproximationAttr().Get())
                count = cooking.get_nb_convex_mesh_data(path)
                if approximation != "convexHull" or count != 1:
                    raise RuntimeError("Original Mesh is not a single cooked convexHull; source overlap approximation would be ambiguous: " + path)
                convexes = []
                for index in range(count):
                    data = cooking.get_convex_mesh_data(path,index)
                    convexes.append({"num_vertices":int(data["num_vertices"]),
                        "vertices":[list(map(float,p)) for p in data["vertices"]],
                        "num_polygons":int(data["num_polygons"]), "indices":list(map(int,data["indices"])),
                        "polygons":[{"plane":list(map(float,p["plane"])),
                                     "num_vertices":int(p["num_vertices"]),"index_base":int(p["index_base"])}
                                    for p in data["polygons"]]})
                if not convexes:
                    raise RuntimeError("Actual cooked convex unavailable, refusing authored-hull substitute: "+path)
                cooked[path] = {"model_link":model_by_shape[path], "convexes":convexes,
                    "authored_approximation":str(UsdPhysics.MeshCollisionAPI(prim).GetApproximationAttr().Get())}
        write_json(args.output_dir / "cooked_shapes.json", cooked)
        write_json(args.output_dir / "scene_audit.json", {
            "visible_gui": True, "cube_count":1, "enabled_collision_shapes":model_by_shape,
            "cube_mass_kg":np.asarray(cube.get_masses()).tolist(),
            "cube_effective_material_properties":np.asarray(cube.get_material_properties()).tolist(),
            "original_material_binding_reused":False,
            "articulations":{side:{"dof_names":list(art.shared_metatype.dof_names),"link_paths":art.link_paths,
                "effective_material_properties":np.asarray(art.get_material_properties()).tolist()}
                for side,art in arts.items()},
            "original_srdf_allowed_pairs":[{"pair":list(p),"reason":reason} for p,reason in original_acm.items()],
            "controller_graphs":[],"gravity_disabled":False,"simulation_integration_requested":False})
        immutable_geometry_sha, immutable_geometry_records = original_geometry_fingerprint(
            stage, enabled, list(arts["left"].link_paths[0]) + list(arts["right"].link_paths[0]) + ["/World/Task01/Cube"],
            UsdPhysics, UsdGeom, return_records=True)
        write_json(args.output_dir / "immutable_geometry_at_load.json", {
            "sha256": immutable_geometry_sha, "records": immutable_geometry_records})
        initial_body_output_ops = body_output_op_audit(
            stage, list(arts["left"].link_paths[0]) + list(arts["right"].link_paths[0]) + ["/World/Task01/Cube"], UsdGeom)
        write_json(args.output_dir / "body_output_ops_at_load.json", initial_body_output_ops)
        write_json(args.output_dir / "query_api_contract.json", {
            "is_readback_suppressed": readback_suppressed,
            "readback_flag_api_note":"official API returns false when simulation is not running; paused flag alone is not freshness proof",
            "tensor_frontend": "numpy", "tensor_device_ordinal": int(sim.device_ordinal),
            "pose_guard": "nominal FK + live tensors + native actor + USD collider frame",
            "moving_target_query_guard": "each original collider inside sphere hit; remembered old point negative only with conservative world AABB separation proof",
            "query_sphere_radius_m": 1e-5,
            "mesh_guard": "original single cooked convexHull only; actual cooked vertices, no authored-hull substitute",
            "physics_integration_requested": False, "poststep_contacts": "NOT_RUN"})
        # 原固定墙角是车厢构造连接，不属于 MoveIt 的机器人/物体碰撞查询。
        # 保留实际 hits 和 AABB 证明；不添加 ACM，不删除或关闭任何原 collider。
        env_paths=[path for path in enabled if model_by_shape[path] in
                   ("table","carriage_deep_wall","carriage_minus_y_wall","carriage_plus_y_wall")]
        bbox=UsdGeom.BBoxCache(0.,[UsdGeom.Tokens.default_],useExtentsHint=False)
        ranges={path:bbox.ComputeWorldBound(stage.GetPrimAtPath(path)).ComputeAlignedRange() for path in env_paths}
        fixture_pairs={}
        for n,a in enumerate(env_paths):
            for b in env_paths[n+1:]:
                overlap=[min(ranges[a].GetMax()[k],ranges[b].GetMax()[k])-max(ranges[a].GetMin()[k],ranges[b].GetMin()[k]) for k in range(3)]
                if min(overlap)>=-1e-7:
                    fixture_pairs[tuple(sorted((a,b)))]= {"overlap_xyz_m":list(map(float,overlap)),
                        "construction":"ORIGINAL_FIXED_TABLE_WALL_CONNECTION",
                        "provenance":"FCL_RUN_SNAPSHOT_AND_ORIGINAL_USD_BOX_AABB"}
        deep="/World/Task01/Carriage/WallDeep"
        expected_smoke={"/World/Task01/Carriage/WallMinusY","/World/Task01/Carriage/WallPlusY"}
        code=PhysicsSchemaTools.encodeSdfPath(Sdf.Path(deep))
        smoke = native_query_hits(lambda report: query.overlap_shape(code[0],code[1],report,False),
                                  model_by_shape, "original_fixed_wall_overlap_shape")
        smoke_hits = [hit["collision"] for hit in smoke["hits"]]
        smoke_ok=expected_smoke.issubset(set(smoke_hits)) and all(
            tuple(sorted((deep,p))) in fixture_pairs and min(fixture_pairs[tuple(sorted((deep,p)))]["overlap_xyz_m"])>0. for p in expected_smoke)
        smoke_ok = smoke_ok and "error" not in smoke
        write_json(args.output_dir/"positive_query_smoke.json",{
            "known_original_overlap_query_source":deep,"required_native_hits":sorted(expected_smoke),
            "actual_native_hits":smoke_hits,"native_query_details":smoke,
            "fixture_aabb_pairs":[{"shape_pair":list(p),**d} for p,d in fixture_pairs.items()],
            "status":"PASS_NATIVE_QUERY" if smoke_ok else "FAIL_QUERY_NOT_VERIFIED"})
        if not smoke_ok:raise RuntimeError("Original positive-overlap smoke failed; empty native queries are not parity PASS")
        order = list(dict.fromkeys([0,135,136,292,196] + list(range(len(states)))))
        rows, remembered_inside_points = [], {}
        moving_negative_checks = 0
        with (args.output_dir / "static_replay.jsonl").open("w") as stream:
            for index in order:
                if stopping:
                    raise RuntimeError("Inspection interrupted, incomplete parity is not PASS")
                row = states[index]
                actual = {}
                for side, art in arts.items():
                    q = np.array(art.get_dof_positions(), copy=True)
                    expected_names = [f"fr3_joint{i}" for i in range(1,8)]
                    selected = [list(art.shared_metatype.dof_names).index(name) for name in expected_names]
                    q[0,selected] = row[side+"_q_rad"]
                    art.set_dof_positions(q,np.array([0],np.uint32))
                    art.set_dof_position_targets(q,np.array([0],np.uint32))
                    art.set_dof_velocities(np.zeros_like(q),np.array([0],np.uint32))
                    observed = np.array(art.get_dof_positions(),copy=True)[0,selected]
                    if not np.all(np.isfinite(observed)) or not np.all(np.isfinite(row[side+"_q_rad"])) or np.max(np.abs(observed-row[side+"_q_rad"]))>1e-6:
                        raise RuntimeError("Non-finite or inaccurate live q reset: "+side)
                    actual[side] = {"q_rad":observed.tolist(),
                        "maximum_q_reset_error_rad":float(np.max(np.abs(observed-row[side+"_q_rad"]))) }
                cube.set_transforms(np.array([row["cube_center_world_m"]+row["cube_orientation_xyzw"]],np.float32),np.array([0],np.uint32))
                cube.set_velocities(np.zeros((1,6),np.float32),np.array([0],np.uint32))
                kinematic_update = sim.update_articulations_kinematic()
                if kinematic_update is False:
                    raise RuntimeError("Original articulation kinematic refresh returned failure")
                physx.update_transformations(True,True)
                cube_actual=np.array(cube.get_transforms(),copy=True)[0]
                cube_position_error=math.dist(cube_actual[:3],row["cube_center_world_m"])
                cube_angle_error=quat_angle(cube_actual[3:],row["cube_orientation_xyzw"])
                if not np.all(np.isfinite(cube_actual)) or cube_position_error>1e-6 or cube_angle_error>1e-5:
                    raise RuntimeError("Non-finite or inaccurate live Cube reset")
                live_by_path={"/World/Task01/Cube":transform_matrix(cube_actual,Gf)}
                fk = []
                for side, art in arts.items():
                    transforms = np.array(art.get_link_transforms(),copy=True)[0]
                    if len(transforms) != len(art.link_paths[0]) or not np.all(np.isfinite(transforms)):
                        raise RuntimeError("Malformed or non-finite live link FK: "+side)
                    live_by_path.update({path:transform_matrix(p,Gf) for path,p in zip(art.link_paths[0],transforms)})
                    for link in range(9):
                        path = f"/World/{side}_fr3/fr3_link{link}"
                        k = list(art.link_paths[0]).index(path)
                        observed = transforms[k]
                        expected = row["link_world_poses"][f"{side}_fr3_link{link}"]
                        epos = math.dist(observed[:3],expected["translation_m"])
                        eang = quat_angle(observed[3:],expected["quaternion_xyzw"])
                        fk.append({"model_link":f"{side}_fr3_link{link}","live_pose_xyzw":observed.tolist(),
                                   "nominal_fk_translation_error_m":epos,"nominal_fk_rotation_error_rad":eang})
                        if epos > 1e-5 or eang > 1e-4:
                            write_json(args.output_dir / "fk_rejection.json",{"state_index":index,"fk":fk,"actual_q":actual})
                            raise RuntimeError("Live nominal FK mismatch; do not claim parity at wrong pose: "+path)
                    tcp_observed=matrix_pose(tcp_local[side]*live_by_path[f"/World/{side}_fr3/fr3_link8"])
                    tcp_expected=row["link_world_poses"][side+"_fr3_side_suction_tcp"]
                    epos=math.dist(tcp_observed[:3],tcp_expected["translation_m"])
                    eang=quat_angle(tcp_observed[3:],tcp_expected["quaternion_xyzw"])
                    if not np.all(np.isfinite(tcp_observed)) or epos>1e-5 or eang>1e-4:
                        raise RuntimeError("Live original fixed-tool TCP mismatch: "+side)
                    actual[side]["live_tcp_xyzw"]=tcp_observed
                    actual[side]["tcp_position_error_m"]=epos
                    actual[side]["tcp_rotation_error_rad"]=eang
                native_bodies={}
                native_actor_gate_completed = False
                for body_path,live_matrix in live_by_path.items():
                    native=physx.get_rigidbody_transformation(body_path)
                    if not native.get("ret_val"):
                        raise RuntimeError("Original PhysX actor pose unavailable: "+body_path)
                    native_pose=list(map(float,native["position"]))+list(map(float,native["rotation"]))
                    live_pose=matrix_pose(live_matrix)
                    epos=math.dist(native_pose[:3],live_pose[:3])
                    eang=quat_angle(native_pose[3:],live_pose[3:])
                    native_bodies[body_path]={"native_actor_pose_xyzw":native_pose,
                        "tensor_pose_xyzw":live_pose,"position_difference_m":epos,"rotation_difference_rad":eang}
                    if not np.all(np.isfinite(native_pose)) or epos>1e-5 or eang>1e-4:
                        write_json(args.output_dir/"native_actor_rejection.json",{"state_index":index,
                            "native_actor_comparison":native_bodies,"actual_q":actual,
                            "kind":"ENGINEERING_STALE_NATIVE_ACTOR_STOP","physics_step":None,"simulation_timestamp":None})
                        raise RuntimeError("Native PhysX actor differs from LIVE tensor FK: "+body_path)
                native_actor_gate_completed = True
                def stale_shape_paths():
                    return [path for path in enabled if float(np.max(np.abs(
                        np.asarray(UsdGeom.Xformable(stage.GetPrimAtPath(path)).ComputeLocalToWorldTransform(0.)) -
                        np.asarray(local_to_owner[path]*live_by_path[owners[path]] if owners[path] else local_to_owner[path])))) > 1e-5]
                sync = {"before_stale_shapes": stale_shape_paths(), "existing_pose_ops_written": [],
                        "original_body_output_ops_at_load": initial_body_output_ops,
                        "before_adapter_body_output_ops": body_output_op_audit(stage, list(live_by_path), UsdGeom)}
                if sync["before_stale_shapes"]:
                    physx.update_transformations_scene(PhysicsSchemaTools.sdfPathToInt("/physicsScene"), True, False)
                    sync["after_official_scene_export_stale_shapes"] = stale_shape_paths()
                    if sync["after_official_scene_export_stale_shapes"] and fabric_interface is not None:
                        fabric_interface.force_update(1./60., static_timeline_time)
                        fabric_interface.save_to_usd()
                        sync["after_existing_fabric_export_stale_shapes"] = stale_shape_paths()
                    if stale_shape_paths():
                        sync["existing_pose_ops_written"] = mirror_existing_body_pose_ops(
                            stage, live_by_path, Gf, UsdGeom, np)
                sync["after_output_stale_shapes"] = stale_shape_paths()
                # 暂停 GUI 处理 USD notices；不能假定 USD 写值只是渲染输出。
                # 后面的原生 actor / q / geometry / step 守卫全部在 notices 后检查。
                render_only()
                static_subsystem_refresh(omni.physx.get_physx_simulation_interface(),
                    omni.physx.get_physx_stage_update_interface(), timeline, physics_steps)
                sync["official_disabled_physics_subsystem_refresh"] = {
                    "flush_buffered_changes": True, "elapsed_sec": 0.0,
                    "enable_physics_update": False, "query_freshness_not_assumed": True}
                sync["after_paused_notice_update_stale_shapes"] = stale_shape_paths()
                # 只重建原物理对象，不对新 view 做任何 position setter。
                # 若原14q不能从当前原 body poses恢复，立即停，不修补模型。
                original_body_paths = list(live_by_path)
                sim, arts, cube = rebuild_original_static_handles(
                    physx, tensors, sim, settings, timeline, physics_steps, immutable_geometry_sha,
                    lambda: original_geometry_fingerprint(stage, enabled, original_body_paths, UsdPhysics, UsdGeom))
                reloaded_actual = {}
                for side, art in arts.items():
                    selected = [list(art.shared_metatype.dof_names).index(f"fr3_joint{i}") for i in range(1,8)]
                    q_reloaded = np.array(art.get_dof_positions(), copy=True)[0,selected]
                    reloaded_actual[side] = {"q_rad":q_reloaded.tolist(),
                        "maximum_q_difference_from_candidate_rad":float(np.max(np.abs(q_reloaded-row[side+"_q_rad"]))) }
                    if not np.all(np.isfinite(q_reloaded)) or reloaded_actual[side]["maximum_q_difference_from_candidate_rad"] > 1e-6:
                        write_json(args.output_dir / "original_rebuild_rejection.json", {
                            "state_index":index, "reloaded_actual_before_any_setter":reloaded_actual,
                            "expected_q":{s:row[s+"_q_rad"] for s in ("left","right")},
                            "kind":"ENGINEERING_ORIGINAL_RELOAD_STATE_STOP"})
                        raise RuntimeError("Original model reload did not recover candidate 14q: " + side)
                reloaded_cube = np.array(cube.get_transforms(), copy=True)[0]
                if not np.all(np.isfinite(reloaded_cube)) or math.dist(reloaded_cube[:3],cube_actual[:3])>1e-6 or quat_angle(reloaded_cube[3:],cube_actual[3:])>1e-5:
                    raise RuntimeError("Original reloaded Cube pose differs before any setter")
                sync["original_handle_rebuild"] = {
                    "reloaded_q_before_any_setter": reloaded_actual,
                    "reloaded_cube_before_any_setter_xyzw":reloaded_cube.tolist(),
                    "new_joint_state_schema_or_attribute":False,
                    "query_freshness_not_assumed":True}
                sync["after_adapter_body_output_ops"] = body_output_op_audit(stage, list(live_by_path), UsdGeom)
                sync["immutable_geometry_sha256"] = original_geometry_fingerprint(
                    stage, enabled, list(live_by_path), UsdPhysics, UsdGeom)
                sync["original_immutable_geometry_sha256"] = immutable_geometry_sha
                sync["physics_step_callback_count"] = len(physics_steps)
                if (physics_steps or timeline.is_playing() or float(timeline.get_current_time()) != static_timeline_time or
                        {path: settings.get(path) for path in output_settings_paths} != original_output_settings or
                        sync["immutable_geometry_sha256"] != immutable_geometry_sha):
                    write_json(args.output_dir/"output_sync_rejection.json", {"state_index": index, "sync": sync,
                        "native_actor_comparison_before_output":native_bodies, "actual_q":actual,
                        "kind":"ENGINEERING_OUTPUT_INTEGRITY_STOP"})
                    digest, changed_records = original_geometry_fingerprint(
                        stage, enabled, list(live_by_path), UsdPhysics, UsdGeom, return_records=True)
                    write_json(args.output_dir / "immutable_geometry_at_rejection.json", {
                        "sha256": digest, "records": changed_records})
                    raise RuntimeError("Output sync changed geometry/settings or integrated physics")
                after_native = {}
                for body_path, before in native_bodies.items():
                    native = physx.get_rigidbody_transformation(body_path)
                    if not native.get("ret_val"):
                        raise RuntimeError("Native actor disappeared after output sync: " + body_path)
                    pose = list(map(float,native["position"])) + list(map(float,native["rotation"]))
                    before_pose = before["native_actor_pose_xyzw"]
                    after_native[body_path] = {"native_actor_pose_xyzw":pose,
                        "position_change_m":math.dist(pose[:3],before_pose[:3]),
                        "rotation_change_rad":quat_angle(pose[3:],before_pose[3:])}
                    if not np.all(np.isfinite(pose)) or after_native[body_path]["position_change_m"] > 1e-6 or after_native[body_path]["rotation_change_rad"] > 1e-5:
                        raise RuntimeError("Output sync altered native actor pose: " + body_path)
                for side, art in arts.items():
                    names = [f"fr3_joint{i}" for i in range(1,8)]
                    selected = [list(art.shared_metatype.dof_names).index(name) for name in names]
                    observed = np.array(art.get_dof_positions(),copy=True)[0,selected]
                    if not np.all(np.isfinite(observed)) or np.max(np.abs(observed-actual[side]["q_rad"])) > 1e-6:
                        raise RuntimeError("Output sync altered original articulation q: " + side)
                sync["native_actor_comparison_after_output"] = after_native
                shape_frames, live_shape_matrices = [], {}
                for path in enabled:
                    actual_matrix=UsdGeom.Xformable(stage.GetPrimAtPath(path)).ComputeLocalToWorldTransform(0.)
                    expected_matrix=local_to_owner[path]*live_by_path[owners[path]] if owners[path] else local_to_owner[path]
                    matrix_error=float(np.max(np.abs(np.asarray(actual_matrix)-np.asarray(expected_matrix))))
                    frame={"shape_path":path,"owner":owners[path],"actual_usd_matrix":np.asarray(actual_matrix).tolist(),
                           "expected_from_live_body_matrix":np.asarray(expected_matrix).tolist(),"max_abs_matrix_error":matrix_error}
                    shape_frames.append(frame)
                    live_shape_matrices[path] = expected_matrix
                    if not np.all(np.isfinite(np.asarray(actual_matrix))) or matrix_error>1e-5:
                        write_json(args.output_dir/"query_frame_rejection.json",{"state_index":index,"rejected_frame":frame,
                            "actual_q":actual,"live_fk_comparison":fk,"Cube_actual_xyzw":cube_actual.tolist(),
                            "native_actor_comparison":native_bodies,"output_sync":sync,
                            "kind":"ENGINEERING_STALE_USD_QUERY_SOURCE_STOP","physics_step":None,"simulation_timestamp":None})
                        raise RuntimeError("USD query source differs from LIVE original rigid body frame: "+path)
                # 不添加任何物体或改碰撞掩码；直接查询原 collider 内部点。
                # 静态墙角 smoke 不能证明移动 target 的 broadphase 已更新。
                if index in (0,135,136,292,196):
                    capture_viewport_to_file(get_active_viewport(),str(args.output_dir/f"static_source_state_{index:03d}.png"))
                    for _ in range(4): render_only()
                    if physics_steps or timeline.is_playing():
                        raise RuntimeError("Static source screenshot integrated physics")
                moving_query_guards = []
                for path in enabled:
                    point, lower, upper = transformed_probe_geometry(
                        stage.GetPrimAtPath(path), cooked.get(path), live_shape_matrices[path], np, Gf, UsdGeom)
                    sphere_radius = 1e-5
                    positive = native_query_hits(
                        lambda report: query.overlap_sphere(sphere_radius, Gf.Vec3f(*map(float, point)), report, False),
                        model_by_shape, "inside_original_collider_native_overlap_sphere")
                    matching = [hit for hit in positive["hits"] if hit["collision"] == path]
                    owner_ok = owners[path] is None or all(hit["rigid_body"] == owners[path] for hit in matching)
                    guard = {"shape_path": path, "model_link": model_by_shape[path],
                             "expected_rigid_body_owner": owners[path], "world_inside_point_m": point.tolist(),
                             "conservative_world_shape_aabb_min_m": lower.tolist(),
                             "conservative_world_shape_aabb_max_m": upper.tolist(),
                             "sphere_radius_m": sphere_radius, "positive_query": positive,
                             "positive_exact_path_hit": bool(matching), "positive_owner_matches": owner_ok}
                    if "error" in positive or not matching or not owner_ok:
                        guard["status"] = "FAIL_POSITIVE_TARGET_QUERY"
                        write_json(args.output_dir / "moving_query_rejection.json", {
                            "state_index": index, "guard": guard, "earlier_guards_this_state": moving_query_guards,
                            "kind": "ENGINEERING_STALE_OR_UNVERIFIED_NATIVE_QUERY_STOP",
                            "physics_step": None, "simulation_timestamp": None})
                        raise RuntimeError("Native query did not prove the LIVE original collider target: " + path)
                    previous = remembered_inside_points.get(path)
                    if previous is not None and sphere_proven_outside_aabb(previous["point"], lower, upper, sphere_radius):
                        negative = native_query_hits(
                            lambda report: query.overlap_sphere(sphere_radius, Gf.Vec3f(*previous["point"]), report, False),
                            model_by_shape, "old_point_proven_outside_current_original_shape_aabb")
                        negative_exact_hit = any(hit["collision"] == path for hit in negative["hits"])
                        guard.update({"negative_query": negative, "remembered_point_state_index": previous["state_index"],
                                      "remembered_world_point_m": previous["point"],
                                      "negative_proof": "sphere separated from whole current world AABB by additional 1e-6 m",
                                      "negative_exact_path_absent": not negative_exact_hit})
                        if "error" in negative or negative_exact_hit:
                            guard["status"] = "FAIL_STALE_NEGATIVE_TARGET_QUERY"
                            write_json(args.output_dir / "moving_query_rejection.json", {
                                "state_index": index, "guard": guard, "earlier_guards_this_state": moving_query_guards,
                                "kind": "ENGINEERING_STALE_OR_UNVERIFIED_NATIVE_QUERY_STOP",
                                "physics_step": None, "simulation_timestamp": None})
                            raise RuntimeError("Native query retained the old collider at a proven-separated point: " + path)
                        moving_negative_checks += 1
                    else:
                        guard["negative_query"] = "NOT_REQUIRED_FIRST_SAMPLE_OR_AABB_SEPARATION_NOT_PROVED"
                    if previous is None:
                        remembered_inside_points[path] = {"point": point.tolist(), "state_index": index}
                    guard["status"] = "PASS_POSITIVE_AND_ANY_PROVED_NEGATIVE_TARGET_QUERY"
                    moving_query_guards.append(guard)
                hits, unallowed, dedup = [], [], set()
                original_shape_queries = []
                for source_path in enabled:
                    code = PhysicsSchemaTools.encodeSdfPath(Sdf.Path(source_path))
                    observed_query = native_query_hits(
                        lambda report: query.overlap_shape(code[0],code[1],report,False),
                        model_by_shape, "original_physx_overlap_shape")
                    observed_query["source_path"] = source_path
                    original_shape_queries.append(observed_query)
                    if "error" in observed_query:
                        write_json(args.output_dir / "query_callback_rejection.json", {
                            "state_index": index, "query": observed_query,
                            "kind": "ENGINEERING_NATIVE_QUERY_CALLBACK_STOP",
                            "physics_step": None, "simulation_timestamp": None})
                        raise RuntimeError("Original-shape native query callback/count guard rejected: " + source_path)
                    for native_hit in observed_query["hits"]:
                        target_path = native_hit["collision"]
                        if target_path == source_path:
                            continue
                        pair = tuple(sorted((source_path,target_path)))
                        if pair in dedup:
                            continue
                        dedup.add(pair)
                        a,b = model_by_shape[source_path],model_by_shape[target_path]
                        mp = tuple(sorted((a,b)))
                        expected_contact = a == b or mp in original_acm
                        reason = "SAME_MODEL_LINK" if a == b else original_acm.get(mp)
                        fixture_proof=fixture_pairs.get(pair)
                        if fixture_proof:
                            expected_contact,reason=True,"FIXTURE_ENVIRONMENT_CONSTRUCTION"
                        if "shared_cube" in mp:
                            other = b if a == "shared_cube" else a
                            env = next((item for item in row["cube_environment_geometry"]["checks"]
                                        if item["body2"] == other),None)
                            if env and not env["volumetric_penetration"] and env["signed_axis_aligned_distance_m"] <= 1e-12:
                                expected_contact,reason=True,"INTENDED_NOMINAL_SUPPORT_OR_TARGET_BOUNDARY_CONTACT"
                        record={"shape_pair":list(pair),"model_pair":[a,b],
                                "query":"original_physx_overlap_shape","expected_by_existing_geometry":expected_contact,
                                "existing_reason":reason, "query_source_path":source_path,
                                "query_target_collision_path":target_path,
                                "query_target_rigid_body_path":native_hit["rigid_body"]}
                        if fixture_proof:record["fixture_construction_aabb_proof"]=fixture_proof
                        hits.append(record)
                        if not expected_contact:
                            unallowed.append(record)
                record={"kind":"GEOMETRY_STATIC_REPLAY","state_index":index,"segment":row["segment"],
                    "segment_index":row["segment_index"],"cube_center_world_m":row["cube_center_world_m"],
                    "fcl_result":row["fcl"],"nominal_minimum_fcl_distance":row["minimum_fcl_distance"],
                    "nominal_minimum_wrist_tool_environment_fcl_distance":row["minimum_wrist_tool_environment_fcl_distance"],
                    "actual_q":actual,"live_fk_comparison":fk,"native_actor_comparison":native_bodies,
                    "live_original_shape_frames":shape_frames,
                    "output_sync":sync,
                    "moving_target_query_guards":moving_query_guards,
                    "original_shape_queries":original_shape_queries,
                    "is_readback_suppressed":bool(physx.is_readback_suppressed()),
                    "Cube_actual_xyzw":cube_actual.tolist(),"Cube_position_reset_error_m":cube_position_error,
                    "Cube_rotation_reset_error_rad":cube_angle_error,"overlaps":hits,"unexpected_overlaps":unallowed,
                    "simulation_timestamp":None,"physics_step":None,"status":"FAIL_STOP" if unallowed else "PASS_STATIC_SAMPLE"}
                stream.write(json.dumps(record,sort_keys=True,allow_nan=False)+"\n")
                stream.flush()
                rows.append(record)
                if unallowed:
                    capture_viewport_to_file(get_active_viewport(),str(args.output_dir/"first_overlap.png"))
                    for _ in range(8): render_only()
                    write_json(args.output_dir/"summary.json",{"status":"FAIL_MODEL_PARITY_OVERLAP_STOP",
                        "records_checked":len(rows),"failing_state_index":index,"unexpected_overlaps":unallowed,
                        "READY_reset_not_run":True,"physics_integration_requested":False})
                    print("TASK01 STATIC_PARITY FAIL_STOP "+json.dumps(unallowed),flush=True)
                    return 1
                if len(rows)%25==0 or index in (0,135,136,292,196):
                    print(f"TASK01 STATIC_SAMPLE index={index} checked={len(rows)}/293 PASS overlaps={len(hits)}",flush=True)
                render_only()
        if (physics_steps or timeline.is_playing() or float(timeline.get_current_time()) != static_timeline_time):
            raise RuntimeError("Static replay final GUI update integrated physics or changed timeline")
        if moving_negative_checks == 0:
            raise RuntimeError("No original moving target negative-query check was verified; static-only queries are not full parity PASS")
        write_json(args.output_dir/"summary.json",{"status":"PASS_NOMINAL_STATIC_COOKED_SHAPE_PARITY_ONLY",
            "records_checked":len(rows),"unexpected_overlaps":[],"READY_reset_not_run":True,
            "moving_negative_query_checks":moving_negative_checks,
            "physics_step_callback_count":len(physics_steps),
            "physics_integration_requested":False,"poststep_model_contact_check":"NOT_RUN"})
        print("TASK01 STATIC_PARITY PASS_NOMINAL_STATIC_ONLY: 293; READY not run",flush=True)
        return 0
    except Exception as error:
        write_json(args.output_dir/"failure.json",{"status":"FAIL_INITIALIZATION_OR_STATIC_REPLAY",
            "error":repr(error),"traceback":traceback.format_exc(),"READY_reset_not_run":True,
            "state_index":locals().get("index"),"output_sync":locals().get("sync"),
            "native_actor_gate_completed":locals().get("native_actor_gate_completed",False),
            "native_actor_comparison":locals().get("native_bodies"),
            "actual_q_and_tcp":locals().get("actual"),
            "live_fk_comparison":locals().get("fk"),
            "Cube_actual_xyzw":locals().get("cube_actual").tolist() if locals().get("cube_actual") is not None else None,
            "physics_step_callback_count":len(physics_steps),
            "physics_step_callback_dt_values_sec":physics_steps,
            "physics_step":None,"simulation_timestamp":None})
        traceback.print_exc()
        return 1
    finally:
        # No background physics run survives this bounded probe.
        try:
            import omni.timeline
            omni.timeline.get_timeline_interface().pause()
            deadline=time.monotonic()+args.hold_for_inspection_sec
            while not stopping and app.is_running() and time.monotonic()<deadline:
                static_render_update(app, omni.timeline.get_timeline_interface(),
                    __import__("carb.settings",fromlist=["get_settings"]).get_settings(), physics_steps)
        finally:
            app.close()


if __name__ == "__main__":
    raise SystemExit(main())
