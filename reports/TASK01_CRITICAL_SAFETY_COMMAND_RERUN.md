# TASK01 — One Command-Only Critical-State Safety Rerun

2026-10-08. Status: **PREPARED / NOT_RUN**. This is the user's additional allowance **1/1**, not a new probe or a renewed static-parity budget.

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

Pending this one authorized launch. No simulator has been started for this rerun at the preparation checkpoint.
