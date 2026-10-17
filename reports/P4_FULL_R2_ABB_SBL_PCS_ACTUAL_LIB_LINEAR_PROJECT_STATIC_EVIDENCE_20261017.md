# SBL 公有 13 点观察：实际 OMPL 库线性投影静态证据

2026-10-17。仅本机头文件、ELF、符号及反汇编只读核对；没有加载或执行该库，没有编译、项目 import、describe、transform、setup、FK、IK、碰撞、RBS、solve、stage 或 claim。只新增本报告，不修改工程稿、协议、账目或共享治理。

## 结论与适用边界

所绑定库中 `RealVectorLinearProjectionEvaluator::project` 的正常路径把既存对象内的 `ProjectionMatrix` 和输入 state 的 values 交给 `ProjectionMatrix::project`。后者实现固定矩阵与输入向量的浮点乘加，计算到临时向量后复制到输出；完整正常路径和闭合乘加 kernel 中没有 OMPL RNG、C `rand`、随机矩阵构造或采样器调用。因而在矩阵、输入、浮点环境和实际符号绑定固定时，支持“13 次既存公有 project 观察本身不额外抽取 OMPL/C 随机数”的静态结论。

这不是零分配、零成本的纯函数：本机正常非空路径会为临时向量执行 `malloc`/`free`，并写输出。不能从本报告推出 setup 内部随机数次数、实际 evaluator 动态类型/维数/矩阵值、已观察输出或机器人构型资格，也没有读取 protected `projection_`。浮点乘加的舍入和 signed-zero 结果仍应保存实际 binary64，不能把基向量作用结果冒称 protected 原始存储字节。

`RealVectorRandomLinearProjectionEvaluator` 的实际绑定头定义仅有四个构造函数，继承线性类且没有 `project` override；随机矩阵生成在构造器的 `ProjectionMatrix::ComputeRandom` 参数中。导出符号核对也没有发现随机线性类的独立 `project`。缺少独立符号本身不构成证明，结论依据完整绑定类定义；未来必须核对实际对象精确动态类型是这两个已审类之一，不能将本结论扩展到任意派生 evaluator。

`Linear::project` 调用 `ProjectionMatrix::project` 经 PLT，存在通常的动态符号插入边界。本报告识别的是这个文件内的实现，尚未证明未来进程的实际加载路径、预加载环境或运行时符号绑定；首次 setup 门必须把它们与本文件 SHA/构建依赖绑定。异常/分配失败路径不视为一次合格完成的观察。

## 实际文件身份

| 输入 | 路径或身份 | SHA-256 |
|---|---|---|
| 被核对库链接 | `/opt/ros/humble/lib/x86_64-linux-gnu/libompl.so` | `25e9cbdc7c1c3b1e7c56221e954e72c4f5cb96e6c45253631773655cac71499e` |
| 链接实际目标 | `/opt/ros/humble/lib/x86_64-linux-gnu/libompl.so.1.7.0` | 与上行同文件内容 |
| ProjectionMatrix 头 | `/opt/ros/humble/include/ompl-1.7/ompl/base/ProjectionEvaluator.h` | `e6d38f478826365f110fee87e0bca58ab20686a354d91f98a1c391ada0c7ea4d` |
| 线性/随机线性类头 | `/opt/ros/humble/include/ompl-1.7/ompl/base/spaces/RealVectorStateProjections.h` | `34fc567e726e8cafef27e1169c60b90d21e0f2091c1461919220120535ed9ead` |

ELF 为 x86-64、ELF64、小端、DYN；GNU Build ID `2ee555e2cf432b96ffbf076b03e6b77571f2014f`。本次相关代码所在 executable LOAD 的文件偏移和虚拟地址同为 `0x11c000`，因此下列代码虚拟地址同时是文件偏移。头文件与 ELF 分别绑定，不声称已取得该发行库的完整源码构建证明。

## 符号与控制流证据

`readelf --dyn-syms -W`（经 `c++filt`）给出两个 GLOBAL FUNC：

| 函数 | 符号虚拟地址/文件偏移 | 符号长度 | 本次完整主函数范围 |
|---|---:|---:|---|
| `RealVectorLinearProjectionEvaluator::project(State const*, Eigen::Ref<VectorXd>) const` | `0x1a7990` | 96 B | `[0x1a7990, 0x1a79f0)` |
| `ProjectionMatrix::project(double const*, Eigen::Ref<VectorXd>) const` | `0x1dbdb0` | 538 B | `[0x1dbdb0, 0x1dbfca)` |

线性类函数的决定性指令为：`0x1a799c add rdi,0xc0`（移到既存成员），`0x1a79c9 mov rsi,[rsi+0x8]`（取 state values），`0x1a79d1 call 0x12b170 <ProjectionMatrix::project@plt>`；随后只有栈保护检查和返回，未构造/替换 evaluator。

矩阵函数读取 `this+0x8`/`this+0x10` 维数和 `this` 的矩阵数据指针。单行路径 `0x1dbf6e..0x1dbf9e` 明确以 `mulsd`/`addsd` 对输入与矩阵项做点积；一般维数路径调用无导出名字的内部 kernel `0x486390`。该 kernel 的完整代码闭合范围 `[0x486390,0x486a71)` 已逐段检查：矩阵/输入读取、索引循环、`mulpd/addpd` 与 `mulsd/addsd`、目的向量累加写入，正常返回在 `0x4866da` 或 `0x486a34`；没有 `call` 或间接控制转移，全部条件/直接跳转留在该范围。`objdump` 给它显示的最近导出名字 `ProlateHyperspheroid::...+0x2c080` 只是 stripped 内部函数的最近符号标注，不能当成真实调用了该构造函数。

一般 kernel 的缩放参数由矩阵函数 `0x1dbe11` 从只读 `0x4aa468` 取值；实际 8 B 为 `000000000000f03f`（小端 binary64 的 1.0）。临时输出先清零再累加，随后复制到调用者输出。矩阵函数还调用内部 resize/分配助手 `[0x17fbb0,0x17fc57)`：其正常路径只有维数/溢出检查、`free@plt`、`malloc@plt` 和指针/长度更新；没有 RNG 或模型调用。主函数正常外部辅助调用还包括 `memset@plt`、`free@plt`，栈保护失败调用 `__stack_chk_fail@plt`；分配失败/异常 landing 不纳入“成功完成观察”。

绑定头的对应事实：`ProjectionEvaluator.h:55–106` 定义矩阵乘法用途及 `Matrix mat`；`RealVectorStateProjections.h:52–80` 定义线性类和其 `project` override；`83–123` 是完整随机线性类，没有任何 `project` override，四个构造器均显式使用 `ComputeRandom`。本报告没有调用这些构造器。

## 可复查的只读命令

```bash
readlink -f /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
sha256sum /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so /opt/ros/humble/include/ompl-1.7/ompl/base/ProjectionEvaluator.h /opt/ros/humble/include/ompl-1.7/ompl/base/spaces/RealVectorStateProjections.h
readelf -hW /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
readelf -lW /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
readelf -nW /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
readelf --dyn-syms -W /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so | c++filt | rg 'ProjectionMatrix::project|RealVectorLinearProjectionEvaluator::project|RealVectorRandomLinearProjectionEvaluator'
objdump -d -C -M intel --start-address=0x1a7990 --stop-address=0x1a79f0 /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
objdump -d -C -M intel --start-address=0x1dbdb0 --stop-address=0x1dbfca /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
objdump -d -C -M intel --start-address=0x486390 --stop-address=0x486a71 /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
objdump -d -C -M intel --start-address=0x17fbb0 --stop-address=0x17fc57 /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
objdump -s --start-address=0x4aa468 --stop-address=0x4aa470 /opt/ros/humble/lib/x86_64-linux-gnu/libompl.so
```

这些是文件分析工具，不是项目二进制调用。新增工程/科学执行、public project 调用、VI 构造与正式实验均为 0；VI 974/974、正式 Table I 0/22500、211 项原文义务保持。
