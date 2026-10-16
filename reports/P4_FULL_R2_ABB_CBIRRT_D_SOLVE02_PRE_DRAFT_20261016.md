# CBiRRT S02：唯一已知 setup 前导行的版本化transport修复草案

2026-10-16。**DRAFT_ONLY / NOT_FROZEN / NO_IMPORT / NO_PROTOCOL / NO_CLAIM / NO_EXECUTION**。S01原冻结源码、协议、claim、raw、STOP、费用永久保留；S02只修我方stdout协议解析，不改现有binary、driver、observer、OMPL、原算法或任何科学阈值，不编译。所有211项原文义务、VI974余额0、正式0/22500与旧路径/失败保持。

## 原失败与精确根因

S01 actual source `6ac452b4f6edf0c4b396307c385c64a71073a8d0`、run `20261015_R2_ABB_CBIRRT_D_SOLVE01`，execution SHA `99c5cc5e980bf52489b154d5a678df903a1897a1e9e966c341ea6b5229533fdd`，status `STOP_PREFIX_RETAINED`。父Session将首条完整stdout误当最终JSON，触发JSONDecodeError；源进程78833被kill/-9并reaped，最终response JSON=0、完整raw gate=false、diagnostics空。这个失败属于我方transport，不是作者数学、投影或规划失败。stderr证明源solve已进入identify/FK/IK及collision前缀，不能把本项说成0solve；原solve完整返回与后缀仍UNOBSERVED。

精确stdout为55bytes，SHA `daa344847b00a40924a64df3aebb4f859fa26327791294bb30f793a0edaba532`：

```text
Debug:   CBiRRT: Planner range detected to be 3.415829
```

末尾为单个LF，Debug冒号后恰3个空格。driver `planner->setup()` 位于其 `Redirect quiet` 作用域外；原CBi setup调用SelfConfig.configurePlannerRange(maxDistance_)，产生该日志。Console.h定义默认OutputHandlerSTD；实际已绑定libompl的OutputHandlerSTD::log静态反汇编可见DEBUG/INFO走std::cout，所以setup行未被driver重定向，solve作用域内同机制日志则随std::cout rdbuf转stderr。本次没有关闭日志或更换logger。

完整源码还表明setup的3.415829只是临时自动范围：构造原 `Range=maxStep=2.6`，setup暂给maxDistance_自动值，随后原solve首部 `setRange(Range)` 将实际grow范围设回2.6。S02保持原request range2.6、原setRange时序和所有科学行为；不将该调试数值当作规划范围被修改。独立来源诊断 `reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_STDOUT_SOURCE_DIAGNOSIS_20261016.json` SHA `cd257201d77757ee6b7fa0c6aca73859afe7813603f171c58b591e438cb4bfd7` 一并绑定。

## 最小解析修复与停止规则

新文件 `scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py` 从原S01复制，只增加原STOP/共享预算证据链、精确一次setup行识别和新run/claim；原S01文件不编辑。继续使用已审TAIL journal、非阻塞双pipe、PID登记、signal短屏蔽、完整raw保存、中央kill/drain/wait、native输出fsync及终局receipt。

stdout每个完整行先原样以base64进入raw journal，原全流始终保留。只允许 **response前恰一次** 上述55bytes完整行；单列setup_preamble_lines_observed=1，继续等待唯一最终JSON，不作为JSON响应或资格成功。第二条同日志、空格/数值/换行变化、空白行、任意其他非JSON stdout均立即STOP并保留原字节。最终JSON之前必须已经观察到该精确setup行；JSON仍须通过原完整schema/request/trace与身份门，不能用任意JSON放行。response后的任意额外stdout尾（包括第二JSON或该日志）仍由原EOF/tail门STOP。

正常完成最终stdout必须严格两行：原55byte前导行+一个完整JSON；stdout_complete_lines_observed=2、setup_preamble_lines_observed=1、raw_response_lines_observed=1、solve_dispatched=1。未知输出不做通用过滤、不regex吞日志、不trim或改写原字节、不改源函数返回。除这一精确transport例外外，原S01数值/trace/tree/Motion/branch/限位/碰撞和后续P独立路径规则完全保持。

## 共享原S预算与唯一新运行

S01外层原行 `1.43 0.93 0.19 1`，实际保守上界1.44秒wall/1.14秒CPU已消费；不能以内部1.194684555001004/1.0460630000000002较小样本退回余额。S02与S01共享原30wall/60CPU，精确余28.56wall/58.86CPU，并继续受R2总3600/7200扣账后余额约束。原10秒source solve上限、seed7和全部输入不变。S01的已进入solve尝试不被抹掉；S02是明示transport修复后的第二次版本化入口尝试，不冒称首试成功或独立统计样本。

新run `20261015_R2_ABB_CBIRRT_D_SOLVE02`；新claim `P4_R2_ABB_CBIRRT_D_SOLVE02_SHARED_REMAINDER_II_SEED7_ONCE_20261016`。仍恰一个源进程、一个固定II/seed7/2.6/10s请求，原A01两端完整binary64，原D-fixed binary/hash与原L02完整AND证书。actual S01 source/protocol/claim、完整raw/trace、receipt、监督日志和全部原资产SHA均前后绑定。

仅在root完成S01独立实际STOP费用审查及权威后续ledger后，S02的current_prior才可能通过：最新ledger必须涵盖S01在内的全部真实execution，并按独立外层charged成本一次入账；旧历史未测尾部仍UNKNOWN。缺失实际费用结算或D/L前置硬拒绝，不生成乐观协议。当前不调用describe或import。

对应具体supervisor `scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py` 只改新run/runner/receipt schema和共享剩余帽；O_EXCL time FD、真实PID/argv/parent/inode、Decimal上界、完整worker lifetime及失败charge记录保持。实际S02 caps以min(28.56,R2余wall)、min(58.86,R2余CPU)判定，超过即STOP，不借原预算30/60重新开帽。只有真实独立POST能把外层cost资格置true；内部sample/receipt/charge保持false。

源EXACT仍仅 `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT`；非exact/false/unknown/超帽保留，无自动第三次、换seed、换branch或再加日志白名单。后续完整P路径门、成本pilot及正式大预算仍分阶段，不开展RSS新VI构造、P2或Isaac。当前仅准备具体版本化修复，源码/PRE需独立静态审查、root冻结提交后才可能执行。
