# P4 D084 S4 post-task — bounded PCS difficulty diagnostic

Date: 2026-10-25 (Asia/Seoul)

S4 is complete as a read-only packaging task. I read the D084 index, S4 card, the frozen D083 preregistration, configuration, failed-first-call artifact, resume source, and S0 checkpoint. The existing `difficult02` result was verified; no planner, RBS, IK, collision, or numerical call was rerun.

## Delivered

`reports/p4_d084_pcs_difficulty/` contains the 36-row planner ledger, method and paired summaries, independent qualifications and paths, condition diagnostics, RSS singular audit, cost binding, source/config hashes, and diagnostic plot. The 35 raw planner gzip files remain at their original local path and are covered by the complete artifact manifest.

The frozen batch has 36 registered calls, 35 complete artifacts, one UNKNOWN serialization failure, and 29 independent successes. PCS is 8/8 among complete artifacts plus one UNKNOWN; compatible fixed-0 is 9/9; NR is 9/9; RSS is 3/9 with six time limits. No tree or final-path partition switches were observed. The batch did not establish a hard scene or PCS superiority.

External cost is 17.00 wall / 19.84 process-CPU seconds including the original failed call, within 180/240. The original first call was not rerun. No P4/D083 process is running; unrelated processes in other workspaces were left untouched.

S4 has no remaining scientific calls. The exact next task is **D084 S5 — final report and handoff**. Continue automatically as authorized, but preserve all limitations and do not claim full-paper completion.
