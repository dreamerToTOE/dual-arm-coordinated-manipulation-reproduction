# H 科学协议describe保存前的账目断言停止

2026-10-16。唯一H工程已成功且保留。root调用真正科学runner的--describe-protocol，只读元数据输出在保存candidate前断言26prior失败，因此新candidate未写入、未冻结、未建科学claim/输出、未派发任何helper/模型。随后validate-draft因candidate不存在而退出，原命令错误保留。

根因：科学draft_protocol复用builder.prior()，该工程函数正确地排除自己的BUILD01 run，却使科学candidate遗漏新工程成本。必须只改未执行科学runner的prior读取为包含H工程、排除science自身；不改已冻结builder、工程execution或PRE。先保留修前字节、独立审查新26prior元数据，再生成新草案。该事件是preflight账目拒绝，不是科学失败，不重复build。
