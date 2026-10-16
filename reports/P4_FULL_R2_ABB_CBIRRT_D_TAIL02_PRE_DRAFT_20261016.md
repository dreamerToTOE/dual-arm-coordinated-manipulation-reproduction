# ABB CBiRRT D_TAIL02 未派发两项资格 PRE 草案

2026-10-16。**STATIC_DRAFT / NOT_FROZEN / NO_PROTOCOL_OR_PRIOR_SNAPSHOT / NO_EXECUTION**。本文件只冻结待审设计；本次草案准备不导入runner，不创建协议、prior、claim或进程。runner为`scripts/qualify_p4_full_r2_abb_cbirrt_d_tail02_draft.py`，仅使用stdlib与保存的D64资产/传输辅助函数；不改原D64源码、协议、结果或作者binary。

## 原失败及本项边界

原D64唯一运行保持`STOP_FINAL_WALL_OR_CPU_BUDGET`：61项runner complete，62次真实请求及62个完整raw返回，原UNKNOWN始终为[61,62,63]；第62项index61只有完整raw和独立saved-only审计，不能补造原JSON、qualification或成功记录。原尾进程exit=-9，原完整raw门false，原固定15墙钟/30CPU项已停止，不能恢复或重新打开。

原失败保存证据为execution SHA`6e18068ea1ffad849c01faa377e5268fe892448029640feb4421c3c05941e140`；独立raw-prefix POST SHA`15fd13b857b663a46656600b1318d65c49aebcdf6785e1a3e660c47f5264917d`，510/510，支持62个保存返回的局部算术、state和30组plain/trace配对，不证明原单run通过。

本项不是D64重跑。仅派发原固定清单中从未派发的dispatch_index **62、63**，原request字节数值、case_id、role0/1、III环境及判据全部沿用。旧0..61只链接原raw及独立审计hash，不重新查询，也不重新生成旧qualification。新建1个D-fixed、III、trace的原CBi进程，继续使用实际BUILD01中的同一binary；源码、Comau/ABB模型、基座、抓持、几何、限位、碰撞与规划参数均无变化。本接口没有新FK/IK/NR/碰撞/RBS/solve调用，不扩正式Table I预算。

结果只允许独立标签`SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO`，不得映射成原`PASS_FIXED16_ACTIVE_DISTANCE_INTERFACE`。若本项成功，跨次事实是旧62+新2=64个真实dispatch，8+1=9个真实进程/CBi构造及9个**结构性**直接RNG成员初始化。不能声称原第8进程顺序历史被恢复；原D64 STOP、61 complete、UNKNOWN、-9及false门全部永久保留。

## 固定资格门与跨次审计

新进程仍由原driver在构造前setSeed(7)一次，不能每请求重置；每次请求显式设置原active_chain并写入完整12角OMPL state。原distance分支无随机采样；未hook的库内部RNG构造和seed-draw仍UNOBSERVED，不报0。新两项不是奇异/RSS候选，VI仍974/974、余额0。

独立版本化aggregate须对**全部64个保存真实响应**重新执行stdlib资格门，而非只查看新两项：16固定上下文、独立六关节L2绝对误差≤1e-12、D-fixed严格对角0、精确交换对称、role0跨源binary64相等、64份原输入state逐binary64保持、32组plain/trace非观测字段逐binary64相等、原source-control错误公式及四个唯一非零同点反例。内部runner沿用冻结context参考值；人员独立POST必须从原q重新fsum/sqrt计算全部参考值，不能只相信内部结果。观测字段归一化仍只去mode/source计数/trace，不删除实际输入返回或state变化。

每进程的construction metadata要求一致并只绑定一次；新两项属于第9进程，不能并入原第8进程。新stdout严格两条完整JSON行且无额外尾部，stderr完整保存，要求1个mesh_load及2个activeDistance各entry/return，原请求trace id每次重置为1。新进程必须EOF、exit0并全部reaped；旧8进程的原资格结论不改。跨次原raw trace事实为mesh_load5、activeDistance32各entry/return；32份plain内部body starts/completions仍UNOBSERVED。构造几何/PQP BVH不算碰撞查询。

任何错误、额外stdout、不完整EOF、trace差异、原raw/资产改变、新进程异常exit、超时或预算超限即STOP；不改两点、role、阈值、输入、seed，不补调，不新增claim或resume。本项完成后仍须人员独立saved-only POST核完整aggregate、supervision和全部绑定；L12未来版本必须完整验证此证据契约，不得以状态字符串OR跳过原门。

## 独立5墙钟/10CPU预算与终局费用

新诊断项上限**5秒墙钟、10秒CPU**，并扣原R2总3600/7200余额；原D64 15/30不重开。新source进程另有RLIMIT_CPU10，父20ms timer监控self+已reaped children+登记PID live CPU，最终超帽STOP。预算从execute入口起，包含preflight、唯一claim、真实请求、关闭回收、mandatoryhash和最终证据保存；协议生成不属于科学运行，但本草案未生成任何协议或prior。

Session由父持有后启动；实际Popen与PID登记之间短暂屏蔽父SIGALRM，子preexec恢复原mask并设RLIMIT10，父finally恢复mask后立即检查。该段无距离请求，但不把已exec源构造计成零。异常入口先关重复timer，父级对完整PID registry先kill、再drain和独立wait/reap。回收、保存与STOP尾部继续计费，任何未reaped或清理错误不允许接受。

为避免原每请求四文件durable保存的工程瓶颈，本项用一个独占append JSONL journal保存setup、events、固定请求、原stdout/stderr chunk的base64原字节、raw响应、资格结果和最终完整raw snapshots；每记录flush，journal终局一次fsync。唯一claim单独创建且fsync；execution和cost_receipt各只保存一次。不存在每请求省略原raw或丢弃失败的例外。若append被打断，原残行保留，终局另起边界保存完整可得raw快照，必须STOP，不能借快照修饰成功。

execution先记录已测own-cost并完成其最终序列化/fsync；随后独占`cost_receipt.jsonl`追加一条费用receipt，实测通过execution最终持久化的墙钟/CPU并绑定execution hash。**最后receipt自身序列化、flush、fsync和终端退出尾部仍有非零成本，内部receipt不能递归地测全自身，因此必须明确UNMEASURED。**内部SPLIT标签只表示内部固定门完成，`external_supervision_qualified=false`，不能单独作为最终科学资格。

具体外层入口为`scripts/supervise_p4_full_r2_abb_cbirrt_d_tail02_draft.py --protocol <冻结协议>`，源码及`/usr/bin/time`、`/usr/bin/python3`实际hash纳冻。supervisor在派发任何runner前以`O_WRONLY|O_CREAT|O_EXCL`原子创建新sibling `results/p4_full/20261015_R2_ABB_CBIRRT_D_TAIL02.supervision.time.txt`，以`pass_fds`传递已打开FD。固定time argv为`/usr/bin/time --quiet -f "%e %U %S %x" -o /proc/self/fd/<独占FD> /usr/bin/python3 <绝对runner> --protocol <绝对协议>`；不以普通`time -o <已有文件路径>`替代独占条件。元数据JSONL、stderr与最终charge各自独占创建并保留。

supervisor在Popen前持久化planned_launch，含协议/源码/程序hash、固定argv、supervisor PID及time文件dev/inode；Popen后记录真实time PID，wait后记录exit。科学runner在claim前读取该planned行，核实际父程序为绑定GNUtime、实际argv、父/祖父PID链、父time仍持有同一dev/inode输出FD，保存父PID及start ticks。独立POST核planned首行hash与实际time PID、argv、inode闭合。源构造数9专指9个原CBi源进程；外层supervisor/time是监督进程，不混入源构造/RNG计数。

独立POST须核外层exit0，墙钟两位精度上界elapsed+0.01≤5、CPU上界user+system+0.02≤10，并与receipt和execution一致；不通过即预算STOP。外层time覆盖内部execution、receipt最后fsync、preflight及进程退出；监督程序自己的日志写入不冒充科学子进程自身费用。即使preflight在claim前失败，监督time/charge仍保留、独占sibling阻止再次启动，实际费用不得消失。time结果不能解析时，保留外层wait墙钟和reaped-children CPU的有限观测；其完整性标UNKNOWN，不将其称为已认证upper，也不批准资格。

supervisor将time原始行、metadata、stderr、execution和receipt hash及有效上界写入独占`.supervision.charge.json`，本文件仍不自称人员独立批准。新的R2账目由root的`append_external_cost_snapshot_20261016.py`及独立POST按监督上界**替换一次**该项pre-save样本：保留原wall/cpu字段，另记charged_wall/cpu，不能double-count。本runner在本项冻结时仍只读取原V13全部prior，不增加通用监督框架。未来prior必须使用已审账目中的charged费用，并保留旧D64末端UNKNOWN，不再把内部pre-save样本称为精确全进程总费用。

## 冻结前交付

先只审本PRE、最小runner、具体独占supervisor、原62raw/独立审计的绑定策略与全部64门；旧claim必须与原execution before/after hash一致，不能将修改后的当前claim接受为新基线。两位无阻塞后，再由root授权生成实际D BUILD01 binary/mesh/库/旧结果/源码的绑定协议与最新完整prior；不生成placeholder。外层启动前仍需全部源码和最终协议提交且无修改、显式review冻结、唯一run/claim/监督sibling均不存在、无其他活动P4试验；内部claim前则要求相应独占监督文件和真实parent证明已经存在。结束后mandatory重hash全部bound、协议、claim及完整prior，全部旧失败和数据保持原样。

本项不证明PCS规划、RSS/RBS、连续无碰撞、全局优势或论文完整复现。211全文义务、正式Table I0/22500、原H失败/30UNKNOWN、既有PCS177与NR393离散路径保持；不进入P2或Isaac。当前准备阶段0科学执行、0编译、0claim、0protocol、0prior、0提交。
