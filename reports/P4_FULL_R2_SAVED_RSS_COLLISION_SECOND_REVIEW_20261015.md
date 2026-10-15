# P4 R2 旧48分支碰撞续验的第二独立只读复核

2026-10-15。复核 `20261015_R2_SAVED_RSS_COLLISION01` execution、48份结果、48输入/stdout/stderr、events、冻结协议和原 observations，并对照 `P4_FULL_R2_SAVED_RSS_COLLISION_POST_REVIEW_20261015.md`。**未发现结果或范围误报；0处来源/数组/输出矛盾。** 未调用 FK/J、IK、NR、碰撞、随机采样、RBS或规划，未修改旧文件，未编译或提交。

177份绑定文件在冻结协议、execution前后哈希与当前文件中全部相同。48个旧 observation 的 canonical JSON SHA、原12角、mode、source_index、branch、数组下标与本次 fixed_case 逐值相同；48个进程实际输入/保存 stdout 对象与其固定候选相同，stdout/stderr SHA和退出0相符。48项 started/returned/finished与48个 process started/finished唯一对应；192个内部 arm FK/J开始与完成均实际留在stderr，顺序为每候选 `[1,2,1,2]`。

| 环境 | 旧数学合格分支 | 选定aligned clear / collision | 原数学合格目标数 | 有clear分支目标数 | native / aligned pair查询数 |
|---|---:|---:|---:|---:|---:|
| II | 18 | 10 / 8 | 7 | 3 | 2088 / 2088 |
| III | 22 | 16 / 6 | 8 | 5 | 2214 / 2214 |
| V | 8 | 0 / 8 | 4 | 0 | 696 / 696 |

目标用 `(source_index, mode)` 去重。48分支属于旧700固定目标/5600 IK中19个数学合格目标；表中3/7、5/8、0/4不能冒充原300、300、100目标的RSS新随机采样成功率，也不能将同一目标的多个根当作独立试验。

**PQP API返回0不等于clear。** 实际96个native/aligned查询包含9996个pair API返回码，均0；但22个逻辑候选的保存 `native_result=1`、实际 `collision=true`。传输驱动保存的是 `PQP_Tolerance` 的API返回值；源碰撞谓词另读 `CloserThanTolerance()` 并聚合为 `native_result`。没有pair身份或各pair碰撞布尔/距离证据，不可据全0码定位V碰撞根因。

**native与aligned资格不同。** 48个native TCP物理位置对照全部失败，48个aligned全部通过；各逻辑返回均 `selected_variant=aligned`。native最大平移差 II=.0043392222671911895 mm、III=.0041152630862910655 mm、V=.015427453546834613 mm；aligned三环境最大值为4.547473508864641e−13 mm。两变体碰撞布尔在本批恰好一致，也不能据此把native坐标改判合格或声称原生执行等价。

**原checkEE没有执行。** 保存 execution 所有 `original_source_EE_executed=false`；worker只调用既有 collision adapter，驱动只运行 `collision_state`，没有调用源 `checkEE`。V只读已保存独立TCP高度，source_index10的两个分支不满足“两TCP均≥10mm”，45/50/71的六分支满足；实际8项均collision。这是两个不同谓词的证据，不定位碰撞原因，不证明V wrist模式无解。报告保留了该边界，表述正确。

执行账实际为13.069952120997186秒墙钟、12.882597秒CPU，R2累计95.36535738999828/45.058033秒；没有重复累加cumulative字段，也没有扣VI B预算。第二复核纯保存归约另外测得墙钟2.144733380999秒、CPU2.144774秒，科学调用0，不作为实验候选或FK次数。

复核输入版本：execution SHA `f06a0afa82da9cea66224d7b2e438673570aabbefb022c8b00fffedd02ab5f8f`；冻结协议SHA `0c4dd6276093593c0f7012042300e9f385392fdbc0d325cdcaf7d4a203a80d78`；原POST SHA `5fc0672fbc8513f551c102fbef512676235ce9c6e4e9022886bda9c9efeb0727`。旧Q2 UNKNOWN、V碰撞根因UNKNOWN及所有全文统计义务均保持。
