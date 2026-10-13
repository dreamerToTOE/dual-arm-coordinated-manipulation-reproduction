# 修正3/3：NumPy标量JSON表示等值转换（最后一次）

2026-10-13。失败源码 `17202df`；round2全部文件保留。
17项数学测试通过，已保存RSS/E0/budget200/seed7完整TIME_LIMIT试验（5.000025635s、286nodes）。
下一PCS调用到保存raw JSON时抛出：`TypeError: Object of type bool_ is not JSON serializable`。
其中`reached`的NumPy比较产生`np.bool_`，不是模型/算法资格失败。
PCS gzip未完成，不将其当完整试验/成功统计；run result为ABORTED，有原始termination traceback。

## 唯一改动

JSON输出仅对`np.generic`使用`.item()`，得到等值的Python bool/int/float。
不改变规划判断、节点、路径、门限、采样、模型、环境、预算、测试或浮点数值。
仍`allow_nan=False`，不接受非有限值；其他未知类型仍报错，不能默默删字段。
所有raw/metadata/summary JSON使用同一等值转换，避免再次局部序列化错。

预期：固定17项+60规划+3重复整套记录到独立round3目录，不覆盖round0/1/2。
原round2已保存TIME_LIMIT保留，但不加入最终每条件5个trial的统计分母。
这是补齐序列化边界，不是改变算法以逼近论文结果。

**实现修正预算3/3已用满**。本次若再次启动/接口/源码失败，则停止并工程升级；
科学TIME_LIMIT/ITERATION_LIMIT等只作为真实失败统计，不继续调参/改场景/择种子。
