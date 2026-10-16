# IV fixed100 v3：1 ULP 根因与冻结前静态审查

**PASS_STATIC_PENDING_ROOT_REVIEW_FREEZE**：157/157，失败0。0模型/IK/编译/候选/新claim。

first01在0 target/0 FK/J/0 K处由精确guard停止。原R1 q1 literal ±3.1416（hex尾a7）与既有runtime ±180×3.1416/180（hex尾a6）每侧相差1 ULP=4.440892098500626e-16rad，其他五关节十个边值、基座、抓持均不变。根因属于我们前置guard混同比较两种浮点表示，不能归于论文、机器人FK或作者IK。

新v3分别冻结原metadata与runtime预期全12界，运行前exact比较完整runtime界；实际physical.source_limits及候选legal判据未动。六科学函数AST不变，run只改前置guard，全部后续循环/数学门/输入/分支保持。原v2与first01原字节不改。

run02新claim保持同一共享30wall/60CPU，扣first01自身0.03671536999991076/0.036766999999999994秒，余29.96328463000009/59.963233秒；100目标/800请求未消耗而非重置。V10全部28笔自身账目及64资产SHA通过，v5草案describe/validate零query通过且未冻结。此工程版本由本审查者按root授权实施，root仍须独立核diff并冻结提交，才可唯一执行。
