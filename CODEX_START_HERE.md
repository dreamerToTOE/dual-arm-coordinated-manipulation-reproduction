# CODEX_START_HERE.md

## 最新研究任务 D067（2026-10-13，覆盖历史P4等待门禁）

P4@79cc871阶段性审查通过，RSS失败与PCS换链优势未充分验证、全论文部分完成结论保留。P4不再修改/追加实验。
当前独立 `reproduce-p2-paper-audit`：已阅读全文P2八页，交[审计](reports/P2_ORIGINAL_PAPER_AUDIT.md)与[协议](reports/P2_CLOSED_LOOP_EXPERIMENT_PROTOCOL.md)，[任务卡](docs/tasks/P2_PAPER_AUDIT_AND_PROTOCOL.md)。
**当前暂停在式15接触运动学科学裁决**：正号在自由滑动反例中产生80μm/4ms形变；仅改负号还不足以认证有限形变。
原式与诊断保留，不执行闭环，不自动修正、不P3。待决定后先完成模型推导/资格和协议冻结。
最小模型允许原物块/Cartesian软接触，不强制双FR3、吸盘、Cube、车厢或Isaac；完整IESEKF/硬件未完成项必须明示。
三轮后续小修预算本轮0/3；正式Benchmark与旧TASK07–10保持不变。

## 当前交付门禁（2026-10-13，D066）：P4三方法部分完成，停止等待审查

分支reproduce-p4-three-methods；20R同类重建RSS/PCS/NR已各自运行，60统计与3重复、
三轮有据修正、10图/16公式/18页正式中文Word/PDF及全量失败已交付。
读[交付说明](reports/P4_THREE_METHOD_POST_TASK.md)。RSS0/20、PCS20/20、NR20/20不是原全论文通过；
RSS完整重复未过、原六环境/m曲线未覆盖。原NR/FR3与历史失败不改。
上传后停止；不得自动重复实验、重新分配3轮修正、P2或Isaac场景集成。

## 最新决定 D065（2026-10-13）：P4 三种方法均须实际复现并在同条件下出图；报告按我的科研汇报口吻

本节覆盖此前“P4仅整理现有NR、不得新增实验”的历史任务描述。**P4原论文是比较研究，RSS（奇异构型随机采样）、PCS（被动链切换）、NR（牛顿迭代投影）都必须有实际实现与可复查实验；不得因为已有NR成功就跳过另外两种。** 不应先验声称哪一种总是“差算法/好算法”，应依据原文各环境和实测对照分析。

当前优先任务：[P4 三策略统一实验](docs/tasks/P4_THREE_METHOD_COMPARISON.md)。先核查论文和作者源码的三个方法的实现机制、可行的原论文机构/逆运动学模型与实验条件；基于适合这些方法的最小论文式模型开展共同测试，**不强制转成现有FR3/车厢/Isaac场景**。每种至少有实际运行数据、成功/失败、耗时、投影及路径相关指标，出可复查对比图表。避免把同一随机种子的重复运行当独立样本。先审计和锁定协议，再按预算进行代码实现/实验；如原文代码缺失、伪代码不完整，可进行最多**三轮有依据的小幅实现修正**。三轮仍无法达到可比的原论文现象或数值，则停止并如实写差距和原因，保留所有失败版本/日志，**不能无限调参、改变原方法或修改验收门限**。

导师Word报告**使用我的第一人称科研表述**，开篇直接讲原文研究问题、模型、RSS/PCS/NR机制、结果与实验。禁止“编写目的”“我按你的要求”“本报告根据老师要求”“本章定位”“本文档说明”“ChatGPT/Codex指令”等对话式/编写说明。原理论和我们实测区别清晰；最后独立“应用于当前双机械臂场景的差距与问题”一章，不做方法改进或Isaac集成。现有11页阶段稿只是NR历史数据报告，**不能冒充三种方法完整比较版**；三方法运行结果未取得前只标“待实验”，不得占位造数字。

任务结束先交P4三策略源码与原始数据、报告Word/PDF和全部失败记录，**停止等待用户审查**，不自动P2/P3/Isaac。历史TASK03精度未通过、TASK06原协议部分完成、B0执行不满足均不改判，原始FR3记录不覆盖。


## 最新研究决定 D064（2026-10-13）：五篇原论文算法复现优先、现有场景不再作为前置条件

**本节高于 D055/D062/D063 等历史阶段规则。** 当前 P4→P2→P3→P5→P1，先以原论文为对象完成核心算法、最小可复现实验、原论文实验结果对照、中文 Word 报告；五篇收尾后另行研究小改和在双 FR3 / Cube / 车厢 / Isaac Sim 场景中的应用。**不要求 P2/P3/P5/P1 使用本项目的 FR3、车厢、吸盘、Isaac、旧 Task26 的模型、起终点或控制架构。** 优先复用作者的模型/代码/实验设置；模型、软件、数据、硬件条件不具备时允许经审查的最小可复现替代，但必须在报告中列清偏差，不得称原文条件完全复现。

复现质量判断依据：论文**具体创新的实现忠实度、对照实验与曲线的真实性、结果可重复、与原论文的差异及原因**，而不是能否放入我们的场景。不得提前增加“适应车厢”“增加FR3控制”“吸盘保持力”等优化要求；这些归后续应用与小改阶段，当前不设为通过门槛。

导师报告篇幅与章节重心：第一部分深讲原论文研究问题、模型假设、算法/控制器组成、公式推导、算法流程及作用机理；第二部分只展示实际复现平台、参数、**与原论文实验对应**的曲线数据/图表/指标/失败；**最后独立开设“面向本课题场景的适用性差距与待研究问题”**，只做概念性、证据分级的差距分析，不做当前复现验收，不推出我们改进有效的结论。前两部分不得让本课题 FR3/车厢工程日志反客为主。

P4 已提交原 23 页报告 `02f9346` 不删除不改历史科学结论；**需按本决定重构报告叙事/Word，保留原始报告作版本存档**。独立修订任务见 `docs/tasks/P4_REPORT_REFOCUS.md`。本轮规划本身不授权新实验、原论文 RSS/PCS 编码、Isaac/ROS/控制或自动进入 P2；修订报告经用户审查后才准进入 P2。


## 2026-10-12 交付门禁（D063）：P4报告完成，等待审查

独立分支 `report-p4-paper-first` 从指定 e32d19d 建立。
读[中文Word](reports/P4_论文复现汇总.docx)、[PDF](reports/P4_论文复现汇总.pdf)、[交付报告](reports/P4_REPORT_POST_TASK.md)。
六份私有资料SHA匹配；主代理已阅读全文P4八页及范例，10中文图/16可编辑公式/23页。
只整理旧数据，没有规划/IK/NR/FCL/Isaac/ROS/机器人新实验。
**P4报告待审查，不等于P4完整复现通过；不得自动P2或执行B0路径。**
原精度FAIL、TASK06整体PARTIAL、B0执行不满足、TASK02-D暂缓和Benchmark草案不变。
下方“当前先整理P4”是本轮启动前优先级，不能交付后自动再跑实验或开启下一篇。

## 最新执行优先级（2026-10-12，D062，覆盖本文件所有历史“下一步”指令）

导师要求逐篇**论文级复现汇总报告**，用户提供DEFORM（18页Word）作为格式样本。**当前先完成五篇核心算法与最小可复现实验的图表报告，暂缓各篇Isaac集成/改进，不废除未来应用到双FR3场景的总目标。**

固定复现顺序：**P4现有数据整理报告（不重跑）→ P2→P3→P5→P1 → 小改方法设计 → 统一Isaac场景验证。**

- 必读：[五篇原文身份与合法获取链接](references/ORIGINAL_PAPERS.md)、[逐篇任务与验收](docs/PAPER_FIRST_REPRODUCTION_ORDER.md)、[导师报告规范](docs/PAPER_REPRODUCTION_REPORT_FORMAT.md)。
- 私有本地副本相对路径 `references/private_sources/P1_original.pdf` 至 `P5_original.pdf` 及 `DEFORM_report_example.docx`；**这些文件当前不在公开GitHub提交中**，须用户本人从私有资料包解压到Codex实际工作树。若不存在，尝试可信作者/官方原文链接，仍无法读全文则先向用户索取，不允许根据二手卡片虚构公式和图表。
- **当前唯一可开展工作**：检查原文/私人副本就绪情况，整理P4核心算法已有数据为导师式中文报告；**不重新运行科学规划、不开发TASK06-IS-B1、不执行Isaac/ROS/控制命令**。P4报告提交后停下待审查；不得自动开始P2。
- 必须分项保存TASK03历史精度未通过、TASK06完整协议部分完成、TASK06-IS-A离线通过、B0执行资格不满足；不更改原始数据与Benchmark草案。
- 说明与用户优先使用中文，少用英文状态词；论文/函数/文件名可保留原文。

以下为此前 Isaac 研发任务的**历史门禁**，不是本轮的当前授权。


## 当前交付门禁（2026-10-12，D060/D061）：B0审查已完成，执行准备不满足

A离线适配已获用户接受；用户只批准固定1869点执行前审查，不批准Isaac执行。
左J4 index860仅.236039°余量，原终点误差.035/.06rad且无全程包络；另缺加速度/
共同赋时和实际持件START对齐。原路径/闭链/FCL来源仍合格，全部历史结果不改。
读[完整B0报告/图表](reports/TASK06_IS_B0_PRE_EXECUTION_REVIEW.md)。
**提交后停止等用户决定；不得自动重规划/新seed/捷径/时间轨迹或Isaac/ROS/命令。**
B/C/TASK07不自动授权，Benchmark草案、原TASK06整体部分完成、TASK02-D暂缓。
以下A“等待接受”及“下一步A”门禁保留历史，不覆盖本节。

## 当前交付门禁（2026-10-12，D058/D059，覆盖以下历史交付门禁）

TASK06-IS-A第二阶段**无执行规划适配初步验收通过；停止等待用户审查**。
分支task06-is-a-p4-scene-adapter；基线7bae83a；协议20fe06d，测试c88a80c。
读[本轮报告](reports/TASK06_IS_A_NOMINAL_SCENE02.md)：原Task26 .628m独立来源输入、
完整14q名义端点、原P4 seed7 96nodes/1869点路径及原FCL独立复核已保存。
这是离线构造，不是实际持件测量/Isaac执行/连续证书；原TASK06整体部分完成不改。
原失败归档不重写，TASK02-D暂缓，Benchmark草案。科学预算本轮已结束，
**不得自动再跑候选/seed、物理控制、B/C/TASK07**；下一步由用户审查另行授权。

## 当前交付门禁（2026-10-12，D056/D057）

TASK06-IS-A部分完成，分支task06-is-a-p4-scene-adapter，**停止等待用户审查**。
读 [新报告](reports/TASK06_IS_A_SCENE_ADAPTER01.md)：Task26 world内宽628mm不等于
旧P4归档606mm，实际持件A起终点/附件证据缺失。source验证1/1已停止；没有
native加载/真实FCL状态查询/IK/搜索/执行。编译和纯离线回归通过不能替代路径证据。
不自动改旧world、再跑来源门禁、取得实时状态或启动B/C/TASK07。输入路线需审查。
旧TASK06整体部分完成、TASK02-D暂缓、Benchmark草案未定稿。
下列D055“下一步A”以及此前门禁保留为历史规划，不授权交付后的自动续跑。

## 当前优先指令（2026-10-12，D055，覆盖以下历史停止门禁）

用户已经更新总体路线：五篇论文的核心算法必须逐篇应用于现有双 FR3 + 侧吸盘 + Cube + 车厢场景。每篇按“算法/数学→场景无命令验证→单独授权的 Isaac Sim GUI 运行→阶段对比”推进。详见 [最新路线](docs/REPRODUCTION_ROADMAP.md)。

**唯一下一步任务：TASK06-IS-A — P4 现有场景适配与无命令规划验证**，见 [任务卡](docs/tasks/TASK06_IS_A_SCENE_PLANNING_ADAPTER.md)。本次规划提交本身不授权运行；用户随后提供明确 TASK06-IS-A 指令时才开展。不得启动仿真/ROS 服务或发送机械臂、吸盘、导轨命令，若需要实时接口必须停下征询授权。TASK06-IS-B/C、TASK07 均未授权。

原 TASK06 核心软件初步验收通过、完整协议部分完成，直接碰撞专项缺口不改判。TASK02-D 暂缓、正式基准草案未定稿。旧工程只薄适配不重造轮子。向用户的报告优先使用中文状态词。以下旧执行门禁均为历史记录，仅在不与本节及 AGENTS/新任务卡冲突时参考。


## Mission
Build a traceable reproduction and benchmarking stack for five high-level dual-arm manipulation baselines, then use measured evidence to design our own method.

## Current research task
Dual FR3 tightly coordinated transport of one shared Cube followed by cooperative constrained insertion/pushing into a carriage-like space.

## Platforms
- **Final system benchmark:** Ubuntu 22.04 + ROS2 Humble + Isaac Sim + dual FR3.
- **Fast force/contact lab:** MuJoCo, mainly P2/P3.
- **Planning/math:** MoveIt2/OMPL/FCL and standalone kinematics/QP modules where appropriate.

## Five baselines
- P4: closed-chain constrained planning.
- P2: object pose + internal wrench control.
- P3: hybrid force/position insertion and recovery.
- P5: centralized QP coordination and collision constraints.
- P1: two-stage sampling MPC with null-space constraint handling.

## Dependency order
`Foundation → P4 → P2 → P3 → P5 → P1 → unified benchmark → baseline freeze → ours`.

## Current execution gate

**Latest user review D054 (base74d4276): TASK06 core offline planner software =
PASS CANDIDATE; overall TASK06 = PARTIAL. REVIEW RECORDED / STOP.**
Original protocol/result remains failed at directPROJECTION_JUMP, not proven
directCOLLISION; no FCLquery at rejectedmidpoint.18calls/9pairs/4NODE_LIMIT and
553node148edge successes retained unchanged. Missing obstaclequalification is
a separate **DEFERRED P4 evaluation, not authorized**. No code/parameters/scene/
ACM/model/Benchmark change, new experiments or TASK07. TASK02IN_PROGRESS,
DDEFERRED, BenchmarkDRAFT. [Scoped review](reports/TASK06_REVIEW_CLOSEOUT.md).
The pre-review delivery gates below are retained history.

**Latest delivery: TASK06 = PARTIAL / STOP FOR USER REVIEW.** Branch
`task06-p4-constrained-rrtconnect`, baseline91a1adc, testedsource29a9d5c, D052/D053.
True two-tree NR/RBS/FCL paths and all9fixedseedrepeats verified; private obstacle
20261012 succeeds twice (553nodes/148edges). Its directTASK05connector is rejected
first by unchanged projectionlocalityguard, notCOLLISION as predeclared. Retain
thatFAIL; no newseeds/scenetuning/thresholdchanges or completePASSclaim.
Allsoftware/native regressionspass; compile-negative/fullrawfailedsearch evidence
retained. NoIsaac/services/robot/Task26/model/ACM/Benchmarkchange. TASK02IN_PROGRESS,
DDEFERRED, BenchmarkDRAFT. **Do not start TASK07 or additional experiments.**
Read [latest POST-TASK REPORT](reports/TASK06_CONSTRAINED_RRTCONNECT01.md).
All older authorization/stop entries below are historical, not current instructions.

**Latest delivery: TASK05 PASS CANDIDATE (OFFLINE DISCRETE LOCAL CONNECTION ONLY).
STOP FOR USER REVIEW; do not start TASK06 or runtime.** Branch
`task05-p4-local-connection`, base5d41869, D050/D051. Existing C/Jc/NR/FK and
genuine private FCL reused; no ACM/model/Benchmark/Task26 changes. Ten positives,
three bound/closure/realFCL negatives and300syntheticchecks pass; complete ordered
prefix/projection/collision evidence saved. No continuous safety/full P4 planning
or physical claim. TASK02-D DEFERRED, parentTASK02 IN_PROGRESS, Benchmark DRAFT.
[Latest POST-TASK REPORT](reports/TASK05_LOCAL_CONNECTION01.md).
Earlier delivery/authorization gates below are preserved history, not active work.

**Delivery complete; STOP FOR USER REVIEW. TASK04 = PASS CANDIDATE (OFFLINE
PROJECTION MATHEMATICS ONLY).** Read [TASK04 report](reports/TASK04_NR_PROJECTION01.md)
and [projection contract](baselines/p4_closed_chain/PROJECTION.md). D048 protocol
unchanged: 194/194 neighboring + 293/293 independent diagnostic projections converge.
Original TASK03 0.05-micrometre historical precision FAIL remains FAIL; TASK03 math
acceptance is user-reviewed D047. TASK02 IN_PROGRESS; Benchmark DRAFT / NOT FROZEN.
No authorization to start TASK05/TASK06, physics, controller or Benchmark changes.
The authorization and older delivery entries below remain historical.

Latest user review/authorization: **D047 accepts TASK03 PASS CANDIDATE (OFFLINE
MATHEMATICS ONLY)**. Original0.05μm historical precision FAIL/max0.435028μm and all
source/tests/data remain unchanged; full P4 reproduction incomplete. Active **TASK04
NR projection OFFLINE ONLY**, base91422f4, same task03-p4-closure-constraint branch.
Read TASK04 card/D048 predeclared protocol: existingC/Jc/FK only, SVD full updates,
independent1e-8m/1e-8rad, max40, exact bound rejection,97×2 deterministic neighbors
+293 original-grasp diagnoses. No physics/ROS services/Task26/Benchmark or TASK05/06.
Stop after GitHub delivery for review; old stop/partial statements below are history.

Latest delivery: **TASK03 = PARTIAL / USER REVIEW**, not PASS CANDIDATE. Offline
SE3 closure/Jacobian software verified on unchanged actual FR3 model:72TASK02 +93
math tests and435derivative configsPASS. Original fixed-grasp archived closure
0.435μm exceeds predeclared0.05μm; algebraic test-only G* cannot substitute.
Read [TASK03 POST-TASK REPORT](reports/TASK03_CLOSURE_CONSTRAINT01.md) and
[formulas/frames](baselines/p4_closed_chain/README.md). No threshold/IK/G change,
Isaac/services/Observer/projection/controller or benchmark freeze. Stop for user
precision/fixture review; **do not start TASK04 automatically**. TASK02-D remains
PARTIAL/DEFERRED, parent TASK02 IN_PROGRESS, Benchmark DRAFT. The IN_PROGRESS
authorization entries below are retained history, not an instruction to keep coding.

Latest explicit authorization: close **TASK02-D = PARTIAL / DEFERRED** ([localAPIaudit](reports/TASK02_POST_STEP_API_AUDIT.md));
native post-step/clock/reset qualification belongs to later Isaacmeasurementadaptation and does
not block offline math/planning. Active **TASK03 P4 closure residual/Jacobian, OFFLINE ONLY**,
branch `task03-p4-closure-constraint`, softwarebase36c95ab. NoObserver, Isaacphysicalrun,
oldTask26 change, Newtonprojection/TASK04 or Benchmarkedit/freeze. Deliver real-modelFK+
finite-difference evidence then stopforreview. TASK02 remainsIN_PROGRESS. The C-only stop
below is retained history and superseded only by this bounded new approval.

Latest user decision (2026-10-09): **TASK01 foundation PASS CANDIDATE ACCEPTED**, not a frozen scientific Benchmark. The original batch1 two-Cube/HOME evidence and first negative run remain unchanged. Do not redevelop original grasp/regrasp/push or repeat foundation qualification.

Active work: **TASK02 minimal migration and unified interfaces**, branch `task02-minimal-foundation-interface`. Use accepted predecessor assets in place through thin adapters first, not a copy/rewrite. TASK02-A state/provenance passes; **TASK02-B/C = PASS CANDIDATE**, parent TASK02 IN_PROGRESS. C reuses Task14 initial-drift geometry/max/RMS, adds explicit tracking/insertion math and data-only wrench/distance with strict clocks/qualification; two independent mock adapters agree. Final72A/B/C tests PASS, no Isaac/ROS/MoveIt invocation, backend/control binding or scientific threshold freeze. Read [latest C POST-TASK REPORT](reports/TASK02_METRICS_MEASUREMENTS01.md), [metric semantics](common/metrics/README.md), [B scope](reports/TASK02_EXCHANGE_LOGGING01.md), STATUS and reuse map. Real post-step binding/attestation, execution RNG control and scoring decisions need separate bounded scope. Stop after C delivery: do not launch runtime, TASK02-D or TASK03 under this authorization. BENCHMARK remains DRAFT / NOT FROZEN.

### Historical qualification (completed; not an active work list)

TASK01 predecessor qualification ran on branch `task01-legacy-scene-foundation`.

TASK01 has been explicitly restarted. Do not continue the previous custom TASK01 harness line.

The original qualification scope was:
1. read the pinned predecessor dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a;
2. launch its mature Task26 scene using the original GUI → scene → Play → bridge lifecycle;
3. reduce Task26 to exactly one independent Cube (task26_r0_deep) using an existing mode or the smallest selector-only patch;
4. run the predecessor planning-only check and then one complete physical Cube flow;
5. decide whether that old scene is suitable as the Isaac foundation.

The current benchmark_v1.yaml is DRAFT and is not an input to this qualification beyond historical comparison.

Read docs/tasks/TASK01_BENCHMARK_FREEZE.md for the restarted scope.

## Scientific rule
“Runs successfully” is not equivalent to “paper reproduced”.

Equally important:
“An auxiliary probe is imperfect” is not equivalent to “the current scientific task is blocked”.

Use minimum sufficient evidence, attempt budgets, blocker ownership, and escalation rules. Never continue an engineering loop merely because another diagnostic refinement is technically possible.

## Reuse rule for TASK02+
Before implementing TASK02 or later, read `docs/POST_TASK01_REUSE_MAP.md` and complete the mandatory PRIOR-ASSET CHECK from `AGENTS.md`. Reuse validated engineering infrastructure from the predecessor project where appropriate; keep paper-specific algorithms new and traceable.
