# P2 — 独立动力学、视觉触觉估计与位姿/内部力联合控制

Status: IN_PROGRESS

2026-10-14：用户明确授权第二阶段实施；覆盖D068历史的“尚未授权后续实验”。已批准几何替代沿用，P4/RSS/P3/Isaac不在本任务内。

## Scientific objective

由独立软接触刚体模型与42维右SE(3)估计闭环，在固定消融和预算下取得真实模拟位姿误差、内部作用力与控制响应，并据实比较原论文机制及缺项。

## Minimum sufficient evidence

- [ ] 独立force/moment作用点映射、原式10阻尼、式16刚体与固定5s settle/半步资格。
- [ ] 式17测量独立、42维IESEKF/右重置/C冻结/真实时间戳资格；主控制无GT泄漏。
- [ ] 原式20/21/25与H-selected因果input队列、exp2/4开关及全动力学半步资格。
- [ ] 首套30case ledger，包括20主运输、全部代表例/诊断及failed/aborted/NOT_EXECUTED；原始数据可重建曲线。
- [ ] 中文Word/PDF分数学/真实仿真/独立应用差距章，科学失败及原模型差异如实保留。

## Explicit non-goals

- P4新实验/修改、RSS追加、自动P3。
- FR3/Cube/吸盘/车厢/Isaac适配及真实机器人动作。
- 增加低层抓力/摩擦/释放模型，使滑动守门强行通过。
- 把GT、静态分解、解析h衰减、观测噪声合成图冒作主闭环结果。

## Inputs / frozen dependencies

- 科学协议：[冻结JSON](../../configs/p2_closed_loop_protocol_v1.json)，SHA256 423f58ca7cfe13861586bb486dcfd6d19c5e3d82b69e40c3d403c90d7c871df3。
- 几何：p2.spatial_free_log_constraint.v1，模块SHA256 47557da9189d8525e8a1ec343b5a4afc929405071d4e5de7d562091cc04a629a；68项qualification已完成。
- 相关paper card：[P2](../../references/P2_pose_force.md)；实际原文P2_original.pdf、式1–26/图1–9/表I–II。
- 前阶段：[POST-TASK](../../reports/P2_CONTACT_GEOMETRY_POST_TASK.md)、原文审计、初稿历史证据不覆盖。
- 阶段PRE/资产：[实施前报告](../../reports/P2_STAGE2_PRE_TASK.md)。
- 运行前资格：[Stage2 qualification spec](../../reports/P2_STAGE2_QUALIFICATION_SPEC.md)。
- 历史FR3 Benchmark仍DRAFT，不将其场景/阈值混入本P2数值协议。

## Requirement

严格保留原接触力、动力学、内部力/位姿控制和已批准几何；通过顺序资格后按固定矩阵实做。若资格或科学假设不成立，保存真实证据、退出和未执行账目，写部分完成/未通过，不能通过改判据“完成复现”。

## Preferred method

独立式16COM plant与Lie中点；原式9–12力场；纯几何模块不改；由真实plant生成带噪式17观测；经核验的right-SE(3) IESEKF（候选IKFoM或等价独立实现）；原控制叠加后经H选择和多率队列。数学/物理oracle、部件资格、全动力学半步依次推进，首套30case与源/协议hash明确登记。

## Fallback method

资格失败保存数据并停止后续，作有依据的小修或报告模型限制；不换GT/普通EKF/另一个物理模型，不临时延长120秒case或5秒settle。

## Attempt budget

P2累计小修1/3已用、剩余2，跨数学资格/估计/动力学/控制合并计数。每个非重大实现问题先诊断再凭证据修正；不得按子模块各重开3轮。初套30控制case，未来最多74且原81上限不扩大；120秒/case、7200秒总体。部件资格单独预登记，不作为额外性能样本。

## Stop / escalation conditions

- 独立动力学、原settle、估计/时间/协方差、全动力学半步或模式守门失效。
- 冻结参数/几何/种子/轨迹/性能判据需要改变，或需要新增摩擦/低层抓力/其他重大算法。
- 总小修/控制case/壁钟预算耗尽。
- 组件合格不足却拟用GT或合成响应替代主结果。

## Deferred issue ownership

| Issue type | Owner |
|---|---|
| 原硬件关节/位置伺服与300ms真实执行器辨识 | 后续硬件条件对照，不扩大本轮 |
| .3N低抓力、摩擦释放及完整多块装配 | P2后续物理复现，当前列缺项 |
| FR3/吸盘力接口、Isaac迁移、车厢适用性 | 正式报告最后应用差距章及后续独立应用任务 |
| P3及其它论文算法 | 用户后续独立授权 |

## Outputs

- code：baselines/p2_pose_force的独立mechanics/estimator/controller/sensor-clock及脚本，由root分配。
- report：阶段资格、失败/修正、真实结果与中文Word/PDF。
- result artifacts：独占results目录、各资格input/metadata/trace、30case ledger及控制原始日志/曲线。
- persistent records：root按治理规则追加STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK，保留全部历史。

## PASS criteria

- [ ] 每个实现组件有对应独立资格，原几何/参数/指标/预算未偷偷改变。
- [ ] 如控制比较可执行，完整同源数据和三条固定配对比较假设逐seed公开；不成立据实写失败。
- [ ] 如资格失败，失败证据/停止原因/NOT_EXECUTED完整，不宣称控制成功。
- [ ] 报告的主图仅重建自落盘模拟观测/plant/估计/控制日志，GT诊断单独标明，原文与本机数值分开。

任务实施完成与论文科学假设通过分别记录；前者不自动令后者PASS。

## Paper fidelity

- [ORIGINAL]：式9/10/11/12/16/17/19–21/25、原H/W、原表I/II及四组增益/模型K设置。
- [ADAPTATION]：均质惯量/自定抓点与路点、Cartesian执行器、COM模拟观测、静止预标定、异步Q/C冻结；均沿用已有披露。
- [ENGINEERING]：独占目录、整数clock、因果queue、独立oracle/Jacobian、源码/日志SHA及失败账目。
- [DEVIATION]：用户已批准的式15抓取演化替代，仅此继承批准；不称原作者勘误。
- [EXPERIMENTAL]：固定GT/步长/时延/理想滑动诊断；不将自建对照结果说成作者原始数据或完整硬件复现。
