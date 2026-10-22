# P2多率闭环首次运行声明

2026-10-14；前置：v3 N/D70/70和E/C35/35实际通过，仍无控制case。预算累计小修2/3余1；v1/v2/v3参数快照中的历史记账不覆盖，runtime ledger记当前预算。明确数值路线批准不自动改变observer式18。

新增整数clock组件仅接收新命令/模式，分别保存command、oldpublished、actual queue input；两个无ODE确定性资格在源冻结后先运行，若失败不启动case。之后第一条为原ID11 exp3/seed7 coarse完整95s，第二条仅原ID30 fine；不新增预检、不重复ID11。Gate H成功前其余28项不执行；任何非finite/滤波/形变/单case120s/整体7200s停止并留证。无自动增益调节/饱和/状态重置。

每case从原初态：75对静止视觉样本→右SE3平均C→独立lockedEE 5s真实settle→t0全新观测O/E1/E2初始化，V0/G声明；t0packet所有身份标consumed，不重复更新。calibration/settle/transport分开phase时间，同时保存global_case_time（0–5/5–10/10+t），C在运输t0前因果可用。主filter/controller不读true state或真实力；GT副本仅传感器/评分或原ID26–29明示诊断。

事件顺序：plant以旧actualU积分到事件整数tick→oldH真实contact/guard及新观测→observer以oldpublishedU及旧模式预测到该时刻、新模式生效后同戳观测分组update→新controller命令250Hz→两个publish时刻H选择最新因果命令→delayed queue于准确tick生效供下一物理步。滤波heartbeat/新测量间隔仍原Euler；无内部substep。每段reference从自身估计，13/23/55准确建立段，76之后最终hold；不跨组用own-reference error排名。

physical NativeModel逐1/3000(半步1/6000)完整耦合积分，batch只跨没有任何观测/控制/发布/延迟/模式事件的恒U interval。truepad逐物理步native验证，W秩/投影/finite每事件检查。estimate不能离开backend获资格的soft-pad域；采用原每分量rho .005m/theta .15rad门，分别保存ESTIMATOR_MODEL_PAD_DOMAIN_INVALID，不能与truepad异常混称。估计自由Log不投影/清零。原连续三次nonconverged停止，失败stop_report与完整P/最后F/Q/prior/H/K/reset/anchor NPZ保存。

日志：plant每250Hz完整真state/D/tau/hK/hB/raw/internal/W/sigma、reference和真实目标/跟踪/估计误差；sensor每样本完整value/R/身份/相位及采样/到达戳；estimator每heartbeat或新测量事件保存完整est state/P diagonal/预测间隔/创新/迭代增量与convergence/oldpublished input，每1s另存完整42×42 P，失败完整P/最后更新矩阵；command每250Hz完整UF/UP/cmd/estimated internal与model hK/hB/oldpublished/actual nextinput，事件publication/actuation全部存events。每次内部预测/更新仍由冻结cov门处理完整P，日志频率不是协方差降维。正常solver记录batch迭代/残差和末步delta/residual，失效保存last accepted与candidate完整evidence。gzip level1仅压缩，不删样本。统计只读这些日志，窗口未到记null。

主case95秒成功仍只是第一条完整资格轨迹；同源fine通过原position50µm/angle5e−4rad/raw及internal每force.05N/moment.002Nm之后才可运行余下20主矩阵/代表/诊断。switch5/25 guard不通过即保存该代表失败；不得延迟/重锚或新增低抓力控制。不得将GT诊断曲线合并主组或代替正式filter。
