# ABB CBiRRT D：单次原空间 solve runner 设计 PRE 草案

2026-10-16。**DESIGN_ONLY / NOT_FROZEN / NO_PROTOCOL_PRIOR_CLAIM_BUILD_OR_QUERY**。本稿由 `nr_entry_review` 只读检查已有 driver 与 RRT transport 后编写。未编译、运行 binary、生成当前 prior 或可执行协议。D64 原超时、61/64 原完整资格、UNKNOWN[61,62,63]保持；D_TAIL02 和 L12 尚未通过，**本稿不能启动 solve**。原211项及正式0/22500、VI974/974保持。

本项目标是已有 D-fixed binary 中真实作者 CBiRRT 的一次入口观测。工程 BUILD01 已成功不等于该入口通过；不得把原 RRT 成功路径或未来 native EXACT 当作 CBiRRT 完整路径资格。

## 先决条件与唯一请求

只有 D 固定清单获得独立、明确标记的完整接口证据，以及 L12 三条原非平凡 RBS/回溯接缝通过后，才允许准备 S 的最终冻结。D_TAIL02 若成功只能按 `SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO` 引用，原 D64 STOP/UNKNOWN 和9个总进程事实不得改写为原八进程运行PASS。L12 必须引用其实际唯一运行及独立 POST，不能只用源码相同跳过。

使用 BUILD01 的 `distance_destination_fix/p4_abb_cbirrt_d` 及其原完整 build/claim/源/库/mesh/hash 链；driver、observer、APC、SVC、collision、CBi 源均不得修改或重编译。D 单 token、原 R2 数值及已声明的保留 temp 观测 I/O 偏差保持，H helper break 不混入。

固定 argv 为 `BINARY II NEW_RUN/work solve trace`；stdin **恰一行**：

```json
{"environment":"II","operation":"solve","seed":7,"range_rad":2.6,"solve_seconds":10.0,"start_q12":"A01 II_0.selected_q_rad 完整12角","goal_q12":"A01 II_1.selected_q_rad 完整12角"}
```

实际冻结必须用原 JSON 数组替换上面的设计占位文字，并逐 binary64 绑定 A01 两文件及所有原始资格证据；本稿不是可直接使用的 request。起终 passive 原 branch 分别3/0，不声称共有一个解析分支。固定 A01 原12角不 wrap、lift、平滑或重新投影。

driver 已固定原 sampler box（两臂重复）：low `[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]`，high `[2.88,1.919,1.22,2.79,2.09,3.1416]`；resolution `.02`、恒true callback、range2.6、10秒 solve。`ompl::RNG::setSeed(7)` 与 `srand(7)`各一次，均在对象前；原角色 `rand()%2`、sampleUniform、完整12维NN、100/500迭代、分支fallback与RBS次序保持。CBi 没有 RRT goalBias，不增加该参数。仅一个 source-dispatch site、一个新进程、一条请求、最多一次原 solve；不做第二 plain solve、control solve、换seed或重试。

## 原 transport 复用与独占输出

以已有 RRT_PCS E2E runner 的 committed build/source/endpoint绑定、exclusive claim、raw结果先保全、失败前缀及事后资产核对为参考；不调用旧 RRT runner、不修改任何冻结 NR/PCS runner。D64 新审清理经验可复用为新版本 stdlib transport，但不得 import 后触发旧科学执行或生成过期 prior。

未来 runner 需先创建独占 `NEW_RUN/work/simulator/`，仅复制本次已绑定的20个 mesh 原字节；复制与校验费用计 S 帽。禁止复制旧 paths。执行前 `NEW_RUN/work/paths` 与 `NEW_RUN/paths` 均不存在；driver 原逻辑再分别创建 `./paths/`、`../paths/`，使作者两个相对路径完全落在新run。不能修改作者路径、temp行为或source返回值。结束后完整递归保存两处原文本文件和所有 temp，包括 false/partial，不以其低精度文本重构高精度角度。

使用非阻塞 stdout/stderr 两 pipe 持续泵取到独占 raw 文件，完整保留 `P4_CBIRRT_D_TRACE` 原字节及作者/PQP诊断。父级 journal 采用 append/flush；不为每条原始 trace 单独 fsync，终局再同步少量文件并记录各同步完成状态。原函数观测 stdout 最终JSON必须先作为raw完整保存，再解析；溢出/截断/异常也保存。只有 `trace` 的真实 started/completed 可报告，不能从 cap、返回或静态结构推断未观测 starts。

所有 Popen 在异步 timer 前后均有父级 registry，先登记 Session 再 start；信号屏蔽短段及其边界必须明示。异常先关闭周期 timer，按所有实际 Popen 并集 kill、drain、wait/reap，再测 self+reaped children CPU；未回收者单列 actual/live/UNKNOWN且不能PASS。旧 H 或 D64 的 timer/清理错误不能复制进新 runner。

## 唯一运行必须保留的证据

- 请求原字节、64位数组、命令、env、seed及构造 dispatch。原 CBi 的直接 RNG 成员结构性初始化与库内部真实 seed draws 分列；后者仍 UNOBSERVED。solve随机动作不报0，原未插桩 `rand/sampleUniform` 的精确调用数不能由grow返回推断。
- 所有 activeDistance 的真实角色、完整 a/b12角、返回，identify 的输入/输出；原 state/vector RBS、固定branch投影、native FK/IK、collision、state/vector回溯与 grow 的真实 entry/return/false/partial原序。观测不添加科学调用。
- `save_source_mpaths` 在原 save body 前记录的两侧原高精度 Motion序列与 parent、branch、a_chain；save完整返回不证明每边重构成功。保留每次 state-level reconstruction 的完整 path，包括所有 false 候选。
- solve 的原返回 status/code、solve wall scope（含原save/I/O，不作论文计时）、solution_count/difference、exact/approximate/has_solution及高精度里程点。
- 原树中 Motion/state各自运行内ID、parent/root、tree侧、完整q、两branch、a_chain；connectionPoint 原两state与Motion映射。不以同q合并不同Motion。只有source exact时调用原 getPlannerData，保存vertex stateID/tag/start/goal及有向边；非exact不制造bridge或为补数据额外调用该接口。
- 整个bound集、claim/protocol、完整prior前后hash；全部source原始输出、raw EOF/exit/进程组/CPU与终局落盘记录。

中断可能只有 raw trace 而没有最终树snapshot，必须标 UNOBSERVED 后缀。不能为补树/bridge重跑原 solve。

## 分类、失败与后续独立路径门

source EXACT 且完整JSON只允许 `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT`。作者 save2file 可以在双role reconstruction均false时提前返回，而外层仍添加exact路径；保留原行为，不能改源码让false变true或仅凭EXACT报路径成功。非exact、timeout、原false、signal、EOF、source/asset变化或预算超帽均保留各自前缀，不再选seed或扩深。

实际 S 后，先只读核对双树 parent/root/branch 和原 connectionPoint。真实 start→goal 由 start侧 parent→child、原桥、goal侧 child→parent构成；必须逐 Motion身份核对，不能直接套单RRT树图门。每里程点边需找到原顺序完整true重构，role0失败再清M试role1的所有失败也保留。完整 dense queue 在另一项 P 冻结后才允许独立物理检查；S runner 本身不能 FK/IK/NR/投影/修路径。

P 仍为独立冻结与claim，拟上限2048唯一原节点、120墙钟/240CPU，旧原闭链/branch/全12限位/离散aligned collision与full12叶距离严格<.05保留。队列超帽则不执行、不只验前2048；完整原首末 binary64等于A01。通过也只可称离散source-policy start→goal路径，不推导连续碰撞、完整几何安全、全局PCS优势或FULL复现。

## 预算与落盘收据

S 拟独立30秒墙钟/60秒CPU，扣当时R2总3600/7200余额；仅一次solve的10秒source限制不是父级总预算。最终冻结须读取全部已结算 execution 的实际own-cost和既有不可测尾部声明，不能沿用本稿或D64旧prior计数。不自动串行启动P或正式统计实验。

预算覆盖claim后准备、mesh/原始请求、构造/solve、pipe、回收、hash和执行证据最终持久化。应采用独立外层 stdlib supervisor 对整个子runner `wait4`/wall计时，runner不留下活跃科学进程；外层receipt以独占append保存最终子进程wall/CPU/exit及execution hash，明确receipt自身保存尾部未被同一receipt闭合测量。最终caps以更完整外层实测判定，越帽只可STOP。不得称包含最终execution fsync的全程成本，除非外层测量实际覆盖；不得将未知收据尾部报0，也不得通过改写旧execution修补历史成本。

本稿未实现或运行supervisor，不证明其已合格。具体新runner与外层计时源码、最终完整request、资格先决证据及budget均须独立静态审查、版本提交和root冻结；未经这些步骤不得执行。
