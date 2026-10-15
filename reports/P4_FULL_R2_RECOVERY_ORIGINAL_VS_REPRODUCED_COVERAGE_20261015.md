# P4 R2 断点恢复：原论文与实际复现完整范围对照表

2026-10-15。完整论文仍**部分完成**。保留原 **211 入口、30 父义务、原29项任务**及全部原文规模。此表为恢复阶段快照，不能据有限组件、单点或构造请求判为论文结题。历史R1与旧R2表不改。

## 历史列与当前列

配套CSV的前30列逐值保持R1事实列；随后5列逐值保存旧R2快照，含当时已知的映射问题。当前判断只读取新增 `recovery_*` 列。VI Q2桥接与IV NR local分别列明。原始端点与重建端点单独列出，原失败永不回填为通过。MD逐行保留相同211个ID、原要求和规模，当前实证与未完成内容不省略义务。

## 本次真实进展

- R1原1826检查、1580通过/246失败原样保留。原R2空间2091检查2088通过/3FAIL；160次NR为154合法闭合/6闭合后限位拒绝。平面解析233检查、NR56检查通过。IV保存数据支持“额外正控必成功断言缺乏先验证据”，不能改判旧3FAIL。新增**IV NR local**独立24固定轴向±h输入24/24 CONVERGED并通过闭链/源界/source-policy，52原生FK、24碰撞调用完成，绑定文件不变。墙钟2.651571520s、CPU0.882651s；原6拒绝/3FAIL均保留。此结论仅覆盖这24输入，不代表整个邻域、原±.01组、速度基准或规划。
- A：原12端点闭链全FAIL保留。A01的8个source-policy合格与IV/V共4个UNKNOWN原样保存。A02在source0465ad8冻结后仅回放四个已存同分支候选，4/4 source-policy合格，最新重建12/12合格；TCP最大差6.821e-13mm。4次实际adapter调用保留native/aligned，墙钟1.321430518s、CPU1.324637s，绑定原文件字节不变。A两次累计8.771571746s墙钟、7.350284s CPU，新IK/NR/采样/规划0。不能将重建成功冒充原端点直接通过。
- B初组：独立重建VI RSS候选30请求，868构造、13888 IK分支；7请求各得1个source-policy合格候选，23请求在32构造上限失败。指定臂2为2、臂3为5，候选覆盖门通过。原γ=0.2保留，但没有规划采样事件；7/30不是RSS规划成功率。原作者RSS实现缺项仍保留。
- **VI Q2**：固定219/643两中心进行36构造（8显式曲线+28真实RBS中点）、576 IK分支、36原生FK、36碰撞调用；36/36节点数学与source-policy合格，两组曲线合格。四个严格半连接在depth3仍未达到全18关节距离h=.0025rad，桥接门为**UNKNOWN**，不能称RSS/RBS桥接PASS。source阈值与奇异shortcut旁审不参与严格通过。墙钟7.987086492s、CPU6.310368s，根因只读审查中。B+VI Q2累计904构造，原预算余56构造/126.879319736wall秒/348.048457CPU秒，不允许重置或自动重跑。
- 当前R2真实执行累计**80.902103069墙钟秒、30.799802 CPU秒**。这不包含编写/审查工程耗时，也不构成任何正式大规模运行授权。
- II/III/V旧固定RSS构造700目标/5600分支，19目标48分支仅过闭合+原限位+真实奇异三门。II/III mode0各0/100原FAIL保留；这些结果不计入I/IV。
- 实际原mesh/PQP正负控8次加平面原函数4次共12控制通过；范围仅**作者离散source-policy**。完整实体几何、遗漏pair、自身覆盖完整性及CCD未获证。ABB原共线杆三角形不能作为实体杆证书。
- **Table I正式规划0/22500**，45单元各500次、1000s/call全保留。500000配对投影、约50000合法可见性点对、Fig.3–5、Table II、全部无障碍/复杂障碍/窄通道与固定partition义务均未删除。后续先冻结资格和小规模成本测算，大预算另行报告。

## 主要证据

|证据|文件/运行|边界|
|---|---|---|
|R2数学|`20261015_R2_SPATIAL01`、`20261015_R2_PLANAR01`、`P4_FULL_R2_SPATIAL_INDEPENDENT_REVIEW.md`|有限FK/IK/Jacobian/NR组件；不是完整规划|
|IV根因|`P4_FULL_R2_IV_NR_ROOT_CAUSE_RECOVERY_20261015.md`|只读保存数据，旧6拒绝/3FAIL保留|
|IV NR local|`20261015_R2_IV_NR_LOCAL01/execution.json`|24/24固定输入局部资格通过；不替换旧组|
|source-policy控制|`20261015_R2_COLLISION_CONTROLS01/result.json`|12真实控制通过；不证明完整物理几何/CCD|
|A原资格|`20261015_R2_ENDPOINT_RECONSTRUCTED01/execution.json`|原12FAIL与A01重建8合格/4UNKNOWN原样保留|
|A碰撞续验|`20261015_R2_ENDPOINT_COLLISION_REPLAY01/execution.json`|4/4保存候选合格；最新重建12/12，原端点仍FAIL|
|TCP v3|`P4_FULL_R2_COLLISION_TCP_INSTRUMENTATION_REVIEW_20261015.md`|IV误读未初始化T7；V工具观测少2mm；观测修复不改碰撞逻辑|
|旧固定RSS|`20261015_R2_RSS_CONSTRUCTION01`、`P4_FULL_R2_RSS_MODE0_SAVED_TARGET_REVIEW.md`|II/III/V有效，不外推I/IV；无碰撞/桥接|
|B|`20261015_R2_VI_RSS_RECONSTRUCTED01/execution.json`|868构造/13888分支、7/30请求；独立重建、非完整RSS|
|VI Q2|`20261015_R2_VI_RSS_BRIDGE01/execution.json`|36节点合格、四半连接UNKNOWN；非完整RSS或桥接PASS|

## 全部211项

状态表示原义务累计覆盖范围；PARTIAL不表示完整通过。父项不按子组件数量计分。CSV另保留逐行完整证据路径、分类、VI Q2、IV NR local、原/重建端点及碰撞范围列。

### 30项父义务

|ID|原文要求|原次数/规模|R1 / 旧R2 / 当前|本次及已有实际证据|仍须完成|
|---|---|---|---|---|---|
|P4-T01|完整闭链构型/有效空间/各类人工奇异及可见性定义|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / PARTIAL / PARTIAL|原R2空间2091检查2088通过/3失败，160次NR为154合法闭合/6闭合后限位拒绝；平面解析233/233、NR56/56检查通过。新增IV NR local独立24固定输入全部CONVERGED+闭链/原界/source-policy合格，旧6拒绝/3FAIL不改。组件数不是规划分母。 A原12端点闭链均FAIL且保留；A01重建8合格/4UNKNOWN原样，v3纯TCP观测修复后A02仅回放4个已存同支候选，4/4 source-policy合格；最新重建12/12合格。新IK/NR/采样/规划0，完整几何/CCD未证。 B独立重建VI初组：30请求、868构造/13888分支，7请求各得1个source-policy合格候选（臂2为2、臂3为5），23请求32构造上限失败。VI Q2固定219/643续验36构造（8曲线+28中点）/576分支，36节点数学+source-policy合格，但4半连接depth3未达h=.0025，严格桥接UNKNOWN。累计904构造；非RSS/桥接/规划PASS。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。 可见性定义尚无完整运行证据。|
|P4-T02|APC被动链解析IK/所有可达分支、成功与失败采样|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / PARTIAL / PARTIAL|原R2空间2091检查2088通过/3失败，160次NR为154合法闭合/6闭合后限位拒绝；平面解析233/233、NR56/56检查通过。新增IV NR local独立24固定输入全部CONVERGED+闭链/原界/source-policy合格，旧6拒绝/3FAIL不改。组件数不是规划分母。|有限固定目标合格不证明所有分支覆盖；空间R2未重放原远距离不可达负例；保留原作者R1失败。尚须完整环境/局部路径资格。|
|P4-T03|NR全链Jacobian/SVD投影及数值收敛/失败|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / PARTIAL / PARTIAL|原R2空间2091检查2088通过/3失败，160次NR为154合法闭合/6闭合后限位拒绝；平面解析233/233、NR56/56检查通过。新增IV NR local独立24固定输入全部CONVERGED+闭链/原界/source-policy合格，旧6拒绝/3FAIL不改。组件数不是规划分母。|Python参考NR不是C++ APC公平速度基准；原式伪逆更新及限位拒绝成本须保留；完整局部连接和规划未验证。 IV NR local 24项独立通过，不替换原±.01组，旧3FAIL保留。|
|P4-T04|APC vs NR 500000随机样本：投影成功率、耗时分布及成本；原原环境设定|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR原500000配对ambient配置效率实验实际0；有限FK/IK/NR资格不计入此分母。|保留同500000输入的两方法配对、无碰撞/无关节界原条件、成功率/距离/时间/迭代与分布；不得用小样本替代。|
|P4-T05|RBS递归中点/IK分支/碰撞局部连接、失败与精度|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|VI Q2独立三臂离散局部检查：固定219/643，8显式曲线+28真实主动臂1算术中点/被动臂2/3固定支投影；36节点闭链/原界/真秩/分支/source-policy合格。四半连接在depth3仍有叶距≥.0025rad，全部UNKNOWN；原作者source shortcut仅旁审，不计严格PASS。|严格局部桥接仍UNKNOWN，根因只读审查中；未验证作者原生可运行RBS、连续路径/CCD或全局路径。不得以36节点合格代替四半连接通过。|
|P4-T06|可见域、独立/依赖被动链的统计上界及理论适用条件；解析+模拟核对|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|可见域、独立/依赖被动链的统计上界及理论适用条件；解析+模拟核对；原规模保持，尚须冻结条件并实际执行。|
|P4-T07|RSS合法人工奇异目标生成与跨IK分支路径|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / PARTIAL / PARTIAL|II/III/V固定700目标/5600分支，19目标48分支仅过数学三门，II/III mode0各0/100 FAIL。I/IV未执行RSS构造。B独立重建VI初组：30请求、868构造/13888分支，7请求各得1个source-policy合格候选（臂2为2、臂3为5），23请求32构造上限失败。VI Q2固定219/643续验36构造（8曲线+28中点）/576分支，36节点数学+source-policy合格，但4半连接depth3未达h=.0025，严格桥接UNKNOWN。累计904构造；非RSS/桥接/规划PASS。|所有六环境完整RSS及原分布覆盖、碰撞、RBS/分支桥和全局规划均未完成；VI Q2严格门UNKNOWN不得改判。|
|P4-T08|PCS变换多个被动链、选择共有可连接IK分支、搜索树和解路径切换证据|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|新增PCS切换/固定链消融或NR/PCS/RSS公平规划比较0；APC单点闭合不提供树或解路径切换证据。|PCS变换多个被动链、选择共有可连接IK分支、搜索树和解路径切换证据；保留全部环境和固定partition，先完成局部连接/规划资格再运行。|
|P4-T09|NR与PCS/RSS在共同规划栈和独立原生栈中的真实代价比较|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|新增PCS切换/固定链消融或NR/PCS/RSS公平规划比较0；APC单点闭合不提供树或解路径切换证据。|NR与PCS/RSS在共同规划栈和独立原生栈中的真实代价比较；保留全部环境和固定partition，先完成局部连接/规划资格再运行。|
|P4-T10|原环境I平面20R障碍/关节界/精确起终点、奇异跨分支|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|平面100原FK、80两端点×20划分×2分支、2Jacobian、8解析fixture共233检查通过；另32次NR、56检查通过。 2/2重建端点source-policy合格；主动角保持，原分支及最近合法周期解。|仅该环境组件/端点及已列局部性质；RSS/PCS/NR完整规划、场景难度优势、全路径独立资格未完成。|
|P4-T11|原环境II双ABB IRB120搬杆跨杆障碍，刚性闭链|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|330/330组件检查；100原输入对应100臂变换；两类IK目标各80分支接受44；32/32 NR合法闭合。 2/2重建端点source-policy合格；主动角保持，原分支及最近合法周期解。|仅该环境组件/端点及已列局部性质；RSS/PCS/NR完整规划、场景难度优势、全路径独立资格未完成。|
|P4-T12|原环境III双ABB IRB120窄通道|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / PARTIAL / PARTIAL|330/330组件检查；100原输入对应100臂变换；两类IK目标各80分支接受44；32/32 NR合法闭合。 2/2重建端点source-policy合格；主动角保持，原分支及最近合法周期解。|仅该环境组件/端点及已列局部性质；RSS/PCS/NR完整规划、场景难度优势、全路径独立资格未完成。|
|P4-T13|原环境IV双Comau NJ-16搬杆/多障碍|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / PARTIAL / PARTIAL|原430组件检查427通过/3FAIL；200臂变换；两类IK目标各80分支接受28；原32次NR为26合法/6闭合后限位拒绝。新增独立NR local 24/24固定±h输入CONVERGED+闭链/原界/source-policy合格，旧失败不改。 A01原2个UNKNOWN保留；A02用v3修正我方误读T7的TCP观测，仅回放原候选22/44，2/2重建source-policy合格；主动角/原支/原界不变。|仅该环境组件/端点及已列局部性质；RSS/PCS/NR完整规划、场景难度优势、全路径独立资格未完成。 IV NR local不消除旧6拒绝/3FAIL。|
|P4-T14|原环境V双Comau NJ-16吸盘抓箱输送带至安装位|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / PARTIAL / PARTIAL|430/430组件检查；200臂变换；两类IK目标各80分支接受24；32/32 NR合法闭合。 A01原2个UNKNOWN保留；A02用v3修正我方少2mm的TCP观测，仅回放原候选52/22，2/2重建source-policy合格；主动角/原支/原界不变。|仅该环境组件/端点及已列局部性质；RSS/PCS/NR完整规划、场景难度优势、全路径独立资格未完成。|
|P4-T15|原环境VI三Comau抓环绕两杆、多闭环和独立约束|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / PARTIAL / PARTIAL|571/571组件检查；300臂变换；两类IK目标各80分支接受20；32/32同步12×18物理NR合法闭合，属独立重建。 2/2重建端点source-policy合格；主动臂1保持，原被动臂2/3分支及最近合法周期组合。 B独立重建VI初组：30请求、868构造/13888分支，7请求各得1个source-policy合格候选（臂2为2、臂3为5），23请求32构造上限失败。VI Q2固定219/643续验36构造（8曲线+28中点）/576分支，36节点数学+source-policy合格，但4半连接depth3未达h=.0025，严格桥接UNKNOWN。累计904构造；非RSS/桥接/规划PASS。|仅该环境组件/端点及已列局部性质；RSS/PCS/NR完整规划、场景难度优势、全路径独立资格未完成。|
|P4-T16|所有六环境起终点需要跨越奇异构型；可行路径/分支见证、碰撞/限位|按子义务；未公开计数标 UNKNOWN，不代填500|UNKNOWN / PARTIAL / PARTIAL|A原12端点闭链均FAIL且保留；A01重建8合格/4UNKNOWN原样，v3纯TCP观测修复后A02仅回放4个已存同支候选，4/4 source-policy合格；最新重建12/12合格。新IK/NR/采样/规划0，完整几何/CCD未证。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。|
|P4-T17|RRT / Bi-RRT / SBL × RSS/PCS/NR 同环境算法比较|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|RRT / Bi-RRT / SBL × RSS/PCS/NR 同环境算法比较；三规划器×三方法义务均保留。|
|P4-T18|环境II–VI × 三规划器 × 三投影方法：原500次/单元、1000秒上限、超时删失|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|Table I 五环境×三规划器×三方法45单元正式0/22500；每单元原500次、1000s/call保持。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T19|环境I被动链数m=1,2,3,7,20与NR：局部连接成功率-距离、运行时间-链数|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|环境I被动链数m=1,2,3,7,20与NR：局部连接成功率-距离、运行时间-链数；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20|环境II可见份额、调优步长、采样/失败、采样占时、局部连接成本、树/路径节点|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|环境II可见份额、调优步长、采样/失败、采样占时、局部连接成本、树/路径节点；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T21|约50000合法点对局部连接概率、按构型距离分箱与方法对比；核对图注I和正文II差异|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|约50000合法点对局部连接概率、按构型距离分箱与方法对比；核对图注I和正文II差异；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T22|投影前后邻点配置距离绝对变化随初始距离关系；APC对NR|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|投影前后邻点配置距离绝对变化随初始距离关系；APC对NR；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T23|移除障碍前后 NR/PCS/RSS 在各空间环境表现；验证复杂障碍是否消弱NR可见性优势|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|移除外部障碍消融实际0；现有source-policy单点资格未验证复杂障碍相对优势。|移除障碍前后 NR/PCS/RSS 在各空间环境表现；验证复杂障碍是否消弱NR可见性优势；全部空间环境、自碰撞/限位、原模型及公平调参义务保持。|
|P4-T24|每方法单独调优规划步长/距离和RSS γ=0.2；与统一参数公平诊断分开|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|RSS配置γ=0.2保留；B为构造请求，VI Q2为固定局部检查，二者均无gamma规划事件。步长profiling、独立计时及原混合事件分母尚未运行。|每方法单独调优规划步长/距离和RSS γ=0.2；与统一参数公平诊断分开；不得改gamma制造优势，不将7/30构造成功当作混合RSS采样/规划成功率。|
|P4-T25|独立机器/OS/OMPL/KDL/PQP、作者开源版本与我们的运行/许可差异|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|版本/命令/hash保存；PQP实际原mesh正负控8次及平面原函数4次共12控制通过；native/aligned活动pair审计通过。IV/V纯观测v3四编译通过、构建阶段科学查询0；A02和IV NR local真实查询另列。|作者最终统计生产版本/依赖/机器对应仍需追溯；原资源许可边界保持，不将原作者外部源/网格复制公开；本机秒数不直接等同原文。|
|P4-T26|局部路径可见性、平滑度、碰撞几何连续性、采样投影成本在复杂空间场景联合解释|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|新增离散单点source-policy资格和真实残差证据；联合路径可见性、平滑度、连续碰撞与采样成本比较尚无正式数据。|局部路径可见性、平滑度、碰撞几何连续性、采样投影成本在复杂空间场景联合解释；原规模保持，尚须冻结条件并实际执行。|
|P4-T27|空间PCS独立和依赖被动链及多被动链数上限、解析IK可行性；三臂环结构限制|按子义务；未公开计数标 UNKNOWN，不代填500|PARTIAL / NOT_ATTEMPTED / PARTIAL|VI独立12×18约束/Jacobian和候选2/3指定臂构造有有限证据；VI Q2 36节点合格但严格四半桥接UNKNOWN。尚未验证全部PCS多被动链搜索、独立/依赖切换与上限主张。|空间PCS独立和依赖被动链及多被动链数上限、解析IK可行性；三臂环结构限制；原规模保持，尚须冻结条件并实际执行。|
|P4-T28|NR易推广、PCS障碍优势和分析限制在与原文一致的困难条件下是否成立|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|PCS复杂障碍/窄通道相对优势新增合格统计0；单点数学/候选资格不能证实该主张。|NR易推广、PCS障碍优势和分析限制在与原文一致的困难条件下是否成立；原规模保持，尚须冻结条件并实际执行。|
|P4-T29|逐方法NR/RBS/PCS/RSS应用双FR3 Benchmark A/B、接口/依赖/风险及未来实证|按子义务；未公开计数标 UNKNOWN，不代填500|DEFERRED / NOT_ATTEMPTED / DEFERRED|当前未开展FR3/Isaac/P2拓展。P4完成后再单独比较RSS/PCS/NR/RBS用于双FR3吸盘搬运和约束装配的条件与扩展。|先完成P4并提交最新完整对照表供用户审查；概念应用分析与实际FR3场景验证分开，不自动启动Isaac或P2。|
|P4-T30|全部环境 APC/NR 投影后分布近似相同与流形覆盖主张|按子义务；未公开计数标 UNKNOWN，不代填500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR投影分布/流形覆盖独立统计实际0；FK/IK回代一致不等于分布相同。|全部环境 APC/NR 投影后分布近似相同与流形覆盖主张；原规模保持，尚须冻结条件并实际执行。|

### 181项细分义务

|ID|原文要求|原次数/规模|R1 / 旧R2 / 当前|本次及已有实际证据|仍须完成|
|---|---|---|---|---|---|
|P4-T01-EQ1|完整定义/推导/适用假设核对式1|UNKNOWN|NOT_ATTEMPTED / PARTIAL / PARTIAL|原R2空间2091检查2088通过/3失败，160次NR为154合法闭合/6闭合后限位拒绝；平面解析233/233、NR56/56检查通过。新增IV NR local独立24固定输入全部CONVERGED+闭链/原界/source-policy合格，旧6拒绝/3FAIL不改。组件数不是规划分母。 A原12端点闭链均FAIL且保留；A01重建8合格/4UNKNOWN原样，v3纯TCP观测修复后A02仅回放4个已存同支候选，4/4 source-policy合格；最新重建12/12合格。新IK/NR/采样/规划0，完整几何/CCD未证。 B独立重建VI初组：30请求、868构造/13888分支，7请求各得1个source-policy合格候选（臂2为2、臂3为5），23请求32构造上限失败。VI Q2固定219/643续验36构造（8曲线+28中点）/576分支，36节点数学+source-policy合格，但4半连接depth3未达h=.0025，严格桥接UNKNOWN。累计904构造；非RSS/桥接/规划PASS。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。 可见性定义尚无完整运行证据。|
|P4-T01-EQ2|完整定义/推导/适用假设核对式2|UNKNOWN|NOT_ATTEMPTED / PARTIAL / PARTIAL|原R2空间2091检查2088通过/3失败，160次NR为154合法闭合/6闭合后限位拒绝；平面解析233/233、NR56/56检查通过。新增IV NR local独立24固定输入全部CONVERGED+闭链/原界/source-policy合格，旧6拒绝/3FAIL不改。组件数不是规划分母。 A原12端点闭链均FAIL且保留；A01重建8合格/4UNKNOWN原样，v3纯TCP观测修复后A02仅回放4个已存同支候选，4/4 source-policy合格；最新重建12/12合格。新IK/NR/采样/规划0，完整几何/CCD未证。 B独立重建VI初组：30请求、868构造/13888分支，7请求各得1个source-policy合格候选（臂2为2、臂3为5），23请求32构造上限失败。VI Q2固定219/643续验36构造（8曲线+28中点）/576分支，36节点数学+source-policy合格，但4半连接depth3未达h=.0025，严格桥接UNKNOWN。累计904构造；非RSS/桥接/规划PASS。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。 可见性定义尚无完整运行证据。|
|P4-T06-EQ3|完整定义/推导/适用假设核对式3|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|完整定义/推导/适用假设核对式3；原规模保持，尚须冻结条件并实际执行。|
|P4-T06-EQ4|完整定义/推导/适用假设核对式4|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|完整定义/推导/适用假设核对式4；原规模保持，尚须冻结条件并实际执行。|
|P4-T06-EQ5|完整定义/推导/适用假设核对式5|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|完整定义/推导/适用假设核对式5；原规模保持，尚须冻结条件并实际执行。|
|P4-T06-EQ6|完整定义/推导/适用假设核对式6|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|完整定义/推导/适用假设核对式6；原规模保持，尚须冻结条件并实际执行。|
|P4-T06-EQ7|完整定义/推导/适用假设核对式7|UNKNOWN|UNKNOWN / NOT_ATTEMPTED / NOT_ATTEMPTED|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|完整定义/推导/适用假设核对式7；原规模保持，尚须冻结条件并实际执行。|
|P4-T06-EQ8|完整定义/推导/适用假设核对式8|UNKNOWN|PARTIAL / NOT_ATTEMPTED / PARTIAL|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|完整定义/推导/适用假设核对式8；原规模保持，尚须冻结条件并实际执行。|
|P4-T06-EQ9|完整定义/推导/适用假设核对式9|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|完整定义/推导/适用假设核对式9；原规模保持，尚须冻结条件并实际执行。|
|P4-T01-FIG1a|四杆完整构型|UNKNOWN|NOT_ATTEMPTED / PARTIAL / NOT_ATTEMPTED|本子图的构型/局部不连接/跨分支桥或PCS切换实证0；一般FK/IK组件不等于Fig.1图示验证。|四杆完整构型的专属可复查几何/路径见证未执行。|
|P4-T01-FIG1b|固定被动链遇人工奇异导致局部不连接|UNKNOWN|NOT_ATTEMPTED / PARTIAL / NOT_ATTEMPTED|本子图的构型/局部不连接/跨分支桥或PCS切换实证0；一般FK/IK组件不等于Fig.1图示验证。|固定被动链遇人工奇异导致局部不连接的专属可复查几何/路径见证未执行。|
|P4-T01-FIG1c|RSS通过奇异桥跨IK分支|UNKNOWN|NOT_ATTEMPTED / PARTIAL / NOT_ATTEMPTED|本子图的构型/局部不连接/跨分支桥或PCS切换实证0；一般FK/IK组件不等于Fig.1图示验证。|RSS通过奇异桥跨IK分支的专属可复查几何/路径见证未执行。|
|P4-T01-FIG1d|PCS另被动链可连接|UNKNOWN|NOT_ATTEMPTED / PARTIAL / NOT_ATTEMPTED|本子图的构型/局部不连接/跨分支桥或PCS切换实证0；一般FK/IK组件不等于Fig.1图示验证。|PCS另被动链可连接的专属可复查几何/路径见证未执行。|
|P4-T02-I|APC可达分支、正负FK/IK/限位/闭链资格|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|平面100原FK、80两端点×20划分×2分支、2Jacobian、8解析fixture共233检查通过；另32次NR、56检查通过。|有限固定目标合格不证明所有分支覆盖；空间R2未重放原远距离不可达负例；保留原作者R1失败。尚须完整环境/局部路径资格。|
|P4-T03-I|原NR原生全链/VI默认顺序方法与独立完整闭链残差交叉核验|UNKNOWN / 原文没有R1资格次数|PARTIAL / PARTIAL / PARTIAL|平面100原FK、80两端点×20划分×2分支、2Jacobian、8解析fixture共233检查通过；另32次NR、56检查通过。|Python参考NR不是C++ APC公平速度基准；原式伪逆更新及限位拒绝成本须保留；完整局部连接和规划未验证。|
|P4-T16-I|原端点合法性与需要跨人工奇异的起终branch证据及路径见证|UNKNOWN / 原文没有R1资格次数|UNKNOWN / PARTIAL / PARTIAL|2/2重建端点source-policy合格；主动角保持，原分支及最近合法周期解。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。|
|P4-T23-I|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位|原文未给；待冻结诊断规模|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|移除外部障碍消融实际0；现有source-policy单点资格未验证复杂障碍相对优势。|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位；全部空间环境、自碰撞/限位、原模型及公平调参义务保持。|
|P4-T30-I|APC/NR投影后分布与branch/pose覆盖诊断|原文未给；新增独立诊断待注册|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR投影分布/流形覆盖独立统计实际0；FK/IK回代一致不等于分布相同。|APC/NR投影后分布与branch/pose覆盖诊断；原规模保持，尚须冻结条件并实际执行。|
|P4-T02-II|APC可达分支、正负FK/IK/限位/闭链资格|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|330/330组件检查；100原输入对应100臂变换；两类IK目标各80分支接受44；32/32 NR合法闭合。|有限固定目标合格不证明所有分支覆盖；空间R2未重放原远距离不可达负例；保留原作者R1失败。尚须完整环境/局部路径资格。|
|P4-T03-II|原NR原生全链/VI默认顺序方法与独立完整闭链残差交叉核验|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|330/330组件检查；100原输入对应100臂变换；两类IK目标各80分支接受44；32/32 NR合法闭合。|Python参考NR不是C++ APC公平速度基准；原式伪逆更新及限位拒绝成本须保留；完整局部连接和规划未验证。|
|P4-T16-II|原端点合法性与需要跨人工奇异的起终branch证据及路径见证|UNKNOWN / 原文没有R1资格次数|UNKNOWN / PARTIAL / PARTIAL|2/2重建端点source-policy合格；主动角保持，原分支及最近合法周期解。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。|
|P4-T23-II|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位|原文未给；待冻结诊断规模|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|移除外部障碍消融实际0；现有source-policy单点资格未验证复杂障碍相对优势。|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位；全部空间环境、自碰撞/限位、原模型及公平调参义务保持。|
|P4-T30-II|APC/NR投影后分布与branch/pose覆盖诊断|原文未给；新增独立诊断待注册|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR投影分布/流形覆盖独立统计实际0；FK/IK回代一致不等于分布相同。|APC/NR投影后分布与branch/pose覆盖诊断；原规模保持，尚须冻结条件并实际执行。|
|P4-T02-III|APC可达分支、正负FK/IK/限位/闭链资格|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|330/330组件检查；100原输入对应100臂变换；两类IK目标各80分支接受44；32/32 NR合法闭合。|有限固定目标合格不证明所有分支覆盖；空间R2未重放原远距离不可达负例；保留原作者R1失败。尚须完整环境/局部路径资格。|
|P4-T03-III|原NR原生全链/VI默认顺序方法与独立完整闭链残差交叉核验|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|330/330组件检查；100原输入对应100臂变换；两类IK目标各80分支接受44；32/32 NR合法闭合。|Python参考NR不是C++ APC公平速度基准；原式伪逆更新及限位拒绝成本须保留；完整局部连接和规划未验证。|
|P4-T16-III|原端点合法性与需要跨人工奇异的起终branch证据及路径见证|UNKNOWN / 原文没有R1资格次数|UNKNOWN / PARTIAL / PARTIAL|2/2重建端点source-policy合格；主动角保持，原分支及最近合法周期解。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。|
|P4-T23-III|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位|原文未给；待冻结诊断规模|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|移除外部障碍消融实际0；现有source-policy单点资格未验证复杂障碍相对优势。|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位；全部空间环境、自碰撞/限位、原模型及公平调参义务保持。|
|P4-T30-III|APC/NR投影后分布与branch/pose覆盖诊断|原文未给；新增独立诊断待注册|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR投影分布/流形覆盖独立统计实际0；FK/IK回代一致不等于分布相同。|APC/NR投影后分布与branch/pose覆盖诊断；原规模保持，尚须冻结条件并实际执行。|
|P4-T02-IV|APC可达分支、正负FK/IK/限位/闭链资格|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|原430组件检查427通过/3FAIL；200臂变换；两类IK目标各80分支接受28；原32次NR为26合法/6闭合后限位拒绝。新增独立NR local 24/24固定±h输入CONVERGED+闭链/原界/source-policy合格，旧失败不改。|有限固定目标合格不证明所有分支覆盖；空间R2未重放原远距离不可达负例；保留原作者R1失败。尚须完整环境/局部路径资格。 保存数据根因支持原正控完整性断言缺乏先验证据；新增NR local仅证明24固定±h输入，不替换旧组，不证明全邻域。|
|P4-T03-IV|原NR原生全链/VI默认顺序方法与独立完整闭链残差交叉核验|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|原430组件检查427通过/3FAIL；200臂变换；两类IK目标各80分支接受28；原32次NR为26合法/6闭合后限位拒绝。新增独立NR local 24/24固定±h输入CONVERGED+闭链/原界/source-policy合格，旧失败不改。|Python参考NR不是C++ APC公平速度基准；原式伪逆更新及限位拒绝成本须保留；完整局部连接和规划未验证。 保存数据根因支持原正控完整性断言缺乏先验证据；新增NR local仅证明24固定±h输入，不替换旧组，不证明全邻域。|
|P4-T16-IV|原端点合法性与需要跨人工奇异的起终branch证据及路径见证|UNKNOWN / 原文没有R1资格次数|UNKNOWN / PARTIAL / PARTIAL|A01原2个UNKNOWN保留；A02用v3修正我方误读T7的TCP观测，仅回放原候选22/44，2/2重建source-policy合格；主动角/原支/原界不变。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。|
|P4-T23-IV|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位|原文未给；待冻结诊断规模|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|移除外部障碍消融实际0；现有source-policy单点资格未验证复杂障碍相对优势。|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位；全部空间环境、自碰撞/限位、原模型及公平调参义务保持。|
|P4-T30-IV|APC/NR投影后分布与branch/pose覆盖诊断|原文未给；新增独立诊断待注册|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR投影分布/流形覆盖独立统计实际0；FK/IK回代一致不等于分布相同。|APC/NR投影后分布与branch/pose覆盖诊断；原规模保持，尚须冻结条件并实际执行。|
|P4-T02-V|APC可达分支、正负FK/IK/限位/闭链资格|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|430/430组件检查；200臂变换；两类IK目标各80分支接受24；32/32 NR合法闭合。|有限固定目标合格不证明所有分支覆盖；空间R2未重放原远距离不可达负例；保留原作者R1失败。尚须完整环境/局部路径资格。|
|P4-T03-V|原NR原生全链/VI默认顺序方法与独立完整闭链残差交叉核验|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|430/430组件检查；200臂变换；两类IK目标各80分支接受24；32/32 NR合法闭合。|Python参考NR不是C++ APC公平速度基准；原式伪逆更新及限位拒绝成本须保留；完整局部连接和规划未验证。|
|P4-T16-V|原端点合法性与需要跨人工奇异的起终branch证据及路径见证|UNKNOWN / 原文没有R1资格次数|UNKNOWN / PARTIAL / PARTIAL|A01原2个UNKNOWN保留；A02用v3修正我方少2mm的TCP观测，仅回放原候选52/22，2/2重建source-policy合格；主动角/原支/原界不变。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。|
|P4-T23-V|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位|原文未给；待冻结诊断规模|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|移除外部障碍消融实际0；现有source-policy单点资格未验证复杂障碍相对优势。|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位；全部空间环境、自碰撞/限位、原模型及公平调参义务保持。|
|P4-T30-V|APC/NR投影后分布与branch/pose覆盖诊断|原文未给；新增独立诊断待注册|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR投影分布/流形覆盖独立统计实际0；FK/IK回代一致不等于分布相同。|APC/NR投影后分布与branch/pose覆盖诊断；原规模保持，尚须冻结条件并实际执行。|
|P4-T02-VI|APC可达分支、正负FK/IK/限位/闭链资格|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|571/571组件检查；300臂变换；两类IK目标各80分支接受20；32/32同步12×18物理NR合法闭合，属独立重建。|有限固定目标合格不证明所有分支覆盖；空间R2未重放原远距离不可达负例；保留原作者R1失败。尚须完整环境/局部路径资格。|
|P4-T03-VI|原NR原生全链/VI默认顺序方法与独立完整闭链残差交叉核验|UNKNOWN / 原文没有R1资格次数|FAILED / PARTIAL / PARTIAL|571/571组件检查；300臂变换；两类IK目标各80分支接受20；32/32同步12×18物理NR合法闭合，属独立重建。|Python参考NR不是C++ APC公平速度基准；原式伪逆更新及限位拒绝成本须保留；完整局部连接和规划未验证。|
|P4-T16-VI|原端点合法性与需要跨人工奇异的起终branch证据及路径见证|UNKNOWN / 原文没有R1资格次数|UNKNOWN / PARTIAL / PARTIAL|2/2重建端点source-policy合格；主动臂1保持，原被动臂2/3分支及最近合法周期组合。|这些起终点间跨人工奇异的必要性、真实分支桥、完整RBS及全路径独立复核未完成；source-policy合格不证明完整物理几何或CCD。|
|P4-T23-VI|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位|原文未给；待冻结诊断规模|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|移除外部障碍消融实际0；现有source-policy单点资格未验证复杂障碍相对优势。|同模型移除外部障碍消融；全部空间环境比较并保留自碰撞/限位；全部空间环境、自碰撞/限位、原模型及公平调参义务保持。|
|P4-T30-VI|APC/NR投影后分布与branch/pose覆盖诊断|原文未给；新增独立诊断待注册|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR投影分布/流形覆盖独立统计实际0；FK/IK回代一致不等于分布相同。|APC/NR投影后分布与branch/pose覆盖诊断；原规模保持，尚须冻结条件并实际执行。|
|P4-T04-APC|同一500000 ambient配置投影：无碰撞/无关节界；成功/距离/时间/迭代记录|500000|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR原500000配对ambient配置效率实验实际0；有限FK/IK/NR资格不计入此分母。|保留同500000输入的两方法配对、无碰撞/无关节界原条件、成功率/距离/时间/迭代与分布；不得用小样本替代。|
|P4-T04-NR|同一500000 ambient配置投影：无碰撞/无关节界；成功/距离/时间/迭代记录|500000|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|APC/NR原500000配对ambient配置效率实验实际0；有限FK/IK/NR资格不计入此分母。|保留同500000输入的两方法配对、无碰撞/无关节界原条件、成功率/距离/时间/迭代与分布；不得用小样本替代。|
|P4-T19-VIS_M1|PCS可见率按全关节距离bin .3rad，m=1|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|PCS可见率按全关节距离bin .3rad，m=1；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-VIS_M2|PCS可见率按全关节距离bin .3rad，m=2|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|PCS可见率按全关节距离bin .3rad，m=2；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-VIS_M3|PCS可见率按全关节距离bin .3rad，m=3|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|PCS可见率按全关节距离bin .3rad，m=3；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-VIS_M7|PCS可见率按全关节距离bin .3rad，m=7|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|PCS可见率按全关节距离bin .3rad，m=7；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-VIS_M20|PCS可见率按全关节距离bin .3rad，m=20|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|PCS可见率按全关节距离bin .3rad，m=20；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-VIS_NR|NR可见率，配对同合法点对与共同oracle|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|NR可见率，配对同合法点对与共同oracle；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M1|Bi-RRT PCS规划时间m=1|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=1；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M2|Bi-RRT PCS规划时间m=2|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=2；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M3|Bi-RRT PCS规划时间m=3|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=3；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M4|Bi-RRT PCS规划时间m=4|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=4；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M5|Bi-RRT PCS规划时间m=5|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=5；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M6|Bi-RRT PCS规划时间m=6|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=6；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M7|Bi-RRT PCS规划时间m=7|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=7；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M8|Bi-RRT PCS规划时间m=8|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=8；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M9|Bi-RRT PCS规划时间m=9|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=9；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M10|Bi-RRT PCS规划时间m=10|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=10；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M11|Bi-RRT PCS规划时间m=11|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=11；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M12|Bi-RRT PCS规划时间m=12|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=12；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M13|Bi-RRT PCS规划时间m=13|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=13；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M14|Bi-RRT PCS规划时间m=14|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=14；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M15|Bi-RRT PCS规划时间m=15|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=15；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M16|Bi-RRT PCS规划时间m=16|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=16；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M17|Bi-RRT PCS规划时间m=17|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=17；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M18|Bi-RRT PCS规划时间m=18|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=18；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M19|Bi-RRT PCS规划时间m=19|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=19；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_M20|Bi-RRT PCS规划时间m=20|作者mode4每m1000；原文未说明生产数|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT PCS规划时间m=20；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-TIME_NR|Bi-RRT NR时间横线参考|作者mode4 1000；原生产未说明|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|Bi-RRT NR时间横线参考；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T19-PLANAR_PROJECTION|平面PCS/APC与NR投影成本约40倍的原主张|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|平面PCS/APC与NR投影成本约40倍的原主张；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T18-II_RRT_RSS|II RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-II_RRT_PCS|II RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-II_RRT_NR|II RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-II_Bi-RRT_RSS|II Bi-RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II Bi-RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-II_Bi-RRT_PCS|II Bi-RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II Bi-RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-II_Bi-RRT_NR|II Bi-RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II Bi-RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-II_SBL_RSS|II SBL RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II SBL RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-II_SBL_PCS|II SBL PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II SBL PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-II_SBL_NR|II SBL NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|II SBL NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_RRT_RSS|III RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_RRT_PCS|III RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_RRT_NR|III RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_Bi-RRT_RSS|III Bi-RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III Bi-RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_Bi-RRT_PCS|III Bi-RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III Bi-RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_Bi-RRT_NR|III Bi-RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III Bi-RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_SBL_RSS|III SBL RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III SBL RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_SBL_PCS|III SBL PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III SBL PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-III_SBL_NR|III SBL NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|III SBL NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_RRT_RSS|IV RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_RRT_PCS|IV RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_RRT_NR|IV RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_Bi-RRT_RSS|IV Bi-RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV Bi-RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_Bi-RRT_PCS|IV Bi-RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV Bi-RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_Bi-RRT_NR|IV Bi-RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV Bi-RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_SBL_RSS|IV SBL RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV SBL RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_SBL_PCS|IV SBL PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV SBL PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-IV_SBL_NR|IV SBL NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|IV SBL NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_RRT_RSS|V RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_RRT_PCS|V RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_RRT_NR|V RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_Bi-RRT_RSS|V Bi-RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V Bi-RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_Bi-RRT_PCS|V Bi-RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V Bi-RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_Bi-RRT_NR|V Bi-RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V Bi-RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_SBL_RSS|V SBL RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V SBL RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_SBL_PCS|V SBL PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V SBL PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-V_SBL_NR|V SBL NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|V SBL NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_RRT_RSS|VI RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_RRT_PCS|VI RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_RRT_NR|VI RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_Bi-RRT_RSS|VI Bi-RRT RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI Bi-RRT RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_Bi-RRT_PCS|VI Bi-RRT PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI Bi-RRT PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_Bi-RRT_NR|VI Bi-RRT NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI Bi-RRT NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_SBL_RSS|VI SBL RSS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI SBL RSS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_SBL_PCS|VI SBL PCS 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI SBL PCS 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T18-VI_SBL_NR|VI SBL NR 全部500次真实规划/失败与独立路径检查|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|VI SBL NR 全部500次真实规划/失败与独立路径检查：实际0/500，成功/失败/超时统计均尚未产生。|先完成对应环境与算法资格；小规模成本测算不能替换原500次/1000秒统计，较大预算需另报告。|
|P4-T21-RSS|50000合法点对local connection，bin .3rad|50000|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|50000合法点对local connection，bin .3rad；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T21-PCS|50000合法点对local connection，bin .3rad|50000|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|50000合法点对local connection，bin .3rad；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T21-NR|50000合法点对local connection，bin .3rad|50000|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|50000合法点对local connection，bin .3rad；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-visibility|对照TableII指标 visibility|50000 legal pairs (D079 protocol interpretation)|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 visibility；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-step|对照TableII指标 step|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 step；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-samples|对照TableII指标 samples|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 samples；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-failed_samples|对照TableII指标 failed_samples|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 failed_samples；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-sampling_time_fraction|对照TableII指标 sampling_time_fraction|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 sampling_time_fraction；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-local_cost|对照TableII指标 local_cost|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 local_cost；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-local_checks_per_s|对照TableII指标 local_checks_per_s|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 local_checks_per_s；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-local_time_fraction|对照TableII指标 local_time_fraction|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 local_time_fraction；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-tree_nodes|对照TableII指标 tree_nodes|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 tree_nodes；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T20-path_nodes|对照TableII指标 path_nodes|500|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|对照TableII指标 path_nodes；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T22-APC|同邻点定义，投影前后到valid neighbor的构型距离绝对变化，bin .46rad|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|同邻点定义，投影前后到valid neighbor的构型距离绝对变化，bin .46rad；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T22-NR|同邻点定义，投影前后到valid neighbor的构型距离绝对变化，bin .46rad|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|同邻点定义，投影前后到valid neighbor的构型距离绝对变化，bin .46rad；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T08-I_ABLATION|full PCS与每个fixed partition [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]、NR、RSS公平配对；tree和solution switching分开|新增预注册规模待模型资格与预算|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增PCS切换/固定链消融或NR/PCS/RSS公平规划比较0；APC单点闭合不提供树或解路径切换证据。|full PCS与每个fixed partition [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]、NR、RSS公平配对；tree和solution switching分开；保留全部环境和固定partition，先完成局部连接/规划资格再运行。|
|P4-T08-II_ABLATION|full PCS与每个fixed partition [0, 1]、NR、RSS公平配对；tree和solution switching分开|新增预注册规模待模型资格与预算|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增PCS切换/固定链消融或NR/PCS/RSS公平规划比较0；APC单点闭合不提供树或解路径切换证据。|full PCS与每个fixed partition [0, 1]、NR、RSS公平配对；tree和solution switching分开；保留全部环境和固定partition，先完成局部连接/规划资格再运行。|
|P4-T08-III_ABLATION|full PCS与每个fixed partition [0, 1]、NR、RSS公平配对；tree和solution switching分开|新增预注册规模待模型资格与预算|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增PCS切换/固定链消融或NR/PCS/RSS公平规划比较0；APC单点闭合不提供树或解路径切换证据。|full PCS与每个fixed partition [0, 1]、NR、RSS公平配对；tree和solution switching分开；保留全部环境和固定partition，先完成局部连接/规划资格再运行。|
|P4-T08-IV_ABLATION|full PCS与每个fixed partition [0, 1]、NR、RSS公平配对；tree和solution switching分开|新增预注册规模待模型资格与预算|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增PCS切换/固定链消融或NR/PCS/RSS公平规划比较0；APC单点闭合不提供树或解路径切换证据。|full PCS与每个fixed partition [0, 1]、NR、RSS公平配对；tree和solution switching分开；保留全部环境和固定partition，先完成局部连接/规划资格再运行。|
|P4-T08-V_ABLATION|full PCS与每个fixed partition [0, 1]、NR、RSS公平配对；tree和solution switching分开|新增预注册规模待模型资格与预算|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增PCS切换/固定链消融或NR/PCS/RSS公平规划比较0；APC单点闭合不提供树或解路径切换证据。|full PCS与每个fixed partition [0, 1]、NR、RSS公平配对；tree和solution switching分开；保留全部环境和固定partition，先完成局部连接/规划资格再运行。|
|P4-T08-VI_ABLATION|full PCS与每个fixed partition [0, 1, 2]、NR、RSS公平配对；tree和solution switching分开|新增预注册规模待模型资格与预算|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增PCS切换/固定链消融或NR/PCS/RSS公平规划比较0；APC单点闭合不提供树或解路径切换证据。|full PCS与每个fixed partition [0, 1, 2]、NR、RSS公平配对；tree和solution switching分开；保留全部环境和固定partition，先完成局部连接/规划资格再运行。|
|P4-T07-RSS_I|真实合法人工奇异目标、多个模式、被动rank、全链闭合/界/碰撞/分支桥及完整RSS规划；不得NR冒名|UNKNOWN|NOT_ATTEMPTED / PARTIAL / NOT_ATTEMPTED|本环境RSS候选构造/真秩/碰撞/分支桥/规划新增实证0；II/III/V数据不适用于I。|不沿用旧R2错误的PARTIAL映射；需独立冻结平面RSS资格。|
|P4-T05-I_RSS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-I_PCS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-I_NR|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T24-STEP_I|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RSS配置γ=0.2保留；B为构造请求，VI Q2为固定局部检查，二者均无gamma规划事件。步长profiling、独立计时及原混合事件分母尚未运行。|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时；不得改gamma制造优势，不将7/30构造成功当作混合RSS采样/规划成功率。|
|P4-T07-RSS_II|真实合法人工奇异目标、多个模式、被动rank、全链闭合/界/碰撞/分支桥及完整RSS规划；不得NR冒名|UNKNOWN|NOT_ATTEMPTED / PARTIAL / PARTIAL|固定300被动目标/2400主动IK分支，7目标18分支通过闭合+原界+真奇异；mode0为0/100且原正例门FAIL。未查碰撞。|保存mode0腕心均超可达包络证据；不能推出整个mode0集合为空。其余模式归因、完整合法目标、桥接及规划未证。|
|P4-T05-II_RSS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-II_PCS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-II_NR|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T24-STEP_II|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RSS配置γ=0.2保留；B为构造请求，VI Q2为固定局部检查，二者均无gamma规划事件。步长profiling、独立计时及原混合事件分母尚未运行。|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时；不得改gamma制造优势，不将7/30构造成功当作混合RSS采样/规划成功率。|
|P4-T07-RSS_III|真实合法人工奇异目标、多个模式、被动rank、全链闭合/界/碰撞/分支桥及完整RSS规划；不得NR冒名|UNKNOWN|NOT_ATTEMPTED / PARTIAL / PARTIAL|固定300被动目标/2400主动IK分支，8目标22分支通过闭合+原界+真奇异；mode0为0/100且原正例门FAIL。未查碰撞。|保存mode0腕心均超可达包络证据；不能推出整个mode0集合为空。其余模式归因、完整合法目标、桥接及规划未证。|
|P4-T05-III_RSS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-III_PCS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-III_NR|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T24-STEP_III|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RSS配置γ=0.2保留；B为构造请求，VI Q2为固定局部检查，二者均无gamma规划事件。步长profiling、独立计时及原混合事件分母尚未运行。|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时；不得改gamma制造优势，不将7/30构造成功当作混合RSS采样/规划成功率。|
|P4-T07-RSS_IV|真实合法人工奇异目标、多个模式、被动rank、全链闭合/界/碰撞/分支桥及完整RSS规划；不得NR冒名|UNKNOWN|NOT_ATTEMPTED / PARTIAL / NOT_ATTEMPTED|本环境RSS构造新增实证0；旧R2把II/III/V的700目标计入IV不成立。IV数学组件、重建端点与NR local不是RSS资格。|需独立冻结IV RSS模式/真实被动秩及完整候选资格；NR local独立24项通过，原NR旧3FAIL保留。|
|P4-T05-IV_RSS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-IV_PCS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-IV_NR|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T24-STEP_IV|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RSS配置γ=0.2保留；B为构造请求，VI Q2为固定局部检查，二者均无gamma规划事件。步长profiling、独立计时及原混合事件分母尚未运行。|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时；不得改gamma制造优势，不将7/30构造成功当作混合RSS采样/规划成功率。|
|P4-T07-RSS_V|真实合法人工奇异目标、多个模式、被动rank、全链闭合/界/碰撞/分支桥及完整RSS规划；不得NR冒名|UNKNOWN|NOT_ATTEMPTED / PARTIAL / PARTIAL|原公开wrist-only模式100目标/800分支，4目标8分支通过闭合+原界+真奇异；未查这些RSS候选的碰撞。|不能将端点source-policy或VI候选的碰撞结果外推到V的RSS样本；其他理论奇异子集、桥接和规划未证。|
|P4-T05-V_RSS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-V_PCS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-V_NR|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T24-STEP_V|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RSS配置γ=0.2保留；B为构造请求，VI Q2为固定局部检查，二者均无gamma规划事件。步长profiling、独立计时及原混合事件分母尚未运行。|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时；不得改gamma制造优势，不将7/30构造成功当作混合RSS采样/规划成功率。|
|P4-T07-RSS_VI|真实合法人工奇异目标、多个模式、被动rank、全链闭合/界/碰撞/分支桥及完整RSS规划；不得NR冒名|UNKNOWN|FAILED / UNKNOWN / PARTIAL|B独立重建VI初组：30请求、868构造/13888分支，7请求各得1个source-policy合格候选（臂2为2、臂3为5），23请求32构造上限失败。VI Q2固定219/643续验36构造（8曲线+28中点）/576分支，36节点数学+source-policy合格，但4半连接depth3未达h=.0025，严格桥接UNKNOWN。累计904构造；非RSS/桥接/规划PASS。|作者原三臂RSS仍非完整已验证实现；独立重建候选覆盖门通过，VI Q2严格桥接UNKNOWN，根因只读审查中。未证明原RSS分布等价、完整RBS/分支桥、局部可见性或全局路径。原预算余56构造/126.879319736wall/348.048457CPU，不自动重跑。|
|P4-T05-VI_RSS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：RSS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / PARTIAL|VI Q2独立三臂离散局部检查：固定219/643，8显式曲线+28真实主动臂1算术中点/被动臂2/3固定支投影；36节点闭链/原界/真秩/分支/source-policy合格。四半连接在depth3仍有叶距≥.0025rad，全部UNKNOWN；原作者source shortcut仅旁审，不计严格PASS。|严格局部桥接仍UNKNOWN，根因只读审查中；未验证作者原生可运行RBS、连续路径/CCD或全局路径。不得以36节点合格代替四半连接通过。|
|P4-T05-VI_PCS|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：PCS未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T05-VI_NR|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|新增RBS递归中点/分支桥/路径检查运行0；A端点或B奇异候选均不是RBS。|RBS真实递归中点、失败与分支/奇异末端、合法性/稠密路径复核：NR未完成；需冻结原中点、终止门、碰撞与稠密独立复核。|
|P4-T24-STEP_VI|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RSS配置γ=0.2保留；B为构造请求，VI Q2为固定局部检查，二者均无gamma规划事件。步长profiling、独立计时及原混合事件分母尚未运行。|每planner/method各自profiling步长与统一参数诊断分开，冻结选择规则/候选网格与独立计时；不得改gamma制造优势，不将7/30构造成功当作混合RSS采样/规划成功率。|
|P4-T17-I_RRT_RSS|环境I RRT RSS 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I RRT RSS 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T17-I_RRT_PCS|环境I RRT PCS 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I RRT PCS 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T17-I_RRT_NR|环境I RRT NR 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I RRT NR 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T17-I_Bi-RRT_RSS|环境I Bi-RRT RSS 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I Bi-RRT RSS 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T17-I_Bi-RRT_PCS|环境I Bi-RRT PCS 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I Bi-RRT PCS 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T17-I_Bi-RRT_NR|环境I Bi-RRT NR 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I Bi-RRT NR 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T17-I_SBL_RSS|环境I SBL RSS 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I SBL RSS 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T17-I_SBL_PCS|环境I SBL PCS 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I SBL PCS 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T17-I_SBL_NR|环境I SBL NR 可执行路径和公平对照，不能只验证Bi-RRT|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|RRT/Bi-RRT/SBL真实规划新增0；没有合格正式路径统计。|环境I SBL NR 可执行路径和公平对照，不能只验证Bi-RRT；三规划器×三方法义务均保留。|
|P4-T24-GAMMA|RSS gamma0.2原设置及profiling来源与随机/奇异请求分母记录|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / PARTIAL|RSS配置γ=0.2保留；B为构造请求，VI Q2为固定局部检查，二者均无gamma规划事件。步长profiling、独立计时及原混合事件分母尚未运行。|RSS gamma0.2原设置及profiling来源与随机/奇异请求分母记录；不得改gamma制造优势，不将7/30构造成功当作混合RSS采样/规划成功率。|
|P4-T20-NN_COST|最近邻成本随树增大与RSS奇异邻点距离、局部失败阶段机制；配对仪表化，不把全wall差当NN成本|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本行原图表/统计实验实际0；未以数学组件或端点候选填入数据。|最近邻成本随树增大与RSS奇异邻点距离、局部失败阶段机制；配对仪表化，不把全wall差当NN成本；原图注/正文条件差异、分母和统计方式仍须冻结并如实保留。|
|P4-T25-AUTHOR_RAW_LINEAGE|逐作者raw版本/条件/分母/统计脚本到最终论文数值的来源链，筛成功和手填点差异明确保留|UNKNOWN|NOT_ATTEMPTED / NOT_ATTEMPTED / NOT_ATTEMPTED|本项本次新增实验0；保留R1审查及旧R2快照，不把其他义务的组件计数当作本项验证。|逐作者raw版本/条件/分母/统计脚本到最终论文数值的来源链，筛成功和手填点差异明确保留；原规模保持，尚须冻结条件并实际执行。|

## 一致性核对

通过逐值与ID检查：211/211唯一ID及顺序与R1/旧R2完全一致；30父项与181子项完整；R1前30字段逐值不变，旧R2新增5字段逐值不变；45个Table I子单元每项500，合计22500；全部行有当前实证和剩余内容；MD/CSV各211个明细ID同序；当前没有FULL状态。状态分布只作文件一致性统计，不是科学完成率。

当前状态行数：{"PARTIAL": 46, "NOT_ATTEMPTED": 164, "DEFERRED": 1}。

源表SHA256：R1 `2848a61b9321ebfcdb974c2d1275a95c1fe63892baeeb75bbc101b74103e21ed`，旧R2 `c2460634ef7268bea26d41bc5ee705fdc880b0883598a571b58cf3dc0256298b`。
