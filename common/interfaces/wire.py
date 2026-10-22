"""小型、确定性的 JSON 契约编解码；无执行、网络或模拟器依赖。"""

from dataclasses import asdict, fields, is_dataclass
from enum import Enum
import json
import math
from typing import Union, get_args, get_origin, get_type_hints


def canonical_json(value):
    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def decode(value, kind):
    """显式恢复类型；未知字段、enum、bool 冒充数值均拒绝。"""
    origin, args = get_origin(kind), get_args(kind)
    if origin is Union:
        if value is None and type(None) in args:
            return None
        return decode(value, next(t for t in args if t is not type(None)))
    if origin is tuple:
        if not isinstance(value, (tuple, list)):
            raise ValueError("expected array")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(decode(item, args[0]) for item in value)
        if len(value) != len(args):
            raise ValueError("wrong array length")
        return tuple(decode(item, t) for item, t in zip(value, args))
    if isinstance(kind, type) and issubclass(kind, Enum):
        return kind(value)
    if is_dataclass(kind):
        if not isinstance(value, dict):
            raise ValueError("expected object")
        names = {field.name for field in fields(kind)}
        if set(value) - names:
            raise ValueError("unknown contract fields")
        hints = get_type_hints(kind)
        return kind(**{name: decode(item, hints[name]) for name, item in value.items()})
    if kind is float:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("expected finite number")
        return value  # 保留整数/浮点的 JSON 编码，round-trip 不隐式改变字节格式。
    if type(value) is not kind:
        raise ValueError(f"expected {kind.__name__}")
    return value


class WireRecord:
    SCHEMA = "task02.record.v0.1"

    def to_dict(self):
        return {"schema_version": self.SCHEMA, "data": asdict(self)}

    def to_json(self):
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, value):
        if set(value) != {"schema_version", "data"} or value["schema_version"] != cls.SCHEMA:
            raise ValueError("wrong contract schema")
        return decode(value["data"], cls)

    @classmethod
    def from_json(cls, value):
        return cls.from_dict(json.loads(value))
