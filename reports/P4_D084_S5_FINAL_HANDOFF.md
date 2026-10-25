# P4 D084 S5 final handoff

Date: 2026-10-25 (Asia/Seoul)

Status: **S0–S5 delivered; original-paper reproduction remains PARTIAL. STOP FOR USER REVIEW.**

S5 integrates existing, verified saved evidence. It executed zero planner, IK, RBS, collision, or qualification calls and regenerated zero research figures. Only document generation, PDF conversion, saved-file hashing, text extraction, and visual page review were performed. The original models, configurations, acceptance thresholds, coverage CSV, failures, and raw artifacts were not changed.

## Final deliverables and Git lineage

The final version is `reports/p4_d084_s5_final/P4_D084_P4证据整合最终报告_20261025_v5.docx` and the corresponding `.pdf` (15 pages). Earlier drafts are preserved locally and are not the final version.

| Asset | SHA-256 |
|---|---|
| Final DOCX | `e26f0e36001094cedd911877ab608c32d4aabc612b8192ccc1569d8093f359ea` |
| Final PDF | `3550e29e9f5df1f25bd21e9f69a9f78b4c2135f3fffff90d6fe495ffcb4f4c8a` |
| Unchanged D082 211×257 historical CSV | `e51494c1e37913b40a354ad5160f57a123e2f8a54740bbad72f1623117615d71` |

`reports/p4_d084_s5_final/manifest.json` binds the document, builder, 140-input hash map, QA record, and local-only inventory. `SHA256SUMS` provides a direct verification entry point. The report contains native Word mathematics inherited from the preserved D082 report, six unchanged source figures with captions and hashes, per-path provenance, frozen numerical parameters, statistical limitations, and a limited additive P4-T coverage appendix. It does not rewrite historical coverage cells.

| Stage | Complete commit SHA |
|---|---|
| Latest confirmed D084 documentation before recovery | `df11a5387149c7dae1ed601d161d33b6757ca2cf` |
| S0 recovered assets | `a660e14189ded7878685d9388c6241b65166ffc7` |
| S0 checkpoint amendment | `4b86552829177799f8bc22ca6a6cf113fe8943b0` |
| S1 ABB II | `613611d89cbc1e39e4ffbb9bd1e73f40c45285ff` |
| S2 ABB III | `882ff171f819d9dd2735edf04ac8f783289f3f7f` |
| S3 controlled Fig3 | `0ed66ec30d22a85f6a03088b3bfbfd4b21a50291` |
| S4 bounded diagnostic and S5 source HEAD | `bec0f9450a78a115c439368f0ca5ecfdb09b0cfb` |
| S5 report, builder, manifest and inventory payload | `d14ed936326ffd8ffe3de7b1534507e41ace6755` |

This handoff is a separate subsequent commit, so its containing commit is the final branch HEAD. The final response records that full SHA after push and remote verification. No self-referential commit SHA is embedded in its own file.

## Actual completion and accepted evidence

- **S0 complete:** recovered and preserved D083 scripts, configurations, saved outputs, figures, manifests, failures and partial artifacts. The exact recovery checkpoint is `reports/P4_D084_S0_RECOVERY_CHECKPOINT.md`.
- **S1 complete:** four Environment II saved paths (177/413/393/689 nodes), bound source certificates and a 3D figure. It adds no planning or independent scientific qualification.
- **S2 complete:** Environment III has 649 saved states, 15 milestones, 14 edges and four accepted-edge role switches at source nodes 179/248/392/492. Its original certificate is `PASS_649_DISCRETE_SOURCE_POLICY_PATH`, with `independent_path_qualified=false`; the report preserves this distinction. Native TCP mismatch remains 649/649.
- **S3 complete as archival packaging:** 96 frozen endpoints, 180 shared nonself pairs, 2,880 candidate calls and 900 bounded calls previously executed in D083. There are 2,358 candidate successes, 896 bounded successes, four retained m=1 failures, 3,254 independently qualified accepted local-call records and 97,577 discrete point references. The failed initial prepare remains preserved.
- **S4 complete as archival packaging:** all 36 registered calls were actually attempted previously: 35 complete artifacts and one original C1/PCS/seed7 serialization failure retained as UNKNOWN, never rerun. PCS has 8/8 complete successes plus one UNKNOWN; compatible fixed-0 9/9; NR 9/9; RSS 3/9 with six time limits. Twenty-nine complete successes have saved independent qualifications. Tree and final-path partition switches are all zero. All 1,696 RSS singular constructions are IK_UNREACHABLE; the three RSS successes are ordinary same-branch paths.
- **S5 complete:** final Chinese Word/PDF, source appendix, limited coverage summary, reproducible document builder, hash binding, page QA, local-only inventory, and this handoff.

The D082 main pilot remains 50 calls, 26 SUCCESS/24 TIME_LIMIT and 13 distinct successful paths reused across E0/E1. Historical RSS full planning remains 0/10 with 2,304 IK_UNREACHABLE singular constructions. No result establishes general PCS superiority, a genuinely difficult narrow-passage benchmark, original m=20, the original population or Bi-RRT runtime curves, native TCP equivalence, continuous CCD, dynamics, or hardware execution. Original Table I formal runs remain 0/22,500; the canceled 18,000-call plan is not reopened. IV/V/VI and other papers remain outside this delivery.

## Calls, budget and process status

| Frozen stage | Conservative used wall / CPU seconds | Cap wall / CPU | Nominal unused wall / CPU | Remaining calls |
|---|---:|---:|---:|---:|
| B / controlled Fig3, including failed prepare | 86.29 / 90.71 | 300 / 300 | 213.71 / 209.29 | 0 |
| C / bounded difficulty, including original failed call | 17.00 / 19.84 | 180 / 240 | 163.00 / 220.16 | 0 |

Unused arithmetic budget is not authorization for new calls, reruns, seed changes or repairs. S5 consumed **zero scientific calls**; document-rendering time is not added to Stage B/C. All approved scientific calls are already exhausted by identity, irrespective of unused time.

The final pre-commit `/proc` audit found **no active P4/D083 scientific process**. The independent audit also found no active repository writer. Unrelated processes were not stopped, signaled or modified. No reset, clean, untracked-file deletion, or irreversible cleanup occurred.

## Preserved files that remain only local

`reports/p4_d084_s5_final/local_only_inventory.json` explicitly enumerates every Git-listed untracked and ignored path at the final artifact snapshot, excluding the intended S5 deliverables: **1,531 untracked entries, 1,146 ignored entries, 894,429,300 regular-file bytes**. Untracked regular files carry SHA-256; ignored caches/runtime files carry path/type/size metadata, and symlinks retain targets. Nothing was copied into Git merely because it was present.

Material local-only assets include:

- `results/20261022_D083_fig3_controlled02/raw_pairs/`: 180 gzip files, 45,389,043 bytes; complete raw hashes remain in the original/package artifact manifests and the S5 inventory.
- `results/20261022_D083_difficult02/raw_planner/`: 35 gzip files, 8,269,303 bytes. The original failed `difficult01` archive is tracked and remains unchanged (51,080 bytes).
- `reports/P4_D083闭链规划受控实验与双ABB空间仿真研究报告_20261022.docx` and the corresponding `_20261023.docx` draft.
- Earlier S5 drafts under `reports/p4_d084_s5_final/`, all original and revised report drafts, PNGs/PDFs/text/logs under `work/p4_d084_s5_qa/` and `work/p4_d084_s5_render*/`, plus `work/build_d084_final_report.py` and the independent inventory snapshot.
- Prior `work/d081_*`, `work/d082_*`, `work/d083_report/`, `work/d083_render_runtime/`, S1/S2 render attempts, and the original recovery tarball `work/d082_recovery_20261022/initial_dirty_files.tar.gz` (30,615,405 bytes).
- Ignored build/runtime/private-reference/cache files and preserved V engineering snapshots, individually enumerated by the inventory. Private meshes and the private paper are not redistributed.

A fresh clone therefore contains the review report and packaged evidence, but not the local raw gzip archives or isolated runtime. Exact local paths/hashes are preserved for a later authorized archival transfer; no fresh numerical execution is needed for this delivery.

## Document reproduction and validation

Run only from the repository root. The first command verifies delivery hashes without running science:

```bash
sha256sum -c reports/p4_d084_s5_final/SHA256SUMS
```

For a separate document replay, use the Codex bundled Python and a **new** output name. The builder rejects existing outputs and checks all 140 frozen input hashes before authoring:

```bash
ARTIFACT_PY=/home/ubuntu2004/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
"$ARTIFACT_PY" scripts/p4_d084/build_final_report.py \
  --output work/P4_D084_report_review_replay01.docx
"$ARTIFACT_PY" work/d083_render_runtime/render_docx_isolated.py \
  work/P4_D084_report_review_replay01.docx \
  --output_dir work/p4_d084_s5_review_replay01 --emit_pdf
```

The standard skill renderer failed because this host lacks its required GLIBC_2.38/GLIBCXX_3.4.31. The existing D083 isolated LibreOffice/Poppler renderer then produced the actual final PDF. Its wrapper, runtime and hashes remain local and are recorded in the inventory/QA record. PDF replay elsewhere requires a compatible renderer; this is a runtime portability limitation, not a scientific failure.

Final PDF text was extracted and checked for the scientific counts, UNKNOWN and source-policy qualifications. All 15 substantive pages were visually inspected; the final pages are pixel-identical to the inspected iterations. Native equations, repeated table headers, unsplit rows and complete figures are present, with no blank or clipped document page. Frozen figures retain their original annotation spacing; exact switch labels also appear in body text. No unit/experiment suite was rerun for this document-only change.

## Exact next task

**User review of the final S5 Chinese report, evidence boundaries and remaining gaps. Stop after committing/pushing this handoff and verifying remote HEAD and clean tracked state. There is no automatic next scientific task.**
