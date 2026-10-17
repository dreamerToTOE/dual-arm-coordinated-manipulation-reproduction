# RSS 固定32草案静态补充：计数、秩与未完成工程

草案维持未运行、未冻结。本补充不修改既有runner/协议/PRE或任何科学输入；本轮优先SBL工程，不为赶进度运行RSS。

`recover_p4_full_r2_endpoints.branch_identity` 静态函数体仅 `math.atan2/sin/cos/hypot`、`sign_or_unknown`、branch列表枚举与布尔判断；内部没有FK、IK、J、碰撞、采样或项目模型调用。其直接导入模块及两个几何oracle的顶层只有Path/sys.path准备、常量和np.diag，不执行main或模型函数。依赖导入本身有时间/内存成本，仍须计入未来外部监督。此判断来自AST/源码阅读，未import。

独立arm FK/J上限40=4原输入×两臂8次 + 至多32个成功IK输出×被动arm2一次。branch_identity不会增加40这个上限。rank SVD上限36=4个原arm2+最多32输出。所有J为独立elementary-transform的真实6×6几何Jacobian，平移行先除1000（mm→m），角速度行不变；`rank_relative=1e-6`，数值rank=#(sigma>sigma_max×1e-6)，与原RSS_CONSTRUCTION的既定门一致。rank<6是该尺度阈值下的数值降秩证据，不声称精确符号秩证明。原branch集合零因子门64×binary64 epsilon与rank门用途不同，不互相替换。

以下是阻止直接执行的工程缺口：

1. launcher当前仅是未制作接口，runner检查receipt.parent_pid不足以证明唯一GNU time/worker链、真实process-group生命周期、外部退出码、退出后空组和未触达额外子进程。必须复用已合格外部一次性监督方式，核父/祖父PID+start_ticks+唯一request/协议SHA/命令，持有原始GNU time输出并在worker结束后做空组检查；真实外部上界覆盖导入、调用与落盘。
2. 当前alarm贯穿finally；到限后的SIGALRM可能再次中断证据落盘/子进程清理。最小修正是finally入口先关闭worker内部alarm，将清理收尾交给已冻结外部硬上界；逐阶段捕获清理错误、保留counts/未完成列表，先kill/wait/reap后写最终执行与durable receipt。不能靠停alarm扩预算；必须在同10/20内预留清理尾额或由监督提前停止。
3. 36个短进程和逐row fsync的wall尾尚未实测，历史5600记录1.50秒不证明新结构10秒内完成32。若维持当前结构，到限保留前缀而非重试；如改为每环境单个持久会话减少启动，必须先独立审查唯一固定请求流/EOF/实时原字节/partial计数，不追加IK或换点，不能临时为了通过预算更换结构。
4. 既有F/K kernel只有完整行response，没有内部FK/J trace。K成功返回证明其内部FK已完成；中断K的内部FK起止必须UNKNOWN，不能把32上限当实际值。若需要逐内部起止，另做最小观察工程review/build，原计算/分支/输入不变，并单列工程成本。
5. 当前 `finally` 保全还缺对hash收尾异常、signal关闭和execution持久化失败的独立receipt路径。最小修正同现有监督模式：每个不可变源hash可验证但失败只记错误，不跳过后续reap/receipt；目录与receipt fsync有外部证明。此工程未实施。

下一步仅是主代理独立审查后决定采用哪一项最小监督修正，再产生版本化新草案；当前原草案保留。数学门、原32输入、原branch/限位/闭链/秩阈值、0VI/0RBS/0solve/0sampling和collision另门都不变。

- `scripts/qualify_p4_full_r2_abb_rss_branch_fixed32_draft.py` SHA256 `9ef810d81bc87bb670dc68baefcbaf7974abd926655817e428c4ed6b661c585a`。
- `configs/p4_full/r2_abb_rss_branch_fixed32_math_v1.draft.json` SHA256 `1bea1b060542c1ef6f478581817e1dda963622600bd9ad3119c99616601da656`。
- `scripts/recover_p4_full_r2_endpoints.py` SHA256 `4723c08f33a85e4ea85d9067544979d222212c588c82d004934b293253bb555f`。
- `baselines/p4_full/abb_independent_oracle.py` SHA256 `573af526968476f8b41b94b2ead5a555b45874eae6b080255e03c8aba489b075`。
- `baselines/p4_full/analyze_comau_native_qualification.py` SHA256 `58e320d64f945f2c913a571a936b7203508c9e5494cedc56aeec8e479cd8d321`。
