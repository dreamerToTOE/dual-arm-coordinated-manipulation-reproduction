"""离线 A/B 指标：复用 Task14 数学和样本筛选思想，不移植历史门限。

FRAME/SESSION/DOMAIN/QUALIFICATION 不一致拒绝整个输入；缺失/无效/时间偏差
按输入样本记录拒绝原因。无重采样、补零、目标到达判定、SUCCESS 或传感器调用。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from common.interfaces.exchange import MeasurementQualification, TimeBasis, TimePoint, enum_value, text
from common.interfaces.measurement import PoseMeasurement
from common.interfaces.state import Pose, nonnegative_integer
from common.interfaces.wire import WireRecord
from .math import ScalarSummary, insertion_geometry, midpoint_error, orientation_error, relative_tcp_error, same_frame, summarize, position_error


class EvaluationMode(str, Enum):
    FORMAL = "FORMAL_DECLARED_POST_STEP"
    SYNTHETIC = "SYNTHETIC_OFFLINE_NOT_SCIENTIFIC"


@dataclass(frozen=True)
class MetricContext:
    frame_id: str
    simulation_session_id: str
    object_id: str
    mode: EvaluationMode
    max_stamp_skew_ns: int  # 必须显式给出，不隐含旧30ms；只用于数据对齐。

    def __post_init__(self):
        for value in (self.frame_id, self.simulation_session_id, self.object_id):
            text(value)
        enum_value(self.mode, EvaluationMode)
        nonnegative_integer(self.max_stamp_skew_ns, "explicit sample alignment policy")


@dataclass(frozen=True)
class TransportSample:
    left_tcp: Optional[PoseMeasurement]
    right_tcp: Optional[PoseMeasurement]
    obj: Optional[PoseMeasurement]
    desired_object_pose: Optional[Pose]  # 调用方明确给出的对应参考；不自动按索引配轨迹。


@dataclass(frozen=True)
class RejectedSample:
    input_index: int
    reason: str


@dataclass(frozen=True)
class TransportPoint:
    input_index: int
    time: TimePoint
    relative_tcp_error_m: float
    box_to_tcp_midpoint_error_m: float
    object_position_error_m: float
    object_orientation_error_rad: float


@dataclass(frozen=True)
class TransportMetrics(WireRecord):
    SCHEMA = "task02.transport_metrics.v0.1"
    context: MetricContext
    input_samples: int
    valid_samples: int
    rejected_samples: int
    rejections: Tuple[RejectedSample, ...]
    reference_input_index: Optional[int]
    reference_time: Optional[TimePoint]
    reference_left_tcp: Optional[Pose]
    reference_right_tcp: Optional[Pose]
    reference_object: Optional[Pose]
    relative_tcp_error_m: Optional[ScalarSummary]
    box_to_tcp_midpoint_error_m: Optional[ScalarSummary]
    object_position_error_m: Optional[ScalarSummary]
    object_position_rmse_m: Optional[float]
    object_orientation_error_rad: Optional[ScalarSummary]
    samples: Tuple[TransportPoint, ...]


@dataclass(frozen=True)
class InsertionPoint:
    input_index: int
    time: TimePoint
    cube_target_position_error_m: float
    axial_displacement_m: float
    axial_progress: float
    lateral_deviation_m: float
    orientation_deviation_rad: float


@dataclass(frozen=True)
class InsertionMetrics(WireRecord):
    SCHEMA = "task02.insertion_metrics.v0.1"
    context: MetricContext
    axis_origin: Pose
    target: Pose
    unit_axis: Tuple[float, float, float]
    input_samples: int
    valid_samples: int
    rejected_samples: int
    rejections: Tuple[RejectedSample, ...]
    cube_target_position_error_m: Optional[ScalarSummary]
    final_cube_target_position_error_m: Optional[float]
    lateral_deviation_m: Optional[ScalarSummary]
    orientation_deviation_rad: Optional[ScalarSummary]
    insertion_time_sec: Optional[float]
    time_unavailable_reason: Optional[str]
    samples: Tuple[InsertionPoint, ...]


def _measurement(observation, context):
    if observation is None:
        return "MISSING_MEASUREMENT"
    if not isinstance(observation, PoseMeasurement):
        raise ValueError("typed pose measurement required")
    info = observation.info
    required = (MeasurementQualification.SYNCHRONIZED_POST_STEP if context.mode is EvaluationMode.FORMAL
                else MeasurementQualification.SYNTHETIC)
    if info.qualification is not required:
        raise ValueError("MEASUREMENT_QUALIFICATION_MISMATCH: no legacy/native/synthetic mixing")
    if observation.pose is not None:
        if observation.pose.frame_id != context.frame_id:
            raise ValueError("FRAME_MISMATCH: explicit transform required")
        same_frame(observation.pose)
    if info.time is not None:
        if info.time.basis is not TimeBasis.SIMULATION:
            raise ValueError("TIME_DOMAIN_MISMATCH: trajectory time is not simulation time")
        if info.time.clock_id != context.simulation_session_id:
            raise ValueError("SIMULATION_SESSION_MISMATCH")
    if not info.valid:
        return "INVALID_MEASUREMENT: " + info.invalid_reason
    if not info.post_physics_step or info.time is None or info.time.physics_step is None:
        return "MISSING_POST_STEP_CLOCK"
    return None


def _ordered(time, previous):
    if previous is not None:
        if time.nanoseconds < previous.nanoseconds or time.physics_step < previous.physics_step:
            raise ValueError("SIMULATION_TIME_REVERSED: reset/session cannot be silently merged")
        if time.nanoseconds == previous.nanoseconds or time.physics_step == previous.physics_step:
            return "DUPLICATE_SAMPLE_CLOCK"
    return None


def _stats(points, field):
    return summarize(getattr(point, field) for point in points) if points else None


def evaluate_transport(samples, *, context):
    if not isinstance(context, MetricContext):
        raise ValueError("explicit metric context required")
    rows, points, rejected = tuple(samples), [], []
    reference, reference_index, reference_time, identities, previous = None, None, None, None, None
    for index, row in enumerate(rows):
        if row is None:
            rejected.append(RejectedSample(index, "MISSING_SAMPLE"))
            continue
        if not isinstance(row, TransportSample):
            raise ValueError("typed transport sample required")
        observations = (row.left_tcp, row.right_tcp, row.obj)
        reasons = [_measurement(observation, context) for observation in observations]
        if row.obj is not None and row.obj.entity_id != context.object_id:
            raise ValueError("OBJECT_ID_MISMATCH")
        if row.desired_object_pose is None:
            reasons.append("MISSING_DESIRED_OBJECT_POSE")
        else:
            if row.desired_object_pose.frame_id != context.frame_id:
                raise ValueError("REFERENCE_FRAME_MISMATCH")
            same_frame(row.desired_object_pose)
        if any(reasons):
            rejected.append(RejectedSample(index, "; ".join(reason for reason in reasons if reason)))
            continue
        times = tuple(observation.info.time for observation in observations)
        if max(t.nanoseconds for t in times) - min(t.nanoseconds for t in times) > context.max_stamp_skew_ns:
            rejected.append(RejectedSample(index, "TIMESTAMP_SKEW"))
            continue
        if len({time.physics_step for time in times}) != 1:
            rejected.append(RejectedSample(index, "PHYSICS_STEP_SKEW"))
            continue
        time = row.obj.info.time
        order_reasons = [_ordered(t, p) for t, p in zip(times, previous or (None, None, None))]
        if any(order_reasons):
            rejected.append(RejectedSample(index, "; ".join(r for r in order_reasons if r)))
            continue
        current_ids = tuple(observation.entity_id for observation in observations)
        if len(set(current_ids)) != 3 or (identities is not None and current_ids != identities):
            raise ValueError("TCP_OBJECT_IDENTITY_MISMATCH")
        if reference is None:
            reference = (row.left_tcp.pose, row.right_tcp.pose, row.obj.pose)
            reference_index, reference_time, identities = index, time, current_ids
        left0, right0, obj0 = reference
        points.append(TransportPoint(
            index, time, relative_tcp_error(row.left_tcp.pose, row.right_tcp.pose, left0, right0),
            midpoint_error(row.obj.pose, row.left_tcp.pose, row.right_tcp.pose, obj0, left0, right0),
            position_error(row.obj.pose, row.desired_object_pose), orientation_error(row.obj.pose, obj0),
        ))
        previous = times
    position = _stats(points, "object_position_error_m")
    left0, right0, obj0 = reference if reference else (None, None, None)
    return TransportMetrics(
        context, len(rows), len(points), len(rejected), tuple(rejected), reference_index, reference_time,
        left0, right0, obj0, _stats(points, "relative_tcp_error_m"),
        _stats(points, "box_to_tcp_midpoint_error_m"), position, position.rms if position else None,
        _stats(points, "object_orientation_error_rad"), tuple(points),
    )


def evaluate_insertion(samples, *, context, axis_origin, target, unit_axis):
    if not isinstance(context, MetricContext):
        raise ValueError("explicit metric context required")
    insertion_geometry(axis_origin, axis_origin, target, unit_axis)  # 即使无有效样本也校验配置。
    if axis_origin.frame_id != context.frame_id:
        raise ValueError("REFERENCE_FRAME_MISMATCH")
    rows, points, rejected, previous = tuple(samples), [], [], None
    for index, observation in enumerate(rows):
        reason = _measurement(observation, context)
        if observation is not None and observation.entity_id != context.object_id:
            raise ValueError("OBJECT_ID_MISMATCH")
        if reason is None:
            reason = _ordered(observation.info.time, previous)
        if reason:
            rejected.append(RejectedSample(index, reason))
            continue
        values = insertion_geometry(observation.pose, axis_origin, target, unit_axis)
        points.append(InsertionPoint(index, observation.info.time, *values))
        previous = observation.info.time
    duration = None
    if context.mode is EvaluationMode.SYNTHETIC:
        time_reason = "SYNTHETIC_DATA_NOT_REAL_EXECUTION_TIME"
    elif len(points) < 2:
        time_reason = "FEWER_THAN_TWO_QUALIFIED_SAMPLES"
    elif points[0].input_index != 0 or points[-1].input_index != len(rows) - 1:
        time_reason = "INCOMPLETE_INSERTION_WINDOW_ENDPOINTS"
    else:
        # 仅调用方明确截取的 INSERT_READY→观测结束窗口，不推断 TARGET 到达。
        duration = (points[-1].time.nanoseconds - points[0].time.nanoseconds) * 1e-9
        time_reason = None
    return InsertionMetrics(
        context, axis_origin, target, unit_axis, len(rows), len(points), len(rejected), tuple(rejected),
        _stats(points, "cube_target_position_error_m"),
        points[-1].cube_target_position_error_m if points and points[-1].input_index == len(rows) - 1 else None,
        _stats(points, "lateral_deviation_m"), _stats(points, "orientation_deviation_rad"),
        duration, time_reason, tuple(points),
    )
