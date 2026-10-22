# P2-T01 PRE — 环境/参数冻结、式(18)传播裁决、预算与性能基线

**任务**：`p2/tasks/P2_T01_ENV_PROTOCOL.md`（G0 门），并按 Issue #35 审查意见（2026-10-19 评论）前移两项
**分支**：`reproduce-p2-numerical-simulation-20261018`
**前置**：T00 本地提交 `0b3448ee` 已推送至同名远端分支（`a2f023d9..0b3448ee`）
**本轮性质**：静态协议 + 数学分析 + **明确预算的微基准**。**不启动闭环、不重跑 30 案、不改估计器源码。**

---

## 1. 范围

### 1.1 原 T01 内容（保留）

1. 记录 Python/NumPy/SciPy、g++、Eigen、Boost 版本与解释器路径（含 `PATH` 陷阱）。
2. 审计 `baselines/p2_pose_force`、`tests/test_p2_*`、`scripts/*p2*.py` 的导入依赖，确认不依赖已移除的 P4 辅助模块。
3. 以 `configs/p2_closed_loop_protocol_v3.json` 为历史基线**只读**，新建独立版本 `p2/configs/paper_reference_v1.json`。
4. 从原文抽出 Table I–II、物块质量/尺寸、时序、指标；缺失量标 `UNKNOWN` 并给出敏感性处理方式，不静默猜测。
5. 仅在 PRE 批准后执行短 smoke。

### 1.2 新增（Issue #35 审查意见）

6. **式(18) 数值传播裁决**：保留 `PAPER_LITERAL_EULER` 与其失败证据；设计版本化 `STABLE_DISCRETIZATION_V1` 候选；在同一快模态、采样时间、物理参数下比较显式 Euler 与稳定格式；必须同时覆盖 SE(3) 状态更新、状态转移矩阵、协方差传播、测量更新时序。
7. **计算预算与性能审查**：分别量化环境初始化、动力学积分、状态预测、测量更新、日志写入；明确 95 s 任务的仿真时长/墙钟口径；给出 exp1–exp4 单实验与总预算、提前停止条件。
8. 登记：Python 环境、缺失参数、**111 个未导入的历史排版资产**（逐条列出，不得写"零遗漏所有资产"）、Fig.9 与四物体装配的建模缺口。
9. T03 计划补充：快/慢模态谱、受扰运动验证、C 的 `ρ=2.73` 核查。**本轮不执行 T03。**

### 1.3 明确不做

- 不运行 30 案、不运行任何 95 s/30 s 控制案例、不跑完整闭环。
- 不修改 `estimator.py`/`mechanics.py`/`native_kernel.cpp` 的科学内容；`STABLE_DISCRETIZATION_V1` 只出设计与数学表，不落实现。
- 不改论文参数、增益、Q/R、时钟、验收判据；不覆盖 T00 或旧失败。
- 不触碰 P4 的任何文件、分支、进程、报告。

## 2. 预期输入

| 输入 | 位置 |
|---|---|
| 论文（8 页） | `references/private_sources/P2_original.pdf`（私有，不入库）；Table I/II、Fig.5(d)、Fig.6–9 |
| 历史协议 | `configs/p2_closed_loop_protocol_v3.json`（SHA256 `0de8477f…f794c`） |
| 失败证据 | `results/20261014_P2_closed_loop_suite02/case_11_exp3_7/`（F/Qd/P/K/H npz、estimator/sensors/plant 日志） |
| 快模态证据 | `results/20261014_P2_stage2_numerical_audit01/`（λ_min = −2183.07 s⁻¹；4 ms Euler 因子 −7.732；C 为 −9335.81 / −36.34） |
| native 构建 | `/home/ubuntu2004/lmy/.p2_native_build_v3/p2_native.so`（源码 SHA 未变，预期命中缓存不重编） |

## 3. 预期输出

| 文件 | 内容 |
|---|---|
| `p2/reviews/T01_PRE.md` | 本文件 |
| `p2/reviews/T01_DISCRETIZATION.md` | 式(18) 裁决：模态、稳定性判据、格式对照表、SE(3)/Φ/Q_d/更新时序设计、风险与回退 |
| `p2/reviews/T01_BUDGET.md` | 成本分解、口径定义、单实验/总预算、提前停止条件、性能优化备选 |
| `p2/reviews/T01_ENVIRONMENT.md` | 环境、依赖、导入审计、缺失参数与资产登记 |
| `p2/configs/paper_reference_v1.json` | 论文参数与来源（`PAPER` / `UNKNOWN` / `ADAPTATION`）独立冻结 |
| `p2/tools/t01_discretization_modes.py` | 闭式放大因子表（纯数学，不足 1 s） |
| `p2/tools/t01_cost_probe.py` | 微基准探针（硬上限见 §4） |
| `p2/reviews/T01_POST.md` | 实际结果、通过/失败/未做、决定请求 |

## 4. 计算预算（本 PRE 授权范围）

**微基准总墙钟上限 60 s，单项上限 10 s，超时即中止并记 `BENCH_TIMEOUT`。**

| 探针 | 规模 | 上限 |
|---|---|---|
| 导入 P2 模块 + 读协议 + native 缓存校验 | 1 次 | 10 s |
| `native.contact` | 200 次 | 5 s |
| `native.advance(dt=1/3000, steps=1)` | 200 步 | 10 s |
| `native.continuous_linearization` | 100 次 | 10 s |
| `RightIESEKF.predict(0.004)` | 200 次 | 10 s |
| `RightIESEKF.update(packet)` | 100 次 | 10 s |
| 日志写入（真实行长，gzip） | 1000 行 | 5 s |
| `scipy.linalg.expm(42×42)` | 20 次 | 5 s |

不写轨迹、不留 plant 状态演化、不调用 `run_p2_closed_loop.py`。所有产物标 `ENGINEERING_SMOKE`，不得作为科学结论。

## 5. 预登记判定规则（式 18 裁决）

1. `PAPER_LITERAL_EULER` 永久保留为对照基线，失败证据不改写；新格式**只能并列**，不得替换基线记录。
2. 稳定性判据：对连续谱 λ，要求 `|1 + hλ| < 1`（Euler）或所选格式的放大因子 `|R(hλ)| ≤ 1`，并在 `h = 1/3000, 1/1000, 1/250 s` 三个采样率上给出表。
3. 格式必须保持**同一连续模型**：同一 `f(X,U)`、同一 `Q_c`、同一测量时序；只允许改离散传播算子。
4. 协方差一致性：`P⁺ = Φ P Φᵀ + Q_d`，`Q_d` 必须与 `Φ` 同源（Van Loan 或等价），禁止 `Φ=exp(hA)` 配 `Q_d=hQ_c` 的混搭；Joseph 形式与右 reset 保持。
5. 误差阶与耗散：记录每种格式的局部截断阶、是否 L-stable、对 λh→−∞ 的极限（Euler→−∞、CN→−1、IE→0、exp→0），并说明是否会引入非物理阻尼。
6. 任何格式若使 `ρ(Φ)>1` 即判不合格；若 `ρ(Φ)→1` 但引入 O(h) 人工阻尼，须单列"以精度换稳定"的代价，不得声称"更准"。
7. 实现代价必须给出每步的额外场/Jacobian 调用次数与实测/估算墙钟，作为 T04 选型依据。

## 6. 验收条件

- 环境与解释器路径可复现，`python3` 陷阱被显式记录并有固定命令。
- `paper_reference_v1.json` 每个数值都有来源标记；原文未给的量全部 `UNKNOWN`，不得填猜测值。
- 式(18) 三个采样率 × 至少 5 种格式的放大因子表可复算；`PAPER_LITERAL_EULER` 在 4 ms 的不稳定被显式复现（解析层面）。
- 协方差传播与测量时序有书面设计，且明确不改测量节拍。
- 预算口径明确到"分子分母"，给出 95 s 单案墙钟与 exp1–exp4 总预算，并给出提前停止条件。
- 111 个未导入资产逐条登记；Fig.9 与装配缺口有明确状态。
- 总体状态仍为 `PARTIAL`；T01 自身状态最多 `PROTOCOL_FROZEN_PENDING_REVIEW`。

## 7. 停止条件

- 微基准任一项超时/超预算 → 停止该项，记录，不追加尝试。
- 发现必须改连续模型（而非仅离散化）才能稳定 → 停止，上报，不擅自改模型。
- 发现原文参数与协议冲突 → 记录冲突，交用户裁决，不静默选一个。
- 若 T00 远端交付被审查否决 → 立即停止 T01。
