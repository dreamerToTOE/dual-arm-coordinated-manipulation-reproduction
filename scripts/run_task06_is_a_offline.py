"""TASK06-IS-A 单次只读来源/模型审计；无 ROS/Isaac/IK/控制命令。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from common.interfaces.exchange import BenchmarkResult, MeasurementQualification, ResultStatus, RunMetadata
from common.logging.run import RunLogger, source_ref
from platforms.offline_moveit.task06_is_a_scene_adapter.source_audit import audit, sha

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "configs/engineering/task06_is_a_scene_adapter_v1.json"
LEGACY = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation")


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, allow_nan=False, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    # 实验前提交的协议不可改变，包括 null 端点；无事后调参/补造端点。
    committed = subprocess.check_output(["git", "show", "462e6b1:"+PROTOCOL], cwd=ROOT)
    if (ROOT/PROTOCOL).read_bytes() != committed:
        parser.error("Predeclared protocol changed; stop for review")
    protocol = json.loads(committed)
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")[:-1]
    protected = [p for p in tracked if p.startswith(("results/", "baselines/", "common/", "tests/fixtures/",
        "platforms/isaac_ros2/", "configs/benchmark/", "platforms/offline_moveit/task03_",
        "platforms/offline_moveit/task04_", "platforms/offline_moveit/task05_", "platforms/offline_moveit/task06_constrained"))]
    before = {p: sha(ROOT/p) for p in protected}
    sources = sorted(set(protected) | {PROTOCOL, "scripts/run_task06_is_a_offline.py",
        "tests/test_task06_is_a_scene_adapter.py"} | {
        str(p.relative_to(ROOT)) for p in (ROOT/"platforms/offline_moveit/task06_is_a_scene_adapter").glob("*") if p.is_file()})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = RunMetadata(args.run_id, "TASK06-IS-A", "P4_EXISTING_SCENE_OFFLINE_ADAPTER", "OFFLINE_MOVEIT_CORE_FCL",
        commit, 0, None, tuple([sys.executable]+sys.argv), ("D056_scene_adapter_v1",), (PROTOCOL,),
        tuple(source_ref(f"source_{i}", ROOT/p) for i, p in enumerate(sources)))
    build = ROOT/"build/task06_is_a_scene_adapter"
    with RunLogger(ROOT/"results", metadata) as logger:
        exits, source, native = {}, {}, {}
        error = None
        try:
            source = audit(ROOT, LEGACY, protocol)
            write_json(logger.path/"source_audit.json", source)
            commands = [
                ("configure.log", ["cmake", "-S", "platforms/offline_moveit/task06_is_a_scene_adapter", "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"], protocol["configure_timeout_sec"]),
                ("build.log", ["cmake", "--build", str(build), "--parallel", "2"], protocol["build_timeout_sec"]),
                ("task02_regression.log", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_task02*.py", "-v"], protocol["test_timeout_sec"]),
                ("adapter_tests.log", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_task06_is_a_scene_adapter.py", "-v"], protocol["test_timeout_sec"]),
                ("ctest.log", ["ctest", "--test-dir", str(build), "--output-on-failure"], protocol["test_timeout_sec"]),
                ("native_audit.log", [str(build/"task06_is_a_native_audit"), PROTOCOL, str(logger.path/"source_audit.json")], protocol["native_audit_timeout_sec"]),
            ]
            for name, argv, timeout in commands:
                print(f"TASK06-IS-A offline: {name}", flush=True)
                with (logger.path/name).open("x", encoding="utf-8") as handle:
                    process = subprocess.run(argv, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT,
                                             timeout=timeout, check=False)
                exits[name] = {"argv": argv, "timeout_sec": timeout, "exit_code": process.returncode}
                if process.returncode:
                    raise RuntimeError(f"Bounded offline command failed: {name}")
            # 完整 stdout 保留；原 MoveIt 原生加载日志可能先于独立 JSON。
            raw = (logger.path/"native_audit.log").read_text()
            native = json.loads(raw[raw.index("{\n"):])
            write_json(logger.path/"native_audit.json", native)
        except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
            error = str(exc)
            write_json(logger.path/"failure.json", {"error": error, "stage": "SOURCE_MODEL_INPUT_AUDIT"})
        after = {p: sha(ROOT/p) for p in protected}
        unchanged = before == after
        summary = {"task06_is_a_status": "PARTIAL", "status_zh": "部分完成", "error": error,
                   "commands": exits, "software_ok": error is None, "protected_unchanged": unchanged,
                   "protected_hashes_before": before, "protected_hashes_after": after,
                   "protocol_sha256": hashlib.sha256(committed).hexdigest(),
                   "endpoint_gate": source.get("endpoint_gate"), "planning_calls": 0,
                   "conditional_seeds_unused": protocol["conditional_seeds"], "actual_rng_seed": None,
                   "ik_calls": 0, "execution_commands": 0, "physical_runtime_starts": 0,
                   "native_state_collision_queries": 0, "qualified_path_count": 0,
                   "minimum_collision_distance_m": None, "simulation_time": None, "physics_step": None,
                   "minimum_distance_status": protocol["minimum_collision_distance"],
                   "claim_scope": "SOURCE_ALIGNMENT_NATIVE_MODEL_LOAD_INPUT_REJECTION_ONLY"}
        write_json(logger.path/"summary.json", summary)
        evidence = tuple(p.name for p in sorted(logger.path.iterdir()) if p.is_file() and p.name != "metadata.json")
        logger.finish(BenchmarkResult(args.run_id, metadata.baseline_id,
            ResultStatus.INCOMPLETE if error is None and unchanged else ResultStatus.ABORTED,
            summary["claim_scope"], MeasurementQualification.UNQUALIFIED, evidence, metadata.config_ids,
            tuple(s.source_id for s in metadata.sources), failure_stage="ENDPOINT_INPUT_UNAVAILABLE" if error is None else "SOURCE_MODEL_INPUT_AUDIT",
            reason=error or ("Protected source changed" if not unchanged else "Actual shared-held START/PRE_PUSH 14q unconfirmed; no planning dispatched"),
            limitations=("NOT_EXECUTED", "NO_QUALIFIED_PATH", "NOT_A_FORMAL_SINGLE_CUBE_BENCHMARK")))
        print(json.dumps({"status": "部分完成", "software_ok": error is None,
                          "reason": error or "Actual shared-held endpoints unconfirmed", "run": str(logger.path)}, ensure_ascii=False))
    return 0 if error is None and unchanged else 1


if __name__ == "__main__":
    raise SystemExit(main())
