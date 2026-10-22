# P2数值协议v3：已批准五点资格与固定N/D继续

2026-10-14；输入4276ce5。用户明确批准只版本化native continuous-field Jacobian oracle为Boost50位五点四阶中央差分。原ε1e−6/绝对门1e−7、原公式/observer式18/控制/观测/时刻/seed/形变/五秒和半步门以及预算保持；原v1/v2、首门FAIL_STOP、三点诊断/归档修正2与Word不覆盖。累计小修2/3余1；本次明确数值资格裁决不重开或自动消耗修正额度。

沿用P2_IMPLICIT_QUALIFICATION_SPEC.md原固定输入/顺序/所有门，仅第3项native continuous-field oracle改为D4(h)=[−f(+2h)+8f(+h)−8f(−h)+f(−2h)]/(12h)。每列在同一状态的右SE3扰动上独立四次primal求值，不使用AD作FD、不归一化、不变ε/门。原两点native导出函数原代码保留，物理field/contact/G/implicit kernel不变。

资格脚本qualify_p2_implicit_v3.py为原脚本的薄版本适配，只切v3config、v3独立build目录、oracle导出与元数据/当前预算；实际固定36＋18＋6 Jacobian＋1残差＋6五秒＋3步长=70项预声明检查，失败立即停。不把中断导致实际小于70说成完整通过。A/C三模式Jacobian均需通过原数值门；单步仍以canonical重新计算r≤1e−12；6条lockedEE5秒和3对粗/半步不延长不重置。原三组件资格仅N/D全部通过后才运行，冻结30case完整控制gate再后续。

新native编译目录.p2_native_build_v3不覆盖旧二进制；源码差异仅新增FD5导出/调用，报告build/source/旧原始结果SHA。原物理执行式9–12/16与原观察器Eq18不受本次批准影响。
