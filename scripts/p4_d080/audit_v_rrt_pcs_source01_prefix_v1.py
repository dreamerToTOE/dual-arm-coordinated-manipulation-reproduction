#!/usr/bin/env python3
"""Independent saved-prefix audit for the failed V SOURCE01 run.

The input is the already-written ``path_milestones.txt``/``temp.txt`` prefix.
This script never calls RRT, never resumes SOURCE01, and never changes the
source result.  It evaluates only the saved configurations with the pinned
independent FK/closure, branch, limits, and native/aligned collision checks.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import recover_p4_full_r2_endpoints as oracle
from baselines.p4_full.geometry_consistent import collision_adapter
from baselines.p4_full.geometry_consistent import physical_nr

RUN_DIR = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4"
MILESTONE_FILE = RUN_DIR / "runtime/paths/path_milestones.txt"
TEMP_FILE = RUN_DIR / "runtime/paths/temp.txt"
PROTOCOL = ROOT / "configs/p4_d080/v_rrt_pcs_source01_v4.json"
MANIFEST = Path("/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json")
OUTPUT_DIR = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT"
OUTPUT = OUTPUT_DIR / "audit.json"
GATES = {"position_maxabs_mm": 1e-5, "rotation_matrix_maxabs": 1e-5, "branch_zero_relative_epsilon": 64 * sys.float_info.epsilon}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_path(path: Path):
    rows = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    return [list(map(float, row.split())) for row in rows]


def max_abs(a, b):
    return max(abs(float(x) - float(y)) for x, y in zip(a, b))


def finite_q(q):
    return len(q) == 12 and all(math.isfinite(float(x)) for x in q)


def audit_node(index, q):
    closure = physical_nr.residual_metrics(q, "V")
    limits = oracle.limit_score(q, "V")
    branches = [oracle.branch_identity(q[6 * arm:6 * arm + 6], "V", GATES["branch_zero_relative_epsilon"]) for arm in range(2)]
    collision = collision_adapter.check_collision("V", q, timeout_s=10.0, manifest_path=MANIFEST)
    variants = collision.get("variants", {})
    native = variants.get("native", {})
    aligned = variants.get("aligned", {})
    math_pass = closure["translation_max_abs"] <= GATES["position_maxabs_mm"] and closure["rotation_matrix_max_abs"] <= GATES["rotation_matrix_maxabs"]
    branch_pass = all(row.get("unique") is True and len(row.get("branch_set", [])) == 1 for row in branches)
    collision_pass = collision.get("status") == "CHECKED" and aligned.get("pose_consistency", {}).get("passed") is True and all(
        isinstance(code, int) and code == 0 for code in aligned.get("query_codes", [])
    )
    return {
        "node_id": index,
        "q12": q,
        "closure": closure,
        "closure_gate": {"position_maxabs_mm": GATES["position_maxabs_mm"], "rotation_matrix_maxabs": GATES["rotation_matrix_maxabs"], "passed": math_pass},
        "limits": limits,
        "limits_passed": limits.get("legal") is True,
        "ik_branch_identity": branches,
        "ik_branch_gate_passed": branch_pass,
        "collision": collision,
        "original_native_collision": native.get("native_collision"),
        "aligned_collision": aligned.get("native_collision"),
        "original_query_codes": native.get("query_codes", []),
        "aligned_query_codes": aligned.get("query_codes", []),
        "collision_gate_passed": collision_pass,
        "node_discrete_gate_passed": math_pass and limits.get("legal") is True and branch_pass and collision_pass and aligned.get("native_collision") is False,
    }


def main():
    begun = time.monotonic()
    protocol = json.loads(PROTOCOL.read_text())
    start_q = protocol["request"]["start_q12"]
    goal_q = protocol["request"]["goal_q12"]
    milestone_lines = MILESTONE_FILE.read_text().splitlines()
    declared = int(milestone_lines[0])
    milestones = parse_path(MILESTONE_FILE)[0:]  # header is nonnumeric and excluded by parse_path below
    # parse_path intentionally receives the separate numeric suffix to keep the
    # source file byte-for-byte untouched.
    milestones = [list(map(float, line.split())) for line in milestone_lines[1:] if line.strip()]
    temp = parse_path(TEMP_FILE)
    nodes = []
    try:
        for index, q in enumerate(milestones):
            if not finite_q(q):
                raise ValueError(f"INVALID_MILESTONE_{index}")
            nodes.append(audit_node(index, q))
    finally:
        collision_adapter.close_sessions()

    milestone_step_l2 = [math.sqrt(sum((float(b) - float(a)) ** 2 for a, b in zip(milestones[i], milestones[i + 1]))) for i in range(len(milestones) - 1)]
    temp_first = max_abs(temp[0], milestones[0]) if temp else math.inf
    temp_last_errors = [max_abs(temp[-1], q) for q in milestones] if temp else []
    nearest_temp_last = min(range(len(milestones)), key=lambda i: temp_last_errors[i]) if temp else None
    start_error = max_abs(milestones[0], start_q)
    goal_error = max_abs(milestones[-1], goal_q)
    result = {
        "schema": "P4_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT_V1",
        "status": "FAIL_PREFIX_CANDIDATE_NOT_A_COMPLETE_PATH",
        "personnel_independent": True,
        "source_run": "20261019_R2_D080_V_RRT_PCS_SOURCE01_V4",
        "source_boundary": "PREFIX_CANDIDATE_FROM_FAILED_SOURCE_RUN",
        "independent_path_qualified": False,
        "continuous_collision_certificate": False,
        "formal_table_I_calls": 0,
        "new_VI_candidate_constructions": 0,
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": sha(PROTOCOL),
        "manifest": str(MANIFEST),
        "manifest_sha256": sha(MANIFEST),
        "milestone_file": str(MILESTONE_FILE.relative_to(ROOT)),
        "milestone_file_sha256": sha(MILESTONE_FILE),
        "temp_file": str(TEMP_FILE.relative_to(ROOT)),
        "temp_file_sha256": sha(TEMP_FILE),
        "declared_milestones": declared,
        "observed_milestones": len(milestones),
        "temp_configurations": len(temp),
        "start_endpoint": {"max_abs_rad_difference": start_error, "within_1e-12": start_error <= 1e-12, "within_2e-6_rounding": start_error <= 2e-6},
        "goal_endpoint": {"max_abs_rad_difference": goal_error, "within_1e-12": goal_error <= 1e-12},
        "path_backtracking": {
            "milestone_adjacent_l2_rad": milestone_step_l2,
            "all_adjacent_steps_finite_nonzero": bool(milestone_step_l2) and all(math.isfinite(v) and v > 0 for v in milestone_step_l2),
            "temp_first_max_abs_to_milestone0": temp_first,
            "temp_last_max_abs_to_each_milestone": temp_last_errors,
            "temp_last_nearest_milestone_index": nearest_temp_last,
            "temp_reaches_declared_final_milestone": bool(temp_last_errors) and temp_last_errors[-1] <= 1e-12,
            "trace_backtracking_complete": False,
            "reason": "temp.txt ends at an earlier reconstructed prefix while path_milestones.txt contains a later partial milestone; no complete source result or final goal trace exists.",
        },
        "nodes": nodes,
        "node_discrete_pass_count": sum(bool(row["node_discrete_gate_passed"]) for row in nodes),
        "node_discrete_fail_count": sum(not bool(row["node_discrete_gate_passed"]) for row in nodes),
        "audit_elapsed_wall_s": time.monotonic() - begun,
        "limitations": [
            "Closure and branch results are independent checks of rounded saved configurations; they do not reconstruct missing source precision.",
            "IK branch identity is an invariant check, not a fresh native IK solve or proof of a source branch transport.",
            "Native and aligned collision results are discrete endpoint queries; they do not certify continuous collision-free interpolation.",
            "The source process limit and source solve limit were already consumed; this audit did not relaunch or resume the planner.",
        ],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "nodes": len(nodes), "node_discrete_pass_count": result["node_discrete_pass_count"], "node_discrete_fail_count": result["node_discrete_fail_count"], "start_error": start_error, "goal_error": goal_error, "elapsed_wall_s": result["audit_elapsed_wall_s"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
