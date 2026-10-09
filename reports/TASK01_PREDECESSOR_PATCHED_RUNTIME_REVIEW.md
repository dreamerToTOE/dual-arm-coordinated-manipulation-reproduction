# TASK01 — 已批准软件修正版的有界 GUI 物理验收

2026-10-09 · ENGINEERING · 执行前记录

## PRE-TASK REPORT

```text
Task: D041 predecessor Task26 batch1 physical qualification with authorized fixes
Scientific objective: verify the mature two-Cube flow can complete as foundation candidate
Minimum sufficient evidence: original preflight PASS, two original physical task PASS,
  wall/cell acceptance and safe retreat/HOME; preserve raw logs and final actual state
Current scope: existing visible GUI, original scene/Play/bridge/MoveIt lifecycle;
  predecessor631b1f + approved two-change commit5ed0c96, original max_batches=1
Explicit non-goals: any additional runtime/source/geometry/physics/ACM/gate change;
  new probe/controller, five Cubes, force/wrench, benchmark redesign or FROZEN
Attempt budget: latest user approves at most3 physical-acceptance attempts;
  each fresh lifecycle, preflight <=600s, physical <=1200s engineering wall caps;
  stop on first full success. Previous runs remain separate historical evidence.
Preferred method: existing GUI executor invokes original assets and direct patched binary
Fallback method: no implementation fallback; unchanged fresh retry for safely rejected planning
Stop / escalation: third unsuccessful attempt; native crash, confirmed unexpected physical
  collision, bridge/state/rail-world/attachment corruption, torque/jam/drift safety fault
  stops immediately rather than repeating a dangerous state. No fix-and-rerun.
Files expected to change: this report, run logs/metadata/snapshots, six persistent records,
  TASK01 status; no production/runtime/benchmark source changes
Validation plan: immutable hashes, fresh original lifecycle, original preflight and physical
  gates, final bridge feedback, original PASS/HOME markers and process cleanup
Known ambiguities/risks: original preflight and carried-Cube FCL coverage limits retained;
  downstream nominal precheck not physical guarantee; USD/ROS-clock feedback not atomic
  post-physics scientific measurement; rail advance is unchanged .100m
Need user confirmation: no; latest user explicitly authorizes runtime up to3 attempts
```

## 授权、现场和固定输入

用户：“继续物理验收，如果三次尝试都失败再反馈给我”。本轮不要求用户再次手动重置；通过现有 GUI 操作原 Stop→scene→Play→bridge 生命周期，保留正常 UI 可见性，不开 standalone/headless。正常重置前先调用旧 bridge 原有 shutdown，避免旧物理订阅/句柄留在被替换 Stage。当前仅有本任务场景，无外部 MoveIt/执行器运行；GUI PID39508/8226 正常响应，双 SG OPEN，rail .750，暂停在旧失败现场。

采用最新软件修正版，不声称 pin 字节完全一致：

- predecessor branch `task01-foundation-side-preflight-fix`, commit `5ed0c967401e5fedb93b938e1c3904f4a4c87600`；
- executable SHA256 `a84cb3ad8734d6a597a81ed33039c732d595029e23a46225c963dfb7069ce992`；
- scene SHA256 `43aa7c2eb6a5667da5e94eaaef347229fe6178ec58d6a10d12dddf14ba2aa9e7`；
- bridge SHA256 `13b5f88d1e7563a37ecafbf571d8ef93015b57059b8912ba9f3399e21e339644`；
- controller SHA256 `8c984cc761b7b4071bfcbc3f01398f30adfa9c43858032f23af551abd752e0f0`。

软件两项修正已完成离线检查与编译，不在本轮再修复。固定 original max_batches=1、execution_time_scale=3.0、ROS_LOCALHOST_ONLY=0。不启用 TASK27，不重新求科研 START，不使用 reproduction scene/bridge/handoff。原两件 active、另外两件 dormant；不是 SINGLE_CUBE。

## 执行状态

准备完成，物理调用0/3；结果待填。当前 TASK01 PARTIAL，FOUNDATION_SCENE NOT_QUALIFIED。

