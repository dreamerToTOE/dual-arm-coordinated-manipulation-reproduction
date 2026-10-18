# P2-T00: Historical frozen snapshot & completeness

**Initial status:** NOT_EXECUTED. **Predecessor:** none (branch setup). **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Verify current branch and a clean P4-unrelated change set.
- Independently compare every copied legacy file blob SHA against source commit 7787c75a8042af041579e5df0c9ac3e3ec4f6195; generate `p2/reviews/LEGACY_BLOB_CHECK.json` listing source/destination SHA, omissions and binary artifacts.
- Read accepted delivery, Eq.15 deviation audit, implicit Jacobian failure, 70/70, 35/35, 2/2 and the t=3.948s filter failure. Report what is truly usable, provisional and invalid.
- Read all eight pages of the original paper + Fig.1–9, Tables I–II; list unverified supplemental footage/URLs; no assumptions of accessible code or parameters.
- Define full equations-to-code-to-experiments index and mark legacy 30-run protocol vs paper E01–E09 separately.

## Acceptance / 验收门槛
No simulation; Git/JSON static verification only. Exit: every imported blob accounted for, core old failures preserved, every paper experimental claim indexed, status still PARTIAL. Stop if copy mismatch.

## Guard / 禁止事项
No experiment run; original P4 untouched.

## Minimum handoff
Provide `p2/reviews/T00_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T00_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.
