# P5-T10 POST — The end-to-end numeric chain `τ → LPV DS → virtual object → QP → LVI`

**Status**: `PASS` — 15 checks (9 positive / 6 negative), 0 failed, 172 s.
*(D020/R1/R3 added P10.8's applied-rhs audit rewrite, P10.9 and N10.6 — see §9. The 800-step rollout
is still solved by the **exact active set**, not by integrating Eq.(20); P10.9 quantifies that gap.)*
*(Numbers regenerated after the post-delivery audit D019 — see §8.)*
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
(17d)     -grad_q Gamma . qdot <= log(Gamma_raw / kappa)    T08 + Eq.(26) from T07  (kappa = 1, D007)
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
| P10.2 | end-to-end, learned boundary in the QP | `min_t Γ_raw = **1.0043**`, **0** crossings, row active on **96.9 %** of the steps, and the calibrated row is feasible on **all 800** steps — no freeze, no drop ever fired |
| P10.3 | matched SCA-off control | `min_t Γ_raw = **−2.3147**`, **534** crossings (same state, object motion, `dt`, solver) |
| P10.4 | sub-task consistency | `τ` vs an independent RK4 of Eq.(8) driven by the recorded `G`: `8.5e-04`; `Γ` recomputed from the recorded joints: `0.0`; per-step KKT residual `3.2e-16` |
| P10.5 | Theorem-3 identity *at every QP solution* | `max abs(ψ − YᵀU) = 3.3e-16` (relative `6.5e-16`): the active-set solution is the LVI fixed point, so `YᵀU` collapses onto `ψ` and `V̇` onto 0 instantaneously |
| P10.6 | the plan's ledger, fully accounted | `∫YᵀU dt − ΔV − ∫ψ dt = +0.0153` while `ΔV = −0.0153`; `residual + ΔV = **4.9e-17**`, i.e. the whole non-closure *is* the quasi-static jump of the multiplier vector (D017) |
| P10.7 | fallback attribution | **no step was ever infeasible**, so freeze/drop never fires and the crossing-free outcome is attributable to the row alone; the fallback machinery is exercised by the negative controls instead (N10.4: 594 steps; T08/N8.1: 647) |
| P10.8 | applied-rhs audit (rewritten by D020/R1) | over all **800** row-bearing steps the audit reads the **`QP` object**, not a re-derivation: pre-solve `Γ_raw` recomputed from the joints `0.0`, calibrated `Γ_cal = 1 + Γ_raw/κ` `0.0`, joint-space gradient `0.0`, (17d) reconstructed from that `Γ` vs the **applied** rhs `0.0`, vs `S.log_barrier` `0.0`, assembled inequality `−g·q̇ ≤ λ·rhs` `2.2e-16`, `λ = 1` |
| P10.9 | LVI (Eq.19/20) vs the active set on **the loop's own instances** | 16 instances re-solved (4 nearest min-`Γ`, 6 with an active row, 6 uniform; `Γ_raw ∈ [1.004, 4.237]`): the active-set answer is the LVI fixed point to **2.8e-16** on every one; the Eq.(20) flow reaches `7.0e-10` at best and agrees to `4.2e-09` where it reaches `1e-6`; **0/16** reached `1e-10` (limitation, §9c) |

P10.2 / P10.3 is the result. The same task, the same initial state, the same solver, and the only
difference is what the QP is allowed to know: `Γ` stays positive at 1.0043 against `−2.31` with 534
crossings when the row is removed.

## 4. Three findings that the plan did not predict, reported as measured

**(a) The hard (17d) row is feasible on every step once the calibration of D007 is honoured.** The
first accepted version of this task used the uncalibrated rhs `log(Γ_raw − 1)` (domain `Γ_raw > 1`),
which silently moved the barrier one unit above the learned boundary `Γ_raw = 0` and made the QP
infeasible on 370/800 steps. After the audit fix (`log(Γ_raw/KAPPA)`, D019) the row is feasible on
**all 800** steps and the freeze/drop fallback never fires. The earlier "46 % infeasible" was an
artifact of the offset, not a property of the paper's mechanism. What remains true is the structural
lesson: a hard barrier row whose demand `Γ̇ ≥ −log(Γ_raw/κ)` grows without bound as `Γ_raw → 0⁺` has
no slack, so feasibility near the boundary is a property of the fixture's null space (2 dims here),
not a guarantee; the fallback policies stay in the code and are exercised by the negative controls.
The standing rule survives the fix: **no timing or tracking-quality claim is drawn from these runs**.

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
| N10.5 | `dt` doubled | `min Γ 1.0043 → 1.0042`, `t_switch 2.800 → 2.820 s`: the step size is really in the loop, and no "step-size independent" claim is made |
| N10.6 | **replace the applied rhs with `log(Γ_raw − 1)`** (D020/R1) | the P10.8 audit **fails on it**: over 200 mutated steps the reconstructed (17d) diverges from the applied rhs by **0.483** and from `S.log_barrier` by **0.483**, while the `Γ` reconstruction stays exactly `0.0` — i.e. the audit reads the solver's input, so the D019-class drift can never pass silently again |

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
cd p5/impl && PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T10     # ~172 s, 15 checks
cd p5/impl && PYTHONPATH=. /usr/bin/python3.10 run_all.py                # ~296 s, 116 checks, G1-G4
```

## 8. Post-delivery audit (D019) — what changed and why

The first accepted G4 delivery (`8a64c38c`) passed 12 checks with the uncalibrated rhs
`log(Γ_raw − 1)`. The post-delivery adversarial audit found that this contradicted D007 (the G0-approved
calibration `Γ_cal = 1 + Γ_raw/κ`, `κ ≡ 1`), silently moving the barrier to `Γ_raw = 1`, one unit above
the learned boundary. Effects of the fix, old → new:

| Quantity | Pre-audit (`log(Γ_raw−1)`) | Calibrated (`log(Γ_raw/κ)`) |
|---|---|---|
| `min_t Γ_raw` SCA on | 2.0700 | **1.0043** |
| QP infeasible steps (SCA on) | 370/800 (46 %) | **0/800** |
| Row activation | 53.1 % | **96.9 %** |
| Theorem-3 identity residual | 9.1e-13 | **3.3e-16** |
| Theorem-3 ledger non-closure | −328.4 (ΔV = −0.0466) | **+0.0153** (ΔV = −0.0153, unexplained 4.9e-17) |
| Boundary crossings (SCA on / off) | 0 / 534 | **0 / 534** (unchanged) |
| `t_switch`, `τ` checks, λ = 0 direction | — | unchanged |

The acceptance criterion (crossings) never moved, the corrected row is *weaker* away from the boundary,
and the negative controls got sharper — this is an implementation fix against an approved decision, not
a retune. T08 was regenerated with the same fix; its audit numbers are in `P5_T08_POST.md` §8.

## 9. Independent review round 2 (D020) — R1, R2, R3

The second review was right on the substantive point: **P10.8 as delivered compared two derived
values and never touched the number the solver received.** What follows is what changed.

### 9a. R1 — the audit now reads the QP, and is proven to catch the mutation

The rollout records, per step, from the `QP` object itself (`qp.sca_rows[0][1]`, `qp.lam`): the
pre-solve `Γ_raw`, the calibrated `Γ_cal = 1 + Γ_raw/κ`, the embedded joint-space gradient, the
applied joint velocity, and the rhs. The audit then independently reconstructs everything from
`q_pre = q0 if k == 0 else q[k−1]` — note the QP uses **pre**-integration state, the old check used
the post-integration history — and compares five ways. Measured over 800/800 row-bearing steps:

| comparison | max diff |
|---|---|
| `Γ_raw` recomputed from `q_pre` vs recorded pre-solve value | **0.0** |
| calibrated `Γ_cal = 1 + Γ_raw/κ` vs recorded | **0.0** |
| embedded gradient `embed_pair_gradient(∇_qΓ)` vs the row's `g` | **0.0** |
| (17d) reconstructed from the recomputed `Γ` vs the **applied** rhs | **0.0** |
| applied rhs vs `S.log_barrier` | **0.0** |
| assembled inequality `−g·q̇ ≤ λ·rhs` at the applied `q̇`, `λ = 1` | **2.2e-16** |

The mutation test **N10.6** re-runs 200 steps with the rhs actually assembled as
`log(Γ_raw − 1)` and demands that P10.8's audit notice: reconstruction diverges by **0.483**, the
helper comparison by **0.483**, `Γ` reconstruction stays `0.0`. It fails the audit by construction, so
a D019-class drift is now a red suite rather than a silently green one.

### 9b. R2 — three different "boundaries", kept apart

- **SVM classification boundary `Γ_raw = 0`** — `Γ_raw(q)` *is* the learned decision function
  (`bias = 0`); "positive class" means `Γ_raw > 0`. A property of the model, not of the dynamics.
- **Logarithmic domain boundary `Γ_raw = 0`** — `log(Γ_raw/κ)` has its singularity there.
- **Continuous-time forward-invariant threshold `Γ_raw = 1`** — for `Γ̇_raw ≥ −log Γ_raw`,
  `V(Γ) = Γ log Γ − Γ + 1 ≥ 0`, `V(1) = 0`, `V̇ = log(Γ)·Γ̇ ≥ −(log Γ)² ≤ 0`, and at `Γ = 1` the bound
  reads `Γ̇ ≥ 0`, so `[1, ∞)` is forward invariant. The **pre-audit** form `−log(Γ_raw − 1)` had its
  analogous threshold at `Γ_raw = 2`.

Measured on this run: `min_t Γ_raw = 1.0043`, **0/800 steps below `Γ_raw = 1`** (margin `+0.0043`),
**0/800 below `Γ_raw = 0`** — stated as *observations on this trajectory*, with the acceptance
criterion still the empirical per-step `Γ_raw < 0` crossing count. No finite-step safety claim is
derived from the continuous-time argument: the fixture integrates forward Euler at `dt = 10 ms`, and
the invariance lemma says nothing about a discretisation with this step.

### 9c. R3 — the loop does **not** run an LVI controller, and P10.9 says so

The execution path is `qp.solve_active_set()`; the LVI fixed-point conditions are evaluated
afterwards (that is P10.5's identity). That is not "solving each QP with Eq.(20)", and no claim of an
LVI-dynamics rollout is made anywhere.

P10.9 re-solves 16 of the **actual** instances captured in this rollout (4 nearest min-`Γ`, 6 with an
active SCA row, 6 uniform; `Γ_raw ∈ [1.004, 4.237]`) with the Eq.(20) RK4 flow, protocol
`dt = 5e-3 / 20 000` steps plus one retry at `dt = 1e-3 / 60 000`:

- the active-set answer is the LVI fixed point to **2.8e-16** on every instance — so the *fixed point*
  is identical;
- the Eq.(20) **flow** is slow: best fixed-point residual `7.0e-10` (agreeing with the active set to
  `4.2e-09`), worst **0.76**, and **0/16** reached the `1e-10` tolerance within the budget;
- a third probe at `dt = 2e-4 / 100 000` steps was *worse* (≥ `1.2e-3`), because the same step budget
  covers less ODE time — this is stiffness of the `(I + Mᵀ)` dynamics near the log barrier, not a
  step-size tuning problem;
- total cost of the 16 re-solves: **63.7 s**, i.e. ≈ 4 s per instance at these settings, against
  ≈ 2 ms per active-set solve in the loop.

**Limitation, recorded rather than papered over:** the LVI-dynamics route is not viable as this
fixture's per-step solver (it would be ~2000× slower and still not converge to the stated tolerance),
so the closed loop keeps the exact fixed-point solve — which is exactly what the official solver does
(one QP per cycle). "An LVI controller executed the 800-step rollout" must not be written anywhere;
what is supported is "each step's LVI fixed point is solved exactly, and the fixed point coincides
with the active-set solution to 2.8e-16."

### 9d. R4 — documentation and test integrity

- §1's equation block printed the stale `log(Gamma_raw − 1)`; corrected to `log(Gamma_raw/κ)` with
  `κ = 1` (D007).
- P10.7's verdict printed the **reference** run's infeasibility count (`0`) where the N10.4
  counterfactual belongs (**594**); fixed.
- N10.3 confirmed to build an in-memory `fake` result dict and call `run_all.evaluate_gates` on it —
  the only disk access in that check is a read-only `_load_status` of `T01–T08`.
- P10.7's gate was tightened from prose to logic: `ref_ok` (0 crossings, `min Γ > 0`, and
  `sum(INF_NOROW_*) == QP_INFEASIBLE` when the latter is non-zero) is now required on **every**
  branch, so a crossing or an *unattributed* infeasibility fails the check; the strong branch still
  needs `QP_INFEASIBLE == 0` **and** `ROW_DROPPED == 0`, so a crossing-free outcome obtained by frozen
  motion cannot be reported as an SCA-only result.
