# P4 R2 ABB PCS LOCAL01：保存证据二次审查

2026-10-15。运行源提交`95851e093ae24065887ab3e9b44a0b69e8e033c2`，构建源`aa57c24`，运行目录`results/p4_full/20261015_R2_ABB_PCS_LOCAL01`。本审查只读取保存JSON、stdout/stderr、events和源码，复算计数、距离及保存目标的必要代数不等式；未导入模型、未执行新FK/IK/碰撞/RBS/规划，也未修改绑定资产或原输出。

**结论：原`FIXED_LOCAL_ABB_PCS_PARTIAL`准确。** 10条R2数值版本局部边的真实RBS、回溯、离散闭合/界/branch/碰撞与叶距离均有完整来源；另6条固定局部候选真实拒绝，不能靠换h/seed补成16/16。原数值版本16条局部候选全被外门拒绝，不能称其固定投影合格。两个数值版本分别与其plain/trace对应，并非二者互相等价。全局规划、随机PCS分划及正式统计仍无本项PASS。

## 溯源、原返回和外部门

逐文件复核180个source pair，包括160个直接投影pair、10个RBS pair、10个回溯pair。每pair的两个原始进程输入相同，逻辑`environment/request/status/returned/q12/path_q12`逐字段相等，trace原输出与保存pair记录相同。360个源进程及368个碰撞worker，合728个进程均exit0；process_finished的stdout/stderr SHA匹配实际文件，无run_stopped或process_interrupted。

绑定源码、14项prior execution、原4个A01中心、外部构建源/mesh/binary与运行前后SHA一致。8个根branch选择记录均恰有一个与中心唯一几何branch相同的合格候选，选择与固定距离/branch tie规则相符；没有因碰撞换branch。四个中心重验通过，8个负控按原期望拒绝，原端点失败没有被覆盖。

| 范围 | source true / source requests（trace逻辑请求） | 独立门 |
|---|---:|---|
| author_native直接投影，根+局部 | 41/80 | 41个成功输出均闭合位置超门；native FK与独立FK一致 |
| R2直接投影，根+局部 | 41/80 | 41个数学/原界/branch通过，40个aligned离散碰撞clear、1个collision |
| R2 RBS | 10/10 | 141个实际成功中点投影全部独立合格；原内部282次碰撞查询中的对应141次均clear |
| R2回溯 | 10/10 | 141个实际成功中点全部独立合格，path来源、顺序、端点、叶距离通过 |

R2共323个成功投影事件（41直接+141RBS+141回溯）数学sound，保存闭合最大位置`3.979039320256561e-13 mm`、旋转矩阵`4.440892098500626e-16`；原生FK与独立FK最大位置差`1.7053025658242404e-13 mm`、旋转差`3.3306690738754696e-16`。这些是已运行证据的汇总，没有新算FK。主动角、原全12关节界、几何branch记录均一致。源native的41个成功直接输出位置残差`0.0006732109797553676..0.003476600799302787 mm`，均超`1e-5 mm`，而FK本身受独立支持，故本项是原IK数值/分支闭合问题证据，不能改写为ABB FK错或论文理论反例。

368次v3逻辑碰撞全部CHECKED，native/aligned均有保存PQP code=0及4次内部arm FK/J进入/完成，aligned TCP一致门通过。366次双variant clear、2次双variant collision，无variant结果分歧；两次collision来自同一`II_0_a0_s-1`固定局部输入的原数值/R2数值输出复检。原native碰撞和aligned外门保持分列，未偷偷替换RBS内的原查询。仍只认证原离散mesh/pair/8mm容差政策，不认证完整实体几何、遗漏pair或CCD。

## 六条R2局部拒绝的准确机制

所有h保持冻结值0.08 rad。`source false`不自动等于“几何不可达”。对5条false，仅使用已保存`native_ik entered.args.T`和原ABB常数形成wrist-center必要判据：

`l2=270, L34=hypot(70,302), c=(D²-l2²-L34²)/(2*l2*L34)`。

五条的肩方向均满足q1原界，故可排除更早q1拒绝。若`1-c²<0`，源在q3两连杆几何门直接false。对branch0且`c>-0.22580175235374073`的无wrap区，原q3下界要求`c>=cos(110*3.1416/180-atan2(302,70))=0.8381922412179712`。这只是保存T的标量门审查，没有生成新关节候选或执行IK。

| 固定case | source返回 | 保存证据定位 | 对应解释 |
|---|---|---|---|
| II_0_a0_s-1 / branch3 | true | 数学、界、branch通过；native/aligned collision均true | 普通碰撞拒绝，非IK/RBS失败 |
| II_0_a1_s-1 / branch0 | false | c=1.13766512020864，1−c²=−0.2942819257393394 | 保存目标超两连杆最大几何距离 |
| II_0_a1_s+1 / branch0 | false | c=0.6559121385088346在几何reach内，但小于0.8381922412179712 | 指定解析分支q3低于原−110°界；不能称几何不可达 |
| II_1_a0_s-1 / branch0 | false | c=1.2699452237701871，1−c²=−0.6127608713767108 | 保存目标超最大几何距离 |
| II_1_a0_s+1 / branch0 | false | c=0.6316093608368295在几何reach内，但小于q3界阈值 | 指定分支q3下界拒绝，未证明其他分支也失败 |
| III_1_a0_s-1 / branch3 | false | c=1.0939367830025377，1−c²=−0.19669768520594122 | 保存目标超最大几何距离 |

没有证据支持对这些普通拒绝实施“修复”。本项未搜其他分支、周期等价或缩小h。原数值局部16条另准确分解为5条source false，以及11条source true但闭合位置残差`0.0006732109797553676..0.0019706050834429334 mm`被外门拒绝；这11条不是source自己返回false，不能合写成16次作者IK失败。

## 十条真实RBS/回溯路径

以下每条path首尾与保存中心、对应局部投影端点完全相同，内部q逐节点存在本次回溯的成功投影及独立门记录。RBS、回溯各141次中点，path合计161个节点、151个叶；实际递归叶数与path相邻边数逐条一致。所有源内部collision返回0，所有叶全12L2<0.05，均非阈值提前true。

| case | branch | 原完整距离rad | RBS中点数 / path节点数 / 叶数 | 最大叶rad |
|---|---:|---:|---:|---:|
| II_0_a0_s+1 | 3 | 0.3716493784 | 8 / 10 / 9 | 0.0491634533 |
| II_1_a1_s-1 | 3 | 0.3075234220 | 7 / 9 / 8 | 0.0390226469 |
| II_1_a1_s+1 | 3 | 0.3230744094 | 7 / 9 / 8 | 0.0418561128 |
| III_0_a0_s-1 | 1 | 0.4828240164 | 15 / 17 / 16 | 0.0307641887 |
| III_0_a0_s+1 | 1 | 0.5223571148 | 15 / 17 / 16 | 0.0350692487 |
| III_0_a1_s-1 | 1 | 0.7181762071 | 19 / 21 / 20 | 0.0487004786 |
| III_0_a1_s+1 | 1 | 0.5182067293 | 15 / 17 / 16 | 0.0359736574 |
| III_1_a0_s+1 | 3 | 0.5724840437 | 15 / 17 / 16 | 0.0433468288 |
| III_1_a1_s-1 | 1 | 0.5461686504 | 15 / 17 / 16 | 0.0392881207 |
| III_1_a1_s+1 | 1 | 0.9192200836 | 25 / 27 / 26 | 0.0488092276 |

## 实际调用、预算和未执行范围

| 计数 | 保存原始证据复算 |
|---|---:|
| 顶层project / RBS / reconstruct，含plain和trace | 320 / 20 / 20 |
| trace固定投影 / native IK | 442 / 442 |
| trace成功投影事件独立复检 | 364（原数值41 + R2 323） |
| trace native FK | 1170 |
| plain driver调用后观测native FK | **164**（82个成功project各2次；原execution只列trace，需此补充） |
| 独立数学arm FK | 752=2×(364投影+4中心+8负控) |
| v3逻辑碰撞 / 内部arm FK/J requested=started=completed | 368 / 1472 |
| 原trace内部collision / 实际PQP pair queries | 282 / 29618 |
| v3两variant实际PQP pair queries | 78252 |
| trace RBS / reconstruct递归入口 | 292 / 292（各141内部节点+151叶） |

plain原算法内部FK/IK/PQP仍UNOBSERVED；不得用trace数假冒其计测值。可确定的plain调用后观测FK164已由保存stdout补列，未增加实际消耗，也不重写原execution。预算始终包含这些真实进程CPU/墙钟，所以此展示漏项不造成时间预算漏账。

运行无终止异常，wall81.1323500819999s/CPU78.392314s，均在120/240；本轮累计15项execution（14科学+1工程）wall285.28806236599576s/CPU264.43608s。VI B构造不扣账，累计974余0不变。

所有64根×两数值variant及16局部×两variant的source pair已完成，未遗漏固定投影。44个`uncompleted_source_pair_labels`恰好是22个被拒局部端点（native16+R2六）各自RBS/回溯两个条件未启动；它们是NOT_EXECUTED/前置拒绝，不能算RBS false、超时或运行中断。十个进入RBS的R2候选均完成回溯，无失败后补点或换条件。

## 最早下一门

本轮最早尚未获得正向局部证据的固定中心/角色是`II_0/active_chain1`，其次`II_1/active_chain0`；它们的±0.08候选有已定位的几何/界拒绝，不构成可盲修的算法bug。完整16/16正控门仍未通过，必须保留PARTIAL；若要新正向fixture覆盖这些中心/角色，需另写科学条件与预算、审查其采样依据，不能把本项h缩小或换seed重跑来抹掉失败。

普通PCS继续通往solve前的实现门，则是原`sample_q`的`collision && !limits`漏拒及随机三参数IKproject的成功后不break问题：应留source-native对照、提出版本化有效性实现并先资格随机采样/分划身份，尚不能直接启动三种planner正式统计。可并行复用本次薄接口推进IV/V或NR的已有模型资格；这不取消II覆盖缺口、其余环境或原论文完整实验。原作者代码问题、R2数值修复、外部门和论文理论仍分开。

审查输入SHA：execution `e0793f6ca95cec240b32a6be36d20b0e3df31cd307054fbe4d7cf97789990c6b`；events `1102c2149b18b188c9fa6e5335f47c1c6e90462816b0dbf97a9792ce1700197f`；冻结科学配置 `1b545278f37d60dc4a1b9279ad631b982311fed6723956f17a600a34927f2240`。保存数据审查脚本位于聊天work的`review_abb_pcs_local01_saved.py`，只使用标准库读取文本/JSON、计数/距离，不调用模型；本次审查新增科学调用为0。
