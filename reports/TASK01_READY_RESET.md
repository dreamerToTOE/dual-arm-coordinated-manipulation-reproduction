# TASK01 — READY / Reset

## 2026-10-08 current: BLOCKED_BY_SHARED_HOLD_SEMANTICS — no reset trials

Latest user instruction supersedes older plans: four safety snapshots only, **zero reset repetitions**. FreeCube/no holdingconstraint falls2.725005mm at START in one original step, not already-stably-sharedheldSTART. No stableREADY, sharedgrasp/suction stability or deterministicheldreset claim. Recorded14q unchanged/notFROZEN; thresholds PENDING_USER_REVIEW.

Additional launcher-only attempt also fails safety at TARGET292 (leftlink7/deepwall−3.016427159mm contact), immediate STOP; raw right contact negative too. **Benchmark A reset count0; Benchmark B reset count0.** No5+5 or other repeats, attachment mechanism or force/drive/friction/suction tuning. [Exact run](TASK01_CRITICAL_SAFETY_COMMAND_RERUN.md).

TASK01 PARTIAL / safety FAIL / READY BLOCKED_BY_SHARED_HOLD_SEMANTICS. User must separately choose collision response and held-start representation: existing suction, benchmark rigid/shared-object attachment, or another existing fixedhold mechanism. No automatic choice/retry. Lower entries preserve historical plans, not current authorization.

## 2026-10-08 latest: NOT_RUN — approved safety fallback incomplete

User approved one bounded controlled safety replay (START/PRE/state196/TARGET), then START and PRE_PUSH **five resets each only after the four-state safety gate**. The single GUI attempt saved START at step1/time0.01666666753590107s, with14q initialized from the recorded candidate (no newIK), then stopped at the added stdin execution-review barrier and outer120s timeout124. Otherthreecriticalstates and reset loops were not reached; no internalsummary/failure generated, noacceptedcriticalreview. [Actual report](TASK01_BOUNDED_CONTROLLED_REPLAY.md).

**Reset trial count: Benchmark A START0/5; Benchmark B PRE_PUSH0/5.** Do not relabel the first critical safety snapshot as a reset repetition or extrapolate repeatability from setter readback. Recorded14q candidates remain unchanged/notFROZEN.

One saved START snapshot contains pre-/post-step q/Cube/TCP and stable carriage frame[.91,0,.2,0,0,0,1]. Preqmax9.70629e-8rad; postqmax9.05020e-5rad, TCPposition0.096015/0.067458mm. Free dynamic Cube, no suction constraint, fell2.725005mm under originalgravity. This is **not stable shared-held READY evidence**. No gravity disabled/pose rewritten after the measurement, no physical drift hidden. Numeric reset acceptance thresholds remain PENDING_USER_REVIEW; no invented/widened threshold.

Approved controlled fallback budget1/1 consumed; allownedprocessesreaped and no subsequent simulator/source repair. Stopforuser before anyextra bounded terminal rerun. Wrench/force/suction-stability/P2/P3/fiveCube remain outside this round. TASK01 overall PARTIAL, not PASS CANDIDATE/FROZEN. Old entries below are preserved historical plans, not current mandates for exhaustive model parity.

2026-10-08. Status: **NOT_RUN_PENDING_MODEL_PARITY**.

Current governance correction: **NOT_RUN_PENDING_RUNTIME_ACCEPTANCE_EVIDENCE / FALLBACK DECISION**, not indefinitely gated on perfect zero-stepnativequeries.09 actual originalreload returnedleftq all0 andstopped, rightreloadunobserved/callback0; no READYtrial. Recent07/08/09 same-rootbudget exhausted andstaticseriesstopped. Proposed smalltargetedvisiblecontrolledreplayplus≥3START/PREreset withtruepoststep time requiresuserapproval; unexecuted/no PASS/FROZEN. Earlier entries below arehistorical plans anddo not authorizeautomaticcontinuation. [Governance review](TASK01_GOVERNANCE_REVIEW.md).

Latest08 actual gate: zero steps/model/native/q/FK/TCP correct, but official non-physics refresh still did not prove link2 query target at START. Accepted0, no collision verdict or READY trial. 09 guarded original-physics handle rebuild prepared, not run, exact candidateq must be recovered without new schema/setter repair before any parity claim.

Current actual gate:07 reached zero actual physics callbacks and original native/output agreement, but stopped at START on an unverified moving native query (link2 inside-point miss), accepted0. This is not a verified geometric collision or a READY/reset trial. 08 disabled-physics subsystem refresh is prepared, not run; READY remains gated on complete model parity.

Latest checkpoint: 06 render-only path still triggered two direct physics callbacks at START and stopped with accepted0. No READY/reset data exists. 07 is prepared to initialize native handles without timeline PLAY/SDK implicit warm-up; exact candidate14q and all actual guards remain unchanged.

Current gate: 05 actually detected unintended physics dispatch during its paused GUI update and stopped before any accepted parity sample. Official render-only dispatch06 is prepared/not run. This invalid static attempt is **not** a repeated READY/reset trial; no post-step reset acceptance or scientific time record is claimed.

Latest actual GUI attempt03 stopped at START/index0 on stale USD collider output before any accepted parity sample. This is an engineering source-frame rejection, not a geometric collision verdict. Output-adapter04 is prepared but not yet run. See [parity report](TASK01_ISAAC_MODEL_PARITY.md). No repeated post-step reset has occurred and no READY state is claimed.

Later Oct8 checkpoint: 04 actually stopped on a Cube state-output `Quatf/Quatd` type mismatch, again accepted0, not a geometry failure; typed-output correction05 is prepared/not run. READY/reset remains NOT_RUN, and the earlier 03/04-plan text above is preserved as history.

Actual START/PRE_PUSH candidate 14q was recorded by the native full-chain geometry probe in [candidate YAML](../configs/benchmark/benchmark_v1.yaml) and [full-chain report](TASK01_FULL_SINGLE_CUBE_GEOMETRY.md). These are not FROZEN; future benchmark reset must restore them rather than randomly solve IK again.

Do not initialize dynamic held-Cube READY before original Isaac/MoveIt collision-model parity passes. Planned scope: repeated Benchmark A START and Benchmark B PRE_PUSH reset; record q error, Cube pose error, both TCP errors, carriage frame, true post-physics-step simulation timestamp/step and unintended contacts. A paused nominal static replay is not this test.

No force/wrench calibration or full controller; BUG001 belongs to TASK10-IS and does not block this gate. TASK01 can only become PASS CANDIDATE after actual parity and reset evidence, followed by user freeze approval.
