# P1 公式审计（Equation Audit）

> 配套：`P1_PAPER_STUDY.md`、`P1_OFFICIAL_CODE_AUDIT.md`
> 论文：Zhu, Mao, Yang, Li, IEEE T-RO 42 (2026) 1942–1960，DOI `10.1109/TRO.2026.3686224`
> PDF SHA256：`8b4589ce07f932bf1294c7a39b30320a8791f630a4bcd2cd71782b3a2a56de3c`
> 源码快照：`dual_arm_gpu_mpc@fe5b49f7`、`cuda_dq_kernel@231f130e`（另审计接受到前快照 `1820a9e8` / `c762b7d6`）

本文件逐式记录：**假设、输入、输出、维度、源码落点、判定**。判定只用五种标签：

- `ORIGINAL` — 源码逐项实现论文式子；
- `CODE_MODIFIED` — 论文有式子，源码实现的是**不同但相关**的形式（必须记录差异）；
- `MISSING` — 论文有、源码没有；
- `AMBIGUOUS` — 论文自身或论文与代码之间无法唯一确定；
- `EXTERNAL_DEPENDENCY` — 依赖外部库/库函数（dqrobotics、cuRobo、kmeans_pytorch）。

---

## 1. 记号与维度总表

| 符号 | 含义 | 维度 | 出现 |
|---|---|---|---|
| $\Theta$ | 双臂关节位置 | $n=n_1+n_2$ | (12) |
| $u_k$ | 关节速度指令 | $n$ | (12) |
| $T_h$ | 预测离散步长 | 标量 | (12)(19) |
| $N$ | 预测步数 | 标量（15） | (19) |
| $M$ | 采样轨迹数 | 标量（1000） | (20)(23) |
| $K$ | 簇数 | 标量（6） | (22) |
| $m$ | 精英样本数（表 I 标为 “Candidate trajectory count”） | 标量（表 I：10；代码：3） | §V-4 |
| $x,x_r,x_a,l_a$ | 单位对偶四元数 | 8 个实参数（6 维流形） | (3)(7)(8)(9) |
| $\mathrm{vec}_8(\cdot)$ | 对偶四元数 → $\mathbb{R}^8$ | $8$ | (10)(11) |
| $J,J_r,J_a,J_l$ | 对偶四元数雅可比 | $8\times n$，秩 6 | (10)(11) |
| $N(S_i)$ | 零空间投影 | $n\times n$，秩 $n-6$ | (26)(27) |
| $D$ | 聚类特征 | $1+n$ | (52) |
| $U_s$ | 控制序列 | $N\times n$ | (19) |
| $L$ | 未探索度指标 | 标量 | (47)(48) |

**关键维度事实**：8 行的对偶四元数雅可比秩为 6，因为它映射到一个 6 维流形；这决定了 $J_rJ_r^\top\in\mathbb{R}^{8\times8}$ 必奇异，伪逆必须阻尼，零空间维数为 $n-6$。任何把 8 行当 8 个独立约束的实现都会得到错误的零空间。

---

## 2. 代数与表示（式 (1)–(9)）

| 式 | 内容 | 假设 | 输入 → 输出 | 维度 | 源码 | 判定 |
|---|---|---|---|---|---|---|
| (1) | 四元数集合定义 | 无 | — | 4 | `dq_common.cuh` 基础类型 | ORIGINAL |
| (2) | 对偶四元数集合 | $\epsilon^2=0$ | — | 8 | 同上 | ORIGINAL |
| (3) | $x=r+\epsilon\frac12 pr$ | 单位对偶四元数 | $(r,p)\to x$ | 8 | `dq_from_rt` 类构造；`dq_mult` 组合 | ORIGINAL |
| (4) | $r=a+bi+cj+dk$，单位约束 | $a^2+b^2+c^2+d^2=1$ | — | 4 | `dq_normalize_inline` | ORIGINAL |
| (5) | 轴角 → 四元数 | 单位轴 $n$ | $(\varphi,n)\to r$ | 4 | `dq_exp_inline`（螺旋形式） | ORIGINAL |
| (6) | 纯四元数平移 | — | $(x,y,z)\to p$ | 4 | `dq_translation` | ORIGINAL |
| (7) | $x_r=x_2^*x_1$ | 单位对偶四元数 | $(x_1,x_2)\to x_r$ | 8 | `rel_abs_pose_rel_jac_inline`：`conj(x2)⊗x1` | ORIGINAL |
| (8) | $x_a\triangleq x_2^*x_{r/2}$ | 「平均两个末端变换」 | $(x_2,x_r)\to x_a$ | 8 | 实为 $x_2\otimes\sqrt{x_r}$ | **AMBIGUOUS**（论文排版错误，见 §3.1） |
| (9) | $l_a=n_a+\epsilon(s_a\times n_a)$ | 直线过点 $s_a$、方向 $n_a$ | $(n_a,s_a)\to l_a$ | 8 | 未显式构造；只算方向夹角 | **CODE_MODIFIED**（矩缺失） |

### 2.1 式 (8) 的判定（重点）

**论文原文**（p.1945）："One practical approach to defining this is by averaging the transformations of the two end-effectors' poses, which can be mathematically expressed as $x_a\triangleq x_2^*x_{r/2}$."

**源码**（`dq_composite_ops.cuh:113-118`）：

```
dq_mult_inline(x_effector2_conj, x_effector1, rel_pose);   // x_r = x2* x1
dq_sqrt_inline(rel_pose, x_effector1_sqrt);               // s = sqrt(x_r)
dq_mult_inline(x_effector2, x_effector1_sqrt, abs_pose);  // x_a = x2 * s
```

**三条独立判据**：

1. **群中点**：$x_a^{-1}x_1=s$，$x_a^{-1}x_2=s^{-1}$，故 $x_a$ 到两末端等群距；字面式 (8) 不满足。
2. **基座无关**：$x_1s^{-1}=x_2x_rs^{-1}=x_2s=x_a$，交换"哪条臂是 2"不改变结果；字面式 (8) 会改变。
3. **正文语义**："averaging the transformations"。

**几何含义（必须写进复现文档）**：$x_a$ 是 **SE(3) 螺旋中点**，不是位置算术平均。独立 SE(3) 对数/指数核对：取 $R_1=R_z(0.9)$、$R_2=R_z(-0.4)$、$t_1=(0.5,0.2,0.1)$、$t_2=(-0.1,0.3,0.2)$，得 $t_a=(0.1832,0.1489,0.1500)$ m，算术平均 $(0.2,0.25,0.15)$ m，偏差 0.1025 m；纯平移时两者重合。因此**绝对位姿依赖相对旋转**，$C_{\text{goal}}$ 与辅助控制器都受影响。

**建议**：主实现用 $x_2\sqrt{x_r}$，并在所有报告中注明论文式 (8) 的星号为排版错误；不接受"按字面实现"作为 fidelity 的借口，因为字面式在几何上不是 workspace 位姿。

### 2.2 式 (9) 的判定

式 (9) 的矩 $s_a\times n_a$ 在源码中没有任何对应量：倾角只用方向。对式 (17) 的倾角约束，矩不影响夹角，故**功能等价**；但若下游要用"绝对直线"做位置相关约束（论文未做），则该式在代码中不存在。判定 `CODE_MODIFIED`，并注明"等价于只实现方向部分"。

---

## 3. 微分运动学（式 (10)(11)）

| 式 | 内容 | 假设 | 输入 → 输出 | 维度 | 源码 | 判定 |
|---|---|---|---|---|---|---|
| (10) | $\mathrm{vec}_8\dot x=J\dot\Theta$ | 串联链、DH/MDH 参数已知 | $(\Theta,\dot\Theta)\to \dot x$ | $8\times n$ | `dq_composite_ops.cuh` 解析列 | ORIGINAL |
| (11) | $\mathrm{vec}_8\dot x_r=J_r\dot\Theta$ 等 | 同上 | — | $8\times n$ | 同一 kernel 输出 `Jxr` | ORIGINAL |

### 3.1 $J_r$ 的完整推导（论文未给，复现必须补）

单个关节的变换 $A_k(q_k)$ 满足 $\partial A_k/\partial q_k=\frac12\zeta_kA_k$，$\zeta_k$ 为该关节螺旋轴在当前系下的对偶四元数。于是串联链第 $k$ 列

```
j_k = (1/2) z_k x,     z_k = b A_1 ... A_{k-1} ζ_k A_{k-1}^{-1} ... b^{-1}
```

（代码：`Ad_inline(x1,w,z1); z1*=0.5; dq_mult_inline(z1,x_effector1,j1)`，`dq_composite_ops.cuh:87-96`。）

对 $x_r=x_2^*x_1$：

```
d/dt(x_2*) = C_8 ẋ_2,   C_8 = diag(1,-1,-1,-1,1,-1,-1,-1)
J_r = [ H_+(x_2*) J_1 ,  H_-(x_1) C_8 J_2 ]     ∈ R^{8×(n1+n2)}
```

代码 `Jxr1_temp = H_+(x_2^*) J_1`、`Jxr2_temp = H_-(x_1) C_8 J_2`（`dq_composite_ops.cuh:120-127`）与此逐项一致。**秩**：$\mathrm{rank}(J_r)=6$（一般位形），因为 $x_r$ 的 8 个分量受两个单位约束。

**验收含义**：任何复现实现都必须能用中心差分把 $J_r$ 打到 $O(h^2)$ 误差；这是模块 A 的核心 oracle。若只比较与 `dqrobotics` 的一致性，会把"两个实现共享同一个约定错误"误判为正确。

---

## 4. 系统模型与约束（式 (12)–(18)(29)）

| 式 | 内容 | 假设 | 输入 → 输出 | 维度 | 源码 | 判定 |
|---|---|---|---|---|---|---|
| (12) | $\Theta_{k+1}=\Theta_k+T_hu_k$ | 速度控制、Euler 积分 | $(\Theta_k,u_k)\to\Theta_{k+1}$ | $n$ | `mppi_project_step` 内积分 | ORIGINAL |
| (12) | $\ddot\Theta_k=(u_k-u_{k-1})/T_h$ | 后向差分 | — | $n$ | `get_acc_cost` 用 $\Delta u$，**未除 $T_h$** | **CODE_MODIFIED** |
| (13)–(15) | 关节位置/速度/加速度箱约束 | 箱式、时不变 | — | $n$ | 位置/速度：核内截断；加速度：Python 侧截断 | ORIGINAL |
| (16) | $x_{r,k}=x_{r,d}$ | 刚性抓取 | — | 6 | 由 (29) 的微分形式实现 | ORIGINAL |
| (29) | $J_r\dot\Theta=0$ | 同上 | — | 8（秩 6） | 零空间投影 | ORIGINAL |
| (17) | $\vartheta_{\min}\le\vartheta_k\le\vartheta_{\max}$ | 倾角可测 | — | 1 | 软罚项 (32) | CODE_MODIFIED（软约束） |
| (18) | $d_{k,ij}\ge d_{\min}$ | 球近似 | — | 1/对 | 软罚项 (33)(34) | CODE_MODIFIED（软约束） |

**式 (12) 的加速度**：论文定义为 $(u_k-u_{k-1})/T_h$；代码 `get_acc_cost` 直接对相邻速度差取 $L_1$ 加权（`common_ops.py:191-204`），**没有除以 $T_h$**。由于表 I 中 $p_a=0$、示例 YAML 中 `q_acc_weight=0`，该差异在当前配置下不影响结果；但一旦启用加速度代价，量纲会差 $1/T_h\approx6.67$ 倍。判定 `CODE_MODIFIED`。

**约束的硬/软**：式 (13)–(15) 通过截断是**硬**的（在采样传播内）；式 (16)(29) 通过投影是**结构硬**的（一阶）；式 (17)(18) 通过罚项是**软**的。论文行文把三类都称为"约束满足"，复现报告必须分开表述。

---

## 5. 采样与两阶段优化（式 (19)–(24)(52)）

| 式 | 内容 | 假设 | 输入 → 输出 | 维度 | 源码 | 判定 |
|---|---|---|---|---|---|---|
| (19) | $S_N=f(T_h,S_0,U_s)$ | 确定性 rollout | $(S_0,U_s)\to S_N$ | $N\times n$ | 逐步 `rel_abs_pose_rel_jac` | ORIGINAL |
| (20) | $U_{s,i}\sim\mathcal N(U_s^{*,\text{last}},\Sigma_{\exp})$ | 高斯、轨迹级协方差 | $\to\{U_{s,i}\}_{i=1}^M$ | $M\times N\times n$ | `epsilon_generator_colored`（频域） | **CODE_MODIFIED** |
| (21) | $C_{\exp}=C_{\text{std}}+C_{\text{stay}}$ | 两层代价 | — | 标量 | `stage_cost` + 停滞项 | ORIGINAL |
| (22) | k-means 目标 | 欧氏距离、$K$ 固定 | $\{D_i\}\to\{\alpha_k\}$ | $K\times(1+n)$ | `kmeans_pytorch.kmeans` | EXTERNAL_DEPENDENCY |
| (23) | 簇内加权聚合 | 权重指数、簇内归一化 | $\to U_s^{*,\exp}$ | $N\times n$ | `compute_weights_k` + `current=w+last` | ORIGINAL |
| (24) | 第二阶段采样与聚合 | 小方差、全样本 | $\to U_s^{*,\text{new}}$ | $N\times n$ | `epsilon_generator_log` + `compute_weights` | **CODE_MODIFIED** |
| (52) | $D=[C_{\exp},[\Theta_0-\Theta_N]^\top]$ | 特征可归一化 | $\to D$ | $1+n$ | 三块逐列归一化后拼接 | ORIGINAL（归一化未记载） |

### 5.1 式 (20) 与源码：三种不同的"Σ"

论文式 (20) 写 $U_{s,i}\sim\mathcal N(U_s^{*,\text{last}},\Sigma_{\exp})$，其中 $\Sigma_{\exp}$ 按记号是**轨迹级协方差矩阵**（$Nn\times Nn$，含时序相关）。但：

- 表 I 把 $\Sigma_{\exp},\Sigma_{\text{std}}$ 写成 "3.0, 0.6"，是标量；
- §VII-D 称"sampling variances"，又说"$\Sigma_{\exp}$ typically set to 2–3 in normalized action units"；
- 代码 `config.std=3.0`，在 `epsilon_generator_colored` 里作为**逐元素标准差**使用（`common_ops.py:299`：`variance = (f^{-γ}) std² / ζ`）。

所以同一个符号在三处分别是：协方差矩阵、方差、标准差。复现口径应固定为**标量标准差 + 指定谱形**，并在报告中写明"不是式 (20) 的轨迹协方差"。

### 5.2 式 (23) 的两种等价写法

论文：$U^{*,\exp}=\sum w_iU_{s,i}/\sum w_i$（绝对序列加权）。
代码：`w_epsilon = Σ w_i ε_i`，`current = w_epsilon + last_mppi_result`（噪声加权再叠加均值）。
因 $U_{s,i}=\text{last}+\epsilon_i$ 且 $\sum w_i=1$，两式恒等。**但代码多了一步**：`moving_average_filter(w_epsilon, window=mppi_T)`（`kmeans_adpan.py:332-333`），即对加权噪声再做窗长 $T$ 的滑动平均。这一步不在论文任何式子中，会额外平滑指令。判定：式 (23) 本身 `ORIGINAL`，但整条聚合链 `CODE_MODIFIED`。

### 5.3 式 (24) 与源码：对数正态混合的"两次同种子"

论文式 (24) 写 $\Delta U\sim\mathcal N(0,\Sigma_{\text{std}})$；§VII-A 说第二阶段用"normal log-normal mixed distribution [46]"。代码：

```
torch.manual_seed(seed); data = randn(...)                     # ξ
torch.manual_seed(seed); log_normal_data = exp(randn(...)*log_std)  # 同一颗种子 → 同一组 ξ
combined = data * log_normal_data * std + mean
```

**两次 `manual_seed` 相同**，故实际采样是 $X\cdot e^{\sigma X}$（$X\sim\mathcal N(0,1)$），而不是 $X\cdot e^{\sigma Y}$（$X,Y$ 独立）。这与 [46] 的"log-normal mixture"分布不同：分布的偏度、尾部都变了。同样的问题出现在第一阶段：$T=15$ 为奇数，实部与虚部用同一颗种子各抽一次，导致复谱是 $(a+ia)$ 而非独立实虚部（`common_ops.py:288-295`）。判定：`CODE_MODIFIED`，且属于**会影响探索行为**的实现细节，不是纯工程噪声。

**每周期重置种子**：两个生成器开头都 `torch.manual_seed(self.mppi_seed)`，而 `mppi_seed=0` 固定。因此每个控制周期的噪声样本集合完全相同（只是加了新的均值）。这使"随机采样"变成**确定性周期采样**，与论文的随机 MPC 语义不同，也会影响抖动统计。复现时若要逐字对照代码，必须保留；若要对照论文，应改成连续 RNG 流（标 [DEVIATION]）。

### 5.4 式 (52) 的特征与 k-means

论文特征为 $[C_{\exp},(\Theta_0-\Theta_N)^\top]$，维度 $1+n$。代码把三块分别 min-max 归一化到 $[0,1]$ 后拼接（`kmeans_adpan.py:268-300`），且 `stage_cost` 已经包含停滞项（因为停滞项在拼接前已加进 `stage_cost`）。判定：内容一致，归一化是必要的工程处理（否则代价的量级会淹没关节变化），但论文未记载，复现时应作为显式参数记录。

---

## 6. 代价函数（式 (32)–(43)）

| 式 | 内容 | 假设 | 维度 | 源码 | 判定 |
|---|---|---|---|---|---|
| (32) | 倾角指示罚 | 倾角可计算 | 标量/步 | `get_tilt_constraint_cost` | ORIGINAL |
| (33) | 外部碰撞指示罚 | 球近似、距离可查 | 标量/步 | `get_collision_cost`（curobo，二值化） | ORIGINAL（实现依赖外部库） |
| (34)(35) | 自碰撞指示罚 | 安全对集合 $S$ | 标量/步 | 同上（curobo self-collision） | ORIGINAL |
| (36) | $w=\sqrt{\prod_{i=1}^6\sigma_i}$ | $\sigma_i$ 为 $J_rJ_r^\top$ 非零特征值 | 标量 | `manipulability_*_pdet` | ORIGINAL（metric 等价） |
| (37) | $C_{\text{sing}}=p_e/\max(\zeta,w)$ | 同上 | 标量 | `_terminal_manip_cost`：$0.5/\mathrm{clamp}(w)$ | **CODE_MODIFIED**（位置/权重/层数不同） |
| (38) | $C_{\text{goal}}=p_g\|\mathrm{vec}_8(x_{a,N}-x_{a,d})\|_1$ | 终端、$L_1$ | 标量 | `get_abs_cost`（终端权重 100） | ORIGINAL（但见 A2） |
| (39) | $C_{\text{vel}}=p_v\|\dot\Theta\|_1$ | 逐步 | 标量 | `get_vel_cost`（权重 0） | ORIGINAL |
| (40) | $C_{\text{acc}}=p_a\|\ddot\Theta\|_1$ | 逐步 | 标量 | `get_acc_cost`（$\Delta u$，权重 0） | CODE_MODIFIED |
| (41) | $C_{\text{std}}$ 汇总 | 七项 | 标量 | `stage_cost`（第二阶段） | ORIGINAL |
| (42) | $C_{\text{stay}}=p_sC_{\text{goal}}/\max(\zeta,\|\Theta_0-\Theta_N\|_1)$ | 反停滞 | 标量 | $C_{\text{goal}}/(p_s\cdot\mathrm{clamp}(\|\Delta\Theta\|_2^2,10^{-3}))$ | **CODE_MODIFIED**（$p_s$ 位置、范数、$\zeta$ 全部不同） |
| (43) | $C_{\exp}=C_{\text{std}}+C_{\text{stay}}$ | — | 标量 | `stage_cost += abs_terminal + abs_terminal/stagnation` | ORIGINAL（结构） |

### 6.0 式 (38) 的实现细节（位置被罚两次）

`get_abs_cost(desire_abs_pos, abs_pos, desire_abs_position, abs_position, w_rot, w_pos)` 返回

```
w_rot * ||vec8(x_a,d - x_a)||_1  +  w_pos * ||p_d - p||_1
```

其中第二项是 3 维欧氏位置。**平移同时出现在 8 维对偶四元数差与 3 维位置差中**，即位置被罚两次；示例 YAML 的两项权重都为 100，等价于把位置项相对旋转放大。论文式 (38) 只有 $p_g\|\mathrm{vec}_8(x_{a,N}-x_{a,d})\|_1$ 一项。判定：结构 `ORIGINAL`，数值口径 `CODE_MODIFIED`；复现时要么按论文单一项，要么显式记录双项权重。

### 6.1 式 (36)(37) 的判定细节

- **metric**：$J_rJ_r^\top$ 的特征值 $\sigma_i=s_i^2$，故 $w=\prod_{i=1}^6s_i$ = 吉川可操作度。代码 `pdet` 对 6×N 的 twist 雅可比取 6 个奇异值之积（`manipulability.py:290-312`），**数值上等价**；差别在秩亏时：论文规定 $w=0$，代码把奇异值 clamp 到 $\epsilon=10^{-12}$，返回 $\epsilon^6$ 而非精确 0。
- **位置**：论文把 $C_{\text{sing}}$ 放进 $C_{\text{std}}$（式 (41)），即**每个预测步**都罚；代码只在第二阶段**终端**加一次（`kmeans_adpan.py:413-416`），第一阶段完全不含奇异项。
- **权重**：表 I $p_e=10$；代码 `manip_weight=0.5`（默认值，示例 YAML 未覆盖）。
- **结论**：三者叠加使"奇异规避"在代码中远弱于论文。若复现目标是论文行为，必须按式 (41) 逐 step 实现，并把代码版作为对照。

### 6.2 式 (42) 的量纲问题

论文 $p_s\cdot C_{\text{goal}}/\|\Delta\Theta\|$：$p_s$ 无量纲，$C_{\text{goal}}$ 是混合量纲的 $L_1$，$\Delta\Theta$ 是弧度。
代码 $C_{\text{goal}}/(p_s\cdot\|\Delta\Theta\|_2^2)$：$p_s$ 进入分母，且用平方范数。
把两式写成同一轨迹上的比值：论文 $T_p=0.125\,C/\|\Delta\Theta\|_1$，代码 $T_c=C/(10\,\|\Delta\Theta\|_2^2)$，故

```
T_c / T_p = 0.8 / ||ΔΘ||
```

在 $\|\Delta\Theta\|\sim0.1$ rad 时 $T_c\approx8T_p$（代码惩罚更强）；在 $\|\Delta\Theta\|\sim1$ rad 时 $T_c\approx0.8T_p$。**两者没有固定比例，且随位移量反向变化**——这不是“参数微调”，是函数形式与参数位置都不同。

---

## 7. 零空间与状态更新（式 (26)–(31)）

| 式 | 内容 | 假设 | 维度 | 源码 | 判定 |
|---|---|---|---|---|---|
| (25) | $S_N=f(T_h,S_0,U_s^{null})$ | 投影后 rollout | — | 同 (19) | ORIGINAL |
| (26) | $u^{null,temp}=N(S_i)u_i$ | $N$ 由当前预测状态构造 | $n$ | `mppi_project_step` | ORIGINAL |
| (27) | $N=I-J_c^\dagger J_c$ | 伪逆存在（阻尼） | $n\times n$ | $J^\top(JJ^\top+10^{-16}I)^{-1}$，float64 | ORIGINAL（正则化） |
| (28) | $u^{null}=g(T_h,u^{null,temp},S_i)$ | 位置/速度/加速度限幅 | $n$ | 核内速度+位置；Python 加速度 | CODE_MODIFIED（加速度不在 $g$ 内） |
| (29) | $J_r\dot\Theta=0$ | 刚性抓取 | 8（秩 6） | 投影的动机 | ORIGINAL |
| (30) | $\dot\Theta=N_ru$ | 辅助控制 | $n$ | `traditional_control_result` | ORIGINAL |
| (31) | $\Theta_{i+1}=\Theta_i+T_hu_i^{null}$ | Euler | $n$ | 核内积分 | ORIGINAL |

**残差阶数（复现的核心验收点）**：

```
x_r(Θ + T_h N u) = x_r(Θ) + T_h J_r N u + (T_h²/2) ẍ_r + O(T_h³)
                 = x_r(Θ) + O(T_h²)
```

因为 $J_rN=0$ 只在当前线性化点成立。故"每步投影"给出的是 $O(T_h^2)$ 的单步残差，$N$ 步累积 $O(NT_h^2)$；论文"enforced exactly"应理解为连续时间意义。模块 B 的接受准则就是测这个残差随 $T_h$ 的斜率（应为 2），以及投影/非投影的残差比（应 ≥ $10^6$）。

**Remark 2 的秩条件**：论文写"约束数不得超过自由度"。严格的退化条件是 $\mathrm{rank}(J_c)=n$，不是"行数 > n"。8 行约束、$n=12$ 时 $N$ 仍有 6 维零空间。复现的负对照应构造 $\mathrm{rank}=n$ 的增广约束（例如把 12 个独立任务行都加入），验证 $N\to0$。

---

## 8. 辅助控制与切换（式 (44)–(51)）

| 式 | 内容 | 假设 | 维度 | 源码 | 判定 |
|---|---|---|---|---|---|
| (44) | $u_a=J_a^\dagger K_ae_a$ | 绝对位姿可微 | $n$ | `traditional_control_result`：阻尼伪逆 | ORIGINAL |
| (45) | $u_t=N_ru_a$ | 相对零空间 | $n$ | $(I-J_r^+J_r)u_a$ | ORIGINAL |
| (46) | $\Theta_{i+1}=\Theta_i+T_hu_{t,i}$ | 多步开环 | $n$ | 循环 $N$ 步 | ORIGINAL |
| (47) | $L_{k+1}=L_k+T_h(C_{k,t}/C_{k,s}-\eta)$ | $C_s>0$ | 标量 | `update_c`：$T_h=\texttt{mppi\_dt}$ | ORIGINAL |
| (48) | $L$ 饱和 | $L_{\min}<0<L_{\max}$ | 标量 | `max(-0.05,min(c,0.4))` 硬编码 | ORIGINAL（值硬编码） |
| (49) | $u_h=u_s$ if $L\ge0$ else $u_t$ | 二值切换 | $n$ | `if flag: u0=p_u0 else: mppi_u0` | ORIGINAL |
| (50) | $u_r=J_r^\dagger K_re_r$ | 低层、漂移修正 | $n$ | `relative.py:69-79` | ORIGINAL |
| (51) | $u_l=u_r+N_ru_h$ | 两级层次 | $n$ | `relative.py:80-93` | ORIGINAL |

**两个实现差异**：

1. **$C_s$ 取的是第一阶段的 `min_energy`，不是第二阶段最终序列的代价**（`base.py:364-370`：`_, mppi_energy = self.mppi_worker()`，随后 `mppi_u, _ = self.mppi_worker2()`）。论文式 (47) 的 $C_{k,s}$ 应是"采样控制器最终策略的代价"。判定 `CODE_MODIFIED`。影响：$L$ 的积分用了偏乐观（或偏悲观）的代价比，会改变切换时刻。
2. **$L$ 的饱和界硬编码**（-0.05/0.4），而表 I 也给出同值；一致，但不可配置。

**切换不对称的机制**（论文 p.1952 的说法不准确）：不对称来自 $|L_{\min}|\ll L_{\max}$。以 $\eta=0.4$、比值偏离 0.1 为例，从 $L_{\max}=0.4$ 降到 0 需 4 s，从 $L_{\min}=-0.05$ 升到 0 需 0.5 s，正好 8 倍。复现应把它作为可测现象（切换停留时间比 ≈ $L_{\max}/|L_{\min}|$），而不是引用"smaller threshold"。

---

## 9. 论文与源码的口径冲突清单

| 编号 | 冲突 | 论文 | 源码 | 判定 |
|---|---|---|---|---|
| A1 | 绝对位姿 | $x_2^*x_{r/2}$ | $x_2\sqrt{x_r}$ | AMBIGUOUS（论文排版错） |
| A2 | 误差度量 | $\mathrm{vec}_8$ 差 + $L_1$ | 同（逐分量） | AMBIGUOUS（缺 $\mathrm{vec}_8$ 定义、量纲混合） |
| A3 | 采样分布 | 高斯 (20)(24) | 频域 / 对数正态 | CODE_MODIFIED |
| A4 | $\Sigma$ 语义 | 协方差/方差/标准差混用 | 标量 std | AMBIGUOUS |
| A5 | 停滞项 | $p_s$ 分子、$L_1$ | $p_s$ 分母、平方 $L_2$ | CODE_MODIFIED |
| A6 | 奇异项 | 逐 step、两层、$p_e=10$ | 终端、仅第二阶段、0.5 | CODE_MODIFIED |
| A7 | 参数表 | 表 I | 示例 YAML 不同 | AMBIGUOUS（见 §10） |
| A8 | 加速度 | $(u_k-u_{k-1})/T_h$ | $\Delta u$（未除 $T_h$） | CODE_MODIFIED |
| A9 | 控制频率 | 30 Hz / 125 Hz | 无节流 / 125 Hz | MISSING（高层节流） |
| A10 | 动态障碍膨胀 | 按速度膨胀 | `pass` | MISSING |
| A11 | 每周期种子 | 随机采样 | 每周期重置种子 | CODE_MODIFIED |
| A12 | 对数正态 | $X e^{\sigma Y}$ | $X e^{\sigma X}$（同种子） | CODE_MODIFIED |

---

## 10. 表 I 与示例 YAML 的逐项对照

| 参数 | 表 I | `examples/sim1_ur/ur3_and_ur3e.yaml` | 差异 |
|---|---|---|---|
| $\Sigma_{\exp},\Sigma_{\text{std}}$ | 3.0, 0.6 | `std: 3.0`, `an_std: 1.0` | $\Sigma_{\text{std}}$ 0.6 vs 1.0 |
| $\lambda_{\exp},\lambda_{\text{std}}$ | adaptive | `param_lambda=0.5` + 目标和 [22,30]/[15,20] | 口径不同 |
| $M$ | 1000 | `batch_size: 1000` | 一致 |
| $T_h$ | 0.15 | `mppi_dt: 0.15` | 一致 |
| $N$ | 15 | `mppi_T: 15` | 一致 |
| $K$ | 6 | `num_clusters: 6` | 一致 |
| $m$ | 10（表 I 标为 “Candidate trajectory count”，§V-4 用作精英数） | `common_num: 3` | **不一致** |
| $\vartheta_{\min},\vartheta_{\max}$ | −8, 8 | `max_abs_tilt_angle: 8.0`（对称） | 一致 |
| $p_{ec},p_{sc}$ | 1500 | `collision_constraint_weight: 1500` | 一致 |
| $p_a,p_v$ | 0 | `q_acc_weight: 0`, `q_vel_weight: 0` | 一致 |
| $p_g$（表 I 记作 $p_q$） | 100 | `terminal_abs_weight: 100`, `terminal_abs_position_weight: 100` | 数值一致，符号不一致（$p_q$ vs $p_g$） |
| $p_t,p_e$ | 1500, 10 | `tilt_constraint_weight: 1500`；`manip_weight: 0.5` | $p_e$ **不一致** |
| $p_s$ | 0.125 | `stagnation_weight: 10` | **不一致**（且函数形式不同） |
| $\delta_e,\delta_s$ | 0 | `min_collision_distance: 0`, `min_self_collision_distance: 0` | 一致 |
| $L_{\max},L_{\min}$ | 0.4, −0.05 | `c_abs_max: 0.4`；$-0.05$ 硬编码 | 一致 |
| $\eta$ | 0.1 | `c_eta: 0.4` | **不一致** |
| $T_l$ | 0.004 | `ros_update_rate: 125` → 0.008 | **不一致** |
| $K_r$ | 0.5 | `high_rel_gain: 0.02` | **不一致** |
| $K_a$ | 0.5 | `high_abs_gain: 2.0` | **不一致** |

**结论**：表 I 不是示例 YAML 的摘要，二者是两个不同的参数集。复现必须建立**双基线**（paper-faithful / code-faithful），并把"用哪一套"作为显式实验因子，否则任何数值对比都不可解释。

---

## 11. 公式→源码总索引

| 组件 | 论文 | 源码文件:行 | 判定 |
|---|---|---|---|
| DQ 基元（乘/共轭/逆/exp/log/sqrt） | (1)–(6) | `cuda_dq_kernel/src/native/include/dq_torch/device/dq_primitives.cuh` | ORIGINAL |
| DH/MDH 正运动学 | (10) | `.../dq_composite_ops.cuh:44-85` | ORIGINAL |
| 相对位姿 | (7) | 同上 `:113-116` | ORIGINAL |
| 绝对位姿 | (8) | 同上 `:114-118` | AMBIGUOUS |
| 相对雅可比 | (11) | 同上 `:120-127` | ORIGINAL |
| 倾角 | (9)(17)(32) | 同上 `:130-135`；`common_ops.py:182-187` | CODE_MODIFIED |
| 零空间投影 | (26)(27)(31) | `cuda_dq_kernel/src/native/host_ops/mppi_project_step.h:20-100` | ORIGINAL |
| 第一阶段采样 | (20) | `common_ops.py:266-316` | CODE_MODIFIED |
| 第二阶段采样 | (24) | `common_ops.py:240-263` | CODE_MODIFIED |
| 停滞项 | (42) | `kmeans_adpan.py:259-265` | CODE_MODIFIED |
| 聚类 | (22)(52) | `kmeans_adpan.py:268-306` | ORIGINAL |
| 选模 | §V-4 | `kmeans_adpan.py:307-327` | ORIGINAL |
| 簇内聚合 | (23) | `kmeans_adpan.py:328-336`；`common_ops.py:72-85` | ORIGINAL |
| 第二阶段聚合 | (24) | `kmeans_adpan.py:417-426`；`common_ops.py:56-69` | ORIGINAL |
| 奇异项 | (36)(37) | `kmeans_adpan.py:413-416,429-439`；`manipulability.py:109-130` | CODE_MODIFIED |
| 辅助控制 | (44)–(46) | `kmeans_adpan.py:441-487` | ORIGINAL |
| $L$ 指标 | (47)–(49) | `base.py:318-325,360-384` | ORIGINAL（$C_s$ 取 stage-1） |
| 低层 | (50)(51) | `controllers/low_level/relative.py:69-93` | ORIGINAL |
| 动态障碍膨胀 | §VII-C | `base.py:256-257`（`pass`） | MISSING |
