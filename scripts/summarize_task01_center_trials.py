"""Summarize Task01 Cube_05 exploratory ROS logs; never infer a PASS from plans alone.

The parser only reads logs. It does not define or change benchmark thresholds.
"""

import argparse
import json
import re
import statistics
from pathlib import Path


NUMBER = r"([+-]?\d+(?:\.\d+)?)"
FINAL = re.compile(
    rf"center Ground Truth: .*?cell_error={NUMBER} mm, "
    rf"\+X_gap={NUMBER} mm, \+Y_inner_gap={NUMBER} mm, "
    rf"-Y_inner_gap={NUMBER} mm, total={NUMBER} mm"
)
TORQUE = re.compile(rf"PUSH complete: peak_torque={NUMBER} Nm")
PUSHER = re.compile(r"Task01 center pusher=(left|right)")
START_TIME = re.compile(r"^\[[A-Z]+\] \[(\d+\.\d+)\]")


def read_run(path):
    body = Path(path).read_text(encoding="utf-8", errors="replace")
    final_matches = FINAL.findall(body)
    torque_matches = TORQUE.findall(body)
    pusher_matches = PUSHER.findall(body)
    stamps = [float(match.group(1)) for line in body.splitlines()
              if (match := START_TIME.match(line))]
    success = "Task27 batch 5 PASS" in body
    if success and (len(final_matches) != 1 or len(torque_matches) != 1 or
                    len(set(pusher_matches)) != 1):
        raise ValueError(f"PASS log has ambiguous/missing metrics: {path}")
    metrics = None
    if len(final_matches) == 1:
        center, wall, plus, minus, total = map(float, final_matches[0])
        metrics = {
            "center_error_mm": center,
            "deep_wall_gap_mm": wall,
            "plus_y_gap_mm": plus,
            "minus_y_gap_mm": minus,
            "gap_sum_mm": total,
            "gap_imbalance_mm": abs(plus - minus),
            "peak_joint_torque_nm": float(torque_matches[0]) if torque_matches else None,
        }
    return {
        "log_path": str(Path(path).resolve()),
        "arm": pusher_matches[-1] if pusher_matches else None,
        "status": "PASS" if success else "FAIL_OR_INCOMPLETE",
        "pre_close_reacquire": "PRE_CLOSE_REACQUIRE" in body,
        "logged_duration_sec": round(stamps[-1] - stamps[0], 3) if len(stamps) > 1 else None,
        "metrics": metrics,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="+", help="Task27 ROS log paths")
    args = parser.parse_args()
    runs = [read_run(path) for path in args.logs]
    aggregate = {}
    for arm in ("left", "right"):
        subset = [run for run in runs if run["arm"] == arm]
        complete = [run for run in subset if run["status"] == "PASS"]
        aggregate[arm] = {
            "runs": len(subset),
            "passes": len(complete),
            "mean_center_error_mm": (
                statistics.mean(run["metrics"]["center_error_mm"] for run in complete)
                if complete else None
            ),
            "max_center_error_mm": (
                max(run["metrics"]["center_error_mm"] for run in complete)
                if complete else None
            ),
            "max_gap_imbalance_mm": (
                max(run["metrics"]["gap_imbalance_mm"] for run in complete)
                if complete else None
            ),
        }
    print(json.dumps({"runs": runs, "aggregate": aggregate},
                     ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
