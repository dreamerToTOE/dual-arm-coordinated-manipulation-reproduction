# P4 D080 断点恢复与阶段性执行计划（2026-10-17）

当前项目名称：面向双机械臂受限空间协同操作的P4重点环境复现与原论文对照。D080仅改变后续范围与排程；D079的真实数据、独立验收、来源区分、保全与三次同根因审查规则继续有效。本次为M0范围恢复交付，未开展新科学运行。

## 已恢复的真实状态

实际仓库 `/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full`，分支 `p4-full-reproduction-pcs-study`。切换前本地HEAD `bb3ca7e1fa37165d1b788dffa562c4eff73e021f`，已包含SBL SETUP01实际结果、独立后审及V25；无已修改的tracked文件，94个未提交文件共1121261字节。先逐字归档并逐成员校验，再fetch并fast-forward至D080 `dc810b78`。没有reset、clean、覆盖、删除或重启旧实验。无残留科学/编译进程；其他五工作树保持。

本地保全归档位于 `/home/ubuntu2004/lmy/.p4_d080_recovery_snapshots/20261017T084538Z/pre_d080_local_uncommitted.tar.gz`，SHA256 `f1871eef7d8068c20c5bfbd8855f402fc1ce0ba2138b5cabc063fca9a979e4f1`；公开manifest见 `P4_D080_PRE_SWITCH_LOCAL_PRESERVATION_20261017.json`。归档含历史作者派生源码，仅保留本地，不新增公开转载。

远程D080交接中的“setup尚待实际运行、V24”为较早快照；本次采用更晚的实际证据，不回退或改写旧交接：

|环境/方法|当前实际证据|尚未完成|
|---|---|---|
|I 平面20R|R1/R2组件与根因记录保留|原Fig3各m、PCS/NR投影及完整机制/算法统计；不能由旧同类模型代替|
|II RRT+PCS / RRT+NR|分别177/393节点完整离散路径，直接复用|原每组500次、性能/障碍优势及CCD未证|
|II CBiRRT+PCS / CBiRRT+NR|分别413/689节点完整离散路径，直接复用|同上；单seed不是正式统计|
|II SBL+PCS|BUILD01与SETUP01均独立通过；setup一次/public project13/solve0|新writer-shadow工程、SBL local/lazy/RBS、一次solve与完整路径|
|II–V RSS|原数学根/碰撞/失败与源码记录保留；无合格原生全程路径|原生RBS、采样分布/身份与完整规划独立线|
|III 窄通道|既有ABB运动学/端点资格与原障碍资产|本环境独立规划/碰撞/路径资格，不套用II路径|
|IV 多障碍|既有Comau数值/端点；fixed100/800数学记录|PCS/NR完整规划、RSS后续条件与正式比较|
|V 双吸盘搬箱|后续ENDPOINT_COLLISION_REPLAY01已对start候选52、goal候选22给出RECONSTRUCTED_SOURCE_POLICY_QUALIFIED|工具/物体/碰撞pair完整来源核对、PCS/NR原入口与完整路径；RSS旧8根碰撞根因独立待查|
|VI 三臂|全部原生/重建/失败/UNKNOWN及974/974预算留存|D080范围外，禁止新增VI修复、采样、规划和统计，不计本轮完成分母|

上述四条II路径为作者搜索控制流+CORRECTED数值+RECONSTRUCTED A01端点+aligned v3离散source-policy证书。原端点失败、native TCP mismatch、未证实体/连续碰撞均保留。完整45个I–V方法/规划器资格格见 `P4_D080_ENVIRONMENT_METHOD_PLANNER_QUALIFICATION_20261017.csv`；其中36格属于TableI。无证据的格不标算法成功或数学无解。

SBL setup复用证书：`P4_FULL_R2_ABB_SBL_PCS_SETUP01_POST_TASK_20261017.md`，独立JSON SHA `1c3ac4aef9f08917d33af7302f0b003f1d7960a557ddef4c1fad28f6caec8415`，执行SHA `107b8fe30b5e2f02c0a2ad035a2cee62d42f5b604c39d8de4bcd1952505b56e4`；不重跑。已完成但未提交的RSS supervised_v2/矩阵输出补充稿与V26保全草案从未执行科学；现转为暂停草稿，不能因旧22500/VI完整范围guard而直接启动。SBL shadow候选仅两处writer读取替换，未知输出明确-1/null；独立纯文本逆恢复已通过，尚无新C++构建或真实sidecar写成功证据。

## 211项范围与正式分母

新表 `P4_D080_ORIGINAL_VS_APPROVED_VS_ACTUAL_COVERAGE_20261017.csv/.md` 从V25最新211×186继承，保留ID、顺序和全部历史值，追加10列成196列；旧CSV不改。21行VI专属仅存档，30行跨环境部分范围，160行其余保留（含V应用优先21行、I/方法基准54行和仅概念应用分析1行）。范围中的FULL表示义务保留，并非实际复现已通过。9条公式及三臂适用限制的文献/理论核对仍完整保留；排除的是VI新增经验验证，不删除公式。Fig4图注I/正文II歧义继续记录，未替用户选择新科学条件。

原TableI 45组合×500=22500；D080 II–V 36×500=18000；VI原9×500=4500存档。正式已执行0/18000，原历史0/22500留原字节。`configs/p4_d080/formal_18000_jobs_DRAFT_NOT_AUTHORIZED_v1.csv` 为18000个唯一任务编号，每格500，原1000s上限；seed/source/协议仍待冻结、结果均NOT_RUN，没有启动器或自动执行授权。

## 预算与资源

实际V25 43execution=32科学账+11工程；计费上界839.3257053759941wall / 771.588923CPU秒。R2原3600wall/7200CPU帽不重开，余额仅上界2760.674294624006wall / 6428.411077CPU；历史未测尾仍UNKNOWN。V25账SHA `ce612e7c9706666a338aae6deda581274f1aadb229e2be999cd6ee836499e64a`。D080另加scope overlay，不改旧账的22500字段、不把VI历史消耗抹掉。新科学执行0，正式预算未批准。

本机Intel i7-10700F，8物理核/16逻辑CPU，约50.44GB物理内存；公平并发和每进程峰值内存尚未测。18000×1000s仅“配置solve上限之和”即5000小时；不含物理验证/I/O或软超时超调。若全部超时，理想8个独占物理核也约26天，超过21天目标；真实分布和并行效率需pilot，不能承诺两三周必能完成。14/21天、8个理想worker对应平均每调用可用solve墙钟约537.6/806.4s，仍须再扣验证和I/O，不作为实测。

成本pilot草案见 `configs/p4_d080/cost_pilot_DRAFT_NOT_EXECUTABLE_v1.json`：建议36格×3配对seed=108调用，原1000s；只作成本，不替正式样本。108000s是其solve帽之和，并非已获R2授权额度。先完成逐格资格，按可用预算另冻结实际子集/预算，超过原余额须申请；最终正式18k必须提交实测资源申请并获批准。n=3的P50/P95只作探索性成本摘要，保留删失/不确定性；不会冒充稳定算法成功率。

## 阶段性执行计划（目标14–21天）

|时间目标|主线与并行线|退出证据与审批门|
|---|---|---|
|10月17–18日 M0|本次安全恢复、211附列、18k待审批清单、预算overlay、统一日志/pilot草案，提交推送|历史不变、逐行独立审查、无新科学调用|
|10月17–20日 M1|SBL+PCS优先：复用setup；shadow writer新工程/落盘→原local/lazy删树及RBS→单次原solve→完整路径；SBL_NR依赖准备|源码/输入/门限冻结，独立离散路径；不能以build/setup替代|
|10月18–23日 M2a|并行V原工具/抓持/物体/碰撞pair资格与PCS/NR入口，优先端到端|复用已合格V端点，避免重跑；不能忽略RSS旧8根碰撞|
|10月20–25日 M2b|III窄通道、IV多障碍PCS/NR；I原Fig3/m与投影机制独立低资源线；II–V RSS有界诊断|每环境本地完整路径/失败、来源分列；同根因三次进入审查|
|资格后尽早 M3|统一调度程序与真实成本pilot；分开solve、验证、I/O、CPU、RSS内存、负载与并发|pilot协议/预算先冻；实测后提交18k预算申请，未批不开正式统计|
|批准后至目标10月31日–11月7日 M4|18k公平批处理/中断恢复、Fig3–5/TableII/50万投影/约5万可见性/关键消融、分析与Word/PDF|依实际成本调整并及时报告资源；不私自缩样本或删内容，最终表交用户审查|

这是依赖与目标窗口，尚无实测成本支持最终日期保证。不同环境/方法的工程可并行，正式计时须隔离并控制线程与负载；RSS不阻塞PCS/NR。普通授权工程连续推进，不为每个小检查停机。新增算法/几何/阈值假设、扩大预算、正式18k、再删范围或最终结题必须请示。P2、Isaac、双FR3新实验均禁止。

## 原文图表与关键实验清单

|原文内容|211行索引|D080处理/规模|
|---|---|---|
|式1–9、Fig1四杆机制与适用条件|T01-EQ1/2、T06-EQ3..9、T01-FIG1a..d|全文数学/来源审查保留；示例重建必须单列|
|Fig3平面PCS被动链数与NR|T19-VIS_M1/2/3/7/20、VIS_NR、TIME_M1..20/TIME_NR、PLANAR_PROJECTION|原m系列/原统计定义保留，不拿空间II代替|
|TableI|T18及45子行|原22500与本次18000分别披露；36×500/1000s，VI4500存档|
|APC/NR投影效率|T04-APC/NR|同50万ambient配置配对投影，原条件保留|
|Fig4可见性|T21-RSS/PCS/NR|约5万合法点对与原距离分箱；图注I/正文II歧义待原证据冻结|
|Fig5投影距离畸变|T22-APC/NR|同邻点定义与.46rad分箱；原未公开样本数仍UNKNOWN，不伪填50000|
|TableII|T20及十个指标子行|II Bi-RRT原指标；可见性独立点对，其他相应原500规划日志|
|无障碍/有障碍、full-vs-fixed链、换链及分布|T23-I..V、T08-I..V_ABLATION、T24、T30-I..V|保留原/已预注册定义；未公开规模冻结前不编造|
|三臂/多闭环经验泛化|VI专属21行及跨环境30行的VI部分|只读保全旧结果，明确本次不复现；不由I–V外推成功|
|双FR3适用性分析|T29|P4实证后逐方法条件/接口/风险/扩展路线，仅分析，无新FR3/Isaac实验|

统一记录至少含env/planner/method/seed、AUTHOR_NATIVE/CORRECTED/RECONSTRUCTED、源码/参数/输入SHA、尝试与派发数、成功/失败/超时、路径证书层级、原生/aligned碰撞、solve/验证/I/O费用。调度需独占job claim、原子结果持久化和可恢复尝试链；旧失败不覆写，pilot与正式隔离，不能重复计样。
