# R2 环境II首条完整空间 PCS 路径：独立保存证据 POST 复核

2026-10-15。结论：**PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH；独立 saved-only 复核2337/2337通过。** 新审查不调用任何FK/J、IK、NR、碰撞、RBS、RNG、规划或编译；只读取已保存的完整数组、物理姿态/分支记录、日志与哈希。

该结果使用 A01 `RECONSTRUCTED` 端点、R2版本化数值与原作者 RRT_PCS/RBS控制流。原作者舍入端点和R0/R1原始失败保持，不冒充原端点直接通过。范围为固定环境II、seed7、原Range2.6、goalBias.05、solve10秒和原main舍入采样框；不是完整P4或正式性能统计。

## 完整性、参数与真实执行

- 原solve仅一次，exact=true、approximate=false，`Exact solution`（code6），1个solution；完整树6节点/5边、原milestone4个，完整source有向路径 `[1,2,5,0]`。原identify返回日志11条，重构3次均true。
- 稠密边分别80、65、34个节点，公共端点按原binary64字节去重后**177个distinct节点**。全部节点、3条边和每条叶均检查；没有抽稀、补插值、修复、平滑或未执行尾部。2048资源止点未触发。
- source执行提交 `1a5b811b61be61dea80f8183f123379d167fd3f0`，整次source wall=0.2776374349996331秒、CPU=0.19540999999999997秒；driver内部solve计时0.016837364秒。观测和资格成本单独保存，均不能当论文正式速度结果。
- 独立路径资格执行提交 `b4cbbffa1db5d2a04f42b8eacab6c65b8188ae69`，wall=40.94035644100222秒、CPU=1.1020530000000002秒，低于冻结120wall/240CPU并扣既有R2总帽；本复核不重记这些成本。

## 闭链、限位与分支

177个节点的保存物理姿态按原300mm grasp和facing矩阵重新组合，独立核对保存残差计算及门限，未重新求FK。最大位置maxabs **3.410605131648481e-13mm**，最大旋转矩阵maxabs **4.440892098500626e-16**，均低于原1e-5门。所有12角按原degrees×3.1416/180机械界检查，无wrap/lift；最小限位余量 **0.035336181584417536rad**，出现在node165的第9角（零基索引8）。

| 原边 | 主动链索引 | 被动臂/分支 | 完整稠密节点数 | 最大相邻全12角L2/rad |
|---|---:|---|---:|---:|
| 0 | 0 | 臂2 / 3 | 80 | 0.04949053472601928 |
| 1 | 1 | 臂1 / 3 | 65 | 0.04617935003996265 |
| 2 | 0 | 臂2 / 0 | 34 | 0.048056299055741124 |

每个节点的全部原边引用均保留，不能只核对第一次出现时的分支。保存肩/肘/腕符号与8分支枚举一致，各边被动branch_set含原requested branch；本路径遇到的集合均为单值 `[0]` 或 `[3]`。按物理臂1/臂2顺序，起点分支为 `[0,3]`、终点为 `[3,0]`；原`identify`以主动角色记录的被动分支顺序与物理臂顺序不同，报告不混用。角色变化证明这条有限路径实际使用分划切换，不能据此推出固定链消融失败或PCS统计优势。

## 原离散碰撞策略与计账

全部177节点各执行一次v3 adapter，native与aligned分别保存177份完整原响应；二者均无碰撞，aligned每节点均真实CHECKED且TCP姿态一致。每variant每节点116次PQP查询，native20532、aligned20532，总 **41064**，全部query code为0。source mesh/pair/8mm tolerance/杆件建模策略保持；这不是完整实体杆件、遗漏pair或连续CCD证书。

保存started/completed计数完全配对：数学臂FK354/354、分支身份354/354、collision adapter177/177、adapter内部臂FK/J708/708。events、逐臂partial、完整math、原collision response与最终node文件逐项一致；所有原始响应在解释资格前已保存。无停止节点、无清理错误、无未检查尾部、无额外solve/VI构造/正式统计调用。

## 来源、前后哈希与产物

冻结协议、claim、execution、真实source result及其protocol/claim/build manifest/binary、A01端点、工程源/网格和全部**215个bound资产**，运行前/后及本复核时均一致；原端点精确首尾、原重构日志与result数组、source request均一致。source result无approx替代，全部milestone都属于保存原树的有向起终点路径。

- 复核JSON：`reports/P4_FULL_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW_20261015.json`，SHA256 `637d294b65a7baed72e08f326b232e9e7d98b284d81bd6f6790f382941ac2073`。
- 路径execution：SHA256 `f3b5a3b30a9067c1b92a069edf4a2ac72acb3b0f378e63fc486c73399f837c97`。
- 冻结路径协议：SHA256 `2ff16d0958675a5a357a7f253b2357ba393fc48d770bbbe515cd5ad2a46bccf7`。
- 路径runner：SHA256 `bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865`。
- source execution：SHA256 `b64ce8eef7a6456ea7f082ed1ef94f63d3abaebac06baa068de37b13c79fb7d3`。
- stdlib-only独立复核脚本保存在恢复工作目录 `work/recovery_20261015/audit_abb_rrt_path_saved.py`，SHA256 `782875ef7a30f9286182e77f4f251325c7cd40626aad1540325fc9d175020f12`；未导入科学模块。

本阶段取得一条合格空间起终点路径；其他环境、NR/RSS完整规划、三规划器对照、原文全部图表/统计、PCS复杂场景与固定被动链消融仍需逐项完成。Table I正式次数仍0/22500，完整211项义务保留，不自动进入P2或Isaac。
