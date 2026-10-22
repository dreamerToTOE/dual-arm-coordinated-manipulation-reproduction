# P4：原论文范围、D082批准范围与实际证据（2026-10-22）

本表继承211行原论文义务，原248列逐单元格保持；追加9列D082范围、状态、实际证据、限制及统计口径。原始矩阵有P4-T01–T30共30条主义务，全部保留（不是29条）。CSV读取回验确认211×248个历史值与列名/次序完全相同。

继承来源：`reports/P4_D080_III_RRT_PCS_PHYSICAL01_ORIGINAL_VS_APPROVED_VS_ACTUAL_20261019.csv`；SHA256 `99aa8a306943e63cd77e7f8f6d9fa28a356fffe0c20c131013e198154bd30808`。独立主任务oracle：`results/20261022_D082_independent_planar01/summary.json`；SHA256 `867755cda518eb7abb8776d827733604266e5be8440aed64fd4f7fff5ceffbc1`；状态`PASS_DISCRETE_WITH_STRATEGY_MIDPOINT_REFINEMENT`。

当前批准要求是核心算法与一套真实端到端虚拟任务。平面20R主任务50次paired pilot中26条成功路径已独立核闭链、界、碰撞、分支及加密策略中点；24次TIME_LIMIT保留。NR10/10、兼容fixed0 10/10、fullPCS6/10、fixed16 0/10、RSS0/10。完整任务的离散数值证据通过，不等于RSS规划已成功、原论文全部曲线相同或六环境完整复现。

原TableI为22500次；D080历史目标18000次由D081取消；当前正式原TableI次数0。当前比较为50次预注册paired pilot（5方法×2场景×5种子），此前20次探索pilot单列，不能合并成500次/单元的正式统计，也不把重验已有路径计为新规划。

空间II四条完整路径与III一条aligned离散路径只读复用；III最终路径4次角色切换。平面6条成功PCS路径的最终划分切换全部0，失败树仅1条真实父子切换。fixed16起终点分支不兼容，仅属结构性负对照，兼容fixed0才是公平的固定划分基线。未观察到PCS优于fixed0。

RSS真实失败：72奇异请求/2304候选全部IK_UNREACHABLE，尚无接受的闭合奇异目标；根因UNKNOWN，保留rank2与两侧分支桥的数学正例，但不把正例代作RSS规划成功。Fig3各m使用不同状态池且含不同自配对比例，当前曲线不支持划分数的因果优势。原m20、500000投影和50000合法点对未做。

VI只读归档，不新增科学调用；V5只是未授权source的工程候选。所有路径均为有限离散安全范围，无连续CCD；空间原碰撞pair/8mm容差/杆件模型和native TCP不一致继续保留。

## 30条主义务

|ID|原义务|D082当前状态|实际结果与限制|
|---|---|---|---|
|P4-T01|完整闭链构型/有效空间/各类人工奇异及可见性定义|algorithm_partial|闭链定义、20R几何/限位/障碍及独立数值oracle均有实现。 定义和重建数值证据不覆盖原论文全部模型与理论证明。|
|P4-T02|APC被动链解析IK/所有可达分支、成功与失败采样|algorithm_partial|重建APC解析3R、双IK分支及投影真实成功/失败；原空间II/III已有解析分支资格。 平面只实现17个连续正长3R划分，不能替代原20划分。|
|P4-T03|NR全链Jacobian/SVD投影及数值收敛/失败|algorithm_partial|768条NR投影成功768条；保留迭代、残差、耗时和独立FD数学检查。 不是原50万样本/全部空间NR栈的完整重复。|
|P4-T04|APC vs NR 500000随机样本：投影成功率、耗时分布及成本；原原环境设定|reduced_scale_proxy|APC/NR各768投影，共1536条原始记录。 原500000随机样本未执行；模型和采样分布有差异。|
|P4-T05|RBS递归中点/IK分支/碰撞局部连接、失败与精度|verified_discrete_reconstructed|50次paired pilot中26条成功全路径经独立oracle：2142保存点+6348策略中点，2116叶全通过。 只验证离散点与固定策略加密，未证明连续扫掠安全。|
|P4-T06|可见域、独立/依赖被动链的统计上界及理论适用条件；解析+模拟核对|theory_and_proxy_partial|局部可见性有RSS/PCS/NR各240对真实RBS数值。 有限抽样不证明原文可见域概率界；可比性与假设必须逐项保留。|
|P4-T07|RSS合法人工奇异目标生成与跨IK分支路径|algorithm_partial_rss_planning_failed|RSS paired规划0/10；72奇异请求、2304构造全IK_UNREACHABLE；另有rank2和两侧分支桥数学正例。 无接受闭合奇异目标；根因UNKNOWN，不以手工桥替代RSS规划成功。|
|P4-T08|PCS变换多个被动链、选择共有可连接IK分支、搜索树和解路径切换证据|algorithm_partial_no_pcs_advantage|fullPCS6/10、fixed0 10/10、fixed16 0/10；仅失败树1条真实0→16父子切换；6条成功PCS最终路径切换0。 fixed16端点分支不兼容，仅作结构性负对照；fullPCS未优于公平fixed0。|
|P4-T09|NR与PCS/RSS在共同规划栈和独立原生栈中的真实代价比较|matched_proxy_pilot_only|同重建场景/种子/公共预算：NR10/10、PCS6/10、fixed0 10/10、fixed16 0/10、RSS0/10。 计时为重建Python/GEOS；不同方法随机消耗和计算成本不同；未复现全部原生栈。|
|P4-T10|原环境I平面20R障碍/关节界/精确起终点、奇异跨分支|verified_reconstructed_virtual_task|平面20R E0/E1完整起终点任务及26条独立合格路径，真实障碍和限位，保留24次TIME_LIMIT。 属于重建平面任务，不冒称原环境I端点/障碍完全相同。|
|P4-T11|原环境II双ABB IRB120搬杆跨杆障碍，刚性闭链|reused_qualified_spatial_discrete|环境II四条完整路径：RRT/PCS177、RRT/NR393、CBiRRT/PCS413、CBiRRT/NR689节点。 A01重建端点、aligned原离散策略，native TCP/杆件/省略pair等限制保留。|
|P4-T12|原环境III双ABB IRB120窄通道|reused_qualified_spatial_discrete|环境III RRT/PCS649节点、15里程点、14边、4次最终路径角色切换；绑定/hash恢复通过。 aligned重建离散证据；649个native TCP均不一致，无连续CCD。|
|P4-T13|原环境IV双Comau NJ-16搬杆/多障碍|preserved_incomplete_not_required_full_env|保留环境IV原模型、端点/腕部资格与失败；D082未新增完整规划。 原IV完整任务未复现，不把组件资格当完整路径。|
|P4-T14|原环境V双Comau NJ-16吸盘抓箱输送带至安装位|preserved_failure_v5_engineering_only|保留V source/碰撞失败；V4残缺前缀无完整目标路径；V5仅工程候选。 V5新source未授权且未执行；不将stdout solved当独立合格轨迹。|
|P4-T15|原环境VI三Comau抓环绕两杆、多闭环和独立约束|archived|沿用历史VI数学/失败/预算记录，新增调用0。 原实验未完成部分保持；974/974预算及UNKNOWN不改判。|
|P4-T16|所有六环境起终点需要跨越奇异构型；可行路径/分支见证、碰撞/限位|partial_endpoint_and_path_witnesses|II四条及III一条保存空间路径；平面任务26条独立合格路径。 原六环境/原始端点跨奇异结论未全部核实，IV/V不补成功、VI归档。|
|P4-T17|RRT / Bi-RRT / SBL × RSS/PCS/NR 同环境算法比较|reduced_planner_comparison|平面重建单套双树规划栈完成50次paired pilot；空间II有RRT/CBiRRT已有路径。 未执行所有RRT/Bi-RRT/SBL×三方法×全环境，不能按完整组合解释。|
|P4-T18|环境II–VI × 三规划器 × 三投影方法：原500次/单元、1000秒上限、超时删失|formal_scale_cancelled_proxy_pilot|原TableI分母22500保留；D080历史18000已D081取消；本次比较为50次paired pilot。 正式原TableI试验仍0；20次探索pilot单列，不能合并为500/单元。|
|P4-T19|环境I被动链数m=1,2,3,7,20与NR：局部连接成功率-距离、运行时间-链数|fig3_population_confounded_partial|m=1,2,3,7,16各180对保存RBS记录。 m组重新生成状态池，m1有19/180自配对、m16无；不可因果归因于m；原m20缺失。|
|P4-T20|环境II可见份额、调优步长、采样/失败、采样占时、局部连接成本、树/路径节点|table_ii_proxy_metrics_partial|paired50记录samples、失败/超时、树节点、局部调用、投影数、路径长度与耗时。 这些是平面proxy；无原空间II原TableII各算法调优/完整成本口径。|
|P4-T21|约50000合法点对局部连接概率、按构型距离分箱与方法对比；核对图注I和正文II差异|reduced_visibility_proxy|RSS/PCS/NR各240对，共720行真实局部连接记录，距离分箱可复核。 原50000合法点对未执行；图注I/正文II与重建模型差异单列。|
|P4-T22|投影前后邻点配置距离绝对变化随初始距离关系；APC对NR|fig5_proxy_partial|APC/NR各384行投影前后距离变化，共768行。 扰动/参照邻点定义与原图条件不完全一致；不能原样同条件比较。|
|P4-T23|移除障碍前后 NR/PCS/RSS 在各空间环境表现；验证复杂障碍是否消弱NR可见性优势|obstacle_ablation_proxy_negative|E0稀疏/E1杂障使用相同端点与paired种子；成功率相同，无PCS优势。 不是原空间各环境逐个移除障碍实验；现路径指标高度相似，不能宣称复杂窄通道优势。|
|P4-T24|每方法单独调优规划步长/距离和RSS γ=0.2；与统一参数公平诊断分开|common_budget_not_original_tuning|保存统一pilot预算/分辨率/随机种子，RSS奇异概率0.2。 未逐方法调优步长；不是论文最优参数性能排名。|
|P4-T25|独立机器/OS/OMPL/KDL/PQP、作者开源版本与我们的运行/许可差异|traceable_reconstruction_partial|源码、配置、raw gzip、50-artifact manifest、独立数值与历史空间hash链接完整。 保留Python/GEOS与原OMPL/KDL/PQP、几何及作者条件的差异；作者raw到论文统计仍未全闭合。|
|P4-T26|局部路径可见性、平滑度、碰撞几何连续性、采样投影成本在复杂空间场景联合解释|discrete_safety_and_cost_partial|真实约束/碰撞与RBS、局部调用、投影成本、净空和路径曲线均可核。 无连续CCD、动力学/时间参数化或空间复杂场景完整统计。|
|P4-T27|空间PCS独立和依赖被动链及多被动链数上限、解析IK可行性；三臂环结构限制|model_applicability_partial|区分平面17划分与空间双臂角色切换；III最终路径4次角色切换。 三臂独立/依赖多闭环限制未解决，VI归档；不能从平面划分数推广空间。|
|P4-T28|NR易推广、PCS障碍优势和分析限制在与原文一致的困难条件下是否成立|negative_findings_no_original_advantage_claim|当前pilot NR与兼容fixed0全成功，PCS6/10，RSS0/10，明确报告负面发现。 样本小、场景弱、fixed16不兼容；不证明原PCS障碍优势或RSS方法本身失效。|
|P4-T29|逐方法NR/RBS/PCS/RSS应用双FR3 Benchmark A/B、接口/依赖/风险及未来实证|conceptual_future_application_only|D082报告最后章讨论双FR3接口、约束/Jacobian/IK/碰撞前置与未来研究。 本阶段不实现FR3适配，不声称机器人/Isaac实证；完整性以最终报告为准。|
|P4-T30|全部环境 APC/NR 投影后分布近似相同与流形覆盖主张|original_distribution_claim_unverified|有限投影成功率/距离记录保存。 未建立全部环境APC/NR输出分布近似相同或流形覆盖的统计证据。|

## 211行状态分布

|状态|行数|
|---|---:|
|algorithm_partial|5|
|algorithm_partial_no_pcs_advantage|2|
|algorithm_partial_rss_planning_failed|2|
|archived|21|
|author_raw_to_paper_lineage_incomplete|1|
|common_budget_not_original_tuning|5|
|conceptual_future_application_only|1|
|definition_and_reconstructed_illustration|5|
|discrete_safety_and_cost_partial|1|
|fig3_population_confounded_partial|10|
|fig5_proxy_partial|3|
|formal_scale_cancelled_proxy_pilot|1|
|matched_proxy_pilot_only|1|
|mathematical_bridge_only|1|
|model_applicability_partial|1|
|nearest_neighbor_cost_not_isolated|1|
|negative_findings_no_original_advantage_claim|1|
|no_qualified_spatial_nr_path|1|
|no_qualified_spatial_rss_path|4|
|not_available_original_m20|2|
|not_executed_original_cell|13|
|not_performed_matched_fig3_nr|2|
|not_performed_original_chain_count|14|
|not_performed_spatial_obstacle_removal|2|
|not_performed_spatial_partition_ablation|2|
|obstacle_ablation_proxy_negative|2|
|original_distribution_claim_unverified|4|
|partial_endpoint_and_path_witnesses|1|
|preserved_failure_v5_engineering_only|1|
|preserved_incomplete|40|
|preserved_incomplete_not_required_full_env|1|
|reduced_planner_comparison|1|
|reduced_scale_proxy|4|
|reduced_visibility_proxy|4|
|reused_qualified_spatial_discrete|2|
|reused_spatial_discrete_rbs|3|
|reused_spatial_math_or_path|6|
|single_proxy_planner_not_original_combination|9|
|single_spatial_path_reused_no_formal_statistics|5|
|table_ii_proxy_metrics_partial|11|
|theory_and_proxy_partial|1|
|theory_explained_not_fully_numerically_proved|7|
|traceable_reconstruction_partial|1|
|verified_discrete_reconstructed|4|
|verified_reconstructed_endpoints_not_original_I|1|
|verified_reconstructed_virtual_task|1|

合计211行。各状态是本轮D082实际映射，不回写历史列的成功/失败；`partial`、`not_performed`、`archived`均不算原论文FULL。

## 可复核入口

- 主任务独立数值资格：`results/20261022_D082_independent_planar01/summary.json`。
- 空间保全与q12绑定：`reports/P4_D082_SPATIAL_RECOVERY_20261022.json`。
- 机制/失败根因与可比性：`reports/P4_D082_ALGORITHM_FINDINGS_20261022.md`。
- 真正父子切换及最终路径统计：`results/20261022_D082_saved_analysis01/summary.json`。
- 七幅真实中文图与原数据：`reports/p4_d082_research_assets_20261022/manifest.json`。

生成命令：`python3 scripts/p4_d082/build_coverage_20261022.py`。为保全已有交付，脚本以排他新建方式写入；再次生成须先指定/版本化新的输出文件名，不能覆盖旧矩阵。
