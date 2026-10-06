# WORKLOG

## 2026-10-06 — PhysX时基production通过并fresh可见GUI启动

build02修正重名后58.5s/exit0，source6fa161e/binary75f798a1、源码冻结期间编译；63Python/两组C++通过。fresh可见GUI再次加载同原场景，图片确认第一供料落稳后启动normal1.0首件，没有用旧慢速/旧初始化stage代替。同步shared phase来自同一次stamp，单臂也用原子反馈；保持原轨迹和保护，新增缺失ready/age/stamp错误日志及侧接近互锁详情。真实结果RUNNING，读取原子消息的外部20s只读时钟采样无命令。

## 2026-10-06 — GUI首件负结果与实际物理时间计时PRE

run02实际COMMON搬运完成，但重抓侧臂下降CONTACT跟踪最大10.109deg并与Cube真实接触，left raw86.323Nm，原保护拒绝/安全OPEN，无X/Y。最初日志缺接近互锁细节，不能称闭合超时；补正式负结果/held审计。暂停余下drive再正常停owned GUI0，不无界面重启。仅Task01执行器改用既有原子PhysX stamp，共享双臂进度、不用wall fallback；get时原250ms且回退拒绝，旧Task26/27、路径、physics、ACM等不变。新增进度C++测试，63Python及两政策组PASS；首编译final hold重名失败保留，build02修正后进行中，不边改源边build。

## 2026-10-06 — 可见GUI启动诊断及首件正常倍率回归

按用户“启动gui继续测试”。先官方可见GUI加载原fixture/Bridge/readonly recorder，Prim/物理存在但空网格，机器人命令0；渲染detach/readd排查后native139，完整负记录保留。撤下仅本轮新增且未使用的GUI原型，改复用原记录器的SimulationApp可见入口，显示原完整场景成功。新增缺DISPLAY拒绝的GUI入口、循环执行客户端（仅127.0.0.1:8226）、两GUI设置单测；不改原场景/Bridge/物理/门限。

新fresh可见run02第一供料真实落稳、截图确认后启动08f3060a原production，first1/max1/scale1/roll-15/rear45。63Python PASS，无headless进程启动；实际结果RUNNING，原反馈过期问题待观察，不从配置通过推断物理通过。

## 2026-10-06 — 正常播放倍率与可见GUI工作流

按用户新要求停止延续无界面实验。核对播放计时为wall_elapsed/time_scale，上轮5.0=20%，旧默认3.0约33.3%；新`TASK01_DUAL_SUCTION_FIXTURE`默认1.0，增加明确播放比例与保留12%规划限速的启动日志，有限值/倍率>=1门禁在任何Arm命令前拒绝错误输入。旧Task26/27节点默认3.0不静默改动，历史显式5.0日志不篡改。README/启动指南记录GUI场景→Play→原Bridge→原子反馈全部步骤。没有改接触速度规划、场景、ACM、保护门限或启动新物理实验；编译与软件检查结果另见TASK01_GUI_SPEED报告。

此前full01最终归档FAIL_X16_STALE_OR_INVALID/controller1、headless0/completed[]；17几何匹配、5862held/21398atomic/3566sparse完整性0错，未到空载转场。保留原数据和未知根因，不能用normal速度设置称修复了反馈问题。

## 2026-10-06 — 空载局部管线重放PASS/真实five-Cube开始

第一请求局部action探针3个postprocessed路径被MoveIt拒绝，负结果保留。最终仅新fixture OPENhandoff复用当前进程本机OMPL与参数副本，segment fraction0.0005/原RRTConnect/原目标/完整世界，IPTP不改q路点，顺序第二臂含第一预测终点，执行前再以第一实测关节完整FCL复验。无远程Scene或参数写/额外move_group/背景预规划，旧及加载链不改。probe03同f237cff串行重编译并实际无命令PASS，首编译main-local槽位lambda错误与中间binary一致性边界保留。原61Python/两C++/benchmark36nulls/hash PASS。新fresh原headless普通供料five-Cube回归启动，source/binary检查后运行，暂不预记完成。

## 2026-10-06 — full02终局归档与空载转场PRE

控制器1、第三件实际双吸推压放置成功但handoff未完成，不能把三放置/两batch冒称五件成功。正常停自有headless0并审计完整stream：105精确stamp、36469held、51175atomic、8529sparse/0errors；原raw保存。当前只读读取MoveIt world/ACM证实无Cube条目全豁免，不能以扩大ACM修复。准备仅新节点的有限空载路径候选筛选、同一实测完整起点和第二段预测partner起点，原RRTConnect/目标/每侧3mm冗余/30mm退出不变。不是冻结的Task22后台沙箱预规划。

磁盘不足时仅自有已结束full01空闲日志gzip无损压缩，逐字节解压SHA验证；元数据保留路径/hash/恢复方式。没有删除原始内容或改用户文件。

## 2026-10-06 — full02前两件物理完成，第三关键回归继续

第一rear候选1–4联合gate拒绝、5/24通过后执行，第二1/24通过；两件实际X16/Y16/双CLOSED/无释放角色交换及短RRT转场batchPASS。最终短清障center0.302/0.407、deep0.156/0.091、side0.259/0.397mm。第二rearOPEN norm2.026→1.031→0.036mm。原门限未变；只前两件证据，第三/后两/最终同一步审计待结果。

## 2026-10-06 — final binary full02启动正常

不再边改源边编译，CMake -B目标重建57e72f83、两组root arm字符串与run前SHA验证成功。新fresh原stage/正常供料/零预置，自动READY后启动controller模型正常并已进入首件实际运动；先前full01未运动负记录保留。没有放宽保护、改场景或用采样空转宣称物理通过。完整回归和同一步审计继续中。

## 2026-10-06 — production二进制一致性审计更正

full01控制器启动阶段拒绝/命令0；通过只读RPC核对六参数类型值正确，strings揭示production缺root arm前缀，probe有。编译时修改include造成已读旧源码、链接更新mtime并后续no-op；不再称production与a3fceab一致。保留startup负日志/3600s空闲采样（非运动验收），串行CMake -B重编译/字符串及SHA验证后另fresh full02。未修改源码行为/场景/物理/门限来掩盖失败。

## 2026-10-06 — 联合rear预检实现/诊断验证，物理fresh复测启动

首三候选只读HIGH IK+连续下降+双X/Y+短退出复用现有本地FK/FCL，不再拿旧solo链代表新协议；后两精准solo不变。原blocked姿态拒绝、3替代完整本地链通过。参数读取首轮拒绝（实际是left/right_arm.* LMA）修正后通过，旧失败日志保留；61Python/两C++ PASS，第一次C++临时目录不存在不是源码失败，set-e/mktemp重跑通过。a3fceab控制器SHA174d6ef7，fresh零预置五件headless启动；没改场景/物理/门限，未称物理完成。

## 2026-10-06 — BUG021无命令重放与联合链修复PRE

probe从/move_group有界读取当前KDL参数，用第三件held step46343精确14关节/Cube重放；原rear固定侧HIGH 60/60解都有工具↔right link5碰撞。保持rear TCP，前7有效IK找到3终点组合自由。保存build/side_goal_probe/rear_goal_search日志及binary SHA，未发机器人/吸盘/供料/导轨或远程Scene命令。新增联合候选预检PRE见原子反馈报告：纯软件、首三件、旧后两与原模型/物理/ACM/门限不改；先编译/共用只读链，再真实fresh回归。

## 2026-10-06 — full01真实2/5，第三goal诊断

前三后杯OPEN精调都通过，第一第二新主从双吸X/Y、释放/短RRT转场真实通过；第三rear重抓后side HIGH无合法goal sample×8（各约20s），安全双OPEN/exit1，不执行第四第五。保存70精确stamp几何/37804完整held审计和全部失败日志，headless正常停机0；无持件机器人-墙非零接触。新增纯probe精确14关节/Cube输入、60有限KDL种子与FCL pair计数，不构造Arm/发命令/改远程Scene。不是目标全局不可行证明，也不直接改控制器。

## 2026-10-06 — 首件新协议实际通过，开始完整五件回归

runtime39f1a0c原场景rear45/side-15，后杯OPEN两次XYZ后norm0.205mm，X16/Y16/双吸附主从换角/释放/HOME全部完成/controller0，最终中心0.303/deep0.212/side0.216mm。同一步35几何精确匹配、8470held0完整性错且窗口无非零机器人-墙接触；原80Nm/2.5mm不变。Isaac正常0退出，MoveIt关闭-11另记。保存首件报告/metadata/audits；同binary fresh first1/max5继续，不能复用这一件称全部稳定。

## 2026-10-06 — rear45真实Z残差与后杯OPEN精调

rear_roll_cube01最终X1原alignment失败、双OPEN，精确stamp确认rear Z为PRE_CLOSE -2.363/CLOSED -2.462/X1 -2.578mm；不是USD假报，没到墙。保存metadata/geometry_audit/held_analysis，失败不抹。runtime39f1a0c新增仅前三rear OPEN的有界XYZ，上一命令FK加实测残差，原Cube参与完整联合FCL，helper保持实测姿态，失效拒绝CLOSE。初编译linkPose签名错误exit2，修正后build50.4s PASS/61Python/两组C++/analytic36nulls。原模型/物理/保护门限不改，真实新首件待测。

## 2026-10-06 — 后腕名义检查与实际重抓接入

- rear45镜像/side-15无命令前三链3/3 PASS；1330双腕节点三墙均0交集，不仅查深墙。
- SciPy1.8 HiGHS默认status4两次保留，换同约束内点LP并检查残差，61Python/C++PASS；没有放宽交集判据或跳过坏行。
- 新节点前三件后抓OPEN RRT/预演统一姿态函数，后两件/旧节点原pushPose不变；待编译和新鲜首件原门限物理验证，不能提前PASS。

## 2026-10-06 — 原子反馈实测与后腕侧墙定位

- runtime88ef454/build54.2s/binary31d862a6…；原子反馈首件真实X16/Y14，Y15原保护停止，bothOPEN/完成0。33精确stamp几何校验匹配，60Python/C++PASS；源对照显示USD可在有效物理正gap时输出<-1mm。
- 同步问题工程修复不能解决几何碰撞：实际rear right link7↔+Y墙745.808N。旧nominal02补三墙凸包，有7右腕Y节点重叠；原deep-only证据限缩。
- 第二阶段PRE：只读后杯面法向worldX镜像转腕45deg，中心/法向不变，使腕部向中央。需前三IK/FCL/TCP+原USD双腕三墙检查，暂不改执行器/物理/门限；失败保留。

## 2026-10-06 — 腕姿实测负结果与持件原子反馈

- dd63c74编译/非法31deg提前拒绝通过，首件X3旧rear gap负值停止；保存4738 held/4085 sparse/0错误，未到深墙，不声称姿态物理修复。
- 本轮PRE：定位旧USD显示滞后及独立latest观测，新增可选live PhysX五Cube+两link8单view快照/TCP固定变换/单PoseArray；独立3+2控制节点必需该源、格式/时间/250ms门控、不回退旧反馈。旧场景/bridge源码/后两单推不变。
- 56Python/C++边界检查PASS，编译和新鲜首件headless验证进行中。P2/P3未实施，36nulls不填，benchmark未冻结。

## 2026-10-06 latest — 真实接触诊断与只读腕姿候选

诊断02原source d35cc0c/b749abc实际首件复现Y15保护，原物理/模型/80Nm/ACM不改。先自动safe abort，再手动结束仅仿真记录进程；保存10538连续held与4598稀疏行、精确峰值接触/DOF、服务FK/FCL重放和原mesh/hull审计。发现left link7深墙实体接触，而同关节MoveIt墙检查自由；测量FK一致，不能继续把根因只归为闭链内部力。

新增只读重放脚本、凸包审计和9单测，53Python通过。探针0cfdbaf名义3链通过，但多线程日志穿插污染数据，分析器拒绝；c13ea40改独立不覆盖数据文件，重新nominal02通过3链与1330原mesh离线节点/0墙重叠。杯面中心/法向不变，仅面内转角候选，仍未改执行器/运行新物理任务。原资产fresh GET SHA与cache一致，未使用不明替代模型。

## 2026-10-06 follow-up — 网络恢复，原场景第二次启动

原S3直连/代理HEAD恢复HTTP200，runtime d35cc0c正常push成功；保留startup01失败。相同官方资产/原参数的startup02重新运行，held live handles与首件物理诊断仍待验证，尚未发controller命令。BUG017根因未解决，BUG018外部连接暂时恢复不抹掉负结果；模型/物理/门限/YAML不变。本段更新此前“final”失败checkpoint，不叫新物理PASS。

## 2026-10-06 final — 本轮启动负结果，未开展物理推压

实现持件phase只读记录、全机器人contact路径/DOF targets/positions/velocity/projected effort、同一步/丢步/空流/非有限分析门控，44单测与编译PASS。真实启动在FR3远程stat连接失败，未导入诊断到有效机器人；本轮不是Y15再次失败或修复证据。尝试直连/代理/另一S3域名/SSH及SDK缓存lookup，均失败；离线缓存含FR3但来源映射未证实，不擅自替代。原场景/工具/质量/摩擦/门限/ACM/YAML哈希未变，自有进程结束。

## 2026-10-06 — 持件诊断搭建

复用原pose/contact sampler和release logger接口，专用held phases；记录机器人全部link/桌墙Cube接触对、DOF positions/targets/velocities/projected effort，零接触对仅压缩不设力阈值。保持旧logger默认行为；39 Python/build PASS，启动验证中。

## 2026-10-05 final — 实测换角色复测结束，保存未通过结果

`dual_fixture_cube01_measured`/e0477ab/binary d1658940…：X16与Y14段实际完成且双CLOSED，Y15 raw effort86.975/32.984Nm触发80Nm保护。controller1/completed0，后续四件保持停车，不叫首件或五件PASS。保存metadata、analysis、protocol与精选控制器原日志。

新增只读 `diagnose_released_state:=true` 探针并编译66s，释放后实际14关节姿态对桌/墙/其他物体联合FCL通过；仅本地忽略当前合法接触Cube01，不修改远程Scene/ACM、不发布机器人命令。不能回推互锁步无碰撞。末双CLOSED样本距名义侧压终点还有17.354mm；原release logger只采释放窗口，本轮没进入它，零接触样本不等于零接触力。

35 Python PASS；稀疏姿态9432/完整性错误0；自有Isaac0退出与MoveIt关闭-11分别记录。模型/物理/门限/benchmark哈希不变。持件同一步接触/关节观测待下一步，不从两次失败推断必须改基准或加论文力控。

## 2026-10-05 follow-up — 保存首块负结果与实测换角版本

首件新协议实际X完成16/16双CLOSED、贴深墙0.286mm，但Y开始触发未细分互锁，控制器1、双OPEN、completed0。保存4747无完整性错误PhysX样本与精选原日志/protocol，不把搬到深墙叫整件PASS。

仅新分支增加换角时实测双臂起点/新Cube GT、当前状态FCL与重算Y/退路，记录互锁rear/side及raw力矩。e0477ab编译54.3s，35 Python/4 C++ PASS，新鲜首件复测已启动。没有改场景/模型/物理/ACM/门限或开始论文力控；根因未确定。

## 2026-10-05 — 新3+2协议实现与首块验证

完成PRE报告后新增独立节点/策略header/共享实现include/无执行探针，保留旧节点。前三件建立rear+朝中央空隙side两个面中心吸附，双CLOSED下共同X推入与不松吸盘的主从互换Y压紧；第四第五继承精准单推。保留80Nm原始effort监督、原接触几何门控、失败双OPEN并回写当前Cube。工具盒体初检不等于FR3证据。

完整探针先失败于本地IK缺参，再暴露独立轨迹时间缩放不保相对几何/Cartesian跳支。复制当前MoveIt运动学参数、复用连续世界FK微解算成同一位移网格、扩大对置名义seed覆盖后，最终前三链全部通过，relativeTCP最大约0.002mm；无机器人命令。34 Python+4 C++策略测试、colcon build PASS。新鲜headless原场景首块运行中，源码ff20ac3/binarybd1de5b7…；不借用旧5/5或启动纸面力控。

## 2026-10-04 final — 完成普通五件回归并收尾上传

保持已编译源码 `df9c2c0` 和原场景/模型/物理/门限，实际跑完零预置 first_batch=1 / max_batches=5 / time_scale=5 / release hold=0。五个 batch 均 PASS，controller 0，双臂 HOME；普通空载 Cartesian 成功，新 RRT 备用未触发。保存 metadata、analysis、release_windows 和精选 controller 原日志；raw 留本地、不提交大数据。18,498 条稀疏姿态 / 0 完整性错误，3,212 条释放诊断。复核 Cube02 XYZ 两次有限修正的规划 0.069299 s / 慢速执行 7.418296 s，不把约 28.77 min 的 demo 当效率结果。

停止自有 Isaac、MoveIt 与控制器进程；保留 MoveIt teardown -11 / bridge 1。六份记录和 TASK01 报告更新，历史普通失败、重放 01 失败不抹掉。此前退出成功与本次成功都保留，但不能据此证明所有冗余构型可靠或 BUG-016 已修复。TASK01 仍待用户基准/接触/测量审查，TASK02 未开始。

## 2026-10-04 — Bounded fallback built and replayed before commands

FinalRRT source/runtime df9c2c0 pushed; fullbuild55.8s PASS. OriginalMoveItrequestgoalconstraintsreplaceincorrecthandwrittenaggregate-angleguard, notsuccessthresholdchange. Negativefirstreplayretained; finalno-commandreplay02PASS1277jointFCLsamplesincludingreleasedCube; syncREMOVE/absenceconfirmed. Ordinaryheadless0preplacedfive-runlaunched, binarypinned, resultpending. Prioroldexitsnotdiscarded; sameCube02differentredundantqrecorded. Existing-objectbitwise restoration comparison needslaterunitreview; noclaimresolved.

## 2026-10-04 — Reconcile prior retreat successes with normal-feed failure

UsercorrectlyrecallspreviousexitPASS; comparedactualCube02jointseedsratherthanassumingglobalregression. Currentleftj3=-2.7546/j4=-2.8750rad, tinytrackingdelta; originalFKguardrejectsbadCartesian. ArchivedFAILsummary17319poses/0errors, stopownedheadlessafterbothOPEN. PreparingRRTreplayusingretainedrailshift0.1m, sameworld/target; threecandidatebudgetandshortestjointtravelranking, verifiedsceneundo, no robotcommandsinprobe. Existing28PythonPASS; build/physicalpending. PREinTASK01_RELEASE_CLEARANCE, no scientificchange.

## 2026-10-04 — Diagnostic failure retained; actual side seed engineering repair

Diagnostic02 Cube02SIDE_HIGH_APPROACH t0 activeCube collision0.783mm aborts before sidepress/release; onlybatch1PASS. Collected13227poses/1617releasecontacts0errors; stoppedheadlesswithbothOPEN, MoveItteardown-11. PostabortstaticrearCupgap0.267mm notexactfailuretimestamp. Mixedcommandseed+actualGT identifiedinsource; adapted independentactualsideplan tosinglemeasuredRobotState andexistingdeltabounds/graspstate, currentCubeFCL stillstrict. Sharedfinite-seed helper/unitextended; runtime2fbfa0bpushed, build62s/finalincremental0.44s/Python28testsPASS. Normalhold0/fullfive preparing, originalreleasedrift remainsOPEN/noeffectclaim yet.

## 2026-10-04 — Release diagnostic startup/build/first-object checkpoint

Compiledindependentvariant56.5s/package56.8s/total, committedruntimeb259366. Startup01failsBRANCH_SIGN lookup beforecontroller, failure.json retained despiteIsaaccloseexit0; corrected logger config namespace only. Diagnostic02 startsnativecube/tool/contactviews beforecommands; optionalhold3s distinguishesrelease fromclearance. First-objectholdX0.028mm,clearanceX0mm; secondobjectstillrunning. Addedsummary peak/mixed-step/nonfinite regression, Python28/28PASS. Exactbinary/pins/commands inmetadata. Diagnosticstopatbatch2 prevents later loaded motion atsimdeadline; not ordinaryfullfive proof.

## 2026-10-04 — Release-window diagnostic preparation

Reread mandatory instructions/currentTask01/spec/P2/P3 cards and statuses, sent PRE-TASK. Scoped userapprovalto release/clearance engineering, not forcecontrol/model/gates. Addedphasepublisher plusoptionaldiagnostichold default0 onlyindependentnode; opt-in headless usesexisting validatedPhysicsContactSampler and nativeRigidPrim tools, noUSDdisplaypose. Full-rate onlyduringreleasephases, sparseordinaryposesunchanged. Phasearrivalsasyncexplicitlylabelled; collisionforcesnotD6wrench. 25softwaretestsPASS; build/actualdiagnosticpending.

## 2026-10-04 final — XYZ validation completed, release-window failure retained

Built runtime f0812a4; C++/22Python/real RobotModel PASS including XYZ obstruction rejection. Started actual normal-feed headless with unchanged scene/bridge hashes, no preplaced objects. Cube01PASS; Cube02 needs two XYZ corrections and passes original preclose gates (X0.606/Z0.451/gapdelta0.275mm). Planning0.078621s/execution7.569621s, bounded1mm and3checks. Actual Cube02 later fails final deep gap5.138mm against3mm despite pre-side-press0.488mm; physical data shows negativeX retreat around rear suction release after sidewall reached. No loaded/contact/physics/gate repair silently added. Preserved full fail/exit1,7680samples0errors and release_drift.json; no later cube advanced. Stopped exact owned processes, headlessexit0/MoveItteardown-11. Updated all six records/task/report/metadata; branches uploaded through command-local existing proxy after directSSH failure. TASK01 IN_PROGRESS/36nulls, TASK02TODO; next release/contact diagnosis needs scope decision.

## 2026-10-04 — Pre-close XYZ engineering implementation

Read required task/benchmark/paper records and git status; announced PRE-TASK. User approved merged XYZ correction rather than three serial axis moves. Added pure finite-input helper with total 1mm vector cap, accumulated commanded-FK targets in the independent variant, OPEN guards, static FK/Isaac diagnostics and timing. Preserved legacy Y logic under other nodes and all existing gates/model/physics/loaded control. Extended mathematical and no-command RobotModel probes; build/physical evidence pending.

## 2026-10-03 — Normal full-five negative result preserved

Actually ran normal feed first1/max5/time_scale5, no preplaced cubes and unchanged binary77b4f499... . Cube01PASS (center1.605mm, deep1.006/side1.251mm), short/RRT handoff to Cube02. Two fine Y corrections converge gap asymmetry to0.001mm but X mismatch remains3.150mm>2.500mm, so pre-close safely exits1 without suction or later tasks. Stationary TCP read-only snapshots support3.149754mm difference, not synchronous dynamic calibration. 7214 valid sparse poses; no code/model/gate changes. Added null guard for parked/unexecuted Cube04 neighbor geometry in summarizer, not physical scene. Saved raw/metadata/analysis/report, stopped all owned processes; MoveItteardown-11 persists. User-review boundary: do not silently add XYZ feedback/model/material changes to obtainPASS.

## 2026-10-03 — Normal five-Cube regression preparation

Read current handoff and scoped validation records. No hard choice needed to test the current variant from normal feed. Added zero-preplaced mode to the existing sparse headless probe, preserving Bridge automatic batch1 and requiring actual first arrival (no empty-set READY). Expanded read-only summaries to retain all five final geometry lines and distinguish placement PASS from feed ARRIVED. Original runtime/controller/scene/physics/ACM/gates unchanged. Full report PRE-TASK saved; full-run result pending. Keep prior negative results and all numeric/model decisions pending.

## 2026-10-03 — Final empty retreat validation / review stop

Clean Cube04→05 trial exits0, batches4/5 actual PASS: fourth neighbor0.375mm/deepgap0.244mm, fifth position0.530mm/deepgap0.476mm. Macro-scoped live-start ordinary Cartesian succeeds with currentCube strictFCL (540/287 samples), fallback not physically triggered; separate long no-command replay proves seeded solver feasibility. Fourth no trim, helperOPEN; short clear/RRT next-object transition preserved. 7778 sparse samples0errors; independent fifth4691 samples0errors andexit0. All owned runtimes stopped, MoveIt teardown-11 repeats. Exact metadata/raw/summary in three empty_retreat run dirs; final report complete. No reliability/full-five-new-variant/force/paper/freeze claim. Six records updated, protected folder/old scene/material/ACM untouched; stop before model/contact/numeric decisions needing user review.

## 2026-10-03 — Empty retreat repair checkpoint

Added macro-isolated measured-state empty retreat / fresh released-Cube FCL world / bounded seed-continuation fallback, reusing existing fine IK rather than changing loaded/contact control. Added read-only real RobotModel FK/FCL probe and pure C++ guards; added optional four-preplaced fixture mode. colcon final completion 57.2 s, policy PASS, Python19/19, unchanged YAML/36 nulls. Physical results pending; negative prior fourth/fifth results retained.

Follow-up: final real RobotModel basic probe PASS after correcting only invalid-quaternion test input (ROS default w=1). Long rounded-seed no-command replay left404.716/right301.601mm PASS +610 FCL samples including released Cube. Actual isolated fifth full cycle/controller exit0:0.540mm center/0.514mm deepgap, 4691 sparse samples, no integrity errors. Four fixture cubes preplaced; fallback not physically triggered, so no causal/reliability claim. All owned first-run runtimes stopped; MoveIt teardown -11. New clean actual fourth/fifth trial starting.

## 2026-10-03 — Cube04 variant physical handoff / tests stopped
- Final `7be3659` binary time_scale=5 passes fourth: precise staging 0.040 mm, final neighbor 0.227 mm, deep gap 0.413 mm, cell error 1.339 mm. No helper-side suction or inner trim; short-clearance/RRT transition to fifth completes.
- Fifth actually dual-carried/dropped, but actual empty Cartesian retreat fails original 5-mm line-deviation guard (up to 450.1 mm), safely opens both cups and exits 1. Only fourth physically completed. No ignored constraint/fallback/extra feedback implemented; original fifth controller behavior remains preserved.
- 8,985 sparse samples, zero integrity/sampler errors; fourth insertion Y span 0.205 mm/yaw max 0.053 deg. Later actual material/mass unchanged. Python 19/19 plus standalone C++ policy PASS. MoveIt stop again -11, both owned runtimes stopped. Report/metadata/negative evidence uploaded; no benchmark freeze.

## 2026-10-03 — Cube04 first physical failure retained
- Actual first three settled, fourth normal-fed/dual-carried/staged/rear-regrasped/pushed. PRE_PUSH precision error 0.046 mm passes, but lateral drift produces final gap 1.827 mm, exceeding unchanged 1.5-mm gate; controller exit 1, no fifth command.
- 6,036 sparse PhysX samples, no integrity/readout errors; fourth helper CLOSED count inside carriage=0, no inner trim; peak raw joint torque 23.0 Nm. No force calibration claim.
- Exploratory controller was launched before final logging/nonfinite-guard rebuild completed; exact binary hash retained. Separate final-build clean-scene time_scale=5 repetition running. Avoid calling the exploratory binary the final delivery. No changes to scene/material/ACM, no silent online correction.

## 2026-10-03 — Cube04 precision insert implementation checkpoint
- Read all mandated task/source/benchmark records; issued pre-task report. User explicitly approves Cube04 contact-protocol adaptation.
- Added independent legacy ROS executable + compile-time policy, reused shared controller; fourth no longer plans/executes INNER_SIDE_TRIM, remains inner-neighbor accepted. PRE_PUSH uses previous pressed target 0.5 mm. Old nodes/scenes unchanged in behavior/geometry.
- New physical fixture initializes/settles first three only, logs sparse same-step PhysX positions and actual material/mass. First probe callback argument mistake retained, fixed via already validated post-step API. Compile/unit/syntax PASS; physical run preparing. Six records updated; no freeze/paper algorithms.

## 2026-10-03 — Further persistence / non-mutating contact alternative check
- User repeated “继续，直到task01调通，再汇报” and “继续”; no model/numeric approval was supplied. Tested a safe alternative before requesting a tool change: 24 discrete TCP rolls at the same Cube04 face-center/inward normal. All retain lateral-support/neighbor intersection; no command/IK/model change, no continuous-search impossibility claim.
- Added corresponding rod/roll regression (18 offline Python tests total). Preserved exact upstream patch context spaces using scoped .gitattributes instead of editing patch syntax.

## 2026-10-03 — TASK01 final evidence and mandatory review boundary
- Controlled default-zero task-thread hold completes normally: Cube01 / both HOME / exit 0. 34,510 recorded snapshots, zero integrity errors; 238 full-rate hold samples after first second. Mean force error 0.000370 N, instantaneous RMS 0.494278 N; mean moment residual 0.014902 Nm, tensor-vs-position-FD velocity max error 0.013163 m/s. Not force/internal-wrench calibration PASS. Repaired analyzer decimation aliasing, kept raw peaks and added regression; all 17 Python offline tests PASS.
- Existing xacro OBB audit: Cube04 face-center sidePose right has lateral/vertical support intersections with actual seated Cube03. Lateral minimum SAT axis overlap=33.524 mm, not PhysX penetration depth; no exhaustive arbitrary-roll claim or robot command. This is a protocol/geometry review blocker (BUG-009), not license to move cup to edge or ignore neighbor.
- Three startup mass/material audits retained, final reads actual backend Cube mass 0.800000012 kg and shape coefficients 0.5/0.5/0. Source material gets deleted in _build_objects after it was created. No silent restoration to 0.90/0.75; that would change physical comparison (BUG-012). First audit's incorrect tool path and intermediate partial binding checks explicitly retained.
- MoveIt teardown again -11; normal manipulation results not called clean-launch lifecycle PASS. All owned test processes stopped. Ordinary full-five and failed pause outcomes remain alongside new summaries and six records.
- GitHub records prepared on task01-benchmark-draft; legacy 76408c8 on task01-runtime-fixes already pushed. Scientific stop boundary: tool/contact/material review needed; 36 nulls unchanged and TASK02 still TODO.

## 2026-10-03 — TASK01 repaired full-flow outcome and load-check follow-up
- Normal fixed-feed inherited demo completes 5/5 physical batches with controller exit 0 and both arms HOME. No pre-placed fixture, physics/ACM/gate relaxation. Real final center errors 1.669/2.276/0.574/0.615/0.563 mm; final sample yaw maximum 0.741 deg. Controller fifth-Cube settle value 0.493 mm is a different sampling time.
- Full-stream integrity audit PASS: 70,434 snapshots, zero missed/nonmonotonic/nonfinite/mixed-step samples, dt=0.0166666675359 s. 5 analysis unit checks PASS.
- Read-only sampled contact-topology audit corroborates BUG-009: transport has opposed-side suction, but first-four rear+side simultaneous CLOSED is absent. No full D004 or paper success claim.
- Archived failed whole-process-pause metrology: suspending ROS executor expires current-state request; after resume controller opens both and returns 1. Does not invalidate ordinary five-Cube PASS. Replaced with opt-in task01_calibration_hold_sec in legacy 76408c8, default 0, main task thread only; normal ROS executor remains active. Build PASS (47.9 s). Supported SIGSTOP driver removed, exact initial variant retained in failed raw.
- Fresh controlled hold/load test is underway, with received phase observed alongside simulation step in opt-in measurement stream. No dynamic contact/internal-force calibration claim yet.
- Requested user model review for 1e6 suction break limits / retained 1.946277 kg branch; candidate YAML/hash/nulls unchanged. Six records and README/task report updated; TASK01 IN_PROGRESS / TASK02 TODO.

## 2026-10-03 — TASK01 runtime-repair checkpoint (execution ongoing)
- User requested continuing until TASK01 works, not another routine interim handoff. No numeric freeze or theory change was inferred.
- Fixed Task27 pre-close minimum-step overshoot with full measured residual correction capped at 1 mm and no minimum step. A seeded local FK/Jacobian micro-solver requires 5 um / 50 urad endpoint accuracy; joint bounds, seed neighborhood, full synchronized FCL, original 0.300 mm measured gate and three-attempt stop remain mandatory. This is [ENGINEERING], not a new paper planner. Task26 default path unchanged.
- Corrected scaled-USD quaternion extraction only in Task27; position/time lag remains separately open. Legacy fixes committed on task01-runtime-fixes at d80b6b6. Pure C++ regression PASS and ROS package build PASS (55.7 s); initial missing include-path build FAIL retained.
- Explicit official asset-root option bypasses failed S3 directory discovery, without substituting the FR3 asset. Real link8 incoming fixed-joint anchor/axes audit now succeeds on both arms.
- Fresh normal-feed five-Cube physical run ongoing: Cube01 legacy batch PASS; preclose asymmetry 0.447 -> 0.001 mm. Cube02 passes preclose at 0.287 mm, below unchanged 0.300 mm gate. Do not infer final 5/5 yet.
- Audit found an additional protocol gap: legacy helper parks during deep push, and inner cubes receive solo rear-suction lateral trim. A legacy full-flow PASS alone cannot validate the explicitly requested D004 rear-primary/side-constraint and role-swap fixture protocol. Geometry/gates remain unchanged; benchmark draft still has 36 nulls.

Append-only project work log.

## 2026-09-29 — Repository initialization
- Created V2 architecture for five-paper reproduction.
- Defined dual-platform strategy: MuJoCo for contact/force unit validation; Isaac/ROS2 for final benchmark.
- Defined mandatory traceability rules for Codex.
- Next task: TASK00 Environment Audit.

## 2026-09-30 — TASK00 environment audit started
- Cloned the repository and opened `task00-environment-audit` from `main`.
- Began read-only host, ROS 2, MoveIt, Isaac Sim, model and runtime-interface checks.
- No paper algorithm or benchmark geometry has been changed.

## 2026-09-30 — TASK00 environment audit completed
- Recorded host/GPU/ROS/MoveIt/OMPL/FCL/Isaac/MuJoCo versions and exact probe commands in reports/TASK00_ENVIRONMENT.md.
- Corrected the initial system-Python-only MuJoCo finding: MuJoCo 3.13.0 works in the existing isolated .venv; its minimal step was logged under results/.
- Expanded the legacy dual-FR3 URDF/SRDF, sampled live ROS interfaces while available, and marked unavailable or untested scientific interfaces explicitly.
- TASK00 PASS is an audit result, not a claim of benchmark readiness. TASK01 is READY but cannot be FROZEN before user review.

## 2026-09-30 — TASK01 benchmark candidate study started
- Compared the repository benchmark requirements with the existing Task27 Cube/side-suction/carriage geometry and control constants.
- Asked whether the frozen benchmark should use that validated scene as its geometric starting point or a separately designed scene.
- No benchmark values have been frozen; paper algorithms remain untouched.
- Added reports/TASK01_SOURCE_PARAMETER_MATRIX.md: source-grounded Task27 geometry/material/robot values, dimensional checks and explicit decisions still needed before any benchmark_v1 freeze.
- Isaac/MoveIt runtime had exited before TASK01 validation; no fresh physical benchmark was run.

## 2026-09-30 — TASK01 Task27-derived draft assembled
- Recorded user confirmation of Task27 as the geometric starting point in D003.
- Added `configs/benchmark/benchmark_v1.yaml` with source hashes, frames, dual-FR3/rail/L-tool geometry, cube/carriage coordinates, nominal side TCP transforms and explicit nulls for unapproved values.
- Added an analytic checker for internal dimension, handoff, wall-flush and nominal grasp consistency. It passed and enumerated 30 unresolved fields.
- No fresh Isaac simulation was run: no Isaac process was active during this iteration. TASK01 remains IN_PROGRESS; do not interpret the static pass as physics or paper-method validation.

## 2026-09-30 — TASK01 contact-protocol clarification
- Recorded the user's distinct Cube 01–04 dual-arm corrective push/press protocol and Cube 05 precision-staged single-arm insertion protocol in D004 and the draft YAML.
- Extended the static checker to verify four fixture targets and the required single-arm Cube 05 contact topology; it passed with 36 explicit unresolved fields.
- Calculated the nominal center-Cube geometric sensitivity: 1° yaw consumes about 1.038 mm of the 1.5-mm per-side clearance, leaving about 0.462 mm for lateral offset before any physical margin.
- No robot, Isaac or paper baseline was run. The draft remains IN_PROGRESS, not FROZEN.

## 2026-09-30 — TASK01 center-Cube left/right physical probe
- Added a separate Isaac probe wrapper that loads Task27, directly pre-places Cubes 01–04 into their intended cells and waits for real physics settle before permitting only batch 5 feed.
- Added a Task27 test parameter to choose left or right as the fifth Cube's -X-face pusher; its default remains the original right arm. Added a 100 nm float32 comparison epsilon to the inner fixture side-gap boundary (measured 38 nm rounding overshoot), without changing target cells or the millimeter-scale threshold.
- Built `fr3_dual_palletize`, then passed left and right MoveIt/FCL planning-only checks.
- Ran two clean headless Isaac 4.5 scenes, one per physical arm test. Both completed the fifth Cube and returned HOME. Right/left center errors were 0.603/0.669 mm; see `reports/TASK01_CENTER_ARM_SYMMETRY.md` for gap and torque details.
- This is [EXPERIMENTAL] evidence for single-Cube physical feasibility, not a full five-Cube benchmark run or paper-method result. TASK01 remains IN_PROGRESS.

## 2026-10-02 — TASK01 center-Cube exploratory repeatability
- Restarted the Isaac fixture scene and MoveIt independently for four more physical Cube 05 runs (right/left/right/left). With the two earlier runs, each pusher arm now has three completed runs, all with `Task27 batch 5 PASS` and both arms HOME.
- Right arm final center errors: 0.603, 0.429, 0.374 mm; left arm: 0.669, 0.408, 0.561 mm. This is only fixed-scene exploratory repeatability, not proof of statistical equivalence or a frozen benchmark. OMPL seed is not controlled.
- Added read-only final six-DoF Bridge pose sampling, a read-only PhysX/USD pose-source comparison in the headless runner, and a ROS-log parser that only calls a run PASS when the final Task27 PASS line exists.
- In the local Isaac 4.5 `python.sh` clean terminal, ROS Bridge needed explicit bundled Humble `LD_LIBRARY_PATH` and `RMW_IMPLEMENTATION`; the first failed Bridge startup sent no robot commands. Corrected reproduction command in the report.
- Observed motion-time PhysX/USD pose-source disagreement up to about 2.8 mm but zero positional difference after settle (printed precision). Reproduced post-task MoveIt Ctrl-C teardown segfault on each completed run. Recorded BUG-004/BUG-005; neither changed the task geometry or controller.

## 2026-10-03 — TASK01 physical pose/time channel diagnosis and calibration
- Isolated USD position frame-update lag from a separate scaled-transform quaternion extraction defect. At 0.2 m/s, callback position lag grew from 6.667 to 10.000 mm when application frames changed from 30 to 20 Hz; after app update positions match. Raw scaled USD rotation extraction had up to 27.464 deg error, versus 0.000154 deg after removing scale. Marked old Bridge yaw invalid for physical 6D claims without erasing the historical data.
- Added a separate opt-in read-only live-PhysX pose/velocity snapshot with simulation timestamp and step number, external ROS calibration/stream recorders, and a launcher that removes inherited system ROS Python/library paths. No Task27 scene/control source, benchmark value or paper algorithm changed.
- Kept failed attempts visible: mixed ROS type-support startup, a free-body angular expectation that omitted default damping, and an unsupported tuple argument to the five-body view. Corrected those causes without relaxing gates. Zero damping is authored only on the calibration fixture.
- External ROS known-motion calibration passed at 60 Hz physics with both 30/20 Hz app frames (120 motion samples each; maximum position error about 0.000313 mm, angle error about 0.000865 deg).
- One additional right-arm full Cube 05 physical probe passed, center error 0.520 mm, both arms HOME. Separate 250-s recorder received 14,295 contiguous snapshots without record errors. PhysX final yaw was 0.026334 deg while the old Bridge returned 0 deg. Report and complete commands: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md.
- Stopped the processes started by this iteration. MoveIt shutdown yielded SIGINT -2 rather than prior -11; BUG-004 remains open. TASK01 remains IN_PROGRESS with 36 unresolved fields; TASK02 and paper implementations remain untouched.
- Final code regression re-ran 30 Hz calibration with explicit position AND quaternion snapshot equality: all checks PASS. Empty-input recorder test saved FAIL and exited 1 as expected. Python compilation, shell syntax, draft analytic check (36 unresolved fields, unchanged SHA256) and diff checks passed; legacy tracked source remains unchanged.

## 2026-10-03 — TASK01 contact/mount force feasibility checkpoint
- Added a same-step collision sampler combining normal and friction impulses, contact locations and moments about an explicit body origin. Path ordering and shared contact/friction buffers are checked; 8 offline tests PASS.
- Known-load calibration at 60/120 Hz PASS: 0.8 kg support 7.848 N, horizontal friction -2 N, resisting moment about -0.04 Nm, rotated-wall 4 N direction. Dual suction holds the body while collision signal stays zero, confirming this channel does not measure D6 constraint loads.
- Independent mount reaction probes at 0/90 deg roll and nonzero COM/principal axes PASS; identified link-axis components/about-link-origin convention in this API. Actual FR3 gravity/inertia compensation has not been validated.
- Actual FR3 topology retains about 1.946277 kg in the link8/hidden hand/finger/hand_tcp branch. Do not silently delete mass or treat its roughly 19.093 N empty support as contact force.
- Retained startup failures: incorrect 4.5 PhysicsContext getter, SingleRigidPrim constructor keyword, nonexistent feed-state constant, and overwritten scene namespace. No failed startup sent robot commands. Fast-shutdown exit 0 is not a PASS criterion.
- Added full normal-feed five-Cube measurement runner without pre-placement. All five planning-only batches passed; physical execution is underway at this checkpoint. Benchmark YAML remains unchanged with 36 unresolved fields, TASK02 stays TODO.

## 2026-10-03 — TASK01 reference correction and final full-flow result
- Supersedes the checkpoint's reference-point conclusion: early COM fixtures had rigid-body scale, which also scaled authored COM/anchors. Preserve their software PASS but invalidate origin inference. Final unscaled fixture verifies actual COM=5 mm and tests nine axes/point hypotheses; only incoming joint axes/about joint anchor matches (3.436e-6 N / 4.430e-7 Nm error). Final code regression repeats this result.
- Collision calibration remains PASS (13 checks each at 60/120 Hz); 8 offline tests, final Python compilation, analytic draft and diff checks PASS. Benchmark hash unchanged with 36 nulls.
- Normal five-batch preflight PASS, but actual run placed only Cube 01 then safely failed Cube 02 before suction: asymmetry 0.968 -> 0.315 -> 0.339 mm against 0.300 mm gate, with mandatory 0.650 mm minimum correction (BUG-008). PhysX final asymmetry 0.338941 mm independently confirms. No later physical task was advanced.
- 37,236 same-step snapshots, zero measurement errors; not full task PASS. Cube 01 PhysX yaw -1.095465 deg contradicts legacy scaled-USD near-zero yaw (BUG-006). Deep-wall collision peak 139.098 N is not suction/internal force or an approved gate.
- Own full-run processes stopped. MoveIt teardown -11 recurred (BUG-004). Final added authored FR3 joint-frame audit failed on remote asset-root lookup before control commands; new audit remains unverified.
- Reports distinguish force calibration, failed full flow and 36-field freeze review. Metadata retains negative starts and invalidated fixtures; heavy raw remains local/ignored. No legacy tracked model/control or protected-directory change.
- TASK01 IN_PROGRESS, TASK02 TODO. Next scoped correction fix must retain gates, followed by normal five-Cube re-run and remaining model/frame/numeric review; no paper force controller yet.


## 2026-10-06 — TASK01 research reset approved
- Reviewed current GitHub progress after extensive five-Cube Task27 debugging.
- Identified task-scope overload: multi-Cube sequencing, empty retreat, tool-neighbor interference, material mismatch, wrench calibration and timing work had all accumulated inside benchmark freeze.
- Re-scoped benchmark_v1 to one shared Cube + dual FR3 + one carriage.
- Preserved all legacy five-Cube evidence without making it a freeze gate.
- Deferred Isaac force/wrench calibration to TASK10-IS before P2 Isaac migration.
- Next action: single-Cube geometric feasibility probe, then deterministic Isaac READY/reset, then user freeze review.
