# P2 T04-B PRE — 模式 B 受控闭环仿真（5 s settle + 7.5 s transport）

**性质**：新因果仿真（**非 R2 重放**），产生新的传感器流。模式 B 估计器 + 原 native plant + 原控制器。
**授权**：Issue #35 R1+ 审查（B-coupled PRE 草案要求）
**分支**：`reproduce-p2-numerical-simulation-20261018`

---

## 1. 固定条件

| 项 | 值 |
|---|---|
| 案例 | id=11, exp3, seed=7, A, transport, GT_control=False |
| 估计器 | `ADAPTED_STABLE_PROPAGATION_V1`（`StableRightIESEKF`） |
| plant | 原 native 隐式模型（未改） |
| 控制器 | 原 `PoseForceController`（未改） |
| Q/R/增益/传感器/域门/时钟 | 全部原值 |
| precalibration | 原样 75 对 |
| settle | 原样 5 s |
| transport | 0 → **7.5 s**（22500 ticks） |
| 内力反馈 | t=7 s 开启（原始 event_ticks 包含 7） |
| 位姿反馈 | **不运行**（13 s > 7.5 s） |
| 墙钟 | ≤ **120 s** |

## 2. 精确命令

```bash
/usr/bin/python3.10 p2/tools/t04_b_coupled.py \
  --confirm case11-exp3-seed7-A-modeB \
  --transport-limit-s 7.5 --wall-cap-s 120
```

入口 fail-closed；输出 `p2/runs/<unique>/`；不触碰 `results/`。

## 3. 预期事件

| t | 事件 |
|---|---|
| 0–5 s | settle（无估计器/控制） |
| 5 s | transport 开始，估计器初始化 |
| 5–7 s | 无反馈（内力/位姿均未开启），估计器自由运行 |
| **7 s** | 内力反馈开启（PoseForceController 激活 force 通道） |
| 7–7.5 s | 内力反馈运行 0.5 s |

## 4. 预算

| 阶段 | 上限 |
|---|---:|
| precalibration + settle (5 s) | ≤40 s |
| transport (7.5 s) | ≤75 s |
| 合计 | **≤120 s** |

## 5. 停止条件

- 域门（5 mm / 0.15 rad）→ `FAIL_STOP`
- 连续 3 次不收敛 → 停止
- 墙钟 120 s → `CASE_WALL_LIMIT`
- 到达 7.5 s → `SMOKE_TRUNCATED`（非论文实验完成）

## 6. 交付

POST + manifest + 估计误差图 + 内力曲线 + P/covariance 曲线 + 事件台账。
