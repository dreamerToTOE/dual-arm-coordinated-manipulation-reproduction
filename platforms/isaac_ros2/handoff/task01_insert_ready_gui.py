"""[ENGINEERING] One bounded visible integration of D039, ending at INSERT_READY.

Reuse original scene constructors, Task26 SG/joint/rail methods and existing
post-step sampler. No five-Cube app, push-to-TARGET, force/drive/material tuning,
new attachment mechanism, parity/query-tree work or automatic second launch.
"""
import argparse
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "platforms/isaac_ros2"))
sys.path.insert(0, str(ROOT / "platforms/isaac_ros2/probes"))
from task01_single_cube_model_parity_gui import (
    original_constructor_namespace, SOURCE_SHA, ASSET_SHA, sha, write_json,
    model_name, matrix_pose, transform_matrix, quat_angle,
)
from physics_object_sampler import PhysicsObjectSampler
from fixture_geometry_stream import geometry_poses
from reused_bridge import build_bridge


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/benchmark/benchmark_v1.yaml")
    parser.add_argument("--moveit-launch", type=Path, default=Path(__file__).with_name("moveit_handoff.launch.py"))
    parser.add_argument("--driver-binary", type=Path, default=ROOT / "build/task01_handoff/task01_rear_handoff")
    parser.add_argument("--wall-limit-sec", type=float, default=180.)
    parser.add_argument("--reset-repeats", type=int, default=2)
    args = parser.parse_args()
    if not os.environ.get("DISPLAY"):
        parser.error("Visible GUI is required; no headless fallback")
    if not 0 <= args.reset_repeats <= 2 or not 0 < args.wall_limit_sec <= 180:
        parser.error("Bounded single integration: at most two recorded-state restores, 180 s")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    import yaml
    config = yaml.safe_load(args.config.read_text())
    station = config["robots"]["rail_state_candidates"]
    if (station["A_and_pre_push_shared"]["left_x_world_m"] != .650 or
            station["INSERT_READY"]["left_x_world_m"] != .750 or
            station["INSERT_READY"]["right_x_world_m"] != .750):
        raise RuntimeError("Only the approved fixed rail handoff is allowed")
    source = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/isaac/scripts/task26_truck_box_scene.py")
    asset = ROOT / "results/20261006_TASK01_held_fixture_diagnostic02/raw/fr3_official.usd"
    srdf = ROOT / "results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf"
    for path, expected in ((source, SOURCE_SHA), (asset, ASSET_SHA)):
        if sha(path) != expected:
            raise RuntimeError("Original model/constructor source changed: " + str(path))
    write_json(args.output_dir / "inputs.json", {
        "task": "TASK01", "scope": "single_cube_fixed_handoff_to_INSERT_READY_only",
        "config_path": str(args.config), "config_sha256": sha(args.config),
        "source_sha256": sha(source), "asset_sha256": sha(asset), "srdf_sha256": sha(srdf),
        "gui_source_sha256": sha(__file__), "seed": 0, "attempt": "1/1",
        "git_commit": subprocess.check_output(["git","-C",str(ROOT),"rev-parse","HEAD"],text=True).strip(),
        "driver_sha256": sha(args.driver_binary), "launch_sha256": sha(args.moveit_launch),
        "wall_limit_sec_engineering_only": args.wall_limit_sec,
        "recorded_state_restore_cap": args.reset_repeats, "headless": False,
        "TARGET_execution": False, "force_calibration": False, "FROZEN": False,
        "time_contract": "one live PhysX post-step stamp; wall time only for deadline",
    })
    started = time.monotonic()
    stopped = False
    def stop_signal(signum, frame):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGTERM, stop_signal)
    signal.signal(signal.SIGINT, stop_signal)
    app = bridge = process = stream = contact_stream = ros_log = None
    exit_code = 1
    subscriptions, errors, contacts, resets = [], [], [], []
    latest, captured = {}, None
    planning = {"refreshed": False, "generation": 0, "world_shift_x_m": None}
    capture_requested = False
    initial_ready = False
    phase = "INITIALIZATION"
    try:
        from isaacsim import SimulationApp
        app = SimulationApp({"headless": False, "width": 1280, "height": 960,
                             "multi_gpu": False, "sync_loads": False, "fast_shutdown": True})
        import numpy as np
        import omni.physx
        import omni.timeline
        import omni.usd
        from pxr import Gf, PhysicsSchemaTools, PhysxSchema, UsdGeom, UsdLux, UsdPhysics
        from isaacsim.core.prims import RigidPrim, SingleArticulation
        from isaacsim.core.simulation_manager import SimulationManager
        from isaacsim.core.utils.extensions import enable_extension
        from isaacsim.core.utils.viewports import set_camera_view
        # 先启用 Isaac 自带 Humble 模块，不依赖系统 rclpy。
        enable_extension("isaacsim.ros2.bridge")
        from rosgraph_msgs.msg import Clock
        from sensor_msgs.msg import JointState
        from std_msgs.msg import Bool, String
        timeline = omni.timeline.get_timeline_interface()
        timeline.stop()
        enable_extension("isaacsim.robot.surface_gripper")
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
            app.update()  # STOP timeline: asset/UI loading, no controller
        ns["_apply_official_joint_limits"]()
        for side, sign in (("left", -1.), ("right", 1.)):
            ns["_build_tool"](f"/World/{side}_fr3", sign)
        box = ns["_box"]
        box("/World/Table", config["table"]["center_world_m"], config["table"]["size_m"], (0., .65, .85))
        x0, x1 = config["carriage"]["interior_x_world_m"]
        y0, y1 = config["carriage"]["interior_y_world_m"]
        t, h = config["carriage"]["wall_thickness_m"], config["carriage"]["wall_height_m"]
        z = config["table"]["top_world_z_m"] + h/2
        UsdGeom.Xform.Define(stage, "/World/Task01")
        UsdGeom.Xform.Define(stage, "/World/Task01/Carriage")
        box("/World/Task01/Carriage/WallDeep", (x1+t/2, 0., z), (t, y1-y0+2*t, h), (.32,.4,.55))
        for label, yy in (("MinusY", y0-t/2), ("PlusY", y1+t/2)):
            box(f"/World/Task01/Carriage/Wall{label}", ((x0+x1)/2, yy, z),
                (x1-x0+2*t, t, h), (.32,.4,.55))
        pre = config["benchmarks"]["handoff_pre_push_to_insert_ready"]["start_cube_center_world_m"]
        box("/World/Task01/Cube", pre, config["cube"]["size_m"], (.92,.62,.18), dynamic=True, gravity=True)
        entrance = UsdGeom.Xform.Define(stage, "/World/Task01/carriage_entrance")
        entrance.AddTranslateOp().Set(Gf.Vec3d(*config["frames"]["carriage_entrance"]["origin_world_m"]))
        carriage_pose = matrix_pose(entrance.ComputeLocalToWorldTransform(0.))
        UsdLux.DomeLight.Define(stage, "/World/PreviewLight").CreateIntensityAttr(1000.)
        set_camera_view(eye=[2.5,-2.2,1.8], target=[.8,0.,.35])
        models = {}
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.)
            if prim.HasAPI(UsdPhysics.CollisionAPI) and UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Get():
                models[str(prim.GetPath())] = model_name(str(prim.GetPath()))
        acm = {tuple(sorted((e.get("link1"),e.get("link2")))) for e in ET.parse(srdf).getroot().findall("disable_collisions")}
        physx = omni.physx.get_physx_interface()
        sim_interface = omni.physx.get_physx_simulation_interface()
        def on_contact(headers, data):
            try:
                for header in headers:
                    paths = [str(PhysicsSchemaTools.intToSdfPath(v)) for v in (header.collider0,header.collider1)]
                    points = [{"position_world_m": list(map(float,d.position)), "separation_m": float(d.separation)}
                              for d in (data[i] for i in range(header.contact_data_offset,
                                        header.contact_data_offset+header.num_contact_data))]
                    contacts.append({"shape_pair": paths, "model_pair": [models[p] for p in paths], "points": points})
            except Exception as error:
                errors.append("contact_callback:"+repr(error))
        subscriptions.append(sim_interface.subscribe_contact_report_events(on_contact))
        # 4.5 prims.initialize() 使用正常 PLAY/warm-start 的 SimulationManager。
        # 这是既有 SDK 启动同步，不做 zero-step/native-handle/query-tree 修复。
        timeline.play()
        for _ in range(3):
            app.update()
            if SimulationManager.get_physics_sim_view() is not None:
                break
        timeline.pause()  # STOP 会使正常 SDK view 失效；之后只做明确的受控步。
        sim = SimulationManager.get_physics_sim_view()
        if sim is None:
            raise RuntimeError("Normal SDK physics warm-start failed; no second launch")
        arts = {s: sim.create_articulation_view(f"/World/{s}_fr3") for s in ("left","right")}
        cube = sim.create_rigid_body_view("/World/Task01/Cube")
        idx = np.array([0],np.uint32)
        selections = {s: [list(a.shared_metatype.dof_names).index(f"fr3_joint{i}") for i in range(1,8)] for s,a in arts.items()}
        def restore(qvalues, cube_pose):
            for side, art in arts.items():
                q = np.zeros_like(art.get_dof_positions())
                q[0,selections[side]] = qvalues[side]
                art.set_dof_positions(q,idx)
                art.set_dof_position_targets(q,idx)
                art.set_dof_velocities(np.zeros_like(q),idx)
            cube.set_transforms(np.array([cube_pose],np.float32),idx)
            cube.set_velocities(np.zeros((1,6),np.float32),idx)
        restore(config["robots"]["pre_push_shared_joint_state_rad"], list(pre)+[0.,0.,0.,1.])
        articulations = {s: SingleArticulation(prim_path=f"/World/{s}_fr3",name=f"task01_{s}") for s in arts}
        for art in articulations.values():
            art.initialize(physics_sim_view=sim)
        bridge = build_bridge(stage,articulations,config)
        view = RigidPrim(["/World/Task01/Cube","/World/left_fr3/fr3_link8","/World/right_fr3/fr3_link8"],
                         reset_xform_properties=False,prepare_contact_sensors=False)
        view.initialize(physics_sim_view=sim)
        sampler = PhysicsObjectSampler(view)
        scene_values = {"branch_sign":{"left":-1.,"right":1.},"tcp_y":.155,"vertical_drop_z":.080}
        node = bridge.node
        joint_pub = node.create_publisher(JointState,"/joint_states",20)
        clock_pub = node.create_publisher(Clock,"/clock",20)
        snapshot_pub = node.create_publisher(String,"/task01/ready_snapshot",10)
        def on_ack(message):
            nonlocal planning
            try:
                ack = json.loads(message.data)
                if ack["world_shift_x_m"] not in (0.,.100) or not ack["refreshed"]:
                    raise RuntimeError("Invalid fixed planning-world ACK")
                planning = ack
            except Exception as error:
                errors.append("planning_ack:"+repr(error))
        def on_capture(message):
            nonlocal capture_requested
            capture_requested = bool(message.data)
        bridge.subscriptions.append(node.create_subscription(String,"/task01/planning_world_ack",on_ack,10))
        bridge.subscriptions.append(node.create_subscription(Bool,"/task01/capture_insert_ready",on_capture,10))
        stream = (args.output_dir/"post_step_states.jsonl").open("w")
        contact_stream = (args.output_dir/"post_step_contacts.jsonl").open("w")
        def on_post_step(dt):
            nonlocal latest,captured
            try:
                sample = sampler.capture()
                poses = geometry_poses(sample,("/World/Task01/Cube",),scene_values)
                pose7 = lambda p: list(p["position_m"])+list(p["quaternion_xyzw"])
                bases = {s:np.array(a.get_root_transforms(),copy=True)[0].tolist() for s,a in arts.items()}
                qout = {s:np.array(a.get_dof_positions(),copy=True)[0,selections[s]].tolist() for s,a in arts.items()}
                shift = sum(b[0] for b in bases.values())/2-.650
                pp = dict(planning)
                pp["refreshed"] = bool(pp.get("refreshed") and abs(shift-pp["world_shift_x_m"]) <= .001)
                cp,tp = pose7(poses[0]),{s:pose7(p) for s,p in zip(("left","right"),poses[1:])}
                relative = matrix_pose(transform_matrix(tp["right"],Gf)*transform_matrix(cp,Gf).GetInverse())
                latest = {"schema_version":1,"physics_step":sample.physics_step,"simulation_stamp_ns":sample.stamp_ns,
                    "frame_id":"world","phase":phase,"handoff_initial_ready":initial_ready,
                    "rails":{s:{"measured_x_m":bases[s][0],"arrived":bool(bridge.rail_arrived[s])} for s in arts},
                    "bases":bases,"joints":qout,"cube_pose_xyzw":cp,"tcp_poses":tp,
                    "suction":{"left_closed":bool(bridge.grippers["left"].is_closed()),"right_closed":bool(bridge.grippers["right"].is_closed())},
                    "world_shift_x_m":shift,"planning_world":pp,
                    "attachment":{"right":bridge.attachment_identity("right"),
                        "relative_transform_cube_to_right_tcp_xyzw":relative,
                        "relative_transform_source":"same_post_step_physics_pose_relative_transform_not_joint_anchor"},
                    "helper_park":{"label":pp.get("helper_park_label","NOT_YET_PARKED"),"actual_q_rad":qout["left"],"actual_tcp_pose_xyzw":tp["left"]},
                    "carriage_frame_world_xyzw":carriage_pose,"insert_ready_captured":captured is not None,
                    "physics_snapshot":asdict(sample)}
                clock = Clock()
                clock.clock.sec,clock.clock.nanosec = divmod(sample.stamp_ns,1_000_000_000)
                clock_pub.publish(clock)
                msg = JointState()
                msg.header.stamp = clock.clock
                for side in arts:
                    msg.name.extend(f"{side}_fr3_joint{i}" for i in range(1,8))
                    msg.position.extend(qout[side])
                joint_pub.publish(msg)
                if capture_requested and captured is None:
                    if (latest["suction"]["left_closed"] or not latest["suction"]["right_closed"] or
                            any(abs(b[0]-.750)>.001 for b in bases.values()) or not pp["refreshed"] or
                            pp.get("world_shift_x_m") != .100):
                        raise RuntimeError("INSERT_READY capture gate invalid: SG/rail/refreshed world")
                    captured = json.loads(json.dumps(latest))
                    captured["insert_ready_captured"] = True
                    latest["insert_ready_captured"] = True
                    write_json(args.output_dir/"insert_ready_candidate.json",captured)
                snapshot_pub.publish(String(data=json.dumps(latest,allow_nan=False)))
                stream.write(json.dumps(latest,allow_nan=False)+"\n")
            except Exception as error:
                errors.append("post_step:"+repr(error))
        write_json(args.output_dir/"scene_audit.json",{
            "models_by_enabled_shape":models,"cube_mass_kg":np.array(cube.get_masses(),copy=True).tolist(),
            "cube_material":np.array(cube.get_material_properties(),copy=True).tolist(),
            "physics_scene_attributes":{str(a.GetName()):str(a.Get()) for a in scene.GetPrim().GetAttributes()},
            "source":bridge.provenance,"changes":"only approved rail targets; original geometry/physics preserved"})
        def step():
            if stopped or time.monotonic()-started >= args.wall_limit_sec-15:
                raise RuntimeError("Bounded integration deadline; no retry")
            contacts.clear()
            bridge.pre_step(1/60)
            stamp = float(sampler.core.get_sim_time())
            sim_interface.simulate(1/60,stamp)
            sim_interface.fetch_results()
            physx.update_transformations(True,True)
            # fetch 完成后取同一次 native post-step；不从 wall/旧USD拼接。
            on_post_step(1/60)
            if errors or bridge.halted:
                raise RuntimeError("Interface STOP: "+repr(errors+bridge.errors))
            contact_stream.write(json.dumps({"phase":phase,"physics_step":latest["physics_step"],
                "simulation_stamp_ns":latest["simulation_stamp_ns"],"contacts":contacts},allow_nan=False)+"\n")
            for contact in contacts:
                a,b = contact["model_pair"]
                pair = tuple(sorted((a,b)))
                expected = a == b or pair in acm or set(pair) <= {"table","carriage_deep_wall","carriage_minus_y_wall","carriage_plus_y_wall"}
                if "shared_cube" in pair:
                    other = b if a == "shared_cube" else a
                    # 只有杯面是预期接触；L杆/歧管穿入Cube仍首败即停。
                    expected = other == "table" or any("/side_suction_tool/cup_r" in p for p in contact["shape_pair"])
                if not expected and any(p["separation_m"] < 0 for p in contact["points"]):
                    write_json(args.output_dir/"unexpected_collision.json",{"phase":phase,"snapshot":latest,"contact":contact})
                    raise RuntimeError("Unexpected physical penetration: "+str(contact["shape_pair"]))
            app.update()
        phase = "PRE_PUSH_INITIAL_SHARED_HOLD"
        step()  # 正常最小同步，Cube已在支持面；不是 free airborne READY。
        for side in arts:
            bridge._command(side,Bool(data=True))
        for _ in range(60):
            step()
            if latest["suction"]["left_closed"] and latest["suction"]["right_closed"]:
                break
        else:
            raise RuntimeError("Existing bilateral SG did not close at PRE_PUSH; STOP")
        for _ in range(10):
            step()
        if (not all(latest["suction"].values()) or math.dist(latest["cube_pose_xyzw"][:3],pre)>.005):
            raise RuntimeError("PRE_PUSH shared-held initialization failed; not a valid handoff start")
        initial_ready = True
        step()
        write_json(args.output_dir/"pre_push_shared_sample.json",latest)
        phase = "FIXED_HANDOFF"
        ros_log = (args.output_dir/"moveit_driver.log").open("w")
        command = ("source /opt/ros/humble/setup.bash\n"
                   "source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash\n"
                   "exec ros2 launch \""+str(args.moveit_launch)+"\" "
                   "benchmark_config:=\""+str(args.config)+"\" driver:=\""+str(args.driver_binary)+"\"")
        process = subprocess.Popen(["/bin/bash","--noprofile","--norc","-c",command],
            stdout=ros_log,stderr=subprocess.STDOUT,start_new_session=True,
            env={k:v for k,v in os.environ.items() if k not in ("LD_LIBRARY_PATH","PYTHONPATH","AMENT_PREFIX_PATH","COLCON_PREFIX_PATH","CMAKE_PREFIX_PATH")})
        write_json(args.output_dir/"owned_process.json",{"launch_pid":process.pid,"launch_process_group":process.pid})
        while captured is None:
            if process.poll() is not None:
                raise RuntimeError(f"MoveIt/driver exited before capture: {process.returncode}; inspect moveit_driver.log")
            step()
        # 停止控制进程后只做既有 candidate 的两次相同状态恢复，不重新规划。
        # 给driver机会消费capture ACK并退出；launch的OnProcessExit收尾自身进程。
        finish_deadline = time.monotonic()+8
        while process.poll() is None:
            if time.monotonic()>finish_deadline:
                raise RuntimeError("Captured but owned MoveIt launch did not finish; STOP")
            step()
        if process.returncode != 0:
            raise RuntimeError("Owned MoveIt launch failed after capture")
        seed = captured
        for repeat in range(1,args.reset_repeats+1):
            phase = f"INSERT_READY_RESTORE_{repeat}"
            for side in arts:
                bridge._command(side,Bool(data=False))
            for _ in range(5):
                step()
            if any(g.is_closed() for g in bridge.grippers.values()):
                raise RuntimeError("OPEN failed before deterministic INSERT_READY restore")
            restore(seed["joints"],seed["cube_pose_xyzw"])
            sampler = PhysicsObjectSampler(view)
            step()
            bridge._command("right",Bool(data=True))
            for _ in range(30):
                step()
                if bridge.grippers["right"].is_closed():
                    break
            else:
                raise RuntimeError("Right existing SG reset attachment failed")
            for _ in range(10):
                step()
            if bridge.grippers["left"].is_closed():
                raise RuntimeError("Unexpected left attachment in INSERT_READY")
            record = {"repeat":repeat,"snapshot":latest,
                "q_reset_max_error_rad":{s:max(abs(a-b) for a,b in zip(latest["joints"][s],seed["joints"][s])) for s in arts},
                "cube_reset_translation_error_m":math.dist(latest["cube_pose_xyzw"][:3],seed["cube_pose_xyzw"][:3]),
                "cube_reset_rotation_error_rad":quat_angle(latest["cube_pose_xyzw"][3:],seed["cube_pose_xyzw"][3:]),
                "tcp_reset_translation_error_m":{s:math.dist(latest["tcp_poses"][s][:3],seed["tcp_poses"][s][:3]) for s in arts},
                "scientific_acceptance_thresholds":"PENDING_USER_FREEZE_REVIEW"}
            resets.append(record)
            write_json(args.output_dir/f"insert_ready_restore_{repeat}.json",record)
            if record["cube_reset_translation_error_m"]>.005 or max(record["q_reset_max_error_rad"].values())>.01:
                raise RuntimeError("Repeat restore violates explicit engineering drift guard; STOP")
        write_json(args.output_dir/"summary.json",{"task":"TASK01","status":"INSERT_READY_CANDIDATE_CAPTURED_REVIEW_REQUIRED",
            "task01_status":"PARTIAL","candidate":captured,"restore_records":resets,
            "TARGET":"NOT_RUN","FROZEN":False,"attempt":"1/1","post_step_source":"live PhysX",
            "wall_runtime_s_engineering_only":time.monotonic()-started})
        print("TASK01 INSERT_READY candidate captured; TASK01 PARTIAL / NOT FROZEN",flush=True)
        exit_code = 0
    except Exception as error:
        write_json(args.output_dir/"failure.json",{"task":"TASK01","status":"BOUNDED_INTEGRATION_STOP",
            "phase":phase,"error":repr(error),"traceback":traceback.format_exc(),"latest_snapshot":latest,
            "captured":captured,"restore_records":resets,"callback_errors":errors,"attempt":"1/1",
            "no_second_attempt_authorized":True,"task01_status":"PARTIAL","FROZEN":False})
        print("TASK01 HANDOFF STOP:",repr(error),flush=True)
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid,signal.SIGINT)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL)
                process.wait(timeout=2)
        for sub in subscriptions:
            sub.unsubscribe()
        if stream:
            stream.close()
        if contact_stream:
            contact_stream.close()
        if ros_log:
            ros_log.close()
        if bridge:
            bridge.shutdown()
        if app:
            app.close()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
