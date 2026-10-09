"""TASK02-C pure offline mathematics/measurement regression, synthetic only."""

from copy import deepcopy
from dataclasses import replace
import math
import unittest
from unittest.mock import patch

from common.interfaces.exchange import MeasurementQualification, TimeBasis, TimePoint
from common.interfaces.measurement import ContactWrench, CollisionDistance, MeasurementInfo, PoseMeasurement
from common.interfaces.state import Pose
from common.metrics.evaluate import (
    EvaluationMode, InsertionMetrics, MetricContext, TransportMetrics,
    TransportSample, evaluate_insertion, evaluate_transport,
)
from common.metrics.math import (
    insertion_geometry, midpoint_error, orientation_error, position_error,
    relative_tcp_error, subtract, summarize,
)
from task02c_synthetic_inputs import (
    IDENTITY, SESSION, IsaacLikeSyntheticInput, MujocoLikeSyntheticInput,
    isaac_raw, mujoco_raw, numeric_transport, paired_transport_inputs,
    paired_transport_samples, synthetic_context,
)


def pose(position=(0.0, 0.0, 0.0), quaternion=IDENTITY, *, frame="world", source="synthetic_target"):
    return Pose(frame, tuple(position), tuple(quaternion), source)


def yaw(angle):
    return (0.0, 0.0, math.sin(angle / 2.0), math.cos(angle / 2.0))


def observation(position=(0.0, 0.0, 0.0), *, index=0, entity="cube", quaternion=IDENTITY):
    return IsaacLikeSyntheticInput.measurement(isaac_raw(entity, position, index=index, quaternion=quaternion))


def replace_time(item, **changes):
    return replace(item, info=replace(item.info, time=replace(item.info.time, **changes)))


def declared_post_step_test_double(item):
    """TEST DOUBLE exercises declared-qualified branch, not native attestation.

    These fabricated observations must never be published as scientific evidence.
    Real adapters/native timestamp validation are out of this offline test scope.
    """
    return replace(item, pose=replace(item.pose, measurement_source="declared_post_step_TEST_DOUBLE"),
                   info=replace(item.info, source_id="declared_post_step_TEST_DOUBLE",
                                qualification=MeasurementQualification.SYNCHRONIZED_POST_STEP,
                                evidence_refs=("test-double://NOT_REAL_PHYSICS",)))


class PureMetricMathTest(unittest.TestCase):
    def test_zero_position_orientation_and_quaternion_sign(self):
        item = pose((1.0, 2.0, 3.0), yaw(0.2))
        self.assertEqual(position_error(item, item), 0.0)
        self.assertAlmostEqual(orientation_error(item, item), 0.0)
        opposite = replace(item, quaternion_xyzw=tuple(-v for v in item.quaternion_xyzw))
        self.assertAlmostEqual(orientation_error(item, opposite), 0.0)

    def test_known_fixed_translation_and_rotation(self):
        self.assertAlmostEqual(position_error(pose((0.03, 0.04, 0.0)), pose()), 0.05)
        self.assertAlmostEqual(orientation_error(pose(quaternion=yaw(0.4)), pose()), 0.4)

    def test_task14_initial_relative_and_midpoint_definitions(self):
        left0, right0, obj0 = pose((-0.2, 0, 0)), pose((0.2, 0, 0)), pose((0, 0, 0.1))
        left, right, obj = pose((-0.1, 0, 0)), pose((0.3, 0, 0)), pose((0.1, 0, 0.1))
        self.assertAlmostEqual(relative_tcp_error(left, right, left0, right0), 0.0)
        self.assertAlmostEqual(midpoint_error(obj, left, right, obj0, left0, right0), 0.0)
        self.assertAlmostEqual(relative_tcp_error(left, pose((0.33, 0, 0)), left0, right0), 0.03)
        self.assertAlmostEqual(midpoint_error(pose((0.1, 0, 0.13)), left, right, obj0, left0, right0), 0.03)

    def test_continuous_error_max_rms_and_different_sample_counts(self):
        report = summarize((0.0, 0.03, 0.04))
        self.assertEqual(report.count, 3)
        self.assertEqual(report.maximum, 0.04)
        self.assertAlmostEqual(report.rms, math.sqrt(0.0025 / 3.0))
        self.assertEqual(summarize((0.02,) * 7).rms, summarize((0.02,) * 2).rms)
        self.assertTrue(math.isfinite(summarize((1e300, 1e300)).rms))
        for invalid in ((), (-1,), (float("nan"),), (float("inf"),), (True,)):
            with self.assertRaises(ValueError):
                summarize(invalid)

    def test_explicit_axis_projection_lateral_negative_and_overshoot(self):
        origin, target = pose((1, 2, 3)), pose((1, 4, 3))
        values = insertion_geometry(pose((1.3, 3, 3.4)), origin, target, (0.0, 1.0, 0.0))
        self.assertAlmostEqual(values[0], math.sqrt(1.25))
        self.assertEqual(values[1], 1.0)
        self.assertEqual(values[2], 0.5)
        self.assertAlmostEqual(values[3], 0.5)
        self.assertEqual(insertion_geometry(pose((1, 1, 3)), origin, target, (0, 1, 0))[2], -0.5)
        self.assertEqual(insertion_geometry(pose((1, 5, 3)), origin, target, (0, 1, 0))[2], 1.5)
        for axis in ((0, 0, 0), (0, 2, 0), (0, float("nan"), 0)):
            with self.assertRaises(ValueError):
                insertion_geometry(origin, origin, target, axis)
        with self.assertRaises(ValueError):
            insertion_geometry(origin, origin, pose((1, 1, 3)), (0, 1, 0))

    def test_vector_lengths_are_checked_before_subtraction(self):
        for first, second in (((1, 2, 3, 4), (1, 2, 3)), ((1, 2), (1, 2, 3))):
            with self.assertRaises(ValueError):
                subtract(first, second)


class SyntheticAdapterMetricTest(unittest.TestCase):
    def test_two_independent_adapters_zero_error(self):
        isaac, mujoco = paired_transport_samples()
        a = evaluate_transport(isaac, context=synthetic_context())
        b = evaluate_transport(mujoco, context=synthetic_context())
        self.assertEqual(numeric_transport(a), numeric_transport(b))
        self.assertEqual(a.valid_samples, 4)
        self.assertEqual(a.rejected_samples, 0)
        for summary in (a.relative_tcp_error_m, a.box_to_tcp_midpoint_error_m,
                        a.object_position_error_m, a.object_orientation_error_rad):
            self.assertAlmostEqual(summary.maximum, 0.0)
            self.assertAlmostEqual(summary.rms, 0.0)
        self.assertFalse(hasattr(a, "status"))
        self.assertFalse(hasattr(a, "success"))

    def test_fixed_translation_rmse_not_relative_geometry_error(self):
        isaac, mujoco = paired_transport_samples(count=5, positions=[(0.03, 0.04, 0.0)] * 5)
        a = evaluate_transport(isaac, context=synthetic_context())
        b = evaluate_transport(mujoco, context=synthetic_context())
        self.assertEqual(numeric_transport(a), numeric_transport(b))
        self.assertAlmostEqual(a.object_position_rmse_m, 0.05)
        self.assertAlmostEqual(a.box_to_tcp_midpoint_error_m.maximum, 0.0)
        self.assertAlmostEqual(a.relative_tcp_error_m.maximum, 0.0)

    def test_constant_initial_midpoint_offset_is_not_failure(self):
        first, second = paired_transport_samples(constant_midpoint_offset=(0.0, 0.0, 0.1))
        for samples in (first, second):
            result = evaluate_transport(samples, context=synthetic_context())
            self.assertAlmostEqual(result.box_to_tcp_midpoint_error_m.maximum, 0.0)
            self.assertAlmostEqual(result.object_position_rmse_m, 0.0)

    def test_fixed_orientation_uses_first_accepted_reference(self):
        first, second = paired_transport_samples(orientations=[yaw(0.4)] * 4)
        for samples in (first, second):
            report = evaluate_transport(samples, context=synthetic_context())
            self.assertAlmostEqual(report.object_orientation_error_rad.maximum, 0.0)
        first, second = paired_transport_samples(orientations=[IDENTITY] + [yaw(0.4)] * 3)
        a = evaluate_transport(first, context=synthetic_context())
        b = evaluate_transport(second, context=synthetic_context())
        self.assertEqual(numeric_transport(a), numeric_transport(b))
        self.assertAlmostEqual(a.object_orientation_error_rad.maximum, 0.4)
        self.assertAlmostEqual(a.object_orientation_error_rad.rms, math.sqrt(3 * 0.4 ** 2 / 4))

    def test_continuous_object_error_max_rms_and_roundtrip(self):
        offsets = [(0, 0, 0), (0.03, 0, 0), (0.04, 0, 0)]
        first, second = paired_transport_samples(count=3, positions=offsets)
        a = evaluate_transport(first, context=synthetic_context())
        b = evaluate_transport(second, context=synthetic_context())
        self.assertEqual(numeric_transport(a), numeric_transport(b))
        self.assertAlmostEqual(a.object_position_error_m.maximum, 0.04)
        self.assertAlmostEqual(a.object_position_rmse_m, math.sqrt(0.0025 / 3))
        restored = TransportMetrics.from_json(a.to_json())
        self.assertEqual(a, restored)
        self.assertEqual(a.to_json(), restored.to_json())

    def test_reference_is_first_valid_sample_and_missing_counted(self):
        samples, _ = paired_transport_samples(count=3, orientations=[yaw(1.0), yaw(0.4), yaw(0.4)])
        rows = (None, replace(samples[0], desired_object_pose=None), *samples[1:])
        report = evaluate_transport(rows, context=synthetic_context())
        self.assertEqual((report.input_samples, report.valid_samples, report.rejected_samples), (4, 2, 2))
        self.assertEqual(report.reference_input_index, 2)
        self.assertAlmostEqual(report.object_orientation_error_rad.maximum, 0.0)
        self.assertEqual(report.rejections[0].reason, "MISSING_SAMPLE")
        self.assertIn("MISSING_DESIRED", report.rejections[1].reason)

    def test_invalid_and_unavailable_samples_rejected_without_zero_fill(self):
        samples, _ = paired_transport_samples(count=2)
        invalid = replace(samples[0].obj, pose=None, info=replace(samples[0].obj.info, valid=False,
                          invalid_reason="TEST_DOUBLE unavailable payload"))
        no_clock = replace(samples[1].obj, info=replace(samples[1].obj.info, time=None, post_physics_step=False))
        report = evaluate_transport((replace(samples[0], obj=invalid), replace(samples[1], obj=no_clock)),
                                    context=synthetic_context())
        self.assertEqual(report.valid_samples, 0)
        self.assertEqual(report.rejected_samples, 2)
        self.assertIsNone(report.object_position_rmse_m)
        self.assertIsNone(report.reference_object)
        self.assertIsNone(report.relative_tcp_error_m)
        self.assertIn("INVALID_MEASUREMENT", report.rejections[0].reason)
        self.assertIn("MISSING_POST_STEP_CLOCK", report.rejections[1].reason)

    def test_frame_domain_session_and_qualification_reject_series(self):
        samples, _ = paired_transport_samples(count=2)
        cube = samples[1].obj
        legacy_info = MeasurementInfo("legacy_saved_snapshot", MeasurementQualification.LEGACY_ASYNCHRONOUS,
                                      None, False, True, ("historical://task26",))
        cases = (
            replace(cube, pose=replace(cube.pose, frame_id="other")),
            replace(cube, info=replace(cube.info, time=TimePoint(TimeBasis.TRAJECTORY_RELATIVE, "plan", 0),
                                      post_physics_step=False)),
            replace_time(cube, clock_id="other_session"),
            replace(cube, info=legacy_info),
            declared_post_step_test_double(cube),
        )
        for modified in cases:
            with self.subTest(modified=modified), self.assertRaises(ValueError):
                evaluate_transport((samples[0], replace(samples[1], obj=modified)), context=synthetic_context())
        with self.assertRaises(ValueError):
            evaluate_transport((replace(samples[0], desired_object_pose=pose(frame="other")),),
                               context=synthetic_context())

    def test_explicit_timestamp_skew_policy_and_physics_step_rejection(self):
        samples, _ = paired_transport_samples(count=2)
        skewed = replace(samples[1], left_tcp=replace_time(samples[1].left_tcp, nanoseconds=1_000_000_005))
        strict = evaluate_transport((samples[0], skewed), context=synthetic_context())
        loose = evaluate_transport((samples[0], skewed), context=synthetic_context(skew_ns=5))
        self.assertEqual((strict.valid_samples, strict.rejected_samples), (1, 1))
        self.assertEqual(strict.rejections[0].reason, "TIMESTAMP_SKEW")
        self.assertEqual(loose.valid_samples, 2)
        step_skew = replace(samples[1], right_tcp=replace_time(samples[1].right_tcp, physics_step=99))
        report = evaluate_transport((samples[0], step_skew), context=synthetic_context())
        self.assertEqual(report.rejections[0].reason, "PHYSICS_STEP_SKEW")
        with self.assertRaises(TypeError):
            MetricContext("world", SESSION, "cube", EvaluationMode.SYNTHETIC)

    def test_duplicate_and_reversed_clocks_and_entity_changes(self):
        samples, _ = paired_transport_samples(count=2)
        report = evaluate_transport((samples[0], samples[0], samples[1]), context=synthetic_context())
        self.assertIn("DUPLICATE_SAMPLE_CLOCK", report.rejections[0].reason)
        with self.assertRaises(ValueError):
            evaluate_transport((samples[1], samples[0]), context=synthetic_context())
        wrong_tcp = replace(samples[1], left_tcp=replace(samples[1].left_tcp, entity_id="other_tcp"))
        with self.assertRaises(ValueError):
            evaluate_transport((samples[0], wrong_tcp), context=synthetic_context())
        wrong_cube = replace(samples[1], obj=replace(samples[1].obj, entity_id="other_cube"))
        with self.assertRaises(ValueError):
            evaluate_transport((samples[0], wrong_cube), context=synthetic_context())

    def test_each_channel_reversal_and_duplicate_do_not_hide_step_reversal(self):
        samples, _ = paired_transport_samples(count=2)
        first = replace(samples[0], left_tcp=replace_time(samples[0].left_tcp, nanoseconds=5))
        second = replace(samples[1],
                         left_tcp=replace_time(samples[1].left_tcp, nanoseconds=4),
                         right_tcp=replace_time(samples[1].right_tcp, nanoseconds=1),
                         obj=replace_time(samples[1].obj, nanoseconds=1))
        with self.assertRaises(ValueError):
            evaluate_transport((first, second), context=synthetic_context(skew_ns=5))
        earlier_step = tuple(replace_time(item, physics_step=0) for item in
                             (samples[0].left_tcp, samples[0].right_tcp, samples[0].obj))
        duplicate_stamp_back_step = replace(samples[0], left_tcp=earlier_step[0],
                                            right_tcp=earlier_step[1], obj=earlier_step[2])
        with self.assertRaises(ValueError):
            evaluate_transport((samples[0], duplicate_stamp_back_step), context=synthetic_context())

    def test_different_sample_counts_and_empty_summary(self):
        for count in (1, 3, 7):
            first, second = paired_transport_samples(count=count, positions=[(0.02, 0, 0)] * count)
            a = evaluate_transport(first, context=synthetic_context())
            b = evaluate_transport(second, context=synthetic_context())
            self.assertEqual(numeric_transport(a), numeric_transport(b))
            self.assertEqual(a.valid_samples, count)
            self.assertAlmostEqual(a.object_position_rmse_m, 0.02)
        empty = evaluate_transport((), context=synthetic_context())
        self.assertEqual((empty.input_samples, empty.valid_samples), (0, 0))
        self.assertIsNone(empty.object_position_rmse_m)
        self.assertIsNone(empty.reference_time)

    def test_adapter_bad_fields_units_quaternion_and_nonfinite_rejected(self):
        for factory, adapter, position_key, quaternion_key in (
            (isaac_raw, IsaacLikeSyntheticInput, "position", "orientation"),
            (mujoco_raw, MujocoLikeSyntheticInput, "translation", "rotation"),
        ):
            invalid_q = factory("cube", (0, 0, 0), quaternion=(0, 0, 0, 0))
            invalid_p = factory("cube", (float("nan"), 0, 0))
            missing = factory("cube", (0, 0, 0))
            del missing[position_key]
            for raw in (invalid_q, invalid_p, missing):
                with self.assertRaises(ValueError):
                    adapter.measurement(raw)
            malformed = factory("cube", (0, 0, 0))
            del malformed["entity_id" if adapter is IsaacLikeSyntheticInput else "body"]
            with self.assertRaises(KeyError):
                adapter.measurement(malformed)
        raw = mujoco_raw("cube", (0, 0, 0))
        raw["sim_seconds"] = "0.0000000001"
        with self.assertRaises(ValueError):
            MujocoLikeSyntheticInput.measurement(raw)
        raw["sim_seconds"] = "NaN"
        with self.assertRaises(ValueError):
            MujocoLikeSyntheticInput.measurement(raw)

    def test_pure_calculation_has_no_process_network_or_controller_side_effect(self):
        samples, _ = paired_transport_samples()
        with patch("socket.socket", side_effect=AssertionError("network")), \
                patch("subprocess.Popen", side_effect=AssertionError("process")), \
                patch("os.system", side_effect=AssertionError("shell")):
            report = evaluate_transport(samples, context=synthetic_context())
            TransportMetrics.from_json(report.to_json())


class InsertionMetricTest(unittest.TestCase):
    def test_cross_adapter_progress_lateral_orientation_and_no_real_duration(self):
        origin, target = pose((0, 0, 0)), pose((2, 0, 0))
        positions = ((0, 0, 0), (1, 0.3, 0.4), (2, 0, 0), (3, 0, 0))
        angles = (0.0, 0.2, 0.2, 0.2)
        a = tuple(IsaacLikeSyntheticInput.measurement(isaac_raw("cube", p, index=i, quaternion=yaw(angles[i])))
                  for i, p in enumerate(positions))
        b = tuple(MujocoLikeSyntheticInput.measurement(mujoco_raw("cube", p, index=i, quaternion=yaw(angles[i])))
                  for i, p in enumerate(positions))
        ar = evaluate_insertion(a, context=synthetic_context(), axis_origin=origin, target=target, unit_axis=(1, 0, 0))
        br = evaluate_insertion(b, context=synthetic_context(), axis_origin=origin, target=target, unit_axis=(1, 0, 0))
        self.assertEqual(ar.to_json(), br.to_json())
        self.assertEqual([sample.axial_progress for sample in ar.samples], [0.0, 0.5, 1.0, 1.5])
        self.assertAlmostEqual(ar.lateral_deviation_m.maximum, 0.5)
        self.assertAlmostEqual(ar.orientation_deviation_rad.maximum, 0.2)
        self.assertEqual(ar.final_cube_target_position_error_m, 1.0)
        self.assertIsNone(ar.insertion_time_sec)
        self.assertEqual(ar.time_unavailable_reason, "SYNTHETIC_DATA_NOT_REAL_EXECUTION_TIME")
        self.assertEqual(ar, InsertionMetrics.from_json(ar.to_json()))

    def test_declared_qualified_clock_branch_test_double_only(self):
        # ONLY fabricated branch coverage. No simulator/source attestation claim.
        samples = tuple(declared_post_step_test_double(observation((i, 0, 0), index=i)) for i in range(3))
        context = MetricContext("world", SESSION, "cube", EvaluationMode.FORMAL, 0)
        report = evaluate_insertion(samples, context=context, axis_origin=pose(), target=pose((2, 0, 0)), unit_axis=(1, 0, 0))
        self.assertEqual(report.insertion_time_sec, 2.0)
        self.assertIsNone(report.time_unavailable_reason)
        with self.assertRaises(ValueError):
            evaluate_insertion((observation(),), context=context, axis_origin=pose(), target=pose((2, 0, 0)), unit_axis=(1, 0, 0))

    def test_incomplete_endpoint_window_does_not_claim_duration(self):
        samples = tuple(declared_post_step_test_double(observation((i, 0, 0), index=i)) for i in range(3))
        context = MetricContext("world", SESSION, "cube", EvaluationMode.FORMAL, 0)
        for invalid in ((None, *samples[1:]), (*samples[:2], None), (samples[0],)):
            report = evaluate_insertion(invalid, context=context, axis_origin=pose(), target=pose((2, 0, 0)), unit_axis=(1, 0, 0))
            self.assertIsNone(report.insertion_time_sec)
            self.assertIn(report.time_unavailable_reason, ("INCOMPLETE_INSERTION_WINDOW_ENDPOINTS", "FEWER_THAN_TWO_QUALIFIED_SAMPLES"))
            if invalid[-1] is None:
                self.assertIsNone(report.final_cube_target_position_error_m)

    def test_insertion_unqualified_frame_session_duplicate_and_unavailable(self):
        item = observation()
        origin, target = pose(), pose((2, 0, 0))
        for modified in (replace(item, pose=pose(frame="other")), replace_time(item, clock_id="other"),
                         declared_post_step_test_double(item)):
            with self.assertRaises(ValueError):
                evaluate_insertion((modified,), context=synthetic_context(), axis_origin=origin, target=target, unit_axis=(1, 0, 0))
        report = evaluate_insertion((item, item), context=synthetic_context(), axis_origin=origin, target=target, unit_axis=(1, 0, 0))
        self.assertEqual(report.rejections[0].reason, "DUPLICATE_SAMPLE_CLOCK")
        empty = evaluate_insertion((None,), context=synthetic_context(), axis_origin=origin, target=target, unit_axis=(1, 0, 0))
        self.assertEqual((empty.valid_samples, empty.rejected_samples), (0, 1))
        self.assertIsNone(empty.cube_target_position_error_m)
        self.assertIsNone(empty.final_cube_target_position_error_m)


class MeasurementContractTest(unittest.TestCase):
    def test_wrench_and_signed_distance_serialization(self):
        info = observation().info
        wrench = ContactWrench("cube", "tool", "world", (1, 2, 3), (0.1, 0.2, 0.3), (0.4, 0.5, 0.6), info)
        self.assertEqual(wrench, ContactWrench.from_json(wrench.to_json()))
        self.assertEqual(wrench.to_json(), ContactWrench.from_json(wrench.to_json()).to_json())
        for distance in (0.02, 0.0, -0.001):
            item = CollisionDistance("tool", "wall", "world", distance, (0, 0, 0), (0, 0, 0.02), info)
            self.assertEqual(item, CollisionDistance.from_json(item.to_json()))
            self.assertFalse(hasattr(item, "collision_failure"))

    def test_invalid_measurement_can_report_unavailable_without_zero_fill(self):
        info = replace(observation().info, valid=False, invalid_reason="backend not queried")
        wrench = ContactWrench("cube", "tool", "world", None, None, None, info)
        distance = CollisionDistance("tool", "wall", "world", None, None, None, info)
        self.assertIsNone(ContactWrench.from_json(wrench.to_json()).force_N)
        self.assertIsNone(CollisionDistance.from_json(distance.to_json()).signed_distance_m)
        self.assertEqual(distance.info.invalid_reason, "backend not queried")

    def test_valid_payload_point_units_ids_and_finite_validation(self):
        info = observation().info
        for arguments in (
            ("cube", "tool", "world", None, (0, 0, 0), (0, 0, 0), info),
            ("cube", "cube", "world", (0, 0, 0), (0, 0, 0), (0, 0, 0), info),
            ("cube", "tool", "world", (float("inf"), 0, 0), (0, 0, 0), (0, 0, 0), info),
            ("cube", "tool", "world", (0, 0, 0), (0, 0, 0), None, info),
        ):
            with self.assertRaises(ValueError):
                ContactWrench(*arguments)
        with self.assertRaises(ValueError):
            ContactWrench("cube", "tool", "world", (0, 0, 0), (0, 0, 0), (0, 0, 0), info, force_unit="kN")
        for distance in (None, float("nan"), True):
            with self.assertRaises(ValueError):
                CollisionDistance("tool", "wall", "world", distance, (0, 0, 0), (1, 0, 0), info)
        with self.assertRaises(ValueError):
            CollisionDistance("tool", "tool", "world", 1.0, (0, 0, 0), (1, 0, 0), info)
        with self.assertRaises(ValueError):
            CollisionDistance("tool", "wall", "world", 1.0, (0, 0, 0), (1, 0, 0), info, distance_unit="mm")

    def test_legacy_synthetic_promotion_or_unqualified_clock_rejected(self):
        clock = TimePoint(TimeBasis.SIMULATION, SESSION, 0, 1)
        for source in ("legacy_task26", "synthetic_fixture"):
            with self.assertRaises(ValueError):
                MeasurementInfo(source, MeasurementQualification.SYNCHRONIZED_POST_STEP, clock, True, True, ("fixture",))
        with self.assertRaises(ValueError):
            MeasurementInfo("legacy_saved_snapshot", MeasurementQualification.LEGACY_ASYNCHRONOUS, clock, False, True, ("fixture",))
        with self.assertRaises(ValueError):
            MeasurementInfo("declared_native", MeasurementQualification.SYNCHRONIZED_POST_STEP, None, False, True, ("fixture",))
        with self.assertRaises(ValueError):
            PoseMeasurement("cube", pose(), replace(observation().info, valid=True, evidence_refs=()))


if __name__ == "__main__":
    unittest.main()
