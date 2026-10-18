# P2 第二阶段：首门超时后的固定数值风险审查

2026-10-14。首轮真实动力学资格已记录FAIL_STOP：120.05096s只到tick9972、物理时刻3.324s，最后250Hz样本3.32s。前11个数学检查通过，但固定5s settle未完成；不能把当前力平衡或趋势当终端门通过。highmoment/C实际settle、IESEKF、控制矩阵没有因这条记录取得资格。

本审查先登记源码、输入和方法，等待root冻结commit后执行。结果唯一目录为results/20261014_P2_stage2_numerical_audit01。这里的静态数学点和孤立one-step微分不是新增ODE trajectory，不运行控制/估计，也不对真实plant补时间、reset或强行设置平衡。未修改冻结JSON、质量/刚度/阻尼/增益/初态/clock/科学判据和已批准几何，故本审查不消耗新的小修轮。

## 1. 固定输入与分析方法

源码：[audit_p2_stage2_numerics.py](../scripts/audit_p2_stage2_numerics.py)。只使用冻结A transport与C sliding fixture，各两个点，总4点：

| 数学点 | 固定构造 | 限定 |
|---|---|---|
| A_nominal | 原A初始O/E/C/G，V=U=0，双pivot，名义physics | 运动速度为0，但gravity加速度未平衡，不是实际静态平衡 |
| A_analytic_equilibrium | 上述诊断副本O向world−z移δ=mg/(K1_x+K2_x)，其它不改 | 仅检查解析点残差；不是5s积分结果或真实plant初始化 |
| C_nominal | 原竖直C初始O/E/C/G，V=U=0，双pivot，名义physics | 实际C动力学门尚未运行完成，不能称已有C实验失败 |
| C_analytic_equilibrium | 同C诊断副本O向world−z移相应δ | 同上；不得用于替换真实settle |

每点保存完整42维state、K/B/Ba/M/g、tau/hK/hB、f0和contact+gravity残差。对象惯量按冻结均质箱公式；core几何模块SHA47557da9…和协议SHA423f58ca…运行前核对不变。

中央差分ε=1e−6，沿用冻结Jacobian差分步。状态按O/V/E1/E2/C/G1/G2，各SE(3)右retract、V欧氏扰动。连续field Jacobian由state_rate的正负扰动求得；这些点的SE(3)速度基准为0，不将一般运动点的body field差分冒称完整流形误差transport。

对每点分别取h=1/3000、1/6000s，调用midpoint_step的孤立one-step map；所有正负输出在同一未扰动one-step输出处作right local，然后差分42×42矩阵。没有逐时刻轨迹、控制或sensor数据，不算任何运输case。保存实际map矩阵和谱，同时列I+hA+.5h²A²的线性中点谱；nominal点因f0非零，两者差异不自动解释成代码错误。

谱完整保存real/imag/modulus，单列最快负实branch。严格|μ|>1的原始数与near-one中性数分开；near-one仅沿用原algebra_atol=1e−10作浮点标签，同时保留未筛选值。这不是新增稳定性验收阈值，输出无PASS/FAIL gate决定。equilibrium存在零rate和endpoint/C/G中性方向，μ约1不得混写成快模态数值发散。

同一A额外列出原式18完整4ms Euler预测I+.004A的风险乘子，只研究无measurement update的线性预测。没有运行IESEKF、异步观测或covariance correction，不能由此声称完整滤波已经发散，也不自动改变预测模型。

## 2. 独立物理矩阵交叉核对

用经典点速度v_point=v+ω×p、EE旋转换轴构造6维M和瞬时阻尼D，不复用Adjoint/Jr实现。Eq10的速度在object抓点计算、wrench在EE原点映射，因此预载有限D时两点可不同；不强迫瞬时D对称来偷偷修正原近似阻尼。

未变形名义点另列K=Σ J_point^T H^T H Kpad J_point以及gravity旋转导数，形成12维小形变reference，与完整42维的速度/位姿块分别比较。有限预载点K只标undeformed reference，不声称这个近似矩阵已经等于有限Log/geometric stiffness。误差逐行保存，不用混合单位norm创造新科学阈值。

原C long-axis Ixx约1.11467e−4kgm²，旋转阻尼和lever可能产生约−9.3e3s逆快模态；粗步中点存在风险。这个先验量级不是实测C失败。A的物理静态解可达，也不保证canonical Python在120s内完成5s；实现性能和数值稳定性是两个独立问题。

## 3. 审查输出与待决定事项

执行前状态：NOT_EXECUTED。root需先提交源码和本输入声明，然后运行固定一次；metadata登记commit/源码SHA/环境/ε/方法/全部参数和数学点。source、fixtures.jsonl、summary、termination及artifact SHA独立保存，任何失败不覆写首次动力学记录。

显式与隐式积分、物理substep或observer预测细分会改变既定数值解释；如果诊断支持此类改变，应提出具体协议选择并由用户决定，不自动实现。性能等价优化必须另证与不变canonical几何/力学等价，不能借超时放宽120s、改physics或直接用解析平衡绕过首门。当前仍是动力学门未完成、控制run0、小修1/3余2；本数学风险审查不使后续控制ready。
