# P4 D080：环境 V 原资产、PCS/NR 复用边界与首项资格工程静态审查

2026-10-17。接管基线 `dc810b78f490950bf11f609a8dbf1a60b688dece`，分支 `p4-full-reproduction-pcs-study`。本项仅阅读 D080、原作者源码及保存结果、计算文件 SHA256，并新增本报告和证据索引；没有导入项目模块，没有编译、运行 describe/validate、FK/J/IK/NR/PQP/RBS/solve/RNG 或新候选构造。没有修改治理文件、旧数据、RSS/V26 暂停稿或运行账本。

**结论：环境 V 的两个重建端点已经通过后续 v3 aligned 离散 source-policy 资格，不应重做任务 A。最早缺失的是 V 自身的工具/箱体观测契约和 PCS/NR 局部入口、真实 RBS/回溯资格；环境 II 的四条路径证书不能迁移到 V。** 推荐优先准备 V 原 RRT_PCS 局部入口与原路径观测，再并行移植已冻结物理 NR 数学到 Comau C++；RSS 旧八根的碰撞定位独立推进。

## 1. D080 与已有证据的适用范围

已读 `AGENTS.md`、`CODEX_START_HERE.md` 的 D080 节，以及 D080 决策、执行任务书和交接摘要。当前保留 I 方法基准、II–V 完整双臂范围，V 为应用优先；VI 仅只读存档。原 211 项/22,500 次是历史论文事实，D080 正式目标另列 II–V 的 18,000 次、每次 1000 s。此静态审查不启动正式统计或 pilot，不扩大 R2 时间预算，不将源修正/重建写成原作者原生成功。

| 保存资产 | 实际已证明 | 不能据此推断 |
|---|---|---|
| `20261015_R2_SPATIAL01/V/summary.json` | V 430/430 组件检查；32 次 NR 为 CONVERGED；源输入 SHA `431d54db72d84cb5df3808d973608c58f9c7287767eb42323584196a08655ced` | 当时 `collision_checked=false`、planning=0；不是 V RBS/原入口或路径资格 |
| `20261015_R2_ENDPOINT_RECONSTRUCTED01/V_start.json`、`V_goal.json` | 所有原始输入、75+75 候选和旧 UNKNOWN 保留 | 这两个旧 UNKNOWN 不能盖过后续 A02 回放证据 |
| `20261015_R2_ENDPOINT_COLLISION_REPLAY01/V_start.json`、`V_goal.json` | start 候选 52 / branch 3，goal 候选 22 / branch 1；均 RECONSTRUCTED_SOURCE_POLICY_QUALIFIED | 不是原始端点直接通过，不证明 native 坐标一致、实体或连续无碰撞 |
| II 的 RRT_PCS177、RRT_NR393、CBiRRT_PCS413、CBiRRT_NR689 | 仅其冻结 II 模型/源修正/重建端点/aligned 离散策略下的完整路径 | 不覆盖 V 的 Comau、吸盘、箱、基座、障碍、GD 反向链或 V 规划器入口 |

后续 V 端点读数如下（只读保存值，没有重新计算）：

| 项目 | start | goal |
|---|---:|---:|
| 原始闭链位置 maxabs，mm | 0.005602716454632173 | 0.006258998285090911 |
| 原始闭链旋转矩阵 maxabs | 5.359871821213135e-6 | 7.30940705960732e-6 |
| 原始闭链资格 | false | false |
| 重建主动角逐值不变 | true | true |
| 重建被动角 L2 改变量，rad | 1.0588340994903246e-5 | 6.908982370946026e-6 |
| 重建被动角 Linf 改变量，rad | 8.168801626795563e-6 | 4.893931728755518e-6 |
| 重建闭链位置 maxabs，mm | 4.547473508864641e-13 | 6.821210263296962e-13 |
| 重建旋转矩阵 maxabs | 1.1102230246251565e-16 | 3.3306690738754696e-16 |
| 原关节限位 / 周期 lift | legal / 六个 0 | legal / 六个 0 |
| native / aligned 原碰撞布尔 | clear / clear | clear / clear |
| native TCP 一致性 | false，臂 2 差 0.015427453546863035 mm | false，同量差 |
| aligned TCP 一致性 | true，最大 2.2737367544323206e-13 mm | true，最大 4.547473508864641e-13 mm |

两个端点各保存 native/aligned 的 87 个 pair 查询码，均无非零 API 错误码；实际选用 aligned。API 返回码为 0 只表示查询 API 无错误，碰撞布尔来自源 `CloserThanTolerance()` 的聚合，不能混用。

## 2. V 原作者模型、抓持和碰撞来源

作者资产为 `avishais/ckcComau` 的 **industrialScene**，commit `ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca`，本机只读根为 `/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/ckcComau_industrialScene`。不能误用较旧 master 或环境 IV 的 `ckcComau2`。

`proj_classes/apc_class.cpp:4–35`、`proj_classes/def.h` 和独立 `analyze_comau_native_qualification.py:49–64` 给出相同来源契约：

- 单臂六轴顺序 Z/Y/Y/X/Y/X；长度单位 mm、关节单位 rad。几何字面量为 b=344、l1x=524.5、l1z=199、l2=1250、l3x=186.5、l3z=210、l4=1250、l5=116.5、工具 lee=400.7+22。
- 两基座位置/偏航分别为 `[-(2358.3-20.055)/2,0,1000,0]` 和 `[(2358.3-20.055)/2,4200,100,-3.1416/2]`。物理近似 π 偏航保留；不能用精确 π 重置世界坐标。
- 两 TCP 的抓持变换 Q 为 `[[0,0,-1,250],[0,1,0,0],[1,0,0,750],[0,0,0,1]]`，源闭链为 `T2=T1 Q diag(-1,-1,1,1)`。Q 的旋转是源精确符号置换，不用近似 π 的三角值代替。
- 每臂物理限位（度）为 q1±180、q2[-60,125]、q3[-90,75]、q4±2700、q5±120、q6±400，源 deg2rad 的 3.1416 保留。`run/plan_PCS.cpp:80–107`/`plan_GD.cpp` 的采样 box 另有 q4/q6±π、q2 上界 2.1871 等字面值；必须分别记录采样范围和机械限位，不能把它们悄然统一。

碰撞源码中，arm1 的 EE mesh frame `T7=T6+R6*[20,0,0]`；物理 TCP 则是 `T6+R6*[422.7,0,0]`。arm2 的 `T72` 已含 22 mm，再加 400.7 mm 才是物理 TCP。旧 v2 将 arm1 mesh frame 当 TCP，少了 2 mm，是我方观测错误；v3 已修复采集表达式，未改变原 mesh/pair/tolerance。保存修复解释见 `P4_FULL_R2_COLLISION_TCP_INSTRUMENTATION_REVIEW_20261015.md`。

箱体源位姿在 `collisionDetection.cpp:154–161`：平移由 T6/R6 与 `[400.7+435+22,0,300]` 构造，旋转由 `R7 * MRotY(-3.1416/2)` 构造。后续必须保留它与 Q/物理 TCP 的各自定义。现有 v3 结果只保存 TCP 的两份 3×4 pose，没有箱体世界矩阵或独立吸盘接触面证据；**不能从 TCP 合格进一步宣称箱体表面抓持/完整物理几何已经验证**。可在下一项 V 局部测试中用纯观测字段同时采集 Rbox/Tbox，避免单独重跑旧端点证书。

源策略为 PQP 8 mm tolerance、source env=1、withObs=true。静态统计 87 条活动查询：两臂自碰各 14、臂间 16、EE 对另一臂 8、箱对臂/基座 9、chassis 13、conveyor 13。box–arm1 base 查询被注释；未列 pair 不推断为 clear。manifest 保全 27 个 mesh；原 load_models 实际引用 21 次/19 个不同文件，其中 link6.tris 和 ee.tris 各复用两次，b1/b2 被加载但没有活动 pair。room/floor/table 等文件在 manifest 中并不表示活动碰撞查询包含它们。以上是原离散 source-policy 的边界，不应擅增/删 pair 来改变论文条件。

当前 v3 manifest SHA `c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388`，V native/aligned binary SHA 分别为 `6e91ed66c64d5952537865c26afe2ff91ebf8488ab270c92d766c4aa16a528ce` / `f3a0a1bccc479a70743f89326df1cfd9369faa155073bd98a29cfc1583a881e5`。本次读取确认源 hash、27 网格、aligned binary 以及已资格 APC stage/manifest 没有漂移。aligned 仅对 arm2 世界基座平移作既定对齐，原局部 mesh frame、物体和障碍策略未改。

## 3. PCS/NR 入口差异与最早未达门

**PCS。** V 已资格 Comau APC stage 是 `build/p4_full/20261015_R2_SPATIAL01/ckcComau_industrialScene`；APC CPP SHA `825465213d855f623948c9ee7e263053f67baed7e6907eae4f1549473f516d12`，stage manifest SHA `0253983631c567e81738bc3a911d84a46d77b816cdfb091938a7e0423b81443b`。其改动范围是几何一致的 IK 数值/符号/象限/分支恢复与截零去除；原构造函数、Q、基座和限位不变。这只资格 APC 数学，不资格 V `StateValidityCheckerPCS`。

V 原 `StateValidityCheckerPCS.cpp:174–209` 的随机分支 `IKproject(q1,q2,int)` 在成功 identify 后没有退出循环；最终 i==8 导致 false。这与 ABB 既知 helper 机制相同，但 V 尚无该入口的修正/资格。`IKproject(...,State &ik,int &active_chain,State ik_nn)` 的 role1 分支引用 `ik_nn[0]`、写 `ik_nn[1]` 也须按 identify 的 role0/role1 契约审计，不能只因名称相同就采用 ABB 补丁。`CBiRRT_PCS.cpp:122–142` 的 role1 activeDistance 把首状态写入 qb，qa 未按该角色填充；同样需要版本化单因子审查。

V RRT_PCS 的搜索内投影是直接的原解析分支调用，包含主动角色切换；它不通过上述随机分支重载实现每次扩展。故首项可从 **V 原 RRT_PCS 局部入口**进入，保留完整原搜索控制流和已知失败，不等所有 CBiRRT/SBL 问题解决后才验证 V。`StateValidityCheckerPCS.h:167–168` 的 RBS_tol=.05、max_depth=150；`checkMotionRBS` 与 `reconstructRBS` 的实际递归体均在源内。必须观察非平凡中点、返回值、分支、链切换和回溯叶，不能以 build/setup/短边 early-return 当 RBS 合格。

**NR。** V 原数值入口是 `kdl::GD`，文件/类为 `kdl_class`、`StateValidityCheckerGD`、`RRT_GD/CBiRRT_GD/SBL_GD`，不是 ABB `StateValidityCheckerNR` 的机械复制。原 `kdl_class.cpp:4–158` 有 Comau 偏置、Q、第二臂反向关节顺序和符号映射、硬编码 `T_pose`，并在返回后截小角。R1 原失败必须保留。已资格 Python `physical_nr.py` 支持 V，使用实际双 TCP 闭链 g/J 的无阻尼伪逆；现有 `physical_nr_abb_cpp_draft.hpp` 明确只接受 II/III，包含 ABB 硬编码几何，不能给 V 使用或把 II 转移证书改名。

可复用的是既有 Eigen 伪逆/日志结构、隔离进程/预算/claim 与静态逐体保留工具；数学端必须把已冻结 V 的 Python 实际几何/闭链移植成独立 Comau 版本，并先对保存 V 固定输入/矩阵做 C++ 转移资格。原 max_iterations=10000、位置/旋转门 1e-5、SVD 相对截断 1e-12、近 π 图异常与限位拒绝语义不变，不增加 damping/APC fallback 或搜索种子。

## 4. 最小首项工程计划（尚未冻结或执行）

| 顺序 | 具体可审查产物 / 复用 | 进入后项的门槛 |
|---|---|---|
| V0 字节契约 | 从上述固定 industrialScene 与已资格 APC stage 建新 V namespace；绑定原 run bounds、原 RRT_PCS、V 端点 A02、v3 mesh/pair/tolerance/source env=1。复用已保存证书，不重做 R1/R2 数学全集或任务 A | hash/依赖差异明确；原始和 corrected/reconstructed/aligned 标签分列 |
| V1 PCS 工程入口 | 建 V plain/trace 局部目标；薄适配真实原 PCS API。只观测原函数前后、递归、branch/active role、Rbox/Tbox、pair身份和源碰撞布尔。原 body/几何/PQP参数逐一保留；需要的 helper 修正独立因素版本化 | 独立静态审查通过、预算/固定输入/输出与停止条件冻结；编译不等于资格 |
| V2 有界局部资格 | 固定 A02 两中心及预声明输入；覆盖两主动角色的投影、真实非平凡 RBS、重建、plain/trace一致性；在这些新入口调用里同时补工具/箱/逐pair观测。所有返回 false/UNKNOWN、原失败和原输入均保留 | 独立检查闭链、机械界、分支、叶距、v3 aligned source-policy与物体观测；不在失败后更换输入/阈值或加深 |
| V3 NR 工程转移（可并行） | 新 Comau C++物理 NR；优先读取 V 保存的 32 个固定 NR 输入/输出与 g/J、trace；不重跑 Python 原矩阵来制造基线。接 V 原 GD API 时保留原GD body副本 | 独立转移资格、原 API 局部/RBS/回溯资格后方可 solve；II C++证书只复用不变实现部分 |
| V4 原端到端资格 | 原 V RRT_PCS 或 GD 对应入口在单个已冻结条件下作一次有界 solve，exact 源路径与完整回溯全保存，随后独立逐节点/叶资格 | 实际完整起终点路径；一次见证不计入正式500次，不证明CCD或PCS优势 |

这些是工程排程，不是本报告授予的调用额度。下一项实际协议须先列固定调用清单、估计成本、原 R2 剩额、单次/累计双时钟和一用 claim。若移植只保留已批数学则按 D080 做工程开发和有界资格；新增算法/几何/阈值、扩大时间或正式 18k 必须取得用户批准。现有 RSS/V26 草案仍暂停，旧 22500 执行 guard 不能在 D080 下直接运行。

## 5. 随后 III/IV 的最早门与复用

| 环境 | 可复用的已存证据 | 尚缺的本环境门 |
|---|---|---|
| III 双 ABB 窄通道 | 同 CKCplanning 源与已资格 ABB FK/IK；源基距1200/杆长500（II为900/300）；R2组件330/330、32 NR CONVERGED；A01 `III_0`、`III_1` 均 RECONSTRUCTED_SOURCE_POLICY_QUALIFIED；C++物理核已有II/III环境接口 | III 实际源障碍/碰撞参数、局部入口/RBS/回溯和完整窄通道路径；II路径与SBL setup不替代 |
| IV 双 Comau 多障碍 | `ckcComau2` commit `80089340f0f1f6822e5b2821a63c998b6ae0413f`，基座±3000、杆1800、tool22；APC/NR组件430项中427通过/3原FAIL；原6次NR限位拒绝保留；后续独立冻结24个局部±h输入24/24闭链/原界/source-policy通过；A02两个端点合格；fixed100/800 RSS六数学根只读复用 | 独立 IV C++几何/入口转移、RBS/完整路径；旧局部24点不证明整个邻域或原±.01组通过。RSS数学六根不等于PCS/NR或RSS全局成功 |

III 和 IV 均须记录各自 native/aligned 及未证 CCD。不得将 VI 的候选/桥/预算作为这两环境的新调用来源，D080 不再追加 VI。

V RSS 的旧100腕目标/800分支中4目标8数学根已补检为8/8 aligned collision；其中2根 TCP 高度不满足10 mm、6根满足，原 checkEE 未运行。旧证据缺逐pair碰撞身份，具体碰撞根因仍 UNKNOWN，不能推断腕模式整体无解或论文错误。可先零调用建立源 pair 映射，今后确需固定旧八根重放时另冻有限输入/预算；本线不阻塞上表 V PCS/NR。

## 6. 证据索引与当前交付界限

机器索引：`reports/P4_D080_ENV_V_ASSETS_AND_FIRST_QUALIFICATION_STATIC_EVIDENCE_20261017.json`。包含本报告依赖的保存文件 SHA、V源文件 SHA、端点缩略读数、stage/碰撞manifest当前字节核对与87 pair静态分类。索引不替代原始输入/stdout/stderr或独立后审证书。

本次新增科研运行数为0、资源账扣费为0；V局部/路径新资格数为0，正式统计仍0/18000。下一步应准备 V 的独立版本化工程产物和冻结局部协议，同时继续 II SBL，随后 III/IV；本报告没有完成 V 动态工具/箱/逐pair检查、没有批准新科学设计或正式计算。
