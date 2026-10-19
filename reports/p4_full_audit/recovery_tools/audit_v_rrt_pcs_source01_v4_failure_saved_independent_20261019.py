#!/usr/bin/env python3
"""Saved-only independent POST for the retained V SOURCE01 failure.

This auditor does not import the robot model, launch the planner, or inspect a
candidate as a qualified path.  It verifies the immutable transport/cost
boundary and records that the source emitted ``Solved`` before the external
supervisor stopped the incomplete trace/reconstruction prefix.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
RUN = "20261019_R2_D080_V_RRT_PCS_SOURCE01_V4"
RUN_DIR = ROOT / "results/p4_full" / RUN
EXEC = RUN_DIR / "execution.json"
PROTOCOL = ROOT / "configs/p4_d080/v_rrt_pcs_source01_v4.json"
CLAIM = ROOT / "results/p4_full/P4_D080_V_RRT_PCS_SOURCE01_V4_A02_SEED7_30W60CPU_20261019.claim.json"
RECEIPT = RUN_DIR / "cost_receipt.json"
EXT_CHARGE = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4.supervision.charge.json"
EXT_TIME = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4.supervision.time.txt"
EXT_META = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4.supervision.jsonl"
EXT_STDERR = ROOT / "results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4.supervision.stderr.log"
STDOUT = RUN_DIR / "process0_stdout.bin"
MILESTONES = RUN_DIR / "runtime/paths/path_milestones.txt"
TEMP = RUN_DIR / "runtime/paths/temp.txt"
POST = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_V4_FAILURE_SAVED_INDEPENDENT_POST_20261019.json"

checks = []
retained = {}


def digest(path: Path) -> str:
    data = path.read_bytes()
    value = hashlib.sha256(data).hexdigest()
    retained[str(path.relative_to(ROOT))] = value
    return value


def load(path: Path):
    return json.loads(path.read_text())


def check(name: str, passed: bool, evidence=None):
    row = {"name": name, "passed": bool(passed)}
    if evidence is not None:
        row["evidence"] = evidence
    checks.append(row)


execution = load(EXEC)
protocol = load(PROTOCOL)
claim = load(CLAIM)
receipt = load(RECEIPT)
charge = load(EXT_CHARGE)
time_fields = EXT_TIME.read_text().split()
stdout = STDOUT.read_bytes()

check(
    "immutable_execution_protocol_claim_identity",
    execution["schema"] == "P4_D080_V_RRT_PCS_SOURCE01_EXECUTION_V1"
    and execution["run_id"] == RUN
    and execution["status"] == "STOP_PREFIX_RETAINED"
    and execution["protocol"] == str(PROTOCOL.relative_to(ROOT))
    and execution["protocol_sha256"] == digest(PROTOCOL)
    and execution["claim"] == str(CLAIM.relative_to(ROOT))
    and execution["claim_sha256"] == digest(CLAIM)
    and claim["run_id"] == RUN
    and claim["protocol_sha256"] == digest(PROTOCOL)
    and claim["no_retry_reset_resume"] is True,
)
check(
    "frozen_source_boundary_and_zero_formal_or_vi_calls",
    execution["classification"]
    == "CORRECTED_COMAU_APC_ALIGNED_V3_RECONSTRUCTED_A02_ORIGINAL_RRT_CONTROL"
    and execution["independent_path_qualified"] is False
    and execution["continuous_collision_certificate"] is False
    and execution["formal_table_I_calls"] == 0
    and execution["new_VI_candidate_constructions"] == 0
    and execution["new_independent_model_calls"] == 0
    and execution["source_actual_internal_call_starts"] == "UNOBSERVED"
    and execution["source_FK_IK_PQP_started"] == "UNOBSERVED_NO_START_HOOK",
)
check(
    "one_real_source_process_and_request_no_retry",
    execution["binary_execution_calls"] == 1
    and execution["counts"] == {
        "source_process_start_attempted": 1,
        "source_process_started": 1,
        "source_request_dispatch_attempted": 1,
        "source_request_dispatched": 1,
    }
    and len(execution["source_process_registry"]) == 1
    and execution["source_process_registry"][0]["returncode"] == -9
    and execution["source_process_registry"][0]["actual_group_after_cleanup"] == []
    and execution["source_process_registry"][0]["pipe_EOF_observed"] == {"stdout": True, "stderr": True}
    and execution["source_process_registry"][0]["request_bytes"]
    == execution["source_process_registry"][0]["request_sent"] == 1092
    and execution["source_process_registry"][0]["stdin_closed_after_request"] is True,
)
check(
    "termination_is_trace_reconstruction_budget_failure",
    execution["termination_reason"] == "RuntimeError('III_SOURCE_SELF_REAPED_LIVE_GROUP_WORK_CAP')"
    and execution["external_supervision_qualified"] is False
    and receipt["status"] == "STOP_PREFIX_RETAINED"
    and receipt["external_supervision_qualified"] is False,
)
check(
    "stdout_retains_real_solved_observation_without_source_result",
    b"Solved in " in stdout
    and not (RUN_DIR / "parsed_source_result.json").exists()
    and not (RUN_DIR / "runtime/result.json").exists()
    and execution["source_reported_solve_calls"] is None
    and execution["solve_calls_from_result"] is None
    and execution.get("source_result_sha256") is None,
    {"stdout": stdout.decode(errors="replace"), "source_solve_observed": True},
)
check(
    "external_charge_receipt_time_and_cap_boundary",
    digest(EXEC) == charge["execution_sha256"]
    and digest(RECEIPT) == charge["receipt_sha256"]
    and digest(EXT_TIME) == charge["time_sha256"]
    and digest(EXT_META) == charge["metadata_sha256"]
    and digest(EXT_STDERR) == charge["stderr_sha256"]
    and charge["time_fields"] == time_fields
    and charge["time_returncode"] == charge["measured_child_exit"] == 1
    and charge["timing_valid"] is True
    and charge["monotonic_envelope_valid"] is True
    and charge["wall_CPU_caps_pass"] is True
    and charge["completed_process_exit0"] is False
    and charge["external_supervision_qualified"] is False
    and charge["wall_s"] == 26.42207942299661
    and charge["cpu_s"] == 25.113139,
)
check(
    "source_prefix_files_are_retained_and_have_six_declared_milestones",
    MILESTONES.exists()
    and TEMP.exists()
    and len(MILESTONES.read_text().splitlines()) == 7
    and int(MILESTONES.read_text().splitlines()[0]) == 6
    and len(TEMP.read_text().splitlines()) == 53,
    {"path_milestones": str(MILESTONES.relative_to(ROOT)), "temp": str(TEMP.relative_to(ROOT))},
)
check(
    "candidate_prefix_never_promoted_to_complete_path",
    execution["status"] == "STOP_PREFIX_RETAINED"
    and execution["independent_path_qualified"] is False
    and execution["continuous_collision_certificate"] is False
    and execution["source_implementation"].startswith("RECONSTRUCTED_"),
)

for path in (EXEC, PROTOCOL, CLAIM, RECEIPT, EXT_CHARGE, EXT_TIME, EXT_META, EXT_STDERR, STDOUT, MILESTONES, TEMP):
    digest(path)

failed = [row for row in checks if not row["passed"]]
report = {
    "schema": "P4_D080_V_RRT_PCS_SOURCE01_V4_FAILURE_SAVED_INDEPENDENT_POST_V1",
    "personnel_independent": True,
    "status": "FAIL_SOURCE_TRACE_RECONSTRUCTION_PREFIX_RETAINED" if not failed else "FAIL_SAVED_POST_AUDIT",
    "checks_total": len(checks),
    "checks_passed": len(checks) - len(failed),
    "checks_failed": len(failed),
    "checks": checks,
    "failures": failed,
    "external_supervision_qualified": False,
    "external_timing_qualified": charge["timing_valid"],
    "external_cost_qualified": charge["monotonic_envelope_valid"] and charge["wall_CPU_caps_pass"],
    "source_transport_qualified": False,
    "source_solved_stdout_observed": True,
    "source_exact": None,
    "source_approximate": None,
    "independent_path_qualified": False,
    "continuous_collision_certificate": False,
    "termination_reason": execution["termination_reason"],
    "execution": str(EXEC.relative_to(ROOT)),
    "execution_sha256": digest(EXEC),
    "protocol": str(PROTOCOL.relative_to(ROOT)),
    "protocol_sha256": digest(PROTOCOL),
    "claim": str(CLAIM.relative_to(ROOT)),
    "claim_sha256": digest(CLAIM),
    "external_charge": str(EXT_CHARGE.relative_to(ROOT)),
    "external_charge_sha256": digest(EXT_CHARGE),
    "internal_receipt": str(RECEIPT.relative_to(ROOT)),
    "internal_receipt_sha256": digest(RECEIPT),
    "external_time": str(EXT_TIME.relative_to(ROOT)),
    "external_time_sha256": digest(EXT_TIME),
    "external_metadata": str(EXT_META.relative_to(ROOT)),
    "external_metadata_sha256": digest(EXT_META),
    "external_stderr": str(EXT_STDERR.relative_to(ROOT)),
    "external_stderr_sha256": digest(EXT_STDERR),
    "charged_wall_s": charge["wall_s"],
    "charged_cpu_s": charge["cpu_s"],
    "charge_basis": charge["charge_basis"],
    "source_process_started": execution["counts"]["source_process_started"],
    "source_request_dispatched": execution["counts"]["source_request_dispatched"],
    "source_result_json_present": False,
    "source_prefix_path_milestones": 6,
    "retained_sha256": retained,
    "limits": [
        "The stdout Solved line is an observation only; no source result JSON or complete trace was transported.",
        "The six milestone file is a source-failure prefix candidate and was not independently path-qualified here.",
        "The exact source solve and process budget are consumed; no retry, changed seed, or resume is permitted.",
        "Independent physical candidate review is a separate saved-input audit and cannot alter this failure POST.",
    ],
}
POST.open("w").write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ("status", "checks_total", "checks_passed", "checks_failed", "charged_wall_s", "charged_cpu_s")}, ensure_ascii=False))
