# IV run02 独立保存结果审查

2026-10-16。审查者 nr_path_prepare，与 v3 实现者及运行者分离。仅 stdlib 读取既有原始文件和矩阵算术，5667/5667 项通过；0科学模块import、0模型 FK/J/IK、0原生程序/编译/claim。

核对100组 R1原输入、仅q5置零的被动角、100组 target、800原始K输入与native JSON/stdout、800分支记录及106次FK/J的保存事件，顺序、分母、重复文件和hash均一致。完整1302个输出文件及协议/claim/全部绑定 before/after hash 保全，未发现缺项或未执行尾部。

G0与G1均为6/800分支、3/100目标：sample40、56、92，各branch1和3。其余794分支保留原始IK拒绝。六解使用原解析返回值和原12关节精确runtime界，分支符号与meeting set独立核对一致。对保存Jacobian使用独立stdlib对称Jacobi Gram谱算术：100个被动rank5，六个主动rank6，六个完整约束rank6；没有新增机器人查询。

独立从保存pose/J重组的闭链Jacobian最大元素差4.547473508864641e-13；六解独立闭链最大位置残差7.105427357601002e-13mm，旋转矩阵最大差2.498001805406602e-16，保持原1e-5闭链门限。谱复算比较容差仅处理审查数值舍入，不改变原relative rank1e-6或其他科学判据；详情及峰值见同名JSON。

run02实际5.185225903000173s wall、2.800878s CPU；与保留失败first01合计5.221941273000084s wall、2.837645s CPU，低于原共享30/60帽。计数800派发/800JSON、6可观察accepted nativeFK；无原生start hook的内部真实IK/FK started仍为UNOBSERVED。

结论仅支持 `PASS_RECONSTRUCTED_MATH_ONLY` 的保存数据和数学门。未重算模型输出，不证明碰撞、checkEE/RBS、RSS分布、连续局部路径或规划成功。first01失败、原作者失败、VI974/974、Table I0/22500和完整211项义务均保留。
