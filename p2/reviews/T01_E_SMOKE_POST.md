# P2 T01-E SMOKE POST — 单案例受限管线测试结果

**状态**：`ENGINEERING_SMOKE` 已执行（唯一一次科学运行），结果 **`FAIL_STOP`（科学失败，预期可能）**；
仪器/日志检查 **12/12 通过**。论文复现仍为 **PARTIAL**。

- 运行目录：`p2/runs/20261019_103729_T01E_SMOKE_case11_exp3_seed7/`
- 案例：id=11，exp3，seed=7，object A，`PAPER_LITERAL_EULER`，无 GT 反馈
- 限制：settle 5 s + transport ≤4.5 s，总墙钟 ≤60 s
- 实际：transport 在 **3.948 s** 因 `ESTIMATOR_MODEL_PAD_DOMAIN_INVALID` 停止；总墙钟 **26.59 s**
- 全程未改 Q/R、增益、初值、时钟、域门；未跑 T03/T04；未触碰 P4

---

## 1. 执行记录（两次调用，一次科学运行）

| # | 时间 | 结果 | 说明 |
|---|---|---|---|
| 1 | 10:35:23 | **基础设施中止**（precalibration，tick=null） | `NameError: name 'inverse' is not defined`，见 §9。**未推进任何物理时间**，不算科学运行 |
| 2 | 10:37:29 | `FAIL_STOP` @ 3.948 s | 修复后的唯一授权运行 |

第一次中止留下了完整 `termination.json`（reason/traceback/phase=precalibration），未删除。
两次运行目录互不覆盖；`results/` 未被触碰。

## 2. 科学结果

| 项 | 值 |
|---|---|
| 状态 | `FAIL_STOP` |
| 原因 | `ESTIMATOR_MODEL_PAD_DOMAIN_INVALID` |
| tick / 时间 | 11844 / **3.948 s** |
| 运输样本 | 987（250 Hz） |
| 估计器预测 / 更新 | 1619 / 829 |
| 不收敛更新 | 3（最大连续 1，未触发"连续 3 次"停门） |
| GT 控制读取 | **0** |
| 末态估计 \|ω\| | **260.021 rad/s** |
| 末态真值 \|ω\| | 8.1e-08 rad/s |
| 末态 published U | 全零（手动抬升已结束，力/位姿反馈尚未开启） |
| 墙钟 | 26.59 s（< 60 s） |

与 2026-10-14 的历史运行对比：同 tick 11844、同 3.948 s、同 reason，历史 \|ω\| 260.0205 vs 本次 260.021
→ **确定性复现**。优化未改变数值行为（与 444/444 位相同一致）。

**这不是 `SMOKE_TRUNCATED`**：运行在 4.5 s 之前因真实数值失败停止；也不是管线失败（日志与证据完整）。
7 s 内力、13 s 位姿反馈均未到达，**不能据此声称反馈控制有效或无效**。

## 3. 日志验收（`smoke_verification.json`）

| 检查 | 结果 |
|---|---|
| summary 存在且与日志行数一致（987） | PASS |
| plant / estimator 时间戳单调 | PASS |
| 每行含 `state`、`h_N_Nm`、`internal_N_Nm` | PASS |
| 每行含 `state`、`P_diagonal` | PASS |
| 被抑制行不含 `W`（降频规则生效） | PASS |
| 每个 plant tick 都出现在 estimator 流中（含包时刻） | PASS |
| 同 tick 时间戳一致 | PASS |
| `GT_control_state_reads == 0` | PASS |
| 失败上下文各 200 事件 | PASS |
| termination 与 summary 的 reason 一致 | PASS |

日志规模：plant 987 行、estimator 1620 行、sensors 1 897 条观测、commands 987 行、settling 1 251 行、
events 若干；全部可 `json.loads` 读回。

## 4. NumPy 序列化（已修复）

`EventLog._write` 原先直接 `json.dumps(row)`，遇到 `ndarray`（`D/W/hK/P_diagonal/innovation_*`）会
`TypeError`。新增 `_jsonable`：`ndarray → 嵌套 list`、`np.floating → float`、`np.integer → int`、
`np.bool_ → bool`；**非有限值不丢弃、不裁剪**，写成 `"nan"/"inf"/"-inf"` 字符串（沿用旧 runner `clean()` 约定，可检索）。

真实行预检（`t01e_log_preflight.py`）：plant 300 行 / estimator 300 行，全部解析成功；
`W`、`P_diagonal` **逐位往返**；NaN 写成 `"nan"` 且可检出；标定路径 75 对 2 次迭代收敛。

## 5. 环形缓冲（已修复为完整行）

原实现只存 `REQUIRED_KEYS` 摘要。现改为保存**最近 200 个完整行**（含 `state/W/innovation/...`，已转 JSON 类型），
失败时写入 `failure_context_plant.jsonl`（1.81 MB）与 `failure_context_estimator.jsonl`（0.96 MB）；
读回检查：每个文件 200 个事件、`reason` 正确、首事件含 `state`。

## 6. 1 Hz 降频边界（按真实载荷核对）

| 字段 | 频率 | 依据 |
|---|---|---|
| `W`、`D`、`W_singular_values`、`estimated_state`、`solver` | **1 Hz + 异常触发** | 纯诊断大载荷 |
| `state`（7 块位姿）、`h_N_Nm`、`internal_N_Nm`、`tau`、`hK_N_Nm`、`hB_N_Nm` | **每个事件（250 Hz）** | 半步门与指标提取逐点读取 |
| `P_diagonal`、创新、迭代/收敛、样本 id | 每个事件 | 审计必需 |

本次 plant/estimator 各 4 个 bulk 快照；被抑制行确认不含 `W`。**未降频半步门依赖的任何字段。**

## 7. 成本（本运行）

| 项 | 值 | 来源 |
|---|---:|---|
| 总墙钟 | **26.59 s** | summary（唯一实测总量） |
| settle 阶段（5 s 仿真） | 0.64 s | 组件基准（同批量、同日志） |
| 预测 4 ms | 1.16 ms | 组件基准 |
| 更新 1 观测 / 2 迭代 | 3.72 ms | 组件基准 |
| 更新 3 观测 / 3 迭代 | 13.66 ms | 组件基准 |
| 更新 6 观测 / 4 迭代 | 36.34 ms | 组件基准 |
| plant 单步 | 0.083 ms | 组件基准 |

用运行日志中真实的 (观测数, 迭代数) 分布（1 obs:395、2:40、3:197、4:178、6:19；迭代 2/3/4/5 混合）
加权，滤波部分约 **11.5 s**；其余约 **14 s** 归因于 plant 运动中的 Newton 迭代、每事件
`require_contact`/`validate_state`、行构造与 `clean`、传感器生成与 gzip I/O —— **未逐项插桩**。

**限制**：本次运行的 summary 没有分阶段墙钟（插桩是在运行后加入的）。下次授权运行将输出
`timing_s = {precalibration, settle, transport, total}`。
**不声明端到端加速**：单次墙钟受机器负载影响（同机微基准波动可达 2×），且本次总时长与历史 24.94 s
不可直接比较（历史运行日志路径不同、机器状态不同）。

## 8. GT 与预算

- `GT_control_state_reads = 0`；termination 中 `diagnostic_GT=false`；无 GT 进入主反馈。
- 墙钟 26.59 s ≤ 60 s；transport 3.948 s ≤ 4.5 s；未触发 `CASE_WALL_LIMIT`。
- 运行一次，无重试；失败后立即停止。

## 9. 发现并修复的集成缺陷（重要）

| 缺陷 | 影响 | 修复 |
|---|---|---|
| `observations.calibrate_paired_visuals` 仍引用 O1-a 删除的 `inverse` | 标定阶段 `NameError`，管线无法启动 | 改用 `_inv4/_log4`；**oracle 未覆盖标定路径**，已把标定检查加入 `t01e_log_preflight.py` |
| `EventLog._write` 未转换 ndarray | 真实运行 `TypeError` | `_jsonable` + 真实行预检 |
| ring 只存摘要 | 失败无法复盘 | 存完整 200 行 |
| `end_s` 在异常路径未定义 | 早失败时掩盖原始原因 | 提前初始化 |

第一条说明：T01-E 的 444 数组 oracle **没有覆盖预标定流程**，这是等价性覆盖的真实缺口；
现在 preflight 会跑 75 对标定并断言收敛。

## 10. 结论

- **管线可用**：日志写入/读回、事件时序、异常上下文、1 Hz 降频、GT 隔离、硬预算全部通过。
- **估计器仍按预期数值失败**：3.948 s 域越界，与历史一致；根因仍是 T01 裁决的 4 ms Euler 快模态不稳定。
- **T03 可以开始**（plant 谱、C 的 ρ=2.73、受扰运动），但 **T04 之前不应做任何控制实验**；
  本次运行没有、也不能证明反馈控制有效。
- 400 s/案、7200 s/套件仍为待验证预算；本次 26.59 s 只覆盖 3.948 s 运输，不能外推。

## 11. 文件与哈希

`smoke_verification.json` 内含全部文件 SHA256；`smoke_manifest.json` 含命令、Git commit、源码与协议 SHA、
限制与结果。关键文件大小：`plant.jsonl.gz` 1.36 MB、`estimator.jsonl.gz` 3.14 MB、
`failure_context_plant.jsonl` 1.81 MB、`failure_context_estimator.jsonl` 0.96 MB。

## 12. 提交

见本轮 commit（smoke 入口与修复、运行产物、本报告）。未修改 `results/`、未触碰 P4。

---

## 附录 A — 溯源口径更正（2026-10-19，T03 审查要求；原日志未改）

| 项 | 原文写法 | 更正 |
|---|---|---|
| 传感器行数 | "sensors 1 897 条观测" | `sensors.jsonl.gz` 实际 **2 048 行 = 150 预标定 + 1 898 运输**（1 892 `fresh_filter_packet` + 6 `initialization_only`） |
| metadata 墙钟 | `metadata.json` 记录 `wall_limit_s=120` | 诊断入口实际为 **60 s**（见 `smoke_manifest.json`）；已在 `run_case` 改为记录真实传入值，旧运行保持原样 |
| 环形缓冲 | "200 个完整行" | ring 存的是 200 条**已发出的行**；1 Hz 降频期间 bulk（W/D/奇异值/estimated_state/solver）本就不在行内，不能称为"200 份完整原始矩阵" |

原始运行目录 `p2/runs/20261019_103729_T01E_SMOKE_case11_exp3_seed7/` 未做任何修改。
