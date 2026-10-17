# ABB RSS 固定4×8分支 roundtrip：PRE 草案

状态：DRAFT，仅完成保存输入与源码静态准备；未执行项目 import、describe、FK、IK、Jacobian、碰撞、RBS、solve、随机采样或编译，未生成 claim。四个输入严格为旧 `II_obs0681/0689`、`III_obs1065/1073`，每个完整原 q12 × 被动 arm2 的原 branch0…7，共32次 K；主动 arm1 原六角不变，无新候选筛选、周期提升或替换。原 active_branch=1 全是构造 arm1 的分支，绝不作 arm2 分支。

## 输入身份与已有证据

|case|原 observation 下标|原 source_index / mode|原数学资格|原碰撞证据|
|---|---:|---|---|---|
|II_obs0681|681|28 / 1|闭链/原界合格，真实被动 rank5|aligned clear、TCP一致；native clear但TCP不一致|
|II_obs0689|689|28 / 2|闭链/原界合格，真实被动 rank5|aligned clear、TCP一致；native clear但TCP不一致|
|III_obs1065|1065|44 / 1|闭链/原界合格，真实被动 rank5|aligned clear、TCP一致；native clear但TCP不一致|
|III_obs1073|1073|44 / 2|闭链/原界合格，真实被动 rank5|aligned clear、TCP一致；native clear但TCP不一致|

逐点已核对原 observations.candidate_q_rad、旧 collision protocol fixed_case.q12_rad、保存 replay q12 完全一致；前六角等于原 K arm1 branch1 解，后六角等于原 forced_passive_q_rad。协议保留原记录 canonical SHA、整份源文件与 replay SHA。旧 clear 仅对同一原 q12 有效，不能转移给 roundtrip 的其他 q12。

## 两层实现与最小工程

本32次运行层为 **GEOMETRY_CONSISTENT_CORRECTED / RECONSTRUCTED**。可复用既有 `build/p4_full/20261015_R2_SPATIAL01/abb_batch`，无需新 C++ 或构建；driver 接口为 `F arm q6` 和 `K arm branch T16`，K成功后内部再 FK一次。II/III 既有空间检查均330/330；corrected APC 的 geometry-consistent 修复、原 literal native APC 和同一 header 均分别绑定，不将 corrected 输出冒充原作者 literal runtime。

原 native APC cpp SHA为 `c74ea9ade8bb7d80b0b980139c58b659e6911ab3d3cb61b853be980654ede22c`；corrected cpp为 `aec7ea77728b32f1c0aacc8f5040d0085de2e54704b916e778541edc4c654e54`，header不变。native 在本32次没有新 IK 调用；若需其逐分支 runtime 对照，最小工程是将同一既有 spatial_batch_driver.cpp 链接固定 native APC 生成新外部 binary（无需新数学源码），单列构建与后续运行预算，不能暗加另一批32次。

独立数学接口复用 `physical_nr.arm_fk_jac(q6,env,arm)` → `abb_independent_oracle.abb_fk_and_jacobian` 的独立世界 FK/J（mm）；复用 endpoints 的 `branch_identity` 几何符号规则，不复用最近根推测。现有 Batch类无需改动；新草案 runner 为每次输入保留独立原始 stdin/stdout/stderr/JSON、进程 pid/回收状态及启动/完成计数。

## 固定操作与科学含义

每点先作一次 source F arm1，保留 `T1 Q12 diag(-1,-1,1,1)` 的源 target 与独立物理 target 两份。按原序 K arm2 b0…7。最多32 IK、4显式源FK、32个IK成功时内部FK、40独立arm FK/J、36个被动rank SVD。4×8是IK输入上限，非所有内部运算合计。

原闭链/roundtrip门1e-5 mm与1e-5矩阵误差；源FK独立一致门1e-7 mm/1e-10；真实被动J先将平移行mm→m，秩阈值sigma_max×1e-6。原界使用literal 3.1416和原机械界。逐根记录原角变化、raw L2、canonical wrist、独立arm2分支集合与请求分支成员关系、闭链、秩、限位；奇异分支合并仍保留，不要求八个不同解。源raw<0.1的原状态身份只单独报告，不用于最近解选点或通过门。

本项仅数学分支映射：`qualified_math_only` 不是 RSS节点资格，`singular_math_only` 另要求真实被动rank<6。所有输出 collision=UNKNOWN；必须另冻原pair/mesh/8mm、native+aligned的逐输出碰撞 replay 后才能考虑 RBS入口。此草案不推断 regular邻点、regular↔singular桥或RSS规划成功。0 VI、0 RBS、0 solve、0 NR、0采样/RNG、0碰撞、0正式统计，γ=.2未改。

## 预算与下一门

拟单项10秒墙钟/20秒CPU，受原R2 3600/7200总限约束。历史 `RSS_CONSTRUCTION01` 保存为5600固定分支记录、1.5027174159999959秒wall/1.015161秒CPU；这里只能作为有限可行性依据，不能当本项实测。本草案改为36个短进程并逐条fsync，启动与I/O尾成本未测，不能保证10秒内完整32项；到限必须 STOP_PREFIX_RETAINED/UNKNOWN，保留未执行清单，禁止重试或换输入。当前未重新测成本。

执行前下一门是主代理/独立静审 runner 与本32固定表，冻结当前root最新账的真实SHA和可用剩额、同一外部一次性监督launcher。协议当前 `frozen=false`、`accounting_snapshot=null`，runner拒绝运行。launcher尚未准备；须绑定当前协议SHA、live parent PID、单次启动及10/20硬资源边界，外部监督上界与独立POST必须覆盖导入、所有子进程、执行和落盘尾部。不能把旧ledger残余复制成新总预算。

待上述条件冻结后的命令接口是 `python3 scripts/qualify_p4_full_r2_abb_rss_branch_fixed32_draft.py --protocol <reviewed-frozen-protocol> --external-launcher-receipt <live-reviewed-receipt>`，本次没有执行该命令。普通IK false或数学拒绝保留并继续其余固定分支；源/输入/证据/预算异常停止，保留原始前缀和未执行项。真实结果还须独立POST，之后才能入最新账或提出RBS门。

全部旧0/100、奇异中心、原RSS失败、VI974/974耗尽、211项完整义务和正式0/22500均保留。无P2或Isaac扩展。

## 文件绑定

- runner草案 `scripts/qualify_p4_full_r2_abb_rss_branch_fixed32_draft.py`，SHA256 `9ef810d81bc87bb670dc68baefcbaf7974abd926655817e428c4ed6b661c585a`。
- 协议草案 `configs/p4_full/r2_abb_rss_branch_fixed32_math_v1.draft.json`，SHA256 `1bea1b060542c1ef6f478581817e1dda963622600bd9ad3119c99616601da656`。
- corrected binary SHA256 `03fccdee5f0693202210ab033721208976fa2a68794b48a2412531839d23f2b3`。完整23份绑定在协议。
