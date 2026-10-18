# D080 环境 V：固定 PCS 局部请求完成，物理资格待验

冻结提交 `7bf8afb784de429e87e2a4bef9abbcd0361d6409`，协议 `configs/p4_d080/v_pcs_local01_v1.json` SHA `e2a2388bc37f3ddd0347c9bf6a889976251c19eec922194940d239ba06a9f311`。本次唯一执行原 36 public 请求、38 stdout JSON，未换节点/分支、未采样、未调用 planner/solve。

## 实际新增结果

trace/plain 两进程均 exit 0、已 reap、组空、双 EOF；全结果、binary64 数值、观察记录和计数一致。人员独立保存 POST 194/194，仅证明 source/transport/语义及费用，不证明独立 Comau 物理或路径资格。证书 SHA `06c1a4c82db1accd7900b26e78c7bc84ebed33948e0b7d1d734aef877e00ac49`。原 execution SHA `a0549cd8207b0a4c16e5adb71aab0f063859458a803916ba72db287e419d7985` 不改写。

以下是每份程序的结果，两份不能当作独立科学重复：

| 请求 | 固定数量 | 实际结果 |
|---|---:|---|
| identify | 2 | start `[3,3]`，goal `[1,3]` |
| public project | 8 | 7 true、1 false |
| public RBS | 4 | 3 false、1 依赖失败未执行 |
| public reconstruct | 4 | 3 false、1 依赖失败未执行；保存部分路径 14/3/3 节点 |

每模式实际 project（含递归）42、RBS 29、reconstruct 29、isValid 34、collision 34、PQP 2958；最大 RBS 深度 4。完整保存队列仍 24 个唯一节点，包含投影成功点、内部合法点、失败回溯素材和原碰撞诊断点；不能将 false 根内 true 叶当作公有连接通过。

## 原 false 的保存证据

`start_role0_minus` 的被动 arm2 branch3 原 IK 返回 false，其 RBS/回溯依赖未执行；该 IK 内部具体拒绝条件未观察，保持 UNKNOWN。

另三条 RBS 和对应回溯各自投影成功后，被原 source 碰撞谓词拒绝：start role1 为 `conveyor–box`（pair86），goal role0 为 `chassis–box`（pair73），goal role1 为 `chassis–EE2`（pair72）。此时不能认定独立物理碰撞已证实，也不能归因论文或 RBS 数学错误；须独立核闭链、真实分支、原限位、TCP、87 pair 和箱体姿态。未改变 ±.05 输入或原 .05/150 连接判据。

## 费用与当前账本

raw GNUtime、外单调时钟/reaped CPU、内部 receipt 三观测按原 Decimal 包络计费：12.661639838999472 秒墙钟 / 8.950921 秒 CPU，原本项 30/60 帽内。保存证书只替换一次内部样本，V33 共 51 execution（37 科学账、14 工程账），累计 1103.9938663219941 秒墙钟 / 923.983153 秒 CPU；R2 总帽 3600/7200 保持，余额仅上界 2496.006133678006/6276.016847，历史未测尾 UNKNOWN 保留。

211 项表增至 228 列，前 224 列逐值保留：`reports/P4_D080_V_PCS_LOCAL01_ORIGINAL_VS_APPROVED_VS_ACTUAL_20261018.csv/.md`。source solve 累计仍 6、此次新增 0；正式 0/18,000，VI 974/974 只读，II 五条旧合格路径未重跑。

下一项将冻结原 24 节点的独立 Comau 物理资格（拟 60wall/120CPU，扣原 R2 余额），检查原失败及成功素材后再决定规划入口的最早未通过门。V 端到端尚无合格路径；III/IV 与 RSS 独立推进，正式成本 pilot/18,000 次预算仍在其后。无 P2、Isaac、FR3 新实验或结题。
