# P4 中文报告图表与数据来源

交付：[可编辑 Word](../P4_论文复现汇总.docx) / [PDF 页面预览](../P4_论文复现汇总.pdf)。
只使用已有日志，不运行科学算法、ROS、Isaac、机器人或FCL查询。

## 只重建报告

在仓库根目录，使用已有 Python 环境或独立工具虚拟环境（不修改科学环境）：

```bash
python3 -m venv --system-site-packages /tmp/p4-report-env
/tmp/p4-report-env/bin/python -m pip install python-docx==1.2.0
/tmp/p4-report-env/bin/python scripts/build_p4_report_assets.py
/tmp/p4-report-env/bin/python scripts/build_p4_paper_report.py \
  --private-sources /home/ubuntu2004/lmy/papers_and_reference_all/references/private_sources
```

NumPy、Matplotlib、Noto CJK 需可用；路径不同可调整 `--private-sources`。
第二个脚本只核对私有文件 SHA256，不将全文嵌入/复制报告。
命令会重建**本目录的派生图表及报告**，不会重跑实验或修改 `results/`。
原实验复跑需单独授权，不是本节命令的组成部分。

PDF 可使用 LibreOffice 在独立临时profile中转换，不启动 Isaac。
使用 `scripts/check_p4_report_delivery.py` 检查静态交付（需要生成的PDF）。

## 图的证据资格

| 图 | 内容 | 来源/资格 |
|---|---|---|
| 01 | NR–RBS–双树流程 | 原创理论示意；原文II-B/C、IV与固定作者增长审计 |
| 02 | 双FK与固定抓取 | 原创坐标示意，非机械臂截图/物理状态 |
| 03 | 历史残差、导数差分误差 | TASK03 closure02 原293条记录；435配置总覆盖另列正文 |
| 04 | NR位置/旋转收敛 | TASK04 projection03：96非零输入曲线；97输入含零更新夹具，194调用/2重复 |
| 05 | 成功/失败和计算时间 | TASK06 search02：18调用/9对，不是18独立随机样本 |
| 06 | 553节点双树二维投影 | 原私有障碍seed20261012 repeat0；不在二维图推断碰撞 |
| 07 | 14关节角度与限位 | IS-A名义run03原1869q，空间路径非时间轨迹 |
| 08 | 路径闭链残差与左J4风险 | 原独立验证+B0；没有最近FCL距离 |
| 09 | 全14关节限位余量 | 原1869q与原B0限位；不是机器人环境净距 |
| 10 | 累计行程与端点净变化绝对值 | 原B0记录；只报告层取abs，不改原有符号值 |

所有图以中文标注并提供PNG/SVG；由脚本从真实记录生成，理论示意图明确单列。

## 机器可读派生文件

- `task03_historical.csv`：293条原历史残差/差分误差。
- `task04_iteration_traces.csv`：1212条真实初值/已接受更新，包含194邻域调用和293历史诊断；不补齐、不补零。
- `task06_trials.csv`：全部18调用；失败路径长留空，不填0。
- `scene_path_1869.csv`：原全14q、闭链残差、14关节余量，无物理时间。
- `report_data.json`：数字汇总、完整原始来源SHA、图/字段映射；不代替原日志。
- `build_assets_check.json`：逐个18原始gzip读回、9对确定性、1869点匹配等只读检查。
- `build_word_check.json`：六份资料SHA、16个原生OMML公式、10图、原始输入不变。
- `delivery_check.json`：最终页面/数值/私有资料排除及软件scope检查。

历史精度FAIL、TASK06整体PARTIAL、障碍直连PROJECTION_JUMP与FCL未查询、B0执行条件不满足保留。
原PDF与DEFORM范例只在用户本地，不能提交本目录/公开GitHub。
