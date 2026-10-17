# ABB SBL_PCS 下一入口：保存材料的静态准备 V1

2026-10-17。状态 `STATIC_PREPARATION_ONLY`；只新增本报告及同名 JSON。复用 `P4_FULL_R2_ABB_SBL_PCS_CBIRRT_NR_ENTRY_STATIC_DIAGNOSIS_20261016.md/.json`，其 SBL 结论与当前作者/已资格模板逐字身份保持，不重复巨大审计。

## 本项 PRE 与复用

目标是给下一单 target 工程明确观察契约；最小证据为原源码行号、现有适配不适用处和工程门。零编译、项目 import、describe、binary/query、setup、模型/FK/IK/碰撞/RBS/solve/VI 构造；不生成科学协议或 claim、不改算法/源码/账/治理。只新增这两份报告。D079 全部 211 义务、正式 45×500=22500 调用和 VI 974/974、余额 0 保持；root 正做 CBiNR 完整 P，本项不重跑或消费它。

`DIRECT_PORT`：只读复用已有 PCS R2 数值几何、固定 branch SVC/RBS/回溯及 source collision body，旧资格不重跑。`THIN_ADAPTER`：CBiD 单请求、原相对路径目录隔离、完整 raw 到 EOF、外层费用边界和可逆完整 body wrapper。`REFERENCE_ONLY`：CBiD 树遍历、永不退役地址 map、全 Motion a_chain 读取，均不能直接移植。原 SBL grid/PDF/lazy 策略保持。

## 单 target 工程必要差异

1. **默认 projection 和 sampler。** 作者 `SBL_PCS.cpp:63–71` 由 SelfConfig 配置默认 projection；`139–140` 在 solve 内 allocValidStateSampler；main 没有 setProjectionEvaluator。保留原对象、setup 顺序和默认分配，seed 设置早于首次相关构造。未来保存实际类型、dimension、cell sizes、bounds/userConfigured、grid dimension 和实际 sampler name/attempts；本次具体类型/维数/矩阵数值仍 UNKNOWN。头文件只说 SelfConfig 选 state space default、无自定义 allocator 时分配 UniformValidStateSampler，不能将这些契约写成实测。

   矩阵留证需先补合法观察路径：本机 linear evaluator 的 `projection_` 为 protected、没有 public 矩阵 getter；ProjectionMatrix::mat 本身 public 不改变这一点。getDimension/getCellSizes/普通 settings 不自动证明矩阵已绑定。不替换 evaluator、不做伪派生 downcast；无法合法取得实际矩阵则保留 UNKNOWN，下一 solve 契约不放行。真实内部 RNG 未 hook 时标 UNOBSERVED，不填 0；不额外构造/反复挑 projection。

2. **lazy 删除和地址代际。** `addMotion:466–484` 入 grid/PDF；`isPathValid:367–402` 失败触发 `removeMotion:410–464`，后者递归释放 state/Motion，且先把 child parent 置 null。SBL registry 需单调 lifetime ID、地址代际、active/retired 与删除事件，在有效对象期复制 q/branch/parent/root，child 原关系须在 parent=null 前留证。覆盖 freeGridMotions/clear/析构；返回后不解引用已释放指针。CBiD 当前 pointer→ID map 只有 reset、无 retire，不能用作跨生命周期唯一身份。

3. **未初始化 a_chain 不读取。** Motion 两构造未初始化它；start/goal/grow 显式赋值，而 `checkSolution:310–318` 的 connect 没赋值。按作者赋值来源登记；connect 输出 null/UNINITIALIZED_NOT_READ，不能整树无差别读取或为观察添加初始化。其 branch/parent/state 已赋值可读。原 save 两 mpaths 不含该 connect。

4. **原 mpaths/bridge 与同 q Motion。** `checkSolution:327–358` 实际 bridge 为 motion↔connectOther；另造 connect 与 connectOther 同 q、不同身份。mpath1 从 motion 起、mpath2 从 connectOther 起，按 start swap；connect 不进输出 solution，却在树和 PlannerData。保存入参/创建/lazy 返回、两原 mpaths/swap/connectionPoint；完整树保留 connect，不按 q 合并。CBiD 两 NN 树 snapshot 或最终 PlannerData 均不足以独自反推 SBL 来源。

5. **false 和独立重构不能抹去。** `isPathValid:385–388` 先 role0/共同 q1 branch，失败再 role1；`save2file:603–615` 再次独立 reconstruct，role1 前清 M，最终 false 只让 void save 返回，solve 仍可 EXACT。保留每次原 RBS/reconstruct true/false、当时 M、clear/fallback 顺序，失败 M 不充成功边；按原 mpaths 和全部真 M 先完成素材核对，才可另冻完整 P。不再求解、换 seed 或补点来填缺 M。

6. **随机分支 helper 与真实 SBL 投影分开。** SBL `193–232` 用 rand()%2 选 active，再直接调用 existing 对应固定解析 branch 及 fallback；不调用三参随机 IKproject。原三参 `IKproject:165–194` 缺 break 的历史失败和 H STOP/UNKNOWN 保持，不把 H 修补混入 SBL 或误设为 SBL 必经前置。SBL 每次实际投影的原返回仍须完整观察。

## 下一可行动工程边界

可准备 SBL 专属 transport/observer/transform 和单 target builder，作者 cpp/h 整体可逆、科学 body 原样一次；不混入 CBiD 单 token 距离修复、H 或 NR seam。先独立静审上述 projection/lifecycle/字段/bridge/M 契约，再冻结所有受管依赖，用已通过的多 TU `-MD -MF -` 原 stdout 规则及明确派生切片留证，防重现 BUILD01/02 遗漏。拟 45 wall/90 CPU 只是旧静态路线建议，**本报告未冻结、授权执行或消耗该额度**；未来 PRE 绑定 root 当时最新实际总账，不抄旧余额。

工程通过仅 BUILT_NOT_QUERIED；唯一 solve、完整 P 分别另冻源码/条件/最新总账和外层费用帽。原 main 的恒 true callback、12 维 box、q6±3.1416、resolution .02、II range2.6 等须由实际协议明示；观察不调整。原里程点 `../paths` 与密路径 `./paths` 分别隔离到新 run，保留错误/partial 文件，不因 void save 返回而称路径完整。未来矩阵观察的具体实现尚需独立审查，本报告不预设已完成。

本项不是新 SBL 资格、路径证书、RSS 结论、pilot 或正式预算；不 P2、不 Isaac、不提前结题 Word/PDF。
