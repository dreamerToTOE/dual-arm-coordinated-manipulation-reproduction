# 原论文与我们实际复现范围逐项对照表（P1–P5 通用模板）

这是每篇结题时**必须更新后提交给用户的最终表**，不是可以预先填PASS的自评。对应正文、每项原始实验和必要控制器/规划器，逐个使用稳定编号 `P?-T01` 等。表中“原论文章节/图式”必须有可验证的页码/公式/图/表，不得仅使用“原论文结果”作为出处。对应的csv格式字段见下。

论文 / DOI / 原文版本SHA256 / 作者源码固定SHA / 本次科研源码SHA / 冻结协议SHA / 执行机器 / 依赖及许可 / 实际报告版次：**在结题时填实值**。

| ID | 原论文页/章/式/图/表 | 原论文必须复现的方法/算法/试验 | 原论文真实条件、重复与指标 | 我们实际实现模型和实验条件 | 实际真实结果/失败（含分母、单位） | 与原文是否可直接比较 | 结果原始文件、源码SHA及独立核验证据 | 未覆盖/差异/失败根因与归属 | 状态 | 后续处理 |
|---|---|---|---|---|---|---|---|---|---|---|
| P?-T01 | 待核实 | 待核实 | 待核实 | 未执行 | 暂无（不填写零值） | 未能比较 | 无 | 未尝试；待执行 | NOT_ATTEMPTED | 原文义务必须处理 |

## 状态和归因严格定义

- `FULL`：与原文足够同源、所有相关主要算法行为/指标/场景和可比实验均有独立可核验成功证据；不是单位测试合格。
- `RECONSTRUCTED`：原始输入缺失但有透明、符合原文机制的独立重建，其成功只支持适配条件，不支持原硬件精确数值对应。
- `PARTIAL`：已真实实现或运行一部分，但仍缺实验条件/核心机理或关键表现。
- `FAILED`：实际执行并取得有证据的负面结果，注明具体退出条件，不能把没有执行的项记成失败。
- `BLOCKED-PAPER-RESOURCE`：经公开/作者资产审计、重建尝试及归因无法唯一确定必要原始条件，因此目前不能精确复现；必须有证据链接，不能直接写作者方法错。
- `PAPER-ISSUE-SUSPECTED`：原文公式/方法存在可重复独立数学反例或潜在相互矛盾，仍需核对作者实现，不写确定性“论文错误”。
- `NOT_ATTEMPTED`：从未执行，**最终交付不能存在无说明的此项**，需先补实验或合理证据BLOCKED。
- `UNKNOWN`：已诊断但责任和根因尚不能确认，必须给出下一步可否证的取证计划、所需条件及是否申请审批。
- 可在状态后增加细分 `MATH-PASS`、`CONTROLLER-FAILED`，不可代替主状态含义。所有归因至少判 OUR-IMPLEMENTATION / PAPER-REPRODUCIBILITY-LIMITATION / PAPER-METHOD-ISSUE-SUSPECTED / MIXED / UNKNOWN之一，注明证据等级与排除的替代解释。

## CSV 字段

`paper_id,item_id,original_page_section_equation_figure_table,original_requirement,original_model_platform,original_input_asset,original_repeats,original_duration_budget,original_metric,original_claim,source_url_or_sha,ours_model_and_version,ours_parameter_config_sha,ours_run_ids,ours_actual_trials_success_fail_timeout,ours_metric_and_units,comparability,ours_result_and_independent_verification,missing_coverage,root_cause_category,root_cause_confidence,claim_evidence_level,status,next_action,report_section,notes`

## 上报规则

1. Codex在**任何科学实验以前**先完成原文义务表（无需真实数字的位置标NOT_ATTEMPTED），逐图/表/公式/子实验审查，报告源文件是作者accepted或发表版；有附录则同样展开。
2. 执行期间每次run及根因审查实时更新表，不删除记录项、失败、样本和更早源码SHA；如新增原文义务用新的稳定item_id追加。
3. 完成每篇论文后，将最终Markdown、CSV和真实Word/PDF提交GitHub并**在消息中向用户实际展示关键覆盖对照表及链接**；明确 FULL/PARTIAL/BLOCKED，不允许用“组件通过率”冒充科研全文成功。
4. 报告最后一章必须含双FR3 Benchmark A/B迁移分析：具体可借鉴算法/原理、真实证据等级、接口、模型/接触与观测必要条件、风险、建议对照实验，并在全部五篇原文复现完成前不启动Isaac集成。
