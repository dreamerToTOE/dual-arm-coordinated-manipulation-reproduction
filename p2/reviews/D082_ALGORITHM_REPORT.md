# P2 核心算法数值复现报告（D082 范围）

**验收目标**：`ALGORITHM_NUMERICAL_VERIFIED`
**日期**：2026-10-19 | **分支**：`reproduce-p2-numerical-simulation-20261018` | **HEAD**：见 git log

---

## 1. 论文解决什么问题

De Simone 等（RA-L 2026, DOI 10.1109/LRA.2026.3665445）研究双臂刚性抓取柔性物体的
**协同位姿-内力控制**：通过视觉-触觉反馈，同时控制物体位姿（6 DOF）和双臂内部作用力
（不移动物体的内力分量），使用 IESEKF 融合视觉与触觉观测。

## 2. 原文提出什么算法

| 公式 | 内容 |
|---|---|
| Eq.1–6 | SE(3) 运算：Exp/Log、Adjoint、复合 |
| Eq.8–11 | 柔性接触模型：弹性形变 τ、刚度 K、阻尼 B |
| Eq.12 | 抓取矩阵 W：从臂坐标到物体坐标的 wrench 映射 |
| Eq.13–14 | 物体动力学：M V̇ + h = W h + gravity |
| Eq.15 | 自由对数约束：抓握框架在 H 约束自由方向内的运动 |
| Eq.17 | 观测模型：EE 位姿、弹性 wrench、物体位姿（视觉） |
| Eq.18 | IESEKF：右误差坐标、迭代更新、Joseph 协方差 |
| Eq.19–21/25 | 位姿-内力解耦控制：U_F = −KF·h_I、U_P = KP·error + feedforward |

## 3. 我们如何实现

| 模块 | 代码 | 关键类/函数 |
|---|---|---|
| SE(3) | `contact_geometry.py` | `se3_exp/log/adjoint/inverse/selection` |
| 接触 | `mechanics.py` | `mechanics()`: D, τ, hK, hB, h, W, internal |
| 动力学 | `native_kernel.cpp` + `mechanics.py` | `native.advance` (隐式中点), `midpoint_step` |
| 式(15) | `contact_geometry.grasp_rate` | `spatial_free_log_constraint.v1` |
| IESEKF | `estimator.py` | `RightIESEKF.predict/predict_to/update` |
| 稳定传播 | `stable_propagation.py` | `StableRightIESEKF`, `propagate`, `van_loan_stable` |
| 控制律 | `control.py` | `PoseForceController.evaluate` |
| 观测 | `observations.py` | `ObservationGenerator`, `initialize_from_fresh` |

## 4. 数值验证证据

### 4.1 SE(3) 运算（T02, 21 项 PASS）

| 检查 | 最大误差 |
|---|---:|
| Exp/Log 往返（随机/小角/近π） | 4.4e-16 |
| Ad(T₁T₂)=Ad(T₁)Ad(T₂) | 4.4e-16 |
| Ad(Exp(τ))=expm(ad(τ)) | 4.5e-16 |
| Wrench 功率不变性 | 2.2e-16 |
| Jr⁻¹ vs FD | 2.6e-10 |
| 近 π 域门 | 行为正确 |

### 4.2 接触模型（T02, 6 项 PASS）

| 检查 | 最大误差 |
|---|---:|
| 式(8) D=E⁻¹OG | 0 |
| 式(9) hK=−Kτ（含 K 正定） | 0 |
| 式(10)(11) hB=−B(R̄Ad(G⁻¹)V−U) | 0 |
| 式(12) W 结构 | 0 |
| 虚功一致性 | 5.9e-16 |
| 式(20) 投影幂等/零功/完备性 | 3.2e-13 |

### 4.3 动力学（T03）

| 检查 | 结果 |
|---|---|
| 连续谱（A/B/C） | −2183 / −6750 / −9336 s⁻¹ |
| native 隐式映射 ρ(h/h2/h4) | 1.000000（中性） |
| 显式 Euler ρ(h) | 1.0 / 1.25 / 2.11（B/C 不稳） |
| Richardson 收敛阶 | **2.00**（全块） |
| 受扰运动（0.3 s） | 衰减、能量降、Newton≤2 |
| 4 对象（A/B1/B2/C） | 全部通过（B1/B2 为 ADAPTATION） |

### 4.4 IESEKF（T04）

| 检查 | 模式 A (Euler) | 模式 B (指数) |
|---|---|---|
| ρ(Φ) @ 4 ms | **7.73 (A) / 36.38 (C)** | 1.000019 / 1.000026 |
| Φ vs map FD | 1.8e-10（精确） | 1.35e-2（O(h²) 近似） |
| Qd | h·Lw·Qc·Lwᵀ | Van Loan（scaling/squaring） |
| R1 重放 | **逐位复现** 3.948 s 失败 | PREFIX_SURVIVED |
| R1+ 闭环 7.5 s | — | **因果闭环通过** |
| 95 s 闭环 | — | BUDGET_STOP @ 65.8 s（稳定） |

### 4.5 观测 Jacobian（T02）

6 类观测（EE1/EE2/hK1/hK2/visual1/visual2）解析 Jacobian vs 独立中心差分：**5.9e-11**。

### 4.6 位姿-内力控制律（D082 新增，14/14 PASS）

| 检查 | 内容 |
|---|---|
| 零误差不动点 | 零位姿误差 → U_P = 0 |
| 内力零合力 | W @ (H @ h_I) ≈ 0（不移动物体） |
| 力增益比例 | U_F ∝ h_I |
| 位姿误差映射 | 非零误差 → 非零 U_P，方向一致 |
| 选择矩阵过滤 | H^T H 正确提取选定分量 |
| 混合模式 | U_cmd = U_F + U_P |
| 命令域 | \|lin\|<0.15, \|ang\|<0.5 |
| 激活时序 | force_active/pose_active 标志正确 |
| 非法输入 | NaN/非 FilterState 被拒绝 |

## 5. 我们的适配（非原文内容）

| 适配 | 原因 | 量化 |
|---|---|---|
| 式(15) 替代 | 印刷式产生 2× 自由形变（80 µm/4ms） | 反例独立复现 |
| 稳定传播 V1 | 模式 A 的 Euler 在 4 ms 不稳（ρ=7.73） | 模式 B ρ=1.0 |
| `midpoint_step` ≠ native | 旧审计的 ρ=2.73 是显式中点，非生产隐式 | 标量因子逐位吻合 |
| B1/B2 惯量/抓取 | 论文未给出 | ADAPTATION |

## 6. D082 范围外的原文实验（`OUT_OF_SCOPE_D082`）

| 原文实验 | 状态 |
|---|---|
| Exp1–Exp4 完整 95 s 闭环 | `OUT_OF_SCOPE_D082` |
| Fig.6 位姿/内力时间曲线 | `OUT_OF_SCOPE_D082` |
| Fig.7 高内力场景 | `OUT_OF_SCOPE_D082` |
| Fig.8 四物块装配 | `OUT_OF_SCOPE_D082` |
| Fig.9 Pivoting/Sliding | `OUT_OF_SCOPE_D082` |
| 30 案 × 5 seed | `OUT_OF_SCOPE_D082` |
| 真实视觉/触觉硬件 | `OUT_OF_SCOPE_D082` |

## 7. P2 原文 / D082 / 实际三栏对照

| 模块 | 原文要求 | D082 要求 | 实际状态 |
|---|---|---|---|
| SE(3) 数学 | ✅ | ✅ | **VERIFIED** |
| 接触/抓取 | ✅ | ✅ | **VERIFIED** |
| 动力学 | ✅ | ✅ | **VERIFIED** |
| IESEKF | ✅ | ✅ | **VERIFIED**（含 3.948s 失败证据） |
| 位姿控制 | ✅ | ✅ | **VERIFIED** |
| 内力控制 | ✅ | ✅ | **VERIFIED** |
| 95 s 闭环 | ✅ | ❌ | OUT_OF_SCOPE_D082 |
| Fig.6–9 | ✅ | ❌ | OUT_OF_SCOPE_D082 |
| 4 物块装配 | ✅ | ❌ | OUT_OF_SCOPE_D082 |

**结论**：P2 达到 `ALGORITHM_NUMERICAL_VERIFIED`。

## 8. 双 FR3 侧吸协同搬运适用性

本报告验证的算法可直接映射到双 FR3 侧吸 Benchmark：
- **SE(3) + 接触模型** → 吸盘-物体接触建模（将 K/B 替换为吸盘刚度）
- **抓取矩阵 + 内力解耦** → 双臂内力协调（防止挤压或滑落）
- **IESEKF** → 视觉-力传感器融合状态估计
- **位姿-内力解耦控制** → 同时跟踪目标位姿和控制内部力

**适用边界**：本验证基于数值模型，未考虑执行器动力学、传感器噪声、通信延迟等
实际因素。迁移到真实系统需要额外的鲁棒性设计和实验验证。

## 9. 关键文件

| 文件 | 内容 |
|---|---|
| `p2/reviews/T02_POST.md` | SE(3)/接触/抓取 23 项审计 |
| `p2/reviews/T03_POST.md` | 动力学谱/受扰/收敛 |
| `p2/reviews/T04_STAGE_A_POST.md` | 稳定预测器资格 |
| `p2/reviews/T04_R1_POST.md` | R1 A/B 重放 |
| `p2/reviews/T04_R1_PLUS_POST.md` | R1+ 完整统计 |
| `p2/reviews/T04_B_COUPLED_7P5_POST.md` | 7.5 s 闭环 |
| `p2/reviews/T04_B_95_POST.md` | 95 s 闭环（BUDGET_STOP） |
| `p2/reviews/D082_CONTROL_VERIFICATION.json` | 控制律 14/14 PASS |
| `p2/reviews/T03_SPECTRUM.json` | 4 对象谱分析 |
| `p2/reviews/T02_MATH_AUDIT.json` | 23 项数学审计 |
