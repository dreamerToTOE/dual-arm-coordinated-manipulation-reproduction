# S02 原始日志交付

原始 evidence.jsonl 为 132278298 字节，超过 GitHub 单文件限制。原文件在本地原路径保留，执行记录和独立审查仍绑定其原 SHA；Git 提交保存无损 evidence.jsonl.gz 与 evidence_delivery_manifest.json。其他 stdout/stderr、原生路径和所有失败记录分别保留。

在新克隆仓库中，从仓库根目录运行以下保存字节恢复命令；它先完整校验 gzip，原文件存在时只核验，不覆盖。

```bash
/usr/bin/python3 reports/p4_full_audit/recovery_tools/restore_cbirrt_solve02_journal_20261016.py --restore
```

省略 --restore 仅流式验证，不创建文件。恢复/校验不会启动机器人模型、规划器或任何科学查询。压缩前后解压 SHA256 均为 c297a6a8c9f3107bf756e70381eedca7b3799d5ef78b283eaeca35b84aa885df，原科学内容和判定没有改变。
