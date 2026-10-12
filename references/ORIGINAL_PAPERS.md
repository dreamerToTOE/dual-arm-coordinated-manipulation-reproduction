# 五篇论文原文与 DEFORM 报告参考资料目录（2026-10-12）

> 最新决策：**先复现核心算法、最小实验与导师要求的报告，再集中研究场景改进和 Isaac Sim 集成**。执行顺序 `P4（报告收尾）→ P2 → P3 → P5 → P1`。详细任务见 [复现优先顺序](../docs/PAPER_FIRST_REPRODUCTION_ORDER.md)。
>
> 本目录包含**五篇已核实原文的身份、权威链接、私有本地副本校验和阅读指令**，并非论文全文公开镜像。本 GitHub 仓库是公开的，未经授权不得在仓库中再发布有版权限制的 PDF 或来源不明的 DEFORM 示例 Word。

## 核实的文献和原文入口

| 编号 | 完整论文题名／刊物／作者 | DOI 与论文原始入口 | 本地原文文件 |
|---|---|---|---|
| **P4** | Avishai Sintov, Andy Borum, Timothy Bretl. *Motion Planning of Fully Actuated Closed Kinematic Chains With Revolute Joints: A Comparative Analysis*. IEEE RA-L, 2018 | [DOI](https://doi.org/10.1109/LRA.2018.2846806) · [作者手稿 PDF](https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf) · [作者代码](https://github.com/avishais/CKCplanning) | `references/private_sources/P4_original.pdf` |
| **P2** | Marco De Simone, Marco Costanzo, Giuseppe De Maria, Ciro Natale. *Cooperative Object Transport and Assembly: Pose/Force Control by Visual-Tactile Feedback*. IEEE RA-L, 2026 | [DOI](https://doi.org/10.1109/LRA.2026.3665445) · [公开作者手稿页面，CC BY 4.0](https://www.researchgate.net/publication/400852785_Cooperative_Object_Transport_and_Assembly_PoseForce_Control_by_Visual-Tactile_Feedback) | `references/private_sources/P2_original.pdf` |
| **P3** | Dong-Hyuk Lee, Myoung-Su Choi, Hyeonjun Park, Ga-Ram Jang, Jae-Han Park, Ji-Hun Bae. *Peg-in-Hole Assembly With Dual-Arm Robot and Dexterous Robot Hands*. IEEE RA-L 7(4):8566–8573, 2022 | [DOI](https://doi.org/10.1109/LRA.2022.3187497) · [出版平台](https://ieeexplore.ieee.org/document/9811265) | `references/private_sources/P3_original.pdf` |
| **P5** | Seyed Sina Mirrazavi Salehian, Nadia Figueroa, Aude Billard. *A Unified Framework for Coordinated Multi-Arm Motion Planning*. IJRR 37(10):1205–1232, 2018 | [DOI](https://doi.org/10.1177/0278364918765952) · [作者项目页及代码](https://nbfigueroa.github.io/multi-arm-coordination/) | `references/private_sources/P5_original.pdf` |
| **P1** | Tianqi Zhu, Jianliang Mao, Jun Yang, Shihua Li. *Real-Time Dual-Arm Cooperative Manipulation Under Multiple Constraints: A Two-Stage Sampling MPC Approach*. IEEE T-RO 42:1942–1960, 2026 | [DOI](https://doi.org/10.1109/TRO.2026.3686224) · [论文项目与代码入口](https://dq-gpu-mpc.github.io/) | `references/private_sources/P1_original.pdf` |

这些条目对应用户此前发来的五篇**英文论文全文 PDF**，不是中文版译读摘要。首次使用须校验文件 SHA256、题名、论文公式编号和图表编号，不能以 `references/P*.md` 的二手摘要替代原文。

## 第六份资料：导师要求的报告样式

- **DEFORM 示例报告**：`references/private_sources/DEFORM_report_example.docx`，用户上传的 18 页《第4篇DEFORM论文复现汇总》，**是复现报告参考范例，不是 P1–P5 的第六篇待复现论文，也不能据此推定用户拥有公开转载授权**。
- 示例结构：第一部分「数学模型」（运动学、队形/任务分配、控制与约束、评价公式）；第二部分「仿真复现实验」（环境参数、基础实验、轨迹/误差曲线、复杂场景、结果对比、已完成内容及与原文差距、代码与结果使用、参考依据）。
- 在本项目中借鉴**报告结构和证据类别**，不能把 DEFORM 的实验结果套到双 FR3 上。具体统一模板见 [导师式复现报告规范](../docs/PAPER_REPRODUCTION_REPORT_FORMAT.md)。

## 用户自有原文副本的 SHA256 核验

本地六份材料已经在当前会话中确认存在，并整理为一个供用户个人研究使用的资料压缩包。**由于公开仓库的版权再发布限制，PDF/Word 字节不在本次 GitHub 提交中**。放置到 `references/private_sources/` 后核对：

| 文件 | SHA256 |
|---|---|
| `P1_original.pdf` | `8b4589ce07f932bf1294c7a39b30320a8791f630a4bcd2cd71782b3a2a56de3c` |
| `P2_original.pdf` | `0188b6be5f9029b40c99b377bcd1e2885ec6e6b56acc49276d6fe1fc72cc0346` |
| `P3_original.pdf` | `d16235aa3af25e8e8a52299abb8d1e47c5f9190b3e766f2450cd963687139bd1` |
| `P4_original.pdf` | `193710e5a9d4284cf62b30ff189a1df038a9d5c5ce3f1545525dc2f78bea08c6` |
| `P5_original.pdf` | `6f367be45e0c925df64ec5e4ab3046e1de8aa96627c65ddb2fd71720d9eedc02` |
| `DEFORM_report_example.docx` | `d036bd716f89498d379d3f7bdd734542f04e6d5019ed3870a27eeabfa4a64c2d` |

核验命令：`sha256sum references/private_sources/{P1,P2,P3,P4,P5}_original.pdf references/private_sources/DEFORM_report_example.docx`。

文件可从用户的**私人资料压缩包**解压至仓库工作树（不追踪上传）；如果 Codex 的运行环境没有这些文件，应先检查上述 DOI/作者授权版链接并告诉用户缺失项，不得推测原论文内容或声称已通读。特别是 P3 的所给 IEEE 正式 PDF 有“再发布需 IEEE 许可”标记、P1 版权页写有 © IEEE 和 all rights reserved；P5 的所给 PDF 提及期刊复用许可，P4 作者手稿未附明确二次上传授权。P2 所给版本标注 CC BY 4.0，但本分支仍统一采取**链接+本地副本**方式；未来若要公开原文须逐篇核对具体许可与署名。

## 论文阅读与代码复现前的强制流程

1. 打开当前论文 `P*_original.pdf`（若本地缺失，走可信公开原文/作者手稿），读**全文**，并记录论文的**问题假设、系统、公式/算法/图、实验条件、对比对象**及确切页码；不可只阅读 GitHub 参考卡。
2. 将论文对应方法逐项标记：**原论文方法、软件实现、双 FR3 适配、工程补充、尚未复现**。P4 比较 RSS/PCS/NR，已有核心实现主要是 NR/RBS/双树，不等于整篇方法对比全部完成；P2 不得用抓取矩阵替代位姿/内力闭环；P3 不得用纯位置推送替代力位混合；P5 需注明原文的数据驱动避碰模型；P1 需实现双阶段采样/模式选择及等式约束处理。
3. 先设计能够**产出导师报告图表的最小实验**，记录先验实验协议、原始数据、绘图代码、成功与失败、与原论文不可比的变量。
4. 生成完整中文复现报告并经审查，才申请下一篇；不要自动创建漫长的 Isaac 场景排错任务。状态词用中文，保留原审查缺口不改判。

[历史科研卡 P1](P1_sampling_mpc.md) · [P2](P2_pose_force.md) · [P3](P3_peg_in_hole.md) · [P4](P4_closed_chain.md) · [P5](P5_qp_coordination.md)
