# P2-T02 PRE — SE(3)、接触与抓取数学复核（原版回归基线）

**任务**：`p2/tasks/P2_T02_MATH_CONTACT.md`（G1 门）
**分支**：`reproduce-p2-numerical-simulation-20261018`，起点 `ca01bdb1`
**前置**：T01 审查通过（Issue #35，2026-10-19）；T01 数学协议已按裁决修订（Van Loan `Q_d = S Φᵀ` 等）
**本轮性质**：**只读数学复核 + 建立未优化回归基线**。零控制案例、零闭环、零 plant 长时间积分、零源码修改。

---

## 1. 范围

复核对象（以现有代码为主，不重写）：

| 论文 | 复核内容 | 代码 |
|---|---|---|
| (1)–(6) | Exp/Log、SE(3) 复合/逆、Adjoint 及其同态/逆/指数恒等式 | `contact_geometry.py` |
| (7)–(9) | 弹性位移、刚度本构、能量正定 | 同上 + `mechanics.py` |
| (10)–(11) | 相对 twist（含 `R̄` 近似）、阻尼本构 | `mechanics.py` |
| (12) | W 的构造、wrench 坐标变换、虚功一致 | `mechanics.py` |
| (15) | 印刷式 vs `p2.spatial_free_log_constraint.v1` 的差异（含反例） | `contact_geometry.grasp_rate` |
| (17) | 6 类观测的解析 Jacobian vs 独立有限差分 | `estimator.py` |
| (18) | 现有右 Euler 一步 map 的**右误差 FD** 与 `F` 对照 | `estimator.prediction_linearization` |
| (20) | 内部 wrench 投影的幂等/零功/完备性 | `mechanics.mechanics` |
| H | tight/pivot/sliding 选择矩阵与零空间 | `contact_geometry.selection` |

另需复核的边界/异常：小角度（1e-9…1e-4）、接近 π（π−1e-3、π−1e-5、π−1e-7 的域门）、非 SE(3) 输入拒绝、pad 域门阈值（5 mm / 0.15 rad）。

## 2. 预期输出

| 文件 | 内容 |
|---|---|
| `p2/reviews/T02_PRE.md` | 本文件 |
| `p2/reviews/T02_MATH_AUDIT.json` | 逐项检查：名称、pass/fail/deviation、误差、容差、单位、证据 |
| `p2/reviews/T02_MATH_BASELINE.json` | **未优化基线**：源码 SHA256 + 一组固定输入的黄金数值，供 T01-E 等价性对照 |
| `p2/reviews/T02_POST.md` | 结论、通过/失败清单、仍存疑问、T01-E 准入判断 |
| `p2/reviews/T02_REPORT.md` + `p2/reviews/figures/*.png` | P2 自有渲染器生成的中文报告（不依赖 P4） |
| `p2/tools/t02_math_audit.py`、`p2/tools/p2_md_report.py`、`p2/tools/t02_report.py` | 可复跑脚本 |
| `p2/reviews/LEGACY_REPORT_PATH.md` | 三个 P4 依赖脚本的 `LEGACY_REPORT_PATH_UNUSABLE` 登记（原字节保留） |

## 3. 判定口径

- `PASS`：数学性质在给定容差内成立。
- `FAIL`：应当成立但不成立 → 视为代码问题，需单独立项，不得在 T02 内静默修。
- `DEVIATION_CONFIRMED`：已知的论文近似或已批准偏离，本轮只做**量化确认**，不算 FAIL。
- `NOT_APPLICABLE`：该性质对当前实现无定义（例如印刷式 (15) 未被实现）。

容差：代数恒等式 `1e-12`（相对 `max(1,‖·‖∞)`）；有限差分 `1e-6`（相对）；随机状态数 10；
固定随机种子 `20261019`（PCG64），所有输入可复算。

## 4. 计算预算

| 项 | 预算 |
|---|---|
| 总墙钟 | **≤ 180 s** |
| 单项 | ≤ 20 s |
| 长积分 | **0**（不做 5 s plant 积分） |
| 闭环/控制 | **0** |
| 随机状态 | 10 个固定种子状态 |
| FD 列数 | 42（预测 F）、6×6（观测 H，含扰动态） |

## 5. 验收条件

- 每个复核项都有独立记录（通过/失败/偏离），不得只给总数。
- 至少覆盖：Exp/Log 往返（随机/小角/近 π）、Ad 同态与逆、Ad(Exp)=expm(ad)、wrench 功率不变、
  刚度/阻尼本构、W 结构与虚功、投影幂等与零功、三种模式的 H/N、式(15) 反例、
  现有 `F` 的右误差 FD、6 类观测 H 的 FD。
- 旧失败记录不被修改；不新增对旧结果的改写。
- 基线 JSON 含源码 SHA256 与黄金数值，能被 T01-E 直接用作等价性 oracle。
- 状态最多 `MATH_PASS`，**不得**声称论文控制实验成功。

## 6. 停止条件

- 出现 `FAIL`：记录、隔离、上报，不在 T02 内修改源码。
- 近 π 边界行为与代码域门冲突：记录冲突，交裁决，不改域门。
- 预算超限：停止该项，记 `BUDGET_STOP`，不追加。
- 发现必须改连续模型才能通过某项：停止并上报，不擅自改。
