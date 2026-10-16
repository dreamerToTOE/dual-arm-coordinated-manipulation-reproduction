# D64 runner 独立静态审查

2026-10-16。nr_path_prepare 与 D64 实现者分离；38/38 项已完成静态检查通过，无阻塞。绑定runner `390be3a6e9e0c2431609d699e8393bf2d6bb22ac90deec49086ec3e60a65307d`，PRE `b7d72f8ce352cf03ce98203ca6d15697793fa8eb8328904f82058c59bcb9da13`。本报告仅复记已经完成的只读审查，0runner import/describe/validate/模型/二进制/编译/claim/prior快照。

固定四A01端点、16context、两源版本×plain/trace×两环境共8进程，每进程8请求，共64真实距离接口。32trace原函数entry/return可观察，32plain内部保持UNOBSERVED。原错公式role1与四唯一非零self反例必须复现，D修复版两role核独立六维L2、严格0对角与交换对称；role0跨版本和32组plain/trace逐binary64一致，全部state不变。

construction metadata可在每response重复，但raw序列仅每进程计一次，且严格entered/completed、id1、空args/result。每request重置trace id；最终raw必须恰4mesh_load和32activeDistance entry/return，plain无trace。8个CBi直接RNG成员初始化仅结构性计数，库内部actual constructor/seed draw保持UNOBSERVED。双raw stream保留path/SHA/长度、非marker诊断原字节，EOF/异常exit/额外stdout/trace尾不匹配均拒绝通过。未登记constructor前缀也保留、计raw并标UNKNOWN。

逐PID live CPU加self/reaped、20ms guard、启动/关闭group检查、15wall/30CPU最终帽及hash保全尾一致；异常后先kill所有活跃group再drain/reap，不重发request。PRE的“模型建树”仅指碰撞几何/PQP BVH构建，不是planner搜索树或碰撞查询。

本审查只支持进入实际BUILD/prior绑定和root冻结，不证明真实距离输出、路径、规划或完整论文。最终协议须使用实际合格D BUILD01、完整最新prior与独立协议审查；原H失败、VI974/974、Table I0/22500和211义务保持。明细及全部SHA见同名JSON。
