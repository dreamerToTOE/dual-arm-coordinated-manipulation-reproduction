# P2 42维右扰动 IESEKF 解析设计草案

2026-10-14；阶段基线 `834bcc372717a3b4ffbd0bd6ef7262b3b58237bf`。

当前状态：**估计器未实现、资格未执行，PASS未获。** `baselines/p2_pose_force/estimator.py` 不存在；下文是接口契约、解析推导和资格计划，不是已运行的算法。独立动力学首轮在壁钟上限内未完成固定5秒settle，见[原始动力学summary](../results/20261014_P2_stage2_dynamics01/summary.json)。我据此停止估计器及等价快速计算核的实现/运行，不用GT、普通EKF或解析力衰减替代后续视觉触觉闭环。

原先先行声明的测试，已原字节移出可执行测试目录，保存为 [P2_STAGE2_ESTIMATOR_QUALIFICATION_PLAN.py](P2_STAGE2_ESTIMATOR_QUALIFICATION_PLAN.py)，SHA256 `c7e38ba1c5ae892078046c3bf07f6e201a6a562ce3d8f3eea94252e30d49eb14`。它引用未来估计器接口，只是不能直接运行的设计草案；以后实现并获准进入资格时再迁回tests。移动未提交草案是交付组织，不是科学算法修正；未执行测试或微基准。

## 1. 论文与固定接口

依据原文式(14)/(16)–(18)和[冻结JSON](../configs/p2_closed_loop_protocol_v1.json)，状态切空间严格排列为

\[
\delta x=(\delta O,\delta V,\delta E_1,\delta E_2,
\delta C,\delta G_1,\delta G_2)\in\mathbb R^{42}.
\tag{E1}
\]

| 块 | 切空间索引（Python） | 约定 |
|---|---|---|
| O | 0:6 | 物体COM到共同b1，右SE(3)扰动 |
| V | 6:12 | 物体body twist，欧氏加法 |
| E1 | 12:18 | EE1到原生b1，右扰动 |
| E2 | 18:24 | EE2到原生b2，右扰动 |
| C | 24:30 | b1坐标到b2，右扰动 |
| G1 | 30:36 | 抓点1到物体，右扰动 |
| G2 | 36:42 | 抓点2到物体，右扰动 |

规划中的 `FilterState` 与 [mechanics.State](../baselines/p2_pose_force/mechanics.py) 使用相同字段 `O,V,E1,E2,C,G1,G2`。初始输入及每个可变数组必须独立复制，禁止与plant共享可变状态。pose更新为 `T <- T Exp(delta)`，V为欧氏加；`state.local(reference)` 返回各 `Log(inv(reference.pose) state.pose)` 及V差。供几何计算的共同EE为 `E1_common=E1`、`E2_common=C^-1 E2`；存储和式(17)EE观测仍使用原生base。

拟定接口如下，尚未实现：

| 接口 | 输入及输出职责 |
|---|---|
| `FilterState.from_mechanics(state)` | 复制相同坐标契约，不能在主初始化中接收真实plant作为观测替代 |
| `RightIESEKF.from_protocol(state,config,physics,modes,initial_time)` | 按冻结P0/Q/收敛量构建独立42维估计器；physics使用条件对应的observer K |
| `predict(delta,U_published)` | 只使用旧的、已发布且经H选择的held body command；返回预测F与过程协方差等记录 |
| `update(observations)` | 在实际sample时间戳消费一份全新观测packet，内层共用同一prior，最终更新P一次 |
| `Observation` | kind、value、covariance、sample_id、sample_stamp、delivery_stamp；pose4×4或弹性wrench6维 |
| `measurement_prediction/jacobian` | 六类式(17)观测及局部右扰动Jacobian，允许新观测子集改变总维数 |
| `prediction_linearization/right_reset_jacobian` | 离散式(18)的F与噪声映射、注入后的协方差切空间变换 |

六类观测为 `EE1/EE2/hK1/hK2/visual1/visual2`，没有GT输入类型。预标定75对视觉、真实重力settle、t=0新观测初始化仍按冻结顺序；C不得取trueC，触觉只含hK，不包含hB。状态初始V为0、G为声明几何，不预填真值接触力。

算法参考为原论文参考文献[18]的[作者IKFoM工具](https://github.com/hku-mars/IKFoM)，冻结候选commit为 `59cfc095ca74425f9b330c7c04a5d74f68c6dd62`。计划采用独立核验的右SE(3)IESEKF，不能把只用SO(3)和世界平移的框架直接冒充原SE(3)模型。本轮没有复制作者源码、连接工具或取得框架等价资格。

## 2. 相对pose与测量解析Jacobian

记 `J_D,r` 将42维右扰动映射为D的右扰动。由原式(8)，

\[
D_1=E_1^{-1}OG_1,\qquad D_2=E_2^{-1}COG_2,
\]

\[
\xi_{D,1}=\Ad_{G_1^{-1}}\delta O
-\Ad_{D_1^{-1}}\delta E_1+\delta G_1,
\tag{E2}
\]

\[
\xi_{D,2}=\Ad_{G_2^{-1}}\delta O
-\Ad_{D_2^{-1}}\delta E_2
+\Ad_{(OG_2)^{-1}}\delta C+\delta G_2.
\tag{E3}
\]

因此弹性观测的欧氏微分为

\[
\delta h_{K,r}=-K_rJ_r(\tau_r)^{-1}\xi_{D,r},
\qquad \tau_r=\Log D_r.
\tag{E4}
\]

EE pose的测量右扰动分别选择对应E块。camera1输出O，其右扰动为 `δO`；camera2输出 `CO`，其右扰动为

\[
\xi_{visual2}=\delta O+\Ad_{O^{-1}}\delta C.
\tag{E5}
\]

以上是预测观测本身的局部Jacobian，不是直接拿Euler角/世界平移相减所得的导数。独立中央差分的eps=1e−6与冻结 `Jacobian_atol=1e−7` 是后续资格需要遵守的原判据；当前未执行，未取得资格。

计划草案提出将弹性测量的双方Jacobian行除以固定K，转回Log-strain单位检查链导数，并另查原始有符号hK是否与mechanics一致。**这是尚待单位解释审核的候选诊断，不能称为等效沿用冻结Jacobian绝对容差。** 若归一化后以1e−7判定，则第i行的物理Jacobian绝对误差实际上可达到 `K_i×1e−7`，对高刚度force行明显放大了原数值门；原始hK数值一致也不能替代其未归一化导数资格。

后续运行前须先逐块报告未归一化物理Jacobian及其中央差分误差，标清输出和输入单位：force对pose平移/旋转分别为N/m、N/rad，moment对应为Nm/m、Nm/rad；其他状态块按各自实际单位标记，包括理论零导数块。未经另行批准，不得用除K或其他归一化门替代原1e−7判据，不得只保存归一化误差而隐藏物理误差。若浮点差分不能满足原门，记录资格未获并提出具体单位/数值问题，不在结果后自行换门。原PLAN文件保持原字节作为未运行草案，不能直接迁回tests便宣称该尺度已获批准。

## 3. 完整动力学解析Jacobian策略

名义预测仍须使用原式(16)与已批准G演化，不用plant的Lie中点替代observer的式(18)右Euler均值。在线不能每个tick执行42维中央差分；中央差分只作资格oracle。

### 3.1 接触与外部wrench

令 `q=Ad(G^-1)V`、`Rbar=diag(R_D,R_D)`，则原式(10)的输入为 `v_rel=Rbar q−U`。局部微分为

\[
\delta q=\operatorname{ad}(q)\delta G+\Ad_{G^{-1}}\delta V,
\tag{E6}
\]

\[
\delta v_{rel}=\bar R\,\delta q+
\begin{bmatrix}-R_D[q_v]_\times\\-R_D[q_\omega]_\times\end{bmatrix}
\xi_{D,\omega},\qquad
\delta h=-KJ_r^{-1}\xi_D-B\,\delta v_{rel}.
\tag{E7}
\]

输入U在对状态求导时固定，是已发布命令历史，不是同次迭代重新计算的控制器输出。

对每侧令 `T=E_common^-1 O`、`P_h=H^T H`，物体系贡献为 `y=Ad(T)^T P_h h`。其微分是

\[
\delta y=\mathcal C(y)\xi_T+\Ad_T^\top P_h\delta h,
\qquad
\mathcal C(y)=
\begin{bmatrix}0&[f_y]_\times\\[f_y]_\times&[m_y]_\times\end{bmatrix}.
\tag{E8}
\]

这里wrench作用点与原式(12)一致。对第一侧，`ξ_T1=δO−Ad(T1^-1)δE1`；第二侧为

\[
\xi_{T,2}=\delta O-\Ad_{T_2^{-1}}\delta E_2
+\Ad_{O^{-1}}\delta C.
\tag{E9}
\]

两侧求和得到外部wrench的Jacobian，无需对W伪逆求导：式(16)只依赖外部wrench，内部力投影属于后续控制器，不进入f本身。

### 3.2 刚体项

令 `M` 为固定COM惯量、`C_V=[[ω×,0],[v×,ω×]]=−ad(V)^T`。Coriolis项的微分满足

\[
\delta(C_VM V)
=\left(C_VM-\mathcal C(MV)\right)\delta V.
\tag{E10}
\]

重力项的body线性部分为 `g_o=R_O^T g`，其pose微分为 `δg_o=[g_o]× δθ_O`。于是由(E8)–(E10)及原Ba可直接形成加速度的全42维解析导数；质量、惯量、重力和K/B仍取冻结值，exp4只改变observer K。

### 3.3 已批准抓点更新的隐式微分

采用[已批准接触推导](P2_CONTACT_GEOMETRY_DERIVATION.md)，记

\[
L=J_r(\tau)^{-1},\quad z=\Ad_{D^{-1}}U,
\quad a=q-z,\quad N_g=\Ad_{D^{-1}}N_e,
\quad A=N_e^\top L N_g,
\quad V_G=N_g\zeta.
\]

固定模式下N_e不随估计迭代改变。有

\[
\delta\tau=L\xi_D,\qquad
\delta a=\delta q-\operatorname{ad}(z)\xi_D,
\qquad \delta N_g\,\zeta=\operatorname{ad}(V_G)\xi_D.
\tag{E11}
\]

由 `N_e^T L(a+V_G)=0` 隐式微分，得到

\[
\delta V_G=\operatorname{ad}(V_G)\xi_D
-N_gA^{-1}N_e^\top L
\left(\delta a+\operatorname{ad}(V_G)\xi_D
-(\delta J_r)\dot\tau\right).
\tag{E12}
\]

这给出G更新的解析Jacobian；tight取 `V_G=0`、其状态导数为0。它没有给形变强加新的投影、重锚或卸载模型，也不将原式(22)用作真实内力动力学。

## 4. 离散预测与异步Q

令连续字段为 `f_i`，其数值body分量对右状态扰动的Jacobian为 `A_i`，`S_i`选取该状态块。式(18)pose右更新的离散Jacobian行为

\[
F_i=\Ad_{\Exp(-\Delta f_i)}S_i
+\Delta J_r(\Delta f_i)A_i.
\tag{E13}
\]

V为欧氏块，`F_V=S_V+Δ A_V`。O字段为V；EE字段为各自held U；C字段为0。保留(E13)中的初始误差伴随输运，不能只写 `I+ΔA` 而忽略右切空间变化。

异步Q沿用冻结近似 `Q_c=.004 Q_table`。每个真实事件间隔Δ使用

\[
Q_d=\Delta L_wQ_cL_w^\top,\qquad
P^-=F P F^\top+Q_d,
\tag{E14}
\]

其中pose噪声映射块为 `J_r(Δf_i)`，V为I，运输C的Q块为0。不能把事件切分后每段都用 `Δ²Q_table`，也不能把原4ms心跳改为传感器近似时间。完整4ms无中间事件时，该尺度对应已冻结的 `.004² Q_table`；它仍是工程异步近似，不声称复刻作者未公开的异步实现。

## 5. 迭代误差状态更新与Schmidt冻结

计划使用固定prior `(X0,P0)`，每次内层迭代在 `Xi=X0 boxplus δ_i` 重新线性化，不能将同一packet重复当作独立测量降低协方差。pose残差为 `r_i=Log(h(Xi)^-1 Z)`，弹性wrench为 `Z−h(Xi)`；原R不调参。

局部pose残差对预测观测扰动的负导数含 `J_l(r_i)^-1`；从prior误差δ到Xi局部右误差的映射为各pose块 `J_r(δ_i)`，V块为I。令该锚定映射为T_i，可构成

\[
H_{anchor,i}=J_l(r_i)^{-1}H_{local,i}T_i
\tag{E15}
\]

的pose行；欧氏wrench行不乘残差Jacobian。由此在同一prior切空间形成迭代候选

\[
\delta_{i+1}=K_i\left(r_i+H_{anchor,i}\delta_i\right),
\quad K_i=P_0H_{anchor,i}^\top
\left(H_{anchor,i}P_0H_{anchor,i}^\top+R\right)^{-1}.
\tag{E16}
\]

运输时令K的C行严格为0，保持C均值；不清零其先验不确定度。拟用测量白化与Cholesky求解改善不同SI尺度下的数值条件，数学上仍与(E16)等价，不新增噪声或采用伪逆来绕过坏协方差。

最多5次内层迭代；以相邻候选之间的右 `local` 差按冻结分量门判断收敛：pose平移/旋转各1e−6m/rad，V线性/角向各1e−5m/s及rad/s。未收敛保留实际迭代数和状态；连续3个packet未收敛触发停止，不强称收敛或扩大迭代预算。

最终只计算一次Joseph协方差

\[
P_{anchor}^+=(I-KH)P_0(I-KH)^\top+K R K^\top.
\tag{E17}
\]

在C的K行0、C均值注入0时，该式保留P_CC并正确更新active/C跨块。注入最终δ后，按右retraction微分重置

\[
P^+=T_\delta P_{anchor}^+T_\delta^\top,
\qquad (T_\delta)_{pose}=J_r(\delta_{pose}),
\qquad (T_\delta)_V=I.
\tag{E18}
\]

C块的重置为I。计划以独立矩阵Exp/Log差分核验(E18)，而不是只比较同一个helper的输出。按冻结条件检查非有限、协方差非对称及负特征值；不对角化、裁剪负特征值或把估计自由形变投影为0。

这些是尚待实现与验证的迭代流形估计设计。未取得资格前，不能据这些方程声称已复现IESEKF或满足实时预算。

## 6. 因果时间与样本独立性

observer预测到实际新sample时间戳；250Hz仍为心跳和控制频率。同stamp的新观测成组，多个可见视图是变维观测，不重复消费缓存。sample_id必须唯一，sample_stamp与当前滤波时间相符，delivery_stamp不得早于sample_stamp。错时、重复或缺失样本记录失败，不把5ms的采样当8ms当前观测，不隐式改时间戳。

预测输入只能是上次已经发布的H-selected body command历史。主滤波不读取当前真实EE速度、真实V、真实接触力或待执行队列中的oracle速度。300ms代表例仍是未建模时延压力条件；不能为使结果变好改成GT实际input或添加预测补偿。主控制器只访问独立的估计状态，真值只用于评分及已明示诊断/模式资格。

## 7. 在线快速计算候选及未获资格

原几何模块的字节、模型ID与reference SHA保持不变。在线速度可选方案只是同一模型的等价数值计算核，尚未实现、未微基准、未接入mechanics，不能据此重新启动当前失败资格。

候选一使用

\[
J_r(\tau)=\sum_{n=0}^{\infty}
\frac{(-\operatorname{ad}\tau)^n}{(n+1)!}
\tag{E19}
\]

及小tau幂级数，替代每次12×12矩阵指数。计算 `(δJ_r) dotτ` 时可只微分矩阵作用向量：固定w，令 `q_0=w`、`D_0=0`，递推

\[
q_n=-\operatorname{ad}(\tau)q_{n-1},\qquad
D_n=-\operatorname{ad}(\tau)D_{n-1}+\operatorname{ad}(q_{n-1}).
\tag{E20}
\]

则 `sum D_n/(n+1)!` 给出 `(dJ_r/dτ)w`，用于(E12)，避免六次Frechet矩阵指数。

候选二在小tau域使用inverse-Jacobian的Bernoulli展开，记 `A=ad(τ)`：

\[
J_r^{-1}=I+\tfrac12A+\tfrac1{12}A^2
-\tfrac1{720}A^4+\tfrac1{30240}A^6
-\tfrac1{1209600}A^8+\tfrac1{47900160}A^{10}
-\tfrac{691}{1307674368000}A^{12}+\cdots.
\tag{E21}
\]

标准pivot的约束求解还可仅使用SO(3)左Jacobian逆；sliding需保留SE(3)线角耦合，不可将其当纯线性投影。原软垫逐分量旋转界仍意味着 `||θ||≤sqrt(3)×.15rad`，不是norm≤.15；快速计算核必须在完整有效域资格，对照未改的canonical `grasp_rate` 的D、tau、a、V_G、tau_dot、约束矩阵和EE原点零功。还须检查误差尾项、近零角分支、条件数、无状态重锚及全f/Jac等价，不能仅凭“幂级数很快”声称可投入运行。

任何后续等价性能工程必须先明确资格与预算，不能放宽120秒case、缩短5秒settle、修改K/B/惯量/积分器或将主滤波换为GT。若问题来自冻结积分方法对刚性动力学的不稳定，优化计算速度不能解决其数值稳定性；两者应分别报告。

## 8. 资格计划与当前缺项

预先声明的计划包含42维状态/noalias、六类测量及解析Jacobian、三种双臂模式的离散F差分、右reset独立矩阵oracle、固定prior单包线性Gaussian例、Schmidt C均值/P_CC与跨块、异步Q、重复/错时拒绝、快速几何对canonical。这些只是将来待执行的数学/接口case，不是本轮实验样本。

该计划尚未证明任何滤波门成立，也尚未覆盖完整75对预标定、多率传感器生成器、全95秒估计/控制、反复未收敛退出或在线性能。后续若动力学及模型争议解除，仍须按[阶段资格规格](P2_STAGE2_QUALIFICATION_SPEC.md)完成这些缺项，记录实际源码/输入/阈值/墙钟/输出，才可标estimator_qualified。

本轮停止于独立动力学门：没有估计器实现，没有估计器资格运行，没有快速计算核运行，没有控制矩阵结果。P2累计小修仍为1/3，剩余2；本设计及未执行测试声明不消耗新的科学修正轮次。冻结几何/协议和P4证据不改，不自动进入P3。
