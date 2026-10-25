# P4 D084 S3 post-task — controlled Fig. 3

Date: 2026-10-25 (Asia/Seoul)

S3 is complete as a read-only packaging task. I read the D084 index, S3 card, the frozen pre-task protocol, configuration, controlled-experiment source, and the S0 checkpoint. The existing `controlled02` output was verified; no prepare, execute, planner, RBS, IK, collision, or numerical call was rerun.

## Delivered

`reports/p4_d084_fig3_controlled/` contains the frozen pool and pairs, candidate and bounded outcome tables, per-`m` and distance summaries, independent saved-result verification, execution metadata, recommended plots, and a package manifest. The 180 raw pair gzip files remain preserved at their original local path and are covered by the complete artifact hash manifest.

The experiment has 96 frozen endpoints, 180 shared pairs, 2,880 candidate calls, 900 bounded calls, 2,358 candidate successes, 896 bounded successes, four retained `m=1` failures, and 3,254 independently qualified accepted local-call records. All shared-pair identities, candidate-union monotonicity, bounded first-success identity, and independent geometry checks passed in `saved_result_verification.json`.

The successful output reports 84.4633 s internal execute wall / 84.7020 s CPU; the outer conservative total including the failed prepare is 86.29 s wall / 90.71 s CPU against 300/300. Remaining scientific calls are zero for S3.

The result remains a finite reconstructed 20R proxy. It does not support the original author Fig. 3 population, Bi-RRT runtime, `m=20`, continuous CCD, or PCS-superiority claims. The original failed prepare artifact remains preserved and was never rerun.

No scientific process is running. The exact next task is **D084 S4 — bounded PCS difficulty**. Stop after the S3 commit and push; do not begin S4 automatically.
