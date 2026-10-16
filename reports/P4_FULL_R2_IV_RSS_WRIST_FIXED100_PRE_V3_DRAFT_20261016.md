# P4 R2 环境 IV fixed100：精确关节界表示恢复 PRE v3

2026-10-16。仅新版本工程资格恢复；旧 v1/v2 源码、PRE、冻结协议、first01 失败、原始输入和所有输出原字节保留。当前未冻结、未执行、未编译。本文件不授权新采样设计、额外时间或大规模规划。

## 已确认的 first01 停止机制

`20261015_R2_IV_RSS_WRIST_FIXED100_01` 在运行前几何/界一致性 guard 停止：`RUNTIME_GEOMETRY_OR_SOURCE_LIMITS_CHANGED`。自身 wall=0.03671536999991076s、CPU=0.036766999999999994s；0 target、0数学 FK/J、0 K派发/返回、0 IK/碰撞/NR/RBS/RNG/solve，800条原分母全未执行。该失败属于我们资格入口把两种等价十进制表达式要求浮点逐值相等的实现问题，不是机器人模型变化、原IK失败或论文数学反例。

R1原metadata把q1原界写成 literal `[-3.1416,3.1416]`；既有 `physical.source_limits` 保留 degree×3.1416/180 的逐步binary64运算，对±180得 `±3.1415999999999995`。两者每侧相差1 ULP=4.440892098500626e-16rad：literal正值hex `0x1.921ff2e48e8a7p+1`，runtime正值 `0x1.921ff2e48e8a6p+1`。其余五关节十个边值逐bit相同；两臂复用同原界。基座、抓持和原Comau几何不变。旧guard正确停止并保留记录；不得删除、覆盖或将first01改为通过。

## 允许的最小新版本修复

新 `scripts/qualify_p4_full_r2_iv_rss_wrist_fixed100_v3.py` 使用独占 run02/新claim，分类继续为 RECONSTRUCTED / IV-SOURCE-WRIST-ONLY / FIXED-MATH-COMPONENT。在协议额外冻结 `geometry.source_limit_representations`，分别保存R1原literal界、runtime degree×原3.1416/180六关节界及完整12关节界。原metadata自身仍精确检查；运行前 guard 对完整12 runtime界作exact equality，不使用allclose、epsilon、门限放宽或自动修角。

真实候选 `bounds=physical.source_limits('IV')` 与 `legal=np.all((bounds[:,0]<=q)&(q<=bounds[:,1]))` 保持原字节/AST，不修改 actual validity gate。被动q5=0、其余五角原binary64、100原R1目标、sample0..99/branch0..7的800编号、原模式/基座/几何/抓持、原解析根和所有数学/rank/branch判据不变。除 run入口的表示guard 外，六个科学函数 fixed_inputs/rank_data/cached_closure/fk/native/native_prefix_accounting 与 v2 AST完全相同；run循环体及全部科学调用/判据也保持原样。

## 同一共享预算，不重新发放额度

first01与run02合计仍限30秒wall/60秒CPU，100固定目标/800 K及100+A≤900数学FK/J。first01零模型查询，因而run02保留同一未执行清单；共享时间必须扣first01自身成本。run02单项硬帽精确为 wall=29.96328463000009s、CPU=59.963233s，均继续受R2总3600/7200约束。`shared_budget_state` 每次describe/validate校验first01确为精确零query guard STOP、协议/claim/输入前后hash不变，否则拒绝生成新协议。不得把first01计费遗漏或让run02重获30/60。

新协议必须绑定根代理V10全部28份prior execution自身成本一次，并绑定first01 execution/protocol/claim。原27笔加first01，不能累计cumulative字段；科学/工程保持分列。原parent+live group CPU每≤20ms、一线程、最终protocol/claim hash后采样wall/CPU的超帽拒绝仍保留。若共享30/60耗尽，停止保留前缀，不扩大预算或重试。

## 执行与解释边界

先完成根因反例、精确diff、全部绑定SHA、固定100输入与共享成本独立审查，root再冻结/提交唯一协议，之后才可考虑run02。此PRE和describe/validate均0新科学/编译。新run不是修改first01或续写旧结果，不隐去旧失败。若任何accepted根不sound，按原规则停止；普通IK/界/branch/rank拒绝仍在固定分母内。

本项只有原wrist-only数学组件；0碰撞、checkEE/RBS/RSS分布/规划/新VI构造，VI974/974余额0、正式Table I0/22500与完整211义务保持。数学正例不等于原RSS忠实实现、连续无碰撞、规划成功或P4完成，不进入P2/Isaac。
