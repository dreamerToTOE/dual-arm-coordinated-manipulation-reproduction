# EXPERIMENT_LOG

## 2026-10-07 — single_cube_core_benchmark / IK diagnosis + same-seed precision A/B

Task: TASK01；Baseline: [ENGINEERING]/[EXPERIMENTAL]有限数值诊断，不是论文算法。Platform: native Humble/MoveIt2 2.5.9/LMA/FCL，无Isaac。Source: instrumentation12a6d74/binary415f23ef；A/B与dense8a5bbaf/binary01d64241；AABB2856fa5。Config:原schema2候选ff490a56…及runtime d4b290c模型hash不变。Seed:原显式端点策略；A/B精确原probe02 PRE_PUSH14q、每臂一次；dense上一q延续。

Results: diagnostic01为编译结束前旧binary误跑，INVALID_DIAGNOSTIC_OLD_BINARY/exit1，缺诊断字段和实际exe SHA，不当作新代码验证。正确diagnostic02/原精度对照exit1均定位ROTATION_RESIDUAL_REJECTED：两臂SUCCESS、bounds true、角残差2.582469e-4/9.985173e-4rad。仅本地epsilon1e-7（权重/验收不变）同seed角残差1.841597e-6/2.037263e-6rad、IK/FCL PASS，exit3/PASS_RECORDED_STEP_ONLY。

Dense: 六端点PASS；157状态、步长1.987179mm、FCL pairs0、joint margin最小25.755478deg、相邻单关节增量最大0.415676deg、TCP translation最大6.591492e-9m/rotation9.942151e-6rad。无时间化/连续扫掠保证。AABB audit:628对、体积穿透0、table边界touch157/deep目标touch1、4基本测试PASS/exit0。

Artifacts: results/20261007_TASK01_single_cube_{ik_diagnostic01,ik_diagnostic02,precision_default,precision_tight,precision_dense}/各metadata.json、JSON/CSV、probe_evidence.log；完整命令见reports/TASK01_SINGLE_CUBE_IK_DIAGNOSIS.md及逐run metadata。Native dense exit3/PARTIAL_UNDEFINED_START，不是TASK01 PASS。机器人/吸盘命令0、新物理启动0、ACM/工具/车厢/TCP/基座修改0；BUG019模型差异仍OPEN，START和READY/reset待验。

## 2026-10-06 — single_cube_core_benchmark / geometry_probe01,02

- Platform: native ROS2 Humble/MoveIt2 2.5.9/LMA/FCL，零Isaac启动/零关节和吸盘命令。Source b31ff05/c9d71f4，runtime模型d4b290c；候选hash ff490a56…，几何/ACM不改。
- probe01: 六规定插入端点通过，START未定义，exit3/PARTIAL；不是完整链PASS。
- probe02: 六端点通过；上一q seed连续检查第二状态（CubeX0.791987179，0.641026%）无合格双IK，exit1/FAIL_STOP。不记录为物理碰撞/全局无解；具体臂/插件错误需另行批准诊断。
- 端点最小关节余量3.189440°；最近腕/工具墙FCL距离为right_link7↔deep wall2.205603mm；最大抓取位置残差0.000585mm。原Isaac mesh不等价，不能据此认证物理净空。
- Artifact roots: results/20261006_TASK01_single_cube_geometry_probe01、probe02；metadata.yaml/sample_results.json/dense_insertion_results.json/三个CSV/精选原日志；详情和完整命令见reports/TASK01_SINGLE_CUBE_GEOMETRY.md。
- Stop rule: 首败立即停止，未进入Isaac READY/reset、force/P4或其它后续任务。

## 2026-10-06 — legacy_task27_five_cube / 仅结束上一请求遗留GUI

旧gui_contact_timing_cube01在本轮请求前已controller1，DUAL_SIDE_APPROACH rearCLOSED/sideOPEN、left86.949/right27.352Nm触发80Nm保护，无后续X/Y执行。本轮仅pause并正常关闭自有GUI0，补旧metadata，不开展新旧应用测试。raw summary2650 snapshots/errors[]保留；不算新单Cube科研试验。

## 2026-10-06 — gui_physclock_cube01 final FAIL；CONTACT IPTP准备

6fa161e/75f798a1、fresh可见/zero-preplaced/first1,max1/scale1。CONTACT310样本、左tracking5.429181deg、leftJ2 raw86.670166Nm、Cube左工具接触217.403930N；原80Nm互锁/双OPEN/controller1/完成0，无X/Y。GUIpause/SIGINT0，1904held/11098atomic/1849sparse完整性0错，279.117870s。早20s外部只读原子1199样本/PhysX-wall1.000084/receipt max41.339ms，不覆盖contact窗口或作单因证明。下一仅Task01侧下降同q/IPTP按现有缩放构建中，物理PASS待结果。

## 2026-10-06 — gui_physclock_cube01 RUNNING

runtime6fa161e/binary75f798a1、GUIadapter433e836，production build02 58.5s/exit0、63Python/两政策C++ PASS。0preplaced/first1/max1/scale1/rear45/side-15/PhysX秒回放，fresh可见GUI截图确认/first feed真实READY后开始actual运动。沿用自有新MoveIt，无新后台沙箱/全局参数或world豁免。命令完整写metadata；只读20s原子receipt对物理stamp采样，尚未从软件/启动预记物理PASS。

## 2026-10-06 — gui_normal_cube01_run02 FAIL_CONTACT / PhysX秒修复准备

生产6bc24ec/08f3060a，headlessFalse/zero-preplaced/first1/max1/scale1现实墙钟。CONTACT207样本、左跟踪10.108530deg、Cube-left link8峰468.823105N、leftJ2 raw86.323242Nm；原80Nm拒绝、双OPEN/controller1/完成0，无X/Y及后续Cube。GUIpause再SIGINT0，6158held/26516atomic/4419sparse0完整性错、573.024725s。构型随机性/GUI物理实时比未控制，不能断言单因。原动态Cube被工具接触后移动，最终不是成功落位。

仅Task01计时以已有原子物理stamp推进的新软件测试通过；首build22.3s/error2变量重名，日志原样保留，修正后build02待结果。修改路径几何/drive/物理/门限0次，未重启headless，fresh正常GUI复测待启动。

## 2026-10-06 — 可见GUI负启动与正常倍率首件RUNNING

gui_normal_cube01：官方Isaac GUI可见但Viewport空网格，原物理/Prim/first feed有效；控制器命令0，渲染连接排查后Kit139，不是速度/协议物理结果。gui_normal_cube01_run02：可见SimulationApp入口截图显示完整原fixture，runtime6bc24ec/binary08f3060a，first1/max1/scale1/zero-preplaced/roll-15/rear45，原atomic反馈和full-rate只读held/release启用、ROS_LOCALHOST_ONLY0。正常GUI实测已启动，结果未出，不预填成功。新GUI设置两测试加原61=63PASS，benchmark36nulls/原hash不变，完整命令和负结果在metadata/报告。

## 2026-10-06 — empty_handoff_full01 final FAIL；新倍率没有物理结果

runtimef237cff/binary812c71ee、原零预置first1/max5/scale5/hold0配置；第一X1–15双CLOSED完成，X16互锁反馈STALE_OR_INVALID（left20.627/right30.965Nm<80），安全双OPEN、controller1/completed[]，后续Cube未命令。Isaac受控SIGINT后exit0。17stamp匹配舍入差<=0.000491945mm/deg，5862held/21398atomic/3566sparse无记录完整性错；release0、wall474.505s。记录完整性通过不等于ROS及时交付通过。空载helper未物理触发，根因待诊断。

随后用户要求normal倍率/GUI-only；独立Task01默认1.0、MoveIt规划限速仍12%。只编译和61离线测试，不启动headless或新GUI物理动作；尚无1.0倍率的运行误差/速度/成功率。旧scale5证据不可用于该新配置验收，benchmark36nulls/hash不变。

## 2026-10-06 — exact empty handoff replay PASS，物理回归RUNNING

results/20261006_TASK01_empty_handoff_replay：旧action/probe1；局部OMPL/IPTP probe02与最终f237cff probe03均0。最终a33c7565、full02最后step51290/stamp854833377916精确14q/三pose，same-start11+left491+right469完整FCL，CLOSED/obstruction安全拒绝、world前后完全一致；6条同raw路径三种计时全部安全，不证明单一TOTG因果。原参数/scene/ACM不改；软件61Python/2C++、analytic36nulls PASS。fresh results/20261006_TASK01_empty_handoff_full01本机headless0preplaced/first1/max5/scale5/hold0/side-15/rear45，production812c71ee、READY与hash守卫后开始实际回归；物理结果尚未产生。

## 2026-10-06 — coupled_rear_full02 final FAIL

runtimea3fceab/binary57e72f83，参数/命令见run metadata。前三真实CONTACT/X16/Y16/ROLE_SWAP/OPEN完成，GT center0.302/0.407/1.343mm、deep0.156/0.091/0.087mm、侧/邻缝0.259/0.397/0.160mm。第三清障6.3mm RRT无合法样本；26.9mm得到左右各3候选却只取最短，后验FCL拒绝left suction↔Cube03（t0.610/depth0.329mm），未执行该路径。completed[1,2]、controller1、headless0、后两无命令。105stamp舍入差≤0.000499181mm/deg；36469held/51175atomic/8529sparse完整性0错，release501。CONTACT/X/Y peak raw46.019/48.571/37.297Nm、该窗口机器人-墙非零pair0；COMPLETE跨转场，不能称全程零接触。BUG021旧HIGH本轮跨过，不宣称所有构型修复。原参数/36nulls不变。

## 2026-10-06 — coupled_rear_full02物理2/5运行checkpoint

controller仍运行/batch[1,2]PASS，前三新协议前两X/Y各16段均CLOSED且swap在release前。第一后抓candidate5/24通过新gate、第二candidate1；第二rearXYZ norm2.026/1.031/0.036mm。最新release+短清障GT中心误差0.302/0.407mm、deep0.156/0.091、side0.259/0.397，无批间HOME、原路长退出。第三初始抓取已开始，但尚未到关键side HIGH；不写五件PASS或稳定性。最终采样审计待flush，原seed/model/physics/gates不变。

## 2026-10-06 — coupled_rear_full02 RUNNING

runtime a3fceab/source final、serial force binary57e72f83，fresh Isaac4.5本机headless/0preplaced/first1/max5/scale5/hold0/side-15/rear45；沿用自有原参数MoveIt launch，仅fresh物理stage。启动等待READY≤90s并exactSHA守卫，controller实际模型/IK/首件RRT+FCL完成进入运动。尚无全件完成结果；commands/metadata独立full02，full01startup失败不覆盖。seed null/原模型物理门限保持。

## 2026-10-06 — coupled_rear_full01 FAIL_STARTUP_NO_COMMANDS

controller SHA174d6ef7 exit1因旧filter拒绝当前LMA root-arm参数；命令0/完成0，非物理推压失败。Isaac ready但在3600s空闲采样时限正常退出0，35998sparse/215989atomic0errors，仅自动第一件供料，未执行机器人。六参数RPC类型值有效；生产strings无root arm前缀，成功probe有，因此之前source/binary等价声明作废。串行强制 -B重建后再fresh full02，原日志保留、不覆盖。

## 2026-10-06 — coupled_rear只读链PASS，fresh full01启动

coupled_rear_goal_search首次exit1无命令/参数名布局错误，修正后02 exit0：记录rear60IK/0free拒绝，替代attempt4/5/6完成200mm连续下降/约330mm X/1mm Y/30mm退出完整FCL与相对TCP。某些endpoint-free候选连续链仍失败，负日志原样保存；HIGH的RRT连接不属于这个纯本地PASS。61Python与两C++成功重跑，C++首harness路径错误保留；controller52.2s构建、probe53.0s+修正build。当前实际插件LMA（KDL底层），不是更改IK算法。a3fceab /174d6ef7生产binary，fresh coupled_rear_full01零预置五件headless启动；metadata记录原参数/seed null，实际完成数待定。

## 2026-10-06 — full01第三件goal与rear替代构型诊断

side_goal_probe exit1：原fixed-rear下60IK/0free，主pair left_fr3_side_suction↔right_fr3_link5。rear_goal_search exit0：同rear TCP，rear_solved7，3对HIGH/CONTACT/park终点全FCL自由（attempt2/5/6）。两个无命令实验共用准确held快照46343/stamp772383373616、原远程world，仅本地替换当前Cube；未控制KDL内部RNG，不是全球不可行/受控A/B/路径/物理PASS。探针 ebddf6d、SHAa4462325、build52.7s；完整精确命令/输入见full01 metadata、raw日志。联合链版编译进行中，不预填通过。

## 2026-10-06 — rear_open_xyz_full01 FAIL_CUBE03_SIDE_HIGH

runtime39f1a0c/repro566ff09/binaryefb1d133，zero-preplaced first1/max5/scale5/hold0。实际completed[1,2]、各X16/Y16，最终center0.269/0.470mm，deep0.099/0.019mm，side0.250/0.470mm；短清障RRT转场/无批间HOME。rear XYZ最终0.047/0.006/0.002mm。第三侧臂高位8×约20s目标采样失败/Invalid goal state，controller1/安全双OPEN，第四第五未命令；非几何/80Nm触发。70原子stamp精确匹配/roundingmax0.000496，37804held/8899sparse/53398atomic0错误，release163（不称全部释放窗口覆盖）；headless0/wall1481.936s。持件窗口robot-wall非零pair0，不是模型一致性或五件稳定性证明。只读goal诊断新探针初build52.7s有声明/format warnings，修正后重新build中。

## 2026-10-06 — rear_open_xyz_cube01 PASS_FIRST_CUBE_ONLY

runtime39f1a0c/repro7b61780/binaryefb1d133…，普通zero-preplaced first1/max1/scale5/hold0。rear residual2.196→1.201→0.205mm，两次命令增量≤1mm、实际FK微轨迹span3.178/3.200mm（仍原4mm scope）；X16/Y16/controller0/batch[1]/双OPEN/HOME，最终center0.303/deep0.212/side0.216mm。35精确stamp geometry/rounding≤0.0004966，8470held/26166atomic/4361sparse0错误，4524release；持件窗口robot-wall非零pair0，raw revolute CONTACT最大46.669Nm。560.393s采样、headless0、MoveIt清理-11/joint bridge1。首件单次PASS不是多件稳定/GUI/benchmark冻结，full-five同binary准备。

## 2026-10-06 — rear_roll_cube01 FAIL_X1 / OPEN rear XYZ software PASS

runtime4ebe279/reproe4004ab/binarye50b23fe…，fresh零预置first1/max1/scale5/hold0、rear45/side-15。X1 alignment2.577694mm>原2.5mm；3条原子stamp准确匹配、日志舍入差max0.000488mm/deg。controller1/completed[]/双OPEN/headless0，35922atomic/4552held/5987sparse均0完整性错；没到墙/Y，非碰墙修复PASS。

新runtime39f1a0c/binaryefb1d133…后杯OPEN XYZ最多3次/向量1mm/目标0.3mm，不变原加载验收。colcon目标首次linkPose参数类型错误exit2/20.8s，修正后50.4s PASS；61Python、实际header的preclose与dual_fixture两组C++ PASS，analytic36nulls/DRAFT。fresh首件物理试验准备；不是论文算法或可靠性证明。

## 2026-10-06 — rear_roll_nominal01 PASS_NO_COMMAND

runtime39d72c6/probe902c1fb1…/build51.2s，side-15、rear镜像45，probe0/3链通过。第一次原世界坐标LP status4，等价重心坐标default仍status4；两份失败JSON保留。同约束HiGHS-IPM审计1330节点×三墙0交集，61PythonPASS。无机器人/吸盘/供料/轨道/remoteScene命令，未物理执行，非全机器人PhysX或连续tracking保证。

## 2026-10-06 — atomic_feedback_cube01 FAIL_Y15_FRESH

完整命令/源码hash在run metadata。controller1/完成0，X16/Y14完成，Y15原80Nm left86.999/right70.170、feedback FRESH；实际right link7↔+Y墙745.807766N/step19613。双OPEN/headless0。25171feedback/0错、9491held/4195sparse/0完整性错误；33打印几何与精确物理stamp匹配到舍入误差。

同callbackUSD源X9–11可产生-1.622/-1.631/-1.755mm假负rear gap，最大rear差3.055mm；未重建旧ROS异步接收。旧nominal02三墙凸包：1330节点deep0/minusY0/plusY7交集，LP值非深度；只读后腕45deg候选待检查。60Python/C++PASS，场景/物理/门限/YAML不变。

## 2026-10-06 — cup_roll_cube01 FAIL_X3 / atomic feedback准备

run metadata保存runtime dd63c74、repro eb3b7f9、binary f74cc897…、first1/max1/scale5/hold0/zero-preplaced/roll-15、seed null和完整命令。controller1/完成0，X3旧rear=-1.784mm/末同一步+1.065277mm；双OPEN，headless0，held4738/sparse4085/0错误。未到深墙/Y，不能用名义1330节点检查当物理PASS。

新原子测量软件56Python/C++PASS；原模型/桥/scene/hash/YAML不变。新的受控源对照首件待实际结果，不预填通过。

## 2026-10-06 latest — held diagnostic02 FAIL / nominal wrist02 PASS_NO_COMMAND

- 本机Isaac4.5 headless / 原source d35cc0c+b749abc / first1,max1,scale5,hold0,zero-preplaced / RNG未受控；diagnostic02 controller1、X16/Y14、Y15原80Nm止动 left86.958/right52.123；bothOPEN/后四件未发指令，headless SIGINT后0。held10538/稀疏4598均0完整性错误。源commit、binaryhash、完整命令见run metadata。
- 真正机器人-墙pair `/World/left_fr3/fr3_link7`↔`WallDeep`，X16峰309.657685N；Y15 step21051 same-row raw leftJ2=86.997253Nm/contact140.242401N。20Hz ROS guard与poststep峰值不同，不强行对齐。四肢/DOF同一步，不是D6 wrench。
- 19627/19753/21051精确14关节只读服务重放，模型FK+已知rail0.1m与物理最大差0.000872mm；实测X16/Y15 `/check_state_validity` valid且无wall pair。object.pose与primitive local pose单列，防规范化局部0位置误读。
- Fresh official USD SHA3feceb47…与cache一致；NVIDIA mesh convexHull、URDF STL差异存在；原USD凸包在记录实测姿态与深墙LP交集有正共同球半径，STL凸包比较则不相交。LP值不是碰撞深度/最小距离，未逆向PhysX cooked hull/contact offset。
- nominal01/0cfdbaf probe0/3链名义通过，但stdout/rosout穿插，hull分析1拒绝，保存负结果。nominal02/c13ea40独立数据，probe0/3链通过、1330腕部节点、0深墙凸包重叠/minXplane6.766308mm。只读无joint/suction/feed/rail与Scene/ACM写；不是物理/全五件PASS。
- 53Python/build目标PASS，analytic PASS only/36nulls。新转角仅探针，未改执行器。原source/scene/bridge/YAML hash保持。

## 2026-10-06 follow-up — 网络恢复，原场景第二次启动

原S3直连/代理HEAD恢复HTTP200，runtime d35cc0c正常push成功；保留startup01失败。相同官方资产/原参数的startup02重新运行，held live handles与首件物理诊断仍待验证，尚未发controller命令。BUG017根因未解决，BUG018外部连接暂时恢复不抹掉负结果；模型/物理/门限/YAML不变。本段更新此前“final”失败checkpoint，不叫新物理PASS。

## 2026-10-06 final — held_fixture_diagnostic01 FAIL_STARTUP

Task TASK01；local Isaac4.5 headless/ROS2 Humble/MoveIt；runtime d35cc0c769fe51832dd0717ba0fcf71b873e2cef/binary d6b53269…，seed null。原first1/max1/scale5/hold0/0preplaced配置，controller未启动。44Python/build103s PASS、analytic36nulls；headless原FR3_asset_url失败，failure.json存在但app exit0，严格判FAIL_STARTUP，held_samples0/live handle未验证。MoveIt启动planning ready，关闭-11/bridge1，非运动失败。结果metadata与startup_evidence.log保存，完整raw本地ignored。网络curl35（SSL EOF）/SSH255（banner timeout）/SDK ERROR_CONNECTION；未使用未经溯源缓存。

## 2026-10-06 — held_fixture_diagnostic01准备

Task TASK01；[EXPERIMENTAL]首件新协议诊断；local Isaac4.5 headless/ROS2 Humble/MoveIt。first1/max1/scale5/hold0/zero preplaced；新代码待commit SHA记录；39Python/build PASS。原场景和门限不变，原Y15FAIL保留；startup检查中，未发控制命令。结果路径results/20261006_TASK01_held_fixture_diagnostic01/，metadata待真实过程补齐。

## 2026-10-05 final — dual_fixture_cube01_measured FAIL / released diagnostic PASS

- Task: TASK01; baseline: [EXPERIMENTAL] user-approved3+2 protocol; platform: local user-machine Isaac4.5 headless/PhysX/ROS2 Humble/MoveIt.
- Executed commit e0477ab3a8ba2b23bf99297e8af99227d727ede0, binary d1658940c72be17d4cb903bd0fdd3357ce5f82b7514d22d5e55207baaff82cff; seed null/uncontrolled. Config benchmark_v1.yaml/hash a49d60a4… unchanged; first1/max1/scale5/hold0/zero preplaced. Commands: measured run metadata.json.
- FAIL/controller1/completed=[]: X16/16 and Y14/16 dualCLOSED; measured-start FCL/replanning succeeds; Y15 guard left86.975/right32.984Nm>80Nm. Later cubes not commanded; bothOPEN on abort. X deep seat0.445mm; Y last completed deep seat0.191mm/alignment1.448mm/tilt0.220deg.
- Released static-state diagnostic exit0/FCL PASS (all remaining walls/table/other objects retained). Later released state is not event-time collision proof. Last sparse dualCLOSED pose (1.099520,0.225646,0.260454)m, 17.354mm short of nominal Y endpoint. No calibrated contact-wrench/root-cause claim.
- Artifacts: results/20261005_TASK01_dual_fixture_cube01_measured/{metadata.json,analysis.json,protocol.json,controller_evidence.log,released_state_evidence.log}; ignored raw logs/poses/audit/summary. 9432 snapshots/0 integrity errors; release_contact_samples.jsonl empty because release phases not reached.
- Build66s/Python35 PASS; analytic geometry PASS only/36nulls. All owned processes stopped, headless exit0; MoveIt teardown-11/bridge1 independently of controller1. No source edits during physical run. Old5/5/new nominal3-chain PASS do not establish new physical5/5.

## 2026-10-05 follow-up — dual_fixture_cube01 FAIL / measured replay running

- Actual runtimeff20ac3/bd1de5b7…, first1/max1/scale5/hold0/0preplaced: controller1, completed=[], bothOPEN on abort. X16/16 dualCLOSED, deep0.286mm/alignment2.171mm/tilt0.265deg; Y0 completed slices. Raw guard lacked torque/state reason; no exact cause claim. 4747 sparse PhysX samples, integrity0; later4 cubes parked. Metadata/analysis/protocol/controller_evidence all under run directory.
- e0477ab/d1658940…: measured role-swap seed/current FCL/explicit interlock diagnostics only; 54.3s buildPASS, Python35PASS, prior4 C++ policiesPASS. Fresh original scene measured Cube01 replay started, same config; result pending, no source edits mid-run. MoveIt retained, original physical stage restarted. Detailed commands/artifact paths in measured run metadata.

## 2026-10-05 TASK01 dual_fixture_preflight / cube01

- Platform: local user machine Isaac 4.5 headless + ROS2 Humble MoveIt; not GUI acceptance.
- Runtime final source: ff20ac3 / probe binarybe34b81c… / executablebd1de5b7…; reproduction basebb301b2 + new records/tests. Seed:null, explicit nominal joint seeds in source, internal IK/OMPL randomness uncontrolled.
- Commands/config/status/artifacts: `results/20261005_TASK01_dual_fixture_preflight/metadata.json` and `results/20261005_TASK01_dual_fixture_cube01/metadata.json`. 原场景/工具/参数/ACM/门限未改；YAML SHA256 a49d60a4…，36nulls。
- Offline: 34 Python /4 C++ policy / build PASS. Analytic candidate PASS only.
- No-command nominal full-robot probe04 exit0: 3/3 contact/X/Y/30mm released exit FCL chains PASS, relative TCP max axis about0.002mm; no Arm publishers, remote scene/ACM mutation or physical commands. Probe01–03 failures preserved (IK config; independent time-scale relative drift / rejected Cartesian branch; narrow joint seed coverage).
- Fresh normal-feed first1/max1/scale5/hold0 physical controller started; actual result pending. It is not full-five, force-control or paper-method evidence.

## 2026-10-04 final — empty_rrt_full_01 普通实际执行 5/5 PASS

- 平台：用户本机 Isaac 4.5 headless + PhysX + ROS2 Humble + MoveIt2；不是 GUI 验收。源码 `df9c2c0` / binary `c760d506…`，无中途重编译或场景/门限调整。
- 配置：preplaced_count=0，first_batch=1，max_batches=5，center_pusher_arm=right，execution_time_scale=5.0，release_diagnostic_hold_sec=0（默认）。已知离线位姿；OMPL 随机数未受控。
- 结果：实际 completed=[1,2,3,4,5]，controller=0，最终双臂 HOME、双吸盘 OPEN。中心误差 [1.983,0.807,0.723,1.319,0.481] mm，深墙 gap [1.521,0.800,0.235,0.641,0.406] mm。第四 neighbor gap=0.347 mm；第五两侧 gap=1.987/1.473 mm。
- Cube02 preclose gap asymmetry 1.283→0.850→0.219 mm，3 checks / 2 corrections；规划总计 0.069299 s，执行 7.418296 s。其他四件不做多余纠偏。原门限不变。
- 记录：18,498 个稀疏 PhysX snapshots / 0 integrity errors，3,212 个 release snapshots；controller 首日志至最终 batch PASS=1,726.184527 s，sampler wall=1,940.471278 s（含准备/空闲）。慢速 scale=5，非效率基准。
- 退出：headless=0；MoveIt 子进程关闭 -11 / joint bridge 1 单列，不能由 launcher 0 宣称全部干净关闭。自有进程已停。
- 证据：`results/20261004_TASK01_empty_rrt_full_01/{metadata.json,analysis.json,release_windows.json,controller_excerpt.txt}`；raw 在该目录本地保存并忽略。完整命令见 metadata 和报告。
- 边界：RRT 备用未物理触发；一轮成功不解决历史释放漂移/可靠性/已有对象恢复比较，也不证明论文接触/力控或冻结基准。TASK01 IN_PROGRESS / 36 nulls。

## 2026-10-04 — empty_rrt_replay_01 FAIL / replay_02 PASS; full_01 running

Replay01exit1/newguardrejections/exactrestorefalse; norobotcommand. Replay02freshMoveItactualrequestconstraints/railshift.1: exit0, fullFCL1277samples, CLOSEDandobstructionnegativePASS, originalnamedIDs0→temporary6→restored0; notexisting-IDrestorationproof. Builds56.2s/55.8s separatelyrecorded. Runtimefinaldf9c2c0/binaryc760d506.../Python28/C++PASS. Full_01 localIsaacheadlessnormalfirst1/max5/scale5/hold0/3000sdeadline starts; samplerREADY/controllerplanning, actualcompletionpending. Preserveallraw/metadata/commandsandnegativeprecedingrun.

## 2026-10-04 — measured_side_full_01 final physical FAIL

Runtime2fbfa0b/binary6a64fb90..., hold0/preplaced0/first1/max5/scale5. Cube01batchPASS; Cube02COMMON_DROPGT(.768,-.060,.262), bothOPEN; fourCartesianstepsfraction1butFK752–967mm, boundedIK118/151failure, exit1/safeabort. NoCube02side/release-windowtestandnolaterCubecommand. 17319sparsePhysXposes0integrityerrors; headlessSIGTERMaftercontrollerabortwritesummary, noGUIused. Finalmetadata/analysis/release_windows inresults/20261004_TASK01_measured_side_full_01. CurrentnewRRTunbuilt/notusedinthisrun. 28offlinePythontestsPASSnextiteration.

## 2026-10-04 — Diagnostic02 final FAIL and new ordinary regression preparing

Diagnostic02 raw/analysis/release_windows retained: exit1/completed[1], firstcell0.946/deep0.497/side0.805mm; seconddeep1.804mm, laterpre-releaseSIDEPREFLIGHTcommandseedFCL0.783mm abort. No secondrelease trace, no causalclaim on originalBUG016. 13227poses0integrityerrors,1617windowcontacts; headlessexit0,teardownmovegroup-11/jointbridge1. Addedmeasuredsideactualstart runtime2fbfa0b/binary6a64fb90...,policyCPP/Python28/buildPASS. Normalfirst1/max5/scale5/hold0/preplaced0 runmeasured_side_full_01next; not a PASS untilactualcompletion.

## 2026-10-04 — Diagnostic02 in-progress checkpoint

TASK01 EXPERIMENTAL normalfeedfirst1/max5/scale5/releasehold3s, runtimeb259366/binaryc0939f21..., sourcecapture6f8dd67. Original scene/physics/gates preserved. FirstcubeSIDE_PRESS/release/shortclearance observed: stationaryOPEN holdXdelta0.028mm, shortclearanceXdelta0.000mm. This is not evidence for secondcube norordinary timing. Stopafterbatch2 planned beforeCube03 commands. Startup01negativeBRANCH_SIGN failure archive, no controller then; build56.5s andPython28testsPASS. No active motion repair yet; tools/contacts samephysstep, phasearrivalasync, collisionforceexcludesD6wrench.

## 2026-10-04 — Release diagnostic software checks

TASK01 ENGINEERING, 25PythonunittestsPASS including activephasewindow selection/identity+rotatedtoolTCP transform/invalidquaternion rejection. Diagnostic runtime addsnoordinarymotionchanges, optionalholdEXPERIMENTALdefault0. Preparingnormalfeedfirst1/max5/scale5/hold3, releasewindowfull-rate same-step contact/tools only; actualresultpending, notphysicalPASS.

## 2026-10-04 final — Actual bounded XYZ PASS, full five FAIL at later release

TASK01 ENGINEERING/EXPERIMENTAL, Isaac4.5/Humble/MoveIt2, runtimef0812a4/binaryfc5e7f8a...; reproductionb0dbd86(test)/8adf617(launch record), OMPL RNG uncontrolled. Metadata commands/config/hashes in `results/20261004_TASK01_preclose_xyz_full_01`. Normalfeed0preplaced; exit1/completed[1],714.408s controller/815.721s sampler. Cube01cell1.576/deep0.871/side1.313mm. Cube02 actualXYZ correction X2.012→1.361→0.606,Z1.589→1.009→0.451,gapdelta0.879→0.607→0.275mm; original gatesPASS, maxvector1mm, two correctionsplan0.078621s/execute7.569621s. Pre-side-pressdeep0.488mm but final5.138mm>3mm; sim689.933firstbothOPEN x1.099789, sim691.133x1.094862, finalyaw0.000120deg. 7680samples0errors; Cube03–05unexecuted; allownedprocessesstopped, teardown-11retained. StaticFK/Isaac maxnorm0.056mm is not dynamic synchronized calibration. C++/22Python/build/realXYZ+FCLno-commandPASS in unitrun; firstPython parserfailure retained. No scene/model/physics/ACM/threshold/loaded-control/freezechange; not stable/full-five benchmark proof.

## 2026-10-04 — XYZ header mathematical checks

Task TASK01, baseline ENGINEERING pre-close XYZ, standalone C++17. Command: `c++ -std=c++17 -Wall -Wextra -Werror -I <legacy>/ros_ws/src/fr3_dual_palletize/include platforms/isaac_ros2/probes/test_preclose_alignment.cpp -o /tmp/task01_preclose_xyz_test`; execution PASS. Checks: old Y semantics, combined vector direction/1mm norm bound, tiny and zero residual, NaN/Inf rejection, mathematical previous-static-failure replay. No robot commands or physical-tracking proof. Build/real-model/full-flow trials pending; report TASK01_PRECLOSE_XYZ.

## 2026-10-03 — Current variant full-five actual FAIL_SAFE_STOP

TaskTASK01, baselineEXPERIMENTAL normal-feed D014/D015 variant, Isaac4.5/ROS2/MoveIt2; repro511349c atlaunch/legacy3ee42d2/binary77b4f499..., OMPLuncontrolled. Commands/config/artifacts: `results/20261003_TASK01_precision_full_five_01/metadata.json`, reportTASK01_PRECISION_FULL_FIVE_REGRESSION. Actualexit1/completed[1], no preplacement. Cube01center1.605/deep1.006/side1.251mm; Cube02precloseX3.027→3.145→3.150mm against2.500mm gate, gapdelta2.230→0.427→0.001mm against0.300mm gate. No suction/laterCube execution. 7214sparse samples0errors, sampler761.389s/controller472.036s, rawpushtorque35.53Nm(notTCP). Allownedruntimesstopped; MoveItteardown-11/jointbridgeExternalShutdown exit1 independent. Offline21/21PASS; no YAML/hash/runtime/model/physics/gate change. Prior partialsuccess does not erase newfailure; no frozenbenchmark/paper/reliability claim.

## 2026-10-03 — Current variant normal full-five run preparing

Task TASK01, baseline EXPERIMENTAL normal-feed approved precision variant, Isaac4.5/ROS2/MoveIt2; uncontrolled OMPL, no preplacement. Planned run `results/20261003_TASK01_precision_full_five_01/`, first_batch1/max_batches5/time_scale5, same binary77b4f499... and original physics/gates. No physical result yet; exact commands/pins/artifacts in metadata and report TASK01_PRECISION_FULL_FIVE_REGRESSION. Test-only code changes; no statistical reliability or frozen benchmark claim.

## 2026-10-03 — Final actual fourth/fifth continuous run

Task TASK01 / EXPERIMENTAL Cube04 precision + engineering empty retreat. Legacy3ee42d2/controller binary77b4f499..., reproduction5c72a1a atlaunch; uncontrolledOMPL, originalslots/cells/time_scale5. Exact commands/config/pins in `results/20261003_TASK01_empty_retreat_pair_01/metadata.json`. Controllerexit0, actual batches[4,5]PASS (first3preplaced). Fourthgap0.375/deep0.244mm, fifthcenter0.530/deep0.476mm; 7778 valid sparse poses/0errors; rawpeakjoint torque34.21Nm. ReleasedcurrentCube FCL540/287samples passes, no fallbacktrigger. Simulatorstopped successfully; MoveItteardown-11 separately. Basic/long no-command FK/FCL and isolated fifthalsoPASS; final report TASK01_EMPTY_RETREAT_REPAIR. No YAML freeze/full-five/reliability proof; all prior failures preserved.

## 2026-10-03 — TASK01 empty retreat software regression

Result: PASS software only. Commands: `colcon build --packages-select fr3_dual_palletize --symlink-install --executor sequential --cmake-args -DCMAKE_BUILD_TYPE=Release`, C++ policy -Wall/-Wextra/-Werror, Python unittest19/19, benchmark draft analytic checker PASS/36nulls. No robot commands yet in this iteration. Report: TASK01_EMPTY_RETREAT_REPAIR.md. Real RobotModel and physical trials next.

Follow-up runs: `20261003_TASK01_empty_retreat_unit` basic + long deterministic rounded-seed FK/FCL replay PASS (initial probe-only input mistake retained); `20261003_TASK01_empty_retreat_center_01` actual fifth full physical exit0/PASS, 0.540mm error, 0.514mm deepgap, 4691 samples/0errors. CurrentCube FCL included, no fallback trigger, no threshold/model/physics change. Four preplaced not executed; exact commands/source hashes in run metadata. MoveIt teardown -11. `...empty_retreat_pair_01` starts next clean fourth/fifth experiment.

## 2026-10-03 — Final Cube04 variant physical result: PARTIAL
- `_03`: PARTIAL_CUBE04_PASS_CUBE05_EMPTY_RETREAT_PLANNING_ABORT. Exact final source `7be3659`, binary `daec912…`, time_scale=5. Actual batch4 PASS (neighbor 0.227 mm, deep 0.413 mm); batch5 transport/drop done, empty retreat invalid FK path rejected, no fifth rear push. Controller exit 1, move_group teardown -11.
- 8,985 sparse post-step snapshots, 0 sampler/integrity errors; fourth helper closed inside=0, inner trim commands=0; fourth lateral span 0.205 mm/yaw max 0.053 deg, max raw push joint torque 24.29 Nm. Not calibrated contact wrench. First three pre-placed: not full-five proof or stable-success estimate. Both test processes stopped.
- Python regression 19/19 PASS; C++ policy/syntax/diff checks PASS; unchanged benchmark analytic checker PASS with 36 nulls/hash `a49d60…`. No paper/TASK02 implementation.

## 2026-10-03 — Cube04 precise staging is not sufficient in first physical trial
- `_02`: FAIL_CUBE04_FINAL_NEIGHBOR_GAP_SAFE_STOP, controller exit 1, zero completed new batches. Initial Y error 0.046 mm / oriented clearance 0.454 mm; final original axis-gap acceptance 1.827 mm, oriented projected gap 1.607 mm. Cube05 not executed. Raw push torque max 23.0 Nm. 6,036 sparse samples, zero integrity errors, no helper-side suction/inner trim. MoveIt teardown -11 retained separately.
- `_03`: FINAL_BUILD_REPETITION_RUNNING, time_scale=5 instead of 3, clean original physics, same original gates; not a new force/feedback algorithm. Exact source/binary identity will be recorded.

## 2026-10-03 — Cube04 precision variant startup
- C++ policy regression and Python syntax PASS. Package build PASS; non-portable directive-inside-logging-macro warning removed before final test build.
- `20261003_TASK01_cube04_precision_01`: FAIL_NEW_PROBE_STARTUP_API, no controller execution; initially passed extra argument to legacy callback subscription; raw startup preserved. Final probe uses existing verified post-step API and exception artifact writer.
- `20261003_TASK01_cube04_precision_02`: RUNNING_CHECKPOINT; first three pre-placed/physically settled, Cube04/05 physical execution pending. Not full-five proof; scene/material/final gates unchanged.

## 2026-10-03 — TASK01 fixed-contact TCP roll diagnostic
- Same `20261003_TASK01_fixture_protocol_clearance` run family, additional `roll_sweep_summary.json`: fixed face center/normal, TCP roll 0..345 deg in 15 deg steps, 24/24 poses have lateral rod/Cube03 OBB intersection, zero clear box-only poses. No robot commands; no arbitrary-contact/IK completeness claim. New regression passes; 18 Python offline tests total.

## 2026-10-03 — TASK01 controlled hold, protocol geometry and actual material
- `20261003_TASK01_fr3_static_payload_v2`: PASS_CONTROLLED_HOLD_AND_CUBE01 / PARTIAL_METROLOGY. Default-zero optional 7-s task-thread hold, legacy 76408c8; controller exit 0, placement/HOME complete. 34,510 snapshots, 238 full-rate load samples. Mean net-support error 0.000370 N but instantaneous RMS 0.494278 N / moment mean 0.014902 Nm and velocity discrepancy persist. Raw six-step diagnostic was aliased; full-rate reanalysis does not convert this into a sensor PASS.
- `20261003_TASK01_fixture_protocol_clearance`: REQUIRED_SIDE_POSE_INTERFERES. Read exact existing xacro and prior full-flow Cube03 PhysX pose; Cube04 centered right helper support boxes intersect neighbor, minimum lateral SAT axis overlap 33.524 mm. Analytic only, no commands/model changes. Metadata + summary tracked.
- `20261003_TASK01_mass_material_audit`, `_v2`, `_v3`: Initial two PARTIAL audits retained; final PASS_MASS_AND_SHAPE_READOUT / MODEL_REVIEW_PENDING. Cube actual mass 0.800000012 kg, static/dynamic friction 0.5/0.5, restitution 0.0. Declared 0.90/0.75 material deleted by cleanup; no effective combine-rule freeze. Initial wrong tool path corrected in reader only; no scene changed.
- `python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py' -v`: 17/17 PASS. YAML checker still analytic PASS / 36 unresolved, not TASK01 PASS. Report `TASK01_RUNTIME_REVIEW_20261003.md` contains commands, results and boundaries.
- MoveIt SIGINT teardown again exit -11; retained full-five raw launch log. Test processes fully stopped; no ordinary controller failure inferred from teardown.

## 2026-10-03 — TASK01 completed normal feed and retained failed metrology
- results/20261003_TASK01_full_five_corrected_01/: PASS_LEGACY_FIVE_CUBE_DEMO_ONLY, controller exit 0, physical batches 1–5 complete, both arms HOME, wall 1284.391 s. Detailed physical geometry and 70,434-snapshot integrity analysis uploaded; raw heavy remains ignored. BUG-009 contact protocol not passed.
- results/20261003_TASK01_fr3_static_payload/: FAIL_EXPERIMENTAL_PAUSE_THEN_SAFE_ABORT, 7-s SIGSTOP of controller group also pauses state monitor; resume triggers stale-state failure and releases both cups. Raw script/negative logs preserved; no normal-flow regression claimed.
- Fresh results/20261003_TASK01_fr3_static_payload_v2/ is controlled opt-in task-thread hold instead of process suspension; phase recorded with physical snapshots. Build PASS 47.9 s; physical force statistics pending at this checkpoint.

## 2026-10-03 — TASK01 corrected runtime checkpoint
- Run: results/20261003_TASK01_preclose_unit/metadata.json — PASS_UNIT_AND_BUILD_ONLY. Residual regression and corrected colcon build PASS; initial target include-path failure retained.
- Run: results/20261003_TASK01_full_five_corrected_01/metadata.json — RUNNING_CHECKPOINT. Fresh headless normal feed, max_batches=5, right center pusher, time_scale=3, no pre-placed fixture. Cube01 complete; Cube02 pre-close correction passes original gate. Final completion/force/pose audit pending.
- Link8 authored incoming fixed-joint anchor/axes audit succeeds; empty-branch static force/torque consistency is preliminary only, not dynamic contact/internal-force calibration.

Append-only experiment index.

At repository initialization, no experiments had been run.

## 2026-09-30 20260930_TASK00_mujoco_smoke
Task: TASK00
Baseline: none; environment smoke test only
Platform: existing isolated MuJoCo .venv
Commit at probe: 9f71e0a78a9d852d060b4e7e4c3225558d1d9bb1
Seed: not applicable
Command: see results/20260930_TASK00_mujoco_smoke/metadata.yaml
Config: inline one-joint sphere model
Result: PASS
Key metrics: MuJoCo 3.13.0; one mj_step advanced simulation time to 0.002 s
Artifacts: results/20260930_TASK00_mujoco_smoke/
Notes: This is not a dual-arm force-control or paper-reproduction experiment.

## 2026-09-30 20260930_TASK01_static_geometry
Task: TASK01
Baseline: none; candidate geometry check only
Platform: system Python 3 + PyYAML; analytic validation (not Isaac)
Commit at probe: ca2b1f75a85c32bcad87b193328cbe7424680183
Seed: not applicable
Command: `python3 scripts/validate_benchmark_candidate.py`
Config: `configs/benchmark/benchmark_v1.yaml` (DRAFT)
Result: PASS for internal analytic geometry; TASK01 itself remains IN_PROGRESS
Key metrics: 0 failed dimension checks; 30 unresolved/null configuration fields
Artifacts: `results/20260930_TASK01_static_geometry/`
Notes: No physical contact, collision, sensing or timing validation was performed.

## 2026-09-30 20260930_TASK01_contact_protocol
Task: TASK01
Baseline: none; candidate protocol and geometry check only
Platform: system Python 3 + PyYAML; analytic validation (not Isaac)
Commit at probe: 93e7e54 (parent of uncommitted draft)
Seed: not applicable
Command: `python3 scripts/validate_benchmark_candidate.py`
Config: `configs/benchmark/benchmark_v1.yaml` (DRAFT)
Result: PASS for internal analytic geometry/protocol; TASK01 itself remains IN_PROGRESS
Key metrics: 0 failed checks; 36 unresolved/null configuration fields; 1° yaw consumes 1.038 mm nominal center clearance
Artifacts: `results/20260930_TASK01_contact_protocol/`
Notes: No physical contact, collision, sensing or timing validation was performed.

## 2026-09-30 20260930_TASK01_center_right_physical
Task: TASK01
Baseline: none; experimental Task27 fifth-Cube probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit at probe: 76d24dc (new repo), d93f285 (legacy repo), with working-tree test patch later committed unchanged as 631b1f6
Seed: not fixed in legacy OMPL
Command/config: `results/20260930_TASK01_center_right_physical/metadata.yaml`
Result: PASS, one physical run; four fixtures pre-placed
Key metrics: Cube 05 final center 0.603 mm; +X wall gap 0.586 mm; +Y/-Y side gaps 1.361/1.639 mm; peak joint torque 35.96 Nm
Artifacts: metadata, `reports/TASK01_CENTER_ARM_SYMMETRY.md`, external raw ROS log listed therein

## 2026-09-30 20260930_TASK01_center_left_physical
Task: TASK01
Baseline: none; experimental Task27 fifth-Cube probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit at probe: 76d24dc (new repo), d93f285 (legacy repo), with working-tree test patch later committed unchanged as 631b1f6
Seed: not fixed in legacy OMPL
Command/config: `results/20260930_TASK01_center_left_physical/metadata.yaml`
Result: PASS, one independent physical run; four fixtures pre-placed
Key metrics: Cube 05 final center 0.669 mm; +X wall gap 0.633 mm; +Y/-Y side gaps 1.719/1.281 mm; peak joint torque 35.87 Nm; one pre-close reacquire
Artifacts: metadata, `reports/TASK01_CENTER_ARM_SYMMETRY.md`, external raw ROS log listed therein
Notes: Both arms HOME. Left and right results differ; no statistical equivalence is claimed.

## 2026-10-02 20261002_TASK01_center_repeatability
Task: TASK01
Baseline: none; [EXPERIMENTAL] legacy Task27 Cube 05 arm-symmetry probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Seed: uncontrolled legacy OMPL (no fixed-seed claim)
Command/config: Four per-run `results/20261002_TASK01_center_{right,left}_{02,03}/metadata.yaml` files; benchmark draft `configs/benchmark/benchmark_v1.yaml`
Result: Four new physical runs PASS with both arms HOME; including 2026-09-30, right 3/3 and left 3/3 PASS. TASK01 remains IN_PROGRESS.
Key metrics: right center error [0.603, 0.429, 0.374] mm, mean 0.469 mm; left [0.669, 0.408, 0.561] mm, mean 0.546 mm; maximum side-gap imbalance 0.582/0.802 mm (right/left).
Artifacts: `reports/TASK01_CENTER_ARM_SYMMETRY.md`, four per-run metadata files, external raw ROS logs named there; scripts `task01_capture_final_pose.py` and `summarize_task01_center_trials.py`.
Limitations: Four fixture cubes were pre-placed; no contact wrench; motion-time PhysX/USD pose disagreement remains open (BUG-005). `move_group` repeatedly segfaulted during Ctrl-C teardown after completed task runs (BUG-004).
Notes: Both arms HOME. Not a reproducibility or statistical symmetry result.

## 2026-10-03 TASK01 known-motion sensor diagnosis/calibration
Task: TASK01
Baseline: none; [EXPERIMENTAL] measurement calibration, not contact control
Platform: Isaac Sim 4.5; external ROS2 Humble observer
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus uncommitted measurement changes committed with this report
Seed: no random sampling
Command/config: Per-run metadata in results/20261003_TASK01_pose_timing/, physics_ros_30hz/, physics_ros_debug/, physics_ros_clean_30hz/, physics_ros_zero_damping_30hz/ and physics_ros_zero_damping_20hz/
Result: Initial no-ROS pose diagnosis passed. Mixed-library startups failed; clean-ROS angular calibration initially failed because the known-motion model omitted angular damping. Explicit zero damping on the free calibration body then produced two PASS_SENSOR_CALIBRATION results; gates unchanged.
Key metrics: 120 motion samples/run; p_max=0.000312946/0.000312902 mm, angle_max=0.000864737/0.000864742 deg (30/20 Hz frames, 60 Hz physics); callback errors=0; legacy USD callback lag=6.667/10.000 mm; scaled-quaternion error up to 27.464 deg.
Artifacts: Per-run metadata and ignored raw JSONL/JSON; reports/TASK01_PHYSICS_POSE_MEASUREMENT.md
Boundary: Deterministic no-contact free body; not manipulation accuracy or a benchmark gate. Explicit zero damping is not a change to Task27 physics.

## 2026-10-03 TASK01 fixture physics-channel integration
Task: TASK01
Baseline: none; [EXPERIMENTAL] pre-placed four-Cube fixture + legacy right-arm fifth-Cube task
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus uncommitted measurement adapter; legacy unchanged at 631b1f65656d025c1bb2173e874192f3fe4d355a
Seed: uncontrolled legacy OMPL
Command/config: results/20261003_TASK01_fixture_sampler_startup/metadata.yaml (failed startup) and results/20261003_TASK01_fixture_physics_channel/metadata.yaml (physical run)
Result: Unsupported tuple constructor argument caused first startup FAIL without robot commands. Corrected list initialization; fresh-scene right-arm full Cube 05 task PASS and independent physics recorder PASS.
Key metrics: center error 0.520 mm; deep gap 0.505 mm; side gaps 1.374/1.626 mm; peak joint torque 35.41 Nm; both arms HOME; logged task duration 215.142 s. Recorder: 14,295 samples, no missing physics steps, no errors, timestamps increasing. Final physical yaw 0.026334 deg versus legacy Bridge 0 deg.
Artifacts: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md; selected result summary + metadata; ROS log /home/ubuntu2004/.ros/log/task27_five_cube_center_insert_32050_1791006079693.log; ignored 32-MB physics snapshot JSONL.
Boundary: New topic is read-only, controller still consumes legacy Bridge; no claim of a synchronized wrench/TCP contract or complete five-Cube fixture construction. MoveIt SIGINT -2 today does not resolve prior BUG-004.

## 2026-10-03 TASK01 final measurement regression / empty-input guard
Task: TASK01
Baseline: none; [ENGINEERING] final measurement checks, [EXPERIMENTAL] known-motion fixture
Platform: Isaac Sim 4.5 + external ROS2 Humble; guard test without an Isaac publisher
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus final working-tree measurement changes
Seed: no random sampling / not applicable
Command/config: results/20261003_TASK01_final_calibration_30hz/metadata.yaml and results/20261003_TASK01_recorder_empty_guard/metadata.yaml
Result: Final 30 Hz external calibration PASS including exact position/quaternion equality of PoseArray and JSON snapshot. Empty stream yielded saved FAIL summary and exit 1 (negative test PASS, not sensor success).
Key metrics: 120 motion / 150 total pose samples; p_max=0.000312945784 mm, angle_max=0.000864737421 deg; zero callback errors. Empty guard: zero samples, 2-s startup timeout.
Artifacts: Per-run metadata, ignored raw summaries, reports/TASK01_PHYSICS_POSE_MEASUREMENT.md
Boundary: No paper controller, no altered benchmark gate; failure is kept distinguishable from physical task success.

## 2026-10-03 TASK01 collision force/torque calibration
Task: TASK01
Baseline: none; [EXPERIMENTAL] independent known-load fixture, [ENGINEERING] measurement sampler
Platform: Isaac Sim 4.5 PhysX CPU/numpy
Commit: 32ccb2b902ab23cd5f60c191d579ff7e2ccc7fe6 plus per-run uncommitted probe variants saved in this iteration; benchmark SHA unchanged
Seed: no random sampling
Command/config: results/20261003_TASK01_contact_force_{60hz,60hz_v2,60hz_v3,60hz_torque,120hz_yaw30}/metadata.json; probe paths/arguments/variant recorded separately
Results: First startup FAIL (nonexistent PhysicsContext getter); second startup FAIL (unsupported SingleRigidPrim keyword). Corrected 60 Hz v3 PASS has no nonzero torque stage and is not torque evidence. Final 60 Hz torque and 120 Hz/yaw30 runs each PASS all 13 checks. Saved check results are authoritative; early exceptions can still exit 0 with fast shutdown.
Key metrics: support 7.84800024/7.84799969 N; friction Fx -1.99999991/-2.00000003 N; resisting Tz -0.03996668/-0.03998334 Nm; wall yaw0/yaw30 (Fx,Fy)=(-4,0)/(-3.464101,-2) N. Each main window 60/120 samples. Dual suction CLOSED supports payload at 0.500 m while collision signal is zero, proving this interface excludes suction D6 forces.
Artifacts: per-run metadata/selected summary, ignored raw contact_samples.jsonl and Kit logs; reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md.
Boundary: Fixed calibration gates (0.05 N, 0.001 Nm) belong only to independent fixture. No benchmark material/physics/threshold change or paper/internal-force control.

## 2026-10-03 TASK01 incoming mount reaction / reference identification
Task: TASK01
Baseline: none; [EXPERIMENTAL] static articulated mount and suction payload
Platform: Isaac Sim 4.5 PhysX, Surface Gripper
Commit: 32ccb2b plus explicitly different uncommitted probe variants; seed not applicable
Command/config: per-run metadata in mount_reaction_identity, mount_reaction_roll90, mount_reference_identity, mount_joint_reference, mount_joint_reference_unscaled and mount_joint_reference_final under results/20261003_TASK01_*/
Results: Identity/roll90 trials establish known-load availability/direction, not reference-point identity because frames/points coincide. Early scaled-body COM trials have saved software PASS, but their unscaled COM/anchor interpretation is INVALIDATED; metadata reviewed status PARTIAL_REFERENCE_MODEL_INVALIDATED, raw kept. Final two unscaled trials PASS unique joint_axes_about_joint_anchor among nine hypotheses, verify physics COM=5 mm, principal roll45, joint anchor3 mm/joint roll30, payload hold and CLOSED/timestamps. Final field-name regression repeats exact numeric result.
Key metrics: known payload 0.8 kg, world Fz=7.848 N and Ty=-1.255680 Nm; final raw delta (Fx,Fy,Fz) about (0,6.796570575,-3.923998765) N, (Tx,Ty,Tz) about (0,0.616067643,1.067061339) Nm. Correct joint-axis/anchor error 3.435906e-6 N/4.429936e-7 Nm; wrong link origin 0.023544 Nm, wrong COM 0.015696 Nm, wrong link axes 4.0624 N.
Artifacts: metadata/selected summary, raw mount_samples.jsonl and Kit logs; force report.
Boundary: Not real FR3 compensation or universal rotating-joint convention validation. Hidden tool branch mass was not removed; false early origin inference explicitly corrected rather than silently erased.

## 2026-10-03 TASK01 full normal-feed five-Cube readout/preflight/execution
Task: TASK01
Baseline: none; [EXPERIMENTAL] unchanged legacy Task27 normal five-Cube flow, no pre-placed fixture
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit: 32ccb2b plus measurement runner variants; legacy unchanged at 631b1f65656d025c1bb2173e874192f3fe4d355a
Seed: legacy OMPL uncontrolled; no fixed-seed/repeatability claim
Command/config: results/20261003_TASK01_full_fixture_readout/, full_fixture_readout_v2/, full_five_physical/, full_five_preflight/, full_five_physical_v2/ and full_fixture_frame_audit/ metadata.json; full report contains all scene/bridge/MoveIt/controller commands
Results: Initial readout FAIL nonexistent STATE_READY; corrected v2 PASS_READOUT_STARTUP. Full-run startup FAIL bridge-overwritten namespace/BOX_INTERIOR_X; corrected run ready. Five planning-only batches PASS. Actual run FAIL: completed1/5, Cube02 stopped at PRE_CLOSE before suction, no later physical object commanded. Last added authored-frame startup audit FAIL on remote asset-root lookup (no robot commands), so that audit unverified.
Key metrics: 37,236 physics/contact/raw joint snapshots, zero callback errors; feed state [2,2,0,0,0] is ARRIVED, not placement. Cube02 gap delta 0.968 -> 0.315 -> 0.339 mm vs original 0.300 mm gate, minimum correction0.650 mm; independent physical final delta0.338941 mm. Cube01 center error1.792 mm, physical yaw -1.095465 deg; nearest oriented deep/+Y gaps0.06355/0.19531 mm, not whole-face flush. Peak Cube01-deepwall collision resultant139.098 N, not suction/internal wrench or a frozen force gate. MoveIt teardown -11 recurs.
Artifacts: selected metadata/summaries, full report; local ignored raw controller/MoveIt/Kit logs, topology and approximately1 GB physics_contact_samples.jsonl.
Boundary: Measurement completion and planning PASS are not physical full-flow PASS. Control event wall time is not yet aligned to recorded simulation time. New quaternion/force sampler is read-only; original controller still consumes old pose channel. TASK01 IN_PROGRESS, 36 fields unresolved, TASK02 TODO.

## 2026-10-03 TASK01 final offline/static validation
Task: TASK01
Baseline: none; [ENGINEERING] sampler algebra/guard tests and artifact checks
Platform: Python3/numpy offline
Commit: 32ccb2b plus final measurement changes
Seed: not applicable
Commands: python3 platforms/isaac_ros2/probes/test_physics_contact_sampler.py; python3 -m py_compile (five new Python files); python3 scripts/validate_benchmark_candidate.py; git diff --check; sha256sum configs/benchmark/benchmark_v1.yaml
Results: 8/8 unit tests PASS; Python compile and static checks PASS, analytic draft reports36 unresolved nulls. Draft hash a49d60a4dc6a8a00c3bf55a512113af50760968827a8cefe64dae1c7de55fde8 unchanged.
Artifacts: results/20261003_TASK01_contact_sampler_unit/{metadata,summary}.json; reports/TASK01_FREEZE_REVIEW_CHECKLIST.md lists all36 fields and explicitly pending approvals.
Boundary: These tests do not establish a frozen benchmark or five-Cube physical success.

## 2026-10-03 TASK01 full recorded-stream integrity
Task: TASK01; baseline none, [ENGINEERING] read-only artifact audit
Platform: Python3 JSONL, offline; seed not applicable; commit32ccb2b plus recorded measurement variants
Command/config: Self-contained Python stdin scan in results/20261003_TASK01_full_record_integrity/metadata.json, reading full_five_physical_v2/raw/physics_contact_samples.jsonl
Result: PASS_RECORD_INTEGRITY across37,236 rows. Missing steps, nonmonotonic steps/stamps, contact/pose stamp-step mismatches and nonfinite contact/articulation arrays all0. Maximum force-matrix vs normal reconstruction error1.525879e-5 N; dt0.0166666675359 s; Cube quaternion norm-squared error4.44e-16.
Artifacts: metadata.json/summary.json and original ignored JSONL. Does not turn the incomplete physical task into PASS or establish ROS-event clock alignment/FR3 wrench compensation.

Recommended entry:
```text
## <date> <run_id>
Task:
Baseline:
Platform:
Commit:
Seed:
Command:
Config:
Result: PASS/FAIL
Key metrics:
Artifacts:
Notes:
```
