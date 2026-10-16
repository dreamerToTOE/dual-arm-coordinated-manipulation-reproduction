# P4 R2 IV fixed100 wrist数学资格：独立静态PRE审查

2026-10-15。审查时HEAD `67f007126fddd7ad18229eb360efda2b5684e903`，工作分支 `p4-full-reproduction-pcs-study`。本审查只读取源码、配置、原始保存字节、已有构建记录及账目，新增本报告；**新FK/J、IK、碰撞、NR、RBS、RNG、solve、编译及科学run均为0**。未导入或运行待审runner，没有改动其绑定文件。

结论：**`STATIC_PRE_REVIEW_PASS_FOR_ROOT_FREEZE`**。未发现阻止本次固定数学组件资格的源码/API/输入/账目问题。此结论不是科学通过；当前配置仍为草案，`frozen=false`、三项review均false，且run目录与claim均不存在。父任务须确认本报告与V4账目，将同一协议明确冻结、提交所有执行绑定源码/PRE/配置，然后才可单次运行。若在此之前又有新的R2 execution，现有配置会拒绝匹配，必须更新prior并再确认，而不能沿用旧余额。

## 1. 审查对象与字节绑定

| 对象 | SHA256 |
|---|---|
| `scripts/qualify_p4_full_r2_iv_rss_wrist_fixed100.py` | `600ca71fe2056a7ced3ca796cadbcf92e51a6b6ad533cc668955b1d461cd404d` |
| `configs/p4_full/r2_iv_rss_wrist_fixed100_qualification_v1.draft.json` | `9f898ec5068a39151352b4397f9dc2df2a4354498043b599d45543a834249774` |
| `reports/P4_FULL_R2_IV_RSS_WRIST_FIXED100_PRE_DRAFT_20261015.md` | `31126e0b061531c4dff5958ca572d4a85153e5b087a7f4738f0dcaf94575081f` |
| 既有 `comau_iv_batch` | `acb44b837629fb8d822c4a238ab5014f78fd594dd1eb2e075015645e7370882a` |
| R1 IV原始输入 | `3ae03596a6e5e52ba9e4c5b99fa10e61c713dcb9741860c7064563e4ca87b2f6` |

用纯标准库读取/标量检查独立核对配置全部41项绑定哈希，41/41一致；AST仅作语法解析。没有调用`--protocol`、模型函数或子进程二进制。草案生成/校验函数的执行前条件也按源码逐项检查，不将静态检查冒充真实调用测试。

## 2. 真实作者路径、坐标及API

外部原作者 `ckcComau2@80089340f0f1f6822e5b2821a63c998b6ae0413f` 的 `sampleSingular:260–307` 固定`sMode=1`，arm2仅令q5=0；碰撞/checkEE条件实际被注释。待审程序准确保留该唯一模式规则，但输入是已保存R1原界uniform数组，并不是作者`rand()`采样/随机选根/拒绝重试的分布复现，已明确标为`RECONSTRUCTED / FIXED-MATH-COMPONENT`。

原`IsRobotsFeasible_R2:418–430`使用`T1*=T2·S·Q^-1`。runner构造`p2@FLIP@inv(grasp)`相同；物理闭链复验为`T2=T1·Q·S`，其中S自逆，不交换S和Q。Comau九几何参数、两原基座、原3.1416物理yaw/角界、1800mm抓持均保持；q4多圈与q6原值不wrap。q5之外五角逐值保持，`apply_mode(COMAU,1)`须等于冻结数组。

旧`comau_iv_staging.json`保存的构建命令明确为`-DP4_MODEL=4`，链接现有`spatial_batch_driver.cpp`与绑定的staged APC，exit0；本次不重编译。旧stage中的`STAGED_NOT_COMPILED_OR_QUALIFIED`是保存的阶段字段，不能替代该构建exit或R2已有实测记录。

driver对Comau接受argv `binary NEW_OUTPUT_FILE`，无需ABB的`--env`；stdin的`K 1 branch T16`中arm1与branch0…7正确，16矩阵元素按row-major和17位有效数字传递。driver返回每请求一行、对应`input_line=1…8`及原target；runner核对类型、型号、arm/branch、目标和error，核对stdout与独占新输出逐字一致。既有K若源IK返回true，会取原6维解并额外做一次native FK，然后才输出JSON。没有显式F调用。

Comau原branch shoulder0…3/4…7、elbow符号`(+,-,+,-,+,-,+,-)`、wrist符号`(+,-,-,+,-,+,+,-)`与独立branch_set口径一致，奇异零因子保留meeting set，未强造唯一标签。源IK数值修正与canonical奇异腕代表沿用既有R2版本，不加周期lift、替代根或NR fallback。

## 3. 固定分母与数学门

独立逐条核对100条原`fk_sample`的行号、含原换行的行哈希、12角、arm2六角、forced六角及sample0…99顺序；全部一致。800个`IV_sNNN_bB`请求编号唯一且按sample后branch升序。模式未按成功筛样，所有原始角和失败均保留。

每个已启动target仅一次passive物理FK/J；每个有限accepted active根仅一次active物理FK/J。缓存用于回代、闭链、active/passive秩及6×12物理约束Jacobian，因此完整运行数学调用为`100+A≤900`，不是重复调用`residual_metrics`或`closure_vector_jacobian`。`cached_closure`的平移块、抓持偏置skew、SO(3) log及left Jacobian inverse，与`physical_nr.closure_vector_jacobian:123–134`逐项相同；本审查没有执行新的数值Jacobian检查。

位置maxabs≤1e−5mm、旋转矩阵maxabs≤1e−5和秩门1e−6均保留。秩的前三行mm→m；G0为passive rank<6+物理闭链+原12角界，G1再要求passive rank5、请求active标签属于独立branch_set、完整物理约束rank6。至少一个G1目标、全部source-accepted根独立回代sound且全部100/800诊断完成，才可给数学组件正例门PASS；即使有早期正例，中断前缀也不会被标整体通过。所有800条分支与100目标分母须分别报告。

## 4. 预算、冻结与保全

15份prior execution与V4账本逐份哈希/自身wall、CPU一致，目录清单精确相等：14 science+1 engineering。纯标量`math.fsum`复核wall=`285.28806236599576`秒、CPU=`264.43608`秒；未使用cumulative字段再次累加。工程成本保守纳入R2，但没有当成科学成功。

本次帽为30秒wall/60秒CPU，扣既有R2总3600/7200一次，不扣VI候选。VI B明确974/974、候选余0；无新VI构造，也不因余下时间重新开候选额度。

执行校验只允许frozen/reviews/readiness三个冻结字段与描述草案不同，其他字段、输入和所有绑定哈希须完全相等；执行时要求frozen=true、三review全true、readiness=`FROZEN_REVIEWED_READY`，并要求SOURCES及协议已跟踪且无未提交变化。独占`new_json(...,'x')`创建固定claim，结果目录拒绝既存，native输出也用O_EXCL。没有重试、resume或claim重置路线。

source-accepted非有限/独立回代不闭合、来源/接口变化、进程异常或时限触发均停止并保留前缀；没有先删失败再重跑。常规解析false、界/branch/rank拒绝留在固定分母内，不因此改输入。每target八K一次派发意味着当前target的全部已返回JSON可能先于独立branch诊断停止，原生输出和target均有独立保存。

## 5. POST必须保留的解释边界

- `external_K_dispatched`是接口派发量；合格保存JSON行给出`external_K_JSON_completed`，不能由800请求上界推断实际启动/完成。`native_accepted_FK_observed`仅计finite accepted JSON证明已完成的内部FK路径，不代表所有可能已启动的内部FK。两项内部真实started保持`UNOBSERVED_NO_NATIVE_START_HOOK`。
- 中断后须用已保存dispatched ID、JSON-completed ID及uncompleted diagnostic ID作集合分解，分别报告已派发未确认、已返回未诊断、从未派发尾项；它们不能被混记成解析失败/超时。runner保存的集合足以无新模型调用地重建这三类。
- G0/G1是固定数学组件资格，碰撞、源checkEE、RBS、普通RSS随机分布、奇异集完整性、全局规划及方法优势均未执行，不能由数学正例外推通过。
- 数学完整通过后再冻结全部G1根的完整碰撞清单，前缀成本测量须复用实际结果，不能挑首个成功根或重复花同一预算。当前审查不批准后续碰撞/规划计算，也不改变211项义务和正式Table I 0/22500状态。

本报告为新增独立审查记录，原PRE、原失败、旧700目标、R0/R1及全部历史数据字节不改。父任务负责把本审查结论、实际冻结/执行状态及此后的新账目写入主记录；本审查没有科学结果可登记。
