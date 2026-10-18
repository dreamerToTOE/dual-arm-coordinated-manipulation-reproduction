# D080 RSS II–V 下一资格：增量静态接续（2026-10-18）

**最早未通过的是II/III保存奇异根的被动arm2分支身份，不是重新生成奇异候选。** 原source contract与26个clear输入可以复用。已有fixed32 supervised V2从未执行，仍绑V25旧账；不能直接以当前余量启动。PCS/NR主线继续独立推进。

本项只新增本MD/同名JSON；项目import、describe、编译、FK/IK/J/SVD、碰撞、RBS/回溯、随机/采样、solve、候选、claim、账本/211表写入均0。只读核对28份II–V作者源码和旧contract的38份绑定输入，SHA全部与旧证书相同；未重复R0/R1数学验证。基线`f6ac8f786e835c04877e2664932a5516a3699395`。VI仅历史归档，不新增源码分析或任何运行；环境I不在本增量内，仍保留D080义务。

## 1. 旧证据直接复用，不能跨层升级

| 环境 | 已保存证据 | 最早未过门 |
|---|---|---|
| II | 300目标/2400根，7目标18数学根；10 aligned clear / 8 collision | 固定输入的arm2分支、原奇异RBS与trace；无RSS完整路径 |
| III | 300/2400，8目标22数学根；16 clear / 6 collision | 同源契约复用；环境本身的分支/碰撞/桥资格独立 |
| IV | fixed100/800完整；s040/s056/s092各b1/b3，共6数学根、794拒绝 | 原六根collision/checkEE；不重跑100/800或新增目标 |
| V | 旧8数学根aligned全collision；保存TCP高度2低于门、6满足，非原checkEE执行 | 原8根pair级诊断；碰撞根因仍UNKNOWN，不替换失败样本 |

II/III旧`active_branch`是构造**arm1**的标签；RBS `active_chain=0`反解**arm2**，不可直接代入。原`-2`仅规划器奇异标志，不能替代真实rank。四个regular端点证书可复用：II_0 arm2 b3、II_1 b0、III_0 b1、III_1 b3。全部26个clear都是奇异候选，不是已经合格的regular邻点。

原固定四点仍为II_obs0681、II_obs0689、III_obs1065、III_obs1073（各环境mode1/2首个clear），完整q12、原构造branch1、原record hash均保存。四点旧rank=5且aligned pose一致/离散predicate=0；各自原native碰撞谓词也返回0，但TCP仍`COLLISION_PHYSICAL_TCP_MISMATCH`，不能称原native物理资格。II每variant116、III103条保存PQP query。所有clear仅原pair/mesh/8mm离散策略；没有CCD或遗漏pair证明。

## 2. γ与入口：源码事实和论文条件分列

本地原论文accepted manuscript **p5 IV-A末段**明确RSS使用一个被动链，profiling后取γ=.2（同名JSON只记录私有PDF SHA，不上传原文）。作者源码三个空间来源都存在：

| 源文件（asset快照根下） | 原字面奇异请求阈值 | 位置 |
|---|---|---|
| CKCplanning/planners/RRT_RSS.cpp | 非goal分支.2 | 158–170 |
| CKCplanning/planners/CBiRRT_RSS.cpp | .20 | 350–357 |
| CKCplanning/planners/SBL_RSS.cpp | **.05，注释20%** | 192–213 |
| ckcComau2 / industrialScene 的RRT_SG.cpp | 非goal分支.2 | 158–170 |
| 同两来源CBiRRT_SG.cpp | .20 | 413–420 |
| 同两来源SBL_SG.cpp | **.05，注释20%** | 192–213 |

完整真实路径/SHA在JSON。这只是请求分支概率，**未测得接受样本分布或RSS成功率**。保留作者原生.05与论文条件.2的不同版本/统计身份；本报告不改γ、不新建随机试验，也不要求重批已明确授权的条件。启动前须在协议中写清既有授权覆盖及版本归属，不能按注释冒称原源为.2。

ABB sampler在一次请求开头`rand()%3`选模式，拒绝循环内不重选；IV/V硬编码mode1腕。IV `StateValidityCheckerRSS.cpp:301`注释了collision/checkEE接收条件，V同位置启用；两者`isValidRBS:519–529`均在withObs时查collision与checkEE。ABB `sampleSingular:255–305`、Comau `259–306`均有不读ptc的拒绝循环，外层solve超时不能单独证明每次请求有界。

三来源RRT在255处禁用了exact赋值分支，approximate fallback不能冒充精确终点。CBiRRT导出是独立的.1插值/固定分支投影，不是原RBS回溯（ABB627–661，Comau696–730），没有导出内碰撞门，n=0/未定分支风险需fail-closed观察，不能故意执行未定义行为。SBL双-2树边的branch=-2风险、lazy和trace优先顺序差异已在旧contract证据化；不以运行负索引作证明。`save2file`局部失败不充分传播，任何“Solved”仍须独立完整路径门。

## 3. 原RBS true与严格叶门各报各的

原常规叶门d<.05、depth150不变。ABB奇异首层投影中点到选定奇异端点<.75可提前true（SVC:468–496）；IV/V为<.35（599–624）。trace同类提前返回发生在插入中点之前（ABB588–624、Comau719–755），可能只导出两端；否则子递归转常规重载。checker/trace的深度计数还有一层边界差异，旧静审直接复用。

因此未来固定桥至少分报`source_return`、实际trace、全部相邻raw-q12叶距<.05、每节点独立闭链/真实秩/分支/完整限位/离散碰撞。原true不能替代严格叶门；严格叶失败就保存失败，不自动加密、换连接器或改阈值。两者都不等于连续无碰撞。这是作者具体程序的契约差异，**不是论文数学已被否证**。

## 4. 下一固定资格草案：复用原四点，不生成新候选

1. **只刷新fixed32工程门再送审。** 原四完整q12×被动branch0…7，32 K+4 F；独立arm FK/J≤40、rank SVD≤36，总帽仍旧10wall/20CPU。原全部数学门不变，结果仅`RECONSTRUCTED_FIXED_SAVED_INPUT_BRANCH_MAPPING_MATH_ONLY`；不重新采样或跑旧构造。旧三稿留存：runner`4839efdf…`、supervisor`fada7f5a…`、template`da3431b1…`。当前仍frozen=false、reviews=false；没有对应result/claim。
2. **不能直接启动旧V2。** runner仍硬绑V25及SHA，当前保存账已V29；旧formal guard只核历史0/22500，缺D0800/18000；旧supervisor尚未按最新保守monotonic-envelope费用/收据策略复审。应只做版本化工程刷新、保全旧稿、复用原科学AST/输入及适用独审，再绑定届时真正最新账。矩阵存储addendum后的runner也必须用适用的新SHA证书，不能拿旧SHA审查通过顶替。
3. **输出collision不能继承。** 仅与旧q12完全相同且来源/判据均未变者可复用旧证书；改变的被动输出须另冻有限collision资格。不能按source true、角差<.1或近似相等免检。
4. 分支门支持后，原contract第5节的最小桥提案仍可保留：II_0↔II_obs0681、III_1↔III_obs1065，active0/passive b3，各正反sg2/sg1，共4 checker+4 trace，旧建议每项≤16中点投影、合≤128。**此处未冻结/未授权执行桥费用**。b3若不合、碰撞或到限，保存失败/UNKNOWN，不临时换点、branch、seed或加深。source early true、strict leaf和数学/碰撞结果分列；没有新connector、NR兜底、solve或正式统计。

只读账快照V29 SHA`8b00cc927468bbe10475b0fc90443efe58560df4ec58b3f23942d4ab346d17ea`：47execution=35科学+12工程，保守累计999.015969348994wall/826.637646000CPU；余量上界2600.984030651006/6373.362354000。**该快照不能充作未来实际prior**，任何新运行前要核对最新账。原TableI事实0/22500、D080批准正式0/18000；VI974/974仅历史保全，不借时间余量。完整图表/投影/可见性/消融义务不缩，本项无新增科研费用。

本项JSON SHA256 `4c9ecc0eb1f48fa1832c80fc6f40100ee8cee9c27344b6ce681b446702c0ad58`，保存28源/38旧输入/四原点/精确行号及未运行边界；写报告前后所有已绑定源和旧输入SHA一致。未提交推送，交root统一审阅与交付。
