# CBiRRT_NR 环境II完整离散起终路径资格通过

2026-10-17。主记录 personnel_independent=false；独立后审41787/41787、失败0，支持本版本环境II/A01 RECONSTRUCTED physical NR的完整source-policy离散路径资格。原source、GD数值接缝、重建端点和aligned碰撞适配分别保留来源，不冒充作者原KDL或原精度端点直接通过。论文全文仍部分完成。

冻结提交 `742fff283e26c806b3296d5504be522f1a892253`（完整SHA见execution），协议 `configs/p4_full/r2_abb_cbirrt_nr_full_path_v1.json` SHA `bac031b7de04580c0de0af2049077bb552a06daf160d0f048a5fc5db97908f36`。实际唯一命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_cbirrt_nr_path_draft.py --protocol configs/p4_full/r2_abb_cbirrt_nr_full_path_v1.json
```

原S一次II/A01/seed7/range2.6/solve10秒已在119a1b3运行，source EXACT/候选状态不改；本P没有新solve/采样/IK/NR投影/RBS。完整原树16Motion、桥16→14和11个true M全部保留，M长度65/65/17/65/129/129/65/33/33/33/65，699引用→689唯一节点/688叶，不换点、不补点、不截尾。原GD/project/RBS false与所有旧STOP/UNKNOWN原字节保存。

实际 `20261016_R2_ABB_CBIRRT_NR_PATH01/execution.json` SHA `ee8691a2e6ca2318e2ef4a8a2c8a2b3cc2f5a18c4d6e319a3d1857112a3ab025`，`PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH`。689/689数学闭链、原机械限位、v3 aligned离散碰撞全通过；闭链max位置 `9.8002665254171e-06 mm`、旋转矩阵max `4.6722628137957356e-08`，均在固定1e-5门内；最小机械限位余量 `.08726666666666683 rad`，max叶 `.04951897373867186 rad < .05`。NR不额外强加PCS固定链/branch门。

实际数学FK1378、collision689、adapter内部FK/J2756、PQP159848（native/aligned各79924）。native与aligned原碰撞均为0，但native TCP一致性0/689（max位置.0035660851019088113mm、旋转7.347506431889042e-6），其物理pose资格仍未通过；aligned一致性689/689（max3.410605131648481e-13mm/4.440892098500626e-16）。接纳仅原已冻aligned source policy，不把两者混为作者原native全资格。

独立POST `reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_20261017.json` SHA `b3a2443cb790df547597fe5a72b4eeb78341d2f93a4b4beca8252eba692c40c8`，41787/41787、0失败，independent_path_qualified和external supervision/timing/cost均true。完整689/688、两端binary64、11原M、全部raw/PQP/pose、真实双worker登记/EOF/exit0/reap/空组、3447个tar成员逐字匹配散文件及完整尾节点全部核验；原execution/receipt里的false字段不回写。

工程持久化沿用NR393原即时close writer，counted与完整science循环逐AST不变。完整3447散文件/queue/events另存单个exclusive无压缩tar并fsync、逐member/散字节/SHA验证，执行内绝对预算守护覆盖最终哈希与重I/O。原散文件和tar均保留；Git交付逐字无损压缩tar与manifest，不把I/O优化当算法性能改进。GNUtime `19.58 15.94 1.87 0`，上界19.59wall/17.83CPU，只替换本次内部19.30437744699998/17.686329样本一次，在120/240内；不作论文性能样本。

V23实际41execution=31科学账+10工程，charged815.475705375994wall/734.288923CPU；余额仅上界2784.524294624006/6465.711077，历史未测尾UNKNOWN仍保留。账本SHA `a8435b0c6321062e9bb4627012c5288c120af176b048a6195ea46db795df0ca7`。v3工具保留旧费用/独立证书和历史条目，增加逐execution真实source调用累计5（本P新增0），旧狭scope值留历史。新211×178范围表保前174列，单II资格不生成III/其他环境证据；45×500/1000s与全部原实验规模不缩。

V23保全实际passed=true、七组mismatch均空，SHA `b61dfee56fa04b8589ccc870f824d651c403d152086b2fc145323be9022aed02`；旧1028科学、57崩溃文件8482891B及tar、另五工作树13未提交、V22和全部历史列均保持。保全工具初稿两处静态类型/related-ID遗漏在首次执行前被root修正，旧自核报告及纠正addendum保留；并非科学失败或门限修改。

本证书只覆盖完整离散source-policy路径，不证明连续碰撞、实体杆表面、源省略pair、nativeKDL等价、全局统计成功率、RSS分布或PCS优势。VI974/974余0、正式TableI0/22500、211义务均保持。下一推进SBL的默认projection实际观察、lazy删除的身份代际/未初始化字段/原bridge与M契约；RSS独立诊断原RBS/分布/规划入口，不增加VI样本。各新阶段先冻结再运行，端到端后成本pilot再正式预算申请；不进入P2/Isaac或提前结题Word/PDF。
