# P2 — 几何一致接触模型资格与协议冻结

Status: CONTACT_GEOMETRY_QUALIFIED / PROTOCOL_FROZEN / CLOSED_LOOP_NOT_EXECUTED
日期：2026-10-14；科学来源51696a8；承接59260fa审计与用户明确模型批准。

## Scientific objective
核验有限SE(3)形变下，抓点只在EE物理自由twist子空间运动且自由Log形变保持初值，再冻结最小闭环实验协议。

## Minimum sufficient evidence
- [x] 明确D精确微分、Ng lift、Ac可逆域、VG解与资格边界。
- [x] 独立Exp/Log有限差分、坐标/自由基变换、零功与有限积分。
- [x] 新释放及新恢复预载独立拒绝、无重锚/形变清零。
- [x] 原记录保留、修正1/3完整、68case同源证据及SHA。
- [x] 新冻结版继承原参数/主seed/时刻/性能判据，旧DRAFT保留。

## Explicit non-goals
完整物体动力学/传感器/42维IESEKF/控制实现、真实闭环或Word实验结果、P4/RSS、P3、Isaac/ROS/FR3场景。

## Inputs / frozen dependencies
- P4@79cc871原成果保留。
- 用户批准几何一致模型；原式20/21/25及9/10/11/12保留。
- 模型p2.spatial_free_log_constraint.v1；固定源码SHA见新冻结JSON。
- 初稿configs/p2_closed_loop_protocol_v1_draft.json原字节保留。
- 冻结协议configs/p2_closed_loop_protocol_v1.json及reports/P2_CLOSED_LOOP_FROZEN_PROTOCOL.md。

## Requirement / Preferred method / Fallback
Requirement：有限形变满足两种独立几何约束并如实界定物理能力。
Preferred：Ng=Ad(D^-1)N，Ac=N^T Jr^-1 Ng，VG=−Ng solve(Ac,N^T Jr^-1 a)。
Fallback：资格失败保留输入/记录，按剩余预算修具体程序错误，不以伪逆/状态投影/新释放控制补成功。

## Attempt budget
初版66case记录PASS但交付资格INCOMPLETE（带符号日志/恢复负例缺口）。修正1后保留原66输入并增加2独立恢复负例，68/68通过；核心模型源不变。
P2总小修已用1/3，剩余2。临时解释器路径失败发生在Python启动前、case0；系统相同版本恢复不另算算法修正。控制run0，不重置原81run上限。

## Stop / escalation conditions
本轮完成冻结，不自动开始控制矩阵或P3。后续在冻结协议下实现；需要更改力模型/摩擦释放、major滤波/控制方法、时间/seed/阈值则按原规则停止。
切换在规定时刻失守直接MODE_SWITCH_PRELOAD_INVALID，不自动等待/重新抓点。

## Deferred issue ownership
| Issue | Owner |
|---|---|
| 独立Eq16动力学、Eq17观测和42维IESEKF | P2下一实现阶段 |
| 控制20/21/25与时钟队列、真正半步动力学资格 | P2下一实现阶段 |
| 低抓力/摩擦释放、硬件与完整装配 | 明确缺项，另行研究 |
| FR3/吸盘/Isaac及P3 | 后续独立阶段 |

## Outputs
新模型源码、完整推导、资格脚本/两轮证据/启动失败、冻结JSON/说明、六份持续记录、保全清单。

## PASS criteria
- [x] 68数学资格case与独立归档核对通过。
- [x] 只标接触几何资格及协议冻结；原近似阻尼/力学/全局稳定性不获PASS。
- [ ] 真实控制响应、IESEKF和整篇P2尚未复现完成。

## Paper fidelity
[ORIGINAL] H/W、原力学式9/10/11/12、原控制20/21/25及表参数。
[DEVIATION / USER_APPROVED] 式15由唯一spatial-free Log约束解替代，明确模型初态域。
[ADAPTATION] 初稿Cartesian/COM观测等缩减仍保留。
[ENGINEERING] 原阈值内数据符号/覆盖修正、固定Python、独占归档。
[EXPERIMENTAL] 控制矩阵仅预声明，尚未运行。
