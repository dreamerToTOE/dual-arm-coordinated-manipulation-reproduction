# P4 三方法复现交付：部分完成，等待审查

2026-10-13。分支 reproduce-p4-three-methods，基线d5b5096；实验源码3d51ca0，
协议6d64b26，已有未提交成果保全提交219a8a7。没有重建分支、重置工作树或覆盖本地文件。

本次核验并交付三种独立算法、真实统一实验及中文报告；**不宣称原论文完整复现通过**。
原文全文审计与实验前协议见[P4_THREE_METHOD_PRE_TASK](P4_THREE_METHOD_PRE_TASK.md)及
[补充审计](P4_THREE_METHOD_ORIGINAL_AUDIT.md)。

## 真实结果及结论范围

| 方法 | 成功 / 总调用 | 全调用平均计算耗时 s | 平均树节点 | 平均成功路径长度 rad |
|---|---:|---:|---:|---:|
| RSS | 0 / 20 | 5.000134，全部达到5s上限 | 268.85 | 不可用 |
| PCS | 20 / 20 | 0.581200 | 32.60 | 4.573955 |
| NR | 20 / 20 | 0.035464 | 5.00 | 1.270807 |

这是两个环境×两个外层预算×三个方法×五个固定seed的60次调用。
另外3次重复仅核查一致性，不进入统计分母；同seed跨预算/环境是配对条件，不是20个独立种子。
RSS耗时为右截断失败预算，不能与成功求解时间作无条件速度比。
所有数字来自round3原始gzip/CSV；没有将原Table I/II或旧FR3数字放入本次实测组。

三方法共用20R重建机构、起终点、原生关节边界、GEOS胶囊/圆碰撞、双向树、
0.6rad步长、0.05rad离散RBS、200/800外层、2000节点、5s预算和PCG64种子。
该几何属于原环境I同类重建；不是原作者精确输入，未复现六环境和m增长曲线。

RSS精确奇异fixture和两段RBS确实合格，但313次随机请求/9996次生成尝试没有合格奇异目标，
20次统计均失败。PCS两划分参与搜索，但全部92条解边用p0、父子树边实际转换数0，
不宣称已经展示解路径内频繁换链。E1新增障碍未改变PCS/NR成功路径，不能据此验证复杂障碍效应。
PCS/NR重复完整非计时载荷一致；RSS超时截断工作量不同，原完整重复判据未通过。

## 交付文件

- [正式中文Word](第一篇P4闭链运动规划论文复现汇总.docx)、[18页PDF预览](第一篇P4闭链运动规划论文复现汇总.pdf)。
  正文16个原生可编辑公式、10幅中文图，最后独立讨论双FR3应用差距。
- [三算法源码说明](../baselines/p4_comparison/README.md)与[冻结配置](../configs/engineering/p4_three_methods_v1.json)。
- [60次全部统计](../results/20261013_P4_three_methods_round3/trials.csv)、[63份规划原件及数学记录](../results/20261013_P4_three_methods_round3/)。
- [图表和派生CSV](p4_three_assets/)、[绘图脚本](../scripts/build_p4_three_assets.py)。
- [修正1](P4_THREE_METHOD_CORRECTION_01.md)、[修正2](P4_THREE_METHOD_CORRECTION_02.md)、[修正3](P4_THREE_METHOD_CORRECTION_03.md)，
  round1失败和round2中断全保留；round0没有独立logger目录，原traceback片段留在修正1中。
- [来源及保全清单](P4_THREE_METHOD_HANDOFF_SNAPSHOT.json)、[独立交付检查](P4_THREE_METHOD_DELIVERY_QA.json)。
- [排版修订脚本](../scripts/build_p4_three_report_revision.py)及[修订清单](p4_three_layout_revision/revision_check.json)。
  原三方法Word/PDF仍保留；新稿仅移动图9图例、更换页脚，正文XML和全部科研数值不变。

## 验证及使用

在Python3.10环境中安装requirements-p4-three-methods.txt。中文出图另需fonts-noto-cjk；
PDF用LibreOffice 7.3转换。运行位置为仓库根目录。

    python3 scripts/verify_p4_three_delivery.py
    python -m unittest discover -s tests -p 'test_p4_comparison_*.py' -v

第一条只依赖Python标准库，支持任意克隆路径，且不导入科学规划模块。
核对131个接手文件、561个旧保护文件、9个科学来源、60次全部覆盖与图表来源。
独立线段距离核验全部3312个成功路径点，最大净距记录差2.78e-17m；
最大闭链位置残差9.03967e-9m、旋转残差约2.00e-15rad，原精度全部满足。
17项原数学/接口测试复核通过；没有新增统计规划调用。

只复建图表时使用独立新输出目录：

    python scripts/build_p4_three_assets.py --run-id 20261013_P4_three_methods_round3 --output reports/p4_three_rebuilt_assets

历史绘图/Word生成脚本包含执行时绝对来源路径和私有资料路径；本机可按原命令复建。
新克隆若缺少该绝对路径，应先用可移植核验器检查数据，而不是改写原来源记录。
所有原图PNG/SVG和可编辑Word已随交付保存；排版修订脚本复用保存数据，无私有PDF依赖。
修订脚本只创建新文件；已有正式Word时拒绝覆盖，需在独立工作树复建。

原科学运行命令保存于metadata.json：

    /tmp/p4-three-source.sHcHgg/venv/bin/python scripts/run_p4_three_methods.py --run-id 20261013_P4_three_methods_round3

run-id独立目录拒绝覆盖。该命令是既有实验的真实记录；本轮未再次执行它。
三轮科学修正已用满，交付后停止，不以复建说明自动授权额外统计实验。

## POST-TASK REPORT

- **Task / Status**：P4 RSS/PCS/NR统一重建比较及报告，部分完成，等待审查。
- **Scientific objective**：真实运行三方法并公正比较；数据交付完成，原论文数值/全部现象未完成。
- **Minimum sufficient evidence**：三策略源码、冻结条件、全量成功失败、原文审计和中文报告已齐；完整P4通过证据未齐。
- **Completed**：已有131文件按字节保全、全文/作者代码复核、数据独立检查、正式Word/PDF与图表、六份科研记录。
- **Files changed**：新增交付文件、报告排版修订、依赖清单和可移植核验器；科研算法、冻结配置及历史结果没有修改。
- **Commands run**：git fetch/status/祖先检查、pdftotext/pdftoppm、17项软件检查、两份保存数据核验、报告排版及LibreOffice。
- **Tests / results**：17/17数学；60统计/63原件；3312点独立几何；16公式/10图/18页。
- **TASK-BLOCKING（完整P4）**：RSS全局路径未取得、原平面完整输入缺失、完整重复及原六环境/m曲线未通过。
- **KNOWN LIMITATION**：小种子集、配对条件重复、全关节距离/统一步长与原调优不同、离散资格无连续证明。
- **DEFERRED**：FR3多分支IK、实际抓持/赋时/Isaac，五篇完成后另审；不进入P2。
- **LEGACY**：原TASK03历史精度失败、TASK06部分完成、B0执行不满足等原判保持。
- **Attempt budget**：科学修正3/3已耗尽；报告图例修订不改变算法、数据或判据。
- **Escalation**：不申请第四轮算法调整，按授权交付真实失败及差距，停止待审。
- **Paper fidelity**：[ORIGINAL] RSS/PCS/NR/RBS机制；[ADAPTATION]20R重建、GEOS与NumPy；
  [ENGINEERING]日志/有限预算/资格核查；[DEVIATION]原输入、软件、步长调优及统计范围差异全部披露；
  [EXPERIMENTAL]独立E0/E1比较，不称原六环境精确复刻。
- **Records updated**：STATUS、WORKLOG、EXPERIMENT_LOG、BUGS、DECISIONS、USER_FEEDBACK均新增本次条目。
- **Recommended next step**：审查P4报告和失败结果；本次上传后停止。
- **Git branch / source**：reproduce-p4-three-methods；科研源码3d51ca0、保全219a8a7；最终交付见该分支HEAD。
