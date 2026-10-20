# P3-T04 PRE — Feedforward torque law (Eq.27)

**Date**: 2026-10-20 | **Branch**: `reproduce-p3-paper-study-20261019`

```text
=== PRE-TASK REPORT ===
Task:                P3-T04 full arm torque law
Scientific objective: every source-confirmed term of Eq.(27) is implemented with the paper's
                     ordering and frames, and no measured-force feedback is added
Minimum evidence:    independent loop oracle equality; term-by-term decomposition; position term
                     annihilated along the push axis; virtual work (J^T F)^T qdot = F^T (J qdot);
                     affine response in the feedforward wrench; input mutations (sign, frame,
                     selector, damping, gravity, friction) detected; singular J accepted
Current scope:       J^T[[Omega,0],[0,I]]K_p dx + J^T[[R_h,0],[0,R_h]]w - D qdot + tau_g + tau_f
Explicit non-goals:  robot dynamics, actuator limits, force sensing (absent by design),
                     joint-space redundancy resolution beyond a fixed J
Attempt budget:      3
Preferred method:    control.arm_torque / torque_terms + oracle_control.torque (index loops)
Stop / escalation:   none expected
Validation plan:     results/<run>/results.json + 2 figures
Need user confirmation: no
```

**Acceptance criteria**: reproduce every source-confirmed term preserving the ordering and frames
of `J`, `R_h`, position command, damping, gravity and friction compensation; independent numerical
oracle; virtual-work identity; affine response to feedforward wrench for fixed state; inject
sign/frame/control-term mutations; verify **no measured external force feedback** was added;
singular `J` need not make `Jᵀw` diverge.
