# P4 R2 NR Q1 科学runner/worker独立静态二审

2026-10-15。结论 `PASS_STATIC_PRE_FOR_ROOT_FREEZE_ONLY`。未发现阻止该固定64输入、192顶层上限的有限移植资格进入root冻结的明显逻辑问题。审查只读源码、协议、保存数据和文件哈希，未编译、运行C++、启动Python worker或调用任何模型/NR/碰撞/planner。该结论不是科学PASS，不批准正式规划。

## 绑定版本与现有实际工程

|对象|SHA256|
|---|---|
|`scripts/qualify_p4_full_r2_nr_abb_q1_draft.py`|`4dbc25240aaf63fe40d9f04d7703f442f2af9332944c758e5b4da05f528592bf`|
|`reports/P4_FULL_R2_NR_ABB_Q1_RUNNER_PRE_DRAFT_20261015.md`|`ce96b7c3b16f96284179f24c133214a205dadc29704fa117fd07654e3312e311`|
|`configs/p4_full/r2_nr_abb_q1_qualification_v1.draft.json`|`1c2e2fb1eefbdf662f64d314e0a41d00c36bfb83238f833aee348d11eeac81e4`|
|实际C++ binary|`d4a60b5e67ba19016f7ec54d3b9f4ea5bb76a1738fb0c169b27e9a04961e7687`|
|实际build manifest|`fa02e29069a1723107d771f723b2d854bef4d7eddf0cb188e3ea95ac62fc45f1`|
|实际build execution|`53bd4479d42d92698eaaedc918e4d994c92e8c5cdbb37edbbcd4a96736709f4e`|

工程source为 `35246c34bac6d65b8002e06d97101694efe3e11d`，状态BUILT_NOT_QUERIED，wall8.80554415199731、CPU12.280458秒。审查逐个重新hash协议922项绑定文件，922/922匹配；协议含19个prior execution，自身耗时累计wall352.43897730499975、CPU301.74190400000003秒。当前Q1 run目录/claim不存在，draft frozen=false、三review=false，不存在本项科学前缀需要重跑。

## 输入、调度与观测边界

runner固定从原SPATIAL01 II/III全部nr_reference观察重建case，逐项核对原审核清单、observation index、输入、状态、候选和metric trace；II32/III32、64独立case ID，plain64→trace64→原Python64，最大192顶层。原源码及独立ABB oracle的SHA固定，没有新样本、RNG、成功筛选或替换。每个有限C++最终候选独立physical metric只重验一次，最多64metric/128armFK/J；不是新的NR调用。

plain/trace调用同binary内核，比较除wall/trace外完整结果精确相同；跨语言比较q/g/J、谱、cutoff、rank、迭代/更新模式和末态，数值门与PRE一致。Python原重放与每项历史status/iteration序列精确比较，候选和逐metric按同一绝对门，差异UNKNOWN并阻断transfer PASS。没有硬编码184次检查/120次更新作为新执行数量。

Python为单独serial JSONL worker。原project_nr/closure/residual/SVD函数本体不替换；仅arm_fk_jac加不增加模型求值的started/completed日志wrapper，finally恢复。原function code的sys.settrace只复制已经计算的量；proposal与observed rounded delta分列。logger错误不会改变原solver数值，但observer_errors会在响应保全后立即阻断后续科学调用。

## 资源控制与中断保全

parent使用原RunBudget加live process-group CPU工具，监视C++与Python worker，60wall/120CPU取R2余额min；Python observer吞回调异常不能吞parent预算。每次serial request bytes发送、响应raw bytes、parsed JSON、stderr事件先保留，随后解释。超帽kill进程组，dispatch未return调用UNKNOWN，C++未return内部trace明确UNOBSERVED，不能用历史步数补填。

worker独占token拒绝第二次启动；固定run/claim和输出文件exclusive创建，无retry/resume/reset。响应索引/请求/模式/schema严格核对；输入/执行源/build/依赖/prior运行前后hash匹配，证据/清理错误及后处理超帽均不能PASS。Python FK/J实际started/completed从已保存worker事件计数；C++内部数量明示未观测，不由结构预测升级为实测。

一次parent setup中导入旧common模块会在RunBudget构造前载入NumPy；其耗时已由outer clock/CPU纳入本项，随后立即调整deadline，若已超帽则停止且不能PASS。该段没有模型调用。报告应按实际setup记录，不宣称SIGALRM已覆盖导入前的每一条语句；这不构成当前有限数学资格的额外机器人试验门。

## PASS语义及下游边界

最终标签仅 `PASS_FIXED64_NUMERICAL_TRANSFER`，还要求全部64比较、64历史重放及“C++报告CONVERGED蕴含独立物理资格”soundness门。CONVERGED与物理合格数量另列；仅同失败不能被写成投影能力PASS。当前历史全CONVERGED，逐case历史/status门亦会拒绝新状态退化。

通过后仍不证明原KDL逐轨迹、原GD/RBS接缝、随机空间能力、碰撞、全局规划、公平速度或其他四环境。VI974/974余0，本项VI候选0；TableI正式0/22500及211项完整义务不变。root应将实际build、冻结commit、Q1结果和最新账目分别登记，本报告没有科学执行可计账。
