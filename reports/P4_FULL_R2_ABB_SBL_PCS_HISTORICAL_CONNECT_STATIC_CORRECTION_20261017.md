# SBL_PCS 历史 connect 与 a_chain：静态纠正补记

2026-10-17，仅新增保存源码解释，零编译/运行。此前两份 SBL 静态报告中“connect 不进入原 mpaths”只对本次 checkSolution 新建的末端 connect 成立，不能推广到该 Motion 的整个生命周期；旧报告原字节保留。

作者 `SBL_PCS.cpp:320` 先执行本树 `isPathValid(tree,connect)`，再短路执行另一树 `isPathValid(otherTree,connectOther)`。若前者 true 而后者 false，本树已 valid 的 connect 不被删除；以后可能被 selectMotion 选中、成为新节点祖先，进入后来成功的 mpaths。其 a_chain 从创建至此仍未赋值。因此观察器必须按整个 lifetime 保留 `UNINITIALIZED_NOT_READ`，不能在 save 阶段假设每个元素均已初始化。

逐项检索当前作者 SBL cpp 的全部 `a_chain`：121/174/253 行是 root/root/grow 的三处赋值；553/564 行是原 save 写 `../paths/ik_path.txt` 两侧里程点 metadata 的读取。原 cpp 未用这个成员作投影、lazy RBS、分支选择或回溯控制条件；这支持“该读取位于输出 metadata”这一静态结论，但 C++ 未初始化读取本身仍是风险，不能因此称运行无影响或推断已经发生。原 global `active_chain` 是另一字段，不能混同。

当前工程稿完整链接原 SBL TU，body 可逆保留一次，未初始化或修改 Motion。observer 对历史 connect 始终输出 null；driver 只提供单独未来冻结的 setup 操作，明确拒绝 solve，避免在本阶段触发尚未审查的原 save 读取。后续单 solve 资格前，可进一步审查只在输出处使用 shadow 来源字段的版本化输出修复；须保留原源文件/差异/风险，不静默初始化或改算法控制。此风险诊断不删除 SBL 及全部原文义务。
