# TASK01 — Governance Review / Engineering Escalation

Date: 2026-10-08. Status: **PARTIAL; static-query series STOPPED; fallback decision pending**.

## Authority and scope

User requested re-reading the updated GitHub governance and reassessment, explicitly rejecting default continuation of parity09. Main read the complete current [AGENTS.md](https://github.com/dreamerToTOE/dual-arm-coordinated-manipulation-reproduction/blob/0e3f8f5b25bac24cd75a477744d06150b76f0ddb/AGENTS.md) (243 lines) and [EXECUTION_GOVERNANCE.md](https://github.com/dreamerToTOE/dual-arm-coordinated-manipulation-reproduction/blob/0e3f8f5b25bac24cd75a477744d06150b76f0ddb/docs/EXECUTION_GOVERNANCE.md) (103 lines), plus CODEX_START_HERE, remote/local task/status, BENCHMARK_SPEC, P4 card and worktree status. Cloud main HEAD observed `0e3f8f5`; local task HEAD at review `a5dba59`. Git fetch over SSH/HTTPS failed, so the current authoritative governance was read via commit-pinned raw GitHub, **not** the stale local `origin/main` (`046c4ad`). No merge/reset of task records.

After the user's interruption, no new source edit, Isaac run, controller, physics integration, JointState initialization implementation, or new parity variant was made. Existing09 had already actually run and stopped; its previously PREPARED metadata and IN DESIGN descriptions must be superseded by actual negative evidence.

## PRE-TASK REPORT

- Task: TASK01 scope/governance review only.
- Scientific objective: minimal, stable, reproducible one-Cube common benchmark for later baselines.
- Minimum sufficient evidence: recorded nominal geometry/configuration; feasible approved A/B discrete chain; actual Isaac critical-state safety sanity; deterministic START/PRE_PUSH repeated reset with post-physics-step timestamps; user candidate review.
- Current scope: read-only evidence audit and append-only record correction.
- Explicit non-goals: perfect zero-step query semantics; exhaustive FCL/PhysX equivalence; new simulator integration layer; new probe/control/force-calibration work; five-Cube operation; benchmark/ACM/threshold changes.
- Attempt budget: same-root07/08/09 at least3/3 used; earlier01–06 not erased or used to reset the budget.
- Preferred method: static native query route; further development stopped.
- Fallback method: small critical-state controlled synchronized GUI replay, then repeated START/PRE reset; only a proposal, not run or pre-approved.
- Stop/escalation condition: budget exhausted; no new implementation without user decision.
- Expected files: six records, task scope review, three report status corrections, this review,09 actual metadata/summary.
- Validation plan: compare existing frozen source snapshots, negative logs and sampled geometry artifacts; no new experiments.
- Risk: actual new-chain Isaac collision/reset acceptance evidence still missing.
- Need user confirmation: yes, for the proposed evidence-route replacement and one bounded fallback attempt.

## ENGINEERING ESCALATION

**Scientific question:** Does the approved one-Cube setup provide a feasible, safe-enough-to-benchmark, reproducible common environment? It is not a research question about perfect PhysX query-cache semantics or exact STL/cooked-hull equivalence.

**Already established:** A136/136 and B157/157 sampled nominal states pass the independent IK/bounds/shared-grasp/full robot FCL and Cube-environment geometry gates. There are293 records/292 unique states, exact PRE14q seam, per-state signed FCL distances/pairs, and captured deterministic START/PRE14q. Minimum joint margin0.461828rad; wrist/tool-environment minimum2.212219mm at TARGET (`left_fr3_link7` / `carriage_deep_wall`); all-pair minimum0.999669mm is the intended Cube/tool gap. None of this is a timed trajectory, continuous collision certificate, or Isaac stability proof.

**Unknown:** Actual unexpected collision at the critical benchmark states in the final Isaac model; reliable repeated post-step START/PRE reset. No new-chain PhysX collision verdict was established in07–09. READY/reset has not run.

**Why it matters:** FCL has only approximately2.2mm wrist-wall clearance, while Isaac uses original cooked convex hulls. It is inappropriate to declare TASK01 PASS using only FCL or empty/unverified scene-query results. But fixing the query subsystem itself is not necessary if a valid lower-cost task-acceptance measurement route exists.

### Attempts for the same evidence blocker

| Attempt | Actual observation | Conclusion |
|---|---|---|
| 07 diagnosis | No PLAY; callbacks0; native/FK/USD pose guards pass; original link2 interior-point query returns no exact target hit | Query freshness unverified; no collision verdict |
| 08 evidence-based fix | Official flush + stage update with physics disabled; callbacks0; same link2 query miss | Fix did not establish safety evidence |
| 09 bounded alternate | Original native handles rebuilt; left7q read as all0 before any setter, max candidate difference2.43079576661854rad; callbacks0; immediate stop | State restoration failed; right reloadedq not read; no collision verdict |

09 source commit `a5dba59`, SHA `803b1e9ef6c24c6baf92ded33fcaa92311c41141636c831bc6f731a2ad7ce229`; [actual metadata](../results/20261008_TASK01_isaac_model_parity09/metadata.json), [summary](../results/20261008_TASK01_isaac_model_parity09/summary.json). 70 software tests/0.148s passed, not simulator acceptance. Wrapper exit0 is not PASS. The owned GUI exited/reaped; no surviving Isaac/MoveIt experiment. Earlier01–06 negative engineering runs remain historical evidence. Total parity directories01–09 must not be represented as an unused/new budget.

### Blocker ownership

| Issue | Classification | Action |
|---|---|---|
| Zero-step native query synchronization / exhaustive FCL–PhysX equivalence | KNOWN LIMITATION | Preserve negative evidence; stop subsystem perfection; not an independent TASK01 requirement |
| Missing actual critical-state collision sanity and repeated START/PRE reset | TASK-BLOCKING acceptance-evidence gap | Obtain bounded Tier2 evidence through an approved alternate route; do not claim PASS now |
| BUG019 original STL/cooked-hull discrepancy | KNOWN LIMITATION | Keep discrepancy/risk recorded; no RESOLVED/equivalence claim; actual critical safety gap remains separate |
| BUG001 force/TCP wrench and gravity-inertia calibration | DEFERRED | TASK10-IS owner; non-blocking for TASK01/P4 |
| Old five-Cube sequencing/retreat/fixture reliability | LEGACY | Preserve history; do not use as the current one-Cube prerequisite |

**Is the engineering root itself still task-critical?** No. The required runtime safety/reset evidence is task-critical; the particular zero-step query implementation is only a method.

**Lower-cost route proposed:** Tier2 targeted visible GUI controlled/synchronized replay of START, PRE_PUSH, insertion10/30/50/70/100%, and distinct minimum-clearance states selected from the already recorded chain. Deduplicate identical states; label actual sampled fractions honestly. Restore the captured14q, not new random IK. Record actual q/Cube/TCP/frame, unexpected contact/overlap pairs and post-physics-step simulation time. Treat expected Cube support/deep-wall touch separately from unintended robot/tool contact. This is not force/wrench calibration or a claim of full dynamic stability/continuous collision freedom. Reuse existing GUI/READY infrastructure; no new platform integration layer.

**Proposed bounded allowance, requiring approval:** one fallback implementation/GUI acceptance attempt, visible run no more than120s, repeated START/PRE reset at least3 times each within that allowance. If input/state/contact measurement cannot be validated, or any unexpected collision occurs, stop and report the exact recorded failure; do not autonomously add another diagnostic variant, alter the tool/carriage/ACM, or relax thresholds. If the existing reset path cannot meet that bound, report the limitation before extending it.

**Recommendation:** STOP FOR USER now; ask to use FALLBACK + ACCEPT LIMITATION. Do not mark TASK01 PASS CANDIDATE until runtime critical-state/reset evidence meets the unchanged scientific gates. No FROZEN without user confirmation. The latest instruction changes the evidence strategy, not benchmark geometry or paper theory.

## POST-TASK REPORT

- Task: TASK01 governance review.
- Status: PARTIAL; engineering-series stopped, user fallback decision pending.
- Scientific objective/minimum sufficient evidence achieved: nominal geometry yes; full TASK01 acceptance no.
- Completed: full updated-rule reading; evidence/budget/ownership audit;09 actual negative record correction; proposed finite Tier2 path.
- Files changed: this report,09 metadata/summary/selected rejection, three report status notes, six records, task scope note. No source/config/runtime geometry edits after the user override.
- Commands: read-only git status/log/remote/fetch attempts and commit-pinned GitHub reads; existing JSON/log audit; diff check. No new simulator/test experiment after override.
- Results/key metrics: A136/B157 nominal PASS;07–09 accepted0;09 callbacks0 and leftq reset discrepancy2.430796rad; right reload not observed. Prior09 software70OK is retained, not rerun under this review.
- Blockers: classifications in table above.
- Attempt budget used: at least3/3 for same root; escalation required yes, not automatically replenished by a different sub-error or method.
- Paper fidelity: [ORIGINAL] no baseline claim; [ADAPTATION] unchanged dual-FR3 benchmark; [ENGINEERING] scope/record correction and proposed evidence route; [DEVIATION] none executed; [EXPERIMENTAL] previous negative engineering probes, not paper results.
- Records: STATUS, WORKLOG, EXPERIMENT_LOG, BUGS, DECISIONS, USER_FEEDBACK updated append-only.
- Open risk: actual critical-state safety/reset not established.
- Next step: user approves or revises the one bounded fallback; no automatic parity10.
- Git: `task01-benchmark-draft`; starting HEAD `a5dba59` was previously pushed; this review is a local record update, not a successful cloud-sync claim. Preserve pre-existing untracked01/02 launch logs and raw data.
