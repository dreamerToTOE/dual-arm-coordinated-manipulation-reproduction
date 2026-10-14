# P4 作者程序构建、接口和资格输入的只读核查

2026-10-14。接续作者资产审计。这次仅读取 makefile、头文件、调用入口和机器已有依赖，并提取作者原始端点；未安装依赖、未编译、未执行规划器/资格样本、未改作者快照或项目工作树。结构化清单见同目录 `P4_D079_BUILD_INTERFACE_AUDIT.json`，原依赖探测 stdout/stderr 见 `dependency_readonly_probe.json`。

## 机器现成依赖

| 库/工具 | 实测版本与路径 | 构建影响 |
|---|---|---|
| g++ | Ubuntu 11.4.0 | 保留 compiler/flags、二进制 SHA，不能把新机器耗时直接等同比较原 i7 |
| OMPL | **1.7.0**，`/opt/ros/humble/include/ompl-1.7`，`/opt/ros/humble/lib/x86_64-linux-gnu/libompl.so.1.7.0` | 现成可复用；默认 pkg-config 路径没有 ROS，所以默认查询报缺包，不能据此说库不存在 |
| Orocos KDL | **1.5.1**，`/usr/include/kdl`，`/usr/lib/x86_64-linux-gnu/liborocos-kdl.so.1.5.1` | 可用 `-I/usr/include/eigen3 -lorocos-kdl` |
| Eigen | **3.4.0**，`/usr/include/eigen3` | 已安装，取代作者机器绝对 include 路径属构建适配 |
| Armadillo | **10.8.2**，`/usr/lib/libarmadillo.so.10.8.2` | 若相应源文件需要，可直接 `-larmadillo`；库不在 x86_64 子目录不表示缺失 |
| Boost | **1.74**，filesystem/system/serialization/program_options 开发包已装 | 作者 OMPL planner 可用现有库 |
| OpenGL/GLU | GL、GLU 已有，GLU pkg-config 9.0.2 | 仅可视化构建相关 |
| GLUT | 指定 `/usr/include/GL/glut.h`与系统 `libglut.so`不存在，freeglut3-dev 未装 | 作者 header 有闲置 include；无需为非可视规划器立即安装图形栈 |
| PQP | 在已完成的 `/opt`、`/usr/local`、`/usr/include`、`/home/ubuntu2004/lmy`文件检索未找到 `PQP.h`或`libPQP` | 空间碰撞还需要取得并构建原 PQP；不能用 FCL 静默替代原查询模型 |

更大 `/home/ubuntu2004`递归扫描已中断，无结果不构成全机“不存在”结论。OMPL 的现成 .pc 文件使用生成表达式作为 Requires，建议直接指定上述 include/lib/rpath，而不是依赖它的自动解析；现成头库配置要求 C++17，作者旧命令的 C++11 需版本化为工程适配。

## 首轮最小实际 build 建议

先构建每个模型的原始 APC 和 KDL object（5 个模型组，共 10 个源文件对象），再链接一个自写固定输入资格 harness。纯运动学源文件不含 OMPL/PQP/GL 依赖，能够先产出真实编译证据和 FK/IK/NR 交叉资格，不等待空间碰撞依赖。

可执行的首个 object 命令建议如下，输出目录由主代理另建；本审计没有执行它：

```bash
g++ -std=c++17 -O2 -fPIC \
  -I/usr/include/eigen3 \
  -c /home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning/proj_classes/apc_class.cpp \
  -o /home/ubuntu2004/lmy/.p4_d079_native_build/abb_apc.o
```

同一构建函数依次替换模型目录及 `apc_class.cpp`/`kdl_class.cpp`，KDL 的 harness 链接加 `-lorocos-kdl`。保留原文件 SHA，失败 stdout/stderr 和 exit code；编译不通过仍是本轮真实工程证据。不要先运行作者附带的陈旧 ELF。

由于各模型复用 `two_robots`、`kdl`等类符号，建议每模型/方法建立独立目标并以独立进程执行，避免把五套同名 C++ 类链接成单一 executable 触发 ODR 冲突。统一的是获取、构建、配置、日志和资格接口，不是混合类实现。

## 纯运动学接口

| 模型组 | 原始源文件 | 构造与固定参数 | 资格调用 |
|---|---|---|---|
| I，`planar_ckc` | `proj_classes/apc_class.cpp`、`kdl_class.cpp` | `ckc(20,0.3)`、`kdl(20,0.3)` | APC `project(q,nc,IK_sol)`，nc=0…19，两 IK；FK 左右链/闭合；NR `GD(q)`及`get_GD_result()`；源中基座(7,4)、19根长度1杆 |
| II，`CKCplanning` | 同上 | `two_robots({-450,0,0},{450,0,3.1416},300)`、`kdl(900,300)` | `FKsolve_rob(q,arm)`、`IKsolve_rob(T,arm,branch)`、8分支 getter、`calc_specific_IK_solution_R1(Q,q1,branch)`/R2、整链 `GD(q)` |
| III，`CKCplanning` | 同上 | 第二臂基座距1200 mm，杆长500 mm；构造基座 ±600，第二臂3.1416 | 同 II，不混用 II 杆长度或障碍索引 |
| IV，`ckcComau2` | 同上，`def.h`为冻结模型输入 | `two_robots()`、`kdl()` | 双臂 FK、8分支 IK，`calc_specific_IK_solution_R1(q1,branch)`/R2，`getQ()`，KDL整链NR |
| V，`ckcComau_industrialScene` | 同上，必须是正确工业分支 | `two_robots()`、`kdl()` | 同 IV；Q为转动加平移箱体抓取变换，不得当纯杆 |
| VI，`ckcComau3` | 同上，`def.h`、Q12/Q13 | `two_robots()`、`kdl()` | 三臂 FK和 `calc_specific_IK_solution_R{1,2,3}(q_active,branch_a,branch_b)`；两个闭合 residual；默认NR `GD(q18)`是GD12+IK3顺序实现 |

固定输入首先使用作者静态 `c_start`/`c_goal`原数组，记录舍入导致的真实残差，不能自动按更宽阈值视为闭合或无说明投影/覆盖端点。JSON 保存了46处作者源码字面端点及源文件行号（包含重复 benchmark 模式，不能把46处当46个独立实验）。再用已冻结资格 protocol 的固定微扰/随机数组测 FK–IK、全链闭合、Jacobian、分支身份及奇异秩；资格样本数和判据由主代理统一冻结，本审计没有新增科学条件。

独立 harness 可以设置公开 `IK_counter=0`、`IK_time=0`作为计时初始化，避免未初始化计数影响日志；这应标成工程初始化，不能作为投影结果修正。单独 APC/NR 的 `include_joint_limits`必须按该项原实验条件设定：500000 纯投影比较原文关闭限位/碰撞，规划任务保持限位和碰撞，不能混用。

## 空间碰撞 target 与资产

四个空间模型的最小原数学碰撞单元都是 `validity_checkers/collisionDetection.cpp`，使用 PQP 的模型/距离容差查询。此 cpp 没有 OpenGL 或 `Model::Draw/Model`调用；作者 makefile 加入的 `validity_checkers/model.cpp`纯粹包含 GLUT 绘图代码。非可视目标可以在隔离 staging copy 做以下构建 patch：

1. 去掉 `collisionDetection.h`闲置 `<GL/glut.h>`include，并不编译`model.cpp`；不变换碰撞模型与容差。
2. 把某些 header 的 `/home/avishai/.../simulator/MatVec.h`绝对路径指向同快照`simulator/MatVec.h`；它还需要 PQP 的 `PQP_Compile.h`。
3. 去掉`-lompl_app/-lompl_app_base`及GL/GLUT等不被非可视单元引用的链接项，保留原PQP、OMPL/KDL使用部分。

这里是静态依赖判断，实际编译链接仍需要保存证据；不应一开始批量编辑数学或算法。

| 模型 | 碰撞构造/调用 | 资产与约定 |
|---|---|---|
| II/III | `collisionDetection(D,0,0,0,env)`；`collision_state(P,q1,q2)` | env=1/2；从`./simulator/`读 ABB Base/Link/EE/table/obs/cone；P由SVC以20 mm间隔构成原杆中心线；容差8 mm |
| IV | 无参构造；`collision_state(q12)`或(q1,q2) | 从`./simulator/`读取Comau两臂、rod/obs/obs1；容差8 mm |
| V | 无参构造；同 IV | 原吸盘工具、箱体、chassis、conveyor及基座；容差8 mm，原碰撞排除对不可静默补/删 |
| VI | 无参构造；`collision_state(q18)`或(q1,q2,q3) | 三臂网格、wheel和三组障碍网格；容差8 mm |

所有 cpp 实际加载的 mesh 文件已按代码逐行核查，在对应作者快照中均存在，文件清单与SHA见JSON。运行必须用正确模型 staging 根作为 cwd，或隔离cwd中提供该模型 `simulator`资源；不要让同目录路径/日志覆盖其他 trial。平面碰撞在 validity checker 的几何函数内，不能用旧 Python 简化场景替换作者障碍。

## 完整 planner 的确定编译单元

每种方法先链接该模型独立 executable；自写 harness 取代作者不受本次预算约束的旧 main，调用原 public planner/validity checker 接口，保存所有日志和边。原 run 文件可按单个 translation unit 改名 legacy main 保留`plan_C`，或只用新 harness 分配原planner；具体改法需源码提交和证据。

| 模型/方法 | 方法源 | 搜索器源（RRT/Bi-RRT/SBL） | 其他单元 |
|---|---|---|---|
| I PCS | `run/plan_PCS.cpp`，`StateValidityCheckerPCS.cpp`，`apc_class.cpp` | `RRT_pcs.cpp`、`CBiRRT_pcs.cpp`、`SBL_pcs.cpp` | `verification_class.cpp`；没有RSS原入口，HB不能改名RSS |
| I NR | `run/plan_GD.cpp`，`StateValidityCheckerGD.cpp`，`kdl_class.cpp` | `RRT_gd.cpp`、`CBiRRT_gd.cpp`、`SBL_gd.cpp` | 同上 |
| II/III PCS | `run/plan_PCS.cpp`，`StateValidityCheckerPCS.cpp`，`apc_class.cpp` | `RRT_PCS.cpp`、`CBiRRT_PCS.cpp`、`SBL_PCS.cpp` | 原 run/h 还引用PRM_PCS，若保持入口须链接它；collisionDetection.cpp |
| II/III NR | `run/plan_NR.cpp`，`StateValidityCheckerNR.cpp`，`kdl_class.cpp` | `RRT_NR.cpp`、`CBiRRT_NR.cpp`、`SBL_NR.cpp` | 同理PRM_NR；collisionDetection.cpp |
| II/III RSS | `run/plan_RSS.cpp`，`StateValidityCheckerRSS.cpp`，`apc_class.cpp` | `RRT_RSS.cpp`、`CBiRRT_RSS.cpp`、`SBL_RSS.cpp` | collisionDetection.cpp |
| IV/V PCS | `run/plan_PCS.cpp`，`StateValidityCheckerPCS.cpp`，`apc_class.cpp` | `RRT_PCS.cpp`、`CBiRRT_PCS.cpp`、`SBL_PCS.cpp` | collisionDetection.cpp |
| IV/V NR | `run/plan_GD.cpp`，`StateValidityCheckerGD.cpp`，`kdl_class.cpp` | `RRT_GD.cpp`、`CBiRRT_GD.cpp`、`SBL_GD.cpp` | collisionDetection.cpp |
| IV/V RSS | `run/plan_SG.cpp`，`StateValidityCheckerRSS.cpp`，`apc_class.cpp` | `RRT_SG.cpp`、`CBiRRT_SG.cpp`、`SBL_SG.cpp` | collisionDetection.cpp；SG就是作者RSS入口 |
| VI PCS/NR | 同 IV/V相应命名 | 相应PCS/GD三搜索器 | collisionDetection.cpp；全18D、多闭环分支标签 |
| VI RSS | SG/RSS命名单元 | 默认makefile只列CBiRRT_SG，其它SG源存在 | 公开RSS版本有签名/递归移植缺陷，须编译证据先定位，不能直接判方法无效 |

作者 makefile 多数注释掉某些算法 target；不要把默认`make`只有一种输出当作其它源码缺失。作者 run 的默认模式可能内部循环87/500次或直到找到成功，种子还用time；不能作为单次公平预算runner直接启动。应提前冻结单次调用、全部方法相同/原论文两套预算、固定seed和超时拒绝行为，再运行科学cases。

当前状态：**依赖/构建入口审计完成；编译、FK/IK/collision资格、全部planner科学试验均尚未执行。**
