# P4 R2 环境IV：原wrist-only固定100目标数学资格 PRE v2草案

2026-10-16（Asia/Shanghai）。**未冻结、未执行、未编译；本文件只供根代理和独立审查者审查。** 旧v1 runner、配置、PRE与PRE_REVIEW四文件原字节保留。新v2仅刷新真实R2逐execution账目与来源绑定、增加已有live process-group CPU硬帽和最终保全超帽不得通过的工程守卫；固定科学设计保持原样。

## 恢复状态与当前授权解释

旧v1草案在ABB PCS LOCAL01期间准备，绑定V4的15execution（14科学+1工程）；未创建IV wrist run或claim，未执行100个目标。当前普通ABB PCS/NR局部与首条空间路径已有新实测，旧v1的prior匹配应当失效，不能使用旧余额直接运行。新v2须绑定根代理新V8账和当前全部25份execution（20科学+5工程）的自身wall/CPU及SHA；若增加任何execution，已有candidate必须重新生成，不能静默沿用旧prior。V8尚未落盘时不生成可运行candidate。

用户明确要求RSS与PCS/NR解耦推进、按D079继续其他环境和算法资格。该项是此前已准备的**原IV唯一腕部模式数学核验**，属于既有版本化资格范围：不改变奇异集合、概率、几何、阈值、固定输入或800分支分母，不创建新RSS方案，也不追加VI构造。本项原30秒wall/60秒CPU计R2总3600/7200秒一次，旧v1未消耗此项预算，因而不存在重复执行。根代理需先完成审查、冻结且提交源码/配置，再决定唯一运行；本PRE本身不代表已执行或授权新的科学设计。

## 科学问题与最低充分证据

问题：原作者环境IV `ckcComau2@80089340f0f1f6822e5b2821a63c998b6ae0413f` 的 `sampleSingular` 实际固定 `sMode=1`、仅令被动arm2的q5=0时，是否存在真实passive Jacobian秩下降、原限位内、闭链且原解析分支身份可信的active arm1根。完整记录固定100目标×8支，若0个合格目标同样保留结论，不能换输入、换模式或换阈值。

原作者 `validity_checkers/StateValidityCheckerRSS.cpp:260–307` 的arm2掩码为 `{1,1,1,1,0,1}`，加角全0；其碰撞/checkEE条件实际被注释。原 `proj_classes/apc_class.cpp:425` 的 `IsRobotsFeasible_R2` 构造 `T1*=T2·S·Q^-1`，与本固定数学候选一致。此项只验证该数学组件，**不执行原sampleSingular循环、rand采样、随机挑根/拒绝重试分布**，不称原RSS全局运行通过。

输入沿用R1原 `results/p4_full/20261014T1545_R1_COMAU02/IV_native.jsonl`，SHA `3ae03596a6e5e52ba9e4c5b99fa10e61c713dcb9741860c7064563e4ca87b2f6`。完整取100条 `fk_sample`，sample0…99、原行号、含原换行的行hash、q12和arm2六角均冻结。只改q5（零起index4）为0，其余五角binary64原值不变。原seed20261014、effective20265014、std::mt19937_64只作来源，不重新调用RNG或重生成样本；每目标branch0…7升序，共800个唯一固定请求编号。

## 原模型、解析版本与数学判据

Comau九参数 `[344,524.5,199,1250,186.5,210,1250,116.5,22]` mm、原基座 `[-3000,0,0,0]` 与 `[3000,0,0,-3.1416]`、抓持Q=Tx1800mm、S=diag(-1,-1,1,1)保持。原角界degrees `[−180,180], [−60,125], [−90,75], [−2700,2700], [−120,120], [−400,400]`乘原3.1416/180；不wrap/lift、多圈q4/q6原代表保持。真实闭链为 `T2=T1·Q·S`，不交换S/Q，不用数学π改物理yaw/界。

仅复用已存在且已R2实测的 `build/p4_full/20261015_R2_SPATIAL01/comau_iv_batch`，SHA `acb44b837629fb8d822c4a238ab5014f78fd594dd1eb2e075015645e7370882a`。绑定原作者commit、staged APC/header/def、patcher、batch driver、manifest及 `results/p4_full/20261015_R2_SPATIAL01/comau_iv_staging.json` 的原exit0构建命令（-DP4_MODEL=4），不重编。保留stage原 `STAGED_NOT_COMPILED_OR_QUALIFIED` 历史字段，不拿该字段代替真实构建记录或R2资格。R2已审的signed radial、full quadrant、原编号branch恢复、腕canonical代表和截零修正继续明确标RECONSTRUCTED，不能冒称作者原数值。

每个target一次独立passive FK/J生成T2、J2和原target；每个有限source-accepted根一次active独立FK/J，缓存pose/J用于全部诊断，避免重复模型调用。闭链及active目标回代位置maxabs≤1e-5mm、旋转矩阵maxabs≤1e-5；rank前三行mm→m、SVD相对门1e-6。保留每个谱、原IK标签与几何meeting branch_set，不强造奇异腕唯一身份。

G0为passive rank<6、闭链/目标回代和两臂原界；这是与旧700-target口径的可比列，旧失败不覆盖。G1另外要求passive rank=5、请求active标签属于独立几何branch_set、完整物理6×12闭链约束Jacobian rank=6。Jacobian复用已通过原physical_nr公式的缓存T/J：平移抓持skew、SO(3)log和左Jacobian逆，0额外FK、FD或NR。**所有100目标/800诊断完成、所有source-accepted根独立回代sound，且至少一个G1目标**，才给 `PASS_RECONSTRUCTED_MATH_ONLY`；前缀正例不能成为整体PASS。各G0/G1目标和分支分母分列。

## 预算、真实计数与停止

本项最多100固定目标、800 K派发；数学臂FK/J为100+A≤900，其中A为实际有限accepted active根；现有K内部每个finite accepted JSON已执行一次native FK，单独计A≤800，无显式F。数学started/completed和JSON完成逐项记录，内部真实K/FK started无hook仍UNOBSERVED；800上界、派发量和实际完成不能混同。0碰撞、RBS、NR、RNG、solve、VI构造；VI累计974/974余额0不变，时间余额不能换VI候选。

30秒wall/60秒CPU受R2总3600/7200秒约束。v2与既有NR资格相同，父进程RunBudget硬墙钟、每≤20ms检查自身+已回收子进程+活动完整进程组CPU，一线程，子进程中断保留stdin/stdout/stderr与原batch JSON前缀；finalization成本计入本次实耗，超帽或保全错误不得数学PASS。每目标完整8K是固定分派：若独立诊断中途soundness矛盾，该target其他已返回原生JSON仍保留，后续诊断与从未派发目标分别标UNKNOWN/未执行，不换根重试。

source-accepted非有限、target回代或闭链不闭合为soundness停止；普通不可达/限位/branch/rank拒绝记入固定分母。原输入、source/API、几何、界、gate或hash变化、进程异常和时间帽亦停止留证。新run/claim独占创建，旧claim/run存在则拒绝，不reset/retry/resume。同机制三修后按D079根因审查，不把0目标归咎于论文理论。

## 后续门与交付边界

数学资格不含任何碰撞、checkEE、RBS、完整RSS随机分布/跨branch/global planner或Fig/Table结论。之后若需要碰撞，须将**全部**G1根按原sample/branch冻结为独立完整清单，先可重复成本pilot，再报告预算，不挑首个正例，不重复查旧候选。本项不批准后续碰撞/规划、新科学采样设计或正式大规模实验。

新脚本 `scripts/qualify_p4_full_r2_iv_rss_wrist_fixed100_v2.py` 与新 `configs/p4_full/r2_iv_rss_wrist_fixed100_qualification_v2.draft.json` 的frozen=false、三review=false。旧四文件不改；新增科学循环 `fixed_inputs/rank_data/cached_closure/Qualification.fk/native/run/native_prefix_accounting` 与旧v1 AST一致。根代理与独立审查先核实输入/来源/最新账/工程守卫，然后提交冻结版本，才可唯一运行。当前仅AST、文件hash与describe/validate，0新科学/编译。

完整211项、Table I0/22500、500000投影、约50000点对、Fig.3–5/Table I–II及所有消融保持。P4仍部分完成，不P2/Isaac，不提前生成结题Word/PDF。

## 2026-10-16 冻结前最终元数据刷新

上文25prior/V8为本草案最初准备状态；其后H工程与唯一science已完成，旧v2 candidate已按预期拒绝。当前只将未冻结runner的四处账本/描述V8指针改为V9，旧runner/PRE原字节与SHA存work/iv_wrist_v2_v8_metadata_recovery_20261016；固定100输入、800编号、七个科学函数AST、模式/几何/判据和30/60帽均不变。最终候选另存qualification_v3.draft，不覆盖旧v1/v2。

真实V9为27execution=21科学+6工程，自身成本504.43514921199426wall/457.702161CPU；R2余额3095.5648507880057wall/6742.297839CPU。H原STOP/30UNKNOWN保留，本IV项不修补H，不新增VI。运行前必须由新describe绑定V9全部27prior并独立审查、提交冻结配置。
