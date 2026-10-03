"""Isolate TASK01 PhysX/USD pose timing and scaled-quaternion errors in Isaac 4.5.

The free rigid body is an EXPERIMENTAL sensor calibration fixture. It changes
neither Task27 geometry nor its controller, and does not prove contact behavior.
Run with Isaac's python.sh; JSONL captures are written only as run artifacts.
"""

import argparse
import json
import math
import sys
from pathlib import Path


def quaternion_angle_deg(first, second):
    norms = math.sqrt(sum(v * v for v in first) * sum(v * v for v in second))
    if norms < 1e-12:
        raise ValueError("Cannot compare zero quaternion")
    cosine = abs(sum(a * b for a, b in zip(first, second))) / norms
    return math.degrees(2.0 * math.acos(min(1.0, cosine)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--physics-dt", type=float, default=1.0 / 60.0)
    parser.add_argument("--rendering-dt", type=float, default=1.0 / 30.0)
    parser.add_argument("--motion-steps", type=int, default=120)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--enable-ros", action="store_true")
    args = parser.parse_args()
    if args.physics_dt <= 0 or args.rendering_dt <= 0 or args.motion_steps < 10:
        parser.error("dt must be positive and motion-steps must be >= 10")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    from isaacsim import SimulationApp
    app = SimulationApp({"headless": True, "multi_gpu": False,
                         "sync_loads": False, "fast_shutdown": True})
    subscriptions = []
    physics_publisher = node = ros_context = None
    try:
        import numpy as np
        import omni.physx
        import omni.usd
        from pxr import Gf, PhysxSchema, Usd, UsdGeom, UsdPhysics
        from isaacsim.core.api import World
        from isaacsim.core.prims import RigidPrim, SingleRigidPrim
        from isaacsim.core.nodes.bindings import _isaacsim_core_nodes

        omni.usd.get_context().new_stage()
        if args.enable_ros:
            import omni.kit.app
            omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
                "isaacsim.ros2.bridge", True)
        world = World(physics_dt=args.physics_dt, rendering_dt=args.rendering_dt,
                      stage_units_in_meters=1.0)
        stage = omni.usd.get_context().get_stage()
        cube = UsdGeom.Cube.Define(stage, "/World/ProbeCube")
        cube.CreateSizeAttr(1.0)
        transform = UsdGeom.Xformable(cube.GetPrim())
        transform.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, 1.0))
        transform.AddOrientOp().Set(Gf.Quatf(Gf.Rotation(Gf.Vec3d(0, 0, 1), 7).GetQuat()))
        transform.AddScaleOp().Set(Gf.Vec3f(0.12, 0.12, 0.12))
        UsdPhysics.RigidBodyAPI.Apply(cube.GetPrim())
        UsdPhysics.CollisionAPI.Apply(cube.GetPrim())
        UsdPhysics.MassAPI.Apply(cube.GetPrim()).CreateMassAttr(0.8)
        body_api = PhysxSchema.PhysxRigidBodyAPI.Apply(cube.GetPrim())
        body_api.CreateDisableGravityAttr(True)
        # 已知匀速校准必须显式关闭默认角阻尼，否则期望角度模型不成立。
        body_api.CreateLinearDampingAttr(0.0)
        body_api.CreateAngularDampingAttr(0.0)
        world.reset()
        rigid = SingleRigidPrim("/World/ProbeCube")
        rigid.initialize()
        for _ in range(5):
            world.step(render=True)
        if args.enable_ros:
            import omni.graph.core as og
            import rclpy
            import geometry_msgs
            from rclpy.context import Context
            from rclpy.qos import QoSProfile, DurabilityPolicy
            from std_msgs.msg import String
            sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
            from physics_object_sampler import PhysicsObjectSampler, PhysicsPosePublisher
            print(f"[TASK01 ROS origins] rclpy={rclpy.__file__} geometry_msgs={geometry_msgs.__file__}",
                  flush=True)
            if "/opt/ros/" in str(rclpy.__file__) or "/opt/ros/" in str(geometry_msgs.__file__):
                raise RuntimeError("Use scripts/run_isaac_bundled_ros.sh to avoid mixed system/internal ROS")

            og.Controller.edit(
                {"graph_path": "/ClockGraph", "evaluator_name": "execution"}, {
                    og.Controller.Keys.CREATE_NODES: [
                        ("Tick", "omni.graph.action.OnPlaybackTick"),
                        ("Time", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                        ("Clock", "isaacsim.ros2.bridge.ROS2PublishClock")],
                    og.Controller.Keys.CONNECT: [
                        ("Tick.outputs:tick", "Clock.inputs:execIn"),
                        ("Time.outputs:simulationTime", "Clock.inputs:timeStamp")],
                    og.Controller.Keys.SET_VALUES: [("Time.inputs:resetOnStop", True),
                                                    ("Clock.inputs:topicName", "/clock")],
                })
            ros_context = Context()
            rclpy.init(context=ros_context)
            node = rclpy.create_node("task01_physics_calibration", context=ros_context)
            calibration_pub = node.create_publisher(
                String, "/task01/physics/calibration",
                QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
            view = RigidPrim("/World/ProbeCube", reset_xform_properties=False,
                             prepare_contact_sensors=False)
            view.initialize()
            # Warm DDS discovery before starting the known-motion interval.
            for _ in range(30):
                world.step(render=True)
            physics_publisher = PhysicsPosePublisher(node, PhysicsObjectSampler(view))
        core = _isaacsim_core_nodes.acquire_interface()
        rows, callback_errors = [], []
        phase = "motion"
        baseline_time = float(core.get_sim_time())
        initial_position, _ = rigid.get_world_pose()
        initial_position = tuple(float(v) for v in initial_position)
        _, initial_wxyz = rigid.get_world_pose()
        if args.enable_ros:
            calibration = String()
            calibration.data = json.dumps({
                "baseline_time_s": baseline_time, "initial_position_m": initial_position,
                "initial_quaternion_xyzw": [float(initial_wxyz[i]) for i in (1, 2, 3, 0)],
                "linear_velocity_m_s": [0.2, 0.0, 0.0], "angular_velocity_z_rad_s": 0.3,
                "motion_duration_s": args.motion_steps * args.physics_dt,
                "physics_dt_s": args.physics_dt, "rendering_dt_s": args.rendering_dt,
                "linear_damping": 0.0, "angular_damping": 0.0})
            calibration_pub.publish(calibration)
        velocity = np.array([0.2, 0.0, 0.0])
        rigid.set_linear_velocity(velocity)
        rigid.set_angular_velocity(np.array([0.0, 0.0, 0.3]))

        def sample(where, dt=None):
            position, wxyz = rigid.get_world_pose()
            physics_position = tuple(float(v) for v in position)
            physics_xyzw = tuple(float(wxyz[i]) for i in (1, 2, 3, 0))
            matrix = transform.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
            usd_position = tuple(float(v) for v in matrix.ExtractTranslation())
            raw = matrix.ExtractRotationQuat()
            clean = matrix.RemoveScaleShear().ExtractRotationQuat()
            raw_xyzw = tuple(float(v) for v in raw.GetImaginary()) + (float(raw.GetReal()),)
            clean_xyzw = tuple(float(v) for v in clean.GetImaginary()) + (float(clean.GetReal()),)
            sim_time = float(core.get_sim_time())
            row = {
                "where": where, "phase": phase, "dt": dt,
                "physics_steps": int(core.get_physics_num_steps()), "sim_time_s": sim_time,
                "world_time_s": world.current_time,
                "physics_position_m": physics_position, "usd_position_m": usd_position,
                "physics_quaternion_xyzw": physics_xyzw,
                "position_difference_mm": math.dist(physics_position, usd_position) * 1000,
                "raw_usd_rotation_error_deg": quaternion_angle_deg(physics_xyzw, raw_xyzw),
                "scale_removed_usd_rotation_error_deg": quaternion_angle_deg(physics_xyzw, clean_xyzw),
                "analytic_position_error_mm": math.dist(
                    physics_position,
                    [initial_position[i] + float(velocity[i]) * (sim_time - baseline_time)
                     for i in range(3)],
                ) * 1000 if phase == "motion" else None,
            }
            rows.append(row)

        def callback(where):
            def record(dt):
                try:
                    sample(where, float(dt))
                except Exception as error:
                    callback_errors.append(repr(error))
            return record

        interface = omni.physx.get_physx_interface()
        subscriptions.extend([
            interface.subscribe_physics_step_events(callback("legacy_callback")),
            interface.subscribe_physics_on_step_events(callback("pre_step"), True, 100),
            interface.subscribe_physics_on_step_events(callback("post_step"), False, 100),
        ])
        start_steps = int(core.get_physics_num_steps())
        while int(core.get_physics_num_steps()) - start_steps < args.motion_steps:
            world.step(render=True)
            sample("after_app_update")
        phase = "stationary"
        rigid.set_linear_velocity(np.zeros(3))
        rigid.set_angular_velocity(np.zeros(3))
        for _ in range(15):
            world.step(render=True)
            sample("after_app_update")

        summary = {"physics_dt_s": world.get_physics_dt(),
                   "rendering_dt_s": world.get_rendering_dt(),
                   "callback_errors": callback_errors, "samples": len(rows), "phases": {},
                   "linear_damping": 0.0, "angular_damping": 0.0}
        if physics_publisher is not None:
            summary["physics_publisher"] = {
                "snapshots": physics_publisher.snapshots, "errors": physics_publisher.errors}
            summary["ros_module_origins"] = {"rclpy": str(rclpy.__file__),
                                             "geometry_msgs": str(geometry_msgs.__file__)}
        for stage_name in ("motion", "stationary"):
            summary["phases"][stage_name] = {}
            for where in ("legacy_callback", "pre_step", "post_step", "after_app_update"):
                subset = [row for row in rows if row["phase"] == stage_name and row["where"] == where]
                summary["phases"][stage_name][where] = {
                    "samples": len(subset),
                    "max_position_difference_mm": max(row["position_difference_mm"] for row in subset),
                    "max_raw_rotation_error_deg": max(row["raw_usd_rotation_error_deg"] for row in subset),
                    "max_scale_removed_rotation_error_deg": max(row["scale_removed_usd_rotation_error_deg"] for row in subset),
                    "max_analytic_position_error_mm": max(
                        (row["analytic_position_error_mm"] for row in subset
                         if row["analytic_position_error_mm"] is not None), default=None),
                }
        (args.output_dir / "pose_samples.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        (args.output_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("[TASK01 pose timing] " + json.dumps(summary, sort_keys=True), flush=True)
        if callback_errors:
            raise RuntimeError("Physics callbacks failed; inspect captured errors")
        if physics_publisher is not None and physics_publisher.errors:
            raise RuntimeError("Physics publishing failed")
    except Exception as error:
        # Fast Kit shutdown can hide a pending Python traceback and exit zero.
        # Persist the failure before teardown and use normal shutdown on errors.
        import traceback
        traceback.print_exc()
        (args.output_dir / "failure.json").write_text(
            json.dumps({"status": "FAIL", "error": repr(error),
                        "traceback": traceback.format_exc()}, indent=2) + "\n", encoding="utf-8")
        app.set_setting("/app/fastShutdown", False)
        raise
    finally:
        if physics_publisher is not None:
            physics_publisher.close()
        for subscription in subscriptions:
            subscription.unsubscribe()
        if node is not None:
            node.destroy_node()
        if ros_context is not None:
            ros_context.shutdown()
        app.close()


if __name__ == "__main__":
    main()
