# P4 D084 / S4 — Complete bounded PCS difficulty diagnostic

**Single-window rule:** Complete ONLY this task; commit, push, give a short post-task report, then STOP. No automatic next stage. The overall task router is `docs/tasks/P4_D084_WINDOW_INDEX_20261023.md`. D084 changes orchestration only, not D083 scientific scope or author-paper facts. Scientific baseline pre-D084 `0b41236e`; always inspect current HEAD instead of assuming it.

**Purpose:** Safely resume the preregistered **three-condition** PCS difficult-scene diagnostic without rerunning lost call.**

Read `reports/P4_D083_DIFFICULT_PREREGISTRATION_20261022.md`, `configs/p4_d083/difficult_v1.json`, `results/20261022_D083_difficult01/engineering_failure.json`, `scripts/p4_d083/bounded_difficulty_resume.py`, and S0 checkpoint. If `results/20261022_D083_difficult02/` exists locally, inspect it FIRST; never relaunch jobs writing existing outputs. Original first call `C1_PCS_seed7` executed and produced an incomplete serialized artifact; observed textual SUCCESS prefix and 0.142819s solve are **NOT independent success evidence**. Mark `UNKNOWN_ARTIFACT_SERIALIZATION_FAILED`; never rerun or count as PASS.

Freeze same three prechosen endpoints, seeds [7,23,41], strategies PCS/endpoint-compatible fixed/NR/RSS, unchanged collision geometry and 1s per-call wall ceiling, total at most 36 calls. Resume script allows at most the **35 unexecuted calls**, following static scrutiny and SHA checks. Budget includes previous 0.94s wall and 2.23s CPU, total stage **180 wall /240 process CPU seconds**; account for other local runs and UNKNOWN. Preserve failures, actual feasible witness, genuine obstruction checks and independent path/partition switch tests; no reselect endpoints or force PCS victory. If condition is not proven hard, explicitly label as an archival endpoint diagnostic and do not claim universal hard-scene advantage.

**Deliverable:** complete or boundedly stopped trial ledger, remaining-call evidence, summary and plot with unknown denominator, actual runtime budget, `reports/P4_D084_S4_POST.md`. Commit/push; **STOP**. No Fig3, ABB imagery or PDF.

## Session exit checklist
- Record source commit(s), input/result hashes, completed/UNKNOWN/failed evidence, resource consumption and remaining block.
- Any files still only local must be explicitly enumerated. No irreversible cleanup.
- Push the stage report and artifacts if possible, verify remote HEAD/clean tracked state, then terminate work.
