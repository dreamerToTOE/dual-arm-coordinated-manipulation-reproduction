# ABB RRT_PCS 原完整路径独立资格 PRE-TASK

2026-10-15。状态：**PRE_DRAFT / RULES_INHERITED_FROM_PRE_SOLVE_FROZEN_PROTOCOL / NOT_EXECUTED**。

规则沿用首轮 solve 前冻结的 `r2_abb_rrt_pcs_e2e_qualification_v1.json` 中 `subsequent_independent_path_audit.gates`。本文件将其落实到独立后审；没有在看到成功路径后选择节点、端点、分支、阈值或预算。只审固定 E2E01 的实际输出，不能改用别的 solve/seed。实际节点队列在原 result 生成后逐字派生并随新协议冻结；描述阶段只读 JSON/字节，不运行 FK/IK/碰撞/规划。

科学目标：确认原 RRT_PCS 返回的 exact 起终点路径是否满足独立物理闭链、原机械限位、原被动分支身份、原 RBS 离散分辨率以及对齐原碰撞策略。有限单次路径资格不是正式统计、PCS优势、连续碰撞或完整实体杆件证书。

输入和溯源：固定 `results/p4_full/20261015_R2_ABB_RRT_PCS_E2E01/runtime/result.json`；核实相同执行的 execution/protocol/claim/build manifest/binary、工程执行及原 A01 II_0/II_1 端点哈希。request 精确为环境II、seed7、Range2.6、goalBias.05、solve10秒、原main舍入采样界（含q6±3.1416）。审查物理限位独立使用原 degrees×3.1416/180，不将采样界当机械界。要求 source returncode0、dispatched1、solve_calls1、exact true、approximate false、完整result及重构/identify日志一致。approx、截断或回溯失败保留为原证据，不改称合格路径。

完整队列派生规则：保持全部原 milestone 顺序，每相邻对按原记录调用顺序保留失败尝试、选原控制流第一次返回true的重构结果；原稠密Confs完整首尾必须精确等于该对。不得筛除失败节点、重新投影/平滑/补插值/换分支/最短角归一化。稠密节点仅按12个binary64坐标逐字节去重（包含signed zero），全部原边引用保留；源 PlannerData 还须包含这些 milestone 的原有向起终点路径。所有原始失败尝试和日志完整绑定。

固定验收门：每条叶相邻12角原坐标L2严格小于.05rad；每个distinct稠密节点（含全部milestone和起终点）独立闭链 position maxabs≤1e-5mm、rotation matrix maxabs≤1e-5、全部12角在原机械界内；每条所处原边的被动臂 branch_set 包含原requested branch，合并分支meeting set原样保留。所有节点查询v3 adapter，保存native和aligned两种原PQP响应，仅真实CHECKED、aligned collision=false可通过；原query codes须完整可解释且均0。无IK/NR/RBS/projection/solve/RNG新调用。

资源：一次120 wall/240 CPU，扣原R2总帽3600/7200与实时自有execution累计；无新VI构造。完整队列始终保存。最多处理2048distinct节点只是资源止点，不是必须凑满2048；若有尾部未检查，状态为STOP/UNKNOWN，绝不能将前缀或抽稀结果作为整条路径PASS。计数上界按min(N,2048)给出：数学臂FK≤2N、adapter调用≤N、adapter内部臂FK/J≤4N。逐臂started/completed记录，不把两个臂同时预记完成。

证据与恢复：独立原子固定claim、全新目录、禁止重复与覆盖；claim后预算初始化、imports、events打开与每步科学调用均进入try/finally。每臂返回立即保存；完整数学结果先保存，碰撞原始返回先保存，再解释status/codes；失败当前node partial及全未执行尾部保留。所有bound资产/protocol/claim运行前后核hash，收尾异常写入execution并阻断PASS。清理成本纳入真实wall/CPU，最终超帽也阻断PASS。read-only冻结/既存claim等admission拒绝在新claim之前，无科学消耗；OS强杀/磁盘完全不可写无法承诺最终文件，已存在claim/setup_started/逐步证据仍不重置。

复用：现有独立ABB FK/分支/原限位oracle为TEST_ORACLE，v3碰撞为已版本化原离散策略THIN_ADAPTER，现有RunBudget/独立claim与账本模式复用；没有新solver、采样器或通用预算系统。原运行数据、旧PRE和全部失败不改。源代码恢复为独立重建数值/端点，不能称原作者原生端点直接通过。

本阶段不要求未达helper或RSS资格，不进行新IV/VI实验，不进入P2/Isaac。完整211项、Table I 0/22500及其他原文实验义务保留。源码需提交、独立静态审查和实际source派生完整队列需冻结后，父任务才可执行。此脚本及PRE本身尚未执行科学计算或生成资格claim。
