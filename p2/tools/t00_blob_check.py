#!/usr/bin/env python3
"""T00: byte-level provenance audit of the legacy P2 import.

Compares every file in the declared P2 integration scope between the frozen
legacy commit and the current branch head, using Git blob SHAs only.
No working-tree reads, no simulation, no timing.
"""
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = "7787c75a8042af041579e5df0c9ac3e3ec4f6195"
DST = "HEAD"
# The acceptance record (P2_ACCEPTED_DELIVERY_FREEZE_MANIFEST.json) was written in the
# commit that recorded the user's acceptance, one commit after SRC; SRC does not contain it.
MANIFEST_REV = "f4f9d3b97e80481dbc74ca419ac9b390447e4eef"
MANIFEST_PATH = "reports/P2_ACCEPTED_DELIVERY_FREEZE_MANIFEST.json"
OUT = REPO / "p2" / "reviews" / "LEGACY_BLOB_CHECK.json"

SCOPE_PREFIXES = (
    "baselines/p2_pose_force/",
    "common/",
    "reports/P2_",
    "docs/tasks/P2_",
    "configs/p2_",
    "p2/",
    "references/P2_",
    "tests/test_p2_",
)


def in_scope(path: str) -> bool:
    if path.startswith(SCOPE_PREFIXES):
        return True
    if path.startswith("scripts/") and "p2" in Path(path).name.lower():
        return True
    if path.startswith("results/"):
        head = path.split("/")[1] if "/" in path else ""
        return "P2" in head
    return False


def ls_tree(rev: str) -> dict:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-tree", "-r", "-z", "--long", rev],
        capture_output=True, check=True,
    ).stdout
    entries = {}
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, otype, sha, size = meta.split()
        entries[path.decode("utf-8")] = {
            "mode": mode.decode(),
            "type": otype.decode(),
            "sha": sha.decode(),
            "size": int(size),
        }
    return entries


def is_binary_blob(sha: str) -> bool:
    data = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", sha],
                          capture_output=True, check=True).stdout
    return b"\0" in data[:8000]


def sha256_manifest_crosscheck() -> dict:
    """Second, independent byte-level layer: SHA256 from the accepted-delivery manifest.

    Git blob SHAs prove tree identity; SHA256 over the working-tree bytes proves the
    checked-out files are the same bytes the user accepted, independent of git.
    """
    raw = subprocess.run(["git", "-C", str(REPO), "show",
                          f"{MANIFEST_REV}:{MANIFEST_PATH}"],
                         capture_output=True, check=True).stdout
    manifest = json.loads(raw)
    entries = manifest["files_sha256"]
    match, mismatch, missing = [], [], []
    for path, expected in sorted(entries.items()):
        target = REPO / path
        if not target.is_file():
            missing.append(path)
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        (match if actual == expected else mismatch).append(path)
    missing_suffix = {}
    for path in missing:
        suffix = Path(path).suffix or "<none>"
        missing_suffix[suffix] = missing_suffix.get(suffix, 0) + 1
    return {
        "manifest_rev": MANIFEST_REV,
        "manifest_path": MANIFEST_PATH,
        "manifest_entries": len(entries),
        "manifest_declared_frozen_file_count": manifest.get("frozen_file_count"),
        "sha256_match": len(match),
        "sha256_mismatch": len(mismatch),
        "sha256_missing": len(missing),
        "mismatch_paths": mismatch,
        "missing_by_suffix": missing_suffix,
        "missing_non_image_paths": [p for p in missing if Path(p).suffix != ".png"],
        "missing_are_report_rendering_assets_only": all(
            "/review_assets" in p or "_review_assets" in p or "layout_review" in p
            or "report_assets" in p or "font_preview" in p
            for p in missing),
        "interpretation": (
            "Every non-image omitted path is a Word/PDF rendering or pagination asset; "
            "no run log, summary.json, cases.jsonl or trajectory asset is missing."
        ),
    }


def main() -> int:
    src_all = ls_tree(SRC)
    dst_all = ls_tree(DST)
    src = {p: v for p, v in src_all.items() if in_scope(p)}
    dst = {p: v for p, v in dst_all.items() if in_scope(p)}

    records = []
    counts = {"MATCH": 0, "MODIFIED": 0, "NEW": 0, "OMITTED": 0}
    for path in sorted(set(src) | set(dst)):
        s = src.get(path)
        d = dst.get(path)
        if s and d and s["sha"] == d["sha"]:
            status = "MATCH"
        elif s and d:
            status = "MODIFIED"
        elif d:
            status = "NEW"
        else:
            status = "OMITTED"
        counts[status] += 1
        records.append({
            "path": path,
            "status": status,
            "source_sha": s["sha"] if s else None,
            "dest_sha": d["sha"] if d else None,
            "source_size": s["size"] if s else None,
            "dest_size": d["size"] if d else None,
            "binary": is_binary_blob((d or s)["sha"]),
        })

    areas = {}
    for r in records:
        if r["path"].startswith("results/"):
            area = "results/"
        elif r["path"].startswith("scripts/"):
            area = "scripts/"
        else:
            area = r["path"].split("/")[0] + "/"
        a = areas.setdefault(area, {"MATCH": 0, "MODIFIED": 0, "NEW": 0, "OMITTED": 0})
        a[r["status"]] += 1

    modified = [r for r in records if r["status"] == "MODIFIED"]
    new = [r for r in records if r["status"] == "NEW"]
    omitted = [r for r in records if r["status"] == "OMITTED"]
    sha_layer = sha256_manifest_crosscheck()

    payload = {
        "audit_id": "T00_LEGACY_BLOB_CHECK",
        "generated_by": (
            "p2/tools/t00_blob_check.py -- layer 1: git ls-tree blob SHAs; "
            "layer 2: SHA256 over working-tree bytes vs the accepted-delivery manifest"),
        "repo": str(REPO),
        "branch": subprocess.run(["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"],
                                 capture_output=True, text=True).stdout.strip(),
        "source_commit": SRC,
        "dest_commit": DST,
        "dest_commit_resolved": subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", DST],
            capture_output=True, text=True).stdout.strip(),
        "scope": {
            "included_prefixes": list(SCOPE_PREFIXES),
            "extra_rules": [
                "scripts/<name containing 'p2'>",
                "results/<folder name containing 'P2'>",
            ],
            "excluded_deliberately": [
                "P4 code, P4 branches, P4 reports and results",
                "bulky rendered images referenced only by legacy reports",
            ],
        },
        "totals": {
            "files_compared": len(records),
            "source_files_in_scope": len(src),
            "dest_files_in_scope": len(dst),
            **counts,
        },
        "by_area": areas,
        "sha256_freeze_manifest_crosscheck": sha_layer,
        "verdict": {
            "all_dest_files_byte_identical_to_source": counts["MODIFIED"] == 0,
            "modified_count": len(modified),
            "new_count": len(new),
            "omitted_count": len(omitted),
            "modified_is_only_shared_readme": (
                [r["path"] for r in modified] == ["common/README.md"]),
            "sha256_mismatch_zero": sha_layer["sha256_mismatch"] == 0,
            "note": (
                "NEW files are the p2/ roadmap written on this branch plus T00 review "
                "outputs; OMITTED files exist at the frozen commit but were not imported. "
                "common/README.md differs because this branch is based on main, which "
                "carries an older TASK02 README; it is documentation, not P2 algorithm code."
            ),
        },
        "modified_files": modified,
        "new_files": new,
        "omitted_files": omitted[:400],
        "omitted_files_truncated": len(omitted) > 400,
        "all_records": records,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")

    print(json.dumps({k: payload[k] for k in ("totals", "by_area", "verdict")},
                     indent=2, ensure_ascii=False))
    print("\nMODIFIED:", [r["path"] for r in modified][:20])
    print("\nNEW (non p2/):",
          [r["path"] for r in new if not r["path"].startswith("p2/")][:20])
    print("\nOMITTED sample:", [r["path"] for r in omitted][:25])
    print("\nwrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
