# V23 保全草案：root 首次执行前审查修正补记

2026-10-17。原作者自核 10/10 报告保持原字节：`P4_FULL_R2_V23_PRESERVATION_DRAFT_STATIC_SELFCHECK_20261017.json`，SHA `1e3de7dcb2231f323d3968478f441d3a22531caae770400d55c9e236d362bcc9`。该报告只核 AST、字符串和继承块，**没有覆盖实际字段类型和本轮明确配置**；不能称独立审查或实际保全通过。

root 首次运行前查出并修正两项我方保存审计草案错误：

- `durable_saved_snapshot.members_verified` 实际是整数 **3447**，原草案误与 `True` 作身份比较。修正为数量等于 3447，另对 fsync/目录 fsync/loose-byte 三项真布尔分别检查。
- coverage related IDs 不应套用账工具的默认集合。修正为本轮真实 V23 明确集合：`P4-T03,T05,T09,T11,T16,T17,T25,T26`；原草案会错拒正确账及覆盖表。

原草案 SHA `abad4231ad160a487839a8c11a6871e1df0c6baaffa66baf4a1a6257a59a8c31`，**未曾执行**。修正后工具 SHA `ce26b86e618bcef88434b95651fc72750f08b1e570afc0e662652f54aa3ce324`；root 已唯一执行修正版本，保存结果 `results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V23.json`，SHA `b61dfee56fa04b8589ccc870f824d651c403d152086b2fc145323be9022aed02`，真实 passed=true、七组 mismatch 均为空。该结果证书的 analysis_source_sha256 与当前修正工具一致。

错误归因于我们静态自核覆盖不足，不是路径科学失败、作者源码问题或论文数学问题；不回写旧 10/10 报告。此补记只读取已存源码/JSON并新增本文件，未重跑保全工具、模型或科学，新增 VI/solve/协议/claim 均 0。
