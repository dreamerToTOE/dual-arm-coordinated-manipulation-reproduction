# D080 环境 V：RRT+PCS SOURCE01 V5 监督器修复候选 PRE（2026-10-19）

## 任务边界

本文件只冻结 V4 失败后发现的资源监督器重入缺陷的工程修复候选。V4 的 source 进程、stdout/stderr、6 个里程点、53 个临时配置、失败后审查、V43/V44 账本和前缀审查全部只读保留。V5 尚未启动 source process、source request 或 solve，也不占用新的 source 预算。

科学输入沿用 V4：环境 V、RRT+PCS、A02 重建端点、seed=7、range=0.2 rad、goal bias=0.05、单次 solve=10 s、外层 30 s wall/60 s CPU、工作保留 25 s/50 s。原始闭链、分支、限位、碰撞、安全带、路径回溯和 `source exact`/`approximate` 分界不变。

## 根因与修复

V4 在 source 已输出 `Solved in 0.249101s.` 后的 transport/trace 阶段触发 `III_SOURCE_SELF_REAPED_LIVE_GROUP_WORK_CAP`。当前最有证据的根因为 `SIGALRM` 处理器进入 `Budget.check()` 时，`/proc/*/stat` live-group CPU 扫描又收到周期信号，造成资源检查重入并清理尚未完成输出的 source 子进程。竞争解释“source 自身尚未完成日志写出”仍保留。

V5 只增加工程保护：`Budget.check()` 设置不可重入标志，并在 live-group CPU 扫描期间阻塞 `SIGALRM`；处理器在检查进行时只登记 pending alarm，不进入第二次扫描。V5 不改变 wall/CPU 上限，不改变子进程数量、请求数量、模型、随机条件或科学验收门。

## 资格门

当前只允许：Python 解析、AST/源码静态审查、信号重入模拟和冻结文件哈希检查。静态通过不代表 source transport、source exact、完整路径或连续无碰撞通过。

若要运行 V5 source，必须先完成独立静态 POST、root freeze、最新 prior 绑定，并另行批准新的单次 source process/solve 预算。不得使用 V4 已消耗的调用重试，也不得把 V5 候选当作正式统计样本。

## 预期证据

- `scripts/p4_d080/qualify_v_rrt_pcs_source01_v5_draft.py`：V4 科学入口的版本化 guarded runner；
- `scripts/p4_d080/supervise_v_rrt_pcs_source01_v5_draft.py`：唯一外层 GNUtime 入口；
- `configs/p4_d080/v_rrt_pcs_source01_v5_draft.json`：未冻结、未授权执行的协议草案；
- `scripts/p4_d080/check_v_rrt_pcs_source01_v5_guard.py`：只做静态与 supervisor-only 回归；
- `reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_V5_SUPERVISOR_GUARD_STATIC_POST_20261019.json`：独立静态结果。

状态词：`ENGINEERING_CANDIDATE_NOT_AUTHORIZED`。本阶段新增 source/solve/model/collision/path/formal calls 均为 0，R2 账本不变。
