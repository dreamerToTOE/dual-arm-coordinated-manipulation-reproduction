# P3-T01 PRE — Perturbation patterns (Eq.16–22)

**Date**: 2026-10-20 | **Branch**: `reproduce-p3-paper-study-20261019` | **Base**: `5e43cf05`

```text
=== PRE-TASK REPORT ===
Task:                P3-T01 perturbation patterns
Scientific objective: the four paper patterns are implemented exactly as Eq.(16)-(22)
                     and the implementation is validated by mathematics independent of itself
Minimum evidence:    analytic agreement at prescribed times vs scalar closed forms;
                     time-domain invariants (constancy, zero mean, quadrature, radius);
                     axis/unit placement; rejection of invalid inputs; mutation sensitivity
Current scope:       push (19), rub (20), wiggle (21), spiral (22), general form (16)-(18)
Explicit non-goals:  contact forces, robot motion, stage composition (T02), numeric agreement
                     with the paper's experiments (no parameters published)
Attempt budget:      3 iterations
Preferred method:    production code in baselines/p3_peg_in_hole/patterns.py; oracle in
                     p3/oracles/oracle_patterns.py written as scalar closed forms (no imports)
Fallback method:     analytic scalar expressions at fixed sample times (already the oracle)
Stop / escalation:   source ambiguity changing the equations (none found in T00 audit)
Validation plan:     results/<run>/results.json + 2 figures
Known ambiguities:   A3 (a constant vs a(t)) resolved by Eq.(22) being explicit
Need user confirmation: no
```

**Acceptance criteria (from the review decision)**: source transcription audit (done in T00); exact
analytical spot checks; sample/time invariants; bounds only where the source justifies them;
reject non-finite/dimensionally invalid inputs; swapped sine phase/frequency/amplitude must fail;
`b = 0` is legal; `β < 0` must not be rejected.

**Implementation mapping**

| Eq. | Code | Note |
|---|---|---|
| (16) | `patterns.WRENCH_ORDER`, `COMPONENT_UNITS` | force x,y,z then moment x,y,z |
| (17)–(18) | `GeneralPattern.wrench` | `diag(a(t))·sin(t·b + c) + d` |
| (19) | `Push` | `d=[0,0,f_push,0,0,0]`, push along +z |
| (20) | `Rub` | only `mz`, `f_rub` is a moment (N·m) |
| (21) | `Wiggle` | `mx = f sin(vt)`, `my = f cos(vt)` (phase π/2 on component 5) |
| (22) | `Spiral` | `a1=a2=α sin(vt)+β`, `c2=π/2` |
