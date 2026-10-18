# P2本轮最终审查摘要：动力学通过，完整闭环估计资格停止

2026-10-14；分支reproduce-p2-paper-audit；本轮输入eb2600a，数值资格续行输入4276ce5。P2完整论文仍**部分完成**。

## 实际结果

1. 用户批准implicit plant和仅native连续Jacobian的五点oracle版本化。source45a547c的[N/D70/70](../results/20261014_P2_implicit_qualification_v3_01/summary.json)通过：36原有限输入backend、18 A/C力学模式组合、6 Jacobian、1独立canonical residual、6真实五秒积分、3粗/半步比较。真实A/高moment/C均完成5s，无解析重置或延长。保留v2两点原FAIL。
2. [观测/42维IESEKF/原控制35/35](../results/20261014_P2_components_qualification01/summary.json)、[因果时序2/2](../results/20261014_P2_clock_qualification01/summary.json)通过。组件证据不等于完整控制响应。
3. 实际完整闭环source513c36a，[原ID11 exp3/seed7](../results/20261014_P2_closed_loop_suite02/case_11_exp3_7/summary.json)在t=3.948s停止：ESTIMATOR_MODEL_PAD_DOMAIN_INVALID。987个250Hz运输样本到3.944s；1619次预测、829次更新；case wall24.939s，GT控制state读取0。完整真实plant、观测、P记录、命令、events、最后accepted state和完整失败滤波矩阵保存。
4. 真实pad仍在域内；末态估计tau-x分别−0.00642450658m/+0.00520706318m，越过原±.005m；估计角速度范数260.02053293rad/s，真角速度8.09901e−8rad/s。估计位置误差.000146910993m、角误差.1184859123rad。最后3ms预测无新测量，保存F谱半径5.54745；P有限、数值最小eig约5.59e−14/不对称0，未因负P停止。829更新中3次不收敛，最大连续1次，亦非连续3次停门。
5. 尚未到7s内力和13s位姿反馈事件；UF/UP实际均0，只有原0–3s手动lift。不能宣称联合反馈已有效或失效。实际两侧内力峰约.00202018N、内力矩峰约2.89285e−6Nm，来自真实接触，未作为原1.5N/80%的改进证据。
6. [30case账目](../results/20261014_P2_closed_loop_suite02/case_ledger.json)：主1条失败/19未执行，其他10未执行，95s窗口和完整半步都未取得，RMS为null；不将未运行记控制失败，不把前缀改成新的评分窗口。

## 科学解释与停止

直接停因是估计模型域越界，非真实物体动力学不稳。原观察器Eq18仍Euler，未由implicit plant批准自动改预测。保存单步F/估计速度与刚性模型数值风险相符，但无更换预测消融，不能唯一归因于Euler；有偏固定C、均质惯量、有限接触/阻尼近似及作者未公开细节都须保持区分。不能据本适配失败断言原作者论文或真实机器人结果无效。

累计小修**3/3，剩0**。修正2是诊断JSON归档索引；修正3是入口relative/absolute路径（首次启动case0）。来源前后、原始运行和影响分别见[修正2](P2_IMPLEMENTATION_CORRECTION02.md)/[修正3](P2_IMPLEMENTATION_CORRECTION03.md)。最终不追加第四轮、不改gain/R/Q/质量/惯量/clock/退出门、不重置或强制进入95s。若继续取得原联合控制响应，必须先另行审查/裁决观察器数值解释；本轮已按第7/9节停门保存收尾。

## Word与保全

[中文Word](第二篇P2物体位姿与内部作用力控制论文复现汇总_闭环资格审查.docx)、[17页PDF](第二篇P2物体位姿与内部作用力控制论文复现汇总_闭环资格审查.pdf)：第一部分原接触/动力学/42维估计/原控制及批准几何差异；第二部分真实六条动力学、实际估计/内力/命令、四组未取得指标与原文限定；最后独立FR3应用差距。只读日志绘图，不把估计速度当真实转速。

[保全/因果审计](../results/20261014_P2_closed_loop_delivery_audit01/preservation_and_causality.json)通过：P4保护1023、旧P2八文件、4276ce5前171个P2科学/失败/报告保持；1898个transport观测唯一且恰消费一次，sample/update/delivery戳一致；source/params/log SHA及未执行账目一致。P4工作树79cc871干净。全部旧Word及失败保留，私有原PDF不上传。不启Isaac/P3/P4/RSS/FR3改进。

## POST-TASK REPORT

- Status：PARTIAL/BLOCKED；最小完整联合控制证据未达到。
- 已建立：原力/动力学数值资格，原42维估计/控制数学组件，因果多率调度及首条真实观测控制前缀。
- 未建立：7–95s有效反馈、完整半步、五seed四组对比、原文描述性实验结果。
- Blocker：TASK-BLOCKING完整估计状态域失效；不得以GT或换预测器隐式兜底。有限阻尼/软接触/摩擦、COM视觉及理想端点为KNOWN LIMITATION；FR3应用为DEFERRED；旧平台为LEGACY。
- Attempt budget：3/3已用；无第四轮。原首套30/120s/7200s不扩大；仅实际1名额。
- [ORIGINAL]：Eq9–12/16/17/18/19–21/25及原参数；[ADAPTATION]：冻结的均质惯性/COM观测/Cartesian端点/静态标定；[DEVIATION]：已批G及implicit plant；[ENGINEERING]：等价C++/AD及已批FD5资格；[EXPERIMENTAL]：70/35/2组件和真实失败ID11，各层分栏。
- 六记录：STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK更新D076。

## ENGINEERING ESCALATION

Scientific question：原模型/观测和冻结条件下，能否由估计状态实现位姿/内力联合控制？
What is established：独立动力学与组件资格通过，首条真实闭环3.948s出现估计域失效。
What remains unknown：原作者实际预测离散细节/惯量和本适配误差对闭环的作用；未取得7–95s反馈结果。
Why it matters：不能跨过估计资格或用GT补齐论文实验。
Attempts made：原显式失败保留；批准implicit和FD5资格；累计小修3/3；无第四轮。
Root blocker classification：TASK-BLOCKING。
Is it still task-critical：yes。
Lower-cost evidence available：仅审查原式18、作者框架和保存F/P/创新，不修改代码、不新增实验。
Recommended action：保留当前部分完成交付；进一步预测解释研究另行明确范围，不重开本轮预算。
Need user decision：是否接受当前交付，或另行限定纯数学/作者实现审查；不自动进入P3。
