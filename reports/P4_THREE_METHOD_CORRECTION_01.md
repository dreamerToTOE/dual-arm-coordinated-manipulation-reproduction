# 修正1/3：Git中文路径的只读哈希输入解析

2026-10-13。初版源码提交 `2ab2348`，预协议 `6d64b26`。
运行命令：`/tmp/p4-three-source.sHcHgg/venv/bin/python scripts/run_p4_three_methods.py --run-id 20261013_P4_three_methods_round0`。

## 原始失败

进程exit1，失败在创建RunLogger之前的`protected()`；没有数学测试、IK、投影、碰撞状态或规划调用。
`git ls-tree --name-only` 默认将中文文件名写成带引号的C风格转义；runner将其当普通路径读取，触发FileNotFoundError。
真实报告文件仍存在，没有覆盖或删除，原失败不是模型/算法不合格。

```text
File "scripts/run_p4_three_methods.py", line 114, in main
  before=protected()
File "scripts/run_p4_three_methods.py", line 42, in protected
  return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
FileNotFoundError: reports/P4_\350\256\272\346\226\207\345\244\215\347\216\260\346\261\207\346\200\273.docx
```

## 唯一改动与预期

将只读`git ls-tree`改为NUL分隔`-z`输出，并按NUL拆分文件名。
不改源码模型、三策略、树、碰撞、参数、端点、种子、预算、门限、统计口径。
预期仅让保护文件hash读取到真实中文路径，随后原封不动运行预登记数学与60次比较套件。
旧失败保留为启动证据，不算一个科学规划失败；下一run独立目录、不覆盖。
实现修正额度本次 **1/3**。没有新算法或数据资格主张。
