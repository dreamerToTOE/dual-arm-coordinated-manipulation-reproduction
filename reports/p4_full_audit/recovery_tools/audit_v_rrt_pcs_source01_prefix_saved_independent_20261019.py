#!/usr/bin/env python3
"""Saved-only POST for the V SOURCE01 prefix candidate audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT"
AUDIT = AUDIT_DIR / "audit.json"
RECEIPT = AUDIT_DIR / "cost_receipt.json"
CHARGE = AUDIT_DIR / "external_charge.json"
TIME = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT.supervision.time.txt"
STDOUT = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT.supervision.stdout.log"
STDERR = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT.supervision.stderr.log"
SCRIPT = ROOT / "scripts/p4_d080/audit_v_rrt_pcs_source01_prefix_v1.py"
SOURCE_EXEC = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4/execution.json"
SOURCE_POST = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_V4_FAILURE_SAVED_INDEPENDENT_POST_20261019.json"
POST = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_PREFIX_AUDIT_SAVED_INDEPENDENT_POST_20261019.json"

checks = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_bytes())


def check(name: str, passed: bool, evidence=None):
    row = {"name": name, "passed": bool(passed)}
    if evidence is not None:
        row["evidence"] = evidence
    checks.append(row)


a = load(AUDIT)
c = load(CHARGE)
receipt = load(RECEIPT)
source = load(SOURCE_EXEC)
source_post = load(SOURCE_POST)

check("saved_audit_schema_and_failure_boundary", a["schema"] == "P4_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT_V1" and a["status"] == "FAIL_PREFIX_CANDIDATE_NOT_A_COMPLETE_PATH" and a["personnel_independent"] is True and a["independent_path_qualified"] is False and a["continuous_collision_certificate"] is False)
check("source_failure_is_unchanged_and_not_relaunched", source["status"] == "STOP_PREFIX_RETAINED" and source["counts"]["source_process_started"] == 1 and source["counts"]["source_request_dispatched"] == 1 and source_post["checks_failed"] == 0 and source_post["independent_path_qualified"] is False)
check("fixed_six_milestones_and_complete_node_audit", a["declared_milestones"] == a["observed_milestones"] == 6 and len(a["nodes"]) == 6 and a["node_discrete_pass_count"] == 0 and a["node_discrete_fail_count"] == 6)
check("endpoint_and_backtracking_failure_recorded", a["start_endpoint"]["within_1e-12"] is False and a["start_endpoint"]["within_2e-6_rounding"] is True and a["goal_endpoint"]["within_1e-12"] is False and a["goal_endpoint"]["max_abs_rad_difference"] > 1.0 and a["path_backtracking"]["trace_backtracking_complete"] is False and a["path_backtracking"]["temp_reaches_declared_final_milestone"] is False)
check("each_node_strict_closure_gate_rejected_rounding_prefix", all(row["closure_gate"]["passed"] is False and row["closure"]["translation_max_abs"] > 1e-5 for row in a["nodes"]))
check("each_node_limits_and_branch_invariants_recorded", all(row["limits_passed"] is True and row["ik_branch_gate_passed"] is True and [x["branch_set"] for x in row["ik_branch_identity"]] == [[3], [3]] for row in a["nodes"]))
check("native_and_aligned_collision_queries_are_retained", all(row["collision"]["status"] == "CHECKED" and row["original_native_collision"] is False and row["aligned_collision"] is False and row["collision_gate_passed"] is True and all(code == 0 for code in row["original_query_codes"] + row["aligned_query_codes"]) for row in a["nodes"]))
check("no_continuous_or_path_promotion", all(row["node_discrete_gate_passed"] is False for row in a["nodes"]) and a["continuous_collision_certificate"] is False and a["independent_path_qualified"] is False)
check("audit_cost_receipt_and_gnu_time_exit0", receipt["source_execution_sha256"] == sha(AUDIT) and receipt["external_supervision_qualified"] is False and receipt["status"] == a["status"] and receipt["audit_elapsed_wall_s"] > 0 and receipt["audit_elapsed_wall_s"] < 2.0 and sha(TIME) == c["time_sha256"] and c["time_returncode"] == 0 and c["completed_process_exit0"] is True and c["wall_s"] == 1.81 and c["cpu_s"] == 1.8900000000000001)
check("all_saved_input_and_script_hashes_bind", a["protocol_sha256"] == sha(ROOT / a["protocol"]) and a["manifest_sha256"] == sha(Path(a["manifest"])) and a["milestone_file_sha256"] == sha(ROOT / a["milestone_file"]) and a["temp_file_sha256"] == sha(ROOT / a["temp_file"]) and sha(SCRIPT) == load(CHARGE)["audit_script_sha256"] and sha(AUDIT) == load(CHARGE)["execution_sha256"] and sha(RECEIPT) == load(CHARGE)["receipt_sha256"] and sha(STDOUT) == load(CHARGE)["stdout_sha256"] and sha(STDERR) == load(CHARGE)["stderr_sha256"])
check("zero_formal_vi_and_source_relaunch_calls", a["formal_table_I_calls"] == 0 and a["new_VI_candidate_constructions"] == 0 and load(CHARGE)["new_source_process_calls"] == 0)

failed = [row for row in checks if not row["passed"]]
report = {
    "schema": "P4_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT_SAVED_INDEPENDENT_POST_V1",
    "personnel_independent": True,
    "status": "PASS_PREFIX_AUDIT_REJECTS_COMPLETE_PATH" if not failed else "FAIL_PREFIX_AUDIT_POST",
    "checks_total": len(checks),
    "checks_passed": len(checks) - len(failed),
    "checks_failed": len(failed),
    "checks": checks,
    "failures": failed,
    "external_supervision_qualified": False,
    "external_timing_qualified": True,
    "external_cost_qualified": True,
    "independent_path_qualified": False,
    "continuous_collision_certificate": False,
    "source_run": "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4/execution.json",
    "source_run_sha256": sha(SOURCE_EXEC),
    "source_failure_post": str(SOURCE_POST.relative_to(ROOT)),
    "source_failure_post_sha256": sha(SOURCE_POST),
    "audit": str(AUDIT.relative_to(ROOT)),
    "audit_sha256": sha(AUDIT),
    "cost_receipt": str(RECEIPT.relative_to(ROOT)),
    "cost_receipt_sha256": sha(RECEIPT),
    "external_charge": str(CHARGE.relative_to(ROOT)),
    "external_charge_sha256": sha(CHARGE),
    "external_time": str(TIME.relative_to(ROOT)),
    "external_time_sha256": sha(TIME),
    "audit_script": str(SCRIPT.relative_to(ROOT)),
    "audit_script_sha256": sha(SCRIPT),
    "charged_wall_s": load(CHARGE)["wall_s"],
    "charged_cpu_s": load(CHARGE)["cpu_s"],
    "source_process_calls": 0,
    "formal_table_I_calls": 0,
    "new_VI_candidate_constructions": 0,
    "limitations": [
        "The six configurations are a saved prefix from a failed source run, not a source result or complete path.",
        "Rounded path text fails the strict closure gate; branch and discrete collision observations do not repair the missing endpoint/trace.",
        "Native/aligned endpoint queries do not establish continuous collision-free interpolation or planner success.",
        "The audit used direct GNU time without a separate supervisor; its measured cost is recorded separately from the SOURCE01 charge.",
    ],
}
POST.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ("status", "checks_total", "checks_passed", "checks_failed", "charged_wall_s", "charged_cpu_s")}, ensure_ascii=False))
