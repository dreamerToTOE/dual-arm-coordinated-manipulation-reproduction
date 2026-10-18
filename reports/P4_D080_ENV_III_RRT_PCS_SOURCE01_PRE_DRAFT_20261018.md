# 环境 III RRT+PCS SOURCE01 保存恢复点（DRAFT，未齐协议）

2026-10-18，接续 V35。此文件保存已确认的工程边界和最早未完成项，不是 PRE 通过证书。root 要求本轮在明确不可执行的保存点收束；本代理不冻结、不运行、不入账、不提交。新增编译、二进制、机器人/碰撞模型及科学调用均为 0。

当前只有 `scripts/p4_d080/qualify_iii_rrt_pcs_source01_v1_draft.py` 初稿落盘，未经独立审查。配对的 `configs/p4_d080/iii_rrt_pcs_source01_v1.DRAFT.json` 和 `scripts/p4_d080/supervise_iii_rrt_pcs_source01_v1_draft.py` **尚未创建**。runner 的冻结门、真实 GNUtime 父进程/argv/独占 inode 门均必须满足才允许工作；缺配对文件和完整冻结配置时不可执行。不得将此保存点描述为四稿齐备或可执行协议。

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

1. 审查当前 runner 初稿与上述已审函数的差异，先保留初稿再修必要的工程错误。当前仅落盘，不存在独立静审结论。重点核实际 BUILD execution/POST 字段、20 mesh 集合、所有实际依赖覆盖、端点 status 键、完整 request、真实 worker 启停/双 EOF、异常时已有原日志保存与费用证据；不可用未运行初稿的意图代替完成证据。
2. 生成薄适配监督器和 DRAFT 协议；`frozen`、`scientific_execution_authorized`、`independent_review_passed` 和所有 reviews 先全 false。DRAFT 引用 V35，但 `actual_charge_prior` 与最新全量证书绑定由 root 冻结前按最新状态填入。独立审查/commit/真实先验/预算均齐备前不执行。
3. 固定科学输入只允许 III、A01、seed7、range `.8`、goal bias `.05`、原 sampler box、原内部 env2、一次原10秒 solve；外项30 wall/60 CPU、work25/50为待冻结工程提议，并在原R2总3600/7200内，不是正式实验或新增总预算。不得在 source 失败后更换点、种子、阈值或重试同 claim。
4. stdin 必须恰好一行 compact JSON 再 EOF，不能把 pretty JSON 文件直接喂给 `getline` driver。全部 stdout/stderr 保留；stdout 有作者原日志，不能要求每行 JSON。独立 `result.json` 和最后 stdout JSON 必须一致。
5. source exact、approximate、无解、非零退出、超时和回溯 false 各自留存。保存完整17位 `reconstruction_attempts.jsonl`、`identify_observations.jsonl`、原 paths 和 PlannerData；不补点、不截断、不合并替换 false。source exact 只产生后审候选，`independent_path_qualified=false`，不证明闭链、分支、限位、碰撞或完整离散路径。
6. 真正独立物理路径门后置，另立完整条件与实际预算，不直接移用 II 数学/物理资格或将 source返回 exact 当成功。内部 FK/IK/PQP started 未插桩仍是 UNOBSERVED；不能由一次请求反推精确内部次数。

D080 的正式 Table I 仍 0/18,000；环境 VI 只读归档且不追加；不开展 P2、Isaac Sim、双 FR3 或正式统计。V 的四个 RRT 工程 DRAFT 已独立薄审20/20通过并保持原字节，本恢复点不修改它们。
