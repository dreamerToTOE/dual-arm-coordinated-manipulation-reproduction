# P2-T00 PRE — 旧成果证据审计（只读）

**任务**：`p2/tasks/P2_T00_PROVENANCE.md`（G0 门）
**分支**：`reproduce-p2-numerical-simulation-20261018`
**论文**：De Simone, Costanzo, De Maria, Natale, *Cooperative Object Transport and Assembly: Pose/Force Control by Visual-Tactile Feedback*, RA-L 2026, DOI 10.1109/LRA.2026.3665445
**本轮声明状态**：READ-ONLY AUDIT。零仿真、零积分、零参数改动。

> 时序说明：本文件与 `T00_POST.md` 在同一会话内完成、同一次提交入库。PRE 的内容在读取任何结果之前固定（范围、方法、判定规则、预算），结果出现后未回改；由于两者同时入 Git，提交时间戳本身不能证明先后，先后关系由本文件的"预登记判定规则"与 POST 的证据编号体现。

## 1. 范围（In / Out）

**In**
1. 分支、工作树、迁入文件完整性核查。
2. 论文式 (1)–(26)、Fig. 1–9、Table I–II 与现有代码、T01–T10 的对应关系。
3. 旧 P2 全部资格证据（几何 68/68、动力学 70/70、组件 35/35、时序 2/2、首条闭环 3.948 s 停止）的实际内容审计。
4. T01–T10 对论文实验的覆盖完整性。

**Out（本轮明确不做）**
- 不运行任何数值积分、闭环、MuJoCo、单元测试或 native 编译。
- 不修复估计器、不改 Q/R/增益/刚度/质量/时钟、不重跑闭环。
- 不启动 T01–T10 的任何科学运行。
- 不接触/不修改 P4 的文件、分支、进程、报告。

## 2. 预期输入

| 输入 | 位置 | 用途 |
|---|---|---|
| 冻结旧交付树 | commit `7787c75a8042af041579e5df0c9ac3e3ec4f6195` | blob 级比对基准 |
| 验收记录 | commit `f4f9d3b97e80481dbc74ca419ac9b390447e4eef` 的 `reports/P2_ACCEPTED_DELIVERY_FREEZE_MANIFEST.json` | 第二层 SHA256 基准 |
| 权威论文 | `/home/ubuntu2004/lmy/papers_and_reference_all/references/private_sources/P2_original.pdf`（8 页，SHA256 `0188b6be…cc0346`） | 公式/图表/参数 |
| 旧报告 | `reports/P2_*.md`（32 份） | 结论与失败记录 |
| 旧结果 | `results/*_P2_*/`（18 目录、113 文件） | 原始数据 |
| 旧协议 | `configs/p2_closed_loop_protocol_v3.json` | 参数/时钟/30 案台账 |
| Issue #35 | GitHub API | 阶段清单与工作规则 |

## 3. 执行顺序（预登记）

1. 分支/工作树/HEAD 记录；确认主仓库 P4 工作树未被触碰。
2. `git ls-tree` blob 比对（层 1）+ 验收 manifest SHA256 比对（层 2），生成 `LEGACY_BLOB_CHECK.json`。
3. 逐页读论文（文本 + 页面图像双通道，防止公式抽取错位），建立式 (1)–(26) 与代码的对应表。
4. 读旧结果 JSON/JSONL/NPZ，区分"实际检查内容"与"报告措辞"；对 3.948 s 失败做证据链重建。
5. 对照论文实验清单检查 T01–T10 覆盖。
6. 写 POST、更新 STATUS、按文件逐个 `git add` 提交。

## 4. 计算预算

| 项 | 预算 | 实际 |
|---|---|---|
| 仿真/积分 | 0 | 0 |
| 单元测试 | 0 | 0 |
| native 编译 | 0 | 0 |
| 允许操作 | `git ls-tree/show/rev-parse/log`、文件读取、`pdftotext/pdftoppm`、`sha256sum`、JSON/JSONL/NPZ 只读解析 | 同左 |
| 墙钟预算 | ≤ 15 min | 见 POST |

## 5. 预登记判定规则

- **MATCH**：同一路径在冻结提交与本分支 HEAD 的 blob SHA 完全相同。
- **MODIFIED**：两处都存在但 SHA 不同 → 必须逐个人工解释；不得默认接受。
- **OMITTED**：冻结提交存在、本分支不存在 → 必须分类为"渲染/排版资产"或"科学证据缺失"；后者阻断。
- **NEW**：本分支存在、冻结提交不存在 → 只能是 `p2/` 路线图或 T00 自身产物。
- **SHA256 层**：以验收 manifest 为准；任何 mismatch 一律视为来源污染，停止并上报。
- 组件/单元测试通过 **不得** 记为论文实验通过；`PASS` 只对"该检查实际覆盖的内容"有效。
- 论文实验未运行时只能记 `NOT_EXECUTED`，不得记 FAIL 或 PASS。
- 与原文不一致的实现必须标 `ADAPTATION` / `DEVIATION` / `OUR_EXTENSION`，不得并入"原式实现"。

## 6. 验收条件（对应任务文件）

- 每个迁入 blob 都有归属（MATCH/MODIFIED/OMITTED/NEW）。
- 旧核心失败（Eq15 偏离、Eq22 疑点、FD 两点失败、70/70、35/35、2/2、3.948 s）全部保留且被正确描述。
- 论文每条实验声明都有索引与状态。
- 总状态仍为 PARTIAL。
- 复制不一致 → 立即停止。

## 7. 交付物

- `p2/reviews/T00_PRE.md`（本文件）
- `p2/reviews/T00_POST.md`
- `p2/reviews/T00_EQUATION_INDEX.md`（式 1–26 / 图表 → 代码 → 任务 → 状态）
- `p2/reviews/LEGACY_BLOB_CHECK.json`
- `p2/tools/t00_blob_check.py`（可复跑的两层哈希核对脚本）
- `p2/STATUS.md` 更新
