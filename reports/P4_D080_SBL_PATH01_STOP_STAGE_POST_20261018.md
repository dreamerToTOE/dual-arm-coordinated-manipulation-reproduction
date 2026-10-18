# D080：SBL 已保存路径前缀资格与时钟诊断（2026-10-18）

本阶段部分完成。II/A01/seed7 原 SBL 唯一 solve 的 387 节点、386 叶、六 milestone 原路径保持；没有第二次规划、投影或 RBS。原 II 四条合格全程路径直接复用，没有重跑。原论文211义务的D080范围映射已完成，本阶段只追加实际证据，VI永久只读，不开展P2/Isaac/FR3。

原路径资格由提交9d87603a冻结后唯一执行：`/usr/bin/python3 scripts/supervise_p4_full_r2_abb_sbl_pcs_path_draft.py --protocol configs/p4_full/r2_abb_sbl_pcs_path_v1.json`。原120墙钟/240 CPU帽下，执行记录为261完成/261合格，id261即第262点已获得完整数学与碰撞响应，但fsync中断，原终止为`D64_AGGREGATE_HARD_WALL_CAP`，状态`STOP_FINAL_WALL_OR_CPU_BUDGET`。原文件、原失败回溯和原停止记录不修改。

保存后独审分别核261 final与第262个partial：数学闭链、原机械限位、按原边解析分支及aligned v3离散碰撞全部通过。首审42140项通过、1项失败，是审查时loader cache与旧manifest不同；追加35项增量时序审查证明cache在运行结束后14:43:49随libbluetooth/libc-bin触发更新，运行前后记录一致，15个实际绑定共享库逐字未变。首审FAIL永久保留，组合证书独立覆盖原id0..261共262点；不能改称原run完成262。当前可读partial字节与重复响应一致，原被中断fsync当时是否完成仍UNKNOWN。

262点已保存闭链最大位置误差3.410605131648481e−13mm、旋转矩阵4.996003610813204e−16，机械限位最小余量0.08726666666666683rad；原完整队列386叶最大0.04975420918021825rad<.05。native/aligned各262次均无原pair碰撞，native TCP pose mismatch仍保留，aligned物理TCP资格逐点核验。实际保存PQP60784，原execution计数60552因第262次在计数入账前被中断；两者分别保留。尚有原id262..386共125点未验证，不得宣称第五条完整路径已合格、CCD、RSS成功或PCS性能优势。

原GNUtime为119.80/9.11/.96/exit1，但receipt单调时钟121.897074102、外层单调等待122.070263973。只读同boot日志记录运行内部实时时钟相对单调时钟回拨约2.259910秒，与timesync服务重启/初次同步相邻；支持主要计时差异解释，具体actor/syscall与全部I/O成本仍未证。原119.80日志保留，不能当完整墙钟上界。独审采用raw/outer-monotonic/receipt三观测Decimal最大包络，保守费用122.08026397300002墙钟/10.098723 CPU；局部120秒帽越界如实登记，总R2帽不变。

V29共47 execution=35科学账+12工程，累计999.0159693489941墙钟/826.637646 CPU，R2余量仅上界2600.984030651006/6373.362354；历史未测持久化尾UNKNOWN不补零。实际source solve累计6、本项新增0；正式TableI仍0/18000，原论文22500历史分母原样保留。最新完整对照表为`P4_D080_SBL_PCS_PATH01_STOP_ORIGINAL_VS_APPROVED_VS_ACTUAL_20261018.csv`（211×212），旧208列逐值保持。

下一项只为原125点准备独立TAIL02：90墙钟/180 CPU总帽，工作80/160为收尾留额，仍原R2总余额；原全队列和前缀组合证书冻结，原STOP不resume/覆盖，不更换节点、不改模型/几何/阈值，不重新solve或重查前262点。TAIL02先增量独审与冻结提交再唯一执行。V PCS纯工程与固定局部草案已准备，随后按V→III→IV推进；RSS独立线不阻塞PCS/NR。正式18000次仍须成本pilot和用户预算审批。

证据：`P4_FULL_R2_ABB_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json`（e2fb37a5…）；`P4_FULL_R2_ABB_SBL_PCS_PATH01_CLOCK_READONLY_DIAGNOSIS_20261018.json`（2ecc257d…）；原运行`results/p4_full/20261018_R2_ABB_SBL_PCS_PATH01/`；实际账本V29。
