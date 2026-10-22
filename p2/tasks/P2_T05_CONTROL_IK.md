# P2-T05: Pose-force controllers + joint-level inversion

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T04 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Verify Eq.(19)–(25) as published: W/H projector, force gain, local stability assumptions, SE(3) pose error/twist frame, no unreported normalization or extra force term.
- Implement/audit Eq.(26) with actual 7-DOF model or clearly identified surrogate and correctly dimensioned Jacobian, pseudoinverse, null-space, singularity damping, per-mode transmitted twist and joint limits; note historical ideal-Cartesian-endpoint limitation.
- Closed loop uses `hat X` from estimator rather than plant truth. Apply 7s wrench-on and 13s pose-on timing when following original paper, along with paper trajectory phases.
- Check local force decay with perturbations, position/attitude tracking, max forces, torques, saturation, timing and zero external force controls.

## Acceptance / 验收门槛
Exit: completed estimated-state controlled case through reference waypoints without domain bypass, plus joint-level evidence and both error channels.

## Guard / 禁止事项
If original robot model unavailable, mark joint model SURROGATE; no claim original-hardware parity.

## Minimum handoff
Provide `p2/reviews/T05_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T05_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
