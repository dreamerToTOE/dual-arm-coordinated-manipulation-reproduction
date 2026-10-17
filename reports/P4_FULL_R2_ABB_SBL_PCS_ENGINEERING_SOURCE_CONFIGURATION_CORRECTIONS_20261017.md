# SBL_PCS 工程草案配置纠正补记（未执行）

2026-10-17，静态自核与 root 独立源码复核后纠正三个工程草案问题。仅改新增未执行草案，不覆盖旧记录、作者源码或已完成的 R2 资格；零项目 import/describe/transform/compile/binary/setup/solve，零协议/claim/stage。

1. 初稿 builder 的 DIAGNOSIS 误拼成不存在的 `P4_FULL_R2_ABB_SBL_PCS_SBL_PCS_ENTRY_STATIC_DIAGNOSIS_20261016.json`。现指向实际既有 `P4_FULL_R2_ABB_SBL_PCS_CBIRRT_NR_ENTRY_STATIC_DIAGNOSIS_20261016.json`；此修复只纠正文档资产绑定。
2. 初稿沿 RRT 复用了 constructor Range=2.6。作者 `run/plan_PCS.cpp:249–253` 的 SBL case4 明确 `step={0.8,0.6}`，277 行传 `step[env-1]`；本项 II 映射 native env1，所以 Probe 改为 `SBL(si,.8,1)`。这是恢复原作者 SBL 配置，不是实验证据后的调参。原 SBL constructor 仅赋 `Range=maxStep`（55行），setup 自动配置 `maxDistance_`（63–72行），原 solve 才 `setRange(Range)`（92行）。当前仍保持此顺序，分别输出 setup getRange 与原 solve Range，不提前 setRange。既有 NEXT_ENTRY_STATIC_PREPARATION 的“II range2.6”描述过宽且不适用于 SBL；旧字节保留，本补记明确纠正。
3. 独立静审指出实际两grid维数尚未输出。driver 增加各grid的 public `getDimension()` 与 `==projection getDimension()` 守门；只观察当前原setup对象，不改grid、projection、RNG或sampler。

首次修前七稿已逐字保存在 `work/preserved_sbl_pcs_engineering_draft_before_static_self_fixes_20261017/`，含保存SHA；修grid/Range前的driver、PRE和已改DIAGNOSIS builder另保存在 `work/preserved_sbl_pcs_engineering_before_grid_range_source_fix_20261017/`。这些是草案字节保全，不是实际构建manifest或资格结果。

三个Python新稿仅通过标准库AST语法解析；16个观察wrapper的字面签名在冻结R2模板中逐个恰好出现一次。实际变换/whole-file逆恢复尚未执行，不能把代码中的逆恢复门称为已通过。未来工程仍须独立静审、root冻结、源码/协议提交、外层计费与真实POST；本补记不授权运行。

保留的边界：原save历史connect的a_chain未初始化读取风险；作者类与系统SBL符号同名风险；未来public13须绑定实际库乘法的独立静态证据；原setup内部RNG实际调用仍UNOBSERVED。GNUtime覆盖builder完整child，builder begun在validate前，但原继承timer安装在validate后，不能声称preflight已有硬watchdog。外层实际收费与最终45wall/90CPU上界必须真实满足。
