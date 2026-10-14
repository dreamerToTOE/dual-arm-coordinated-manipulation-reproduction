# P2隐式积分与原闭环实施前记录

2026-10-14，输入eb2600a；用户明确批准“隐式耦合Lie中点plant：版本化数值协议，先做等价计算优化与求解/步长资格，再继续闭环”。原v1、9194f9f失败及385d08d数值审查保留。

## PRE-TASK REPORT

科学目标仍为原P2独立物体动力学、42维右扰动IESEKF与式19–21/25联合控制在原条件下的真实响应。当前先解决已确认的计算性能和C显式积分局部稳定性；新授权只变物理积分数值实现，不自动改变原式18估计预测。

最小证据依次为：数值核与canonical几何/力学逐项一致、隐式残差/右切Jacobian/无状态投影、A/C等原五秒settle及半步、估计/控制/观测资格、已登记30case中的exp3粗/半步资格，再执行其余矩阵。失败保存、固定判据不改；重大新模型/算法问题停止。

新数值协议v2与v1逐项diff：仅积分实现/新授权/来源/readiness元数据。原K/B/mass/inertia、geometry、gain、clock、noise、seed、event、reference、120/7200秒及控制case预算保持。原v1 SHA423f58ca…与geometry SHA47557da9…不变。修正累计1/3，余2；用户本次明确科学数值路线裁决单独记账，不重开三轮。

数值定义为δ=dt f(X_old⊞δ/2,U)，X_new=X_old⊞δ；E1/E2增量dt U、C增量0已知；O/V/G1/G2共24未知用full Newton。初值Euler δ0=dt f(Xold,U)，最大12次、逐分量残差≤1e−12，no line search/substeps/projection/fallback。求解失败保存末次δ/残差，不强行接受。连续f用原式9–12/16及批准G闭合，primitive与原reference比较。

优化采用本机Eigen3.4.0/g++编译纯数值核与前向自动微分。canonical Python保持不变作资格oracle；pivot约束仅SO3左Jacobian逆角向行，sliding按同闭合式用inverse-Jacobian Bernoulli向量求值，物理pad角域≤.15rad分量内另有等价资格。编译flags/headers版本/二进制/源码SHA都记录；编译产物不代替科学源码。不混用Rbar近似阻尼与精确G几何a。

其余实现由原任务授权继续：新观测仅由trueplant+noise生成；主初态只读fresh measurements/calibration；IESEKF均值仍式18 Euler、C Schmidt、原Q/R/5次迭代；控制仅estimated state及旧published held command，理想端点H选择与原速率。原完整halfstep使用同物理事件时刻，GT诊断独立。非目标P4/RSS/P3/Isaac/FR3优化继续不启动。

## PRIOR-ASSET CHECK

已沿用先前读取EXECUTION_GOVERNANCE、STATUS、task/card、P2原文与六资料、POST_TASK01_REUSE_MAP与common/logger、原Report/OMML。DIRECT_PORT无机器人控制器；THIN_ADAPTER独占run/原子JSON/失败证据、原中文报告；TEST_ORACLE未改canonical geometry/mechanics/已有68记录；REFERENCE_ONLY旧FR3/ROS执行和旧P2未提交代码，不进入新的算法。新native核、implicit solver、42维滤波、原控制/观测为明确科学缺项。需要再确认：无，本次路线已获用户明确批准。
