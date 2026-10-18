# P2-T04: Visual/tactile fusion, IESEKF and failure diagnosis

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T03 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Begin **read-only replay** of frozen exp3/seed7 last-accepted estimator state and pad-domain failure at t=3.948s, including covariance, linearization domain and measurement causality; do not overwrite baseline.
- Audit paper Eq.(17)–(18): sensor frames, visual ArUco pose, contact forces, time stamps, robot-to-robot calibration, noise covariances, 42-state filter and right reset.
- Reproduce a nominal on-manifold IESEKF plus a fair conventional EKF comparator with same observations, noise and initialization; report bias/RMSE/NEES where valid, covariance SPD, dropouts and delay.
- Enforce no GT in feedback; GT allowed for metrics only. Re-enable full plant closed loop only after deterministic replay and preapproved small-run budget.
- If legacy Eq.15 correction or filter domain issues require new scientific model, version a **new** variant and keep paper/accepted code comparisons.

## Acceptance / 验收门槛
Exit: diagnostic root cause, independent filter trajectories past 3.948s without bypass, baseline/EKF comparable curves, honest failure and no hidden clamps.

## Guard / 禁止事项
After 3 justified repairs: BLOCKED with cause tree, not speculative tuning.

## Minimum handoff
Provide `p2/reviews/T04_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T04_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
