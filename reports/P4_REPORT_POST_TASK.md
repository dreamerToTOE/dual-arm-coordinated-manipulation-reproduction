# P4 正式论文复现汇总 — POST-TASK REPORT

日期：2026-10-12。规划基线：`e32d19d53812f008c6bc3f2d71cbf761e2b954a3`。
任务前协议提交：`266de05`。独立分支：`report-p4-paper-first`。

## 结论与交付

**本轮报告整理完成，等待用户审查；不是完整 P4 论文复现通过。**

- [《第一篇P4闭链运动规划论文复现汇总》可编辑 Word](P4_论文复现汇总.docx)
- [23 页 PDF 排版预览](P4_论文复现汇总.pdf)
- [原创图表、派生 CSV、来源与重建说明](p4_report_assets/README.md)
- [最终交付检查](p4_report_assets/delivery_check.json)

最低充分证据已取得：六份本地资料 SHA256 一致；主代理阅读全文 P4 八页及 DEFORM 范例；
报告包含两大部分、16 个可编辑 OMML 公式和 10 幅中文原创图；所有实验图来自保存的原日志，
理论流程/坐标示意与实验图明确区分。完整报告不代表其他方法或物理实验已补齐。

## 已完成内容

1. 解释原文 RSS、PCS、NR 三种约束处理策略与 RRT/BiRRT/SBL 规划器的区别。
2. 解释本项目真实 FR3 的 SE(3) 闭链约束、解析雅可比、Newton–SVD 投影、RBS 和双向树；
   显式标明原论文方法、双 FR3 适配与保守工程护栏。
3. 整理 TASK03–06、TASK06-IS-A 和 B0 的既有数据、成功/失败分母、投影曲线、14 关节空间路径和限位风险。
4. 对照原文 Table I/II、平台、模型、试验规模和指标；不同条件不作性能优势推断。
5. 保留历史未通过和未完成项；未运行新的科学算法、Isaac、ROS、机器人或碰撞查询。

## 静态检查结果

| 检查 | 结果与范围 |
|---|---|
| 私有资料 | 六份均存在、SHA256 与 registry 一致；全文不上传 |
| 原始来源 | 39 个来源文件 SHA256 验证一致；科学源码/配置/结果未编辑 |
| TASK03 派生数据 | 293 条历史记录来自原始日志，原精度 FAIL 保留 |
| TASK04 曲线 | 1212 条真实初值/已接受更新，194 次邻域调用及 293 次历史诊断；不补零 |
| TASK06 统计 | 18 次原始调用，14 次 SUCCESS、4 次 NODE_LIMIT；9 对确定性重复，不当作 18 个独立样本 |
| IS-A 路径 | 1869 个点的全 14q、闭链残差与各关节余量逐值一致 |
| Word 结构 | 16 个原生可编辑公式、10 幅图；公式坐标方向经独立复核 |
| 页面检查 | PDF 23 页；主代理查看全页缩略图及关键公式/图表原尺寸页面，无乱码或明显裁切 |
| 公开文件范围 | 不提交原论文 PDF、DEFORM DOCX、全文提取文本或原工作区未跟踪日志 |

三个并行只读审查分别复核数学/历史数据、规划/路径数据和原论文方法忠实性。
采纳的修正仅在报告层：净变化图取绝对值、明确固定抓取变换方向与可见性推导假设、
修复 Word 数学空占位；不改变算法或实验数据。代理交付复核不等同于用户科研审查批准。

## 执行过的报告工具

```bash
python3 scripts/build_p4_report_assets.py
/tmp/p4-report-tools.MVbzAm/venv/bin/python scripts/build_p4_paper_report.py
timeout 60s libreoffice \
  -env:UserInstallation=file:///tmp/p4-report-tools.MVbzAm/lo-report \
  --headless --convert-to pdf --outdir reports reports/P4_论文复现汇总.docx
/tmp/p4-report-tools.MVbzAm/venv/bin/python scripts/check_p4_report_delivery.py
```

`--headless` 仅为办公文档转换参数，不是 Isaac 运行方式。
工具依赖放在独立临时环境，不修改科学环境。可迁移重建命令见资产 README。
本轮科学实验次数为 **0**；一次报告构建工具链、两次纯报告排版/表述修正。
不运行旧算法回归，因为本轮没有更改科学算法，且用户禁止新增 P4 实验。

## 保留的科学资格与问题

- **已接受范围不变**：TASK03 数学实现、TASK04 离线投影数学、TASK05 真实 FR3/FCL 离散连接和 TASK06 核心软件的原分项验收。
- **历史未通过不改判**：TASK03 原 0.05 μm 精度要求，219/293 位置残差超限；最大 0.435028 μm。
- **TASK06 整体仍部分完成**：障碍直连为 PROJECTION_JUMP，被拒中点未进行 FCL 查询；不能改称 COLLISION 拒绝。
- **IS-A 仅无执行规划适配**：原 1869 点路径合格，不是 Isaac 物理执行；0.213194502 s 是规划计算时间。
- **B0 执行准备不满足**：左 J4 index860 最小限位余量 0.236039°；赋时、全程跟踪界及实际持件起点仍缺证。
- **KNOWN LIMITATION**：主要实现 NR 路线；RSS/PCS、三策略完整比较、原可见性和一般奇异通道未完成。
- **DEFERRED**：TASK02-D 同步测量认证、物理执行和路径改进；不阻塞本轮报告，但不能据此声明正式物理指标。
- **LEGACY**：旧 Task26 两 Cube 工程成功仅为资产来源，不合并为新 P4 物理成功次数。
- 最近 FCL 距离仍为 UNAVAILABLE，离散检查不提供连续扫掠安全证书。
- Benchmark 仍为草案/未定稿。本轮无 TASK-BLOCKING 问题需要扩大实现；无工程升级或新 probe。

## 忠实性标签

- **[ORIGINAL]**：论文约束采样、NR、RBS 和双向搜索的已有实现说明、原公式/表定义。
- **[ADAPTATION]**：真实双 FR3 的 14 维坐标、固定抓取、SE(3) 残差与 FCL 场景映射。
- **[ENGINEERING]**：只读日志统计、中文图表、Word 排版、source hash 和报告交付检查。
- **[DEVIATION]**：已有秩/局部性/限位护栏，以及对一般奇异路径覆盖的限制明确披露；本轮未新增算法差异。
- **[EXPERIMENTAL]**：仅整理以前独立工程协议的数据，无新科学试验。

## 文件与记录

新增三份报告层脚本、Word/PDF、图表/派生 CSV/JSON、本 POST-TASK。
更新 README、CODEX_START_HERE、P4 参考卡，以及 STATUS、WORKLOG、EXPERIMENT_LOG、BUGS、DECISIONS、USER_FEEDBACK。
原 worktree 分支与 HEAD 不移动，五份原未跟踪日志保留，不提交。
最终 Git commit 以分支历史及交付消息为准，不在提交内部虚构自引用 SHA。

**下一步：停止，等待用户审查本 Word。不得自动进入 P2。**
审查后才依 P2→P3→P5→P1 顺序逐篇开展；每篇需原文、公式、独立真实实验、原数据/图表和中文 Word。
