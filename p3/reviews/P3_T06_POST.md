# P3-T06 POST — Deterministic numerical integration (Eq.16–28)

**Status**: `PASS` — 12/12 checks (metrics corrected 2026-10-20, review R2).
**Run**: `results/20261020_104237_P3-T06_integration/results.json` (+ 4 CSV traces)
**Superseded run (preserved)**: `results/20261020_094514_P3-T06_integration/results.json`
**Command**: `/usr/bin/python3.10 p3/tools/run_t06_integration.py`
**Figures**: `p3_t06_case1_trace.png`, `p3_t06_case_sequences.png`

## 1. Pipeline under test

```
pattern (T01, Eq.16-22) → stage composition (T02, Eq.23-26) → A1 frame relabelling
→ Ω selection + wrench rotation (T03, Eq.27-28) → torque law (T04, Eq.27)
```
All four modules are the production modules already validated in T01–T04; the driver
adds no new algorithm code.

## 2. Results

| Check | Content | Result |
|---|---|---|
| T06_01 | every documented stage of every case exercised (no dead branch) | 12 stage blocks, none missing |
| T06_02 | clock monotone, uniform `dt = 0.01 s`, attribution matches schedule | 2.0e-15 s |
| T06_03 | per-sample wrench = composition oracle | 0 |
| T06_04 | per-sample torque = independent oracle (A1 mapping explicit) | < 1e-12 N·m |
| T06_05 | all samples finite; max component and vector norm separated | `max_{t,k}\|τ_k\| = 10.152 N·m`, `max_t‖τ‖₂ = 12.590 N·m`; `max_{t,i}\|F_i\| = 10.00 N`, `max_t‖F‖₂ = 11.18 N`; `max_t‖m‖₂ = 0.391 N·m` |
| T06_06 | position command never acts along the push axis | < 1e-12 N |
| T06_07 | second full pass bitwise identical (sha256 of numeric rows) | identical |
| T06_08 | per-stage sample counts, durations and magnitudes recorded | JSON `per_stage_stats` |
| T06_09 | A1 mapping composes as `R_h·R_task→hole` in the perturbation term | 0 |
| T06_N1 | dropping search+align from case 1 is detected | detected |
| T06_N2 | overlapping/backwards clocks rejected | rejected |
| T06_N3 | out-of-range sampling rejected (not clamped) | rejected |

Chronology (case 1): approach 0–3.2 s (push 10 N only) → search 3.2–10.5 s (+spiral in fx/fy)
→ align 10.5–16.5 s (+wiggle mx/my, +rub mz) → insert 16.5–17.5 s (push only). Joint torques stay
bounded (`max_{t,k}|τ_k| = 10.152 N·m`, `max_t‖τ‖₂ = 12.590 N·m`) and follow the command components with no discontinuity other than the
reported stage jumps.

## 3. What this does and does not establish

**Establishes**: the four documented stage sequences can be routed through one deterministic,
independently validated pipeline; every documented stage is exercised; commands and torques are
finite, clock-consistent and reproducible bit-for-bit.

**Does not establish** (explicit, per the review decision):
- any object motion, peg trajectory, contact state or insertion outcome;
- Fig.9/Fig.11 trajectory agreement (no calibrated dynamics, no digitized measurements);
- the paper's 87% success rate or 13.86 s mean time (50-DOF hardware, different sensing);
- automatic stage recognition (switching remains an externally prescribed script: **[ADAPTATION]**).

The commanded traces are **not** the original robot trajectories. All state values (`Δx`, `q̇`, `J`,
gains, damping, gravity, friction) are **TEST_FIXTURE**.

## 4. Notes

- `T06_06` exposed a real subtlety worth recording: the push axis must be evaluated as
  `R_h·(R_task→hole·e_z)`, not as `R_h·R_task→hole·e_x`; the first attempt of this check used the
  wrong basis vector and failed spuriously. The implementation was correct (T06_09); the check was
  fixed, not the algorithm.
- Without the A1 relabelling (`R_task_to_hole=None`), the same pipeline runs but the selection axis
  and the push axis are expressed in different conventions; that literal variant is retained in
  `control.py` for audit and is *not* used for the integration traces.
