# IV wrist固定100/800：零查询入口停止与根因

状态：PARTIAL / OUR-IMPLEMENTATION。冻结c598631后唯一run01在首模型构造前触发`RUNTIME_GEOMETRY_OR_SOURCE_LIMITS_CHANGED`；0 target、0 FK/J、0 IK，800分支全部未执行。这不是RSS数学失败或论文理论反例。原execution、events、claim、v2源码保持。

入口guard将R1元数据q1字面界±3.1416，与既有physical.source_limits的±180×3.1416÷180直接逐值比较；Python binary64的正上界分别为3.1415999999999999（0x1.921ff2e48e8a7p+1）和3.1415999999999995（0x1.921ff2e48e8a6p+1），差1ULP=4.440892098500626e-16rad。其余限位、基座和抓持一致。支持我方元数据guard来源混淆，不支持模型被修改。

修复路线：分别冻结R1 literal元数据和既有runtime degree换算界，runtime精确比较其自身来源；科学bounds仍使用既有physical.source_limits，不能用allclose、容差或改界过门。新v3、新run02/claim保存原01引用；全部100输入、800原解析编号及原科学函数、原1e-5闭链门/1e-6rank门不变。实施和独立静态审查后再冻结执行。

run01自身wall0.03671536999991076/CPU0.036766999999999994秒只计一次。共享原30wall/60CPU只余29.96328463000009/59.963233秒，新run不重开预算。本项不含碰撞、RBS、NR、RNG、solve或VI新构造。

另项H64真实helper原STOP/34完整门/30 UNKNOWN保留。398/398独立保存证据链接已通过：64输出19精确q12键中12键由H原完整门覆盖、7键由旧PCS_LOCAL01合格证据覆盖，每context主动角/分支标签另核。标签SAVED_REUSED_EVIDENCE_ONLY，0新科学，不能改写原run为64现场完整门通过。

V10：28execution=22科学运行账（含零查询失败）+6工程，R2累计wall504.47186458199417/CPU457.738928，余3095.528135418006/6742.261072。VI974/974余0，正式Table I 0/22500。211义务和原正式统计规模全部保持；不P2/Isaac，不提前结题Word/PDF。保全V10通过1028旧科学文件、57崩溃未提交文件8482891bytes及tar、另5工作树/13未提交文件、旧V9账和211行前114列。
