# ABB CBiRRT D S01：固定 II/seed7 单次原 solve PRE 草案

2026-10-16。**DRAFT_ONLY / NOT_FROZEN / NO_PROTOCOL / NO_PRIOR_SNAPSHOT / NO_CLAIM / NO_EXECUTION**。只准备具体 transport 与监督源码，不运行 driver，不编译，不提前生成有乐观 L 结果的协议。原 211 项论文义务、正式 Table I 0/22500、VI 974/974 余额 0 保持；不开展 P2 或 Isaac。

本稿落实已有 `P4_FULL_R2_ABB_CBIRRT_D_SOLVE_RUNNER_DESIGN_PRE_DRAFT_20261016.md` 的具体实现。原 D64 仍是 STOP、原完整资格 61、UNKNOWN[61,62,63]、最后源进程 -9；TAIL02 只有分次接口资格，不等价原八进程历史。原 H 科学 STOP/30 UNKNOWN 和旧 PCS177/NR393 离散证书保持。

## 前置 AND 门与当前状态

D 的实际 TAIL02 已保存，人员独立 POST 为 `P4_TAIL02_SAVED_INDEPENDENT_AGGREGATE_POST_V1`、`PASS_SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO_INDEPENDENT_POST`，1374/1374，绑定 64 真响应、9 总进程、32 plain/trace 对、1.21 wall/.99 CPU 外层上界。S 精确绑定该 POST 的 SHA `4c6d30b2e8106394235e8990de7b6738d0d587bf198a94d314d6fe49736ff2ca`，不改称原单次 D64 PASS。

L 仍等待未来 `20261015_R2_ABB_CBIRRT_D_LOCAL02` 实际运行与独立 POST。S 的 `prerequisites()` 先检查这些实际文件是否存在；缺失即硬拒绝 describe/validate/execute，不生成协议、claim 或当前 prior。未来只接收精确 `P4_LOCAL02_SAVED_INDEPENDENT_POST_V1`、`PASS_LOCAL02_SAVED_DISCRETE_SEAM_INDEPENDENT_POST`、全部 checks 通过、人员独立与外层监督为真、execution hash 匹配、全部 retained 字节重核，以及以下八个 required_gates 全键全 true：实际12全true、6对binary64、M80/65/34完整相同、2SVC且0CBi/直接RNG、raw/EOF/正常退出回收、旧177完整离散证书复用、外层费用与身份资格、原D/H STOP保持。L 内部 PASS 或单个 status 字符串不能放行。

最终冻结另读取届时最新权威实际 ledger，要求其 execution 集合逐 SHA 等于真实全部 execution；已监督运行使用 charged wall/CPU 替换内部样本一次，绑定其独立 POST。历史未测尾部继续 UNKNOWN。不得沿用本稿撰写时的 prior/余额。

## 唯一固定请求与源码

沿用实际 D BUILD01 的 `distance_destination_fix/p4_abb_cbirrt_d`，完整 build、claim、source、transform、库与 mesh SHA 链由原只读 reader 校验。无 H patch、无重编译、无新 planner 修改。S 固定一个新进程、一个 request、至多一次原 solve：

`BINARY II NEW_RUN/work solve trace`

请求固定 environment II、operation solve、seed7、range2.6、solve10秒，start/goal 为原 A01 II_0/II_1 的完整 12 个 binary64 原角。旧 D 保存的 endpoint hash 逐字绑定；不 wrap/lift/重投影。原被动 branch 分别 start3/goal0，不推称共有一个 branch。原 sampler box、resolution .02、恒 true callback、rand角色、NN、fallback 与 RBS 次序由现有 driver/源码保持；无 RRT goalBias 参数。

新 run 下独占创建 work/simulator，仅复制已绑定的20个 mesh。构造前 work/paths 与 run/paths 均不存在，原 driver 自行建立两处输出目录；不拷贝旧 path。所有原文本、temp、false/partial 输出原地保留并哈希，不依赖低精度文本恢复高精度角。

## transport、证据与清理

`scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_draft.py` 仅 stdlib 及冻结 TAIL/D 保存字节 reader；导入不执行模型、生成协议或 prior。具体 Session 继承 TAIL 的非阻塞双 pipe、raw chunk journal、EOF 与 cleanup，覆盖固定 solve 命令和唯一 request。每段原 stdout/stderr 字节随读以 base64 写入 append journal，flush 而不逐 trace fsync；最终全流 snapshot、独占 source_stdout.bin/source_stderr.bin、journal 终局 fsync，原字节完整绑定。原 response 先入 raw journal，再解析/检查。

父级先拥有 Session，再启动 Popen；只在 fork/exec 到 PID registry 登记的短段屏蔽 SIGALRM，child 恢复原 signal mask 并限制 CPU60秒。异常先关闭周期 timer，再按 registry 与实际 Session Popen 并集 kill/drain/wait，保留真实 returncode。start 与 close group 均序列化，EOF、pending 与已回收状态明确保存。计时超帽、JSON/trace不完整、资产变化或 cleanup 错误保留 STOP，无第二次进程或重试。

完整 trace 保留真实 entered/completed，构造 mesh一次、setSeed7/srand7各一次、一个结构性直接 RNG member；库内真实 RNG constructor/seed draws、未插桩 rand/sampleUniform 精确次数保持 UNOBSERVED。solve 内原 FK/IK/collision/RBS/projection 可真实发生，S 的零调用仅指额外独立物理查询、编译、旧接口重查、VI 和正式统计。

tree 的 Motion/state identity、parent/root/branch、两树 side、原 connectionPoint、planner_data、所有 reconstruction false 与完整高精度 path 原样保存。不同 Motion 即使 q 相同也不合并。S 只检查实际 transport/trace 结构，不调用物理模型、不修 path，不把 native exact 当成独立路径通过。

## 分类与后续独立门

原 EXACT 只保存 `SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT`；原 nonexact 保存 `SOURCE_NONEXACT_RETAINED_PREFIX`。两者都不是 PCS 路径 PASS、连续碰撞证明、RSS或原论文 FULL。native save/reconstruct false 仍保留；不得为补树、改 branch 或补 bridge 再运行 solve。

S 完成后由独立 saved-only 审核核对两树 root/parent/Motion identity、真实 bridge、start到goal方向、全部里程点和每边真实 true 重构。后续 P 的完整密集节点队列、预算、物理与 branch/限位/原离散碰撞/严格 full12叶距<.05 判据另行冻结。队列超帽不能截尾。S 不自动启动 P 或正式成本 pilot。

## 30/60 总帽与具体外层监督

S 拟独立30秒 wall/60秒 CPU，仍扣 R2 总3600/7200真实 charged余额；原10秒 solve是 source limit。预算覆盖 mesh、request、source、管道、清理、全部 hash、raw/journal/execution 与 receipt 持久化。内部 sample 与 receipt 保留真实范围，receipt 自身尾部非零未测，不能报0。

唯一未来启动命令为 `python3 scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_draft.py --protocol FROZEN_PROTOCOL`。该具体 supervisor 从已审 TAIL 版本复制，只更换 S 常量及30/60帽，继续 O_EXCL 独占 time FD、GNUtime完整 child lifetime、实际 PID/argv/parent/inode证明、Decimal wall+.01/CPU+.02 上界和独立 charge 文件。任何 preflight失败即使没有 execution也保留外层尝试费用；不启动第二次。runner裸调用在claim前拒绝。

internal/receipt/charge 的 `external_supervision_qualified` 始终 false；只有人员独立实际 POST 可以确认外层费用/身份资格，再单次入账。supervisor自己的日志持久化尾部在 scientific child成本范围外，明确披露。源码静态审查、L实际前置、最新ledger、root最终freeze和提交缺一不可；本稿不授权执行。
