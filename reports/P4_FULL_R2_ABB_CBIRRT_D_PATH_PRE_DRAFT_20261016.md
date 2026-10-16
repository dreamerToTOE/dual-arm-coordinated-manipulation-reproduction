# CBiRRT D P：完整保存路径独立资格 PRE 草案

2026-10-16。DRAFT_ONLY / NOT_FROZEN / NO_P_PROTOCOL_PRIOR_CLAIM_OR_EXECUTION。本阶段已完成 P 源码草案和保存数组提取，尚未执行 P 物理检查。本稿和源码须先经人员独立静态审查，再由 root 冻结最新总账、完整队列与具体协议、提交并唯一执行。原 211 项义务、正式 Table I 0/22500、VI 974/974 余 0、全部原失败与 UNKNOWN 保持。

固定来源为唯一 `20261015_R2_ABB_CBIRRT_D_SOLVE02`，实际 execution SHA `c7cbd868da1cd9feb149bc057c4a63ff3e722b81123998e1a8cc5e8e1bab5906`。原状态 `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT`，exact/has_solution=true、approximate=false。真实人员独立 POST 为 `reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_SAVED_INDEPENDENT_POST_20261016.json`，schema `P4_SOLVE02_SAVED_INDEPENDENT_POST_V1`、status `PASS_SOLVE02_TRANSPORT_EVIDENCE_INDEPENDENT_POST`、SHA `730dbb69ff3749975639dd9cad2fe1f31ca45cb2bf370c0470cfddd329d64412`，5284/5284、费用与入口证据通过；`independent_path_qualified=false`。S01 原 STOP/一 solve 已进入/源末 -9/无完整 JSON 及费用独立保留，不以 S02 覆盖。

生成具体协议前须核 S02 冻结 protocol/claim、全部 bound before/after、唯一请求/进程/EOF/exit0、两行 stdout（精确一次原 55B setup 日志加唯一原 JSON）、完整 stderr trace/journal、运行 mesh、全部原生 path/partial/temp 输出和独立 POST retained SHA。仅从原高精度 response 提取，不使用低精度 path 文本修角，不运行新 RBS/solve 或补桥。缺实际证据或证书则在生成 P 协议和总账前硬拒绝。

保存数组 materializer 合同详见 `P4_FULL_R2_ABB_CBIRRT_D_PATH_MATERIALIZER_PRE_DRAFT_20261016.md`。实际六个 Motion、五个 milestone，两链 `[[6,4,1],[5,3]]`，真实桥 Motion 6→5；Motion 7/5 的 q 相同而身份不同，保持区分。五次原回溯 `[true,true,false,true,true]`、M 大小 `[109,145,2,33,129]`，false 主动 0/b3/M2 和原主动 1/b3 fallback 完整保留。选中四条真 M 为 109/145/33/129 点，共 416 个边引用、413 唯一物理节点、412 叶；最大叶距 .049872908712302065 rad，严格小于原 .05。保存数组分析产物 `work/cbirrt_d_source02_saved_materialize_20261016/full_queue.json` SHA `38ce4780897186fadff49f15cec239008df237b519deb9d16ddbac73eedb852f`。此提取只做保存数据算术，物理检查数为零。

P 已填入 `scripts/qualify_p4_full_r2_abb_rrt_path.py` 的原完整 `for i,q in enumerate(spec['fixed_queue']['nodes'])` 科学循环及原 counted FK/J 包装；AST 对比均完全一致。原文件 SHA `bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865` 绑定并在生成协议前核对。全部 413 节点保持原顺序，独立双臂 FK、闭链位置/旋转 maxabs 各 1e-5、原机械限位、每条边对应被动解析分支、64 倍 binary64 epsilon 零分支规则、v3 native/aligned 原离散碰撞及 PQP 8mm 原判据不变。原 mesh/pair 和 native 全结果保留，接纳仍只依据 aligned 原离散策略。零新 IK/NR/projection/RBS/solve/RNG/VI/正式统计。

完整唯一队列最多 2048 点、单 P 帽 120 秒墙钟/240 秒 CPU，计入原 R2 3600/7200 总帽；不是新正式规划统计预算。必须先提取并冻结全部真实队列，超 2048 保留全队列并拒绝科学执行，不验前缀、不换点、不重采样、不放宽门限、不重试或续跑。生成及执行时逐 SHA 核最新权威 ledger 和全部实际 execution 集合；已有外层独立证书以其上界替换本项内部样本一次，历史未测尾部仍 UNKNOWN。当前 V17 实际 35 execution、charged 580.675705375994 wall/530.628923 CPU 仅作本 PRE 事实记录，实际协议须现场绑定最新权威账，不能写死旧 prior。

外层 supervisor 复用经审 S02 的 O_EXCL time FD、真实 GNUtime 父 PID/argv/inode 证明、完整 child lifetime 测量与 Decimal +.01 wall/+.02 CPU 保守上界，改为 P 身份与 120/240 帽。整个科学 child 的 import/preflight、实际双 worker、清理、hash、journal/execution/receipt 持久化和退出均在外层计量内；supervisor 自身 metadata/fsync 范围外明示。内部 execution 与 charge 的 `external_supervision_qualified=false`，最终仍须真实人员独立保存 POST。

P 的生命周期适配只登记原碰撞 worker 的 Popen，不改变原 query/数值逻辑：仅 fork/exec→登记短窗口屏蔽 SIGALRM；子进程独立组/CPU 硬帽，启动即纳入 live CPU。即使原 adapter 构造在写入 session 前失败，中央 registry 仍 kill/reap；开始/清理进程组现场快照保存。先关闭 timer 再清理，调用原 close_sessions，确认 selector 实际关闭，再有限非阻塞排空并实际观察 stdout EOF，保存 pending/tail，不把吞掉的 close 异常推断成通过。两个进程均 exit0/reaped、完整登记一致、无意外尾部/遗留组才有 worker 成功门；清理或保存异常只能 STOP。节点 raw、完整未完成尾部、事件与全部 hash 保留。

原 S02 EXACT 只提供候选，P 必须通过全部数学/分支/限位/离散碰撞门与最终独立保存审查才可称完整原离散 source-policy 起终路径。即使 P 通过，也不证明连续无碰撞、实体杆/省略 pair 安全、RSS、PCS 复杂优势、全局成功率或完整论文复现。端到端资格后另做可重复成本 pilot 再申请正式预算；不提前 P2/Isaac 或结题 Word/PDF。
