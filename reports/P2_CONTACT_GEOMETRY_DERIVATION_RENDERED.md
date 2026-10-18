# P2 有限 SE(3) 抓取坐标演化推导

2026-10-14；模型 `p2.spatial_free_log_constraint.v1`。

此显示版仅将Ad/Log写成标准LaTeX算子；资格元数据引用的[原推导字节版本](P2_CONTACT_GEOMETRY_DERIVATION.md)保留，数学内容不变。

我采用用户批准的几何一致路线，重新推导抓取坐标演化。下面的演化属于 **[DEVIATION / 用户已批准]**：以原文的相对变换和右更新为基础，同时约束自由方向的 Log 形变和抓点的物理自由 twist；不将它写成作者式(15)的原样实现或已核实勘误。Cartesian端点和观测缩减另属[ADAPTATION]。原式及其符号争议继续保留在[原文审计第7节](P2_ORIGINAL_PAPER_AUDIT.md#7-关键争议推导与本轮数学证据)，不改写历史审计。

原论文依据为本机私有源`references/private_sources/P2_original.pdf`的式(1)、(7)–(15)，身份/SHA见[原文审计](P2_ORIGINAL_PAPER_AUDIT.md)。右、左Jacobian约定采用原文参考[19]，Solà、Deray、Atchuthan的[A micro Lie theory for state estimation in robotics v9](https://arxiv.org/html/1812.01537v9)，尤其III-B/C及附录D-C3。下述接触闭合式、可逆域证明和资格边界是本项目的推导。

## 1. 坐标、状态与精确相对运动学

记 `T^a_b` 将 b 坐标映射到 a 坐标，六维量排列为 `[线性，角向]`。令

\[
O=T^b_o,\qquad E=T^b_e,\qquad G=T^o_g,
\qquad D=T^e_g=E^{-1}OG,
\qquad \tau=\operatorname{Log}(D)=\begin{bmatrix}\rho\\\theta\end{bmatrix}.
\tag{D1}
\]

O 和 E 必须先表达在同一个 base。若沿用原文的机器人原生 EE pose，记 `B1=T^b_b1`、`C=T^b2_b1`，则 `E1_shared=B1 E1_native`、`E2_shared=B1 C^-1 E2_native`；不能将 robot2 原生 base 中的 E 直接代入(D1)。固定左乘 base 变换不改变 EE 的 body twist。

采用原式(1)/(18)的右更新，定义

\[
\dot O=O\widehat V_o,\qquad
\dot E=E\widehat U,\qquad
\dot G=G\widehat V_G.
\tag{D2}
\]

其中 `V_o` 在物体 body frame，U 在 EE body frame，`V_G` 是 G 的右切空间速度，表达在 g 轴下。对(D1)逐项求导，得到

\[
D^{-1}\dot D
=\widehat{\operatorname{Ad}_{G^{-1}}V_o}
-\widehat{\operatorname{Ad}_{D^{-1}}U}
+\widehat V_G.
\tag{D3}
\]

因此令

\[
a=\operatorname{Ad}_{G^{-1}}V_o-\operatorname{Ad}_{D^{-1}}U,
\qquad \dot\tau=J_r(\tau)^{-1}(a+V_G).
\tag{D4}
\]

这里 a 是暂时冻结 G 时的相对 body twist；不是原式(10)以 `Rbar` 定义的相对速度。右 Jacobian 是指数映射的微分，不能在有限形变下以 I 替代。其与左 Jacobian 满足

\[
J_l(\tau)=\operatorname{Ad}_DJ_r(\tau),\qquad
J_r(\tau)^{-1}\operatorname{Ad}_{D^{-1}}=J_l(\tau)^{-1}.
\tag{D5}
\]

此处采用的微分约定与 Micro Lie 原文式(67)–(75)一致；式(D3)则直接由矩阵乘积微分获得。

## 2. EE 自由子空间与抓点 lift

原论文的标准选择矩阵保持不变：

| 模式 | H | EE 自由生成元 |
|---|---|---|
| tight | `I6` | 无 |
| pivot | `[I5,0]` | 纯角速度 z |
| sliding | `[0_(4×2),I4]` | 纯线速度 x、y |

取 `N_e` 的列为 `null(H)` 的正交基，满足

\[
HN_e=0,\qquad N_e^\top N_e=I_k,
\qquad k=6-\operatorname{rows}(H).
\tag{D6}
\]

H 与 `N_e` 按 EE 的传感器原点和轴定义。对 G 的更新，物理自由 twist 在 EE 作用点应为 `N_e ζ`；转换成 G 的 body 速度必须使用完整伴随：

\[
\operatorname{Ad}_DV_G=N_e\zeta,
\qquad N_g=\operatorname{Ad}_{D^{-1}}N_e,
\qquad V_G=N_g\zeta.
\tag{D7}
\]

这一步同时处理轴方向与作用点。pivot 的 g-body 生成元可能包含线速度：它对应绕 EE z 轴旋转，不能误写成始终只绕 g 的 z 轴旋转。sliding 的两个纯线速度生成元则随 D 的旋转转换到 g 轴。

我将自由 Log 分量约束另行明确为

\[
N_e^\top\dot\tau=0.
\tag{D8}
\]

式(D8)是本最小模型对自由垫片形变的定义，不是一般摩擦接触定律。约束行作用于 EE 约定下的 Log 坐标；`N_g` 作用于 g-body twist。二者不能直接使用同一个数值基来代替。

代入(D4)/(D7)，定义

\[
A_c=N_e^\top J_r(\tau)^{-1}N_g,
\qquad
\zeta=-A_c^{-1}N_e^\top J_r(\tau)^{-1}a,
\qquad
V_G=-N_gA_c^{-1}N_e^\top J_r(\tau)^{-1}a.
\tag{D9}
\]

小矩阵可逆时，这给出唯一的自由 twist 系数，无需另设优化控制器。tight 模式没有自由列，直接取 `V_G=0`，不求空矩阵的逆。由(D5)也可在 EE 空间等价求解：

\[
b=\operatorname{Ad}_Da,\qquad
A_c=N_e^\top J_l(\tau)^{-1}N_e,
\qquad
\zeta=-A_c^{-1}N_e^\top J_l(\tau)^{-1}b.
\tag{D10}
\]

在 `D=I` 时，(D9)退化为 `V_G=−N_e N_e^T a`，恢复原文审计反例所需的负向抓点运动；有限形变下则保留 Jacobian 和完整 lift。这与仅给印刷式(15)添加一个负号不同。

## 3. 自由 Log 初值与传递 wrench 零功

将(D9)代回(D4)，直接得到

\[
N_e^\top\dot\tau
=N_e^\top J_r^{-1}a+A_c\zeta=0.
\tag{D11}
\]

在固定接触模式、固定 EE 轴选择的连续时间段内，`N_e^T τ(t)=N_e^T τ(t0)`。初值为零时自由 Log 形变保持零；初值非零时它保持该非零值，模型不会自行卸载、重锚或清零。数值积分只近似保持这一不变量，漂移必须按既定门限记录，不能在每步投影状态后再宣称门禁通过。

令 EE 传递 wrench 为 `h_tr^e=H^T H h^e`，则由(D6)/(D7)

\[
(h_{tr}^e)^\top\operatorname{Ad}_DV_G
=(Hh^e)^\top HN_e\zeta=0.
\tag{D12}
\]

因此抓点自由更新不对传递 wrench 做虚功。这里的 wrench 和 twist 位于同一个 EE 原点；不能把 EE wrench 与未经转换的 g-body `V_G` 直接点乘。该结论对传递弹性/阻尼 wrench 都成立，但只涉及抓点更新这一项。

原式(12)的双臂 wrench 映射仍使用逆转置伴随。矩阵式 `(Wh)^T V=h^T W^T V` 只是代数转置恒等式；独立物理检查还须核对各侧的坐标方向和作用点，不能仅靠这个恒等式证明原式(12)全部正确。

## 4. 标准模式的可逆域与协议上限

令 `φ=||θ||`，取主 Log 图域 `0≤φ<π`。SE(3) 左 Jacobian 逆有块上三角结构，两块对角均为 SO(3) 左 Jacobian 逆 `L(θ)`。标准 sliding 的 `N_e` 只取线性 x/y，标准 pivot 只取角向 z，所以 `A_c` 分别是 L 的二维主子块或标量主子块，不包含线角耦合块。

由 SO(3) 左 Jacobian 逆的标准表达，令

\[
c(\phi)=\frac{1-\frac\phi2\cot(\frac\phi2)}{\phi^2},
\qquad
L=I-\tfrac12[\theta]_\times+c(\phi)[\theta]_\times^2,
\tag{D13}
\]

在零点取连续极限 `c(0)=1/12`。Micro Lie 原文式(146)给出等价形式。其对称部沿 θ 的特征值为1，垂直于 θ 的特征值为

\[
\beta(\phi)=\frac\phi2\cot\left(\frac\phi2\right)>0,
\qquad \beta(0)=1.
\tag{D14}
\]

因此任一上述标准主子块满足

\[
\operatorname{sym}(A_c)\succeq\beta(\phi)I_k.
\tag{D15}
\]

若 `A_c x=0`，则 `0=x^T A_c x≥β||x||²`，故 x=0；这证明小矩阵在该图域可逆，并给出 `σ_min(A_c)≥β(φ)`。该论证仅覆盖论文的标准 tight/pivot/sliding，不能推广到任意混合线角方向的 H。

原协议规定的是每个垫片旋转分量 `|θ_i|≤0.15rad`，不是 `||θ||≤0.15rad`。因此有效域的统一界为

\[
\phi\le\sqrt3\times0.15
\approx0.2598076211\ \mathrm{rad},
\qquad
\beta(\phi)\ge
\beta(\sqrt3\times0.15)
\approx0.9943686617.
\tag{D16}
\]

这里的数值是解析域界，不是资格运行结果。理论可逆域较宽，也不能据此扩大原软接触形变有效域或原实验退出界。实现保留 `rcond=1e−12` 的小矩阵奇异性检查和主 Log 边界检查；失败时报告，不以伪逆、状态归一化或形变投影掩盖。

## 5. 模式切换的初态资格

固定模式的(D11)只保持自由分量现值。它不能证明释放已有载荷时垫片会自行变为零形变，也不能复现低抓力、摩擦或低层夹爪控制。

设旧、新传递索引集合为 `T_old/T_new`，新恢复分量为 `R=T_new−T_old`，新释放分量为 `L=T_old−T_new`，新自由分量为 `F={0,…,5}−T_new`。沿用已登记卸载门限：

- `R∪L∪F` 的每个 Log 分量均须满足 `|τ_i|≤1e−6`，前三分量单位 m，后三分量 rad。
- `R∪L` 的切换前真实、未经过 H 选择的 `h=h_K+h_B`，各 force 分量须≤0.006N，各 moment 分量须≤2e−6Nm。不能用命令力或已经清除自由方向的 selected wrench代替。

| 切换 | 新释放分量 | 新恢复分量 |
|---|---|---|
| pivot→sliding | EE Fx、Fy | EE Mz |
| sliding→pivot | EE Mz | EE Fx、Fy |

检查新释放载荷是新模型零自由 Log 初态域的必要资格；它不改变原控制性能判据，也不声称原论文规定了这些数值。恢复条件沿用已登记门限。若新释放方向已有非零形变，仅切H会留下非零自由初值，随后(D11)不会自动把它消除，因此不能省略该检查。

门禁必须在协议规定的固定事件时刻执行。失败记录 `MODE_SWITCH_PRELOAD_INVALID`，保留 D/G/EE/物体状态及原始载荷证据；不重锚、不清零，不等待卸载后改切换时刻，也不增加低层抓握或释放动力学来制造成功。真值载荷只用于该资格与停止判定，不进入位姿/内力控制器或用于选择更有利的事件时间。未来 sliding 代表例可能由此真实失败。

即使门禁满足，也没有证明切换后的内部 wrench 范数不增加，更没有证明混合系统稳定；W/H 的改变及力学响应仍须独立分析和记录。

## 6. 坐标等价的限定范围

传感器 EE 原点及其接触轴是本模型的一部分，保持固定。此次可直接检查的坐标等价包括：

1. **共同世界 base 改变。** 对任意固定 `S∈SE(3)`，令 `O'=SO`、`E'=SE`，G及各 body twist不变，则D、a、`V_G`和`τ_dot`不变。改变 world 原点不等于移动传感器原点。
2. **物体 COM 的轴标签改变。** 对纯旋转Q，令 `O'=OQ`、`G'=Q^-1 G`、`V_o'=Ad(Q^-1)V_o`，E/U不变，D及g-body抓点更新仍不变。惯量和物体轴表达量须同步变换；物理物体及COM位置不变。
3. **自由基重参数化。** 对正交R，令 `N_e'=N_e R`，相应系数变为 `ζ'=R^T ζ`，物理`V_G`不变。

这些结论不授权任意更换传感器作用点后继续原样使用H、对角K/B和Log分量约束。一般局部坐标变换还须分别处理twist列、wrench对偶及约束行；完整SE(3) Ad通常不是正交矩阵，不能把 twist 和 wrench 当作同一种向量变换。此次资格不声称任意局部SE(3)换轴/移原点下模型全面等价。

## 7. 保留的原公式与未验证边界

式(9)/(10)/(11)/(12)/(20)/(21)/(25)及原 K/B/KF/KP、H/W 保留。本次只替换式(15)中 G 的演化。由独立plant软接触计算力、由原控制器计算输入的后续要求不变；本推导不以式(22)/(24)生成控制曲线。

数值步长比较若定义 `Δτ=τ_coarse−τ_fine`，则原式(9)对应的有符号弹性wrench差必须是 `Δh_K=−K Δτ`。逐分量门限可比较绝对值，但有符号原始输出必须保持这个负号；前三分量按N、后三分量按Nm分别记录，不将两类量拼成一个“总力”范数。

特别地，原式(10)是

\[
V_{rel,orig}=\bar R(D)\operatorname{Ad}_{G^{-1}}V_o-U,
\qquad h_B=-B V_{rel,orig}.
\tag{D17}
\]

若物体和EE作同一 world spatial运动，令 `q=Ad(G^-1)V_o`，则 `U=Ad(D)q`，精确相对运动给出 `a=0`、`V_G=0`、D不变。但原阻尼输入仍为

\[
V_{rel,orig}
=(\bar R(D)-\operatorname{Ad}_D)q
=\begin{bmatrix}-[t]_\times R\omega_g\\0\end{bmatrix},
\qquad D=\begin{bmatrix}R&t\\0&1\end{bmatrix}.
\tag{D18}
\]

当t非零且角速度适当时，它一般不为零。因此共同运动资格应检验精确相对运动与抓点更新，不能自动要求原阻尼力为零，更不能悄悄改式(10)消除这个差异。该有限形变近似继续列为与精确力学的差距。

此外，`h_K=−Kτ`的有限Log形变与物理相对twist之间存在Jacobian。即使形式上写出二次Log形变能，(D12)也不足以证明原弹性wrench是该能量的完整物理共轭。此次没有验证整个粘弹性模型的被动性、耗散性、全局稳定性、状态估计闭环、执行器时延性能、摩擦或硬件接触可执行性。局部软垫假设和原协议形变界仍约束后续解释。

## 8. 证据入口

几何实现见 [contact_geometry.py](../baselines/p2_pose_force/contact_geometry.py)，固定资格方法见 [qualify_p2_contact_geometry.py](../scripts/qualify_p2_contact_geometry.py) 与[任务前协议](P2_CONTACT_GEOMETRY_PRE_TASK.md)。后续资格记录入口为 [20261014 第二轮 summary.json](../results/20261014_P2_contact_geometry_qualification02/summary.json)。该链接指向待形成的运行证据，本推导不预填其状态或通过数量；最终资格、原始case和失败信息以实际落盘记录为准。
