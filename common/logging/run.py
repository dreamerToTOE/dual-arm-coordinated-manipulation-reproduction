"""轻量实验日志：独占 run、逐条 JSONL、原子 JSON、失败也留证据。

借鉴 Task16@631b1f 的 seed/trial/失败记录输出模式；不调用 OMPL RNG、
ROS logger、数据库或旧执行器。单进程/单写者，不设计控制中间件。
"""

from dataclasses import asdict
import hashlib
import os
from pathlib import Path
import re
import traceback

from common.interfaces.exchange import (
    BaselineCommand, BenchmarkResult, CommandType, EventKind, EventLedger,
    MeasurementQualification, ResultStatus, RunMetadata, SourceRef,
)
from common.interfaces.state import StateRecord
from common.interfaces.wire import canonical_json, decode


def source_ref(source_id, path):
    path = Path(path)
    return SourceRef(source_id, str(path), hashlib.sha256(path.read_bytes()).hexdigest())


class RunLogger:
    def __init__(self, root, metadata):
        if not isinstance(metadata, RunMetadata):
            raise ValueError("typed run metadata required")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", metadata.run_id) or ".." in metadata.run_id:
            raise ValueError("run_id must be one safe path component")
        root = Path(root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / metadata.run_id
        self.path.mkdir(exist_ok=False)  # 已存在 run 不覆盖、不追加到旧实验。
        self.metadata = metadata
        self.ledger = EventLedger()
        self._commands = {}
        self._state_qualifications = set()
        self._state_count = 0
        self._result = None
        self._finished = False
        self._write_metadata()

    def _open(self):
        if self._finished:
            raise ValueError("run already finalized")

    def _atomic_json(self, name, value):
        # 文件名均来自本类常量，不接受调用方的可逃逸输出路径。
        temp = self.path / (name + ".tmp")
        with temp.open("x", encoding="utf-8") as handle:
            handle.write(canonical_json(value) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, self.path / name)

    def _append(self, name, value):
        line = canonical_json(value) + "\n"  # 序列化失败前不打开/修改文件。
        with (self.path / name).open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def _write_metadata(self):
        output = {"schema_version": "task02.run_log.v0.1", "run_metadata": self.metadata.to_dict()}
        output["seed_status"] = self.metadata.seed_status
        output["command"] = list(self.metadata.command)
        output["config_path"] = list(self.metadata.config_paths)
        output["status"] = "IN_PROGRESS" if self._result is None else self._result.status.value
        output["metrics"] = {"commands_logged": len(self._commands), "events_logged": len(self.ledger._events),
                             "states_logged": self._state_count}
        output["source_hash_scope"] = "caller-provided file provenance; not native measurement attestation"
        output["artifacts"] = [
            {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(self.path.iterdir()) if path.is_file() and path.name != "metadata.json"
        ]
        output["artifact_paths"] = [a["path"] for a in output["artifacts"]]
        self._atomic_json("metadata.json", output)

    def _bindings(self, config_ids, source_ids):
        if not set(config_ids) <= set(self.metadata.config_ids):
            raise ValueError("unknown configuration reference")
        if not set(source_ids) <= {s.source_id for s in self.metadata.sources}:
            raise ValueError("unknown source reference")

    def append_command(self, command):
        self._open()
        if not isinstance(command, BaselineCommand) or command.baseline_id != self.metadata.baseline_id:
            raise ValueError("command baseline mismatch")
        self._bindings(command.config_ids, command.source_ids)
        if command.command_id in self._commands:
            raise ValueError("duplicate command ID")
        self._append("commands.jsonl", command.to_dict())
        self._commands[command.command_id] = command

    def append_event(self, event):
        self._open()
        self._bindings((), (event.source_id,))
        if event.command_id:
            command = self._commands.get(event.command_id)
            expected = {
                EventKind.SUCTION_ON: CommandType.SUCTION_ON, EventKind.ATTACH: CommandType.SUCTION_ON,
                EventKind.SUCTION_OFF: CommandType.SUCTION_OFF, EventKind.DETACH: CommandType.SUCTION_OFF,
            }[event.kind]
            if (command is None or command.command_type is not expected or
                    command.robot_ids != event.robot_ids or command.object_id != event.object_id):
                raise ValueError("event command identity/type mismatch")
        self.ledger.validate(event)
        self._append("events.jsonl", {"sequence": len(self.ledger._events), "event": event.to_dict()})
        self.ledger.append(event)

    def append_state(self, record, qualification):
        self._open()
        if not isinstance(qualification, MeasurementQualification):
            raise ValueError("explicit state measurement qualification required")
        if record.get("schema_version") != "task02.state.v0.1":
            raise ValueError("unknown state schema")
        state = decode(record["state"], StateRecord)
        if qualification is MeasurementQualification.SYNCHRONIZED_POST_STEP:
            state.clock.require_scientific_timestamp()
            if record.get("evidence_class") == "LEGACY_ASYNCHRONOUS_ENGINEERING_SNAPSHOT":
                raise ValueError("legacy snapshot cannot be promoted to scientific state")
            poses = [state.arms.left.base_pose, state.arms.right.base_pose,
                     state.arms.left.tcp_pose, state.arms.right.tcp_pose] + [o.pose for o in state.objects]
            if any("legacy" in pose.measurement_source.lower() or "synthetic" in pose.measurement_source.lower()
                   for pose in poses):
                raise ValueError("legacy/synthetic measurement source is not native synchronized evidence")
        self._append("states.jsonl", {"measurement_qualification": qualification, "record": record})
        self._state_qualifications.add(qualification)
        self._state_count += 1

    def finish(self, result):
        self._open()
        if not isinstance(result, BenchmarkResult) or (result.run_id, result.baseline_id) != (
                self.metadata.run_id, self.metadata.baseline_id):
            raise ValueError("result identity mismatch")
        self._bindings(result.config_ids, result.source_ids)
        if result.measurement_qualification is MeasurementQualification.SYNCHRONIZED_POST_STEP and (
                not self._state_qualifications or any(q is not MeasurementQualification.SYNCHRONIZED_POST_STEP
                                                     for q in self._state_qualifications)):
            raise ValueError("scientific qualification requires nonempty qualified state records")
        self._atomic_json("result.json", result.to_dict())
        self._result = result
        self._finished = True
        self._write_metadata()

    def __enter__(self):
        return self

    def __exit__(self, kind, error, trace):
        if not self._finished:
            evidence = {
                "reason": "no explicit terminal result" if error is None else (str(error) if str(error).strip() else repr(error)),
                "traceback": [] if error is None else traceback.format_exception(kind, error, trace),
            }
            self._atomic_json("termination.json", evidence)
            self.finish(BenchmarkResult(
                self.metadata.run_id, self.metadata.baseline_id,
                ResultStatus.INCOMPLETE if error is None else ResultStatus.ABORTED,
                "logger termination, not robot/scientific acceptance", MeasurementQualification.UNQUALIFIED,
                ("termination.json",), self.metadata.config_ids,
                tuple(s.source_id for s in self.metadata.sources),
                failure_stage="LOGGER_CONTEXT", reason=evidence["reason"],
            ))
        return False  # 原异常不吞掉。
