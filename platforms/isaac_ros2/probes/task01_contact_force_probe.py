"""[EXPERIMENTAL] 已知载荷接触校准；不改 Task27，也不实现论文力控。

工况：自由落体、静放、静摩擦抵抗已知水平力、双吸盘悬空、已知力触墙。
吸盘承重而碰撞信号为零是可测性诊断，不是吸盘反力测量成功。
"""

import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--physics-dt", type=float, default=1 / 60)
    parser.add_argument("--wall-yaw-deg", type=float, default=0.0)
    args = parser.parse_args()
    if not 0 < args.physics_dt <= 1 / 60 or not math.isfinite(args.wall_yaw_deg):
        parser.error("physics-dt must be in (0,1/60] and yaw must be finite")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    from isaacsim import SimulationApp
    app = SimulationApp({"headless": True, "multi_gpu": False, "sync_loads": False,
                         "fast_shutdown": True})
    grippers = []
    try:
        import numpy as np
        import omni.kit.app
        import omni.physics.tensors as tensors
        import omni.physx
        import omni.usd
        from pxr import Gf, PhysxSchema, UsdGeom, UsdPhysics, UsdShade
        from isaacsim.core.api import World
        from isaacsim.core.prims import RigidPrim, SingleRigidPrim
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from physics_object_sampler import PhysicsObjectSampler
        from physics_contact_sampler import PhysicsContactSampler

        omni.usd.get_context().new_stage()
        omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
            "isaacsim.robot.surface_gripper", True)
        from isaacsim.robot.surface_gripper._surface_gripper import Surface_Gripper, Surface_Gripper_Properties
        world = World(physics_dt=args.physics_dt, rendering_dt=args.physics_dt,
                      stage_units_in_meters=1.0)
        stage = omni.usd.get_context().get_stage()
        world.get_physics_context().set_gravity(-9.81)
        # 保留 solver stabilization；不能因启用传感器偷偷改变求解器设置。
        stabilization_before = world.get_physics_context().get_current_physics_scene_prim().GetAttribute(
            "physxScene:enableStabilization").Get()
        material = UsdShade.Material.Define(stage, "/World/CalibrationMaterial")
        physics_material = UsdPhysics.MaterialAPI.Apply(material.GetPrim())
        physics_material.CreateStaticFrictionAttr(0.8)
        physics_material.CreateDynamicFrictionAttr(0.6)
        physics_material.CreateRestitutionAttr(0.0)

        def box(path, position, size, mass=None, kinematic=False, yaw=0.0):
            cube = UsdGeom.Cube.Define(stage, path)
            cube.CreateSizeAttr(1.0)
            cube.AddTranslateOp().Set(Gf.Vec3d(*position))
            cube.AddOrientOp().Set(Gf.Quatf(math.cos(yaw / 2), Gf.Vec3f(0, 0, math.sin(yaw / 2))))
            cube.AddScaleOp().Set(Gf.Vec3f(*size))
            prim = cube.GetPrim()
            UsdPhysics.CollisionAPI.Apply(prim)
            UsdShade.MaterialBindingAPI.Apply(prim).Bind(material, UsdShade.Tokens.weakerThanDescendants, "physics")
            if mass is not None or kinematic:
                body = UsdPhysics.RigidBodyAPI.Apply(prim)
                body.CreateKinematicEnabledAttr(kinematic)
                UsdPhysics.MassAPI.Apply(prim).CreateMassAttr(mass if mass else 1.0)
                api = PhysxSchema.PhysxRigidBodyAPI.Apply(prim)
                # 校准时保持 actor 醒着；不将该设置写入正式 benchmark。
                api.CreateSleepThresholdAttr(0.0)
            PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.0)
            return prim

        cube_path = "/World/CalibrationCube"
        floor_path, wall_path = "/World/Floor", "/World/Wall"
        carriers = ["/World/LeftCarrier", "/World/RightCarrier"]
        mass, gravity = 0.8, 9.81
        cube_prim = box(cube_path, (0, 0, 1), (0.12,) * 3, mass=mass)
        box(floor_path, (0, 0, -0.05), (6.0, 2.0, 0.1))
        yaw = math.radians(args.wall_yaw_deg)
        wall_center = np.array([2.0, 0.0, 0.5])
        wall_normal = np.array([math.cos(yaw), math.sin(yaw), 0.0])
        box(wall_path, wall_center, (0.05, 0.5, 0.5), yaw=yaw)
        for path, sign in zip(carriers, (1, -1)):
            box(path, (0, -sign * 0.071, 0.5), (0.02,) * 3, kinematic=True)
        world.reset()
        cube = SingleRigidPrim(cube_path)
        cube.initialize()
        sim_view = tensors.create_simulation_view("numpy")
        sim_view.set_subspace_roots("/")
        filters = [floor_path, wall_path] + carriers
        contact_view = sim_view.create_rigid_contact_view(
            cube_path, filter_patterns=filters, max_contact_data_count=128)
        body_view = RigidPrim(cube_path, reset_xform_properties=False, prepare_contact_sensors=False)
        body_view.initialize()
        pose_sampler = PhysicsObjectSampler(body_view)
        contact_sampler = PhysicsContactSampler(contact_view, [cube_path], filters)
        force_body = sim_view.create_rigid_body_view(cube_path)

        for path, sign in zip(carriers, (1, -1)):
            props = Surface_Gripper_Properties()
            props.parentPath, props.d6JointPath = path, path + "/SuctionJoint"
            offset = tensors.Transform()
            offset.p.y = sign * 0.011
            offset.r.z, offset.r.w = sign * math.sqrt(0.5), math.sqrt(0.5)
            props.offset = offset
            props.gripThreshold, props.forceLimit, props.torqueLimit = 0.003, 1e6, 1e6
            props.bendAngle, props.stiffness, props.damping = 0.0, 1e4, 1e3
            props.retryClose, props.disableGravity = True, False
            gripper = Surface_Gripper()
            if not gripper.initialize(props):
                raise RuntimeError("Calibration Surface Gripper failed to initialize")
            grippers.append(gripper)

        rows = []
        def sample_steps(phase, count, force=(0.0, 0.0, 0.0), torque=(0.0, 0.0, 0.0)):
            for _ in range(count):
                if any(force) or any(torque):
                    force_body.apply_forces_and_torques_at_position(
                        np.asarray([force], dtype=np.float32),
                        np.asarray([torque], dtype=np.float32), None,
                        np.array([0], dtype=np.uint32), True)
                for gripper in grippers:
                    gripper.update()
                world.step(render=True)
                snapshot = pose_sampler.capture()
                contacts = contact_sampler.capture(snapshot, world.get_physics_dt())
                row = {"phase": phase, "physics": asdict(snapshot), "contact": contacts,
                       "grippers_closed": [gripper.is_closed() for gripper in grippers]}
                rows.append(row)

        def move_cube(position, yaw_angle=0.0):
            cube.set_world_pose(np.asarray(position), np.array([
                math.cos(yaw_angle / 2), 0, 0, math.sin(yaw_angle / 2)]))
            cube.set_linear_velocity(np.zeros(3))
            cube.set_angular_velocity(np.zeros(3))

        sample_steps("free_fall", max(5, round(0.2 / args.physics_dt)))
        move_cube((0, 0, 0.065))
        sample_steps("table_settle", round(2 / args.physics_dt))
        sample_steps("table_static", round(1 / args.physics_dt))
        # 2 N 小于静摩擦极限。测得摩擦力应抵消外加水平力。
        sample_steps("friction_settle", round(2 / args.physics_dt), (2.0, 0.0, 0.0))
        sample_steps("static_friction", round(1 / args.physics_dt), (2.0, 0.0, 0.0))
        # 非零力矩校准：桌面应同时抵消 2 N 水平力与 +Z 的 0.04 Nm。
        sample_steps("torque_settle", round(2 / args.physics_dt), (2.0, 0.0, 0.0), (0.0, 0.0, 0.04))
        sample_steps("static_torque", round(1 / args.physics_dt), (2.0, 0.0, 0.0), (0.0, 0.0, 0.04))
        move_cube((0, 0, 0.5))
        for _ in range(3):
            for gripper in grippers:
                gripper.close()
            sample_steps("suction_acquire", 1)
        if not all(gripper.is_closed() for gripper in grippers):
            raise RuntimeError("Dual calibration suction did not close")
        sample_steps("suction_settle", round(2 / args.physics_dt))
        sample_steps("dual_suction_hold", round(1 / args.physics_dt))
        for gripper in grippers:
            gripper.open()
        PhysxSchema.PhysxRigidBodyAPI(cube_prim).CreateDisableGravityAttr(True)
        move_cube(wall_center - wall_normal * (0.025 + 0.060 + 0.020), yaw)
        push = tuple(4.0 * wall_normal)
        sample_steps("wall_approach", round(2 / args.physics_dt), push)
        sample_steps("wall_static", round(1 / args.physics_dt), push)

        def phase_data(phase, path=None):
            data = [row for row in rows if row["phase"] == phase]
            forces, moments, normal = [], [], []
            for row in data:
                pairs = [p for p in row["contact"]["pairs"] if path is None or p["other_path"] == path]
                forces.append(np.sum([p["collision_force_world_n"] for p in pairs], axis=0))
                normal.append(np.sum([p["normal_force_world_n"] for p in pairs], axis=0))
                moments.append(np.sum([p["collision_torque_about_sensor_origin_world_nm"] for p in pairs], axis=0))
            return data, np.asarray(forces), np.asarray(moments), np.asarray(normal)

        metrics = {}
        for phase in ("free_fall", "table_static", "static_friction", "static_torque", "dual_suction_hold", "wall_static"):
            data, force, moment, normal = phase_data(phase)
            metrics[phase] = {"samples": len(data), "mean_collision_force_world_n": force.mean(axis=0).tolist(),
                              "mean_normal_force_world_n": normal.mean(axis=0).tolist(),
                              "mean_torque_world_nm": moment.mean(axis=0).tolist(),
                              "max_collision_force_norm_n": float(np.linalg.norm(force, axis=1).max()),
                              "last_position_m": data[-1]["physics"]["bodies"][0]["position_m"]}
        support = np.array([0, 0, mass * gravity])
        measured = lambda phase: np.asarray(metrics[phase]["mean_collision_force_world_n"])
        hold_rows, _, _, _ = phase_data("dual_suction_hold")
        hold_positions = np.array([row["physics"]["bodies"][0]["position_m"] for row in hold_rows])
        checks = {
            "free_fall_collision_signal_zero": metrics["free_fall"]["max_collision_force_norm_n"] < 0.01,
            "table_support_matches_mg_within_0_05_n": float(np.linalg.norm(measured("table_static") - support)) <= 0.05,
            "static_friction_force_balance_within_0_05_n": float(np.linalg.norm(measured("static_friction") - (support + [-2, 0, 0]))) <= 0.05,
            "static_torque_force_balance_within_0_05_n": float(np.linalg.norm(measured("static_torque") - (support + [-2, 0, 0]))) <= 0.05,
            "known_torque_balance_within_0_001_nm": float(np.linalg.norm(
                np.asarray(metrics["static_torque"]["mean_torque_world_nm"]) + [0, 0, 0.04])) <= 0.001,
            "known_wall_load_balance_within_0_05_n": float(np.linalg.norm(measured("wall_static") + np.asarray(push))) <= 0.05,
            "normal_matrix_reconstruction": max(p["matrix_vs_normal_error_n"] for row in rows for p in row["contact"]["pairs"]) < 1e-4,
            "suction_held_height_within_1_mm": float(np.max(np.abs(hold_positions[:, 2] - 0.5))) <= 0.001,
            "suction_closed_entire_hold": all(all(row["grippers_closed"]) for row in hold_rows),
            "suction_collision_signal_does_not_include_constraint_load": metrics["dual_suction_hold"]["max_collision_force_norm_n"] < 0.05,
            "same_step_pose_contact_stamp": all(row["physics"]["stamp_ns"] == row["contact"]["stamp_ns"] for row in rows),
            "timestamps_increasing": all(b["physics"]["stamp_ns"] > a["physics"]["stamp_ns"] for a, b in zip(rows, rows[1:])),
            "stabilization_not_changed_by_measurement": stabilization_before ==
                world.get_physics_context().get_current_physics_scene_prim().GetAttribute("physxScene:enableStabilization").Get(),
        }
        summary = {"status": "PASS_CONTACT_CALIBRATION" if all(checks.values()) else "FAIL",
                   "checks": checks, "metrics": metrics, "physics_dt_s": args.physics_dt,
                   "wall_yaw_deg": args.wall_yaw_deg, "mass_kg": mass, "gravity_m_s2": gravity,
                   "sensor_paths": contact_view.sensor_paths, "filter_paths": contact_view.filter_paths,
                   "collision_wrench_validated": all(checks.values()),
                   "suction_constraint_wrench_measured": False,
                   "surface_gripper_public_methods": [name for name in dir(grippers[0]) if not name.startswith("_")],
                   "physx_force_or_constraint_methods": [name for name in dir(omni.physx.get_physx_interface())
                        if "force" in name.lower() or "constraint" in name.lower()],
                   "notes": "This is collision wrench about Cube origin, NOT left/right suction wrench or force-control reproduction."}
        (args.output_dir / "contact_samples.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("[TASK01 contact calibration] " + json.dumps(summary, sort_keys=True), flush=True)
        if not all(checks.values()):
            raise RuntimeError("Contact calibration checks failed; inspect summary")
    except Exception as error:
        import traceback
        traceback.print_exc()
        (args.output_dir / "failure.json").write_text(json.dumps({"status": "FAIL", "error": repr(error),
            "traceback": traceback.format_exc()}, indent=2) + "\n", encoding="utf-8")
        raise
    finally:
        for gripper in grippers:
            gripper.open()
        grippers.clear()
        app.close()


if __name__ == "__main__":
    main()
