# III 原RRT_PCS最薄工程草案

2026-10-18。**DRAFT / 未冻结 / 未编译 / 未执行**。本项只新增driver源码与逐TU工程JSON计划，未创建stage、claim或实验目录，未导入/执行旧builder或describe，未启动模型、RNG、规划、资格或费用账。不占用V当前科学执行资源。

新`baselines/p4_full/geometry_consistent/abb_iii_rrt_pcs_e2e_driver_draft.cpp`由已合格II e2e driver逐字派生，仅8个明确替换：首行来源注释、结果schema、环境请求/输出II→III、range请求/输出2.6→.8、错误标签及`og::RRT(si,2.6,1)`→`og::RRT(si,.8,2)`。逆替换后与原II driver字节相同。原sampler、恒true callback、.02 resolution、OMPL与C RNG seed、goalBias、solve/output/完整回溯及PlannerData观察逻辑不改；原随机project helper、RBS、source搜索体、既有R2数学修正与observer没有改动。

III对应作者内部env2：基座距离1200mm、杆长500mm，构造器读取原env2的双锥障碍和原碰撞策略；原RRT range为.8。两A01输入分别SHA85550cbc…/50db8b75…，原selected index1/3与完整12角逐值记录在工程计划；sampler仍原±2.88等12维盒、q6±3.1416。此处seed7/solve10仅沿旧有限入口准备未来request，**本工程计划不授权该request执行**；后续source与独立全路径协议另冻。II证书不转成III路径资格，原III PCS7条成功/1条拒绝局部证据直接复用。

`configs/p4_d080/iii_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json`给出精确32项freshstage复制（10份所需source/header、20mesh、新driver与原observer），原II stage及原source只读。新stage拟为`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_iii_rrt_pcs_e2e_v1/geometry_consistent_observed`，当前不存在。复用字节已按旧manifest核对，不重新调用旧instrument变换。编译器固定当前g++11真实路径，保持旧`-std=c++17 -O2 -Wall -Wextra -pthread`与原PQP/OMPL/Boost链接条件；新增`-MD/-MF/-MT`仅保留真实依赖。

工程计划为**5个顺序TU＋1次link**：新driver、原corrected APC、原observed PCS checker、原collision、原observed RRT。每TU独立stdout/stderr、argv/进程identity/exit、实际`.o/.d`与SHA、输入前后SHA，成功对象立即采集；原5TU/ELF不存在可复用object，不伪称只重链driver。首次工程应保存实际MD dependency并检查冻结protected依赖，失配即保留失败、不自动重编；全部5TU成功后唯一link，结果最多`BUILT_NOT_QUERIED`，不执行binary/loaded-symbol probe/setup。

**工程组帽提议45wall/90CPU，工作帽40/80预留最终留证，仍受原R2总3600/7200及实际余额限制，不扩大总预算。** 仅作已授权普通工程的待冻结分项；旧II同5TU单命令实际17.12737691100483wall/23.727903CPU是参照，不是III逐TU实测。计划没有绑定V32或任何过时prior；root须待当前已授权原子操作结束后绑定最新实际收费账、独审、工具/运行依赖、独占claim与source commit。费用沿当前已审三观测Decimal包络，raw GNUtime单独保留，首记只入一次。若帽失败保全全部对象/依赖/原日志，不新增科学或重复attempt。

本次准备self静态8/8：精确8替换可逆、observer/driver绑定、32输入字节一致、5TU/MD计划、stage未创建、全部授权flag=false、prior显式未绑定、III几何/range/sampler固定。此为作者自审，不冒充人员独立审查。下一门是root对唯一thin diff/工程分项增量独审并冻结可执行工程监督器；本文件与JSON计划没有执行器，不可直接当科学协议运行。

文件SHA：driver `1ca2cf62944649a2a59d1e52280ec016cd878386a3fdd66b3b700ab0ada170e5`；工程计划`cb5f028e38339a36306d791dda2b41f9de04cc922e5fc70a8876046a1485258e`；self JSON `5fe383a814665ad264bde52d07a950c17d1af2722cd9b801ff147142cb4564bd`。旧II driver `eeb5e4bc…`、observer `b597b561…`及旧manifest `e1d665a5…`原样复用。
