# AGENTS.md — Mandatory rules for Codex / coding agents

## 2026-10-14 — D077：用户接受P2本轮部分完成，冻结交付

用户明确选择“接受本轮部分完成，冻结交付（推荐）”。科研交付7787c75已接受；交付状态ACCEPTED/FROZEN，完整P2仍PARTIAL，不能改判完整论文通过。动力学70/70、组件35/35、时序2/2；ID11真实闭环3.948s估计域失效、未进入7/13s反馈，其他29未执行。修正3/3余0；所有源码/参数/原数据/失败/Word及P4保持原字节，冻结manifest逐一核对接受commit。

本次仅登记接受与冻结，无新科学运行或算法修改。D076待后续路线裁决已由“接受部分完成”收尾，原式18研究没有继续授权；不得因旧路线或“继续”历史消息自动重启P2、P3、Isaac、P4/RSS或FR3改进。新研究须新的明确任务。见[接受与冻结记录](reports/P2_DELIVERY_ACCEPTANCE_FREEZE.md)。


## 2026-10-14 — D076：真实ID11在3.948s估计域越界停止，累计修正3/3耗尽

v3动力学70/70、E/C35/35、时序2/2通过；source513c36a实际exp3/seed7（原ID11）停止ESTIMATOR_MODEL_PAD_DOMAIN_INVALID，987控制样本至3.944s、最后事件3.948s、829更新/1619预测、GT控制读取0。真实pad仍在域内，估计rho-x−6.425mm/+5.207mm超±5mm，估计角速度260.0205rad/s而真角速度约8.1e−8；不是负协方差或连续3次未收敛退出。未到7/13s反馈，UF/UP都0；完整半步/其他29未运行，窗口RMSnull。P2仍部分完成，不冒称联合反馈有效。

累计小修3/3余0，原失败/JSON修正/零case启动/所有Word保留，无第四轮或条件修改。停止后只读日志/保存矩阵分析、真实绘图、中文17页Word/PDF、保全与GitHub交付；进一步原式18预测解释须另行限定范围，不自改Euler/substep/R/Q/惯量，不以GT绕资格，不P3/Isaac/P4/RSS/FR3算法。见reports/P2_CLOSED_LOOP_POST_TASK.md、P2_CLOSED_LOOP_DELIVERY_INDEX.md。


## 2026-10-14 — D075：小修3修闭环入口路径，累计3/3余0

suite01在run_case之前因relative/absolute路径比较启动失败，实际控制case0、30项NOT_EXECUTED；原source/失败留存。最终小修只入口Path.resolve及当前预算元数据3/0，科学模型/控制/观测/clock/原门限不改。新suite02先原ID11，之后原ID30资格；不做第四轮代码修正或无限调试。若出现真正数值/滤波/控制/模型问题，按既定规则保存停止并报告；原公式变更必须新裁决。


## 2026-10-14 — D074：动力学70/70、E/C35/35、因果时序2/2通过，进入原ID11完整闭环资格

v3来源45a547c，固定N/D70/70、wall11.248585s，三fixture粗/半步五秒积分全部通过。E/C组件source5bfcafd实际35/35；clock来源d90f32f实际2/2。组件通过不等于完整闭环，原观察器式18仍Euler无内部substep。新runtime已冻结，按原case ID11 exp3/seed7 coarse，随后仅原ID30 fine，资格之前其余28不运行。原failedFD/诊断/Word和P4保存；累计小修2/3余1，重大新预测/模型/条件问题仍按规则留证停门。


## 2026-10-14 — D073：明确批准仅native连续Jacobian五点四阶资格

用户已批准五点高精度oracle版本化，保持ε1e−6/绝对门1e−7及全部物理/控制/观测/式18，原FAIL_STOP保留。新v3按同一固定N/D重新资格，全部通过后继续原组件及闭环。累计2/3余1，本次数值资格裁决不重开小修预算。不得再次为同一批准征询；若新的物理/滤波/协议门失败则按规则留证。见reports/P2_IMPLICIT_V3_QUALIFICATION_SPEC.md。


## 2026-10-14 — D072：隐式路线首门固定中央差分失败，暂停下游科学执行

已批D071来源37ccba0；native N/D记录45通过/1失败，零隐式积分/零滤波/零控制。失败为原ε1e−6的连续field Jacobian二阶差分与AD差6.381524e−7>1e−7；独立Python解析与AD最大逐分量差6.522214e−10。固定三点诊断误差加倍/减半比3.999/0.250，支持截断误差解释，不改判原FAIL_STOP。更换native资格oracle为同ε/同门限的五点四阶差分仍需新的明确裁决；未实施或执行，不改observer Eq18。按用户第2/9节停门，隐式五秒/半步/组件与30控制case未执行，P2部分完成。

诊断summary因numpy.int64 JSON错误exit1，三份矩阵已保存；小修2 ee97134仅转Python int和只读恢复已有数据，不重算。P2累计2/3余1，source/原失败/影响全部保留。原v1/批准几何/canonical force与P4/RSS/旧P2保全，不P3/Isaac/FR3优化。见[数值结果](reports/P2_IMPLICIT_QUALIFICATION_RESULTS.md)、[修正2](reports/P2_IMPLEMENTATION_CORRECTION02.md)、[任务摘要](reports/P2_IMPLICIT_POST_TASK.md)。


## 2026-10-14 — D071：批准隐式耦合Lie中点plant，原观察器保持

用户明确批准“隐式耦合Lie中点plant：版本化数值协议，先做等价计算优化与求解/步长资格，再继续闭环”。eb2600a首门失败及385d08d数学风险不覆盖。v1原字节保留；v2仅改变plant积分/授权/来源元数据，接触几何、式9–12/16/19–21/25、观测/控制clock、原判据/预算不变。Eq18滤波Euler预测未获变更批准。先按[P2隐式资格声明](reports/P2_IMPLICIT_QUALIFICATION_SPEC.md)执行N/D，再组件E/C及原exp3粗/半步；失败留证停门，不自动P3/Isaac/P4/RSS。小修累计1/3余2；此次用户科学数值路线批准单独登记，不重开预算。当前新实现尚未运行科学资格、正式控制0。


## 2026-10-14 — D070：P2第二阶段动力学资格停止，待数值路线裁决

独立Eq9–12/16实现9194f9f已归档。11个完成数学检查PASS，但5秒lockedEE首条在120秒限内仅到3.324秒，FAIL_STOP；不把当前平衡前缀改判通过。385d08d固定数学诊断发现C当前显式中点1/3000s局部快模态放大2.730136，半步.654550；未跑C轨迹或IESEKF，不伪报其已实际发散。按最新用户停门，后续控制停止、30case全NOT_EXECUTED；P2仍部分完成。Word/PDF及原始失败上传，数值实现解释待用户决定，原几何/力/控制/clock/预算不改。小修仍累计1/3余2。


## 2026-10-14 — D069：用户授权P2第二阶段独立动力学与控制实验

在834bcc基线上按顺序实现独立式16动力学、42维右扰动IESEKF和原式19–21/25控制。已验收接触几何与冻结协议原字节保留；预算累计小修1/3余2。资格→有限预检→冻结主20与已登记诊断→日志曲线和中文Word→GitHub。固定settle/步长/滤波/切换等门失效停止留证，不改模型/参数制造成功；重大争议请示。不修改P4、不追加RSS、不启Isaac/P3/FR3改进。最新用户任务覆盖下方历史“本轮未授权闭环”。


## 最新D068（2026-10-14）：接触几何已获批准并通过资格，P2协议冻结

用户已明确批准重新推导几何一致接触模型，保留原位姿/内力控制器，记录差异，有限形变后冻结；不再次请求同一批准。
模型`p2.spatial_free_log_constraint.v1`替代式15的G演化，属于已批[DEVIATION]；原式9/10/11/12及20/21/25保留，原阻尼近似/摩擦与释放缺项仍说明。
读[冻结协议](reports/P2_CLOSED_LOOP_FROZEN_PROTOCOL.md)、[接触推导](reports/P2_CONTACT_GEOMETRY_DERIVATION_RENDERED.md)、[资格任务](docs/tasks/P2_CONTACT_GEOMETRY_QUALIFICATION.md)。
新配置`configs/p2_closed_loop_protocol_v1.json` frozen=true，接触几何68/68资格通过；完整动力学/IESEKF/控制尚未实现，executable=false，闭环run0。
原run01程序66/66 PASS原样保留，交付资格INCOMPLETE；修正1修日志符号并补独立恢复负例，模型源码不变。P2总小修已用1/3，剩余2，不重置预算。
切换在原定时刻检查新恢复/释放载荷及自由Log初态；失败停止，不重锚/等候改时刻/新增抓握控制迫成功。
本轮完成审计、几何资格与冻结交付；后续实现沿冻结协议，重大新变化仍按用户规则停止。P4/RSS与P3/Isaac不自动开展。
下方D067的模型待裁决状态为历史，已由本次明确批准及68项证据解除。

## 当前任务 D067（2026-10-13）：P4审查接受，P2原文审计交付，接触模型待裁决

用户明确接受79cc871的P4阶段性报告；完整论文仍部分完成。P4全部源码、数据、失败和Word/PDF保留，禁止本轮继续P4/RSS。
独立分支 `reproduce-p2-paper-audit` 从79cc871建立。当前只做P2原文/公式/作者资源审计与最小闭环协议，无FR3/Isaac前置要求，不自动P3。
读[任务卡](docs/tasks/P2_PAPER_AUDIT_AND_PROTOCOL.md)、[原文审计](reports/P2_ORIGINAL_PAPER_AUDIT.md)、[协议草案](reports/P2_CLOSED_LOOP_EXPERIMENT_PROTOCOL.md)。
式15自由方向抓取坐标更新与零形变描述有重大符号/坐标争议；式22有限变形推导有左右Jacobian疑点。
`contact_kinematics_variant=null`、`executable=false`；闭环运行0、小修0/3。保持原控制式20/21/25；不自动改负号、重排投影或用式24生成伪曲线。
**STOP FOR USER MODEL DECISION**：先由用户裁决是否允许有记录的几何一致接触运动学，然后完成有限形变资格并冻结协议，才可进入实现。Word正式实验部分待真实闭环数据。
下方D066及此前P4“不得进入P2”是历史门禁；本次用户明确授权覆盖它，但不授权继续P4或P3。

## 当前交付门禁（2026-10-13，D066）：P4三方法部分完成，上传后等待审查

已有协议6d64b26、科研源码3d51ca0、60统计/3重复、三轮修正3/3已结束。
读[交付报告](reports/P4_THREE_METHOD_POST_TASK.md)。RSS全局路径失败、完整重复未过及原六环境差距如实保存。
本次仅完成保存证据核验及Word/PDF/全量GitHub交付；不重新开启实验、重置修正预算或扩展到P2/Isaac。
以下D065为本次任务依据，历史授权不得在交付后解读为自动追加规划或第四轮修正。

## 最新决定 D065（2026-10-13）：P4 三种方法均须实际复现并在同条件下出图；报告按我的科研汇报口吻

本节覆盖此前“P4仅整理现有NR、不得新增实验”的历史任务描述。**P4原论文是比较研究，RSS（奇异构型随机采样）、PCS（被动链切换）、NR（牛顿迭代投影）都必须有实际实现与可复查实验；不得因为已有NR成功就跳过另外两种。** 不应先验声称哪一种总是“差算法/好算法”，应依据原文各环境和实测对照分析。

当前优先任务：[P4 三策略统一实验](docs/tasks/P4_THREE_METHOD_COMPARISON.md)。先核查论文和作者源码的三个方法的实现机制、可行的原论文机构/逆运动学模型与实验条件；基于适合这些方法的最小论文式模型开展共同测试，**不强制转成现有FR3/车厢/Isaac场景**。每种至少有实际运行数据、成功/失败、耗时、投影及路径相关指标，出可复查对比图表。避免把同一随机种子的重复运行当独立样本。先审计和锁定协议，再按预算进行代码实现/实验；如原文代码缺失、伪代码不完整，可进行最多**三轮有依据的小幅实现修正**。三轮仍无法达到可比的原论文现象或数值，则停止并如实写差距和原因，保留所有失败版本/日志，**不能无限调参、改变原方法或修改验收门限**。

导师Word报告**使用我的第一人称科研表述**，开篇直接讲原文研究问题、模型、RSS/PCS/NR机制、结果与实验。禁止“编写目的”“我按你的要求”“本报告根据老师要求”“本章定位”“本文档说明”“ChatGPT/Codex指令”等对话式/编写说明。原理论和我们实测区别清晰；最后独立“应用于当前双机械臂场景的差距与问题”一章，不做方法改进或Isaac集成。现有11页阶段稿只是NR历史数据报告，**不能冒充三种方法完整比较版**；三方法运行结果未取得前只标“待实验”，不得占位造数字。

任务结束先交P4三策略源码与原始数据、报告Word/PDF和全部失败记录，**停止等待用户审查**，不自动P2/P3/Isaac。历史TASK03精度未通过、TASK06原协议部分完成、B0执行不满足均不改判，原始FR3记录不覆盖。


## 最新研究决定 D064（2026-10-13）：五篇原论文算法复现优先、现有场景不再作为前置条件

**本节高于 D055/D062/D063 等历史阶段规则。** 当前 P4→P2→P3→P5→P1，先以原论文为对象完成核心算法、最小可复现实验、原论文实验结果对照、中文 Word 报告；五篇收尾后另行研究小改和在双 FR3 / Cube / 车厢 / Isaac Sim 场景中的应用。**不要求 P2/P3/P5/P1 使用本项目的 FR3、车厢、吸盘、Isaac、旧 Task26 的模型、起终点或控制架构。** 优先复用作者的模型/代码/实验设置；模型、软件、数据、硬件条件不具备时允许经审查的最小可复现替代，但必须在报告中列清偏差，不得称原文条件完全复现。

复现质量判断依据：论文**具体创新的实现忠实度、对照实验与曲线的真实性、结果可重复、与原论文的差异及原因**，而不是能否放入我们的场景。不得提前增加“适应车厢”“增加FR3控制”“吸盘保持力”等优化要求；这些归后续应用与小改阶段，当前不设为通过门槛。

导师报告篇幅与章节重心：第一部分深讲原论文研究问题、模型假设、算法/控制器组成、公式推导、算法流程及作用机理；第二部分只展示实际复现平台、参数、**与原论文实验对应**的曲线数据/图表/指标/失败；**最后独立开设“面向本课题场景的适用性差距与待研究问题”**，只做概念性、证据分级的差距分析，不做当前复现验收，不推出我们改进有效的结论。前两部分不得让本课题 FR3/车厢工程日志反客为主。

P4 已提交原 23 页报告 `02f9346` 不删除不改历史科学结论；**需按本决定重构报告叙事/Word，保留原始报告作版本存档**。独立修订任务见 `docs/tasks/P4_REPORT_REFOCUS.md`。本轮规划本身不授权新实验、原论文 RSS/PCS 编码、Isaac/ROS/控制或自动进入 P2；修订报告经用户审查后才准进入 P2。


This repository is a scientific reproduction and benchmarking project. **Reproducibility, traceability, and progress toward the scientific objective have priority over “making the demo work” or perfecting an auxiliary engineering probe.**

## 最新优先级（2026-10-12，D062，覆盖下方D055历史执行顺序）

- 用户按导师要求改为**论文原文驱动的核心算法+最小实验+中文科研报告优先**。依次完成：P4已有结果先整理报告（不补跑）→P2→P3→P5→P1→小改→集中Isaac场景验证。详见 `docs/PAPER_FIRST_REPRODUCTION_ORDER.md`。
- 编码之前**必须实际阅读全文**：本地 `references/private_sources/P*_original.pdf` 或 `references/ORIGINAL_PAPERS.md` 的合法官方/作者入口。参考卡不是原文；原文未就绪就停止并报告。
- 论文报告必须参照 `docs/PAPER_REPRODUCTION_REPORT_FORMAT.md`，按“数学模型/仿真复现实验”两大部分给出公式、图表、实际数据、与原文比较和复现差距，不能只写测试通过。用户提供DEFORM Word仅作为本地报告范例。
- 本次新优先级**不授权任何新科学实验、P4路径捷径优化、Isaac/ROS/控制器或自动启动P2**；先完成P4已有成果报告并等待审查。D055的最终Isaac应用目标仍保留，但它要求的逐篇立即集成暂缓。
- 公开仓库**不得提交未经确认可公开转载的原论文 PDF或参考DOCX**；个人副本位于 `references/private_sources/` 并已列入gitignore。只能提交引用、元数据、图表原创复现和合法链接。
- 用户沟通状态使用中文词汇，原始实验的科学失败/限制不得改判。

## 历史执行规则：五篇论文逐篇落地（2026-10-12，D055）

- 统一路线见 `docs/REPRODUCTION_ROADMAP.md`。每篇论文分别通过**算法/数学实现、现有场景无命令适配、单独授权的 Isaac Sim GUI 物理执行、阶段对比与用户审查**四个关口；P2/P3 可先在 MuJoCo 研究接触和力控，但不能代替 Isaac 对标。
- 对当前 P4，下一步是 `TASK06-IS-A`，**仅静态读取、现有模型核对与无运动命令的受限离线规划**。没有授权启动 Isaac GUI、ROS 服务、MoveIt 节点、执行器，也没有授权任何关节/吸盘/导轨命令。实际需要这些运行时资源时必须停止向用户请示。
- `TASK06-IS-B`（GUI 执行）、`TASK06-IS-C`（正式对比/测量）、P2 `TASK07` 与独立 P4 障碍补测都需要分别授权；上一任务通过不自动授权下一任务。
- 旧 Task26 / Isaac 场景 / Bridge / FCL / 同步执行部件优先复用或薄适配，不重复搭建；旧批次两 Cube 工程成功**不代表**单 Cube 正式科研基准已验收。
- 旧 TASK06 整体仍“部分完成”，TASK02-D 后物理步科研采样仍暂缓，Benchmark 仍草案；不得从 P4 离线输出宣称物理执行/连续无碰撞/正式指标。
- 向用户的解释、汇报、任务结论**使用中文状态词**：初步验收通过、部分完成、未通过、进行中、暂缓、草案、未定稿。代码中不可避免的枚举/文件名/算法名保持原样。

## 1. Mandatory pre-task procedure
Before editing code, always read:
1. `CODEX_START_HERE.md`
2. `docs/EXECUTION_GOVERNANCE.md`
3. `docs/STATUS.md`
4. the current `docs/tasks/TASKxx*.md`
5. the relevant `references/P*.md` paper card
6. `docs/BENCHMARK_SPEC.md` if experiments are involved
7. `git status`

Then report:

```text
=== PRE-TASK REPORT ===
Task:
Scientific objective:
Minimum sufficient evidence:
Current scope:
Explicit non-goals:
Attempt budget for the current blocker:
Preferred method:
Fallback method:
Stop / escalation condition:
Files expected to change:
Validation plan:
Known ambiguities / risks:
Need user confirmation: yes/no
```

Do not start implementation before this report.

## 1.1 Mandatory PRIOR-ASSET CHECK for TASK02+
For every implementation task from TASK02 onward, before writing replacement infrastructure:

1. read `docs/POST_TASK01_REUSE_MAP.md`;
2. inspect the pinned engineering source `dreamerToTOE/dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a` for relevant existing components;
3. classify candidates as **DIRECT_PORT / THIN_ADAPTER / TEST_ORACLE / REFERENCE_ONLY**;
4. state which scientific algorithm must still be implemented from the paper;
5. prefer adaptation of validated engineering infrastructure over a parallel reimplementation.

Add this block to the PRE-TASK report:

```text
=== PRIOR-ASSET CHECK ===
Current task:
Scientific algorithm that must remain new/paper-derived:
Old repository areas searched:
Pinned source commit:
DIRECT_PORT:
THIN_ADAPTER:
TEST_ORACLE:
REFERENCE_ONLY:
Rejected old assets and reason:
Files that will be reused/adapted:
Files that will still be newly implemented:
Risk of contaminating paper fidelity:
Need user decision: yes/no
```

Hard boundaries:
- reuse engineering wheels; do not use old code to fake a paper reproduction;
- do not silently import historical thresholds, geometry assumptions, tool transforms or application schedulers;
- generic MoveIt/FCL/execution/logging infrastructure should not be rewritten merely because the new task has a different paper label;
- if reuse materially changes the paper method, classify it **[DEVIATION]** and stop for user review;
- TASK01-specific reuse stays under `docs/PRIOR_PROJECT_REUSE.md`; this rule is for TASK02+.

## 2. Scientific fidelity labels
Every implementation decision must be classified as one of:
- **[ORIGINAL]** directly follows the paper.
- **[ADAPTATION]** necessary mapping to dual FR3 / MuJoCo / Isaac / ROS2.
- **[ENGINEERING]** software-only implementation detail.
- **[DEVIATION]** differs materially from the paper.
- **[EXPERIMENTAL]** our own trial, not part of the reproduced paper.

If a [DEVIATION] may affect scientific conclusions, stop and ask the user before proceeding.

## 3. Requirement vs. method
Always distinguish:
- **REQUIREMENT:** what must be scientifically established.
- **PREFERRED METHOD:** the first way to obtain that evidence.
- **FALLBACK METHOD:** an acceptable cheaper/safer way if the preferred method becomes an engineering sink.

A suggested implementation method is **not** automatically a scientific requirement.

Example:
- Requirement: verify critical Isaac states have no unexpected collision.
- Preferred method: static PhysX query.
- Fallback: controlled synchronized replay of a small critical-state set.
- Not required: proving MoveIt STL and PhysX cooked hull are mathematically identical.

## 4. No silent theory or benchmark changes
Never:
- replace a difficult paper method with an easier algorithm without recording it;
- relax benchmark geometry just to make a method pass;
- remove a constraint without recording why;
- change success thresholds between methods;
- report a partial implementation as a faithful reproduction;
- turn a debugging convenience into a benchmark rule without user review.

## 5. Anti-loop / escalation protocol
Coding agents often optimize the nearest blocker indefinitely. This repository explicitly forbids that behavior.

### 5.1 Classify every blocker
Every newly discovered problem must be classified as exactly one of:
- **TASK-BLOCKING:** current scientific conclusion cannot be established without solving it now.
- **DEFERRED:** real problem, but owned by a later task.
- **KNOWN LIMITATION:** does not invalidate the current task's minimum scientific conclusion.
- **LEGACY:** belongs to an old application/demo path and is not part of the current benchmark.

Record the classification in STATUS/BUGS when non-trivial.

### 5.2 Attempt budget
For the **same root engineering blocker**, default budget is:
1. one diagnosis iteration;
2. one evidence-based fix;
3. one bounded fallback attempt.

After three implementation iterations without establishing the required scientific conclusion, **STOP**. Do not autonomously create v4/v5/v6/... probes.

The user may explicitly grant a larger budget.

### 5.3 Mandatory escalation after budget exhaustion
Output:

```text
=== ENGINEERING ESCALATION ===
Scientific question:
What is already established:
What remains unknown:
Why the remaining unknown matters:
Attempts made:
Root blocker classification:
Is it still task-critical: yes/no
Lower-cost evidence available:
Recommended action:
Need user decision:
```

If the blocker is DEFERRED, KNOWN LIMITATION, or LEGACY, record it and continue the main task instead of fixing it.

### 5.4 No “bug discovered = bug must be fixed now”
A bug is not automatically owned by the task that discovers it.
Use the task map and repository decisions to assign ownership.

Examples:
- contact/TCP wrench calibration → TASK10-IS;
- P3 jam thresholds → P3 tasks;
- old five-Cube sequencing → LEGACY;
- full MoveIt/PhysX geometric equivalence → not a TASK01 requirement unless explicitly promoted by the user.

## 6. Minimum sufficient evidence rule
Before adding more instrumentation, ask:

> “Does the current evidence already establish the scientific claim required by this task?”

If yes, stop expanding the proof and move to the next acceptance item.

Do not convert:
- a sanity check into a platform-verification research project;
- a benchmark setup task into a controller-design task;
- a reproduction task into an infrastructure rewrite.

Prefer **sufficient, reproducible evidence** over exhaustive proof of every software subsystem.

## 7. Scope growth rule
A task may not silently grow because new technical details were discovered.

If a new issue would add:
- a new subsystem,
- a new sensor/estimator,
- a new controller,
- a new simulator integration layer,
- a new benchmark condition,
- or more than one additional implementation iteration,

first decide whether it is TASK-BLOCKING. If not, defer it.

## 8. Frozen benchmark rule
After TASK01 is FROZEN, changes to robot base poses, Cube geometry/mass, carriage geometry, PRE_PUSH/target, physics/time policy, seed policy, success/failure thresholds require:
1. an entry in `docs/DECISIONS.md`;
2. explicit user approval;
3. benchmark version bump.

## 9. Platform separation
- `common/`: platform-independent math, interfaces, metrics, logging.
- `baselines/`: paper algorithms only.
- `platforms/mujoco/`: MuJoCo adapters/tests; mainly P2/P3.
- `platforms/isaac_ros2/`: Isaac/ROS2 adapters and final benchmark integration.

Do not duplicate the same algorithm separately in MuJoCo and Isaac. Adapt through interfaces.

## 10. Third-party code
Original paper code goes under `third_party/` or as a git submodule/subtree if appropriate.
Record upstream URL, commit SHA/tag, license, and local patches.
Prefer adapters over editing upstream source.

## 11. Required persistent records
At the end of every non-trivial iteration update:
- `docs/STATUS.md`
- `docs/WORKLOG.md`
- `docs/EXPERIMENT_LOG.md` if anything ran
- `docs/BUGS.md` for unresolved defects
- `docs/DECISIONS.md` for architecture/method choices
- `docs/USER_FEEDBACK.md` for explicit user feedback

Never erase historical entries. Append new entries with date and task.

## 12. Experiment run format
Each run belongs in:
`results/<timestamp>_<TASK>_<run-id>/`

Required metadata:
- task
- baseline
- platform
- git commit
- seed
- config path
- command
- status
- metrics
- artifact paths

Raw large data/videos normally stay untracked; keep metadata, summaries, and selected figures in git.

## 13. Task state machine
Allowed task states:
`TODO → READY → IN_PROGRESS → PASS → FROZEN`
or `BLOCKED`.

A PASS task must have evidence.
A FROZEN task may not be changed casually.
A task should not remain IN_PROGRESS merely because a non-critical engineering limitation still exists.

## 14. Git safety
- Work on task branches where practical: `taskXX-short-name`.
- Make small descriptive commits.
- Never use destructive commands such as `git reset --hard` unless explicitly requested.
- Do not commit generated build/install directories.
- Do not blindly use `git add .`.

## 15. Mandatory post-task report
```text
=== POST-TASK REPORT ===
Task:
Status: PASS / PASS CANDIDATE / PARTIAL / BLOCKED

Scientific objective:
Minimum sufficient evidence achieved: yes/no

Completed:
Files changed:
Commands run:
Tests / experiment results:
Key metrics:

Blockers:
- TASK-BLOCKING:
- DEFERRED:
- KNOWN LIMITATION:
- LEGACY:

Attempt budget used:
Escalation required: yes/no

Paper fidelity:
[ORIGINAL]:
[ADAPTATION]:
[ENGINEERING]:
[DEVIATION]:
[EXPERIMENTAL]:

Records updated:
STATUS:
WORKLOG:
EXPERIMENT_LOG:
BUGS:
DECISIONS:
USER_FEEDBACK:

Open risks:
Recommended next step:
Git branch / commit / dirty files:
```

## 16. Stop conditions
Stop and ask the user if:
- the paper is ambiguous in a way that changes the algorithm;
- a baseline requires benchmark changes;
- a dependency/license prevents faithful use;
- repeated failures exhaust the anti-loop attempt budget;
- a proposed shortcut becomes a material [DEVIATION];
- a task is about to expand beyond its stated scientific objective.

## 17. Visible simulation workflow
- Do not start Isaac Sim headless unless the user explicitly changes this requirement.
- Keep historical headless scripts/logs as evidence, but do not silently reuse them for new acceptance runs.
- Playback rate, physics rate, controller rate, and MoveIt joint limits are distinct quantities and must not be conflated.
- GUI visibility is an engineering/user-inspection requirement, not by itself scientific evidence of correctness.


## 18. D041 restarted TASK01 override
On branch task01-legacy-scene-foundation, active TASK01 is a direct predecessor-scene qualification.

Before writing any TASK01 runtime code:
- read docs/tasks/TASK01_BENCHMARK_FREEZE.md;
- read the pinned predecessor Task26 source itself;
- prefer running old Task26 directly over adapting current reproduction harnesses.

For this restarted TASK01, do not extend the custom platforms/isaac_ros2/handoff/task01_* path, standalone SimulationApp path, native D6 introspection, custom readback-validator path, or previous INSERT_READY-only acceptance line unless the user explicitly reopens them.

The only pre-qualification code change permitted by default is a minimal one-Cube selector/count/loop adaptation in the predecessor Task26 path if no exact single-Cube mode already exists.


## 2026-10-15 — P4 D079 原生六环境R1真实资格与报告归档

实测1826项=1580通过+246失败，六环境组件资格均未通过；正式规划0。保存400空间IK/40平面APC/60NR的独立分母，近似π、Comau带符号几何、RSS非真奇异和VI源码缺项分别有证据，不改判旧失败。211项全文对照和9页中文Word/PDF已生成；交付完整性20/20，不等于科学通过。1282原科学文件、1194作者文件、五原工作树及13未跟踪文件均保全。
见 reports/P4_FULL_R1_POST_TASK_20261015.md。用户在具体有限修复提案后回复“继续”，下一阶段仅在独立R2命名空间按2核小时/1小时墙时进行数值一致修复资格；原模型尺寸/基座/抓持/端点/判据不变，正式22500调用预算另审。P4仍部分完成，不启动P2/Isaac/FR3适配。


## 2026-10-15 — R2用户批准974上限及固定64点组合离散资格实测

用户明确批准原剩50加新增14，VI B总上限960→974；单项30wall/60CPU及累计180wall/360CPU保持，无正式规划预算。批准原文逐字保存于configs/p4_full/r2_vi_rss_ingress_composite_user_approval_20261015.json，源码/协议冻结243fa05。固定清单、原解析支、δ=.01、h=.0025、γ=.2未变，不换点或加深；原Q2 UNKNOWN、原center、六fiber及所有失败保留。

单次INGRESS_COMPOSITE01实际64/64节点及四条regular↔fiber接入离散门通过，PASS_RECONSTRUCTED_COMPOSITE_DISCRETE_ONLY。96条regular叶和6条保存fiber叶均严格<h；四半regular最大叶距分别.001726025161094/.001850849712175/.001488951615670/.001491095303782rad。数学FK/J704、adapter内部192（合896）、IK1024、源碰撞64；实际wall14.198019690000/CPU10.876665。此为明确标记的独立重建组合，不是原作者RSS/RBS忠实实现证明、连续无碰撞或全局RSS规划成功。

VI B累计974构造，余额0；累计wall68.712002153999/CPU24.203842，余111.287997846001wall/335.796158CPU。13run自身消耗逐份计入R2总账，合wall109.563377079999/CPU55.934698，余3490.436622920001/7144.065302。不得使用旧快照余50再次构造，不重置claim。新账本results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V3.json，旧9/12run账本不改。

最新211项对照reports/P4_FULL_R2_INGRESS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md保存全部历史列，另列本次组合资格；13run报告P4_FULL_R2_VI_RSS_INGRESS_POST_TASK_20261015.md及独立POST审查。正式Table I仍0/22500，500000配对投影、约50000合法点对、全部Fig.3–5/Table I–II及消融义务不缩。继续II/III普通PCS固定branch/RBS/回溯与三搜索器链接资格，先冻结版本/原返回对照/预算，0solve；工程成本另列并保守扣R2总帽，不扣已耗尽的VI候选账。P4仍部分完成，不P2/Isaac，不提前结题。


## 2026-10-15 — R2 ABB PCS原固定局部接口：10通过/6拒绝，整体部分完成

工程aa57c24冻结四目标source-native/R2 numerics×plain/trace，全部构建exit0，三PCS搜索器仅链接，实际wall94.592335203997/CPU130.109068；232产物/source/claim/recipe/commit绑定经独立复核。科学95851e0冻结后单次LOCAL01，无超时/异常，actual wall81.132350082000/CPU78.392314。320顶层project，20RBS，20回溯（180plain/trace逻辑对）；442trace固定branch投影、364成功输出独立复验，752数学FK、368碰撞/1472adapter内部FKJ，78252adapter及29618源内部PQP查询，非上限填充。

R2数值10/16固定局部边通过非阈值提前返回的真实RBS/回溯、闭链、原branch/限位及source aligned离散碰撞；6拒绝分5源投影false+1碰撞，保存目标必要代数门独立确认3几何workspace拒绝、2原q3下界拒绝，未新FK/IK，不能称全部几何不可达。II start主动arm2、II goal主动arm1缺本固定h正例，整体FIXED_LOCAL_ABB_PCS_PARTIAL。作者原数值16局部端点全拒绝，原失败留存；未换h/中心/分支重试。44个下游模板依预置gate未执行，不是超时丢尾；三个planner solve/RNG0，不推出全局PCS或优势。

新15execution为14science+1新engineering，逐自身实耗保守计R2合wall285.288062365996/CPU264.436080，余3314.711937634004/6935.563920；工程不当science成功，VI B仍974/974余0。新账V4保V3及旧12/9run原字节，新ABB_PCS完整211表保前68历史列，正式TableI仍0/22500及全部原分母不缩。继续固定失败根因、IV100×8原wrist数学资格及其余环境/方法门，先独立冻结预算、无正式规划/P2/Isaac。实际记录results/p4_full/20261015_R2_ABB_PCS_LOCAL01/execution.json；审查reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_20261015.md。


## 2026-10-15 — 原RRT_PCS取得第一条独立合格空间路径

工程85acfd5来源E2E_BUILD01成功，wall17.12737691100483/CPU23.727903；1a5b811冻结E2E01，原RRT_PCS环境II、seed7、原采样盒与恒true callback、range2.6/goalBias.05、10s单次solve实测exact非approx，solve段.016837364s，整次wall.2776374349996331/CPU.19540999999999997。4里程点、6树节点/5树边、3段原成功回溯，连接角色/branch依次(0,3)→(1,3)→(0,0)，有2次真实角色切换。使用A01 RECONSTRUCTED端点和R2几何一致数值，原始端点及native失败保留，不能冒充原作者原输入直接通过。

b4cbbff冻结完整路径后审PATH01：177/177原密集节点、176叶全部通过独立闭链、原机械限位、每边被动branch及v3对齐原离散碰撞策略，最大闭链位置3.410605131648481e-13mm、旋转4.440892098500626e-16；叶距max.04949053472601928<.05。实际354数学FK、354分支、177collision、708adapter内部FK/J、41064PQP；wall40.94035644100222/CPU1.1020530000000002。原source执行仍保留PENDING历史，独立后审新文件单独给PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH，不改写旧execution。

18execution=16science+2engineering，R2总wall343.63343315300244/CPU289.461446，余3256.3665668469976/6910.538554；VI B974/974余0，正式Table I0/22500不变。最新211项新表保前73历史列，另8列本路径实证。新V5保全审查PASS：1028旧科学文件、57崩溃文件8482891bytes、tar57成员、另5工作树及13未提交文件、旧V4均保持。

原导出随机IKproject/sample_q缺陷不在真实RRT调用链；CBiRRT activeDistance同点非零缺陷尚待版本化修复；原PQP638个BeginModel警告及原统计时间域差异保留。路径资格仅原离散策略，不保证CCD、完整实体杆件/省略碰撞对，也不证明PCS性能优势或完整论文。随后普通NR C++逐式移植/trace等价资格，与RSS解耦；大规模正式实验仍须端到端资格后成本pilot另审。全部原文211项义务保持，不P2/Isaac。详见reports/P4_FULL_R2_ABB_RRT_PCS_PATH_POST_TASK_20261015.md、最新ABB_RRT_PCS覆盖表及V5账本。


## 2026-10-15 — ABB NR固定64移植资格实际通过

c68fa76冻结后的唯一Q1执行完成：II32+III32、C++plain64/trace64/原Python64共192派发与192完成，64跨语言、64历史重放、64独立终态全部通过。q最大差4.440892098500626e-16rad；终态最大位置8.342067303601652e-7mm、旋转矩阵1.50461743064767e-9，原1e-5门不变。Python原NR内部864/864 armFKJ，独立终态128/128；C++内部started/completed仍UNOBSERVED。actual7.05127794699365wall/7.9173490000000015CPU。详细源码、命令、版本和差异见reports/P4_FULL_R2_NR_ABB_Q1_POST_TASK_20261015.md；独立保存证据审查另存，不借0exit或同失败证明能力。

20execution=17科学+3工程保守总359.4902552519934wall/309.65925300000004CPU，旧V5保持，新V6逐own实耗一次。资格标签仅PASS_FIXED64_NUMERICAL_TRANSFER / RECONSTRUCTED_PHYSICAL_FULL_NR_CPP，不是作者KDL轨迹/公平速度或全随机空间投影能力。下一步原GD薄接缝、原NR非平凡RBS/回溯和原RRT入口，先独立PRE/版本/预算冻结；源sample_q未达调用链问题不捆修。VI974余0、正式0/22500、全部211义务不缩。原失败保持，不P2/Isaac。


## 2026-10-16 — 普通NR原GD/SVC/RBS固定局部资格通过，真实规划仍待

7ee551a冻结后LOCAL01唯一执行20/20顶层（4端点+3边RBS/回溯各plain/trace）、10逻辑对binary64和非计时计数一致；3/3非平凡原RBS与完整原回溯通过。147/147全唯一节点/全部来源ref经独立闭链、原3.1416机械界、v3 aligned离散源碰撞合格；max位置9.887878832159913e-6mm/旋转2.5558390071012127e-8，在原1e-5门内，三路径65/65/17节点、最大叶距.04769340858982442<.05。traceGD286/原PQP33150；数学逐臂FK/J294、adapterFK/J588、collision147、native/aligned共34052PQP均实际观测；plain内部UNOBSERVED。原nativeTCP不一致147节点保留，非换门改判。标签RECONSTRUCTED physical full NR +原SVC/RBS控制流，非原KDL轨迹或论文速度。

actual3.6995257820017287wall/4.245554CPU；新工程22.57619615099975wall/31.233423CPU为独立build-only。22execution=18科学+4工程，保守R2累计385.7659771849949wall/345.13823CPU，原3600/7200帽保持。VI974/974余0、正式TableI0/22500和211项全部义务保持。新V7账及完整对照表继承前90列211行逐值不变，新增8列；原V6不改。

runner作者另写保存审计117258/117258（personnel_independent=false），第二代理独立事件树/矩阵算术/资产审计218766/218766及raw-link补审666/666通过，0新科学。大JSON原字节本地保留，确定性无损gzip与SHA manifest入Git；不删除或重跑原失败。详见reports/P4_FULL_R2_ABB_NR_LOCAL_POST_TASK_20261015.md、两份POST与RAW_LINK_ADDENDUM、reports/P4_FULL_R2_ABB_NR_LOCAL_SAVED_POST_ARCHIVE_20261016.json。

环境II下一有限planner门已通过，但尚无NR起终点路径：下一项另冻原RRT_NR单target工程45/90、II seed7单次10s solve外帽30/60、完整独立路径另120/240/max2048，不自动连跑、不调seed/门限/端点。PCS随机三参helper H与CBiRRT距离D仍独立草案未运行；RSS原RBS/分布/入口解耦诊断且不追加VI构造。正式大规模成本pilot需相关端到端资格后安排并向用户报预算，不缩完整原文统计、不P2/Isaac。


## 2026-10-16 — 原 RRT_NR 首条完整空间起终点路径已独立合格

II seed7 的唯一原 RRT_NR solve 得到 exact 非 approximate、7 milestone、55树节点/54树边，6次原完整回溯均true。原source execution的PENDING历史保持；单独完整PATH01检查393/393唯一节点和392叶，通过数学闭链、原机械界和v3 aligned原离散碰撞。最大位置9.793997321594361e-6mm、旋转矩阵3.0701365727470176e-8，最大叶距.0478001489336342<.05rad；最小原界余量.046633132713711944rad。实际数学臂FK/J786、adapter内部1572、collision393、PQP91176（双worker各45588）；原native TCP不一致393记录完整保留。

工程28.08202379599993wall/34.574132999999996CPU；solve执行1.7845762399997511wall/1.7793930000000007CPU；完整path3.7730926529998214wall/3.9572699999999985CPU。V8按25 execution=20科学+5工程逐自身成本一次，累计419.4056698739944wall/385.449026CPU；原3600/7200帽保持。保存算术后审36348/36348（作者兼runner，人员独立=false），另代理人员独立24448/24448全部通过，0新科学/编译。V8保全通过：1028旧科学文件、57崩溃文件及tar、另5worktree/13未提交文件、旧V7和211行前98列均保持；新表另8列证据，不删原义务。

本路径使用A01 RECONSTRUCTED端点与重建physical full NR接缝，不能冒充作者原输入/KDL轨迹或公平速度。仅原离散source policy，非CCD、完整实体/省略pair安全、成功率/方法胜负或完整论文。详见reports/P4_FULL_R2_ABB_RRT_NR_PATH_POST_TASK_20261016.md、两份保存POST、V8账和NR_RRT_PATH完整对照表。VI974/974余额0，正式TableI0/22500与全部原文统计规模保持。

下一项随机三参helper H的缺break返回修复单独冻结有限资格；H不在已合格RRT实际grow调用链。CBiRRT距离D、其他搜索器/环境、RSS原RBS/分布/入口依次诊断；新科学设计/新增VI/正式大预算另审。相关端到端资格后做可重复成本pilot，不提前正式大规模，不P2/Isaac/结题Word/PDF。


## 2026-10-16 — H真实随机三参返回修补：控制流完成、完整终态门墙钟停止

d53a68c固定16context×2控制流×plain/trace共64真实helper全部正常返回；32binary64模式对、16首次成功prefix全部通过，原32false、成功break32true，主动角不变。H不在原三planner真实grow调用链，不据此宣称规划提升。工程2target各exit0，actual24.520090279000215wall/33.067454999999995CPU；工程283/283保存审查通过。原builder/PRE保持；science preflight漏计新工程被26prior断言拦截，未建科学claim前最小修science_prior，修前字节和诊断保留。

独立终态仅34/64完整通过（原false32+修true2）。第35数学门已完，native/aligned两raw worker已返；adapter在总60wall帽处捕获Timeout，aligned内部第140FK/J未完成，实际139/139，仅native变体入adapter结果；不能将raw拼成完整资格。两个partial JSON可解析，原stopped_partial保存二次timer诊断保留。原STOP_CLEANUP_OR_EVIDENCE_ERROR及IDs34..63的30条UNKNOWN不改，不重跑helper/原claim、不自动放宽帽。实耗60.50938905899966wall/39.185680000000005CPU含收尾全扣R2。

人员独立saved后审12622/12622通过仅支持STOP前缀证据一致；原V1报告MD纯展示TypeError另存后V2重审，0科学。64输出19个env+q12字节键，完整34覆盖12键，另7键先查历史精确证据；不以近似角/source true替代物理门。原native TCP mismatch34单列。真实35数学门/70数学臂FK/70geometry、35adapter（1error）/70worker/139adapterFKJ，完整门PQP各3736而全部raw各4060，统计层级不混；plain内部与rand真实计数UNOBSERVED。

V9共27execution=21科学+6工程，自身成本一次累计504.43514921199426wall/457.702161CPU，原3600/7200帽余3095.5648507880057/6742.297839。V9保全PASS，旧1028科学文件、57崩溃文件及tar、另5worktree/13未提交、V8和211行前106列均保持；新表另8列H证据。VI974/974余0，正式0/22500和全部原文统计规模保持。详见reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_POST_TASK_20261016.md、ROOT_INDEPENDENT_POST及V2、V9和HELPER_H完整对照表。

继续原IV wrist-only固定100/800数学组件与其他原RBS/分布/入口资格；CBiRRT距离D独立因子先静态冻结。H必要的后续外门先据现有成本和精确去重另冻，原64资格STOP不改。正式大规模仍待相关端到端资格及成本pilot预算申请，不P2/Isaac，不提前结题Word/PDF。
