# R2 II/III 物理全链 NR C++移植最小工程与Q1资格 PRE草案

日期：2026-10-15。状态：**PRE_DRAFT / NOT_BUILT / NOT_EXECUTED / NOT_QUALIFIED**。本次仅准备，不编译、不运行binary/Python参考、不调用FK/J、SVD、NR、IK、碰撞、RNG或planner，不改旧header、已冻结源/协议/日志/输入。以下新文件仍待独立静态审查与root冻结。

## 具体恢复对象与标签

复用既有项目自有 `physical_nr_abb_cpp_draft.hpp`，不重写数学内核。新的 `physical_nr_abb_q1_driver_draft.cpp` 是单binary JSONL薄入口，argv选择plain/trace：两者调用同一个 `p4nr_draft::project_nr`，只设同一Options的 `detailed_trace`，不编译两套solver。原Python `physical_nr.py` 及64个II/III历史输入/全部历史终态保留；原KDL、原GD/SVC/RBS、RSS/PCS和其他环境本阶段均不改。

候选标签仍 `RECONSTRUCTED_PHYSICAL_FULL_NR_CPP_DRAFT`，是已合格NumPy物理全链NR的C++移植资格，不是作者原生KDL、不是其迭代轨迹，也不是速度基线。Q1通过之后才可另冻结原GD接缝/真实RBS与规划；本阶段0 solve、0 collision、0正式Table I。

## 工程一次构建：45 wall / 90 CPU

`build_p4_full_r2_nr_abb_q1_draft.py` 复用既有RRT build模块的纯文件/时钟/CPU/claim工具，不导入科学模块。`--describe-protocol` 仅读文件/哈希/旧execution；`--validate-draft` 零编译。只有所有源/协议已入commit、独立审查/root冻结flags均true，且完整own/prior/library SHA与当前逐值一致时，`--protocol` 才可启动一次编译；固定新claim、stage和execution，已有任何一个即阻断，不retry/reset/resume。

编译命令为一个translation unit，`g++ -std=c++17 -O1 -g0 -Wall -Wextra -I/usr/include/eigen3 ...`，无fast-math、OpenMP、并行make、原作者/PQP/OMPL/KDL链接。Eigen和nlohmann整个include树、真实g++二进制以及全部自有源绑定SHA。工程时间含准备后的编译/后哈希，live process group累计CPU与墙钟帽均监视，超帽kill整个组、保存stdout/stderr/失败binary前缀及execution，不能为追求成功自行重编。binary构建成功也**不执行**。

45/90是root提出的工程上限，**不是实测Eigen编译成本承诺**。既有RRT_PCS一次工程为17.12737691100483 wall /23.727903 CPU；其源码和Eigen实例化不同，不能外推为NR成本。天真两目标基线翻倍会是34.25475382200966/47.455806，已经消耗45秒的76.12%，只余10.74524617799034 wall给未知Eigen模板成本，缺乏保证。因此采用一binary runtime flag、一个目标、-O1，消除第二次相同Eigen实例化。若单目标仍超45秒，只能保留失败并依据该实测成本记录后续预算方案，不自动提升预算或再试。-O1与旧-O2工程差别明确保存；资格不输出公平性能结论。

## Q1固定完整输入与192次顶层预算

输入全部来自 `reports/P4_FULL_R2_NR_SOURCE_AUDIT_SAVED_INPUTS_20261015.json` 的 `Q1_saved_NR_cases_in_original_environment_and_observation_order`：II32、III32，原顺序64条，不筛选、不构造新样本、不换fixture/h/seed。每条保留source_path/observation index/历史输入/终态/metric轨迹，冻结时还须逐项核对原observations对应条目，不能只信复制JSON。

固定调度：C++ plain全部64 → 同binary trace全部64 → Python原函数完整观测全部64，共最多192次顶层NR。记录dispatched/completed，外部kill后未返回调用标UNKNOWN；不能由192预算推算完成。任一运行时/哈希/预算失败保存完整prefix与未执行列表，不补抽/重排/重复；普通科学数值不一致须完整记录并阻断依赖阶段，不能换成功子集。

默认数学参数完全保持：10000次最大更新、iteration0及10000收敛检查、每调用120s内部wall、位置maxabs1e-5 mm/旋转矩阵maxabs1e-5、相对SVD cutoff1e-12、未缩放mm/rad、无阻尼/线搜索/夹紧/迭代内限位拒绝。外部科学帽**60 wall /120 CPU**是整次192调度+trace保存/比较+独立终态门总帽，取R2总余额min；外部帽不修改NR算法10000次或原内部120s参数。固定单线程数值环境，线程配置和NumPy/Eigen版本必须实际保存；不能据此作跨语言速度结论。

只读历史成本：这64条原保存运行均CONVERGED；共184次迭代检查、120次SVD更新，最长3检查；64个原wall总0.26916984900208263s。历史轨迹只有metric，缺q/g/J/sigma/update；新完整观测是有预算资格调用，不冒称已经保存。历史成本仅用于选择小规模60/120帽，不保证新C++数值轨迹或trace时间相同；出现原外未收敛要保留而不是夹紧/缩减参数。

## Python原函数完整trace：观测而非第二solver

`p4_full_r2_nr_python_trace_draft.py::observe_project_nr` 接收原module，用 `sys.settrace` **只匹配原 `project_nr.__code__`**。在原 `trace.append` 行前复制已算出的q/g/J/metrics；在原 `q-=` 后的isfinite行前复制已存在s、mask和q_next，cutoff按已有s0与原阈值记录。无额外FK/J/SVD/NR，无body复制或函数monkeypatch；finally恢复进入时的trace hook。可选 `event_sink` 每个STEP_SNAPSHOT/STEP_UPDATE后收到独立deepcopy记录，由runner立即持久保存，使外部BaseException/kill前已观察的完整prefix不只存于内存。logger/sink异常只缓存到observer_errors，不向原solver抛入改变其返回。

header `Step.delta_q` 实际保存 `-correction`（proposal），与浮点落地 `q_next-q_before` 存在舍入语义差别。driver明确分列 `proposed_delta_q` 和保存q重建的 `observed_delta_q`；Python只提供同义observed_delta，跨语言比较q_before/q_next/observed_delta，不能把Python观测差冒充未保存proposal。末步无更新时s/cutoff/rank/update字段保持空/0，异常/迭代上限prefix保留。U/V列符号或简并子空间基不作逐值门；比较奇异值、秩和最终实际更新。

## 运行前冻结的门

1. 同binary plain/trace的status、输入、候选、metrics、accepted_updates解析数值逐值相同；仅mode、trace、wall可不同。若false由wall触发，记录资源UNKNOWN，不换参数重试。
2. Python原重放与历史：status/trace iteration数一致，逐次metric及最终q按下列跨语言数值门比较；旧失败和旧结果不改。C++ trace与Python完整trace的逐次iteration、维度、终止/空更新模式、cutoff数值秩一致。
3. q_before/q_next/observed_delta：绝对误差≤1e-10；g及J前三位置行绝对误差≤1e-8（mm或mm/rad），后三旋转行绝对误差≤1e-11（rad或rad/rad）；sigma abs≤1e-8+1e-10×maxabs；cutoff abs≤1e-18+1e-10×maxabs；metric位置绝对误差≤1e-8 mm、矩阵/角≤1e-11。status/iteration/update模式严格相同。均为移植对照门，**不放宽物理1e-5门**。cutoff/接受边界附近出现秩/迭代/状态差异为UNKNOWN并进入数值根因审查，不放宽门消差异。
4. C++plain/trace精确等价后，对每条trace最终q调用原Python `residual_metrics` 和原机械 `source_limits` 独立重评，位置≤1e-5mm、旋转矩阵≤1e-5，12坐标源3.1416度界逐值合法，不wrap/lift/修复；任何C++CONVERGED但此门失败为soundness阻断。预计64终态metrics额外128次arm FK/J，单独计账；不是额外NR调用。
5. 此Q1不检查碰撞、不固定主动臂/解析分支、无PCS限制挪作NR门。只验证固定64移植和既有物理实现一致，不重新做R1几何/有限差分研究，不证明原KDL轨迹、全环境/全局规划、公平速度、RSS或PCS优势。

参考原轨迹若完全一致，单份64 Python project内部由184×(2arm gj+2arm metric)+64×2arm postchart=864次arm FK/J；加64终态独立metric的128=992次。两C++模式的同结构预计1728次内部arm FK/J。**这些只是预注册结构推算，不是观测的实际started/completed**；header未加内部start hook，不能在实际账中把此预测升级为实测。顶层调用与Python观测记录按真实事件计数。

## 冻结与停止边界

当前新工程recipe和Q1 recipe皆draft，reviews false，不申请或消耗新科学额度。构建和Q1由root在独立审查通过后分别冻结，Q1必须绑定实际binary/manifest/build execution/新source commit及最新全execution账；不能沿用冻结前的MUST_BUILD占位。当前仅有engineer builder可执行入口；Q1调度/比较runner仍需依照本草案实现并独立审查后才能冻结，**该缺口不能用手工零散运行代替**。

参考最新V5：18execution=16科学+2工程；保守R2 wall343.63343315300244/CPU289.461446，余3256.3665668469976/6910.538554。ledger SHA `9162bb167285285c74f492e64c7c15b5a8dc00a44dfb93a32eacdaa76e8e535c`；冻结前重读全execution，预算逐次own cost一次，不复用过期累计。VI B974/974余0，RSS候选不追加。

所有211项、TableI45×500=22500/原1000s、Fig3–5/TableII、APC/NR投影500000、点对50000、被动链数量/局部可见性/复杂障碍/窄通道/固定链消融原完整义务不变；正式TableI仍0。三次同机制有证据修复仍失败进入D079根因审查，保留竞争解释/UNKNOWN，不盲试或放宽门。P4后中文Word/PDF与双FR3适用分析保留，用户审查最新全范围表后才能另议下一任务，不开展P2/Isaac。
