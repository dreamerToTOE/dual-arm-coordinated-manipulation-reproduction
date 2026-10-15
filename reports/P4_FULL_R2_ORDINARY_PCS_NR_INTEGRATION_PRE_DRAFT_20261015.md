# P4 R2 普通PCS/NR方法整合 PRE草稿

2026-10-15，PRE / READY_FOR_ENGINEERING_FREEZE。已完成固定条件与调用计数的两方静态审查；先提交冻结工程协议，构建成功并绑定实际产物后再冻结科学协议，依次单次执行。接续原R2，不新增额度，不更改211项义务或正式0/22500。VI原Q2仍UNKNOWN，新获批组合仅离散通过；普通方法按模型继续资格。

## 科学目标与首个有限切片

从已合格数学组件推进**作者固定分支PCS投影、真实RBS递归与回溯接口**。首先整合ABB的II/III，同一固定作者版本909bd72、原900/300与1200/500mm、原3.1416基座/抓持/关节界与碰撞原查询。I循环3R、IV/V同系双Comau及VI多闭环随后复用同一日志/冻结接口逐项资格，不能把ABB通过写成其余环境通过。

首片只链接作者RRT_PCS/CBiRRT_PCS/SBL_PCS源，不分配或调用solve，不跑随机sample_q，不做RSS。后续NR先以现physical_nr为oracle，C++实现与原KDL失败分开；I为3×20、II–V为6×12、VI为12×18同时伪逆，不能以VI原GD12+IK3顺序程序代替。共用接口不代表混合作者同名类或换模型。

## 复用与新增文件/API

| 资产 | 用法 |
|---|---|
| spatial_ik_patch.stage_spatial_ik | 到外部新根建立abb数值修复stage，先验证全作者文件manifest，不改原快照 |
| 原SVCPCS固定`IKproject(q1,q2,active_chain,branch)` | active_chain0=arm1主动/解arm2，1=arm2主动/解arm1；branch原0..7，不用随机重载 |
| 原`checkMotionRBS`、`reconstructRBS` | 原.05全12L2、maxdepth150、实际算术中点/固定branch/原collision，保留全部返回；外部调用帽截断为UNKNOWN，不能当原false |
| 既有A01 II_0/II_1/III_0/III_1 | 读取selected_q_rad、原始q、全部候选和合格状态，不重新恢复端点 |
| 原PQP native + 合格v3 adapter | 内部RBS维持原native collision；每个输出另跑已合格native/aligned并记录两结果，不能隐改source内部坐标 |
| recover_p4_full_r2_endpoints工具 | 独立FK/闭合/原界/几何branch oracle，原physical_nr不变 |
| `abb_pcs_qualification_driver.cpp` | 项目自有JSONL薄API：project / rbs / reconstruct / limits；没有随机/solve入口 |
| `pcs_source_trace.hpp` | 项目自有调用边界、输入输出、原生FK/IK/PQP计数和前缀，原函数body在lambda内原样执行 |
| `build_p4_full_r2_abb_pcs.py` | 外部新stage、plain/trace×author_native/geometry_consistent四构建；原未许可source/mesh不进入Git |
| `qualify_p4_full_r2_abb_pcs.py` | 固定条件、atomic claim、原返回与独立资格、source-equivalence、预算与未执行前缀；draft只有读文件/数组生成 |

## 原source风险，不静默修理

1. SVCPCS随机IKproject重载for循环成功后无break，循环结束i==8返回false；首片完全不调用该重载，但源码SHA/缺陷保留，不据未用重载阻挡固定branch资格，也不隐修。
2. check_angle_limits在APC.cpp明示true=全12在界内。PCS两个sample_q用`withObs && collision && !limits`，会漏拒碰撞且合法界/无碰撞且越界；不是check函数语义相反。首片不调用采样；将来完整PCS接入必须版本化处理并留source-native对照。
3. isValidRBS只调用固定IKproject后判原collision；未独立重检全12界/闭合。外部门必须检查，但不得把外部门改写成原source本来做过。d<.05提前true是源条件，非法端点负控不能当违反其“端点已有效”假设的理论反例。
4. 数值修复只用已经审查的spatial_ik_patch；四目标分别是原数值plain/trace和R2修复plain/trace。除去记录包装后同variant body必须原字节语义一致，source-equivalence逐固定调用输出比较；不更改SVC循环、碰撞、限位、tol、midpoint、分支或steer。
5. 原source collision对齐与物理FK有已知差异；本片保留其返回，再调用v3选aligned独立资格。source返回true不能自动成为合格RBS或全物理/CCD证书。

## 固定输入与调用计划

只读取四个A01中心。每中心×active_chain0/1×branch0..7，共64个根枚举project请求。每个请求同时送四目标，**256次顶层project**；plain/trace结果在同数值variant逐字段相等，原数值FAIL和R2PASS分开。

每中心/角色在R2固定64组结果中，按原全12欧氏距离最小、branch最小tie，选择闭合/原界/与中心原几何branch一致的根；这只是预先定义的局部fixture身份，不换原端点或用碰撞筛branch。不具候选则该角色前缀NOT_QUALIFIED，不搜另一中心。基准取原中心本身，选branch后不把root输出替换中心。

每中心/角色取主动臂第一个关节，h=min(.08rad,该主动坐标原bound margin/4)，±h各一，共16条固定主动扰动。h/坐标/符号在draft数组中冻结；不使用过去微小h造成原RBS全部阈值提前通过的组作为充分RBS证据。每扰动送四目标：**64次顶层project**；投影结果形成明确有来源的候选端点，不冒称原论文端点。若完整距离<.05，记录VACUOUS_SOURCE_THRESHOLD，不补大h。所有失败保留，不换branch或缩h。

最多16对×4目标=64次顶层rbs；只有对应rbs源返回true才最多64次顶层reconstruct。每次原RBS/重构最多64固定branch内部投影、128递归入口、256nativeFK、8192实际PQP调用，超帽抛出独立CAP并保留已执行前缀，不改source返回false。plain无法观察内部次数，采用trace相同输入已证输出等价及独立进程CPU/墙帽；plain仍计“未直接观测”，不伪称其内部次数实测。

另每中心两个固定负控：原始12维端点闭合FAIL重验；中心q0改为原上界+.01rad（其余不变）的限位拒绝；共8个独立node负控，无投影或RBS补救，不把不满足原前置条件的输入称原算法反例。碰撞引擎已有12正负控制不重跑；新增候选若碰撞，真实记录并保留。

独立验收覆盖trace捕获的全部有限成功固定投影输出（根/局部端点/真实中点），每输出2次数学FK，和driver在顶层调用完成后才做的2nativeFK比对；绝不在原递归中间插入额外FK以改变作者可变T1/T2。原branch几何身份、主动角不变、原界、闭链1e-5mm/旋转矩阵1e-5、native独立FK1e-7mm/1e-10及v3CHECKED全部留证。四个保存中心各独立重验一次；8负控只作数学检查。投影事件不去重，逐调用计账；回溯path节点只可复用本次已检查的完全相同q记录或已合格边端点，不作未计账FK。原数值不闭合保留并禁止该候选下游；R2修复数值若成功但不闭合/FK不符/主动角或branch改变即soundness停机。失败输出也保留，非有限停机。

工程构建四目标总180s wall/360s CPU，每目标45/90；科学资格120s wall/240s CPU。均从原R2 3600/7200余量扣，不与VI B974构造混账，工程另列execution台账并保守纳总帽。构建的全程墙钟alarm、编译进程组live CPU、reaped CPU及每目标CPU均限额；stage/失败编译与日志保留。运行每次只一个源进程或碰撞worker，原始stdout/stderr、实际边界进入/完成和未完成请求列表保留。

| 调用类 | 固定最坏上界 | 计数口径 |
|---|---:|---|
| 顶层project / RBS / reconstruct，四目标合计 | 320 / 64 / 64 | 每目标80 / 16 / 16；RBS/回溯只在原样预置条件满足时调用 |
| trace固定分支project | 4256 | 两trace目标×80直接投影 + 两trace目标×(16RBS+16回溯)×64内部投影；plain内部未观测 |
| 成功投影事件独立检查 | 4256 | 不去重，包括原数值不闭合的成功返回 |
| 独立数学arm FK | 8536 | 4256×2 +4中心×2 +8负控×2 |
| v3逻辑碰撞 / 内部arm FK/J | 4260 / 17040 | 4256投影+4中心，每逻辑调用native/aligned各2次FK/J；requested/started/completed分列 |
| v3实际PQP pair queries | 988320 | 4260×2variants×最多116pair；逐query_code计实数 |
| trace native FK | 57344 | 2trace目标×112顶层请求×每请求256；包含原FK及调用后观察FK，保守帽 |
| trace内部PQP pair queries | 524288 | 64个trace RBS/回溯请求×8192；直接投影不调用碰撞 |

trace每请求固定branch64、rbs/reconstruct各128、nativeFK256、nativeIK64、collision64、PQP8192任一帽到达均UNKNOWN并保留前缀。plain无内部观测，不能写成相同内部计数实测值；其相同请求逻辑返回逐字段比对trace，进程本身仍受总墙钟/CPU预算约束。上述上界不是预报消耗，也不能当完成数。

最初草稿绑定12run的旧预算快照已归档；当前13run自有wall109.56337707999865/CPU55.934698，B累计974构造且余0，不再追加VI候选。freeze前重新读取所有execution自有wall/CPU字段并绑定SHA，按最新原预算余量取min，不复用旧快照另开额度。工程成功后再生成并冻结科学协议；未构建草稿明确MUST_BUILD_BEFORE_FREEZE，不能执行。不同时启动两个资格；现有claim/output存在立即拒绝。任何失败/source不一致/未完整统计都保留prefix和未执行列表。

## 验收与后续

source-equivalence必须plain/trace一致；R2成功输出如违反独立闭合/FK则阻断，不能仅外部拒绝后继续宣称数学soundness。碰撞或限位是普通候选失败，不代表理论错。完整正控需II/III、start/goal、两个角色各至少一条非阈值提前返回的真实RBS及回溯边通过所有独立门；不足则PARTIAL/FAIL/UNKNOWN原样报告，不能换fixture。原数值返回是保存对照，无须原数值也通过才记录R2有限修复性质。

这仅普通PCS固定局部接口，不是随机PCS分划策略、RRT/Bi-RRT/SBL规划、奇异跨支、500次统计或PCS优势。下一步按相同薄API接IV/V及I循环solver；VI普通PCS维护两被动支对和三主动角色；NR另先做C++/Python固定保存trace等价，再用原full-coordinateRBS。所有原文Fig3–5、TableI–II、投影500000、点对50000、固定划分/去障碍/复杂场景/所有211行和结题Word/PDF义务保留。新方法/新分布/正式大算另列可审查方案，P2/Isaac不开展。


## 根代理冻结前审查与PRE-TASK声明

任务：II/III作者PCS固定branch局部接口资格；科学目标与最小证据：四个已合格中心×两主动角色的全部八支有限枚举，以及固定±h真实RBS/回溯、plain/trace输出等价及独立门。范围与非目标见上文；0solve、0新随机、无正式统计。方法复用原SVCPCS/三搜索器、既有R2数值patch/端点/FK/碰撞oracle，新增仅薄传输与观测计账。固定单次工程180wall/360CPU、后续科学120wall/240CPU均从原R2总帽扣；实际source/input/build/claim/hash/返回前缀逐项保留。停止条件为任一帽/依赖变更/观测不等价/R2数值soundness错误，普通限位/碰撞失败保留，不换fixture/branch/h。相同机制三次修复仍失败则D079根因审查；本阶段不放宽任何门。

先前工程资产复用：docs/POST_TASK01_REUSE_MAP.md及已保全631b1f工程复用清单保持，generic原日志/claim预算为THIN_ADAPTER；作者SVC/搜索器直接引用外部固定快照为DIRECT_PORT；独立FK/J及源碰撞为TEST_ORACLE；FR3/MoveIt/Isaac只作REFERENCE_ONLY，不能替代ABB论文机构。新增文件为本报告表中五份项目自有代码与两份配置，不导入未许可作者源码/mesh。主要风险为原数值/源碰撞对齐/原采样控制流以及plain内部未观测，已分别保留；需要额外用户确认：否，此为已授权R2有限资格内的原接口集成，不产生新科学假设、正式预算或VI构造。

工程溯源审查要求：manifest/claim/execution记录本仓库source_commit、固定四目标、编译exit与binary SHA；科学runner核验其own-source在该commit及当前均同SHA，并绑定工程execution/claim。每目标45wall/90CPU覆盖copy/instrument/hash/compile全段；group live CPU含已回收后代累计CPU，工程预算初始化失败也保留记账。构建工程通过只证明可链接，科学通过仅证明这些固定局部接口，不代表随机PCS策略或三规划器全局能力。
