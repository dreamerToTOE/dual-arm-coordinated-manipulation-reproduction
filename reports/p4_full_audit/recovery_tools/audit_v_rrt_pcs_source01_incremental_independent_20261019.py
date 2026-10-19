#!/usr/bin/env python3
"""Thin independent static audit for the V RRT+PCS SOURCE01 draft.

This audit does not import the candidate runner, compile, launch an ELF, load
the model, or consume a scientific budget.  The V driver/observer and the
preflight helper are covered only by their already independent certificates;
this audit checks that the new SOURCE entry binds those certificates without
silently changing their scope.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / "scripts/p4_d080/qualify_v_rrt_pcs_source01_v1_draft.py"
SUPERVISOR = ROOT / "scripts/p4_d080/supervise_v_rrt_pcs_source01_v1_draft.py"
CONFIG = ROOT / "configs/p4_d080/v_rrt_pcs_source01_v1.DRAFT.json"
PRE = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_PRE_DRAFT_20261018.md"
DRIVER_REVIEW = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_20261018.json"
HELPER_REVIEW = ROOT / "reports/P4_D080_PREFLIGHT_RECOVERY_CHAIN_THIN_INDEPENDENT_PRE_ADDENDUM_20261018.json"
SELF_ADDENDUM = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_EXECUTOR_SELF_STATIC_ADDENDUM_20261018.json"
ENDPOINT_DIR = ROOT / "results/p4_full/20261015_R2_ENDPOINT_COLLISION_REPLAY01"

RUN = "20261018_R2_D080_V_RRT_PCS_SOURCE01"
CLAIM = "P4_D080_V_RRT_PCS_SOURCE01_A02_SEED7_30W60CPU_20261018"
RUNNER_SHA = "b0391ce045ddb98e85755c12acc1b14a1729a22efa1fed82f63546b0fdd15544"
SUPERVISOR_SHA = "b6dfca4b0475e6635bb6d383a40b3d82ebd5c01084a62bd18cedb5fe488b0279"
CONFIG_SHA = "d7a28dc43da59e90c53f38bac97d72df4398d60c65322120efc3a4e3eb4f6d4d"
PRE_SHA = "4302a8c40e8bf6399bfd0c4887b5789899a0ff76a67bceced66384dad084ec2e"
DRIVER_CERT_SHA = "d5f05c246a2a7cfafc5183e3166bde9bd2ce47ab42d3da9dd43b3df72ac1f858"
HELPER_CERT_SHA = "17e47992e46e1b9ae0eee6242c71edda90e3e0ce559332e867ce1ceed728cba3"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(checks: list[dict], name: str, passed: bool, evidence: object = None) -> None:
    row = {"name": name, "passed": bool(passed)}
    if evidence is not None:
        row["evidence"] = evidence
    checks.append(row)


def top_level_forbidden_call(path: Path) -> bool:
    tree = ast.parse(path.read_text())
    forbidden = {"run", "Popen", "check_output", "check_call", "call", "execute"}
    return any(
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute)
        and node.value.func.attr in forbidden
        for node in tree.body
    )


def main() -> None:
    spec = json.loads(CONFIG.read_text())
    checks: list[dict] = []

    check(checks, "new runner/supervisor/config/PRE exact reviewed identities", all([
        digest(RUNNER) == RUNNER_SHA,
        digest(SUPERVISOR) == SUPERVISOR_SHA,
        digest(CONFIG) == CONFIG_SHA,
        digest(PRE) == PRE_SHA,
    ]))
    check(checks, "candidate runner and supervisor parse with no import-time process call",
          ast.parse(RUNNER.read_text()).__class__ is ast.Module
          and ast.parse(SUPERVISOR.read_text()).__class__ is ast.Module
          and not top_level_forbidden_call(RUNNER)
          and not top_level_forbidden_call(SUPERVISOR))
    check(checks, "DRAFT remains unfreezed and all three review approvals are false",
          spec["status"].startswith("DRAFT_")
          and all(spec[k] is False for k in ("frozen", "scientific_execution_authorized",
                                               "independent_review_passed", "formal_execution_authorized"))
          and all(v is False for v in spec["reviews"].values()))
    check(checks, "V/A02 identity and source-only boundary are exact",
          spec["environment"] == "V" and spec["run_id"] == RUN and spec["claim_id"] == CLAIM
          and spec["method"] == "PCS" and spec["planner"] == "RRT"
          and spec["source_qualification_only"] is True
          and spec["independent_path_qualified"] is False
          and "SOURCE_EXACT" in spec["source_vs_physical_boundary"])
    request = spec["request"]
    cap_names = {"public_request", "project_fixed", "identify", "is_valid_rbs", "rbs",
                 "reconstruct", "native_fk", "native_ik", "specific_ik", "limits",
                 "collision", "pqp", "mesh_load", "records"}
    check(checks, "A02 seed/range/goal bias/solve and all fourteen caps are frozen",
          request["seed"] == 7 and request["range_rad"] == 0.2 and request["goal_bias"] == 0.05
          and request["solve_seconds"] == 10.0
          and set(request["caps"]) == cap_names
          and all(type(v) is int and v == 1_000_000 for v in request["caps"].values())
          and spec["source_process_limit"] == spec["source_solve_limit"] == 1
          and spec["cap_reached_action"] == "FAIL_RETAIN_PREFIX_NO_RETRY")
    check(checks, "original restricted V sampler bounds are retained", request["bounds_low_rad"] ==
          [-3.1416, -1.0472, -3.1416 / 2, -3.1416, -2.0944, -3.1416] * 2
          and request["bounds_high_rad"] ==
          [3.1416, 2.1871, 1.3090, 3.1416, 2.0944, 3.1416] * 2)
    expected = {
        "start": "f906a6b61999c71efe15c8d86188edbded704d66dcba18f9833d940ccfa6c405",
        "goal": "feae5fd78837327db9c83d66621e2aa4fc9eec72a46c0d0dfc1e98cbc9d88737",
    }
    endpoint_ok = True
    for role, expected_sha in expected.items():
        endpoint = ENDPOINT_DIR / f"V_{role}.json"
        row = json.loads(endpoint.read_text())
        endpoint_ok &= digest(endpoint) == expected_sha
        endpoint_ok &= request[f"{role}_q12"] == row["selected_q_rad"]
        endpoint_ok &= row["status"] == "RECONSTRUCTED_SOURCE_POLICY_QUALIFIED"
        endpoint_ok &= row["environment"] == "V" and row["classification"] == "RECONSTRUCTED"
        endpoint_ok &= row["active_coordinates_exactly_unchanged"] is True
        endpoint_ok &= row["collision"]["selected_variant"] == "aligned"
        endpoint_ok &= row["collision"]["collision"] is False
    check(checks, "saved A02 RECONSTRUCTED endpoints and aligned collision gates are exact", endpoint_ok)
    check(checks, "outer/work budgets and no new model/path claim are retained",
          spec["budget"] == {"wall_s": 30, "cpu_s": 60}
          and spec["working_budget"] == {"wall_s": 25, "cpu_s": 50}
          and spec["new_independent_model_calls"] == 0
          and spec["formal_table_I_calls"] == 0)
    check(checks, "D080 VI and formal statistics remain out of this draft",
          spec["VI_future_science_authorized"] is False
          and spec["formal_table_I_D080_required"] == 18_000
          and spec["formal_execution_authorized"] is False)
    bound_ok = all(Path(name).is_file() and digest(Path(name)) == value
                   for name, value in spec["bound_files_sha256"].items())
    check(checks, "all currently bound source/evidence/dependency bytes match their hashes", bound_ok,
          {"bound_count": len(spec["bound_files_sha256"])})
    check(checks, "BUILD02/ELF/independent POST/latest prior are explicit pending bindings",
          spec["target"]["binary_sha256"] is None
          and all(spec["build_assets"][key] is None for key in ("execution_sha256", "post_sha256", "post_checks_total"))
          and spec["actual_charge_prior"] is None
          and all(spec["prior"][key] is None for key in ("ledger", "ledger_sha256", "wall_s", "cpu_s")))
    check(checks, "new entry calls the reviewed prior helper with run-local identity",
          "validate_prior(spec, RUN, ROOT / 'results/p4_full' / RUN)" in RUNNER.read_text()
          and spec["prior_validator_helper"]["sha256"] == "b315972ce22569684c4fe21dc487fc0456b7db63b8224906020d6fc41911f65e")
    helper = json.loads(HELPER_REVIEW.read_text())
    check(checks, "prior helper certificate is reused without re-audit", digest(HELPER_REVIEW) == HELPER_CERT_SHA
          and helper["personnel_independent"] is True
          and helper["checks_total"] == helper["checks_passed"] == 11
          and helper["new_scientific_compile_binary_model_calls"] == 0)
    driver = json.loads(DRIVER_REVIEW.read_text())
    check(checks, "V driver/observer independent 20/20 seam certificate is reused", digest(DRIVER_REVIEW) == DRIVER_CERT_SHA
          and driver["personnel_independent"] is True
          and driver["checks_total"] == driver["checks_passed"] == 20
          and driver["new_compile_calls"] == driver["new_binary_calls"] == driver["new_model_calls"] == driver["new_scientific_calls"] == 0)
    self_addendum = json.loads(SELF_ADDENDUM.read_text())
    check(checks, "executor self-review remains provenance only, not independent evidence",
          self_addendum["personnel_independent"] is False
          and self_addendum["status"] == "PASS_SELF_ONLY_NOT_INDEPENDENT_NOT_FROZEN")
    source = RUNNER.read_text()
    inherited_transport = (ROOT / "scripts/p4_d080/qualify_iii_rrt_pcs_source01_v1_draft.py").read_text()
    check(checks, "source result remains exact/approximate/path/CCD/trace qualified false",
          all(fragment in (source + inherited_transport) for fragment in (
              "result['independent_path_qualified'] is False",
              "result['full_physical_geometry_or_CCD_qualified'] is False",
              "result['full_solve_plain_trace_consistency_qualified'] is False",
              "result['source_observation_trace_mode'] == 1")))
    check(checks, "single compact request, EOF, raw stdout/result equality and post-return logs are guarded",
          all(fragment in (source + inherited_transport) for fragment in (
              "len(raw) < 4096", "self.proc.stdin.close()", "WHOLE_MIXED_STDOUT_MUST_REMAIN_RETAINED",
              "RESULT_FILE_AND_FINAL_STDOUT_OBJECT_MUST_AGREE", "COMPLETE_DISTINCT_V_OBSERVER_LIFETIMES_REQUIRED",
              "V_ENTIRE_TRACE_ENTRY_AND_COMPLETION_AGREES_WITH_RESULT_NO_CAP_NO_TRUNCATION")))
    check(checks, "real worker cleanup, dual EOF, no retry and raw evidence persistence are guarded",
          all(fragment in source for fragment in (
              "FRESH_SINGLE_V_SOURCE_NO_OTHER_P4_OR_D080", "ALL_REAL_WORKERS_REAPED_EMPTY_DUAL_EOF_REQUIRED",
              "no_retry_reset_resume", "raw_evidence_persistence", "L.durable_new(folder / 'cost_receipt.json', receipt)")))
    supervisor = SUPERVISOR.read_text()
    check(checks, "supervisor uses exclusive timing inode and one child with no retry",
          all(fragment in supervisor for fragment in (
              "os.O_WRONLY|os.O_CREAT|os.O_EXCL", "proc=subprocess.Popen", "proc.wait()",
              "This supervisor never starts a second time/runner after a failure.",
              "external_supervision_qualified=False")))
    check(checks, "no run directory or claim has been created by this static review",
          not (ROOT / "results/p4_full" / RUN).exists()
          and not (ROOT / "results/p4_full" / (CLAIM + ".claim.json")).exists())

    result = {
        "schema": "P4_D080_V_RRT_PCS_SOURCE01_INCREMENTAL_INDEPENDENT_PRE_V1",
        "personnel_independent": True,
        "status": "PASS_THIN_SOURCE_ENTRY_PRE_ONLY" if all(row["passed"] for row in checks) else "FAIL_RETAINED",
        "checks_total": len(checks),
        "checks_passed": sum(row["passed"] for row in checks),
        "checks_failed": sum(not row["passed"] for row in checks),
        "checks": checks,
        "input_sha256": {
            str(path.relative_to(ROOT)): digest(path)
            for path in (RUNNER, SUPERVISOR, CONFIG, PRE, DRIVER_REVIEW, HELPER_REVIEW, SELF_ADDENDUM)
        },
        "reused_independent_evidence": {
            "V_driver_observer": str(DRIVER_REVIEW.relative_to(ROOT)),
            "V_driver_observer_sha256": DRIVER_CERT_SHA,
            "preflight_recovery_helper": str(HELPER_REVIEW.relative_to(ROOT)),
            "preflight_recovery_helper_sha256": HELPER_CERT_SHA,
        },
        "scope": {
            "new_incremental_review": ["V SOURCE runner", "V SOURCE supervisor", "V SOURCE DRAFT/PRE seams"],
            "reused_without_reaudit": ["V driver/observer", "preflight recovery helper", "III audited transport"],
            "excluded": ["BUILD02", "ELF", "actual source execution", "independent path qualification", "formal statistics"],
        },
        "limits": [
            "Static PRE only; all three freeze/review flags remain false.",
            "Actual BUILD02 execution, ELF and independent POST must be bound by root before freeze.",
            "Latest charged prior must be independently validated and bound by root before freeze.",
            "A source exact result would remain only a candidate until separate full path audit.",
        ],
    }
    out = ROOT / "reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_INCREMENTAL_INDEPENDENT_PRE_20261019.json"
    if out.exists():
        raise FileExistsError(out)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks_passed": result["checks_passed"],
                      "checks_total": result["checks_total"], "checks_failed": result["checks_failed"],
                      "sha256": digest(out)}))


if __name__ == "__main__":
    main()
