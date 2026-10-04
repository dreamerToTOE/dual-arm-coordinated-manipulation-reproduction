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
