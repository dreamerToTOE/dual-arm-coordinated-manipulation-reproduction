# P4 R2 ABB physical NR C++ 草案逐式静态审查

2026-10-15。只读核对，没有编译、运行、FK/J/IK/NR/碰撞调用，也没有修改草案或冻结科学输入。结论为 `STATIC_FORMULA_MATCH_NOT_RUNTIME_QUALIFIED`：在环境 II/III、有限 q12、协议默认选项的域内，没有发现相对现存 Python 参考的算法公式偏移。此结论不证明 Eigen 可构建、跨语言数值轨迹或运行效率。

## 绑定字节与范围

|文件|本次读取 SHA256|
|---|---|
|`baselines/p4_full/geometry_consistent/physical_nr_abb_cpp_draft.hpp`|`e387e7c4b625ffa41d63d47093a4cf0c75a04d07d1f1b8d4693162653814449e`|
|`baselines/p4_full/geometry_consistent/physical_nr.py`|`e2dc41936190c7fe335a442c1fee2952681ea5c1be5b94393590188f0fb87d43`|
|`baselines/p4_full/abb_independent_oracle.py`|`573af526968476f8b41b94b2ead5a555b45874eae6b080255e03c8aba489b075`|

这是我们独立重建的 physical full-Jacobian NR，不是原作者 KDL NR 的逐轨迹等价实现。原 KDL 使用的坐标、绝对 SVD 判据和已保存失败继续单列；草案只覆盖 II/III，不能外推 I、IV、V、VI。

## 已核对的公式

- ABB 轴顺序 z-y-y-x-y-x、基座高度 166 mm 和六段偏置与独立 oracle 相同；基座 yaw 保留 3.1416，II 的 D/L=900/300 mm，III=1200/500 mm。
- 每关节先记录世界轴与原点，再旋转、平移；平移 J 列为 axis×(endpoint−origin)，角 J 为世界轴。没有引入新的 URDF、零位修正或 exact-pi 基座。
- target 为 T1·grasp·diag(−1,−1,1,1)，旋转误差为 R2·Rtargetᵀ；SO(3) 主值图、近 π 歧义和小角 left-Jacobian-inverse 展开与 Python 相同。
- 约束 g 为三位置差和三个 log 分量，J 的主动平移块为 −Jp1+skew(R1·grasp.p)Jw1，旋转块为 −Jlog⁻¹·E·Jw1；另一臂块为 Jp2 与 Jlog⁻¹·Jw2。保留 mm/rad 混排行，不作额外缩放。
- 每步重新计算 matrix-entry 残差；判据仍为位置≤1e−5 mm、旋转元素≤1e−5。SVD cutoff=smax·1e−12，仅 s>cutoff 求逆，q←q−V·diag(inv)·Uᵀg。无 damping、line search、步长夹紧或迭代中限位投影。
- iteration=0…10000，最多10000次更新；终止状态默认 ITERATION_LIMIT，墙钟、非有限、近 π 异常保留。收敛后 atan2(sin,cos) 真 2π chart，再检查闭合与原 3.1416 换算的机械限位。

## 观察接口的一个须澄清点

`Step.delta_q` 注释写的是实际 `q_next−q_before`，赋值却是 `−correction`。后者是更新提案；浮点减法后，再由两个已保存 q 相减得到的观测差可能有末位舍入差。两者都不改变求解器，但日志必须清楚分列/标注。

Python 原表达式不保存 correction，只能在原 q-= 之后观察已有 q，再由保存 q_before/q_next 重建 rounded difference。因此跨语言比较应比较相同语义的 observed delta 或直接比较 q_before/q_next；不能把 Python 的差冒称原 SVD proposal。C++ 若同时保存 proposal，应另命名。此问题属于可修正的观测语义，不是 NR 数学公式错误。

## 完整 trace 的静态接受条件

原 Python trace 只有每步残差。后续详细 trace 应观察原 `project_nr.__code__` 的局部变量，复制 q/g/J/s/inv/mask，保留原返回对象和旧残差 trace；不要复制一份新数值 solver，也不要为观测增加 FK/J/SVD。若使用 `sys.settrace`，必须在 finally 恢复进入前的 trace，限制到原函数 code/frame，并记录异常或无更新末步。

单 binary 的 C++ plain/trace flag 只允许控制日志复制。相同 C++ 数学输入与配置下应核对最终状态、q、残差、更新次数一致；跨 Python/Eigen 不假定逐字节轨迹，SVD 的 U/V 列符号也不作为独立门。详细比较应针对 s、cutoff、rank、g/J、已有 q 序列和匹配语义的更新。敏感点分歧必须保存并诊断，不能反向调整通过阈值。

64 个 C++ 最终候选另由现存 Python `residual_metrics` 与 `source_limits` 检查，额外成本应登记为64次 metrics、128次数学 arm FK/J，不冒充零成本保存审计。NR 可改变完整12角；PCS 的固定主动角与固定分支不是 NR 的失败门。碰撞和 planner/RBS 仍须另验。

## 边界差异与结论限制

C++ 对非法 environment、错误维数的异常捕获顺序与 Python 并非逐字符串相同，plain 默认不保存 Python 的残差列表；这些应由冻结 valid-input 域和观测契约处理。当前没有借此要求额外机器人试验，也没有修改现存历史输入或求解器。静态审查无法证明异常运行时、wall-limit 调度、内存使用、Eigen 构建或跨语言收敛一致性；应由下一份有限 PRE 和实际日志回答。

科学调用0；工程构建0；新增 VI 候选0；正式规划0。本报告为新增静态审查，不覆盖任何已冻结 PRE、源码、配置、失败或执行结果。
