# AGENTS.md — Mandatory rules for Codex / coding agents

This repository is a scientific reproduction and benchmarking project. **Reproducibility, traceability, and progress toward the scientific objective have priority over “making the demo work” or perfecting an auxiliary engineering probe.**

## 1. Mandatory pre-task procedure
Before editing code, always read:
1. `CODEX_START_HERE.md`
2. `docs/EXECUTION_GOVERNANCE.md`
3. `docs/STATUS.md`
4. the current `docs/tasks/TASKxx*.md`
5. the relevant `references/P*.md` paper card
6. `docs/BENCHMARK_SPEC.md` if experiments are involved
7. `git status`

Then report:

```text
=== PRE-TASK REPORT ===
Task:
Scientific objective:
Minimum sufficient evidence:
Current scope:
Explicit non-goals:
Attempt budget for the current blocker:
Preferred method:
Fallback method:
Stop / escalation condition:
Files expected to change:
Validation plan:
Known ambiguities / risks:
Need user confirmation: yes/no
```

Do not start implementation before this report.

## 1.1 Mandatory PRIOR-ASSET CHECK for TASK02+
For every implementation task from TASK02 onward, before writing replacement infrastructure:

1. read `docs/POST_TASK01_REUSE_MAP.md`;
2. inspect the pinned engineering source `dreamerToTOE/dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a` for relevant existing components;
3. classify candidates as **DIRECT_PORT / THIN_ADAPTER / TEST_ORACLE / REFERENCE_ONLY**;
4. state which scientific algorithm must still be implemented from the paper;
5. prefer adaptation of validated engineering infrastructure over a parallel reimplementation.

Add this block to the PRE-TASK report:

```text
=== PRIOR-ASSET CHECK ===
Current task:
Scientific algorithm that must remain new/paper-derived:
Old repository areas searched:
Pinned source commit:
DIRECT_PORT:
THIN_ADAPTER:
TEST_ORACLE:
REFERENCE_ONLY:
Rejected old assets and reason:
Files that will be reused/adapted:
Files that will still be newly implemented:
Risk of contaminating paper fidelity:
Need user decision: yes/no
```

Hard boundaries:
- reuse engineering wheels; do not use old code to fake a paper reproduction;
- do not silently import historical thresholds, geometry assumptions, tool transforms or application schedulers;
- generic MoveIt/FCL/execution/logging infrastructure should not be rewritten merely because the new task has a different paper label;
- if reuse materially changes the paper method, classify it **[DEVIATION]** and stop for user review;
- TASK01-specific reuse stays under `docs/PRIOR_PROJECT_REUSE.md`; this rule is for TASK02+.

## 2. Scientific fidelity labels
Every implementation decision must be classified as one of:
- **[ORIGINAL]** directly follows the paper.
- **[ADAPTATION]** necessary mapping to dual FR3 / MuJoCo / Isaac / ROS2.
- **[ENGINEERING]** software-only implementation detail.
- **[DEVIATION]** differs materially from the paper.
- **[EXPERIMENTAL]** our own trial, not part of the reproduced paper.

If a [DEVIATION] may affect scientific conclusions, stop and ask the user before proceeding.

## 3. Requirement vs. method
Always distinguish:
- **REQUIREMENT:** what must be scientifically established.
- **PREFERRED METHOD:** the first way to obtain that evidence.
- **FALLBACK METHOD:** an acceptable cheaper/safer way if the preferred method becomes an engineering sink.

A suggested implementation method is **not** automatically a scientific requirement.

Example:
- Requirement: verify critical Isaac states have no unexpected collision.
- Preferred method: static PhysX query.
- Fallback: controlled synchronized replay of a small critical-state set.
- Not required: proving MoveIt STL and PhysX cooked hull are mathematically identical.

## 4. No silent theory or benchmark changes
Never:
- replace a difficult paper method with an easier algorithm without recording it;
- relax benchmark geometry just to make a method pass;
- remove a constraint without recording why;
- change success thresholds between methods;
- report a partial implementation as a faithful reproduction;
- turn a debugging convenience into a benchmark rule without user review.

## 5. Anti-loop / escalation protocol
Coding agents often optimize the nearest blocker indefinitely. This repository explicitly forbids that behavior.

### 5.1 Classify every blocker
Every newly discovered problem must be classified as exactly one of:
- **TASK-BLOCKING:** current scientific conclusion cannot be established without solving it now.
- **DEFERRED:** real problem, but owned by a later task.
- **KNOWN LIMITATION:** does not invalidate the current task's minimum scientific conclusion.
- **LEGACY:** belongs to an old application/demo path and is not part of the current benchmark.

Record the classification in STATUS/BUGS when non-trivial.

### 5.2 Attempt budget
For the **same root engineering blocker**, default budget is:
1. one diagnosis iteration;
2. one evidence-based fix;
3. one bounded fallback attempt.

After three implementation iterations without establishing the required scientific conclusion, **STOP**. Do not autonomously create v4/v5/v6/... probes.

The user may explicitly grant a larger budget.

### 5.3 Mandatory escalation after budget exhaustion
Output:

```text
=== ENGINEERING ESCALATION ===
Scientific question:
What is already established:
What remains unknown:
Why the remaining unknown matters:
Attempts made:
Root blocker classification:
Is it still task-critical: yes/no
Lower-cost evidence available:
Recommended action:
Need user decision:
```

If the blocker is DEFERRED, KNOWN LIMITATION, or LEGACY, record it and continue the main task instead of fixing it.

### 5.4 No “bug discovered = bug must be fixed now”
A bug is not automatically owned by the task that discovers it.
Use the task map and repository decisions to assign ownership.

Examples:
- contact/TCP wrench calibration → TASK10-IS;
- P3 jam thresholds → P3 tasks;
- old five-Cube sequencing → LEGACY;
- full MoveIt/PhysX geometric equivalence → not a TASK01 requirement unless explicitly promoted by the user.

## 6. Minimum sufficient evidence rule
Before adding more instrumentation, ask:

> “Does the current evidence already establish the scientific claim required by this task?”

If yes, stop expanding the proof and move to the next acceptance item.

Do not convert:
- a sanity check into a platform-verification research project;
- a benchmark setup task into a controller-design task;
- a reproduction task into an infrastructure rewrite.

Prefer **sufficient, reproducible evidence** over exhaustive proof of every software subsystem.

## 7. Scope growth rule
A task may not silently grow because new technical details were discovered.

If a new issue would add:
- a new subsystem,
- a new sensor/estimator,
- a new controller,
- a new simulator integration layer,
- a new benchmark condition,
- or more than one additional implementation iteration,

first decide whether it is TASK-BLOCKING. If not, defer it.

## 8. Frozen benchmark rule
After TASK01 is FROZEN, changes to robot base poses, Cube geometry/mass, carriage geometry, PRE_PUSH/target, physics/time policy, seed policy, success/failure thresholds require:
1. an entry in `docs/DECISIONS.md`;
2. explicit user approval;
3. benchmark version bump.

## 9. Platform separation
- `common/`: platform-independent math, interfaces, metrics, logging.
- `baselines/`: paper algorithms only.
- `platforms/mujoco/`: MuJoCo adapters/tests; mainly P2/P3.
- `platforms/isaac_ros2/`: Isaac/ROS2 adapters and final benchmark integration.

Do not duplicate the same algorithm separately in MuJoCo and Isaac. Adapt through interfaces.

## 10. Third-party code
Original paper code goes under `third_party/` or as a git submodule/subtree if appropriate.
Record upstream URL, commit SHA/tag, license, and local patches.
Prefer adapters over editing upstream source.

## 11. Required persistent records
At the end of every non-trivial iteration update:
- `docs/STATUS.md`
- `docs/WORKLOG.md`
- `docs/EXPERIMENT_LOG.md` if anything ran
- `docs/BUGS.md` for unresolved defects
- `docs/DECISIONS.md` for architecture/method choices
- `docs/USER_FEEDBACK.md` for explicit user feedback

Never erase historical entries. Append new entries with date and task.

## 12. Experiment run format
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

Raw large data/videos normally stay untracked; keep metadata, summaries, and selected figures in git.

## 13. Task state machine
Allowed task states:
`TODO → READY → IN_PROGRESS → PASS → FROZEN`
or `BLOCKED`.

A PASS task must have evidence.
A FROZEN task may not be changed casually.
A task should not remain IN_PROGRESS merely because a non-critical engineering limitation still exists.

## 14. Git safety
- Work on task branches where practical: `taskXX-short-name`.
- Make small descriptive commits.
- Never use destructive commands such as `git reset --hard` unless explicitly requested.
- Do not commit generated build/install directories.
- Do not blindly use `git add .`.

## 15. Mandatory post-task report
```text
=== POST-TASK REPORT ===
Task:
Status: PASS / PASS CANDIDATE / PARTIAL / BLOCKED

Scientific objective:
Minimum sufficient evidence achieved: yes/no

Completed:
Files changed:
Commands run:
Tests / experiment results:
Key metrics:

Blockers:
- TASK-BLOCKING:
- DEFERRED:
- KNOWN LIMITATION:
- LEGACY:

Attempt budget used:
Escalation required: yes/no

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

## 16. Stop conditions
Stop and ask the user if:
- the paper is ambiguous in a way that changes the algorithm;
- a baseline requires benchmark changes;
- a dependency/license prevents faithful use;
- repeated failures exhaust the anti-loop attempt budget;
- a proposed shortcut becomes a material [DEVIATION];
- a task is about to expand beyond its stated scientific objective.

## 17. Visible simulation workflow
- Do not start Isaac Sim headless unless the user explicitly changes this requirement.
- Keep historical headless scripts/logs as evidence, but do not silently reuse them for new acceptance runs.
- Playback rate, physics rate, controller rate, and MoveIt joint limits are distinct quantities and must not be conflated.
- GUI visibility is an engineering/user-inspection requirement, not by itself scientific evidence of correctness.


## 18. D041 restarted TASK01 override
On branch task01-legacy-scene-foundation, active TASK01 is a direct predecessor-scene qualification.

Before writing any TASK01 runtime code:
- read docs/tasks/TASK01_BENCHMARK_FREEZE.md;
- read the pinned predecessor Task26 source itself;
- prefer running old Task26 directly over adapting current reproduction harnesses.

For this restarted TASK01, do not extend the custom platforms/isaac_ros2/handoff/task01_* path, standalone SimulationApp path, native D6 introspection, custom readback-validator path, or previous INSERT_READY-only acceptance line unless the user explicitly reopens them.

The only pre-qualification code change permitted by default is a minimal one-Cube selector/count/loop adaptation in the predecessor Task26 path if no exact single-Cube mode already exists.
