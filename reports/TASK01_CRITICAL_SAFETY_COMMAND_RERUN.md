# TASK01 — One Command-Only Critical-State Safety Rerun

2026-10-08. **TASK01 = PARTIAL; Critical-state Isaac safety = FAIL; READY/reset = BLOCKED_BY_SHARED_HOLD_SEMANTICS.** The additional allowance **1/1 is consumed**. Stop for user; no new probe/retry. The preparation section below is retained history.

## PRE-TASK REPORT

- Task: TASK01; four-state Isaac safety sanity only.
- Scientific objective/minimum sufficient evidence: at the recorded START0, PRE_PUSH135, state196/B60 and TARGET292, find no obvious unexpected robot/tool–environment collision that invalidates the nominal single-Cube benchmark.
- Current scope: reuse the existing controlled replay harness and actual recorded14q/Cube pose; one original normal PhysX step per state; visible GUI; maximum120s including startup/close.
- Non-goals: READY/reset repetitions, held-object/suction stability, force/wrench/P2/P3, five-Cube Task27, new probes, static-query/native-handle repair, geometry/model/ACM/physics/IK changes.
- Attempt budget: previous static07/08/09 remains exhausted3/3 and previous controlled attempt remains used1/1. Exactly one newly authorized **launcher-only additional attempt1/1**; no repair/retry if it fails.
- Preferred/fallback method: same existing controlled harness, stdin supplied through a pipe rather than backgroundTTY; no further fallback authorized.
- Stop/escalation: original collision/measurement guards remain intact; first unexpected collision or new engineering failure stops. After the fourth safety snapshot is saved, deliberately supply `stop` at the existing review barrier, before screenshot/UI refresh or RESET. No fifth physics step/reset is authorized.
- Files expected to change: records/reports/run metadata only; **harness and launcher source remain unchanged**.
- Validation: unchanged source/input hashes, existing pure classification tests, four raw state snapshots with actual q/TCP/Cube drift/contact/overlap and actual post-step simulation time; independently audit after the process closes. Never infer safety from wrapper exit0.
- Known risks: free dynamic Cube has no shared-held constraint and previously fell2.725mm in one step. Automated `accept_snapshot` tokens only let the next approved safety sample proceed; they are not manual scientific acceptance or READY/reset thresholds.
- Need user confirmation: no for this exact one rerun; held-object READY representation still requires user selection.

## Authorized launch command

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
printf '%s\n' accept_snapshot accept_snapshot accept_snapshot stop | \
  timeout --signal=KILL 120s env DISPLAY=:1 PYTHONUNBUFFERED=1 \
  scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_critical_controlled_replay_gui.py \
  --output-dir results/20261008_TASK01_critical_safety_command_rerun/raw \
  >results/20261008_TASK01_critical_safety_command_rerun/launch.log 2>&1
```

GNU timeout's default separate process group is retained so the120s KILL cap covers owned child processes. No terminal stdin read remains. The existing fourth-state `stop` intentionally produces a review-stop `failure.json`, not a collision failure or a RESET result. Its exact status/error and at most3 returned/accepted replay labels must be preserved; four completed safety snapshots are audited separately. If an earlier real failure occurs, it is not this planned boundary.

## Scientific reporting boundary

The only allowed positive conclusion is:

> 关键构型下未发现会否定当前 benchmark 几何可行性的明显非预期 Isaac 机器人/工具—环境碰撞。

TASK01 remains PARTIAL; READY/reset is BLOCKED_BY_SHARED_HOLD_SEMANTICS. No stable READY, shared-grasp stability, suction validation, deterministic held-object reset or FROZEN claim is authorized.

User must subsequently choose an existing suction attachment, benchmark-specific rigid/shared-object attachment, or another existing fixed-hold representation. No such mechanism is implemented in this run. TARGET Cube/deep-wall boundary remains a pending benchmark-definition item, not redesigned or automatically failed.

## Actual result

One visible run executed from checkpoint `a10db77`. Harness SHA remains `ab1748840559e8e4cbed33ab194d5c70fd118dc15a6951d5d094e4195c740dc8`, identical to the previous attempt; **no harness, launch script, collision logic, input14q, IK, geometry, ACM or physics change**. All six input hashes and the scene_audit dictionary exactly match the previous controlled attempt. Seven existing pure classification tests pass; they are not simulator acceptance.

| State | Post-step/time (simulation s) | Isaac observation | Max q error (rad) | TCP error L/R (mm) | Free Cube drift (mm) |
|---|---|---|---:|---:|---:|
| START0 | 1 / 0.0166666675 | no unexpected collision observed | 0.000090502 | 0.096015 / 0.067458 | 2.725005 |
| PRE_PUSH135 | 2 / 0.0333333351 | no unexpected collision observed | 0.000154556 | 0.183549 / 0.105363 | 0.000298 |
| state196/B60 | 3 / 0.0500000026 | no unexpected collision observed | 0.000357720 | 0.351379 / 0.156873 | 1.362503 |
| TARGET292 | 4 / 0.0666666701 | **unexpected link7/deep-wall penetration; immediate STOP** | 0.018546728 | 2.513139 / 4.758278 | 0.252231 |

Each row uses the exact recorded requested14q/Cube pose with one normal1/60s PhysX simulate/fetch step. Native core timestamps match the post-step dt accumulator. The carriage frame stays `[0.91,0,0.2,0,0,0,1]`. Actual14q, TCP, Cube, all robot body poses and drift remain in the exact selected raw copies; none is reconstructed from planning FK as a measurement. No dynamic acceptance threshold is invented.

The first three snapshots complete17 focus-shape overlap queries each. START has37hits/0environmenthits; PRE/state196 each38hits with1 expected Cube/table support hit and no robot/tool–environment overlap. State196 also reports left link7/minusY wall contact with **positive**8.798026mm separation; contact-offset proximity is not penetration. TARGET stops before focus overlap queries, so those are **NOT_RUN**, not zero-hit evidence.

## Exact blocking collision — TARGET/state292

- Requested Cube world pose: `[1.100,0,0.260,0,0,0,1]` (xyzw convention), unchanged.
- First triggering original shape pair: `/World/left_fr3/fr3_link7/collisions` ↔ `/World/Task01/Carriage/WallDeep`.
- Contact header has3points; minimum PhysX separation **−0.003016427159309387m**, at world point `[1.1605294942855835,-0.23803561925888062,0.34703701734542847]m`. Original classifier labels this `UNEXPECTED_PENETRATION` and immediately raises/stops.
- Same post-step raw contact batch also includes `/World/right_fr3/fr3_link7/collisions` ↔ the same deep wall, min separation **−0.0030162432231009007m**, point `[1.1605294942855835,0.19396410882472992,0.3470372259616852]m`. This is an **additional raw negative-separation observation**, not a pair that the stopped classifier subsequently evaluated.
- Requested14q setter readback before the step is accurate: max9.158985e-8rad, Cube position error2.567847e-8m. After the step, actual max q error is0.018546728rad and max q change0.018546820rad, with millimetre-scale TCP motion. These actual deviations are preserved, not accepted as a deterministic reset.
- The nominal MoveIt/FCL record gives **+2.2122185355mm** for left link7/deep wall. The controlled original Isaac contact observation is negative. This establishes failure of this critical-state safety check; it does **not** isolate collision-mesh mismatch versus contact/dynamic response as a unique cause, prove mathematical model equivalence, or prove every possible TARGET IK is infeasible.
- Cube/deep-wall raw separation is only−5.587935e-8m (nominal boundary-touch case); Cube/table is−1.117587e-8m. These are recorded separately and **are not the blocking robot–wall pair**. No TARGET redefinition or boundary-policy decision is made.

The exact [TARGET sample](../results/20261008_TASK01_critical_safety_command_rerun/critical_TARGET_sample.json) contains requested and actual14q, poses and contact points. [Probe failure](../results/20261008_TASK01_critical_safety_command_rerun/probe_failure.json) reports `UNEXPECTED_COLLISION_STOP`, phaseCRITICAL,3 returned/accepted labels and **0reset rows**. Its fourth intended stdin `stop` was never consumed because the earlier collision guard fired. No `summary.json` exists. [Metadata](../results/20261008_TASK01_critical_safety_command_rerun/metadata.json), [read-only run audit](../results/20261008_TASK01_critical_safety_command_rerun/run_outcome.json), [verbatim log](../results/20261008_TASK01_critical_safety_command_rerun/launch.log).

Inherited `probe_inputs.json` still advertises the unchanged harness's old default5reset repeats. This is **not this run's authorization or execution**; current allowance is0reset and actual failure shows0. Do not edit historical raw metadata to hide that distinction.

## Process boundary

The physical experiment stops at step4 on the first classified penetration. GUI app shutdown begins at logged app time13.108s, but its USD-resource wait persists until the original external120s **KILL hard cap**, wrapperexit137. Read-only checks confirm all owned launcher/Python processes are absent. No more physics step, reset, controller or suction command was sent. This is **not clean shutdown**, and the exit code must not replace the saved collision verdict. No shutdown repair or second launch is authorized/performed.

## POST-TASK REPORT / stop for user

- Task/status: **PARTIAL**; critical-state Isaac safety **FAIL**; READY/reset **BLOCKED_BY_SHARED_HOLD_SEMANTICS**,0trials.
- Scientific objective/minimum evidence achieved: the four-state gate yields a concrete negative result, not a PASS. Existing nominal discrete geometry remains valid only in its own FCL scope.
- Completed/files: command-only stdin correction; four exact post-step raw snapshots, original failure/scene/input/log evidence and metadata; reports and six records. No implementation/model/physics source changed.
- Commands/results: existing7puretestsOK; one120s-capped GUI command above; four real post-steps; first TARGET collision stops; shutdown capped137; no retry.
- TASK-BLOCKING: explicit TARGET robot/deep-wall safety failure; independently, no current shared-held READY representation.
- DEFERRED: BUG001 TCP/wrench/gravity-inertia calibration → TASK10-IS; force/P2/P3 unchanged.
- KNOWN LIMITATION: no equivalence/continuous-safety/all-chain query proof; first three free-Cube samples do not establish held-object stability; lifecycle close wait not repaired.
- LEGACY: five-Cube Task27, not run.
- Budget/escalation: additional1/1 consumed; static3/3 and previous controlled1/1 histories preserved. **STOP FOR USER**, no further experiment or source repair.
- Fidelity: [ENGINEERING] launcher-only evidence collection; [ADAPTATION] unchanged dualFR3 benchmark; [EXPERIMENTAL] safety observation, not paper algorithm/control; no [DEVIATION] implemented and no [ORIGINAL] paper-controller result claimed.
- Records: STATUS, WORKLOG, EXPERIMENT_LOG, BUGS, DECISIONS and USER_FEEDBACK updated; historical entries preserved.
- User decisions needed: what bounded action, if any, is allowed for the observed robot–wall failure; separately, shared-held READY representation (existing suction / benchmark rigid-shared attachment / another existing fixed-hold mechanism). No selection or dynamics tuning is made here. No PASS CANDIDATE/FROZEN claim.
- Git: `task01-benchmark-draft`, run checkpointa10db77; pre-existing untracked parity01/02logs preserved. Publication is verified separately after records commit.
