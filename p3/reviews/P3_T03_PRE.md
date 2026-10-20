# P3-T03 PRE — Force/position selection and frames (Eq.27–28)

**Date**: 2026-10-20 | **Branch**: `reproduce-p3-paper-study-20261019`

```text
=== PRE-TASK REPORT ===
Task:                P3-T03 selection matrix Omega and wrench frame rotation
Scientific objective: Eq.(28) Omega = R_h diag([0 1 1]) R_h^T and the 6x6 selector of Eq.(27) are
                     implemented with correct dimensions, frame semantics and projection algebra
Minimum evidence:    symmetry, idempotence, rank, annihilated-axis identification, frame covariance,
                     paired twist/wrench power invariance, dimension checks; wrong-frame / transpose /
                     non-orthonormal / improper-rotation mutations detected
Current scope:       Omega (3x3), [[Omega,0],[0,I3]] (6x6), blockdiag(R_h,R_h) wrench rotation,
                     explicit task->hole relabelling for the push axis (A1)
Explicit non-goals:  torque magnitudes (T04), singular-Jacobian "failure" claims (a rank-deficient J
                     must NOT be rejected), norm-equality claims ||J^T w|| = ||w||
Attempt budget:      3
Preferred method:    control.py + independent oracle via the complementary projector I - n n^T
Stop / escalation:   none expected (A1 resolved without changing acceptance properties)
Validation plan:     results/<run>/results.json + 2 figures
Need user confirmation: no
```

**Acceptance criteria**: verify the precise position-selection operator from the source page
(3×3 Ω, 6×6 block with `I₃` in the rotational block); `Ωᵀ=Ω`, `Ω²=Ω`, selected-axis
annihilation, rotated-frame covariance, correctly paired twist/wrench power invariance;
detect wrong-frame / transpose / sign / non-orthonormal mutations; **do not** reject singular J;
make no norm-preservation claim for `Jᵀw`.
