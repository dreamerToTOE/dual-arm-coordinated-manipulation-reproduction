# TASK01 — 持件几何的原子 PhysX 反馈

2026-10-06，IN_PROGRESS；不是论文控制律/基准冻结。

最新工作流取代下方历史headless命令：用户要求后续只用可见GUI，新节点默认正常
播放倍率1.0（保留12% MoveIt RRT限速）。完整scene/Bridge/原子反馈代码见
[TASK01_GUI_SPEED](TASK01_GUI_SPEED.md)。最后full01已经首件X16反馈过期/无效安全
失败并停止，完成0；下方RUNNING是历史检查点，不是当前状态。

## === PRE-TASK REPORT ===

Task: TASK01 / BUG005、017、019，新增测量反馈工程修复。
Goal: 避免Cube/双TCP的USD显示滞后或独立latest消息混合造成间隙误判。
Paper method understood as: 不实现P2/P3；保持已批准3+2位置规划/执行协议。
Scope of this iteration: 新独立节点只在前三双吸附的几何门禁中采用同物理步消息；原场景/桥/材料/ACM/80Nm/几何门限/后两精准单rear不变。
Files expected to change: 独立PhysX观测适配器/headless opt-in/GUI bootstrap与单测；runtime新节点的buffer/几何消费；报告/六记录/结果元数据。
Validation plan: 消息布局/固定TCP变换/数值/时间/过期拒绝单测，编译；本机headless新鲜零预置首件scale5/hold0，保留原门限并记录同一步USD源对照与真实contact/DOF。首件成功再考虑下一件。
Known ambiguities / risks: 上轮X3日志rear=-1.784mm但末端同一步PhysX≈+1.065mm，时钟未对齐，尚不能判定唯一因果；新姿态尚未到深墙，原模型碰撞差异风险未消失；OMPL/IK种子未受控。
Need user confirmation: no，仅测量软件同步；若需要改模型/物理/门限/论文算法则停止另问。

## 接口与边界

`/task01/physics/fixture_geometry`：PoseArray，`world`，仿真时间，原`cube_paths`次序后接left TCP/right TCP。单个live RigidPrim view一次读取Cube与两个link8，TCP复用已验证固定工具变换；不读USD、无无效物理句柄回退。消费者检查长度/有限值/单位四元数/时间递增，steady接收年龄≤250ms，缺失或失效就停止。250ms为观测超时而非几何容差。

旧`/task27/cube_poses`与TCP话题/源码不变，供料/规划及后两单推仍走原流程。当前变更不是所有传感通路统一，也不是wrench标定。[ENGINEERING]原子消费，[ADAPTATION]仿真GT，[EXPERIMENTAL]首件复测。

GUI加载原Task27 bridge、PLAY后，Script Editor执行：

```python
exec(open('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/platforms/isaac_ros2/probes/task01_fixture_geometry_bridge.py', encoding='utf-8').read())
```

headless原复测命令增加`--physics-fixture-feedback`。控制器缺少新话题时拒绝启动，不能默默退回旧USD反馈。

## 原子反馈实测 POST（第一阶段，PARTIAL）

新鲜本机headless首件 / runtime88ef454/reproa952a18/binary31d862a6… / first1,max1,scale5,hold0,零预置、原side roll -15。

- 同步反馈启动有效；25171快照/0采样错，9491 held与4195稀疏记录0完整性错。33条打印几何按**精确仿真时间戳**匹配同一步真实记录，所有差仅日志0.001精度舍入（max0.00049987mm或deg），不按墙钟近似对齐。
- X16通过、Y14通过，原子gap没有X3假负值。源对照X9–11原USD rear最小-1.622/-1.631/-1.755mm，对应相同物理源rear均正，最大差3.055mm；证明USD源可使原门限误判，但不等于已经逐个重建上一轮ROS三个latest的接收顺序。
- Y15原80Nm保护停止：left86.999/right70.170，atomic_feedback=FRESH。真实right link7↔+Y墙峰745.807766N/step19613。双OPEN、controller1/完成0、headless正常停止0；不是反馈超时，不是论文内力或吸盘wrench。
- 原side roll只解决名义deep-wall检查的范围。补查旧nominal02双腕1330节点对三墙：deep0/minusY0，plusY有7个右腕Y节点交集；LP共同球半径不是穿透深度。此前deep-only PASS绝不能推广为all-wall PASS。
- 60Python/C++策略检查PASS，旧scene/bridge/YAML hash不变。新反馈消费工程得到实测支持，但完整任务仍FAIL，BUG017/019仍OPEN，不能冻结基准或推进论文方法。

## 第二阶段 PRE — 后推杯面法向腕姿候选（历史准备与新结果）

实测原子反馈首件完成X16/Y14，Y15出现rear right link7↔+Y墙接触，原80Nm保护停止。只读尝试rear绕worldX法向45deg，正Y件正转/负Y件镜像负转，目标是把后腕偏向中央空区；side仍worldY -15deg。中心/法向/L几何/原接触点与桌/墙位置不动，没有载荷下旋转或执行器自动启用。

验证：名义前三链全FR3 FCL/TCP约束、输出精确双腕FK，同时检查原USD link7凸包对三面墙（此前deep-only检查不足）。失败保留、不放宽门限；只读PASS不替代真实物理/空载接近完整验证。

结果`rear_roll_nominal01` /runtime39d72c6：probe0/前三链3/3/FCL与TCP约束PASS。原SciPy1.8.0 HiGHS默认LP在一条记录status4，不吞掉该行；等价重心坐标仍失败。保留两次负证据，换HiGHS内点LP、同一全部不等式/原>0交集判断、显式解残差检查，全1330双腕节点对三墙deep/minusY/plusY均0交集。共同球半径不是碰撞深度/最小距离，未替换任何PhysX/MoveIt几何。61Python/C++PASS。

物理复测PRE：在OPEN后抓-RRT及其预演链调用同一`dualRearFixturePose`，前三件rear幅值45deg、正Y正/负Y负；吸点/法向保持，后两单rear调用原pushPose。吸住后仍同进度平移，不在CLOSED时转腕；原物理/门限不动。编译→fresh首件原场景/scale5/hold0/原子反馈→同一步contact/DOF/几何审计；失败不推进下一件。

## 第三阶段 PRE — 后杯OPEN的XYZ到位精调

rear_roll_cube01在X1原2.5mm对齐guard失败2.578mm，双OPEN/controller1；精确同一步回放证实rear Z差为-2.363mm(PRE_CLOSE)、-2.462mm(CLOSED)、-2.578mm(X1)，不是旧USD假负值。新腕姿尚未实际到墙，不能宣布已修复墙碰撞。

复用现有`precloseAlignmentDeltaXYZ`（1mm向量限步、无最低量化）与`planFinePreclose`的局部FK微解算，在rear吸附之前、两杯OPEN时将后TCP到达新的Cube后面中心。目标到位精度0.3mm仅吸附前工程目标，不放宽原2.5mm加载门限；最多3次修正/4次检查，失败不CLOSE。按上一命令FK累加残差以消除执行偏差，保持现有杯面姿态，原Cube参与完整双臂FCL，helper只保持实测关节。第四第五/旧节点不改变；不做CLOSED补偿、力控或物理参数更改。

验证计划：已有XYZ边界单测+编译→fresh首件scale5/hold0/原子反馈→记录每次XYZ残差与次数/原门限结果；若仍需模型/物理/门限改变则停止另问。

实现/软件检查：runtime39f1a0c，controller build50.4s、61Python/两组C++/analytic36nulls通过。首编译误用`linkPose`参数类型，exit2后修正，不掩盖失败。首次fresh运行rear OPEN residual norm2.196mm，第一微轨迹FK span3.178mm；**1mm限的是加到上一命令FK的修正向量，不是从当前实测位姿算起的整条TCP轨迹长度**。这条轨迹还包含之前命令的到位残差，仍受既有fine solver的4mm总span/0.02rad姿态/联合FCL约束。未将1mm命令增量误报成1mm实际位移门限，物理结果待定。

## 第三阶段 POST — 首件物理PASS，整体仍PARTIAL

`rear_open_xyz_cube01` /runtime39f1a0c/repro7b61780/binaryefb1d133…；普通零预置first1/max1/scale5/hold0。后杯OPEN两次精调norm2.196→1.201→0.205mm（总微轨迹span3.178/3.200mm、每次命令增量≤1mm），之后后杯/侧杯闭合。实际X16/Y16全部完成、主从互换时未释放，最后双OPEN、局部退出/共同HOME、controller0。

最终中心误差0.303mm，deep gap0.212mm，side gap0.216mm；35条打印几何与精确同一步PhysX匹配，日志舍入差max0.0004966mm/deg。8470 held记录完整性0错，**仅该持件记录窗口**未发现机器人-三墙非零contact，CONTACT/实际X/Y峰raw revolute effort46.669Nm，低于保留80Nm；不是校准TCP/吸盘D6内力。26166atomic/4361sparse/4524release有效记录，采样错0。

测试结束后停止自有headless/MoveIt：Isaac0，MoveIt launch0但move_group关闭-11、joint bridge1，BUG004保留；不能把这些清理错误当控制器失败或称软件完全无缺陷。原模型/材料/L工具/几何/ACM/几何与effort门限不变。前面的负结果全部保存；一次首件不是后四件、GUI、多次稳定性、TASK01基准冻结或P2/P3方法复现证明。

下一步：同一源码/binary，fresh零预置first1/max5/scale5/hold0，验证前三新双吸附以及后两原精准单rear连续执行；失败即停止后续Cube，不改变场景/物理/保护来换PASS。TASK01 IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。

## 第四阶段 PRE — 第三件侧臂高位的只读目标诊断

full01 fresh零预置五件在batch1/2实际通过后，Cube03后杯OPEN residual1.542→0.549→0.002mm、rear已闭合而side仍OPEN；其后`DUAL_SIDE_HIGH`8次RRT均无合法goal sample、controller1安全双OPEN停止，Cube04/05未执行。不是新Y力矩失败，也不能从有限采样断言目标物理不可行。

Goal: 区分固定rear构型挡住side goal和单臂高位目标本身不可行。Paper method: 不改变协议，不实施P2/P3。Scope/files: 仅现有无命令probe增加精确实测14关节/Cube pose参数输入与本地KDL/FCL候选/碰撞对输出；读取原MoveIt参数和world、不构造Arm、不发布机器人/吸盘/供料/导轨、无远程Scene/ACM写。Validation: source finite/bounds、完整原机器人/世界FCL、有限不同IK种子；保留0合法候选结果，不叫全局不可行或物理成功。Risks: 此为安全释放后的静态重放，不等同失败时全速动态碰撞；原NVIDIA/URDF模型差异未消失。Need user confirmation: no（只读工程诊断）；模型/物理/成功门限改变则停止另问。

## 第四阶段 POST — 相同rear TCP有可用的另一冗余构型

`full01/raw/side_goal_probe.log`及`rear_goal_search.log`：精确输入来自第三件最后rear CLOSED/side OPEN的held同一步46343/stamp772383373616（不是拿释放后的姿态当失败瞬间）。当前rear固定时60/60 side HIGH IK解都出现left side suction ↔ right link5碰撞；个别解另碰-Y墙。此为MoveIt原模型的有限采样证据，不是全局不可行证明。PRE中“安全释放后重放”应理解为诊断运行发生于安全停止后，而输入来自以上持件记录。

保持该rear TCP变换，有限40个不同rear IK种子在前7个有效IK解中找到3组rear-at-park、side HIGH、side CONTACT终点都完整FCL自由的组合（attempt2/5/6）。未改变Cube/吸点/工具/墙/ACM，probe0；只证明终点组合存在，尚未证明RRT连接、连续下降/X/Y或PhysX实际成功。probe构建52.7s通过；二进制SHA256 `a44623250ca993463090436e1d080277e4025d846a1a53db29942f36246b4117`。两份日志保留，60采样碰撞次数会随KDL内部随机性变化，不能作受控可靠性或因果A/B统计。

## 第五阶段 === PRE-TASK REPORT === — rear候选纳入新的双臂链

Task: TASK01 / BUG021；Goal: 防止仅通过旧solo推入预检的rear冗余构型被选中，随后堵住侧臂HIGH。
Paper method understood as: 不实现P2/P3；已批准前三rear+side主从互换/后两精准单rear不变。
Scope of this iteration: [ENGINEERING]纯软件、吸附前候选筛选，先确认same candidate rear固定时side HIGH、连续CONTACT下降、联合X/Y及退出预检；保留原现场执行时再次规划/检查。局部IK插件来自当前MoveIt参数，不硬编码/改插件。
Files expected to change: runtime独立fixture include/主文件仅新节点宏下调用/无命令probe共用验证；测试、结果元数据、本报告与六记录。
Validation plan: 编译、原61Python/C++、精确Cube03负姿态拒绝与替代姿态只读链；通过后fresh原场景零预置物理回归，保存每件完成与失败、同一步几何/contact/DOF；不将endpoint或只读PASS称物理PASS。
Known ambiguities / risks: 有限候选未找到并不证明不存在；HIGH终点可行仍可能RRT连接失败；原NVIDIA/URDF碰撞模型差异/实际到位残差未消失。
Need user confirmation: no（既有RRT候选联合可行性工程筛选）；任何场景/物理/ACM/原门限或论文方法更改则另问。

第五阶段软件POST：runtime `a3fceab8e368c73a39f3ad9c1b54bc8d3dad31c1`，仅新前三将过时solo PUSH/RETREAT候选筛选替换为已批准dual链，后两/旧节点不变。联合gate拒绝记录的blocked rear（60IK/0HIGH_free），替代attempt4/5/6的连续CONTACT下降、同进度X约330mm/Y1mm、30mm短退出全部full FCL/relative TCP通过，probe0。HIGH从park的RRT连接依旧必须现场验证，不被这份纯本地gate豁免。

第一次联合probe无命令启动exit1，因为参数名筛选只认robot_description_kinematics.*，实际MoveIt使用left_arm.*/right_arm.*；有界读取适配实际布局后复测成功。当前双组实际参数均为`lma_kinematics_plugin/LMAKinematicsPlugin`（基于KDL ChainIkSolverPos_LMA），不是硬编码更换KDL插件。原diag日志/失败原样保存。probe构建53.0s/修正build通过，controller构建52.2s/再检查0.41s，61Python与两组C++严格编译通过；C++第一次临时目录不存在导致harness失败，改用已有runtime artifacts下mktemp并set-e重跑通过，不称首轮编译通过。benchmark analytic 36nulls/DRAFT。

联合gate实测probe binary `f5143152ddb33fd5be81d27357469aebe4053b7fdb1d13de5168d74255c8922e`，是ebddf6d工作树中上述新增gate；最终a3fceab只再修正probe总结标签（连续链不再写endpoint-only），最终probe另编译。production controller binary `174d6ef7ec237967792bf92119f58e50e27629019ae26630859d04c95db072f0`与a3fceab执行源码一致。

物理复测PRE：`results/20261006_TASK01_coupled_rear_full01/`，本机headless原资产/原场景、零预置first1/max5/scale5/hold0、rear45/side-15、原子反馈及同一步held记录。机器人/墙/Cube/材料/原80Nm/原几何门限不变，旧负结果保留；只有controller全五batch完成才能称这次物理流程PASS。启动/运行失败即停后续对象，不预填结果。此为[EXPERIMENTAL]工程回归，不是科学benchmark冻结/论文方法/GUI验收。

### 第五阶段运行记录更正 — full01没有机器人动作

本轮controller启动exit1/命令0，报告local IK configuration unavailable。原headless正常启动并在3600s时限退出0（35998稀疏/215989原子快照，0完整性错），只有自动第一件到料，不能称完成了运动测试。已核对MoveIt六个kinematics参数有效，双组实际LMA；不是场景/URDF或Python选择器故障。

核对binary strings发现production SHA174d6ef7缺left_arm./right_arm.筛选字符串，而成功probe有。其编译开始于include前缀修正之前、link晚于修改，后续增量构建no-op。因此上一段“a3fceab执行源码与production一致”的断言**作废**，只读probe结果不受影响，生产结果不能引用该源码通过。串行`cmake --build build/fr3_dual_palletize --target task01_dual_suction_fixture -- -B -j2`强制重编译，最终核对SHA和参数字符串；重新fresh `coupled_rear_full02`，不覆盖这一启动负结果，也不边改源边构建生产目标。

### full02运行checkpoint — 2/5真实完成，第三关键环节待验

最终串行binary57e72f83与a3fceab执行源、root arm参数筛选一致；fresh场景first1/max5/scale5、READY与hash守卫后运行。batch1/2实际X16/Y16/双吸CLOSED主从互换/释放及短清障RRT到下一件通过，无批间HOME。第一rear pool前4候选被新gate拒绝，5/24通过；第二candidate1通过，rear XYZ2.026→1.031→0.036mm。最新短清障GT中心误差0.302/0.407mm，deep0.156/0.091mm，side0.259/0.397mm；第三已经抓取搬运，但尚未到上一轮side HIGH阻塞环节。不是五件或稳定性PASS，最终同一步数据审计等待正常flush。

### 第五阶段 POST — 前三实际推压完成，第三空载handoff仍FAIL

full02 controller1/headless0，batch完成[1,2]，实际放置三件但第三后续handoff未完成。前三各X16/Y16全部双CLOSED、互换角色未释放；第三实际HIGH/CONTACT/X/Y跨过先前阻塞。短清障后的中心误差0.302/0.407/1.343mm，deep0.156/0.091/0.087mm、侧/邻缝0.259/0.397/0.160mm。第四第五无机器人命令。

第三释放/6.3mm短清障后RRT3次无解；26.9mm清障后左右各3候选，代码只选各最短，后验FCL在左路径t0.610s拒绝left_fr3_side_suction↔task26_cube_3，depth0.329mm。该路径没有执行，不通过扩大ACM/缩小Cube/原路长退出掩盖。几何105条打印与同一步真实反馈精确stamp匹配，最大舍入差0.0004991804mm或deg；36469held/51175atomic/8529sparse0完整性错，release501。CONTACT/X/Y原始关节effort峰46.019/48.571/37.297Nm，该窗口机器人-墙非零pair0。COMPLETE标签覆盖空载及下一件接近，其中接触数据仍保留，**不声称全流程无实体接触**。

### 第六阶段 === PRE-TASK REPORT === — 空载handoff有限候选与一致起点

Task: TASK01 / BUG022. Goal: 严格碰撞检查后短清障→下件预吸位，避免只选最短再整池失败。
Paper method understood as: 用户已批准3+2，不实现P2/P3；[ENGINEERING]候选和起点一致性。
Scope/files: 新fixture宏内共享helper与无命令probe/依赖、结果/本报告/六记录。第一臂从单份完整实测state规划、逐候选完整FCL；第二臂以第一臂预测终点及自身原起点规划/验。保持每个起点3次/每次3s，候选失败不命令。使用现有/move_action的plan_only请求局部完整scene，不写远程world/ACM，不是冻结的Task22背景沙箱预规划。
Validation plan: 精确full02最终bothOPEN 14关节/三落位Cube重放；确认远程world前后不变、CLOSED/碰撞起点拒绝；数值/限位/adapter起点/原目标约束及完整联合FCL；串行构建和原测试后再fresh真实回归。
Known ambiguities/risks: 不控制LMA/OMPL内部RNG；有限候选不等于全局结论；原USD/URDF碰撞模型差异仍存在，只读PASS不是PhysX/GUI/五件稳定性或基准冻结。
Need user confirmation: no（工程修复）；模型/物理/ACM/门限或科学方法改动另问。

MoveIt2 Humble官方实现：plan_only分支通过copyPlanningScene(planning_scene_diff)规划，区别于planAndExecute；[源码](https://github.com/moveit/moveit2/blob/humble/moveit_ros/move_group/src/default_capabilities/move_action_capability.cpp)。运行依旧调用本机安装MoveIt2，不下载/替换算法。

### 第六阶段首轮只读负结果与软件范围补充

request-local /move_action重放probe SHA13d8ea50、build55.6s：CLOSED/碰撞起点拒绝、remote world前后完全相同均PASS，但3次左RRT全被MoveIt自己的planning_pipeline拒绝，错误明确写postprocessing后Cube03/深墙碰撞。停Isaac后的current-state时戳等待警告保留；请求起点是明确保存的14q，不将警告当根因。probe1，无机器人/吸盘/导轨/供料或远程Scene命令。首编译probe调用main-local槽位lambda失败，改用同一原A/B常量重建；负记录不覆盖。

补充工程范围/验证：只在OPEN转场的当前控制器进程内调用同一本机MoveIt OMPL插件，复制原配置（读RPC）、本地加密longest_valid_segment_fraction至0.0005，不更改全局/move_group参数或启动额外沙箱服务器。原RRTConnect/IK/世界/ACM/目标/0.12速度加速度比例不变，加载链仍用原MoveIt管线。空载用保持每个关节路点逐值不变的IPTP计时、原0.01s完整FCL；若改变路点或adapter起点则拒绝。无命令探针对同一原始RRT路径做raw/defaultTOTG/IPTP对照，先获得证据，不能仅凭日志推定TOTG是唯一根因。这是[ENGINEERING]数值碰撞检查/计时，不是论文算法替代或benchmark值变更；物理/model修改另问。

### 第六阶段软件POST / 真实复测PRE

runtime `f237cff`，production串行build56.2s/SHA812c71eeab695c02d992ce4c16569c951e390a296b8429d655ef40bdc1ab9ef3；最终probe在同一clean commit上另串行build59.5s，SHAa33c7565b5e2c443ec523519215afe2d9293a23303cf8c5e9f963f27e737de20，probe03实际exit0。精确snapshot来自full02最后同一步51290/stamp854833377916，两杯OPEN；14q/三7D姿态与原raw逐值核对，无四舍五入，不能说它是被拒绝轨迹t0.610s的碰撞姿态。

same-start FCL11次、选中左491/右469次，安全pair、CLOSED拒绝、obstruction拒绝、remote world序列化严格前后相同全部PASS。有限3+3候选各numeric/start/原goal/bounds检查通过；第二臂预测partner及执行前实测partnerFCL为新节点特有，后两的空载转场也受保护，但其加载单rear插入不变。对6条同raw RRT路径raw/defaultTOTG/IPTP均安全，**不证明TOTG是唯一根因，也非受控RNG的resolution A/B统计**。最初action负日志与中间probe02仍保留，最终probe03消除未执行main后来变动的二进制/源码不一致边界。

61Python/两C++严格编译/PASS、analytic36nulls/hash、scene/bridgehash及diff检查通过。本轮仅软件工程PASS，物理总任务仍PARTIAL。fresh `results/20261006_TASK01_empty_handoff_full01`原stage、零预置、普通供料first1/max5/scale5/hold0/side-15/rear45、原子反馈+held/release记录，READY+exact productionSHA后启动。本机headless不是用户GUI；原模型/物理/ACM/80Nm/几何gate/YAML不变。待实际五件完成与同一步审计后才更新结果；失败立即停止后续物体，不能用只读成功替代实际任务。
