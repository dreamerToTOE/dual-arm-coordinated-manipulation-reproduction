# V BUILD02尾段独审文字匹配补记

PASS 5/5，直接复用首版44项通过，不重复依赖/资产审。首版唯一失败源于审查器要求PRE包含“RLIMIT_CPU=90”，实际PRE为“RLIMIT_CPU仍为旧90秒”；原invoke AST与PRE都清楚区分旧子进程90防护、15wall/30CPU工作及20wall/40CPU总帽。原FAIL证书保留，实施三稿和DRAFT原字节不变。

不运行describe/import模型/编译/link/transform。root可仅增加本证书绑定和三个批准flag后冻结；科学/正式flag保持false。
