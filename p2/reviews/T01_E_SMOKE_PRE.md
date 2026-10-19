# P2 T01-E SMOKE PRE — 单案例受限管线测试

**性质**：`ENGINEERING_SMOKE`（工程管线 + 估计器数值行为），**不是**论文实验。
**授权**：Issue #35，2026-10-19 T01-E POST 裁决；只批准**一次**、transport ≤4.5 s、总墙钟 ≤60 s 的运行。

---

## 1. 目的

验证以下四件事，且只验证这四件事：

1. O2 日志在**真实 runner 数据**（含 NumPy 数组）下能写入、读回、异常落盘；
2. 优化后的估计器在真实事件流（4 ms 心跳 + 200/50/100 Hz + 15 fps）下的行为与耗时；
3. 原始 `PAPER_LITERAL_EULER` 在真实闭环前缀中的数值失败是否复现、以及失败时证据是否完整；
4. 无 GT 进入主反馈、事件计数/时间戳自洽、硬预算被执行。

**不证明**：反馈控制成功（7 s 内力、13 s 位姿都未到达）、论文 Fig.6–9、估计器稳定、95 s 可行。

## 2. 固定条件（不可改）

| 项 | 值 |
|---|---|
| 案例 | id=11，condition=`exp3`，seed=7，object=A，variant=`transport`，`GT=False` |
| 预测器 | `PAPER_LITERAL_EULER`（4 ms 右 Euler，未改） |
| settle | 原始 5 s（15000 ticks @1/3000） |
| transport | **≤ 4.5 s**（13500 ticks） |
| 总墙钟 | **≤ 60 s** |
| 协议 | `configs/p2_closed_loop_protocol_v3.json`，未修改 |
| Q/R、增益、初值、时钟、域门 | 全部原值 |
| GT | 只用于评分/诊断，主反馈零读取 |

## 3. 精确命令

```bash
cd /home/ubuntu2004/lmy/p2-num-sim-20261018
/usr/bin/python3.10 p2/tools/run_p2_smoke.py \
  --confirm case11-exp3-seed7-A \
  --transport-limit-s 4.5 \
  --wall-cap-s 60
```

入口 `p2/tools/run_p2_smoke.py` 为 fail-closed：`--confirm` 不匹配、limit 超出 (0,4.5]、wall 超出 (0,60]
一律拒绝（退出码 2）；代码中无 case 列表、无循环，**不可能启动其他 29 案**。
所有输出写入 `p2/runs/<run_id>_T01E_SMOKE_case11_exp3_seed7/`，`results/` 不被触碰。

## 4. 执行前检查（必须先通过）

| 检查 | 命令 | 通过条件 |
|---|---|---|
| O2 真实行序列化 | `/usr/bin/python3.10 p2/tools/t01e_log_preflight.py` | `verdict: PASS`：300 事件、必需字段每行都在、bulk 仅在快照行、`W`/`P_diagonal` 逐位往返、ring=200 全量、dump 可读、NaN 记为 `"nan"` |
| 比较器负例（回归） | `/usr/bin/python3.10 p2/tools/t01e_compare_tests.py` | `all_passed: True` |
| 优化等价性（回归） | 生成候选 + `t01e_compare.py` | 444/444 位相同 |

## 5. 失败判据与状态

| 状态 | 含义 |
|---|---|
| `FAIL_STOP` + `ESTIMATOR_MODEL_PAD_DOMAIN_INVALID` | **预期可能结果**：原始 Euler 在 ~3.948 s 域越界。**保留为科学失败**，不得改参数/关检查绕过 |
| `FAIL_STOP` + 其他原因 | 记录原始 reason 与 traceback，不做第二次尝试 |
| `SMOKE_TRUNCATED` | 跑满 4.5 s 未失败：仅表示管线走通，**不表示控制成功** |
| `CASE_WALL_LIMIT` | 60 s 墙钟用尽：记录超时点与已落盘证据 |
| 入口拒绝 / 导入错误 | 退出码 1/2，不重试 |

**不自动重试**；不在同一轮内改任何参数后重跑。

## 6. 证据清单（运行后核对）

1. `summary.json`、`termination.json`（若失败）、`smoke_manifest.json`；
2. `plant.jsonl.gz`、`estimator.jsonl.gz`、`sensors.jsonl.gz`、`commands.jsonl.gz`、`settling.jsonl.gz`、`events.jsonl`；
3. `failure_context_plant.jsonl`、`failure_context_estimator.jsonl`（异常时）；
4. 事件数/时间戳一致性：同一 tick 的预测、更新、样本 id；
5. `GT_control_state_reads == 0`；
6. 分阶段墙钟（settle / transport）与更新/预测耗时采样；
7. 全部文件 SHA256。

## 7. 预算

| 阶段 | 上限 |
|---|---|
| preflight（真实行序列化 + 负例 + 等价性） | ≤ 60 s |
| smoke（settle 5 s + transport ≤4.5 s） | **≤ 60 s 墙钟** |
| 结果核对与报告 | ≤ 60 s |

**硬停止**：任一阶段超时即停，保存已有证据，不做第二次运行。
