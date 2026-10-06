# TASK01 — 持件几何的原子 PhysX 反馈

2026-10-06，IN_PROGRESS；不是论文控制律/基准冻结。

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
