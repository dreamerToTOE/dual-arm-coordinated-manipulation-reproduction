"""TASK02-B 数据接口；绝不下发命令或改变机器人/吸附状态。

THIN_ADAPTER 来源：predecessor@631b1f task_event.hpp /
task_trajectory_candidate.hpp / task16_planning_benchmark.cpp。
保留计划事件/相对阶段/显式 seed-trial 语义，不导入旧数值门限。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from .state import Pose, finite_vector, nonnegative_integer
from .wire import WireRecord


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("nonempty identity/text required")


def identities(values, required=True):
    if not isinstance(values, tuple) or (required and not values):
        raise ValueError("explicit immutable identity tuple required")
    for value in values:
        text(value)
    if len(set(values)) != len(values):
        raise ValueError("duplicate identity")


def enum_value(value, kind):
    if not isinstance(value, kind):
        raise ValueError(f"explicit {kind.__name__} required")


class TimeBasis(str, Enum):
    TRAJECTORY_RELATIVE = "TRAJECTORY_RELATIVE"
    SIMULATION = "SIMULATION"


@dataclass(frozen=True)
class TimePoint:
    basis: TimeBasis
    clock_id: str  # trajectory ID / simulation session ID，不能跨 reset/session 混用。
    nanoseconds: int
    physics_step: Optional[int] = None

    def __post_init__(self):
        enum_value(self.basis, TimeBasis)
        text(self.clock_id)
        nonnegative_integer(self.nanoseconds, "time nanoseconds")
        if self.physics_step is not None:
            nonnegative_integer(self.physics_step, "physics_step")
        if self.basis is TimeBasis.TRAJECTORY_RELATIVE and self.physics_step is not None:
            raise ValueError("trajectory time cannot carry a physics step")

    def require_same_clock(self, other):
        if (self.basis, self.clock_id) != (other.basis, other.clock_id):
            raise ValueError("clock domains differ; no implicit wall/trajectory/simulation conversion")


class CommandType(str, Enum):
    JOINT_TARGET = "JOINT_TARGET"
    TASK_POSE = "TASK_POSE"
    HOLD = "HOLD"
    SUCTION_ON = "SUCTION_ON"
    SUCTION_OFF = "SUCTION_OFF"


@dataclass(frozen=True)
class JointTarget:
    robot_id: str
    joint_names: Tuple[str, ...]
    positions_rad: Tuple[float, ...]

    def __post_init__(self):
        text(self.robot_id)
        identities(self.joint_names)
        if not isinstance(self.positions_rad, tuple):
            raise ValueError("immutable joint values required")
        finite_vector(self.positions_rad, len(self.joint_names))


@dataclass(frozen=True)
class TaskPoseTarget:
    robot_id: str
    link_id: str
    pose: Pose

    def __post_init__(self):
        text(self.robot_id)
        text(self.link_id)
        if not isinstance(self.pose, Pose):
            raise ValueError("explicit pose target required")


@dataclass(frozen=True)
class BaselineCommand(WireRecord):
    SCHEMA = "task02.command.v0.1"
    command_id: str
    baseline_id: str
    robot_ids: Tuple[str, ...]
    object_id: Optional[str]
    command_type: CommandType
    frame_id: str
    units: str  # rad / m+quaternion_xyzw / not_applicable；不接受隐式度或毫米。
    issued_at: TimePoint
    deadline: TimePoint
    config_ids: Tuple[str, ...]
    source_ids: Tuple[str, ...]
    joint_targets: Tuple[JointTarget, ...] = ()
    pose_targets: Tuple[TaskPoseTarget, ...] = ()

    def __post_init__(self):
        for value in (self.command_id, self.baseline_id, self.frame_id):
            text(value)
        for values in (self.robot_ids, self.config_ids, self.source_ids):
            identities(values)
        if self.object_id is not None:
            text(self.object_id)
        enum_value(self.command_type, CommandType)
        if not isinstance(self.issued_at, TimePoint) or not isinstance(self.deadline, TimePoint):
            raise ValueError("explicit command clocks required")
        self.issued_at.require_same_clock(self.deadline)
        if self.deadline.nanoseconds < self.issued_at.nanoseconds:
            raise ValueError("deadline before issue time")
        expected = {
            CommandType.JOINT_TARGET: ("joint_space", "rad"),
            CommandType.TASK_POSE: (self.frame_id, "m+quaternion_xyzw"),
        }.get(self.command_type, ("not_applicable", "not_applicable"))
        if (self.frame_id, self.units) != expected:
            raise ValueError("command frame/unit mismatch")
        if not isinstance(self.joint_targets, tuple) or not isinstance(self.pose_targets, tuple):
            raise ValueError("immutable targets required")
        if any(not isinstance(t, JointTarget) for t in self.joint_targets) or any(
                not isinstance(t, TaskPoseTarget) for t in self.pose_targets):
            raise ValueError("typed motion targets required")
        if self.command_type is CommandType.JOINT_TARGET:
            if not self.joint_targets or self.pose_targets:
                raise ValueError("joint command needs only joint targets")
            targets = self.joint_targets
        elif self.command_type is CommandType.TASK_POSE:
            if not self.pose_targets or self.joint_targets:
                raise ValueError("pose command needs only pose targets")
            if any(t.pose.frame_id != self.frame_id for t in self.pose_targets):
                raise ValueError("pose target frame differs")
            targets = self.pose_targets
        else:
            if self.joint_targets or self.pose_targets:
                raise ValueError("hold/suction commands carry no motion target")
            targets = ()
        if targets and (len({t.robot_id for t in targets}) != len(targets)
                        or {t.robot_id for t in targets} != set(self.robot_ids)):
            raise ValueError("each commanded robot needs exactly one target")
        if self.command_type in (CommandType.SUCTION_ON, CommandType.SUCTION_OFF) and self.object_id is None:
            raise ValueError("suction intent requires explicit object identity")


class EventKind(str, Enum):
    SUCTION_ON = "SUCTION_ON"
    ATTACH = "ATTACH"
    SUCTION_OFF = "SUCTION_OFF"
    DETACH = "DETACH"


class EventStatus(str, Enum):
    PLANNED = "PLANNED"
    OBSERVED = "OBSERVED"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class TaskStageMarker(WireRecord):
    SCHEMA = "task02.stage.v0.1"
    name: str
    start: TimePoint
    end: TimePoint

    def __post_init__(self):
        text(self.name)
        if not isinstance(self.start, TimePoint) or not isinstance(self.end, TimePoint):
            raise ValueError("explicit stage clocks required")
        self.start.require_same_clock(self.end)
        if self.start.basis is not TimeBasis.TRAJECTORY_RELATIVE or self.end.nanoseconds < self.start.nanoseconds:
            raise ValueError("stage interval must be ordered trajectory-relative time")


@dataclass(frozen=True)
class TaskEvent(WireRecord):
    SCHEMA = "task02.event.v0.1"
    event_id: str
    kind: EventKind
    status: EventStatus
    time: TimePoint
    stage_id: str
    robot_ids: Tuple[str, ...]
    object_id: str
    source_id: str
    link_id: Optional[str] = None
    command_id: Optional[str] = None
    planned_event_id: Optional[str] = None
    observed_event_id: Optional[str] = None
    attachment_id: Optional[str] = None
    evidence_refs: Tuple[str, ...] = ()
    reason: Optional[str] = None

    def __post_init__(self):
        for value in (self.event_id, self.stage_id, self.object_id, self.source_id):
            text(value)
        identities(self.robot_ids)
        identities(self.evidence_refs, required=False)
        enum_value(self.kind, EventKind)
        enum_value(self.status, EventStatus)
        if not isinstance(self.time, TimePoint):
            raise ValueError("explicit event clock required")
        for value in (self.link_id, self.command_id, self.planned_event_id, self.observed_event_id,
                      self.attachment_id, self.reason):
            if value is not None:
                text(value)
        if self.status is EventStatus.PLANNED:
            if self.time.basis is not TimeBasis.TRAJECTORY_RELATIVE or self.observed_event_id:
                raise ValueError("planned event uses trajectory clock, not observed confirmation")
        elif self.status in (EventStatus.OBSERVED, EventStatus.CONFIRMED):
            if self.time.basis is not TimeBasis.SIMULATION or self.time.physics_step is None:
                raise ValueError("observation/confirmation requires explicit post-step simulation time")
        if self.status is not EventStatus.PLANNED and not self.evidence_refs:
            raise ValueError("observation/confirmation/failure requires raw evidence")
        if self.status is EventStatus.CONFIRMED and not self.observed_event_id:
            raise ValueError("confirmation requires separate prior observation")
        if self.status is EventStatus.OBSERVED and self.observed_event_id is not None:
            raise ValueError("observation cannot be a confirmation")
        if self.status is EventStatus.FAILED and not self.reason:
            raise ValueError("failure requires reason")
        if self.status is EventStatus.FAILED and self.time.basis is TimeBasis.SIMULATION and self.time.physics_step is None:
            raise ValueError("physical failure requires actual physics step")
        if self.kind in (EventKind.ATTACH, EventKind.DETACH):
            if not self.link_id:
                raise ValueError("attach/detach needs exact link identity")
            if self.status in (EventStatus.OBSERVED, EventStatus.CONFIRMED) and not self.attachment_id:
                raise ValueError("SG CLOSED alone is not object attachment evidence")


class EventLedger:
    """仅验证记录因果/同域顺序；不是控制状态机，不触发吸盘或 ATTACH。"""

    def __init__(self):
        self._events = {}
        self._last_times = {}
        self._terminal_observations = set()

    def validate(self, event):
        if not isinstance(event, TaskEvent):
            raise ValueError("typed event required")
        if event.event_id in self._events:
            raise ValueError("duplicate event ID")
        key = (event.time.basis, event.time.clock_id)
        previous = self._last_times.get(key)
        if previous and (event.time.nanoseconds < previous.nanoseconds or
                         (previous.physics_step is not None and event.time.physics_step is not None
                          and event.time.physics_step < previous.physics_step)):
            raise ValueError("event time/step moved backwards in same clock")
        for ref, expected in ((event.planned_event_id, EventStatus.PLANNED),
                              (event.observed_event_id, EventStatus.OBSERVED)):
            if ref is None:
                continue
            earlier = self._events.get(ref)
            if earlier is None or earlier.status is not expected:
                raise ValueError("causal event missing or wrong status")
            if (earlier.kind, earlier.stage_id, earlier.robot_ids, earlier.object_id, earlier.link_id) != (
                    event.kind, event.stage_id, event.robot_ids, event.object_id, event.link_id):
                raise ValueError("causal identity mismatch; suction command is not attach")
            if expected is EventStatus.PLANNED and earlier.command_id is not None and earlier.command_id != event.command_id:
                raise ValueError("referenced plan belongs to another command")
            if expected is EventStatus.OBSERVED:
                earlier.time.require_same_clock(event.time)
                if (earlier.attachment_id != event.attachment_id or earlier.command_id != event.command_id
                        or ref in self._terminal_observations):
                    raise ValueError("attachment/command mismatch or already resolved observation")

    def append(self, event):
        self.validate(event)
        self._events[event.event_id] = event
        self._last_times[(event.time.basis, event.time.clock_id)] = event.time
        if event.observed_event_id and event.status in (EventStatus.CONFIRMED, EventStatus.FAILED):
            self._terminal_observations.add(event.observed_event_id)
        return len(self._events) - 1


class ResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ABORTED = "ABORTED"
    INCOMPLETE = "INCOMPLETE"


class MeasurementQualification(str, Enum):
    UNQUALIFIED = "UNQUALIFIED"
    SYNTHETIC = "SYNTHETIC"
    LEGACY_ASYNCHRONOUS = "LEGACY_ASYNCHRONOUS"
    SYNCHRONIZED_POST_STEP = "SYNCHRONIZED_POST_STEP"


@dataclass(frozen=True)
class BenchmarkResult(WireRecord):
    SCHEMA = "task02.result.v0.1"
    run_id: str
    baseline_id: str
    status: ResultStatus
    claim_scope: str
    measurement_qualification: MeasurementQualification
    evidence_refs: Tuple[str, ...]
    config_ids: Tuple[str, ...]
    source_ids: Tuple[str, ...]
    failure_stage: Optional[str] = None
    reason: Optional[str] = None
    limitations: Tuple[str, ...] = ()

    def __post_init__(self):
        for value in (self.run_id, self.baseline_id, self.claim_scope):
            text(value)
        enum_value(self.status, ResultStatus)
        enum_value(self.measurement_qualification, MeasurementQualification)
        for values in (self.evidence_refs, self.config_ids, self.source_ids):
            identities(values)
        identities(self.limitations, required=False)
        if self.status is ResultStatus.SUCCESS:
            if self.failure_stage is not None or self.reason is not None:
                raise ValueError("success cannot hide failure fields")
        else:
            text(self.failure_stage)
            text(self.reason)
        # SUCCESS 是提交方的带 scope 结果，不执行评分，不提供任何成功数值默认值。


@dataclass(frozen=True)
class SourceRef:
    source_id: str
    path: str
    sha256: str

    def __post_init__(self):
        text(self.source_id)
        text(self.path)
        if len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256):
            raise ValueError("explicit lowercase SHA256 required")


@dataclass(frozen=True)
class RunMetadata(WireRecord):
    SCHEMA = "task02.run.v0.1"
    run_id: str
    task: str
    baseline_id: str
    platform: str
    git_commit: str
    trial_id: int
    seed: Optional[int]  # 必须显式传入 None 或整数；不继承旧默认 seed。
    command: Tuple[str, ...]
    config_ids: Tuple[str, ...]
    config_paths: Tuple[str, ...]
    sources: Tuple[SourceRef, ...]

    def __post_init__(self):
        for value in (self.run_id, self.task, self.baseline_id, self.platform, self.git_commit):
            text(value)
        nonnegative_integer(self.trial_id, "trial_id")
        if self.seed is not None:
            nonnegative_integer(self.seed, "seed")
        identities(self.config_ids)
        identities(self.config_paths)
        if not isinstance(self.command, tuple) or not self.command:
            raise ValueError("explicit immutable command argv required")
        for argument in self.command:
            text(argument)  # argv 可重复；例如同一命令中的多个 -p。
        if not isinstance(self.sources, tuple) or any(not isinstance(s, SourceRef) for s in self.sources):
            raise ValueError("immutable typed source tuple required")
        identities(tuple(s.source_id for s in self.sources))

    @property
    def seed_status(self):
        return "UNSET" if self.seed is None else "SET"
