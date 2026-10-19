# D080 环境 V SOURCE01 V5 监督器修复候选阶段后审（2026-10-19）

本阶段只完成 V4 根因对应的版本化工程候选和 supervisor-only 回归，没有启动 V5 source process、没有发送 source request、没有调用 source solve、模型、碰撞、路径或正式统计。

## 结果

- V4 runner、V4 supervisor、V4 PRE、V4 原始执行目录、V43/V44 账本和 V4 前缀审查保持原字节。
- 新 V5 runner 仅增加 `Budget` 子类：`SIGALRM` 处理器在检查进行时登记 pending alarm；live-group CPU 的 `/proc` 扫描期间阻塞 `SIGALRM`；扫描结束后恢复原 mask。
- V5 保持 V4 的 seed=7、range=0.2、goal bias=0.05、solve=10 s、30/60 wall/CPU、25/50 working cap、单 source process/solve 和所有科学验收门。
- 13/13 静态/回归检查通过：Python 解析、guard AST、请求参数和预算一致性、未冻结/未授权协议、V5 supervisor 路径、V5 运行产物不存在，以及模拟嵌套 alarm 只触发一次 live CPU 扫描并恢复信号屏蔽。

证据：`reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_V5_SUPERVISOR_GUARD_STATIC_POST_20261019.json`。该文件明确 `personnel_independent=false`，表示这是当前 Codex 的工程静态后审，不冒充科学路径或人员独立 source 审查。

## 预算与科学状态

本阶段新增 source process/request/solve/model/collision/path/formal calls 均为 0；没有新增 R2 wall/CPU 账目。V4 的 1 次 source dispatch、`Solved` stdout、transport 失败和前缀不完整结论保持不变。V5 状态为 `ENGINEERING_CANDIDATE_NOT_AUTHORIZED`，必须先完成独立静态审查、root freeze、最新 prior 绑定并获得新的单次 source 预算，才可考虑运行。

## 根因边界

该修复只消除“监督器 SIGALRM 与 live CPU 扫描重入”的我方竞争解释，不能证明 source 会自然完成日志传输，不能把 V4 的 `Solved` 提示升级为 exact/path，也不改变“source 自身可能尚未写完输出”的竞争解释。

## 下一步

先由独立审查确认 V5 的 AST、冻结字段、哈希和无运行状态；审批后再决定是否运行一次新的 V5 source 入口。V5 运行若失败，保留所有原始证据并按 D079 根因规则处理；不重复使用 V4 配额，不启动 VI 或正式统计。
