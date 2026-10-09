# TASK02-C — Unified Metrics & Measurement Contracts

2026-10-09 · ENGINEERING · `task02-minimal-foundation-interface` · base `c7b33b1`

**TASK02-C = PASS CANDIDATE**

**TASK02 = IN_PROGRESS**

**BENCHMARK = DRAFT / NOT FROZEN**

完成一次有界纯离线实现与验证，未启动Isaac、ROS、MoveIt或Task26。
指标不自动判SUCCESS；旧基础场景、A/B接口语义、科研Benchmark及原始运行证据未修改。

## PRE-TASK REPORT

```text
Task: TASK02-C common metric math and draft measurements
Scientific objective: comparable explicit definitions and qualified data boundaries for A/B
Minimum sufficient evidence: Task14 formula reuse; two independent mock-input numerical
  parity; quality/clock/serialization negative tests; all TASK02-A/B/C regression; scope hashes
Current scope: common/metrics, measurement dataclasses, synthetic tests and file artifacts
Explicit non-goals: runtime/sensors/force estimation/FCL queries/real-time middleware;
  Task26/SG/rails/physics/tool/carriage/ACM changes; benchmark thresholds; paper algorithms
Attempt budget for the current blocker: one offline implementation/validation cycle;
  simulator/ROS/MoveIt/physical allowance0
Preferred method: thin extraction of Task14 math; reuse A/B Pose/time/qualification/wire
  and Task16 seed/trial/source/artifact evidence organization
Fallback method: none requiring execution or mature engineering replacement
Stop / escalation condition: old accepted semantics or geometry must change; runtime,
  scientific thresholds or a new measurement backend needed to claim software acceptance
Files expected to change: new common metrics/measurement and tests, selected new result
  files, task/API/readme/start/report and six persistent records
Validation plan: synthetic and stored historical snapshot tests, actual JSON roundtrip/
  numerical readback, unchanged accepted assets/YAML/A/B code and scoped diff
Known ambiguities / risks: old metrics are initial world-vector drift, not SE(3) closure;
  declared post-step qualification is not native attestation; no default success threshold
Need user confirmation: no for this explicit offline slice; yes for later runtime/freeze
```

Main re-read AGENTS/governance/STATUS/TASK02/reuse-map/P4/Benchmark before implementation,
and fully read the three required pinned predecessor sources. Active origin fetched and
equal to local `c7b33b16c3b4332fb9b00d03f1ae853cbf519da2` at start; unrelated local raw logs
were preserved and excluded. Read-only audit/review and disjoint synthetic-test work were
delegated; no agent ran simulator/control software.

## PRIOR-ASSET CHECK

```text
Current task: TASK02-C offline mathematical metrics and measurement records
Scientific algorithm that must remain new/paper-derived: all P1–P5 algorithms;
  this slice implements no closed-chain planner, force controller, QP or MPC
Old repository areas searched: Task14 monitor/doc, Task16 planning benchmark;
  accepted TASK02-A snapshot and TASK02-B codec/logger
Pinned source commit: 631b1f65656d025c1bb2173e874192f3fe4d355a
DIRECT_PORT: none of the old runtime monitor/control nodes
THIN_ADAPTER: Task14 relative/midpoint/quaternion/max/RMS math and timestamp-filter idea;
  Task16 seed/trial/CSV/JSON evidence organization already reused in B
TEST_ORACLE: analytic synthetic trajectories plus TASK02-A converted legacy snapshot
REFERENCE_ONLY: old 3mm/5mm/2deg/30ms acceptance and ROS/SG CLOSED listener behavior
Rejected old assets and reason: asynchronous ROS/USD streams cannot be promoted into
  scientific post-step data; no execution stack or native backend needed for offline math
Files reused/adapted: Task14 cpp/doc and Task16 cpp; existing A/B Pose/time/qualification/
  WireRecord without modification; stored converted_snapshot.json unchanged
Files newly implemented: common/interfaces/measurement.py, common/metrics/*,
  test-only independent input decoders and metric/measurement tests
Risk of contaminating paper fidelity: do not rename world-vector drift SE(3) closure,
  import old thresholds, or label synthetic/native-declared test doubles scientific evidence
Need user decision: no for approved definitions; later scoring/native binding needs approval
```

Pinned source provenance (read through `git show`, not current branch assumptions):

- `task14_shared_box_geometry_monitor.cpp`, SHA256
  `f598018252b881ffae797b296ac76d7f3f3c60edf7e4150106665f6a7bdf8395`.
- `TASK14_CONTINUOUS_GEOMETRY.md`, SHA256
  `d5b5e7bb9613c1f69e888313ef1dd86a7131f467ff1e8729bfca6d4dd41ef00b`.
- `task16_planning_benchmark.cpp`, SHA256
  `e913ecb9db58af4c30a20b76a6c4bcec4fee46afdef61582d77b784f09a23820`:
  explicit seed/trial/stage/failure and file organization reused through existing B,
  not its planner parameters, timings or controller.

## Implemented definitions and boundaries

Task14 lines224–237 define relative TCP vector and object-midpoint offset drift against
the first accepted sample, and normalized sign-invariant quaternion angle. Lines148–151
define equally weighted sample RMS. This slice preserves those definitions, including
**constant initial midpoint offset is not an error** and constant initial attitude is not
target-tracking error. No body-frame rotation compensation or relative TCP attitude is claimed.

Benchmark A adds explicit reference-position Euclidean RMSE. Benchmark B adds target
Euclidean error, signed axial displacement/progress, perpendicular distance to explicit
axis line, target attitude error and eligible insertion-window stamp duration. These are
new basic mathematical contracts, **not old Task14 implementations or paper algorithms**.
Details/formulas/API are in [common/metrics](../common/metrics/README.md).

ContactWrench explicitly defines torque about its application point in its expression
frame; CollisionDistance declares signed gap and backend witness points. Unknown invalid
values remainNone, valid missing values reject. Neither acquires data or estimates forces.

Same simulation session and SIMULATION time required; trajectory-relative/wall time is
not converted. Qualification/frame/session/identity mismatch or time reversal rejects
the whole input; missing/invalid/duplicate/skewed rows carry input-index/reason/count.
Physics steps must match across A channels; each channel is monotonic. Stamp-skew policy
is explicit with **no legacy default**. No valid samples yieldsnull summaries.
Malformed quaternion/vector/nonfinite data raises a format error rather than zero fill.

Formal duration requires declared synchronized native post-step endpoints of a caller-
defined window. It does not detect completion. Rejected endpoints never become duration
or final-target evidence from another sample. Synthetic example duration is alwaysnull.
The FORMAL test-double unit case tests code branches only, **not real native qualification**.
Legacy A snapshot remains engineering compatibility evidence and is rejected by formal metrics.

## Offline acceptance and actual saved files

Commands run from repository root:

```bash
python3 -m unittest discover -s tests -p 'test_task02*.py' -v
PYTHONPATH=. python3 tests/task02c_synthetic_inputs.py \
  --output results/20261009_TASK02_metrics_measurements01/example_metrics.json
git diff c7b33b1 --exit-code -- configs/benchmark/benchmark_v1.yaml \
  common/interfaces/state.py common/interfaces/exchange.py common/interfaces/wire.py \
  common/logging/run.py platforms baselines ours third_party \
  tests/test_task02_foundation_interface.py tests/test_task02_exchange_logging.py
```

**72/72 tests PASS**, exit0, saved engineering wall duration2.540s:
A14 + B19 + C39 (measurement11 + metric/adapter28). This wall duration is test-run timing,
not benchmark insertion or robot performance. Coverage includes zero/fixed translation/
fixed attitude, changing max/RMS, q/-q, differing sample counts, unavailable samples,
empty data, nonfinite/quaternion/frame/entity errors, clock/session/step/skew/qualification,
strict serialization, no execution side effects, signed distances/wrench points and
actual legacy snapshot compatibility. Review caught four issues before final regression:
channel-specific order checking, reverse-before-duplicate, vector lengths before zip,
and unavailable final endpoint; corrected only new C code, no accepted A/B semantic edits.

Two mock adapters independently decode dict/xyzw/integer-ns and array/wxyz/seconds.
4-sample fixture: desiredx=.1*i, actualx=.11*i, yaw=.1*i, TCPy=±.2,z=.5,
axis+X and B targetx=.33. Both adapters produce **identical numerical results**:

| Metric | Synthetic value |
| --- | ---: |
| A relative TCP max / RMS | 0m / 0m |
| A midpoint drift max | .030m |
| A object position RMSE | .0187082869338697m |
| A object attitude max / RMS | .300rad / .187082869338696rad |
| B axial progress | 0, 1/3, 2/3, 1 |
| B final target error | ≈5.55e−17m (floating-point roundoff) |
| B formal insertion time | null (synthetic, not actual physics) |
| Samples per adapter / per metric | 4valid / 0rejected |

Evidence directory: [metadata](../results/20261009_TASK02_metrics_measurements01/metadata.json),
[test output](../results/20261009_TASK02_metrics_measurements01/tests.log),
[full example JSON](../results/20261009_TASK02_metrics_measurements01/example_metrics.json),
[scope/source hashes](../results/20261009_TASK02_metrics_measurements01/scope_checks.log),
[actual JSON readback](../results/20261009_TASK02_metrics_measurements01/artifact_readback.log).
Seed explicitlyUNSET (`null`), trial0; deterministic constructed input uses no RNG.
Output is a new exclusive-create artifact, not rewriting old evidence. Exact source hashes
bind working-tree implementation to the artifact even before its enclosing delivery commit.

Accepted old local assets4/4 hash match, old checkout clean at5ed0c96. Benchmark YAML SHA
`fbef560ae81963fdf5839cd83d95274edebd9769024d1ae74527f00092c8f2a2` unchanged;
A/B source and old platform/algorithm areas unchanged. No mature runtime module was edited.

## POST-TASK REPORT

```text
Task: TASK02-C Unified Metrics & Measurement Contracts
Status: PASS CANDIDATE
Scientific objective: source-independent mathematics with explicit measurement/time quality
Minimum sufficient evidence achieved: yes, for this offline software slice only
Completed: Task14-derived A geometry stats; A reference-position RMSE; B axis/target/
  attitude/window metrics; data-only wrench/distance; two mock adapters; strict quality tests
Files changed: new common/interfaces/measurement.py + common/metrics/; three C test files;
  this report; new result directory; six records; task/readme/common/start docs
Commands run: standard-library unittest, synthetic artifact CLI, JSON readback, git read-only
  scope/asset/hash checks, then scoped commit/push; no simulator/ROS/build/control commands
Tests / experiment results: 72/72 offline PASS; two mock inputs numerically identical;
  no physical experiment, scientific RMSE dataset or real execution-time result
Key metrics: synthetic positionRMSE.0187082869m; orientationRMS.1870828693rad;
  formal insertion time unavailable; qualification and rejection checks PASS
Blockers:
  TASK-BLOCKING: none for C software delivery
  DEFERRED: real post-step binding/attestation, scoring config, RNG execution plumbing,
    force measurement/calibration TASK10-IS; additional full export/runtime scope
  KNOWN LIMITATION: source/evidence declarations not tamper-proof native attestation;
    sample-weighted metrics depend on sampling; initial-drift metrics are not full closure;
    caller supplies correctly aligned reference/window; no real simulator consistency claim
  LEGACY: original asynchronous Task26 data, parity/image-core/five-Cube diagnostics
Attempt budget used: one offline implementation/validation cycle; physical allowance0/0
Escalation required: no
Paper fidelity:
  [ORIGINAL]: no P1–P5 algorithm implemented or reproduced in this slice
  [ADAPTATION]: exact predecessor Task14 math plus stricter explicit eligibility boundary
  [ENGINEERING]: common records, basic tracking/axis math, deterministic file evidence
  [DEVIATION]: no benchmark/old execution/physics/acceptance change
  [EXPERIMENTAL]: mock-source software tests only; not physical or scientific benchmark data
Records updated: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS(D044)/USER_FEEDBACK,
  TASK02 scope, root/common README and CODEX_START_HERE
Open risks: real source binding and user-approved success/measurement policy not yet available
Recommended next step: stop; user reviews C and separately defines any later bounded slice
Git branch / commit / dirty files: task02-minimal-foundation-interface;
  base c7b33b16c3b4332fb9b00d03f1ae853cbf519da2; exact new source hashes in metadata;
  delivery commit is the commit containing this report; unrelated pre-existing raw logs
  remain local/untracked and are excluded from this scoped delivery
Stop state: TASK02-C PASS CANDIDATE; TASK02 IN_PROGRESS; BENCHMARK DRAFT/NOT FROZEN;
  no automatic TASK02-D/TASK03 or real-time robot test
```
