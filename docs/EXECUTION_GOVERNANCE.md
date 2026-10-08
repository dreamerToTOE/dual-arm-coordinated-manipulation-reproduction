# Execution Governance — Scientific Progress Over Engineering Loops

This document defines how coding agents decide **what is worth fixing now**.

## 1. The central rule
Every task must answer one scientific/benchmark question.

Do not optimize a diagnostic subsystem beyond what is required to answer that question.

The task specification must therefore separate:
- **Scientific objective**
- **Minimum sufficient evidence**
- **Non-goals**
- **Preferred method**
- **Fallback method**
- **Attempt budget**
- **Stop/escalation condition**
- **Deferred issues**

## 2. Blocker taxonomy

### TASK-BLOCKING
Without resolving it, the task's required scientific conclusion is invalid or unavailable.

### DEFERRED
Real issue, but explicitly owned by a later task.

### KNOWN LIMITATION
Uncertainty remains, but the current claim can be stated honestly with that limitation.

### LEGACY
Belongs to historical application/demo code and is not part of the current benchmark.

Only TASK-BLOCKING issues justify extending the current task by default.

## 3. Default engineering attempt budget
For one root blocker:
- Attempt 1: diagnose.
- Attempt 2: implement the most evidence-supported fix.
- Attempt 3: use a bounded fallback or alternative measurement route.

If still unresolved: stop and escalate.

Do not automatically create serial variants such as probe04/probe05/probe06 without a new user-approved reason.

## 4. Escalation decision
After the attempt budget is exhausted, answer:

1. What scientific statement were we trying to establish?
2. What has already been established?
3. What remains uncertain?
4. Does that uncertainty invalidate the task?
5. Is there a lower-cost evidence route?
6. Should the issue be deferred or accepted as a limitation?

The coding agent must recommend one of:
- **CONTINUE** — truly task-blocking and worth another approved attempt.
- **FALLBACK** — use another acceptable evidence method.
- **DEFER** — assign to a later task/bug owner.
- **ACCEPT LIMITATION** — record and proceed.
- **STOP FOR USER** — benchmark/theory decision required.

## 5. Evidence tiers
Use the lowest tier that is sufficient.

### Tier 1 — Sanity evidence
Enough to reject obvious model/interface errors.

### Tier 2 — Task acceptance evidence
Reproducible evidence sufficient for the task's PASS criteria.

### Tier 3 — Research-grade comparison evidence
Repeated, logged, fair evidence needed for a paper table/claim.

### Tier 4 — Subsystem equivalence / exhaustive proof
Only pursue if the research question explicitly requires it.

A TASK01 benchmark setup usually needs Tier 2, not Tier 4.

## 6. Examples for this repository

### TASK01 collision-model difference
Scientific requirement:
critical benchmark states must not show unexpected collision in the final Isaac environment.

Acceptable evidence:
targeted critical-state sanity/replay plus recorded model discrepancy.

Not automatically required:
proving exact equivalence of FCL STL and PhysX cooked convex hulls or perfect zero-step query-cache semantics.

### TASK10-IS force/wrench
Scientific requirement:
validated wrench semantics for P2's internal-force claims.

This **is** task-blocking for P2 Isaac evaluation, but it is DEFERRED for TASK01/P4.

### Legacy five-Cube Task27
Useful application/stress-test evidence, but LEGACY with respect to the one-Cube scientific benchmark.

## 7. Task writing rule
When creating or revising a task, use `docs/tasks/TASK_TEMPLATE.md`.
Technical details belong under Preferred Method; do not accidentally promote them into Requirements.

## 8. Progress review trigger
A task requires a governance review when any of the following occurs:
- same root blocker reaches three implementation iterations;
- task duration/commit count grows without new scientific evidence;
- new subsystem is added;
- acceptance criteria keep expanding;
- agent proposes a fourth probe/version for the same root issue;
- a later-task issue begins blocking the current task.

At that point, update STATUS with a short scope review before further coding.
