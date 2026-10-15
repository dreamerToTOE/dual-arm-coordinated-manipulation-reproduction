#!/usr/bin/env python3
"""Stage a traceable, local geometry-consistent variant of pinned author sources.

This project owns the patching code and its newly derived algebra.  Author files
are read from a separately acquired, pinned snapshot and copied to a new external
or Git-ignored directory.  Nothing is downloaded, compiled, solved or benchmarked
by this module.  The original snapshot and all original R1 observations survive.

The arm's elementary-transform geometry gives, after removing the terminal x
offset, r=A*sin(q2)+B*cos(q2), z=A*cos(q2)-B*sin(q2), with
A=l2+L*cos(q3+alpha), B=L*sin(q3+alpha).  Thus q2=atan2(r,z)-atan2(B,A).
The radial coordinate is signed after the selected shoulder rotation; taking its
absolute value loses solutions inside the Comau shoulder offset.  The source's
q3 and wrist-sign branch order, joint bounds, bases and grasp matrices remain.

Wrist derivation, independent of the author's expanded FK expressions:
R03=Rz(q1)*Ry(q2+q3), W=R03^T*R=Rx(q4)*Ry(q5)*Rx(q6).  Therefore
W00=cos(q5), (W10,W20)=sin(q5)*(sin(q4),-cos(q4)), and
(W01,W02)=sin(q5)*(sin(q6),cos(q6)).  The original sign456[branch]
selects the signed q5; hypot(W10,W20) evaluates |sin(q5)| without subtracting
nearly equal squares.  At q5=0, only q4+q6 is identifiable.  Choosing q4=0
gives q6=atan2(W21,W22); at q5=+/-pi, q6=atan2(-W21,-W22).
The latter case is rejected by the unchanged original +/-120 degree q5 bound
when joint limits are enabled.  Singular branches may share a representative;
we do not claim that eight distinct solutions exist on a singular stratum.

Only 64*double_epsilon is used to identify floating-point zero in this wrist
decomposition (1.4210854715202004e-14).  It is separate from experimental
success gates, which are neither read nor modified here.  Original 1e-4 q5
and 1e-5 all-joint truncations are removed rather than used as tolerances.

No endpoint or target is consumed by this patcher.  Downstream qualifications
must preserve both the saved, originally clipped target and the independent
physical-FK target under distinct labels rather than silently replacing either.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "P4_D079_GEOMETRY_CONSISTENT_APC_STAGE_V1"
CPP_REL = Path("proj_classes/apc_class.cpp")
HEADER_REL = Path("proj_classes/apc_class.h")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = PROJECT_ROOT / "configs/p4_full/author_source_manifest.json"

# These hashes were read from the immutable R0 snapshots before any staging.
# They also prevent mistakenly using ckComau's older master as environment V.
SOURCES: dict[str, dict[str, Any]] = {
    "abb": {
        "repository": "CKCplanning", "branch": "master",
        "commit": "909bd72fff778aca8682c96f9eb86ae4eb75557b",
        "url": "https://github.com/avishais/CKCplanning",
        "cpp_sha256": "c74ea9ade8bb7d80b0b980139c58b659e6911ab3d3cb61b853be980654ede22c",
        "header_sha256": "d65480bdbc0d62772a3732bff4a7c5d06cc9f9f0b41927a9012a4d0d111e28cf",
        "shoulder_offset": "0.0", "height": "l1 + b",
        "alpha": "atan2(l3b + l4, l3a)", "fk_clip_loops": 0,
        "robot_count": 2,
    },
    "comau_iv": {
        "repository": "ckcComau2", "branch": "master",
        "commit": "80089340f0f1f6822e5b2821a63c998b6ae0413f",
        "url": "https://github.com/avishais/ckcComau2",
        "cpp_sha256": "265c1718e3ce2a6081419b2a954794fa10c9a59dc7d4984b8541904c0333a923",
        "header_sha256": "508ac232a81a0915b7a6c709fc8aa6dcb539936e4b648325dba82b04e6404402",
        "shoulder_offset": "l1x", "height": "l1z + b",
        "alpha": "atan2(l3x + l4, l3z)", "fk_clip_loops": 1,
        "robot_count": 2,
    },
    "comau_v": {
        "repository": "ckcComau", "branch": "industrialScene",
        "commit": "ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca",
        "url": "https://github.com/avishais/ckcComau/tree/industrialScene",
        "cpp_sha256": "ad2e271952cfb4dbb726f817b8d5b08dfed0fb8c7a4616bd94d5fe0413d64933",
        "header_sha256": "d57ffc7d5b3af7e00c5a633ae784dac18d24699341267cd3ae0af9797c9611f1",
        "shoulder_offset": "l1x", "height": "l1z + b",
        "alpha": "atan2(l3x + l4, l3z)", "fk_clip_loops": 1,
        "robot_count": 2,
    },
    "comau_vi": {
        "repository": "ckcComau3", "branch": "master",
        "commit": "25488a86947cd07377cc62c43850df719a70d9ee",
        "url": "https://github.com/avishais/ckcComau3",
        "cpp_sha256": "8f52ae7296c4cdb6310ce957d65eac882ce8e56baba35710b8a8fd083e2b2522",
        "header_sha256": "210a1a6c594ed3dadd93ab40d9cc369da2d01b18aadc4e1ecd051929d1090be9",
        "shoulder_offset": "l1x", "height": "l1z + b",
        "alpha": "atan2(l3x + l4, l3z)", "fk_clip_loops": 1,
        "robot_count": 3,
    },
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _function_span(text: str, signature: str) -> tuple[int, int]:
    """Find one C++ definition, respecting comment and string-literal braces."""
    if text.count(signature) != 1:
        raise ValueError(f"Expected exactly one function definition: {signature}")
    begin = text.index(signature)
    brace = text.index("{", begin + len(signature))
    depth, state, i = 0, "normal", brace
    while i < len(text):
        c, pair = text[i], text[i:i + 2]
        if state == "line":
            if c == "\n":
                state = "normal"
        elif state == "block":
            if pair == "*/":
                state, i = "normal", i + 1
        elif state in ('"', "'"):
            if c == "\\":
                i += 1
            elif c == state:
                state = "normal"
        elif pair == "//":
            state, i = "line", i + 1
        elif pair == "/*":
            state, i = "block", i + 1
        elif c in ('"', "'"):
            state = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return begin, i + 1
        i += 1
    raise ValueError(f"Unbalanced function definition: {signature}")


def _replace_once(text: str, old: str, new: str, label: str,
                  changes: list[dict[str, Any]]) -> str:
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected one exact anchor, found {text.count(old)}")
    changes.append({"id": label, "occurrences": 1,
                    "removed_segment_sha256": _sha(old.encode()),
                    "inserted_segment_sha256": _sha(new.encode()),
                    "removed_characters": len(old), "inserted_characters": len(new)})
    return text.replace(old, new, 1)


def _patch_cpp(raw: bytes, model: str) -> tuple[bytes, list[dict[str, Any]]]:
    """Derive patch text in memory; no IK evaluation or file write occurs here."""
    spec = SOURCES[model]
    # Preserve the author's CRLF files byte for byte outside the changed spans.
    newline = "\r\n" if b"\r\n" in raw else "\n"
    original = raw.decode("utf-8")
    text = original.replace("\r\n", "\n")
    changes: list[dict[str, Any]] = []
    signature = "bool two_robots::IKsolve_rob(Matrix T, int robot_num, int solution_num)"
    start, end = _function_span(text, signature)
    ik = text[start:end]
    ik = _replace_once(
        ik, "\tState q(6);",
        "\t// P4 geometry-consistent numerical variant: local mathematical pi only.\n"
        "\tconst double p4_math_pi = acos(-1.0);\n\tState q(6);",
        "IK_LOCAL_MATHEMATICAL_PI_DECLARATION", changes)
    pi_count = len(re.findall(r"\bPI_\b", ik))
    if pi_count != 17:
        raise ValueError(f"Unexpected IK PI_ token count: {pi_count}, expected 17")
    previous_pi = ik
    ik = re.sub(r"\bPI_\b", "p4_math_pi", ik)
    changes.append({"id": "IK_LOCAL_PI_TOKEN_SUBSTITUTION", "occurrences": pi_count,
                    "scope": signature, "before_segment_sha256": _sha(previous_pi.encode()),
                    "after_segment_sha256": _sha(ik.encode()),
                    "model_global_PI_PI__and_header_unchanged": True})

    # Work from the selected q1.  In particular, a shoulder reversal changes r;
    # no absolute radius or unsigned square root may substitute for that sign.
    radial_start = ik.index("\tdouble k2 =" if model == "abb" else "\tdouble k =")
    radial_end = ik.index("\tdouble l34 =", radial_start)
    old_radial = ik[radial_start:radial_end]
    new_radial = (
        "\t// Signed wrist-centre coordinates in this shoulder branch.\n"
        f"\tconst double p4_r = p5[0]*cos(q[0]) + p5[1]*sin(q[0]) - {spec['shoulder_offset']};\n"
        f"\tconst double p4_z = p5[2] - ({spec['height']});\n"
        "\tdouble D2 = p4_r*p4_r + p4_z*p4_z;\n")
    ik = _replace_once(ik, old_radial, new_radial,
                       "IK_BRANCH_SIGNED_RADIAL_AND_DISTANCE", changes)
    # Keep the original eight q3 signs and wrapping/limit checks.  Only q2's
    # triangle reconstruction changes; the prior sqrt loses cosine quadrant.
    q2_start = ik.index("\t\tdouble sinalpha1 =")
    q2_end = ik.index("\t\tif (q[1]>p4_math_pi)", q2_start)
    old_q2 = ik[q2_start:q2_end]
    new_q2 = (
        f"\t\tconst double p4_alpha = {spec['alpha']};\n"
        "\t\tconst double p4_A = l2 + l34*cos(q[2] + p4_alpha);\n"
        "\t\tconst double p4_B = l34*sin(q[2] + p4_alpha);\n"
        "\t\tq[1] = atan2(p4_r, p4_z) - atan2(p4_B, p4_A);\n")
    ik = _replace_once(ik, old_q2, new_q2,
                       "IK_Q2_FULL_QUADRANT_TRIANGLE_RECONSTRUCTION", changes)

    wrist_start = ik.index("\t//q5\n")
    wrist_end = ik.index("\tif (include_joint_limits && (fabs(q[3])", wrist_start)
    old_wrist = ik[wrist_start:wrist_end]
    new_wrist = (
        "\t// W = (Rz(q1)*Ry(q2+q3))^T * R, with original wrist branch signs.\n"
        "\tdouble p4_W[3][3];\n"
        "\tfor (int p4_j = 0; p4_j < 3; ++p4_j) {\n"
        "\t\tp4_W[0][p4_j] = c23*c1*R[0][p4_j] + c23*s1*R[1][p4_j] - s23*R[2][p4_j];\n"
        "\t\tp4_W[1][p4_j] = -s1*R[0][p4_j] + c1*R[1][p4_j];\n"
        "\t\tp4_W[2][p4_j] = s23*c1*R[0][p4_j] + s23*s1*R[1][p4_j] + c23*R[2][p4_j];\n"
        "\t}\n"
        "\tconst double p4_abs_sin5 = hypot(p4_W[1][0], p4_W[2][0]);\n"
        "\tconst double p4_wrist_roundoff = 64.0 * 2.2204460492503131e-16;\n"
        "\tif (p4_abs_sin5 <= p4_wrist_roundoff) {\n"
        "\t\t// Canonical representative of a non-unique singular wrist family.\n"
        "\t\tq[4] = atan2(sign456[solution_num]*0.0, p4_W[0][0]);\n"
        "\t\tq[3] = 0.0;\n"
        "\t\tconst double p4_pole = p4_W[0][0] < 0.0 ? -1.0 : 1.0;\n"
        "\t\tq[5] = atan2(p4_pole*p4_W[2][1], p4_pole*p4_W[2][2]);\n"
        "\t} else {\n"
        "\t\tq[4] = atan2(sign456[solution_num]*p4_abs_sin5, p4_W[0][0]);\n"
        "\t\tq[3] = atan2(sign456[solution_num]*p4_W[1][0], -sign456[solution_num]*p4_W[2][0]);\n"
        "\t\tq[5] = atan2(sign456[solution_num]*p4_W[0][1], sign456[solution_num]*p4_W[0][2]);\n"
        "\t}\n"
        "\tif (include_joint_limits && fabs(q[4]) > q5minmax)\n"
        "\t\treturn false;\n\n")
    ik = _replace_once(ik, old_wrist, new_wrist,
                       "IK_W_R03_TRANSPOSE_R_HYPOT_AND_CANONICAL_SINGULAR_WRIST", changes)
    # q5's former truncation belongs to the wrist replacement above.  Preserve
    # the separate all-joint removal as a separately identified patch record.
    q5_clip = "q[4] = fabs(q[4]) < 1e-4 ? 0 : q[4];"
    if old_wrist.count(q5_clip) != 1:
        raise ValueError("Expected exactly one original q5 angle truncation")
    changes.append({"id": "IK_REMOVE_Q5_1E_MINUS_4_ANGLE_TRUNCATION",
                    "occurrences": 1, "removed_segment_sha256": _sha(q5_clip.encode()),
                    "inserted_segment_sha256": _sha(b""),
                    "included_in": "IK_W_R03_TRANSPOSE_R_HYPOT_AND_CANONICAL_SINGULAR_WRIST"})
    angle_clip = ("\tfor (int i = 0; i < 6; i++)\n"
                  "\t\tif (fabs(q[i])<1e-5)\n"
                  "\t\t\tq[i] = 0;\n")
    ik = _replace_once(ik, angle_clip,
                       "\t// Preserve solved joint values; no all-joint decimal truncation.\n",
                       "IK_REMOVE_ALL_JOINT_1E_MINUS_5_ANGLE_TRUNCATION", changes)
    text = text[:start] + ik + text[end:]

    fk_signature = "void two_robots::FKsolve_rob(State q, int robot_num)"
    fk_start, fk_end = _function_span(text, fk_signature)
    fk = text[fk_start:fk_end]
    clip = ("\tfor (int i = 0; i < 3; i++)\n"
            "\t\tfor (int j = 0; j < 4; j++)\n"
            "\t\t\tT_fk_temp[i][j] = fabs(T_fk_temp[i][j]) < 1e-4 ? 0 : T_fk_temp[i][j];\n")
    if fk.count(clip) != spec["fk_clip_loops"]:
        raise ValueError("Unexpected FK clipping policy in pinned source")
    if spec["fk_clip_loops"]:
        fk = _replace_once(fk, clip,
                           "\t// P4 numerical variant: preserve continuous physical FK entries.\n",
                           "FK_REMOVE_ELEMENTWISE_1E_MINUS_4_CLIPPING", changes)
        text = text[:fk_start] + fk + text[fk_end:]
    else:
        changes.append({"id": "FK_ALREADY_CONTINUOUS_NO_CHANGE", "occurrences": 0})
    patched = text.replace("\n", newline).encode("utf-8")
    # Verify the public change scope without embedding the author functions in
    # a public diff file.  Constructor, base/grasp definitions and joint bounds
    # reside outside the two permitted function spans.
    def excluded_functions(value: str) -> str:
        for sig in (signature, fk_signature):
            a, b = _function_span(value, sig)
            value = value[:a] + "<P4_PERMITTED_FUNCTION>" + value[b:]
        return value
    if excluded_functions(original.replace("\r\n", "\n")) != excluded_functions(text):
        raise AssertionError("Modification escaped the permitted FK/IK functions")
    return patched, changes


def _snapshot_files(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if ".git" in rel.parts:
            continue
        if path.is_symlink():
            raise ValueError(f"Snapshot symlink is not accepted: {rel}")
        if path.is_file():
            raw = path.read_bytes()
            result[rel.as_posix()] = {"sha256": _sha(raw), "bytes": len(raw)}
    return result


def _verify_manifest(root: Path, model: str, manifest_path: Path,
                     files: dict[str, dict[str, Any]]) -> dict[str, Any]:
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    spec = SOURCES[model]
    matches = [entry for entry in manifest["repositories"]
               if entry["repository"] == spec["repository"]
               and entry["branch"] == spec["branch"]
               and entry["commit"] == spec["commit"]]
    if len(matches) != 1:
        raise ValueError("The audited manifest lacks this exact repository/branch/commit")
    entry = matches[0]
    expected = {record["path"]: {"sha256": record["sha256"], "bytes": record["bytes"]}
                for record in entry["files"]}
    if files != expected:
        missing = sorted(set(expected) - set(files))
        extra = sorted(set(files) - set(expected))
        changed = sorted(key for key in set(expected) & set(files)
                         if expected[key] != files[key])
        raise ValueError(f"Source snapshot differs: missing={missing}, extra={extra}, changed={changed}")
    for rel, key in ((CPP_REL, "cpp_sha256"), (HEADER_REL, "header_sha256")):
        if _sha((root / rel).read_bytes()) != spec[key]:
            raise ValueError(f"Built-in fixed source hash mismatch: {rel}")
    return {"path": str(manifest_path), "sha256": _sha(manifest_raw),
            "repository": spec["repository"], "branch": spec["branch"],
            "commit": spec["commit"], "url": spec["url"],
            "file_count": len(files), "all_file_hashes_verified": True}


def _require_local_untracked_stage(destination: Path) -> None:
    if PROJECT_ROOT == destination or PROJECT_ROOT in destination.parents:
        check = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "check-ignore", "--quiet", str(destination)],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if check.returncode != 0:
            raise ValueError("Author copies inside the project must be in a Git-ignored directory")


def stage_spatial_ik(model: str, author_root: str | Path, output_root: str | Path,
                     source_manifest: str | Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    """Create a fresh local stage and return its manifest for a later NR patch.

    The output must not exist.  No on-disk source edit is attempted until all
    input hashes and all text anchors pass.  A failed copy is retained as failed
    staging evidence; it is never reset or deleted by this script.
    """
    if model not in SOURCES:
        raise ValueError(f"Unknown model {model!r}; choose {tuple(SOURCES)}")
    source = Path(author_root).expanduser().resolve(strict=True)
    destination = Path(output_root).expanduser().resolve()
    manifest_path = Path(source_manifest).expanduser().resolve(strict=True)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite an existing stage: {destination}")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Source and stage paths must be disjoint, unrelated directories")
    _require_local_untracked_stage(destination)
    before = _snapshot_files(source)
    provenance = _verify_manifest(source, model, manifest_path, before)
    original_cpp = (source / CPP_REL).read_bytes()
    patched_cpp, changes = _patch_cpp(original_cpp, model)
    payload: dict[str, Any] = {
        "schema": SCHEMA, "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "STAGED_NOT_COMPILED_OR_QUALIFIED", "model": model,
        "robot_count": SOURCES[model]["robot_count"],
        "author_root": str(source), "stage_root": str(destination),
        "source_provenance": provenance,
        "patcher_sha256": _sha(Path(__file__).read_bytes()),
        "changes": changes,
        "permitted_modified_files": [CPP_REL.as_posix()],
        "cpp_before_sha256": _sha(original_cpp), "cpp_after_sha256": _sha(patched_cpp),
        "header_unchanged_sha256": SOURCES[model]["header_sha256"],
        "branch_policy": "Original 0..7 q3/sign456 numbering; no NR fallback",
        "singular_wrist_policy": {
            "matrix": "W=(Rz(q1)*Ry(q2+q3))^T R=Rx(q4)*Ry(q5)*Rx(q6)",
            "zero_sine_threshold": 1.4210854715202004e-14,
            "threshold_definition": "64*IEEE754_binary64_epsilon; numerical zero only",
            "canonical_q4_rad": 0.0,
            "canonical_q5_zero_q6": "atan2(W21,W22)",
            "canonical_q5_pi_q6": "atan2(-W21,-W22); original enabled joint limits reject q5=+/-pi",
            "branch_nonuniqueness": "Singular family representatives may coincide across branch indices",
        },
        "model_policy": "Unchanged physical parameters, base/grasp literals and joint limits",
        "target_policy": "No target supplied here; original clipped and physical FK targets must remain distinct",
        "original_files": before,
    }
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".git"))
    (destination / CPP_REL).write_bytes(patched_cpp)
    staged = _snapshot_files(destination)
    expected_stage = dict(before)
    expected_stage[CPP_REL.as_posix()] = {"sha256": _sha(patched_cpp), "bytes": len(patched_cpp)}
    if staged != expected_stage:
        raise AssertionError("Staged files differ outside the single declared APC source patch")
    after = _snapshot_files(source)
    if after != before:
        raise AssertionError("Original source snapshot changed during staging")
    payload["original_snapshot_verified_unchanged_after_staging"] = True
    payload["staged_files_before_followup_patches"] = staged
    manifest_out = destination / "p4_geometry_consistent_apc_stage_manifest.json"
    with manifest_out.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return {"model": model, "stage_root": str(destination),
            "manifest": str(manifest_out), "manifest_sha256": _sha(manifest_out.read_bytes()),
            "cpp_after_sha256": _sha(patched_cpp), "status": payload["status"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=tuple(SOURCES), required=True)
    parser.add_argument("--author-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    result = stage_spatial_ik(args.model, args.author_root, args.output_root,
                              args.source_manifest)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
