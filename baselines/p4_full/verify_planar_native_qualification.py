"""Read-only independent scoring of saved planar diagnostic JSON.

CLI: python3 verify_planar_native_qualification.py input.json output.json
Uses direct cumulative angles and math.fsum; it does not call author solvers.
The source input manifest supplies original endpoints, without snapping.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector(value, length):
    return (
        isinstance(value, list)
        and len(value) == length
        and all(isinstance(x, (int, float)) and math.isfinite(x) for x in value)
    )


def independent(q, author_pi):
    """Closed-chain FK directly from 19 unit-link cumulative angles."""
    if not vector(q, 20):
        raise ValueError("Non-finite/wrong-length saved joint vector")
    angles = [math.fsum(q[: j + 1]) for j in range(19)]
    x = math.fsum(math.cos(a) for a in angles)
    y = math.fsum(math.sin(a) for a in angles)
    terminal = math.fsum([*q[:19], author_pi, -q[19]])
    c, s = math.cos(terminal), math.sin(terminal)
    return x, y, c, s


def closure_error(q, author_pi):
    x, y, c, s = independent(q, author_pi)
    return max(abs(x - 7), abs(y - 4)), max(abs(c - 1), abs(s))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument(
        "--source-input-manifest",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "configs/p4_full/build_interface_manifest.json",
    )
    args = parser.parse_args()
    source = json.loads(args.input_json.read_text())
    manifest = json.loads(args.source_input_manifest.read_text())
    expected_models = [
        m for m in manifest["model_records"] if m["environment"] == "I"
    ]
    if len(expected_models) != 1:
        raise ValueError("Expected exactly one author planar input manifest")
    model = expected_models[0]
    original = {}
    for point in model["endpoints"]:
        if point["file"] == "run/plan_PCS.cpp":
            original.setdefault(point["type"], point["values_rad"])
    if set(original) != {"c_start", "c_goal"}:
        raise ValueError("Missing unchanged author endpoint facts")
    pi = 3.1416
    checks = []

    def check(identifier, passed, detail):
        checks.append(
            {
                "check_id": identifier,
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

    records = source.get("records", [])
    counts = Counter(r.get("kind") for r in records)
    expected_counts = {
        "raw_endpoint": 2,
        "fk": 100,
        "nr_projection": 10,
        "apc_projection": 40,
        "negative_closure": 1,
        "negative_unreachable_IK": 2,
    }
    check(
        "saved_count_identity",
        dict(counts) == expected_counts,
        {"expected": expected_counts, "observed": dict(counts)},
    )
    check(
        "source_identity",
        source.get("source_commit") == model["commit"]
        and source.get("seed") == 20261014
        and source.get("formal_planning_calls") == 0,
        {
            "expected_source_commit": model["commit"],
            "observed": source.get("source_commit"),
            "expected_seed": 20261014,
        },
    )
    raw_errors = []
    fk_errors = []
    nr_errors = []
    apc_errors = []
    apc_valid_partitions = set()
    apc_rejects = 0
    seen = Counter()
    wrapped_rotation_diagnostics = []
    for record in records:
        kind = record["kind"]
        if kind == "raw_endpoint":
            key = "c_start" if record["endpoint"] == 0 else "c_goal"
            q = record["q"]
            check(
                "raw_endpoint_" + key,
                q == original[key] and record.get("gate_applied") is False,
                {"policy": "raw unchanged; errors not snapped or gated"},
            )
            p, r = closure_error(q, pi)
            raw_errors.append(
                {"endpoint": key, "position_source_units": p, "rotation_matrix": r}
            )
        elif kind == "fk":
            index = record["index"]
            seen[("fk", index)] += 1
            q = record["q_author_chart"]
            x, y, c, s = independent(q, pi)
            native = record["author_KDL_matrix4"]
            if vector(native, 16):
                p = max(abs(native[3] - x), abs(native[7] - y), abs(native[11]))
                expected = [c, -s, 0, s, c, 0, 0, 0, 1]
                actual = [native[4 * i + j] for i in range(3) for j in range(3)]
                r = max(abs(a - b) for a, b in zip(actual, expected))
                physical = q.copy()
                physical[19] = pi - q[19]
                check(
                    f"fk_{index}",
                    p <= 1e-7
                    and r <= 1e-10
                    and record["q_temporary_KDL"] == physical,
                    {"position_source_units": p, "rotation_matrix": r},
                )
                fk_errors.append((p, r))
            else:
                check(f"fk_{index}", False, {"failure": "nonfinite native matrix"})
            wrapped_rotation_diagnostics.append(
                record.get("apc_left_physical_matrix_error_diagnostic")
            )
        elif kind == "nr_projection":
            i = record["index"]
            seen[("nr_projection", i)] += 1
            point = original["c_start" if i < 5 else "c_goal"].copy()
            point[i % 5] += 0.01 if i % 2 else -0.01
            check(f"nr_input_{i}", record["q_input"] == point, {"offset_rad": 0.01 if i % 2 else -0.01})
            if record["source_return"] and vector(record.get("q_output"), 20):
                p, r = closure_error(record["q_output"], pi)
                check(f"nr_output_{i}", p <= 1e-5 and r <= 1e-5, {
                    "position_source_units": p, "rotation_matrix": r
                })
                nr_errors.append((p, r))
            else:
                check(f"nr_output_{i}", False, {"failure": "source reject/nonfinite"})
        elif kind == "apc_projection":
            part, branch = record["partition"], record["branch"]
            seen[("apc_projection", part, branch)] += 1
            check(
                f"apc_input_{part}_{branch}",
                record["q_input"] == original["c_start"] and record["collision_checked"] is False,
                {"scope": "component projection only, no collision/planning qualification"},
            )
            if not record["source_return"]:
                apc_rejects += 1
                apc_errors.append({"partition": part, "branch": branch, "state": "SOURCE_REJECT_REASON_NOT_YET_IDENTIFIED"})
            elif vector(record.get("q_candidate_diagnostic"), 20):
                p, r = closure_error(record["q_candidate_diagnostic"], pi)
                ok = p <= 1e-5 and r <= 1e-5
                check(f"apc_returned_output_{part}_{branch}", ok, {
                    "position_source_units": p, "rotation_matrix": r
                })
                if ok:
                    apc_valid_partitions.add(part)
                apc_errors.append({"partition": part, "branch": branch, "state": "RETURNED", "position_source_units": p, "rotation_matrix": r})
            else:
                check(f"apc_returned_output_{part}_{branch}", False, {"failure": "nonfinite output"})
        elif kind == "negative_closure":
            expected = original["c_start"].copy()
            expected[0] += 0.1
            p, r = closure_error(record["q_input"], pi)
            check(
                "negative_closure",
                record["q_input"] == expected and (p > 1e-5 or r > 1e-5),
                {"position_source_units": p, "rotation_matrix": r},
            )
        elif kind == "negative_unreachable_IK":
            branch = record["branch"]
            seen[("negative_unreachable_IK", branch)] += 1
            check(
                f"negative_unreachable_{branch}",
                record["target_source_units_rad"] == [100000000, 0, 0]
                and record["source_return"] is False,
                {"reason": "target exceeds two-link plus half-terminal reach"},
            )
    required_keys = (
        [("fk", i) for i in range(100)]
        + [("nr_projection", i) for i in range(10)]
        + [("apc_projection", p, b) for p in range(20) for b in range(2)]
        + [("negative_unreachable_IK", b) for b in range(2)]
    )
    check(
        "unique_fixture_ids",
        set(seen) == set(required_keys) and all(v == 1 for v in seen.values()),
        {"expected_unique": len(required_keys), "observed_unique": len(seen)},
    )
    result = {
        "schema": "P4_PLANAR_SAVED_EVIDENCE_VERIFICATION_V1",
        "input_sha256": digest(args.input_json),
        "source_input_manifest_sha256": digest(args.source_input_manifest),
        "verifier_sha256": digest(Path(__file__)),
        "classification": "INDEPENDENT_SAVED_COMPONENT_CHECK_NOT_PLANNER_OR_PAPER_FULL",
        "oracle": "direct cumulative angles with math.fsum; author terminal encoder PI_-q19; no solver calls",
        "units": "source_link_length_unit / rad",
        "checks": checks,
        "check_counts": dict(Counter(c["status"] for c in checks)),
        "raw_endpoint_errors_diagnostic_only": raw_errors,
        "fk_max_errors": [max((x[j] for x in fk_errors), default=None) for j in (0, 1)],
        "nr_max_errors": [max((x[j] for x in nr_errors), default=None) for j in (0, 1)],
        "apc_projection_details": apc_errors,
        "apc_source_rejects": apc_rejects,
        "apc_partitions_with_one_independently_valid_returned_branch": sorted(apc_valid_partitions),
        "apc_left_wrapped_scalar_physical_rotation_diagnostic": wrapped_rotation_diagnostics,
        "limit": "No collisions, RBS, planner, all reachable branch completeness, or artificial-singularity rank qualification. Source rejects are retained with unknown reason.",
        "new_planner_calls": 0,
    }
    args.output_json.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )


if __name__ == "__main__":
    main()
