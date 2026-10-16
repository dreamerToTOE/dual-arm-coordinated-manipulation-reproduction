# IV 原腕模式 fixed100/800 数学组件实际结果

状态：PASS_RECONSTRUCTED_MATH_ONLY / P4仍PARTIAL。source697b519、v3 runner、qualification_v5，唯一run02完成100/100固定目标和800/800原编号解析K请求，UNKNOWN0；数学arm FK/J开始/完成106，源accepted内FK返回观测6，真实内部K开始无hook仍UNOBSERVED。无采样、碰撞、RBS、NR、RSS分布或solve，不新增VI。

6/800 accepted根全通过独立数学闭链/回代、原完整机械界及原分支身份，G0/G1均6分支/3目标：s040/s056/s092各b1、b3。其余794均ACTIVE_IK_REJECTED，97目标0解、3目标2解；不能用3正例推断RSS成功分布。100被动Jacobian保存谱rank5，6accepted主动rank6、完整6×12约束rank6；主动branch分别单集1/3，被动相会集[1,3]。闭链位置最大7.105427357601002e-13mm、旋转矩阵最大2.498001805406602e-16，主动回代位置最大6.821210263296962e-13mm，原1e-5闭链门、rank1e-6和原几何/基座/抓持/界保持。

原run01首模型前元数据guard零查询STOP保留，不重写为通过。v3只分开R1 literal与runtime degree换算的精确表示；实际bounds和完整科学循环未变。六科学函数AST完全同v2，独立静态35/35及root diff/账核通过。v3工程实施者saved后审6386/6386通过，已披露非完全人员独立；另人员完全独立保存审查5667/5667通过：独立标量矩阵与Jacobi Gram谱/秩、完整100/800来源和J重组均吻合；0新科学。报告RUN02_INDEPENDENT_SAVED_REVIEW单独保存。

执行命令：`python3 scripts/qualify_p4_full_r2_iv_rss_wrist_fixed100_v3.py --protocol configs/p4_full/r2_iv_rss_wrist_fixed100_qualification_v5.json`。run02实际5.185225903000173wall/2.800878CPU；原01+02共享30/60共5.221941273000084wall/2.837645CPU。全部固定100/800已耗，剩余时间不授权新输入或重跑。新V11共29execution=23科学运行账（含零查询失败）+6工程，逐own一次合计509.65709048499434wall/460.539806CPU，R2余3090.3429095150059/6739.4601940000002。

V11保全PASS：1028旧科学文件、57崩溃未提交文件8482891bytes及tar57成员、另5worktree/13未提交、V10旧账及211行前122列全部保持。最新IV_WRIST_MATH完整表130列，211原文义务不缩；VI974余0、正式0/22500，全部500000投影、约50000点对、Fig3–5/TableI–II和消融保持。原R1/native失败与H原STOP保持，不归因论文理论。

下一项：CBiRRT因子D先仅编译两目标，然后分别冻结真实distance64、原local12及单solve入口；RSS碰撞/原RBS/分布/入口仍列待验。正式大规模在相关端到端资格及可重复成本pilot后申请预算，不P2/Isaac，不提前结题Word/PDF。
