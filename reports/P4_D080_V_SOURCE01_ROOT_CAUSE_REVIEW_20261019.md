# D080 环境 V SOURCE01 失败根因审查（2026-10-19）

## 观察

失败执行的唯一 source 子进程已真实启动并收到完整请求。stdout 为：

```text
Robots initialized.
Debug:   RRT: Planner range detected to be 3.518361
Info:    RRT: Starting planning with 1 states already in datastructure
Solved in 0.249101s.
Logging path to files...
```

外层最终写入 `RuntimeError('III_SOURCE_SELF_REAPED_LIVE_GROUP_WORK_CAP')`。堆栈进入 `qualify_iii_rrt_pcs_source01_v1_draft.py:65` 的 `Budget.check()`，再进入 `build_p4_full_r2_abb_cbirrt_d_draft.py:109` 的 `/proc/*/stat` 扫描；同一检查由 SBL 兼容层的 SIGALRM handler 重新进入。原始 stderr、evidence、6 个里程点和 53 个 `temp.txt` 配置均保留。

## 根因判断

目前最有证据的解释是**我们自己的资源监督器存在 SIGALRM 重入缺陷**：周期性定时器在 `live_group_cpu()` 遍历 `/proc` 时再次调用 `Budget.check()`，造成非重入检查嵌套。异常发生在 source 输出已出现 `Solved` 之后的日志/回溯监督阶段，随后清理了仍未完成 transport 的子进程。这是 `OUR_SUPERVISOR_NUMERICAL_RESOURCE_GUARD_REENTRANCY`，不是原 RRT/PCS 数学或碰撞结论。

竞争解释仍保留：source 进程在写路径日志时本身可能尚未自然退出；现有证据不足以判断完整 source trace 是否还会继续写出目标节点。因此不能把 stdout 的求解提示升级为 source exact，也不能把 6 个里程点升级为路径。

## 修复路线（仅提出，未执行）

1. 为 `Budget.check()` 增加不可重入状态，并在读取 live group CPU 前阻塞 SIGALRM；检查退出后恢复原 signal mask。
2. 或者把周期性 SIGALRM 只用于设置“到期标志”，把实际 `/proc` 扫描和异常抛出放到主循环的非重入位置。
3. 保持 30 s/60 s、25 s/50 s 工作预算、原始 seed/range/goal bias、闭链/碰撞/限位和 source process/solve=1 门不变；修复不能把预算门放宽。
4. 对修复版本做静态独立审查与小型 supervisor-only 回归后，再申请新的单次 source 预算；不得使用本次已消耗的预算重跑。

该修复尚未构成科学运行，也未改变失败 POST、原始日志或 V43/V44 账本。
