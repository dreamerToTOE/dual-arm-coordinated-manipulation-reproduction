# D080 环境 V PCS 固定局部资格 PRE 草案（2026-10-18）

状态：草案，未 describe、未冻结、未执行任何算法 query。先等 V 首次编译的人员独立 POST 和最新实际账完成；root/独审确认本固定列表与运行帽后才另生成运行协议。本文件不授权运行。

=== PRE-TASK REPORT ===
Task: V PCS 固定 A02 中心、双角色投影、原 RBS 与路径重建局部资格的 transport 草案。
Scientific objective: 观察固定分支 PCS 投影及非平凡 RBS/重建在 V 箱体障碍环境中的实际行为，随后独立检查成功离散节点与叶距离。失败和依赖未执行如实保留。
Minimum sufficient evidence: 两新 binary 同一18命名请求；trace/plain 数学与返回值一致；全部原始流、递归/碰撞与箱体姿态观察、512总project帽；最多256唯一成功节点待独立资格。
Current scope: 只读已有 V A02 start/goal，不重复端点恢复；环境V，PCS，固定local API，无planner实例/solve。
Explicit non-goals: 原随机H返回修复、CBiRRT D、NR/RSS、正式规划/统计/性能、连续碰撞、VI/P2/Isaac/FR3全部不运行。
Attempt budget: 草案本次科学调用0。未来固定一次source-local提议30wall/60CPU，两source合计；512 public+internal fixed project、256独立唯一节点，仍受原R2累计3600/7200。独立oracle运行帽另冻，不能把它隐含在本source帽中。
Preferred method: 复用SBL local外层GNUtime和Budget/Journal/Session pipe/cleanup，只适配V一次argv协议的1条setup和18条请求结果（每binary合计19条JSON）。
Fallback method: 保全false、UNKNOWN、cap/transport失败及NOT_EXECUTED依赖；不更换节点、分支或阈值，不追加样本/自动重试。
Stop / escalation: 任意资产漂移、预算帽、源协议/账不完整、三次相同根因；新科学设计或扩额须请示。
Files expected to change: 新local runner/supervisor、固定fixture DRAFT、本PRE；不修改已审V driver/header/transform/builder或旧记录。
Validation plan: AST与固定列表形状/保存来源纯文本检查，复用219/101/合并工程证书；编译通过后另独审冻结。运行后的人员独立物理/分支/限位/碰撞/叶距离资格与预算另冻。
Known ambiguities / risks: 真实return及是否碰撞未知；30/60只为有限资格帽，非估计实测成本；driver不等待stdin，不能宣称观察了模型前实际loaded symbol；未证明连续路径。
Need user confirmation: no（已授权普通资格工程草案；实际执行仍等root/独审冻结，不引入新科学假设）。

=== PRIOR-ASSET CHECK ===
Current task: V fixed local transport。
Scientific algorithm remaining paper-derived: 原V四参固定IKproject、isValidRBS、checkMotionRBS、reconstructRBS；Comau CORRECTED APC与aligned-v3来源分别保留。
Old repository areas searched: 已有V driver/config、SBL local与setup生命周期、POST_TASK01_REUSE_MAP。
Pinned source commit: 旧工程631b1f65656d025c1bb2173e874192f3fe4d355a只作复用图参考；本次直接用本仓库已独审SBL基础设施，不导入FR3科学场景。
DIRECT_PORT: SBL GNUtime supervisor、Budget/Journal、非阻塞双pipe保存与Session.finish/组kill-reap。
THIN_ADAPTER: V一次文件协议启动，不发stdin；多行setup+18请求收集；V source counter归并。
TEST_ORACLE: 原A02 V端点文件、V219原体/pair静审；不把II成功证书用于V。
REFERENCE_ONLY: SBL科学fixture和ABB数学/规划，不移植。
Rejected assets: SBL loaded_scope依赖stdin等待门且检验无关random-linear符号，V无等待门，不能照搬后声称模型前验证。
Reused files: scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py、scripts/supervise_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py、V builder逐prior证书函数。
New files: scripts/p4_d080/qualify_v_pcs_local_v1_draft.py、supervise_v_pcs_local_v1_draft.py、configs/p4_d080/v_pcs_local_fixed_saved_v1.DRAFT.json。
Risk: 仅transport薄适配；源体、几何、抓持、87pair/8mm、RBS .05/150不动。
Need user decision: no。

固定fixture为原两个A02保存中心，每中心先一次identify；每role0/1分别只改变主动臂首关节−.05/+ .05rad，原另一臂角保持为中心输入；使用该中心对应identify的原branch，随后同role/branch的这两投影结果仅做一次RBS和一次reconstruct。每binary2identify+8project+4RBS+4reconstruct=18，trace→plain共36public。投影失败后对应依赖记NOT_EXECUTED，不替换端点或选择其它分支；无重采样、RNG或planner调用。

每binary project上限256（8public+最多248内部中点）；RBS或reconstruct各4root的二叉森林最多248内部点，递归条目帽500；identify2最多4FK/32IK，加project256得到FK260、IK288、specific256；内部collision≤248，原87pair给PQP21576；记录帽25000覆盖这些软件entry上界。两binary的project合计≤512；重建节点与成功project/isValid输出按binary64去重，最多256唯一节点排队独立检查，超帽停止，不丢弃超出节点或只验证前256。原阈值没有改变，调用帽是资源停止条件，不是算法通过判据。

runner只保存实际source结果并比较plain/trace，成功结果仍标 `SOURCE_FIXED_LOCAL_OBSERVED_PENDING_INDEPENDENT_POST`。原RBS不显式检全部端点关节限位，不能用source true代替独立资格；后续要验证所有成功投影/中点/重建离散节点的物理闭链、真实分支、原限位、原87pair碰撞与每叶normDistanceDuo<.05。箱体世界矩阵、TCP、全部pair API返回码和CloserThanTolerance布尔已由原观察稿保留，当前不重写碰撞。

复用原始V A02证书，不重复数学查询；失败原端点/重建偏差、native与aligned差异和CCD未知继续保留。当前固定fixture只从保存JSON读取12角并做±.05加法，未构造机器人或求IK。独立数学运行不是此次源码runner的隐含动作，后续另行冻结预算和实现。

2026-10-18工程兼容增量：修前runner/supervisor/PRE逐字保全于`work/preserved_v_pcs_fixed_local_before_monotonic_compat_20261018/`。外监督薄复用当前已审V BUILD的精确Decimal三观测包络，raw GNUtime独立保留，最终费用为raw/outer monotonic与reaped/内部receipt各加原.01wall或.02CPU后max；完整性失效不升级费用资格，原30/60及R2总3600/7200不变。prior直接复用固定SHA已审V builder的`validate_prior`，保留PATH01原STOP及一次历史raw charge例外，不重复计算prior算法。当前build独立POST必须已证明工程通过及新basis，核原execution、charge、receipt SHA；本稿不生成冻结协议。

静态输出合同明确：driver `argc==3`，argv仅binary/work/driver_protocol，无stdin请求。每binary先1条SETUP_COMPLETED，再按固定列表输出18条请求结果，共19条JSON；trace→plain共38条stdout与36次public_request。plain/trace两模式都保存相同JSON records，trace模式仅多stderr观察行；依赖失败仍占原命名请求行，保留NOT_EXECUTED，不替换分支/节点。固定fixture、driver/header/transform及所有36原请求、分支引用、资源帽、闭链/限位/碰撞/叶距离判据均不修改。
