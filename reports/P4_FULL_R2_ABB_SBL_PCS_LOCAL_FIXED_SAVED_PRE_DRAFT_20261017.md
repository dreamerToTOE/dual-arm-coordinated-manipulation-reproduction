# D080 SBL_PCS 固定保存节点 local 资格 PRE-TASK 草案

2026-10-17。状态 `DRAFT_SAVED_INPUT_ONLY_NOT_FROZEN_NOT_RUN`。本独立 PRE 不修改已审 BUILD02 工程 PRE/driver/header/transform/builder/supervisor。

root 已批准正、负两项 lazy fixture，各 trace/plain，严格四进程合计 15 秒墙钟 / 30 秒 CPU，仍扣 R2 总额 3600/7200。当前仅从旧 CBi 完整离散合格路径读取原始保存字节与独立 POST（58152/58152），无模型计算、采样、identify、投影、编译或二进制运行。来源 queue 的旧 pending 标记原样保留；后续独立 POST 及每节点 qualified=true 是已完成证据，不能改写 queue。

## 固定输入与真实分支

正例固定原 queue edge0 的 node0→108：q12 原字节、role0、两节点真实 SBL ik=[3,0]。原 CBi edge0 是109节点的独立合格离散段；本次仅将其端点放入重建的 root/grow 树，实际执行原 SBL isPathValid 和递归 RBS。既有 CBi 成功不预判 SBL 成功；要求实际 nontrivial RBS dispatch>1、true、节点保留及 child valid=true。

负例固定 root node0→child359→grandchild360。node359/360 原 edge3 role1，真实 SBL ik=[0,3]；根仍原 root role0、ik=[3,0]。原 identify_state_ik 的静态映射明确 ik[0] 是被动 arm2 分支、ik[1] 是被动 arm1 分支，没有新增 identify。三节点各有已保存闭链、分支、限位和 aligned 源策略碰撞资格。root→359 是有意重建的 ancestry，不声称它是旧 CBi 原边或可行 SBL 边；双方两个真实分支自然不同，原 lazy guard 应不调 RBS，真实返回 false，原 removeMotion 递归退役 child+grandchild，根保留。不得改分支制造失败。

四条 schedule 顺序固定 positive trace、positive plain、negative trace、negative plain。每个进程一次必要原 setup，不重做13点 projection 观察；原 seed7、Range=.8、II、A01 完整 start/goal 保持。无 connect fixture，不保存路径、不 solve、不 retry。所有输入来源 SHA 与 JSON 指针保存在单独 draft JSON；request只裁去不参与执行的重复provenance/预期文字，完整证据保留于fixtures，用于单次原子write的紧凑request严格小于4096 bytes；最终协议只允许改显式冻结布尔，不更换节点、关节角、branch、role、顺序或阈值。

## 待独立判据

读取实际原返回与前后树、全部 trace/raw字节、live lifetime、parent/null-before-delete 与 recursive remove；正例最少2次RBS，负例0次RBS/2次remove。trace source started/completed 一一配对、原 stderr marker 与 JSON events 一致。plain/trace 比较语义结果、q12 binary64、分支、shadow角色、valid、父子身份和保存的文件/sidecar；时间、仅观察计数和事件序号分开保留。原 writer 在local不应触达，attempt空只能说明未见writer，不能证明写成功。

保留真实 false、异常、超时、缺文件、额外文件和所有partial trace；任一不符立即停止本固定清单，不换输入重跑。root冻结提交、BUILD02成功且独立POST后才运行。完成local独审并全额入账后，再另冻单次seed7原10秒trace solve（建议20wall/40CPU，尚未由本PRE授权）；connect仅由该solve自然观察，未观察到即保留缺项。

本项为 `RECONSTRUCTED_TREE_FIXTURE_ORIGINAL_SBL_METHOD_BODIES`，不代表连续碰撞、RSS、SBL全局成功、原作者原生输入直接成功或正式性能。D080 I–V 范围、原22500事实与D08018000义务保留；VI974/974只读存档。无P2/Isaac/正式规划或结题文档。
