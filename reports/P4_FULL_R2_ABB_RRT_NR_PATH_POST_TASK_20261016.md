# 环境 II 原 RRT_NR 首条完整离散起终点路径 POST

2026-10-16。本阶段已完成单次原 RRT_NR 入口运行及完整保存路径的独立资格，全文仍部分完成。环境 II 使用 A01 `RECONSTRUCTED` 起终点、已独立合格的 physical full NR C++ 接缝；不是作者原始端点或 KDL 数值轨迹直接通过。

工程来源 `1f99868`，`20261015_R2_ABB_RRT_NR_E2E_BUILD01` 单目标构建成功且不查询，实际 28.08202379599993 秒墙钟 / 34.574132999999996 秒 CPU。完整源码、编译输出和 manifest 保留。原 RRT 源的唯一临时文件保留 I/O 差异可逆后整文件字节等于作者源；GD 数值接缝及完整回溯观测差异单独登记。

入口来源 `91901bb`，唯一命令 `python3 scripts/qualify_p4_full_r2_abb_rrt_nr_e2e_draft.py --protocol configs/p4_full/r2_abb_rrt_nr_e2e_qualification_v1.json`。原 sampler box、q6 ±3.1416、恒 true callback、resolution .1、Range 2.6、goalBias .05，OMPL seed 7 与 srand 7；只调用一次 solve，10 秒限、外帽 30 秒墙钟 / 60 秒 CPU。实际 exact=true、approximate=false，7 个里程点、55 树节点 / 54 树边；6 次原 state-level 完整回溯均返回 true，保存节点数 65/65/129/65/65/9。solve 段 .675570016 秒；整个 execution 自身 1.7845762399997511 秒墙钟 / 1.7793930000000007 秒 CPU。原 execution 的 `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT` 历史状态保持。

完整路径资格来源 `7df21bd`，唯一命令 `python3 scripts/qualify_p4_full_r2_abb_rrt_nr_path_draft.py --protocol configs/p4_full/r2_abb_rrt_nr_path_qualification_v1.json`。`20261015_R2_ABB_RRT_NR_PATH01` 单独结果为 `PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH`：393/393 唯一节点、392 叶及全部尾部经独立数学闭链、原机械界与 v3 aligned 原离散碰撞策略合格。未重投影、修路径、增加 solve 或附加 PCS 固定主动链/解析分支门。

最大位置闭链误差 9.793997321594361e-6 mm，最大旋转矩阵误差 3.0701365727470176e-8，原门均 1e-5；最大 full12 L2 叶距 .0478001489336342 rad < .05，原界最小余量 .046633132713711944 rad。实际数学逐臂 FK/J 786、adapter 内部 FK/J 1572、collision 393、PQP 91176（native/aligned 各45588）。native TCP 不一致的393个记录保留；aligned 资格另列，不改判原失败。实际 3.7730926529998214 秒墙钟 / 3.9572699999999985 秒 CPU，在120/240帽内。

保存证据后审分两层：runner 作者的独立 stdlib 算术 36348/36348 通过（人员独立=false），另一代理人员独立 saved-only 审查 24448/24448 通过，覆盖6条原回溯 binary64、树路径、393节点/392叶、保存 TCP 矩阵闭链、原界、双碰撞原始响应、5502实际事件、1352资产 SHA 和完整尾部。两层均 0 新模型查询/编译；不重复科学运行。见 `P4_FULL_R2_ABB_NR_PATH_INDEPENDENT_POST_20261016.json/.md` 和 `P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json/.md`。

V8 共25 execution=20科学+5工程，逐自身成本一次合计419.4056698739944秒墙钟 /385.449026秒CPU，保守计入R2的3600/7200帽；余额3180.5943301260056/6814.550974秒。VI 974/974、构造余额0；正式 Table I 0/22500。本次资格仅离散 source policy，保留8mm容差、原pair和共线杆三角形限制，不证明CCD、完整实体杆表面/省略pair安全、速度/成功率、PCS优势或完整P4。

全部211项原义务与原统计规模保持，最新 V8 对照表逐值保留前98列211行，新增8列本路径证据。下一项随机三参 helper H 修复与本路径分开冻结/资格；其不在已验证 RRT grow 调用链。CBiRRT 距离修复、其余环境/搜索器、RSS 原RBS/分布/入口仍待，正式成本 pilot 在相关端到端资格后安排并报告预算。不 P2/Isaac，不提前结题 Word/PDF。
