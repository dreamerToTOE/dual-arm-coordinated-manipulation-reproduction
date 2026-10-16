# CBiRRT D P：双树保存路径提取 PRE 草案

2026-10-16。DRAFT_ONLY / NOT_FROZEN。纯 stdlib 提取器已对真实 S02 保存数组作一次只读物化，未 import 科学 runner、生成 P protocol/prior/claim、运行物理/碰撞/RBS/solve。原 S01 草案与本次修订前字节已分别保存于 `work/preserved_cbirrt_path_source01_draft_before_source02_20261016/` 和 `work/preserved_cbirrt_path_source02_before_cleanup_evidence_fix_20261016/`，另有最早提取器修订原件；不覆盖原失败。原 211 项义务、正式 Table I 0/22500、VI 974/974 余 0 保持。

`scripts/materialize_p4_full_r2_abb_cbirrt_d_path_draft.py` 只接受实际 S 完整响应与已绑定的原 A01 request。调用者另核实际 S02 execution/冻结协议/claim、原始 stdout/stderr/journal、来源 build 全链及人员独立实际 POST；本模块不从单个自报 status 授予 P 执行资格。模块没有 main、文件读写、模型、子进程或协议生成入口。真实 S02 execution SHA `c7cbd868da1cd9feb149bc057c4a63ff3e722b81123998e1a8cc5e8e1bab5906`，独立入口/保存 POST SHA `730dbb69ff3749975639dd9cad2fe1f31ca45cb2bf370c0470cfddd329d64412`；后者只核 transport，尚未核 P 物理路径。

原 solve 连接成功后先将 startMotion 或 goalMotion 退一 parent，再记录 connectionPoint。因此只用真实保存的 connectionStart/Goal，不补回已退节点、不从相同 q 猜 Motion、不将单 RRT 的 q 图门套到双树。完整 tree snapshot 中 Motion/state 身份必须唯一，parent 存在/同树/无环，root Motion/state/q 逐字吻合，固定原起终点要求两树各一根。

save2file 的 observed `save_source_mpaths` 与其完整返回两链须保留 binary64（包括 ±0）严格相同，且分别正是 connection 到 root 的完整 parent 链。`reverse(start mpath)+goal mpath` 逐 binary64 等于全部 milestones，首末原 A01 12 角不变。PlannerData 按实际 state 身份覆盖全部树 Motion，精确包含 start parent→child、goal child→parent 和真实桥，start/goal/root/tag 均核。不同 Motion 即使 q 相同仍保留；只有物理检查按完整 q12 binary64 去重，并保留共享节点的所有边分支约束。

提取器只消费原 save2file 真正完成的 state_reconstruct，保持每边原 role0 优先、失败后清 M 的 role1 fallback 次序和原 branch。全部成功/失败尝试及完整 Confs 保留。每条最终边必须实际 true 返回、原 M 完整、首末逐 binary64 等于真实相邻 Motion、原解析 branch 合法、full12 每叶 L2 严格 `<.05`。原 EXACT/save 已返回仍不能代替此门；任一边不完整就停止保留，不另跑 RBS、重构或补桥。

实际保存-only 结果位于 `work/cbirrt_d_source02_saved_materialize_20261016/full_queue.json`，SHA `38ce4780897186fadff49f15cec239008df237b519deb9d16ddbac73eedb852f`，summary 同目录。六个 Motion/五个 milestone，两链 `[[6,4,1],[5,3]]`，桥 6→5；q 相同的 Motion 7/5 身份分开。原五次尝试 true/true/false/true/true，全量 109/145/2/33/129 点；选中 true 边如下。原 false 29266 的主动 0/b3/M2 和随后的原 fallback 均留存。

|边|Motion|原实际主动/branch|选中 attempt / 原消费次序|完整 M 点数|最大 full12 叶距 rad|
|---|---|---|---|---:|---:|
|0|1→4|0/3|0 / [0]|109|.049872908712302065|
|1|4→6|0/3|1 / [1]|145|.049003850978920994|
|2 真桥|6→5|1/3|3 / [2,3]|33|.04288789195357552|
|3 goal 反向树边|5→3|1/3|4 / [4]|129|.034781812342410415|

共 416 边节点引用、413 唯一物理节点、412 叶，无物理查询。先完整提取全部真实节点；超过 2048 就保留全队列并拒绝科学执行，绝不只验前 2048。当前队列未超帽，但不因此自报物理通过。

P 执行体现已复制原已验证 PCS path 的完整数学/branch/限位/v3 persistent collision 科学循环，AST 一致，另加最新 charged ledger、exclusive 外层完整测量和安全 worker 登记/清理。完整 PRE 见 `P4_FULL_R2_ABB_CBIRRT_D_PATH_PRE_DRAFT_20261016.md`。120 秒墙钟/240 秒 CPU，原 R2 总帽不变；全部保存清理计入 child 范围，历史未测尾部 UNKNOWN，实际外层费用还须人员独立 POST。

下一步独立静态审查本完整源码和 PRE，再由 root 绑定真实 S02/实际最新 prior、冻结全 413 节点和原科学门、提交与唯一 P 执行。零新 source solve/RBS/随机采样，不重算原 S02。即使 P 离散全门通过，也不证明 CCD、完整实体杆/遗漏 pair 安全、RSS/PCS 优势或完整论文复现。
