# P2累计小幅修正2：诊断汇总JSON类型转换

2026-10-14；before源码c66496e。前阶段已用小修1，当前本次为累计2/3，剩余1；没有将第二阶段重新计成三轮。

固定三点差分诊断已完成ε=1e−6、2e−6、5e−7的三份完整AD/FD50/Python矩阵保存，但写summary时max_index由numpy.unravel_index产生numpy.int64，json.dumps拒绝，exit1：TypeError: Object of type int64 is not JSON serializable。原输出目录及三个矩阵均保留，不把归档失败说成没有执行计算。

本轮仅将该脚本的索引转成Python int；before/after全文由git c66496e与本提交保留。新增只读archive脚本从已保存矩阵恢复summary和哈希索引，不重跑三个点、不积分、不运行滤波或控制。原脚本缺失的自身wall_s恢复为null，外部工具返回的整个失败进程wall=0.145563236s单独标注。

这次修正影响归档，不改变Jacobian、AD、差分、连续field、implicit solver、接触/控制模型、ε、门限或实验条件。原N/D FAIL_STOP继续保留；不能用“汇总修好”解除资格失败。源与原始矩阵before/after SHA、错误与影响在结果目录分别保存。
