# P4 R2 VI RSS regular↔fiber组合离散资格 POST-TASK

2026-10-15。固定64/64新节点通过，四半桥在既定严格离散门下接到匹配fiber，经已验证fiber组件返回原center。状态为 **PASS_RECONSTRUCTED_COMPOSITE_DISCRETE_ONLY**。原Q2 **UNKNOWN_OR_FAILED** 保留；P4全文仍部分完成，正式规划0/22500。

## 授权、源码、参数与实际命令

用户明确批准原960候选上限增加14至974，以及版本化独立组合设计；本项64中原余额50+新增14，本项30wall/60CPU，累计180wall/360CPU不扩，未批准正式规划。批准逐字原文保存于`configs/p4_full/r2_vi_rss_ingress_composite_user_approval_20261015.json`，SHA `c9ae237e61bf578ba508d72e757e6b0867216e0adbd8093452fcd4da934356dc`。

执行源码提交 `243fa059aa9512d9b2fa9a48fdf7e18cbdf43e74`；runner SHA `3903e21f8429825b7e1d3a02819552b09644ebdbf0b10140ea7292d204538843`；冻结协议 SHA `592ca2321a48ca1745d833226947ef86e5c483ec7fc337950bf7db51476b3379`。实际目录 `results/p4_full/20261015_R2_VI_RSS_INGRESS_COMPOSITE01`，execution SHA `784dcf0be2e85e28114c8cf9b54b96cff76b2775607967b68caf5af22840fb3a`。全部来源/输入/prior SHA保存在execution与V3账目，未改旧source/protocol/数据。

```sh
python3 scripts/qualify_p4_full_r2_vi_rss_ingress_composite.py --protocol configs/p4_full/r2_vi_rss_ingress_composite_qualification_v1.json
```

0新随机流，固定B construction219/643与原Q2 depth3叶，原B种子[7,23,41,101,20261013]只作来源；γ=.2、δ=.01、h=.0025、原几何/近似π物理基座/抓持/限位/PQP策略均不改。复用40旧q，新增64点按冻结full18算术中点保active1前6，原解析支与原最近合法2π规则闭合arms2/3。原center没有替换或canonical化；旧树与旧UNKNOWN保留。

## 真实结果及四处接入

|fixture/侧|新合格节点|regular叶|regular最大叶距rad|贴fiber实际叶距rad|结果|
|---|---:|---:|---:|---:|---|
|219/负侧|24|32|0.00172602516109385|0.00172602516109385|严格离散PASS|
|219/正侧|24|32|0.00185084971217464|0.00174751783661607|严格离散PASS|
|643/负侧|8|16|0.00148895161566975|0.00148652769635875|严格离散PASS|
|643/正侧|8|16|0.00149109530378192|0.00149109530378192|严格离散PASS|

64节点均闭合、原界合法、固定唯一branch及body/physical秩一致；保存body秩64次均arm2=6/arm3=6/passive12/full12，independent physical full/passive均12。保存残差最大位置 1.1937117960769683e-12 mm、旋转矩阵元素差 1.574296248918472e-13。96条regular叶逐条由保存q独立重算，范围 0.0014865276963587466–0.0018508497121746436 rad；6条已保存fiber叶亦重新核对<h，合104节点/102边。该只读复核不重新调用FK/J或重做科学资格。

实际1024 IK支、64 native F、704数学arm FK/J（target64+accepted根256+body192+physical192）、192adapter内部FK/J，合896；64碰撞均CHECKED/clear，未确认请求0。64成功、0候选失败、0超时、0未执行尾项；无换点/改阈值/自适应加深/重试。原样本219/643指定分支负1/正3、另一被动3、active1分支1均保留。

## 根因修复范围及仍未证明内容

原固定active直弦在原奇异腕状态处的一阶像不相容属于OUR-RECONSTRUCTION局部图/连接设计问题；本项用已资格同位姿fiber锚点和离散fiber自运动显式接回原center，解决这两个fixture的组合离散接入门。它没有修改原Q2算法/深度/失败，也没有证明作者数学错误或原全局无路径。

新规则不是作者原生VI RSS/RBS忠实实现：公开VI singular RBS不完整，source .05提前返回和7*.05奇异捷径未被用于本严格门。source-policy clear只覆盖原已资格mesh/pair/容差，遗漏pair/完整实体/CCD和任意连续lift均未证。未验证全部奇异模式、原RSS采样分布/γ混合事件、全局RSS/PCS/NR、搜索器或Table/Fig统计。只有本有限组合组件通过，不能升级整个RSS或P4完成。

## 实际13run账目、历史保全与下一步

|run|源码提交|wall s|CPU s|执行状态|
|---|---|---:|---:|---|
|20261015_R2_COLLISION_CONTROLS01|`17da8c3`|0.021082576000|0.022198000|SOURCE_POLICY_QUALIFIED|
|20261015_R2_ENDPOINT_COLLISION_REPLAY01|`0465ad8`|1.321430518001|1.324637000|EVIDENCE_RECORDED|
|20261015_R2_ENDPOINT_RECONSTRUCTED01|`8188e93`|7.450141228001|6.025647000|QUALIFICATION_EVIDENCE_RECORDED|
|20261015_R2_IV_NR_LOCAL01|`b686e7b`|2.651571520000|0.882651000|FINITE_LOCAL_PROPERTY_PASS|
|20261015_R2_PLANAR01|`28cd986`|0.111326417000|0.112283000|COMPONENT_EVIDENCE_RECORDED|
|20261015_R2_RSS_CONSTRUCTION01|`98d999a`|1.502717416000|1.015161000|FIXED_COMPONENT_CONSTRUCTION_RECORDED|
|20261015_R2_SAVED_RSS_COLLISION01|`ca2c553`|13.069952120997|12.882597000|SAVED_48_CANDIDATES_SOURCE_POLICY_CHECKED|
|20261015_R2_SPATIAL01|`1fa1778`|14.723153130000|9.465682000|COMPONENT_EVIDENCE_RECORDED|
|20261015_R2_VI_RSS_BRIDGE01|`2f465d6`|7.987086492001|6.310368000|LOCAL_BRIDGE_QUALIFICATION_RECORDED|
|20261015_R2_VI_RSS_CENTER_IMAGE01|`57ca473`|0.208154164000|0.208192000|FIXED_CENTER_FIRST_ORDER_DIAGNOSTIC_RECORDED|
|20261015_R2_VI_RSS_FIBER_COMPONENT01|`b6e40a4`|1.185148035998|1.167442000|SINGULAR_FIBER_COMPONENT_RECORDED|
|20261015_R2_VI_RSS_INGRESS_COMPOSITE01|`243fa05`|14.198019690000|10.876665000|FIXED_COMPOSITE_QUALIFICATION_RECORDED|
|20261015_R2_VI_RSS_RECONSTRUCTED01|`3fad1b5`|45.133593772000|5.641175000|CANDIDATE_CONSTRUCTION_RECORDED|

本项实际wall=14.198019690000365s、CPU=10.876665s；13run累计wall=109.56337707999865s、CPU=55.934698s，R2余3490.4366229200014/7144.065302s。B累计974/974候选、wall=68.71200215399949s、CPU=24.203841999999998s，候选余0，原时间余111.28799784600051/335.796158s；时间余量不能自动转成新增构造额度。

新V3逐execution原值只加一次，不相加cumulative或重复controls result；工程构建/未运行草案/本保存分析均不计科学run。旧V2及CONTINUATION表56列/211ID逐值原样保留，新范围表`P4_FULL_R2_INGRESS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md`只加ingress_*列；全部原统计分母不变。历史SPATIAL01的run_qualification.py原SHA与当前后续版本不同，已在其source_commit中核对原SHA，账目保留两者，不将版本差异伪作原数据损坏。

下一步继续D079未完成的普通PCS/NR及原搜索器薄整合、IV原wrist100×8数学资格、II/III奇异桥与V碰撞根因；这些工程/草案尚未运行，不列作完成。正式规划先完成各门与有限成本测算再报告资源；新增设计/额度仍须另审，B不得自动重跑。22500正式规划、500000投影、约50000合法点对、Fig.3–5/Table I–II及全部PCS优势/消融义务保持。P4完成后再更新中文Word/PDF与双FR3适用性专章，先把最新完整范围表交用户审查，不自动P2/Isaac。

本报告为保存数据汇总，科学调用0。纯分析账wall=0.36599221299911733s、CPU=0.364453s（不含最终序列化），单独列在V3；不重跑旧汇总脚本。
