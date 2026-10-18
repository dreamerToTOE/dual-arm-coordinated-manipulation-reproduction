# P2 独立动力学、估计与联合控制实施前记录

2026-10-14；分支 reproduce-p2-paper-audit；输入基线834bcc372717a3b4ffbd0bd6ef7262b3b58237bf。

## PRE-TASK REPORT

- 科学目标：在已批准接触演化下，由独立物体动力学产生运动与真实接触力，再验证42维右扰动IESEKF及式19–21/25联合控制的四组对照。
- 最小证据：按顺序通过独立动力学、观测/滤波、控制/时序、全动力学半步资格，才能取得冻结20主试验与对应原始曲线。任何失败均保存，停止门不得用重置或调参绕过。
- 输入：已逐项读取六份指定资料（含八页私有原文）；68/68几何资格与冻结JSON沿用，文件SHA不变。原文式15/22与已批准修订的差异完整保留。
- 本轮授权：用户明确启动第二阶段，覆盖历史文档的“下一阶段尚未授权”。不改冻结文件内的历史授权标记；另以本记录记载新授权。
- 范围：独立COM刚体、原接触力、理想Cartesian端点、模拟观测、42维IESEKF、原联合控制、已登记实验、日志绘图、中文Word及GitHub交付。
- 非目标：P4/RSS新实验、P3、Isaac、FR3/吸盘/车厢控制改进、物理抓力/摩擦释放、真实机器人关节控制。
- 方法：式16耦合Lie中点动力学；原式9–12力模型；不变的contact_geometry.grasp_rate；观测与已发布历史命令驱动独立右扰动IESEKF；原式20/21/25相加后H选择。
- 降级：资格失败时保存实际数据并报告部分完成，不替换模型/算法、不把GT诊断混入正式结果。
- 预算：P2累计小修1/3，剩余2；首套30控制run，未来最多74且保留原81天花板；120秒/case、7200秒整体；数值资格不当作主控制试验。
- 停点：固定五秒settle不合格、步长/滤波/切换等协议门失效、重大力模型/控制/协议改变需要停止。具体程序错误仅凭证据修正并保留前后版本。
- 验证：资格输入和阈值在首跑前写入P2_STAGE2_QUALIFICATION_SPEC；冻结参数/几何/历史SHA复核；正式controller不接受plant引用；所有统计从保存日志重读。
- 风险：原Rbar阻尼并不构成有限变形客观耗散模型；低抓力卸载不在模型内；异步滤波与采样可能使闭环失效。不得据数学资格宣称完整控制复现成功。
- 确认：新用户任务已明确授权本范围，不再请求重复批准。

## PRIOR-ASSET CHECK

- 旧工程来源：POST_TASK01_REUSE_MAP已核对，工程库side-suction-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a；本仓库common/logging/run.py、common/metrics/math.py和既有P4 Word/图表脚本已实际读取。
- DIRECT_PORT：不迁移旧机械臂/控制器。
- THIN_ADAPTER：common logger的独占run、原子JSON、逐条原始记录、失败留证据；已有Noto中文绘图、Word原生OMML构造和文档预览模式。
- TEST_ORACLE：已验收contact_geometry纯函数及原68case；旧P2未提交数学资产仅保全、不作为新控制复现证据。
- REFERENCE_ONLY：旧shared_object_executor、Task14/16记录模式；FR3原生StateRecord具有机器人平台语义，不能给独立ODE模拟器冒用“原生测量”标签。
- 拒绝：ROS/MoveIt/Isaac/吸盘执行、旧GT派发、解析力衰减作实验轨迹。它们会改变模型或混淆观测来源。
- 新实现：mechanics、sensor/clock、IESEKF、controller和qualification/runner；均是P2明确科学缺项而非重复开发机器人平台。
- 偏差风险：所有Cartesian、COM观测、均质惯性、静态标定与接触G修订沿用既定标签；不新增论文有效性结论。
- 需要新用户裁决：目前无；若资格揭示重大问题，保存证据后提出具体争议。
