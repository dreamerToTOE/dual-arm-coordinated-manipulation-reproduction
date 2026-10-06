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
