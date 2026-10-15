# R2 ABB NR固定64输入C++数值移植资格 POST

日期：2026-10-15。状态：**PASS_FIXED64_NUMERICAL_TRANSFER**，有限数值移植资格通过；独立保存证据POST另外归档。原论文完整复现仍部分完成。

来源 `c68fa7605a94eb07f7588e850b95980b62bc0c8f`，协议 `configs/p4_full/r2_nr_abb_q1_qualification_v1.json`，唯一run `20261015_R2_NR_ABB_Q1_01`。命令：`python3 scripts/qualify_p4_full_r2_nr_abb_q1_draft.py --protocol configs/p4_full/r2_nr_abb_q1_qualification_v1.json`。没有换输入、筛成功、重跑、调阈值或修改原Python/已冻结C++数学内核。

固定II32+III32按旧顺序完整执行C++plain64→同binary trace64→原Python观测64，共**192派发/192完成**；64个C++最终候选再独立物理检查。64项plain/trace非计时完整结果精确一致，64项跨语言逐步门通过，64项原Python历史重放门通过；C++和Python各64/64 CONVERGED，64/64终态闭合和源机械界通过。无未完成尾项、观察器错误、运行时异常、超时或资产变动。

|证据|实际结果|
|---|---:|
|最终q跨语言最大逐角差|4.440892098500626e-16 rad|
|迭代q/实际落地delta最大差|8.881784197001252e-16 rad|
|约束位置g最大差|3.979039320256561e-13 mm|
|约束位置J最大差|4.547473508864641e-13 mm/rad|
|旋转g / J最大差|1.5168090037025878e-15 / 6.661338147750939e-16|
|奇异值最大差|3.183231456205249e-12|
|cutoff最大差|2.481541837659083e-24|
|独立终态最大位置残差|8.342067303601652e-7 mm|
|独立终态最大旋转矩阵残差|1.50461743064767e-9|
|最小机械限位余量|0.07996374640843196 rad|

原物理门仍1e-5mm/1e-5旋转矩阵，跨语言比较门按PRE固定。C++proposal与observed rounded delta分列，只比较同义落地差；不比较SVD U/V任意符号。通过仅限固定near64输入，不证明随机ambient空间投影能力或原KDL迭代轨迹。

实际资源 **7.05127794699365秒墙钟 / 7.9173490000000015秒CPU**，小于整次60/120帽；含启动、观测I/O、比较、终态和922资产后哈希。Python3.10.12、NumPy1.24.4，数值线程变量全部1；C++单目标g++11/-O1。存在被计入outer clock的common导入准备区间，SIGALRM在其后安装；没有在该区间调用模型。所有科学worker阶段受parent独立墙钟/live CPU硬帽，observer捕获回调异常不能吞parent终止。

真实事件记录Python原NR内部arm FK/J **864 started/864 completed**，独立终态metric **64/64**、内部arm FK/J **128/128**。C++ plain/trace内部FK/J与SVD started/completed **UNOBSERVED**，不把理论结构推算当实测。NR顶层次数由真实request和响应计，不按预算填满。0 IK/碰撞/RBS/规划/RNG/VI新候选/正式调用。

20 execution=17科学+3工程，逐自身实耗合359.4902552519934wall/309.65925300000004CPU秒，R2余3240.5097447480066wall/6890.340747CPU秒；新V6由实际execution独立生成，旧V5保持。VI974/974余0，正式Table I0/22500，211项全文义务不缩。

候选标记**RECONSTRUCTED_PHYSICAL_FULL_NR_CPP**：是原论文全链Jacobian/SVD方式的已合格物理实现移植，保留mm/rad未缩放、相对1e-12截止、10000次最大更新及原chart/限位；不是作者原KDL路径、原截零/近似π实现或性能基线。现阶段没有碰撞和RBS/回溯、NR规划资格。下一步保持原StateValidityCheckerNR/RRT_NR完整搜索/递归算法，在独立新stage以kdl::GD薄接缝调用此内核，先固定局部门，再单次有限起终点规划与完整独立路径检查。

原R1/R2失败、旧原始端点、原source exact历史PENDING、PCS路径独立PASS及VI Q2 UNKNOWN各自保持。不提前声称PCS优势、RSS全局成功、CCD或完整实体碰撞。P4后再写最终中文Word/PDF和双FR3适用分析，并将最新范围表交用户审查；不P2/Isaac。
