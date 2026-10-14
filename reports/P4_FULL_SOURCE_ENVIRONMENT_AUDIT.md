# P4 D079 作者代码与原实验资产来源审计

2026-10-14。这里只做联网来源核查、只读克隆、固定版本文件审查和作者场景图片核对，没有运行规划器、投影实验或科学资格样本。历史 P4/P2 工作树未修改。本审计补充新阶段来源，不覆盖 2026-10-13 已接受审计。

## 论文与获取范围

原论文为 Sintov、Borum、Bretl，*Motion Planning of Fully-actuated Closed Kinematic Chains with Revolute Joints: A Comparative Analysis*，IEEE RA-L 3(4):2886–2893，2018，[DOI](https://doi.org/10.1109/LRA.2018.2846806)。作者[八页手稿](https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf)仍可访问。当前作者实验室[出版物页](https://robotics.sites.tau.ac.il/publications)链接到此论文及 IEEE 页面。IEEE 文献页在本次浏览工具下无法读取，作者出版物页此条未提供视频链接；这只表示已检查入口没有获取到额外视频，不表示补充视频不存在。

按照论文代码链接，我先核查 [CKCplanning](https://github.com/avishais/CKCplanning)，再通过 GitHub 官方 API `https://api.github.com/users/avishais/repos?per_page=100` 枚举作者全部公开仓库。由此补齐之前只查 CKCplanning 时遗漏的 `planar_ckc`、`ABB_dualarm_planning`、`ckcComau`、`ckcComau2`、`ckcComau3`。

原始 API 响应保存为 `author_repositories.json`。`author_source_manifest.json`记录七个仓库/分支快照的完整 commit、Git tree、逐文件字节数和 SHA256。作者源码和网格只保存在本地外部审计目录，没有复制进公开项目仓库。

## 固定版本与环境映射

| 原论文义务 | 作者仓库/分支与完整 commit | 实际取得资产 | 来源结论 |
|---|---|---|---|
| I：20R 平面闭链，Fig.2a、Fig.3 | [planar_ckc/master](https://github.com/avishais/planar_ckc/tree/e5edcb58e151b78baca43dd4922bfe27a48388cd)，`e5edcb58e151b78baca43dd4922bfe27a48388cd` | APC 三关节被动链、最多 20 个划分、KDL NR、RRT/Bi-RRT/SBL、障碍/端点、MATLAB 场景图、m 可见性/规划时间测试、作者数据 | 原作者资源已取得；不应再称原 20R 配置未找到 |
| II：双 ABB IRB120 搬杆，Fig.2b | [CKCplanning/master](https://github.com/avishais/CKCplanning/tree/909bd72fff778aca8682c96f9eb86ae4eb75557b)，`909bd72fff778aca8682c96f9eb86ae4eb75557b`；另有 [ABB_dualarm_planning/master](https://github.com/avishais/ABB_dualarm_planning/tree/ca095265818cc6b88402c9e6ed47df598dc6d906)，`ca095265818cc6b88402c9e6ed47df598dc6d906` | 双 6R 的八分支解析 IK、RSS/PCS/NR、三种搜索器、三个柱障碍网格和起终点；后者额外提供原测试及作者统计数据 | CKCplanning 的 `env=1` 对应论文 II，不对应论文 I |
| III：双 ABB 窄通道，Fig.2c | 同上述双 ABB 来源 | 两圆锥障碍、相对位置、900/1200 mm 基座距配置、300/500 mm 杆长分支、对应端点 | CKCplanning 的 `env=2` 对应论文 III；运行帮助中编号重复是源码文字问题 |
| IV：双 Comau 搬杆障碍，Fig.2d | [ckcComau2/master](https://github.com/avishais/ckcComau2/tree/80089340f0f1f6822e5b2821a63c998b6ae0413f)，`80089340f0f1f6822e5b2821a63c998b6ae0413f` | Comau 运动学、两臂基座配置、1800 mm 杆、机器人/障碍三角网格、固定端点、三种方法/搜索器、可见性及基准日志，`matlab/images/envIIII.png` | 作者图是双 Comau 搬杆，多柱障碍；图内字母(c)不能代替全文环境映射 |
| V：双 Comau 吸盘搬箱工业场景，Fig.2e | [ckcComau/industrialScene](https://github.com/avishais/ckcComau/tree/ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca)，`ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca` | 箱体、吸盘工具、输送/安装结构网格，非纯平移抓取变换、异高非对称基座、固定端点、RSS/PCS/NR、三搜索器和基准日志，`matlab/images/envV.png` | 必须选此分支；默认 `master` 仅为 `4f540c3ed3a0775a80f9b8f92d8c5610a1fd3ad3` 初稿，不能据默认分支把 V 判成缺失 |
| VI：三 Comau 搬环多闭环，Fig.2f | [ckcComau3/master](https://github.com/avishais/ckcComau3/tree/25488a86947cd07377cc62c43850df719a70d9ee)，`25488a86947cd07377cc62c43850df719a70d9ee` | 三个基座位置、18D 端点、环的两独立抓取变换、`wheel.tris`、两柱、每主动臂两被动臂 IK 分支、PCS/NR/RSS 草稿、RRT/Bi-RRT/SBL 和作者数据，`matlab/images/envVI.png` | 原作者环境已取得；RSS 代码存在未完成移植迹象，是否能运行需编译和资格证据 |

本地克隆均为干净工作区。`ckcComau_industrialScene/`由正确分支的 `git archive`解压，只读保存；原 clone 仍保持默认 master，未 checkout 改写。

## 可直接核查的原模型输入

平面 I 的 `proj_classes/apc_class.cpp:6`与`kdl_class.cpp:8`给出 20 个转动关节、19 个长度 1 的杆，末端零长度转动关节，基座终点 `(7,4)`。`validity_checkers/StateValidityCheckerPCS.h:119`给出四圆障碍 `(-3.2,4,1)`、`(2.6,6.8,1)`、`(4.2,-2.9,1.5)`、`(8,2,0.8)`。两个 run 文件给出同一个四障碍起终点。作者代码关节角界是 ±179.9°，论文文字是 ±180°，应保留此差异。

ABB II–III 的 `StateValidityCheckerPCS.h:23`给出两个基座间距/杆长组合，`run/plan_PCS.cpp:267`和`:272`给出固定端点；`collisionDetection.cpp`及`simulator/*.tris`给出相应碰撞模型。机构参数在 `apc_class.cpp:5`，单位为 mm，与 KDL 整链坐标约定须交叉验证。

Comau IV 的 `proj_classes/def.h`给出 X 距离 6000 mm、Y 距离 0、第二臂朝向约 −π、两基座等高、杆长 1800 mm，末端长度 22 mm。固定端点见 `run/plan_PCS.cpp:252`。V 的工业分支给出 X 距离 `2358.3−20.055` mm、Y 距离 4200 mm、基座高 1000/100 mm、第二臂朝向约 −π/2，工具长 422.7 mm，抓取变换包含 Ry(−π/2) 和 `(250,0,750)` mm 平移。固定端点见工业分支 `run/plan_PCS.cpp:262`。VI 的 `def.h`给出 RR=2600 mm、环 RD=400 mm、三臂约 120° 布局，`apc_class.cpp`给出 Q12/Q13，固定 18D 端点见 `run/plan_PCS.cpp:264`。

已渲染检查四个作者环境图片，I、IV、V、VI 的图像分别呈现平面四障碍、Comau 搬杆多柱、吸盘搬箱工业装配、三臂搬环双柱，与论文文字场景相符。图片只用于资产身份核对，不作本次实验结果。

当前 [Comau 官方 NJ-16-3.1 产品页](https://www.comau.com/en/our-offer/products-and-solutions/robot-team/nj-16-3-1/)有 CAD 下载入口和厂家关节范围；此页写 q6 ±2700°，作者代码使用 ±400°；q3 也需要核对参考零位后才能比较。忠实复现应先保留作者实验输入，不能静默按现代页面改参数。旧 ABB 官方产品 URL 本次返回 404；ROS-Industrial 当前 ABB 支持库存在 IRB120 描述，但本阶段已有原作者模型，不需要用社区 URDF 替换原运动学/碰撞模型。

## 三种算法与 RBS 的作者实现证据

- RSS：`CKCplanning/validity_checkers/StateValidityCheckerRSS.cpp:254`从三个预设奇异类型随机选一个，先随机置被动第二臂并固定相应关节，再反解第一臂，识别被动分支并拒绝碰撞。它采用无界拒绝循环，`planners/CBiRRT_RSS.cpp:351`用 0.2 奇异请求概率；原实现不是先对普通闭合点做 NR 再称为奇异采样。RBS 对奇异末端有距离早停实现，与普通 RBS 相同分辨率的独立审查应分开记录。
- PCS：`CKCplanning/planners/CBiRRT_PCS.cpp:145`随机选主动臂，投影失败再试另一臂；连接对面树原有闭合点时保持对方状态，要求至少一个共享被动 IK 分支；RBS 可按另一个共有分支继续尝试。不能只记录调用次数就称为路径切换优势。
- VI PCS：`ckcComau3/validity_checkers/StateValidityCheckerPCS.cpp:117`依主动臂选两被动臂的 IK 分支对，失败后换另一个主动臂。身份应记录成“主动臂 + 两个被动分支”，不能把单个分支标签沿用为多闭环局部连接资格。
- NR：双 ABB、双 Comau 和平面代码使用 KDL `ChainIkSolverPos_NR`配合 SVD 伪逆，最大 10000 次、精度 1e−5。VI 默认 `proj_classes/kdl_class.cpp:107`先对臂1–2整链 NR，再对臂3单臂 NR；`kdl_class_tree.cpp`另有树式求解版本，但默认 makefile 不使用。不能把顺序实现写成作者默认全18D同时投影。
- RBS：作者各 validity checker 实现递归中点投影与约束检查，通常声明分辨率 0.05 rad；它是局部连接技术，不是与 RSS/PCS/NR 并列的投影策略。路径重建、独立闭合/碰撞/连续性检查及缩步资格仍须在本次运行后完成。

## Fig.3–5、Table I–II 与公开数据

Fig.3 在平面源码里有 `tests/test_pcs_vary_m.cpp`、`tests/results/test_pcs_vary_m.m`、`pcs_m_analysis.txt`、`Vgd.mat`、`matlab/pcs_obs20_m.m`和规划时间数据，能够追溯 m=1、2、3、7、20 及 m=1…20 扫描。Fig.3/4 的原论文距离分箱宽为 0.3；Fig.5 为 0.46。

ABB 完整仓库的 `tests/test_apc_kdl.cpp`声明 500000 投影样本并输出成功、距离、耗时，`tests/results/apc_kdl_proj.txt`及对应 MATLAB 脚本可作为作者原始比较资料；`test_rbs_pcs_d.cpp`、`test_rbs_gd_d.cpp`保存投影前后距离及局部连接，`compare_rbs.m`/`compare_rbs_d.m`对应可见性与距离变化。不能混淆它们的条件分布：部分生成器先丢弃无法投影的目标，后统计的是被接受样本。

Table I 的空间来源仓库都提供规划基准日志，但具体日志可能混有不同步长、历史版本和失败截断；必须核查每行模式及数据列才能标成原表的精确对应。论文表 I 为每条件 500 次、最大 1000 s，硬件为 i7-6700HQ、8GB、C++/OMPL/PQP/KDL。不同机器秒数不能直接归为算法改进。

Table II 的论文 II 条件明确给出 Bi-RRT 距离 RSS/PCS/NR=0.6/1/2.6。公开 clean `CKCplanning`三个 run 文件却全用 `step={2.6,1}`；完整 ABB 仓库也保留多个 profiling/benchmark 模式。因此当前 HEAD 不是可不加审计就宣称“论文表 II 原配置”的执行入口。应原论文优先，保存参数选择来源和每方法单独 profiling/公平公共步长两条结果。

原 Fig.4 图注写环境 I、正文及表 II 指 II，此处保留原引用差异。作者记录属于 AUTHOR_REFERENCE，不能计入本次 REPRODUCED_RUN 的成功率/曲线或取代新的真实运行。

## 已发现的实现/数据审查风险

1. `planar_ckc/tests/test_pcs_vary_m.cpp:39`及`test_rbs_pcs.cpp:39`用整数除法生成主动划分/IK号，随机变量几乎总为0；未找到共同分支时 `vsuc`还可能未初始化。这是可直接检验的测试程序问题，尚未构成论文方法错误证据。
2. `CKCplanning/validity_checkers/StateValidityCheckerPCS.cpp:218`及`:252`把碰撞和超限同时发生作为拒绝条件，源码逻辑可能接受有碰撞但角度合法的样本。固定样本独立资格应验证，不得仅相信 checker 返回值。
3. `ckcComau3/validity_checkers/StateValidityCheckerRSS.cpp:360`的奇异采样仍只声明两臂变量并调用两臂遗留签名；`:661`有未定义 `dsg2`及缺少第三臂参数的递归调用，与其 18D 类声明不一致。需要真实编译证据及多闭环数学交叉验证，不能靠重复延时运行解决。
4. 原工业分支 `matlab/benchmarkResults.m`先按成功列过滤后求均值；这与包含超时的成本/成功率统计不是同一个口径。新的全部失败应保留，无成功窗口和未运行项不能伪装成数值。
5. 作者部分投影分析脚本还手工填入/替换图中的首个统计点；新的图只能读取新日志和原始作者记录的实际值，并对公开脚本处理方式另列差异。
6. 几何精度、KDL角度小值清零、毫米/弧度混合残差及返回路径存储存在需资格核查之处。当前只完成静态证据定位，不能把尚未运行的实现称为已资格通过。

## 真正仍未取得的资源与可执行边界

- 七个快照没有独立 LICENSE/COPYING 文件，GitHub API 对这几个仓库的 license 为 null；部分 OMPL 继承文件自带版权头不等于整个作者项目及 CAD 网格统一授权。本地研究可保留来源/版本，公开交付宜提交自己的适配程序、获取脚本、参数记录、差异 patch 和哈希，不自动重发布完整作者源码/网格。
- 原论文精确软件依赖版本、全部生产试验随机种子，以及每个公开 raw 文件与最终论文表格的一一生成链尚未核实。这是“待溯源”，不是机器人模型、场景或代码完全缺失。
- 已取得原 I–VI 环境运动学、场景、起终点及大部分原方法代码，优先原作者资产；独立重建不能再以“没查到 Comau/三臂资源”为前提。
- VI RSS 是公开代码可见的不完整实现候选，当前状态为 IMPLEMENTATION_SUSPECT，须在受预算约束的编译/固定样本核验中定位。若最终需要改变方法科学假设，应交给主代理按 D079 停门处理。
- 没有执行科学实验；不存在新的成功路径、规划耗时、投影效率、切换率或成功率。本审计只能支持 Gate 0 的资源可用性和后续协议设计。

外部资产目录：`/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/`。
