# SBL PCS SETUP01：V25 saved-only 保全草案静审

状态：`DRAFT / STATIC ONLY / NOT RUN`。本次只读取源码和既有保存文件，使用标准库 AST/SHA 与只读 Git blob 核对；没有导入或运行任何项目源码，没有描述协议、编译、启动 SETUP、模型查询、solve、采样、生成 V25 账目/覆盖表或实际保全结果。

草案：`reports/p4_full_audit/recovery_tools/audit_preservation_v25.py`，SHA256 `b4016a57689d8996dd41b443f5ae267a22de1aaafe7db887ac932c7748774685`。静审 JSON：`reports/P4_FULL_R2_SBL_PCS_SETUP01_V25_PRESERVATION_STATIC_DRAFT_20261017.json`，SHA256 `5865516d088e2eff56af1fdbba0ea6f0964e421c395158eb5249c3c186c7a347`。本次静态检查 17/17；该数字仅属于静态草案检查，不是未来独立 SETUP POST 的检查数。

草案固定历史提交 `c71420557dc866b41ee05a97c7a9c55c0e4811da`，并实际核对以下三份文件的当前字节 SHA 与该提交 blob 一致：

| 历史文件 | 固定 SHA256 |
| --- | --- |
| `results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V24.json` | `adee31c9150354e4b145718b91f70a4451eaf9bf0f300e067905d6776b48d81e` |
| `reports/P4_FULL_R2_SBL_PCS_BUILD01_ORIGINAL_VS_REPRODUCED_COVERAGE_20261017.csv` | `8536a239e117d4008363b86b4e7e331ac3b25a96d97fc4ba5a77950ab001a3bd` |
| `results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V24.json` | `b5e513181859674caa3ebc31f636f820a28a7a71ab832dab7a6f6c03825735a9` |

未来实际使用须提供 `--external-post`、`--external-post-sha256` 与 `--new-csv`，均为真实已产生输入。草案不预填未来 POST 路径、SHA、检查总数、实际耗时或结果。独立审查方确认的接口为 `P4_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST_V1 / PASS_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST`；必须 `personnel_independent / external_supervision_qualified / external_timing_qualified / external_cost_qualified / setup_qualified` 全真，真实正数检查总数全部通过、无失败，并保存实际链文件和 `retained_sha256`。SETUP 没有新 manifest，绑定实际 BUILD manifest 与 BUILD 人员独立 POST。

此草案的合格分支要求保留原始 `SOURCE_SETUP_PUBLIC13_OBSERVED_PENDING_INDEPENDENT_POST`，原始 `external_supervision_qualified=false`、`independent_path_qualified=false`，再单独引用真实独立 POST。只允许一次 source 进程、一次请求、一次 setup、13 次已存在公共投影调用；双管道原始 EOF、完整单次请求及关闭 stdin、子进程归零回收、完整原 body trace、实际 loaded maps、20 个运行 mesh 与 bound/protocol/claim 前后 SHA 均须由保存记录支持。setup 库内部 RNG 仍是 `UNOBSERVED`，不能凭观测矩阵推断其随机来源或 solve 入口资格。

V25 目标账目是 43 次执行＝32 项科学账＋11 项工程账；SETUP 不是工程编译。旧 42 行逐字典相等保留，每项实际 execution 仅计一次，真实外部十进制上界替代内部样本一次，科学/工程小计与总计使用 `math.fsum`。SETUP 保持 10 秒墙钟/20 秒 CPU 上限；R2 总上限 3600/7200 不变。VI 构造 974/剩余 0、实际 source solve 总 5/新增 0、正式 0/22500 均保留。

覆盖表保留 211 项、旧 182 列和值与顺序，新增 `v25_status/scope/execution/ledger` 四列至 186；相关项仍为 T02、T05、T08、T11、T17、T25，不能使其自动成为规划通过。45 个 Table I 单元的 500 次与 1000s/call 义务全部保留。V24 的 1028 个旧科研文件、57 个崩溃前文件/8482891 字节、外部 tar、5 个其他工作树/13 个未提交文件保全逻辑原样保留。

只有未来真实 SETUP 和人员独立 POST 已完成，且真实 V25 ledger 与 CSV 已生成并审查后，才可由 root 决定执行这个 saved-only 草案。此草案不是 SETUP 成功、独立资格、路径资格、正式统计或论文完整复现结论。若真实 SETUP 失败，原失败与实际费用仍须记账；不能为满足本草案的合格证书分支而重跑。
