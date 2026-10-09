# TASK02-B — unified command, event, result and lightweight logs

2026-10-09 · ENGINEERING · branch `task02-minimal-foundation-interface`

**TASK02-B = PASS CANDIDATE; TASK02 = IN_PROGRESS.** Formal Benchmark remains DRAFT.
One bounded offline implementation only. No Isaac/ROS/MoveIt execution, Task26 rewrite,
scientific threshold freeze, live command binding or TASK03. TASK01 foundation acceptance
and all earlier positive/negative physical evidence are unchanged.

## PRE-TASK REPORT

```text
Task: TASK02-B command/event/result/lightweight file logging
Scientific objective: expose engineering evidence through common platform-independent data
Minimum sufficient evidence: offline serialization/causal-clock/qualification/failure tests;
  actual file readback with TASK02-A historical snapshot; immutable old source/config scope
Current scope: typed records, planned-only event adapter, stdlib logger, synthetic/file tests
Explicit non-goals: execution/controller/scene/bridge/SG/rail/FCL/physics/benchmark changes,
  paper algorithms, scientific scoring, native attestation, runtime or TASK03
Attempt budget: one bounded offline implementation/validation cycle; physical allowance0
Preferred method: reuse pinned event/stage semantics and Task16 seed/trial/output patterns
Fallback method: none requiring runtime or mature-module replacement; stop on scope ambiguity
Stop/escalation: old geometry/physics/controller changes required, semantic evidence loss,
  benchmark threshold decision or runtime needed to claim offline acceptance
Files expected: common/interfaces, common/logging, foundation/legacy_events.py,
  tests, selected offline results, documentation and six persistent records
Validation plan: synthetic/negative tests + saved snapshot/file readback + hash/scoped diff
Known risks: legacy asynchronous state; declared evidence/IDs are not native measurement proof
Need user confirmation: no for this explicitly approved slice; yes before future runtime/scope
```

Main re-read latest AGENTS, governance, TASK02 and POST_TASK01_REUSE_MAP before implementation.
Origin branch was fetched and equal to local base `06d54341efdb82a61d0097ee5bda439f50c47249`.
Pinned source files were read completely, not replaced by agent summaries. Independent agent
review was read-only and limited to contract/logging scope; no runtime or second implementation.

## PRIOR-ASSET CHECK

```text
Current task: TASK02-B offline exchange/logging
Scientific algorithm that must remain new/paper-derived: all P1-P5; none implemented here
Old assets searched (full read):
  ros_ws/src/fr3_dual_palletize/include/fr3_dual_palletize/task_event.hpp
  ros_ws/src/fr3_dual_palletize/include/fr3_dual_palletize/task_trajectory_candidate.hpp
  ros_ws/src/fr3_dual_palletize/src/task16_planning_benchmark.cpp
Pinned source:631b1f65656d025c1bb2173e874192f3fe4d355a
Accepted Task26 source exception:5ed0c967401e5fedb93b938e1c3904f4a4c87600, unchanged
DIRECT_PORT:none; no mature C++ controller copied/executed
THIN_ADAPTER:event names, relative event/stage times, explicit seed/trial/failure/file-output
TEST_ORACLE:TASK02-A normalized saved Task26 final snapshot
REFERENCE_ONLY:legacy controller/scheduler/planner parameters/acceptance thresholds
Rejected:new executor, automatic SG→attachment inference, historical-threshold default import
Reused:validated semantics/output organization, existing StateRecord/legacy source guard
New:stdlib immutable exchange contracts, strict codec, single-writer logger, offline tests
Paper fidelity risk:mistaking engineering wire/logging PASS for scientific reproduction
Need user decision:no for this software slice; benchmark/runtime remain separate decisions
```

The old header explicitly separates physical suction command boundaries from world/attached
geometry events. TaskStageMarker records relative start/end and TaskTrajectoryCandidate uses
one relative task axis. Task16 records explicit seeds, trials, stages, failures and CSV/JSON.
This slice adapts those concepts into file-only Python interfaces; it neither copies the old
planner nor calls its OMPL seed API. Only JSON/JSONL is needed for the approved B scope.

## Implementation and acceptance boundary

- [Data contracts](../common/interfaces/exchange.py): frozen BaselineCommand, targets,
  TimePoint, TaskEvent/TaskStageMarker/EventLedger, BenchmarkResult, RunMetadata/SourceRef.
  Commands carry IDs/robots/object/type/frame/SI targets/clock/deadline/config/source;
  they have no execute/send/publish/step method or runtime imports.
- [Wire codec](../common/interfaces/wire.py): versioned envelopes, recursive typed readback,
  unknown-field/enum rejection, finite-number validation and deterministic sorted UTF-8 JSON.
  Same input retains int/float representation, no default RNG/wall stamp is injected.
- [Old event adapter](../platforms/isaac_ros2/foundation/legacy_events.py): emits PLANNED only,
  with explicit trajectory ID and relative ns; no SG query, state change or observation.
  Seconds→ns rounding≤0.5ns is representation encoding, not an acceptance threshold.
- [File logger](../common/logging/run.py): exclusive new run directory, metadata JSON,
  commands/events/states JSONL, result JSON and exception termination evidence. Typed run
  metadata is nested as `run_metadata`; it is directly decodable without weakening wire checks.
  Each JSONL line is flushed/fsynced; JSON uses a temporary file then atomic replacement.
- [Offline tests](../tests/test_task02_exchange_logging.py):19B tests plus existing14A tests.
  [Usage and actual-file reading](../common/README.md).

PLANNED is trajectory-relative; OBSERVED/CONFIRMED require declared post-step simulation
stamp/step/session. No numeric comparison/conversion occurs across trajectory/simulation IDs.
Same-domain backwards time/step, duplicate event IDs and missing causal refs are rejected.
CONFIRMED must refer to prior separate OBSERVED with matching kind/stage/robot/object/link,
command, attachment and clock; observation cannot be resolved twice. FAILED preserves reason
and evidence. Explicit plan command binding cannot be replaced by another command.

**SUCTION_ON never generates ATTACH.** ATTACH/DETACH observations need exact attachment
identity and raw evidence references, not SG CLOSED alone. These IDs/paths are declared data;
the schema does not itself establish PhysX/D6 identity or authenticate evidence bytes.

BenchmarkResult supports SUCCESS/FAILURE/ABORTED/INCOMPLETE with scope, qualification,
failure stage/reason, evidence/config/source and limitations. No scoring function or numerical
success default exists. Explicit results are caller declarations, not validated robot success.
Unhandled Python exception leaves ABORTED and traceback (including empty-message exceptions);
normal context exit without explicit finish leaves INCOMPLETE, never implicit SUCCESS.

Optional states retain TASK02-A raw normalized data. A legacy clock/evidence label/source
cannot be silently upgraded to SYNCHRONIZED_POST_STEP by adding timestamps or deleting a label.
Logger synchronized result qualification requires nonempty all-qualified state records.
This is a conservative provenance/formal-input guard, not proof against rewriting all fields.
The actual sample below uses **UNQUALIFIED** run result, synthetic events and legacy state.

Seed must be explicitly an integer (SET, including0) or None (UNSET). Trial is explicit.
Source paths and SHA256, command argv (duplicates permitted), config paths and final artifact
hashes are recorded. This bookkeeping does **not** seed execution RNGs. Source hash is file
provenance, not timestamp authenticity or historical snapshot/native measurement attestation.

## Offline acceptance evidence

Final command from repo root, Python3.10.12, no setup.bash/GUI/services needed:

```bash
python3 -m unittest discover -s tests -p 'test_task02*.py' -v
```

Final observed result: **33/33 PASS; exit0;2.265s engineering wall duration**.
Regressions were re-run within this same offline implementation cycle after review fixes;
there were no independent physical attempts or new algorithm alternatives.

Coverage:

- joint/pose/hold/suction command roundtrip, units/target/robot validation; network/process/shell
  execution tripwires and no command execution methods;
- PLANNED/OBSERVED/CONFIRMED/FAILED ordering, causal identity, explicit attachment and evidence;
- clock-domain mismatch/reverse order/step rejection, relative stage serialization;
- four results, failure log retention, empty/nonempty exceptions ABORTED and unfinished INCOMPLETE;
- actual metadata/event/result readback, SET/UNSET seed, source/config/command/run identity;
- historical snapshot field/source guards and prevention of empty-state qualification upgrade;
- identical input yields identical file-format bytes; existing run/path-escape/finalized writes rejected.

Published example is a **deliberately failed synthetic gate**, not robot FAILURE:
1 data-only command,3synthetic events (planned→observed→confirmed),1historical asynchronous
state, seed UNSET, terminal FAILURE. Its synthetic stamp50000000000ns/step10 is invented
test data, not a new Isaac clock sample. Source/trial/argv/config/artifact hashes are saved.
The complete exact generation command is data in its metadata; re-running the same run ID
is intentionally refused, so a new output directory/run ID is required.

- [Acceptance metadata](../results/20261009_TASK02_exchange_logging01/metadata.json)
- [Final test log](../results/20261009_TASK02_exchange_logging01/tests.log)
- [Synthetic raw fixture](../results/20261009_TASK02_exchange_logging01/synthetic_observation.json)
- [Run metadata/source hashes](../results/20261009_TASK02_exchange_logging01/retained_failure/metadata.json)
- [Command JSONL](../results/20261009_TASK02_exchange_logging01/retained_failure/commands.jsonl)
- [Event JSONL](../results/20261009_TASK02_exchange_logging01/retained_failure/events.jsonl)
- [Retained FAILURE result](../results/20261009_TASK02_exchange_logging01/retained_failure/result.json)
- [Historical state JSONL](../results/20261009_TASK02_exchange_logging01/retained_failure/states.jsonl)
- [Scope/hash checks](../results/20261009_TASK02_exchange_logging01/scope_validation.json)

The historical state input is unchanged `results/20261009_TASK02_foundation_interface01/
converted_snapshot.json`, from accepted Task26 run02. No new final snapshot was sampled.
Metadata git_commit denotes the pre-implementation base06d5434; changed-source file hashes
in the emitted run identify exact tested bytes, not a false claim that the new code was at base.

## Scope validation and known limits

Read-only accepted-source guard matches four declared local assets (scene/bridge/controller/
binary), and isolated old worktree remains clean. `configs/benchmark/benchmark_v1.yaml` SHA256
remains `fbef560ae81963fdf5839cd83d95274edebd9769024d1ae74527f00092c8f2a2`.
No old Task26/scene/bridge/FCL/SG/rails/push/physics/source, current simulation harness,
benchmark geometry/config, thresholds or paper baseline is changed. No build/runtime/import
of Isaac/ROS/MoveIt, native state/time/control command, reset or new physics evidence.
Unrelated historical untracked raw logs remain untouched and excluded from this commit.

Single-process/single-writer logger, not a crash-recovery system. SIGKILL/disk-loss/power
failure, cross-file transactions, concurrent writers and resumable experiments are not claimed.
In-progress counts/artifact hashes refresh at creation/finish, not after every appended line.
No DB, ROS log service or complex middleware. Controlled exception retention does not imply
hard-crash recovery. Source hashes do not attest the whole legacy dependency world.

## POST-TASK REPORT

```text
Task:TASK02-B unified command/event/result/lightweight file logs
Status:PASS CANDIDATE; TASK02 IN_PROGRESS; Benchmark DRAFT/NOT FROZEN
Scientific objective:common evidence/data layer while preserving accepted execution foundation
Minimum sufficient evidence achieved:yes, only for approved offline slice
Completed:data contracts/codec, planned-only adapter, logger, fixtures/tests/readback, provenance
Files changed:common/interfaces(+export),common/logging,foundation/legacy_events.py,
  tests/test_task02_exchange_logging.py,selected TASK02 exchange results,
  common/foundation README,rootREADME,start guide,TASK02 spec,report andsixrecords
Commands run:read-only git/pinned-source checks;stdlib unittest;offline RunLogger example;
  accepted asset guard;YAML hash;scoped diff/JSON checks;git commit/push on existing task branch
Tests/experiment results:19B+14A=33PASS/exit0;file example/readback0;hashes4/4
Key metrics:1example command/3synthetic events/1legacy state;seedUNSET;
  Isaac/ROS/MoveIt/control/build/physics calls0
Blockers:
  TASK-BLOCKING:none for TASK02-B offline contract acceptance
  DEFERRED:ContactWrench/CollisionDistance/scientific metrics/RNG control/live same-step binding
  KNOWN LIMITATION:caller provenance;legacy async feedback;single-writer/no hard-crash guarantee
  LEGACY:inactive custom TASK01 parity/startup/five-Cube paths;not reopened
Attempt budget used:1bounded offline implementation/validation cycle;physical0
Escalation required:no
Paper fidelity:
  ORIGINAL:no paper algorithm implemented
  ADAPTATION:predecessor event/stage/time/seed-trial-output concepts
  ENGINEERING:typed data,strict codec,causal guards,file logger/source hashes
  DEVIATION:none tobenchmark/runtime/paper method;no inherited numerical acceptance default
  EXPERIMENTAL:synthetic/offline conformance only,not scientific robot experiment
Records updated:STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK:yes
Open risks:formal benchmark/metrics/native qualification remain separate review items
Recommended next step:user review B;only then scope remaining TASK02 metric/measurement slice
Git branch:task02-minimal-foundation-interface;test base06d5434+explicit changed-source hashes
Dirty files:only unrelated historical untracked raw artifacts preserved after scoped publication
```

Stop here. This delivery does not authorize a live test, mature runtime replacement, TASK03
or formal success-threshold freeze.
