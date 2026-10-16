# L12 v2：journal与最终计费工程变更方案

2026-10-16。**ENGINEERING_CHANGE_PLAN_ONLY / NO_RUNNER_IMPLEMENTED / NOT_FROZEN / ZERO_EXECUTION**。root授权准备方案；本文件不覆盖原L12 runner/PRE，不生成当前prior、可执行protocol、claim或费用测量。TAIL02 runner及其外层监督还需独立静态审查与实际POST，本文不预先认定其正确。

目标是让相同12个原local接口调用得到可复核完整证据，同时消除D64已观察到的每请求4次独立fsync所造成的保存开销。预算仍30墙钟/60CPU、不增科学调用；完整证据、原M逐bit和旧177证书门保留。

## 新文件与隔离

未来实施使用新的L12 v2 runner、PRE和专属run/claim/schema；具体名称由root冻结时指定。原 `qualify_p4_full_r2_abb_cbirrt_d_local_draft.py`、旧PRE、旧自审和D64冻结源码、execution、协议、claim、日志逐字保全。新版本不能通过更新旧RUN/CLAIM常量让旧原始记录看似续跑；同一新run失败后仍不重试。

## 最小代码改动边界

- 原 `fixed_edges`、`saved_certificate`、`schedule`、`trace_audit` 四个函数完整AST复制不变，继续核对原3边、12请求、原80/65/34、177唯一旧节点及所有原分支/递归计数。只对新模块文件的依赖注入/路径包装单列工程审查，不改科学函数以适应新输出。
- `prerequisites`另建严格的分次证书adapter，实施 `LOCAL_V2_PREREQUISITE_CONTRACT_DRAFT` 的全部AND项。必须等实际TAIL02和人员独立aggregate64、external supervisory POST后才可绑定；不预造路径、sha、prior或PASS对象。只接受明确新split schema，不将原D64 status映射成PASS。
- `Budget`保持30/60、20ms检查、父CPU+reaped children+live source PID；child CPU收紧不放宽。先登记Session再start、fork握手mask、中央union kill/reap、EOF和原字节stdio完整保存的已审原则保持。TAIL02 transport若获审查可以复用其纯工程方法，但必须对L12两个source进程和大trace响应重新审，不盲目复制。
- 新证据sink采用一个exclusive journal和原stdout/stderr流。每个请求的完整raw line先保留，再写request/response/qualification/trace对应的journal事件，不更改源响应。优先每source批次或整run一批durable checkpoint；调用前、返回、门失败和STOP前缀仍有原始序号和stage记录。任何持久化失败均STOP，不能把缓存成功冒充已保存证据。
- 不再为每请求强制四个独立fsync。每请求若仍需可读独立JSON，可在全部12接口完成或异常清理后从journal一次导出；它们明确为派生视图，真实证据以journal/stdio原字节为准。不得重新执行原body来生成缺失文件，部分journal损坏不得补造。
- 所有原门仍在内存完成并写入journal；保持6对plain/trace完整非观测字段比较、3对RBS/reconstruct投影序列和原M内点multiset、12次双state逐bit不变、全部trace嵌套与原源返回/碰撞值。false或差异立即停止发送新请求，不等到批次末才继续跑过失败。
- 正常流程只启动plain/trace两个SVC进程、每个6请求，禁止CBi构造/RNG/solve或新物理外门。结束stdin后正常exit0、全部EOF/raw_trace绑定、无extra stdout、registry完整及最终hash均为必要门；异常先停请求、kill全部仍活组、drain/reap，再保全prefix和UNKNOWN。
- 所有journal、原始stdio、派生视图、旧资产及协议/prior前后hash、unknown、最终内层execution的mandatory写入须在外层受监督工作程序退出前完成。外层独立计时/CPU观测覆盖该程序完整生命周期，不能再以内层sample排除最后execution序列化/fsync。
- 外层最终费用与监督输出本身的开销边界须在实施PRE明确：哪些费用包含于受测进程、哪些为监督/保存后审，如何给最终R2提供单一完整own-cost来源。不得以计时文件有值便声称监督者最后写入成本也已实测；不能用0补未测。需要可复查的外层原始time/时钟日志、退出/PID绑定和人员独立POST，任何超帽/未知费用不允许PASS。
- 新L12最终PASS仍是局部接缝及旧离散证书复用，不表示新完整CBi路径。保留来源 `SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO`，原D64 STOP/-9、LOCAL PARTIAL和所有历史失败显式引用。

## 实施后必做的静态delta审查

1. 四个纯科学函数AST逐字等于本文件绑定值；原角色、branch、80/65/34、12请求/2进程、.05/150/withObs及旧177证书门未变。
2. 前置adapter不能只OR标签，全部64来源/32pairs/四同点反例/64次双state/资产/监督费用AND约束无缺项；任一缺失、未知、hash变动或旧STOP被改即fail closed。
3. journal文件使用exclusive create、原raw与事件序号/bytes/hash可独立重建，失败前缀无法被派生视图掩盖；batch策略不改变科学请求或内存门执行顺序。
4. source PID登记、timer、write/pump、超时清理、EOF和reap的所有异常边界与新版传输独立审查一致；不新增writer线程、fork或未计费辅助进程。
5. 外层真实计费覆盖最后内层mandatory持久化，不重复扣旧D64或TAIL02费用；30/60及最新R2总余额严格。测试仅用saved fixture/stdlib/fake I/O，不启动科学binary或构造新prior/claim。

具体代码就绪后另出独立静态审查，只有root冻结并提交源码、实际前置全真且无活动P4执行，才可生成真实当时协议并唯一执行。当前没有实现新runner，也没有开始L12科学调用。

## 原科学AST绑定（仅静态来源）

原runner SHA256：`622a25ffdf23f95aba437309fa511d564ebaeab172323666d050a89598739e36`。

|函数|AST SHA256（无位置属性）|
|---|---|
|`fixed_edges`|`fe85f634c3aa7b9242b14ed82bbef54da316574e30e747bcf076d56cee4b9fb6`|
|`saved_certificate`|`520f71ab243dafd852adb5509151f64615d0511bbc5745bb764f2119e48c2491`|
|`schedule`|`47134a1e1363dfefbb773e4ee9ec76db307998e51983bec43ae767d33baeff96`|
|`trace_audit`|`c3667ce5e86a931f313d928d19fbc4ba65eb8811702d3cb200f9575cc0aa1457`|
