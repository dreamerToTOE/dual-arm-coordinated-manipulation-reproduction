# D081 范围映射最小补记（2026-10-19）

本补记只新增状态索引，不修改 D080 的 211 行 CSV/MD 或任何历史结果。

- D081 已取消 D080 计划的环境 II–V、3 planner×3 method、500 次/单元的 18,000 次正式规划。D080 主表仍保留原 18,000 目标字段；后续状态统一解释为 `CANCELLED_BY_USER_D081_NOT_EXECUTED`，实际完成数保持 0。
- 原论文 22,500 次 Table I 历史义务仍保留；环境 VI 仍为 D080 只读归档，不恢复执行。
- III 649 节点 PCS 端到端资格已完成并独立保存：这是资格/离散 source-policy 路径证书，不计入 Table I 正式统计，也不改变 P4-T18 的取消状态。证据：`reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json`。
- V BUILD01 orphan：保留原失败、无 runtime execution/receipt；事后 saved-only 两观测费用索引单独计费，不能计为构建成功或科学运行。证据：`reports/P4_D080_ENV_V_RRT_PCS_BUILD01_ORPHAN_SAVED_INDEPENDENT_POST_20261018.json`及 recovery cost-only POST。
- V BUILD02 与 SOURCE01：当前仅有版本化工程/入口审查和草案，未把待定状态改为运行通过；其后续 source 资格必须单独记录真实调用与独立 POST。
- D081 后续优先级转为数值仿真：保留 III exact 独立验证、V 最小 source solve、RSS/PCS/NR/RBS/APC 对照及 Fig.3–5/Table II 等非18k数值义务；每个实验记录真实样本数、种子、参数、失败/超时和可比性，不能冒称原文500次统计强度。

建议新增字段（附加表或新 D081 映射表）：`d081_status`、`d081_scope_decision`、`d081_formal_trials_target`、`d081_formal_trials_completed`、`d081_cancel_reason`、`d081_qualification_evidence`、`d081_next_numerical_scope`。对 P4-T18 总行及其 II–V 36 子行：`d081_status=CANCELLED_BY_USER_D081_NOT_EXECUTED`、target=18000（总行）或 500（子行）、completed=0；对 III649 资格另记 `d081_status=QUALIFICATION_COMPLETED_NOT_FORMAL_STATISTICS`；对 V BUILD01 `ENGINEERING_PREFLIGHT_FAILED_COST_ONLY_RECOVERED`；对 V BUILD02/SOURCE01 `PENDING_VERSIONED_ENTRY_NOT_RUN`。

D081 决策文件：`docs/decisions/D081_P4_CANCEL_18000_NUMERICAL_REPRODUCTION_20261018.md`。
原 D080 表 SHA256：`c9599003f3a2369e1f9ce106884ac2ebc5453d1774b185899eb6a397191bd3b7`。
