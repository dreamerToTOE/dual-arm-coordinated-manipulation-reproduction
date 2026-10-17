# D080 SBL_PCS 单次原生 solve PRE-TASK 草案

2026-10-17。状态 `DRAFT_NOT_DESCRIBED_NOT_FROZEN_NOT_RUN`。本草案不运行任何二进制或模型，也不修改已冻结 local runner、fixture、源代码、阈值或旧日志。

唯一候选为环境 II、已保存 A01 重建起终点、seed7、原 SBL Range=.8、trace模式，一次原 `solve(timedPlannerTerminationCondition(10.))`。最多一个新进程、一次请求、一次必要 setup、一次 solve；零额外 local fixture、零13点 projection 观察、零 connect fixture、零二次 solve、零路径独立物理检查。单项总帽20秒墙钟/40秒CPU，仍受R2累计3600/7200；子进程复用已审Session的20秒CPU上限。root要求先准备草案；正式冻结及执行必须等local实际独审通过和全额入账，不由本文自动启动。

直接复用已审SETUP01/local的Budget计时器、Session单次原子write+stdinEOF、loaded-library记录、Journal、隔离mesh、进程组强制回收、双管道EOF、源/依赖/ledger哈希工具。仅薄适配新RUN/claim、单请求、20/40帽和source pending结果。外GNUtime supervisor是local已审版本的身份/预算薄端口，独占inode与真实父进程链证明保持。未重新构造框架或模型oracle。

describe必须读取真实BUILD02独审、真实local独审及当前最新charged ledger；local必须已经四进程完成、人员独立局部和外计费证书通过，并出现在ledger完整execution集合。冻结协议绑定其字节以及当前所有源码、ELF、manifest、mesh、library、D080和逐执行成本证据。当前不得填占位local POST或提前生成会过期的预算协议。

保留原EXACT/NONEXACT/异常/超时、全部trace、原重建尝试（包括false/提前返回）、原文件存在/缺失和最终完整字节、shadow输出、live Motion/分支/代际、自然checkSolution connect。unknown connect角色保持JSON null/text -1及RECONSTRUCTED_OUTPUT_METADATA_ONLY，不回写生产字段。是否见到connect由这一次原solve决定；缺项不得添加fixture或重试。原fstream内部open/write/flush flags继续UNKNOWN，最终字节读回与sidecar不等于内部写状态。

source EXACT始终 `PENDING_INDEPENDENT_PATH_QUALIFICATION`，本项不要求成功、不替换端点、不简化或补点、不自动启动独立路径检查；由保存证据和独审决定最早未通过项目及后续预算。完整离散资格也不证明连续无碰撞或性能。若预算耗尽，保留所有prefix与真实费用，不重复启动。

D080 I–V已批范围、原22500事实、D08018000正式义务均保留。VI974/974仅只读存档；不推进RSS/VI新构造、不进入P2/Isaac，不生成提前结题报告。完整实验端到端资格通过后才做可重复cost pilot并单独申请正式计算预算。
