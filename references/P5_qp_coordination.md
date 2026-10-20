# P5 — Unified Coordinated Multi-Arm Motion Planning

Paper: *A Unified Framework for Coordinated Multi-Arm Motion Planning* (IJRR, 2018).

## Core method
- synchronous/asynchronous multi-arm task-space coordination;
- centralized inverse kinematics formulated as convex QP;
- joint-space self-collision avoidance;
- paper includes a learned/data-driven SCA boundary representation.

## Reproduction stages
### Core
- centralized dual-arm QP IK;
- joint position/velocity constraints;
- relative/synchronization tasks;
- collision-distance constraints using available FCL geometry.

### Paper-like extension
- reproduce learned SCA boundary only after the core QP baseline is stable and only if needed for scientific comparison.

## Fidelity warning
A QP using FCL distance constraints is a useful core adaptation but not identical to the paper's learned SCA model. Label the difference explicitly.

---

## Addendum (2026-10-20) — paper study result

Added after the full-text study; the staged plan above is **not** rewritten.

- PDF: IJRR 37(6):583–603, DOI `10.1177/0278364918765952`;
  SHA256 `6f367be45e0c925df64ec5e4ab3046e1de8aa96627c65ddb2fd71720d9eedc02`.
- The ordering "core QP first, learned SCA later" does **not** hold up scientifically. The learned
  boundary Γ, its gradient ∇Γ, the CPSP pruning and the 2 ms budget occupy roughly eight pages
  (Sec. 4–5) and are the paper's main contribution, not an optional plug-in. In
  `p5/P5_PROPOSED_REPRODUCTION_MATRIX.csv` the SCA tasks are therefore `MINIMUM_ESSENTIAL`.
- The "collision-distance constraints using available FCL geometry" bullet above is an
  **ADAPTATION**, not the paper's method; it is kept only as a baseline (task P5-T09) and must never
  be reported as an SCA reproduction.
- Official code: 0 of 9 repositories run out of the box; the QP backend (CVXGEN) is absent from
  `QP_IK_solver` and its SCA path is dead code. See `p5/P5_OFFICIAL_CODE_AUDIT.md`.
- Details: `p5/P5_PAPER_STUDY.md` §1.3.
