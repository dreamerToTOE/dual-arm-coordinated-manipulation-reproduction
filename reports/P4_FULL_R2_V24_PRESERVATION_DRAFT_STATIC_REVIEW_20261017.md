# V24 saved-only 保全草案静态审查

**DRAFT：AST及静态核对16/16通过，未执行工具。** SBL BUILD01未由本任务运行；没有预测未来POST的SHA/checktotal，也没有生成V24账本、范围表、保全结果、claim或科学调用。

新工具保留V23的BASE/tar/其他工作树只读保全块，固定BASE SHA、1028历史文件、57崩溃文件/8482891字节、另5树13文件；tar只流读成员不解包。固定80e2b9e提交的V23 ledger/coverage/preservation三份真实SHA，历史41账行逐值保留。新总数要求42=31科学账+11工程，178→182列原值和211项、TableI45×500/1000s义务不变；related严格T02/T05/T08/T11/T17/T25。

新工程run为 `20261017_R2_ABB_SBL_PCS_BUILD01`、分类 `ENGINEERING_BUILD_ONLY_ORIGINAL_SBL_PCS_EXISTING_R2_NUMERICS`。检查BUILT_NOT_QUERIED、compiler退出0/已回收/空组、query/solve/binary/formal/VI全0；实际外部成本上界只替换内部样本一次。真实独立POST要求personnel/external/engineering true、完整无失败且checks_total>0；五TU完整依赖细审由绑定的真实独立证书约束，不重复Make lexer或编译。

调用数权威表要求42项逐execution SHA、source此前5/新增0/累计5，保留原失败；VI974/974剩0、正式0/22500不变。唯一可写输出是exclusive x的新V24保全JSON。

未来执行接口须提供 `--external-post <真实路径> --external-post-sha256 <真实SHA> --new-csv <真实V24范围表>`。实际POST/账表到齐并经主代理审查后才可调用，本次只AST/源码读取。该静态PASS不证明尚未发生的构建成功或实际保全PASS。

- `reports/p4_full_audit/recovery_tools/audit_preservation_v24.py` SHA256 `0e3213361fc543a0f5ac71d9fe5a546d4e231352952bc463916fcc9503bf418a`。
- `reports/P4_FULL_R2_V24_PRESERVATION_DRAFT_STATIC_REVIEW_20261017.json` SHA256 `855cc16b66bbcf3f909968c7f705fa6d06dbd00e98a25c6ecf0e738fe8a3126f`。
