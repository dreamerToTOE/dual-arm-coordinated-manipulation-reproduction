# Dual-Arm Coordinated Manipulation Reproduction

面向双 FR3 紧协调搬运与受限空间协同推进任务的**论文复现、统一对标与后续方法研究仓库**。

本仓库不是原 `dual-arm-embodied-palletizing` 工程的继续堆叠，而是一个独立的 SCI baseline/reproduction 工程。目标是在统一实验规范下复现并比较 5 类代表方法：

1. **P4 — Closed-chain constrained motion planning**：闭链约束投影 + 受约束 RRT/RRTConnect。
2. **P2 — Cooperative pose/force control**：共享物体位姿控制 + internal wrench 调节。
3. **P3 — Hybrid force/position insertion**：位置推进 baseline、力位混合、搜索/对准/卡滞恢复。
4. **P5 — QP coordinated multi-arm control**：集中式 QP-IK + 在线碰撞/关节约束。
5. **P1 — Two-stage sampling MPC**：双阶段采样 MPC + null-space equality constraint + GPU。

最终所有可横向比较的正式结果，原则上统一落到 **Isaac Sim + ROS 2 + 双 FR3 + Cube + 车厢** 场景；MuJoCo 仅作为 P2/P3 的接触/力控快速验证平台。

## 当前进度（2026-10-09）

TASK01 已按用户要求**完全重启**，当前分支为 task01-legacy-scene-foundation。

**最新：用户已接受 TASK01 基础场景可行性 PASS CANDIDATE；正式科研 Benchmark 暂不冻结。** 已验收 Task26 原抓取/重抓/推进链不再重新开发。开始 TASK02 最小迁移与统一接口，使用原地薄适配优先；当前分支 `task02-minimal-foundation-interface`。[TASK02-A 软件结果与后续范围](reports/TASK02_FOUNDATION_INTERFACE01.md)：统一状态/来源、只读旧快照转换和四项资产 hash 核验已完成，14项离线测试 PASS；无新仿真/控制运行，不代表完整 TASK02 或科研数据接口已通过。

已接受的物理证据：在现有可见 Isaac GUI 中，已批准的原 Task26 软件修正版完成第一批两件的实际抓持、搬运、释放、导轨前移、后抓、推进、侧压、退出和共同 HOME，执行器exit0。用户最多3次授权实际用2次：第1次第二件到位超时，第2次完整通过；成功后停止，不隐去失败，也不宣称重复可靠性。原执行器验收格位误差为1.181/0.376mm。[完整物理结果、边界和原始证据](reports/TASK01_PREDECESSOR_PATCHED_RUNTIME_REVIEW.md)。

候选名称：`PREDECESSOR_TASK26_BATCH1_TWO_CUBES_WITH_AUTHORIZED_SOFTWARE_FIXES`。独立数值 FK 返回、复用 Task27 后抓候选侧压整链筛选的两项修正在旧仓库独立分支 `task01-foundation-side-preflight-fix` / `5ed0c96`；本轮物理重试不再修改生产源码。原几何、物理、ACM和5mm门禁不变，不覆盖原side-suction分支。[软件修改范围、编译与验证证据](reports/TASK01_PREDECESSOR_SIDE_PREFLIGHT_FIX.md)。

历史负结果保留：此前零修改631b1f原 Task26预检通过，但实际首件侧压5mm贴线门禁拒绝，未完成第二件和HOME。它不是本次软件修正版通过结果，也没有被回写为PASS。[原始失败与完整证据](reports/TASK01_PREDECESSOR_FOUNDATION_RUNTIME01.md)。

新的 TASK01 不再继续调试 reproduction 仓库中新建的单 Cube harness，而是先直接验证旧工程的成熟 Task26 场景能否作为基础场景：

    旧仓库 Task26
    → 用户批准原批1两件（deep → shallow，其他两件休眠）
    → 原 GUI / scene / Play / bridge 生命周期
    → 原 MoveIt
    → 原 planning_only
    → 原完整批1两件物理流程
    → 判断是否可作为 FOUNDATION_SCENE

旧仓库固定读取：
dreamerToTOE/dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a

禁止重新实现 scene、bridge、Surface Gripper、rail、rear regrasp、segmented push 或新的校验器。两件审批已消除 selector 适配需求，继续使用原 `max_batches=1`；额外批准的两项软件修正已单独记录，不修改原几何、物理或验收门限。

基础场景资格验收已完成；当前 benchmark_v1 仍是 DRAFT。用户接受工程可行性不等于批准正式 Benchmark 的状态、参数和跨算法评分门限。

详见：
- [重启后的 TASK01](docs/tasks/TASK01_BENCHMARK_FREEZE.md)
- [D041 / 当前状态](docs/STATUS.md)
- [旧工程复用说明](docs/PRIOR_PROJECT_REUSE.md)

此前自建 TASK01 harness 的 INSERT_READY、startup、readback、native debug 等结果全部保留为历史证据，但不再是当前 TASK01 的 active blocker。

## 历史检查点（2026-10-06，保留原证据）

- TASK01 保持 **IN_PROGRESS / DRAFT**，36 项基准参数待评审，TASK02 未开始。
- 最新运行要求：**以后只用可见 Isaac GUI，不再启动 headless**。当前独立Task01节点默认`execution_time_scale=1.0`，按规划时间正常播放；上轮5.0是20%而不是50%。MoveIt RRT速度/加速度12%仍保留，正常播放不是关节极限速度。完整GUI加载步骤与验证边界见[运行约定](reports/TASK01_GUI_SPEED.md)。新速度未物理验收。
- 当前用户确认的接触协议是 **前三件后杯+侧杯双吸附推入，到深墙后互换主从侧压；第四、第五件精准暂放后单 rear 插入**。旧五件成功不作为新协议通过证据。
- 新协议首件已在本机 Isaac4.5 **headless** 实际通过：原子 PhysX Cube+双TCP反馈、杯面法向保持的腕姿、吸附前后杯有界XYZ精调；X16/Y16、释放/退出/HOME完成，controller0，最终中心误差0.303mm、深/侧墙间隙0.212/0.216mm。原模型、物理、ACM及2.5mm/80Nm保护未改。
- 前一轮零预置回归：**前三件实际双吸推入与侧压完成，batch计数2/5**，第三空载RRT转场被严格FCL拒绝，后两未执行。新版空载候选池通过精确无命令重放；随后fresh实测在首件X16因原子反馈过期/无效安全停止，完成0/5，未实际到空载转场。根因未隔离，不改场景/ACM/原门限，不称五件、GUI、可靠性或论文控制律通过。
- [当前报告、反馈接口及Script Editor加载代码](reports/TASK01_ATOMIC_FIXTURE_FEEDBACK.md) · [首件实际记录](results/20261006_TASK01_rear_open_xyz_cube01/metadata.json) · [最新五件负结果](results/20261006_TASK01_coupled_rear_full02/metadata.json) · [最新状态](docs/STATUS.md)

## 历史检查点（2026-10-03，保留原证据）

- TASK00 环境审计已通过；TASK01 benchmark 草案仍在评审，有 36 项未定值，尚未冻结。
- 左右臂各三次第五块物理探针通过；新只读 PhysX 位姿通路已通过外部 ROS 匀速校准，并随一次完整第五块任务记录 14,295 个连续物理快照。
- 碰撞接触力/力矩在 60/120 Hz 已知载荷校准中通过；最终无缩放安装座辨识出 incoming joint 坐标/anchor。预吸附微调过冲修正后，正常供料的旧工程五块物理流程 **5/5 完成**，双臂 HOME，记录 70,434 个完整快照；未放宽门限或改物理模型。但旧流程前四块的 helper 停放/单臂内件微调与用户确认的 rear+side 双吸主从推压不一致（BUG-009），不能据此冻结 TASK01。真实 FR3 动态 TCP wrench 补偿仍待验证。
- 这些是工程/可行性验证，**不是论文算法复现结果**。先解决力测量、坐标/时间契约与参数评审，再推进 TASK02。
- [第五块探针报告](reports/TASK01_CENTER_ARM_SYMMETRY.md) · [测量诊断、结果与完整启动命令](reports/TASK01_PHYSICS_POSE_MEASUREMENT.md) · [状态表](docs/STATUS.md)
- [力测量可行性、校准证据与复现命令](reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md)
- [完整五块物理探针与未解决缺陷](reports/TASK01_FULL_FIXTURE_CONTACT_PROBE.md)
- [冻结前 36 项评审清单（尚未批准）](reports/TASK01_FREEZE_REVIEW_CHECKLIST.md)
- [本次完整结果与必须确认的阻塞](reports/TASK01_RUNTIME_REVIEW_20261003.md)：当前面中心 helper 的支架碰邻 Cube；真实 Cube 摩擦为 0.5/0.5 而非源码声明的 0.90/0.75；受控 hold 的平均承重正确不等于瞬时 wrench 标定通过。没有静默改工具/材料或冻结基准。

## 总体架构

```text
Papers / reproduction specs
            |
            v
     Platform-independent core
  kinematics / grasp / collision /
       metrics / logging
      /                 \
     v                   v
Planning & QP       Force & Contact
 P4 / P5 / P1        P2 / P3
 OMPL/FCL/QP           MuJoCo
      \                 /
       \               /
        v             v
          Isaac Sim + ROS 2
     Dual FR3 + Cube + Carriage
                 |
                 v
          Unified Benchmark
                 |
                 v
           Baseline Freeze
                 |
                 v
              OURS
```

## 推荐执行顺序

```text
Phase 0  Foundation
  TASK00 Environment Audit
  TASK01 Predecessor Single-Cube Scene Foundation Qualification
  TASK02 Common Interface / Logger / Metrics

Phase 1  P4 Closed-chain planning
  TASK03 Closure Constraint
  TASK04 Newton-Raphson Projection
  TASK05 Constrained Local Connection
  TASK06 Constrained RRTConnect

Phase 2  P2 Pose / Internal Force
  TASK07-MJ Grasp Matrix + Internal Wrench
  TASK08-MJ Object Pose Controller
  TASK09-MJ Pose + Internal Force
  TASK10-IS Isaac Migration

Phase 3  P3 Constrained Insertion
  TASK11-MJ Position-only Push
  TASK12-MJ Hybrid Force/Position
  TASK13-MJ Jam Detection
  TASK14-MJ Search / Align Recovery
  TASK15-IS Isaac Migration

Phase 4  P5 QP Coordination
  TASK16 QP IK Core
  TASK17 Joint Constraints
  TASK18 Collision Constraints
  TASK19 Isaac Real-time Execution

Phase 5  P1 Sampling MPC
  TASK20 Upstream Reproduction
  TASK21 Dual-FR3 Adapter
  TASK22 Equality Constraint / Null Space
  TASK23 Stage-1 Exploration
  TASK24 Stage-2 Refinement
  TASK25 GPU Benchmark
  TASK26 Isaac Integration

Phase 6  Unified evaluation
  TASK27 Unified Benchmark
  TASK28 Ablation
  TASK29 Failure Case Analysis
  TASK30 Baseline Freeze

Phase 7  Post-reproduction
  TASK31 Ours v0 Design
```

## 两个统一 Benchmark

### Benchmark A — TIGHT_TRANSPORT
从“双臂已稳定抓住同一 Cube”开始，到达车厢入口前的 PRE_PUSH。主要指标：success rate、compute/execute time、object pose RMSE、relative-pose RMSE、minimum distance、smoothness、internal wrench。

### Benchmark B — CONSTRAINED_INSERTION
从 PRE_PUSH 开始，经历 CONTACT → PUSH → SEARCH/ALIGN → INSERT。主要指标：success rate、insertion time、contact force RMS/max、左右作用力差、横向/姿态误差、jam rate、recovery count。

详见：
- [Codex 必读](CODEX_START_HERE.md)
- [Agent 规则](AGENTS.md)
- [系统架构](docs/ARCHITECTURE.md)
- [复现路线](docs/REPRODUCTION_ROADMAP.md)
- [Benchmark 规范](docs/BENCHMARK_SPEC.md)
- [当前状态](docs/STATUS.md)

> **重要：** 在 TASK30 Baseline Freeze 之前，`ours/` 不实现新算法。先把 baseline 做清楚，再基于失败案例和统一对标结果决定自己的方法。
