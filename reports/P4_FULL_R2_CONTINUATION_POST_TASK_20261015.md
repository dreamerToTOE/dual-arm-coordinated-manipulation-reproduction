# P4 R2断点接续：中心、奇异fiber与保存RSS碰撞资格

2026-10-15。P4完整论文仍为**部分完成**，正式Table I规划 **0/22500**。本阶段继续原工作树及原分支，没有重新初始化、重做R0/R1、覆盖旧失败或进入P2/Isaac。

## 恢复状态及已完成前缀

实际仓库`/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full`，分支`p4-full-reproduction-pcs-study`。接管时本地`a39e963`领先远程`356a3b1`五次提交，另57未提交文件8,482,891字节；先归档与manifest，再原字节提交`0792acf`。六工作树保留，无残留科学试验进程。最新fetch没有远程分叉。完整恢复过程见`P4_FULL_R2_RECOVERY_POST_TASK_20261015.md`。

R1的1826项检查（1580通过/246失败）及旧R2空间2088/2091、平面233/233和NR56/56均是保留的历史结果。旧空间NR154合法闭合/6闭合后限位拒绝、IV三项正控FAIL不改；新IV局部24输入通过不替代原失败。原12端点闭链FAIL保持，A01与A02分列；最新12个RECONSTRUCTED端点通过固定主动角、原支、原界及源离散碰撞策略资格。四个A01 UNKNOWN保留，A02只修我方TCP观测后重放保存候选。

VI独立RSS初组868构造，7/30请求找到合格候选；Q2再36构造，全部节点合格而四半严格桥depth3仍UNKNOWN。没有把节点合格、原source的0.05提前返回或0.35奇异捷径当成严格桥通过。所有原构造、输入、源码与日志保留。

## 本阶段三项真实运行

|运行|冻结源码提交|真实调用|结果|wall s|CPU s|
|---|---|---|---|---:|---:|
|CENTER_IMAGE01|`57ca473`|2固定active FK/J，0候选/IK/NR/碰撞/采样/规划|原center四active弦方向不在指定rank5像内|0.208154164000|0.208192000|
|FIBER_COMPONENT01|`b6e40a4`|6固定候选，36数学+18adapter内部FK/J，6碰撞/798PQP pair|6/6，PASS_COMPONENT_DISCRETE_ONLY|1.185148035998|1.167442000|
|SAVED_RSS_COLLISION01|`ca2c553`|48旧分支一次碰撞补验，96native/aligned查询，192内部FK/J，9996PQP pair|26clear/22碰撞；无未执行尾项|13.069952120997|12.882597000|

原始运行完整路径均为`results/p4_full/20261015_R2_<上述后缀>/`。每项在源码与协议提交冻结后单次执行，独占claim保留，禁止换run名称重复消耗预算。随机种子：上述三项均无新随机流，固定输入直接绑定旧B construction219/643和原II/III/V observations顺序。B原种子`[7,23,41,101,20261013]`不变，γ=0.2保持；本阶段γ规划事件0。

实际命令（仓库根目录）：

```sh
python3 scripts/diagnose_p4_full_r2_vi_rss_center_image.py --protocol configs/p4_full/r2_vi_rss_center_image_diagnostic_v1.json
python3 scripts/qualify_p4_full_r2_vi_rss_fiber_component.py --protocol configs/p4_full/r2_vi_rss_fiber_component_qualification_v1.json
python3 scripts/qualify_p4_full_r2_saved_rss_collision.py --protocol configs/p4_full/r2_saved_rss_collision_qualification_v1.json
```

协议、runner和依赖SHA完整保存在各execution；碰撞v3 manifest SHA `c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388`。VI仍复用原v2的native二进制，IV/V观察修复不改变VI。作者源码/网格只在外部只读快照，不搬入公开仓库。

## VI根因及可支持的科学结论

固定中心直接求值的像外残差：219负/正为`1.147547689397e-5`/`1.244607455200e-5`，643负/正为`7.088385268660e-6`/`7.331088181478e-6`（平移mm→m、旋转rad）。独立保存矩阵复算一致。支持**OUR-RECONSTRUCTION局部投影图问题**：固定主动关节直弦在原指定腕族状态处不满足有限可微局部lift必要条件。该证据不排除非C1、非线性主动曲线、奇异fiber运动或全局路径，不能归为论文理论错误。

六点仅改变指定臂`q4+=theta*f`、`q6-=theta*f`，其余16角与q5=0逐值不变。原X-Y-X腕结构使整条fiber保持末端位姿，实际六点又检查两闭环、三臂原位姿、原界、指定秩5/另一被动6/passive11/full12、独立physical/body Jacobian秩和meeting branch_set[1,3]。独立保存矩阵审查谱最大差`2.665e-15`；双闭合最大约`9.095e-13mm`/`1.665e-15`旋转矩阵差，原界最小余量`.43239801390092225rad`。

219两侧各两叶约`.001262431085`/`.001371065015rad`；643两侧单叶`.002282057371`/`.002344348440rad`，均严格小于h=.0025。6次源碰撞均clear，798个PQP返回码全0。四fiber端点的一阶image残差降至约`6.6e-18–9.6e-18`，仅为接入设计的一阶相容证据。**regular↔fiber仍未测试**，原Q2 UNKNOWN不变，不能称原作者RBS、完整RSS或连续碰撞通过。

独立审查：`P4_FULL_R2_VI_RSS_CENTER_IMAGE_REVIEW_20261015.md`、`P4_FULL_R2_VI_RSS_FIBER_COMPONENT_POST_REVIEW_20261015.md`。旧已绑定的保存根因JSON/MD保持原字节。

## 旧48个RSS分支的真实碰撞结果

|环境|固定数学合格分支|selected aligned clear|selected aligned碰撞|剩余资格|
|---|---:|---:|---:|---|
|II|18|10|8|原mode0零候选FAIL保持；奇异分支桥/RBS/完整采样与规划未证|
|III|22|16|6|原mode0零候选FAIL保持；奇异分支桥/RBS/完整采样与规划未证|
|V|8|0|8|缺collision合格正控；不能推出整个wrist模式无解|

只使用旧`20261015_R2_RSS_CONSTRUCTION01`中已有true资格标记的全部48行，原数组/顺序/模式/周期代表逐值绑定。没有重新做700目标/5600IK，没有新增候选、IK、NR、RNG、RBS或规划。native/aligned两种源结果和TCP差全部保留；clear只在已资格selected aligned源策略范围内有效。

原source checkEE与原采样控制流未执行。V源singular还要求两TCP z≥10mm；即便只读保存pose可计算高度，也不能称执行了原checkEE。当前源输出不含逐pair碰撞身份，仅返回总collision和query错误码，不能据9996个零错误码定位碰撞实体；零错误码表示查询成功，不表示无碰撞。不能用一批碰撞候选证明模式不可达。

完整实体几何、遗漏pair、自碰撞覆盖及CCD仍未证。ABB源rod三角形共线，source-policy clear不是实体杆面证书。source-native、物理基座aligned和我方重建分别报告，不能混为原作者原生执行。

## 实际预算与完整义务

原9run快照保持不改；新增V2账目`results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V2.json`逐份加12个execution自身wall_s/cpu_s一次：**95.365357389998秒墙钟、45.058033秒CPU**，原R2余`3504.634642610002wall / 7154.941967CPU`。不重复相加cumulative、controls result或工程构建。

VI B累计 **910/960构造**，`54.513982463999wall / 13.327177CPU`；余 **50构造 / 125.486017536001wall / 346.672823CPU**。旧48补验只扣R2总账，不扣VI B子账。预算未重置，后续不能用旧56余额再领取一次。

最新完整范围表：`P4_FULL_R2_CONTINUATION_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md`，211唯一ID、顺序和全部原文规模保持；CSV前47列逐值保存上份恢复表，新current列报告本次。完整正式Table I仍45单元×500次、1000s/call=22500次；500000配对投影、约50000合法点对、Fig.3–5、Table II、全部fixed partition、无障碍/复杂障碍/窄通道及PCS优势实证义务均未缩减。

下一项从实际未通过资格继续：VI regular↔fiber接入需独立固定方案及原960构造预算边界审查；其他环境普通PCS/NR与原搜索器薄整合并行准备，不调用solve，先冻结数值等价与局部RBS资格。SBL source奇异概率实际.05、RRT/Bi-RRT .2的差异另列，VI重建γ=.2不改；作者SVC控制流可疑返回必须留证，不能静默修后叫原生。

全部相关资格通过后再运行合格小规模成本测算、报告正式资源，未批准大规模规划不执行。P4未结题，完整中文Word/PDF和双FR3适用性专章留待真实完整实证后生成；最终最新范围表先交用户审查，不自动进入P2/Isaac。
