# ABB PCS固定局部POST审查补充：以规划器真实可达路径确定前置门

2026-10-15。保留原 `P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_20261015.md` 原字节；本补充纠正其末段把未达helper缺陷概括为solve前置阻断的范围。只读源码，无编译、模型或规划调用。

原`sample_q`的`collision && !limits`漏拒，以及三参数随机`IKproject`成功后不break，确实存在于公开导出helper；但独立核查RRT_PCS、CBiRRT_PCS、SBL_PCS主体，三者均不调用这两个`sample_q`或该三参数重载。RRT/CBiRRT使用OMPL `sampleUniform`，SBL使用valid sampler `sampleNear`；实际grow采用`calc_specific_IK_solution_R1/R2`、`identify_state_ik`、原碰撞及固定支RBS。因此不能要求先修复未达helper，才允许这些规划器的有限资格。

solve前置与输出资格应针对实际可达的grow/identify/原限位与碰撞路径、起终点身份、RBS/回溯及输出完整性。原固定LOCAL01只证明其中有限非平凡局部接口，整体仍PARTIAL；不推出全局路径成功。新有限端到端资格可保留原规划源码及未达helper原状，固定seed/输入/参数/预算后真实执行，再由独立物理闭链、分支、限位和离散碰撞检查决定输出是否合格。

未达helper问题属于导出接口的已知限制，后续若某真实入口新增调用再重新归类；不将它当成原论文PCS方法理论错误。正式Table I 0/22500、所有211义务及LOCAL01失败保持。
