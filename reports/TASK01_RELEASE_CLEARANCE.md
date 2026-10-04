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
