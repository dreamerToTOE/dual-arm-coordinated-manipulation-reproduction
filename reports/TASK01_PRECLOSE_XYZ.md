# TASK01 — 吸附前合并 XYZ 有界纠偏

日期：2026-10-04；状态：IN_PROGRESS，物理验证待完成。TASK01仍未冻结。

## PRE-TASK REPORT

- Task: TASK01，当前独立精准推入工程版吸附前对中。
- Goal: 原门限内修复上一轮 Cube02 X对应偏差3.15mm导致的安全停机，并记录新增耗时。
- Paper method understood as: 基准工程准备，尚未实施P2/P3论文力控；既有前三件D004接触协议差异仍保留，不以demo冒充科学复现。
- Scope: 用户明确同意未吸附XYZ残差合并微调；静止态命令FK/实测FK/IsaacTCP诊断、数学/真实模型只读测试、正常五件实际回归。
- Files expected to change: 上游运行工程preclose_alignment.hpp、独立宏分支、只读probe；本仓测试/分析/报告/六份记录/结果。
- Validation plan: header数学测试→colcon完成→真RobotModel细IK/FCL无命令测试→正常供料五件→旧几何门限/安全停止/耗时统计。
- Known ambiguities/risks: 误差来源尚未完全隔离；三次检查最多两次微调，1mm向量限幅不保证大误差可修；原传感器静止快照非同一步同步；OMPL未固定seed；旧MoveIt teardown问题仍可能出现。
- Need user confirmation: no，用户已明确批准本次XYZ扩展；模型/物理/接触/门限/基准冻结仍不在授权范围。

## 实现

只在 `TASK01_CUBE04_PRECISION_INSERT` 独立分支启用；旧Task26/Task27节点保留原Y残差逻辑。对每个杯面，计算 `delta = desired_GT - actual_GT`，按整个位移向量长度限幅到1mm，然后将其累加到上一条命令FK位置。XYZ一次规划/执行，不逐轴重新RRT。复用原细IK、联合FCL与原姿态；滑轨偏移统一到模型坐标，不重复扣除。

合格即吸附，零额外修正动作；最多三次检查/两次微调，失败保持OPEN并停止后续任务。只有两杯均OPEN才准许纠偏，规划后执行前再次检查。保持原2.5mm XYZ对应门限、0.3mm预吸附间隙差门限及全部已放置Cube验收门限，不改变场景/工具/摩擦/质量/ACM/载物动作。

每轮静止检查记录命令FK、实测关节FK、IsaacTCP及差值。实测FK接近Isaac但不同于命令时支持关节跟踪残差解释；若FK与Isaac不同，则需继续查模型/坐标/时间合同，不能宣称已隔离原因。单一读取每侧GT仍不是硬同步，不作动态测量合同证明。

计时拆分 `plan_wall_s`、`execute_wall_s`、`total_wall_s`，总项含复测等待/诊断。真实模型probe直接调用同一细IK实现，不发送joint/suction命令。

Fidelity：[ORIGINAL] 尚无论文方法；[ADAPTATION] 当前FR3/TCP/滑轨坐标映射；[ENGINEERING] 未吸附XYZ残差修正/测试/计时；[DEVIATION] 不新增接触或门限差异，既有D004差异保留；[EXPERIMENTAL] 固定场景运行，不构成可靠性或基准冻结证明。

上游：https://github.com/dreamerToTOE/dual-arm-embodied-palletizing ，原commit3ee42d2；根未声明统一许可证。本仓只存适配测试/证据，上游补丁均单独提交。

## 验证结果

colcon完成（包69s，总73s）；C++原Y策略及新XYZ向量限幅测试PASS；Python最终22/22 PASS。最初Python新增解析测试暴露日志末尾句点被读成数字的错误，已修复正则并保留失败记录，不涉及机器人逻辑。

真实MoveIt RobotModel只读probe exit=0：左右合并XYZ细IK各0.707mm/9点，联合FCL25样本PASS；加入已释放Cube障碍后正确拒绝。原空载退出及真实种子回放也PASS。probe未构造机器人/吸盘命令发布器。物理回归待完成；上一轮失败原始证据保持在 `20261003_TASK01_precision_full_five_01`。
