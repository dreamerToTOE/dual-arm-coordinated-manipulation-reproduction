#!/usr/bin/env python3
"""Compare two T01-E baseline snapshots element by element.

Used as the equivalence oracle for O1/O2: run `t01e_baseline.py` on the frozen
original code (baseline) and on the optimised code (candidate), then compare.
No thresholds are relaxed here; they are read from the baseline index.

Pass criteria
  strict keys (no floating-point reordering allowed): bitwise identical
  other numeric keys:                                |a-b| <= abs and |a-b|/max(|a|,|b|,1) <= rel
  metadata (case ids, iteration counts, convergence, exception type/message): exact match

Reports, for every array, the maximum absolute difference, the maximum relative
difference and the location of the maximum absolute difference.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

STRICT_PREFIX_HINT = ("__Qd", "__P0", "__P_pred", "__X", "__U", "__f", "__F", "__A", "__Lw")


def load(d: Path):
    index = json.loads((d / "index.json").read_text())
    cases = [json.loads(line) for line in (d / "cases.jsonl").read_text().splitlines() if line]
    arrays = np.load(d / index["arrays_npz"])
    return index, cases, {k: arrays[k] for k in arrays.files}


def compare(base_dir: Path, cand_dir: Path, out_path: Path) -> int:
    bi, bcases, barr = load(base_dir)
    ci, ccases, carr = load(cand_dir)
    tol = bi.get("tolerances_proposed", {}).get("reordered_float_paths", {})
    abs_tol = float(tol.get("abs", 1e-12))
    rel_tol = float(tol.get("rel", 1e-12))

    results = []
    failed = []

    bkeys, ckeys = set(barr), set(carr)
    for key in sorted(bkeys - ckeys):
        results.append({"key": key, "status": "MISSING_IN_CANDIDATE"})
    for key in sorted(ckeys - bkeys):
        results.append({"key": key, "status": "EXTRA_IN_CANDIDATE"})

    n_bitwise = 0
    n_within = 0
    worst_abs = 0.0
    worst_rel = 0.0
    worst_key = None

    for key in sorted(bkeys & ckeys):
        a, b = np.asarray(barr[key]), np.asarray(carr[key])
        if a.shape != b.shape:
            results.append({"key": key, "status": "SHAPE_MISMATCH",
                            "baseline_shape": list(a.shape), "candidate_shape": list(b.shape)})
            failed.append(key)
            continue
        diff = np.abs(a.astype(np.float64) - b.astype(np.float64))
        max_abs = float(np.max(diff)) if diff.size else 0.0
        denom = np.maximum(np.maximum(np.abs(a), np.abs(b)), 1.0)
        rel = diff / denom
        max_rel = float(np.max(rel)) if rel.size else 0.0
        loc = tuple(int(x) for x in np.unravel_index(int(np.argmax(diff)), diff.shape)) if diff.size else ()
        bitwise = bool(np.array_equal(a, b, equal_nan=True))
        strict = any(key.endswith(sfx) or sfx in key for sfx in STRICT_PREFIX_HINT)
        if bitwise:
            n_bitwise += 1
        ok = bitwise if strict else (max_abs <= abs_tol and max_rel <= rel_tol)
        if ok:
            n_within += 1
        else:
            failed.append(key)
        if max_abs > worst_abs:
            worst_abs, worst_key = max_abs, key
        worst_rel = max(worst_rel, max_rel)
        results.append({
            "key": key, "status": "PASS" if ok else "FAIL", "strict_bitwise": strict,
            "bitwise_equal": bitwise, "max_abs": max_abs, "max_rel": max_rel,
            "argmax_location": list(loc),
        })

    # metadata comparison
    bmap = {c["id"]: c for c in bcases}
    cmap = {c["id"]: c for c in ccases}
    meta_results = []
    for cid in sorted(set(bmap) | set(cmap)):
        if cid not in bmap or cid not in cmap:
            meta_results.append({"case": cid, "status": "MISSING"})
            failed.append(f"meta:{cid}:missing")
            continue
        a, b = bmap[cid], cmap[cid]
        keys = ("update_iterations", "update_converged", "rejected", "exception_type", "message",
                "W_rank")
        diffs = {k: [a.get(k), b.get(k)] for k in keys if a.get(k) != b.get(k)}
        meta_results.append({"case": cid, "status": "PASS" if not diffs else "FAIL", "diffs": diffs})
        if diffs:
            failed.append(f"meta:{cid}")

    out = {
        "kind": "T01E_EQUIVALENCE_COMPARISON",
        "baseline": str(base_dir),
        "candidate": str(cand_dir),
        "baseline_source_sha256": bi.get("source_sha256"),
        "candidate_source_sha256": ci.get("source_sha256"),
        "tolerances": {"abs": abs_tol, "rel": rel_tol, "strict": list(STRICT_PREFIX_HINT)},
        "arrays_compared": len(bkeys & ckeys),
        "arrays_bitwise_equal": n_bitwise,
        "arrays_within_tolerance": n_within,
        "failed_keys": failed,
        "worst_abs": worst_abs,
        "worst_abs_key": worst_key,
        "worst_rel": worst_rel,
        "verdict": "PASS" if not failed else "FAIL",
        "array_results": results,
        "meta_results": meta_results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"arrays={out['arrays_compared']} bitwise={n_bitwise} within={n_within} "
          f"failed={len(failed)} worst_abs={worst_abs:.3e} ({worst_key}) -> {out['verdict']}")
    if failed:
        for k in failed[:20]:
            print("  FAIL", k)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    return compare(Path(a.baseline), Path(a.candidate), Path(a.output))


if __name__ == "__main__":
    sys.exit(main())
