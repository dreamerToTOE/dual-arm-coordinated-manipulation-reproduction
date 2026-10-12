# TASK06-IS-B0 — 任务前报告与只读路径审查协议

2026-10-12；基线 f0a57c289b67f187fe8fd2161c15a594c7402a7c；
分支 task06-is-a-p4-scene-adapter。用户接受 A 无执行适配初步验收，
没有批准仿真执行。这是新独立审查，不追溯更改 A 的结果。

## PRE-TASK REPORT

- Task：TASK06-IS-B0，固定离线路径的执行前安全审查。
- Scientific objective：判断已保存 P4 空间路径是否具有足够的执行准备证据。
- Minimum sufficient evidence：14 关节逐项最小限位余量/累计行程/邻接/反向统计、
  完整曲线；保存的闭链及离散 FCL 来源复核；旧执行通路、限速/限加速度、
  到位门禁、持件与实际起点对齐审计；明确满足/不满足及缺口。
- Scope：固定 JSON/原生限位和已有日志源码的只读审查，纯 Python 数值分析和图表。
- Non-goals：重新规划/IK/投影/FCL 查询，时间轨迹构造，Isaac/ROS 服务/控制器，
  实际状态采集/命令，修改 Task26/P4/场景/ACM/物理/端点/原结果/Benchmark。
- Attempt budget：一次固定数据审查，软件单元测试和一次正式分析输出；没有科学
  搜索或物理尝试预算。任何输入不一致即停，不造替代路径或新执行器。
- Preferred：读取 saved path 与独立逐点记录，复用原限位/门限/旧执行源码及日志。
- Fallback：证据不充分则“执行准备条件不满足”，保留具体缺口，不自动修复。
- Stop/escalation：路径/来源哈希不一致、记录不对应、需要实时验证或改变标准。
- Files expected：本协议、新纯分析脚本/合成测试/结果 CSV JSON 图表、最终报告，
  STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK 和入口任务卡。
- Validation：输入 SHA 前后不变，逐点 q/闭链/限位/邻接与已存验证一致；合成数学
  回归；原数据、模型、Benchmark、旧工程 source 不变；图表与表格来自同一结果。
- Risks：离线名义 q 不是实际持件 q；末端到位门禁不是全路径跟踪误差上界；
  两件工程成功不是本 P4 路径执行资格；没有时间意味着不能求速度/加速度。
- User confirmation：授权范围内不需要；任何重规划/物理/标准决策须另行审批。

## PRIOR-ASSET CHECK

- Scientific algorithm：TASK03–06 P4 数学/投影/局部连接/双树保持不变，不重实现。
- Old areas：Task26 Arm/executeSync/interpolate/ensureTiming/retime 与 bridge，
  description 限位配置、共享物体同步器及旧两件 physical.log。
- Pin：631b1f65656d025c1bb2173e874192f3fe4d355a；批准的 controller 小修 5ed0c96。
- DIRECT_PORT：TASK02 轻量 RunLogger（只写本轮文件，不绑定命令）。
- THIN_ADAPTER：保存的 JSON 读取/数学诊断；仅为只读报告，不接执行接口。
- TEST_ORACLE：A 的逐点/树边 FCL 与闭链记录、原生限位、旧执行器源码/日志。
- REFERENCE_ONLY：旧时间参数化/吸盘/导轨/Bridge 作为能力与缺口审计，不运行。
- Rejected：普通 MoveIt 重规划、第二执行器、独立双臂 TCP 重采样改变固定14q路径，
  用旧成功日志冒充新路径动态误差认证。
- Reused files：qualified_joint_path.json / independent_path_validation.json /
  planner_seed7.json.gz / metadata/native manifest 与固定旧 Task26 source。
- New files：工程分析和图表，不是新运动学/碰撞/控制模块。
- Fidelity risk：把工程审查误写成 P4 连续安全或物理通过；报告明确禁止。
- Need user decision：只在交付后决定独立路径改进或后续执行授权。

## 预声明计算规则（工程诊断，非 Benchmark 成功标准）

1. 固定读取 results/20261012_TASK06_IS_A_nominal_scene03/qualified_joint_path.json，
   SHA256 073723b32e4bc392af3fb0a182a03e92e45026771dc1d46fa9b7276b21614781。
2. 每一点/关节 margin=min(q-lower,upper-q)，保留 rad 和 deg、零基 index 与
   一基 point number、原始角和最近边界；不 wrap、不 clamp、不改原 q。
3. 累计行程=sum(abs(q[i+1]-q[i]))；端点位移=q[-1]-q[0]；excess=行程-abs位移，
   ratio=行程/abs位移（位移为0则 null），全关节空间路径长度=sum(norm(delta,2))。
4. 邻接报告每关节 max abs delta 和完整逐边 L2/Linf，不求未定义的运动速度。
   原 TASK05 max_adjacent_l2_rad 与 max_adjacent_joint_rad 门限原样读取核对。
5. 方向反复：原始非零 delta sign 的变化；另输出 abs(delta)>1e-9rad 的过滤
   计数和反转路径点位置。1e-9 仅浮点诊断阈值，不是轨迹/碰撞/执行接受标准。
6. 固定输出最大的10条 L2邻接（同值按 index 排序）与每关节累计行程曲线；
   14条位置+原限位、余量、累计行程+端点直线参照；x轴为点序号/关节空间
   弧长而非时间，不把反向本身当碰撞或数学失败。
7. 所有独立记录必须与固定 path q 相等；复用既有 1e-8m/1e-8rad 闭链及原邻接
   门限，不新调阈值。FCL 只核对既有来源、对象、ACM、逐点和树边资格，不新查询。
8. 不构造时间轨迹：目前限位风险与起点/跟踪资格需要先审查。只研究旧方法
   能力/适用条件；旧粗略 ensureTiming 不能作为本路径动态限值证书。
9. 执行余量条件采用 m_j > E_tracking,j + E_alignment/model,j 的明确误差预算；
   旧工程门禁可作为复用能力参照，不作为已证实的瞬时误差上界。缺上界则
   不满足执行准备条件，禁止事后降低门禁迁就当前余量。
10. 本轮 seed 未设置（无 RNG），simulation time/physics step 不可用；分析耗时
    仅 CPU/wall 诊断，不是执行时间。提交后停止，不自动 B/C/TASK07。
