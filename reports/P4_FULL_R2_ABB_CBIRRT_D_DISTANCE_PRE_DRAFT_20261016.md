# ABB CBiRRT D64 真实距离接口资格 PRE 草案

2026-10-16。**STATIC_RUNNER_DRAFT / NOT_FROZEN / NO_PROCESS_OR_SCIENTIFIC_EXECUTION**。runner为`scripts/qualify_p4_full_r2_abb_cbirrt_d_distance_draft.py`，只导入stdlib和已审D工程builder的保存资产函数；不导入模型、数值库、FK/IK/NR/碰撞/RBS/solve。本文不批准运行，实际D BUILD01成功和最新全部prior保存后才允许生成最终可执行协议与独占claim。

## 固定条件与判据

D64只使用既有`P4_FULL_R2_ABB_CBIRRT_ACTIVEDISTANCE_SAVED_COUNTEREXAMPLE_20261015.json`保存的四个A01合格端点和16case：II/III各环境内两点有序笛卡尔积×role0/1，不跨环境配点、不换端点。每源版本×plain/trace×环境独立新进程，共8个原CBi对象；每进程严格8个固定距离请求，共64个真实受保护原`activeDistance`调用。source-control与D-fixed两版本仅D单token差异，禁混H。

每请求真实12角写入OMPL RealVectorState，显式设置原active_chain，借用state的probe Motion直接调用原函数，返回完整请求、距离、两份后state和其binary64。distance不调用setup、grow、NN、投影、RBS、FK/IK、碰撞查询或solve。原构造载入mesh是模型建树，不混计碰撞查询。driver未来调用接口不等于接口已经通过资格。

source-control必须复现原错误公式role1=`norm(b.arm2)`以及四个唯一原非零同点反例；这是对照应有行为，不能要求控制版满足距离公理而把它整个改判失败。D-fixed两role匹配独立stdlib六维L2参考，绝对误差≤1e-12 rad；对角距离严格0，交换精确对称；role0两源版返回binary64逐值一致。每源版同case的plain/trace输入、返回、完整非观测字段binary64一致，64个输入state全部保持。原16条保存算术同时绑定核对，不用公式冒充原C++执行。

64个请求、raw响应行原字节、解析JSON、单请求门结果全部保留，包括在算术门前已经返回但未合格的候选。若中断或门失败，原raw/失败/partial保存；完整fixed64未完成部分保留UNKNOWN，不改点/role/阈值，不补调或换seed。通过只能报`PASS_FIXED16_ACTIVE_DISTANCE_INTERFACE`，不能报PCS规划、RSS/RBS、路径或FULL论文复现通过。

## 构造、随机与真实计数边界

每进程OMPL对象前一次`ompl::RNG::setSeed(7)`，64次距离过程中不重置seed；driver的distance分支不调用srand/rand/shuffle/sampleUniform。原CBi仍含直接RNG成员：8次完成CBi constructor dispatch对应8次**结构性**直接RNG成员初始化；实际库内部RNG constructor/seed-draw started/completed没有hook，必须标`UNOBSERVED`，不能报0或用返回数伪造真实starts。

trace版4进程的原mesh load entry/return各4个；plain版4进程内部调用保持UNOBSERVED。64个顶层transport dispatch各计started/completed；仅32个trace距离能观察原函数body真实entry/return。另32个plain内部starts/completions保持UNOBSERVED。不能把64个transport返回数同时当成64个插桩原函数starts。

driver响应在每一行重复同一份`construction`信息，runner按进程只计一次并要求8份重复metadata一致；raw stderr完整绑定每进程的construction trace一次，加8个request trace。每请求trace序号重新置零，不能把它误判成进程级连续序号。plain/trace归一化仅移除mode和观测字段，不能移除真实输入、返回或state变化。observer不添加模型/随机调用。

## 15秒墙钟/30秒CPU与原始尾部

整次own-cost限15墙钟/30 CPU，并受R2总3600/7200余额约束，不扩预算。预算从claim前开始，到运行后的mandatory旧资产/协议/prior重hash与证据保全尾部计入；最终实测越帽必须STOP。20ms timer及每dispatch/pump前后检查wall/CPU；每源进程另有30 CPU秒RLIMIT。

父进程CPU采用self+已回收children，再加已登记直接source PID的live `/proc/PID/stat` utime/stime/cutime/cstime。根据已审driver/probe/observer/transform没有fork/exec/system/popen/thread入口，启动和关闭时保存完整process group成员并要求只有已登记PID。冻结前runner还会对绑定的自有源进行排除注释/字符串后的静态词法断言；不把该断言扩大为任意链接系统库行为的证明。未知或额外组成员即STOP；env固定单线程。最终关闭后以self+已reaped children计一次own-cost，不双计live与reaped。

source进程按固定8请求后关闭stdin正常退出；stdout/stderr双pipe非阻塞泵取且保存完整raw字节，reap后再次读至EOF。额外stdout、未EOF、trace不完整/不匹配、异常exit不允许PASS。逐raw trace采用含signed zero的binary64结构比较；construct只绑定一次。不因stderr的作者/PQP诊断文本而丢弃raw。若中断，先停止所有仍活跃组、回收，再保存完整可得前缀；未知尾部不能成为成功。

清理修订保全于`work/preserved_d64_distance_draft_390be3_20261016/`：原runner、PRE和全部旧静态报告均保留原字节。Session先由父级登记，再显式start；Budget先由父级持有，再启用20ms timer。仅在固定fork/setrlimit/exec握手至实际Popen/PID登记的小段屏蔽父SIGALRM，子进程preexec恢复原mask并设置原30CPU RLIMIT，父mask由finally恢复；该段不发送距离请求，恢复后立即检查累计帽。源构造可能已在exec后启动，不能把它记成零工作。系统启动阻塞仍计入15/30 own-cost，不授予额外时间；恢复后的检查或最终越帽必须STOP，不能将短段屏蔽宣称为严格15秒内已完成回收的证明。

异常处理入口先停重复timer，再做证据和清理；父finally对`budget.processes`与所有已登记`Session.proc`并集先kill，再drain和独立wait/reap，不能因管道或日志错误漏回收Popen。最终真实PID registry、started事件数、session数分别报告，完整PASS要求8个实际进程、8个started事件且全部reaped。最终CPU以self+reaped children为主；若仍有未reaped登记PID，其可测live CPU另列并加入总CPU，强制STOP，不冒充完整记账。

## 冻结依赖与工作范围

`--describe-protocol`必须首先找到真实合格D BUILD01 execution、manifest、两个binary及源/库/mesh/编译日志的actual hash；没有真实build就拒绝生成placeholder可执行协议。科学prior集合重新扫描实际全部R2 execution并包含D工程自己的own-cost。启动前要求全部bound/prior与当前一致、指定自有源码和协议已提交且无修改、reviews全显式批准、无其他活动P4执行、run/claim均不存在。结束再核对原资产、协议/claim、完整prior集合，若变化保留STOP。

本草案准备只执行stdlib AST、保存端点/16case算术与排表、源词法断言；不会调用builder describe生成过时prior。实际八进程、64距离、32配对以及独立saved-only POST均是下一冻结项。原H科学STOP/30UNKNOWN、VI974/974余额0、既有PCS/NR离散合格路径、211全文义务和正式Table I0/22500保持。不P2、不Isaac。
