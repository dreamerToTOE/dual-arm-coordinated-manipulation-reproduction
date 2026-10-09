"""TASK02-A：统一 SI/xyzw 状态，不在公共层导入 ROS 或 Isaac。

借鉴 predecessor@631b1f 的显式对象/关节身份和统一时间轴契约，
不导入其坐标、尺寸、控制门限或应用调度器。
"""

from dataclasses import asdict, dataclass
import math
from typing import Optional, Tuple


def finite_vector(values, length=None):
    if length is not None and len(values) != length:
        raise ValueError(f"expected {length} components")
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
               and math.isfinite(v) for v in values):
        raise ValueError("components must be finite numbers")


def nonnegative_integer(value, label):
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")


@dataclass(frozen=True)
class Pose:
    frame_id: str
    position_m: Tuple[float, float, float]
    quaternion_xyzw: Tuple[float, float, float, float]
    measurement_source: str

    def __post_init__(self):
        if not self.frame_id or not self.measurement_source:
            raise ValueError("pose frame and measurement source are required")
        finite_vector(self.position_m, 3)
        finite_vector(self.quaternion_xyzw, 4)
        # 仅校验四元数消息格式；不是 IK/碰撞/成功容差，不修改输入。
        norm = math.sqrt(sum(v * v for v in self.quaternion_xyzw))
        if abs(norm - 1.0) > 1e-6:
            raise ValueError("quaternion must be unit length")


@dataclass(frozen=True)
class ObservationClock:
    simulation_stamp_ns: Optional[int] = None
    physics_step: Optional[int] = None
    post_physics_step: bool = False
    legacy_timeline_time_sec: Optional[float] = None
    diagnostic_ros_clock_ns: Optional[int] = None

    def __post_init__(self):
        if not isinstance(self.post_physics_step, bool):
            raise ValueError("post_physics_step must be boolean")
        for label in ("simulation_stamp_ns", "physics_step", "diagnostic_ros_clock_ns"):
            value = getattr(self, label)
            if value is not None:
                nonnegative_integer(value, label)
        if self.legacy_timeline_time_sec is not None:
            finite_vector((self.legacy_timeline_time_sec,))
            if self.legacy_timeline_time_sec < 0:
                raise ValueError("timeline time must be nonnegative")
        if self.post_physics_step and (self.simulation_stamp_ns is None or self.physics_step is None):
            raise ValueError("post-step state requires actual simulation stamp and step")
        if not self.post_physics_step and (self.simulation_stamp_ns is not None or self.physics_step is not None):
            raise ValueError("unqualified diagnostics cannot supply a scientific clock")

    def require_scientific_timestamp(self):
        if not self.post_physics_step:
            raise ValueError("legacy/asynchronous observation is not a scientific post-step state")
        return self.simulation_stamp_ns


@dataclass(frozen=True)
class ArmState:
    arm_id: str
    joint_names: Tuple[str, ...]
    positions_rad: Tuple[float, ...]
    velocities_rad_s: Tuple[float, ...]
    base_pose: Pose
    tcp_pose: Pose

    def __post_init__(self):
        if not self.arm_id or not self.joint_names or any(not name for name in self.joint_names):
            raise ValueError("arm and joint identities are required")
        if len(set(self.joint_names)) != len(self.joint_names):
            raise ValueError("duplicate joint identity")
        finite_vector(self.positions_rad, len(self.joint_names))
        finite_vector(self.velocities_rad_s, len(self.joint_names))
        if self.base_pose.frame_id != self.tcp_pose.frame_id:
            raise ValueError("base/TCP frames differ; explicit transform required")


@dataclass(frozen=True)
class DualArmState:
    left: ArmState
    right: ArmState

    def __post_init__(self):
        if self.left.arm_id == self.right.arm_id:
            raise ValueError("two distinct arm identities required")
        if self.left.base_pose.frame_id != self.right.base_pose.frame_id:
            raise ValueError("dual-arm frames differ; explicit transform required")


@dataclass(frozen=True)
class ObjectState:
    object_id: str
    pose: Pose

    def __post_init__(self):
        if not self.object_id:
            raise ValueError("object identity required")


@dataclass(frozen=True)
class StateRecord:
    clock: ObservationClock
    arms: DualArmState
    objects: Tuple[ObjectState, ...]

    def __post_init__(self):
        ids = [item.object_id for item in self.objects]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate object identity")
        if any(item.pose.frame_id != self.arms.left.base_pose.frame_id for item in self.objects):
            raise ValueError("object/arm frames differ; explicit transform required")

    def to_dict(self):
        return {"schema_version": "task02.state.v0.1", "state": asdict(self)}
