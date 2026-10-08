"""[ENGINEERING] TASK01 单件薄桥：仅绑定固定旧源码的 SG / joint / rail。

不执行旧 Task26 初始化、供料、五 Cube、effort 或 USD Ground Truth。
科学状态由调用方同一 post-step sampler 记录，本桥 Bool 仅用于执行门禁。
RAIL_MAX_SPEED=.20m/s 等只沿用获批 rail mover 内部工程常量，非机械臂
velocity/time_scale、drive 或 P3 优化参数；不带回旧推进 effort/gap 门限。
"""
import ast
import hashlib
import json
import math
from pathlib import Path
import subprocess
import threading
import time

SOURCE_COMMIT = "631b1f65656d025c1bb2173e874192f3fe4d355a"
SOURCE_PATH = "isaac/scripts/task26_truck_box_bridge.py"
SOURCE_SHA256 = "13b5f88d1e7563a37ecafbf571d8ef93015b57059b8912ba9f3399e21e339644"
LEGACY_ROOT = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing")
METHODS = {
    "_build_gripper", "_command", "_stamp_key", "_joint_command",
    "_apply_joint_command", "_apply_pending_joint_commands", "_rail_command",
    "_author_translate", "_rail_read_x", "_write_rail_x", "_apply_rail", "_check_rail",
}
CONSTANTS = {
    "SIDES", "BRANCH_SIGN", "RIGID_GRASP_FORCE_LIMIT", "RIGID_GRASP_TORQUE_LIMIT",
    "GRASP_STIFFNESS", "GRASP_DAMPING", "RAIL_TOLERANCE", "RAIL_MAX_SPEED",
    "RAIL_HOLD_SEC", "RAIL_COMMAND_QUIET_SEC",
}


def selected_source(source):
    """只允许已审计函数；setter 最后兼容性 fallback 失败时显式传播。"""
    if hashlib.sha256(source.encode("utf-8")).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("Pinned Task26 bridge hash mismatch; refusing source substitution")
    parsed = ast.parse(source, filename=SOURCE_PATH)
    constants = []
    methods = []
    for node in parsed.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in CONSTANTS for t in node.targets):
            constants.append(node)
        if isinstance(node, ast.ClassDef) and node.name == "Task26BatchedFeedBridge":
            methods = [m for m in node.body if isinstance(m, ast.FunctionDef) and m.name in METHODS]
    if {m.name for m in methods} != METHODS:
        raise RuntimeError("Pinned bridge method allowlist incomplete")
    if {t.id for n in constants for t in n.targets if isinstance(t, ast.Name)} != CONSTANTS:
        raise RuntimeError("Pinned bridge constant allowlist incomplete")
    writer = next(m for m in methods if m.name == "_write_rail_x")
    last_handlers = [n for n in ast.walk(writer) if isinstance(n, ast.ExceptHandler) and n.name == "exc2"]
    if len(last_handlers) != 1:
        raise RuntimeError("Original rail setter exception structure changed")
    # 唯一源码补丁：旧代码 print 后继续会假报导轨成功；现在失败立即冒泡。
    last_handlers[0].body.append(ast.Raise(exc=None, cause=None))
    cls = ast.ClassDef(name="PinnedPrimitives", bases=[], keywords=[], body=methods,
                       decorator_list=[])
    return ast.fix_missing_locations(ast.Module(body=constants + [cls], type_ignores=[]))


def load_primitives(bindings):
    source = subprocess.run(
        ["git", "-C", str(LEGACY_ROOT), "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"],
        check=True, capture_output=True, text=True, timeout=10).stdout
    namespace = dict(bindings)
    exec(compile(selected_source(source), SOURCE_PATH, "exec"), namespace)
    return namespace["PinnedPrimitives"], namespace


def build_bridge(stage, articulations, config, namespace="/task01"):
    """articulations 必须由 GUI 主入口初始化；这里不启动/重置仿真。"""
    import numpy as np
    import omni.physics.tensors
    from pxr import Gf, UsdGeom
    import rclpy
    from rclpy.context import Context
    from rclpy.executors import SingleThreadedExecutor
    from isaacsim.core.utils.types import ArticulationAction
    from isaacsim.robot.surface_gripper._surface_gripper import (
        Surface_Gripper, Surface_Gripper_Properties)
    from sensor_msgs.msg import JointState
    from std_msgs.msg import Bool, Float64, String
    if namespace != "/task01":
        raise ValueError("Bounded integration is restricted to /task01")
    if set(articulations) != {"left", "right"}:
        raise ValueError("Both initialized articulations are required")
    if not stage.GetPrimAtPath("/World/Task01/Cube").IsValid():
        raise RuntimeError("Single benchmark Cube missing; refusing legacy feed")
    bindings = dict(np=np, omni=omni, Gf=Gf, UsdGeom=UsdGeom, time=time, math=math,
                    ArticulationAction=ArticulationAction, Surface_Gripper=Surface_Gripper,
                    Surface_Gripper_Properties=Surface_Gripper_Properties,
                    DUAL_SYNC_FRAME_ID="task01_dual_sync")
    primitives, legacy = load_primitives(bindings)

    class SingleCubeBridge(primitives):
        def __init__(self):
            self.stage, self.articulations = stage, articulations
            self.cube_paths = ("/World/Task01/Cube",)
            self._lock = threading.Lock()
            self._desired = {s: False for s in legacy["SIDES"]}
            self._last_commanded = {s: None for s in legacy["SIDES"]}
            self._retry_accum = {s: 0.0 for s in legacy["SIDES"]}
            self._retry_interval = 0.05  # 原 Task26 close 重试间隔，不调吸附参数。
            self._single_commands = {s: None for s in legacy["SIDES"]}
            self._dual_commands = {s: None for s in legacy["SIDES"]}
            self._pending_rail = {s: None for s in legacy["SIDES"]}
            self._pending_rail_rejected = {s: None for s in legacy["SIDES"]}
            self._queued_rail_request = None
            self._last_joint_command_time = 0.0
            self.rail_base_y = {s: float(config["robots"][s]["base_at_rest_world_m"][1]) for s in legacy["SIDES"]}
            self.rail_carriage_z = 0.0  # 本轮无新导轨视觉件；不改变物理模型。
            self.rail_rest_x = 0.650
            self.rail_travel = {s: config["robots"][s]["rail_x_limits_world_m"] for s in legacy["SIDES"]}
            self.rail_target = {s: self.rail_rest_x for s in legacy["SIDES"]}
            self.rail_measured = dict(self.rail_target)
            self.rail_arrived = {s: True for s in legacy["SIDES"]}
            self.rail_stable = {s: 0.0 for s in legacy["SIDES"]}
            self.errors, self.halted, self._publish_accum = [], False, 0.0
            self.grippers = {s: self._build_gripper(s) for s in legacy["SIDES"]}
            self.context = Context()
            rclpy.init(context=self.context)
            self.node = rclpy.create_node("task01_reused_single_cube_bridge", context=self.context)
            self.executor = SingleThreadedExecutor(context=self.context)
            self.executor.add_node(self.node)
            self.subscriptions, self.state_pubs = [], {}
            for side in legacy["SIDES"]:
                self.subscriptions.append(self.node.create_subscription(
                    JointState, f"/{side}/joint_command",
                    lambda m, s=side: self._joint_command(s, m), 20))
                self.subscriptions.append(self.node.create_subscription(
                    Bool, f"{namespace}/{side}/suction_command",
                    lambda m, s=side: self._command(s, m), 10))
                self.state_pubs[side] = self.node.create_publisher(Bool, f"{namespace}/{side}/suction_state", 10)
            self.subscriptions.append(self.node.create_subscription(
                String, f"{namespace}/rail_command", self._both_rails, 10))
            self.spin_thread = threading.Thread(target=self.executor.spin, daemon=True)
            self.spin_thread.start()
            self.provenance = {
                "repository": "dreamerToTOE/dual-arm-embodied-palletizing", "commit": SOURCE_COMMIT,
                "path": SOURCE_PATH, "sha256": SOURCE_SHA256, "methods": sorted(METHODS),
                "patch": "raise original final rail setter exception instead of silently continuing",
                "rail_mover_original_engineering_constants": {k: legacy[k] for k in
                    ("RAIL_MAX_SPEED", "RAIL_TOLERANCE", "RAIL_HOLD_SEC", "RAIL_COMMAND_QUIET_SEC")},
                "scientific_pose_feedback": "external live-PhysX post-step sampler, not old USD publisher",
            }

        def _both_rails(self, message):
            try:
                request = json.loads(message.data)
                if set(request) != {"left_x", "right_x"}:
                    raise ValueError("Both rail targets are required")
                targets = {s: float(request[f"{s}_x"]) for s in legacy["SIDES"]}
                if any(not math.isfinite(x) or abs(x - 0.750) > 1e-9 for x in targets.values()):
                    raise ValueError("Only user-approved both-rail station 0.750 is allowed")
                if any(g.is_closed() for g in self.grippers.values()):
                    raise RuntimeError("Both physical SG must be OPEN before rail request")
                with self._lock:
                    if any(self._desired.values()) or any(self._last_commanded.values()):
                        raise RuntimeError("Both suction OFF transitions must be applied before rails")
                    self._queued_rail_request = targets
            except Exception as error:
                self.halted = True
                self.errors.append(repr(error))
                self.node.get_logger().error(f"Fixed handoff rail STOP: {error}")

        def pre_step(self, dt):
            if self.halted:
                return
            try:
                self._apply_pending_joint_commands()
                with self._lock:
                    rail_request = self._queued_rail_request
                    self._queued_rail_request = None
                if rail_request is not None:
                    if any(g.is_closed() for g in self.grippers.values()):
                        raise RuntimeError("SG closed before queued rail request; STOP")
                    # 原门禁在同一 physics callback 对两侧完成，不留下半侧请求。
                    for side in legacy["SIDES"]:
                        self._rail_command(side, Float64(data=rail_request[side]))
                    with self._lock:
                        rejected = {s: r for s, r in self._pending_rail_rejected.items() if r is not None}
                        if rejected:
                            self._pending_rail = {s: None for s in legacy["SIDES"]}
                            raise RuntimeError(f"Original rail gate rejected request: {rejected}")
                with self._lock:
                    desired = dict(self._desired)
                    pending = dict(self._pending_rail)
                    self._pending_rail = {s: None for s in legacy["SIDES"]}
                if any(desired.values()) and (any(p is not None for p in pending.values()) or
                                              any(not arrived for arrived in self.rail_arrived.values())):
                    raise RuntimeError("SG ON during fixed rail transition; STOP")
                for side in legacy["SIDES"]:
                    if pending[side] is not None:
                        self._apply_rail(side, pending[side])
                    self._check_rail(side, dt)
                    if not self.rail_arrived[side] and self._rail_read_x(side) is None:
                        raise RuntimeError(f"Live {side} base measurement failed during rail move")
                # 原 Task26 SG 生命周期逐句复用，仅移除 feed/arrival/effort 分支。
                for side in legacy["SIDES"]:
                    gripper = self.grippers[side]
                    if desired[side] != self._last_commanded[side]:
                        ok = gripper.close() if desired[side] else gripper.open()
                        print(f"[TASK01 reused {side}] SUCTION {'ON' if desired[side] else 'OFF'}, result={ok}", flush=True)
                        self._last_commanded[side] = desired[side]
                        self._retry_accum[side] = 0.0
                    if desired[side]:
                        gripper.update()
                        if not gripper.is_closed():
                            self._retry_accum[side] += float(dt)
                            if self._retry_accum[side] >= self._retry_interval:
                                self._retry_accum[side] = 0.0
                                gripper.close()
                    else:
                        self._retry_accum[side] = 0.0
                self._publish_accum += float(dt)
                if self._publish_accum >= 0.05:
                    self._publish_accum = 0.0
                    for side in legacy["SIDES"]:
                        self.state_pubs[side].publish(Bool(data=bool(self.grippers[side].is_closed())))
            except Exception as error:
                self.halted = True
                self.errors.append(repr(error))
                raise  # 主入口必须观察 errors 后 STOP；不可假成功/自行重试。

        def attachment_identity(self, side):
            path = f"/World/{side}_fr3/fr3_link8/task26_side_surface_gripper_joint"
            info = {"joint_name": path, "closed": bool(self.grippers[side].is_closed()),
                    "actual_joint_anchor": "UNAVAILABLE", "identity_source": "existing Surface Gripper"}
            try:
                from omni.isaac.dynamic_control import _dynamic_control
                dc = _dynamic_control.acquire_dynamic_control_interface()
                info["public_d6_handle"] = int(dc.get_d6_joint(path))
            except Exception as error:
                info["public_d6_handle"] = "UNAVAILABLE"
                info["identity_read_error"] = repr(error)
            return info

        def shutdown(self):
            self.halted = True
            for gripper in self.grippers.values():
                gripper.open()
            self.executor.shutdown(timeout_sec=0.5)
            self.node.destroy_node()
            self.context.shutdown()

    return SingleCubeBridge()
