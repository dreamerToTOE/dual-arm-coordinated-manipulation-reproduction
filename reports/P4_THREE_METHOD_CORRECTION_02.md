# 修正2/3：精确奇异解的数值身份保持

2026-10-13，失败源码 `41689ef`，原结果 `results/20261013_P4_three_methods_round1/` 全保留。
本轮17项测试中16项通过；还没有开展60次规划比较。

## 已保存证据

- 两环境START/GOAL均限位/闭链/GEOS合格。
- 登记singular fixture `q17=0`，被动Jacobian秩2，det=4.0647156867484834e-19；
  最小singular value=1.1978564752449852e-17，闭链位置8.349770295452321e-16m。
- 两段RSS RBS均 `DISCRETE_RBS_QUALIFIED`，完整记录在math_evidence.json。
- 唯一失败：`test_singular_fixture_has_true_passive_rank_loss` 重新对该精确奇异解进行±根解析IK，
  数值差4.39521109844431e-7rad > 预定1e-7rad，两根合并验收未通过。
- 原函数从变换重算余弦，在D≈1的边界用acos时微小浮点误差被放大；没有模型/奇异定义错误的证据。

## 唯一实现修正

在解析IK中，若输入已满足**原**闭链容差、原关节边界和原被动branch=0条件，
其已经是两分支共有的合法奇异解，直接返回该实际q及原余弦值。
其他非闭合或非奇异输入仍按原±acos公式计算，不进行新snap/clamp，不扩大cosine/branch/闭链门限。
这与初版Strategy对已闭合精确奇异点保持身份一致，避免底层IK再次人为拆分。
不更改任何测试断言、fixture、参数、几何或数据，不优化算法性能。

预期：两个分支对精确合法singular input都返回原q，原1e-7rad测试保持不变；
随后原协议17项数学测试+60规划调用+3重复以独立round2目录运行。
修正额度 **2/3**；原round0/round1失败保留。
