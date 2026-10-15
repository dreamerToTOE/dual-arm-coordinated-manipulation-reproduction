# P4 R2 ABB原RRT：一次科学pilot冻结独立静态复核

2026-10-15。结论：**当前candidate可由根代理冻结、提交后执行一次原RRT_PCS pilot**。审查仅AST、保存文件/输入标量和只读draft/validate；0新compile、0FK/IK/碰撞/solve/RNG，未领claim。

1. 来源链通过：已成功build来源85acfd55e32882dfc4cf6b08a3a3c7a43c32a97c，工程exit0/query0/solve0，自有17.12737691100483wall/23.727903CPU；runner验证build manifest↔execution↔claim/protocol、HEAD中的工程OWN blob、compiled source/headers、mesh、二进制和旧资产，129项assets当前SHA均相符。16prior自有成本各加一次，当前R2余额3297.5845607229994wall/6911.836017CPU。
2. frozen request与已合格A01 II start/goal逐值绑定；envII/sourceenv1、seed7、原run range2.6、goalBias.05、solve10s；原截断采样盒与q6±3.1416、恒true callback保留。driver/body与前工程审查一致，不新增IK/FK，不使用未达sample_q或随机IKproject，不引入CBiRRT activeDistance bug。
3. runner只派发一次binary；每次执行新O_EXCL claim、新目录及独立mesh/runtime，原paths不复制。30wall/60CPU全source段（含准备、原save2file回溯）有alarm+aggregate live process-group CPU+RLIMIT_CPU，失败杀组/reap，不重试。10s只为原solve外层ptc，不能据此推定内部RBS即时返回。真实成本及超帽/failure都保留。
4. stdout/stderr、原低精度paths/temp、result、每次completed true/false reconstruction与identify JSONL原字节均hash保全；若hardkill或结果缺失，仍写source execution/退出signal/partial JSONL tail。内部started明确UNOBSERVED，不从completed反推；无nativeFK/IK/PQP hook处不伪填实测数。
5. 原source exact/approx/nonexact与driver返回分栏。runner仅标SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT；独立path_qualified始终false，不因exact或status bool冒称完整路径通过。来源/输出异常留STOP_PREFIX，原普通approx/timeout/false不覆盖。后续2048-node/120wall/240CPU全路径门独立claim，若source回溯缺边或任一门不通过不得升级PASS。

静态validate当前candidate与即时配方完全一致；最终frozen须root标reviews=true及FROZEN_REVIEWED_READY，提交runner/protocol后执行。此处没有将正式22500统计规模或其他义务删除，一次pilot不计Table I、不证明PCS优势；VI候选0，不进NR/P2/Isaac。

|被审文件|SHA256|
|---|---|
|`scripts/qualify_p4_full_r2_abb_rrt_pcs_e2e.py`|`7d8e7bce553893f313a4882488f2d6e52fa4b2fbe83cf15231709c9390349149`|
|`configs/p4_full/r2_abb_rrt_pcs_e2e_qualification_v1.candidate.json`|`c18cc33e2df591b817df0e524aa75da77033bc06633fce4f0606a80ea160f538`|
|`configs/p4_full/r2_abb_rrt_pcs_e2e_engineering_v1.json`|`d1271168d29fef9b0f53dceb42f2876be67e26dbaf7a92a4fef1c05afcf90f67`|
|`results/p4_full/20261015_R2_ABB_RRT_PCS_E2E_BUILD01/execution.json`|`1e70eb0edf9a163ef1c5fbdcc16e15ac6598a368f21f75aa93792ca65d7e409b`|
|`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_pcs_e2e_v1/manifest.json`|`e1d665a5ff6c99a3654cf9433e8c2465b50e4d22dea5f91a226b42974e5adc0c`|
