# TASK06-IS-A — 任务前报告与既有资产复用审查

日期：2026-10-12。基线 `eb8586511419940f1dce8a7e667fffa52a21cf82`；
分支 `task06-is-a-p4-scene-adapter`。本报告在实现及新测试之前登记。

## PRE-TASK REPORT

- Task：P4 现有双 FR3 场景只读适配与无命令离线验证。
- Scientific objective：证明既有场景定义下能否产生一条合格共同搬运路径。
- Minimum sufficient evidence：来源一致的模型/环境/抓取、可确认的起终点 14q、
  原 TASK03–06 合格搜索及独立离散复核；仅加载模型不算规划通过。
- Current scope：静态源码与历史证据核对、薄适配、有限离线软件验证和文件日志。
- Explicit non-goals：Isaac、ROS 节点/服务、控制命令、场景重建、IK 搜索、
  新 FCL/算法/执行器、B/C/TASK07、原 TASK06 障碍专项、Benchmark 定稿。
- Attempt budget：一次固定离线验证。输入缺口不是概率规划失败，不轮换场景/种子；
  仅允许有证据的构建/序列化修正，不能借此重选端点或改变门限。
- Preferred method：原 TASK02 文件契约/日志、TASK03 FK、TASK05 私有 FCL、
  TASK06 NR/RBS 双树搜索。旧文件只读、原算法不改。
- Fallback method：缺少合法端点时保存输入拒绝证据并交付“部分完成”；
  不用历史不匹配构型、四位小数单臂日志、HOME 或新 IK 代替。
- Stop/escalation：来源/模型不一致、端点未确认、原生碰撞/闭链拒绝、
  必须改几何/ACM/阈值或启动实时采集。提交后停止等待审查。
- Files expected：新 adapter/runner/tests、工程协议、对照报告与六项持续记录。
- Validation：只读 Git/源码 SHA256；原 xacro 离线展开对照；真实 MoveIt/FCL
  加载与参数清单；输入门禁和既有纯数学/接口回归。仅端点完整时规划。
- Known risks：旧两件工程成功不等于单 Cube 科研验收；USD/PhysX 时间和
  凸包一致性未认证；源代码命令位姿不等于测量状态；最小距离不可用。
- Need user confirmation：本轮静态/离线实现不需要；补采实际端点或选择新的
  名义端点/IK 构造路线需要单独审查，本轮不自主执行。

## PRIOR-ASSET CHECK

固定旧源码：`dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a`；
批准的两处控制软件修正：`5ed0c967401e5fedb93b938e1c3904f4a4c87600`。
已核对两版本差异仅 controller 的 13 行 diff；scene/bridge/描述未改。

| 分类 | 资产与本轮用途 |
|---|---|
| DIRECT_PORT / 直接复用 | 已验收 TASK03 C/Jc/FK、TASK04 NR、TASK05 RBS、TASK06 双树搜索；TASK02 文件日志，不复制算法 |
| THIN_ADAPTER / 薄适配 | TASK03 `DualFr3Model`、TASK05 `CollisionAdapter` 的原生加载/检查；Task26 静态定义和来源核验输入 |
| TEST_ORACLE / 对照证据 | 固定 URDF/SRDF、Task01 原两件运行日志和快照、原 TASK03–06 报告/失败结果 |
| REFERENCE_ONLY / 仅参考 | Task26 scene/bridge、Surface Gripper、导轨、同步执行器、旧 shared_object_planner / spatiotemporal_conflict_detector；不启动/移植 |

查阅：Task26 scene、bridge 的工具/状态/时间/导轨接口，controller 的
`sidePose`、`cubeObject`、`boxWallObjects`、`tableObject`、共同搬运与落桌阶段；
原描述 URDF/tool/SRDF/launch，旧通用 shared planner 与冲突检测接口。
原通用 shared planner 是顶部吸盘 `.105 m` 适配，不能代替侧吸 P4；其额外
tool–Cube 接触许可不导入。P4 算法已完成，此轮不新增论文方法。

Reused files：`baselines/p4_closed_chain/`、
`platforms/offline_moveit/task03_closure/model_adapter.*`、
`task05_local_connection/collision_adapter.*`、TASK06 evidence、TASK02 logger。
New files：本轮来源映射/输入拒绝薄接口与测试；不新增控制子系统。
Paper-fidelity risk：把场景匹配/两件工程结果当作正式 P4 单 Cube 执行；
把早期历史 q 或拟合抓取冒充新场景实际端点。明确拒绝这些替代。
Need user decision：有，实际搬运端点与持件抓取的补充证据路线；不阻止离线审计。

## 已发现的输入缺口（不是碰撞或规划算法失败）

原成功 `20261009_TASK01_predecessor_patched_runtime02` 保存初始/最终全量快照，
但初始 HOME 与最终 HOME 均双吸盘 OPEN。共同持件阶段只有三位小数 Cube
位置及附件诊断，未保存完整双方 14q/TCP/attachment transform。
四条 `RIGHT_CONTACT final command q=` 为单臂、四位小数、接触前命令，不能代替。

原 Task26 `.500,0,.260` 为供料位；名义共同 LIFT 为 `.500,0,.540`。
`task26_r0_deep.pre_push` 为 `.790,+.060,.260`，但带件短推终点为
`.790,+.060,.280`，随后 `COMMON_DROP_TO_TABLE` 使用 `entry_x=.770`。
因此任务名义预推、带件短推和落桌终点不能混写；本轮不修旧流程。
早期归档 START `[.55,0,.38]` / PRE_PUSH `[.79,0,.26]` 是 D041 前科研设计，
不是已验收旧 Task26 搬运的实际端点。它仅作数学对照，不重新启用。

**当前不满足实际端点输入门禁，科学搜索预算保持未使用。**

## 预声明离线协议

`configs/engineering/task06_is_a_scene_adapter_v1.json` 在实现测试前提交。
只运行一次来源检查、模型加载、输入门禁与既有离线回归。
规划条件：同一来源的 START/PRE_PUSH、完整有序 14q、固定抓取/世界/基座/导轨
一致；不修复端点。条件成立才调用原 TASK06（种子 7/41/20261012，各至多一次，
首条合格即停；600 节点、800 迭代、20 s，原 NR/RBS 门限不变）。
当前两端点 null，因此不得尝试这些种子；不运行原三场景专项。
物理时间/step null；成本仅 wall compute，最小距离不可用，无连续安全声明。
