# CODEX ENTRY — P2 ONLY

This file is the startup handoff for any **future** Codex session. Creating this file does not start Codex.

1. Confirm checkout of branch `reproduce-p2-numerical-simulation-20261018`. If you are in another branch, do **not** modify it; report and stop.
2. Read `p2/AGENTS.md`, `p2/README.md`, `p2/LEGACY_EVIDENCE.md`, `p2/EXPERIMENT_MATRIX.md`, `p2/PAPER_TO_CODE.md`, and `p2/tasks/INDEX.md`.
3. Read the frozen P2 reports, especially `reports/P2_DELIVERY_ACCEPTANCE_FREEZE.md`, `reports/P2_CLOSED_LOOP_POST_TASK.md`, `reports/P2_CONTACT_GEOMETRY_POST_TASK.md`, and `reports/P2_ORIGINAL_PAPER_AUDIT.md`. Never infer successful full-paper reproduction.
4. Do **only** `P2_T00_PROVENANCE.md` first. Prepare a pre-task scope/inputs/budget/checklist. Do not skip into experiment runs or invoke simulations until that task's gate passes.
5. For each task, produce `p2/reviews/Txx_PRE.md`, `p2/reviews/Txx_POST.md`, and machine-readable run manifests. Preserve failures and exact commands. A failure is an observation, never grounds to change a paper parameter invisibly.
6. Work one step at a time and stop for user approval after the declared gate; do not run unattended massive parameter sweeps. No 18,000-run planning batch; P4 is unrelated.
7. New improvements must be marked as `OUR_EXTENSION`, evaluated **in addition** to, never in place of, `PAPER_BASELINE`.
8. At most three scientifically justified repair attempts per blocking issue before reporting a root-cause tree to the user. A new experiment/protocol version must be explicitly declared, not retroactively changed.
9. Do not create or upload private paper PDF, credentials, or local sensor datasets into this repo.
