# ABB 原 RRT_NR 入口独立静态复核

2026-10-16。状态 `PASS_STATIC_ENGINEERING_AND_SCIENCE_DRAFT_REVIEW`，38/38 项静态检查通过，0 compile/query/solve/RNG。复核者非入口作者。

原作者 RRT_NR.cpp 除唯一保留 temp 的 I/O 差异外可逐字节还原；原 SVC 完整 cpp 去除 state-level 返回后 Confs 观察包装后可逐字节还原；原 kdl cpp 仅 GD body 调用已合格 physical NR，并保留完整原文件。原 vector RBS/回溯及搜索控制流未改。环境 II/native1、range2.6、goalBias.05、resolution.1、原12维sampler box及恒true callback均对应原入口。完整Confs保存 normal true/false，未返回的 Confs 不作推断。

真实 local execution/protocol、作者保存证据117258项、人员独立保存证据218766项及 raw-link666项全部绑定，三层精确契约及完整 SHA 才可开gate。5项内存反例证明失败的执行soundness、协议SHA、POST状态、独立检查数或raw→main SHA均闭门；不更改证据文件。

工程v2 draft SHA `e0a61f792d3e157b9368a7f31312ba0a3c987f02a6998ab69d389c1c2c4f061c`，绑定1201资产及22既往execution。该draft仍frozen=false/reviews全false，工程45wall/90CPU。科学v2 draft SHA `2629a77814e66fb6aa7ca38d4056a496fb716ce456d598a01e6e365ca590d034`，仍无成功新build；必须实际build后重绑。单seed7、一次solve10秒/外帽30wall/60CPU，完整路径后审另120wall/240CPU、最多2048唯一节点。均独立claim，不自动连跑。

原v1 draft两文件SHA保留。静态复核不证明编译成功、原NR规划成功、完整连续碰撞或任何性能比较；0/22500正式统计、VI974余0和全文211义务保持。root可独立冻结工程，再决定唯一构建；科学与路径分别后审。
