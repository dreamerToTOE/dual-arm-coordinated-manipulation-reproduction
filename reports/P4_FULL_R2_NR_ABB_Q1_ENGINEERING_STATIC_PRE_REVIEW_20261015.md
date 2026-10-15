# R2 ABB NR Q1 单目标工程与原 Python 观测静态 PRE 审查

2026-10-15。`PASS_STATIC_ENGINEERING_PRE_ONLY`：下列绑定草案可以进入 root 的一次工程冻结审查，没有发现阻止该单目标构建的明显源码逻辑问题。本次不编译、不运行binary/Python参考，不做任何模型或科学调用。科学Q1 runner与冻结协议尚需另审，本报告不授权192次NR或后续planner。

|对象|读取 SHA256|
|---|---|
|`physical_nr_abb_q1_driver_draft.cpp`|`1211d0f741bad8cb5175a282d8f65137a7c5a1498c961323686ef0adb98eeb81`|
|`build_p4_full_r2_nr_abb_q1_draft.py`|`6c526ffb5359ecd26116c17dc592a274d9d04aa2956bb2d2bd35e6b78dd2c1af`|
|`p4_full_r2_nr_python_trace_draft.py`|`919008f7c008f1025e32469f43df155bc6751f7087bc871963e17b74efe5b0c2`|
|`P4_FULL_R2_NR_ABB_CPP_Q1_PRE_DRAFT_20261015.md`|`5ed62af8a64cd6159836da48f71532f0862cf4b95b66f8b97f873a49f7b457b8`|
|`configs/p4_full/r2_nr_abb_q1_engineering_v1.draft.json`|`bd80876b96b40c8d82675fe1c38d078d11af50eb1ee1b1f2a8926641693a458a`|

数学header逐式核对另见 `P4_FULL_R2_NR_CPP_FORMULA_STATIC_REVIEW_20261015.md`；header没有被本审查改动。

## 工程范围

builder只编译一个项目自有translation unit，原数学内核不复制；plain/trace为同binary runtime flag，只改变日志。固定绝对编译器 `/usr/bin/x86_64-linux-gnu-g++-11`，-std=c++17/-O1/-g0，无fast-math；绑定7自有文件、379编译器/库header资产和18个既有execution。工程config仍frozen=false、两review=false、scientific_execution_authorized=false。

execute要求全部源/协议与当前commit字节相同；全字段、prior SHA及R2余额动态核对。新claim、build root、execution目录防重启；45wall/90CPU与R2总帽取min，监视子进程组CPU/墙钟并保留stdout/stderr/返回码和失败前缀。工程成功只为 BUILT_NOT_QUERIED，零query/solve，不能视作Eigen NR已合格或公平速度样本。45秒是否足够仍UNKNOWN，超帽保留实测成本而不自行重编。

## 入口与观测

driver仅接受case_id/environment/q12三个key，II/III、有限12角；Options保留原默认10000更新、120s/call、1e−5/1e−5和1e−12。每条JSONL保存请求、模式、顶层完成、结果；transport异常返回非0且不重试。candidate/metrics、终止状态和完整trace由runner判定，不凭进程exit0判科学PASS。

driver已将header的−correction标为 proposed_delta_q，将保存q_next−q_before标为 observed_delta_q。Python观察器只匹配原function code，按唯一源码行锚点复制已有q/g/J/metric及SVD后s/mask/q，finally恢复原trace hook；无复制solver、额外FK/J/SVD或改原函数。末步无update保持空数组，cross-language只比较同义observed数据，不比较U/V列任意符号。

## 科学runner必须保持的边界

- 64输入须从原observations逐值核对，固定II32/III32原顺序；plain64→trace64→Python原函数64，192为最多顶层次数，不是预填完成数。完整失败/未返回/未执行尾项保留。
- 同binary模式精确等价与Python轨迹门按已披露PRE；另64终态metrics的128armFK/J计入真实预算。碰撞、RBS、planner及其他环境不在此Q1。
- observer主动捕获BaseException并将其记到observer_errors，目的是不让logger改变solver数值结果。因此**不能把event_sink抛异常作为唯一墙钟/CPU停止机制**。Q1科学runner应由独立外部watchdog/process-group硬帽控制Python worker；每个observer_errors都必须使完整观测资格不通过并停止依赖科学调用。已分发未返回调用为UNKNOWN，不自动重放。
- Python及C++内部理论FK/J计数与实际instrumented starts/completions分列；尚未观测的内部调用不能由结构推算伪填为实测。资源帽包含观察、持久化与终态检查，不借header内部120s/call越过整次60/120帽。

本报告为新增只读审查。未改builder/header/driver/observer/PRE/config；没有启动任何工程或科学进程，新增VI候选0，正式TableI调用0。
