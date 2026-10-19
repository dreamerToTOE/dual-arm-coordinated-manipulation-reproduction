# ABB SBL_PCS 首次 setup / 公有13点观察 PRE（草案，未执行）

2026-10-17。本项仅准备未来独立资格，源码为新增 runner/supervisor；不修改待构建的八份工程稿。没有项目 import/describe/transform/compile/binary/setup/solve，没有创建协议、claim或stage。当前须先完成唯一工程build及真实人员独立POST，随后root按真实最新总账冻结本项，不能用缺省/placeholder工程证书通行。

固定范围：II/native1、既有A01 `RECONSTRUCTED` 起终点原文件SHA、seed7；driver只接受setup；原SBL构造Range=.8，setup仍自动配置maxDistance，不能提前setRange。只启动一个新source进程、只写一个完整JSON请求，然后立即关闭stdin；driver先读到EOF才构造模型。唯一原setup不solve，不重测端点或已有FK/IK/局部/路径资格。

预算建议10秒墙钟/20秒CPU，纳入R2累计3600/7200；不借VI余额，VI仍974/974。既有含两worker和12局部dispatch的D_LOCAL02外收费2.47wall/2.13CPU仅作量级参照，本项不是复测或承诺运行成本；10/20覆盖启动、预检查、20mesh复制/原构造加载、固定13观察、完整原始留证和退出，外GNUtime真实upper方能判合格。预检查超帽或超时则保留STOP，不换预算重试。builder/runner前检查始终计入外层child费用，但继承的异步timer在validate后启用，不能声称此前已有硬watchdog。

观察实际原setup对象的精确linear/random-linear动态类型、projection维数/cell sizes/bounds/userConfigured、两grid实际公有维数及空树、setup自动getRange、原Range=.8、sampler尚未分配。只在既存对象上按0,e0…e11固定13次调用公有project，不另造evaluator/RNG/sampler，不读取protected矩阵；输出每点输入/输出binary64及公有线性作用列。维数不得事后调参，冻结判据为正且不超过12、两grid均相等、cell大小有限正数、bounds存在时有限有序、13输入及binary64逐项完整、原点作用为0。

实际库静态证据为 `P4_FULL_R2_ABB_SBL_PCS_ACTUAL_LIB_LINEAR_PROJECT_STATIC_EVIDENCE_20261017.md`（SHA 788dad1f7eda728078699f271b949204e3689d8714c4765a40355f9f87a9d535）：所绑libompl正常路径为固定矩阵乘加，无OMPL/C RNG，但有分配/释放和PLT边界。runner源码仅用stdlib读ELF dynsym；未来source在等待请求时保存实际/proc/exe/maps/environ、所有映射文件SHA，要求审过的libompl是两个project符号的唯一已加载全局/弱可见定义提供者。source只继承明确环境，LD_BIND_NOW=1、无LD_PRELOAD/LD_AUDIT/LD_LIBRARY_PATH，系统ld.so.preload须不存在或空，cache预冻。此为“静态+请求前loaded symbol scope”，不冒称读取了运行时GOT地址、protected矩阵存储或已证明所有库内部调用次数。

source新原body trace预期只有mesh_load一次、空grid清理两次，entered/completed各配对；其余FK/IK/collision/RBS/identify/motion注册都应0。setup内部库RNG次数仍UNOBSERVED，不能以观察器无额外RNG代替全部实际调用计数。constructor原模型加载可以发生，碰撞query和独立模型资格调用仍0。

进程合同复用既有单请求/双pipeEOF/真实poll和reap模式的工程代码，以源码复制方式放入新文件，未import执行旧模块。新runner先要求真实build执行/manifest与人员独立POST全通过，五TU实际依赖和前后SHA、外费/receipt全部吻合，才可描述协议；不使用placeholder。未来实际启动需source/protocol已提交一致、root/独立审/最新账三true，独占新claim/run/path。完整保留request实际单write字节/返回值、stdin关闭、原stdout/stderr、每chunk和完整raw SHA/base64、实际两pipeEOF、PID/starttick、close前poll与回收后空group，所有false/未知/tail/partial均STOP。setup不得产生原planning文件。

只有真实外层10/20上界、source1请求1、13观察、完整raw与双EOF、全组回收和最终hash均通过，才标 `SOURCE_SETUP_PUBLIC13_OBSERVED_PENDING_INDEPENDENT_POST`；仍须另做人员独立保存证据POST。此状态不认证算法、路径、连续无碰撞、RSS能力或性能，正式Table I调用仍0/22500，完整211义务保留。后续SBL solve仍受历史connect未初始化a_chain原save读取风险的独立门约束；本项不修此源风险、不自动开启solve或P2/Isaac。
