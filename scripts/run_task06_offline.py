"""TASK06固定协议离线搜索；复用TASK02 logger，失败保留完整证据，不自动调参。"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from common.interfaces.exchange import BenchmarkResult, MeasurementQualification, ResultStatus, RunMetadata
from common.logging.run import RunLogger, source_ref
from platforms.isaac_ros2.foundation.legacy_task26 import load_manifest, verify_legacy_assets

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "configs/engineering/task06_constrained_rrtconnect_test_v1.json"
PROTOCOL_SHA = "74a1aa3864da4e3527b6889bfa04b41c7226010a58b8d384e71bf9ce3e6ab32c"
LOCAL_PROTOCOL = "configs/engineering/task05_local_connection_test_v1.json"
LOCAL_SHA = "55e53493109f19b6c14fb4f536cf24027f27d2c5dc7b90ecf14c30ac6fb2c765"
ARCHIVE = "results/20261007_TASK01_full_single_cube_geometry01/"
LEGACY = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation")
MESH = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/franka_description/meshes/robots/fr3/collision")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / PROTOCOL).read_text())
    for path, expected in ((PROTOCOL, PROTOCOL_SHA), (LOCAL_PROTOCOL, LOCAL_SHA),
                           (config["fixture"], config["fixture_sha256"])):
        if sha(ROOT / path) != expected:
            parser.error(f"Predeclared immutable input changed: {path}; stop, no retuning")
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")[:-1]
    protected = sorted(p for p in tracked if p.startswith(("common/", "tests/fixtures/", "results/",
        "platforms/isaac_ros2/", "configs/benchmark/", "tests/test_task02")) or p in (
        "baselines/p4_closed_chain/closure.cpp", "baselines/p4_closed_chain/closure.hpp",
        "baselines/p4_closed_chain/projection.cpp", "baselines/p4_closed_chain/projection.hpp",
        "baselines/p4_closed_chain/local_connection.cpp", "baselines/p4_closed_chain/local_connection.hpp",
        "tests/task03_closure_math.cpp", "tests/task04_projection_math.cpp", "tests/task05_local_connection_math.cpp",
        "configs/engineering/task04_projection_test_v1.json", PROTOCOL, LOCAL_PROTOCOL,
        "scripts/run_task03_offline.py", "scripts/run_task04_offline.py", "scripts/run_task05_offline.py"))
    # 仅新增两个只读/私有fixture入口。保存基线diff，不允许修改已有算法/旧数据。
    adapters = ["platforms/offline_moveit/task03_closure/model_adapter.hpp",
                "platforms/offline_moveit/task03_closure/model_adapter.cpp",
                "platforms/offline_moveit/task05_local_connection/collision_adapter.hpp",
                "platforms/offline_moveit/task05_local_connection/collision_adapter.cpp"]
    source_paths = sorted({PROTOCOL, LOCAL_PROTOCOL, config["fixture"],
        ARCHIVE + "config_at_run.yaml", "tests/fixtures/task03/robot.urdf", "tests/fixtures/task03/robot.srdf",
        "baselines/p4_closed_chain/closure.cpp", "baselines/p4_closed_chain/closure.hpp",
        "baselines/p4_closed_chain/projection.cpp", "baselines/p4_closed_chain/projection.hpp",
        "baselines/p4_closed_chain/local_connection.cpp", "baselines/p4_closed_chain/local_connection.hpp",
        "baselines/p4_closed_chain/constrained_rrtconnect.cpp", "baselines/p4_closed_chain/constrained_rrtconnect.hpp",
        "platforms/offline_moveit/task05_local_connection/evidence.hpp",
        "common/logging/run.py", "common/interfaces/exchange.py", "common/interfaces/wire.py",
        "scripts/run_task06_offline.py", "tests/task06_constrained_rrtconnect_math.cpp"} | set(adapters) |
        {str(p.relative_to(ROOT)) for p in (ROOT / "platforms/offline_moveit/task06_constrained_rrtconnect").glob("*") if p.is_file()})
    before = {p: sha(ROOT / p) for p in protected}
    meshes = [MESH / f"link{i}.stl" for i in range(8)]
    mesh_before = {str(p): sha(p) for p in meshes}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = RunMetadata(args.run_id, "TASK06", "P4_NR_CONSTRAINED_RRTCONNECT", "OFFLINE_REAL_FR3_MOVEIT_FCL",
        commit, 0, None, tuple([sys.executable] + sys.argv), ("D052_task06_v1",), (PROTOCOL, LOCAL_PROTOCOL),
        tuple(source_ref(f"source_{i}", ROOT / p) for i, p in enumerate(source_paths)) +
        tuple(source_ref(f"original_mesh_{i}", p) for i, p in enumerate(meshes)))
    build = ROOT / "build/task06_constrained_rrtconnect"
    with RunLogger(ROOT / "results", metadata) as logger:
        legacy_before = verify_legacy_assets(LEGACY, load_manifest())
        with (logger.path / "adapter_baseline.diff").open("x") as handle:
            handle.write(subprocess.check_output(["git", "diff", "91a1adc", "--"] + adapters, cwd=ROOT, text=True))
        commands = [
            ("configure.log", ["cmake", "-S", "platforms/offline_moveit/task06_constrained_rrtconnect", "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"], 60),
            ("build.log", ["cmake", "--build", str(build), "--parallel", "2"], 240),
            ("task02_regression.log", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_task02*.py", "-v"], 60),
            ("ctest.log", ["ctest", "--test-dir", str(build), "--output-on-failure"], 60),
            ("task03_real_model.log", [str(build / "task05_reuse/task04_reuse/task03_reuse/task03_model_test"),
                "--urdf", "tests/fixtures/task03/robot.urdf", "--srdf", "tests/fixtures/task03/robot.srdf",
                "--fixture", ARCHIVE + "state_records.json", "--config", ARCHIVE + "config_at_run.yaml",
                "--output", str(logger.path / "task03_regression_metrics.json")], 60),
            ("task04_real_model.log", [str(build / "task05_reuse/task04_reuse/task04_model_test"),
                "--protocol", "configs/engineering/task04_projection_test_v1.json", "--output", str(logger.path / "task04_regression_metrics.json")], 60),
            ("task05_real_fcl.log", [str(build / "task05_reuse/task05_model_test"), "--protocol", LOCAL_PROTOCOL,
                "--output", str(logger.path / "task05_regression_metrics.json")], 60),
            ("task06_real_search.log", [str(build / "task06_model_test"), "--protocol", PROTOCOL, "--output-dir", str(logger.path)], 480),
        ]
        exits = {}
        for name, argv, timeout in commands:
            print(f"TASK06 offline: {name}", flush=True)
            with (logger.path / name).open("x", encoding="utf-8") as handle:
                try:
                    r = subprocess.run(argv, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout, check=False)
                    record = {"argv": argv, "exit_code": r.returncode, "timed_out": False, "timeout_sec": timeout}
                except (OSError, subprocess.TimeoutExpired) as e:
                    record = {"argv": argv, "exit_code": None, "timed_out": isinstance(e, subprocess.TimeoutExpired), "timeout_sec": timeout, "error": str(e)}
            exits[name] = record
            if record["exit_code"] != 0:
                break  # 科学固定失败保留，不重规划/不扩大种子/不改障碍。
        native_file = logger.path / "planning_metrics.json"
        native = json.loads(native_file.read_text()) if native_file.exists() else {}
        trial_metadata = []
        for case in native.get("cases", []):
            for trial in case["trials"]:
                m = RunMetadata(trial["trial_id"], "TASK06", metadata.baseline_id, metadata.platform, commit,
                    trial["repeat"], trial["seed"], tuple([str(build / "task06_model_test"), "--protocol", PROTOCOL]),
                    metadata.config_ids, metadata.config_paths, metadata.sources)
                trial_metadata.append(m.to_dict())
        with (logger.path / "trial_metadata.json").open("x") as handle:
            json.dump({"suite_seed": None, "suite_rng_status": "NO_SUITE_RNG_EXPLICIT_MULTISEED_CHILD_PLANNERS",
                "actual_rng": config["rng"], "trials": trial_metadata}, handle, indent=2, allow_nan=False)
        compressed = {}
        # Mechanical lossless compression before logger finalization; raw bytes hash retained.
        for path in sorted(logger.path.glob("*.json")):
            if not (path.name.startswith(("direct_", "negative_")) or "_seed" in path.name):
                continue
            raw = path.read_bytes()
            with path.with_suffix(".json.gz").open("xb") as handle:
                with gzip.GzipFile(filename="", mode="wb", fileobj=handle, mtime=0) as stream:
                    stream.write(raw)
            compressed[path.name] = {"compressed_path": path.name + ".gz", "raw_sha256": hashlib.sha256(raw).hexdigest(),
                "raw_bytes": len(raw), "compression": "LOSSLESS_GZIP_MTIME_ZERO"}
            path.unlink()  # only exact newly created own file, preserved losslessly in adjacent.gz
        after = {p: sha(ROOT / p) for p in protected}
        mesh_after = {str(p): sha(p) for p in meshes}
        legacy_after = verify_legacy_assets(LEGACY, load_manifest())
        unchanged = before == after and mesh_before == mesh_after and legacy_before == legacy_after
        software_ok = len(exits) == len(commands) and all(r["exit_code"] == 0 for r in exits.values())
        accepted = software_ok and unchanged and native.get("task06_status") == "PASS_CANDIDATE"
        summary = {"task06_status": "PASS_CANDIDATE" if accepted else "PARTIAL",
            "claim_scope": "OFFLINE_NR_CONSTRAINED_SEARCH_REAL_FR3_NATIVE_FCL_DISCRETE_ONLY",
            "commands": exits, "software_ok": software_ok, "protected_unchanged": unchanged,
            "protected_hashes_before": before, "protected_hashes_after": after,
            "mesh_hashes_before": mesh_before, "mesh_hashes_after": mesh_after,
            "legacy_assets_before": legacy_before, "legacy_assets_after": legacy_after,
            "compressed_evidence": compressed, "native_error": native.get("error"), "native_failures": native.get("failures"),
            "seed_policy": "THREE_ACTUAL_SEEDS_TWO_REPEATS_EACH_PER_SCENE", "seeds": config["seeds"],
            "minimum_collision_distance": "UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED",
            "simulation_time": None, "physics_step": None, "physical_commands": 0,
            "task02": "IN_PROGRESS", "task02_d": "PARTIAL_DEFERRED", "benchmark": "DRAFT_NOT_FROZEN",
            "continuous_collision_certificate": False, "task07_started": False}
        with (logger.path / "summary.json").open("x") as handle:
            json.dump(summary, handle, indent=2, allow_nan=False)
        logger.finish(BenchmarkResult(args.run_id, metadata.baseline_id,
            ResultStatus.SUCCESS if accepted else ResultStatus.FAILURE,
            "TASK06 offline engineering acceptance only, not physical or frozen Benchmark success",
            MeasurementQualification.UNQUALIFIED,
            tuple(p.name for p in sorted(logger.path.iterdir()) if p.is_file() and p.name != "metadata.json"),
            metadata.config_ids, tuple(s.source_id for s in metadata.sources),
            failure_stage=None if accepted else "OFFLINE_SEARCH_ACCEPTANCE", reason=None if accepted else "See complete bounded failures",
            limitations=("Discrete FCL only; no swept-volume guarantee or native minimum distance",
                "Inherited conservative NR/RBS guards; not paper singularity/performance reproduction",
                "TASK02-D deferred; no post-step/physical/suction certificate", "Benchmark DRAFT; TASK07 not started")))
    print(f"TASK06={summary['task06_status']}; evidence={logger.path}", flush=True)
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
