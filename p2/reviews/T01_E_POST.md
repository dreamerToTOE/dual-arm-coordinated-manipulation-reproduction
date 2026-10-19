# P2 T01-E POST — O1/O2 工程优化执行结果

**状态**：`COMPLETE (engineering equivalence)`；**不是**端到端性能验证，也不是任何科学结论。
所有 444 个黄金数组逐位一致；未运行 95 s 案例、未跑闭环、未改数学传播格式、未动 seed、未触碰 P4。

- 分支 `reproduce-p2-numerical-simulation-20261018`，起点 `14baf241`
- 本轮诊断总墙钟 **< 20 s**（预算 150 s：等价性 ≤120 s、微基准 ≤15 s、日志 ≤10 s、其他 ≤5 s）
- 冻结基线 `p2/reviews/t01e_baseline/` 未被修改（`arrays.npz` SHA 不变）

---

## 1. 结论摘要

| 项 | 结果 |
|---|---|
| 比较器 | 已改为 fail-closed；11 个负例全部 FAIL 且退出码 1，正对照 PASS 退出码 0 |
| O1-a 去重复校验 | 通过，**444/444 位相同** |
| O1-b 缓存选择矩阵 | 通过，**444/444 位相同** |
| O1-c copy/retract 免重复 SE(3) 校验 | 通过，**444/444 位相同** |
| O1-d 替换 `se3_log` | **放弃**：随机姿态 1.2e-10、近 π 2.8e-6，超 1e-12 判据；scipy 保留 |
| O2 日志 | 事件流无损、bulk 快照 1 Hz + 异常触发、环形缓冲 200；载荷 −23%，写入 −13% |
| 最终 444 数组 | `t01e_final_compare.json`：`PASS`，`bitwise 444/444`，`failures 0`，退出码 0 |
| 异常夹具 | 9 个非法输入仍以相同异常类型与**逐字相同**消息被拒绝 |

## 2. 比较器修复与对抗测试（先决门）

修复点（`p2/tools/t01e_compare.py`）：

1. 候选缺失/多余数组、缺失 case → 计入 `failed`；此前只记录不判负。
2. **退出码**：仅 `PASS` 返回 0，其余返回 1。
3. 严格项比较 **dtype + shape + 原始字节**（`view(np.uint8)`），覆盖符号零与 NaN payload；
   移除 `np.array_equal(equal_nan=True)`。
4. 合法数值夹具中出现任何 NaN/Inf → `NONFINITE_VALUES` 失败，不掩盖。
5. 分类改为**冻结的后缀表**（44 项），未知后缀 `UNCLASSIFIED_KEY` 直接失败；取消子串匹配。
   `--mode o1d` 才启用的容差表显式列在代码中，并在输出里标注。
6. 相对误差 `|a−b|/max(|a|,|b|)`，仅在 `max(|a|,|b|) ≥ 1e-12` 时有意义；不再用常数 1 归一化。

负例测试（`p2/tools/t01e_compare_tests.py` → `t01e_compare_negative.json`）：

| 用例 | 断言 | 结果 |
|---|---|---|
| 正对照（未改动副本） | PASS / rc=0 | 通过 |
| 删除数组 | MISSING_IN_CANDIDATE / rc=1 | 通过 |
| 增加数组 | EXTRA_IN_CANDIDATE / rc=1 | 通过 |
| 改一个元素 1e-3 | BITWISE_MISMATCH / rc=1 | 通过 |
| 改 1 ulp | BITWISE_MISMATCH / rc=1 | 通过 |
| dtype float64→float32 | DTYPE_OR_SHAPE_MISMATCH / rc=1 | 通过 |
| `+0.0 → −0.0` | BITWISE_MISMATCH / rc=1 | 通过 |
| 写入 NaN | NONFINITE_VALUES / rc=1 | 通过 |
| 改 shape | DTYPE_OR_SHAPE_MISMATCH / rc=1 | 通过 |
| 改迭代次数 | METADATA_MISMATCH / rc=1 | 通过 |
| 改异常消息 | METADATA_MISMATCH / rc=1 | 通过 |
| 增加虚构 case | MISSING_CASE / rc=1 | 通过 |

两次独立生成基线：`444/444` 位相同、退出码 0（`t01e_baseline/selfcheck.json`）。

## 3. O1 逐项

### O1-a 去内部重复 SE(3) 校验 —— 通过

新增私有 `_exp6/_log4/_inv4/_adj4`，只在"入参已在入口校验过"的调用链内使用：
`grasp_rate`、`FilterState.retract/local`、估计器的几何/观测/预测/残差路径。
公共 API 全部保留校验：`se3_exp`（入参与出参）、`se3_log`、`inverse`、`adjoint`、
`FilterState`/`Observation` 构造、`_check_packet`。

证据：`t01e_o1a_compare.json` — 444/444 位相同、0 元数据差异、退出码 0。

### O1-b 缓存不可变常量 —— 通过

`selection()` 三种标准模式返回同一个只读数组，未知模式仍抛 `GeometryDomainError`。
核对调用方（`grasp_rate`、`mechanics`、`estimator._null`、`control`、`clocking`）均只读。

证据：`t01e_o1b_compare.json` — 444/444 位相同。更新路径无可测收益（该函数不在迭代内），保留仅为去分配。

### O1-c copy/retract 免重复校验 —— 通过

`FilterState._from_validated`：`copy()` 与 `retract()` 的输入块已知合法（已校验状态 + 有限增量），
用一次向量化有限性检查替代 7 次 SE(3) 重校验。公共构造仍全量校验；`retract` 仍通过 `_vector` 拒绝非有限增量。

证据：`t01e_o1c_compare.json` — 444/444 位相同。

### O1-d 替换 `se3_log` —— **放弃**

单独探针（未改估计器）对 3000 随机姿态、1e-12…1e-4 小角、π−1e-8…π−1e-3 近 π、
坐标轴恰好 π、单位阵、带平移的完整 SE(3) Log 做了对照：

| 用例 | 最大绝对误差 | 判定 |
|---|---:|---|
| random_3000 | **1.16e-10** | 超 1e-12 |
| near_pi | **2.80e-6** | 超 1e-12 |
| small_angle | 1.7e-21 | 通过 |
| exact_pi_axes | 0 | 通过 |
| se3_log_full_pose | 2.8e-17 | 通过 |

近 π 的 `acos` 条件数 + `(R+I)/2` 开方是主要误差源。按预登记判据**放弃 O1-d**，scipy 保留；
`se3_exp` 与其他坐标函数未做任何替换。证据：`t01e_o1d_probe.json`。

## 4. O2 日志

新增 `scripts/p2_event_log.py`，并接入 `run_p2_closed_loop.py` 的 plant / estimator 流：

- **无损事件流**：类型、`time_s`、`tick`、收敛/迭代、连续不收敛计数、创新前后、观测样本 id、
  域门/终止原因、逐样本 `h_N_Nm`/`hK`/`hB`/`internal`（半步门与指标提取需要）——每行都在。
- **仅降频大载荷**：`W`、`D`、奇异值、`estimated_state`、`solver` 诊断 → 1 Hz + 异常触发。
- **异常上下文**：200 事件环形缓冲，异常时在 `finally` 前落盘 `failure_context_*.jsonl`。
- 计数器 `events = snapshots + suppressed`。

同一 600 事件（250 Hz，含 1 个异常事件）流 A/B：

| 指标 | legacy | policy |
|---|---:|---:|
| 事件数 / 顺序 / 时间戳 / 摘要 | 600 | 600，全部一致 |
| bulk 快照数 | 600 | 3（首个 + 1 s 边界 + 异常） |
| 压缩后字节 | 24 239 | 18 600（−23.3%） |
| 写入耗时（600 行） | 31.4 ms | 27.2 ms（−13.4%） |

证据：`t01e_log_compare.json`。**runner 集成只做了导入检查，没有跑闭环**，端到端日志逐行 diff 待批。

## 5. 性能（同一夹具、同一方法；中位数）

| 项 | 优化前（T01_COST_PROBE） | 优化后（本轮） | 变化 |
|---|---:|---:|---:|
| 预测 4 ms（有界先验） | 3.368 ms | **1.163 ms** | −65.5%（2.90×） |
| 更新 3 观测包 | 32.10 ms | **13.66 ms** | −57.5%（2.35×） |
| `se3_log` 公共调用 | — | 0.148 ms | — |
| `se3_log` 内部（`_log4`） | — | **0.060 ms** | 比公共版快 2.5× |
| `mechanics` 单次 | — | 1.84 ms | 未优化（不在估计器热路径） |
| 日志写入 | 见 §4 | −13.4% | — |

**不声明端到端**：按组件成本线性外推，95 s 案约 350–420 s（原 556–826 s），
但**没有实测**，且不构成 400 s 预算成立的证据。95 s 案例与 30 案套件仍需单独批准。

## 6. 未验证 / 不声明

- 未运行任何闭环、95 s 案例、30 案套件；未测端到端墙钟。
- O2 的 runner 集成只通过 `py_compile` 与模块导入；未跑出真实日志做逐行对比。
- 未验证长时间积分后的数值行为（属 T03/T04）。
- 未声明 IESEKF 已稳定；传播格式未改（仍为 `PAPER_LITERAL_EULER`）。
- 未做论文 Fig.6–9 的任何对标。

## 7. 风险

1. `_from_validated` 依赖"输入块已合法"这一前提；公共构造仍全量校验，但若未来有人用 `retract` 传入
   非有限增量以外的问题（如极端幅值导致 `Exp` 溢出），只剩有限性检查兜底。建议 T04 在闭环前加一次
   端到端域门（已有 `PAD_DOMAIN_INVALID`）。
2. O1-b 的只读数组若被未来代码原地修改会抛错（比静默污染好，但需知晓）。
3. O2 的降频只覆盖 `BULK_KEYS`；新增字段若体积大且未登记，会继续全量写入。
4. 性能数字同机同法，但机器负载波动可达 2×（更新 12.6–25.5 ms），只能作相对比较。

## 8. 是否具备进入 T03 的条件

**具备（工程层面）**：

- 数学实现与优化前逐位一致（444/444），异常行为逐字一致；
- 优化集中在校验/分配，未触碰数值格式、迭代次数、时序、域门；
- 基线 oracle 与比较器可复跑，A/B 结果可审计。

**但** T03 仍需单独 PRE；并且端到端性能（400 s/案是否成立）必须在获得批准的短基准或单案运行中验证，
不能引用本报告的外推值。建议 T03 之前补一次**获批的**短闭环 smoke（1–5 s 仿真）同时验证：O2 日志集成、
优化后更新耗时在真实事件流下的表现、以及快模态下的收敛行为。

## 9. 提交清单（可逐项回退）

| SHA | 内容 |
|---|---|
| `9fb38aac` | 比较器 fail-closed + 11 负例 |
| `eb1b3d9d` | O1-a 去重复 SE(3) 校验 |
| `30f8a008` | O1-b 缓存选择矩阵 |
| `633553e6` | O1-c copy/retract 免重复校验 |
| `bd25ddce` | O1-d 探针与放弃 |
| `67d7825c` | O2 事件日志 + runner 集成 |

## 10. 待裁决

1. 是否接受 O1-d 放弃（scipy 保留）。
2. 是否批准一次**短闭环 smoke**（1–5 s 仿真，`<= 60 s` 墙钟）来验证 O2 集成与真实事件流下的更新耗时。
3. 400 s/案与 7200 s/套件仍为待验证预算，是否维持。
