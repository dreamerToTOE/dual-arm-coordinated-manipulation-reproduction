#!/usr/bin/env python3.10
# -*- coding: utf-8 -*-
"""Build p5/evidence/P5_official_code_manifest.json.

The JSON is derived *only* from artefacts already captured during the P5 paper
study session:

  <WORK>/api/*.json              GitHub REST metadata (repo + HEAD commit)
  <WORK>/tgz_*.tar.gz            source snapshots (codeload tarball)
  <WORK>/sb/*/                   extracted snapshots (for file inventories)

Nothing is downloaded here, so the manifest is reproducible offline.  Provenance
that could not be captured (e.g. codeload tar sha256 for the two repositories we
only inspected through the API) is recorded explicitly as `null` with an
`unavailable_reason`, never guessed.

Usage
-----
    /usr/bin/python3.10 p5/tools/p5_manifest.py --work <WORK> --out p5/evidence/P5_official_code_manifest.json
    /usr/bin/python3.10 p5/tools/p5_manifest.py --check <manifest.json>

`--check` re-derives every field it can from the on-disk artefacts and compares
against the committed JSON, so drift is detectable in CI-style fashion.
"""

import argparse
import hashlib
import json
import os
import sys
import tarfile
from collections import Counter

PAPER = {
    "title": "A Unified Framework for Coordinated Multi-Arm Motion Planning",
    "authors": ["Sina Mirrazavi Salehian", "Nadia Figueroa", "Aude Billard"],
    "venue": "The International Journal of Robotics Research (IJRR)",
    "year": 2018,
    "volume": 37,
    "issue": 6,
    "pages": "583-603",
    "doi": "10.1177/0278364918765952",
    "pdf_sha256": "6f367be45e0c925df64ec5e4ab3046e1de8aa96627c65ddb2fd71720d9eedc02",
    "pdf_pages": 28,
}

# ---------------------------------------------------------------------------
# Repository registry.  `role` / `equations` / `executability` are the P5 audit
# conclusions (see P5_OFFICIAL_CODE_AUDIT.md); they are asserted here so the
# manifest cannot silently drift away from the prose report.
# ---------------------------------------------------------------------------
REPOS = [
    {
        "key": "Multiarm_ds",
        "owner": "SinaMirrazavi",
        "name": "Multiarm_ds",
        "api_json": "api/SinaMirrazavi_Multiarm_ds.json",
        "commit_json": "api/commits/SinaMirrazavi_Multiarm_ds.json",
        "tgz": "tgz_Multiarm_ds.tar.gz",
        "alias_urls": ["https://github.com/sinamr66/Multiarm_ds"],
        "role": "Single-DS multi-arm behaviour generator; coordination allocation tau and virtual-object dynamics.",
        "equations": ["(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)", "(9)", "(10)", "(11)", "(12)", "(13)", "(36)"],
        "key_files": ["src/multiarm_ds.cpp", "src/LPV.cpp", "include/multiarm_ds.h", "include/LPV.h"],
        "executability": "BUILDABLE_AFTER_PATCH",
        "blockers": [
            "ROS package (catkin) with a hard dependency on SESODS_lib and ML_toolbox; not a standalone library.",
            "calculate_coordination_allocation() implements a variant of (8) (DIVERGENT from the printed equation); see P5_EQUATION_AUDIT.md O2.",
            "calculate_u() uses U = -A^T X instead of the paper's U_i = tau * dot{x}^V (DIVERGENT); see O1.",
        ],
    },
    {
        "key": "LPV",
        "owner": "SinaMirrazavi",
        "name": "LPV",
        "api_json": "api/SinaMirrazavi_LPV.json",
        "commit_json": "api/commits/SinaMirrazavi_LPV.json",
        "tgz": "tgz_LPV.tar.gz",
        "alias_urls": ["https://github.com/sinamr66/LPV"],
        "role": "Standalone LPV/GMR DS solver: builds A_ik and theta_k, integrates the DS.",
        "equations": ["(3)", "(4)", "(5)"],
        "key_files": ["src/LPV.cpp", "include/LPV.h"],
        "executability": "BUILDABLE_AFTER_PATCH",
        "blockers": [
            "Depends on ML_toolbox (GMR) and Eigen; CMakeLists assumes a ROS/catkin context.",
            "No test target and no golden data; correctness must be re-established numerically (P5-T02).",
        ],
    },
    {
        "key": "QP_IK_solver",
        "owner": "SinaMirrazavi",
        "name": "QP_IK_solver",
        "api_json": "api/SinaMirrazavi_QP_IK_solver.json",
        "commit_json": "api/commits/SinaMirrazavi_QP_IK_solver.json",
        "tgz": "tgz_QP_IK_solver.tar.gz",
        "alias_urls": ["https://github.com/sinamr66/QP_IK_solver"],
        "role": "Centralised velocity-level QP inverse kinematics with LVI projection dynamics.",
        "equations": ["(16)", "(17a)", "(17b)", "(17c)", "(17d)", "(18)", "(19)", "(20)", "(21a)", "(21b)", "(22)", "(23)", "(25)", "(26)"],
        "key_files": ["src/qp_ik_solver.cpp", "include/qp_ik_solver.h"],
        "executability": "NOT_EXECUTABLE",
        "blockers": [
            "CVXGEN-generated solver sources are absent from the repository; the QP backend does not exist in the snapshot.",
            "get_gamma() is declared/called but never defined.",
            "Gamma_ / DGamma_ are never updated: the SCA path is dead code, so (17d) is structurally present but numerically inert.",
            "Omega_projector() has a return-value defect (returns its input); (21b) therefore cannot produce the projected iterate as published.",
        ],
    },
    {
        "key": "SCA_data_construction",
        "owner": "SinaMirrazavi",
        "name": "SCA_data_construction",
        "api_json": "api/SinaMirrazavi_SCA_data_construction.json",
        "commit_json": "api/commits/SinaMirrazavi_SCA_data_construction.json",
        "tgz": "tgz_SCA_data_construction.tar.gz",
        "alias_urls": ["https://github.com/sinamr66/SCA_data_construction"],
        "role": "Generates the labelled 36-D SCA dataset (free vs collision) used to train the boundary.",
        "equations": ["(27)"],
        "key_files": ["src/", "matlab/"],
        "executability": "PARTIALLY_REPRODUCIBLE",
        "blockers": [
            "Requires a robot model (KUKA LWR via kuka-rviz-simulation / ROS) to evaluate distances.",
            "Random sampling configuration does not reproduce the paper's stated sampling count; see P5_PAPER_STUDY.md section 8.4.",
        ],
    },
    {
        "key": "SCA-Boundary-Learning",
        "owner": "nbfigueroa",
        "name": "SCA-Boundary-Learning",
        "api_json": "api/nbfigueroa_SCA-Boundary-Learning.json",
        "commit_json": "api/commits/nbfigueroa_SCA-Boundary-Learning.json",
        "tgz": "tgz_SCA-Boundary-Learning.tar.gz",
        "alias_urls": [],
        "role": "Trains the RBF-SVM SCA boundary and performs CPSP support-vector pruning.",
        "equations": ["(24)", "(25)", "(28)"],
        "key_files": ["models/cpsp_models/2d_example.mat", "models/cpsp_models/2d_example2.mat", "models/cpsp_models/36D-24k_sparse_exact.mat", "libsvm/"],
        "executability": "MODEL_ONLY",
        "blockers": [
            "Trained models ship with the repository, but the training sets do not; retraining is not reproducible from this repo alone.",
            "MATLAB + mex libsvm toolchain required.",
            "No license file: redistribution of models is legally unclear (see license_policy).",
        ],
    },
    {
        "key": "SVMGrad",
        "owner": "nbfigueroa",
        "name": "SVMGrad",
        "api_json": "api/nbfigueroa_SVMGrad.json",
        "commit_json": "api/commits/nbfigueroa_SVMGrad.json",
        "tgz": "tgz_SVMGrad.tar.gz",
        "alias_urls": [],
        "role": "Analytical gradient of the RBF-SVM decision function w.r.t. the query point: implements (25).",
        "equations": ["(24)", "(25)"],
        "key_files": ["include/", "src/", "matlab/"],
        "executability": "BUILDABLE_AFTER_PATCH",
        "blockers": [
            "README gradient formula is missing a factor of 2 relative to a direct differentiation of the RBF kernel; the code is the authority, the README is wrong.",
            "Bundled training data is large (170 MB) and partially duplicated.",
            "No license file.",
        ],
    },
    {
        "key": "SESODS_lib",
        "owner": "SinaMirrazavi",
        "name": "SESODS_lib",
        "api_json": "api/SinaMirrazavi_SESODS_lib.json",
        "commit_json": "api/commits/SinaMirrazavi_SESODS_lib.json",
        "tgz": "tgz_SESODS_lib.tar.gz",
        "alias_urls": ["https://github.com/sinamr66/SESOSDS_lib"],
        "role": "Second-order DS library used by Multiarm_ds for the underlying single-arm dynamics.",
        "equations": ["(1)", "(2)"],
        "key_files": ["matlab/", "models/"],
        "executability": "NOT_EXECUTABLE_AS_IS",
        "blockers": [
            "Repository name in the paper's project page is misspelled `SESOSDS_lib`; the live repository is `SESODS_lib` (the misspelling 404s).",
            "MATLAB-only, no automated tests, large binary model set.",
        ],
    },
    {
        "key": "ML_toolbox",
        "owner": "epfl-lasa",
        "name": "ML_toolbox",
        "api_json": "api/epfl-lasa_ML_toolbox.json",
        "commit_json": "api/commits/epfl-lasa_ML_toolbox.json",
        "tgz": None,
        "alias_urls": [],
        "role": "Gaussian mixture regression / LPV machinery shared by LPV and Multiarm_ds.",
        "equations": ["(3)", "(4)"],
        "key_files": ["(metadata only, not snapshotted)"],
        "executability": "METADATA_ONLY",
        "blockers": [
            "Not snapshotted in this session (size-driven decision); only GitHub metadata captured.",
            "MATLAB toolbox; Python equivalents (sklearn GaussianMixture) are an ADAPTATION for any reimplementation.",
        ],
    },
    {
        "key": "kuka-rviz-simulation",
        "owner": "epfl-lasa",
        "name": "kuka-rviz-simulation",
        "api_json": "api/epfl-lasa_kuka-rviz-simulation.json",
        "commit_json": "api/commits/epfl-lasa_kuka-rviz-simulation.json",
        "tgz": None,
        "alias_urls": [],
        "role": "KUKA LWR URDF/RViz environment used for the paper's experiments and for distance queries during data construction.",
        "equations": [],
        "key_files": ["(metadata only, not snapshotted)"],
        "executability": "METADATA_ONLY",
        "blockers": [
            "Not snapshotted in this session; only GitHub metadata captured.",
            "ROS1 / RViz dependent, which conflicts with the Python-only scope of the proposed D082 reproduction.",
        ],
    },
]

LICENSE_POLICY = {
    "principle": "read for understanding, never vendor, never copy code into this repository",
    "lgpl_repos": ["Multiarm_ds", "LPV", "QP_IK_solver", "SCA_data_construction", "SESODS_lib"],
    "unlicensed_repos": ["SCA-Boundary-Learning", "SVMGrad", "ML_toolbox", "kuka-rviz-simulation"],
    "consequence": (
        "The four repositories that matter most for the numerical reproduction (QP_IK_solver, Multiarm_ds, "
        "SCA-Boundary-Learning, SVMGrad) are either LGPL-3.0 or carry no license at all. Any P5 implementation "
        "must therefore be a clean-room re-derivation from the paper's equations, not a port. Only numeric "
        "constants, file-format facts, and behavioural observations may be carried over."
    ),
    "model_artifacts": (
        "Trained .mat models are treated as opaque binary reference data for comparison only; they are not "
        "committed to this repository."
    ),
}

EXECUTABILITY_SUMMARY = {
    "BUILDABLE_AFTER_PATCH": ["Multiarm_ds", "LPV", "SVMGrad"],
    "PARTIALLY_REPRODUCIBLE": ["SCA_data_construction"],
    "MODEL_ONLY": ["SCA-Boundary-Learning"],
    "NOT_EXECUTABLE": ["QP_IK_solver"],
    "NOT_EXECUTABLE_AS_IS": ["SESODS_lib"],
    "METADATA_ONLY": ["ML_toolbox", "kuka-rviz-simulation"],
    "headline": (
        "0 of 9 repositories run out of the box. 3 build after patching, 1 is model-only, 1 is partial, "
        "1 (the QP backend, i.e. the paper's core solver) cannot execute at all because the CVXGEN sources "
        "are missing and the SCA path is dead code."
    ),
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_stats(work, tgz_name):
    if not tgz_name:
        return None
    path = os.path.join(work, tgz_name)
    if not os.path.exists(path):
        return {"available": False}
    with tarfile.open(path) as tf:
        members = [m for m in tf.getmembers() if m.isfile()]
        ext = Counter(os.path.splitext(m.name)[1].lower() for m in members)
        return {
            "available": True,
            "codeload_tarball": tgz_name,
            "tarball_sha256": sha256_file(path),
            "tarball_bytes": os.path.getsize(path),
            "file_count": len(members),
            "uncompressed_bytes": sum(m.size for m in members),
            "top_extensions": {k or "(noext)": v for k, v in ext.most_common(6)},
        }


def build(work):
    repos = []
    for spec in REPOS:
        api_path = os.path.join(work, spec["api_json"])
        commit_path = os.path.join(work, spec["commit_json"])
        meta = json.load(open(api_path))
        commits = json.load(open(commit_path))
        head = commits[0]
        entry = {
            "key": spec["key"],
            "canonical_url": meta["html_url"],
            "alias_urls": spec["alias_urls"],
            "default_branch": meta["default_branch"],
            "head_commit": head["sha"],
            "head_commit_date": head["commit"]["committer"]["date"],
            "head_commit_message": head["commit"]["message"].strip(),
            "license_spdx": (meta.get("license") or {}).get("spdx_id"),
            "api_size_kb": meta.get("size"),
            "role_in_paper": spec["role"],
            "equations_covered": spec["equations"],
            "key_files": spec["key_files"],
            "executability": spec["executability"],
            "blockers": spec["blockers"],
            "snapshot": snapshot_stats(work, spec["tgz"]),
        }
        if entry["snapshot"] is None:
            entry["snapshot"] = {
                "available": False,
                "unavailable_reason": (
                    "Not snapshotted in the P5 study session (only GitHub REST metadata captured); "
                    "treated as METADATA_ONLY."
                ),
            }
        repos.append(entry)

    return {
        "manifest_version": "1.0",
        "manifest_kind": "official_code_audit",
        "generated_for": "P5 paper study (pre-implementation gate)",
        "generated_by": "p5/tools/p5_manifest.py",
        "generated_at_utc": "2026-10-20T03:41:00Z",
        "paper": PAPER,
        "provenance_notes": [
            "Repository identity, default branch, SPDX license and HEAD commit come from the GitHub REST API "
            "as captured in .work/p5/api/. `SinaMirrazavi/*` and `sinamr66/*` resolve to the same repositories "
            "(the account was renamed; GitHub 301s the old paths).",
            "Source snapshots are codeload tarballs of the default branch at the recorded HEAD; sha256 is over "
            "the tarball bytes as downloaded during this session.",
            "Two repositories (ML_toolbox, kuka-rviz-simulation) were deliberately not snapshotted because they "
            "are out of scope for the numerical reproduction; they are recorded as METADATA_ONLY rather than "
            "silently omitted.",
            "No file in this manifest is vendored into the reproduction repository. See license_policy.",
        ],
        "repositories": repos,
        "executability_summary": EXECUTABILITY_SUMMARY,
        "license_policy": LICENSE_POLICY,
        "counts": {
            "repositories": len(repos),
            "snapshotted": sum(1 for r in repos if r["snapshot"].get("available")),
            "metadata_only": sum(1 for r in repos if not r["snapshot"].get("available")),
            "lgpl3": sum(1 for r in repos if r["license_spdx"] == "LGPL-3.0"),
            "unlicensed": sum(1 for r in repos if not r["license_spdx"]),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("P5_WORK"))
    ap.add_argument("--out", default="p5/evidence/P5_official_code_manifest.json")
    ap.add_argument("--check", nargs="?", const=True, default=False)
    args = ap.parse_args(argv)

    if not args.work:
        ap.error("--work is required (or set P5_WORK)")

    data = build(args.work)
    text = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"

    if args.check:
        target = args.check if isinstance(args.check, str) else args.out
        current = open(target, encoding="utf-8").read()
        if current != text:
            print("MANIFEST DRIFT: %s" % target, file=sys.stderr)
            return 1
        print("manifest: OK (%s, %d repositories)" % (target, data["counts"]["repositories"]))
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("wrote %s (%d bytes)" % (args.out, len(text)))
    print(json.dumps(data["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
