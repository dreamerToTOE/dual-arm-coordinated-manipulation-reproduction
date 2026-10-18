# D080 环境 III PCS/NR：最小只读续研入口核对

2026-10-18；仅只读既有源码、JSON、manifest及40份网格字节。本报告没有新编译、二进制/describe执行、FK/J、IK、NR、碰撞、RBS、RNG或solve，也没有新增科学预算、冻结协议或修改旧证据。范围遵循D080 I–V；VI未进一步分析。该报告是下一门定位，不能作为III路径证书。

**III PCS已具备有限局部证据，最早缺门是III专用规划工程/冻结入口；III NR已有端点投影，尚缺本环境非平凡RBS/回溯资格。** 两个II e2e可执行文件均硬编码II，不能改输入标识后直接用于III；II路径证书不迁为III资格。

|项目|可复用旧证据|尚缺内容|
|---|---|---|
|III A01起终点|`20261015_R2_ENDPOINT_RECONSTRUCTED01/III_0.json`及`III_1.json`，均RECONSTRUCTED_SOURCE_POLICY_QUALIFIED；selected index1/3、被动arm2 branch1/3，source regular、独立branch、闭链、原界与选定碰撞策略合格|不是作者原舍入端点直接通过，不证明路径/CCD|
|III固定PCS局部|`20261015_R2_ABB_PCS_LOCAL01/execution.json`内本环境8条R2边，7条原RBS+回溯非平凡成功且节点独立检查；`III_1_a0_s-1`原workspace拒绝保留。III起终的两主动角色均有正控；plain/trace旧比较复用|全局规划、整路径及统计尚无III证书；不补跑第8条制造8/8|
|III固定NR局部|`20261015_R2_ABB_NR_LOCAL01/execution.json`的`endpoint_project_gate_by_environment.III=true`；同数值core支持III1200/500|该次3条非平凡边全部来自II旧PCS路径，`next_planner_environment`也是II。III非平凡NR RBS/回溯尚未实际通过|
|III障碍工程资产|两个e2e stage均有完整20份mesh且当前SHA逐份等于各自旧manifest；包括相同`cone.tris`|旧binary不能选择III；仅mesh完整不构成III碰撞或规划通过|

作者CKCplanning @909bd72中的**内部env2对应论文III**：`StateValidityCheckerPCS.h`与`StateValidityCheckerNR.h`均选择基座间距1200mm、杆长500mm，臂1基座−600、臂2+600并转`PI_`。原`run/plan_PCS.cpp:237–252`及`run/plan_NR.cpp:233–248`给出RRT步长向量`{2.6,0.8}`，因此III RRT必须0.8；CBiRRT为1.0，SBL为0.6。不能将II range2.6平移过去。原采样盒仍需按该main逐字绑定，不把机械界和采样盒混淆。

`collisionDetection.cpp:425–476`的env2保留两TCP高度超过800mm即拒绝、下锥位姿`(0,0,0)`、上锥位姿`(0,0,790)`及原`MRotX(3.14)`；`load_models:921`两障碍均读`cone.tris`。原pair/8mm/杆几何、native数值失败和aligned策略身份继续分列。旧RSS22根/16clear证据不作为PCS/NR路径资格。

两个II e2e driver的薄适配点为：请求门、结果environment、range0.8及`og::RRT(si,0.8,2)`；NR还必须将`p4nr_iface::environment`同步为III。`abb_nr_interface_kernel_draft.cpp`本身已接受III1200/500，同一物理全NR内核可按SHA复用；不能将它称原KDL轨迹。原observer、搜索/RBS主体、数值修复、mesh与独立oracle应按已审SHA复用，避免无关改动。

**仍需工程编译。** 两个旧e2e stage均无`.o`，旧builder为单条编译/链接命令，不能声称有可供“仅driver重链”的旧目标文件。可薄适配新driver后在fresh stage建立一次按TU保留objects的工程方案；旧源码与数学/接口证据不因重编再运行。实际构建须由root冻结精确依赖和当前费用，不能直接运行过时prior/22500-current-scope的旧builder。

建议接续顺序（均尚未冻结/执行）：III PCS薄工程→按原III条件一次有限入口→若exact且完整重建，整路径独立闭链/branch/限位/aligned碰撞/叶距审查；III NR先冻结少量**已有III保存局部边**的原project/RBS/回溯plain/trace门，再薄工程和有限入口。具体输入、seed、时限及分项预算由root冻结；不换失败输入或扩大预算。这是D080普通资格工作，正式18,000次仍0，真实成本pilot和批准前不启动。

## 精确证据指纹

以下相对路径均以仓库为根；外部stage及manifest按绝对路径保存。此处只保留必要指纹，不重建211行大清单。

|证据|SHA256|
|---|---|
|`results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/III_0.json`|`85550cbc3ffbf80c80519b5e592e85401dcf1e96ce747f0df5f3d97c97065c6a`|
|`results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/III_1.json`|`50db8b75e8c29c9dfc42646e5165c22f31dd8e2853858686572405c3cd91cc12`|
|`results/p4_full/20261015_R2_ABB_PCS_LOCAL01/execution.json`|`e0793f6ca95cec240b32a6be36d20b0e3df31cd307054fbe4d7cf97789990c6b`|
|`results/p4_full/20261015_R2_ABB_NR_LOCAL01/execution.json`|`d9e548a26dcaa2488e6556e7e235f64fa83511ef517289d985e5b8b61eacc8a8`|
|`reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_ADDENDUM_20261015.md`（未达helper非前置阻断）|`1a825dee5f72e8d857f444e46ca386e649f6d51dce47e25a07e6a1fdf22de9fb`|
|`reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_INDEPENDENT_POST_20261015.md`|`499a805ba6e00e28e2e740da7f939971898dd7300cb6b178bbe6f08b5400c5cf`|
|`baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_driver.cpp`|`eeb5e4bce07ef6e7f466086374b6b304258684c110dc7cb9b8048fdeb16c2478`|
|`baselines/p4_full/geometry_consistent/abb_rrt_nr_e2e_driver_draft.cpp`|`4a8749f2df2b820892f8cb0c2fcf335257db22e937323ac8f7eee0a9468e6aeb`|
|`baselines/p4_full/geometry_consistent/abb_nr_interface_kernel_draft.cpp`|`2d5d61ac8742330611c39243c740df5a6e5e15fbe13a72ad6ea50973917c930b`|
|外部`CKCplanning/run/plan_PCS.cpp`|`af868b6ed9bb1253fc2283f6d4d2fe8f3437a91ab349414bc44521892c4b3f69`|
|外部`CKCplanning/run/plan_NR.cpp`|`b322c444ba296b2e1f19173cef61cc67c98bd8a3525f6d3d6f375f7ea7217409`|
|外部两stage与作者`collisionDetection.cpp`相同|`9d8e59304a2af3a22ade7aa8dcc5481157f94af981bb95c9b54dbe0ed8eef0c3`|
|外部两stage `simulator/cone.tris`相同|`d22e702fbe3fd649678e9d0d85dd165c2a8cdf9aaf3047da526e5a84a096821d`|
|`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_pcs_e2e_v1/manifest.json`|`e1d665a5ff6c99a3654cf9433e8c2465b50e4d22dea5f91a226b42974e5adc0c`|
|`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_nr_e2e_v1/manifest.json`|`0c7138250e081c5ce6b47fc69d5e703230ff8c6aee8f2ad1d8c6237c9c586a8a`|

外部stage分别为`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_pcs_e2e_v1/geometry_consistent_observed`和`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_nr_e2e_v1/physical_nr_observed`。无新科学执行，不追加实验费用账，不修改旧SOURCE_EXACT、原失败、UNKNOWN或独立PATH结论。
