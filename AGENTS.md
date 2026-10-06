# AGENTS.md — Mandatory rules for Codex / coding agents

This repository is a scientific reproduction and benchmarking project. **Reproducibility and traceability have priority over “making the demo work”.**

## 1. Mandatory pre-task procedure
Before editing code, always read:
1. `CODEX_START_HERE.md`
2. `docs/STATUS.md`
3. the current `docs/tasks/TASKxx*.md` file
4. the relevant `references/P*.md` paper card
5. `docs/BENCHMARK_SPEC.md` if the task touches experiments
6. `git status`

Then report:

```text
=== PRE-TASK REPORT ===
Task:
Goal:
Paper method understood as:
Scope of this iteration:
Files expected to change:
Validation plan:
Known ambiguities / risks:
Need user confirmation: yes/no
```

Do not start implementation before this report.

## 2. Scientific fidelity labels
Every implementation decision must be classified as one of:
- **[ORIGINAL]** directly follows the paper.
- **[ADAPTATION]** necessary mapping to dual FR3 / MuJoCo / Isaac / ROS 2.
- **[ENGINEERING]** software-only implementation detail.
- **[DEVIATION]** differs materially from the paper.
- **[EXPERIMENTAL]** our own trial, not part of the reproduced paper.

If a change is [DEVIATION] and could affect conclusions, stop and ask the user before proceeding.

## 3. No silent theory changes
Never:
- replace a difficult paper method by an easier algorithm without recording it;
- relax benchmark geometry just to make a method pass;
- remove a constraint without recording why;
- change success thresholds between methods;
- report a partially implemented method as a faithful reproduction.

## 4. Frozen benchmark rule
After TASK01 is FROZEN, changes to robot base poses, cube geometry/mass, carriage geometry, pre-push pose, insertion depth, physics/control step, seed policy, success/failure thresholds require:
1. an entry in `docs/DECISIONS.md`;
2. explicit user approval;
3. benchmark version bump.

## 5. Platform separation
- `common/`: platform-independent math, interfaces, metrics, logging.
- `baselines/`: paper algorithms only.
- `platforms/mujoco/`: MuJoCo adapters/tests; mainly P2/P3.
- `platforms/isaac_ros2/`: Isaac/ROS2 adapters and final benchmark integration.
Do not duplicate the same algorithm separately in MuJoCo and Isaac. Adapt through interfaces.

## 6. Third-party code
Original paper code goes under `third_party/` or as a git submodule/subtree if appropriate.
Record:
- upstream URL
- commit SHA/tag
- license
- local patches
Prefer adapters over editing upstream source.

## 7. Required persistent records
At the end of every non-trivial iteration update:
- `docs/STATUS.md`
- `docs/WORKLOG.md`
- `docs/EXPERIMENT_LOG.md` if anything was run
- `docs/BUGS.md` for unresolved defects
- `docs/DECISIONS.md` for architectural/method choices
- `docs/USER_FEEDBACK.md` for explicit user feedback affecting future work

Never erase historical entries. Append new entries with date and task.

## 8. Experiment run format
Each run belongs in:
`results/<timestamp>_<TASK>_<run-id>/`

Required metadata:
- task
- baseline
- platform
- git commit
- seed
- config path
- command
- status
- metrics
- artifact paths

Raw large data/videos should normally stay untracked; keep metadata, summaries and selected figures in git.

## 9. Task state machine
Allowed task states:
`TODO → READY → IN_PROGRESS → PASS → FROZEN`
or `BLOCKED`.

A PASS task must have evidence. A FROZEN task may not be changed casually.

## 10. Git safety
- Work on task branches where practical: `taskXX-short-name`.
- Make small, descriptive commits.
- Never use destructive commands such as `git reset --hard` unless the user explicitly asks.
- Do not commit generated build/install directories.
- Do not use `git add .` blindly; stage intended files.

## 11. Mandatory post-task report
```text
=== POST-TASK REPORT ===
Task:
Status: PASS / PARTIAL / BLOCKED

Completed:
Files changed:
Commands run:
Tests / experiment results:
Key metrics:

Paper fidelity:
[ORIGINAL]:
[ADAPTATION]:
[ENGINEERING]:
[DEVIATION]:
[EXPERIMENTAL]:

Records updated:
STATUS:
WORKLOG:
EXPERIMENT_LOG:
BUGS:
DECISIONS:
USER_FEEDBACK:

Open risks:
Recommended next step:
Git branch / commit / dirty files:
```

## 12. Stop conditions
Stop and ask the user if:
- the paper is ambiguous in a way that changes the algorithm;
- a baseline requires benchmark changes;
- a dependency/license prevents faithful use;
- repeated failures suggest the reproduction target itself must change;
- a proposed shortcut would become a [DEVIATION].

## 13. Visible simulation workflow (user requirement, 2026-10-06)

- Do not start Isaac Sim in headless mode. Use a visible GUI so the user can inspect the scene and motion; this overrides earlier headless debugging plans unless the user explicitly changes it later.
- Keep historical headless scripts/logs as evidence, but do not copy their launch commands into new runs. If a visible GUI cannot be connected or started, report that limitation instead of silently using headless.
- Current `task01_dual_suction_fixture` defaults to `execution_time_scale=1.0` (100% planned-trajectory playback). Earlier `5.0` means20% playback, not50%. Explicit ROS parameters override the default.
- Do not confuse playback倍率 with MoveIt joint velocity/acceleration limits (currently12%). Changing to100% joint limits is a separate physical/control change, not implied by normal playback; actual new-speed performance needs GUI verification.
