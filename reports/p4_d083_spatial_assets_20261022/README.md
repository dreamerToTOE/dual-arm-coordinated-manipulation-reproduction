# D083 Stage A — 空间保存轨迹可视化（2026-10-22版本）

## 已完成资产

- `fig_A1_environment_II_saved_PCS_NR.png/.pdf`：环境II原RRT/PCS177点与RRT/NR393点，真实保存起点/中点/终点、两臂TCP轨迹、原CAD表面与原障碍。
- `fig_A2_environment_III_narrow_passage_v2.png/.pdf`：环境III649点的起点/中点/终点、原上下锥形障碍。v2仅修图边距；原A2及原manifest保留。
- `fig_A3_environment_III_four_switch_frames.png/.pdf`：四次切换各自前一节点/共享里程点/后一节点，共12幅真实构型。
- `fig_A4_environment_III_roles_and_evidence.png/.pdf`：14条最终边的主动角色、保存闭链残差、原native TCP差异曲线。
- `fig_A5_spatial_saved_trajectories.png/.pdf`：实际保存物体中点轨迹、PCS关节坐标；线段仅连接保存状态作显示。
- `environment_III_saved_states.gif`：36个保存状态，含所有切换前后节点；任意播放时长，无动力学、物理速度或连续安全主张。

对应原始导出及manifest：`results/20261022_D083_spatial_visualization01/`。三个CSV按真实源边顺序导出；NR的原唯一节点队列并非路径顺序，绘图使用`edge.node_ids`，未错误地按节点ID排序。每行保留源node_id、12q、两TCP、保存资格指标。原始科研输入未改动，作者私有`.tris`不复制到交付目录。

## 数值与证据边界

| 保存路径 | 节点/叶 | 全12q路径长/rad | 最大叶距/rad | 最小原限位余量/rad | 保存位置闭链最大/mm | 保存旋转矩阵最大差 |
|---|---:|---:|---:|---:|---:|---:|
| II RRT/PCS |177/176|6.976979771878481|0.04949053472601928|0.035336181584417536|3.410605131648481e-13|4.440892098500626e-16|
| II RRT/NR |393/392|14.266406302141537|0.0478001489336342|0.046633132713711944|9.793997321594361e-06|3.0701365727470176e-08|
| III RRT/PCS |649/648|22.634836624258902|0.04995648687917435|0.19440000000000035|4.547473508864641e-13|4.468647674116255e-15|

这些是三条既有路径的描述，不能解释为PCS成功率或速度优于NR。所有资格继承原独立保存证书；渲染仅复核其数据绑定，不重新资格。原始闭链/碰撞/限位容差未更改。

III四次角色切换在零基源节点179、248、392、492，对应一基最终边3→4、4→5、7→8、9→10，主动臂A1→A2→A1→A2→A1。共享节点本身不改变构型，角色描述入边与出边的主动/被动选择，不是瞬时物理动作。完整角色序列：`[0,0,0,1,0,0,0,1,1,0,0,0,0,0]`。

III649/649 aligned TCP通过、0/649 native TCP通过。沿用`RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY`：不升级native几何等价、CCD、最小净空、实体杆表面、遗漏碰撞对或动态安全。杆件以两TCP之间线字形显示，线宽不是材料表面证书。上下锥体使用原`cone.tris`：下锥恒等变换，上锥`Rx(3.14)`及`[0,0,790]mm`；II障碍使用原`obs.tris`在原三个位置。

## 复现命令

在仓库根目录，以系统Python3、NumPy、Matplotlib、Pillow运行。`--mesh-root`替换为本机合法持有、SHA与保存证据一致的作者`CKCplanning/simulator`目录。作者源commit为`909bd72fff778aca8682c96f9eb86ae4eb75557b`；本地已确认目录如下。程序拒绝覆盖旧结果。

```bash
python3 scripts/p4_d083/render_spatial.py \
  --output work/d083_spatial_replay01/data \
  --figures work/d083_spatial_replay01/figures \
  --mesh-root /home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning/simulator \
  --animation-frames 24

python3 scripts/p4_d083/build_spatial_supplement.py \
  --data work/d083_spatial_replay01/data \
  --figures work/d083_spatial_replay01/figures \
  --mesh-root /home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning/simulator
```

首命令生成A1–A4/GIF/CSV，第二命令生成A2v2/A5，并添加`report_figures`，保留`manifest_render_original.json`。GIF实际帧数除预选24点外还加入所有四次切换邻点，因此为36。报告选A2v2；原A2是保留的图边距前稿。

## 工作量与验证

主生成真实wall36.996203220005555秒、进程CPU59.117752015秒；主manifest内2,438次逐臂渲染FK，仅用于显示TCP与保存姿态相符，最大差2.8421709430404007e-13mm、旋转矩阵3.3306690738754696e-16。补图wall4.192742147002718秒、CPU6.2637816299999995秒；6次逐臂渲染FK，最大TCP平移差1.1368683772161603e-13mm。两次成功生成合计wall41.188945367008273秒、CPU65.381533645秒。它们不是规划耗时或新增资格成本。

两个早期入口因NR队列schema与`_collision_raw.json`命名差异停止，原错误说明分别保留`ENGINEERING_ATTEMPT01.md`/`02.md`。每次已完成II PCS177点的渲染FK（354逐臂），未生成数据/图片；其进程CPU未独立记录，不并入上述成功生成总成本。全阶段新增planner/IK/NR/RBS/collision查询均为0；包括两次入口前缀及补图的逐臂渲染FK总计3,152。

最终只读复核：主manifest的3,682输入hash及全部18项原派生输出、补图输入/4输出hash、保留manifest与补图manifesthash均一致，三个CSV的行数/唯一源节点177/393/649。主manifest、补图manifest及原始manifest各自留存；根代理另作人员独立保存复核。
