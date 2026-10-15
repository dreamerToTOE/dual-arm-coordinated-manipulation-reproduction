# R2 ABB NR Q1 单目标工程 POST

日期：2026-10-15。状态：**BUILT_NOT_QUERIED / 仅工程通过**。

来源 `35246c34bac6d65b8002e06d97101694efe3e11d`，冻结协议 `configs/p4_full/r2_nr_abb_q1_engineering_v1.json`；唯一 claim、唯一构建均保留。单目标在45墙钟/90CPU上限内 exit0，实际 **8.80554415199731秒墙钟 / 12.280458秒CPU**；没有执行二进制、NR/FK/J/SVD、碰撞、随机数或规划。

命令为原冻结 Python builder 的 `--protocol` 入口；编译器 g++11，C++17、-O1/-g0，无fast-math。同一binary的plain/trace runtime flag不构成两次构建。binary SHA256 `d4a60b5e67ba19016f7ec54d3b9f4ea5bb76a1738fb0c169b27e9a04961e7687`；外部manifest SHA256 `fa02e29069a1723107d771f723b2d854bef4d7eddf0cb188e3ea95ac62fc45f1`。本run保留manifest与stdout/stderr原字节副本，未公开搬运作者源码或网格。

工程链的7个自有源、379编译器/库头字节前后相同，18个prior execution哈希匹配。编译警告仅driver矩阵JSON输出的缩进歧义：内层for逐元素push，随后在外层行循环中push row；源码实际括号层级符合矩阵行输出。保留警告，不为排版重编，不推断数值资格。

累计19 execution=16科学+3工程；逐自身实耗相加为 **352.43897730499975墙钟 /301.74190400000003 CPU秒**，R2原帽余3247.5610226950004/6898.258096秒。原V5快照保持；下一科学阶段冻结时读取完整19个execution，不能使用旧18条账。VI B974/974余0；正式Table I0/22500。

下一步是固定II32+III32输入的C++plain64→trace64→原Python完整观测64及64终态独立物理门，整项60墙钟/120CPU，待runner/worker独立审查与提交冻结。标签为RECONSTRUCTED物理NR C++移植；不冒称原作者KDL轨迹或速度基线。Q1后仍须原GD接缝、非平凡RBS、回溯与端到端规划资格；全部211项原文义务不缩。P4部分完成，不P2/Isaac。
