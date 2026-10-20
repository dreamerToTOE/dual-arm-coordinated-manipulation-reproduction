# P5-T10 POST — The end-to-end numeric chain `τ → LPV DS → virtual object → QP → LVI`

**Status**: `PASS` — 12 checks (7 positive / 5 negative), 0 failed, 142 s.
**Run**: `p5/evidence/impl_checks/T10.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T10`)
**Code**: `p5/impl/tasks/t10_e2e.py` **[ORIGINAL]** equations + **[ADAPTATION]** fixture and scales ·
reuses `p5core/{tau,lpv,multiarm_ds,kinematics,qp_ik,lvi,svm_sca}.py`
**Figures**: `t10_e2e_triptych.png`, `t10_phase.png`, `t10_sca_ablation.png`

## 1. What the chain actually is

```
Eq.(8)    tau_dot = tau (1 - tau) G / k                     T01, integrated (not switched)
Eq.(2)    xdot_i^R = taudot_i e + tau_i xdot^V + A (p_i - x*_i - tau_i e)   T02
Eq.(15)   gammadot = (1 - gamma) / (|x^O - x*| + eps)       T03
Eq.(36)   xdot^V = R(gamma, gammadot, x^O, xdot^O, x^V)     T03
Eq.(17)   min ||qdot||^2  s.t. J qdot = xdot^R, box         T04 (exact active set)
(17d)     -grad_q Gamma . qdot <= log(Gamma_raw - 1)        T08 + Eq.(26) from T07
(19)-(23) LVI assembly; multipliers read back               T05
```

Fixture (all `ADAPTATION`, no hardware): two 3R planar arms, links `0.60 / 0.45 / 0.35`, bases at
`(0,0)` and `(1.6,0)`, `d_Q = 6`, `d_n = 4` (both tips), `d_c = 1`. Object starts at `(1.25, 0.75)`
and is driven to `x* = (0.95, 0.25)`; the goal tip separation is `(0.28, 0.41)`. `τ` starts at
`ε = (0.02, 0.03)` per arm, `k = 0.8`, `A_ARM = -0.35 I`, `|xdot_tip| <= 0.15 m/s`,
`|qdot| <= 1.5 rad/s`, `dt = 10 ms`, `T = 8 s` (800 steps), `λ = 1`.

The learned boundary is the **official 2-D CPSP model** (`2d_example.mat`, sha256 `4e9efd5f…021a`)
evaluated in its native coordinates on the relative position of a body-point pair.

## 2. Two fixture decisions that make the test mean something

**(a) The pair is chosen before any constrained run, by a rule that uses only the *uncontrolled*
trajectory.** Among the 15 mixed pairs (3 left × 3 right body points) keep those with
`Γ_raw(t=0) > 1.5`, `min_t Γ_raw < -0.5` on the SCA-off run (otherwise the constraint is never
exercised) and a null-space share `>= 0.10` over the whole path (otherwise (17d) is implied by the
task equality and the QP can only freeze). The rule selects **left tip vs right elbow (`L3–R2`)**,
`Γ_raw(0) = 4.2255`, share 0.21. The candidate table is written into the evidence, so the choice can
be re-audited; it is not tuned against the outcome.

**(b) `τ` is integrated, never switched.** Eq.(8) is a logistic field with equilibria at 0 and 1, so
the asynchronous→synchronous transition has to *emerge*. N10.2 pins `τ ≡ 1` and `τ ≡ 0` and shows the
switch disappears in both cases (see §4), which is what makes P10.1 a measurement rather than a label.

## 3. Positive evidence

| Check | Content | Result |
|---|---|---|
| P10.1 | switch observable, not hand-placed | `τ: (0.02,0.03) → (0.982,0.988)`, monotone (min increment `7.6e-06`), `t_switch = **2.800 s**` inside the pre-declared window `[1,5] s`; the pair starts approaching the boundary at `0.02 s`, i.e. *before* the switch (reported side by side, not forced to coincide) |
| P10.2 | end-to-end, learned boundary in the QP | `min_t Γ_raw = **2.0700**`, **0** crossings, row active on **53.1 %** of steps — with its cost disclosed: the hard row makes the QP `INFEASIBLE` on **370/800** steps (§4a) |
| P10.3 | matched SCA-off control | `min_t Γ_raw = **−2.3147**`, **534** crossings (same state, object motion, `dt`, solver) |
| P10.4 | sub-task consistency | `τ` vs an independent RK4 of Eq.(8) driven by the recorded `G`: `8.5e-04`; `Γ` recomputed from the recorded joints: `0.0`; per-step KKT residual `1.6e-14` |
| P10.5 | Theorem-3 identity *at every QP solution* | `max abs(ψ − YᵀU) = 9.1e-13` (relative `3.7e-17`): the active-set solution is the LVI fixed point, so `YᵀU` collapses onto `ψ` and `V̇` onto 0 instantaneously |
| P10.6 | the plan's ledger, fully accounted | `∫YᵀU dt − ΔV − ∫ψ dt = **−328.4**` while `ΔV = −0.0466`; `residual + ΔV = **2.8e-14**`, i.e. the whole non-closure *is* the quasi-static jump of the multiplier vector (D017) |
| P10.7 | counterfactual on the infeasible steps | row **dropped** instead of frozen on 368 steps: `min_t Γ_raw = **1.2400**`, **0** crossings — the guarantee survives without the freeze (§4a) |

P10.2 / P10.3 / P10.7 is the result. The same task, the same initial state, the same solver, and the
only difference is what the QP is allowed to know: `Γ` stays positive at 2.07 (freeze policy) or 1.24
(row-dropped, no freeze at all) against `−2.31` with 534 crossings when the row is removed.

## 4. Three findings that the plan did not predict, reported as measured

**(a) The hard (17d) row makes the QP infeasible on 46 % of the steps — and the counterfactual says the
row still carries the guarantee.** `370/800` steps are `INFEASIBLE`, and the attribution is
unambiguous: the same QP **without** the row is `OPTIMAL` on all 370, and the reference velocity on
those steps is at most `0.0279` (so it is not the velocity box). The mechanism is the one already
recorded for T08 (D016): `log(Γ_raw − 1)` *shrinks* as `Γ` approaches 1, so the row demands
`Γ̇ ≥ −log(Γ−1)` from a hard equality `J q̇ = ẋ^R` that has only a 2-dimensional null space to spend.
A hard row with no slack is therefore routinely unsatisfiable — the paper's formulation is only usable
soft. Because a freeze policy (`q̇ = 0`) would make "0 crossings" look like an artefact, the same run
is repeated with the row *dropped* on exactly those steps: `min Γ = 1.2400`, still 0 crossings. So the
freeze is conservative, **not** the mechanism (D018). It does, however, invalidate any timing or
tracking-quality claim from this run: on 46 % of the steps the arms do not move.

**(b) `λ = 0` does not produce crossings; it blocks the approach.** `min Γ_raw = 4.2235` (vs 2.0700)
with 0 crossings and `594` infeasible steps (vs 370). `λ` multiplies `log(Γ−1)`, which is positive for
`Γ > 2`, so `λ = 1` *grants* a decrease budget while `λ = 0` turns the row into `Γ̇ ≥ 0`. The plan's
N10.4 predicted "crossings rise"; the measured direction is the opposite one. Reported as falsified,
not engineered into a crossing (same finding as T08/N8.2).

**(c) The e2e loop is quasi-static, so Theorem 3 cannot be a ledger here.** The identity holds at every
QP solution (P10.5) and the ledger's entire residual is `−ΔV` (P10.6). What the loop does *not* do is
integrate the projected dynamical system (20); it re-solves the QP from the new state each step. So
`V` jumps between fixed points of a time-varying LVI instead of flowing. Any future claim that
"`V̇ ≤ 0` in the closed loop" would be a statement about a flow this implementation does not have.

## 5. Negative controls

| Check | Mutation | Result |
|---|---|---|
| N10.1 | remove the (17d) row | crossings `0 → 534`, `min Γ 2.0700 → −2.3147` — the counter is proven live |
| N10.2 | pin `τ ≡ 1` / `τ ≡ 0` | **no** switch in either run (`t_switch = None`), against 2.800 s with Eq.(8) |
| N10.3 | doctor `T08` to `FAIL` on disk | `run_all.evaluate_gates` returns `BLOCKED_BY_UPSTREAM` for G4; with the real disk state T01–T08 are 8/8 `PASS` |
| N10.4 | `λ = 0` | `min Γ 4.2235`, 0 crossings, 594 infeasible — direction falsified (§4b) |
| N10.5 | `dt` doubled | `min Γ 2.0700 → 2.0600`, `t_switch 2.800 → 2.820 s`: the step size is really in the loop, and no "step-size independent" claim is made |

## 6. Fidelity, labels and limits

- **`Γ` criterion ≠ geometric clearance.** Passing means the learned 2-D boundary was maintained on
  *this* trajectory. It is not a collision guarantee, and no absolute safety margin is quoted.
- **6-DOF planar toy, velocity level.** No dynamics, no torque limits, no friction, no 12-DOF FR3/IIWA.
  Nothing here is evidence of hardware feasibility.
- **The learned model is used as shipped**; its training set was never published, so Eq.(28) is not
  reproduced and the model is never retrained.
- **`A_ARM = −0.35 I`, `A_V = −1.5 I`, `k = 0.8`, `V_MAX_TIP = 0.15`, `|q̇| ≤ 1.5`, `λ = 1`** are
  `ENGINEERING`/`ADAPTATION` choices: the paper publishes no numerical value for any of them.
- **`τ` enters indirectly.** Per D014, `(11) → (36)` presumes the shared-velocity premise; the e2e run
  deliberately exercises the *asynchronous* regime first (`τ` starts at 0.02/0.03), so a broken `τ`
  coupling cannot hide behind (36).
- **T09 is `NOT_AUTHORIZED_THIS_CYCLE`** and its distance-constraint numbers may never be merged with
  this result into a single "SCA reproduction" claim.
- **Ceiling**: this is `ALGORITHM_NUMERICAL_VERIFIED (D082)`. `FULL_PAPER_REPRODUCED` remains abandoned
  (hardware + unpublished training set + CVXGEN).

## 7. Reproduce

```bash
cd p5/impl && PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T10     # ~142 s, 12 checks
cd p5/impl && PYTHONPATH=. /usr/bin/python3.10 run_all.py                # ~344 s, 115 checks, G1-G4
```
