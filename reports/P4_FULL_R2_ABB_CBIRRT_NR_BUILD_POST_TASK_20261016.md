# ABB CBiRRT_NR BUILD01：编译完成、依赖留证资格停止

2026-10-16。主任务记录 personnel_independent=false；只整理实际保存证据，不追加任何模型/编译/规划调用。冻结提交 `203c6ff95dd3d2367223ccd7c63f21b39e7eca13`，协议 `configs/p4_full/r2_abb_cbirrt_nr_engineering_v1.json` SHA `1909272b19708ddcbaeb5b26a835c4fcc280fc4a2e7fa41232d4e8ad65a8e703`，claim SHA `6591e4d6d991d92692317e57a69e7973164f20d41230f76c47a1e9feca606b38`。唯一命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_draft.py --protocol configs/p4_full/r2_abb_cbirrt_nr_engineering_v1.json
```

实际 execution `results/p4_full/20261016_R2_ABB_CBIRRT_NR_BUILD01/execution.json` SHA `a6f84e38ecef47649d9dc12cf7316a9ebc68429e6b126bd6cc1b23e4845d8b4d`，状态 **STOP_PREFIX_RETAINED**，原因 `RuntimeError('ONE_COMPLETE_MD_FILE_PER_TRANSLATION_UNIT_REQUIRED')`。compiler PID 93400、exit0、真实已回收，清理前后进程组均空，diagnostics为空。二进制实际存在，848464B、SHA `7c6ac348c8facbef8a08d64a9b5606545eeffcacc4208cf673da58b93bb02775`；但 manifest 未产生，工程未通过，不能进入 solve 或任何 binary 查询。编译器返回0不能替代已冻结的六TU依赖留证门。

六输入单driver命令包含 `-MD` 和最终 `-o`，实际只生成 `p4_abb_cbirrt_nr.d`，SHA `05621e65d40d89bccbacac84cdefd03aa9adc69fcede097545ced2dcd33e5538`，其首个source为最后的原CBiRRT_NR.cpp。此前V4静态审查以为默认产生六个独立.d的判断已被本次真实证据推翻；这是**我们自己的工程设计/审查错误**，不是作者算法失败或论文数学问题。V1–V4报告、原源/输入/旧stage/二进制/完整stdout与stderr/唯一.d/STOP/claim均原样保留，不为这次补造缺失的五TU依赖，也不重试同一claim。

内部样本 33.71188176799478wall/55.363333999999995CPU；GNUtime实际 `33.95 44.43 11.03 1`，Decimal外层上界 **33.96wall/55.48CPU**，满足原45/90帽。包含导入/preflight、拷贝/转换、唯一compiler及已回收后代、最终hash、execution/receipt落盘至异常退出；supervisor自身记录持久化在边界外，历史未测尾部仍UNKNOWN。人员独立失败/费用POST目前PENDING，待真实后审后以外层上界替换内部样本一次，不将失败去账或当作科学成功。

实际 binary/query/solve/正式Table I/VI新构造均0。复用原CBiNR full12 NN、mode1/2、100/500、RBS/回溯与既有physical GD接缝的源码已编译，但本次不提供端到端能力证据。既有PCS177、NR393、CBiPCS413节点路径独立资格及所有原失败/UNKNOWN保持。VI974/974余0，Table I0/22500、211义务和45×500/1000s/call及全部原文统计规模保持，不P2/Isaac或提前结题。

后续最小工程修复依据[GCC11官方预处理文档](https://gcc.gnu.org/onlinedocs/gcc-11.5.0/gcc/Preprocessor-Options.html)支持的 `-MF -`：新版本/新run/stage/claim让六TU完整依赖规则进入独占compiler stdout，再按真实六规则逐TU留证并验证全部保护依赖，仍一个compiler调用。只能在失败独立后审/完整入账、源码PRE/独立静态审查/协议提交冻结后执行一次，旧失败不改判；不改变科学body或通过标准。工程新预算45/90仍扣原R2总帽，科学solve和完整路径仍分别待冻。


## 独立失败后审与V19实际交付补记

原PENDING为当时记录，现独立报告实际13720/13720、0证据不一致，status STOP_BUILD_DEPENDENCY_EVIDENCE_INCOMPLETE，SHA `f4d04c1de62acfeea83e94137f146947db2f3f6045ab2b7ee1a544b61b82fed1`。这些检查证明失败事实/保存/费用一致，**不代表工程通过**；engineering_build_qualified=false，external_supervision/timing/cost_qualified=true。根因独立报告为 `reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD01_FAILURE_ROOT_CAUSE_20261016.json`，原唯一.d另有逐字saved copy与manifest供Git审查，不补造缺失规则。

V19实际37execution=29科学账+8工程，累计719.515705375994wall/597.908923CPU，余额上界2880.484294624006wall/6602.091077CPU；历史未测尾部UNKNOWN保持。ledger SHA `10f8a8f335d0fa95e6dbfe764a3b016d669c6aaff86f5a4ba8d66523d2edd18a`。完整覆盖表为 `reports/P4_FULL_R2_CBIRRT_NR_BUILD_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv/.md`，211行162列、前158列逐值保持，新增列只记工程STOP，无新增科学成功。

V19保全真实PASS：旧1028科学文件、57崩溃文件8482891B及tar、另5工作树13未提交、旧V18与完整历史列保持，七组mismatch均空；证据SHA `bd234a255fc3609bdce10b10c1008b05feb23b632199f84a35f74784766ec887`。后续BUILD02只修依赖I/O，源码PRE/独立静态/新协议先冻结，单45/90受原R2帽；尚未执行，不授权该失败binary或科学solve，不重算Q1/local/RRT/CBiPCS旧资格。
