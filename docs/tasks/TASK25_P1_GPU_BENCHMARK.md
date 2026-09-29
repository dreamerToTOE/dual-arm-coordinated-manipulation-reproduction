# TASK25 — P1 GPU Benchmark

Status: TODO

## Goal
Measure whether P1 meets the real-time requirement on the actual GPU.

## Codex actions
- Separate initialization/JIT/warm-up from steady-state timing.
- Sweep prediction horizon, sample count and relevant batch parameters.
- Report mean, p95, p99 latency and control frequency.
- Record GPU model, driver, CUDA and utilization.

## PASS
A reproducible timing envelope and selected benchmark configuration are documented.
