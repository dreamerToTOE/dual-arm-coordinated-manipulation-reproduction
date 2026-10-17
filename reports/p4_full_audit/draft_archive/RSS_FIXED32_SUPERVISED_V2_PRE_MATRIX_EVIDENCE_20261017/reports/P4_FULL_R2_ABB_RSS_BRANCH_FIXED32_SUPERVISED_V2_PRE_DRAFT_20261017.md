# ABB RSS 固定32数学分支：V2工程监督 PRE 草案

状态：DRAFT、未冻结、未运行。本项仅版本化修补 v1 的监督与收尾工程。v1 runner、协议、PRE、静态补充全部保留；没有导入/运行项目、描述协议、编译、模型/FK/IK/J、碰撞、RBS、solve、随机或成本 pilot。本 PRE 不证明未来可在预算内完成，也不构成执行授权。

四个输入及其顺序仍为 II_obs0681、II_obs0689、III_obs1065、III_obs1073，各保持完整原 q12 与主动 arm1 角，按原 arm2 branch0…7 共32次 K，每点一次显式源 F1。仍使用既有 geometry-consistent corrected ABB batch binary，RECONSTRUCTED 数学层；原 native literal APC 字节仍绑定且不新增其运行。原源 target 与独立物理 target 分开保存，不修正 target、不作周期提升、不换点、不NR回退。

原数学门全部保持：闭链与 roundtrip 1e-5 mm/1e-5矩阵，源FK独立一致1e-7 mm/1e-10，平移J行mm→m、相对秩门1e-6，原branch零因子门与原关节限位。最多32 IK、4显式source F、最多32成功K的内部FK、40独立arm FK/J、36原rank SVD。仅增加现有SVD的开始/完成计数与预算检查，不增加SVD。K的内部FK没有逐内部trace；完整成功响应可以提供已返回FK的证据，中断K内部开始/完成仍UNKNOWN，不能把上限作实际调用数。

V2保留原36个短进程结构，每个仍只发一行原F/K请求；使用管道暂缓唯一输入，以先观察实际pid/start_ticks、父pid、独立源进程组、原exe/argv及固定单线程env，再完整写入原字节并关闭stdin。保存每项原stdin、stdout、stderr、native JSON、双管道实际EOF、回收返回码和退出后空组。源模型构造发生在读取stdin前；本项没有新源内部trace，不能声称其内部计算总数已完整观察。输出原collision资格不能转移给新q12；新输出collision仍UNKNOWN，不能认定完整RSS/RBS资格。

外层单次GNUtime监督使用O_EXCL既有inode/继承FD与持久化planned原行。worker核对真实parent GNUtime、祖父supervisor PID/start_ticks、真实GNUtime exe/argv/FD inode与协议/源码SHA；不能用一份离线parent_pid receipt代替。root须在已完成的真实V25 ledger、实际preservation与外部独立POST全入账后生成当前prior，绑定所有实际跨日期execution SHA、charged fsum、历史UNKNOWN、VI974/剩余0与正式0/22500；静态模板accounting_snapshot/actual_charge_prior仍null，frozen与三项reviews仍false。没有复制V24剩余预算来冻结新运行。

预算仍总10秒wall/20秒CPU，受R2总3600/7200约束。工程在同一预算内预留1.5秒wall/2秒CPU，worker科学阶段到8.5秒wall或18秒CPU停止前缀，先停内部alarm防finally重入，随后在原总限内kill/drain/wait/reap、逐项捕获hash/日志错误并持久化execution与独立terminal receipt。所有尾部由仍存活GNUtime计时；终收据本身尾部不假设零。外层live /proc CPU/墙钟watchdog在9.7秒wall/19.7秒CPU停止唯一worker与源组，并尽量保留GNUtime最终原始行；如实际输出/时间无效，则fallback仅为不完整有限观察，绝不当完整合格上界。硬止可使worker收据缺失，外层独立charge仍记录真实终止与费用，原prefix不删除不重跑。

watchdog同时按ancestry与唯一冻结native exe观察源进程，拒绝已有同exe进程，杀进程须匹配pid/start_ticks和源组长；退出后再次保存源组与相同exe存活检查，发现遗留时独立POST必须拒绝完整资格。监督自身watchdog/metadata/fsync成本另行有限观察，维持现有GNUtime child成本边界；监督最终record持久化仍不在该观察样本内，不能宣称所有机器成本精确无尾差。

36进程与多次fsync开销尚未测量。较早5600条历史1.5秒不证明V2成本，也不能凭本草案保证固定32完成。到预算/原始证据异常即保留成功、失败与未执行清单，不重启、不换输入、不加时间。若需改变短进程结构或数学方法，须另审；本V2未引入持久会话或新数学设计。

未来接口为新runner --describe-protocol（仅在真实已固定V25且仍为最新实际账时），root/独立审查冻结输出到独立新协议并提交，再由新supervisor --protocol启动一次。当前没有执行这些命令，也没有生成claim。未来必须独立核对实际GNUtime原行、launch/FD/PID链、每项原字节、完整计数、原数学结果及未完成项，才能追加科学费用账；即使32数学记录完整也不升级碰撞、RBS、RSS分布或规划成功。γ=.2与0VI、0RBS、0NR、0RNG/采样、0solve、0正式统计全部不变。

新草案文件：scripts/qualify_p4_full_r2_abb_rss_branch_fixed32_supervised_v2_draft.py；scripts/supervise_p4_full_r2_abb_rss_branch_fixed32_v2_draft.py；configs/p4_full/r2_abb_rss_branch_fixed32_math_supervised_v2.draft.json。本PRE不嵌入新协议自身SHA，避免与协议绑定PRE形成循环；后续静审文件单独列明真实文件SHA。

静态准备期间实际V25已由root完成并固定：`results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V25.json`，SHA256 `ce612e7c9706666a338aae6deda581274f1aadb229e2be999cd6ee836499e64a`。本候选只允许该文件仍为最新实际账时再冻结，43次执行（32science+11engineering）；若产生更新账或未入账执行，必须重新静审prior，不能静默改用旧剩额。本模板仍未填accounting_snapshot或生成协议。
