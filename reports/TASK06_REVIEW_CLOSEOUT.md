# TASK06 — 分项审查收尾（仅文档）

日期：2026-10-12。基线：`74d4276b8d86d972010d32cbc8f9690a40208ac6`。
工作分支：`task06-p4-constrained-rrtconnect`。审查决定：D054。
本记录不修改或取代 [原始交付报告](TASK06_CONSTRAINED_RRTCONNECT01.md)。

## 审查结论

| 验收范围 | 用户审查决定 | 边界 |
|---|---|---|
| TASK06 核心离线规划器软件实现 | PASS CANDIDATE | 真实双树约束搜索、复用 NR/RBS/FCL、确定性与软件接口；仅离线范围 |
| TASK06 整体及原 D052 协议 | PARTIAL | 未证明障碍场景直接 TASK05 连接因 COLLISION 被拒绝 |

该决定是明确的分项验收，不是原实验改判、门限放宽、完整 P4 复现、
连续扫掠安全或物理执行成功。Benchmark 仍 DRAFT / NOT FROZEN；TASK02
IN_PROGRESS，TASK02-D PARTIAL / DEFERRED。不自动进入 TASK07。

## 保留的原始证据

- 全部 18 次固定种子规划结果，9 对确定性重复；14 次 SUCCESS、4 次 NODE_LIMIT。
- 独立障碍场景种子 `20261012` 的两次成功案例：553 节点、148 条解路径边、
  2261 个离散路径点。其他两种子各两次达到原 600 节点预算。
- 直接连接仍为 PROJECTION_JUMP：失败点 index2/depth1，NR CONVERGED，
  修正 L2 为 `0.08694933778810582 rad`，原守卫 `0.020 rad` 不变。
  **被拒绝的中点 collision=null，未执行该点 FCL 查询**；不能推断其碰撞判决，
  也不将此前已经检查的端点表述为未检查。
- 原 suite 状态 PARTIAL、typed result FAILURE、原指标、原参数、编译负例、
  四次预算失败及所有 TASK03–05 负面证据保持原样。
- 原 TASK03 历史精度 FAIL（最大 0.435028 μm 超过原 0.05 μm）不改判。

原始证据入口：[metrics](../results/20261012_TASK06_constrained_search02/planning_metrics.json)、
[metadata / artifact hashes](../results/20261012_TASK06_constrained_search02/metadata.json)、
[result](../results/20261012_TASK06_constrained_search02/result.json)、
[9 对重复指纹](../results/20261012_TASK06_constrained_search02/deterministic_fingerprints.json)、
[直接连接原始证据](../results/20261012_TASK06_constrained_search02/direct_obstacle.json.gz)。
旧证据位置与字节未重写，新的审查结论只写入文档。

## 独立 P4 评估待办

`P4-EVAL-OBSTACLE-DIRECT-COLLISION = DEFERRED / TODO / NOT AUTHORIZED`。
后续如获单独授权，应先声明独立评估协议，再验证直接连接的碰撞拒绝和障碍绕行；
不追溯性地将 D052 判为 PASS，不覆盖原结果。本轮不设计新障碍、修改投影参数、
实现新算法或执行任何评估实验；此待办不构成 TASK07 的启动许可。

## PRE-TASK REPORT

- Task：TASK06 分项审查文档收尾。
- Scientific objective：分别记录软件验收和原协议证据资格，不新增科学结论。
- Minimum sufficient evidence：用户明确审查决定、原始证据保留、仅文档 diff。
- Current scope：D054、STATUS、任务卡、反馈/工作记录、阅读入口及本独立审查记录。
- Explicit non-goals：代码、几何、ACM、模型、参数、Benchmark、新规划/物理实验、TASK07。
- Attempt budget：一次文档更新；实验预算零。
- Preferred method：附加审查记录，原交付报告和原始结果不动。
- Fallback：上传失败则保留本地提交并报告，不扩展工程范围。
- Stop / escalation：范围外改动或证据不一致即停；提交后停止。
- Validation plan：只读 SHA256、已保存结果计数、文档链接和 Git diff 检查。
- Known risks：核心 PASS CANDIDATE 不等于整体/原协议 PASS。
- Need user confirmation：no，用户已明确批准文档范围。

PRIOR-ASSET CHECK：本轮不是新算法或替代基础设施实现；不移植成熟工程模块。
仅引用已审计的 TASK06 原始产物与旧 TASK03–05 证据；原复用审计、固定来源与数学
实现保持不变。无新 DIRECT_PORT / THIN_ADAPTER，无新增理论或模型。

## POST-TASK REPORT

- Task：TASK06 审查收尾；Status：核心软件 PASS CANDIDATE、整体 PARTIAL。
- Scientific objective / minimum sufficient evidence：分项审查已记录；文档范围满足，
  不新增或宣称满足原协议的直接碰撞验收。
- Completed / files changed：DECISIONS(D054)、STATUS、TASK06 任务卡、BUGS、
  USER_FEEDBACK、WORKLOG、EXPERIMENT_LOG（明确 NO NEW EXPERIMENT），README、
  CODEX_START_HERE、P4 模块 README、本审查记录。
- Commands / validation：只读 Git 状态/差异、文档读取、本地证据 SHA256 与计数、
  Markdown 链接检查、文档 diff whitespace 检查、明确路径 git add/commit/push。
  **未运行编译、回归、规划、IK、FCL、ROS 服务、Isaac 或控制器。**
- Tests / results / key metrics：40 个既有 artifact、35 个源码/网格 SHA256 全部匹配；
  Git diff 确认结果、配置、代码及原交付报告不变，仅 Markdown 文档更新；只读确认
  18 次结果、9 对重复、4 次 NODE_LIMIT、两次 553 节点/148 边成功和原 PARTIAL。
  这是证据保留检查，不是新实验或新增确定性规划复测。
- Blockers：原协议直接-COLLISION 缺口仍未解决；独立 P4 评估 DEFERRED。
  离散安全/无原生距离、继承的局部守卫为 KNOWN LIMITATION；原 Task26 为 LEGACY。
  TASK02-D 原生时间/reset 资格继续 DEFERRED。
- Attempt budget used：文档更新 1 次；新实验 0。无需新增工程修复/重试。
- Paper fidelity：本轮仅 [ENGINEERING] 审查与溯源记录；[ORIGINAL]/[ADAPTATION]
  方法不变，[DEVIATION]/[EXPERIMENTAL] 不新增、不隐去旧记录。
- Records updated：上述六项持续记录及任务卡、阅读入口已更新，历史条目保留。
- Open risks / recommended next step：等待单独审查与授权；不把原协议改判 PASS，
  不自动进入独立评估、TASK07 或运行时实验。
- Git branch / commit / dirty files：同 task06 分支，提交为本基线之后的文档提交；
  原有五个无关未跟踪 TASK01 日志不删除、不提交。新的 GitHub SHA 随交付报告。

**记录完成后停止。**
