# P2-T06: Fig.6 four-way original ablation

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T05 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Freeze one geometric trajectory/time/seed set (including 7s and 13s activation and any 76s waypoint event backed by paper), object A/nominal grasp, common sensor noise and integrator.
- Run **exp1 pose only**, **exp2 wrench only**, **exp3 both**, **exp4 both with intentional true-vs-assumed stiffness mismatch**; one initial equivalence case then a modest predeclared seed replication, not an unexplained 30/18,000 batch.
- Output synchronized plots `position_error_m`, `orientation_error_rad`, `internal_force_N`, plus `internal_moment_Nm` where non-negligible; compare paper qualitative and quantitative observations with intervals and missing parameters clearly noted.
- Preserve runs that fail, stop early or time out; no stitching across failed prefixes.

## Acceptance / 验收门槛
Exit: four finished runs or explicit FAIL/BLOCKED each; fair comparison table and overlays vs published Fig.6 (not synthetic imitation).

## Guard / 禁止事项
Never cite 35/35 component checks as exp1–exp4 success.

## Minimum handoff
Provide `p2/reviews/T06_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T06_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
