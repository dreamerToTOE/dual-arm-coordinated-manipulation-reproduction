"""[ENGINEERING] 用户批准的一次 bounded critical-state controlled replay。

仅 START / PRE_PUSH / state196 / TARGET，安全检查后 START/PRE 各5次reset。
复用原模型与记录14q，正常 simulate/fetch，不重建handle、不修query tree。
这是最低关键态安全证据，不是模型等价/全链/吸附稳定/力控证明。
"""
import argparse
import json
import math
import os
from pathlib import Path
import signal
import time
import traceback
import xml.etree.ElementTree as ET

from task01_single_cube_model_parity_gui import (
    SOURCE_SHA, ASSET_SHA, original_constructor_namespace, model_name,
    quat_angle, matrix_pose, transform_matrix, pure_rigid_matrix,
    native_query_hits, owning_body, sha, write_json,
)

CRITICAL = (("START", 0), ("PRE_PUSH", 135), ("FULL_CHAIN_MIN_STATE196_B60", 196), ("TARGET", 292))
ENV = {"table", "carriage_deep_wall", "carriage_minus_y_wall", "carriage_plus_y_wall"}
STATE_SHA = "607c30480ae264fd20ae4a09a750d5af6acb992d6d67c65a86103f86baa88d8e"
CONFIG_SHA = "3dbe7fcb192d09db83be801314582249ac3c0c77c9ffd683801ca7680d54881b"


def pair_classification(names, state, acm):
    """分类不扩充ACM；TARGET边界接触不自动算FAIL。"""
    pair = tuple(sorted(names))
    if names[0] == names[1]:
        return "EXPECTED_CONTACT", "same_original_model_link"
    if pair in acm:
        return "EXPECTED_CONTACT", "original_SRDF:" + acm[pair]
    if set(names) <= ENV:
        return "EXPECTED_CONTACT", "original_fixture_construction"
    if "shared_cube" in names:
        other = names[1] if names[0] == "shared_cube" else names[0]
        check = next((c for c in state["cube_environment_geometry"]["checks"] if c["body2"] == other), None)
        if check and not check["volumetric_penetration"] and check["signed_axis_aligned_distance_m"] <= 1e-12:
            return "EXPECTED_CONTACT", "nominal_cube_support_or_TARGET_boundary_pending_user_definition"
    return "UNEXPECTED_PAIR", "no_existing_expected_contact_definition"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not os.environ.get("DISPLAY"):
        parser.error("必须使用可见GUI，禁止headless fallback")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[3]
    source = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/isaac/scripts/task26_truck_box_scene.py")
    asset = root / "results/20261006_TASK01_held_fixture_diagnostic02/raw/fr3_official.usd"
    inputs = root / "results/20261007_TASK01_full_single_cube_geometry01"
    config_path = inputs / "config_at_run.yaml"
    state_path = inputs / "state_records.json"
    srdf = root / "results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf"
    for path, expected in ((source, SOURCE_SHA), (asset, ASSET_SHA), (config_path, CONFIG_SHA), (state_path, STATE_SHA)):
        if sha(path) != expected:
            raise RuntimeError("原输入hash变化，停止而非替换模型: " + str(path))
    import yaml
    config = yaml.safe_load(config_path.read_text())
    states = json.loads(state_path.read_text())
    if len(states) != 293 or any(s["status"] != "PASS_DISCRETE_GEOMETRY" or s["fcl"] != "PASS" for s in states):
        raise RuntimeError("不是已经记录的完整名义几何链")
    acm = {tuple(sorted((e.get("link1"), e.get("link2")))): e.get("reason")
           for e in ET.parse(srdf).getroot().findall("disable_collisions")}
    write_json(args.output_dir / "inputs.json", {
        "task": "TASK01", "scope": "bounded_critical_state_controlled_replay_fallback",
        "classification": "ENGINEERING", "critical_states": CRITICAL, "reset_repeats_per_state": 5,
        "source_sha256": sha(source), "asset_sha256": sha(asset), "config_sha256": sha(config_path),
        "states_sha256": sha(state_path), "srdf_sha256": sha(srdf), "probe_source_sha256": sha(__file__),
        "random_IK": False, "physics_parameters_changed": False, "ACM_changed": False,
        "controllers": 0, "suction_commands": 0, "wrench_calibration": False,
        "time_contract": "post_physics_step; sum of actual dt callbacks, not wall time; native clock also recorded",
        "reset_acceptance_tolerances": "PENDING_USER_REVIEW; report measured errors, never invent thresholds",
        "limit": "no full-chain PhysX replay/model equivalence/continuous safety/suction stability proof",
    })
    from isaacsim import SimulationApp
    app = SimulationApp({"headless": False, "width": 1280, "height": 960,
                         "multi_gpu": False, "sync_loads": False, "fast_shutdown": True})
    stopped = False
    def request_stop(signum, frame):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    accepted, reset_rows, completed_records = [], [], []
    current = None
    phase = "INITIALIZATION"
    post_events, contact_events, callback_errors = [], [], []
    subscriptions = []
    started = time.monotonic()
    try:
        import numpy as np
        import omni.physics.tensors as tensors
        import omni.physx
        import omni.timeline
        import omni.usd
        from pxr import Gf, PhysicsSchemaTools, PhysxSchema, Sdf, UsdGeom, UsdLux, UsdPhysics
        from isaacsim.core.utils.viewports import set_camera_view
        from isaacsim.core.nodes.bindings import _isaacsim_core_nodes
        from omni.kit.viewport.utility import capture_viewport_to_file, get_active_viewport
        timeline = omni.timeline.get_timeline_interface()
        timeline.stop()
        omni.usd.get_context().new_stage()
        stage = omni.usd.get_context().get_stage()
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(stage, 1.)
        stage.SetDefaultPrim(UsdGeom.Xform.Define(stage, "/World").GetPrim())
        scene = UsdPhysics.Scene.Define(stage, "/physicsScene")
        scene.GetGravityDirectionAttr().Set(Gf.Vec3f(0., 0., -1.))
        scene.GetGravityMagnitudeAttr().Set(9.81)
        api = PhysxSchema.PhysxSceneAPI.Apply(scene.GetPrim())
        api.CreateEnableCCDAttr().Set(True)
        api.CreateEnableStabilizationAttr().Set(True)
        api.CreateSolverTypeAttr().Set("TGS")
        api.CreateTimeStepsPerSecondAttr().Set(60)
        ns = original_constructor_namespace(source, stage, asset)
        for side in ("left", "right"):
            ns["_add_fr3"](f"/World/{side}_fr3", config["robots"][side]["base_at_rest_world_m"])
        for _ in range(20):
            app.update()  # timeline STOP，仅正常资产加载/UI
        ns["_apply_official_joint_limits"]()
        ns["_build_tool"]("/World/left_fr3", -1.)
        ns["_build_tool"]("/World/right_fr3", 1.)
        box = ns["_box"]
        box("/World/Table", config["table"]["center_world_m"], config["table"]["size_m"], (0., .65, .85))
        x0, x1 = config["carriage"]["interior_x_world_m"]
        y0, y1 = config["carriage"]["interior_y_world_m"]
        t, h = config["carriage"]["wall_thickness_m"], config["carriage"]["wall_height_m"]
        z = config["table"]["top_world_z_m"] + h / 2
        UsdGeom.Xform.Define(stage, "/World/Task01")
        UsdGeom.Xform.Define(stage, "/World/Task01/Carriage")
        box("/World/Task01/Carriage/WallDeep", (x1+t/2, (y0+y1)/2, z), (t, y1-y0+2*t, h), (.32,.4,.55))
        box("/World/Task01/Carriage/WallMinusY", ((x0+x1)/2, y0-t/2, z), (x1-x0+2*t, t, h), (.32,.4,.55))
        box("/World/Task01/Carriage/WallPlusY", ((x0+x1)/2, y1+t/2, z), (x1-x0+2*t, t, h), (.32,.4,.55))
        box("/World/Task01/Cube", states[0]["cube_center_world_m"], config["cube"]["size_m"], (.92,.62,.18), dynamic=True, gravity=True)
        entrance = UsdGeom.Xform.Define(stage, "/World/Task01/carriage_entrance")
        entrance.AddTranslateOp().Set(Gf.Vec3d(*config["frames"]["carriage_entrance"]["origin_world_m"]))
        UsdLux.DomeLight.Define(stage, "/World/PreviewLight").CreateIntensityAttr(1000.)
        set_camera_view(eye=[2.5,-2.2,1.8], target=[.8,0.,.35])
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                # 只开启原刚体接触遥测，不改力/材料/solver/geometry。
                PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.)
        shapes, models, owner_paths, tcp_local = [], {}, {}, {}
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.CollisionAPI) and UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Get():
                path = str(prim.GetPath())
                shapes.append(path)
                models[path] = model_name(path)
                owner = owning_body(prim, UsdPhysics)
                owner_paths[path] = str(owner.GetPath()) if owner else None
        for side in ("left", "right"):
            path = f"/World/{side}_fr3/fr3_link8"
            tcp = path + "/side_suction_tool/side_suction_tcp"
            tcp_local[side] = UsdGeom.Xformable(stage.GetPrimAtPath(tcp)).ComputeLocalToWorldTransform(0.) * pure_rigid_matrix(
                UsdGeom.Xformable(stage.GetPrimAtPath(path)).ComputeLocalToWorldTransform(0.), Gf).GetInverse()
        physx = omni.physx.get_physx_interface()
        sim_interface = omni.physx.get_physx_simulation_interface()
        core = _isaacsim_core_nodes.acquire_interface()
        def post_step(dt):
            post_events.append({"dt_s": float(dt), "native_step": int(core.get_physics_num_steps()),
                                "native_sim_time_s": float(core.get_sim_time())})
        def contact_report(headers, data):
            try:
                for header in headers:
                    shape_pair = [str(PhysicsSchemaTools.intToSdfPath(p)) for p in (header.collider0, header.collider1)]
                    points = [{"position_world_m": list(map(float, d.position)),
                               "normal_world": list(map(float, d.normal)), "separation_m": float(d.separation)}
                              for d in (data[i] for i in range(header.contact_data_offset,
                                        header.contact_data_offset+header.num_contact_data))]
                    contact_events.append({"shape_pair": shape_pair,
                        "body_pair": [str(PhysicsSchemaTools.intToSdfPath(p)) for p in (header.actor0, header.actor1)],
                        "event_type": int(header.type), "points": points})
            except Exception as error:
                callback_errors.append(repr(error))
        subscriptions.append(physx.subscribe_physics_on_step_events(post_step, False, 200))
        subscriptions.append(sim_interface.subscribe_contact_report_events(contact_report))
        # 一次正常原场景初始化，不释放/重建handle，不改变解析/碰撞query树。
        physx.force_load_physics_from_usd()
        physx.start_simulation()
        sim = tensors.create_simulation_view("numpy")
        sim.set_subspace_roots("/")
        arts = {side: sim.create_articulation_view(f"/World/{side}_fr3") for side in ("left", "right")}
        cube = sim.create_rigid_body_view("/World/Task01/Cube")
        for view in [*arts.values(), cube]:
            if view.count != 1 or not view.check():
                raise RuntimeError("原场景正常physics handle无效；本轮停止，不开发修复")
        write_json(args.output_dir / "scene_audit.json", {"models_by_enabled_shape": models, "owner_paths": owner_paths,
            "cube_mass_kg": np.array(cube.get_masses(), copy=True).tolist(),
            "cube_material": np.array(cube.get_material_properties(), copy=True).tolist(),
            "dt_s": 1/60, "gravity_m_s2": 9.81, "solver": "TGS", "CCD": True,
            "cube_dynamic": True, "cube_disable_gravity": False, "suction_constraints": 0,
            "physics_scene_attributes": {str(a.GetName()): str(a.Get()) for a in scene.GetPrim().GetAttributes()},
            "tool_local_to_link8_matrices": {s: np.asarray(m).tolist() for s,m in tcp_local.items()}})
        query = omni.physx.get_physx_scene_query_interface()
        focus = [p for p in shapes if models[p] == "shared_cube" or models[p].endswith(("_link7", "_link8", "_side_suction"))]
        idx = np.array([0], np.uint32)
        def observe(row):
            qout, body_poses = {}, {}
            for side, art in arts.items():
                names = list(art.shared_metatype.dof_names)
                selection = [names.index(f"fr3_joint{i}") for i in range(1, 8)]
                q = np.array(art.get_dof_positions(), copy=True)[0, selection]
                poses = np.array(art.get_link_transforms(), copy=True)[0]
                body_poses.update({p: tr.tolist() for p, tr in zip(art.link_paths[0], poses)})
                tcp = matrix_pose(tcp_local[side] * transform_matrix(body_poses[f"/World/{side}_fr3/fr3_link8"], Gf))
                expected = row["link_world_poses"][side+"_fr3_side_suction_tcp"]
                qout[side] = {"q_rad": q.tolist(), "joint_reset_error_rad": float(np.max(np.abs(q-row[side+"_q_rad"]))),
                    "tcp_pose_xyzw": tcp, "tcp_position_error_m": math.dist(tcp[:3], expected["translation_m"]),
                    "tcp_rotation_error_rad": quat_angle(tcp[3:], expected["quaternion_xyzw"])}
            cube_pose = np.array(cube.get_transforms(), copy=True)[0].tolist()
            # 明确原仿真传感器clock与actual-step-dt累计clock，绝不混入wall time。
            result = {"joint_state": qout, "cube_pose_xyzw": cube_pose,
                "cube_position_reset_error_m": math.dist(cube_pose[:3], row["cube_center_world_m"]),
                "cube_rotation_reset_error_rad": quat_angle(cube_pose[3:], row["cube_orientation_xyzw"]),
                "body_poses_xyzw": body_poses, "physics_step": len(post_events),
                "simulation_timestamp_s": math.fsum(e["dt_s"] for e in post_events),
                "simulation_clock_source": "actual PhysX post-step dt accumulator (manual normal simulate/fetch)",
                "native_core_step": int(core.get_physics_num_steps()), "native_core_sim_time_s": float(core.get_sim_time()),
                "carriage_frame_world_xyzw": matrix_pose(UsdGeom.Xformable(entrance).ComputeLocalToWorldTransform(0.))}
            numeric = [*cube_pose, *[v for s in qout.values() for v in s["q_rad"]+s["tcp_pose_xyzw"]]]
            if not all(math.isfinite(v) for v in numeric):
                raise RuntimeError("post-step状态非有限值")
            return result
        def replay(label, index, repeat=None):
            nonlocal current
            if stopped or time.monotonic()-started > 100:
                raise RuntimeError("bounded实验中断/预算截止，不自动追加尝试")
            row = states[index]
            current = {"label": label, "state_index": index, "segment": row["segment"],
                "segment_index": row["segment_index"], "reset_repeat": repeat,
                "requested_cube_pose_xyzw": row["cube_center_world_m"]+row["cube_orientation_xyzw"],
                "requested_14q_rad": {s: row[s+"_q_rad"] for s in arts}, "nominal_FCL": row["fcl"],
                "minimum_fcl_distance": row["minimum_fcl_distance"],
                "minimum_wrist_tool_environment_fcl_distance": row["minimum_wrist_tool_environment_fcl_distance"]}
            for side, art in arts.items():
                q = np.zeros_like(art.get_dof_positions())
                selection = [list(art.shared_metatype.dof_names).index(f"fr3_joint{i}") for i in range(1, 8)]
                q[0, selection] = row[side+"_q_rad"]
                art.set_dof_positions(q, idx)
                art.set_dof_position_targets(q, idx)
                art.set_dof_velocities(np.zeros_like(q), idx)
            cube.set_transforms(np.array([current["requested_cube_pose_xyzw"]], np.float32), idx)
            cube.set_velocities(np.zeros((1, 6), np.float32), idx)
            current["before_sync"] = observe(row)
            if (max(s["joint_reset_error_rad"] for s in current["before_sync"]["joint_state"].values()) > 1e-6 or
                    current["before_sync"]["cube_position_reset_error_m"] > 1e-6):
                raise RuntimeError("记录14q/Cube正常setter readback失败")
            contact_events.clear()
            steps_before = len(post_events)
            # 最小一次原dt正常物理同步；不改变dt，不在测量前再次写回pose。
            sim_interface.simulate(1/60, math.fsum(e["dt_s"] for e in post_events))
            sim_interface.fetch_results()
            physx.update_transformations(True, True)
            current["after_sync"] = observe(row)
            current["normal_sync_steps"] = len(post_events)-steps_before
            current["post_step_contacts"] = list(contact_events)
            current["unexpected_collision_evidence"] = []
            if current["normal_sync_steps"] != 1 or callback_errors:
                raise RuntimeError("实际post-step计数或contact回调无效；停止，不修集成层")
            before, after = current["before_sync"], current["after_sync"]
            current["measured_sync_drift"] = {
                "cube_translation_m": math.dist(before["cube_pose_xyzw"][:3], after["cube_pose_xyzw"][:3]),
                "cube_rotation_rad": quat_angle(before["cube_pose_xyzw"][3:], after["cube_pose_xyzw"][3:]),
                "max_joint_change_rad": max(math.dist([b], [a]) for s in arts for a,b in zip(
                    after["joint_state"][s]["q_rad"], before["joint_state"][s]["q_rad"])),
                "tcp_translation_m": {s: math.dist(before["joint_state"][s]["tcp_pose_xyzw"][:3],
                    after["joint_state"][s]["tcp_pose_xyzw"][:3]) for s in arts},
            }
            # 使用实际刚体姿态计算Cube边界，不把名义TARGET免责扩大为任意实际深穿透免责。
            cube_tf = transform_matrix(after["cube_pose_xyzw"], Gf)
            half = np.array(config["cube"]["size_m"])/2
            vertices = np.array([cube_tf.Transform(Gf.Vec3d(*map(float, half*np.array([i,j,k]))))
                                 for i in (-1,1) for j in (-1,1) for k in (-1,1)])
            lo, hi = vertices.min(axis=0), vertices.max(axis=0)
            current["actual_cube_environment_plane_gaps_m"] = {
                "table": float(lo[2]-config["table"]["top_world_z_m"]),
                "deep_wall": float(x1-hi[0]), "minus_y_wall": float(lo[1]-y0), "plus_y_wall": float(y1-hi[1]),
            }
            for report in current["post_step_contacts"]:
                if not report["points"]:
                    report["classification"] = "NO_CONTACT_LOST_EVENT"
                    continue
                names = [models[p] for p in report["shape_pair"]]
                classification, reason = pair_classification(names, row, acm)
                report.update({"model_pair": names, "classification": classification, "reason": reason})
                if classification == "UNEXPECTED_PAIR":
                    report["classification"] = "CONTACT_WITHOUT_PENETRATION" if all(p["separation_m"] >= 0 for p in report["points"]) else "UNEXPECTED_PENETRATION"
                    if report["classification"] == "UNEXPECTED_PENETRATION":
                        current["unexpected_collision_evidence"].append(report)
                        current["status"] = "UNEXPECTED_COLLISION_STOP"
                        write_json(args.output_dir / f"{phase.lower()}_{label}_{repeat or 0}.json", current)
                        raise RuntimeError("明确非预期contact penetration，立即停止，等待用户决定")
            # 同步后的原shape overlap仅关注腕/工具/Cube vs原环境；不做query-tree修复或等价证明。
            current["focus_overlap_queries"] = []
            for p in focus:
                encoded = PhysicsSchemaTools.encodeSdfPath(Sdf.Path(p))
                result = native_query_hits(lambda callback: query.overlap_shape(encoded[0], encoded[1], callback, False), set(shapes), p)
                current["focus_overlap_queries"].append(result)
                if "error" in result:
                    raise RuntimeError("原overlap调用失败，本轮停止而非修复")
                for hit in result["hits"]:
                    if models[hit["collision"]] not in ENV:
                        continue
                    names = [models[p], models[hit["collision"]]]
                    classification, reason = pair_classification(names, row, acm)
                    hit.update({"model_pair": names, "classification": classification, "reason": reason})
                    if classification == "UNEXPECTED_PAIR":
                        current["unexpected_collision_evidence"].append({"source_shape": p, **hit, "source": "original_PhysX_overlap_shape_after_normal_step"})
                        current["status"] = "UNEXPECTED_COLLISION_STOP"
                        write_json(args.output_dir / f"{phase.lower()}_{label}_{repeat or 0}.json", current)
                        raise RuntimeError("明确非预期原shape overlap，立即停止，等待用户决定")
            current["status"] = "UNEXPECTED_COLLISION_STOP" if current["unexpected_collision_evidence"] else "NO_UNEXPECTED_COLLISION_OBSERVED"
            write_json(args.output_dir / f"{phase.lower()}_{label}_{repeat or 0}.json", current)
            completed_records.append(current)
            print(f"TASK01 {phase} {label} state={index} step={len(post_events)} status={current['status']}", flush=True)
            if current["unexpected_collision_evidence"]:
                raise RuntimeError("明确非预期Isaac碰撞，立即停止，等待用户决定")
            # 不编造动态reset门限。四关键态及每组首次reset必须由执行者审阅
            # 已保存post-step漂移/actual Cube边界，再决定此态是否仍具有几何代表性。
            # 不显著漂移/实际边界无法确认时STOP，不自动推进为PASS。
            if phase == "CRITICAL" or repeat == 1:
                print("TASK01 SAME-STEP REVIEW " + json.dumps({
                    "state": label, "measured_sync_drift": current["measured_sync_drift"],
                    "actual_cube_environment_plane_gaps_m": current["actual_cube_environment_plane_gaps_m"],
                    "after_sync": {k:v for k,v in after.items() if k != "body_poses_xyzw"},
                    "contact_point_separations_m": [{"pair": c["shape_pair"], "classification": c["classification"],
                        "separations": [p["separation_m"] for p in c["points"]]} for c in current["post_step_contacts"]],
                }), flush=True)
                decision = input("REVIEW: type accept_snapshot or stop (no new benchmark tolerance): ").strip()
                current["execution_review_decision"] = decision
                write_json(args.output_dir / f"{phase.lower()}_{label}_{repeat or 0}.json", current)
                if decision != "accept_snapshot":
                    raise RuntimeError("post-step漂移/边界接触执行审阅未接受，停止并报告用户")
            capture_viewport_to_file(get_active_viewport(), str(args.output_dir / f"{phase.lower()}_{label}_{repeat or 0}.png"))
            # timeline仍STOP，原renderer只显示刚完成的同步状态，无后续运动。
            app.update()
            if len(post_events) != steps_before+1:
                raise RuntimeError("显示刷新新增非受控步，停止")
            return current
        phase = "CRITICAL"
        for label, index in CRITICAL:
            replay(label, index)
            accepted.append(label)
        phase = "RESET"
        for label, index in CRITICAL[:2]:
            for repeat in range(1, 6):
                reset_rows.append(replay(label, index, repeat))
        write_json(args.output_dir / "summary.json", {"status": "SAFETY_AND_DETERMINISTIC_RESET_EVIDENCE_REVIEW_REQUIRED",
            "critical_states_accepted": accepted, "resets_recorded": len(reset_rows), "physics_steps": post_events,
            "reset_records": [str(p.name) for p in args.output_dir.glob("reset_*.json")],
            "reset_thresholds": "PENDING_USER_REVIEW", "suction_stability": "NOT_TESTED",
            "FROZEN": False, "wall_runtime_s_engineering_only": time.monotonic()-started})
    except Exception as error:
        write_json(args.output_dir / "failure.json", {"status": "UNEXPECTED_COLLISION_STOP" if current and current.get("unexpected_collision_evidence") else "BOUNDED_FALLBACK_ENGINEERING_STOP",
            "error": repr(error), "traceback": traceback.format_exc(), "phase": phase, "critical_states_accepted": accepted,
            "resets_recorded": len(reset_rows), "current": current, "post_step_events": post_events,
            "contact_callback_errors": callback_errors, "no_next_attempt_authorized": True})
        print("TASK01 FALLBACK STOP:", repr(error), flush=True)
    finally:
        for sub in subscriptions:
            if hasattr(sub, "unsubscribe"):
                sub.unsubscribe()
        app.close()


if __name__ == "__main__":
    main()
