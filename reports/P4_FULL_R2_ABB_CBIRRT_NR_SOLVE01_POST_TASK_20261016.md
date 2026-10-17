# ABB CBiRRT_NR SOLVE01：完整候选已保存，独立物理路径资格待执行

2026-10-16。主记录 personnel_independent=false。恢复确认实际仓库 `/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full`、分支 `p4-full-reproduction-pcs-study`、冻结 HEAD `119a1b36d918ddd83fe23f49c09bc10b684f02ea`，已 fetch；无待推送提交、无残留资格/规划进程。另五工作树不切换或修改，崩溃前数据保持；已完成资格不重跑。

唯一执行命令（已经运行并结束，禁止重复）：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_cbirrt_nr_solve_v3_draft.py --protocol configs/p4_full/r2_abb_cbirrt_nr_single_solve_v1.json
```

冻结协议 SHA `cc216cb61eceff4105641c027d596b6d6e25fbcc1170715ccd895bb7398a5dc8`；固定 II/A01 RECONSTRUCTED 起终、seed7、range2.6、原 solve 10 秒、外帽30wall/60CPU。原 sampler box、恒真全局 callback、resolution .1、原双树/full12距离/grow/RBS/回溯不改；physical NR 数值接缝仍明确 RECONSTRUCTED，不冒充作者 KDL 实现。

实际 execution SHA `bc30019b1e5282817adee945fbb4b86a7bb9f30e6f419a6def0e559815a7b1b6`；status `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT`，exact=true、approximate=false，dispatch1。16个树节点、12里程点、11段原 state_reconstruct 全true；M长度 `[65,65,17,65,129,129,65,33,33,33,65]`。699个引用按q12 binary64原接缝连接为689唯一节点/688叶；bridge Motion16→14两端q不同，保留原双树链顺序。完整stdout 7,615,248B、stderr 8,394,803B、原native文件与全部false均保留；单次write后stdin EOF、严格唯一JSON、双actual EOF、exit0/reaped/空组、完整raw gate=true、diagnostics=[]。

人员独立保存后审 `P4_FULL_R2_ABB_CBIRRT_NR_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json` SHA `549d585f1fb2be390b28a0d64dfb90815e58092a9efd7e3c4d478abebe381ef1`，16,711/16,711、失败0。只证明实际入口、完整回溯素材与证据/费用成立；`independent_path_qualified=false` 保持。GD29、project45、midpoint44、vectorRBS365/stateRBS46等真实false没有删除。source solve_wall .27836642包含trace/I/O，不作论文性能。

GNUtime `9.05 7.51 1.18 0`，Decimal外层上界9.06wall/8.71CPU，只替换内部8.855144036002457/8.591677样本一次。V22真实40execution=30科学账+10工程，累计795.885705375994wall/716.458923CPU；余额仅上界2804.114294624006/6483.541077，历史未测尾UNKNOWN保持。V22账本SHA `e0432dc0a92852db3a67f9c62535d80b4d4ab8a90f6430832320247420d0ff1e`。最新范围表 `P4_FULL_R2_CBIRRT_NR_SOLVE_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv/.md`：211×174，前170历史列逐值保存；II单候选不构成III窄通道结果，T12仍未获III路径资格。

RSS只读新契约报告 `P4_FULL_R2_ABB_RSS_SOURCE_CONTRACT_STATIC_V1_20261016.md/.json` 保留作者三搜索器不同sg/branch/回溯契约，尤其SBL .05与冻结γ=.2差异、RRT禁用exact分支、CBiRSS serial导出、SBL双-2负branch风险；均为源码证据，尚非运行反例或论文理论错误。没有新RSS/VI调用，不静默改变参数。

下一从最早未过门继续：完整689节点数学闭链/原限位/v3 aligned source-policy collision及688叶距离，先独立静审、真实S证书/V22账/全部素材绑定与源码协议提交冻结，再唯一P；帽2048节点/120wall/240CPU，不重solve、不新RBS、不换点或截尾。基于旧413节点104.88wall的已存证据，调整工程持久化以避免逐文件fsync成本，科学循环逐AST保持NR393。工程I/O审查通过不替代实际P结果。

全部211义务、原45×500/1000s、500000投影、约50000点对和全部图表/消融保留；VI974/974余0，正式TableI0/22500。P4仍部分完成。端到端资格后才成本pilot与正式预算申请，不P2/Isaac或提前结题Word/PDF。

V22保存证据保全已实际执行：`20261016_RECOVERY_IMMUTABLE_VERIFICATION_V22.json` passed=true，七组mismatch均为空；1028旧科学文件、57崩溃文件8482891B及tar、五工作树13未提交、V21与211前170列完整保持。保全SHA `e6e209f000b2f57d06a77952e88f3abd9fcf40792f7b20985ce1c54b61d3ab5f`。资格调用补充账SHA `316024926cbd63e1f6ca53db0be6d7cc4419b9cb3b029450f642e3529f87bcb9`，保留V22旧狭scope字段并另列4+1=5。
