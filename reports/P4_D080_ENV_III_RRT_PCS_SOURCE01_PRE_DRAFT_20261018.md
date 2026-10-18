# 环境 III RRT+PCS SOURCE01 保存恢复点（DRAFT，未齐协议）

2026-10-18，接续 V35。此文件保存已确认的工程边界和最早未完成项，不是 PRE 通过证书。本代理不冻结、不运行、不入账、不提交。新增编译、二进制、机器人/碰撞模型及科学调用均为 0。

历史保存点只有 runner 初稿、没有配对协议与监督器；该版本仍在 Git 历史保留。随后用户明确授权 III SOURCE01 在原 R2 额度内执行一次原10秒 solve，以及候选另立物理门，root 指派本代理补齐当前四稿。现在 `scripts/p4_d080/qualify_iii_rrt_pcs_source01_v1_draft.py`、`scripts/p4_d080/supervise_iii_rrt_pcs_source01_v1_draft.py`、`configs/p4_d080/iii_rrt_pcs_source01_v1.DRAFT.json` 和本文件齐备，所有执行/冻结/静审布尔门仍为 false。独立静审、root 最新 prior 复核及提交冻结之前不执行；本文件不构成已经通过的 PRE。

## 已确认且直接复用的资产

- III 唯一工程 BUILD01：`results/p4_full/20261018_R2_D080_III_RRT_PCS_BUILD01/execution.json`，SHA256 `16696c0d80ce0ac893814afc2ca5e0720e6ebb478da63cc6e46eb8f7b80c4f31`；`BUILT_NOT_QUERIED`。不重新编译。
- 独立工程 POST：`reports/P4_D080_ENV_III_RRT_PCS_BUILD01_SAVED_INDEPENDENT_POST_20261018.json`，SHA256 `c311dd3601995006c6b476163b51c3719bad193896d17ca349e35ca5ed3d829e`；49/49，通过范围只有工程及外层监督/费用，source planning 与 independent path 都仍为 false。
- 已建 ELF：`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_iii_rrt_pcs_e2e_v1/geometry_consistent_observed/p4_abb_iii_rrt_pcs_e2e`，SHA256 `81dac2e24b8c929c1849f60bc95b6e034ee7b4f3ec21eed5dc35595fdb60174e`。
- 已建 driver：`baselines/p4_full/geometry_consistent/abb_iii_rrt_pcs_e2e_driver_draft.cpp`。这是 II 已资格工程的八项 III 环境替换版本，原 RRT/PCS 控制体不改。保留当前 ELF 与全部输入，不为本项修改 driver。
- 旧局部：`reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_TASK_20261015.md` 与 `reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_ADDENDUM_20261015.md`。III 的 7 正 1 拒绝直接复用，拒绝项不改判，不重跑局部。三参随机 helper/sample_q 在该 RRT 路线上不可达，不能误设为前置阻断。
- III A01：`results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/III_0.json`（SHA256 `85550cbc3ffbf80c80519b5e592e85401dcf1e96ce747f0df5f3d97c97065c6a`）、`III_1.json`（SHA256 `50db8b75e8c29c9dfc42646e5165c22f31dd8e2853858686572405c3cd91cc12`）。继续标记 RECONSTRUCTED，不做端点恢复、换点或新 IK/NR。
- 账本 V35：`results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V35.json`，SHA256 `0565da281be5f00acd8444b8d7fd31c2392e0a4556ac2dbab2115b3fb312f28f`，53 executions = 38 science + 15 engineering；累计 wall `1135.516766637992`、CPU `961.89109`；原 R2 3600/7200 帽下余额仅上界 `2464.483233362008` / `6238.10891`。冻结时仍须核对最新真实账，不把保存的 V35 硬当永久最新。

## 最薄复用路线

`scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py` 的 `Budget.start/remaining/close`、`Journal`、`Session.register_pipes/pump/finish`、`kill_source_group`、`active_p4`、`preload_state`、`stat_row` 直接复用。新 Session 只适配已有 driver 的 argv、单次 compact JSON 写入后 EOF 和混合 stdout/result 文件接收；不采用 SBL 的 loaded_scope，也不伪称环境 III 已观察到具体加载符号。

`scripts/p4_d080/build_v_pcs_local_v1_draft.py` 的 `validate_prior` 和其 `lifecycle.live_group_cpu` 直接复用；必须设置 `B.RUN_NAME`/`B.RUN` 为 III SOURCE01，确保本项结束复核正确排除自己的新 execution。最新版账本、每次已计费 execution、独立 POST、原 GNUtime、内部 receipt 和 charge 全部逐字绑定；历史 UNKNOWN 及已有 cap breach 不回写。

`scripts/p4_d080/supervise_v_pcs_local_v1_draft.py` 是未来监督器的薄适配来源：只改 III 的 run/claim/label/runner/schema、单个 source 的描述，保留真实 GNUtime 父链、argv、O_EXCL 已开 inode 与原三观测 Decimal 最大 envelope。仍使用 `cost_receipt.json`。不要建立新的工程框架。

## 尚待完成，按此顺序接续

1. 独立增量静审当前 runner 与已审函数的差异；初稿已在 Git 保留。实际 BUILD execution/POST、20 mesh 集合、677实际依赖映射、端点 status 键、完整 request已做只读字段自核。真实 worker 启停/双 EOF、异常原日志保存与费用证据仍要静审及唯一运行后的独立核对，不能用未运行代码的意图代替完成证据。
2. DRAFT 协议的 `frozen`、`scientific_execution_authorized`、`independent_review_passed` 和所有 reviews 全 false。DRAFT 引用 V35，`actual_charge_prior` 暂为 null；最新全量证书绑定由 root 冻结前按最新状态填入。独立审查/commit/真实先验/预算均齐备前不执行。
3. 固定科学输入只允许 III、A01、seed7、range `.8`、goal bias `.05`、原 sampler box、原内部 env2、一次原10秒 solve；外项30 wall/60 CPU、work25/50为待冻结工程提议，并在原R2总3600/7200内，不是正式实验或新增总预算。不得在 source 失败后更换点、种子、阈值或重试同 claim。
4. stdin 必须恰好一行 compact JSON 再 EOF，不能把 pretty JSON 文件直接喂给 `getline` driver。全部 stdout/stderr 保留；stdout 有作者原日志，不能要求每行 JSON。独立 `result.json` 和最后 stdout JSON 必须一致。
5. source exact、approximate、无解、非零退出、超时和回溯 false 各自留存。保存完整17位 `reconstruction_attempts.jsonl`、`identify_observations.jsonl`、原 paths 和 PlannerData；不补点、不截断、不合并替换 false。source exact 只产生后审候选，`independent_path_qualified=false`，不证明闭链、分支、限位、碰撞或完整离散路径。
6. 真正独立物理路径门后置，另立完整条件与实际预算，不直接移用 II 数学/物理资格或将 source返回 exact 当成功。内部 FK/IK/PQP started 未插桩仍是 UNOBSERVED；不能由一次请求反推精确内部次数。

D080 的正式 Table I 仍 0/18,000；环境 VI 只读归档且不追加；不开展 P2、Isaac Sim、双 FR3 或正式统计。V 的四个 RRT 工程 DRAFT 已独立薄审20/20通过并保持原字节，本恢复点不修改它们。

## 固定字段及证据映射

| 冻结字段 | 真实输入/验收来源 | 范围 |
|---|---|---|
| schema/run_id/claim_id/classification | III SOURCE01 固定常量与两新脚本门 | 新 run/独占 claim；不重用 BUILD claim |
| target | 已保存 BUILD01 的单 target binary 与 SHA | ELF直接复用，不编译 |
| request | III_0/III_1 的 `selected_q_rad`；现有 driver 常量 | III/A01/seed7/.8/.05/10秒，原 q6 sampler bounds |
| runtime_meshes_sha256 | BUILD01 `staged_after_sha256` 中20个 `.tris` | 逐字复制到新 runtime/simulator；paths事前不存在 |
| bound_files_sha256 | 全部 staged/dependencies、链接库、工程POST/receipt/time、端点/local、D080及本项源码 | 前后逐字核对，不改变旧结果 |
| prior/actual_charge_prior | 最新版本账 + `B.validate_prior` 全量证书 | V35为草案引用；root冻结前终核，不扩大R2帽 |
| budget/working_budget | 用户本项授权 + 原R2总帽 | 外30/60、work25/50，给收尾5/10，不改变solve10 |
| source_request_dispatched | 唯一完整 `os.write` 返回字节 + stdin EOF | dispatch 不等于内部精确solve/FK/IK/PQP started |
| source_result | 原 result.json 与混合stdout最后JSON逐值一致 | exact/approx/no solution分开；只 source入口 |
| solve_calls_from_result | 完整exit0/result契约通过后赋 `result['solve_calls']` | 对接v6真实source账；失败未知保留null，不能从dispatch推计 |
| reconstruction/identify | 原17位jsonl与result逐条/完整计数对应 | 保留false/partial；原schema含ABB legacy名称 |
| source_process_registry | 实际PID/start ticks/reap/空group/双pipe EOF | 异常也清理；失败exit不伪装0 |
| external_supervision | 实际父链/argv/O_EXCL inode；原Decimal三观测max | 成本最终由独立POST核，原内部费用不双计 |
| qualification | `independent_path_qualified=false` | source exact不证明闭链/分支/限位/碰撞/叶距/CCD |

独立增量预审发现旧 `L.active_p4` 不覆盖新 D080 脚本路径。本项薄复制 III builder 已审 `active_d080`，仅将 launch proof 的 `actual_time_pid` 键适配为 `time_pid`，匹配真实 Python argv 与 `/proc/<pid>/cwd`，排除经实际父链证明的本 runner/GNUtime/supervisor 三PID；不扫描 shell 命令字符串。此为工程互斥门，不改变算法或预算。
