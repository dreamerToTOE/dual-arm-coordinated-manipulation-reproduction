#!/usr/bin/env python3
"""Adversarial tests for the T01-E comparator.

Every negative case mutates a *copy* of the frozen baseline, runs the comparator as
a subprocess, and requires: verdict FAIL, exit code != 0, and a failure whose
reason matches the mutation. A positive control (unmodified copy) must PASS with
exit code 0. The frozen baseline itself is never modified.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
COMPARE = ROOT / "p2" / "tools" / "t01e_compare.py"


def copy_base(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("index.json", "cases.jsonl", "arrays.npz"):
        shutil.copy2(src / name, dst / name)
    with np.load(dst / "arrays.npz") as z:
        return {k: z[k] for k in z.files}


def save_arrays(dst: Path, arrays):
    np.savez_compressed(dst / "arrays.npz", **arrays)


def run_case(name, mutation, expect_reason, src, tmp_root):
    work = Path(tempfile.mkdtemp(prefix=f"t01e_{name}_", dir=tmp_root))
    arrays = copy_base(src, work)
    cases_path = work / "cases.jsonl"
    cases = [json.loads(l) for l in cases_path.read_text().splitlines() if l]

    if mutation == "drop_key":
        del arrays["C01_nominal_pivot__Qd"]
        save_arrays(work, arrays)
    elif mutation == "add_key":
        arrays["C01_nominal_pivot__EXTRA"] = np.zeros(3)
        save_arrays(work, arrays)
    elif mutation == "change_element":
        arrays["C01_nominal_pivot__F"][3, 4] += 1e-3
        save_arrays(work, arrays)
    elif mutation == "one_ulp":
        a = arrays["C01_nominal_pivot__F"]
        a[3, 4] = np.nextafter(a[3, 4], np.inf)
        save_arrays(work, arrays)
    elif mutation == "dtype_change":
        arrays["C01_nominal_pivot__F"] = arrays["C01_nominal_pivot__F"].astype(np.float32)
        save_arrays(work, arrays)
    elif mutation == "signed_zero":
        u = arrays["C01_nominal_pivot__U"]
        assert u[0] == 0.0, "fixture must contain an exact zero"
        u[0] = -0.0
        save_arrays(work, arrays)
    elif mutation == "nonfinite":
        arrays["C01_nominal_pivot__A"][0, 1] = np.nan
        save_arrays(work, arrays)
    elif mutation == "shape_change":
        arrays["C01_nominal_pivot__F"] = arrays["C01_nominal_pivot__F"][:-1, :]
        save_arrays(work, arrays)
    elif mutation == "meta_iterations":
        target = next(c for c in cases if c["id"] == "C09_residual_update")
        target["update_iterations"] = target["update_iterations"] + 1
        cases_path.write_text("\n".join(json.dumps(c) for c in cases) + "\n")
    elif mutation == "meta_message":
        target = next(c for c in cases if c["id"] == "E01_non_se3")
        target["message"] = target["message"] + " (tampered)"
        cases_path.write_text("\n".join(json.dumps(c) for c in cases) + "\n")
    elif mutation == "meta_extra_case":
        cases.append({"id": "C99_invented", "kind": "nominal_zero_velocity"})
        cases_path.write_text("\n".join(json.dumps(c) for c in cases) + "\n")
    else:
        raise ValueError(mutation)

    out = work / "compare.json"
    proc = subprocess.run([sys.executable, str(COMPARE), "--baseline", str(src),
                           "--candidate", str(work), "--output", str(out)],
                          capture_output=True, text=True)
    verdict = None
    reasons = []
    if out.exists():
        data = json.loads(out.read_text())
        verdict = data["verdict"]
        reasons = sorted({r.get("reason", "") for r in data["array_results"]
                          if r.get("status") == "FAIL"} |
                         {m.get("reason", "") for m in data["meta_results"]
                          if m.get("status") == "FAIL"})
    passed = (proc.returncode != 0 and verdict == "FAIL" and expect_reason in reasons)
    return {
        "case": name, "mutation": mutation, "expected_reason": expect_reason,
        "exit_code": proc.returncode, "verdict": verdict, "reasons": reasons,
        "pass": passed,
        "stderr_tail": proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "",
    }, work


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default=str(ROOT / "p2" / "reviews" / "t01e_baseline"))
    ap.add_argument("--output", default=str(ROOT / "p2" / "reviews" / "t01e_compare_negative.json"))
    args = ap.parse_args()
    src = Path(args.baseline)

    tmp_root = Path(tempfile.mkdtemp(prefix="t01e_negative_"))
    results = []

    # positive control
    ctrl = Path(tempfile.mkdtemp(prefix="t01e_ctrl_", dir=tmp_root))
    copy_base(src, ctrl)
    out = ctrl / "compare.json"
    proc = subprocess.run([sys.executable, str(COMPARE), "--baseline", str(src),
                           "--candidate", str(ctrl), "--output", str(out)],
                          capture_output=True, text=True)
    data = json.loads(out.read_text())
    results.append({"case": "P0_positive_control", "mutation": "none",
                    "expected_reason": None, "exit_code": proc.returncode,
                    "verdict": data["verdict"], "reasons": [],
                    "pass": proc.returncode == 0 and data["verdict"] == "PASS"})

    cases = [
        ("N01_drop_key", "drop_key", "MISSING_IN_CANDIDATE"),
        ("N02_add_key", "add_key", "EXTRA_IN_CANDIDATE"),
        ("N03_change_element", "change_element", "BITWISE_MISMATCH"),
        ("N04_one_ulp", "one_ulp", "BITWISE_MISMATCH"),
        ("N05_dtype_change", "dtype_change", "DTYPE_OR_SHAPE_MISMATCH"),
        ("N06_signed_zero", "signed_zero", "BITWISE_MISMATCH"),
        ("N07_nonfinite", "nonfinite", "NONFINITE_VALUES"),
        ("N08_shape_change", "shape_change", "DTYPE_OR_SHAPE_MISMATCH"),
        ("N09_meta_iterations", "meta_iterations", "METADATA_MISMATCH"),
        ("N10_meta_message", "meta_message", "METADATA_MISMATCH"),
        ("N11_meta_extra_case", "meta_extra_case", "MISSING_CASE"),
    ]
    for name, mutation, reason in cases:
        rec, _ = run_case(name, mutation, reason, src, tmp_root)
        results.append(rec)

    ok = all(r["pass"] for r in results)
    payload = {
        "kind": "T01E_COMPARATOR_ADVERSARIAL_TESTS",
        "baseline": str(src),
        "comparator": str(COMPARE),
        "positive_control": results[0],
        "negative_cases": results[1:],
        "all_passed": ok,
        "note": "every negative case must yield verdict FAIL and a non-zero exit code",
    }
    Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
    for r in results:
        print(f"{'PASS' if r['pass'] else 'FAIL'}  {r['case']:<22} rc={r['exit_code']} "
              f"verdict={r['verdict']} reasons={r['reasons']}")
    print("all_passed:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
