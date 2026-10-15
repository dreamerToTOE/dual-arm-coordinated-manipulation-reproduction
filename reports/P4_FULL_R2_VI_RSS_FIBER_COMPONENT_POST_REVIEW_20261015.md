# P4 R2：VI 六个 singular-fiber 节点实际运行独立复核

2026-10-15。结论：**6/6 固定节点通过，`PASS_COMPONENT_DISCRETE_ONLY`**。本复核仅读取已保存数组、位姿、Jacobian、谱、碰撞返回与过程日志，独立做矩阵运算及哈希核对；新增 FK/J、IK、NR、采样、碰撞和规划调用均为 0。原已绑定 CENTER review 未修改。

## 版本与保存证据

- Run：`results/p4_full/20261015_R2_VI_RSS_FIBER_COMPONENT01`。
- 科学源码提交：`b6e40a4ea71752f4959e6ab6724811637707a452`；runner SHA256：`baf3eba251f14f0b8dc5e7c1b98ea39f2d3261f2d10338877bf99a33deeb395b`。
- 冻结协议 SHA256：`4b491ce2be9d222e35a28c2609c3aac9284ca61b56b804dcdbf0790089fb03b2`。
- execution SHA256：`d164ccf903d5b3259db4710409537f62394c74b47163b09d0b828a496fbc64b7`；events SHA256：`6047d3f684b163c33810e5dd7a2f1e3bf28d48f98aab51acd4f27249cc927e6e`。
- 29 项去重后的 source/input/prior-execution 哈希逐一与当前文件相等；6 个子进程输入与各 candidate 的 VI/18角逐值相等，stdout 等于保存 collision 对象，stdout/stderr SHA 与 process_finished 记录全部相等，退出码均 0。
- 原 CENTER review 当前 SHA256 仍为 `f971a7726d6a885481e1e4b6672ec2f0bfc53d316b39e1aa0cf4cad9b5cc21c1`。

## 独立算术审查

按保存中心重新构成预注册数组：219 两侧各依次 θ/2、θ，643 两侧各 θ；仅指定臂 q4+=fraction·θ、q6−=fraction·θ。全部 6 个输入与保存执行值逐值相等，其余 16 角保持原值、q5=0，原中心未替换。

以原字面 grasp、保存 body Jacobian 独立构造 12×18 双闭环 Jacobian，再做线速度 mm→m 缩放 SVD；6 点全部得到 full12、passive11、designated5、other6。保存 physical Jacobian 另行重算的 full/passive 也是 12/11。与保存谱最大差 `2.665e−15`。保存分支集合均为 designated `[1,3]`、active1 `[1]`、other passive `[3]`；指定奇异腕不被伪赋唯一分支。原关节界重新按源字面 3.1416 计算，最小全18余量 `0.43239801390092225 rad`。

直接用保存三个位姿重算双闭环矩阵残差，最大平移 `9.094947017729282e−13 mm`、旋转矩阵元素差 `1.6653345369377348e−15`；与原 native/B 保存位姿比较的最大差为 `9.094947017729282e−13 mm / 1.7763568394002505e−15`。源碰撞 TCP 与保存独立 TCP 的最大差 `9.094947017729282e−13 mm / 3.3306690738754696e−16`，保存独立 TCP 与 candidate 数学位姿逐值一致。没有重新调用运动学模型。

| 原中心 | 半侧 | 保存原坐标全18叶距（rad） | `< h=0.0025` |
|---|---|---|---|
|219|负侧|0.001262431084826697；0.001262431084828895|通过|
|219|正侧|0.001371065015031822；0.001371065015029310|通过|
|643|负侧|0.0022820573713580885|通过|
|643|正侧|0.0023443484400707820|通过|

叶距全部由保存数组独立重算，与记录逐值相同；未 wrap、未使用原 source 的 0.05/0.35 提前返回规则。

6 个真实 VI native 源碰撞返回全部 `CHECKED / collision=false / native_result=0`；每个 133 个 PQP pair 返回码均 0，合计 **798 pair 查询**。所有输入/输出与 native 源策略完整保留。这仅覆盖原网格、pair 和 8mm tolerance，不能声称遗漏 pair、完整实体或连续路径无碰撞。

四个 endpoint 对应旧固定 active 弦的一阶 image residual 为 `6.877e−18 / 6.642e−18 / 9.605e−18 / 7.127e−18`；219 两个中点分别约 `5.739e−6 / 6.221e−6`。这是既存 physical Jacobian 上的诊断，符合 endpoint 由一阶条件构造的预期；不构成 regular→fiber 接入证据。

## 实际调用与预算

事件为 6 candidate_started、6 pre_collision、6 collision 子进程 started/finished、6 collision_result、6 candidate_finished、4 segment_finished，均完整。实际 6 构造；36 数学 arm FK/J，加适配器内部 18 次 TCP 对照 FK/J，合计 **54**；6 逻辑/6 native 碰撞查询，IK/NR/RNG/规划为 0，无未确定 FK/query 前缀。适配器内部 18 次由已哈希源码的每 VI query 三臂对照控制流及六份返回三臂 TCP 记录共同支持，未冒称另有逐调用观测事件。

实际墙钟 `1.1851480359982816 s`、CPU `1.1674419999999999 s`。原10份 execution 的实际值逐项相加再加本次，R2 共 **82.2954052690011 s wall / 32.175436 s CPU**；不得再次累加 execution 中的 cumulative 字段。

任务 B 初组868、Q2续验36、本次6，累计 **910/960 构造**。从 exact-center 后余额扣本次实际成本，余 **50 构造 / 125.48601753600087 s wall / 346.67282300000005 s CPU**。R2总预算余 **3517.704594730999 s wall / 7167.824564 s CPU**。原一次性 claim、B/Q2/center claim 均保留，不重置。

## 结论边界与下一项

本次是有证据的独立 RSS 重建内部 singular-fiber 离散组件资格，不是作者原生三臂 RBS，不是 regular↔fiber 接入或完整 RSS 规划资格。原 Q2 四半连接 `UNKNOWN` 不变；γ=0.2 未调整、正式规划调用仍 0，不将分段短叶或一阶相容冒充连续路径证书。

下一独立小阶段只准备旧 II18/III22/V8 共48个已数学合格 RSS 分支的真实 v3 source-policy 碰撞补检。其草案应刷新为本次后11份 execution 总账；仅改草案来源账目，不重做旧700目标/5600IK、不新选择样本，也不扣 VI B 的构造或专项预算。独立审查冻结后才允许单次执行。
