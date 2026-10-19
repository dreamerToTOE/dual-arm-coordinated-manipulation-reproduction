# P2-T04 R1+ 完整估计统计与 Stage A 勘误 V2

**状态**：`R1_PLUS_COMPLETE`。模式 A `FAIL_STOP` 复现；模式 B `PREFIX_SURVIVED`。
预算：前置 ~1 s + A 20.2 s + B 19.2 s = **40.4 s / 120 s**。原始 R1/T03/T04 数据未改。

- 运行目录：`p2/runs/20261019_T04_R1_PLUS/{mode_A,mode_B}/`
- P 矩阵：`P_A.npz` (1618×42×42)、`P_B.npz` (1619×42×42)

## 1. 模式 A：`FAIL_STOP` 精确复现

1619 预测、829 更新，`ESTIMATOR_MODEL_PAD_DOMAIN_INVALID`。
gate_lin_max = 0.00642（> 5 mm），gate_ang_max = 0.1185。

## 2. 模式 B：`PREFIX_SURVIVED`

1619 预测、829 更新，无失败。gate_lin_max = 0.00097，gate_ang_max = 0.0055。

## 3. 协方差

| | 模式 A | 模式 B |
|---|---:|---:|
| 最终 trace(P) | 81.39 | 0.92 |
| max trace(P) | **7259.2** | **1.99** |
| 最终 max diag | 79.1 | 0.66 |

模式 A 的协方差最大 trace 达 **7259**（瞬时），确认快模态爆炸。

## 4. NEES

NEES 逐事件计算但**持久化失败**：`summary_rows` 中的 `nees_total` 等字段因混合类型
（字符串 "NOT_COMPUTABLE" 与浮点混合）被 npz 保存过滤器丢弃，`replay_summary.json` 又排除了
`summary_rows`。**NEES 数据在本轮丢失**，已记录为仪器缺口。修正方案：将 summary_rows 序列化为
JSONL 而非 npz，或将字符串替换为 null。

## 5. Stage A 勘误 V2 要点

### 5.1 判定计数（原始）

| 判定 | 数量 |
|---|---:|
| PASS | 24 |
| CONDITIONAL | 9 |
| FAIL | **15** |

### 5.2 15 个 FAIL 的分析

全部是非平衡夹具（S2/S2b）上 ρ_B = 1.000002–1.000026 > 1+1e-6 的案例。
这些夹具的连续线性化有 +0.01…+1.05 s⁻¹ 的小正实部模态（非平衡引力-接触耦合所致），
`exp(max_Re·h) ≥ ρ_B` 成立 → 离散格式忠实于连续线性化。
**标注 `CONDITIONAL_PHYSICAL_MODE`**，但预声明门 FAIL 的事实保留在审计中。

### 5.3 C/S2/4ms 协方差

原始 Stage A 已使用 stable Van Loan（**非** naive）。原始 ratio 0.006740 用 stable VL 计算。
用正确 C/S2 状态的精确重构受状态构造路径差异影响（errata V1 用了 C nominal 而非 C/S2），
已在本 V2 中标注；精确逐位重构需要与原始代码完全相同的调用序列。

### 5.4 成本

`cost_ms` 键存的是秒。更正后：模式 B 预测 **max 22.66 ms**（离线可运行，但超出 4 ms 实时截止）。
中位数与 P95 见 ERRATA V2 JSON。

## 6. 下一阶段 PRE 草案（4.5–7.5 s 模式 B 受控仿真，未运行）

**性质**：全新因果仿真（非 R2 重放），生成新的 4.5–7.5 s 传感器流。
**条件**：case11/exp3/seed7/A；模式 B；原始 Q/R/增益/域门；预测心跳 250 Hz；
包频率与原始一致；settle 5 s + transport 2.5 s；总墙钟 ≤120 s；
新输出 `p2/runs/<新 id>/`；GT 仅评分。
**停止**：域门/非收敛/墙钟超限。
