# TASK01 — 侧压后的释放与短退出诊断/修复

日期：2026-10-04；状态：IN_PROGRESS，尚无新的物理PASS。

## PRE-TASK REPORT

- Task: TASK01，独立精准插入工程版BUG-016。
- Goal: 在原3mm深墙门限内避免Cube02释放附近退离深墙，保留XYZ修正。
- Paper method understood as: 本轮工程基准准备，不实施P2内部力控制/P3力位混合；不能把前三件原D004协议差异改称已复现。
- Scope of this iteration: 用户“继续”明确同意继续修复释放/退出窗口。先阶段标记+同一步PhysX工具/碰撞接触读数，分离释放与退出，再做依据证据的最小退出/释放修复。
- Files expected to change: 上游独立宏分支/只读probe或策略header；本仓headless记录器及测试、此报告、六份记录、task说明、结果。
- Validation plan: 数学/软件测试→编译→真实RobotModel无命令FCL→实际诊断→修复局部回归→正常供料五件。局部预置或诊断hold不计完整五件PASS。
- Known ambiguities / risks: 既有2deg关节落稳门限可能隐藏受压稳态残差；未知是约束解除、杯面接触还是退出起点错误。诊断阶段消息为异步到达标签，工具/物体/碰撞数据在同一步，不能当作吸盘D6或TCP标定力。OMPL随机、不构成可靠性；磁盘仅3.8GB，避免整个流程full-rate巨量力日志。
- Need user confirmation: no，用户已批准该窗口的最小工程修复；几何/材质/质量/吸盘参数/ACM/门限/论文方法/基准冻结仍不在授权范围。如需此类改变则停止。

## 分类与边界

[ORIGINAL] 本轮无论文算法实现；[ADAPTATION] 复用现有FR3/L工具/PhysX/MoveIt；[ENGINEERING] 阶段观测、同一步读数、有限IK/碰撞检查与测量起点；[DEVIATION] 不新增基准/论文接触差异，既有D004差异保留；[EXPERIMENTAL] 可选主线程短hold或局部预置用于诊断，与普通完整执行区分。

上游 https://github.com/dreamerToTOE/dual-arm-embodied-palletizing ，起始commit f0812a4，根未声明统一许可证；上游修改单独记录。本仓起始59a8095。保护目录不访问/不修改。

## 验证与最终记录

待实际实验；上一轮完整失败保持在 `results/20261004_TASK01_preclose_xyz_full_01`，不得覆盖。

### 诊断 checkpoint

独立变体 build PASS56.5s/package56.8s/total，runtime b259366/binaryc0939f21...。Python28/28PASS，包括摘要峰值、混步拒绝、非有限位置拒绝。诊断01在启动期BRANCH_SIGN读取失败，无控制器命令；failure.json是权威负证据，Isaac.close导致exit0不能算PASS。诊断02用bridge命名空间取得既有sign，未改scene/bridge。

诊断02 max5为保留Cube02短转场分支，但在batch2完成后主动停止，避免1400s仿真deadline中断后续持件运动。hold3s改变时序，仅诊断；普通默认0未改。第一块观察到OPEN静止hold的Xdelta0.028mm、短退出Xdelta0mm，不复现此前第二块问题，尚不能归因/宣称修复。实际第二块数据待完成。命令、版本和artifact见run metadata。

### 诊断最终结果 / 实测起点修复

诊断02实际未到达batch2完成：Cube02推到深墙，gap1.804mm通过原3mm门限；后续SIDE_HIGH_APPROACH所有候选在t=0因left_fr3_side_suction与当前Cube碰撞0.783mm而拒绝，安全打开并exit1。第一块cell0.946/deep0.497/side0.805mm通过；13227稀疏物理样本/0错误、1617释放窗口样本，Cube03–05未先进。此前Cube02释放回带尚未复现，不能用这次失败给它归因。结束headless时所有杯已OPEN，MoveItteardown-11继续存在。

实际侧压规划混用了PUSH命令终点与Cube实测位姿。失败后的静态ROS杯面后侧间隙约0.267mm（不同时间，不是失败瞬间证明）；因此先复用已有实测seed工程机制。在独立宏分支的实际侧压入口，用同一RobotState取双臂，验证CLOSED背挡/OPEN侧压臂、关节形状/有限/限位、命令差仍在原0.035rad内，然后生成hold seed，当前Cube仍在完整FCL里。预测预检、侧压/释放轨迹目标、旧Task26/27行为均不改。实测碰撞仍拒绝，不扩大ACM/不豁免Cube。runtime2fbfa0b；最终binary6a64fb90...。C++政策单测PASS，Python28/28PASS，完整build62s+最终增量0.44s；实际效果未先行宣称。

下一次正常供料5件，hold默认0，不使用预置；`results/20261004_TASK01_measured_side_full_01/metadata.json`保存精确命令/版本/hash。普通释放窗口继续只读记录，既有BUG-016仍OPEN。

普通测试checkpoint：同一最终binary的真实RobotModel无命令XYZ/空载退路/FCL probe exit0。Cube01实测side-start联合FCL通过，普通releasehold0，最终cell0.678/deep0.670/side0.108mm通过；batch1PASS并到第二件预吸位。第二件仍在运行，不能提前宣称修复Cube02或完整五件。基准analytic checkerPASS/36nulls/hash不变。一次误传checker的`--help`被当作文件名报错，随后按真实文件参数重跑PASS，不是仿真或模型负结果。

### 2026-10-04 后续 PRE-TASK REPORT：空载退出备用路径

- Task: TASK01，Cube02落桌后空载退出。
- Goal: 对比此前成功记录，复用已允许的空载RRTConnect，保留安全拒绝和释放诊断。
- Paper method understood as: 仍为工程基准准备，不实施P2/P3论文控制方法。
- Scope: 独立变体双杯OPEN后，实测起点+原目标，Cartesian和连续seed失败才尝试有限RRT；已释放Cube保留完整FCL，不更改持件路径/侧压/模型/场景/ACM/门限。
- Files expected to change: 上游共享cpp独立宏、无命令probe；此报告、六份记录、结果metadata/摘要。
- Validation plan: 失败日志差异审查→编译/政策测试→四位小数失败seed无命令重放（临时同步PlanningScene须同步恢复）→全新普通供料物理回归。
- Known ambiguities / risks: 此前局部Cube04→05成功时未触发备用IK，不覆盖本次Cube02肘部分支。OMPL不固定随机seed；同步FCL为离散采样，不是连续碰撞保证。复现仍可能发现实测起点碰撞，必须拒绝。
- Need user confirmation: no，用户明确要求继续，空载RRT属既有工程路径复用；科学/几何/物理/门限变化仍需另行确认。

普通measured_side_full_01实际最终FAIL：Cube01完成；Cube02共同落桌并双杯OPEN后，左臂实测seed与命令差0.000681rad/右0.000995rad。4种Cartesian步长fraction均1，但FK直线偏差752–967mm，严格拒绝；连续IK失败118/151段，controllerexit1，后续对象未执行。未到达Cube02侧压/释放，BUG-016尚无修复证明。Isaac在本机后台headless运行，不是GUI验收；用户询问后已明确说明。

空载RRT最终源码runtime df9c2c0，binaryc760d506...；编译55.8s/package56.1s/total通过。每臂最多3个3s候选；数字/限位/实测首点/原MoveIt目标约束检查，复用关节总路程排序，起点及双臂同步FCL保留当前Cube；场景恢复失败不执行。旧Task26/27宏分支不启用此机制。

无命令重放01 exit1：新手写总角度门限拒绝左候选，场景已有对象的严格逐字段恢复比较失败，均保留。重放02按本次实际MoveIt请求的原目标约束判断（不是放宽用户门限），使用正确上一批railshift0.100m，起点Cube模型x0.667925、目标leftx0.690/rightx0.590。exit0：严格FCL1277采样，CLOSED/起点障碍负测试通过，临时同步的6个原本不存在ID同步删除/查询确认。第一次已有对象逐字段恢复问题没有由第二次absent-ID测试证明解决，后续需独立核查；当前实际caller的当前Cube正常被摘除，走已验证REMOVE分支。该重放不发布机器人命令，不构造Arm，但会临时改PlanningScene，不应叫场景只读。旧Cube04/05连续seed重放及XYZ测试仍通过，Python28/C++策略/analytic36nulls通过。

下一轮`results/20261004_TASK01_empty_rrt_full_01`：本机headless全新普通供料0预置，first1/max5/scale5/hold0，实际结果待完成。源码已推上游task01-runtime-fixes。不得用无命令重放替代实际退出或完整五件证明。

正常物理checkpoint（同一df9c2c0二进制，仍运行）：batch1和2已实际PASS；第一块cell1.983/deep1.521/side1.272mm，第二块cell0.807/deep0.800/side0.104mm。两件空载退路均普通Cartesian通过，未触发RRT。前两释放窗口2870条same-step诊断完整性通过，Cube02press末x1.0992638→clearancelast1.0992001，回带约0.0637mm；CLEARANCE_ENTER内CubeXdelta-0.012mm，后臂TCPX-5.734/侧压臂-14.073mm。工具仍有X运动但本次Cube未大幅回带，不能归因“已消除该运动”。phase标签异步、普通OPEN标签最多1step，不构成单独静止释放观察；历史5.138mm失败仍保留/BUG016仍OPEN。第三块正在原流程执行，不能算完整五件。
