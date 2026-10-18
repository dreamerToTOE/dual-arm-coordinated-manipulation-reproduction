# P2-T03: Independent integrated object/contact plant

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T02 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Audit old 42-dimensional state dynamics and native implicit Lie midpoint solver (paper Eq.(13)–(16)); confirm old 70/70 checks and preserved prior FD oracle failure provenance.
- Reproduce independent COM Newton/Euler dynamics and soft contact under gravity; no desired-pose or force-controller target injected directly into the plant.
- Fixed nominal, high-moment, sliding/free-motion initial conditions: run bounded 5s integration with full/well-stated half-step comparison; check energy/drift/contact wrench plus solver convergence.
- Validate alternative backend/ODE reference at at least two time steps; do not adjust integration tolerances retroactively.

## Acceptance / 验收门槛
Exit: actual integrated state/force/time histories and error convergence, model discrepancies documented, no oracle resets.

## Guard / 禁止事项
Qualified plant does not establish IESEKF/control.

## Minimum handoff
Provide `p2/reviews/T03_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T03_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
