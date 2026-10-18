# P2-T10: Paper-versus-simulation final research audit

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T09 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Audit complete Eq.(1)–(26), Fig.1–9, Tables I–II, and available supplementary video using PAPER_TO_CODE and EXPERIMENT_MATRIX; all missing experiments retained with status.
- Compare target qualitative trend and quantitative metrics without fabricated numbers; label SIMULATED vs PAPER_REPORTED vs UNAVAILABLE data and measurement fidelity.
- Independently validate code/data SHA, seeds, config snapshots, reproducibility and failed runs; report derived vs actual paper formulas and model deviations (including Eq.15).
- Generate Chinese research report with mathematical derivations, algorithm architecture, representative plots and research limitations; classify numerical, independent physics and true hardware evidence separately.
- Suggest optional dual FR3 side-suction transfer as **separate future extension**, not evidence of P2 original reproduction.

## Acceptance / 验收门槛
Exit: reproducible audited deliverables, full scope-to-implementation table, quantitative agreement judgment per experiment, remaining issues and honest overall status.

## Guard / 禁止事项
Do not merge to main or proclaim FULL without user approval.

## Minimum handoff
Provide `p2/reviews/T10_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T10_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
