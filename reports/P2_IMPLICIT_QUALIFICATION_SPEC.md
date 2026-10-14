# 隐式数值核与原闭环资格：首跑前声明

2026-10-14，用户批准隐式plant；输入eb2600a。原v1及所有失败不覆盖，新v2只版本化积分/授权/来源元数据。原数值/控制/观测/种子/指标/预算保持；修正已用1/3，余2。

## 顺序与固定输入

Gate N/D先由scripts/qualify_p2_implicit.py一次归档：

1. 36个已验收finite_differential输入（原qualification02的O/E/G/V/U/模式）仅用于新backend等价证明；不重新裁决contact模型。native G twist对canonical、native τ/hK/hB对原式9–11，逐分量1e−10。输入身份及原记录SHA保存。
2. A transport及C sliding的原fixture，O右扰动[.0002,−.0001,.0001,.03,−.02,.01]、G1右扰动[.0001,−.0001,.0001,−.01,.01,−.01]、G2反向、V=[.01,−.005,.003,.08,−.06,.04]、U1=[.004,−.002,.001,.03,−.02,.01]、U2=[−.003,.001,−.001,−.02,.015,−.01]；所有9个H组合。D/τ/hK/hB/h/external/internal/W对canonical逐分量1e−10；continuous f逐分量1e−7。全数据分force/moment及位姿/速度块记录，不混单位norm。
3. 上述A/C的tight-tight、pivot-pivot、pivot-sliding，native前向AD42与独立Python解析链，以及ε=1e−6中央差分42。FD采用Boost50位小数计算，避免K/I放大世界坐标相减舍入；不使用AD导数作FD、不除K、不变ε/1e−7绝对门。FD与native共享连续方程实现，故单独的canonical primal对照是必需的物理/算法依据，不把同源FD称为独立物理模型。此处不运行IESEKF。
4. 1个A扰动状态、pivot-pivot、dt1/3000孤立implicit步：保存δ/完整24残差，检查native Newton解在canonical field重算的r各分量≤1e−12；E increment与dtU、C保持，Solver≤12修正。该步不是控制trial。
5. transport/high_moment/sliding三个原初态，双pivot、U0、gravity开启，分别1/3000和1/6000积分固定5秒（6条无控制物理资格），每条120秒限。保存250Hz真实state/τ/hK/hB/h/external/internal及每次native batch求解诊断。逐步native SE3/finite/pad界不变；五秒terminal force≤1e−6N、moment≤1e−6Nm、linear≤1e−7m/s、angular≤1e−7rad/s。初态不解析重置、时长不延长，失败停止。
6. 三组coarse/fine在相同4ms输出点对照O、两侧raw contact h及internal h，max position≤5e−5m、angle≤5e−4rad、每force≤.05N、每moment≤.002Nm；均需上述terminal资格。这是无控制资格，不能替代原exp3/seed7完整95秒粗/半步控制资格。

原native fast evaluator只在本protocol pad有效域（angle每分量≤.15，norm≤sqrt3*.15）使用；代码拒绝norm>.30，覆盖上述有效域及资格有限扰动。原canonical π图域与source字节不改；不声称全图域compiled等价。

## Gate E/C与主实验

只有N/D通过，才执行已先声明tests/test_p2_estimator.py、test_p2_control_qualification.py、test_p2_observations_qualification.py；源码/输入/实际case/失败/墙钟另存。严格42维、right坐标、fresh stamp、原式18 Euler、固定prior/5iter、Schmidt/Joseph/reset及因果held input；高精度oracle不归一化替换物理Jacobian门。

组件资格通过后，runner先执行原30名单的exp3/seed7 coarse与一个fine（同clock真实物理事件），作为集成/完整halfstep资格且计入原预算，不再额外生成预检运输case。其后按原协议执行剩余主/代表/GT诊断。每个case含标定/settle/运输，120秒单case、7200秒总限，首套30/原81/实际74控制case上限不扩大。

失败/超时/非finite/3滤波nonconverged等按协议停止；只凭明确错误最多余2轮小修，完整保留源/运行/影响。不能改pose/force条件、参考、noise、时刻、threshold或observer预测取得结果。
