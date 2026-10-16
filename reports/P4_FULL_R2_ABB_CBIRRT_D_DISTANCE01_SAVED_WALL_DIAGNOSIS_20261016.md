# D64 保存证据墙钟诊断

本报告仅用stdlib读取保存文件、事件、源码和mtime；作者参与过runner实现，因此不标人员独立。未执行模型、binary、编译、科学请求、新claim或重跑。原execution及所有raw保持原样，状态仍为`STOP_FINAL_WALL_OR_CPU_BUDGET`。

实际请求62/64、观察到62行响应，runner完成61项资格。第62项index61的完整JSON行与最后stdout逐字节一致，含原body entry/return；但未进入rawJSON和qualification持久化阶段，不能补算为runner完整成功。原UNKNOWN[61,62,63]保留，其中62/63从未dispatch。

已测墙钟15.463848030999秒、总CPU0.981773秒，8个Popen均已reaped，无登记liveCPU。清理专用CPU与activeDistance本体时间没有阶段采样，均UNOBSERVED。stop事件后至最终已测sample约0.359194秒，包含回收、哈希和保存尾部，不能当作纯清理耗时。

61个已返回响应在raw-line写入marker、JSON写入marker、qualification写入marker和complete事件之间合计约10.540117秒。三个后处理区间中位数均约42毫秒，首个至少100毫秒的区间为index9，2026-10-16T06:56:06.674943+00:00起。最大区间为index57 JSON到qualification约451毫秒。62项request写入到dispatch事件合计约3.490988秒。每项有4次单独durable保存：至少245次per-request fsync已完成，另第62raw-line fsync完成状态UNKNOWN。

这些证据支持父级证据保存、I/O或调度开销是本次主要工程瓶颈；不能据此归因为原论文理论错误、源距离函数算术失败或CPU预算不足。没有独立syscall计时，不能把上述窗口全部叫作fsync耗时，也不能判定具体存储设备故障。mtime与UTC存在约1毫秒边界差，49条dispatch到raw写marker为微小负值，所以不以这些marker代替校准计时器。

保存资料把中断收敛到第62raw-line持久化至其retained计数之前；精确open/write/flush/fsync位置需保留的traceback或syscall日志。最终会话14actual/12expected trace多出的完整pair属于该partial，不是已经证明observer产生额外调用。

记账边界另有明确限制：最终wall/CPU sample在execution.json序列化/fsync和终端输出之前，其额外成本未测。原数字原样保留并报告这一限制，不改写历史。

按保存own-cost相加，R2现为墙钟566.005705375994秒、CPU517.618923秒；大帽余额约3033.994294624006/6682.381077秒。这不重新授权D64固定15/30项；D64已到墙钟帽且禁止retry/resume，VI仍974/974。未来任何D证据管道或记账修订必须独立版本化、冻结、申请新预算，保持原64清单和判据。L12可继续草案准备，不能执行。

完整输入hash、mtime、分段描述及限制见同名JSON。全部输入读前读后hash、bytes、mtime一致。
