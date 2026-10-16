# ABB CBiRRT D 两目标工程实现草案

2026-10-16。**STATIC_IMPLEMENTATION_DRAFT / NOT_FROZEN / NOT_COMPILED / NO_BINARY_OR_SCIENTIFIC_EXECUTION**。这是分阶段PRE的工程补充，不是执行协议。实际prior必须在IV及其他当前运行终止、POST与账目保存后重新生成，本草案未生成任何prior快照或claim。

新增四个实现文件：`scripts/build_p4_full_r2_abb_cbirrt_d_draft.py`、`baselines/p4_full/geometry_consistent/abb_cbirrt_d_instrumentation_draft.py`、`abb_cbirrt_d_observation_draft.hpp`、`abb_cbirrt_d_driver_draft.cpp`。原H、PCS、NR冻结源码及所有历史stage/日志/失败只读。工程stage为全新`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_d_v1/{source_control,distance_destination_fix}`，两目标合计60秒墙钟/120秒CPU、每目标45/90；工程不启动任何新binary、距离、local或solve请求。

## 科学变化与来源隔离

两目标从原`abb_pcs_qualification_v1/geometry_consistent_plain`独立复制，仅链接原R2 APC、SVC、碰撞、CBiRRT四个cpp，不再链接RRT或SBL。原CBi cpp SHA256必须为`60f6a483c533f61749bc7e741acc72bfc8cc2e137d719b25392e73831e458d93`。修复版仅采用已有单因子候选函数，将role1第一次`retrieveStateVector(a->state, qa_dummy, qb)`末参改为`qa`，候选未观测cpp SHA256固定`5b87ed08d674251594efc899ad922398f9c29a0a42f74494cafa7fa2424ae5c2`。没有H helper break、NN修改、门限或源数学体替换。

静态内存变换已核对：所有四个完整源文件可逆恢复原始字节（包括APC CRLF）；两观测目标仅CBi cpp不同，修复版逆转上述单token即与控制版逐字节相同。13个观测函数均保留完整原body一次，以原返回类型lambda执行原体，保留所有早退/false/partial。另有唯一已申明I/O差异：原`remove("./paths/temp.txt")`改为保留temp，不修原路径和源返回行为。原未修改源字节会另存在新stage的`preserved_originals/`，记录原/变换body和全文件hash，旧stage不写入。

## 一次binary保留的三个真实入口

`distance`：构造真实`RealVectorStateSpace(12)`、非空SI和原CBiRRT对象；不调用setup/solve。派生probe仅借用两份真实ScopedState创建Motion，设置原`active_chain`后直接调用受保护原`activeDistance`。没有复制距离公式，不调用模型、随机抽样、NN、grow或RBS。probe不读取原Motion未初始化的branch/a_chain字段，不把它插树，ScopedState负责释放。

原CBi构造确实构造SVC和mesh，并有直接`RNG rng_`成员。driver在对象前一次`ompl::RNG::setSeed(7)`；仅solve额外一次`srand(7)`。构造dispatch完成数、mesh-load真实hook、RNG成员结构次数分列；未hook的库内部RNG构造/draw标`UNOBSERVED`，不能把零采样声称为零RNG活动。distance每进程最多8个请求；未来D64 runner须单独冻结八进程固定清单与15/30预算。

`local`：只构造原`StateValidityChecker(si,env)`并初始化原state-space指针和计数，不构造CBi/RNG成员。直接调用原state-level `checkMotionRBS`或`reconstructRBS`，后者保留原先push首末和原向量递归，不自写递归；返回完整M，包括false前缀。未来L12只使用旧三条完整保存边，plain/trace完整M应binary64一致，未在本次执行。

`solve`：仅预留II/seed7/range2.6/10秒/trace单次入口，原12维盒、resolution .02和恒true callback，无goalBias。真实原CBi setup与solve只调用一次；保留原完整搜索体、rand角色、100/500迭代、投影fallback、RBS次序、save2file和EXACT返回。工作目录必须是未来新独占run的子目录，`./paths/`和`../paths/`均要求不存在后新建，旧mesh允许只读复制；所有原文本/临时输出因此留在新run。

solve返回、析构前导出两树真实Motion/state稳定运行内ID、parent/root身份、完整q、两branch和a_chain、connectionPoint映射；不按相同q合并Motion。exact时另外调用原getPlannerData，保留vertex tag/start/goal和有向边；非exact不调用它，避免原无条件空bridge。原全部高精度PathGeometric milestones、stateRBS与state重构全部真假返回、完整M、identify标签、activeDistance输入/角色/返回、save2file两mpath顺序都保存为source trace。任何EXACT仍只是`SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT`，不能代替完整重构和后续独立外门。

观测也覆盖原向量RBS/重构、固定branch projection、原FK/IK、collision和mesh load。observer只读取已有状态并写JSON，不追加任何模型、随机或树操作；未hook的库内部行为不从返回数推断。plain/trace由同binary运行flag选择；构造trace单独放在`construction`字段，每请求trace在构造后重新置零。未来runner绑定raw stderr时，构造trace只按一次真实构造计，不将每响应重复的construction字段重复入账。所有source stdout诊断重定向stderr，JSONL响应保留原输入与state后值/binary64，不能将接口返回当科学资格。

## 工程预算与保存检查

builder只在协议全部字段与即时保存来源一致、reviews为显式布尔且全部批准、源码/协议已提交且指定文件无修改时允许编译。两目标、外部stage、repo run和claim均独占，存在即拒绝重试。保留源byte逆转manifest、编译命令、全部stdout/stderr，成功或失败均保存stage原日志和repo副本；不执行已链接binary。compiler和链接库/原mesh/旧stage/binary及自有源码hash绑定，结束再核对旧资产。

墙钟由父进程timer与循环同时约束；CPU是父进程self+已回收children，加活动独立编译进程组(`/proc`中的utime/stime/cutime/cstime)。compiler另有90 CPU秒RLIMIT；父进程总120与每目标90帽先到即终止全进程组、回收，保留失败前缀。最终log/source/hash保全尾部计入实测own-cost；尾部越帽不得报`BUILT_NOT_QUERIED`。旧资产变化、日志副本不一致或最终预算失败均STOP，不自动补编译。

当前只做了stdlib AST解析和内存原源字节变换/逆转检查：两Python文件语法可解析，两source目标各13个complete-body hooks，H修复不存在，四文件整字节逆转通过，两目标单token差异通过。**未调用C++编译器、未运行builder命令、未生成stage/protocol/prior/claim、未调用任何科学接口**。C++类型与链接仍需独立静态审查和未来已冻结的唯一工程运行验证，不声称工程已成功。

D64科学runner、L12固定输入协议、S单次规划协议和P完整路径外门本次都未冻结/运行。211项全文义务、Table I 0/22500、VI 974/974、H原STOP及30UNKNOWN、原PCS/NR合格路径全部保持。
