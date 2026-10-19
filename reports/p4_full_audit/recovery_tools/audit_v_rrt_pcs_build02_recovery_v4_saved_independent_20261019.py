#!/usr/bin/env python3
"""Read-only independent POST audit for the V RRT+PCS BUILD02 V4 recovery.

This auditor only reads saved execution, supervision sidecars, build artifacts,
and frozen protocol inputs.  It does not execute the ELF, rebuild anything,
or modify historical evidence.  The generated JSON is intentionally a
saved-only engineering certificate; it does not qualify source planning or a
path.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
RUN_ID = "20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY_V4"
RUN = REPO / "results" / "p4_full" / RUN_ID
STAGE = Path("/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_rrt_pcs_e2e_v4")
EXECUTION = RUN / "execution.json"
CLAIM = RUN / "claim.json"
RECEIPT = RUN / "cost_receipt.json"
CHARGE = REPO / "results" / "p4_full" / f"{RUN_ID}.supervision.charge.json"
TIME = REPO / "results" / "p4_full" / f"{RUN_ID}.supervision.time.txt"
META = REPO / "results" / "p4_full" / f"{RUN_ID}.supervision.jsonl"
STDERR = REPO / "results" / "p4_full" / f"{RUN_ID}.supervision.stderr.log"
PROTOCOL = REPO / "configs/p4_d080/v_rrt_pcs_e2e_build_v4.json"
PRIOR = REPO / "results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V41.json"
PRIOR_AUDIT = REPO / "reports/P4_D080_PRIOR_VALIDATOR_V3_V41_INDEPENDENT_AUDIT_20261019.json"
PRE = REPO / "reports/P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_THIN_INCREMENTAL_INDEPENDENT_PRE_V4_20261019.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(checks: list[dict], name: str, passed: bool, evidence=None) -> None:
    checks.append({"name": name, "passed": bool(passed), "evidence": evidence})


def main() -> int:
    execution = json.loads(EXECUTION.read_text())
    claim = json.loads(CLAIM.read_text())
    receipt = json.loads(RECEIPT.read_text())
    charge = json.loads(CHARGE.read_text())
    target = execution["targets"][0]
    checks: list[dict] = []

    check(checks, "execution_exists_and_BUILT_NOT_QUERIED", execution["status"] == "BUILT_NOT_QUERIED")
    check(checks, "claim_execution_run_identity_bound", claim["run_id"] == RUN_ID == execution["run_id"])
    check(checks, "claim_and_protocol_hashes_unchanged_after_run",
          execution["claim_sha256"] == execution["claim_after_sha256"]
          and execution["protocol_sha256"] == execution["protocol_after_sha256"]
          and execution["protocol_sha256"] == sha(PROTOCOL))
    check(checks, "V4_pre_review_and_prior_audit_bind",
          sha(PRE) == "fd8ab420d4c506f7cc4cc5ff3f9a203fe01d54d41e0ffb97c2f1c72039597ff2"
          and sha(PRIOR_AUDIT) == "a5f5a8ee1185851309700ec0f69781a74e392c0145627f81fcb1683cfc3f7efd")
    check(checks, "external_sidecar_file_hashes_exact",
          sha(EXECUTION) == charge["execution_sha256"]
          and sha(RECEIPT) == charge["receipt_sha256"]
          and sha(TIME) == charge["time_sha256"]
          and sha(META) == charge["metadata_sha256"]
          and sha(STDERR) == charge["stderr_sha256"])
    time_fields = TIME.read_text().strip().split()
    check(checks, "GNUtime_four_fields_exit_zero_and_caps_pass",
          len(time_fields) == 4 and time_fields[-1] == "0"
          and charge["completed_process_exit0"] is True
          and charge["timing_valid"] is True
          and charge["wall_CPU_caps_pass"] is True,
          {"time_fields": time_fields, "charged_wall_s": charge["wall_s"], "charged_cpu_s": charge["cpu_s"]})
    meta = [json.loads(line) for line in META.read_text().splitlines() if line.strip()]
    events = [m.get("event") for m in meta]
    check(checks, "external_metadata_launch_start_reap_complete",
          events == ["planned_launch", "time_process_started", "time_process_reaped"]
          and meta[-1].get("returncode") == 0)
    check(checks, "external_stderr_empty_and_supervisor_identity_bound",
          sha(STDERR) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
          and meta[0]["supervisor_source_sha256"] == "3312d8705fc27e7809d759aeda090f2f33e9da1e9b2af690110871049234975f"
          and meta[0]["runner_sha256"] == "94f4e87dcb43869dfa7d11195a13c232e3a6b93ab0c9af39f20602b40d6caffb")
    commands = target["commands"]
    check(checks, "exact_two_compile_one_link_successful",
          target["new_compile_calls"] == 2 and target["new_link_calls"] == 1
          and len(commands) == 3 and all(c["returncode"] == 0 for c in commands))
    check(checks, "compiler_logs_match_saved_execution_hashes",
          all(sha(Path(p)) == h for p, h in execution["compile_log_sha256"].items()))

    object_records = target["objects"]
    object_hash_ok = True
    object_types_ok = True
    for obj in object_records:
        path = Path(obj["object"])
        object_hash_ok &= path.exists() and sha(path) == obj["object_sha256"]
        object_types_ok &= "ELF 64-bit" in subprocess.check_output(["file", str(path)], text=True)
        object_types_ok &= "relocatable" in subprocess.check_output(["file", str(path)], text=True)
    check(checks, "two_new_objects_hash_and_relocatable_ELF", object_hash_ok and object_types_ok,
          [{"path": o["object"], "sha256": o["object_sha256"], "size_bytes": o["object_size_bytes"]} for o in object_records])
    binary = Path(target["binary"])
    file_text = subprocess.check_output(["file", str(binary)], text=True)
    check(checks, "linked_ELF_hash_and_type_exact",
          binary.exists() and sha(binary) == target["binary_sha256"]
          and "ELF 64-bit" in file_text and "executable" in file_text,
          {"binary": str(binary), "sha256": target["binary_sha256"], "file": file_text.strip()})
    check(checks, "staged_after_map_contains_sources_objects_and_binary",
          len(execution["staged_after_sha256"]) == 5
          and execution["staged_after_sha256"][str(binary)] == target["binary_sha256"])
    check(checks, "bound_file_map_unchanged_and_dependency_union_complete",
          execution["bound_files_sha256"] == execution["bound_files_after_sha256"]
          and len(execution["bound_files_after_sha256"]) == 952
          and len(execution["dependencies_after_sha256"]) == 659)
    check(checks, "zero_model_query_solve_rng_binary_and_formal_calls",
          execution["scientific_calls"] == 0 and execution["query_calls"] == 0
          and execution["solve_calls"] == 0 and execution["rng_calls"] == 0
          and execution["binary_execution_calls"] == 0
          and execution["formal_table_I_calls"] == 0
          and execution["new_VI_candidate_constructions"] == 0)
    check(checks, "target_status_and_engineering_classification_exact",
          target["status"] == "BUILT_NOT_QUERIED"
          and execution["classification"] == "ENGINEERING_BUILD_ONLY_V_RRT_PCS_2TU1LINK_ORIGINAL_RRT_CONTROL"
          and claim["engineering_only"] is True)
    check(checks, "V41_prior_hash_and_totals_frozen",
          execution["prior"]["path"] == "results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V41.json"
          and execution["prior"]["sha256"] == sha(PRIOR)
          and execution["prior"]["sha256"] == "ca08ec3c719ec201ca1ce4710652e2ad6a1e1bf0e3f641f0030c8f8c46d0b88a"
          and execution["prior"]["wall_s"] == 1157.5309649199733
          and execution["prior"]["cpu_s"] == 981.858415)
    check(checks, "internal_receipt_BUILT_NOT_QUERIED_and_no_auto_supervision_claim",
          receipt["status"] == "BUILT_NOT_QUERIED"
          and charge["external_supervision_qualified"] is False
          and charge["independent_POST_required"] is True)

    retained = {
        "execution": sha(EXECUTION),
        "claim": sha(CLAIM),
        "receipt": sha(RECEIPT),
        "charge": sha(CHARGE),
        "time": sha(TIME),
        "metadata": sha(META),
        "stderr": sha(STDERR),
        "protocol": sha(PROTOCOL),
        "prior": sha(PRIOR),
        "prior_audit": sha(PRIOR_AUDIT),
        "pre_review": sha(PRE),
        "runner": sha(REPO / "scripts/p4_d080/build_v_rrt_pcs_e2e_v4_draft.py"),
        "supervisor": sha(REPO / "scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v4_draft.py"),
        "object_0": sha(Path(object_records[0]["object"])),
        "object_1": sha(Path(object_records[1]["object"])),
        "binary": sha(binary),
    }
    report = {
        "schema": "P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_V4_SAVED_INDEPENDENT_POST_V1",
        "personnel_independent": True,
        "status": "PASS_BUILT_NOT_QUERIED_SAVED_ENGINEERING_POST" if all(c["passed"] for c in checks) else "FAIL_INDEPENDENT_POST",
        "checks_total": len(checks),
        "checks_passed": sum(c["passed"] for c in checks),
        "checks_failed": sum(not c["passed"] for c in checks),
        "checks": checks,
        "engineering_build_qualified": all(c["passed"] for c in checks),
        "external_supervision_qualified": all(c["passed"] for c in checks),
        "external_timing_qualified": all(c["passed"] for c in checks),
        "external_cost_qualified": all(c["passed"] for c in checks),
        "source_planning_qualified": False,
        "independent_path_qualified": False,
        "run_id": RUN_ID,
        "environment": "V",
        "execution": str(EXECUTION.relative_to(REPO)),
        "execution_sha256": sha(EXECUTION),
        "claim": str(CLAIM.relative_to(REPO)),
        "claim_sha256": sha(CLAIM),
        "protocol": str(PROTOCOL.relative_to(REPO)),
        "protocol_sha256": sha(PROTOCOL),
        "external_charge": str(CHARGE.relative_to(REPO)),
        "external_charge_sha256": sha(CHARGE),
        "external_time": str(TIME.relative_to(REPO)),
        "external_time_sha256": sha(TIME),
        "external_metadata": str(META.relative_to(REPO)),
        "external_metadata_sha256": sha(META),
        "external_stderr": str(STDERR.relative_to(REPO)),
        "external_stderr_sha256": sha(STDERR),
        "internal_receipt": str(RECEIPT.relative_to(REPO)),
        "internal_receipt_sha256": sha(RECEIPT),
        "new_compile_calls": target["new_compile_calls"],
        "new_link_calls": target["new_link_calls"],
        "upper_wall_s": charge["wall_s"],
        "upper_cpu_s": charge["cpu_s"],
        "charge_basis": charge["charge_basis"],
        "prior": {
            "path": str(PRIOR.relative_to(REPO)),
            "sha256": sha(PRIOR),
            "wall_s": execution["prior"]["wall_s"],
            "cpu_s": execution["prior"]["cpu_s"],
        },
        "post_charge_totals": {
            "wall_s": execution["prior"]["wall_s"] + charge["wall_s"],
            "cpu_s": execution["prior"]["cpu_s"] + charge["cpu_s"],
        },
        "binary": str(binary),
        "binary_sha256": sha(binary),
        "objects": [{"path": o["object"], "sha256": sha(Path(o["object"])), "size_bytes": o["object_size_bytes"]} for o in object_records],
        "retained_sha256": retained,
        "limitations": [
            "This POST independently upgrades the saved external supervision evidence boundary only; the raw sidecar remains marked external_supervision_qualified=false until POST.",
            "The run compiled two new translation units and linked one ELF, but did not execute the binary: BUILT_NOT_QUERIED.",
            "No source query, projection, local connection, planning, path reconstruction, collision replay, or formal Table-I call occurred.",
            "Source planning and independent path qualification remain false; SOURCE01 must use the frozen V4 ELF in a separate authorized run.",
            "V41 prior, V3 NameError failure, V2 prebind failure, and all old sidecars remain immutable and separately reported.",
        ],
    }
    out = REPO / "reports/P4_D080_ENV_V_RRT_PCS_BUILD02_RECOVERY_V4_SAVED_INDEPENDENT_POST_20261019.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(out)
    print(json.dumps({k: report[k] for k in ("status", "checks_total", "checks_passed", "checks_failed", "upper_wall_s", "upper_cpu_s", "post_charge_totals")}, ensure_ascii=False))
    return 0 if report["checks_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
