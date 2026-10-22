# P2 D082 V4 POST — 最终交付前五项修正（控制律验证 V4）

**状态**：`V4_COMPLETE`（14/14 正式 PASS + 1 项信息性诊断，不计入正式计数）。
本轮零长仿真、零 GT 反馈、零历史文件改动；仅新增 V4 脚本/JSON、最终报告与交付物。

- 分支 `reproduce-p2-numerical-simulation-20261018`，基线 `55afa59d`（V3 15/15 所在提交）
- 命令：`/usr/bin/python3.10 p2/tools/d082_control_verify_v4.py`（秒级，无长积分）
- 产物：`reviews/D082_CONTROL_VERIFICATION_V4.json`、`reports/final/*`

## 五项修正（对照最终交付审查意见）

| # | 要求 | V3 缺陷 | V4 修正 | 结果 |
|---|---|---|---|---|
| C1 | 零误差不动点在位姿反馈真实激活时重验 | V3_01 在 t=10 s 验证，`pose_active=False`，式(25) 分支被短路，U_P=0 是分支置零而非控制律性质 | V4_01 在 t=20 s（≥13 s）验证，断言 `pose_active` 且 U_F 通道同时激活，U_P 经 Eq.25 真实路径 | PASS，残差 0 m/s / 0 rad/s |
| C2 | 信息性诊断移出正式计数 | V3_14 无条件 `True` 却计入 15/15 | 标 `diagnostic: true`，summary 分列 `formal_total` 与 `diagnostics_excluded` | 14/14 formal + 1 diag |
| C3 | 单位分离 | V3 混写 "N/N·m"、"m/s rad/s"，残差为混合范数 | 内力(N)/力矩(N·m)、线(m/s)/角(rad/s) 全部分列；V4_11 线/角分别门控 | 见 JSON 各 `residual` 字典 |
| C4 | 内力 oracle 描述与实现一致 | V3 描述"独立 null-space oracle"过强：oracle 与控制器共用同一接触评估（H、W、零空间投影定义） | 描述更正为"控制器外部同接触重算，验证算术/符号/增益管道，非独立接触模型"；oracle 显式纳入 hB（断言零输入下 hB=0） | PASS，残差 0 m/s / 0 rad/s |
| C5 | 源码/数值结果/报告一致 | V3_12 描述 "force_off@5s, force_on@10s" 与协议（force_on=7 s, pose_on=13 s）不符 | V4_12 三时段断言：t=5 s 全关、t=10 s 仅力反馈、t=20 s 全开 | PASS |

## 数值结果（与 V3 的一致性）

- V4_02 注入内力：力 4.683e-01 N、力矩 1.751e-01 N·m（V3 混合范数 0.5，分解后自洽：0.468²+0.175² ≈ 0.25）。
- V4_03/04/06/08 的 U_F/U_P 分解与 V3 的混合范数一致（线 3.703e-04 m/s、角 3.005e-03 rad/s）。
- V4_D1 真实夹具内力：1.285e-13 N / 1.154e-14 N·m（V3 为混合 1.29e-13）。
- 所有门限不变；verdict 语义从 "15/15" 变为 "14/14 formal + 1 diagnostic excluded"。

## 报告一致性（C5 覆盖面）

`reports/final/P2_FINAL_REPORT.md` 的 §0（五项修正）、§5.4（V4 表）、§8（对照表 #18–21）、§10（交付清单）与本 JSON 同步；CSV `ORIGINAL_VS_APPROVED_VS_ACTUAL.csv` 行 18–21 同步。V3 脚本/JSON 保留不删。

## 未做

- 未跑任何新的闭环/长仿真（按要求）；
- 未改 `control.py`、协议、历史 JSON；
- 未触碰 P4。
