# ABB CBiRRT D LOCAL02：固定三边局部资格 PRE 草案

2026-10-16。**STATIC_SOURCE_DRAFT / NOT_FROZEN / NO_PROTOCOL_PRIOR_CLAIM_OR_EXECUTION**。新源码为 `scripts/qualify_p4_full_r2_abb_cbirrt_d_local_v2_draft.py`，配套独占外层监督源码为 `scripts/supervise_p4_full_r2_abb_cbirrt_d_local_v2_draft.py`。本草案不批准执行；原L draft/PRE保持原字节，原LOCAL01从未运行，新run为 **20261015_R2_ABB_CBIRRT_D_LOCAL02**。

## 实际前置及来源边界

原D64永久保留STOP、原61/64 runner资格、UNKNOWN[61,62,63]、最后进程-9和原raw gate=false，原15/30不能重开。实际TAIL02只查询未派发62/63，结果仅 `SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO`；独立POST `P4_FULL_R2_ABB_CBIRRT_D_TAIL02_SAVED_INDEPENDENT_POST_20261016.json` 已有1374/1374检查通过，64实际响应、9进程、32plain/trace对，外层费用上界1.21wall/.99CPU。该POST的close_group仍明确为SOURCE_GATE_INFERRED_NOT_SAVED_SNAPSHOT，不能冒称保存了原关闭快照。

LOCAL02前置是AND契约，禁止仅OR成功字符串：硬绑定真实TAIL02 execution、独立POST精确SHA/schema/status/1374检查、64/9/32、原STOP/UNKNOWN/index61未原资格，重核全部retained文件、原D源binary/build/mesh、protocol/claim、tail journal/trace/EOF/registry和external time/charge/metadata/stderr。重读tail两个真实新raw以及62保存raw，按冻结原门核全64；独立人员从原q重算的算术证据来源仍为真实POST。新源码不把内部aggregate当人员独立，也不把原D64改成PASS。

实际权威账为 `results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V14.json`，32execution。逐条原wall_s/cpu_s和execution SHA保持，旧31条没有charged字段时使用原测量；只有tail用charged_wall_s=1.21/charged_cpu_s=.99精确替换一次，并绑定该行external POST/time和收费依据。总charged为567.215705375994wall/518.608923CPU，不能再加tail内部sample。冻结与执行前后要求当时全部execution集合精确等于V14（排除本新run），任何并行新费用或文件改变均阻止执行，不使用过期余额。

## 原科学条件完整保留

原 `fixed_edges`、`saved_certificate`、`schedule`、`trace_audit` 四函数完整AST与原L draft一致；原三条高精度state级边取原E2E reconstruction_attempts.jsonl，角色/branch分别(0,3)/(1,3)/(0,0)，完整参考M为80/65/34节点。3边×原state RBS/reconstruct×plain/trace严格12个顶层调用；每mode一个新SVC进程、每进程6请求，共2进程。仅D-fixed原stage local模式，原RBS_tol=.05、最大深度150、withObs=true，原解析分支、geometry、限位和碰撞策略保持。

12返回必须全部true且三边非平凡递归；原state不变，6对plain/trace完整可观测字段binary64一致。trace检验所有嵌套entry/return/id、真实native FK/IK/collision计数、原角色/branch、主动角不变、RBS与reconstruct投影输入/输出序列精确一致，投影输出multiset等于旧M内点。plain内部UNOBSERVED，不伪造plain内部轨迹。

每份新完整M、首末、顺序及全部binary64须等于原80/65/34；才能复用177唯一旧节点、176叶的完整独立闭链/branch/界/aligned离散碰撞证书。0新独立物理查询；源RBS自己原有FK/IK/collision继续真实调用和trace计数，不报成零。任何false、不同M、截尾、未知trace、碰撞不clear或hash/EOF差异即STOP，不换边、改阈值、换seed或追加物理查询。

## 有限预算和journal证据

整次own-cost仍 **30wall/60CPU**，并受R2总3600/7200的实际charged余额约束；每source child仍RLIMIT_CPU30，20ms父timer计self+reaped children+登记live PID。先登记Session再start、父fork/exec/PID登记短mask、子恢复mask及limits；异常先停重复timer，对中央registry并集先kill、再drain和独立reap，任何未回收或超帽不能通过。正常两个SVC source均需EOF、exit0、无extra stdout，完整构造/每请求source trace与原stderr逐binary64绑定。新LOCAL02明确保存启动group事件和关闭group快照，不延用TAIL02的关闭快照缺失。

证据改为单一exclusive journal，每记录flush、终局一次fsync，记录固定请求、原raw行base64、解析前门响应、每门及停止前缀；原stdout/stderr按D64安全双pipe传输原字节完整保存，每process结束各fsync一次。不再每请求创建四个独立durable文件；journal及源stdio都保留，派生解析不覆盖原raw。原科学门仍逐返回立即执行，失败立即停新请求。断写残行保持，最终另起边界保存完整可得raw绑定和UNKNOWN；保存失败只能STOP。

mandatory旧资产/协议/claim/权威prior重hash、journal/stdio及execution最终持久化纳入受测runner。execution自身sample之后另存receipt，明确receipt最后fsync及退出尾部UNMEASURED_NONZERO；内部PASS时external_supervision_qualified仍false。唯一入口是配套监督器：O_EXCL持有time inode，GNUtime通过继承FD输出，runner强制验证真实父time executable SHA、argv、父祖PID和held inode，监督器保存planned/start/reaped原始链。

外层time从Python入口覆盖import/preflight、source、journal/全部最终落盘和退出；Decimal两位精度上界elapsed+.01≤30、user+system+.02≤60才可接受，超限或未知计时均STOP。监督器自身metadata/time-log fsync属于明确排除的监督开销，不冒充已测科学子进程费用。即使preflight失败没生成execution，唯一外层attempt仍有charge，不能换名重开；未来权威账按独立POST的外层上界替换本execution内部sample一次，不能双扣或遗漏尾部。

## 验收与后续停门

内部成功标签仍限 `PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED`，来源另列split-distance；不是完整CBi路径、CCD、RSS或论文FULL。实际唯一运行后必须由人员独立saved-only POST核全部真实证据和外层费用；预计POST文件为 `reports/P4_FULL_R2_ABB_CBIRRT_D_LOCAL02_SAVED_INDEPENDENT_POST_20261016.json`，schema为P4_LOCAL02_SAVED_INDEPENDENT_POST_V1，status为PASS_LOCAL02_SAVED_DISCRETE_SEAM_INDEPENDENT_POST，checks全通过、personnel_independent=true、external_supervision_qualified=true、execution/time/charge/retained SHA完整。

未来独立POST的required_gates必须精确包含以下八键且全部为bool true，不能由本草案预先生成结果：actual12_all_true、six_plain_trace_pairs_binary64_equal、complete_three_M_binary64_equal_saved80_65_34、two_SVC_zero_CBi_zero_direct_rng、raw_EOF_and_all_processes_reaped_exit0、old177_complete_discrete_certificate_reused、external_cost_and_identity_qualified、original_D64_STOP_and_H_STOP_preserved。原D64与H停止/UNKNOWN及所有旧失败均保持。

两位静态审查及root审查通过后才能冻结真实源码/参数，生成当时可执行protocol和唯一claim并提交；本次尚未执行任何import/describe/prior snapshot/协议/claim/compile或科学调用。S单次solve和P全路径外门仍需真实LOCAL02完整独立POST、后续实际charged账及各自冻结，不能由内部PASS自动启动。VI974/974余额0、Table I0/22500和全部211义务保持，不进入P2或Isaac。
