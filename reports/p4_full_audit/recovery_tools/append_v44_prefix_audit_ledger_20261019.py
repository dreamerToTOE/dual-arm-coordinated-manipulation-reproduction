#!/usr/bin/env python3
"""Append the saved-prefix physical audit cost after the immutable V43 ledger."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V43.json"
NEW = ROOT / "results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V44.json"
RUN = "20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT"
AUDIT = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT/audit.json"
CHARGE = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT/external_charge.json"
RECEIPT = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT/cost_receipt.json"
POST = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_PREFIX_AUDIT_SAVED_INDEPENDENT_POST_20261019.json"
TIME = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT.supervision.time.txt"
STDOUT = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT.supervision.stdout.log"
STDERR = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT.supervision.stderr.log"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_bytes())


def require(value: bool, message: str):
    if not value:
        raise RuntimeError(message)


old = load(OLD)
audit = load(AUDIT)
charge = load(CHARGE)
receipt = load(RECEIPT)
post = load(POST)
require(post["checks_failed"] == 0 and post["status"] == "PASS_PREFIX_AUDIT_REJECTS_COMPLETE_PATH", "PREFIX_POST")
require(charge["execution_sha256"] == sha(AUDIT) and charge["receipt_sha256"] == sha(RECEIPT), "PREFIX_COST_LINKS")
require(charge["wall_s"] == 1.81 and charge["cpu_s"] == 1.8900000000000001 and charge["time_returncode"] == 0, "PREFIX_COST")

source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
row = {
    "run_id": RUN,
    "execution": str(AUDIT.relative_to(ROOT)),
    "execution_sha256": sha(AUDIT),
    "source_commit": source_commit,
    "status": audit["status"],
    "classification": "INDEPENDENT_SAVED_V_SOURCE_PREFIX_PHYSICAL_AUDIT",
    "engineering_only": False,
    "wall_s": audit["audit_elapsed_wall_s"],
    "cpu_s": None,
    "counts": {
        "audit_nodes": 6,
        "collision_calls": 6,
        "native_collision_queries": 6,
        "aligned_collision_queries": 6,
        "source_process_calls": 0,
        "source_solve_calls": 0,
    },
    "authorization_budget_id": None,
    "formal_planning_calls": 0,
    "formal_table_I_calls": 0,
    "new_VI_candidate_constructions": 0,
    "charged_wall_s": charge["wall_s"],
    "charged_cpu_s": charge["cpu_s"],
    "charge_basis": charge["charge_basis"],
    "external_charge": str(CHARGE.relative_to(ROOT)),
    "external_charge_sha256": sha(CHARGE),
    "internal_receipt": str(RECEIPT.relative_to(ROOT)),
    "internal_receipt_sha256": sha(RECEIPT),
    "external_post": str(POST.relative_to(ROOT)),
    "external_post_sha256": sha(POST),
    "external_time": str(TIME.relative_to(ROOT)),
    "external_time_sha256": sha(TIME),
    "external_stdout": str(STDOUT.relative_to(ROOT)),
    "external_stdout_sha256": sha(STDOUT),
    "external_stderr": str(STDERR.relative_to(ROOT)),
    "external_stderr_sha256": sha(STDERR),
    "execution_cap_breach": {"wall": False, "cpu": False},
    "scientific_calls": 1,
    "source_process_calls": 0,
    "independent_path_qualified": False,
    "continuous_collision_certificate": False,
    "prefix_audit_only": True,
}

rows = old["executions"] + [row]
require(len(rows) == 61 and row["execution"] not in {item["execution"] for item in old["executions"]}, "ROW_COUNT")
charged_wall = math.fsum(item.get("charged_wall_s", item["wall_s"]) for item in rows)
charged_cpu = math.fsum(item.get("charged_cpu_s", item["cpu_s"]) or 0.0 for item in rows)
science = [item for item in rows if not item["engineering_only"]]
engineering = [item for item in rows if item["engineering_only"]]

new = copy.deepcopy(old)
new.update(
    {
        "schema": "P4_R2_RECOVERY_ACTUAL_LEDGER_V44",
        "previous_snapshot": str(OLD.relative_to(ROOT)),
        "previous_snapshot_sha256": sha(OLD),
        "executions": rows,
        "count": 61,
        "science_count": len(science),
        "engineering_count": len(engineering),
        "actual_runtime_execution_records_excluding_saved_only_recovery": old["actual_runtime_execution_records_excluding_saved_only_recovery"] + 1,
        "science_wall_s": math.fsum(item.get("charged_wall_s", item["wall_s"]) for item in science),
        "science_cpu_s": math.fsum(item.get("charged_cpu_s", item["cpu_s"]) or 0.0 for item in science),
        "engineering_wall_s": math.fsum(item.get("charged_wall_s", item["wall_s"]) for item in engineering),
        "engineering_cpu_s": math.fsum(item.get("charged_cpu_s", item["cpu_s"]) or 0.0 for item in engineering),
        "conservative_r2_sum_wall_s": charged_wall,
        "conservative_r2_sum_cpu_s": charged_cpu,
        "r2_remaining": {"wall_s": old["r2_caps"]["wall_s"] - charged_wall, "cpu_s": old["r2_caps"]["cpu_s"] - charged_cpu},
        "last_actual_execution": row,
        "new_scientific_calls": 1,
        "new_qualification_planner_solves_in_this_snapshot": 0,
        "previous_snapshot_qualification_planner_solves": old.get("total_qualification_planner_solves", 8),
        "total_qualification_planner_solves": old.get("total_qualification_planner_solves", 8),
        "scope": "D080 I-V retained; V SOURCE01 failure and saved-prefix physical audit appended. No formal statistics, VI work, or complete path promotion.",
        "ledger_correction": {
            "kind": "APPEND_SAVED_PREFIX_PHYSICAL_AUDIT_COST",
            "previous_snapshot": str(OLD.relative_to(ROOT)),
            "execution_sha256": sha(AUDIT),
            "post_sha256": sha(POST),
            "source_process_calls": 0,
            "collision_calls": 6,
            "formal_table_I_calls": 0,
            "new_VI_candidate_constructions": 0,
            "status": "FAIL_PREFIX_CANDIDATE_NOT_A_COMPLETE_PATH",
        },
    }
)
accounting = copy.deepcopy(old["authoritative_source_solve_accounting"])
accounting["previous_snapshot"] = str(OLD.relative_to(ROOT))
accounting["previous_snapshot_sha256"] = sha(OLD)
accounting["previous_actual_source_solve_dispatches"] = old["authoritative_source_solve_accounting"]["total_actual_source_solve_dispatches"]
accounting["new_actual_source_solve_dispatches"] = 0
accounting["total_actual_source_solve_dispatches"] = accounting["previous_actual_source_solve_dispatches"]
accounting["ledger_generation_new_source_solve_dispatches"] = 0
new["authoritative_source_solve_accounting"] = accounting

NEW.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"ledger": str(NEW.relative_to(ROOT)), "sha256": sha(NEW), "count": len(rows), "science_count": len(science), "engineering_count": len(engineering), "wall_s": charged_wall, "cpu_s": charged_cpu, "source_dispatches": accounting["total_actual_source_solve_dispatches"]}, ensure_ascii=False))
