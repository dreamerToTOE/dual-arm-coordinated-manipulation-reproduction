# P4 R2：旧 II/III/V RSS 48 分支碰撞补检实际结果独立复核

2026-10-15。实际冻结的 48 个旧数学合格分支均完成补检：**II 10 clear / 8 collision；III 16 clear / 6 collision；V 0 clear / 8 collision**。这里的 clear 仅指通过选定 aligned 原网格离散 source-policy；不能据此宣称完整 RSS、RBS 或规划资格。

本独立复核只读取保存输入/输出/位姿/计数并计算哈希及 TCP 高度比较。新增 FK/J、IK、NR、随机、碰撞和规划调用均 0；未重选候选、未改已绑定 PRE/runner/config、未提交。

## 版本与输入保全

Run：`results/p4_full/20261015_R2_SAVED_RSS_COLLISION01`；实际源码提交 `ca2c5537f81392c23e4931594fdecbe3db90f6d4`。

- Runner SHA256：`ad6a30f253ee28b99002547f54b0235b0a570320d3699ab994d180fa432c6481`。
- 冻结配置 SHA256：`0c4dd6276093593c0f7012042300e9f385392fdbc0d325cdcaf7d4a203a80d78`。
- execution SHA256：`f06a0afa82da9cea66224d7b2e438673570aabbefb022c8b00fffedd02ab5f8f`。
- events SHA256：`56023564d587462fd5c38df9ec6dd089d4e3ecf08678200bcae2fca6453501fb`。

177 项来源、旧输入/日志、原 source/mesh/binary 与11份 prior execution 的运行前、运行后、当前文件 SHA 全部一致，且等于冻结配置。48 个保存原 observation 的规范 JSON SHA、source_index/mode/branch/原数组下标/input_line、12 角与本次 fixed_case 均逐值一致。只取原 `qualified_closure_rank_bounds_only=true` 的 II18、III22、V8，顺序仍为 II→III→V 与各原 observation 下标升序；旧700目标/5600IK与原 mode0 FAIL、原候选 collision_checked=false 记录原字节保留。

48 个实际子进程输入与 fixed_case 的环境、case_id、12角逐值相等；stdout 等于保存结果对象，stdout/stderr SHA 与 process_finished 记录逐一匹配，退出码均0。每份 stderr 独立记录4次 FK/J started/completed，arm 顺序 `[1,2,1,2]`、环境及6角均与固定输入相等；无中断、重试、替代或未完成尾项。

## 实际结果、计数与物理对齐范围

|环境|旧数学合格分支|选定策略 clear|选定策略 collision|具有 clear 分支的旧目标数|native / aligned PQP pair 调用|
|---|---:|---:|---:|---:|---:|
|II|18|10|8|3/7|2088 / 2088|
|III|22|16|6|5/8|2214 / 2214|
|V|8|0|8|0/4|696 / 696|
|合计|48|26|22|不跨环境合并为采样成功率|4998 / 4998|

这里“旧目标”以 `(source_index, mode)` 去重；分支与目标均来自预先保存的确定性分层组件输入，不是独立新增 RSS 随机试验。事件独立计数为48 candidate_started/returned/finished、48 process_started/finished。实际 **48 逻辑 adapter 调用、96 native/aligned 源查询、192 adapter 内部独立 arm FK/J started/completed、9996 PQP pair 调用**，与执行账目一致。所有 query_codes 为0，表示 PQP API 调用没有错误，**不表示这些 pair 均无碰撞**；collision 判定来自独立保存的 native_result。

II 每次116 pair；III为20次103 pair及2次77 pair（每个 variant 均如此）；V每次87 pair。只报告实际源程序调用数量，不补齐或改写原控制流。

native 与 aligned 在这48个候选上的布尔碰撞结果完全相同，但 native TCP 对照48/48未通过既定物理位置门；不能因此声称 native 坐标已合格。native TCP 最大平移差分别为 II `0.0043392222671911895 mm`、III `0.0041152630862910655 mm`、V `0.015427453546834613 mm`。已有物理基座对齐的 aligned TCP 对照48/48通过，最大平移 `4.547473508864641e−13 mm`、旋转矩阵元素差 `2.220446049250313e−16`。原与对齐版本分开保留，本组结论使用预注册 aligned 门；没有将工程对齐冒称作者原生程序运行等价性。

## V 的保存 TCP 高度诊断与无法定位的碰撞原因

V 的8分支来自4个旧 wrist-only mode1目标，各目标原 active branch1/3 的保存 TCP 高度相同。下表只对已保存 aligned 独立 TCP 的 z 值进行原 `checkEE` 所述“两 TCP 均 ≥10mm”比较；**没有调用原 source checkEE，也没有重新 FK**。保存 native/aligned collision TCP 的高度与表中值仅有约1e−13mm浮点差。

|source_index|原分支|arm1 TCP z / arm2 TCP z（mm）|保存值的 ≥10mm 诊断|实际源碰撞|
|---|---|---|---|---|
|10|1、3|−660.4085200396074 / −237.40893613126258|不满足（2分支）|两分支均 collision|
|45|1、3|22.253816326850426 / 360.74234058669447|满足（2分支）|两分支均 collision|
|50|1、3|1359.8914295476511 / 1388.228210897805|满足（2分支）|两分支均 collision|
|71|1、3|602.8480492835682 / 917.2224659818619|满足（2分支）|两分支均 collision|

因此2分支另有保存 TCP 高度不满足的证据，6分支满足该高度条件仍被实际碰撞策略拒绝。高度条件与碰撞谓词分别报告；不能用高度诊断替代碰撞查询，也不能据此定位某机械臂、地面或障碍 pair。

保存 source_stdout 每查询只有聚合 `P4_COLLISION_RESULT` 一行，包含 native_result、CPU、poses、query_codes；**没有碰撞 pair 身份、距离或逐 pair CloserThanTolerance 结果**。全0 query_codes 是 API 错误码，不是碰撞 witness。故本证据不能确定 V8 的具体碰撞根因、哪个 pair 首先触发、是否存在源 mesh/frame/pair 模型问题，也不能把碰撞归因为 EE 门（本次没有执行该门）。

当前根因状态为 **UNKNOWN / 缺少 pair 级证据**：保存候选可能确实与原环境物体/自身发生源定义的接近，也不能仅靠这些聚合数据排除源碰撞几何或适配物理解释的偏差。此组未得到 V 的 collision-clear 正控，故 V 的 RSS 有效样本资格仍未恢复；**0/8 不能外推原 wrist mode1 整体无解、RSS方法无效或论文数学错误**。任何后续 pair 级诊断或扩展资格都须先冻结新的有限方案和账目，不在本复核中追加查询或重选样本。

## 资源账目与下游边界

实际墙钟 **13.069952120997186 s**、CPU **12.882596999999999 s**，在30wall/60CPU帽内。11份 prior execution 的实际值之和为 `82.2954052690011 / 32.175436 s`，只加本次实际值一次，R2累计为 **95.36535738999828 s wall / 45.058032999999995 s CPU**；余 **3504.6346426100017 s wall / 7154.941967 s CPU**。

本组新候选构造/IK/NR/RNG/RBS/规划均0。仅扣原 R2 总预算，不扣 VI B 专项预算；B仍余50构造、125.48601753600087wall秒、346.67282300000005CPU秒。旧原始失败与未运行的全文实验义务均不改判。

II/III 获得的是这些保存分支的数学资格加 selected source-policy 离散碰撞正例；桥接、完整原 RSS 分布、RBS与正式规划仍待验证。V保存8分支均真实碰撞拒绝，碰撞正控/具体原因与可信新资格路线待审。原 VI Q2 UNKNOWN与既有6fiber组件通过的范围均不受本组影响；不自动进入大规模规划、P2或Isaac。
