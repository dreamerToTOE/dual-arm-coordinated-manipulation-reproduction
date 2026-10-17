# P4 D080：V PCS/NR 首项资格的可实施工程计划（未执行）

2026-10-17。纯源码/保存数据计划，不导入模型，不 describe/validate，不编译，不运行 FK/J/IK/NR/PQP/RBS/规划/RNG。前项静态报告及 JSON 保持原字节：报告 SHA `e5beedda43b8ced4657ba6f0b123b41cec2738f8dd80f9e78ce5f0d04628b4da`；索引 SHA `202ee05a4c94acce01c71c5f8dfb2af15dfe5977873b1b4fbde829496ddfd400`。本次只读核对确认报告 hash 与索引相同，两种 V 碰撞二进制/源/27 mesh、APC stage/manifest 当前 hash 均匹配；静态 pair 分类之和为87。以下状态全为 **DRAFT_NOT_EXECUTABLE / 未冻结、未授权调用**，没有预填通过结论。

## 1. 第一个可实施门

**先做 V PCS plain/trace 两个局部目标的工程准备，再冻结一次有限局部资格。** 原 V A02 起终点及其原 collision replay 证书直接复用，不重新选择或恢复被动角、不重新做任务 A、不重跑 R1/R2 数学全集。V NR 的 C++移植可同时开发，先以保存32输入作转移资格；不能直接运行 ABB 物理核于 V。

建议新文件名（只是本计划的精确工程接口，尚未创建）：

- builder / supervisor：`scripts/p4_d080/build_v_pcs_local_v1_draft.py`、`scripts/p4_d080/supervise_v_pcs_local_v1_draft.py`。
- driver / observation：`baselines/p4_full/geometry_consistent/comau_v_pcs_local_driver_v1_draft.cpp`、`comau_v_pcs_observation_v1_draft.hpp`。
- 协议：`configs/p4_d080/v_pcs_local_v1.DRAFT.json`；fresh stage `/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1`，plain/trace 独立子目录；fresh run `20261017_D080_V_PCS_BUILD01`。存在即停止，不能覆盖/重置 claim。实际执行日期变化时新 run 名应在首次冻结前一次确定。
- V NR 后续新核：`baselines/p4_full/geometry_consistent/physical_nr_comau_v_cpp_v1_draft.hpp`；driver 的公开 GD 参数、结果和调用计数接口沿用 V 原 `kdl`，不得改成 ABB 的 L/T_pose参数接口。

builder 仅允许编译；driver 的本项命令集只有固定输入 identify/project/RBS/reconstruct，没有 solve/sample_q 入口。二进制应包含来源/模式标记；编译后0科学调用证据独立于科学运行记录。

## 2. PCS 必须绑定的精确函数

来源均为固定 `ckcComau/industrialScene@ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca`，不是 CKCplanning 或 ckcComau2。

| 函数 | V 原文件/行 | 首项的用途与限制 |
|---|---|---|
| `two_robots::FKsolve_rob(State,int)`、`IKsolve_rob(Matrix,int,int)`、`calc_specific_IK_solution_R1/R2` | `proj_classes/apc_class.cpp` | 直接用已资格 geometry-consistent V stage；完整源分支身份、原物理近似π和Q保留 |
| `identify_state_ik(State q1,State q2,State ik)` | `StateValidityCheckerPCS.cpp:277` | 两端点中心的两角色 branch 由原函数返回并原样保存；role0=arm1主动/arm2被动，role1相反；返回−1为失败，不代换 |
| `IKproject(State&,State&,int active_chain,int ik_sol)` | 同文件`:140` | 首项固定原 branch 投影；保存 input/output/return与实际calc_specific调用，不加入NR或别的分支兜底 |
| `isValidRBS(State&,State&,int,int)` | 同文件`:457` | 原中点投影后执行实际原碰撞；观测原体一次，不绕过碰撞 |
| `checkMotionRBS(State qa1,State qa2,State qb1,State qb2,int active_chain,int ik_sol,int recursion_depth,int non_decrease_count)` | 同文件`:488` | 保留原递归、normDistanceDuo、中点和左右短路次序；原tol=.05、maxdepth150 |
| `reconstructRBS(State qa1,State qa2,State qb1,State qb2,int active_chain,int ik_sol,Matrix&,int iteration,int last_index,int firstORsecond)` | 同文件`:545` | 原真实中点重建与插入次序；保存全部返回和顺序，false不修复、不截掉失败尾 |
| `collisionDetection::collision_state(State,State)` | `collisionDetection.cpp:39` | v3 aligned既定世界基座策略；87活动pair/8mm/原mesh；同时记录native边界，不能把native TCP mismatch改判 |

状态指针重载（PCS源`:472`/`:533`）可作为薄 public API 层一并编译，但局部数学与回溯证据必须能追到上述递归向量函数。精确原签名与源 hash 在 builder 静态阶段冻结，不能用相似函数名匹配多个重载。

原运行采样box来自 `run/plan_PCS.cpp:80–107`，与机械限位分开保存；source collision env为1。原 `RRT_PCS.cpp` 搜索内直接调用特定解析分支并保存主动角色切换，不依赖三参数随机 helper。局部目标不执行 `RRT::solve`；其原搜索源码可按原字节链接/核对，后续完整路径才运行 `setup()`→`solve(ptc)`。

## 3. 已有修复可复用到哪里

| 已有资产/修复 | 可直接复用 | V 仍需独立做的事 |
|---|---|---|
| `spatial_ik_patch.py` 的 comau_v stage | 已资格 CPP `825465213d855f623948c9ee7e263053f67baed7e6907eae4f1549473f516d12`；manifest `0253983631c567e81738bc3a911d84a46d77b816cdfb091938a7e0423b81443b`；原geometry/Q/base/limits不变 | 新SVC编译、局部API和RBS不是旧APC组件证书范围 |
| v3 collision观察修复 | arm1物理TCP从T6+422.7、arm2从T72+400.7；原pair几何和8mm不改 | 新阶段薄观察要保持原PQP参数/聚合结果；T7仍是20mm mesh frame，不能“修成”22mm去改变原CAD |
| A02 V端点 | start候选52/branch3、goal候选22/branch1，主动角不变、合法、aligned clear，原始失败分列 | 不再资格恢复；新入口输入只读这些q，不将其他候选替上来 |
| ABB H 成功break 单因子源码候选 | 可以复用“成功identify后break”的**最小差异模板和逆恢复工具**；V源`:165–194`同样缺break | V helper没有自己的动态资格。ABB H的原预算停止/未完成记录不能当V证书。首项固定分支RBS不调用此helper；另列修复即可，不让它拖住RRT入口 |
| ABB D 的CBiRRT role1 destination单因子 | V `CBiRRT_PCS.cpp:122–142`同一目标变量问题，可复用定位/逆恢复办法 | V未资格；首项RRT路径不修改CBiRRT。后续单独版本，不混入“原体完整不变”声明 |
| Eigen伪逆、进程隔离、claim、source trace、原体hash与依赖manifest工具 | 不变的工程结构和日志格式 | 不照搬ABB的几何、杆、PQP setP、142-call静态计数、L/T_pose数值接口、II证书或V以外端点 |

V五参数 `IKproject(q1,q2,ik,active_chain,ik_nn)`（源`:94`）在role1使用`ik_nn[0]`而写`ik_nn[1]`，需保持为独立待诊断项；不能把H或D修复的通过自动扩为该重载通过。首项不调用它。用户已要求修正随机返回问题，但不授权把任何新分支策略改写为原作者原生成功。

## 4. 最小局部协议应怎样冻结

保存两个A02中心为不可变输入。为得到真正非平凡RBS，需要预先固定一对相异、共用某角色原解析分支的端点；A02中心自身到自身只能作为API一致性，不能作递归正例。

建议 builder 完成后由 root 在静态审查中一次冻结以下**组件测试夹具**，其作用是入口资格，未改变规划算法、机器人、抓持、RBS阈值或正式实验条件：每个中心、每个主动角色，只在该主动臂第1关节预声明±0.05rad，两边均用中心识别的原被动branch解析闭合。两边主动坐标间距0.1rad使该pair不会只由原`.05`短边门直接返回；projection失败/分支不符/限位或碰撞拒绝均原样报告，不替换角度或挑新中心。是否采用这份夹具必须在执行前协议固定；本计划没有构造它们或计算其可行性。

按这个最小夹具的 public API 上限：2中心×2角色×2符号×plain/trace＝**16次固定分支project**；中心identify为2×plain/trace＝4次；4个pair×plain/trace＝8次checkMotionRBS，以及8次reconstructRBS。所有内部FK/IK/碰撞/递归另按真实入口数计数，不把“36个public调用”误说成总科学成本。原机械限位、闭链门1e-5mm/1e-5矩阵、原branch身份、RBS叶距`.05`均不改。

建议运行器的总内部投影入口上限512、独立后审的唯一路径节点上限256，仅作为本次资格资源上限；到上限保存PREFIX/UNKNOWN、未执行尾和全部日志，不能截短路径后给PASS。原RBS_max_depth150保留。最终冻结还须明确每个签名计数包含关系、调用前原子claim、整体进程组watchdog、所有退出路径和独立后审节点去重规则。未冻结这些项不得运行；失败后不得调整上限续跑同claim。

新的观测字段与原调用合并采集：Rbox/Tbox、原物理TCP、pair身份、`CloserThanTolerance()`布尔和PQP API码。既有collision replay不重跑；这批新入口原本就要查的碰撞附带新观察。独立审查须区分“Q/源mesh姿态和控制流一致”与“CAD表面吸盘接触/完整物理几何尚无证据”；不存在证据的层级保留UNKNOWN，不能靠引入自定义工具模型补齐。

## 5. NR 并行转移的确切边界

原V函数链为 `StateValidityCheckerGD::IKproject(State&,bool)`（`:95`）→`kdl::GD(State q_init_flip)`（`kdl_class.cpp:76`）→`get_GD_result()`；局部连接用 `isValidRBS(State&)`（`:175`）、`checkMotionRBS(State,State,int,int)`（`:207`）、`reconstructRBS(State,State,Matrix&,int,int,int)`（`:251`）。保留GD原体副本，仅在独立数值版本GD体内调用物理NR，原SVC递归体/碰撞体保留一次。该版本必须标CORRECTED/RECONSTRUCTED物理NR，不冒称作者原KDL运行。

V独立几何来自 `analyze_comau_native_qualification.geometry(5)/serial_fk` 和 `physical_nr.model_geometry('V')/arm_fk_jac/closure_vector_jacobian/project_nr`：b/各Comau偏置、tool422.7、不同高度基座、偏航−3.1416/2、非平移Q、两TCP实际闭链。C++ ABB核的require_environment目前拒绝V，不能删这个guard后就声称支持V。保持无阻尼Moore–Penrose更新、原单位、最大10000迭代、SVD相对截断1e-12、1e-5门、图异常和限位拒绝语义；不加APC fallback或线搜索。

转移参照直接读取 `20261015_R2_SPATIAL01/V/observations.json`：**数组下标440–471恰为32条nr_reference**，原10输入（fixture0–9）、start_0…10、goal_0…10；已有结果全CONVERGED，trace长度1–4。静态读取确认每条result已包含input/candidate/metrics/trace，不重新计算Pythonoracle。实际未来C++执行仍须独立记录32次NR及内部调用，比较保存输入、首步g/J、trace、候选、状态和边界；数值差异门由已审转移协议复用/明确，不能为了V新输出而放宽。通过后复用PCS局部协议冻结的同一组输入/边，另测原GD API/RBS/回溯；NR资格不依赖RSS或PCS搜索成功。

## 6. 最小预算建议与批准边界

以下均是**帽上限建议**，不是新费用、调用授权、成本pilot或正式预算。优先只冻结第一行工程项；科学项须另有精确输入/协议和独立审查，不能以本报告自动启动。若阶段提前失败不消耗后项。

| 阶段 | 建议墙钟 / CPU帽 | 最大新增工作与停止点 |
|---|---:|---|
| V PCS BUILD01 | 45s / 90s | 两个plain/trace局部工程目标；0查询/0solve/0RNG；fresh namespace与source恢复审查 |
| V PCS LOCAL01 | 30s / 60s | 上节16 project、4 identify、8 RBS check、8 reconstruct；内部投影≤512；全局双时钟停止，不续跑 |
| V PCS独立POST | 60s / 120s | ≤256唯一路径节点的数学/branch/界/native+aligned源策略；未验证尾保持UNKNOWN；不改原回溯路径 |
| V NR BUILD01 | 45s / 90s | V物理核和原GD薄接口；0查询/0solve；保全原KDL源码 |
| V NR TRANSFER01 | 15s / 30s | 32个固定保存输入；不重跑Python参照、不换seed/输入；到帽保留前缀 |
| V NR转移独立POST | 30s / 60s | 保存g/J/trace/结果与来源/计数归约；不重算原模型。原GD/RBS动态局部项待转移通过后单冻 |
| **上述帽合计** | **225s / 450s** | 未执行，不能扣账或宣称是实际成本；不含后续solve/全路径验证 |

本次读取基线为V25实际账SHA `ce612e7c9706666a338aae6deda581274f1aadb229e2be999cd6ee836499e64a`，已有43 execution=32科学+11工程，charged839.3257053759941wall/771.588923CPU；R2剩额**上界**2760.674294624006wall/6428.411077CPU。D080 scope SHA `edbf914187f449d0ce145987cbf38bc7d668c69b536f806a86b28b6da1bded41`，budget overlay SHA `7fe6eb5eaaf9002c7e1f62192acb472788225bd6207dc181a5d41baca4f52ac7`。未来冻结必须读届时最新实际账和overlay，扣所有并行新增项自身成本；本页剩额不是保留给V的独占额度，不重置原UNKNOWN时间尾。

旧ledger22500字段及旧VI974/974保持原字节，执行协议另绑定D080 18000、VI未来禁止、正式统计未授权。单次原RRT/GD solve及完整路径独立审查**不在这225/450帽中**，只能在前置门过后单冻预算；不把它们随编译自动触发。若需新增科学方法、改变几何/阈值、扩大总预算、启动正式18k，则提交用户明确批准。这里没有新连接器、RSS采样设计、VI工作或Isaac拓展。

## 7. 向下一位实施者的交接

先将V0固定source/hash/输入与两target builder写成可逆工程稿，做一次合并静态审查；源同一函数只能有一个body副本，H/D等有实质差异的版本须逆恢复比较，不能称完整原body未改。再冻结局部夹具及计数/预算。独立后审完成一项才更新实际证据和账本，保留旧失败与原始输出。当前V动态新增资格仍0、端到端路径仍0、正式统计仍0/18000。
