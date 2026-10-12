# TASK06 — P4 Constrained RRTConnect

Overall status: **PARTIAL / REVIEW RECORDED / STOP** (2026-10-12).
Core offline planner software: **PASS CANDIDATE**, explicitly accepted by user
at baseline `74d4276` under D054. Not full P4 or physical/continuous-safety acceptance.

## Scoped review decision (D054)

The software scope is accepted separately from the original D052 obstacle protocol.
The latter still lacks proof that the direct TASK05 connector is rejected for
COLLISION: status remains PROJECTION_JUMP; FCL was not queried at the rejected
midpoint. No historical status/metric/numerical limit is changed by this review.
All18calls,9repeatpairs,4NODE_LIMIT, both553node/148solutionedge successes and
all prior TASK03–05 negatives remain in their original artifacts. This is not
a retrospective PASS of the original suite or a formal Benchmark freeze.
[Review record](../../reports/TASK06_REVIEW_CLOSEOUT.md).

## Independent P4 evaluation backlog — not execution authorization

**P4-EVAL-OBSTACLE-DIRECT-COLLISION: DEFERRED / TODO.** A future independently
authorized evaluation may address collision-specific direct-connection rejection
and obstacle detour under a separately predeclared protocol. It must preserve
the original D052 failure, not overwrite it or reclassify it as PASS. No new
fixture, algorithm, parameter, experiment or TASK07 work is authorized here.
Stop after this documentation-only GitHub submission.

## Original bounded offline slice and preserved outcomes

User accepts TASK05 discrete FR3/FCL only; base91a1adc, branch
`task06-p4-constrained-rrtconnect`. Protocol877decd precedes experiments;
testedsource29a9d5c. Compose unchanged TASK03C/Jc/FK, TASK04NR-SVD and TASK05RBS/FCL
with TASK02 file logs; every inserted search edge validated. NoIsaac/ROSplanning
service/robot/controller/oldTask26/model/ACM/Benchmark change. NoTASK07.

Acceptance evidence: simple0→1 and nontrivial0→100 succeed for7/41/20261012twice;
private fixed obstacle0→100 succeeds twice at20261012 (553nodes/148solutionedges),
7/41twice exhaust600nodes. All9same-seed payload/path/status/counter repeats match.
Software/regressions/native limits and collision negativespass. **Unmet gate:**
directobstacleTASK05connector must reject specificallyCOLLISION, but actually
PROJECTION_JUMP (.0869493rad>.020rad), FCLnullatmidpoint. Nooutcome-driven change.
Overall remains PARTIAL, not PASS; D054 accepts only the core software candidate.
Review recorded; stop. TASK02IN_PROGRESS/DDEFERRED, BenchmarkDRAFT.

Artifacts: [pre-task/source audit and fixed protocol](../../reports/TASK06_PRE_TASK_PROTOCOL.md),
[POST-TASK REPORT](../../reports/TASK06_CONSTRAINED_RRTCONNECT01.md),
[search API/pseudocode](../../baselines/p4_closed_chain/CONSTRAINED_RRTCONNECT.md),
[raw metrics/logs](../../results/20261012_TASK06_constrained_search02/metadata.json).
Discrete point safety is not a continuous certificate; min distance UNAVAILABLE.

## Original future Benchmark outline (historical; not this slice's acceptance)

## Goal
Produce the first formal planning baseline for Benchmark A.

## Codex actions
- Integrate TASK04/TASK05 with RRT/RRTConnect.
- Use common collision interface.
- Log seed and planner parameters.
- Run fixed seed suite.
- Do not tune benchmark geometry.

## Metrics
planning success/time, path length, closure residual max/RMS, min distance, smoothness.

## PASS
Produces reproducible collision-free closed-chain paths on benchmark_v1 and a report comparing seeds/parameters.
