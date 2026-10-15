# R2 II/III NR Q1 科学调度与比较 PRE 草案

2026-10-15。**DRAFT / NOT_FROZEN / ZERO_NEW_SCIENTIFIC_CALLS**。仅准备独立可审查的科学runner与协议草案；不编译、不运行C++ binary、不调用Python NR/FK/J/SVD/碰撞，不提交。工程构建成功并绑定真实binary/manifest/build execution后，由root分别审查、冻结、提交，才能单次执行。

## PRE-TASK REPORT

- Task：R2普通NR最早未通过的C++移植Q1；不是重跑R0/R1/R2既有结论。
- Scientific objective：在历史II/III全部64输入上验证同一C++内核plain/trace一致性，以及与原物理NumPy NR的逐步一致性。
- Minimum sufficient evidence：64项完整来源链、192个顶层派发/完成状态、原计算量的详细观测、全部差异/失败/尾部、独立终态闭合与源界门。
- Current scope：固定II32+III32、原顺序；C++plain64→C++trace64→Python原函数64；不新增或筛样。
- Explicit non-goals：不做原KDL轨迹等价、其他四环境、原GD/RBS接缝、规划、碰撞、RSS、速度统计、正式Table I或PCS优势结论。
- Attempt budget：本次准备0科学；拟单次60wall/120CPU，取原R2累计3600wall/7200CPU余额min；固定claim，不reset/retry/resume。
- Preferred method：复用coverage单binary JSONL driver与只观测原函数的sys.settrace适配器，不复制solver。
- Fallback method：无自动fallback；失败保全，root审查原因及剩余预算。
- Stop/escalation：来源/构建不一致、运行时/预算/日志错误保存prefix停止；数值不一致完整记录，不以成功子集或放宽门解决；三次同机制有证据修复后按D079根因审查。
- Files expected to change：本PRE、`scripts/qualify_p4_full_r2_nr_abb_q1_draft.py`、未冻结Q1 JSON；不改旧源、输入、输出和账本。
- Validation plan：只做语法compile(AST/py_compile)、零科学describe/validate；真实运行须root冻结后单次执行。
- Known ambiguities：异库浮点误差与边界秩；外部kill时C++未返回call内部trace未持久化，标UNKNOWN；有限near64不能证明全RNG能力。
- Need user confirmation：no（在既有版本化有限资格授权内准备；不自动执行大规模规划）。

## PRIOR-ASSET CHECK

已有原任务的631b1f工程复用审计及`docs/POST_TASK01_REUSE_MAP.md`继续适用：当前算法为论文全Jacobian Moore–Penrose NR，FR3/MoveIt/Isaac工程机构不作为ABB替代。`physical_nr.py`、ABB独立oracle为TEST_ORACLE；Eigen SVD为DIRECT_PORT；现有common.RunBudget及RRT build模块的SHA/claim/CPU工具为THIN_ADAPTER；coverage JSONL driver及sys.settrace observer直接复用。旧14维工程projection仅REFERENCE_ONLY，不重造预算、SVD、solver或平台。当前不需要用户另行决定。

## 冻结输入、数学条件与门

runner逐条重建原SPATIAL01 II/III中所有`kind=nr_reference`记录，按原环境与observation顺序核对audit JSON的case_id、fixture、source index、q及完整历史状态/候选/metric轨迹。旧audit SHA固定；原`physical_nr.py` SHA固定`e2dc41936190c7fe335a442c1fee2952681ea5c1be5b94393590188f0fb87d43`。旧184检查/120更新只是历史参考，不将它们或旧64 CONVERGED写成新执行的预期成功门。

保持原默认：10000最大更新、iteration0/10000检查、每call内部120秒、未缩放mm/rad、相对SVD1e-12、位置maxabs1e-5mm及旋转矩阵maxabs1e-5、原3.1416机械界、收敛后真2π periodic_chart。无阻尼、line search、步长/限位夹紧、分支筛选或固定主动臂。

以下门是root提出并在此明确的**预冻结建议**，协议冻结后不可按结果调整：

| 比较对象 | 门 |
|---|---|
| C++plain/trace输入、状态、候选、metrics、accepted_updates、有限性、method、collision标记 | 去除wall与trace后解析值精确相同 |
| C++trace与原Python状态、iteration序列、更新数、空更新模式、谱数值秩 | 精确相同 |
| q_before/q_next/最终q/observed_delta_q | 每坐标绝对≤1e-10rad |
| g前三项、J前三行、位置metric | 每项绝对≤1e-8mm（J为mm/rad） |
| g后三项、J后三行、旋转矩阵/角metric | 每项绝对≤1e-11 |
| singular_values | 每项绝对≤1e-8 + 1e-10×max(abs两值) |
| cutoff | 绝对≤1e-18 + 1e-10×max(abs两值) |
| 独立物理终态 | 原位置≤1e-5mm、旋转矩阵≤1e-5及原机械界；不wrap/lift/修复 |

不比较SVD U/V向量符号。C++保存proposal与observed_delta分别列明，跨语言只比较已落地q差；不伪称Python保存了未计算的proposal。原Python新返回与每项历史status/iteration序列精确比较，候选及全部metric按相同绝对门比较；不一致记`HISTORY_REPLAY_MISMATCH_UNKNOWN`并阻断transfer PASS。旧结果不改写，也不硬编码184/120合计或强迫新调用成功。

## 保全、观测与预算

原Python只调用`physical_nr.project_nr`一次/输入；observer只匹配原code对象，在已有g/J/metrics和已有SVD/update后复制，finally恢复trace。逐STEP_SNAPSHOT/STEP_UPDATE sink即时写worker stderr事件，外部停止仍保留前缀。仅`arm_fk_jac`暂时包装为before/after事件wrapper并finally恢复，直接调用原函数，不增加任何数学评估；`project_nr`/closure/residual/SVD均不替换。工程PRE的“无monkeypatch”在本细化协议中明确为不替换solver本体，不能据它隐去这一计数包装。每个C++trace有限最终候选再单独调用原residual_metrics与source_limits；若CONVERGED却独立闭合/限位失败为soundness阻断。64个有限终态最多128额外arm FK/J，已含整次预算。

Python观测在**一个串行JSONL worker**中先执行原64 NR，再按原顺序独立检查64终态（无效/非有限候选仅返回未合格，不求metric）。父进程以原RunBudget+live process-group CPU监视并在预算时kill整个组，stdout bytes/stderr事件即时保全。observer的BaseException捕获可能吞掉其线程内回调异常，所以**不使用callback异常作为预算控制**；父进程独立硬帽不受其影响。任何observer_errors先保留返回，立即停止后续科学调用，不继续剩余64项。worker独占token防第二次启动；未返回项明确UNKNOWN。

C++每mode一个持久串行进程；每次只派发一个request、收到原响应并保全才派发下一项。每块stdout bytes与全部stderr即时保留；响应先exclusive JSON落盘，再解释。外部kill时原driver未return的内部steps没有可观察日志，明确UNKNOWN，不用历史轨迹推算已执行步数；已完成call完整trace不丢失。plain本来没有详细trace。调度不会重派发或用其他输入补齐。

输入、原参考、runner/observer/driver/header、真实build manifest/binary/build execution/protocol/claim、Eigen/nlohmann树及Python/NumPy实际依赖均绑定SHA；运行前后逐字核对。全execution逐自身wall/CPU加一次，冻结前重读，不用V5旧快照开额度。claim和run目录独占新建，全部修改、导入、trace保存、比较、后哈希与清理计入60/120；子进程live CPU由现有工具监视。任何证据/清理错误不能PASS。

Q1只判断固定64的有限移植一致性，标签`PASS_FIXED64_NUMERICAL_TRANSFER`；物理门、C++/Python实际CONVERGED分母与移植误差门分别输出。双边同false可以构成移植一致，但不是投影能力通过；普通不收敛/限位拒绝如实保存，不伪造成功或理论反例。NR原GD/RBS与全局规划尚须后续冻结资格。所有211项、正式22500、其他图表和算法义务保留。完成P4后Word/PDF和双FR3分析、用户审查最新范围表的要求保持；不进入P2/Isaac。
