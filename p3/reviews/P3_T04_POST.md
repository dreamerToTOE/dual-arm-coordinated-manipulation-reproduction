# P3-T04 POST — Feedforward torque law (Eq.27)

**Status**: `PASS` — 20/20 checks.
**Run**: `results/20261020_094329_P3-T04_torque/results.json`
**Command**: `/usr/bin/python3.10 p3/tools/run_t04_torque.py`
**Code**: `baselines/p3_peg_in_hole/control.py` **[ORIGINAL Eq.(27)]** · Oracle: `p3/oracles/oracle_control.py` (explicit index loops)
**Figure**: `p3_t04_terms.png`

## 1. Source fidelity

| Check | Content | Residual |
|---|---|---|
| T04_01 | full law vs independent loop oracle | 8.9e-16 N·m |
| T04_02 | term decomposition: position, perturbation, damping, gravity, friction | 2.8e-17 N·m |
| T04_03 | printed two-`Jᵀ` form ≡ combined `Jᵀ(F_pos+F_pert)` | 0 |
| T04_04 | position term has no component along `R_h e_x` | 1.7e-18 N |
| T04_05 | shifting `Δx` along the push axis leaves `τ` unchanged | 0 |
| T04_09 | gravity enters additively and independently | 2.8e-16 N·m |
| T04_10 | friction compensation enters additively and independently | 2.1e-16 N·m |
| T04_14 | hole-arm gain inside the paper's `500 ≤ k_p ≤ 1000` | 600 N/m |

Terms implemented exactly as printed: `τ = Jᵀ[[Ω,0],[0,I]]K_pΔx + Jᵀ[[R_h,0],[0,R_h]]w − Dq̇ + τ_g + τ_f`,
with `J ∈ R^{6×7}`, `K_p ∈ R^{6×6}`, `Δx,w ∈ R⁶`, `D ∈ R^{7×7}`, `q̇,τ_g,τ_f ∈ R⁷`, all in **N·m** after `Jᵀ`.

## 2. Physical identities

| Check | Content | Residual |
|---|---|---|
| T04_06 | virtual work `(JᵀF)ᵀq̇ = Fᵀ(Jq̇)` | 1.7e-17 W |
| T04_07 | affine response in `w` (fixed state) | 1.8e-15 N·m |
| T04_08 | homogeneous scaling `τ(cw)−τ(0) = c(τ(w)−τ(0))` | 4.9e-15 N·m |
| T04_11 | rank-deficient `J`: `τ` finite, virtual work still exact | 2.1e-17 W |

The identities hold over 300 random states (`p3_t04_terms.png`, right panel), not just one sample.

## 3. No measured force feedback

| Check | Content | Result |
|---|---|---|
| T04_12 | public API has no force-input argument | params = `J, R_h, Kp, dx, w, D, qdot, tau_g, tau_f` |
| T04_13 | injecting `K_f·F_ext` is detected as a deviation from the source law | 6.0e-02 N·m |

The paper states "there is no force feedback term" (p.8571). The implementation therefore accepts
only the user-commanded feedforward wrench; any measured-force term would break T04_01 against the
independent oracle.

## 4. Mutation evidence

| Check | Mutation | Detection |
|---|---|---|
| T04_M1 | sign flip on the perturbation term | 18.28 N·m |
| T04_M2 | transposed wrench frame `R_hᵀ` | 5.81 N·m |
| T04_M3 | missing selector (position control on all axes) | 5.79e-02 N·m |
| T04_M4 | dropped gravity compensation | 8.00 N·m |
| T04_M5 | dropped damping | 0.177 N·m |
| T04_M6 | force/moment blocks swapped in the position command | 9.24e-02 N·m |

## 5. Limitations

- `J = [I₆ | b]` and all gains/damping/gravity/friction values are **TEST_FIXTURE**; this validates the
  algebra and frames of Eq.(27), not any specific robot's torque magnitudes.
- `τ_f` is injected as an external vector (the paper does not specify a friction model).
- No actuator saturation, joint limits, or inertia coupling is modelled; those belong to a dynamic
  simulation, which is out of D082 scope.
