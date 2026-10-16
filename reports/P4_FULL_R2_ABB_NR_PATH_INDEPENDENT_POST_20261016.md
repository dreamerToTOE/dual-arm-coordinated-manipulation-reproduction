# P4 R2 ABB 原 RRT_NR 完整保存路径独立算术 POST

审查日期 2026-10-16（Asia/Shanghai）；状态 `PASS_SAVED_EVIDENCE_POST`，36348/36348 检查通过，失败 0。独立保存算术得出路径合格 `True`。本审查作者也编写 path runner，人员独立=false；需 root 与另一代理独立复核。仅 stdlib 解析、Git blob读取、文件hash与保存数组矩阵算术，0 新模型、FK/J、NR、IK、PQP、RBS、RNG、solve或编译。

原 source E2E01 的 exact 非approx 结果历史保持 PENDING；本项单独后审。7 个原里程点、6 次原 state-level reconstruct 原返回 true，完整 qa/qb 与首末 Confs binary64 一致，原有向 tree 包含完整起终点序列。按全12角字节独立重建队列、每个ref与碰撞义务，393/393 唯一节点通过，无抽稀、无未知尾部。

闭链最大位置 9.793997321594361e-06 mm，旋转矩阵 3.0701365727470176e-08，原门均1e-5；原 degrees×3.1416/180 机械界最小余量 0.046633132713711944 rad。392 个原全12角叶最远 0.047800148933634198 rad，严格<.05；不加PCS固定主动链或解析分支门，不wrap/lift/重投影。

| 原边 | 原路径节点数 | 叶数 | 最大full12叶L2(rad) | 原返回/精确首末 |
|---|---:|---:|---:|---|
| 0 | 65 | 64 | 0.047800148933634198 | True/True |
| 1 | 65 | 64 | 0.031101554325702295 | True/True |
| 2 | 129 | 128 | 0.027767633178715244 | True/True |
| 3 | 65 | 64 | 0.042765744308204283 | True/True |
| 4 | 65 | 64 | 0.042361310767251317 | True/True |
| 5 | 9 | 8 | 0.045833523578561318 | True/True |

逐节点完整 native/aligned 原PQP响应、实际querycodes、TCP/独立pose、worker事件和累计计数均交叉核对。adapter PQP native/aligned `{"native": 45588, "aligned": 45588}`，实际数学臂FK/J 786、碰撞 393、adapter内部臂FK/J 1572；未以上限冒充实测。native TCP最大差 0.0037193449432919579 mm / 7.3239595073937291e-06，其原失败单列；aligned 2.2737367544323206e-13 mm / 4.4408920985006262e-16。

本次自有wall 3.7730926529998214s /CPU 3.9572699999999985s；之前24份自有execution按fsum重算，R2累计 419.40566987399438 wall / 385.449026 CPU。协议、claim、源码提交blob、build manifest/binary/源和mesh、完整日志/队列hash、前后保全和全部实际计数见同名紧凑JSON。每个失败完整保留；重复大数组只引用原始证据hash。

仅原离散碰撞策略的空间NR起终点路径资格；A01端点与数值接缝属于RECONSTRUCTED，不是作者原输入/KDL直接通过。保留8mm容差、原pair与共线杆三角形，不证明CCD、实体杆表面、省略pair安全、方法速度/成功率、PCS优势或全文复现。211义务、Table I0/22500及其他原文规模均保持，不P2/Isaac。

审查脚本 SHA256 `eccd4a933d9cb841862795b25fd07621bb79ce19a446c525d3d874773907ab43`。
