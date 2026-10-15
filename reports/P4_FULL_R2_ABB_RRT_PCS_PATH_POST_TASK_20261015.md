# P4 R2：首条独立合格的原RRT_PCS空间路径

2026-10-15。阶段**初步验收通过**，P4全文仍**部分完成**。用户要求的ABB局部资格已实际执行，本阶段取得环境II第一条经过独立检查的起终点路径；NR及其他原生规划器仍在资格阶段。

## 实际结果与科学边界

原作者RRT_PCS搜索、固定分支投影、RBS与回溯，在已版本化R2数值和A01恢复端点上返回exact非approx解。原main采样盒（含q6±3.1416）、恒true callback、原环境II range2.6和goalBias.05保持，seed7，原solve时限10秒。起终点逐值保留A01，没有换seed、修改障碍或规划后修路径。

|项目|实际证据|
|---|---|
|原solve|1次，exact=true，approximate=false，goal difference0|
|搜索树|6节点、5有向边；4个解里程点|
|原成功回溯|3段，各80/65/34节点，全部含非平凡中点|
|连接角色/分支|(主动臂1,branch3)→(主动臂2,branch3)→(主动臂1,branch0)|
|独立整路径|177唯一原节点、176叶；全部通过|
|最大位置闭链残差|3.410605131648481e-13 mm（门1e-5）|
|最大旋转矩阵残差|4.440892098500626e-16（门1e-5）|
|分段最大全12维叶L2|.04949053472601928/.0461793500400/.0480562990557 rad，均严格<.05|
|原机械界/被动branch|全部通过；两切换点两侧角色各自独立检查|
|v3原碰撞策略|177/177 aligned clear，native响应同时保留；41064 PQP查询码全0|

这是明确的RECONSTRUCTED端点与R2数值修正下的原搜索器资格。作者原始12端点失败和原native数值失败原样保留。它不是作者原输入直接通过的证据、PCS统计优势、连续无碰撞、完整实体杆或省略碰撞对的证书。正式Table I仍0/22500；单次资格不混入原500重复。

## 来源、命令与成本

|阶段|冻结源码|命令|实际wall/CPU秒|
|---|---|---|---|
|新单目标构建|85acfd5|`python3 scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py --protocol configs/p4_full/r2_abb_rrt_pcs_e2e_engineering_v1.json`|17.12737691100483 / 23.727903|
|单次原RRT入口|1a5b811|`python3 scripts/qualify_p4_full_r2_abb_rrt_pcs_e2e.py --protocol configs/p4_full/r2_abb_rrt_pcs_e2e_qualification_v1.json`|.2776374349996331 / .19540999999999997|
|全部路径独立资格|b4cbbff|`python3 scripts/qualify_p4_full_r2_abb_rrt_path.py --protocol configs/p4_full/r2_abb_rrt_path_qualification_v1.json`|40.94035644100222 / 1.1020530000000002|

原solve含原回溯耗时.016837364s；原perf_log CPU .012在回溯前停止，不能混作本机公平性能。工程、输出I/O与逐节点fsync独立审查均另列，仍保守扣原R2总帽。PATH01实际354数学FK、354分支身份、177adapter调用、708adapter内部FK/J，未运行新IK/NR/投影/RBS/solve。原源内部未插桩FK/IK/PQP true_started为UNOBSERVED，completed hook不反推未返回调用数。

工程66旧资产、science129依赖、path215绑定文件及每段source/claim/protocol/二进制链在执行前后核对。原stdout/stderr、低精度path/temp、17位往返精度JSONL、所有成功/失败回溯观察及PlannerData保存。原source execution保留SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT，由后续独立execution单独给出PASS，不覆盖原时间点结论。

独立审查见`P4_FULL_R2_ABB_RRT_PCS_E2E_POST_REVIEW_20261015.md/.json`及`P4_FULL_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW_20261015.md/.json`。完整保存记录独立POST2337/2337项通过，最小机械限位余量.035336181584417536rad，native/aligned各20532查询。source另有638个PQP BeginModel警告：原collision_state每次重建rod，同一模型首个调用后重复BeginModel，作者忽略其返回码；原警告全部保留。未修改原碰撞实现或重跑本次solve，独立v3响应/TCP/查询错误码另验。

## 账本、保全和下一步

V5总账18execution=16science+2engineering，累计wall343.63343315300244/CPU289.461446，原R2剩3256.3665668469976/6910.538554。VI B974/974、候选余额0，未追加。V5保全复核全部通过，1028旧科学文件、崩溃前57文件/8482891bytes、tar57成员及其他5工作树13未提交文件不变。

最新211项表为`P4_FULL_R2_ABB_RRT_PCS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md`，逐值保留前73历史列，增加8列本阶段事实；原45×500、1000s/call、500000配对投影、约50000点对、Fig3–5/TableI–II及所有消融义务不变。

下一步是普通NR的已合格Python物理全Jacobian/SVD内核逐式移植到C++，先同64保存输入的plain/trace及Python详细参考核验，再接原NR搜索/RBS。CBiRRT activeDistance原角色1重复retrieve导致同点非零另行留证版本化修复；未达sample_q/随机IKproject缺陷不再误列为RRT前置。RSS分布、原RBS和入口解耦诊断，不追加VI构造。全部端到端资格通过后才安排独立成本pilot和正式预算申请，不提前P2/Isaac或结题Word/PDF。
