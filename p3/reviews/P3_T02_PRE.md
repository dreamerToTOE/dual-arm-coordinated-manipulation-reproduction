# P3-T02 PRE — Assembly-stage composition (Eq.23–26)

**Date**: 2026-10-20 | **Branch**: `reproduce-p3-paper-study-20261019`

```text
=== PRE-TASK REPORT ===
Task:                P3-T02 stage-command composition
Scientific objective: reproduce the four stage commands of Eq.(23)-(26) and the four documented
                     assembly-case stage sequences under externally prescribed switching
Minimum evidence:    composition oracle equality per stage; all four documented sequences traced
                     with correct stage attribution; boundary discontinuities reported, not hidden;
                     invalid schedules/unknown stages detected
Current scope:       stage_wrench, StageSchedule (contiguous, ordered), CASES from §V-C
Explicit non-goals:  automatic phase recognition (manual in the paper), contact state inference,
                     torques (T04), trajectory/insertion success (never claimed)
Attempt budget:      3
Preferred method:    stages.py + p3/oracles/oracle_control.py
Stop / escalation:   paper ambiguity about the case sequences (none: §V-C lists them)
Validation plan:     results/<run>/results.json + 2 figures
Known ambiguities:   A6 stage boundaries are ADAPTATION (manual switching in the source)
Need user confirmation: no
```

**Acceptance criteria**: explicit composition oracles; reproduce all four documented case stage
*sequences*; detect incorrect combinations, unknown stages, wrong ordering; **report** boundary
discontinuities instead of assuming they are illegal.
