"""只转换旧 TaskEvent / TaskStageMarker 计划语义；从不生成 OBSERVED。

Source: predecessor@631b1f task_event.hpp / task_trajectory_candidate.hpp.
明确的轨迹 ID + ns 编码；秒到纳秒最多0.5ns格式舍入，不是物理验收容差。
"""

from decimal import Decimal, ROUND_HALF_EVEN

from common.interfaces.exchange import EventKind, EventStatus, TaskEvent, TaskStageMarker, TimeBasis, TimePoint
from common.interfaces.state import finite_vector


def _relative_time(seconds, trajectory_id):
    finite_vector((seconds,))
    if seconds < 0:
        raise ValueError("negative legacy relative time")
    ns = int((Decimal(str(seconds)) * 1_000_000_000).to_integral_value(rounding=ROUND_HALF_EVEN))
    return TimePoint(TimeBasis.TRAJECTORY_RELATIVE, trajectory_id, ns)


def planned_event_from_legacy(data, *, event_id, trajectory_id, robot_id, stage_id, source_id):
    return TaskEvent(
        event_id, EventKind(data["type"]), EventStatus.PLANNED,
        _relative_time(data["time_sec"], trajectory_id), stage_id, (robot_id,),
        data["object_name"], source_id, link_id=data["link_name"],
    )


def planned_stage_from_legacy(data, *, trajectory_id):
    return TaskStageMarker(data["name"], _relative_time(data["start_time_sec"], trajectory_id),
                           _relative_time(data["end_time_sec"], trajectory_id))
