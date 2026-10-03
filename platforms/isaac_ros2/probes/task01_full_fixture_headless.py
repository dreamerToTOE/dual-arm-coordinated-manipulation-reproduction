"""[EXPERIMENTAL] Task27 五件真实流程探针，不预放前四件、不改旧控制器。

只读测量在同一物理步采样 Cube 位姿、碰撞 wrench 与关节原始反力。
关节反力明确保持 raw 标签，不冒充已去重力/惯性的吸盘 TCP wrench。
"""

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import signal
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--duration-sec", type=float, default=1200.0)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--record-calibration-phase", action="store_true",
                        help="Record optional TASK01 hold phase alongside physical step; not a control command")
    parser.add_argument("--asset-root", default=None,
                        help="Explicit official Isaac asset root; bypass unreliable directory discovery only")
    args = parser.parse_args()
    if args.duration_sec <= 0:
        parser.error("duration must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    legacy_root = Path(os.environ.get("TASK01_LEGACY_ROOT", "/home/ubuntu2004/lmy/dual-arm-embodied-palletizing"))
    from isaacsim import SimulationApp
    app = SimulationApp({"headless": True, "multi_gpu": False, "sync_loads": False,
                         "fast_shutdown": True})
    bridge = subscription = None
    stopping = False
    def request_stop(signum, frame):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    snapshots, errors, last_stamp, latest_snapshot = 0, [], None, None
    peak_collision_force = {}
    try:
        import builtins
        import numpy as np
        import omni.physics.tensors as tensors
        import omni.physx
        import omni.timeline
        import omni.usd
        from pxr import PhysxSchema, UsdPhysics, UsdShade
        from isaacsim.core.prims import RigidPrim
        import isaacsim.storage.native as storage
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from physics_object_sampler import PhysicsObjectSampler
        from physics_contact_sampler import PhysicsContactSampler
        omni.usd.get_context().new_stage()
        namespace = {"_SIDE_SUCTION_SCENARIO": "task27"}
        source = legacy_root / "isaac/scripts/task26_truck_box_scene.py"
        # [ENGINEERING] S3 对象可读但目录发现可能失败。仅在显式给出根路径时
        # 跳过目录发现；旧场景仍 stat/引用同一官方 FR3 USD，不替换机器人。
        original_discovery = storage.get_assets_root_path
        if args.asset_root:
            storage.get_assets_root_path = lambda: args.asset_root
        try:
            exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), namespace, namespace)
        finally:
            storage.get_assets_root_path = original_discovery
        scene_values = {"entry_x": float(namespace["BOX_INTERIOR_X"][0]),
                        "table_top_z": float(namespace["TABLE_TOP_Z"]),
                        "tcp_y": float(namespace["TCP_Y"]),
                        "vertical_drop_z": float(namespace["VERTICAL_DROP_Z"])}
        stage = omni.usd.get_context().get_stage()
        paths = [f"/World/Task27/Supply/Cube_{i:02d}" for i in range(1, 6)]
        for path in paths:
            prim = stage.GetPrimAtPath(path)
            if not prim.IsValid():
                raise RuntimeError(f"Missing normal initial-scene Cube: {path}")
            # 只启用接触报告，不关闭 stabilization，也不改几何/重力/摩擦。
            PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.0)
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        for _ in range(120):
            app.update()
        source = legacy_root / "isaac/scripts/task26_truck_box_bridge.py"
        namespace = {"_SIDE_SUCTION_SCENARIO": "task27"}
        exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), namespace, namespace)
        bridge = builtins._task26_batched_feed_bridge
        calibration_phase = ""
        phase_subscription = None
        if args.record_calibration_phase:
            from std_msgs.msg import String
            def receive_phase(message):
                nonlocal calibration_phase
                calibration_phase = message.data
            phase_subscription = bridge.node.create_subscription(
                String, "/task01/calibration_phase", receive_phase, 10)
        view = RigidPrim(paths, reset_xform_properties=False, prepare_contact_sensors=False)
        view.initialize()
        pose_sampler = PhysicsObjectSampler(view)
        sim_view = tensors.create_simulation_view("numpy")
        sim_view.set_subspace_roots("/")
        fixed_filters = ["/World/Table"] + ["/World/Task27/TruckBox/" + name for name in (
            "WallDeep", "WallMinusY", "WallPlusY")]
        contact_samplers = [PhysicsContactSampler(sim_view.create_rigid_contact_view(
            path, fixed_filters + [other for other in paths if other != path], 256),
            [path], fixed_filters + [other for other in paths if other != path]) for path in paths]
        articulations = {side: sim_view.create_articulation_view(f"/World/{side}_fr3")
                         for side in ("left", "right")}
        for side, articulation in articulations.items():
            if articulation.count != 1:
                raise RuntimeError(f"Missing {side} physics articulation")
        topology = {side: {"link_paths": articulation.link_paths, "dof_paths": articulation.dof_paths,
                           "masses_kg": np.asarray(articulation.get_masses()).tolist(),
                           "com_poses": np.asarray(articulation.get_coms()).tolist()}
                    for side, articulation in articulations.items()}
        # Read actual mass instead of inferring it from a scaled USD shape.
        topology["cube_masses_kg_physics"] = np.asarray(view.get_masses()).tolist()
        cube_physics_view = sim_view.create_rigid_body_view(paths)
        if list(cube_physics_view.prim_paths) != paths:
            raise RuntimeError("Cube physics material view path order changed")
        topology["cube_shape_material_properties_physics"] = {
            "paths": paths, "columns": ["static_friction", "dynamic_friction", "restitution"],
            "values": np.asarray(cube_physics_view.get_material_properties()).tolist(),
            "note": "Actual shape coefficients, not pairwise effective friction/combine-mode validation"}
        material_audit = {}
        material_paths = paths + fixed_filters
        for side in ("left", "right"):
            material_paths += [f"/World/{side}_fr3/fr3_link8/side_suction_tool/{name}" for name in
                               ("vertical_support", "lateral_support", "vacuum_manifold")]
        for path in material_paths:
            prim = stage.GetPrimAtPath(path)
            if not prim.IsValid():
                material_audit[path] = {"prim_valid": False}
                continue
            material, relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial(
                materialPurpose="physics")
            general_material, general_relationship = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
            material_prim = material.GetPrim() if material else None
            values = {"prim_valid": True,
                      "physics_purpose_binding": str(material.GetPath()) if material else None,
                      "all_purpose_binding": str(general_material.GetPath()) if general_material else None,
                      "note": "All-purpose PhysicsMaterial binding is also audited; pairwise effective combine rule is not inferred"}
            if not material_prim and general_material:
                material_prim = general_material.GetPrim()
            values["physics_material_candidate"] = (
                str(material_prim.GetPath()) if material_prim and material_prim.HasAPI(UsdPhysics.MaterialAPI) else None)
            if material_prim and material_prim.HasAPI(UsdPhysics.MaterialAPI):
                api = UsdPhysics.MaterialAPI(material_prim)
                values.update({"static_friction": api.GetStaticFrictionAttr().Get(),
                               "dynamic_friction": api.GetDynamicFrictionAttr().Get(),
                               "restitution": api.GetRestitutionAttr().Get()})
                if material_prim.HasAPI(PhysxSchema.PhysxMaterialAPI):
                    physx = PhysxSchema.PhysxMaterialAPI(material_prim)
                    values["friction_combine_mode"] = physx.GetFrictionCombineModeAttr().Get()
            material_audit[path] = values
        topology["physics_material_bindings_audit"] = material_audit
        incoming_joints = {}
        for prim in stage.Traverse():
            if prim.IsA(UsdPhysics.Joint):
                joint = UsdPhysics.Joint(prim)
                for child in joint.GetBody1Rel().GetTargets():
                    quaternion = joint.GetLocalRot1Attr().Get()
                    incoming_joints[str(child)] = {"joint_path": str(prim.GetPath()),
                        "joint_type": prim.GetTypeName(), "child_local_anchor_m_authored": list(joint.GetLocalPos1Attr().Get()),
                        "child_local_joint_quaternion_xyzw": list(quaternion.GetImaginary()) + [quaternion.GetReal()],
                        "note": "Authored frame; robot links have no calibration Cube scaling. Non-fixed axis conventions need separate validation."}
        topology["incoming_joint_frames_authored"] = incoming_joints
        topology["explicit_asset_root"] = args.asset_root
        topology["force_interpretation"] = "RAW reaction in incoming joint axes, about joint anchor; not world/link axes or TCP wrench"
        link8_indices = {side: list(art.link_paths[0]).index(f"/World/{side}_fr3/fr3_link8")
                         for side, art in articulations.items()}
        topology["candidate_carriage_frame"] = {
            "name": "carriage_entrance", "parent": "world", "approval": "PENDING",
            "position_m": [scene_values["entry_x"], 0.0, scene_values["table_top_z"]],
            "quaternion_xyzw": [0.0, 0.0, 0.0, 1.0]}
        # 当前 source 的固定 TCP 变换；记录出处，不把它默认为已冻结的 grasp 变换。
        topology["tool_tcp_offsets"] = {side: {
            "translation_link8_m": [0.0, sign * scene_values["tcp_y"], scene_values["vertical_drop_z"]],
            "quaternion_link8_xyzw": [0.0, 0.0, sign * 2 ** -0.5, 2 ** -0.5]}
            for side, sign in namespace["BRANCH_SIGN"].items()}
        (args.output_dir / "topology.json").write_text(json.dumps(topology, indent=2) + "\n", encoding="utf-8")
        print("[TASK01 full fixture] No pre-placed Cubes; raw articulation topology saved.", flush=True)

        with (args.output_dir / "physics_contact_samples.jsonl").open("w", encoding="utf-8") as stream:
            def post_step(dt):
                nonlocal snapshots, last_stamp, latest_snapshot
                try:
                    sample = pose_sampler.capture()
                    contacts = [sampler.capture(sample, float(dt)) for sampler in contact_samplers]
                    # 明确记录每个 link 的同一物理步 raw incoming；禁止当作接触估计器。
                    incoming = {side: {"link_poses_world_xyzw": np.array(art.get_link_transforms(), copy=True).tolist(),
                                       "incoming_joint_wrench_raw": np.array(
                                           art.get_link_incoming_joint_force(), copy=True).tolist()}
                                for side, art in articulations.items()}
                    tcp_poses = {}
                    for side in articulations:
                        link = np.array(incoming[side]["link_poses_world_xyzw"][0][link8_indices[side]])
                        x, y, z, w = link[3:] / np.linalg.norm(link[3:])
                        rotation = np.array([[1 - 2*(y*y + z*z), 2*(x*y - z*w), 2*(x*z + y*w)],
                            [2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w)],
                            [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)]])
                        offset = topology["tool_tcp_offsets"][side]
                        position = link[:3] + rotation @ np.array(offset["translation_link8_m"])
                        b = np.array(offset["quaternion_link8_xyzw"])
                        a = np.array([x, y, z, w])
                        quaternion = np.r_[a[3]*b[:3] + b[3]*a[:3] + np.cross(a[:3], b[:3]),
                                            a[3]*b[3] - np.dot(a[:3], b[:3])]
                        tcp_poses[side] = {"position_m": position.tolist(),
                                          "quaternion_xyzw": (quaternion / np.linalg.norm(quaternion)).tolist()}
                    row = {"physics": asdict(sample), "contacts": contacts, "articulations": incoming,
                           "tcp_poses_world_from_physics_link8": tcp_poses,
                           "feed_state": list(bridge.cube_state),
                           "suction_closed": {side: bool(g.is_closed()) for side, g in bridge.grippers.items()},
                           "reaction_note": "RAW incoming joint reaction includes body gravity/inertia and needs joint-frame/reference mapping; not TCP wrench"}
                    if args.record_calibration_phase:
                        row["calibration_phase"] = calibration_phase
                    stream.write(json.dumps(row, sort_keys=True) + "\n")
                    for measurement in contacts:
                        for pair in measurement["pairs"]:
                            key = pair["sensor_path"] + " <-> " + pair["other_path"]
                            peak_collision_force[key] = max(peak_collision_force.get(key, 0.0),
                                float(np.linalg.norm(pair["collision_force_world_n"])))
                    snapshots += 1
                    last_stamp = sample.stamp_ns
                    latest_snapshot = asdict(sample)
                except Exception as error:
                    errors.append(repr(error))
                    if len(errors) <= 3:
                        print("[TASK01 full fixture] MEASUREMENT ERROR: " + repr(error), flush=True)

            subscription = omni.physx.get_physx_interface().subscribe_physics_on_step_events(post_step, False, 200)
            started, ready, all_arrived_reported = time.monotonic(), False, False
            while not stopping and app.is_running() and time.monotonic() - started < args.duration_sec:
                app.update()
                if errors:
                    raise RuntimeError("Stopping measurement probe after readout errors")
                if not ready and bridge.cube_state[0] == namespace["STATE_ARRIVED"]:
                    ready = True
                    print("[TASK01 full fixture] READY: batch 1 feed settled; run first_batch:=1 max_batches:=5.", flush=True)
                    if args.verify_only:
                        break
                if ready and not all_arrived_reported and all(state == namespace["STATE_ARRIVED"] for state in bridge.cube_state):
                    print("[TASK01 full fixture] Five arrival flags set; waiting for controller's own PASS/HOME.", flush=True)
                    # 不靠到达标志提早结束；controller 还需要退出/HOME。
                    all_arrived_reported = True
            subscription.unsubscribe()
            subscription = None
        if not ready or snapshots == 0:
            raise RuntimeError("No batch-ready state or no valid measurement")
        summary = {"status": "PASS_READOUT_STARTUP" if args.verify_only and ready else "MEASUREMENT_COMPLETE",
                   "snapshots": snapshots, "errors": errors, "last_stamp_ns": last_stamp,
                   "final_feed_state": list(bridge.cube_state), "final_physics_snapshot": latest_snapshot,
                   "peak_pair_collision_force_n": peak_collision_force,
                   "notes": "Task completion must be taken from controller log; this is NOT paper/benchmark PASS."}
        (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("[TASK01 full fixture] " + json.dumps(summary, sort_keys=True), flush=True)
    except Exception as error:
        import traceback
        traceback.print_exc()
        (args.output_dir / "failure.json").write_text(json.dumps({"status": "FAIL", "error": repr(error),
            "traceback": traceback.format_exc()}, indent=2) + "\n", encoding="utf-8")
        raise
    finally:
        if subscription is not None:
            subscription.unsubscribe()
        if bridge is not None:
            bridge.shutdown()
        app.close()


if __name__ == "__main__":
    main()
