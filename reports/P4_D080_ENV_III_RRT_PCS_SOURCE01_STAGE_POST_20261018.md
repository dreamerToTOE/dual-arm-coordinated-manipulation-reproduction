# D080 环境 III 首次真实 RRT+PCS source solve / V36

本阶段唯一真实求解，不重复II五条路径、III BUILD01及局部7正1拒绝。冻结提交ca984923，III/A01重建端点、seed7、range .8、goal bias .05、原采样盒/双锥/1200mm基距/500mm杆，内部原10秒；外30wall/60CPU、工作25/50。原作者RRT控制与R2修正运动学分开标记，端点为RECONSTRUCTED。

执行命令：`python3 scripts/p4_d080/supervise_iii_rrt_pcs_source01_v1_draft.py --protocol configs/p4_d080/iii_rrt_pcs_source01_v1.json`。

真实新增source solve=1；exact=1、approximate=0，内部solve 6.177099651秒。保存15里程点、615次identify及全部16原回溯（14true/2false）；原false和回退均保持。返回exact仅是候选，不计独立合格路径。完整原M保存物化得到649唯一节点、14边、648离散叶；独立数学/分支/限位/碰撞门尚未执行。本阶段无新独立模型调用，不声称连续无碰撞或PCS优势。

实际process exit0/reaped/空组/双EOF，唯一590字节compact请求后EOF；完整mixed stdout、stderr、result、PlannerData、原paths与17位回溯/identify均保留。保存独立POST25/25通过，证书`reports/P4_D080_ENV_III_RRT_PCS_SOURCE01_SAVED_INDEPENDENT_POST_20261018.json`；不是路径通过证书。

三观测保守包络费用9.899804176000325wall/9.415978999999998CPU，仅替换内部样本一次；V36=54execution（39科学账+15工程账），累计1145.4165708139924wall/971.307069CPU。原R2帽3600/7200不扩，余额仅上界2454.5834291860076wall/6228.692931CPU，历史未测持久化尾UNKNOWN保持。真实source solve累计7，不是7条合格路径。正式0/18000、VI974只读。

下一步完整649原节点的独立路径门，复用同判据原PCS数学loop、III模型和原native/aligned碰撞策略；不补点/截尾/重solve。V原RRT薄工程并行准备。RSS独立线原失败/UNKNOWN保持，无新RSS运行；不开展P2/Isaac/FR3或正式统计。
