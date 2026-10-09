# TASK02 — Common Interfaces, Logger and Metrics

Status: **IN_PROGRESS — TASK02-A offline slice PASS; TASK02-B PASS CANDIDATE; overall TASK02 not PASS**

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

Remaining order:

1. Shared metric functions and remaining measurement contracts with synthetic cross-platform tests; accept thresholds from explicit
   configuration only, never import legacy acceptance values as scientific defaults.
2. Bind already available native post-step state sources behind this interface, through a thin
   read-only adapter. This needs separate scope/evidence, not a replacement scene/bridge.
3. Only then connect paper-specific baselines; formal Benchmark numerical freeze stays a
   separately approved research decision.

No TASK02-B live command adapter, force calibration, controller, reset, physical trial or TASK03.
`ContactWrench`, `CollisionDistance`, scientific metric evaluation, full output export and actual
RNG seed control from the original goal below are not yet complete. B records seed only;
it does not control execution RNGs. Stop after delivery; remaining items are not current authorization.

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
