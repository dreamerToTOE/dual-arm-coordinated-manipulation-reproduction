# DECISIONS

## D035 follow-up — 原属性precision与state-output/geometry双审计，不消除负结果

2026-10-08，[ENGINEERING]。04因原SDK Cube orient expectedQuatf/gotQuatd在START停止，accepted0/wrapper0非PASS；Fabric disabled/updateToUsd=true，native成功值未保存且未进入碰撞判定，03/04均保留，不能作BUG019几何判决或修复证据。

05仅依既有状态属性precision写值。将body pose state-output库存与不可变几何尺度分开：原SDK可能自己物化Cube orient，这是SDK状态输出，不是helper新增ops；helper依旧只写existing translate/orient、不新增/重排，非法顺序拒绝。geometry fingerprint涵盖全scene physics/材料、所有相关ancestors、工具TCP库存，原scale/local collider/shape/mesh/limits/参数和q/native/setting/step0守卫不削弱；新增final与screenshot step0检查。35纯USD/query测试agent报告OK、主代理待复跑，固化source后GUI05尚未运行。

不改任何benchmark/实际几何/ACM，不实现P4、force或论文[DEVIATION]。READY仍须先过实际parity；BUG019未判决、BUG001非TASK01阻塞；全部门禁通过也只PASS CANDIDATE。Git采用命令局部direct push成功上传 `a672224`，首次proxy timeout记录保留，不改全局SSH。

## D035 — 静态输出源工程修复保留原模型与全部取证门禁

2026-10-08，[ENGINEERING]。03 START/state0 因USD collider旧旋转被正确拒绝，accepted0；wrapper0不等于PASS，不把尚未发生的移动shape/full-chain查询说成几何失败或BUG019实际碰撞。已通过native actor门禁但成功值未存，只记录控制流事实，不能事后补成实测数值；后续新的执行应完整保存native与USD比较。

04准备优先复用官方scene/Fabric当前已有导出路径。若仍stale，仅可把已经验证的native actor SE3镜像到**原body已有**translate/orient作为静态输出适配；不得新增/重排xform ops，不动原scale、collider local transforms、网格/shape、物理/设置、工具/车厢/抓持/SRDF/ACM/IK验收/基准。处理paused notices后再次完整核对q、native actor、原几何/设置与step0，实际cooked-shape positive/negative移动query freshness门禁不削弱。不能用USD镜像自动推定PhysX actor或broadphase已同步。

04尚未运行；任何证实FCL-free/Isaac真实意外重叠依旧首败即停/exact pair，不修几何。静态replay以index记录、step/time=null，不伪称postphysics reset数据；仅parity实际通过才继续START/PRE多次READY/reset。此决策不是P4实现、论文替代算法或[DEVIATION]，不为TASK01加force门槛；BUG001属于TASK10-IS。只在所有门禁实际通过后才可PASS CANDIDATE，FROZEN仍待用户批准。

## D034 evidence follow-up — 全链实得14q只候选，先核模型再reset

2026-10-07，[EXPERIMENTAL] 新START几何链实际A136/B157通过，实际PRE14q完全相同；所有状态distance而非仅六端点已保存。START与PRE配置记录候选YAML，不自动FROZEN，不再随机求起点。原run配置独立快照/SHA，避免录q后篡改旧hash。

[ENGINEERING] 全链最小腕工具环境gap在TARGET左link7/deepwall2.212219mm；另全pair min约1mm为现有Cube/杯面间距。实际PhysX对照优先START/PRE/TARGET/state196，再其余全部状态；不用FCL模型给PhysX背书。未过parity不做reset，未过reset不标TASK01 PASS CANDIDATE；旧5Cube与force/wrench仍不在范围内。

## D034 — 新科研START明确批准；全链几何→模型一致性→READY/reset按序门禁

2026-10-07，[ADAPTATION] 用户明确确认Benchmark A START Cube=(0.550,0,0.380)m、xyzw=(0,0,0,1)：双FR3已经通过当前shared-grasp transforms稳定共同持件并离桌，不包含抓取过程。**这是新的科研benchmark设计，不是旧Task27 feed pose**。PRE_PUSH=(0.790,0,0.260)、TARGET=(1.100,0,0.260)、L工具/车厢/抓取/TCP/基座/碰撞网格/SRDF/ACM/独立验收保持。

[ENGINEERING] 探针继续已验证LMA epsilon1e-7/weight0.01、平移1e-5m/旋转1e-4rad验收和≤2mm Cube位移；记录所有状态full FCL最小距离/最近pair及腕工具环境距离。A先检查，首败即停；A通过后以其实际PRE14q延续B，不能简单拼接旧B另一IK构型。记录实际START14q为候选及provenance，供后续reset精确恢复，不自动FROZEN。

[EXPERIMENTAL] 几何通过后才可见GUI静态replay单Cube全链作BUG019原模型对照，任何FCL-free/Isaac-overlap exact pair出现即停止，不改几何/ACM。模型门禁通过后重复START/PRE reset，用post-physics-step simulation stamp记录q/Cube/TCP/frame误差。不得开五Cube/完整控制器/force calibration；BUG001/wrench/重力惯性补偿归TASK10-IS，不是TASK01门禁。全通过也仅PASS CANDIDATE，待用户最终冻结审查。

## D033 — 原几何/门限下同seed数值精度对照，不等同物理或论文PASS

2026-10-07，[ENGINEERING]/[EXPERIMENTAL]。用户批准“继续”保留几何诊断；只在独立探针中记录每臂拒绝并允许收紧LMA epsilon（1e-5→1e-7），同一失败14q/目标重放。保持orientation_vs_position0.01、平移1e-5m/旋转1e-4rad验收、原限位/模型/抓取/ACM/runtime文件不变；不新增随机重试、暗改START或工具/车厢。只证明数值停止精度不满足原验收的局部问题得到解决。

随后≤2mm名义插入检查首次真实失败即停；157状态实际通过，也只记离散几何PASS，整体PARTIAL待START和Isaac审查，TASK02不提前开始。robot FCL未覆盖的worldCube/environment，用当前原盒形/零偏航AABB补审计，不豁免接触/改变PhysX。保留原失败与旧binary无效尝试，完成实际构建后核对exe再跑；无新论文[DEVIATION]。

## D032 — 单 Cube 几何先行，首败后停止，不从端点PASS推断路径PASS

2026-10-06，[ENGINEERING]/[EXPERIMENTAL]。遵循用户新要求及云端已批准单Cube范围（同日single-Cube D016，与历史XYZ D016不同）：只做几何，不启动长Isaac试验。端点PASS与同一seed加密链分开记录；连续链首败后不再搜索/修改，不将数值IK失败称工具几何不可行。START仍待定义，不自行选择供料点或平移导轨。以后只有用户确认诊断范围后再继续，工具/车厢/TCP/SRDF/ACM和force/wrench延期边界保持。未新增论文[DEVIATION]，没有借机实现P4。

## D031 — 仅新侧接触下降补实际规划时间化，不降播放倍率掩盖问题

2026-10-06。[ENGINEERING] 本机Humble Cartesian srv无v/a scale；Task01 DUAL_SIDE_CONTACT以现有MotionPlanRequest速度/加速度scale（当前0.12）做IPTP，逐点q和joint_names必须完全不变，完整同步FCL保持，播放1.0/PhysX秒不变。不是改物理或关闭碰撞，不改其它Cartesian或旧节点时序；不将slow成功当normal成功。真实接近仍失败则保留，不从软件补计时称已经修复。

## D030 run follow-up — fresh GUI实测，不拿软件测试称通过

source6fa161e串行58.5s/Binary75f798a1核对后进入fresh可见原场景首件；GUI显示/READY确认和控制器初始化均实际通过。外部20s只读原子消息receipt记录物理/现实时间关系，不能把receipt频率当纯physics FPS或据此单独证明接触根因。保持所有原保护/模型/36nulls，先实际结果再决定五件。

## D030 — 正常规划播放用实际PhysX秒，GUI延迟不变成隐性加速

2026-10-06。[ENGINEERING] 仅Task01 single/sync执行器，从已校验的原子fixture_geometry拿物理stamp；一次循环双臂同phase，重复stamp停进度，回退拒绝，原250ms收件失鲜拒绝且无wall fallback。1.0定义为正常物理规划秒，12%RRT限速/原Cartesian时间/phase平滑/下发周期均不变。不是改physics dt/drive/路径/ACM，也不是论文控制律。真实GUIrun02跟踪/接触负结果保留；因果不唯一，fresh重测前不宣称物理修复。如果标准规划速度仍失效，不自动降速、提高force gate或改模型。

## D029 — 可见SimulationApp复用原fixture记录器，不静默fallback

2026-10-06。[ENGINEERING] 新GUI入口显式headless=False，缺DISPLAY立即拒绝；本机官方Kit VS Code执行器只监听回环。只增加可视灯光/观察相机，不改原场景/工具/碰撞/物理、采样或控制门限。第一次可见GUI渲染失败时先不运动，保留0命令/native139负启动，再独立fresh GUI截图确认后实测。先单件scale1，后按结果五件；不能拿旧慢速PASS支持新速度/全任务PASS。历史headless源码可保留复现，但本轮及未来不得直接启动其无界面入口。

## D028 — 正常规划轨迹倍率与GUI-only仿真

- Date: 2026-10-06; Classification: [ENGINEERING]运行默认值/工作流；[EXPERIMENTAL]后续新速度验收。
- User input: 用户询问是否50%运行并要求100%；以后不要headless，需要看场景。
- Decision: 当前`task01_dual_suction_fixture`默认`execution_time_scale=1.0`，含义是按规划时间100%播放，之前实测5.0是20%、2.0才是50%。该设置不等于MoveIt/机器人关节上限100%；RRT速度/加速度12%保持并明确告知用户，不推断批准把接触运动直接提高至硬件上限。
- Workflow: 以后助手只启动可见Isaac GUI，不再headless；保留历史脚本、命令与原始负证据，完整列出scene/Play/Bridge/原子反馈加载步骤。当前仅改新节点默认值，旧Task26/27参数不受影响，显式历史5.0参数仍优先于新默认值。
- Validation boundary: 1.0实际轨迹需要重新GUI物理验收；此前慢速单次PASS不可用于normal倍率成功率。250ms反馈/80Nm/2.5mm/ACM/物理/模型/36项null均不改变；不启动P2/P3控制律或TASK02。

## D027 follow-up — 加密空载几何检查、保持路点的计时，先同路径对照

首个请求局部scene探针3次被MoveIt自己判后处理路径无效，全部负结果保留。下一工程范围仅OPEN空载handoff：在当前控制器内加载原OMPL插件和配置副本，本地检查分段比例0.0005、IPTP计时并逐值验证q路点未变，最后仍原0.01s完整FCL/起点/目标/限位守卫。不是启动后台沙箱/第二move_group，也不改全局参数、加载轨迹、ACM、世界或接触门限。probe同一raw RRT分别检查原几何/defaultTOTG/IPTP，不能先验声称TOTG唯一根因。当前改动未作物理成功承诺，不是P2/P3复现或benchmark冻结。

## D027 — 只读重放与实际路径规划使用同一完整场景和顺序起点

Date: 2026-10-06. [ENGINEERING] 新fixture空载转场有限RRT候选池，原场景、目标、碰撞冗余、ACM、阈值不变。先从一次完整实测RobotState规划/验第一臂，再以第一臂预测终点+第二臂原起点规划/验第二臂；两段均通过才执行。MoveGroup plan_only的planning_scene_diff只作用于该请求场景副本，不是后台沙箱预规划，不写远程Scene，也不豁免当前Cube。实现/真实验证待完成，不能预记PASS；若需改变模型/物理/门限则另问用户。官方MoveIt2 Humble move_action_capability.cpp 的executeMoveCallbackPlanOnly使用copyPlanningScene进行请求局部规划。

## D026 physical checkpoint — 以实际完成计数，不以候选成功计数

full02已实际batch1/2通过，第三抓取继续。联合gate PASS只授权同候选后续实测流程，不将preflight当batch完成；原RRT/FCL重试/OPEN XYZ/原子geometry/80Nm仍全部保留。短清障后的GT而非释放前命令终点作为最新落点记录，不从2/5提升稳定性或冻结状态。

## D026 run follow-up — READY与hash双守卫后才运动

production57e72f83强制重编译核对成功后，fresh full02只有在新场景日志出现真实first feed READY且exe SHA完全相符时才启动。启动正确不等于物理成功；运行期间不改当前源码/门限/场景，避免再次二进制与记录时序错位。

## D026 build follow-up — 实验前串行核对最终执行二进制

不边修改include边编译production目标；增量no-op/mtime不足以保证源码一致。full01 174d6ef7等价声明作废并保留启动负结果；当前强制目标重建，不编辑生成install文件。核对新binary SHA及真实执行初始化后才能算source对应运行。probe已通过的本地联合链结果独立保留，不拿未动作的production启动当物理测试。

## D026 follow-up — 旧solo预检不能代表新双吸链

首三选候选改用新双链，不再要求/宣称旧helper-park solo PUSH/RETREAT代表rear+side可行；后两/旧节点保持原逻辑。实际HIGH RRT/下降/加载联合FCL及80Nm/原子几何guard依然必做，不持件换构型。参数从实际运行MoveIt读取，支持现有root arm布局，不把插件变化当成算法修复。只读链通过后才进入fresh原场景物理回归，不以endpoint或软件PASS冻结benchmark。

## D026 — rear在OPEN候选选择时预检新双臂链

2026-10-06，[ENGINEERING]。同rear吸点已有替代端点构型可让side HIGH/CONTACT全FCL自由；选择时只看旧solo推入不够。仅新首三候选改为HIGH IK、连续下降（自由当前Cube参与FCL）、同进度双X/Y和短退出；原合法运动当前Cube仅在本地push世界不作静态障碍，所有其它对象/ACM不动。旧后两精准solo预检不改；现场实际HIGH RRT连接与负载检查仍必做，不能用候选预检绕过真实保护。保持原场景/工具/吸点/姿态/物理/80Nm/几何门限，局部插件参数来自当前MoveIt有界读取。不是论文算法、CLOSED构型调整或全局可行证明；真实回归后才汇报结果。

## D025 — 第三goal失败先做固定rear的有限IK/FCL重放

2026-10-06，[ENGINEERING]/[EXPERIMENTAL]。front2物理通过、third side HIGH无合法目标，先用原MoveIt模型/kinematics/world和精确实测14关节/Cube输入，在纯probe固定后臂、60个有限侧臂IK种子统计goal collision pairs。无Arm/机器人/吸盘/导轨/供料消息、无远程Scene/ACM写入。0合法候选不等于全局不可行；不从怀疑直接改rear/side的物理姿态、场景或保护。若要调整选构型预检，需先得到重放证据，保留full01失败。

## D024 follow-up — 精调首件通过后才进入五件；命令限步与轨迹span分开

首件两次OPEN精调norm2.196→1.201→0.205mm，实际流程controller0。1mm限制上一命令目标的修正向量，不是从实测起点的全部TCP运动；本次span3.178/3.200mm含旧执行残差，仍满足既有4mm/0.02rad微解算/FCL范围。明确记录这一区别，不隐瞒位移或放宽加载门限。

下一步同binary/原物理fresh zero-preplaced first1/max5，前三双吸附后两精准单rear。只一次首件不证明后续Cube、不自动冻结benchmark/推进TASK02；任何失败保留并停止后续对象，原模型/物理/门限权限边界保留。

## D024 — 复用吸附前XYZ消除rear重抓残差，不放宽加载门限

2026-10-06，[ENGINEERING]。rear45实测X1原子alignment2.578mm、主要rear Z残差，复用用户已允许的OPEN XYZ精调：仅前三后杯重抓，上一发送命令FK加同一步Cube/TCP残差；每次整向量≤1mm、最多3次/4检查。0.3mm仅新的吸附前目标精度，不替代原2.5mm/80Nm/碰撞门控。helper OPEN实测保持、原自由Cube/所有其它静态对象参与联合FCL；观测过期/失败则双OPEN停止，不CLOSE或推进下一件。

后两单rear/旧节点/L工具/世界几何/材料/物理/ACM及CLOSED路径不变。属于既有精调软件复用，不是论文控制律或新的力控；实际fresh首件须另验，若需模型/物理/门限改变仍停止询问。

## D023 follow-up — OPEN时建立后腕姿态，CLOSED时只共同平移

无命令rear45三链与三墙检查通过后，仅新3+2节点前三后抓RRT/预演调用同一函数，后两件原pushPose；不在已经吸附时修改相对grasp。参数非法在Arm前拒绝。原几何/物理/门限/ACM不变，fresh首件实际验证是必需，名义结果不叫物理PASS。

LP求解变更为[ENGINEERING]：等价坐标重心化、同全部约束的HiGHS-IPM与解残差检查；两次default solver失败保留，没跳数据/没更改碰撞成功阈值。

## D023 — 保持后杯面法向，先向中央让腕的无命令验证

2026-10-06，[EXPERIMENTAL]/[ENGINEERING]。原子反馈首件暴露rear右腕侧墙接触，不把原80Nm错误叫传感假报。只读probe增加rear worldX法向镜像roll幅值（诊断范围0..60deg，不是验收容差），尝试45deg/+Y正转、-Y负转，把腕向自由中央偏移；side保持-15deg。执行器未采用，没有CLOSED下转腕。

扩大**检查覆盖**到原三面墙，未扩大墙几何/ACM。既有deep-only结果保留且明确受限，新的名义PASS仍需完整空载接近/实际物理验证。模型/质量/材料/门限/36数值冻结若需改变则另问。

## D022 — 修复测量同步，不放宽接触门限

2026-10-06，[ENGINEERING]/[ADAPTATION]。用户继续授权下，在独立3+2节点前三双吸附的几何检查中引入单消息live PhysX快照，Cube与两个TCP共享一次读出；旧场景/bridge/topic和后两单rear不改。250ms仅观测新鲜度超时，不是新几何成功阈值。启动缺消息/运行过期拒绝，不能退回USD或无限重试。

保留dd63c74 X3失败，先进行相同原参数的新鲜first1/max1 headless复测及同回调USD源对照。模型/物理/ACM/80Nm不更改；新姿态深墙风险、碰撞模型差异和36数值评审仍待解决，不提前推进论文控制器/冻结。

## D021 — 先做原点/杯面法向不变的腕姿检查，不靠换场景或加力控

2026-10-06；[ENGINEERING]/[EXPERIMENTAL]。用户“继续”下，先保持原controller/模型/物理/80Nm实际复测并记录；实测机器人-深墙接触且FK一致，不再仅假定闭链内力。只读探针允许绕杯面法向worldY转角（有限±30deg诊断范围，不是benchmark门限）候选，杯面中心、法向、3+2角色、cube/墙/L几何不变；不选新基座/墙/碰撞豁免。

nominal02 -15deg通过原FR3链与原USD凸包离线检查；执行器尚未应用，不用无命令证据替代物理验收。nominal01采样行坏就FAIL分析，独立文件重跑而非吞掉坏行。若需要改模型/物理/benchmark/论文算法则另问；36nulls/TASK02保持。

## 2026-10-06 follow-up — 网络恢复，原场景第二次启动

原S3直连/代理HEAD恢复HTTP200，runtime d35cc0c正常push成功；保留startup01失败。相同官方资产/原参数的startup02重新运行，held live handles与首件物理诊断仍待验证，尚未发controller命令。BUG017根因未解决，BUG018外部连接暂时恢复不抹掉负结果；模型/物理/门限/YAML不变。本段更新此前“final”失败checkpoint，不叫新物理PASS。

## 2026-10-06 final — D020 final：外部依赖失败不篡改模型取得结果

只读代码/44软件测试/编译通过，外部资产失败使真实采样尚未验证；保留原模型/门限，不把未验证来源的cached FR3当作原模型替换。保留失败.json，即使Kit cleanup退出0也判startupFAIL；不宣称新3+2或Y15通过。网络/代理恢复后从同样普通供料首件重启并先确认live sampler，随后再做证据驱动工程修正。没有修改系统网络设置/SSH凭据或开始论文算法。

## 2026-10-06 — D020 诊断优先、控制律不改

[ENGINEERING]新增专用异步phase topic并复用同一步sampler；真实contact-report telemetry为可选运行期API，不改原源码场景/几何/材质/质量/驱动/solver。采DOF投影effort而非混合6Dfallback；保持revolute Nm/prismatic N区别，不叫TCP wrench。先记录后决定是否有原范围内修正，不默许力控/物理/门限改变。

## D019 final checkpoint — 新流程软件实现不等于物理验收

2026-10-05；实测换角色试验X16/Y14后在Y15触发86.975Nm保护。保持前三双吸附/后两精准单推，不以helper退场、单臂替代、提高80Nm或改场景获得PASS。首件未完整完成，不继续后四件并称新5/5。

仅添加释放后静态只读FCL诊断，不解释为触发步无碰撞；下一步为持件同物理步接触/关节观测及证据驱动工程修正。若确需改物理、工具、基准或新增论文/力控方法，遵循原停工确认边界，而不是由失败自行授权。旧5/5与新3+2负证据分开，benchmark仍DRAFT/36nulls。

## D019 follow-up — 换主从角色必须使用墙接触后的实测起点

2026-10-05；[ENGINEERING] e0477ab仅新节点：X到深墙后重新取双臂共享实测状态和新Cube GT，保持双CLOSED，通过当前联合FCL后从该真实起点按原目标重算Y/释放包络。不得把命令终点当作真实刚性闭环状态，不增加顶墙越程、改材料或放宽80Nm/几何门限。旧日志未确定互锁原因，补详细诊断与新鲜场景复测，不把这个合理修正称为已证明根因。

## D019 — 前三 rear+side 双吸附，后两精准单 rear 插入

- Date: 2026-10-05；用户明确批准新的3+2分工，覆盖D004中“前四件双吸附”的该部分。
- [ADAPTATION] 新独立节点 `task01_dual_suction_fixture`：旧共同 lift/XYZ 搬运/落桌后，rear 重抓 -X 面；helper 抓朝中央自由通道的侧面中心。双 CLOSED 才允许共同 +X 推入，到深墙后不松吸盘互换 rear-hold / side-primary。第三件是双吸附侧压，不隐性回退成 helper park / solo trim。第四/第五继承精准暂放、单 rear 推入。
- [ENGINEERING] 两臂使用同一物体位移进度，每2mm共同 waypoint 复用有限世界FK Jacobian微解算；每段保持实际 grasp 相对变换，整条联合10ms FCL及原2.5mm/3deg相对几何门控。不是把独立时间参数化轨迹仅拉成一样时长。旧节点负载路径不变。
- [ADAPTATION] 双吸附闭环不能照搬旧未吸附侧压的4mm压紧越程；新节点终点为既有贴墙格位。没有改变墙/格位/验收值。第三件保留原1mm短压目标，第四没有侧压。新释放局部法向清障包络30mm，只有双OPEN才执行，再接原RRT/FCL转场；不要求helper跨过整个中央槽120mm退出。
- [ENGINEERING] 新执行器带CLOSED/OPEN及原80Nm原始关节effort互锁、有限候选、失败双OPEN并回写当前Cube，保留旧可执行节点。无执行探针不构造Arm或发布joint/suction/feed/rail，也不修改远程PlanningScene/ACM。
- [EXPERIMENTAL] 名义IK种子/盒体检查及本机headless验证只建立工程可行性证据；没有校准接触wrench或P2内部力/P3力位混合控制。推墙阶段只有当前移动Cube按旧接触策略不作静态障碍，其余桌/墙/已放块与全部机器人碰撞检查保留；不声称这就是移动物体的完整连续接触动力学证明。
- TASK01仍IN_PROGRESS / DRAFT /36nulls；模型/物理参数和YAML/hash保持不变。新版5/5未验证前，不借用旧df9c2c0的5/5作为新版PASS。

## D018 final validation — 不把一次成功扩大为方法或可靠性证明

2026-10-04；[ENGINEERING]。保持源码和原门限不变完成一次零预置/hold=0 的实际五件回归。旧 Cartesian/continuous-seed 优先，有限 RRT 仅双吸盘 OPEN 且前者拒绝后使用；本轮未触发，不能用 5/5 为其实际执行背书。失败重放 01、历史 Cube02 回带和 MoveIt teardown 继续保存。

[EXPERIMENTAL] 慢速 scale=5 / OMPL RNG 不受控的一轮本机 headless 成功只证明该次流程到位。停止本轮自有测试进程，不继续循环来声称稳定。TASK01 的论文接触协议、材质/质量、力/时间测量与 36 数值冻结需要用户审查；不因 demo PASS 自动推进 TASK02。没有新增 [DEVIATION]，既有 D014 第四件适配与前三件 D004 差异仍单列。

## D018 validation — Check original goal semantics, keep negative evidence

ENGINEERING: evaluateendpointusingactualMoveItconstructedgoalconstraints insteadofinventingaggregate-anglegate; numeric/seed/bounds remain. Frozenacceptancevaluesunchanged. Beforephysicalcommandsverifyroundedfailedstate/railshift andtemporaryabsent-IDsynccleanup withnorobotpublishers. Preservefailedfirstreplayanddo notinferexisting-objectrestoreverifiedfromabsence-onlycase. Actualrunusespinnedbinary/source; nogoal/scene/material/ACMchangesmidrun.

## D018 — Reuse bounded free-space RRT only after physical release

2026-10-04; ENGINEERING. User“那你继续，我记得之前退出都是没问题的啊”requestscomparisonandrepair. KeepCartesian/localcontinuousseedfirst; ifrejectedandbothcupsOPEN, ≤3RRTConnectrequests/arm,3s/request, samefullmeasuredstartandoriginaltargets. PreservecurrentreleasedCubeinworld/MoveItplanningandjointFCL, checknumeric/bounds/firstpointnotadapter-shifted/endpoint, ranksbyexistingjointtravelscore. Temporarilyaddedworldobjectmustsynchronouslyrestore,elseabort. No loadedXYZ/contact/scene/material/ACM/gate/paperchange. Roundedreplaymustusepreviousbatchrailshift0.1m; noexactA/Borfullphysicsclaimfromreplay.

## D017 — Repair measured start before entering the blocked diagnostic window

ENGINEERING: newdiagnostic revealspre-releaseactualsideplanningmixescommandjointseedwithmeasuredCubeGT. Reuseexistingone-RobotState seedmechanismforindependentactualsideentry; validateCLOSEDpusher/OPENhelper, jointfinite/count/bounds andoriginal0.035radcommanddeltagate. KeepcurrentCubeinFCL, allphysics/contacttargets/protocols/ACM unchanged. Ifmeasuredstartstillcollides, stop; do notallowpairtoobtainPASS. Thisprerequisiterepairdoesnotestablishrelease-driftcause. Nextordinaryfullfivehasdiagnostichold0, nosilent3sdelayfix.

## D017 checkpoint — Diagnostic timing is not normal-flow evidence

Keep3s hold strictlyopt-in/default0. Enddiagnosticaftersecondcompletedbatch andbeforelaterobjectmotion toavoidfixedsimduration interruptingloadedtask. Do notcallfirstcubestabilitysecondcube repair ordiagnosticPASSordinaryfivePASS. Maintainasynctag caveat andcollision-versusD6 distinction; addpeak/mixedstep regression beforeusingcontactsummary. Noactivecontrol/physics/contact/gate changefromthischeckpoint.

## D017 — User-approved release/withdrawal repair, evidence-first scope

2026-10-04; user“继续”followingexplicitproposal permitsminimalrelease/clearanceengineeringrepair. Firstaddread-onlyphase/tool/contactobservations andoptionalpostreleasehold; ifcubeisstablebeforefirstwithdrawal, inspectactualseed/pressure unloading/trajectory ratherthanchangefrictionorforcegates. Adiagnosticholdrunisnotordinaryfull-flowproof. Preservemodel/material/ACM/gripperparameters/successgates/YAML; stopifcontactredesign/forcecontrol/benchmarkchoicebecomesnecessary. PriorD004gapstillpending.

## D016 validation — Scope completed without expanding into loaded/release control

2026-10-04; XYZactualtwo-correctionPASS, but new laterCube02deep-wallfailure5.138mm retained, rather than claiming full-flowPASS or adjusting3mm gate. Stop after safe diagnostics/records; fixing release/withdrawal/contact or adding force/physics changes is a distinct next scope. Originalmodel/material/ACM/contact/loadedflow and36nulls preserved. Report TASK01_PRECLOSE_XYZ; BUG-016. One negative normal-feed run is enough to reject stability, not prove physical impossibility or a specific contact-force root cause.

## D016 — User-approved merged XYZ pre-suction correction

2026-10-04; [ENGINEERING]. User “好的，那就这么做” approves described XYZ extension/speed policy. Apply only when original attachment gate fails and both cups OPEN; accumulated command-FK plus actual residual, total1mm vector bound, same fineIK/FCL/orientation, maximum3checks. No separate X/Y/Z RRT, no correction when already valid, timing recorded. No authority inferred to change mass/material/contact topology/gates/freeze36fields or implement paper force control. Old Task26/27 nodes retain Y-only semantics; current precision variant receives the change.

## 2026-10-03 — Full-run failure retained, no autonomous compensation expansion

Actual no-preplacement run failsCube02Xcorrespondence3.150mm>2.500mm afterYconverges0.001mm; onlyCube01placed. Keep same scene/model/control/gates and stop this test-only iteration rather than silently addXYZtracking compensation or relaxacceptance. Next scope should first isolate FK/tracking/metrology, then discuss bounded ungraspedXYZrepair; noforcecontroller/contactredesign/numericfreeze inferred. Earlierisolated/continuous4→5PASS remains true but cannot establish current full-five stability. TASK01IN_PROGRESS/TASK02TODO,36nulls unchanged.

## 2026-10-03 — Full-flow regression without expanding scope

[ENGINEERING]/[EXPERIMENTAL]: repeated user continuation permits testing current approved variant from normal feed, not redesigning physics or contact. No preplacement and no runtime code/model/gate change. Actual five batch PASS and exit code are required for full-demo evidence; ARRIVED alone is insufficient. A failure requiring material/research decisions stops for tomorrow. Existing36nulls/TASK01 review/D004 first-three discrepancy remain unresolved even if this demo passes.

## D015 validation / hard-decision boundary

2026-10-03; [ENGINEERING] scoped repair physically verified by isolated fifth and fourth/fifth pair, no currentCube exemption. [EXPERIMENTAL] first3/4preplaced; no full-five or stable benchmark assertion. Stop before choosing effective-friction baseline, modifying retained hidden mass, changing first-three D004 protocol, or approving36numericfields. These are material user decisions, not inferred from the instruction to continue independently. Preserve0.5/0.5 actualphysics and originalscene/gates tonight. TASK01 IN_PROGRESS, TASK02 TODO.

## D015 — Engineering continuation limited to already-released empty arms

- Date: 2026-10-03.
- Classification: [ENGINEERING], no paper-method or contact-protocol change.
- Decision: In the approved Cube04 independent variant only, use measured dual-arm seed after confirmed OPEN. Ordinary Cartesian first; bounded piecewise fine-IK seed continuation as fallback, same targets. Include the released Cube in synchronized full FCL and retain all original gates. No feedback/contact/model/physics adjustment to cure drift.
- User boundary: Continue independently only while no hard research decision is needed; stop and record choices if model/material/contact strategy needs to change. Freeze gates remain pending/36 nulls, TASK02 untouched.

## 2026-10-03 — D014/D015 validation boundary
- Final slow trial validates actual fourth single-rear protocol once with original gates; preceding faster trial failed. Report limited feasibility, not stable/five-Cube reproduction. Fifth empty Cartesian exit is independently refused by existing geometric guard. Do not change fifth protocol or hide this negative by calling fourth batch PASS whole-process PASS.
- Recommended next engineering step: safe empty-retreat start-state/IK candidate diagnosis, then repeated fourth→fifth tests. No scene/tool/material/gate change, force controller, research-baseline shortcut or numeric freeze.

## D015 — Retain failed pure single-arm test before considering feedback
- Date: 2026-10-03; [ENGINEERING]/[EXPERIMENTAL]. Cube04 precise-stage variant fails final 1.5-mm neighbor gate at 1.827 mm; do not restore inner trim, widen gates or declare physical impossibility after one sample. Repeat clean physics using final built binary and slower unchanged motion protocol.
- An online lateral-tracking controller would be additional method work, not simply reusing Cube05. Ask before changing that research protocol; all frozen/numeric questions stay pending.

## D014 — Authorized Cube04 single-rear insertion variant
- Date: 2026-10-03; [ADAPTATION]/[DEVIATION], explicit user approval: “那第4块采取第5块的推入方式”. Cube04 is an exception to D004; no blanket approval to change first three or freeze numbers.
- Add an independent executable reusing existing Task26/27 code, guarded compile-time policy; old targets preserve behavior. Do not change original Isaac scene/tool/mass/material/ACM or final placement gates.
- New Cube04 PRE_PUSH Y control target uses Cube02 GT plus 120 mm and original 0.5-mm pressed target; replace post-seat lateral trim, not geometry. Added <=0.5-mm Y engineering staging gate and nonnegative oriented-neighbor projection clearance; no force-control/paper fidelity claim.
- Experimental validation may pre-place/physically settle only the first three; fourth/fifth use normal feed and actual transport. Keep this distinct from all-five proof; YAML remains unchanged/DRAFT.

## D013 — Exhaust non-mutating fixed-contact alternatives before changing tool
- Date: 2026-10-03
- Classification: [ENGINEERING] exact OBB roll diagnostic, not motion planner or paper method.
- Decision: Preserve the user-required face-center contact and inward normal; test discrete TCP rolls on existing tool geometry before asking for alteration. At 15-deg spacing all 24 checked Cube04 poses retain support/neighbor interference. Record this scope; do not infer continuous-search completeness or accept no-box-interference as full IK/path safety.
- Impact: No physics/ACM/contact-position change. Request direction on model/protocol rather than silently adopting half-cup/edge contact.

## D012 — Successful old demo is not authorization to change benchmark physics/contact
- Date: 2026-10-03
- Classification: [ENGINEERING] exact geometry/actual-material readout and full-rate metrology; [EXPERIMENTAL] controlled hold; [DEVIATION] legacy protocol mismatch explicitly identified, not accepted as replacement.
- Decision: Keep ordinary 5/5 PASS separate from D004 fixture and TASK01 freeze. When current face-centered helper pose intersects neighbor, require direction before altering tool/contact/order; do not use ACM/edge-cup shortcuts. When actual Cube friction 0.5/0.5 differs from deleted authored material 0.90/0.75, ask whether to retain actual values or restore/revalidate; don't silently change physics under a bug-fix label.
- Measurement: Use every explicit-hold physics step, report mean bias and raw RMS/peak separately. Do not suppress alternating loads or claim per-cup/internal wrench calibration from correct average support; velocity-vs-pose consistency remains open.
- Impact: TASK01 IN_PROGRESS with unchanged YAML/hash/36 nulls, TASK02 TODO. Scientific review stop follows AGENTS stop conditions; no paper method or numeric/model approval inferred from “until task01 works”.

## D011 — Controlled static-load hold keeps telemetry running
- Date: 2026-10-03
- Classification: [EXPERIMENTAL] static metrology pause; [ENGINEERING] test-only control parameter and phase marker.
- Decision: Do not SIGSTOP a ROS manipulation process for a measurement window: it also stops callback processing and invalidates in-flight state requests. Archive the failed experiment; use task01_calibration_hold_sec only when explicitly requested, default 0, pause task progression while executor stays active and suction/geometry gates continue.
- Impact: 7-s hold changes this experiment's timing and cannot count as an ordinary timing/reliability trial. Physics, grasp stiffness, model masses and benchmark gates remain unchanged. Received hold phase is stamped at physical observation, not claimed to be exact actuator-event timestamp.
- Review: Near-unbreakable suction and hidden branch mass remain proposed inherited model features, not approved numeric freeze; ask user before changing them.

## D010 — Repair quantization without weakening alignment or bypassing protocol review
- Date: 2026-10-03
- Classification: [ENGINEERING] bounded residual/local-FK correction and scaled-transform extraction; [EXPERIMENTAL] normal-feed regression.
- Decision: Remove mandatory 0.650 mm pre-close step, keep maximum 1 mm, original 0.300 mm physical gate and three attempts. Use seeded local FK micro-IK only while ungrasped, with conservative scope/joint bounds and unchanged full synchronized FCL. Task26 default unchanged.
- Measurement: Task27 scale removal fixes its quaternion only, not USD frame lag. Explicit official asset root only avoids directory discovery failure; same FR3 source still required.
- Scientific boundary: A repaired legacy five-Cube demo is not automatically D004 fixture-protocol or TASK01 freeze evidence. No benchmark numeric approval, geometry/mass/material change, ACM expansion or paper implementation is authorized by persistence request.

Append-only architectural and scientific decisions.

## D001 — Two-platform strategy
- Date: 2026-09-29
- Decision: Isaac Sim + ROS2 is the final common benchmark; MuJoCo is an auxiliary force/contact laboratory mainly for P2/P3.
- Reason: preserve fair final comparison while accelerating force/contact debugging.
- Impact: baseline algorithms remain platform-independent and use adapters.

## D002 — Baseline-first rule
- Date: 2026-09-29
- Decision: `ours/` remains algorithmically empty until TASK30.
- Reason: derive our method from reproducible evidence and failure cases rather than premature design.

## D003 — Task27 as TASK01 geometric starting point
- Date: 2026-09-30
- Classification: [ADAPTATION]
- Decision: Use the existing Task27 dual-FR3, fixed L-side-suction, rail and five-wide truck-box scene as the *starting geometry* for the common benchmark draft.
- User input: Explicitly confirmed "对" in response to this proposed starting point.
- Scope: This does not freeze the existing physics, grasp/contact topology, perturbations, timings or success thresholds. TASK01 stays IN_PROGRESS until the candidate and all values are reviewed and validated.
- Impact: The Task27 source constants are traceable in `configs/benchmark/benchmark_v1.yaml`; unresolved choices stay null rather than inheriting unsafe demo defaults.

## D004 — Different contact protocols for the first four and fifth cubes
- Date: 2026-09-30
- Classification: [ADAPTATION] for the common Task27 cell; [EXPERIMENTAL] for the task-specific staged contact sequence.
- Decision: Cubes 01–04 may start from coarse safe PRE_PUSH staging and are pushed toward the deep wall with a rear-face suction primary arm and a side-face suction constraint arm. At deep-wall contact, the side arm presses laterally while the former pusher holds the deep-wall constraint. Cube 05 is precisely aligned at PRE_PUSH, then inserted by one rear-face suction arm; the other arm makes no Cube contact.
- User input: Explicitly distinguished the first four dual-arm adjustable placements from the fifth single-arm precision insertion.
- Scientific boundary: Cube 05 is not a two-arm insertion test and must not be reported as evidence for a reproduced cooperative insertion controller. Cross-method results must distinguish the dual-arm fixture phase from the single-arm center phase.
- Still open: pre-push tolerances, primary arm assignment, contact-force limits, B-case perturbations and physical validation. No values are frozen by this decision.

## D005 — Isolated Cube 05 arm-symmetry probe, not a benchmark shortcut
- Date: 2026-09-30
- Classification: [EXPERIMENTAL] test fixture and [ENGINEERING] test-only arm selector.
- Decision: For the arm-symmetry feasibility probe only, directly place Cubes 01–04 at their final cells, require actual Isaac physics settle, then feed and execute only Cube 05. Run left and right from separate clean scenes. Keep the legacy controller's default `center_pusher_arm=right`; choosing left requires an explicit parameter.
- Reason: Compare whether either arm can physically perform the fifth-Cube single-arm push without spending four prior cycles on each test. This does not validate first-four placement or freeze the benchmark.
- Numerical implementation: 100 nm comparison guard at the 1.5 mm inner-side-gap boundary only, to absorb an observed 38 nm float32 serialization excess; neither the target geometry nor the material threshold changes at meaningful precision.
- Impact: Results are labeled [EXPERIMENTAL], with separate run metadata and raw log pointers. TASK01 remains IN_PROGRESS.

## D006 — Keep Cube 05 repeatability evidence exploratory
- Date: 2026-10-02
- Classification: [EXPERIMENTAL] repeated fixed-fixture trials; [ENGINEERING] read-only logging and pose-source probes.
- Decision: Record right/left 3/3 physical passes as a small-sample feasibility result only. Do not freeze a reliability number, arm-equivalence claim, or contact-dynamics metric from these trials: OMPL seed is uncontrolled, four fixture Cubes were pre-placed, and contact wrench is absent.
- Measurement rule: Final settled `/task27/cube_poses` is usable as Isaac Bridge Ground Truth for this exploratory position report, but motion-time USD and PhysX poses are not yet a synchronized measurement contract. Keep their discrepancy open as BUG-005.
- Impact: TASK01 remains IN_PROGRESS with 36 unresolved configuration fields; no benchmark thresholds, geometry or Task27 control logic changed.

## D007 — Diagnose and isolate measurement errors before benchmark freeze
- Date: 2026-10-03
- Classification: [ENGINEERING] read-only sampler/environment launcher; [EXPERIMENTAL] deterministic free-body calibration; [ADAPTATION] Isaac Ground Truth to ROS.
- Decision: Add a separate optional PhysX post-step pose/velocity channel with one simulation stamp and step number per snapshot. Reject invalid physics handles rather than falling back to USD. Keep Task27 control and legacy topics unchanged while documenting their defects.
- Reason: USD callback positions lag the physical state; quaternion extraction from the scaled Cube transform is independently wrong. Dynamic contact metrics cannot be validated from these old measurements.
- Validation: External ROS known-motion calibration at 60 Hz physics with 30/20 Hz frame updates, without contact. Explicit zero damping applies only to that calibration body, never to the Task27 scene.
- Impact: Old exploratory settled position metrics remain traceable; old yaw metrics are marked invalid for physical 6D claims. TASK01 remains IN_PROGRESS, TASK02 interfaces remain unfrozen, and no contact-force or paper fidelity claim is introduced.

## D008 — Separate collision wrench, mount reaction and contact estimation
- Date: 2026-10-03
- Classification: [ENGINEERING] same-step telemetry/buffer handling; [ADAPTATION] Isaac impulses to world N/Nm; [EXPERIMENTAL] known-load calibration fixtures and nominal full five-Cube probe.
- Decision: Calibrate collision normal/friction forces and moments separately from suction D6 loads. Use an isolated articulated mount to test reaction availability and frame/reference-point conventions, not to silently insert a new FR3 load-cell joint. Keep real FR3 raw reactions explicitly raw until gravity/inertia compensation, sign and TCP moment shift are validated.
- Reason: Suction can support 7.848 N while collision signals are zero. Actual FR3 has retained hidden-body mass; raw reactions are therefore not end-effector contact estimates.
- Numerical boundary: Calibration gates/known loads belong to the independent metrology fixture, not benchmark acceptance thresholds. No TASK01 numeric field is frozen from these experiments, and no legacy model mass or control parameter changes.
- Full-flow boundary: Normal-feed Task27 five-Cube probe uses the existing controller without pre-placing the fixture. Controller log alone establishes its actual physical completion; five feed ARRIVED flags do not prove five placements. Paper fidelity/contact topology still needs separate review.

## D009 — Validate physical reference; retain negative full-flow results
- Date: 2026-10-03
- Classification: [ENGINEERING] raw naming/model checks/metadata; [EXPERIMENTAL] axes/anchor fixture; [ADAPTATION] eventual TCP wrench mapping.
- Decision: Verify actual physics COM, no rigid-body scale in reference fixture. Test link/principal/joint axes crossed with link origin/COM/joint anchor. Final result is joint axes/about joint anchor. Explicitly invalidate earlier scaled-body inferences, preserve raw software PASS.
- Impact: Real FR3 reactions stay raw until actual joint frame/anchor, gravity/inertia and TCP shift checks. Failed asset-root startup is not a successful frame audit.
- Full flow: Record 5/5 planning-only but 1/5 physical completion, Cube 02 pre-close overshoot separately. Never widen the 0.300 mm gate to accommodate minimum 0.650 mm correction. No legacy controller fix in this read-only scope.
- Freeze: 36-field checklist is a review queue, not approved values. Keep YAML/hash unchanged, TASK01 IN_PROGRESS, TASK02 TODO; no early paper algorithm/model mass changes.


## D016 — Single-Cube scientific benchmark; legacy five-Cube flow is non-blocking
- Date: 2026-10-06
- Classification: [ADAPTATION] benchmark architecture.
- User approval: explicit.
- Decision: benchmark_v1 uses one shared Cube, dual FR3 and one carriage. The legacy five-Cube Task27 application is preserved as a later application/stress test and no longer blocks TASK01.
- Reason: the research question is tight cooperative transport plus constrained cooperative insertion, while the inherited five-Cube sequence introduced unrelated multi-object sequencing, retreat and fixture constraints that prevented progress toward paper baselines.
- Force boundary: TASK01 freezes geometry/frames/material/time/start-goal only. Isaac TCP/contact-wrench calibration moves to TASK10-IS, before P2 Isaac migration. P4 is not blocked by force sensing.
- Nominal material candidate: retain the measured effective 0.5/0.5 static/dynamic friction for benchmark_v1 candidate; P3 may later vary friction as robustness perturbation. Final freeze still requires user review.
- Historical evidence: no old result is deleted or re-labeled; old five-Cube reports remain historical evidence only.
