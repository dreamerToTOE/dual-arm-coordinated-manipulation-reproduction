# P2 最小闭环实验协议 v1（2026-10-14 冻结）

协议状态：**原文审计与接触模型资格已完成，实验协议冻结；完整控制器/估计器/动力学闭环尚未实现，控制实验未执行。**
固定参数入口：[p2_closed_loop_protocol_v1.json](../configs/p2_closed_loop_protocol_v1.json)。原[DRAFT全文](P2_CLOSED_LOOP_EXPERIMENT_PROTOCOL.md)与[初稿JSON](../configs/p2_closed_loop_protocol_v1_draft.json)保留历史版本。除下面列明的接触演化、切换初态域、资格状态和修正预算记账外，初稿第1–7节的模型参数、观测、滤波设计、参考、消融、时间、种子、性能判据和失败归档规则全部继承。

## 1. 已裁决的接触演化

用户明确批准：保持原位姿/内力控制器，重新推导几何一致接触模型，记录差异，通过有限形变检查再冻结协议。采用模型 `p2.spatial_free_log_constraint.v1`，属于**用户批准的[DEVIATION]**，不称为作者勘误或式15原样复现。

令`D=E_common^-1 O G`、`τ=LogD`、`a=Ad(G^-1)Vo−Ad(D^-1)U`、`N=null(H)`。固定闭合式为

\[
N_g=\operatorname{Ad}_{D^{-1}}N,\quad
A_c=N^\top J_r(\tau)^{-1}N_g,\quad
V_G=-N_g A_c^{-1}N^\top J_r(\tau)^{-1}a.
\]

tight时N为空、VG=0；否则用直接线性求解和既定rcond1e−12奇异性门禁，不用伪逆掩盖失败。精确关系`τdot=Jr^-1(a+VG)`给出`N^T τdot=0`；同时`Ad(D)VG∈null(H)`。详细推导、标准模式可逆域和虚功限定见[接触几何推导](P2_CONTACT_GEOMETRY_DERIVATION_RENDERED.md)。函数Log分支保护为`||θ||<π−1e−6`；原实验每个pad角分量≤.15rad等有效域未放宽。

O/E必须先表达于共同base：E1_common=B1 E1_native；E2_common=B1 C^-1 E2_native。body twist在固定左乘base变换下不变。不能把robot2原生EE pose直接送入该几何函数。

式9/10/11/12的力模型与H/W、式20/21/25控制器及K/B/KF/KP不变。阻尼仍用原Rbar近似，不以精确几何a偷偷替换式10。共同刚体运动时D不变，不代表原近似阻尼必为0。本资格不证明全力学模型被动性、全局/切换稳定性、真实摩擦或装配安全。

## 2. 固定模式与切换初态域

自由Log分量保持其初值，**不会自动卸掉已有预载**。真实plant初始自由形变须为0；程序没有每步投影或重锚。估计误差不能被当作真值强行清除。

在原定5s/25s事件，两次模式切换都检查新恢复和新释放分量，以及新模式全部自由Log分量。pivot→sliding恢复Mz、释放Fx/Fy；反向恢复Fx/Fy、释放Mz。
新自由/改变分量的|τ|≤1e−6m/rad；改变分量切换前**未经过H选择的真实hK+hB**的force≤.006N、moment≤2e−6Nm。阈值沿用初稿，不根据曲线改变。检查新释放分量是本模型零自由形变初态域所需补充，不是改位姿/内力性能标准。

不满足时记MODE_SWITCH_PRELOAD_INVALID并停止该run；不等待卸载、不改变原定切换时间、不清零/重锚、不新增低层grasp控制使该例通过。此模型没有实现原文.3N低抓力与摩擦释放；未来滑动代表例可以真实失败，不能因几何资格通过预先宣称它成功。

## 3. 已取得的有限形变资格证据

第二轮源码commit`51696a8b6ada556af3ce2f0acb4ebdf9cecca099`；[68项原始记录](../results/20261014_P2_contact_geometry_qualification02/cases.jsonl)、[metadata](../results/20261014_P2_contact_geometry_qualification02/metadata.json)、[汇总](../results/20261014_P2_contact_geometry_qualification02/summary.json)、[独立归档核验](../results/20261014_P2_contact_geometry_qualification02/independent_artifact_audit.json)。

36有限差分、6坐标、2自由基、9双侧H代数、9有限积分、6切换资格，共68/68通过。切换负例使用静态合成hK=−Kτ、hB=0，含刻意构造的无效预载，**不是控制实验测量**。双侧H转置配对只是代数自洽；抓点spatial-free lift的独立零功检查另有证据。

最差线性导数差分2.81893e−11m/s，角导数差分7.835997e−10rad/s；sliding自由积分漂移3.18535e−13m，pivot自由积分漂移3.29656e−12rad。tight无自由方向，标NO_FREE_DIRECTIONS，不将空约束当作收敛证据。

首轮原66/66 PASS文件保留；外部交付资格记INCOMPLETE，因为有符号弹性差日志和新恢复负例覆盖问题。[修正1记录](P2_CONTACT_GEOMETRY_CORRECTION01.md)说明`hK_coarse−hK_fine=−K(τ_coarse−τ_fine)`，保留原66输入并增加2个独立恢复负例。核心抓取模型源码未变；两轮不混成独立样本。临时解释器路径失效的启动失败也保存，实际第二轮用相同版本系统Python运行。

## 4. 未变的主实验与预算

- A原质量/尺寸、均质惯量假设、原表I/II；exp4只改变模型K，trueplant名义K。
- 20主运输：exp1/2/3/4×seed[7,23,41,101,20261013]；exp2仅KP=0、前馈保留。
- 7/13/76/95s事件、23/55s补齐段界与既定路点，200/50/100/15Hz和1/3000s主时钟不变。
- 42维right-SE3 IESEKF设计、C冻结、异步Q尺度、新观测时间戳、无GT泄漏和因果hB规则不变。u_model明确取上一份**H选择后的已发布held input**；不读GT速度。
- 2高moment、2delay、1有条件sliding代表例及5个GT/步长诊断，首套30；代表例不混入主20统计。
- 全部5配对seed的85–95s GT位置RMS/角RMS及13–76s真内力RMS比较假设不变；原文数字仍仅描述性参照。
- 原81控制run天花板、单case120s和总7200s壁钟不扩展。总小修额度3，已用1（资格脚本符号/覆盖），剩余2；因此后续实际上至多30+2×7+30=74控制run，不另给三轮。数学资格不计控制run，但修正预算跨阶段累计。

## 5. 下一阶段入口与本轮停点

`contact_geometry_qualified=true`；`controller_estimator_qualified=false`；`closed_loop_runs=0`；协议`frozen=true`但`executable=false`，因为完整执行栈不存在。本轮只批准推导/资格/冻结，不自动开展控制矩阵或P3。

后续在同协议下实现并核验独立式16动力学、原式9/10/11接触力、式17观测、42维IESEKF、式20/21/25控制与多率队列，再做原已登记的settle和全动力学半步检查。**本次数学积分不能替代这些闭环资格。** 需要重大模型/算法变化仍按原规则停止；不为凑原图1.5N/80%而改bias、阈值或seed。

正式中文Word的数学/控制器、真实仿真与原文对照、最后独立应用差距章节保持既定组织；当前未取得真实闭环曲线，不生成实验完成的Word结论。P4全部科学源码/实验/失败/Word保持原样。
