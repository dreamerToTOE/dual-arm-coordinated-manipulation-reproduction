# D080 SBL BUILD02 阶段记录（2026-10-17）

SBL writer-shadow v2 新目标已构建并经独立保存证据审查通过；本阶段没有执行模型、local 或 solve，不计为第五条完整路径。冻结提交 `14e1f27a`；原 BUILD01、SETUP01 和环境 II 四条完整路径直接复用，不重跑。

唯一命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_sbl_pcs_build_shadow_v2_draft.py --protocol configs/p4_full/r2_abb_sbl_pcs_engineering_shadow_v2_v1.json
```

协议 SHA `9f4c2b5efecd352ed9504a00b203a21629009f0c6feb636bea7cbc29e32652fe`。实际五 TU / 675 依赖，受管遗漏零；compiler exit0、已回收、进程组空、diagnostics 空，原 warnings 完整保留。16 个包装体与两处 writer 元数据表达式逐字逆恢复到原五文件。ELF SHA `ee5292ddcd78a82ea87e3b64f3de038bd8f107c8fb9084f3422db4aa8b6e4998`；独立后审 `P4_FULL_R2_ABB_SBL_PCS_BUILD02_SAVED_INDEPENDENT_POST_20261017.json`，其检查只表明工程证据完整，不是算法成功率。

GNUtime `22.36 30.12 6.91 0`，上界22.37墙钟/37.05 CPU秒；本次替代内部样本一次。V26共44 execution=32科学账+12工程，累计861.6957053759941墙钟/808.638923CPU秒；R2剩额上界2738.304294624006墙钟/6391.361077CPU秒，历史未测尾UNKNOWN保留。实际source solve仍5，本次新增0；正式0/18000。

新211行表 `P4_D080_SBL_PCS_BUILD02_ORIGINAL_VS_APPROVED_VS_ACTUAL_20261017.csv` 保留前196列逐值不变，另附4列工程证据。原22500历史分母、D08018000与VI归档分别表达；VI974/974消耗和所有旧失败/UNKNOWN保持。

下一项为已保存CBiPCS节点重建的正/负两条lazy链，trace/plain共4固定进程、15墙钟/30CPU秒，验证SBL原isPathValid、非平凡RBS、递归remove和生命周期。local通过后另冻一次seed7、Range .8、原10秒solve，EXACT仍须完整独立路径检查。原writer内部stream flags仍UNOBSERVED；sidecar/最终字节持久化与科学资格分列。

环境V原资产和入口差异报告、工程计划已保存；两个A02重建端点的后续aligned离散资格直接复用。当前正准备V专属PCS局部薄适配；V NR须独立Comau转移，不迁用ABB证书。RSS独立推进、VI不追加，正式cost pilot/18000尚无执行授权，不P2/Isaac/FR3实验。
