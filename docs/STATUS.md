# STATUS

## 2026-10-06 — Research reset: TASK01 narrowed to one-Cube core benchmark

User approved a plan correction after review of the overloaded five-Cube Task27-derived TASK01. The common SCI benchmark is now **one shared Cube + dual FR3 + one carriage**. Historical five-Cube debugging remains preserved under legacy/stress-test scope and no longer blocks benchmark freeze.

Current gate:
1. stop five-Cube execution/debugging for TASK01;
2. perform the single-Cube geometry-feasibility probe;
3. create/reuse deterministic one-Cube Isaac READY/reset;
4. freeze geometry/material/time/start-goal values after user review;
5. proceed to TASK02, then P4.

Force/TCP-wrench calibration is explicitly deferred to TASK10-IS before P2 Isaac migration. P4 must not be blocked on force sensing.

| Task | Status | Notes |
|---|---|---|
| TASK00 Environment Audit | PASS | retained |
| TASK01 Core Single-Cube Benchmark Freeze | IN_PROGRESS | **new scope; five-Cube flow non-blocking** |
| TASK02 Common Interfaces / Logger / Metrics | TODO | after TASK01 freeze |
| TASK03–06 P4 | TODO | may start after TASK02; no wrench dependency |
| TASK07–09 P2 MuJoCo | TODO | force/control math |
| TASK10-IS Force/Wrench Calibration + P2 Migration | TODO | owns Isaac wrench calibration |

---

## 历史记录：2026-10-06 GUI physclock final — 单独改时基仍未通过接近

新run实际侧下降left86.670Nm>80、tracking5.429deg、Cube接触217.404N，controller1/完成0，无X/Y；pause/GUI0，1904held/11098atomic/1849sparse完整性0错。早20s反馈接收PhysX/wall1.000084不证明contact窗口实时；时基适配不自动解决物理问题。查本机Humble Cartesian srv不带v/a缩放，只给Task01侧CONTACT补现有0.12/IPTP同q计时后再fresh GUI实测，原物理/模型/门限不动。以下旧五块实验不再作为新单 Cube 基准的冻结门槛。

## 2026-10-06 GUI physclock running — 修复候选已编译并开始实测

runtime6fa161e/binary75f798a1、串行build58.5s/63Python/两C++通过。正常倍率改为同一原子PhysX秒，无wall fallback/原250ms和80Nm门禁。fresh可见GUI完整画面/first feed READY确认后first1/max1/scale1已运动；仅软件PASS，实际结果待定。原scene/Bridge/YAML hash完全不变，TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。

## 2026-10-06 GUI result — 首件真实下降碰Cube，保护停止

run02可见GUI/1.0现实墙钟回放，CONTACT侧臂跟踪10.109deg、Cube-left link8真实468.823N、leftJ2 raw86.323Nm，原80Nm止动，controller1/完成0/X-Y未开始。安全双OPEN后pause并受控GUI0，6158held/26516atomic/4419sparse完整性0错。不是已证实的闭合超时，GUI实时倍率/构型因果未隔离。准备仅Task01改用原子PhysX秒推进（不改物理/路径/门限），详细日志补入approach interlock；首编译重名失败保留，修正后build02进行中。TASK01仍IN_PROGRESS/36nulls，TASK02 TODO。

## 2026-10-06 GUI running — 可见场景已确认，正常倍率首件实测

新的可见SimulationApp入口headless=False显示双FR3/L工具/原三墙/供料Cube（截图实际确认）；原Bridge和同一步反馈/真实first feed READY后启动runtime6bc24ec/binary08f3060a、first1/max1/scale1，无预置。63Python通过，物理结果待定，之后才决定五件测试。首个官方GUI空网格/渲染诊断后native139负启动保留、机器人命令0，不算速度测试失败。仅GUI灯光/相机/本机executor适配，原场景/物理/ACM/门限/36nulls不变。TASK01 IN_PROGRESS，TASK02 TODO。[GUI报告](../reports/TASK01_VISIBLE_GUI_RUN.md)。

## 2026-10-06 latest — 用户要求正常播放倍率与GUI-only

此前实际`execution_time_scale=5.0`是20%规划轨迹播放，不是50%；新Task01独立节点默认改为`1.0`（100%规划轨迹倍率），保留MoveIt RRT速度/加速度12%及原碰撞/接触保护。以后助手不再启动headless，只用可见GUI；历史脚本/无界面记录保留。新倍率尚未完成GUI物理验收，不等于100%关节极限速度，也不能借旧scale5结果称通过。

上一轮`empty_handoff_full01`已经停止：首件X1–15完成，X16原子反馈STALE_OR_INVALID、安全双OPEN/controller1/完成0，自有Isaac正常停止0。17几何精确stamp匹配，5862held/21398atomic/3566sparse完整性0错；空载修复未物理触发。原因未隔离，不放宽250ms门禁。TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。详见[运行约定](../reports/TASK01_GUI_SPEED.md)。下方RUNNING是保留历史检查点。

## 2026-10-06 running — 空载重放通过，新fresh五件实际回归

runtimef237cff/binary812c71ee，串行构建56.2s；同commit探针a33c7565/build59.5s，精确第三释放后14q/三Cube输入一致、两段fullFCL491/469样本、安全pair/CLOSED和碰撞起点拒绝/remote world不变均PASS。局部原OMPL RRTConnect加密检查0.0005，IPTP逐值保持q路点；全局MoveIt/加载链/原模型物理ACM门限不变，不启动后台沙箱。六条same-raw对照raw/TOTG/IPTP都安全，不能归因TOTG唯一故障。61Python/两C++/analytic36nulls通过。fresh empty_handoff_full01实际运动正在启动，零预置first1/max5/scale5、READY+hash守卫；完整物理结果待定，不称5/5。TASK02TODO。

## 2026-10-06 final — full02前三实际放置完成，第三空载转场FAIL

source a3fceab/binary57e72f83，前三各X16/Y16双CLOSED、无释放主从换角与释放全部完成；batch完成计数仍[1,2]，第三26.9mm短清障后最短RRT在0.610s碰left suction↔Cube03（FCL0.329mm），拒绝执行/controller1/第四第五无命令/headless0。三件短退出center0.302/0.407/1.343mm，deep0.156/0.091/0.087mm，侧/邻缝0.259/0.397/0.160mm。105精确stamp匹配、36469held/51175atomic/8529sparse均0完整性错；CONTACT/X/Y窗口无机器人-墙非零pair，不推广到COMPLETE/全流程。下一步空载候选池/同一RobotState/request-local场景诊断，保持原模型/物理/ACM/门限/36nulls，TASK02TODO。

## 2026-10-06 running — final binary full02前两件实际PASS

57e72f83/source a3fceab，batch1/2新双吸协议X16/Y16、无释放主从互换/双OPEN/短清障RRT转场均完成，无批间HOME。短退出后center0.302/0.407mm，deep0.156/0.091mm，side0.259/0.397mm。第三正在抓取搬运，还未到上轮失败side HIGH，不称BUG021已物理修复或全五件PASS；原保护/模型/物理/36nulls保留，TASK02TODO。

## 2026-10-06 running — full02最终二进制已实际进入首件运动

串行强制重建production SHA57e72f83含正确root-arm参数筛选，源码a3fceab；fresh原场景自动READY后hash守卫再启动，模型/IK初始化与首件HIGH/CONTACT候选预检已实际通过、机器人开始执行。full01旧binary无命令失败保留且源码等价声明已纠正。full02零预置first1/max5/scale5，最终完成/几何审计待定，不能称5/5或稳定版。TASK01 IN_PROGRESS/36nulls/TASK02TODO。

## 2026-10-06 — coupled full01启动失败，无机器人测试

controller1/命令0，生产二进制仍旧参数筛选；已查明编译过程中include被修改、link晚于修改使后续增量no-op。前述a3fceab/174d6ef7一致性断言作废；成功probe不受影响。headless自动first feed后空闲达到3600s，正常退出0，35998sparse/215989atomic0錯。现串行强制重编译、验证binary，再fresh full02，不复用旧运行为物理PASS。TASK01仍IN_PROGRESS/36nulls/TASK02TODO。

## 2026-10-06 running — 联合rear候选软件通过，fresh完整五件回归

runtime a3fceab /controller174d6ef7：原blocked rear被联合gate拒绝；3个替代构型连续CONTACT/X约330mm/Y1mm/短退出FCL与相对TCP预检通过，尚未物理执行。实际MoveIt LMA插件参数布局适配后probe0，61Python/两组C++ PASS（临时目录首轮harness失败保留）；原场景/桥/物理/ACM/门限未改。新fresh coupled_rear_full01零预置first1/max5/scale5启动，物理结果待定；TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。

## 2026-10-06 — 第三件固定rear碰撞证据与联合候选筛选准备

只读精确held快照重放：固定rear时60/60 side HIGH解碰left suction↔right link5；相同rear TCP的替代构型在7个有效rear IK中找到3个HIGH/CONTACT全FCL自由组合。endpoint-only/probe0，不是物理或RRT连接PASS。runtime ebddf6d；本轮仅新前三rear候选加入HIGH/连续下降/共同X/Y/短退出预检，编译与实测待验。full01最终2/5失败已完整归档，第四第五无命令；TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。

## 2026-10-06 latest — 五件回归完成2/5，第三侧臂高位目标采样失败

full01同binary，batch1/2真实双吸附X16/Y16/短清障RRT转场通过（center0.269/0.470mm）。前三rear OPEN XYZ最终norm0.047/0.006/0.002mm；第三DUAL_SIDE_HIGH连续8次无合法goal sample/controller1安全双OPEN，第四第五未命令。70精确stamp几何匹配，37804held/53398atomic/8899sparse0完整性错，持件窗口robot-wall非零pair0；headless0。不是五件PASS，也不是Y80Nm失败。

仅无命令probe扩展实测rear固定的side IK/FCL碰撞对诊断，不改场景/物理/ACM/门限；读图/编译/真实模型重放待完成。TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。

## 2026-10-06 running — 新3+2五件零预置回归

同runtime39f1a0c/binaryefb1d133，full01已完成batch1（center0.269/deep0.099/side0.250mm）与短清障RRT到下一件的转场，无批间HOME。第二件后杯OPEN两次精调norm1.866→0.870→0.006mm，双吸附X推进中；其余未验收，完整/记录完整性结果待定。原模型/物理/保护门限不改，TASK01 IN_PROGRESS/TASK02 TODO。

## 2026-10-06 latest — 新rear OPEN精调首件物理PASS，五件连续回归准备

rear_open_xyz_cube01 /39f1a0c/binaryefb1d133：rear norm2.196→1.201→0.205mm，两次OPEN修正后实际X16/Y16/主从换角/双OPEN退出/HOME全部完成，controller0；中心0.303/deep0.212/side0.216mm。35精确stamp几何匹配、8470held0完整性错/窗口内无非零机器人-墙接触，26166atomic/4361sparse0错。

这是first1/max1/scale5/零预置的单次headless PASS，不是五件/GUI/稳定或科学冻结。自有运行已停，Isaac0、MoveIt清理-11/joint bridge1保留。下一轮同源码fresh完整3+2五件准备；TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO，原场景/物理/ACM/门限不变。

## 2026-10-06 latest — 后腕实际首件X1失败；吸附前XYZ复用精调已编译

rear_roll_cube01 /4ebe279：原子反馈精确匹配3条几何，X1 rear Z偏差2.578mm超过原2.5mm，controller1/完成0/双OPEN/headless0；未到墙或Y，不称腕姿物理修复。35922原子快照/4552held/5987稀疏记录均0完整性错。

独立前三后杯OPEN重抓后复用1mm向量限步/FK微解算，最多3修正/4检查、吸附前工程目标0.3mm，原加载门限不变。runtime39f1a0c/build50.4s/61Python与两组C++/analytic36nulls通过；首编译API签名错误已修正并保留，不是物理PASS。fresh首件原场景复测准备，后两/旧节点/物理/ACM不改，TASK01 IN_PROGRESS，TASK02 TODO。

## 2026-10-06 latest — 双腕三墙名义检查通过，后腕OPEN姿态复测准备

rear_roll_nominal01 /39d72c6，side-15/rear镜像45：前三名义链3/3 IK/FCL/相对TCP通过，1330双腕节点对原三墙均0凸包交集。旧SciPy1.8默认LP两次status4保留；同约束内点LP/显式解残差复核通过。61Python/C++PASS，不是实际物理成功。

执行器仅前三后杯OPEN-RRT重抓接入同一腕姿，后两单rear保持原姿态；fresh首件物理验证准备。上轮X16/Y14/Y15力矩保护与侧墙接触仍保留。TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO；原场景/模型/物理/门限无更改。

## 2026-10-06 latest — 原子反馈实测匹配；Y15后腕碰侧墙仍FAIL

atomic_feedback_cube01：33条geometry打印与同一步PhysX精确stamp匹配，X16/Y14完成；Y15原80Nm guard left86.999/right70.170、feedback FRESH，实际right link7↔+Y墙峰745.808N。controller1/完成0/双OPEN，headless0；25171反馈无错、9491held/4195sparse完整性无错。

旧名义1330双腕节点补三墙复核：deep0/minusY0/plusY7节点重叠，不能用deep-only检查称全墙安全。新readonly后腕worldX法向翻转向中央候选检查中，执行器未启用；60Python/C++PASS。Task01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO；原场景/桥/模型/物理/门限不变。报告TASK01_ATOMIC_FIXTURE_FEEDBACK。

## 2026-10-06 latest — 新腕姿X3被旧反馈guard拒绝，原子观测修复中

cup_roll_cube01 / dd63c74 实际首件X1/X2接受，X3 rear=-1.784mm判失败/controller1/完成0/双OPEN；末同一步PhysX rear=+1.065mm，4738 held与4085稀疏样本0完整性错误。未到深墙/Y，腕姿不是物理PASS。旧USD滞后已校准、三个latest独立消费仍存在。

新独立PhysX单消息Cube+双TCP适配器与严格buffer正在编译/实测准备，56Python/C++策略PASS；无原门限/场景/桥/模型/ACM改变，无旧数据fallback。报告TASK01_ATOMIC_FIXTURE_FEEDBACK。TASK01 IN_PROGRESS/DRAFT/36nulls；TASK02 TODO。

## 2026-10-06 latest — 实测腕部碰深墙；杯面内转角候选只读通过

diagnostic02 本机headless首件实际 X16/Y14，Y15原80Nm保护自动停止（left86.958/right52.123Nm）/controller1/整件完成0，双OPEN后自有headless正常停机。10,538同一步held记录/0完整性错误；left link7深墙接触从X16有非零力，峰值309.658N，Y15同一步140.242N/leftJ2 raw86.997Nm。不是D6/TCP力估计。

精确实测14关节只读FK与物理腕部差<0.001mm，MoveIt该步墙FCL无碰撞；原NVIDIA link7 mesh(convexHull)与本机URDF STL不同。新鲜官方资产与旧cache SHA一致，未换模型。原mesh离线凸包复核实测X16/Y15有体积交集，不能把LP球半径当penetration depth。BUG017/新BUG019仍OPEN。

只读绕杯面法向worldY -15deg候选前三链3/3 IK/FCL/relativeTCP通过；nominal02独立导出1330腕部节点，原USD凸包对深墙0重叠，最小X平面余量6.766mm，仍非物理PASS。nominal01日志穿插导致分析安全拒绝，保留负结果。53Python/探针build PASS，执行控制器尚未使用新转角。TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。

## 2026-10-06 follow-up — 网络恢复，原场景第二次启动

原S3直连/代理HEAD恢复HTTP200，runtime d35cc0c正常push成功；保留startup01失败。相同官方资产/原参数的startup02重新运行，held live handles与首件物理诊断仍待验证，尚未发controller命令。BUG017根因未解决，BUG018外部连接暂时恢复不抹掉负结果；模型/物理/门限/YAML不变。本段更新此前“final”失败checkpoint，不叫新物理PASS。

## 2026-10-06 final — 44软件测试/编译通过，资产连接阻塞物理诊断

新持件采样与分析器完成，44Python/build103s PASS；本机headless启动在原_asset_url报“找不到官方FR3 USD”，尚未完成真实句柄/采样验证，机器人命令0。官方S3直连/本地代理curl均SSL EOF，GitHub SSH banner超时；缓存映射SDK返回ERROR_CONNECTION，未替换资产。原Y15根因仍OPEN。自有仿真/MoveIt停止，teardown-11独立保存。TASK01 IN_PROGRESS/36nulls/TASK02 TODO；新记录先本地提交，push结果另记。

## 2026-10-06 — TASK01 BUG-017同物理步诊断扩展

新增可选持件窗口Cube/工具/全机器人contact与DOF记录；新节点仅加异步phase标签，39离线测试/build PASS。本机headless真实句柄启动检查中，无新物理PASS。原模型/物理/门限/YAML不变，TASK01 IN_PROGRESS/36nulls，TASK02 TODO。报告TASK01_HELD_CONTACT_DIAGNOSTIC。

## 2026-10-05 final — 新3+2协议 PARTIAL，首件Y第15段力矩保护停止

实测换角色版 `e0477ab` 在新鲜原场景中完成 X16/16、Y14/16，全部完成片段双杯CLOSED。Y15原始关节effort峰值 left86.975/right32.984Nm，超过保留的80Nm门限，controller1/completed=[]；安全双OPEN，未推进Cube02–05。首件未完整通过，不能交付为新五件验收版。

释放后静态实测姿态只读联合FCL通过，不是触发瞬间FCL证据。最后稀疏双CLOSED样本Y=0.225646m，距+Y目标0.243m仍17.354mm，不能直接归因为最终侧墙压紧。9432条稀疏PhysX样本/0完整性错误；持件推压阶段缺少全速接触/关节联合记录，根因OPEN。35 Python/编译PASS；自有Isaac/MoveIt已停止，关闭时MoveIt-11独立保留。

报告 `reports/TASK01_DUAL_SUCTION_FIXTURE.md`。原场景/工具/物理/ACM/门限/YAML不变，旧5/5不算新协议通过。TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。下一步需同物理步持件接触与关节诊断，不能以提高门限、改变场景或恢复单臂推入替代。

## 2026-10-05 follow-up — 首件X双吸推入通过，Y互锁失败；实测换角复测中

`dual_fixture_cube01`/ff20ac3 controller1/completed=[]；16/16 X片段双CLOSED，deep gap0.286mm，随后Y起步active interlock停止/双OPEN，不是首件完整PASS。4747稀疏PhysX样本/0完整性错误；Cube02–05未推进。旧guard没具体原因，暂不能断言是力矩/吸附/物理不可行。

发现X末tracking残差0.551deg，e0477ab新增从双臂实测/新Cube GT重新规划Y与current-start FCL、详细互锁诊断；新鲜原场景首件复测中，尚无新版PASS。35 Python /4 C++ /build PASS。源码/负证据与后续计划持续上传，报告TASK01_DUAL_SUCTION_FIXTURE。TASK01 IN_PROGRESS /36nulls/TASK02 TODO；原场景/物理/ACM/门限/YAML不变。

## 2026-10-05 — 新3+2接触协议已搭建，首块物理验证运行中

用户批准前三件双吸附主从推压、后两精准单rear插入。独立运行节点 `task01_dual_suction_fixture` / runtime `ff20ac3` 编译通过；34个Python测试、4个C++策略测试通过。新无执行探针前三件名义接触/X推入/Y压紧/局部释放退出通过联合FR3 FCL和相对TCP检查（最大轴向变化约0.002mm）；早期探针负结果保留。

新鲜原场景首件试验 `results/20261005_TASK01_dual_fixture_cube01/` 已启动（first1/max1/scale5/hold0/无预置），目前没有新物理PASS。旧节点df9c2c0的一次5/5仍有效但不证明新协议。原场景/教师认可L工具/物理/ACM/门限及YAML不变；TASK01 IN_PROGRESS / DRAFT /36nulls，TASK02 TODO。报告：`reports/TASK01_DUAL_SUCTION_FIXTURE.md`。下方“final”为保留历史结果。

## 2026-10-04 final — 普通供料五件物理回归 5/5 PASS，基准仍未冻结

本机 Isaac 4.5 **headless**、零预置、普通释放 hold=0 的 `empty_rrt_full_01` 完成 batch 1–5，控制器 exit=0，双臂最终 HOME / 双杯 OPEN。运行源码 `df9c2c0`，二进制 `c760d506…`。五件中心误差分别 1.983 / 0.807 / 0.723 / 1.319 / 0.481 mm；第四邻块缝隙 0.347 mm，第五两侧缝隙 1.987 / 1.473 mm。18,498 条稀疏 PhysX 记录，完整性错误 0；3,212 条释放诊断记录。

这是一轮实际完整执行，不是 GUI 验收、长期稳定性或论文复现证明。普通 Cartesian 空载退出本轮都成功，新增有限 RRT 备用**没有物理触发**；备用仅有失败姿态四位小数重放 / 1,277 次联合 FCL 的无机器人命令验证。BUG-016 历史 Cube02 释放回带本次未复现，原因仍 OPEN；已有对象严格恢复比较问题仍未隔离。所有自有运行进程已停止，MoveIt 关闭时 -11 / joint bridge 1 与控制器 0 分开记录。

最新报告：`reports/TASK01_RELEASE_CLEARANCE.md`。原场景、材质、质量、ACM、验收门限及 YAML 未改变。TASK01 保持 IN_PROGRESS / DRAFT / 36 nulls；TASK02 TODO。下方 running / failure 项均为保留的历史 checkpoint，本段为最新结果。

## 2026-10-04 — Empty RRT no-command replay PASS; clean physics regression running

Runtime df9c2c0 built55.8s; binaryc760d506...; correctedrailshift0.1m failedCube02rounded-seedreplay02exit0/fullFCL1277samples, CLOSED/obstructedstartreject and absent-IDsyncsceneundoPASS. Replay01negativepreserved; existing-objectstrictcomparisonproblemnotclaimedresolved. No Arm/joint/suctioncommandsinprobe. New ordinary0preplacedfirst1/max5/scale5/hold0 localheadlessrunempty_rrt_full_01 started, nofinalphysicsPASSyet. Sourcepushed, TASK01IN_PROGRESS/36nulls/TASK02TODO; BUG016remainsOPEN.

## 2026-10-04 — Ordinary second-Cube retreat rejected; bounded empty RRT preparing

Ordinary measured_side_full_01 controllerexit1/completed[1], Cube01cell0.678/deep0.670/side0.108mm. Cube02dropped/bothOPEN, measured-commanddelta0.000681/0.000995rad, CartesianFK752–967mm rejected; continuousIKfails118/151. EarlierCube02retreatPASSuseddifferentredundantconfiguration; notblanketlogicregression/rootcauseproof. Headlesslocalteststoppedaftercontrollerabort,17319sparseposes0errors. AddedunbuiltOPEN-onlyRRTbackupwithsameactualstart/originalgoal/fullreleasedCubeFCL, ≤3plans/arm; numeric/bounds/adapterstart/goalchecksandverifiedscenecleanup. Pendingreal-model/physicsvalidation, BUG016stillOPEN. No model/physics/ACM/gate/YAMLchange,TASK01IN_PROGRESS/36nulls,TASK02TODO.

## 2026-10-04 — Diagnostic stopped safely; measured side start built

Diagnostic02 exit1/completed[1]; Cube02 before release side-approach t0 commanded-seed/currentCube collision0.783mm, deepseat1.804mm. Firstcubeholdstable notsecondcubeproof. Preserved13227poses/0errors/1617contacts, stoppedallownedprocesses/teardown-11. Independent actual side start nowusesone measuredRobotState, CLOSEDpusher/OPENhelper, existingjointdelta/bounds, strictcurrentCubeFCL. Runtime2fbfa0b/build+policyPASS/Python28PASS. Norelease-control/rootcause claim yet; cleanordinaryhold0/fullfive preparing. ReportTASK01_RELEASE_CLEARANCE, TASK01IN_PROGRESS/36nulls/TASK02TODO.

## 2026-10-04 — Diagnostic physical checkpoint, not a control fix

Runtime b259366 buildPASS56.5s, diagnostic02 physically running with3s hold after OPEN. Cube01 release-hold deltaX0.028mm and clearance deltaX0.000mm, hence first object does not reproduce previous Cube02 failure. Cube02 underway. Initial diagnostic01 startupBRANCH_SIGN ordering failure archived (processclose returned0 despite failure.json); no controller was started then. Logger uses bridge namespace for signs, not scene edit. Python28/28PASS including peak/mixed-step guards. Stop diagnostic after second completed batch before later object control; no normal-flow or reliability claim. Prior full-flowFAIL retained, no active release-motion repair yet.

## 2026-10-04 — Release-window diagnostic underway

User approved continuing BUG-016 repair. Added independent-variant release/clearance stage topic and optional3s post-release main-thread diagnostic hold (ordinarydefault0), plus read-only same-physics-step tools/collision logger active only inside release window. Software25testsPASS, build/physics pending. No scene/model/material/gripper/ACM/gate or active release-control fix yet. Report TASK01_RELEASE_CLEARANCE. TASK01 IN_PROGRESS/36nulls,TASK02TODO; priorXYZPASS/full-flowFAIL preserved.

## 2026-10-04 final — XYZ pre-close verified, full flow still FAIL

User-approved independent XYZ extension compiled, C++/22 Python/real RobotModel XYZ+FCL PASS. Normal-feed run: Cube01 batchPASS; Cube02 physically corrects X2.012→0.606mm/Z1.589→0.451mm/gapdelta0.879→0.275mm within original gates, then grasps/transports/pushes. But after side pressing and rear release, deep gap grows0.488→5.138mm > original3mm, exit1/completed1of5; Cube03–05notadvanced. Two XYZ moves total1mm cap, planning0.078621s/execution7.569621s atscale5. 7680valid sparse PhysX poses/0errors; static FK–Isaac difference norm max0.056mm, no hard dynamic timing proof. All owned processes stopped, teardown-11 repeats. Runtime f0812a4; full report `reports/TASK01_PRECLOSE_XYZ.md`, BUG-016 release-window diagnosis needs next-scope review. No scene/model/physics/ACM/gate/loaded-control/YAML changes; TASK01 IN_PROGRESS,36nulls,TASK02TODO. GitHub transport recovered with command-local existing HTTP CONNECT proxy, no system config edits.

## 2026-10-03 latest — Normal-feed current variant FAIL, stopped for review

Full five-object attempt (no preplacement), same tested binary/model/gates: controller exit1, only Cube01 actual PASS. Cube02 pre-close Y gap asymmetry corrects2.230→0.427→0.001mm, but X TCP mismatch3.150mm exceeds original2.500mm alignment gate; suction never enabled, Cube03–05 not advanced. 7214 sparse PhysX samples/0errors. No controller/model/physics/gate change; all owned test processes stopped, MoveItteardown-11 repeats. Report `reports/TASK01_PRECISION_FULL_FIVE_REGRESSION.md`. Prior partial/legacy PASS evidence retained; current variant is not full-flow stable. Next discuss XYZ execution residual diagnosis/correction scope plus pending model/contact/36numeric review; TASK01 IN_PROGRESS, TASK02 TODO.

## 2026-10-03 — Current variant full normal-feed regression preparing

Adding only zero-preplaced test mode and read-only summaries, then actual first_batch=1/max_batches=5 using unchanged current binary/model/physics/gates. Previous isolated fifth and fourth→fifth PASS remain scoped results. Full-flow result pending; no paper method or benchmark freeze. Report: `reports/TASK01_PRECISION_FULL_FIVE_REGRESSION.md`. Stop for user decision if model/contact/physics/gate changes become necessary; TASK02 TODO.

## 2026-10-03 final — empty-retreat engineering PASS, benchmark review pending

Final report: `reports/TASK01_EMPTY_RETREAT_REPAIR.md`. Real-model FK/FCL basic and long replay PASS; isolated Cube05 physical exit0; clean actual Cube04→Cube05 continuous physical exit0. Fourth neighbor gap0.375mm/deepgap0.244mm; fifth center error0.530mm/deepgap0.476mm. Released Cube included in actual retreat FCL; fallback not physically triggered. 7778+4691 sparse valid samples; no full-five-new-variant/reliability claim. All owned runtimes stopped; MoveIt teardown-11 remains. Code/results pushed. TASK01 IN_PROGRESS with36nulls; model/material/D004/freeze decisions remain for user review; TASK02 TODO.

## 2026-10-03 latest — empty retreat engineering repair, tests pending

New precision-variant empty retreat uses measured joint seed and bounded continuous-seed fallback, with released Cube included in strict FCL. Build + policy +19 Python tests PASS; real RobotModel / physical verification next. No scene/model/material/ACM/gate change. Report: `reports/TASK01_EMPTY_RETREAT_REPAIR.md`. TASK01 IN_PROGRESS, TASK02 TODO; 36 nulls unchanged.

Latest follow-up: real RobotModel basic/long replay PASS; isolated actual Cube05 exit0/batch5 PASS, placement0.540mm/deepgap0.514mm; ordinary measured-start retreat/FCL passes, fallback not triggered physically. New clean Cube04→05 run starting. No stable/full-five claim; MoveIt teardown -11 remains.

Last update: 2026-10-05

## Latest Cube04 variant handoff — PARTIAL, physical tests stopped

Independent `task01_cube04_precision_insert` implemented/pushed (legacy `7be3659`). Final-binary slow trial passes actual Cube04, final neighbor gap 0.227 mm / deep gap 0.413 mm, no side trim/helper side suction. Subsequent Cube05 transport/drop succeeds but empty Cartesian retreat rejected at up to 450.1-mm FK deviation; controller safely exits 1, only batch4 PASS. First faster trial failed Cube04 neighbor gate. No stable/full-five claim. 19 Python + standalone C++ policy tests PASS. All owned test processes stopped; MoveIt teardown -11 persists. Six records/results/report updated. TASK01 IN_PROGRESS; TASK02 TODO.

## Cube04 final-binary slow trial — fourth passed, fifth running

Clean time_scale=5 trial passes Cube04 original final gates: neighbor 0.227 mm, deep-wall 0.413 mm, precise staging Y error 0.040 mm. No inner trim/helper side suction; short-clearance/RRT handoff to Cube05 completes (batch4 PASS). Cube05 actual transport/insert now running. Previous time_scale=3 trial failed; do not infer stable repeatability or causal speed-only fix.

## Cube04 physical negative checkpoint

First time_scale=3 exploratory trial: precise pre-staging 0.046 mm, but final neighbor gap 1.827 mm > original 1.5 mm, safe stop; Cube05 not executed. No inner trim or helper-side suction. Final built binary now repeating from clean physics at time_scale=5; no feedback/force controller added. New failure preserved, TASK01 not passed.

## 2026-10-03 Cube04 protocol adaptation — running

User explicitly approved Cube04 adopting Cube05 precise-stage/single-rear-suction insertion. New independent executable/build/unit checks pass; Cube04/05 physical probe now running with first three pre-placed/settled. Original scenes/materials/ACM/final gates preserved. Control PRE_PUSH Y changes to the existing 0.5-mm pressed target; benchmark YAML unchanged. Report: `reports/TASK01_CUBE04_PRECISION_INSERT.md`. TASK01 remains IN_PROGRESS, TASK02 TODO.

## Project state
Repository initialized. No baseline implementation has started.

| Task | Status | Notes |
|---|---|---|
| TASK00 Environment Audit | PASS | Report: reports/TASK00_ENVIRONMENT.md; external integration gaps identified |
| TASK01 Benchmark Freeze | IN_PROGRESS | New user-approved3+2 protocol PARTIAL: Cube01 X16/Y14 dualCLOSED, Y15 raw effort86.975Nm>80 guard; completed0. Old df9c2c0 physical5/5 retained as different protocol, not freeze/reliability. BUG017/016, force/time/model/36nulls/teardown pending. Latest report TASK01_DUAL_SUCTION_FIXTURE |
| TASK02 Common Interfaces / Logger / Metrics | TODO | Depends on TASK01 |
| TASK03–06 P4 | TODO | |
| TASK07–10 P2 | TODO | |
| TASK11–15 P3 | TODO | |
| TASK16–19 P5 | TODO | |
| TASK20–26 P1 | TODO | |
| TASK27–30 Evaluation/Freeze | TODO | |
| TASK31 Ours v0 | TODO | Must wait for TASK30 |

## Current gate
**Do not implement paper algorithms yet. Draft and review TASK01 benchmark_v1 first.**

## 2026-10-03 final evidence / review stop

Latest report: `reports/TASK01_RUNTIME_REVIEW_20261003.md`. Actual five-Cube ordinary manipulation works; the additional opt-in hold also resumes and places Cube01 with exit 0. Full-rate static diagnostics expose alternating reaction and tensor/pose finite-difference velocity disagreement; no instantaneous force/internal-wrench PASS. OBB audit proves current Cube04 centered helper tool intersects Cube03. Actual material audit exposes 0.5/0.5 coefficients rather than 0.90/0.75. These need explicit model/contact direction, not silent changes under a persistence request. No YAML/null/hash change, paper implementation or frozen benchmark claim. Six records updated, all owned simulators/controllers stopped; MoveIt teardown still -11.

Further continuation: 24 fixed-center/inward-normal TCP rolls all retain lateral-support/Cube03 intersection. No box-clear rotation-only candidate found, no commands. Final offline Python regression 18/18 PASS; protocol/model review still required.

## 2026-10-03 runtime-repair checkpoint

Bounded fine pre-close correction and Task27 quaternion fix are implemented in legacy branch `task01-runtime-fixes` (`d80b6b6`); unit/build PASS. Fresh normal five-Cube physical regression is running: Cube01 complete and Cube02 pre-close passes unchanged 0.300 mm gate. No final full-flow result yet. Real link8 fixed-joint frame/anchor audit now succeeds; dynamic contact compensation still unvalidated. Legacy first-four push/inner-trim topology also differs from D004 (BUG-009), so even legacy demo completion alone cannot freeze TASK01. YAML remains DRAFT with 36 nulls; TASK02 TODO.

## 2026-10-03 completed legacy-demo checkpoint

Subsequent full run completes all five physical batches, controller exit 0 and both arms HOME. Detailed results/negative prior run remain in TASK01_FULL_FIXTURE_CONTACT_PROBE. Final center errors range 0.574–2.276 mm for the four fixtures; Cube05 controller 0.493 mm / later physical sample 0.563 mm. Rear+side simultaneously CLOSED sample count for first four is zero, so D004 is still unmet. Whole-process pause calibration safely fails on stale ROS state; replacement leaves ROS executor active and uses an explicit optional hold parameter. No benchmark freeze, physics/gate change or paper implementation.
