# V 工程费用计量兼容补记（2026-10-18）

状态：仅工程增量草案，未冻结、未运行、未编译、未 import runner/模型。三份科学稿保持原字节；唯一V BUILD01仍45墙钟/90CPU、原R2累计3600/7200，科学调用0。

SBL PATH01原始GNUtime119.80s低于原单调时钟receipt121.89707410200003s与outer122.07026397300001s，原因仍UNKNOWN；原time、charge、receipt、261/387 STOP和cap越界不改。此补记不重跑该路径。

先将已审builder/supervisor/helper逐字保全在 `work/preserved_v_pcs_engineering_before_monotonic_envelope_20261018/`，manifest锁定原SHA。旧87e784合并PRE、原101与helper独审报告继续作历史工程证据，不冒作修改后工程稿已通过独审。

builder仅新增一个可识别费用basis：`EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE`。它从保存原charge fallback、原receipt和raw GNUtime分别取Decimal上界最大值，核独审POST的basis/执行/charge/receipt hash/上下界；若旧charge未声明此basis，只允许已知PATH01原exec与原charge SHA的唯一例外。真实cap breach必须仍在ledger/POST登记，不能因越界拒绝费用入账。其它历史rawbasis验证原样保留，未知basis停止。

V supervisor首次持久化将原GNUtime raw upper独立保存，同时wall=max(raw+.01,outermono+.01,receiptmono+.01)，CPU=max(rawU+S+.02,outerreaped+.02,receiptCPU+.02)，全部按Decimal(str(原float))处理。若receipt或time不完整，保留最大已观测raw/outer成本，envelope_valid=false、不升级合格。完整性、原45/90帽和人员独立POST继续必需；新费用basis不会扩帽。

helper冻结新增显式 `--compat-review` 与 `--compat-review-sha256`。旧合并PRE对变更builder/supervisor的hash改指向修前保全字节，三科学稿/config仍与当前字节一致；新独立增量报告必须绑定当前builder/supervisor/helper三份工程稿。旧PRE和新报告分别进入bound manifest，避免覆盖历史报告或反复修改报告SHA形成循环。仍需root明确最新ledger路径/SHA及freeze批准，当前不生成任何协议。

本次仅AST和保存字节/差异检查；不重复219原体/pair或101历史证书审查。新增量独审由root执行，通过以后才能冻结首次构建。后续V构建若采用envelope费用，应使用能够保留该basis的saved-only入账工具，不能退回raw upper而少计。

root增量审补充：修前builder SHA `2c44c299c87bfb005652b45babd1b1a551bde9d7b658da6cdac91a8d75b33dcb` 已逐字保全在 `work/preserved_v_pcs_builder_before_final_tail_reserve_20261018/`。仅补 execution 的 `query_calls=0`、原 `budget`副本及工作帽40wall/80CPU；原总帽与final/receipt仍45wall/90CPU。5wall/10CPU留给组回收、最终hash和持久化，是工程提前停止条件，不修改编译选项或科学算法。真实两目标编译成本尚未测得，不能保证40/80内完成；若工作帽触发保留STOP和费用，不自动重试或放宽总帽。保留量也不是尾部绝对耗时保证，外层envelope与独立POST继续检查真实总45/90。
