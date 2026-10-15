# P4 R2 原RRT首条空间路径：driver/observer/builder/path审查（静态第一版）

2026-10-15。状态：**草案存在需修正项，尚未冻结可执行**。仅读取源码、AST解析Python及保存数组/字符串算术；0编译、0科学、0claim、0FK/IK/碰撞/solve。源码可能由其他代理继续修改，本审查仅对应以下SHA；修正后必须以新SHA复核。

## 已通过的静态证据

1. 新builder复制现已绑定geometry_consistent_plain到新stage，旧四binary/source/mesh只读核hash；新目标只链接原RRT，未调用CBiRRT已知bug；build与science有独立claim，既存输出不覆盖。工程固定45wall/90CPU、live process group CPU与alarm，失败stage/stdout/stderr保存，工程科学分账。
2. state-level reconstructRBS完整body放于返回bool的lambda，hook仅在原返回后读s1/s2/role/branch/Confs/returned；没有额外FK/IK、没有修改原return。原body在构造后恰保留一次，保存body SHA为`fb3ac4578539a7e5a98a60ea4ab2b4663f6b7e56ba1be75d44460dad04df6915`。三参数随机IKproject/sample_q不达原RRT，不修、不当门。
3. observer用O_EXCL新建和循环write，完成的每次reconstruct都写JSONL；false与其部分Confs保留，调用方随后清M也不会覆盖已存row。nlohmann JSON输出binary64往返精度，milestones同样从内存取double，不从约6有效数字原paths读回。原paths及temp低精度文件另留原字节；retain(temp)仅I/O偏差。
4. driver保存原PlannerStatus code/string、pdef exact/approx/has_solution/difference、全milestone和PlannerData树。不能仅以status bool判exact。原save2file遇重建false仍可能让solve随后报exact，path runner materialize要求每对连续milestones存在returned=true且qa/qb一致、Confs完整且首尾完全相等的重建；缺任何边会拒绝，不能以source exact直接PASS。
5. path runner每个精确unique binary64节点查独立闭链、原physical全界、每实际重建边passive几何branch；保存所有edge引用、严格full12 L2<.05叶；每节点查v3 native/aligned离散碰撞并保留碰撞/数学拒绝，不重投影、平滑或补IK。closure1e−5mm/rotation1e−5未放宽。

## 冻结前必须修正或明确的事项

**S1，原采样盒与callback。** 当前driver第52–74及builder science_draft用机械角度×3.1416/180作OMPL盒并q6±400°，而原run/plan_PCS.cpp是截断采样盒q6±3.1416、callback恒true；PRE误称其已授权。必须改回原run原盒和恒true，physical全界留外部path门。不能将它作为无须说明的原生参数。当前range2也须改原envII 2.6；此前2为root默认，不是用户指定。
**S2，实际identity入口证据。** 当前observer只有reconstruction，无原identify调用日志。按本次parent要求可用只读post-return wrapper记录原identify的q、输入ik及返回ik；若包装vector重载，须在body前仅拷贝输入ik，在body后写记录，不额外计算8根/IK/FK。实际未执行候选不补造。若完整原树branch标签未导出，要明确PlannerData没有两ik，不能声称树标签已保存；完整重建路径branch仍可由原重建role/branch独立验。
**S3，有限path工作量。** 当前path draft把最大FK/collision从运行后N派生，没有预冻N绝对帽。建议预冻N≤2048 unique节点，超过则保存完整路径并标资格未完成/UNKNOWN，不能抽稀或挑prefix PASS；2N数学FK、N逻辑collision、4N adapter内部FK/J、≤232N PQP为最坏界，实际各逐调用计，不用帽填完成数。最终根代理可在冻结前据原预算选更紧N。
**S4，调用计数与未返回。** 当前reconstruct JSONL仅completed记录，无入口事件；hardkill会遗留未返回调用但无result.json。建议新增started/completed索引或明确started=UNOBSERVED，父运行器必须独立保存process_started/exit/signal、stdout/stderr和缺result状态，不从completed反推started。内部native FK/IK、projection与source PQP当前无hook，若不加守卫则计UNOBSERVED；只依硬30wall/60CPU总源进程帽，不声称它们在旧固定local64等帽内。识别/RBS普通false不可改造成预算异常或丢弃。
**S5，path启动与日志保全。** path runner在try之前创建RunBudget、导入模块、open events和装hook；若这些步骤异常/预算初始化失败，可能claim和目录已建但没有execution。应将领取claim后初始化纳入同一finally，预算不足在claim前读余量拒绝，初始化失败仍零/部分成本记账。math_arm_FK_started现一次加2后再依次调用，第一臂抛错时会误记第二臂started；逐臂计requested/started/completed，未观察internal started不倒填。
**S6，来源关联。** source result、源执行execution/claim、冻结request和build manifest/hash必须连成链；path草案目前只hash result和所有prior execution，未显式验证result.request与固定seed7/envII/range2.6/10s、A01原数组、源运行binary/hash。根代理source runner可承担该验证，但最终协议/POST应指向具体链；不能给任意形似JSON的文件以“作者原solve”资格。

## 本次新增运行许可范围的解释

不要求把所有原随机树节点都先验数学通过才准有界solve，也不要求为潜在近周期风险新增8支重算。保存LOCAL01表显示II start预期ik[3,0]、goal[0,3]，8支中唯一<.1，不存在当前起终点的周期漏识/多命中反例。真实path逐节点独立分支门足够否决不可信返回。
CBiRRT activeDistance active1同点非零反例及原三searcher可达图见P4_FULL_R2_ABB_PCS_REACHABLE_GROW_PRE_DRAFT_20261015.md；不因不达RRT的缺陷停止RRT。审查不得变成正式performance前的无穷辅助资格。
固定一次seed7原envII range2.6、10s是有限pilot，solve+path的实际成本从原R2扣，正式22500/500000/约50000义务不变；0新VI候选，不进P2/Isaac。

## 被审文件SHA256

|文件|SHA256|
|---|---|
|`baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_driver.cpp`|`eeb5e4bce07ef6e7f466086374b6b304258684c110dc7cb9b8048fdeb16c2478`|
|`baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_observation.hpp`|`b597b56199279bd02a7030375e0dd055d650c9a0bb4bee80aef6d4242755381c`|
|`scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py`|`a76c67a53690a9e04dcb6fdb087bc65595192d09f69675667ab4ff271d8506e7`|
|`scripts/qualify_p4_full_r2_abb_rrt_path.py`|`2f59a2acf59f2e7d7095fcc49a1779a530198889bb0af2d5ac2d105dea27c81c`|
|`reports/P4_FULL_R2_ABB_RRT_PCS_END_TO_END_PRE_DRAFT_20261015.md`|`d6712e383426f38132b1d63c4bff0cc0819fa102648ea8e558d497eb898c912b`|

本审查不修改上述代码，不调用describe/validate可能触发的模块构造，不进行编译或真实规划；只更新本独立报告及对应reachable PRE。
