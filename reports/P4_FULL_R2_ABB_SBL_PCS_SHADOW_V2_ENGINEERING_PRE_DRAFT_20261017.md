# D080 SBL_PCS shadow v2 合并工程候选 PRE-TASK

2026-10-17。状态 `DRAFT_NOT_DESCRIBED_NOT_FROZEN_NOT_COMPILED_NOT_RUN`。

本阶段只新增工程草案与静态自检。预计唯一未来 BUILD02 构建帽 45 秒墙钟 / 90 秒 CPU，仍计 R2 3600 / 7200；本文件不启动或预扣工程/科学运行，也不批准 local 或 solve。先由 root 与人员独立审查者核候选，再生成当前 SHA 协议、提交冻结；只有冻结以后执行一次编译。旧 BUILD01、SETUP01、二进制和作者原字节不改。

## 科学目标与最小证据

目标是把已审 shadow v2 输出修复接入一个可供后续 SBL 专属 local 和一次 native solve 使用的新 transport。原 SBL grid/PDF、主动角色选择、解析分支、lazy RBS、checkSolution、回溯与重建科学语句保持；唯一作者 body 内差异仍是已审两个 writer metadata 表达式。Range=.8、II/native1、既有 R2 数值与原碰撞 source-policy 保留。未知 connect a_chain 明示 text -1 / JSON null，分类 `RECONSTRUCTED_OUTPUT_METADATA_ONLY`，不初始化或回写生产 Motion 字段。

最小工程证据是五个 TU 成功构建，实际 -MD -MF - 全部依赖、受管依赖零遗漏、原源码及两 I/O edit 逆恢复、外 GNUtime 全成本、进程回收与全源码前后 hash 保持。编译日志中的原 warnings 原样保留。构建通过不代表 SBL 局部、真实规划路径、连续碰撞或性能资格。

## 复用资产和新文件

- DIRECT_PORT：已过 BUILD01 五 TU、GCC stdout 五规则解析、依赖 namespace、完整 compiler 日志、清理与 GNUtime 父进程/FD 绑定。
- THIN_ADAPTER：新 driver 的 local/solve 入口、文件字节保存与 shadow sidecar；新 BUILD02 身份和 D080 绑定。
- TEST_ORACLE：shadow v2 独立有界补充审查 104/104（JSON SHA `85c3a7f9df949d7059f1a99fed85337c9ef29376736a79e5b1bff69dcdc7e365`）；原作者五源字节和实际依赖清单。
- REFERENCE_ONLY：SETUP01 9534/9534 和 V25 已保存实际账；直接复用，不重做 public13 资格。四条 II 已通过完整离散路径只读保留，不作为本阶段新增成功。

新增文件：`baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_shadow_v2_draft.cpp`、`scripts/build_p4_full_r2_abb_sbl_pcs_shadow_v2_draft.py`、`scripts/supervise_p4_full_r2_abb_sbl_pcs_build_shadow_v2_draft.py` 及本 PRE/自检。复用独立新 v2 header/transform，不覆盖 v1。构建根 `/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_sbl_pcs_shadow_v2`、唯一 run `20261017_R2_ABB_SBL_PCS_BUILD02`、claim `P4_R2_ABB_SBL_PCS_SHADOW_V2_BUILD02_45W_90CPU_20261017`。不写原 stage/binary。

## 新 driver 契约

argv 仅 `II FRESH_WORK local|solve plain|trace`；一条 JSON 后 stdin EOF。严格 seed7、Range .8、A01 重建原 start/goal 完整 binary64；solve 另固定 10 秒，最多一次原 `solve(timedPlannerTerminationCondition(10.))`。没有 setup-only 操作，没有 public13/e0…e11 的 project 调用，不为观察分配 sampler 或消耗 RNG。必须的每进程原 setup 是真实运行初始化，不重复 setup 资格；元数据只读实际 projection 类型/维数/cell sizes/grid/range。原 setup 内部 RNG 仍 UNOBSERVED。

`solve` 仅返回原 native status、原 problem milestones、真实 tree lifetime/branch/连接证据及 pending 独立资格标签；不进行简化、补点、第二次 solve 或替换端点。原 solve 包含观察及输出 I/O，不能冒作正式论文纯算法计时。

`local` 不做任意动作解释器。候选只支持单 fixture：`lazy_chain` 或 `connect_pair`，start/goal 各最多 1–3 个保存来源节点。fixture adapter 以原 root/grow 已赋值语义登记树，生产 `checkSolution` 的 connect 只能由作者 body 真正创建；不人工制造 connect shadow。必须显式 `separately_frozen_local_fixture=true`、固定 q12/IK/assigned role/来源指针，未冻结输入不得执行。`lazy_chain` 真正触达原 SBL isPathValid/removeMotion/递归退役；`connect_pair` 真正触达原 SBL checkSolution 的同 cell 选择/ConnectionScope/lazy/原 save，最多一个 checkSolution，真实 false/提前返回原样保留。失败不更换节点、不调整 cell、不重试。source 选择可能原样消耗 rng_.uniformInt；observer 自身新增 RNG 为零。

具体 fixture **尚未冻结、尚未计算或执行**。人员独立审查者正在从已保存原 RBS/完整路径提出最小固定来源与新增触达边界；本工程 PRE 不预判任何 fixture PASS。已有 SVC 局部证书不重新冒名为 SBL 专属资格；地址复用只能如实记录分配器是否发生，不能强迫指定地址。历史 connect unknown 的真实运行见证若本固定 local 未触达，应保留缺项并在单 solve trace 观察，不增加无界 fixture。

## 输出证据与写成功边界

原 writer 文件位置不变：父目录 paths 下 path_milestones.txt / ik_path.txt；work/paths 下 path.txt / temp.txt / perf_log.txt。必须在独占新 work 及父 paths 下运行。driver 在返回或捕获异常后，对这五个原文件分别保存存在/缺失/读取错误/完整最终 bytes_hex，并把存在的文件原字节独占复制到 `writer_evidence/native`，fsync 后读回逐字相等；目录内额外原文件也保存，不覆盖旧文件。原 temp 按作者成功路径删除时，缺失作为真实证据保留。

shadow header 仍只拥有内存 expression attempt buffer。新 driver 在 Motion 退役后、不 reset buffer，生成版本化 `writer_evidence/ik_path_shadow_v2.json`，以独占 POSIX 写入/close/fsync/目录 fsync/读回逐字相等证明 sidecar 实际保存。sidecar 将每个 attempt 的 null/来源/代际/state ID 与最终 ik_path 三整数列及 live branch 快照逐行核对；保持原第一侧反向索引、第二侧正向索引与行序。无 attempt 不等于 writer 成功；缺行、额外行、列不符或文件不可读均保留错误，后续独立 POST 决定资格，不隐去 source EXACT。

最终字节读回匹配只证明最终可读内容及我方证据复制/sidecar持久化。作者原 fstream 各次 open/write/flush/close 状态没有 hook，必须标 `UNOBSERVED`，不得把 attempt 或 sidecar 保存成功冒作原 stream 内部成功。原重建 early return 可以留下 temp 或缺 path，原 EXACT 仍只是 pending 候选。没有从 metadata 修复推导 RBS/闭链或连续碰撞安全。

## 预算、D080 与停门

builder 运行时重新核真实最新 charged ledger、逐 execution SHA、外层费用独立证书与总和；目前实际基准为 V25，charged wall `839.3257053759941` / CPU `771.588923`，历史未测尾 UNKNOWN 不追改。新协议必须包含 D080 决策/任务/211 行范围 CSV/映射校验 SHA 与实际 V25（或更新后全入账快照），保留原 22500 事实并单独声明 D080 18000。工程 build 不批准任何 runtime，正式 18k 仍 cost pilot 后另审。

D080 I–V 为批准范围，VI 974/974 只读存档，零新模型/修复/RBS/solve；旧全部 211 行和历史状态不变。不进 P2/Isaac，不提前结题 Word/PDF。不变更原几何/阈值/算法科学假设，未来若需要这些偏离或额外预算则请示。

## 实际执行与自检

本阶段真实动作是系统文件读取、复制新自有草稿与 Python AST/文本静态自检；未 import 运行 builder 或 transform，未 describe 协议、编译、执行二进制或模型、setup/local/solve。driver 初稿自检修正前字节保存为 `reports/p4_full_audit/draft_archive/sbl_shadow_v2_driver_initial_20261017.cpp.txt`（SHA `5934faaa3528a679c2da8f812d55621158b41e0de434120042be7112d067b88d`）；仅修新 fixture 异常资源释放、root role=0 guard、attempt 行序和额外文件保存路径/捕获错误状态，不改已审 header/transform 或作者科学源。

下一步 root/人员独立审查通过→当前源码/依赖/预算 SHA describe→冻结提交→单 BUILD02。local fixture、运行预算及单 solve另冻；不因接口已实现自动执行。

## 冻结前独审修正：local JSON 前置拒绝

独立审查指出，旧草稿的fixture资格检查在必要模型构造/setup之后才执行。现仅在新driver请求解析之后、工作目录创建/seed/模型之前增加纯JSON preflight：frozen、kind、来源、各链1–3、lazy至少2、每node finite12、两整数IK及[-1,7]界、整数role0/1且root0；Probe内部原guard继续保留。未执行模型/编译/local。修前driver逐字保存在draft_archive/sbl_shadow_v2_driver_before_local_preflight_20261017.cpp.txt（SHA 4cc75e933dedd503f4c3e1668567958a2dd5c9f50912abdd23989eca7787b620），修前PRE也另档。header/transform/builder/supervisor不变。root已批准local固定正/负两lazy fixture、trace/plain共4进程合计15wall/30CPU，仍扣R2总额；具体协议最终冻结前不执行。
