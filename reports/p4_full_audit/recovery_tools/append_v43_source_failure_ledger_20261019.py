#!/usr/bin/env python3
"""Append the independently audited V SOURCE01 failure to a new ledger snapshot.

V42 is immutable.  The source request is counted once as an actual dispatch,
even though its result JSON and complete trace were not transported.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V42.json"
NEW = ROOT / "results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V43.json"
RUN = "20261019_R2_D080_V_RRT_PCS_SOURCE01_V4"
EXEC = ROOT / "results/p4_full" / RUN / "execution.json"
CHARGE = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4.supervision.charge.json"
POST = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_V4_FAILURE_SAVED_INDEPENDENT_POST_20261019.json"
TIME = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4.supervision.time.txt"
META = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4.supervision.jsonl"
STDERR = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4.supervision.stderr.log"
RECEIPT = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4/cost_receipt.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_bytes())


def require(condition: bool, message: str):
    if not condition:
        raise RuntimeError(message)


old = load(OLD)
execution = load(EXEC)
charge = load(CHARGE)
post = load(POST)
receipt = load(RECEIPT)
require(execution["run_id"] == RUN and execution["status"] == "STOP_PREFIX_RETAINED", "SOURCE_STATUS")
require(post["checks_failed"] == 0 and post["checks_total"] == post["checks_passed"] == 8, "SOURCE_POST")
require(post["execution_sha256"] == sha(EXEC) and post["external_charge_sha256"] == sha(CHARGE), "SOURCE_POST_HASH")
require(charge["execution_sha256"] == sha(EXEC) and charge["receipt_sha256"] == sha(RECEIPT), "SOURCE_CHARGE_LINKS")
require(charge["wall_s"] == 26.42207942299661 and charge["cpu_s"] == 25.113139, "SOURCE_CHARGE")
require(execution["counts"]["source_request_dispatched"] == 1, "SOURCE_DISPATCH")

row = {
    "run_id": RUN,
    "execution": str(EXEC.relative_to(ROOT)),
    "execution_sha256": sha(EXEC),
    "source_commit": execution["source_commit"],
    "status": execution["status"],
    "classification": execution["classification"],
    "engineering_only": False,
    "wall_s": execution["wall_s"],
    "cpu_s": execution["cpu_s"],
    "counts": execution["counts"],
    "authorization_budget_id": None,
    "formal_planning_calls": 0,
    "formal_table_I_calls": 0,
    "new_VI_candidate_constructions": 0,
    "charged_wall_s": charge["wall_s"],
    "charged_cpu_s": charge["cpu_s"],
    "charge_basis": charge["charge_basis"],
    "monotonic_envelope": charge["monotonic_envelope_components"],
    "external_charge": str(CHARGE.relative_to(ROOT)),
    "external_charge_sha256": sha(CHARGE),
    "internal_receipt": str(RECEIPT.relative_to(ROOT)),
    "internal_receipt_sha256": sha(RECEIPT),
    "external_post": str(POST.relative_to(ROOT)),
    "external_post_sha256": sha(POST),
    "external_time": str(TIME.relative_to(ROOT)),
    "external_time_sha256": sha(TIME),
    "external_metadata": str(META.relative_to(ROOT)),
    "external_metadata_sha256": sha(META),
    "external_stderr": str(STDERR.relative_to(ROOT)),
    "external_stderr_sha256": sha(STDERR),
    "execution_cap_breach": charge["execution_cap_breach"],
    "source_process_calls": 1,
    "source_request_dispatches": 1,
    "source_solved_stdout_observed": True,
    "source_result_json_present": False,
    "source_transport_qualified": False,
    "independent_path_qualified": False,
    "continuous_collision_certificate": False,
    "scientific_calls": 1,
    "source_failure_post": True,
}

rows = old["executions"] + [row]
require(len(rows) == 60 and row["execution"] not in {item["execution"] for item in old["executions"]}, "ROW_COUNT")
execution_rows = {
    str(path.relative_to(ROOT)): sha(path)
    for path in (ROOT / "results/p4_full").glob("*_R2_*/execution.json")
}
require(execution_rows == {item["execution"]: item["execution_sha256"] for item in rows}, "ALL_EXECUTIONS_COVERED")

charged_wall = math.fsum(item.get("charged_wall_s", item["wall_s"]) for item in rows)
charged_cpu = math.fsum(item.get("charged_cpu_s", item["cpu_s"]) for item in rows)
science = [item for item in rows if not item["engineering_only"]]
engineering = [item for item in rows if item["engineering_only"]]

new = copy.deepcopy(old)
new.update(
    {
        "schema": "P4_R2_RECOVERY_ACTUAL_LEDGER_V43",
        "previous_snapshot": str(OLD.relative_to(ROOT)),
        "previous_snapshot_sha256": sha(OLD),
        "executions": rows,
        "count": 60,
        "science_count": len(science),
        "engineering_count": len(engineering),
        "actual_runtime_execution_records_excluding_saved_only_recovery": old["actual_runtime_execution_records_excluding_saved_only_recovery"] + 1,
        "science_wall_s": math.fsum(item.get("charged_wall_s", item["wall_s"]) for item in science),
        "science_cpu_s": math.fsum(item.get("charged_cpu_s", item["cpu_s"]) for item in science),
        "engineering_wall_s": math.fsum(item.get("charged_wall_s", item["wall_s"]) for item in engineering),
        "engineering_cpu_s": math.fsum(item.get("charged_cpu_s", item["cpu_s"]) for item in engineering),
        "conservative_r2_sum_wall_s": charged_wall,
        "conservative_r2_sum_cpu_s": charged_cpu,
        "r2_remaining": {"wall_s": old["r2_caps"]["wall_s"] - charged_wall, "cpu_s": old["r2_caps"]["cpu_s"] - charged_cpu},
        "last_actual_execution": row,
        "new_scientific_calls": 1,
        "new_qualification_planner_solves_in_this_snapshot": 1,
        "previous_snapshot_qualification_planner_solves": old.get("total_qualification_planner_solves", 7),
        "total_qualification_planner_solves": old.get("total_qualification_planner_solves", 7) + 1,
        "scope": "D080 I-V retained; V4 engineering build and V SOURCE01 single source solve failure appended once. No formal statistics, VI work, or independent path qualification.",
        "ledger_correction": {
            "kind": "APPEND_INDEPENDENTLY_AUDITED_V_SOURCE01_FAILURE",
            "previous_snapshot": str(OLD.relative_to(ROOT)),
            "execution_sha256": sha(EXEC),
            "post_sha256": sha(POST),
            "source_process_calls": 1,
            "source_request_dispatches": 1,
            "source_result_json_present": False,
            "formal_table_I_calls": 0,
            "new_VI_candidate_constructions": 0,
            "status": "STOP_PREFIX_RETAINED",
        },
    }
)

accounting = copy.deepcopy(old["authoritative_source_solve_accounting"])
accounting["previous_snapshot"] = str(OLD.relative_to(ROOT))
accounting["previous_snapshot_sha256"] = sha(OLD)
accounting["previous_actual_source_solve_dispatches"] = old["authoritative_source_solve_accounting"]["total_actual_source_solve_dispatches"]
accounting["new_actual_source_solve_dispatches"] = 1
accounting["total_actual_source_solve_dispatches"] = accounting["previous_actual_source_solve_dispatches"] + 1
accounting["executions_enumerated"] = len(accounting["actual_source_solve_dispatches_by_execution"]) + 1
accounting["actual_source_solve_dispatches_by_execution"].append(
    {
        "run_id": RUN,
        "execution": str(EXEC.relative_to(ROOT)),
        "execution_sha256": sha(EXEC),
        "status": execution["status"],
        "saved_dispatch_fields": {
            "counts.source_process_started": execution["counts"]["source_process_started"],
            "counts.source_request_dispatched": execution["counts"]["source_request_dispatched"],
            "source_solved_stdout_observed": True,
        },
        "actual_source_solve_dispatches": 1,
        "count_basis": "SAVED_ACTUAL_SOURCE_REQUEST_DISPATCHED_BEFORE_TRACE_REAP",
        "new_since_previous_snapshot": True,
    }
)
accounting["ledger_generation_new_source_solve_dispatches"] = 1
new["authoritative_source_solve_accounting"] = accounting

NEW.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"ledger": str(NEW.relative_to(ROOT)), "sha256": sha(NEW), "count": len(rows), "science_count": len(science), "engineering_count": len(engineering), "wall_s": charged_wall, "cpu_s": charged_cpu, "source_dispatches": accounting["total_actual_source_solve_dispatches"]}, ensure_ascii=False))
