"""TASK04 有界离线投影验收；复用 TASK02 日志和 TASK03 数学/真实模型测试。"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from common.interfaces.exchange import (
    BenchmarkResult, MeasurementQualification, ResultStatus, RunMetadata,
)
from common.logging.run import RunLogger, source_ref
from platforms.isaac_ros2.foundation.legacy_task26 import load_manifest, verify_legacy_assets


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "configs/engineering/task04_projection_test_v1.json"
URDF = "tests/fixtures/task03/robot.urdf"
SRDF = "tests/fixtures/task03/robot.srdf"
FIXTURE = "results/20261007_TASK01_full_single_cube_geometry01/state_records.json"
CONFIG = "results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml"
LEGACY_ROOT = Path("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_files():
    return subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")[:-1]


def protected_files():
    # 保护原始数学/测试/模型、历史证据和 TASK02 已验收语义。文档分类记录不在其中。
    prefixes = (
        "common/", "tests/fixtures/", "platforms/isaac_ros2/",
        "platforms/offline_moveit/task03_closure/", "results/", "configs/benchmark/",
    )
    exact = {
        "baselines/p4_closed_chain/closure.hpp", "baselines/p4_closed_chain/closure.cpp",
        "tests/task03_closure_math.cpp", "scripts/run_task03_offline.py", PROTOCOL,
    }
    return sorted(path for path in tracked_files()
                  if path in exact or path.startswith(prefixes) or path.startswith("tests/test_task02"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--build-dir", default="build/task04_projection")
    args = parser.parse_args()
    build = (ROOT / args.build_dir).resolve()
    if not build.is_relative_to(ROOT / "build"):
        parser.error("build-dir must be inside the repository's ignored build directory")
    sources = sorted({
        PROTOCOL, URDF, SRDF, FIXTURE, CONFIG, "scripts/run_task04_offline.py",
        "common/geometry/se3.hpp", "common/logging/run.py",
        "baselines/p4_closed_chain/closure.hpp", "baselines/p4_closed_chain/closure.cpp",
        "baselines/p4_closed_chain/projection.hpp", "baselines/p4_closed_chain/projection.cpp",
        "tests/task03_closure_math.cpp", "tests/task04_projection_math.cpp",
    } | {str(p.relative_to(ROOT)) for directory in (
        "platforms/offline_moveit/task03_closure", "platforms/offline_moveit/task04_projection")
        for p in (ROOT / directory).glob("*") if p.is_file()})
    protected = protected_files()
    before = {path: digest(ROOT / path) for path in protected}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = RunMetadata(
        args.run_id, "TASK04", "P4_NR_PROJECTION", "OFFLINE_MOVEIT_CORE_EIGEN_PYTHON",
        commit, 0, None, tuple([sys.executable] + sys.argv), ("D048_task04_v1",),
        (PROTOCOL, CONFIG),
        tuple(source_ref(f"source_{i}", ROOT / path) for i, path in enumerate(sources)),
    )
    with RunLogger(ROOT / "results", metadata) as logger:
        legacy_before = verify_legacy_assets(LEGACY_ROOT, load_manifest())
        projection_output = logger.path / "projection_metrics.json"
        regression_output = logger.path / "task03_regression_metrics.json"
        commands = [
            ("configure.log", ["cmake", "-S", "platforms/offline_moveit/task04_projection",
                               "-B", str(build), "-DCMAKE_BUILD_TYPE=Release"], 60),
            ("build.log", ["cmake", "--build", str(build), "--parallel", "2"], 180),
            ("task02_regression.log", [sys.executable, "-m", "unittest", "discover",
                                       "-s", "tests", "-p", "test_task02*.py", "-v"], 60),
            ("task03_math.log", [str(build / "task03_reuse/task03_math_test")], 60),
            ("task04_math.log", [str(build / "task04_projection_math")], 60),
            ("ctest.log", ["ctest", "--test-dir", str(build), "--output-on-failure"], 60),
            ("task03_real_model.log", [str(build / "task03_reuse/task03_model_test"),
                                      "--urdf", URDF, "--srdf", SRDF, "--fixture", FIXTURE,
                                      "--config", CONFIG, "--output", str(regression_output)], 60),
            ("task04_real_model.log", [str(build / "task04_model_test"), "--protocol", PROTOCOL,
                                      "--output", str(projection_output)], 60),
        ]
        exits = {}
        for name, command, timeout in commands:
            print(f"TASK04 offline: {name}", flush=True)
            with (logger.path / name).open("x", encoding="utf-8") as handle:
                try:
                    completed = subprocess.run(command, cwd=ROOT, stdout=handle,
                                               stderr=subprocess.STDOUT, timeout=timeout, check=False)
                    record = {"argv": command, "exit_code": completed.returncode,
                              "timeout_sec": timeout, "timed_out": False}
                except (subprocess.TimeoutExpired, OSError) as error:
                    record = {"argv": command, "exit_code": None, "timeout_sec": timeout,
                              "timed_out": isinstance(error, subprocess.TimeoutExpired),
                              "error": str(error)}
            exits[name] = record
            if record["exit_code"] != 0:
                break  # 软件失败后不继续实验，不自动调参或增加重试。
        after = {path: digest(ROOT / path) for path in protected}
        legacy = verify_legacy_assets(LEGACY_ROOT, load_manifest())
        model = json.loads(projection_output.read_text()) if projection_output.exists() else {}
        regression = json.loads(regression_output.read_text()) if regression_output.exists() else {}
        software_pass = (len(exits) == len(commands) and
                         all(v["exit_code"] == 0 for v in exits.values()) and
                         before == after and legacy_before == legacy)
        accepted = software_pass and model.get("task04_status") == "PASS_CANDIDATE"
        summary = {
            "task04_status": "PASS_CANDIDATE" if accepted else "PARTIAL",
            "claim_scope": "OFFLINE_PROJECTION_MATHEMATICS_ONLY",
            "task03_reviewed_mathematical_status": "PASS_CANDIDATE_OFFLINE_MATHEMATICS_ONLY",
            "task03_original_precision_status_unchanged": model.get(
                "historical_original_summary", {}).get("unprojected_TASK03_acceptance", {}).get("status"),
            "task03_regression_unreviewed_diagnostic_status": regression.get("task03_status"),
            "software_tests_passed": software_pass, "commands": exits,
            "protected_hashes_before": before, "protected_hashes_after": after,
            "protected_unchanged": before == after, "legacy_assets_before": legacy_before,
            "legacy_assets_after": legacy, "legacy_root": str(LEGACY_ROOT),
            "seed": None, "seed_status": "UNSET", "random_sampling_or_ik_used": False,
            "simulation_stamp": None, "physics_step": None,
            "benchmark_status": "DRAFT_NOT_FROZEN", "task02_status": "IN_PROGRESS",
            "task05_or_task06_started": False,
            "qualification": "OFFLINE_MATHEMATICS_NOT_PHYSICAL_OR_SCIENTIFIC_TIME_SERIES",
        }
        with (logger.path / "summary.json").open("x", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, allow_nan=False)
            handle.write("\n")
        logger.finish(BenchmarkResult(
            args.run_id, "P4_NR_PROJECTION",
            ResultStatus.SUCCESS if accepted else ResultStatus.FAILURE,
            "TASK04 offline projection test acceptance only; not physical Benchmark success",
            MeasurementQualification.UNQUALIFIED,
            tuple(path.name for path in sorted(logger.path.iterdir())
                  if path.is_file() and path.name != "metadata.json"),
            metadata.config_ids, tuple(s.source_id for s in metadata.sources),
            failure_stage=None if accepted else "OFFLINE_SOFTWARE_OR_PROJECTION_ACCEPTANCE",
            reason=None if accepted else "See preserved bounded test logs, summary and per-trial evidence",
            limitations=("No synchronized physics measurements", "No collision/path or full P4 validation",
                         "Rank-deficient correction intentionally not qualified", "Fixed SI units, no scale-invariance claim",
                         "Benchmark DRAFT / NOT FROZEN; original TASK03 precision FAIL retained"),
        ))
    print(f"TASK04={summary['task04_status']}; evidence={logger.path}")
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
