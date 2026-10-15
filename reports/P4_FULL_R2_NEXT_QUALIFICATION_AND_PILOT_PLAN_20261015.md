# P4 R2 后续资格与成本 pilot 接续清单

2026-10-15。**只读审计及方案，未冻结为可执行协议；本审计未编译、未运行科学调用、未提交。** 审计期间主代理 HEAD 从 `b686e7b`经`1a4bb73`推进到`57ca473`，并完成CENTER_IMAGE01；使用已有 R0/R1/R2 证据，不重新初始化或重做已完成试验。所有预算是上限方案，不是新增授权，也不表示全部前置门已通过。

## 1. 应从哪里继续

最早未通过的当前项目是 VI RSS 固定 construction219/643 的**原始奇异中心接入连续性**。Q2 的36个构造节点通过闭合、限位、真实秩、分支与原 source-policy 碰撞检查；四半段在32个 depth3 叶上均未达到原全18坐标距离 h=.0025，因此严格桥仍 UNKNOWN。主代理新完成CENTER_IMAGE01固定中心一阶诊断，四条主动弦方向均有非零被动rank5像空间残差；这不证明全局连续路径不存在，未构造fiber连接或新路径，仍不升级Q2。独立复核继续处理；本报告不把节点资格、源程序 .05 提前返回、或 .35 奇异捷径当严格桥通过，也不建议盲目加深/换中心/缩扰动。

并行可进行的下一项是**复用作者 planner/RBS 的薄接口与版本化数值修复整合**，先形成可审查源码和固定输入，再逐 gate 资格。现有数学组件通过不意味着六环境三方法九种搜索组合已就绪。特别是：

- 作者原始12端点闭合 FAIL 保留；A01+A02得到的12个 RECONSTRUCTED 端点只达到原离散 source-policy 资格，没有起终点可连接见证或完整物理网格/CCD证明。
- IV 新24个微小输入的原full12 NR全部合格，只证明这一有限局部组；旧6个限位拒绝和3个正控FAIL不改。
- II/III/V旧700固定RSS目标、5600支中19目标48分支只达数学资格；II/III mode0各0/100的失败保持，I/IV没有相应已运行RSS目标组。肩部退化集合的覆盖缺口保持。
- 所有正式 Table I 单元仍0/22500；本报告没有新增规划成绩。

## 2. 复用资产和实际构建状态

权威固定作者版本、文件SHA和既有接口分别见`configs/p4_full/author_source_manifest.json`、`configs/p4_full/build_interface_manifest.json`、`reports/P4_FULL_BUILD_INTERFACE_AUDIT.md`。后者为R0时点记录，不能把其中NOT_EXECUTED误当当前R2没有组件，也不能把当前batch存在误当整套planner通过。

作者资产根为`/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/`。此次按六个所用目录清点，**没有 CMakeLists.txt，入口为 makefile**。不引入一套新规划架构或用FR3代码代替作者模型。

| 当前已有资产 | 可复用用途 | 不能据此声称 |
|---|---|---|
| `build/p4_full/20261015_R2_SPATIAL01/{abb_batch,comau_iv_batch,comau_v_batch,comau_vi_batch}` | R2解析FK/IK batch，stdin `F arm q6` / `K arm branch T16`，ABB须`--env II/III`；独占新输出 | 不含KDL、RBS或搜索器，不能启动规划 |
| `baselines/p4_full/geometry_consistent/planar_geometry.py`及233项资格、56项NR资格 | 原物理循环20R、20标签/真2π解的解析oracle和NR资格 | 不是合格C++20R planner或公平速度基准 |
| `physical_nr.py`及保存原生/独立FK/Jacobian数据 | 原伪逆法的独立NumPy参考；VI12×18同时闭合 | 不能拿Python NR对C++ APC作投影效率结论 |
| 碰撞v2/v3，`collision_adapter.py` | 直接复用已编译PQP及原平面函数；每次保留native/aligned和TCP观测 | 不能推断漏列碰撞对无碰撞、真实杆面或连续CCD |
| VI旧`pgd`/`ppcs` ELF | 原资产来源记录、静态检查 | 不是本机R2构建通过或可运行资格 |
| `baselines/p4_comparison/` | 原独立简化20R两划分比较的历史参考及日志组织 | 不是作者原20R全部20划分；不能把旧结果迁为I的原场景成绩 |
| `baselines/p4_closed_chain/` | 历史FR3算法组织参考 | 不能把14维FR3/旧阈值/旧FCL网格植入六环境 |

VI旧ELF和作者快照同字节：`pgd` SHA256 `5690f0295d24847b752c44f75192d2054afcaee91bca7b4294c8be346f507235`，`ppcs`为`f3065d5ba0da4b565418117de94ab300ed42a03e672c745abc9f9a12b19aa183`。已有VI RSS语法资格`20261014T154529Z_VI_RSS_BUILD01`真实结果是FAILED_COMPILE，不能再执行同一编译来发现相同缺陷。

最新碰撞观察应显式指定v3 manifest，SHA256 `c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388`；它复用I/ABB/VI的v2二进制，只替换IV/V TCP观察。`collision_adapter.py`默认仍指v2，**不显式指定v3会重新遇到已查明的IV/V观察问题**，不能当新科学失败。不得重建、改网格或改原查询对来绕过此问题。

## 3. 六环境 × 方法 × 三规划器源码清点

下表每行三项依次为RRT / Bi-RRT / SBL，均指**源码存在**。除已失败的VI RSS语法资格外，尚无本轮整合planner构建/模型/RBS共同通过证据。三规划器源码存在不等于可运行；未作编译的潜在移植问题保持UNKNOWN。

| 环境/作者仓库 | 方法 | 三搜索器源 | 现有入口与最早缺口 |
|---|---|---|---|
| I `planar_ckc@e5edcb5` | PCS | `RRT_pcs / CBiRRT_pcs / SBL_pcs` | `plan_PCS`+SVCPCS+APC；把合格通用循环3R数值接口接到原20标签后，资格RBS所有划分 |
| I 同上 | NR | `RRT_gd / CBiRRT_gd / SBL_gd` | `plan_GD`+SVCGD+KDL；原坐标失败与新物理NR分开，C++数值等价和RBS待证 |
| I 同上 | RSS | **三个均没有公开RSS入口** | HB不是RSS；旧简化两划分RSS不能直接移植冒称原生。若要原模型RSS，需独立重建方案/分支连续性与新科学决定 |
| II `CKCplanning@909bd72` | PCS | `RRT_PCS / CBiRRT_PCS / SBL_PCS` | `plan_PCS`；修复APC整合、两主动角色/共有支RBS、源碰撞资格 |
| II 同上 | NR | `RRT_NR / CBiRRT_NR / SBL_NR` | `plan_NR`；原KDL坐标与物理NR分别版本化；全12 C++等价、RBS待证 |
| II 同上 | RSS | `RRT_RSS / CBiRRT_RSS / SBL_RSS` | `plan_RSS`；48支中本环境18支待碰撞/桥；mode0 0/100不可删除；肩部覆盖和SBL概率差异未解 |
| III 同仓库 | PCS | 同II三个PCS源，独立env=2 | 距离1200mm/杆500mm；不得拿II的900/300或障碍编号替换；两角色RBS待证 |
| III 同上 | NR | 同II三个NR源，独立env=2 | 独立环境参数和全12原闭合NR、RBS资格 |
| III 同上 | RSS | 同II三个RSS源，独立env=2 | 本环境22数学支待碰撞/桥；mode0 0/100和肩部缺口保持 |
| IV `ckcComau2@8008934` | PCS | `RRT_PCS / CBiRRT_PCS / SBL_PCS` | `plan_PCS`；v3观察合格，原符号/支补丁整合和两角色RBS待证 |
| IV 同上 | NR | `RRT_GD / CBiRRT_GD / SBL_GD` | `plan_GD`；24局部组已过，C++等价/RBS未过，不重跑旧±.01组 |
| IV 同上 | RSS | `RRT_SG / CBiRRT_SG / SBL_SG` | `plan_SG`即RSS；原wrist-only构造尚未运行，原采样碰撞注释/奇异族接入待查 |
| V `ckcComau_industrialScene@ef6e9c4` | PCS | `RRT_PCS / CBiRRT_PCS / SBL_PCS` | `plan_PCS`；保留箱体/吸盘/输送带Q变换，v3观察，所有角色RBS待证 |
| V 同上 | NR | `RRT_GD / CBiRRT_GD / SBL_GD` | `plan_GD`；物理full12 NR到原搜索器的C++整合/RBS待证 |
| V 同上 | RSS | `RRT_SG / CBiRRT_SG / SBL_SG` | `plan_SG`；原wrist-only100目标中8数学支，待碰撞/奇异桥；不擅自扩大为Comau三mode |
| VI `ckcComau3@25488a8` | PCS | `RRT_PCS / CBiRRT_PCS / SBL_PCS` | `plan_PCS`；全18维、三个主动角色和双被动支对、两闭环RBS待证 |
| VI 同上 | NR | `RRT_GD / CBiRRT_GD / SBL_GD` | `plan_GD`；原GD12+IK3和独立full18同时伪逆分开；全12×18约束C++等价/RBS待证 |
| VI 同上 | RSS | SG三个文件存在；默认main/makefile只接Bi-RRT | public SVC未声明q3/dsg2、2/3臂接口/State/Matrix和递归签名缺项；RRT/SBL默认allocation注释。Q1/Q2独立重建仅候选/桥资格，不是完整planner |

所有方法另需原`collisionDetection.cpp`；I另需原`verification_class.cpp`。保留CKCplanning原run时还引用PCS/NR的PRM单元，薄harness可直接分配原RRT/Bi-RRT/SBL以免链接无关PRM。OMPL1.7、KDL1.5.1、Eigen3.4、Boost1.74及PQP compat02都已有证据；去除未使用GLUT/model绘图和ompl_app链接仅属已审计非可视构建适配。各同名类必须模型/方法分进程或独立目标，不能混链造成ODR冲突。

## 4. RBS、源码参数与统计口径必须先解决

1. 原SVC含`checkMotionRBS`/`reconstructRBS`：I tol=.05、maxdepth100，空间tol=.05、maxdepth150。应复用真实中点、支选择、碰撞和回溯，保留原返回；独立验证记录每个投影输入/输出和全q距离。仅d<tol不经过投影的叶须区别于真正检查过的边。source资格不自动成为连续安全证书。
2. RSS近奇异shortcut：ABB15×.05=.75rad，Comau7×.05=.35rad；源递归内部回到普通重构的行为也须逐字记录。严格接入诊断沿用其已冻结h=.0025原坐标门；不能用source shortcut救回Q2 UNKNOWN。若发现任意精确中心的规范化不连续，需要对保留中心的IK族/分支映射先推导，不能偷偷选新中心或让NR兜底。
3. I/IV暂无原模型RSS实证；II/III mode0保存样本均在主动腕心可达包络外，只说明这批失败，不说明整个mode空集。不得以删除mode0、改混合权重或样本筛选换通过。三mode/Comau wrist-only、真实肘部角与作者固定角、肩部退化遗漏都分项保留。
4. 源RSS概率不一致：`CKCplanning/planners/SBL_RSS.cpp:193`及IV/V/VI的`planners/SBL_SG.cpp:193`均使用`rng_.uniform01() > .05`（普通分支），注释却写20%；RRT及Bi-RRT使用.2。freeze须逐文件绑定。论文γ=.2和本次VI重建γ=.2保持；原源码.05另列SOURCE_NATIVE。更正到论文.2须明确PAPER_ALIGNED版本及差异，不能无记录合并或按胜负调概率。
5. IV `sampleSingular`碰撞/checkEE条件被注释，V启用；VI RSS header默认`withObs=false`，其他空间方法默认true。**源返回、独立资格拒绝和修复后行为分开**；不得把关闭withObs造成的限位/碰撞漏检当去障碍消融。去障碍只关闭障碍对，保留关节界/闭链/自碰撞/互碰等既定条件。
6. `CKCplanning` CLI是1 Bi-RRT /2 RRT /3 PRM /4 SBL；Comau和planar是1 Bi-RRT /2 RRT /3 SBL。`srand(time(NULL))`及内部500/1000/87次模式不适合本预算单次执行；复用类，替换为单次薄harness，显式固定C rand和OMPL RNG两随机流。不得直接跑旧main或旧ELF。
7. 作者每法/环境/规划器步长不一致，CKCplanning当前值也不等于全部Table II值。先冻结来源表；源码原参数、论文对齐参数、共同参数诊断分开。找不到最终原调优网格/种子时UNKNOWN，不用试跑后挑参数补全来源。
8. 真路径成功须独立检查起终点、每条树边及最终回溯路径、双闭合/真实branch/原限位/原碰撞。记录树上与解路径真实partition变化；PCS未切换不自动失败，也不冒充切换机理已经验证。完整物理网格/遗漏对/连续性未证的范围持续标明。

## 5. 下一有限资格：先冻结才执行

下列是为主代理准备的**上限草案**。不能因为本报告列了数字就运行。先审阅exact-center根因、源码/模型/RBS差异和版本，填充唯一run_id、固定数组与SHA、独占claim、调用计数器、墙钟/CPU双deadline、停止前缀。连续三次同机制修复后按D079根因审查；工程错误也留原输入、失败与版本，不原地重启。

### Q0：VI exact-center最小根因诊断

主代理已执行`20261015_R2_VI_RSS_CENTER_IMAGE01`，固定219/643；0构造、0 IK/NR/采样/碰撞/规划、2次active FK/J，wall=.208154164s、CPU=.208192s，源码`57ca473`。四个方向的scaled image residual约7.09e-6至1.24e-5；假设一阶fiber极限全18间距约.00228至.00274rad仅是未构造推断，不是新合格端点或路径。严格桥UNKNOWN不变。

因此当前**B余额为56构造、126.671165572s wall、347.840265s CPU**；R2十run合计wall81.110257233s、CPU31.007994s。不得重跑该诊断或把旧余额再领取一遍。每构造16支上限和全部候选留存继续适用。只有解释中心极限、branch身份与秩并独立复核，才可拟后续严格桥方案。新连续族/局部连接算法与原法实质不同则交科学决定；不能据剩余额度自动展开。Q0本诊断已完成，不在后续帽中重复预留60秒作已执行成本。

### Q1：原搜索器整合与源等价资格

复用上表13个现有可适配模型/方法目标（I2、ABB3共享II/III、IV3、V3、VI2）；VI RSS若根因门通过且差异审定，增加第14目标。每目标含三个原搜索器，保留独立的原生失败与版本化数值修复。此时不调用`solve()`。

建议build总帽630s wall/1260s CPU，单目标45s wall/90s CPU，串行并禁用隐式多核；超限保留build前缀，不立刻重试。原单诊断120s上限仍不可超。即使工程构建通常另账，本方案保守把新工程帽也占入R2余量，避免预算口径不明。

不增加旧R0/R1数学样本。C++修复仅在需要移植的接口上对**已保存原输入/输出**逐项核验等价：原模型/基座/抓持/限位/单位/闭合方程/合法周期副本/全部支、原NR伪逆迭代与终止。NumPy NR保留为oracle而非计时对照；新C++输出差异须给误差与数学理由。输入列表及每条调用数在freeze时从固定保存数据生成并哈希；缺这个精确列表不进入Q2。

### Q2：普通PCS/NR的固定局部连接资格

**明确拟用输入**：A01/A02最终合格RECONSTRUCTED start/goal各一，不替换中心；每中心所有可用PCS主动角色/被动划分，取该角色中索引最小的主动关节，±h扰动；h=min(1e-4,该中心全q最小source-bound余量/8)。各center/partition的全部branch身份先枚举并保存；不具共有支、不可解析或投影出界的pair原样失败，不能搜下一个关节/更小h。NR同两中心取全q索引0的±h输入，由全链原伪逆投影；不固定主动角或增加branch门。此是新有限局部组，不能替代原全部资格或宣称邻域保证。

- PCS：I20划分×2中心×2符号=80条pair；II–V各2角色×2×2=8条，共32；VI3角色×2×2=12，共**124条**。
- NR：六环境各2中心×2符号，共**24条pair**。
- 普通RBS共**148条pair**；每条depth4最多15个真实中点，故≤2220中点投影，另≤148 endpoint投影。各角色完整8支（VI两个被动臂各8支）必须计入IK预算，不能把16支写作1次IK。source tol和独立检查分别留证；未到叶门则UNKNOWN，不能把depth cap记算法无解。
- 资格运行总帽450s wall/900s CPU，≤2368投影、≤2368逻辑source-policy碰撞（每逻辑query含native/aligned变体及其PQP对数另记）、≤6864空间nativeFK行；I解析分支计算单列。这里nativeFK是粗硬帽，所有中间支复核也计入，freeze须展开精确调用列表；未展开前不执行。碰撞/支/残差拒绝和UNKNOWN全保留，不追加补跑或随机换pair。
- 这148对只验证局部接口/分支/回溯；真实start→goal可达见证、奇异跨支和复杂环境可见性仍是独立待做义务。若无正控通过或oracle矛盾，相关方法不进pilot。

上述数是可审查的有限方案，不是原文参数。h/depth上限应在执行前被完整协议定版；与原 .05 source策略的差别明示为独立资格，不可称改良原法成绩。

### Q3：RSS已保存候选补齐与未运行原模式资格

先对II18/III22/V8共**48个已有数学合格支**补真实碰撞，不重做700目标/5600支生成。按原目标/支ID排序，所有拒绝保留；每个原mode取排序首个独立合格候选仅作桥fixture，不能在失败后继续挑fixture至通过。mode0无候选的事实保持FAIL/覆盖未定，不据其他mode代填。

IV原wrist-only尚未运行：若主代理确认属于已授权R2原模式数值修复，可另freeze **100个目标×8支=800 IK评估**，采用旧RSS固定脚本相同生成规则、明确seed及IV原界/基座/抓持；最多100构造、800候选真实闭合/秩/支/界，合格者每支最多1碰撞（≤800逻辑query）。没有合法候选就保留FAIL，不偷改分布。肩部模式/Comau三mode是额外科学设计，不在这100里暗加。

此阶段帽240s wall/480s CPU，≤848碰撞query；**不含新RSS奇异桥构造**。桥必须等Q0根因处理后单独freeze原中心保持、共有支/真实秩/全部叶、调用帽和方法标签；没有合格RSS桥的环境不能用普通PCS连接冒名RSS进pilot。I独立RSS和完整肩部集合重建另需科学决定；VI所有新增构造仍受原B总960约束。

## 6. 条件通过后的资源 smoke 与成本 pilot 草案

执行门：模型、数值源码、碰撞控制、端点、原RBS及独立路径验收、RSS相关奇异桥均通过；native与reconstructed标签冻结，任何方法无合格正控不启动其对应单元。缺的单元保留在矩阵为待处理，不能删除，也不能用已合格两法比较代表三法全覆盖。

建议先做**单次资源smoke**，不是充分成本pilot：45个Table I单元+I的PCS/NR各3搜索器=51单元，最多两个固定种子2026101501/2026101502，各10s `solve` 上限，共**102次、1020s最大solve时间**。I RSS三个单元仍待独立重建决定，若后续通过，另加6次并相应重新预算。两seed配对不等于算法随机调用一一相同；C rand/OMPL独立子流与调度固定，所有投影/采样/RBS与碰撞调用计数留存。

连同路径独立验收、序列化与进程收尾，group帽1350s wall/2400s CPU；单次进程13s wall/20s CPU，最多10s规划，超时通过外部监督器终止并保留前缀。每条路径验收最多10000节点、每个逻辑碰撞调用单独计时；超过验收帽只记UNQUALIFIED_PREFIX，不能报告SUCCESS。不允许后台未计时线程或嵌套采样无限循环逃逸总帽。

该102次仅回答框架能否按时停止、日志/恢复/路径验收是否真实执行、成功或10s删失的成本与粗计数。**不能从2次/10s外推1000s成功率、完整成本或排名**。若大量删失，下一份真正成本pilot建议每组10seed，原1000s cutoff及完整义务保留，先根据这批真实运行报预算，再请科学/资源决定；不能自动接着跑，也不能只把成功单元挑进正式矩阵。R2原配置的`formal_planning_calls=0`不因此被更改；smoke独立记`diagnostic_planning_calls`，正式仍0/22500。

后续预算合计草案为：Q1 630/1260、Q2 450/900、Q3 240/480、smoke1350/2400，共**2670s wall/5040s CPU**。与目前十run的81.110257233s/31.007994s相加为2751.110257233/5071.007994，低于R2总3600/7200；剩848.889742767wall/2128.992006CPU仅作未执行保留，不自动重试/扩样，也不等于新的RSS桥预算已获批准。若其他新run已运行，先读实际ledger重算，不能用这个快照再领取同一预算。每阶段实际成本分别记账，不拿上限当已耗，不叠加execution内cumulative字段。

所有步骤都是严格依赖序列；无需等VI解决才读源码/做合格环境的可审查整合，但不得在RBS不合格时提前solve。方案的目标是拿到下一轮可决策成本，不声称在这2670s内完成P4。

## 7. 本方案不减少原文或D079任何义务

最新覆盖对照CSV的**211个唯一ID、30父项+181子项及其顺序**保持；R1原30事实列和旧R2额外5快照列均不覆盖。该有限资格/smoke不把PARTIAL改成FULL，完整formal实验另用`full_experiment_execution_ledger.json`原分母：

- Table I：II–VI×RRT/Bi-RRT/SBL×RSS/PCS/NR=45单元×500=22500调用；1000s/call和dash/超时单元全保留，最坏6250单核小时尚未批准。
- APC/NR500000配对ambient配置，原纯投影关闭碰撞/限位；与规划条件分别实现，失败也在分母。
- Fig.3上m=1,2,3,7,20+NR局部连接，下m=1..20+NR规划。原最终N不明处保持UNKNOWN，source mode4每m1000/成功目标计数和原论文N不同，不擅自把它们等同。
- 约50000合法点对的局部可见性、Fig.4正文II/图注I冲突、Table II十指标及d参数、Fig.5同一邻点前后距离绝对变化；现source不一致/accepted-only/手工缩放均保留，不直接跑旧脚本冒充原图。
- 全部固定被动划分、独立/依赖链、VI双被动支对、无障碍消融、复杂障碍/窄通道和PCS优势验证；困难fixture先有独立可行路径见证或UNKNOWN，无后验挑图/挑seed。
- RSS肩部退化、被动秩与原固定角反例、APC/NR分布及连续流形覆盖限制、Fig.1/其余公式和科学论断继续逐行核验。仅资格通过不能证明论文理论或优势。
- 完成后更新中文Word/PDF和NR/RBS/PCS/RSS对双FR3适用条件；最终完整对照表先交用户审查，P2和Isaac场景拓展不开展。

## 8. 明确的决定边界

可在既有授权内先做、但仍须freeze和源码审查的部分：保留原物理模型的有证据数值修复整合、v3观察显式绑定、固定既有输入的独立资格、原A/B余额内且有明确根因的有限诊断。不能要求用户再批准已经明示批准的A/B同一修复，也不能把它们预算重新开一份。

需要新的科学决定或补充协议的部分：I原模型RSS独立构造、未授权肩部/新mode分布、保留奇异中心的全新局部连接策略、将VI独立候选扩为三搜索器完整RSS、源SBL .05与paper .2的正式比较标签/参数来源不明的重建；以及所有超出现资格范围的成本pilot/正式大规模计算。先提供推导、源码差异、固定条件和成本，不以“缺失”结束工作，也不默默把新的方法叫作者原生。

本文件只创建计划文本；科学调用0、构造0、编译0、planner solve0。后续执行前必须由主代理把可运行子协议、代码及独立复核冻结到Git，再按真实日志更新原对照表和总账。
