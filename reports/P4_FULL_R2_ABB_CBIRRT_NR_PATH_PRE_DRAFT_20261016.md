# ABB CBiRRT_NR 完整原始路径资格 P PRE 草案

2026-10-16。DRAFT_ONLY / NOT_FROZEN / NO_PROTOCOL_OR_PRIOR_OR_CLAIM / NO_NEW_SCIENCE。本阶段只准备 saved/static 四稿：独立NR素材化helper、runner、supervisor和本PRE；不运行项目runner/describe、数学模型、碰撞、RBS、规划或新候选。所有实际冻结、执行、V22账与治理由root独占。原211项原论文义务、VI974/974余0、Table I0/22500、原失败与UNKNOWN均保留。端到端资格后仍先可重复成本pilot再申请正式预算，原文统计规模不缩减。

## 唯一真实来源与前置门

源为唯一实际 `20261016_R2_ABB_CBIRRT_NR_SOLVE01`，freeze commit `119a1b36d918ddd83fe23f49c09bc10b684f02ea`；execution SHA `bc30019b1e5282817adee945fbb4b86a7bb9f30e6f419a6def0e559815a7b1b6`。原生source EXACT、has_solution=true、approximate=false只提供候选。实际人员独立S POST为 `reports/P4_FULL_R2_ABB_CBIRRT_NR_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json`，SHA `549d585f1fb2be390b28a0d64dfb90815e58092a9efd7e3c4d478abebe381ef1`，schema `P4_CBIRRT_NR_SOLVE01_SAVED_INDEPENDENT_POST_V1`、status `PASS_CBIRRT_NR_SOLVE01_TRANSPORT_EVIDENCE_INDEPENDENT_POST`、16711/16711通过，真实外层费用9.06wall/8.71CPU。该POST仅证明transport/source原始树/完整回溯与成本，independent_path_qualified仍false。

runner在形成具体protocol/prior之前先要求实体source execution与独立POST存在并精确SHA相符，人员独立、successful_transport_qualified、completed_process_exit0、外层费用、全部checks和无failures。它绑定原协议/claim、完整bound前后SHA、实际单process/request/solve、所有原native输出/mesh/raw/journal、POST全retained映射；原stdout必须单完整JSON+LF且binary64 exact等于journal parsed_response，不引入PCS setup preamble例外。stderr原NR marker完整construction+solve trace exact相同，request必须等于已冻结S原请求。缺失、false、UNKNOWN或SHA改变直接拒绝，不生成placeholder queue、protocol、prior或claim。

## 完整原 M、树身份与方向

原16Motion/state身份、两个root、父链、root身份/q、PlannerData全部vertices与有向edges须一致。相同q不合并Motion：原start Motion17/state30与goal Motion14/state21恰好同q，实际保存桥仍为Motion16→14、state18→21，不能以17替代14。原 `source_mpaths` 是start `[16,15,2]`、goal `[14,11,10,9,8,7,6,4,3]`；helper严格核每个mpath元素的motion_id/state_id/parent_id/q12与真实树，字段必须是NR原四项，树是NR原八项。`reverse(start)+goal`才是12个实际里程点 `[2,15,16,14,11,10,9,8,7,6,4,3]`；首尾为原已重建并独立资格A01起终binary64。起树边parent→child、桥edge2、goal边child→parent均按原source。

完整trace栈与序列号、entered/completed/observed、实际start/complete计数必须平衡；恰一个void save2file和其内部一个真实mpaths标记，标记与save返回原副本exact。恰11个直接位于save下的state_reconstruct，参数只含qa12/qb12、返回只含returned/path_q12；按原调用序列与11里程边逐一精确匹配，不引入PCS active/passive身份或分支fallback。void save返回不能证明完整；任一false、缺调用、额外调用、端点非exact或不完整M只STOP并保留原raw/原失败，不补点、重新RBS、重投影、换seed、反选路径或截尾。

11个真实M长度 `[65,65,17,65,129,129,65,33,33,33,65]`，所有首末packed big-endian binary64 q12（含signed zero）等于其原参数与里程点。保留全部699个M节点引用、11条边和688个叶距；仅物理查询去重为689个完整q12节点，原Motion/state及边引用不合并。与原save输出首M全取、后M[1:]一致；helper保留全部原数组，独立计算full12 L2，每叶严格小于0.05（实际saved最大0.04951897373867186）。runner额外固定689/688/699、12/11、16树身份、bridge2和原Motion序列，不接受从完整尾部切出的任何子队列。完整队列上限2048；超过只阻止科学，完整原队列仍保留，不做前缀PASS。

## 独立科学判据与原循环复用

新P只验证完整原路径；不规划、不调用IK/NR/projection/RBS/RNG，不改变S source、GD seam或原模型。数学与碰撞science block直接逐字摘自 `scripts/qualify_p4_full_r2_abb_nr_local_draft.py` 的 `node_worker` 内 `counted` 和完整 `for source in queue`，与原NR393路径通过时实际调用的block保持AST一致。local源码SHA `6c2e5bad7b0b16c4657e454e04b50195a226ec4779b16e1b7580ba1239772467`，原NR393 path runner SHA `2b9ec39b195a8470a00c58cd82788d67543b824c8c2039c6609ef88535801fc8`。只增加父层全队列准备、进程登记/预算/外层费用和保存结果汇总，不修改数值/判据或循环节点顺序。

每个q12调用独立数学 `oracle.arm_fk` 两臂，原抓持/FLIP闭链位置及旋转矩阵maxabs都≤1e-5、原 `limit_score`（机械角界按原PI=3.1416）、保持原几何/基座/抓持/单位/关节顺序。NR是full12数值流形，不施加PCS固定被动链/解析分支身份门，也不继承任何PCSrole字段。每点无论数学是否通过，仍按原循环进行一次v3 native+aligned collision适配调用，保留完整原碰撞raw、每variant全部PQP code与TCP pose consistency；所有code为0只是API执行资格，最终需aligned pose一致且collision=false。native另外报告；不把native与aligned结果混为一体。

完整689节点要求数学FK started=completed=1378，collision started=completed=689，适配内FK/J started=completed=2756；实际每query variant code数量与总PQP由真实response计数，不用预填代替观测。loop数值block/计数AST不变，计数包装还原原physical_nr.arm_fk_jac。未完成点、当前partial、所有已完成文件、真实started/completed和全部raw均保留。节点有任一数学/限位/aligned碰撞失败，完整资格只能REJECT，source原EXACT不改。所有节点完成、全真和完整worker/hash/预算门才可 `PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH`；仍是原离散source-policy，不能推出连续无碰撞、完整实体rod/遗漏pair安全、作者原KDL数值等价、算法统计成功率/优势或P4完整复现。

## 资源、进程与交付边界

唯一拟run `20261016_R2_ABB_CBIRRT_NR_PATH01`、claim `P4_R2_ABB_CBIRRT_NR_PATH_FULL2048_120W_240CPU_20261016`。本P单项最多120wall/240CPU，仍扣原R2总3600/7200，碰撞worker每进程CPU240硬帽；不是另授权正式实验。冻结前动态选覆盖全部真实execution的最新权威charged ledger（目前root正在完成V22；不在草案预写预测成本），每个历史外层证书只替换内部费用一次，孤立supervision charge须先补账，历史未测尾UNKNOWN保留。实际全部源码和protocol提交、entry独立静审和root全队列冻结后才可唯一启动。无retry/reset/resume。

父层采用既已通过的CBiPCS P生命周期外壳：exclusive GNUtime FD/inode、真实parent PID/argv/hash，parent own+reaped+登记live collision groups CPU、20ms预算alarm，fork/setrlimit/exec登记短mask，只作用工程生命周期。两个native/aligned worker须实际登记，start/close单PID同组、优先原adapter.close再独立scan/kill/wait、actual after-reap空组，merged stdout/stderr实际EOF、空pending/tail、原selector确实关闭，全部进程和pipe闭合事实保存。即使原close吞异常、初始化未入_sessions或Popen先已退出，登记列表仍不丢失；不通过cleanup或证据门只能STOP，绝不默认成功。

外层GNUtime完整计import/preflight、saved全部raw/哈希/素材化、模块加载、689节点数学/碰撞、日志/数组、全部worker回收、最终bound/prior/protocol/claim SHA、execution/receipt持久化和退出。Decimal+.01wall/+.02CPU仍须单项及累计通过；supervisor自身journal/fsync边界外明确披露，内部external_supervision_qualified保持false等人员独立POST。计时器先关闭再cleanup，全部资产前后SHA以及最新prior集必须不变；超预算保留真实前缀和未检查尾，不增加预算、不改门。执行后仍由另一审查者仅读全部节点/原M/边/物理raw/counts及成本完成独立POST，再更新论文覆盖表/账目/治理并提交GitHub。

## 已有成本证据与工程等价持久化

root检查旧CBiPCS P413实际耗104.88wall；保存事件显示node0至node412约96秒，约0.23s/节点，不能直接把带逐文件fsync的原P外壳扩至689而盲跑。NR393实际3.77wall的science worker使用 `build_p4_full_r2_abb_rrt_pcs_e2e.new_json`，每个exclusive文件close、无逐文件fsync；当前TAIL Journal.add是即时unbuffered append/flush，finish才一次fsync。以上来自旧真实saved记录；按689规模的耗时判断只是工程风险预测，不是新pilot、成功保证或正式成本测量。

经root明确批准，本P的`new_json`直接逐字复用NR393原函数，science block AST不变；所有5类每节点文件即时写完close、全部真实journal照常append。完整成功或异常时，在worker退出后把当时所有已close散文件（含partial、queue）与finish后的journal写入新exclusive无压缩 `complete_saved_prefix.tar`，保留原散文件不删除；每项记录实际原字节长度/SHA、唯一member名，归档fsync和目录fsync后，再逐member核包内完整字节与散文件相同、全file集合无漏/重/额外。只有完整验证的durable snapshot可支持PASS。execution/receipt后续分别exclusive写入和fsync，最后目录fsync，全部仍在同一GNUtime实际成本边界。

为避免在关闭science timer后无限做重I/O，worker清理后用同一绝对begun/CPU起点重开20ms final I/O alarm，覆盖最终全部bound/prior哈希、journal finish、归档复制、归档与目录fsync、全部member/散文件验回和归档hash；逐项另做budget.check。超120wall或240CPU仅触发一次中断，保留未完成包/散文件与diagnostic、终态STOP，不续写重试或延时增加预算。若时间已耗尽，不能声称前缀archive已durable；保留其真实partial状态。终端execution/receipt与其fsync也计外层完整时间，receipt及独立外层Decimal上界仍须满足原帽，否则STOP。此方案不改变文件内容、科学判据、节点队列或任何采样/规划，仅用可逐字核验的单包耐久副本代替数千次逐节点fsync；不得把工程预测当新科学成本pilot。
