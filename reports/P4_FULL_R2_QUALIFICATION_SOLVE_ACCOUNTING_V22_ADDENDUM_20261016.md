# V22 资格 solve 实际调用计数补充（saved-only）

结论：截至 V22，实际向原生规划器派发的资格 solve 共 **5 次**，V21 已有 **4 次**，V22 新增 **1 次**。包含 CBiRRT PCS/D SOLVE01 的失败派发；不以成功次数、路径数、POST 次数或 ledger 行数代替实际调用数。

V22 ledger 原字节保留。`new_qualification_planner_solves_in_this_snapshot=0`、`previous_snapshot_qualification_planner_solves=0`、`total_qualification_planner_solves=2` 是沿用的历史狭 scope 字段，不再作为当前完整调用计数。第四个字段 `new_scientific_calls=0` 只表示 saved-only ledger 生成没有调用科学程序，不表示 V21→V22 没有新增记录。当前计数以补充 JSON 的 `authoritative_counters` 与逐 run_id 证据为准。

| run_id | 实际 dispatch | V22 新增 | 保存状态 |
|---|---:|---:|---|
| `20261015_R2_ABB_RRT_PCS_E2E01` | 1 | 否 | `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT` |
| `20261015_R2_ABB_RRT_NR_E2E01` | 1 | 否 | `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT` |
| `20261015_R2_ABB_CBIRRT_D_SOLVE01` | 1 | 否 | `STOP_PREFIX_RETAINED` |
| `20261015_R2_ABB_CBIRRT_D_SOLVE02` | 1 | 否 | `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT` |
| `20261016_R2_ABB_CBIRRT_NR_SOLVE01` | 1 | 是 | `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT` |

RRT PCS/NR 分别由 dispatch 文件、唯一子进程及保存结果 `solve_calls=1` 支持。PCS/D SOLVE01 保存唯一 solve_request、`solve_dispatched=1`、返回码 -9 和 JSONDecodeError；stdout 只有 55 字节 Debug 前导行、无 solver JSON，因此保留原失败，不推断成功或路径资格。PCS/D SOLVE02 的两行 stdout 是 setup 前导加一个 JSON 响应，唯一请求和 `solve_calls=1` 只计一次。NR SOLVE01 的 612 字节请求、实际发送 612 字节、关闭 stdin、唯一源进程及完整响应 `solve_calls=1` 相互绑定。

JSON 记录 execution、dispatch/journal、原始 stdout/stderr/result 的真实 SHA256、行号、状态和次数。保存 R2 execution 共 40 项、40 个唯一目录 ID，其中 37 项有显式 run_id，另 3 项 legacy execution 由目录标识；恰好上述 5 项有非零 solve_dispatched。仅用标准库读取文件，无项目导入或科学调用。

成本仍为 V22 的 795.885705375994 秒墙钟、716.458923 秒 CPU。NR 新调用以外部 charge 9.06/8.71 秒替代内部样本一次；补充不增加成本或 execution 行。VI 候选仍为 974/974、剩余 0；正式 Table I 为 0/22500。调用计数不宣称 5 条路径均合格，不替代待执行的 NR 完整物理路径资格。

绑定文件：

- `results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V22.json` SHA256 `e0432dc0a92852db3a67f9c62535d80b4d4ab8a90f6430832320247420d0ff1e`。
- `results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V21.json` SHA256 `44bca63413c2e4aebdc52f360784a049d60f5c4d001ebd3f3d6abd692c84766b`。
- `results/p4_full/20261016_RECOVERY_QUALIFICATION_SOLVE_ACCOUNTING_V22_ADDENDUM.json` SHA256 `316024926cbd63e1f6ca53db0be6d7cc4419b9cb3b029450f642e3529f87bcb9`。
