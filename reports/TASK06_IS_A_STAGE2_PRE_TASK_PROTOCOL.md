# TASK06-IS-A 第二阶段 — 任务前报告与固定离线协议

2026-10-12；基线7bae83a，分支task06-is-a-p4-scene-adapter。实现/实验前提交。
用户接受第一阶段来源/接口/软件回归，**没有接受整体场景规划验收**；
本次另行批准一次独立名义输入及端点候选路线，不能回写第一轮协议或失败。

## PRE-TASK REPORT

- Task：TASK06-IS-A 第二阶段，只读来源核对、名义端点和有界离线P4规划。
- Scientific objective：在固定旧Task26来源世界中生成一条闭链/FCL合格路径。
- Minimum sufficient evidence：世界对象逐项相等；两端点完整14q/TCP/Cube/闭链/
  原限位/FCL合格；原P4生成完整路径且每离散点和连续性独立复核。
- Current scope：独立v2 YAML/协议、最小可配置world输入、现成KDL-LMA候选接口，
  调用原C/Jc/NR/RBS/双树和TASK02日志。
- Explicit non-goals：Isaac、ROS节点/规划服务、控制、真实持件测量、scene/bridge/
  执行器、改工具/模型/ACM/旧结果/正式Benchmark、B/C/TASK07、新IK或FCL引擎。
- Attempt budget：一轮固定软件/来源核验与科学工作进程；每端点最多64对，
  每臂LMA最多500迭代，端点15s；原P4最多种子7/41/20261012各一次/20s，
  首条完整合格即停；总科学进程120s。端点失败停止，不加候选/新seed/新几何。
- Preferred method：原运动学解析器+KDL-LMA直接API（不创建ROS Node），原NR作
  闭链精化，原私有MoveIt/FCL构造及检查，原TASK06搜索，无普通MoveIt RRT替代。
- Fallback method：保存失败分类/构型/完整前缀，部分完成；不启动GUI补采。
- Stop/escalation：来源不一致、FCL不可用、预算耗尽/无端点、所有搜索失败、
  独立路径复核拒绝；不因失败换抓取/模型/端点选择规则或放宽标准。
- Files expected：新v2输入/runner/候选与核对接口/测试/报告/结果；原TASK05
  平台FCL包装器仅增可选world对象ID输入和只读readback，原默认分支保持行为。
  `baselines/`、TASK03 FK/C/Jc、TASK04/05/06门限/算法及原协议结果不修改。
- Validation：来源SHA/xacro等价；旧日志/轨迹完整构型检查；新source world与
  native world readback比较；原离线回归；端点和路径约束/限位/FCL/连续性。
- Known ambiguities/risks：离线名义抓取不是真实SG附件；单个携带研究物体仍保留
  原第二供料件作为静态障碍；旧ros/asynchronous快照仍不合格科研测量。
- Need user confirmation：当前固定授权内不需要；任何预算扩展/物理采集需要。

## PRIOR-ASSET CHECK

- Pinned source：旧631b1f65656d025c1bb2173e874192f3fe4d355a及批准5ed0c96；
  查scene、controller的sidePose/world/cubeObject/held trace、旧launch、描述与H快照。
- Scientific algorithm：本轮不新实现P4；必须保留原NR/RBS双树组合。
- DIRECT_PORT：TASK02日志；TASK03/04/05/06数学和搜索入口。
- THIN_ADAPTER：TASK05原Scene/FCL世界加载（可选来源对象配置）；
  同一URDF经原kdl_parser提取chain，直接调用MoveIt LMA所用现成求解器。
- TEST_ORACLE：固定Task26源码，原URDF/SRDF/限位、历史两件日志和快照，原报告。
- REFERENCE_ONLY：旧scene/bridge/吸盘/导轨/同步执行器；以前geometry probe的
  ROS Node launcher不允许启动，仅原LMA数值/独立pose验收作为工程参考。
- Rejected：截断单臂q/HOME作为端点、旧293q替代、普通MoveIt规划器、夹带旧ACM。
- Newly implemented：小的来源对象映射、有限种子/candidate文件输出/入口调用；
  不实现运动学、逆解公式、投影/碰撞/新控制器。
- Fidelity risk：名义离线数据冒充实测、已有近似工程成功冒充正式论文物理对比。
- Need user decision：当前定义已经用户批准；通过或失败交付后均等待审查。

## 固定世界与端点

`task06_is_a_task26_scene_v2.yaml` 为新输入，不覆盖0.606m历史归档。
内宽0.628m，原task26_table、task24_table及三墙原编号均保留。
**原slot B的task26_cube_2全程作为固定World障碍保留**，不是随结果删除；
这是一个携带对象的研究，不是两件调度。后批Cube03/04按原休眠/规划政策排除。
无新的导轨/标记Collider；携带body保留原task26_cube_1 ID，touch_links=[]，
原SRDF/ACM、zero padding与scale=1不变。

起点COMMON_LIFT完成：Cube=(.500,0,.540)，终点COMMON_SIDE_SHORT_PUSH完成：
Cube=(.790,.060,.280)，两者单位姿态；双CLOSED trace在释放之前。
名义目标直接由旧slotA、lift .280、pre_push .790/.060、release gap .020定义，
不是采样历史物理状态，也不使用落桌/HOME/原科研端点。

## 数值协议（工程标准，不冻结Benchmark）

- LMA epsilon=1e-7，姿态权重.01，maxiter500，joint increment epsilon1e-15；
  原MoveIt插件的KDL backend，直接调用且拒绝越界原始角，无clamp/2π修复。
- 原geometry probe独立pose标准1e-5m/1e-4rad沿用，仅端点FK验收；
  **闭链NR仍1e-8m/1e-8rad**，原40迭代/SVD/限位守卫不变。
- NR修正L2/Linf各≤.020rad（参考原局部投影限制）；修正后重验名义目标及FCL。
- 候选0：START用原SRDF HOME作seed，GOAL用首个已合格START作seed，均不作为端点。
  候选1..63独立原生14D均匀seed；START RNG=2026101202，GOAL=2026101203，
  std::mt19937_64，u=(engine()>>11)*2^-53。首个全部合格即停；规划失败不重选。
- 所有原P4门限照原TASK05/06协议读取；不改600nodes/800iterations/20s。
  成功路径仍只是离散点证据，没有时间参数化或连续扫掠证明；最近距离不可用。

## API来源

本机`/usr/include/kdl/chainiksolverpos_lma.hpp`和原kdl_parser接口已读取；
[MoveIt2 2.5.9 LMA源码](https://github.com/moveit/moveit2/blob/2.5.9/moveit_kinematics/lma_kinematics_plugin/src/lma_kinematics_plugin.cpp)
确认使用KDL-LMA、相同权重及迭代参数。无需运行其ROS Node包装器。
本轮直接后端不借用插件的隐式随机重试/角度harmonize，所有seed和拒绝显式记录。
