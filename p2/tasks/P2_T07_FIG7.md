# P2-T07: Fig.7 high internal-moment motion

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T06 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Reproduce paper high-moment object maneuver, compare pose-only vs combined controllers at identical start pose, trajectory and contact properties.
- Track force in N and internal moment in N*m separately, with mean/RMS/peak across paper-aligned intervals; independently compute wrench balance.
- Compare author-reported approximately 80% internal moment reduction **only** after defining matching interval/definition and units. State sensitivity to altered parameters and do not tune toward 80%.

## Acceptance / 验收门槛
Exit: independent controlled paired trajectories and reproducible figure/metrics; otherwise report trend-only or non-comparable.

## Guard / 禁止事项
High-moment plant-only output is NOT controlled comparison.

## Minimum handoff
Provide `p2/reviews/T07_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T07_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
