#!/usr/bin/env python3
"""Independent, read-only audit of the D080 prior-validator successor.

The audit intentionally does not import the successor as the source of truth
for its static checks.  It compares the frozen v1 source, checks the single
declared III cost-only exception, validates the current V39 ledger once, and
reports missing digest bindings.  It never edits ledger, experiment, or source
artifacts.  Use ``--output`` only to write a new audit report.
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
LEDGER = ROOT / "results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V39.json"
POST = ROOT / "reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json"
RUN = "20261018_R2_D080_III_RRT_PCS_PHYSICAL01"
POST_REL = "reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json"
V1_SHA = "b315972ce22569684c4fe21dc487fc0456b7db63b8224906020d6fc41911f65e"


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

    # The exception must be one immutable run and one declared cost basis.  A
    # generic external_cost_qualified escape hatch is a protocol failure.
    exception_matches = re.findall(
        r"exception\s*=\s*\(row\['run_id'\]\s*==\s*COST_ONLY_RUN\s+and\s+row\['charge_basis'\]\s*==\s*'([^']+)'\)",
        v2_src,
    )
    check(rows, "single_explicit_iii_exception", exception_matches == ["EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE"],
          {"matches": exception_matches})
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

    # These are intentionally strict.  They currently expose the v2 defect if
    # the exception does not bind the ledger's external_post_sha256 to bytes.
    check(rows, "exception_binds_post_path_constant", "str(post_path.relative_to(ROOT))==COST_ONLY_POST" in v2_src)
    post_sha_patterns = [
        "sha(post_path)==row['external_post_sha256']",
        "row['external_post_sha256']==sha(post_path)",
    ]
    exception_text = v2_src[v2_src.find("if exception:"):v2_src.find("else:", v2_src.find("if exception:"))]
    check(rows, "exception_binds_post_digest_to_ledger", any(p in exception_text for p in post_sha_patterns),
          {"required_one_of": post_sha_patterns})
    check(rows, "exception_forces_external_timing_false", "post['external_timing_qualified'] is False" in v2_src)
    target_row = None
    if LEDGER.is_file():
        target_row = next((r for r in load(LEDGER)["executions"] if r.get("run_id") == RUN), None)
    check(rows, "exception_binds_exact_corrected_post_sha",
          POST.is_file() and target_row is not None and sha(POST) == target_row.get("external_post_sha256", ""),
          {"actual": sha(POST) if POST.is_file() else None,
           "ledger": target_row.get("external_post_sha256") if target_row else None})

    # Dynamic saved-only smoke test: this uses no model, binary, compiler,
    # subprocess, or mutation.  It proves the validator can consume V39 while
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
    check(rows, "dynamic_v39_saved_only_validation", dynamic["status"] == "PASS", dynamic)

    status = "PASS" if not errors and all(row["passed"] for row in rows) else "FAIL"
    report = {"schema": "P4_D080_PRIOR_VALIDATOR_V2_INDEPENDENT_AUDIT_V1",
              "status": status, "v1_sha256": sha(V1), "v2_sha256": sha(V2),
              "ledger": str(LEDGER.relative_to(ROOT)), "ledger_sha256": sha(LEDGER) if LEDGER.is_file() else None,
              "checks": rows, "errors": errors,
              "interpretation": "PASS requires ordinary v1 predicates plus a single digest-bound III cost-only exception; it does not qualify scientific planning or continuous collision."}
    return finish(rows, errors, args.output, report)


def finish(rows, errors, output=None, report=None):
    if report is None:
        report = {"schema": "P4_D080_PRIOR_VALIDATOR_V2_INDEPENDENT_AUDIT_V1",
                  "status": "PASS" if not errors and all(r["passed"] for r in rows) else "FAIL",
                  "checks": rows, "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
