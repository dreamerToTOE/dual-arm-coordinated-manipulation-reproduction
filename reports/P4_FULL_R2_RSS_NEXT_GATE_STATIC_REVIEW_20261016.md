# P4 R2 RSS 下一门：保存证据与源码静态审查（2026-10-16）

结论：六环境均未取得合格的完整 RSS 规划路径。下一项可继续做 ABB 原生 RBS 的分支/奇异标记/检查与回溯契约静态映射；IV 接着冻结旧六根的碰撞与 checkEE 资格。VI 974/974 已耗尽，固定组合的离散通过不能推广为通用 RSS/RBS；新生产分布或通用连接器须先作科学设计裁决。

本次仅阅读既有源码、报告、保存 JSON/CSV；只新增本 Markdown 与同名 JSON。编译、项目模块导入、协议/prior/claim 生成、二进制、FK/IK/J、碰撞、采样、RBS、solve、新候选与正式规划调用均 **0**。未改源码、协议、账本或211表，未重做 R0/R1。审查基线 HEAD `909d6aa4f41bd28de85676f3d32b4a82d5d96e20`；本报告不是新的实验 PASS。

| 环境 | 已有可用证据 | 原生 RBS、分布与入口当前门 | 最早继续处与设计边界 |
|---|---|---|---|
| I | 平面运动学/NR资格不构成RSS证据；最新表RSS_I仍NOT_ATTEMPTED。 | 已审作者 run/planners/validity_checkers 无RSS/sampleSingular/gamma命中；HB用GD投影与APC角色分支RBS，不能改名RSS。 | 先解决平面RSS源码/资源映射。若独立定义奇异被动链与跨分支桥，属RECONSTRUCTED新设计，须审查；不能套用空间6R公式。 |
| II | 300目标/2400根：7目标18分支数学合格；mode0/1/2为0/3/4。旧18根aligned源策略离散碰撞10clear/8collision，3目标有clear根。 | 作者三RSS规划器源码在；原生奇异RBS/回溯和RSS路径未过；固定分层不等于随机分布实证。 | 先静态映射原生sg、branch、check/reconstruct，再冻结旧clear候选的有限非平凡桥资格。更换mode0输入或新增连接器须单列预审。 |
| III | 300目标/2400根：8目标22分支数学合格；mode0/1/2为0/3/5。旧22根16clear/6collision，5目标有clear根。 | 与II共享ABB来源，但本环境桥与入口资格仍须单独成立。 | 同II；不得以II证据替代III。 |
| IV | fixed100/800已完成，6根/3目标（s040/s056/s092各b1,b3）通过独立数学闭合/真实秩/原界/分支；794拒绝。 | PASS_RECONSTRUCTED_MATH_ONLY；碰撞、原RBS、分布、路径未过。作者sampleSingular碰撞/checkEE行被注释，RBS的withObs路径则检查两者。 | 旧六根的输入绑定、碰撞/checkEE谓词对照有明确验证路线，先冻结有限预算；不重跑100/800、不用剩余时间换目标。 |
| V | 100腕目标/800根：4目标8根数学合格，旧8根aligned全部collision；保存TCP高度2根低于10mm，6根满足高度，原checkEE未运行。 | 聚合PQP返回码均0仅表示API调用成功；缺pair身份，碰撞根因UNKNOWN。RSS原生RBS/路径未过。 | 先静态设计旧8根pair级可观察性；若重放需冻结原输入、有限预算。不得随机替换旧失败、断言整个腕模式无解或归因论文。 |
| VI | 974/974耗尽；旧Q2四半桥UNKNOWN保留。批准fixed64后104节点/102边组合离散通过，四半桥接到对应fiber并保留原center。 | 原source仍两臂sampleSingular残留；奇异RBS有q3未声明、dsg2及递归参数残留。原生完整RSS/RBS/生产分布/入口未验证。 | 可继续零调用数学/源码契约诊断。把固定fiber组合推广通用算法、选择奇异臂分布或新增候选，均须新科学设计与预算裁决。 |

所有 clear 仅指既定 aligned 离散源碰撞对/mesh/tolerance 策略；不含完整物理几何、遗漏碰撞对或连续碰撞证书。PCS/NR 已有路径不能资格替代 RSS。

## 三个必须在入口前固定的源码差异

1. **抽样概率并非所有原源码都为0.2。** ABB `sampleSingular`在请求开始用`rand()%3`选模式一次，拒绝循环内不重选；Comau IV/V及VI残留代码硬编码mode1，即腕模式。RRT非goal抽样分支用0.2，CBiRRT用0.20；本次静态发现全部四份空间SBL文件实际`uniform01()>0.05`走regular，否则sampleSingular，注释却写20%。因此SBL字面源为5%分支概率，不能按注释报20%。原文/冻结γ=.2义务保持；将作者字面.05与修为.2的版本分开，执行前解决科学参数归属，不静默修改。尚无新的随机频率测试。
2. **原生RBS与独立严格叶距门有不同语义。** 作者常规叶门0.05、maxdepth150；奇异重载先投影中点，在ABB距奇异center小于15×0.05、Comau小于7×0.05时可提前true。回溯同类提前停止需逐函数映射。这是源码语义证据，既不能充当严格叶距/连续证书，也不能单凭差异判论文方法错误。最小下一门为RRT/CBiRRT/SBL的sg方向、分支身份、checker返回与reconstruct节点覆盖对照。
3. **修正集合、固定失败与论文理论分别记。** R1独立反例表明含偏置的原固定q3=−PI_/2不保证真肘奇异；修正条件sin(q3+α)=0，ABB α=atan2(302,70)，Comau α=atan2(1436.5,210)，保留SOURCE-CORRECTION身份。II/III旧mode0各100目标腕心距离均超过580.0064515457702mm包络（II685.046247–2008.590441，III815.207142–2498.758159）；仅解释这些固定输入，不证明整个mode0集合为空。已有analytic witness仍是手选未执行候选，不能替换旧0/100。肩部ρ=0未被原三模式穷尽，各分支全局连接仍UNKNOWN。

## 执行次序与预算边界

继续PCS/NR既定主线与RSS解耦。RSS先完成上表零调用的source contract；若准备有限原生资格，冻结确切旧输入/版本、分支、函数、完整停止条件、独立校验与成本上限，再在授权覆盖内执行。IV旧六根资格和V旧八根pair诊断已有可审查的验证路线，仍不能绕过冻结过程。I新平面构造、VI通用生产采样/连接器、新模式或概率裁决属于新增科学设计。

VI额度剩0；旧累计B为68.71200215399949wall/24.203842CPU，时间余额不授权新构造。IV原01+02固定100/800耗尽。所读V19账37执行（29科学账项、8工程），保守入账719.515705375994wall/597.908923CPU；历史未测尾部边界仍UNKNOWN。本审查不增加科学账，也不把root后续工程进度反向写入此固定快照。

所读最新211表为`P4_FULL_R2_CBIRRT_NR_BUILD_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv`（211×162）；旧`current_status`是保留历史，IV应同时读`iv_fixed100_actual_status=PASS_RECONSTRUCTED_MATH_ONLY`，不能只用旧NOT_ATTEMPTED列。Table I仍0/22500，45×500与1000s、Fig3–5/TableI–II、投影/局部可见性/复杂障碍及全部211原文义务不减；先端到端资格，再可重复成本pilot和正式预算审查。无P2/Isaac/FR3实施。

## 字节级来源

同名JSON保存全部25份本仓库输入与35份作者源码的实际SHA256、来源版本、六环境门和211表所读列。作者快照：CKCplanning@909bd72、planar_ckc@e5edcb58、ckcComau2@80089340、ckcComau industrialScene@ef6e9c4、ckcComau3@25488a86。

| 关键输入 | 实际SHA256 |
|---|---|
| 211×162表 | `9f5ca144542bfb788f3e220c3ada045db751a9ea45ad41d201de1b41e1836a94` |
| ABB RSS validity source | `133e1f7036583b3e6a5ae9d9df978a679df9af88c5103d195e727546934fd8c6` |
| ABB SBL RSS source | `1a52d9fae20d0aa98f7c22c28139c581ac6e20451f8a4ab17f6e242826a9c2fc` |
| IV source | `a8d4d705419b47657f95b0ed4cbf7c00e147f15f927e7c2a6d6b9b6057c0eaf1` |
| V source | `50223b4723583984e4b994eaa0bfb577aacbe7ce76a72e9da50a55075f28745f` |
| VI source | `0b6c611fb2fb053277310781eb2c54150956e55832fc9c9f29ee90175e015ddf` |
| IV fixed100 execution | `8dc596f33a20a6ba4d4ed57b060992689e549b20e2c2603763386449695e6069` |
| VI ingress execution | `784dcf0be2e85e28114c8cf9b54b96cff76b2775607967b68caf5af22840fb3a` |
| 本次JSON | `1b5fdb2a4379a5dc3e7c52b8fe337816e342903592f45a30d2107e47ef906ac2` |

全部输入在写报告前后哈希相同；未提交或推送，由主代理审阅后统一交付。
