# D081 P4 数学复现接管与数值 pilot 入口

日期：2026-10-19。执行分支：`p4-full-reproduction-pcs-study`。

## 状态保全

- `HEAD` 与 `origin/p4-full-reproduction-pcs-study` 均为 `2b2fd1fa`；远端已包含 D080 取消 18,000 次正式规划和当前 D082 交付层级说明。
- 工作区已有的 `baselines/p4_comparison/strategies.py` 固定 PCS 修改、`scripts/p4_d082/audit_iii_saved_path.py`、III 审查 JSON 和其他工作树未跟踪日志不覆盖、不清理。
- 已检查运行进程；没有本仓库的 RRT/PCS/RSS/NR 求解进程，Isaac bridge 进程属于其他工作树服务，不作停止操作。
- 原论文私有 PDF SHA256 为 `193710e5a9d4284cf62b30ff189a1df038a9d5c5ce3f1545525dc2f78bea08c6`，已通读全文并用公式/图表编号绑定本入口。

## 可以直接复用的成果

| 成果 | 复用方式 | 科学边界 |
|---|---|---|
| 平面 20R `PlanarModel` | 直接复用闭链、解析 3R IK 两分支、3×20 Jacobian、关节界与 GEOS 胶囊/圆障碍 | `RECONSTRUCTED` 环境 I 同类模型，不冒称作者原 Figure 2a 输入 |
| NR / RBS / 双向树 | 直接复用 `nr_project`、`rbs_connect`、`planner.plan` | 当前是离散中点资格；未宣称连续 CCD |
| APC / RSS / PCS | 复用 `Strategy` 的真实 IK 分划、RSS 奇异请求、PCS 分支选择；新增 fixed partition 消融 | RSS 仍可能全局失败；固定分划失败要保留 |
| ABB/Comau 数学核 | 复用 `physical_nr.py`、`abb_independent_oracle.py`、`rss_geometry.py` | 原始 KDL/PQP 运行时与独立重建标签分开 |
| 环境 II 合格路径 | 只读复用已有 R2/NR/PCS 独立路径与闭链/限位/离散碰撞记录 | 不重跑求解；不把路径升级为原论文统计 |
| 环境 III exact source 649 节点 | 只读审查 `audit_iii_saved_path.py` 的闭链、分支、限位、aligned 碰撞和叶距 | native TCP mismatch 与连续碰撞仍单列；审查不新增 source/planner call |
| 环境 V 负例与 TCP 差异 | 报告中引用原始保存记录 | 不用负例替代成功路径；不重新启动 V source |

## 不再作为数值实验前置条件

1. 作者全部 C++/OMPL/KDL/PQP 接口逐字节恢复、全部旧构建数量、Isaac Sim/ROS/真实机器人和高保真动力学。
2. D080 的 18,000 次（36×500）正式规划及其专门 pilot/预算申报；原 Table I 22,500 分母和 VI 归档状态继续在范围表中保留。
3. 在可靠的数学模块可运行后重复编译、重复审查和重复已完成的 II/III 路径求解。

## 先执行的真实数值 pilot

`configs/p4_d081/numeric_pilot_v1.json` 固定配对 PCG64 种子、投影扰动尺度、Fig.3/4/5 分箱、规划时间/节点/RBS 预算，并保存每次原始记录：

1. 闭链、FK/IK、Jacobian 差分、平面奇异秩和空间 ABB II/III 保存端点数学核；
2. APC 与 NR 的同输入投影成功率、迭代数、投影距离和真实 Python 计时；
3. Fig.3 可实现的被动分划数量 `m=1,2,3,7,16`；`m=20` 因本重建 20R 只有 17 个连续三关节非零分划，标为未实现，不补造；
4. Fig.4 局部可见性、Fig.5 投影前后距离变化；
5. Table I/II 的阶段性 planar proxy pilot：RSS、PCS、fixed PCS、NR 在稀疏/复杂障碍下的真实成功、失败、超时、节点和路径指标。

## 真正的科学阻塞与预估

| 项目 | 当前阻塞 | pilot 后预计 |
|---|---|---:|
| 数学资格与代表性路径 | 已有代码/路径可直接复用；主要工作是统一输出与独立审查 | 0.5–1 天 |
| APC/NR 投影与 Fig.3–5 pilot | 原始 500,000/50,000 规模尚未执行；原图输入/完整 m=20 结构不公开 | 1–2 天（pilot），完整批量需据实测吞吐另估 |
| PCS full/fixed 与障碍消融 | 当前平面模型只有 17 个合法连续 3R 分划；空间全分划解析 IK 不完备 | 2–4 天（代表性空间/平面） |
| RSS | 奇异构型需真实被动 Jacobian 秩缺陷和跨分支连接；全局路径历史上失败 | 1–3 天资格；若仍失败按 D079 根因归类 |
| Table I 原环境 II–V | 原作者输入、依赖和完整公平统计不可完全获得；18k 已取消 | pilot 后给出实际吞吐/置信度/资源预算，不把小样本写成 500 次 |
| 中文 Word/PDF | 需要将真实图表、差异标签和失败记录整合 | 1–2 天 |

本文件只登记接管和执行入口；结论以 `results/20261019_D081_numeric_pilot/` 中的真实数据为准。
