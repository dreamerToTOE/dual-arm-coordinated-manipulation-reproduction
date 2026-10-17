# SBL writer/shadow v2 独立静审补记与首次内存文本核验

原审查器在 transform 前因两个我方文本检查错误停止：构造器子串误计与生成式变量遮蔽切片索引。旧脚本/JSON/MD 原字节保留，两 transform 调用均 0；旧 MD 固定叙述的后续逆恢复并未执行，不能作通过证据。本补记仅修 checker，不修改候选/原源码或科学条件；本次才首次实际调用 v1/v2 纯文本 transform。

状态：`FAIL_RETAINED_INDEPENDENT_STATIC_REVIEW`。真实检查 56/57，失败 1。

本项真实执行一次系统 Python 工程审查进程，保存源码 AST 中的 v1 与 v2 instrument_sources 各调用一次，只在内存变换五份字节；未 import 项目包、编译 C++、创建 stage、调用模型、setup、solve、RBS、IK、采样或碰撞。两份报告使用独占 x 创建，禁止重复执行以替代原结果。

固定原作者三处 a_chain 赋值、两处 writer 读取及四个 addMotion 来源均核对；ConnectionScope 只覆盖 checkSolution 的 connect 登记。历史 connect 可存活并成为未来父节点，registry 保留其 CHECKSOLUTION_CONNECT/unknown 来源，不因 parent 改变或地址复用而补值。候选仅在非 connect 且已有原赋值时读取一次 Motion::a_chain，此后 snapshot/writer 均读 optional shadow；无 Motion 字段写回。

独立词法掩码与括号扫描逆剥 v1/v2 各 16 个 returning-lambda wrappers；v2 另逆回两处 I/O 表达式。核对所有五文件逐字恢复。v1/v2 的 APC、SVC、collision、HDR 输出相等；SBL 输出差异严格为两个 writer 表达式与来源观察标签。原 save 完整原 body 声明已明确不适用 v2，两 I/O edits 单列，其他原科学 body 保留。

已知 0/1 由 optional 的是否持值判断（值 0 仍为有值）；unknown 输出 -1，JSON 记录 null、来源和 lifetime/代际/state ID。plain/trace 均收集内存 attempt buffer。header 未落盘 sidecar，text_write_success_observed=null；不能声称文本写成功、sidecar 已保存、完整路径或 SBL 端到端合格。

D080 已读并采用：I-V 为批准范围；VI 只读存档且本项新增 VI 运行 0。原 211 行和 22500 事实保留，D080 正式目标 18000 须 pilot 后单独批准。不重跑 II 四条成功路径，不进 P2/Isaac。

下一步可接入新版本工程候选并单独冻结；实际 C++ header、driver 保存、plain/trace 和 solve 资格仍未由本项证明。所有候选/原作者/旧证据字节检查保持，未改共享治理或预算账。

机器可核验结果：`reports/P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_ADDENDUM_20261017.json`。
