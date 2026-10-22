# P2-T04 R1 PRE — 冻结观测流离线重放（模式 A/B 各一次）

**授权**：Issue #35 2026-10-19 T04 Stage A 审查（R1 有条件批准）
**前置**：`T04_STAGE_A_ERRATA.md`（资格勘误已完成：Simpson 门可达、判据补齐、trace 对账、噪声模型声明）
**分支**：`reproduce-p2-numerical-simulation-20261018`，起点见 §6

---

## 1. 冻结输入（不可变）

| 文件 | 用途 |
|---|---|
| `p2/runs/20261019_103729_T01E_SMOKE_case11_exp3_seed7/estimator.jsonl.gz` | 事件序列（1620 行：tick、time、U、消费样本、创新） |
| 同 `sensors.jsonl.gz` | 观测值/协方差/样本 id/时间戳（2048 行，取运输段 1892+6） |
| 同 `initialization.json` | 初始估计（7 块）、P0、已消费样本 |
| 同 `commands.jsonl.gz`、`plant.jsonl.gz` | 交叉核对；plant 仅事后评分 |

**禁止**：重新生成观测、扩展时间流、GT 进反馈、改 Q/R/域门/seed/时间戳。

## 2. 重放因果链（与原 runner 逐事件对应）

```
for each estimator row i≥1 (按冻结顺序):
    U_i   = row.old_published_model_input      (2×6，冻结)
    t_i   = row.time_s                          (冻结)
    filt.predict_to(t_i, U_i)                   # 模式 A: 原代码; 模式 B: 子类覆盖 predict
    if row.observations_consumed:
        packet = [Observation(冻结 sensors 值) for 每个消费样本 id]
        filt.update(packet)
    域门: native.contact(filt.state, U_i, modes, ph_est)
         |tau|>5mm/0.15rad → ESTIMATOR_MODEL_PAD_DOMAIN_INVALID
```

初始滤波器：`initialization.json.estimate` + `P0`（逐位来自原运行）；`seen_samples` 预置
初始化已消费样本；`rate_provider = native.continuous_linearization`；A-physics = `observer=True`。

## 3. 模式

- **模式 A `PAPER_LITERAL_EULER`**：`est.RightIESEKF` 原类，原 `predict`。
- **模式 B `ADAPTED_STABLE_PROPAGATION_V1`**：重放器内子类覆盖 `predict`
  （`stable_propagation.propagate`），**不修改 `estimator.py`、不设为默认路径**。

## 4. 验收与停止

| 门 | 判据 |
|---|---|
| A 重放有效 | 预测数 1619、更新数 829、停止 tick 11844/t=3.948、reason 相同；重放 state/P_diag/innovation 与冻结行最大绝对差 ≤1e-12 |
| A 无效 | 任一不满足 → `REPLAY_INVALID`，停止，不跑 B |
| B 前缀 | 跑完冻结记录（3.948 s）无失败 → `PREFIX_SURVIVED`；失败 → 记录时刻/原因 |
| B 禁止 | 不得标"4.5 s 通过"或"闭环成功" |

容差预声明：状态/P/创新 max-abs ≤ **1e-12**（JSON 浮点往返精确，预期 ~1e-16）。

## 5. 预算（硬上限 180 s）

| 阶段 | 上限 |
|---|---:|
| 勘误数值前置（已完成并另计） | — |
| 模式 A 重放 | 45 s |
| 模式 B 重放 | 90 s |
| 核验与报告 | 15 s |

看门狗：每事件检查累计墙钟，超限即 `BUDGET_STOP` 落盘。**无重试。**

## 6. 版本

- 代码 HEAD：记录于 manifest；重放脚本 `p2/tools/t04_r1_replay.py`
- 输入 SHA256：见 `T04_R1_AB_COMPARE.json.inputs`
- 输出：`p2/runs/20261019_T04_R1/`（新目录，不覆盖任何已有目录）
