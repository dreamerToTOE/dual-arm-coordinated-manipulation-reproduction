# ABB CBiRRT_NR 工程 v3：五个真实 PQP 头冻结 PRE 草案

2026-10-16。DRAFT_ONLY / NOT_FROZEN / NO_CONCRETE_PROTOCOL_PRIOR_CLAIM / NOT_BUILT_OR_EXECUTED。此稿只准备另版本工程构建，不执行规划器、模型、NR/IK/碰撞/RBS、随机采样或正式规划。原211项论文义务、VI974/974余0、Table I 0/22500、所有旧失败与UNKNOWN保留。旧BUILD01/02源码、协议、claim、目录、binary、日志、依赖、独立STOP/费用报告均不修改；原成功V20保全脚本仅保留不执行。

BUILD01真实失败仍为 `ONE_COMPLETE_MD_FILE_PER_TRANSLATION_UNIT_REQUIRED`，compiler exit0不通过工程。BUILD02解决了这项真实I/O证据缺口：原stdout 196455 bytes，SHA `0b7c5fc52ace8c9e0112b2cf4ca92624d7cbfcb61d635dab579aee2082b22084`，完整六规则、六TU各一次、六原raw切片、compiler exit0/reaped/after-group空/diagnostics空。但末门真实发现五个PQP头不在冻结manifest；execution SHA `dcc96bbef72e47e663e51eb2dcbe8ae8f1bb99cef1e31d5eabad17f056fe15df`、status STOP_PREFIX_RETAINED，termination `RuntimeError('ACTUAL_PROTECTED_DEPENDENCY_NOT_IN_FROZEN_MANIFEST')`。这是我们的工程资产绑定遗漏；不是symlink别名，不归因作者程序/模型/论文数学。不得将BUILD02改PASS、补其冻结清单或运行其未合格binary。

唯一新增绑定是实际 `compat02/PQP_v1.3/include` 的五个头。`PQP`仍解析现有真实路径 `/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3`，不修改几何或碰撞库：

| 头文件 | 冻结SHA256 |
|---|---|
| BV.h | 3861336bea7a475cb8dab1e64c95e749f7b14fe3ea2896b658b8c87839f8a213 |
| PQP.h | 4c35d6ac10e1518d84e3845fde918a308db904b740a2d8e04d627a1a58dd79c2 |
| PQP_Compile.h | e05dce007f2db29c5e75b2c1414569b615583d4a4c656b0dd6d00fc6eb7a0ea2 |
| PQP_Internal.h | 76fe69dcf588b0ba39d0fa75584265093a0f1310d405a8f7d60758c5dafb4c7f |
| Tri.h | da184954a2bcbabd69cbc63e9670ded5df76d733c8327208ca14723249827102 |

`assets()`还逐项读取BUILD02真实保存的全部743实际依赖SHA，以其原frozen+原派生stage映射重算原受管缺失集合，必须恰好这五个；加入固定五项后所有原受管依赖必须全有相同SHA。这是saved-only资产核对，不调用compiler/parser/模型、不泛绑wholeOS。BUILD03未来真实编译仍须独立重验全部实际依赖；旧清单不能预测新执行通过。真实新依赖若再缺失仍STOP并保全，不运行后补冻结冒充该次PASS。

唯一新run `20261016_R2_ABB_CBIRRT_NR_BUILD03`、claim `P4_R2_ABB_CBIRRT_NR_BUILD_3_45W_90CPU_20261016`、新目录 `/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_nr_v3/physical_nr_observed`、binary名仍 `p4_abb_cbirrt_nr`。只新增 `scripts/build_p4_full_r2_abb_cbirrt_nr_v3_draft.py`、matching supervisor及本PRE；所有新claim/stage/log必须不存在。原BUILD02三稿SHA分别 `b9b0274dec6f6c2ccb014f907e145619425e474b5b3a752423afe84834ec5c3d`、`4860db3c64b30650008ab3ad40d172f1b3c12f581e710ee20fafb1b9464a8be3`、`4683b3a1d6248e2d8b05aba6f1e951a65baf47b05fadd5dab747a82c7904312b`，必须保持原字节。新assets显式绑定BUILD02真实execution/recipe/claim、原own源码、全部run文件、原stage源码/mesh/原件/六切片/binary、raw与原失败，不能抹去第二次消耗。

原作者commit `909bd72fff778aca8682c96f9eb86ae4eb75557b`；完整科学source/transform/observer/driver与BUILD02完全相同。Transform SHA `07f5632ca92843b0be96ebece15cc8a64060768cdf4dc466242e176505a04c3e`、observer `74917caa8fab59821776617b44c119f57762153135e0c773bbc22dd180b190e4`、driver `65c95cdb2fe09e916a9f564baf01906901d80e136ccb48014c8ce9633b1bf0e7`。原KDL/SVC NR/collision/CBiNR full12 NN/双树/grow/RBS/回溯完整body、原geometry/mesh/基座/限位、唯一已资格physical-GD seam均不变；继续RECONSTRUCTED，不冒充作者原KDL数值实现。无PCS H/D、active role、解析branch、概率或SBL projection改变。

唯一真实g++仍 `-MD -MF -` 同一driver六TU编译链接一次；C++17/O1/g0、库/优化/flags不变。依赖parser、protected门、raw原字节offset/SHA、六TU distinct/各一次、exact binary target、Make转义/禁止未知输出、明确非compiler原生六文件的派生切片及前后SHA全沿用BUILD02已实际到达的源码，不重写解析基础设施。[GCC11官方预处理规则](https://gcc.gnu.org/onlinedocs/gcc-11.1.0/gcc/Preprocessor-Options.html) 支持stdout依赖与真实编译副产物；旧BUILD01通用aux命名推断错误仍保留。compiler必须exit0/reaped/after-group空、binary真实SHA、全部受管冻结依赖通过才可BUILT；六规则存在不单独代表合格。

本v3工程另项最多45wall/90CPU、child CPU90硬帽，仍扣原R2总3600/7200。先将BUILD02真实失败和人员独立外层费用纳入最新V20或更高权威ledger、全部实际execution集完整后才可冻结；动态核账，不写死V19或预测值，不预生成protocol/prior/claim。前两次消耗不删除不重复使用。外层GNUtime完整计import/preflight、saved依赖/五头核查、stage拷贝/转换、唯一compiler及已回收后代、raw/解析/切片、cleanup/hash、manifest/execution/receipt保存和退出，+.01wall/+.02CPU仍须单项/累计帽通过；supervisor自身journal/fsync边界外披露，历史尾UNKNOWN保留。若超帽仅STOP，无自动增加预算。

exclusive time FD/真实parent PID/argv/inode、Popen登记短mask、own+reaped+live compiler CPU、timer先关闭、actual before与kill/wait后group强空、全部旧/新资产与prior最终SHA门均不变。失败orphan CPU若外层不能证明完整则保留UNKNOWN。无retry/reset/覆盖旧目录或运行binary。真实成功后仍须新的BUILD03人员独立POST，单solve草案将另存v3绑定该实体，BUILD01/02费用true绝不能打开规划入口；正式实验仍待端到端路径独立资格和成本pilot后预算审批。
