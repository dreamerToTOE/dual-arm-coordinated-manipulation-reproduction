# SBL_PCS 下一入口：公有投影观察与生命周期方案补记（待 root 审查）

2026-10-17。补充 `P4_FULL_R2_ABB_SBL_PCS_NEXT_ENTRY_STATIC_PREPARATION_20261017.md/.json`。此处只是工程观察方案，**未写 builder/driver/observer、未编译或运行 setup/模型/科学**；不改变原默认 projection、sampler、lazy、分支或阈值。root 审查后再分别冻结工程 build 与首次 setup，二者不能合并成默认科学授权。

## 实际默认对象的合法公有观察

保持作者 `SelfConfig::configureProjectionEvaluator` 与实际默认对象；OMPL seed 在 space/planner/相关 RNG 首次构造前设置，C rand seed 也在原调用前固定。setup 后从 `getProjectionEvaluator()` 取得该既存对象，保存动态类型、dimension、cell sizes、bounds/userConfigured 及 grid dimensions。先要求精确动态类型为本机已绑定的 `RealVectorLinearProjectionEvaluator` 或其头文件中未 override project 的 `RealVectorRandomLinearProjectionEvaluator`；不匹配则 UNKNOWN/停门，不替换 evaluator。

仅通过该对象原有 public `project` 接口，固定观察 **13 次**：12 维零向量和依序 e0…e11。零/基向量由专用 ambient State 装填，不做闭链投影、有效性判定、FK/IK、碰撞、采样或 RNG；不把它们计为机器人合格构型。保存输入/输出全部 binary64，要求结果有限、维数一致，零向量输出数值为零且保留正负零原位。令第 i 列为原 public project(ei) 返回向量，命名 `OBSERVED_LINEAR_ACTION_MATRIX`；与绑定的实际线性乘法实现共同定义公有映射身份。

该办法没有保护字段访问、伪派生 downcast 或重造随机矩阵，**不宣称逐字读取 private/protected matrix storage**；公有乘法对零的求和可能改变 signed-zero 表示。若必须验 private 原始矩阵字节，保留该差距，不能把此观察改名冒充。root 应先审定“精确动态类型+绑定线性实现+13 次公有作用结果”是否满足本轮身份契约，再实施；不能事后因结果不合而换观察定义。

“观察不额外取随机数”要有实现证据：静审绑定实际 libompl/相关头及该 project 纯乘法实现（精确对应源码，或本地只读符号/反汇编证据），不能只据函数名推断；13 次调用不得调用 setup/inferCellSizes/inferBounds/allocate sampler/new evaluator。实际 setup 内部随机抽取未 hook 仍为 UNOBSERVED。所有观察调用和成本另记，不能写成零调用或论文规划时间。

## 仅观察的 Motion 生命周期 registry

采用新的 SBL registry，不复用 CBiD 永不退役 pointer→ID map。每次原 `addMotion` 在对象仍活时登记单调 lifetime ID，并给该地址递增 generation；关联本代 state ID、tree、parent/root、q/branch。观察器自身不 alloc/free Motion，不更改 native grid/PDF/parent/valid。

用 `checkSolution` 完整 body wrapper 的观察作用域识别其内部新增 connect；只有该作用域内的 addMotion 属于原 connect 创建。root/grow 的 a_chain 原本已赋值，可按明确来源读取；connect 只输出 null/UNINITIALIZED_NOT_READ，任何 tree/save/删除 snapshot 都不得读其 a_chain。保持 connect 与同 q 的 connectOther 两份身份，save 原两 mpaths 和真实 motion↔connectOther bridge 另存。

`removeMotion` wrapper 在调用原 body **之前**复制本节点和全部当前 children 的 lifetime ID、q/parent/root/branch；把原父子关系留在事件中，因为 source 会先将 child parent=null 再递归。原 body 完整执行一次；返回后只用预存的地址 token/ID 标记 retired，不解引用已释放对象。递归层各自留证；同地址下一次 addMotion 得新 lifetime ID，不能继承旧 parent/branch。`freeGridMotions` 原循环直接 delete，须在调用前一次复制全 grid 活对象，再在原 body 返回后按预存 token 退役；clear/析构结束检查注册活对象归零。registry 只能在没有活对象时 reset。

所有 observer wrapper 必须逆变换恢复完整原文件字节；不改原 `isPathValid`、removeMotion 的递归顺序、same-branch role0/role1 优先级、save 的 M.clear/fallback 或 false 返回。observer 不吞异常、不回填 missing M，不按 q 合并身份；原 false 与 partial 继续独立保存。

## 分阶段冻结边界

工程 build 仅冻结并编译一个 SBL target，采用已有 actual dependency/raw/外层费用机制，成功仅 BUILT_NOT_QUERIED；不在 builder 中 describe 或运行 binary。单独首次 setup 资格再冻结构造顺序、seed、13 次映射观察、元数据/清理/计数、最新实际总账与外层帽，未批准执行前只保留稿。

原 SBL `sampler_` 在 solve 的作者原行才分配，所以首次 setup 时若仍 null 就报告 null；不能为提前取 sampler metadata 单独 alloc。未来唯一 solve 在原分配行之后观察实际 sampler name/attempts，必须另冻；其自身 setup 的默认对象也核对被冻结的作用身份，不因不匹配重构或重试。原路径/回溯与完整 P 仍是后续独立门。本补记不提交新预算数值、不执行任何阶段。

全部 211 原文义务与原统计规模保持，VI 974/974 余额 0、正式 Table I 0/22500。不开展 RSS 新构造、P2、Isaac 或提前结题。
