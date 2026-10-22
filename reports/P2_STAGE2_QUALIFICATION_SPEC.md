# P2 第二阶段：实施资格与固定实验映射

2026-10-14；阶段输入834bcc372717a3b4ffbd0bd6ef7262b3b58237bf。用户已明确授权第二阶段完整实施；本文件在资格程序和控制矩阵运行前登记，不改上一阶段冻结JSON及其历史授权字段。

本阶段依据[冻结协议](P2_CLOSED_LOOP_FROZEN_PROTOCOL.md)、[参数JSON](../configs/p2_closed_loop_protocol_v1.json)、[原文审计](P2_ORIGINAL_PAPER_AUDIT.md)、[几何资格交付](P2_CONTACT_GEOMETRY_POST_TASK.md)及八页P2私有原文。原文式15历史疑义与批准的几何替代已裁决，不重新翻转符号或调整自由运动模型。

## 1. PRE-TASK REPORT与证据状态

- 科学目标：由独立式16刚体与原式9–12接触模型产生真实模拟位姿和wrench，核验42维右扰动IESEKF及原位姿/内部力控制，按同一固定协议记录四组结果。
- 最小证据：独立力矩/动力学资格；有时间戳的观测与流形滤波资格；因果控制/队列资格；全动力学半步资格；已登记30个case及全部失败和未执行项的明确账目。
- 范围：原物块、Cartesian软接触、独立plant/测量/估计/控制、数值运行、落盘指标与曲线；root负责实施与运行，本文件的独立审查者不启动实验。
- 非目标：P4/RSS、P3、Isaac/ROS、FR3/吸盘/车厢改进、完整抓力/摩擦卸载和硬件位置伺服。
- 预算：总P2小修1/3已用、余2；初套30控制case；实际后续上限74且原81天花板不扩大，120秒/case和7200秒总体上限保持。
- 优先方法：固定Lie指数中点独立plant；式17新观测；右SE(3)IESEKF；式20/21/25联合控制和整数事件队列。
- 后备方法：保存失败和部分完成结论，禁止用GT/普通EKF/解析衰减替换主实验。资格失败停止后续门，不自动更换模型或阈值。
- 文件范围：本资格说明和任务卡；其他科学源码由root分配实施，冻结/保护文件不修改。
- 确认：本阶段新授权明确，无需重复批准。重大理论/模型变化仍停止请示。

既有68/68只证明接触几何资格。第二阶段的动力学、IESEKF、控制和完整闭环状态分别记账；未取得证据前均不能标合格。数学/部件资格程序可以不占控制case，但必须预登记实际输入、运行次数、源码、结果和壁钟，不通过重复不同初态/时长隐含扩展实验。一次首次部件资格不是一次算法修正；运行失败后的源码小修跨阶段消耗剩余2轮。

## 2. 不变依赖与独立性

冻结JSON SHA256：423f58ca7cfe13861586bb486dcfd6d19c5e3d82b69e40c3d403c90d7c871df3。几何模块SHA256：47557da9189d8525e8a1ec343b5a4afc929405071d4e5de7d562091cc04a629a。每次资格/正式运行记录当前科学源码、协议和依赖版本SHA。发现这些保护对象改变即停止，不能把改后的文件沿用旧资格。

plant保存自己的O/V/E1/E2/C/G1/G2；observer拥有独立可变状态和P。共同纯数学函数可复用，但不得共享可变数组、从plant读取估计初态或将期望pose直接写回O。主控制器仅接收估计状态、参考、模式及已发布历史input。GT仅评分、明确GT诊断和切换真值守门使用。

原式10的Rbar(D)保留，不能用完整Ad(D)或新几何精确a替换阻尼。两机器人body input在固定base左乘下不变，E2送入几何函数前必须由C逆变换到共同base。式9弹性hK、式11阻尼hB和总h分别保存；式17模拟触觉只含hK与指定R噪声。

## 3. Gate D：独立力学与动力学

首跑Gate D以已先行提交的[独立动力学窄规格](P2_STAGE2_DYNAMICS_QUALIFICATION_SPEC.md)和源码9194f9f为实际门；本表对齐该规格，不在首跑后追加新门或把未执行检查说成通过。其结果标NUMERICAL_DYNAMICS_QUALIFICATION，不是主控制/消融数据；任一失败停止后续观测、滤波和控制矩阵。

| 检查 | 固定输入/方法 | 判据与证据 |
|---|---|---|
| D1：9种双H物理wrench映射 | 冻结A fixture的O右扰动[.0003,−.0002,.0001,.04,−.03,.02]；Vo=0；U1=[.001,−.002,.001,.01,−.015,.003]，U2=0；所有tight/pivot/sliding组合 | 独立用f_o=R f_e、m_o=p×R f_e+R m_e计算作用点力矩，不能只检验W与W转置配对；逐分量沿用代数1e−10，内力零空间残差≤1e−9N/Nm。rank约定已由68项资格认证，本程序保存新fixture奇异值，不称新增显式rank检查 |
| D2：接触/阻尼公式独立只读审查 | 有限D及两个native/common EE、Vo/U坐标与原式7–11逐项核对；审查mechanics源码 | Rbar保持原近似；G逆含object点lever；减去同EE body U；hK=−K LogD、hB=−B Vrel。首跑D1因Vo=0，不能把它冒称非零Vo/Rbar独立数值检查；主测量隔离资格仍须确认触觉不含hB |
| D3：无接触自由落体 | 只在明确部件诊断副本中K=B=Ba=0、tight、Vo初始0、原A初态，一个1/3000s积分步；主物理参数不改 | 世界平移/速度与常重力解析值逐分量≤1e−10；无反馈、无期望轨迹、无假接触力；日志区分“资格用参数”与主名义值 |
| D4：body惯性项/动能 | K=B=Ba=g=0；V=[.01,−.02,.03,.2,−.3,.4]，A均质M | 与独立Newton/Euler body方程加速度逐分量≤1e−10，动能导数绝对值≤1e−10W。gravity换轴由D3及D5保存的力平衡另行观察；不称已自动认证总软接触能量/耗散/被动性 |
| D5：真实locked-EE settle | transport、high_moment、sliding三种冻结初态，名义K/B/Ba、gravity开启、两EE速度0、控制关闭，各固定5s实际积分 | 完整末端线速≤1e−7m/s、角速≤1e−7rad/s，contact+gravity每force分量≤1e−6N、每moment≤1e−6Nm；任一不符记INIT_INVALID，不延长、不换初态、不用解析平衡覆写 |
| D6：transport settle半步数值资格 | transport的1/3000与1/6000s，全部5s、共同输出时刻、无控制；highmoment/C不额外添加半步run | 原窄规格比较position≤50μm、angle≤5e−4rad、各internal force差≤.05N、各internal moment差≤.002Nm；两边都须满足D5末态门。对称internal接近0时不能据此声称完整raw接触瞬态已通过半步；后续Gate H要求全闭环raw contact资格 |

D5/D6按窄规格顺序共有四条固定无控制5s物理积分：transport主步、transport半步、highmoment主步、C主步；不是四个运输性能case。每12个主tick对应250Hz保存完整state、tau、hK/hB、external/internal、force/moment平衡残差；半步按相同物理输出时刻保存。数值积分一直使用冻结Lie中点，保留所有过程、终端门、失效时间和未执行项。尚无完整的非零Vo阻尼数值oracle或全部raw contact半步证据时，明确列局限，不把第一门的有限覆盖说成全模型认证。

冻结对称初态的可达性只作独立预测：A两EE x都沿world+z，纯重力下沉δ给τ_x=−δ、每臂hK_x=5641δ。对称力矩抵消，静态δ=mg/(2×5641)约0.59476mm、每臂约3.35502N；纵向线性化为m zddot+100 zdot+11282(z−z_eq)=0。高moment的Rz旋转不改变重力轴。C的竖直抓持同样由EE-x承担重力。这个预测不是实验输出，也不替代D5/D6实际门；若失败，先检查作用方向、dual wrench映射、base变换和SI重力，不调整判据。

数值可达性与静态平衡存在分开：C的Ixx约1.11467e−4kgm²，两pad对EE-x转动的B至少1Nms/rad、lever约另加.04，因此快阻尼特征量可能约−9330s逆。显式中点主步对应z约−3.11、放大因子约2.73，超出负实稳定区[−2,0]。这仅是运行前的线性数值风险预测；实际C门若失败须保存，不能把它简单改判成物理平衡不存在或自动换步长/积分器/阻尼。

## 4. Gate E：观测、42维IESEKF与时间

以下确定性部件资格在正式控制前完成；每个fixture与packet、seed/stream、初态、P/Q/R及顺序在资格源与metadata中固定，不新增主实验随机seed。除明确线性Gaussian oracle外，使用完整右SE(3)42维状态，不以向量EKF充数。

- 右retract/local、状态与观测Jacobians使用独立中央差分；步1e−6、atol1e−7沿用冻结值。差分输出在相同预测/观测切空间，不能将两个世界平移或Euler角直接相减。采用解析/自动求导/其他等价在线实现前，须与这个oracle核对。
- 原式17的EE、hK、cam1 O与cam2 C O分别通过source/input隔离检查。噪声使用原R、右切空间pose perturbation与固定camera bias；无噪声fixture明确是部件诊断。所有原始样本有sample_stamp、delivery_stamp、唯一ID，15/60/30/200 tick及76s关闭cam2事件按原设置。
- 相同packet的IESEKF内层迭代共用同一prior及观测，只在最终更新/重置P一次；线性Gaussian oracle检验无重复信息累积。最多5次及原收敛量不变；连续3次不收敛触发停止。
- 非零有限注入的右retraction协方差重置，用独立切空间差分检查；不随意对角化、裁剪负特征值或强行投影估计自由形变。对称≤1e−10、负特征值不得低于−1e−10，按冻结门。
- C的均值与gain行冻结，Q_C=0；Schmidt/Joseph保留P_CC和正确跨块。线性fixture与独立dense Joseph计算核对，检查C均值不变而active state/P可更新；不得把P_CC清零当标定精确。
- 时间调度到真实sample stamp，不把5ms样本当8ms当前样本；旧缓存只可持有、不能重复更新。异步过程噪声采用已冻结Q_c=.004Q_table，不因切步次数重设尺度。
- 75对静止视觉预标定、真实gravity settle、t=0新观测初始化依次进行；主滤波初态不得读取trueC/trueO/trueh或用GT补失败。PCG64配对noise按传感器sample_index产生，控制消融不会改变同seed的外部噪声流。

资格通过标estimator_qualified，不自动等于控制闭环有效。若未完成解析Jacobian、在线速度或框架适配，保留该缺项；不能为了达到120秒/case将主估计器替换成GT。

## 5. Gate C：控制、参考与因果队列

- 独立核对hI=H^T(I−W†W)Hh、U_F=−KF hI、U_P=Ad(A逆)(Ad(O_hat逆 T_d)V_d+KP Log(O_hat逆 T_d))及U=U_F+U_P。W rcond、原增益、零内部目标、SI与EE坐标不变。
- 开关fixture分别验证exp1的KF=0、exp2仅KP=0而前馈保留、exp3联合、exp4只observer K失配；GT-exp4仍保留altered model K计算控制h，不能同时替换成true force。
- 同一事件先plant/旧input力与新观测，再observer预测/更新，再控制计算新Ucmd，最后各200/50Hz发布tick作H选择并排执行队列。observer用旧已发布H-selected input计算hB；300ms代表例保持未建模时延，不泄露实际GT速度或做事后补偿。
- 参考每段从本组估计O生成，目标/时刻固定；Log与前馈相同object frame。跨组只依原GT共同目标RMS指标判定，不能按各自tracking AUC排名。
- 两次滑动mode event使用已验收原guard检查true未选择hK+hB及自由形变。未卸载可在5s停止；不能增加抓力控制、变更事件或重锚。
- 退出界与缺失/重复sample、协方差、pad/速度命令、时间预算均沿用冻结文件，不增加静默饱和或自动reset。

组件资格记录还须证明plant/observer数组无共享、主controller接口没有plant引用；统计和曲线仅由保存日志重读。

## 6. 首套30个控制case映射与全动力学门

ID表示固定矩阵位置，实际运行顺序写入ledger，不要求先执行ID01。每个case独占目录，failed/aborted/timeout仍占该名额；未执行明确标NOT_EXECUTED。每个case包含原预标定/settle、正式clock及终止账目，120秒壁钟不得用拆phase反复重置。

| ID | 类型 | 条件/seed | 期限与标签 |
|---|---|---|---|
| 01–05 | primary transport | exp1；7/23/41/101/20261013 | 95s；正式估计闭环 |
| 06–10 | primary transport | exp2；同五seed | 95s；前馈保留 |
| 11–15 | primary transport | exp3；同五seed | 95s；联合控制 |
| 16–20 | primary transport | exp4；同五seed | 95s；仅模型K失配 |
| 21–22 | high moment | exp1/exp3；seed7 | 95s；代表例独立统计 |
| 23–24 | unmodeled delay | exp1/exp3；seed7 | 95s；第二端点300ms |
| 25 | conditional sliding | exp3；seed7；C | 30s；原5/25s守门，可真实失败 |
| 26–29 | GT diagnostic | exp1/exp2/exp3/exp4；seed7 | 95s；读取GT state、保留条件模型，不混入主结果 |
| 30 | full-dynamics half-step | exp3；seed7；1/6000s | 95s；以ID11的1/3000s数据作粗步，不再新增粗步case |

Gate H固定：ID11与ID30同seed/外部noise、原控制/观测物理时间及输出时刻，比较全95s真实O、force、moment；沿用50μm/5e−4rad/.05N/.002Nm。半步clock中事件tick同比倍增，不能把sensor rate/延迟或滤波时间减半。只有门通过才能把该批数据用于四组控制比较；失败时两份轨迹保留、其余矩阵停止，不运行第二条粗步或换seed凑资格。可先运行ID11/30完成Gate H，再运行余下矩阵，ID11不得再次计作新样本。

五配对seed最终85–95s真欧氏目标距离RMS/真SO(3)角RMS与13–76s真stack内部force RMS的三条比较假设全部沿用；位置和角分别判定并列出不满足的seed。原文0.1mm、0.42°、10mm/4.5°、1.5N、80%仍仅描述性参照，不作调参目标。

## 7. 失败、修正与交付资格

动态门失败先保存trace/source/hash/status，停止后续资格和控制；只可凭具体实现错误作剩余两轮小修，保留各源码与原失败。证明故障属于冻结模型/理论限制时，不把改控制增益、重力/质量、settle长度、初态、模式、滤波结构或放宽门限计作小修。

若发生新修正，每轮最多原7个受影响诊断case，终版同源全套至多再30；两次控制修正上限为30+2×7+30=74，原81天花板保持，不额外分配预算。部件数值资格与控制case分栏，wall-time分栏且总体预算真实记账。

“完成”要求先区别：组件/闭环科学结论通过、或已在冻结预算内实做并真实报告不通过/部分完成。只要缺完整估计或动力学门，就不能用GT诊断的曲线冒称视觉触觉闭环复现。真实曲线、全部失败和NOT_EXECUTED账目、原文条件差异及中文Word/PDF由root交付；正式报告最后独立应用差距章，不做FR3/Isaac改进，不启动P3。
