# ABB SBL_PCS 单 target 工程资格 PRE（V1 草案，未执行）

2026-10-17。Task：继续 D079 的 SBL_PCS 原生搜索器入口；当前只准备编译工程，科学目标为未来真实 SBL grid/PDF/lazy 资格建立可观察入口。最小证据是一个实际编译目标、完整五 TU 真实依赖规则、全部受管预冻依赖、原源码/变换逆恢复、完整编译日志和外层费用/回收证据；不以 ELF 存在代替通过。

当前范围仅新 stage `/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_sbl_pcs_v1/geometry_consistent_observed`、run `20261017_R2_ABB_SBL_PCS_BUILD01`、单 claim 草案；拟 45wall/90CPU，扣最新完整实际 charged ledger（目前 V23）、R2 总 3600/7200。尚未生成协议/claim/manifest 或运行 describe/import项目/compile/binary/setup/solve。独立静审、root 复核、源码/协议提交冻结和真实外层监督是以后执行前置。

## 复用与必要变化

- DIRECT_PORT：既有 `geometry_consistent_plain` 的 R2 APC 数值、PCS SVC 固定分支/RBS/回溯与 source collision；作者 SBL cpp/h 逐字身份先核。原原始端点和数值失败保持，不能称作者原输入/原数值直接通过。
- THIN_ADAPTER：CBiNR BUILD03 已通过的 `-MD -MF -` 完整多 TU stdout、保护依赖前冻/实后复核、逐 raw 切片、单编译进程组 watchdog/回收与独占 GNUtime 外层监督。本目标实际是 driver+APC+SVC+collision+SBL **五 TU**，不是沿用六 TU 常数。
- REFERENCE_ONLY：CBiD 的 NN 遍历、指针永久 ID 和整体 a_chain 读取；本稿另用仅观察的 lifetime/代际 registry。未移植 D 距离修补、H break 或 NR seam，未重跑已经通过的组件和路径。

新 driver 仅接受 `II work setup`，argv 为 solve 时在任何模型构造前返回64；源码仍完整链接原 SBL solve/局部/回溯实现，但工程不调用。未来 setup 保留原 main 的构造/setup 顺序、seed7、12维盒、q6±3.1416、恒 true callback、resolution .02、constructor Range2.6；setup 的自动 getRange 与原 solve 后才 setRange(Range) 分开报告，不偷偷提前改 range。

实际默认 projection 的13次 public project(0,e0…e11)仅为未来另冻操作预留，保存类型/元数据/公有线性作用列和 binary64；不访问 protected storage，不额外构造 RNG/evaluator/sampler，不称私有矩阵逐字导出。未来执行前必须有实际 lib project 纯乘法实现的独立静态证据。首次 setup 的 sampler 可为 null；不提前 alloc。详见观察方案补记。

registry 在 addMotion 前读活对象登记代际；removeMotion/freeGridMotions 前保存原关系，返回后仅用 token 退役，不访问 freed 指针。checkSolution 作用域仅给新增 connect 标 provenance，历史 connect 全 life a_chain=null；原 mpaths/M/false 均完整保存。新增静态证据表明历史 connect 可成为未来祖先，原 save 仍可能读取其 a_chain；见 HISTORICAL_CONNECT_STATIC_CORRECTION。此稿不修原源读取，故 runtime solve 不可用，后续资格需单独处理 metadata 输出边界。

## 依赖与停止门

实际已读取新 SBL `ProjectionEvaluator.h`、Grid.h、PDF.h，Grid 的 Eigen/Core/unordered_map/algorithm/cstdlib、PDF 的 util/Exception.h，以及公有投影的 RealVectorStateProjections.h/typeinfo/cmath。builder 前冻整个 OMPL/KDL/Eigen/nlohmann 小 namespace、Boost literal/macro递归闭包、既有五个 PQP 头及库、实际 compiler/linker/库/OS；绝不在看到编译后新增头改判本次成功。实际五 TU 规则须每 TU 一次、全 raw 字节覆盖，切片明确为派生，不冒充 compiler 各自 .d。

作者类与系统 SBL 同名/guard；单 target 不包含系统 SBL.h，不链接第二份项目 SBL TU。实际依赖门拒绝系统 SBL.h，compiler 生成 link.map 留供独立审查；不凭名称承诺 ABI/动态符号无风险。新受管依赖未冻、编译失败/超时、source/body/前后哈希变、进程组不空、日志或回收不全则保存 STOP，无第二次 claim/重试/放宽。新的有据工程修复先另版本、预算并保存失败。

## 预计新文件与验证

只新增 SBL builder/supervisor、driver/observer/instrumentation、PRE 与历史 connect 静态纠正补记。源码准备阶段只做 AST/文本/实际头文件读取；不执行 transform 项目 import、describe 或构建。之后由独立代理静审；root 审查后才可生成 draft/protocol、绑定真实最新总账，提交冻结并唯一编译。编译成功仅 BUILT_NOT_QUERIED，必须真实独立 POST 才入有效工程账；binary/setup/solve 以及后续完整路径各另冻，不从本 PRE 自动运行。

完整211义务、正式22500调用和其他原实验分母保留；VI974/974余额0。本工程不给路径/性能/方法优势/全文完成资格，不 P2/Isaac/提前结题。Need user confirmation：本项已由现有继续资格工程授权覆盖；新科学设计、VI扩额和正式大预算仍另审。
