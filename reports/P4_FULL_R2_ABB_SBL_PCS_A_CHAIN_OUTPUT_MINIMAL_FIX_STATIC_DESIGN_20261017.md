# SBL_PCS a_chain 最小输出修复：静态设计草案

2026-10-17。状态：`STATIC_DESIGN_ONLY_NOT_IMPLEMENTED_NOT_FROZEN`。本项只读取保存源码、现有观察器和已经完成的 SETUP01 证据，新增本报告；项目 import、源码变换、编译、binary/query/setup/solve、模型、RBS、IK、采样调用均为 0。不改已有工程八稿、SETUP 三稿、stage、binary、共享治理或预算账。

## 1. 结论与接续位置

原作者 `Motion::a_chain` 只有三处赋值和两处值读取。两处读取均用于 `save2file` 将里程点 metadata 写入 `../paths/ik_path.txt`，没有查到该成员参与投影、分支选择、lazy RBS、树选择或回溯控制。新建 connect 没有给该成员赋值；历史 connect 能存活并进入未来成功路径，因此原 writer 可能求值未初始化的 `int`。这构成作者公开程序的具体源码风险，不能归因为论文数学错误，也不能声称已经在实际 solve 中触发。

可审查的最小候选是：在已有、来源可证的 lifetime registry 中保存 root/grow 的已赋值 shadow；connection 的 shadow 从创建到退役始终 unknown。仅替换原 writer 的两处 `a_chain` 输出表达式：已知值原样输出；未知值使用明确的 `-1` sentinel，并在版本化 JSON sidecar 写 `null` 与来源。绝不初始化或写回 `Motion::a_chain`，也不从 RBS 成功角色、父节点、另一树或当前全局 `active_chain` 猜出一个值。

此候选能保留原本有定义的 metadata 数值与行序，但未知字段没有可忠实保留的数值语义。`-1`/`null` 是公开记录的输出格式偏差，不可宣称对未定义原输出逐字等价；未来实现应标 `RECONSTRUCTED_OUTPUT_METADATA_ONLY`。本报告不实现该候选，也不解除当前 driver 的 solve 禁止。

SETUP01 已完成的人员独立保存后审为 9534/9534、失败 0，仅证明 setup 接口、公有 13 点线性作用与保存/费用链。该执行来源 commit 为 `ff25dc60`，execution SHA256 为 `107b8fe30b5e2f02c0a2ad035a2cee62d42f5b604c39d8de4bcd1952505b56e4`。这没有运行 solve，不能消除上述 writer 风险。V25 入账由主代理独立处理，本报告不另造 execution 或费用。

## 2. 来源身份

作者只读副本：`/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning`，commit `909bd72fff778aca8682c96f9eb86ae4eb75557b`。

| 文件 | SHA256 |
|---|---|
| 作者 `planners/SBL_PCS.cpp` | `a8ebe8a01ad57347096b03621099f5fdf61f78ebcfb6b1635745cfbf4a8cb407` |
| 作者 `planners/SBL_PCS.h` | `76d0ba8df05cae6d79575d5b9d63d875f4c56bbd5a6240065d4c0dcf9d396cfc` |
| 作者 `run/plan_PCS.cpp` | `af868b6ed9bb1253fc2283f6d4d2fe8f3437a91ab349414bc44521892c4b3f69` |
| 当前 `baselines/p4_full/geometry_consistent/abb_sbl_pcs_observation_draft.hpp` | `7507648eb8ede25eea1cadcc32270a0bdf27633b1520de717718f6a907b986ac` |
| 当前 `baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_draft.py` | `cf5f5192840883634dfd3f18ea117dd505b66a8f1648391ae15113508ae2a237` |

以上行号均指该 SHA 的原作者文件，不是未来 stage 的行号。现有来源风险补记 `P4_FULL_R2_ABB_SBL_PCS_HISTORICAL_CONNECT_STATIC_CORRECTION_20261017.md` 与旧误判原字节继续保留。

## 3. Motion::a_chain 的全部依赖

| 位置 | 原操作 | 已赋值性与意义 |
|---|---|---|
| `SBL_PCS.h:164–171,190` | 两个 Motion ctor 均只初始化 root/state/parent/valid；声明 `int a_chain` | ctor 不初始化此字段；不得通过修改 ctor 偷换原行为 |
| `SBL_PCS.cpp:121`，进入 start tree 前 | `motion->a_chain = 0` | start root 已知 0；只是作者 root metadata |
| `SBL_PCS.cpp:174`，进入 goal tree 前 | `motion->a_chain = 0` | goal root 已知 0 |
| `SBL_PCS.cpp:253`，grow/addMotion 前 | `motion->a_chain = active_chain` | 已知为当次 grow 最终选用的主动角色 0/1；不是后来 lazy RBS 的结果 |
| `SBL_PCS.cpp:310–318` | 新建 connect，复制 state/root/parent/两 IK 分支并 addMotion | 没有 a_chain 赋值；复制 state 不会复制 Motion 成员 |
| `SBL_PCS.cpp:553` | 输出 `mpath1[i]->a_chain`，随后两个 IK 列 | 第一次且仅用于 metadata 的值读取 |
| `SBL_PCS.cpp:564` | 输出 `mpath2[i]->a_chain`，随后两个 IK 列 | 第二次且仅用于 metadata 的值读取 |

对固定作者 `SBL_PCS.cpp/.h` 的完整文本检索只得到上述三个成员赋值、两个成员值读取和字段声明。`SBL_PCS.h:145` 的 planner 成员 `active_chain` 与 `h:146` 的 `a_chain_connection` 是不同字段；前者在 `cpp:193/201/208/224` 决定 grow 投影/切换，后者在本 cpp 没有引用。`save2file:539` 的局部 `active_chain` 声明也不读取 Motion 字段。

`ik_path.txt` 在作者副本的 `*.cpp,*.h,*.hpp,*.py,*.m` 检索只出现 SBL_PCS、SBL_RSS、CBiRRT_PCS 的 writer，没有找到 reader；在本仓库 `baselines/`、`scripts/` 同扩展名检索没有找到 reader。该结论仅覆盖已检索文件，不证明仓库外没有消费者。未来消费端必须显式识别 sentinel/schema，不能把 `-1` 当合法主动角色。

## 4. 为什么历史 connect 不能视作已赋值

作者 `checkSolution:320` 先执行本树 `isPathValid(tree,connect)`，成功后才执行另一树 `isPathValid(otherTree,connectOther)`。本树调用返回 true、另一树返回 false 时，本树 connect 已被标 valid 且不会随另一树删枝自动删除；本次 `checkSolution` 返回 false，原 connect 仍留在本树 grid/PDF。`addMotion:466–483` 将它按原规则登记，`selectMotion:404–407` 可以在以后选中它。后续 grow 可把它作为 parent；未来的 `while(parent)` 路径提取 `335–345` 因而可以包括这个历史 connect。

当前一次成功连接中新建的末端 connect 本身没有直接放入该次 `mpath1/2`，不能据此推断所有未来里程点都有赋值。对于仍存活的历史 connect，`isPathValid:391–393` 只改 valid，不补 a_chain；`removeMotion:455–459` 的 parent 解绑与递归也不补该值。对象地址复用更不能继承上一 lifetime 的已知性或值。

lazy 验证 `isPathValid:385–388` 与输出重建 `save2file:605–609` 依据相邻两 IK 分支，按 role 0 再 role 1 尝试。它们没有读 Motion::a_chain；尝试成功角色也不等于 grow metadata。不能借此给 unknown 填一个“看似合理”的角色。

## 5. 最小候选的静态边界

### 5.1 Shadow 来源与 lifetime

现观察器 `Lifetime` 只有 `a_chain_initialized` 与 origin，尚未保存 shadow 数值。`snapshot` 使用条件运算符，unknown 分支返回 `null`，不会求值 `m->a_chain`。这已保护观察器，未保护原 writer。

未来可在 observer-owned Lifetime 增加可选值与来源，保持 Motion 字节布局和所有作者 ctor 不变。在原 addMotion wrapper 登记时，固定原源码只有 start-root、goal-root、grow 与 checkSolution-connect 四个调用来源：已有 `ConnectionScope` 在整个 checkSolution 期间标记 connection。非 connection 的前三个来源都在原赋值之后到达 addMotion；仅此时读取一次已赋值字段并保存 shadow 0/1。connection 路径既不读取字段，也不创建数值；其来源保持 `CHECKSOLUTION_CONNECT / UNINITIALIZED_NOT_READ`。

该分类必须由固定源码的精确调用点与静态差异证明，不能推广成“凡 parent 非空就已赋值”。parent 是否为空只可区分已经排除 connection 的 root/grow，不能把以后断开 parent 的历史 connect 改标 root。地址与代际、唯一 lifetime/state ID、退役 token 的当前规则继续保留；lookup 缺项或代际不符应作为工程证据失败保全，不猜值、不重试、不修改树来恢复。

Shadow 登记在 plain/trace 两模式都必须执行；emit 开关只控制观察输出。否则 trace-disabled writer 会丢来源。未来 `snapshot` 和 writer helper 只读取 registry shadow；unknown 的任何时刻均不得读取原 Motion 字段。新 shadow 不回写 Motion，不改变 branch、valid、parent、root、children、grid/PDF 或 sampler/RNG。

### 5.2 仅两处作者输出表达式

未来源码候选只在原 `save2file:553,564` 将第一列表达式分别改成同一个 shadow 输出 helper；两 IK 列、空格、endl、双侧遍历方向、数量、路径状态输出、RBS 重建 body 及它的原 false/提前 return 均保持。

| 来源 | `ik_path.txt` 第一列 | JSON sidecar | 含义 |
|---|---|---|---|
| root | `0` | value=0，root 原赋值来源 | 作者已定义值原样保留 |
| grow | 原 shadow `0` 或 `1` | 同值，grow 原赋值来源 | 作者已定义值原样保留 |
| 任意 lifetime 的 connect | `-1` | value=`null`，`UNINITIALIZED_NOT_READ` | 明示原字段未赋值；不赋予算法角色 |

`-1` 保留原文件三列整数形状，但改变第一列的允许值域；不得将其称为无格式变化。sidecar 至少标 schema/version、RECONSTRUCTED 分类、对应原 writer 文件名/行序、side、行号、motion lifetime ID/address generation、state ID、a_chain value、sentinel、赋值来源。sidecar 必须按原两次遍历的**实际输出顺序**逐行记录，和里程点数及路径快照做一一核对；未知不是有效角色，不能用于 RBS 分支或外推距离资格。

不建议将第一列直接写字面 `null` 而继续使用原无版本文件约定，因为它破坏原三整数形状且容易被旧消费者误读；也不建议填 0/1 或父节点值。整数 sentinel 加 JSON null 仍是版本化 metadata 偏差，不能隐去。

### 5.3 逆恢复与实现声明

已构建的 BUILD01/stage/binary 和 SETUP01 证据不得覆盖。未来实施应创建独立版本化源码与 stage；先绑定上述完整原字节与现观察器 SHA，再将两个 I/O edits 单独列在 manifest 中，给出精确原/新表达式、计数恰二、修前/修后 SHA 与逆恢复。

当前 instrumentation 的“每个完整原 body 出现一次”声明对未来被改动的 save body不能照抄。新版本必须明示：save body 含两个经审的 I/O edits；其他科学 body 逐字保留；先逆剥 wrapper、再逆回两个表达式，最终五源文件与固定输入逐字相等。不能以 wrapper 逆恢复通过来掩盖 body 内改动。observer registry/header 改动另独立列出。

## 6. 仍需后续独立审查和资格的事项

本报告只提出有源码证据的输出边界修复。后续实施前应独立确认：四个原 addMotion 来源穷尽、connection lifetime 永远 unknown、已知 shadow 与合法原赋值一致、plain/trace 捕获一致、helper 不读 Motion 未赋值成员、两处输出 edit 唯一且逆恢复完整、所有模型/控制/branch/RBS/几何/采样条件不变。此处没有生成声称测试通过的 fixture 或证书。

若未来实现这些纯工程边界，仍须新的独立工程 stage/build/review/费用冻结；旧 setup-only binary 继续拒绝 solve。其后首次 SBL solve、原 lazy/RBS/bridge/M 和完整独立离散路径资格须各自先冻结，按原 seed/输入/原 SBL step=.8 与既有门限执行，不能用本报告或 SETUP01 代替。未定义原输出不能作为对照去承诺整个程序在 UB 存在时逐步等价；可证明的范围是固定源码的科学控制语句未改及定义域内 metadata 保留。

原连接失败、UNKNOWN、所有旧源码/实验记录保留；本项不增加 VI 候选（974/974，余额 0），不启动 RSS、正式 Table I 或成本 pilot。全部 211 项全文义务、原统计规模和正式 22500 调用义务不缩减，不进入 P2/Isaac，不提前结题。

## 7. 本项实际命令与交付

实际仅使用 `git status/branch/rev-parse`、`rg`、`sed/nl`、`sha256sum` 读取固定来源和已保存 SETUP01 后审；通过文件 patch 新增本 MD。没有执行任何项目 Python 模块、源码变换、编译器、规划器或模型。未 add/commit/push，由主代理审阅后统一交付。科研执行预算使用 0；不生成新科学成功、失败、超时或性能统计。
