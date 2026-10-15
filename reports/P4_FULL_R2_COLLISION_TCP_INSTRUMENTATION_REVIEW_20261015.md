# P4 R2：IV/V 碰撞 TCP 观测插桩根因与 v3 工程准备

日期：2026-10-15。范围：读取已保存端点结果、核对原作者源代码、编译独立观测修正版。新增 IK、NR、采样、碰撞查询、规划运行均为 **0**。本记录不能将任何原失败改判通过。

## 原结果保留

`results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/` 的 `IV_start.json`、`IV_goal.json`、`V_start.json`、`V_goal.json` 及相应 progress 日志原样保留。四端点均为 `UNKNOWN_COLLISION_QUALIFICATION`，原始端点闭链失败也保留。

| 已存端点 | v2 臂1 TCP 最大平移差 mm | v2 aligned 臂2差 mm | 原候选总数 | 已存最近 pre-collision 合格候选索引 |
|---|---:|---:|---:|---:|
| IV start | 1796.1723344647771 | 4.547473508864641e-13 | 75 | 22 |
| IV goal | 1537.7368575481096 | 4.547473508864641e-13 | 60 | 44 |
| V start | 1.999999999986585 | 4.547473508864641e-13 | 75 | 52 |
| V goal | 1.9999999999864713 | 4.547473508864641e-13 | 75 | 22 |

这些最近候选保持原主动关节、原解析分支，闭链最大平移残差为 4.55e-13 至 6.82e-13 mm。此处只是读取既有输出；未重新求解，也未重新进行碰撞资格。

## 可验证根因

原文件均在外部只读资产目录 `/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/`，不复制作者源文件或网格进入公共仓库。

1. **IV 是我方读取未赋值变量的观测错误。** `ckcComau2/validity_checkers/collisionDetection.cpp:61` 声明 `T7`，但 :147–152 的所有 `T7` 赋值均被注释。作者实际 rod 位姿用 :154–161 的 `Trod=T6+R6*[22,0,0]`，原碰撞查询也使用 `Trod`，不使用 `T7`。v2 插桩擅自把 `T7` 当作 TCP，读到了未初始化值。该证据不能称为作者原碰撞逻辑错误，更不能归因为论文数学错误。
2. **V 是我方混淆 mesh frame 与 physical TCP 的观测错误。** `ckcComau_industrialScene/validity_checkers/collisionDetection.cpp:147–152` 将 `T7` 设在 `T6+R6*[20,0,0]`，而已资格物理模型 `baselines/p4_full/analyze_comau_native_qualification.py:51–54` 使用工具长度 422.7 mm，即 22+400.7 mm。v2 在 `T7` 上再加 400.7 mm，只得到 420.7 mm，恰少 2 mm。作者 :154–161 另算 box 位姿，均无需更改。臂2 :258–263 的 `T72` 已含 22 mm，因此其 `T72+400.7` 观测本来正确。
3. 两环境的 source native 臂2小量世界坐标差、以及已有 aligned 基座变换规则保持 v2 历史定义。本次不改变这部分科研条件。

## 独立 v3 观测版本

新增 `scripts/build_p4_full_collision_adapter_v3.py`。原 v2 builder、Python adapter、manifest、binary 与 VI 的运行条件不改。

v3 只将采集行替换为：

```cpp
// IV
p4_pose(R6,Trod); p4_pose(R62,T72);
// V
p4_pose(R6,T6,422.7); p4_pose(R62,T72,400.7);
```

采集仍在原 `PQP_REAL tolerance = 8;` 之前，位置本身不是根因；错误来自所选变量和工具偏置。`p4_pose` 只读取原变量，并将结果写入我方观测容器，不写回源碰撞变量。

执行命令：

```bash
python3 scripts/build_p4_full_collision_adapter_v3.py
```

工程构建耗时 **3.419461395 wall s / 3.420515 CPU s**。4 个 IV/V native/aligned 编译均 exit 0。没有执行构建产物或发起科学查询。

新 manifest：`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json`。

- manifest SHA256：`c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388`
- v3 builder SHA256：`67ac61dfdabc5904720933dd62ec4b9809c22e3992e359601b7999dd3841f3d3`
- 原 v2 manifest SHA256：`9ed2e7c634e4c5d58698101571145960c96417c94f8ff0f546d7a637e0e1d302`
- 原 adapter SHA256：`b14c48231048498c9b3b77e90ad26fca2aaa7db54c1ef1eeda08a1453dcb5578`

manifest 复用全部不受影响的 v2 条目，只替换 IV/V 的四个工程产物。每条记录含原 source/mesh/binary hash、命令、stderr/stdout 日志、查询数 0、观测表达式和证据位置。

## 静态等价核对

对 IV/V 各 native/aligned 逐一验证：

- 去除 `p4_pose` 观测行后，v3 staged collisionDetection.cpp 与相应 v2 staged 文件**完全相同**。
- 过滤注释并规范化空白后，原活动 `PQP_Tolerance` 的全部参数与 v3 `p4_query` 参数逐项相等：IV 每版本 **82** 条，V 每版本 **87** 条。
- 原模型、网格、mesh/link frame、障碍、pair list、8 mm tolerance 和原查询返回逻辑不改变。未把注释或遗漏 pair 推断成安全。

因此本版本是我方观测实现修复，不是碰撞模型修正或标准放宽。现阶段仍须用冻结版本对已保存同分支候选作独立碰撞回放，才能确认观测与物理 FK 一致和端点 source-policy 资格。不得重跑全部任务 A，不得重建候选，不得将旧 UNKNOWN 覆盖。本工程准备不授权正式规划，也不提供完整实体几何或连续无碰撞证书。
