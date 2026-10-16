# P4 R2 ABB 原 RRT_NR 完整保存路径独立资格 PRE 草案

准备日期为 2026-10-16（Asia/Shanghai）；文件名沿用本轮 20261015 run 标识，不代表提前执行。当前未冻结，未执行任何新科学调用、编译或 planner solve。须等真实 `20261015_R2_ABB_RRT_NR_E2E01` 完成，才可绑定实际 source execution/result/JSONL、完整队列、manifest/binary/source/mesh/claim/hash 与最新逐 execution 自有成本账。

科学问题：环境 II、A01 RECONSTRUCTED 起终点、已通过 Q1 的物理全链 NR C++ 接缝和原 RRT_NR 控制流返回的第一条 exact 非 approximate 路径，能否通过完整独立离散资格。原作者起终点和 KDL 数值失败、旧历史状态均保留，不能把本路径记为作者原始输入/原 KDL 直接合格，不能据此得出速度、成功率或全文复现结论。

最低充分证据：完整原里程点首=start、末=goal 的 binary64 精确一致；每一对连续里程点恰有一次原 state-level reconstruct 完成调用且返回 true，完整原 `qa12/qb12/Confs` 首尾逐 bit 一致；原所有 full12 L2 叶严格小于 0.05 rad。真实原有向 planner tree 必须包含这条首尾标记正确的里程点序列。任何 false、缺失或不严格叶保留原完整记录并阻断路径通过，不能换边、选另一成功候选或平滑/重投影。

队列冻结包括全部里程点、每个原 state-level 调用的两个输入端点和全部返回 Confs（即使 false 的前缀），按环境+完整 12 角 packed binary64 去重，signed zero 保留；全部来源 refs、原顺序保留。所有唯一节点均须独立数学和碰撞验证，不抽稀、不只验叶端点子集，不把原文本路径文件低精度输出当真值。

独立数学采用既有已合格的 local node_worker，不调用 NR/IK/RBS/projection。每节点逐臂两次独立 FK（该实现实际同时形成 Jacobian，按 FK/J 如实说明），检查 `T2 = T1 @ grasp @ diag(-1,-1,1,1)`，位置 maxabs ≤1e-5 mm、旋转矩阵 maxabs ≤1e-5；原机械界使用原 `degrees * 3.1416 / 180`，包括 q6±400°。不作 wrap/lift，不加 PCS 固定主动链或解析分支门。

每节点调用既有 collision_adapter_v3，一次完整 native/aligned 原策略碰撞请求，合计四次 adapter 内部臂 FK/J；全部原 PQP query code 必须为整数 0，aligned 两臂 TCP 必须与独立 FK 通过原 1e-5 门，最终状态 CHECKED、selected=aligned、collision=false。native 原 TCP 偏差与结果单独保存，不把 native mismatch 改记通过。保留原 mesh/pair/8mm PQP 容差及共线杆三角形，不证明 CCD、实体杆表面或省略 pair 的安全。

执行预算为最多 120 秒墙钟、240 秒 CPU，且始终扣本轮 R2 累计 3600/7200 秒总帽；最多 2048 个完整唯一节点。若完整队列超帽，保留整个队列和全部未检查尾部，0 科学启动并记 UNKNOWN，不截前 2048 个声称合格。上限对应数学臂 FK/J4096、碰撞2048、adapter内部臂FK/J8192；实际计数仅由完成/开始事件获得，不用上限冒充实耗。无新增 solve、NR、IK、projection、RBS、RNG 或 VI 构造，正式 Table I 仍不计样本。

父进程使用既有 RunBudget/Evidence 保存前缀协议与原 live process-group CPU 读数，20ms监测父+已回收子+活动整进程组 CPU，墙钟硬中断，单个串行 worker 继承一线程环境。独立 node_worker 数学不变，仅绑定本阶段 RUN/CLAIM/OWN 调度元数据；其 parent_pid、protocol/hash、完整队列hash检查保持。正常节点、逐臂/数学/碰撞partial、原stdout/stderr、事件、完整未知尾部均独占新建保存。异常/kill未返回的观测只按已有前缀计数，不造完成记录。

准备方法：脚本 `scripts/qualify_p4_full_r2_abb_rrt_nr_path_draft.py --describe-protocol` 仅读取保存字节/数组；实际 source 未就绪时标 `WAIT_ACTUAL_NR_E2E01_RESULT`。实际结果产生后重新生成精确 candidate，独立审查并由 root 冻结、提交后才可用 `--protocol` 执行唯一一次。已有 claim/run 会拒绝，不重置、不覆盖、不恢复执行。失败须区分原 source path 返回/我方观测/独立数学/离散碰撞/资源 UNKNOWN 根因，不改原门。

P4 全文211项、Table I22500、500000投影、约50000点对及全部图表/消融义务保持。此项通过只增加一条原离散策略的空间NR路径证据，之后仍需其余环境、RSS/PCS、三搜索器端到端资格与可重复成本 pilot；正式大规模计算另报预算，不进入P2或Isaac。
