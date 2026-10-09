"""[ENGINEERING] Startup-only launcher; never run the handoff/control section.

原 harness 保持字节不变；仅当前 main 的 Python 行事件设置退出屏障。
不构成零物理步、碰撞或 READY 验证；SDK/native 线程不受 trace 暂停。
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

GUI_SHA256 = "539615dc789460abc2e3b0b2e7c09dff8c7ad00b8dc74327f1e8d114a0a1a77c"


def validated_barrier(source, expected_sha256=GUI_SHA256):
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise RuntimeError("Original GUI hash mismatch; refusing SDK startup")
    tree = ast.parse(data, filename=str(source))
    mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"]
    if len(mains) != 1:
        raise RuntimeError("Expected exactly one original main")
    anchors = []
    plays = []
    for n in ast.walk(mains[0]):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if (isinstance(f, ast.Subscript) and isinstance(f.value, ast.Name)
                and f.value.id == "ns" and isinstance(f.slice, ast.Constant)
                and f.slice.value == "_apply_official_joint_limits"):
            anchors.append(n.lineno)
        if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                and f.value.id == "timeline" and f.attr == "play"):
            plays.append(n.lineno)
    if len(anchors) != 1 or not plays or anchors[0] >= min(plays):
        raise RuntimeError("Unique pre-control barrier cannot be validated")
    return anchors[0]


class StartupGuard:
    def __init__(self, source, barrier_line, evidence_path, exit_now=os._exit):
        self.source = str(source.resolve())
        self.barrier_line = barrier_line
        self.evidence_path = evidence_path
        self.exit_now = exit_now
        self.last_marker = None

    def emit(self, status, line=None):
        record = {"scope": "startup_diagnosis_only", "status": status,
                  "original_gui_sha256": GUI_SHA256, "source": self.source,
                  "barrier_line": self.barrier_line, "observed_line": line,
                  "pid": os.getpid(), "robot_suction_rail_commands_authorized": False,
                  "simulation_timestamp": None,
                  "not_scientific_simulation_evidence": True}
        with self.evidence_path.open("w", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        print("TASK01_STARTUP_GUARD " + json.dumps(record, ensure_ascii=False), flush=True)

    def trace(self, frame, event, arg):
        if frame.f_code.co_filename != self.source or frame.f_code.co_name != "main":
            return None
        if event == "line":
            line = frame.f_lineno
            if line >= self.barrier_line:
                at_barrier = line == self.barrier_line
                self.emit("PRE_CONTROL_BARRIER_STOP" if at_barrier else
                          "UNEXPECTED_CONTROL_FLOW_STOP", line)
                self.exit_now(42 if at_barrier else 43)  # 不执行 original finally/app.close。
                raise RuntimeError("exit callback unexpectedly returned")
            if line in (88, 100, 106, 107, 120, 122, 124) and line != self.last_marker:
                self.last_marker = line
                self.emit("BEFORE_SOURCE_LINE", line)
        return self.trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    args = parser.parse_args()
    if not os.environ.get("DISPLAY"):
        parser.error("Visible DISPLAY required; no headless fallback")
    source = Path(__file__).with_name("task01_insert_ready_gui.py").resolve()
    barrier = validated_barrier(source)
    if not args.run_dir.is_dir() or (args.run_dir / "raw").exists():
        parser.error("Prepared run directory required; raw must not already exist")
    guard = StartupGuard(source, barrier, args.run_dir / "startup_guard.json")
    sys.argv = [str(source), "--output-dir", str(args.run_dir.resolve() / "raw"),
                "--wall-limit-sec", "180", "--reset-repeats", "0"]
    sys.settrace(guard.trace)
    guard.emit("GUARD_INSTALLED")
    runpy.run_path(str(source), run_name="__main__")
    guard.emit("ORIGINAL_RETURNED_BEFORE_BARRIER")
    os._exit(43)


if __name__ == "__main__":
    main()
