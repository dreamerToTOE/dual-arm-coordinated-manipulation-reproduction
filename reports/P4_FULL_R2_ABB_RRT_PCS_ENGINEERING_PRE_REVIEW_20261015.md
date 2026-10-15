# P4 R2 ABB原RRT：45wall/90CPU工程冻结独立静态复核

2026-10-15。结论：**本版可由根代理冻结、提交后执行一次工程构建**。这不是科学solve或路径PASS授权；科学runner和独立path协议仍须分别冻结。

- Python builder与path runner AST解析通过。以非main导入builder，只调用只读draft_protocol/validate；66项旧template/source/mesh/二进制/manifest/claim/工程execution与依赖SHA逐项核验，当前engineering draft与即时生成配方完全匹配。0编译、0FK/IK/碰撞/solve/RNG查询，未建claim/stage/run。
- 独立在内存重建两wrapper并逆变换：state-level reconstructRBS和vector-level identify_state_ik反包装后，与已绑定旧plain stage的完整SVC文本逐字相同；原函数body各保留一次。body SHA分别为`fb3ac4578539a7e5a98a60ea4ab2b4663f6b7e56ba1be75d44460dad04df6915`、`d2a0e1793b0a2dd71d9353504f77e21d2661e3767c750efbf46ea52f42fde32b`。RRT仅remove(temp)改retain(temp)，逆替换后全文逐字相同。观察只读原调用完成后的结果，不额外IK/FK，不改原采样/投影/碰撞/RBS/失败fallback。
- 修正后的driver采用原run采样盒（q6±3.1416）、恒true callback、envII原range2.6、goalBias.05与固定A01输入；seed7在OMPL对象构造前设置OMPL RNG与C srand。先前静态第一版S1/S2已就当前SHA解除；不再声称±400°采样盒获批。
- observer保存每次已完成reconstruct的true/false与完整/部分Confs，post-return identify保存q/input_ik/returned_ik；nlohmann binary64往返精度，内存milestone不依赖6有效位txt。原paths和temp保留。硬kill时只有completed被直接观测，started不得从其推断；后续source runner须明确UNOBSERVED及进程退出前缀。
- 新外部stage/root、O_EXCL claim/日志与既存拒绝保证不覆盖旧四目标、旧paths或历史失败。builder只调用g++，不调用产物；query_calls=solve_calls=0。45wall/90CPU全工程段受alarm、aggregate live group CPU与进程RLIMIT_CPU保护；失败杀进程组、保留stdout/stderr/stage并记exit/termination。旧资产after SHA复核，工程自有wall/CPU独立execution且保守纳原R2总3600/7200，既存claim禁止重复。

冻结时仍需根代理将reviews置true、frozen置true，提交OWN与正式协议后执行；validate(execute=True)核当前配方、clean tracked文件及HEAD blob SHA。新review不加入OWN形成递归哈希。本报告不自行修改代码或配置、commit、build或science。

|被审文件|SHA256|
|---|---|
|`scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py`|`a76c67a53690a9e04dcb6fdb087bc65595192d09f69675667ab4ff271d8506e7`|
|`baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_observation.hpp`|`b597b56199279bd02a7030375e0dd055d650c9a0bb4bee80aef6d4242755381c`|
|`baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_driver.cpp`|`eeb5e4bce07ef6e7f466086374b6b304258684c110dc7cb9b8048fdeb16c2478`|
|`reports/P4_FULL_R2_ABB_RRT_PCS_END_TO_END_PRE_DRAFT_20261015.md`|`d6712e383426f38132b1d63c4bff0cc0819fa102648ea8e558d497eb898c912b`|
|`configs/p4_full/r2_abb_rrt_pcs_e2e_engineering_v1.draft.json`|`f2e9f41ef85b10cc86b12cebffe7683a7b75a9651c4cb59bd2517775366a1ac2`|

工程成功只证明当前薄入口可链接。下一步的source solve必须单独保存30wall/60CPU硬预算、exact/approx/回溯失败状态、build/source/request/hash和缺result前缀；path审查仍须完整节点门与有限N帽。不能拿本工程静态审查代替真实全路径资格或正式统计。
