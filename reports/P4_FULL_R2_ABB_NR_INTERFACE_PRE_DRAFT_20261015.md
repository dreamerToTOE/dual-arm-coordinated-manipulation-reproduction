# R2 ABB 普通 NR：原 GD 接缝单目标工程 PRE 草案

2026-10-15。**DRAFT / ZERO_QUERY_ZERO_COMPILE / NOT_FROZEN**。本报告只申请一个隔离工程构建，不是已运行科学资格，也不授权任何 solve。Q1 已完成固定64数值移植资格，独立 saved-only POST 为14272/14272；不重新运行Q1/R0/R1。

## PRE-TASK REPORT

- Task：将已经Q1合格的II/III C++ physical NR接入作者原`kdl::GD`入口，构建可供原SVC/RBS/回溯局部资格使用的单一binary。
- Scientific objective：工程只证明确切源码能编译/链接；闭合、碰撞、原局部行为必须由另一份冻结科学协议验证。
- Minimum sufficient evidence：一次确切源码/编译命令、退出码、binary/source/mesh哈希、原GD保全副本、原body观测映射、完整工程预算及失败日志。
- Scope：一个fresh隔离stage、一个target、一个唯一Eigen数值TU；link原`RRT_NR`，当前driver只允许local操作，不构造搜索器。
- Non-goals：0 query/FK/J/NR/IK/PQP/RBS/solve/RNG；不重写solver、RBS或planner，不改原`sample_q`未到达漏洞，不追加RSS/VI候选或公平速度比较。
- Attempt budget：一次45秒wall/90秒CPU，取R2总3600/7200余额min；fresh claim、结果、stage，失败不重试/不清理失败前缀。
- Preferred method：复用既有RRT_PCS builder的资产校验、body定位、exclusive JSON、live-process CPU、claim/manifest/watchdog机制；复用现有PCS trace/PQP wrapper及JSONL transport形状。
- Fallback：无自动fallback；构建失败保留compile日志和原stage，先根因审查，不扩大预算盲试。
- Stop/escalation：Q1/独立POST或原资产/源码/协议不匹配阻断；编译/墙钟/聚合CPU失败保存prefix。工程成功仅`BUILT_NOT_QUERIED`，不能转成资格PASS。
- Files expected：本PRE、builder、轻量observation header、唯一kernel TU、local driver、saved-input inventory和工程配置草案；不修改历史bound文件/账本。
- Validation：AST、纯字节/保存标量describe/validate、原body保全静态检查；root独立工程二审和提交冻结后才能执行构建。
- Need user confirmation：no（用户已授权的有限资格恢复准备；正式规划与原文统计仍须单独冻结和成本审查）。

## PRIOR-ASSET CHECK 与复用映射

`docs/POST_TASK01_REUSE_MAP.md`及631b1f工程资产审计继续适用。既有`physical_nr_abb_cpp_draft.hpp`逐字节复用为DIRECT_PORT；Q1证明固定64下C++/Python数值移植，不证明原KDL迭代轨迹或全局投影能力。原KDL头/其他成员函数、`StateValidityCheckerNR`、`RRT_NR`是作者DIRECT_PORT；现有R2 corrected `collisionDetection`/PQP几何和原离散配对策略复用。现有PCS trace、RRT_PCS builder的工程函数及JSONL形状为THIN_ADAPTER。独立物理oracle和v3 aligned碰撞是后续TEST_ORACLE。14维工程projection、FR3/MoveIt/Isaac仅REFERENCE_ONLY，均不迁入论文机构。

唯一新数值TU为`abb_nr_interface_kernel_draft.cpp`，只有此TUinclude不可改的physical NR core。force-include轻量`abb_nr_interface_observation_draft.hpp`仅声明seam、保存事件和引用已有PCS logger，不使五个作者TU重复实例化Eigen。编译使用Q1同一绝对`/usr/bin/x86_64-linux-gnu-g++-11`及`-std=c++17 -O1 -g0`；逐SHA重新核对Q1 build manifest中379个compiler/Eigen/nlohmann头/库资产并纳入本轮binding。link现有OMPL/KDL/PQP和原RRT_NR；构建不启动binary。一个binary支持plain/trace，避免native/R2×plain/trace多target。原native失败与已保存历史独立保留。

## 真实来源、允许差异与保全

只读template为`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/geometry_consistent_plain`；新stage为`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_nr_interface_v1/physical_nr_observed`。template manifest及其所有旧source/mesh/binary资产均沿既有builder校验，另明确绑定原作者`CKCplanning@909bd72fff778aca8682c96f9eb86ae4eb75557b`的kdl/SVC_NR/RRT_NR六文件。当前六文件template与作者字节完全一致。不得改旧stage、旧作者快照或旧结果。

只允许以下改动，每项进入manifest：

1. 新stage的`kdl::GD(State q_init_flip)`唯一body替换为`physical_gd`调用。替换前完整`kdl_class.cpp`复制到新stage `preserved_originals/proj_classes/kdl_class.cpp`，保存完整SHA及原GD body SHA；旧文件和全部原始失败均保留。kdl header、constructor、get_GD_result及其他成员函数不变。
2. 原SVC vector `IKproject`、`isValidRBS`、vector `checkMotionRBS`、vector `reconstructRBS`完整body逐字节保留一次，外面只加entry及post-return观测lambda。无新碰撞/模型查询。
3. 既有corrected collision完整数值/配对/返回策略保留，原142个`PQP_Tolerance`调用站点改用已有`p4pcs::query`（`res[116]`因环境分支有重复站点，不能误称116站点）；外加完整`collision_state` body entry/post-return观察。
4. `RRT_NR.cpp/.h`逐字节不变并link，不改搜索/树/goal/save2file/删除temp行为。**当前无solve入口**；未来要运行必须另建薄solve driver与完整state-level回溯Confs JSONL观察、明确temp保全I/O偏差、独立PRE与claim。不得用当前vector布尔trace冒充已具完整planner路径记录。

原GD为nonvirtual，不能靠子类同名方法误称已转接；此处明确在原member body内调用。函数收到原物理12角，核对D/L与driver环境II(900/300)、III(1200/500)，且原`include_joint_limits=true`。唯一数值调用为已合格core `project_nr`；仅`CONVERGED`返回true并更新原`q_solution`，随后原SVC自行取`get_GD_result`并检查原碰撞。失败候选保留但不覆盖q_solution。不对结果再次倒序、截零、按2×3.1416 wrap。原IK_counter和IK_time语义保持为顶层投影次数/CPU时间，driver每请求调用原`initiate_log_parameters`清零。

数值参数沿Q1/default：最多10000次更新、内部120秒、1e-5mm/旋转矩阵1e-5、相对SVD cutoff1e-12、收敛后真2π周期图及原3.1416机械限位；plain/trace均`detailed_trace=false`。此次不重放每步谱/J；Q1详细逐步对照证据单独绑定。普通NR能改变所有12角，不施加PCS固定active/branch门。

## Local JSONL接口与事件契约

binary参数：`p4_abb_nr_interface ENV MODE RUNTIME`。ENV仅II/III，MODE仅plain/trace。RUNTIME由科学runner新建，仅含绑定simulator网格；driver拒绝已有`paths`，不复制原路径。stdin每行一个JSON对象：

```json
{"id":"II_0","op":"project_q12","q12":[12.0]}
{"id":"edge0_rbs","op":"rbs","qa12":[12.0],"qb12":[12.0]}
{"id":"edge0_reconstruct","op":"reconstruct","qa12":[12.0],"qb12":[12.0]}
```

上例`[12.0]`仅表示字段位置；真实请求必须精确12个有限角。driver仅接受这三种op。project调用原`IKproject(q,true)`；rbs调用原vector入口(depth0,nondecrease0)；reconstruct以Confs={qa,qb}调用原vector入口(iteration0,index1,first1)，与原state wrapper相同初值。`.05`、depth150、中点全12算术均值、左后右递归、插入索引与返回体均不变。

stdout响应前缀`P4_NR_RESPONSE `；字段为schema=`P4_ABB_NR_THIN_V1`、request/id/op/environment/mode/status/returned。project始终保存SVC返回后q12（false亦存）；reconstruct始终保存完整path_q12/false前缀，异常/kill未返回Confs为UNOBSERVED，保留已发事件，不推造完整path；只有响应实际含path_q12时才确认该前缀已保存。rbs不制造path。额外保存solve_calls=0/rng_calls=0、observed_counts、gd_completed_candidates、observer_errors、source_log_counters。原source stdout转stderr，JSON由nlohmann输出round-trip binary64。

trace stderr沿用`P4_PCS_TRACE `，kind为nr_gd/nr_project/nr_valid_midpoint/nr_rbs/nr_reconstruct/collision/pqp，保留entered/completed/id配对。GD完成候选含input_q12/candidate_q12/status/returned/accepted_updates/metrics，有限失败也保存。原源log粗计数两mode可见，plain低层递归/PQP事件未观测，不能把trace计数或帽当plain已发生次数。trace每请求外部帽GD/中点/碰撞1024、RBS/回溯2049、PQP131072；触帽抛出资源停止并保存UNKNOWN前缀，不能改成普通false。plain由同一个父runner墙钟/聚合CPU watchdog约束。obs错误保留源已返回结果后停止后续科学，不在原源内部改布尔判定。

fixed-input inventory逐字复制4个A01和首PCS路径全部4milestone/3边；3边原full12 L2为2.525929452013416、2.756491973773139、0.7598746804749721，均非`.05`捷径。这里只做保存标量算术，没有求FK/J/NR/碰撞或生成新fixture。局部科学由另一份`P4_FULL_R2_ABB_NR_LOCAL_INTERFACE_PRE_DRAFT_20261015.md`及runner负责，拟60wall/120CPU、最多20顶层，工程成功不自动批准科学。

## Budget、冻结条件与证据边界

每次describe重读所有现有R2 `execution.json`自有wall/CPU，用math.fsum一次计入并绑定SHA；不存在可复用的“剩余VI预算”：VI累计974/974、余0，本工程新增0。工程recipe own-source、Q1 execution/独立POST、template/作者六文件及库资产全部绑定；执行只接受已提交、字节精确、reviews全true的冻结副本。新claim/output/stage任一已存在即拒绝。构建包括复制、instrument、编译、等待、hash与日志，watchdog监控process group live CPU；失败不运行binary，保留日志/partial stage。SIGALRM解除后的证据收尾实际wall/CPU仍纳账，不伪称资源帽绝对零超出。

通过仅`BUILT_NOT_QUERIED`。其后local应按全部固定请求/完整节点/失败保全验证，原RBS正常拒绝不等于论文理论错；至少一个真实非平凡成功只支持有限接口及下一规划资格门，不支持全局规划或性能。后续若进入原RRT，已静态核对原`plan_NR.cpp`：paper II/native1 range2.6、paper III/native2 range0.8、resolution0.1、goal bias默认.05、原12维sampler box/q6±3.1416及恒true validity callback；须另冻结seed/短时pilot/完整路径资格，不沿PCS .02或分支门。

完整211条原文义务、TableI0/22500、500000投影、约50000点对、三planner、Fig3–5/TableI–II、复杂窄通道/固定链消融/被动链数量/局部可见性保留。P4完成后的中文Word/PDF与双FR3吸盘/装配适用分析及用户审查最新范围表要求保持，不自动P2/Isaac。
