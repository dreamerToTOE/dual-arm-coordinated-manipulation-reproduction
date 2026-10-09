# TASK02-A — accepted foundation, minimum in-place state interface

2026-10-09 · ENGINEERING · offline slice PASS; overall TASK02 IN_PROGRESS

## Outcome and acceptance boundary

User accepted **TASK01 foundation feasibility PASS CANDIDATE**, expressly not the formal
scientific Benchmark freeze. Prior evidence at5222b2e remains unchanged: approved
Task26@631b1f+5ed0c96, second two-Cube/fullHOME runexit0 after first joint-settle failure.
No repeated physical qualification or mature grasp/regrasp/push redevelopment is needed.

After user “继续”, this slice uses validated assets **in place**, not a new scene or controller.
14 offline tests PASS; four local accepted asset hashes match; real saved snapshot conversion
exit0. This is not a new physical run, scientific synchronization, full TASK02 PASS or paper result.

## PRE-TASK REPORT

```text
Task: TASK02-A minimum provenance and read-only state interface
Scientific objective: expose accepted engineering state without reimplementing runtime
Minimum sufficient evidence: source hash match, real snapshot conversion, offline rejection tests
Current scope: common state types, thin file adapter, identity/provenance, tests/records
Explicit non-goals: runtime/controller rewrite, new simulation, benchmark freeze, P1-P5
Attempt budget: one implementation and offline validation cycle; physics allowance0
Preferred method: accepted predecessor in place through platform-independent contracts
Fallback method: no parallel replacement; report unresolved interface ambiguity
Stop/escalation: source mismatch, unpreservable data semantics, old behavior change required
Files expected: common/interfaces, platform foundation adapter/manifest, tests/results, records
Validation plan: stdlib unittest, saved real snapshot, immutable old assets and scoped diff
Known risks: old USD/native/ROS-clock feedback not atomic post-step; must remain labeled
Need user confirmation: no for this slice; yes for future formal benchmark definitions
```

## PRIOR-ASSET CHECK

```text
Current task: TASK02-A states/provenance only
Scientific algorithm that remains new/paper-derived: all P1-P5; none implemented now
Old areas searched: pinned task_event.hpp, task_trajectory_candidate.hpp,
  Task26 scene/object identity and bridge/snapshot semantics, Task16 output/seed patterns
Pinned source:631b1f65656d025c1bb2173e874192f3fe4d355a
Approved runtime exception:5ed0c967401e5fedb93b938e1c3904f4a4c87600
DIRECT_PORT: none this slice; no controller source copy
THIN_ADAPTER: explicit source/frame/joint/object/event/time contract concepts;
  legacy Task26 stored feedback into common SI/xyzw states
TEST_ORACLE: accepted run02 final snapshot; negative malformed-input fixtures
REFERENCE_ONLY: old application scheduler, nominal target geometry, numeric acceptance/force guards
Rejected assets: custom TASK01 handoff/parity/startup replacement path, new SG/regrasp/push
Reused: accepted scene/bridge/controller/binary in place; original raw evidence immutable
New implementation: stdlib common state schema, read-only conversion and source guard/tests
Paper-fidelity risk: calling engineering conversion a reproduced algorithm or synced measurement
Need user decision: no for this software slice; formal benchmark remains DRAFT
```

## Implementation

- [Common contracts](../common/interfaces/state.py): Pose, ObservationClock, ArmState,
  DualArmState, ObjectState, StateRecord. SI field names, quaternionxyzw, explicit frame/source.
- [Thin adapter](../platforms/isaac_ros2/foundation/legacy_task26.py): only reads files,
  verifies approved asset bytes, maps seven arm joints by exact names rather than array positions,
  converts native basewxyz toxyzw, preserves old diagnostics and explicit missing information.
- [Manifest](../platforms/isaac_ros2/foundation/legacy_task26_manifest.json): accepted source pin,
  patch commit, four asset hashes, original fourCube Prim identities, no benchmark defaults.
- [Tests](../tests/test_task02_foundation_interface.py): valid saved input; identity reorder;
  failed envelope, missing/duplicate identities, NaN/Inf/bool, malformed dimensions/quaternion,
  clock/frame rejection, source mismatch/path escape, callback failures retained.

Legacy object/TCP observations remain USD feedback; bases remain native articulation feedback.
The converter does not promote them to a common atomic sample. Scientific simulation stamp/step
are null, post_physics_stepfalse; timeline and ROS clock are separate diagnostics.
`ObservationClock.require_scientific_timestamp()` rejects this legacy observation.
No world_shift is inferred from railX, attachment identity from SG CLOSED, or collision distance
and wrench from logs. Four local hashes do not attest the entire dependency world or historical
snapshot origin. Original raw snapshot SHA10c412fd… is carried into normalized output.

## Validation and artifacts

From repository root, no ROS/Isaac imports, runtime or new dependency:

```bash
python3 -m unittest discover -s tests -p 'test_task02_foundation_interface.py' -v
python3 -m platforms.isaac_ros2.foundation.legacy_task26 \
  --legacy-root /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation \
  --snapshot results/20261009_TASK01_predecessor_patched_runtime02/final_snapshot.json
```

Actual tests14/14PASS (recorded0.009s), converterexit0, four local assetshashes match.
[Metadata](../results/20261009_TASK02_foundation_interface01/metadata.json),
[test log](../results/20261009_TASK02_foundation_interface01/tests.log),
[converted real snapshot](../results/20261009_TASK02_foundation_interface01/converted_snapshot.json).
The unchanged old worktree remains clean. Benchmark YAML, geometry, physics, tool, ACM,
old source/control/launch and previous probe paths were not edited. No build/Isaac/ROS/robot/rail/
SG calls; no physics timestep or new scientific timestamp. Unit-test temporary fixtures stay
outside both production repositories and are automatically cleaned by TemporaryDirectory.

## Next bounded slice, not yet implemented

1. Common command/result/event + light metadata/logger contracts; offline adapters first.
   Keep commands as data until a separately scoped live execution binding is tested.
2. Shared metric calculations and synthetic identical-input cross-platform tests;
   thresholds only through explicit configuration, no historical-default promotion.
3. Read-only live binding of already existing native post-step sources, after checking their
   frame/identity/time semantics. No new scene/bridge/holding implementation or force experiment.
4. Paper algorithms consume these contracts; their mathematics must still follow papers.

Formal START/INSERT_READY/reset/measurement/threshold freeze is a separate user decision,
not a pretext to reopen TASK01 engineering qualification or silently adopt old Task26 parameters.

## POST-TASK REPORT

```text
Task: TASK02-A minimal state/source adapter
Status: slicePASS; parentTASK02PARTIAL/IN_PROGRESS; TASK01candidate accepted, notFROZEN
Scientific objective: reuse engineering foundation behind unified state contracts
Minimum sufficient evidence achieved: yes for offline slice only
Completed: source/classification audit, commondraft, thinadapter, manifest, tests/realconversion
Files changed: common/interfaces, foundation/, tests/test_task02_foundation_interface.py,
  results/20261009_TASK02_foundation_interface01, README/start/task/spec/status andsixrecords
Commands: read-only git/source checks; unittest; file converter; scoped git records publication
Tests/results:14PASS, unittest0, converter0, localhash4/4
Key metrics:14armjoints,4originalobjects retained, physicalruns0
Blockers:
  TASK-BLOCKING: none for this offline slice
  DEFERRED: remainingTASK02 command/logger/metrics/seed andlive post-step binding
  KNOWN LIMITATION: legacyasynchronousfeedback/firstphysicalnegative/fourasset-only verification
  LEGACY: customTASK01 parity/startup/fiveCube routes; no reopening
Attempt budget used:1softwarecycle; no physical attempt
Escalation required:no
Paper fidelity:
  ORIGINAL:no paper algorithm implemented
  ADAPTATION:SI/xyzw/frame/source mapping fromlegacyplatform data
  ENGINEERING:sourceguard/typedread-onlyinterface
  DEVIATION:none tobenchmarks, runtime orpaper methods
  EXPERIMENTAL:offlineconformance, notresearchcomparison
Records updated:STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK:yes
Open risks:command/result/metrics notcomplete; no synced native scientificstate yet
Recommended next step:one bounded offline command/event/result/logger slice
Git branch:task02-minimal-foundation-interface; base5222b2e+disclosedtasksourcechanges
Unrelated historical untracked results:preserved/uncommitted
```
