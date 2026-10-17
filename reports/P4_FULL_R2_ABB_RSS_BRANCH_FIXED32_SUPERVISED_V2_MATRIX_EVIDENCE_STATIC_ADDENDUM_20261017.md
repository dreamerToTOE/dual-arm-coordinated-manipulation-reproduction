# RSS固定32 V2：既有独立矩阵输出静态补充

状态：DRAFT / STATIC ONLY / NOT RUN。仅按root授权保存将来已经算出的全位姿/Jacobian；没有import、describe、validate、模型/FK/J/SVD、编译或科学执行。

修改前8份稳定稿/静审记录已逐字备份，manifest `reports/p4_full_audit/draft_archive/RSS_FIXED32_SUPERVISED_V2_PRE_MATRIX_EVIDENCE_20261017/manifest.json`，SHA `38134630486a208032bbf30f8e30f85254a5a4e1f2bbf6f2bf1b9242c5811422`。初次标准库备份脚本复制完8文件后因Path索引笔误未创建manifest；修正仅核对原副本并独占创建manifest，未覆盖备份或修改源码，过程记录在manifest。

新候选仅在original JSON保存已算one/j1/two/j2全矩阵，在成功row保存已算outpose/j全矩阵，并写env、arm、q6、单位、J行序、未缩放声明和原rank平移行×.001说明。既有rank函数仍复制原J再按原门求秩，未增加FK/J/SVD或改任何门/输入/次序/次数。矩阵的tolist和JSON尾成本仍在同10/20预算内，未测可行性。

当前科学循环正确声明为：剥离恰好两处 `independent_already_computed` 输出keyword后，AST与v1完全相同（静态检查10/10）。此前逐字相同声明与人员独立PASS保留为旧SHA历史，不能作当前候选新SHA审查结论。新人员独立补充审查待nr_entry_review出具。

| 当前文件 | SHA256 |
| --- | --- |
| `scripts/qualify_p4_full_r2_abb_rss_branch_fixed32_supervised_v2_draft.py` | `4839efdf5b6bb921e1ec82a06074d20dda007365b1d8744f9e72abd343a49862` |
| `scripts/supervise_p4_full_r2_abb_rss_branch_fixed32_v2_draft.py` | `fada7f5aaf9e94d06aeb7572c062ba2dff7b843286ebaa571bf3af293a590619` |
| `configs/p4_full/r2_abb_rss_branch_fixed32_math_supervised_v2.draft.json` | `da3431b145d1100c26b5dd5593edcbc74e012da08c451bcd800f7d00a204d691` |
| `reports/P4_FULL_R2_ABB_RSS_BRANCH_FIXED32_SUPERVISED_V2_PRE_DRAFT_20261017.md` | `d182443483d429014e1d7cc0016ae3482daf12bcd5cd1e8d08c083d7fec11b02` |

本静态JSON：`reports/P4_FULL_R2_ABB_RSS_BRANCH_FIXED32_SUPERVISED_V2_MATRIX_EVIDENCE_STATIC_ADDENDUM_20261017.json`，SHA `f8fea0a45e447e65a65b15eefb7043fc19a102101939914a9db93363daf8b1a6`。仍未产生任何实际数学矩阵、结果、claim或execution；只在未来真实完整记录后才可math_recording_qualified，不升级collision/fullRSS/RBS/规划。
