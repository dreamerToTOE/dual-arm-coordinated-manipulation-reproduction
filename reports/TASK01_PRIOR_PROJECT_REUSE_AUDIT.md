# TASK01 — 旧项目资产复用审计与最小集成方案

日期：2026-10-08。**复用审计完成；最小集成方案待站位确认；TASK01 = PARTIAL / DRAFT。**

本轮只读源码、历史日志与当前定义，随后更新审计文档。没有运行 Isaac、ROS、IK、构建、重抓、推进或 reset；没有生成 INSERT_READY，也没有新物理验收结果。

## 1. 输入与治理边界

重新读取最新 AGENTS、EXECUTION_GOVERNANCE、CODEX_START_HERE、STATUS、D039、PRIOR_PROJECT_REUSE、TASK01、BENCHMARK_SPEC、P4 paper card 与 benchmark_v1.yaml。

- 当前仓库：`dreamerToTOE/dual-arm-coordinated-manipulation-reproduction`，`task01-benchmark-draft`。
- 审计输入提交：`c525fc15bc65633db2154135960706a1ec8f4ff8`，已安全快进同步。不是停留在旧 main 定义上。
- 旧资产：`dreamerToTOE/dual-arm-embodied-palletizing@side-suction-palletizing`，固定提交 `631b1f65656d025c1bb2173e874192f3fe4d355a`；远端 ref 本轮核验相同。
- 旧本地工作树仍为 `task01-runtime-fixes@d4b290c`。资产通过 **git show 固定提交对象**读取；没有切换或修改这个工作树，也没有把 runtime-fixes 当成指定分支。
- 当前 YAML SHA256：`da1b1de421111a52a874cd776a7fdc34cc86654bfddb144399f05ef480f10634`，本轮不修改。
- [源码清单](TASK01_REUSE_SOURCE_MANIFEST.json)保存 19 个旧资产的 Git blob/SHA256，以及当前配置和既有采样模块 SHA。

旧 static parity07–09 的 3/3、controlled fallback 1/1、command-only additional 1/1 均不恢复额度；不开发 parity10。D039 是已批准的任务拓扑纠正，不是同一 query-tree 问题的第四种实现。本轮新集成尝试数 **0**；未来遵守 TASK01 的“一次 bounded integration，实质失败即停”。旧 3×8 RRT 候选是一次预检内部的候选上限，不是三次治理层试验。

### PRE-TASK REPORT（执行前已报告的范围，集中归档）

```text
Task: TASK01 predecessor asset audit and minimal integration plan
Scientific objective: 在 D039 下复用既有持件/重抓/推进，明确最小科研接口
Minimum sufficient evidence: 可追溯旧源码、历史证据、配置差异、分段集成与停止门禁
Current scope: 只读 Task24/11–13/26–27；审计报告与项目记录
Explicit non-goals: Isaac/ROS/IK/build/controller/reset/force；改模型、工具、车厢或 ACM
Attempt budget for the current blocker: 本轮物理/集成 0；旧耗尽额度不重启
Preferred method: 固定 side-suction-palletizing 源对象 + 已有原始日志
Fallback method: 历史文档只能作带限制的工程证据，不补造新运行
Stop / escalation condition: 缺失核心资产、定义冲突、需新增 benchmark 决策即升级
Files expected to change: reuse audit/manifest/excerpt、复用映射、六项项目记录、TASK01链接
Validation plan: 源 hash、原日志摘录一致性、配置未变、记录一致性、git diff
Known ambiguities / risks: 旧 PASS 非新起点/站位/时钟证据；候选 q 非 actual q
Need user confirmation: 审计不需要；集成前未定义的 B 导轨站位需要
```

## 2. 当前唯一有效拓扑

```text
A: START (.550,0,.380), identity, 双侧已持件
   → 既有双臂共同搬运
   → PRE_PUSH_SHARED (.790,0,.260)

固定 handoff（不计 P3 控制得分）:
   双吸盘 OFF 且确认 OPEN
   → 左 helper 安全让位
   → 右臂到 Cube -X 面，复用后侧重抓
   → 右 Surface Gripper CLOSED + 实测几何核对
   → INSERT_READY

B: INSERT_READY → 右臂 +X 分段推进 → TARGET (1.100,0,.260)
   → 深墙支撑/间隙记录 → 既有安全释放、退出
```

START 是 D034 新科研起点，不是旧 Task27 feed。所有 Cube 姿态保持 identity。现有 A136 状态及既有原生 IK 实际返回并记录的 START/PRE 14q 保留，不重新随机求 IK；这些 q 不是 PhysX 持件实测初态。旧 bilateral B157、state196/B60 与 TARGET link7/deep-wall 约 −3.016 mm 是**旧拓扑历史证据**，不能充当新 rear B 的状态或证书；不删、不重跑去修复。

PRIOR_PROJECT_REUSE 的摘要曾把 rear regrasp 写在 helper park 前，本轮仅纠正文档顺序，使其与 D039、TASK01 和 YAML 一致。

## 3. 已找到的复用资产

以下行号属于固定 `631b1f…`，不是旧工作树当前文件。来源：[固定旧仓库快照](https://github.com/dreamerToTOE/dual-arm-embodied-palletizing/tree/631b1f65656d025c1bb2173e874192f3fe4d355a)。

### 3.1 双侧 Surface Gripper：不要重新发明 attachment

| 源文件 / 位置 | 可复用职责 | 薄适配边界 |
|---|---|---|
| `isaac/scripts/task24_side_suction_tight_bridge.py:154–200`，`_build_gripper` | 官方 Surface_Gripper 初始化、现有 D6 attachment | 绑定单 Cube/当前 task namespace；parent 必须是 link8 |
| 同文件 `:202–204,269–293` | desired 命令、close/open、每 physics step update、50 ms retry | 原机制/参数不重新设计；不能在 reset 时假装初始已 CLOSED |
| 同文件 `:241–267` | 两臂相同 stamp 的目标在同个 physics callback 提交 | 保持唯一关节目标写入者；不拼接不同时刻命令 |
| Task24 C++ `:679–693,758–780,814–868` | 同 phase/stamp 发送、等待真实 CLOSED、双臂执行 | 复用协议，不继承旧 steady-clock 作为科研测量时间 |
| Task24 C++ `:1515–1639` | CLOSED 加 Cube/TCP 几何核对 | CLOSED 不是正确吸到当前 Cube 的充分证据 |

Task24 bridge/scene/`dual_side_suction.xacro:71–76` 三处一致：link8→TCP 为 `(0,sign×.155,.080)`，xyzw=`(0,0,sign×.70710678,.70710678)`；left sign=-1，right=+1。两侧对吸时 TCP +X 各朝世界 +Y/-Y，TCP +Z 向下。

现有四杯阵列是工具几何；**每臂一个 Surface Gripper 约束**，不是八个独立吸附。扩展 close 固定实际相对几何，不会自动修正大间隙；旧源码没有新 START 的对象端 anchor 快照。

历史工程参数为 capture .003 m、bendAngle 0、stiffness 1e4、damping 1e3、break force/torque 1e6、retryClose=True、disableGravity=False。它们是持件抽象，不是已标定力能力。当前候选已引用同组参数；不调吸附动力学，不新建手写 rigid/shared constraint。

### 3.2 后侧重抓、完整链预检、推进：实现已经在 Task26

`task27_five_cube_center_insert.cpp` 只有 5 行，是定义宏再 include `task26_truck_box_push_in.cpp` 的入口。Task27 bridge/scene 同样调用 Task26；不能把 wrapper 当成独立重抓算法，也不能整体运行五件应用来验收单件。

| Task26 C++ 位置 | 已有能力 | 此次取舍 |
|---|---|---|
| `:257`，`pushPose` | rear TCP +X 朝世界 +X，xyzw=(1,0,0,0) | 原姿态；Cube -X 面；.060+.001=.061 m 后侧偏置 |
| `:976`，`planPoseCandidatesFrom` | 显式起点、有限 RRTConnect 候选、关节行程排序 | 复用；不是新的 IK 求解策略 |
| `:3560–3864`，局部 `preplanPush` | rear approach → +X push → exit 全链预检，再选解 | 是局部 lambda/Arm 实现，需最小抽取/绑定，不假称现有公共库 API |
| `:1410,1493,1530,1639` | 双臂联合 FCL、严格 Cartesian 与 FK 直线偏离核对 | pusher 动、helper park；保持桌面/三墙/helper 碰撞门禁 |
| `:4548–4603` | 双侧释放和 helper park / pusher high | PRE 已在桌面高度；不重复旧 20 mm 落桌动作 |
| `:4629–4644,4755–4808` | 从 live Cube 构造 rear pose，预检成功再 swing、核对漂移、close | 不能复制旧 release 后 x≈.771 的落点作为新 PRE=.790 |
| `:2508`，`executePushWithSupervision` | +X 16 片推进、逐片位移/lag 与 effort 护栏 | 只复用位置基线；参数 left/right 实际是 pusher/helper 顺序 |
| `:2334,2429,4828` | 深墙支持间隙及高度核对 | 记录原几何；旧 3 mm 不是擅自冻结的新成功阈值 |
| `:5136–5187` | 单 rear OPEN 确认、预检过的 -X 退出、settle 回读 | 不带回五件 HOME/下一件 handoff |

旧 bridge `task26_truck_box_bridge.py:323–342,627–680,722–739` 已有同一个 Surface Gripper、单臂/双臂命令和 open/close/update；rear 只是改变工具姿态，不是换吸附机制。C++ 核心仅依赖标准库、ROS、MoveIt、yaml-cpp、ament，不需要迁入完整 palletizing 库。

## 4. 历史证据等级与不能偷换的结论

| 证据 | 历史观察 | 限制 |
|---|---|---|
| Task11–13 文档 | 同一刚体双 SG；lift 50 mm/误差 .446 mm，transport 100 mm/误差 .311 mm，place .947 mm | 顶吸大箱、hand parent/Z=.105，不迁几何；只说明双 SG 持一刚体已有工程基础 |
| Task24 文档 `:116–133` | 两次单件侧吸放置误差 .184/.115 mm | 文档级；未给逐运行原始路径；固定 ref 已是八件配置，八件预检失败也保留 |
| 旧 raw `full_run_606_optimized.log` | **right pusher**；16 片完成；深墙 .426 mm，退出落稳 .480 mm / cell error .509 mm | 包含两基座 .650→.750；旧摩擦/速度/多件邻块；日志未注明可验 build/source SHA |

原日志本地路径：`/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/artifacts/task27_repeat_20260926/full_run_606_optimized.log`。

Task24 还有明确文档/源码漂移：文档写接触 TCP +1 mm Z，固定 ref C++ L69 为 0；文档和场景供料布局也不同。因此历史单件 PASS 不能逐字对应固定 ref 全套配置，不从旧文档带回该 Z 偏置或旧供料位。

SHA256=`2a286c3ad2a339f2525025ef13ed28ef752cf1ba515da9a41912fa5a2e593bec`。已逐字保存[11 行原日志摘录](evidence/TASK01_PRIOR_RIGHT_PUSH_EXCERPT.log)，不是新运行或完整日志替代。原始行号/哈希在 manifest。

另一个 `full_run_dynamic_center_20260929.log:3190` 为 **left pusher**；不能拿它的 .509 mm 标签证明默认 right。固定源码 `631b1f…` 才显式设 `center_pusher_arm=right`。这些证据只支持旧工程路线可行，不是新 benchmark PASS、统计成功率或力控证据。

## 5. 关键差异与必须消费的接口

1. **导轨是当前唯一需先明确的 nominal 状态决策。** 新 YAML 的 base_at_rest X=.650 是静止站位，不等于 B 禁止用现有导轨；rail limits 也不等于 B=.750 已获准/冻结。旧参数 `task26_push_control.yaml:18` 为 +.100，源码 `:4687–4751` 在两吸盘 OPEN、关节命令静默后移动**两侧**导轨，并重建 X-offset 规划世界。原始 right PASS 用两侧 .750。建议复用这个**候选站位**，但等待用户确认，不默默改 config。
2. **INSERT_READY 不只是 14q。** 至少保存实际 left/right q、两侧 base 世界位姿/rail X、规划 world_shift、Cube pose、两 TCP、右 attachment 身份/实际相对变换、left OPEN/right CLOSED、helper park、carriage frame，同一 post-physics-step stamp/step。旧 candidate goal 7q 不是 actual14q；所有 pending 保持。
3. **单件不等于把旧 kTasks 截成一项。** `isCenterInsertTask:2354` 硬编码 index4；`:3066–3087` 动态居中和 `validCellPlacement:2450–2484` 读邻 Cube。适配需显式 rear-only 单件模式，固定 Y=0，不使用四邻块、center index4、side compaction、feed/batch/HOME。
4. **释放必须确认。** `openBothAndConfirm:2651–2666` 返回 bool，但旧正常调用 `:4560` 没消费。新薄适配必须在 OPEN 确认失败时停止，不声称原实现已有这处阻断。
5. **当前物理保持。** 旧 authored friction .90/.75 与当前 effective .50/.50 不同；不回调旧摩擦、drive、dt、速度或吸附参数来复制 PASS。旧 20 mm 落桌/40 mm 短推不重复加入当前 PRE。
6. **当前采样复用。** 旧 bridge 的 USD 默认变换/ROS clock、buffer 丢 header，不作为科研状态。复用已有 `fixture_geometry_stream.FixtureGeometryPublisher`（支持可变 Cube paths）与 `physics_object_sampler.PhysicsObjectSampler`，从 live RigidPrim + link8/TCP SE3 在 post-step 采样；reset 后重建 sampler。旧 Task27 bootstrap/四邻块 probe 不能照搬；不重造新的记录框架。
7. **碰撞生命周期要显式。** 旧 rear RRT 有当前 Cube world object，推入段临时移除它；适配应保留当前机器人/工具/三墙/桌面及 Cube–environment 几何检查，并单独记录吸盘接触的生命周期，不能永久忽略 Cube、扩大 ACM 或冒称旧代码有完整 moving-object 碰撞证明。导轨切换后必须刷新规划世界，不复用切换前缓存。
8. **旧护栏不是力控。** 20 mm lag、80 Nm raw joint effort、3 mm 深墙 gap、10 mm 高度门限是旧工程参考；不升级为新科研指标。16片采样 effort 峰值不是连续峰值，也不是 TCP wrench。force/admittance/yaml 调参留 TASK10-IS/P3。

## 6. 最小集成方案（未实施）

只增加单件薄桥接入口、单件阶段 driver 和状态捕获绑定；原算法/几何仍有明确固定来源，不迁入整个五件 app，不建新 SG/IK/推进框架。代码抽取范围先列清单、保留源码出处，再做一次有界集成。

| 阶段 | 复用 / 输入 | 最低证据与停止门禁 |
|---|---|---|
| A START 已持件表示 | 既有 Task24 SG；已记录 START14q、Cube identity；现有 local TCP | 在计分外建立两个实际 attachment；同 post-step 的 CLOSED+Cube/TCP 核对，不能用 free Cube 代替 |
| A → PRE | 已通过 A136 及 START/PRE14q；共同命令协议 | 不重求 dense IK；保存 held 端点与实际误差，不宣称动力学/力控稳定性已证明 |
| handoff | PRE 实际状态 → 两侧 OPEN → left park → 可选已批准 rail 站位 → right rear 完整链预检/到位/CLOSED | helper/rail 都要进入当前完整 RobotState；OPEN/碰撞/对象漂移失败即停；候选预检先于实际 rear-close |
| INSERT_READY 捕获 | 右 rear .061 偏置 + live Cube、左 park、实际 bases/q/attachments | 记录完整状态，不先 FROZEN；不同 P3 方法后续统一从这个状态开始 |
| B 几何和最少 GUI sanity | 复用 rear +X/exit 预检；固定 TARGET；当前场景模型 | 新 rear 链单独记录密集 IK/FCL/限位/Cube几何；选择 START/PRE/新rear危险态/TARGET 最低必要检查，不做全模型等价或旧157复跑 |
| READY/reset 审查 | A START/PRE 双侧 hold；B INSERT_READY 单侧 rear hold | 只有持件语义、安全门禁和站位一致后才重复 reset；次数/数值验收仍待用户冻结，最后仅 PASS CANDIDATE REVIEW |

固定 handoff 日志单列；P3 评分从 INSERT_READY 开始。TASK01 不实现力控、卡阻恢复、五件流程或新的选择器。SOURCE package 声明 Apache-2.0，但未识别独立的仓库根/Isaac-script 许可证：保留作者/源码出处，不据此给整个旧仓库补写许可证，也不称为论文原始算法实现。

### 集成前需要用户决定

**建议：复用已有双轨 +.100 m 站位，两侧 base X=.750，将其显式记入 B INSERT_READY 候选及 reset。** A 仍用 rest X=.650；工具、车厢、TARGET、物理、ACM 不变。

如果用户选择 B 保持 X=.650，应明确那是新的 nominal 站位，旧 right 成功不能为它背书；需要一次新的 rear-chain 门禁，不先开发替代算法或改工具。本轮不为两种方案分别找 IK，也不做双路线试验。

## 7. 实际检查与交付

本轮只做以下读检/文档操作：

```bash
git status --short
git show 631b1f65656d025c1bb2173e874192f3fe4d355a:<source-path>
git rev-parse 631b1f65656d025c1bb2173e874192f3fe4d355a:<source-path>
git show 631b1f65656d025c1bb2173e874192f3fe4d355a:<source-path> | sha256sum
sha256sum configs/benchmark/benchmark_v1.yaml
sha256sum artifacts/task27_repeat_20260926/full_run_606_optimized.log
sed -n '2982,2985p;3094p;3145,3149p;3164p' artifacts/task27_repeat_20260926/full_run_606_optimized.log
```

路径分别在当前/旧仓库执行；`<source-path>` 的完整 19 项列表在 manifest。不将这些读取叫实验通过。

交付前实际检查：`git diff --check`、manifest 的 JSON 解析、YAML 的 DRAFT/one-Cube/释放→左让位→右重抓/pending INSERT_READY 定义断言全部 exit0；`cmp` 确认保存的 11 行与原日志所选行逐字一致。配置和两个既有采样模块 SHA 与审计输入一致，`git diff --exit-code -- configs/benchmark/benchmark_v1.yaml platforms/isaac_ros2` exit0；旧仓库 tracked worktree 无修改。上述均为文档/来源检查，不是 simulator acceptance。

### POST-TASK REPORT

```text
Task: TASK01 prior asset reuse audit / minimal integration plan
Status: PARTIAL（TASK01）；audit complete；integration NOT_RUN
Scientific objective: 用已验证工程基础恢复 D039 staged topology，不再重复造轮子
Minimum sufficient evidence achieved: yes for audit/plan; no for TASK01 runtime acceptance
Completed: 固定 source/hash、持件与 rear 流程、原 right 日志、差异与集成门禁
Files changed: audit report/source manifest/raw excerpt；reuse map/TASK01 link；六项记录
Commands run: Git read/sync、rg/sed、sha256sum、文档一致性验证；publication另由提交记录
Tests / experiment results: 无 simulator/ROS/IK/build/reset；无新物理 PASS
Key metrics: 19 pinned source assets；11 raw historical lines；new attempts=0
Blockers:
- TASK-BLOCKING: B rail/base nominal state待确认；held READY/INSERT_READY/new rear B仍需验证
- DEFERRED: BUG001/TCP wrench/force/jam/P2/P3及正式 success/frequency/repetition冻结
- KNOWN LIMITATION: 旧物理日志无build SHA；旧top吸/Task24文档级证据；非模型等价
- LEGACY: 五件/邻块/批次/旧HOME/速度调参
Attempt budget used: 本轮集成/物理0；旧3/3、1/1、1/1不恢复
Escalation required: yes，选择 INSERT_READY rail/base 状态后再集成
Paper fidelity:
[ORIGINAL]: 本轮没有新增论文算法实现声明
[ADAPTATION]: D039 staged single-Cube common benchmark，等待nominal站位确认
[ENGINEERING]: 原SG/Task26 rear原语复用与现有post-step采样绑定方案
[DEVIATION]: 无工具/车厢/ACM/模型/物理/阈值改动
[EXPERIMENTAL]: 未运行
Records updated: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK
```
