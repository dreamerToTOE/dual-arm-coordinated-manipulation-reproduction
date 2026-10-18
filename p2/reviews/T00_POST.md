# P2-T00 POST — 旧成果证据审计结果

**结论（一句话）**：迁入的 P2 代码/数据/报告在**字节级**与用户已验收的冻结交付一致（198/198 个在范围内的科学文件 blob 相同；验收 manifest 中 181 个可定位文件 SHA256 全等、0 不符）；旧交付的真实状态是**数学与组件资格通过、完整论文实验全部未取得**；首条估计闭环在 **3.948 s** 停止的直接原因是**式(18) 4 ms 右 Euler 预测对 −2183 s⁻¹ 快模态的数值不稳定**，该风险在本轮之前的静态审计中已被算出（4 ms 特征值 −7.732），但没有改变预测器就进入了真实闭环。**总状态仍为 PARTIAL。**

执行日期：2026-10-18。分支 `reproduce-p2-numerical-simulation-20261018`，HEAD 起点 `a2f023d9`。零仿真、零积分、零参数改动。

---

## 1. 项目状态核查

| 项 | 结果 |
|---|---|
| 分支 | `reproduce-p2-numerical-simulation-20261018`，起点 `a2f023d95f2fdc8cbae6ebb6863aed654b33e556`，基线 `main`=`0e3f8f5b` |
| 工作树 | 独立 worktree `/home/ubuntu2004/lmy/p2-num-sim-20261018`，审计开始时**干净**（`git status --porcelain` 为空） |
| 分支获取方式 | 原仓库 `origin` 走 SSH:22 被环境拦截（`kex_exchange_identification`），改用 HTTPS 只读 fetch 后 `git worktree add`。**未 checkout 主工作树、未改 P4 分支、未推送** |
| P4 保护 | 主仓库仍在 `task06-is-a-p4-scene-adapter` / `fe7d3dbe`，前后均为 5 个未跟踪日志文件（`results/2026*`），未增未减；未运行任何 P4 进程 |
| 迁入规模 | 受控文件 219 条（源提交范围内 200、当前 218） |
| 结果目录 | `results/` 19 个目录，其中 18 个为 `*_P2_*`（113 个受控文件）；唯一非 P2 目录为 `20260930_TASK00_mujoco_smoke`（P2 环境冒烟，无 P4 数据） |
| 环境 | `g++ 11.4.0`、`/usr/include/eigen3`、Boost 头文件存在；`/usr/bin/python3.10`=3.10.12 + numpy 1.24.4 + scipy 1.8.0 + pytest 6.2.5。**注意**：`PATH` 上的 `python3` 是 3.13.12（无 numpy），直接 `python3 scripts/...` 会失败 |

## 2. 迁入文件完整性（两层哈希）

证据：`p2/reviews/LEGACY_BLOB_CHECK.json`（由 `p2/tools/t00_blob_check.py` 生成，可复跑）。

**层 1 — Git blob SHA（源 `7787c75a` vs HEAD）**

| 区 | MATCH | MODIFIED | NEW | OMITTED |
|---|---:|---:|---:|---:|
| baselines/p2_pose_force | 9 | 0 | 0 | 0 |
| common | 12 | 1 | 0 | 1 |
| configs | 5 | 0 | 0 | 0 |
| docs/tasks | 4 | 0 | 0 | 0 |
| references | 1 | 0 | 0 | 0 |
| reports | 32 | 0 | 0 | 0 |
| results | 113 | 0 | 0 | 0 |
| scripts（P2） | 18 | 0 | 0 | 0 |
| tests | 4 | 0 | 0 | 0 |
| p2/（新路线图） | 0 | 0 | 19 | 0 |
| **合计** | **198** | **1** | **19** | **1** |

**层 2 — 验收 manifest SHA256（工作树字节 vs `P2_ACCEPTED_DELIVERY_FREEZE_MANIFEST.json`）**

- manifest 292 条；**181 条 SHA256 完全相同，0 条不符**。
- 111 条未导入：97 个 `.png`（Word 分页/contact-sheet 预览）+ 11 个 `report_data.json`/QA json + 2 个 `report_text.txt` + 1 个 `preview_status.md`。**全部位于 `reports/*_review_assets/`、`*layout_review*/`、`*report_assets*/`，属排版渲染资产，不含任何运行日志、`summary.json`、`cases.jsonl` 或轨迹数据。**

**三处必须记账的偏差**
1. `common/README.md` **MODIFIED**：当前为 `main` 版本（`84a696ec`，TASK02 精简说明），源提交为 `3ffe8814`（含测量/指标/Task02 交付说明）。原因是本分支基于 `main` 而非旧 P2 审计分支分支。**是文档，不是 P2 算法代码**；但 `common/README.md` 源版引用的 `common/metrics/README.md` 因此也缺失（OMITTED）。→ T01 需补一份"文档事实说明"，不得直接覆盖历史文件。
2. `common/metrics/README.md` **OMITTED**：指标定义文档（r(t)、d(t)、四元数角度、max/RMS 定义）。代码 `common/metrics/math.py|evaluate.py` 在，但定义说明缺失。T06 的 `position_error_m`/`orientation_error_rad` 定义需引用它，属**中等风险**。
3. `reports/P2_DELIVERY_ACCEPTANCE_FREEZE.md` 与 `reports/P2_ACCEPTED_DELIVERY_FREEZE_MANIFEST.json` **不在本分支**：它们产生于验收提交 `f4f9d3b9`（`7787c75a` 的子提交），而非冻结提交本身。`p2/CODEX_START_HERE.md` 要求"阅读 `reports/P2_DELIVERY_ACCEPTANCE_FREEZE.md`"在此分支**不可满足**。本轮通过 `git show f4f9d3b9:...` 只读取用，未导入、未改写。

## 3. 论文 ↔ 算法 ↔ 代码对应

完整逐式索引见 `p2/reviews/T00_EQUATION_INDEX.md`（式 1–26、H、表 I/II、Fig 1–9、视频）。要点：

**按原文实现的**：式 (1)–(9)、(11)–(14)、(16)（M 对角除外）、(17)、(18)（右 Euler，字面）、(19)–(21)、(25)。
**保留论文自身近似的**：式 (10) 的 `R̄`（代码注释明示"不是 Ad(D)"）。
**用户已批准的偏离**：式 (15) 不按印刷式，改用 `p2.spatial_free_log_constraint.v1`（不变量 `Nᵀτ̇ = 0`，自由 Log 分量保持初值）；印刷式的正号仍作为审计对照保留（`decisions.printed_eq15_preserved=true`）。
**故意不实现**：式 (22)–(24) 不用于生成力曲线（旧审计已发现印刷式 Jr 参数与式 (9) 直接微分不一致）。
**未实现**：式 (26) 关节级逆解——以 `U_applied = HᵀHU`（J=I、q̇₀=0）代替，属明确标注的理想 Cartesian 约化。
**代码有、论文无**：5 s 初始 settle、75 对预标定、视觉 bias、`Q_cont=0.004Q_table`、模式切换守门阈值、命令上限拒绝、延迟压力案。全部已在协议中标注 `ADAPTATION/ENGINEERING`，T01 需转成正式 deviation register。

**因此不能把旧实现整体称为"作者原始算法"**：接触演化（式 15）是替代解释，刚性/阻尼/惯量/抓点是适配，关节层是理想化。

## 4. 旧结果审计

### 4.1 70/70 动力学资格（`results/20261014_P2_implicit_qualification_v3_01/`）

实际是 70 个检查：36 = native 几何（3 模式 × 3 形状 × 4 运动）；18 = 力学（2 变体 × 9 种 H 组合）；6 = native 连续 Jacobian（AD vs 五点 50 位差分）；1 = implicit 与 canonical 残差；6 = 五秒积分（3 变体 × 粗/半步）；3 = 步长细化。
**它们证明的是**：C++ 与 Python canonical 等价、隐式中点收敛、积分稳定、Jacobian 正确。
**它们不证明**：论文轨迹可跟随、控制响应、与论文数值一致。
**一个需要写清的细节**：样本 `five_seconds_transport_coarse` 的终端力 ≈ 1e-19 N、终端速度 ≈ 1e-14 → 六个"五秒积分"都是**收敛到静止平衡**，不是持续运动/滑移轨迹。资格覆盖"稳态整合与收敛"，不覆盖"运动保真"。

### 4.2 35/35 组件资格（`results/20261014_P2_components_qualification01/`）

18 项估计器（状态契约无别名、6 类测量的解析 Jacobian、3 组离散预测 Jacobian、右 reset、迭代复用先验、Schmidt 冻结 C、Q 缩放、重复/错时戳拒绝、快速几何与 canonical 等价）+ 7 项观测（bias、只用 h_K、时钟、76 s 视觉关闭、75 对标定与新鲜初始化）+ 10 项控制（四条件开关、只用旧发布输入、GT 需显式诊断、手动抬升时序、测地参考、滑移参考、命令上限拒绝）。
**边界**：全部是"输入给定 → 输出符合定义"的组件检查，**没有一次反馈闭环**。

### 4.3 时序 2/2（`results/20261014_P2_clock_qualification01/`）

旧发布值与新命令/延迟实际值无关；粗/细步长的物理事件与发布时刻一致。

### 4.4 3.948 s 停止：证据链与根因

**事实**（`results/20261014_P2_closed_loop_suite02/case_11_exp3_7/`）

| 项 | 值 |
|---|---|
| 案例 | ID 11，exp3，seed 7，transport，非 GT |
| 停止 | `ESTIMATOR_MODEL_PAD_DOMAIN_INVALID`，t=3.948 s，tick 11844，phase=transport |
| 触发点 | `scripts/run_p2_closed_loop.py:103`：用**估计状态**重算接触，若 `|τ_lin|>.005 m` 或 `|τ_ang|>.15 rad` 即停止 |
| 上下文 | 0–3 s 为开环手动抬升，3 s 后 U≡0；**7 s 内力、13 s 位姿反馈均未到达**，日志中 UF/UP 全为 0 |
| 样本 | 987 个 250 Hz 运输样本、1619 次预测、829 次更新、3 次不收敛（最大连续 1，未触发"连续 3 次"停门） |
| GT 泄漏 | `GT_control_state_reads = 0` |
| 真实状态 | 物体几乎静止（|v|≈3e-11 m/s，|ω|≈8e-8 rad/s）；真实内力峰值 2.02e-3 N、内力矩峰值 2.89e-6 Nm → **真值全程在域内** |
| 估计状态 | 末态 |ω|=260.02 rad/s；估计 τ_x = −6.42 mm / +5.21 mm，越过 ±5 mm；估计姿态误差 0.118 rad |
| 协方差 | P 有限、最小特征值 5.59e-14、不对称度 0；ω_x 方差 2508.9 (rad/s)² |
| 保存矩阵 | `failure_filter_matrices.npz`：F 在最后一个 3 ms 预测上的特征值为 **−5.547** |

**关键交叉证据**（本轮发现并核对）

1. `results/20261014_P2_stage2_numerical_audit01/`（**在闭环之前**运行的静态审计）已算出：A 对象 plant 最快连续实特征值 **−2183.07 s⁻¹**；并显式计算了"原式(18) 4 ms 完整 Euler 预测 I+0.004A"的谱，最大特征值 **−7.732**（|·|>1）。C 对象为 −9335.8 s⁻¹ / −36.34。
2. 实际失败时保存的 F（3 ms）特征值 **−5.547**，与 `1 + 0.003×(−2183.07) = −5.55` 精确吻合 —— **同一个模态**。
3. 逐行读 `estimator.jsonl.gz` 可见：从 t≈0.26 s 起，ω_x 在每次"仅 EE1 更新"后反号并放大（−1.13 → +1.34 → −7.45 → +5.88 → −32.7 → +38.7），在"EE1+EE2+hK1+hK2"整包更新处被拉回（≈0.4）；周期与 200 Hz EE1 节拍一致。这是显式格式对刚性模态的典型两步振荡（负实特征值、|λ|>1）。
4. 所有预测间隔（1–4 ms）对该模态都不稳定：`1+0.001×(−2183) = −1.18`。

**根因判定（本轮，基于既有证据，未做新实验）**
- 直接原因：式(18) 右 Euler 预测在论文的 4 ms 滤波周期下，对本实现 soft-contact 模型的 −2183 s⁻¹ 快模态数值不稳定；每次预测把速度误差放大并反号，测量更新只能部分拉回，误差累积到估计垫片形变越界，被 5 mm/0.15 rad 域门拦下。
- **不是**：真值动力学发散（真值静止且域内）、测量伪造、GT 泄漏、增益/参数临场改动（`control_gain_or_condition_changes=false`、`no_reset=true`）、或"连续 3 次不收敛"停门。
- **仍不能唯一归因的部分**：该快模态来自本实现的 K/B/惯量/接触约束组合，作者实际使用的离散传播方式未公开；因此"论文模型不可复现"与"本实现的离散化选择不当"目前只能分开陈述，不能合并成前者。旧报告"不能唯一归因于 Euler"的说法在本轮可以**加强为**"Euler 是已量化的必要环节"，但仍不排除参数/几何适配放大该模态。

**为何它必须在 T04 前解决**：T05–T09 全部依赖同一预测器。若不先裁决传播格式，T05 必然复现同一停止，白白消耗修正预算。

### 4.5 其他保留的旧失败（均未被覆盖）

| 证据 | 内容 |
|---|---|
| `results/20261014_P2_implicit_qualification01/` | 两点固定差分门第 46 项 FAIL（行 9/列 27 差 6.38e-7 > 1e-7）；后经批准改五点四阶 oracle 才通过，原失败保留 |
| `results/20261014_P2_closed_loop_suite01/` | `FAIL_STOP_LAUNCH / OUTPUT_PATH_TYPE_MISMATCH`，0 案执行 |
| `results/20261014_P2_stage2_dynamics01/` | 120 s 墙钟在 3.324 s 物理时刻超时；11 项通过后停 |
| `results/20261013_P2_contact_geometry_qualification01/` | 66/66 程序 PASS，但交付判 INCOMPLETE（符号与覆盖），修正后另有 68/68 |
| `results/20261014_P2_closed_loop_suite02/summary.json` | `FAIL_STOP`，执行 1 案、完成 0 案，其余 19+10 案 `NOT_EXECUTED` |
| `reports/P2_IMPLICIT_QUALIFICATION_RESULTS.md` | ε 诊断表（1e-6/2e-6/5e-7）证明截断误差为主因，未替换资格 |

## 5. T01–T10 覆盖完整性

**结论：论文实验在规划层面无遗漏。** 式 1–26 有 T02–T05；表 I/II 与参数有 T01；Fig.6 exp1–4 有 T06；Fig.7 有 T07；Fig.8 有 T09；Fig.9 有 T08；视频两段分别落在 T04 与 T09。

**但存在 5 个必须补的规划缺口（不删除任何实验、不降低验收）**

| # | 缺口 | 影响任务 | 建议动作（补充规划，非改验收） |
|---|---|---|---|
| G1 | 协议 `model.objects` 只有 A、C，**缺 B1/B2**（0.280 kg / 75×140×40 mm） | T09 | T01 冻结对象集合 A/B1/B2/C 与惯量；B1/B2 与 A 共用抓取几何假设，需声明 |
| G2 | **无抓力控制/摩擦模型**（论文 Fig.9 依赖抓力降到 0.3 N、切向力 ≤0.3 N） | T08、T09 | T08 显式新增"抓力伺服 + 摩擦接触"子项；做不到则记 `NUMERICAL_MODE_TEST` + `PHYSICAL_SLIDE_NOT_VERIFIED` |
| G3 | Fig.9 时间基不一致：论文 0–250 s（事件约 50/130/150/200 s），旧协议为 30 s 替代（5/25 s，下移 200 mm） | T08 | T08 必须二选一并声明：按论文时间基重建，或明确记为"时间压缩替代"，禁用论文数值直接对标 |
| G4 | **装配布局无坐标**（Fig.5(b) 仅图像） | T09 | T09 需给出从图估读的布局并标 `ESTIMATED_FROM_FIGURE`，做敏感性；不得声称与作者一致 |
| G5 | **接触检测/最终放置未实现**（旧协议 `after_76: no plate contact`） | T09 | T09 需新增"外力估计 + 接触检测 + 慢速下放"子项，对应视频 2 / §IV-A 末段 |

另有 2 个**已覆盖但强度不足**的项（建议在 PRE 里加严，不改验收）：
- T04 只写"版本化新变体"，未写"逐步谱半径门"与"预测器稳定性前置门"→ 建议 T04 增加：每个预测区间记录 F 谱半径、ω/τ 域余量，先通过预测器稳定性门再做闭环。
- T06 未显式要求复算"卡尺 <0.1 mm / 0.42°"对应的**最终位姿精度**口径 → 协议已有 `GT final/world waypoint errors`，T06 PRE 需把它写成正式指标。

## 6. 可复用代码分级

**A 级 — 字节一致、有数学/组件资格、可直接作为 PAPER_BASELINE 复用**
`baselines/p2_pose_force/contact_geometry.py`（标 `ADAPTED_GEOMETRY`）、`mechanics.py`、`control.py`、`observations.py`、`clocking.py`、`native_kernel.cpp`、`native_model.py`、`configs/p2_closed_loop_protocol_v3.json`、`tests/test_p2_*.py`、`scripts/qualify_p2_*.py`、`scripts/audit_p2_*.py`。

**B 级 — 可复用但必须重新验证/改造**
- `estimator.py`：18 项 Jacobian/更新资格通过，**但式(18) 预测在本参数下不稳定**，只能作为 `PAPER_LITERAL_EULER` 基线保留，不能直接用于 T05。
- `scripts/run_p2_closed_loop.py`：runner 骨架、日志与失败保全设计很好（可复用），但**预算与逐案墙钟需重定**，且域门应改为"记录 + 分类"而非硬停（须先版本化）。
- `configs/*.json`：参数与时钟可复用；对象集合、装配布局、Fig.9 时间基需扩展。

**C 级 — 有已知问题，不得用于论文结论**
式(18) Euler 预测；式(10) 的 `R̄` 近似（有限形变）；native 隐式中点在 **C 对象 1/3000 步长**下谱半径 2.73（同审计已记录，T03 必须处理）；式(22)/(24) 只能作定性说明。

**D 级 — 完全未实现**
式(26) 关节级逆解与 7-DOF 模型；抓力伺服与摩擦；四物体装配场景；外力/接触检测；标准 EKF 公平对照；MuJoCo 独立物理；Fig.8/9 任何真实运行。

## 7. 未检查项（不得默认为通过）

- `native_kernel.cpp` 只做了代码阅读，**未编译、未运行**（T01）。
- `tests/test_p2_*.py` 未执行（T01）；本轮采信的是旧 `summary.json` 记录，不是重跑结果。
- Word/PDF 交付物不在仓库内，未核对；仅核对其渲染资产清单。
- 附加视频未取得（旧审计检索过作者站点/仓库/BibTeX，未定位到可认证实现或视频），视频两段实验当前只能"自建对照"，不能"复现"。
- Fig.5(b) 装配布局只做了目视读取，未提取坐标。
- 论文采用的离散传播方式、作者惯量、抓取点、基座相对位姿均**未知**，本报告不假设。
- P4 未审计（本轮禁止）。

## 8. 进入 T01 前必须解决的问题

1. **预测器裁决（阻断级）**：式(18) 在 4 ms 下对 −2183 s⁻¹ 模态不稳（预注册值 −7.732，实测 F −5.547）。必须在 T01 内以**协议决策**形式确定：保留 `PAPER_LITERAL_EULER` 为基线 + 新增一个**版本化**传播变体（如矩阵指数/隐式/子步），并预登记"两者并行、不替代"的对照规则。不做此裁决，T04 无法通过，T05 起必重复失败。
2. **预算重定（阻断级）**：实测 24.94 s 墙钟完成 5 s settle + 3.948 s 运输 ≈ **2.79× 实时**。95 s 运输 ≈ 279 s 墙钟，**超过冻结的 120 s/案**；20 主案 ≈ 5600 s，加上其他案将逼近/超过 7200 s 套预算。需用户在 T01 决定：提高单案/套预算，或先做不改科学判据的性能优化（native 已存在，但日志频率、每 4 ms 全量 JSON 是主要开销）。
3. **验收记录可读性**：`P2_DELIVERY_ACCEPTANCE_FREEZE.md` 与验收 manifest 不在本分支。需决定是"只读引用 `f4f9d3b9`"还是"以不覆盖方式补入 `p2/reviews/` 引用副本"。本轮采用只读引用。
4. **文档偏差**：`common/README.md` 与缺失的 `common/metrics/README.md` 需在 T01 写事实说明；不得直接改写历史文件。
5. **环境固定**：`PATH` 的 `python3`=3.13 无 numpy；T01 必须写死 `/usr/bin/python3.10`（或建 venv），并记录 g++/Eigen/Boost 版本与 native 编译产物 SHA。
6. **对象与场景冻结**：补 B1/B2 质量尺寸、装配布局、Fig.9 时间基（见 G1/G3/G4）。

## 9. 后续任务顺序建议

- **保持 T01→T02→T03→T04→T05→T06→T07→T08→T09→T10 的总体顺序不变**（依赖关系正确：T08 的滑动是 T09 装配 C 块的前置，现顺序已把 T08 放在 T09 前）。
- **建议把两件事前移到 T01（不新增科学运行）**：(a) 预测器离散化裁决与 deviation register；(b) 预算/性能基线。
- **建议 T03 增加一个"慢模态/快模态谱"记录项**（复用 `audit_p2_stage2_numerics.py` 的方法），把 −2183/−9335 s⁻¹ 作为已知常数带进后续所有闭环，避免再次"跑完才发现不稳"。
- **不建议**调整 T06–T10 的相对顺序，也不建议为省时间合并 T08/T09。

## 10. 状态与决定请求

| 门 | 状态 |
|---|---|
| T00 | `COMPLETE`（静态审计）；判定 `PROVENANCE_PASS_WITH_RECORDED_DEVIATIONS` |
| T01–T10 | `NOT_EXECUTED` |
| 论文整体 | `PARTIAL`（数学/组件有证据，实验 0 取得） |

**需要用户裁决**
1. 是否批准进入 T01？
2. 是否批准把"式(18) 传播格式裁决 + 预算重定"作为 T01 的两项前置决议（只做协议与性能，不跑科学实验）？
3. 单案/套墙钟预算如何定（保持 120/7200 s，或按 2.79× 实测率重定）？
4. 验收 manifest 采用"只读引用旧提交"还是"补入副本"？

**本轮未做**：未启动 T01–T10，未运行大型仿真，未修复旧闭环，未开始论文实验，未合并到 `main`，未触碰 P4。
