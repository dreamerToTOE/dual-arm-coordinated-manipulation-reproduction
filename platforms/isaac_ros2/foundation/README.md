# Accepted Task26 foundation — minimal in-place adapter

TASK01 基础场景可行性 PASS CANDIDATE 已由用户接受；正式科研 Benchmark 仍未冻结。
工程来源为 `631b1f` + 已明确批准的 `5ed0c96`，不是未修改的 pin。

本目录只校验已验收本地文件 hash 和转换旧快照，**不会加载场景、启动 ROS、
发布关节/导轨/吸盘命令，也不会复制或重新实现抓取、重抓、推进代码**。
原 GUI → scene → Play → bridge → MoveIt → Task26 链继续作为唯一成熟执行路径。

仓库根目录运行以下纯离线转换；不需要 Isaac GUI：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
python3 -m platforms.isaac_ros2.foundation.legacy_task26 \
  --legacy-root /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation \
  --snapshot results/20261009_TASK01_predecessor_patched_runtime02/final_snapshot.json
```

输出 `task02.state.v0.1` JSON，包含完整两臂 14q、两臂速度、base/TCP、四件显式
Prim 身份（包括原休眠件）、rail/SG/bridge 诊断和来源 hash。
`native_articulation` base 与 `legacy_USD_feedback` Cube/TCP 分开标记。
轨道 X 不自动等同于 `world_shift_x`；SG CLOSED 不等同于 attachment identity。
未测得 collision distance、wrench、carriage frame 等字段明确列为 unavailable。

旧快照缺少同一 post-step 的物理 step/stamp，因此 `simulation_stamp_ns=null`、
`physics_step=null`、`post_physics_step=false`。Timeline 与 ROS clock 仅作诊断保留。
科研输入检查必须调用 `ObservationClock.require_scientific_timestamp()`；此类旧快照
会被拒绝，而不能进入正式跨算法评分。局部文件 hash 仅证明本地资产字节，
不能反向证明历史快照的来源或为旧反馈增加真实性。

适配器保留原坐标与数值，不重命名世界坐标、不换算 rail 规划偏移、不加尺寸/质量
默认值、不导入旧成功容差、不生成安全或动力学结论。

TASK02-B 的 `legacy_events.py` 薄适配器只把旧TaskEvent/TaskStageMarker字典转换为
明确trajectory ID的PLANNED相对ns事件/阶段（编码舍入≤0.5ns，不是物理验收容差）。
它不把计划或SG状态转换成实际ATTACH，不访问运行中Isaac，不改变成熟执行链。
[统一数据/日志接口](../../../common/README.md)及[离线报告](../../../reports/TASK02_EXCHANGE_LOGGING01.md)。

实时 post-step 数据绑定另作明确的软件集成切片，不重启旧 TASK01 probe 或扩大到力控。
