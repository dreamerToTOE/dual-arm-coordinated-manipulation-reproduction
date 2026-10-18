# P2-T02: SE(3), soft contact and grasp statics

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T01 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Independently verify paper Eq.(1)–(12), especially right/left perturbation and body/spatial wrench adjoint; test Exp/Log, finite differences, grasp rank and transmitted/internal decomposition under pivot/tight/sliding modes.
- Evaluate historical modified Eq.(15) as a separate `ADAPTED_GEOMETRY` baseline; keep a derivation and a distinct `PAPER_LITERAL` candidate if realizable; no silent synonym claim.
- Use physically dimensioned units, full wrench force (N) and moment (Nm), rank/null-space tests, zero-power proofs, finite elastic preload, gravity and contact-shape edge cases.
- Parameter-sweep only bounded representative analytic cases fixed before results.

## Acceptance / 验收门槛
Exit: finite-difference identities, energy/force consistency and dual-model discrepancy table; all edge failures retained.

## Guard / 禁止事项
Cannot call contact PASS a full controller PASS.

## Minimum handoff
Provide `p2/reviews/T02_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T02_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
