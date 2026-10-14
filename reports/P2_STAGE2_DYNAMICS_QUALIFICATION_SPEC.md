# P2 第二阶段独立动力学资格：首跑前固定

2026-10-14；所有输入/阈值在首跑前提交；不含控制器/滤波器运行，不是主试验。

1. 原始名义fixture O右扰动[.0003,-.0002,.0001,.04,-.03,.02]，两侧命令固定[.001,-.002,.001,.01,-.015,.003]及零。tight/pivot/sliding九对H，独立经典向量公式f_o=R f_e、m_o=R m_e+p×R f_e，与式12核对，误差每分量≤1e−10 N/Nm；内力投影每分量≤1e−9 N/Nm。不将双sliding要求成rank6。
2. K/B/Ba=0、双tight、初始速度零，一个1/3000秒积分步，与自由落体p=p0+.5 g dt²、v=g dt逐分量≤1e−10；不拿这个无接触合成检查冒充真实持件。
3. K/B/Ba/g=0，V=[.01,-.02,.03,.2,-.3,.4]；式16与独立Newton/Euler body方程逐分量≤1e−10，动能导数绝对值≤1e−10 W。不测试或宣称全软接触模型被动性。
4. 原JSON初态、原gravity/K/B/Ba、锁EE/控制关闭、固定5秒：transport主步、transport半步、高moment主步、sliding物块C主步，按此顺序。各run保存250Hz O/V/E/C/G、tau、hK/hB、external/internal、force/moment residual；终端力平衡≤1e−6N、力矩≤1e−6Nm、线速≤1e−7m/s、角速≤1e−7rad/s，逐分量。SE3/有限/pad界沿原protocol。任一失败马上停止后续，不延长、改初态或重置。
5. transport无控制主/半步在同一4ms时刻比较，max position≤5e−5m、orientation≤5e−4rad、每侧true internal force分量≤.05N、moment分量≤.002Nm。这是独立动力学资格；不能代替后来原exp3/seed7完整95秒多率闭环半步资格。

每个5秒资格run仍受120秒壁钟约束。全保留失败/源码/实际运行环境/配置SHA；原接触几何文件、冻结JSON不改。P2修正累计1/3，剩2；当前脚本首版设计不冒充修正，所有资格失败之后的修正须另存证据。此门通过才推进估计/控制实现和已有30case预算。
