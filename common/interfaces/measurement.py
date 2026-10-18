"""TASK02-C 测量草案：只描述数据，不估计力、不查询碰撞、不采集传感器。

复用 TASK02-A Pose 与 TASK02-B 时间/资格/编解码，不改变其已验收语义。
资格和 source/evidence 均为调用方声明，不是 native measurement attestation。
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from .exchange import MeasurementQualification, TimeBasis, TimePoint, enum_value, identities, text
from .state import Pose, finite_vector
from .wire import WireRecord


Vector3 = Tuple[float, float, float]


def vector3(value):
    if not isinstance(value, tuple):
        raise ValueError("immutable SI vector required")
    finite_vector(value, 3)


@dataclass(frozen=True)
class MeasurementInfo:
    source_id: str
    qualification: MeasurementQualification
    time: Optional[TimePoint]
    post_physics_step: bool
    valid: bool
    evidence_refs: Tuple[str, ...]
    invalid_reason: Optional[str] = None

    def __post_init__(self):
        text(self.source_id)
        enum_value(self.qualification, MeasurementQualification)
        identities(self.evidence_refs, required=self.valid)
        if type(self.valid) is not bool or type(self.post_physics_step) is not bool:
            raise ValueError("explicit boolean validity/post-step required")
        if self.time is not None and not isinstance(self.time, TimePoint):
            raise ValueError("typed measurement clock required")
        if self.valid and self.invalid_reason is not None:
            raise ValueError("valid measurement cannot conceal invalid reason")
        if not self.valid:
            text(self.invalid_reason)
        if self.post_physics_step and (self.time is None or self.time.basis is not TimeBasis.SIMULATION
                                       or self.time.physics_step is None):
            raise ValueError("post-step needs simulation session/stamp/step")
        if self.qualification is MeasurementQualification.SYNCHRONIZED_POST_STEP:
            if not self.post_physics_step:
                raise ValueError("synchronized qualification needs post-step clock")
            if any(label in self.source_id.lower() for label in ("legacy", "synthetic")):
                raise ValueError("legacy/synthetic provenance cannot be promoted")
        if self.qualification is MeasurementQualification.LEGACY_ASYNCHRONOUS and (
                self.post_physics_step or self.time is not None):
            raise ValueError("legacy diagnostics cannot acquire a scientific clock")


@dataclass(frozen=True)
class PoseMeasurement(WireRecord):
    SCHEMA = "task02.pose_measurement.v0.1"
    entity_id: str
    pose: Optional[Pose]
    info: MeasurementInfo

    def __post_init__(self):
        text(self.entity_id)
        if not isinstance(self.info, MeasurementInfo):
            raise ValueError("typed measurement metadata required")
        if self.pose is not None and not isinstance(self.pose, Pose):
            raise ValueError("typed SI/xyzw pose required")
        if self.info.valid and self.pose is None:
            raise ValueError("valid pose payload is missing")
        if self.info.qualification is MeasurementQualification.SYNCHRONIZED_POST_STEP and self.pose:
            if any(label in self.pose.measurement_source.lower() for label in ("legacy", "synthetic")):
                raise ValueError("pose provenance cannot be promoted")


@dataclass(frozen=True)
class ContactWrench(WireRecord):
    """作用于 on_body 的力/力矩；都在 frame 中表达，力矩关于 application_point。

    应用点坐标也在同一 frame 中，绝不默认为 TCP/COM/world origin。
    这里不做坐标变换、moment shift、重力惯性补偿或力估计。
    """

    SCHEMA = "task02.contact_wrench.v0.1"
    on_body_id: str
    by_body_id: str
    frame_id: str
    force_N: Optional[Vector3]
    torque_Nm: Optional[Vector3]
    application_point_m: Optional[Vector3]
    info: MeasurementInfo
    force_unit: str = "N"
    torque_unit: str = "N*m"
    point_unit: str = "m"

    def __post_init__(self):
        for value in (self.on_body_id, self.by_body_id, self.frame_id):
            text(value)
        if self.on_body_id == self.by_body_id:
            raise ValueError("distinct wrench body identities required")
        if not isinstance(self.info, MeasurementInfo):
            raise ValueError("typed wrench metadata required")
        if (self.force_unit, self.torque_unit, self.point_unit) != ("N", "N*m", "m"):
            raise ValueError("explicit SI wrench units required")
        for value in (self.force_N, self.torque_Nm, self.application_point_m):
            if value is None:
                if self.info.valid:
                    raise ValueError("valid wrench component/application point missing")
            else:
                vector3(value)


@dataclass(frozen=True)
class CollisionDistance(WireRecord):
    """signed distance: >0 净空，=0 边界接触，<0 穿透；不是自动失败判定。

    closest points 都在 frame 中。负距离时它们是来源后端声明的 witness points，
    不假定唯一、不强制其欧氏距离等于穿透深度；未测得必须标 invalid/None。
    """

    SCHEMA = "task02.collision_distance.v0.1"
    body_a_id: str
    body_b_id: str
    frame_id: str
    signed_distance_m: Optional[float]
    closest_point_a_m: Optional[Vector3]
    closest_point_b_m: Optional[Vector3]
    info: MeasurementInfo
    distance_unit: str = "m"

    def __post_init__(self):
        for value in (self.body_a_id, self.body_b_id, self.frame_id):
            text(value)
        if self.body_a_id == self.body_b_id:
            raise ValueError("distinct collision body identities required")
        if not isinstance(self.info, MeasurementInfo) or self.distance_unit != "m":
            raise ValueError("typed metadata and SI collision distance required")
        if self.signed_distance_m is None:
            if self.info.valid:
                raise ValueError("valid distance missing")
        else:
            finite_vector((self.signed_distance_m,), 1)
        for point in (self.closest_point_a_m, self.closest_point_b_m):
            if point is None:
                if self.info.valid:
                    raise ValueError("valid nearest/witness point missing")
            else:
                vector3(point)
