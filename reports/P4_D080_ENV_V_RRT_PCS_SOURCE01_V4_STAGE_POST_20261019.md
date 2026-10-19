# D080 环境 V：RRT+PCS SOURCE01 V4 阶段后审（2026-10-19）

本阶段只记录一次已经授权并完成的真实 source 入口，以及随后对保存前缀的独立审查。没有重启 source、改变 seed/range/goal bias、放宽碰撞/闭链/限位门，也没有启动正式统计。

## 真实执行

- 协议：`configs/p4_d080/v_rrt_pcs_source01_v4.json`，seed=7，range=0.2，goal bias=0.05，单次 solve=10 s，外层 30 s/60 s。
- 真实进程启动 1 次、请求发送 1 次；stdout 保留 `Solved in 0.249101s.`。
- `runtime/paths/path_milestones.txt` 写出 6 个里程点，`temp.txt` 写出 53 个配置；没有 `parsed_source_result.json` 或 `runtime/result.json`。
- 监督器在 trace/回溯阶段触发 `RuntimeError('III_SOURCE_SELF_REAPED_LIVE_GROUP_WORK_CAP')`，随后唯一 source 子进程以 `-9` 清理，stdout/stderr 双 EOF，进程组为空。
- 外部 charged wall/CPU：26.42207942299661 / 25.113139 s；预算门通过，但 source transport 不合格。

证据：

- 执行记录：`results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4/execution.json`
- 原始日志：`results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_V4/evidence.jsonl`、`process0_stdout.bin`、`process0_stderr.bin`
- 失败后独立 POST：`reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_V4_FAILURE_SAVED_INDEPENDENT_POST_20261019.json`（8/8）
- V43 账本：`results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V43.json`

## 保存前缀独立审查

对已有 6 个里程点只读运行独立 FK/闭链残差、分支不变量、限位及 native/aligned 离散碰撞查询。结果为 6/6 节点限位合法、两臂分支均为 `[3]`、native/aligned 碰撞均为 false 且查询码为 0；但 6/6 节点的保存文本精度使闭链位置残差超过严格 `1e-5 mm` 门。首点只在约 `1.06e-6 rad` 的四舍五入误差内接近起点，末点与冻结目标的最大关节差为 `1.3722385939317288 rad`。`temp.txt` 的最后配置对应里程点 4，而不是声明的最后里程点 5；没有达到目标。

因此独立审查状态为 `PASS_PREFIX_AUDIT_REJECTS_COMPLETE_PATH`，不是完整路径成功，也不是连续无碰撞证明。审查本身 charged wall/CPU 为 1.81 / 1.89 s，单独计入 V44；没有 source process、solve、正式统计或 VI 构造新增调用。

证据：

- 原始审查：`results/p4_full/20261019_R2_D080_V_RRT_PCS_SOURCE01_PREFIX_AUDIT/audit.json`
- 独立 POST：`reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_PREFIX_AUDIT_SAVED_INDEPENDENT_POST_20261019.json`（11/11）
- V44 账本：`results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V44.json`

## 科学结论与边界

V 当前仍没有独立合格的端到端 RRT+PCS 路径。stdout 的 `Solved` 只能证明原生入口曾返回求解提示；完整 source transport、目标到达、闭链、分支、限位和碰撞路径门必须同时通过。本次失败根因审查暂定为“我们监督器的 SIGALRM 资源检查重入”，详见 `reports/P4_D080_V_SOURCE01_ROOT_CAUSE_REVIEW_20261019.md`；这不应被写成原论文算法失败。

后续只允许在新版本化监督器通过独立静态审查、重新冻结并获得新的 source 预算后再考虑重试。当前不重复消耗已用完的 source process/solve 额度；可继续推进保留环境的其他已授权 PCS/NR/RSS 工程线。
