# ABB CBiRRT_NR BUILD02：六TU留证完成，缺五PQP头冻结停止

2026-10-16。主记录personnel_independent=false，只读取本次真实保存证据，零新增编译/模型/binary。冻结commit `909d6aa4f41bd28de85676f3d32b4a82d5d96e20`，协议 `configs/p4_full/r2_abb_cbirrt_nr_engineering_v2.json` SHA `374bfa916b60591a090be26cc2ac30cf75f74ee916e6bb839bc9bafcbe2e5018`，claim SHA `cdd80f68aeda56352d88a7a29d3a858a986e41736ef316c2ac98ea5272273a41`。唯一命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_v2_draft.py --protocol configs/p4_full/r2_abb_cbirrt_nr_engineering_v2.json
```

execution SHA `dcc96bbef72e47e663e51eb2dcbe8ae8f1bb99cef1e31d5eabad17f056fe15df`，status **STOP_PREFIX_RETAINED**，原因 `RuntimeError('ACTUAL_PROTECTED_DEPENDENCY_NOT_IN_FROZEN_MANIFEST')`。compiler exit0/PID95787/已回收，实际before/after进程组空，diagnostics空；ELF848464B/SHA `8295c051952f0678c2cab40859f1a6913262e4554918ba3260faf0bb1d37ea90`保存，成功manifest不存在，本次binary/query/solve/VI/formal均0。未通过工程门，不能启动该binary或借source编译0声称算法资格。

本次真实 `-MD -MF -` stdout完整196455B，恰好六条原始规则，六TU各一次；原始raw offset/SHA与六个派生切片全部已保存，切片明确非compiler直接生成六.d。BUILD01的同名覆盖根因已解决，但本次最后核全部protected依赖时发现五个PQP头未在run前冻结manifest：BV.h、PQP.h、PQP_Compile.h、PQP_Internal.h、Tri.h。bound仅包含libPQP.a，五个内容SHA在bound无同值别名，因此属于真正遗漏，不将其称为路径规范化误报。这是我们的依赖冻结完整性错误，不是算法/机器人模型或论文理论问题。完整列见execution.unfrozen_protected_dependencies；本次不运行后补清单改判PASS。

旧BUILD01 STOP/原六稿/claim/stage/raw唯一.d/V4判断和费用均保留；本次原stdout/stderr/全部源码/协议/claim/ELF/6raw规则/失败亦原字节保留，不重试同claim、不改科学源码或阈值。独立后审当前PENDING，应分别确认失败事实、真实六规则、缺失五资产及外层费用。

内部样本33.32665385099972wall/54.87463699999999CPU，独占GNUtime实际 `33.56 43.99 10.98 1`，外层Decimal上界33.57wall/54.99CPU，原45/90帽内；import/preflight至receipt落盘/退出与回收compiler链全计，supervisor自身记录范围外，历史未测尾UNKNOWN保持。待独立费用证书后V20一次替换内部样本，不抹除失败费用或增加科学成功数。

下一步仅saved-only精确核全实际依赖清单，并版本化补绑定这五个PQP头；实际没有变更的历史资产不重新计算科学资格。新BUILD03/全新stage/claim最多45wall/90CPU仍受R2总帽，先独立静态/PRE/协议提交后唯一工程，旧失败保持。若再次出现依赖机制失败，按D079独立根因审查继续有据修复，不盲目重试。全部211义务、TableI0/22500、VI974/974余0与原统计规模保持，不P2/Isaac/结题WordPDF。


## 独立失败后审、精确依赖核对与V20交付

真实人员独立POST现为13762/13762、零证据不一致，status STOP_BUILD_PROTECTED_DEPENDENCY_UNFROZEN，SHA `56a9800f2b7fd70c71e52ebe088c8a870406f46ec60d8f85efb1df3d1cea9737`；engineering_build_qualified=false，外层time/cost监督单独true。使用与实现不同的regex字节lexer重建完整196455B六规则/offset/slices/TU once及743唯一实际依赖，受管未冻恰五PQP头；五内容SHA在冻结清单所有别名均不存在，其他受管未发现缺项。该保存检查没有新增compile/binary/模型调用，不能当工程或路径PASS。

V20实际38execution=29科学账+9工程，charged累计753.085705375994wall/652.898923CPU，R2余额上界2846.914294624006wall/6547.101077CPU，历史未测尾部UNKNOWN。ledger SHA `19cf4ecb806532f0330b2a1e56ffde4475c07bd1011f0d2640578259c54fca0f`，211行166列表保前162列逐值不变。V20保全实际PASS、七组mismatch空，旧1028科学文件/57崩溃文件8482891B及tar/另5工作树13未提交/V19均保持，证据SHA `707e451cc2b1a42237f6ed2fd050526276a871149fc3ca64c35d09cb45c3f700`。全部原义务和统计规模不缩。

下一BUILD03仅在新冻结清单绑定这五个实际PQP头，并saved-only逐项核已有实际743依赖与所有受管资产；禁止运行后给BUILD02补清单改判。原作者完整body与physicalGD科学接缝不变，唯一新工程45/90扣原R2总帽，不开启该失败binary、solve或正式规划。
