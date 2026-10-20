# P3-T01 POST — Perturbation patterns (Eq.16–22)

**Status**: `PASS` — 21/21 checks.
**Run**: `results/20261020_093347_P3-T01_patterns/results.json`
**Command**: `/usr/bin/python3.10 p3/tools/run_t01_patterns.py`
**Code**: `baselines/p3_peg_in_hole/patterns.py` **[ORIGINAL]** · Oracle: `p3/oracles/oracle_patterns.py` (scalar closed forms, no production imports)
**Figures**: `p3/evidence/figures/p3_t01_patterns_time.png`, `p3_t01_spiral.png`

## 1. Positive evidence

| Check | Content | Residual | Unit |
|---|---|---|---|
| T01_01 | push vs closed form (6 sample times) | 0 | N |
| T01_02 | rub vs closed form | 0 | N·m |
| T01_03 | wiggle vs closed form | 0 | N·m |
| T01_04 | spiral vs closed form | 0 | N |
| T01_05 | Eq.(18) general form vs per-component loop | 0 | mixed |
| T01_06 | push constant in time (a=b=c=0) | 0 | N |
| T01_07 | rub zero mean over 20 integer periods | 4.7e-08 | N·m |
| T01_08 | wiggle quadrature `w4²+w5²=f²` | 3.5e-16 | N²·m² |
| T01_09 | spiral radius `= |f_spiral(t)|` | 4.4e-15 | N |
| T01_10 | spiral modulation `a1=a2=α sin(vt)+β` | 0 | N |
| T01_11 | `b=0` constant mode legal | 0 | mixed |
| T01_12 | `β<0` accepted (no invented positivity domain) | 2.2e-15 | N |
| T01_13 | axis placement: push→fz, rub→mz, wiggle→mx,my, spiral→fx,fy | behaviour | — |

## 2. Negative / mutation evidence

| Check | Content | Result |
|---|---|---|
| T01_N1 | NaN amplitude | rejected |
| T01_N2 | inf frequency | rejected |
| T01_N3 | wrong shape (5,) | rejected |
| T01_N4 | non-finite time | rejected |
| T01_N5 | unknown pattern kind | rejected |
| T01_M1 | phase/frequency swapped (b↔c) | **detected** (3.08e-01 N·m) |
| T01_M2 | amplitude scaled by ½ | **detected** (9.11e-02 N·m) |
| T01_M3 | π/2 phase on mx instead of my | **detected** (3.53e-01 N·m) |

The mutation tests fail on the *checker* only when the pattern is wrong; the unmutated patterns
pass at 1e-14 or better, so the suite is not vacuous.

## 3. Notes on fidelity

- `f_rub` is a **moment** amplitude (N·m) because the rub pattern acts on `w6`; the name `f_*`
  in the paper does not imply force units. Recorded explicitly to keep units separated.
- The spiral's amplitude is itself time-varying (Eq.22), so `a` cannot be treated as the constant
  vector declared in Eq.(18). Implementation uses `a(t)`; documented as **[ORIGINAL: Eq.22 wins]**.
- No numeric value from the paper exists for any pattern parameter → all fixture numbers are
  `TEST_FIXTURE` and the figures carry that label.

## 4. Limitations

Component-level only: no contact, no robot motion, no claim about insertion behaviour or the
paper's experiments. The patterns are validated at the commanded-wrench level.
