# ABB CBiRRT_NR 工程 v2：真实依赖 stdout 恢复 PRE 草案

2026-10-16。DRAFT_ONLY / NOT_FROZEN / NO_CONCRETE_PROTOCOL_PRIOR_CLAIM / NOT_BUILT_OR_EXECUTED。只准备另版本工程构建，不执行规划器、模型、NR/IK/碰撞/RBS、随机采样或正式规划。原 211 项论文义务、VI 974/974 余 0、Table I 0/22500、所有旧失败/UNKNOWN 保留。

BUILD01 已真实执行且必须保持失败：`20261016_R2_ABB_CBIRRT_NR_BUILD01` execution SHA `a6f84e38ecef47649d9dc12cf7316a9ebc68429e6b126bd6cc1b23e4845d8b4d`，status STOP_PREFIX_RETAINED，termination `RuntimeError('ONE_COMPLETE_MD_FILE_PER_TRANSLATION_UNIT_REQUIRED')`。compiler exit0、已回收且 after-group 空，不足以通过该工程门。实际只留下 `p4_abb_cbirrt_nr.d`，SHA `05621e65d40d89bccbacac84cdefd03aa9adc69fcede097545ced2dcd33e5538`，内容为最后 CBiRRT_NR TU 的依赖；此前静态引用通用 auxiliary 命名推断六份默认 `.d` 的判断错误，已被真实结果推翻。责任属于我们的工程实现及静态审查，不归因作者程序、机器人模型或论文数学。旧六稿、冻结协议、claim、外层费用/独立STOP POST、旧stage、binary、唯一.d、完整compile日志均保持原样；不向其补造缺失依赖，不改PASS、不复用claim，也不运行该未合格binary。

GCC11具体预处理文档明确：`-MD` 在存在 `-o` 时以其参数改后缀 `.d` 定义默认依赖文件；`-MF` 覆盖该默认，参数 `-` 则写 stdout；`-MD` 不隐含 `-E`，依赖为真实编译副产物。[GCC11.1官方预处理选项](https://gcc.gnu.org/onlinedocs/gcc-11.1.0/gcc/Preprocessor-Options.html)。[GCC11.1 c-opts.c](https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-11.1.0/gcc/c-family/c-opts.c) 中 `deps_file == "-"` 直接选 stdout，命名文件才 fopen；[GCC11.1 mkdeps.c](https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-11.1.0/libcpp/mkdeps.c) 保存每主TU完整Make rule及续行。这些只读源码依据支持本恢复设计，不代替下次唯一真实编译的实证门。禁止 `-MP` 伪规则、不调用 make/eval。

唯一新工程 run `20261016_R2_ABB_CBIRRT_NR_BUILD02`，claim `P4_R2_ABB_CBIRRT_NR_BUILD_2_45W_90CPU_20261016`，新build目录 `/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_nr_v2`、stage `physical_nr_observed`、binary名 `p4_abb_cbirrt_nr`；所有新目录/claim/日志必须不存在。仅新建 `build_p4_full_r2_abb_cbirrt_nr_v2_draft.py`、matching supervisor 和本 PRE，不修改 BUILD01 的六稿。原作者 commit `909bd72fff778aca8682c96f9eb86ae4eb75557b`、原 KDL/SVC NR/collision/CBiNR 完整body、full12 NN、双树/RBS/回溯、既有physical-GD seam、mesh/几何/限位/收敛门/原sampler界/原resolution均不改。

三个科学源码仍逐字绑定已提交版本：instrumentation SHA `07f5632ca92843b0be96ebece15cc8a64060768cdf4dc466242e176505a04c3e`、observer SHA `74917caa8fab59821776617b44c119f57762153135e0c773bbc22dd180b190e4`、driver SHA `65c95cdb2fe09e916a9f564baf01906901d80e136ccb48014c8ce9633b1bf0e7`。Numerical kernel仍唯一已Q1/local/RRT_NR资格的原文件；重建GD继续标RECONSTRUCTED，不冒充作者原KDL数值实现。无PCS H/D/role/解析branch设计，无SBL projection改变。

唯一未来 g++11 命令只将依赖 I/O 改为 `-MD -MF -`；同一driver仍编译原六TU并链接一次，flags仍C++17/O1/g0/Wall/Wextra/pthread。compiler stdout以独占新文件 `compile.stdout` 完整保存，stderr另存，不与日志拼接，不开第二个compiler/-M/-E探测。compiler必须实际exit0/reaped、binary真实存在且保存SHA后（或已完成编译时）解析raw stdout；即使编译出错也可能有依赖输出，所以六规则绝不单独代表编译成功。

依赖门要求恰好六条完整逻辑Make rules；所有物理行LF完整、续行完整、每字节完整属于一条原raw片段，不跳过未知stdout/空白行/额外规则。专用字节解析器处理GCC Make反斜杠转义的空白/#/colon/backslash和双美元，不使用shell shlex、变量展开或执行依赖文本；未支持/未闭合转义、未转义comment/变量/控制字符只可STOP并保全。每条恰好一个target，按固定cwd解析后必须为实际新BINARY；target可在六规则重复。第一prerequisite必须为六个冻结TU之一，六源各恰好出现一次、无漏项/重复，不能依默认.d名字猜覆盖。

保存完整stdout bytes/SHA/路径、逐rule原raw byte offset begin/end、raw长度/SHA、真实target、TU和完整依赖清单。为审查可写六份 `dependency_stdout_slices/<index>_<source>.d`，但每份明确标 `compiler_created_individual_d_file=false`，且必须逐字等于stdout对应切片；它们是派生证据，不声称compiler直接生成六文件。原raw继续为证据源，切片前后SHA都检查；任何规则不完整或切片不一致仅STOP。

四个实际Boost `.so` 按本命令-L后系统目录选择并绑定链接路径/解析目标。继续完整OMPL/KDL小型头命名空间、实际Boost静态literal/macro-literal闭包与支持目录、既有Eigen/json/PQP/数值核心/全部本地源码绑定；动态macro include不凭静态推断通过。六TU实际所有受管依赖必须属于冻结bound manifest或由冻结transform派生的本stage源码/header manifest，SHA须匹配；缺一只可STOP，不能运行后补冻结冒充本次PASS。通用libc/libstdc++系统头保实际清单/SHA、compiler/OS指纹，不泛绑全/usr/include，也不宣称完整OS逐字节复现。

本v2工程新项最多45wall/90CPU、child CPU90硬帽，仍扣原R2总3600/7200。BUILD01费用不可重复使用或抹除；只有失败账与真实人员独立外层费用证书被最新权威V19或更高ledger覆盖全部真实execution后才可冻结。不写死旧V18总额，不预生成prior/protocol/claim。外层GNUtime边界计import/preflight、旧证据/依赖hash、stage拷贝/转换、唯一compiler及已回收后代、stdout/规则解析/切片、final hash、manifest/execution/receipt保存和退出；+.01wall/+.02CPU后仍须满足单项及累计帽。supervisor自身journal/fsync边界外明确披露，历史未测尾UNKNOWN保留。若新依赖I/O核查超帽同样STOP，不自行加预算。

沿用已审查的exclusive time FD/真实parent PID/argv/inode、Popen登记前短mask、own+reaped+live compiler-group CPU监视、timer先关/消费pending、实际before与kill/wait后group扫描、后组强空门，全部旧资产/新源码/mesh/原件/派生依赖切片/prior最终SHA一致。失败orphan CPU若外层不能证明完整则保留UNKNOWN，空组本身不替代成本资格。无自动重试/reset/覆盖旧stage或运行binary分支。真实工程通过仍须人员独立POST；single-solve草案继续等待新工程资格，不因BUILD01编译exit0解除其门。
