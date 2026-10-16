# P4 R2 ABB NR 固定 local 保存证据 POST（2026-10-15）

状态：`PASS_SAVED_EVIDENCE_POST`；检查 117258/117258 通过，失败 0。

本审查作者也编写了 local runner。这里的独立性指单独实现的 stdlib 保存证据解析与算术，不能声称人员独立；须由 root 和另一代理复核。审查不导入科学模块，不调用模型、FK/J、NR、IK、PQP、RNG、planner 或编译器，仅 Git 读取、文件重 hash 和保存数组算术。

冻结源提交 `7ee551afea8dc8ae49d4427e69f36f32bd771da5`；execution SHA256 `d9e548a26dcaa2488e6556e7e235f64fa83511ef517289d985e5b8b61eacc8a8`。协议/claim、1203 项绑定的前/后/当前 hash、冻结提交源 blob、已有未查询 build 的源码/mesh/binary 链均核对。4个A01 RECONSTRUCTED端点和首PCS原路径全部3条连续边逐项回溯；原作者原端点没有据此改记直接合格。

20/20 原响应、10 logical pairs 均保留；plain/trace 非计时结果与 binary64 q/path 精确一致，entered/completed 按 id/kind/LIFO 配对。全部 GD summary 与原 trace 逐项一致，PQP 原返回码全0。按环境与 q12 二进制字节重新构造全部 147 节点，全部 refs、collision-required OR 及节点顺序一致，无抽稀、无未检查尾部。

147/147 节点通过。仅由保存 poses 计算 `T2 - T1 @ grasp @ diag(-1,-1,1,1)`，最大位置残差 9.8878788321599131e-06 mm，最大旋转矩阵残差 2.5558390071012127e-08；物理门均为1e-5。原关节界保留 `degrees * 3.1416 / 180`，最小余量 0.087266666666666826 rad；没有wrap/lift/主动链或PCS分支门。

| 固定原边 | 原 reconstruct 节点数 | 最大全12角叶L2 (rad) | 门 |
| --- | ---: | ---: | --- |
| II_edge_0_reconstruct | 65 | 0.041259710686189298 | 首尾binary64精确、所有叶严格<0.05、所有节点合格 |
| II_edge_1_reconstruct | 65 | 0.043801152733444253 | 首尾binary64精确、所有叶严格<0.05、所有节点合格 |
| II_edge_2_reconstruct | 17 | 0.047693408589824418 | 首尾binary64精确、所有叶严格<0.05、所有节点合格 |

全部3条 RBS/reconstruct 各有真实GD递归，原始返回均 true。没有 RBStrue/reconstructfalse，soundness通过，环境II两个固定project通过，支持下一项环境II RRT_NR规划入口资格（仍须单独冻结与审批）。本次不计正式规划/统计，不证明NR全局能力、PCS相对优势或Table I结论。

原 trace计数：`{"nr_gd": 286, "pqp": 33150, "collision": 286, "nr_project": 4, "nr_valid_midpoint": 282, "nr_rbs": 285, "nr_reconstruct": 285}`。GD accepted-updates分布：`{"0": 4, "1": 60, "2": 208, "3": 14}`。数学逐臂294次、adapter FK/J 588次，独立碰撞147次；adapter PQP native/aligned 各 17026 / 17026，共 34052。源trace PQP是另一层计数 33150，plain内部标记UNOBSERVED，未按trace倍增。

native TCP最大位置差 0.0035317329275983411 mm、旋转差 7.1602714435126114e-06，保留失败证据；selected aligned最大位置差 2.2737367544323206e-13 mm、旋转差 3.3306690738754696e-16，所有pose门通过。逐variant原stdout、query_codes、provenance、node collision raw与worker副本全部交叉核对。

本次 wall 3.6995257820017287s / CPU 4.2455540000000003s，低于60/120；之前21项自有execution按fsum重算，总R2累计wall 385.76597718499488s / CPU 345.13823000000002s，低于3600/7200。5个进程完成退出0，所有process原始stdout/stderr hash及worker开始证据相符，无stopped partial、未完成请求、节点尾部或cleanup诊断。

保留原离散碰撞pair策略、8mm PQP容差、共线杆三角形限制；不声称连续碰撞、实体杆表面或省略pair安全。旧`math_arm_FK`标签实际经FK/J实现，不解释为Jacobian零次。211项完整覆盖清单和Table I 0/22500义务保留。

详细检查、每对响应计数及每节点算术见同名JSON。审查脚本SHA256 `ec97463c38bb3cfcc7a34520d64cb7a3d9a480e78508551573b65ed4fe96b24e`。
