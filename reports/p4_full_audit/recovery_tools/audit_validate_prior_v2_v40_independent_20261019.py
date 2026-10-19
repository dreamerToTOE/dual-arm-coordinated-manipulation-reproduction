#!/usr/bin/env python3
"""Independent, read-only audit of the D080 prior-validator successor.

The audit intentionally does not import the successor as the source of truth
for its static checks.  It compares the frozen v1 source, checks the two
declared cost-only exceptions (III physical01 and the V BUILD02 prebind
failure), validates the current V40 ledger once, and reports missing digest or
zero-call bindings.  It never edits ledger, experiment, or source artifacts.
Use ``--output`` only to write a new audit report.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V1 = ROOT / "scripts/p4_d080/validate_prior_preflight_recovery_v1.py"
V2 = ROOT / "scripts/p4_d080/validate_prior_preflight_recovery_v2.py"
LEDGER = ROOT / "results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V40.json"
POST = ROOT / "reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json"
RUN = "20261018_R2_D080_III_RRT_PCS_PHYSICAL01"
COST_ONLY_RUN = RUN
POST_REL = "reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json"
V1_SHA = "b315972ce22569684c4fe21dc487fc0456b7db63b8224906020d6fc41911f65e"

# Immutable identities for the separately declared V BUILD02 prebind
# engineering failure.  These are deliberately literal rather than derived
# from the files under audit, so a changed artifact cannot silently redefine
# the exception it is meant to prove.
PREBIND_RUN = "20261018_R2_D080_V_RRT_PCS_BUILD02"
PREBIND_POST = "reports/P4_D080_ENV_V_RRT_PCS_BUILD02_FAILURE_SAVED_INDEPENDENT_POST_20261019.json"
PREBIND_EXECUTION = "results/p4_full/20261018_R2_D080_V_RRT_PCS_BUILD02/execution.json"
PREBIND_TIME = "results/p4_full/20261018_R2_D080_V_RRT_PCS_BUILD02.supervision.time.txt"
PREBIND_CHARGE = "results/p4_full/20261018_R2_D080_V_RRT_PCS_BUILD02.supervision.charge.json"
PREBIND_RECEIPT = "results/p4_full/20261018_R2_D080_V_RRT_PCS_BUILD02/cost_receipt.json"
PREBIND_EXECUTION_SHA = "adaef230b2c94f8afdca1d52565910ccecceafb0238c24f8a6cb02330bb2e74e"
PREBIND_POST_SHA = "21142d5023cb01b362a78c21fac2d73f0c0bb40523069174ec5fe319eb50c837"
PREBIND_TIME_SHA = "980c2a7b2ee104846ee4f62ad6bc4395458fbb4a81cfab0ebbd02c3a83ab422b"
PREBIND_CHARGE_SHA = "1761f1beaa78cac882ce2a1ac9bda9c342240a3cc27d5673326a3ecd75a1d271"
PREBIND_RECEIPT_SHA = "9261284104078611fb7e9a49cc40bc01e747d9b7cce998ec85de8a53399babc7"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_bytes())


def check(rows, name, passed, details=None):
    rows.append({"name": name, "passed": bool(passed), "details": details or {}})


def function_node(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise RuntimeError(f"function not found: {name}")


def string_constants(tree):
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, help="write a new JSON report; otherwise stdout only")
    args = ap.parse_args()
    rows = []
    errors = []

    check(rows, "v1_frozen_hash", V1.is_file() and sha(V1) == V1_SHA,
          {"expected": V1_SHA, "actual": sha(V1) if V1.is_file() else None})
    check(rows, "v2_exists_and_parses", V2.is_file(), {})
    if not V2.is_file():
        errors.append("missing v2")
        return finish(rows, errors, args.output)

    v1_src = V1.read_text()
    v2_src = V2.read_text()
    try:
        v1_tree = ast.parse(v1_src, filename=str(V1))
        v2_tree = ast.parse(v2_src, filename=str(V2))
        check(rows, "v2_ast_parse", True)
    except SyntaxError as exc:
        check(rows, "v2_ast_parse", False, {"error": repr(exc)})
        errors.append("v2 syntax error")
        return finish(rows, errors, args.output)

    v1_validate = function_node(v1_tree, "validate_prior")
    v2_validate = function_node(v2_tree, "validate_prior")
    v2_consts = string_constants(v2_tree)
    # These are the v1's ordinary gates.  Keeping the message predicates is a
    # conservative static check; the dynamic call below checks their current
    # saved behavior against V39.
    required_predicates = [
        "LATEST_VERSIONED_CHARGED_LEDGER_REQUIRED",
        "PRIOR_LEDGER_CHANGED",
        "PRIOR_LEDGER_MUST_COVER_EVERY_ACTUAL_EXECUTION",
        "PRIOR_EXTERNAL_POST_EXECUTION_TIMING_CERTIFICATE_REQUIRED",
        "PRIOR_HASHED_EXTERNAL_CHARGE_BINDING_REQUIRED",
        "PRIOR_INTERNAL_PERSISTENCE_RECEIPT_REQUIRED",
        "PRIOR_EXACT_FOUR_GNUTIME_FIELDS_REQUIRED",
        "PRIOR_FINITE_TIME_AND_EXACT_SAVED_EXIT_REQUIRED",
        "PRIOR_DECIMAL_UPPER_REPLACEMENT_ONCE_REQUIRED",
        "ONLY_IMMUTABLE_PATH01_OLD_RAW_CHARGE_EXCEPTION_ALLOWED",
        "FINITE_SAVED_OUTER_AND_RECEIPT_ENVELOPE_REQUIRED",
        "PRIOR_INDEPENDENT_EXACT_MONOTONIC_ENVELOPE_CERTIFICATE_REQUIRED",
        "NEW_ENVELOPE_CHARGE_MUST_SEPARATELY_RETAIN_RAW_TIME",
        "UNKNOWN_PRIOR_CHARGE_BASIS_NO_SILENT_FALLBACK",
        "UNACCOUNTED_SUPERVISED_ATTEMPT_",
        "EXACT_CURRENT_CHARGED_SUMS_REQUIRED",
        "NO_R2_TOTAL_BUDGET_INCREASE",
        "EXACT_FROZEN_CHARGED_PRIOR_REQUIRED",
        "RETAINED_UNKNOWN",
    ]
    missing = [s for s in required_predicates if s not in v2_consts and s not in v2_src]
    check(rows, "v1_ordinary_predicate_messages_retained", not missing, {"missing": missing})
    check(rows, "v1_recovered_preflight_delegation_retained",
          "V1.validate_recovered_preflight" in v2_src and "RECOVERED_BASIS" in v2_src)
    check(rows, "v1_helper_import_is_explicit", bool(re.search(r"^import validate_prior_preflight_recovery_v1 as V1$", v2_src, re.M)))

    # The exceptions must be two named, immutable runs with one declared cost
    # basis each.  A generic external_cost_qualified escape hatch is a
    # protocol failure.  Keep these checks source-level and independent from
    # the imported successor below.
    basis = "EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE"
    iii_exception_source = (
        "iii_exception=(row['run_id']==COST_ONLY_RUN and "
        "row['charge_basis']=='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE')"
    )
    prebind_exception_source = (
        "prebind_exception=(row['run_id']==PREBIND_RUN and "
        "row['charge_basis']=='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE')"
    )
    check(rows, "single_explicit_iii_exception", iii_exception_source in v2_src,
          {"run": COST_ONLY_RUN, "basis": basis})
    check(rows, "single_explicit_v_prebind_exception", prebind_exception_source in v2_src,
          {"run": PREBIND_RUN, "basis": basis})
    check(rows, "exceptions_are_explicitly_combined",
          "exception=iii_exception or prebind_exception" in v2_src)
    check(rows, "cost_only_no_supervision_upgrade", "post['external_supervision_qualified'] is False" in v2_src)
    generic_cost_branches = [
        line.strip()
        for line in v2_src.splitlines()
        if "external_cost_qualified" in line
        and "post[" not in line
        and "COST_ONLY" not in line
    ]
    check(rows, "no_generic_cost_only_escape_hatch", len(generic_cost_branches) == 0,
          {"suspicious_lines": generic_cost_branches})

    # These are intentionally strict.  Each exception must bind its POST path
    # and POST digest to the ledger row; the V branch also binds the literal
    # failure identity and zero-call prefix.
    check(rows, "iii_exception_binds_post_path_constant", "str(post_path.relative_to(ROOT))==COST_ONLY_POST" in v2_src)
    check(rows, "v_prebind_exception_binds_post_path_constant", "str(post_path.relative_to(ROOT))==PREBIND_POST" in v2_src)
    post_sha_patterns = [
        "sha(post_path)==row['external_post_sha256']",
        "row['external_post_sha256']==sha(post_path)",
    ]
    check(rows, "exceptions_bind_post_digest_to_ledger", any(p in v2_src for p in post_sha_patterns),
          {"required_one_of": post_sha_patterns})
    check(rows, "v_prebind_exception_binds_literal_post_digest",
          "row['external_post_sha256']==sha(post_path)==PREBIND_POST_SHA" in v2_src)
    check(rows, "v_prebind_exception_requires_zero_calls",
          "execution.get('compile_calls',0)==0" in v2_src
          and "execution.get('binary_execution_calls',0)==0" in v2_src
          and "execution.get('query_calls',0)==0" in v2_src
          and "execution.get('solve_calls',0)==0" in v2_src)
    check(rows, "exception_forces_external_timing_false", "post['external_timing_qualified'] is False" in v2_src)
    ledger_obj = load(LEDGER) if LEDGER.is_file() else None
    target_row = next((r for r in ledger_obj["executions"] if r.get("run_id") == RUN), None) if ledger_obj else None
    prebind_row = next((r for r in ledger_obj["executions"] if r.get("run_id") == PREBIND_RUN), None) if ledger_obj else None
    check(rows, "exception_binds_exact_corrected_post_sha",
          POST.is_file() and target_row is not None and sha(POST) == target_row.get("external_post_sha256", ""),
          {"actual": sha(POST) if POST.is_file() else None,
           "ledger": target_row.get("external_post_sha256") if target_row else None})

    # V40 artifact-level checks: all three independent layers (POST, external
    # charge, and internal receipt) must be present and hash-bound to the same
    # execution.  This is deliberately separate from the helper's generic
    # charge loop so the audit remains useful if that loop is later edited.
    prebind_paths = {
        "post": ROOT / PREBIND_POST,
        "execution": ROOT / PREBIND_EXECUTION,
        "time": ROOT / PREBIND_TIME,
        "charge": ROOT / PREBIND_CHARGE,
        "receipt": ROOT / PREBIND_RECEIPT,
    }
    prebind_files_present = all(p.is_file() for p in prebind_paths.values())
    check(rows, "v40_prebind_artifact_bundle_present", prebind_files_present,
          {name: str(path) for name, path in prebind_paths.items()})
    prebind_post = load(prebind_paths["post"]) if prebind_paths["post"].is_file() else {}
    prebind_execution = load(prebind_paths["execution"]) if prebind_paths["execution"].is_file() else {}
    prebind_charge = load(prebind_paths["charge"]) if prebind_paths["charge"].is_file() else {}
    prebind_receipt = load(prebind_paths["receipt"]) if prebind_paths["receipt"].is_file() else {}
    actual_prebind_hashes = {name: sha(path) if path.is_file() else None for name, path in prebind_paths.items()}
    expected_prebind_hashes = {
        "post": PREBIND_POST_SHA,
        "execution": PREBIND_EXECUTION_SHA,
        "time": PREBIND_TIME_SHA,
        "charge": PREBIND_CHARGE_SHA,
        "receipt": PREBIND_RECEIPT_SHA,
    }
    check(rows, "v40_prebind_artifact_hashes_match_frozen_identity",
          prebind_files_present and actual_prebind_hashes == expected_prebind_hashes,
          {"expected": expected_prebind_hashes, "actual": actual_prebind_hashes})
    check(rows, "v40_prebind_ledger_row_identity_and_sha_binding",
          prebind_row is not None
          and prebind_row.get("run_id") == PREBIND_RUN
          and prebind_row.get("charge_basis") == basis
          and prebind_row.get("execution") == PREBIND_EXECUTION
          and prebind_row.get("execution_sha256") == PREBIND_EXECUTION_SHA
          and prebind_row.get("external_post") == PREBIND_POST
          and prebind_row.get("external_post_sha256") == PREBIND_POST_SHA
          and prebind_row.get("external_charge") == PREBIND_CHARGE
          and prebind_row.get("external_charge_sha256") == PREBIND_CHARGE_SHA
          and prebind_row.get("internal_receipt") == PREBIND_RECEIPT
          and prebind_row.get("internal_receipt_sha256") == PREBIND_RECEIPT_SHA
          and prebind_row.get("external_time") == PREBIND_TIME
          and prebind_row.get("external_time_sha256") == PREBIND_TIME_SHA,
          {"row": prebind_row})
    check(rows, "v40_prebind_post_charge_receipt_sha_binding",
          prebind_files_present
          and prebind_post.get("execution_sha256") == PREBIND_EXECUTION_SHA
          and prebind_post.get("external_charge") == PREBIND_CHARGE
          and prebind_post.get("external_charge_sha256") == PREBIND_CHARGE_SHA
          and prebind_post.get("internal_receipt") == PREBIND_RECEIPT
          and prebind_post.get("internal_receipt_sha256") == PREBIND_RECEIPT_SHA
          and prebind_charge.get("execution_sha256") == PREBIND_EXECUTION_SHA
          and prebind_charge.get("source_execution") == PREBIND_EXECUTION
          and prebind_charge.get("receipt") == PREBIND_RECEIPT
          and prebind_charge.get("receipt_sha256") == PREBIND_RECEIPT_SHA
          and prebind_receipt.get("execution_sha256") == PREBIND_EXECUTION_SHA,
          {"post_external_charge_sha256": prebind_post.get("external_charge_sha256"),
           "post_internal_receipt_sha256": prebind_post.get("internal_receipt_sha256"),
           "charge_receipt_sha256": prebind_charge.get("receipt_sha256")})
    zero_call_fields = {
        "compile_calls": prebind_execution.get("compile_calls", 0),
        "model_calls": prebind_execution.get("model_calls", 0),
        "query_calls": prebind_execution.get("query_calls", 0),
        "solve_calls": prebind_execution.get("solve_calls", 0),
    }
    check(rows, "v40_prebind_compile_model_query_solve_zero",
          all(value == 0 for value in zero_call_fields.values()),
          {"counts": zero_call_fields,
           "present_fields": [field for field in zero_call_fields if field in prebind_execution]})
    check(rows, "v40_prebind_status_and_failure_boundary",
          prebind_execution.get("status") == "STOP_ENGINEERING_FAILURE_RETAINED_PREFIX"
          and "ALL_REQUIRED_INPUTS_AND_REUSED_OBJECTS_PREBOUND" in prebind_execution.get("error", "")
          and prebind_post.get("personnel_independent") is True
          and prebind_post.get("external_supervision_qualified") is False
          and prebind_post.get("external_timing_qualified") is False
          and prebind_post.get("external_cost_qualified") is True
          and prebind_post.get("scientific_calls") == 0
          and prebind_post.get("formal_table_I_calls") == 0
          and prebind_post.get("new_VI_candidate_constructions") == 0,
          {"execution_status": prebind_execution.get("status"),
           "failure": prebind_execution.get("error"),
           "post_status": prebind_post.get("status")})

    # Dynamic saved-only smoke test: this uses no model, binary, compiler,
    # subprocess, or mutation.  It proves the validator can consume V40 while
    # preserving the ordinary current ledger predicates.
    dynamic = {"status": "SKIPPED", "error": None}
    try:
        sys.path.insert(0, str(V2.parent))
        import validate_prior_preflight_recovery_v2 as successor
        ledger = load(LEDGER)
        spec = {"prior": {"ledger": str(LEDGER.relative_to(ROOT)),
                           "ledger_sha256": sha(LEDGER),
                           "wall_s": ledger["conservative_r2_sum_wall_s"],
                           "cpu_s": ledger["conservative_r2_sum_cpu_s"]},
                "budget": {"wall_s": 1.0, "cpu_s": 1.0}}
        result = successor.validate_prior(spec, "INDEPENDENT_AUDIT_DUMMY_RUN", ROOT / "results/p4_full/INDEPENDENT_AUDIT_DUMMY_RUN")
        dynamic = {"status": "PASS", "wall_s": result["wall_s"], "cpu_s": result["cpu_s"],
                   "evidence_count": len(result["evidence_sha256"])}
    except Exception as exc:  # report, do not conceal a failed audit
        dynamic = {"status": "FAIL", "error": repr(exc)}
        errors.append("dynamic saved-only V39 validation failed")
    check(rows, "dynamic_v40_saved_only_validation", dynamic["status"] == "PASS", dynamic)

    status = "PASS" if not errors and all(row["passed"] for row in rows) else "FAIL"
    report = {"schema": "P4_D080_PRIOR_VALIDATOR_V2_V40_INDEPENDENT_AUDIT_V2",
              "status": status, "v1_sha256": sha(V1), "v2_sha256": sha(V2),
              "ledger": str(LEDGER.relative_to(ROOT)), "ledger_sha256": sha(LEDGER) if LEDGER.is_file() else None,
              "checks": rows, "errors": errors,
              "interpretation": "PASS requires ordinary v1 predicates plus the two explicitly digest-bound III and V BUILD02 prebind cost-only exceptions, including V zero compile/model/query/solve calls; it does not qualify scientific planning or continuous collision."}
    return finish(rows, errors, args.output, report)


def finish(rows, errors, output=None, report=None):
    if report is None:
        report = {"schema": "P4_D080_PRIOR_VALIDATOR_V2_V40_INDEPENDENT_AUDIT_V2",
                  "status": "PASS" if not errors and all(r["passed"] for r in rows) else "FAIL",
                  "checks": rows, "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
