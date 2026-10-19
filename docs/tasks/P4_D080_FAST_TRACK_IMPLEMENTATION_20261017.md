# P4 D080：Codex 下一阶段执行任务书（2026-10-17）

> **D081执行覆盖（2026-10-18）**：本任务书中所有“正式18,000次运行、36×500、为其专设cost pilot和正式规模预算审批”的未来执行指令已经由用户取消。保留原论文原分母、D080批准历史和已有失败/结果，不再执行18k。继续真实数值仿真实验、可重复的代表性算法对照、Fig.3–5/Table I–II趋势与PCS消融；详情[最新决策](../decisions/D081_P4_CANCEL_18000_NUMERICAL_REPRODUCTION_20261018.md)。旧段落仅供历史溯源，和本条矛盾时以上述新决策为准。

**先读** `docs/decisions/D080_P4_RELEVANCE_SCOPE_ACCELERATION_20261017.md`，其D080范围高于旧D079“全部六环境”要求；其他证据/质量门沿用D079。工作分支 `p4-full-reproduction-pcs-study`，不新建分支。不得自动进入P2、Isaac/FR3应用。

## 接管与首个检查点（先做，不要重跑）

1. `git status` / HEAD / 远程状态；保全全部脏文件、在跑进程和旧科学记录，合并新增D080指令不要覆盖已有工作树。首次接管基线GitHub `ff25dc6`，若分支已有后续提交以**实际最新状态**为准。
2. 阅读 D080决策、`CODEX_START_HERE.md`、`AGENTS.md`、D079全文根因规范、六环境原审计、原论文PDF及本地作者源码；只读核对最近实验的独立审查证书、V24以后实际账本与未提交SBL setup结果。不得根据陈旧报告误把setup当完成。
3. **生成D080独立211行覆盖表**：从最新原始完整矩阵程序化继承，旧列全部保持；新增范围标志（I–V in scope、VI archived outside approved scope、跨VI条目部分范围）、原文分母、D080批准分母、状态与证据来源。提供MD/CSV、行数校验、差异统计、SHA、明确固定原分母：Table I原22500，D080批准18000，差额VI原4500；不得错误地填成9000或省略原分母。旧表不覆盖。
4. 报告：I–V各场景的各个规划器/方法是否已有端到端路径、连续碰撞是否验证、当前科学失败及预算。若SBL setup正在运行，先按原授权安全完成及保全，不启动重复实例。

## 执行主线（可开发并行、但每项科学执行都需遵已批准协议和预算）

### A：结束ABB已有端到端覆盖，进入有用困难环境

- 环境II既有RRT_PCS(177)、RRT_NR(393)、CBiRRT_PCS(413)、CBiRRT_NR(689)的独立离散source-policy路径都做只读复用；**不能重新做这四个成功证书作为推进量**。
- 按最新保存进度继续SBL_PCS的真实setup → SBL原生local → 一次原生solve → 完整原路径独立验证；包括作者默认projection、lazy删除/地址代际、connect未初始化a_chain、原RBS虚假early-return等实现边界，不能把构建/setup当路径资格；先检查保存证据不重跑。
- SBL_NR、BiRRT其他方法与ABB其余机制按原论文计划继续。已在R2证明的完整路径只证明离散原source-policy，单独保留native TCP mismatch、重建端点、未证CCD。

### B：优先环境V，紧接III和IV；II作为对照基线

- V（双吸盘搬箱）先做原native/reconstructed起终点、吸盘抓持、手爪TCP/物体姿态、一致的碰撞pair资格；前期V RSS旧8根aligned全部collision且pair根因未定，不能忽略；PCS/NR合格独立于RSS该阻塞。
- III（窄通道）必须证明存在路径及算法差异；保留真实障碍、限位、碰撞与换链见证，不能用II成功替代III。
- IV（多障碍）保留原Comau几何与腕限位，已审fixed100/800数学证据只读复用；不能把数学6正例升为RSS全局成功。
- 环境I平面原Fig3、m变量与投影机制恢复为独立低资源统计线；不能拿它冒充空间环境或FR3结果。

### C：RSS独立阻塞线

- II–V的RSS仍是**IN_SCOPE**，必须做作者源身份映射（实际奇异模式/概率/分支/原RBS提前返回/连续路径资格），优先复用已保存合法数学根和旧碰撞结果。
- 明确证据：II/III mode0固定输入失败不证明数学整体无解，IV固定100/800数学6根不等于正式规划，V旧8根碰撞拒绝，VI实际候选预算974/974，D080范围外且不追加。
- 三轮同根因没有科研结论则停止该阻塞盲目修补，提交有依据的OUR_IMPLEMENTATION / AUTHOR_RESOURCE_GAP / METHOD_ISSUE_SUSPECTED / UNKNOWN等独立证据、修复方向或不可复现解释，请示科学新设计和预算。RSS难点不能阻止PCS/NR与实验自动化的研发。

### D：性能实验流水线，不直接开大规模

- 统一`env × planner × projection × seed`配置和真实来源标签；每个正式请求最多1000s，正式18,000分母受预算审批；以原每组合500次为目标。
- 准备“少量、分层、预声明”的cost pilot，用于测RRT/CBiRRT/SBL×PCS/NR/RSS中最快/慢和超时组合；pilot数据另记，不能混入正式统计。测算法solve秒、路径独立验证秒、I/O秒、完整CPU/墙钟/内存；提出可实施并发上限、内存模型、有效CPU隔离、失败恢复与数据格式。
- 公平性：保持方法统一原始模型、原始参数及单独调优定义；不同算法按配对seed/交错运行，计时不混编译/审查/日志写入；限制同机进程争抢；需要GPU/云服务器时先量化预算和平台差异。
- 按原文实现Fig3–5、TableII、APC/NR 500000投影、约50000可见性点对、PCS full vs fixed被动链、无障碍/有障碍消融，所有实验真实统计；受VI影响的论文泛化条目诚实标记“D080未复现”。

### E：科研证据与文档提速，不缩水

- 批量生成日志、hash、分析和对照表，统一一项科研里程碑的PRE/RUN/POST/独立审查；复用内容哈希不变的历史审查证书；检查预算及源签名无漂移。避免因纯日志/排版问题多轮重复跑科学样本。
- 独立物理验证每条关键路径仍需保留，明确多层验收：源exact→离散数学闭链/限位→原raw collision与aligned variant→加密采样/连续碰撞（若另行实现）→正式算法比较。
- 用户汇报里不能用“PASS 41787/41787”代替规划算法统计成功率。一次单seed完整路径资格只是一条机制见证。

## 里程碑与审批

- **M0（尽快）**：D080范围转换、最新工作区核验、211行新矩阵、18k实验运行清单、计算成本pilot协议草案，报告用户。
- **M1**：SBL在II真正完成原生规划资格，II相关九组合中已打通的组合与尚未打通的差距清晰列出。
- **M2**：V、III、IV至少各有PCS或NR成功端到端资格及对应失败记录；RSS单独诊断有实证的源缺口，不拖延其它实验。
- **M3**：cost pilot真实数据、资源需求、18k正式实验启动申请；**未经用户批准不得启动正式18k**。
- **M4**：授权后完成正式实验与Fig3–5/TableII/消融、同条件统计/不确定性和完整的教师报告；最终只在用户接受后关闭P4、转P2。

**预计目标**14–21天完成本篇 *D080重点环境复现*，以真实pilot/失败为准调整，不为赶工删II–V或RSS。每天末尾或每个科学里程碑给一个中文简短进度（本日新增可复核科研结果 / 尚未通过 / 今日耗时与剩余 / 下一步）；普通已批工程任务可连续进行，不必每个静态审查停机；涉及新科学假设、正式预算或范围改变必须暂停取得明确批准。


## 2026-10-18 D080：V固定24节点独立诊断完成 / V34

原24保存节点唯一执行，闭链/branch/原限位24全过，aligned source-policy15clear/9collision拒绝，最大闭链位置1.4779288903810084e-12mm。native24TCP mismatch保留；人员独立保存430/430只证固定诊断/费用，local/path/CCD仍false，原三公有RBS/回溯false不改判。原17 source TCP/box/pair保存交叉核单列待验，不冒称adapter未保存的逐pair独立closer重算。见reports/P4_D080_ENV_V_PCS_PHYSICAL01_STAGE_POST_20261018.md。

费用9.466394254997576wall/3.7087890000000003CPU一次入V34，52execution=38science14engineering，charged1113.4602605769917wall/927.6919419999999CPU，原总3600/7200保持，历史尾UNKNOWN。211×232保前228列；source solve6/本次0，正式0/18000、VI974永久只读、II五路径复用。下一V保存对照/原RRT薄工程及III .8工程，RSS解耦；不新假设/放宽判据/正式大统计/P2/Isaac/FR3。


### V PHYSICAL01后续保存补证

原source17点的TCP/箱体/87pair/API/8mm聚合保存核对634项及独立薄审8项通过：17点14clear3reject，另7project-only点1clear6reject；独立逐pair closer未保存，UNKNOWN保持。无新模型/入账，原主POST PENDING不回写。见reports/P4_D080_ENV_V_PCS_PHYSICAL01_SOURCE_SAVED_ADDENDUM_20261018.md。V下一最早门为原RRT薄工程/有限入口，III .8工程并行。


## 2026-10-18 D080：III原RRT_PCS薄工程独立通过 / V35

freeze77d37499唯一32copy/5TU1link完成，6compiler exit0/reap/空组、5原MD/672实际依赖、17原log/dependency逐字归档。独立保存49/49，ELF81dac2e2、execution16696c0d，仅BUILT_NOT_QUERIED，binary/setup/source solve/路径均未执行。费用22.0565060610004wall/34.199148CPU一次入V35；53execution=38science15eng，charged1135.516766637992wall/961.89109CPU，原3600/7200及历史尾UNKNOWN保持。211×236保前232列，source solve6/新增0、正式0/18000、VI974只读、II五路径复用。见reports/P4_D080_ENV_III_RRT_PCS_BUILD01_STAGE_POST_20261018.md。

下一V原RRT薄2TU/link未冻结；III单次10秒source入口30/60草案准备，须独审冻结后唯一运行并另作全路径门；RSS fixed4×8工程刷新不改原科学或γ、不采新样本。无P2/Isaac/FR3/正式统计/结题。


最新V35后续精确恢复点：`reports/P4_D080_V35_CONTINUATION_FRONTIER_20261018.md`。V薄工程20项独审、RSS刷新仅自审30项均不可执行；III SOURCE01仅未审初稿/配对协议未齐，无新solve，不冒称端到端通过。
