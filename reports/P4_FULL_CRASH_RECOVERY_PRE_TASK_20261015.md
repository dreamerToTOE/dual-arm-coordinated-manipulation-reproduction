# P4 崩溃断点恢复与 R2 接续声明

2026-10-15（Asia/Shanghai）。本次是原研究接续，不初始化仓库、不新开分支。

## 恢复报告

- 工作树 `/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full`，分支 `p4-full-reproduction-pcs-study`；接管时 HEAD `a39e963f34af123d483759bbabfd3963b7a3f216`。
- 保全后 `git fetch origin` 确认远程仍为 `356a3b148c8d50a071a266c2ae010ab967ffca0d`；本地领先5提交、落后0，无分叉。没有 pull、reset、clean 或切换工作树。
- 6个已有工作树均保留。无残留 P4 规划、资格、编译或实验进程。工作树与进程检查是本次快照，不追溯崩溃确切时刻。
- 57个未提交文件共8,482,891字节已先归档并记录SHA256，再以 `0792acf` 提交原字节。包含空间独立复核、RSS mode0保存数据审查、端点来源审计、两版图表数据和未完成排版验证的Word草稿。归档不意味着这些草稿已获科学/排版验收。
- R1共1826组件断言：1580通过、246失败。R2空间2091项：2088通过、3失败；平面233项和NR56项通过。空间NR160次中154合法收敛、6闭合后限位拒绝；IV附加3正例失败保留。12原端点全部闭链失败。
- 既有RSS固定700目标/5600主动IK，19目标48分支仅满足闭合、限位和真奇异，碰撞/RBS未执行。II/III mode0各0/100，其已存目标均超主动腕心几何可达上界；不外推全连续模式不可行，不重跑这批输入。
- R2三批实际求解共wall16.337196963s、CPU10.593126s。任务A最近同支恢复尚未运行；任务B三臂独立构造尚未运行，960/180wall/360CPU额度未使用。
- 原端点恢复与VI RSS重建的旧待批门已由本次用户明确授权覆盖。正式规划仍0，Table I 22500调用预算尚未获批；所有211义务及500000投影、50000合法点对、Fig3–5/TableI–II、全fixed划分/去障碍对照保留。

## PRE-TASK REPORT

Task: D079原研究R2任务A/B的独立版本化资格。

Scientific objective: 在原几何、基座、抓持、关节界与门限不变的条件下，恢复原端点同解析支最近合法周期代表，并验证三臂RSS候选是否真闭合/真奇异/限位和碰撞合法。

Minimum sufficient evidence: 原输入与全部候选/失败保存；主动角精确不变；独立FK、结构分支、周期lift、原限位；源PQP真实碰撞及姿态一致性；VI两闭环和独立Jacobian谱。碰撞或分支不明不计通过。

Current scope: 仅固定资格与原数据延续，不以本组样本替代正式统计。

Explicit non-goals: P2、Isaac、FR3控制或大规模规划；不改判R0/R1/旧R2失败。

Attempt budget: A最多wall120s/CPU240s，无新IK/NR/随机样本；B单次最多960构造/wall180s/CPU360s，均计入原wall3600s/CPU7200s总账。工程构建独立记账，每构建最多120s。同机制三次有证据修复后进入根因审查，不机械重试。

Preferred method: 直接复用已保存端点全解析支与原作者外部PQP/网格，以薄适配核对世界坐标；VI按候选A显式独立构造。

Fallback method: 接口或资源缺失保留UNKNOWN/BLOCKED及具体证据，不用NR/改阈值制造通过；有证据的实现问题另冻修复后继续。

Stop/escalation: 新分布超本次冻结定义、改变原几何/门限、正式计算或批准预算耗尽时停止相应依赖项；原失败不得消除。

Files expected: 新配置、独立恢复/三臂RSS/碰撞适配脚本、新run_id、阶段审查与覆盖表；原科学源码/配置/结果保持。

Validation plan: 冻结协议和源码提交后才运行；每run记录命令、源码/输入/协议/外部依赖SHA、seed、完整失败前缀、CPU/wall、退出原因；复核恢复前1028个科学文件和57原未提交文件的哈希。

Known ambiguities: 来源端点为舍入文本，无更高有效位匹配副本；RSS VI公开源缺项；原碰撞模块的mesh帧/基座与修订FK可能需逐帧核对；IV的原NR正例完整性门仍失败。

Need user confirmation: no。本次用户已批准A/B资格，正式大规模计算仍需另审。

## PRIOR-ASSET CHECK

Scientific algorithm: 论文APC/RSS的同支解析构造、真实被动Jacobian失秩与多闭链关系。

Pinned source: 原工程 `631b1f65656d025c1bb2173e874192f3fe4d355a`；已有reuse map与R2资产审查沿用，不重建工程栈。

DIRECT_PORT: 原保存候选、不可覆盖日志和SHA记录。

THIN_ADAPTER: 本库R2 C++ APC batch、外部作者PQP/网格、原模型与抓持读取。

TEST_ORACLE: 已独立资格的ABB/Comau逐段FK、平面累计点和矩阵积、物理全约束Jacobian。

REFERENCE_ONLY: 旧FR3/MoveIt碰撞与规划器；不引入其尺度、抓持、阈值或端点。

New: 固定同支最近候选选择器与VI独立RSS有限资格器。分类RECONSTRUCTED，禁止冒充作者原生实现。

Need user decision: no，本授权范围内执行。
