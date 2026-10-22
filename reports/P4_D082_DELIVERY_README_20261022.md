# P4 D082 研究交付与复现入口

状态：**D082 VIRTUAL_SIMULATION_VERIFIED_DISCRETE_RECONSTRUCTED**。完成一套真实端到端20R闭链虚拟规划研究及独立离散验证；原论文全范围仍为 **PARTIAL**，RSS随机完整规划仍为 **FAILED**。全部历史失败保留，交付后等待用户审核。

## 交付入口

- 中文研究报告：`P4_D082闭链规划算法与完整虚拟仿真研究报告_20261022.docx` 及同名PDF。含可编辑公式、7幅真实数据/算法图、比较、局限及双FR3潜在应用分析。
- 完整范围：`P4_D082_ORIGINAL_VS_APPROVED_VS_ACTUAL.md/.csv`，211行、257列；原248列逐值继承，追加9列。原30项主义务T01–T30全部保留，21项VI专属只读归档。
- 算法与失败：`P4_D082_ALGORITHM_FINDINGS_20261022.md`；空间保存证据：`P4_D082_SPATIAL_RECOVERY_20261022.md/.json`。
- 独立验证：`../results/20261022_D082_independent_planar01/`；全部CSV、JSON、26份增密NPZ、正负oracle、运行耗时及SHA清单均在其中。
- 保存结果分析：`../results/20261022_D082_saved_analysis01/`；逐调用、真实父子边、最终解边、分层失败和RSS构造记录。
- 图表：`p4_d082_research_assets_20261022/`；脚本在 `../scripts/p4_d082/`。
- 本轮复用边界和任务记录：`P4_D082_REUSE_AND_GAPS.md`、`P4_D082_POST_TASK_20261022.md`。

## 实测结果与分母

主统计来自原 `results/20261019_D081_stability_pilot/` 的50次真实调用：E0/E1 × RSS/PCS/fixed-0/fixed-16/NR × `[7,23,41,59,73]`。共同每调用1秒、120外迭代、300树节点；RBS叶长0.05 rad、深度12、最多256次投影。输入模型与科学代码SHA均与原运行一致。

| 方法 | 每个环境成功/5 | E0平均wall/s | E1平均wall/s | 成功路径平均长度/rad |
|---|---:|---:|---:|---:|
| RSS | 0/5 | 1.000157 | 1.000178 | 无 |
| PCS full | 3/5 | 0.543752 | 0.569454 | 3.729474 |
| PCS fixed-0 | 5/5 | 0.148059 | 0.177601 | 3.849089 |
| PCS fixed-16 | 0/5 | 1.000125 | 1.000094 | 无 |
| NR | 5/5 | 0.032505 | 0.038454 | 1.301996 |

26条SUCCESS记录、24条TIME_LIMIT，其他终止失败0。26条记录对应13条不同关节路径，各自分别在两个环境验证，不能当作26条独立随机路径。旧20次pilot与主统计有重复seed，不合并成每组7个独立样本。wall平均包含超时，不是成功求解平均或无条件加速比；历史CPU未记录。

独立程序不导入生产FK/IK/策略/规划或GEOS，使用累积变换、解析线段几何及独立PCS/NR中点计算。2142个原保存点、2116条原叶、6348个新增中点，共8490个离散状态通过；11个正负oracle通过。最大位置残差9.039665918e-9 m、角度残差2.220446049e-15 rad，最小净距0.053965014 m，最小限位余量0.346012241 rad。GNUtime为3.62秒wall、4.93秒CPU、417528 KiB最大RSS；内部计时范围不同，保留在summary，不混加。

全PCS成功解的最终分划切换为0；搜索树中仅1次真实父子边切换，发生于超时调用。fixed-0兼容端点且更好，fixed-16端点分支相反为结构负对照。13对跨环境成功q路径逐值相同，新增障碍未形成有效窄通道挑战。因此没有PCS性能优势结论。空间III的4次最终主动臂角色切换属于另一套保存证据。

RSS的72次奇异请求、2304次构造全在闭合IK阶段拒绝，0个合格随机奇异目标。固定奇异夹具的rank2和两侧桥只证明局部机制，不能计入RSS规划成功。根因保留UNKNOWN（采样支持/重建闭合可达性耦合），未定位为新实现bug，也不指控原论文错误。

## 原始证据与复现命令

在仓库根目录运行。科学环境为Python3.10、NumPy1.24.4、Shapely2.1.2、Matplotlib3.5.1，见 `requirements-p4-three-methods.txt`。规划和独立验证脚本拒绝覆盖已有输出。下列是复现说明，本轮交付没有再次执行50调用。

```bash
python3 -m unittest tests.test_p4_comparison_model tests.test_p4_comparison_strategies
python3 scripts/p4_d081_stability_pilot.py --output results/D082_user_replay01
python3 scripts/p4_d081_numeric_pilot.py --output results/D082_user_numeric_replay01
python3 scripts/p4_d082/independent_planar_validation.py --output results/D082_user_validation_replay01
python3 scripts/p4_d082/audit_spatial_saved_20261022.py --output reports/P4_user_spatial_replay01.json
python3 scripts/p4_d082/build_research_figures.py --output work/D082_user_figures01
```

主协议为 `configs/p4_d081/numeric_stability_pilot_v1.json`，机制协议为 `numeric_pilot_v1.json`。独立验证器固定读取已冻结的D081主统计，不会因为上一行产生新规划目录而自动改输入。绘图器也固定读取交付数据；新目录只指定输出。`results/20261022_D082_saved_analysis01/analyze_saved.py` 是只读输入的后处理入口，但会覆盖其自身派生输出，故不要为“检查”而重跑已交付的该脚本。

Word使用Codex内置Python；这与科学运行的系统Python分开，不混用二者依赖：

```bash
ARTIFACT_PY=/home/ubuntu2004/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
"$ARTIFACT_PY" scripts/p4_d082/build_chinese_research_report.py --output work/D082_user_report01.docx
"$ARTIFACT_PY" scripts/p4_d082/render_report_isolated.py --docx work/D082_user_report01.docx --output-dir work/D082_user_report_render01
```

报告构建读取已发布的7幅图及独立summary，输出路径必须不存在。在另一台机器上，替换ARTIFACT_PY及渲染器的`--dependencies`为该机内置运行时路径。当前Ubuntu22与捆绑LibreOffice/Poppler的glibc不兼容，轻量渲染配方使用固定Ubuntu24镜像的任务局部动态加载器；需Docker、网络或已备sysroot及Noto CJK字体。它不修改主机库、不调用桌面Office；精确镜像、两次失败/恢复和日志见 `p4_d082_render_engineering_20261022/`。无需为阅读最终PDF安装上述工具。

独立验证关键身份：summary SHA256 `867755cda518eb7abb8776d827733604266e5be8440aed64fd4f7fff5ceffbc1`；运行脚本 SHA256 `42561f047c278a79e45988bdf75426257982c80443e9d56338129354abf51c77`。完整输入和60项输出清单在对应结果目录。空间审查的18646是保存哈希引用次数，不是18646个唯一文件。

## 结论边界

这些是重建机构的有限离散结果，未认证连续CCD、动力学、原作者native TCP几何等价或硬件执行。III aligned资格仍伴随649/649 native TCP mismatch。Fig3不同m使用不同构型总体，不能识别分划数的因果作用；Fig5每方法384输入独立于每方法768投影统计。NR更新平均7.446615次，旧8.446615字段为trace长度。

原Table I的22500调用是论文事实，D080的18000是D081已取消计划，当前主统计是50；原六环境、500/格、500000投影、约50000点对及m20规划时间未复现，不以本报告覆盖。V5只保留工程候选，VI不追加，P1/P2/P3/P5、Isaac和FR3适配均不启动。
