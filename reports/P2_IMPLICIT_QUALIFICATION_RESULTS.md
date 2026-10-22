# P2隐式数值路线资格结果：固定中央差分门停止

2026-10-14。用户已批准隐式耦合Lie中点plant；本次实现来源37ccba062ebebd4c622901b016fbba563efcb390。原已验收geometry、canonical mechanics、v1协议、P4与旧失败保留。

## 实际完成范围

[N/D首跑](../results/20261014_P2_implicit_qualification01/summary.json)记录45项通过、1项失败，共46项；FAIL_STOP。36个已验收有限输入的新backend等价检查只比较G body twist及τ，不扩大为新的接触模型审查或36个完整力学检查。A的9个H组合另独立比较D/τ/hK/hB/h/合wrench/内力/W和连续field，与canonical相符。

第46项native_Jac_transport_tight_tight失败。42×42矩阵保存于[jac_transport_tight_tight.npz](../results/20261014_P2_implicit_qualification01/jac_transport_tight_tight.npz)。最大差分差异在零基行9/列27：物体body角加速度ω̇x对双机器人C右旋转扰动δθx的偏导，单位(rad/s²)/rad，即s⁻²。

- native前向AD：−33852.8882515372s⁻²。
- 固定ε=1e−6rad、Boost50位中央差分：−33852.888252175355s⁻²。
- 两者差6.381524144671857e−7s⁻²，超过原10⁻⁷逐分量数值门；不能改判PASS。
- native AD与独立Python解析链全矩阵逐分量差异均≤6.522213880089112e−10（各块保留自身单位）；连续field与Python最大逐分量差≤4.547473508864641e−13。解析一致不能独自解除差分门。

首跑在第46项停止，原始终止记录保存。隐式单步/五秒/半步、高moment、C尚未执行；不称implicit稳定或性能已验证。状态估计、观测和原控制源码已写入，但只做py_compile，组件测试未执行，均未获资格。完整调度/控制runner未实施、20主+10代表/诊断仍NOT_EXECUTED。

## 单轮固定诊断

[诊断首跑前声明](P2_IMPLICIT_FD_DIAGNOSIS_SPEC.md)，科学source c66496e；只在同一A fixture、同一连续field检查预声明ε=1e−6/2e−6/5e−7三个点，不积分、不新增控制case。三份完整矩阵已经保存；汇总归档错误另列，不混成算法发散。

| ε / rad | 行9/列27差异 / s⁻² | 相对原ε误差比 | 用途 |
|---|---:|---:|---|
| 1e−6 | 6.381524144671857e−7 | 1 | 原资格，FAIL保留 |
| 2e−6 | 2.552136720623821e−6 | 3.9992588960972326 | 诊断，不替代资格 |
| 5e−7 | 1.5964906197041273e−7 | 0.2501738743771877 | 诊断，不替代资格 |

中央差分D₂(h)=f′(0)+h²f‴(0)/6+O(h⁴)。误差近4/0.25比例，支持截断项为主要来源；高精度只减少舍入，不消除二阶截断。该证据不是对其他状态/模式或整机控制的保证。

若后续获明确批准，可仅将native continuous-field资格oracle版本化为五点四阶差分D₄(h)=[−f(2h)+8f(h)−8f(−h)+f(−2h)]/(12h)，仍h=1e−6、逐分量绝对门10⁻⁷、无K归一化，不改变连续field/AD/Newton/原模型/observer式18/控制/观测条件。它是资格计算方法的变更，尚未实施或执行；不得将当前矩阵组合诊断升级为资格PASS。原测量H/离散F的已声明资格保持。

## 修正与停门

固定诊断矩阵计算完成后，summary.json因numpy.int64未转Python int而写入失败，exit1。已按[累计小修2](P2_IMPLEMENTATION_CORRECTION02.md)保留源码前后与原始矩阵；只读归档从既有NPZ恢复summary，不重算。原缺失脚本墙钟为null，外部工具进程0.145563236s单独标注。[归档记录](../results/20261014_P2_implicit_FD_diagnosis01/archive_recovery.json)。累计2/3，剩1。

本次停点来自用户第二阶段第2节“不满足既定资格时停止并保存证据”与第9节“必须改变…冻结协议的重大问题，立即停止征询”。更换差分资格oracle须作明确裁决；没有擅自改变ε、门限、滤波式18或继续下游实验。完整P2仍部分完成，当前无四组真实控制响应。
