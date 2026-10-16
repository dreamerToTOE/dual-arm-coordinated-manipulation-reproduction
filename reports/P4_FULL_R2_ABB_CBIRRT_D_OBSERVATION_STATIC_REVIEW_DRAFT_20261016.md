# CBiRRT D：构造与完整路径观察的独立静态清单

2026-10-16，**STATIC_DESIGN_REVIEW_DRAFT / NO_BUILD_OR_QUERY**。本项为新D两目标builder/probe提供只读技术支持，未改其文件、未生成protocol/prior/claim、未编译或调用科学接口。本文不是新driver的最终PASS；实际新文件完成后仍须逐字审查。

原来源为 `CKCplanning@909bd72fff778aca8682c96f9eb86ae4eb75557b`。原CBiRRT cpp SHA256 `60f6a483c533f61749bc7e741acc72bfc8cc2e137d719b25392e73831e458d93`，header `714076be551bf08383402076466fbe4a15ed0e36cb1b3300e9533a67aa1f91b7`。以下行号均相对此原来源。单tokenD候选与完整阶段建议见 `P4_FULL_R2_ABB_CBIRRT_D_STAGED_QUALIFICATION_PRE_DRAFT_20261016.md`；两文件不授予执行权限。

## 真实构造、state与析构

1. 原 `CBiRRT(si,maxStep,env)` cpp49先构造OMPL Planner和`StateValidityChecker(si,env)`。SVC必须收到真实非空SI；不能用无SI的`SVC(int env)`之后调用defaultSettings，因为该构造不赋`mysi_`。SVC(si)构造two_robots和collisionDetection，前者初始化几何/矩阵/界，后者`load_models()`读mesh并建PQP模型；SVC再setQ/setP。这里没有FK/IK/闭链/碰撞查询，但mesh处理本身不是0资源。
2. 原CBi的cpp59 `defaultSettings()`仅取`mysi_->getStateSpace().get()`，并非setup。未setup时两NN shared_ptr为空；distance模式不调用setup、allocStateSampler、checkValidity、solve、grow、getPlannerData或clear。
3. CBi header的`RNG rng_`即使distance模式也会构造。安装OMPL 1.7 `RandomNumbers.h:59–60`明确默认RNG构造初始化不同seed；固定setSeed(7)应在OMPL对象前。8个source×mode×env进程的直接CBi RNG成员初始化单列；库内部无hook的种子生成draw为UNOBSERVED，不能记0。距离体、observer中0 rand/shuffle/sampleUniform与0抽样另列。
4. `State`为vector<double>；OMPL使用真正`RealVectorStateSpace(12)`，`StateType::values`为12元素double数组，source retrieve固定前6/后6。q须有限、恰12角，原binary64输入完整写回；不得用CompoundStateSpace布局替代。
5. probe每次显式设置原public `active_chain`为0/1；不要依赖其未初始化值。Motion默认构造仅初始化root/state/parent，`ik_q1_active/ik_q2_active/a_chain`未初始化；distance observer不得读取它们，或在fixture中显式赋值。activeDistance只读取state和active_chain，不需要branch。
6. 推荐两ScopedState分配真实state、栈上默认Motion仅借用其指针，probe中不插入任何树。Motion析构为空，不释放state；ScopedState做唯一RAII释放。若用Motion(si)需对显式allocState异常安全地free，不能泄漏或双释放。
7. 不setup时CBi析构cpp64→freeMemory：tStart_/tGoal_都空，各if跳过，不触发NN。应在SI/space仍存活时析构planner，之后释放fixture state；不要为观察而故意让原析构接触无效树或已释放state。
8. 原SVC若干计数未在构造初始化，读取它们不能证明0调用。可调用原`initiate_log_parameters()`做纯计数reset，再报告实际hook；不要读未初始化成员。原mesh缺失会`exit(-1)`，父runner需保存进程退出及stdout/stderr，不能期待catch捕获。构造“Robots initialized”等stdout转stderr，JSONL输出保持干净。

## 单token隔离与运行模式

- control完全保留D缺陷；fixed仅role1首次retrieve第三实参qb→qa，整文件反向恢复必须等于原字节。APC采用同一既有R2数值基底，SVC/H不变；H成功break严禁混入。
- 两stage的相同观测变换必须先移除再逐字还原相应科学来源。原APC、SVC、collision、planner数学body在plain/trace下相同；plain/trace仅观测开关。
- distance：64次真实原接口，禁止额外模型/随机采样。local：只构造原SVC，原三边、12个顶层state-level调用；无需构造CBi及rng_。solve：真实原CBi单次入口，另冻资格，不因binary已经链接而自动执行。
- 一个binary具备三模式，只减少工程重复；每模式有独立新run/claim/输入/预算，builder不启动任意mode。错误请求应在科学入口前拒绝，不做fallback/retry。

## 一次编译应预留的最小源观察

|原接口|返回后必须保留|科学保真条件|
|---|---|---|
|CBi activeDistance|call index、role、两输入q12、原返回double，源started/completed区分|原body完整一次，observer不改active_chain、不取额外模型、不抽样|
|SVC state-level checkMotionRBS|两输入q12、role、branch、原bool；可附稳定运行内state ID|保持原state→vector wrapper和完整递归；不自写替代RBS|
|SVC state-level reconstructRBS|两输入q12、role、branch、原bool、完整M，包括false前缀|原wrapper先push首末且原完整body一次；false不清除原证据|
|SVC vector identify|q12、原input labels、returned labels、call index|原body一次，observer不能重新identify|

只记录这些真实完成调用，不能把completed数冒充未返回的内部started。必要时加纯entry计数与异常前缀，口径先冻。local trace还需既有固定branch/RBS递归观察，以核对中点真实存在和plain/trace相同；不为观测新增FK/IK/collision。

原状态层RBS被grow在cpp245/247调用；原重构在save2file628/631调用。只派生公开同名方法不能拦截非虚原内部调用，必须采用审查过的源body返回lambda观测或等价有证据的接缝。

## 只读双树snapshot及source path

solve返回后、planner析构前，由派生probe只读列出两NN树。每个Motion保存稳定运行内ID、tree_name、state_ID、q12、parent_ID、root_ID/状态、原两IK label和a_chain；再保存原connectionPoint两state映射的Motion_ID。全树包含未在最终path中的节点，也保留同q但不同Motion的身份。未初始化或悬空字段不能读取；source合法加入的root/新节点都已有赋值。

`PlannerDataVertex::operator==`在安装`PlannerData.h:92–95`比较**state指针**。原PlannerData会保留同q不同Motion；新JSON不得按q去重。应导出vertex tag1/2、原start/goal、原有向edges及Motion映射，所有状态在释放前复制到JSON。

原连接链：cpp400–401分辨两树相遇点，414–417将startMotion退parent，否则goalMotion退parent，以排除双树重复状态；419赋connectionPoint。422–436按parent分别形成mpath1（连接→start）及mpath2（连接→goal），444–447拼成reverse(mpath1)+mpath2。必须保留这条真实原拼接，不能按最近q自行重接。

独立图验收需要：start树parent→child；goal树child→parent；单个原connectionPoint桥start→goal。原getPlannerData对应cpp496–497、512–513、518。真实exact后可调用原getPlannerData作交叉证据。TIMEOUT/INVALID时connectionPoint仍可能null，而原方法无条件加桥；此时不为补证调用它，使用只读树snapshot并标桥不存在/UNKNOWN，不创造边。

完整树snapshot、pdef原PathGeometric高精度milestones与真实原回溯日志足以推导并核对上述mpath序列。若额外做save-entry观测可保存原mpath1/2的Motion IDs，但不能改数学控制流或自写重构。不得因源样本数少，省略对原connection桥或goal反向边的核对。

## 原save2file的失败与I/O

cpp451原save2file后，453仍添加非approx路径。save2file628先role0共branch重构；失败且role1共branch时630清M、631再重构；635–636双失败则提前return。**source EXACT不能用来证明完整dense路径**。完整高精度假/真回溯必须保留，任何边无最终true或首末不连则保留source exact而拒绝路径外门，不改原bool或换seed。

原milestone/ik写`../paths/`，dense temp/path写`./paths/`。同一新独占run内部两处目录均应存在，所有文件由当前进程新建，严禁触碰历史paths；原文本完整留存并视为低精度旁证。保留temp代替cpp661 remove只能标I/O偏差；原smoothing注释不启用。真实轨迹使用回溯JSON的binary64完整q，不从txt恢复角度或修缝。

solver固定II、A01原恢复起终点、seed7、range2.6、resolution .02、原采样盒及恒true callback、10秒solve；原CBi没有goalBias参数，不拷RRT的.05。原数学计时在回溯前cpp407–408停止，driver墙钟含观察及回溯，两者分开记录，不能当公平速度样本。

本设计保留所有原失败和211项义务；VI974余额0、正式Table I0/22500不变。下一步仅在新builder/probe完成后做静态技术审查；本文件不生成运行资格、不增加预算、不启P2/Isaac。
