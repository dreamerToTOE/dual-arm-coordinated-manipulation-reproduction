"""TASK02-C test doubles only; these are not Isaac/MuJoCo runtime adapters.

Both formats carry explicitly SYNTHETIC metadata. No installed simulator is
required and neither source can provide a scientific execution-time claim.
"""

from decimal import Decimal

from common.interfaces.exchange import MeasurementQualification, TimeBasis, TimePoint
from common.interfaces.measurement import MeasurementInfo, PoseMeasurement
from common.interfaces.state import Pose
from common.metrics.evaluate import EvaluationMode, MetricContext, TransportSample


SESSION = "synthetic_session_1"
IDENTITY = (0.0, 0.0, 0.0, 1.0)


def synthetic_context(*, skew_ns=0):
    return MetricContext("world", SESSION, "cube", EvaluationMode.SYNTHETIC, skew_ns)


class IsaacLikeSyntheticInput:
    """Independent dict/xyzw/integer-nanosecond decoder; no simulator import."""

    SOURCE = "synthetic_isaac_like_test_double"

    @classmethod
    def pose(cls, raw):
        if raw["position_unit"] != "m" or raw["quaternion_order"] != "xyzw":
            raise ValueError("explicit synthetic m/xyzw format required")
        return Pose(raw["header"]["frame_id"],
                    tuple(raw["position"][axis] for axis in ("x", "y", "z")),
                    tuple(raw["orientation"][axis] for axis in ("x", "y", "z", "w")),
                    cls.SOURCE)

    @classmethod
    def measurement(cls, raw):
        if raw is None:
            return None
        header = raw["header"]
        clock = TimePoint(TimeBasis.SIMULATION, header["session_id"],
                          header["stamp_ns"], header["physics_step"])
        valid = raw["valid"]
        info = MeasurementInfo(cls.SOURCE, MeasurementQualification.SYNTHETIC,
                               clock, raw["post_physics_step"], valid,
                               ("synthetic://isaac-like-fixture",), raw.get("invalid_reason"))
        payload = cls.pose(raw) if "position" in raw and "orientation" in raw else None
        return PoseMeasurement(raw["entity_id"], payload, info)

    @classmethod
    def transport(cls, raw):
        desired = cls.pose(raw["desired"]) if raw["desired"] is not None else None
        return TransportSample(cls.measurement(raw["left"]), cls.measurement(raw["right"]),
                               cls.measurement(raw["cube"]), desired)


class MujocoLikeSyntheticInput:
    """Independent arrays/wxyz/seconds decoder; no simulator import.

    Decimal conversion must exactly represent an integer number of ns. This is
    test input conversion, not a trajectory/simulation domain conversion.
    """

    SOURCE = "synthetic_mujoco_like_test_double"

    @classmethod
    def pose(cls, raw):
        if raw["length_unit"] != "m" or raw["rotation_order"] != "wxyz":
            raise ValueError("explicit synthetic m/wxyz format required")
        w, x, y, z = raw["rotation"]
        return Pose(raw["frame"], tuple(raw["translation"]), (x, y, z, w), cls.SOURCE)

    @classmethod
    def measurement(cls, raw):
        if raw is None:
            return None
        seconds = Decimal(str(raw["sim_seconds"]))
        ns = seconds * Decimal(1_000_000_000)
        if not ns.is_finite() or ns != ns.to_integral_value():
            raise ValueError("synthetic seconds must exactly represent integer ns")
        clock = TimePoint(TimeBasis.SIMULATION, raw["session"], int(ns), raw["step"])
        info = MeasurementInfo(cls.SOURCE, MeasurementQualification.SYNTHETIC, clock,
                               raw["after_step"], raw["valid"],
                               ("synthetic://mujoco-like-fixture",), raw.get("invalid_reason"))
        payload = cls.pose(raw) if "translation" in raw and "rotation" in raw else None
        return PoseMeasurement(raw["body"], payload, info)

    @classmethod
    def transport(cls, raw):
        desired = cls.pose(raw["reference"]) if raw["reference"] is not None else None
        return TransportSample(cls.measurement(raw["tcp_a"]), cls.measurement(raw["tcp_b"]),
                               cls.measurement(raw["object"]), desired)


def isaac_raw(entity, position, *, index=0, quaternion=IDENTITY):
    return {
        "entity_id": entity, "header": {"frame_id": "world", "session_id": SESSION,
        "stamp_ns": index * 1_000_000_000, "physics_step": index + 1},
        "position_unit": "m", "quaternion_order": "xyzw",
        "position": dict(zip(("x", "y", "z"), position)),
        "orientation": dict(zip(("x", "y", "z", "w"), quaternion)),
        "valid": True, "post_physics_step": True,
    }


def mujoco_raw(entity, position, *, index=0, quaternion=IDENTITY):
    x, y, z, w = quaternion
    return {
        "body": entity, "frame": "world", "session": SESSION,
        "sim_seconds": str(index), "step": index + 1,
        "length_unit": "m", "rotation_order": "wxyz",
        "translation": list(position), "rotation": [w, x, y, z],
        "valid": True, "after_step": True,
    }


def paired_transport_inputs(*, positions=None, orientations=None, count=4,
                            constant_midpoint_offset=(0.0, 0.0, 0.0)):
    """Known artificial trajectory x=.1*i; each desired pose is explicit.

    Baseline TCP separation is 0.4m in Y. Object may have a constant fixture
    offset from TCP midpoint; Task14 measures its change, not its absolute value.
    `positions` is a per-sample object offset from the explicit desired pose.
    """
    positions = positions if positions is not None else [(0.0, 0.0, 0.0)] * count
    orientations = orientations if orientations is not None else [IDENTITY] * count
    if len(positions) != count or len(orientations) != count:
        raise ValueError("explicit fixture arrays must match requested sample count")
    isaac, mujoco = [], []
    for index in range(count):
        desired = (0.1 * index, 0.0, 0.5)
        midpoint = tuple(a - b for a, b in zip(desired, constant_midpoint_offset))
        left = (midpoint[0], midpoint[1] + 0.2, midpoint[2])
        right = (midpoint[0], midpoint[1] - 0.2, midpoint[2])
        actual = tuple(a + b for a, b in zip(desired, positions[index]))
        isaac.append({
            "left": isaac_raw("left_tcp", left, index=index),
            "right": isaac_raw("right_tcp", right, index=index),
            "cube": isaac_raw("cube", actual, index=index, quaternion=orientations[index]),
            "desired": isaac_raw("cube", desired, index=index),
        })
        mujoco.append({
            "tcp_a": mujoco_raw("left_tcp", left, index=index),
            "tcp_b": mujoco_raw("right_tcp", right, index=index),
            "object": mujoco_raw("cube", actual, index=index, quaternion=orientations[index]),
            "reference": mujoco_raw("cube", desired, index=index),
        })
    return isaac, mujoco


def paired_transport_samples(**kwargs):
    isaac, mujoco = paired_transport_inputs(**kwargs)
    return (tuple(IsaacLikeSyntheticInput.transport(row) for row in isaac),
            tuple(MujocoLikeSyntheticInput.transport(row) for row in mujoco))


def numeric_transport(report):
    """Only numeric/math fields; source provenance intentionally remains distinct."""
    return {key: value for key, value in report.to_dict()["data"].items()
            if key not in ("reference_left_tcp", "reference_right_tcp", "reference_object")}


def synthetic_example():
    """Reusable small offline example, with no formal execution-time result."""
    import math
    from common.metrics.evaluate import evaluate_transport, evaluate_insertion

    offsets = [(0.01 * index, 0.0, 0.0) for index in range(4)]
    orientations = [(0.0, 0.0, math.sin(0.05 * index), math.cos(0.05 * index)) for index in range(4)]
    first, second = paired_transport_samples(positions=offsets, orientations=orientations)
    context = synthetic_context()
    a = evaluate_transport(first, context=context)
    b = evaluate_transport(second, context=context)
    origin = Pose("world", (0.0, 0.0, 0.5), IDENTITY, "explicit_synthetic_axis_origin")
    target = Pose("world", (0.33, 0.0, 0.5), IDENTITY, "explicit_synthetic_target")
    insert_a = evaluate_insertion(tuple(row.obj for row in first), context=context,
                                  axis_origin=origin, target=target, unit_axis=(1.0, 0.0, 0.0))
    insert_b = evaluate_insertion(tuple(row.obj for row in second), context=context,
                                  axis_origin=origin, target=target, unit_axis=(1.0, 0.0, 0.0))
    if numeric_transport(a) != numeric_transport(b) or insert_a.to_json() != insert_b.to_json():
        raise ValueError("synthetic adapter numeric parity failed")
    return {
        "schema_version": "task02.synthetic_metrics_example.v0.1",
        "evidence_class": "SYNTHETIC_OFFLINE_NOT_SCIENTIFIC",
        "seed": None, "seed_status": "UNSET_NO_RANDOM_INPUT",
        "source_kind": "TWO_TEST_DOUBLES_NO_SIMULATOR_RUNTIME",
        "fixture_definition": {
            "samples": 4, "timestamps_ns": [0, 1_000_000_000, 2_000_000_000, 3_000_000_000],
            "physics_steps": [1, 2, 3, 4], "explicit_stamp_skew_policy_ns": 0,
            "desired_object_m": [[0.1 * i, 0.0, 0.5] for i in range(4)],
            "object_translation_offset_m": offsets, "object_yaw_rad": [0.1 * i for i in range(4)],
            "left_right_tcp_separation_m": 0.4,
            "insertion_axis_origin_m": origin.position_m, "insertion_target_m": target.position_m,
        },
        "numeric_source_consistency": True,
        "transport": {"isaac_like": a.to_dict(), "mujoco_like": b.to_dict()},
        "insertion": {"isaac_like": insert_a.to_dict(), "mujoco_like": insert_b.to_dict()},
        "limitations": ["No native post-step attestation", "No formal execution duration",
                        "No automatic benchmark success decision", "No historical thresholds imported"],
    }


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from common.interfaces.wire import canonical_json

    parser = argparse.ArgumentParser(description="Synthetic offline TASK02-C metrics file example only")
    parser.add_argument("--output", required=True, help="explicit new artifact path; never overwrite")
    args = parser.parse_args()
    example = synthetic_example()
    with Path(args.output).open("x", encoding="utf-8") as stream:
        stream.write(canonical_json(example) + "\n")
    print("Synthetic metrics example saved; no simulator, execution-time or SUCCESS claim.")
