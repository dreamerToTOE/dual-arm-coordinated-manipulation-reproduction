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

## 第二阶段 PRE — 后推杯面法向腕姿只读候选

## 原子反馈实测 POST（第一阶段，PARTIAL）

新鲜本机headless首件 / runtime88ef454/reproa952a18/binary31d862a6… / first1,max1,scale5,hold0,零预置、原side roll -15。

- 同步反馈启动有效；25171快照/0采样错，9491 held与4195稀疏记录0完整性错。33条打印几何按**精确仿真时间戳**匹配同一步真实记录，所有差仅日志0.001精度舍入（max0.00049987mm或deg），不按墙钟近似对齐。
- X16通过、Y14通过，原子gap没有X3假负值。源对照X9–11原USD rear最小-1.622/-1.631/-1.755mm，对应相同物理源rear均正，最大差3.055mm；证明USD源可使原门限误判，但不等于已经逐个重建上一轮ROS三个latest的接收顺序。
- Y15原80Nm保护停止：left86.999/right70.170，atomic_feedback=FRESH。真实right link7↔+Y墙峰745.807766N/step19613。双OPEN、controller1/完成0、headless正常停止0；不是反馈超时，不是论文内力或吸盘wrench。
- 原side roll只解决名义deep-wall检查的范围。补查旧nominal02双腕1330节点对三墙：deep0/minusY0，plusY有7个右腕Y节点交集；LP共同球半径不是穿透深度。此前deep-only PASS绝不能推广为all-wall PASS。
- 60Python/C++策略检查PASS，旧scene/bridge/YAML hash不变。新反馈消费工程得到实测支持，但完整任务仍FAIL，BUG017/019仍OPEN，不能冻结基准或推进论文方法。

下一步第二阶段仅no-command后腕roll候选与三墙检查，执行器尚未应用。

实测原子反馈首件完成X16/Y14，Y15出现rear right link7↔+Y墙接触，原80Nm保护停止。只读尝试rear绕worldX法向45deg，正Y件正转/负Y件镜像负转，目标是把后腕偏向中央空区；side仍worldY -15deg。中心/法向/L几何/原接触点与桌/墙位置不动，没有载荷下旋转或执行器自动启用。

验证：名义前三链全FR3 FCL/TCP约束、输出精确双腕FK，同时检查原USD link7凸包对三面墙（此前deep-only检查不足）。失败保留、不放宽门限；只读PASS不替代真实物理/空载接近完整验证。
