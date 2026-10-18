# V RRT+PCS：真实调用图与下一项最薄资格路线

2026-10-18。**DRAFT，仅保存数据与源码静态诊断；未生成节点、导入模型、编译、运行RNG/IK/FK/PQP/RBS/solve或新增费用。** 不修改当前PHYSICAL01 PRE及其稳定文件。任务为定位V完整路径入口，最低证据为具体重载调用链及原失败保留方式；优先复用既有II单次入口/原V搜索体与当前生命周期监管。当前阻塞不是随机helper修复，科学执行仍须root先冻结具体协议、当前账本、预算及独审。

## 真实可达图

来源为固定 `ckcComau/industrialScene@ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca`；下列行号均为原作者只读副本，不以插桩后的行号代替：

`run/plan_PCS.cpp:55–58,142–162` → `og::RRT(si,maxStep,env)` → `setup()` → `solve(ptc)`。原main validity callback恒true（同文件41–44、117），并不代做闭链或碰撞资格。

| 实际阶段 | 原调用及控制流 | helper可达性 |
|---|---|---|
| 初始节点/目标身份 | `RRT_PCS.cpp:115–125,147–149` → `identify_state_ik` → 原全分支IK搜索/近邻身份识别 | 不调用三参或五参 `IKproject` |
| 环境采样 | RRT`:155–165`，原goalBias `.05`，否则OMPL ambient `sampleUniform`；`rand()%2`选主动角色 | 不调用SVC `sample_q`；ambient采样不等于三参随机分支project |
| grow固定分支投影 | RRT`:181–219`直接调用 `calc_specific_IK_solution_R1/R2`，以近邻对应被动branch作投影；失败可按作者原次序切换角色；两者失败continue | **不经任何 `IKproject` 重载**；此处原collision拒绝与身份识别保留 |
| goal直连候选 | 仅 `gg && reach` 跳过上述投影、使用已存 `ik_goal`（`:225–226`）；仍必须通过下行原RBS门 | 不因原goal callback恒true而免除RBS |
| 接纳边 | RRT`:228–249`仅在同branch且非−1时调用 `checkMotionRBS`；role0失败后才试原role1；只有true才写parent并入树 | 向量递归SVC`:488–512` → `isValidRBS` `:457–467` → **四参** `IKproject(q1,q2,active_chain,ik_sol)` `:140–161` |
| 中点/碰撞 | 四参project先按固定branch闭合；`isValidRBS`随后原 `collision_state`；原全12维叶距严格 `<.05`，depth150保留 | 没有把三参helper偷偷作为fallback |
| 回溯 | RRT`:281–298,373–411` → 原状态级 `reconstructRBS` → 向量递归/四参project与原collision | 三参、五参helper仍不可达 |

`StateValidityCheckerPCS.cpp:165–194` 的三参helper确实缺少成功后的`break`：正常遍历总以 `i==8` 返回false，即便中间已写出可识别解；这属于独立源码缺陷，但**不是上述RRT实际grow或LOCAL01固定分支路径的失败机制**。五参helper`:94–138`的role1索引不一致亦不在该调用图。应分项版本化诊断，不能为跑此RRT而先混入H/D/五参修复，不能将其称作已经动态资格通过。

## 已有失败怎样约束下一步

LOCAL01原execution `a0549cd8207b0a4c16e5adb71aab0f063859458a803916ba72db287e419d7985`及保存false诊断保持。每mode 8 public project为7true/1false；4 public RBS为3false/1依赖未执行；回溯同样3false/1未执行。不能以24成功投影/中点或true递归子叶将false根改判通过。

最早 `start_role0_minus`是被动arm2 branch3 native IK返回false，内部精确拒绝门仍UNKNOWN；不替换该点、不改branch、不追加局部夹具。其余三条RBS及三次回溯是在成功投影后被原8mm source安全带拒绝：start role1 conveyor–box/pair86，goal role0 chassis–box/pair73，goal role1 chassis–EE2/pair72。原最大探索深度4，不是depth150或预算耗尽。PHYSICAL01先核全部既存24节点，独立数学、branch、限位、TCP/native与aligned/pair分列；正常reject保留，不要求这些原本应拒绝的边变成功。

**前置验收应是“原接受/拒绝与独立证据相符”，不是强迫四条预定边全部通过。** 若PHYSICAL01与保存POST支持原三条碰撞拒绝，可保留它们作为负例，并以一次原完整RRT观察是否在原采样盒内找到其他路径；这不会删除局部资格义务。若独立物理判据与source拒绝冲突，先定位模型/姿态/pair来源，禁止绕碰撞、移动箱体或提高叶距来进入solve。

## 下一项最薄端到端资格草案

1. 复用II已交付的一次性entry/JSON往返精度、PlannerData、成功与失败reconstruction保存，以及V已审构建/claim/进程组/watchdog/费用包络；II旧单次资格不重跑。保留原V `RRT_PCS.cpp/.h` 全字节。`abb_rrt_pcs_e2e_driver.cpp`/observation为THIN_ADAPTER资产，不能只改环境标签而保留ABB采样盒、range2.6或ABB数学核。当前V local driver根本没有planner实例/solve入口，其链接成功不是端到端资格。
2. 新entry仅V A02原恢复起终点，分类 `CORRECTED_COMAU_APC_ALIGNED_V3_RECONSTRUCTED_A02_ORIGINAL_RRT_CONTROL`；原端点另列。环境为V、作者工业场景 `env=1`，原 `run/plan_PCS.cpp:80–107` 12维采样盒（含每臂q4/q6±3.1416）、goalBias `.05`、callback恒true、resolution `.02`；原单次mode1 range `.2`（`:276`）。显式固定一次seed，并同步OMPL与C RNG；不搜索多个seed或失败后改range。预算、seed、solve时限和最大保存后审节点数由root在执行前冻结，本报告不赋值或授权运行。若使用短资格时限，必须与Table I原1000s分列，不能把短时超时计入正式失败。
3. 仅一次原 `setup→solve(ptc)`，不路径简化、不额外连接器、不预制路线、不以已验24节点喂给planner。保留全source返回、所有尝试/失败、原低精度路径及17位JSON/二进制身份；start/destination/branch/role与parent关联可追溯。可直接复用LOCAL01已经证明的plain/trace局部语义，若下一协议要声称完整solve两mode一致，必须在执行前明列两次实际solve及相同seed成本，不能用一mode结果代称。
4. **单次source exact仍只是待后审。** 原 `PlannerStatus` 的bool可接受approximate；`plan_C::solved_bool`及stdout“Found solution”不能作通过依据。分别检查exact=true、approximate=false、solution_difference、完整原起终点逐值和里程点。原 `save2file`遇回溯false只void return（`:401–404`），其外层solve随后仍会设置solved/加入里程点路径；故必须独立检查每个解里程点边确有成功原回溯、完整连续节点顺序及失败fallback记录，不能只读 `path.txt` 存在或planner solved。
5. 只对真实保存的原路径作下一独立资格：完整union节点、全部闭链/原限位/被动branch及角色切换、显式v3 native+aligned TCP与原87pair、每条全12维叶严格<.05；后审达帽只保留前缀UNKNOWN，不重构/截短/补点造PASS。原source perf在回溯前停表，公平成本另外计实际完整入口及独立后审。离散通过仍不证明CCD、CAD吸盘接触或省略pair完整性。

相关稳定来源：RRT.cpp SHA `4ea1a052a5e9f2668fd62918c39f5a3820fc0300158f9cef0d51def3cb226b0f`；原SVC.cpp SHA `beae1a631a7112179bde95b94d518014b6d8ea5cbb7903384189e8fa34ee177e`。V已资格APC和v3 collision精确绑定沿PHYSICAL01/LOCAL01协议，不能用原SVC来源hash冒称整个V已原生通过。本报告不变更974/974的VI归档、18,000正式分母、其他环境/算法义务或原R2总预算。
