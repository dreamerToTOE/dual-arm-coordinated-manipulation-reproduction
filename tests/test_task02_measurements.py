"""TASK02-C measurement drafts: synthetic/offline only, no estimator/query/sensor."""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from common.interfaces.exchange import MeasurementQualification as Q, TimeBasis, TimePoint
from common.interfaces.measurement import ContactWrench, CollisionDistance, MeasurementInfo, PoseMeasurement
from common.interfaces.state import Pose, StateRecord
from common.interfaces.wire import decode
from common.metrics import EvaluationMode, MetricContext, TransportSample, evaluate_transport, evaluate_insertion


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "results/20261009_TASK02_foundation_interface01/converted_snapshot.json"
STAMP = TimePoint(TimeBasis.SIMULATION, "synthetic_contract_session", 100_000_000, 6)


def info(**changes):
    values = dict(source_id="synthetic_fixture", qualification=Q.SYNTHETIC,
                  time=STAMP, post_physics_step=True, valid=True,
                  evidence_refs=("fixture://offline-only",))
    values.update(changes)
    return MeasurementInfo(**values)


def wrench():
    return ContactWrench("cube", "tool", "world", (1.0, 2.0, 3.0), (0.1, 0.2, 0.3),
                         (0.5, -0.2, 0.4), info())


def distance():
    return CollisionDistance("link", "wall", "world", 0.002,
                             (0.1, 0.2, 0.3), (0.102, 0.2, 0.3), info())


class MeasurementContractTest(unittest.TestCase):
    def test_contact_wrench_round_trip_explicit_reference_and_units(self):
        value = wrench()
        restored = ContactWrench.from_json(value.to_json())
        self.assertEqual(restored, value)
        self.assertEqual(restored.to_json(), value.to_json())
        self.assertEqual(restored.application_point_m, (0.5, -0.2, 0.4))
        self.assertEqual((restored.force_unit, restored.torque_unit, restored.point_unit), ("N", "N*m", "m"))
        # Changing the reference point does not secretly compute a moment shift.
        self.assertEqual(replace(value, application_point_m=(0.0, 0.0, 0.0)).torque_Nm, value.torque_Nm)

    def test_collision_distance_round_trip_signed_convention(self):
        for signed in (-0.002, 0.0, 0.002):
            value = replace(distance(), signed_distance_m=signed)
            restored = CollisionDistance.from_json(value.to_json())
            self.assertEqual(restored, value)
            self.assertEqual(restored.signed_distance_m, signed)
            self.assertFalse(hasattr(restored, "success"))
            self.assertFalse(hasattr(restored, "collision_query"))

    def test_invalid_payloads_are_unavailable_not_zero(self):
        bad_info = info(valid=False, invalid_reason="sensor unavailable", time=None, post_physics_step=False)
        force = ContactWrench("cube", "tool", "world", None, None, None, bad_info)
        gap = CollisionDistance("link", "wall", "world", None, None, None, bad_info)
        pose = PoseMeasurement("cube", None, bad_info)
        for value in (force, gap, pose):
            self.assertEqual(type(value).from_json(value.to_json()), value)
            self.assertFalse(value.info.valid)
        self.assertIsNone(force.force_N)
        self.assertIsNone(gap.signed_distance_m)
        self.assertIsNone(pose.pose)

    def test_missing_valid_wrench_fields_rejected(self):
        for field in ("force_N", "torque_Nm", "application_point_m"):
            with self.assertRaises(ValueError):
                replace(wrench(), **{field: None})
        with self.assertRaises(ValueError):
            PoseMeasurement("cube", None, info())

    def test_missing_valid_distance_fields_rejected(self):
        for field in ("signed_distance_m", "closest_point_a_m", "closest_point_b_m"):
            with self.assertRaises(ValueError):
                replace(distance(), **{field: None})

    def test_nonfinite_bool_wrong_dimension_and_units_rejected(self):
        for vector in ((float("inf"), 0, 0), (float("nan"), 0, 0), (True, 0, 0), (0, 0), [0, 0, 0]):
            with self.assertRaises(ValueError):
                replace(wrench(), force_N=vector)
            with self.assertRaises(ValueError):
                replace(distance(), closest_point_a_m=vector)
        for scalar in (float("inf"), float("nan"), True):
            with self.assertRaises(ValueError):
                replace(distance(), signed_distance_m=scalar)
        for changes in (dict(force_unit="kN"), dict(torque_unit="N*mm"), dict(point_unit="mm"),
                        dict(frame_id=""), dict(by_body_id="cube")):
            with self.assertRaises(ValueError):
                replace(wrench(), **changes)
        for changes in (dict(distance_unit="mm"), dict(frame_id=""), dict(body_b_id="link")):
            with self.assertRaises(ValueError):
                replace(distance(), **changes)

    def test_validity_and_evidence_qualification_are_explicit(self):
        for changes in (dict(valid="true"), dict(post_physics_step=1), dict(evidence_refs=()),
                        dict(valid=False), dict(invalid_reason="hidden failure"), dict(source_id="")):
            with self.assertRaises(ValueError):
                info(**changes)
        raw = info(qualification=Q.UNQUALIFIED, time=None, post_physics_step=False)
        self.assertTrue(raw.valid)  # Valid data format is not scientific eligibility.

    def test_post_step_clock_and_legacy_promotion_guards(self):
        with self.assertRaises(ValueError):
            info(time=TimePoint(TimeBasis.TRAJECTORY_RELATIVE, "plan", 0))
        with self.assertRaises(ValueError):
            info(time=TimePoint(TimeBasis.SIMULATION, "sim", 0))
        with self.assertRaises(ValueError):
            info(qualification=Q.SYNCHRONIZED_POST_STEP)
        with self.assertRaises(ValueError):
            info(qualification=Q.SYNCHRONIZED_POST_STEP, source_id="native", post_physics_step=False)
        with self.assertRaises(ValueError):
            info(qualification=Q.LEGACY_ASYNCHRONOUS)
        declared = info(qualification=Q.SYNCHRONIZED_POST_STEP, source_id="declared_post_step_TEST_DOUBLE")
        with self.assertRaises(ValueError):
            PoseMeasurement("cube", Pose("world", (0, 0, 0), (0, 0, 0, 1), "legacy_USD_feedback"), declared)

    def test_strict_wire_fields_and_qualification_round_trip(self):
        value = json.loads(wrench().to_json())
        value["data"]["info"]["qualification"] = "ESTIMATED_REAL"
        with self.assertRaises(ValueError):
            ContactWrench.from_dict(value)
        value = json.loads(distance().to_json())
        value["data"]["new_fcl_query_flag"] = True
        with self.assertRaises(ValueError):
            CollisionDistance.from_dict(value)
        with self.assertRaises(ValueError):
            ContactWrench.from_json(distance().to_json())

    def test_contracts_and_metric_calls_have_no_execution_side_effects(self):
        with patch("socket.socket", side_effect=AssertionError("network")), \
                patch("subprocess.Popen", side_effect=AssertionError("process")), \
                patch("os.system", side_effect=AssertionError("shell")):
            ContactWrench.from_json(wrench().to_json())
            CollisionDistance.from_json(distance().to_json())
            ctx = MetricContext("world", STAMP.clock_id, "cube", EvaluationMode.SYNTHETIC, 0)
            pose = Pose("world", (0, 0, 0), (0, 0, 0, 1), "specified_reference")
            evaluate_transport([], context=ctx)
            evaluate_insertion([], context=ctx, axis_origin=pose,
                               target=replace(pose, position_m=(1, 0, 0)), unit_axis=(1, 0, 0))
        for value in (wrench(), distance()):
            for method in ("execute", "send", "publish", "step", "estimate", "query"):
                self.assertFalse(hasattr(value, method))
        for path in (ROOT / "common/interfaces/measurement.py", ROOT / "common/metrics/math.py",
                     ROOT / "common/metrics/evaluate.py"):
            text = path.read_text()
            for forbidden in ("import rclpy", "import rospy", "import omni", "import moveit", "import mujoco"):
                self.assertNotIn(forbidden, text)

    def test_historical_task02a_snapshot_is_compatibility_only(self):
        before = hashlib.sha256(HISTORY.read_bytes()).hexdigest()
        state = decode(json.loads(HISTORY.read_text())["state"], StateRecord)
        legacy = info(source_id="legacy_snapshot", qualification=Q.LEGACY_ASYNCHRONOUS,
                      time=None, post_physics_step=False, evidence_refs=(str(HISTORY),))
        obs = PoseMeasurement(state.objects[0].object_id, state.objects[0].pose, legacy)
        self.assertEqual(PoseMeasurement.from_json(obs.to_json()), obs)
        ctx = MetricContext(obs.pose.frame_id, "not_a_real_session", obs.entity_id, EvaluationMode.FORMAL, 0)
        with self.assertRaisesRegex(ValueError, "QUALIFICATION"):
            evaluate_insertion((obs,), context=ctx, axis_origin=obs.pose,
                               target=replace(obs.pose, position_m=(obs.pose.position_m[0] + 1, *obs.pose.position_m[1:])),
                               unit_axis=(1, 0, 0))
        with self.assertRaises(ValueError):
            replace(obs, info=info(source_id="declared_native_TEST_DOUBLE", qualification=Q.SYNCHRONIZED_POST_STEP))
        self.assertEqual(before, hashlib.sha256(HISTORY.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
