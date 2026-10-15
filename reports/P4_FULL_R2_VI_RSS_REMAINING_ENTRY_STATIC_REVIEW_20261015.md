# P4 R2 VI RSS 剩余 RBS、分布与真实搜索入口静态审查

2026-10-15。只读审查，不编译，不新增候选，不调用 FK/J、IK、NR、碰撞或 planner。结论：已有独立组合组件的离散 PASS 成立；VI 的原作者 RSS 可运行等价、生产采样分布、通用局部连接器和真实搜索入口仍未通过。它们是不同资格项目，不能相互代替。

## 当前证据与不能升级的结论

|项目|实际已知状态|尚缺内容|
|---|---|---|
|原作者 VI RSS|`SOURCE_INCOMPLETE / NOT_EXECUTED`|三臂 sampler、branch 数据结构、singular RBS 与搜索器接口一致性|
|独立 B 条件奇异构造|868构造、30请求，7请求成功/23个32次请求失败；7个合格center，指定arm2有2个、arm3有5个|不是 RSS Bernoulli 混合事件，也不是全局搜索成功率|
|原 Q2 固定 active 直弦|`UNKNOWN_OR_FAILED` 原样保留；36个新点本身合格，但 depth3 的32叶均未达 h|不能以原source的宽捷径升级通过，不能以新组合改写旧算法|
|独立 fiber 组件|6/6点、6叶离散通过|只在固定同位姿奇异纤维内|
|独立 ingress 组合|64/64新点，104节点/102边、两条过原center的固定离散链；`PASS_RECONSTRUCTED_COMPOSITE_DISCRETE_ONLY`|两个fixture以外的通用性、连续lift/CCD、分布、真正grow/solve|

现有组合绑定 source `243fa059aa9512d9b2fa9a48fdf7e18cbdf43e74`、协议 SHA `592ca2321a48ca1745d833226947ef86e5c483ec7fc337950bf7db51476b3379`、execution SHA `784dcf0be2e85e28114c8cf9b54b96cff76b2775607967b68caf5af22840fb3a`。本报告只引用保存结论，没有重跑或重新核验机器人模型。

7个合格原 B center 的 construction 顺序为219、363、415、437、483、643、836。组合只覆盖219/643（固定 first-by-designated-arm），指定奇异分支meeting-set均为[1,3]。836的meeting-set为[0,2]，其active arm1 branch3、另一被动arm3 branch1；尚无该分支组合的 ingress 资格。不能把几何分支集合存在等同于已连接路径。

## 作者快照与真实 RBS 入口

快照 `ckcComau3@25488a86947cd07377cc62c43850df719a70d9ee`，原 manifest 123文件、tree `22772508872cb02b7138c0d8cb4740825381581f`。本次核对的 `StateValidityCheckerRSS.cpp/.h` SHA 分别为 `0b6c611fb2fb053277310781eb2c54150956e55832fc9c9f29ee90175e015ddf`、`2dfb86e6c37aa6bcfb65a1a78282286f22ee3e31e912be6bcdd0e092e2a329fc`，与原manifest一致；没有改作者文件。

原普通 RBS 的概念结构已部分三臂化：`StateValidityCheckerRSS.cpp:589–614` 计算 raw full18 距离，full18算术中点，固定active和两被动branch经IKproject投影，随后递归两半；`reconstructRBS:701–734` 保存投影中点。source叶门为 d<.05、深度150，它假设两端已有效，没有独立闭链/branch/物理Jacobian资格。

奇异入口 `:619–665` 保留两臂移植错误：函数体只声明 q1/q2 却使用 q3，`:661` 使用未定义 dsg2，第二递归调用缺失第三臂参数；header 的 isValidRBS 和若干 singular overload 的末参 int/State 也与定义不一致。这些是具体 C++ 声明/函数体矛盾；本次没有重新编译来制造重复失败。原 singular RBS 的额外 `distance(midpoint,singular)<7*.05=.35` 提前返回，以及重建 `:779–780` 在保存该midpoint前提前返回，不能证明本轮 h=.0025 下的完整离散节点链。

原 `sampleSingular:360–407` 未构造 q3，仍调用两臂 `IsRobotsFeasible_R2(q2)`、`updateStateVector(state,q1,q2)`，并将三臂 Matrix identify 返回值赋予 State ik。原header只声明三臂update；APC声明也不是该旧两臂接口。因此仅修 `q3/dsg2` 拼写远远不足以恢复原生VI RSS，必须把重建范围公开列出。

新组合没有执行上述作者原函数。它复用固定图及已知fiber端点，在原解析分支、合法真实2π lift和严格h下验证有限节点；因此应持续标记独立重建组件，而不是 author-native RBS、连续数学路径或整个RSS PASS。

## 分布层次必须分列

1. 原三臂公开 sampler 片段硬编码 sMode=1、只奇异化arm2；原随机角从[-3.1416,3.1416]生成并带旧两臂可达性重试。三臂有效条件、第三臂选根、完整随机消耗流并未定义为可执行实现。
2. 独立 B 协议明确固定active1，指定被动臂2/3概率(.5,.5)，每请求固定指定臂、最多32构造；六角按原机械界均匀抽样再令q5=0，对arm1及另一被动臂各求全部8原支，再从源界内合法根按原branch顺序均匀抽取。重复原支保留重数、碰撞后不换根。这是已披露的独立条件分布，并非原三臂分布等价。q4±2700°、q6±400°的机械界也不能悄悄替代planner普通采样盒±π。
3. B 中 `rss_gamma=.2` 是保留的规划参数；`gamma_used_for_planner_events=false`，没有实际γ混合事件。Q2/fiber/ingress亦为固定数据、随机抽样0。因此7/30不能当作整体RSS规划成功率，也不能据此验证γ=.2生产流。
4. 原搜索器公开片段还相互不一致：CBiRRT_SG.cpp:427–435使用20%奇异事件；RRT_SG.cpp:158–170先goal bias，再在非goal事件内20%奇异；SBL_SG.cpp:193实际阈值为.05，注释却称20%。用户要求γ=.2，后续若恢复SBL应明确修订该字面不一致，保留原.05对照，不通过调高γ制造性能优势。

## 真实搜索入口与最少必须冻结的契约

`makefile` 默认指向 `plan_SG + CBiRRT_SG + CPPRSS`，RRT/SBL SG编译列表注释；`run/plan_SG.cpp:46–71` 也仅分配Bi-RRT，RRT/SBL分支注释。state space虽为18D、callback原样恒true，CBiRRT仍有State branch tuple与scalar -2比较/赋值、IKproject引用/重载不一致等未完成迁移。RRT/SBL源保留两臂q/标量branch/getQ/旧collision调用；RRT甚至在`:255`以 `if(0 && sat)` 禁用该处goal命中。源码文件存在不等于已验可运行入口。

后续通用RECONSTRUCTED版本至少要在任何科学运行前冻结：

- 完整18角状态、active arm1和两被动branch tuple；奇异状态只标记实际指定的被动臂及其meeting-set，不能把两臂都写成一个−2标量。
- ordinary sampler盒、原物理界、奇异条件分布、根选择与随机消耗顺序；γ=.2每次触发位置、goal bias和SBL网格条件均分别记录。
- 普通解析投影、regular↔singular入口、fiber运动的确定性规则与失败状态；现有219/643保存图只作为fixtures，不能对未知center返回缓存PASS。
- 每个真实grow/solve调用、每条成功边及完整精度重建；所有节点闭链/分支/界/秩/作者碰撞策略和叶距独立资格。原宽捷径若保留对照，不能取得严格门PASS。
- author-native、SOURCE-CORRECTION、INDEPENDENT-RECONSTRUCTION三列来源、参数和统计；完整实体/漏pair/CCD与原离散source-policy范围分别报告。

## 下一阶段最小可审设计与预算草案（未授权执行）

当前 VI B累计 **974/974、候选余0**；时间余额不能转换候选额度。故没有可合法启动的新VI候选、RBS中点或RSS solve。主线可继续其他已授权普通PCS/NR资格；这不删除VI义务。

最小下一步建议为 `VI_RSS_RUNTIME_CONTRACT_SAVED_ONLY`：只新增版本化接口/状态机草案，对现存7center、合计104节点的两个组合分量及失败记录作只读输入映射，展开三搜索器差异；用明确固定mock返回值检验分支tuple、γ=.2事件分派、异常/预算/日志保全。建议工程资源帽 **15秒wall/30秒CPU，科学候选/FK/J/IK/NR/碰撞/grow/solve均0**；未执行且不计为科学通过。它不能声称验证生产采样分布或规划。

在该接口及通用fiber数学规则可审以后，再给新的科学PRE：优先从已保存未覆盖的836（[0,2] meeting-set）和363（不同原腕家族）固定选择，先用已保存矩阵推导单侧图、fiber角与必须细分的精确清单，再据清单申请**独立新增候选上限**与成本。不得先运行再定预算，不得重启原868随机构造，也不能把旧219/643通过图重复计新资格。现阶段缺少这些新fixture的固定叶清单，诚实的新增科学预算是“尚未冻结/不得运行”，而不是编造一个保证通过的候选数。

P4正式规划仍0/22500；500000投影、约50000合法点对、Fig.3–5/Table I–II、211行全文义务和完整PCS优势/消融均不变。本次没有修改任何治理总表或历史科学数据。
