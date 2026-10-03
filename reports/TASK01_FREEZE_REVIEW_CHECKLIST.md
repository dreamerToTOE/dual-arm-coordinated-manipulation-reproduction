# TASK01 冻结前评审清单（2026-10-03）

状态：**PENDING，不是用户数值批准，不修改 benchmark YAML。**

草案仍有 36 个 null，SHA256 `a49d60a4dc6a8a00c3bf55a512113af50760968827a8cefe64dae1c7de55fde8`。后续修正版正常五件已实际完成；早期 Cube02 停止作为历史失败保留。FR3 TCP wrench 尚未标定，不能由“旧流程完成/平均承重正确”自动填入控制/安全门限。

最新 [运行与评审报告](TASK01_RUNTIME_REVIEW_20261003.md)：真实 link8 固定 joint 帧已核验，但 D004 contact topology / 当前侧吸工具干涉 / actual friction 0.5/0.5 vs declared 0.90/0.75 / 瞬时 wrench 与速度契约仍未解决。以下 36 项保持候选，不偷偷按现有 demo 默认数值冻结。

## 接口方向（待评审）

- [ENGINEERING] pose/contact/TCP 使用同一 post-step 的 simulation stamp/step；公共消费者统一 use_sim_time，控制事件映射仍须验证。
- [ADAPTATION] world 右手系、m/N/Nm；carriage_entrance 候选 `(0.910, 0, 0.200)`，+X 推入/+Y 宽/+Z 上。
- [ENGINEERING] collision wrench 与 suction/mount raw reaction 分开命名；真实 joint axes/anchor、重力/惯性和 TCP moment shift 标定前不称接触力。
- [EXPERIMENTAL] 候选继续检查 60 Hz physics + 10 ms command；60/120 Hz 独立校准不等于批准更改场景 dt。
- 前四件夹具构造与第五件单臂插入分别统计；左右 pusher 分开报告。

## 36 项逐项清单

所有字段均未冻结。A=`benchmarks.A_tight_transport`，B=`benchmarks.B_constrained_insertion`，F=`B.fixture_preparation_cubes_01_to_04`，C=`B.center_cube_05`。

| # | 字段 | 处理建议 / 缺口 |
|---|---|---|
| 1 | robots.rail_pose_at_benchmark_a_start_world_x_m | 保存稳定 CLOSED 初态的两轨道位置，不用途中的 rest pose |
| 2 | robots.rail_pose_at_benchmark_b_start_world_x_m | 定义 PRE_PUSH 固定轨道初态，与 A handoff 一致 |
| 3 | cube.effective_contact_material_rule | 审计双方材质和 combine mode，不只写 authored friction |
| 4 | A.initial_cube_center_world_m | 候选正常供料点；先验证稳定双吸初态，不用失败的 Cube 02 状态 |
| 5 | A.initial_robot_joint_state_rad | 保存相应全部关节/轨道，明确 seed/映射 |
| 6 | A.final_pose_tolerance_m | 从新测量提出统一 gate，不能逐方法调宽 |
| 7 | A.final_orientation_tolerance_rad | 先迁移错误旧 quaternion 消费者 |
| 8 | A.max_relative_tcp_error_m | 同一步相对 SE(3)，不用异步双 topic 差 |
| 9 | A.timeout_s | 分开规划/执行/settle 时间，先完成完整链 |
| 10 | F.initial_staging_safety_tolerance_m | 保留粗安全暂放，不用精确暂放替代双臂推压 |
| 11 | F.dual_contact_force_policy | rear 主推/side 约束及互换需载荷标定，不是 collision force 单通道 |
| 12 | F.fixture_final_pose_tolerance_m | 正常四件实测，区分 center error 与有向 face gap |
| 13 | F.fixture_settle_policy | 建议仿真时间的连续 pose/velocity 稳定窗口，需验证 |
| 14 | C.pre_push_lateral_tolerance_m | 与 1.5 mm 每侧间隙联立 yaw/接触 margin |
| 15 | C.pre_push_yaw_tolerance_rad | 1° yaw 消耗约 1.038 mm 侧隙；旧 yaw 不可用 |
| 16 | C.pre_push_x_tolerance_m | 固定 PRE_PUSH 与插入深度的同一 frame 误差 |
| 17 | C.pusher_arm | 建议左右对称子试验，具体策略待批准 |
| 18 | B.final_pose_tolerance_m | 与四件 fixture gate 分开，明确参考点/面 |
| 19 | B.final_orientation_tolerance_rad | 用归一化物理 quaternion 检查夹缝内角度 |
| 20 | B.max_contact_force_n | 不从 139 N 瞬态倒推 gate；先力通道/安全依据 |
| 21 | B.jam_detection_thresholds | 力+推进速度+持续时间，待测量与基础链完成 |
| 22 | B.timeout_s | 成功插入阶段时间统计后固定，同方法共用 |
| 23 | B.cases.C1_small_lateral.lateral_offset_m | 从冻结 C0 margin 内选小扰动，先不猜数值 |
| 24 | B.cases.C2_larger_lateral.lateral_offset_m | 更大且有明确接触/恢复解释，不与 C1 重合 |
| 25 | B.cases.C3_yaw.yaw_error_rad | 用有向 clearance 计算正/负 case |
| 26 | B.cases.C4_lateral_and_yaw.lateral_offset_m | 与 yaw 联立，记录是否几何阻塞 |
| 27 | B.cases.C4_lateral_and_yaw.yaw_error_rad | 同上，不偷偷改车厢宽度 |
| 28 | B.cases.C5_contact_perturbation.friction_scale | 审计 combine rule 后定义 |
| 29 | timing_and_trials.physics_dt_s | 候选 1/60 s；场景显式设置/测量并批准后冻结 |
| 30 | timing_and_trials.ros_time_policy | 建议 simulation clock；现有 wall time 需迁移验证 |
| 31 | timing_and_trials.seed_policy | 分别固定布局/扰动/规划源，旧 OMPL 未固定 |
| 32 | timing_and_trials.seeds | 定 seed 列表及 tuning/test 划分，待评审 |
| 33 | timing_and_trials.trial_count_per_case | 调试与统计预算分开；3/3 非可靠性结论 |
| 34 | timing_and_trials.tuning_budget | 共用搜索/运行预算，不无限重试 |
| 35 | measurement.contact_wrench_interface | 已验证 collision + 待标定 mount/TCP，不用 effort 冒充 |
| 36 | measurement.collision_distance_interface | FCL nearest/signed distance 独立接口待建；碰撞 PASS 非最小距离输出 |

## null 之外仍需评审

近不可断吸盘 `forceLimit/torqueLimit=1e6`、隐藏支路约 1.946 kg 质量、grasp nominal gap、初始 joint state、车厢 TF 和扰动协议不能因不是 null 就视为批准。删除质量、改吸盘断裂策略/几何会改变物理，须记录并获批准。

后续顺序：用户确认材料/中心侧吸可达性方向 → D004 实现与实际物理验证 → FR3 补偿/时间契约 → 安全/扰动/试验预算提案 → 数值评审 → TASK01 FROZEN → TASK02。微调过冲修复和普通五件回归已完成，不重复冒充下一步成果。
