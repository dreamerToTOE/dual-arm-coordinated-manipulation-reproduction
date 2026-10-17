# SBL shadow v2 local 前置拒绝静态补记

状态 `PASS_STATIC_TEXT_ONLY`，22/22。仅读取文本、Python AST 与保存字节，未 import 项目或运行编译/模型/setup/local/solve。人员独立性 false，不替代独审。

新 local_preflight 在 request 解析及固定端点核验后、工作目录/seed/模型前执行；原内部 guard 保留。旧稿与旧静态失败证据逐字保留。工程 PRE 和其余五个工程资产保持最终冻结候选 SHA。
