# CBiRRT D P：双树保存路径提取 PRE 草案

2026-10-16。DRAFT_ONLY；当前只准备纯 stdlib 保存数组提取源码，不 import 该源码、不读取尚未产生的 S raw、不生成 queue/protocol/prior/claim、不执行任何物理/碰撞/RBS/solve。原 211 项完整义务、正式 Table I 0/22500、VI 974/974 余0保持。

`scripts/materialize_p4_full_r2_abb_cbirrt_d_path_draft.py` 只接受实际 S 完整响应与已绑定的原 A01 request。其调用者必须另核 S execution、冻结协议/claim、原始 stdout/stderr/journal、来源 build 全链及人员独立实际 POST；本模块不从单个自报 status 授予 P 执行资格。没有 `__main__`、文件读取或输出、副作用 import、模型、子进程或协议生成入口。

原 solve 在连接成功后先将 startMotion 或 goalMotion 退一 parent，再记录 connectionPoint。因此仅使用真实保存的 connectionStart/Goal；不补回已退节点、不从相同 q 猜测 Motion、不把单 RRT 的 q 图门照搬到双树。

完整 tree snapshot 中每个 Motion/state 身份必须唯一，所有 parent 必须存在、同树且无环，root Motion/state/q 逐字吻合；固定原起终点要求两树各一个根。save2file 的 observed `save_source_mpaths` 与其完整返回保存的两链严格相同，每条都必须正是 connection 到 root 的完整 parent 链。`reverse(start mpath)+goal mpath` 必须逐 binary64 等于全部 milestones，首末原 A01 12角保持。

PlannerData 必须按实际 state 身份覆盖全部树 Motion，精确包含 start parent→child、goal child→parent 和实际 connectionStart→connectionGoal 的一条桥；start/goal/root/tag 逐项核对。不同 Motion 即使 q 相同仍保留，只有后续物理检查可以按完整12维 binary64 去重，共享节点所有边分支身份都要验证。

提取器只消费原 save2file 内真正完成的 state_reconstruct，保持每边原 role0 优先、失败后清 M 的 role1 fallback 次序和原 branch。全部成功与失败尝试及完整 Confs 均保存。每条最终边必须有实际 true 返回、完整原 M、首末逐 binary64等于其真实相邻 Motion、合法原解析 branch、full12 每叶 L2 严格 `<.05`。原 EXACT 即使 save2file 已返回，若一边没有合格 true M，也会停止并保留失败，不能另跑 RBS/重构或补桥。

未来 P 仍须单独冻结，拟沿用已验证 PCS path 的独立数学闭链/原机械限位/每边 branch 和 v3 原 discrete aligned collision 判据。数学门位置/旋转矩阵 maxabs 均1e-5，branch zero relative epsilon仍64倍binary64 epsilon，PQP 原8mm/原mesh和pair保持。native与aligned原结果均保留；不推称连续无碰撞、完整实心杆或遗漏pair安全。

P 最多120秒墙钟/240秒CPU，完整唯一物理节点最多2048；先提取全部真实节点，超帽就保留全队列并拒绝执行，不只验前2048。最终执行体应复用原已验证数学/分支及persistent v3 collision worker，加入届时最新charged ledger和独占外层完整测量。全部持久化和清理计帽，历史未测尾部仍UNKNOWN；外层费用须实际人员独立POST确认。当前草案没有物理执行体，不授权立即运行P。

下一步等待真实 S raw与独立保存审查，核此提取契约与实际字段；只有原每边实际true重构完整且队列合格，才准备具体P执行体与最新prior并独立静态审查、提交和root冻结。S nonexact、false、不完整或超预算不会触发第二次solve或源内补构造。原全部失败和源码保持。
