# P1 官方代码审计（Official Code Audit）

> 配套：`P1_PAPER_STUDY.md`、`P1_EQUATION_AUDIT.md`
> 论文：Zhu, Mao, Yang, Li, IEEE T-RO 42 (2026) 1941–1958，DOI `10.1109/TRO.2026.3686224`
> 官方项目页：`https://dq-gpu-mpc.github.io/`（仅链接代码与视频，无数据/参数）
> 本文件只读审计，**未安装依赖、未编译扩展、未初始化 GPU 上下文、未运行任何论文算法**。

---

## 1. 审计对象与固定 SHA

### 1.1 仓库与快照

| 仓库 | 引用 | SHA | 提交日期 | 提交信息 | 说明 |
|---|---|---|---|---|---|
| `zhutianqi2006/dual_arm_gpu_mpc` | `main` | `fe5b49f7bb49c60911243fa809de311daad078e3` | 2026-04-17 | `feat: publish new kmeans-adpan mainline` | 论文上线前的重构主线；精简包结构 |
| `zhutianqi2006/dual_arm_gpu_mpc` | `pre-paper-accept`（tag） | `1820a9e8bb8865014fa2a7ffee5bd69ca0773cad` | 2026-01-24 | `update some example` | 投稿前快照；含全部基线与 42 个场景目录 |
| `zhutianqi2006/cuda_dq_kernel` | `main` | `231f130e6c770e4c58168c393d393d9c04fbd4d6` | 2026-04-17 | `feat: publish refactored dq torch package` | 重构后的 `src/native` 包 |
| `zhutianqi2006/cuda_dq_kernel` | `pre-paper-accept`（tag） | `c762b7d69c7a3db69c122a27f7dc287c7efc0c32` | 2025-09-08 | `Update README.md` | 单文件 `dq_kernel.cu` 结构 |

### 1.2 快照指纹

| 文件 | 字节 | SHA256 |
|---|---|---|
| `dual_arm_gpu_mpc` @ `fe5b49f7` tar.gz | 65 MB（解包 371 MB） | `7ed99e5eb56f4b87a896422eea2577593735fe2e96530cdb284bf83d14e1b223` |
| `dual_arm_gpu_mpc` @ `1820a9e8` tar.gz | 112 MB | `cea777f016a854ec1d5105d6bc35874c75f2844ed4c2e79fb78a636a0cff8823` |
| `cuda_dq_kernel` @ `231f130e` tar.gz | 159 KB | `d4363fc97622f54eb3fdb6081dabc857ecd490e176c6c64a48e91446942ed47f` |
| `cuda_dq_kernel` @ `c762b7d6` tar.gz | 148 KB | `bdc8c30d590ebb510e9bb1ff594dbbf48f9a6e4affaa3c8f6a7c873631781d3e` |
| 主仓库 `kmeans_adpan.py`（post） | — | `84ca7e9fe6b962f0b8f4dec6f6e2a5f36161d69c7070ba6b3907c1c6f431f6d2` |
| 主仓库 `common_ops.py`（post） | — | `8ca0360bcc4a026831f4513dd3af52a431df928bf1dfa0bd7641612de5ee57fa` |
| 主仓库 `mppi_kmeans_adpan_module.py`（pre） | — | `a03d8a9bd92eb7602d489693d661af60ef0624d99c333403ea71df25ef51e34b` |
| 内核 `mppi_project_step.h`（post） | — | `cd9664ec76857bd6f7078b4932d2620c2ae15c269af13e08119cd6b0f0a17b7d` |
| 内核 `dq_composite_ops.cuh`（post） | — | `5d098bba0262f91af5b35ef3316475bb573b7ad61a34925f4132e5cbcb6daa0d` |

完整清单见 `evidence/P1_official_code_manifest.json`。

### 1.3 为什么必须审计两个快照

`main` 是重构后的"可发布"版本，只保留 `Ours` 与 `Ours without cluster` 两个控制器、4 个示例目录。论文表 II 的 14 个控制器里，有 12 个**只在 `pre-paper-accept` 快照中存在**；六个仿真场景里只有前三个在 `main` 中有对应目录。若只看 `main`，会得出"基线缺失、场景缺失"的结论；若只看 `pre`，会误以为存在一套可直接运行的包（实际是 42 个互相复制的示例脚本 + 33 个 `utils` 模块，18,351 行）。两者都看，才能给出正确的"可复现边界"。

---

## 2. 许可证与使用边界

| 仓库 | GitHub API `license` | 仓库内 LICENSE/COPYING/NOTICE |
|---|---|---|
| `dual_arm_gpu_mpc`（两个快照） | `null` | 0 个 |
| `cuda_dq_kernel`（两个快照） | `null` | 0 个 |

**结论**：仓库**未授予任何开源许可证**。默认版权规则下，"保留所有权利"。

对 P1 的实际约束：

1. **可以**阅读代码、理解算法、在论文层面复现其数学（算法思想不受版权保护）。
2. **不可以**把上游源码复制进本仓库、以本仓库许可证再分发，或把 `cuda_dq_kernel` 作为本项目的 vendored 依赖提交。
3. **可以**在本地为验证目的构建/运行上游代码（若后续阶段获批），但不得随交付物分发其二进制或源码。
4. 任何"引用上游实现作为 oracle"的方案，必须在报告中标注"仅本地验证，不再分发"，并优先使用独立实现（`dqrobotics` 或自写 SE(3)）作为 oracle。

这是 G0 的硬约束，写入 `P1_IMPLEMENTATION_PLAN.md` 的依赖策略。

---

## 3. 依赖与版本

### 3.1 主仓库（post，`fe5b49f7`）

`pyproject.toml`：

```
requires-python = ">=3.10,<3.11"
numpy>=1.26,<2 ; scipy>=1.15,<2 ; pyyaml>=5.4
dqrobotics==23.4.0a22 ; kmeans-pytorch ; pybind11>=3,<4
torch==2.9.1 ; torchvision==0.24.1 ; torchaudio==2.9.1   (pytorch-cu126 index)
```

`environment.yml` 追加：`networkx, trimesh, scikit-image, tqdm, importlib-resources, numpy-quaternion, yourdfpy>=0.0.60, warp-lang>=1.12.1, pytest`。

README 的"已验证基线"：Ubuntu 22.04、Python 3.10.12、`uv 0.7.19`、PyTorch 2.9.1+cu126、CUDA 12.6、`curobo` 源码安装（`pip install -e . --no-build-isolation`）、ROS 2 Humble（在线控制器）。

### 3.2 内核仓库（post）

README 基线同上（CUDA 12.6 / torch 2.9.1 / Python 3.10.12）；`setup.py` 用 `CUDAExtension`，编译选项含 `-O3 -use_fast_math -Xptxas -O3 -dlcm=ca`。**`-use_fast_math` 会影响浮点可复现性**（尤其 `sqrt`/`exp`/`log`），逐位对齐 CPU 参考实现不应作为验收标准。

### 3.3 内核仓库（pre）

README 基线：Ubuntu 22.04、**CUDA 11.8、PyTorch 2.0.1**；结构为单文件 `dq_kernel.cu`（2,341 行）+ `dq.cpp`（193 行）+ `dq_torch.pyi`。

**含义**：论文 Fig. 8 的计时（260/330 ms CPU，1.1/1.6 ms GPU，20,000 次实例）来自**旧栈**（CUDA 11.8 / torch 2.0.1），不是 `main` 的新栈。用新栈复现得到的绝对时延不能与论文直接比较。

### 3.4 未声明的依赖

- **PyBullet**：`examples/*/bullet_robot_ros.py`、`examples/ur_real_arm_ros.py` 直接 `import pybullet`，但 `pyproject.toml` / `environment.yml` 均未声明。
- **cuRobo**：不在 `pyproject.toml`，需按 README 从源码安装（依赖 `git-lfs`、`warp-lang`）。
- **ROS 2**：`src/dual_arm_gpu_mpc/ros/*` 在模块导入期即 `import rclpy`，因此**没有 ROS 2 时高层控制器无法 import**（README 亦承认）。
- **MATLAB**：README 提到 `analysis/matlab`，实际目录不在快照中。

### 3.5 本机环境（只读清点，未安装）

| 项 | 值 | 与论文/上游的差距 |
|---|---|---|
| GPU | NVIDIA RTX 3070 LHR（GA104，8 GB，sm_86） | 论文为 RTX 4080 Laptop |
| 驱动 | 580.178.04 | — |
| CUDA Toolkit | **未安装**（无 `/usr/local/cuda`、无 `nvcc`） | 需要 12.6（post）或 11.8（pre） |
| Python | 3.10.12（系统） | 与上游一致 |
| PyTorch | **未安装** | 需 2.9.1+cu126 |
| ROS 2 / cuRobo | 未安装 | 需 Humble / 源码 |

**结论**：GPU 路径（模块 G）在本机需要一整套 CUDA/PyTorch/cuRobo/ROS 安装，属于 G0 明确排除的动作；且硬件级别不同，绝对时延不可比。

---

## 4. 代码结构

### 4.1 post（`fe5b49f7`）：精简包

```
dual_arm_gpu_mpc/
├── src/dual_arm_gpu_mpc/            # 3,228 行 Python
│   ├── controllers/high_level/mppi/
│   │   ├── base.py        (397)     # 公共状态、碰撞代价、L 指标、play_once
│   │   ├── adpan.py       (426)     # 两阶段，无聚类（= "ours without cluster"）
│   │   ├── kmeans_adpan.py(528)     # 两阶段 + k-means（= "ours"）
│   │   └── common_ops.py  (316)     # 采样器、权重、代价、零空间
│   ├── controllers/low_level/relative.py (116)   # 式 (50)(51)
│   ├── robotics/dq/manipulability.py (395)       # 可操作度（pdet/gram/yoshikawa）
│   ├── robotics/collision/curobo_loader.py       # cuRobo 世界/机器人
│   ├── ros/{high,low}.py                         # ROS2 收发
│   └── config/{loader,hydra}.py                  # YAML/Hydra
├── configs/{robot,world,experiment}              # cuRobo 机器人/世界、实验
├── examples/{sim1_ur,sim2_ur,sim3_ur,exp1_ur}    # 4 个场景
├── model/{dual_arm_model,dual_panda_model,...}   # URDF + meshes（370 MB）
└── tests/{unit,integration}                      # 11 个测试文件
```

内核 `cuda_dq_kernel`（post）：`src/native/{bindings,kernels,host_ops,include}`，2,980 行；导出 23 个算子，其中复合算子 `rel_abs_pose_rel_jac`、`rel_abs_pose_rel_abs_jac`、`mppi_project_step` 是控制器的主路径。

### 4.2 pre（`1820a9e8`）：实验脚本集合

```
dual_arm_gpu_mpc/
├── examples/            # 42 个场景目录（sim1_ur … sim29_kl, exp1_ur … exp4_ur）
├── utils/               # 33 个模块，18,351 行
│   ├── mppi_{std,log,fre,biased,high}_{exp,std}_module.py   # 基线
│   ├── mppi_{adpan,kmeans_adpan,kmeans_an,an}_module.py     # 本文及消融
│   ├── cem_module.py / icem_module.py / mppi_five_module.py # CEM 三套
│   └── crocoddyl_ddp_vfi_module.py                          # DDP/VFI 对照
├── model/               # 同一套 URDF/meshes
└── envs/ddp             # DDP 环境
```

**结构判断**：`main` 是 `pre` 的**模块化重构**，不是重写。逐行对比 `utils/mppi_kmeans_adpan_module.py`（1,070 行）与 `src/.../kmeans_adpan.py`（528 行），两阶段结构、停滞项形式、`param_lambda=0.5`、k-means 特征、精英选模、簇内聚合全部一致；差异主要是把重复代码抽到 `common_ops.py`、把配置读取统一到 `ConfigModule`。这支持"公开代码是论文实验代码的后继重构"这一判断，但不等于"代码忠实于论文式子"——两者都有 §6 列出的偏差。

---

## 5. 示例、场景与模型文件

### 5.1 场景覆盖

| 论文实验 | 平台 | `main` 对应 | `pre` 对应（推测） | 判定 |
|---|---|---|---|---|
| Task 1 点到点 | UR3+UR3e | `examples/sim1_ur` | `sim1_ur` | 有 |
| Task 2 窄通道 | UR3+UR3e | `examples/sim2_ur`（静态障碍） | `sim2_ur` | 部分（"窄通道"几何未文档化） |
| Task 3 单动态障碍 | 双 Franka | `configs/world/franka_dynamic_exp1_env.yml`，**无示例脚本** | `sim3_franka`… | 缺示例 |
| Task 4 双动态障碍 | 双 Franka | 仅 world 配置 | `sim4_franka`（推测） | 缺 |
| Task 5 静动混合 | 双 Franka | 仅 world 配置 | `sim5_franka`（推测） | 缺 |
| Task 6 十字障碍 | 双 Franka | 无 | `sim14_ur_cross`（UR 版） | 缺（且平台不符） |
| 真机 5 组 | UR3+UR3e | `examples/exp1_ur` | `exp1_ur`…`exp4_ur` | 仅 1 组公开 |

`configs/world` 有 7 个世界文件（`dual_arm_collision_env`、`ur_p2p_exp1`、`ur_dynamic_exp1`、`franka_static_exp1`、`franka_dynamic_exp1/2/3`），说明 Franka 场景的碰撞世界是存在的，但**没有对应的控制器入口脚本**；`pre` 快照里 `sim3_franka`…`sim6_franka` 很可能就是这四个任务，但没有任何 README 或映射表，不能当作已确认。判定：`AMBIGUOUS` + `MISSING`。

### 5.2 模型文件

- `model/dual_arm_model/`（85 MB）：`dual_arm_model.urdf`、`dual_arm_notray_model.urdf`、`meshes/`；
- `model/dual_arm_model_without_plane/`（85 MB）、`model/dual_panda_model/`（201 MB）、`model/plane/`；
- `configs/robot/dual_arm_model_real.yml`：cuRobo 机器人配置，`collision_link_names` 12 个 + `flange1`，逐 link 的 `collision_spheres`（中心 + 半径），对应论文 Fig. 6 的"球近似"；
- `configs/world/*.yml`：长方体障碍（`dims`、`pose`、`color`）。

**可用性**：URDF + 球近似 + 世界文件足以在**不装 cuRobo** 的情况下自建一个 CPU 碰撞检查器（球-球、球-长方体），这是模块 E 能在纯 Python 上做的关键。反过来，若要逐字复现论文的碰撞代价，必须用 cuRobo 的激活距离语义（距离为 0 表示未激活），属于外部依赖。

---

## 6. 缺失组件（按对复现的影响排序）

| # | 组件 | 证据 | 影响 | 分类 |
|---|---|---|---|---|
| 1 | 表 II 的 12 个基线（MPPI/Log/Fre/Biased/High/CEM） | `main` 仅有 `adpan.py`、`kmeans_adpan.py`；`pre` 有对应 `utils/mppi_*_module.py` | 表 II 无法在 `main` 上复现；`pre` 可用但无文档 | MISSING（main） |
| 2 | Task 3–6 的场景脚本 | 仅有 world 配置；`pre` 目录无映射 | 六个场景只能复现前两个 | MISSING |
| 3 | 动态障碍速度膨胀 | `update_obstacle_velocity_estimate(): pass`（`base.py:256-257`，`pre` 同） | 论文 §VII-C 的机制完全缺失；动态任务只能靠"障碍球固定半径 + 位置流"近似 | MISSING |
| 4 | 30 Hz 高层节流 | 示例 `while True: play_once()`，无 `sleep`/定时器 | 论文的实时频率无法由代码复现；只能测单次求解耗时 | MISSING |
| 5 | 高层/低层频率分离 | 两侧都用 `ros_update_rate: 125` | 与论文 30/125 Hz 不符 | CODE_MODIFIED |
| 6 | "ours without adp" 消融 | 所有模块都含 `update_c`；命名 `an`/`adpan` 无文档 | 消融标签无法唯一映射 | AMBIGUOUS |
| 7 | 原始实验日志/逐 trial 数据 | 仓库无 `results/`、无随机种子记录（除代码内 seed=0） | 表 II 的数值无法核对 | MISSING |
| 8 | 参数表与 YAML 的一致性 | 见 `P1_EQUATION_AUDIT.md` §10 | 两套参数，无法判断论文用哪套 | AMBIGUOUS |
| 9 | 真机数据/标定 | 仅示例脚本与 AprilTag 话题 | 真机实验不可复现 | MISSING（硬件） |
| 10 | `analysis/matlab` | README 提到，快照中不存在 | 无关算法 | MISSING（文档） |

---

## 7. 论文公式 → 源码映射与分类

分类口径：`ORIGINAL` 逐项实现；`CODE_MODIFIED` 实现了不同但相关的形式；`MISSING` 不存在；`AMBIGUOUS` 无法唯一判定；`EXTERNAL_DEPENDENCY` 依赖外部库。

| # | 组件 | 论文 | 源码（post） | 分类 | 关键差异 |
|---|---|---|---|---|---|
| 1 | DQ 乘/共轭/逆/norm/sqrt/exp/log | (1)–(6) | `dq_primitives.cuh` | ORIGINAL | float32 + fast-math |
| 2 | DH/MDH 正运动学 | (10) | `dq_composite_ops.cuh:44-85` | ORIGINAL | — |
| 3 | 相对位姿 | (7) | 同上 `:113-116` | ORIGINAL | — |
| 4 | 绝对位姿 | (8) | 同上 `:114-118` | AMBIGUOUS | 论文印 $x_2^*x_{r/2}$，代码 $x_2\sqrt{x_r}$ |
| 5 | 相对雅可比 | (11) | 同上 `:120-127` | ORIGINAL | 解析列，无差分 |
| 6 | 绝对位姿雅可比 | (11) | `rel_abs_pose_rel_abs_jac` | ORIGINAL | 导出但控制器未用 |
| 7 | 绝对直线/倾角 | (9)(17)(32) | 同上 `:130-135`；`common_ops.py:182-187` | CODE_MODIFIED | 只算方向，无矩 |
| 8 | 零空间投影 | (26)(27) | `mppi_project_step.h:60-70` | ORIGINAL | 阻尼 $10^{-16}$，float64 |
| 9 | 投影 + 限幅 $g$ | (28)(31) | 同上 `:72-88` + `kmeans_adpan.py:240-243` | ORIGINAL | 加速度限幅在 Python 侧 |
| 10 | 第一阶段采样 | (20) | `common_ops.py:266-316` | CODE_MODIFIED | 频域有色噪声，非高斯 |
| 11 | 停滞项 | (42) | `kmeans_adpan.py:259-265` | CODE_MODIFIED | $p_s$ 在分母、平方 $L_2$ |
| 12 | k-means | (22)(52) | `kmeans_adpan.py:299-306` | EXTERNAL_DEPENDENCY | `kmeans_pytorch` |
| 13 | 精英选模 | §V-4 | `kmeans_adpan.py:307-327` | ORIGINAL | 众数，非加权得分 |
| 14 | 簇内聚合 | (23) | `kmeans_adpan.py:328-336`；`common_ops.py:72-85` | ORIGINAL | 噪声形式 + 滑动平均 |
| 15 | 第二阶段采样 | (24) | `common_ops.py:240-263` | CODE_MODIFIED | 对数正态且实虚同种子 |
| 16 | 第二阶段聚合 | (24) | `kmeans_adpan.py:417-426`；`common_ops.py:56-69` | ORIGINAL | 自适应 λ |
| 17 | 奇异项 | (36)(37) | `kmeans_adpan.py:413-416,429-439` | CODE_MODIFIED | 终端、仅第二阶段、权重 0.5 |
| 18 | 碰撞代价 | (33)(34) | `base.py:280-294` | EXTERNAL_DEPENDENCY | cuRobo 距离二值化 |
| 19 | 倾角代价 | (32) | `common_ops.py:182-187` | ORIGINAL | — |
| 20 | 关节限幅 | (13)–(15) | `mppi_project_step.h:72-88` | ORIGINAL | 位置/速度硬，加速度外层 |
| 21 | 辅助控制器 | (44)–(46) | `kmeans_adpan.py:441-487` | ORIGINAL | 阻尼伪逆 $10^{-7}$ |
| 22 | $L$ 指标与切换 | (47)–(49) | `base.py:318-325,360-384` | ORIGINAL | $C_s$ 取第一阶段 min |
| 23 | 低层相对控制 | (50)(51) | `relative.py:69-93` | ORIGINAL | — |
| 24 | 动态障碍膨胀 | §VII-C | `base.py:256-257` | MISSING | `pass` |
| 25 | 基线控制器 | 表 II | 仅 `pre` 的 `utils/mppi_*` | MISSING | main 已删 |
| 26 | 六个仿真场景 | Fig. 9 | 4 个示例 | MISSING | T3–T6 缺 |
| 27 | 30 Hz 高层 | §VIII-A | 无节流 | MISSING | — |
| 28 | GPU 批处理内核 | §VII | `kernels/*.cu` | ORIGINAL | — |
| 29 | dqrobotics CPU 模型 | (44)(50) | `base.py:8-13` | EXTERNAL_DEPENDENCY | 双实现（CPU/GPU）需一致 |
| 30 | kmeans_pytorch | (22) | `kmeans_adpan.py:39` | EXTERNAL_DEPENDENCY | GPU k-means |
| 31 | ROS 2 IO | — | `ros/*.py` | EXTERNAL_DEPENDENCY | 导入即依赖 |
| 32 | PyBullet 仿真 | — | `examples/*/bullet_robot_ros.py` | EXTERNAL_DEPENDENCY | 未在依赖中声明 |
| 33 | 碰撞球模型 | Fig. 6 | `configs/robot/*.yml` | ORIGINAL | 逐 link 球 |
| 34 | 每周期重置种子 | — | `common_ops.py:288,290` | CODE_MODIFIED | 随机采样变确定性 |
| 35 | 终端绝对位姿代价 | (38) | `common_ops.py:121-133` | CODE_MODIFIED | 8 维差 + 3 维位置差，位置双计 |

**分类统计（35 项）**：`ORIGINAL` 17、`CODE_MODIFIED` 7、`MISSING` 4、`AMBIGUOUS` 1、`EXTERNAL_DEPENDENCY` 6。逐项编号与机器可读计数见 `evidence/P1_official_code_manifest.json` 的 `classification_counts`。

注意：`ORIGINAL` 只表示"源码实现了论文该式"，不表示"数值与论文一致"。例如 #1 的 DQ 基元用 float32 + `-use_fast_math` 编译，#8 的投影用 float64 + $10^{-16}$ 阻尼，二者的可复现精度不同。

---

**补充（式 (38) 的代价口径）**：`get_abs_cost` 把 8 维对偶四元数差的 $L_1$ 与 3 维位置差的 $L_1$ 相加，位置因此被罚两次；示例 YAML 两项权重均为 100。论文式 (38) 只有一项。这是终端代价在实现层的额外整形，已记入 `P1_EQUATION_AUDIT.md` §6.0。

## 8. 与通用 MPPI 的差异（源码级）

| 维度 | 通用 MPPI 实现 | 本仓库 | 证据 |
|---|---|---|---|
| 采样 | `randn` 逐步独立 | 第一阶段 FFT 着色；第二阶段对数正态 | `common_ops.py:240-316` |
| 随机性 | 连续 RNG | **每周期重置 seed=0** | `common_ops.py:253,255,288,290` |
| 权重 | 全样本 softmax + 控制代价 | 第一阶段仅簇内；无控制代价 | `kmeans_adpan.py:328-332` |
| 均值 | 加权噪声 + 名义序列 | 同，但额外滑动平均 | `kmeans_adpan.py:332-334` |
| 多模态 | 无 | k-means + 精英众数 | `kmeans_adpan.py:299-327` |
| 约束 | 罚项 | 等式逐步投影 + 不等式软罚 | `mppi_project_step.h` |
| 温度 | 固定 λ | 调 λ 使权重和 ∈ [22,30]（簇内 [15,20]） | `common_ops.py:57-85` |
| 拒绝 | 可选 | 无显式拒绝；罚权 $e^{-1500/\lambda}$ 近似拒绝 | — |

**结论**：仓库实现的是"簇条件 MPPI + 零空间传播 + 辅助控制器"的复合体，结构上确实不是通用 MPPI；但它的**采样分布（两处）、停滞项、奇异项、终端代价、倾角实现、随机种子**与论文式子有 7 处可核实的偏差（§7 的 CODE_MODIFIED 行），参数集另有一组 `AMBIGUOUS`。因此"上游存在实现"只能证明**结构可运行**，不能证明**数值保真**。

---

## 9. 保真度结论

### 9.1 可以判定为"忠实"的部分

- 对偶四元数运动学与相对/绝对位姿的解析构造（除式 (8) 的排版问题）；
- 相对雅可比的解析列与 $8\times n$ 结构；
- 零空间投影的代数形式与限幅顺序；
- 两阶段的**控制流**：探索 → 聚类 → 选模 → 簇内聚合 → 精化 → 聚合；
- 辅助控制器、$L$ 指标、低层相对修正的公式结构；
- GPU 批处理的算子划分。

### 9.2 不能判定为"忠实"的部分

- 采样分布（频域/对数正态 vs 式 (20)(24) 的高斯）与随机性（每周期重置种子）；
- 停滞项函数形式；
- 奇异项的位置、层数与权重；
- 参数集（表 I vs 示例 YAML，8 项数值不一致，另有 λ 口径不同）；
- 动态障碍膨胀（缺失）；
- 高层频率（缺失）；
- 基线（main 缺失，pre 无文档）；
- 场景（T3–T6 缺失）。

### 9.3 对复现策略的直接含义

1. **不要以 `main` 为唯一参照**：它缺基线、缺场景、缺动态障碍逻辑。算法结构以 `main` 为准（可读性好），实验对照以 `pre` 为准（基线齐全）。
2. **不要以"跑通上游示例"作为复现成功**：示例只覆盖 Task 1/2，且参数与表 I 不同。
3. **不要把 `cuda_dq_kernel` 当 oracle**：它与控制器共享同一套约定（包括式 (8) 的读法），一致性不能证明正确性。独立 oracle 必须是 SE(3) 复合/有限差分/SVD。
4. **许可证**：不得复制上游源码入库；本地验证可以，但交付物只含自写实现与文档。
