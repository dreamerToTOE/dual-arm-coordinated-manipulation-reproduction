# L12 v2：分次距离接口证据的前置契约草案

2026-10-16。**PREREQUISITE_CONTRACT_DRAFT_ONLY / NOT_FROZEN / NOT_IMPLEMENTED / NO_EXECUTION_AUTHORIZATION**。

本草案只说明未来 L12 v2 如何严格接收一个经过独立审查的分次距离接口证书。当前 TAIL02 尚无实际执行结果或完整 aggregate64、外层监督 POST，因而任何 L12 v2 可执行协议均不得生成。原 L12 runner、PRE 和严格的原单次 D64 PASS 前置保持原字节；本草案不改它们，不生成 protocol、claim、prior、binary 或实际费用快照。

## 来源及结论边界

原 D64 run01 为 `STOP_FINAL_WALL_OR_CPU_BUDGET`，15/30 项已停止，原运行资格为61/64、UNKNOWN `[61,62,63]`，8个进程均回收而最后进程为SIGKILL/-9。原 `no_retry_reset_or_resume=true`、完整原始记录和 gate=false 必须保存；未来任何新证据都不能把它改称 `PASS_FIXED16_ACTIVE_DISTANCE_INTERFACE`。

index61 已有完整真实 raw response，独立 saved-only 审查可以引用；原 runner 未生成该项 raw JSON/qualification 的事实仍保留。index62/63 原先没有dispatch，不允许公式、plain响应、同点理论或旧状态代替其尚待实际执行的原 body。

提出中的 TAIL02 只用同一 D-fixed binary、原 III 环境、trace模式、seed7和原冻结请求62/63，另建1个进程，独立5 wall/10 CPU帽；旧0..61不重查。它属于新版本、不同进程历史的有限接口证据；成功仅使用 `SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO` 限定标签。它不证明原8进程矩阵完整正常退出、RNG进程历史等价、CBi全局规划或原论文FULL。

新 distance certificate 只能与 L12 的其他完整前置组成AND契约。禁止把原 `status==PASS...` 改为宽泛的 `status in [...]` 或仅OR一个新标签后放行。

## 接收分次证书的全部必要条件

1. **真实新执行。** 存在已冻结且源码已提交的TAIL02协议、唯一claim、真实execution和原字节journal/外层日志；分别绑定source commit、binary、全部原始源码、观测变换、库/mesh和两个原输入。实际顶层dispatch/return恰为2、原索引恰为62/63，未发送旧0..61、无重试、无新候选或替代输入。不能接收草案、placeholder、预测成功或只含人工标签的对象。
2. **原来源不变。** 原D64 execution、protocol、claim、0..61 request/raw、8进程stdout/stderr、计时/根因审查及独立prefix审计，均按保存资产sha/bytes绑定，并在未来L12冻结和执行前后重核。原STOP、61 completed、UNKNOWN和-9真实进程状态显式保留；新certificate单列64项覆盖，不能覆写原字段。
3. **完整64项覆盖。** 人员独立aggregate POST必须读取并绑定实际全部64条原C++返回。原0..60使用原raw链，index61使用完整raw与prefix审计链，新62/63使用TAIL02新raw链；索引并集严格0..63、无缺失、无重复、无不明额外响应。每条均有真实body/transport来源，不能用参考公式填补执行证据。
4. **原完整数值门。** aggregate重新独立核对16个固定case在source-control/D-fixed和plain/trace的全部64返回：原source-control错误公式及四个唯一非零同点反例；D-fixed六维L2参考误差≤1e-12 rad、同点严格0、交换对称；role0两source返回binary64相同。四个原role1同点非零值为3.239119425422773、4.128865608898457、1.665155567082146、2.4702822659418953 rad，不将原对照应有错误改判为理论门失败。
5. **32对plain/trace。** 全部32对完整非观测字段和原request、distance、qa/qb-after、binary64串一致；只可移除mode和原明确观测字段，不能忽略真实source返回、输入或状态。tail62的配对plain46/control-trace30、tail63的plain47/control-trace31都真实存在并绑定。跨进程Motion身份只作为各自trace来源，不伪称全进程ID相等。
6. **64次双state不变。** 每次实际响应的qa12和qb12均按原输入binary64检查，包含signed zero；64次请求合计128份state输出均覆盖。每次显式role、原环境及原source factor一致。不存在重排序joint、阈值/单位/坐标改动。
7. **source trace与构造计数。** 新TAIL02原body activeDistance entered/completed各2，mesh_load各1；旧真实prefix为30及4，累计trace为32 activeDistance及5 mesh_load。累计实际dispatch/return为62+2=64、构造为8+1=9、结构性直接RNG member初始化为9；库内真实RNG constructor/seed draws保持UNOBSERVED。原32 plain内部真实body starts/completions仍UNOBSERVED，不将64 transport返回冒充64插桩body。每process construction只计一次。
8. **raw及进程监督。** 新TAIL02全部stdout/stderr读至EOF、无额外stdout、无未配对trace或未解析尾；真实新PID唯一登记、进程组无未知成员、已reaped且新源正常exit0。旧第8进程-9不能通过聚合被改成exit0；它只可提供经过独立核对的完整响应前缀证据。所有旧/新raw绑定与registry差异都须明列。
9. **外层监督POST。** 实际 external supervisory post须独立绑定TAIL02原命令、journal、stdout/stderr、execution、source PID/退出和外层time/时钟原始记录，确认强制证据落盘和清理尾部纳入5/10上限；实际任何超帽或不完整账目均STOP。内层sample不能代替最终journal/execution fsync及程序退出的测量，也不能补0给未测CPU。具体监督实现和精确字段必须在TAIL02冻结前独立审查，本文没有预先认定某一实现通过。
10. **全部实际费用一次入账。** 原D64的15.463848030998633 wall/.9817729999999999 CPU保留；TAIL02新执行按完整own-cost另外扣R2总3600/7200实际余额，独立保存分析不伪造science成本；aggregate证书不把旧成本再累计一次。新L12冻结时扫描当时全部真实execution，不绑定今天的推测prior或余额。任何外层最终费用/内层记录差异须有清晰单一计费来源和独立复核，不能重复计费或漏掉尾部。
11. **精确版本与独立性。** 在实际TAIL02成功后，需独立aggregate全部64和external supervisory POST均明确通过，且报告所绑定源码/协议/raw/费用字段一致。最终L12 v2只能接受冻结schema、精确成功标签、全部required gate全真及本契约明确列出的资产；未知schema、多余/缺少关键字段、假bool、过期hash、仅人工改label均拒绝。最终具体路径和sha只能取届时真实已保存结果，本草案不预填。
12. **门限与统计声明。** 这只满足distance-interface的分次受限资格前置，不意味着L12本身通过，也不授权S单solve或P路径外门。RSS/NR/H、VI974/974余额0、正式Table I 0/22500、完整211义务和所有原失败不变。

## L12自身保持的完整契约

L12 v2仍是D-fixed stage仅local接口，原三条边(0,3)/(1,3)/(0,0)；输入来自原E2E的全部三条高精度state回溯边，完整M节点数80/65/34。三边×原state-level RBS/reconstruct×plain/trace为恰12个顶层调用、2个SVC进程，不构造CBi或直接RNG member，不增加seed调用、独立FK/J/IK/碰撞外门、VI、solve或正式实验。原RBS_tol=.05、最大深度150、withObs=true保持。

预算仍整次30 wall/60 CPU、受R2实际余额限制；不因增加前置证据或监督而扩帽。原L草案final sample在execution.json写入前，存在已知尾部未测限制；未来v2实施与冻结前必须独立审查完整最终记账路线，将强制证据和监督写入纳入原30/60。本文只提出条件，不改原runner或自动移植TAIL02传输。

全部12源返回true，RBS确有非平凡递归；trace嵌套entry/return、投影原角色/解析branch、主动角不变、native FK/IK/collision真实计数均保持原审查规则。每边RBS/reconstruct投影输入/输出序列相同，投影输出multiset精确等于旧M内点。plain内部UNOBSERVED，只比对可观测qa/qb/源返回/完整M；不能编造plain内部trace。

新重构M每个binary64及完整首末、节点顺序须精确等于旧80/65/34；只有这样才能复用旧177唯一节点独立物理证书和176叶。禁止epsilon等价、截尾、换边、重采样、调阈值或新增物理查询以补救不等价。旧离散证书不证明连续碰撞安全。任何新M不同、false、trace/EOF/registry/hash不全即STOP，原旧路径资格和原局部PARTIAL保持。

L12成功标签仍限 `PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED`，certificate来源须额外标明SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO并绑定全部来源链；不能写原D64已PASS。原staged PRE的S和P前置需届时单独版本化，不由本说明自动放行。

## 冻结顺序与当前状态

先完成TAIL02具体runner/PRE独立静态审查和root冻结，再唯一真实执行及外层监督；保存全部成功/失败前缀。只有实际成功，才能独立aggregate64、审查监督与完整费用，随后另写新L12 v2 runner/PRE并审查本契约落实。最后才生成当时真实prior和最终执行协议，独立claim、提交源码并执行L12。若TAIL02停止，本契约仍不满足；不得用它准备乐观成功协议、自动再补预算或继续L12。

本草案不改变原L12 runner/PRE，也未生成当前prior、protocol、claim、compile或science。以下sha仅绑定本草案阅读的静态来源，不是可执行协议，也不表示这些来源已经拥有新TAIL02证据。

|静态来源|SHA256|
|---|---|
|`scripts/qualify_p4_full_r2_abb_cbirrt_d_local_draft.py`|`622a25ffdf23f95aba437309fa511d564ebaeab172323666d050a89598739e36`|
|`reports/P4_FULL_R2_ABB_CBIRRT_D_LOCAL_PRE_DRAFT_20261016.md`|`01a894ca390715ea8f59e0c010d9df4796d132b1443e60c58fe16f8641b20637`|
|`reports/P4_FULL_R2_ABB_CBIRRT_D_LOCAL_STATIC_SAVED_FIXTURE_REVIEW_20261016.json`|`d0b518f541220458f7c6186d4dfc2686b55a98ed918c924f5165f656bc9e5aef`|
|`reports/P4_FULL_R2_ABB_CBIRRT_D_SPLIT_SOURCE_BOUNDARY_INDEPENDENT_REVIEW_20261016.json`|`63166a93e9745427eae32fafc773b13540be9c8f2e710e2d62ea036b578ccadb`|
