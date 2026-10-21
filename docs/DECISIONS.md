# DECISIONS

Append-only architectural and scientific decisions.

## D001 — Two-platform strategy
- Date: 2026-09-29
- Decision: Isaac Sim + ROS2 is the final common benchmark; MuJoCo is an auxiliary force/contact laboratory mainly for P2/P3.
- Reason: preserve fair final comparison while accelerating force/contact debugging.
- Impact: baseline algorithms remain platform-independent and use adapters.

## D002 — Baseline-first rule
- Date: 2026-09-29
- Decision: `ours/` remains algorithmically empty until TASK30.
- Reason: derive our method from reproducible evidence and failure cases rather than premature design.

## D003 — P1 数值复现的范围与基线
- Date: 2026-10-21
- Decision: P1 当前阶段只做**算法数值复现**，分支从 `main@a596c973` 建立；不继承 P2/P3/P4/P5 的未合并分支，不做 Isaac Sim / MuJoCo / ROS 2 / 双 FR3 集成。
- Reason: P1 的算法主张（两阶段模式选择、零空间传播、辅助切换）可在纯 CPU 上独立验证；平台集成属于另一类证据，混入会掩盖算法是否被复现。
- Impact: 复现代码放在 `p1/src/`，不触碰 `baselines/`、`platforms/`、`common/`；若将来提升为统一基准基线，再按 AGENTS §9 迁移并单独审查。

## D004 — P1 官方代码按两个快照审计，且不作为算法 oracle
- Date: 2026-10-21
- Decision: 同时审计 `main`（`fe5b49f7`）与 `pre-paper-accept`（`1820a9e8`）及其内核快照；上游实现只用于"实现存在性"与差异定位，不作为正确性 oracle。
- Reason: 主分支删除了 12 个基线与 Task 3–6 场景，但保留了论文的控制器结构；接收前快照含基线但无文档。两者都不完全等于论文式子，且仓库无许可证。
- Impact: 独立 oracle 必须是 SE(3) 复合/有限差分/SVD 零空间；不复制上游源码入库；GPU 路径（模块 G）单列并需单独授权。

## D005 — P1 数值实现的默认口径
- Date: 2026-10-21
- Decision: 按 `P1_IMPLEMENTATION_PLAN.md` §5 的建议默认值实现 Q1–Q10：式 (8) 用 $x_2\sqrt{x_r}$；`vec8` 用 `[r,d]` 与字面 L1；采样主实现用频域/对数正态；参数双轨（表 I 为主）；停滞项主表用论文式 (42)；奇异项按论文逐 step；不等式保持软约束。
- Reason: 这些默认值在 G0 已给出三重证据或明确的参数出处，先实现再在报告中并列 code-faithful 对照，避免"先改论文再复现"。
- Impact: `p1/src/p1_repro/*` 与三份验收报告；任何与默认值不同的选择必须在报告中标 [DEVIATION]。

## D006 — P1 数值复现的验收以"机制"而非"表 II 数字"为准
- Date: 2026-10-21
- Decision: G1–G3 的验收指标是运动学/零空间/估计器/消融的独立可验证量；不以表 II 的逐格数值为目标，也不因两阶段在某任务上未胜出而修改任务直到胜出。
- Reason: G0 已证明表 II 缺场景、缺基线、参数不一致；G3 的负结果（去掉聚类更好）是真实测量，应保留并解释，而不是调参掩盖。
- Impact: `reports/G3_ACCEPTANCE.md` 如实记录负结果；后续若要表 II 级复现，需另立任务并先补齐 G0 §7 的六个缺口。

## D007 — P1 只做数值算法复现，不做仿真/实物
- Date: 2026-10-21
- Decision: P1 的交付边界固定为**数值算法复现**：纯 CPU 的数学/算法实现、独立 oracle、受控数值任务与消融。不做 Isaac Sim / MuJoCo / ROS 2 / 双 FR3 集成，不做真机，不把 GPU 计时作为验收项（G4 关闭）。
- Reason: 论文的可检验主张（两阶段模式处理、零空间约束、辅助切换）都是算法层的，可在 NumPy 中独立验证；仿真/实物引入的是另一类证据，且会把复现变成平台工程。
- Impact: `P1_IMPLEMENTATION_PLAN.md` 的 G4 标记为 out of scope；`reports/G*` 不再规划 GPU 项；后续工作只允许在数值层改代码。
