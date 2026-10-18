# D080 RSS II–V：最小可证伪下一门

2026-10-18，保存材料只读接续。**下一可执行科学门仍是II/III原四点的被动arm2分支资格；不是新增奇异样本，也不是直接启动RSS规划。** 当前旧fixed32草案从未执行，工程前账/监督策略过期，应先版本化刷新，再由root冻结。PCS/NR继续独立推进。

本项只新增本报告与同名JSON；未编译、导入项目、describe、FK/IK/J/SVD、碰撞、采样、RBS、solve或新增claim/费用。只复用旧NEXT_GATE、SOURCE_CONTRACT和D080增量证据，不重做R0/R1或28源码全审。环境VI不在本报告分析或后续计划内。

| 最早未过门 | 具体可证伪问题与保存证据 | 最小继续路线与拒绝条件 |
|---|---|---|
| II/III被动分支 | 原四点`II_obs0681/0689、III_obs1065/1073`的`active_branch=1`是构造arm1的标签；RBS active0却反解arm2。不能由该标签或`-2`推出arm2可用branch。四点原q12与aligned clear/真实rank5已保存。 | 完全复用fixed4×branch0…7数学草案：最多32K+4显式F、40独立armFK/J、36rank SVD，仍10wall/20CPU并扣原R2总额。保持主动角、原解析分支、完整原输入/顺序/数学门；逐项报原输入与canonical输出、闭链/真实rank/分支/原限位。若预置b3不支持，保留失败，不换点或branch。数学成功仍不是RBS资格；改变q12的输出不得继承旧碰撞证书。 |
| II/III原奇异RBS | ABB奇异shortcut可在距中心<.75时true，trace在插入中点前返回；原true是否同时满足完整导出与严格叶距<.05，尚未实际验证。 | 仅在固定分支与精确状态物理门支持后，另冻旧提案两对`II_0↔II_obs0681、III_1↔III_obs1065`，active0/b3、双方向sg2/sg1，各4checker+4trace；旧提案每项≤16中点投影、合≤128。此报告没有冻结桥时间/CPU。原source返回、原trace、每节点物理门、原raw-q12叶距分列；到限UNKNOWN，不加密、加深或换连接器。 |
| IV旧六根物理门 | `IV_s040/s056/s092`各b1/b3已独立数学通过，794拒绝完整保留；原sampleSingular注释了collision/checkEE接受行，isValidRBS却检查两者。 | 先冻结这六个精确q12的collision与原checkEE谓词对照；保存全部pair/8mm策略/实际TCP与谓词。只读math证书直接复用，不重跑100/800、不新采目标。未有新有限运行预算，先做工程协议。 |
| V旧八根碰撞根因 | `V_obs0081/0083/0361/0363/0401/0403/0569/0571`原aligned均collision；已有aggregate PQP API0不能识别拒绝pair。当前V PCS的24点另有输入，不能替代这八个RSS姿态。 | 为精确旧八根准备pair可观察性与原checkEE对照；未来重放须单独有限冻结。保留8/8拒绝、UNKNOWN；不把新PCS拒绝pair移植给RSS，不据此断言腕奇异集合为空。 |

上述clear仅对应原pair/mesh/tolerance离散策略，没有CCD或省略pair安全证明。

分布与入口的三项诊断应排在上述数学/局部门后；目前只接受以下源码事实，不用固定构造的通过率代替生产分布：

1. **概率与拒绝循环。** 原RRT非goal/CBiRRT奇异请求阈值为.2；三来源SBL字面为.05、注释20%。ABB每请求只在循环外选一次mode；IV/V只用腕mode1。未来分布资格需分别保存regular/singular请求数、模式、每请求重试/接受/外停，不能由请求阈值推导接受率；原`sampleSingular`不读ptc，外层solve限时不足以证明一次请求有界。先设计fail-closed外监督与计数契约，不调用sampler。本报告不改γ；原source .05与论文条件γ=.2必须分版本，未经相应冻结不混统计。
2. **RRT精确终点。** 旧契约已定位`RRT_RSS.cpp:255`的`if(0 && sat)`；approximate fallback不是精确解。下一门先将源返回、approximate标签、导出完整性和起终资格字段固化；不暗改exact开关，也不预言一次规划会成功。
3. **CBiRRT/SBL导出。** CBiRRT serial导出使用独立.1插值/投影，无导出内碰撞门，存在n=0/未定branch风险；SBL双-2树边可能把-2传入8分支数组，lazy与trace方向优先次序不同。先准备wrapper对照与非法输入的fail-closed证据，不为取证执行除零或负索引；guard触发就保存STOP，不能伪称原作者路径成功。任何真实候选都须完整独立路径验收。

来源身份必须保持三列：**AUTHOR_NATIVE_LITERAL**保存作者原字面控制/概率/失败；**SOURCE_CORRECTED**列明既有ABB/Comau几何数值修正与aligned碰撞版本；**RECONSTRUCTED**用于固定数学恢复、独立qualification wrapper或后续经批重建。混合“作者原RBS控制＋修正APC＋aligned碰撞”只能如实标混合来源，不升级原生复现。现有源码问题也不直接升级为论文数学错误。

root可先安排fixed32的纯工程刷新：保全V2三稿，保留原科学AST和两处既有矩阵存储，替换硬绑V25的过期前账为运行时真正最新账、补D080 I–V/正式0/18000门，复用已审Decimal三观测收费与真实进程监督；旧10/20帽不增加。V34仅本报告只读快照：52execution，已收费1113.4602605769917wall/927.6919419999999CPU，剩额仅上界2486.5397394230085/6272.3080580000005；之后有新实际运行必须刷新prior。此报告没有冻结协议、分配新额度或启动实验，正式18k仍0；完整图表/50万投影/约5万可见性/消融义务不变。

精确证据定位：

- D080增量报告`P4_D080_RSS_II_V_NEXT_QUALIFICATION_INCREMENTAL_STATIC_20261018.json`的`readonly_reuse.fixed_four_full_inputs`、`fixed32_existing_draft`、`next_bridge_proposal_reused_not_frozen`；旧分支/sg/导出行号见`P4_FULL_R2_ABB_RSS_SOURCE_CONTRACT_STATIC_V1_20261016.md`第1–5节。
- 四原点位于`results/p4_full/20261015_R2_SAVED_RSS_COLLISION01/`；IV六根位于`20261015_R2_IV_RSS_WRIST_FIXED100_02/IV_s{040,056,092}_b{1,3}.json`，原800分母见其execution；V八根同前述RSS碰撞目录。
- 同名JSON逐文件绑定上述保存输入、四regular端点、旧fixed32三稿/PRE、原契约和本次V34账SHA；没有重新打开或分析VI源码/结果。其输入写报告前后保持原SHA。
