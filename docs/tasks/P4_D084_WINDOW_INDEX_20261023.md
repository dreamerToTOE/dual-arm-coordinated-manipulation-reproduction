# D084 — P4 Segmented Work-Window Index (2026-10-23)

**Decision:** The user reported repeated Codex/other-model session failures and requested continuation in independent, bounded conversations. This file is the new short **execution router**, not a request for more experiments or a revision of D083 scientific methodology. D082 remains delivered; D083's three-environment work remains the scientific target, with 18,000 planning runs canceled. Scope remains planar 20R + spatial dual ABB II and III; IV/V/VI, Isaac/ROS/FR3 and P1/P2/P3/P5 are excluded.

**Last scientifically updated remotely confirmed HEAD before D084 documentation:** `0b41236e5c1fed28e43eb0727f98dd1fd1d4d91e` (2026-10-22 UTC). This is a **baseline, not a target to reset to**. New commits may exist; always inspect remote/local HEAD, untracked files and active processes first.

## Evidence currently on GitHub (not a claim about local unfinished files)

- D082: 50 planar planner calls, 26 SUCCESS records = 13 distinct q trajectories reused across E0/E1, 24 TIME_LIMIT, 8490 checked discrete configurations. NR10/10; compatible fixed0 10/10; fullPCS6/10; fixed16/RSS0/10. PCS final accepted 20R solution partition switches 0; PCS superiority **not** supported. RSS random target attempts 2304/2304 `IK_UNREACHABLE` with root cause UNKNOWN.
- ABB II: four genuine saved qualified discrete paths (PCS177/413, NR393/689) plus separately documented SBL path, not new planning needed for a diagram.
- ABB III: 649 saved aligned-only discrete states; solution active-arm role sequence `[0,0,0,1,0,0,0,1,1,0,0,0,0,0]`, four true changes; 649/649 native TCP mismatches. No native exact or CCD proof.
- D083 Fig3: protocol and `controlled_fig3.py` committed. Remote `...fig3_controlled01/` holds **only** `prepare_failure.json` due to private symlink provenance path; scientific run not remotely qualified. A later second output directory was visible as **local untracked** in the prior run.
- D083 difficulty: three conditions/36 max calls frozen. Remote `...difficult01/` contains real first C1_PCS_seed7 execution but incomplete JSON due to NumPy bool serialization; prefix SUCCESS is not qualified. `bounded_difficulty_resume.py` is committed, designed for **remaining 35 only**. Later `...difficult02/` was reported as **local untracked**, not confirmed finished.
- D083 ABB visualization script/assets and Chinese report builder were reported as **local untracked** in a prior metadata receipt, not remotely delivered. Never infer their current local existence or quality without inspection. GitHub does not reveal live process state.

## Six one-window tasks, in recommended order

| Window | Task card (read only this card and 1–4 named local inputs) | Exit artifact | Allowed new science |
|---|---|---|---|
| **S0** | [Safe recovery](p4_d084/S0_SAFE_LOCAL_RECOVERY.md) | `reports/P4_D084_S0_RECOVERY_CHECKPOINT.md` and rescued files | **none** |
| **S1** | [ABB II visualization](p4_d084/S1_ABB_II_VISUALIZATION.md) | figures/manifest + `P4_D084_S1_POST.md` | **none** |
| **S2** | [ABB III switching](p4_d084/S2_ABB_III_ROLE_SWITCH.md) | figures/timeline + `P4_D084_S2_POST.md` | **none** |
| **S3** | [Controlled Fig3](p4_d084/S3_CONTROLLED_FIG3.md) | frozen paired data/plots + `P4_D084_S3_POST.md` | only registered Fig3 within remaining Stage B budget |
| **S4** | [Bounded PCS](p4_d084/S4_BOUNDED_DIFFICULTY.md) | remaining-call logs/results + `P4_D084_S4_POST.md` | only original remaining Stage C calls, never rerun failed first call |
| **S5** | [Final report](p4_d084/S5_FINAL_REPORT.md) | new Chinese Word/PDF and final handoff | **none** |

S0 is strictly first. S1/S2 can be swapped, S3/S4 can be swapped **only after S0**; do not run them in parallel against the same worktree. S5 runs last and must represent any missing/failed stages honestly. If S3/S4 already finished locally, their task becomes read-only verification and packaging, **not** automatic rerun.

## Context-budget discipline for EVERY new assistant/model window

1. **Start each new session with only the 8-line prompt in this index plus one stage ID.** Read *this index* and only the selected stage card; skip old master D079/D080 files and long 211-row CSV unless a concrete unresolved scientific question requires a small slice.
2. Keep one workspace and one active writer. Do not clone/rebranch or overlap writers. `git status --porcelain=v1 -uall`, `git log -3`, and process read-only probes precede action. If remote has new commits, integrate safely and do not reset local untracked state.
3. One task = one primary output = one short post-task report = commit/push = **STOP**. No next-stage code, no full PDF generation during S1/S2/S3/S4, no new planners during S1/S2/S5. **No general scope expansion or algorithm redesign.**
4. Limit session result reports to <=400 English words with direct paths, hashes, actual work, blockers and scientific denominators. Save detailed numerical tables/logs to files instead of chat. Avoid dumping huge terminal logs/entire scripts and old multi-column CSV into context; target relevant ranges using grep/head/tail or small parsers. If window starts to grow, save a versioned checkpoint and end it; resume same stage with suffix `S3b` etc.
5. Never overwrite frozen results or silently discard failures. New studies must use previously frozen seed/geometry/collision/threshold/budget. Preserved original journal/negative science remains primary evidence.
6. **Time and cost envelope are per historical stage, NOT per new window.** Stage B <=300 wall/300 process CPU, Stage C <=180 wall/240 process CPU including all previous attempts; UNKNOWN costs stay UNKNOWN. Any change needs user approval.

## Copy/paste into EVERY new Codex/DeepSeek local-agent conversation (replace STAGE_ID)

```text
You are continuing an existing P4 research repository, NOT starting over. Execute ONLY D084 stage STAGE_ID.
Repository: dreamerToTOE/dual-arm-coordinated-manipulation-reproduction
Branch: p4-full-reproduction-pcs-study
Local worktree (verify exists): /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full

First inspect git status/HEAD, local untracked files, active jobs and latest remote commits without destructive actions. Read ONLY:
- docs/tasks/P4_D084_WINDOW_INDEX_20261023.md
- docs/tasks/p4_d084/STAGE_CARD_FOR_STAGE_ID.md (resolve the exact stage filename from the index)
- files explicitly named in that stage card.

Do not load all D079/D080 history, the full 211-row coverage CSV or other stages into context. Preserve all D082/D083 results. Perform only the selected bounded task; if already complete locally, audit and package it instead of rerunning. Record exact results, real failures, budgets and hashes, commit and push a versioned task-specific POST/checkpoint, then STOP. Do not automatically begin another stage.
```

**Final governance:** Subtask posts are evidence checkpoints, not automatic acceptance of a paper claim. The final D084 scientific review and acceptance remain with the user. The distinction between full virtual task simulation and all-experiment author reproduction remains.
