# TASK01：完整旧流程通过后的基准阻塞评审

状态：**PARTIAL / 待用户方向确认。旧流程调通不等于 TASK01 PASS/FROZEN。**

本次按“继续直到调通”完成了实际机器人测试，而不是只做规划。没有修改保护目录、几何、质量、摩擦、吸盘断裂阈值或 ACM，也没有开始 TASK02/论文控制器。

## 已完成的工程验证

- 正常连续供料、没有预放前四件：五件都完成搬运/推入，controller exit=0，两臂回 HOME。一次未固定 OMPL seed 的完整回归，不是可靠性统计。
- 预吸附微调修复保留原 0.300 mm gate / 三次停机；第一件左右 gap 差 0.447 → 0.001 mm，第四件 0.973 → 0.296 mm。
- 第五件 controller settle center error=0.493 mm；随后最后 PhysX 样本=0.563 mm。四件 fixture 后续 center error=1.669/2.276/0.574/0.615 mm。
- 70,434 个同一步快照，完整性错误=0。实际物理 dt=0.0166666675359 s。
- 最后 18 项 Python 离线测试、9 项 C++ residual assertions 和相关 ROS package build 通过。真实 link8 incoming fixed joint 的子端 anchor=0、axes=identity 已核验。
- 可选 task-thread 7-s hold 保持 ROS executor 工作，CLOSED / 后续搬运 / Cube01 / HOME 均通过。失败的 SIGSTOP 试验仍保留，不掩盖失败。

来源、完整启动/编译命令、原始日志位置：
[完整五件报告](TASK01_FULL_FIXTURE_CONTACT_PROBE.md)、[上游修补来源](../platforms/isaac_ros2/legacy_patches/README.md)。本轮 legacy branch=`task01-runtime-fixes`，普通完整回归=d80b6b6，可选静载 hold=76408c8。

## 阻塞一：实际前四件流程没有实现 D004

源码及逐六步 contact-topology 审计一致：向深墙推进时 helper 停放；外件随后用未吸附杯面侧压；内件做 rear 单臂 trim。前四件 rear+side 同时 CLOSED 的采样数均为 **0**。

这与用户规定的 rear 主推 / side 吸附约束、到深墙后交换主从不同。因此不把 5/5 旧 demo 误报为协同 fixture PASS（BUG-009）。

### 当前侧吸姿态还有实际工具干涉

只读载入现有 xacro box collision 几何，用完整回归的真实 Cube03 结束位姿计算 Cube04 右 helper 的面中心侧吸目标：

```text
Cube04 center       = (1.100, -0.1215, 0.260) m
required +Y TCP     = (1.100, -0.0605, 0.260) m
link8 origin        = (1.100, +0.0945, 0.340) m
lateral rod center  = (1.100, +0.0295, 0.260) m
rod length          = 0.130 m
Cube03 near Y face  ≈ +0.060976 m
```

在现有 sidePose(right) 下，横杆和竖杆均与 Cube03 相交；横杆最小 SAT 轴投影 overlap=**33.524 mm**。这是精确 OBB 相交证据，**不是 PhysX penetration depth**。没有扩大 ACM 或忽略 Cube，也没有发送机器人命令。

后续按用户“继续”补做只读 roll 扫描：吸点中心/杯面法向保持不变，绕 TCP +X 从 0° 至 345°、步长 15° 的 **24 个姿态全部存在横杆-邻 Cube 相交**，box-clear 候选数=0。新增单测验证杆中心沿法向的相对位置不因 roll 而移动。无机器人命令。

边界：离散 roll 结果不是连续姿态/任意接触顺序/IK 的穷举证明。无碰撞的替代接触策略或修改教师确认的 L 工具，需要显式评审，不能悄悄把面中心吸附改成边缘/半吸附。

命令与结果：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
python3 platforms/isaac_ros2/probes/audit_fixture_tool_clearance.py \
  --xacro /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/urdf/dual_side_suction.xacro \
  --physical-analysis results/20261003_TASK01_full_five_corrected_01/analysis.json \
  --roll-sweep-step-deg 15 \
  --output results/20261003_TASK01_fixture_protocol_clearance/roll_sweep_summary.json
```

## 阻塞二：源码声明的摩擦未实际生效

最终启动审计同时查 physics-purpose/all-purpose binding，并直接读取 PhysX shape material properties，避免把源码常量当物理实测：

- Cube 实际 mass=**0.800000012 kg**。
- 五件 Cube shape 的实际 `(static friction, dynamic friction, restitution)` 均为 **(0.5, 0.5, 0)**，不是草案来源常量 `(0.90, 0.75, 0)`。
- Cube/Table/三面墙的两种 purpose 均未解析到有效 material binding。
- 源码先 `_make_material()`，随后 `_build_objects()` 删除 `/World/Task27`，而材质就在该任务根内；删除后未重建（BUG-012）。没有把现在的 5/5 倒推成 0.90/0.75 材料下的成绩。
- 前两次审计未读实际 shape coeff；第一次还用了错误工具路径，均保留 PARTIAL 记录。第三次才验证真实 `fr3_link8/side_suction_tool` 及 backend 系数。

修正材质生命周期将改变实际摩擦，必须决定继续使用实测 0.5/0.5，还是恢复声明的 0.90/0.75 后重新验证。不能用修复后的成绩覆盖当前历史记录；pairwise combine rule 仍须单独验证。

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_full_fixture_headless.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --verify-only --duration-sec 45 \
  --output-dir results/manual_TASK01_material_audit/raw
```

## 阻塞三：FR3 TCP 动态接触力尚未标定

受控 hold 的 238 个完整物理步（剔除起始 1 s）：

| 诊断 | 实测 |
|---|---:|
| 双臂补偿后平均承重 Z | 7.847884 N；解析值 7.848 N |
| 平均力向量误差 | 0.000370 N |
| 瞬时力误差 RMS / max | 0.494278 / 0.526523 N |
| Cube 中心平均力矩残差 | 0.014902 Nm |
| 瞬时力矩误差 RMS | 0.039022 Nm |
| tensor linear speed RMS | 0.012773 m/s |
| 相邻位置差分 speed RMS | 0.000505 m/s |
| tensor 与位置差分速度误差 max | 0.013163 m/s |

力信号近逐步交替；原每六步抽样产生约 0.498 N 的假 DC 偏置，已改为完整物理步，分别报告均值和瞬时 RMS，单测覆盖交替序列。**平均承重准确不能证明瞬时力矩或各吸盘内力准确。** 位置仅微米量级变化与 tensor 速度不一致的根因尚未证实；不能只凭 CLOSED 或 hold 标签宣布静力平衡/接触 estimator PASS（BUG-011）。没有调宽标定 gate、滤掉峰值来伪造通过，也没有动惯量/solver。

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py' -v
python3 platforms/isaac_ros2/probes/analyze_full_fixture.py \
  results/20261003_TASK01_fr3_static_payload_v2/raw \
  --output results/20261003_TASK01_fr3_static_payload_v2/analysis.json
python3 scripts/validate_benchmark_candidate.py
```

## 冻结/后续边界

`benchmark_v1.yaml` 未改，36 个 null / numeric model review 仍未批准。`forceLimit/torqueLimit=1e6`、隐藏支路 1.946277 kg 和混合时钟也未默认为批准。MoveIt teardown 再现 exit=-11（BUG-004），操纵 controller 与 Isaac 已停止，没有遗留 paused robot process。

需要用户选择：是否允许修复失效材料并以明确材料版本重测；侧吸面中心保持不变时，是否允许研究 L 工具/接触顺序调整。得到方向前，不做模型/协议偏离、不冻结基准、不启动论文方法。

标签：无 [ORIGINAL] 论文实现；[ADAPTATION] 真实 FR3/Isaac 测量映射；[ENGINEERING] 有界预吸附修补/采样/诊断；[DEVIATION] 识别并记录旧流程偏离 D004，未认可为替代协议；[EXPERIMENTAL] 普通五件/独立标定/受控 hold/几何审计。
