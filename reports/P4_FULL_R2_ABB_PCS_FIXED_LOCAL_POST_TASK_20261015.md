# P4 R2 ABB PCS固定局部接口 POST-TASK

2026-10-15。II/III固定局部资格为**部分完成**。R2数值修复10/16固定局部边通过非阈值提前返回的真实RBS和回溯；6个端点拒绝，未更换h、分支或中心。作者原数值16局部端点均未达到独立资格。三种PCS搜索器已链接，规划求解0，完整论文仍部分完成。

## 来源、执行与判据

原作者CKCplanning固定909bd72；工程协议aa57c24，实际构建四目标author_native/geometry_consistent×plain/trace，source及三个planner主体保留。source-native与R2数值使用同一输入和选定branch；只后者调用已审查spatial_ik_patch。观测版本与plain逐请求比较逻辑返回/配置/路径，不用trace耗时冒充原规划性能。源随机重载与sample_q已知控制流问题原样留存，本资格没有调用这些路径。

```sh
python3 scripts/build_p4_full_r2_abb_pcs.py --protocol configs/p4_full/r2_abb_pcs_engineering_v1.json
python3 scripts/qualify_p4_full_r2_abb_pcs.py --protocol configs/p4_full/r2_abb_pcs_local_v1.json
```

工程记录results/p4_full/20261015_R2_ABB_PCS_BUILD01，科学记录results/p4_full/20261015_R2_ABB_PCS_LOCAL01，后者source_commit=95851e093ae24065887ab3e9b44a0b69e8e033c2。完整协议/source/input/build SHA及exclusive claim已保存。固定输入为既有A01的II/III起终点，不重新恢复；四中心×两active角色×八原branch，后续仅16个冻结主动首关节±h。h=min(.08,原界余量/4)，原RBS_tol=.05/maxdepth150不变。碰撞保留原native内部返回，外门用已合格v3 aligned原mesh/pair/8mm策略；不证明遗漏pair、完整实体杆或CCD。

独立门：闭链位置maxabs≤1e−5mm、旋转元素差≤1e−5，native FK与独立FK位置≤1e−7mm/旋转≤1e−10；主动角精确不变，原branch/原界合法，源离散碰撞clear。端点有效后才进源RBS；每个成功投影事件独立检查，路径中点须逐值有本次资格记录，相邻距离严格<.05，至少一个真实中点/回溯投影才能算nonvacuous。

## 结果与失败证据

|R2数值局部输入|结果|保存证据支持的原因|
|---|---|---|
|II start/active1/负|端点拒绝|闭链、branch、界通过，aligned源离散碰撞|
|II start/active2/负|源投影false|保存目标cosphi=1.137665，几何workspace门拒绝|
|II start/active2/正|源投影false|保存目标cosphi=.655912，低于此branch原q3下界所需.8381922412|
|II goal/active1/负|源投影false|保存目标cosphi=1.269945，几何workspace门拒绝|
|II goal/active1/正|源投影false|保存目标cosphi=.631609，低于原q3下界所需.8381922412|
|III goal/active1/负|源投影false|保存目标cosphi=1.093937，几何workspace门拒绝|
|其余10项|局部边通过|端点、中点、原RBS/回溯、保存路径及各独立门通过|

上述5个源false只对保存target做必要标量不等式复核，没有新构造关节解、运行IK/FK或换输入。原source拒绝是本有限输入下正确的几何/原界拒绝，不是新算法bug或论文错误。仍按冻结门保留PARTIAL：II start主动arm2及II goal主动arm1没有本固定h的局部正控，不能把10成功升级为16成功。

作者原数值5个sourcefalse、11个source true但闭链位置残差6.7321e−4至1.9706e−3mm超过1e−5，全部不进入RBS。其native FK仍与独立计算一致，不能归因FK错误；与既有IK近似π/分支数值问题相符，保留源返回及残差，不改判原端点或旧R1失败。

180组plain/trace逻辑对完成；320顶层project、20顶层RBS、20顶层回溯。trace固定投影442（364成功输出均独立复验），trace native FK1170；plain额外观察FK164由其82条native_checks确认，plain算法内部FK/IK/PQP仍为UNOBSERVED，不能将1170当全部native调用数。数学FK752、逻辑v3碰撞368、adapter内部FK/J1472、adapter PQP78252、源trace内部PQP29618。所有计数是保存实测边界，不填最坏帽。44个下游模板按预置有效端点gate不执行，非超时未完成；没有超时、异常或未保存科学前缀。

独立审查：reports/P4_FULL_R2_ABB_PCS_FIXED_SOURCE_PRE_REVIEW_20261015.md及P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_20261015.md；实际拒绝代数、逐请求哈希、路径叶与计账见POST审查。工程成功不代表算法成功，局部成功不代表随机PCS、全局规划、解上换链或PCS优势。

## 预算、完整覆盖与继续位置

工程wall94.59233520399721s/CPU130.109068s，科学wall81.1323500819999s/CPU78.392314s，分别在冻结180/360和120/240帽内。新增V4将14个science+1个新engineering自身消耗各加一次，工程保守纳原R2总帽：wall285.28806236599576s/CPU264.43608s，余3314.7119376340042wall/6935.56392CPU。旧9/12/13run快照不改；VI B仍974/974、候选余0，不从时间余额再领候选。

新完整表P4_FULL_R2_ABB_PCS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md前68列逐值保留上份INGRESS211行，另列pcs_*新状态。正式Table I仍0/22500，500000配对投影、约50000合法点对、Fig.3–5/Table I–II、全部场景/换链/固定划分/去障碍义务不减。新历史保全V4确认1028旧科学文件、57崩溃文件、备份与五其他工作树/13未跟踪文件不变，旧V2false及V3浮点解释都保留。

继续IV原wrist100×8数学资格以及其他环境普通PCS/NR接口，均独立冻结；之后需处理源随机采样控制流并验证全方法栈，相关设计及预算要具体可审查。全资格和真实pilot之前不启动正式大规模规划。P4最终完整中文Word/PDF及双FR3适用性专章仍待实证，结束先交最新范围表审查，不自动P2/Isaac。
