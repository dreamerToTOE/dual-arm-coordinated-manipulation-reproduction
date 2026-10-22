# P2 T04-B 95s PRE — 模式 B 完整单案例数值仿真

**授权**：Issue #35 T04-B 7.5s 验收（95s 授权）
**分支**：`reproduce-p2-numerical-simulation-20261018`

## 固定条件
- case11, exp3, seed=7, object A, transport, GT_control=False
- **估计器**: `ADAPTED_STABLE_PROPAGATION_V1`（StableRightIESEKF）
- plant: 原 native 隐式；controller: 原 PoseForceController
- Q/R/增益/传感器/域门/时钟/参考轨迹: 全部原值
- precalibration: 原样; settle: 原样 5 s; transport: 0→95 s
- 事件: 3, 7, 13, 23, 55, 76, 85, 95 s
- 墙钟: ≤ **600 s**（外部 timeout 900 s）

## 命令
```bash
/usr/bin/python3.10 p2/tools/t04_b_coupled.py \
  --confirm case11-exp3-seed7-A-modeB \
  --transport-limit-s 95 --wall-cap-s 600
```

## 停止条件
- `COMPLETE`: 到达 t=95 s 无失败
- `FAIL_STOP`: 域门/非收敛/数值失败
- `BUDGET_STOP`: 600 s 墙钟超限
- `INFRASTRUCTURE_FAIL`: 运行器崩溃

## 预期
- 3075 预测 / 1575 更新 (7.5s) → ~39000 预测 / ~20000 更新 (95s)
- 内力反馈 @ 7 s，位姿反馈 @ 13 s，robot2 视觉关闭 @ 76 s
- plant 集成率 ~4×（优化后），95s transport ≈ 475 s + settle ≈ 500 s
