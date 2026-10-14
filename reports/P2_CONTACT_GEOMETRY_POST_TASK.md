# P2 接触几何资格与协议冻结结果（2026-10-14）

我已依据用户批准的路线形成几何一致接触演化，并完成有限形变检查与协议冻结。当前完成的是原文审计、接触几何及实验协议，**完整P2控制与状态估计复现尚未完成，闭环实验0次**。

## 数学模型与差异

模型`p2.spatial_free_log_constraint.v1`用精确`D=E^-1OG`微分，固定`Ng=Ad(D^-1)N`，在EE原点自由twist lift中求解`N^T Jr^-1(a+VG)=0`。[完整推导显示版](P2_CONTACT_GEOMETRY_DERIVATION_RENDERED.md)明确标准mode小矩阵可逆域、自由Log初值保持及传递wrench零功。仅将算子改成标准LaTeX写法，资格metadata引用的原推导SHA及字节版本保留。
这属于用户批准的接触演化偏离；不是作者式15原样实现或已核实勘误。式9/10/11/12、式20/21/25、原K/B/KF/KP和H/W保持。原Rbar阻尼的有限形变近似、无物理预载释放、无全局稳定性/硬件证明继续列为限制。

## 实际资格证据

| 检查 | 数量/结论 |
|---|---|
| 有限形变完整导数、自由导数、spatial lift与零功 | 36/36 |
| 共同base/物体COM轴标签变换 | 6/6 |
| 自由基参数变化 | 2/2 |
| 双H维度/秩/内力投影/转置配对代数 | 9/9；转置恒等式不是完整物理wrench认证 |
| 固定时长有限几何积分/步长 | 9/9；tight空约束不作为收敛证据 |
| 预定模式切换accept、released/restored独立reject | 6/6；静态合成预载，无真实闭环测量 |

合计**68/68通过**。最大线性差分残差2.81893e−11m/s、角差分7.835997e−10rad/s；sliding自由漂移3.18535e−13m、pivot自由漂移3.29656e−12rad；传递wrench对自由lift功率残差≤8.68e−19W。测试小矩阵最小奇异值.99891637、最大条件数1.00108465；不把有限输入测试当无限输入域证据。

实际命令：

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/qualify_p2_contact_geometry.py --output-dir results/20261014_P2_contact_geometry_qualification02

科学源码commit51696a8；Python3.10.12/NumPy1.24.4/SciPy1.8.0。source/原始case SHA与当前文件核对相同；初稿参数/旧66名称与几何输入保持。
见[metadata](../results/20261014_P2_contact_geometry_qualification02/metadata.json)、[逐case](../results/20261014_P2_contact_geometry_qualification02/cases.jsonl)、[独立核验及分单位统计](../results/20261014_P2_contact_geometry_qualification02/independent_artifact_audit.json)。这些是预设运动学数学检查，不是物体惯性动力学、视觉触觉估计或控制曲线。

## 修正、失败和预算

原run01的66/66程序PASS原样保存，交付资格单独标INCOMPLETE：h差日志应为−KΔτ，恢复负例遗漏。[修正1](P2_CONTACT_GEOMETRY_CORRECTION01.md)修符号并追加两个独立无效预载输入；原66输入/门限不换，模型源SHA未变。
原临时解释器消失导致一次exit127，Python尚未启动、case0；失败另存，改用已验证同版本系统Python，不算新的算法修正。
P2小修累计**1/3，剩余2**；控制run仍0，81run上限不扩展、不在未来重新给3轮。

## 冻结协议和后续边界

[冻结JSON](../configs/p2_closed_loop_protocol_v1.json)与[冻结说明](P2_CLOSED_LOOP_FROZEN_PROTOCOL.md)保留主参数、五seed、路点/事件、exp2增益关闭前馈保留、exp4只模型K失配、观察时间戳/Q/C设计及性能判据。新增几何闭合、已批准偏离、切换新自由初态域和修正预算记账；[旧DRAFT](P2_CLOSED_LOOP_EXPERIMENT_PROTOCOL.md)保留。

协议`frozen=true`，`contact_geometry_qualified=true`；完整controller/IESEKF/独立动力学尚未实现，`executable=false`。下一阶段须实现和核验这些环节及原settle/全动力学半步门禁；本次数学积分不能替代真实控制响应。
P4所有科学文件和旧P2工作树保留；未运行P4/RSS、P3、Isaac/ROS。正式Word实验部分在真实闭环后形成，当前不填不存在的曲线和成功数字。
最终[冻结/保全核对](../results/20261014_P2_contact_geometry_qualification02/freeze_and_preservation_audit.json)20项通过：1023个受保护基线文件、旧P2八个未提交文件SHA保持；原P4工作树仍79cc871且干净。冻结JSON SHA256为`423f58ca7cfe13861586bb486dcfd6d19c5e3d82b69e40c3d403c90d7c871df3`。

## POST-TASK REPORT

- 科学目标：接触几何资格与最小实验协议冻结，已完成。
- 输入：用户明确模型批准、59260fa原文审计、ac9e35d初版及修正1。
- 实现：唯一spatial-free Log闭合与守门纯函数，无机器人平台/控制系统副作用。
- 验证：68固定数学case、原输入/源码/数据归档独立校验、原参数/判据继承和保全校验。
- 未完成：42维IESEKF、物体动力学闭环、原实验响应、摩擦/装配、正式结果Word。
- 风险：切换释放预载未建模，未来代表例可真实守门失败；不能重锚/改事件以强行通过。
- 下一步：按冻结协议进入独立实现阶段；本轮在冻结交付处结束，不自动P3。
