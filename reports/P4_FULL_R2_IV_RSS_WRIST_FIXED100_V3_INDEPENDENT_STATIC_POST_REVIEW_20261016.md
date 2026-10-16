# IV v3/run02 独立静态审查

2026-10-16。审查者 nr_path_prepare，与 v3 实现者分离。35/35 项静态检查通过，未见阻塞；仅表示可进入 root 冻结流程，不代表数学资格通过。所有检查仅使用已保存文件、stdlib AST 与纯算术，未 import 科学模块、运行模型/原生程序、生成协议或 claim。

六个科学函数 AST 与 v2 完全相同。`Qualification.run` 共七条顶层语句，前五赋值和完整科学 For 循环 AST 相同；唯一变化是前置 If 对两种关节界表示分别作精确检查。真实 `physical.source_limits` 文件与 first01 绑定相同，候选实际限位判据原样保留。完整循环 AST SHA256 为 `5d2ff7d1768813455a0c23b9fe133520a9d0206dc897736ea7b77d6259c3c442`。

独立转录原 R1 100 组输入、800 分支编号，与 first01 协议完全相同。q1 literal 正值为 `0x1.921ff2e48e8a7p+1`，runtime 正值为 `0x1.921ff2e48e8a6p+1`，负侧对应相同差异：每侧相差1 ULP，即4.440892098500626e-16rad；其他五关节十边值逐值相同。没有 allclose、epsilon 扩界或候选修角。

first01 仍为 `STOP_PREFIX_RETAINED / RUNTIME_GEOMETRY_OR_SOURCE_LIMITS_CHANGED`，目录只有 events/execution 两文件，事件只有 started/stopped，0 targets/FKJ/K/其他科学查询，800 分支均未执行，protocol/claim/全部绑定 before/after hash 保全。其 wall=0.03671536999991076s、CPU=0.036766999999999994s 已扣原共享30/60帽，run02仅余29.96328463000009s wall、59.963233s CPU。

V10 全部28份 prior（22科学、6工程）路径、hash、各笔自身成本与 fsum 独立核对一致：504.47186458199417s wall、457.738928s CPU。64个绑定资产及7个legacy均匹配；保存diff与实际v2→v3字节diff完全一致。审查时run02未冻结、无claim、无execution。具体绑定SHA及35项明细见同名JSON，后续冻结应保留该原始审查与first01失败。

VI仍974/974、余额0；本审查无新构造、碰撞、RBS、RSS分布或规划资格结论，正式Table I与完整211项义务不变。
