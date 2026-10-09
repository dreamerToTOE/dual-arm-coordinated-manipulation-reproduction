# TASK02 — Common Interfaces, Logger and Metrics

Status: **IN_PROGRESS — TASK02-A offline state/provenance slice PASS; overall TASK02 not PASS**

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

Remaining order:

1. Unified command/result/event and minimal logger/metadata contracts, offline adapters first.
2. Shared metric functions with synthetic cross-platform tests; accept thresholds from explicit
   configuration only, never import legacy acceptance values as scientific defaults.
3. Bind already available native post-step state sources behind this interface, through a thin
   read-only adapter. This needs separate scope/evidence, not a replacement scene/bridge.
4. Only then connect paper-specific baselines; formal Benchmark numerical freeze stays a
   separately approved research decision.

No TASK02-A live command adapter, force calibration, controller, reset or physical trial.
`ContactWrench`, `CollisionDistance`, `BaselineCommand`, `BenchmarkResult`, formal logger/metrics
and seed plumbing from the original goal below are not yet claimed complete.

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
