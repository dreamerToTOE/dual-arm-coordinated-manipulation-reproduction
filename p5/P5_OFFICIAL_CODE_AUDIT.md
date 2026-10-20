# P5 官方代码审计（Official Code Audit）

> 范围：论文 *A Unified Framework for Coordinated Multi-Arm Motion Planning*（IJRR 2018）官方项目页所列仓库
> 方法：**只读**。GitHub REST API 读取元数据与文件树，`codeload` 下载固定分支快照到仓库外的工作目录；未安装、未编译、未运行任何官方代码。
> 证据：`p5/evidence/P5_official_code_manifest.json`（含每个仓库的 commit、许可证、关键文件 SHA256、tar 包指纹）

---

## 0. 方法与边界

### 0.1 做了什么

1. 读取论文 Table 2（p.1214）与作者项目页 <https://nbfigueroa.github.io/multi-arm-coordination/> 的仓库清单，交叉核对。
2. 对每个仓库取 `default_branch` 的 **HEAD commit SHA**，用该 SHA 下载 tar 快照（`codeload.github.com/<repo>/tar.gz/refs/heads/master`），记录 tar 包 SHA256。
3. 静态阅读：`CMakeLists.txt`、`package.xml`、`README`、`LICENSE`、核心 `.cpp/.h/.m`，统计文件数/体积/语言。
4. 对随仓库发布的**模型文件**做字段级检查（用 `scipy.io.loadmat` 只读解析，不解算任何算法）。

### 0.2 没做什么（以及为什么）

- **未编译**：策略上本阶段禁止"major installation"；且多个仓库需要 ROS1 catkin 工作空间与 EPFL 内部的 `mathlib/skinematics/sgaussians`，安装成本远超审计需要。
- **未运行**：同上。
- **未把官方源码复制进本仓库**：许可证不统一（见 §7），只记录 URL + commit + 指纹。任何后续使用都通过"按 SHA 下载 + 校验"的方式复现。

因此下文所有"能否编译/运行"的判断都明确标注为**静态判定**，不是实测。

### 0.3 一个必须知道的环境事实

`sina mr66` 这个 GitHub 账号已改名为 **`SinaMirrazavi`**。论文与项目页里的 `github.com/sinamr66/...` 全部 301 跳到 `github.com/SinaMirrazavi/...`。**写进脚本/文档时必须用规范 URL，否则某些工具链（不跟随 301 的 git 客户端、静态检查器）会失败。**

---

## 1. 三份清单的对照

| 论文 Table 2（8 项） | 项目页（7 项） | 任务书给定（6 项） | 规范 URL（HEAD） | 性质 |
|---|---|---|---|---|
| Multiarm_ds | ✅ | ✅ | `github.com/SinaMirrazavi/Multiarm_ds` | 论文算法（§3 任务空间） |
| QP_IK_solver | ✅ | ✅ | `github.com/SinaMirrazavi/QP_IK_solver` | 论文算法（§4 QP） |
| SCA_data_construction | ✅ | ✅ | `github.com/SinaMirrazavi/SCA_data_construction` | 论文算法（§5 数据） |
| SCA-Boundary-Learning | ✅ | ✅ | `github.com/nbfigueroa/SCA-Boundary-Learning` | 论文算法（§5 学习） |
| SVMGrad | ✅ | ✅ | `github.com/nbfigueroa/SVMGrad` | 论文算法（§5 评估） |
| **SESOSDS_lib**（Table 2 拼写） | **SESODS_lib** | ❌ | `github.com/SinaMirrazavi/SESODS_lib` | 上游工具（二阶 DS 学习） |
| LPV | ✅ | ✅ | `github.com/SinaMirrazavi/LPV` | 论文算法（§3 LPV/GMM 执行） |
| ML_toolbox | ❌ | ❌ | `github.com/epfl-lasa/ML_toolbox` | 外部依赖（交叉验证/libSVM） |
| kuka-rviz-simulation | ❌ | ❌ | `github.com/epfl-lasa/kuka-rviz-simulation` | 仿真环境（非算法） |

**三处必须记录的差异**：

1. **Table 2 的 `SESOSDS_lib` 是拼写错误**：该 URL 404。实际仓库是 `SESODS_lib`（少一个 S），项目页拼写正确。这是论文排版错误，不是仓库消失。
2. **LPV 不在 Table 2 里**，只在项目页出现。但它是 `Multiarm_ds` 的编译依赖（`include/LPV.h` 同名实现），属于论文 §3 的实际执行代码。因此任务书把 LPV 列入是正确的，**Table 2 不完整**。
3. **ML_toolbox 与 kuka-rviz 不属于论文算法**：前者是 libSVM 的 MATLAB 封装 + 交叉验证，后者是 KUKA + RViz 仿真环境。它们只影响"能否复现实验"，不影响"能否复现算法"。

### 1.1 依赖闭包（静态读取 `package.xml`）

```
Multiarm_ds            -> catkin, roscpp, std_msgs, motion_prediction(=epfl-lasa/Object-Trajectory-Prediction)
                          + Eigen + mathlib(robot-toolkit)
QP_IK_solver           -> catkin, roscpp, rospy, std_msgs, eigen, svm_grad, sg_differentiation
                          + NLopt + CVXGEN(缺失) + OpenMP + Boost
SCA_data_construction  -> catkin, roscpp, rospy, std_msgs, mathlib, skinematics, sgaussians, kuka_fri_bridge
                          + mlpack + Eigen + OpenMP
SCA-Boundary-Learning  -> MATLAB + 打包的 svm_perf/svm_struct 二进制 + ML_toolbox + SVMGrad
SVMGrad                -> MATLAB（svm-lite mex） / catkin + eigen（C++ 包）
LPV                    -> Eigen（无 ROS）
SESODS_lib             -> MATLAB（LMI/优化求解器）
```

外部依赖是否仍在？

| 依赖 | 状态（2026-10-20 查询） |
|---|---|
| `epfl-lasa/Object-Trajectory-Prediction` | 存在，但只有 5 个文件（`TrajectoryEstimation.{h,cpp}` 共约 19 KB） |
| `epfl-lasa/robot-toolkit`（mathlib/skinematics/sgaussians 所在） | 存在（2.58 MB） |
| `epfl-lasa/sg_differentiation` | 存在 |
| `nbfigueroa/kuka_interface_packages` | 存在 |
| `epfl-lasa/kuka-rviz-simulation` | 存在 |

即：**依赖闭包在 2026 年仍然完整可得**，但全部是 ROS1（catkin）时代代码，与 ROS2 不兼容。

---

## 2. 逐仓库档案

### 2.1 `SinaMirrazavi/Multiarm_ds`

| 项 | 值 |
|---|---|
| 论文 URL | `https://github.com/sinamr66/Multiarm_ds`（301） |
| 规范 URL | `https://github.com/SinaMirrazavi/Multiarm_ds` |
| HEAD | `c6ccbf48639b0c9abad67b91eb7a233ff9c775d1`（2019-04-16） |
| 许可证 | LICENSE 文件 = **LGPL-3.0**；源码头注释 = **GPL v2 or later**（矛盾，见 §7） |
| 规模 | 24 KB，10 个文件，C++ |
| 核心 | `src/multiarm_ds.cpp` 968 行、`include/multiarm_ds.h` 221 行、`src/LPV.cpp` 586 行 |
| 构建 | catkin（`roscpp`, `motion_prediction`）；无测试、无可执行 main |
| 对应论文 | §3 全部（式 (1)(2)(3)(8)(9)(10)(11)(15)） |

**保真度**：式 (2) **逐项一致**（唯一的 `CODE_MATCH`）；式 (3) 通过内置 LPV 一致；式 (8)(10)(11)(15) **是另一套实现**（详见 `P5_EQUATION_AUDIT.md` §2）。

**可用性**：作为"官方参照实现"只能用于**式 (2) 的数值对照**与"官方变体长什么样"的记录；不能作为"论文 (11) 的实现"。API 是"你自己在循环里喂状态、取期望速度"，没有可运行示例。

### 2.2 `SinaMirrazavi/QP_IK_solver`

| 项 | 值 |
|---|---|
| HEAD | `f1c28fc17da5...`（2019-05-14） |
| 许可证 | LICENSE = LGPL-3.0；头注释 = GPL v2 or later |
| 规模 | 245 KB，8 个文件，C++ |
| 核心 | `src/qp_ik_solver.cpp` 726 行、`include/qp_ik_solver.h` 191 行 |
| 构建 | catkin + **CVXGEN 生成代码** + NLopt（硬编码 `/usr/local/lib/libnlopt.so.0.8.2`） |
| 对应论文 | 式 (17)–(23)、定理 3 |

**这是本次审计中问题最多的仓库**，逐条列证据（行号为 HEAD 版本）：

| 编号 | 事实 | 证据 | 后果 |
|---|---|---|---|
| Q1 | **CVXGEN 代码缺失**，作者因授权主动删除 | README 原文："Due to the license, I needed to remove CVxgen… This package will not work without CVXGEN!"；`CMakeLists.txt` 引用 `cvxgen/solver.cpp`、`cvxgen/ldl.cpp`、`cvxgen/example/testsolver.cpp` | `cmake` 阶段直接失败 |
| Q2 | 依赖 **NLopt 硬编码绝对路径** | `target_link_libraries(... /usr/local/lib/libnlopt.so.0.8.2 ...)` | 换机器即失败 |
| Q3 | `get_gamma(double&)` **只声明未定义** | 头文件 103 行有声明，`qp_ik_solver.cpp` 无定义 | 任何调用都链接失败 |
| Q4 | `Gamma_`、`DGamma_` **从不更新** | `Finalize_Initialization()` 置 `Gamma_=2`、`DGamma_=0`；全文件 grep 无其他赋值 | **SCA 约束在公开代码中是死代码**（O9） |
| Q5 | `lambda` **未初始化** | 头文件 161 行 `double lambda;`，无构造函数/默认值 | `b` 的 SCA 项取值不确定（O3） |
| Q6 | `Omega_projector()` **返回输入而非输出** | 函数体算了 `output(i)=min(max(...))`，最后 `return Input;` | 该函数若被调用则投影恒等（当前主循环走内联版本，未触发）（O4） |
| Q7 | `svm_grad` 在 `package.xml/CMakeLists` 里，但**源码从未 include/调用** | grep 无 `svm` | SCA 评估链路根本没接上（O9/O10） |
| Q8 | `Super_constraint` 的 sigmoid 平滑**论文未描述** | `Construct_boundaries_vel()`：`U_plus=1e5/(1+1e4·exp(−10·C))` | 官方实现比论文多一层机制 |
| Q9 | 无 main、无测试、无 launch 文件 | 目录清单 | 无法"跑起来"，只能被别的包链接 |

**保真度**：式 (19)(20)(21a)(23) 逐行一致（`CODE_MATCH`）；式 (17) 结构在、求解器缺（`CODE_PARTIAL`）；式 (17d)(21b) 不可用（`CODE_DIVERGENT`）；式 (22) 有缺陷（`CODE_BUGGY`）。

**结论**：这个仓库**不能作为"可执行参照"**，但**极有价值**：它把 LVI 的块矩阵装配（式 21a）写得很直白，是可以逐行对照的"论文→代码"翻译，也是我们实现 P5-T04/T05 时最强的结构参考。

### 2.3 `SinaMirrazavi/SCA_data_construction`

| 项 | 值 |
|---|---|
| HEAD | `ed3c3cda576e...`（2018-08-08） |
| 许可证 | LGPL-3.0（LICENSE）/ GPL-2+（头注释） |
| 规模 | 22.3 MB，37 个文件，C++ |
| 核心 | `src/constructing_data_set.cpp`、`src/analysing_data_set.cpp`、`include/common.h` |
| 依赖 | mathlib、skinematics、sgaussians、kuka_fri_bridge、mlpack、OpenMP |
| 对应论文 | 式 (27)、§5.2 数据构造、式 (1) 的 workspace GMM |

**可复现的关键常量（全部硬编码在源码里，与论文可对照）**：

| 量 | 代码值 | 论文值 | 一致性 |
|---|---|---|---|
| 关节采样步长 | `resolution = 3`（×10° = **30°**） | **20°** | ❌ 不一致（O5） |
| 位置限位 | `±170°`（q1,q3,q5,q7）、`±120°`（q2,q4,q6） | 同 | ✅ |
| DH（IIWA 型） | `d1=0.36/0.34, d3=0.42/0.40, d5=0.40, a=0, α=±π/2` | 未给出 | 只能在代码里取 |
| 球半径和 | 由 `setDH` 的球参数决定（论文 r*_i+r*_j=20 cm） | 10 cm/球 | 需逐场景核对 |
| 边界带 | `0.30 < d < 0.33` | `b⁻=30 cm, b⁺=33 cm` | ✅ |
| base 偏移 | `(0, 1.33, 0.06)`（`Position_base`） | `[0, 1.3, 0.34]` | ❌ 不一致（O6） |

另外：`include/common.h` 里 `folder_path` 需要用户手动改成自己的 home；`constructing_data_set.cpp` 用注释切换**多套**机器人布置（2 臂 / 3 臂）。也就是说"论文那一套"并没有被单独参数化，只能靠读源码还原。

**可用性**：生成数据集**理论上可复现**（依赖闭包完整），但需要 ROS1 + 4 个 EPFL 内部包 + mlpack + 手工改路径；成本高（论文自己说 12k 点约 1 天）。**D082 不重跑**，只把常量作为"官方几何"的取证来源。

### 2.4 `nbfigueroa/SCA-Boundary-Learning`

| 项 | 值 |
|---|---|
| HEAD | `147afdb10b74...`（2018-03-21） |
| 许可证 | **根目录无 LICENSE**；仅 `svm_perf/LICENSE.txt`（SVM-Struct, T. Joachims） |
| 规模 | 34.4 MB，111 个文件，MATLAB + 预编译 mex |
| 核心 | 4 个学习脚本（`boundary_learning_2d.m`、`boundary_learning_robots.m`、`boundary_learning_sparse_CPSP_2D.m`、`boundary_learning_sparse_CPSP_robots.m`）+ `models/` |
| 对应论文 | 式 (24)(25)(28)、Fig.5/Fig.9/Fig.10/Fig.22 |

**这是本次审计中"最有价值"的仓库**，因为**训练好的模型随仓库发布**：

| 模型文件 | 类型 | 关键字段（实测） | SHA256 前 16 位 |
|---|---|---|---|
| `models/cpsp_models/2d_example.mat` | CPSP（2D 玩具，Fig.5） | `D=2, Nbvs=40, gamma=50, bias=0` | `4e9efd5f85a34523` |
| `models/cpsp_models/NewIIWASetup-Feb18-SparseModel.mat` | CPSP（36D 双臂） | `D=36, Nbvs=3000, gamma=3.3, bias=0` | `9f217f512b50816d` |
| `models/NewSetup-IIWAs-Feb18/36D-24k-...-OptimalModel.mat` | libSVM 精确模型 | `totalSV=7262`, `rho=−3.5749`, `sigma` 存于 `model.sigma` | `107d77ecb01e8d2c` |
| `models/cpsp_models/robot-collision-{067k,130k,270k,540k}.mat` | CPSP 系列 | 各 3000 BV（与论文 `k_max` 一致） | 见 manifest |
| `svm_perf/robotCollision/36d-540k-...-Model-3000.dat` | svm_perf 文本模型 | 头注释 `-g 0.9298`、`3001 SVs`、`b=0`（**与 .mat 的 gamma=3.3 不同**） | `6bbff62f8d56134a` |

**三个关键结论**：

1. **评估链路可复现，训练链路不可复现**。模型在，但训练集（`../function_learning/collisionDatasets/...`）**不在仓库里**，脚本里引用的是作者本机相对路径。因此"重新训练一个 FPR=1.45% 的模型"做不到；"用官方模型复算指标"做得到。
2. **`gamma` 与 `sigma` 的语义陷阱**：`.mat` 里的 `gamma` 是 `λ=1/(2σ²)`（来自 svm_perf 的 `-g`），不是论文的 `σ`。`gamma=3.3 ⇒ σ≈0.389`。
3. **`bias=0`**：分类边界落在决策函数的**零点**，而不是论文 (16) 要求的 `Γ=1`（O7）。

**缺失的能力**：全仓库 **没有任何 Jacobian / 运动学导数**代码（grep 无 `Jacobian`）。也就是说式 (26) 的 `∂f/∂q` 在这一侧完全没有实现，SCA 梯度只能在**特征空间**（36 维）里算，无法直接给关节空间 QP 用。

### 2.5 `nbfigueroa/SVMGrad`

| 项 | 值 |
|---|---|
| HEAD | `4f79d2de5366...`（2019-09-04） |
| 许可证 | **根目录无 LICENSE**；源码头声明"free for non-commercial academic use… must not be modified or distributed without prior permission" |
| 规模 | 92.9 MB，212 个文件，MATLAB + C++（catkin 包 `svm_grad`） |
| 核心 | `matlab/classifier/{calculateGamma,calculateGammaDerivative,calculateClass}.m`、`matlab/kernel/*`、`svm_grad/src/svm_grad/svm_grad.cpp` |
| 对应论文 | 式 (24)(25)，以及 C++ 端的在线评估 |

**保真度**：MATLAB 与 C++ 两条实现一致，`λ=1/(2σ²)`，梯度 `−2λ·k·(x−x_s) = −(1/σ²)k(x−x_s)`，与 (25) **一致**。

**文档缺陷**：README 把梯度写成 `−1/(2σ²)·α y k (x−x_i)`，比代码与论文少一个因子 2。**以代码为准**，但这条差异足以让照着 README 实现的人得到"梯度只有一半"的结果，必须记录。

**依赖**：MATLAB 端 `svm-lite` 有预编译 `.mexa64`（Linux x86_64）；C++ 端只依赖 Eigen + catkin，是全套里最轻的。

### 2.6 `SinaMirrazavi/LPV`

| 项 | 值 |
|---|---|
| HEAD | `27772473ee0d...`（2017-11-03） |
| 许可证 | LGPL-3.0 |
| 规模 | 19 KB，7 个文件，C++（仅库，无 main） |
| 核心 | `src/LPV.cpp` 586 行：GMM + LPV |
| 对应论文 | 式 (3) 与 GMR 调度参数 |

**保真度**：`Calculate_A()` = `Σ A_k θ_k`；`Calculate_Theta()` = 先验×高斯后验再归一化，`sum<1e-100` 时退化均匀。与论文描述一致（`CODE_MATCH`）。

**价值**：这是"θ 归一化"最直接的官方证据；P5-T02 可以用它作为语义参照（但用 numpy 重写，不引入 C++ 依赖）。

### 2.7 `SinaMirrazavi/SESODS_lib`（Table 2 拼作 SESOSDS_lib）

| 项 | 值 |
|---|---|
| HEAD | `7503728c99c2...`（2019-02-12） |
| 许可证 | LGPL-3.0 |
| 规模 | 49 MB，276 个文件，MATLAB |
| 内容 | `Convex/`（LMI 约束下学习稳定二阶 DS）、`Non_convex/`（SEDS 系列） |
| 对应论文 | 式 (3) 的**上游**：如何得到 `A_ik` |

**注意**：它解决的是"**学一个稳定的 DS**"，不是"**验证 (5) 的 LMI**"。两者容易混淆。P5-T02 需要的是后者，而官方没有提供；前者只能作为"我们怎么造 A_ik"的参考。

### 2.8 两个外部依赖

- `epfl-lasa/ML_toolbox`（26.8 MB，MATLAB，无 LICENSE）：libSVM 封装 + 交叉验证 + 网格搜索。论文 §5.3 的 σ/C 搜索用它。**不可直接用于 Python 复现**，但算法（网格搜索 + 10 折交叉验证）可复写。
- `epfl-lasa/kuka-rviz-simulation`（1.29 MB，C++，无 LICENSE）：KUKA + RViz 仿真，论文 E06/E07 的实验平台。与算法无关。

---

## 3. 可执行性矩阵（静态判定）

| 仓库 | 能否原样构建 | 阻断项 | 能否原样运行 | 备注 |
|---|---|---|---|---|
| Multiarm_ds | ❌ | 需 ROS1 catkin + `motion_prediction` + `mathlib`；无 main | ❌ | 库形态，需自写驱动 |
| QP_IK_solver | ❌ | **CVXGEN 目录不存在**（cmake 直接失败）；NLopt 绝对路径；`get_gamma` 未定义 | ❌ | 即使修好，SCA 仍是死代码 |
| SCA_data_construction | ❌ | 需 ROS1 + mathlib/skinematics/sgaussians/kuka_fri_bridge + mlpack；`folder_path` 需手改 | ❌ | 生成一套数据集需数小时–数天 |
| SCA-Boundary-Learning | ⚠️ 部分 | 2D 示例的数据 `data/2d-example2.mat` 在；"robots" 脚本引用的数据集**不在仓库** | ⚠️ | 依赖 MATLAB + 预编译 `.mexa64` |
| SVMGrad | ⚠️ 部分 | MATLAB 示例有模型可跑；C++ 包需 catkin+Eigen | ⚠️ | 最轻量的可跑组件 |
| LPV | ⚠️ 部分 | 仅库，需 Eigen；无测试 | ❌ | 只能被链接 |
| SESODS_lib | ⚠️ 未知 | 需 MATLAB + LMI 求解器（PENBMI/YALMIP 等，未验证） | ⚠️ | 与 D082 无关 |

**统一结论**：**没有一个仓库能"下载即跑"**。这与论文的可复现性声明无关（作者提供了算法核心），但与"复现工程"直接相关：任何复现都必须自己搭驱动、自己补 SCA 链路、自己替换求解器。

---

## 4. 许可证与合规策略

### 4.1 事实

| 仓库 | LICENSE 文件 | 源码头注释 | 冲突？ |
|---|---|---|---|
| Multiarm_ds | LGPL-3.0 | GPL-2.0-or-later | **是** |
| QP_IK_solver | LGPL-3.0 | GPL-2.0-or-later | **是** |
| SCA_data_construction | LGPL-3.0 | GPL-2.0-or-later | **是** |
| LPV | LGPL-3.0 | （未见头注释） | 否 |
| SESODS_lib | LGPL-3.0 | — | 否 |
| SCA-Boundary-Learning | **无** | — | 无许可证声明 |
| SVMGrad | **无** | "free for non-commercial academic use… must not be modified or distributed" | **限制性声明** |
| ML_toolbox / kuka-rviz | 无 | — | 无许可证声明 |

LGPL-3.0 与 GPL-2.0-or-later 是**不同**的许可证，不能互相覆盖。作者意图大概率是 "GPL/LGPL 双许可" 或 "文件头没跟上 LICENSE 变更"，但**我们无权替作者裁定**。

### 4.2 本项目采取的策略（写进规范）

1. **不 vendor、不复制、不修改**任何官方源码进本仓库。
2. 只记录 URL + commit SHA + SHA256；需要时按 SHA 下载到**仓库外**的工作目录，用完即弃（或留在 `.work/` 且不入库）。
3. 模型文件按"学术、非商业、只读评估"使用；**不重新分发**，报告里只给指纹与字段统计。
4. 复现代码**从公式重写**（clean-room，以论文 + 本审计为依据），而不是改官方代码。这样既避开许可证冲突，也保证"独立实现"的科学价值。
5. 若未来需要分发任何官方派生物，先向作者确认许可证（LGPL-3 vs GPL-2+ / SVMGrad 的非商业条款）。

---

## 5. 对复现范围的直接结论

| 官方资产 | 在 D082 中的角色 | 允许的表述 |
|---|---|---|
| 式 (2) 的 `Multiarm_ds` 实现 | **数值对照基准**（同式不同实现） | "与官方实现在式 (2) 上逐项一致" |
| 式 (8)(10)(11)(15) 的官方实现 | **DEVIATION_REFERENCE**（记录差异，不追平） | "官方实现采用另一种 τ/γ/U 定义，差异已量化" |
| `QP_IK_solver` 的 M/b 装配 | **结构参照**（式 21a 的翻译） | "块矩阵装配与官方代码一致；求解器自行实现" |
| `QP_IK_solver` 的 SCA 链路 | **不可用**（死代码 + 缺 CVXGEN） | "官方 QP 未接入 SCA，不能作为对照" |
| `SCA-Boundary-Learning` 的模型 | **官方模型**（只读评估） | "使用官方预训练模型复算 Γ 与 ∇Γ 及分类指标" |
| `SCA-Boundary-Learning` 的训练流程 | **不可复现**（数据集未发布） | "训练集未随仓库发布，重训不在范围内" |
| `SVMGrad` 的公式 | **语义参照**（MATLAB/C++ 双实现互证 (24)(25)） | "梯度公式与官方 MATLAB/C++ 实现一致" |
| `SCA_data_construction` 的 DH/常量 | **几何取证** | "FR3 需重建；IIWA 几何取自官方源码" |

**一句话**：官方代码足以支撑**"数学对照"**与**"模型评估"**，但**不足以支撑"可执行复现"**——后者必须我们自己写。这正是 `P5_IMPLEMENTATION_PLAN.md` 的前提。
