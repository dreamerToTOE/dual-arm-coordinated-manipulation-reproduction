"""[EXPERIMENTAL] 独立安装座试验：关节反力能否读到吸盘 D6 载荷。

不是 FR3 力传感器，更不是论文控制器；不改真实机器人模型。
用一自由度高刚度安装座分别测空载、悬挂 0.8 kg 的安装关节六维反力。
"""

import argparse
import json
import math
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--roll-deg", type=float, default=0.0)
    parser.add_argument("--tool-com-x", type=float, default=0.0)
    parser.add_argument("--principal-roll-deg", type=float, default=0.0)
    parser.add_argument("--joint-child-anchor-x", type=float, default=0.0)
    parser.add_argument("--joint-roll-deg", type=float, default=0.0)
    args = parser.parse_args()
    if not all(math.isfinite(v) for v in (args.roll_deg, args.tool_com_x, args.principal_roll_deg,
                                         args.joint_child_anchor_x, args.joint_roll_deg)):
        parser.error("roll/com/principal axis must be finite")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    from isaacsim import SimulationApp
    app = SimulationApp({"headless": True, "multi_gpu": False, "sync_loads": False,
                         "fast_shutdown": True})
    gripper = None
    try:
        import numpy as np
        import omni.kit.app
        import omni.physics.tensors as tensors
        import omni.usd
        from pxr import Gf, PhysxSchema, UsdGeom, UsdPhysics
        from isaacsim.core.api import World
        from isaacsim.core.prims import SingleRigidPrim
        from isaacsim.core.nodes.bindings import _isaacsim_core_nodes
        omni.usd.get_context().new_stage()
        omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
            "isaacsim.robot.surface_gripper", True)
        from isaacsim.robot.surface_gripper._surface_gripper import Surface_Gripper, Surface_Gripper_Properties
        world = World(physics_dt=1 / 60, rendering_dt=1 / 60, stage_units_in_meters=1.0)
        world.get_physics_context().set_gravity(-9.81)
        stage = omni.usd.get_context().get_stage()
        angle = math.radians(args.roll_deg)
        rotation = np.array([[1, 0, 0], [0, math.cos(angle), -math.sin(angle)],
                             [0, math.sin(angle), math.cos(angle)]])
        orientation = Gf.Quatf(math.cos(angle / 2), Gf.Vec3f(math.sin(angle / 2), 0, 0))

        def body(path, position, size, mass):
            shape = UsdGeom.Cube.Define(stage, path)
            if len(set(size)) != 1:
                raise ValueError("Calibration mount uses uniform Cubes without rigid-body scaling")
            # 不能用刚体 scale 实现尺寸：它也会缩放 authored COM / joint anchor。
            shape.CreateSizeAttr(size[0])
            shape.AddTranslateOp().Set(Gf.Vec3d(*position))
            shape.AddOrientOp().Set(orientation)
            prim = shape.GetPrim()
            UsdPhysics.RigidBodyAPI.Apply(prim)
            UsdPhysics.CollisionAPI.Apply(prim)
            UsdPhysics.MassAPI.Apply(prim).CreateMassAttr(mass)
            PhysxSchema.PhysxRigidBodyAPI.Apply(prim).CreateSleepThresholdAttr(0.0)
            return prim

        root = UsdGeom.Xform.Define(stage, "/World/Carrier")
        UsdPhysics.ArticulationRootAPI.Apply(root.GetPrim())
        tool_origin = np.array([0.0, 0.0, 0.5])
        base, tool = "/World/Carrier/Base", "/World/Carrier/Tool"
        body(base, tool_origin, (0.04,) * 3, 1.0)
        tool_prim = body(tool, tool_origin, (0.02,) * 3, 0.1)
        tool_mass = UsdPhysics.MassAPI(tool_prim)
        tool_mass.CreateCenterOfMassAttr(Gf.Vec3f(args.tool_com_x, 0, 0))
        principal_angle = math.radians(args.principal_roll_deg)
        tool_mass.CreatePrincipalAxesAttr(Gf.Quatf(math.cos(principal_angle / 2),
                                                  Gf.Vec3f(math.sin(principal_angle / 2), 0, 0)))
        tool_mass.CreateDiagonalInertiaAttr(Gf.Vec3f(*([0.1 * 0.02 ** 2 / 6] * 3)))
        principal_rotation = np.array([[1, 0, 0], [0, math.cos(principal_angle), -math.sin(principal_angle)],
                                      [0, math.sin(principal_angle), math.cos(principal_angle)]])
        fixed = UsdPhysics.FixedJoint.Define(stage, "/World/Carrier/WorldJoint")
        fixed.CreateBody1Rel().SetTargets([base])
        fixed.CreateLocalPos0Attr(Gf.Vec3f(*tool_origin))
        fixed.CreateLocalRot0Attr(orientation)
        mount = UsdPhysics.PrismaticJoint.Define(stage, "/World/Carrier/MountJoint")
        mount.CreateBody0Rel().SetTargets([base])
        mount.CreateBody1Rel().SetTargets([tool])
        mount.CreateAxisAttr("X")
        mount.CreateLocalPos0Attr(Gf.Vec3f(args.joint_child_anchor_x, 0, 0))
        mount.CreateLocalPos1Attr(Gf.Vec3f(args.joint_child_anchor_x, 0, 0))
        joint_angle = math.radians(args.joint_roll_deg)
        joint_orientation = Gf.Quatf(math.cos(joint_angle / 2), Gf.Vec3f(math.sin(joint_angle / 2), 0, 0))
        mount.CreateLocalRot0Attr(joint_orientation)
        mount.CreateLocalRot1Attr(joint_orientation)
        joint_rotation = np.array([[1, 0, 0], [0, math.cos(joint_angle), -math.sin(joint_angle)],
                                  [0, math.sin(joint_angle), math.cos(joint_angle)]])
        drive = UsdPhysics.DriveAPI.Apply(mount.GetPrim(), "linear")
        drive.CreateTypeAttr("force")
        drive.CreateTargetPositionAttr(0.0)
        drive.CreateStiffnessAttr(1e6)
        drive.CreateDampingAttr(1e4)
        cube_path = "/World/Payload"
        payload_offset = rotation @ np.array([0.16, 0, 0])
        payload_prim = body(cube_path, tool_origin + payload_offset, (0.12,) * 3, 0.8)
        # 只在试验准备阶段禁用载荷重力；吸住后重新启用再检验承重。
        gravity_api = PhysxSchema.PhysxRigidBodyAPI(payload_prim)
        gravity_api.CreateDisableGravityAttr(True)
        world.reset()
        sim_view = tensors.create_simulation_view("numpy")
        sim_view.set_subspace_roots("/")
        articulation = sim_view.create_articulation_view("/World/Carrier")
        if articulation.count != 1 or tool not in articulation.link_paths[0]:
            raise RuntimeError(f"Unexpected mount articulation: {articulation.link_paths}")
        tool_index = list(articulation.link_paths[0]).index(tool)
        actual_com_poses = np.array(articulation.get_coms(), copy=True)
        if not np.allclose(actual_com_poses[0, tool_index, :3], [args.tool_com_x, 0, 0], atol=1e-7):
            raise RuntimeError(f"Physical COM differs from calibration model: {actual_com_poses}")
        payload = SingleRigidPrim(cube_path)
        payload.initialize()
        rows = []
        core = _isaacsim_core_nodes.acquire_interface()

        def steps(phase, count):
            for _ in range(count):
                if gripper is not None:
                    gripper.update()
                world.step(render=True)
                wrench = np.array(articulation.get_link_incoming_joint_force(), copy=True)[0, tool_index]
                if not np.isfinite(wrench).all():
                    raise RuntimeError("Nonfinite mount reaction")
                position, wxyz = payload.get_world_pose()
                rows.append({"phase": phase, "stamp_ns": round(core.get_sim_time() * 1e9),
                             "physics_step": int(core.get_physics_num_steps()),
                             "mount_reaction_raw": wrench.tolist(),
                             "payload_position_m": position.tolist(), "payload_wxyz": wxyz.tolist(),
                             "closed": gripper.is_closed() if gripper is not None else False})

        steps("unloaded_settle", 120)
        steps("unloaded", 60)
        props = Surface_Gripper_Properties()
        props.parentPath, props.d6JointPath = tool, tool + "/SuctionJoint"
        offset = tensors.Transform()
        offset.p.x = 0.1
        props.offset = offset
        props.gripThreshold, props.forceLimit, props.torqueLimit = 0.003, 1e6, 1e6
        props.bendAngle, props.stiffness, props.damping = 0.0, 1e4, 1e3
        props.retryClose, props.disableGravity = True, False
        gripper = Surface_Gripper()
        if not gripper.initialize(props) or not gripper.close():
            raise RuntimeError("Mount calibration suction failed to close")
        gravity_api.GetDisableGravityAttr().Set(False)
        steps("loaded_settle", 120)
        steps("loaded", 60)
        means = {phase: np.array([r["mount_reaction_raw"] for r in rows if r["phase"] == phase]).mean(axis=0)
                 for phase in ("unloaded", "loaded")}
        delta = means["loaded"] - means["unloaded"]
        support = np.array([0.0, 0.0, 0.8 * 9.81])
        # 先列 link 原点的参考预测；非重合工况必须识别 joint/link/惯性轴，不能预设。
        expected_world = np.r_[support, np.cross(payload_offset, support)]
        expected_local = np.r_[rotation.T @ support, rotation.T @ expected_world[3:]]
        # 质心/主惯性轴不为零时才能识别 API 的力矩参考点和表达坐标系。
        hypotheses = {}
        for axes, frame_rotation in (("link", rotation), ("principal", rotation @ principal_rotation),
                                     ("joint", rotation @ joint_rotation)):
            for point, reference in (("link_origin", tool_origin),
                                     ("com", tool_origin + rotation @ np.array([args.tool_com_x, 0, 0])),
                                     ("joint_anchor", tool_origin + rotation @ np.array([args.joint_child_anchor_x, 0, 0]))):
                expected = np.r_[frame_rotation.T @ support,
                    frame_rotation.T @ np.cross(tool_origin + payload_offset - reference, support)]
                hypotheses[axes + "_axes_about_" + point] = {
                    "expected_delta": expected.tolist(),
                    "force_error_n": float(np.linalg.norm(delta[:3] - expected[:3])),
                    "torque_error_nm": float(np.linalg.norm(delta[3:] - expected[3:]))}
        matching = [name for name, value in hypotheses.items()
                    if value["force_error_n"] <= 0.05 and value["torque_error_nm"] <= 0.005]
        identifying_test = abs(args.tool_com_x) >= 0.001 and abs(args.principal_roll_deg) >= 10
        extended_identifying_test = (identifying_test and abs(args.joint_child_anchor_x) >= 0.001
            and abs(args.tool_com_x - args.joint_child_anchor_x) >= 0.001
            and abs(args.joint_roll_deg) >= 10
            and abs(args.principal_roll_deg - args.joint_roll_deg) >= 10)
        basic_matching = [name for name in matching if not name.startswith("joint_") and not name.endswith("joint_anchor")]
        hold = [r for r in rows if r["phase"] == "loaded"]
        checks = {
            "incoming_wrench_matches_known_load_hypothesis": len(matching) == 1 if extended_identifying_test else (
                len(basic_matching) == 1 if identifying_test else bool(matching)),
            "payload_held_within_1_mm": max(float(np.linalg.norm(
                np.array(r["payload_position_m"]) - (tool_origin + payload_offset))) for r in hold) <= 0.001,
            "suction_closed_through_load_window": all(r["closed"] for r in hold),
            "timestamps_increasing": all(b["stamp_ns"] > a["stamp_ns"] for a, b in zip(rows, rows[1:])),
        }
        summary = {"status": "PASS_MOUNT_CALIBRATION" if all(checks.values()) else "FAIL",
                   "checks": checks, "roll_deg": args.roll_deg, "physics_dt_s": 1 / 60,
                   "tool_com_x_m": args.tool_com_x, "principal_roll_deg": args.principal_roll_deg,
                   "reference_point_and_axes_identifying_test": identifying_test,
                   "joint_child_anchor_x_m": args.joint_child_anchor_x, "joint_roll_deg": args.joint_roll_deg,
                   "joint_anchor_and_axes_identifying_test": extended_identifying_test,
                   "reference_hypotheses": hypotheses, "matching_hypotheses": matching,
                   "link_paths": articulation.link_paths, "tool_index": tool_index,
                   "physical_com_poses": actual_com_poses.tolist(), "rigid_body_scaling": "none",
                   "unloaded_mean": means["unloaded"].tolist(), "loaded_mean": means["loaded"].tolist(),
                   "measured_delta_raw": delta.tolist(),
                   "reference_delta_in_link_axes_about_link_origin": expected_local.tolist(),
                   "expected_delta_world": expected_world.tolist(),
                   "notes": "Isolated experimental mount reaction; NOT calibrated FR3 TCP wrench or paper force control."}
        (args.output_dir / "mount_samples.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("[TASK01 mount calibration] " + json.dumps(summary, sort_keys=True), flush=True)
        if not all(checks.values()):
            raise RuntimeError("Mount calibration checks failed; inspect summary")
    except Exception as error:
        import traceback
        traceback.print_exc()
        (args.output_dir / "failure.json").write_text(json.dumps({"status": "FAIL", "error": repr(error),
            "traceback": traceback.format_exc()}, indent=2) + "\n", encoding="utf-8")
        raise
    finally:
        if gripper is not None:
            gripper.open()
        gripper = None
        app.close()


if __name__ == "__main__":
    main()
