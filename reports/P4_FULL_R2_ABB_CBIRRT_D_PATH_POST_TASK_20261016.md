# ABB CBiRRT D P：413节点完整离散起终路径实际记录

2026-10-16。主任务记录，**personnel_independent=false**；只整理实际保存文件，本稿零新增科学调用。唯一P运行 `20261015_R2_ABB_CBIRRT_D_PATH01`，source commit `c5e4d2e54b06720619dab3670b0a5aa65fdb15b7`，冻结协议 `configs/p4_full/r2_abb_cbirrt_d_complete_path_v1.json` SHA `affe08d5ceafcf374e6adf6256ab45940f177d5acb21a114cf2f98ca9a31d265`，claim SHA `f206f7f05bb0fa51cf4927f7644cb19dfd0a0ffa8636f5b66396ec2bb7e2fbbb`。命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_cbirrt_d_path_draft.py --protocol configs/p4_full/r2_abb_cbirrt_d_complete_path_v1.json
```

实际execution SHA `8e51edb83293d57e9bb8a4d40188d6b9fcf0aff880505f64a8bfb914791df024`，status **PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH**。完成/合格均413/413、full_queue_checked=true、未完成ID与diagnostics空，worker cleanup gate=true。这是运行器内部完整离散资格记录；人员独立物理/保存POST当前**PENDING**，原execution/charge中external_supervision_qualified及independent_path_qualified仍false，不回写或提前授予独立通过。

来源为S02固定环境II、seed7、range2.6的唯一原CBiRRT solve候选，源execution `c7cbd868da1cd9feb149bc057c4a63ff3e722b81123998e1a8cc5e8e1bab5906`，独立入口5284/5284已实际通过。路径类别为 `R2_NUMERICS_D_FIXED_CBIRRT_RECONSTRUCTED_A01_DISCRETE_SOURCE_POLICY_PATH`：使用版本化几何/距离接口修正及**RECONSTRUCTED A01端点**，不将其冒称作者原始端点或未经修正的公开程序直接通过。P没有再运行solve、RBS、IK、NR、投影、随机采样或新VI构造。

原两树6Motion、5milestones，真实连接Motion6→5；四条最终true原M109/145/33/129，416边节点引用按完整binary64去重为413唯一节点/412叶，原full12叶距严格<.05，完整起终点及所有原节点保留，不截尾、不换点。原五次回溯[T,T,F,T,T]、M[109,145,2,33,129]完整保存；原role0/b3 false29266/M2及随后role1/b3 fallback29271/M33不被删除或改判。原save2file文本与高精度trace分别保存，不以低精度文本修角。

本次真实两臂独立FK started/completed各826，branch_identity各826；collision adapter顶层各413、adapter内部FK/J各1652，PQP queries95816。原已验PCS数学循环及counted包装AST完全复用：闭链位置/旋转maxabs各1e-5、原机械限位、所有关联边的被动branch及64epsilon、v3 native/aligned原mesh/pair/PQP8mm判据保持。合格依据仍是aligned原离散source-policy，native结果单独留存；这些计数不混为原solve内部调用。

两个碰撞worker88329/88330（native/aligned）均exit0/reaped，起闭进程组现场快照均单子进程；selector实际关闭、stdout实际EOF drained，pending/tail均空，中央registry与session身份一致、无遗留组。v3 manifest绑定的复用binary路径包含collision_adapter_v2，是版本化manifest中的既有资产路径，不因此改写成新编译或不同判据。完整events SHA `2ae81ff53b04afd0710bae3569df74f5c62db655ca0dca6a3374b9e365f6dd3e`；全部节点原始数学/碰撞响应、source/prior/bound前后SHA和未完成尾部规则保留。

内部样本104.70202309700107wall/11.710718CPU；独占外层GNUtime实际 `104.87 10.53 1.25 0`，Decimal上界**104.88wall/11.8CPU**，正常exit0，满足P120/240与R2原总帽。time SHA `81385f411fddff9e4cf5d6bc65c5b61341378e5694658a97d5d1bace26f6e2fe`、charge SHA `b5cd2a87473c8c5391e4ecaecf194547cf34878506099250cf8408428d8abc07`、receipt SHA `56109261c157186d06b69f331d243cf84358b467c6cec3edea2b62c5de4bc23c`。外层包含导入/preflight、原始保存链核对、413节点物理、清理/hash及execution/receipt落盘退出；supervisor自身记录持久化在范围外。此完整资格开销不能当作论文规划性能或成本pilot数据。独立审查后只以外层上界替换内部样本一次，历史未测尾部UNKNOWN保持；V18账与范围/保全待实际生成后补记，不预填估算数。

即使独立后审通过，也只证明该版本化候选完整起终路径的既定离散资格；不证明连续无碰撞、实体杆/省略碰撞对安全、全局成功率、RSS分布/原RBS资格、PCS复杂障碍优势或完整论文复现。原S01 STOP/已进入solve但无完整结果、原D64 STOP/61完成/UNKNOWN[61,62,63]/末−9/false raw门、split证书边界、原H STOP/30UNKNOWN以及旧PCS177/NR393全部保留。VI974/974余0，正式Table I0/22500、211项论文义务与原统计规模不缩。后续继续其余原生搜索器/环境资格，再做可重复成本pilot与预算申请；不自动大规模规划、P2、Isaac或提前结题Word/PDF。


## 2026-10-16 补记：完整离散路径独立后审、variant边界及V18实际交付

初稿PENDING原文保留为时间记录；实际人员独立物理/保存POST现已交付：`reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_20261016.json`，schema `P4_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_V1`、status `PASS_COMPLETE_DISCRETE_SOURCE_POLICY_CBIRRT_PATH_INDEPENDENT_POST`，**58152/58152、0失败**，SHA `2c548df054867c7d9545fac3726142f3581b3cdfbe54299233a27bb07bace4d0`。external_supervision_qualified与independent_path_qualified均true，continuous_collision_certificate=false。本主POST仍personnel_independent=false，仅引用独立证书；不回写原S02/P execution/receipt/charge中的pending/false字段。

独立后审核完整413节点/412叶、真实两树与桥、原5尝试及四完整M、节点数学/branch/原限位/原raw/碰撞TCP与PQP/双worker回收/费用全链。保存值最大闭链位置4.547473508864641e-13mm、旋转6.730727086790012e-16，最小原机械限位余量.016467847389747492rad，最大叶距.049872908712302065rad。四段实际主动链[0,0,1,1]、被动branch[3,3,3,3]均通过；原role0失败桥与role1成功fallback只是本条路径的切换机制见证，不是PCS优势统计。

独立variant补充 `reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_VARIANT_SCOPE_SAVED_SUPPLEMENT_20261016.json` 实际1659/1659、0失败，SHA `287a9dd1877b17e3cf439aca891c5832869f5b40973e9757f6314c8822be705a`。**native全部413节点存在物理TCP pose mismatch，native_physical_pose_qualified=false**；保存最大translation误差.003531998994674268mm、rotation6.824437533303751e-6。aligned全部413节点pose通过，最大translation3.410605131648481e-13mm、rotation4.440892098500626e-16。两variant原raw collision均0、各47908PQP；原raw collision0不能把native几何不一致改判通过。**本路径只按事先冻结的aligned原离散source-policy接纳**，不是native几何全过，也不由本次临时挑选碰撞策略。原POST保持原hash，补充单独版本化。

V18现已实际生成：36execution=29科学账+7工程，charged累计685.555705375994wall/542.4289229999999CPU，R2余额上界2914.444294624006wall/6657.5710770000005CPU。P外层104.88/11.8仅替换本项内部样本一次，S01等历史失败仍各计一次、未测尾部UNKNOWN保持。ledger SHA `a23faa25bf526276224ada5dd23bd394b896017064e19f499d13a685e8ad46c3`。最新原文完整范围表 `reports/P4_FULL_R2_CBIRRT_D_PATH_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv/.md` 为**211行158列，前154列逐值保持**，CSV SHA `317599526b1cf4ae8db01b27b0516e148966059c5a19c2e4e876781853bac957`。

V18保全现已实际PASS，七组mismatch均空：1028旧科学文件、57崩溃文件8482891B及tar、另5工作树13未提交、旧V17账/保全和211历史列保持；证据 `results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V18.json`，SHA `f5e8afead1255aa9cb3c8cd0215e23a3275af183c75d357dcef0afc47c35db84`。本次完整路径仅环境II的RECONSTRUCTED A01/versioned D-fixed候选。其余原生搜索器和环境仍需逐项资格，RSS分布/原生RBS/入口与VI974耗尽分开处理；随后合格成本pilot与正式预算申请，原211义务/正式0/22500不缩，不自动P2/Isaac。
