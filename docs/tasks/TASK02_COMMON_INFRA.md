# TASK02 — Common Interfaces, Logger and Metrics

Status: **IN_PROGRESS — TASK02-A offline slice PASS; TASK02-B/C PASS CANDIDATE; BENCHMARK DRAFT / NOT FROZEN; overall TASK02 not PASS**

## 2026-10-09 TASK02-D closure / current execution override

**TASK02-D = PARTIAL / DEFERRED.** Local4.5 directPhysX post-step and native articulation/
rigid/link/CoreNodes time/count capabilities are available; exactstamp/step binding, reset
identity and USDrefreshorder are notcertified. NoObserver implemented, no newruntime.
[Audit and source signatures](../../reports/TASK02_POST_STEP_API_AUDIT.md).
User assigns this gap to laterformalIsaacmeasurementadaptation and explicitly unblocks offline
P4 mathematical/planning work. The older “only then connect baselines” order below is historical,
not a reason to hold TASK03. Existing A/B/C data semantics stay unchanged; formal metric inputs
still require native qualification. ParentTASK02 remainsIN_PROGRESS; nofullPASS orfreeze.

## 2026-10-09 minimal integration scope

User accepts TASK01 foundation PASS CANDIDATE but does not freeze the formal Benchmark.
Reuse approved Task26 source `631b1f + 5ed0c96` in place; no grasp/regrasp/push redevelopment.

Completed TASK02-A:

- platform-independent SI/xyzw/frame/source state contracts;
- explicit joint identity mapping and dual-arm/object state;
- legacy snapshot conversion, local accepted-source hash guard;
- preserve unavailable/asynchronous semantics, reject false scientific-clock upgrade;
- 14 offline tests plus actual saved-snapshot conversion, no Isaac/ROS run.

[Detailed report and PRIOR-ASSET CHECK](../../reports/TASK02_FOUNDATION_INTERFACE01.md).

Completed TASK02-B (one bounded offline implementation, no Isaac/ROS/MoveIt):

- data-only BaselineCommand with explicit intent, targets/units/frame, clock/deadline and provenance;
- predecessor event/stage semantics, explicit PLANNED/OBSERVED/CONFIRMED/FAILED and causal evidence;
- four-status draft BenchmarkResult, measurement qualification and failure/evidence fields;
- exclusive run directories, metadata/command/event/state JSONL/result JSON, source/artifact hashes,
  explicit trial/seed SET or UNSET and failure retention;
- 19 B tests + 14 A regression tests PASS, actual retained-failure file example and historical state.

**TASK02-B = PASS CANDIDATE.** [POST-TASK REPORT](../../reports/TASK02_EXCHANGE_LOGGING01.md).
No execution binding, scientific success threshold, native timestamp or full TASK02 PASS is inferred.

Completed TASK02-C (one bounded offline implementation fromc7b33b1):

- Task14-derived relative TCP/midpoint/attitude initial drift and max/sample-RMS;
- explicit object tracking positionRMSE; insertion target/axis/progress/lateral/attitude/window metrics;
- ContactWrench/CollisionDistance data-only drafts, explicit frame/SI/point/source/time/validity;
- frame/session/domain/qualification guards, missing/invalid/rejection counts, no zero fill;
- two independent synthetic input formats give identical math; synthetic durationnull;
- all A/B/C regressions72/72PASS (14+19+39), saved metricsJSON/readback/source evidence;
- unchanged A/B semantics/old source/benchmark, no simulator/ROS/MoveIt/control/backend call.

**TASK02-C = PASS CANDIDATE.** [POST-TASK REPORT](../../reports/TASK02_METRICS_MEASUREMENTS01.md),
[metric definitions](../../common/metrics/README.md). Metrics do not automatically declare SUCCESS;
old3mm/5mm/2deg/30ms engineering parameters are not new defaults. Declared-qualified test doubles
are branch coverage only, not native scientific data. Benchmark remains DRAFT / NOT FROZEN.

Remaining order:

1. Review the completed C software slice; any next slice needs separately bounded approval.
2. Bind already available native post-step state sources behind this interface, through a thin
   read-only adapter. This needs separate scope/evidence, not a replacement scene/bridge.
3. Only then connect paper-specific baselines; formal Benchmark numerical freeze stays a
   separately approved research decision.

No TASK02-C live command adapter, force calibration, controller, reset, physical trial or TASK03.
Native metric evidence/attestation, full output export and actual RNG seed control from the
original goal below remain incomplete. B records seed only; it does not control execution RNGs.
Stop after C delivery; do not automatically start TASK02-D/TASK03. Remaining items are not authorization.

## Goal
Create platform-independent contracts used by every baseline.

## Codex actions
Define types/interfaces for:
- DualArmState
- ObjectState
- ContactWrench
- CollisionDistance
- BaselineCommand
- BenchmarkResult

Implement:
- run metadata writer;
- experiment directory creation;
- metric evaluator for Benchmark A/B;
- CSV/JSON/YAML outputs;
- deterministic seed plumbing.

## PASS
Synthetic unit tests show identical metric results independent of platform adapter.
