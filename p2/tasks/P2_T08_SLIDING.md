# P2-T08: Fig.9 pivot/sliding & changing wrench subspace

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T07 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Model grasp-pad compliance and friction/contact interfaces; implement original H/mode switching and actual tool-object relative sliding, not merely a changed H rank.
- Independently test release/friction thresholds, frictional wrench power, contact persistence, discontinuity, no teleportation and mode-trigger causality.
- If feasible run MuJoCo physics contact model with transparent tuning and contact sensor readback. Compare C slide distance/trajectory, endpoint pose and bilateral grasp forces with Fig.9.
- If soft-pad physics fidelity is insufficient, retain honest `NUMERICAL_MODE_TEST` and mark `PHYSICAL_SLIDE_NOT_VERIFIED`, retaining this experiment in completeness ledger.

## Acceptance / 验收门槛
Exit: numerical mode behavior and credible contact physics validation separately labelled; no fake contact forces.

## Guard / 禁止事项
No object ghosting or direct pose overwrites.

## Minimum handoff
Provide `p2/reviews/T08_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T08_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
