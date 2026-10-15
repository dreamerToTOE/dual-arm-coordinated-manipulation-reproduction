# P4 R2 ABB原RRT_PCS端到端资格 PRE-TASK草案

2026-10-15。用户将优先级明确调整为PCS/NR原生规划入口和第一条合格空间起终点路径。当前仅工程准备：新增driver、一次工程builder与未冻结协议；不编译、不solve、不commit、不创建运行claim。IV fixed100数学方案已完成独立静态审查，按新优先级暂缓运行。

## PRE-TASK REPORT

- Task：原作者RRT_PCS实际入口，环境II，固定A01 reconstructed start/goal、seed7的一次端到端资格。
- Scientific objective：验证真实原RRT_PCS是否能返回完整空间路径，以及该输出是否通过独立闭链/原限位/分支和离散碰撞门。一次pilot不是正式性能统计，也不证明PCS优势。
- Minimum sufficient evidence：原solve exact/approx状态、完整milestone、完整PlannerData树、每次state-level reconstructRBS结束后的17位qa/qb/role/branch/Confs/returned；保留原低精度paths及temp作为对照。物理路径后审由独立runner负责；solve exact与source save2file完成不自动当路径合格。
- Observation accounting：reconstruct与identify均为原返回之后的completed观测，硬kill前未返回调用的真实started为UNOBSERVED，不由日志行数反推。没有添加started或额外IK hook。
- Current scope：仅复制既有geometry_consistent_plain到全新外部stage，链接原RRT_PCS，保持源投影/identify/原native collision/RBS算法与失败；不修未达helper。环境II的A01恢复端点原字节作为固定输入，各端保持自身原分支（arm2起点3、终点0，并非起终同支）；seed7用于OMPL RNG::setSeed与srand，Range2.6、goalBias.05、solve10s。Range2.6来自作者run/plan_PCS.cpp的RRT环境II条目，头文件默认2不是原main此环境实际传值，未将内部初稿默认值当成用户指示。
- Explicit non-goals：正式Table I、换seed/换端点/步长调优、平滑、裁断路径、NR兜底、其他planner和环境、IV新运行、VI候选、P2/Isaac/FR3施工。
- Attempt budget：单一工程build45wall/90CPU，单次规划总30wall/60CPU，独立路径audit120wall/240CPU；都扣原R2 3600wall/7200CPU并分别保存实际成本。此稿只准备build与科学草案，不授权执行；prior必须在各自冻结时重新绑定。
- Independent audit cap：完整保存全部dense节点队列，最多2048 unique节点的独立查询（math FK≤4096、collision≤2048、adapter内部FK/J≤8192）；超过预算则保全完整队列和未验尾项、UNKNOWN，不能截断路径给PASS。外审不调用IK/投影/NR，不做平滑或CCD。
- Preferred method：复用已成功链接的外部plain stage与既有编译配方；最小只读输出hook。
- Fallback method：无运行重试；失败保留全部源、stage、日志、近似解、回溯false和未执行尾项，进入根因审查。预算/条件不在失败后更改。
- Stop/escalation：来源/hash/冻结不符、既存claim/output、build失败/时限、运行异常或独立门失败均留证；不把partial/approx变exact。任何后续预算/实现修正另记证据。
- Files expected to change：本新PRE、`scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py`、新C++driver/输出header、新build与science draft配置；旧外部资产和旧实验原字节不改。
- Validation plan：静态API/源body/argv/冻结/预算/哈希审查；仅AST与已保存字节/标量分析，独立审查通过且父任务冻结提交后才可编译，成功工程链再进入规划冻结。
- Known ambiguities / risks：原RRT不显式复验全部最终节点物理闭链或完整限位；原save2file可在回溯false时提前return，solve仍添加milestone为solution，必须分栏检查。原RBS端点有效前提和原低精度文本不可用作独立最终资格。真实路径后审必须使用完整17位Confs而非低精度path.txt。
- Need user confirmation：no，本工程准备及有界资格来自当前明确授权；冻结和独立审查尚未完成，不提前执行。

## PRIOR-ASSET CHECK

沿用D079已审作者CKCplanning固定909bd72、R2模型和旧项目分类；本项不重新造规划器或碰撞系统。

- DIRECT_PORT：外部`abb_pcs_qualification_v1/geometry_consistent_plain`的原RRT_PCS/APC/SVCPCS/PQP/网格；原R2数值修正已单独标RECONSTRUCTED。
- THIN_ADAPTER：现有`build_p4_full_r2_abb_pcs.py`编译/来源/claim/CPU总帽与新driver JSON输出。
- TEST_ORACLE：原A01端点、现有独立FK/J/branch与v3 collision adapter；物理后审由父任务实现，不能反向修原规划返回。
- REFERENCE_ONLY：旧FR3/MoveIt/FCL/Isaac工程；不引入本论文资格。
- New code：只写传输、I/O观测及单次工程保全，不重写科学grow/RBS。
- Fidelity risk：原作者plan_PCS.cpp OMPL采样盒逐臂为lower `[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]`、upper `[2.88,1.919,1.22,2.79,2.09,3.1416]`，本次逐值保留，原callback恒true不变；源grow/RBS仍保留原collision。独立路径audit另验原完整机械界，不用宽机械界替换原采样分布。纯数组检查A01两端均在原采样盒内。原RRT main在作者env=1（论文环境II）传Range=2.6，goalBias=.05保持；solve10s是有界资格而非原正式1000秒。此前内部草案的Range2与“已批机械采样界”不是用户指定参数，静态审查阶段已纠正且从未运行。
- I/O deviation：仅新stage内原`std::remove("./paths/temp.txt")`替换为保留temp；state-level reconstructRBS在原返回后记录完整Confs，原vector identify_state_ik在原返回后记录q12、input_ik、returned_ik，不新增FK/IK/碰撞调用。该观测会增加输出开销，不能以其时间充当论文正式性能。
- Need user decision：no，已明确限于此工程/有限资格；完整统计与新方法变更无授权。
