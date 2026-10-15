# P4 R2 几何一致修复资格声明

=== PRE-TASK REPORT ===
Task: D079六环境原生失败后的有界修复资格。
Scientific objective: 在不改变原机器人/物体几何和物理坐标条件下，检验解析IK、真实奇异条件与原论文NR伪逆方法能否满足原物理闭合门。
Minimum sufficient evidence: 原输入重放、独立FK/解析Jacobian交叉验证、已知闭合正控、明确不可达/非奇异负控；保留每个被拒绝输入。
Current scope: configs/p4_full/r2_geometry_consistent_qualification_v1.json；仅数学及组件资格。
Explicit non-goals: 正式规划矩阵、数据筛选、原始端点替换、P2/Isaac/FR3控制。
Attempt budget: 最多2核小时、1小时实际执行墙时；每构建/诊断120秒；同机制三次修正强制独立根因复核。
Preferred method: 在外部隔离副本修复作者解析IK；NR按原伪逆原理统一到实际物理闭合坐标；保留全部原生对照。
Fallback: 只有独立参考NR/确定性奇异fixture，不冒充作者C++速度或完整RSS采样。
Stop: 新模型/实验判据/不确定VI采样分布/正式预算须裁决；固定资格失效不能静默下游。
Files expected: geometry_consistent新目录、R2新配置/日志/审查；旧科研文件不改。
Validation: 冻结配置后冻结源码，再真实执行；逐项原输入/变换/分支/单位/CPU与墙时留存。
Known risks: 原公开端点的舍入精度、VI未公开生产RSS、球腕奇异的规范代表不能证明整个奇异集合覆盖。
Need user confirmation: 本轮建议范围已由用户“继续”接续；不重复请求。新的重大科学设计仍待裁决。

=== PRIOR-ASSET CHECK ===
Scientific algorithm: 论文APC、NR、RSS；不能用旧FR3算法代替。
Pinned prior project: dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a，前阶段已审计。
DIRECT_PORT: 原有报告工具与保全哈希。
THIN_ADAPTER: R1原生C++harness、不可覆写输出和依赖编译方法。
TEST_ORACLE: R1独立ABB/Comau逐关节FK、保存的原输入和原生FD。
REFERENCE_ONLY: 原FR3离线规划器/碰撞与执行基础设施。
Rejected: 旧FR3长度、抓持、成功阈值和随机采样，不适用于作者六环境。
New: 数值一致补丁工具、一般循环3R解析、实际闭合NR/Jacobian和有限资格运行器。
Contamination: 参考PythonNR只作组件核验，不能与C++APC做速度结论；所有修复与源码差异显式保留。

## 物理闭合NR推导

保持Tj*=T1 Q1j S。令d=Q1j S的平移，R*=R1 RQ，位置残差ep=pj-p1-R1d，姿态残差er=Log(Rj R*^T)。对各臂世界几何Jacobian(Jp,Jw)，位置对臂1为-Jp1+[R1d]×Jw1，对臂j为Jpj。令E=Rj R*^T、phi=Log(E)，姿态导数为Jl(phi)^-1(-E Jw1)及Jl(phi)^-1 Jwj。VI叠加两条约束，形成12×18而非公开默认两阶段投影；这是原论文全约束NR的独立实现差异。

按dq=-J^+g迭代，不作阻尼、APC兜底或隐式成功。代数SVD同时含mm/rad，不能把其范数当物理误差；通过判断分别使用位置与旋转矩阵门。限位拒绝单列，既不把原返回false误称发散，也不删除其失败。

R1所有失败保留。新已闭合fixture仅用于组件正控，明确记录相对原始端点的变化，绝不成为未经裁决的正式起终点。VI RSS候选只能交推导，不先运行未知原分布。
