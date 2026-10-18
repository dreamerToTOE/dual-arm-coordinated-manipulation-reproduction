"""纯数学定义。Task14@631b1f 的位置/四元数/max/RMS 公式薄适配。

无科研成功默认阈值；无钟域转换、测量来源推断或执行副作用。
"""

from dataclasses import dataclass
import math
from typing import Tuple

from common.interfaces.measurement import vector3
from common.interfaces.state import Pose, finite_vector


def subtract(first, second):
    vector3(first)
    vector3(second)
    result = tuple(a - b for a, b in zip(first, second))
    vector3(result)
    return result


def norm(value):
    vector3(value)
    result = math.hypot(*value)
    finite_vector((result,))
    return result


def same_frame(*poses):
    for pose in poses:
        if not isinstance(pose, Pose):
            raise ValueError("explicit pose required")
        # 校验输入而不补零或静默归一化无效四元数；沿用 A 的消息格式契约。
        Pose(pose.frame_id, pose.position_m, pose.quaternion_xyzw, pose.measurement_source)
    if len({pose.frame_id for pose in poses}) != 1:
        raise ValueError("pose frames differ; explicit transform required")


def position_error(actual, desired):
    same_frame(actual, desired)
    return norm(subtract(actual.position_m, desired.position_m))


def orientation_error(actual, desired):
    same_frame(actual, desired)
    first, second = actual.quaternion_xyzw, desired.quaternion_xyzw
    # Task14 quaternionAngle，q/-q 等价；归一化有效消息以抵消格式舍入。
    dot = abs(math.fsum(a * b for a, b in zip(first, second))) / (math.hypot(*first) * math.hypot(*second))
    return 2.0 * math.acos(min(1.0, max(0.0, dot)))


def relative_tcp_error(left, right, initial_left, initial_right):
    same_frame(left, right, initial_left, initial_right)
    return norm(subtract(subtract(right.position_m, left.position_m),
                         subtract(initial_right.position_m, initial_left.position_m)))


def midpoint_offset(obj, left, right):
    same_frame(obj, left, right)
    midpoint = tuple(0.5 * a + 0.5 * b for a, b in zip(left.position_m, right.position_m))
    return subtract(obj.position_m, midpoint)


def midpoint_error(obj, left, right, initial_obj, initial_left, initial_right):
    same_frame(obj, left, right, initial_obj, initial_left, initial_right)
    return norm(subtract(midpoint_offset(obj, left, right),
                         midpoint_offset(initial_obj, initial_left, initial_right)))


@dataclass(frozen=True)
class ScalarSummary:
    count: int
    maximum: float
    rms: float


def summarize(errors):
    values = tuple(errors)
    if not values:
        raise ValueError("no valid samples; no zero-valued summary")
    finite_vector(values)
    if any(value < 0 for value in values):
        raise ValueError("error magnitudes must be nonnegative")
    maximum = max(values)
    # 与 Task14 sqrt(sum(e^2)/N) 等价；缩放避免有限输入平方溢出。
    rms = 0.0 if maximum == 0 else maximum * math.sqrt(math.fsum((e / maximum) ** 2 for e in values) / len(values))
    return ScalarSummary(len(values), maximum, rms)


def insertion_geometry(actual, origin, target, axis: Tuple[float, float, float]):
    """显式名义轴上的投影；progress不截断，保留回退/超调，不判定完成。"""
    same_frame(actual, origin, target)
    vector3(axis)
    axis_norm = norm(axis)
    if abs(axis_norm - 1.0) > 1e-6:  # 向量消息格式，不是 benchmark 成功阈值。
        raise ValueError("explicit unit insertion axis required")
    axis = tuple(component / axis_norm for component in axis)  # 有效单位向量的编码舍入。
    delta = subtract(actual.position_m, origin.position_m)
    extent = math.fsum(a * b for a, b in zip(subtract(target.position_m, origin.position_m), axis))
    if extent <= 0:
        raise ValueError("target must have positive displacement along insertion axis")
    displacement = math.fsum(a * b for a, b in zip(delta, axis))
    lateral = norm(subtract(delta, tuple(displacement * a for a in axis)))
    progress = displacement / extent
    finite_vector((displacement, progress))
    return position_error(actual, target), displacement, progress, lateral, orientation_error(actual, target)
