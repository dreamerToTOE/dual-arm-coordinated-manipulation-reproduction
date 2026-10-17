# SBL_PCS writer/shadow v2：最小实现静态草案

2026-10-17。`DRAFT_NOT_FROZEN_NOT_IMPORTED_NOT_TRANSFORMED_NOT_BUILT_NOT_RUN`。本项依据先行静态设计 `P4_FULL_R2_ABB_SBL_PCS_A_CHAIN_OUTPUT_MINIMAL_FIX_STATIC_DESIGN_20261017.md` 与主代理的明确最小实现授权，只新增独立文件；没有扩大 driver、builder 或未来运行。

## PRE-TASK / PRIOR-ASSET CHECK

- Task / scientific objective：移除原 SBL writer 对历史 connect 未初始化 `a_chain` 的两处读取风险，保持原科学控制和已定义 metadata。
- Minimum sufficient evidence：穷尽原三个赋值/两个读取/四个 addMotion 来源；已知 shadow 来源、unknown 不读原字段；两 I/O 表达式有独立逆恢复及整文件相等 guard。
- Current scope：两个独立 v2 文本文件与本报告；旧八稿、SETUP、原作者、stage、binary 原样保留。
- Explicit non-goals：无模型/规划/采样/RBS/IK/碰撞/编译/项目 import/项目 transform；不修改科学条件，不新增实际 sidecar 或路径资格。
- Attempt budget：本项实际科学执行 0、工程编译 0；不创建 execution/claim，不动总账。未来 build 与 solve 须分别冻结。
- Preferred method：已验证 v1 observer/transform 的薄适配，仅 shadow metadata 与两 writer 表达式；没有新增算法。
- Fallback / stop condition：独立静审未通过则保留稿件和问题，停止接入；不通过初始化 Motion、猜角色或改 RBS 消除 unknown。
- Files expected to change：仅本节下列三个新文件；先行静态设计报告另保留。
- Validation plan：stdlib `ast.parse`、literal 两表达式检查、v1/v2 文本 diff、旧文件 SHA；无执行新模块或 C++。
- Known risk：shadow/new JSON 有分配和时间成本，不能宣称性能无扰动；没有验证实际 C++编译或运行；未知字段不可能保留未定义原数值。
- Need user confirmation / decision：本次静态最小稿不需；并不批准任何后续实际运行。
- Pinned prior asset：本仓库现 v1 observer/transform（SHA 见先行设计），作者 `909bd72fff778aca8682c96f9eb86ae4eb75557b`。
- DIRECT_PORT：v1 全部16个 wrap 位置、树登记/退役/代际、原模型观察契约。
- THIN_ADAPTER：Lifetime 改存可选 shadow，snapshot 改读 shadow，两 writer 表达式与 JSON attempt buffer；逆恢复单列。
- TEST_ORACLE：固定作者全源字节；既存历史 connect 静态反例。
- REFERENCE_ONLY：其他 planner 的 writer，不移植其已赋值假设；旧 FR3/MoveIt 无关本项，不增工程轮子。
- Risk of paper fidelity contamination：仅版本化输出 metadata 偏差标 `RECONSTRUCTED_OUTPUT_METADATA_ONLY`，不加入 H/D/NR、角色猜测、模型或科学控制改动。

## 新增实现

1. `baselines/p4_full/geometry_consistent/abb_sbl_pcs_observation_shadow_v2_draft.hpp` 是独立新 header，不能与同 namespace 的 v1 同 TU 混用。新增 `std::optional<int>` shadow，不改原 Motion 定义、布局、构造或 storage。固定非 connection 的 root/grow addMotion 前，原程序已赋值，observer 只读一次并要求为 0/1；connection 根本不读 `m->a_chain`，shadow 的整个 lifetime 保持空。后续 snapshot 和 writer helper 只读 shadow。地址复用按既有代际重新登记，旧已知性不继承。
2. `baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_shadow_v2_draft.py` 保留 v1 全部 wrap 位置，仅在包裹前于完整原 save body 替换两表达式：`mpath1[i]->a_chain` → `p4sbl::writer_a_chain(mpath1[i],1,i)`；`mpath2[i]->a_chain` → `p4sbl::writer_a_chain(mpath2[i],2,i)`。剩余 body 和五文件字节必须通过逆剥 wrapper、逆回两表达式后完全恢复；manifest 明示 save body 不再是逐字原 body，而非复用旧完整原 body 声明。
3. `writer_a_chain` 对已知来源返回原 int，对 unknown 返回 `-1`。它在 plain/trace 均收集 `writer_metadata_attempts`，其 JSON `a_chain=null / a_chain_provenance=UNINITIALIZED_NOT_READ`，有 schema/version、RECONSTRUCTED 分类、side/原 index/attempt 行号、lifetime/代际/state ID、text sentinel。trace 开关只决定是否额外 emit 该观察，不决定收集或值。

## 保存证据边界

该 header 只有内存 attempt buffer 与 const getter，没有打开任何文件或自动保存 JSON sidecar。`text_write_success_observed=null` 是明确的未知：helper 在链式 `<<` 里被求值，不证明 ofstream 已打开、成功写入/flush 或文件持久化。未来 driver 必须在 reset 前独立复制与保存 buffer，对每次 save 的实际 `ik_path.txt` 行数/三列/顺序、已知值与 unknown sentinel逐项核验，才能形成真正 sidecar。当前没有 driver 或接入代码，不能称已保存 metadata、修复已运行或路径已资格。

单次进程多次 save 时 attempt 行号为全 buffer顺序，source_side/index可能重复；未来协议须先冻结允许 save 次数，并结合完整事件序列逐 save 核对，不能把全 buffer冒称最后一个被覆盖文件的一一对应。当前最小实现不改变原 save 的文件覆盖方式，不新增科学分支来解决 I/O。

新文件要求 C++17 的 optional，与当前 v1 本身使用 inline 变量的语言级要求一致；本次没有测试编译器配置。任何后续 caller必须显式选 v2 header，不能把 v2变换接到 v1 header，或把 v1原 writer误接到新 header后宣称风险已消除。manifest 的 `required_header_variant` 明示此边界。

## 实际静态核对

使用系统 Python stdlib 仅 parse 文件 AST（没有 import 本项目或 invoke instrument_sources），新旧 Python AST 均成功。`WRITER_EDITS` 的 AST literal 为恰两项，旧表达式恰为已审两处成员读取。v1/v2 diff核对：原16处 wrap位置/科学args、原树grid/PDF/branch/RBS/回溯body变换规则不改；差异仅新metadata替换/逆恢复/显式manifest、shadow/header及attempt记录。

旧 observer SHA 仍 `7507648eb8ede25eea1cadcc32270a0bdf27633b1520de717718f6a907b986ac`，旧 transform SHA 仍 `cf5f5192840883634dfd3f18ea117dd505b66a8f1648391ae15113508ae2a237`。`diff -u` 返回1表示新旧预期文本不同，不是编译/科学失败。完整候选字节变换和 inverse guard 尚未实际调用，不能把代码中的 guard当成已执行通过的证据；C++ header也未编译或执行。主代理另做独立审查。

SETUP01原9534/9534只限原setup与公有13作用；原writer未定义输出风险及旧误判补记原样保留。此稿不触碰VI（974/974余0）、正式0/22500、全部211全文义务与原规模，不进P2/Isaac，不提前结题。未自行 add/commit/push。
