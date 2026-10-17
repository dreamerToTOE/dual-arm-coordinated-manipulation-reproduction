# ABB RSS SOURCE_CONTRACT_STATIC V1（2026-10-16）

六环境RSS仍PARTIAL。本次只读ABB作者 `CKCplanning@909bd72` 控制流与旧保存输入；II/III共用源码，资格结果必须分开。RRT、CBiRRT、SBL的局部控制并不统一；特别是CBiRRT检查用RBS，导出却另用0.1步长投影程序。尚未启动资格运行。

基线 `b67668db77df5b442288bd12614a402bb2c4bcf2`。仅新增本MD/JSON；编译、项目import、binary、FK/IK/J、碰撞、随机/采样、RBS、solve、协议/claim生成、新候选均0。源码、旧样本、协议、211表与账本未改；VI974/974不动。另一名只读审查者独立核对SBL/SVC四文件并取得相同SHA和映射。

## 1. 首先固定分支含义

状态顺序为arm1六角、arm2六角；`active_chain=0`固定arm1，指定分支求arm2。`identify_state_ik`的ik[0]为arm2分支，ik[1]为反向arm1分支，使用原始关节欧氏距离<0.1的首个匹配，并非奇异点全部相邻分支集合（SVC:23–40、140–161、322–371）。`-2`为规划器写入的singular样本标签，不能替代真实Jacobian秩。

**旧clear记录的`active_branch`不可直接当RBS分支。** 旧构造给定奇异arm2，再用`K arm1 branch`求arm1；其1/3/5/7等标签属于arm1。RBS这里反向求arm2，需要另行绑定被动分支身份。四个已保存合格regular端点的arm2分支为II_0=3、II_1=0、III_0=1、III_1=3。26个clear候选仍全部是奇异候选，不能把两枚候选当成已合格regular↔singular桥。

## 2. 三规划器如何传sg和branch

源码路径下文省略前缀`CKCplanning/planners/`；SVC为`validity_checkers/StateValidityCheckerRSS.cpp`。

| 控制 | RRT_RSS | CBiRRT_RSS | SBL_RSS |
|---|---|---|---|
| 奇异请求 | 非goal分支概率.2；调用后sg=true | 概率.20；mode=3，普通mode1、树连接mode2 | 实际.05，注释20%；调用后sg=true；同投影格选父节点 |
| 存-2 | 仅sg且range确实reach | 仅mode3且reach | sg即存-2，新边lazy valid=false |
| 从-2节点向普通状态扩展 | 只选0或3（203–207） | rand()%8（162–165） | 取当前树的起/终点分支；startTree此前已翻转（155–157、220–224） |
| 普通→奇异新样本 | sg2,active0,继承普通分支（231–233） | mode3reach时sg2（204–218） | lazy子节点-2时sg2,父分支（391–392） |
| 奇异→普通 | sg1,active0,选定分支（235–237） | 父-2时sg1（219–220） | lazy父-2时sg1,子分支（387–388） |
| 普通→普通 | 普通RBS,active0,b（240） | 普通RBS,active0,b（222） | 必须两分支相等，普通RBS（395–396） |
| 奇异→奇异 | 到奇异target拒绝父-2（194–195） | mode2双-2拒绝（192–193）；mode3拒绝父-2 | 树间桥拒绝双-2；树内采样未排除父-2（205–212、304–309） |
| 最终回溯 | 按最终路径端点-2重新选sg1/2，恰一奇异端点与checker一致（393–402） | **不调用reconstructRBS**，另调serial reconstruct（591–594、627–661） | 恰一奇异端点方向/分支一致；goal树反向后按端点重选（595–620） |

CBiRRT还有一项确定的不对称：**mode2树连接在“普通父→奇异树target且reach”时走普通RBS，而非sg2**，新节点也存普通分支；mode3的新奇异样本则走sg2（158–231）。实际影响待隔离运行，不能据此声称已观察错误路径。

SBL树内双-2父子若出现，lazy优先父奇异，传sg1/branch=-2；回溯优先末端奇异，传sg2/branch=-2。`IKsolve_rob`直接用branch索引八元素数组（APC:117–141），没有前置合法性guard。此为确定源码风险、实际触达UNKNOWN；**不得为了复现而直接运行负索引未定义行为**。

## 3. RBS与reconstruct的精确停止契约

SVC:388–624，头文件:222–224。所有距离均12角原始欧氏距离，逐分量算术中点，无周期最短路处理。

| 项目 | checker | reconstructRBS |
|---|---|---|
| 常规叶门 | 先d<.05直接true | 先将iteration加1，再d<.05直接true |
| 深度 | 初始0，d未停且depth>150失败 | 初始0但先++，d未停且iteration>150失败；非叶边界比checker少一层 |
| 中点资格 | 固定branch投影成功且withObs时碰撞谓词为0 | 相同isValidRBS |
| 奇异方向 | sg1参考首端，其余参考末端 | 相同 |
| 奇异提前接受 | 首层投影后距参考<15×.05=.75即true | 相同阈值，但**返回发生在插入中点之前**，输出可只有原两端 |
| 后续递归 | 奇异首层未提前接受，则两子调用均转普通重载，丢弃奇异参考 | 相同转普通重载 |

因此“源码check=true”不蕴含所有输出叶<.05，也不证明连续闭链/连续无碰撞。常规check与trace的深度边界也不完全等价；尚无新运行反例。

**CBiRRT另有导出算法。** `reconstruct(Motion*,Motion*,M)`以`n=int(distance/.1)`、i=0…n、比例i/n插值，固定regular侧分支投影并push；没有碰撞调用。d<.1时n=0的除0风险、双-2或不等regular分支时ik_sol未初始化也无guard（627–661）。这是导出契约差异，不可将其称为原RBS trace。smoothPath调用被注释（579），不纳入活跃调用链。

三规划器`save2file`均void。回溯失败仅打印并从导出返回，调用方仍可添加solution；故OMPL状态或“Solved”日志不足以通过独立路径门。另RRT的`if(0 && sat)`禁用了exact goal赋值（255），退出时仅有approxsol fallback（269–275），`final_solved`据approximate置false（318）；必须保留字面来源结果，不能按外层bool把它升级为精确解。

## 4. checker、碰撞、限位与循环

`isValidRBS`只调用固定分支`IKproject`，失败false；成功且`!withObs || !collision_state(P,q1,q2)`才true。withObs默认true。ABB这条RSS链没有Comau的checkEE调用；不能移入“两TCPz≥10mm”后仍称原生同条件。

固定分支IK对**求出的被动臂**检查原界（APC include_joint_limits=true）；SVC并无另查完整12角主动/被动界或独立闭链残差/真实秩的门。碰撞源PQP tolerance=8，读`CloserThanTolerance()`：1碰撞、2 rod异常、0 clear；其逻辑返回值与PQP API返回码不同（collisionDetection:263、480–493）。原坐标与aligned适配的差异仍须分别报告。

生产`sampleSingular`在循环外一次rand()%3选mode，mode0/2固定原−PI_/2肘角，mode1腕q5=0。每轮[-PI_,PI_]采样arm2、反解arm1、随机取可行根，写状态，仅显式拒绝反向ik[1]==−1，再要求碰撞false；没有完整arm2原界/真实rank检查。`do while(!valid)`不读ptc、无次数或时间门，外层solve超时不能在其中生效。三caller忽略返回bool后设置奇异标记；函数当前仅在valid后返回true（SVC:255–305）。不能推断一定挂起，也不能用外层限时保证请求有界。

plan_RSS全局isStateValid恒true（41–43）；其状态空间用近似舍入界且q6缩为±PI_（79–104），与原机械±400°不同。全局检查器不能代替独立资格。辅助all-branch IKproject有循环无break问题（SVC:165–193），sample_q也有不同的`collision && !limits`拒绝条件（196–251）；主RSS控制/RBS使用固定branch helper，不能把辅助函数的结果冒充已核主入口。

## 5. 最小有限资格路线：建议，尚未冻结或执行

1. 先绑定旧10/16 clear根的原q、mode、arm1构造branch、保存碰撞与源版本；JSON列出全部26份身份/SHA。保留旧0/100及其失败。不能只凭-2或arm1 branch选被动branch。
2. 可先冻结四个代表：II_obs0681/0689、III_obs1065/1073（各环境mode1/2首个clear case）。每个**同一原输入**仅枚举原被动IK branch0…7，共最多32次固定输入roundtrip，保存输出角改变、canonical wrist变化、真实branch/闭链/秩/限位/源碰撞。此步无新中点/采样，不保证能产生合格regular邻点。
3. 若独立branch契约支持，再单独冻结最小桥诊断：II_obs0681配旧II_0、III_obs1065配旧III_1，预置被动branch3，各正反方向，共4次singular checker和4次reconstructRBS；若branch3不相邻、投影失败或碰撞，就保留失败/不合资格，不能临时换节点。此表仅提案，不是执行协议或授权。CBiRRT serial导出应单列诊断，不混为同一RBS输出。
4. 每项执行前另定明确墙钟/CPU及操作上限。有限提案例：上述8项checker/trace每项最多16次中点投影，共128；保持原.05/.75/depth150，外层计数到限标UNKNOWN_BUDGET_STOP，禁止重试/加深。具体额度仍待主代理冻结并确认授权覆盖。本报告没有生成协议、claim或新预算。

这条路线检验旧源控制与现有保存输入，存在明确可审查的验证方法，但不承诺数学连接存在。要取得真正跨分支RSS路径，仍需全部节点/分支/闭链/真实秩/原界/碰撞/trace叶距和start→goal独立审查。

观测wrapper、输入绑定、负索引/n=0 fail-closed门及导出状态传播可作为版本化工程诊断审阅；不得更改合格门。换邻点、扰动中心、改分支选择/连接器/肩模式、改变停止阈值或把SBL .05统一为冻结γ=.2属于科学设计/参数裁决；先审批再执行。源literal、已审IK修正、aligned碰撞三层来源必须明确，不能互相冒名。VI974/974不得借用，任何未来ABB中点都须独立计入获准R2账。

## 来源SHA

完整14份作者源码、38份保存输入SHA和逐项行号在同名JSON。关键值：

- 作者SVC cpp：`133e1f7036583b3e6a5ae9d9df978a679df9af88c5103d195e727546934fd8c6`
- 作者RRT cpp：`3c86eeb3f9fcc1a4e984bcbbda89cef90f493f70b92b32874bf9c6e1afe15486`
- 作者CBiRRT cpp：`3d5a84a999637beef574c22fe436963c85376acc96727c0da0ea86762f94912a`
- 作者SBL cpp：`1a52d9fae20d0aa98f7c22c28139c581ac6e20451f8a4ab17f6e242826a9c2fc`
- 本次JSON：`bd81f6f3d89a3e7648d35147fa19af79ce9827fb89bf81cfe2fa255b79f87177`

全部绑定输入写报告前后字节相同；未提交/推送，由主代理审阅。原211全文义务、正式0/22500、原γ=.2与source SBL .05争议均保留；无P2/Isaac/FR3实施。
