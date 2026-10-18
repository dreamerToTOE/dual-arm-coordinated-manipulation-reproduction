# D080 环境 V PCS BUILD02 最小工程尾段 PRE 草案

2026-10-18。DRAFT，未describe、未冻结、未编译、未运行任何binary或模型。新run为`20261018_R2_D080_V_PCS_BUILD02_TAIL`，新输出stage为`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_build02`。本稿不授权执行；独立增量静审、最新V31实际账、root冻结并commit后才可唯一运行。

=== PRE-TASK REPORT ===
Task: 保留BUILD01原工程STOP，直接复用已经完成的8 TU对象、8依赖与plain ELF，只完成trace剩余两TU和一次链接。
Scientific objective: 无新科学问题；补齐既有同字节V局部观察工具的第二个工程目标。
Minimum sufficient evidence: 旧失败和独立first-collected证书完整保留；旧stage只读；新2TU原flags/真实MD依赖/3编译链接组回收/新ELF/最终源和对象身份/保守费用独审。
Current scope: 仅工程2 compile + 1 link，源/几何/branch/87pair/8mm/固定36请求不改。
Explicit non-goals: 不重transform、不重编旧8TU、不再链接plain、不执行plain/trace、不进行setup/local/RBS/数学/碰撞/规划/正式统计；不VI/P2/Isaac/FR3。
Attempt budget: 提议20秒wall/40秒CPU，原R2累计3600/7200内；工作帽15/30，预留5/10给回收/最终hash和持久化。只消费新尾段实际成本，不重开BUILD01原45/90或抹除其41.415730890000084wall/61.545897CPU费用。
Preferred method: 复用原builder已审validate_prior/invoke/dependency_evidence和原supervisor Decimal三观测；仅run/stage/两条编译命令/链接输入映射薄适配。
Fallback method: 保全任何STOP/错误/不完整MD与新输出，不自动重试、改flags、加时或改源。
Stop / escalation: 新stage/run占用、源/旧对象hash或mtime漂移、未知prior、依赖遗漏、预算或编译失败均停门。若实测20/40不足，保全费用后另报有证据方案，不自行扩大。
Files expected to change: 新tail builder/supervisor/PRE；全部BUILD01源码/protocol/run/旧stage/失败POST与local稿不改。
Validation plan: 人员独立增量静审；冻结后唯一工程运行；saved-only合并独审确认旧plain+新trace及实际费用，不能把工程通过说成局部科学资格。
Known ambiguities / risks: 单TU精确耗时/CPU未单独计量；旧对象原STOP时SHA未记录，必须持续UNKNOWN。first-collected只证当前保留对象身份及其已保存成功命令/依赖关系，不补造历史before/after SHA。20/40是有限资格帽，不能保证所有主机负载下都完成。
Need user confirmation: no。D080已授权普通工程资格；root明确同意原R2余额内20/40提议。正式统计、新科学设计或总预算扩大仍需用户审批。

=== PRIOR-ASSET CHECK ===
Current task: V BUILD02 tail engineering。
DIRECT_PORT: scripts/p4_d080/build_v_pcs_local_v1_draft.py中的validate_prior、invoke、dependency_evidence及生命周期；V build supervisor的Decimal三观测包络完整块。
THIN_ADAPTER: 新run/stage/身份；旧trace源与include绝对路径不改，仅-MF/-MT/-o指向新stage；link引用旧trace前三.o及新trace后二.o；新依赖额外要求旧stage实际source/header均预冻。
TEST_ORACLE: 独立failure POST PASS78/78，SHA`3dca76842b2f50751bd9c0455b592dff89dd4dbf7c09fbf7dfcf72c487d9576a`。它的17项first-collected资产清单恰为8.o+8.d+plain ELF。
REFERENCE_ONLY: 原219 body/pair与101工程证书仅复用SHA；不重新transform或复审旧8TU科学body。
Rejected assets: 原trace collision未完成对象、未运行RRT/link均不视为成功；旧BUILD01整体engineering_build_qualified=false永久保留。
Need user decision: no。

原BUILD01 execution SHA为`0027c3c1c64d72cf02903b383ea7bbf3fb417b2b0107c6a673398cb8db825a2a`，status=`STOP_ENGINEERING_FAILURE_RETAINED_PREFIX`，error=`BUILD_WORKING_CAP40W80CPU_RESERVE_FINAL45W90CPU`。plain五TU+link、trace前三TU为9个成功命令；trace collision第10个尝试被回收为-9，trace RRT/link未启动，实际query/solve/binary均0。

本项直接引用旧stage的plain ELF以及八个已完成.o/.d。原对象在STOP时未单独hash：对象`original_STOP_sha256=null`、`UNKNOWN_NOT_RECORDED_AT_STOP`不改。新冻结只能使用人员独立failure POST于当前首次收集的SHA/大小/mtime，运行前后均核同值；.d和plain ELF原已记录SHA分别保持。旧失败POST和原运行字节不被新组合结果替代。

新stage只新增trace `3_collisionDetection.o/.d`、`4_RRT_PCS.o/.d`和`v_pcs_local`。compiler仍`-std=c++17 -O2 -Wall -Wextra -pthread -DP4V_TRACE_MODE=1`，保留原OMPL/Eigen/PQP/旧trace include及强制observer头、原两cpp绝对路径；链接保持原g++/pthread/PQP/OMPL/Boost/rpath，旧三个trace对象按原顺序放在新两对象之前。所有输入、原8依赖/源与17保留资产在bound清单预冻；新两TU的实际MD仍完整核验，不允许事后补缺依赖改判。

成本依据仅为已保存原命令/文件时间线：plain collision从对应stdout日志初始mtime到.o mtime跨度约2.684秒，plain RRT约4.244秒；trace前三TU跨度约5.084/3.253/3.992秒。这些是保存文件时间戳跨度，不能替代独立单TU wall/CPU性能计量。完整BUILD01的外测41.4157wall/61.5459CPU包含旧8TU、plain链接、失败中断和持久化。只余两TU+link，20/40有限提议留出合理收尾空间，当前证据没有要求提25/50；若触帽保留失败，不暗改帽。

冻结协议必须采用schema=`P4_D080_V_PCS_BUILD02_TAIL_FROZEN_V1`、run_name/classification与新源码常量、environment V、engineering/frozen/independent_review=true、scientific/formal=false、budget20/40和working_budget15/30、stage_root新stage、`commands`精确两compile+一次link、已冻所有`bound_files_sha256`、最新V31 `prior`、原式GNUtime external_supervision路径/工具SHA。不生成本协议，不运行describe。原root已审工具负责冻结前最新账SHA和完整证据绑定。

外费用保持`EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE`：原raw GNUtime、outer monotonic/reaped和内部receipt分别加精确.01wall/.02CPU后取Decimal最大值，仅由实际独立POST替换本execution内部样本一次。新execution显式engineering分类、budget、query/solve/binary=0及JSON receipt，兼容现有v6成功计费工具；费用未知/原STOP/旧对象历史hash未知全部保留。
