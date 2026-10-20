# P3-T06 PRE — Deterministic numerical integration of Eq.16–28

**Date**: 2026-10-20 | **Branch**: `reproduce-p3-paper-study-20261019`

```text
=== PRE-TASK REPORT ===
Task:                P3-T06 deterministic stage-script integration
Scientific objective: route every stage command of all four documented case sequences through the
                     same independently validated pattern -> composition -> selection -> torque
                     pipeline and show finite, clock-consistent, complete command/torque timelines
Minimum evidence:    per-sample oracle equality for tau and w; every documented stage exercised;
                     clock monotonicity; boundary alignment; no dead/unexercised branches;
                     determinism (bitwise identical rerun); CSV traces with units
Current scope:       four cases, 0.01 s grid, TEST_FIXTURE state trajectory and gains
Explicit non-goals:  rigid-body/contact dynamics, peg motion, Fig.9/Fig.11 trajectory reproduction,
                     hardware success rate, any claim of insertion success
Attempt budget:      3
Preferred method:    run_t06_integration.py reusing T01-T04 production modules and oracles
Fallback method:     coarser grid if runtime exceeds 60 s (not expected)
Stop / escalation:   if a documented stage cannot be exercised at all
Validation plan:     results/<run>/{results.json, case*_trace.csv} + 2 figures
Need user confirmation: no
```

**Acceptance criteria**: trace Eq.16–28 through all applicable stage sequences; generate finite
command/torque timelines, per-stage comparisons and plots with units; detect missing stage commands,
clock/frame inconsistencies, dead or unexercised branches; **do not** claim reproduced object motion
or original success statistics.
