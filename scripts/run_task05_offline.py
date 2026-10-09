"""TASK05 固定预算离线 RBS / 原生 FCL；复用 TASK02 文件日志与 TASK03/04 回归。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from common.interfaces.exchange import BenchmarkResult, MeasurementQualification, ResultStatus, RunMetadata
from common.logging.run import RunLogger, source_ref
from platforms.isaac_ros2.foundation.legacy_task26 import load_manifest, verify_legacy_assets

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "configs/engineering/task05_local_connection_test_v1.json"
PROTOCOL_SHA = "55e53493109f19b6c14fb4f536cf24027f27d2c5dc7b90ecf14c30ac6fb2c765"
ARCHIVE = "results/20261007_TASK01_full_single_cube_geometry01/"
LEGACY_ROOT = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation")
MESH_ROOT = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/franka_description/meshes/robots/fr3/collision")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if digest(ROOT / PROTOCOL) != PROTOCOL_SHA:
        parser.error("Pre-experiment protocol hash changed; stop, do not retune")
    build = ROOT / "build/task05_local_connection"
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")[:-1]
    protected = sorted(p for p in tracked if p.startswith((
        "common/", "tests/fixtures/", "platforms/isaac_ros2/", "results/", "configs/benchmark/",
        "platforms/offline_moveit/task03_closure/", "platforms/offline_moveit/task04_projection/",
        "tests/test_task02")) or p in (
            "baselines/p4_closed_chain/closure.hpp", "baselines/p4_closed_chain/closure.cpp",
            "baselines/p4_closed_chain/projection.hpp", "baselines/p4_closed_chain/projection.cpp",
            "tests/task03_closure_math.cpp", "tests/task04_projection_math.cpp",
            "configs/engineering/task04_projection_test_v1.json", PROTOCOL,
            "scripts/run_task03_offline.py", "scripts/run_task04_offline.py"))
    sources = sorted(set(protected) | {
        "scripts/run_task05_offline.py", "baselines/p4_closed_chain/local_connection.hpp",
        "baselines/p4_closed_chain/local_connection.cpp", "tests/task05_local_connection_math.cpp",
    } | {str(p.relative_to(ROOT)) for p in (ROOT / "platforms/offline_moveit/task05_local_connection").glob("*") if p.is_file()})
    # 元数据sources只列直接算法/模型/协议/适配源码；历史保护集单独完整保存。
    direct = [p for p in sources if not p.startswith("results/") or p in (
        ARCHIVE + "config_at_run.yaml", ARCHIVE + "state_records.json",
        "results/20261009_TASK04_projection03/projection_metrics.json")]
    meshes = [MESH_ROOT / f"link{i}.stl" for i in range(8)]
    before = {p: digest(ROOT / p) for p in protected}
    mesh_before = {str(p): digest(p) for p in meshes}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = RunMetadata(
        args.run_id, "TASK05", "P4_RBS_LOCAL_CONNECTION", "OFFLINE_MOVEIT_FCL_EIGEN",
        commit, 0, None, tuple([sys.executable] + sys.argv), ("D050_task05_v1",),
        (PROTOCOL, ARCHIVE + "config_at_run.yaml"),
        tuple(source_ref(f"source_{i}", ROOT / p) for i, p in enumerate(direct)) +
        tuple(source_ref(f"original_mesh_{i}", p) for i, p in enumerate(meshes)),
    )
    with RunLogger(ROOT / "results", metadata) as logger:
        legacy_before = verify_legacy_assets(LEGACY_ROOT, load_manifest())
        metrics = logger.path / "local_connection_metrics.json"
        old3 = logger.path / "task03_regression_metrics.json"
        old4 = logger.path / "task04_regression_metrics.json"
        commands = [
            ("configure.log", ["cmake", "-S", "platforms/offline_moveit/task05_local_connection", "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"], 60),
            ("build.log", ["cmake", "--build", str(build), "--parallel", "2"], 180),
            ("task02_regression.log", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_task02*.py", "-v"], 60),
            ("ctest.log", ["ctest", "--test-dir", str(build), "--output-on-failure"], 60),
            ("task03_math.log", [str(build / "task04_reuse/task03_reuse/task03_math_test")], 60),
            ("task04_math.log", [str(build / "task04_reuse/task04_projection_math")], 60),
            ("task05_math.log", [str(build / "task05_connection_math")], 60),
            ("task03_real_model.log", [str(build / "task04_reuse/task03_reuse/task03_model_test"), "--urdf", "tests/fixtures/task03/robot.urdf", "--srdf", "tests/fixtures/task03/robot.srdf", "--fixture", ARCHIVE + "state_records.json", "--config", ARCHIVE + "config_at_run.yaml", "--output", str(old3)], 60),
            ("task04_real_model.log", [str(build / "task04_reuse/task04_model_test"), "--protocol", "configs/engineering/task04_projection_test_v1.json", "--output", str(old4)], 60),
            ("task05_real_fcl.log", [str(build / "task05_model_test"), "--protocol", PROTOCOL, "--output", str(metrics)], 60),
        ]
        exits = {}
        for name, argv, timeout in commands:
            print(f"TASK05 offline: {name}", flush=True)
            with (logger.path / name).open("x", encoding="utf-8") as handle:
                try:
                    result = subprocess.run(argv, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout, check=False)
                    record = {"argv": argv, "exit_code": result.returncode, "timeout_sec": timeout, "timed_out": False}
                except (OSError, subprocess.TimeoutExpired) as e:
                    record = {"argv": argv, "exit_code": None, "timeout_sec": timeout, "timed_out": isinstance(e, subprocess.TimeoutExpired), "error": str(e)}
            exits[name] = record
            if record["exit_code"] != 0:
                break  # 不自动重跑，不调协议；保留失败日志和完整结果。
        after = {p: digest(ROOT / p) for p in protected}
        mesh_after = {str(p): digest(p) for p in meshes}
        legacy_after = verify_legacy_assets(LEGACY_ROOT, load_manifest())
        native = json.loads(metrics.read_text()) if metrics.exists() else {}
        software_ok = len(exits) == len(commands) and all(r["exit_code"] == 0 for r in exits.values())
        unchanged = before == after and mesh_before == mesh_after and legacy_before == legacy_after
        accepted = software_ok and unchanged and native.get("task05_status") == "PASS_CANDIDATE"
        summary = {
            "task05_status": "PASS_CANDIDATE" if accepted else "PARTIAL",
            "claim_scope": "OFFLINE_DISCRETE_LOCAL_CONNECTION_REAL_FR3_AND_NATIVE_FCL_ONLY",
            "software_ok": software_ok, "commands": exits, "protected_unchanged": unchanged,
            "protected_hashes_before": before, "protected_hashes_after": after,
            "mesh_hashes_before": mesh_before, "mesh_hashes_after": mesh_after,
            "legacy_assets_before": legacy_before, "legacy_assets_after": legacy_after,
            "native_summary": native.get("summary"), "native_error": native.get("error"),
            "seed": None, "seed_status": "UNSET_NO_RANDOM_SAMPLING",
            "physics_step": None, "simulation_time": None, "physical_commands": 0,
            "task02_d": "PARTIAL_DEFERRED", "task02": "IN_PROGRESS", "benchmark": "DRAFT_NOT_FROZEN",
            "continuous_collision_certificate": False, "task06_started": False,
        }
        with (logger.path / "summary.json").open("x", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, allow_nan=False); handle.write("\n")
        logger.finish(BenchmarkResult(
            args.run_id, "P4_RBS_LOCAL_CONNECTION", ResultStatus.SUCCESS if accepted else ResultStatus.FAILURE,
            "TASK05 offline discrete test acceptance only; not scientific Benchmark or physical success",
            MeasurementQualification.UNQUALIFIED,
            tuple(p.name for p in sorted(logger.path.iterdir()) if p.is_file() and p.name != "metadata.json"),
            metadata.config_ids, tuple(s.source_id for s in metadata.sources),
            failure_stage=None if accepted else "OFFLINE_SOFTWARE_OR_NATIVE_FCL_ACCEPTANCE",
            reason=None if accepted else "See retained bounded logs and exact failures",
            limitations=("Discrete states only; not continuous collision/manifold-branch proof",
                "Historical fixed fixture is not frozen Benchmark", "No physical or suction validation",
                "TASK02-D measurement binding DEFERRED", "TASK06 not implemented"),
        ))
    print(f"TASK05={summary['task05_status']}; evidence={logger.path}", flush=True)
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
