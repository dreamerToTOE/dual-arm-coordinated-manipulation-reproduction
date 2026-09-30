# TASK01 — Freeze Benchmark V1

Status: IN_PROGRESS (candidate study; benchmark_v1 not yet reviewed or frozen)

## Current progress (2026-09-30)
- User confirmed the existing Task27 dual-FR3, L-side-suction and truck-box scene as the **geometric starting point**, not as a wholesale approval of its numerical parameters or thresholds.
- Draft candidate: `configs/benchmark/benchmark_v1.yaml`; analytic checker: `scripts/validate_benchmark_candidate.py`.
- Initial static geometry passed with 30 unresolved fields. After recording the user-confirmed B-fixture/B-center contact split, the latest static check still passes and has 36 unresolved fields (new alignment/force gates were made explicit). Fresh Isaac contact/geometry validation has not been run in this repository.
- The benchmark remains **DRAFT / IN_PROGRESS**. No paper baseline may use it as a frozen common test yet.

## Goal
Freeze one common dual-FR3 Cube/carriage benchmark before tuning any paper method.

## Codex actions
- Define FR3 base poses.
- Define cube size, mass and friction/contact parameters.
- Define left/right grasp transforms.
- Define carriage geometry and entrance frame.
- Define PRE_PUSH and insertion target/depth.
- Define physics dt, control dt and seed policy.
- Define all success/failure tolerances for Benchmark A/B.
- Define C0–C5 insertion perturbations.
- Validate geometry in Isaac; validate P2/P3 reduced version in MuJoCo if needed.

## Outputs
- `configs/benchmark/benchmark_v1.yaml`
- benchmark scene notes.
- benchmark hash/version.

## PASS/FROZEN
All values reviewed by user. Then mark FROZEN. Any later change requires DECISIONS entry and benchmark version bump.
