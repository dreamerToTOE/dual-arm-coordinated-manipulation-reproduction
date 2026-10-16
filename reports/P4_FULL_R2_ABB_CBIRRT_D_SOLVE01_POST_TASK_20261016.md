# ABB CBiRRT D S01：已进入 solve，transport 中止后的实际记录

2026-10-16。主任务记录，**personnel_independent=false**；仅整理已保存证据，零新增科学调用。实际运行 `20261015_R2_ABB_CBIRRT_D_SOLVE01`，source commit `6ac452b4f6edf0c4b396307c385c64a71073a8d0`。固定环境 II、seed7、单次原 solve；runner `scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_draft.py` SHA `7f0327f56bb86246d22f897743b0b2abad6fd54e9527eb0a55e79fdbe4589a46`，协议 `configs/p4_full/r2_abb_cbirrt_d_single_solve_v1.json` SHA `1635899e7b025d5eaac57acf9e88345b8aa7f9304b4a521e2082129eee138c94`。实际命令由原监督日志完整保留：

```bash
/usr/bin/time --quiet -f '%e %U %S %x' -o /proc/self/fd/3 /usr/bin/python3 scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_draft.py --protocol configs/p4_full/r2_abb_cbirrt_d_single_solve_v1.json
```

实际 execution SHA `99c5cc5e980bf52489b154d5a678df903a1897a1e9e966c341ea6b5229533fdd`，status `STOP_PREFIX_RETAINED`，终止 `JSONDecodeError('Expecting value: line 1 column 1 (char 0)')`。源进程78833确已启动、唯一 solve 请求确已 dispatch；保存 stderr 证明已进入 solve。stdout 只有55字节 setup debug 行，完整结果 JSON **0**；历史 `raw_response_lines_observed=1` 计的是该日志，不能改称一条结果。清理后源返回−9且reaped，完整原raw gate=false。solve完成、EXACT、解、树、M与回溯结果全部 **UNKNOWN**；不能记成零 solve、规划失败或路径通过。

原stdout为 `Debug:   CBiRRT: Planner range detected to be 3.415829\n`，SHA `daa344847b00a40924a64df3aebb4f859fa26327791294bb30f793a0edaba532`；stderr8669B，SHA `884ad123208c452b47dc4e8477ae1ce9bf34c80aff42e6e9c74d446d45d0749c`。真实trace started/completed：mesh_load1/1、identify1/1、native_fk2/2、native_ik16/16；collision1/0（id20 entered未返）。下游未观测保留UNKNOWN。

人员独立POST `reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json`（SHA `2263c58e15b65930fd07d616f0b94c040b3d89e48bab3a46bab6780777de41fb`）实际2688/2688、0失败，审查状态 `PASS_FAILED_PREFIX_PRESERVATION_AND_COST_AUDIT`，科学/transport状态仍 `FAIL_SOLVE01_TRANSPORT_EVIDENCE_INDEPENDENT_POST`。外层exit1原时间 `1.43 0.93 0.19 1`，资格上界1.44wall/1.14CPU，仅证明失败进程身份及费用；successful_transport_qualified=false。原内部样本1.194684555001004wall/1.0460630000000002CPU与原false资格字段保留；外层上界替换本项计费一次，不能相加。

独立源码诊断及实际libompl静态补证（`SOLVE01_STDOUT_SOURCE_DIAGNOSIS`、`SOLVE01_STDOUT_LIBRARY_STATIC_SUPPLEMENT`）确认我方接收器把 setup 日志当JSON。driver 的 planner->setup() 在 Redirect quiet 作用域外，OMPL DEBUG输出走std::cout；solve/getPlannerData在Redirect内。本次是我方transport缺陷，不归因作者算法或论文数学。setup临时自动range3.415829；原solve开头setRange(Range)恢复**实际grow range2.6**，不是科学参数变化。原runner、源、失败、claim和全部raw不回写。

root已保存V16：34execution=27科学账+7工程；累计charged571.125705375994wall/521.878923CPU，R2余额上界3028.874294624006wall/6678.121077CPU。历史未监督尾部费用UNKNOWN保持。`P4_FULL_R2_CBIRRT_D_SOLVE_STOP_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv/.md` 为211行150列，前146列保持；V16保全passed=true：1028旧科学文件、57崩溃文件8482891B及tar、另5工作树13未提交、旧V15/历史列无mismatch。ledger SHA `b71f500b9d02a7fa51ab07b8b9835acf0f68a4863c88e4561962aa25677afeac`。

下一项S02仅版本化接受一次已审55字节前缀再等唯一JSON，另行冻结；沿原30wall/60CPU共享余额**28.56wall/58.86CPU**，不重开预算、不改binary/driver/算法/seed7/范围2.6/10秒solve或判据。本记录未执行S02。即使原EXACT返回，也只为路径候选，仍须P独立完整路径门。原D64 STOP/61完成/UNKNOWN[61,62,63]/末−9/完整raw=false、split证书边界、原H STOP/30 UNKNOWN、旧PCS177/NR393均保留。VI974/974余额0、正式Table I 0/22500、全部211项论文义务与统计规模不缩减；不启动正式大规模、P2或Isaac。
