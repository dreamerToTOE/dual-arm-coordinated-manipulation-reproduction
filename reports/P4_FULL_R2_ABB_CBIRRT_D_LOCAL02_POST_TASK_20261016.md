# ABB CBiRRT D LOCAL02：三条原非平凡局部接缝完成记录

2026-10-16。主任务记录；编写者参与前置/transport工作，**personnel_independent=false**。本稿读取实际保存文件，不新增任何科学调用。当前原 runner 完整12项内部资格通过；人员独立保存后审 **PENDING**，尚不将内部 `external_supervision_qualified=false` 改写为独立批准。

唯一实际运行 `20261015_R2_ABB_CBIRRT_D_LOCAL02`，source commit `4ffdda497e34ed5f97ab6d1ca281ed0e233c860e`，协议 `configs/p4_full/r2_abb_cbirrt_d_local_fixed12_v2.json`（SHA `2d56ecdb7ed755da4526218102eb4d742d7134dedbf9b13a4a2dd51d7b3e8723`），claim SHA `5d8abe06b9de45053fb1f8b164a84980659241441201b0868cbb453d9159ab49`。命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_cbirrt_d_local_v2_draft.py --protocol configs/p4_full/r2_abb_cbirrt_d_local_fixed12_v2.json
```

实际 execution SHA `5151df50119bc6847ab2a0c68dd0e36e346d22bea3a43253c6419ed838e5d48a`；status `PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED`，classification `R2_NUMERICS / D_LOCAL_SEAM / SPLIT_DISTANCE_SOURCE / REUSE_SAVED177`。这只覆盖固定三条原 state-level RBS/完整回溯接缝，不证明 CBiRRT 全局 solve 或完整论文。

## 固定范围与实际结果

输入为原 RRT_PCS 已保存的全部三条高精度回溯边：角色/被动branch `(0,3)`、`(1,3)`、`(0,0)`；完整 M 节点数为80、65、34。每条分别调用原 state-level RBS和reconstruct，各 plain/trace，共恰12顶层请求；原容差 .05、最大深度150、withObs=true不变。未选择新边、改主动角、改解析分支、截尾、平滑或修路径。

实际 dispatch/完整 raw response/parsed response/qualification 均12，completed IDs 0..11；UNKNOWN空，diagnostics空。6对 plain/trace 非观测字段和完整 M 按 binary64相同，qa/qb不变；三条非平凡 RBS与完整原回溯均返回true，M逐节点/首末/顺序精确等于旧80/65/34。这一精确相同条件成立后才复用原 PATH01 的177唯一节点独立闭链、branch、原机械限位与 aligned原离散碰撞证明，未再执行任何独立 FK/J或collision adapter。

真实两个SVC进程分别为72046和72048，均正常exit0且reaped；plain/trace各6次完整响应，EOF drained、closed，额外stdout尾0，原始trace字节绑定通过。close-group现场快照也分别保存为仅该源PID，未把TAIL02的推断边界冒充本项现场记录。plain内部仍UNOBSERVED，不能因返回true而补报内部计数。

trace真实 entered/completed均完整配对：mesh_load1；state_rbs3、vector_rbs349；state_reconstruct3、vector_reconstruct349；fixed_branch_project346、native_fk346、native_ik346、collision346。实际完整原trace事件4178。以上是原源函数内部观测，不能混作新的独立物理资格检查或plain内部计数。构造只为SVC，CBi构造/直接CBi RNG member/seed设置/solve均0；未插桩库内部真实行为不据此补0。

证据位于该run的 `evidence.jsonl`（SHA `10dab1046a2e4d305ee98cdc98318decc42f8dd16bb6c5bb147a5a156fe6426b`）和runtime双模式完整stdout/stderr；原response先以raw留存后再检查。所有成功/原拒绝/原失败记录继续保留。

## 独立后审与计费边界

待 personnel-independent 实际后审文件：`reports/P4_FULL_R2_ABB_CBIRRT_D_LOCAL02_SAVED_INDEPENDENT_POST_20261016.json`。该文件当前尚未交付；不预填schema成功、checks、required_gates或独立监督结论。后审需核对全部12实际响应/6模式对、M精确复用、原177完整证书、全部资产/claim/协议前后hash、两进程/原raw/trace/EOF、真实外层PID/argv/inode与成本。独立后审通过之前，S不能仅凭本稿或runner内部PASS生成可执行协议。

内部执行样本为2.31582639899716秒wall、2.071816秒CPU；receipt已覆盖execution持久化时为2.3782246819973807秒wall、2.0803429999999996秒CPU。receipt自身落盘尾部明确非零未内测。独占GNUtime原行为 `2.46 1.86 0.25 0`，Decimal外层上界2.47秒wall/2.13秒CPU，完整覆盖worker导入、preflight、科学源进程、raw/清理/hash/execution/receipt持久化及退出，落在既定30/60内；supervisor自己的日志/fsync费用在scientific child边界之外。当前charge/runner/receipt的 `external_supervision_qualified` 均false，待独立POST确认。

root另负责V15权威ledger与完整范围表；本稿不提前填入尚未保存的V15总数或保全PASS。正确计费应保留原内部sample，以独立确认的2.47/2.13外层上界只替换本项有效计费一次，不能两者相加。所有旧unsupervised记录的末端费用UNKNOWN保持，余额仍为上界。

## 原失败、研究义务与下一关

距离前置只引用已经独立1374/1374的 `SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO`，原D64仍STOP、原完成61、UNKNOWN[61,62,63]、末-9、完整原raw gate=false永久保留。原H64科学STOP/30 UNKNOWN和另保存链接结论不改；旧PCS177及NR393离散路径资格也不由本项重算或覆盖。

本项实际零compile、独立armFK/J、独立collision adapter、NR、activeDistance、CBi constructor、solve、新VI候选和正式Table I。VI974/974余额0；正式0/22500、全部211项原论文义务和原统计规模保持。成功标签不证明连续无碰撞、完整实体几何、省略碰撞对、RSS分布/全局规划、PCS性能优势或论文FULL。

独立LOCAL02保存审查及V15费用/范围/保全交付后，继续已准备的S固定II/seed7单10秒原solve；其源码/PRE/监督仍需最终冻结与提交，不能自动串行执行。S原EXACT仍只候选并等待单独P完整路径独立门；正式大规模仍待端到端资格、可重复成本pilot和计算预算申请。不提前P2、Isaac或结题Word/PDF。


## 2026-10-16 补记：人员独立后审与V15交付已实际完成

上文PENDING为最初落稿时状态，原文保留作时间记录；现实际独立POST已保存，schema `P4_LOCAL02_SAVED_INDEPENDENT_POST_V1`、status `PASS_LOCAL02_SAVED_DISCRETE_SEAM_INDEPENDENT_POST`，19150/19150、0失败，八项required_gates全true，personnel_independent及external_supervision_qualified均true。文件SHA `9c2445a2d8ff25aac353dc06e677dfd0f12573bbce0cfd620fdefb294431adcf`。独立核对实际12调用、6模式对、三完整M80/65/34、177唯一节点/176叶原证书精确复用、两SVC/0CBi/直接RNG、raw/EOF/两进程起闭组现场快照及回收、全部版本/费用与原D/H STOP保持。没有新增模型查询、重算旧路径或提高门限。

独立外层成本确认2.47wall/2.13CPU；execution SHA保持`5151df50119bc6847ab2a0c68dd0e36e346d22bea3a43253c6419ed838e5d48a`，time SHA `b0dce0dc2ae7f00c2cf40e7f49991d0c91f35a81396f10e7e830f92ff29f0d3c`、charge SHA `2648fae705b239141ac6af9102f50c3da0e1dffefb1ec9a5259925d2e37a1910`。原内部sample/receipt/charge仍保持external_supervision_qualified=false，独立资格只由新POST给出，不回写旧记录。

root已保存V15：33execution=26科学运行账+7工程，charged累计569.685705375994wall/520.738923CPU，R2余额上界3030.314294624006wall/6679.261077CPU。原内部样本保留，只有本项外层上界替换计费一次，旧历史未测尾部仍UNKNOWN。新完整表 `reports/P4_FULL_R2_CBIRRT_D_LOCAL_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv/.md` 为211行146列，前142列逐值保留。

V15保全实际PASS、无mismatch：1028旧科学文件、57崩溃文件8482891B及tar、另5工作树13未提交、原V14和211行历史列保持。证据为 `results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V15.json`。本主POST仍非人员独立，只引用独立报告。下一项仍为另冻S单次solve；本项没有solve或新完整CBi路径，原211义务、正式0/22500及VI974余额0不变。
