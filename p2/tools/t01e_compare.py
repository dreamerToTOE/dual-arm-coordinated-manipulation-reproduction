#!/usr/bin/env python3
"""Strict equivalence comparator for T01-E baselines.

Exit code is 0 only when every array and every metadata field passes. Missing or
extra candidate arrays are failures. Strict arrays are compared by dtype, shape
and raw byte pattern (which covers signed zero and NaN payload); non-finite
values in valid numeric fixtures are failures, never masked.

Array classification is a frozen table keyed by the exact suffix after "<case>__".
There is no substring matching: an unknown suffix is UNCLASSIFIED and fails.

Relative error is dimensioned: rel = |a-b| / max(|a|,|b|), evaluated only where
max(|a|,|b|) >= REF_FLOOR; elements below the floor are judged by absolute error
alone. Nothing is normalised by a constant 1.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ABS_TOL = 1e-12
REL_TOL = 1e-12
REF_FLOOR = 1e-12          # below this magnitude a relative error is not meaningful

# ---- frozen classification -------------------------------------------------
ALL_SUFFIXES = (
    "X", "U", "f", "A", "F", "Lw", "Qd", "P0", "P_pred", "X_pred",
    "D", "tau", "hK", "hB", "h", "W", "internal", "singular_values",
    "tau_rate_0", "tau_rate_1", "grasp_body_0", "grasp_body_1",
    "H_EE1", "H_EE2", "H_hK1", "H_hK2", "H_visual1", "H_visual2",
    "z_EE1", "z_EE2", "z_hK1", "z_hK2", "z_visual1", "z_visual2",
    "residual_EE1", "residual_EE2", "residual_hK1", "residual_hK2",
    "residual_visual1", "residual_visual2",
    "P_post", "V_post", "innovation_before", "innovation_after",
)

# O1-a/b/c: everything must be bitwise identical.
STRICT_CLASSES = {s: "bitwise" for s in ALL_SUFFIXES}

# O1-d (optional se3_log replacement): only arrays that flow through se3_log may
# use the 1e-12 tolerance; inputs and covariance priors stay bitwise. Enabled
# only by the explicit --mode o1d flag, and reported as such in the output.
O1D_OVERRIDES = {
    "tau": "tolerance", "hK": "tolerance", "hB": "tolerance", "h": "tolerance",
    "D": "tolerance", "W": "tolerance", "internal": "tolerance",
    "singular_values": "tolerance",
    "tau_rate_0": "tolerance", "tau_rate_1": "tolerance",
    "grasp_body_0": "tolerance", "grasp_body_1": "tolerance",
    "H_EE1": "tolerance", "H_EE2": "tolerance", "H_hK1": "tolerance",
    "H_hK2": "tolerance", "H_visual1": "tolerance", "H_visual2": "tolerance",
    "z_EE1": "tolerance", "z_EE2": "tolerance", "z_hK1": "tolerance",
    "z_hK2": "tolerance", "z_visual1": "tolerance", "z_visual2": "tolerance",
    "residual_EE1": "tolerance", "residual_EE2": "tolerance",
    "residual_hK1": "tolerance", "residual_hK2": "tolerance",
    "residual_visual1": "tolerance", "residual_visual2": "tolerance",
    "f": "tolerance", "A": "tolerance", "F": "tolerance", "Lw": "tolerance",
    "Qd": "tolerance", "P_pred": "tolerance", "X_pred": "tolerance",
    "P_post": "tolerance", "V_post": "tolerance",
    "innovation_before": "tolerance", "innovation_after": "tolerance",
}
MODE_TABLE = {"strict": STRICT_CLASSES,
              "o1d": {**STRICT_CLASSES, **O1D_OVERRIDES}}


def suffix_of(key):
    return key.split("__", 1)[1] if "__" in key else None


def load(d: Path):
    index = json.loads((d / "index.json").read_text())
    cases = [json.loads(line) for line in (d / "cases.jsonl").read_text().splitlines() if line]
    with np.load(d / index["arrays_npz"]) as z:
        arrays = {k: z[k] for k in z.files}
    return index, cases, arrays


def bitwise_equal(a, b):
    if a.dtype != b.dtype or a.shape != b.shape:
        return False
    return (np.ascontiguousarray(a).view(np.uint8).tobytes() ==
            np.ascontiguousarray(b).view(np.uint8).tobytes())


def compare_arrays(a, b):
    a64 = a.astype(np.float64, copy=False)
    b64 = b.astype(np.float64, copy=False)
    finite_a = np.isfinite(a64)
    finite_b = np.isfinite(b64)
    diff = np.abs(a64 - b64)
    scale = np.maximum(np.abs(a64), np.abs(b64))
    meaningful = scale >= REF_FLOOR
    rel = np.zeros_like(diff)
    if np.any(meaningful):
        rel[meaningful] = diff[meaningful] / scale[meaningful]
    max_abs = float(np.max(diff)) if diff.size else 0.0
    max_rel = float(np.max(rel[meaningful])) if np.any(meaningful) else 0.0
    loc_abs = tuple(int(x) for x in np.unravel_index(int(np.argmax(diff)), diff.shape)) \
        if diff.size else ()
    loc_rel = ()
    if np.any(meaningful):
        masked = np.where(meaningful, rel, -1.0)
        loc_rel = tuple(int(x) for x in np.unravel_index(int(np.argmax(masked)), rel.shape))
    return {
        "max_abs": max_abs,
        "max_rel_meaningful": max_rel,
        "argmax_abs": list(loc_abs),
        "argmax_rel": list(loc_rel),
        "nonfinite_baseline": int(np.size(a64) - np.count_nonzero(finite_a)),
        "nonfinite_candidate": int(np.size(b64) - np.count_nonzero(finite_b)),
        "dtype": [str(a.dtype), str(b.dtype)],
        "shape": [list(a.shape), list(b.shape)],
    }


def floats_close(x, y):
    if isinstance(x, float) or isinstance(y, float):
        if not isinstance(x, float) or not isinstance(y, float):
            return False
        if not (np.isfinite(x) and np.isfinite(y)):
            return False
        return abs(x - y) <= ABS_TOL * max(1.0, abs(x), abs(y))
    return x == y


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--mode", choices=sorted(MODE_TABLE), default="strict")
    args = ap.parse_args()

    table = MODE_TABLE[args.mode]
    bi, bcases, barr = load(Path(args.baseline))
    ci, ccases, carr = load(Path(args.candidate))

    failures, results = [], []
    counts = {"bitwise": 0, "bitwise_pass": 0, "tolerance": 0, "tolerance_pass": 0}
    worst_abs, worst_key = 0.0, None
    bkeys, ckeys = set(barr), set(carr)

    for key in sorted(bkeys - ckeys):
        failures.append({"key": key, "reason": "MISSING_IN_CANDIDATE"})
        results.append({"key": key, "status": "FAIL", "reason": "MISSING_IN_CANDIDATE"})
    for key in sorted(ckeys - bkeys):
        failures.append({"key": key, "reason": "EXTRA_IN_CANDIDATE"})
        results.append({"key": key, "status": "FAIL", "reason": "EXTRA_IN_CANDIDATE"})

    for key in sorted(bkeys & ckeys):
        suffix = suffix_of(key)
        if suffix is None or suffix not in table:
            failures.append({"key": key, "reason": "UNCLASSIFIED_KEY", "suffix": suffix})
            results.append({"key": key, "status": "FAIL", "reason": "UNCLASSIFIED_KEY",
                            "suffix": suffix})
            continue
        kind = table[suffix]
        a, b = barr[key], carr[key]
        if a.shape != b.shape or a.dtype != b.dtype:
            info = {"key": key, "status": "FAIL", "reason": "DTYPE_OR_SHAPE_MISMATCH",
                    "baseline": [str(a.dtype), list(a.shape)],
                    "candidate": [str(b.dtype), list(b.shape)]}
            results.append(info)
            failures.append(info)
            continue

        info = compare_arrays(a, b)
        nonfinite = bool(info["nonfinite_baseline"] or info["nonfinite_candidate"])
        if kind == "bitwise":
            counts["bitwise"] += 1
            ok = (not nonfinite) and bitwise_equal(a, b)
            reason = "NONFINITE_VALUES" if nonfinite else ("BITWISE_MISMATCH" if not ok else None)
            if ok:
                counts["bitwise_pass"] += 1
        else:
            counts["tolerance"] += 1
            ok = (not nonfinite and info["max_abs"] <= ABS_TOL
                  and info["max_rel_meaningful"] <= REL_TOL)
            reason = "NONFINITE_VALUES" if nonfinite else ("TOLERANCE_EXCEEDED" if not ok else None)
            if ok:
                counts["tolerance_pass"] += 1
        if info["max_abs"] > worst_abs:
            worst_abs, worst_key = info["max_abs"], key
        info.update({"key": key, "class": kind, "status": "PASS" if ok else "FAIL",
                     "reason": reason})
        results.append(info)
        if not ok:
            failures.append(info)

    bmap = {c["id"]: c for c in bcases}
    cmap = {c["id"]: c for c in ccases}
    meta = []
    for cid in sorted(set(bmap) | set(cmap)):
        if cid not in bmap or cid not in cmap:
            meta.append({"case": cid, "status": "FAIL", "reason": "MISSING_CASE"})
            failures.append({"case": cid, "reason": "MISSING_CASE"})
            continue
        a, b = bmap[cid], cmap[cid]
        diffs = {k: [a.get(k), b.get(k)] for k in sorted(set(a) | set(b))
                 if not floats_close(a.get(k), b.get(k))}
        meta.append({"case": cid, "status": "PASS" if not diffs else "FAIL",
                     "reason": None if not diffs else "METADATA_MISMATCH", "diffs": diffs})
        if diffs:
            failures.append({"case": cid, "reason": "METADATA_MISMATCH", "diffs": diffs})

    verdict = "PASS" if not failures else "FAIL"
    out = {
        "kind": "T01E_EQUIVALENCE_COMPARISON",
        "mode": args.mode,
        "baseline": str(args.baseline),
        "candidate": str(args.candidate),
        "baseline_git_commit": bi.get("git_commit"),
        "candidate_git_commit": ci.get("git_commit"),
        "baseline_source_sha256": bi.get("source_sha256"),
        "candidate_source_sha256": ci.get("source_sha256"),
        "thresholds": {"abs": ABS_TOL, "rel": REL_TOL, "relative_floor": REF_FLOOR},
        "arrays_compared": len(bkeys & ckeys),
        "classes": counts,
        "worst_abs": worst_abs,
        "worst_abs_key": worst_key,
        "failure_count": len(failures),
        "failed_keys": [f.get("key") or f.get("case") for f in failures],
        "verdict": verdict,
        "array_results": results,
        "meta_results": meta,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")

    print(f"mode={args.mode} arrays={out['arrays_compared']} "
          f"bitwise={counts['bitwise_pass']}/{counts['bitwise']} "
          f"tolerance={counts['tolerance_pass']}/{counts['tolerance']} "
          f"failures={len(failures)} -> {verdict}")
    for f in failures[:10]:
        print("  FAIL", f.get("key") or f.get("case"), f.get("reason"))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
