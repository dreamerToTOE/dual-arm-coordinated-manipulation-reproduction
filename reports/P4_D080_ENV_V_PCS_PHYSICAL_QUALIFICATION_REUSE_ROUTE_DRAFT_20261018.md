# D080 环境 V PCS：局部执行后的独立物理资格最薄复用路线（只读草案）

2026-10-18；编写者 `/root/sbl_path_resume`。状态 `DRAFT_NOT_FROZEN_NOT_EXECUTABLE`（未冻结、不可执行）。本页只读现有源码、manifest和保存JSON，未导入项目模型、未调用FK/J/IK/NR/PQP/RBS、未编译、未启动二进制、未扣新资格预算。编写时 `20261018_R2_D080_V_PCS_LOCAL01/execution.json` 尚不存在；不能预填新局部结果。最终执行/费用/账本/提交均由root唯一负责。

```text
=== PRE-TASK REPORT ===
Task: 确认V局部后审最薄复用路线及未通过门。
Scientific objective: 用独立Comau数学核和原V离散source-policy验证新保存局部结果。
Minimum sufficient evidence: 完整原成功/失败流、完整节点与叶段、闭链/branch/原限位/native+aligned碰撞证据。
Current scope: 只读设计；V；固定A02/±.05夹具；节点上限256不扩。
Explicit non-goals: 模型执行、编译、科学冻结、预算增加、solve、VI、正式18k、P2/Isaac/FR3。
Attempt budget for the current blocker: 0次科学调用；不申请/消耗新科学预算。
Preferred method: 复用已有独立serial FK、关节几何branch和v3碰撞adapter；仅增加V数据接缝。
Fallback method: 缺字段/超帽/来源漂移时留证UNKNOWN，不重新生成节点。
Stop / escalation condition: 无完整成功路径/叶、未完成独审、资源或来源门不满足。
Files expected to change: 本只读路线报告。
Validation plan: 源码/保存JSON逐项核对；无科学验证。
Known ambiguities / risks: 离散source-policy、箱体CAD/吸盘接触、连续安全是不同层级。
Need user confirmation: no，本页无执行或新科学设计。
```

## 1. 直接复用的数学核及不可借用的证书

| 需要的门 | 最薄现有实现 | 必须保留的V语义 |
|---|---|---|
| 世界FK/闭链 | `scripts/recover_p4_full_r2_endpoints.py::{arm_fk,grasps_for,matrix_error}` → `analyze_comau_native_qualification::{serial_fk,geometry}` | 显式`environment='V'`/model5；每臂6角、单位rad/mm；与作者核独立的基本齐次变换连乘 |
| 原关节限位 | 同脚本`bounds_for/limit_score` | 每臂deg为[-180,180],[-60,125],[-90,75],[-2700,2700],[-120,120],[-400,400]，用原`AUTHOR_PI=3.1416`转rad；不做principal-chart重映射 |
| 真实分支 | 同脚本`branch_identity` | signed shoulder radius、`-sin(q3+atan2(1436.5,210))`、`sin(q5)`；原相对零门`64*sys.float_info.epsilon`；零因子保留合并branch集合，不声称唯一 |
| 碰撞TCP一致性 | `collision_adapter._evaluate_pose` → `physical_nr.arm_fk_jac` | Comau分支最终仍用同一个独立`serial_fk`及其stages；它不是第二个相互独立的FK oracle，不重复计成双重数学支持 |
| 有序叶段 | 纯保存数组的big-endian binary64 key、full12 L2范式 | 可借SBL materializer的纯数据模式；不能复用SBL/ABB的几何、路径证书或motion身份解析器 |

V几何固定为 properties `[344,524.5,199,1250,186.5,210,1250,116.5,422.7]` mm；`d=2358.3-20.055`；bases `[[-d/2,0,1000,0],[d/2,4200,100,-3.1416/2]]`。抓持Q必须为精确矩阵 `[[0,0,-1,250],[0,1,0,0],[1,0,0,750],[0,0,0,1]]`，不能改成近似π的三角函数矩阵；闭链为 `T2 = T1 @ Q @ diag(-1,-1,1,1)`。原位置最大绝对误差≤`1e-5` mm、旋转矩阵最大绝对误差≤`1e-5`。原向量顺序与角色：role0臂1主动/臂2被动，role1反之；每个node对所有关联角色分别核requested branch是否属于实际被动臂branch_set。

## 2. A02旧证书的精确复用边界

原两个中心字节及结果可只读复用，不再端点恢复、不选其他候选：

| 保存文件 | SHA256 | 已保存结论 |
|---|---|---|
| `results/p4_full/20261015_R2_ENDPOINT_COLLISION_REPLAY01/V_start.json` | `f906a6b61999c71efe15c8d86188edbded704d66dcba18f9833d940ccfa6c405` | RECONSTRUCTED；被动branch3；闭链位置4.547473508864641e-13mm、旋转1.1102230246251565e-16；原限位合法；aligned clear |
| `results/p4_full/20261015_R2_ENDPOINT_COLLISION_REPLAY01/V_goal.json` | `feae5fd78837327db9c83d66621e2aa4fc9eec72a46c0d0dfc1e98cbc9d88737` | RECONSTRUCTED；被动branch1；闭链位置6.821210263296962e-13mm、旋转3.3306690738754696e-16；原限位合法；aligned clear |

两个旧中心native的碰撞聚合虽为0，但臂2 TCP偏移最大约`0.015427453546863035`mm超过原门，保持 `COLLISION_PHYSICAL_TCP_MISMATCH`。aligned独立TCP通过，仍只证明原离散pair策略。旧 `UNKNOWN_COLLISION_QUALIFICATION`、作者原端点不合格、所有候选/改变量与旧失败不改判。

新±.05投影、内部RBS中点、回溯路径是新状态，不能继承中心的clear资格。若新队列确实包含完全相同binary64中心且来源/判据/模型/碰撞字节相同，可引用旧逐点记录；签名不同或只近似相等时不可复用。原中心branch只描述原被动臂，不能替代新的双角色identify/branch资格。

## 3. 完整保存队列与最小字段

local runner的`independent_nodes_PENDING.json`仅排队成功`project_fixed/is_valid_rbs`输出，是待验索引，不是完整物理证书。后续先做stdlib-only materialization：

1. 保留trace/plain原38行及所有成功、false、依赖未执行、aborted记录；核原公共请求顺序、resolved role/branch和两binary语义一致性。
2. 以完整q12的12个big-endian binary64字节为key（保留signed zero），取所有成功投影/成功isValid、全部回溯`path_q12`及true RBS每叶两端点的union。false回溯的部分路径也保存，标清其不是成功路径；不得删失败尾。
3. 对每个q保留多来源列表：`{mode,public_request_id,source_record_id,kind,input_q12,output_q12,active_chain,requested_branch,returned,parent_trace_id}`。物理查询可按字节去重；原顺序、不同调用身份、角色关联不合并丢弃。
4. 完整union必须≤256；超帽时保全完整队列并停，不截前256、不重生成更短路径、不补节点。
5. 每个连接保存`{request_id,returned,role,branch,qa_key,qb_key,ordered_node_keys,source_RBS_records,source_reconstruct_records,leaf_pairs,leaf_full12_L2_rad}`；每个node保存`{q12,poses,closure,limits,branches,all_role_assignments,native_collision,aligned_collision,qualified,stage,raw_evidence_refs}`。

原trace进入/返回流允许恢复递归parent及左右次序；stdout完成记录不自行提供parent，不能通过ID近邻猜树。true RBS的每个叶必须从原递归参数得到，计算 `sqrt(sum_i((qa[i]-qb[i])**2)) < .05`（严格、全12维、未做wrap）；每个true回溯必须首尾与原投影端点binary64一致、完整顺序叶全部<.05。不能仅检查相邻抽样、只检查主动6维或忽略最后叶。固定原maxdepth150不变。

## 4. 原87pair、TCP与箱体姿态

显式绑定 `/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json`，SHA `c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388`。adapter默认仍为v2，不能省略manifest参数。V/native和V/aligned各自现有二进制、source、27 mesh、PQP库等签名均需由最终协议冻结，native/aligned原始返回分别保留，仅aligned用于新节点接纳。

每node需要真实native+aligned两query：准确87个PQP码、均为整数0；完整2个物理TCP并满足原1e-5门；aligned聚合collision为bool且False才清。native TCP不符是保留差异，不要求把native改到通过。总节点N≤256时最多N次adapter调用、2N次worker query、174N次PQP（≤44544）；独立数学FK2N次，adapter原TCP核额外4N次`arm_fk_jac`。这些是后续冻结时的理论计数上限，尚无新增调用或预算。

已有v3 batch response只输出TCP、API码和聚合，不输出箱体或各pair `CloserThanTolerance()`。本local观察已直接保存 `physical_tcp_poses/source_box_pose/active_pairs`，应只读核87个pair身份/8mm/原次序/API码/closer布尔，以及`returned == any(closer)`；已有219项纯文本body/pair审查可以复用，不重跑纯工程源变换。不能把API码0误认成clear，也不能漏掉原注释pair保持不查询的事实。

箱体原source mesh姿态可从独立臂1物理TCP `Ttcp=[R,p]`直接转录原算式审查：`Rbox=R @ Ry(-3.1416/2)`，`pbox=p+R@[435,0,300]`（source是T6+R@[400.7+435+22,0,300]，TCP是T6+R@[422.7,0,0]）。这是原source mesh姿态的一致性检查，不能把它替换成精确抓持Q，也不能据此声称CAD表面/吸盘接触已得到独立验证；数值判据在后续执行协议中显式冻结。T7仍是20mm mesh frame；物理TCP为臂1T6+422.7、臂2T72+400.7，禁止为统一外观改原CAD。

worker生命周期可薄复用已审SBL PATH/TAIL02的进程登记、group隔离、超时、reap、stdout/stderr EOF、残留流和外部三观测费用包络。只复用工程逻辑；原`close_sessions()`吞close异常，单独调用它不能证明清理完成。无需重新编译碰撞二进制。

## 5. 当前未通过门与下一项停止边界

- BUILD02组合工程资格和219项body/pair静态资格可以按不变签名引用；不能升级为V新节点物理通过。
- 编写时LOCAL01尚无execution；其最终source/transport/plain-trace结果及保存独审必须先由root读取。随后才可把真实完整队列冻结，不能预设36请求全部成功或四条连接全部接通。
- 新队列完整性、所有node数学/branch/原限位/碰撞、所有true叶段，以及新box观察一致性均待实际独立资格。成功投影但位于碰撞内应如实分列；失败连接前缀不冒充通过连接。
- 原60wall/120CPU独立POST只是工程计划里的建议，尚不是本页执行授权；需要结合最新实际账、冻结的真实N、独审和整体治理后由root确定下一次唯一执行。不得沿旧建议直接启动，也不新增总R2预算。
- 本项局部通过也仍不是V原生solve、完整起终点路径、RSS成功、PCS优势或正式统计。原离散87pair/8mm不覆盖省略pair、实体CAD、真实吸盘接触、加密采样或CCD；这些边界保持。

本页不修改原211行/历史证书或数据。D080 I–V范围、VI只读保全、正式0/18000、RSS独立推进均保持。
