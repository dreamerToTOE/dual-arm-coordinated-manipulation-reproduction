# P4 R2：旧 II/III/V RSS 固定候选碰撞补检 PRE-TASK / PRIOR-ASSET

2026-10-15。状态：**准备与静态审查，尚未运行本阶段科学查询**。接续 D079 与既有 R2 3600 秒墙钟 / 7200 秒 CPU 总预算；本阶段不使用 VI 用户 B 的候选构造子预算。旧记录、旧失败与原始输入全部原字节保留。

## PRE-TASK REPORT

- **Task / Scientific objective**：仅为 `20261015_R2_RSS_CONSTRUCTION01` 已保存的 II 18、III 22、V 8 个闭链/真奇异秩/原关节界合格分支，补真实原离散 source-policy 碰撞资格。判明这些旧候选哪些碰撞、哪些仅通过指定源策略；不重新选择样本。
- **Minimum sufficient evidence**：完整冻结 48 项，按环境 II→III→V、各原 observations 数组下标升序；保留 `source_index/mode/branch/native_active_ik.input_line` 与原 12 角逐值副本。每项最多一次逻辑 adapter 调用，保留 native/aligned 两查询全部 stdout、PQP 返回码、pair 数、TCP 对照、耗时及通过/碰撞/UNKNOWN。未运行的尾项明确列出。
- **Current scope**：II 的 300 固定被动目标/2400 分支中原已合格 18 分支，III 的 300/2400 中 22，V 原 wrist-only 100/800 中 8；分支不是独立新采样。旧 700 目标/5600 IK 均不重做。原来源为 R1 保存 FK 样本与 R2 数值一致独立重建，非原作者原生完整 RSS 分布试验。
- **Explicit non-goals**：不改变原角值、周期代表、原排序、模式、种子、门限、几何、网格/pair/8mm tolerance；0 新 IK/NR/RNG/规划、0 新候选构造。无新 RBS、regular↔singular 桥、连续碰撞或完整 RSS 成功结论；不修复旧 mode0 失败，不把本批结果外推到 I/IV/VI。
- **Attempt budget**：单次不可重置 claim；最多 48 逻辑 collision adapter 调用、96 native/aligned 查询、30 秒墙钟 / 60 秒 CPU。实际时间计 R2 总账一次，VI B 额度不扣。每 candidate 的 adapter 内部 TCP 对照为 2 variant×2 arm=4 次独立 FK/J，全部完成为 **192 次内部 FK/J**；不声称总新 FK=0。没有额外重跑原运动学资格。
- **Preferred method**：薄 runner 复用已有 `collision_adapter`、原 qualified v3 manifest 和已有有界子进程证据接口；候选只读取旧文件，原资格只读取保存残差/秩/限位字段。每个 adapter 进程保留输入/stdout/stderr，预算到时终止整个进程组并保留前缀。
- **Fallback method**：无重试、无替代样本或备用碰撞模型。来源或 TCP 矛盾/查询错误时保存 UNKNOWN 前缀，进入有证据根因审查。
- **Stop / escalation**：来源/协议/ledger SHA 不匹配、原48条资格/数组/排序变化、非有限输入、返回 variant/pose/query 格式不符、非零 PQP 错误码、选定 aligned TCP 与独立 FK 不符、超预算均停；普通真实碰撞为候选拒绝，继续冻结其余项。native 物理基座偏差如实保留，不伪称 native 通过；aligned 选定门不变。
- **Files expected to change**：新增本 PRE、`scripts/qualify_p4_full_r2_saved_rss_collision.py`、`configs/p4_full/r2_saved_rss_collision_qualification_v1.json`；独立审查/冻结后才允许新增唯一 run 目录与 claim。当前不提交、不执行。
- **Validation plan**：静态编译、`--describe-protocol`/`--validate-draft`；独立比对48数组及完整来源hash、48/96/192计数与预算；执行前须 committed/frozen=true；执行后独立只读归约、原文件hash前后相等、更新对照与六份状态记录。静态检查不调用 FK/IK/碰撞。
- **Known ambiguities / risks**：source-policy 与完整实体碰撞不同；源代码碰撞/界/EE 控制流各异；原作者源实现、R2数值一致重建、aligned 工程修正分别标识。native 与 aligned 可不同，均完整记录，不能将 aligned 结果写成原生作者运行。
- **Need user confirmation**：no。本阶段属于已授权 R2 资格补齐，使用既有总预算；父任务独立复核、冻结并单次运行，不自动授权正式规划。

## 源碰撞、限位与 EE 差异的静态证据

1. `CKCplanning/.../StateValidityCheckerRSS.cpp:258–307` 的 `sampleSingular` 原三模式、随机选根、`identify_state_ik` 后调用实际 `collision_state`；该分支未显式调用 `check_angle_limits`。普通 `sample_q` :216/:245 使用 `collision && !check_angle_limits` 的合取；本次保留旧已通过原界的候选并另测碰撞，**不是执行该原控制流**。R2 mode0/2 使用有证据的真实肘部降秩角，原作者固定约 -π/2 的源码与重建应区分。
2. `ckcComau_industrialScene/.../StateValidityCheckerRSS.cpp:260–308` 实际 `sMode=1`（`rand()%3` 被注释），singular 分支要求 `!collision_state && checkEE`，未显式单独调用 `check_angle_limits`。普通 `sample_q` :217/:250 是 collision/界/EE 的析取拒绝。`checkEE` :368–380 要求两个原 FK TCP 高度均 ≥10mm。**本批只补碰撞，EE 另列保存位姿诊断/未执行原 checkEE，不得称完整源 RSS 状态合格**。
3. v3 manifest 中 ABB native/aligned 沿用 v2 二进制；aligned 仅将 arm2 基座 yaw/translation 与已资格 APC 物理坐标对齐。V v3 是已有 TCP 观测修复；原原生网格/pair/tolerance 保留，aligned 仅将 arm2 世界平移与原 APC 对齐。不得把观测修复误写成作者碰撞算法修复。
4. 实际源网格 pair 与 8mm PQP tolerance 不增删。ABB 原 `setP` 保留共线 rod 三角形；源策略 clear 不代表 rod 实体面、遗漏 pair 或连续路径 clear。完整返回原 query_codes 与 source_stdout，而非用注释推测已运行。

## PRIOR-ASSET CHECK

- **Current task**：48 个旧数学合格 RSS 分支的碰撞续验薄适配。
- **Scientific algorithm that must remain paper-derived**：不新增科学采样/求解/规划算法；原 RSS 模式、几何、闭链与 source 碰撞规则有独立来源。既有 R2 数值修复继续标 RECONSTRUCTED。
- **Old repository areas searched / pinned source**：已读 `docs/POST_TASK01_REUSE_MAP.md`、`docs/PRIOR_PROJECT_REUSE.md`；只读 `dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a:ros_ws/src/fr3_dual_palletize/src/task16_planning_benchmark.cpp` 的候选/试验记录结构。没有启动或更改旧工程。
- **DIRECT_PORT**：无须迁移新实现。
- **THIN_ADAPTER**：直接复用本仓已有 `collision_adapter.py` 与 v3 manifest；复用已验证 `qualify_p4_full_r2_vi_rss_reconstructed.py` 的 RunBudget/Evidence 进程组、原输入/stdout/stderr与独立总账模式；新 runner 仅选择冻结旧记录和归约结果。
- **TEST_ORACLE**：原 RSS observations/checks/summary、R1 原输入、原协议/源码/binary/hash、现有 collision controls 为只读来源与资格证据；原失败不修改。
- **REFERENCE_ONLY**：旧 Task16 候选日志设计、FR3/MoveIt/FCL/Isaac 几何与执行器；不能用其 clear 代替论文 ABB/Comau 原网格策略。
- **Rejected old assets and reason**：旧吸盘/装配/FR3 模型、运动规划器和 ROS 执行链会污染论文机器人与源碰撞条件，本阶段不导入。
- **Files reused/adapted**：现有 Evidence/RunBudget、collision_adapter、v3 manifest，以及旧48候选所在全部输入/输出/过程日志；不修改这些文件。
- **Files newly implemented**：上述薄 runner、frozen=false 配置和本 PRE。
- **Risk of contaminating paper fidelity**：源 collision、aligned collision、原界、EE、数学资格分别报告；本组通过不升级原 RSS sampler、RBS、连续碰撞或全文状态。
- **Need user decision**：no；若后续要新增算法、改变界/EE/碰撞规则或扩大正式规划资源，另行冻结提案与审查。
