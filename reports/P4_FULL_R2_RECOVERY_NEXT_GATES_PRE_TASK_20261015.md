# P4 R2 恢复后最早缺口：局部连接与IV NR资格

2026-10-15。本记录接续恢复PRE-TASK和用户已批R2/A/B；不重开额度，不改旧失败。

## VI-Q2 PRE-TASK

科学目标：首个指定臂3/2合格样本construction219/643的真实腕分支局部接入。固定原q4/q6连续族，先构造±.01/±.005rad指定q5曲线点，再以active1线性中点与被动2/3原固定branch解析投影构造RBS。中心本身复用，未改为canonical IK。

最小证据：8显式曲线构造、最多4×7=28中点构造；总≤40、60s墙钟/120s CPU，从B原余92/134.866406228/354.358825扣。所有16根/构造、native F、原限位、双闭合、实际branch/真实Jacobian谱、原source-policy碰撞及叶全18原坐标距离<.0025均保存。指定负侧支1、正侧支3、另被动支3；active1原branch1。seed与fixture不可换，δ不缩，depth3未到h则UNKNOWN。

方法边界：作者VI RSS源码存在三臂遗留接口/未声明q3/dsg2及递归参数错误；独立重建不冒称作者可运行。原source tol=.05、singular shortcut=7×.05=.35rad（I/II/III才是15倍）。仅从已计算严格树归约source文本语义；阈值直接返回记录VACUOUS_THRESHOLD_PASS，不能借此称严格桥接成功。gamma=.2不改，新增规划事件0。

资格失败/预算耗尽保留真实前缀；不更换样本、扰动、分支或门限，不原地重启claim。accepted IK不sound、独立秩不一致或source变化立即阻断。仅证两条局部离散桥，不证全RSS/global path/全部奇异模式/CCD。

独立复核：audit_endpoints已只读确认目标变换、分支、原source语义和depth计数；根代理读完整工具/协议、对照旧all_roots和collision接口；独立代码复核另记。基础physical_nr/rss_geometry/collision_adapter及B原协议/claim保持原字节。

PRIOR-ASSET：原631b1f6记录和有界执行模式THIN_ADAPTER；B Evidence/RunBudget/独立FK/秩/原碰撞接口直接复用；旧FR3模型/规划仅REFERENCE_ONLY。独立新增仅三臂桥资格，原作者source/mesh不发布。

## IV-NR PRE-TASK

旧6条闭合后限位拒绝和3个额外正控FAIL保留。根因已表明±.01组在start仅.0008rad界余量附近不具必成功保证；这不证明论文NR错误。新组单独回答合法、微小、固定输入附近投影可执行性，不能替代旧组或声称完整邻域收敛。

绑定A02合格start22/goal44两个重建中心，h=min(1e-4,全12最小source-bound余量/8)在运行前定数；每中心arm1六坐标各±h，共24原始输入。只改变输入，原full12不阻尼伪逆NR/periodic_chart/原残差门/原限位拒绝不变；不固定NR内部active，不加约束、line-search或IK兜底。余量只证明输入在界内，不保证输出。输出branch只诊断，不添加原法没有的branch门。

预算最多24NR、24source-policy碰撞、52native F行、60s wall/120s CPU，计原R2 3600s/7200s。绑定全部previous ledger和source SHA，Q2先执行后刷新本组冻结账目。每input/trace/原生/独立残差/界/碰撞与拒绝全保存，任何普通失败使新组FAIL；来源/非有限/oracle矛盾/预算故障停前缀。没有新增随机或正式规划。

## 后续完整义务

本两组通过也不能解除全部规划gate：还需六环境各RSS/PCS/NR、原RBS/分支转移、所有planner构建/稠密路径验证和资格成本pilot。完整211行、22500正式规划、500000投影、50000点对、Fig3–5/TableI–II及全部消融/复杂障碍保持。正式大规模统计仍须在合格pilot成本后单独预算审查；P2/Isaac不开展。

冻结前代码复核：audit_coverage对脚本SHA4cde4164c4ee0a68d2f0c4ca17f108728374a580b0bfb79f565620e84b0db666独立只读复核未发现阻断执行的问题；父余额、固定首fixture、active中点、真2π副本、严格门与source文本旁审、timeout前缀及one-shot claim均与声明一致。

IV-NR冻结前独立代码复核：audit_coverage逐项核对24固定数组、原NR全12更新不变、旧失败保留、native52F/24碰撞及60wall120CPU帽、Q2后8份ledger、CONVERGED独立soundness和前缀留证，未发现阻断项。源码SHA a2d0530295404a4dd150b8c3d6c3374a984492b5bd8b77b1163894d6ab76a3fa；h_start=9.999999999996123e-5、h_goal=1e-4 rad；冻结前R2累计wall78.25053154900252/CPU29.917151。


## VI固定中心精确求值的一阶数学诊断 PRE-TASK

用户既有B预算内部，固定219/643保存中心各调用一次原独立arm1 FK/J，总2次；无新构型、IK/NR/碰撞/随机/规划，候选数0。预算5wall/10CPU从B原余126.879319736/348.048457与R2总账扣；全部prior9 execution、B/Q2 claim、原source和保存根因JSON先绑定。另建不可重复claim，原56候选余额不变。

目的：去掉保存数据active J向center外推的不确定性，直接测试原腕族rank5像的一阶相容。以原Q/S杠杆得到目标J，将固定active弦方向投影至B保存的指定奇异center J像；保存SVD、残差、6basis condition、非零q5导数与条件性的fiber角推断。active FK与原生IK保存T交叉。只检查有限可微lift的必要条件，不升格为无连续路径/全RSS失败/论文错误，也不构造推断fiber端点。

复用B RunBudget/Evidence和原已资格arm_fk_jac；新增最小代数诊断，既有几何、阈值和原Q2 UNKNOWN保留。独立代码审查后源码/协议提交再执行；同名已有run/claim拒绝复跑。source/pose/J秩矛盾、预算到达即保存前缀不重启。

独立代码审查audit_endpoints确认仅2固定active模型调用、targetJ负activeblock与原约束一致、保存nativeT可交叉、rank5/sixbasis/θ符号正确、budget及声明边界匹配；脚本SHA95881dab8fefbd9b198c9a81468a2635896eb727b2b5f05c4e2512851c2b07e0。未新增科学运行。

## VI固定6点奇异fiber组件资格 PRE-TASK（接续同一B授权）

固定中心一阶诊断已执行并由audit_endpoints只读重算：四条主动直弦的目标twist均不在原指定奇异center的rank5像内。仅支持OUR-RECONSTRUCTION局部投影图不匹配，不能推为无连续路径或原论文理论错误；Q2原UNKNOWN保持。详见新增CENTER_IMAGE_REVIEW报告，已绑定的旧保存归约JSON/MD保持原字节。

当前最小科学问题：条件性推得的四个同位姿奇异fiber端点及219两侧各一个theta/2中点，是否通过原几何、两闭环、branch、rank、限位和源离散碰撞策略，以及原center到各端点的短叶门。只6个固定构造，按exact-center保存theta逐值绑定，不新IK/NR/RNG/规划。只改指定臂q4+=theta*f、q6-=theta*f，其余16角保持且q5=0。219各两叶、643各一叶，全18原坐标欧氏距离严格<.0025。

预算6构造/10wall/20CPU从原B余56构造/126.671165572wall/347.840265CPU扣；原960/180/360与R2总3600/7200均不重置。数学arm FK/J36、源碰撞适配器内部TCP对照18，总54；6逻辑collision/native查询。内部请求、确认完成和中断不确定前缀分开记账，拒绝/失败不换点重试。保留独占claim、全部矩阵、输入、过程日志和真实成本。

这只是已批独立三臂RSS重建内部的奇异fiber离散组件资格；没有regular↔fiber接入、作者原生RBS、连续碰撞或RSS规划通过的结论。若之后采用新通用局部连接规则，先提供相对原RBS的数学差异、固定条件和新预算供科学审查，不将组件通过冒充新算法已被批准。

PRIOR-ASSET：复用已冻结B的RunBudget/Evidence、physical_nr/rss_geometry、原位姿与Q2保存节点、原已资格collision adapter。原固定631b1f6工程及复用分类沿既有PRE记录；只新增6点组件runner和独立协议，旧FR3/Isaac模型仅REFERENCE_ONLY，不替换作者几何。科学执行前源码/协议和全部输入须提交冻结；已有run/claim立即拒绝复跑。

冻结前独立代码复核audit_endpoints：runner SHA baf3eba251f14f0b8dc5e7c1b98ea39f2d3261f2d10338877bf99a33deeb395b，固定6点schedule、全部秩/branch/原界/位姿/叶门、54个FK/J计数、原B及R2余额、独占claim与前缀、Q2 UNKNOWN及仅组件边界均匹配，无阻断项；源码与协议提交后单次执行。
