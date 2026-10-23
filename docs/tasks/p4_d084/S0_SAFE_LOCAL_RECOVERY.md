# P4 D084 / S0 — Safe local recovery and handoff

**Single-window rule:** Complete ONLY this task; commit, push, give a short post-task report, then STOP. No automatic next stage. The overall task router is `docs/tasks/P4_D084_WINDOW_INDEX_20261023.md`. D084 changes orchestration only, not D083 scientific scope or author-paper facts. Scientific baseline pre-D084 `0b41236e`; always inspect current HEAD instead of assuming it.

**Purpose:** Rescue/qualify uncommitted local D083 work and prevent duplicate jobs. **No new numerical experiments or simulation.**

Inspect only the existing P4 worktree, initially recorded at `/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full` if present. Inspect `git status --porcelain=v1 -uall`, branch/log/remote/worktrees, recent D083 outputs and active processes. The confirmed pre-D084 remote scientific base was `0b41236e5c1fed28e43eb0727f98dd1fd1d4d91e`; do not reset to it, because newer D084 documentation commits are expected.

**Prioritize:** `scripts/p4_d083/render_spatial.py`, `reports/p4_d083_spatial_assets_20261022/`, `results/20261022_D083_spatial_visualization01/`, `results/20261022_D083_fig3_controlled02/`, `scripts/p4_d083/build_chinese_report.py`, `results/20261022_D083_difficult02/`. These were previously mentioned as local/untracked and **are NOT confirmed present or complete remotely**.

Determine for each whether it exists, is complete, was actually run, contains valid numbers, and can be safely versioned. Stage only reviewed research source/small results, never private papers, tokens, runtime sysroot, caches, giant checkpoints, or other worktrees' data. Verify SHA/manifest and check whether existing running process writes to any of them; do not terminate a live job without inspecting its owner and progress. Keep partial scientific output as partial; do not fabricate missing lines. If scientific data are too large, include a concise manifest with actual local path and preservation state and report that they remain local.

**Deliverable:** `reports/P4_D084_S0_RECOVERY_CHECKPOINT.md` with local HEAD, process status, stage A/B/C/D and untracked inventory, exact completed scientific calls, stage budget usage/unknown, rescued commit(s) and explicit per-stage next actions. Push reviewed rescue artifacts and report; **STOP**. No S1/S2/S3/S4/S5 in this window.

## Session exit checklist
- Record source commit(s), input/result hashes, completed/UNKNOWN/failed evidence, resource consumption and remaining block.
- Any files still only local must be explicitly enumerated. No irreversible cleanup.
- Push the stage report and artifacts if possible, verify remote HEAD/clean tracked state, then terminate work.
