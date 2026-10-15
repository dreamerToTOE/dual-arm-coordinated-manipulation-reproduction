# P4 崩溃恢复与 R2 接续阶段报告

2026-10-15。状态：**断点恢复完成，P4全文复现仍部分完成**。本次沿原工作树和工作分支推进，没有重新初始化或重做R0/R1。

## 真实断点

实际仓库 `/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full`，分支 `p4-full-reproduction-pcs-study`。接管时本地HEAD a39e963、远程356a3b1，本地5个未推送R2提交；另有57未提交文件8,482,891字节。先归档/manifest，再原字节提交0792acf。fetch确认未分叉，6工作树全部保留，无残留P4实验进程。没有pull/reset/clean或覆盖历史。

已完成的R1 1826检查=1580通过/246失败；R2先前空间2091项=2088通过/3失败，平面233/233和NR56/56；空间160NR为154合法闭合、6闭合后限位拒绝。旧原始12端点闭链全部失败。上述分母各自独立，不汇成虚假规划成功率。旧RSS19目标48分支只是700固定目标/5600IK中的数学资格，未具碰撞/RBS完整证据。

## 任务 A：原端点与精度恢复分列

原12端点FAIL全部保留，主动角不改，原结构分支不改。从已保存全解析根枚举全部合法真2π代表，共36组root、8423周期代表；后者不是独立实验数量。按被动角原坐标L2最小、branch/lift字典序精确tie选择。每代表独立闭链/限位，碰撞仅按周期等价共享原root查询。

A01：8 source-policy合格，IV/V四UNKNOWN；它们selected_q=null。独立审查定位我方TCP观测插桩错误：IV读取作者未赋值且不用于碰撞的T7，V把20mm mesh参考点当作22mm TCP，产生2mm差。v3只替观测表达式，所有原query参数、mesh、pair list和8mm容差不改。IV82/V87活动语句逐项一致，去观测行后v2/v3源码相同。

A02仅回放4个已保存最近同支候选：IV_start22/goal44，V_start52/goal22。4/4实际PQP source-policy合格，TCP最大差6.821e-13mm；新IK/NR/采样/规划0，wall1.321430518s/CPU1.324637s。最新重建12/12合格，A01四UNKNOWN及原12FAIL不覆写。A两run合计wall8.771571746s/CPU7.350284s。

“source-policy合格”只覆盖原作者离散碰撞策略：遗漏pair、完整实体几何和CCD仍未证；ABB原共线rod三角形不能称实体杆证书。原网格/源码仅在外部hash引用，未搬入公开仓库。

## 任务 B：VI独立三臂RSS

Q0原关系与physical/body Jacobian独立交叉通过。Q1固定主动臂1、指定被动臂2/3、原Comau几何/基座/Q/S/界，wrist mode1(q5=0)，gamma=.2；条件请求资格无规划gamma事件。seed7/23/41/101/20261013各6请求，每最多32构造，不碰撞后换根。

30请求、868构造、13888IK；7请求成功、23请求达32上限失败。12候选数学合格进入碰撞：7 clear、5碰撞拒绝；指定臂2得到2、臂3得到5。候选覆盖门通过不等于RBS或RSS规划成功。wall45.133593772s/CPU5.641175s，原claim防重复。

Q2固定各指定臂首次成功219/643，不换样本；保留原q4/q6奇异族。8个±.01/±.005rad指定q5曲线点与28个active1线性中点/被动2、3解析投影，共36构造、576IK、36native F、36碰撞均节点合格。四半段在depth3的32叶全未达到严格全18原坐标距离h=.0025，因此仍UNKNOWN。wall7.987086492s/CPU6.310368s。

原VI source本身不构成可编译三臂RBS：存在q3/dsg2/递归参数缺项；文本tol=.05、奇异shortcut=7*.05=.35rad，单独归约。阈值提前返回不是独立严格桥资格。新节点全部合格不能掩盖尚未证实的奇异接入连续性；保存数据根因与后续最小诊断另列。

B目前共904/960构造，wall53.120680264/180s，CPU11.951543/360s；剩56构造/126.879319736wall/348.048457CPU，不可重置。此为exact-center数学诊断前账目快照。

## 环境 IV：旧失败根因与新增局部资格

旧6次均2–3步先闭合，因q3低于原界而正确拒绝；4输入原已越界，2输入合法但无约束NR走向界外根。原start距下界仅.0008rad，±.01组“应全部合法收敛”是我方额外完整性假设，非论文保证。保存合法start_0是附近合法解存在性见证；不据此改判旧3FAIL，也不私加限位NR策略。

新独立组绑定A02两个同支重建中心，h_start=9.999999999996123e-5、h_goal=1e-4rad，每中心arm1六轴各±h，共24输入。原full12不阻尼伪逆/periodic_chart/残差/界不改，branch只诊断；余量/8只保证输入合法，不保证NR输出。

实际24/24 CONVERGED且独立原生FK、限位和源碰撞合格，52F、24adapter；14例1步、10例2步。原生闭链最大9.519668993e-6mm、旋转矩阵1.422114565e-9，均原门内。所有24例主动角都被NR改变，最大8.9435582891e-5rad，不能称固定主动角投影。输出最小界余.000735893469rad。wall2.651571520s/CPU.882651s，26绑定hash不变。旧6拒绝/3FAIL仍留存，未重跑旧组。

## 全文义务与下一门

完整211入口、30父义务保留；新对照表逐字段保留R1的30事实列与旧R2的5快照列，新增当前列而非覆盖历史。RSS_I/IV不再误套II/III/V数学结果。正式TableI仍0/22500，45单元各500次和1000s上限不缩减；500000配对投影、50000合法点对、Fig3–5/TableI–II、全部fixed划分、去障碍、窄通道/复杂障碍及PCS优势验证保持。

R2当前9科学run累计wall80.902103069s/CPU30.799802s（各execution自身字段相加，不加cumulative，工程构建另账）。原总帽3600/7200s仍在。所有正式大规模计算待资格后pilot实测成本再申请，不能用本次有限检查替代原统计。P2/Isaac/FR3扩展未开展。

## 复核、提交与尚未完成

恢复前1028个科学文件、57个崩溃前未提交文件、其余5工作树HEAD和13未提交文件已逐哈希核对不变；最终交付前再复核。A/B/IV新数据分别经独立只读归约，源码/协议先冻结提交后执行。

已推送b686e7b包含原R2本地进度、保全、A/B资格和Q2全日志。NR实际结果、最新对照表/预算/根因报告继续提交，最终commit随后登记。完整中文Word/PDF结题报告尚未生成：P4未完成，不把旧草稿或阶段记录冒充结题。

下一步先完成VI严格桥的根因复核与最小数学诊断，再按逐gate接续清单处理六环境全部RSS/PCS/NR与三planner，冻结小规模成本pilot。任何新local planner处理须标独立重建及原法差异；不以盲加深、缩δ、换fixture或source提前返回取得成功。

## 执行命令与源码版本索引

以下均在原p4-full工作树执行，所有参数先冻结；无同run重启。

|run|source commit|命令|
|---|---|---|
|A01|8188e93|`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/recover_p4_full_r2_endpoints.py --run-id 20261015_R2_ENDPOINT_RECONSTRUCTED01 --protocol configs/p4_full/r2_endpoint_reconstruction_execution_v1.json`|
|B-Q1|3fad1b5|`python3 scripts/qualify_p4_full_r2_vi_rss_reconstructed.py --protocol configs/p4_full/r2_vi_rss_reconstructed_qualification_v1.json`|
|A02|0465ad8|`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/replay_p4_full_r2_endpoint_collision.py --protocol configs/p4_full/r2_endpoint_collision_replay_v1.json`|
|B-Q2|2f465d6|`python3 scripts/qualify_p4_full_r2_vi_rss_bridge.py --protocol configs/p4_full/r2_vi_rss_bridge_qualification_v1.json`|
|IV-NR|b686e7b|`python3 scripts/qualify_p4_full_r2_iv_nr_local.py --protocol configs/p4_full/r2_iv_nr_local_qualification_v1.json`|

source完整SHA、源码与配置/依赖/输入SHA、stdout/stderr及事件前缀均在各run。原controls及A01相关工具见5fb7a6a/17da8c3/8188e93；崩溃前未提交原字节归档0792acf。源码、失败、候选与参数版本均可从提交回溯，未重写旧历史。
