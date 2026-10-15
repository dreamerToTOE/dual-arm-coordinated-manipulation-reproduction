# Execution Governance — Scientific Progress Over Engineering Loops

This document defines how coding agents decide **what is worth fixing now**.

## 1. The central rule
Every task must answer one scientific/benchmark question.

Do not optimize a diagnostic subsystem beyond what is required to answer that question.

The task specification must therefore separate:
- **Scientific objective**
- **Minimum sufficient evidence**
- **Non-goals**
- **Preferred method**
- **Fallback method**
- **Attempt budget**
- **Stop/escalation condition**
- **Deferred issues**

## 2. Blocker taxonomy

### TASK-BLOCKING
Without resolving it, the task's required scientific conclusion is invalid or unavailable.

### DEFERRED
Real issue, but explicitly owned by a later task.

### KNOWN LIMITATION
Uncertainty remains, but the current claim can be stated honestly with that limitation.

### LEGACY
Belongs to historical application/demo code and is not part of the current benchmark.

Only TASK-BLOCKING issues justify extending the current task by default.

## 3. Default engineering attempt budget
For one root blocker:
- Attempt 1: diagnose.
- Attempt 2: implement the most evidence-supported fix.
- Attempt 3: use a bounded fallback or alternative measurement route.

If still unresolved: stop and escalate.

Do not automatically create serial variants such as probe04/probe05/probe06 without a new user-approved reason.

## 4. Escalation decision
After the attempt budget is exhausted, answer:

1. What scientific statement were we trying to establish?
2. What has already been established?
3. What remains uncertain?
4. Does that uncertainty invalidate the task?
5. Is there a lower-cost evidence route?
6. Should the issue be deferred or accepted as a limitation?

The coding agent must recommend one of:
- **CONTINUE** — truly task-blocking and worth another approved attempt.
- **FALLBACK** — use another acceptable evidence method.
- **DEFER** — assign to a later task/bug owner.
- **ACCEPT LIMITATION** — record and proceed.
- **STOP FOR USER** — benchmark/theory decision required.

## 5. Evidence tiers
Use the lowest tier that is sufficient.

### Tier 1 — Sanity evidence
Enough to reject obvious model/interface errors.

### Tier 2 — Task acceptance evidence
Reproducible evidence sufficient for the task's PASS criteria.

### Tier 3 — Research-grade comparison evidence
Repeated, logged, fair evidence needed for a paper table/claim.

### Tier 4 — Subsystem equivalence / exhaustive proof
Only pursue if the research question explicitly requires it.

A TASK01 benchmark setup usually needs Tier 2, not Tier 4.

## 6. Examples for this repository

### TASK01 collision-model difference
Scientific requirement:
critical benchmark states must not show unexpected collision in the final Isaac environment.

Acceptable evidence:
targeted critical-state sanity/replay plus recorded model discrepancy.

Not automatically required:
proving exact equivalence of FCL STL and PhysX cooked convex hulls or perfect zero-step query-cache semantics.

### TASK10-IS force/wrench
Scientific requirement:
validated wrench semantics for P2's internal-force claims.

This **is** task-blocking for P2 Isaac evaluation, but it is DEFERRED for TASK01/P4.

### Legacy five-Cube Task27
Useful application/stress-test evidence, but LEGACY with respect to the one-Cube scientific benchmark.

## 7. Task writing rule
When creating or revising a task, use `docs/tasks/TASK_TEMPLATE.md`.
Technical details belong under Preferred Method; do not accidentally promote them into Requirements.

## 8. Progress review trigger
A task requires a governance review when any of the following occurs:
- same root blocker reaches three implementation iterations;
- task duration/commit count grows without new scientific evidence;
- new subsystem is added;
- acceptance criteria keep expanding;
- agent proposes a fourth probe/version for the same root issue;
- a later-task issue begins blocking the current task.

At that point, update STATUS with a short scope review before further coding.


## 2026-10-15 — R2用户批准974上限及固定64点组合离散资格实测

用户明确批准原剩50加新增14，VI B总上限960→974；单项30wall/60CPU及累计180wall/360CPU保持，无正式规划预算。批准原文逐字保存于configs/p4_full/r2_vi_rss_ingress_composite_user_approval_20261015.json，源码/协议冻结243fa05。固定清单、原解析支、δ=.01、h=.0025、γ=.2未变，不换点或加深；原Q2 UNKNOWN、原center、六fiber及所有失败保留。

单次INGRESS_COMPOSITE01实际64/64节点及四条regular↔fiber接入离散门通过，PASS_RECONSTRUCTED_COMPOSITE_DISCRETE_ONLY。96条regular叶和6条保存fiber叶均严格<h；四半regular最大叶距分别.001726025161094/.001850849712175/.001488951615670/.001491095303782rad。数学FK/J704、adapter内部192（合896）、IK1024、源碰撞64；实际wall14.198019690000/CPU10.876665。此为明确标记的独立重建组合，不是原作者RSS/RBS忠实实现证明、连续无碰撞或全局RSS规划成功。

VI B累计974构造，余额0；累计wall68.712002153999/CPU24.203842，余111.287997846001wall/335.796158CPU。13run自身消耗逐份计入R2总账，合wall109.563377079999/CPU55.934698，余3490.436622920001/7144.065302。不得使用旧快照余50再次构造，不重置claim。新账本results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V3.json，旧9/12run账本不改。

最新211项对照reports/P4_FULL_R2_INGRESS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md保存全部历史列，另列本次组合资格；13run报告P4_FULL_R2_VI_RSS_INGRESS_POST_TASK_20261015.md及独立POST审查。正式Table I仍0/22500，500000配对投影、约50000合法点对、全部Fig.3–5/Table I–II及消融义务不缩。继续II/III普通PCS固定branch/RBS/回溯与三搜索器链接资格，先冻结版本/原返回对照/预算，0solve；工程成本另列并保守扣R2总帽，不扣已耗尽的VI候选账。P4仍部分完成，不P2/Isaac，不提前结题。


## 2026-10-15 — R2 ABB PCS原固定局部接口：10通过/6拒绝，整体部分完成

工程aa57c24冻结四目标source-native/R2 numerics×plain/trace，全部构建exit0，三PCS搜索器仅链接，实际wall94.592335203997/CPU130.109068；232产物/source/claim/recipe/commit绑定经独立复核。科学95851e0冻结后单次LOCAL01，无超时/异常，actual wall81.132350082000/CPU78.392314。320顶层project，20RBS，20回溯（180plain/trace逻辑对）；442trace固定branch投影、364成功输出独立复验，752数学FK、368碰撞/1472adapter内部FKJ，78252adapter及29618源内部PQP查询，非上限填充。

R2数值10/16固定局部边通过非阈值提前返回的真实RBS/回溯、闭链、原branch/限位及source aligned离散碰撞；6拒绝分5源投影false+1碰撞，保存目标必要代数门独立确认3几何workspace拒绝、2原q3下界拒绝，未新FK/IK，不能称全部几何不可达。II start主动arm2、II goal主动arm1缺本固定h正例，整体FIXED_LOCAL_ABB_PCS_PARTIAL。作者原数值16局部端点全拒绝，原失败留存；未换h/中心/分支重试。44个下游模板依预置gate未执行，不是超时丢尾；三个planner solve/RNG0，不推出全局PCS或优势。

新15execution为14science+1新engineering，逐自身实耗保守计R2合wall285.288062365996/CPU264.436080，余3314.711937634004/6935.563920；工程不当science成功，VI B仍974/974余0。新账V4保V3及旧12/9run原字节，新ABB_PCS完整211表保前68历史列，正式TableI仍0/22500及全部原分母不缩。继续固定失败根因、IV100×8原wrist数学资格及其余环境/方法门，先独立冻结预算、无正式规划/P2/Isaac。实际记录results/p4_full/20261015_R2_ABB_PCS_LOCAL01/execution.json；审查reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_20261015.md。
