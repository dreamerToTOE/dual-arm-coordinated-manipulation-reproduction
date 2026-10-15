# P4 R2 ABB PCS 固定局部接口：静态二次审查

2026-10-15。审查基线 `aa57c24a63edb24e6a4f7b30d4383cb1972793c3`，作者源 `CKCplanning@909bd72fff778aca8682c96f9eb86ae4eb75557b`。本次只读源码、冻结配置、已有数组及SHA；没有编译、FK/IK/碰撞/RBS/规划查询。没有改动任何已绑定源码、PRE或配置。此文不证明构建成功或运行通过；实际plain/trace等价与输出soundness必须由后续冻结资格记录支持。

## 固定路径与随机性

driver只构造`StateValidityChecker`并初始化日志，不创建RRT、CBiRRT或SBL对象。`project`明确调用四参数固定分支`IKproject(q1,q2,active_chain,branch)`；`rbs`和`reconstruct`调用八/十一参数vector重载，初始depth0、重构path={qa,qb}/iteration0/last_index1/first1与原state入口一致。

固定投影→`calc_specific_IK_solution_R1/R2`→FK→单个`IKsolve_rob`；`isValidRBS`仍用该固定投影与原碰撞，再递归中点。所有这些可达函数体没有`rand`或随机分支选择。原随机三参数投影及两个`sample_q`虽然仍被编译、保留原缺陷，但本接口没有入口到达它们。构造器/setQ/setP/模型加载和被静态核查的PQP源码也没有可执行RNG调用；PQP的“random pair”命中只是TriDist注释。`rng_calls=0`及`solve_calls=0`是该有限可达路径的静态结论/接口声明，不能冒称已经通过RNG拦截器实测，也不适用于后续规划运行。

## 分支与端点前置条件

`active_chain=0`固定arm1、解arm2，`=1`固定arm2、解arm1；driver验证角色0/1和branch0..7。原IK数组保持：肩支0..3/4..7，肘符号`(+,-,+,-,+,-,+,-)`，腕符号`(+,-,-,+,-,+,+,-)`。R2 patch保留其索引/关节界/原3.1416基座抓持，局部数学π及q2/腕数值修复不能称作者原数值。

runner用独立几何半径、`-sin(q3+alpha)`及`sin(q5)`恢复branch集合，根选择须与原保存中心的唯一几何branch相同；按固定全12距离、branch号tie选择，不用碰撞择branch。局部扰动保留中心、角色、坐标、h和符号；选定branch同时用于两个数值variant，失败不换branch/h。

原RBS源码明确假设两个端点有效，并在全12距离<0.05时直接true；它不重新检查端点。runner先重新验证保存中心的独立闭合/界/碰撞，局部投影端点另通过主动角不变、branch、native/独立FK、闭合、界、aligned离散碰撞后才进RBS。8个非法负控仅独立检查，未送RBS。因此非法端点不被用作原论文理论反例。源native成功但不闭合的输出被保留并阻断其下游；R2成功却数学不sound会终止本资格。

真实RBS仍是原算术中点、原固定branch、原native collision、原0.05全12L2和150depth；外部有限调用帽是UNKNOWN终止，不是修成源false。回溯只在对应原RBS true后调用；其path必须与端点完全相等、每内部节点已有完全相同q的独立记录、相邻距离<0.05。至少一次真实中点及回溯投影才是nonvacuous；仅阈值提前true不能使正控合格。

## trace观测边界

builder按唯一函数签名找到body；在lambda内保留传入的完整body文本，并检查插入的body逐字符相同。每个原return仅变为返回该lambda，外层记录后原样返回；原递归调用和`&&`短路保持。对collision body，PQP调用名先替换成观测wrapper，所以其“body不变”严格指该显式替换后的body；不是宣称整个作者文件字节完全相同。`read_text/write_text`还会归一换行，原snapshot仍保留。

PQP wrapper仍将原模型、姿态、容差和默认queue_size=2传给原`PQP_Tolerance`。记录与异常帽不改变未触帽的数学输入；触帽改变执行终止方式，必须留UNKNOWN。FK观察在整个源顶层调用结束后才发生，不会中途覆盖作者共享T1/T2；日志`clock()`耗时会受trace开销影响，所以plain/trace仅比较逻辑返回/配置/路径，不能用trace时间作原性能统计。运行资格仍须逐请求证明plain/trace逻辑等价，静态body审查不能替代它。

## 结论与边界

当前静态可达路径、角色/branch传递和有效端点前置条件没有发现阻断该有限局部资格的新增问题。冻结工程可保留其独立build结果，随后应重新生成包含工程execution的新科学协议，再审查并单次执行。既有源native失败、所有原失败输入和VI Q2 UNKNOWN不变。这里只覆盖II/III固定局部接口；随机PCS分划、三个searcher solve、跨支、正式统计及其他环境仍未通过本项获得资格。

审查SHA：builder `918af0d33cb4bd0223c457f850367a4a54fde34285731ea15a3c1a1612684c43`；runner `776700587300eb2a16c7a6cb5ecdba13ea3bce35e717485bdbe38b2de7017dc4`；driver `fe6f849fa862efc4bfa528adede742b4fdab24f187233528ea191650ae8d485e`；trace `63366eeebe7822947c50f5b151aab4c03321d7be3339ae3f6bdc85aea204d366`；冻结工程配置 `98eb2f1b5659a8397ded0f8556253108f9ec9869d9bce4176ea9782b21782fc4`。

## 构建完成后的只读复核

根代理通知build01完成后，本审查以`build_assets()`读取并验证232个绑定资产，未启动任何binary查询。构建source_commit为上述`aa57c24`；本仓库own文件与该commit blob/当前文件SHA一致，冻结recipe、atomic claim、外部manifest、工程execution互链通过。四个固定target均exit0，合计wall94.59233520399721s/CPU130.109068s，已作为独立工程execution计入R2；13项科学执行加本工程为14个execution、wall204.15571228399586s/CPU186.043766s。所有target整目标wall<45、CPU<90，合计<180/360。

| target | binary SHA256 | wall / CPU s |
|---|---|---:|
| author_native/plain | `413567c24f7e59657fb88a5ff61698410ad7e0a0411877ecafc420b411f5941f` | 23.702375222001137 / 31.334107000000003 |
| author_native/trace | `143dac36249e7a1f733a163d1b8b9332272f7e3e75b5d4777fe3ea9ab80a85bf` | 24.452486374000728 / 34.094942 |
| geometry_consistent/plain | `a461f6908ba1df041a951836804fb5114e0921eb3d8b80641364c442662330aa` | 21.934770444000605 / 30.527862 |
| geometry_consistent/trace | `05a418b18d4c53d774aa56e81034b119f87435432a41f563a354d9f92a5dd7e2` | 24.43372191999879 / 34.08318400000002 |

另做纯文本反包装核查：两variant各6个实际trace函数body，共12个，都包含对应plain body文本恰好一次（碰撞先识别所声明PQP调用名替换）；在内存移除这12个包装后，各variant的APC/SVCPCS/collision三文件全文与plain解码文本完全相等。两variant三种planner源的plain/trace文件原字节完全相等。因此未发现未声明算法body变化。没有写回外部源、重新构建或运行查询。

外部manifest SHA `b05d53d3ff65e9122179f785836eff6162eca1c4221ecd0513fd901854e657aa`；claim SHA `e298f7c63fdfbce6befcada10bba61de7e36cc609ba14914b4e2af5068f2a5ee`。在绑定当前14项execution、该成功构建链和固定输入的前提下，可冻结120wall/240CPU科学资格；此结论只解除工程与静态前置阻断，未提前给任何IK/RBS/回溯/规划PASS。
