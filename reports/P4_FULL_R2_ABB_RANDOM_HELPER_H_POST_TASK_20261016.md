# H 固定64真实三参接口：控制流通过，完整终态资格超时

2026-10-16。源码冻结 `d53a68c`，唯一命令 `python3 scripts/qualify_p4_full_r2_abb_random_helper_h_draft.py --protocol configs/p4_full/r2_abb_random_helper_h_qualification_v2.json`。原16个A01上下文（II/III起终点×主动角色0/1×seed7/17）在两控制流×plain/trace中共64次真实原三参helper，均正常完成。保留全部输入、原始响应、8个持久进程stdout/stderr、源内部候选和完整EOF；32对plain/trace含signed-zero binary64相等，16对原/修补首次双身份成功前缀相等。

原控制流32次均返回false且完整尝试8支；仅插入成功break的版本32次均返回true，16个trace上下文分别在4/4/1/1/1/1/4/4/4/4/4/4/3/2/4/4次尝试后结束。全部主动角原位保持。该证据确认缺break的原函数返回缺陷及本固定输入的最小修补效果，不是随机空间成功率或规划器能力；H不在原三planner的真实grow调用链，已合格PCS/NR RRT路径不据此改判。

独立终态门完整完成34/64，34均通过闭链、原界、独立几何branch关系与v3 aligned离散源碰撞，其中32个为原控制流false输出、2个为修补true输出。第35个数学门完成；其native和aligned worker各自原始响应已保存，但第140个adapter内FK/J未完整发生（实际139/139），adapter记录 `COLLISION_ADAPTER_ERROR`、error=`TimeoutError('H_AGGREGATE_HARD_WALL_CAP')`，不能据两份worker返回认定完整adapter资格。对应collision JSON和stopped_partial JSON均完整可解析；后者保存过程又受timer触发产生诊断，原字节/诊断均保留。

原执行状态为 `STOP_CLEANUP_OR_EVIDENCE_ERROR`，主终止原因为60秒墙钟帽，实际含收尾60.50938905899966秒墙钟/39.185680000000005秒CPU。没有因已有34个正例把整项改判通过，未完成final IDs34…63的30项保持原UNKNOWN；不自动重放helper或重开原claim。该次实耗全部扣R2，不用60秒上限替代实际成本。

实际分层计数：64helper、35数学终态、70数学逐臂FK、70几何branch、35adapter返回（含1 error）、70原worker返回、139adapter内部逐臂FK/J。完整34门累计PQP native/aligned各3736；全部70worker raw另外证明各4060条query code，二者统计层级分别保留。trace半数32helper实际329 native FK、1393 native IK、76 identify、177 branch进入，均有匹配完成；plain内部和rand真实计数仍UNOBSERVED，不由trace倍增或用448结构上界冒充观测。

人员独立saved-only审查12622/12622通过，0新模型/编译，结论为原STOP前缀证据一致；不升级完整资格。34完整native TCP mismatch继续保留，aligned结果单列。保存原始矩阵、响应、branch标记、完整raw尾、计数和资产SHA均可复核。见 `P4_FULL_R2_ABB_RANDOM_HELPER_H_ROOT_INDEPENDENT_POST_20261016.json` 及后续只读审查；JSON已保存后的报告MD展示异常与其修正另存，不触及科学结果。

只读按环境和全12角binary64分组得到19个输出键，34完整终态覆盖12键。尚未覆盖7键，固定原dispatch分组为[34,50]、[36,52]、[38,39,54,55]、[40,41,56,57]、[42,43,58,59]、[44,45,60,61]、[46,47,62,63]。对已有精确相同状态可引用保存证据；不能以近似角、同seed或source true替代独立资格，也不改变原64请求或原UNKNOWN。后续应先核历史精确证据和成本，再冻结必要的独立终态门，避免重复helper或重做已合格状态。

V9共27 execution=21科学+6工程，自身实耗各计一次累计504.43514921199426秒墙钟/457.702161秒CPU；R2原3600/7200帽余3095.5648507880057/6742.297839秒。VI974/974余0，正式TableI0/22500，211项与全部原统计规模保持；最新表在前106列历史上新增8列H实证。本项不混CBiRRT距离D；继续其他原环境/方法/规划入口资格，相关端到端合格后再成本pilot与正式预算申请。不P2/Isaac，不提前结题。
