# ABB CBiRRT D S02：原生 EXACT 候选与独立路径门待审

2026-10-16。主任务记录，**personnel_independent=false**；读取实际保存数据，零新增科学调用。实际运行 `20261015_R2_ABB_CBIRRT_D_SOLVE02`，source commit `4065ac6d00c2ae73a5147e193fa249b7d69cf148`。固定环境II、seed7、range2.6、原单次10秒solve、原端点/几何/判据不变。v2只修我方stdout接收契约：精确保留一次已审55B setup行，再接收唯一JSON；原binary/driver/算法未改。协议 `configs/p4_full/r2_abb_cbirrt_d_single_solve_v2.json` SHA `4220791572538287371c30800adfae6ce98f651383f3aca62b3758a85db4d8a0`。命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py --protocol configs/p4_full/r2_abb_cbirrt_d_single_solve_v2.json
```

实际 execution SHA `c7cbd868da1cd9feb149bc057c4a63ff3e722b81123998e1a8cc5e8e1bab5906`，status **SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT**。唯一源进程85119、唯一solve dispatch，正常exit0/reaped；stdout恰两完整行：一次原setup前缀和一次完整JSON，无diagnostic，完整原raw gate=true。原返回exact=true、has_solution=true、approximate=false、solution_count1、difference0。这是原生求解候选，**independent_path_qualified=false**；人员独立入口/保存后审和完整路径物理审查当前PENDING，不能以本稿或EXACT直接宣称合格完整路径。

原树6 Motion，planner_data6顶点/5边，solution5 milestones。全部5次state-level reconstruct原始结果顺序 **[true,true,false,true,true]**，M节点数 **[109,145,2,33,129]**。第三次role0/branch3返回false、M只留2端点；原save2file随后role1/branch3 fallback返回true，保留失败与成功完整证据，未删除失败或强制重构。四段实际选取、方向、接口缝合、闭链/branch/限位/原碰撞与叶距离仍待独立P核验，不将任意两点失败输出算成功边。

真实原trace started/completed均配对：activeDistance367、collision4682、fixed_branch_project4527、growTree364、identify108、native_fk5254、native_ik6024、save2file1、state_rbs114/vector_rbs7954、state_reconstruct5/vector_reconstruct821；另构造mesh_load1/1。计数只是原源内部trace，不是人员独立物理查询或plain/trace对照。库内部RNG种子draw/member初始化真调用未插桩部分保持UNOBSERVED。solve返回内测0.512958872秒含原save2file及观测I/O，**不作论文性能样本**。

原stdout14050348B，SHA `594e6614121bf7955f3fcd77dc1133d05849b9a75414569ccabdc95ab30755d5`；stderr15761808B，SHA `973c6250a9a55e9d9e5dad9bceaca5b5418d3be58271d92f9d34286d2ab98d39`；evidence SHA `c297a6a8c9f3107bf756e70381eedca7b3799d5ef78b283eaeca35b84aa885df`。五份原生path/ik/milestone/perf/temp输出已fsync并hash绑定；原path.txt保持原精度，未替换成高精度拼接结果。

外层GNUtime原行 `9.54 7.85 0.88 0`，Decimal上界9.55wall/8.75CPU；原内部sample9.358301447005942wall/8.646851CPU、receipt及charge保留，external_supervision_qualified=false，待人员独立后审。S01原失败外层1.44/1.14加本次9.55/8.75，原30wall/60CPU共享累计 **10.99wall/9.89CPU**，未重置。计费上界只替换本execution内部样本一次，不能相加；root的V17实际账、范围表及保全报告待落盘后另补，不预填未保存结果。

原S01 STOP/JSONDecodeError/源−9与UNKNOWN永久保留；S02完整返回不回写其失败。原D64 STOP/61完成/UNKNOWN[61,62,63]/末−9/完整raw=false、split证书边界、原H STOP/30 UNKNOWN、旧PCS177/NR393证书保持。VI974/974余0，正式Table I 0/22500、全部211项论文义务及原统计规模不缩减。本项不证明连续无碰撞、全部实体碰撞对完整、全局成功率或PCS性能优势。下一关是人员独立保存后审及P原路径资格，尚不启动正式大规模实验、P2、Isaac或提前结题Word/PDF。


## 2026-10-16 补记：独立入口审查及V17已实际完成

上文PENDING为初稿保存时状态，历史原文保留。实际人员独立POST已保存：`reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_SAVED_INDEPENDENT_POST_20261016.json`，schema `P4_SOLVE02_SAVED_INDEPENDENT_POST_V1`、status `PASS_SOLVE02_TRANSPORT_EVIDENCE_INDEPENDENT_POST`，5284/5284、0失败，SHA `730dbb69ff3749975639dd9cad2fe1f31ca45cb2bf370c0470cfddd329d64412`。personnel_independent、external_supervision_qualified及successful_transport_qualified均true，确认唯一完整响应/原raw/源exit0、真实费用及版本；**independent_path_qualified仍false**，不将入口通过冒充物理完整路径。原false bridge29266/M2及fallback29271/M33保留；四真M109/145/33/129按原连接关系完整拼接为413唯一节点/412叶，尚未执行独立物理P。原execution/receipt/charge false字段不回写。

独立外层上界9.55wall/8.75CPU；共享S01+S02累计10.99/9.89。root实际V17为35execution=28科学账+7工程，charged580.675705375994wall/530.628923CPU，R2余额上界3019.324294624006wall/6669.371077CPU；每execution只计一次，旧未测尾部UNKNOWN保持。ledger SHA `10b7d97d485e6a28bcb5760cce2cb1f2d5ca920884531bb456e6de749e6dea8a`。最新完整范围表 `reports/P4_FULL_R2_CBIRRT_D_SOLVE02_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv/.md` 为211行154列、前150列保持。V17保全passed=true，无mismatch，证据SHA `b51b534748924d3cebcd6e43e7a0b4bbdd46ef762a3588391b89f1d060996d77`；旧科学/崩溃文件及其他工作树完整保留。主POST仍personnel_independent=false，仅引用独立审查；下一关P全413节点/412叶的固定独立物理资格，不截尾、不重新solve，120wall/240CPU及最多2048节点须最终冻结后才执行。
