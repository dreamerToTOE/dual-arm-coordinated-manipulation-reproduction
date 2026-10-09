"""有界离线验收及文件记录；无 ROS context、执行器、仿真或 IK。"""

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


ROOT = Path(__file__).resolve().parents[1]
URDF = "tests/fixtures/task03/robot.urdf"
SRDF = "tests/fixtures/task03/robot.srdf"
FIXTURE = "results/20261007_TASK01_full_single_cube_geometry01/state_records.json"
CONFIG = "results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml"
PROTECTED = (
    "configs/benchmark/benchmark_v1.yaml",
    "common/interfaces/state.py", "common/interfaces/exchange.py",
    "common/interfaces/wire.py", "common/logging/run.py",
)
PROTECTED_DIRS = ("common/metrics", "platforms/isaac_ros2/foundation")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--build-dir", default="build/task03_closure")
    args = parser.parse_args()
    sources = sorted(set([
        URDF, SRDF, FIXTURE, CONFIG, "scripts/run_task03_offline.py",
        "common/geometry/se3.hpp", "baselines/p4_closed_chain/closure.hpp",
        "baselines/p4_closed_chain/closure.cpp", "tests/task03_closure_math.cpp",
    ] + [str(p.relative_to(ROOT)) for p in
         (ROOT / "platforms/offline_moveit/task03_closure").glob("*") if p.is_file()]))
    protected = list(PROTECTED) + [str(p.relative_to(ROOT)) for directory in PROTECTED_DIRS
                                  for p in (ROOT / directory).rglob("*")
                                  if p.is_file() and "__pycache__" not in p.parts]
    before = {p: digest(ROOT / p) for p in protected}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = RunMetadata(
        args.run_id, "TASK03", "P4_CLOSURE_MATH", "OFFLINE_MOVEIT_CORE_EIGEN_PYTHON",
        commit, 0, None, tuple([sys.executable] + sys.argv), ("archived_grasp",), (CONFIG,),
        tuple(source_ref(f"source_{i}", ROOT / path) for i, path in enumerate(sources)),
    )
    with RunLogger(ROOT / "results", metadata) as logger:
        output = logger.path / "model_metrics.json"
        commands = [
            ("task02_regression.log", [sys.executable, "-m", "unittest", "discover",
                                       "-s", "tests", "-p", "test_task02*.py", "-v"]),
            ("task03_math.log", [str(ROOT / args.build_dir / "task03_math_test")]),
            ("ctest.log", ["ctest", "--test-dir", args.build_dir, "--output-on-failure"]),
            ("real_model.log", [str(ROOT / args.build_dir / "task03_model_test"),
                                "--urdf", URDF, "--srdf", SRDF, "--fixture", FIXTURE,
                                "--config", CONFIG, "--output", str(output)]),
        ]
        exits = {}
        for name, command in commands:
            # 只运行列出的离线测试；单个测试 60s 上限，不添加任何后台服务。
            with (logger.path / name).open("x", encoding="utf-8") as handle:
                completed = subprocess.run(command, cwd=ROOT, stdout=handle,
                                           stderr=subprocess.STDOUT, timeout=60, check=False)
            exits[name] = {"argv": command, "exit_code": completed.returncode}
        after = {p: digest(ROOT / p) for p in protected}
        model = json.loads(output.read_text()) if output.exists() else {}
        software_pass = all(v["exit_code"] == 0 for v in exits.values()) and before == after
        task_status = model.get("task03_status", "PARTIAL") if software_pass else "PARTIAL"
        summary = {
            "task03_status": task_status, "software_tests_passed": software_pass,
            "commands": exits, "protected_hashes_before": before,
            "protected_hashes_after": after, "protected_unchanged": before == after,
            "seed": None, "seed_status": "UNSET", "random_ik_or_rng_used": False,
            "simulation_stamp": None, "physics_step": None,
            "qualification": "OFFLINE_KINEMATICS_NOT_PHYSICAL_OR_SCIENTIFIC_TIME_SERIES",
        }
        with (logger.path / "summary.json").open("x", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, allow_nan=False)
            handle.write("\n")
        accepted = software_pass and task_status == "PASS_CANDIDATE"
        logger.finish(BenchmarkResult(
            args.run_id, "P4_CLOSURE_MATH",
            ResultStatus.SUCCESS if accepted else (ResultStatus.INCOMPLETE if software_pass else ResultStatus.FAILURE),
            "TASK03 offline mathematical acceptance only; no physical benchmark success",
            MeasurementQualification.UNQUALIFIED,
            ("model_metrics.json", "summary.json", "task02_regression.log", "task03_math.log", "ctest.log", "real_model.log"),
            metadata.config_ids, tuple(s.source_id for s in metadata.sources),
            failure_stage=None if accepted else ("ORIGINAL_FIXED_GRASP_CLOSURE_PRECISION" if software_pass else "OFFLINE_SOFTWARE_TEST"),
            reason=None if accepted else ("Original fixed-grasp historical closure exceeds predeclared engineering precision; no threshold/IK/grasp change" if software_pass else "See saved exits/logs and protected hashes"),
            limitations=("Not synchronized measured physics", "No collision, suction, projection or planner validation", "Benchmark DRAFT / NOT FROZEN"),
        ))
    print(f"software_tests_passed={software_pass}; TASK03={task_status}; evidence={logger.path}")
    # 退出0只表示离线软件检查通过；TASK03和统一结果另行明确记录。
    return 0 if software_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
