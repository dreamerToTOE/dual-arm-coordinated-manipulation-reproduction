# D083 — P4 Final Simulation Supplement and Codex New-Session Handoff

> **D084 2026-10-23执行方法覆盖本文件的长会话入口**：本D083全文仍为科研目标和禁止项依据，但**新模型窗口不要直接一次性执行此全部内容**。改为阅读[六个短窗口任务路由](P4_D084_WINDOW_INDEX_20261023.md)，每个窗口选一个S0–S5，先提交短POST再交接/停止；Stage B/C预算跨窗口不重置。

**Authorized by user 2026-10-22. Highest-priority current P4 execution supplement after D082.**
**Branch:** `p4-full-reproduction-pcs-study` (reuse; do not create a new branch).
**Last confirmed remote baseline:** `4a0bc337089c2f4b97bb0f0d33125f65579e1b46` (D082 independently validated virtual simulation study). **Do not assume this SHA remains HEAD:** check local/remote and uncommitted work before doing anything.
**Scope:** 20R planar Environment I, ABB dual-arm Environment II, ABB dual-arm narrow-passage Environment III. **No new IV/V/VI experiment. No 18,000 formal trials, Isaac/ROS, hardware, P1/P2/P3/P5 execution, or FR3 adaptation.**

## 0. Safe recovery — mandatory for a new Codex conversation

1. Locate the existing local repository/worktree rather than cloning into a new copy. A previous recorded path was `/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full`; use it *only if it exists and is the correct repo*. Run `pwd`, `git rev-parse --show-toplevel`, `git status --short --branch`, `git log -8 --oneline`, `git worktree list`; inspect `git remote -v` and any running experiments. Inspect `git fetch` outcome carefully. Never discard uncommitted changes, never force-reset/clean or re-run frozen source solves as a recovery shortcut.
2. Read this file, `CODEX_START_HERE.md`, `AGENTS.md`, `docs/decisions/D082_FIVE_PAPERS_ONE_VIRTUAL_SIM_FOUR_ALGORITHMS_20261019.md`, `reports/P4_D082_DELIVERY_README_20261022.md`, `reports/P4_D082_ALGORITHM_FINDINGS_20261022.md`, `reports/P4_D082_SPATIAL_RECOVERY_20261022.md`, `reports/P4_D082_ORIGINAL_VS_APPROVED_VS_ACTUAL.md`, and the current source/experiment configuration.
3. Preserve D082's original Word/PDF, scientific data, negative results, hashes, saved source paths and certificates as immutable predecessors. New D083 assets must have new paths/IDs, no overwrite of historical evidence. Report which tasks were already completed locally but not yet committed, and resume at the earliest incomplete D083 milestone. Do not ask the user to re-explain old chat history.

## 1. Established evidence (do not count as new simulations)

- Planar 20R: 50 preregistered calls, E0/E1 × RSS/PCS/fixed-0/fixed-16/NR × five seeds, 26 successful call records = 13 unique joint-space trajectories duplicated in E0/E1; 24 timeouts; 8,490 independently checked discrete states, not continuous CCD.
- Full PCS success 6/10, fixed-0 success 10/10, NR success 10/10, fixed-16 and RSS both 0/10. Compatible fixed-0 is the fair benchmark; fixed-16 has structurally mismatched endpoint branches. Successful planar PCS paths contain **zero final solution partition switches**, and E0/E1 successful trajectories are identical; no complex-obstacle PCS advantage demonstrated.
- Fig.3 prior m groups used different configuration/pair populations, producing a confounded ablation; it must be corrected, not presented as causal evidence.
- ABB Environment II: already saved/qualified discrete paths RRT/PCS 177, RRT/NR 393, CBiRRT/PCS 413, CBiRRT/NR 689 nodes (plus an SBL path with separate certificate). Reuse actual q trajectories and model; do not rerun planning merely to draw them.
- ABB Environment III: saved RRT/PCS result with 15 milestones, 14 accepted solution edges, 649 discrete states and **four actual active-arm role transitions**. The recorded role sequence is `[0,0,0,1,0,0,0,1,1,0,0,0,0,0]`. **Only RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY qualifies; all 649 points retain native TCP mismatch.** Four role transitions are mechanism evidence, not proof of performance improvement. Render this accurately, never hide that limitation.
- RSS random singular generator: 72 requests/2304 constructions, all `IK_UNREACHABLE`; full RSS planning failed, root cause UNKNOWN. Retain the rank-2 manual fixture as distinct local mechanism proof, not random planner success.

## 2. Stage A — Existing spatial results first, no new planning

Use authentic saved geometry and joint paths for dual ABB Environment II and III. Produce reproducible 3D plots, optional short animation and clear labeled path frames. Show real robot base transforms, grasped bar/object, obstacle geometry and start/goal/waypoints; overlay quantitative closure/limits/collision evidence from correctly bound saved independent qualifications. All visuals must bind to source path sha/config/certificate. No generic robot poses substituted for source FK; no invented smooth physically executed trajectory. II should compare PCS/NR examples without unearned speed/success superiority. III must include a role-switch timeline and frame-by-frame illustration around the **four** switching edges. Clearly mark aligned/native-TCP and discrete/continuous safety limitations. Animation time is arbitrary playback, not physical dynamics.

**Deliverable:** Versioned plots (and animation if cost-effective), source-linked raw path/qualifier manifest, executable rendering instructions, evidence labels.

## 3. Stage B — Correct Fig.3 with a controlled shared population

Frozen once: an identical set of VALID closed-chain endpoint pairs and distance bins for every m. Exclude or independently count self-pairs. Use mathematically valid **nested** available partition sets (e.g. m=1,2,3,7,16 if valid; do not invent unavailable m=20). Preserve same geometry, pair set, tests, thresholds and per-method randomness where relevant.
Distinguish:
- **existential availability**: whether any of the first m partitions yields a legal local connection, expected to be nondecreasing for nested sets under identical deterministic rules;
- **finite-budget search result**: actual success under a bounded strategy and overhead;
- time/attempt cost and observed partition/IK-branch identities.

Require separate CSV/JSON of every pair × m × outcome, frozen seeds, real bins/denominators; plots of visibility by distance, visibility by m and local cost by m, showing uncertainty when meaningful. If expected monotonicity fails, inspect whether the implementation is actually comparing the same nested existential candidate set, before attributing it to P4's underlying theory. Contrast with original paper Fig.3 and disclose reconstructed 20R and missing original m20.

**Pilot size guidance, not unlimited compute authorization:** begin with a modest predefined shared pair pool consistent with prior 180-pair experiments, and calculate likely cost first. Stay within already approved local computational limits; ask permission if new science parameters or resource scope exceeds existing authorization.

## 4. Stage C — Bounded PCS difficult-scenario investigation

Use 20R or existing III, whichever can produce valid scientific evidence without rebuilding infrastructure. Freeze a small set of independent candidate conditions **before evaluating success**. A legitimate narrow passage must have valid endpoints, an actual obstruction to at least one candidate route and independent feasible-path evidence where possible. Do not choose a posteriori favorable runs or move obstacles until PCS wins. For a deliberately constructed mechanism witness, explicitly label it DIAGNOSTIC rather than unbiased general performance.

Compare full PCS, an **endpoint-compatible** fixed-partition baseline, NR, and RSS where scientifically applicable. Maintain identical task, valid geometry, collision model, joint limits and reasonably matched budget. Pre-register a small paired-seed set; count timeouts/failures and distinguish successful path partition changes from search-tree changes. If missing compatibility or feasibility invalidates the comparison, mark it UNKNOWN/NOT_COMPARABLE, not a method failure. Do not bypass original RSS's real sampling failure or force a winning narrative.

**Stopping rule:** make one limited, predefined investigation within the project's authorized compute budget. If no valid demonstration of PCS superiority results, document the negative result and why; do not escalate to IV/V/VI, unbounded search, posthoc seed selection or new 18k-scale batches. Continue to final report.

## 5. Stage D — Research-grade Chinese Word/PDF and archival handoff

Keep the D082 PDF/DOCX unchanged; generate versioned D083 Chinese report with a strong academic narrative:
1. Original paper problem and mathematical derivations (NR, APC, PCS, RSS, RBS).
2. 20R task, fixed Fig.3 methodology, actual algorithms and real sampled evidence.
3. 3D ABB Environment II true spatial planning and numerical trajectory results.
4. 3D ABB Environment III narrow passage and verified four role transitions.
5. PCS full/fixed/NR/RSS difficult-scenario comparison, actual success/failure, provenance and limits.
6. Original paper numeric results vs actual current reconstructed results and missing evidence, honest negative conclusions.
7. Final FR3 transferable mechanisms and preconditions only (NO current FR3 scene integration).

Use genuine figures and source-linked data. Create versioned `P4_D083_ORIGINAL_VS_APPROVED_VS_ACTUAL.md/.csv` inheriting all 211 historical items. Do not present aligned-discrete paths as native exact CCD-certified trajectories; do not relabel RSS or PCS performance superiority as successful if still unsupported. Retain original 22,500 and canceled 18,000 as historical obligations, not to run.

## 6. Prioritization, checkpoints and actual execution

Suggested order: **(A) spatial visualization → (B) corrected Fig.3 → (C) bounded difficult scenario → (D) final report**. These can share code/figure assets, but avoid a second infrastructure rewrite.

At the first progress report, give a short recovery table (existing, new, failed, next) and begin execution directly. Subsequent reports should feature actual newly created plots, scientific calls/denominators, source links, numerical errors and costs, not long management prose. Distinguish previously reused evidence from new D083 computations.

Target an overall incremental 4–7 day *planning goal* only; not a success promise or deadline justifying false results. If a blocker emerges, report the scientific root cause and proceed along unblocked work. Changes to physical geometry, collision policy, mathematical acceptance tolerances or major new runtime budgets require explicit user authorization, with negative historical evidence retained.

**Stop after versioned report/data/code/figures are pushed, send user a clear acceptance summary and wait for review. Do not auto-launch another P4 campaign, P1/P2/P3/P5, FR3, ROS or Isaac.**
