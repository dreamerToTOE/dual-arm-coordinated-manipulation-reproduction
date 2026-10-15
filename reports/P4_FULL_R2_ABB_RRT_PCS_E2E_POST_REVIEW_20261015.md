# R2 ABB 原 RRT_PCS 单次执行：独立保存证据 POST 审查

日期：2026-10-15。结论：**SOURCE_TRACE_PROVENANCE_PASS_PENDING_INDEPENDENT_PATH_AUDIT**。本审查仅读取文件、Git blob、完整保存数组与计数器，并计算数组距离；0 FK/J、0 IK、0 NR、0碰撞、0 RNG、0 solve、0编译。源求解器返回 Exact solution 和回溯完整性均得到保存证据支持；**尚不能把该路径标为物理资格 PASS**。

证据明细见同名 JSON（SHA256 `ab7dd727ecae8552ec606f99396e0eaab53c793330a27c1c814750ad564a9690`）。绑定执行为 `results/p4_full/20261015_R2_ABB_RRT_PCS_E2E01/execution.json`，source commit `1a5b811b61be61dea80f8183f123379d167fd3f0`；result SHA256 `eefb6673101fe7a4a47f319bac5e8a20498ae1cee88930ec7bca710ce8de45b4`。

## 来源与原程序本体保全

独立重算 before/after 各129资产、5份自有源码及提交blob、2端点、32运行保留文件、16先前execution的所有SHA256，全部一致。冻结science protocol、claim、engineering recipe/claim、manifest、binary及编译执行链一致。manifest与工程execution的科学/工程字段完全一致；仅各自保存另一文件位置和manifest SHA的非自引用元数据不同。16先前执行成本用 `math.fsum` 与冻结预算基线逐值一致，不重复扣账。

在内存中删除state级 `reconstructRBS` 与vector级 `identify_state_ik` 的返回后观测包装，得到与旧plain `StateValidityCheckerPCS.cpp` 整份文本相同；两原body各仅保留一次。`RRT_PCS.cpp` 仅 `remove(temp.txt)` 改为保留原文件注释；APC与collision源字节相同。没有修复helper、投影算法、RBS、分支、碰撞判定或原采样箱。

## 完整源路径与树

原seed7、Range2.6、goal bias .05、always-true主程序validity callback、12维原采样界和A01各自原分支端点均与冻结request完全相同。源返回 Exact solution（code6），非approximate，solution_count1、difference0；4个milestone，6个树节点，5条有向边。选中树路径是 `1→2→5→0`，每条选中边存在，所有其他树节点也可由start1到达，树的其他试探分支完整保留。

| 顺序 | active_chain / branch | 完整回溯节点 | 最大相邻12维L2距离 |
|---|---|---:|---:|
| 0 | 0 / 3 | 80 | 0.04949053472601928 |
| 1 | 1 / 3 | 65 | 0.04617935003996265 |
| 2 | 0 / 0 | 34 | 0.04805629905574112 |

全部3次原state级回溯已完成且返回true；JSONL与result数组逐值相同，首尾严格等于相应milestone，milestone首尾严格等于冻结起终点。拼接后177节点、177唯一节点、176叶，全部叶距离严格小于.05。原低精度 `path.txt` 首行177，177行关节数组等于完整double trace各值的默认6位有效数字输出；末尾空行保留。资格必须使用17位完整trace，不能使用该低精度文本代替。

实际选中路径的role序列0→1→0提供2次原PCS角色切换见证；不能由此推断PCS复杂场景优势、论文统计或路径物理合格。11次原vector identify返回均有连续索引和完整日志；两端返回[3,0]/[0,3]。仅观测**已完成**调用；真实started、内部FK/IK/PQP调用数仍为UNOBSERVED，不能用预算上限或完成数补造。

## 原计数器、运行成本与警告

`perf_log.txt` 的16项为 `[1,4.25219,.012,628,.003,639,.014,628,4,6,.010001,10,5,0,0,0]`。628位于原 `IKproject` 入口增量，**不是** `IKsolve_rob` 的总调用数：一个projection可尝试两个解析分支调用，identify也可在此计数器外调用IK。639为原source collision计数器，不是独立观测PQP query次数。保存数值如实记录，不用其构造未经观测内部工作量。

source `total_runtime=.012` 是到保存/回溯前的CPU段；其余累计计数/计时保存于回溯之后，driver `solve_wall_s=.016837364` 含原solve内部保存/回溯。因此collision .014大于total .012不是可直接比较的同域时间，不作速度结论。执行总wall `.2776374349996331`、CPU `.19540999999999997`；工程build另计wall `17.12737691100483`、CPU `23.727903`。

stderr保留638条PQP `BeginModel` 警告，未覆盖/删除；这是原source loader行为的记录。本次零碰撞审查不能判断其物理影响，后续独立v3 aligned collision审查必须决定177唯一节点是否合格。setup时自动range日志不等于solve生效范围，原solve在循环前setRange(2.6)，request与结果也保存2.6。

## 明确尚未通过的门

独立177节点物理闭链、12角原机械限位、每条边被动解析分支meeting-set及v3 aligned离散碰撞仍待实际执行。本报告不消耗该资格预算，不启动重复审查，不提前PASS。完整trace既已保存，若独立门失败，保留原source Exact与具体失败节点并分别报告。

此次只有1次资格solve，Table I正式调用仍0/22500，VI新增构造0。211条完整原文义务、三规划器、Fig.3–5/Table I–II、投影/可见性/被动链数量/复杂障碍/窄通道/固定链消融等全部保留。独立path结果完成后再新增V5实际账和211行范围快照，旧账本和所有原73列逐值保留。
