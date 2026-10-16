# ABB SBL_PCS 与 CBiRRT_NR 后续入口：只读静态诊断

2026-10-16。本项没有编译、模型/科学执行、协议/claim 生成或 P 源码修改。作者 commit 为 `909bd72fff778aca8682c96f9eb86ae4eb75557b`，逐文件身份与 staged 对照见同名 JSON。两个 planner 的 cpp/h 与作者原件逐字相同；当前 PCS 几何模板的 apc 是已登记 R2 数值版本，NR 则须沿用已 Q1/局部/RRT_NR 资格的 physical GD seam，不能称未经修改作者 KDL 数值原实现。

|项目|SBL_PCS 原入口|CBiRRT_NR 原入口|
|---|---|---|
|选择/距离|没有 NN/activeDistance；grid cell PDF 抽 cell 再抽 Motion；跨树仅同 projection cell 候选|两树 NN 都绑定 `distanceFunction`，原函数仅 `si_->distance(a->state,b->state)`，全 12 维 RealVector L2；注释 active distance 不等于代码|
|投影/角色|solve 内随机 active=rand()%2，直接用现有节点对应分支 `calc_specific_IK_solution_R1/R2` 并原 fallback；不调用 H 三参随机 IKproject|grow 对 mode1 或尚未 reach 的 mode2 调 `IKproject(dstate)`→原 SVC vector `GD(q)`→已合格 physical NR seam；不涉及主动角色或解析分支|
|局部/回溯|lazy `isPathValid` 先同 q1 branch 的 role0 RBS，失败再同 q2 branch 的 role1；save 重构保持相同优先级和清 M fallback|原全 12 维 RBS、GD 中点；save 每边单个 NR reconstruct，没有 PCS 分支 fallback|
|保存/末门|原 save 写 `../paths` 里程点/IK 与 `./paths` 密 M；false 后 save 返回 void，solve 仍可 EXACT|原 save 只写 `./paths`；false 后 save 返回 void，solve 仍可 EXACT|

SBL 原 main 没有显式设置 projection，而 setup 使用 SelfConfig 默认 projection；具体默认类型、维数、矩阵、cell sizes 和实际 valid-state sampler 需在后续单独入口冻结时真实观察并绑定。不得悄改 projection、cell sizes、valid sampler、lazy 策略或换为 NN。当前只从头文件确认配置入口，尚未运行库 setup；默认实现细节标 UNKNOWN，不凭回忆补造。

SBL `checkSolution` 新建一个 q 与 connectOther 相同的 connect Motion，挂在当前树并做 lazy RBS；最终 mpaths 从原 motion/connectOther 起提取，重复 connect 不入输出路径，但仍在完整树与 PlannerData。因此不能直接复用 CBiP “仅实际 bridge 加两树”输出推断，不得按 q 合并 Motion。connect 未赋 a_chain，Motion 构造也未初始化该字段；observer 必须不读取它，不为方便观察而改科学初始化。原失败 `removeMotion` 会删子树并释放 Motion/state；原 CBiD 地址 map 不能直接作为跨生命周期唯一身份，应版本化观察活动对象/代际，保留删除证据并避免旧地址复用误认。该边界只约束观察，不授权改算法。

CBiRRT_NR 不存在 CBi PCS 已发现的 `activeDistance` qa/qb 单 token 错误，不应把 D 修复或 H 控制流补丁混入。原 growTree 和 solve 中点/iteration100与500、Range2.6、退一 parent 后 connectionPoint、双树 root/parent 链、原 NN 与原 collision 策略全部保持。start/goal 原 source validation 被 `if(0)`关闭，须用独立已合格 A01 端点并在完整路径门再次检查，不能把源 EXACT 当终态资格。

最小路线先 CBiRRT_NR：从现有已验模板拷入新 stage，GD 仅调用已合格同一 numerical seam；原 CBiNR 控制流、全 12 距离以及所有 SVC 科学 body 保留一次、wrapper 可逆。一个新 target 编译即够，runtime plain/trace 可在同 binary 选择；工程拟 45 秒墙钟/90 秒 CPU，0 binary query/solve，扣最新 charged ledger 并以独占 GNUtime 外层覆盖 import→compiler/reap→全部持久化→exit。此处仅拟预算，尚未冻结或消耗。

工程通过后，不重复 Q1/NR 局部/RRT_NR 或已过 CBiPCS P。先按逐字 body/kernel 绑定复用原组件证书，仅对新 planner 的 NN/树与控制链做观测；另冻结一次 II/A01/seed7/原 range2.6/solve10 候选，拟整体30墙钟/60CPU。完整保存双树身份、source mpaths、所有原成功/失败 NR M、唯一请求/PID/raw/EOF/exit和外层费用。若 source EXACT，只从原真 M 得到全部物理队列，另冻最多2048全节点/120墙钟/240CPU独立数学闭链/机械限位/v3 aligned离散碰撞门，不截尾、不补构造、不重复 solve。source非EXACT/缺M/超帽按原结果留证进入根因审查，不能换seed延时。后两项是路线建议，不是当前工程授权。

SBL 暂只静态记录；待其上述 projection、lazy删树/身份及未初始化字段观察方案独立审查后，才能做新 stage 的单target工程、一次solve和完整P，预算分别拟45/90、30/60、120/240，均另冻最新总账。SBL 源 scientific control flow 目前不修改。

原211完整论文义务和统计规模保留，VI974/974余0、正式TableI0/22500；端到端资格后再做可重复成本pilot并申请正式预算。上述离散候选即使通过，也不是连续无碰撞、RSS、方法优势或完整论文复现；不进入P2/Isaac。
