# V PHYSICAL01 最薄冻结字段与工程复用接缝

本页是不可执行DRAFT字段图；未调用模型、编译或科学。最终runner/supervisor/PRE报SHA后不追加结果；结果另写POST。

| 字段 | 冻结含义 |
|---|---|
| `schema/run_id/claim_id` | `P4_D080_V_PCS_PHYSICAL_FIXED24_RUN_V1` / `20261018_R2_D080_V_PCS_PHYSICAL01` / `P4_D080_V_PCS_PHYSICAL01_FIXED24_60W120CPU_20261018` |
| `environment/classification` | V / `CORRECTED_COMAU_APC_RECONSTRUCTED_A02_FIXED24_INDEPENDENT_DISCRETE_DIAGNOSTIC` |
| `queue/queue_sha256/fixed_queue` | 原saved完整24节点队列6fa6…e35原字节；嵌套源DRAFT保持不变，不能改nested frozen或任一q |
| `execution_node_ids` | 固定0..23；每个node取`q12`，核全部`role_branch_assignments`；不是重选24成功样本 |
| `source_provenance/queue_provenance` | 原LOCAL01 execution a054…7985、transport194 06c1…ac49、queue addendum ca155…c59c；原identity FAIL与14复用项保留 |
| `frozen/scientific_execution_authorized/reviews` | 本DRAFT全部false；root独审后方可改true并绑定新独审证书，最终提交后唯一执行 |
| `budget` | 60wall/120CPU，work50/100，原R2总3600/7200；worker RLIMIT120；没有新时间或采样总额度 |
| `prior/actual_charge_prior` | V33当时真实1103.9938663219941wall/923.983153CPU；直接借B.validate_prior，显式B.RUN_NAME/B.RUN设为本新run避免排除旧BUILD01 |
| `bound_files_sha256` | 源/队列证书和原输入、OWN及工程依赖、Comau数学核、v3 manifest/双variant binary/source/mesh/PQP、最新账及execution/POST/charge/receipt/time/metadata/stderr；每个当前SHA前后不变 |
| `gates` | 原位置/矩阵1e-5、branch64epsilon；原全12叶严格<.05、几何/限位不改 |
| `max_*` | 48独立FK、48branch、24adapter、96adapter内部FK/J、4176PQP；完整运行精确计数，无IK/NR/RBS/solve/RNG/正式统计/VI调用 |
| `external_supervision` | 原tail02 O_EXCL time inode、真实父argv/进程证据、Decimal三观测max包络；receipt为cost_receipt.jsonl，与旧v6入账解析兼容 |
| `independent_local_qualified/independent_path_qualified` | 始终false；24节点诊断完成且包含原正常拒绝可exit0；不能变三false公有根为成功 |

AST直接复用：tail02 `supervisor_proof`原函数；old.Budget的start/alarm/check/remaining/close；完整collision worker注册/进程组/EOF/selector/raw-tail清理块、adapter FK计数块。显式工程适配仅新V身份、L.Journal别名、budget50/100及60/120、RLIMIT120、B当前run身份与最终诊断完成状态。supervisor保留原tail02全文结构，只替身份/路径/schema/限额与更严格冻结入口。

科学适配单列：独立endpoint核从II改V，取既存完整q12/角色关联；每node保存全部2FK、闭链、原限位、双臂branch及每assignment，再调用显式v3的V/native+aligned；aligned碰撞true或数学reject继续后点，UNKNOWN/API/缺variant/TCP失败先保存响应，再停prefix。原17唯source collision的pair聚合与box矩阵由保存POST按原数学式交叉核，不在runner新增box通过阈值。零新构造/采样/规划。
