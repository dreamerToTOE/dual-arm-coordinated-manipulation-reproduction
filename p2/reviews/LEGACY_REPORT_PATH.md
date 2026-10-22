# 遗留报告路径登记 — `LEGACY_REPORT_PATH_UNUSABLE`

**日期**：2026-10-19
**决定**：三个依赖 P4 渲染代码的报告脚本**保持原字节不动**，标记为 `LEGACY_REPORT_PATH_UNUSABLE`；
P2 之后的报告一律走 `p2/tools/p2_md_report.py`（Markdown + PNG，零 P4 依赖）。

## 为什么改状态而不是改文件

这三个脚本与冻结交付 `7787c75a` 逐字节相同（blob SHA 一致，见下表）。T00 的溯源结论依赖"迁入文件未改动"。
若在文件里加标记注释，会破坏 blob 一致性、使 `LEGACY_BLOB_CHECK.json` 的 MATCH 失效。
因此以**外部登记**的方式标记状态，文件本身不动。

## 登记表

| 脚本 | SHA256 | Git blob（HEAD / `7787c75a`） | 阻断原因 | 状态 |
|---|---|---|---|---|
| `scripts/build_p2_stage2_report.py` | `a6bed108…a5b0782` | `7d592966…` / 相同 | `from build_p4_paper_report import Report, brackets, fraction, ...`；该模块属 P4，本分支无 | `LEGACY_REPORT_PATH_UNUSABLE` |
| `scripts/build_p2_implicit_review.py` | `c15c957f…40268eb9` | `f557a684…` / 相同 | `import build_p2_stage2_report as base`（连带阻断）+ `docx` | `LEGACY_REPORT_PATH_UNUSABLE` |
| `scripts/build_p2_closed_loop_review.py` | `e0ae77a1…81b6e25` | `9eed775a…` / 相同 | `import build_p2_stage2_report as base`（连带阻断） | `LEGACY_REPORT_PATH_UNUSABLE` |

附加环境缺口：本机**未安装 `python-docx`**（`import docx` 失败）。即便修掉 P4 依赖，这三条路径仍无法生成 `.docx`。

## 替代路径

| 能力 | 新实现 | 依赖 |
|---|---|---|
| Markdown 报告 | `p2/tools/p2_md_report.py::render` | 标准库 |
| 图表 | `p2/tools/p2_md_report.py::bar_chart`（matplotlib Agg） | matplotlib 3.5.1 |
| 示例 | `p2/tools/t02_report.py` → `p2/reviews/T02_REPORT.md` + `figures/` | 同上 |

约束（审查意见）：

- 新报告**不得** `import` 或调用任何 P4 模块；
- 不修改 P4 文件；
- PDF/Word 导出不是本阶段必需，留到 T10 单独决定；
- 报告数字必须能从 `results/` 或 `p2/reviews/*.json` 重算，不得手工填。

## 复现命令

```bash
cd /home/ubuntu2004/lmy/p2-num-sim-20261018
/usr/bin/python3.10 p2/tools/t02_math_audit.py     # 生成审计 JSON 与基线
/usr/bin/python3.10 p2/tools/t02_report.py         # 生成 T02_REPORT.md 与图
```
