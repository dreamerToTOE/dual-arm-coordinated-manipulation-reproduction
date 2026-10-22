# P2-T00 式(1)–(26)/图表 → 代码 → 任务 对照索引

**状态口径**（全文统一）

| 标记 | 含义 |
|---|---|
| `LITERAL` | 按论文印刷式实现，未发现代数改写 |
| `APPROX` | 保留论文显式引入的近似（如 R̄） |
| `ADAPTED` | 用户已批准的偏离，有独立推导与资格证据 |
| `NOT_IMPL` | 论文有、代码无 |
| `EXTRA` | 代码有、论文无（工程/扩展项） |

代码路径均相对仓库根。行号以本分支 HEAD 为准，仅供定位。

---

## 1. SE(3) 预备（式 1–6）→ `baselines/p2_pose_force/contact_geometry.py`

| 式 | 内容 | 代码 | 状态 | 说明 |
|---|---|---|---|---|
| (1)(2) | ⊞ / ⊟ 右扰动、右差 | `State.retract` / `State.local`（`mechanics.py`）；`FilterState.retract/local`（`observations.py`） | LITERAL | 姿态块用 `T @ Exp(δ)`，速度块用加法；与 (2) 的 `Log(Y⁻¹X)` 一致 |
| (3) | T = [R t; 0 1] | 全局 4×4 数组 | LITERAL | — |
| (4) | Exp_SE(3) = [Exp_SO(3)(θ), V(θ)ρ] | `se3_exp` + `_V` | LITERAL | `_V` 用小角度级数切换，阈值 1e-4 |
| (5) | Log_SE(3) = [V(θ)⁻¹t, θ] | `se3_log` | LITERAL | 用 `solve(_V(θ), t)`，非迭代 |
| (6) | Ad_T = [R, [t]×R; 0, R] | `adjoint` | LITERAL | 线性在前 `[v;ω]`，与论文 twist 顺序一致 |

**约定**：`T^a_b` 把 b 映入 a；body twist `[v;ω]`；wrench `[f;m]`；共同 base 取 `b = b1`；长度 m、角度 rad。已在协议 `conventions` 段冻结。

## 2. 接触模型（式 7–12）

| 式 | 内容 | 代码 | 状态 | 说明 |
|---|---|---|---|---|
| (7) | τ = Log(T^e_g) | `grasp_rate` / `mechanics`：`D = inverse(E) @ O @ G`，`tau = se3_log(D)` | LITERAL | D 即 T^{e_r}_{g_r} |
| (8) | T^{e1}_{g1} = (T^{e1}_{b1})⁻¹(T^{b1}_b)⁻¹T^b_o T^o_{g1}；T^{e2}_{g2} = (T^{e2}_{b2})⁻¹T^{b2}_{b1}(T^{b1}_b)⁻¹T^b_o T^o_{g2} | 同上 + `common_endpoints`（`E2_common = C⁻¹E2`） | LITERAL | C 方向为 b1→b2，未颠倒 |
| (9) | h_K = −K τ | `mechanics`：`elast = -K[r]*tau` | LITERAL | 负号方向正确（机器人作用于物体） |
| (10) | V^e_{g,e} = R̄ Ad_{(T^o_g)⁻¹}V^o_o − V^e_e | `relative = Rbar @ adjoint(inverse(G)) @ V - U[r]` | APPROX | 代码注释明确"保留论文的 R̄ 近似，不是 Ad(D)"；有限形变下非精确 |
| (11) | h_B = −B V^e_{g,e} | `damp = -B*relative` | LITERAL | B 对角 |
| (12) | h^o_E = W H h，W = [Adᵀ_{(T^o_{e1})⁻¹}, Adᵀ_{(T^o_{e2})⁻¹}] Hᵀ | `maps = adjoint(inverse(A)).T`，`W = hstack(maps) @ H.T` | LITERAL | 连尾部的 `Hᵀ` 也照印；对选择矩阵 HᵀH 幂等，数值上等价 |

**H 选择矩阵**（论文 §III-A）：`selection("tight") = I6`、`pivot = I6[:5]`（不传递 z 向力矩）、`sliding = I6[2:]`（不传递 x/y 线力）→ 与论文 `[I5,0]`、`[0_{4×2},I4]` 一致。`H̄` 取 H 零空间正交基；对三种标准模式用精确基，其他 H 走 SVD。

## 3. 动力学与状态（式 13–16）

| 式 | 内容 | 代码 | 状态 | 说明 |
|---|---|---|---|---|
| (13) | U = (V^{e1}_{e1}, V^{e2}_{e2}) ∈ R¹² | `state_rate`：`rate[12:18]=U[0]`、`rate[18:24]=U[1]` | LITERAL | 理想 Cartesian 速度端点 |
| (14) | X = (T^b_o, V^o_o, T^{b1}_{e1}, T^{b2}_{e2}, T^{b1}_{b2}, T^o_{g1}, T^o_{g2})，p_X = 42 | `State` / `FilterState`，状态顺序 `O,V,E1,E2,C,G1,G2` | LITERAL | 42 维协方差按此顺序 |
| (15) | f(X,U) 七块 | `state_rate`；抓取块由 `grasp_rate` 给出 | **ADAPTED** | 见下方"式 (15) 争议" |
| (16) | V̇^o = M⁻¹(h^o_E − B_a V^o − [[ω]×,0;[v]×,[ω]×] M V^o) + [R^o_b g^b; 0] | `acceleration` | LITERAL（M 除外） | Coriolis 块写法与论文一致；**M 取均质长方体对角阵**（论文未给惯量）→ 属 ADAPTATION |

**式 (15) 争议（必须单列）**
- 论文印刷式最后两项为 `+H̄H̄ᵀAd_{(T^e_g)⁻¹}V^e_{g,e}`。旧审计给出反例：sliding 自由方向、EE 静止、物体 0.01 m/s，按印刷正号 4 ms 后 D 平移 80 µm，与"自由方向垫片不变形"矛盾。
- 现实现为 `p2.spatial_free_log_constraint.v1`：令 `a = Ad(G⁻¹)V_o − Ad(D⁻¹)U`，`N = null(H)`，`Ng = Ad(D⁻¹)N`，解 `NᵀJr(τ)⁻¹(a + VG) = 0` 得 `VG`，`τ̇ = Jr(τ)⁻¹(a + VG)`。不变量 `Nᵀτ̇ = 0`：自由 Log 分量保持初值，不清零、不重锚。
- 该模型是**用户批准的接触演化偏离**，有 68/68 有限形变资格，**不是**作者原式，也不是已核实勘误。原印刷式仅作审计对照保留。

## 4. 观测与滤波（式 17–18）

| 式 | 内容 | 代码 | 状态 | 说明 |
|---|---|---|---|---|
| (17) | Z = (T^{b1}_{e1}, T^{b2}_{e2}, h^e_{K1}, h^e_{K2}, {T^{b1}_o}ᵢ, {T^{b2}_o}ⱼ) | `_measurement`（`estimator.py`）；`ObservationGenerator.sample` | LITERAL | 视觉为 marker→COM 后的物体位姿；robot2 用 `C@O = T^{b2}_o`；触觉只送 **h_K**（不含 h_B） |
| (18) | X_{k+1} = X_k ⊞ ΔT(f + w)；Z = g(X) ⊞ v | `RightIESEKF.predict` + `prediction_linearization` | LITERAL | 右 Euler；**正是 3.948 s 停止的数值根因，见 POST §4.4** |

多率：plant tick 1/3000 s；滤波心跳 4 ms（250 Hz）；EE 传感器/命令 200 Hz、50 Hz；触觉 100 Hz；视觉 15 fps；76 s 后停用 robot2 视觉。均与论文一致。

## 5. 控制（式 19–26）

| 式 | 内容 | 代码 | 状态 | 说明 |
|---|---|---|---|---|
| (19) | V^e_e = V^{e_F}_e + V^{e_P}_e | `ControlResult.U_F/U_P/U_cmd` | LITERAL | 同一坐标系内相加 |
| (20) | h_{I,t} = (I − W†W)Hh；h_I = Hᵀh_{I,t} | `hI = H.T@(I − pinv(W))@(H@h)` | LITERAL | 缩放 `HᵀH` 后缀与 W 一致 |
| (21) | V^{e_F} = −K_F h^e_I | `UF = -KF*hI`，KF 形状 (2,6) | LITERAL | KF1/KF2 取表 II |
| (22)(23)(24) | 内力闭环局部线性化 | **不用于生成力曲线** | NOT_IMPL（故意） | 旧审计发现印刷式 Jr 参数与式(9)直接微分不一致；协议 `eq22_used_to_generate_force_curves=false` |
| (25) | V^{e_P} = Ad_{(T^o_e)⁻¹}(V^o_{o,d} + K_P τ^o_{o,d}) | `UP = Ad(inv(inv(O)@E)) @ (ff + KP*error)` | LITERAL + EXTRA | 括号内求和与伴随外置与原文一致；`ff = Ad(O⁻¹O_d)V_d` 是代码对"desired→current 物体系"的显式实现（原文未展开该细节，需 T05 复核） |
| (26) | q̇ = J†_{e,t}V^r_{e,t} + (I − J†J)q̇₀；J_{e,t} = H_r J^r_e | 未实现关节级 | NOT_IMPL（代之以 `U_applied = Hᵀ H U`，J=I、q̇₀=0） | 明确标注为理想 Cartesian 约化，**不**证明 iiwa/SIA5F/FR3 可执行性；T05 要求补 7-DOF |

## 6. 表 I / 表 II 参数（已逐项核对页面图像）

表 I（Q/R 对角，乘倍率）与表 II（K、B、B_a、KF、KP）在 `configs/p2_closed_loop_protocol_v3.json::original_parameters` 中逐项落地；exp4 模型刚度 `K1=diag(1641,1641,1400,.7,.7,.7)`、`K2=diag(7641,7641,6400,1.8,1.8,1.8)` 也已记录。**exp4 只改观测/控制器模型 K，真实 plant 保持名义 K**（论文文字支持此读法）。

正文明细：A 0.684 kg / 280×90×40 mm；B1、B2 各 0.280 kg / 75×140×40 mm；C 0.418 kg / 370×40×40 mm。**协议 `model.objects` 目前只有 A 与 C，缺 B1、B2**（T09 前置缺口，见 POST §5）。

## 7. 实验 → 任务 → 当前状态

| 论文证据 | 内容 | 任务 | 状态 |
|---|---|---|---|
| Fig. 6 exp1 | 仅位姿控制，维持约 1.5 N 不必要内力 | T06 | NOT_EXECUTED |
| Fig. 6 exp2 | 仅内力控制，位置/角度误差约 10 mm / 4.5° | T06 | NOT_EXECUTED |
| Fig. 6 exp3 | 双控制器同时，精度近 exp1、内力近 exp2 | T06 | NOT_EXECUTED（旧闭环=首条 exp3 于 3.948 s 停止） |
| Fig. 6 exp4 | 刚度失配，瞬态变差、稳态相近 | T06 | NOT_EXECUTED |
| Fig. 6 卡尺精度 | 位置 < 0.1 mm、角度 0.42° | T06 | NOT_EXECUTED（仿真不可直接对标，需声明测量分辨率差异） |
| Fig. 7 | 高内力矩机动，exp3 力矩降约 80% | T07 | NOT_EXECUTED |
| Fig. 8 | A→B1→B2→C 装配，5 次重复，法向角均值/标准差 | T09 | NOT_EXECUTED |
| Fig. 9 | 130 s 抓力降至 0.3 N，H2 pivot→sliding，目标下移 200 mm | T08 | NOT_EXECUTED（旧仅有 30 s 理想运动学替代方案，未运行） |
| 附加视频 1 | 流形 IESEKF 与标准 EKF 对比 | T04 | NOT_EXECUTED（视频未取得，只能自建对照并标 OUR_EXTENSION） |
| 附加视频 2 / §IV-A 末段 | 慢速下放、外力和接触检测完成最终放置 | T09 | NOT_EXECUTED（放置段在旧协议中明确"no plate contact"） |
| Fig. 1–5、Table I–II | 系统、几何、初始/最终构型、参数 | T01/T02/T09 | 参数与示意图已核对；Fig. 5(b) 装配布局无坐标，只能估读 |

## 8. 论文未给、代码自行引入的量（必须保持可见）

均质长方体惯量；抓取点坐标 `A_grasps`、`conditional_sliding.grasps`；机器人基座相对变换 `true_C_b1_to_b2 = (0,0.6,0), Rz(π)`；路点绝对坐标与分段时刻（13/23/55/76/95 s 中 23 与 55 为自定）；5 s 初始 settle；75 对预标定；视觉 bias `visual_bias_body_cam1/2`；`Q_cont = 0.004 Q_table` 的连续化解释；模式切换守门阈值（1e-6 m / 6e-3 N / 2e-6 Nm）；命令上限（0.15 m/s、0.5 rad/s，拒绝而非饱和）。以上在协议中均有 `ADAPTATION`/`ENGINEERING` 标注，T01 需转成正式的 deviation register。
