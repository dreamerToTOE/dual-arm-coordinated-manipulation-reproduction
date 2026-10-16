# ABB 原生 CBiRRT_NR：单目标工程 PRE 草案

2026-10-16。DRAFT_ONLY / NOT_FROZEN / NO_CONCRETE_PROTOCOL_OR_CLAIM / NOT_BUILT_OR_EXECUTED。仅准备一个新 CBiRRT_NR binary 的版本化源码；本稿不授权运行 driver、NR/IK/碰撞/RBS/solve、随机采样或正式统计。原 211 项论文义务、VI 974/974 余 0、Table I 0/22500 及原失败/UNKNOWN 保留。不改刚完成的 CBiPCS P 或治理文件。

原作者 commit `909bd72fff778aca8682c96f9eb86ae4eb75557b`。原 `planners/CBiRRT_NR.cpp` SHA `436a89887a7c233f1515800f216e9d626f9f29dee3c230fd8d1ff86567367804`、`.h` SHA `fe47f4b4d0bd9ab38792ca42c6c3280f622f8a4b0babbce910b4600ba8303338`，实际与既有 qualified template、RRT_NR stage 逐字相同。静态诊断见 `P4_FULL_R2_ABB_SBL_PCS_CBIRRT_NR_ENTRY_STATIC_DIAGNOSIS_20261016.md/.json`。SBL 暂停在该静态记录，不改其默认 projection、lazy 控制或未初始化字段。

新目录 `/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_nr_v1/physical_nr_observed` 必须不存在；唯一工程 run `20261016_R2_ABB_CBIRRT_NR_BUILD01` 和原子 claim 也必须不存在。从既有 geometry_consistent_plain 模板新拷贝，不修改任何旧 stage/binary/失败/路径。编译链接原 KDL/SVC NR/collision/CBiRRT_NR 四个 cpp，加唯一已合格 `abb_nr_interface_kernel_draft.cpp`；沿用 g++11、C++17、O1/g0、OMPL1.7、orocos-KDL、PQP 和原 mesh/header。所有旧 compiler/library/header/manifest/源码/二进制 SHA 都绑定，保存完整工程 stderr/stdout 与部分失败。

唯一数值偏离是原 `kdl::GD` body 继续调用同一已 Q1、NR local、RRT_NR 资格通过的 physical GD seam：`physical_gd(q_init_flip,T_pose[0][3],L,include_joint_limits,q_solution,IK_counter,IK_time)`。原 KDL body 与完整源文件在新 stage 的 preserved_originals 原字节保存；kernel/options/限位/收敛门/单位不变。不能将此 physical-NR 数值重建标为作者原 KDL 数值实现。

原 CBiNR 没有 active role 或解析 branch。NN comparator 的原完整 body 仅返回全 12 维 `si_->distance(a->state,b->state)`，不加入 PCS 的 H break 或 D qa/qb 修复。原 growTree mode1/mode2、100/500 iteration、原 q 中点与 GD/RBS/reconstruct、Range、退一 parent 后真实 connectionPoint、原双树与随机控制流均保留。Transform 对 distanceFunction、原 GD seam、state/vector project、RBS、reconstruct、growTree、save、collision/mesh 加原完整 body lambda 的只读进入/返回观察；逆变换须逐字恢复全部原始文件。只有 `std::remove("./paths/temp.txt")` 改为保留原 temp，属于 I/O 偏离。

Observer 不调用 FK/IK/NR/碰撞/RBS/RNG，不重算任何数值，不读取 PCS branch/role 字段。记录实际 Motion/state 身份，等 q 不合并；原 CBiNR 只在最终 freeMemory 删除树对象，快照期间没有 SBL 式删树地址复用。原低层 p4pcs trace 在 plain/trace 均关闭，同一不变 numerical kernel 执行；新 p4cbnr trace 只包原函数，plain 未观察内部不可推断为零。

Driver 仅为未来单次 II/seed7/range2.6/solve10 保存入口：原 main sampler box（含 q6 ±3.1416）、always-true callback、NR 原 resolution .1、原两树 NN、无 smoothing 保持；一次 setSeed(7)/srand(7) 在所有 OMPL 对象之前。所有 constructor/setup/solve/getPlannerData 日志都在 Redirect 作用域进 stderr，stdout 只一个完整 JSON，避免重复 S01 setup-preamble 接收错误。仅原 `./paths` 新输出目录，原 false/partial/path/temp 全留。未来仅 source EXACT 候选可触发另冻的全原 M 独立路径门；工程编译不执行此入口。

本工程拟单目标最多 45 秒墙钟/90 秒 CPU，仍受原 R2 3600/7200 总帽；不新增 VI 或正式规划预算。源码生成阶段没有具体 protocol/prior/claim。冻结时必须消费最新权威 charged ledger 的全部真实 execution 集合，并逐 SHA 核所有外层人员独立成本证书；外层成本只替换内部样本一次，历史末尾未测成本 UNKNOWN。此 PRE 已知最新 V18 为 36 execution、charged 685.555705375994 wall/542.4289229999999 CPU、ledger SHA `a23faa25bf526276224ada5dd23bd394b896017064e19f499d13a685e8ad46c3`；代码现场选择最新版本，不写死旧总账。发现孤立 supervision charge 时必须先补账，不能跳过。

工程通过独立静态审查、root 冻结和源码/协议提交后，唯一由外层 supervisor 执行 `/usr/bin/time`→该 builder→一个 g++ 进程组。O_EXCL time FD、真实父 PID/argv/inode 证明沿用近期已经审查的完整边界；time 计入 import/preflight、拷贝/转换、compiler及其已回收后代、hash、日志/execution/receipt 持久化和退出。Decimal +.01 wall/+.02 CPU 上界须满足 45/90 和累计帽，不能只用旧内部 own 样本宣称费用通过。Supervisor 自身 journal/fsync 范围外披露；execution/charge 的 external_supervision_qualified 仍 false，须由真实人员独立保存 POST 确认。

内部监视 own+reaped+live compiler group CPU；Popen 前短暂屏蔽 alarm 到登记完成，设置独立组与单进程 CPU90 硬帽，失败保留部分编译日志并 kill/reap。清理先关闭 timer；全部旧资产/新 source/mesh/原件和最新 prior 最终逐 hash 核对，异常/预算超帽只能 STOP。没有重试、reset、覆盖旧 stage 或自动运行 binary 的分支。工程 manifest 的 BUILT 状态仍须与实际 execution/receipt/外层独立证书共同满足，不能单独打开科学入口。

后续只在工程实际通过并独立保存审查后，另冻结一次 II/A01/seed7/原10秒 solve 的整体候选（拟30wall/60CPU），完整双树/原 M/失败/raw/EOF/退出保全；再对完整真实保存 M 单独冻结最多2048节点/120wall/240CPU的独立数学/机械限位/v3 aligned离散碰撞检查，不补构造、不截尾、不换 seed 或放宽门。两项尚未由本工程授权。端到端资格后才做成本 pilot，再申请正式大规模；不提前 P2/Isaac 或完整论文结题。


## V2 工程静态审查修正（不改变科学 body 或预算）

V1 两项未通过静态审查均保留：未显式绑定四个实际 Boost `.so`/新增传递头；清理后没有实际 compiler group snapshot。实现者已在 `work/preserved_cbirrt_nr_build_v1_before_independent_static_fixes_20261016/` 原字节保全原六稿，manifest SHA `597703d8f5b59e8e7ab657d6f29591064b4321632530ed88597ec6f0b2558320`；独立审查者另保全 `reports/p4_full_audit/recovery_tools/cbirrt_nr_reviewed_v1_snapshot/`。本次仅 builder 和本 PRE 变化，supervisor、transform、observer、driver 仍为 V1 原字节；不将 V1 失败改写成通过。

V2 显式按本命令 `-L/opt/ros/humble/lib/x86_64-linux-gnu` 后系统目录顺序选择 filesystem/system/serialization/program_options 四个真实 Boost 链接 `.so`，同时保存符号链接路径和解析后目标内容 SHA。完整绑定小型 OMPL/KDL 头命名空间；Boost 冻结范围为来自这些命名空间、已有绑定数值头及实际本地源码的递归 literal/macro-literal 路径闭包，并保守绑定 MPL preprocessed 和 preprocessor iteration/detail 支持目录。此静态闭包不宣称能推导任意动态 macro include；实际依赖由唯一未来真实编译的 `-MD` 副产物核实，不新增 `-M/-E` 或其他 compiler 进程。

单次 g++ compile-and-link 的六个 TU 各自必须产生 `BINARY-<TU-stem>.d`，不共享会相互覆盖的单个 `-MF`。保留六份完整原始依赖文件及 SHA，要求每份清单含其实际 TU；所有实际依赖清单逐项保存 SHA。我们源码/派生 stage、既有数值核心/Eigen/json、OMPL/KDL/Boost/PQP 的实际依赖必须属于冻结 bound manifest 或由已冻结 transform 得到的本 stage 源码/header manifest；任何缺失或 SHA 不符只可 STOP 并保留，不允许运行后补清单冒充该次通过。通用 libc/libstdc++ 等系统头保留实际依赖清单/SHA，并绑定 g++11/cc1plus/as/ld 及 `/etc/os-release`/uname 环境指纹；本门不宣称完整操作系统逐字节重建，不泛绑整个 `/usr/include`。新增扫描、hash、六份依赖输出与最终核查全部仍计原45wall/90CPU及既定外层边界，超帽原样 STOP。

清理现在独立保存清理前和 kill/wait 后实际 `/proc` compiler process-group 成员及后次观察时刻，要求真实 reaped 且后次 group 为空；扫描/kill/wait/后次扫描任何异常均只可 STOP。编译失败后的 orphan descendant CPU 若不能由现存 GNUtime 已回收后代链证明完整覆盖，后审必须保留 UNKNOWN；after-group 为空不能单独证明成本完整。正常成功的 g++ 回收后代链另由真实人员独立 POST 审查。以上修正尚未运行 builder/import/describe/protocol/prior/claim、C++ 编译、binary 或任何科学调用。
