# ABB CBiRRT_NR：唯一单次规划入口 PRE 草案

2026-10-16。DRAFT_ONLY / NOT_FROZEN / NO_PROTOCOL_OR_CLAIM / NOT_EXECUTED。本草案仅准备一次原作者 CBiRRT_NR 双树规划的版本化入口；工程六稿保持稳定，由 root 独占冻结与执行。原 211 项论文义务、VI 974/974 余 0、Table I 0/22500、原失败与 UNKNOWN 全部保留，不开展正式统计、P2 或 Isaac。

唯一拟运行 `20261016_R2_ABB_CBIRRT_NR_SOLVE01`，分类 `R2_RECONSTRUCTED_PHYSICAL_NR_SINGLE_ORIGINAL_CBIRRT_NR_SOLVE`。源码为已独立静态审查的原 CBiNR NN/双树/grow/RBS/回溯完整控制 body，仅沿用已资格通过的 physical-GD seam、只读完整 body 观察和保留 temp 的 I/O 偏离。该数值重建不冒充作者原 KDL GD；不混入 PCS H/D、active role、解析 branch 或 SBL projection 设计。

在实际工程 build 和人员独立工程 POST 尚不存在时，`build_assets()` 必须在形成具体 protocol/prior 之前拒绝。工程独立 POST 的预先接口（并非预测结果）由独立审查者明确：`reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_20261016.json`，schema `P4_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_V1`；只有真实状态 `PASS_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST`、人员独立和外层成本通过、全部 checks 通过，以及实际 execution/manifest/internal receipt/外层 receipt/protocol/claim SHA 全部匹配时，才可形成后续冻结草案。未知、缺失或失败均不能用 placeholder、空对象或预测 true 代替。还要求真实工程状态 BUILT_NOT_QUERIED、compiler exit0/reaped/after-group 空、六份实际 TU 依赖合格、绑定/新源码/mesh/原件最终 SHA 相同、零 binary/query/solve。

复用现存 Q1 工程与已保存 NR local 全资格、人员独立 local 218766/218766 和 raw-link 666/666，以及完整 393 节点 NR 路径人员独立 24448/24448。后者 execution SHA `fd74acd7ce5f747cc7123cacef8c9467b1fa985d9d88afdcac47aee0956a5754`、源 solve execution SHA `573a1e0bb11a345811ff380a838eb4818000963e98adb90664dfaace755a58b7`。仅绑定并检查保存证据、数组/文件/源码 SHA，不重新调用 FK/IK/NR/Jacobian/碰撞或运行旧 binary。旧 RRT_NR 路径证书只证明既有数学/离散碰撞适配资格，不能代替本次新双树路径检查。

拟固定环境 II、同一 RECONSTRUCTED A01 原已资格起终 q12、seed7、range2.6、原 solve10 秒、原 sampler low/high（含第6/12轴 ±3.1416）、always-true callback、原 NR resolution .1、原 full12 L2 NN、无 smoothing。一次 setSeed7/srand7 在 OMPL 对象前；只有一个实际 source process、一个请求和一次 source solve。observer 的 13 类 NR body 计数与实际嵌套 enter/completed 原样保存；只允许源 `save_source_mpaths` 只读观察，不读取不存在的 PCS chain/branch 字段。实际未 hook 的库 seed/RNG draw 总数继续 UNOBSERVED，不报零。

本项独立最多30wall/60CPU，child单进程CPU硬帽60，仍受 R2 总3600wall/7200CPU；不是 S01/S02 共享余量或重复运行。冻结必须使用最新权威跨日期 charged ledger 的全部实际 execution 集合，外层人员独立证书只替换内部成本一次；孤立 supervision charge 先补账，历史未测尾部 UNKNOWN 保留。源码/协议必须实际提交后，root 才能唯一启动外层 supervisor→GNUtime→runner→source。所有 import/preflight、保存证据读取、mesh拷贝、solve及其原始文件/trace写入、双pipe排空/回收、最终hash、execution/receipt持久化和退出均在既定外层边界计费；Decimal +.01 wall/+.02 CPU 后仍须满足单项/累计帽。Supervisor自身journal/fsync边界外明确披露，内部 external_supervision_qualified 始终 false，等真实独立 POST。

与已审查 S 传输的两项必要工程适配已获 root 明确授权。第一，NR driver 唯一 getline 后等待 stdin EOF 才 dispatch，所以必须以一次 `os.write` 写完 exact compact JSON+LF 后立即 close stdin；不能等 finish 才关。完整请求 bytes/base64/SHA、实际 sent/实际已写字节和 SHA、close 结果及 response.request exact 匹配全部保全。短写、写入结果 UNKNOWN、close 失败只能 STOP，不重写或补请求。第二，driver 在唯一 JSON 后直接退出，normal close group 可以是真实单 PID 且原 startticks 的活组，也可以是实际 poll exit0 后独立扫描为空的组；空组不能推断成功。两条路都必须实际 stdout/stderr 各自 `os.read()==b''`、wait/reap exit0、之后实际 group 为空、原 PID startticks 持续保全。未知/额外成员、非零退出或未观察双 EOF 只能 STOP。异常清理独立检查/kill 原 group，即便 Popen 已经记录退出也不遗漏同组成员。

stdout 合同严格为一条完整 JSON+LF；本 driver 的 constructor/setup/solve/getPlannerData 都在 Redirect 内，不能继承 S02 的55字节 preamble例外或跳过未知行。第一行后仍排空双pipe，第二行、非换行尾或未知前导均保留并STOP。完整原始 stdout/stderr、每chunk原字节、NR marker `P4_CBIRRT_NR_TRACE ` 的完整函数观察与 response trace binary64 exact 相同、最终EOF和退出证据全存。construction reset 后的 solve ID/计数独立；临时 Motion ID 不强制属于终态树，等q不同Motion不合并。

保存原两个树所有 Motion/state/root/parent 身份、实际退parent后的两桥端、source mpaths、milestones、PlannerData及全部原生 `work/paths` 文件/失败/temp。桥两端不强制等q，goal树边方向按原source保留，不自创 branch fallback。原 `save2file` 是 void，可能在 reconstruction false 后返回但 solve 仍报告 EXACT；因此本项状态只允许 SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT 或完整 NONEXACT prefix，均非路径资格。所有 false、部分 dense 和 source exact 矛盾都留待独立审查；不以文件存在/returncode0/save return冒充完整路径。

若取得 source EXACT 候选，后续仍须另冻针对全部真实原 M 的数学闭链、原限位、v3 aligned 离散碰撞与全 leaf 距离门，不截尾、不补点、不换seed、不降低门槛。本草案不启动该检查，更不宣称连续无碰撞、统计优势、作者原 KDL 等价或完整 P4。端到端资格后才运行可重复成本 pilot 并向用户申请正式计算预算；全部原文规模继续保留。
