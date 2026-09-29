# TASK02 — Common Interfaces, Logger and Metrics

Status: TODO

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
