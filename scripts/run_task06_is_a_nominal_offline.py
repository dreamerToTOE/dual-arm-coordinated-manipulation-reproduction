"""单次 V2 名义端点/规划科学进程。协议先提交，失败不重跑；无 ROS/Isaac 服务。"""
import argparse
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

from common.interfaces.exchange import BenchmarkResult, MeasurementQualification, ResultStatus, RunMetadata
from common.logging.run import RunLogger, source_ref
from platforms.offline_moveit.task06_is_a_scene_adapter.nominal_inputs import nominal_audit
from platforms.offline_moveit.task06_is_a_scene_adapter.source_audit import sha
from platforms.isaac_ros2.foundation.legacy_task26 import load_manifest, verify_legacy_assets

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "configs/engineering/task06_is_a_scene_adapter_v2.json"
PREDECLARED = "20fe06d"
LEGACY = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation")


def write(path, value):
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, allow_nan=False, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    protocol = json.loads((ROOT/PROTOCOL).read_text())
    locked = [PROTOCOL, protocol["geometry_archive"], protocol["local_protocol"], protocol["planner_protocol"]]
    for path in locked:
        committed = subprocess.check_output(["git", "show", PREDECLARED+":"+path], cwd=ROOT)
        if committed != (ROOT/path).read_bytes():
            parser.error("Predeclared input changed: " + path)
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")[:-1]
    protected = [p for p in tracked if p.startswith(("results/", "baselines/", "common/", "tests/fixtures/",
        "configs/benchmark/", "platforms/isaac_ros2/", "platforms/offline_moveit/task03_",
        "platforms/offline_moveit/task04_", "platforms/offline_moveit/task06_constrained"))]
    before = {p: sha(ROOT/p) for p in protected}
    legacy_before = verify_legacy_assets(LEGACY, load_manifest())
    # 与原 FCL resourcePath 相同的 ament 首个匹配包；不代换 mesh。
    prefixes = [Path(p) for p in os.environ.get("AMENT_PREFIX_PATH", "").split(":") if p]
    mesh_package = next((p/"share/franka_description" for p in prefixes
        if (p/"share/ament_index/resource_index/packages/franka_description").is_file()), None)
    if mesh_package is None:
        parser.error("Original franka_description package unavailable")
    meshes = sorted((mesh_package/"meshes/robots/fr3/collision").glob("*.stl"))
    if len(meshes) != 8:
        parser.error("Expected eight original FR3 collision STL resources")
    mesh_before = {str(p.resolve()): sha(p) for p in meshes}
    sources = sorted(set(protected+locked+[
        "scripts/run_task06_is_a_nominal_offline.py", "tests/test_task06_is_a_nominal_inputs.py",
        "platforms/offline_moveit/task05_local_connection/collision_adapter.cpp",
        "platforms/offline_moveit/task05_local_connection/collision_adapter.hpp"]) |
        {str(p.relative_to(ROOT)) for p in (ROOT/"platforms/offline_moveit/task06_is_a_scene_adapter").glob("*") if p.is_file()})
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = RunMetadata(args.run_id, "TASK06-IS-A", "P4_TASK26_NOMINAL_STAGE2", "OFFLINE_REAL_FR3_MOVEIT_FCL_KDL",
        commit, 0, None, tuple([sys.executable]+sys.argv), ("D058_scene_adapter_v2",), tuple(locked),
        tuple(source_ref(f"source_{i}", ROOT/p) for i, p in enumerate(sources)) +
        tuple(source_ref(f"original_mesh_{i}", p.resolve()) for i, p in enumerate(meshes)))
    build = ROOT/"build/task06_is_a_scene_adapter"
    with RunLogger(ROOT/"results", metadata) as logger:
        commands, native, error = {}, {}, None
        write(logger.path/"protocol_at_run.json", protocol)
        write(logger.path/"build_preflight_note.json", {
            "scientific_process_started_before_this_run": False,
            "preflight_compile_error": "kdl_parser/kdl_parser.hpp unavailable through legacy CMake variables",
            "source_evidence": "/opt/ros/humble/share/kdl_parser/cmake/export_kdl_parserExport.cmake:54-58",
            "evidence_based_fix": "link existing imported target kdl_parser::kdl_parser; no numerical changes",
            "second_compile_error": "ambiguous std::set<string>::insert(nlohmann::json) in old-default regression",
            "second_compile_fix": "explicit get<string>(); formatting warning clarified; no runtime experiment yet"})
        (logger.path/"adapter_baseline.diff").write_text(subprocess.check_output([
            "git", "diff", "7bae83a", "--", "platforms/offline_moveit/task05_local_connection",
            "platforms/offline_moveit/task06_is_a_scene_adapter"], cwd=ROOT, text=True))
        try:
            source = nominal_audit(ROOT, LEGACY, protocol)
            write(logger.path/"source_audit.json", source)
            plan = [
                ("configure.log", ["cmake", "-S", "platforms/offline_moveit/task06_is_a_scene_adapter", "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"], protocol["configure_timeout_sec"]),
                ("build.log", ["cmake", "--build", str(build), "--parallel", "2"], protocol["build_timeout_sec"]),
                ("task02_regression.log", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_task02*.py", "-v"], protocol["test_timeout_sec"]),
                ("adapter_tests.log", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_task06_is_a*.py", "-v"], protocol["test_timeout_sec"]),
                ("ctest.log", ["ctest", "--test-dir", str(build), "--output-on-failure"], protocol["test_timeout_sec"]),
                ("nominal_science.log", [str(build/"task06_is_a_nominal_planning"), PROTOCOL, str(logger.path)], protocol["max_scientific_process_sec"]),
            ]
            for name, argv, timeout in plan:
                print("TASK06-IS-A V2 offline: " + name, flush=True)
                with (logger.path/name).open("x", encoding="utf-8") as f:
                    try:
                        p = subprocess.run(argv, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
                        commands[name] = {"argv": argv, "exit_code": p.returncode, "timeout_sec": timeout, "timed_out": False}
                    except subprocess.TimeoutExpired:
                        commands[name] = {"argv": argv, "exit_code": None, "timeout_sec": timeout, "timed_out": True}
                        raise RuntimeError("Hard budget reached: " + name)
                if p.returncode:
                    if name == "nominal_science.log" and p.returncode == 1:
                        break  # 预声明端点/搜索失败是科学证据，不作为软件重跑理由。
                    raise RuntimeError("Bounded command failed: " + name)
        except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
            error = str(exc)
            write(logger.path/"failure.json", {"reason": error, "action": "STOP_NO_RETRY"})
        if (logger.path/"planning_summary.json").exists():
            native = json.loads((logger.path/"planning_summary.json").read_text())
        compressed = {}
        for path in sorted(logger.path.glob("planner_seed*.json")):
            raw = path.read_bytes()
            with path.with_suffix(".json.gz").open("xb") as f:
                with gzip.GzipFile(filename="", fileobj=f, mode="wb", mtime=0) as z:
                    z.write(raw)
            compressed[path.name] = {"path": path.name+".gz", "raw_sha256": sha(path), "raw_bytes": len(raw)}
            path.unlink()  # 仅本轮自身完整证据文件，已无损保存在邻近 .gz。
        after = {p: sha(ROOT/p) for p in protected}
        legacy_after = verify_legacy_assets(LEGACY, load_manifest())
        mesh_after = {str(p.resolve()): sha(p) for p in meshes}
        unchanged = before == after and legacy_before == legacy_after and mesh_before == mesh_after
        accepted = error is None and unchanged and native.get("qualified_path_count") == 1
        summary = {"status_zh": "无执行规划适配初步验收通过" if accepted else "部分完成",
            "task06_is_a_status": native.get("task06_is_a_status", "PARTIAL"),
            "native": native, "commands": commands, "error": error, "protected_unchanged": unchanged,
            "protected_hashes_before": before, "protected_hashes_after": after,
            "legacy_assets_before": legacy_before, "legacy_assets_after": legacy_after,
            "mesh_hashes_before": mesh_before, "mesh_hashes_after": mesh_after,
            "compressed_evidence": compressed, "protocol_commit": PREDECLARED,
            "actual_rng_seeds": {"start": protocol["ik"]["start_rng_seed"], "goal": protocol["ik"]["goal_rng_seed"],
                                 "planning": [t["seed"] for t in native.get("trials", [])]},
            "physical_execution_commands": 0, "physical_runtime_starts": 0,
            "simulation_time": None, "physics_step": None, "benchmark": "DRAFT_NOT_FROZEN"}
        write(logger.path/"summary.json", summary)
        logger.finish(BenchmarkResult(args.run_id, metadata.baseline_id,
            ResultStatus.SUCCESS if accepted else (ResultStatus.ABORTED if error else ResultStatus.INCOMPLETE),
            "NOMINAL_OFFLINE_SCENE_ADAPTATION_ONLY", MeasurementQualification.UNQUALIFIED,
            tuple(p.name for p in sorted(logger.path.iterdir()) if p.is_file() and p.name != "metadata.json"),
            metadata.config_ids, tuple(s.source_id for s in metadata.sources),
            failure_stage=None if accepted else native.get("failure_stage", "SOURCE_OR_SOFTWARE_GATE"),
            reason=None if accepted else error or native.get("reason", "See retained failure evidence"),
            limitations=("No Isaac execution/shared-grasp stability proof", "Nominal constructed endpoints, not measured states",
                         "Discrete FCL only; native distance unavailable", "TASK02-D deferred; Benchmark not frozen")))
        print(json.dumps({"status": summary["status_zh"], "run": str(logger.path)}, ensure_ascii=False), flush=True)
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
