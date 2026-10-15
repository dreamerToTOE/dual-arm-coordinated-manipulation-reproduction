# R2 II/III NR Q1：独立保存证据 POST 复核

2026-10-15。**PASS_INDEPENDENT_SAVED_POST_REVIEW；14272/14272项检查通过。** 本审查只使用Python标准库读取已保存JSON/JSONL、原始stdout/stderr、Git blob及文件哈希；不导入科学runner、NumPy、FK/J、SVD、NR、IK、碰撞、RBS、RNG或planner，不增加任何科学调用或重复扣资格运行成本。

## 真实执行与来源

原资格执行source为`c68fa7605a94eb07f7588e850b95980b62bc0c8f`，run为`20261015_R2_NR_ABB_Q1_01`，实际wall **7.05127794699365秒**、CPU **7.9173490000000015秒**，低于本次60wall/120CPU及原R2总帽余额。资格runner、observer、原Python reference和冻结协议均与执行提交blob一致；冻结协议、claim、实际工程binary/manifest/execution、原64输入和全部**922个绑定资产**的before/after/current链均一致。实际19prior的own cost为wall352.43897730499975/CPU301.74190400000003；本审查不将其中累计时间重复相加。

原输入逐条从SPATIAL01 II/III的全部`nr_reference`重建，II32+III32，与inventory和本次协议完全一致，无筛样或新输入。三个独立串行进程的完整request bytes、原stdout与逐份raw response一致：C++plain64→C++trace64→Python原函数64，共**192派发/192返回**；随后同Python worker独立终态64项返回。无多余request、stopped事件、未返回调用、未完成尾部或清理错误。

标签是`RECONSTRUCTED_PHYSICAL_FULL_NR_CPP / FIXED64_TRANSFER_ONLY`。这是既有NumPy物理全链NR的项目自有C++移植资格，不是原作者KDL迭代轨迹，也不改变旧R0/R1/R2失败。

## 逐步、历史与物理门

C++plain/trace去除trace和计时后所有解析值完全相同。C++trace与原Python状态/iteration/update模式一致；原Python新重放与每项历史状态、iteration序列、候选和metrics均通过固定门，历史候选逐坐标差为0。完整逐项trace保存**184次检查、120次更新**，每项最多3次检查；这些数字由本次实际日志得到，没有把历史184/120写成预期总数。所有实际更新保存的数值秩均为6，终止无更新的空谱/空delta单独核对，不把其占位rank0当数学降秩。

| 跨语言量 | 保存证据最大逐项绝对差 | 冻结比较门 |
|---|---:|---:|
| q_before/q_next/候选/observed_delta | 8.881784197001252e-16 rad | 1e-10 rad |
| g位置 | 3.979039320256561e-13 mm | 1e-8 mm |
| g旋转 | 1.5168090037025878e-15 | 1e-11 |
| J位置行 | 4.547473508864641e-13 mm/rad | 1e-8 mm/rad |
| J旋转行 | 6.661338147750939e-16 | 1e-11 |
| singular_values | 3.183231456205249e-12 | 1e-8+1e-10×maxabs |

审查独立从已保存q恢复observed_delta、相邻迭代q连续性、谱顺序/cutoff/rank及原观测事件流，未重新求SVD或投影。proposal与observed_delta分别核对，不将浮点落地差伪称原Python未保存的proposal。所有comparison/history/final文件、summary副本及其逐项verdict与独立复核一致。

两C++模式和原Python各**64/64 CONVERGED**；独立终态物理门**64/64通过**。原位置门1e-5mm、旋转矩阵门1e-5和原3.1416机械界均未改。保存终态最大位置残差 **8.342067303601652e-7mm**，最大旋转矩阵残差 **1.50461743064767e-9**，最大旋转角 **1.6322179798507961e-9rad**；最小源限位余量 **0.07996374640843196rad**。审查从保存候选和原度界重算限位余量，从已真实计算的metric复核原闭合门，没有在POST重新求FK或宣称新独立模型计算。

## 真实计数、预算与限制

worker的每条STEP_SNAPSHOT/STEP_UPDATE与返回trace逐值一致。原Python内部arm FK/J **864 started/864 completed**；额外64终态metric内部arm FK/J **128/128**，独立metric **64/64**。这992次是实际事件计数，逐case臂顺序与原函数每轮closure/metric及收敛后chart重评结构一致。C++内部没有start hook，保持**UNOBSERVED**；trace可见完成更新不能冒充全部内部started/completed测量。原NR本体/closure/residual/SVD不替换，只有arm_fk_jac做事件before/after wrapper且finally恢复，无额外数学求值。

Python参考和终态在单worker内串行，由父进程wall/live group CPU硬帽与killpg监控，observer异常不能吞掉父进程预算；本次observer_errors为空。父进程common模块导入在RunBudget安装SIGALRM之前，outer clock仍计入该setup成本，之后即检查余额；此段无模型调用，不把它描述为已受同一异步alarm守护。清理与后哈希计入实际own cost。

本阶段仅支持**固定near64数值移植一致性**，同时这64个候选独立物理资格通过；不是所有随机输入投影能力、原GD/SVC/RBS接缝、全局NR规划、碰撞/CCD、其他四环境、公平速度或PCS优势证据。正式Table I仍0/22500，全部211项全文义务、图表、三规划器、复杂场景与消融均保留。下一步应独立冻结NR真实GD/RBS接缝资格；不自动进入P2或Isaac。

## 复核产物与哈希

- 独立JSON：`reports/P4_FULL_R2_NR_ABB_Q1_INDEPENDENT_SAVED_POST_REVIEW_20261015.json`，SHA256 `ac586e9b5e3f68b5ce445cc7b65204a6c2e378b3337524f147784e138a92df49`。完整14272项证据约22.48MB，保留原字节。
- stdlib-only审查脚本：`scripts/audit_p4_full_r2_nr_abb_q1_saved.py`，SHA256 `2bbea56a6fa2dec509ba35d70b346d079d1ab14bf99ee2d7e8cd365a64a30896`。
- 原资格execution：SHA256 `e2e545675f48b14981846c145820ca9450a75f7ce0d835d6d3746ebeefd24340`。
- 冻结Q1协议：SHA256 `764382ebf9d022de2370cda86a9f091ef7c61f54966c56071a7faf85f31ce15c`。

只读执行命令：

```bash
python3 scripts/audit_p4_full_r2_nr_abb_q1_saved.py --protocol configs/p4_full/r2_nr_abb_q1_qualification_v1.json --output reports/P4_FULL_R2_NR_ABB_Q1_INDEPENDENT_SAVED_POST_REVIEW_20261015.json
```

该命令已完成一次；原输出exclusive，不覆盖。未做任何新的科学重放、调参、编译或提交。
