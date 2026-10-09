"""TASK02-B offline-only contracts/logging; no Isaac/ROS/MoveIt imports."""

from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from common.interfaces import (
    BaselineCommand, BenchmarkResult, CommandType, EventKind, EventLedger, EventStatus,
    JointTarget, MeasurementQualification, Pose, ResultStatus, RunMetadata, SourceRef,
    TaskEvent, TaskPoseTarget, TaskStageMarker, TimeBasis, TimePoint,
)
from common.logging import RunLogger
from platforms.isaac_ros2.foundation.legacy_events import planned_event_from_legacy, planned_stage_from_legacy


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "results/20261009_TASK02_foundation_interface01/converted_snapshot.json"
SRC = SourceRef("fixture", "synthetic://offline-fixture", hashlib.sha256(b"fixture").hexdigest())
REL = TimePoint(TimeBasis.TRAJECTORY_RELATIVE, "trajectory_1", 1_000_000_000)
SIM = TimePoint(TimeBasis.SIMULATION, "synthetic_sim_session", 50_000_000_000, 10)


def command():
    return BaselineCommand("cmd1", "offline", ("right",), "cube", CommandType.SUCTION_ON,
                           "not_applicable", "not_applicable", REL,
                           replace(REL, nanoseconds=2_000_000_000), ("config",), ("fixture",))


def event(event_id="planned", status=EventStatus.PLANNED, **changes):
    data = dict(event_id=event_id, kind=EventKind.ATTACH, status=status,
                time=REL if status is EventStatus.PLANNED else SIM,
                stage_id="CONTACT", robot_ids=("right",), object_id="cube", source_id="fixture",
                link_id="tcp", command_id="cmd1")
    if status is not EventStatus.PLANNED:
        data.update(evidence_refs=("synthetic-observation.json",), attachment_id="synthetic_attachment")
    data.update(changes)
    return TaskEvent(**data)


def metadata(seed=None):
    return RunMetadata("trial_0", "TASK02-B", "offline", "synthetic_offline", "06d5434",
                       0, seed, ("python3 -m unittest",), ("config",),
                       ("tests/test_task02_exchange_logging.py",), (SRC,))


def result(status=ResultStatus.SUCCESS, qualification=MeasurementQualification.SYNTHETIC, **changes):
    data = dict(run_id="trial_0", baseline_id="offline", status=status,
                claim_scope="offline contract only, not robot acceptance",
                measurement_qualification=qualification, evidence_refs=("synthetic-observation.json",),
                config_ids=("config",), source_ids=("fixture",))
    if status is not ResultStatus.SUCCESS:
        data.update(failure_stage="SYNTHETIC_GATE", reason="synthetic rejection")
    data.update(changes)
    return BenchmarkResult(**data)


class ExchangeContractTest(unittest.TestCase):
    def test_all_command_types_and_stable_round_trip(self):
        joint = replace(command(), command_type=CommandType.JOINT_TARGET,
                        frame_id="joint_space", units="rad",
                        joint_targets=(JointTarget("right", ("joint1", "joint2"), (0, 0.5)),))
        pose = replace(command(), command_type=CommandType.TASK_POSE, frame_id="world",
                       units="m+quaternion_xyzw", pose_targets=(TaskPoseTarget(
                           "right", "tcp", Pose("world", (1, 0, 0), (0, 0, 0, 1), "specified_target")),))
        hold = replace(command(), command_type=CommandType.HOLD, object_id=None)
        for item in (joint, pose, hold, command(), replace(command(), command_type=CommandType.SUCTION_OFF)):
            restored = BaselineCommand.from_json(item.to_json())
            self.assertEqual(item, restored)
            self.assertEqual(item.to_json(), restored.to_json())

    def test_commands_have_no_execution_side_effects(self):
        with patch("socket.socket", side_effect=AssertionError("network")), \
                patch("subprocess.Popen", side_effect=AssertionError("process")), \
                patch("os.system", side_effect=AssertionError("shell")):
            BaselineCommand.from_json(command().to_json())
        for name in ("execute", "publish", "send", "step"):
            self.assertFalse(hasattr(command(), name))
        for path in (ROOT / "common/interfaces/exchange.py", ROOT / "common/logging/run.py"):
            code = path.read_text()
            for forbidden in ("import rclpy", "import rospy", "import omni", "import moveit"):
                self.assertNotIn(forbidden, code)

    def test_wrong_units_and_target_union_rejected(self):
        for changes in (dict(units="mm"), dict(frame_id="world"),
                        dict(joint_targets=(JointTarget("right", ("j",), (0,)),)),
                        dict(command_type=CommandType.JOINT_TARGET, frame_id="joint_space", units="rad")):
            with self.assertRaises(ValueError):
                replace(command(), **changes)
        with self.assertRaises(ValueError):
            JointTarget("right", ("j",), (float("nan"),))
        with self.assertRaises(ValueError):
            JointTarget("right", ("j",), (True,))

    def test_command_deadline_cannot_mix_clocks_or_reverse(self):
        for deadline in (SIM, replace(REL, clock_id="other"), replace(REL, nanoseconds=0)):
            with self.assertRaises(ValueError):
                replace(command(), deadline=deadline)
        with self.assertRaises(ValueError):
            TimePoint(TimeBasis.SIMULATION, "sim", True, 1)
        with self.assertRaises(ValueError):
            TimePoint(TimeBasis.TRAJECTORY_RELATIVE, "plan", 0, 1)

    def test_unknown_wire_enum_schema_and_fields_rejected(self):
        value = json.loads(command().to_json())
        value["data"]["command_type"] = "EXECUTE_ROBOT"
        with self.assertRaises(ValueError):
            BaselineCommand.from_dict(value)
        value = json.loads(command().to_json())
        value["data"]["new_threshold"] = 1
        with self.assertRaises(ValueError):
            BaselineCommand.from_dict(value)
        with self.assertRaises(ValueError):
            BenchmarkResult.from_json(command().to_json())

    def test_legacy_events_and_stage_remain_planned_relative(self):
        item = planned_event_from_legacy({"time_sec": 1.25, "type": "SUCTION_ON", "object_name": "cube",
                                          "link_name": "tcp"}, event_id="legacy", trajectory_id="trajectory_1",
                                         robot_id="right", stage_id="CONTACT", source_id="fixture")
        self.assertEqual(item.status, EventStatus.PLANNED)
        self.assertEqual(item.time.nanoseconds, 1_250_000_000)
        self.assertIsNone(item.time.physics_step)
        self.assertEqual(TaskEvent.from_json(item.to_json()), item)
        stage = planned_stage_from_legacy({"name": "CONTACT", "start_time_sec": 1, "end_time_sec": 2},
                                          trajectory_id="trajectory_1")
        self.assertEqual(TaskStageMarker.from_json(stage.to_json()), stage)
        with self.assertRaises(ValueError):
            TaskStageMarker("bad", REL, SIM)
        with self.assertRaises(ValueError):
            TaskStageMarker("bad", REL, replace(REL, nanoseconds=0))

    def test_planned_observed_confirmed_are_distinct_and_clock_domains_not_compared(self):
        ledger = EventLedger()
        ledger.append(event())
        observation = event("obs", EventStatus.OBSERVED, planned_event_id="planned")
        ledger.append(observation)
        # 计划2秒可在仿真50秒记录之后出现；不同域不做大小比较。
        ledger.append(event("plan2", time=replace(REL, nanoseconds=2_000_000_000)))
        confirmation = event("confirm", EventStatus.CONFIRMED, observed_event_id="obs",
                             planned_event_id="planned", time=replace(SIM, nanoseconds=51_000_000_000, physics_step=11))
        ledger.append(confirmation)
        self.assertEqual(TaskEvent.from_json(confirmation.to_json()), confirmation)
        with self.assertRaises(ValueError):
            ledger.append(replace(confirmation, event_id="twice"))

    def test_suction_on_never_implicitly_attaches(self):
        ledger = EventLedger()
        ledger.append(event(kind=EventKind.SUCTION_ON))
        self.assertEqual(len(ledger._events), 1)
        with self.assertRaises(ValueError):
            ledger.append(event("obs", EventStatus.OBSERVED, planned_event_id="planned"))
        with self.assertRaises(ValueError):
            event("obs", EventStatus.OBSERVED, attachment_id=None)  # SG CLOSED 不能替代 attachment ID。

    def test_confirmation_requires_observation_evidence_and_same_attachment(self):
        with self.assertRaises(ValueError):
            event("confirm", EventStatus.CONFIRMED)
        with self.assertRaises(ValueError):
            event("obs", EventStatus.OBSERVED, evidence_refs=())
        with self.assertRaises(ValueError):
            event("obs", EventStatus.OBSERVED, time=REL)
        ledger = EventLedger()
        ledger.append(event("obs", EventStatus.OBSERVED))
        for changes in (dict(attachment_id="other"), dict(object_id="other"),
                        dict(command_id="other_command"),
                        dict(time=replace(SIM, clock_id="other_session"))):
            with self.assertRaises(ValueError):
                ledger.append(event("confirm", EventStatus.CONFIRMED, observed_event_id="obs", **changes))
        planned = EventLedger()
        planned.append(event())
        with self.assertRaises(ValueError):
            planned.append(event("obs", EventStatus.OBSERVED, planned_event_id="planned", command_id="other_command"))

    def test_event_backward_time_step_duplicate_and_failed_reason(self):
        ledger = EventLedger()
        ledger.append(event("obs", EventStatus.OBSERVED))
        for item in (event("obs", EventStatus.OBSERVED),
                     event("earlier", EventStatus.OBSERVED, time=replace(SIM, nanoseconds=0)),
                     event("step_back", EventStatus.OBSERVED, time=replace(SIM, physics_step=9))):
            with self.assertRaises(ValueError):
                ledger.append(item)
        with self.assertRaises(ValueError):
            event("failed", EventStatus.FAILED)
        failed = event("failed", EventStatus.FAILED, reason="synthetic fail", observed_event_id="obs")
        ledger.append(failed)
        self.assertEqual(TaskEvent.from_json(failed.to_json()), failed)

    def test_four_result_statuses_and_metadata_round_trip(self):
        for status in ResultStatus:
            item = result(status)
            self.assertEqual(BenchmarkResult.from_json(item.to_json()), item)
        for seed in (None, 0, 42):
            item = metadata(seed)
            self.assertEqual(RunMetadata.from_json(item.to_json()), item)
            self.assertEqual(item.seed_status, "UNSET" if seed is None else "SET")
        repeated_argv = replace(metadata(), command=("python3", "demo.py", "-p", "a:=1", "-p", "b:=2"))
        self.assertEqual(RunMetadata.from_json(repeated_argv.to_json()), repeated_argv)
        with self.assertRaises(ValueError):
            result(ResultStatus.FAILURE, reason=None)
        with self.assertRaises(ValueError):
            result(failure_stage="hidden_failure")
        with self.assertRaises(ValueError):
            metadata(True)


class FileLoggerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="task02b-logs-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_success_logs_metadata_commands_events_states_artifacts_and_seed(self):
        with RunLogger(self.root, metadata()) as writer:
            writer.append_command(command())
            writer.append_event(event())
            writer.append_event(event("obs", EventStatus.OBSERVED, planned_event_id="planned"))
            writer.append_event(event("confirmed", EventStatus.CONFIRMED, observed_event_id="obs"))
            history = json.loads(HISTORY.read_text())
            writer.append_state(history, MeasurementQualification.LEGACY_ASYNCHRONOUS)
            writer.finish(result(qualification=MeasurementQualification.LEGACY_ASYNCHRONOUS))
        meta = json.loads((writer.path / "metadata.json").read_text())
        self.assertEqual(meta["seed_status"], "UNSET")
        self.assertEqual(RunMetadata.from_dict(meta["run_metadata"]), metadata())
        self.assertIsNone(meta["run_metadata"]["data"]["seed"])
        self.assertEqual(meta["command"], ["python3 -m unittest"])
        self.assertEqual(meta["config_path"], ["tests/test_task02_exchange_logging.py"])
        self.assertEqual(meta["status"], "SUCCESS")
        events = [json.loads(line) for line in (writer.path / "events.jsonl").read_text().splitlines()]
        self.assertEqual([item["sequence"] for item in events], [0, 1, 2])
        restored = [TaskEvent.from_dict(item["event"]) for item in events]
        self.assertEqual(restored[-1].status, EventStatus.CONFIRMED)
        state_line = json.loads((writer.path / "states.jsonl").read_text())
        self.assertEqual(state_line["record"], history)
        for artifact in meta["artifacts"]:
            self.assertEqual(artifact["sha256"], hashlib.sha256((writer.path / artifact["path"]).read_bytes()).hexdigest())
        self.assertIn("result.json", meta["artifact_paths"])
        self.assertFalse(list(writer.path.glob("*.tmp")))

    def test_failure_result_and_existing_events_are_preserved(self):
        with RunLogger(self.root, metadata(42)) as writer:
            writer.append_command(command())
            writer.append_event(event())
            writer.append_event(event("failed", EventStatus.FAILED, reason="synthetic gate failure"))
            writer.finish(result(ResultStatus.FAILURE))
        saved = BenchmarkResult.from_json((writer.path / "result.json").read_text())
        self.assertEqual(saved.status, ResultStatus.FAILURE)
        self.assertEqual(len((writer.path / "events.jsonl").read_text().splitlines()), 2)
        meta = json.loads((writer.path / "metadata.json").read_text())
        self.assertEqual(meta["seed_status"], "SET")
        self.assertEqual(meta["run_metadata"]["data"]["seed"], 42)

    def test_exception_leaves_aborted_result_and_propagates(self):
        with self.assertRaisesRegex(RuntimeError, "offline failure"):
            with RunLogger(self.root, metadata()) as writer:
                writer.append_event(event(command_id=None))
                raise RuntimeError("offline failure")
        saved = BenchmarkResult.from_json((writer.path / "result.json").read_text())
        self.assertEqual(saved.status, ResultStatus.ABORTED)
        self.assertIn("offline failure", saved.reason)
        self.assertTrue((writer.path / "events.jsonl").exists())
        self.assertTrue((writer.path / "termination.json").exists())
        with self.assertRaises(RuntimeError):
            with RunLogger(self.root / "empty_exception", metadata()) as empty_writer:
                raise RuntimeError()
        saved_empty = BenchmarkResult.from_json((empty_writer.path / "result.json").read_text())
        self.assertEqual(saved_empty.status, ResultStatus.ABORTED)
        self.assertEqual(saved_empty.reason, "RuntimeError()")

    def test_unfinished_context_is_incomplete_not_success(self):
        with RunLogger(self.root, metadata()) as writer:
            pass
        saved = BenchmarkResult.from_json((writer.path / "result.json").read_text())
        self.assertEqual(saved.status, ResultStatus.INCOMPLETE)

    def test_source_command_and_run_identity_checks(self):
        with RunLogger(self.root, metadata()) as writer:
            with self.assertRaises(ValueError):
                writer.append_command(replace(command(), source_ids=("unknown",)))
            with self.assertRaises(ValueError):
                writer.append_event(event())  # 引用的命令尚未记录。
            writer.append_command(command())
            with self.assertRaises(ValueError):
                writer.append_command(command())
            with self.assertRaises(ValueError):
                writer.finish(result(run_id="other"))

    def test_no_legacy_state_or_run_qualification_upgrade(self):
        history = json.loads(HISTORY.read_text())
        with RunLogger(self.root / "no_states", metadata()) as writer:
            with self.assertRaises(ValueError):
                writer.finish(result(qualification=MeasurementQualification.SYNCHRONIZED_POST_STEP))
        with RunLogger(self.root, metadata()) as writer:
            with self.assertRaises(ValueError):
                writer.append_state(history, MeasurementQualification.SYNCHRONIZED_POST_STEP)
            forged = deepcopy(history)
            forged["state"]["clock"].update(post_physics_step=True, simulation_stamp_ns=100, physics_step=1)
            with self.assertRaises(ValueError):
                writer.append_state(forged, MeasurementQualification.SYNCHRONIZED_POST_STEP)
            del forged["evidence_class"]
            with self.assertRaises(ValueError):
                writer.append_state(forged, MeasurementQualification.SYNCHRONIZED_POST_STEP)
            writer.append_state(history, MeasurementQualification.LEGACY_ASYNCHRONOUS)
            with self.assertRaises(ValueError):
                writer.finish(result(qualification=MeasurementQualification.SYNCHRONIZED_POST_STEP))

    def test_path_escape_existing_run_and_finished_writes_rejected(self):
        for run_id in ("../outside", "/outside", "..", "x/y"):
            with self.assertRaises(ValueError):
                RunLogger(self.root, replace(metadata(), run_id=run_id))
        with RunLogger(self.root, metadata()) as writer:
            writer.finish(result())
        with self.assertRaises(FileExistsError):
            RunLogger(self.root, metadata())
        for action in (lambda: writer.append_command(command()), lambda: writer.append_event(event()),
                       lambda: writer.finish(result())):
            with self.assertRaises(ValueError):
                action()

    def test_same_input_produces_identical_file_formats(self):
        outputs = []
        for folder in ("a", "b"):
            with RunLogger(self.root / folder, metadata()) as writer:
                writer.append_command(command())
                writer.append_event(event())
                writer.finish(result(ResultStatus.FAILURE))
            outputs.append({p.name: p.read_bytes() for p in writer.path.iterdir()})
        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()
