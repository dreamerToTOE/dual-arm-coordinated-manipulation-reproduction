# P2 — 原文公式审计与最小闭环协议

Status: AUDIT_COMPLETE / PROTOCOL_DRAFT / STOP_FOR_MODEL_DECISION

## Scientific objective
核对P2的SE(3)软接触、状态估计与联合位姿/内力控制，设计能取得独立物体动力学和接触力曲线的最小实验，不用代数或命令力冒充复现。

## Minimum sufficient evidence
- [x] 8页原文全文与图/表/式(1)–(26)身份及内容核验。
- [x] 作者资源、既有资产及未实现内容核查。
- [x] 原表I/II、真实plant/观测/估计/控制、参考/消融/统计与预算草案。
- [x] 式15/22争议的独立推导、固定诊断和原始输出。
- [ ] 接触运动学科学裁决及之后的有限形变门禁，才可冻结实验协议。

## Explicit non-goals
- P4源码/数据/报告修改、新RSS实验、P3/Isaac/ROS/当前场景适配。
- 本轮实现闭环或伪造实验曲线；将预案写成正式实验完成的Word。
- 修改正式Benchmark或旧TASK07–10场景任务的门限/结果。

## Inputs / frozen dependencies
- P4基线79cc87173e5fad778927d0b4f8b3b0db6e41de7b；P4阶段报告已接受、完整论文部分完成。
- 私有PDF SHA0188b6be…；论文DOI10.1109/LRA.2026.3665445。
- references/P2_pose_force.md、原文审计；旧P2工作树不导入/覆盖。
- configs/p2_closed_loop_protocol_v1_draft.json是待裁决草案，不是正式Benchmark。

## Requirement
公式、模式、坐标、单位、观测与控制目标可追溯；重大接触模型疑点保留证据停止，不默认更正原文。

## Preferred method
原作者完整模型/代码；目前未定位到。使用原质量/尺寸/增益与论文Cartesian软接触/刚体模型的最小候选，滤波优先引用[18]固定作者工具。

## Fallback method
明确标记的速度端点/均质物块/带噪COM观测模型；不能退化为GT主控制、纯hdot曲线或双weld。接触争议修正需用户决定。

## Attempt budget
本轮固定数学诊断1次，控制仿真0次，小幅算法修正0/3。后续预算：首轮30run；最多3轮×7固定诊断；终版最多再一套30，总81，单case120s、总7200s壁钟先触顶先停。

## Stop / escalation conditions
式15正号/有限形变投影争议已触发停止；模型variant=null、executable=false。式22理论限制单独记录，不生成plant曲线。重大模型/算法替换、判据/场景更改、预算耗尽均停止请示；不得自动P3。

## Deferred issue ownership
| Issue | Owner |
|---|---|
| 式15科学裁决、有限形变推导/资格 | P2后续模型任务 |
| 接触/动力学、IESEKF及闭环控制实现 | P2后续实验任务，协议冻结后 |
| 完整装配/低层夹持、摩擦、图像感知 | P2原文缺项，单独扩展 |
| FR3/吸盘/Isaac应用 | 最终差距章节及后续场景阶段 |

## Outputs
- reports/P2_AUDIT_PRE_TASK.md、P2_ORIGINAL_PAPER_AUDIT.md、P2_CLOSED_LOOP_EXPERIMENT_PROTOCOL.md。
- scripts/audit_p2_kinematic_identities.py、results/20261013_P2_original_audit/。
- configs/p2_closed_loop_protocol_v1_draft.json、六份持续记录、本轮保全校验。

## PASS criteria
- [x] 原文审计与协议草案可复核，关键不一致如实保存。
- [ ] 获裁决后，冻结前科学/数值资格全部通过。
- [ ] 真实闭环数据与原文对照尚未执行，不能称P2复现通过。

## Paper fidelity
- [ORIGINAL] 软接触、式16动力学、H/W/零目标内力、式21/25叠加、参数/消融。
- [ADAPTATION] Cartesian端点、均质惯量、抓点/路点、COM观测、多率/标定初始化。
- [ENGINEERING] 事件/日志、协方差冻结和数值资格。
- [DEVIATION] 接触演化修正未授权；完整预抓取IESEKF和原硬件低层未复现。
- [EXPERIMENTAL] 自定固定bias/时延代表例，仅预声明，尚未执行。
