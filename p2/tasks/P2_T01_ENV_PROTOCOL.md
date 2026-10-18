# P2-T01: Environment, parameter freeze and minimal baseline

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T00 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Record Python/NumPy/SciPy, g++, Eigen, Boost versions and optional MuJoCo. Prefer Python 3.10–3.12, pin actual working versions, not guesses.
- Audit imports for all `baselines/p2_pose_force`, `tests/test_p2_*`, `scripts/*p2*.py`; no dependency on removed P4 helpers.
- Select the specific accepted P2 protocol `configs/p2_closed_loop_protocol_v3.json` as historical baseline, without editing it; make an independently versioned new `p2/configs/paper_reference_v1.json`.
- Extract published Table I–II parameter values, object mass, timing, trajectory and tracking metrics. Missing dimensions/initializations must be UNKNOWN/assumed with sensitivity, never silently guessed.
- Verify imports, compile one isolated native kernel in temporary build directory if necessary, and execute only short smoke checks after PRE approval.

## Acceptance / 验收门槛
Exit: installation instructions, reproducible seed+versions, complete baseline parameter provenance, immutable config hash, smoke outcomes and failure logs.

## Guard / 禁止事项
No time-budget escalation / no starting 30-case suite.

## Minimum handoff
Provide `p2/reviews/T01_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T01_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
