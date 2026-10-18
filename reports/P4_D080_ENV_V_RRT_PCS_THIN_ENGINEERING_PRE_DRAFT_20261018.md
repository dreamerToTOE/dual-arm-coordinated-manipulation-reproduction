# V RRT+PCS 最薄工程接缝草案

**状态：不可执行DRAFT。** 本项只新增driver、纯字节观察变换和工程字段plan；未运行变换、编译、二进制、模型或科学，未设seed/solve时限/caps/费用/prior，未提交冻结。PHYSICAL01 PRE、源码、原失败和已有合格结果未改。

PRE-TASK：任务为准备V单次原RRT入口；科学目标为后续取得从原A02 start到goal的真实完整路径并独立核验。最小充分证据必须有exact非approx、原完整回溯及独立物理/branch/限位/叶距，工程链接不能代替。当前范围为只读资产复用与I/O薄适配；不做随机helper/CBiRRT修复、不动RRT/几何/阈值、不生成新点。预算尚未冻结，当前科学尝试0；出现在输出/构建/模型/最新账本不匹配时保留证据停止，不隐含扩大原R2预算。无需额外用户决定即可继续已授权普通工程准备；执行前仍须root冻结及独审。

PRIOR-ASSET：II已合格e2e driver及观察header、V LOCAL01 plain/trace及BUILD02_TAIL为来源。II数学、采样盒和range2.6不移用。DIRECT_PORT为II独占输出/17位JSON写入/PlannerData/失败回溯保存ABI和V原已审observer；THIN_ADAPTER为V一次性driver、SVC两处post-return观察；TEST_ORACLE仅保存PHYSICAL01与旧A02记录；REFERENCE_ONLY为II路径数学证书。无需重写builder/supervisor/group-CPU/依赖/Decimal费用框架，最终builder可薄适配已有V/III工程层。科学核心仍为已资格修正Comau APC、aligned-v3碰撞以及原V PCS/RRT控制，标CORRECTED/RECONSTRUCTED，不冒称作者原输入原数值直接通过。

| 文件 | 接缝 |
|---|---|
| `baselines/p4_full/geometry_consistent/comau_v_rrt_pcs_e2e_driver_v1_draft.cpp` | 复用II一次entry和完整输出；V采样盒、range.2、callback/resolution/goalBias原样；未来冻结request才提供seed/时限/caps，当前未授权 |
| `baselines/p4_full/geometry_consistent/comau_v_rrt_pcs_e2e_instrumentation_v1_draft.py` | 输入已审V local SVC `bdbe…0509`；状态级reconstruct完整原体仅一次；现有vector identify只加输入副本和post-return观察表达式，不再套第二科学lambda；整个文件可逐字逆恢复 |
| `configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json` | 固定对象/原命令/源与.d身份、2新TU+1link的完整命令草案；budget/prior/seed/时限/caps全null，执行flags全false |
| 既有 `abb_rrt_pcs_e2e_observation.hpp` | 原字节复用；record schema中的ABB仅历史ABI名称，V结果显式注明。完整环境/数值分类始终V |

三个直接复用对象是 `v_pcs_local_v1/trace/1_apc_class.o`、`v_pcs_local_build02/trace/3_collisionDetection.o`、`v_pcs_local_build02/trace/4_RRT_PCS.o`。只新编driver和加I/O观察后的SVC，两者uniform `P4V_TRACE_MODE=1`。所有新TU compiler-preinclude现有**同一路径**V observer，driver不再另外include仓库同内容副本，避免不同文件pragma-once与ODR问题；保留原编译器/flags，并补RRT header include路径及II header preinclude。现有三个对象的所有.d依赖及原源文件/headers/库须与已审保存池联合绑定，不能仅核对象hash即声称依赖完整。使用同字节对象不构成重新执行旧资格。

V `RRT_PCS.cpp/.h`完整字节不改，原成功`temp.txt`删除仍按原作者执行；成功`path.txt`保存同一原低精度序列，失败提前return自然保留temp。17位reconstruction与identify JSON同时保存全部成功/false/partial。旧II的retain-temp源码替换不引入V。三参随机helper缺break/五参role1索引问题不修入此版本，具体不可达图见 `P4_D080_ENV_V_RRT_PCS_CALL_GRAPH_AND_THIN_E2E_ROUTE_DRAFT_20261018.md`。

后续root先做纯字节变换/逆恢复增量审查，再基于最新实际账冻结工程预算及复用监管；本草案尚无新builder执行入口。构建通过后另冻科学protocol，明确完整A02端点逐binary64输入、所有真实内部调用帽、一个seed/一个原入口、原墙钟截止与外层余量、全路径后审队列/预算，失败后不换点/seed/range。此单trace模式不能宣称完整solve plain/trace一致，既有LOCAL01语义一致可直接复用。原局部三条碰撞拒绝、project-only被拒点和最早IK UNKNOWN不改判；完整端到端资格仍未通过。

driver的state级post-return hook未返回时true_started不可观测，明确保留该边界；原V trace-1 source生命周期日志会记录entered/completed/aborted前缀，科学运行器必须归档raw stderr并全组回收，不因未来源异常丢掉前缀。source exact后仍须核每个原解边的成功完整回溯、所有保存节点的闭链/真实branch/全12原限位、显式v3 aggregate/TCP及叶距`.05`；source87逐pair自一致与独立aggregate证据分列，未暴露的独立逐pair closer保持UNKNOWN。

此阶段正式统计0/18,000、VI后续0，不涉及P2、Isaac、FR3或结题。
