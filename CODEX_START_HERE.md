# CODEX_START_HERE.md

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
