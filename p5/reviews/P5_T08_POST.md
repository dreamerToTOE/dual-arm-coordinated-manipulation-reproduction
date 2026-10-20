# P5-T08 POST — The learned SCA boundary inside the closed-loop QP

**Status**: `PASS` — 13 checks (7 positive / 6 negative), 0 failed, 85 s.
*(Numbers regenerated after the post-delivery audit D019 — see §8; the closed-loop rhs now
implements the D007 calibration `log(Γ_raw/κ)` with its barrier at the learned boundary
`Γ_raw = 0`, not the pre-audit `log(Γ_raw − 1)` with its barrier at `Γ_raw = 1`.)*
**Run**: `p5/evidence/impl_checks/T08.json` (regenerate: `PYTHONPATH=. /usr/bin/python3.10 run_all.py --only T08`)
**Code**: `p5/impl/tasks/t08_sca_closed_loop.py` **[ORIGINAL]** structure + **[ADAPTATION]** scale · reuses
`p5core/qp_ik.py`, `p5core/svm_sca.py`, `p5core/kinematics.py`
**Figures**: `t08_min_gamma.png`, `t08_joint_traj.png`, `t08_grad_check.png`, `t08_events.png`

## 1. What was wired together

```
(17d)   -grad Gamma(q)^{ij} . qdot^{ij}  <=  log(Gamma_cal - 1)      [Q3: +log, not the printed -log]
(26)    grad_q Gamma = (J_right - J_left)^T grad_f Gamma             [feature f = p_right - p_left]
(21a/b) the row enters the QV matrix M and vector b with lambda = 1
(16)    Gamma > 1 free / = 1 boundary / < 1 collision -- and the paper's PAPER_FALLBACK below 1
```

The learned boundary is the **official 2-D CPSP model** (`2d_example.mat`, sha256 `4e9efd5f…021a`,
40 BVs, σ = 0.1, bias = 0) used as an oracle: it is fed the relative position of the two tips, so the
constraint really is the learned model and not a hand-written distance function. `d_Q = 4`, `d_n = 2`,
`d_c = 1`; the model is evaluated in its **native** coordinates — no rescaling, no rotation, no
tuning of the feature map.

## 2. Why the task and the SCA feature must be *different* quantities

This is the design decision that decides whether the test can mean anything at all, and it is not in
the plan. If the SCA feature happened to be the task coordinate itself, then

```
Gamma_dot = grad_f Gamma . f_dot = grad_f Gamma . (J_task qdot)
```

would be **implied by the equality row**: (17d) could never bind, the QP would either accept the task
velocity or declare infeasibility, and the redundant joints would have no way to satisfy the
constraint. The learned boundary would behave like a switch, not like a constraint.

So the fixture is built the way the paper builds it: the **task** drives one arm's tip, while the
**SCA** constrains the tip *pair* — which involves both arms. The second arm's two joints are then
genuine slack for (17d). Measured activation ratio **0.47** and `nu_max = 1.0e-3 > 0`: the constraint is used, not merely satisfied.

## 3. Positive evidence

| Check | Content | Result |
|---|---|---|
| P8.1 | SCA on, λ = 1, literal `+log` form, 8 s | `min_t Γ_raw = **1.3347**`, crossings **0** |
| P8.2 | is the constraint actually binding? | active on **47.0 %** of steps, `nu_max = 1.0e-3 > 0` |
| P8.3 | Eq.(26) vs central difference of `Γ(f(q))`, 400 configs | max rel err **1.2e-09**; `+∇_qΓ` raises `Γ` on **400/400** |
| P8.4 | four event classes, each with evidence for and against | see §5 |
| P8.5 | matched control, SCA **off**, same task and state | `min_t Γ_raw = **−2.3942**`, **656** crossings |
| P8.6 | `PAPER_FALLBACK` on its own (starts at `Γ_raw = −3.015`) | fires; direction right; hard row **infeasible** — see §4 |
| P8.7 | step-size convergence, `dt ∈ {5e-3, 2.5e-3, 1.25e-3}` | `min Γ_raw = 1.33474 / 1.33677 / 1.33743`, successive Δ ≤ **2.0e-03** |

The pair P8.1/P8.5 is the whole result: the same task, the same initial state, the same solver, and
the only difference is whether the learned boundary is in the QP. It is the difference between
`Γ_raw` staying positive at 1.3347 and falling to −2.39 with 656 crossings.

## 4. Three findings that contradict the plan, reported as measured

**(a) `PAPER_FALLBACK` cannot be honoured by a hard-constrained QP.** The paper says: when `Γ < 1`,
"we replace `log(Γ−1)` with a large negative number that pushes the robots outward". With
`PAPER_FALLBACK = −1000` the row becomes `Γ̇ ≥ 1000`. The direction is right — the box vertex along
`+∇Γ` raises `Γ` at **28.2 s⁻¹** — but 28.2 ≪ 1000, so the exact solver reports `INFEASIBLE` and the
robot freezes instead of retreating. The fallback only makes sense in a **soft/penalty** formulation;
implemented as a hard row it is a stop command. This fixture says so explicitly (P8.6) rather than
pretending the mechanism works.

**(b) `λ = 0` is *stricter*, not looser, far from the boundary.** The plan's N8.2 predicted "no
margin ⇒ crossings under discretisation error". Measured: `λ = 0` turns the row into `Γ̇ ≥ 0`, which
forbids *any* decrease, so the approach is blocked at the first step (`min Γ_raw` stays at 6.380,
activity 75 %). The reason is that `λ` multiplies `log(Γ−1)`, which is **positive** for `Γ > 2`: the
`λ = 1` row *grants a budget* to approach, while `λ = 0` grants nothing. The predicted direction of
the effect was wrong and the POST says so.

**(c) The printed `−log(Γ−1)` inverts the request.** Under the D007 calibration the KKT form demands
`Γ̇ ≥ −log(Γ_raw)` and the printed form demands `Γ̇ ≥ +log(Γ_raw)`. At `Γ_raw = 0.01` — right at the
learned boundary — the KKT form demands `Γ̇ ≥ +4.61` (a retreat: the barrier) while the printed form
allows `Γ̇ ≥ −4.61` (an approach); at `Γ_raw = 6.38` the printed form demands a retreat `+1.85` where
the KKT form allows an approach `−1.85`. **The protection vanishes exactly where it is needed** and is
over-tight far away. In closed loop the printed form saturates the velocity box immediately and the
run never gets near the boundary — `min Γ_raw` held at 6.380 by the box, not by the boundary. This is
the closed-loop consequence of the sign error already recorded as D006.

## 5. The four event classes (P8.4)

| Class | Count (SCA on) | Why that number, and where the class is exercised |
|---|---|---|
| `LOG_DOMAIN` | **0** | The log budget binds while `Γ_raw` is still ≈ 2.18, so the motion is deflected long before the domain ends. Exercised by construction in P8.6 (start at `Γ_raw = −3.015`). |
| `QP_INFEASIBLE` | **0** | The barrier is satisfied *inside* the velocity box instead of saturating it. Exercised by N8.1 (701 steps) and N8.3 (1473 steps), so the counter is wired to a live path and is not dead code. |
| `SOLVER_FAILURE` | **0** | Every solve returns a KKT-verified point, max primal residual **8.3e-16**. Never exercised anywhere: the exact enumerator either finds the optimum or proves infeasibility — it has no "gave up" state, which is a property of the solver choice (D010), not of the mechanism. |
| `BOUNDARY_CROSSING` | **0** | Against **656** with SCA off (P8.5), i.e. the counter is proven live by the matched control. |

No class is reported as "0 because nothing happened"; each zero is either explained mechanically or
demonstrated live in another run.

## 6. Negative controls

| Check | Mutation | Result |
|---|---|---|
| N8.1 | flip the sign of `∇_qΓ` (one character) | `min Γ_raw` 1.335 → **−0.021** — an actual boundary crossing — and the run freezes at `t = 4.765 s` |
| N8.2 | `λ = 0` | `min Γ_raw` 6.380, activity 75 % — the cone blocks the approach (§4b) |
| N8.3 | printed `−log(Γ−1)` | demanded rate inverted (rhs table at `Γ_raw ∈ {0.01, 0.2, 1.0, 6.38}`); saturates immediately (§4c) |
| N8.4 | zero-padding defects | length-3 gradient into 2 columns → `ValueError`; arm-2 block written into arm-1 columns → `Γ̇` prediction off by rel **1.03** (P8.3 rejects it) |
| N8.5 | silent clamping | `np.clip` replaced by a tripwire: **0** calls in 60 closed-loop steps (the only `clip` in the package is in the unused SLSQP backend) |
| N8.6 | `dt × 10` | `min Γ_raw` 1.3347 → **1.3126**, crossings 0 → 0: discretisation error is real but small *at this hold point*; no "any step size is perfect" claim is made |

## 7. Fidelity and limits (restated from the plan, all of them load-bearing)

- **`Γ` criterion ≠ geometric clearance.** Passing means the learned boundary of the *2-D model* was
  maintained **on this trajectory**. It is **not** a collision-avoidance guarantee, and no "absolute
  safety margin" is reported: the 2-D model's `Γ` scale has no calibration against the planar arm's
  physical distance.
- **Only arm–arm pairs are modelled** (O12); single-arm self-collision is absent, as in the paper.
  `TPR ≈ 97.4 %` is a statistic about the classifier, not a guarantee.
- **Both tips are point features**, so the "arms" are two material points each; a 4-DOF planar toy is
  not evidence of feasibility on the dual FR3/IIWA hardware.
- The 2-D CPSP model's training set was never published, so the model is used as shipped; nothing here
  retrains it or reproduces Eq.(28).
- `λ = 1` is the reference and **no calibration of `λ` against the paper exists** — the paper gives no
  numerical value, so `λ` is a `ENGINEERING` choice and the λ = 0 comparison is reported as such.
- T09 (FCL/distance constraints) is **not authorised this cycle** and is not part of this result; its
  numbers may never be merged with T08 into a single "SCA reproduction" claim.

## 8. Post-delivery audit (D019) — what changed and why

The first accepted G3 delivery implemented the (17d) rhs as `log(Γ_raw − 1)` with domain `Γ_raw > 1`,
contradicting the G0-approved calibration D007 (`Γ_cal = 1 + Γ_raw/κ`, `κ ≡ 1` ⇒ rhs `= log(Γ_raw)`,
domain `Γ_raw > 0`). The pre-audit barrier therefore sat one unit **above** the learned boundary
`Γ_raw = 0`, and every row was stricter than the approved form. Old → new:

| Quantity | Pre-audit (`log(Γ_raw−1)`) | Calibrated (`log(Γ_raw/κ)`) |
|---|---|---|
| `min_t Γ_raw` SCA on | 2.1813 | **1.3347** (crossings still 0) |
| Row activation / `nu_max` | 50.1 % / 1.1e-3 | **47.0 % / 1.0e-3** |
| dt ladder (`5e-3 → 1.25e-3`) | 2.18127 / 2.18267 / 2.18316, Δ ≤ 1.4e-3 | **1.33474 / 1.33677 / 1.33743, Δ ≤ 2.0e-3** |
| N8.1 (gradient sign flipped) | min 0.986, no crossing, 701 infeasible | **min −0.021 (crossing), 647 infeasible** — a sharper control |
| N8.3 (printed form) infeasible steps | 1473 | 1479 |
| N8.6 (`dt × 10`) | 2.1645 | **1.3126** |
| SCA-off control | −2.3942 / 656 crossings | unchanged |

The acceptance criterion (crossings) never moved and the corrected row is *weaker* away from the
boundary, so this is an implementation fix against an approved decision, not a retune. T10 was
regenerated with the same fix (see `P5_T10_POST.md` §8); the drift guard that keeps the closed loop
bit-identical to `S.log_barrier` is T10/P10.8.
