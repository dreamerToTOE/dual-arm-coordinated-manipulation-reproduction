# P2-T09: Fig.8 virtual four-object placement and video evidence

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T08 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Build virtual A/B1/B2/C placement model with the author's reported dimensions and support geometry; account for unavailable hardware mesh details and changed gripper physics.
- Recreate sequence and final slow contact placement with external wrench estimate; include Fig.9 sliding stage for object C.
- Target five predeclared repetitions with distinct initial seeds if feasible; record per-object position/angular errors and success, collision, peak contact wrench and video/gif/frames.
- Paper's <0.1mm caliper-limited claim is not a physically validated simulation precision target. Report measurement-resolution mismatch and physical fidelity bounds.
- Supplementary video still needs independent verification; do not invent missing event times.

## Acceptance / 验收门槛
Exit: all four placed under actual simulated contact plus 5 repeat metrics, or each missing subtask explicitly BLOCKED with reason.

## Guard / 禁止事项
No physical robot experiments.

## Minimum handoff
Provide `p2/reviews/T09_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T09_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
