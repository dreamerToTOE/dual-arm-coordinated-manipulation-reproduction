# P4 D084 S0 recovery checkpoint

Date: 2026-10-25 (Asia/Seoul)

This checkpoint covers S0 only. I read `docs/tasks/P4_D084_WINDOW_INDEX_20261023.md` and `docs/tasks/p4_d084/S0_SAFE_LOCAL_RECOVERY.md` from the D084 documentation tip before acting. No planner, IK, simulation, or numerical experiment was rerun.

## Git and process state

- Worktree: `/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full`, branch `p4-full-reproduction-pcs-study`.
- Initial local HEAD was `0b41236e5c1fed28e43eb0727f98dd1fd1d4d91e`; `origin/p4-full-reproduction-pcs-study` was `df11a5387149c7dae1ed601d161d33b6757ca2cf` (10 documentation commits ahead, no divergence). I fast-forwarded only; no reset, clean, checkout, or deletion was used.
- Current local and remote HEAD are both `df11a5387149c7dae1ed601d161d33b6757ca2cf` before this S0 rescue commit. The tracked tree was clean before staging recovered assets.
- Read-only process probes found no `bounded_difficulty`, `controlled_fig3`, `render_spatial`, planner, Isaac, MuJoCo, or other P4/D083 scientific process. A few stale `find` commands from the inspection shell remain; they are unrelated and were left untouched.

## Recovered and verified

The D083 inventory contains 408 D083-named files (106,016,413 bytes). The following reviewed research assets are staged for this checkpoint:

- Six untracked public source scripts in `scripts/p4_d083/` (the previously tracked `bounded_difficulty.py`, `bounded_difficulty_resume.py`, and `controlled_fig3.py` were not duplicated).
- Five public D083 report/data files under `reports/` (coverage JSON, difficulty findings, Fig.3 findings, and original/approved/actual CSV+Markdown). The two Chinese DOCX reports are preserved locally and excluded as private report artifacts.
- `reports/p4_d083_spatial_assets_20261022/` (18 files, 10,972,606 bytes): ABB II A1, ABB III A2/A2v2/A3/A4/A5, and the 36-frame saved-state GIF, with README, pre/post notes, and engineering-failure notes.
- `results/20261022_D083_spatial_visualization01/` (9 files, 1,723,484 bytes), `results/20261022_D083_delivery_verification01/`, the reviewed summaries/manifests/plots/qualifications in `results/20261022_D083_fig3_controlled02/`, the reviewed summaries/manifests/qualifications/independent paths in `results/20261022_D083_difficult02/`, and `results/20261023_D083_session_recovery02/` (11 files, 219,222 bytes). The Fig.3 and difficulty artifact manifests were checked against all present files; their raw archives remain local below. Key hashes: spatial manifest `0c6ac37c4e5a9185f42c14ee2150dee7004edb5a6784cc0d51792f8eb7b8de9e`; Fig.3 summary `bfe1f03236e0aea96f9da894e2b3970be5f8b68e382dd70d45472f6dd8ea5207`; difficulty summary `159f69327a0644a85a7cf1ed8a7efaf3405713c7e63ce29b1ba07a264bdefe32`; recovery snapshot `0e0a96d688be79b737b850b5257a08863d94bbb9d766c14b06824be0fc16517f`.
- Small execution logs in `work/d083_C/` and `work/d083_fig3_controlled_execution/` are also staged. All other untracked work remains in place.

The reviewed rescue set is 163 files (about 25.6 MB). The omitted raw archives are covered by the staged `artifact_sha256.json` manifests and remain available at their original local paths.

Spatial evidence is complete saved-path rendering only: II PCS/NR and III PCS saved paths are rendered, four III role switches are shown, 2,438+6 rendering FK calls were used, and new planner/IK/NR/RBS/collision calls are zero. Native III TCP mismatch remains 649/649 by the preserved evidence policy.

The controlled Fig.3 output is complete locally: 2,880 candidate and 900 bounded evaluations over 180 frozen pairs, 3,254 independently checked accepted local-call records, zero new planner calls, and conservative outer cost 86.29 wall / 90.71 process-CPU seconds against the 300/300-second Stage B cap. The initial private-path prepare failure remains preserved in the tracked `...fig3_controlled01/prepare_failure.json` and was not rerun.

The bounded PCS batch is complete locally: 36 registered calls total, 35 resume calls completed, 29 complete successes and 6 RSS timeouts, with the original C1/PCS/seed7 serialization-truncated call retained as UNKNOWN and never rerun. Combined Stage C cost is 17.00 wall / 19.84 process-CPU seconds against 180/240 seconds. Remaining scientific calls are zero.

The current `build_chinese_report.py` is retained and staged, but its SHA differs from the older recovery manifest because it is a later local report-only revision; this is recorded rather than treated as a scientific-result hash match.

## D084 stage state and handoff

| Stage | Actual local state |
|---|---|
| S1 ABB II visualization | Scientific assets complete and verified locally; D084 S1 post artifact not yet written. |
| S2 ABB III role switching | Scientific assets complete and verified locally; D084 S2 post artifact not yet written. |
| S3 controlled Fig.3 | Experiment complete locally; D084 S3 post artifact not yet written. |
| S4 bounded PCS difficulty | Remaining 35 calls complete; one original UNKNOWN preserved; D084 S4 post artifact not yet written. |
| S5 final report | Not complete. Draft DOCX/PDF/20-page render remain under `work/d083_report/`; no D084 final PDF was generated. |

The nominal unused envelopes are 213.71 wall / 209.29 CPU seconds for Stage B and 163.00 wall / 220.16 CPU seconds for Stage C, but these are not new execution authorization; historical unmeasured tails remain UNKNOWN. The exact next task after this checkpoint is **D084 S1 — ABB II visualization**, read-only packaging/verification of the recovered assets. Stop here; do not start S1 automatically.

## Preserved local-only inventory

No files were deleted. The excluded Fig.3 `raw_pairs/` archive (180 gzip files), difficulty `raw_planner/` archive (35 gzip files), two Chinese DOCX reports, `work/d083_report/`, `work/d083_render_runtime/` (including its sysroot), and prior D081/D082 scratch/runtime directories remain uncommitted and untouched. They are available for later review; private report and runtime files were intentionally not staged.

Rescue commit: `RESCUE_COMMIT_PENDING`
