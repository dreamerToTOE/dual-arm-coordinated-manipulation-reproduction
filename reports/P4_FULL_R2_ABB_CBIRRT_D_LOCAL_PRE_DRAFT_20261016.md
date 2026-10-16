# ABB D-fixed L12 原局部连接接缝资格 PRE 草案

2026-10-16。STATIC_RUNNER_DRAFT / NOT_FROZEN / NO_SCIENTIFIC_EXECUTION。本草案对应已有分阶段PRE的阶段L，只编写runner与保存输入审查；0compile/query/claim/执行协议/prior快照。需人员独立静态审查、真实D64接口PASS、最新实际全部R2账及root冻结后才能执行。

## 唯一固定输入与12个顶层调用

原RRT_PCS E2E01的全部三条高精度state-level回溯边直接取自 `results/p4_full/20261015_R2_ABB_RRT_PCS_E2E01/runtime/reconstruction_attempts.jsonl`，SHA256 `2aea2a4b79c280d09543a3d2f7f675422c3479c6440d4802e33ca5c66f7c2b26`。原index0/1/2、(active_chain,branch)=(0,3)/(1,3)/(0,0)，原完整M节点数80/65/34。仅D-fixed binary、环境II；plain/trace各一个新SVC进程，每进程依edge0/1/2次序各调原state RBS与state reconstruct，共6请求，合计12顶层。source-control局部源码与D-fixed相同，无需重跑相同矩阵。

旧edge输入qa/qb、原role/branch和完整reference M全冻结；不能从低精度txt反推或换边。两端全12维距离大于原.05，全部三条均为非平凡边。原withObs=true、RBS_tol=.05、max_depth150、固定分支IK和源递归原样保留，不加H或改driver/binary。

## 数学、trace与证书继承门

12顶层必须全部真实返回true、原输入state binary64不变；plain/trace的完整外部请求/返回/M及全部非观测字段逐binary64一致，包括signed zero。每个新state reconstruct的完整M必须逐节点、逐角与原80/65/34完全相同，不使用epsilon、删尾或抽子集。

trace按原body entry/return严格嵌套匹配id/kind，每请求reset，source counts与原始stderr一致。每边每种调用实际观察1个state body、2m+1个对应vector递归、m个fixed-branch project/FK/IK/collision，其中m=N-2。每个原project、IK、递归返回true，原collision返回0；固定主动角/role/branch不变，project输出multiset逐binary64等原M的全部内部节点。trace RBS与reconstruct的project输入/返回序列逐binary64相同。实际source body starts/completions从trace分别计，不用顶层返回数伪造。

plain内部project/FK/IK/collision starts/completions为UNOBSERVED，不能宣称观察了plain内部投影。plain/trace比较限完整外部输入/返回/state/M；内部投影的独立检查在trace和旧M之间进行。这沿用plain的原观测边界，不添加“为了观测”的新模型调用。

原PATH01的177个唯一节点及三边映射、全部节点物理/branch/界/碰撞保存证明冻结绑定。仅当上述全部M逐binary64一致，才继承旧177节点外门：原闭链1e-5mm/1e-5rotation、原机械界、原相应branch、aligned离散source collision与全部叶<.05。全部原node/arm1/arm2/math/collision文件保留并hash绑定；不再次查询同节点独立物理模型或collision adapter。若有任何M差异，停门保留原结果，不用新外门补救本项、换边或放宽标准。

## 计数、构造与预算

local driver只构造原SVC：2次SVC dispatch，0CBi对象/直接CBi RNG成员初始化、0setSeed/srand。trace进程原mesh load一次；metadata虽重复6次，raw construction只计一次。plain构造内部保持UNOBSERVED，库内部未hook行为不扩大为已证零。PQP模型载入只表示碰撞几何/BVH构造，不是planner搜索树或碰撞query。

“0新物理查询”只指0额外独立FK/J与collision worker。真实原RBS/reconstruct内部仍按原算法执行FK/固定IK/collision，trace如实记录；不能把这些固有调用写成0。没有随机采样、activeDistance、NR、solve、VI构造或正式Table I运行。

本项整次own-cost30秒wall/60秒CPU，受R2总3600/7200实际余额限制；继承已审D64的20ms预算、先持有Budget再启timer、先登记Session再Popen、SIGALRM短mask握手、逐PID live CPU加self/reaped、启动/关闭group成员检查、singlethread环境。每child继承30CPU RLIMIT，属于收紧，非新额外额度。使用修正版D64 transport的start/pump/kill/finish/central registry helpers，不复制旧390be3的清理缺陷。

异常后先关闭timer、中央登记PID全部kill，再drain/EOF/reap，最终确认2真实PID均回收；原stdout/stderr全部原字节/hash/长度、trace顺序、extra stdout、未配对尾、EOF与exit均独立gate。constructor或未登记session前缀也保存计raw并标UNKNOWN；任何未知尾、清理失败或final wall/CPU超帽不能PASS。Mandatory原资产/协议/claim/prior重hash和证据尾成本记入本项，不重发任何request。

## 冻结与解释边界

最终describe必须先读取实际合格D BUILD01与真实D64完整PASS和其全部输出，再扫描当时全部R2 own-cost一次；本草案不预造binary hash、当前prior数或余额。执行前源码/协议已commit、reviews显式全真、无活动P4进程、独占run/claim；执行后核对全部旧资产与protocol/claim/prior未变。

通过仅报 `PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED`：新D-stage局部接口接缝与旧离散证书一致。不是新完整CBi路径、CCD、RSS分布/RBS全局能力、PCS复杂场景优势或P4全文完成。旧LOCAL PARTIAL、H失败/UNKNOWN与其他原失败均保留；VI974/974余额0、Table I0/22500和完整211义务不变，不P2、不Isaac。后续S单solve与P完整队列需另行冻结，不能由本项自动启动。
