# P2累计小修3：闭环入口路径规范化

2026-10-14，before source2d62c87。N/D70、E/C35、clock2先已通过；首次闭环启动suite01在进入任何run_case之前失败：out=Path(args.output_dir)为relative，directory.relative_to(ROOT)中的ROOT为absolute，pathlib拒绝比较不同路径类型。ValueError与原metadata/30项NOT_EXECUTED账目保存，不把未开始算控制case失败或仿真发散。

仅将main入口out=Path(args.output_dir).resolve()。relative与absoluteCLI两种路径得到同一绝对结果，目录独占/不覆盖保护不变。run_case/plant/filter/controller/clock/观测/旧已发布命令/算法/阈值/条件不改。before/after完整源码由git保存，此次只有一行差异。

累计小修3/3，余额0，不重开。后续代码/科学异常按规则停止、实际记录，不进行第四轮。下一启动使用新独占suite02目录，suite01字节保留。此次没有执行控制case；没有回滚/重置物体或清零接触。仍只先原ID11，再ID30及其余矩阵（资格合格才允许）。运行metadata当前预算覆盖冻结参数快照中的旧历史预算标记，原v1/v2/v3不修改。
